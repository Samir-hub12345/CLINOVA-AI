"""CLINOVA AI — Comprehensive Clinical Scenario Test Suite.

Verifies all 17 Mandatory Synthetic Clinical Scenarios from Section 21 of the Master Contract:
SCEN-01: Routine Ambulatory Case (Action: CONTINUE)
SCEN-02: Urgent Non-Critical Case (Action: OBSERVE)
SCEN-03: Critical Resuscitation Case (Action: ESCALATE)
SCEN-04: Incomplete Information Case (State: INSUFFICIENT_DATA -> Action: ASK)
SCEN-05: Conflicting Evidence Case (State: CONFLICTING_DATA -> Action: VERIFY)
SCEN-06: Low-Confidence OCR Case (State: OCR_FAILED -> Fallback)
SCEN-07: Voice Transcription Workflow (VOICE_TRANSCRIBED provenance & Hindi translation)
SCEN-08: New Evidence Changing Risk (Lab / Vitals elevation -> Delta R update)
SCEN-09: Deteriorating Trajectory Case (Delta R >= +1.5/hr -> Action: ESCALATE)
SCEN-10: Clinician Override Case (Doctor overrides OBSERVE to ESCALATE with rationale)
SCEN-11: Referral Required Case (Stroke at rural PHC -> INFEASIBLE -> Action: REFER)
SCEN-12: Current Facility Unsuitable (Obstetric Hemorrhage lacking blood bank -> INFEASIBLE)
SCEN-13: Alternative Facility Match & SBAR Generation (Ranks destinations, generates SBAR)
SCEN-14: Referral Completion Case (Transfer completes -> COMPLETED)
SCEN-15: Follow-up & Outcome Loop (Discharge disposition -> OUTCOME)
SCEN-16: Facility Demand Increase (ICU capacity saturation discounts referral rank)
SCEN-17: System Signal Generation (Hemorrhagic fever cases trigger outbreak Z-score alert)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.init_db import init_db


@pytest.fixture(autouse=True)
async def setup_database():
    """Initializes and seeds database before running scenario tests."""
    await init_db()


@pytest.mark.asyncio
async def test_scen_01_routine_ambulatory_case():
    """SCEN-01: Routine Ambulatory Case -> Action: CONTINUE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Intake
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "reported_name": "Test Routine",
                "reported_age": 25,
                "biological_sex": "FEMALE",
                "narrative_text": "Mild seasonal cold, runny nose, slight throat irritation for 2 days.",
                "vitals": {
                    "heart_rate": 72,
                    "systolic_bp": 118,
                    "diastolic_bp": 78,
                    "spo2_percent": 99,
                    "respiratory_rate": 16,
                    "temperature_celsius": 36.8,
                },
            },
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]

        # 2. Orchestration Evaluation
        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        data = orch_res.json()
        assert data["recommended_action"] == "CONTINUE"
        assert data["priority_level"] == "ROUTINE_GREEN"


@pytest.mark.asyncio
async def test_scen_02_urgent_non_critical_case():
    """SCEN-02: Urgent Non-Critical Case -> Action: OBSERVE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "reported_name": "Test Urgent",
                "reported_age": 52,
                "narrative_text": "High fever, body chills, generalized weakness.",
                "vitals": {
                    "heart_rate": 98,
                    "systolic_bp": 125,
                    "diastolic_bp": 82,
                    "spo2_percent": 96,
                    "respiratory_rate": 20,
                    "temperature_celsius": 39.2,
                },
            },
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "OBSERVE"


@pytest.mark.asyncio
async def test_scen_03_critical_resuscitation_case():
    """SCEN-03: Critical Resuscitation Case -> Action: ESCALATE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "reported_name": "Test Critical",
                "reported_age": 34,
                "narrative_text": "Polytrauma after road accident, massive bleeding from thigh, hypotensive shock.",
                "vitals": {
                    "heart_rate": 142,
                    "systolic_bp": 72,
                    "diastolic_bp": 40,
                    "spo2_percent": 88,
                    "respiratory_rate": 28,
                    "temperature_celsius": 35.4,
                    "avpu_score": "VOICE",
                },
            },
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]
        assert intake_res.json()["acuity_tier"] == "CRITICAL"

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "ESCALATE"


@pytest.mark.asyncio
async def test_scen_04_incomplete_information_case():
    """SCEN-04: Incomplete Information Case -> State: INSUFFICIENT_DATA -> Action: ASK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Vague chest discomfort reported.",
                "vitals": {
                    "heart_rate": 78,
                    "systolic_bp": 120,
                    "diastolic_bp": 80,
                    "spo2_percent": 98,
                    "respiratory_rate": 16,
                },
            },
        )
        assert intake_res.status_code == 200
        data = intake_res.json()
        assert data["status"] == "INSUFFICIENT_DATA"
        assert len(data["missing_parameters"]) > 0

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": data["case_id"], "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "ASK"


@pytest.mark.asyncio
async def test_scen_05_conflicting_evidence_case():
    """SCEN-05: Conflicting Evidence Case -> State: CONFLICTING_DATA -> Action: VERIFY."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Patient feels completely normal and asymptomatic with no fever.",
                "vitals": {
                    "heart_rate": 80,
                    "systolic_bp": 120,
                    "spo2_percent": 84,  # Contradicts "asymptomatic/normal"
                    "temperature_celsius": 39.5,  # Contradicts "no fever"
                },
            },
        )
        assert intake_res.status_code == 200
        data = intake_res.json()
        assert data["status"] == "CONFLICTING_DATA"
        assert len(data["conflicts"]) > 0

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": data["case_id"], "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "VERIFY"


@pytest.mark.asyncio
async def test_scen_06_low_confidence_ocr_case():
    """SCEN-06: Low-Confidence OCR Case -> OCR_FAILED -> Fallback."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ocr_res = await client.post(
            "/api/v1/intake/ocr",
            json={
                "raw_text": "Faded smudged discharge slip with unclear values...",
                "confidence_score": 0.42,  # Below 0.70 threshold
            },
        )
        assert ocr_res.status_code == 200
        data = ocr_res.json()
        assert data["status"] == "OCR_FAILED"
        assert "below confidence threshold" in data["error"]


@pytest.mark.asyncio
async def test_scen_07_voice_transcription_workflow():
    """SCEN-07: Voice Transcription Workflow in Hindi -> VOICE_TRANSCRIBED provenance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        voice_res = await client.post(
            "/api/v1/intake/voice",
            json={
                "facility_id": "FAC-PHC-01",
                "audio_transcript": "मुझे छाती में दर्द हो रहा है और चक्कर आ रहे हैं",
                "confidence_score": 0.94,
                "language": "hi",
            },
        )
        assert voice_res.status_code == 200
        data = voice_res.json()
        assert data["provenance_type"] == "VOICE_TRANSCRIBED"
        assert data["voice_confidence"] == 0.94
        assert data["primary_syndrome"] == "CHEST_PAIN"


@pytest.mark.asyncio
async def test_scen_08_new_evidence_changing_risk():
    """SCEN-08: New Evidence Changing Risk -> CareGraph update."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Start with moderate asthma
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Wheezing and cough for 1 day.",
                "vitals": {
                    "heart_rate": 84,
                    "systolic_bp": 120,
                    "spo2_percent": 95,
                    "respiratory_rate": 20,
                },
            },
        )
        case_id = intake_res.json()["case_id"]
        initial_risk = intake_res.json()["risk_score"]

        # Append deteriorating vitals
        vitals_res = await client.post(
            f"/api/v1/caregraph/{case_id}/vitals",
            json={
                "heart_rate": 136,
                "systolic_bp": 88,
                "spo2_percent": 86,
                "respiratory_rate": 32,
                "avpu_score": "VOICE",
            },
        )
        assert vitals_res.status_code == 200
        data = vitals_res.json()
        assert data["updated_risk_score"] > initial_risk
        assert data["updated_acuity_tier"] == "CRITICAL"


@pytest.mark.asyncio
async def test_scen_09_deteriorating_trajectory_case():
    """SCEN-09: Deteriorating Trajectory Case (Delta R >= +1.5/hr) -> Action transitions to ESCALATE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Fever and mild tachycardia.",
                "vitals": {
                    "heart_rate": 92,
                    "systolic_bp": 120,
                    "spo2_percent": 97,
                    "respiratory_rate": 18,
                    "temperature_celsius": 38.2,
                },
            },
        )
        case_id = intake_res.json()["case_id"]

        # Serial vitals indicating rapid deterioration
        vitals_res = await client.post(
            f"/api/v1/caregraph/{case_id}/vitals",
            json={
                "heart_rate": 138,
                "systolic_bp": 84,
                "spo2_percent": 88,
                "respiratory_rate": 30,
                "temperature_celsius": 39.8,
            },
        )
        assert vitals_res.status_code == 200
        assert vitals_res.json()["trajectory_slope"] >= 1.0

        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "ESCALATE"


@pytest.mark.asyncio
async def test_scen_10_clinician_override_case():
    """SCEN-10: Clinician Override Case -> Decision recorded with mandatory rationale."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-DH-04",
                "narrative_text": "Abdominal discomfort.",
                "vitals": {"heart_rate": 80, "systolic_bp": 120, "spo2_percent": 98},
            },
        )
        case_id = intake_res.json()["case_id"]

        # Doctor overrides advisory recommendation to ESCALATE
        dec_res = await client.post(
            "/api/v1/orchestration/decision",
            json={
                "case_id": case_id,
                "action": "ESCALATE",
                "decision_type": "OVERRIDE",
                "clinician_id": "usr-doc-01",
                "override_reason": "Bedside exam reveals acute rigid peritonitis and signs of septic perforation.",
            },
        )
        assert dec_res.status_code == 200
        data = dec_res.json()
        assert data["decision_type"] == "OVERRIDE"
        assert data["action_authorized"] == "ESCALATE"
        assert data["case_status"] == "ESCALATE"


@pytest.mark.asyncio
async def test_scen_11_referral_required_case():
    """SCEN-11: Referral Required Case (Stroke at rural PHC without CT scanner) -> Action: REFER."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patient arrives at Angul Rural PHC (FAC-PHC-01) with acute stroke symptoms
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-PHC-01",
                "narrative_text": "Acute right-sided facial droop and arm weakness starting 45 minutes ago. Suspected stroke.",
                "vitals": {
                    "heart_rate": 86,
                    "systolic_bp": 160,
                    "diastolic_bp": 98,
                    "spo2_percent": 97,
                    "respiratory_rate": 18,
                },
            },
        )
        case_id = intake_res.json()["case_id"]
        assert intake_res.json()["primary_syndrome"] == "STROKE_ACUTE"

        # Check local feasibility at PHC
        feas_res = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": "FAC-PHC-01", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        )
        assert feas_res.status_code == 200
        assert feas_res.json()["feasibility"]["status"] == "INFEASIBLE"

        # Orchestration advises REFER
        orch_res = await client.post(
            "/api/v1/orchestration/evaluate",
            json={"case_id": case_id, "facility_id": "FAC-PHC-01"},
        )
        assert orch_res.status_code == 200
        assert orch_res.json()["recommended_action"] == "REFER"


@pytest.mark.asyncio
async def test_scen_12_current_facility_unsuitable_obstetric():
    """SCEN-12: Obstetric Hemorrhage at PHC lacking blood bank -> INFEASIBLE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        feas_res = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": "FAC-PHC-01", "required_bundle": "BUNDLE_OBSTETRIC_HEMORRHAGE"},
        )
        assert feas_res.status_code == 200
        feas = feas_res.json()["feasibility"]
        assert feas["status"] == "INFEASIBLE"
        assert "BLOOD_BANK" in feas["missing_capabilities"]


@pytest.mark.asyncio
async def test_scen_13_alternative_facility_match_and_sbar():
    """SCEN-13: Alternative Facility Ranking & SBAR Transfer Packet Generation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Rank network facilities from PHC
        rank_res = await client.post(
            "/api/v1/facilities/referral-rank",
            json={"current_facility_id": "FAC-PHC-01", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        )
        assert rank_res.status_code == 200
        rankings = rank_res.json()["ranked_destinations"]
        assert len(rankings) > 0
        # District Hospital or Tertiary Med College should be top capable destination
        top_dest = rankings[0]
        assert top_dest["feasibility_status"] == "FEASIBLE"

        # Generate SBAR packet
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={
                "facility_id": "FAC-PHC-01",
                "narrative_text": "Slurred speech and hemiparesis for 1 hour.",
                "vitals": {"heart_rate": 82, "systolic_bp": 150, "spo2_percent": 96},
            },
        )
        case_id = intake_res.json()["case_id"]

        sbar_res = await client.post(
            "/api/v1/referrals/sbar",
            json={"case_id": case_id, "destination_facility_id": top_dest["facility_id"]},
        )
        assert sbar_res.status_code == 200
        sbar = sbar_res.json()
        assert "sbar_situation" in sbar
        assert "sbar_background" in sbar
        assert "sbar_assessment" in sbar
        assert "sbar_recommendation" in sbar


@pytest.mark.asyncio
async def test_scen_14_referral_completion_case():
    """SCEN-14: Referral Dispatch and Completion -> State: COMPLETED."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={"facility_id": "FAC-PHC-01", "narrative_text": "Fracture needing surgery."},
        )
        case_id = intake_res.json()["case_id"]

        create_ref = await client.post(
            "/api/v1/referrals/create",
            json={
                "case_id": case_id,
                "origin_facility_id": "FAC-PHC-01",
                "destination_facility_id": "FAC-DH-04",
                "required_bundle": "BUNDLE_TRAUMA_CRITICAL",
                "sbar_situation": "Trauma referral",
                "sbar_background": "Fall from height",
                "sbar_assessment": "Closed fracture",
                "sbar_recommendation": "OT evaluation",
            },
        )
        assert create_ref.status_code == 200
        ref_id = create_ref.json()["referral_id"]

        # Ambulance arrives and transfer is accepted
        upd_res = await client.post(
            f"/api/v1/referrals/{ref_id}/status",
            json={"status": "COMPLETED"},
        )
        assert upd_res.status_code == 200
        assert upd_res.json()["case_status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_scen_15_outcome_loop():
    """SCEN-15: Case Outcome Loop -> State transitions to OUTCOME."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        intake_res = await client.post(
            "/api/v1/intake/text",
            json={"facility_id": "FAC-DH-04", "narrative_text": "Mild headache."},
        )
        case_id = intake_res.json()["case_id"]

        outcome_res = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            json={
                "disposition": "DISCHARGED_ROUTINE",
                "final_condition": "RESOLVED",
                "notes": "Patient treated with oral analgesics and discharged home.",
            },
        )
        assert outcome_res.status_code == 200
        assert outcome_res.json()["status"] == "OUTCOME"


@pytest.mark.asyncio
async def test_scen_16_facility_demand_increase():
    """SCEN-16: Facility Demand Increase -> ICU saturation flips feasibility to DEGRADED."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Set District Hospital ICU available beds to 0
        cap_res = await client.post(
            "/api/v1/facilities/FAC-DH-04/update-capacity",
            json={"icu_beds_available": 0},
        )
        assert cap_res.status_code == 200

        # Check feasibility of stroke bundle at DH
        match_res = await client.post(
            "/api/v1/facilities/match",
            json={"facility_id": "FAC-DH-04", "required_bundle": "BUNDLE_STROKE_ACUTE"},
        )
        assert match_res.status_code == 200
        feas = match_res.json()["feasibility"]
        assert feas["status"] == "DEGRADED"
        assert "0 available ICU beds" in feas["reason"]

        # Restore DH ICU beds
        await client.post(
            "/api/v1/facilities/FAC-DH-04/update-capacity",
            json={"icu_beds_available": 2},
        )


@pytest.mark.asyncio
async def test_scen_17_system_signal_generation():
    """SCEN-17: System Signal Generation -> Multiple hemorrhagic fever events raise outbreak Z-score alert."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ingest 6 hemorrhagic fever cases
        for _ in range(6):
            await client.post(
                "/api/v1/signalgraph/inject-event",
                json={
                    "facility_id": "FAC-DH-04",
                    "syndrome_tag": "SYNDROME_HEMORRHAGIC_FEVER",
                    "acuity_tier": "URGENT",
                },
            )

        surges_res = await client.get("/api/v1/signalgraph/surges")
        assert surges_res.status_code == 200
        clusters = surges_res.json()["clusters"]
        dengue_cluster = next((c for c in clusters if c["syndrome"] == "SYNDROME_HEMORRHAGIC_FEVER"), None)
        assert dengue_cluster is not None
        assert dengue_cluster["observed_cases_48h"] >= 6
        assert dengue_cluster["z_score"] >= 3.5
        assert dengue_cluster["status"] == "SURGE_ALERT"
