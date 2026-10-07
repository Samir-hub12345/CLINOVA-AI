"""Master Orchestrator Service for Phase 5 Intelligent Completion (Sub-Phase 5.14).

Coordinates the complete Phase 5 completion loop:
VERIFIED CASE -> INFORMATION GAPS -> CANDIDATES -> VALIDATION -> PRIORITIZATION ->
NEXT QUESTION -> PATIENT DELIVERY -> ANSWER CAPTURE -> EVIDENCE CREATION ->
CASE REBUILD -> RE-VERIFICATION -> STOPPING EVALUATION.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import TriageCase
from app.models.patient import Patient
from app.models.user import User
from app.models.case_evidence import CaseEvidence
from app.models.canonical_case import CaseSnapshot
from app.models.verification import VerificationRun
from app.models.completion import (
    CompletionSession,
    CompletionQuestion,
    CompletionAnswer,
    CompletionSessionStatus,
    QuestionStatus,
    StoppingCriterion,
)
from app.services.case_builder import CaseBuilderService
from app.services.verification import CaseVerificationService
from app.services.completion.domain import InformationGap, QuestionCandidate, PrioritizedQuestion
from app.services.completion.history_tracker import InteractionHistoryTracker
from app.services.completion.gap_engine import InformationGapEngine
from app.services.completion.candidate_engine import QuestionCandidateEngine
from app.services.completion.question_validator import QuestionValidator
from app.services.completion.prioritization_engine import QuestionPrioritizationEngine
from app.services.completion.selector_engine import NextBestQuestionSelector
from app.services.completion.delivery_service import QuestionDeliveryService
from app.services.completion.answer_service import AnswerCaptureService
from app.services.completion.rebuilder import CaseRebuildCoordinator
from app.services.completion.reverifier import CaseReverificationCoordinator
from app.services.completion.stopping_engine import StoppingEngine
from app.services.completion.safety_guard import CompletionSafetyGuard

logger = logging.getLogger("clinova.completion.service")


class CompletionService:
    """Master service for orchestrating intelligent completion interviews."""

    def __init__(self):
        self.gap_engine = InformationGapEngine()
        self.candidate_engine = QuestionCandidateEngine()
        self.validator = QuestionValidator()
        self.prioritization_engine = QuestionPrioritizationEngine()
        self.selector = NextBestQuestionSelector()
        self.delivery_service = QuestionDeliveryService()
        self.answer_service = AnswerCaptureService()
        self.rebuilder = CaseRebuildCoordinator()
        self.reverifier = CaseReverificationCoordinator()
        self.stopping_engine = StoppingEngine()
        self.safety_guard = CompletionSafetyGuard()
        self.history_tracker = InteractionHistoryTracker()

    async def get_or_create_session(
        self,
        case_id: str,
        db: AsyncSession,
        max_turns: int = 5,
        force_new: bool = False,
    ) -> CompletionSession:
        """Retrieves active completion session for the case or initializes a new one."""
        now = datetime.now(timezone.utc)

        # 1. Fetch case
        case_stmt = (
            select(TriageCase)
            .where(TriageCase.id == case_id)
            .options(selectinload(TriageCase.patient))
        )
        case_res = await db.execute(case_stmt)
        case = case_res.scalar_one_or_none()
        if not case:
            raise ValueError(f"Triage case with ID '{case_id}' not found.")

        # 2. Check for active existing session
        if not force_new:
            session_stmt = (
                select(CompletionSession)
                .where(
                    CompletionSession.case_id == case_id,
                    CompletionSession.is_current == True,
                    CompletionSession.status.in_([
                        CompletionSessionStatus.ACTIVE.value,
                        CompletionSessionStatus.WAITING_FOR_ANSWER.value,
                        CompletionSessionStatus.PROCESSING_ANSWER.value,
                    ]),
                )
                .options(
                    selectinload(CompletionSession.questions).selectinload(CompletionQuestion.answer),
                )
                .order_by(CompletionSession.created_at.desc())
            )
            sess_res = await db.execute(session_stmt)
            existing = sess_res.scalar_one_or_none()
            if existing:
                return existing

        # If forcing new, archive existing current sessions
        if force_new:
            await db.execute(
                update(CompletionSession)
                .where(CompletionSession.case_id == case_id)
                .values(is_current=False)
            )

        # 3. Fetch latest snapshot and verification run
        snapshot = await self._get_latest_snapshot(case_id, db)
        if not snapshot:
            # Build initial canonical case if not already built
            snapshot, _ = await CaseBuilderService().build_canonical_case(case_id, db)

        verification_run = await self._get_latest_verification(case_id, db)
        if not verification_run:
            verification_run = await CaseVerificationService().verify_case(case_id, db)

        # 4. Compute initial gaps
        initial_gaps = self.gap_engine.identify_gaps(snapshot, verification_run, [])
        initial_score = verification_run.review_readiness_score if verification_run else 0.0

        # 5. Create new session
        session = CompletionSession(
            id=str(uuid.uuid4()),
            case_id=case_id,
            patient_id=case.patient_id,
            encounter_id=case.encounter_id,
            initial_verification_run_id=verification_run.id if verification_run else None,
            latest_verification_run_id=verification_run.id if verification_run else None,
            status=CompletionSessionStatus.ACTIVE.value,
            case_version_started=snapshot.case_version,
            case_version_current=snapshot.case_version,
            current_turn=0,
            max_turns=max_turns,
            questions_asked_count=0,
            questions_answered_count=0,
            questions_skipped_count=0,
            initial_gap_count=len(initial_gaps),
            remaining_gap_count=len(initial_gaps),
            initial_readiness_score=initial_score,
            current_readiness_score=initial_score,
            engine_version="5.0.0",
            is_current=True,
            created_at=now,
            updated_at=now,
        )
        db.add(session)
        await db.flush()

        sess_stmt = (
            select(CompletionSession)
            .where(CompletionSession.id == session.id)
            .options(
                selectinload(CompletionSession.questions).selectinload(CompletionQuestion.answer),
            )
        )
        sess_res = await db.execute(sess_stmt)
        return sess_res.scalar_one()

    async def get_or_generate_next_question(
        self,
        case_id: str,
        db: AsyncSession,
        max_turns: int = 5,
    ) -> Tuple[CompletionSession, Optional[CompletionQuestion]]:
        """Returns pending question if already presented, or selects and delivers the next question."""
        session = await self.get_or_create_session(case_id, db, max_turns=max_turns)

        # 1. If session is already completed or stopped
        if session.status in (
            CompletionSessionStatus.COMPLETED.value,
            CompletionSessionStatus.STOPPED_MAX_TURNS.value,
            CompletionSessionStatus.STOPPED_NO_GAPS.value,
            CompletionSessionStatus.STOPPED_PATIENT_DECLINED.value,
            CompletionSessionStatus.FAILED.value,
        ):
            return session, None

        # 2. Check if a question is already presented and awaiting answer
        for q in session.questions:
            if q.status == QuestionStatus.PRESENTED.value:
                return session, q

        # 3. Read current state
        snapshot = await self._get_latest_snapshot(case_id, db)
        verification_run = await self._get_latest_verification(case_id, db)

        # 4. Identify remaining actionable gaps
        remaining_gaps = self.gap_engine.identify_gaps(
            snapshot, verification_run, session.questions
        )
        session.remaining_gap_count = len(remaining_gaps)

        # 5. Evaluate stopping conditions
        should_stop, stop_criterion, stop_reason = self.stopping_engine.evaluate_stopping(
            session=session,
            remaining_gaps=remaining_gaps,
            verification_run=verification_run,
            existing_questions=session.questions,
        )

        if should_stop:
            await self._finalize_session(session, stop_criterion, stop_reason, db)
            return session, None

        # 6. Generate candidate questions
        raw_candidates = self.candidate_engine.generate_candidates(remaining_gaps)

        # 7. Validate candidate questions
        valid_candidates = []
        for cand in raw_candidates:
            is_valid, reason = self.validator.validate_candidate(cand, session.questions)
            if is_valid:
                valid_candidates.append(cand)
            else:
                logger.debug(f"Candidate rejected: {reason}")

        # 8. Prioritize candidates
        prioritized = self.prioritization_engine.prioritize_candidates(
            valid_candidates, remaining_gaps, session.questions
        )

        # 9. Select next best question
        top_question, select_stop_reason = self.selector.select_next_question(
            session, prioritized, session.questions
        )

        if not top_question:
            # No valid question to ask; stop cleanly
            criterion = (
                StoppingCriterion.MAX_TURNS_REACHED
                if session.current_turn >= session.max_turns
                else StoppingCriterion.NO_CRITICAL_GAPS
            )
            await self._finalize_session(session, criterion, select_stop_reason or "Interview complete.", db)
            return session, None

        # 10. Enforce non-diagnostic safety guard before delivery
        self.safety_guard.enforce_non_diagnostic_boundary(top_question.candidate.question_text)

        # 11. Present question to patient
        presented_q = await self.delivery_service.present_question(session, top_question, db)
        return session, presented_q

    async def submit_answer(
        self,
        case_id: str,
        question_id: str,
        raw_answer_text: str,
        db: AsyncSession,
        modality: str = "patient_text",
        is_skipped: bool = False,
        structured_payload: Optional[Dict[str, Any]] = None,
        actor: Optional[User] = None,
    ) -> Dict[str, Any]:
        """Captures answer, produces evidence, rebuilds case, reverifies, and evaluates next turn."""
        session = await self.get_or_create_session(case_id, db)

        # 1. Locate target question
        q_stmt = select(CompletionQuestion).where(
            CompletionQuestion.id == question_id,
            CompletionQuestion.session_id == session.id,
        )
        q_res = await db.execute(q_stmt)
        question = q_res.scalar_one_or_none()
        if not question:
            raise ValueError(f"Completion question '{question_id}' not found in active session.")

        if (
            question.status in (QuestionStatus.ANSWERED.value, QuestionStatus.SKIPPED.value)
            or question.answer is not None
        ):
            raise ValueError(f"Question '{question_id}' has already been resolved ({question.status}).")

        # 2. Capture answer & create CaseEvidence
        patient_user_id = actor.id if actor else None
        try:
            answer, evidence = await self.answer_service.capture_answer(
                session=session,
                question=question,
                raw_answer_text=raw_answer_text,
                modality=modality,
                is_skipped=is_skipped,
                structured_payload=structured_payload,
                db=db,
                patient_user_id=patient_user_id,
            )
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Question '{question_id}' has already been answered by a concurrent request.")

        # 3. Red flag detection without autonomous triage
        if not is_skipped and raw_answer_text:
            red_flag_msg = self.safety_guard.check_for_red_flags(raw_answer_text)
            if red_flag_msg:
                question.is_safety_flag = True
                logger.warning(f"Case {case_id} turn {question.turn_number}: {red_flag_msg}")

        previous_readiness = session.current_readiness_score
        new_snapshot = None
        new_verification_run = None

        # 4. If evidence was created, trigger Rebuild (Phase 3) and Reverification (Phase 4)
        if evidence:
            try:
                new_snapshot, build_run = await self.rebuilder.rebuild_case(session, db)
                new_verification_run = await self.reverifier.reverify_case(session, db, actor=actor)
            except Exception as e:
                self.safety_guard.handle_session_failure(session, e)
                await db.commit()
                raise e
        else:
            # If skipped, fetch existing verification
            new_verification_run = await self._get_latest_verification(case_id, db)

        new_readiness = (
            new_verification_run.review_readiness_score
            if new_verification_run
            else previous_readiness
        )
        readiness_improved = new_readiness > previous_readiness

        # 5. Check remaining gaps & stopping criteria
        remaining_gaps = self.gap_engine.identify_gaps(
            new_snapshot or await self._get_latest_snapshot(case_id, db),
            new_verification_run,
            session.questions,
        )
        session.remaining_gap_count = len(remaining_gaps)

        should_stop, stop_criterion, stop_reason = self.stopping_engine.evaluate_stopping(
            session=session,
            remaining_gaps=remaining_gaps,
            verification_run=new_verification_run,
            existing_questions=session.questions,
        )

        next_q = None
        if should_stop:
            await self._finalize_session(session, stop_criterion, stop_reason, db)
        else:
            # Generate next question for upcoming turn
            _, next_q = await self.get_or_generate_next_question(case_id, db)

        await db.commit()

        return {
            "session_id": session.id,
            "case_id": session.case_id,
            "answer": answer,
            "new_evidence_id": evidence.id if evidence else None,
            "new_case_version": session.case_version_current,
            "rebuilt_snapshot_id": new_snapshot.id if new_snapshot else None,
            "verification_run_id": new_verification_run.id if new_verification_run else None,
            "new_readiness_score": new_readiness,
            "readiness_improved": readiness_improved,
            "next_question": next_q,
            "is_session_complete": session.status in (
                CompletionSessionStatus.COMPLETED.value,
                CompletionSessionStatus.STOPPED_MAX_TURNS.value,
                CompletionSessionStatus.STOPPED_NO_GAPS.value,
                CompletionSessionStatus.STOPPED_PATIENT_DECLINED.value,
                CompletionSessionStatus.STOPPED_ZERO_GAIN.value,
                CompletionSessionStatus.STOPPED_SAFETY_LIMIT.value,
                CompletionSessionStatus.FAILED.value,
                CompletionSessionStatus.ABORTED.value,
            ),
            "stopping_reason": session.stopping_reason,
            "stopping_criterion": session.stopping_criterion,
        }

    async def complete_session_manually(
        self,
        case_id: str,
        reason: str,
        db: AsyncSession,
    ) -> CompletionSession:
        """Manually concludes the completion interview."""
        session = await self.get_or_create_session(case_id, db)
        await self._finalize_session(
            session,
            StoppingCriterion.PATIENT_DECLINED,
            f"Manually concluded: {reason}",
            db,
        )
        await db.commit()
        return session

    async def get_session_status(
        self,
        case_id: str,
        db: AsyncSession,
    ) -> Optional[CompletionSession]:
        """Retrieves the latest completion session for a case with all questions and answers."""
        stmt = (
            select(CompletionSession)
            .where(CompletionSession.case_id == case_id)
            .options(
                selectinload(CompletionSession.questions).selectinload(CompletionQuestion.answer),
            )
            .order_by(CompletionSession.created_at.desc())
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def _finalize_session(
        self,
        session: CompletionSession,
        criterion: Optional[StoppingCriterion],
        reason: Optional[str],
        db: AsyncSession,
    ) -> None:
        """Finalizes the session state and records summary."""
        now = datetime.now(timezone.utc)
        criterion_val = criterion.value if criterion else StoppingCriterion.NO_CRITICAL_GAPS.value

        if criterion == StoppingCriterion.MAX_TURNS_REACHED:
            session.status = CompletionSessionStatus.STOPPED_MAX_TURNS.value
        elif criterion == StoppingCriterion.PATIENT_DECLINED:
            session.status = CompletionSessionStatus.STOPPED_PATIENT_DECLINED.value
        elif criterion == StoppingCriterion.ZERO_INFORMATION_GAIN:
            session.status = CompletionSessionStatus.STOPPED_ZERO_GAIN.value
        elif criterion == StoppingCriterion.SAFETY_ESCALATION:
            session.status = CompletionSessionStatus.STOPPED_SAFETY_LIMIT.value
        elif criterion in (StoppingCriterion.NO_CRITICAL_GAPS, StoppingCriterion.READINESS_ACHIEVED):
            session.status = CompletionSessionStatus.COMPLETED.value
        else:
            session.status = CompletionSessionStatus.COMPLETED.value

        session.stopping_criterion = criterion_val
        session.stopping_reason = reason or "Intelligent completion concluded."
        session.completed_at = now
        session.updated_at = now

        session.completion_summary = {
            "initial_readiness": session.initial_readiness_score,
            "final_readiness": session.current_readiness_score,
            "readiness_delta": round(session.current_readiness_score - session.initial_readiness_score, 4),
            "turns_taken": session.current_turn,
            "questions_answered": session.questions_answered_count,
            "questions_skipped": session.questions_skipped_count,
            "initial_gaps": session.initial_gap_count,
            "remaining_gaps": session.remaining_gap_count,
            "gaps_resolved": max(0, session.initial_gap_count - session.remaining_gap_count),
        }
        await db.flush()

    async def _get_latest_snapshot(self, case_id: str, db: AsyncSession) -> Optional[CaseSnapshot]:
        stmt = (
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id, CaseSnapshot.is_current == True)
            .options(
                selectinload(CaseSnapshot.facts),
                selectinload(CaseSnapshot.timeline_events),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def _get_latest_verification(self, case_id: str, db: AsyncSession) -> Optional[VerificationRun]:
        stmt = (
            select(VerificationRun)
            .where(VerificationRun.case_id == case_id, VerificationRun.is_current == True)
            .options(
                selectinload(VerificationRun.findings),
                selectinload(VerificationRun.conflicts),
            )
            .order_by(VerificationRun.completed_at.desc())
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()
