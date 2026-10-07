from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.case_evidence import EvidenceSourceType, VerificationState
from app.services.case_state_machine import CaseWorkflowState, ReviewReadinessStatus


class EvidenceCreateRequest(BaseModel):
    canonical_field: str
    raw_value: str
    normalized_value: Optional[str] = None
    source_type: EvidenceSourceType = EvidenceSourceType.PATIENT_REPORTED
    source_reference: Optional[str] = None
    verification_state: VerificationState = VerificationState.UNVERIFIED
    confidence_score: Optional[float] = None
    observed_at: Optional[datetime] = None
    processor_name: Optional[str] = None


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    encounter_id: Optional[str] = None
    canonical_field: str
    raw_value: str
    normalized_value: Optional[str] = None
    source_type: EvidenceSourceType
    source_reference: Optional[str] = None
    verification_state: VerificationState
    confidence_score: Optional[float] = None
    observed_at: Optional[datetime] = None
    created_by_user_id: Optional[str] = None
    processor_name: Optional[str] = None
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CaseTransitionRequest(BaseModel):
    target_state: CaseWorkflowState
    reason: Optional[str] = None


class CaseTransitionResponse(BaseModel):
    case_id: str
    synthetic_case_id: str
    previous_state: str
    current_state: str
    case_version: int
    updated_at: datetime


class ReviewReadinessResponse(BaseModel):
    status: str
    has_symptoms: bool
    has_vitals: bool
    has_conflicts: bool
    missing_fields: List[str]


class CanonicalCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    synthetic_case_id: str
    owner_user_id: Optional[str] = None
    patient_id: Optional[str] = None
    facility_id: Optional[str] = None
    encounter_id: Optional[str] = None
    language: str
    facility_type: str
    visit_type: str
    status: str
    workflow_state: str
    case_version: int
    review_readiness_status: str
    queue_category: str
    queue_reason: Optional[str] = None
    consent_status: bool
    raw_symptoms: Optional[str] = None
    normalized_symptoms: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    evidence_items: List[EvidenceResponse] = []
    current_snapshot: Optional[CaseSnapshotResponse] = None


class CaseTextInput(BaseModel):
    text: str
    language: str = "en"
    field_name: str = "reported_symptoms"


class CaseTranslateInput(BaseModel):
    source_evidence_id: Optional[str] = None
    text: Optional[str] = None
    source_language: str = "auto"
    target_language: str = "en"


class CaseTTSInput(BaseModel):
    text: str
    language: str = "en"


class ProcessingRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    capability: str
    modality: str
    provider_name: str
    model_name: Optional[str] = None
    status: str
    source_reference: Optional[str] = None
    output_evidence_id: Optional[str] = None
    latency_ms: int
    retry_count: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CanonicalFactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    snapshot_id: str
    category: str
    concept: str
    value: str
    normalized_value: Optional[str] = None
    unit: Optional[str] = None
    polarity: str
    certainty: str
    attribution: str
    temporal_status: str
    duration: Optional[str] = None
    onset_approximate: Optional[str] = None
    source_evidence_id: Optional[str] = None
    source_span: Optional[str] = None
    supporting_evidence_ids: Optional[List[str]] = None
    has_conflict: bool = False
    conflicting_value: Optional[str] = None
    conflicting_source_id: Optional[str] = None
    verification_state: str = "unverified"
    confidence_score: float = 1.0
    is_active: bool = True
    created_at: datetime


class TimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    snapshot_id: str
    event_type: str
    description: str
    relative_time: Optional[str] = None
    approximate_date: Optional[str] = None
    temporal_status: str
    source_evidence_id: Optional[str] = None
    attribution: str
    certainty: str
    order_index: int
    created_at: datetime


class CaseBuildRequest(BaseModel):
    trigger_type: str = "manual_rebuild"
    force_rebuild: bool = False
    include_inactive_evidence: bool = False


class CaseBuildRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    status: str
    trigger_type: str
    input_evidence_count: int
    facts_extracted_count: int
    facts_rejected_count: int
    target_case_version: int
    build_logic_version: str
    provider_name: str
    model_name: Optional[str] = None
    latency_ms: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    warnings: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class CaseSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    build_run_id: Optional[str] = None
    case_version: int
    schema_version: int
    build_version: str
    provider_name: str
    model_name: Optional[str] = None
    case_data: Dict[str, Any]
    delta_summary: Optional[Dict[str, Any]] = None
    is_current: bool
    created_at: datetime
    facts: List[CanonicalFactResponse] = []
    timeline_events: List[TimelineEventResponse] = []


class SpecialtySignal(BaseModel):
    specialty: str
    relevance_score: float
    matching_concepts: List[str]
    rationale: str
