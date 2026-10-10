"""CLINOVA AI — Core Authorization & Facility/Case Policy Engine.

Continuous Care Intelligence System.
Phase 14: Authentication + RBAC + Authorization + Identity Hardening.
Grounded in Section 10, 11, 12, 13 of Phase 14 Specifications.

Policy Invariants:
1. "Who are you?" (Authentication) is distinct from "What are you allowed to do?" (Authorization).
2. Facility Scope: A user assigned to Facility A cannot access Facility B data.
   Access to out-of-scope resources returns 404 to avoid leaking existence.
3. Patient Self-Scope: Patients can only access their own linked case data.
4. Autonomous Actions: AI_DIAGNOSIS, AUTO_PRESCRIBE, AI_ADMISSION, AI_DISCHARGE,
   AUTHORIZE_PROCEDURE are unconditionally rejected server-side (HTTP 422).
5. All security denials produce structured, de-identified errors and audit entries.
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ClinovaAPIError
from app.core.rbac import (
    Permission,
    has_permission,
    normalize_role,
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_RECEPTIONIST,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
    ROLE_REFERRAL_COORDINATOR,
    ROLE_FACILITY_ADMIN,
    ALLOWED_REVIEW_ACTIONS,
    PROHIBITED_CLINICAL_ACTIONS,
    NURSE_ALLOWED_REVIEW_ACTIONS,
    NURSE_PERMITTED_TRANSITIONS,
    CLINICIAN_PERMITTED_TRANSITIONS,
)
from app.db.models import Case, AuditEvent, utc_now


async def record_security_audit_event(
    db: Optional[AsyncSession],
    actor_id: str,
    actor_role: str,
    action: str,
    object_type: str,
    object_id: str,
    result: str,
    details: Optional[Dict[str, Any]] = None,
    case_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    commit: bool = True,
) -> None:
    """Records an authoritative security/authorization audit event."""
    if db is None:
        return
    try:
        event = AuditEvent(
            case_id=case_id,
            actor_id=actor_id,
            actor_role=normalize_role(actor_role),
            action=action,
            object_type=object_type,
            object_id=object_id,
            result=result,
            correlation_id=correlation_id or f"sec-{uuid.uuid4()}",
            details=details or {},
            created_at=utc_now(),
        )
        db.add(event)
        if commit:
            await db.commit()
        else:
            await db.flush()
    except Exception:
        # Audit logging failure must never leak secrets or break core safety checks
        pass


async def authorize_facility_access(
    facility_id: str,
    actor,
    correlation_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> None:
    """
    Enforces facility boundary isolation.
    Global roles (SYSTEM_ADMIN, AUDITOR) have system-wide visibility.
    Staff roles (CLINICIAN, NURSE, FACILITY_ADMIN, REFERRAL_COORDINATOR)
    are strictly confined to their assigned facility.
    """
    actor_role = normalize_role(actor.role)

    # Global roles bypass facility boundary
    if actor_role in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
        return

    # If actor has an assigned facility, it must match the target facility
    if actor.facility_id and actor.facility_id != facility_id:
        if db:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.facility_access_denied",
                object_type="FACILITY",
                object_id=facility_id,
                result="DENIED",
                correlation_id=correlation_id,
                details={
                    "actor_facility": actor.facility_id,
                    "target_facility": facility_id,
                    "reason": "Cross-facility access restricted",
                },
            )
        raise ClinovaAPIError(
            category="NOT_FOUND",
            message=f"Facility '{facility_id}' not found.",
            status_code=404,
            correlation_id=correlation_id,
        )


async def authorize_case_access(
    case: Case,
    actor,
    required_permission: Optional[Permission] = None,
    correlation_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> None:
    """
    Enforces unified case-level authorization:
    1. Permission check (RBAC)
    2. Facility scope isolation
    3. Patient self-scope isolation
    """
    actor_role = normalize_role(actor.role)

    # 1. Server-side RBAC Permission Check
    if required_permission is not None:
        if not has_permission(actor_role, required_permission):
            if db:
                await record_security_audit_event(
                    db=db,
                    actor_id=actor.actor_id,
                    actor_role=actor.role,
                    action="security.permission_denied",
                    object_type="CASE",
                    object_id=case.id,
                    case_id=case.id,
                    result="DENIED",
                    correlation_id=correlation_id,
                    details={
                        "required_permission": getattr(required_permission, "value", required_permission),
                        "actor_role": actor_role,
                    },
                )
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message=f"Role '{actor_role}' lacks permission '{getattr(required_permission, 'value', required_permission)}' for this case.",
                status_code=403,
                details={
                    "required_permission": getattr(required_permission, "value", required_permission),
                    "actor_role": actor_role,
                },
                correlation_id=correlation_id,
            )

    # 2. Patient Self-Scope Isolation
    if actor_role == ROLE_PATIENT:
        if not actor.patient_id or case.patient_id != actor.patient_id:
            if db:
                await record_security_audit_event(
                    db=db,
                    actor_id=actor.actor_id,
                    actor_role=actor.role,
                    action="security.case_access_denied",
                    object_type="CASE",
                    object_id=case.id,
                    case_id=case.id,
                    result="DENIED",
                    correlation_id=correlation_id,
                    details={
                        "reason": "Patient self-scope restriction",
                        "actor_patient_id": actor.patient_id,
                        "case_patient_id": case.patient_id,
                    },
                )
            # Deny via 404 to hide other patients' cases without leaking existence
            raise ClinovaAPIError(
                category="NOT_FOUND",
                message=f"Case '{case.id}' not found.",
                status_code=404,
                correlation_id=correlation_id,
            )
        return

    # 3. Facility Boundary Isolation
    if actor_role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
        if actor.facility_id and case.facility_id and actor.facility_id != case.facility_id:
            if db:
                await record_security_audit_event(
                    db=db,
                    actor_id=actor.actor_id,
                    actor_role=actor.role,
                    action="security.facility_access_denied",
                    object_type="CASE",
                    object_id=case.id,
                    case_id=case.id,
                    result="DENIED",
                    correlation_id=correlation_id,
                    details={
                        "reason": "Cross-facility case boundary violation",
                        "actor_facility": actor.facility_id,
                        "case_facility": case.facility_id,
                    },
                )
            # Deny via 404 to avoid leaking cross-facility record existence
            raise ClinovaAPIError(
                category="NOT_FOUND",
                message=f"Case '{case.id}' not found.",
                status_code=404,
                correlation_id=correlation_id,
            )


async def validate_review_action_safety(
    action: str,
    actor,
    case_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> None:
    """
    Enforces server-side non-diagnostic clinical boundaries and role constraints.
    Rejects prohibited autonomous actions and unauthorized actor attempts.
    """
    action_upper = action.strip().upper()
    actor_role = normalize_role(actor.role)

    # 1. Unconditionally reject prohibited autonomous clinical actions (Section 12)
    if action_upper in PROHIBITED_CLINICAL_ACTIONS:
        if db:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.prohibited_clinical_action_attempt",
                object_type="REVIEW_ACTION",
                object_id=action_upper,
                case_id=case_id,
                result="REJECTED",
                details={
                    "attempted_action": action_upper,
                    "reason": "Prohibited autonomous AI clinical action rejected server-side",
                },
            )
        raise ClinovaAPIError(
            category="UNSUPPORTED_OPERATION",
            message=(
                f"Prohibited autonomous clinical action '{action_upper}'. "
                "Clinova AI is non-diagnostic and advisory only. Autonomous prescription, "
                "diagnosis, admission, and procedure authorizations are strictly barred."
            ),
            status_code=422,
        )

    # 2. Verify against allowed qualified clinical review vocabulary (DOC-07)
    if action_upper not in ALLOWED_REVIEW_ACTIONS:
        raise ClinovaAPIError(
            category="VALIDATION_ERROR",
            message=f"Action '{action_upper}' is not in allowed review vocabulary: {sorted(list(ALLOWED_REVIEW_ACTIONS))}",
            status_code=422,
        )

    # 3. Qualified Human Clinical Authority check
    if actor_role not in {ROLE_CLINICIAN, ROLE_NURSE}:
        if db:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.review_action_denied",
                object_type="REVIEW_ACTION",
                object_id=action_upper,
                case_id=case_id,
                result="DENIED",
                details={
                    "attempted_action": action_upper,
                    "actor_role": actor_role,
                    "reason": "Requires licensed clinician or triage nurse",
                },
            )
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor_role}' cannot perform clinical review actions. Licensed clinician or triage nurse required.",
            status_code=403,
        )

    # 4. Nurse vs Clinician Action Boundaries
    if actor_role == ROLE_NURSE and action_upper not in NURSE_ALLOWED_REVIEW_ACTIONS:
        if db:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.review_action_denied",
                object_type="REVIEW_ACTION",
                object_id=action_upper,
                case_id=case_id,
                result="DENIED",
                details={
                    "attempted_action": action_upper,
                    "actor_role": actor_role,
                    "reason": "Nurses cannot perform clinician review actions",
                },
            )
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Nurses cannot perform '{action_upper}' action. Licensed clinician sign-off required.",
            status_code=403,
        )


async def validate_state_transition_safety(
    action: str,
    actor,
    case_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> None:
    """
    Enforces role constraints on clinical state transitions.
    Nurses can execute triage-level transitions; clinicians execute clinical reviews and closures.
    Non-clinical roles are strictly barred from driving clinical state transitions.
    """
    action_upper = action.strip().upper()
    actor_role = normalize_role(actor.role)

    if actor_role == ROLE_NURSE:
        if action_upper not in NURSE_PERMITTED_TRANSITIONS:
            if db:
                await record_security_audit_event(
                    db=db,
                    actor_id=actor.actor_id,
                    actor_role=actor.role,
                    action="security.state_transition_denied",
                    object_type="STATE_TRANSITION",
                    object_id=action_upper,
                    case_id=case_id,
                    result="DENIED",
                    details={"action": action_upper, "actor_role": actor_role},
                )
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message=f"Nurses cannot execute state transition '{action_upper}'. Clinician authority required.",
                status_code=403,
            )
    elif actor_role == ROLE_CLINICIAN:
        if action_upper not in CLINICIAN_PERMITTED_TRANSITIONS:
            raise ClinovaAPIError(
                category="VALIDATION_ERROR",
                message=f"Transition action '{action_upper}' is not recognized.",
                status_code=422,
            )
    else:
        if db:
            await record_security_audit_event(
                db=db,
                actor_id=actor.actor_id,
                actor_role=actor.role,
                action="security.state_transition_denied",
                object_type="STATE_TRANSITION",
                object_id=action_upper,
                case_id=case_id,
                result="DENIED",
                details={"action": action_upper, "actor_role": actor_role},
            )
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{actor_role}' is not authorized to drive clinical case state transitions.",
            status_code=403,
        )
