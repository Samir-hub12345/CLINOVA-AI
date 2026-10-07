"""Intelligent Information Completion & Adaptive Follow-up Models for Clinova AI (Phase 5).

Supports completion sessions, patient-facing follow-up questions, validated answers,
evidence provenance linkage, information gap tracking, and safe stopping control.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CompletionSessionStatus(str, enum.Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    PROCESSING_ANSWER = "processing_answer"
    COMPLETED = "completed"
    STOPPED_MAX_TURNS = "stopped_max_turns"
    STOPPED_NO_GAPS = "stopped_no_gaps"
    STOPPED_PATIENT_DECLINED = "stopped_patient_declined"
    STOPPED_ZERO_GAIN = "stopped_zero_gain"
    STOPPED_SAFETY_LIMIT = "stopped_safety_limit"
    FAILED = "failed"
    ABORTED = "aborted"


class QuestionType(str, enum.Enum):
    TEXT = "text"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    DATE_TIME = "date_time"


class QuestionStatus(str, enum.Enum):
    CANDIDATE = "candidate"
    SELECTED = "selected"
    PRESENTED = "presented"
    ANSWERED = "answered"
    SKIPPED = "skipped"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class AnswerModality(str, enum.Enum):
    PATIENT_TEXT = "patient_text"
    PATIENT_CHOICE = "patient_choice"
    PATIENT_VOICE = "patient_voice"
    DECLINED_OR_SKIPPED = "declined_or_skipped"


class GapType(str, enum.Enum):
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    UNRESOLVED_CONFLICT = "UNRESOLVED_CONFLICT"
    UNCERTAIN_FACT = "UNCERTAIN_FACT"
    INCOMPLETE_TIMELINE = "INCOMPLETE_TIMELINE"
    CONTEXT_ENRICHMENT = "CONTEXT_ENRICHMENT"


class StoppingCriterion(str, enum.Enum):
    NO_CRITICAL_GAPS = "NO_CRITICAL_GAPS"
    READINESS_ACHIEVED = "READINESS_ACHIEVED"
    MAX_TURNS_REACHED = "MAX_TURNS_REACHED"
    PATIENT_DECLINED = "PATIENT_DECLINED"
    ZERO_INFORMATION_GAIN = "ZERO_INFORMATION_GAIN"
    SAFETY_ESCALATION = "SAFETY_ESCALATION"


class CompletionSession(Base):
    """Tracks a patient-facing intelligent completion session for a canonical triage case."""
    __tablename__ = "completion_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    encounter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    initial_verification_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("verification_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    latest_verification_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("verification_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default=CompletionSessionStatus.ACTIVE.value, nullable=False, index=True
    )
    case_version_started: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    case_version_current: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    current_turn: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_turns: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    questions_asked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_answered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_skipped_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    initial_gap_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remaining_gap_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    initial_readiness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_readiness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    stopping_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stopping_criterion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    completion_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    engine_version: Mapped[str] = mapped_column(String(50), default="5.0.0", nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case = relationship("TriageCase")
    patient = relationship("Patient")
    questions = relationship(
        "CompletionQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="CompletionQuestion.turn_number",
        lazy="selectin",
    )
    answers = relationship(
        "CompletionAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_completion_sessions_case_status", "case_id", "status"),
        Index("ix_completion_sessions_case_current", "case_id", "is_current"),
    )


class CompletionQuestion(Base):
    """Discrete, patient-facing follow-up question generated to fill a verified information gap."""
    __tablename__ = "completion_questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("completion_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)

    target_gap_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_gap_type: Mapped[str] = mapped_column(String(50), default=GapType.MISSING_REQUIRED_FIELD.value, nullable=False)
    target_field: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), default=QuestionType.TEXT.value, nullable=False
    )
    options: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    placeholder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    priority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    clinical_rationale: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), default=QuestionStatus.CANDIDATE.value, nullable=False, index=True
    )
    is_safety_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    presented_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    session = relationship("CompletionSession", back_populates="questions")
    case = relationship("TriageCase")
    answer = relationship(
        "CompletionAnswer",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_completion_questions_session_turn", "session_id", "turn_number"),
        Index("ix_completion_questions_case_target", "case_id", "target_field"),
    )


class CompletionAnswer(Base):
    """Discrete answer submitted by a patient to an intelligent completion question."""
    __tablename__ = "completion_answers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("completion_questions.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("completion_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )

    raw_answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    answer_modality: Mapped[str] = mapped_column(
        String(50), default=AnswerModality.PATIENT_TEXT.value, nullable=False
    )
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True, index=True
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    question = relationship("CompletionQuestion", back_populates="answer")
    session = relationship("CompletionSession", back_populates="answers")
    case = relationship("TriageCase")
    patient = relationship("Patient")
    evidence = relationship("CaseEvidence")

    __table_args__ = (
        Index("ix_completion_answers_case_question", "case_id", "question_id"),
    )
