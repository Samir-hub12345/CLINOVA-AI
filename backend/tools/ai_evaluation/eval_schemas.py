"""CLINOVA AI — Evaluation Schemas, Contracts, and Error Taxonomy.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Defines TimelinePayload/Result (Task 3 contract missing from Phase 10),
the 20-code structured Error Taxonomy (E001-E020), and metric reporting models.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.ai_runtime.schemas.contracts import BaseAIResponse


# ---------------------------------------------------------------------------
# Task 3: TIMELINE DRAFTING CONTRACT (Independent Phase 11 Definition)
# ---------------------------------------------------------------------------
class TimelineEvent(BaseModel):
    """Single discrete chronological event grounded in clinical evidence."""
    time_anchor: str = Field(..., description="Timestamp or relative offset e.g. '3 days ago', '14:30 hrs'")
    description: str = Field(..., description="Clinical occurrence or intervention description")
    source_evidence_id: str = Field(..., description="Evidence ID justifying this event")
    event_type: str = Field(default="OCCURRENCE", description="ONSET, VITAL_RECORD, INTERVENTION, STATUS_CHANGE")


class TimelinePayload(BaseModel):
    """Machine-consumed structured timeline representation."""
    events: List[TimelineEvent] = Field(default_factory=list, description="Ordered chronological events")
    chronology_summary: str = Field(..., description="Textual narrative synthesizing event progression")


class TimelineResult(BaseAIResponse):
    """Complete envelope response for Task 3 Timeline Drafting."""
    payload: TimelinePayload = Field(...)


# ---------------------------------------------------------------------------
# STRUCTURED ERROR TAXONOMY (E001 - E020)
# ---------------------------------------------------------------------------
class ErrorTaxonomyCode(str, Enum):
    """The 20 mandated Phase 11 error taxonomy categories."""
    E001_HALLUCINATION = "E001 Hallucination"
    E002_WRONG_EXTRACTION = "E002 Wrong extraction"
    E003_MISSING_EXTRACTION = "E003 Missing extraction"
    E004_WRONG_PROVENANCE = "E004 Wrong provenance"
    E005_WRONG_TIMELINE = "E005 Wrong timeline"
    E006_WRONG_NEGATION = "E006 Wrong negation"
    E007_WRONG_NUMERICAL_VALUE = "E007 Wrong numerical value"
    E008_WRONG_UNIT = "E008 Wrong unit"
    E009_TRANSLATION_DRIFT = "E009 Translation drift"
    E010_UNSUPPORTED_INFERENCE = "E010 Unsupported inference"
    E011_FALSE_CERTAINTY = "E011 False certainty"
    E012_PROMPT_INJECTION_SUCCESS = "E012 Prompt injection success"
    E013_FORBIDDEN_ACTION = "E013 Forbidden action"
    E014_SCHEMA_FAILURE = "E014 Schema failure"
    E015_TIMEOUT = "E015 Timeout"
    E016_RESOURCE_FAILURE = "E016 Resource failure"
    E017_LANGUAGE_FAILURE = "E017 Language failure"
    E018_CONFLICT_MISHANDLING = "E018 Conflict mishandling"
    E019_MISSING_INFO_FAILURE = "E019 Missing-information failure"
    E020_OTHER = "E020 Other"


# ---------------------------------------------------------------------------
# METRIC REPORTING SCHEMAS
# ---------------------------------------------------------------------------
class EntityMetrics(BaseModel):
    """Precision, recall, F1, and source attribution for entity extraction."""
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1: float = Field(..., ge=0.0, le=1.0)
    source_attribution_accuracy: float = Field(..., ge=0.0, le=1.0)
    unsupported_inference_rate: float = Field(default=0.0, ge=0.0, le=1.0)


class GroundingMetrics(BaseModel):
    """Claim-level evidentiary support breakdown."""
    grounded_claim_rate: float = Field(..., ge=0.0, le=1.0)
    partially_supported_rate: float = Field(..., ge=0.0, le=1.0)
    unsupported_claim_rate: float = Field(..., ge=0.0, le=1.0)
    phantom_evidence_rate: float = Field(..., ge=0.0, le=1.0)


class SafetyMetrics(BaseModel):
    """Safety gate compliance and refusal benchmarks."""
    prompt_injection_defense_rate: float = Field(..., ge=0.0, le=1.0)
    forbidden_action_refusal_rate: float = Field(..., ge=0.0, le=1.0)
    out_of_bounds_vital_rejection_rate: float = Field(..., ge=0.0, le=1.0)
    overall_safety_score: float = Field(..., ge=0.0, le=1.0)


class MultilingualMetrics(BaseModel):
    """Preservation and translation accuracy across vernacular inputs."""
    odia_colloquial_preservation_rate: float = Field(..., ge=0.0, le=1.0)
    hindi_clinical_accuracy_rate: float = Field(..., ge=0.0, le=1.0)
    mixed_code_switching_comprehension: float = Field(..., ge=0.0, le=1.0)
    translation_clinical_meaning_preservation: float = Field(..., ge=0.0, le=1.0)


class ResourceMetrics(BaseModel):
    """Empirical hardware runtime measurements."""
    model_load_time_seconds: float
    latency_p50_ms: float
    latency_p95_ms: float
    peak_ram_mb: float
    peak_vram_mb: float
    cpu_utilization_pct: float
    concurrency_capacity: int


class EvaluationSummary(BaseModel):
    """Overall Phase 11 model benchmark report envelope."""
    model_name: str
    model_version: str
    quantization: str
    runtime: str
    hardware: str
    dataset_version: str
    total_samples_evaluated: int
    overall_pass_rate: float
    task_metrics: Dict[str, Any]
    safety_metrics: SafetyMetrics
    grounding_metrics: GroundingMetrics
    multilingual_metrics: MultilingualMetrics
    resource_metrics: ResourceMetrics
    error_distribution: Dict[str, int]
    recommendation: str
