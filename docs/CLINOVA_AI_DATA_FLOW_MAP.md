# CLINOVA AI — AI Data Flow Map
**Phase 0 Architecture Discovery**  
**Repository Commit:** `238f1eb917829642ca7525735d25f5882206247e` | **Branch:** `master`  
**Operating Rules:** 4, 14, 20, 21 (External Data Transmission Gate & Safety-First Rules)

---

## 1. High-Level Data Flow Topology

Clinova AI processes medical intake across three primary operational modes:
1. **Zero-Cloud Local Mode (`GEMINI_API_KEY=""` or `OFFLINE_DEMO=True`):** 100% of data remains on the local host machine.
2. **Cloud-Assisted Prototype Mode (`GEMINI_API_KEY=configured`):** Specific reasoning and transcription tasks route out of the local server to Google Gemini API servers (`generativelanguage.googleapis.com`).
3. **Browser Web Speech Mode:** Real-time client microphone audio is processed directly by the client browser's vendor speech engine (Google or Microsoft).

```
                                      ┌────────────────────────────────────────────────────────┐
                                      │                     CLIENT BROWSER                     │
                                      │                                                        │
                                      │  [Patient / Clinician UI]                              │
                                      │           │                                            │
                                      │           ├── (Speech Mic) ──> [Web Speech API Cloud]  │
                                      │           │                   (Google / Microsoft)     │
                                      │           ▼                                            │
                                      │     [fetchApi / JSON]                                  │
                                      └───────────┬────────────────────────────────────────────┘
                                                  │ HTTPS / REST (Port 8000)
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FASTAPI SERVER (LOCAL)                                   │
│                                                                                              │
│   [Endpoints: /ai/triage, /ai/soap-summary, /assistant/message, /intake/speech, /cases]      │
│                                           │                                                  │
│                                           ▼                                                  │
│                         [Security & Anonymization Gate]                                      │
│                  - Prompt injection filtering (`assistant_service.py`)                       │
│                  - Aadhaar / Phone / Email regex redact (`anonymizer.py`)                    │
│                                           │                                                  │
│                    ┌──────────────────────┴──────────────────────┐                           │
│                    │                                             │                           │
│                    ▼ (Key Missing or Offline)                    ▼ (Key Configured)          │
│       ┌─────────────────────────┐                   ┌─────────────────────────┐              │
│       │ CLINOVA LOCAL HEURISTIC │                   │   GEMINI CLIENT ADAPTER │              │
│       │                         │                   │                         │              │
│       │ • DeterministicRiskEngine│                  │ • google-genai SDK      │              │
│       │ • _heuristic_triage     │                   │ • gemini-2.5-flash      │              │
│       │ • _heuristic_soap       │                   │ • Audio Part Upload     │              │
│       │ • Turn-Taking Dialog    │                   └────────────┬────────────┘              │
│       └────────────┬────────────┘                                │                           │
│                    │                                             │ Encrypted HTTPS Payload   │
│                    │                                             ▼                           │
│                    │                                ┌─────────────────────────┐              │
│                    │                                │   GOOGLE GEMINI CLOUD   │              │
│                    │                                │  generativelanguage.    │              │
│                    │                                │     googleapis.com      │              │
│                    │                                └────────────┬────────────┘              │
│                    │                                             │                           │
│                    │                                             │ Structured JSON Response  │
│                    │◄────────────────────────────────────────────┘                           │
│                    ▼                                                                         │
│   [Clinova Synthesis & Validation Engine]                                                    │
│   - Schema validation (Pydantic)                                                             │
│   - Urgency & Red Flag categorization                                                        │
│   - Non-diagnostic clinical disclaimer injection                                             │
│   - Audit Event persistence (`AuditService.log_event`)                                       │
│                    │                                                                         │
│                    ▼                                                                         │
│       [PostgreSQL / SQLite Database] ───> Return JSON to Frontend Client                     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Service-by-Service Data Pathways

### Pathway 1: Clinical Triage & Differential Diagnosis
- **Trigger:** Clinician clicks "Run AI Triage" in UI (`/patients` or `/consultations/[id]`).
- **Data Flow:**
  1. **Frontend:** `frontend/src/lib/api.ts` -> `apiClient.performAITriage(payload)`
  2. **Backend API:** `backend/app/api/v1/endpoints/ai_assist.py` -> `perform_clinical_triage(req: TriageRequest)`
  3. **Data Preprocessing:** **DEFECT IDENTIFIED:** No sanitization is performed on `req.chief_complaint`, `req.symptoms`, `req.relevant_medical_history`, or `req.known_allergies`.
  4. **Adapter Execution:** `backend/app/services/ai/gemini_service.py` -> `ai_service.analyze_triage(req)`
  5. **External Transmission:** If `GEMINI_API_KEY` is active:
     - **Destination:** Google Gemini API (`gemini-2.5-flash`)
     - **Data Leaves Device:** **YES (EXTERNAL)**
     - **Payload:** Chief complaint, symptoms, age, gender, medical history, known allergies, vitals JSON.
  6. **Local Fallback:** If `GEMINI_API_KEY` is blank or call fails:
     - **Destination:** **LOCAL ONLY** (`_heuristic_triage(req)`)
  7. **Persistence:** If linked to consultation, updates `triage_level`, `ai_differential_diagnosis`, and `ai_generated_summary` in `consultations` table. Logs to `audit_logs` table.
  8. **Frontend Consumer:** Renders colored urgency badge, differential table, and bedside recommendations.

---

### Pathway 2: Clinical SOAP Note Synthesis
- **Trigger:** Clinician clicks "Generate SOAP Draft" in consultation workspace.
- **Data Flow:**
  1. **Frontend:** `frontend/src/lib/api.ts` -> `apiClient.generateSOAPDraft(payload)`
  2. **Backend API:** `backend/app/api/v1/endpoints/ai_assist.py` -> `generate_soap_notes(req: SOAPGenerateRequest)`
  3. **Data Preprocessing:** **NONE.**
  4. **Adapter Execution:** `backend/app/services/ai/gemini_service.py` -> `ai_service.generate_soap_notes(req)`
  5. **External Transmission:** If `GEMINI_API_KEY` is active:
     - **Destination:** Google Gemini API (`gemini-2.5-flash`)
     - **Data Leaves Device:** **YES (EXTERNAL)**
     - **CRITICAL PRIVACY VIOLATION:** Line 120 formats `req.patient_name` directly into the prompt:
       ```python
       Patient: {req.patient_name} ({req.age_and_gender or 'Demographics unspecified'})
       Chief Complaint: {req.chief_complaint}
       Clinical Encounter Transcript / Notes: {req.encounter_notes}
       ```
       The patient's actual legal name, entire un-redacted doctor encounter notes, and medical history are sent to Google cloud servers.
  6. **Local Fallback:** `_heuristic_soap(req)` executes locally if offline or no key.
  7. **Persistence:** Doctor can inspect and edit the draft; upon saving, saved to `consultations.soap_notes`. Logs to `audit_logs`.
  8. **Frontend Consumer:** Editable SOAP note form in Doctor Consultation screen.

---

### Pathway 3: Floating Voice Assistant Chat
- **Trigger:** Patient or staff types or speaks a query into Floating Clinova Assistant.
- **Data Flow:**
  1. **Frontend:** `frontend/src/components/assistant/floating-assistant.tsx` -> POST `/api/v1/assistant/message`
  2. **Backend API:** `backend/app/api/v1/endpoints/assistant.py` -> `send_message(req)`
  3. **Security Preprocessing:**
     - Prompt injection detection regex (`assistant_service.py:150-162`).
     - Medical boundary enforcement (blocks autonomous diagnosis & prescription demands).
     - Emergency red flag keyword advisory.
  4. **Adapter Execution:** `assistant_service.py:435` calls `ai_service.generate_voice_chat(...)`
  5. **External Transmission Status:**
     - **INTENDED:** Transmit `user.full_name`, `user.role`, conversation history (6 turns), and query message to Gemini.
     - **ACTUAL RUNTIME BEHAVIOR:** **FAILS BEFORE TRANSMISSION.** Line 456 attempts to access `settings.GEMINI_MODEL`, which is not defined in `Settings`. Raises `AttributeError`, caught by L468 (`logger.warning`), and immediately falls back to Clinova's local deterministic turn-taking heuristic.
     - **Data Leaves Device:** **NO (Currently 100% LOCAL due to bug).**
  6. **Local Fallback Engine:** Purely local turn-taking heuristic (`assistant_service.py:455-520`) matches duration, severity, and medications, and generates empathetic follow-up probes.
  7. **Persistence:** Logs query in `audit_logs` if consequential or authenticated.
  8. **Frontend Consumer:** Floating Assistant chat window; spoken aloud via browser `speechSynthesis`.

---

### Pathway 4: Speech-to-Text Audio Upload
- **Trigger:** Audio file submitted to `/api/v1/intake/speech`.
- **Data Flow:**
  1. **Frontend:** `frontend/src/lib/api.ts` -> `transcribeSpeech(formData)`
  2. **Backend API:** `backend/app/api/v1/endpoints/intake.py` -> `process_speech_audio(file, language_hint)`
  3. **Adapter Execution:** `backend/app/services/speech_service.py` -> `speech_service.transcribe_audio(audio_bytes)`
  4. **External Transmission:**
     - If `GEMINI_API_KEY` is present and `OFFLINE_DEMO=False`:
       - **Destination:** Google Gemini API (`gemini-2.5-flash`)
       - **Data Leaves Device:** **YES (EXTERNAL)**
       - **Payload:** Raw audio recording bytes (biometric voice data) uploaded as `types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)`.
     - If key is blank or offline:
       - **Destination:** **LOCAL ONLY.** Returns structured response with empty transcript and message: `"Automated backend transcription requires an active AI service key. Please type symptoms manually or use browser speech recognition."`
  5. **Persistence:** Temporary in memory; final transcript saved in `triage_cases.speech_transcript` upon case submission.
  6. **Frontend Consumer:** Automatically populated into symptoms input field.

---

### Pathway 5: Case Intake Creation
- **Trigger:** Patient or triage receptionist clicks "Submit Case" on intake step 5.
- **Data Flow:**
  1. **Frontend:** `frontend/src/app/intake/page.tsx` -> POST `/api/v1/cases`
  2. **Backend API:** `backend/app/api/v1/endpoints/cases.py` -> `create_triage_case(req)`
  3. **Sanitization:** `anonymizer.sanitize_text(req.raw_symptoms)` strips Aadhaar numbers, phone numbers, emails (`cases.py:52`).
  4. **Local Synthesis:** Calls `ai_service.synthesize_triage_note(...)`
     - **NOTE:** Despite residing inside `gemini_service.py`, `synthesize_triage_note` **NEVER CALLS GEMINI**. It executes 100% locally using `risk_engine.evaluate(...)`, deterministic timeline generators, and heuristic missing information checkers.
  5. **Data Leaves Device:** **NO (100% LOCAL).**
  6. **Persistence:** Created record in `triage_cases` table. Logs `CASE_INTAKE_CREATED` in `audit_logs`.
  7. **Frontend Consumer:** Case receipt confirmation modal with synthetic case ID.

---

### Pathway 6: Medical Report Lab OCR
- **Trigger:** User attaches lab report image/PDF on intake step 4.
- **Data Flow:**
  1. **Frontend:** `frontend/src/components/clinical/report-uploader.tsx` -> POST `/api/v1/intake/ocr`
  2. **Backend API:** `backend/app/api/v1/endpoints/intake.py` -> `process_medical_report(file)`
  3. **Execution:** `ocr_service.process_report(file_bytes)`
  4. **Data Leaves Device:** **NO (100% LOCAL).**
  5. **Processing:** Returns hardcoded synthetic Complete Blood Count (CBC) panel with verification status `"pending"`.
  6. **Persistence:** Persisted in `triage_cases.report_ocr_data` as JSON upon case creation.
  7. **Frontend Consumer:** Editable OCR table showing Hb, WBC, Platelets, and RBC with confidence badges.

---

### Pathway 7: Multilingual Normalization & Translation
- **Trigger:** Intake language switched to Odia or Hindi.
- **Data Flow:**
  1. **Frontend:** `frontend/src/app/intake/page.tsx` -> POST `/api/v1/intake/translate`
  2. **Backend API:** `backend/app/api/v1/endpoints/intake.py` -> `normalize_regional_text(input_data)`
  3. **Execution:** `translation_service.translate_and_normalize(text, source_language)`
  4. **Data Leaves Device:** **NO (100% LOCAL).**
  5. **Processing:** Uses in-memory `DEMO_TRANSLATIONS` dictionary to normalize Odia/Hindi symptoms to English clinical summaries while preserving verbatim text.
  6. **Persistence:** Saved in `triage_cases.normalized_symptoms`.
  7. **Frontend Consumer:** Displays bilingual view (original regional text alongside English clinical normalization).

---

## 3. Data Movement Classification Summary

| Pathway / Capability | Data Classification | Leaves Device? | Patient Identifiers Transmitted? | Biometrics Transmitted? | External Endpoint |
|:---|:---:|:---:|:---:|:---:|:---|
| **AI Triage (`/ai/triage`)** | **EXTERNAL** (when key set) | Yes | Risk: Unsanitized chief complaint / history | No | `generativelanguage.googleapis.com` |
| **SOAP Notes (`/ai/soap-summary`)** | **EXTERNAL** (when key set) | Yes | **CRITICAL: Direct Patient Name & Clinical Notes** | No | `generativelanguage.googleapis.com` |
| **Speech STT (`/intake/speech`)** | **EXTERNAL** (when key set) | Yes | Indirect (in speech audio) | **CRITICAL: Raw Voice Audio Waves** | `generativelanguage.googleapis.com` |
| **Voice Chat (`/assistant/message`)** | **LOCAL** (Due to bug) | No | Intended User Name (Blocked by bug) | No | N/A (Fails to local) |
| **Case Intake (`/cases`)** | **LOCAL** | No | Stripped by `anonymizer.py` | No | None (Server memory/DB) |
| **Lab OCR (`/intake/ocr`)** | **LOCAL** | No | None (Synthetic mock) | No | None (Server memory) |
| **Translation (`/intake/translate`)** | **LOCAL** | No | None | No | None (Server memory) |
| **Browser Web Speech API** | **EXTERNAL** (Vendor Cloud) | Yes | Voice audio captured by browser | **Raw Voice Audio to Google/MS** | Browser Vendor Speech Engine |

---

## 4. Untrusted Input & Injection Defense Verification

In compliance with Permanent Operating Rule 21 (*Safety-First Development Rule*):

1. **Document & Text Content as Untrusted Data:**
   - Text inputs from `raw_symptoms`, `speech_transcript`, and `encounter_notes` are treated as untrusted strings.
   - Pydantic models validate string lengths (`min_length`, `max_length`), preventing buffer and payload exhaustion attacks.

2. **Prompt Injection Defense in Assistant:**
   - `AssistantService.process_message` implements regex filters against system instruction override, SQL injection keywords, and credential probing (`assistant_service.py:150-178`).
   - Requests matching injection patterns are met with an immediate structured refusal (`"Safety Policy (Refusal)"`).

3. **Autonomous Clinical Guardrails:**
   - Assistant explicitly refuses direct diagnosis requests (`"cannot provide a personal medical diagnosis"`) and prescription requests (`"cannot prescribe medications"`).
   - High-impact consequential actions (case approval, referral escalation) are intercepted by a mandatory confirmation gate (`requires_confirmation=True`).
