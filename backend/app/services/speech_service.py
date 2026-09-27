import re
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.case import SpeechTranscribeResponse

logger = logging.getLogger("clinova.speech")


class SpeechService:
    """Audio speech-to-text service with real multimodal transcription and native Indic script support."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if not settings.OFFLINE_DEMO and self.api_key and self.api_key.strip():
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("SpeechService initialized with Gemini GenAI client.")
            except Exception as e:
                logger.warning("Could not initialize GenAI Client for SpeechService: %s", e)

    @staticmethod
    def detect_script(text: str) -> str:
        """Identify language from text script blocks."""
        if not text or not text.strip():
            return "Unknown"
        if re.search(r"[\u0B00-\u0B7F]", text):
            return "Odia"
        if re.search(r"[\u0900-\u097F]", text):
            return "Hindi"
        if re.search(r"[\u0980-\u09FF]", text):
            return "Bengali"
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "Tamil"
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "Telugu"
        if re.search(r"[a-zA-Z]", text):
            return "English"
        return "Unknown"

    async def transcribe_audio(
        self, audio_bytes: bytes, filename: str = "recording.wav", language_hint: str = "en"
    ) -> SpeechTranscribeResponse:
        """Transcribe uploaded audio bytes accurately using configured AI speech models."""
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

        # Multimodal transcription via Gemini
        if self.client:
            try:
                from google.genai import types

                mime_type = "audio/wav"
                ext = filename.lower()
                if ext.endswith(".webm"):
                    mime_type = "audio/webm"
                elif ext.endswith(".mp3"):
                    mime_type = "audio/mp3"
                elif ext.endswith(".ogg"):
                    mime_type = "audio/ogg"

                prompt = (
                    f"Transcribe this clinical speech recording accurately in its original spoken language and script. "
                    f"Target language hint: {language_hint}. "
                    f"Do not translate. Preserve native Indic script (e.g., Devanagari for Hindi, Odia script for Odia, Latin for English). "
                    f"Output ONLY the verbatim transcribed words without commentary or pleasantries."
                )

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                        prompt,
                    ],
                )

                raw_transcript = (response.text or "").strip()
                detected_lang = self.detect_script(raw_transcript)
                if detected_lang == "Unknown" and language_hint:
                    detected_lang = "Hindi" if language_hint == "hi" else "Odia" if language_hint == "or" else "English"

                return SpeechTranscribeResponse(
                    transcript=raw_transcript,
                    detected_language=detected_lang,
                    confidence=0.95,
                    duration_seconds=duration_est,
                    is_demo_fallback=False,
                    disclaimer="Speech transcription — review carefully before clinical submission.",
                )
            except Exception as e:
                logger.error("Gemini audio transcription error: %s", e)

        # Service unavailable or offline
        return SpeechTranscribeResponse(
            transcript="",
            detected_language="Hindi" if language_hint == "hi" else "Odia" if language_hint == "or" else "English",
            confidence=0.0,
            duration_seconds=duration_est,
            is_demo_fallback=False,
            disclaimer="Automated backend transcription requires an active AI service key. Please type symptoms manually or use browser speech recognition.",
        )


speech_service = SpeechService()
