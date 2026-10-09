"""CLINOVA AI — Application AI Task Catalog & Specifications.

Phase 18: AI Application Integration.
Defines explicit, versioned clinical advisory AI tasks adhering to:
- DOC-03 (Role & Permission Boundaries)
- DOC-07 (Master Case Data Model)
- DOC-08 (Evidence Provenance)
- Deterministic Safety Boundary (AI is Advisory Only; Never Decides Care)
"""

from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from app.ai_runtime.schemas.contracts import (
    SummaryPayload,
    CaseSummaryPayload,
    TimelineSummaryPayload,
    MissingInformationPayload,
    QuestionPayload,
    DraftNotePayload,
)
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_DOCTOR,
    ROLE_NURSE,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
)

# Canonical Task Identifiers
TASK_CASE_SUMMARY = "CASE_SUMMARY_V1"
TASK_TIMELINE_SUMMARY = "TIMELINE_SUMMARY_V1"
TASK_MISSING_INFORMATION = "MISSING_INFORMATION_V1"
TASK_FOLLOWUP_QUESTIONS = "FOLLOWUP_QUESTION_V1"
TASK_TRIAGE_NOTE_DRAFT = "TRIAGE_NOTE_DRAFT_V1"


class AITaskDefinition(BaseModel):
    """Specification of an explicit, versioned application AI task."""
    task_id: str
    task_version: str = "1.0.0"
    prompt_id: str
    prompt_version: str = "1.0.0"
    description: str
    target_schema: Any
    allowed_roles: List[str]
    is_advisory_only: bool = True
    timeout_seconds: float = 5.0
    requires_evidence: bool = True


TASK_CATALOG: Dict[str, AITaskDefinition] = {
    TASK_CASE_SUMMARY: AITaskDefinition(
        task_id=TASK_CASE_SUMMARY,
        task_version="1.0.0",
        prompt_id="CASE_SUMMARY_V1",
        prompt_version="1.0.0",
        description="Synthesizes evidence-grounded case summary distinguishing KNOWN, UNKNOWN, CONFLICTING, UNRELIABLE, VERIFIED, INFERRED.",
        target_schema=CaseSummaryPayload,
        allowed_roles=[ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE],
        is_advisory_only=True,
        timeout_seconds=5.0,
    ),
    TASK_TIMELINE_SUMMARY: AITaskDefinition(
        task_id=TASK_TIMELINE_SUMMARY,
        task_version="1.0.0",
        prompt_id="TIMELINE_SUMMARY_V1",
        prompt_version="1.0.0",
        description="Chronological synthesis of Master Case events, temporal progression, and conflict highlights.",
        target_schema=TimelineSummaryPayload,
        allowed_roles=[ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE],
        is_advisory_only=True,
        timeout_seconds=5.0,
    ),
    TASK_MISSING_INFORMATION: AITaskDefinition(
        task_id=TASK_MISSING_INFORMATION,
        task_version="1.0.0",
        prompt_id="MISSING_INFORMATION_V1",
        prompt_version="1.0.0",
        description="Analyzes clinical information completeness and flags missing parameters with clinical rationale.",
        target_schema=MissingInformationPayload,
        allowed_roles=[ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE],
        is_advisory_only=True,
        timeout_seconds=5.0,
    ),
    TASK_FOLLOWUP_QUESTIONS: AITaskDefinition(
        task_id=TASK_FOLLOWUP_QUESTIONS,
        task_version="1.0.0",
        prompt_id="FOLLOWUP_QUESTION_V1",
        prompt_version="1.0.0",
        description="Generates bounded, targeted clarification questions based on identified clinical information gaps.",
        target_schema=QuestionPayload,
        allowed_roles=[ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE],
        is_advisory_only=True,
        timeout_seconds=5.0,
    ),
    TASK_TRIAGE_NOTE_DRAFT: AITaskDefinition(
        task_id=TASK_TRIAGE_NOTE_DRAFT,
        task_version="1.0.0",
        prompt_id="TRIAGE_NOTE_DRAFT_V1",
        prompt_version="1.0.0",
        description="Drafts structured triage documentation for clinician review with mandatory non-final disclaimer.",
        target_schema=DraftNotePayload,
        allowed_roles=[ROLE_CLINICIAN, ROLE_DOCTOR, ROLE_NURSE],
        is_advisory_only=True,
        timeout_seconds=5.0,
    ),
}


def get_task_definition(task_id: str) -> Optional[AITaskDefinition]:
    """Retrieves task definition by task ID with alias fallback."""
    if task_id in TASK_CATALOG:
        return TASK_CATALOG[task_id]
    alias_map = {
        "summary": TASK_CASE_SUMMARY,
        "timeline": TASK_TIMELINE_SUMMARY,
        "timeline-summary": TASK_TIMELINE_SUMMARY,
        "missing-information": TASK_MISSING_INFORMATION,
        "follow-up-questions": TASK_FOLLOWUP_QUESTIONS,
        "followup": TASK_FOLLOWUP_QUESTIONS,
        "triage-note": TASK_TRIAGE_NOTE_DRAFT,
        "triage_draft": TASK_TRIAGE_NOTE_DRAFT,
    }
    canonical_id = alias_map.get(task_id.lower().replace("_", "-"))
    return TASK_CATALOG.get(canonical_id) if canonical_id else None
