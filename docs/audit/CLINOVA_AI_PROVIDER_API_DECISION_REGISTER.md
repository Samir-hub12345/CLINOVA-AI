# CLINOVA AI — PROVIDER & EXTERNAL API DECISION REGISTER

**Version:** 2.0  
**Phase:** Phase 2 Multimodal Ingestion  
**Enforcement:** Master Approval & Governance Rules (Strict Human-in-the-Loop)  
**Status:** ACTIVE AUDIT REGISTER — PHASE 2 VERIFIED  

---

## 1. Governance Principles & Approval Boundary

1. **Human Authority Always Comes First**: AI never diagnoses, prescribes, or makes autonomous clinical determinations.
2. **Backend-Only External Calling**: All third-party providers are invoked strictly server-side behind standardized Clinova provider interfaces.
3. **Zero Secret Exposure**: API keys never appear in frontend code, client bundles, git history, or application logs.
4. **₹0 Free-First Policy**: No automatic billing, no paid fallbacks without explicit project owner approval. `AI_EXTERNAL_ENABLED=False` by default; full pipeline functions with zero API cost via deterministic local fallbacks.
5. **Zero Real Patient Data**: Development and testing use synthetic clinical cases and fixtures only (`REAL_PATIENT_DATA_EXTERNAL_ALLOWED=False`).
6. **Abstraction Isolation**: The Canonical Patient Case engine never leaks provider-specific data structures or SDK types.
7. **Gemini Decommissioning**: Completed. `google-genai` SDK uninstalled, legacy Gemini client references excised, all endpoints migrated to designated Phase 2 provider adapters.

---

## 2. Designated Provider Profiles & Architecture

### A. Speech-to-Text (STT): Sarvam Saaras v4
- **Provider / Service**: Sarvam AI — Saaras v4 STT
- **Adapter**: `SarvamSaarasAdapter` (inherits `SpeechToTextProvider`)
- **Mode**: REST (`mode=transcribe`, max chunk duration $\le 30$s)
- **Supported Languages**: Hindi, Odia, Bengali, Tamil, Telugu, English + Code-mixed Indic
- **Script Handling**: Verbatim native Indic scripts preserved (Devanagari, Odia script, etc.)
- **Fallback**: `LocalSpeechToTextProvider` (deterministic regional script detector & mock)
- **Telemetry**: Records latency, provider name, and audio checksum in `MultimodalProcessingRecord`

### B. Optical Character Recognition (OCR): OCR.Space
- **Provider / Service**: OCR.Space Free API (Engine 2)
- **Adapter**: `OCRSpaceAdapter` (inherits `OCRProvider`)
- **Boundaries**: 1 MB payload limit, 3-page boundary limit, table parsing enabled (`isTable=True`)
- **Digital PDF Optimization**: Integrated `pdf_extractor` (local text extraction via `pypdf`/stream parsing) routes digital PDFs directly, bypassing external OCR if native text $\ge 40$ characters
- **Fallback**: `LocalOCRProvider` (deterministic CBC laboratory template matcher)

### C. Translation: Sarvam Mayura v1
- **Provider / Service**: Sarvam AI — Mayura v1 Translation Engine
- **Adapter**: `SarvamTranslationAdapter` (inherits `TranslationProvider`)
- **Chunking**: Sentence-aware chunking for payloads $> 1,000$ characters to stay within REST limits
- **Language Coverage**: Odia $\rightarrow$ English, Hindi $\rightarrow$ English, Bengali $\rightarrow$ English, etc.
- **Fallback**: `LocalTranslationProvider` (deterministic medical dictionary normalizer)

### D. Text-to-Speech (TTS): Sarvam Bulbul v3
- **Provider / Service**: Sarvam AI — Bulbul v3
- **Adapter**: `SarvamBulbulAdapter` (inherits `TextToSpeechProvider`)
- **Chunking**: Sentence-boundary chunking for payloads $> 2,500$ characters
- **Speakers**: Multilingual Indic voices (e.g. `meera`, `arvind`)
- **Fallback**: `LocalTextToSpeechProvider` (deterministic RIFF/WAV audio generator)

### E. Bounded Text Generation: Groq (`openai/gpt-oss-120b`)
- **Provider / Service**: Groq Cloud API (`openai/gpt-oss-120b`)
- **Adapter**: `GroqTextGenerationAdapter` (inherits `TextGenerationProvider`)
- **Role**: Strictly bounded extraction, formatting, and schema normalization with temperature $0.2$. Prohibited from autonomous clinical decision-making or prescribing.
- **Schema Validation**: Output rigorously parsed and validated against expected JSON schemas
- **Fallback**: `LocalTextGenerationProvider` (deterministic rule-based triage heuristic)

---

## 3. Capability Decision Register Matrix

| Capability | Phase 2 Component | Adapter Class | Designated Provider | Quota / Tier | Data Leaves Device? | Key Variable (Server-Side) | Ownership Tier | Status | Rationale & Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Speech-to-Text (STT)** | `speech_service.py` | `SarvamSaarasAdapter` | Sarvam Saaras v4 | Free credits / ₹0 default | Only if `AI_EXTERNAL_ENABLED=true` | `SARVAM_API_KEY` | O1 (Adapter) | **VERIFIED** | High accuracy across Indic languages & scripts. Fallback to `LocalSpeechToTextProvider`. |
| **Optical Character Recognition (OCR)** | `ocr_service.py` & `pdf_extractor.py` | `OCRSpaceAdapter` | OCR.Space Free API + Local Digital PDF Parser | Free tier (25k calls/mo) | Only if `AI_EXTERNAL_ENABLED=true` | `OCR_SPACE_API_KEY` | O1 (Adapter) | **VERIFIED** | Local extraction for native digital PDFs; OCR.Space for scanned pages $\le 3$ pages / 1 MB. |
| **Translation** | `translation_service.py` | `SarvamTranslationAdapter` | Sarvam Mayura v1 | Free credits / ₹0 default | Only if `AI_EXTERNAL_ENABLED=true` | `SARVAM_API_KEY` | O1 (Adapter) | **VERIFIED** | High quality Indic-to-English translation. Automatic sentence chunking $> 1,000$ chars. |
| **Text-to-Speech (TTS)** | `cases.py` (`/{case_id}/tts`) | `SarvamBulbulAdapter` | Sarvam Bulbul v3 | Free credits / ₹0 default | Only if `AI_EXTERNAL_ENABLED=true` | `SARVAM_API_KEY` | O1 (Adapter) | **VERIFIED** | Sentence chunking $> 2,500$ chars. Fallback generates valid playable WAV stream. |
| **Bounded Text Generation** | `gemini_service.py` / `cases.py` | `GroqTextGenerationAdapter` | Groq (`openai/gpt-oss-120b`) | Free tier (Groq Cloud) | Only if `AI_EXTERNAL_ENABLED=true` | `GROQ_API_KEY` | O1 (Adapter) | **VERIFIED** | Bounded schema extraction at temp 0.2. Strict JSON validation; non-diagnostic. |
| **Gemini Decommissioning** | Whole Backend | N/A | Decommissioned | Removed | No | `GEMINI_API_KEY` (Deprecated) | N/A | **DECOMMISSIONED** | `google-genai` uninstalled. Zero Gemini runtime dependencies remaining in `backend/app`. |

---

## 4. Normalized Error Classification Standard

All provider adapters strictly normalize upstream failures to the canonical error enumeration:
- `VALIDATION_ERROR`: Input payload fails format, size, or duration constraints.
- `AUTHENTICATION_ERROR`: Missing or invalid credentials.
- `AUTHORIZATION_ERROR`: Token lacks required scope.
- `RATE_LIMITED`: Provider throttle threshold exceeded.
- `QUOTA_EXHAUSTED`: Credit/token limit reached (fails safely without auto-billing).
- `TIMEOUT`: Gateway or inference timeout exceeded.
- `NETWORK_ERROR`: Connection dropped or DNS unreachable.
- `PROVIDER_UNAVAILABLE`: Upstream service 502/503 outage.
- `UNSUPPORTED_FORMAT`: File or codec unsupported.
- `PROCESSING_ERROR`: Unparseable or malformed provider output.
- `SAFETY_BLOCKED`: Provider safety filter triggered.
- `UNKNOWN_ERROR`: Unclassified runtime exception.

---

## 5. Approval & Verification Audit Log

- **Audit Date:** 2026-10-06  
- **Auditor:** Antigravity (Advanced Agentic Coding)  
- **Phase Gate Status:** **PASS** (17/17 Phase 2 tests passed, 96/96 full backend regression passed, 27/27 frontend tests passed, 0 TypeScript errors).  
- **Approved External Calling**: Gated behind `AI_EXTERNAL_ENABLED=False` and `REAL_PATIENT_DATA_EXTERNAL_ALLOWED=False`. Zero real patient data transmitted.  
