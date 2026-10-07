"""Canonical Patient Case Intelligence Build models for Clinova AI.

Supports immutable case snapshots, build runs, discrete structured facts,
chronological timeline events, and multi-source provenance.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class BuildRunStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    BUILDING = "building"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    REBUILD_REQUIRED = "rebuild_required"


class FactPolarity(str, enum.Enum):
    AFFIRMED = "AFFIRMED"
    NEGATED = "NEGATED"


class FactCertainty(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    REPORTED = "REPORTED"
    UNCERTAIN = "UNCERTAIN"
    APPROXIMATE = "APPROXIMATE"


class TemporalStatus(str, enum.Enum):
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    RESOLVED = "RESOLVED"
    RECURRING = "RECURRING"
    ONGOING = "ONGOING"
    UNKNOWN = "UNKNOWN"


class CaseBuildRun(Base):
    """Tracks a single execution of the Canonical Patient Case Builder."""
    __tablename__ = "case_build_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default=BuildRunStatus.BUILDING.value, nullable=False, index=True
    )
    trigger_type: Mapped[str] = mapped_column(
        String(50), default="manual_rebuild", nullable=False
    )
    input_evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    facts_extracted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    facts_rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    target_case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    build_logic_version: Mapped[str] = mapped_column(String(50), default="3.0.0", nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), default="clinova_rule_builder", nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warnings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case = relationship("TriageCase")
    snapshots = relationship("CaseSnapshot", back_populates="build_run")

    __table_args__ = (
        Index("ix_case_build_runs_case_status", "case_id", "status"),
    )


class CaseSnapshot(Base):
    """Immutable versioned snapshot of the compiled Canonical Patient Case."""
    __tablename__ = "case_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    build_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_build_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    build_version: Mapped[str] = mapped_column(String(50), default="3.0.0", nullable=False)

    provider_name: Mapped[str] = mapped_column(String(100), default="clinova_rule_builder", nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Full structured Canonical Case data dictionary
    case_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    delta_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    case = relationship("TriageCase")
    build_run = relationship("CaseBuildRun", back_populates="snapshots")
    facts = relationship("CanonicalFact", back_populates="snapshot", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_case_snapshots_case_version", "case_id", "case_version", unique=True),
        Index("ix_case_snapshots_case_current", "case_id", "is_current"),
    )


class CanonicalFact(Base):
    """Discrete structured clinical fact atom linked to evidence and case snapshot."""
    __tablename__ = "canonical_facts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("case_snapshots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # symptom, vital, lab_value, medication, allergy, documented_condition, family_history
    )
    concept: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    polarity: Mapped[str] = mapped_column(
        String(20), default=FactPolarity.AFFIRMED.value, nullable=False
    )
    certainty: Mapped[str] = mapped_column(
        String(20), default=FactCertainty.REPORTED.value, nullable=False
    )
    attribution: Mapped[str] = mapped_column(
        String(50), default="PATIENT_REPORTED", nullable=False
    )
    temporal_status: Mapped[str] = mapped_column(
        String(20), default=TemporalStatus.CURRENT.value, nullable=False
    )

    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    onset_approximate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    source_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_span: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supporting_evidence_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # Multiple sources

    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conflicting_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conflicting_source_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    verification_state: Mapped[str] = mapped_column(String(50), default="unverified", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    snapshot = relationship("CaseSnapshot", back_populates="facts")
    source_evidence = relationship("CaseEvidence")

    __table_args__ = (
        Index("ix_canonical_facts_case_category", "case_id", "category"),
        Index("ix_canonical_facts_snapshot_concept", "snapshot_id", "concept"),
    )


class TimelineEvent(Base):
    """Chronological event node anchored to evidence within a case snapshot."""
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("case_snapshots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # symptom_onset, consultation, test_performed, procedure, medication_started
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    relative_time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approximate_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    temporal_status: Mapped[str] = mapped_column(
        String(20), default=TemporalStatus.CURRENT.value, nullable=False
    )

    source_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True, index=True
    )
    attribution: Mapped[str] = mapped_column(String(50), default="PATIENT_REPORTED", nullable=False)
    certainty: Mapped[str] = mapped_column(String(20), default=FactCertainty.REPORTED.value, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    snapshot = relationship("CaseSnapshot", back_populates="timeline_events")
    source_evidence = relationship("CaseEvidence")

    __table_args__ = (
        Index("ix_timeline_events_case_order", "case_id", "order_index"),
    )
