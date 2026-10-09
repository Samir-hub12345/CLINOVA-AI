"""CLINOVA AI — Phase 23 Outcome Loop & SignalGraph Test Suite.

Validates:
1. Four-way explicit separation:
   - AI recommendation
   - Professional decision
   - Actual operational action
   - Recorded clinical outcome
2. Explicit UNKNOWN outcome semantics (no false optimism)
3. Historical outcome correction workflow (is_corrected=True, version bump, audit trail)
4. Duplicate submission idempotency (no duplicate rows or double-counted telemetry)
5. Strict RBAC authorization (clinician only for final disposition, patient/nurse blocked)
6. CareGraph outcome node feedback (OUTCOME node, CONCLUDES_WITH edge)
7. SignalGraph de-identified outcome telemetry aggregation & deduplication
8. Zero PHI privacy guarantees in SignalGraph
9. Failure recovery & boundary validation (non-existent case returns 404)
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import Case, CaseOutcome, AuditLog
from app.core.config import settings
from app.domain.signalgraph.engine import signal_engine


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture(autouse=True)
async def setup_environment():
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = True
    await init_db()


@pytest.fixture
async def sample_case():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create patient
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "45-54", "biological_sex": "MALE"},
            headers=headers,
        )
        assert p_res.status_code == 200, p_res.text
        pt_id = p_res.json()["id"]

        # 2. Create case
        case_res = await client.post(
            "/api/v1/cases",
            json={
                "patient_id": pt_id,
                "facility_id": "FAC-DH-04",
                "presenting_complaint": "Acute severe epigastric pain radiating to back",
                "primary_syndrome": "ACUTE_ABDOMEN",
            },
            headers=headers,
        )
        assert case_res.status_code == 200, case_res.text
        return case_res.json()


# ===========================================================================
# 1. OUTCOME CREATION & RETRIEVAL (FOUR-WAY SEPARATION)
# ===========================================================================

@pytest.mark.asyncio
async def test_outcome_creation_and_retrieval(sample_case):
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # POST /api/v1/cases/{case_id}/outcome
        outcome_payload = {
            "disposition": "DISCHARGE_HOME",
            "final_condition": "RECOVERED",
            "recommendation": "CONTINUE_MEDICATION",
            "professional_decision": "DISCHARGE_WITH_ORAL_ANTIBIOTICS",
            "actual_action": "DISCHARGED",
            "outcome_status": "RECOVERED",
            "notes": "Patient symptoms fully resolved. Vitals stable upon discharge.",
        }

        res = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json=outcome_payload,
            headers=headers,
        )
        assert res.status_code == 200, res.text
        data = res.json()

        assert data["case_id"] == case_id
        assert data["status"] == "OUTCOME"
        assert data["disposition"] == "DISCHARGE_HOME"
        assert data["final_condition"] == "RECOVERED"
        assert data["recommendation"] == "CONTINUE_MEDICATION"
        assert data["professional_decision"] == "DISCHARGE_WITH_ORAL_ANTIBIOTICS"
        assert data["actual_action"] == "DISCHARGED"
        assert data["outcome_status"] == "RECOVERED"
        assert data["version"] == 1
        assert data["is_corrected"] is False
        assert data["recorded_by"] is not None

        # GET /api/v1/cases/{case_id}/outcome
        get_res = await client.get(
            f"/api/v1/cases/{case_id}/outcome",
            headers=headers,
        )
        assert get_res.status_code == 200, get_res.text
        get_data = get_res.json()

        assert get_data["case_id"] == case_id
        assert get_data["recommendation"] == "CONTINUE_MEDICATION"
        assert get_data["professional_decision"] == "DISCHARGE_WITH_ORAL_ANTIBIOTICS"
        assert get_data["actual_action"] == "DISCHARGED"
        assert get_data["outcome_status"] == "RECOVERED"
        assert get_data["notes"] == "Patient symptoms fully resolved. Vitals stable upon discharge."


# ===========================================================================
# 2. STRICT SEPARATION: RECOMMENDATION != DECISION != ACTION != OUTCOME
# ===========================================================================

@pytest.mark.asyncio
async def test_separation_of_recommendation_decision_action_outcome(sample_case):
    """
    Validates that:
    - AI recommended one thing (e.g., REFER_TERTIARY)
    - Clinician decided another (e.g., ADMIT_LOCAL_OBSERVATION)
    - Operational reality was different (e.g., TRANSFERRED to private center at family request)
    - Final outcome was distinct (e.g., DETERIORATED)
    None of these are substituted or collapsed into one another.
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "disposition": "TRANSFER_EXTERNAL",
            "final_condition": "DETERIORATED",
            "recommendation": "REFER_TERTIARY_GOVT",
            "professional_decision": "ADMIT_LOCAL_OBSERVATION",
            "actual_action": "TRANSFERRED_PRIVATE_FACILITY",
            "outcome_status": "DETERIORATED",
            "notes": "Family insisted on transfer to private tertiary center.",
        }

        res = await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()

        assert data["recommendation"] != data["professional_decision"]
        assert data["professional_decision"] != data["actual_action"]
        assert data["actual_action"] != data["outcome_status"]

        assert data["recommendation"] == "REFER_TERTIARY_GOVT"
        assert data["professional_decision"] == "ADMIT_LOCAL_OBSERVATION"
        assert data["actual_action"] == "TRANSFERRED_PRIVATE_FACILITY"
        assert data["outcome_status"] == "DETERIORATED"


# ===========================================================================
# 3. EXPLICIT UNKNOWN OUTCOME SEMANTICS
# ===========================================================================

@pytest.mark.asyncio
async def test_unknown_outcome_handling(sample_case):
    """
    Validates that when an action occurs but the outcome remains unconfirmed,
    it is explicitly persisted as UNKNOWN and never counted as positive recovery.
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "disposition": "TRANSFERRED",
            "actual_action": "TRANSFERRED",
            "outcome_status": "UNKNOWN",
            "notes": "Patient in transit; final outcome at receiving facility not yet confirmed.",
        }

        res = await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["actual_action"] == "TRANSFERRED"
        assert data["outcome_status"] == "UNKNOWN"

        # Check SignalGraph metrics reflect explicit unknown count
        telemetry_res = await client.get("/api/v1/signalgraph/outcomes", headers=headers)
        assert telemetry_res.status_code == 200
        telemetry = telemetry_res.json()

        assert telemetry["unknown_outcomes_count"] >= 1
        assert "UNKNOWN" in telemetry["outcome_status_distribution"]


# ===========================================================================
# 4. HISTORICAL OUTCOME CORRECTION WORKFLOW
# ===========================================================================

@pytest.mark.asyncio
async def test_outcome_correction_workflow(sample_case):
    """
    Validates that updating a recorded outcome with is_corrected=True:
    1. Bumps the version number
    2. Sets is_corrected = True
    3. Emits a CASE_OUTCOME_CORRECTED audit log
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Initial record
        initial_payload = {
            "disposition": "DISCHARGE_HOME",
            "outcome_status": "STABLE",
            "actual_action": "DISCHARGED",
            "is_corrected": False,
        }
        r1 = await client.post(f"/api/v1/cases/{case_id}/outcome", json=initial_payload, headers=headers)
        assert r1.status_code == 200
        assert r1.json()["version"] == 1
        assert r1.json()["is_corrected"] is False

        # Step 2: Clinician corrects record (e.g. readmission within 12h)
        corrected_payload = {
            "disposition": "READMITTED",
            "outcome_status": "DETERIORATED",
            "actual_action": "READMITTED_ICU",
            "is_corrected": True,
            "notes": "Patient presented to ED 8 hours post-discharge with acute relapse.",
        }
        r2 = await client.post(f"/api/v1/cases/{case_id}/outcome", json=corrected_payload, headers=headers)
        assert r2.status_code == 200
        d2 = r2.json()

        assert d2["version"] == 2
        assert d2["is_corrected"] is True
        assert d2["outcome_status"] == "DETERIORATED"
        assert d2["actual_action"] == "READMITTED_ICU"

        # Verify audit trail
        async with async_session_factory() as session:
            stmt = select(AuditLog).where(
                AuditLog.action == "CASE_OUTCOME_CORRECTED"
            ).order_by(AuditLog.timestamp.desc())
            audits = (await session.execute(stmt)).scalars().all()
            assert len(audits) >= 1
            latest_audit = audits[0]
            assert latest_audit.details.get("case_id") == case_id
            assert latest_audit.details.get("is_corrected") is True
            assert latest_audit.details.get("version") == 2


# ===========================================================================
# 5. DUPLICATE SUBMISSION IDEMPOTENCY
# ===========================================================================

@pytest.mark.asyncio
async def test_duplicate_submission_idempotency(sample_case):
    """
    Submitting the exact same outcome payload twice (e.g. network retry):
    - Should succeed idempotently
    - Should not create a second row in case_outcomes
    - Should not increase telemetry event count
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "disposition": "DISCHARGE_HOME",
            "outcome_status": "RECOVERED",
            "actual_action": "DISCHARGED",
        }

        # First submission
        r1 = await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)
        assert r1.status_code == 200
        outcome_id_1 = r1.json()["outcome_id"]

        # Duplicate retry submission
        r2 = await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)
        assert r2.status_code == 200
        outcome_id_2 = r2.json()["outcome_id"]

        assert outcome_id_1 == outcome_id_2

        # Check DB has exactly 1 record for this case
        async with async_session_factory() as session:
            stmt = select(CaseOutcome).where(CaseOutcome.case_id == case_id)
            rows = (await session.execute(stmt)).scalars().all()
            assert len(rows) == 1


# ===========================================================================
# 6. ROLE-BASED ACCESS CONTROL (RBAC) ENFORCEMENT
# ===========================================================================

@pytest.mark.asyncio
async def test_authorization_enforcement(sample_case):
    """
    Asserts that:
    - Nurse CANNOT finalize disposition/outcome (Permission.DISPOSITION_FINALIZE is clinician only)
    - Patient CANNOT finalize disposition/outcome (403)
    - Invalid bearer token returns 401 Unauthorized
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "disposition": "DISCHARGE_HOME",
            "outcome_status": "RECOVERED",
        }

        # 1. Invalid Bearer Token -> 401
        res_unauth = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json=payload,
            headers={"Authorization": "Bearer invalid-bearer-token-12345"},
        )
        assert res_unauth.status_code == 401

        # 2. Nurse token -> 403 Forbidden
        nurse_token = await login_helper(client, "nurse")
        nurse_headers = {"Authorization": f"Bearer {nurse_token}"}
        res_nurse = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json=payload,
            headers=nurse_headers,
        )
        assert res_nurse.status_code == 403

        # 3. Patient token -> 403 Forbidden
        patient_token = await login_helper(client, "patient")
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        res_patient = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json=payload,
            headers=patient_headers,
        )
        assert res_patient.status_code == 403


# ===========================================================================
# 7. CAREGRAPH OUTCOME NODE FEEDBACK
# ===========================================================================

@pytest.mark.asyncio
async def test_caregraph_outcome_node_feedback(sample_case):
    """
    Validates that once an outcome is recorded:
    1. CareGraph topology includes a node of type "OUTCOME"
    2. Edge connects encounter node -> outcome node with relation "CONCLUDES_WITH"
    3. Outcome dictionary is returned in the response
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Record outcome
        payload = {
            "disposition": "DISCHARGE_HOME",
            "outcome_status": "RECOVERED",
            "actual_action": "DISCHARGED",
            "recommendation": "OBSERVE_AND_DISCHARGE",
            "professional_decision": "DISCHARGE",
        }
        r_out = await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)
        assert r_out.status_code == 200

        # Fetch CareGraph
        r_cg = await client.get(f"/api/v1/caregraph/{case_id}", headers=headers)
        assert r_cg.status_code == 200, r_cg.text
        cg_data = r_cg.json()

        assert "outcome" in cg_data
        assert cg_data["outcome"] is not None
        assert cg_data["outcome"]["outcome_status"] == "RECOVERED"
        assert cg_data["outcome"]["actual_action"] == "DISCHARGED"

        nodes = cg_data["graph"]["nodes"]
        edges = cg_data["graph"]["edges"]

        outcome_nodes = [n for n in nodes if n["type"] == "OUTCOME"]
        assert len(outcome_nodes) == 1
        out_node = outcome_nodes[0]
        assert out_node["data"]["outcome_status"] == "RECOVERED"
        assert out_node["data"]["actual_action"] == "DISCHARGED"

        # Verify edge CONCLUDES_WITH
        concludes_edges = [e for e in edges if e["relation"] == "CONCLUDES_WITH"]
        assert len(concludes_edges) == 1
        assert concludes_edges[0]["target"] == out_node["id"]


# ===========================================================================
# 8. SIGNALGRAPH TELEMETRY & PRIVACY AGGREGATION
# ===========================================================================

@pytest.mark.asyncio
async def test_signalgraph_deduplication_and_privacy_aggregation(sample_case):
    """
    Validates:
    1. SignalGraph ingests outcomes without double-counting
    2. Zero PHI: response contains only aggregates, no patient names, identifiers, or free text
    """
    case_id = sample_case["id"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Get initial count
        t0 = (await client.get("/api/v1/signalgraph/outcomes", headers=headers)).json()
        initial_count = t0["total_outcomes_recorded"]

        # Record outcome
        payload = {
            "disposition": "TRANSFERRED_TERTIARY",
            "outcome_status": "STABLE",
            "actual_action": "TRANSFERRED",
        }
        await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)

        # Telemetry should increase by 1
        t1 = (await client.get("/api/v1/signalgraph/outcomes", headers=headers)).json()
        assert t1["total_outcomes_recorded"] == initial_count + 1

        # Post again (idempotent retry)
        await client.post(f"/api/v1/cases/{case_id}/outcome", json=payload, headers=headers)

        # Telemetry should NOT increase again
        t2 = (await client.get("/api/v1/signalgraph/outcomes", headers=headers)).json()
        assert t2["total_outcomes_recorded"] == initial_count + 1

        # Privacy Assertion: Zero PHI in payload
        assert "patient_id" not in t2
        assert "patient_name" not in t2
        assert "case_id" not in t2
        assert "notes" not in t2
        assert t2["mode"] == "SYNTHETIC_TELEMETRY_MODE"


# ===========================================================================
# 9. FAILURE RECOVERY: INVALID CASE ID
# ===========================================================================

@pytest.mark.asyncio
async def test_failure_recovery_invalid_case():
    fake_case_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.post(
            f"/api/v1/cases/{fake_case_id}/outcome",
            json={"disposition": "DISCHARGE_HOME"},
            headers=headers,
        )
        assert res.status_code == 404
        assert "not found" in res.json().get("detail", res.text).lower()

        # GET non-existent
        get_res = await client.get(
            f"/api/v1/cases/{fake_case_id}/outcome",
            headers=headers,
        )
        assert get_res.status_code == 404
