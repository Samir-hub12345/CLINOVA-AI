import enum
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class EvidenceSourceType(str, enum.Enum):
    PATIENT_REPORTED = "patient_reported"
    PATIENT_TEXT = "patient_text"
    PATIENT_VOICE = "patient_voice"
    STAFF_ENTERED = "staff_entered"
    STAFF_VERIFIED = "staff_verified"
    CLINICIAN_ENTERED = "clinician_entered"
    CLINICIAN_CONFIRMED = "clinician_confirmed"
    DOCUMENT_DERIVED = "document_derived"
    OCR_DERIVED = "ocr_derived"
    AI_EXTRACTED = "ai_extracted"
    AI_INFERRED = "ai_inferred"
    SYSTEM_GENERATED = "system_generated"


class VerificationState(str, enum.Enum):
    UNVERIFIED = "unverified"
    PATIENT_REPORTED = "patient_reported"
    EXTRACTED_PENDING_VERIFICATION = "extracted_pending_verification"
    STAFF_ENTERED = "staff_entered"
    STAFF_VERIFIED = "staff_verified"
    CLINICIAN_ENTERED = "clinician_entered"
    CLINICIAN_CONFIRMED = "clinician_confirmed"
    DISPUTED_CONFLICTING = "disputed_conflicting"
    UNCERTAIN = "uncertain"
    SUPERSEDED = "superseded"


class CaseEvidence(Base):
    """Discrete, traceable multimodal evidence item linked to a Canonical Patient Case."""
    __tablename__ = "case_evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    encounter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    canonical_field: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_type: Mapped[EvidenceSourceType] = mapped_column(
        Enum(EvidenceSourceType), default=EvidenceSourceType.PATIENT_REPORTED, nullable=False, index=True
    )
    source_reference: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    verification_state: Mapped[VerificationState] = mapped_column(
        Enum(VerificationState), default=VerificationState.UNVERIFIED, nullable=False, index=True
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    processor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    case = relationship("TriageCase", back_populates="evidence_items")
    encounter = relationship("Encounter")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])

    __table_args__ = (
        Index("ix_case_evidence_case_field", "case_id", "canonical_field"),
        Index("ix_case_evidence_case_active", "case_id", "is_active"),
        Index("ix_case_evidence_verification", "verification_state", "source_type"),
    )
