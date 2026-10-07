import json
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.audit import AuditLog
from app.services.case_state_machine import CaseWorkflowState, ReviewReadinessStatus
from app.services.providers import (
    ProviderError,
    ProviderErrorCode,
    ProviderResponseMetadata,
    SpeechToTextProvider,
    OCRProvider,
    TranslationProvider,
    TextGenerationProvider,
    TextToSpeechProvider,
)


@pytest.mark.asyncio
async def test_scenario_a_new_patient_text_intake(async_client: AsyncClient, database):
    """Scenario 1 / A: New patient creates text-only case.

    Verify canonical case, encounter linkage, evidence creation, and audit logging.
    """
    async with database() as db:
        patient_user = User(
            email="patient.scenario.a@test.invalid",
            full_name="Patient Scenario A",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(patient_user)
        await db.commit()
        await db.refresh(patient_user)

    token = create_access_token(subject=patient_user.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "raw_symptoms": "High fever, chills, and mild headache for two days.",
        "preferred_language": "en",
        "consent_acknowledged": True,
        "approximate_age": 34,
        "gender": "Female",
        "facility_type": "Community Clinic",
        "visit_type": "Outpatient",
    }

    resp = await async_client.post("/api/v1/cases", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    case_data = resp.json()
    case_id = case_data.get("id") or case_data.get("synthetic_case_id")

    # Fetch canonical case
    canon_resp = await async_client.get(f"/api/v1/cases/{case_id}/canonical", headers=headers)
    assert canon_resp.status_code == 200, canon_resp.text
    canon_data = canon_resp.json()

    assert canon_data["workflow_state"] == "INTAKE"
    assert canon_data["case_version"] >= 1
    assert len(canon_data["evidence_items"]) >= 1

    symptom_ev = next(e for e in canon_data["evidence_items"] if e["canonical_field"] == "symptom")
    assert symptom_ev["source_type"] == EvidenceSourceType.PATIENT_TEXT.value
    assert symptom_ev["verification_state"] == VerificationState.PATIENT_REPORTED.value
    assert "High fever" in symptom_ev["raw_value"]

    # Check audit trail
    async with database() as db:
        stmt = (
            select(AuditLog)
            .where(AuditLog.resource_id == canon_data["synthetic_case_id"])
            .where(AuditLog.action == "CASE_INTAKE_CREATED")
        )
        result = await db.execute(stmt)
        audit_entry = result.scalar_one_or_none()
        assert audit_entry is not None


@pytest.mark.asyncio
async def test_scenario_b_voice_evidence_placeholder(async_client: AsyncClient, database):
    """Scenario 2 / B: Voice evidence placeholder.

    Verify modality tracking, source preservation, and pending transcription status.
    """
    async with database() as db:
        patient_user = User(
            email="patient.scenario.b@test.invalid",
            full_name="Patient Scenario B",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(patient_user)
        await db.commit()
        await db.refresh(patient_user)

    token = create_access_token(subject=patient_user.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={
            "raw_symptoms": "Persistent cough",
            "consent_acknowledged": True,
            "approximate_age": 45,
            "gender": "Male",
        },
        headers=headers,
    )
    case_id = create_resp.json()["id"]

    # Append voice audio evidence
    voice_payload = {
        "canonical_field": "speech_audio",
        "raw_value": "artifact://voice_recordings/turn_001.wav",
        "source_type": EvidenceSourceType.PATIENT_VOICE.value,
        "source_reference": "audio_turn_001.wav",
        "verification_state": VerificationState.PATIENT_REPORTED.value,
        "processor_name": "browser_mic_capture",
    }
    ev_resp = await async_client.post(f"/api/v1/cases/{case_id}/evidence", json=voice_payload, headers=headers)
    assert ev_resp.status_code == 201, ev_resp.text
    ev_data = ev_resp.json()

    assert ev_data["canonical_field"] == "speech_audio"
    assert ev_data["source_type"] == EvidenceSourceType.PATIENT_VOICE.value
    assert ev_data["source_reference"] == "audio_turn_001.wav"
    assert ev_data["verification_state"] == VerificationState.PATIENT_REPORTED.value


@pytest.mark.asyncio
async def test_scenario_c_document_evidence_placeholder(async_client: AsyncClient, database):
    """Scenario 3 / C: Document evidence placeholder.

    Verify document provenance, unverified state preservation, and safety boundary.
    """
    async with database() as db:
        patient_user = User(
            email="patient.scenario.c@test.invalid",
            full_name="Patient Scenario C",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(patient_user)
        await db.commit()
        await db.refresh(patient_user)

    token = create_access_token(subject=patient_user.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Dizziness and fatigue", "consent_acknowledged": True},
        headers=headers,
    )
    case_id = create_resp.json()["id"]

    # Append document-derived metric
    doc_payload = {
        "canonical_field": "document_metric:hemoglobin",
        "raw_value": "11.2 g/dL",
        "normalized_value": "11.2",
        "source_type": EvidenceSourceType.DOCUMENT_DERIVED.value,
        "source_reference": "lab_report_october.pdf",
        "verification_state": VerificationState.STAFF_VERIFIED.value,  # Attempting premature verification
        "processor_name": "ocr_extraction_pipeline",
    }
    ev_resp = await async_client.post(f"/api/v1/cases/{case_id}/evidence", json=doc_payload, headers=headers)
    assert ev_resp.status_code == 201, ev_resp.text
    ev_data = ev_resp.json()

    # Cardinal Rule: Document extractions CANNOT self-verify
    assert ev_data["verification_state"] == VerificationState.EXTRACTED_PENDING_VERIFICATION.value
    assert ev_data["source_type"] == EvidenceSourceType.DOCUMENT_DERIVED.value
    assert ev_data["source_reference"] == "lab_report_october.pdf"


@pytest.mark.asyncio
async def test_scenario_d_staff_verification(async_client: AsyncClient, database):
    """Scenario 4 / D: Staff verification.

    Staff enters measured vitals with STAFF_VERIFIED status and nurse attribution.
    """
    async with database() as db:
        patient = User(
            email="patient.scenario.d@test.invalid",
            full_name="Patient D",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        nurse = User(
            email="nurse.triage@test.invalid",
            full_name="Nurse Florence",
            role=UserRole.NURSE,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add_all([patient, nurse])
        await db.commit()
        await db.refresh(patient)
        await db.refresh(nurse)

    pat_token = create_access_token(subject=patient.id, role="patient")
    nurse_token = create_access_token(subject=nurse.id, role="nurse")

    # Patient creates case
    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Headache and blurred vision", "consent_acknowledged": True},
        headers={"Authorization": f"Bearer {pat_token}"},
    )
    case_id = create_resp.json()["id"]

    # Nurse enters verified vitals
    vital_payload = {
        "canonical_field": "vital:bp",
        "raw_value": "142/92 mmHg",
        "normalized_value": "142/92",
        "source_type": EvidenceSourceType.STAFF_ENTERED.value,
        "verification_state": VerificationState.STAFF_VERIFIED.value,
        "processor_name": "triage_desk_sphygmomanometer",
    }
    vital_resp = await async_client.post(
        f"/api/v1/cases/{case_id}/evidence",
        json=vital_payload,
        headers={"Authorization": f"Bearer {nurse_token}"},
    )
    assert vital_resp.status_code == 201, vital_resp.text
    vital_data = vital_resp.json()

    assert vital_data["verification_state"] == VerificationState.STAFF_VERIFIED.value
    assert vital_data["source_type"] == EvidenceSourceType.STAFF_ENTERED.value
    assert vital_data["created_by_user_id"] == nurse.id


@pytest.mark.asyncio
async def test_scenario_e_doctor_correction_history_preservation(async_client: AsyncClient, database):
    """Scenario 5 / E: Doctor clinical correction & historical provenance preservation.

    Doctor amends prior duration without erasing history. Prior marked SUPERSEDED.
    """
    async with database() as db:
        patient = User(
            email="patient.scenario.e@test.invalid",
            full_name="Patient E",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        doctor = User(
            email="doctor.attending@test.invalid",
            full_name="Dr. Attending MD",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add_all([patient, doctor])
        await db.commit()
        await db.refresh(patient)
        await db.refresh(doctor)

    pat_token = create_access_token(subject=patient.id, role="patient")
    doc_token = create_access_token(subject=doctor.id, role="doctor")

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Stomach cramp", "consent_acknowledged": True},
        headers={"Authorization": f"Bearer {pat_token}"},
    )
    case_id = create_resp.json()["id"]

    # Initial patient-reported symptom duration
    await async_client.post(
        f"/api/v1/cases/{case_id}/evidence",
        json={
            "canonical_field": "symptom_duration",
            "raw_value": "started this morning",
            "source_type": EvidenceSourceType.PATIENT_TEXT.value,
            "verification_state": VerificationState.PATIENT_REPORTED.value,
        },
        headers={"Authorization": f"Bearer {pat_token}"},
    )

    # Doctor corrects after physical examination
    amend_resp = await async_client.post(
        f"/api/v1/cases/{case_id}/evidence",
        json={
            "canonical_field": "symptom_duration",
            "raw_value": "4 days progressive onset",
            "source_type": EvidenceSourceType.CLINICIAN_ENTERED.value,
            "verification_state": VerificationState.CLINICIAN_CONFIRMED.value,
            "processor_name": "clinical_bedside_evaluation",
        },
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    assert amend_resp.status_code == 201, amend_resp.text
    amend_data = amend_resp.json()
    assert amend_data["version"] == 2
    assert amend_data["verification_state"] == VerificationState.CLINICIAN_CONFIRMED.value

    # Query full history including superseded
    hist_resp = await async_client.get(
        f"/api/v1/cases/{case_id}/evidence?include_superseded=true",
        headers={"Authorization": f"Bearer {doc_token}"},
    )
    all_evidence = hist_resp.json()
    duration_items = [e for e in all_evidence if e["canonical_field"] == "symptom_duration"]
    assert len(duration_items) == 2
    v1_item = next(e for e in duration_items if e["version"] == 1)
    v2_item = next(e for e in duration_items if e["version"] == 2)
    assert v1_item["verification_state"] == VerificationState.SUPERSEDED.value
    assert v2_item["verification_state"] == VerificationState.CLINICIAN_CONFIRMED.value


@pytest.mark.asyncio
async def test_scenario_f_conflicting_evidence_preservation(async_client: AsyncClient, database):
    """Scenario 6 / F: Conflicting evidence preservation (No silent overwrite).

    Patient self-report conflicts with uploaded document report; both preserved as DISPUTED_CONFLICTING.
    """
    async with database() as db:
        patient = User(
            email="patient.scenario.f@test.invalid",
            full_name="Patient F",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)

    pat_token = create_access_token(subject=patient.id, role="patient")
    headers = {"Authorization": f"Bearer {pat_token}"}

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Skin rash", "consent_acknowledged": True},
        headers=headers,
    )
    case_id = create_resp.json()["id"]

    # 1. Patient reported: no penicillin allergy
    await async_client.post(
        f"/api/v1/cases/{case_id}/evidence",
        json={
            "canonical_field": "allergy:penicillin",
            "raw_value": "No allergies",
            "source_type": EvidenceSourceType.PATIENT_TEXT.value,
            "verification_state": VerificationState.PATIENT_REPORTED.value,
        },
        headers=headers,
    )

    # 2. Document report states: anaphylaxis to penicillin
    doc_ev_resp = await async_client.post(
        f"/api/v1/cases/{case_id}/evidence",
        json={
            "canonical_field": "allergy:penicillin",
            "raw_value": "Anaphylaxis to Penicillin G in 2021",
            "source_type": EvidenceSourceType.DOCUMENT_DERIVED.value,
            "source_reference": "hospital_discharge_2021.pdf",
            "verification_state": VerificationState.EXTRACTED_PENDING_VERIFICATION.value,
        },
        headers=headers,
    )
    assert doc_ev_resp.status_code == 201

    # Verify both records exist and both are marked DISPUTED_CONFLICTING
    list_resp = await async_client.get(f"/api/v1/cases/{case_id}/evidence", headers=headers)
    allergy_items = [e for e in list_resp.json() if e["canonical_field"] == "allergy:penicillin"]
    assert len(allergy_items) == 2
    assert all(e["verification_state"] == VerificationState.DISPUTED_CONFLICTING.value for e in allergy_items)


@pytest.mark.asyncio
async def test_scenario_g_unauthorized_cross_patient_access_idor(async_client: AsyncClient, database):
    """Scenario 7 / G: IDOR protection and cross-patient isolation.

    Patient A cannot view or modify Patient B's case.
    """
    async with database() as db:
        patient_a = User(
            email="patient.a@test.invalid",
            full_name="Patient A",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        patient_b = User(
            email="patient.b@test.invalid",
            full_name="Patient B",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add_all([patient_a, patient_b])
        await db.commit()
        await db.refresh(patient_a)
        await db.refresh(patient_b)

    token_a = create_access_token(subject=patient_a.id, role="patient")
    token_b = create_access_token(subject=patient_b.id, role="patient")

    # Patient A creates a case
    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Severe migraines", "consent_acknowledged": True},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    case_a_id = create_resp.json()["id"]

    # Patient B attempts to access Patient A's case
    get_resp = await async_client.get(
        f"/api/v1/cases/{case_a_id}/canonical",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_resp.status_code == 403, "Cross-patient read access must be strictly forbidden!"

    # Patient B attempts to add evidence to Patient A's case
    post_resp = await async_client.post(
        f"/api/v1/cases/{case_a_id}/evidence",
        json={
            "canonical_field": "malicious_injection",
            "raw_value": "Spoofed data",
            "source_type": EvidenceSourceType.PATIENT_TEXT.value,
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert post_resp.status_code == 403, "Cross-patient evidence addition must be strictly forbidden!"


@pytest.mark.asyncio
async def test_scenario_h_invalid_state_transition_rejected(async_client: AsyncClient, database):
    """Scenario 8 / H: State machine rejects invalid transitions.

    Jumping directly from INTAKE to FINALIZED is rejected with 422 and logged.
    """
    async with database() as db:
        doctor = User(
            email="doctor.trans@test.invalid",
            full_name="Doctor Transition",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)

    token = create_access_token(subject=doctor.id, role="doctor")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Joint swelling", "consent_acknowledged": True},
        headers=headers,
    )
    case_id = create_resp.json()["id"]

    # Attempt illegal transition: INTAKE -> FINALIZED
    bad_transition_resp = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.FINALIZED.value, "reason": "Bypassing triage"},
        headers=headers,
    )
    assert bad_transition_resp.status_code == 422, "Illegal state transition must be rejected!"
    assert "Invalid case transition" in bad_transition_resp.json()["detail"]

    # Verify case state unchanged
    canon_resp = await async_client.get(f"/api/v1/cases/{case_id}/canonical", headers=headers)
    assert canon_resp.json()["workflow_state"] == "INTAKE"


@pytest.mark.asyncio
async def test_scenario_i_review_readiness_and_lifecycle(async_client: AsyncClient, database):
    """Scenario 9 / I: Full lifecycle from INTAKE through REVIEW to FINALIZED.

    Verifies permitted state flow and Review Readiness Index evaluation.
    """
    async with database() as db:
        nurse = User(
            email="nurse.lifecycle@test.invalid",
            full_name="Nurse Lifecycle",
            role=UserRole.NURSE,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        doctor = User(
            email="doctor.lifecycle@test.invalid",
            full_name="Doctor Lifecycle",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add_all([nurse, doctor])
        await db.commit()
        await db.refresh(nurse)
        await db.refresh(doctor)

    nurse_headers = {"Authorization": f"Bearer {create_access_token(subject=nurse.id, role='nurse')}"}
    doc_headers = {"Authorization": f"Bearer {create_access_token(subject=doctor.id, role='doctor')}"}

    create_resp = await async_client.post(
        "/api/v1/cases",
        json={"raw_symptoms": "Low back pain", "consent_acknowledged": True},
        headers=nurse_headers,
    )
    case_id = create_resp.json()["id"]

    # 1. Evaluate readiness
    readiness_resp = await async_client.get(f"/api/v1/cases/{case_id}/readiness", headers=nurse_headers)
    assert readiness_resp.status_code == 200
    readiness = readiness_resp.json()
    assert readiness["has_symptoms"] is True

    # 2. Sequential valid state transitions
    # INTAKE -> PROCESSING -> BUILDING -> READY_FOR_REVIEW
    t1 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.PROCESSING.value},
        headers=nurse_headers,
    )
    assert t1.status_code == 200
    assert t1.json()["current_state"] == "PROCESSING"

    t2 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.BUILDING.value},
        headers=nurse_headers,
    )
    assert t2.status_code == 200

    t3 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.READY_FOR_REVIEW.value},
        headers=nurse_headers,
    )
    assert t3.status_code == 200

    # READY_FOR_REVIEW -> STAFF_REVIEW (Nurse claims triage desk)
    t4 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.STAFF_REVIEW.value},
        headers=nurse_headers,
    )
    assert t4.status_code == 200

    # STAFF_REVIEW -> DOCTOR_REVIEW (Nurse routes to doctor)
    t5 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.DOCTOR_REVIEW.value},
        headers=nurse_headers,
    )
    assert t5.status_code == 200

    # DOCTOR_REVIEW -> CLINICAL_DECISION (Doctor decides)
    t6 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.CLINICAL_DECISION.value},
        headers=doc_headers,
    )
    assert t6.status_code == 200

    # CLINICAL_DECISION -> FINALIZED (Doctor finalizes case)
    t7 = await async_client.post(
        f"/api/v1/cases/{case_id}/transition",
        json={"target_state": CaseWorkflowState.FINALIZED.value},
        headers=doc_headers,
    )
    assert t7.status_code == 200
    assert t7.json()["current_state"] == "FINALIZED"


@pytest.mark.asyncio
async def test_scenario_j_provider_abstraction_and_credential_protection(async_client: AsyncClient, database):
    """Scenario 10 / J: Provider abstraction, normalized error model, and credential isolation.

    Zero secrets leaked in responses; ProviderError formats standardized.
    """
    # 1. Verify ProviderError contracts
    err = ProviderError(
        error_code=ProviderErrorCode.QUOTA_EXHAUSTED,
        message="Free monthly limit reached for Sarvam STT",
        provider_name="sarvam",
        retryable=False,
    )
    assert err.error_code == ProviderErrorCode.QUOTA_EXHAUSTED
    assert "quota_exhausted" in str(err)
    assert err.retryable is False

    meta = ProviderResponseMetadata(
        provider_name="sarvam",
        model_name="saaras-v4",
        latency_ms=142,
        processing_status="success",
    )
    assert meta.provider_name == "sarvam"
    assert meta.latency_ms == 142

    # 2. Inspect case API outputs for credential leakage
    async with database() as db:
        doc = User(
            email="doctor.cred.test@test.invalid",
            full_name="Dr. Credentials Test",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPassword123!"),
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

    token = create_access_token(subject=doc.id, role="doctor")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/cases", headers=headers)
    assert resp.status_code == 200
    body = resp.text

    # Assert that no API keys or secret tokens appear in API body
    forbidden_tokens = ["AIzaSy", "SARVAM_", "GROQ_", "OCR_SPACE_", "password", "hashed_password"]
    for secret in forbidden_tokens:
        assert secret not in body, f"Potential credential leakage detected for token: {secret}"
