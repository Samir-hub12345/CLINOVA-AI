"""SQLAlchemy ORM models package."""

from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.consultation import Consultation, ConsultationStatus, TriageLevel
from app.models.audit import AuditLog
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.multimodal_job import MultimodalProcessingRecord, ProcessingStatus
from app.models.revoked_token import RevokedToken

from app.models.canonical_case import (
    BuildRunStatus,
    FactPolarity,
    FactCertainty,
    TemporalStatus,
    CaseBuildRun,
    CaseSnapshot,
    CanonicalFact,
    TimelineEvent,
)

from app.models.verification import (
    VerificationRunStatus,
    ReviewReadinessLevel,
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
    ConflictType,
    CompletenessFieldStatus,
    VerificationRun,
    VerificationFinding,
    VerificationConflict,
)

from app.models.completion import (
    CompletionSessionStatus,
    QuestionType,
    QuestionStatus,
    AnswerModality,
    GapType,
    StoppingCriterion,
    CompletionSession,
    CompletionQuestion,
    CompletionAnswer,
)

__all__ = [
    "User",
    "UserRole",
    "Patient",
    "Consultation",
    "ConsultationStatus",
    "TriageLevel",
    "AuditLog",
    "TriageCase",
    "CaseEvidence",
    "EvidenceSourceType",
    "VerificationState",
    "MultimodalProcessingRecord",
    "ProcessingStatus",
    "RevokedToken",
    "BuildRunStatus",
    "FactPolarity",
    "FactCertainty",
    "TemporalStatus",
    "CaseBuildRun",
    "CaseSnapshot",
    "CanonicalFact",
    "TimelineEvent",
    "VerificationRunStatus",
    "ReviewReadinessLevel",
    "FindingSeverity",
    "FindingType",
    "FindingCategory",
    "FindingStatus",
    "ConflictType",
    "CompletenessFieldStatus",
    "VerificationRun",
    "VerificationFinding",
    "VerificationConflict",
    "CompletionSessionStatus",
    "QuestionType",
    "QuestionStatus",
    "AnswerModality",
    "GapType",
    "StoppingCriterion",
    "CompletionSession",
    "CompletionQuestion",
    "CompletionAnswer",
]

