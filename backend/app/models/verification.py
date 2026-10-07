"""Clinical Information Verification & Review Readiness Models for Clinova AI (Phase 4).

Supports verification runs, discrete verification findings, cross-source conflicts,
and explainable review readiness assessments.
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
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class VerificationRunStatus(str, enum.Enum):
    REQUESTED = "requested"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    ABORTED = "aborted"


class ReviewReadinessLevel(str, enum.Enum):
    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    REVIEW_READY_WITH_FLAGS = "review_ready_with_flags"
    REVIEW_READY = "review_ready"


class FindingSeverity(str, enum.Enum):
    BLOCKING = "BLOCKING"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingType(str, enum.Enum):
    STRUCTURAL = "STRUCTURAL"
    COMPLETENESS = "COMPLETENESS"
    CONFLICT = "CONFLICT"
    TEMPORAL = "TEMPORAL"
    PROVENANCE = "PROVENANCE"
    UNCERTAINTY = "UNCERTAINTY"
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"


class FindingCategory(str, enum.Enum):
    IDENTITY = "IDENTITY"
    ENCOUNTER = "ENCOUNTER"
    PRESENTING_INFORMATION = "PRESENTING_INFORMATION"
    SYMPTOM_INFORMATION = "SYMPTOM_INFORMATION"
    TIMELINE = "TIMELINE"
    DOCUMENTS = "DOCUMENTS"
    MEASUREMENTS = "MEASUREMENTS"
    HISTORY = "HISTORY"
    SOURCE_METADATA = "SOURCE_METADATA"
    VERIFICATION = "VERIFICATION"


class FindingStatus(str, enum.Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED_BY_NEW_EVIDENCE = "RESOLVED_BY_NEW_EVIDENCE"
    RESOLVED_BY_HUMAN_VERIFICATION = "RESOLVED_BY_HUMAN_VERIFICATION"
    RESOLVED_BY_CORRECTION = "RESOLVED_BY_CORRECTION"
    DISMISSED_WITH_REASON = "DISMISSED_WITH_REASON"


class ConflictType(str, enum.Enum):
    VALUE_CONFLICT = "VALUE_CONFLICT"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    MODALITY_CONFLICT = "MODALITY_CONFLICT"
    UNIT_CONFLICT = "UNIT_CONFLICT"
    DUPLICATE_CONFLICT = "DUPLICATE_CONFLICT"
    STATUS_CONFLICT = "STATUS_CONFLICT"
    VERIFICATION_CONFLICT = "VERIFICATION_CONFLICT"


class CompletenessFieldStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"
    PARTIALLY_AVAILABLE = "PARTIALLY_AVAILABLE"


class VerificationRun(Base):
    """Tracks a single execution of the Phase 4 Clinical Verification Engine."""
    __tablename__ = "verification_runs"

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
    case_snapshot_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_snapshots.id", ondelete="SET NULL"), nullable=True, index=True
    )
    case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), default=VerificationRunStatus.RUNNING.value, nullable=False, index=True
    )
    engine_version: Mapped[str] = mapped_column(String(50), default="4.0.0", nullable=False)
    ruleset_version: Mapped[str] = mapped_column(String(50), default="4.0.0", nullable=False)

    # Review readiness evaluation
    review_readiness_status: Mapped[str] = mapped_column(
        String(50), default=ReviewReadinessLevel.NOT_READY.value, nullable=False, index=True
    )
    review_readiness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_readiness_reasons: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Finding telemetry
    findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocking_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    info_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unresolved_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resolved_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Subsystem statuses
    structural_integrity_status: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)
    completeness_status: Mapped[str] = mapped_column(String(50), default="COMPLETE", nullable=False)
    consistency_status: Mapped[str] = mapped_column(String(50), default="CONSISTENT", nullable=False)
    temporal_status: Mapped[str] = mapped_column(String(50), default="COHERENT", nullable=False)
    provenance_status: Mapped[str] = mapped_column(String(50), default="COMPLETE", nullable=False)
    uncertainty_status: Mapped[str] = mapped_column(String(50), default="CLEAR", nullable=False)

    # Execution telemetry and metadata
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    case = relationship("TriageCase")
    patient = relationship("Patient")
    encounter = relationship("Encounter")
    snapshot = relationship("CaseSnapshot")
    findings = relationship(
        "VerificationFinding", back_populates="verification_run", cascade="all, delete-orphan"
    )
    conflicts = relationship(
        "VerificationConflict", back_populates="verification_run", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_verification_runs_case_status", "case_id", "status"),
        Index("ix_verification_runs_case_ver_composite", "case_id", "case_version"),
        Index("ix_verification_runs_case_current", "case_id", "is_current"),
    )



class VerificationFinding(Base):
    """Discrete, explainable finding identified during case verification."""
    __tablename__ = "verification_findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    verification_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("verification_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)

    finding_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    field_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(20), default=FindingSeverity.MEDIUM.value, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default=FindingStatus.UNRESOLVED.value, nullable=False, index=True
    )
    is_blocking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    expected_information: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observed_information: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_evidence_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    fact_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    timeline_event_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_version: Mapped[str] = mapped_column(String(50), default="4.0.0", nullable=False)

    # Resolution metadata
    resolved_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    verification_run = relationship("VerificationRun", back_populates="findings")
    case = relationship("TriageCase")
    resolved_by_user = relationship("User")

    __table_args__ = (
        Index("ix_verification_findings_case_severity", "case_id", "severity"),
        Index("ix_verification_findings_case_status", "case_id", "status"),
        Index("ix_verification_findings_run_status", "verification_run_id", "status"),
    )


class VerificationConflict(Base):
    """Explicit cross-source or cross-modal contradiction preserved without silent overwrite."""
    __tablename__ = "verification_conflicts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    verification_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("verification_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)

    conflict_type: Mapped[str] = mapped_column(
        String(50), default=ConflictType.VALUE_CONFLICT.value, nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(20), default=FindingSeverity.HIGH.value, nullable=False
    )

    # Source A preservation
    source_a_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True
    )
    source_a_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_a_modality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_a_value: Mapped[str] = mapped_column(Text, nullable=False)
    source_a_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Source B preservation
    source_b_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True
    )
    source_b_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_b_modality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_b_value: Mapped[str] = mapped_column(Text, nullable=False)
    source_b_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resolution_state: Mapped[str] = mapped_column(
        String(50), default=FindingStatus.UNRESOLVED.value, nullable=False, index=True
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rule_id: Mapped[str] = mapped_column(String(100), default="cross_source_conflict_rule", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    verification_run = relationship("VerificationRun", back_populates="conflicts")
    case = relationship("TriageCase")
    source_a_evidence = relationship("CaseEvidence", foreign_keys=[source_a_evidence_id])
    source_b_evidence = relationship("CaseEvidence", foreign_keys=[source_b_evidence_id])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by_user_id])

    __table_args__ = (
        Index("ix_verification_conflicts_case_field", "case_id", "field_name"),
        Index("ix_verification_conflicts_state", "case_id", "resolution_state"),
    )
