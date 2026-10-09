"""CLINOVA AI — Local Ollama Runtime Adapter.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Connects to local on-premise Ollama daemon (default: http://127.0.0.1:11434).
Zero cloud communication, zero API fees.
"""

from typing import Dict, Any, Optional
import httpx
from app.ai_runtime.adapters.base import RuntimeAdapter
from app.ai_runtime.models import (
    RuntimeConfig,
    RuntimeState,
    ModelDescriptor,
)


class OllamaRuntimeAdapter(RuntimeAdapter):
    """Runtime adapter for local Ollama server running Qwen models."""

    def __init__(self, config: RuntimeConfig):
        super().__init__(config)
        self.base_url = config.endpoint_url.rstrip("/")

    async def check_health(self) -> RuntimeState:
        """Probes Ollama daemon via /api/tags."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models_data = res.json().get("models", [])
                    target_model = self.config.model_descriptor.model_id
                    # Check if requested model or family is present
                    has_model = any(target_model in m.get("name", "") for m in models_data)
                    return RuntimeState.MODEL_READY if has_model else RuntimeState.MODEL_DISCOVERY
                return RuntimeState.MODEL_LOAD_FAILURE
        except (httpx.ConnectError, httpx.ConnectTimeout):
            return RuntimeState.MODEL_UNAVAILABLE
        except Exception:
            return RuntimeState.PROCESS_CRASH

    async def get_model_info(self) -> ModelDescriptor:
        return self.config.model_descriptor

    async def invoke_raw(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        enforce_json: bool = True,
    ) -> str:
        """Executes generation against Ollama /api/generate."""
        payload: Dict[str, Any] = {
            "model": self.config.model_descriptor.model_id,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if enforce_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                elif response.status_code == 507:
                    raise MemoryError("OUT_OF_MEMORY: Edge device GPU/RAM exceeded.")
                else:
                    raise RuntimeError(
                        f"Ollama server returned HTTP {response.status_code}: {response.text}"
                    )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"TIMEOUT: Ollama inference exceeded {self.config.timeout_seconds}s limit: {exc}")
        except httpx.ConnectError as exc:
            raise RuntimeError(f"MODEL_UNAVAILABLE: Could not connect to Ollama daemon at {self.base_url}: {exc}")
