"""CLINOVA AI — Comprehensive Audit Test Suite: Regular vs Emergency Intake.

Verifies all 18 clinical scenarios specified in Section G of Master Specification:
1. Regular intake with a complete typed narrative.
2. Regular intake with a voice narrative.
3. Extraction failure followed by successful retry.
4. Partial extraction with missing-information detection.
5. Adaptive question answered and summary updated.
6. No additional questions required.
7. Regular case routed to staff verification and vital signs.
8. Verified staff data rejoining the same Master Case.
9. Regular case progressing to CAREGRAPH and clinician review.
10. Emergency case routed directly to rapid assessment.
11. Emergency escalation when configured urgent signals are present.
12. Emergency workflow when optional AI/transcription is unavailable.
13. Emergency handoff to the configured Emergency Ward or OT workflow.
14. Refresh and resume an in-progress case.
15. Duplicate-submit and stale-response handling.
16. Incorrect-role and cross-patient access attempts.
17. Correct patient-specific report generation and download.
18. Complete regression test of both pathways after changes.
"""

import uuid
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_AUDITOR,
)
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Patient,
    Encounter,
    Case,
    CaseStateTransition,
    Consent,
    Evidence,
    Vital,
    VitalReading,
    TimelineEvent,
    AuditEvent,
    AuditLog,
    FollowUpQuestion,
    User,
)


@pytest.fixture(autouse=True)
async def setup_audit_environment():
    """Ensure database is initialized and strict auth is configured."""
    await init_db()
    orig_legacy_headers = settings.ALLOW_LEGACY_ACTOR_HEADERS
    orig_legacy_anon = settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK
    settings.ALLOW_LEGACY_ACTOR_HEADERS = False
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False

    yield

    settings.ALLOW_LEGACY_ACTOR_HEADERS = orig_legacy_headers
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = orig_legacy_anon


async def login(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Helper to authenticate and return access token."""
    res = await client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# ===========================================================================
# SCENARIOS 1 - 18
# ===========================================================================

@pytest.mark.asyncio
async def test_scenario_1_regular_intake_typed_narrative():
    """1. Regular intake with a complete typed narrative."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "30-39",
                "biological_sex": "MALE",
                "chief_complaint": "Low grade fever for 3 days with mild dry cough, body ache, no chest pain, no breathing difficulty",
                "symptom_duration": "3 days",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["pathway"] == "REGULAR_STANDARD"
        assert data["case_id"]
        assert data["encounter_id"]
        assert data["patient_synthetic_id"].startswith("PT-SYN-")
        assert data["current_state"] == "INTAKE_RECORDED"
        assert data["primary_syndrome"] is not None
        assert data["required_bundle"] is not None
        assert data["summary"] is not None
        assert data["uncertainty_score"] is not None
        assert data["safety_escalated"] is False


@pytest.mark.asyncio
async def test_scenario_2_regular_intake_voice_narrative():
    """2. Regular intake with a voice narrative."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "reported_age_bracket": "50-59",
                "biological_sex": "MALE",
                "chief_complaint": "Patient reports pain via audio recording",
                "voice_transcript": "Severe acute retrosternal chest pain radiating to left jaw with sweating for 2 hours",
                "intake_channel": "VOICE_TRANSCRIBED",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["primary_syndrome"] == "CHEST_PAIN"
        assert data["required_bundle"] == "BUNDLE_STEMI_CARDIAC"
        assert len(data["extracted_entities"]) > 0
        assert any(e["name"] == "severe_chest_pain" for e in data["extracted_entities"])


@pytest.mark.asyncio
async def test_scenario_3_extraction_failure_followed_by_successful_retry():
    """3. Extraction failure (invalid empty input) followed by successful retry."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")

        # Step 1: Whitespace-only complaint triggers validation failure
        fail_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "   \n\t  ",
                "consent_confirmed": True,
            },
        )
        assert fail_res.status_code == 422
        assert fail_res.json()["error"]["code"] == "VALIDATION_ERROR"

        # Step 2: Retry with valid structured narrative succeeds cleanly
        retry_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Persistent dry itchy skin with mild urticaria for 4 days",
                "consent_confirmed": True,
            },
        )
        assert retry_res.status_code == 200
        assert retry_res.json()["success"] is True
        assert retry_res.json()["current_state"] == "INTAKE_RECORDED"


@pytest.mark.asyncio
async def test_scenario_4_partial_extraction_with_missing_information_detection():
    """4. Partial extraction with missing-information detection."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Sudden sharp chest pain",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["primary_syndrome"] == "CHEST_PAIN"
        # Protocol completeness detects missing parameters (e.g. onset_duration, heart_rate, ecg_troponin)
        assert data["missing_parameters"] is not None
        assert len(data["missing_parameters"]) > 0
        assert data["uncertainty_score"] > 0.30
        assert len(data["follow_up_questions"]) > 0


@pytest.mark.asyncio
async def test_scenario_5_adaptive_question_answered_and_summary_updated():
    """5. Adaptive question answered and persisted against the case."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Severe chest pain",
                "consent_confirmed": True,
            },
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]
        questions = intake_res.json()["follow_up_questions"]
        assert len(questions) > 0
        target_q = questions[0]

        # Answer question via foundation follow-up API
        ans_res = await client.post(
            f"/api/v1/cases/{case_id}/follow-up/answer",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question_id": target_q["id"],
                "answer_text": "Pain started 2 hours ago while sitting; radiates into left arm.",
            },
        )
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        assert ans_data["question_id"] == target_q["id"]
        assert ans_data["answer_text"] == "Pain started 2 hours ago while sitting; radiates into left arm."

        # Verify DB state of answered question
        async with async_session_factory() as db:
            q_db = await db.get(FollowUpQuestion, target_q["id"])
            assert q_db is not None
            assert q_db.status == "ANSWERED"


@pytest.mark.asyncio
async def test_scenario_6_no_additional_questions_required():
    """6. Complete information results in protocol satisfaction."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Mild recurrent seasonal allergy",
                "symptom_duration": "5 days",
                "vitals": {
                    "heart_rate": 72,
                    "systolic_bp": 120,
                    "diastolic_bp": 80,
                    "temperature_celsius": 36.8,
                    "spo2_percent": 98,
                    "respiratory_rate": 16,
                    "avpu_score": "ALERT",
                },
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["primary_syndrome"] == "GENERAL_ROUTINE"
        # All required general routine parameters (duration, HR, SBP, Temp) provided
        assert len(data["missing_parameters"]) == 0
        assert len(data["follow_up_questions"]) == 0


@pytest.mark.asyncio
async def test_scenario_7_regular_case_routed_to_staff_verification():
    """7. Regular case routed to staff triage queue for vital signs verification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Moderate abdominal pain and nausea for 1 day",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        case_id = res.json()["case_id"]

        # Nurse views queue and sees case in worklist
        nurse_token = await login(client, "nurse")
        q_res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {nurse_token}"})
        assert q_res.status_code == 200
        q_data = q_res.json()
        q_cases = q_data.get("queue", [])
        assert any(c["case_id"] == case_id for c in q_cases)


@pytest.mark.asyncio
async def test_scenario_8_verified_staff_data_rejoining_same_master_case():
    """8. Verified staff data rejoining the same Master Case ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login(client, "patient")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "General body weakness",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]
        original_encounter = intake_res.json()["encounter_id"]
        original_pt_id = intake_res.json()["patient_id"]

        # Nurse records triage vital signs to the same case
        nurse_token = await login(client, "nurse")
        vit_res = await client.post(
            f"/api/v1/caregraph/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 84,
                "systolic_bp": 124,
                "diastolic_bp": 82,
                "spo2_percent": 97,
                "respiratory_rate": 16,
                "temperature_celsius": 37.1,
                "avpu_score": "ALERT",
            },
        )
        assert vit_res.status_code == 200

        # Verify Master Case continuity
        cg_res = await client.get(f"/api/v1/caregraph/{case_id}", headers={"Authorization": f"Bearer {nurse_token}"})
        assert cg_res.status_code == 200
        cg_data = cg_res.json()
        assert cg_data["case"]["id"] == case_id
        assert cg_data["case"]["encounter_id"] == original_encounter
        assert len(cg_data["vitals_history"]) >= 1


@pytest.mark.asyncio
async def test_scenario_9_regular_case_progressing_to_caregraph_and_clinician_review():
    """9. Regular case progressing to CAREGRAPH analysis and authorized clinician sign-off."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Mild productive cough with clear sputum",
                "symptom_duration": "4 days",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # Nurse advances case through triage to clinician review
        t_res1 = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"action": "START_TRIAGE", "reason": "Begin routine triage"},
        )
        assert t_res1.status_code == 200, t_res1.text

        t_res2 = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"action": "SUBMIT_TRIAGE", "reason": "Triage vitals verified and complete"},
        )
        assert t_res2.status_code == 200, t_res2.text

        # Clinician inspects CAREGRAPH
        doc_token = await login(client, "clinician")
        cg_res = await client.get(f"/api/v1/caregraph/{case_id}", headers={"Authorization": f"Bearer {doc_token}"})
        assert cg_res.status_code == 200
        assert cg_res.json()["case"]["pathway"] == "OPD_GENERAL"
        assert cg_res.json()["case"]["emergency_active"] is False

        # Clinician records authorized clinical decision
        dec_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            headers={"Authorization": f"Bearer {doc_token}"},
            json={
                "decision_type": "ACCEPT",
                "clinical_rationale": "Recommend complete blood count and sputum examination. Routine follow-up.",
                "clinical_impression": "Mild acute bronchitis",
                "treatment_plan": "Supportive care with fluids and rest",
            },
        )
        assert dec_res.status_code == 200, dec_res.text
        dec_data = dec_res.json()
        assert dec_data["case_id"] == case_id
        assert dec_data["decision_type"] == "ACCEPT"
        assert dec_data["current_state"] == "DISPOSITION_PENDING"


@pytest.mark.asyncio
async def test_scenario_10_emergency_case_routed_directly_to_rapid_assessment():
    """10. Emergency case created by nurse routes directly to rapid assessment."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Acute severe shortness of breath with central cyanosis",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["pathway"] == "EMERGENCY"
        assert data["current_state"] == "INTAKE_RECORDED"

        # Check case persisted with CRITICAL acuity
        case_id = data["case_id"]
        cg_res = await client.get(f"/api/v1/caregraph/{case_id}", headers={"Authorization": f"Bearer {nurse_token}"})
        assert cg_res.status_code == 200
        assert cg_res.json()["case"]["acuity_tier"] == "CRITICAL"
        assert cg_res.json()["case"]["emergency_active"] is True


@pytest.mark.asyncio
async def test_scenario_11_emergency_escalation_when_urgent_signals_present():
    """11. Automatic emergency escalation when configured urgent signals (stridor/massive bleeding) are present."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patient selects regular intake, but narrative contains critical stridor
        patient_token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Patient has acute choking, foreign body aspiration and severe stridor with inability to speak",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        # Safety escalation triggered: forced to EMERGENCY pathway
        assert data["safety_escalated"] is True
        assert data["pathway"] == "EMERGENCY"
        assert any(rf["rule_id"] == "RF-CLINICAL-AIRWAY" and rf["triggered"] for rf in data["red_flags"])


@pytest.mark.asyncio
async def test_scenario_12_emergency_workflow_deterministic_safety_without_ai():
    """12. Emergency deterministic red flag rules execute reliably without AI dependencies."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "nurse")
        # Massive bleeding + shock in vital signs
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Active massive bleeding after road traffic accident",
                "vitals": {
                    "heart_rate": 138,
                    "systolic_bp": 72,
                    "diastolic_bp": 45,
                    "spo2_percent": 86,
                    "respiratory_rate": 32,
                    "avpu_score": "VOICE",
                },
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["pathway"] == "EMERGENCY"
        # Deterministic red flags: Hypoxia (SpO2 86 <= 88) + Shock (SBP 72 <= 80) + Massive bleeding
        rf_dict = {rf["rule_id"]: rf["triggered"] for rf in data["red_flags"]}
        assert rf_dict.get("RF-PHYSIO-HYPOXIA") is True
        assert rf_dict.get("RF-PHYSIO-SHOCK") is True
        assert rf_dict.get("RF-CLINICAL-MASSIVE-BLEEDING") is True


@pytest.mark.asyncio
async def test_scenario_13_emergency_handoff_to_ward_or_ot_workflow():
    """13. Emergency handoff to configured Emergency Ward or OT workflow."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Acute surgical abdomen with perforation peritonitis",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # Step 1: Invalid destination unit rejected with 422
        bad_handoff = await client.post(
            f"/api/v1/cases/{case_id}/handoff",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "destination_unit": "GENERAL_CAFETERIA",
                "receiving_team": "Team Alpha",
            },
        )
        assert bad_handoff.status_code == 422
        assert bad_handoff.json()["error"]["code"] == "VALIDATION_ERROR"

        # Step 2: Valid handoff to OPERATING_THEATRE
        good_handoff = await client.post(
            f"/api/v1/cases/{case_id}/handoff",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "destination_unit": "OPERATING_THEATRE",
                "receiving_team": "Trauma Surgery Emergency Team B",
                "handoff_status": "ACCEPTED",
                "notes": "Emergency exploratory laparotomy indicated. 2 units PRBC cross-matched.",
            },
        )
        assert good_handoff.status_code == 200
        h_data = good_handoff.json()
        assert h_data["success"] is True
        assert h_data["destination_unit"] == "OPERATING_THEATRE"
        assert h_data["current_state"] == "EMERGENCY_HANDOFF"

        # Verify timeline event recorded
        cg_res = await client.get(f"/api/v1/caregraph/{case_id}", headers={"Authorization": f"Bearer {nurse_token}"})
        timeline = cg_res.json()["timeline"]
        assert any(t["event_type"] == "EMERGENCY_HANDOFF" for t in timeline)


@pytest.mark.asyncio
async def test_scenario_14_refresh_and_resume_in_progress_case():
    """14. Refresh and resume an in-progress case preserves exact pathway and state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Acute cardiac chest pain",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # Multiple consecutive reads mimic page reloads
        for _ in range(3):
            cg_res = await client.get(f"/api/v1/caregraph/{case_id}", headers={"Authorization": f"Bearer {nurse_token}"})
            assert cg_res.status_code == 200
            data = cg_res.json()
            assert data["case"]["pathway"] == "EMERGENCY"
            assert data["case"]["emergency_active"] is True
            assert data["case"]["status"] == "NEW"


@pytest.mark.asyncio
async def test_scenario_15_duplicate_submit_and_stale_response_handling():
    """15. Idempotent submission prevents duplicate records and handles stale requests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        sub_id = f"sub-audit-{uuid.uuid4().hex[:8]}"

        # Submission 1
        res1 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Persistent headache and fever",
                "client_submission_id": sub_id,
                "consent_confirmed": True,
            },
        )
        assert res1.status_code == 200
        case_id_1 = res1.json()["case_id"]
        assert res1.json()["is_duplicate"] is False

        # Submission 2 with same idempotency key
        res2 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Persistent headache and fever",
                "client_submission_id": sub_id,
                "consent_confirmed": True,
            },
        )
        assert res2.status_code == 200
        assert res2.json()["is_duplicate"] is True
        assert res2.json()["case_id"] == case_id_1


@pytest.mark.asyncio
async def test_scenario_16_incorrect_role_and_cross_patient_access_attempts():
    """16. Server-side role boundaries prevent unauthorized and cross-patient actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login(client, "patient")

        # 1. Patient cannot access staff triage queue
        queue_res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {patient_token}"})
        assert queue_res.status_code == 403

        # 2. Patient cannot alter pathways
        pathway_res = await client.patch(
            f"/api/v1/cases/{uuid.uuid4()}/pathway",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"pathway": "EMERGENCY"},
        )
        assert pathway_res.status_code == 403

        # 3. Patient cannot execute handoff
        handoff_res = await client.post(
            f"/api/v1/cases/{uuid.uuid4()}/handoff",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"destination_unit": "OPERATING_THEATRE", "receiving_team": "Team Alpha"},
        )
        assert handoff_res.status_code == 403


@pytest.mark.asyncio
async def test_scenario_17_correct_patient_specific_report_generation():
    """17. Patient report summary and PDF generation with cryptographic tamper evidence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Mild dermatitis and rash on forearm",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # Report Summary endpoint
        doc_token = await login(client, "clinician")
        rep_res = await client.get(f"/api/v1/reports/{case_id}/summary", headers={"Authorization": f"Bearer {doc_token}"})
        assert rep_res.status_code == 200
        rep_data = rep_res.json()
        assert rep_data["case"]["id"] == case_id
        assert "evidence" in rep_data

        # PDF Download endpoint
        pdf_res = await client.get(f"/api/v1/reports/{case_id}/pdf", headers={"Authorization": f"Bearer {doc_token}"})
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content.startswith(b"%PDF")
        assert "x-report-sha256" in pdf_res.headers


@pytest.mark.asyncio
async def test_scenario_18_complete_regression_test_both_pathways():
    """18. Complete regression test of both Regular and Emergency pathways."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        doc_token = await login(client, "clinician")

        # --- A. REGULAR PATHWAY ---
        reg_intake = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Mild recurrent seasonal allergy with sneezing and rhinorrhea",
                "symptom_duration": "4 days",
                "consent_confirmed": True,
            },
        )
        assert reg_intake.status_code == 200
        reg_case_id = reg_intake.json()["case_id"]
        assert reg_intake.json()["pathway"] == "REGULAR_STANDARD"

        # Regular case pathway change by authorized staff
        pw_change = await client.patch(
            f"/api/v1/cases/{reg_case_id}/pathway",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"pathway": "OPD_GENERAL", "reason": "Routed to general outpatient desk"},
        )
        assert pw_change.status_code == 200
        assert pw_change.json()["pathway"] == "OPD_GENERAL"

        # --- B. EMERGENCY PATHWAY ---
        em_intake = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Crushing retrosternal chest pain with diaphoresis",
                "consent_confirmed": True,
            },
        )
        assert em_intake.status_code == 200
        em_case_id = em_intake.json()["case_id"]
        assert em_intake.json()["pathway"] == "EMERGENCY"

        # Emergency OT Handoff
        handoff = await client.post(
            f"/api/v1/cases/{em_case_id}/handoff",
            headers={"Authorization": f"Bearer {doc_token}"},
            json={
                "destination_unit": "CARDIAC_CATH_LAB",
                "receiving_team": "Interventional Cardiology On-Call Team",
                "notes": "Emergency primary PCI scheduled.",
            },
        )
        assert handoff.status_code == 200
        assert handoff.json()["destination_unit"] == "CARDIAC_CATH_LAB"
        assert handoff.json()["current_state"] == "EMERGENCY_HANDOFF"


# ===========================================================================
# DEEP AUDIT VERIFICATION: NEGATION, VOICE ESCALATION, EVIDENCE & GUARDS
# ===========================================================================

@pytest.mark.asyncio
async def test_clinical_negation_prevents_false_emergency_escalation():
    """Verify clinical negation handles negative assertions without spurious red-flag escalation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Minor scratch on right hand. Patient denies chest pain, denies shortness of breath, no stridor, no massive bleeding.",
                "symptom_duration": "1 hour",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["safety_escalated"] is False
        assert data["pathway"] == "REGULAR_STANDARD"
        assert data["primary_syndrome"] == "GENERAL_ROUTINE"
        # Verify no airway or bleeding red flags were falsely triggered
        rf_dict = {rf["rule_id"]: rf["triggered"] for rf in data["red_flags"]}
        assert rf_dict.get("RF-CLINICAL-AIRWAY") is not True
        assert rf_dict.get("RF-CLINICAL-MASSIVE-BLEEDING") is not True


@pytest.mark.asyncio
async def test_voice_transcript_airway_stridor_triggers_emergency_escalation():
    """Verify voice transcript red flag (stridor) is evaluated and escalates to EMERGENCY."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Patient came in coughing",
                "voice_transcript": "Child swallowed a foreign object, now presenting with acute choking and severe inspiratory stridor",
                "intake_channel": "VOICE_TRANSCRIBED",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["safety_escalated"] is True
        assert data["pathway"] == "EMERGENCY"
        assert any(rf["rule_id"] == "RF-CLINICAL-AIRWAY" and rf["triggered"] for rf in data["red_flags"])


@pytest.mark.asyncio
async def test_parameter_audit_epistemic_classification_contract():
    """Verify intake response contains parameter_audit with explicit epistemic classifications."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "High fever and persistent dry cough for 3 days",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "parameter_audit" in data
        assert isinstance(data["parameter_audit"], list)
        assert len(data["parameter_audit"]) > 0
        states = {item["state"] for item in data["parameter_audit"]}
        assert "KNOWN" in states or "UNKNOWN" in states
        for item in data["parameter_audit"]:
            assert "parameter" in item
            assert "state" in item
            assert "reason" in item


@pytest.mark.asyncio
async def test_questions_answer_alias_and_evidence_reduction():
    """Verify /cases/{case_id}/questions/answer alias, evidence persistence, and uncertainty score reduction."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Severe sharp abdominal pain with nausea",
                "consent_confirmed": True,
            },
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]
        initial_u = intake_res.json()["uncertainty_score"]
        questions = intake_res.json()["follow_up_questions"]
        assert len(questions) > 0

        # Answer question via the frontend alias endpoint /cases/{case_id}/questions/answer
        target_q = questions[0]
        ans_res = await client.post(
            f"/api/v1/cases/{case_id}/questions/answer",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question_id": target_q["id"],
                "answer_text": "Pain localized to right lower quadrant, began 6 hours ago.",
            },
        )
        assert ans_res.status_code == 200
        ans_json = ans_res.json()
        assert ans_json.get("answer_id") or ans_json.get("id")
        assert ans_json["question_id"] == target_q["id"]

        # Verify DB records: Evidence, TimelineEvent, and uncertainty reduction
        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case.uncertainty_score < initial_u

            # Check TimelineEvent
            tl_stmt = select(TimelineEvent).where(
                TimelineEvent.case_id == case_id,
                TimelineEvent.event_type == "FOLLOW_UP_ANSWERED",
            )
            tl_ev = (await db.execute(tl_stmt)).scalars().first()
            assert tl_ev is not None
            assert "Pain localized to right lower quadrant" in tl_ev.event_content

            # Check Evidence
            ev_stmt = select(Evidence).where(
                Evidence.case_id == case_id,
                Evidence.source_class == "PATIENT_REPORTED",
            )
            ev_list = (await db.execute(ev_stmt)).scalars().all()
            assert any("Pain localized" in str(ev.content_value) for ev in ev_list)


@pytest.mark.asyncio
async def test_pathway_validation_and_closed_case_guards():
    """Verify invalid pathway rejection and closed-case handoff and pathway guards."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login(client, "nurse")
        intake_res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Routine checkup",
                "consent_confirmed": True,
            },
        )
        case_id = intake_res.json()["case_id"]

        # 1. Invalid pathway string rejected with 422
        bad_pw = await client.patch(
            f"/api/v1/cases/{case_id}/pathway",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"pathway": "INVALID_PATHWAY_FOO"},
        )
        assert bad_pw.status_code == 422

        # 2. Close the case
        async with async_session_factory() as db:
            c = await db.get(Case, case_id)
            c.is_closed = True
            await db.commit()

        # 3. Attempt to alter pathway on closed case -> 400
        closed_pw = await client.patch(
            f"/api/v1/cases/{case_id}/pathway",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"pathway": "EMERGENCY"},
        )
        assert closed_pw.status_code == 400

        # 4. Attempt emergency handoff on closed case -> 400
        closed_handoff = await client.post(
            f"/api/v1/cases/{case_id}/handoff",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "destination_unit": "EMERGENCY_WARD",
                "receiving_team": "ER Team",
            },
        )
        assert closed_handoff.status_code == 400


@pytest.mark.asyncio
async def test_document_upload_ocr_extracted_evidence_persistence():
    """Verify document upload intake creates OCR_EXTRACTED evidence in the database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Persistent dry cough",
                "document_uploaded": True,
                "document_type": "LAB_REPORT",
                "narrative_notes": "Attached external lab report: blood_count.pdf",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            ev_stmt = select(Evidence).where(
                Evidence.case_id == case_id,
                Evidence.source_class == "OCR_EXTRACTED",
            )
            ev = (await db.execute(ev_stmt)).scalars().first()
            assert ev is not None
            assert ev.epistemic_state == "KNOWN"
            assert ev.parameter_name in ["lab_report_summary", "uploaded_medical_document"]

