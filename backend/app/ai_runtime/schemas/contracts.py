"""CLINOVA AI — Task Request & Structured Output Contracts.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Defines strongly-typed Pydantic contracts for all 7 permitted machine-consumed tasks:
1. EXTRACTION_RESULT
2. SUMMARY_RESULT
3. QUESTION_RESULT
4. TRANSLATION_RESULT
5. NORMALIZATION_RESULT
6. DRAFT_NOTE_RESULT
7. ADVISORY_RESULT
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.ai_runtime.models import (
    ValidationStatus,
    EvidenceReference,
)


class BaseAIResponse(BaseModel):
    """Canonical base contract for all machine-consumed AI outputs."""
    status: str = Field(..., description="SUCCESS, REJECTED, or FALLBACK")
    model: str = Field(..., description="Model identifier that produced inference")
    model_version: str = Field(..., description="Model checkpoint or release version")
    runtime: str = Field(default="local_runtime", description="Backend runtime identifier")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp of inference"
    )
    source_references: List[EvidenceReference] = Field(
        default_factory=list,
        description="Explicit evidence record IDs grounding this output"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Calibrated model predictive confidence (separate from clinical risk)"
    )
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings or ambiguities")
    validation_state: ValidationStatus = Field(
        default=ValidationStatus.VALID,
        description="Validation outcome from deterministic safety validator"
    )
    epistemic_state: str = Field(
        default="AI_INFERRED",
        description="Mandatory epistemic state. Never VERIFIED or CLINICIAN_APPROVED."
    )


# ---------------------------------------------------------------------------
# 1. EXTRACTION
# ---------------------------------------------------------------------------
class ExtractedSymptom(BaseModel):
    name: str = Field(..., description="Symptom name")
    duration: Optional[str] = Field(None, description="Reported duration e.g. '2 days'")
    severity: Optional[str] = Field(None, description="Reported severity: MILD, MODERATE, SEVERE, UNKNOWN")
    body_site: Optional[str] = Field(None, description="Anatomical location if stated")
    source_evidence_id: str = Field(..., description="Evidence ID containing symptom mention")


class ExtractedVitalMention(BaseModel):
    parameter: str = Field(..., description="HR, SBP, DBP, RR, SPO2, TEMP")
    value: float = Field(..., description="Numeric value extracted")
    unit: str = Field(..., description="Measurement unit (bpm, mmHg, %, C, F)")
    source_evidence_id: str = Field(..., description="Evidence ID containing vital mention")


class ExtractionPayload(BaseModel):
    symptoms: List[ExtractedSymptom] = Field(default_factory=list)
    vital_mentions: List[ExtractedVitalMention] = Field(default_factory=list)
    reported_allergies: List[str] = Field(default_factory=list)
    reported_medications: List[str] = Field(default_factory=list)
    identified_gaps: List[str] = Field(default_factory=list)


class ExtractionResult(BaseAIResponse):
    payload: ExtractionPayload = Field(...)


# ---------------------------------------------------------------------------
# 2. SUMMARY
# ---------------------------------------------------------------------------
class SummaryPayload(BaseModel):
    chief_complaint: str = Field(..., description="Synthesized chief complaint")
    brief_chronology: str = Field(..., description="Chronological timeline of current illness")
    pertinent_positives: List[str] = Field(default_factory=list)
    pertinent_negatives: List[str] = Field(default_factory=list)
    uncertainty_statement: str = Field(..., description="Explicit description of missing or unclear information")
    epistemic_distinctions: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Categorization of facts into KNOWN, UNKNOWN, CONFLICTING, UNRELIABLE, VERIFIED, INFERRED"
    )
    source_evidence_ids: List[str] = Field(default_factory=list)


class SummaryResult(BaseAIResponse):
    payload: SummaryPayload = Field(...)


class CaseSummaryPayload(SummaryPayload):
    """Phase 18 Case Summary payload with explicit epistemic state distinctions."""
    pass


class CaseSummaryResult(BaseAIResponse):
    payload: CaseSummaryPayload = Field(...)


# ---------------------------------------------------------------------------
# 3. QUESTION GENERATION (Value of Information / Next Best Inquiry)
# ---------------------------------------------------------------------------
class CandidateQuestion(BaseModel):
    question_text: str = Field(..., description="Patient-facing inquiry text")
    language: str = Field(default="en", description="Question language e.g. en, hi, od")
    information_gap: str = Field(..., description="Specific missing clinical domain element addressed")
    rationale: str = Field(..., description="Why this question is valuable for narrowing differential")
    priority: int = Field(default=1, ge=1, le=5, description="1=Highest priority")
    target_evidence_id: Optional[str] = Field(None, description="Evidence ID grounding the inquiry")


class QuestionPayload(BaseModel):
    candidate_questions: List[CandidateQuestion] = Field(default_factory=list)
    total_gaps_identified: int = Field(default=0)


class QuestionResult(BaseAIResponse):
    payload: QuestionPayload = Field(...)


# ---------------------------------------------------------------------------
# 4. TRANSLATION
# ---------------------------------------------------------------------------
class TranslationPayload(BaseModel):
    source_text: str = Field(..., description="Original unaltered source text")
    source_language: str = Field(..., description="Detected source language e.g. hi, od, en")
    target_language: str = Field(..., description="Target language e.g. en")
    translated_text: str = Field(..., description="Translated text")
    preserved_colloquialisms: Dict[str, str] = Field(
        default_factory=dict,
        description="Original regional terms preserved verbatim with tentative clinical meaning"
    )


class TranslationResult(BaseAIResponse):
    payload: TranslationPayload = Field(...)


# ---------------------------------------------------------------------------
# 5. NORMALIZATION
# ---------------------------------------------------------------------------
class NormalizedEntity(BaseModel):
    colloquial_term: str = Field(..., description="Raw text term")
    standard_concept: str = Field(..., description="Clinical standard concept name")
    coding_system: str = Field(default="SNOMED-CT", description="Coding system (SNOMED-CT, LOINC, ICD-11)")
    concept_code: Optional[str] = Field(None, description="Standard code if available")
    mapping_confidence: float = Field(..., ge=0.0, le=1.0)


class NormalizationPayload(BaseModel):
    entities: List[NormalizedEntity] = Field(default_factory=list)


class NormalizationResult(BaseAIResponse):
    payload: NormalizationPayload = Field(...)


# ---------------------------------------------------------------------------
# 6. DRAFT NOTE (Non-Diagnostic Clinician Assistant)
# ---------------------------------------------------------------------------
class DraftNotePayload(BaseModel):
    subjective_draft: str = Field(..., description="Draft subjective history")
    objective_observations_draft: str = Field(..., description="Draft objective observations")
    advisory_considerations_draft: Optional[str] = Field(None, description="Non-binding considerations for clinician")
    vital_summary_draft: Optional[str] = Field(None, description="Summary of recorded vitals")
    deterministic_risk_summary: Optional[str] = Field(None, description="Summary of deterministic risk")
    clinical_concerns: List[str] = Field(default_factory=list, description="Clinical concerns for review")
    suggested_next_steps: List[str] = Field(default_factory=list, description="Suggested next steps")
    uncertainty_and_gaps: Optional[str] = Field(None, description="Missing or uncertain information")
    disclaimer: str = Field(
        default="DRAFT ASSISTANT NOTE ONLY. NOT A FINAL CLINICAL RECORD. REQUIRES RMP REVIEW AND SIGN-OFF.",
        description="Mandatory legal disclaimer"
    )


class DraftNoteResult(BaseAIResponse):
    payload: DraftNotePayload = Field(...)


# ---------------------------------------------------------------------------
# 7. ADVISORY (Candidate Reasoning Signals)
# ---------------------------------------------------------------------------
class CandidateDifferential(BaseModel):
    condition_name: str = Field(..., description="Candidate condition under consideration")
    supporting_evidence_ids: List[str] = Field(..., description="Evidence IDs supporting consideration")
    opposing_evidence_ids: List[str] = Field(default_factory=list)
    epistemic_note: str = Field(..., description="Reason this is an advisory consideration, not diagnosis")


class AdvisoryPayload(BaseModel):
    candidate_signals: List[str] = Field(default_factory=list)
    differential_considerations: List[CandidateDifferential] = Field(default_factory=list)
    suggested_diagnostic_pathways: List[str] = Field(default_factory=list)
    safety_reminders: List[str] = Field(default_factory=list)
    is_autonomous_diagnosis: bool = Field(
        default=False,
        description="Must be FALSE. AI cannot make an autonomous diagnosis."
    )

    @field_validator("is_autonomous_diagnosis")
    @classmethod
    def must_not_be_autonomous(cls, v: bool) -> bool:
        if v is True:
            raise ValueError("AI is strictly prohibited from asserting an autonomous diagnosis.")
        return v


class AdvisoryResult(BaseAIResponse):
    payload: AdvisoryPayload = Field(...)


# ---------------------------------------------------------------------------
# 8. TIMELINE SUMMARY (Phase 18 Task A)
# ---------------------------------------------------------------------------
class TimelineEventItem(BaseModel):
    event_title: str = Field(..., description="Short milestone title")
    relative_time: Optional[str] = Field(None, description="Relative time e.g. '2h ago', 'onset'")
    description: str = Field(..., description="Detailed clinical milestone event description")
    source_evidence_ids: List[str] = Field(default_factory=list, description="Evidence record IDs")
    epistemic_status: Optional[str] = Field("INFERRED", description="Epistemic status of milestone")


class TimelineSummaryPayload(BaseModel):
    timeline_events: List[TimelineEventItem] = Field(default_factory=list)
    chronological_progression: str = Field(..., description="Summary of disease course over time")
    unresolved_items: List[str] = Field(default_factory=list)
    conflict_notes: List[str] = Field(default_factory=list)


class TimelineSummaryResult(BaseAIResponse):
    payload: TimelineSummaryPayload = Field(...)


# ---------------------------------------------------------------------------
# 9. MISSING INFORMATION ANALYSIS (Phase 18 Task B)
# ---------------------------------------------------------------------------
class MissingInfoGap(BaseModel):
    parameter_name: str = Field(..., description="Name of missing clinical parameter")
    clinical_rationale: str = Field(..., description="Why missing parameter matters clinically")
    priority: str = Field(default="IMPORTANT", description="CRITICAL, IMPORTANT, ROUTINE")
    target_domain: Optional[str] = Field(None, description="VITALS, LABS, HISTORY, ALLERGIES")
    recommended_action: Optional[str] = Field(None, description="Recommended clinician action")
    evidence_reference: Optional[str] = Field(None, description="Related evidence ID if applicable")


class MissingInformationPayload(BaseModel):
    identified_gaps: List[MissingInfoGap] = Field(default_factory=list)
    completeness_score: float = Field(default=0.8, ge=0.0, le=1.0)
    high_priority_gap_count: int = Field(default=0)
    epistemic_uncertainty_note: str = Field(..., description="Preservation of clinical uncertainty")


class MissingInformationResult(BaseAIResponse):
    payload: MissingInformationPayload = Field(...)
