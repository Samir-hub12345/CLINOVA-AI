"""CLINOVA AI — Structured AI Output Schemas and Contracts."""

from app.ai_runtime.schemas.contracts import (
    BaseAIResponse,
    ExtractionPayload,
    ExtractionResult,
    SummaryPayload,
    SummaryResult,
    QuestionPayload,
    QuestionResult,
    TranslationPayload,
    TranslationResult,
    NormalizationPayload,
    NormalizationResult,
    DraftNotePayload,
    DraftNoteResult,
    AdvisoryPayload,
    AdvisoryResult,
)

__all__ = [
    "BaseAIResponse",
    "ExtractionPayload",
    "ExtractionResult",
    "SummaryPayload",
    "SummaryResult",
    "QuestionPayload",
    "QuestionResult",
    "TranslationPayload",
    "TranslationResult",
    "NormalizationPayload",
    "NormalizationResult",
    "DraftNotePayload",
    "DraftNoteResult",
    "AdvisoryPayload",
    "AdvisoryResult",
]
