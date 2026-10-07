import json
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File, Form, Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.multimodal_job import MultimodalProcessingRecord, ProcessingStatus
from app.models.user import User, UserRole
from app.core.deps import (
    get_client_ip,
    get_current_clinician,
    get_current_doctor,
    get_current_user,
    get_current_user_optional,
    get_intake_user,
)
from app.schemas.portal import PatientCaseResponse
from app.api.v1.endpoints.portal import patient_case_response
from app.schemas.case import (
    CaseCreateRequest,
    CaseResponse,
    CaseAssignRequest,
    CaseVerifyIntakeRequest,
    StructuredTriageNote,
)
from app.schemas.canonical_case import (
    EvidenceCreateRequest,
    EvidenceResponse,
    CaseTransitionRequest,
    CaseTransitionResponse,
    ReviewReadinessResponse,
    CanonicalCaseResponse,
    CaseTextInput,
    CaseTranslateInput,
    CaseTTSInput,
    ProcessingRecordResponse,
    CaseBuildRequest,
    CaseBuildRunResponse,
    CaseSnapshotResponse,
    CanonicalFactResponse,
    TimelineEventResponse,
)
from app.schemas.verification import (
    VerificationFindingResponse,
    VerificationConflictResponse,
    VerificationRunResponse,
    VerifyCaseRequest,
    ResolveFindingRequest,
    ReviewReadinessSummaryResponse,
)
from app.schemas.completion import (
    StartCompletionSessionRequest,
    SubmitAnswerRequest,
    SkipQuestionRequest,
    CompleteSessionRequest,
    CompletionQuestionResponse,
    CompletionAnswerResponse,
    CompletionSessionResponse,
    NextQuestionResponse,
    SubmitAnswerResponse,
)
from app.services.completion import CompletionService
from app.models.completion import (
    CompletionSessionStatus,
    QuestionStatus,
)
from app.services.verification import CaseVerificationService
from app.services.case_builder import CaseBuilderService
from app.services.case_state_machine import (

    CaseStateMachine,
    CaseWorkflowState,
    ReviewReadinessStatus,
)
from app.services.anonymizer import anonymizer
from app.services.ai.gemini_service import ai_service
from app.services.audit import AuditService
from app.services.speech_service import speech_service
from app.services.ocr_service import ocr_service
from app.services.translation_service import translation_service
from app.services.storage import storage_service
from app.services.providers.sarvam_tts import SarvamBulbulAdapter
from app.services.providers.local_fallback import LocalTextToSpeechProvider

logger = logging.getLogger("clinova")
router = APIRouter()


@router.post("", response_model=PatientCaseResponse | CaseResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PatientCaseResponse | CaseResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_triage_case(
    req: CaseCreateRequest,
    request: Request,
    current_user: User = Depends(get_intake_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new multimodal triage case with anonymization and structured decision support."""
    if not req.consent_acknowledged or not req.raw_symptoms.strip():
        raise HTTPException(422, "Consent and a symptom description are required.")
    if req.report_ocr_data:
        for field in req.report_ocr_data:
            field.verification_status = "pending"
    # 1. Anonymize patient reported text
    sanitized_symptoms, was_redacted = anonymizer.sanitize_text(req.raw_symptoms)
    synthetic_case_id = anonymizer.generate_synthetic_case_id()

    # 2. Synthesize structured non-diagnostic triage note
    triage_note = await ai_service.synthesize_triage_note(
        case_id=synthetic_case_id,
        symptoms=sanitized_symptoms,
        speech_transcript=req.speech_transcript,
        report_fields=req.report_ocr_data,
        patient_age=req.approximate_age,
        gender=req.gender,
        facility_type=req.facility_type,
        visit_type=req.visit_type,
    )

    ocr_json = json.dumps([f.model_dump() for f in req.report_ocr_data]) if req.report_ocr_data else None
    vitals_json = json.dumps(req.vitals) if req.vitals else None

    # Determine patient ID (either explicit, or authenticated user if patient)
    resolved_patient_id = req.patient_id
    if not resolved_patient_id and current_user and current_user.role == UserRole.PATIENT:
        resolved_patient_id = current_user.id

    # 3. Create case record
    case = TriageCase(
        owner_user_id=current_user.id,
        synthetic_case_id=synthetic_case_id,
        patient_id=resolved_patient_id,
        language=req.preferred_language,
        facility_type=req.facility_type,
        visit_type=req.visit_type,
        status="awaiting_review",
        case_version=1,
        workflow_state=CaseWorkflowState.INTAKE.value,
        review_readiness_status=ReviewReadinessStatus.READY_FOR_REVIEW.value,
        queue_category=triage_note["queue_category"],
        queue_reason=triage_note["queue_reason"],
        consent_status=req.consent_acknowledged,
        approximate_age=req.approximate_age,
        gender=req.gender,
        context_notes=req.context_notes,
        vitals=vitals_json,
        intake_verified=False,
        raw_symptoms=sanitized_symptoms,
        normalized_symptoms=triage_note["symptom_summary"],
        speech_transcript=req.speech_transcript,
        detected_language=req.detected_language,
        report_filename=req.report_filename,
        report_ocr_data=ocr_json,
        image_reference=req.image_reference,
        triage_summary=json.dumps(triage_note),
        missing_information=json.dumps(triage_note["missing_information"]),
        follow_up_questions=json.dumps(triage_note["follow_up_questions"]),
        risk_signals=json.dumps(triage_note["risk_signals"]),
        timeline_events=json.dumps(triage_note["timeline"]),
    )

    db.add(case)
    await db.commit()
    await db.refresh(case)

    # 3b. Create initial discrete CaseEvidence records
    if req.raw_symptoms:
        symptom_ev = CaseEvidence(
            case_id=case.id,
            encounter_id=case.encounter_id,
            canonical_field="symptom",
            raw_value=req.raw_symptoms,
            normalized_value=sanitized_symptoms,
            source_type=EvidenceSourceType.PATIENT_TEXT,
            verification_state=VerificationState.PATIENT_REPORTED,
            created_by_user_id=current_user.id,
            processor_name="patient_intake",
            version=1,
            is_active=True,
        )
        db.add(symptom_ev)

    if req.speech_transcript:
        voice_ev = CaseEvidence(
            case_id=case.id,
            encounter_id=case.encounter_id,
            canonical_field="speech_transcript",
            raw_value=req.speech_transcript,
            source_type=EvidenceSourceType.PATIENT_VOICE,
            verification_state=VerificationState.PATIENT_REPORTED,
            created_by_user_id=current_user.id,
            processor_name="voice_transcription",
            version=1,
            is_active=True,
        )
        db.add(voice_ev)

    if req.report_filename:
        doc_ev = CaseEvidence(
            case_id=case.id,
            encounter_id=case.encounter_id,
            canonical_field="document_report",
            raw_value=req.report_filename,
            source_type=EvidenceSourceType.DOCUMENT_DERIVED,
            source_reference=req.report_filename,
            verification_state=VerificationState.EXTRACTED_PENDING_VERIFICATION,
            created_by_user_id=current_user.id,
            processor_name="document_intake",
            version=1,
            is_active=True,
        )
        db.add(doc_ev)

    await db.commit()

    # 4. Audit trail logging
    await AuditService.log_event(
        db=db,
        action="CASE_INTAKE_CREATED",
        resource_type="TRIAGE_CASE",
        resource_id=case.synthetic_case_id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=(
            f"Case: {case.synthetic_case_id} | Queue: {case.queue_category.upper()} | "
            f"PatientID: {case.patient_id or 'Anonymous'} | Redacted: {was_redacted}"
        ),
    )

    return patient_case_response(case) if current_user.role == UserRole.PATIENT else _format_case_response(case)


@router.get("", response_model=List[CaseResponse])
@router.get("/", response_model=List[CaseResponse], include_in_schema=False)
async def list_cases(
    queue_category: Optional[str] = Query(None, description="urgent-review, priority, routine"),
    status_filter: Optional[str] = Query(None, description="awaiting_review, in_review, ready_for_doctor, approved, rejected, referred"),
    assigned_doctor_id: Optional[str] = Query(None, description="Filter by assigned clinician ID"),
    patient_id: Optional[str] = Query(None, description="Filter by patient record ID"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_clinician),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve prioritized queue of triage cases with backend role isolation."""
    stmt = select(TriageCase).where(TriageCase.is_deleted == False)

    if patient_id:
        stmt = stmt.where(TriageCase.patient_id == patient_id)

    if assigned_doctor_id:
        stmt = stmt.where(TriageCase.assigned_doctor_id == assigned_doctor_id)
    if queue_category:
        stmt = stmt.where(TriageCase.queue_category == queue_category)
    if status_filter:
        stmt = stmt.where(TriageCase.status == status_filter)

    # Sort: Most recently created first
    stmt = stmt.order_by(desc(TriageCase.created_at)).limit(limit)
    cases = (await db.execute(stmt)).scalars().all()

    return [_format_case_response(c) for c in cases]


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    current_user: User = Depends(get_current_clinician),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve single case by ID or synthetic_case_id with patient isolation checks."""
    stmt = select(TriageCase).where(
        (TriageCase.id == case_id) | (TriageCase.synthetic_case_id == case_id),
        TriageCase.is_deleted == False,
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Triage case not found.")

    # Patient role check
    if current_user and current_user.role == UserRole.PATIENT:
        if case.patient_id and case.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to another patient's triage case.",
            )

    return _format_case_response(case)


@router.post("/{case_id}/assign", response_model=CaseResponse)
async def assign_case(
    case_id: str,
    req: CaseAssignRequest,
    request: Request,
    current_user: User = Depends(get_current_clinician),
    db: AsyncSession = Depends(get_db),
):
    """Staff/Admin: Assign patient case to a doctor and department."""
    stmt = select(TriageCase).where(
        (TriageCase.id == case_id) | (TriageCase.synthetic_case_id == case_id),
        TriageCase.is_deleted == False,
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Triage case not found.")

    if req.assigned_doctor_id:
        case.assigned_doctor_id = req.assigned_doctor_id
    if req.assigned_doctor_name:
        case.assigned_doctor_name = req.assigned_doctor_name
    if req.assigned_department:
        case.assigned_department = req.assigned_department
    if req.priority_category:
        case.queue_category = req.priority_category
    if req.notes:
        existing_notes = case.reviewer_notes or ""
        case.reviewer_notes = f"{existing_notes}\n[Staff Routing]: {req.notes}".strip()

    case.status = "ready_for_doctor"
    await db.commit()
    await db.refresh(case)

    await AuditService.log_event(
        db=db,
        action="CASE_ASSIGNED",
        resource_type="TRIAGE_CASE",
        resource_id=case.synthetic_case_id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=(
            f"Assigned by {current_user.full_name} to Doctor: {case.assigned_doctor_name or case.assigned_doctor_id} "
            f"| Dept: {case.assigned_department}"
        ),
    )

    return _format_case_response(case)


@router.post("/{case_id}/verify-intake", response_model=CaseResponse)
async def verify_case_intake(
    case_id: str,
    req: CaseVerifyIntakeRequest,
    request: Request,
    current_user: User = Depends(get_current_clinician),
    db: AsyncSession = Depends(get_db),
):
    """Staff: Verify patient reported intake, record baseline vitals, and hand off to doctor queue."""
    stmt = select(TriageCase).where(
        (TriageCase.id == case_id) | (TriageCase.synthetic_case_id == case_id),
        TriageCase.is_deleted == False,
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Triage case not found.")

    case.intake_verified = req.verified
    if req.vitals:
        # Merge existing vitals if present
        existing_vitals = json.loads(case.vitals) if case.vitals else {}
        existing_vitals.update(req.vitals)
        case.vitals = json.dumps(existing_vitals)

    if req.staff_notes:
        existing_notes = case.reviewer_notes or ""
        case.reviewer_notes = f"{existing_notes}\n[Staff Verification]: {req.staff_notes}".strip()

    if req.route_to_doctor_id:
        case.assigned_doctor_id = req.route_to_doctor_id
    if req.route_to_doctor_name:
        case.assigned_doctor_name = req.route_to_doctor_name
    if req.route_to_department:
        case.assigned_department = req.route_to_department

    case.status = "ready_for_doctor"
    await db.commit()
    await db.refresh(case)

    await AuditService.log_event(
        db=db,
        action="CASE_INTAKE_VERIFIED",
        resource_type="TRIAGE_CASE",
        resource_id=case.synthetic_case_id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=f"Intake verified by {current_user.full_name} ({current_user.role}). Status: ready_for_doctor",
    )

    return _format_case_response(case)


@router.delete("/{case_id}")
async def delete_case_data(
    case_id: str,
    request: Request,
    current_user: User = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Data retention: delete temporary media and anonymize/purge case record."""
    stmt = select(TriageCase).where(
        (TriageCase.id == case_id) | (TriageCase.synthetic_case_id == case_id)
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    case.is_deleted = True
    case.raw_symptoms = "[DELETED PER RETENTION POLICY]"
    case.speech_transcript = None
    case.report_ocr_data = None
    case.status = "deleted"
    case.normalized_symptoms = None
    case.context_notes = None
    case.triage_summary = None
    case.missing_information = None
    case.follow_up_questions = None
    case.risk_signals = None
    case.timeline_events = None
    case.report_filename = None
    case.image_reference = None
    case.referral_note = None
    case.reviewer_notes = None
    await db.commit()

    await AuditService.log_event(
        db=db,
        action="CASE_DATA_DELETED",
        resource_type="TRIAGE_CASE",
        resource_id=case.synthetic_case_id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=f"Permanent deletion of temporary media & symptoms for {case.synthetic_case_id}",
    )

    return {
        "status": "success",
        "case_id": case.synthetic_case_id,
        "message": "Temporary media and intake symptoms purged successfully per privacy policy.",
    }


def _format_case_response(c: TriageCase) -> CaseResponse:
    """Helper to deserialize JSON fields and compute wait time."""
    now = datetime.now(timezone.utc)
    created = c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else c.created_at
    waiting_mins = max(0, int((now - created).total_seconds() / 60))

    return CaseResponse(
        id=c.id,
        synthetic_case_id=c.synthetic_case_id,
        patient_id=c.patient_id,
        language=c.language,
        facility_type=c.facility_type,
        visit_type=c.visit_type,
        status=c.status,
        queue_category=c.queue_category,
        queue_reason=c.queue_reason,
        consent_status=c.consent_status,
        approximate_age=c.approximate_age,
        gender=c.gender,
        context_notes=c.context_notes,
        raw_symptoms=c.raw_symptoms,
        normalized_symptoms=c.normalized_symptoms,
        speech_transcript=c.speech_transcript,
        detected_language=c.detected_language,
        report_filename=c.report_filename,
        report_ocr_data=json.loads(c.report_ocr_data) if c.report_ocr_data else None,
        image_reference=c.image_reference,
        triage_summary=json.loads(c.triage_summary) if c.triage_summary else None,
        missing_information=json.loads(c.missing_information) if c.missing_information else None,
        follow_up_questions=json.loads(c.follow_up_questions) if c.follow_up_questions else None,
        risk_signals=json.loads(c.risk_signals) if c.risk_signals else None,
        timeline_events=json.loads(c.timeline_events) if c.timeline_events else None,
        vitals=json.loads(c.vitals) if c.vitals else None,
        intake_verified=c.intake_verified,
        assigned_doctor_id=c.assigned_doctor_id,
        assigned_doctor_name=c.assigned_doctor_name,
        assigned_department=c.assigned_department,
        reviewer_notes=c.reviewer_notes,
        reviewer_id=c.reviewer_id,
        reviewer_name=c.reviewer_name,
        reviewed_at=c.reviewed_at,
        approved_at=c.approved_at,
        created_at=c.created_at,
        updated_at=c.updated_at,
        waiting_minutes=waiting_mins,
        is_deleted=c.is_deleted,
    )


async def _get_case_or_404(case_id: str, db: AsyncSession, current_user: User) -> TriageCase:
    """Retrieve case by ID or synthetic_case_id with strict server-side IDOR / RBAC checks."""
    stmt = (
        select(TriageCase)
        .where(
            (TriageCase.id == case_id)
            | (TriageCase.synthetic_case_id == case_id)
        )
        .where(TriageCase.is_deleted == False)
    )
    res = await db.execute(stmt)
    case = res.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    # RBAC & IDOR check: Patients can only access their own case
    if current_user.role == UserRole.PATIENT:
        is_owner = (case.owner_user_id == current_user.id)
        is_patient_match = (case.patient_id == current_user.id)
        if not (is_owner or is_patient_match):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to view or modify this case.",
            )

    return case


@router.post("/{case_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def add_case_evidence(
    case_id: str,
    req: EvidenceCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a discrete, source-tracked evidence item to the Canonical Patient Case."""
    case = await _get_case_or_404(case_id, db, current_user)

    # Inspect existing active evidence for this canonical field to manage versioning & conflicts
    stmt = (
        select(CaseEvidence)
        .where(CaseEvidence.case_id == case.id)
        .where(CaseEvidence.canonical_field == req.canonical_field)
        .where(CaseEvidence.is_active == True)
    )
    res = await db.execute(stmt)
    existing_items = list(res.scalars().all())

    version = 1
    if existing_items:
        version = max(e.version for e in existing_items) + 1
        for old_item in existing_items:
            # Check for conflicting values
            if old_item.raw_value.strip().lower() != req.raw_value.strip().lower():
                if req.source_type == EvidenceSourceType.CLINICIAN_ENTERED or req.verification_state == VerificationState.CLINICIAN_CONFIRMED:
                    # Clinician amendment supersedes previous without destroying historical provenance
                    old_item.verification_state = VerificationState.SUPERSEDED
                else:
                    # Contradictory evidence: preserve both and mark disputed
                    old_item.verification_state = VerificationState.DISPUTED_CONFLICTING
                    req.verification_state = VerificationState.DISPUTED_CONFLICTING

    # Cardinal Rule: AI/OCR extractions cannot automatically be staff or clinician verified
    if req.source_type in [EvidenceSourceType.AI_EXTRACTED, EvidenceSourceType.OCR_DERIVED, EvidenceSourceType.DOCUMENT_DERIVED]:
        if req.verification_state in [VerificationState.STAFF_VERIFIED, VerificationState.CLINICIAN_CONFIRMED]:
            req.verification_state = VerificationState.EXTRACTED_PENDING_VERIFICATION

    evidence = CaseEvidence(
        case_id=case.id,
        encounter_id=case.encounter_id,
        canonical_field=req.canonical_field,
        raw_value=req.raw_value,
        normalized_value=req.normalized_value,
        source_type=req.source_type,
        source_reference=req.source_reference,
        verification_state=req.verification_state,
        confidence_score=req.confidence_score,
        observed_at=req.observed_at,
        created_by_user_id=current_user.id,
        processor_name=req.processor_name,
        version=version,
        is_active=True,
    )
    db.add(evidence)
    case.case_version += 1
    case.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(evidence)

    await AuditService.log_event(
        db=db,
        action="EVIDENCE_ADDED",
        resource_type="CASE_EVIDENCE",
        resource_id=evidence.id,
        user=current_user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        details=(
            f"Evidence added to case {case.synthetic_case_id} | field: {evidence.canonical_field} | "
            f"source: {evidence.source_type.value} | status: {evidence.verification_state.value}"
        ),
    )

    return evidence


@router.get("/{case_id}/evidence", response_model=List[EvidenceResponse])
async def list_case_evidence(
    case_id: str,
    include_superseded: bool = Query(True, description="Whether to include superseded/historical items"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all evidence items for a case with provenance and verification history."""
    case = await _get_case_or_404(case_id, db, current_user)
    stmt = select(CaseEvidence).where(CaseEvidence.case_id == case.id)
    if not include_superseded:
        stmt = stmt.where(CaseEvidence.is_active == True).where(CaseEvidence.verification_state != VerificationState.SUPERSEDED)
    stmt = stmt.order_by(CaseEvidence.created_at.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/{case_id}/transition", response_model=CaseTransitionResponse)
async def transition_case_state(
    case_id: str,
    req: CaseTransitionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transition the Canonical Patient Case through its permitted lifecycle states."""
    case = await _get_case_or_404(case_id, db, current_user)
    prev_state = case.workflow_state

    updated_case = await CaseStateMachine.transition(
        case=case,
        target_state=req.target_state,
        actor=current_user,
        db=db,
        reason=req.reason,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    await db.commit()
    await db.refresh(updated_case)

    return CaseTransitionResponse(
        case_id=updated_case.id,
        synthetic_case_id=updated_case.synthetic_case_id,
        previous_state=prev_state,
        current_state=updated_case.workflow_state,
        case_version=updated_case.case_version,
        updated_at=updated_case.updated_at,
    )


@router.get("/{case_id}/readiness", response_model=ReviewReadinessResponse)
async def get_case_readiness(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate Review Readiness Index for clinical triage."""
    case = await _get_case_or_404(case_id, db, current_user)
    stmt = select(CaseEvidence).where(CaseEvidence.case_id == case.id).where(CaseEvidence.is_active == True)
    res = await db.execute(stmt)
    evidence_items = list(res.scalars().all())
    readiness = CaseStateMachine.evaluate_review_readiness(case, evidence_items)
    return readiness


@router.get("/{case_id}/canonical", response_model=CanonicalCaseResponse)
async def get_canonical_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full Canonical Patient Case with structured timeline and attached evidence items."""
    case = await _get_case_or_404(case_id, db, current_user)
    stmt = select(CaseEvidence).where(CaseEvidence.case_id == case.id).order_by(CaseEvidence.created_at.asc())
    res = await db.execute(stmt)
    evidence_items = list(res.scalars().all())

    builder_service = CaseBuilderService()
    current_snapshot = await builder_service.get_current_snapshot(case.id, db)

    resp = CanonicalCaseResponse(
        id=case.id,
        synthetic_case_id=case.synthetic_case_id,
        owner_user_id=case.owner_user_id,
        patient_id=case.patient_id,
        facility_id=case.facility_id,
        encounter_id=case.encounter_id,
        language=case.language,
        facility_type=case.facility_type,
        visit_type=case.visit_type,
        status=case.status,
        workflow_state=case.workflow_state,
        case_version=case.case_version,
        review_readiness_status=case.review_readiness_status,
        queue_category=case.queue_category,
        queue_reason=case.queue_reason,
        consent_status=case.consent_status,
        raw_symptoms=case.raw_symptoms,
        normalized_symptoms=case.normalized_symptoms,
        created_at=case.created_at,
        updated_at=case.updated_at,
        evidence_items=evidence_items,
        current_snapshot=current_snapshot,
    )
    return resp


@router.post("/{case_id}/text", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def ingest_case_text(
    case_id: str,
    payload: CaseTextInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ingests patient typed symptom text into the Canonical Patient Case."""
    case = await _get_case_or_404(case_id, db, current_user)
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text symptom cannot be empty.")

    evidence = CaseEvidence(
        case_id=case.id,
        canonical_field=payload.field_name,
        raw_value=payload.text.strip(),
        source_type=EvidenceSourceType.PATIENT_TEXT,
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=1.0,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="patient_text_input",
    )
    db.add(evidence)

    # Record processing job telemetry
    job = MultimodalProcessingRecord(
        case_id=case.id,
        capability="text_intake",
        modality="text",
        provider_name="direct_intake",
        status="completed",
        output_evidence_id=evidence.id,
    )
    db.add(job)

    # Update case raw symptoms if unset
    if not case.raw_symptoms:
        case.raw_symptoms = payload.text.strip()
    if case.workflow_state == CaseWorkflowState.CREATED.value:
        case.workflow_state = CaseWorkflowState.INTAKE.value

    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.post("/{case_id}/audio", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def ingest_case_audio(
    case_id: str,
    file: UploadFile = File(...),
    language_hint: str = Form("en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ingests patient voice audio, validates, creates source evidence, and runs Sarvam STT."""
    case = await _get_case_or_404(case_id, db, current_user)
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file cannot be empty.")

    raw_filename = file.filename or "recording.wav"
    # Save audio file to secure local object store
    storage_key = storage_service.generate_storage_key(
        document_id=case.id,
        original_filename=raw_filename,
        patient_id=case.patient_id,
        facility_id=case.facility_id,
        version=1,
    )
    storage_service.save_file(storage_key, audio_bytes)

    # 1. Create SOURCE audio evidence first (source preserved even if STT fails)
    source_evidence = CaseEvidence(
        case_id=case.id,
        canonical_field="raw_voice_recording",
        raw_value=storage_key,
        source_type=EvidenceSourceType.PATIENT_VOICE,
        source_reference=storage_key,
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=1.0,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="audio_recorder",
    )
    db.add(source_evidence)
    await db.flush()

    # 2. Transcribe audio using Sarvam Saaras adapter
    transcribe_res = await speech_service.transcribe_audio(
        audio_bytes=audio_bytes,
        filename=raw_filename,
        language_hint=language_hint,
    )

    # 3. Create DERIVED transcript evidence pointing to source audio
    derived_evidence = CaseEvidence(
        case_id=case.id,
        canonical_field="reported_symptoms",
        raw_value=transcribe_res.transcript or "[Audio captured — pending review]",
        normalized_value=transcribe_res.detected_language,
        source_type=EvidenceSourceType.PATIENT_VOICE,
        source_reference=source_evidence.id,
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=transcribe_res.confidence,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="sarvam_saaras_v4",
    )
    db.add(derived_evidence)

    # 4. Record processing job record
    job = MultimodalProcessingRecord(
        case_id=case.id,
        capability="speech_to_text",
        modality="voice",
        provider_name="sarvam_saaras_v4",
        status="completed" if transcribe_res.transcript else "partial",
        source_reference=source_evidence.id,
        output_evidence_id=derived_evidence.id,
    )
    db.add(job)

    if not case.raw_symptoms and transcribe_res.transcript:
        case.raw_symptoms = transcribe_res.transcript
    if case.workflow_state == CaseWorkflowState.CREATED.value:
        case.workflow_state = CaseWorkflowState.INTAKE.value

    await db.commit()
    await db.refresh(derived_evidence)
    return derived_evidence


@router.post("/{case_id}/documents", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def ingest_case_document(
    case_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Uploads medical document/PDF, runs local PDF extraction or OCR.Space, and attaches to case."""
    case = await _get_case_or_404(case_id, db, current_user)
    raw_filename = file.filename or "uploaded_report.pdf"
    claimed_mime = file.content_type or "application/pdf"
    file_bytes = await file.read()

    safe_filename, final_mime, checksum, scan_result = storage_service.validate_and_process_upload(
        filename=raw_filename,
        file_bytes=file_bytes,
        claimed_mime=claimed_mime,
    )

    storage_key = storage_service.generate_storage_key(
        document_id=case.id,
        original_filename=safe_filename,
        patient_id=case.patient_id,
        facility_id=case.facility_id,
        version=1,
    )
    storage_service.save_file(storage_key, file_bytes)

    # 1. Create SOURCE document evidence
    source_evidence = CaseEvidence(
        case_id=case.id,
        canonical_field="medical_document_source",
        raw_value=storage_key,
        source_type=EvidenceSourceType.DOCUMENT_DERIVED,
        source_reference=storage_key,
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=1.0,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="document_uploader",
    )
    db.add(source_evidence)
    await db.flush()

    # 2. Run OCR / Local PDF parser
    ocr_result = await ocr_service.process_report(file_bytes=file_bytes, filename=safe_filename)

    # 3. Create DERIVED OCR evidence pointing to source document
    derived_evidence = CaseEvidence(
        case_id=case.id,
        canonical_field="extracted_lab_report",
        raw_value=ocr_result.raw_extracted_text or "[Document received — text extraction pending]",
        normalized_value=json.dumps([f.model_dump() for f in ocr_result.fields]) if ocr_result.fields else None,
        source_type=EvidenceSourceType.OCR_DERIVED,
        source_reference=source_evidence.id,
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=ocr_result.confidence_average,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="ocr_space_v1",
    )
    db.add(derived_evidence)

    # 4. Record processing job
    job = MultimodalProcessingRecord(
        case_id=case.id,
        capability="ocr",
        modality="document",
        provider_name="ocr_space_v1",
        status="completed" if ocr_result.status == "success" else "failed",
        source_reference=source_evidence.id,
        output_evidence_id=derived_evidence.id,
    )
    db.add(job)

    await db.commit()
    await db.refresh(derived_evidence)
    return derived_evidence


@router.post("/{case_id}/translate", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def translate_case_evidence(
    case_id: str,
    payload: CaseTranslateInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Translates symptom evidence (e.g. Odia/Hindi to English) via Sarvam Mayura and attaches derived evidence."""
    case = await _get_case_or_404(case_id, db, current_user)
    text_to_translate = payload.text
    source_ref = payload.source_evidence_id

    if not text_to_translate and payload.source_evidence_id:
        # Retrieve source evidence
        stmt = select(CaseEvidence).where(CaseEvidence.id == payload.source_evidence_id)
        src_ev = (await db.execute(stmt)).scalar_one_or_none()
        if src_ev:
            text_to_translate = src_ev.raw_value

    if not text_to_translate or not text_to_translate.strip():
        raise HTTPException(status_code=400, detail="Text to translate cannot be empty.")

    trans_res = await translation_service.translate_and_normalize(
        text=text_to_translate,
        source_language=payload.source_language,
    )

    derived_evidence = CaseEvidence(
        case_id=case.id,
        canonical_field="symptoms_english_translation",
        raw_value=trans_res.translated_text,
        normalized_value=trans_res.normalization_summary,
        source_type=EvidenceSourceType.PATIENT_TEXT,
        source_reference=source_ref or "direct_text",
        verification_state=VerificationState.UNVERIFIED,
        confidence_score=0.95,
        observed_at=datetime.now(timezone.utc),
        created_by_user_id=current_user.id,
        processor_name="sarvam_mayura_v1",
    )
    db.add(derived_evidence)

    job = MultimodalProcessingRecord(
        case_id=case.id,
        capability="translation",
        modality="text",
        provider_name="sarvam_mayura_v1",
        status="completed",
        source_reference=source_ref,
        output_evidence_id=derived_evidence.id,
    )
    db.add(job)

    await db.commit()
    await db.refresh(derived_evidence)
    return derived_evidence


@router.post("/{case_id}/tts")
async def synthesize_case_speech(
    case_id: str,
    payload: CaseTTSInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Synthesizes speech audio for patient explanations via Sarvam Bulbul adapter."""
    await _get_case_or_404(case_id, db, current_user)
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text for TTS cannot be empty.")

    local_tts = LocalTextToSpeechProvider()
    bulbul_adapter = SarvamBulbulAdapter(fallback_provider=local_tts)
    audio_bytes, _ = await bulbul_adapter.synthesize(text=payload.text, language=payload.language)

    return Response(content=audio_bytes, media_type="audio/wav")


@router.get("/{case_id}/processing", response_model=List[ProcessingRecordResponse])
async def list_processing_records(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all multimodal processing job telemetry and provenance records for a case."""
    case = await _get_case_or_404(case_id, db, current_user)
    stmt = (
        select(MultimodalProcessingRecord)
        .where(MultimodalProcessingRecord.case_id == case.id)
        .order_by(MultimodalProcessingRecord.created_at.desc())
    )
    res = await db.execute(stmt)
    records = list(res.scalars().all())
    return records


@router.post("/{case_id}/build", response_model=CaseSnapshotResponse, status_code=status.HTTP_200_OK)
async def build_case_intelligence(
    case_id: str,
    payload: Optional[CaseBuildRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes the Canonical Patient Case Intelligence Builder.
    
    Extracts facts, normalizes clinical terminology, links multi-source evidence,
    constructs chronological timeline, and compiles an immutable CaseSnapshot.
    """
    case = await _get_case_or_404(case_id, db, current_user)
    req = payload or CaseBuildRequest()
    builder = CaseBuilderService()
    try:
        snapshot, _ = await builder.build_canonical_case(
            case_id=case.id,
            db=db,
            trigger_type=req.trigger_type,
            force_rebuild=req.force_rebuild,
            include_inactive_evidence=req.include_inactive_evidence,
        )
        return snapshot
    except Exception as e:
        logger.error(f"Case build failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Canonical case build failed: {str(e)}",
        )


@router.get("/{case_id}/snapshots", response_model=List[CaseSnapshotResponse])
async def list_case_snapshots(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all immutable snapshots generated for a canonical patient case."""
    case = await _get_case_or_404(case_id, db, current_user)
    builder = CaseBuilderService()
    snapshots = await builder.list_snapshots(case.id, db)
    return snapshots


@router.get("/{case_id}/snapshots/{version}", response_model=CaseSnapshotResponse)
async def get_case_snapshot_by_version(
    case_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a specific immutable snapshot of a case by version."""
    case = await _get_case_or_404(case_id, db, current_user)
    builder = CaseBuilderService()
    snapshot = await builder.get_snapshot_by_version(case.id, version, db)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot version {version} not found for case {case.id}",
        )
    return snapshot


@router.get("/{case_id}/builds", response_model=List[CaseBuildRunResponse])
async def list_case_build_runs(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the history of all builder executions and latencies for a case."""
    case = await _get_case_or_404(case_id, db, current_user)
    builder = CaseBuilderService()
    runs = await builder.list_build_runs(case.id, db)
    return runs


# ============================================================================
# PHASE 4: CLINICAL INFORMATION VERIFICATION & REVIEW READINESS ENDPOINTS
# ============================================================================

@router.post("/{case_id}/verify", response_model=VerificationRunResponse, status_code=status.HTTP_200_OK)
async def verify_canonical_case(
    case_id: str,
    request: Request,
    payload: Optional[VerifyCaseRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes the Phase 4 Clinical Information Verification Engine.
    
    Determines completeness, detects cross-source and cross-modal conflicts, checks temporal
    integrity, validates provenance, assesses clinical uncertainty, and evaluates review readiness.
    """
    case = await _get_case_or_404(case_id, db, current_user)
    req = payload or VerifyCaseRequest()
    verifier = CaseVerificationService()
    try:
        run = await verifier.verify_case(
            case_id=case.id,
            db=db,
            actor=current_user,
            force_reverify=req.force_reverify,
            include_ai_checks=req.include_ai_checks,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        return run
    except Exception as e:
        logger.error(f"Case verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical information verification failed: {str(e)}",
        )


@router.get("/{case_id}/verification", response_model=VerificationRunResponse)
async def get_latest_case_verification(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the latest verification run for a case, including stale-version detection."""
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    run = await verifier.get_latest_verification(case.id, db)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification run found for case {case.id}. Please execute verification first.",
        )
    return run


@router.get("/{case_id}/verification/runs", response_model=List[VerificationRunResponse])
async def list_case_verification_runs(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all historical verification executions and telemetry for a case."""
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    runs = await verifier.list_verification_runs(case.id, db)
    return runs


@router.get("/{case_id}/verification/runs/{run_id}", response_model=VerificationRunResponse)
async def get_case_verification_run_by_id(
    case_id: str,
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a specific verification run by ID."""
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    run = await verifier.get_verification_run(run_id, db)
    if not run or run.case_id != case.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification run '{run_id}' not found for case {case.id}.",
        )
    return run


@router.get("/{case_id}/verification/findings", response_model=List[VerificationFindingResponse])
async def list_case_verification_findings(
    case_id: str,
    run_id: Optional[str] = Query(None, description="Filter findings by verification run ID"),
    severity: Optional[str] = Query(None, description="Filter findings by severity (BLOCKING, HIGH, MEDIUM, LOW, INFO)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (UNRESOLVED, RESOLVED_BY_HUMAN_VERIFICATION)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves verification findings for a case with optional severity and status filters."""
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    findings = await verifier.list_findings(
        case_id=case.id,
        db=db,
        run_id=run_id,
        severity=severity,
        status=status_filter,
        category=category,
    )
    return findings


@router.post(
    "/{case_id}/verification/findings/{finding_id}/resolve",
    response_model=VerificationFindingResponse,
)
async def resolve_verification_finding(
    case_id: str,
    finding_id: str,
    payload: ResolveFindingRequest,
    request: Request,
    current_user: User = Depends(get_current_clinician),
    db: AsyncSession = Depends(get_db),
):
    """Allows an authorized clinician or staff member to resolve a verification finding.
    
    Preserves historical conflict data while marking the finding resolved with explicit clinical notes.
    """
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    try:
        updated = await verifier.resolve_finding(
            case_id=case.id,
            finding_id=finding_id,
            resolution_state=payload.resolution_state,
            resolution_notes=payload.resolution_notes,
            actor=current_user,
            db=db,
            ip_address=get_client_ip(request),
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to resolve finding: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve verification finding: {str(e)}",
        )


@router.get("/{case_id}/review-readiness", response_model=ReviewReadinessSummaryResponse)
async def get_case_review_readiness(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves an explainable Review Readiness summary for a case.
    
    Provides information package readiness for professional review. Not a medical diagnostic score.
    """
    case = await _get_case_or_404(case_id, db, current_user)
    verifier = CaseVerificationService()
    run = await verifier.get_latest_verification(case.id, db)

    if not run:
        return ReviewReadinessSummaryResponse(
            case_id=case.id,
            case_version=case.case_version,
            verified_case_version=None,
            review_readiness_status=ReviewReadinessStatus.NOT_READY.value,
            review_readiness_score=0.0,
            review_readiness_reasons=["Verification has not been executed for this case yet."],
            is_stale=False,
            blocking_count=0,
            unresolved_count=0,
            completeness_status="UNKNOWN",
            consistency_status="UNKNOWN",
            temporal_status="UNKNOWN",
            provenance_status="UNKNOWN",
            uncertainty_status="UNKNOWN",
            last_verified_at=None,
        )

    return ReviewReadinessSummaryResponse(
        case_id=case.id,
        case_version=case.case_version,
        verified_case_version=run.case_version,
        review_readiness_status=run.review_readiness_status,
        review_readiness_score=run.review_readiness_score,
        review_readiness_reasons=run.review_readiness_reasons,
        is_stale=run.is_stale,
        blocking_count=run.blocking_findings_count,
        unresolved_count=run.unresolved_findings_count,
        completeness_status=run.completeness_status,
        consistency_status=run.consistency_status,
        temporal_status=run.temporal_status,
        provenance_status=run.provenance_status,
        uncertainty_status=run.uncertainty_status,
        last_verified_at=run.completed_at or run.started_at,
    )


# ============================================================================
# PHASE 5: INTELLIGENT INFORMATION COMPLETION & ADAPTIVE INTERVIEW ENDPOINTS
# ============================================================================

@router.post(
    "/{case_id}/completion/start",
    response_model=CompletionSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def start_completion_session(
    case_id: str,
    payload: Optional[StartCompletionSessionRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Starts or resumes a patient intelligent completion interview session."""
    case = await _get_case_or_404(case_id, db, current_user)
    req = payload or StartCompletionSessionRequest()
    service = CompletionService()
    session = await service.get_or_create_session(
        case_id=case.id,
        db=db,
        max_turns=req.max_turns or 5,
        force_new=req.force_new,
    )
    await db.commit()
    full_session = await service.get_session_status(case.id, db)
    return full_session or session


@router.get(
    "/{case_id}/completion/session",
    response_model=CompletionSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_completion_session(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current completion session state and full interview question history."""
    case = await _get_case_or_404(case_id, db, current_user)
    service = CompletionService()
    session = await service.get_session_status(case.id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No completion session found for case {case.id}. Please start a session first.",
        )
    return session


@router.get(
    "/{case_id}/completion/next-question",
    response_model=NextQuestionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_next_completion_question(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves next pending or freshly generated completion question for the patient."""
    case = await _get_case_or_404(case_id, db, current_user)
    service = CompletionService()
    session, question = await service.get_or_generate_next_question(case.id, db)
    await db.commit()
    is_complete = session.status in (
        CompletionSessionStatus.COMPLETED.value,
        CompletionSessionStatus.STOPPED_MAX_TURNS.value,
        CompletionSessionStatus.STOPPED_NO_GAPS.value,
        CompletionSessionStatus.STOPPED_PATIENT_DECLINED.value,
        CompletionSessionStatus.STOPPED_ZERO_GAIN.value,
        CompletionSessionStatus.STOPPED_SAFETY_LIMIT.value,
        CompletionSessionStatus.FAILED.value,
        CompletionSessionStatus.ABORTED.value,
    )
    return NextQuestionResponse(
        session_id=session.id,
        case_id=session.case_id,
        turn_number=session.current_turn,
        max_turns=session.max_turns,
        is_complete=is_complete,
        stopping_reason=session.stopping_reason,
        stopping_criterion=session.stopping_criterion,
        question=question,
        remaining_gaps_count=session.remaining_gap_count,
        current_readiness_score=session.current_readiness_score,
    )


@router.post(
    "/{case_id}/completion/questions/{question_id}/answer",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_completion_answer(
    case_id: str,
    question_id: str,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submits patient answer, creates evidence, rebuilds case, reverifies, and computes next turn."""
    case = await _get_case_or_404(case_id, db, current_user)
    service = CompletionService()
    try:
        result = await service.submit_answer(
            case_id=case.id,
            question_id=question_id,
            raw_answer_text=payload.raw_answer_text,
            db=db,
            modality=payload.modality or "patient_text",
            is_skipped=payload.is_skipped,
            structured_payload=payload.structured_payload,
            actor=current_user,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting completion answer: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process answer and rebuild case: {str(e)}",
        )


@router.post(
    "/{case_id}/completion/questions/{question_id}/skip",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def skip_completion_question(
    case_id: str,
    question_id: str,
    payload: Optional[SkipQuestionRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Records that the patient chose to skip or decline answering this question."""
    case = await _get_case_or_404(case_id, db, current_user)
    req = payload or SkipQuestionRequest()
    service = CompletionService()
    try:
        result = await service.submit_answer(
            case_id=case.id,
            question_id=question_id,
            raw_answer_text=f"Skipped: {req.reason or 'patient_declined'}",
            db=db,
            modality="declined_or_skipped",
            is_skipped=True,
            structured_payload={"skipped": True, "reason": req.reason},
            actor=current_user,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{case_id}/completion/complete",
    response_model=CompletionSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_completion_session_early(
    case_id: str,
    payload: Optional[CompleteSessionRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allows patient or clinician to explicitly conclude the completion interview."""
    case = await _get_case_or_404(case_id, db, current_user)
    req = payload or CompleteSessionRequest()
    service = CompletionService()
    session = await service.complete_session_manually(
        case_id=case.id,
        reason=req.reason or "patient_concluded",
        db=db,
    )
    full_session = await service.get_session_status(case.id, db)
    return full_session or session
