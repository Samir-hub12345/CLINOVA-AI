"""Groq LLM text generation provider adapter for Clinova AI with structured output validation."""

import time
import json
import logging
from typing import Optional, Tuple
import httpx

from app.core.config import settings
from app.services.providers.base import (
    TextGenerationProvider,
    ProviderResponseMetadata,
    ProviderError,
    ProviderErrorCode,
)
from app.services.providers.local_fallback import LocalTextGenerationProvider

logger = logging.getLogger("clinova.providers.groq_llm")


class GroqTextGenerationAdapter(TextGenerationProvider):
    """Adapter for Groq text generation with openai/gpt-oss-120b.
    
    Used strictly as a baseline capability behind the Clinova abstraction layer.
    Enforces structured output validation, schema parsing, and deterministic fallback.
    Prohibited from making autonomous definitive diagnoses or prescriptions.
    """

    API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, fallback_provider: Optional[TextGenerationProvider] = None):
        super().__init__(provider_name="groq_text_engine")
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        self.fallback = fallback_provider or LocalTextGenerationProvider()

    def is_available(self) -> bool:
        return bool(settings.AI_EXTERNAL_ENABLED and self.api_key and self.api_key.strip())

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, ProviderResponseMetadata]:
        if not prompt or not prompt.strip():
            raise ProviderError(
                error_code=ProviderErrorCode.VALIDATION_ERROR,
                message="Prompt text cannot be empty.",
                provider_name=self.provider_name,
                retryable=False,
            )

        if not self.is_available():
            logger.info("Groq external API disabled or key absent. Using local rule fallback.")
            output, meta = await self.fallback.generate(prompt, system_instruction, temperature)
            meta.fallback_used = True
            return output, meta

        sys_inst = system_instruction or (
            "You are Clinova AI's structured clinical documentation support assistant. "
            "You provide strictly non-definitive, draft triage and SOAP structuring. "
            "Never produce definitive autonomous medical diagnoses or prescriptions. "
            "Return valid JSON only."
        )

        messages = [
            {"role": "system", "content": sys_inst},
            {"role": "user", "content": prompt},
        ]

        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(self.API_ENDPOINT, headers=headers, json=payload)

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                resp_json = response.json()
                choices = resp_json.get("choices", [])
                if not choices:
                    raise ProviderError(
                        error_code=ProviderErrorCode.PROCESSING_ERROR,
                        message="Groq returned empty choices list.",
                        provider_name=self.provider_name,
                    )

                content = choices[0].get("message", {}).get("content", "").strip()

                # Validate JSON structure if expected
                try:
                    json.loads(content)
                except json.JSONDecodeError as err:
                    logger.warning("Groq response was not valid JSON: %s", err)
                    raise ProviderError(
                        error_code=ProviderErrorCode.PROCESSING_ERROR,
                        message="Groq output failed JSON schema validation.",
                        provider_name=self.provider_name,
                    )

                metadata = ProviderResponseMetadata(
                    provider_name=self.provider_name,
                    model_name=self.model_name,
                    latency_ms=latency_ms,
                    fallback_used=False,
                    processing_status="success",
                )
                return content, metadata

            elif response.status_code in (401, 403):
                raise ProviderError(
                    error_code=ProviderErrorCode.AUTHENTICATION_ERROR,
                    message="Groq API key unauthorized.",
                    provider_name=self.provider_name,
                )
            elif response.status_code == 429:
                raise ProviderError(
                    error_code=ProviderErrorCode.RATE_LIMITED,
                    message="Groq rate limit exceeded.",
                    provider_name=self.provider_name,
                    retryable=True,
                )
            else:
                raise ProviderError(
                    error_code=ProviderErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"Groq returned HTTP {response.status_code}",
                    provider_name=self.provider_name,
                    retryable=response.status_code >= 500,
                )

        except httpx.TimeoutException:
            logger.warning("Groq request timed out. Using local fallback.")
            if self.fallback:
                output, meta = await self.fallback.generate(prompt, system_instruction, temperature)
                meta.fallback_used = True
                return output, meta
            raise ProviderError(
                error_code=ProviderErrorCode.TIMEOUT,
                message="Groq request timed out.",
                provider_name=self.provider_name,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.warning("Groq network failure: %s. Using local fallback.", exc)
            if self.fallback:
                output, meta = await self.fallback.generate(prompt, system_instruction, temperature)
                meta.fallback_used = True
                return output, meta
            raise ProviderError(
                error_code=ProviderErrorCode.NETWORK_ERROR,
                message="Groq connection failure.",
                provider_name=self.provider_name,
                retryable=True,
            )
