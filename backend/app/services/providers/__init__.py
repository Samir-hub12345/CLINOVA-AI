"""Clinova AI Provider Abstraction & Adapter Layer."""

from app.services.providers.base import (
    ProviderInterface,
    SpeechToTextProvider,
    OCRProvider,
    TranslationProvider,
    TextGenerationProvider,
    TextToSpeechProvider,
    ProviderError,
    ProviderErrorCode,
    ProviderResponseMetadata,
)
from app.services.providers.local_fallback import (
    LocalSpeechToTextProvider,
    LocalOCRProvider,
    LocalTranslationProvider,
    LocalTextToSpeechProvider,
    LocalTextGenerationProvider,
)
from app.services.providers.sarvam_stt import SarvamSaarasAdapter
from app.services.providers.ocr_space import OCRSpaceAdapter
from app.services.providers.sarvam_translation import SarvamTranslationAdapter
from app.services.providers.sarvam_tts import SarvamBulbulAdapter
from app.services.providers.groq_llm import GroqTextGenerationAdapter

__all__ = [
    "ProviderInterface",
    "SpeechToTextProvider",
    "OCRProvider",
    "TranslationProvider",
    "TextGenerationProvider",
    "TextToSpeechProvider",
    "ProviderError",
    "ProviderErrorCode",
    "ProviderResponseMetadata",
    "LocalSpeechToTextProvider",
    "LocalOCRProvider",
    "LocalTranslationProvider",
    "LocalTextToSpeechProvider",
    "LocalTextGenerationProvider",
    "SarvamSaarasAdapter",
    "OCRSpaceAdapter",
    "SarvamTranslationAdapter",
    "SarvamBulbulAdapter",
    "GroqTextGenerationAdapter",
]
