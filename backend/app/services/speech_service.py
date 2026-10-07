"""Audio speech-to-text service for Clinova AI with Sarvam Saaras v4 and native Indic script support."""

import re
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.case import SpeechTranscribeResponse
from app.services.providers.sarvam_stt import SarvamSaarasAdapter
from app.services.providers.local_fallback import LocalSpeechToTextProvider

logger = logging.getLogger("clinova.speech")


class SpeechService:
    """Audio speech-to-text service powered by Sarvam Saaras v4 with deterministic local fallback."""

    def __init__(self):
        self.local_provider = LocalSpeechToTextProvider()
        self.adapter = SarvamSaarasAdapter(fallback_provider=self.local_provider)

    @staticmethod
    def detect_script(text: str) -> str:
        """Identify language from text script blocks."""
        return LocalSpeechToTextProvider.detect_script(text)

    async def transcribe_audio(
        self, audio_bytes: bytes, filename: str = "recording.wav", language_hint: str = "en"
    ) -> SpeechTranscribeResponse:
        """Transcribe uploaded audio bytes accurately using configured speech models."""
        if not audio_bytes or len(audio_bytes) == 0:
            return SpeechTranscribeResponse(
                transcript="",
                detected_language="Unknown",
                confidence=0.0,
                duration_seconds=0.0,
                is_demo_fallback=False,
                disclaimer="Empty audio payload — no speech captured.",
            )

        duration_est = round(len(audio_bytes) / 32000.0, 1)

        try:
            transcript, metadata = await self.adapter.transcribe(
                audio_bytes=audio_bytes,
                language_hint=language_hint,
            )
            detected_lang = self.detect_script(transcript)
            if detected_lang == "Unknown" and language_hint:
                detected_lang = "Hindi" if language_hint in ("hi", "hindi") else "Odia" if language_hint in ("or", "odia") else "English"

            return SpeechTranscribeResponse(
                transcript=transcript,
                detected_language=detected_lang,
                confidence=0.95 if not metadata.fallback_used else 0.85,
                duration_seconds=duration_est,
                is_demo_fallback=False,
                disclaimer="Speech transcription — review carefully before clinical submission.",
            )
        except Exception as e:
            logger.error("Audio transcription error: %s", e)
            return SpeechTranscribeResponse(
                transcript="",
                detected_language="Hindi" if language_hint == "hi" else "Odia" if language_hint == "or" else "English",
                confidence=0.0,
                duration_seconds=duration_est,
                is_demo_fallback=False,
                disclaimer="Automated backend transcription unavailable. Please review or type symptoms manually.",
            )


speech_service = SpeechService()
