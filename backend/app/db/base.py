from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy ORM models in CLINOVA AI."""
    pass


# Import all models here so that Base.metadata has a complete catalog
# for Alembic migrations and SQLAlchemy runtime introspection.
from app.models.user import User, UserRole  # noqa: E402, F401
from app.models.facility import Facility  # noqa: E402, F401
from app.models.patient import Patient  # noqa: E402, F401
from app.models.consultation import Consultation, ConsultationStatus, TriageLevel  # noqa: E402, F401
from app.models.case import TriageCase  # noqa: E402, F401
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState  # noqa: E402, F401
from app.models.multimodal_job import MultimodalProcessingRecord, ProcessingStatus  # noqa: E402, F401
from app.models.revoked_token import RevokedToken  # noqa: E402, F401
from app.models.document import Document, DocumentType, DocumentStatus, DocumentArtifact, ScanStatus, ArtifactType  # noqa: E402, F401
from app.models.job import BackgroundJob, JobStatus, JobType  # noqa: E402, F401
from app.models.audit import AuditLog  # noqa: E402, F401

# Phase 2 Clinical Architecture Models
from app.models.identifier import PatientIdentifier, IdentifierType  # noqa: E402, F401
from app.models.encounter import Encounter, EncounterType, EncounterStatus  # noqa: E402, F401
from app.models.observation import (  # noqa: E402, F401
    ClinicalObservation,
    ObservationType,
    ObservationSource,
    VerificationStatus,
)
from app.models.allergy import Allergy, AllergySeverity, AllergyStatus  # noqa: E402, F401
from app.models.medication import Medication, MedicationType, MedicationStatus  # noqa: E402, F401
from app.models.condition import (  # noqa: E402, F401
    MedicalCondition,
    ConditionClinicalStatus,
    ConditionVerificationStatus,
)
from app.models.diagnosis import Diagnosis, DiagnosisType, DiagnosisStatus  # noqa: E402, F401
from app.models.note import ClinicalNote, NoteType, NoteStatus  # noqa: E402, F401
from app.models.ai_run import AIRun, AIRunStatus, AIReviewStatus  # noqa: E402, F401
from app.models.referral import Referral, ReferralPriority, ReferralStatus  # noqa: E402, F401

# Phase 3 Canonical Case Intelligence Build Models
from app.models.canonical_case import (  # noqa: E402, F401
    BuildRunStatus,
    FactPolarity,
    FactCertainty,
    TemporalStatus,
    CaseBuildRun,
    CaseSnapshot,
    CanonicalFact,
    TimelineEvent,
)

# Phase 4 Clinical Verification Models
from app.models.verification import (  # noqa: E402, F401
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

# Phase 5 Intelligent Completion Models
from app.models.completion import (  # noqa: E402, F401
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

