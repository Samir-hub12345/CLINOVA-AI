"""CLINOVA AI — Relational Database Models.

Continuous Care Intelligence System.
Grounded in DOC-14 Data Model Specification.
Provides full persistence across Patients, Encounters, Evidence, CareGraph,
FacilityGraph, Referrals, Decisions, Outcomes, Audit Logs, and Signal Events.
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
    full_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(32))  # CLINICIAN, NURSE, ADMIN, REVIEWER
    facility_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("facilities.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    facility = relationship("Facility", back_populates="staff")
    decisions = relationship("ClinicianDecision", back_populates="clinician")


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    facility_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    tier: Mapped[str] = mapped_column(String(32))  # LEVEL_1_PHC, LEVEL_2_CHC, LEVEL_3_SDH, LEVEL_4_DH, LEVEL_5_TERTIARY
    latitude: Mapped[float] = mapped_column(Float, default=20.5)
    longitude: Mapped[float] = mapped_column(Float, default=85.8)
    icu_beds_total: Mapped[int] = mapped_column(Integer, default=0)
    icu_beds_available: Mapped[int] = mapped_column(Integer, default=0)
    general_beds_total: Mapped[int] = mapped_column(Integer, default=10)
    general_beds_available: Mapped[int] = mapped_column(Integer, default=5)
    ed_waiting_cases: Mapped[int] = mapped_column(Integer, default=0)
    ed_avg_wait_min: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    capabilities = relationship("FacilityCapability", back_populates="facility", cascade="all, delete-orphan")
    staff = relationship("User", back_populates="facility")
    cases = relationship("Case", back_populates="facility")


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
    synthetic_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # e.g., SYN-PT-1042
    age_bracket: Mapped[str] = mapped_column(String(16))  # e.g., "40-49"
    biological_sex: Mapped[str] = mapped_column(String(8))  # MALE, FEMALE, OTHER
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    cases = relationship("Case", back_populates="patient")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # e.g., CAS-2026-001
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True)
    facility_id: Mapped[str] = mapped_column(String(36), ForeignKey("facilities.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="NEW", index=True)
    acuity_tier: Mapped[str] = mapped_column(String(16), default="ROUTINE")  # ROUTINE, MODERATE, URGENT, CRITICAL
    risk_score: Mapped[float] = mapped_column(Float, default=0.1)  # 0.0 - 1.0
    trajectory_slope: Mapped[float] = mapped_column(Float, default=0.0)  # points / hour
    uncertainty_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 - 1.0
    presenting_complaint: Mapped[str] = mapped_column(Text, default="")
    primary_syndrome: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    required_bundle: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    patient = relationship("Patient", back_populates="cases")
    facility = relationship("Facility", back_populates="cases")
    vitals = relationship("VitalReading", back_populates="case", cascade="all, delete-orphan", order_by="VitalReading.recorded_at")
    evidence_records = relationship("EvidenceRecord", back_populates="case", cascade="all, delete-orphan")
    decisions = relationship("ClinicianDecision", back_populates="case", cascade="all, delete-orphan")
    consent = relationship("Consent", back_populates="case", uselist=False, cascade="all, delete-orphan")
    referral = relationship("Referral", back_populates="case", uselist=False, cascade="all, delete-orphan")
    outcome = relationship("CaseOutcome", back_populates="case", uselist=False, cascade="all, delete-orphan")


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    consent_granted: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(16), default="en")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="consent")


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    provenance_type: Mapped[str] = mapped_column(String(32))  # PATIENT_REPORTED, VOICE_TRANSCRIBED, OCR_EXTRACTED, CLINICIAN_VERIFIED, AI_INFERRED, SYSTEM_DERIVED
    source_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extracted_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(16), default="UNVERIFIED")  # UNVERIFIED, CONFIRMED, MODIFIED, DISPUTED
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
    avpu_score: Mapped[Optional[str]] = mapped_column(String(16), default="ALERT")  # ALERT, VOICE, PAIN, UNRESPONSIVE
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="vitals")


class ClinicianDecision(Base):
    __tablename__ = "clinician_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), index=True)
    clinician_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    action_type: Mapped[str] = mapped_column(String(32))  # ASK, VERIFY, CONTINUE, OBSERVE, ESCALATE, REFER
    decision_type: Mapped[str] = mapped_column(String(16), default="ACCEPT")  # ACCEPT, OVERRIDE
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="decisions")
    clinician = relationship("User", back_populates="decisions")


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
    status: Mapped[str] = mapped_column(String(32), default="REQUESTED")  # REQUESTED, ACCEPTED, DISPATCHED, COMPLETED, REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="referral")


class CaseOutcome(Base):
    __tablename__ = "case_outcomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    disposition: Mapped[str] = mapped_column(String(64))  # DISCHARGED_ROUTINE, TRANSFERRED_OUT, ADMITTED_INPATIENT, OBSERVATION_RESOLVED
    final_condition: Mapped[str] = mapped_column(String(64), default="STABLE")  # STABLE, IMPROVED, CRITICAL, REFERRED
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
