"""CLINOVA AI — Multimodal Intake Router.

Implements BPUT Baseline Multimodal Intake:
- Informed consent capture
- Text narrative intake with PII anonymization
- Voice speech-to-text intake (VOICE_TRANSCRIBED provenance)
- Medical report / lab OCR extraction (OCR_EXTRACTED provenance)
- Regional translation (Hindi, Odia, English)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models import (
    Patient,
    PatientIdentifier,
    Encounter,
    Case,
    CaseStateTransition,
    Consent,
    Evidence,
    EvidenceRecord,
    Vital,
    VitalReading,
    TimelineEvent,
    AuditEvent,
    AuditLog,
    Facility,
    User,
    TriageSnapshotRecord,
    utc_now,
)
from app.domain.triage import compute_deterministic_triage
from app.core.config import settings
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import Permission, check_role_permission
from app.core.policy import (
    authorize_facility_access,
    record_security_audit_event,
)
from app.core.errors import ClinovaAPIError
from app.schemas.intake import (
    PatientIntakeRequest,
    PatientIntakeResponse,
    FrontendIntakeSubmissionRequest,
    normalize_pathway,
)
from app.baseline.intake.adapters import (
    translate_text,
    scrub_pii,
    parse_clinical_narrative,
    process_voice_transcript,
    parse_medical_report_ocr,
)
from app.domain.caregraph.engine import (
    calculate_risk_score,
    evaluate_uncertainty_and_gaps,
)
from app.domain.signalgraph.engine import signal_engine

router = APIRouter()


class ConsentRequest(BaseModel):
    case_id: Optional[str] = None
    patient_ref: Optional[str] = None
    language: str = "en"
    consent_granted: bool = True


class TextIntakeRequest(BaseModel):
    facility_id: str = "FAC-DH-04"
    reported_name: Optional[str] = None
    reported_age: Optional[int] = 45
    biological_sex: str = "MALE"
    narrative_text: str
    language: str = "en"
    consent_granted: bool = True
    vitals: Optional[Dict[str, Any]] = None


class VoiceIntakeRequest(BaseModel):
    facility_id: str = "FAC-PHC-01"
    audio_transcript: str
    confidence_score: float = 0.92
    language: str = "hi"
    reported_name: Optional[str] = None
    reported_age: Optional[int] = 50
    biological_sex: str = "MALE"
    consent_granted: bool = True


class OCRIntakeRequest(BaseModel):
    raw_text: str
    confidence_score: float = 0.88
    filename: Optional[str] = "lab_report.pdf"


class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str = "en"


@router.post("/consent", tags=["Multimodal Intake"])
async def record_consent(req: ConsentRequest, db: AsyncSession = Depends(get_db)):
    """Records patient informed consent."""
    consent_id = str(uuid.uuid4())
    if req.case_id:
        existing = await db.execute(select(Consent).where(Consent.case_id == req.case_id))
        consent_obj = existing.scalars().first()
        if consent_obj:
            consent_obj.consent_granted = req.consent_granted
            consent_obj.language = req.language
            consent_obj.recorded_at = datetime.now(timezone.utc)
        else:
            consent_obj = Consent(
                id=consent_id,
                case_id=req.case_id,
                consent_granted=req.consent_granted,
                language=req.language,
                recorded_at=datetime.now(timezone.utc),
            )
            db.add(consent_obj)
        await db.commit()

    return {
        "consent_id": consent_id,
        "consent_granted": req.consent_granted,
        "language": req.language,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "status": "RECORDED",
    }


@router.post("/text", tags=["Multimodal Intake"])
async def intake_text_narrative(req: TextIntakeRequest, db: AsyncSession = Depends(get_db)):
    """
    Ingests text narrative clinical encounter.
    Enforces PII minimization, translation, initial risk scoring, and uncertainty evaluation.
    """
    # 1. Translation
    normalized_text, _ = translate_text(req.narrative_text, req.language, target_lang="en")

    # 2. PII Scrubbing
    pii_result = scrub_pii(normalized_text, reported_name=req.reported_name, reported_age=req.reported_age)
    synthetic_pt_id = pii_result["synthetic_id"]
    age_bracket = pii_result["age_bracket"]
    scrubbed_narrative = pii_result["scrubbed_narrative"]

    # 3. Clinical Entity & Syndrome Extraction
    parsed = parse_clinical_narrative(scrubbed_narrative)
    syndrome = parsed["primary_syndrome"]
    req_bundle = parsed["required_bundle"]
    red_flags = parsed["red_flags"]

    # 4. Risk & Acuity Scoring
    vitals_dict = req.vitals or {}
    rt, acuity_tier = calculate_risk_score(vitals_dict, red_flags=red_flags)

    # 5. Uncertainty & Missing Parameter Detection
    ev_record_temp = [{"provenance_type": "PATIENT_REPORTED", "confidence_score": 0.90, "verification_status": "UNVERIFIED"}]
    u_eval = evaluate_uncertainty_and_gaps(syndrome, vitals_dict, ev_record_temp, narrative_text=scrubbed_narrative)
    u_t = u_eval["uncertainty_score"]

    # Determine initial FSM state
    if len(u_eval["conflicts"]) > 0:
        initial_status = "CONFLICTING_DATA"
    elif u_t > 0.40 and len(u_eval["missing_parameters"]) > 0 and rt < 0.70:
        initial_status = "INSUFFICIENT_DATA"
    elif rt >= 0.70:
        initial_status = "TRIAGED"
    else:
        initial_status = "REVIEW_REQUIRED"

    # Persist Synthetic Patient (ensuring synthetic_id uniqueness)
    check_pt = await db.execute(select(Patient).where(Patient.synthetic_id == synthetic_pt_id))
    if check_pt.scalars().first():
        while True:
            synthetic_pt_id = f"SYN-PT-{uuid.uuid4().hex[:8].upper()}"
            recheck = await db.execute(select(Patient).where(Patient.synthetic_id == synthetic_pt_id))
            if not recheck.scalars().first():
                break

    patient = Patient(
        synthetic_id=synthetic_pt_id,
        age_bracket=age_bracket,
        biological_sex=req.biological_sex,
    )
    db.add(patient)
    await db.flush()

    # Verify Facility exists
    fac = await db.get(Facility, req.facility_id)
    if not fac:
        fac = (await db.execute(select(Facility))).scalars().first()
        facility_id = fac.id if fac else req.facility_id
    else:
        facility_id = req.facility_id

    case_num = f"CAS-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
    case = Case(
        case_number=case_num,
        patient_id=patient.id,
        facility_id=facility_id,
        status=initial_status,
        current_state=initial_status,
        state_version=1,
        acuity_tier=acuity_tier,
        risk_score=rt,
        trajectory_slope=0.0,
        uncertainty_score=u_t,
        presenting_complaint=scrubbed_narrative,
        primary_syndrome=syndrome,
        required_bundle=req_bundle,
    )
    db.add(case)
    await db.flush()

    # Consent
    consent = Consent(
        case_id=case.id,
        consent_granted=req.consent_granted,
        language=req.language,
    )
    db.add(consent)

    # Evidence Record
    ev = EvidenceRecord(
        case_id=case.id,
        provenance_type="PATIENT_REPORTED",
        source_filename="narrative_text_intake.txt",
        extracted_payload={"narrative": scrubbed_narrative, "syndrome": syndrome, "bundle": req_bundle},
        confidence_score=0.90,
        verification_status="UNVERIFIED",
    )
    db.add(ev)

    # Initial Vital Reading if provided
    if vitals_dict:
        vital_reading = VitalReading(
            case_id=case.id,
            heart_rate=vitals_dict.get("heart_rate"),
            systolic_bp=vitals_dict.get("systolic_bp"),
            diastolic_bp=vitals_dict.get("diastolic_bp"),
            spo2_percent=vitals_dict.get("spo2_percent"),
            respiratory_rate=vitals_dict.get("respiratory_rate"),
            temperature_celsius=vitals_dict.get("temperature_celsius"),
            avpu_score=vitals_dict.get("avpu_score", "ALERT"),
        )
        db.add(vital_reading)

        canonical_vital = Vital(
            id=str(uuid.uuid4()),
            case_id=case.id,
            heart_rate=vitals_dict.get("heart_rate"),
            systolic_bp=vitals_dict.get("systolic_bp"),
            diastolic_bp=vitals_dict.get("diastolic_bp"),
            spo2_percent=vitals_dict.get("spo2_percent"),
            respiratory_rate=vitals_dict.get("respiratory_rate"),
            temperature_celsius=vitals_dict.get("temperature_celsius"),
            avpu_score=vitals_dict.get("avpu_score", "ALERT"),
            supplemental_o2=vitals_dict.get("supplemental_o2", False),
            source="PATIENT_REPORTED",
            recorded_at=utc_now(),
            provenance_metadata={"source": "PATIENT_REPORTED"},
            verification_context={"verified": False, "verification_status": "UNVERIFIED", "source_type": "PATIENT_REPORTED"},
            created_at=utc_now(),
        )
        db.add(canonical_vital)

    # Audit Trail
    audit = AuditLog(
        actor_id="INTAKE_SYSTEM",
        action="INTAKE_TEXT_CREATED",
        entity_type="CASE",
        entity_id=case.id,
        details={
            "case_number": case.case_number,
            "patient_synthetic_id": synthetic_pt_id,
            "status": initial_status,
            "risk_score": rt,
            "acuity_tier": acuity_tier,
        },
    )
    db.add(audit)
    await db.commit()

    # Feed SignalGraph
    signal_engine.record_event(
        facility_id=facility_id,
        syndrome_tag=f"SYNDROME_{syndrome}",
        acuity_tier=acuity_tier,
    )

    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "patient_synthetic_id": synthetic_pt_id,
        "status": case.status,
        "acuity_tier": case.acuity_tier,
        "risk_score": case.risk_score,
        "uncertainty_score": case.uncertainty_score,
        "primary_syndrome": syndrome,
        "required_bundle": req_bundle,
        "missing_parameters": u_eval["missing_parameters"],
        "follow_up_questions": u_eval["follow_up_questions"],
        "conflicts": u_eval["conflicts"],
    }


async def intake_voice(req: VoiceIntakeRequest, db: AsyncSession = Depends(get_db)):
    """Transcribes audio narrative, assigns VOICE_TRANSCRIBED provenance, and executes intake."""
    translated, _ = translate_text(req.audio_transcript, req.language, target_lang="en")
    voice_result = process_voice_transcript(translated, confidence=req.confidence_score)

    # Execute text intake with voice metadata
    text_req = TextIntakeRequest(
        facility_id=req.facility_id,
        reported_name=req.reported_name,
        reported_age=req.reported_age,
        biological_sex=req.biological_sex,
        narrative_text=translated,
        language="en",
        consent_granted=req.consent_granted,
    )
    result = await intake_text_narrative(text_req, db)

    # Update evidence record provenance to VOICE_TRANSCRIBED
    ev_stmt = select(EvidenceRecord).where(EvidenceRecord.case_id == result["case_id"])
    ev_obj = (await db.execute(ev_stmt)).scalars().first()
    if ev_obj:
        ev_obj.provenance_type = "VOICE_TRANSCRIBED"
        ev_obj.confidence_score = req.confidence_score
        ev_obj.source_filename = "voice_audio_stream.wav"
        await db.commit()

    result["provenance_type"] = "VOICE_TRANSCRIBED"
    result["voice_confidence"] = req.confidence_score
    return result


@router.post("/ocr", tags=["Multimodal Intake"])
async def intake_medical_report_ocr(req: OCRIntakeRequest):
    """Parses medical report / lab slip with OCR extraction and confidence guardrails."""
    res = parse_medical_report_ocr(req.raw_text, confidence=req.confidence_score)
    return res


@router.post("/translate", tags=["Multimodal Intake"])
async def translate_clinical_text(req: TranslateRequest):
    """Translates between regional Indian languages and clinical English."""
    translated, target = translate_text(req.text, req.source_lang, req.target_lang)
    return {
        "original_text": req.text,
        "translated_text": translated,
        "source_lang": req.source_lang,
        "target_lang": target,
    }


@router.post("/submit", response_model=PatientIntakeResponse, tags=["Multimodal Intake"])
async def submit_frontend_intake(
    req: PatientIntakeRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Authoritative Phase 15 Patient Intake & Consent Persistence Endpoint.
    Enforces:
    1. Server-side authentication and role check (Permission.CASE_CREATE).
    2. Compulsory presenting symptoms/chief complaint validation.
    3. Pathway validation and metadata assignment.
    4. Informed consent enforcement (mandatory for regular, explicit implied handling for emergency).
    5. Patient self-scope vs. staff-assisted intake boundary enforcement.
    6. Atomic persistence of Patient, Encounter, canonical Master Case, and Consent.
    7. Provenance tracking, longitudinal timeline event, and medicolegal audit event.
    8. Idempotency duplicate detection without destructive merges.
    """
    # 1. RBAC Authority Verification
    check_role_permission(actor.role, Permission.CASE_CREATE)

    # 2. Symptoms Validation (compulsory, non-empty, non-whitespace, bounded length)
    complaint_clean = (req.chief_complaint or "").strip()
    if not complaint_clean:
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Presenting symptom / chief complaint cannot be empty or whitespace-only.",
            status_code=422,
        )
    if len(complaint_clean) > 5000:
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Presenting symptom narrative exceeds maximum allowable length of 5000 characters.",
            status_code=422,
        )

    # 3. Pathway Validation & Normalization
    canonical_pathway = normalize_pathway(req.pathway)

    # 4. Facility Resolution & Scope
    fac = await db.get(Facility, req.facility_id)
    if not fac:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Referenced healthcare facility '{req.facility_id}' does not exist.",
            status_code=404,
        )

    # 5. Consent Enforcement
    if req.consent_status == "REVOKED":
        is_consent_given = False
    else:
        is_consent_given = bool(req.consent_confirmed or req.consent_granted or (req.consent_status == "GRANTED"))

    if canonical_pathway == "EMERGENCY":
        consent_status = "GRANTED" if is_consent_given else "IMPLIED_EMERGENCY"
    else:
        if not is_consent_given:
            raise ClinovaAPIError(
                category="VALIDATION_ERROR",
                message="Informed consent is mandatory for non-emergency patient intake.",
                status_code=422,
            )
        consent_status = "GRANTED"

    # 6. Idempotency / Duplicate Submission Check (Pre-Mutation: Prevents Orphan Records)
    if req.client_submission_id:
        dup_stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.action == "intake.submitted",
                AuditEvent.actor_id == actor.actor_id,
                AuditEvent.correlation_id == req.client_submission_id,
            )
            .order_by(desc(AuditEvent.created_at))
        )
        existing_audit = (await db.execute(dup_stmt)).scalars().first()
        if not existing_audit:
            fallback_stmt = (
                select(AuditEvent)
                .where(
                    AuditEvent.action == "intake.submitted",
                    AuditEvent.actor_id == actor.actor_id,
                )
                .order_by(desc(AuditEvent.created_at))
                .limit(50)
            )
            for aud in (await db.execute(fallback_stmt)).scalars().all():
                if aud.details and aud.details.get("client_submission_id") == req.client_submission_id:
                    existing_audit = aud
                    break

        if existing_audit and existing_audit.case_id:
            existing_case = await db.get(Case, existing_audit.case_id)
            if existing_case:
                existing_patient = await db.get(Patient, existing_case.patient_id)
                existing_consent = (
                    await db.execute(select(Consent).where(Consent.case_id == existing_case.id))
                ).scalars().first()
                q_cases = (
                    await db.execute(
                        select(Case).where(Case.facility_id == existing_case.facility_id, Case.is_closed == False)
                    )
                ).scalars().all()
                c_id = existing_consent.id if existing_consent else ""
                c_status = existing_consent.status if existing_consent else consent_status
                return PatientIntakeResponse(
                    success=True,
                    case_id=existing_case.id,
                    case_number=existing_case.case_number,
                    patient_id=existing_case.patient_id,
                    patient_synthetic_id=existing_patient.synthetic_id if existing_patient else "PT-SYN-UNKNOWN",
                    synthetic_reference=existing_patient.synthetic_id if existing_patient else "PT-SYN-UNKNOWN",
                    encounter_id=existing_case.encounter_id or "",
                    facility_id=existing_case.facility_id,
                    pathway=existing_case.pathway,
                    status=existing_case.status,
                    current_state=existing_case.current_state,
                    state_version=existing_case.state_version,
                    consent_status=c_status,
                    consent_id=c_id,
                    queue_position=len(q_cases),
                    message="Duplicate submission detected. Returned existing case reference.",
                    is_mock=False,
                    is_duplicate=True,
                )

    # 7. Patient Scope Authorization & Validation
    if actor.is_patient():
        if req.synthetic_patient_id:
            if actor.patient_id:
                patient_check = await db.get(Patient, actor.patient_id)
                if not patient_check:
                    stmt = select(Patient).where(Patient.synthetic_id == actor.patient_id)
                    patient_check = (await db.execute(stmt)).scalars().first()
                if patient_check and (
                    req.synthetic_patient_id != patient_check.id
                    and req.synthetic_patient_id != patient_check.synthetic_id
                ):
                    await record_security_audit_event(
                        db=db,
                        actor_id=actor.actor_id,
                        actor_role=actor.role,
                        action="security.patient_scope_denied",
                        object_type="PATIENT",
                        object_id=req.synthetic_patient_id,
                        result="DENIED",
                        details={"reason": "Patients may only submit intake for their own patient identity"},
                    )
                    raise ClinovaAPIError(
                        category="AUTHORIZATION_ERROR",
                        message="Patients are only authorized to submit intake for their own patient identity.",
                        status_code=403,
                    )
            else:
                # Unlinked patient account attempting to supply arbitrary external synthetic patient ID
                await record_security_audit_event(
                    db=db,
                    actor_id=actor.actor_id,
                    actor_role=actor.role,
                    action="security.patient_scope_denied",
                    object_type="PATIENT",
                    object_id=req.synthetic_patient_id,
                    result="DENIED",
                    details={"reason": "Unlinked patient accounts may not claim external patient identities."},
                )
                raise ClinovaAPIError(
                    category="AUTHORIZATION_ERROR",
                    message="Patients are only authorized to submit intake for their own patient identity.",
                    status_code=403,
                )
    else:
        # Staff-assisted intake: verify facility authorization
        await authorize_facility_access(req.facility_id, actor, db=db)

    # 8. Complete Atomic Database Persistence Transaction
    try:
        # A. Patient Resolution & Persistence
        is_new_patient = False
        if actor.is_patient():
            source_class = "PATIENT_REPORTED"
            patient = None
            if actor.patient_id:
                patient = await db.get(Patient, actor.patient_id)
                if not patient:
                    stmt = select(Patient).where(Patient.synthetic_id == actor.patient_id)
                    patient = (await db.execute(stmt)).scalars().first()

            if not patient:
                is_new_patient = True
                while True:
                    synth_id = f"PT-SYN-{random.randint(10000, 999999)}"
                    existing_pt = await db.execute(select(Patient).where(Patient.synthetic_id == synth_id))
                    if not existing_pt.scalars().first():
                        break
                patient = Patient(
                    id=str(uuid.uuid4()),
                    synthetic_id=synth_id,
                    age_bracket=req.reported_age_bracket or "25-35 YRS",
                    biological_sex=(req.biological_sex or "FEMALE").upper(),
                    is_synthetic=True,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                )
                db.add(patient)
                ident = PatientIdentifier(
                    id=str(uuid.uuid4()),
                    patient_id=patient.id,
                    identifier_type="SYNTHETIC_ID",
                    identifier_value=synth_id,
                    is_primary=True,
                    created_at=utc_now(),
                )
                db.add(ident)
                db_user = await db.get(User, actor.actor_id)
                if db_user:
                    db_user.patient_id = patient.id
                await db.flush()
        else:
            source_class = "STAFF_ENTERED"
            patient = None
            if req.synthetic_patient_id:
                stmt = select(Patient).where(
                    (Patient.id == req.synthetic_patient_id) | (Patient.synthetic_id == req.synthetic_patient_id)
                )
                patient = (await db.execute(stmt)).scalars().first()

            if not patient:
                is_new_patient = True
                if req.synthetic_patient_id:
                    synth_id = req.synthetic_patient_id
                else:
                    while True:
                        synth_id = f"PT-SYN-{random.randint(10000, 999999)}"
                        existing_pt = await db.execute(select(Patient).where(Patient.synthetic_id == synth_id))
                        if not existing_pt.scalars().first():
                            break
                patient = Patient(
                    id=str(uuid.uuid4()),
                    synthetic_id=synth_id,
                    age_bracket=req.reported_age_bracket or "25-35 YRS",
                    biological_sex=(req.biological_sex or "FEMALE").upper(),
                    is_synthetic=True,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                )
                db.add(patient)
                ident = PatientIdentifier(
                    id=str(uuid.uuid4()),
                    patient_id=patient.id,
                    identifier_type="SYNTHETIC_ID",
                    identifier_value=patient.synthetic_id,
                    is_primary=True,
                    created_at=utc_now(),
                )
                db.add(ident)
                await db.flush()

        # B. Clinical Encounter Initialization
        encounter_id = str(uuid.uuid4())
        encounter = Encounter(
            id=encounter_id,
            patient_id=patient.id,
            facility_id=fac.id,
            environment=req.environment or settings.ENVIRONMENT,
            pathway=canonical_pathway,
            source_actor_id=actor.actor_id,
            source_actor_role=actor.role,
            started_at=utc_now(),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(encounter)
        await db.flush()

        # C. Canonical Master Case Root Aggregate
        case_id = str(uuid.uuid4())
        case_num = f"CAS-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:8].upper()}"
        acuity_tier = "CRITICAL" if canonical_pathway == "EMERGENCY" else "ROUTINE"

        source_lang = req.preferred_language or "en"
        case = Case(
            id=case_id,
            case_number=case_num,
            patient_id=patient.id,
            encounter_id=encounter.id,
            facility_id=fac.id,
            pathway=canonical_pathway,
            current_state="INTAKE_RECORDED",
            status="NEW",
            acuity_tier=acuity_tier,
            risk_score=0.90 if canonical_pathway == "EMERGENCY" else 0.10,
            trajectory_slope=0.0,
            uncertainty_score=0.50,
            state_version=1,
            environment_id=req.environment or settings.ENVIRONMENT,
            presenting_complaint=complaint_clean,
            source_language=source_lang,
            target_language="en",
            translation_status="NONE" if source_lang == "en" else "TRANSLATION_PENDING",
            primary_syndrome=None,
            required_bundle=None,
            is_closed=False,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(case)
        await db.flush()

        # D. Initial Case State Transition Milestone
        transition = CaseStateTransition(
            id=str(uuid.uuid4()),
            case_id=case.id,
            from_state="NONE",
            to_state="INTAKE_RECORDED",
            actor_id=actor.actor_id,
            actor_role=actor.role,
            reason=f"Patient intake recorded via {req.intake_channel} ({canonical_pathway})",
            state_version=1,
            created_at=utc_now(),
        )
        db.add(transition)

        # E. Informed Consent Persistence
        consent_id = str(uuid.uuid4())
        consent = Consent(
            id=consent_id,
            case_id=case.id,
            purpose=req.consent_purpose or "CLINICAL_CARE_TRIAGE",
            language=req.preferred_language or "en",
            channel=req.consent_channel or "DIGITAL_APP",
            consent_version=req.consent_version or "v1.0",
            status=consent_status,
            consent_granted=(consent_status != "REVOKED"),
            hash_reference=f"ACTOR:{actor.actor_id}:{uuid.uuid4().hex[:12]}",
            recorded_at=utc_now(),
            created_at=utc_now(),
        )
        db.add(consent)
        await db.flush()

        # F. Discrete Clinical Evidence & Provenance Preservation (epistemic_state: KNOWN direct observation)
        evidence = Evidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            source_class=source_class,
            epistemic_state="KNOWN",
            parameter_name="presenting_complaint",
            content_value={
                "chief_complaint": complaint_clean,
                "symptoms": req.symptoms,
                "symptom_duration": req.symptom_duration,
                "narrative_notes": req.narrative_notes,
                "voice_transcript": req.voice_transcript,
                "document_uploaded": req.document_uploaded,
                "document_type": req.document_type,
                "pathway": canonical_pathway,
            },
            confidence_score=0.95 if actor.is_patient() else 0.90,
            captured_timestamp=utc_now(),
            provenance_metadata={
                "channel": req.intake_channel or "DIGITAL_APP",
                "actor_id": actor.actor_id,
                "actor_role": actor.role,
                "intake_mode": "STAFF_ASSISTED" if not actor.is_patient() else "PATIENT_SELF",
                "source_language": source_lang,
                "language_declaration": "USER_DECLARED",
            },
            verification_metadata={
                "verified": False,
                "verification_status": "UNVERIFIED",
            },
            transformation_metadata={},
            created_at=utc_now(),
        )
        db.add(evidence)

        # Upstream EvidenceRecord compatibility record
        ev_compat = EvidenceRecord(
            id=str(uuid.uuid4()),
            case_id=case.id,
            provenance_type=source_class,
            source_filename="intake_submission.json",
            extracted_payload={
                "narrative": complaint_clean,
                "duration": req.symptom_duration,
                "notes": req.narrative_notes,
            },
            confidence_score=0.95 if actor.is_patient() else 0.90,
            verification_status="UNVERIFIED",
            created_at=utc_now(),
        )
        db.add(ev_compat)

        # G. Physiological Vitals (if provided at intake)
        if req.vitals:
            if source_class in ["PATIENT_REPORTED", "DEVICE_DERIVED"]:
                verif_ctx = {
                    "verified": False,
                    "verification_status": "UNVERIFIED",
                    "source_type": source_class,
                }
            else:
                is_clinician = actor.role in ["CLINICIAN", "DOCTOR"]
                verif_ctx = {
                    "verified": is_clinician,
                    "verification_status": "CLINICIAN_VERIFIED" if is_clinician else "STAFF_RECORDED",
                    "verified_by": actor.actor_id if is_clinician else None,
                    "role": actor.role,
                }

            prov_meta = {
                "recorded_by": actor.actor_id,
                "actor_role": actor.role,
                "source": source_class,
            }
            if case.encounter_id:
                prov_meta["encounter_id"] = case.encounter_id

            v_obj = Vital(
                id=str(uuid.uuid4()),
                case_id=case.id,
                heart_rate=req.vitals.get("heart_rate"),
                systolic_bp=req.vitals.get("systolic_bp"),
                diastolic_bp=req.vitals.get("diastolic_bp"),
                spo2_percent=req.vitals.get("spo2_percent"),
                respiratory_rate=req.vitals.get("respiratory_rate"),
                temperature_celsius=req.vitals.get("temperature_celsius"),
                avpu_score=req.vitals.get("avpu_score", "ALERT"),
                supplemental_o2=req.vitals.get("supplemental_o2", False),
                source=source_class,
                recorded_at=utc_now(),
                provenance_metadata=prov_meta,
                verification_context=verif_ctx,
                created_at=utc_now(),
            )
            db.add(v_obj)
            vr_compat = VitalReading(
                id=str(uuid.uuid4()),
                case_id=case.id,
                heart_rate=req.vitals.get("heart_rate"),
                systolic_bp=req.vitals.get("systolic_bp"),
                diastolic_bp=req.vitals.get("diastolic_bp"),
                spo2_percent=req.vitals.get("spo2_percent"),
                respiratory_rate=req.vitals.get("respiratory_rate"),
                temperature_celsius=req.vitals.get("temperature_celsius"),
                avpu_score=req.vitals.get("avpu_score", "ALERT"),
                recorded_at=utc_now(),
            )
            db.add(vr_compat)

            # Compute initial deterministic triage snapshot
            now_triage = utc_now()
            snapshot = compute_deterministic_triage(
                case_id=case.id,
                pathway=canonical_pathway,
                current_state=case.current_state,
                presenting_complaint=complaint_clean,
                latest_vital=v_obj,
                now=now_triage,
            )
            case.acuity_tier = snapshot["acuity_tier"]
            case.risk_score = snapshot["risk_score"]
            case.uncertainty_score = snapshot["uncertainty_score"]

            snapshot_record = TriageSnapshotRecord(
                id=str(uuid.uuid4()),
                case_id=case.id,
                vital_id=v_obj.id,
                priority_tier=snapshot["priority_tier"],
                acuity_tier=snapshot["acuity_tier"],
                risk_score=snapshot["risk_score"],
                uncertainty_score=snapshot["uncertainty_score"],
                news2_score=snapshot["news2"].get("score"),
                shock_index=snapshot["shock_index"].get("score"),
                has_critical_red_flags=snapshot["has_critical_red_flags"],
                snapshot_data=snapshot,
                ruleset_version=snapshot["ruleset_version"],
                calculated_at=now_triage,
            )
            db.add(snapshot_record)

        # H. Longitudinal Timeline Milestone Events (Section 18)
        # 1. Intake Submitted
        tl_intake = TimelineEvent(
            id=str(uuid.uuid4()),
            case_id=case.id,
            event_type="INTAKE_SUBMITTED",
            event_title="Patient Clinical Intake Recorded",
            event_content=f"Intake completed via {req.intake_channel or 'DIGITAL_APP'} for pathway {canonical_pathway}. Presenting: {complaint_clean[:100]}",
            event_timestamp=utc_now(),
            actor_id=actor.actor_id,
            actor_role=actor.role,
            evidence_id=evidence.id,
            is_conflict=False,
            provenance_metadata={
                "pathway": canonical_pathway,
                "consent_status": consent_status,
                "intake_channel": req.intake_channel,
            },
            created_at=utc_now(),
        )
        db.add(tl_intake)

        # 2. Consent Recorded
        tl_consent = TimelineEvent(
            id=str(uuid.uuid4()),
            case_id=case.id,
            event_type="CONSENT_RECORDED",
            event_title="Patient Consent Recorded",
            event_content=f"Consent status '{consent_status}' captured for purpose '{req.consent_purpose or 'CLINICAL_CARE_TRIAGE'}' (version {req.consent_version or 'v1.0'}).",
            event_timestamp=utc_now(),
            actor_id=actor.actor_id,
            actor_role=actor.role,
            is_conflict=False,
            provenance_metadata={
                "consent_id": consent.id,
                "status": consent_status,
                "channel": req.consent_channel or "DIGITAL_APP",
            },
            created_at=utc_now(),
        )
        db.add(tl_consent)

        # 3. Master Case Created
        tl_case = TimelineEvent(
            id=str(uuid.uuid4()),
            case_id=case.id,
            event_type="CASE_CREATED",
            event_title="Master Case Initialized",
            event_content=f"Canonical Master Case {case.case_number} initialized in state INTAKE_RECORDED.",
            event_timestamp=utc_now(),
            actor_id=actor.actor_id,
            actor_role=actor.role,
            is_conflict=False,
            provenance_metadata={
                "encounter_id": encounter.id,
                "facility_id": fac.id,
                "acuity_tier": acuity_tier,
            },
            created_at=utc_now(),
        )
        db.add(tl_case)

        # I. Medicolegal Audit Ledger Events (Section 18)
        # 1. Patient created or reused
        audit_patient = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="patient.created" if is_new_patient else "patient.reused",
            object_type="PATIENT",
            object_id=patient.id,
            result="SUCCESS",
            correlation_id=req.client_submission_id,
            details={
                "synthetic_id": patient.synthetic_id,
                "age_bracket": patient.age_bracket,
                "biological_sex": patient.biological_sex,
            },
            created_at=utc_now(),
        )
        db.add(audit_patient)

        # 2. Encounter created
        audit_encounter = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="encounter.created",
            object_type="ENCOUNTER",
            object_id=encounter.id,
            result="SUCCESS",
            correlation_id=req.client_submission_id,
            details={"patient_id": patient.id, "facility_id": fac.id, "pathway": canonical_pathway},
            created_at=utc_now(),
        )
        db.add(audit_encounter)

        # 3. Master Case created
        audit_case = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="case.created",
            object_type="CASE",
            object_id=case.id,
            result="SUCCESS",
            correlation_id=req.client_submission_id,
            details={
                "case_number": case.case_number,
                "patient_id": patient.id,
                "facility_id": fac.id,
                "acuity_tier": acuity_tier,
                "pathway": canonical_pathway,
            },
            created_at=utc_now(),
        )
        db.add(audit_case)

        # 4. Consent recorded
        audit_consent = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="consent.recorded",
            object_type="CONSENT",
            object_id=consent.id,
            result="SUCCESS",
            correlation_id=req.client_submission_id,
            details={
                "consent_status": consent_status,
                "purpose": consent.purpose,
                "channel": consent.channel,
                "version": consent.consent_version,
            },
            created_at=utc_now(),
        )
        db.add(audit_consent)

        # 5. Intake submitted
        audit_intake = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="intake.submitted",
            object_type="CASE",
            object_id=case.id,
            result="SUCCESS",
            correlation_id=req.client_submission_id,
            details={
                "case_number": case.case_number,
                "patient_synthetic_id": patient.synthetic_id,
                "facility_id": fac.id,
                "pathway": canonical_pathway,
                "consent_status": consent_status,
                "client_submission_id": req.client_submission_id,
            },
            created_at=utc_now(),
        )
        db.add(audit_intake)

        # Upstream AuditLog compatibility record
        audit_log = AuditLog(
            actor_id=actor.actor_id,
            action="INTAKE_SUBMISSION_RECORDED",
            entity_type="CASE",
            entity_id=case.id,
            details={
                "case_number": case.case_number,
                "patient_synthetic_id": patient.synthetic_id,
                "status": "NEW",
                "pathway": canonical_pathway,
            },
        )
        db.add(audit_log)

        # Commit entire atomic intake transaction
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

    # Calculate queue depth at the receiving facility
    q_cases = (
        await db.execute(
            select(Case).where(Case.facility_id == fac.id, Case.is_closed == False)
        )
    ).scalars().all()

    return PatientIntakeResponse(
        success=True,
        case_id=case.id,
        case_number=case.case_number,
        patient_id=patient.id,
        patient_synthetic_id=patient.synthetic_id,
        synthetic_reference=patient.synthetic_id,
        encounter_id=encounter.id,
        facility_id=fac.id,
        pathway=canonical_pathway,
        status=case.status,
        current_state=case.current_state,
        state_version=case.state_version,
        consent_status=consent_status,
        consent_id=consent.id,
        queue_position=len(q_cases),
        message="Patient intake recorded successfully in live clinical database.",
        is_mock=False,
        is_duplicate=False,
    )

