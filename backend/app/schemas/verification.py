"""Pydantic schemas for Phase 4 Clinical Information Verification and Review Readiness."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class VerificationFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    verification_run_id: str
    case_id: str
    case_version: int
    finding_type: str
    category: str
    field_name: Optional[str] = None
    severity: str
    status: str
    is_blocking: bool
    title: str
    description: str
    explanation: str
    expected_information: Optional[str] = None
    observed_information: Optional[str] = None
    source_evidence_ids: Optional[List[str]] = None
    fact_ids: Optional[List[str]] = None
    timeline_event_ids: Optional[List[str]] = None
    rule_id: str
    rule_version: str
    resolved_by_user_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime


class VerificationConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    verification_run_id: str
    case_id: str
    case_version: int
    conflict_type: str
    field_name: str
    severity: str
    source_a_evidence_id: Optional[str] = None
    source_a_type: Optional[str] = None
    source_a_modality: Optional[str] = None
    source_a_value: str
    source_a_timestamp: Optional[datetime] = None
    source_b_evidence_id: Optional[str] = None
    source_b_type: Optional[str] = None
    source_b_modality: Optional[str] = None
    source_b_value: str
    source_b_timestamp: Optional[datetime] = None
    resolution_state: str
    resolution_notes: Optional[str] = None
    resolved_by_user_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    rule_id: str
    created_at: datetime


class VerificationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    case_snapshot_id: Optional[str] = None
    case_version: int
    status: str
    engine_version: str
    ruleset_version: str
    review_readiness_status: str
    review_readiness_score: float
    review_readiness_reasons: List[str] = []
    findings_count: int
    blocking_findings_count: int
    high_findings_count: int
    medium_findings_count: int
    low_findings_count: int
    info_findings_count: int
    unresolved_findings_count: int
    resolved_findings_count: int
    structural_integrity_status: str
    completeness_status: str
    consistency_status: str
    temporal_status: str
    provenance_status: str
    uncertainty_status: str
    is_current: bool
    is_stale: bool = False
    latency_ms: int
    failure_reason: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    findings: List[VerificationFindingResponse] = []
    conflicts: List[VerificationConflictResponse] = []


class VerifyCaseRequest(BaseModel):
    force_reverify: bool = Field(False, description="Whether to bypass cache/idempotency and rerun verification.")
    include_ai_checks: bool = Field(True, description="Whether to include optional bounded AI semantic conflict checks.")


class ResolveFindingRequest(BaseModel):
    resolution_state: str = Field(
        "RESOLVED_BY_HUMAN_VERIFICATION",
        description="Resolution status (e.g., RESOLVED_BY_HUMAN_VERIFICATION, DISMISSED_WITH_REASON).",
    )
    resolution_notes: str = Field(
        ...,
        min_length=3,
        description="Clinical rationale explaining why the finding was resolved or dismissed.",
    )


class ReviewReadinessSummaryResponse(BaseModel):
    case_id: str
    case_version: int
    verified_case_version: Optional[int] = None
    review_readiness_status: str
    review_readiness_score: float
    review_readiness_reasons: List[str]
    is_stale: bool
    blocking_count: int
    unresolved_count: int
    completeness_status: str
    consistency_status: str
    temporal_status: str
    provenance_status: str
    uncertainty_status: str
    last_verified_at: Optional[datetime] = None
