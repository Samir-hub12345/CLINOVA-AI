"""CLINOVA AI — Core Foundation Endpoints.

Continuous Care Intelligence System.
Phase 13: Core Backend Foundation, Master Case Persistence & API Layer.
Grounded in Section 20 of Master Specification.

Implements Authoritative API Endpoints:
- Patients (/patients)
- Encounters (/encounters)
- Master Cases (/cases)
- Evidence & Provenance (/cases/{case_id}/evidence)
- Vitals (/cases/{case_id}/vitals)
- Timeline (/cases/{case_id}/timeline)
- Consents (/cases/{case_id}/consent)
- Follow-ups (/cases/{case_id}/follow-up)
- Triage Notes (/cases/{case_id}/triage-note)
- Human Review Actions (/cases/{case_id}/review-actions)
- State Transitions (/cases/{case_id}/transitions)
- Audit Trail (/cases/{case_id}/audit)
"""

import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import (
    Patient,
    PatientIdentifier,
    Encounter,
    Case,
    CaseStateTransition,
    Consent,
    Evidence,
    Vital,
    TimelineEvent,
    FollowUpQuestion,
    FollowUpAnswer,
    TriageNote,
    ReviewAction,
    AuditEvent,
    Facility,
    EvidenceRecord,
    VitalReading,
    TriageSnapshotRecord,
    utc_now,
)
from app.core.auth import (
    get_current_actor,
    ActorContext,
    require_role,
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_FACILITY_ADMIN,
    ROLE_AUDITOR,
    ROLE_SYSTEM,
)
from app.core.rbac import (
    Permission,
    has_permission,
    check_role_permission,
)
from app.core.policy import (
    authorize_case_access,
    authorize_facility_access,
    validate_review_action_safety,
    validate_state_transition_safety,
    record_security_audit_event,
)
from app.core.errors import ClinovaAPIError
from app.domain.state_machine import execute_state_transition
from app.schemas.foundation import (
    PatientCreate,
    PatientRead,
    PatientIdentifierCreate,
    PatientIdentifierRead,
    EncounterCreate,
    EncounterRead,
    CaseCreate,
    CaseRead,
    StateTransitionRequest,
    StateTransitionRead,
    EvidenceCreate,
    EvidenceRead,
    VitalCreate,
    VitalRead,
    TimelineEventCreate,
    TimelineEventRead,
    ConsentCreate,
    ConsentRead,
    FollowUpQuestionCreate,
    FollowUpQuestionRead,
    FollowUpAnswerCreate,
    FollowUpAnswerRead,
    TriageNoteCreate,
    TriageNoteRead,
    ReviewActionCreate,
    ReviewActionRead,
    AuditEventRead,
)
from app.schemas.triage import (
    VitalLatestRead,
    TriageSnapshotRead,
    CasePriorityRead,
)
from app.domain.triage import (
    compute_deterministic_triage,
    evaluate_vital_freshness,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Patient Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/patients",
    response_model=PatientRead,
    summary="Create Patient",
    description="Registers a patient context with synthetic-safe identifier and demographic metadata.",
    tags=["Patients"],
)
async def create_patient(
    req: PatientCreate,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    patient_id = str(uuid.uuid4())
    if req.synthetic_id:
        existing = await db.execute(select(Patient).where(Patient.synthetic_id == req.synthetic_id))
        if existing.scalars().first():
            raise ClinovaAPIError(
                category="CONFLICT",
                message=f"Patient with synthetic ID '{req.synthetic_id}' already exists.",
                status_code=409,
            )
        synth_id = req.synthetic_id
    else:
        while True:
            synth_id = f"PT-SYN-{random.randint(1000, 99999)}"
            existing = await db.execute(select(Patient).where(Patient.synthetic_id == synth_id))
            if not existing.scalars().first():
                break

    patient = Patient(
        id=patient_id,
        synthetic_id=synth_id,
        age_bracket=req.age_bracket,
        biological_sex=req.biological_sex,
        is_synthetic=req.is_synthetic,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(patient)

    # Add primary synthetic identifier
    ident = PatientIdentifier(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        identifier_type="SYNTHETIC_ID",
        identifier_value=synth_id,
        is_primary=True,
        created_at=utc_now(),
    )
    db.add(ident)

    # Audit event
    audit = AuditEvent(
        case_id=None,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="patient.created",
        object_type="PATIENT",
        object_id=patient_id,
        result="SUCCESS",
        details={"synthetic_id": synth_id, "age_bracket": req.age_bracket},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(patient)
    return patient


@router.get(
    "/patients/{patient_id}",
    response_model=PatientRead,
    summary="Get Patient",
    description="Retrieves registered patient demographic information.",
    tags=["Patients"],
)
async def get_patient(
    patient_id: str = Path(..., description="Internal Patient UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Patient '{patient_id}' not found.",
            status_code=404,
        )
    return patient


# ---------------------------------------------------------------------------
# 2. Encounter Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/encounters",
    response_model=EncounterRead,
    summary="Create Encounter",
    description="Initializes a clinical encounter linking a patient to a healthcare facility.",
    tags=["Encounters"],
)
async def create_encounter(
    req: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    patient = await db.get(Patient, req.patient_id)
    if not patient:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Referenced patient '{req.patient_id}' does not exist.",
            status_code=404,
        )

    facility = await db.get(Facility, req.facility_id)
    if not facility:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Referenced facility '{req.facility_id}' does not exist.",
            status_code=404,
        )

    encounter_id = str(uuid.uuid4())
    started_at = req.started_at or utc_now()
    encounter = Encounter(
        id=encounter_id,
        patient_id=req.patient_id,
        facility_id=req.facility_id,
        environment=req.environment,
        pathway=req.pathway,
        source_actor_id=req.source_actor_id or actor.actor_id,
        source_actor_role=req.source_actor_role or actor.role,
        started_at=started_at,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(encounter)

    audit = AuditEvent(
        case_id=None,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="encounter.created",
        object_type="ENCOUNTER",
        object_id=encounter_id,
        result="SUCCESS",
        details={"patient_id": req.patient_id, "facility_id": req.facility_id},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(encounter)
    return encounter


@router.get(
    "/encounters/{encounter_id}",
    response_model=EncounterRead,
    summary="Get Encounter",
    description="Retrieves encounter record by UUID.",
    tags=["Encounters"],
)
async def get_encounter(
    encounter_id: str = Path(..., description="Internal Encounter UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    encounter = await db.get(Encounter, encounter_id)
    if not encounter:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Encounter '{encounter_id}' not found.",
            status_code=404,
        )
    return encounter


# ---------------------------------------------------------------------------
# 3. Canonical Master Case Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases",
    response_model=CaseRead,
    summary="Create Master Case",
    description="Establishes the single canonical Master Case root aggregate for an encounter.",
    tags=["Cases"],
)
async def create_case(
    req: CaseCreate,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    # RBAC Permission check
    check_role_permission(actor.role, Permission.CASE_CREATE)

    # Facility scope check
    await authorize_facility_access(req.facility_id, actor, db=db)

    # Patient self-scope check: patients may only create cases for their own identity
    if actor.is_patient():
        if not actor.patient_id or req.patient_id != actor.patient_id:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.patient_scope_denied",
                object_type="PATIENT",
                object_id=req.patient_id,
                result="DENIED",
                details={
                    "reason": "Patients may only submit intake for themselves",
                    "actor_patient_id": actor.patient_id,
                    "target_patient_id": req.patient_id,
                },
            )
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message="Patients are only authorized to create cases for their own identity.",
                status_code=403,
            )

    # Verify Patient
    patient = await db.get(Patient, req.patient_id)
    if not patient:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Patient '{req.patient_id}' not found.",
            status_code=404,
        )

    # Verify Facility
    facility = await db.get(Facility, req.facility_id)
    if not facility:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Facility '{req.facility_id}' not found.",
            status_code=404,
        )

    # Encounter resolution
    encounter_id = req.encounter_id
    if encounter_id:
        encounter = await db.get(Encounter, encounter_id)
        if not encounter:
            raise ClinovaAPIError(
                category="NOT_FOUND",
                message=f"Encounter '{encounter_id}' not found.",
                status_code=404,
            )
    else:
        # Implicit atomic encounter creation if not specified
        encounter_id = str(uuid.uuid4())
        encounter = Encounter(
            id=encounter_id,
            patient_id=req.patient_id,
            facility_id=req.facility_id,
            environment=req.environment_id,
            pathway=req.pathway,
            source_actor_id=actor.actor_id,
            source_actor_role=actor.role,
            started_at=utc_now(),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(encounter)

    case_id = str(uuid.uuid4())
    case_num = f"CAS-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:8].upper()}"

    case = Case(
        id=case_id,
        case_number=case_num,
        patient_id=req.patient_id,
        encounter_id=encounter_id,
        facility_id=req.facility_id,
        pathway=req.pathway,
        current_state="INTAKE_RECORDED",
        status="NEW",
        acuity_tier=req.acuity_tier.upper(),
        state_version=1,
        environment_id=req.environment_id,
        presenting_complaint=req.presenting_complaint,
        primary_syndrome=req.primary_syndrome,
        required_bundle=req.required_bundle,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(case)

    # Initial state transition record
    transition = CaseStateTransition(
        id=str(uuid.uuid4()),
        case_id=case_id,
        from_state="NONE",
        to_state="INTAKE_RECORDED",
        actor_id=actor.actor_id,
        actor_role=actor.role,
        reason="Case initial creation and intake recording",
        state_version=1,
        created_at=utc_now(),
    )
    db.add(transition)

    # Audit event
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="case.created",
        object_type="CASE",
        object_id=case_id,
        result="SUCCESS",
        details={
            "case_number": case_num,
            "patient_id": req.patient_id,
            "facility_id": req.facility_id,
            "acuity_tier": req.acuity_tier,
        },
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(case)
    return case


@router.get(
    "/cases",
    response_model=List[CaseRead],
    summary="List Master Cases",
    description="Returns cases filtered by acuity, current state, or facility.",
    tags=["Cases"],
)
async def list_cases(
    acuity: Optional[str] = Query(None, description="ROUTINE, MODERATE, URGENT, CRITICAL"),
    state: Optional[str] = Query(None, description="Current workflow state"),
    facility_id: Optional[str] = Query(None, description="Facility ID filter"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    check_role_permission(actor.role, Permission.CASE_LIST)
    if facility_id:
        await authorize_facility_access(facility_id, actor, db=db)

    stmt = select(Case)
    # Server-side facility & patient scoping
    if not actor.is_system_admin() and not actor.is_auditor() and not actor.is_patient():
        if actor.facility_id:
            stmt = stmt.where(Case.facility_id == actor.facility_id)
    if actor.is_patient():
        if not actor.patient_id:
            return []
        stmt = stmt.where(Case.patient_id == actor.patient_id)

    if acuity:
        stmt = stmt.where(Case.acuity_tier == acuity.upper())
    if state:
        stmt = stmt.where(Case.current_state == state.upper())
    if facility_id:
        stmt = stmt.where(Case.facility_id == facility_id)
    stmt = stmt.order_by(desc(Case.created_at)).limit(limit)

    res = await db.execute(stmt)
    return res.scalars().all()


@router.get(
    "/cases/{case_id}",
    response_model=CaseRead,
    summary="Get Master Case",
    description="Retrieves the canonical Master Case aggregate root by UUID.",
    tags=["Cases"],
)
async def get_case(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)
    return case


# ---------------------------------------------------------------------------
# 4. Evidence & Provenance Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/evidence",
    response_model=EvidenceRead,
    summary="Add Case Evidence",
    description="Appends an immutable clinical evidence observation with strict epistemic and provenance tracking.",
    tags=["Evidence"],
)
async def add_case_evidence(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: EvidenceCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.EVIDENCE_ADD, db=db)

    # Invariant: Never convert INFERRED -> VERIFIED without an explicit human verification action by a clinician
    epistemic_state = req.epistemic_state.upper()
    if epistemic_state == "VERIFIED" and not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Evidence can only be marked as VERIFIED by a licensed clinician.",
            status_code=403,
        )

    ev_id = str(uuid.uuid4())
    prov_meta = req.provenance_metadata or {}
    prov_meta.setdefault("submitted_by", actor.actor_id)
    prov_meta.setdefault("actor_role", actor.role)

    evidence = Evidence(
        id=ev_id,
        case_id=case_id,
        source_class=req.source_class.upper(),
        epistemic_state=epistemic_state,
        parameter_name=req.parameter_name,
        content_value=req.content_value,
        unit=req.unit,
        confidence_score=req.confidence_score,
        source_timestamp=req.source_timestamp,
        captured_timestamp=utc_now(),
        provenance_metadata=prov_meta,
        verification_metadata=req.verification_metadata or {},
        transformation_metadata=req.transformation_metadata or {},
        created_at=utc_now(),
    )
    db.add(evidence)

    # Also record in evidence_records for upstream backward compatibility
    compat_record = EvidenceRecord(
        id=str(uuid.uuid4()),
        case_id=case_id,
        provenance_type=req.source_class.upper(),
        extracted_payload={req.parameter_name: req.content_value, "unit": req.unit},
        confidence_score=req.confidence_score,
        verification_status="CONFIRMED" if epistemic_state == "VERIFIED" else "UNVERIFIED",
        verified_by=actor.actor_id if epistemic_state == "VERIFIED" else None,
        created_at=utc_now(),
    )
    db.add(compat_record)

    # Audit event
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="evidence.created",
        object_type="EVIDENCE",
        object_id=ev_id,
        result="SUCCESS",
        details={
            "parameter_name": req.parameter_name,
            "source_class": req.source_class,
            "epistemic_state": epistemic_state,
        },
        created_at=utc_now(),
    )
    db.add(audit)

    case.updated_at = utc_now()
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.get(
    "/cases/{case_id}/evidence",
    response_model=List[EvidenceRead],
    summary="Get Case Evidence",
    description="Retrieves all discrete evidence items persisted for a case.",
    tags=["Evidence"],
)
async def get_case_evidence(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(Evidence).where(Evidence.case_id == case_id).order_by(Evidence.created_at)
    res = await db.execute(stmt)
    return res.scalars().all()


def record_triage_audit_events(
    db: AsyncSession,
    case_id: str,
    actor: ActorContext,
    snapshot: Dict[str, Any],
    snapshot_record_id: str,
    prev_priority: Optional[str],
    now: datetime,
) -> None:
    """Emits Phase 16 auditable events for deterministic triage triggers and changes."""
    if prev_priority and prev_priority != snapshot.get("priority_tier"):
        db.add(AuditEvent(
            case_id=case_id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="triage.priority_changed",
            object_type="TRIAGE_SNAPSHOT",
            object_id=snapshot_record_id,
            result="SUCCESS",
            details={"previous_priority": prev_priority, "new_priority": snapshot.get("priority_tier")},
            created_at=now,
        ))

    for rf in snapshot.get("red_flags", []):
        if rf.get("triggered"):
            db.add(AuditEvent(
                case_id=case_id,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="triage.red_flag_triggered",
                object_type="RED_FLAG",
                object_id=rf.get("rule_id"),
                result="SUCCESS",
                details={"rule_name": rf.get("name"), "severity": rf.get("severity"), "explanation": rf.get("explanation")},
                created_at=now,
            ))

    if snapshot.get("missing_critical_vitals"):
        db.add(AuditEvent(
            case_id=case_id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="triage.missing_vital_detected",
            object_type="TRIAGE",
            object_id=case_id,
            result="SUCCESS",
            details={"missing_critical_vitals": snapshot.get("missing_critical_vitals")},
            created_at=now,
        ))

    v_status = snapshot.get("vitals_overall_status")
    if v_status in ["STALE", "EXPIRED"]:
        db.add(AuditEvent(
            case_id=case_id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="triage.stale_vital_detected",
            object_type="TRIAGE",
            object_id=case_id,
            result="SUCCESS",
            details={"freshness_status": v_status, "age_minutes": snapshot.get("vital_age_minutes")},
            created_at=now,
        ))


# ---------------------------------------------------------------------------
# 5. Vitals Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/vitals",
    response_model=VitalRead,
    summary="Record Vitals",
    description="Appends verified or staff-entered physiological vitals with structural range enforcement.",
    tags=["Vitals"],
)
async def record_case_vitals(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: VitalCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.VITALS_RECORD, db=db)

    vital_id = str(uuid.uuid4())
    recorded_at = req.recorded_at or utc_now()

    source = (req.source or "STAFF_ENTERED").strip().upper()
    prov_meta = dict(req.provenance_metadata or {})
    prov_meta.setdefault("recorded_by", actor.actor_id)
    prov_meta.setdefault("actor_role", actor.role)
    prov_meta.setdefault("source", source)
    if case.encounter_id:
        prov_meta.setdefault("encounter_id", case.encounter_id)

    if source in ["PATIENT_REPORTED", "DEVICE_DERIVED"]:
        verif_context = {
            "verified": False,
            "verification_status": "UNVERIFIED",
            "source_type": source,
        }
    else:
        is_clinician = actor.role in ["CLINICIAN", "DOCTOR"]
        verif_context = {
            "verified": is_clinician,
            "verification_status": "CLINICIAN_VERIFIED" if is_clinician else "STAFF_RECORDED",
            "verified_by": actor.actor_id if is_clinician else None,
            "role": actor.role,
        }

    vital = Vital(
        id=vital_id,
        case_id=case_id,
        heart_rate=req.heart_rate,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        spo2_percent=req.spo2_percent,
        respiratory_rate=req.respiratory_rate,
        temperature_celsius=req.temperature_celsius,
        avpu_score=req.avpu_score or "ALERT",
        supplemental_o2=req.supplemental_o2,
        source=source,
        recorded_at=recorded_at,
        provenance_metadata=prov_meta,
        verification_context=verif_context,
        created_at=utc_now(),
    )
    db.add(vital)

    # Maintain upstream vital_readings compatibility
    compat_reading = VitalReading(
        id=str(uuid.uuid4()),
        case_id=case_id,
        heart_rate=req.heart_rate,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        spo2_percent=req.spo2_percent,
        respiratory_rate=req.respiratory_rate,
        temperature_celsius=req.temperature_celsius,
        avpu_score=req.avpu_score or "ALERT",
        recorded_at=recorded_at,
    )
    db.add(compat_reading)

    # Add milestone event to timeline
    v_desc = []
    if req.heart_rate:
        v_desc.append(f"HR: {req.heart_rate} bpm")
    if req.systolic_bp:
        v_desc.append(f"BP: {req.systolic_bp}/{req.diastolic_bp or '--'} mmHg")
    if req.spo2_percent:
        v_desc.append(f"SpO2: {req.spo2_percent}%")

    timeline_event = TimelineEvent(
        id=str(uuid.uuid4()),
        case_id=case_id,
        event_type="VITALS_RECORDED",
        event_title="Point-of-Care Vitals Acquired",
        event_content=", ".join(v_desc) or "Serial vitals recorded",
        event_timestamp=recorded_at,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        provenance_metadata={"vital_id": vital_id},
        created_at=utc_now(),
    )
    db.add(timeline_event)

    # Audit event
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="vital.created",
        object_type="VITAL",
        object_id=vital_id,
        result="SUCCESS",
        details={"summary": ", ".join(v_desc)},
        created_at=utc_now(),
    )
    db.add(audit)

    # Recompute and persist deterministic triage snapshot
    now = utc_now()
    prev_snap_stmt = (
        select(TriageSnapshotRecord)
        .where(TriageSnapshotRecord.case_id == case_id)
        .order_by(TriageSnapshotRecord.calculated_at.desc())
    )
    prev_snap = (await db.execute(prev_snap_stmt)).scalars().first()
    prev_priority = prev_snap.priority_tier if prev_snap else None

    snapshot = compute_deterministic_triage(
        case_id=case_id,
        pathway=case.pathway,
        current_state=case.current_state,
        presenting_complaint=case.presenting_complaint,
        latest_vital=vital,
        now=now,
    )
    case.acuity_tier = snapshot["acuity_tier"]
    case.risk_score = snapshot["risk_score"]
    case.uncertainty_score = snapshot["uncertainty_score"]
    case.updated_at = now

    snapshot_record = TriageSnapshotRecord(
        id=str(uuid.uuid4()),
        case_id=case_id,
        vital_id=vital_id,
        priority_tier=snapshot["priority_tier"],
        acuity_tier=snapshot["acuity_tier"],
        risk_score=snapshot["risk_score"],
        uncertainty_score=snapshot["uncertainty_score"],
        news2_score=snapshot["news2"].get("score"),
        shock_index=snapshot["shock_index"].get("score"),
        has_critical_red_flags=snapshot["has_critical_red_flags"],
        snapshot_data=snapshot,
        ruleset_version=snapshot["ruleset_version"],
        calculated_at=now,
    )
    db.add(snapshot_record)

    record_triage_audit_events(
        db=db,
        case_id=case_id,
        actor=actor,
        snapshot=snapshot,
        snapshot_record_id=snapshot_record.id,
        prev_priority=prev_priority,
        now=now,
    )

    await db.commit()
    await db.refresh(vital)
    return vital


@router.get(
    "/cases/{case_id}/vitals",
    response_model=List[VitalRead],
    summary="Get Case Vitals",
    description="Retrieves chronological series of vital sign readings for a case.",
    tags=["Vitals"],
)
async def get_case_vitals(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(Vital).where(Vital.case_id == case_id).order_by(Vital.recorded_at)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get(
    "/cases/{case_id}/vitals/latest",
    response_model=VitalLatestRead,
    summary="Get Latest Case Vitals with Freshness Evaluation",
    description="Retrieves the most recent vital observation for a case along with parameter freshness metrics.",
    tags=["Vitals"],
)
async def get_case_latest_vitals(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(Vital).where(Vital.case_id == case_id).order_by(Vital.recorded_at.desc())
    latest_vital = (await db.execute(stmt)).scalars().first()

    if not latest_vital:
        freshness_res = evaluate_vital_freshness(None, {})
        return VitalLatestRead(
            vital=None,
            freshness_by_parameter=freshness_res["freshness_by_parameter"],
            overall_status=freshness_res["overall_status"],
            age_minutes=None,
            recorded_at=None,
        )

    vital_dict = {
        "heart_rate": latest_vital.heart_rate,
        "systolic_bp": latest_vital.systolic_bp,
        "diastolic_bp": latest_vital.diastolic_bp,
        "spo2_percent": latest_vital.spo2_percent,
        "respiratory_rate": latest_vital.respiratory_rate,
        "temperature_celsius": latest_vital.temperature_celsius,
        "avpu_score": latest_vital.avpu_score,
    }
    freshness_res = evaluate_vital_freshness(latest_vital.recorded_at, vital_dict)
    return VitalLatestRead(
        vital=latest_vital,
        freshness_by_parameter=freshness_res["freshness_by_parameter"],
        overall_status=freshness_res["overall_status"],
        age_minutes=freshness_res["age_minutes"],
        recorded_at=latest_vital.recorded_at,
    )


@router.post(
    "/cases/{case_id}/triage/calculate",
    response_model=TriageSnapshotRead,
    summary="Execute Deterministic Triage Calculation",
    description="Calculates deterministic NEWS2, Shock Index, red flags, uncertainty, and queue priority.",
    tags=["Triage"],
)
async def calculate_case_triage(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to execute operational triage calculations.",
            status_code=403,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    # Fetch previous snapshot to detect priority change
    prev_snap_stmt = (
        select(TriageSnapshotRecord)
        .where(TriageSnapshotRecord.case_id == case_id)
        .order_by(TriageSnapshotRecord.calculated_at.desc())
    )
    prev_snap = (await db.execute(prev_snap_stmt)).scalars().first()
    prev_priority = prev_snap.priority_tier if prev_snap else None

    # Fetch latest vital observation
    v_stmt = select(Vital).where(Vital.case_id == case_id).order_by(Vital.recorded_at.desc())
    latest_vital = (await db.execute(v_stmt)).scalars().first()

    now = utc_now()
    snapshot = compute_deterministic_triage(
        case_id=case.id,
        pathway=case.pathway,
        current_state=case.current_state,
        presenting_complaint=case.presenting_complaint,
        latest_vital=latest_vital,
        now=now,
    )

    # Update canonical Case operational acuity & risk
    case.acuity_tier = snapshot["acuity_tier"]
    case.risk_score = snapshot["risk_score"]
    case.uncertainty_score = snapshot["uncertainty_score"]
    case.updated_at = now

    # Persist immutable historical triage snapshot
    snapshot_record = TriageSnapshotRecord(
        id=str(uuid.uuid4()),
        case_id=case.id,
        vital_id=snapshot.get("vital_id"),
        priority_tier=snapshot["priority_tier"],
        acuity_tier=snapshot["acuity_tier"],
        risk_score=snapshot["risk_score"],
        uncertainty_score=snapshot["uncertainty_score"],
        news2_score=snapshot["news2"].get("score"),
        shock_index=snapshot["shock_index"].get("score"),
        has_critical_red_flags=snapshot["has_critical_red_flags"],
        snapshot_data=snapshot,
        ruleset_version=snapshot["ruleset_version"],
        calculated_at=now,
    )
    db.add(snapshot_record)

    # Audit event
    audit = AuditEvent(
        case_id=case.id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="triage.calculated",
        object_type="TRIAGE_SNAPSHOT",
        object_id=snapshot_record.id,
        result="SUCCESS",
        details={
            "priority_tier": snapshot["priority_tier"],
            "acuity_tier": snapshot["acuity_tier"],
            "news2_score": snapshot["news2"].get("score"),
            "has_critical_red_flags": snapshot["has_critical_red_flags"],
        },
        created_at=now,
    )
    db.add(audit)

    record_triage_audit_events(
        db=db,
        case_id=case.id,
        actor=actor,
        snapshot=snapshot,
        snapshot_record_id=snapshot_record.id,
        prev_priority=prev_priority,
        now=now,
    )

    await db.commit()
    return snapshot


@router.get(
    "/cases/{case_id}/triage/snapshot",
    response_model=TriageSnapshotRead,
    summary="Get Latest Deterministic Triage Snapshot",
    description="Retrieves the current authoritative deterministic triage snapshot for a case.",
    tags=["Triage"],
)
async def get_case_triage_snapshot(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    # Query latest persisted snapshot
    stmt = (
        select(TriageSnapshotRecord)
        .where(TriageSnapshotRecord.case_id == case_id)
        .order_by(TriageSnapshotRecord.calculated_at.desc())
    )
    latest_snap = (await db.execute(stmt)).scalars().first()

    if latest_snap and latest_snap.snapshot_data:
        return latest_snap.snapshot_data

    # If no snapshot yet, compute deterministically on the fly
    v_stmt = select(Vital).where(Vital.case_id == case_id).order_by(Vital.recorded_at.desc())
    latest_vital = (await db.execute(v_stmt)).scalars().first()

    return compute_deterministic_triage(
        case_id=case.id,
        pathway=case.pathway,
        current_state=case.current_state,
        presenting_complaint=case.presenting_complaint,
        latest_vital=latest_vital,
    )


@router.get(
    "/cases/{case_id}/priority",
    response_model=CasePriorityRead,
    summary="Get Case Operational Priority Breakdown",
    description="Returns priority tier, triggering rules, physiological indicators, missing data, and uncertainty.",
    tags=["Triage"],
)
async def get_case_priority_breakdown(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    # Fetch latest snapshot or compute
    stmt = (
        select(TriageSnapshotRecord)
        .where(TriageSnapshotRecord.case_id == case_id)
        .order_by(TriageSnapshotRecord.calculated_at.desc())
    )
    latest_snap = (await db.execute(stmt)).scalars().first()

    if latest_snap and latest_snap.snapshot_data:
        snap_data = latest_snap.snapshot_data
    else:
        v_stmt = select(Vital).where(Vital.case_id == case_id).order_by(Vital.recorded_at.desc())
        latest_vital = (await db.execute(v_stmt)).scalars().first()
        snap_data = compute_deterministic_triage(
            case_id=case.id,
            pathway=case.pathway,
            current_state=case.current_state,
            presenting_complaint=case.presenting_complaint,
            latest_vital=latest_vital,
        )

    triggering_rules = [
        rf["rule_id"] for rf in snap_data.get("red_flags", []) if rf.get("triggered")
    ]
    calc_at = snap_data.get("calculated_at")
    if isinstance(calc_at, str):
        calc_at = datetime.fromisoformat(calc_at)

    return CasePriorityRead(
        case_id=case.id,
        priority_tier=snap_data.get("priority_tier", "P4_ROUTINE"),
        acuity_tier=snap_data.get("acuity_tier", case.acuity_tier),
        risk_score=snap_data.get("risk_score", case.risk_score),
        uncertainty_score=snap_data.get("uncertainty_score", case.uncertainty_score),
        pathway=case.pathway,
        has_critical_red_flags=snap_data.get("has_critical_red_flags", False),
        triggering_rules=triggering_rules,
        priority_reasons=snap_data.get("priority_reasons", []),
        physiological_indicators={
            "vitals_summary": snap_data.get("vitals_summary", {}),
            "news2": snap_data.get("news2", {}),
            "shock_index": snap_data.get("shock_index", {}),
        },
        missing_critical_vitals=snap_data.get("missing_critical_vitals", []),
        ruleset_version=snap_data.get("ruleset_version", "PRIORITY-RULES-v1.0"),
        calculated_at=calc_at or utc_now(),
    )


# ---------------------------------------------------------------------------
# 6. Timeline Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/cases/{case_id}/timeline",
    response_model=List[TimelineEventRead],
    summary="Get Case Timeline",
    description="Retrieves longitudinal chronological milestones for a case with explicit conflict tracking.",
    tags=["Timeline"],
)
async def get_case_timeline(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(TimelineEvent).where(TimelineEvent.case_id == case_id).order_by(TimelineEvent.event_timestamp)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post(
    "/cases/{case_id}/timeline",
    response_model=TimelineEventRead,
    summary="Add Timeline Event",
    description="Inserts a clinical milestone into the longitudinal timeline.",
    tags=["Timeline"],
)
async def add_timeline_event(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: TimelineEventCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.EVIDENCE_ADD, db=db)

    event_id = str(uuid.uuid4())
    event_ts = req.event_timestamp or utc_now()

    event = TimelineEvent(
        id=event_id,
        case_id=case_id,
        event_type=req.event_type,
        event_title=req.event_title,
        event_content=req.event_content,
        event_timestamp=event_ts,
        source_timestamp=req.source_timestamp,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        evidence_id=req.evidence_id,
        is_conflict=req.is_conflict,
        provenance_metadata=req.provenance_metadata or {},
        created_at=utc_now(),
    )
    db.add(event)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="timeline.created",
        object_type="TIMELINE_EVENT",
        object_id=event_id,
        result="SUCCESS",
        details={"event_type": req.event_type, "event_title": req.event_title},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(event)
    return event


# ---------------------------------------------------------------------------
# 7. Consent Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/consent",
    response_model=ConsentRead,
    summary="Record Case Consent",
    description="Persists or updates informed consent for a clinical case.",
    tags=["Consent"],
)
async def record_case_consent(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ConsentCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_CREATE, db=db)

    existing = (await db.execute(select(Consent).where(Consent.case_id == case_id))).scalars().first()
    if existing:
        existing.purpose = req.purpose
        existing.language = req.language
        existing.channel = req.channel
        existing.consent_version = req.consent_version
        existing.status = req.status
        existing.consent_granted = (req.status != "REVOKED")
        existing.hash_reference = req.hash_reference
        existing.recorded_at = utc_now()
        consent_obj = existing
    else:
        consent_obj = Consent(
            id=str(uuid.uuid4()),
            case_id=case_id,
            purpose=req.purpose,
            language=req.language,
            channel=req.channel,
            consent_version=req.consent_version,
            status=req.status,
            consent_granted=(req.status != "REVOKED"),
            hash_reference=req.hash_reference,
            recorded_at=utc_now(),
            created_at=utc_now(),
        )
        db.add(consent_obj)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="consent.recorded",
        object_type="CONSENT",
        object_id=consent_obj.id,
        result="SUCCESS",
        details={"status": req.status, "purpose": req.purpose, "channel": req.channel},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(consent_obj)
    return consent_obj


@router.get(
    "/cases/{case_id}/consent",
    response_model=ConsentRead,
    summary="Get Case Consent",
    description="Retrieves the consent record for a case.",
    tags=["Consent"],
)
async def get_case_consent(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    consent = (await db.execute(select(Consent).where(Consent.case_id == case_id))).scalars().first()
    if not consent:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Consent record for case '{case_id}' not found.",
            status_code=404,
        )
    return consent


# ---------------------------------------------------------------------------
# 8. Follow-Up Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/follow-up",
    response_model=FollowUpQuestionRead,
    summary="Add Follow-up Question",
    description="Persists a targeted follow-up question to close clinical uncertainty.",
    tags=["Follow-up"],
)
async def create_case_follow_up(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: FollowUpQuestionCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    return await add_follow_up_question(case_id=case_id, req=req, db=db, actor=actor)


@router.post(
    "/cases/{case_id}/follow-up/question",
    response_model=FollowUpQuestionRead,
    summary="Add Follow-up Question",
    description="Persists a targeted follow-up question to close clinical uncertainty.",
    tags=["Follow-up"],
)
async def add_follow_up_question(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: FollowUpQuestionCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.FOLLOW_UP_CREATE, db=db)

    q_id = str(uuid.uuid4())
    question = FollowUpQuestion(
        id=q_id,
        case_id=case_id,
        question_text=req.question_text,
        reason=req.reason,
        priority=req.priority,
        status="PENDING",
        created_at=utc_now(),
    )
    db.add(question)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="follow_up.created",
        object_type="FOLLOW_UP_QUESTION",
        object_id=q_id,
        result="SUCCESS",
        details={"priority": req.priority, "reason": req.reason},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(question)
    return question


@router.post(
    "/cases/{case_id}/follow-up/answer",
    response_model=FollowUpAnswerRead,
    summary="Answer Follow-up Question",
    description="Records a patient or staff response to an outstanding follow-up question.",
    tags=["Follow-up"],
)
async def answer_follow_up(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: FollowUpAnswerCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.FOLLOW_UP_ANSWER, db=db)

    question = await db.get(FollowUpQuestion, req.question_id)
    if not question or question.case_id != case_id:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Question '{req.question_id}' not found for case '{case_id}'.",
            status_code=404,
        )

    ans_id = str(uuid.uuid4())
    answer = FollowUpAnswer(
        id=ans_id,
        question_id=req.question_id,
        case_id=case_id,
        answer_text=req.answer_text,
        answered_by=actor.actor_id,
        answered_at=utc_now(),
        evidence_id=req.evidence_id,
        created_at=utc_now(),
    )
    db.add(answer)

    question.status = "ANSWERED"

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="follow_up.answered",
        object_type="FOLLOW_UP_ANSWER",
        object_id=ans_id,
        result="SUCCESS",
        details={"question_id": req.question_id},
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(answer)
    return answer


@router.get(
    "/cases/{case_id}/follow-up",
    response_model=List[FollowUpQuestionRead],
    summary="Get Case Follow-ups",
    description="Retrieves all follow-up questions for a case.",
    tags=["Follow-up"],
)
async def get_case_follow_ups(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(FollowUpQuestion).where(FollowUpQuestion.case_id == case_id).order_by(FollowUpQuestion.created_at)
    res = await db.execute(stmt)
    return res.scalars().all()


# ---------------------------------------------------------------------------
# 9. Triage Note Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/triage-note",
    response_model=TriageNoteRead,
    summary="Add Triage Note",
    description="Persists structured triage notes, maintaining strict separation between human and AI authorship.",
    tags=["Triage Note"],
)
async def add_triage_note(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: TriageNoteCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.TRIAGE_NOTE_CREATE, db=db)

    note_id = str(uuid.uuid4())
    triage_note = TriageNote(
        id=note_id,
        case_id=case_id,
        author_id=actor.actor_id,
        author_role=actor.role,
        author_type=req.author_type,
        summary=req.summary,
        acuity_assessment=req.acuity_assessment,
        clinical_concerns=req.clinical_concerns,
        suggested_next_steps=req.suggested_next_steps,
        is_ai_generated=req.is_ai_generated,
        created_at=utc_now(),
    )
    db.add(triage_note)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="triage_note.created",
        object_type="TRIAGE_NOTE",
        object_id=note_id,
        result="SUCCESS",
        details={
            "acuity_assessment": req.acuity_assessment,
            "author_type": req.author_type,
            "is_ai_generated": req.is_ai_generated,
        },
        created_at=utc_now(),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(triage_note)
    return triage_note


@router.get(
    "/cases/{case_id}/triage-note",
    response_model=List[TriageNoteRead],
    summary="Get Triage Notes",
    description="Retrieves structured triage notes persisted for a case.",
    tags=["Triage Note"],
)
async def get_triage_notes(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(TriageNote).where(TriageNote.case_id == case_id).order_by(TriageNote.created_at)
    res = await db.execute(stmt)
    return res.scalars().all()


# ---------------------------------------------------------------------------
# 10. Human Review Actions Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/review-actions",
    response_model=ReviewActionRead,
    summary="Submit Human Review Action",
    description="Records binding qualified human review decisions. Strictly rejects prohibited autonomous actions.",
    tags=["Human Review"],
)
async def submit_human_review_action(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ReviewActionCreate = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    # 1. Enforce Server-Side Non-Diagnostic and Vocabulary Boundaries
    await validate_review_action_safety(req.action, actor, case_id=case_id, db=db)

    action_id = str(uuid.uuid4())
    action_upper = req.action.upper()

    # 2. If VERIFY on Evidence, promote epistemic state
    if action_upper == "VERIFY" and req.target_entity_type == "EVIDENCE" and req.target_entity_id:
        ev = await db.get(Evidence, req.target_entity_id)
        if ev and ev.case_id == case_id:
            ev.epistemic_state = "VERIFIED"
            ev.verification_metadata = {
                "verified_by": actor.actor_id,
                "verified_at": utc_now().isoformat(),
                "notes": req.notes,
            }

    # 3. If RESOLVE_CONFLICT, record resolution
    if action_upper == "RESOLVE_CONFLICT":
        audit_conflict = AuditEvent(
            case_id=case_id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="conflict.resolved",
            object_type=req.target_entity_type or "CLINICAL_DATA",
            object_id=req.target_entity_id or case_id,
            result="SUCCESS",
            details={"reason": req.reason, "notes": req.notes},
            created_at=utc_now(),
        )
        db.add(audit_conflict)

    review_action = ReviewAction(
        id=action_id,
        case_id=case_id,
        clinician_id=actor.actor_id,
        action=action_upper,
        target_entity_type=req.target_entity_type,
        target_entity_id=req.target_entity_id,
        original_value=req.original_value,
        updated_value=req.updated_value,
        reason=req.reason,
        notes=req.notes,
        created_at=utc_now(),
    )
    db.add(review_action)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="review_action.created",
        object_type="REVIEW_ACTION",
        object_id=action_id,
        result="SUCCESS",
        details={
            "action": action_upper,
            "target_type": req.target_entity_type,
            "target_id": req.target_entity_id,
        },
        created_at=utc_now(),
    )
    db.add(audit)

    case.updated_at = utc_now()
    await db.commit()
    await db.refresh(review_action)
    return review_action


# ---------------------------------------------------------------------------
# 11. State Transition Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cases/{case_id}/transitions",
    response_model=StateTransitionRead,
    summary="Execute Controlled State Transition",
    description="Advances case through deterministic FSM with optimistic concurrency verification.",
    tags=["State Machine"],
)
async def transition_case_state_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: StateTransitionRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.CLINICAL_STATE_TRANSITION, db=db)
    await validate_state_transition_safety(req.action, actor, case_id=case_id, db=db)

    transition_record = await execute_state_transition(
        case=case,
        action=req.action,
        actor=actor,
        reason=req.reason,
        expected_version=req.expected_state_version,
        db=db,
        metadata=req.transition_metadata,
    )

    await db.commit()
    await db.refresh(transition_record)
    return transition_record


# ---------------------------------------------------------------------------
# 12. Medicolegal Audit Trail Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/cases/{case_id}/audit",
    response_model=List[AuditEventRead],
    summary="Get Case Audit Ledger",
    description="Retrieves immutable medicolegal audit event records for a specific case.",
    tags=["Audit"],
)
async def get_case_audit_trail(
    case_id: str = Path(..., description="Canonical Case UUID"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )
    await authorize_case_access(case, actor, required_permission=Permission.AUDIT_READ, db=db)

    stmt = (
        select(AuditEvent)
        .where(AuditEvent.case_id == case_id)
        .order_by(desc(AuditEvent.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()
