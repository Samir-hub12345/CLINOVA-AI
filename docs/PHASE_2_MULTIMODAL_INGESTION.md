# CLINOVA AI — PHASE 2: MULTIMODAL INGESTION

**Product:** Clinova AI  
**Phase:** 2 of 10  
**Phase Name:** Multimodal Ingestion  
**Status:** IMPLEMENTED & VERIFIED  
**Previous Phase:** Phase 1 — Foundation  
**Next Phase:** Phase 3 — BUILD (Clinical Reasoning & Adaptive Triage)  

---

## 1. Overview & Objective

Phase 2 establishes the Multimodal Ingestion layer of Clinova AI. It enables the platform to safely receive, validate, normalize, and attach multimodal clinical patient inputs to the Canonical Patient Case without data flattening, information loss, or security compromise.

The multimodal inputs supported in this phase include:
1. **Patient Typed Text**: Verbatim symptom statements in English and regional languages.
2. **Patient Voice Audio**: Spoken audio recordings in WAV, WebM, MP3 format with native Indic script transcription (Hindi, Odia, English, Code-mixed).
3. **Medical Documents & Lab Reports**: Digital text PDFs, scanned PDFs, and medical images with OCR table parsing and local fallback templates.
4. **Multilingual Translation**: Seamless translation of Indic symptom descriptions into standardized English while preserving original statements and linkage.
5. **Text-to-Speech (TTS)**: Conversational audio synthesis for patient accessibility.

---

## 2. Architecture & Design Principles

### A. Provider Abstraction Boundary
All external services reside behind standardized abstract interfaces defined in `app/services/providers/base.py`:
- `SpeechToTextProvider`
- `OCRProvider`
- `TranslationProvider`
- `TextToSpeechProvider`
- `TextGenerationProvider`

Each provider interface implements strict error normalization via `ProviderError` and `ProviderErrorCode`, decoupling the application from vendor-specific SDKs and network protocols.

### B. Free-First Development Rule (₹0 Default)
- `AI_EXTERNAL_ENABLED=False` is set by default in application configuration.
- Every adapter includes a local deterministic fallback (`LocalSpeechToTextProvider`, `LocalOCRProvider`, `LocalTranslationProvider`, `LocalTextToSpeechProvider`, `LocalTextGenerationProvider`).
- Development and automated regression testing incur **zero API costs**.

### C. Source File & Raw Data Preservation
- When voice audio or documents are uploaded, the raw binary payload is saved in secure object storage via `storage_service` and recorded as source `CaseEvidence` *before* downstream AI processing.
- If STT or OCR fails, the source evidence remains permanently intact in the case graph for manual clinician review.
- Derived evidence explicitly references source evidence through `source_reference`.

### D. Security, Anti-Malware & IDOR Defense
- Document uploads undergo magic-byte MIME type verification (`storage.py`), rejecting spoofed executables (`MZ`, `ELF`, Mach-O) with HTTP 415.
- Path traversal sanitization protects storage paths.
- All endpoints enforce strict patient ownership checks (`_get_case_or_404`), returning HTTP 403 on cross-patient access attempts.

---

## 3. Designated Provider Stack

| Capability | Primary Adapter | Designated Provider | Fallback Provider | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **STT** | `SarvamSaarasAdapter` | Sarvam Saaras v4 | `LocalSpeechToTextProvider` | REST $\le 30$s, Indic scripts preserved verbatim (Devanagari, Odia) |
| **Digital PDF** | `LocalDigitalPDFParser` | Local stream parser | N/A | Local stream extraction (`BT ... ET`), bypasses external OCR |
| **OCR** | `OCRSpaceAdapter` | OCR.Space Free API | `LocalOCRProvider` | Engine 2, table parsing (`isTable=True`), 1MB & 3-page boundaries |
| **Translation** | `SarvamTranslationAdapter` | Sarvam Mayura v1 | `LocalTranslationProvider` | Sentence chunking $> 1,000$ chars, Indic $\rightarrow$ English |
| **TTS** | `SarvamBulbulAdapter` | Sarvam Bulbul v3 | `LocalTextToSpeechProvider` | Sentence chunking $> 2,500$ chars, streaming WAV output |
| **Bounded Text** | `GroqTextGenerationAdapter` | Groq `openai/gpt-oss-120b` | `LocalTextGenerationProvider` | Temperature 0.2, JSON schema validation, non-diagnostic |

---

## 4. API Endpoints

The following REST endpoints are implemented in `app/api/v1/endpoints/cases.py`:

- `POST /api/v1/cases/{case_id}/text`: Ingests patient typed symptoms and creates unverified evidence.
- `POST /api/v1/cases/{case_id}/audio`: Ingests audio, stores source file, transcribes via STT, and creates derived evidence.
- `POST /api/v1/cases/{case_id}/documents`: Ingests document/image, verifies MIME, extracts text via local PDF parser or OCR, and creates derived evidence.
- `POST /api/v1/cases/{case_id}/translate`: Translates text or existing evidence to English, preserving source reference.
- `POST /api/v1/cases/{case_id}/tts`: Synthesizes text into spoken audio stream.
- `GET /api/v1/cases/{case_id}/processing`: Retrieves multimodal processing jobs and execution telemetry.

---

## 5. Gemini Decommissioning

In accordance with Phase 2 instructions, legacy Gemini dependencies were decommissioned:
- Uninstalled `google-genai` SDK from `backend/requirements.txt`.
- Refactored `backend/app/services/speech_service.py` to use `SarvamSaarasAdapter`.
- Refactored `backend/app/services/ai/gemini_service.py` to use `GroqTextGenerationAdapter` and deterministic clinical heuristics.
- Confirmed zero `google.genai` imports or runtime calls across the backend codebase.

---

## 6. Verification & Test Results

- **Phase 2 Ingestion Suite** (`backend/tests/test_phase2_multimodal_ingestion.py`):
  - 17 of 17 tests passed (Cases 1–16 + Cross-Modal Demonstration).
- **Full Backend Regression Suite** (`backend/tests/`):
  - 96 of 96 tests passed (100% pass rate in 400.99s).
- **Frontend Test Suite** (`frontend/`):
  - 27 of 27 tests passed.
- **TypeScript Static Verification**:
  - 0 errors, 0 warnings.
