"""Multimodal processing job and telemetry records for Clinova AI."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXHAUSTED = "quota_exhausted"
    UNAVAILABLE = "unavailable"
    REQUIRES_REVIEW = "requires_review"


class MultimodalProcessingRecord(Base):
    """Tracks asynchronous and synchronous multimodal processing jobs, provider telemetry, and provenance linkage."""
    __tablename__ = "multimodal_processing_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    capability: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # "speech_to_text", "ocr", "translation", "tts", "text_generation"
    )
    modality: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # "voice", "document", "image", "text"
    )
    provider_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="completed", nullable=False, index=True
    )

    source_reference: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    output_evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True, index=True
    )

    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

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
    case = relationship("TriageCase")
    output_evidence = relationship("CaseEvidence")

    __table_args__ = (
        Index("ix_processing_records_case_capability", "case_id", "capability"),
        Index("ix_processing_records_status_created", "status", "created_at"),
    )
