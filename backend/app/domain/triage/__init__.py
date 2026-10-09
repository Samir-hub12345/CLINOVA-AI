"""CLINOVA AI — Deterministic Clinical Triage & Physiological Engine.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.
Grounded in RCP NEWS2 (2017), Shock Index (Allgöwer & Burri, 1967),
and DOC-07/DOC-08 evidence & provenance governance.

100% Decoupled from stochastic AI models.
Pure deterministic functions, auditable rules, explainable outputs.
"""

from app.domain.triage.scoring import (
    calculate_deterministic_news2,
    calculate_deterministic_shock_index,
    evaluate_vital_freshness,
    FRESH_THRESHOLD_MINUTES,
    STALE_THRESHOLD_MINUTES,
    NEWS2_VERSION,
    SHOCK_INDEX_VERSION,
)
from app.domain.triage.red_flags import (
    evaluate_deterministic_red_flags,
    RED_FLAGS_VERSION,
)
from app.domain.triage.priority import (
    evaluate_priority_tier,
    sort_clinical_queue,
    PRIORITY_RULES_VERSION,
)
from app.domain.triage.engine import (
    compute_deterministic_triage,
)

__all__ = [
    "calculate_deterministic_news2",
    "calculate_deterministic_shock_index",
    "evaluate_vital_freshness",
    "evaluate_deterministic_red_flags",
    "evaluate_priority_tier",
    "sort_clinical_queue",
    "compute_deterministic_triage",
    "FRESH_THRESHOLD_MINUTES",
    "STALE_THRESHOLD_MINUTES",
    "NEWS2_VERSION",
    "SHOCK_INDEX_VERSION",
    "RED_FLAGS_VERSION",
    "PRIORITY_RULES_VERSION",
]
