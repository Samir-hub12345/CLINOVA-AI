"""CLINOVA AI — AI Evaluation Package.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Contains evaluation schemas, error taxonomy (E001-E020), metric calculators,
and model evaluation harness.
"""

from backend.tools.ai_evaluation.eval_schemas import (
    TimelinePayload,
    TimelineResult,
    TimelineEvent,
    ErrorTaxonomyCode,
    EntityMetrics,
    GroundingMetrics,
    SafetyMetrics,
    MultilingualMetrics,
    ResourceMetrics,
    EvaluationSummary,
)
from backend.tools.ai_evaluation.metrics import (
    calculate_entity_metrics,
    calculate_timeline_ordering_accuracy,
    calculate_grounding_metrics,
    classify_error_code,
)
from backend.tools.ai_evaluation.evaluator import ModelEvaluator

__all__ = [
    "TimelinePayload",
    "TimelineResult",
    "TimelineEvent",
    "ErrorTaxonomyCode",
    "EntityMetrics",
    "GroundingMetrics",
    "SafetyMetrics",
    "MultilingualMetrics",
    "ResourceMetrics",
    "EvaluationSummary",
    "calculate_entity_metrics",
    "calculate_timeline_ordering_accuracy",
    "calculate_grounding_metrics",
    "classify_error_code",
    "ModelEvaluator",
]
