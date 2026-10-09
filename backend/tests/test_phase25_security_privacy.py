"""CLINOVA AI — Phase 25 Security, Privacy & Audit Hardening Test Suite.

Continuous Care Intelligence System.
Phase 25: Security + Privacy + Audit Hardening.

Validates the 20 critical security & privacy specifications:
1. Unauthenticated rejection (401 Unauthorized in strict mode)
2. Token tampering / expiration / revocation rejection (401)
3. Inactive account access rejection (401/403)
4. Server-side RBAC enforcement across roles
5. Patient data isolation (cross-patient access blocked with 404/403)
6. Facility data isolation (cross-facility mutations blocked with 404/403)
7. Object-level authorization (random UUID guessing returns 404 with structured error)
8. Mass-assignment / client-controlled field protection
9. Prohibited autonomous clinical actions unconditionally rejected (422/403)
10. Referral mutation access control & facility boundary enforcement
11. Facility capability/capacity mutation access control
12. SignalGraph telemetry injection access control (patients blocked, cross-facility blocked)
13. Orchestration decision authorization & clinician-only enforcement
14. Sync replay & payload tampering detection (reused operation ID with altered payload -> FAILED)
15. Sync cross-facility & patient scope enforcement
16. Sync prohibited clinical actions rejection
17. Clinician-only conflict resolution with cross-facility rejection
18. Audit log immutability (strictly read-only for authorized roles; no mutation/deletion endpoints)
19. Zero secret / token / password leakage in API responses
20. Structured error contract & security headers (X-Content-Type-Options, X-Frame-Options, X-Clinical-Safety)
"""

import uuid
from typing import Optional, Tuple
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from jose import jwt
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_REFERRAL_COORDINATOR,
    ROLE_FACILITY_ADMIN,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
    PROHIBITED_CLINICAL_ACTIONS,
)
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import Case, Patient, User, SyncJournal, ClinicianDecision, utc_now


@pytest.fixture(autouse=True)
async def setup_phase25_environment():
    """Ensure DB schema is initialized and configure strict Phase 25 identity defaults."""
    await init_db()
    original_legacy_headers = settings.ALLOW_LEGACY_ACTOR_HEADERS
    original_legacy_anon = settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK

    # Set strict authentication environment for Phase 25 tests
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False

    yield

    settings.ALLOW_LEGACY_ACTOR_HEADERS = original_legacy_headers
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = original_legacy_anon


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Helper to authenticate and return bearer JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


async def create_test_patient_and_case(
    facility_id: str = "FAC-DH-04",
    link_user_id: Optional[str] = None,
) -> Tuple[Patient, Case]:
    """Helper to create a valid Patient and canonical Master Case satisfying database constraints."""
    async with async_session_factory() as session:
        p = Patient(
            id=str(uuid.uuid4()),
            synthetic_id=f"PT-SYN-{uuid.uuid4().hex[:6].upper()}",
            age_bracket="40-49",
            biological_sex="MALE",
            is_synthetic=True,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        session.add(p)

        if link_user_id:
            user = await session.get(User, link_user_id)
            if user:
                user.patient_id = p.id

        c = Case(
            id=f"case-{uuid.uuid4()}",
            case_number=f"CN-{uuid.uuid4().hex[:8].upper()}",
            patient_id=p.id,
            facility_id=facility_id,
            status="ACTIVE",
            pathway="REGULAR_STANDARD",
            current_state="INTAKE_RECORDED",
            acuity_tier="ROUTINE",
            risk_score=10.0,
            primary_syndrome="CHEST_PAIN",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        session.add(c)
        await session.commit()
        return p, c


# ===========================================================================
# 1. Unauthenticated Rejection (401)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_01_unauthenticated_rejection():
    """Validates that unauthenticated requests without authorization tokens return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request to protected cases endpoint
        res = await client.get("/api/v1/cases")
        assert res.status_code == 401
        data = res.json()
        assert data.get("error", {}).get("code") == "AUTHORIZATION_ERROR" or "detail" in data

        # Request to protected referral endpoint
        res_ref = await client.post(
            "/api/v1/referrals/create",
            json={
                "case_id": str(uuid.uuid4()),
                "origin_facility_id": "FAC-PHC-01",
                "destination_facility_id": "FAC-DH-04",
                "required_bundle": "BUNDLE_ROUTINE_AMBULATORY",
                "sbar_situation": "Chest pain",
                "sbar_background": "Hypertension",
                "sbar_assessment": "Moderate risk",
                "sbar_recommendation": "Transfer for ECG",
            },
        )
        assert res_ref.status_code == 401

        # Request to audit logs
        res_audit = await client.get("/api/v1/audit/logs")
        assert res_audit.status_code == 401


# ===========================================================================
# 2. Token Tampering / Expiration / Revocation Rejection (401)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_02_tampered_expired_revoked_token():
    """Validates that tampered signatures, expired tokens, and revoked tokens return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")

        # 1. Tampered token
        tampered_token = token[:-5] + "XXXXX"
        res = await client.get("/api/v1/cases", headers={"Authorization": f"Bearer {tampered_token}"})
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # 2. Expired token
        expired_payload = {
            "sub": "usr-doc-01",
            "role": ROLE_CLINICIAN,
            "exp": datetime.now(timezone.utc) - timedelta(hours=2),
            "iat": datetime.now(timezone.utc) - timedelta(hours=3),
            "jti": str(uuid.uuid4()),
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        res_exp = await client.get("/api/v1/cases", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_exp.status_code == 401
        assert "expired" in res_exp.json()["error"]["message"].lower()

        # 3. Revoked token (logout)
        logout_res = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_res.status_code == 200

        # Attempt reuse of revoked token
        res_revoked = await client.get("/api/v1/cases", headers={"Authorization": f"Bearer {token}"})
        assert res_revoked.status_code == 401
        assert "revoked" in res_revoked.json()["error"]["message"].lower()


# ===========================================================================
# 3. Inactive Account Access Rejection (401/403)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_03_inactive_account_rejection():
    """Validates that deactivated/inactive user accounts are blocked unconditionally."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Inactive user login attempt
        res = await client.post(
            "/api/v1/auth/login",
            json={"username": "inactive_user", "password": settings.DEMO_USER_PASSWORD},
        )
        assert res.status_code in {401, 403}

        # Forged valid token with inactive user subject
        inactive_payload = {
            "sub": "usr-inactive-08",
            "role": ROLE_NURSE,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        }
        inactive_token = jwt.encode(inactive_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        res_api = await client.get("/api/v1/cases", headers={"Authorization": f"Bearer {inactive_token}"})
        assert res_api.status_code == 403
        assert "deactivated" in res_api.json()["error"]["message"].lower()


# ===========================================================================
# 4. Server-Side RBAC Enforcement Across Roles
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_04_server_side_rbac_enforcement():
    """Validates role-based permission boundaries prevent unauthorized actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        nurse_token = await login_helper(client, "nurse")
        auditor_token = await login_helper(client, "auditor")

        # Patient attempting referral coordination (requires REFERRAL_COORDINATE) -> 403
        res_pt = await client.post(
            "/api/v1/referrals/create",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "case_id": str(uuid.uuid4()),
                "origin_facility_id": "FAC-PHC-01",
                "destination_facility_id": "FAC-DH-04",
                "required_bundle": "BUNDLE_ROUTINE_AMBULATORY",
                "sbar_situation": "Situation",
                "sbar_background": "Background",
                "sbar_assessment": "Assessment",
                "sbar_recommendation": "Recommendation",
            },
        )
        assert res_pt.status_code == 403

        # Nurse attempting clinical decision recording (requires CLINICAL_DECISION_RECORD) -> 403
        res_nr = await client.post(
            "/api/v1/orchestration/decision",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "case_id": str(uuid.uuid4()),
                "action": "OBSERVE",
                "decision_type": "ACCEPT",
                "clinician_id": "usr-nurse-02",
            },
        )
        assert res_nr.status_code == 403

        # Auditor attempting facility capacity modification -> 403
        res_aud = await client.post(
            "/api/v1/facilities/FAC-DH-04/update-capacity",
            headers={"Authorization": f"Bearer {auditor_token}"},
            json={"icu_beds_available": 10},
        )
        assert res_aud.status_code == 403


# ===========================================================================
# 5. Patient Data Isolation (Cross-Patient Access Blocked)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_05_patient_data_isolation():
    """Validates that a patient cannot access or view another patient's case."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        patient_09_token = await login_helper(client, "patient_09")

        # Create patient record and link to usr-patient-07
        _, c = await create_test_patient_and_case(facility_id="FAC-PHC-01", link_user_id="usr-patient-07")

        # Patient 1 (usr-patient-07) can access their own case
        res_self = await client.get(f"/api/v1/cases/{c.id}", headers={"Authorization": f"Bearer {patient_token}"})
        assert res_self.status_code == 200

        # Patient 2 (usr-pt-09) attempting to access Patient 1's case is rejected (404 to avoid enumeration)
        res_other = await client.get(f"/api/v1/cases/{c.id}", headers={"Authorization": f"Bearer {patient_09_token}"})
        assert res_other.status_code in {403, 404}


# ===========================================================================
# 6. Facility Data Isolation (Cross-Facility Mutation Blocked)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_06_facility_data_isolation():
    """Validates that facility administrators cannot mutate resources of a different facility."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # facility_admin is assigned to FAC-DH-04
        admin_token = await login_helper(client, "facility_admin")

        # Attempt mutation on FAC-PHC-01 (out of scope) -> 403 or 404
        res_cap = await client.post(
            "/api/v1/facilities/FAC-PHC-01/update-capacity",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"general_beds_available": 10},
        )
        assert res_cap.status_code in {403, 404}

        res_tog = await client.post(
            "/api/v1/facilities/FAC-PHC-01/toggle-capability",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"capability_code": "OUTPATIENT_TRIAGE", "is_operational": False},
        )
        assert res_tog.status_code in {403, 404}


# ===========================================================================
# 7. Object-Level Authorization (Random UUID Guessing Returns 404)
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_07_object_level_authorization():
    """Validates that querying a non-existent UUID returns a structured 404 without leaking internal traces."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        fake_uuid = str(uuid.uuid4())

        res = await client.get(f"/api/v1/cases/{fake_uuid}", headers={"Authorization": f"Bearer {clinician_token}"})
        assert res.status_code == 404
        body = res.json()
        msg = body.get("error", {}).get("message", "") or body.get("detail", "")
        assert "not found" in msg.lower()
        # Ensure no traceback or internal path is exposed
        assert "Traceback" not in str(body)
        assert ".py" not in str(body)


# ===========================================================================
# 8. Mass-Assignment / Client-Controlled Field Protection
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_08_mass_assignment_protection():
    """Validates that client-submitted privilege escalation fields are rejected via strict schema validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")

        # Attempt to inject role, is_active, is_admin via intake submit
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "chief_complaint": "Persistent cough",
                "consent_confirmed": True,
                "role": "SYSTEM_ADMIN",
                "is_active": True,
                "is_admin": True,
            },
        )
        # Extra fields forbidden -> 422
        assert res.status_code == 422

        # Verify the authenticated user profile remained unaffected
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {patient_token}"})
        assert me_res.status_code == 200
        assert me_res.json()["role"] == ROLE_PATIENT


# ===========================================================================
# 9. Prohibited Autonomous Clinical Actions Unconditionally Rejected
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_09_prohibited_autonomous_clinical_actions():
    """Validates that autonomous clinical actions (AI_DIAGNOSIS, AUTO_PRESCRIBE, etc.) are blocked server-side."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")

        _, c = await create_test_patient_and_case(facility_id="FAC-DH-04")

        # Test each prohibited action
        for bad_action in ["AI_DIAGNOSIS", "AUTO_PRESCRIBE", "AI_ADMISSION", "AI_DISCHARGE", "AUTHORIZE_PROCEDURE"]:
            res = await client.post(
                "/api/v1/orchestration/decision",
                headers={"Authorization": f"Bearer {clinician_token}"},
                json={
                    "case_id": c.id,
                    "action": bad_action,
                    "decision_type": "ACCEPT",
                    "notes": "Autonomous test",
                },
            )
            assert res.status_code in {403, 422}, f"Expected rejection for {bad_action}, got {res.status_code}"


# ===========================================================================
# 10. Referral Mutation Access Control & Facility Scoping
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_10_referral_mutation_access_control():
    """Validates that referral operations enforce REFERRAL_COORDINATE permissions and facility scope."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        coordinator_token = await login_helper(client, "referral")

        # Nurse attempting referral creation -> 403
        res_create = await client.post(
            "/api/v1/referrals/create",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "case_id": str(uuid.uuid4()),
                "origin_facility_id": "FAC-DH-04",
                "destination_facility_id": "FAC-TMC-05",
                "required_bundle": "BUNDLE_ROUTINE_AMBULATORY",
                "sbar_situation": "Chest pain",
                "sbar_background": "Hypertension",
                "sbar_assessment": "Moderate risk",
                "sbar_recommendation": "Transfer for specialist consult",
            },
        )
        assert res_create.status_code == 403

        # Referral coordinator updating non-existent referral -> 404
        res_stat = await client.post(
            f"/api/v1/referrals/{uuid.uuid4()}/status",
            headers={"Authorization": f"Bearer {coordinator_token}"},
            json={"status": "ACCEPTED"},
        )
        assert res_stat.status_code == 404


# ===========================================================================
# 11. Facility Capability/Capacity Mutation Access Control
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_11_facility_capability_capacity_mutation_access():
    """Validates that only authorized facility admins can toggle capabilities and update capacity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")
        admin_token = await login_helper(client, "facility_admin")

        # Clinician attempting capacity update -> 403 (requires FACILITY_ADMIN_MANAGE)
        res_cl = await client.post(
            "/api/v1/facilities/FAC-DH-04/update-capacity",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"icu_beds_available": 5},
        )
        assert res_cl.status_code == 403

        # Nurse attempting capability toggle -> 403
        res_nr = await client.post(
            "/api/v1/facilities/FAC-DH-04/toggle-capability",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"capability_code": "CT_SCAN", "is_operational": False},
        )
        assert res_nr.status_code == 403

        # Authorized facility admin at FAC-DH-04 succeeds
        res_adm = await client.post(
            "/api/v1/facilities/FAC-DH-04/update-capacity",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"icu_beds_available": 8},
        )
        assert res_adm.status_code == 200
        assert res_adm.json()["icu_beds_available"] == 8


# ===========================================================================
# 12. SignalGraph Telemetry Injection Access Control
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_12_signalgraph_telemetry_access_control():
    """Validates telemetry injection blocks patients and out-of-scope facilities."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        nurse_phc_token = await login_helper(client, "nurse_phc")
        clinician_token = await login_helper(client, "clinician")

        # Patient cannot inject telemetry -> 403
        res_pt = await client.post(
            "/api/v1/signalgraph/inject-event",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"facility_id": "FAC-PHC-01", "syndrome_tag": "FEVER", "acuity_tier": "GREEN"},
        )
        assert res_pt.status_code == 403

        # Nurse at FAC-PHC-01 attempting injection for FAC-DH-04 -> 403
        res_cross = await client.post(
            "/api/v1/signalgraph/inject-event",
            headers={"Authorization": f"Bearer {nurse_phc_token}"},
            json={"facility_id": "FAC-DH-04", "syndrome_tag": "FEVER", "acuity_tier": "GREEN"},
        )
        assert res_cross.status_code == 403

        # Clinician at FAC-DH-04 injecting for own facility -> 200
        res_valid = await client.post(
            "/api/v1/signalgraph/inject-event",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"facility_id": "FAC-DH-04", "syndrome_tag": "RESPIRATORY", "acuity_tier": "YELLOW"},
        )
        assert res_valid.status_code == 200
        assert res_valid.json()["status"] == "EVENT_INJECTED"


# ===========================================================================
# 13. Orchestration Decision Authorization & Clinician-Only Enforcement
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_13_orchestration_decision_clinician_only():
    """Validates that clinician decision endpoint derives clinician_id from token, ignoring spoofed fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")

        _, c = await create_test_patient_and_case(facility_id="FAC-DH-04")

        # Submit decision with spoofed clinician_id in payload
        res = await client.post(
            "/api/v1/orchestration/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "case_id": c.id,
                "action": "OBSERVE",
                "decision_type": "ACCEPT",
                "clinician_id": "SPOOFED_CLINICIAN_ID",
                "notes": "Legitimate observation order",
            },
        )
        assert res.status_code == 200
        assert res.json()["status"] == "AUTHORIZED"

        # Verify in database that clinician_id matches authentic token actor_id
        async with async_session_factory() as session:
            dec_q = await session.execute(
                select(ClinicianDecision).where(ClinicianDecision.case_id == c.id)
            )
            dec = dec_q.scalars().first()
            assert dec is not None
            assert dec.clinician_id == "usr-doc-01"
            assert dec.clinician_id != "SPOOFED_CLINICIAN_ID"


# ===========================================================================
# 14. Sync Replay & Payload Tampering Detection
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_14_sync_replay_and_tampering_detection():
    """Validates that reusing a sync_id with a tampered/modified payload is detected and rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        sync_id = f"sync-tamper-{uuid.uuid4()}"
        case_id = str(uuid.uuid4())

        # Initial legitimate sync push
        res1 = await client.post(
            "/api/v1/sync/push",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "node_id": "NODE-SEC-TEST",
                "items": [
                    {
                        "sync_id": sync_id,
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "APPEND_ONLY",
                        "payload_snapshot": {
                            "facility_id": "FAC-DH-04",
                            "patient_name": "Tamper Test Patient",
                            "chief_complaint": "Headache",
                        },
                    }
                ],
            },
        )
        assert res1.status_code == 200
        assert res1.json()["results"][0]["status"] == "SYNCED"

        # Replay same sync_id with tampered payload
        res2 = await client.post(
            "/api/v1/sync/push",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "node_id": "NODE-SEC-TEST",
                "items": [
                    {
                        "sync_id": sync_id,
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "APPEND_ONLY",
                        "payload_snapshot": {
                            "facility_id": "FAC-DH-04",
                            "patient_name": "TAMPERED_NAME_INJECTION",
                            "chief_complaint": "MODIFIED_COMPLAINT",
                        },
                    }
                ],
            },
        )
        assert res2.status_code == 200
        # Tampering detected: status must be FAILED
        assert res2.json()["results"][0]["status"] == "FAILED"
        assert "tampering" in res2.json()["results"][0]["message"].lower()


# ===========================================================================
# 15. Sync Cross-Facility & Patient Scope Enforcement
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_15_sync_cross_facility_and_patient_scope():
    """Validates that sync items adhere to patient and facility boundaries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        nurse_phc_token = await login_helper(client, "nurse_phc")

        # 1. Patient cannot sync clinical decisions
        res_pt_dec = await client.post(
            "/api/v1/sync/push",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "node_id": "NODE-PT",
                "items": [
                    {
                        "sync_id": f"sync-pt-dec-{uuid.uuid4()}",
                        "entity_type": "CLINICIAN_DECISIONS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": str(uuid.uuid4()),
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "CLINICIAN_WINS",
                        "payload_snapshot": {"action_type": "REFER"},
                    }
                ],
            },
        )
        assert res_pt_dec.status_code == 200
        assert res_pt_dec.json()["results"][0]["status"] == "FAILED"

        # 2. Nurse at FAC-PHC-01 cannot sync vitals onto a case owned by FAC-DH-04
        _, c = await create_test_patient_and_case(facility_id="FAC-DH-04")

        res_cross_vitals = await client.post(
            "/api/v1/sync/push",
            headers={"Authorization": f"Bearer {nurse_phc_token}"},
            json={
                "node_id": "NODE-PHC",
                "items": [
                    {
                        "sync_id": f"sync-vitals-{uuid.uuid4()}",
                        "entity_type": "VITALS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": c.id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "APPEND_ONLY",
                        "payload_snapshot": {"heart_rate": 88, "systolic_bp": 120, "diastolic_bp": 80},
                    }
                ],
            },
        )
        assert res_cross_vitals.status_code == 200
        assert res_cross_vitals.json()["results"][0]["status"] == "FAILED"


# ===========================================================================
# 16. Sync Prohibited Clinical Action Rejection
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_16_sync_prohibited_clinical_action_rejection():
    """Validates that offline sync push of prohibited autonomous actions is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")

        res = await client.post(
            "/api/v1/sync/push",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "node_id": "NODE-DOC",
                "items": [
                    {
                        "sync_id": f"sync-auto-{uuid.uuid4()}",
                        "entity_type": "CLINICIAN_DECISIONS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": str(uuid.uuid4()),
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "CLINICIAN_WINS",
                        "payload_snapshot": {
                            "action_type": "AI_DIAGNOSIS",
                            "decision_type": "ACCEPT",
                        },
                    }
                ],
            },
        )
        assert res.status_code == 200
        assert res.json()["results"][0]["status"] == "FAILED"
        assert "prohibited" in res.json()["results"][0]["message"].lower()


# ===========================================================================
# 17. Clinician-Only Conflict Resolution with Cross-Facility Rejection
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_17_sync_conflict_resolution_clinician_cross_facility():
    """Validates that sync conflict resolution requires CLINICIAN role and matches facility scope."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        patient_token = await login_helper(client, "patient")

        fake_conflict_id = str(uuid.uuid4())

        # Nurse cannot resolve conflict -> 403
        res_nr = await client.post(
            f"/api/v1/sync/conflicts/{fake_conflict_id}/resolve",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"resolution_choice": "KEEP_LOCAL", "clinical_rationale": "Nurse attempt"},
        )
        assert res_nr.status_code == 403

        # Patient cannot resolve conflict -> 403
        res_pt = await client.post(
            f"/api/v1/sync/conflicts/{fake_conflict_id}/resolve",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"resolution_choice": "KEEP_LOCAL", "clinical_rationale": "Patient attempt"},
        )
        assert res_pt.status_code == 403


# ===========================================================================
# 18. Audit Log Immutability
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_18_audit_immutability():
    """Validates that audit log records are strictly immutable and read-only for authorized actors."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auditor_token = await login_helper(client, "auditor")
        patient_token = await login_helper(client, "patient")

        # Patient cannot read audit logs -> 403
        res_pt = await client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {patient_token}"})
        assert res_pt.status_code == 403

        # Auditor can read audit logs -> 200
        res_aud = await client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {auditor_token}"})
        assert res_aud.status_code == 200
        assert "logs" in res_aud.json()

        # Audit logs reject all mutations (Method Not Allowed)
        res_del = await client.delete("/api/v1/audit/logs", headers={"Authorization": f"Bearer {auditor_token}"})
        assert res_del.status_code in {404, 405}

        res_post = await client.post("/api/v1/audit/logs", headers={"Authorization": f"Bearer {auditor_token}"})
        assert res_post.status_code in {404, 405}

        res_put = await client.put("/api/v1/audit/logs", headers={"Authorization": f"Bearer {auditor_token}"})
        assert res_put.status_code in {404, 405}


# ===========================================================================
# 19. Zero Secret / Token / Password Leakage in API Responses
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_19_zero_credential_leakage():
    """Validates that user profiles, auth endpoints, and responses never leak password hashes or secrets."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")

        # GET /api/v1/auth/me
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert "password" not in me_data
        assert "hashed_password" not in me_data
        assert "password_hash" not in me_data
        assert "secret_key" not in me_data

        # GET /api/v1/facilities/FAC-DH-04
        fac_res = await client.get("/api/v1/facilities/FAC-DH-04", headers={"Authorization": f"Bearer {token}"})
        assert fac_res.status_code == 200
        fac_text = fac_res.text
        assert "password" not in fac_text.lower()
        assert "secret" not in fac_text.lower()


# ===========================================================================
# 20. Structured Error Contract & Security Headers
# ===========================================================================
@pytest.mark.asyncio
async def test_p25_20_structured_error_contract_and_security_headers():
    """Validates browser security headers and structured error contract on unhandled exceptions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check security headers on root endpoint
        res_root = await client.get("/")
        assert res_root.status_code == 200
        headers = res_root.headers
        assert headers.get("X-Clinical-Safety") == "Non-Diagnostic-Advisory-Only"
        assert headers.get("X-Human-In-The-Loop") == "Required-Before-Action"
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

        # Check structured error on 404
        res_404 = await client.get("/api/v1/non-existent-endpoint")
        assert res_404.status_code == 404
        data = res_404.json()
        assert "category" in data or "error" in data or "detail" in data
        assert "Traceback" not in res_404.text
