import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TriageCase(Base):
    """Triage case intake record representing a patient presentation at a facility or camp."""
    __tablename__ = "triage_cases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    owner_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=True
    )
    synthetic_case_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    facility_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    encounter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    facility_type: Mapped[str] = mapped_column(
        String(100), default="Government Hospital", nullable=False
    )
    visit_type: Mapped[str] = mapped_column(
        String(100), default="Outpatient", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="awaiting_review", nullable=False, index=True
    )
    case_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    workflow_state: Mapped[str] = mapped_column(
        String(50), default="CREATED", nullable=False, index=True
    )
    review_readiness_status: Mapped[str] = mapped_column(
        String(50), default="not_ready", nullable=False, index=True
    )
    queue_category: Mapped[str] = mapped_column(
        String(50), default="routine", nullable=False
    )
    queue_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    consent_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Patient Context
    patient_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    approximate_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    context_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vitals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON: bp, hr, spo2, temp, rr
    intake_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Assignment & Department Routing
    assigned_doctor_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    assigned_doctor_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    assigned_department: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    # Multimodal Intake Inputs
    raw_symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    speech_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Optional Report & Visual Attachments
    report_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    report_ocr_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    image_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Structured Triage Note & Decision Support (JSON strings)
    triage_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    missing_information: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    follow_up_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    risk_signals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    timeline_events: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    # Human-in-the-Loop Review Actions
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewer_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    referral_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    # Data Retention & Lifecycle
    retention_expiry: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    facility = relationship("Facility")
    encounter = relationship("Encounter")
    patient = relationship("Patient")
    evidence_items = relationship(
        "CaseEvidence", back_populates="case", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_triage_cases_status_created", "status", "created_at"),
        Index("ix_triage_cases_facility_created", "facility_id", "created_at"),
    )
