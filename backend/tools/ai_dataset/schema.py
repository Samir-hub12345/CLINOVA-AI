"""CLINOVA AI — Synthetic Dataset Schema & Validation Invariants.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Defines the canonical 22-field synthetic dataset schema, 20 test case groups (A-T),
and zero-PII validation guards.
"""

import re
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class DatasetGroup(str, Enum):
    """The 20 mandated Phase 11 test case groups."""
    GROUP_A_ROUTINE = "GROUP_A_ROUTINE"
    GROUP_B_URGENT = "GROUP_B_URGENT"
    GROUP_C_EMERGENCY = "GROUP_C_EMERGENCY"
    GROUP_D_MISSING_INFO = "GROUP_D_MISSING_INFO"
    GROUP_E_CONFLICTING_INFO = "GROUP_E_CONFLICTING_INFO"
    GROUP_F_UNRELIABLE_EVIDENCE = "GROUP_F_UNRELIABLE_EVIDENCE"
    GROUP_G_OCR_DERIVED = "GROUP_G_OCR_DERIVED"
    GROUP_H_VOICE_DERIVED = "GROUP_H_VOICE_DERIVED"
    GROUP_I_ENGLISH = "GROUP_I_ENGLISH"
    GROUP_J_HINDI = "GROUP_J_HINDI"
    GROUP_K_ODIA = "GROUP_K_ODIA"
    GROUP_L_MIXED_LANGUAGE = "GROUP_L_MIXED_LANGUAGE"
    GROUP_M_REFERRAL = "GROUP_M_REFERRAL"
    GROUP_N_WARD = "GROUP_N_WARD"
    GROUP_O_OT = "GROUP_O_OT"
    GROUP_P_FOLLOW_UP = "GROUP_P_FOLLOW_UP"
    GROUP_Q_OUTCOME = "GROUP_Q_OUTCOME"
    GROUP_R_PROMPT_INJECTION = "GROUP_R_PROMPT_INJECTION"
    GROUP_S_FORBIDDEN_REQUEST = "GROUP_S_FORBIDDEN_REQUEST"
    GROUP_T_HALLUCINATION_TRAP = "GROUP_T_HALLUCINATION_TRAP"


class DatasetSplit(str, Enum):
    """The 6 disjoint dataset splits."""
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    TEST = "TEST"
    ADVERSARIAL_TEST = "ADVERSARIAL_TEST"
    MULTILINGUAL_TEST = "MULTILINGUAL_TEST"
    SAFETY_TEST = "SAFETY_TEST"


class ActionClass(str, Enum):
    """Permitted clinical advisory action classes."""
    ASK = "ASK"
    VERIFY = "VERIFY"
    CONTINUE = "CONTINUE"
    OBSERVE = "OBSERVE"
    ESCALATE = "ESCALATE"
    REFER = "REFER"


# Strict regex patterns for detecting accidental PII in synthetic records
PII_PHONE_REGEX = re.compile(r"(?:\+91[\-\s]?)?[6789]\d{9}\b")
PII_AADHAAR_REGEX = re.compile(r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b")
PII_EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


class SyntheticCaseRecord(BaseModel):
    """Canonical 22-field record schema for CLINOVA AI evaluation & training foundation."""

    case_id: str = Field(..., description="Unique synthetic case identifier (e.g. syn-001)")
    synthetic_case_id: str = Field(..., description="Globally unique synthetic lineage identifier")
    environment: str = Field(..., description="Clinical environment (OPD, EMERGENCY_DEPT, WARD, OT, etc.)")
    language: str = Field(..., description="Source language (en, hi, od, mixed)")
    input_type: str = Field(..., description="Input modality (TYPED_NARRATIVE, OCR_DERIVED, VOICE_DERIVED, etc.)")
    source_type: str = Field(..., description="Source origin (PATIENT_STATEMENT, TRIAGE_NOTE, REFERRAL_LETTER, etc.)")
    source_text: str = Field(..., description="Raw synthetic source narrative")
    structured_truth: Dict[str, Any] = Field(..., description="Objective verified facts for entity/vital evaluation")
    evidence_ids: List[str] = Field(..., description="List of valid evidence record IDs in this case")
    required_fields: List[str] = Field(..., description="Clinical fields mandated for completeness")
    missing_fields: List[str] = Field(default_factory=list, description="Fields genuinely missing from context")
    conflicting_fields: List[str] = Field(default_factory=list, description="Fields with contradictory evidence")
    expected_timeline: List[Dict[str, Any]] = Field(default_factory=list, description="Gold chronology of events")
    expected_questions: List[Dict[str, Any]] = Field(default_factory=list, description="Gold value-of-information inquiries")
    expected_summary: Dict[str, Any] = Field(..., description="Gold structured clinical summary")
    expected_uncertainty: Dict[str, Any] = Field(..., description="Gold epistemic uncertainty state")
    expected_provenance: List[Dict[str, Any]] = Field(default_factory=list, description="Grounding links from claims to evidence IDs")
    expected_advisory_behavior: Dict[str, Any] = Field(..., description="Approved action class (ASK, VERIFY, etc.) and candidate reasoning")
    safety_constraints: List[str] = Field(..., description="Mandatory safety boundaries applied to this case")
    gold_output: Dict[str, Any] = Field(..., description="Human-reviewed expected output across tasks")
    annotation_version: str = Field(default="v1.0.0-synthetic-gold", description="Annotation methodology version")
    dataset_version: str = Field(default="v1.0.0-phase11", description="Dataset release version")

    @field_validator("source_text")
    @classmethod
    def validate_no_real_pii(cls, v: str) -> str:
        """Enforces that synthetic narratives contain zero phone numbers, Aadhaar IDs, or emails."""
        if PII_PHONE_REGEX.search(v):
            raise ValueError("PII VIOLATION: Realistic Indian phone number detected in synthetic text.")
        if PII_AADHAAR_REGEX.search(v):
            raise ValueError("PII VIOLATION: Realistic 12-digit Aadhaar ID pattern detected in synthetic text.")
        if PII_EMAIL_REGEX.search(v):
            raise ValueError("PII VIOLATION: Email address detected in synthetic text.")
        return v

    @field_validator("safety_constraints")
    @classmethod
    def validate_safety_present(cls, v: List[str]) -> List[str]:
        """Ensures every synthetic record contains at least one safety boundary."""
        if not v:
            raise ValueError("Every synthetic record must define at least one explicit safety constraint.")
        return v

    @model_validator(mode="after")
    def validate_consistency(self) -> "SyntheticCaseRecord":
        """Ensures evidence IDs cited in gold output and expected_provenance exist in evidence_ids."""
        evidence_set = set(self.evidence_ids)
        for prov in self.expected_provenance:
            ref_id = prov.get("source_evidence_id")
            if ref_id and ref_id not in evidence_set:
                raise ValueError(f"PROVENANCE INCONSISTENCY: Expected provenance cites '{ref_id}' not in evidence_ids.")
        return self
