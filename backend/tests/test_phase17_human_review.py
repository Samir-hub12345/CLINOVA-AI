"""CLINOVA AI — Phase 17 Human Review + Case State Lifecycle Test Suite.

Continuous Care Intelligence System.
Phase 17: Human Review + Case State Lifecycle Foundation.
Grounded in DOC-03, DOC-06, DOC-07, DOC-08, DOC-14.

Complete Test Matrix:
A. clinician review queue retrieval
B. nurse cannot access clinician review actions
C. patient cannot access clinician review actions
D. authorized clinician starts review
E. unauthorized role cannot start clinician review
F. review state is persisted
G. evidence verification
H. evidence modification
I. original evidence remains preserved
J. evidence provenance remains preserved
K. conflict detection
L. explicit conflict resolution
M. conflict resolution requires authorized clinician
N. missing information request
O. transition to pending information
P. return from pending information
Q. human decision recording
R. rationale persistence
S. human override persistence
T. override requires rationale where required
U. prohibited autonomous action remains rejected
V. valid disposition
W. unauthorized disposition rejected
X. case closure requires valid authority
Y. invalid state transition rejected
Z. optimistic concurrency conflict
AA. duplicate/stale decision protection
AB. audit event creation
AC. review history retrieval
AD. facility-scope enforcement
AE. forged role header fails
AF. forged clinician identity fails
AG. forged facility ID fails
AH. case state consistency
AI. deterministic support remains distinct from human decision
AJ. emergency review priority
AK. emergency administrative incompleteness does not block appropriate review
AL. transaction rollback
AM. structured error contract
AN. synthetic data only
AO. reload persistence
AP. complete review lifecycle

Adversarial Tests:
- clinician ID spoofing
- role escalation via headers
- stale state version
- duplicate finalize
- modifying a closed case
- changing state directly
- cross-facility review
- client-supplied disposition authority
- client-supplied priority override
- client-supplied "verified" evidence
- client-supplied final decision without auth
- bypassing required rationale
- calling clinician endpoints without authentication
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
    PROHIBITED_CLINICAL_ACTIONS,
)
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Patient,
    Encounter,
    Case,
    Vital,
    Evidence,
    ReviewAction,
    ClinicianDecision,
    CaseOutcome,
    CaseStateTransition,
    AuditEvent,
    FollowUpQuestion,
    FollowUpAnswer,
    User,
    utc_now,
)
from app.domain.state_machine import (
    STATE_INTAKE_RECORDED,
    STATE_TRIAGE_PENDING,
    STATE_TRIAGE_IN_PROGRESS,
    STATE_PENDING_INFORMATION,
    STATE_CLINICIAN_REVIEW_REQUIRED,
    STATE_REVIEW_IN_PROGRESS,
    STATE_DISPOSITION_PENDING,
    STATE_CLOSED,
    execute_state_transition,
)


@pytest.fixture(autouse=True)
async def setup_phase17_environment():
    """Ensure DB schema is initialized and configure strict authentication defaults."""
    await init_db()
    original_legacy_headers = settings.ALLOW_LEGACY_ACTOR_HEADERS
    original_legacy_anon = settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK
    settings.ALLOW_LEGACY_ACTOR_HEADERS = False
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False

    yield

    settings.ALLOW_LEGACY_ACTOR_HEADERS = original_legacy_headers
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = original_legacy_anon


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Helper to authenticate and return a bearer JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


async def create_test_case_helper(
    client: AsyncClient,
    clinician_token: str,
    nurse_token: str,
    facility_id: str = "FAC-DH-04",
    pathway: str = "REGULAR_STANDARD",
    chief_complaint: str = "Chest discomfort and sweating",
    advance_to_review: bool = True,
) -> Dict[str, Any]:
    """Helper to create a case, add vitals and evidence, and advance it to CLINICIAN_REVIEW_REQUIRED."""
    # 1. Intake
    intake_res = await client.post(
        "/api/v1/intake/submit",
        headers={"Authorization": f"Bearer {nurse_token}"},
        json={
            "facility_id": facility_id,
            "pathway": pathway,
            "reported_age_bracket": "45-54",
            "biological_sex": "MALE",
            "preferred_language": "en",
            "chief_complaint": chief_complaint,
            "symptom_duration": "3 hours",
            "consent_confirmed": True,
        },
    )
    assert intake_res.status_code == 200, f"Intake submission failed: {intake_res.text}"
    case_id = intake_res.json()["case_id"]

    # 2. Add vital signs
    vital_res = await client.post(
        f"/api/v1/cases/{case_id}/vitals",
        headers={"Authorization": f"Bearer {nurse_token}"},
        json={
            "heart_rate": 88,
            "systolic_bp": 130,
            "diastolic_bp": 82,
            "spo2_percent": 97,
            "respiratory_rate": 18,
            "temperature_celsius": 37.1,
            "avpu_score": "ALERT",
            "supplemental_o2": False,
        },
    )
    assert vital_res.status_code == 200, f"Adding vitals failed: {vital_res.text}"

    # 3. Add clinical evidence
    ev_id = f"ev-{uuid.uuid4().hex[:8]}"
    async with async_session_factory() as session:
        ev = Evidence(
            id=ev_id,
            case_id=case_id,
            source_class="NURSE_ENTRY",
            epistemic_state="KNOWN",
            parameter_name="ECG_ST_SEGMENT",
            content_value="ST elevation in anterior leads",
            confidence_score=0.95,
            provenance_metadata={"recorder": "usr-nurse-02", "source": "12-lead ECG"},
            captured_timestamp=utc_now(),
        )
        session.add(ev)
        await session.commit()

    # 4. Advance case from INTAKE_RECORDED -> TRIAGE_IN_PROGRESS -> CLINICIAN_REVIEW_REQUIRED
    if advance_to_review:
        # Nurse starts triage
        st_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "action": "START_TRIAGE",
                "reason": "Nurse initiating emergency triage protocol",
            },
        )
        assert st_res.status_code == 200, f"Start triage failed: {st_res.text}"

        # Nurse submits triage -> moves to CLINICIAN_REVIEW_REQUIRED
        sub_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "action": "SUBMIT_TRIAGE",
                "reason": "Nurse completed triage, attending physician review required",
            },
        )
        assert sub_res.status_code == 200, f"Submit triage failed: {sub_res.text}"

    return {"case_id": case_id, "evidence_id": ev_id}


# ===========================================================================
# A. CLINICIAN REVIEW QUEUE RETRIEVAL
# ===========================================================================

@pytest.mark.asyncio
async def test_A_clinician_review_queue_retrieval():
    """A: Authorized clinician retrieves review queue with explainable deterministic signals."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.get(
            "/api/v1/cases/review-queue",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "queue" in body
        assert body["is_synthetic_mode"] is True
        assert body["total_cases"] >= 1

        # Locate our case
        case_items = [q for q in body["queue"] if q["case_id"] == case_id]
        assert len(case_items) == 1
        item = case_items[0]
        assert item["review_status"] == "PENDING_REVIEW"
        assert item["current_state"] == STATE_CLINICIAN_REVIEW_REQUIRED
        assert "waiting_minutes" in item
        assert "priority_tier" in item
        assert "acuity_tier" in item


# ===========================================================================
# B. NURSE CANNOT ACCESS CLINICIAN REVIEW ACTIONS
# ===========================================================================

@pytest.mark.asyncio
async def test_B_nurse_cannot_access_clinician_review_actions():
    """B: Nurse is blocked from performing clinician-only review, decision, and disposition actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        # 1. Start review blocked
        r1 = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"notes": "Nurse attempting review"},
        )
        assert r1.status_code == 403

        # 2. Verify evidence blocked
        r2 = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/verify",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"notes": "Nurse verifying"},
        )
        assert r2.status_code == 403

        # 3. Modify evidence blocked
        r3 = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/modify",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"updated_value": "Normal ECG", "reason": "Nurse edit"},
        )
        assert r3.status_code == 403

        # 4. Resolve conflict blocked
        r4 = await client.post(
            f"/api/v1/cases/{case_id}/evidence/resolve-conflict",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"authoritative_evidence_id": ev_id, "resolution_rationale": "Nurse resolving"},
        )
        assert r4.status_code == 403

        # 5. Record clinical decision blocked
        r5 = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Nurse decision"},
        )
        assert r5.status_code == 403

        # 6. Finalize disposition blocked
        r6 = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"disposition_type": "DISCHARGE_HOME", "clinical_summary": "Nurse discharge"},
        )
        assert r6.status_code == 403

        # 7. Close case blocked
        r7 = await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"closure_reason": "Nurse closing encounter"},
        )
        assert r7.status_code == 403


# ===========================================================================
# C. PATIENT CANNOT ACCESS CLINICIAN REVIEW ACTIONS
# ===========================================================================

@pytest.mark.asyncio
async def test_C_patient_cannot_access_clinician_review_actions():
    """C: Patient role cannot inspect review queue, review context, review history, or execute actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")
        patient_token = await login_helper(client, "patient_09")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Review queue barred
        q_res = await client.get(
            "/api/v1/cases/review-queue",
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert q_res.status_code == 403

        # Review context barred
        ctx_res = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert ctx_res.status_code == 403

        # Review history barred
        hist_res = await client.get(
            f"/api/v1/cases/{case_id}/review-history",
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert hist_res.status_code == 403

        # Review actions barred
        act_res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"notes": "Patient trying to start review"},
        )
        assert act_res.status_code == 403


# ===========================================================================
# D. AUTHORIZED CLINICIAN STARTS REVIEW
# ===========================================================================

@pytest.mark.asyncio
async def test_D_authorized_clinician_starts_review():
    """D: Authorized clinician initiates review session, advancing state to REVIEW_IN_PROGRESS."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Attending Dr. Priya Sharma starting evaluation"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["current_state"] == STATE_REVIEW_IN_PROGRESS
        assert body["reviewer_id"] == "usr-doc-01"
        assert body["state_version"] >= 1


# ===========================================================================
# E. UNAUTHORIZED ROLE CANNOT START CLINICIAN REVIEW
# ===========================================================================

@pytest.mark.asyncio
async def test_E_unauthorized_role_cannot_start_clinician_review():
    """E: Unauthenticated users and unauthorized roles fail to start clinical review."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # 1. Unauthenticated request -> 401
        unauth = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            json={"notes": "Anonymous review start attempt"},
        )
        assert unauth.status_code == 401

        # 2. Facility Admin (non-clinician) -> 403
        admin_token = await login_helper(client, "facility_admin")
        adm_res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"notes": "Admin review start attempt"},
        )
        assert adm_res.status_code == 403


# ===========================================================================
# F. REVIEW STATE IS PERSISTED
# ===========================================================================

@pytest.mark.asyncio
async def test_F_review_state_is_persisted():
    """F: Clinical review session state and ReviewAction are durably persisted in database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Doctor session start durable test"},
        )

        async with async_session_factory() as session:
            c = await session.get(Case, case_id)
            assert c is not None
            assert c.current_state == STATE_REVIEW_IN_PROGRESS

            # Check ReviewAction record
            stmt = select(ReviewAction).where(ReviewAction.case_id == case_id)
            actions = (await session.execute(stmt)).scalars().all()
            assert any(a.action == "START_REVIEW" for a in actions)


# ===========================================================================
# G. EVIDENCE VERIFICATION
# ===========================================================================

@pytest.mark.asyncio
async def test_G_evidence_verification():
    """G: Clinician verifies evidence item, updating epistemic status to VERIFIED with provenance metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        # Start review
        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/verify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"rationale": "Verified on 12-lead monitor: acute ST elevations confirmed in V1-V4."},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["epistemic_state"] == "VERIFIED"
        assert body["verification_metadata"]["verified_role"] == ROLE_CLINICIAN


# ===========================================================================
# H. EVIDENCE MODIFICATION
# ===========================================================================

@pytest.mark.asyncio
async def test_H_evidence_modification():
    """H: Clinician modifies evidence value with mandatory clinical rationale."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/modify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "updated_value": "Extensive anterior STEMI with reciprocal depression in III/aVF",
                "reason": "Expert cardiological re-interpretation of ECG morphology",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["content_value"] == "Extensive anterior STEMI with reciprocal depression in III/aVF"
        assert body["epistemic_state"] == "VERIFIED"


# ===========================================================================
# I. ORIGINAL EVIDENCE REMAINS PRESERVED
# ===========================================================================

@pytest.mark.asyncio
async def test_I_original_evidence_remains_preserved():
    """I: Modifying an evidence observation preserves previous value in append-oriented modification history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # Modify evidence
        await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/modify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "updated_value": "Corrected observation value",
                "reason": "Re-measured lead baseline",
            },
        )

        async with async_session_factory() as session:
            ev = await session.get(Evidence, ev_id)
            assert ev is not None
            meta = ev.transformation_metadata or {}
            history = meta.get("modification_history", [])
            assert len(history) >= 1
            # Original value is preserved in history
            assert history[0]["previous_value"] == "ST elevation in anterior leads"
            assert history[0]["reason"] == "Re-measured lead baseline"


# ===========================================================================
# J. EVIDENCE PROVENANCE REMAINS PRESERVED
# ===========================================================================

@pytest.mark.asyncio
async def test_J_evidence_provenance_remains_preserved():
    """J: Evidence modification does not overwrite historical source_class or origin provenance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/modify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"updated_value": "Updated value", "reason": "Physician clinical judgment adjustment"},
        )

        async with async_session_factory() as session:
            ev = await session.get(Evidence, ev_id)
            assert ev is not None
            # Source class remains NURSE_ENTRY rather than being forged as clinician-entered origin
            assert ev.source_class == "NURSE_ENTRY"
            assert ev.provenance_metadata.get("source") == "12-lead ECG"


# ===========================================================================
# K. CONFLICT DETECTION
# ===========================================================================

@pytest.mark.asyncio
async def test_K_conflict_detection():
    """K: Epistemic conflict detection surfaces contradictory evidence observations in review context."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Insert a second contradictory evidence record for the same parameter
        async with async_session_factory() as session:
            conf_ev = Evidence(
                id=f"ev-conf-{uuid.uuid4().hex[:8]}",
                case_id=case_id,
                source_class="PATIENT_REPORT",
                epistemic_state="CONFLICTING",
                parameter_name="ECG_ST_SEGMENT",
                content_value="Normal ECG reported by outside clinic yesterday",
                confidence_score=0.70,
                provenance_metadata={"source": "Patient paper discharge summary"},
                captured_timestamp=utc_now(),
            )
            session.add(conf_ev)
            await session.commit()

        # Retrieve review context
        ctx_res = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert ctx_res.status_code == 200
        body = ctx_res.json()
        conflicts = body.get("conflicts", [])
        assert len(conflicts) >= 1
        assert any("ECG_ST_SEGMENT" in str(c["parameter_name"]) for c in conflicts)


# ===========================================================================
# L. EXPLICIT CONFLICT RESOLUTION
# ===========================================================================

@pytest.mark.asyncio
async def test_L_explicit_conflict_resolution():
    """L: Clinician explicitly resolves epistemic conflict, designating authoritative record."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        primary_ev_id = test_case["evidence_id"]

        # Add contradictory item
        conf_ev_id = f"ev-conf-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            conf_ev = Evidence(
                id=conf_ev_id,
                case_id=case_id,
                source_class="PATIENT_REPORT",
                epistemic_state="CONFLICTING",
                parameter_name="ECG_ST_SEGMENT",
                content_value="Normal ECG yesterday",
                confidence_score=0.50,
                captured_timestamp=utc_now(),
            )
            session.add(conf_ev)
            await session.commit()

        # Resolve conflict designating primary_ev_id as authoritative
        res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/resolve-conflict",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "authoritative_evidence_id": primary_ev_id,
                "parameter_name": "ECG_ST_SEGMENT",
                "resolution_rationale": "Bedside 12-lead ECG is current and diagnostic; outside report is outdated.",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "RESOLVED"

        # Check DB states
        async with async_session_factory() as session:
            ev_auth = await session.get(Evidence, primary_ev_id)
            ev_comp = await session.get(Evidence, conf_ev_id)
            assert ev_auth.epistemic_state == "VERIFIED"
            assert ev_comp.epistemic_state == "SUPERSEDED"


# ===========================================================================
# M. CONFLICT RESOLUTION REQUIRES AUTHORIZED CLINICIAN
# ===========================================================================

@pytest.mark.asyncio
async def test_M_conflict_resolution_requires_authorized_clinician():
    """M: Unlicensed roles (nurse, patient) cannot execute conflict resolution."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/resolve-conflict",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "authoritative_evidence_id": ev_id,
                "resolution_rationale": "Nurse attempt to resolve conflict",
            },
        )
        assert res.status_code == 403


# ===========================================================================
# N. MISSING INFORMATION REQUEST
# ===========================================================================

@pytest.mark.asyncio
async def test_N_missing_information_request():
    """N: Reviewer requests missing clinical data, generating traceable FollowUpQuestion."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/request-information",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "question_text": "Did patient take aspirin or antiplatelets prior to arrival?",
                "reason": "Critical prerequisite before thrombolytic or cath lab activation",
                "priority": "CRITICAL",
                "target_role": "PATIENT",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["current_state"] == STATE_PENDING_INFORMATION
        assert "question_id" in body


# ===========================================================================
# O. TRANSITION TO PENDING INFORMATION
# ===========================================================================

@pytest.mark.asyncio
async def test_O_transition_to_pending_information():
    """O: Requesting missing information transitions case state to PENDING_INFORMATION."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        await client.post(
            f"/api/v1/cases/{case_id}/request-information",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"question_text": "Clarify symptom onset exact time", "reason": "Thrombolysis window check"},
        )

        async with async_session_factory() as session:
            c = await session.get(Case, case_id)
            assert c.current_state == STATE_PENDING_INFORMATION


# ===========================================================================
# P. RETURN FROM PENDING INFORMATION
# ===========================================================================

@pytest.mark.asyncio
async def test_P_return_from_pending_information():
    """P: Providing missing information records answer and returns case to CLINICIAN_REVIEW_REQUIRED."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        q_res = await client.post(
            f"/api/v1/cases/{case_id}/request-information",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"question_text": "Confirm aspirin ingestion", "reason": "Pharmacotherapy check"},
        )
        q_id = q_res.json()["question_id"]

        # Provide information
        ans_res = await client.post(
            f"/api/v1/cases/{case_id}/provide-information",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "question_id": q_id,
                "answer_text": "Patient took 325mg aspirin at home 45 minutes ago.",
            },
        )
        assert ans_res.status_code == 200
        assert ans_res.json()["current_state"] == STATE_CLINICIAN_REVIEW_REQUIRED


# ===========================================================================
# Q. HUMAN DECISION RECORDING
# ===========================================================================

@pytest.mark.asyncio
async def test_Q_human_decision_recording():
    """Q: Attending clinician records authoritative clinical judgment and management plan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "ACCEPT",
                "clinical_rationale": "High-risk acute coronary syndrome verified; admit to CCU for immediate intervention.",
                "clinical_impression": "Acute Anterior STEMI Killip Class I",
                "treatment_plan": "Dual antiplatelet, heparin bolus, emergency cardiac cath lab activation",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["current_state"] == STATE_DISPOSITION_PENDING
        assert body["is_override"] is False
        assert body["clinician_id"] == "usr-doc-01"


# ===========================================================================
# R. RATIONALE PERSISTENCE
# ===========================================================================

@pytest.mark.asyncio
async def test_R_rationale_persistence():
    """R: Clinical decision rationale is durably stored; empty rationale is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # Empty rationale rejected with 422
        bad_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "   "},
        )
        assert bad_res.status_code == 422

        # Valid rationale accepted and stored
        good_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Detailed documented physician rationale"},
        )
        assert good_res.status_code == 200

        async with async_session_factory() as session:
            stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case_id)
            dec = (await session.execute(stmt)).scalars().first()
            assert dec is not None
            assert dec.clinical_rationale == "Detailed documented physician rationale"


# ===========================================================================
# S. HUMAN OVERRIDE PERSISTENCE
# ===========================================================================

@pytest.mark.asyncio
async def test_S_human_override_persistence():
    """S: Clinician explicitly overrides system suggestion, persisting override flag and rationale."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "OVERRIDE",
                "is_override": True,
                "override_reason": "Patient is clinically compensated despite borderline vitals; observe in HDU rather than immediate ICU intubation.",
                "clinical_rationale": "Physician clinical judgment overrides algorithm recommendation.",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["is_override"] is True
        assert "borderline vitals" in body["override_reason"].lower()


# ===========================================================================
# T. OVERRIDE REQUIRES RATIONALE WHERE REQUIRED
# ===========================================================================

@pytest.mark.asyncio
async def test_T_override_requires_rationale_where_required():
    """T: Override submission without mandatory rationale or override reason fails validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "OVERRIDE",
                "is_override": True,
                "clinical_rationale": "",
                "override_reason": "",
            },
        )
        assert res.status_code == 422


# ===========================================================================
# U. PROHIBITED AUTONOMOUS ACTION REMAINS REJECTED
# ===========================================================================

@pytest.mark.asyncio
async def test_U_prohibited_autonomous_action_remains_rejected():
    """U: Prohibited autonomous clinical actions (AI_DIAGNOSIS, AUTO_PRESCRIBE, etc.) are strictly blocked."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        for prohibited in ["AI_DIAGNOSIS", "AUTO_PRESCRIBE", "AI_ADMISSION", "AI_DISCHARGE", "AUTHORIZE_PROCEDURE"]:
            res = await client.post(
                f"/api/v1/cases/{case_id}/decision",
                headers={"Authorization": f"Bearer {clinician_token}"},
                json={"decision_type": prohibited, "clinical_rationale": "Attempting prohibited autonomous action"},
            )
            assert res.status_code in {422, 400}, f"Prohibited action '{prohibited}' was not rejected!"


# ===========================================================================
# V. VALID DISPOSITION
# ===========================================================================

@pytest.mark.asyncio
async def test_V_valid_disposition():
    """V: Clinician finalizes clinical disposition (ADMIT_INPATIENT, DISCHARGE_HOME, etc.)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # Record decision
        await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Admit to telemetry bed"},
        )

        # Finalize disposition closing case
        res = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "disposition_type": "ADMIT_INPATIENT",
                "clinical_summary": "Transferred to Inpatient Cardiology Ward in stable condition.",
                "close_case": True,
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["current_state"] == STATE_CLOSED
        assert body["is_closed"] is True


# ===========================================================================
# W. UNAUTHORIZED DISPOSITION REJECTED
# ===========================================================================

@pytest.mark.asyncio
async def test_W_unauthorized_disposition_rejected():
    """W: Nurse or unauthenticated actor cannot record case disposition."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"disposition_type": "DISCHARGE_HOME", "clinical_summary": "Unauthorized discharge"},
        )
        assert res.status_code == 403


# ===========================================================================
# X. CASE CLOSURE REQUIRES VALID AUTHORITY
# ===========================================================================

@pytest.mark.asyncio
async def test_X_case_closure_requires_valid_authority():
    """X: Closing encounter requires clinician or system admin authority with mandatory reason."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # Nurse close attempt fails
        nurse_close = await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"closure_reason": "Nurse close attempt"},
        )
        assert nurse_close.status_code == 403

        # Clinician close succeeds
        doc_close = await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"closure_reason": "Clinical encounter completed, patient safely transferred"},
        )
        assert doc_close.status_code == 200
        assert doc_close.json()["is_closed"] is True


# ===========================================================================
# Y. INVALID STATE TRANSITION REJECTED
# ===========================================================================

@pytest.mark.asyncio
async def test_Y_invalid_state_transition_rejected():
    """Y: Arbitrary or invalid state transition jumps (e.g. CLOSED -> REVIEW_IN_PROGRESS) fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Close the case
        await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"closure_reason": "Completed"},
        )

        # Attempt to start review on closed case
        res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Trying to revive closed case"},
        )
        assert res.status_code == 422


# ===========================================================================
# Z. OPTIMISTIC CONCURRENCY CONFLICT
# ===========================================================================

@pytest.mark.asyncio
async def test_Z_optimistic_concurrency_conflict():
    """Z: Submitting a stale state_version returns structured 409 CONFLICT."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Start review advances version
        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # Submit decision with stale expected_state_version = 0
        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "ACCEPT",
                "clinical_rationale": "Stale version check",
                "expected_state_version": 0,
            },
        )
        assert res.status_code == 409
        body = res.json()
        err = body.get("error", body.get("detail", {}))
        assert err.get("code") == "CONFLICT" or err.get("category") == "CONFLICT"


# ===========================================================================
# AA. DUPLICATE / STALE DECISION PROTECTION
# ===========================================================================

@pytest.mark.asyncio
async def test_AA_duplicate_stale_decision_protection():
    """AA: Duplicate decision submissions using already-mutated version are rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        start_res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        v = start_res.json()["state_version"]

        # First decision succeeds
        d1 = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "First decision", "expected_state_version": v},
        )
        assert d1.status_code == 200

        # Duplicate decision with original version v fails with 409
        d2 = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Second decision duplicate", "expected_state_version": v},
        )
        assert d2.status_code == 409


# ===========================================================================
# AB. AUDIT EVENT CREATION
# ===========================================================================

@pytest.mark.asyncio
async def test_AB_audit_event_creation():
    """AB: Every clinical review transition creates an immutable AuditEvent."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Audit trace initiation"},
        )

        async with async_session_factory() as session:
            stmt = select(AuditEvent).where(AuditEvent.case_id == case_id)
            audits = (await session.execute(stmt)).scalars().all()
            assert len(audits) >= 1
            assert any(a.actor_role == ROLE_CLINICIAN for a in audits)


# ===========================================================================
# AC. REVIEW HISTORY RETRIEVAL
# ===========================================================================

@pytest.mark.asyncio
async def test_AC_review_history_retrieval():
    """AC: Chronological review history exposes review_actions, decisions, transitions, and audits."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/verify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"rationale": "Verified in history test"},
        )
        await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Decision in history test"},
        )

        res = await client.get(
            f"/api/v1/cases/{case_id}/review-history",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert len(body["review_actions"]) >= 2
        assert len(body["decisions"]) >= 1
        assert len(body["transitions"]) >= 1
        assert len(body["audit_events"]) >= 1


# ===========================================================================
# AD. FACILITY-SCOPE ENFORCEMENT
# ===========================================================================

@pytest.mark.asyncio
async def test_AD_facility_scope_enforcement():
    """AD: Clinician at FAC-DH-04 cannot access or review case belonging to FAC-PHC-01."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")  # Assigned to FAC-DH-04
        nurse_phc_token = await login_helper(client, "nurse_phc")  # Assigned to FAC-PHC-01

        # Create case at FAC-PHC-01
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_phc_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "30-39",
                "biological_sex": "FEMALE",
                "preferred_language": "en",
                "chief_complaint": "Localized fever at rural post",
                "symptom_duration": "1 day",
                "consent_confirmed": True,
            },
        )
        case_id = res.json()["case_id"]

        # Clinician at FAC-DH-04 attempts to access foreign facility case -> 404 (per security policy)
        access_res = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert access_res.status_code == 404


# ===========================================================================
# AE. FORGED ROLE HEADER FAILS
# ===========================================================================

@pytest.mark.asyncio
async def test_AE_forged_role_header_fails():
    """AE: Sending X-Actor-Role: CLINICIAN with nurse credentials does not elevate privileges."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Nurse sends forged role header
        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={
                "Authorization": f"Bearer {nurse_token}",
                "X-Actor-Role": "CLINICIAN",
            },
            json={"decision_type": "ACCEPT", "clinical_rationale": "Forged role attempt"},
        )
        assert res.status_code == 403


# ===========================================================================
# AF. FORGED CLINICIAN IDENTITY FAILS
# ===========================================================================

@pytest.mark.asyncio
async def test_AF_forged_clinician_identity_fails():
    """AF: Spoofing X-Actor-Id: usr-doc-01 does not bypass server identity derivation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={
                "Authorization": f"Bearer {nurse_token}",
                "X-Actor-Id": "usr-doc-01",
                "X-Actor-Role": "CLINICIAN",
            },
            json={"notes": "Spoofed identity start attempt"},
        )
        assert res.status_code == 403


# ===========================================================================
# AG. FORGED FACILITY ID FAILS
# ===========================================================================

@pytest.mark.asyncio
async def test_AG_forged_facility_id_fails():
    """AG: Client-supplied X-Facility-ID header cannot access foreign facility data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")  # Facility FAC-DH-04
        nurse_phc_token = await login_helper(client, "nurse_phc")  # Facility FAC-PHC-01

        # Create PHC case
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_phc_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "30-39",
                "biological_sex": "MALE",
                "preferred_language": "en",
                "chief_complaint": "Foreign facility check",
                "symptom_duration": "1 day",
                "consent_confirmed": True,
            },
        )
        phc_case_id = res.json()["case_id"]

        # Clinician attempts access with spoofed header
        check = await client.get(
            f"/api/v1/cases/{phc_case_id}/review-context",
            headers={
                "Authorization": f"Bearer {clinician_token}",
                "X-Facility-ID": "FAC-PHC-01",
            },
        )
        assert check.status_code == 404


# ===========================================================================
# AH. CASE STATE CONSISTENCY
# ===========================================================================

@pytest.mark.asyncio
async def test_AH_case_state_consistency():
    """AH: Server invariants prevent contradictory actions on closed cases."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        # Close the case
        await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"closure_reason": "Case encounter discharged and closed"},
        )

        # 1. Decision on closed case fails
        d_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Late decision"},
        )
        assert d_res.status_code == 422

        # 2. Modify evidence on closed case fails
        m_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/modify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"updated_value": "Late edit", "reason": "Late correction"},
        )
        assert m_res.status_code == 422


# ===========================================================================
# AI. DETERMINISTIC SUPPORT REMAINS DISTINCT FROM HUMAN DECISION
# ===========================================================================

@pytest.mark.asyncio
async def test_AI_deterministic_support_remains_distinct_from_human_decision():
    """AI: System-determined support contains non-diagnostic disclaimer and is clearly distinct from decisions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res.status_code == 200
        body = res.json()

        sys_supp = body["system_deterministic_support"]
        assert sys_supp["is_system_determined"] is True
        assert sys_supp["is_authoritative_clinical_decision"] is False
        assert "Non-diagnostic and advisory only" in sys_supp["disclaimer"]


# ===========================================================================
# AJ. EMERGENCY REVIEW PRIORITY
# ===========================================================================

@pytest.mark.asyncio
async def test_AJ_emergency_review_priority():
    """AJ: Emergency pathway cases and cases with critical red flags are given top queue priority."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        # Create emergency case
        em_case = await create_test_case_helper(
            client,
            clinician_token,
            nurse_token,
            pathway="EMERGENCY",
            chief_complaint="Severe crushing retrosternal chest pain and diaphoresis",
        )

        res = await client.get(
            "/api/v1/cases/review-queue",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["emergency_count"] >= 1
        queue = body["queue"]

        em_items = [q for q in queue if q["case_id"] == em_case["case_id"]]
        assert len(em_items) == 1
        assert em_items[0]["emergency_active"] is True


# ===========================================================================
# AK. EMERGENCY ADMINISTRATIVE INCOMPLETENESS DOES NOT BLOCK REVIEW
# ===========================================================================

@pytest.mark.asyncio
async def test_AK_emergency_administrative_incompleteness_does_not_block_appropriate_review():
    """AK: Resuscitation-first principle: missing vitals do not prevent clinician from starting review."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        # Create case with zero vitals
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "reported_age_bracket": "60-69",
                "biological_sex": "MALE",
                "preferred_language": "en",
                "chief_complaint": "Acute collapse with suspected cardiac arrest",
                "symptom_duration": "5 minutes",
                "consent_confirmed": True,
            },
        )
        case_id = res.json()["case_id"]

        # Nurse immediately escalates without waiting for administrative vitals
        await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"action": "ESCALATE", "reason": "Immediate resuscitation bay escalation"},
        )

        # Clinician can immediately start review
        start_res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Doctor responding to resuscitation bay call"},
        )
        assert start_res.status_code == 200
        assert start_res.json()["current_state"] == STATE_REVIEW_IN_PROGRESS


# ===========================================================================
# AL. TRANSACTION ROLLBACK
# ===========================================================================

@pytest.mark.asyncio
async def test_AL_transaction_rollback():
    """AL: Database session rollback leaves state and version completely unchanged on abort."""
    async with async_session_factory() as session:
        pt = Patient(
            id=f"pt-roll-{uuid.uuid4().hex[:8]}",
            synthetic_id=f"PT-SYN-ROLL-{uuid.uuid4().hex[:4]}",
            age_bracket="40-49",
            biological_sex="FEMALE",
            is_synthetic=True,
            created_at=utc_now(),
        )
        session.add(pt)
        enc = Encounter(
            id=f"enc-roll-{uuid.uuid4().hex[:8]}",
            patient_id=pt.id,
            facility_id="FAC-DH-04",
            source_actor_id="usr-nurse-02",
            source_actor_role="NURSE",
            started_at=utc_now(),
            created_at=utc_now(),
        )
        session.add(enc)

        # Create a sample case
        case = Case(
            id=f"case-roll-{uuid.uuid4().hex[:8]}",
            case_number=f"CN-ROLL-{uuid.uuid4().hex[:4]}",
            patient_id=pt.id,
            encounter_id=enc.id,
            facility_id="FAC-DH-04",
            pathway="REGULAR_STANDARD",
            current_state=STATE_CLINICIAN_REVIEW_REQUIRED,
            status=STATE_CLINICIAN_REVIEW_REQUIRED,
            state_version=3,
            presenting_complaint="Rollback verification case",
            created_at=utc_now(),
        )
        session.add(case)
        await session.commit()

    # Now simulate an uncommitted transaction and rollback
    async with async_session_factory() as session:
        c = await session.get(Case, case.id)
        c.current_state = STATE_CLOSED
        c.state_version = 99
        await session.rollback()

    # Verify original state persisted
    async with async_session_factory() as session:
        c_fresh = await session.get(Case, case.id)
        assert c_fresh.current_state == STATE_CLINICIAN_REVIEW_REQUIRED
        assert c_fresh.state_version == 3


# ===========================================================================
# AM. STRUCTURED ERROR CONTRACT
# ===========================================================================

@pytest.mark.asyncio
async def test_AM_structured_error_contract():
    """AM: All rejected actions return consistent JSON detail with category, message, and correlation_id."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Test", "expected_state_version": 9999},
        )
        assert res.status_code == 409
        body = res.json()
        assert "error" in body or "detail" in body
        err = body.get("error", body.get("detail", {}))
        assert err.get("code") == "CONFLICT" or err.get("category") == "CONFLICT"
        assert "message" in err
        assert "correlation_id" in err


# ===========================================================================
# AN. SYNTHETIC DATA ONLY
# ===========================================================================

@pytest.mark.asyncio
async def test_AN_synthetic_data_only():
    """AN: All review payloads preserve synthetic data flags as mandated by DOC-09."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        q_res = await client.get(
            "/api/v1/cases/review-queue",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert q_res.json()["is_synthetic_mode"] is True

        ctx_res = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert ctx_res.json()["is_synthetic_mode"] is True
        assert ctx_res.json()["patient"]["is_synthetic"] is True


# ===========================================================================
# AO. RELOAD PERSISTENCE
# ===========================================================================

@pytest.mark.asyncio
async def test_AO_reload_persistence():
    """AO: Review decisions and actions reloaded from fresh database sessions match committed data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "ACCEPT",
                "clinical_rationale": "Verified diagnostic impression for persistence test",
                "treatment_plan": "Oral beta blockers and serial ECG monitoring",
            },
        )

        # Fresh DB session inspection
        async with async_session_factory() as session:
            stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case_id)
            dec = (await session.execute(stmt)).scalars().first()
            assert dec is not None
            assert "Oral beta blockers" in dec.treatment_plan
            assert dec.clinician_id == "usr-doc-01"


# ===========================================================================
# AP. COMPLETE REVIEW LIFECYCLE
# ===========================================================================

@pytest.mark.asyncio
async def test_AP_complete_review_lifecycle():
    """AP: End-to-end integration: Intake -> Triage -> Review -> Verification -> Decision -> Disposition -> Close."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        # 1. Intake
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "50-59",
                "biological_sex": "FEMALE",
                "preferred_language": "en",
                "chief_complaint": "Acute onset epigastric pain and diaphoresis",
                "symptom_duration": "2 hours",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # 2. Vitals
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 84,
                "systolic_bp": 128,
                "diastolic_bp": 80,
                "spo2_percent": 98,
                "respiratory_rate": 16,
                "temperature_celsius": 36.9,
                "avpu_score": "ALERT",
            },
        )

        # 3. Evidence
        ev_id = f"ev-life-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev = Evidence(
                id=ev_id,
                case_id=case_id,
                source_class="NURSE_ENTRY",
                epistemic_state="KNOWN",
                parameter_name="TROPONIN_I",
                content_value="0.45 ng/mL (elevated)",
                confidence_score=0.98,
                captured_timestamp=utc_now(),
            )
            session.add(ev)
            await session.commit()

        # 4. Nurse Triage
        await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"action": "START_TRIAGE", "reason": "Triage starting"},
        )
        await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"action": "SUBMIT_TRIAGE", "reason": "Triage completed, physician review needed"},
        )

        # 5. Clinician Starts Review
        r_start = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert r_start.status_code == 200

        # 6. Clinician Verifies Evidence
        v_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/verify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"rationale": "High-sensitivity troponin authenticated from central laboratory."},
        )
        assert v_res.status_code == 200

        # 7. Clinician Requests & Receives Missing Info
        q_res = await client.post(
            f"/api/v1/cases/{case_id}/request-information",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"question_text": "History of prior myocardial infarction?", "reason": "Risk stratification"},
        )
        q_id = q_res.json()["question_id"]

        ans_res = await client.post(
            f"/api/v1/cases/{case_id}/provide-information",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"question_id": q_id, "answer_text": "No previous cardiac history documented."},
        )
        assert ans_res.status_code == 200

        # 8. Clinician Records Clinical Decision
        dec_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "decision_type": "ACCEPT",
                "clinical_rationale": "Confirmed Non-ST Elevation Myocardial Infarction (NSTEMI); initiate dual antiplatelet and CCU admission.",
                "clinical_impression": "NSTEMI intermediate-to-high risk",
                "treatment_plan": "Aspirin, Ticagrelor, Enoxaparin, early coronary angiography within 24 hours",
            },
        )
        assert dec_res.status_code == 200

        # 9. Clinician Finalizes Disposition
        disp_res = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "disposition_type": "ADMIT_INPATIENT",
                "clinical_summary": "Transferred to Coronary Care Unit bed 4 under Dr. Sharma.",
                "close_case": True,
            },
        )
        assert disp_res.status_code == 200
        assert disp_res.json()["is_closed"] is True
        assert disp_res.json()["current_state"] == STATE_CLOSED


# ===========================================================================
# AQ. EVIDENCE REJECTION
# ===========================================================================

@pytest.mark.asyncio
async def test_AQ_evidence_rejection():
    """AQ: Qualified clinician rejects discrete evidence item, updating epistemic state to REJECTED with audit."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        ev_id = f"ev-rej-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev = Evidence(
                id=ev_id,
                case_id=case_id,
                source_class="BEDSIDE_DEVICE",
                epistemic_state="KNOWN",
                parameter_name="HEART_RATE",
                content_value="240 bpm",
                confidence_score=0.9,
                captured_timestamp=utc_now(),
            )
            session.add(ev)
            await session.commit()

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        rej_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/reject",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "reason": "Electrode motion artifact causing spurious tachyarrhythmia reading.",
                "notes": "ECG rhythm strip shows normal sinus rhythm at 72 bpm.",
            },
        )
        assert rej_res.status_code == 200
        body = rej_res.json()
        assert body["epistemic_state"] == "REJECTED"
        assert body["verification_metadata"]["rejected_by"] == "usr-doc-01"
        assert "Electrode motion artifact" in body["verification_metadata"]["reason"]

        async with async_session_factory() as session:
            ra_stmt = select(ReviewAction).where(ReviewAction.target_entity_id == ev_id)
            ra = (await session.execute(ra_stmt)).scalars().first()
            assert ra is not None
            assert ra.action == "REJECT"
            assert "Electrode motion artifact" in ra.reason

            aud_stmt = select(AuditEvent).where(AuditEvent.object_id == ev_id)
            aud = (await session.execute(aud_stmt)).scalars().first()
            assert aud is not None
            assert aud.action == "evidence.rejected"


# ===========================================================================
# AR. EVIDENCE REJECTION REQUIRES RATIONALE
# ===========================================================================

@pytest.mark.asyncio
async def test_AR_evidence_rejection_requires_rationale():
    """AR: Evidence rejection without mandatory clinical rationale fails with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        ev_id = f"ev-no-rat-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev = Evidence(
                id=ev_id,
                case_id=case_id,
                source_class="NURSE_ENTRY",
                epistemic_state="KNOWN",
                parameter_name="TEMPERATURE",
                content_value="39.5 C",
                confidence_score=0.9,
                captured_timestamp=utc_now(),
            )
            session.add(ev)
            await session.commit()

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res_empty = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/reject",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"reason": "   "},
        )
        assert res_empty.status_code == 422

        res_missing = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/reject",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "No reason field provided"},
        )
        assert res_missing.status_code == 422


# ===========================================================================
# AS. EVIDENCE REJECTION UNAUTHORIZED ROLE
# ===========================================================================

@pytest.mark.asyncio
async def test_AS_evidence_rejection_unauthorized_role():
    """AS: Nurse and patient roles cannot reject clinical evidence (403)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")
        patient_token = await login_helper(client, "patient_09")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        ev_id = f"ev-unauth-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev = Evidence(
                id=ev_id,
                case_id=case_id,
                source_class="BEDSIDE_DEVICE",
                epistemic_state="KNOWN",
                parameter_name="SPO2",
                content_value="88%",
                confidence_score=0.9,
                captured_timestamp=utc_now(),
            )
            session.add(ev)
            await session.commit()

        res_nurse = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/reject",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"reason": "Nurse attempting to reject evidence"},
        )
        assert res_nurse.status_code == 403

        res_patient = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/reject",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"reason": "Patient attempting to reject evidence"},
        )
        assert res_patient.status_code == 403


# ===========================================================================
# AT. CONFLICT DETECTION EXCLUDES REJECTED EVIDENCE
# ===========================================================================

@pytest.mark.asyncio
async def test_AT_conflict_detection_excludes_rejected_evidence():
    """AT: Rejected evidence items are excluded from active contradiction detection."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        ev_id_1 = f"ev-c1-{uuid.uuid4().hex[:8]}"
        ev_id_2 = f"ev-c2-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev1 = Evidence(
                id=ev_id_1,
                case_id=case_id,
                source_class="BEDSIDE_DEVICE",
                epistemic_state="KNOWN",
                parameter_name="HEART_RATE",
                content_value="145",
                confidence_score=0.8,
                captured_timestamp=utc_now(),
            )
            ev2 = Evidence(
                id=ev_id_2,
                case_id=case_id,
                source_class="NURSE_ENTRY",
                epistemic_state="KNOWN",
                parameter_name="HEART_RATE",
                content_value="78",
                confidence_score=0.95,
                captured_timestamp=utc_now(),
            )
            session.add_all([ev1, ev2])
            await session.commit()

        ctx1 = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert ctx1.status_code == 200
        conflicts1 = ctx1.json()["conflicts"]
        assert any(c["parameter_name"].lower() == "heart_rate" for c in conflicts1)

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        rej_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id_1}/reject",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"reason": "Monitor artifact rejected in favor of manual palpation."},
        )
        assert rej_res.status_code == 200

        ctx2 = await client.get(
            f"/api/v1/cases/{case_id}/review-context",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert ctx2.status_code == 200
        conflicts2 = ctx2.json()["conflicts"]
        assert not any(c["parameter_name"].lower() == "heart_rate" for c in conflicts2)


# ===========================================================================
# AU. CONFLICT RESOLUTION CASE INSENSITIVE
# ===========================================================================

@pytest.mark.asyncio
async def test_AU_conflict_resolution_case_insensitive():
    """AU: Conflict resolution operates case-insensitively when identifying competing parameters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        ev_id_a = f"ev-case-a-{uuid.uuid4().hex[:8]}"
        ev_id_b = f"ev-case-b-{uuid.uuid4().hex[:8]}"
        async with async_session_factory() as session:
            ev_a = Evidence(
                id=ev_id_a,
                case_id=case_id,
                source_class="BEDSIDE_DEVICE",
                epistemic_state="KNOWN",
                parameter_name="blood_pressure",
                content_value="120/80",
                confidence_score=0.9,
                captured_timestamp=utc_now(),
            )
            ev_b = Evidence(
                id=ev_id_b,
                case_id=case_id,
                source_class="NURSE_ENTRY",
                epistemic_state="KNOWN",
                parameter_name="BLOOD_PRESSURE",
                content_value="170/105",
                confidence_score=0.95,
                captured_timestamp=utc_now(),
            )
            session.add_all([ev_a, ev_b])
            await session.commit()

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res_resolve = await client.post(
            f"/api/v1/cases/{case_id}/evidence/resolve-conflict",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "authoritative_evidence_id": ev_id_b,
                "parameter_name": "Blood_Pressure",
                "resolution_rationale": "Manual sphygmomanometer confirmed hypertension; automatic cuff leaked.",
            },
        )
        assert res_resolve.status_code == 200

        async with async_session_factory() as session:
            eva_fresh = await session.get(Evidence, ev_id_a)
            evb_fresh = await session.get(Evidence, ev_id_b)
            assert eva_fresh.epistemic_state == "SUPERSEDED"
            assert evb_fresh.epistemic_state == "VERIFIED"


# ===========================================================================
# AV. INVARIANT COMPLETE REVIEW REQUIRES DECISION
# ===========================================================================

@pytest.mark.asyncio
async def test_AV_invariant_complete_review_requires_decision():
    """AV: Invariant check rejects COMPLETE_REVIEW when no clinician decision has been recorded (422)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res_trans = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={
                "action": "COMPLETE_REVIEW",
                "reason": "Attempting to complete review without prior human decision",
            },
        )
        assert res_trans.status_code == 422
        body = res_trans.json()
        assert "decision" in str(body).lower() or body.get("error", {}).get("category") == "INVALID_STATE_TRANSITION"


# ===========================================================================
# ADVERSARIAL TESTS
# ===========================================================================

@pytest.mark.asyncio
async def test_adversarial_clinician_id_spoofing():
    """Adversarial: Client cannot spoof reviewer identity in start review or decisions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        # Nurse attempts to start review supplying spoofed header
        res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {nurse_token}", "X-Actor-Id": "usr-doc-01"},
            json={"notes": "Spoof attempt"},
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_adversarial_role_escalation_via_headers():
    """Adversarial: Header-based role tampering (X-Actor-Role: CLINICIAN) is ignored."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        patient_token = await login_helper(client, "patient_09")

        test_case = await create_test_case_helper(client, clinician_token, await login_helper(client, "nurse"))
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {patient_token}", "X-Actor-Role": "CLINICIAN"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "Spoofed patient decision"},
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_adversarial_stale_state_version_rejection():
    """Adversarial: Stale state versions are rejected with 409 preventing lost updates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"expected_state_version": 999},
        )
        assert res.status_code == 409


@pytest.mark.asyncio
async def test_adversarial_duplicate_finalize_disposition():
    """Adversarial: Calling disposition finalize repeatedly on a closed case fails."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        # First finalize closes case
        r1 = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"disposition_type": "DISCHARGE_HOME", "clinical_summary": "Discharged home", "close_case": True},
        )
        assert r1.status_code == 200

        # Duplicate finalize on closed case fails
        r2 = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"disposition_type": "DISCHARGE_HOME", "clinical_summary": "Duplicate discharge attempt", "close_case": True},
        )
        assert r2.status_code == 422


@pytest.mark.asyncio
async def test_adversarial_modifying_closed_case():
    """Adversarial: Post-closure evidence verification or modification attempts fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]
        ev_id = test_case["evidence_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/close",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"closure_reason": "Closed"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/evidence/{ev_id}/verify",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"rationale": "Attempt to verify on closed case"},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_adversarial_changing_state_directly():
    """Adversarial: Attempting direct state jump without valid action fails."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token, advance_to_review=False)
        case_id = test_case["case_id"]

        # Case is in INTAKE_RECORDED. Trying to jump to CLOSED without valid action fails.
        res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"action": "CLOSE_CASE", "reason": "Direct illegal jump attempt"},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_adversarial_cross_facility_review_tampering():
    """Adversarial: Tampering with cross-facility cases returns 404 (non-existent in facility scope)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")  # FAC-DH-04
        nurse_phc_token = await login_helper(client, "nurse_phc")  # FAC-PHC-01

        # Create case at PHC
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_phc_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "20-29",
                "biological_sex": "MALE",
                "preferred_language": "en",
                "chief_complaint": "Cross facility check",
                "symptom_duration": "1 day",
                "consent_confirmed": True,
            },
        )
        case_id = res.json()["case_id"]

        # Clinician at FAC-DH-04 tries to start review on PHC case
        tamper = await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"notes": "Tampering with cross-facility case"},
        )
        assert tamper.status_code == 404


@pytest.mark.asyncio
async def test_adversarial_client_supplied_disposition_authority():
    """Adversarial: Non-clinician attempting disposition is denied despite claims in body."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/disposition",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "disposition_type": "DISCHARGE_HOME",
                "clinical_summary": "Nurse claiming attending authority in body",
            },
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_adversarial_client_supplied_priority_override():
    """Adversarial: Review queue priority is derived exclusively by server and cannot be manipulated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")

        # Query review queue; queue items have explainable deterministic priority tiers
        res = await client.get(
            "/api/v1/cases/review-queue",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res.status_code == 200
        for item in res.json()["queue"]:
            assert item["priority_tier"] in {
                "P1_CRITICAL",
                "P1_IMMEDIATE_RESUSCITATION",
                "P2_VERY_URGENT",
                "P2_URGENT",
                "P3_URGENT",
                "P3_MODERATE",
                "P4_ROUTINE",
            }


@pytest.mark.asyncio
async def test_adversarial_client_supplied_verified_evidence():
    """Adversarial: Intake cannot submit pre-verified evidence bypassing review."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")

        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "30-39",
                "biological_sex": "FEMALE",
                "preferred_language": "en",
                "chief_complaint": "Intake verification bypass test",
                "symptom_duration": "1 day",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        case_id = res.json()["case_id"]

        # Directly checking evidence created at intake: none can have epistemic_state == VERIFIED
        async with async_session_factory() as session:
            stmt = select(Evidence).where(Evidence.case_id == case_id)
            evs = (await session.execute(stmt)).scalars().all()
            for ev in evs:
                assert ev.epistemic_state != "VERIFIED"


@pytest.mark.asyncio
async def test_adversarial_client_supplied_final_decision_without_auth():
    """Adversarial: Anonymous client cannot record clinical decisions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/cases/case-fake-123/decision",
            json={"decision_type": "ACCEPT", "clinical_rationale": "Unauthenticated decision"},
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_adversarial_bypassing_required_rationale():
    """Adversarial: Submitting white-space only or missing rationale on decisions fails with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        test_case = await create_test_case_helper(client, clinician_token, nurse_token)
        case_id = test_case["case_id"]

        await client.post(
            f"/api/v1/cases/{case_id}/review/start",
            headers={"Authorization": f"Bearer {clinician_token}"},
        )

        res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"decision_type": "ACCEPT", "clinical_rationale": "\t  \n"},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_adversarial_calling_clinician_endpoints_without_auth():
    """Adversarial: Unauthenticated requests to all clinician review endpoints return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_id = "case-unauth-test"

        assert (await client.get("/api/v1/cases/review-queue")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/review/start")).status_code == 401
        assert (await client.get(f"/api/v1/cases/{fake_id}/review-context")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/evidence/ev-1/verify")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/evidence/ev-1/modify")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/evidence/resolve-conflict")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/decision")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/disposition")).status_code == 401
        assert (await client.post(f"/api/v1/cases/{fake_id}/close")).status_code == 401
        assert (await client.get(f"/api/v1/cases/{fake_id}/review-history")).status_code == 401
