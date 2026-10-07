"""Sarvam Mayura Translation provider adapter for Clinova AI with safe chunking."""

import time
import re
import logging
from typing import Optional, List, Tuple
import httpx

from app.core.config import settings
from app.services.providers.base import (
    TranslationProvider,
    ProviderResponseMetadata,
    ProviderError,
    ProviderErrorCode,
)
from app.services.providers.local_fallback import LocalTranslationProvider

logger = logging.getLogger("clinova.providers.sarvam_translation")


class SarvamTranslationAdapter(TranslationProvider):
    """Adapter for Sarvam Mayura v1 Translation API.
    
    Supports English, Hindi, Odia, Bengali, Tamil, Telugu, and other Indic languages.
    Implements sentence-aware safe chunking for inputs exceeding 1,000 characters.
    """

    API_ENDPOINT = "https://api.sarvam.ai/translate"
    MAX_CHUNK_CHARS = 900  # Conservative boundary below the 1,000-character limit

    def __init__(self, api_key: Optional[str] = None, fallback_provider: Optional[TranslationProvider] = None):
        super().__init__(provider_name="sarvam_mayura_v1")
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.model_name = settings.SARVAM_TRANSLATION_MODEL
        self.fallback = fallback_provider or LocalTranslationProvider()

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
            "auto": "auto",
        }
        return mapping.get(code, "auto" if code == "auto" else "en-IN")

    def _split_into_chunks(self, text: str) -> List[str]:
        """Sentence-aware chunking preserving order and boundary punctuation."""
        if len(text) <= self.MAX_CHUNK_CHARS:
            return [text]

        # Split on sentence boundaries: periods, purna viram (।), question marks, newlines
        sentence_delims = re.compile(r"(?<=[।.\n?!])\s*")
        raw_sentences = [s.strip() for s in sentence_delims.split(text) if s.strip()]

        chunks = []
        current_chunk = []
        current_len = 0

        for sent in raw_sentences:
            if current_len + len(sent) + 1 <= self.MAX_CHUNK_CHARS:
                current_chunk.append(sent)
                current_len += len(sent) + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                # If a single sentence is itself longer than MAX_CHUNK_CHARS, split by word
                if len(sent) > self.MAX_CHUNK_CHARS:
                    words = sent.split()
                    sub_chunk = []
                    sub_len = 0
                    for word in words:
                        if sub_len + len(word) + 1 <= self.MAX_CHUNK_CHARS:
                            sub_chunk.append(word)
                            sub_len += len(word) + 1
                        else:
                            chunks.append(" ".join(sub_chunk))
                            sub_chunk = [word]
                            sub_len = len(word)
                    if sub_chunk:
                        current_chunk = sub_chunk
                        current_len = sub_len
                else:
                    current_chunk = [sent]
                    current_len = len(sent)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def _translate_single_chunk(self, client: httpx.AsyncClient, chunk: str, src_code: str, tgt_code: str) -> str:
        headers = {
            "api-subscription-key": self.api_key.strip(),
            "Content-Type": "application/json",
        }
        payload = {
            "input": chunk,
            "source_language_code": src_code,
            "target_language_code": tgt_code,
            "model": self.model_name,
            "mode": "formal",
        }

        response = await client.post(self.API_ENDPOINT, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("translated_text", "").strip()
        elif response.status_code in (401, 403):
            raise ProviderError(
                error_code=ProviderErrorCode.AUTHENTICATION_ERROR,
                message="Sarvam Translation API key unauthorized.",
                provider_name=self.provider_name,
            )
        elif response.status_code == 429:
            raise ProviderError(
                error_code=ProviderErrorCode.RATE_LIMITED,
                message="Sarvam Translation rate limit exceeded.",
                provider_name=self.provider_name,
                retryable=True,
            )
        else:
            raise ProviderError(
                error_code=ProviderErrorCode.PROVIDER_UNAVAILABLE,
                message=f"Sarvam Translation returned status {response.status_code}",
                provider_name=self.provider_name,
                retryable=response.status_code >= 500,
            )

    async def translate(
        self, text: str, source_lang: str = "auto", target_lang: str = "en"
    ) -> Tuple[str, ProviderResponseMetadata]:
        if not text or not text.strip():
            raise ProviderError(
                error_code=ProviderErrorCode.VALIDATION_ERROR,
                message="Text to translate is empty.",
                provider_name=self.provider_name,
                retryable=False,
            )

        if not self.is_available():
            logger.info("Sarvam Translation API disabled or key absent. Using local fallback.")
            result, meta = await self.fallback.translate(text, source_lang, target_lang)
            meta.fallback_used = True
            return result, meta

        src_code = self._map_lang_code(source_lang)
        tgt_code = self._map_lang_code(target_lang)

        chunks = self._split_into_chunks(text)
        start_time = time.time()
        translated_chunks = []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                for chunk in chunks:
                    trans_chunk = await self._translate_single_chunk(client, chunk, src_code, tgt_code)
                    translated_chunks.append(trans_chunk)

            latency_ms = int((time.time() - start_time) * 1000)
            full_translated = " ".join(translated_chunks)

            metadata = ProviderResponseMetadata(
                provider_name=self.provider_name,
                model_name=self.model_name,
                latency_ms=latency_ms,
                fallback_used=False,
                processing_status="success",
            )
            return full_translated, metadata

        except httpx.TimeoutException:
            logger.warning("Sarvam Translation timeout. Falling back to local translation.")
            if self.fallback:
                result, meta = await self.fallback.translate(text, source_lang, target_lang)
                meta.fallback_used = True
                return result, meta
            raise ProviderError(
                error_code=ProviderErrorCode.TIMEOUT,
                message="Sarvam Translation request timed out.",
                provider_name=self.provider_name,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.warning("Sarvam Translation network error: %s. Using local fallback.", exc)
            if self.fallback:
                result, meta = await self.fallback.translate(text, source_lang, target_lang)
                meta.fallback_used = True
                return result, meta
            raise ProviderError(
                error_code=ProviderErrorCode.NETWORK_ERROR,
                message="Sarvam Translation network failure.",
                provider_name=self.provider_name,
                retryable=True,
            )
