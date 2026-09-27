import pytest
from app.services.speech_service import speech_service, SpeechService


def test_detect_script_multilingual():
    """Verify script detection across Indic and Latin scripts."""
    assert SpeechService.detect_script("मुझे तीन दिनों से बुखार है") == "Hindi"
    assert SpeechService.detect_script("ମୋତେ ୩ ଦିନ ହେଲା ଜ୍ୱର ଅଛି") == "Odia"
    assert SpeechService.detect_script("Patient reports mild headache and cough") == "English"
    assert SpeechService.detect_script("বাংলা ভাষায় উপসর্গ") == "Bengali"
    assert SpeechService.detect_script("") == "Unknown"
    assert SpeechService.detect_script("   12345 !@#$  ") == "Unknown"


@pytest.mark.asyncio
async def test_transcribe_empty_audio():
    """Verify empty audio payload yields truthful empty transcript without fake demo strings."""
    res = await speech_service.transcribe_audio(audio_bytes=b"", filename="empty.wav", language_hint="hi")
    assert res.transcript == ""
    assert res.confidence == 0.0
    assert res.is_demo_fallback is False
    assert "no speech" in res.disclaimer.lower()


@pytest.mark.asyncio
async def test_transcribe_audio_offline_graceful():
    """Verify non-empty audio without Gemini key returns truthful limitation without canned clinical diagnosis."""
    # Test with dummy audio payload (1000 bytes)
    dummy_wav = b"RIFF" + b"\x00" * 996
    res = await speech_service.transcribe_audio(audio_bytes=dummy_wav, filename="test.wav", language_hint="or")
    # Must not contain canned demo sentences
    assert "ପ୍ରବଳ ଜ୍ୱର" not in res.transcript
    assert "high fever" not in res.transcript
    assert res.is_demo_fallback is False
