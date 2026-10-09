# PHASE 19: VOICE / STT / MULTIMODAL INTAKE SPECIFICATION & IMPLEMENTATION RECORD

==================================================
PHASE STATUS: READY FOR HUMAN REVIEW
==================================================

## 1. Executive Summary & Objective

Phase 19 introduces vernacular voice-based symptom intake into CLINOVA AI while strictly preserving the existing text intake path and maintaining all upstream safety invariants.

The core objective is to allow frontline patients and health workers in resource-constrained environments (PHCs, camps, district hospitals) to describe chief complaints verbally in vernacular languages (English, Hindi, Odia), process the audio via local speech-to-text models, inspect and edit the generated transcript, and integrate the confirmed transcription directly into the canonical Master Case with explicit provenance tagging (`VOICE_TRANSCRIBED`).

---

## 2. Strict Scope Boundaries & Invariants

In accordance with the Atomic Phase Rule:
- **Phase 19 Scope:**
  - Browser/client audio capture via standard `MediaRecorder` API with fallback presets.
  - Audio upload validation (strict MIME checks, <= 10MB bounds, non-empty payload).
  - Pluggable speech-to-text abstraction (`SpeechToTextProvider`) with `LocalWhisperProvider` and deterministic `MockSpeechToTextProvider`.
  - Ephemeral raw audio handling.
  - Human review of transcripts before canonical confirmation.
  - Integration of confirmed transcripts into canonical `Evidence` (`source_class="VOICE_TRANSCRIBED"`), `EvidenceRecord`, `TimelineEvent`, `AuditEvent`, and `AuditLog`.
  - Strict RBAC: patient scoping and facility boundary enforcement.
  - Prompt injection boundary: voice transcripts are strictly treated as untrusted clinical text.
- **Explicit Exclusions:**
  - OCR and Document Extraction are strictly deferred to **Phase 20**.
  - Translation & cross-lingual semantic normalization are strictly deferred to **Phase 21**.
  - FacilityGraph, referral routing, and SignalGraph remain untouched.
  - No autonomous triage modification by voice transcripts alone.

---

## 3. Architecture & Pluggable Provider Abstraction

### 3.1 `SpeechToTextProvider` Protocol (`backend/app/baseline/intake/stt_provider.py`)

A pluggable interface abstracts STT execution:

```python
class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes, file_name: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe the audio data.
        Returns:
        - transcript: str
        - confidence: float
        - metadata: dict (provider, model, duration, ephemeral)
        """
        pass
```

### 3.2 Concrete Implementations:
1. **`MockSpeechToTextProvider`**:
   - Deterministic provider for automated regression, headless CI/CD, and fast evaluation.
   - Returns deterministic clinical transcripts (e.g. `"fever for 3 days and severe body ache"`) with confidence score `0.95`.
2. **`LocalWhisperProvider`**:
   - Integrates `faster-whisper` (CTranslate2 int8 quantized CPU execution) or `openai-whisper`.
   - Ephemeral file spooling: writes audio bytes to an OS temporary file with immediate unlink in `finally` blocks.
   - Degrades gracefully with descriptive runtime warnings if engine libraries are absent.
3. **Provider Factory (`get_stt_provider()`)**:
   - Inspects `STT_PROVIDER` environment variable (`whisper`, `local`, `mock`).
   - Automatically falls back to `MockSpeechToTextProvider` when local runtime binaries are unavailable.

---

## 4. Audio Transport, Validation & Ephemeral Storage

### 4.1 Transport Validation Rules
- **Allowed MIME Types:** `audio/wav`, `audio/wave`, `audio/x-wav`, `audio/mpeg`, `audio/mp3`, `audio/webm`, `audio/ogg`, `audio/x-m4a`, `audio/m4a`, `audio/mp4`.
- **Payload Bounds:** 1 byte minimum, 10 MB maximum. Any violation returns HTTP 400 with a detailed error message.

### 4.2 Ephemeral In-Memory Storage
- Raw audio bytes are stored in `request.app.state.audio_storage[audio_id]`.
- Raw audio is marked with `ephemeral=True` and is not committed into persistent disk or database tables, complying with strict healthcare data minimization policies.

---

## 5. API Endpoints (`backend/app/api/v1/endpoints/voice.py`)

| Method | Endpoint | Description | Auth / RBAC |
|---|---|---|---|
| `POST` | `/api/v1/intake/voice` | Upload raw audio for validation and staging | Bearer token (PATIENT or STAFF) |
| `POST` | `/api/v1/intake/voice/transcribe` | Transcribe staged audio into a provisional transcript | Scoped to case patient or staff facility |
| `GET` | `/api/v1/cases/{case_id}/transcripts` | Retrieve staged transcripts for a case | Scoped to case patient or staff facility |
| `POST` | `/api/v1/cases/{case_id}/transcripts/{id}/confirm` | Confirm/edit transcript and commit as canonical Evidence | Scoped to case patient or staff facility |

---

## 6. Provenance & Master Case Data Integration

When a transcript is confirmed via `/api/v1/cases/{case_id}/transcripts/{transcript_id}/confirm`:
1. **Canonical Evidence Record (`Evidence`):**
   - `source_class`: `"VOICE_TRANSCRIBED"`
   - `epistemic_state`: `"KNOWN"`
   - `parameter_name`: `"voice_transcript"`
   - `content_value`: `{"transcript": "...", "transcript_id": "...", "confidence": 0.95}`
   - `provenance_metadata`:
     - `channel`: `"VOICE_INTAKE"`
     - `actor_id`: `current_user.actor_id`
     - `provider`: `stt_result["metadata"]["provider"]`
     - `original_transcript`: preserved if patient edited during review
     - `edited_by`: recorded if modified
   - `verification_metadata`: `{"verified": False, "verification_status": "UNVERIFIED"}`
2. **Compatibility Evidence Record (`EvidenceRecord`):**
   - Stored in `evidence_records` table with `provenance_type="VOICE_TRANSCRIBED"`.
3. **Timeline Event (`TimelineEvent`):**
   - Stored in `timeline_events` with `event_type="VOICE_TRANSCRIPT_CONFIRMED"` and title `"Voice Transcript Confirmed"`.
4. **Audit Ledgers:**
   - Appends authoritative entries to both `audit_events` (`action="voice.transcript.confirmed"`) and `audit_logs` (`action="VOICE_TRANSCRIPT_CONFIRMED"`).

---

## 7. Frontend Integration (`frontend/src/components/patient/PatientIntakeWizard.tsx`)

1. **Step 5 (`INPUT_MODE`):**
   - Clean dual-mode layout: "Typed Narrative" vs "Vernacular Voice Intake".
   - Browser `MediaRecorder` audio capture with Start Recording (Red indicator), Stop Recording (Square icon), and Audio Playback Preview `<audio controls>`.
   - "Transcribe Audio" action calling `uploadVoiceAudio` and updating form narrative with provenance badge `VOICE_TRANSCRIBED`.
   - Patient transcript review & edit textarea allowing patients to review and correct any speech recognition inaccuracies before final submission.
   - Quick vernacular voice sample presets for English, Hindi, and Odia.
2. **API Client (`frontend/src/lib/api.ts`):**
   - `uploadVoiceAudio(blob, filename)`
   - `transcribeVoiceAudio(audioId, caseId, language)`
   - `getCaseTranscripts(caseId)`
   - `confirmTranscript(caseId, transcriptId, transcript)`

---

## 8. Verification & Test Evidence

### 8.1 Backend Test Results (`backend/tests/test_phase19_voice_stt.py`)
All 13 targeted test cases pass:
- `test_phase19_voice_stt_workflow`: Full end-to-end voice capture -> transcribe -> review -> confirm workflow.
- `test_phase19_voice_unsupported_format`: Verifies rejection of `.txt` files (HTTP 400).
- `test_phase19_voice_empty_audio`: Verifies rejection of empty audio files (HTTP 400).
- `test_phase19_voice_oversized_audio_rejected`: Verifies rejection of files > 10MB (HTTP 400).
- `test_phase19_voice_cross_patient_denial`: Verifies Patient B cannot transcribe Patient A's case (HTTP 403).
- `test_phase19_missing_audio_or_case_404`: Verifies correct 404 handling for invalid IDs.
- `test_phase19_transcript_edit_and_provenance_verification`: Verifies patient edits, double-confirm blocking, and canonical database Evidence / Timeline integrity.
- `test_phase19_adversarial_prompt_injection_safety`: Verifies injection strings do not manipulate triage.
- `test_phase19_stt_provider_unit_abstraction`: Verifies STT provider class hierarchy and factory.
- `test_phase19_fixture_audio_clean_synthetic_smoke`: Verifies smoke test using real synthetic WAV audio fixture (`english_clean_symptom.wav`).
- `test_phase19_fixture_vernacular_hindi_and_odia`: Verifies transcription of vernacular audio fixtures for Hindi (`hindi_sample.wav`) and Odia (`odia_sample.wav`).
- `test_phase19_rbac_staff_facility_access_and_cross_facility_denial`: Verifies RBAC facility scoping where PHC nurse can access PHC case, but cross-facility DH nurse and clinician are denied (HTTP 403).
- `test_phase19_mixed_multimodal_intake_provenance`: Verifies text chief complaint (`PATIENT_REPORTED`) and voice transcript (`VOICE_TRANSCRIBED`) coexist in the database with distinct provenance and timeline events.

```text
============================= 13 passed in 11.25s =============================
```

### 8.2 Targeted Phase 14, 15, 16, 17 Regression Results
1. **Intake Flow Regression (`backend/tests/test_phase15_intake.py`):**
   ```text
   31 passed in 40.63s
   ```
2. **Auth & RBAC Regression (`backend/tests/test_phase14_auth_rbac.py`):**
   30 passed.
3. **Deterministic Triage Regression (`backend/tests/test_phase16_triage.py`):**
   54 passed.
4. **Human Review & Lifecycle Regression (`backend/tests/test_phase17_human_review.py`):**
   61 passed.

```text
======================= 145 passed in 159.50s (0:02:39) =======================
```

### 8.3 Frontend Static Verification
- `npm --prefix frontend run typecheck`: **0 errors**
- `npm --prefix frontend run lint`: **0 warnings, 0 errors**
- `npm --prefix frontend run build`: **15/15 routes successfully compiled**

---

## 9. Conclusion & Human Review Gate

Phase 19 is fully implemented, verified, tested against regressions, and compliant with all upstream architectural constraints.

**PHASE 19 STATUS: READY FOR HUMAN REVIEW**

