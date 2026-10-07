import enum
import logging
from datetime import datetime, timezone
from typing import Optional, Set, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, VerificationState
from app.models.user import User, UserRole
from app.services.audit import AuditService

logger = logging.getLogger("clinova.case_state_machine")


class CaseWorkflowState(str, enum.Enum):
    CREATED = "CREATED"
    INTAKE = "INTAKE"
    PROCESSING = "PROCESSING"
    BUILDING = "BUILDING"
    NEEDS_INFORMATION = "NEEDS_INFORMATION"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    STAFF_REVIEW = "STAFF_REVIEW"
    DOCTOR_REVIEW = "DOCTOR_REVIEW"
    CLINICAL_DECISION = "CLINICAL_DECISION"
    EMERGENCY_ESCALATION = "EMERGENCY_ESCALATION"
    FINALIZED = "FINALIZED"
    CLOSED = "CLOSED"
    FAILED_PROCESSING = "FAILED_PROCESSING"
    CANCELLED = "CANCELLED"


class ReviewReadinessStatus(str, enum.Enum):
    NOT_READY = "not_ready"
    NEEDS_INFORMATION = "needs_information"
    READY_FOR_REVIEW = "ready_for_review"
    REQUIRES_ESCALATION = "requires_escalation"


PERMITTED_TRANSITIONS: Dict[CaseWorkflowState, Set[CaseWorkflowState]] = {
    CaseWorkflowState.CREATED: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.CANCELLED,
    },
    CaseWorkflowState.INTAKE: {
        CaseWorkflowState.PROCESSING,
        CaseWorkflowState.EMERGENCY_ESCALATION,
        CaseWorkflowState.CANCELLED,
    },
    CaseWorkflowState.PROCESSING: {
        CaseWorkflowState.BUILDING,
        CaseWorkflowState.FAILED_PROCESSING,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.BUILDING: {
        CaseWorkflowState.NEEDS_INFORMATION,
        CaseWorkflowState.READY_FOR_REVIEW,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.NEEDS_INFORMATION: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.BUILDING,
        CaseWorkflowState.READY_FOR_REVIEW,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.READY_FOR_REVIEW: {
        CaseWorkflowState.STAFF_REVIEW,
        CaseWorkflowState.DOCTOR_REVIEW,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.STAFF_REVIEW: {
        CaseWorkflowState.DOCTOR_REVIEW,
        CaseWorkflowState.NEEDS_INFORMATION,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.DOCTOR_REVIEW: {
        CaseWorkflowState.CLINICAL_DECISION,
        CaseWorkflowState.STAFF_REVIEW,
        CaseWorkflowState.NEEDS_INFORMATION,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    CaseWorkflowState.EMERGENCY_ESCALATION: {
        CaseWorkflowState.DOCTOR_REVIEW,
        CaseWorkflowState.STAFF_REVIEW,
    },
    CaseWorkflowState.CLINICAL_DECISION: {
        CaseWorkflowState.FINALIZED,
        CaseWorkflowState.DOCTOR_REVIEW,
    },
    CaseWorkflowState.FINALIZED: {
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.CLOSED: set(),
    CaseWorkflowState.FAILED_PROCESSING: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.CANCELLED,
    },
    CaseWorkflowState.CANCELLED: set(),
}

ROLE_PERMITTED_TRANSITIONS: Dict[UserRole, Set[CaseWorkflowState]] = {
    UserRole.PATIENT: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.PROCESSING,
        CaseWorkflowState.BUILDING,
        CaseWorkflowState.CANCELLED,
    },
    UserRole.NURSE: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.PROCESSING,
        CaseWorkflowState.BUILDING,
        CaseWorkflowState.READY_FOR_REVIEW,
        CaseWorkflowState.STAFF_REVIEW,
        CaseWorkflowState.DOCTOR_REVIEW,
        CaseWorkflowState.NEEDS_INFORMATION,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    UserRole.STAFF: {
        CaseWorkflowState.INTAKE,
        CaseWorkflowState.PROCESSING,
        CaseWorkflowState.BUILDING,
        CaseWorkflowState.READY_FOR_REVIEW,
        CaseWorkflowState.STAFF_REVIEW,
        CaseWorkflowState.DOCTOR_REVIEW,
        CaseWorkflowState.NEEDS_INFORMATION,
        CaseWorkflowState.EMERGENCY_ESCALATION,
    },
    UserRole.DOCTOR: set(CaseWorkflowState),
    UserRole.ADMIN: {
        CaseWorkflowState.CLOSED,
        CaseWorkflowState.CANCELLED,
        CaseWorkflowState.FINALIZED,
    },
}


class InvalidStateTransitionError(HTTPException):
    def __init__(self, current_state: str, target_state: str, reason: str = ""):
        detail = f"Invalid case transition from '{current_state}' to '{target_state}'."
        super().__init__(status_code=422, detail=detail)


class CaseStateMachine:
    """Deterministic, auditable state machine for the Canonical Patient Case lifecycle."""

    @staticmethod
    def is_transition_permitted(
        current_state: CaseWorkflowState, target_state: CaseWorkflowState
    ) -> bool:
        allowed = PERMITTED_TRANSITIONS.get(current_state, set())
        return target_state in allowed

    @staticmethod
    def is_role_authorized(
        role: UserRole, target_state: CaseWorkflowState
    ) -> bool:
        allowed_targets = ROLE_PERMITTED_TRANSITIONS.get(role, set())
        return target_state in allowed_targets

    @classmethod
    async def transition(
        cls,
        case: TriageCase,
        target_state: CaseWorkflowState,
        actor: Optional[User],
        db: AsyncSession,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TriageCase:
        try:
            curr = CaseWorkflowState(case.workflow_state)
        except ValueError:
            curr = CaseWorkflowState.CREATED

        # 1. Validate permitted transitions
        if not cls.is_transition_permitted(curr, target_state):
            # Log rejection audit trail
            await AuditService.log_event(
                db=db,
                action="INVALID_TRANSITION_REJECTED",
                resource_type="TRIAGE_CASE",
                resource_id=case.synthetic_case_id,
                user=actor,
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"Rejected transition from {curr.value} to {target_state.value}. Disallowed transition path.",
            )
            await db.commit()
            raise InvalidStateTransitionError(
                current_state=curr.value,
                target_state=target_state.value,
                reason="Transition is disallowed by case state machine policy.",
            )

        # 2. Validate role authorization if actor provided
        if actor and not cls.is_role_authorized(actor.role, target_state):
            await AuditService.log_event(
                db=db,
                action="UNAUTHORIZED_TRANSITION_BLOCKED",
                resource_type="TRIAGE_CASE",
                resource_id=case.synthetic_case_id,
                user=actor,
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"Actor role {actor.role.value} not authorized to transition case to {target_state.value}.",
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{actor.role.value}' is not authorized to move case to '{target_state.value}'.",
            )

        # 3. Apply state transition
        prev_state = case.workflow_state
        case.workflow_state = target_state.value
        case.case_version += 1
        case.updated_at = datetime.now(timezone.utc)

        # Synchronize backward-compatible status field where relevant
        if target_state == CaseWorkflowState.FINALIZED:
            case.status = "approved"
            case.approved_at = datetime.now(timezone.utc)
        elif target_state == CaseWorkflowState.DOCTOR_REVIEW:
            case.status = "under_review"
            case.reviewed_at = datetime.now(timezone.utc)
        elif target_state == CaseWorkflowState.CLOSED:
            case.status = "closed"
        elif target_state == CaseWorkflowState.EMERGENCY_ESCALATION:
            case.queue_category = "critical"

        # 4. Audit logging
        await AuditService.log_event(
            db=db,
            action="CASE_STATE_TRANSITIONED",
            resource_type="TRIAGE_CASE",
            resource_id=case.synthetic_case_id,
            user=actor,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"State transitioned from {prev_state} to {target_state.value}. Version: {case.case_version}. Reason: {reason or 'Standard workflow'}",
        )

        return case

    @staticmethod
    def evaluate_review_readiness(
        case: TriageCase, evidence_items: List[CaseEvidence]
    ) -> Dict:
        """Evaluate Review Readiness Index based on presence of clinical complaints, vitals, and conflicts."""
        has_symptoms = bool(case.raw_symptoms or case.normalized_symptoms or any(e.canonical_field == "symptom" for e in evidence_items))
        has_vitals = bool(case.vitals or any(e.canonical_field.startswith("vital") for e in evidence_items))
        has_conflicts = any(e.verification_state == VerificationState.DISPUTED_CONFLICTING for e in evidence_items)
        has_red_flags = case.queue_category == "critical"

        missing = []
        if not has_symptoms:
            missing.append("symptoms")
        if not has_vitals:
            missing.append("vitals")

        if has_red_flags:
            readiness_status = ReviewReadinessStatus.REQUIRES_ESCALATION
        elif not has_symptoms:
            readiness_status = ReviewReadinessStatus.NEEDS_INFORMATION
        elif has_conflicts:
            readiness_status = ReviewReadinessStatus.READY_FOR_REVIEW  # Ready for clinician conflict resolution
        elif has_symptoms and has_vitals:
            readiness_status = ReviewReadinessStatus.READY_FOR_REVIEW
        else:
            readiness_status = ReviewReadinessStatus.READY_FOR_REVIEW

        return {
            "status": readiness_status.value,
            "has_symptoms": has_symptoms,
            "has_vitals": has_vitals,
            "has_conflicts": has_conflicts,
            "missing_fields": missing,
        }
