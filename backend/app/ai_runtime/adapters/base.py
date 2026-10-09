"""CLINOVA AI — Abstract AI & Runtime Adapter Interfaces.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Defines clean architectural decoupling:
Domain Layer -> AIAdapter -> RuntimeAdapter -> Local Model (Qwen)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel
from app.ai_runtime.models import (
    ModelDescriptor,
    RuntimeConfig,
    RuntimeState,
)


class RuntimeAdapter(ABC):
    """Abstract lower-level interface communicating with a specific inference engine (Ollama, llama.cpp, etc.)."""

    def __init__(self, config: RuntimeConfig):
        self.config = config

    @abstractmethod
    async def invoke_raw(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        enforce_json: bool = True,
    ) -> str:
        """Executes raw generation on local runtime and returns raw text completion."""
        pass

    @abstractmethod
    async def check_health(self) -> RuntimeState:
        """Returns runtime availability state (READY, UNAVAILABLE, etc.)."""
        pass

    @abstractmethod
    async def get_model_info(self) -> ModelDescriptor:
        """Returns metadata for the currently loaded model checkpoint."""
        pass


class AIAdapter(ABC):
    """High-level task adapter consumed by CLINOVA application services."""

    def __init__(self, runtime: RuntimeAdapter):
        self.runtime = runtime

    @abstractmethod
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        target_schema: Type[BaseModel],
        **kwargs,
    ) -> BaseModel:
        """Executes structured generation and validates result against schema."""
        pass

    @abstractmethod
    async def extract_entities(self, narrative_text: str, source_evidence_id: str) -> BaseModel:
        """Extracts clinical entities (symptoms, vitals) from narrative."""
        pass

    @abstractmethod
    async def summarize(self, case_narratives: Dict[str, str]) -> BaseModel:
        """Synthesizes clinical timeline while preserving epistemic uncertainty."""
        pass

    @abstractmethod
    async def translate(self, source_text: str, source_lang: str, target_lang: str) -> BaseModel:
        """Translates vernacular text while preserving regional clinical terminology."""
        pass

    @abstractmethod
    async def generate_questions(self, identified_gaps: list[str]) -> BaseModel:
        """Generates targeted Next-Best-Inquiry questions."""
        pass
