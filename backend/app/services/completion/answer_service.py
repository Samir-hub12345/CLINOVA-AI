"""Answer Capture and Evidence Creation Service for Phase 5 Intelligent Completion (Sub-Phase 5.9).

Validates patient answers, converts accepted answers into discrete CaseEvidence records,
links evidence provenance, and records question completion states.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.case_evidence import (
    CaseEvidence,
    EvidenceSourceType,
    VerificationState,
)
from app.models.completion import (
    CompletionSession,
    CompletionQuestion,
    CompletionAnswer,
    QuestionStatus,
    AnswerModality,
    CompletionSessionStatus,
)


class AnswerCaptureService:
    """Processes patient responses and translates validated answers into canonical evidence."""

    async def capture_answer(
        self,
        session: CompletionSession,
        question: CompletionQuestion,
        raw_answer_text: str,
        modality: str,
        is_skipped: bool,
        structured_payload: Optional[Dict[str, Any]],
        db: AsyncSession,
        patient_user_id: Optional[str] = None,
    ) -> Tuple[CompletionAnswer, Optional[CaseEvidence]]:
        """Captures an answer, validates it, and generates CaseEvidence if not skipped."""
        now = datetime.now(timezone.utc)
        clean_text = raw_answer_text.strip() if raw_answer_text else ""

        if is_skipped:
            # Patient opted to skip/decline
            answer = CompletionAnswer(
                id=str(uuid.uuid4()),
                question_id=question.id,
                session_id=session.id,
                case_id=session.case_id,
                patient_id=session.patient_id,
                raw_answer_text=clean_text or "Declined / Skipped",
                normalized_value="SKIPPED",
                structured_payload=structured_payload or {"skipped": True},
                answer_modality=AnswerModality.DECLINED_OR_SKIPPED.value,
                is_skipped=True,
                is_valid=True,
                validation_notes="Patient elected to skip this question.",
                evidence_id=None,
                answered_at=now,
            )
            db.add(answer)
            question.answer = answer

            question.status = QuestionStatus.SKIPPED.value
            question.answered_at = now
            session.questions_skipped_count += 1
            session.updated_at = now

            await db.flush()
            return answer, None

        if not clean_text:
            raise ValueError("Answer text cannot be empty unless the question is marked as skipped.")

        # Validate answer if question has options
        normalized_value = self._normalize_answer(question, clean_text)

        # 1. Create discrete CaseEvidence
        evidence = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=session.case_id,
            canonical_field=question.target_field,
            raw_value=clean_text,
            normalized_value=normalized_value,
            source_type=self._map_source_type(modality),
            verification_state=VerificationState.PATIENT_REPORTED,
            confidence_score=1.0,
            observed_at=now,
            created_by_user_id=patient_user_id,
            processor_name="Phase5_Intelligent_Completion",
            source_reference=f"Phase 5 Completion Turn {question.turn_number}",
            version=1,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(evidence)
        await db.flush()

        # 2. Create CompletionAnswer linked to evidence
        answer = CompletionAnswer(
            id=str(uuid.uuid4()),
            question_id=question.id,
            session_id=session.id,
            case_id=session.case_id,
            patient_id=session.patient_id,
            raw_answer_text=clean_text,
            normalized_value=normalized_value,
            structured_payload=structured_payload,
            answer_modality=modality,
            is_skipped=False,
            is_valid=True,
            validation_notes="Validated patient reported answer.",
            evidence_id=evidence.id,
            answered_at=now,
        )
        db.add(answer)
        question.answer = answer

        # Update question and session
        question.status = QuestionStatus.ANSWERED.value
        question.answered_at = now

        session.questions_answered_count += 1
        session.status = CompletionSessionStatus.PROCESSING_ANSWER.value
        session.updated_at = now

        await db.flush()
        return answer, evidence

    def _normalize_answer(self, question: CompletionQuestion, raw_text: str) -> str:
        """Translates raw choices into clean normalized representations."""
        if not question.options:
            return raw_text

        # Check for matching option value or label
        for opt in question.options:
            if str(opt.get("value")).lower() == raw_text.lower():
                return opt.get("label", raw_text)
            if str(opt.get("label")).lower() == raw_text.lower():
                return opt.get("label", raw_text)

        return raw_text

    def _map_source_type(self, modality_str: str) -> EvidenceSourceType:
        if modality_str == AnswerModality.PATIENT_VOICE.value:
            return EvidenceSourceType.PATIENT_VOICE
        if modality_str == AnswerModality.PATIENT_TEXT.value:
            return EvidenceSourceType.PATIENT_TEXT
        return EvidenceSourceType.PATIENT_REPORTED
