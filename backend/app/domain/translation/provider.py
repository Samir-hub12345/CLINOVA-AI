"""CLINOVA AI — Translation Provider Abstraction.

Grounded in Phase 21 Sections 4, 5, 29, 31, 58.
Provides zero-cost, local-first provider implementations:
- TranslationProvider (abstract base class)
- MockTranslationProvider (test/dev deterministic provider)
- LocalTranslationProvider (local zero-cost translation provider)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio

class TranslationProvider(ABC):
    """Abstract interface for local translation engines."""

    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text from source language to target language.
        
        Returns dict with:
        - translated_text: str
        - provider: str
        - model_version: str
        - confidence: float
        """
        pass

class MockTranslationProvider(TranslationProvider):
    """Deterministic mock translation provider for CI/CD and tests."""

    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        if not text:
            return {
                "translated_text": "",
                "provider": "MockTranslationProvider",
                "model_version": "v1.mock",
                "confidence": 1.0,
            }
        
        if source_lang == target_lang:
            return {
                "translated_text": text,
                "provider": "MockTranslationProvider",
                "model_version": "v1.mock",
                "confidence": 1.0,
            }

        from app.baseline.intake.adapters import translate_text
        translated, _ = translate_text(text, source_lang, target_lang)

        # Confidence: High for known supported vocabulary, calibrated for uncertain/colloquial
        confidence = 0.95 if source_lang in ["hi", "or"] else 1.0
        if "शायद" in text or "हुएत" in text or "maybe" in text.lower():
            confidence = 0.65  # Flag uncertainty appropriately

        return {
            "translated_text": translated,
            "provider": "MockTranslationProvider",
            "model_version": "v1.mock",
            "confidence": confidence,
        }

class LocalTranslationProvider(TranslationProvider):
    """Local zero-cost translation provider operating entirely on-device."""

    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        if not text:
            return {
                "translated_text": "",
                "provider": "LocalTranslationProvider",
                "model_version": "v1.local",
                "confidence": 1.0,
            }

        if source_lang == target_lang:
            return {
                "translated_text": text,
                "provider": "LocalTranslationProvider",
                "model_version": "v1.local",
                "confidence": 1.0,
            }

        from app.baseline.intake.adapters import translate_text
        translated, _ = translate_text(text, source_lang, target_lang)

        return {
            "translated_text": translated,
            "provider": "LocalTranslationProvider",
            "model_version": "v1.local",
            "confidence": 0.90,
        }

class TimeoutTranslationProvider(TranslationProvider):
    """Provider specifically designed to simulate timeout scenarios for resilience testing."""

    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        await asyncio.sleep(10.0)
        return {
            "translated_text": text,
            "provider": "TimeoutTranslationProvider",
            "model_version": "v1.timeout",
            "confidence": 0.0,
        }

def get_translation_provider() -> TranslationProvider:
    """Factory providing the configured translation provider."""
    return MockTranslationProvider()
