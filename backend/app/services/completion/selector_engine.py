"""Next-Best-Question Selector for Phase 5 Intelligent Completion (Sub-Phase 5.7).

Selects the single best candidate question to ask next, enforcing interview turn budgets,
fatigue thresholds, safety limits, and respectful abstention.
"""

from typing import Optional, List, Tuple
from app.models.completion import (
    CompletionSession,
    CompletionQuestion,
    QuestionStatus,
)
from app.services.completion.domain import PrioritizedQuestion
from app.services.completion.history_tracker import InteractionHistoryTracker


class NextBestQuestionSelector:
    """Selects the single optimal next question or determines when to abstain."""

    MIN_SCORE_THRESHOLD = 0.20
    MAX_CONSECUTIVE_SKIPS = 2

    def __init__(self):
        self.history_tracker = InteractionHistoryTracker()

    def select_next_question(
        self,
        session: CompletionSession,
        prioritized_questions: List[PrioritizedQuestion],
        existing_questions: List[CompletionQuestion],
    ) -> Tuple[Optional[PrioritizedQuestion], Optional[str]]:
        """Selects the next question or returns (None, stopping_reason)."""
        # 1. Turn budget check
        if session.current_turn >= session.max_turns:
            return None, f"Maximum interview turns limit ({session.max_turns}) reached."

        # 2. Consecutive skip check (respect patient preference)
        consecutive_skips = self.history_tracker.consecutive_skipped_count(existing_questions)
        if consecutive_skips >= self.MAX_CONSECUTIVE_SKIPS:
            return None, f"Patient skipped {consecutive_skips} consecutive questions; respecting patient preference to pause intake."

        # 3. No candidate questions available
        if not prioritized_questions:
            return None, "No remaining clinical information gaps identified."

        # 4. Check highest ranked candidate
        top_question = prioritized_questions[0]

        # 5. Abstention check: if highest score is too low and no high-severity gaps
        if top_question.priority_score < self.MIN_SCORE_THRESHOLD:
            return None, f"Remaining information utility ({top_question.priority_score}) is below completion threshold."

        return top_question, None
