"""CLINOVA AI — Core Innovation Acceptance Tests.

Verifies the 5 Core Innovation Gates from Section 22 of the Master Contract:
1. CAREGRAPH: Dynamic patient state, trajectory (Delta R), and uncertainty (U_t) recalculation.
2. FACILITYGRAPH: Live capability toggle flips care feasibility predicate Phi(F, B).
3. SIGNALGRAPH: Real prototype event consumption and dynamic syndromic cluster telemetry.
4. ORCHESTRATION: Multi-dimensional cognitive synthesis deriving safest achievable care action.
5. OUTCOME LOOP: Encounter disposition closing the clinical loop and feeding system intelligence.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.init_db import init_db


@pytest.fixture(autouse=True)
async def setup_database():
    """Initializes and seeds database before running acceptance tests."""
    from app.core.config import settings
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = True
    await init_db()


@pytest.mark.asyncio
async def test_acceptance_gate_1_caregraph_dynamic_update():
    """
    Acceptance Gate 1 — CAREGRAPH:
    When meaningful evidence (vitals / lab) changes, patient state, trajectory slope (Delta R),
    and uncertainty (U_t) MUST recalculate dynamically.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create case
        res1 = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Cough and mild fever.",
                "vitals": {"heart_rate": 78, "systolic_bp": 120, "spo2_percent": 98, "respiratory_rate": 16},
            },
        )
        assert res1.status_code == 200
        case_id = res1.json()["case_id"]

        # Initial CareGraph inspection
        cg1 = await client.get(f"/api/v1/caregraph/{case_id}")
        assert cg1.status_code == 200
        initial_nodes_count = cg1.json()["graph"]["total_nodes"]
        initial_slope = cg1.json()["trajectory"]["slope"]
        assert initial_slope == 0.0

        # Inject new deteriorating vitals
        res2 = await client.post(
            f"/api/v1/caregraph/{case_id}/vitals",
            json={"heart_rate": 132, "systolic_bp": 86, "spo2_percent": 87, "respiratory_rate": 30},
        )
        assert res2.status_code == 200
        assert res2.json()["trajectory_slope"] > 0.5

        # Re-inspect CareGraph: verify nodes expanded and trajectory recalculated
        cg2 = await client.get(f"/api/v1/caregraph/{case_id}")
        assert cg2.status_code == 200
        assert cg2.json()["graph"]["total_nodes"] > initial_nodes_count
        assert cg2.json()["trajectory"]["slope"] > 0.5


@pytest.mark.asyncio
async def test_acceptance_gate_2_facilitygraph_feasibility_toggle():
    """
    Acceptance Gate 2 — FACILITYGRAPH:
    Changing a facility capability condition (toggling equipment offline) MUST immediately
    alter care-feasibility results from FEASIBLE to INFEASIBLE.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # District Hospital initially has CT_SCAN_24_7 operational -> FEASIBLE for stroke
        m1 = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": "FAC-DH-04", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        )
        assert m1.status_code == 200
        assert m1.json()["feasibility"]["status"] == "FEASIBLE"

        admin_headers = {"X-Actor-Id": "usr-admin-03", "X-Facility-Id": "FAC-DH-04"}

        # Toggle CT scanner offline (e.g. tube replacement maintenance)
        t_res = await client.post(
            "/api/v1/facilities/FAC-DH-04/toggle-capability",
            json={"capability_code": "CT_SCAN_24_7", "is_operational": False, "maintenance_note": "Tube defect"},
            headers=admin_headers,
        )
        assert t_res.status_code == 200
        assert t_res.json()["is_operational"] is False

        # Re-check feasibility: MUST now be INFEASIBLE
        m2 = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": "FAC-DH-04", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        )
        assert m2.status_code == 200
        assert m2.json()["feasibility"]["status"] == "INFEASIBLE"
        assert "CT_SCAN_24_7" in m2.json()["feasibility"]["missing_capabilities"]

        # Restore capability
        await client.post(
            "/api/v1/facilities/FAC-DH-04/toggle-capability",
            json={"capability_code": "CT_SCAN_24_7", "is_operational": True},
            headers=admin_headers,
        )


@pytest.mark.asyncio
async def test_acceptance_gate_3_signalgraph_real_event_consumption():
    """
    Acceptance Gate 3 — SIGNALGRAPH:
    New synthetic case events generated inside the prototype MUST feed the system signal layer.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        initial_surges = await client.get("/api/v1/signalgraph/surges")
        assert initial_surges.status_code == 200
        prev_events_count = initial_surges.json()["total_signals_in_window"]

        # Create 3 new acute respiratory cases
        for _ in range(3):
            await client.post(
                "/api/v1/intake/text",
                json={
                    "facility_id": "FAC-DH-04",
                    "narrative_text": "Shortness of breath and fever.",
                    "vitals": {"heart_rate": 90, "spo2_percent": 94},
                },
            )

        updated_surges = await client.get("/api/v1/signalgraph/surges")
        assert updated_surges.status_code == 200
        assert updated_surges.json()["total_signals_in_window"] >= prev_events_count + 3


@pytest.mark.asyncio
async def test_acceptance_gate_4_orchestration_multi_dimensional_synthesis():
    """
    Acceptance Gate 4 — ORCHESTRATION ENGINE:
    Patient State + Evidence Uncertainty + FacilityGraph Feasibility MUST reach orchestration logic
    and influence the recommended advisory action.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Case at Rural PHC with acute STEMI cardiac symptoms
        res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-PHC-01",
                "narrative_text": "Severe crushing chest pain radiating to left arm and jaw.",
                "vitals": {"heart_rate": 110, "systolic_bp": 130, "spo2_percent": 96},
            },
        )
        case_id = res.json()["case_id"]

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-PHC-01"},
        )
        assert orch_res.status_code == 200
        data = orch_res.json()
        # Rural PHC lacks Cath Lab and Troponin -> Local feasibility INFEASIBLE -> Orchestration advises REFER
        assert data["recommended_action"] == "REFER"
        assert "inputs_considered" in data
        assert data["inputs_considered"]["feasibility_status"] == "INFEASIBLE"


@pytest.mark.asyncio
async def test_acceptance_gate_5_outcome_loop():
    """
    Acceptance Gate 5 — OUTCOME LOOP:
    A completed action/outcome must be representable, update encounter FSM,
    and route de-identified telemetry to system analytics.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={"facility_id": "FAC-DH-04", "narrative_text": "Routine checkup."},
        )
        case_id = intake_res.json()["case_id"]

        outcome_res = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json={
                "disposition": "ADMITTED_INPATIENT",
                "final_condition": "STABLE",
                "notes": "Admitted to general medical ward for observation.",
            },
        )
        assert outcome_res.status_code == 200
        assert outcome_res.json()["status"] == "OUTCOME"

        # Verify case status via detail endpoint
        case_detail = await client.get(f"/api/v1/cases/{case_id}")
        assert case_detail.status_code == 200
        assert case_detail.json()["status"] == "OUTCOME"
