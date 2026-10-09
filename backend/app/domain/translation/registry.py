"""CLINOVA AI — Multilingual Language Registry.

Grounded in Phase 21 Section 7.
Configuration-driven registry for verified languages:
- English (en)
- Hindi (hi)
- Odia (or)
"""

from typing import Dict, Any, List

SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "language_code": "en",
        "display_name": "English",
        "native_name": "English",
        "enabled": True,
        "translation_supported": True,
        "stt_supported": True,
        "ocr_supported": True,
    },
    "hi": {
        "language_code": "hi",
        "display_name": "Hindi",
        "native_name": "हिन्दी",
        "enabled": True,
        "translation_supported": True,
        "stt_supported": True,
        "ocr_supported": True,
    },
    "or": {
        "language_code": "or",
        "display_name": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "enabled": True,
        "translation_supported": True,
        "stt_supported": True,
        "ocr_supported": True,
    },
}

class UnsupportedLanguageError(Exception):
    """Raised when a language code is not enabled or supported for the requested modality."""
    pass

def validate_language_pair(source_lang: str, target_lang: str) -> None:
    """Validates that both source and target languages are supported."""
    if not source_lang or source_lang not in SUPPORTED_LANGUAGES or not SUPPORTED_LANGUAGES[source_lang].get("translation_supported"):
        raise UnsupportedLanguageError(f"Source language '{source_lang}' is not supported for translation.")
    if not target_lang or target_lang not in SUPPORTED_LANGUAGES or not SUPPORTED_LANGUAGES[target_lang].get("translation_supported"):
        raise UnsupportedLanguageError(f"Target language '{target_lang}' is not supported for translation.")

def get_language_metadata(language_code: str) -> Dict[str, Any]:
    """Returns registry metadata for a given language code."""
    if language_code not in SUPPORTED_LANGUAGES:
        raise UnsupportedLanguageError(f"Language '{language_code}' is not registered.")
    return SUPPORTED_LANGUAGES[language_code]

def list_supported_languages() -> List[Dict[str, Any]]:
    """Returns list of enabled languages with modality capabilities."""
    return [meta for meta in SUPPORTED_LANGUAGES.values() if meta.get("enabled")]
