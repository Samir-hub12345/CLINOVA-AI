"""CLINOVA AI — Role-Based Access Control (RBAC) & Authority Specifications.

Continuous Care Intelligence System.
Phase 14: Authentication + RBAC + Authorization + Identity Hardening.
Grounded in DOC-03 (Role-Based Access Control Specification).

Core Governance Invariants:
1. Distinguishes IDENTITY AUTHENTICATION from ROLE AUTHORIZATION.
2. Clinical authority belongs exclusively to qualified human clinicians.
3. Prohibited autonomous clinical actions (AI_DIAGNOSIS, AUTO_PRESCRIBE,
   AI_ADMISSION, AI_DISCHARGE, AUTHORIZE_PROCEDURE) are unconditionally rejected.
4. Server-side permission evaluation is authoritative; client-supplied role
   headers cannot elevate privileges.
"""

from enum import Enum
from typing import Set, Dict, List
from app.core.errors import ClinovaAPIError

# Canonical Roles (DOC-03)
ROLE_PATIENT = "PATIENT"
ROLE_RECEPTIONIST = "RECEPTIONIST"
ROLE_NURSE = "NURSE"
ROLE_CLINICIAN = "CLINICIAN"
ROLE_DOCTOR = "DOCTOR"  # Canonical alias for CLINICIAN
ROLE_REFERRAL_COORDINATOR = "REFERRAL_COORDINATOR"
ROLE_FACILITY_ADMIN = "FACILITY_ADMIN"
ROLE_AUDITOR = "AUDITOR"
ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
ROLE_SYSTEM = "SYSTEM"  # Alias for SYSTEM_ADMIN
ROLE_ADMIN = "ADMIN"    # Legacy alias for FACILITY_ADMIN

# Non-clinical evaluation / research roles (strictly zero clinical mutation)
ROLE_REVIEWER = "REVIEWER"
ROLE_RESEARCHER = "RESEARCHER"
ROLE_HARNESS = "HARNESS"

ALL_CANONICAL_ROLES: Set[str] = {
    ROLE_PATIENT,
    ROLE_RECEPTIONIST,
    ROLE_NURSE,
    ROLE_CLINICIAN,
    ROLE_REFERRAL_COORDINATOR,
    ROLE_FACILITY_ADMIN,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
    ROLE_REVIEWER,
    ROLE_RESEARCHER,
    ROLE_HARNESS,
}


def normalize_role(role: str) -> str:
    """Normalizes role aliases to canonical representation."""
    r = role.strip().upper() if role else ""
    if r == "DOCTOR":
        return ROLE_CLINICIAN
    if r == "ADMIN":
        return ROLE_FACILITY_ADMIN
    if r == "SYSTEM":
        return ROLE_SYSTEM_ADMIN
    return r


class Permission(str, Enum):
    """Discrete server-side permissions separated by domain concern."""

    # Identity
    USER_SELF_READ = "identity:self_read"
    USER_ADMIN_MANAGE = "identity:admin_manage"

    # Case Lifecycle & Access
    CASE_READ = "case:read"
    CASE_CREATE = "case:create"
    CASE_LIST = "case:list"

    # Clinical Actions
    VITALS_RECORD = "clinical:vitals_record"
    VITALS_WRITE = "clinical:vitals_record"
    EVIDENCE_ADD = "clinical:evidence_add"
    FOLLOW_UP_CREATE = "clinical:follow_up_create"
    FOLLOW_UP_ANSWER = "clinical:follow_up_answer"
    TRIAGE_NOTE_CREATE = "clinical:triage_note_create"
    TRIAGE_ACTION_START = "clinical:triage_start"
    TRIAGE_ACTION_SUBMIT = "clinical:triage_submit"
    REVIEW_ACTION_EXECUTE = "clinical:review_action_execute"
    CLINICAL_STATE_TRANSITION = "clinical:state_transition"
    CLINICAL_DECISION_RECORD = "clinical:decision_record"
    CLINICAL_REVIEW_START = "clinical:review_start"
    DISPOSITION_FINALIZE = "clinical:disposition_finalize"
    CASE_CLOSE = "clinical:case_close"

    # Referral Functions
    REFERRAL_COORDINATE = "referral:coordinate"

    # Administrative Actions
    FACILITY_ADMIN_MANAGE = "admin:facility_manage"
    SYSTEM_CONFIG_MANAGE = "admin:system_config"

    # Audit & Inspection
    AUDIT_READ = "audit:read"

    # Offline Synchronization Functions (Phase 24 / RES-99)
    SYNC_PUSH = "sync:push"
    SYNC_READ = "sync:read"
    SYNC_RESOLVE = "sync:resolve"


# Explicit Role-Permission Matrix (Server-Side Authoritative)
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    ROLE_PATIENT: {
        Permission.USER_SELF_READ,
        Permission.CASE_CREATE,       # Patient self-intake submission
        Permission.CASE_READ,         # Self-scope only (verified in policy)
        Permission.CASE_LIST,         # Self-scope listing (verified in policy/endpoint)
        Permission.FOLLOW_UP_ANSWER,  # Answering questions addressed to patient
        Permission.SYNC_PUSH,         # Patient offline intake sync push
    },
    ROLE_RECEPTIONIST: {
        Permission.USER_SELF_READ,
        Permission.CASE_CREATE,       # Patient registration & intake initiation
        Permission.CASE_READ,         # Case lookup for registration
        Permission.CASE_LIST,         # Case lookup & queue search
        Permission.SYNC_PUSH,
        Permission.SYNC_READ,
    },
    ROLE_NURSE: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_LIST,
        Permission.VITALS_RECORD,
        Permission.EVIDENCE_ADD,
        Permission.FOLLOW_UP_CREATE,
        Permission.FOLLOW_UP_ANSWER,
        Permission.TRIAGE_NOTE_CREATE,
        Permission.TRIAGE_ACTION_START,
        Permission.TRIAGE_ACTION_SUBMIT,
        Permission.REVIEW_ACTION_EXECUTE,  # Sub-vocabulary enforced in policy
        Permission.CLINICAL_STATE_TRANSITION,  # Nurse-tier transitions only
        Permission.SYNC_PUSH,
        Permission.SYNC_READ,
    },
    ROLE_CLINICIAN: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_CREATE,
        Permission.CASE_LIST,
        Permission.VITALS_RECORD,
        Permission.EVIDENCE_ADD,
        Permission.FOLLOW_UP_CREATE,
        Permission.FOLLOW_UP_ANSWER,
        Permission.TRIAGE_NOTE_CREATE,
        Permission.REVIEW_ACTION_EXECUTE,
        Permission.CLINICAL_STATE_TRANSITION,
        Permission.CLINICAL_DECISION_RECORD,
        Permission.CLINICAL_REVIEW_START,
        Permission.DISPOSITION_FINALIZE,
        Permission.CASE_CLOSE,
        Permission.REFERRAL_COORDINATE,
        Permission.AUDIT_READ,
        Permission.SYNC_PUSH,
        Permission.SYNC_READ,
        Permission.SYNC_RESOLVE,
    },
    ROLE_REFERRAL_COORDINATOR: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
        Permission.REFERRAL_COORDINATE,
    },
    ROLE_FACILITY_ADMIN: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
        Permission.FACILITY_ADMIN_MANAGE,
        Permission.AUDIT_READ,
    },
    ROLE_AUDITOR: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
        Permission.AUDIT_READ,
    },
    ROLE_SYSTEM_ADMIN: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
        Permission.USER_ADMIN_MANAGE,
        Permission.FACILITY_ADMIN_MANAGE,
        Permission.SYSTEM_CONFIG_MANAGE,
        Permission.AUDIT_READ,
        Permission.CASE_CLOSE,
        Permission.SYNC_PUSH,
        Permission.SYNC_READ,
        Permission.SYNC_RESOLVE,
    },
    ROLE_REVIEWER: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
    },
    ROLE_RESEARCHER: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
    },
    ROLE_HARNESS: {
        Permission.USER_SELF_READ,
        Permission.CASE_READ,
        Permission.CASE_LIST,
    },
}

# Permitted Qualified Human Clinical Review Vocabulary (DOC-07)
ALLOWED_REVIEW_ACTIONS: Set[str] = {
    "VERIFY",
    "MODIFY",
    "REJECT",
    "RESOLVE_CONFLICT",
    "REQUEST_INFORMATION",
    "CONTINUE",
    "OBSERVE",
    "ESCALATE",
    "REFER",
    "OVERRIDE",
    "RECORD_DECISION",
    "DECISION",
    "DISPOSITION",
    "RECORD_DISPOSITION",
    "FINALIZE_DISPOSITION",
    "COMPLETE_REVIEW",
    "COMPLETE_CLINICAL_REVIEW",
    "CLOSE_CASE",
}

# Nurse-Permitted Review Actions (Cannot override clinician diagnoses/notes, verify evidence, or refer)
NURSE_ALLOWED_REVIEW_ACTIONS: Set[str] = {
    "REQUEST_INFORMATION",
    "OBSERVE",
    "ESCALATE",
}

# Strictly Prohibited Autonomous / AI Clinical Actions (Section 12)
PROHIBITED_CLINICAL_ACTIONS: Set[str] = {
    "AI_DIAGNOSIS",
    "AUTO_PRESCRIBE",
    "AI_ADMISSION",
    "AI_DISCHARGE",
    "AUTHORIZE_PROCEDURE",
}

# Permitted State Transitions by Role
NURSE_PERMITTED_TRANSITIONS: Set[str] = {
    "START_TRIAGE",
    "SUBMIT_TRIAGE",
    "REQUEST_INFORMATION",
    "PROVIDE_INFORMATION",
    "ESCALATE",
}

CLINICIAN_PERMITTED_TRANSITIONS: Set[str] = {
    "START_TRIAGE",
    "SUBMIT_TRIAGE",
    "REQUEST_INFORMATION",
    "PROVIDE_INFORMATION",
    "ESCALATE",
    "START_REVIEW",
    "START_CLINICAL_REVIEW",
    "COMPLETE_REVIEW",
    "COMPLETE_CLINICAL_REVIEW",
    "VERIFY",
    "MODIFY",
    "REJECT",
    "RESOLVE_CONFLICT",
    "CONTINUE",
    "OBSERVE",
    "REFER",
    "OVERRIDE",
    "RECORD_DECISION",
    "DECISION",
    "RECORD_DISPOSITION",
    "FINALIZE_DISPOSITION",
    "DISPOSITION",
    "DISCHARGE",
    "TRANSFER",
    "ADMIT",
    "CLOSE_CASE",
    "RESUME_REVIEW",
    "RETURN_TO_REVIEW",
}


def has_permission(role: str, permission: Permission) -> bool:
    """Evaluates whether the specified role holds the required permission."""
    norm = normalize_role(role)
    perms = ROLE_PERMISSIONS.get(norm, set())
    return permission in perms


def check_role_permission(role: str, permission: Permission) -> None:
    """Raises 403 AUTHORIZATION_ERROR if role lacks the specified permission."""
    if not has_permission(role, permission):
        norm = normalize_role(role)
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message=f"Role '{norm}' lacks permission '{permission.value}' for this operation.",
            status_code=403,
            details={"required_permission": permission.value, "assigned_role": norm},
        )
