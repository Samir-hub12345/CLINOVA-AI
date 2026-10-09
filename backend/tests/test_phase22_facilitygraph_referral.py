"""CLINOVA AI — Phase 22 FacilityGraph, Care Orchestration & Referral Test Suite.

Validates:
- Facility capability matching & care feasibility predicate Phi(F, B)
- Dynamic destination ranking & road transit calculations
- Decision hierarchy: ESCALATE, REFER, VERIFY, OBSERVE, ASK, CONTINUE
- Clinician gate & mandatory override justification validation
- Automated SBAR inter-facility clinical transfer packet generation
- Referral creation, dispatch lifecycle, and case state continuity
- Medicolegal audit logging for all facility and referral mutations
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import Case, Facility, FacilityCapability, Referral, ClinicianDecision, AuditLog
from app.core.config import settings
from app.domain.facilitygraph.engine import (
    evaluate_feasibility,
    rank_referral_destinations,
    generate_sbar_packet,
    haversine_transit_estimate,
    CARE_BUNDLES,
)
from app.domain.orchestration.engine import OrchestrationEngine


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
async def sample_case_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Create patient
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "50-59", "biological_sex": "FEMALE"},
            headers=headers,
        )
        assert p_res.status_code == 200
        pt_id = p_res.json()["id"]

        # Create case with acute stroke bundle
        case_res = await client.post(
            "/api/v1/cases",
            json={
                "patient_id": pt_id,
                "facility_id": "FAC-DH-04",
                "presenting_complaint": "Acute onset right-sided weakness and aphasia",
                "primary_syndrome": "ACUTE_STROKE",
            },
            headers=headers,
        )
        assert case_res.status_code == 200
        case_data = case_res.json()

        # Update case to have required bundle
        async with async_session_factory() as session:
            case = await session.get(Case, case_data["id"])
            case.required_bundle = "BUNDLE_STROKE_ACUTE"
            await session.commit()

        return case_data["id"]


# ===========================================================================
# 1. FACILITYGRAPH FEASIBILITY & CAPABILITY MATCHING
# ===========================================================================

def test_facilitygraph_feasibility_evaluation():
    """Validates predicate Phi(F, B) across FEASIBLE, INFEASIBLE, and DEGRADED states."""
    # 1. Fully capable and resourced tertiary center
    tertiary_fac = {
        "id": "FAC-TERT-01",
        "name": "Tertiary Medical Center",
        "tier": "LEVEL_5_TERTIARY",
        "icu_beds_available": 4,
        "general_beds_available": 20,
        "capabilities": [
            {"capability_code": "CT_SCAN_24_7", "is_operational": True},
            {"capability_code": "ICU_BEDS", "is_operational": True},
            {"capability_code": "THROMBOLYTICS", "is_operational": True},
        ],
    }
    feas_tertiary = evaluate_feasibility(tertiary_fac, "BUNDLE_STROKE_ACUTE")
    assert feas_tertiary["status"] == "FEASIBLE"
    assert feas_tertiary["available_beds"] == 4
    assert len(feas_tertiary["missing_capabilities"]) == 0

    # 2. Local PHC lacking CT scanner and ICU
    phc_fac = {
        "id": "FAC-PHC-01",
        "name": "Gram Panchayat PHC",
        "tier": "LEVEL_1_PHC",
        "icu_beds_available": 0,
        "general_beds_available": 4,
        "capabilities": [
            {"capability_code": "OUTPATIENT_TRIAGE", "is_operational": True},
        ],
    }
    feas_phc = evaluate_feasibility(phc_fac, "BUNDLE_STROKE_ACUTE")
    assert feas_phc["status"] == "INFEASIBLE"
    assert "CT_SCAN_24_7" in feas_phc["missing_capabilities"]
    assert "ICU_BEDS" in feas_phc["missing_capabilities"]

    # 3. Capable facility with ICU saturation (0 ICU beds available)
    saturated_fac = {
        "id": "FAC-DH-02",
        "name": "District Hospital Saturated",
        "tier": "LEVEL_4_DH",
        "icu_beds_available": 0,
        "general_beds_available": 10,
        "capabilities": [
            ("CT_SCAN_24_7", True),
            ("ICU_BEDS", True),
            ("THROMBOLYTICS", True),
        ],
    }
    feas_sat = evaluate_feasibility(saturated_fac, "BUNDLE_STROKE_ACUTE")
    assert feas_sat["status"] == "DEGRADED"
    assert feas_sat["available_beds"] == 0


def test_facilitygraph_destination_ranking():
    """Validates deterministic ranking of regional network destination centers."""
    current_fac = {"id": "FAC-PHC-01", "name": "Local PHC", "latitude": 20.3, "longitude": 85.8}
    network = [
        {
            "id": "FAC-DH-NEAR",
            "name": "District Hospital Near",
            "tier": "LEVEL_4_DH",
            "latitude": 20.4,
            "longitude": 85.85,
            "icu_beds_available": 2,
            "ed_avg_wait_min": 15,
            "capabilities": [("CT_SCAN_24_7", True), ("ICU_BEDS", True), ("THROMBOLYTICS", True)],
        },
        {
            "id": "FAC-TERT-FAR",
            "name": "Tertiary Center Far",
            "tier": "LEVEL_5_TERTIARY",
            "latitude": 21.0,
            "longitude": 86.5,
            "icu_beds_available": 10,
            "ed_avg_wait_min": 30,
            "capabilities": [("CT_SCAN_24_7", True), ("ICU_BEDS", True), ("THROMBOLYTICS", True)],
        },
        {
            "id": "FAC-CHC-INCAPABLE",
            "name": "CHC Without CT",
            "tier": "LEVEL_2_CHC",
            "latitude": 20.35,
            "longitude": 85.82,
            "icu_beds_available": 0,
            "ed_avg_wait_min": 5,
            "capabilities": [("OUTPATIENT_TRIAGE", True)],
        },
    ]

    ranked = rank_referral_destinations(current_fac, network, "BUNDLE_STROKE_ACUTE")
    assert len(ranked) == 3
    # Nearest capable facility outranks far tertiary and incapable facility
    assert ranked[0]["facility_id"] == "FAC-DH-NEAR"
    assert ranked[0]["feasibility_status"] == "FEASIBLE"
    # Incapable facility is ranked last
    assert ranked[-1]["facility_id"] == "FAC-CHC-INCAPABLE"
    assert ranked[-1]["feasibility_status"] == "INFEASIBLE"


# ===========================================================================
# 2. FACILITY APIS, TOGGLE CAPABILITY & CAPACITY MUTATION
# ===========================================================================

@pytest.mark.asyncio
async def test_facility_list_and_match_endpoints():
    """Tests GET /facilities and POST /facilities/match."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. List facilities
        list_res = await client.get("/api/v1/facilities")
        assert list_res.status_code == 200
        facs = list_res.json()
        assert len(facs) > 0

        target_fac = facs[0]

        # 2. Check local feasibility
        match_res = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": target_fac["id"], "required_bundle": "BUNDLE_ROUTINE_AMBULATORY"},
        )
        assert match_res.status_code == 200
        data = match_res.json()
        assert "feasibility" in data
        assert data["facility_id"] == target_fac["id"]


@pytest.mark.asyncio
async def test_facility_capability_toggle_and_capacity_update():
    """Tests capability toggling and capacity updates with audit logging."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "facility_admin")
        headers = {"Authorization": f"Bearer {token}"}

        fac_id = "FAC-DH-04"

        # 1. Toggle capability (e.g. set CT Scanner offline)
        toggle_res = await client.post(
            f"/api/v1/facilities/{fac_id}/toggle-capability",
            json={
                "capability_code": "CT_SCAN_24_7",
                "is_operational": False,
                "maintenance_note": "Scheduled tube replacement",
            },
            headers=headers,
        )
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_operational"] is False

        # 2. Update capacity
        cap_res = await client.post(
            f"/api/v1/facilities/{fac_id}/update-capacity",
            json={"icu_beds_available": 1, "general_beds_available": 8, "ed_waiting_cases": 5},
            headers=headers,
        )
        assert cap_res.status_code == 200
        assert cap_res.json()["icu_beds_available"] == 1

        # 3. Verify audit logs recorded
        async with async_session_factory() as session:
            stmt = select(AuditLog).where(
                AuditLog.entity_id == fac_id,
                AuditLog.action.in_(["CAPABILITY_TOGGLED", "CAPACITY_UPDATED"]),
            )
            audits = (await session.execute(stmt)).scalars().all()
            assert len(audits) >= 2


# ===========================================================================
# 3. CARE ORCHESTRATION ENGINE HIERARCHY
# ===========================================================================

def test_orchestration_decision_hierarchy():
    """Validates the 6 clinical actions: ESCALATE, REFER, VERIFY, OBSERVE, ASK, CONTINUE."""
    # 1. ESCALATE: Severe physiological instability
    res_esc = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.85, "acuity_tier": "CRITICAL", "trajectory_slope": 1.8},
        uncertainty_analysis={"uncertainty_score": 0.1, "conflicts": [], "missing_parameters": []},
        feasibility_result={"status": "FEASIBLE"},
    )
    assert res_esc["recommended_action"] == "ESCALATE"
    assert res_esc["priority_level"] == "IMMEDIATE_RED"

    # 2. REFER: Local care infeasible for acute syndrome
    res_ref = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.25, "acuity_tier": "MODERATE", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        uncertainty_analysis={"uncertainty_score": 0.1, "conflicts": [], "missing_parameters": []},
        feasibility_result={"status": "INFEASIBLE", "reason": "Lacks CT scanner"},
    )
    assert res_ref["recommended_action"] == "REFER"
    assert res_ref["priority_level"] == "HIGH_ORANGE"

    # 3. VERIFY: Contradictory evidence
    res_ver = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.2, "acuity_tier": "ROUTINE"},
        uncertainty_analysis={"uncertainty_score": 0.2, "conflicts": [{"message": "History vs Vitals conflict"}]},
        feasibility_result={"status": "FEASIBLE"},
    )
    assert res_ver["recommended_action"] == "VERIFY"
    assert res_ver["priority_level"] == "ELEVATED_YELLOW"

    # 4. OBSERVE: Moderate risk or evolving trajectory
    res_obs = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.45, "acuity_tier": "URGENT", "trajectory_slope": 0.6},
        uncertainty_analysis={"uncertainty_score": 0.2, "conflicts": [], "missing_parameters": []},
        feasibility_result={"status": "FEASIBLE"},
    )
    assert res_obs["recommended_action"] == "OBSERVE"
    assert res_obs["priority_level"] == "MONITORING_BLUE"

    # 5. ASK: High data uncertainty with missing protocol parameters
    res_ask = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.15, "acuity_tier": "ROUTINE"},
        uncertainty_analysis={"uncertainty_score": 0.65, "conflicts": [], "missing_parameters": ["fever_onset", "pain_duration"]},
        feasibility_result={"status": "FEASIBLE"},
    )
    assert res_ask["recommended_action"] == "ASK"
    assert res_ask["priority_level"] == "MODERATE_YELLOW"

    # 6. CONTINUE: Stable low risk
    res_cont = OrchestrationEngine.evaluate(
        case_state={"risk_score": 0.1, "acuity_tier": "ROUTINE", "trajectory_slope": 0.0},
        uncertainty_analysis={"uncertainty_score": 0.1, "conflicts": [], "missing_parameters": []},
        feasibility_result={"status": "FEASIBLE"},
    )
    assert res_cont["recommended_action"] == "CONTINUE"
    assert res_cont["priority_level"] == "ROUTINE_GREEN"


# ===========================================================================
# 4. CLINICIAN GATE & MANDATORY OVERRIDE VALIDATION
# ===========================================================================

@pytest.mark.asyncio
async def test_clinician_decision_and_override_gate(sample_case_id: str):
    """Validates clinician authorization gate and enforces mandatory override justification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Clinician accepts recommendation
        accept_res = await client.post(
            "/api/v1/orchestration/decision",
            json={
                "case_id": sample_case_id,
                "action": "REFER",
                "decision_type": "ACCEPT",
                "clinician_id": "usr-doc-01",
                "notes": "Agree with transfer to stroke center.",
            },
            headers=headers,
        )
        assert accept_res.status_code == 200
        assert accept_res.json()["status"] == "AUTHORIZED"
        assert accept_res.json()["case_status"] == "REFER"

        # 2. Clinician attempts OVERRIDE without mandatory reason -> HTTP 422
        bad_override = await client.post(
            "/api/v1/orchestration/decision",
            json={
                "case_id": sample_case_id,
                "action": "CONTINUE",
                "decision_type": "OVERRIDE",
                "clinician_id": "usr-doc-01",
                "override_reason": "",  # Empty -> must be rejected
            },
            headers=headers,
        )
        assert bad_override.status_code == 422

        # 3. Clinician provides valid OVERRIDE with justification
        good_override = await client.post(
            "/api/v1/orchestration/decision",
            json={
                "case_id": sample_case_id,
                "action": "OBSERVE",
                "decision_type": "OVERRIDE",
                "clinician_id": "usr-doc-01",
                "override_reason": "Patient symptoms resolving rapidly; suspected TIA under observation.",
            },
            headers=headers,
        )
        assert good_override.status_code == 200
        assert good_override.json()["status"] == "AUTHORIZED"
        assert good_override.json()["case_status"] == "OBSERVE"

        # 4. Verify decision persistence and audit trail
        async with async_session_factory() as session:
            decisions = (
                await session.execute(select(ClinicianDecision).where(ClinicianDecision.case_id == sample_case_id))
            ).scalars().all()
            assert len(decisions) == 2

            audits = (
                await session.execute(select(AuditLog).where(AuditLog.entity_id == sample_case_id))
            ).scalars().all()
            assert any(a.action == "CLINICIAN_DECISION_RECORDED" for a in audits)


# ===========================================================================
# 5. REFERRAL SBAR PREPARATION & LIFECYCLE
# ===========================================================================

@pytest.mark.asyncio
async def test_referral_sbar_and_lifecycle(sample_case_id: str):
    """Validates SBAR clinical transfer packet generation, referral creation, and lifecycle states."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Get target facility
        facs_res = await client.get("/api/v1/facilities", headers=headers)
        all_facs = facs_res.json()
        dest_fac = all_facs[1] if len(all_facs) > 1 else all_facs[0]

        # 1. Generate SBAR transfer packet
        sbar_res = await client.post(
            "/api/v1/referrals/sbar",
            json={
                "case_id": sample_case_id,
                "destination_facility_id": dest_fac["id"],
            },
            headers=headers,
        )
        assert sbar_res.status_code == 200
        sbar = sbar_res.json()
        assert "sbar_situation" in sbar
        assert "sbar_background" in sbar
        assert "sbar_assessment" in sbar
        assert "sbar_recommendation" in sbar
        assert "estimated_transit_minutes" in sbar

        # 2. Create inter-facility referral
        ref_res = await client.post(
            "/api/v1/referrals/create",
            json={
                "case_id": sample_case_id,
                "origin_facility_id": "FAC-DH-04",
                "destination_facility_id": dest_fac["id"],
                "required_bundle": "BUNDLE_STROKE_ACUTE",
                "sbar_situation": sbar["sbar_situation"],
                "sbar_background": sbar["sbar_background"],
                "sbar_assessment": sbar["sbar_assessment"],
                "sbar_recommendation": sbar["sbar_recommendation"],
            },
            headers=headers,
        )
        assert ref_res.status_code == 200
        ref_data = ref_res.json()
        referral_id = ref_data["referral_id"]
        assert ref_data["case_status"] == "TRANSFER_PENDING"
        assert ref_data["referral_status"] == "REQUESTED"

        # 3. Transition to DISPATCHED -> Case becomes TRANSFER
        status_disp = await client.post(
            f"/api/v1/referrals/{referral_id}/status",
            json={"status": "DISPATCHED"},
            headers=headers,
        )
        assert status_disp.status_code == 200
        assert status_disp.json()["case_status"] == "TRANSFER"

        # 4. Transition to COMPLETED -> Case becomes COMPLETED
        status_comp = await client.post(
            f"/api/v1/referrals/{referral_id}/status",
            json={"status": "COMPLETED"},
            headers=headers,
        )
        assert status_comp.status_code == 200
        assert status_comp.json()["case_status"] == "COMPLETED"

        # 5. Verify database audit record
        async with async_session_factory() as session:
            ref_record = await session.get(Referral, referral_id)
            assert ref_record.status == "COMPLETED"
            assert ref_record.required_bundle == "BUNDLE_STROKE_ACUTE"

            audits = (
                await session.execute(select(AuditLog).where(AuditLog.entity_id == referral_id))
            ).scalars().all()
            assert len(audits) >= 2
            assert any(a.action == "REFERRAL_DISPATCHED" for a in audits)
            assert any(a.action == "REFERRAL_STATUS_UPDATED" for a in audits)
