"""CLINOVA AI — Patient Intake & Consent Schemas.

Continuous Care Intelligence System.
Phase 15: Patient Intake + Consent + Persistence.
Grounded in DOC-02, DOC-03, DOC-07, and Section 20 Master Specification.

Strict Pydantic v2 validation contracts for patient intake, consent capture,
clinical pathways, and structured responses.
Zero PII requirements; synthetic identifiers and public demographic brackets only.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Canonical Clinical Pathways
# ---------------------------------------------------------------------------

VALID_PATHWAYS = {
    "REGULAR_STANDARD",
    "REGULAR",
    "OPD_GENERAL",
    "EMERGENCY",
    "EMERGENCY_FAST_TRACK",
    "MATERNAL_CHILD",
    "CHRONIC_CARE",
}

VALID_BIOLOGICAL_SEX = {"MALE", "FEMALE", "OTHER", "UNKNOWN"}

VALID_CONSENT_STATUSES = {"GRANTED", "REVOKED", "IMPLIED_EMERGENCY"}

VALID_ENVIRONMENTS = {"development", "staging", "production", "test"}

VALID_LANGUAGES = {"en", "hi", "or"}


def normalize_pathway(pathway: str) -> str:
    """Maps pathway string to canonical representation."""
    p = pathway.strip().upper() if pathway else "REGULAR_STANDARD"
    if p in {"EMERGENCY", "EMERGENCY_FAST_TRACK"}:
        return "EMERGENCY"
    if p in {"REGULAR", "REGULAR_STANDARD", "OPD_GENERAL"}:
        return "REGULAR_STANDARD" if p != "OPD_GENERAL" else "OPD_GENERAL"
    return p


# ---------------------------------------------------------------------------
# Patient Intake Request Schema
# ---------------------------------------------------------------------------

class PatientIntakeRequest(BaseModel):
    """
    Authoritative request schema for patient intake submissions.
    Supports both patient self-intake and staff-assisted intake.
    Strictly forbids unsupported fields (Requirement 16).
    """
    model_config = ConfigDict(extra="forbid")

    facility_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Target healthcare facility identifier (e.g. FAC-DH-04)",
    )
    pathway: str = Field(
        "REGULAR_STANDARD",
        description="Clinical pathway: REGULAR_STANDARD, OPD_GENERAL, EMERGENCY, MATERNAL_CHILD, CHRONIC_CARE",
    )
    reported_age_bracket: Optional[str] = Field(
        "25-35 YRS",
        max_length=32,
        description="Age bracket (e.g. 25-35 YRS, 40-49, 0-1 YR)",
    )
    biological_sex: Optional[str] = Field(
        "FEMALE",
        description="Biological sex: MALE, FEMALE, OTHER, or UNKNOWN",
    )
    preferred_language: Optional[str] = Field(
        "en",
        max_length=16,
        description="Preferred communication language (en, hi, or)",
    )
    environment: Optional[str] = Field(
        None,
        max_length=32,
        description="Deployment environment (development, staging, production, test)",
    )
    chief_complaint: str = Field(
        ...,
        description="Compulsory presenting symptom or chief complaint narrative",
    )
    symptoms: Optional[List[str]] = Field(
        None,
        description="Optional discrete symptom tags",
    )
    symptom_duration: Optional[str] = Field(
        None,
        max_length=64,
        description="Duration/onset of symptoms (e.g. 2 days, 45 minutes)",
    )
    narrative_notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional supplementary clinical narrative notes",
    )
    voice_transcript: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional transcribed speech audio text",
    )
    document_uploaded: Optional[bool] = Field(
        False,
        description="Indicates whether external report evidence was referenced",
    )
    document_type: Optional[str] = Field(
        None,
        max_length=64,
        description="Document type if referenced (e.g. LAB_REPORT, PRESCRIPTION)",
    )
    vitals: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional initial physiological vitals (e.g. heart_rate, spo2_percent)",
    )
    consent_confirmed: bool = Field(
        False,
        description="Informed consent confirmed by patient or authorized intake actor",
    )
    consent_granted: Optional[bool] = Field(
        None,
        description="Interoperability alias for consent_confirmed",
    )
    consent_status: Optional[str] = Field(
        None,
        description="Explicit consent status: GRANTED, REVOKED, IMPLIED_EMERGENCY",
    )
    consent_purpose: str = Field(
        "CLINICAL_CARE_TRIAGE",
        max_length=64,
        description="Medicolegal purpose for data processing",
    )
    consent_version: str = Field(
        "v1.0",
        max_length=16,
        description="Version identifier of consent notice",
    )
    consent_channel: str = Field(
        "DIGITAL_APP",
        max_length=32,
        description="Channel through which consent was acquired",
    )
    intake_channel: str = Field(
        "DIGITAL_APP",
        max_length=32,
        description="Intake submission channel: DIGITAL_APP, STAFF_KIOSK, AMBULANCE_HANDOFF",
    )
    synthetic_patient_id: Optional[str] = Field(
        None,
        max_length=64,
        description="Optional pre-existing synthetic patient UUID or token",
    )
    is_synthetic: bool = Field(
        True,
        description="Guaranteed synthetic indicator",
    )
    client_submission_id: Optional[str] = Field(
        None,
        max_length=64,
        description="Client-side idempotency correlation key to prevent accidental duplicate submission",
    )

    @field_validator("facility_id")
    @classmethod
    def validate_facility_id(cls, v: str) -> str:
        cleaned = v.strip() if v else ""
        if not cleaned:
            raise ValueError("Facility identifier cannot be empty or whitespace-only.")
        return cleaned

    @field_validator("chief_complaint")
    @classmethod
    def validate_chief_complaint(cls, v: str) -> str:
        cleaned = v.strip() if v else ""
        if not cleaned:
            raise ValueError("Presenting symptom / chief complaint cannot be empty or whitespace-only.")
        if len(cleaned) > 5000:
            raise ValueError("Presenting symptom narrative exceeds maximum allowable length of 5000 characters.")
        return cleaned

    @field_validator("pathway")
    @classmethod
    def validate_pathway_field(cls, v: str) -> str:
        p = v.strip().upper() if v else ""
        if p not in VALID_PATHWAYS:
            raise ValueError(
                f"Invalid pathway '{v}'. Allowed pathways: {sorted(list(VALID_PATHWAYS))}"
            )
        return p

    @field_validator("biological_sex")
    @classmethod
    def validate_biological_sex_field(cls, v: Optional[str]) -> str:
        if v is None:
            return "FEMALE"
        b = v.strip().upper()
        if not b:
            return "UNKNOWN"
        if b not in VALID_BIOLOGICAL_SEX:
            raise ValueError(
                f"Invalid biological sex '{v}'. Must be MALE, FEMALE, OTHER, or UNKNOWN."
            )
        return b

    @field_validator("reported_age_bracket")
    @classmethod
    def validate_reported_age_bracket(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return "25-35 YRS"
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Age bracket cannot be empty or whitespace-only.")
        return cleaned

    @field_validator("preferred_language")
    @classmethod
    def validate_preferred_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return "en"
        lang = v.strip().lower()
        if not lang:
            return "en"
        if lang not in VALID_LANGUAGES:
            raise ValueError(
                f"Invalid preferred language '{v}'. Allowed languages: {sorted(list(VALID_LANGUAGES))}"
            )
        return lang

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        env = v.strip().lower()
        if not env:
            return None
        if env not in VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment '{v}'. Allowed environments: {sorted(list(VALID_ENVIRONMENTS))}"
            )
        return env


# Upstream alias for frontend compatibility
FrontendIntakeSubmissionRequest = PatientIntakeRequest


# ---------------------------------------------------------------------------
# Patient Intake Response Schema
# ---------------------------------------------------------------------------

class PatientIntakeResponse(BaseModel):
    """Authoritative response contract for intake creation."""
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    case_id: str = Field(..., description="Canonical Master Case UUID")
    case_number: str = Field(..., description="Human-readable case identifier e.g. CAS-2026-10492")
    patient_id: str = Field(..., description="Internal Patient UUID")
    patient_synthetic_id: str = Field(..., description="Synthetic patient reference e.g. PT-SYN-1042")
    synthetic_reference: str = Field(..., description="Frontend-facing patient token")
    encounter_id: str = Field(..., description="Internal Encounter UUID")
    facility_id: str = Field(..., description="Associated healthcare facility identifier")
    pathway: str = Field(..., description="Persisted clinical pathway")
    status: str = Field(..., description="Lifecycle status e.g. NEW")
    current_state: str = Field(..., description="Initial FSM state: INTAKE_RECORDED")
    state_version: int = Field(1, description="Optimistic concurrency state version")
    consent_status: str = Field(..., description="GRANTED or IMPLIED_EMERGENCY")
    consent_id: str = Field(..., description="Persisted Consent record UUID")
    queue_position: int = Field(..., description="Calculated queue depth at intake facility")
    message: str = Field(..., description="Clinical system status acknowledgment")
    is_mock: bool = Field(False, description="Whether this response was served from a mock fixture")
    is_duplicate: bool = Field(False, description="True if idempotency prevented duplicate creation")
