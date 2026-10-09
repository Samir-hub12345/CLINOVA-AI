"""CLINOVA AI — Runtime Adapter Factory (Phase 18).

Selects the AI runtime adapter from application configuration:
- MOCK_DETERMINISTIC (default): MockDeterministicAdapter — hermetic tests, CI, $0 operation.
- LOCAL_OLLAMA: OllamaRuntimeAdapter against the local on-premise Ollama daemon (Qwen).
- DISABLED: a stub adapter that fails closed with MODEL_UNAVAILABLE so every AI task
  degrades safely (REJECTED_UNAVAILABLE / FALLBACK) while deterministic care continues.

No cloud providers, no paid APIs, no API keys. Zero-dollar operation is preserved in
every mode.
"""

from app.ai_runtime.service import AIRuntimeService
from app.ai_runtime.adapters import MockDeterministicAdapter, OllamaRuntimeAdapter
from app.ai_runtime.adapters.base import RuntimeAdapter
from app.ai_runtime.models import AIProviderMode, ModelDescriptor, RuntimeConfig
from app.core.config import settings


class DisabledRuntimeAdapter(RuntimeAdapter):
    """Fails closed so AI tasks return REJECTED_UNAVAILABLE instead of fabricated output."""

    async def check_health(self):
        from app.ai_runtime.models import RuntimeState

        return RuntimeState.MODEL_UNAVAILABLE

    async def get_model_info(self) -> ModelDescriptor:
        return ModelDescriptor(
            model_id="disabled",
            version="0.0.0",
            quantization="NONE",
            parameter_count_billions=0.0,
            context_window_tokens=0,
            memory_budget_mb=0,
            is_clinically_validated=False,
        )

    async def invoke_raw(self, system_prompt: str, user_prompt: str, temperature: float = 0.0,
                         max_tokens: int = 1024, enforce_json: bool = True) -> str:
        raise RuntimeError("MODEL_UNAVAILABLE: AI provider mode is DISABLED by configuration.")


def build_runtime_service() -> AIRuntimeService:
    """Builds the application AI runtime service from settings.AI_PROVIDER_MODE."""
    mode = (settings.AI_PROVIDER_MODE or "MOCK_DETERMINISTIC").strip().upper()

    if mode == "LOCAL_OLLAMA":
        config = RuntimeConfig(
            provider_mode=AIProviderMode.LOCAL_OLLAMA,
            endpoint_url=settings.AI_RUNTIME_ENDPOINT,
            timeout_seconds=settings.AI_TIMEOUT_SECONDS,
            model_descriptor=ModelDescriptor(
                model_id=settings.AI_MODEL_ID,
                version="1.0.0",
                quantization="Q4_K_M",
                parameter_count_billions=4.0,
                context_window_tokens=8192,
                memory_budget_mb=3200,
            ),
        )
        return AIRuntimeService(runtime_adapter=OllamaRuntimeAdapter(config))

    if mode == "DISABLED":
        config = RuntimeConfig(
            provider_mode=AIProviderMode.DISABLED,
            endpoint_url=settings.AI_RUNTIME_ENDPOINT,
            timeout_seconds=settings.AI_TIMEOUT_SECONDS,
            model_descriptor=ModelDescriptor(
                model_id="disabled",
                version="0.0.0",
                quantization="NONE",
                parameter_count_billions=0.0,
                context_window_tokens=0,
                memory_budget_mb=0,
                is_clinically_validated=False,
            ),
        )
        return AIRuntimeService(runtime_adapter=DisabledRuntimeAdapter(config))

    return AIRuntimeService(runtime_adapter=MockDeterministicAdapter())
