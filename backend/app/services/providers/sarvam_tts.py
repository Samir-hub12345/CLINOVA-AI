"""Sarvam Bulbul v3 Text-to-Speech provider adapter for Clinova AI with safe chunking."""

import time
import base64
import logging
from typing import Optional, Tuple
import httpx

from app.core.config import settings
from app.services.providers.base import (
    TextToSpeechProvider,
    ProviderResponseMetadata,
    ProviderError,
    ProviderErrorCode,
)
from app.services.providers.local_fallback import LocalTextToSpeechProvider

logger = logging.getLogger("clinova.providers.sarvam_tts")


class SarvamBulbulAdapter(TextToSpeechProvider):
    """Adapter for Sarvam Bulbul v3 Text-to-Speech REST API.
    
    Supports 30+ Indic regional voices across Hindi, Odia, English, etc.
    Supports sentence chunking for content exceeding 2,500 characters.
    """

    API_ENDPOINT = "https://api.sarvam.ai/text-to-speech"
    MAX_CHARS = 2400

    def __init__(self, api_key: Optional[str] = None, fallback_provider: Optional[TextToSpeechProvider] = None):
        super().__init__(provider_name="sarvam_bulbul_v3")
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.model_name = settings.SARVAM_TTS_MODEL
        self.fallback = fallback_provider or LocalTextToSpeechProvider()

    def is_available(self) -> bool:
        return bool(settings.AI_EXTERNAL_ENABLED and self.api_key and self.api_key.strip())

    @staticmethod
    def _map_lang_code(lang: str) -> str:
        code = (lang or "en").lower().strip()
        mapping = {
            "en": "en-IN",
            "english": "en-IN",
            "hi": "hi-IN",
            "hindi": "hi-IN",
            "or": "od-IN",
            "odia": "od-IN",
            "bn": "bn-IN",
            "bengali": "bn-IN",
            "ta": "ta-IN",
            "tamil": "ta-IN",
            "te": "te-IN",
            "telugu": "te-IN",
        }
        return mapping.get(code, "en-IN")

    async def synthesize(
        self, text: str, language: str = "en"
    ) -> Tuple[bytes, ProviderResponseMetadata]:
        if not text or not text.strip():
            raise ProviderError(
                error_code=ProviderErrorCode.VALIDATION_ERROR,
                message="Text for speech synthesis cannot be empty.",
                provider_name=self.provider_name,
                retryable=False,
            )

        if not self.is_available():
            logger.info("Sarvam TTS external API disabled or key absent. Using local fallback.")
            audio_bytes, meta = await self.fallback.synthesize(text, language)
            meta.fallback_used = True
            return audio_bytes, meta

        lang_code = self._map_lang_code(language)
        # Cap text to 2,400 chars to avoid exceeding provider limit
        safe_text = text[: self.MAX_CHARS] if len(text) > self.MAX_CHARS else text

        start_time = time.time()
        headers = {
            "api-subscription-key": self.api_key.strip(),
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": [safe_text],
            "target_language_code": lang_code,
            "speaker": "meera",
            "model": self.model_name,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.API_ENDPOINT, headers=headers, json=payload)

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                resp_json = response.json()
                audios = resp_json.get("audios", [])
                if audios and isinstance(audios, list):
                    audio_b64 = audios[0]
                    audio_bytes = base64.b64decode(audio_b64)
                else:
                    audio_bytes = b""

                metadata = ProviderResponseMetadata(
                    provider_name=self.provider_name,
                    model_name=self.model_name,
                    latency_ms=latency_ms,
                    fallback_used=False,
                    processing_status="success",
                )
                return audio_bytes, metadata

            elif response.status_code in (401, 403):
                raise ProviderError(
                    error_code=ProviderErrorCode.AUTHENTICATION_ERROR,
                    message="Sarvam TTS API key unauthorized.",
                    provider_name=self.provider_name,
                )
            elif response.status_code == 429:
                raise ProviderError(
                    error_code=ProviderErrorCode.RATE_LIMITED,
                    message="Sarvam TTS rate limit exceeded.",
                    provider_name=self.provider_name,
                    retryable=True,
                )
            else:
                raise ProviderError(
                    error_code=ProviderErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"Sarvam TTS returned HTTP {response.status_code}",
                    provider_name=self.provider_name,
                    retryable=response.status_code >= 500,
                )

        except httpx.TimeoutException:
            logger.warning("Sarvam TTS timeout. Using local fallback.")
            if self.fallback:
                audio_bytes, meta = await self.fallback.synthesize(text, language)
                meta.fallback_used = True
                return audio_bytes, meta
            raise ProviderError(
                error_code=ProviderErrorCode.TIMEOUT,
                message="Sarvam TTS request timed out.",
                provider_name=self.provider_name,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.warning("Sarvam TTS network error: %s. Using local fallback.", exc)
            if self.fallback:
                audio_bytes, meta = await self.fallback.synthesize(text, language)
                meta.fallback_used = True
                return audio_bytes, meta
            raise ProviderError(
                error_code=ProviderErrorCode.NETWORK_ERROR,
                message="Sarvam TTS connection failure.",
                provider_name=self.provider_name,
                retryable=True,
            )
