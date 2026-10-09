"""CLINOVA AI — Evaluation Metrics & Error Taxonomy Unit Tests.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Verifies entity F1 calculations, grounding metrics, timeline ordering accuracy,
and the E001-E020 structured error classifier.
"""

from backend.tools.ai_evaluation.eval_schemas import (
    TimelinePayload,
    TimelineResult,
    TimelineEvent,
    ErrorTaxonomyCode,
)
from backend.tools.ai_evaluation.metrics import (
    calculate_entity_metrics,
    calculate_timeline_ordering_accuracy,
    calculate_grounding_metrics,
    classify_error_code,
)


def test_timeline_contracts():
    """Verifies Task 3 Timeline drafting schema conforms to BaseAIResponse envelope."""
    event1 = TimelineEvent(
        time_anchor="3 days ago",
        description="Fever and chills onset",
        source_evidence_id="ev-01",
        event_type="ONSET",
    )
    payload = TimelinePayload(
        events=[event1],
        chronology_summary="Onset 3 days ago of fever and chills.",
    )
    result = TimelineResult(
        status="SUCCESS",
        model="qwen2.5-3b-instruct",
        model_version="1.0.0",
        payload=payload,
    )
    assert result.status == "SUCCESS"
    assert result.epistemic_state == "AI_INFERRED"
    assert len(result.payload.events) == 1
    assert result.payload.events[0].time_anchor == "3 days ago"


def test_entity_metrics_exact_match():
    """Verifies entity precision, recall, F1 on exact matches."""
    extracted = ["chest pain", "shortness of breath", "fever"]
    gold = ["chest pain", "shortness of breath", "fever"]
    metrics = calculate_entity_metrics(extracted, gold)
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0
    assert metrics.unsupported_inference_rate == 0.0


def test_entity_metrics_partial():
    """Verifies entity metrics with false positives and false negatives."""
    extracted = ["chest pain", "dizziness"]
    gold = ["chest pain", "vomiting"]
    metrics = calculate_entity_metrics(extracted, gold)
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5
    assert metrics.unsupported_inference_rate == 0.5


def test_timeline_ordering_accuracy():
    """Verifies chronological order calculation."""
    # Correct order
    extracted = ["fever onset", "cough started", "admitted to ward"]
    gold = ["fever onset", "cough started", "admitted to ward"]
    acc = calculate_timeline_ordering_accuracy(extracted, gold)
    assert acc == 1.0

    # Inverted order
    inverted = ["admitted to ward", "cough started", "fever onset"]
    acc_inv = calculate_timeline_ordering_accuracy(inverted, gold)
    assert acc_inv == 0.0


def test_grounding_metrics_supported_and_phantom():
    """Verifies grounding claim rates and phantom evidence detection."""
    valid_ids = {"ev-01", "ev-02"}
    claims = [
        {"claim": "Chest pain for 2 days", "evidence_id": "ev-01", "status": "SUPPORTED"},
        {"claim": "HR 90 bpm", "evidence_id": "ev-02", "status": "SUPPORTED"},
        {"claim": "Took unknown pill", "evidence_id": "ev-non-existent", "status": "UNSUPPORTED"},
    ]
    g_metrics = calculate_grounding_metrics(claims, valid_ids)
    assert g_metrics.grounded_claim_rate == round(2 / 3, 4)
    assert g_metrics.phantom_evidence_rate == round(1 / 3, 4)


def test_error_taxonomy_classification():
    """Verifies mapping of failure categories to E001-E020 codes."""
    assert classify_error_code("injection", "prompt override") == ErrorTaxonomyCode.E012_PROMPT_INJECTION_SUCCESS
    assert classify_error_code("forbidden", "prescribe antibiotic") == ErrorTaxonomyCode.E013_FORBIDDEN_ACTION
    assert classify_error_code("phantom", "evidence citation missing") == ErrorTaxonomyCode.E001_HALLUCINATION
    assert classify_error_code("vital", "HR=450 impossible") == ErrorTaxonomyCode.E007_WRONG_NUMERICAL_VALUE
    assert classify_error_code("timeout", "request exceeded 5000ms") == ErrorTaxonomyCode.E015_TIMEOUT
    assert classify_error_code("schema", "missing field loc") == ErrorTaxonomyCode.E014_SCHEMA_FAILURE
