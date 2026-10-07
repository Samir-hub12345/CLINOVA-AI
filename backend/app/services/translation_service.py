"""Multilingual translation and clinical normalization service for Clinova AI."""

import logging
from app.core.config import settings
from app.schemas.case import TranslationResponse
from app.services.providers.sarvam_translation import SarvamTranslationAdapter
from app.services.providers.local_fallback import LocalTranslationProvider

logger = logging.getLogger("clinova.translation")


class TranslationService:
    """Multilingual translation and normalization service preserving original inputs."""

    def __init__(self):
        self.local_provider = LocalTranslationProvider()
        self.adapter = SarvamTranslationAdapter(fallback_provider=self.local_provider)

    async def translate_and_normalize(
        self, text: str, source_language: str = "en"
    ) -> TranslationResponse:
        """Translates regional input (Hindi/Odia) to English while preserving original text."""
        lang_code = source_language.lower()

        if lang_code in ("en", "english"):
            return TranslationResponse(
                original_text=text,
                original_language="English",
                translated_text=text,
                target_language="en",
                normalization_summary="Original English input retained and normalized.",
                is_demo_fallback=False,
            )

        lang_name = "Odia" if lang_code in ("or", "odia") else "Hindi" if lang_code in ("hi", "hindi") else source_language

        try:
            translated_text, metadata = await self.adapter.translate(
                text=text,
                source_lang=source_language,
                target_lang="en",
            )
            return TranslationResponse(
                original_text=text,
                original_language=lang_name,
                translated_text=translated_text,
                target_language="en",
                normalization_summary=f"Normalized from {lang_name} regional dialect to clinical English representation.",
                is_demo_fallback=metadata.fallback_used,
            )
        except Exception as e:
            logger.error("Translation error: %s. Using local fallback.", e)
            translated_text, meta = await self.local_provider.translate(text, source_language, "en")
            return TranslationResponse(
                original_text=text,
                original_language=lang_name,
                translated_text=translated_text,
                target_language="en",
                normalization_summary=f"Processed in regional language ({lang_name}).",
                is_demo_fallback=True,
            )


translation_service = TranslationService()
