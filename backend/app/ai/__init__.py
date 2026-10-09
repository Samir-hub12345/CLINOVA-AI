"""CLINOVA AI — Application-Level AI Orchestration Package.

Phase 18: AI Application Integration.
Bridges canonical Master Case data to local AI runtime while enforcing:
- Advisory-only role
- Deterministic clinical safety precedence
- Evidence grounding and provenance
- Untrusted input sanitization
- Zero autonomous clinical decision authority
"""

from app.ai.tasks import (
    TASK_CATALOG,
    TASK_CASE_SUMMARY,
    TASK_TIMELINE_SUMMARY,
    TASK_MISSING_INFORMATION,
    TASK_FOLLOWUP_QUESTIONS,
    TASK_TRIAGE_NOTE_DRAFT,
    AITaskDefinition,
    get_task_definition,
)
from app.ai.context_builder import AIContextBuilder, AIContextPack
from app.ai.orchestrator import AIApplicationOrchestrator

__all__ = [
    "TASK_CATALOG",
    "TASK_CASE_SUMMARY",
    "TASK_TIMELINE_SUMMARY",
    "TASK_MISSING_INFORMATION",
    "TASK_FOLLOWUP_QUESTIONS",
    "TASK_TRIAGE_NOTE_DRAFT",
    "AITaskDefinition",
    "get_task_definition",
    "AIContextBuilder",
    "AIContextPack",
    "AIApplicationOrchestrator",
]
