from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import tempfile


class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes, file_name: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe the audio data.
        Returns a dictionary with:
        - transcript: str
        - confidence: float
        - metadata: dict (provider, model, duration, etc.)
        """
        pass


class MockSpeechToTextProvider(SpeechToTextProvider):
    def transcribe(self, audio_data: bytes, file_name: str, language: Optional[str] = None) -> Dict[str, Any]:
        # Return deterministic transcript suitable for synthetic benchmarks and tests
        duration_est = max(1.0, round(len(audio_data) / 16000.0, 2))
        return {
            "transcript": "fever for 3 days and severe body ache",
            "confidence": 0.95,
            "metadata": {
                "provider": "MockSpeechToTextProvider",
                "model": "mock-v1",
                "language": language or "en",
                "duration_seconds": duration_est,
                "ephemeral": True,
            },
        }


class LocalWhisperProvider(SpeechToTextProvider):
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            return self._model
        except ImportError:
            try:
                import whisper
                self._model = whisper.load_model(self.model_size)
                return self._model
            except ImportError:
                raise RuntimeError(
                    "Local Whisper engine not available. Please install faster-whisper or openai-whisper, or use MockSpeechToTextProvider."
                )

    def transcribe(self, audio_data: bytes, file_name: str, language: Optional[str] = None) -> Dict[str, Any]:
        model = self._load_model()
        ext = os.path.splitext(file_name)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            if hasattr(model, "transcribe") and not hasattr(model, "decode"):
                segments, info = model.transcribe(tmp_path, language=language)
                text = " ".join([seg.text.strip() for seg in segments])
                return {
                    "transcript": text.strip(),
                    "confidence": 0.92,
                    "metadata": {
                        "provider": "LocalWhisperProvider (faster-whisper)",
                        "model": self.model_size,
                        "language": info.language if hasattr(info, "language") else language,
                        "duration_seconds": info.duration if hasattr(info, "duration") else 0.0,
                        "ephemeral": True,
                    },
                }
            else:
                result = model.transcribe(tmp_path, language=language)
                return {
                    "transcript": result.get("text", "").strip(),
                    "confidence": 0.90,
                    "metadata": {
                        "provider": "LocalWhisperProvider (openai-whisper)",
                        "model": self.model_size,
                        "language": language or "en",
                        "ephemeral": True,
                    },
                }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def get_stt_provider() -> SpeechToTextProvider:
    provider_type = os.getenv("STT_PROVIDER", "mock").lower()
    if provider_type in ["whisper", "local", "faster-whisper"]:
        try:
            return LocalWhisperProvider()
        except Exception:
            return MockSpeechToTextProvider()
    return MockSpeechToTextProvider()
