"""CLINOVA AI — Authoritative Human Review & Master Case Lifecycle Endpoints.

Continuous Care Intelligence System.
Phase 17: Human Review + Case State Lifecycle.
Grounded in Section 20, DOC-03, DOC-06, DOC-07, DOC-08, DOC-14.

Endpoints:
- GET /cases/review-queue
- POST /cases/{case_id}/review/start
- GET /cases/{case_id}/review-context
- POST /cases/{case_id}/evidence/{evidence_id}/verify
- POST /cases/{case_id}/evidence/{evidence_id}/modify
- POST /cases/{case_id}/evidence/resolve-conflict
- POST /cases/{case_id}/request-information
- POST /cases/{case_id}/provide-information
- POST /cases/{case_id}/decision
- POST /cases/{case_id}/disposition
- POST /cases/{case_id}/close
- GET /cases/{case_id}/review-history
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import (
    Case,
    Patient,
    Facility,
    Evidence,
    Vital,
    TimelineEvent,
    FollowUpQuestion,
    FollowUpAnswer,
    TriageNote,
    ReviewAction,
    AuditEvent,
    ClinicianDecision,
    CaseOutcome,
    CaseStateTransition,
    utc_now,
)
from app.core.auth import (
    get_current_actor,
    ActorContext,
    ROLE_CLINICIAN,
    ROLE_DOCTOR,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_SYSTEM_ADMIN,
    ROLE_AUDITOR,
)
from app.core.rbac import (
    Permission,
    check_role_permission,
    PROHIBITED_CLINICAL_ACTIONS,
)
from app.core.policy import (
    authorize_case_access,
    authorize_facility_access,
    validate_review_action_safety,
    record_security_audit_event,
)
from app.core.errors import ClinovaAPIError
from app.domain.state_machine import (
    execute_state_transition,
    STATE_INTAKE_RECORDED,
    STATE_TRIAGE_PENDING,
    STATE_TRIAGE_IN_PROGRESS,
    STATE_PENDING_INFORMATION,
    STATE_CLINICIAN_REVIEW_REQUIRED,
    STATE_REVIEW_IN_PROGRESS,
    STATE_DISPOSITION_PENDING,
    STATE_CLOSED,
)
from app.domain.triage import (
    compute_deterministic_triage,
    sort_clinical_queue,
)
from app.domain.review import (
    build_case_review_context,
    detect_evidence_conflicts,
)
from app.schemas.review import (
    ReviewQueueItemRead,
    ReviewQueueResponse,
    StartReviewRequest,
    StartReviewResponse,
    EvidenceVerifyRequest,
    EvidenceModifyRequest,
    EvidenceRejectRequest,
    ConflictResolutionRequest,
    RequestInformationRequest,
    ProvideInformationRequest,
    ClinicalDecisionRequest,
    ClinicalDecisionResponse,
    ClinicalDispositionRequest,
    ClinicalDispositionResponse,
    CaseCloseRequest,
    CaseCloseResponse,
    CaseReviewContextRead,
    CaseReviewHistoryRead,
)
from app.schemas.foundation import EvidenceRead

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Clinician Review Work Queue
# ---------------------------------------------------------------------------

@router.get(
    "/review-queue",
    response_model=ReviewQueueResponse,
    summary="Get Clinician Review Queue",
    description="Returns prioritized cases awaiting or undergoing qualified clinical review.",
    tags=["Human Review"],
)
async def get_clinician_review_queue(
    department: Optional[str] = None,
    acuity: Optional[str] = None,
    status: Optional[str] = None,
    pathway: Optional[str] = None,
    has_red_flags: Optional[bool] = None,
    facility_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    # Patient strictly barred
    if actor.is_patient():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to view the clinician review queue.",
            status_code=403,
        )

    # Cross-facility denial
    if facility_id:
        if actor.role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
            if actor.facility_id and actor.facility_id != facility_id:
                raise ClinovaAPIError(
                    category="NOT_FOUND",
                    message=f"Facility '{facility_id}' not found.",
                    status_code=404,
                )

    # Query cases needing review or in active review
    stmt = (
        select(Case)
        .options(
            selectinload(Case.patient),
            selectinload(Case.facility),
            selectinload(Case.vitals_list),
            selectinload(Case.review_actions_list),
        )
        .where(
            Case.current_state.in_([
                STATE_CLINICIAN_REVIEW_REQUIRED,
                STATE_REVIEW_IN_PROGRESS,
                STATE_DISPOSITION_PENDING,
            ])
        )
    )

    # Enforce facility scoping
    if actor.role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
        if actor.facility_id:
            stmt = stmt.where(Case.facility_id == actor.facility_id)
        else:
            stmt = stmt.where(Case.facility_id == "UNASSIGNED")
    elif facility_id:
        stmt = stmt.where(Case.facility_id == facility_id)

    if acuity:
        stmt = stmt.where(Case.acuity_tier == acuity.upper())
    if status:
        stmt = stmt.where(Case.status == status.upper())
    if pathway:
        stmt = stmt.where(Case.pathway == pathway.upper())

    res = await db.execute(stmt)
    cases = res.scalars().all()

    queue_items: List[Dict[str, Any]] = []
    now = utc_now()

    for c in cases:
        # Dynamic query-time wait calculation
        created_time = c.created_at
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        wait_min = int((now - created_time).total_seconds() / 60.0)

        latest_vital = c.vitals_list[-1] if c.vitals_list else None

        # Compute deterministic triage metrics
        triage_summary = compute_deterministic_triage(
            case_id=c.id,
            pathway=c.pathway,
            current_state=c.current_state,
            presenting_complaint=c.presenting_complaint,
            latest_vital=latest_vital,
            now=now,
        )

        critical_rf_count = sum(
            1 for rf in triage_summary.get("red_flags", []) if rf.get("triggered") and rf.get("severity") == "CRITICAL"
        )
        has_crit_rf = critical_rf_count > 0 or triage_summary.get("has_critical_red_flags", False)

        if has_red_flags is not None:
            if has_red_flags and not has_crit_rf:
                continue
            if not has_red_flags and has_crit_rf:
                continue

        acuity_val = triage_summary.get("acuity_tier", c.acuity_tier or "ROUTINE")
        risk_score_val = triage_summary.get("risk_score", c.risk_score)
        uncertainty_val = triage_summary.get("uncertainty_score", c.uncertainty_score)
        priority_tier_val = triage_summary.get("priority_tier", "P4_ROUTINE")

        sla_limit = 10 if acuity_val == "CRITICAL" else (30 if acuity_val == "URGENT" else (60 if acuity_val == "MODERATE" else 120))
        sla_breached = wait_min > sla_limit
        emergency_active = bool(c.pathway.upper().startswith("EMERGENCY") or has_crit_rf)

        # Review status
        if c.current_state == STATE_CLINICIAN_REVIEW_REQUIRED:
            rev_status = "PENDING_REVIEW"
        elif c.current_state == STATE_REVIEW_IN_PROGRESS:
            rev_status = "IN_REVIEW"
        elif c.current_state == STATE_DISPOSITION_PENDING:
            rev_status = "AWAITING_DISPOSITION"
        else:
            rev_status = "IN_REVIEW"

        assigned_clinician = None
        for ra in reversed(c.review_actions_list):
            if ra.action in {"START_REVIEW", "START_CLINICAL_REVIEW"}:
                assigned_clinician = ra.clinician_id
                break

        queue_items.append({
            "case_id": c.id,
            "case_number": c.case_number,
            "patient_synthetic_id": c.patient.synthetic_id if c.patient else "SYN-PT",
            "age_bracket": c.patient.age_bracket if c.patient else "40-49",
            "biological_sex": c.patient.biological_sex if c.patient else "MALE",
            "facility_id": c.facility_id,
            "facility_name": c.facility.name if c.facility else "Unknown",
            "pathway": c.pathway,
            "current_state": c.current_state,
            "status": c.status,
            "priority_tier": priority_tier_val,
            "acuity_tier": acuity_val,
            "risk_score": risk_score_val,
            "trajectory_slope": c.trajectory_slope,
            "uncertainty_score": uncertainty_val,
            "presenting_complaint": c.presenting_complaint,
            "primary_syndrome": c.primary_syndrome,
            "required_bundle": c.required_bundle,
            "waiting_minutes": wait_min,
            "sla_limit_minutes": sla_limit,
            "sla_breached": sla_breached,
            "emergency_active": emergency_active,
            "has_critical_red_flags": has_crit_rf,
            "critical_red_flags_count": critical_rf_count,
            "news2_score": triage_summary.get("news2", {}).get("score"),
            "shock_index": triage_summary.get("shock_index", {}).get("score"),
            "review_status": rev_status,
            "assigned_clinician_id": assigned_clinician,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat() if c.updated_at else c.created_at.isoformat(),
        })

    sorted_queue = sort_clinical_queue(queue_items, now=now)

    return ReviewQueueResponse(
        total_cases=len(sorted_queue),
        emergency_count=sum(1 for q in sorted_queue if q["emergency_active"]),
        critical_count=sum(1 for q in sorted_queue if q["acuity_tier"] == "CRITICAL"),
        urgent_count=sum(1 for q in sorted_queue if q["acuity_tier"] == "URGENT"),
        moderate_count=sum(1 for q in sorted_queue if q["acuity_tier"] == "MODERATE"),
        routine_count=sum(1 for q in sorted_queue if q["acuity_tier"] == "ROUTINE"),
        queue=[ReviewQueueItemRead(**q) for q in sorted_queue],
        is_synthetic_mode=True,
        generated_at=now.isoformat(),
    )


# ---------------------------------------------------------------------------
# 2. Review Session Start & Context
# ---------------------------------------------------------------------------

@router.post(
    "/{case_id}/review/start",
    response_model=StartReviewResponse,
    summary="Start Clinical Review Session",
    description="Authorized clinician begins review session, advancing case state to REVIEW_IN_PROGRESS.",
    tags=["Human Review"],
)
async def start_clinical_review(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: StartReviewRequest = StartReviewRequest(),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' is not authorized to start clinical review. Licensed clinician required.",
            status_code=403,
            details={"actor_role": actor.role, "required_role": "CLINICIAN"},
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )

    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    # Concurrency verification
    if req.expected_state_version is not None and req.expected_state_version != case.state_version:
        raise ClinovaAPIError(
            category="CONFLICT",
            message=(
                f"Optimistic concurrency conflict on case '{case_id}'. "
                f"Current state version is {case.state_version}, expected {req.expected_state_version}."
            ),
            status_code=409,
            details={"current_state_version": case.state_version, "expected_state_version": req.expected_state_version},
        )

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot start review on a closed case.",
            status_code=422,
        )

    now = utc_now()
    if case.current_state == STATE_CLINICIAN_REVIEW_REQUIRED:
        await execute_state_transition(
            case=case,
            action="START_REVIEW",
            actor=actor,
            reason=req.notes or "Clinician initiated clinical review session",
            expected_version=req.expected_state_version,
            db=db,
            metadata={"reviewer_id": actor.actor_id},
        )
    elif case.current_state == STATE_REVIEW_IN_PROGRESS:
        # Idempotent re-entry
        audit = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            action="review.resumed",
            object_type="CASE",
            object_id=case.id,
            result="SUCCESS",
            details={"notes": req.notes, "state_version": case.state_version},
            created_at=now,
        )
        db.add(audit)
    else:
        # Other permitted transitions into review
        try:
            await execute_state_transition(
                case=case,
                action="START_REVIEW",
                actor=actor,
                reason=req.notes or "Clinician started review",
                expected_version=req.expected_state_version,
                db=db,
                metadata={"reviewer_id": actor.actor_id},
            )
        except ClinovaAPIError:
            raise ClinovaAPIError(
                category="INVALID_STATE_TRANSITION",
                message=f"Cannot start clinical review from current state '{case.current_state}'.",
                status_code=422,
            )

    # Persist ReviewAction for review session start
    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case.id,
        clinician_id=actor.actor_id,
        action="START_REVIEW",
        target_entity_type="CASE",
        target_entity_id=case.id,
        reason=req.notes or "Clinical review initiated",
        notes=req.notes,
        created_at=now,
    )
    db.add(rev_action)

    await db.commit()
    await db.refresh(case)

    return StartReviewResponse(
        case_id=case.id,
        current_state=case.current_state,
        status=case.status,
        state_version=case.state_version,
        reviewer_id=actor.actor_id,
        reviewer_name=actor.username or actor.actor_id,
        started_at=now,
        message="Clinical review session started.",
    )


@router.get(
    "/{case_id}/review-context",
    response_model=CaseReviewContextRead,
    summary="Get Case Review Context",
    description="Retrieves complete case context including deterministic support, evidence, vitals, timeline, and prior actions.",
    tags=["Human Review"],
)
async def get_case_review_context(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if actor.is_patient():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to access clinical review context.",
            status_code=403,
        )

    stmt = (
        select(Case)
        .options(
            selectinload(Case.patient),
            selectinload(Case.facility),
        )
        .where(Case.id == case_id)
    )
    res = await db.execute(stmt)
    case = res.scalars().first()

    if not case:
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Case '{case_id}' not found.",
            status_code=404,
        )

    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    ctx = await build_case_review_context(case=case, db=db)
    return CaseReviewContextRead(**ctx)


# ---------------------------------------------------------------------------
# 3. Evidence Verification, Modification, & Conflict Resolution
# ---------------------------------------------------------------------------

@router.post(
    "/{case_id}/evidence/{evidence_id}/verify",
    response_model=EvidenceRead,
    summary="Verify Clinical Evidence",
    description="Qualified clinician verifies discrete clinical evidence parameter, promoting epistemic status to VERIFIED.",
    tags=["Human Review"],
)
async def verify_evidence_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    evidence_id: str = Path(..., description="Evidence UUID"),
    req: EvidenceVerifyRequest = EvidenceVerifyRequest(),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot verify clinical evidence. Licensed clinician required.",
            status_code=403,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot verify evidence on a closed case.",
            status_code=422,
        )

    evidence = await db.get(Evidence, evidence_id)
    if not evidence or evidence.case_id != case_id:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Evidence '{evidence_id}' not found for case '{case_id}'.", status_code=404)

    await execute_state_transition(
        case=case,
        action="VERIFY",
        actor=actor,
        reason=req.rationale or req.notes or f"Evidence '{evidence.parameter_name}' verified by clinician",
        expected_version=req.expected_state_version,
        db=db,
        metadata={"evidence_id": evidence_id, "parameter_name": evidence.parameter_name},
    )

    now = utc_now()
    evidence.epistemic_state = "VERIFIED"
    evidence.verification_metadata = {
        "verified_by": actor.actor_id,
        "verified_role": actor.role,
        "verified_at": now.isoformat(),
        "notes": req.notes,
        "rationale": req.rationale,
    }

    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case_id,
        clinician_id=actor.actor_id,
        action="VERIFY",
        target_entity_type="EVIDENCE",
        target_entity_id=evidence_id,
        notes=req.notes,
        reason=req.rationale,
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="evidence.verified",
        object_type="EVIDENCE",
        object_id=evidence_id,
        result="SUCCESS",
        details={"parameter_name": evidence.parameter_name, "notes": req.notes},
        created_at=now,
    )
    db.add(audit)

    case.updated_at = now
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.post(
    "/{case_id}/evidence/{evidence_id}/modify",
    response_model=EvidenceRead,
    summary="Modify Clinical Evidence with History Preservation",
    description="Qualified clinician updates discrete evidence value, strictly preserving original values and recording rationale.",
    tags=["Human Review"],
)
async def modify_evidence_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    evidence_id: str = Path(..., description="Evidence UUID"),
    req: EvidenceModifyRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot modify clinical evidence. Licensed clinician required.",
            status_code=403,
        )

    if not req.reason or not req.reason.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory clinical rationale required to modify evidence record.",
            status_code=422,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot modify evidence on a closed case.",
            status_code=422,
        )

    evidence = await db.get(Evidence, evidence_id)
    if not evidence or evidence.case_id != case_id:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Evidence '{evidence_id}' not found for case '{case_id}'.", status_code=404)

    await execute_state_transition(
        case=case,
        action="MODIFY",
        actor=actor,
        reason=req.reason,
        expected_version=req.expected_state_version,
        db=db,
        metadata={"evidence_id": evidence_id, "parameter_name": evidence.parameter_name, "updated_value": req.updated_value},
    )

    now = utc_now()
    old_value = evidence.content_value

    # Append-oriented history preservation
    tf_meta = dict(evidence.transformation_metadata or {})
    mod_hist = list(tf_meta.get("modification_history", []))
    mod_hist.append({
        "modified_at": now.isoformat(),
        "modified_by": actor.actor_id,
        "modified_by_role": actor.role,
        "previous_value": old_value,
        "updated_value": req.updated_value,
        "reason": req.reason,
        "notes": req.notes,
    })
    tf_meta["modification_history"] = mod_hist
    evidence.transformation_metadata = tf_meta

    evidence.content_value = req.updated_value
    evidence.epistemic_state = "VERIFIED"
    evidence.verification_metadata = {
        "modified_and_verified_by": actor.actor_id,
        "modified_at": now.isoformat(),
        "reason": req.reason,
    }

    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case_id,
        clinician_id=actor.actor_id,
        action="MODIFY",
        target_entity_type="EVIDENCE",
        target_entity_id=evidence_id,
        original_value=old_value,
        updated_value=req.updated_value,
        reason=req.reason,
        notes=req.notes,
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="evidence.modified",
        object_type="EVIDENCE",
        object_id=evidence_id,
        result="SUCCESS",
        details={
            "parameter_name": evidence.parameter_name,
            "reason": req.reason,
        },
        created_at=now,
    )
    db.add(audit)

    case.updated_at = now
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.post(
    "/{case_id}/evidence/{evidence_id}/reject",
    response_model=EvidenceRead,
    summary="Reject Clinical Evidence with Rationale",
    description="Qualified clinician rejects discrete clinical evidence item (e.g. erroneous measurement, artifact), recording mandatory clinical rationale.",
    tags=["Human Review"],
)
async def reject_evidence_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    evidence_id: str = Path(..., description="Evidence UUID"),
    req: EvidenceRejectRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot reject clinical evidence. Licensed clinician required.",
            status_code=403,
        )

    if not req.reason or not req.reason.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory clinical rationale required to reject evidence record.",
            status_code=422,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot reject evidence on a closed case.",
            status_code=422,
        )

    evidence = await db.get(Evidence, evidence_id)
    if not evidence or evidence.case_id != case_id:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Evidence '{evidence_id}' not found for case '{case_id}'.", status_code=404)

    await execute_state_transition(
        case=case,
        action="REJECT",
        actor=actor,
        reason=req.reason,
        expected_version=req.expected_state_version,
        db=db,
        metadata={"evidence_id": evidence_id, "parameter_name": evidence.parameter_name},
    )

    now = utc_now()
    evidence.epistemic_state = "REJECTED"
    evidence.verification_metadata = {
        "rejected_by": actor.actor_id,
        "rejected_by_role": actor.role,
        "rejected_at": now.isoformat(),
        "reason": req.reason,
        "notes": req.notes,
    }

    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case_id,
        clinician_id=actor.actor_id,
        action="REJECT",
        target_entity_type="EVIDENCE",
        target_entity_id=evidence_id,
        reason=req.reason,
        notes=req.notes,
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="evidence.rejected",
        object_type="EVIDENCE",
        object_id=evidence_id,
        result="SUCCESS",
        details={
            "parameter_name": evidence.parameter_name,
            "reason": req.reason,
        },
        created_at=now,
    )
    db.add(audit)

    case.updated_at = now
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.post(
    "/{case_id}/evidence/resolve-conflict",
    summary="Resolve Clinical Evidence Conflict",
    description="Explicit clinician resolution of contradictory evidence parameters, designating authoritative record and preserving original evidence.",
    tags=["Human Review"],
)
async def resolve_conflict_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ConflictResolutionRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot resolve evidence conflicts. Licensed clinician required.",
            status_code=403,
        )

    if not req.resolution_rationale or not req.resolution_rationale.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory clinical rationale required to resolve evidence conflicts.",
            status_code=422,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot resolve evidence conflict on a closed case.",
            status_code=422,
        )

    target_ev_id = req.authoritative_evidence_id or req.evidence_id
    if not (target_ev_id or req.parameter_name):
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Conflict resolution requires target evidence ID or parameter name.",
            status_code=422,
        )

    authoritative_ev = None
    if target_ev_id:
        authoritative_ev = await db.get(Evidence, target_ev_id)
        if not authoritative_ev or authoritative_ev.case_id != case_id:
            raise ClinovaAPIError(
                category="NOT_FOUND",
                message=f"Evidence '{target_ev_id}' not found for case '{case_id}'.",
                status_code=404,
            )
        authoritative_ev.epistemic_state = "VERIFIED"
        if req.resolved_value is not None:
            authoritative_ev.content_value = req.resolved_value
        authoritative_ev.verification_metadata = {
            "conflict_resolved_by": actor.actor_id,
            "resolved_at": utc_now().isoformat(),
            "rationale": req.resolution_rationale,
        }

    await execute_state_transition(
        case=case,
        action="RESOLVE_CONFLICT",
        actor=actor,
        reason=req.resolution_rationale,
        expected_version=req.expected_state_version,
        db=db,
        metadata={"authoritative_evidence_id": target_ev_id, "resolved_value": req.resolved_value},
    )

    now = utc_now()

    # Mark other competing items for the same parameter as SUPERSEDED (preserving records)
    param = req.parameter_name or (authoritative_ev.parameter_name if authoritative_ev else None)
    if param:
        stmt = (
            select(Evidence)
            .where(Evidence.case_id == case_id)
            .where(func.lower(Evidence.parameter_name) == param.lower())
        )
        param_items = (await db.execute(stmt)).scalars().all()
        for it in param_items:
            if authoritative_ev and it.id != authoritative_ev.id:
                it.epistemic_state = "SUPERSEDED"
                meta = dict(it.transformation_metadata or {})
                meta["superseded_by"] = authoritative_ev.id
                meta["superseded_reason"] = req.resolution_rationale
                it.transformation_metadata = meta
            elif not authoritative_ev:
                it.epistemic_state = "SUPERSEDED"
                meta = dict(it.transformation_metadata or {})
                meta["superseded_reason"] = req.resolution_rationale
                it.transformation_metadata = meta

        # If no existing evidence was designated as authoritative, but a resolved_value was provided, create an authoritative entry
        if not authoritative_ev and req.resolved_value is not None:
            authoritative_ev = Evidence(
                id=str(uuid.uuid4()),
                case_id=case_id,
                source_class="CLINICIAN_ENTRY",
                epistemic_state="VERIFIED",
                parameter_name=param,
                content_value=req.resolved_value,
                confidence_score=1.0,
                verification_metadata={
                    "conflict_resolved_by": actor.actor_id,
                    "resolved_at": now.isoformat(),
                    "rationale": req.resolution_rationale,
                },
                captured_timestamp=now,
            )
            db.add(authoritative_ev)
            target_ev_id = authoritative_ev.id
    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case_id,
        clinician_id=actor.actor_id,
        action="RESOLVE_CONFLICT",
        target_entity_type="EVIDENCE",
        target_entity_id=target_ev_id or case_id,
        updated_value=req.resolved_value,
        reason=req.resolution_rationale,
        notes=f"Resolved conflict on parameter '{req.parameter_name or (authoritative_ev.parameter_name if authoritative_ev else 'clinical observation')}'.",
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="conflict.resolved",
        object_type="EVIDENCE",
        object_id=target_ev_id or case_id,
        result="SUCCESS",
        details={
            "parameter_name": req.parameter_name or (authoritative_ev.parameter_name if authoritative_ev else None),
            "rationale": req.resolution_rationale,
            "authoritative_evidence_id": target_ev_id,
        },
        created_at=now,
    )
    db.add(audit)

    case.updated_at = now
    await db.commit()

    return {
        "case_id": case_id,
        "authoritative_evidence_id": target_ev_id,
        "resolved_parameter": req.parameter_name or (authoritative_ev.parameter_name if authoritative_ev else None),
        "status": "RESOLVED",
        "rationale": req.resolution_rationale,
        "resolved_at": now.isoformat(),
        "message": "Epistemic conflict explicitly resolved by clinician. Original conflicting evidence preserved.",
    }


# ---------------------------------------------------------------------------
# 4. Information Request & Return Lifecycle
# ---------------------------------------------------------------------------

@router.post(
    "/{case_id}/request-information",
    summary="Request Missing Clinical Information",
    description="Transitions case to PENDING_INFORMATION and logs targeted question.",
    tags=["Human Review"],
)
async def request_information_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: RequestInformationRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not (actor.is_clinician() or actor.is_nurse()):
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot request clinical information.",
            status_code=403,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.FOLLOW_UP_CREATE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot request information on a closed case.",
            status_code=422,
        )

    # Persist FollowUpQuestion
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

    # Transition state to PENDING_INFORMATION
    await execute_state_transition(
        case=case,
        action="REQUEST_INFORMATION",
        actor=actor,
        reason=req.reason,
        expected_version=req.expected_state_version,
        db=db,
        metadata={"question_id": q_id, "target_role": req.target_role},
    )

    await db.commit()
    await db.refresh(case)

    return {
        "case_id": case.id,
        "question_id": q_id,
        "current_state": case.current_state,
        "state_version": case.state_version,
        "question_text": req.question_text,
        "priority": req.priority,
        "status": "PENDING_INFORMATION",
        "message": "Missing information requested. Case transitioned to PENDING_INFORMATION.",
    }


@router.post(
    "/{case_id}/provide-information",
    summary="Provide Missing Clinical Information",
    description="Submits missing information answer and returns case to active clinician review or triage.",
    tags=["Human Review"],
)
async def provide_information_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ProvideInformationRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.FOLLOW_UP_ANSWER, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot provide information on a closed case.",
            status_code=422,
        )

    # If specific question ID provided, answer it
    if req.question_id:
        question = await db.get(FollowUpQuestion, req.question_id)
        if question and question.case_id == case_id:
            question.status = "ANSWERED"
            ans = FollowUpAnswer(
                id=str(uuid.uuid4()),
                question_id=req.question_id,
                case_id=case_id,
                answer_text=req.answer_text,
                answered_by=actor.actor_id,
                answered_at=utc_now(),
                evidence_id=req.evidence_id,
                created_at=utc_now(),
            )
            db.add(ans)

    # Transition from PENDING_INFORMATION back
    if case.current_state == STATE_PENDING_INFORMATION:
        await execute_state_transition(
            case=case,
            action="PROVIDE_INFORMATION",
            actor=actor,
            reason="Clinical information provided",
            expected_version=req.expected_state_version,
            db=db,
        )

    await db.commit()
    await db.refresh(case)

    return {
        "case_id": case.id,
        "current_state": case.current_state,
        "state_version": case.state_version,
        "answer_text": req.answer_text,
        "message": f"Information recorded. Case returned to state '{case.current_state}'.",
    }


# ---------------------------------------------------------------------------
# 5. Human Clinical Decision Recording
# ---------------------------------------------------------------------------

@router.post(
    "/{case_id}/decision",
    response_model=ClinicalDecisionResponse,
    summary="Record Authoritative Clinician Decision",
    description="Records binding human physician clinical decision, diagnosis impression, and management orders with mandatory rationale.",
    tags=["Human Review"],
)
async def record_clinician_decision_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ClinicalDecisionRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot record clinical decisions. Licensed clinician required.",
            status_code=403,
            details={"actor_role": actor.role, "required_role": "CLINICIAN"},
        )

    # Unconditionally reject prohibited autonomous actions
    dt_upper = req.decision_type.strip().upper()
    if dt_upper in PROHIBITED_CLINICAL_ACTIONS:
        raise ClinovaAPIError(
            category="UNSUPPORTED_OPERATION",
            message=f"Prohibited autonomous clinical action '{dt_upper}'.",
            status_code=422,
        )

    if not req.clinical_rationale or not req.clinical_rationale.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory human clinical judgment rationale required for clinician decisions.",
            status_code=422,
        )

    if (req.is_override or dt_upper in {"OVERRIDE", "REJECT", "OVERRIDE_RECOMMENDATION"}):
        if not req.override_reason and not req.clinical_rationale:
            raise ClinovaAPIError(
                category="VALIDATION_ERROR",
                message="Clinical rationale and override reason are mandatory when overriding recommendations.",
                status_code=422,
            )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.CLINICAL_DECISION_RECORD, db=db)

    # Optimistic concurrency check
    if req.expected_state_version is not None and req.expected_state_version != case.state_version:
        raise ClinovaAPIError(
            category="CONFLICT",
            message=(
                f"Optimistic concurrency conflict on case '{case_id}'. "
                f"Current state version is {case.state_version}, submitted expected version was {req.expected_state_version}."
            ),
            status_code=409,
            details={"current_state_version": case.state_version, "expected_state_version": req.expected_state_version},
        )

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot record decision on a closed case.",
            status_code=422,
        )

    now = utc_now()

    # State machine transition
    await execute_state_transition(
        case=case,
        action="RECORD_DECISION",
        actor=actor,
        reason=req.clinical_rationale,
        expected_version=req.expected_state_version,
        db=db,
        metadata={
            "decision_type": req.decision_type,
            "is_override": req.is_override,
        },
    )

    dec_id = str(uuid.uuid4())
    decision = ClinicianDecision(
        id=dec_id,
        case_id=case.id,
        clinician_id=actor.actor_id,
        action_type=req.decision_type,
        decision_type="OVERRIDE" if req.is_override else "ACCEPT",
        override_reason=req.override_reason or (req.clinical_rationale if req.is_override else None),
        clinical_impression=req.clinical_impression,
        treatment_plan=req.treatment_plan,
        clinical_rationale=req.clinical_rationale,
        notes=req.clinical_rationale,
        timestamp=now,
    )
    db.add(decision)

    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case.id,
        clinician_id=actor.actor_id,
        action="OVERRIDE" if req.is_override else "RECORD_DECISION",
        target_entity_type="CASE",
        target_entity_id=case.id,
        updated_value={
            "decision_type": req.decision_type,
            "clinical_impression": req.clinical_impression,
            "treatment_plan": req.treatment_plan,
            "is_override": req.is_override,
        },
        reason=req.override_reason or req.clinical_rationale,
        notes=req.clinical_rationale,
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case.id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="decision.recorded",
        object_type="CLINICIAN_DECISION",
        object_id=dec_id,
        result="SUCCESS",
        details={
            "decision_type": req.decision_type,
            "is_override": req.is_override,
            "state_version": case.state_version,
        },
        created_at=now,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(case)

    return ClinicalDecisionResponse(
        id=dec_id,
        case_id=case.id,
        clinician_id=actor.actor_id,
        decision_type=req.decision_type,
        is_override=req.is_override,
        override_reason=req.override_reason,
        clinical_rationale=req.clinical_rationale,
        clinical_impression=req.clinical_impression,
        treatment_plan=req.treatment_plan,
        state_version=case.state_version,
        current_state=case.current_state,
        timestamp=now,
        message="Authoritative clinician decision recorded.",
    )


# ---------------------------------------------------------------------------
# 6. Human Disposition & Case Closure
# ---------------------------------------------------------------------------

@router.post(
    "/{case_id}/disposition",
    response_model=ClinicalDispositionResponse,
    summary="Record Clinical Disposition",
    description="Qualified clinician finalizes encounter disposition (discharge, transfer, inpatient admission, observation).",
    tags=["Human Review"],
)
async def record_clinician_disposition_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: ClinicalDispositionRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot finalize clinical disposition. Licensed clinician required.",
            status_code=403,
            details={"actor_role": actor.role, "required_role": "CLINICIAN"},
        )

    disp_upper = req.disposition_type.strip().upper()
    if disp_upper in PROHIBITED_CLINICAL_ACTIONS:
        raise ClinovaAPIError(
            category="UNSUPPORTED_OPERATION",
            message=f"Prohibited autonomous clinical action '{disp_upper}'.",
            status_code=422,
        )

    if not req.clinical_summary or not req.clinical_summary.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory clinical summary required for disposition.",
            status_code=422,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.DISPOSITION_FINALIZE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Cannot record disposition on a closed case.",
            status_code=422,
        )

    # Concurrency verification
    if req.expected_state_version is not None and req.expected_state_version != case.state_version:
        raise ClinovaAPIError(
            category="CONFLICT",
            message=f"Optimistic concurrency conflict. Current version {case.state_version}, expected {req.expected_state_version}.",
            status_code=409,
        )

    now = utc_now()
    action_name = "FINALIZE_DISPOSITION" if req.close_case else "RECORD_DISPOSITION"

    # Transition state machine
    await execute_state_transition(
        case=case,
        action=action_name,
        actor=actor,
        reason=req.clinical_summary,
        expected_version=req.expected_state_version,
        db=db,
        metadata={"disposition_type": req.disposition_type, "close_case": req.close_case},
    )

    # Persist or update CaseOutcome
    outcome_stmt = select(CaseOutcome).where(CaseOutcome.case_id == case.id)
    outcome = (await db.execute(outcome_stmt)).scalars().first()
    if outcome:
        outcome.disposition = req.disposition_type
        outcome.notes = req.clinical_summary
        outcome.recorded_at = now
    else:
        outcome = CaseOutcome(
            id=str(uuid.uuid4()),
            case_id=case.id,
            disposition=req.disposition_type,
            final_condition="STABLE",
            notes=req.clinical_summary,
            recorded_at=now,
        )
        db.add(outcome)

    rev_action = ReviewAction(
        id=str(uuid.uuid4()),
        case_id=case.id,
        clinician_id=actor.actor_id,
        action="DISPOSITION",
        target_entity_type="CASE",
        target_entity_id=case.id,
        updated_value={"disposition_type": req.disposition_type, "close_case": req.close_case},
        reason=req.clinical_summary,
        notes=req.clinical_summary,
        created_at=now,
    )
    db.add(rev_action)

    audit = AuditEvent(
        case_id=case.id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="disposition.recorded",
        object_type="CASE_OUTCOME",
        object_id=outcome.id,
        result="SUCCESS",
        details={"disposition": req.disposition_type, "is_closed": case.is_closed},
        created_at=now,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(case)

    return ClinicalDispositionResponse(
        case_id=case.id,
        disposition_type=req.disposition_type,
        clinical_summary=req.clinical_summary,
        current_state=case.current_state,
        is_closed=case.is_closed,
        state_version=case.state_version,
        completed_at=now,
        message=f"Clinical disposition recorded. Case status: {case.current_state}.",
    )


@router.post(
    "/{case_id}/close",
    response_model=CaseCloseResponse,
    summary="Close Master Case Encounter",
    description="Terminates master case lifecycle with mandatory administrative/clinical closure reason.",
    tags=["Human Review"],
)
async def close_case_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    req: CaseCloseRequest = ...,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if not (actor.is_clinician() or actor.is_admin()):
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor.role}' cannot close case. Clinician or system admin authority required.",
            status_code=403,
        )

    if not req.closure_reason or not req.closure_reason.strip():
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message="Mandatory closure reason required to close case.",
            status_code=422,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.CASE_CLOSE, db=db)

    if case.is_closed or case.current_state == STATE_CLOSED:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message="Case is already closed.",
            status_code=422,
        )

    await execute_state_transition(
        case=case,
        action="CLOSE_CASE",
        actor=actor,
        reason=req.closure_reason,
        expected_version=req.expected_state_version,
        db=db,
    )

    now = utc_now()
    audit = AuditEvent(
        case_id=case.id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="case.closed",
        object_type="CASE",
        object_id=case.id,
        result="SUCCESS",
        details={"closure_reason": req.closure_reason},
        created_at=now,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(case)

    return CaseCloseResponse(
        case_id=case.id,
        is_closed=case.is_closed,
        current_state=case.current_state,
        closed_at=case.closed_at or now,
        closure_reason=case.closure_reason or req.closure_reason,
        state_version=case.state_version,
        message="Case closed successfully.",
    )


# ---------------------------------------------------------------------------
# 7. Review History Audit Ledger
# ---------------------------------------------------------------------------

@router.get(
    "/{case_id}/review-history",
    response_model=CaseReviewHistoryRead,
    summary="Get Case Clinical Review History",
    description="Retrieves chronological log of all human review actions, clinician decisions, transitions, and audit records.",
    tags=["Human Review"],
)
async def get_case_review_history_endpoint(
    case_id: str = Path(..., description="Canonical Case UUID"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    if actor.is_patient():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to inspect clinical review histories.",
            status_code=403,
        )

    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case '{case_id}' not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.AUDIT_READ, db=db)

    ra_stmt = select(ReviewAction).where(ReviewAction.case_id == case_id).order_by(ReviewAction.created_at)
    review_actions = (await db.execute(ra_stmt)).scalars().all()

    cd_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case_id).order_by(ClinicianDecision.timestamp)
    decisions = (await db.execute(cd_stmt)).scalars().all()

    st_stmt = select(CaseStateTransition).where(CaseStateTransition.case_id == case_id).order_by(CaseStateTransition.created_at)
    transitions = (await db.execute(st_stmt)).scalars().all()

    audit_stmt = (
        select(AuditEvent)
        .where(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at)
    )
    audit_events = (await db.execute(audit_stmt)).scalars().all()

    return CaseReviewHistoryRead(
        case_id=case.id,
        case_number=case.case_number,
        current_state=case.current_state,
        state_version=case.state_version,
        review_actions=[
            {
                "id": ra.id,
                "clinician_id": ra.clinician_id,
                "action": ra.action,
                "target_entity_type": ra.target_entity_type,
                "target_entity_id": ra.target_entity_id,
                "original_value": ra.original_value,
                "updated_value": ra.updated_value,
                "reason": ra.reason,
                "notes": ra.notes,
                "created_at": ra.created_at.isoformat(),
            }
            for ra in review_actions
        ],
        decisions=[
            {
                "id": cd.id,
                "clinician_id": cd.clinician_id,
                "action_type": cd.action_type,
                "decision_type": cd.decision_type,
                "override_reason": cd.override_reason,
                "clinical_impression": getattr(cd, "clinical_impression", None),
                "treatment_plan": getattr(cd, "treatment_plan", None),
                "clinical_rationale": getattr(cd, "clinical_rationale", None) or cd.notes,
                "notes": cd.notes,
                "timestamp": cd.timestamp.isoformat(),
            }
            for cd in decisions
        ],
        transitions=[
            {
                "id": st.id,
                "from_state": st.from_state,
                "to_state": st.to_state,
                "actor_id": st.actor_id,
                "actor_role": st.actor_role,
                "reason": st.reason,
                "state_version": st.state_version,
                "created_at": st.created_at.isoformat(),
            }
            for st in transitions
        ],
        audit_events=[
            {
                "id": au.id,
                "actor_id": au.actor_id,
                "actor_role": au.actor_role,
                "action": au.action,
                "object_type": au.object_type,
                "object_id": au.object_id,
                "result": au.result,
                "details": au.details,
                "created_at": au.created_at.isoformat(),
            }
            for au in audit_events
        ],
    )
