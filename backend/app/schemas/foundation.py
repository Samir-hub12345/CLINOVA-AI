"""CLINOVA AI — Core Pydantic v2 Request & Response Schemas.

Continuous Care Intelligence System.
Phase 13: Core Backend Foundation, Master Case Persistence & API Layer.
Strict separation of Create, Read, Action, and Error models.
Never exposes internal database implementation details.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Patient Schemas
# ---------------------------------------------------------------------------

class PatientCreate(BaseModel):
    synthetic_id: Optional[str] = Field(None, description="Pre-generated synthetic ID or auto-generated if omitted")
    age_bracket: str = Field(..., description="Age bracket e.g. 40-49 or pediatric 0-5")
    biological_sex: str = Field(..., description="MALE, FEMALE, or OTHER")
    is_synthetic: bool = Field(True, description="Strict synthetic data flag")


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    synthetic_id: str
    age_bracket: str
    biological_sex: str
    is_synthetic: bool
    created_at: datetime
    updated_at: datetime


class PatientIdentifierCreate(BaseModel):
    identifier_type: str = Field("SYNTHETIC_ID", description="SYNTHETIC_ID, HOSPITAL_MRN, TEMP_SESSION")
    identifier_value: str
    is_primary: bool = True


class PatientIdentifierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    identifier_type: str
    identifier_value: str
    is_primary: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Encounter Schemas
# ---------------------------------------------------------------------------

class EncounterCreate(BaseModel):
    patient_id: str
    facility_id: str
    environment: str = "development"
    pathway: str = "REGULAR_STANDARD"
    source_actor_id: Optional[str] = None
    source_actor_role: Optional[str] = None
    started_at: Optional[datetime] = None


class EncounterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    facility_id: str
    environment: str
    pathway: str
    source_actor_id: Optional[str]
    source_actor_role: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Canonical Case Schemas
# ---------------------------------------------------------------------------

class CaseCreate(BaseModel):
    patient_id: str
    facility_id: str
    encounter_id: Optional[str] = None
    pathway: str = "REGULAR_STANDARD"
    acuity_tier: str = "ROUTINE"
    presenting_complaint: str = ""
    source_language: str = "en"
    primary_syndrome: Optional[str] = None
    required_bundle: Optional[str] = None
    environment_id: str = "development"


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    patient_id: str
    encounter_id: Optional[str]
    facility_id: str
    pathway: str
    current_state: str
    status: str
    acuity_tier: str
    risk_score: float
    trajectory_slope: float
    uncertainty_score: float
    state_version: int
    environment_id: str
    presenting_complaint: str
    source_language: Optional[str] = None
    translation_status: Optional[str] = "NOT_TRANSLATED"
    translated_complaint: Optional[str] = None
    target_language: Optional[str]
    primary_syndrome: Optional[str]
    required_bundle: Optional[str]
    is_closed: bool
    closed_at: Optional[datetime]
    closure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


class CaseSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    patient_synthetic_id: str
    facility_name: str
    current_state: str
    acuity_tier: str
    risk_score: float
    uncertainty_score: float
    presenting_complaint: str
    created_at: datetime


# ---------------------------------------------------------------------------
# State Transition Schemas
# ---------------------------------------------------------------------------

class StateTransitionRequest(BaseModel):
    action: str = Field(..., description="Action name e.g. START_TRIAGE, SUBMIT_TRIAGE, START_REVIEW, FINALIZE_DISPOSITION, ESCALATE")
    reason: str = Field(..., description="Clinical or operational justification for state mutation")
    expected_state_version: Optional[int] = Field(None, description="Client's expected case state_version for optimistic concurrency")
    transition_metadata: Optional[Dict[str, Any]] = None


class StateTransitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    from_state: str
    to_state: str
    actor_id: str
    actor_role: str
    reason: str
    state_version: int
    correlation_id: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Evidence & Provenance Schemas
# ---------------------------------------------------------------------------

class EvidenceCreate(BaseModel):
    source_class: str = Field(
        ...,
        description="PATIENT_REPORTED, VOICE_TRANSCRIBED, OCR_EXTRACTED, CLINICIAN_VERIFIED, STAFF_ENTERED, AI_INFERRED, SYSTEM_DERIVED, EXTERNAL_RECORD"
    )
    epistemic_state: str = Field(
        "INFERRED",
        description="KNOWN, UNKNOWN, CONFLICTING, UNRELIABLE, VERIFIED, INFERRED"
    )
    parameter_name: str = Field(..., description="Canonical clinical concept e.g. systolic_blood_pressure, fever_duration")
    content_value: Any = Field(..., description="Clinical value or structured observation")
    unit: Optional[str] = None
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    source_timestamp: Optional[datetime] = None
    provenance_metadata: Optional[Dict[str, Any]] = None
    verification_metadata: Optional[Dict[str, Any]] = None
    transformation_metadata: Optional[Dict[str, Any]] = None


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    source_class: str
    epistemic_state: str
    parameter_name: str
    content_value: Any
    unit: Optional[str]
    confidence_score: float
    source_timestamp: Optional[datetime]
    captured_timestamp: datetime
    provenance_metadata: Dict[str, Any]
    verification_metadata: Dict[str, Any]
    transformation_metadata: Dict[str, Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# Vitals Schemas
# ---------------------------------------------------------------------------

class VitalCreate(BaseModel):
    heart_rate: Optional[int] = Field(None, ge=20, le=260, description="Pulse in bpm (20-260)")
    systolic_bp: Optional[int] = Field(None, ge=30, le=300, description="Systolic BP in mmHg (30-300)")
    diastolic_bp: Optional[int] = Field(None, ge=20, le=200, description="Diastolic BP in mmHg (20-200)")
    spo2_percent: Optional[int] = Field(None, ge=30, le=100, description="SpO2 percentage (30-100)")
    respiratory_rate: Optional[int] = Field(None, ge=4, le=80, description="Breaths per min (4-80)")
    temperature_celsius: Optional[float] = Field(None, ge=28.0, le=44.0, description="Core temp in Celsius (28.0-44.0)")
    avpu_score: Optional[str] = Field("ALERT", description="ALERT, VOICE, PAIN, UNRESPONSIVE")
    supplemental_o2: bool = False
    source: str = "STAFF_ENTERED"
    recorded_at: Optional[datetime] = None
    provenance_metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_vital_rules(self):
        if self.systolic_bp is not None and self.diastolic_bp is not None:
            if self.systolic_bp <= self.diastolic_bp:
                raise ValueError("Systolic blood pressure must be strictly greater than diastolic blood pressure.")
        if self.recorded_at is not None:
            rec = self.recorded_at
            if rec.tzinfo is None:
                rec = rec.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if rec > now + timedelta(minutes=5):
                raise ValueError("Vital observation timestamp cannot be in the future.")
        if self.avpu_score is not None:
            norm_avpu = self.avpu_score.strip().upper()
            valid_avpu = {"ALERT", "VOICE", "PAIN", "UNRESPONSIVE", "A", "V", "P", "U"}
            if norm_avpu not in valid_avpu:
                raise ValueError(f"Invalid AVPU score '{self.avpu_score}'. Allowed: {sorted(valid_avpu)}")
            mapping = {"A": "ALERT", "V": "VOICE", "P": "PAIN", "U": "UNRESPONSIVE"}
            self.avpu_score = mapping.get(norm_avpu, norm_avpu)
        if self.source is not None:
            valid_sources = {
                "STAFF_ENTERED",
                "NURSE_ENTERED",
                "CLINICIAN_ENTERED",
                "PATIENT_REPORTED",
                "DEVICE_DERIVED",
                "SYSTEM_DERIVED",
            }
            if self.source.strip().upper() not in valid_sources:
                raise ValueError(f"Invalid vital source '{self.source}'. Allowed: {sorted(valid_sources)}")
        return self


class VitalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    heart_rate: Optional[int]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    spo2_percent: Optional[int]
    respiratory_rate: Optional[int]
    temperature_celsius: Optional[float]
    avpu_score: Optional[str]
    supplemental_o2: bool
    source: str
    recorded_at: datetime
    provenance_metadata: Dict[str, Any]
    verification_context: Dict[str, Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# Timeline Schemas
# ---------------------------------------------------------------------------

class TimelineEventCreate(BaseModel):
    event_type: str = Field(..., description="SYMPTOM_ONSET, MEDICATION_TAKEN, VITALS_RECORDED, CLINICIAN_REVIEWED, etc.")
    event_title: str
    event_content: str
    event_timestamp: Optional[datetime] = None
    source_timestamp: Optional[datetime] = None
    evidence_id: Optional[str] = None
    is_conflict: bool = False
    provenance_metadata: Optional[Dict[str, Any]] = None


class TimelineEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    event_type: str
    event_title: str
    event_content: str
    event_timestamp: datetime
    source_timestamp: Optional[datetime]
    actor_id: Optional[str]
    actor_role: Optional[str]
    evidence_id: Optional[str]
    is_conflict: bool
    provenance_metadata: Dict[str, Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# Consent Schemas
# ---------------------------------------------------------------------------

class ConsentCreate(BaseModel):
    purpose: str = "CLINICAL_CARE_TRIAGE"
    language: str = "en"
    channel: str = "DIGITAL_APP"
    consent_version: str = "v1.0"
    status: str = "GRANTED"  # GRANTED, REVOKED, IMPLIED_EMERGENCY
    hash_reference: Optional[str] = None


class ConsentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    purpose: str
    language: str
    channel: str
    consent_version: str
    status: str
    consent_granted: bool
    hash_reference: Optional[str]
    recorded_at: datetime
    created_at: datetime


# ---------------------------------------------------------------------------
# Follow-Up Schemas
# ---------------------------------------------------------------------------

class FollowUpQuestionCreate(BaseModel):
    question_text: str
    reason: str
    priority: str = "IMPORTANT"  # CRITICAL, IMPORTANT, OPTIONAL


class FollowUpQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    question_text: str
    reason: str
    priority: str
    status: str
    created_at: datetime


class FollowUpAnswerCreate(BaseModel):
    question_id: str
    answer_text: str
    evidence_id: Optional[str] = None


class FollowUpAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    case_id: str
    answer_text: str
    answered_by: str
    answered_at: datetime
    evidence_id: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Triage Note Schemas
# ---------------------------------------------------------------------------

class TriageNoteCreate(BaseModel):
    summary: str
    acuity_assessment: str
    clinical_concerns: List[str] = []
    suggested_next_steps: List[str] = []
    author_type: str = "STAFF_ENTERED"  # STAFF_ENTERED, CLINICIAN_REVIEWED, AI_ADVISORY
    is_ai_generated: bool = False

    @model_validator(mode="after")
    def validate_ai_clinician_distinction(self):
        if self.is_ai_generated and self.author_type == "CLINICIAN_REVIEWED":
            raise ValueError("AI advisory content cannot be marked as clinician-reviewed without explicit human sign-off.")
        return self


class TriageNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    author_id: str
    author_role: str
    author_type: str
    summary: str
    acuity_assessment: str
    clinical_concerns: List[Any]
    suggested_next_steps: List[Any]
    is_ai_generated: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Human Review Action Schemas
# ---------------------------------------------------------------------------

class ReviewActionCreate(BaseModel):
    action: str = Field(..., description="VERIFY, MODIFY, REJECT, RESOLVE_CONFLICT, REQUEST_INFORMATION, CONTINUE, OBSERVE, ESCALATE, REFER")
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    original_value: Optional[Any] = None
    updated_value: Optional[Any] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class ReviewActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    clinician_id: str
    action: str
    target_entity_type: Optional[str]
    target_entity_id: Optional[str]
    original_value: Optional[Any]
    updated_value: Optional[Any]
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Audit Event Schemas
# ---------------------------------------------------------------------------

class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: Optional[str]
    actor_id: str
    actor_role: str
    action: str
    object_type: str
    object_id: str
    result: str
    correlation_id: Optional[str]
    details: Dict[str, Any]
    created_at: datetime


# ---------------------------------------------------------------------------
# Facility Schemas
# ---------------------------------------------------------------------------

class FacilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    facility_code: str
    name: str
    tier: str
    operational_status: str
    latitude: float
    longitude: float
    icu_beds_total: int
    icu_beds_available: int
    general_beds_total: int
    general_beds_available: int
    ed_waiting_cases: int
    ed_avg_wait_min: int
    created_at: datetime
