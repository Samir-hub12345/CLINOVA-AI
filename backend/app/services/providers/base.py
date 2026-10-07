import enum
import time
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


class ProviderErrorCode(str, enum.Enum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXHAUSTED = "quota_exhausted"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    UNSUPPORTED_FORMAT = "unsupported_format"
    PROCESSING_ERROR = "processing_error"
    SAFETY_BLOCKED = "safety_blocked"
    UNKNOWN_ERROR = "unknown_error"


class ProviderError(Exception):
    """Normalized exception standard for all external and local Clinova AI providers."""

    def __init__(
        self,
        error_code: ProviderErrorCode,
        message: str,
        provider_name: str,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(f"[{provider_name}] {error_code.value}: {message}")
        self.error_code = error_code
        self.message = message
        self.provider_name = provider_name
        self.retryable = retryable
        self.details = details or {}


class ProviderResponseMetadata(BaseModel):
    """Standardized operational telemetry for all provider executions."""

    provider_name: str
    model_name: Optional[str] = None
    latency_ms: int = 0
    fallback_used: bool = False
    processing_status: str = "success"  # "success" | "partial" | "failed"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quota_remaining: Optional[int] = None


class ProviderInterface(ABC):
    """Base contract for all interchangeable AI and processing providers."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if credentials and runtime dependencies are configured."""
        pass


class SpeechToTextProvider(ProviderInterface):
    """Interface for voice-to-text transcription."""

    @abstractmethod
    async def transcribe(
        self, audio_bytes: bytes, language_hint: Optional[str] = None
    ) -> Tuple[str, ProviderResponseMetadata]:
        pass


class OCRProvider(ProviderInterface):
    """Interface for document and image optical character recognition."""

    @abstractmethod
    async def extract_text_and_tables(
        self, document_bytes: bytes, mime_type: str
    ) -> Tuple[Dict[str, Any], ProviderResponseMetadata]:
        pass


class TranslationProvider(ProviderInterface):
    """Interface for cross-lingual clinical translation."""

    @abstractmethod
    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> Tuple[str, ProviderResponseMetadata]:
        pass


class TextGenerationProvider(ProviderInterface):
    """Interface for LLM reasoning, structured drafting, and synthesis."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, ProviderResponseMetadata]:
        pass


class TextToSpeechProvider(ProviderInterface):
    """Interface for audio speech synthesis for patient read-aloud explanations."""

    @abstractmethod
    async def synthesize(
        self, text: str, language: str
    ) -> Tuple[bytes, ProviderResponseMetadata]:
        pass
