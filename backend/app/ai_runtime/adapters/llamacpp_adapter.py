"""CLINOVA AI — Local llama.cpp Server Runtime Adapter.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Connects to an in-process or local llama-server instance via OpenAI-compatible endpoints.
Minimal CPU footprint, ideal for low-cost Intel Celeron edge deployments.
"""

from typing import Dict, Any, Optional
import httpx
from app.ai_runtime.adapters.base import RuntimeAdapter
from app.ai_runtime.models import (
    RuntimeConfig,
    RuntimeState,
    ModelDescriptor,
)


class LlamaCppRuntimeAdapter(RuntimeAdapter):
    """Runtime adapter for local llama.cpp / llama-server HTTP endpoints."""

    def __init__(self, config: RuntimeConfig):
        super().__init__(config)
        self.base_url = config.endpoint_url.rstrip("/")

    async def check_health(self) -> RuntimeState:
        """Checks health via /health endpoint."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/health")
                if res.status_code == 200:
                    status_text = res.json().get("status", "")
                    if status_text in ("ok", "ready", "loading model"):
                        return RuntimeState.MODEL_READY
                    return RuntimeState.MODEL_WARM
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
        """Executes completion via /v1/chat/completions."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        payload: Dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if enforce_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                    return ""
                elif response.status_code == 507:
                    raise MemoryError("OUT_OF_MEMORY: llama.cpp host RAM limits reached.")
                else:
                    raise RuntimeError(
                        f"llama.cpp server error HTTP {response.status_code}: {response.text}"
                    )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"TIMEOUT: llama.cpp exceeded {self.config.timeout_seconds}s limit: {exc}")
        except httpx.ConnectError as exc:
            raise RuntimeError(f"MODEL_UNAVAILABLE: Could not reach llama.cpp at {self.base_url}: {exc}")
