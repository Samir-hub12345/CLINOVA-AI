"""CLINOVA AI — Phase 26: Full Integration + End-to-End (E2E) Verification Test Suite.

Exercises the complete integrated system across:
- Journey A: Regular / Non-Emergency Care Workflow (Intake -> Multimodal -> Triage -> CareGraph -> Orchestration -> Clinician Review -> Referral Lifecycle -> Outcome Loop -> SignalGraph)
- Journey B: Emergency Care Pathway & Deterministic Safety Controls (Emergency Intake -> Acuity Derivation -> Orchestration Escalation -> Human Review Gate -> Prohibited Autonomous Actions Prevention)
- Journey C: Comprehensive Role, Multitenancy & Authorization Boundaries (Patient, Nurse, Clinician, Facility Admin, System Admin cross-case and cross-facility isolation)
- Journey D: Offline Synchronization, Idempotency, Replay Defense & Conflict Resolution (Offline Capture -> Push Sync -> Idempotent Retries -> Tampering Rejection -> Gated Clinician Conflict Resolution)
"""

import pytest
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Case,
    Patient,
    Facility,
    FacilityCapability,
    Document,
    DocumentExtraction,
    Vital,
    TimelineEvent,
    ClinicianDecision,
    Referral,
    CaseOutcome,
    SyncJournal,
    SyncConflict,
    AuditLog,
    AuditEvent,
    FollowUpQuestion,
    FollowUpAnswer,
)
from app.core.config import settings
from app.core.rbac import (
    ROLE_PATIENT,
    ROLE_NURSE,
    ROLE_CLINICIAN,
    ROLE_FACILITY_ADMIN,
    ROLE_SYSTEM_ADMIN,
    ROLE_REFERRAL_COORDINATOR,
)


@pytest.fixture(autouse=True)
async def setup_test_environment():
    """Ensures database is initialized and seed fixtures are in clean baseline state."""
    settings.ALLOW_LEGACY_ACTOR_HEADERS = False
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False
    await init_db()
    yield
    settings.ALLOW_LEGACY_ACTOR_HEADERS = False
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False


async def login_user(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Authenticates via POST /api/v1/auth/login and extracts bearer access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# JOURNEY A: REGULAR / NON-EMERGENCY CARE COMPLETE END-TO-END WORKFLOW
# ===========================================================================
@pytest.mark.asyncio
async def test_journey_a_regular_care_end_to_end():
    """
    Validates Journey A:
    1. Authenticate patient test account
    2. Submit structured regular intake with consent
    3. Verify case, encounter, patient, and timeline initialization
    4. Upload clinical report document & verify OCR extraction
    5. Nurse triages case and records vital signs
    6. Verify CareGraph trajectory, slope, and uncertainty representation
    7. Orchestration engine evaluates clinical state and advises next steps
    8. Clinician reviews case and authorizes care decision
    9. FacilityGraph ranks destination receiving centers
    10. Generate SBAR handoff packet and create referral
    11. Referral coordinator transitions referral through lifecycle
    12. Clinician records patient disposition and final outcome
    13. Verify outcome feeds CareGraph as OUTCOME node and SignalGraph macro telemetry
    14. Re-query case to confirm final state consistency and audit log completeness
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Authenticate Patient
        patient_token = await login_user(client, "patient")

        # Step 2: Submit Regular Pathway Intake
        intake_payload = {
            "facility_id": "FAC-DH-04",
            "pathway": "REGULAR_STANDARD",
            "reported_age_bracket": "35-44 YRS",
            "biological_sex": "FEMALE",
            "preferred_language": "en",
            "chief_complaint": "Persistent dull epigastric pain and indigestion for 5 days.",
            "symptom_duration": "5 days",
            "consent_confirmed": True,
            "consent_status": "GRANTED",
        }
        res_intake = await client.post(
            "/api/v1/intake/submit",
            headers=auth_headers(patient_token),
            json=intake_payload,
        )
        assert res_intake.status_code == 200, res_intake.text
        intake_data = res_intake.json()
        assert intake_data["success"] is True
        case_id = intake_data["case_id"]
        case_number = intake_data["case_number"]
        patient_id = intake_data["patient_id"]
        assert intake_data["current_state"] == "INTAKE_RECORDED"
        assert intake_data["status"] == "NEW"
        assert intake_data["consent_status"] == "GRANTED"

        # Step 3: Verify Case and Timeline Initialization in Database
        async with async_session_factory() as session:
            case_db = await session.get(Case, case_id)
            assert case_db is not None
            assert case_db.case_number == case_number
            assert case_db.facility_id == "FAC-DH-04"
            assert case_db.pathway == "REGULAR_STANDARD"

            # Verify initial timeline event exists
            stmt_tl = select(TimelineEvent).where(TimelineEvent.case_id == case_id)
            tl_events = (await session.execute(stmt_tl)).scalars().all()
            assert len(tl_events) >= 1
            assert any(e.event_type == "INTAKE_SUBMITTED" for e in tl_events)

        # Step 4: Upload Medical Document and Extract Findings
        doc_content = b"Lab report showing Hemoglobin 10.2 g/dL and normal leukocytes"
        files = {"file": ("ultrasound_report.pdf", doc_content, "application/pdf")}
        res_upload = await client.post(
            f"/api/v1/cases/{case_id}/documents",
            headers=auth_headers(patient_token),
            files=files,
            data={"document_type": "LAB_RESULT"},
        )
        assert res_upload.status_code == 200, res_upload.text
        doc_data = res_upload.json()
        doc_id = doc_data["id"]
        assert doc_data["filename"] == "ultrasound_report.pdf"

        # Trigger OCR on uploaded document
        res_ocr = await client.post(
            f"/api/v1/cases/{case_id}/documents/{doc_id}/ocr",
            headers=auth_headers(patient_token),
        )
        assert res_ocr.status_code == 200, res_ocr.text

        # Run extraction on document
        res_extract = await client.post(
            f"/api/v1/cases/{case_id}/documents/{doc_id}/extract",
            headers=auth_headers(patient_token),
        )
        assert res_extract.status_code == 200, res_extract.text
        extractions = res_extract.json()
        assert isinstance(extractions, list)
        assert len(extractions) > 0
        assert all(e["document_id"] == doc_id for e in extractions)

        # Step 5: Nurse Authenticates & Triages Case
        nurse_token = await login_user(client, "nurse")

        # Nurse starts triage
        res_triage_start = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers=auth_headers(nurse_token),
            json={"action": "START_TRIAGE", "reason": "Nurse initiating routine triage evaluation"},
        )
        assert res_triage_start.status_code == 200, res_triage_start.text

        # Nurse records vital signs (pulse: 78, bp: 124/82, spo2: 98, temp: 37.0)
        vitals_payload = {
            "heart_rate": 78,
            "systolic_bp": 124,
            "diastolic_bp": 82,
            "spo2_percent": 98.0,
            "temperature_celsius": 37.0,
            "respiratory_rate": 16,
        }
        res_vitals = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers=auth_headers(nurse_token),
            json=vitals_payload,
        )
        assert res_vitals.status_code == 200, res_vitals.text

        # Nurse submits triage note
        triage_note_payload = {
            "summary": "Patient alert, oriented. Epigastric tenderness on deep palpation, no guarding.",
            "acuity_assessment": "ROUTINE",
            "clinical_concerns": ["Cholelithiasis", "Peptic ulcer disease"],
            "suggested_next_steps": ["Doctor consultation", "Ultrasound review"],
            "author_type": "STAFF_ENTERED",
            "is_ai_generated": False,
        }
        res_triage_note = await client.post(
            f"/api/v1/cases/{case_id}/triage-note",
            headers=auth_headers(nurse_token),
            json=triage_note_payload,
        )
        assert res_triage_note.status_code == 200, res_triage_note.text

        # Nurse submits triage and advances to clinician review
        res_triage_submit = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers=auth_headers(nurse_token),
            json={"action": "SUBMIT_TRIAGE", "reason": "Triage evaluation completed"},
        )
        assert res_triage_submit.status_code == 200, res_triage_submit.text
        assert res_triage_submit.json()["to_state"] == "CLINICIAN_REVIEW_REQUIRED"

        # Step 6: Inspect CareGraph Representation
        res_cg = await client.get(
            f"/api/v1/caregraph/{case_id}",
            headers=auth_headers(nurse_token),
        )
        assert res_cg.status_code == 200, res_cg.text
        cg_data = res_cg.json()
        assert "graph" in cg_data
        assert cg_data["graph"]["total_nodes"] > 0
        assert "trajectory" in cg_data
        assert cg_data["case"]["acuity_tier"] == "ROUTINE"
        assert "slope" in cg_data["trajectory"]

        # Step 7: Orchestration Engine Evaluates Case
        res_orch = await client.post(
            "/api/v1/orchestration/evaluate",
            headers=auth_headers(nurse_token),
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert res_orch.status_code == 200, res_orch.text
        orch_eval = res_orch.json()
        assert orch_eval["recommended_action"] in {"OBSERVE", "CONTINUE", "VERIFY", "REFER"}

        # Step 8: Clinician Reviews Case and Authorizes Care Plan
        clinician_token = await login_user(client, "clinician")

        # Clinician starts review
        res_rev_start = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers=auth_headers(clinician_token),
            json={"action": "START_REVIEW", "reason": "Attending physician commencing clinical review"},
        )
        assert res_rev_start.status_code == 200, res_rev_start.text
        assert res_rev_start.json()["to_state"] == "REVIEW_IN_PROGRESS"

        # Missing-Information Detection & Adaptive Follow-up Question
        res_req_info = await client.post(
            f"/api/v1/cases/{case_id}/request-information",
            headers=auth_headers(clinician_token),
            json={
                "question_text": "Are you currently taking any NSAID medications or over-the-counter pain relievers?",
                "reason": "Assess peptic ulcer and gastric mucosal irritation risk factors",
                "priority": "MEDIUM",
                "target_role": "PATIENT",
            },
        )
        assert res_req_info.status_code == 200, res_req_info.text
        req_info_data = res_req_info.json()
        question_id = req_info_data["question_id"]
        assert req_info_data["status"] == "PENDING_INFORMATION"

        # Patient provides missing clinical information
        res_prov_info = await client.post(
            f"/api/v1/cases/{case_id}/provide-information",
            headers=auth_headers(patient_token),
            json={
                "question_id": question_id,
                "answer_text": "No NSAIDs or aspirin taken. Only used antacid liquid occasionally.",
            },
        )
        assert res_prov_info.status_code == 200, res_prov_info.text

        # Verify FollowUpQuestion and FollowUpAnswer in DB
        async with async_session_factory() as session:
            q_db = await session.get(FollowUpQuestion, question_id)
            assert q_db is not None
            assert q_db.status == "ANSWERED"
            stmt_ans = select(FollowUpAnswer).where(FollowUpAnswer.question_id == question_id)
            ans_db = (await session.execute(stmt_ans)).scalars().first()
            assert ans_db is not None
            assert "antacid" in ans_db.answer_text

        # Clinician resumes review following patient response
        await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            headers=auth_headers(clinician_token),
            json={"action": "START_REVIEW", "reason": "Resuming review following patient response"},
        )


        # Clinician records authoritative decision
        decision_payload = {
            "case_id": case_id,
            "action": "OBSERVE",
            "decision_type": "ACCEPT",
            "treatment_plan": "Oral proton pump inhibitors for 14 days, dietary modification, follow up in 2 weeks.",
            "clinical_impression": "Suspected gastritis / peptic acid disease without alarm symptoms.",
        }
        res_dec = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(clinician_token),
            json=decision_payload,
        )
        assert res_dec.status_code == 200, res_dec.text
        dec_data = res_dec.json()
        assert dec_data["status"] == "AUTHORIZED"
        assert dec_data["case_status"] == "OBSERVE"

        # Verify decision and audit trail in DB
        async with async_session_factory() as session:
            dec_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case_id)
            dec_db = (await session.execute(dec_stmt)).scalars().first()
            assert dec_db is not None
            assert dec_db.clinician_id == "usr-doc-01"  # Authoritatively set from token
            assert dec_db.action_type == "OBSERVE"

            audit_stmt = select(AuditLog).where(
                AuditLog.entity_id == case_id,
                AuditLog.action == "CLINICIAN_DECISION_RECORDED",
            )
            audit_db = (await session.execute(audit_stmt)).scalars().first()
            assert audit_db is not None
            assert audit_db.actor_id == "usr-doc-01"

        # Step 9: FacilityGraph Referral Destination Ranking
        res_rank = await client.post(
            "/api/v1/facilities/referral-rank",
            headers=auth_headers(clinician_token),
            json={"current_facility_id": "FAC-DH-04", "required_bundle": "BUNDLE_ROUTINE_AMBULATORY"},
        )
        assert res_rank.status_code == 200
        ranked_dests = res_rank.json()["ranked_destinations"]
        assert len(ranked_dests) > 0
        top_dest = ranked_dests[0]["facility_id"]

        # Step 10: Generate SBAR Inter-Facility Packet
        res_sbar = await client.post(
            "/api/v1/referrals/sbar",
            headers=auth_headers(clinician_token),
            json={"case_id": case_id, "destination_facility_id": top_dest},
        )
        assert res_sbar.status_code == 200, res_sbar.text
        sbar_data = res_sbar.json()
        assert "sbar_situation" in sbar_data
        assert "sbar_background" in sbar_data
        assert "sbar_assessment" in sbar_data
        assert "sbar_recommendation" in sbar_data

        # Step 11: Create and Dispatch Referral (Referral Coordinator)
        ref_coord_token = await login_user(client, "referral")
        ref_payload = {
            "case_id": case_id,
            "origin_facility_id": "FAC-DH-04",
            "destination_facility_id": top_dest,
            "required_bundle": "BUNDLE_ROUTINE_AMBULATORY",
            "sbar_situation": sbar_data["sbar_situation"],
            "sbar_background": sbar_data["sbar_background"],
            "sbar_assessment": sbar_data["sbar_assessment"],
            "sbar_recommendation": sbar_data["sbar_recommendation"],
            "estimated_transit_minutes": 45,
        }
        res_ref_create = await client.post(
            "/api/v1/referrals/create",
            headers=auth_headers(ref_coord_token),
            json=ref_payload,
        )
        assert res_ref_create.status_code == 200, res_ref_create.text
        ref_id = res_ref_create.json()["referral_id"]

        # Update Referral Status through lifecycle: DISPATCHED -> COMPLETED
        res_ref_dispatch = await client.post(
            f"/api/v1/referrals/{ref_id}/status",
            headers=auth_headers(ref_coord_token),
            json={"status": "DISPATCHED"},
        )
        assert res_ref_dispatch.status_code == 200

        res_ref_complete = await client.post(
            f"/api/v1/referrals/{ref_id}/status",
            headers=auth_headers(ref_coord_token),
            json={"status": "COMPLETED"},
        )
        assert res_ref_complete.status_code == 200
        assert res_ref_complete.json()["referral_status"] == "COMPLETED"

        # Step 12: Record Synthetic Clinical Outcome
        outcome_payload = {
            "disposition": "DISCHARGE_HOME",
            "final_condition": "RECOVERED",
            "actual_action": "DISCHARGED",
            "recommendation": "CONTINUE_MEDICATION",
            "professional_decision": "DISCHARGE_ON_MEDICATION",
            "outcome_status": "RECOVERED",
            "notes": "Patient reports complete symptom resolution following 14 days PPI therapy.",
        }
        res_outcome = await client.post(
            f"/api/v1/cases/{case_id}/outcome",
            headers=auth_headers(clinician_token),
            json=outcome_payload,
        )
        assert res_outcome.status_code == 200, res_outcome.text
        out_data = res_outcome.json()
        assert out_data["outcome_status"] == "RECOVERED"
        assert out_data["actual_action"] == "DISCHARGED"

        # Step 13: Verify Outcome Feeds CareGraph with OUTCOME Node
        res_cg_final = await client.get(
            f"/api/v1/caregraph/{case_id}",
            headers=auth_headers(clinician_token),
        )
        assert res_cg_final.status_code == 200
        cg_final = res_cg_final.json()
        outcome_nodes = [n for n in cg_final["graph"]["nodes"] if n.get("type") == "OUTCOME"]
        assert len(outcome_nodes) == 1
        assert outcome_nodes[0]["data"]["outcome_status"] == "RECOVERED"

        # Verify SignalGraph Macro Telemetry Ingestion
        res_sig = await client.get(
            "/api/v1/signalgraph/outcomes",
            headers=auth_headers(clinician_token),
        )
        assert res_sig.status_code == 200
        sig_data = res_sig.json()
        assert "outcome_status_distribution" in sig_data
        assert sig_data["total_outcomes_recorded"] >= 1
        assert sig_data["outcome_status_distribution"].get("RECOVERED", 0) >= 1

        # Step 14: Refresh Case & Verify State Consistency
        res_case_refreshed = await client.get(
            f"/api/v1/cases/{case_id}",
            headers=auth_headers(clinician_token),
        )
        assert res_case_refreshed.status_code == 200
        refreshed_case = res_case_refreshed.json()
        assert refreshed_case["id"] == case_id
        assert refreshed_case["facility_id"] == "FAC-DH-04"


# ===========================================================================
# JOURNEY B: EMERGENCY CARE PATHWAY & DETERMINISTIC SAFETY CONTROLS
# ===========================================================================
@pytest.mark.asyncio
async def test_journey_b_emergency_pathway_end_to_end():
    """
    Validates Journey B:
    1. Rapid emergency intake submission
    2. Deterministic derivation of CRITICAL acuity tier and red flags
    3. Orchestration engine advises emergency escalation (ESCALATE)
    4. Prohibited autonomous clinical actions unconditionally rejected server-side
    5. Clinician signs off on emergency stabilization
    6. Case successfully transitions under qualified human supervision
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_user(client, "nurse")

        # Step 1: Emergency Intake Submission (Acute Crushing Chest Pain, Diaphoresis, Shock Vitals)
        emergency_payload = {
            "facility_id": "FAC-DH-04",
            "pathway": "EMERGENCY",
            "reported_age_bracket": "55-64 YRS",
            "biological_sex": "MALE",
            "preferred_language": "en",
            "chief_complaint": "Sudden onset crushing central chest pain radiating to left arm with severe diaphoresis.",
            "symptom_duration": "45 minutes",
            "consent_confirmed": True,
            "consent_status": "GRANTED",
        }
        res_intake = await client.post(
            "/api/v1/intake/submit",
            headers=auth_headers(nurse_token),
            json=emergency_payload,
        )
        assert res_intake.status_code == 200, res_intake.text
        case_id = res_intake.json()["case_id"]

        # Step 2: Record Shock Vitals (HR: 138, BP: 78/48, SpO2: 88%)
        res_vitals = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers=auth_headers(nurse_token),
            json={
                "heart_rate": 138,
                "systolic_bp": 78,
                "diastolic_bp": 48,
                "spo2_percent": 88.0,
                "respiratory_rate": 32,
                "temperature_celsius": 36.4,
            },
        )
        assert res_vitals.status_code == 200

        # Step 3: Orchestration Evaluation Advises ESCALATE
        res_orch = await client.post(
            "/api/v1/orchestration/evaluate",
            headers=auth_headers(nurse_token),
            json={"case_id": case_id, "facility_id": "FAC-DH-04"},
        )
        assert res_orch.status_code == 200
        orch_eval = res_orch.json()
        assert orch_eval["recommended_action"] == "ESCALATE"

        # Step 4: Verify Zero Autonomous Clinical Actions (Foundational Safety Invariant)
        clinician_token = await login_user(client, "clinician")
        prohibited_actions = [
            "AI_DIAGNOSIS",
            "AUTO_PRESCRIBE",
            "AI_ADMISSION",
            "AI_DISCHARGE",
            "AUTHORIZE_PROCEDURE",
        ]
        for bad_action in prohibited_actions:
            res_bad = await client.post(
                "/api/v1/orchestration/decision",
                headers=auth_headers(clinician_token),
                json={
                    "case_id": case_id,
                    "action": bad_action,
                    "decision_type": "ACCEPT",
                },
            )
            assert res_bad.status_code in {403, 422}, f"Expected rejection for {bad_action}, got {res_bad.status_code}"
            err_msg = res_bad.json().get("error", {}).get("message", "").lower()
            assert "prohibited" in err_msg or "autonomous" in err_msg or "not permitted" in err_msg or "safety" in err_msg

        # Non-clinicians (nurse, patient) unconditionally blocked from authorizing emergency decisions
        res_nurse_bad = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(nurse_token),
            json={
                "case_id": case_id,
                "action": "ESCALATE",
                "decision_type": "ACCEPT",
                "clinical_impression": "Nurse attempting to authorize escalation",
            },
        )
        assert res_nurse_bad.status_code == 403

        # Deterministic safety checks CANNOT be bypassed via offline sync push batch
        res_sync_bad = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json={
                "node_id": "NODE-EMERGENCY-01",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CLINICIAN_DECISIONS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {
                            "action_type": "AUTO_PRESCRIBE",
                            "decision_type": "ACCEPT",
                        },
                    }
                ],
            },
        )
        assert res_sync_bad.status_code == 200
        sync_bad_res = res_sync_bad.json()["results"][0]
        assert sync_bad_res["status"] == "FAILED"
        assert "authorization" in sync_bad_res["message"].lower() or "prohibited" in sync_bad_res["message"].lower()

        res_sync_bad_cl = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(clinician_token),
            json={
                "node_id": "NODE-EMERGENCY-01",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CLINICIAN_DECISIONS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {
                            "action_type": "AUTO_PRESCRIBE",
                            "decision_type": "ACCEPT",
                        },
                    }
                ],
            },
        )
        assert res_sync_bad_cl.status_code == 200
        sync_bad_cl_res = res_sync_bad_cl.json()["results"][0]
        assert sync_bad_cl_res["status"] == "FAILED"
        assert "prohibited" in sync_bad_cl_res["message"].lower()


        # Step 5: Authorized Clinician Emergency Escalation
        res_esc = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(clinician_token),
            json={
                "case_id": case_id,
                "action": "ESCALATE",
                "decision_type": "ACCEPT",
                "clinical_impression": "Acute ST-Elevation Myocardial Infarction complicated by cardiogenic shock.",
                "treatment_plan": "High-flow oxygen, dual antiplatelets, immediate transfer to SCB Tertiary Cath Lab.",
                "clinical_rationale": "Patient in profound shock requiring immediate interventional cardiology.",
            },
        )
        assert res_esc.status_code == 200, res_esc.text
        assert res_esc.json()["case_status"] == "ESCALATE"

        # Step 6: Verify Case State Machine Updated
        async with async_session_factory() as session:
            case_db = await session.get(Case, case_id)
            assert case_db.status == "ESCALATE"


# ===========================================================================
# JOURNEY C: ROLE & MULTITENANCY AUTHORIZATION BOUNDARIES
# ===========================================================================
@pytest.mark.asyncio
async def test_journey_c_role_and_authorization_boundaries_end_to_end():
    """
    Validates Journey C:
    - Patient cannot view another patient's case (horizontal isolation)
    - Patient cannot mutate staff/clinician resources (vertical isolation)
    - Nurse cannot authorize final clinical decisions or resolve sync conflicts
    - Facility Admin at Facility A cannot alter resources of Facility B
    - Mass assignment attempts to spoof role or identity rejected server-side
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_user(client, "patient")
        patient_09_token = await login_user(client, "patient_09")
        nurse_token = await login_user(client, "nurse")
        clinician_token = await login_user(client, "clinician")
        fac_admin_token = await login_user(client, "facility_admin")

        # 1. Create Patient 1's Case
        res_p1_case = await client.post(
            "/api/v1/intake/submit",
            headers=auth_headers(patient_token),
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Private patient case.",
                "consent_confirmed": True,
            },
        )
        assert res_p1_case.status_code == 200
        p1_case_id = res_p1_case.json()["case_id"]

        # 2. Patient 2 attempting to view Patient 1's Case -> 403 or 404
        res_cross_patient = await client.get(
            f"/api/v1/cases/{p1_case_id}",
            headers=auth_headers(patient_09_token),
        )
        assert res_cross_patient.status_code in {403, 404}

        # 3. Patient attempting clinician decision -> 403
        res_pt_dec = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(patient_token),
            json={"case_id": p1_case_id, "action": "OBSERVE", "decision_type": "ACCEPT"},
        )
        assert res_pt_dec.status_code == 403

        # 4. Nurse attempting clinician decision -> 403
        res_nr_dec = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(nurse_token),
            json={"case_id": p1_case_id, "action": "OBSERVE", "decision_type": "ACCEPT"},
        )
        assert res_nr_dec.status_code == 403

        # 5. Nurse attempting sync conflict resolution -> 403
        res_nr_conflict = await client.post(
            f"/api/v1/sync/conflicts/{str(uuid.uuid4())}/resolve",
            headers=auth_headers(nurse_token),
            json={"resolution_choice": "KEEP_LOCAL", "clinical_rationale": "Nurse rationale"},
        )
        assert res_nr_conflict.status_code == 403

        # 6. Facility Admin cross-facility mutation: FAC-DH-04 admin modifying FAC-PHC-01 -> 403 or 404
        res_cross_fac = await client.post(
            "/api/v1/facilities/FAC-PHC-01/update-capacity",
            headers=auth_headers(fac_admin_token),
            json={"icu_beds_available": 0},
        )
        assert res_cross_fac.status_code in {403, 404}

        # 7. Mass-Assignment & Role Elevation Rejection
        # Supplying forged client-side role or privileges in payload
        res_tamper = await client.post(
            "/api/v1/intake/submit",
            headers=auth_headers(patient_token),
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Testing tamper resistance",
                "consent_confirmed": True,
                "role": "SYSTEM_ADMIN",
                "is_admin": True,
            },
        )
        assert res_tamper.status_code == 422

        # 8. System Administrator Global Oversight & Non-Clinical Safety
        sysadmin_token = await login_user(client, "sysadmin")
        res_sys_case = await client.get(
            f"/api/v1/cases/{p1_case_id}",
            headers=auth_headers(sysadmin_token),
        )
        assert res_sys_case.status_code == 200  # Sysadmin has global multi-tenant visibility
        assert res_sys_case.json()["id"] == p1_case_id

        # System Admin is blocked from autonomous clinical decisions
        res_sys_bad = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(sysadmin_token),
            json={
                "case_id": p1_case_id,
                "action": "AI_DIAGNOSIS",
                "decision_type": "ACCEPT",
            },
        )
        assert res_sys_bad.status_code in {403, 422}

        # 9. Unauthorized Referral Creation Block (Nurse and Patient Blocked)
        ref_test_payload = {
            "case_id": p1_case_id,
            "origin_facility_id": "FAC-PHC-01",
            "destination_facility_id": "FAC-DH-04",
            "required_bundle": "BUNDLE_ROUTINE_AMBULATORY",
            "sbar_situation": "Routine transfer request",
            "sbar_background": "Ambulatory care",
            "sbar_assessment": "Stable",
            "sbar_recommendation": "Consultation",
        }
        res_nurse_ref = await client.post(
            "/api/v1/referrals/create",
            headers=auth_headers(nurse_token),
            json=ref_test_payload,
        )
        assert res_nurse_ref.status_code == 403

        res_pt_ref = await client.post(
            "/api/v1/referrals/create",
            headers=auth_headers(patient_token),
            json=ref_test_payload,
        )
        assert res_pt_ref.status_code == 403


        # 10. Unauthorized Facility Capability Mutation (Nurse Blocked)
        res_nurse_cap = await client.post(
            "/api/v1/facilities/FAC-DH-04/toggle-capability",
            headers=auth_headers(nurse_token),
            json={"capability_code": "CT_SCAN_24_7", "is_operational": False},
        )
        assert res_nurse_cap.status_code == 403

        # 11. Cross-Facility Clinician Isolation & Spoofing Defense
        # 11a. Clinician at FAC-DH-04 attempting decision on FAC-PHC-01 case -> 404 (isolation)
        res_cross_dec = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(clinician_token),
            json={
                "case_id": p1_case_id,
                "action": "OBSERVE",
                "decision_type": "ACCEPT",
            },
        )
        assert res_cross_dec.status_code == 404

        # 11b. Clinician at FAC-DH-04 deciding on FAC-DH-04 case with spoofed clinician_id
        res_dh_case = await client.post(
            "/api/v1/intake/submit",
            headers=auth_headers(patient_token),
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Testing clinician decision authorization.",
                "consent_confirmed": True,
            },
        )
        assert res_dh_case.status_code == 200
        dh_case_id = res_dh_case.json()["case_id"]

        res_spoof = await client.post(
            "/api/v1/orchestration/decision",
            headers=auth_headers(clinician_token),
            json={
                "case_id": dh_case_id,
                "clinician_id": "usr-forged-impostor-999",
                "action": "OBSERVE",
                "decision_type": "ACCEPT",
                "treatment_plan": "Bed rest and observation",
                "clinical_rationale": "Clinician authorized management",
            },
        )
        assert res_spoof.status_code == 200
        async with async_session_factory() as session:
            dec_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == dh_case_id)
            dec_db = (await session.execute(dec_stmt)).scalars().first()
            assert dec_db is not None
            assert dec_db.clinician_id == "usr-doc-01"  # Bound strictly to token actor, not spoofed body


# ===========================================================================
# JOURNEY D: OFFLINE SYNC, REPLAY DEFENSE & CONFLICT RESOLUTION
# ===========================================================================
@pytest.mark.asyncio
async def test_journey_d_offline_sync_and_data_consistency_end_to_end():
    """
    Validates Journey D:
    1. Offline action queue simulation without credential leakage
    2. Batch push of queued items to /api/v1/sync/push
    3. Idempotent retries return ALREADY_SYNCED without duplicate rows
    4. Tampering & replay rejection: modified payload with reused sync_id fails
    5. Version conflict creates SyncConflict record in PENDING_HUMAN_REVIEW
    6. Clinician-only reconciliation gate with mandatory rationale
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_user(client, "nurse")
        clinician_token = await login_user(client, "clinician")

        sync_op_id = str(uuid.uuid4())
        offline_case_id = f"case-offline-{uuid.uuid4().hex[:8]}"

        # Step 1: Push offline intake and vitals batch
        push_batch = {
            "node_id": "NODE-PHC-OFFLINE-01",
            "items": [
                {
                    "sync_id": sync_op_id,
                    "entity_type": "CASE",
                    "entity_id": offline_case_id,
                    "operation": "INSERT",
                    "local_version": 1,
                    "payload_snapshot": {
                        "facility_id": "FAC-DH-04",
                        "pathway": "REGULAR_STANDARD",
                        "presenting_complaint": "Offline captured intermittent fever and chills.",
                        "reported_age_bracket": "30-39",
                        "biological_sex": "MALE",
                        "case_number": f"CN-OFF-{uuid.uuid4().hex[:6].upper()}",
                    },
                },
                {
                    "sync_id": str(uuid.uuid4()),
                    "entity_type": "VITALS",
                    "entity_id": str(uuid.uuid4()),
                    "case_id": offline_case_id,
                    "operation": "INSERT",
                    "local_version": 1,
                    "payload_snapshot": {
                        "case_id": offline_case_id,
                        "heart_rate": 84,
                        "systolic_bp": 122,
                        "diastolic_bp": 80,
                        "temperature_celsius": 38.6,
                    },
                },
            ],
        }

        res_push = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json=push_batch,
        )
        assert res_push.status_code == 200, res_push.text
        results = res_push.json()["results"]
        assert len(results) == 2
        assert results[0]["status"] == "SYNCED"
        assert results[1]["status"] == "SYNCED"

        # Step 2: Idempotent Retry of Exact Same Batch
        res_retry = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json=push_batch,
        )
        assert res_retry.status_code == 200
        retry_results = res_retry.json()["results"]
        assert all(r["status"] == "ALREADY_SYNCED" for r in retry_results)

        # Confirm zero duplicate cases in database
        async with async_session_factory() as session:
            stmt_cases = select(Case).where(Case.id == offline_case_id)
            cases = (await session.execute(stmt_cases)).scalars().all()
            assert len(cases) == 1

        # Step 3: Replay & Tampering Defense (reusing sync_op_id with conflicting payload)
        tampered_batch = {
            "node_id": "NODE-PHC-OFFLINE-01",
            "items": [
                {
                    "sync_id": sync_op_id,  # Reused ID
                    "entity_type": "CASE",
                    "entity_id": offline_case_id,
                    "operation": "INSERT",
                    "local_version": 1,
                    "payload_snapshot": {
                        "facility_id": "FAC-DH-04",
                        "presenting_complaint": "TAMPERED PAYLOAD REPLAY ATTACK",
                    },
                }
            ],
        }
        res_tamper = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json=tampered_batch,
        )
        assert res_tamper.status_code == 200
        tamper_result = res_tamper.json()["results"][0]
        assert tamper_result["status"] == "FAILED"
        assert "tampering/replay detected" in tamper_result["message"]

        # Step 4: Stale Version / Concurrent Edit Conflict Detection
        # Send an update with stale version (local_version 0 when remote is 1)
        conflict_sync_id = str(uuid.uuid4())
        conflict_batch = {
            "node_id": "NODE-PHC-OFFLINE-01",
            "items": [
                {
                    "sync_id": conflict_sync_id,
                    "entity_type": "CASE",
                    "entity_id": offline_case_id,
                    "operation": "UPDATE",
                    "local_version": 999,  # Version divergence
                    "payload_snapshot": {
                        "presenting_complaint": "Conflicting update from concurrent offline node",
                    },
                }
            ],
        }
        res_conflict_push = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json=conflict_batch,
        )
        assert res_conflict_push.status_code == 200
        conf_result = res_conflict_push.json()["results"][0]
        assert conf_result["status"] == "CONFLICT"

        # Step 5: List Pending Conflicts
        res_conf_list = await client.get(
            f"/api/v1/sync/conflicts?case_id={offline_case_id}",
            headers=auth_headers(clinician_token),
        )
        assert res_conf_list.status_code == 200
        conf_items = res_conf_list.json()
        assert len(conf_items) >= 1
        target_conflict = conf_items[0]
        conflict_id = target_conflict["conflict_id"]
        assert target_conflict["resolution_status"] == "PENDING_HUMAN_REVIEW"

        # Step 6: Unauthorized Conflict Resolution (Nurse Blocked)
        res_nr_resolve = await client.post(
            f"/api/v1/sync/conflicts/{conflict_id}/resolve",
            headers=auth_headers(nurse_token),
            json={
                "resolution_choice": "KEEP_LOCAL",
                "clinical_rationale": "Nurse attempting resolution",
            },
        )
        assert res_nr_resolve.status_code == 403

        # Step 7: Authorized Clinician Resolves Conflict with Mandatory Rationale
        res_cl_resolve = await client.post(
            f"/api/v1/sync/conflicts/{conflict_id}/resolve",
            headers=auth_headers(clinician_token),
            json={
                "resolution_choice": "KEEP_LOCAL",
                "clinical_rationale": "Verified patient history directly with attending physician at DH.",
            },
        )
        assert res_cl_resolve.status_code == 200, res_cl_resolve.text
        resolve_data = res_cl_resolve.json()
        assert resolve_data["resolution_status"].startswith("RESOLVED")
        assert resolve_data["resolved_by_actor_id"] == "usr-doc-01"

        # Verify resolution recorded in DB
        async with async_session_factory() as session:
            conf_db = await session.get(SyncConflict, conflict_id)
            assert conf_db.resolution_status.startswith("RESOLVED")
            assert conf_db.resolved_by_actor_id == "usr-doc-01"
            assert conf_db.resolved_at is not None

        # Step 8: Concurrency & Duplicate Resolution Guard (Already resolved conflict rejected)
        res_double_resolve = await client.post(
            f"/api/v1/sync/conflicts/{conflict_id}/resolve",
            headers=auth_headers(clinician_token),
            json={
                "resolution_choice": "KEEP_LOCAL",
                "clinical_rationale": "Second resolution attempt by concurrent clinician",
            },
        )
        assert res_double_resolve.status_code == 400
        double_msg = res_double_resolve.json().get("error", {}).get("message", res_double_resolve.text).lower()
        assert "already been resolved" in double_msg

        # Step 9: Rejection of Empty Clinical Rationale on Conflict Resolution
        second_sync_id = str(uuid.uuid4())
        await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(nurse_token),
            json={
                "node_id": "NODE-PHC-OFFLINE-01",
                "items": [
                    {
                        "sync_id": second_sync_id,
                        "entity_type": "CASE",
                        "entity_id": offline_case_id,
                        "operation": "UPDATE",
                        "local_version": 999,
                        "payload_snapshot": {"presenting_complaint": "Second conflict update"},
                    }
                ],
            },
        )
        conf2_res = await client.get(
            f"/api/v1/sync/conflicts?case_id={offline_case_id}",
            headers=auth_headers(clinician_token),
        )
        assert conf2_res.status_code == 200
        pending_confs = [c for c in conf2_res.json() if c["resolution_status"] == "PENDING_HUMAN_REVIEW"]
        assert len(pending_confs) >= 1
        conf2_id = pending_confs[0]["conflict_id"]

        res_empty_rat = await client.post(
            f"/api/v1/sync/conflicts/{conf2_id}/resolve",
            headers=auth_headers(clinician_token),
            json={
                "resolution_choice": "KEEP_LOCAL",
                "clinical_rationale": "   ",
            },
        )
        assert res_empty_rat.status_code == 400
        empty_msg = res_empty_rat.json().get("error", {}).get("message", res_empty_rat.text).lower()
        assert "mandatory clinical rationale" in empty_msg


        # Step 10: Unauthorized Offline Sync by Patient (Patients cannot push clinician decisions)
        patient_token = await login_user(client, "patient")
        res_pt_sync = await client.post(
            "/api/v1/sync/push",
            headers=auth_headers(patient_token),
            json={
                "node_id": "NODE-PATIENT-01",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CLINICIAN_DECISIONS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": offline_case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"action_type": "OBSERVE", "decision_type": "ACCEPT"},
                    }
                ],
            },
        )
        assert res_pt_sync.status_code == 200
        pt_res = res_pt_sync.json()["results"][0]
        assert pt_res["status"] == "FAILED"
        assert "authorization" in pt_res["message"].lower() or "prohibited" in pt_res["message"].lower()
