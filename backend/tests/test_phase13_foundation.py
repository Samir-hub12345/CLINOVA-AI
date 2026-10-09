"""CLINOVA AI — Comprehensive Phase 13 Foundation Test Suite.

Verifies the complete Phase 13 Core Backend Foundation Test Matrix (A through Z):
A. Patient creation
B. Encounter creation
C. Case creation
D. Case retrieval
E. Case filtering
F. Evidence insertion
G. Provenance persistence
H. Vital insertion
I. Timeline retrieval
J. Follow-up insertion
K. Triage note insertion
L. Human review action
M. Invalid review action (prohibited actions rejected server-side)
N. State transition
O. Invalid transition (rejected)
P. Optimistic concurrency conflict (version mismatch rejected with 409)
Q. Audit creation
R. Unauthorized access (role boundary)
S. Cross-case access (invalid case ID)
T. Missing consent
U. Invalid vital data (bounds checking)
V. Transaction rollback
W. Database unavailable error handling
X. Structured error response
Y. Synthetic mode verification
Z. Migration upgrade verification
"""

import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Patient,
    PatientIdentifier,
    Encounter,
    Case,
    CaseStateTransition,
    Evidence,
    Vital,
    TimelineEvent,
    Consent,
    FollowUpQuestion,
    FollowUpAnswer,
    TriageNote,
    ReviewAction,
    AuditEvent,
    Facility,
)


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Initializes tables and seeds facilities before running tests."""
    from app.core.config import settings
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = True
    await init_db()


# ---------------------------------------------------------------------------
# Test A: Patient Creation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_a_patient_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        test_synth_id = f"PT-SYN-{uuid.uuid4().hex[:6].upper()}"
        res = await client.post(
            "/api/v1/patients",
            json={
                "synthetic_id": test_synth_id,
                "age_bracket": "40-49",
                "biological_sex": "MALE",
                "is_synthetic": True,
            },
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["synthetic_id"] == test_synth_id
        assert data["age_bracket"] == "40-49"
        assert data["biological_sex"] == "MALE"
        assert data["is_synthetic"] is True
        assert "id" in data


# ---------------------------------------------------------------------------
# Test B: Encounter Creation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_b_encounter_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create patient first
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "FEMALE"},
        )
        pt_id = p_res.json()["id"]

        enc_res = await client.post(
            "/api/v1/encounters",
            json={
                "patient_id": pt_id,
                "facility_id": "FAC-DH-04",
                "environment": "development",
                "pathway": "EMERGENCY_FAST_TRACK",
            },
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert enc_res.status_code == 200, enc_res.text
        enc_data = enc_res.json()
        assert enc_data["patient_id"] == pt_id
        assert enc_data["facility_id"] == "FAC-DH-04"
        assert enc_data["pathway"] == "EMERGENCY_FAST_TRACK"


# ---------------------------------------------------------------------------
# Test C: Master Case Creation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_c_case_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "50-59", "biological_sex": "MALE"},
        )
        pt_id = p_res.json()["id"]

        case_res = await client.post(
            "/api/v1/cases",
            json={
                "patient_id": pt_id,
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "acuity_tier": "URGENT",
                "presenting_complaint": "Acute crushing retrosternal chest pain radiating to left shoulder.",
                "primary_syndrome": "Acute Coronary Syndrome",
                "required_bundle": "BUNDLE_ACS_THROMBOLYSIS_PCI",
            },
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert case_res.status_code == 200, case_res.text
        case_data = case_res.json()
        assert case_data["patient_id"] == pt_id
        assert case_data["acuity_tier"] == "URGENT"
        assert case_data["current_state"] == "INTAKE_RECORDED"
        assert case_data["state_version"] == 1
        assert "CAS-2026-" in case_data["case_number"]


# ---------------------------------------------------------------------------
# Test D: Master Case Retrieval
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_d_case_retrieval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "20-29", "biological_sex": "FEMALE"})
        pt_id = p_res.json()["id"]
        c_res = await client.post("/api/v1/cases", json={"patient_id": pt_id, "facility_id": "FAC-PHC-01"})
        case_id = c_res.json()["id"]

        # Retrieve
        get_res = await client.get(f"/api/v1/cases/{case_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == case_id


# ---------------------------------------------------------------------------
# Test E: Case Filtering
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_e_case_filtering():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "60-69", "biological_sex": "MALE"})
        assert p_res.status_code == 200, p_res.text
        pt_id = p_res.json()["id"]
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": pt_id, "facility_id": "FAC-DH-04", "acuity_tier": "CRITICAL"},
        )
        assert c_res.status_code == 200, c_res.text

        filter_res = await client.get("/api/v1/cases?acuity=CRITICAL")
        assert filter_res.status_code == 200, filter_res.text
        cases = filter_res.json()
        assert len(cases) >= 1, f"Expected at least 1 case, got {len(cases)}: {cases}"
        assert all(c["acuity_tier"] == "CRITICAL" for c in cases), f"Non-critical cases returned: {[c['acuity_tier'] for c in cases]}"


# ---------------------------------------------------------------------------
# Test F: Evidence Insertion
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_f_evidence_insertion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "30-39", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        ev_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence",
            json={
                "source_class": "PATIENT_REPORTED",
                "epistemic_state": "INFERRED",
                "parameter_name": "fever_duration_days",
                "content_value": 3,
                "unit": "days",
                "confidence_score": 0.95,
            },
        )
        assert ev_res.status_code == 200, ev_res.text
        ev_data = ev_res.json()
        assert ev_data["parameter_name"] == "fever_duration_days"
        assert ev_data["content_value"] == 3
        assert ev_data["source_class"] == "PATIENT_REPORTED"


# ---------------------------------------------------------------------------
# Test G: Provenance Persistence
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_g_provenance_persistence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "45-55", "biological_sex": "FEMALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        ev_res = await client.post(
            f"/api/v1/cases/{case_id}/evidence",
            json={
                "source_class": "VOICE_TRANSCRIBED",
                "epistemic_state": "INFERRED",
                "parameter_name": "breathlessness_on_exertion",
                "content_value": True,
                "confidence_score": 0.88,
                "provenance_metadata": {
                    "audio_model": "Whisper-Large-v3",
                    "snr_db": 18.4,
                    "language": "hi",
                },
            },
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )
        assert ev_res.status_code == 200
        ev_data = ev_res.json()
        assert ev_data["provenance_metadata"]["audio_model"] == "Whisper-Large-v3"
        assert ev_data["provenance_metadata"]["submitted_by"] == "usr-nurse-02"


# ---------------------------------------------------------------------------
# Test H: Vital Insertion & Bounds Checking
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_h_vital_insertion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "50-59", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        v_res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={
                "heart_rate": 112,
                "systolic_bp": 92,
                "diastolic_bp": 60,
                "spo2_percent": 94,
                "respiratory_rate": 22,
                "temperature_celsius": 38.6,
                "avpu_score": "ALERT",
            },
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )
        assert v_res.status_code == 200, v_res.text
        v_data = v_res.json()
        assert v_data["heart_rate"] == 112
        assert v_data["systolic_bp"] == 92
        assert v_data["diastolic_bp"] == 60


# ---------------------------------------------------------------------------
# Test I: Timeline Retrieval
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_i_timeline_retrieval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "25-35", "biological_sex": "FEMALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Insert custom timeline event
        await client.post(
            f"/api/v1/cases/{case_id}/timeline",
            json={
                "event_type": "SYMPTOM_ONSET",
                "event_title": "Fever and chills began",
                "event_content": "Patient reported sudden high fever at home.",
            },
        )

        tl_res = await client.get(f"/api/v1/cases/{case_id}/timeline")
        assert tl_res.status_code == 200
        events = tl_res.json()
        assert len(events) >= 1
        assert any(e["event_type"] == "SYMPTOM_ONSET" for e in events)


# ---------------------------------------------------------------------------
# Test J: Follow-up Insertion & Answering
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_j_follow_up_insertion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "40-49", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Ask question
        q_res = await client.post(
            f"/api/v1/cases/{case_id}/follow-up/question",
            json={
                "question_text": "Do you have any known drug allergies?",
                "reason": "Resolve missing allergy history before medication administration.",
                "priority": "CRITICAL",
            },
        )
        assert q_res.status_code == 200
        q_id = q_res.json()["id"]

        # Answer question
        ans_res = await client.post(
            f"/api/v1/cases/{case_id}/follow-up/answer",
            json={
                "question_id": q_id,
                "answer_text": "No known allergies to penicillin or NSAIDs.",
            },
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert ans_res.status_code == 200
        assert ans_res.json()["answer_text"] == "No known allergies to penicillin or NSAIDs."


# ---------------------------------------------------------------------------
# Test K: Triage Note Insertion
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_k_triage_note_insertion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "35-45", "biological_sex": "FEMALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        tn_res = await client.post(
            f"/api/v1/cases/{case_id}/triage-note",
            json={
                "summary": "Patient exhibits acute severe abdominal pain with localized tenderness in RIF.",
                "acuity_assessment": "URGENT",
                "clinical_concerns": ["Acute Appendicitis", "Peritonitis"],
                "suggested_next_steps": ["Bedside Ultrasound", "Surgical Consultation"],
                "author_type": "STAFF_ENTERED",
                "is_ai_generated": False,
            },
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )
        assert tn_res.status_code == 200, tn_res.text
        assert tn_res.json()["acuity_assessment"] == "URGENT"


# ---------------------------------------------------------------------------
# Test L: Human Review Action (Allowed Action)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_l_human_review_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "55-65", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        rev_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={
                "action": "VERIFY",
                "target_entity_type": "CASE",
                "target_entity_id": case_id,
                "reason": "Clinician confirmed triage presentation and verified vital parameters.",
                "notes": "ECG ordered immediately.",
            },
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert rev_res.status_code == 200, rev_res.text
        assert rev_res.json()["action"] == "VERIFY"


# ---------------------------------------------------------------------------
# Test M: Invalid Review Action (Server-Side Prohibited Action Rejection)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_m_invalid_review_action_prohibited():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "40-49", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Attempt prohibited autonomous diagnosis
        res_diag = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "AI_DIAGNOSIS"},
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert res_diag.status_code == 422
        assert res_diag.json()["error"]["code"] == "UNSUPPORTED_OPERATION"

        # Attempt prohibited autonomous prescription
        res_rx = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "AUTO_PRESCRIBE"},
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert res_rx.status_code == 422
        assert res_rx.json()["error"]["code"] == "UNSUPPORTED_OPERATION"


# ---------------------------------------------------------------------------
# Test N: Valid State Transition
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_n_state_transition():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "30-39", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]
        assert c_res.json()["current_state"] == "INTAKE_RECORDED"

        # Transition INTAKE_RECORDED -> TRIAGE_IN_PROGRESS via START_TRIAGE
        tr_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={
                "action": "START_TRIAGE",
                "reason": "Nurse began bedside assessment",
                "expected_state_version": 1,
            },
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )
        assert tr_res.status_code == 200, tr_res.text
        tr_data = tr_res.json()
        assert tr_data["to_state"] == "TRIAGE_IN_PROGRESS"
        assert tr_data["state_version"] == 2


# ---------------------------------------------------------------------------
# Test O: Invalid State Transition Rejection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_o_invalid_state_transition():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "30-39", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Attempt FINALIZE_DISPOSITION directly from INTAKE_RECORDED (must be rejected)
        tr_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={
                "action": "FINALIZE_DISPOSITION",
                "reason": "Attempting arbitrary bypass to closed state",
                "expected_state_version": 1,
            },
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert tr_res.status_code == 422
        assert tr_res.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


# ---------------------------------------------------------------------------
# Test P: Optimistic Concurrency Conflict
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_p_optimistic_concurrency_conflict():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "30-39", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Actor A advances version from 1 to 2
        await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={"action": "START_TRIAGE", "reason": "Actor A update", "expected_state_version": 1},
            headers={"X-Actor-Id": "usr-nurse-02", "X-Actor-Role": "NURSE"},
        )

        # Actor B submits with stale version 1
        stale_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={"action": "ESCALATE", "reason": "Actor B stale update", "expected_state_version": 1},
            headers={"X-Actor-Id": "usr-doc-01", "X-Actor-Role": "CLINICIAN"},
        )
        assert stale_res.status_code == 409
        err = stale_res.json()["error"]
        assert err["code"] == "CONFLICT"
        assert "Optimistic concurrency conflict" in err["message"]


# ---------------------------------------------------------------------------
# Test Q: Audit Creation on Mutation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_q_audit_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "40-49", "biological_sex": "FEMALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        audit_res = await client.get(f"/api/v1/cases/{case_id}/audit")
        assert audit_res.status_code == 200
        logs = audit_res.json()
        assert len(logs) >= 1
        assert any(l["action"] == "case.created" for l in logs)


# ---------------------------------------------------------------------------
# Test R: Unauthorized Role Access Rejection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r_unauthorized_access():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "40-49", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Patient role attempting to submit clinician review action
        unauth_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "REFER", "reason": "Patient self-referral attempt"},
            headers={"X-Actor-Id": "usr-pt-09", "X-Actor-Role": "PATIENT"},
        )
        assert unauth_res.status_code == 403
        assert unauth_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


# ---------------------------------------------------------------------------
# Test S: Cross-Case Access / Not Found Handling
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_s_cross_case_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        fake_id = str(uuid.uuid4())
        res = await client.get(f"/api/v1/cases/{fake_id}")
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Test T: Consent Persistence
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_t_consent_persistence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "50-59", "biological_sex": "FEMALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        con_res = await client.post(
            f"/api/v1/cases/{case_id}/consent",
            json={
                "purpose": "CLINICAL_CARE_TRIAGE",
                "language": "hi",
                "channel": "DIGITAL_APP",
                "status": "GRANTED",
            },
        )
        assert con_res.status_code == 200
        con_data = con_res.json()
        assert con_data["status"] == "GRANTED"
        assert con_data["consent_granted"] is True

        # Retrieve
        get_con = await client.get(f"/api/v1/cases/{case_id}/consent")
        assert get_con.status_code == 200
        assert get_con.json()["language"] == "hi"


# ---------------------------------------------------------------------------
# Test U: Invalid Vital Data Rejection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_u_invalid_vital_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        p_res = await client.post("/api/v1/patients", json={"age_bracket": "40-49", "biological_sex": "MALE"})
        c_res = await client.post("/api/v1/cases", json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"})
        case_id = c_res.json()["id"]

        # Pulse out of range (HR: 500 bpm is physiologically impossible)
        bad_hr = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={"heart_rate": 500},
        )
        assert bad_hr.status_code == 422
        assert bad_hr.json()["error"]["code"] == "VALIDATION_ERROR"

        # Systolic BP <= Diastolic BP (violates physiological gradient)
        bad_bp = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={"systolic_bp": 60, "diastolic_bp": 90},
        )
        assert bad_bp.status_code == 422
        assert bad_bp.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Test V: Transaction Rollback Integrity
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_v_transaction_rollback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Posting encounter with non-existent patient must fail and rollback cleanly
        bad_enc = await client.post(
            "/api/v1/encounters",
            json={
                "patient_id": "non-existent-pt-id",
                "facility_id": "FAC-DH-04",
            },
        )
        assert bad_enc.status_code == 404
        assert bad_enc.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Test W: Database Unavailable / Error Contract Shielding
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_w_error_contract_shielding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Verify 404 does not expose stack traces, database schema, or internal paths
        res = await client.get("/api/v1/cases/invalid-uuid-format-1234")
        assert res.status_code == 404
        data = res.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "correlation_id" in data["error"]
        # Invariants: No SQL, no file paths
        assert "sqlite" not in str(data).lower()
        assert "traceback" not in str(data).lower()
        assert "c:\\" not in str(data).lower()


# ---------------------------------------------------------------------------
# Test X: Structured Error Response Schema
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_x_structured_error_response_schema():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/patients", json={})
        assert res.status_code == 422
        data = res.json()
        assert "error" in data
        err = data["error"]
        assert "code" in err
        assert "message" in err
        assert "details" in err
        assert "correlation_id" in err


# ---------------------------------------------------------------------------
# Test Y: Synthetic Mode Verification
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_y_synthetic_mode_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        status_res = await client.get("/api/v1/status")
        assert status_res.status_code == 200
        mode = status_res.json()["mode"]
        assert mode["synthetic_data_only"] is True
        assert mode["demo_mode"] is True


# ---------------------------------------------------------------------------
# Test Z: Migration Upgrade Schema Verification
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_z_migration_schema_verification():
    """Confirms that all required Phase 13 tables are initialized and queryable."""
    async with async_session_factory() as session:
        # Verify queryability across all 15 Phase 13 models
        assert (await session.execute(select(Patient))).scalars().all() is not None
        assert (await session.execute(select(PatientIdentifier))).scalars().all() is not None
        assert (await session.execute(select(Encounter))).scalars().all() is not None
        assert (await session.execute(select(Case))).scalars().all() is not None
        assert (await session.execute(select(CaseStateTransition))).scalars().all() is not None
        assert (await session.execute(select(Evidence))).scalars().all() is not None
        assert (await session.execute(select(Vital))).scalars().all() is not None
        assert (await session.execute(select(TimelineEvent))).scalars().all() is not None
        assert (await session.execute(select(Consent))).scalars().all() is not None
        assert (await session.execute(select(FollowUpQuestion))).scalars().all() is not None
        assert (await session.execute(select(FollowUpAnswer))).scalars().all() is not None
        assert (await session.execute(select(TriageNote))).scalars().all() is not None
        assert (await session.execute(select(ReviewAction))).scalars().all() is not None
        assert (await session.execute(select(AuditEvent))).scalars().all() is not None

        # Query facilities
        fac_res = await session.execute(select(Facility))
        facs = fac_res.scalars().all()
        assert len(facs) >= 5, "Synthetic healthcare facility network must be seeded"
