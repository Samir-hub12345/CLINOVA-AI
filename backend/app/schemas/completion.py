"""Pydantic schemas for Phase 5 Intelligent Completion & Adaptive Questioning."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class StartCompletionSessionRequest(BaseModel):
    max_turns: Optional[int] = Field(default=5, ge=1, le=10, description="Maximum interview turns allowed (safety ceiling)")
    force_new: bool = Field(default=False, description="Whether to archive any existing session and start anew")


class SubmitAnswerRequest(BaseModel):
    raw_answer_text: str = Field(..., min_length=1, description="Verbatim patient response or selection")
    modality: Optional[str] = Field(default="patient_text", description="Input modality: patient_text, patient_choice, patient_voice")
    is_skipped: bool = Field(default=False, description="Patient elected to skip/decline this question")
    structured_payload: Optional[Dict[str, Any]] = Field(default=None, description="Structured parsed value if applicable")


class SkipQuestionRequest(BaseModel):
    reason: Optional[str] = Field(default="patient_skipped", description="Reason for skipping the question")


class CompleteSessionRequest(BaseModel):
    reason: Optional[str] = Field(default="patient_concluded", description="Reason for manual completion")


class CompletionOption(BaseModel):
    label: str
    value: str
    description: Optional[str] = None


class CompletionQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    case_id: str
    turn_number: int
    target_gap_id: Optional[str] = None
    target_gap_type: str
    target_field: str
    question_text: str
    question_type: str
    options: Optional[List[Dict[str, Any]]] = None
    placeholder: Optional[str] = None
    priority_score: float
    clinical_rationale: str
    status: str
    is_safety_flag: bool
    created_at: datetime
    presented_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None


class CompletionAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    session_id: str
    case_id: str
    patient_id: Optional[str] = None
    raw_answer_text: str
    normalized_value: Optional[str] = None
    structured_payload: Optional[Dict[str, Any]] = None
    answer_modality: str
    is_skipped: bool
    is_valid: bool
    validation_notes: Optional[str] = None
    evidence_id: Optional[str] = None
    answered_at: datetime


class InformationGapResponse(BaseModel):
    gap_id: str
    gap_type: str
    target_field: str
    category: str
    severity: str
    description: str
    source_finding_id: Optional[str] = None
    source_conflict_id: Optional[str] = None
    is_addressable: bool = True
    resolved: bool = False


class CompletionSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    status: str
    case_version_started: int
    case_version_current: int
    current_turn: int
    max_turns: int
    questions_asked_count: int
    questions_answered_count: int
    questions_skipped_count: int
    initial_gap_count: int
    remaining_gap_count: int
    initial_readiness_score: float
    current_readiness_score: float
    stopping_reason: Optional[str] = None
    stopping_criterion: Optional[str] = None
    completion_summary: Optional[Dict[str, Any]] = None
    engine_version: str
    is_current: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    current_question: Optional[CompletionQuestionResponse] = None
    questions: Optional[List[CompletionQuestionResponse]] = None


class NextQuestionResponse(BaseModel):
    session_id: str
    case_id: str
    turn_number: int
    max_turns: int
    is_complete: bool
    stopping_reason: Optional[str] = None
    stopping_criterion: Optional[str] = None
    question: Optional[CompletionQuestionResponse] = None
    remaining_gaps_count: int = 0
    current_readiness_score: float = 0.0


class SubmitAnswerResponse(BaseModel):
    session_id: str
    case_id: str
    answer: CompletionAnswerResponse
    new_evidence_id: Optional[str] = None
    new_case_version: int
    rebuilt_snapshot_id: Optional[str] = None
    verification_run_id: Optional[str] = None
    new_readiness_score: float
    readiness_improved: bool
    next_question: Optional[CompletionQuestionResponse] = None
    is_session_complete: bool = False
    stopping_reason: Optional[str] = None
    stopping_criterion: Optional[str] = None
