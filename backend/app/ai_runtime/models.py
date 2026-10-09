"""CLINOVA AI — Local AI Runtime Models and Type Definitions.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Defines core lifecycle states, validation enums, runtime configurations,
and model descriptors for isolated AI runtime validation.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AIProviderMode(str, Enum):
    """Local runtime provider options."""
    MOCK_DETERMINISTIC = "mock_deterministic"
    LOCAL_OLLAMA = "local_ollama"
    LOCAL_LLAMACPP = "local_llamacpp"
    LOCAL_TRANSFORMERS = "local_transformers"
    DISABLED = "disabled"


class InferenceTaskType(str, Enum):
    """Permitted inference tasks for local language models."""
    EXTRACTION = "EXTRACTION"
    SUMMARY = "SUMMARY"
    QUESTION_GENERATION = "QUESTION_GENERATION"
    TRANSLATION = "TRANSLATION"
    NORMALIZATION = "NORMALIZATION"
    DRAFT_NOTE = "DRAFT_NOTE"
    ADVISORY = "ADVISORY"


class AIResultLifecycle(str, Enum):
    """Lifecycle states for AI-generated artifacts.
    
    In accordance with Phase 7 Provenance & NMC Regulations 2023,
    an AI result never transitions to clinical truth without human RMP sign-off.
    """
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    REVIEW_PENDING = "REVIEW_PENDING"
    ACCEPTED = "ACCEPTED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"


class ValidationStatus(str, Enum):
    """Deterministic output validation states."""
    VALID = "VALID"
    REJECTED_SCHEMA = "REJECTED_SCHEMA"
    REJECTED_FORBIDDEN_ACTION = "REJECTED_FORBIDDEN_ACTION"
    REJECTED_UNGROUNDED = "REJECTED_UNGROUNDED"
    REJECTED_OUT_OF_BOUNDS = "REJECTED_OUT_OF_BOUNDS"
    REJECTED_TIMEOUT = "REJECTED_TIMEOUT"
    REJECTED_OOM = "REJECTED_OOM"
    REJECTED_INJECTION = "REJECTED_INJECTION"
    REJECTED_MALFORMED = "REJECTED_MALFORMED"
    REJECTED_UNAVAILABLE = "REJECTED_UNAVAILABLE"


class RuntimeState(str, Enum):
    """Inference runtime operational states."""
    MODEL_DISCOVERY = "MODEL_DISCOVERY"
    MODEL_LOAD = "MODEL_LOAD"
    MODEL_WARM = "MODEL_WARM"
    MODEL_READY = "MODEL_READY"
    REQUEST = "REQUEST"
    INFERENCE = "INFERENCE"
    VALIDATION = "VALIDATION"
    RELEASE = "RELEASE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_LOAD_FAILURE = "MODEL_LOAD_FAILURE"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    TIMEOUT = "TIMEOUT"
    PROCESS_CRASH = "PROCESS_CRASH"


class EconomicTier(str, Enum):
    """Cost tier classification in accordance with Zero-Cost Architecture."""
    FREE_LOCAL = "FREE_LOCAL"
    FREE_HOSTED = "FREE_HOSTED"
    FREE_TIER_LIMITED = "FREE_TIER_LIMITED"
    OPTIONAL_FUTURE_PAID = "OPTIONAL_FUTURE_PAID"


class EvidenceReference(BaseModel):
    """Provenance pointer tying an AI inference to an existing evidence record."""
    evidence_id: str = Field(..., description="Unique UUID of the source evidence record")
    text_snippet: Optional[str] = Field(None, description="Exact substring from evidence justifying inference")
    source_type: Optional[str] = Field(None, description="NARRATIVE, VITALS, LAB, OCR, ASR")


class ModelDescriptor(BaseModel):
    """Specification of an approved local model checkpoint."""
    model_id: str = Field(..., description="Model identifier (e.g. qwen3-4b-instruct)")
    version: str = Field(..., description="Release or checkpoint version tag")
    quantization: str = Field(..., description="Quantization scheme (e.g. Q4_K_M, INT8, FP16)")
    family: str = Field(default="Qwen", description="Architecture family")
    parameter_count_billions: float = Field(..., description="Active parameter count in billions")
    license: str = Field(default="Apache-2.0", description="Open-source license")
    context_window_tokens: int = Field(default=8192, description="Maximum context window")
    memory_budget_mb: int = Field(..., description="RAM/VRAM budget ceiling in megabytes")
    economic_tier: EconomicTier = Field(default=EconomicTier.FREE_LOCAL)
    is_clinically_validated: bool = Field(
        default=False,
        description="Must remain FALSE. CLINOVA does not claim clinical validation."
    )


class RuntimeConfig(BaseModel):
    """Configuration for local AI execution."""
    provider_mode: AIProviderMode = Field(default=AIProviderMode.MOCK_DETERMINISTIC)
    endpoint_url: str = Field(default="http://127.0.0.1:11434")
    model_descriptor: ModelDescriptor = Field(
        default_factory=lambda: ModelDescriptor(
            model_id="qwen3-4b-instruct",
            version="1.0.0",
            quantization="Q4_K_M",
            parameter_count_billions=4.0,
            license="Apache-2.0",
            context_window_tokens=8192,
            memory_budget_mb=3200,
        )
    )
    timeout_seconds: float = Field(default=5.0, description="Inference timeout ceiling")
    temperature: float = Field(default=0.0, description="Strict 0.0 for deterministic extraction")
    max_tokens: int = Field(default=1024, description="Maximum completion tokens")
    max_concurrency: int = Field(default=1, description="Serial execution on resource-constrained edge")


class ClinicianOverrideRecord(BaseModel):
    """Audit ledger entry for clinician modifications or rejections of AI output."""
    original_ai_payload: Dict[str, Any] = Field(..., description="Raw output generated by AI")
    clinician_replacement_value: Optional[Dict[str, Any]] = Field(None, description="Clinician's replacement")
    action: AIResultLifecycle = Field(..., description="ACCEPTED, MODIFIED, or REJECTED")
    override_reason: str = Field(..., description="Clinical justification for override")
    clinician_id: str = Field(..., description="UUID / NMR Registration of the RMP")
    recorded_at: str = Field(..., description="ISO-8601 UTC timestamp")
