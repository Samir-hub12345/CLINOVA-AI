"""Sarvam Saaras v4 Speech-to-Text provider adapter for Clinova AI."""

import time
import logging
from typing import Optional, Tuple
import httpx

from app.core.config import settings
from app.services.providers.base import (
    SpeechToTextProvider,
    ProviderResponseMetadata,
    ProviderError,
    ProviderErrorCode,
)
from app.services.providers.local_fallback import LocalSpeechToTextProvider

logger = logging.getLogger("clinova.providers.sarvam_stt")


class SarvamSaarasAdapter(SpeechToTextProvider):
    """Adapter for Sarvam Saaras v4 Speech-to-Text REST API.
    
    Supports 23 Indian languages + English, automatic language detection,
    and code-mixed speech (e.g., Hindi + English, Odia + English).
    Default mode is 'transcribe' to preserve verbatim native script.
    """

    API_ENDPOINT = "https://api.sarvam.ai/speech-to-text"

    def __init__(self, api_key: Optional[str] = None, fallback_provider: Optional[SpeechToTextProvider] = None):
        super().__init__(provider_name="sarvam_saaras_v4")
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.model_name = settings.SARVAM_STT_MODEL
        self.fallback = fallback_provider or LocalSpeechToTextProvider()

    def is_available(self) -> bool:
        return bool(settings.AI_EXTERNAL_ENABLED and self.api_key and self.api_key.strip())

    @staticmethod
    def _map_language_code(hint: Optional[str]) -> str:
        if not hint:
            return "unknown"
        hint = hint.lower().strip()
        mapping = {
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
            "en": "en-IN",
            "english": "en-IN",
        }
        return mapping.get(hint, "unknown")

    async def transcribe(
        self, audio_bytes: bytes, language_hint: Optional[str] = None
    ) -> Tuple[str, ProviderResponseMetadata]:
        if not audio_bytes or len(audio_bytes) == 0:
            raise ProviderError(
                error_code=ProviderErrorCode.VALIDATION_ERROR,
                message="Audio payload is empty.",
                provider_name=self.provider_name,
                retryable=False,
            )

        duration_est = round(len(audio_bytes) / 32000.0, 1)
        if duration_est > 30.0:
            # REST endpoint supports up to 30s
            logger.warning("Audio duration (%.1fs) exceeds REST 30s limit.", duration_est)

        # Fallback if external APIs are disabled or credentials missing
        if not self.is_available():
            logger.info("Sarvam Saaras STT external API disabled or key absent. Using local fallback.")
            transcript, meta = await self.fallback.transcribe(audio_bytes, language_hint)
            meta.fallback_used = True
            return transcript, meta

        # External live call with bounded timeout and safe error normalization
        lang_code = self._map_language_code(language_hint)
        start_time = time.time()
        
        headers = {
            "api-subscription-key": self.api_key.strip(),
        }
        files = {
            "file": ("recording.wav", audio_bytes, "audio/wav"),
        }
        data = {
            "model": self.model_name,
            "language_code": lang_code,
            "mode": "transcribe",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.API_ENDPOINT, headers=headers, files=files, data=data)

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                resp_json = response.json()
                transcript = resp_json.get("transcript", "").strip()
                metadata = ProviderResponseMetadata(
                    provider_name=self.provider_name,
                    model_name=self.model_name,
                    latency_ms=latency_ms,
                    fallback_used=False,
                    processing_status="success",
                )
                return transcript, metadata

            elif response.status_code in (401, 403):
                raise ProviderError(
                    error_code=ProviderErrorCode.AUTHENTICATION_ERROR,
                    message="Sarvam API authentication failed.",
                    provider_name=self.provider_name,
                    retryable=False,
                )
            elif response.status_code == 429:
                raise ProviderError(
                    error_code=ProviderErrorCode.RATE_LIMITED,
                    message="Sarvam STT rate limit or quota exceeded.",
                    provider_name=self.provider_name,
                    retryable=True,
                )
            else:
                raise ProviderError(
                    error_code=ProviderErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"Sarvam STT returned status {response.status_code}",
                    provider_name=self.provider_name,
                    retryable=response.status_code >= 500,
                )

        except httpx.TimeoutException:
            logger.warning("Sarvam STT timeout occurred.")
            if self.fallback:
                transcript, meta = await self.fallback.transcribe(audio_bytes, language_hint)
                meta.fallback_used = True
                return transcript, meta
            raise ProviderError(
                error_code=ProviderErrorCode.TIMEOUT,
                message="Sarvam STT request timed out.",
                provider_name=self.provider_name,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.warning("Sarvam STT network error: %s", exc)
            if self.fallback:
                transcript, meta = await self.fallback.transcribe(audio_bytes, language_hint)
                meta.fallback_used = True
                return transcript, meta
            raise ProviderError(
                error_code=ProviderErrorCode.NETWORK_ERROR,
                message="Sarvam STT connection failed.",
                provider_name=self.provider_name,
                retryable=True,
            )
