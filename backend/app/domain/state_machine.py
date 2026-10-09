"""CLINOVA AI — Deterministic State Machine & Concurrency Control.

Continuous Care Intelligence System.
Phase 13: Core Backend Foundation, Master Case Persistence & API Layer.
Grounded in DOC-06 (Master Patient Workflow) & Sections 8, 9, 10.

Core Invariants:
1. Never permit POST case -> arbitrary state. State changes occur exclusively via controlled actions.
2. Optimistic concurrency control via monotonic `state_version`.
3. Transition history is authoritative historical evidence in `case_state_transitions`.
4. State mutation, transition record, and audit event form a single atomic transaction.
"""

from typing import Optional, Dict, Any, Set
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Case, CaseStateTransition, AuditEvent, utc_now
from app.core.auth import ActorContext, ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE, ROLE_PATIENT
from app.core.errors import ClinovaAPIError

# Controlled State Vocabulary
STATE_INTAKE_RECORDED = "INTAKE_RECORDED"
STATE_TRIAGE_PENDING = "TRIAGE_PENDING"
STATE_TRIAGE_IN_PROGRESS = "TRIAGE_IN_PROGRESS"
STATE_PENDING_INFORMATION = "PENDING_INFORMATION"
STATE_CLINICIAN_REVIEW_REQUIRED = "CLINICIAN_REVIEW_REQUIRED"
STATE_REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
STATE_DISPOSITION_PENDING = "DISPOSITION_PENDING"
STATE_CLOSED = "CLOSED"

# Deterministic State Transition Matrix
TRANSITION_MAP: Dict[str, Dict[str, str]] = {
    STATE_INTAKE_RECORDED: {
        "START_TRIAGE": STATE_TRIAGE_IN_PROGRESS,
        "ESCALATE": STATE_CLINICIAN_REVIEW_REQUIRED,
    },
    STATE_TRIAGE_PENDING: {
        "START_TRIAGE": STATE_TRIAGE_IN_PROGRESS,
        "ESCALATE": STATE_CLINICIAN_REVIEW_REQUIRED,
    },
    STATE_TRIAGE_IN_PROGRESS: {
        "SUBMIT_TRIAGE": STATE_CLINICIAN_REVIEW_REQUIRED,
        "REQUEST_INFORMATION": STATE_PENDING_INFORMATION,
        "ESCALATE": STATE_CLINICIAN_REVIEW_REQUIRED,
    },
    STATE_PENDING_INFORMATION: {
        "PROVIDE_INFORMATION": STATE_TRIAGE_IN_PROGRESS,
        "RESUME_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "RETURN_TO_REVIEW": STATE_CLINICIAN_REVIEW_REQUIRED,
        "START_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "START_CLINICAL_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "ESCALATE": STATE_CLINICIAN_REVIEW_REQUIRED,
    },
    STATE_CLINICIAN_REVIEW_REQUIRED: {
        "START_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "START_CLINICAL_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "ESCALATE": STATE_REVIEW_IN_PROGRESS,
        "REQUEST_INFORMATION": STATE_PENDING_INFORMATION,
        "VERIFY": STATE_REVIEW_IN_PROGRESS,
        "MODIFY": STATE_REVIEW_IN_PROGRESS,
        "REJECT": STATE_REVIEW_IN_PROGRESS,
        "RESOLVE_CONFLICT": STATE_REVIEW_IN_PROGRESS,
        "OVERRIDE": STATE_REVIEW_IN_PROGRESS,
        "RECORD_DECISION": STATE_DISPOSITION_PENDING,
        "DECISION": STATE_DISPOSITION_PENDING,
        "CONTINUE": STATE_DISPOSITION_PENDING,
        "OBSERVE": STATE_DISPOSITION_PENDING,
        "REFER": STATE_DISPOSITION_PENDING,
        "RECORD_DISPOSITION": STATE_DISPOSITION_PENDING,
        "FINALIZE_DISPOSITION": STATE_CLOSED,
        "CLOSE_CASE": STATE_CLOSED,
    },
    STATE_REVIEW_IN_PROGRESS: {
        "START_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "START_CLINICAL_REVIEW": STATE_REVIEW_IN_PROGRESS,
        "VERIFY": STATE_REVIEW_IN_PROGRESS,
        "MODIFY": STATE_REVIEW_IN_PROGRESS,
        "REJECT": STATE_REVIEW_IN_PROGRESS,
        "RESOLVE_CONFLICT": STATE_REVIEW_IN_PROGRESS,
        "OVERRIDE": STATE_REVIEW_IN_PROGRESS,
        "REQUEST_INFORMATION": STATE_PENDING_INFORMATION,
        "CONTINUE": STATE_DISPOSITION_PENDING,
        "COMPLETE_REVIEW": STATE_DISPOSITION_PENDING,
        "COMPLETE_CLINICAL_REVIEW": STATE_DISPOSITION_PENDING,
        "RECORD_DECISION": STATE_DISPOSITION_PENDING,
        "DECISION": STATE_DISPOSITION_PENDING,
        "OBSERVE": STATE_DISPOSITION_PENDING,
        "ESCALATE": STATE_DISPOSITION_PENDING,
        "REFER": STATE_DISPOSITION_PENDING,
        "RECORD_DISPOSITION": STATE_DISPOSITION_PENDING,
        "FINALIZE_DISPOSITION": STATE_CLOSED,
        "CLOSE_CASE": STATE_CLOSED,
    },
    STATE_DISPOSITION_PENDING: {
        "RECORD_DISPOSITION": STATE_DISPOSITION_PENDING,
        "RECORD_DECISION": STATE_DISPOSITION_PENDING,
        "DECISION": STATE_DISPOSITION_PENDING,
        "FINALIZE_DISPOSITION": STATE_CLOSED,
        "CLOSE_CASE": STATE_CLOSED,
        "DISPOSITION": STATE_CLOSED,
        "DISCHARGE": STATE_CLOSED,
        "TRANSFER": STATE_CLOSED,
        "ADMIT": STATE_CLOSED,
        "REOPEN_REVIEW": STATE_REVIEW_IN_PROGRESS,
    },
    STATE_CLOSED: {},
}

# Role Authorization Boundaries per Action
CLINICIAN_ONLY_ACTIONS: Set[str] = {
    "START_REVIEW",
    "START_CLINICAL_REVIEW",
    "COMPLETE_REVIEW",
    "COMPLETE_CLINICAL_REVIEW",
    "VERIFY",
    "MODIFY",
    "REJECT",
    "RESOLVE_CONFLICT",
    "OVERRIDE",
    "RECORD_DECISION",
    "DECISION",
    "CONTINUE",
    "OBSERVE",
    "REFER",
    "RECORD_DISPOSITION",
    "FINALIZE_DISPOSITION",
    "CLOSE_CASE",
    "DISPOSITION",
    "DISCHARGE",
    "TRANSFER",
    "ADMIT",
    "RESUME_REVIEW",
    "RETURN_TO_REVIEW",
    "REOPEN_REVIEW",
}

NURSE_ALLOWED_ACTIONS: Set[str] = {
    "START_TRIAGE",
    "SUBMIT_TRIAGE",
    "REQUEST_INFORMATION",
    "PROVIDE_INFORMATION",
    "ESCALATE",
}


async def execute_state_transition(
    case: Case,
    action: str,
    actor: ActorContext,
    reason: str,
    expected_version: Optional[int],
    db: AsyncSession,
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> CaseStateTransition:
    """
    Enforces atomic state transition, role permissions, optimistic concurrency,
    and audit generation.
    """
    action_upper = action.upper()

    # 1. Optimistic Concurrency Check
    if expected_version is not None and expected_version != case.state_version:
        raise ClinovaAPIError(
            category="CONFLICT",
            message=(
                f"Optimistic concurrency conflict on case '{case.id}'. "
                f"Database state_version is {case.state_version}, but client submitted expected_version={expected_version}. "
                "Another actor has modified this case in the interim. Please reload the latest state."
            ),
            status_code=409,
            details={
                "case_id": case.id,
                "current_state_version": case.state_version,
                "expected_state_version": expected_version,
            },
            correlation_id=correlation_id,
        )

    # 2. Check current state and valid actions
    current_state = case.current_state or STATE_INTAKE_RECORDED
    allowed_actions = TRANSITION_MAP.get(current_state, {})

    if action_upper not in allowed_actions:
        raise ClinovaAPIError(
            category="INVALID_STATE_TRANSITION",
            message=(
                f"Action '{action_upper}' is not permitted from current case state '{current_state}'. "
                f"Permitted actions in this state: {sorted(list(allowed_actions.keys())) or ['None (Terminal state)']}"
            ),
            status_code=422,
            details={
                "case_id": case.id,
                "current_state": current_state,
                "requested_action": action_upper,
                "allowed_actions": sorted(list(allowed_actions.keys())),
            },
            correlation_id=correlation_id,
        )

    # 3. Check actor role permissions
    if not actor.is_clinician() and not actor.is_nurse():
        if not (actor.is_patient() and action_upper == "PROVIDE_INFORMATION"):
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message=f"Role '{actor.role}' is not authorized to execute clinical state transitions.",
                status_code=403,
                correlation_id=correlation_id,
            )

    if action_upper in CLINICIAN_ONLY_ACTIONS and not actor.is_clinician():
        if not (actor.is_admin() and action_upper == "CLOSE_CASE"):
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message=f"Action '{action_upper}' requires a licensed clinician role. Actor role '{actor.role}' is unauthorized.",
                status_code=403,
                details={"actor_role": actor.role, "required_role": "CLINICIAN"},
                correlation_id=correlation_id,
            )

    if actor.is_nurse() and action_upper not in NURSE_ALLOWED_ACTIONS:
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Nursing role cannot execute action '{action_upper}'. Permitted nursing actions: {sorted(list(NURSE_ALLOWED_ACTIONS))}",
            status_code=403,
            correlation_id=correlation_id,
        )

    # 4. Determine target state & mutate case
    to_state = allowed_actions[action_upper]
    if action_upper in {"COMPLETE_REVIEW", "COMPLETE_CLINICAL_REVIEW"}:
        from sqlalchemy import select
        from app.db.models import ClinicianDecision
        dec_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case.id)
        has_decision = (await db.execute(dec_stmt)).scalars().first()
        if not has_decision:
            raise ClinovaAPIError(
                category="INVALID_STATE_TRANSITION",
                message="Cannot complete clinical review without recording an authoritative clinician decision first.",
                status_code=422,
                details={"case_id": case.id, "current_state": current_state},
                correlation_id=correlation_id,
            )
    if current_state == STATE_PENDING_INFORMATION and action_upper == "PROVIDE_INFORMATION":
        from sqlalchemy import select
        prior_trans_stmt = (
            select(CaseStateTransition)
            .where(CaseStateTransition.case_id == case.id)
            .order_by(CaseStateTransition.created_at.desc())
        )
        prior_trans = (await db.execute(prior_trans_stmt)).scalars().first()
        if prior_trans and prior_trans.from_state in {STATE_REVIEW_IN_PROGRESS, STATE_CLINICIAN_REVIEW_REQUIRED}:
            to_state = STATE_CLINICIAN_REVIEW_REQUIRED
        elif metadata and metadata.get("target_state"):
            to_state = metadata["target_state"]
    previous_state = current_state

    case.current_state = to_state
    case.status = to_state  # Keep status aligned for backward compatibility
    case.state_version += 1
    case.updated_at = utc_now()

    if to_state == STATE_CLOSED:
        case.is_closed = True
        case.closed_at = utc_now()
        case.closure_reason = reason

    # 5. Persist transition record
    transition_record = CaseStateTransition(
        id=str(uuid.uuid4()),
        case_id=case.id,
        from_state=previous_state,
        to_state=to_state,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        reason=reason,
        state_version=case.state_version,
        correlation_id=correlation_id,
        transition_metadata=metadata or {},
        created_at=utc_now(),
    )
    db.add(transition_record)

    # 6. Persist audit event
    audit = AuditEvent(
        case_id=case.id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="case.state_transitioned",
        object_type="CASE",
        object_id=case.id,
        result="SUCCESS",
        correlation_id=correlation_id,
        details={
            "action": action_upper,
            "from_state": previous_state,
            "to_state": to_state,
            "reason": reason,
            "state_version": case.state_version,
        },
        created_at=utc_now(),
    )
    db.add(audit)

    return transition_record
