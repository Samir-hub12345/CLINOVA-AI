"""Interaction History Tracker for Phase 5 Intelligent Completion (Sub-Phase 5.2).

Maintains multi-turn context, prevents duplicate and redundant questions,
tracks skipped topics, and monitors patient burden and cognitive load.
"""

from typing import List, Set, Optional, Dict, Any
from app.models.completion import (
    CompletionQuestion,
    CompletionAnswer,
    QuestionStatus,
    QuestionType,
)


class InteractionHistoryTracker:
    """Tracks and evaluates interaction history across interview turns."""

    def get_asked_target_fields(self, questions: List[CompletionQuestion]) -> Set[str]:
        """Returns the set of canonical fields that have been queried in this session."""
        fields = set()
        for q in questions:
            if q.status in (
                QuestionStatus.PRESENTED.value,
                QuestionStatus.ANSWERED.value,
                QuestionStatus.SKIPPED.value,
            ):
                fields.add(q.target_field)
        return fields

    def get_answered_target_fields(self, questions: List[CompletionQuestion]) -> Set[str]:
        """Returns fields that have received an active answer (not skipped)."""
        fields = set()
        for q in questions:
            if q.status == QuestionStatus.ANSWERED.value and q.answer and not q.answer.is_skipped:
                fields.add(q.target_field)
        return fields

    def get_skipped_target_fields(self, questions: List[CompletionQuestion]) -> Set[str]:
        """Returns fields where the patient declined or skipped answering."""
        fields = set()
        for q in questions:
            if q.status == QuestionStatus.SKIPPED.value or (
                q.answer and q.answer.is_skipped
            ):
                fields.add(q.target_field)
        return fields

    def is_field_exhausted(
        self, target_field: str, questions: List[CompletionQuestion], max_attempts: int = 2
    ) -> bool:
        """Determines if a target field has been queried too many times without productive resolution."""
        attempts = 0
        for q in questions:
            if q.target_field == target_field:
                attempts += 1
                if q.answer and not q.answer.is_skipped:
                    return True  # Already successfully answered
        return attempts >= max_attempts

    def is_duplicate_question(
        self, question_text: str, questions: List[CompletionQuestion]
    ) -> bool:
        """Checks if identical or substantially identical question has already been asked."""
        normalized_new = " ".join(question_text.lower().strip().split())
        for q in questions:
            normalized_existing = " ".join(q.question_text.lower().strip().split())
            if normalized_new == normalized_existing:
                return True
        return False

    def calculate_patient_fatigue(self, questions: List[CompletionQuestion]) -> float:
        """Calculates a normalized patient fatigue score (0.0 = fresh, 1.0 = highly fatigued)."""
        if not questions:
            return 0.0

        turns = len(questions)
        base_fatigue = min(turns * 0.15, 0.75)

        # Additional fatigue for open-ended text questions
        open_text_count = sum(
            1 for q in questions if q.question_type == QuestionType.TEXT.value
        )
        text_penalty = min(open_text_count * 0.1, 0.25)

        return min(round(base_fatigue + text_penalty, 3), 1.0)

    def consecutive_skipped_count(self, questions: List[CompletionQuestion]) -> int:
        """Counts how many questions were skipped consecutively at the tail of the session."""
        count = 0
        for q in reversed(questions):
            if q.status == QuestionStatus.SKIPPED.value or (
                q.answer and q.answer.is_skipped
            ):
                count += 1
            elif q.status == QuestionStatus.ANSWERED.value and q.answer and not q.answer.is_skipped:
                break
        return count
