"""CLINOVA AI — Deterministic Triage Schemas.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.
Pydantic v2 Schemas for vitals freshness, deterministic scoring, red flags,
triage snapshots, and clinical queue management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.foundation import VitalRead


class VitalLatestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vital: Optional[VitalRead] = None
    freshness_by_parameter: Dict[str, str] = Field(default_factory=dict)
    overall_status: str = "MISSING"  # AVAILABLE, STALE, MISSING
    age_minutes: Optional[float] = None
    recorded_at: Optional[datetime] = None


class NEWS2Result(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: Optional[int] = None
    is_complete: bool
    risk_level: Optional[str] = None  # LOW, LOW_MEDIUM, MEDIUM, HIGH
    component_scores: Dict[str, Optional[int]] = Field(default_factory=dict)
    missing_components: List[str] = Field(default_factory=list)
    version: str = "NEWS2-RCP-2017"
    calculated_at: datetime
    limitation: Optional[str] = None


class ShockIndexResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: Optional[float] = None
    is_complete: bool
    interpretation: Optional[str] = None  # NORMAL, MILD_ELEVATED, HIGH_SHOCK_RISK, CRITICAL_SHOCK_RISK, MISSING_INPUTS, INVALID_INPUTS
    missing_components: List[str] = Field(default_factory=list)
    version: str = "SHOCK-INDEX-v1.0"
    calculated_at: datetime
    error: Optional[str] = None


class RedFlagResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: str
    rule_version: str
    name: str
    severity: str  # CRITICAL, URGENT, WARNING
    triggered: bool
    explanation: str
    observed_inputs: Dict[str, Any] = Field(default_factory=dict)
    vital_references: List[str] = Field(default_factory=list)
    timestamp: datetime


class TriageSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    vital_id: Optional[str] = None
    pathway: str
    current_state: str
    vitals_summary: Dict[str, Any] = Field(default_factory=dict)
    vitals_freshness: Dict[str, str] = Field(default_factory=dict)
    vitals_overall_status: str = "MISSING"
    vital_age_minutes: Optional[float] = None
    news2: NEWS2Result
    shock_index: ShockIndexResult
    red_flags: List[RedFlagResult] = Field(default_factory=list)
    has_critical_red_flags: bool = False
    uncertainty_score: float = 0.5
    uncertainty_level: str = "MODERATE"
    missing_critical_vitals: List[str] = Field(default_factory=list)
    data_completeness_ratio: float = 0.0
    priority_tier: str = "P4_ROUTINE"
    acuity_tier: str = "ROUTINE"
    risk_score: float = 0.1
    priority_reasons: List[str] = Field(default_factory=list)
    ruleset_version: str
    calculated_at: datetime


class CasePriorityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    priority_tier: str
    acuity_tier: str
    risk_score: float
    uncertainty_score: float
    pathway: str
    has_critical_red_flags: bool
    triggering_rules: List[str] = Field(default_factory=list)
    priority_reasons: List[str] = Field(default_factory=list)
    physiological_indicators: Dict[str, Any] = Field(default_factory=dict)
    missing_critical_vitals: List[str] = Field(default_factory=list)
    ruleset_version: str
    calculated_at: datetime


class QueueItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    uncertainty_score: float
    presenting_complaint: Optional[str] = ""
    waiting_minutes: int
    sla_limit_minutes: int
    sla_breached: bool
    emergency_active: bool = False
    has_critical_red_flags: bool = False
    critical_red_flags_count: int = 0
    red_flags_count: int = 0
    latest_vitals: Optional[Dict[str, Any]] = None
    vitals_overall_status: str = "MISSING"
    missing_critical_vitals: List[str] = Field(default_factory=list)
    epistemic_status: str = "UNKNOWN"
    provenance_type: str = "SYSTEM_DERIVED"
    next_recommended_action: str = "TRIAGE_ASSESSMENT"
    created_at: datetime


class ClinicalQueueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_cases: int
    critical_count: int
    urgent_count: int
    moderate_count: int
    routine_count: int
    queue: List[QueueItemRead]
    is_synthetic_mode: bool = True
    generated_at: datetime
