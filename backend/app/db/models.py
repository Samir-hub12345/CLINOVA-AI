"""CLINOVA AI — Relational Database Models.

Continuous Care Intelligence System.
Phase 13: Core Backend Foundation, Master Case Persistence & API Layer.
Grounded in DOC-07 (Master Case Data Model), DOC-08 (Evidence Provenance),
DOC-03 (Role & Permission Model), and DOC-06 (Master Patient Workflow).

Canonical Root Invariant:
There is exactly ONE Master Case root: `cases`.
All downstream clinical entities (Patient, Encounter, Evidence, Vitals, Timeline,
Consent, Follow-up, Triage Note, Review Action, Audit Events) link back to `cases`.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    BigInteger,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(32))  # PATIENT, NURSE, CLINICIAN, REFERRAL_COORDINATOR, FACILITY_ADMIN, AUDITOR, SYSTEM_ADMIN
    facility_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("facilities.id"), nullable=True)
    patient_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("patients.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    facility = relationship("Facility", back_populates="staff")
    decisions = relationship("ClinicianDecision", back_populates="clinician")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    facility_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    tier: Mapped[str] = mapped_column(String(32))  # LEVEL_1_PHC, LEVEL_2_CHC, LEVEL_3_SDH, LEVEL_4_DH, LEVEL_5_TERTIARY
    operational_status: Mapped[str] = mapped_column(String(32), default="OPERATIONAL")  # OPERATIONAL, DEGRADED, OFFLINE
    latitude: Mapped[float] = mapped_column(Float, default=20.5)
    longitude: Mapped[float] = mapped_column(Float, default=85.8)
    icu_beds_total: Mapped[int] = mapped_column(Integer, default=0)
    icu_beds_available: Mapped[int] = mapped_column(Integer, default=0)
    general_beds_total: Mapped[int] = mapped_column(Integer, default=10)
    general_beds_available: Mapped[int] = mapped_column(Integer, default=5)
    ed_waiting_cases: Mapped[int] = mapped_column(Integer, default=0)
    ed_avg_wait_min: Mapped[int] = mapped_column(Integer, default=15)
    capabilities_profile: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    capabilities = relationship("FacilityCapability", back_populates="facility", cascade="all, delete-orphan")
    staff = relationship("User", back_populates="facility")
    cases = relationship("Case", back_populates="facility")
    encounters = relationship("Encounter", back_populates="facility")


class FacilityCapability(Base):
    __tablename__ = "facility_capabilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"), index=True)
    capability_code: Mapped[str] = mapped_column(String(64), index=True)  # e.g., CT_SCAN_24_7, TROPONIN_LAB, BLOOD_BANK
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)
    maintenance_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    facility = relationship("Facility", back_populates="capabilities")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    synthetic_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # e.g., SYN-PT-1042 or PT-SYN-1042
    age_bracket: Mapped[str] = mapped_column(String(16))  # e.g., "40-49"
    biological_sex: Mapped[str] = mapped_column(String(8))  # MALE, FEMALE, OTHER
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    identifiers = relationship("PatientIdentifier", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="patient")


class PatientIdentifier(Base):
    __tablename__ = "patient_identifiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True)
    identifier_type: Mapped[str] = mapped_column(String(32))  # SYNTHETIC_ID, HOSPITAL_MRN, TEMP_SESSION
    identifier_value: Mapped[str] = mapped_column(String(64), index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    patient = relationship("Patient", back_populates="identifiers")


class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True)
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"), index=True)
    environment: Mapped[str] = mapped_column(String(32), default="development")
    pathway: Mapped[str] = mapped_column(String(64), default="REGULAR_STANDARD")
    source_actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    patient = relationship("Patient", back_populates="encounters")
    facility = relationship("Facility", back_populates="encounters")
    cases = relationship("Case", back_populates="encounter")


class Case(Base):
    """
    CANONICAL MASTER CASE ROOT.
    The single root aggregate for the entire clinical encounter.
    All downstream clinical objects reference this entity.
    """
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # e.g., CAS-2026-001
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True)
    encounter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("encounters.id"), index=True, nullable=True)
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"), index=True)
    pathway: Mapped[str] = mapped_column(String(64), default="REGULAR_STANDARD")
    current_state: Mapped[str] = mapped_column(String(64), default="INTAKE_RECORDED", index=True)
    status: Mapped[str] = mapped_column(String(32), default="NEW", index=True)
    acuity_tier: Mapped[str] = mapped_column(String(16), default="ROUTINE")  # ROUTINE, MODERATE, URGENT, CRITICAL
    risk_score: Mapped[float] = mapped_column(Float, default=0.1)  # 0.0 - 1.0
    trajectory_slope: Mapped[float] = mapped_column(Float, default=0.0)  # points / hour
    uncertainty_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 - 1.0
    state_version: Mapped[int] = mapped_column(Integer, default=1)  # Optimistic concurrency version
    environment_id: Mapped[str] = mapped_column(String(32), default="development")
    presenting_complaint: Mapped[str] = mapped_column(Text, default="")
    source_language: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    translation_status: Mapped[Optional[str]] = mapped_column(String(32), default="NOT_TRANSLATED", nullable=True)
    translated_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_language: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    primary_syndrome: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    required_bundle: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    patient = relationship("Patient", back_populates="cases")
    encounter = relationship("Encounter", back_populates="cases")
    facility = relationship("Facility", back_populates="cases")

    # Authoritative Phase 13 Collections
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    vitals_list = relationship("Vital", back_populates="case", cascade="all, delete-orphan", order_by="Vital.recorded_at")
    timeline = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan", order_by="TimelineEvent.event_timestamp")
    state_transitions = relationship("CaseStateTransition", back_populates="case", cascade="all, delete-orphan", order_by="CaseStateTransition.created_at")
    follow_ups = relationship("FollowUpQuestion", back_populates="case", cascade="all, delete-orphan")
    triage_notes = relationship("TriageNote", back_populates="case", cascade="all, delete-orphan")
    review_actions_list = relationship("ReviewAction", back_populates="case", cascade="all, delete-orphan")
    audit_records = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")
    triage_snapshots = relationship("TriageSnapshotRecord", back_populates="case", cascade="all, delete-orphan", order_by="TriageSnapshotRecord.calculated_at")

    # Upstream Compatibility Relationships
    vitals = relationship("VitalReading", back_populates="case", cascade="all, delete-orphan", order_by="VitalReading.recorded_at")
    evidence_records = relationship("EvidenceRecord", back_populates="case", cascade="all, delete-orphan")
    decisions = relationship("ClinicianDecision", back_populates="case", cascade="all, delete-orphan")
    consent = relationship("Consent", back_populates="case", uselist=False, cascade="all, delete-orphan")
    referral = relationship("Referral", back_populates="case", uselist=False, cascade="all, delete-orphan")
    outcome = relationship("CaseOutcome", back_populates="case", uselist=False, cascade="all, delete-orphan")
    ai_results = relationship("AIResultRecord", back_populates="case", cascade="all, delete-orphan")
    sync_journals = relationship("SyncJournal", back_populates="case", cascade="all, delete-orphan")


class CaseStateTransition(Base):
    __tablename__ = "case_state_transitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    from_state: Mapped[str] = mapped_column(String(64))
    to_state: Mapped[str] = mapped_column(String(64))
    actor_id: Mapped[str] = mapped_column(String(64))
    actor_role: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(String(255))
    state_version: Mapped[int] = mapped_column(Integer)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    transition_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="state_transitions")


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    purpose: Mapped[str] = mapped_column(String(64), default="CLINICAL_CARE_TRIAGE")
    language: Mapped[str] = mapped_column(String(16), default="en")
    channel: Mapped[str] = mapped_column(String(32), default="DIGITAL_APP")
    consent_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    status: Mapped[str] = mapped_column(String(32), default="GRANTED")  # GRANTED, REVOKED, IMPLIED_EMERGENCY
    consent_granted: Mapped[bool] = mapped_column(Boolean, default=True)
    hash_reference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="consent")


class Evidence(Base):
    """
    Authoritative discrete clinical evidence record.
    Preserves raw evidence, epistemic state, confidence, and provenance metadata.
    """
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    source_class: Mapped[str] = mapped_column(String(32), index=True)
    # PATIENT_REPORTED, VOICE_TRANSCRIBED, OCR_EXTRACTED, CLINICIAN_VERIFIED,
    # STAFF_ENTERED, AI_INFERRED, SYSTEM_DERIVED, EXTERNAL_RECORD
    epistemic_state: Mapped[str] = mapped_column(String(32), default="INFERRED", index=True)
    # KNOWN, UNKNOWN, CONFLICTING, UNRELIABLE, VERIFIED, INFERRED
    parameter_name: Mapped[str] = mapped_column(String(128), index=True)
    content_value: Mapped[Any] = mapped_column(JSON, default=dict)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    source_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    captured_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    provenance_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    verification_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    transformation_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="evidence_items")


class Vital(Base):
    """
    Authoritative vital sign reading with clinical validation bounds and provenance.
    """
    __tablename__ = "vitals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    spo2_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    respiratory_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avpu_score: Mapped[Optional[str]] = mapped_column(String(16), default="ALERT")
    supplemental_o2: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(32), default="STAFF_ENTERED")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    provenance_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    verification_context: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="vitals_list")


class TimelineEvent(Base):
    """
    Longitudinal timeline milestone for a case.
    Explicitly tracks chronology and highlights conflicting timestamps.
    """
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    event_title: Mapped[str] = mapped_column(String(128))
    event_content: Mapped[str] = mapped_column(Text)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    source_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    evidence_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("evidence.id"), nullable=True)
    is_conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="timeline")
    evidence = relationship("Evidence")


class FollowUpQuestion(Base):
    __tablename__ = "follow_up_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    question_text: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(16), default="IMPORTANT")  # CRITICAL, IMPORTANT, OPTIONAL
    status: Mapped[str] = mapped_column(String(32), default="PENDING")  # PENDING, ANSWERED, SKIPPED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="follow_ups")
    answers = relationship("FollowUpAnswer", back_populates="question", cascade="all, delete-orphan")


class FollowUpAnswer(Base):
    __tablename__ = "follow_up_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("follow_up_questions.id"), index=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    answer_text: Mapped[str] = mapped_column(Text)
    answered_by: Mapped[str] = mapped_column(String(64))
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evidence_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("evidence.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    question = relationship("FollowUpQuestion", back_populates="answers")
    case = relationship("Case")

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(128))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    storage_path: Mapped[str] = mapped_column(String(512))
    content_fingerprint: Mapped[str] = mapped_column(String(128), index=True)
    processing_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    error_status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ocr_model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_quality_metadata: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    language_metadata: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case")

class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_value: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    bounding_box: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    document = relationship("Document")


class TriageNote(Base):
    __tablename__ = "triage_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    author_id: Mapped[str] = mapped_column(String(64))
    author_role: Mapped[str] = mapped_column(String(32))
    author_type: Mapped[str] = mapped_column(String(32))  # STAFF_ENTERED, CLINICIAN_REVIEWED, AI_ADVISORY
    summary: Mapped[str] = mapped_column(Text)
    acuity_assessment: Mapped[str] = mapped_column(String(32))
    clinical_concerns: Mapped[List[Any]] = mapped_column(JSON, default=list)
    suggested_next_steps: Mapped[List[Any]] = mapped_column(JSON, default=list)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="triage_notes")


class ReviewAction(Base):
    """
    Authoritative record of qualified human clinical review actions.
    Allowed vocabulary: VERIFY, MODIFY, REJECT, RESOLVE_CONFLICT, REQUEST_INFORMATION, CONTINUE, OBSERVE, ESCALATE, REFER.
    """
    __tablename__ = "review_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    clinician_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(32))
    target_entity_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    target_entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    original_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    updated_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="review_actions_list")


class AuditEvent(Base):
    """
    Authoritative medicolegal audit event ledger.
    Records WHO, WHAT, WHEN, CASE, OBJECT, RESULT, CORRELATION ID.
    Never logs raw patient clinical narrative text.
    """
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id"), index=True, nullable=True)
    actor_id: Mapped[str] = mapped_column(String(64))
    actor_role: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(64), index=True)
    object_type: Mapped[str] = mapped_column(String(64))
    object_id: Mapped[str] = mapped_column(String(64))
    result: Mapped[str] = mapped_column(String(32), default="SUCCESS")  # SUCCESS, FAILURE, BLOCKED
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    case = relationship("Case", back_populates="audit_records")


class TriageSnapshotRecord(Base):
    """
    Authoritative historical record of deterministic triage calculations.
    Preserves input vitals snapshot, NEWS2, Shock Index, triggered red flags,
    priority tier, and ruleset version without overwriting prior calculations.
    """
    __tablename__ = "triage_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    vital_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("vitals.id"), nullable=True)
    priority_tier: Mapped[str] = mapped_column(String(32), default="P4_ROUTINE")
    acuity_tier: Mapped[str] = mapped_column(String(16), default="ROUTINE")
    risk_score: Mapped[float] = mapped_column(Float, default=0.1)
    uncertainty_score: Mapped[float] = mapped_column(Float, default=0.5)
    news2_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shock_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_critical_red_flags: Mapped[bool] = mapped_column(Boolean, default=False)
    snapshot_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ruleset_version: Mapped[str] = mapped_column(String(64), default="TRIAGE-RULES-v1.0")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="triage_snapshots")
    vital = relationship("Vital")


class AIResultRecord(Base):
    """
    Authoritative record of AI task executions and advisory results.
    Attached to canonical Master Case `cases.id`.
    Preserves task metadata, prompt/model versions, validation status,
    epistemic state, source evidence pointers, and context fingerprint.
    Never overwrites historical results.
    """
    __tablename__ = "ai_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    task_id: Mapped[str] = mapped_column(String(64), index=True)
    task_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    model_id: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(32))
    prompt_id: Mapped[str] = mapped_column(String(64))
    prompt_version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS")  # SUCCESS, REJECTED, FALLBACK, SUCCESS_CACHED
    validation_state: Mapped[str] = mapped_column(String(32), default="VALID")
    epistemic_state: Mapped[str] = mapped_column(String(32), default="AI_INFERRED")  # Mandatory AI_INFERRED
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    context_fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    case_version: Mapped[int] = mapped_column(Integer, default=1)
    source_evidence_references: Mapped[List[Any]] = mapped_column(JSON, default=list)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    errors: Mapped[List[str]] = mapped_column(JSON, default=list)
    warnings: Mapped[List[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="ai_results")



# ---------------------------------------------------------------------------
# Legacy Upstream Models Preserved for Complete Compatibility
# ---------------------------------------------------------------------------

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    provenance_type: Mapped[str] = mapped_column(String(32))
    source_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extracted_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(16), default="UNVERIFIED")
    verified_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="evidence_records")


class VitalReading(Base):
    __tablename__ = "vital_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    spo2_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    respiratory_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avpu_score: Mapped[Optional[str]] = mapped_column(String(16), default="ALERT")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="vitals")


class ClinicianDecision(Base):
    __tablename__ = "clinician_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    clinician_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(64))
    decision_type: Mapped[str] = mapped_column(String(64), default="ACCEPT")
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_impression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="decisions")
    clinician = relationship("User", back_populates="decisions", foreign_keys=[clinician_id])


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    origin_facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"))
    destination_facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"))
    required_bundle: Mapped[str] = mapped_column(String(64))
    sbar_situation: Mapped[str] = mapped_column(Text, default="")
    sbar_background: Mapped[str] = mapped_column(Text, default="")
    sbar_assessment: Mapped[str] = mapped_column(Text, default="")
    sbar_recommendation: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="REQUESTED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="referral")


class CaseOutcome(Base):
    __tablename__ = "case_outcomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    disposition: Mapped[str] = mapped_column(String(64))
    final_condition: Mapped[str] = mapped_column(String(64), default="STABLE")
    actual_action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default="UNKNOWN")
    recommendation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    professional_decision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    outcome_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default="UNKNOWN")
    recorded_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_corrected: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="outcome")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class SignalEvent(Base):
    __tablename__ = "signal_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"), index=True)
    syndrome_tag: Mapped[str] = mapped_column(String(64), index=True)
    acuity_tier: Mapped[str] = mapped_column(String(16))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

class TranslationRecord(Base):
    __tablename__ = "translation_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))  # e.g., 'Evidence', 'Case'
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    source_language: Mapped[str] = mapped_column(String(16))
    target_language: Mapped[str] = mapped_column(String(16))
    source_text: Mapped[Text] = mapped_column(Text)
    translated_text: Mapped[Text] = mapped_column(Text)
    translation_status: Mapped[str] = mapped_column(String(32)) # COMPLETE, LOW_CONFIDENCE, REQUIRES_REVIEW, FAILED
    provider: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(64))
    source_fingerprint: Mapped[str] = mapped_column(String(64))
    task_version: Mapped[str] = mapped_column(String(32))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    review_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    corrected_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    case = relationship("Case")


class SyncJournal(Base):
    """
    Offline Synchronization Journal (RES-99).
    Tracks local transactions captured offline, their synchronization state,
    and resolution strategies when propagating to central cloud hub.
    """
    __tablename__ = "sync_journals"

    sync_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    node_id: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    operation: Mapped[str] = mapped_column(String(16))  # INSERT, UPDATE, TOMBSTONE
    local_version: Mapped[int] = mapped_column(Integer, default=1)
    remote_version: Mapped[int] = mapped_column(Integer, default=0)
    sync_status: Mapped[str] = mapped_column(String(32), default="PENDING_UPLOAD", index=True)  # PENDING_UPLOAD, SYNCED, CONFLICT, FAILED
    payload_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    conflict_strategy: Mapped[str] = mapped_column(String(32), default="APPEND_ONLY")  # APPEND_ONLY, CLINICIAN_WINS, LAST_WRITE_WINS, MANUAL_GATE
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    case = relationship("Case", back_populates="sync_journals")
    conflicts = relationship("SyncConflict", back_populates="journal", cascade="all, delete-orphan")


class SyncConflict(Base):
    """
    Offline Sync Conflicts Registry (RES-99).
    Freezes conflicting payloads when automated conflict strategies require
    human clinician or administrative reconciliation gate (Inv SYNC-4).
    """
    __tablename__ = "sync_conflicts"

    conflict_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sync_id: Mapped[str] = mapped_column(String(36), ForeignKey("sync_journals.sync_id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    local_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    remote_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    resolution_status: Mapped[str] = mapped_column(String(32), default="PENDING_HUMAN_REVIEW", index=True)  # PENDING_HUMAN_REVIEW, RESOLVED_LOCAL, RESOLVED_REMOTE, RESOLVED_MERGED
    resolved_by_actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    journal = relationship("SyncJournal", back_populates="conflicts")
