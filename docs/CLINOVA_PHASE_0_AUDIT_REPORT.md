# CLINOVA AI — Phase 0 Audit Report
**External API & Model Inventory + Ownership Discovery**  
**Repository Commit:** `238f1eb917829642ca7525735d25f5882206247e` | **Branch:** `master`  
**Date of Audit:** October 2026 | **Operating Rule:** Read-Only Inventory Gate (Rules 1–25)

---

## 1. Phase 0 Real-Time Progress Table

In strict compliance with Operating Rule 15 (*Real-Time Progress Display*), below is the actual audited status of every Phase 0 task:

| Phase 0 Milestone | Actual State | Evidence / Artifact |
|:---|:---:|:---|
| Repository & Dependency Audit | ✅ COMPLETE | Manifests inspected: `backend/requirements.txt`, `frontend/package.json` |
| Provider Discovery | ✅ COMPLETE | Discovered: Google Gemini API (`google-genai`), Browser Web Speech API |
| Model Discovery | ✅ COMPLETE | Discovered: `gemini-2.5-flash`, missing `settings.GEMINI_MODEL`, synthetic mocks |
| Data-Flow Mapping | ✅ COMPLETE | Mapped 8 pathways in `docs/CLINOVA_AI_DATA_FLOW_MAP.md` |
| Pricing & Quota Review | ✅ COMPLETE | Grounded in official docs: `docs/CLINOVA_PROVIDER_RISK_COST_MATRIX.md` |
| Privacy & Regulatory Review | ✅ COMPLETE | Free tier data use identified, direct PII leak flagged in SOAP synthesis |
| Security & Secret Audit | ✅ COMPLETE | Safe: Keys loaded server-side only; Git history clean of API keys |
| Ownership Classification | ✅ COMPLETE | Categorized O0 to O4 in `docs/CLINOVA_OWNERSHIP_DECISION_MATRIX.md` |
| KEEP / REPLACE / BUILD Decisions | ✅ COMPLETE | 11 capability decisions recorded in `docs/CLINOVA_EXTERNAL_API_MODEL_INVENTORY.md` |
| Phase-0 Reports Generated | ✅ COMPLETE | 5 required documents created in `docs/` |
| User Approval & Phase Gate | 🟡 NEEDS USER DECISION | Awaiting explicit project owner sign-off before any Phase 1 action |

---

## 2. Technical Findings Summary (Sections A – P)

### A. All External APIs Currently Used
1. **Google Gemini API:**
   - **Endpoints Called:** `client.models.generate_content` and `client.aio.models.generate_content` via official `google-genai` Python SDK.
   - **Host:** `https://generativelanguage.googleapis.com`
   - **Code Locations:** `backend/app/services/ai/gemini_service.py` (L91, L136, L455), `backend/app/services/speech_service.py` (L80).
2. **Browser Web Speech API (Client-side):**
   - **Endpoints Called:** `window.SpeechRecognition` / `window.webkitSpeechRecognition` (streams microphone audio to Google/Microsoft speech servers).
   - **Code Locations:** `frontend/src/lib/speech-recognition.ts` (L29-32), `frontend/src/components/clinical/voice-recorder.tsx` (L148-180), `frontend/src/components/assistant/floating-assistant.tsx` (L703-750).

---

### B. All Models Currently Used
1. **`gemini-2.5-flash`:**
   - Used for Clinical Triage decision support (`gemini_service.py:92`).
   - Used for SOAP clinical note synthesis (`gemini_service.py:137`).
   - Used for Multimodal audio speech-to-text transcription (`speech_service.py:81`).
2. **`settings.GEMINI_MODEL` (Bug):**
   - Referenced in voice chat (`gemini_service.py:456`), but missing in `Settings` class (`AttributeError`).
3. **Deterministic Clinical Heuristic Models:**
   - `_heuristic_triage`: Rule-based emergency physiological threshold evaluation (`gemini_service.py:154-281`).
   - `_heuristic_soap`: Structured medical SOAP template synthesizer (`gemini_service.py:283-314`).
   - `DeterministicRiskEngine`: Rules `TRIAGE-R01` through `TRIAGE-R06` (`risk_engine.py:12-103`).
4. **Synthetic Lab Model:**
   - `SYNTHETIC_CBC_FIELDS`: Static complete blood count mock generator (`ocr_service.py:11-48`).
5. **Static Translation Model:**
   - `DEMO_TRANSLATIONS`: Dictionary-based Odia/Hindi clinical normalizer (`translation_service.py:11-28`).

---

### C. All Unused / Phantom AI Dependencies
The following dependencies are documented in project architecture or configuration settings but have **zero actual code execution**:
1. **`openai`:** Mentioned in docs (`ARCHITECTURE.md:82`, `CHANGELOG.md:25`); not installed, not in requirements.txt.
2. **`faster-whisper`:** Defined as configuration default (`STT_PROVIDER=faster-whisper` in `config.py:54`); not installed, ignored in code.
3. **`paddleocr`:** Defined in config (`OCR_PROVIDER=paddleocr` in `config.py:55`); not installed, ignored in code.
4. **`indictrans2`:** Defined in config (`TRANSLATION_PROVIDER=indictrans2` in `config.py:56`); not installed, ignored in code.
5. **`pytesseract` / `Tesseract`:** Mentioned in docs; not installed, ignored in code.
6. **`transformers` / `huggingface`:** Mentioned in roadmap; not installed.

---

### D. All External Data Flows
1. **Triage Inference (`/api/v1/ai/triage`):** Transmits patient symptoms, chief complaint, age, gender, medical history, allergies, and vitals to Google cloud servers when `GEMINI_API_KEY` is present.
2. **SOAP Note Synthesis (`/api/v1/ai/soap-summary`):** Transmits **patient full legal name**, doctor encounter notes, vitals, and medical history to Google cloud servers when `GEMINI_API_KEY` is present.
3. **Speech-to-Text Upload (`/api/v1/intake/speech`):** Transmits **raw patient voice audio bytes** to Google cloud servers when `GEMINI_API_KEY` is present.
4. **Client-side Speech Recognition (`VoiceRecorder` & `FloatingAssistant`):** Streams client microphone audio to Google/Microsoft speech servers via browser Web Speech API.

---

### E. All Local AI Components
1. **`DeterministicRiskEngine` (`backend/app/services/risk_engine.py`):** 100% local rule-based urgency classifier.
2. **`AnonymizerService` (`backend/app/services/anonymizer.py`):** 100% local regex de-identifier for Indian Aadhaar numbers, phone numbers, and emails.
3. **`synthesize_triage_note` (`backend/app/services/ai/gemini_service.py:316-401`):** 100% local synthesis pipeline despite residing in `gemini_service.py`.
4. **`_heuristic_triage` & `_heuristic_soap`:** 100% local deterministic fallback engines.
5. **`AssistantService` conversational turn-taking engine (`assistant_service.py:455-520`):** 100% local dialog state machine.
6. **`TranslationService` (`backend/app/services/translation_service.py`):** 100% local keyword dictionary.
7. **`OCRService` (`backend/app/services/ocr_service.py`):** 100% local synthetic lab panel generator.
8. **Browser Speech Synthesis (`speechSynthesis`):** 100% local audio playback via client OS voices.

---

### F. All Current AI Security & Privacy Risks
1. **CRITICAL PRIVACY VIOLATION — Direct PII Leak in SOAP Generator:**
   - In `backend/app/services/ai/gemini_service.py:120`:
     ```python
     Patient: {req.patient_name} ({req.age_and_gender or 'Demographics unspecified'})
     Chief Complaint: {req.chief_complaint}
     Clinical Encounter Transcript / Notes:
     {req.encounter_notes}
     ```
   - Un-redacted patient names and raw doctor notes are sent directly to external Google servers.
2. **CRITICAL REGULATORY RISK — Free Tier Data Training:**
   - Under Google's official API terms, prompts and responses on the **Free Tier are used to train Google products and may be reviewed by human contractors**. Using a free key violates healthcare confidentiality (HIPAA, Indian Digital Personal Data Protection Act 2023, DISHA).
3. **HIGH PRIVACY RISK — Biometric Audio Waveform Transmission:**
   - `speech_service.py:80-86` uploads raw voice audio bytes to external Google endpoints.
4. **HIGH RELIABILITY DEFECT — Runtime Crash on Missing Config Attribute:**
   - `gemini_service.py:456` references `settings.GEMINI_MODEL`, which does not exist in `Settings` class (`config.py`). Whenever voice chat is invoked with an active client, it throws an `AttributeError`.
5. **HIGH INTEGRATION GAP — Unused `AIRun` Audit Persistence:**
   - `backend/app/models/ai_run.py` defines a comprehensive table schema (`AIRun`, `AIRunStatus`, `AIReviewStatus`), but `ai_assist.py` never instantiates or saves `AIRun` records. AI inferences are not tracked in the dedicated AI ledger.

---

### G. All Current AI Cost Risks
1. **Audio Token Ingestion Surcharge:**
   - Audio input tokens on Gemini 2.5 Flash are billed at **$1.00 / 1M tokens** (over 3.3x more expensive than text at $0.30 / 1M). High audio volume in rural clinics creates unexpected spend spikes.
2. **Rolling 10-Minute Spend Cap Lockout:**
   - On Google Tier 1 accounts, exceeding **$10 within a 10-minute rolling window** results in immediate `429 RESOURCE_EXHAUSTED` errors across the hospital.
3. **Projected District Hospital Cost:**
   - An OPD handling 10,000 encounters/day incurs ~$14,311 / year in external cloud token costs, compared to ~$2,200 one-time capex for a dedicated on-premise GPU workstation.

---

### H. All Local Replacement Candidates
1. **Clinical Triage:** Quantized Small Language Models (Llama 3.2 3B-Instruct, BioMistral 7B, Meditron-7B) hosted on local Ollama, vLLM, or llama.cpp runtimes (4-8 GB VRAM).
2. **SOAP Clinical Note Generation:** Clinova Deterministic Structured Template Builder or local 3B SLM fine-tuned on clinical encounter structures.
3. **Speech-to-Text:** AI4Bharat IndicWhisper (state-of-the-art for Odia and Hindi) or Faster-Whisper (small-int8 / medium) running in a local container; Whisper WASM running in the client browser.
4. **Lab Report OCR:** Local PaddleOCR or Tesseract OCR running on local CPU/GPU.
5. **Regional Translation:** AI4Bharat IndicTrans2-1B or expanded Clinova clinical terminology synonym maps.

---

### I. All Clinova-Owned Algorithm Candidates (O2)
1. **`DeterministicRiskEngine`:** Expand emergency keyword and physiological threshold rules from `TRIAGE-R01`–`R06` to a comprehensive 50-rule clinical safety matrix.
2. **`AnonymizerService`:** Expand regex sanitization to remove patient names, doctor names, hospital names, dates of birth, and Indian PIN codes before any model inference.
3. **Structured Clinical Note Builder:** Deterministic translation of structured encounter fields (symptoms, vitals, physical exam, diagnosis) into standard SOAP sections without LLM hallucinations.
4. **Conversational Turn-Taking State Machine:** Enhance `AssistantService` dialog heuristics to manage multi-step patient intake without external cloud calls.

---

### J. All Clinova Model Candidates (O3)
1. **Clinova Indic-Triage-3B:** Llama 3.2 3B quantized (Q4_K_M) fine-tuned on open, de-identified clinical triage protocols.
2. **Clinova Indic-Speech-Whisper:** AI4Bharat IndicWhisper container specialized for rural Odia, Hindi, and English medical acoustic speech.
3. **Clinova Prescript-OCR:** PaddleOCR fine-tuned on handwritten OPD doctor slips and standard pathology lab formats.

---

### K. KEEP Decisions
1. **`DeterministicRiskEngine` (O2):** 100% Clinova-owned, explainable, transparent, offline.
2. **`AnonymizerService` (O2):** Essential data protection algorithm (requires enhancement).
3. **`AssistantService` Security & RBAC Gate (O2):** Strict prompt injection defense and role allowlists.
4. **Browser `speechSynthesis` (O0):** Zero-cost, 100% local client voice playback.

---

### L. REPLACE Decisions
1. **Google Gemini 2.5 Flash SOAP Generator (`_call_gemini_soap`):** Replace immediately due to direct PII leakage and high hallucination risk.
2. **Google Gemini 2.5 Flash Audio Transcription (`speech_service.py`):** Replace with on-premise AI4Bharat IndicWhisper / Faster-Whisper.

---

### M. BUILD Decisions
1. **Clinova On-Premise Document OCR Engine:** Replace synthetic mock with local PaddleOCR / Tesseract pipeline.
2. **Clinova Comprehensive Medical Synonym & Translation Map:** Replace static dictionary with exhaustive medical terminology normalization.
3. **Client-Side Offline Whisper WASM:** Build browser-based local speech recognition fallback.

---

### N. TRAIN Decisions
1. **None in Phase 0.** (Training models or downloading training data in Phase 0 is strictly forbidden by Operating Rule 8 & 15).
2. **Proposed for Phase 1 / Phase 2 (Subject to Project Owner Approval):**
   - Fine-tune Llama 3.2 3B on synthetic clinical triage benchmarks.
   - Fine-tune PaddleOCR on public de-identified prescription slips.

---

### O. REMOVE Decisions
1. **`generate_voice_chat` external Gemini call (`gemini_service.py:402-471`):** Remove broken cloud call that crashes on `settings.GEMINI_MODEL` and transmits user names to Google; rely on Clinova's local conversational state machine.
2. **Unused configuration stubs:** Clean up phantom configuration references in Phase 1 if approved.

---

### P. Unknown / Blocker Items
1. **`settings.GEMINI_MODEL` Runtime Bug:** Calling `ai_service.generate_voice_chat` fails with `AttributeError`. Blocks live Gemini voice chat if client is initialized.
2. **AIRun Ledger Inactive:** Model inferences in `ai_assist.py` do not create rows in the `ai_runs` table despite the schema being present.
3. **Client-Side Web Speech Privacy Disclosure:** Frontend users are not currently warned that clicking the microphone button routes voice audio through Google/Microsoft cloud services.

---

## 3. Verified Verification Command Outputs

### Test Suite Execution (Offline AI & Speech Tests)
```
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\admin\CLIVORA-AI\backend
configfile: pytest.ini
plugins: anyio-4.15.1, asyncio-1.4.0

backend\tests\test_ai.py ..                                              [ 40%]
backend\tests\test_speech_service.py ...                                 [100%]
============================= 5 passed in 17.64s ==============================
```

### Assistant Security & Multi-Turn Suite Execution
```
backend\tests\test_assistant.py .....                                    [100%]
============================= 5 passed in 15.45s ==============================
```

### Git Secret & History Verification
```
git log -S "AIzaSy" --oneline -> 0 commits found (Clean)
git log --all --full-history -- ".env" -> 0 commits found (Clean)
git log --all --full-history -- "frontend/.env.local" -> 0 commits found (Clean)
```

---

## 4. Phase-Gate Stop Condition

In strict accordance with Operating Rule 17 (*Phase Completion Gate*) and Rule 24 (*Permanent Stop Rule*):

- [x] Every AI dependency identified
- [x] Every provider identified
- [x] Every model identified
- [x] Every AI call traced
- [x] Every environment variable identified by NAME only
- [x] Data flows mapped
- [x] External/local status known
- [x] Provider policy checked
- [x] Cost/limits checked
- [x] Local alternatives checked
- [x] Ownership classification complete
- [x] KEEP/REPLACE/BUILD/TRAIN/REMOVE decisions complete
- [x] Security audit complete
- [x] No secrets exposed
- [x] No patient data transmitted
- [x] No training performed
- [x] Phase-0 reports completed

**PHASE 0 AUDIT IS TECHNICALLY COMPLETE. AWAITING EXPLICIT USER DECISION BEFORE PROCEEDING TO PHASE 1.**
