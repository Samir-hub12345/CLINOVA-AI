"""Question Prioritization Engine for Phase 5 Intelligent Completion (Sub-Phase 5.6).

Scores and ranks candidate questions using deterministic multi-attribute utility:
clinical information utility, gap severity weight, and patient burden penalty.
"""

from typing import List, Dict, Any, Optional
from app.models.completion import CompletionQuestion
from app.models.verification import FindingSeverity
from app.services.completion.domain import (
    InformationGap,
    QuestionCandidate,
    PrioritizedQuestion,
)
from app.services.completion.history_tracker import InteractionHistoryTracker


class QuestionPrioritizationEngine:
    """Prioritizes validated candidate questions based on clinical utility and patient burden."""

    SEVERITY_WEIGHTS = {
        FindingSeverity.BLOCKING: 1.0,
        FindingSeverity.HIGH: 0.8,
        FindingSeverity.MEDIUM: 0.5,
        FindingSeverity.LOW: 0.3,
        FindingSeverity.INFO: 0.1,
    }

    def __init__(self):
        self.history_tracker = InteractionHistoryTracker()

    def prioritize_candidates(
        self,
        candidates: List[QuestionCandidate],
        gaps: List[InformationGap],
        existing_questions: List[CompletionQuestion],
    ) -> List[PrioritizedQuestion]:
        """Calculates composite priority score for each candidate and ranks them."""
        # Index gaps by ID for fast lookup
        gap_map = {g.gap_id: g for g in gaps}

        # Calculate current patient fatigue
        patient_fatigue = self.history_tracker.calculate_patient_fatigue(existing_questions)

        scored: List[PrioritizedQuestion] = []

        for candidate in candidates:
            gap = gap_map.get(candidate.target_gap_id)
            severity = gap.severity if gap else FindingSeverity.MEDIUM
            severity_weight = self.SEVERITY_WEIGHTS.get(severity, 0.5)

            utility = candidate.base_clinical_utility

            # Burden penalty: base burden + fatigue penalty
            burden = candidate.burden_score + (patient_fatigue * 0.10)

            # Composite deterministic scoring formula:
            # Score = 0.50 * utility + 0.40 * severity - 0.10 * burden
            raw_score = (0.50 * utility) + (0.40 * severity_weight) - (0.10 * burden)
            normalized_score = max(0.0, min(1.0, round(raw_score, 4)))

            scored.append(
                PrioritizedQuestion(
                    candidate=candidate,
                    priority_score=normalized_score,
                    rank=0,
                    utility_score=round(utility, 4),
                    gap_severity_weight=round(severity_weight, 4),
                    burden_penalty=round(burden, 4),
                    validation_status="VALID",
                )
            )

        # Sort descending by priority score; tie-break on candidate_id for stability
        scored.sort(key=lambda x: (x.priority_score, x.utility_score, x.candidate.candidate_id), reverse=True)

        # Assign ranks
        for idx, item in enumerate(scored, 1):
            item.rank = idx

        return scored
