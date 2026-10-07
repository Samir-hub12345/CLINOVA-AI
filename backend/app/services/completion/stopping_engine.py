"""Stopping and Completion Engine for Phase 5 Intelligent Completion (Sub-Phase 5.12).

Evaluates interview stopping criteria, detects information plateau, enforces safety caps,
and formalizes completion state transitions.
"""

from typing import Tuple, Optional, Dict, Any, List
from app.models.completion import (
    CompletionSession,
    CompletionSessionStatus,
    StoppingCriterion,
    CompletionQuestion,
)
from app.models.verification import (
    VerificationRun,
    ReviewReadinessLevel,
    FindingSeverity,
)
from app.services.completion.domain import InformationGap
from app.services.completion.history_tracker import InteractionHistoryTracker


class StoppingEngine:
    """Evaluates whether an intelligent completion interview should terminate."""

    READINESS_TARGET = 0.85

    def __init__(self):
        self.history_tracker = InteractionHistoryTracker()

    def evaluate_stopping(
        self,
        session: CompletionSession,
        remaining_gaps: List[InformationGap],
        verification_run: Optional[VerificationRun],
        existing_questions: List[CompletionQuestion],
        manual_stop_reason: Optional[str] = None,
    ) -> Tuple[bool, Optional[StoppingCriterion], Optional[str]]:
        """Evaluates all stopping criteria. Returns (should_stop, stopping_criterion, reason)."""
        # 1. Explicit manual stop requested
        if manual_stop_reason:
            return (
                True,
                StoppingCriterion.PATIENT_DECLINED,
                f"Patient or clinician concluded interview: {manual_stop_reason}",
            )

        # 2. Maximum interview turns ceiling reached
        if session.current_turn >= session.max_turns:
            return (
                True,
                StoppingCriterion.MAX_TURNS_REACHED,
                f"Reached maximum interview limit of {session.max_turns} questions.",
            )

        # 3. Patient opted out / skipped consecutive questions
        consecutive_skips = self.history_tracker.consecutive_skipped_count(existing_questions)
        if consecutive_skips >= 2:
            return (
                True,
                StoppingCriterion.PATIENT_DECLINED,
                f"Patient skipped {consecutive_skips} consecutive questions; respecting choice to pause interview.",
            )

        # 4. No remaining gaps at all
        if not remaining_gaps:
            if verification_run and verification_run.review_readiness_score >= self.READINESS_TARGET:
                return (
                    True,
                    StoppingCriterion.READINESS_ACHIEVED,
                    f"Target review readiness ({verification_run.review_readiness_score:.2f}) achieved with all gaps resolved.",
                )
            return (
                True,
                StoppingCriterion.NO_CRITICAL_GAPS,
                "All identified clinical information gaps have been resolved.",
            )

        # 5. Critical gaps check (BLOCKING or HIGH severity)
        critical_gaps = [
            g for g in remaining_gaps
            if g.severity in (FindingSeverity.BLOCKING, FindingSeverity.HIGH, "BLOCKING", "HIGH")
        ]

        # 5a. Information Plateau / Zero Information Gain
        if not critical_gaps and session.questions_answered_count >= 2 and verification_run:
            if session.current_readiness_score <= session.initial_readiness_score:
                return (
                    True,
                    StoppingCriterion.ZERO_INFORMATION_GAIN,
                    "Information plateau reached: subsequent answers yielded zero material improvement in case readiness.",
                )

        # 5b. Stop if no critical gaps remain, at least one turn has run, and review readiness target is reached
        if not critical_gaps and session.current_turn > 0 and verification_run:
            if (
                verification_run.review_readiness_status == ReviewReadinessLevel.REVIEW_READY.value
                or verification_run.review_readiness_score >= self.READINESS_TARGET
            ):
                return (
                    True,
                    StoppingCriterion.READINESS_ACHIEVED,
                    f"Target review readiness ({verification_run.review_readiness_score:.2f}) successfully achieved.",
                )
            elif verification_run.review_readiness_score >= 0.70:
                return (
                    True,
                    StoppingCriterion.NO_CRITICAL_GAPS,
                    "All high-priority clinical gaps resolved; case package is ready for clinician review.",
                )

        return False, None, None
