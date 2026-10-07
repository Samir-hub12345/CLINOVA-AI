"""Patient Question Delivery Service for Phase 5 Intelligent Completion (Sub-Phase 5.8).

Manages question presentation, updates question state, logs presentation timestamps,
and prepares patient-facing interview view models.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.completion import (
    CompletionSession,
    CompletionQuestion,
    QuestionStatus,
    CompletionSessionStatus,
)
from app.services.completion.domain import PrioritizedQuestion


class QuestionDeliveryService:
    """Manages the lifecycle transition of presenting a question to a patient."""

    async def present_question(
        self,
        session: CompletionSession,
        prioritized_q: PrioritizedQuestion,
        db: AsyncSession,
    ) -> CompletionQuestion:
        """Creates and marks a question as PRESENTED in the database."""
        now = datetime.now(timezone.utc)
        candidate = prioritized_q.candidate

        next_turn = session.current_turn + 1

        db_question = CompletionQuestion(
            session=session,
            session_id=session.id,
            case_id=session.case_id,
            turn_number=next_turn,
            target_gap_id=candidate.target_gap_id,
            target_gap_type=(
                candidate.target_gap_type.value
                if hasattr(candidate.target_gap_type, "value")
                else str(candidate.target_gap_type)
            ),
            target_field=candidate.target_field,
            question_text=candidate.question_text,
            question_type=(
                candidate.question_type.value
                if hasattr(candidate.question_type, "value")
                else str(candidate.question_type)
            ),
            options=candidate.options,
            placeholder=candidate.placeholder,
            priority_score=prioritized_q.priority_score,
            clinical_rationale=candidate.clinical_rationale,
            status=QuestionStatus.PRESENTED.value,
            is_safety_flag=candidate.is_safety_flag,
            created_at=now,
            presented_at=now,
        )

        db.add(db_question)
        if session.questions is not None and db_question not in session.questions:
            session.questions.append(db_question)

        # Update session state
        session.current_turn = next_turn
        session.questions_asked_count += 1
        session.status = CompletionSessionStatus.WAITING_FOR_ANSWER.value
        session.updated_at = now

        await db.flush()
        return db_question
