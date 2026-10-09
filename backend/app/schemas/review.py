"""CLINOVA AI — Human Review & Clinical Decision Schemas.

Continuous Care Intelligence System.
Phase 17: Human Review + Case State Lifecycle.
Grounded in DOC-03, DOC-06, DOC-07, DOC-08, DOC-14.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.core.rbac import PROHIBITED_CLINICAL_ACTIONS


class ReviewQueueItemRead(BaseModel):
    case_id: str
    case_number: str
    patient_synthetic_id: str
    age_bracket: str
    biological_sex: str
    facility_id: str
    facility_name: str
    pathway: str
    current_state: str
    status: str
    priority_tier: str
    acuity_tier: str
    risk_score: float
    trajectory_slope: float
    uncertainty_score: float
    presenting_complaint: str
    primary_syndrome: Optional[str] = None
    required_bundle: Optional[str] = None
    waiting_minutes: int
    sla_limit_minutes: int
    sla_breached: bool
    emergency_active: bool
    has_critical_red_flags: bool
    critical_red_flags_count: int
    news2_score: Optional[int] = None
    shock_index: Optional[float] = None
    review_status: str  # PENDING_REVIEW, IN_REVIEW, AWAITING_DECISION, AWAITING_DISPOSITION
    assigned_clinician_id: Optional[str] = None
    created_at: str
    updated_at: str


class ReviewQueueResponse(BaseModel):
    total_cases: int
    emergency_count: int
    critical_count: int
    urgent_count: int
    moderate_count: int
    routine_count: int
    queue: List[ReviewQueueItemRead]
    is_synthetic_mode: bool = True
    generated_at: str


class StartReviewRequest(BaseModel):
    expected_state_version: Optional[int] = None
    notes: Optional[str] = None


class StartReviewResponse(BaseModel):
    case_id: str
    current_state: str
    status: str
    state_version: int
    reviewer_id: str
    reviewer_name: str
    started_at: datetime
    message: str


class EvidenceVerifyRequest(BaseModel):
    notes: Optional[str] = None
    rationale: Optional[str] = None
    expected_state_version: Optional[int] = None


class EvidenceModifyRequest(BaseModel):
    updated_value: Any
    reason: str = Field(..., min_length=1, description="Mandatory rationale for modifying evidence")
    notes: Optional[str] = None
    expected_state_version: Optional[int] = None


class EvidenceRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Mandatory clinical rationale for rejecting evidence observation")
    notes: Optional[str] = None
    expected_state_version: Optional[int] = None


class ConflictResolutionRequest(BaseModel):
    evidence_id: Optional[str] = None
    authoritative_evidence_id: Optional[str] = None
    resolved_value: Optional[Any] = None
    resolution_rationale: str = Field(..., min_length=1, description="Mandatory clinical rationale for conflict resolution")
    parameter_name: Optional[str] = None
    expected_state_version: Optional[int] = None


class RequestInformationRequest(BaseModel):
    question_text: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    priority: str = Field("IMPORTANT", description="CRITICAL, IMPORTANT, OPTIONAL")
    target_role: Optional[str] = "PATIENT"
    expected_state_version: Optional[int] = None


class ProvideInformationRequest(BaseModel):
    question_id: Optional[str] = None
    answer_text: str = Field(..., min_length=1)
    evidence_id: Optional[str] = None
    expected_state_version: Optional[int] = None


class ClinicalDecisionRequest(BaseModel):
    decision_type: str = Field(..., min_length=1, description="ACCEPT, OVERRIDE, REJECT, MODIFY_PLAN, DIAGNOSTIC_HYPOTHESIS, etc.")
    clinical_rationale: str = Field(..., min_length=1, description="Mandatory human clinical judgment rationale")
    clinical_impression: Optional[str] = None
    treatment_plan: Optional[str] = None
    is_override: bool = False
    override_reason: Optional[str] = None
    expected_state_version: Optional[int] = None

    @model_validator(mode="after")
    def validate_decision_rules(self):
        dt = self.decision_type.strip().upper()
        if dt in PROHIBITED_CLINICAL_ACTIONS:
            raise ValueError(f"Prohibited autonomous clinical action '{dt}'.")
        if self.is_override or dt in {"OVERRIDE", "REJECT", "OVERRIDE_RECOMMENDATION"}:
            if not self.override_reason and not self.clinical_rationale:
                raise ValueError("Clinical rationale and override reason are mandatory when overriding recommendations.")
            if not self.override_reason:
                self.override_reason = self.clinical_rationale
        return self


class ClinicalDecisionResponse(BaseModel):
    id: str
    case_id: str
    clinician_id: str
    decision_type: str
    is_override: bool
    override_reason: Optional[str]
    clinical_rationale: str
    clinical_impression: Optional[str]
    treatment_plan: Optional[str]
    state_version: int
    current_state: str
    timestamp: datetime
    message: str


class ClinicalDispositionRequest(BaseModel):
    disposition_type: str = Field(..., min_length=1, description="DISCHARGE_HOME, ADMIT_INPATIENT, ADMIT_ICU, TRANSFER_TERTIARY, OBSERVATION_UNIT, etc.")
    clinical_summary: str = Field(..., min_length=1, description="Mandatory clinical discharge/disposition summary")
    orders: Optional[List[str]] = None
    follow_up_instructions: Optional[str] = None
    close_case: bool = False
    expected_state_version: Optional[int] = None

    @model_validator(mode="after")
    def validate_disposition_rules(self):
        dt = self.disposition_type.strip().upper()
        if dt in PROHIBITED_CLINICAL_ACTIONS:
            raise ValueError(f"Prohibited autonomous clinical action '{dt}'.")
        return self


class ClinicalDispositionResponse(BaseModel):
    case_id: str
    disposition_type: str
    clinical_summary: str
    current_state: str
    is_closed: bool
    state_version: int
    completed_at: datetime
    message: str


class CaseCloseRequest(BaseModel):
    closure_reason: str = Field(..., min_length=1, description="Mandatory closure reason")
    expected_state_version: Optional[int] = None


class CaseCloseResponse(BaseModel):
    case_id: str
    is_closed: bool
    current_state: str
    closed_at: datetime
    closure_reason: str
    state_version: int
    message: str


class CaseReviewContextRead(BaseModel):
    case: Dict[str, Any]
    patient: Dict[str, Any]
    system_deterministic_support: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    vitals_history: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    follow_ups: List[Dict[str, Any]]
    triage_notes: List[Dict[str, Any]]
    prior_review_actions: List[Dict[str, Any]]
    prior_decisions: List[Dict[str, Any]]
    state_transitions: List[Dict[str, Any]]
    ai_advisory_results: List[Dict[str, Any]] = Field(default_factory=list)
    is_synthetic_mode: bool = True


class CaseReviewHistoryRead(BaseModel):
    case_id: str
    case_number: str
    current_state: str
    state_version: int
    review_actions: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    transitions: List[Dict[str, Any]]
    audit_events: List[Dict[str, Any]]
