# CLINOVA AI — Ownership Decision Matrix
**Phase 0 Architecture Discovery**  
**Repository Commit:** `238f1eb917829642ca7525735d25f5882206247e` | **Branch:** `master`  
**Operating Rules:** 1–25 (Permanent Human Approval, Audit & Phase-Gate Master Prompt)

---

## 1. Ownership Level Definitions

Clinova AI defines a 5-tier ownership hierarchy to guarantee data sovereignty, intellectual property ownership, clinical safety, and rural offline autonomy:

```
[O4] Clinova Integrated Intelligence System
       └── [O3] Clinova Task-Specific Models (Custom Fine-Tuned SLMs / Weights)
             └── [O2] Clinova-Owned Algorithms (Deterministic Rules, Math, State Machines)
                   └── [O1] Clinova Integration Layer (Adapters, Sanitizers, Protocol Bridges)
                         └── [O0] External Provider Capabilities (Third-party Cloud APIs / Runtimes)
```

- **O0 — External Provider Capability:** Hosted multi-tenant third-party AI APIs (Google Gemini, OpenAI, Claude). Low ownership, high recurring operating cost, regulatory data transfer risks.
- **O1 — Clinova Integration Layer:** Proprietary interface adapters, error handlers, resilience fallbacks, and schema translators connecting Clinova services to AI backends.
- **O2 — Clinova-Owned Algorithm:** Fully proprietary, deterministic, reproducible algorithms (rules engines, regex sanitizers, clinical scoring trees, turn-taking state machines) executed locally in-process without weights or network calls.
- **O3 — Clinova Task-Specific Model:** Open-weights models (e.g. Llama 3.2 3B, IndicWhisper, PaddleOCR) fine-tuned on Clinova-curated datasets, hosted on-premise or within private clinical clusters.
- **O4 — Clinova Integrated Intelligence System:** The holistic orchestrator binding clinical workflows, human-in-the-loop validation, audit logging, RBAC permissioning, and decision aids into an institutional healthcare platform.

---

## 2. Capability Ownership & Decision Matrix

| Capability ID | Functional Area | Current Component & File | Current Ownership | Proposed Target Ownership | Phase-0 Decision | Technical Justification | Key Evaluated Factors (Privacy, Cost, Offline, Safety) |
|:---|:---|:---|:---:|:---:|:---:|:---|:---|
| **CAP-01** | Clinical Decision Support & Triage | `backend/app/services/ai/gemini_service.py` (`_call_gemini_triage`) | **O0** | **O3 / O2** | **PENDING BENCHMARK / REPLACE** | Cloud dependency prevents air-gapped rural clinic operations. Gemini free tier uses patient inputs for Google model training. Clinova's deterministic heuristic already works 100% offline. Recommendation: Benchmark a private on-premise SLM (e.g., Llama-3.2-3B or Meditron-7B) against Gemini 2.5 Flash, then replace cloud API. | **Privacy:** High risk on Free Tier.<br>**Cost:** $0.30/1M in, $2.50/1M out.<br>**Offline:** 0% (Cloud only).<br>**Safety:** AI outputs non-validated without doctor sign-off. |
| **CAP-02** | SOAP Clinical Note Synthesis | `backend/app/services/ai/gemini_service.py` (`_call_gemini_soap`) | **O0** | **O2 / O3** | **REPLACE** | **CRITICAL PRIVACY BREACH:** Code directly injects raw un-anonymized `req.patient_name` and full doctor clinical encounter notes into the Gemini prompt (`Line 120`). Must be immediately removed and replaced with Clinova's structured clinical template builder (O2) and an on-premise SLM (O3). | **Privacy:** Critical violation (Sends direct PII).<br>**Cost:** Scaled per OPD note.<br>**Offline:** Cloud only.<br>**Safety:** Risk of LLM clinical hallucination. |
| **CAP-03** | Multimodal Audio Speech-to-Text | `backend/app/services/speech_service.py` (`transcribe_audio`) | **O0** | **O3** | **REPLACE** | Gemini audio tokens are expensive ($1.00/1M tokens) and require high-bandwidth uploads of raw biometric audio waveforms. Unusable in bandwidth-constrained rural PHCs. Replace with an on-premise container running AI4Bharat IndicWhisper or Faster-Whisper. | **Privacy:** Voice biometrics transmitted externally.<br>**Cost:** $1.00/1M audio tokens.<br>**Offline:** 0% with Gemini.<br>**Safety:** Inaccurate transcripts could misdirect triage. |
| **CAP-04** | Multilingual Voice Assistant | `backend/app/services/ai/gemini_service.py` (`generate_voice_chat`) | **O0** | **O2** | **REMOVE / BUILD OURSELVES** | Currently crashes at runtime due to an `AttributeError` referencing undefined `settings.GEMINI_MODEL`. Furthermore, the deterministic conversational engine in `AssistantService` (O2) already delivers instant, multilingual, hallucination-free turn-taking with 0 latency, 0 token cost, and 100% patient privacy. | **Privacy:** User legal names sent to external API.<br>**Cost:** Recurring per conversational turn.<br>**Offline:** Broken cloud call.<br>**Safety:** Cloud conversational unpredictability. |
| **CAP-05** | Browser Speech Recognition | `frontend/src/lib/speech-recognition.ts`, `voice-recorder.tsx` | **O0** | **O0 + O3** | **KEEP (with Notice) + BUILD WASM** | Web Speech API is convenient and zero-install on Chrome/Edge, but routes audio to Google/Microsoft cloud. Keep for standard web demo with explicit privacy disclosure, but build an offline in-browser Whisper WASM fallback for air-gapped zero-cloud deployments. | **Privacy:** Vendor-managed audio cloud.<br>**Cost:** $0.00 client-side.<br>**Offline:** Partial (depends on OS speech packs).<br>**Safety:** Fallback to keyboard input provided. |
| **CAP-06** | Browser Text-to-Speech | `frontend/src/components/assistant/floating-assistant.tsx` | **O0** | **O0** | **KEEP** | Browser `window.speechSynthesis` runs 100% locally on the client device's OS voice engine. No network packets leave the device, zero token costs, and high responsiveness. | **Privacy:** 100% Local client audio synthesis.<br>**Cost:** $0.00.<br>**Offline:** 100% functional offline.<br>**Safety:** User controls volume and pause/cancel. |
| **CAP-07** | Deterministic Risk Engine | `backend/app/services/risk_engine.py` (`DeterministicRiskEngine`) | **O2** | **O2** | **KEEP & BUILD OURSELVES** | Rules `TRIAGE-R01` through `TRIAGE-R06` form the core clinical safety anchor of Clinova. 100% reproducible, fully explainable, zero latency, compliant with healthcare CDS standards. Expand with additional clinical guideline rules. | **Privacy:** 100% on-device local execution.<br>**Cost:** $0.00.<br>**Offline:** 100% offline capable.<br>**Safety:** Fully auditable clinical thresholds. |
| **CAP-08** | PII & Sensitive Identifier Anonymizer | `backend/app/services/anonymizer.py` (`AnonymizerService`) | **O2** | **O2** | **KEEP & BUILD OURSELVES (Enhance)** | Critical data sanitization layer. Removes Indian Aadhaar numbers, phone numbers, and emails. Must be enhanced to sanitize doctor notes and patient names in `ai_assist.py` before any potential external communication. | **Privacy:** Core privacy protection engine.<br>**Cost:** $0.00.<br>**Offline:** 100% offline capable.<br>**Safety:** Essential pre-flight filter. |
| **CAP-09** | Medical Report OCR Extraction | `backend/app/services/ocr_service.py` (`OCRService`) | **O1** | **O3 / O2** | **BUILD OURSELVES** | Current code is a synthetic stub returning hardcoded CBC values. Build out a real, local on-premise document pipeline using PaddleOCR or Tesseract with structured regex parsing to extract CBC, metabolic, and lipid panels. | **Privacy:** Lab report scans stay on-premise.<br>**Cost:** $0.00 compute on local CPU/GPU.<br>**Offline:** 100% local.<br>**Safety:** OCR confidence metrics + human verification. |
| **CAP-10** | Regional Language Normalization | `backend/app/services/translation_service.py` (`TranslationService`) | **O2** | **O2 / O3** | **BUILD OURSELVES / PENDING BENCHMARK** | Currently utilizes a static keyword dictionary for Odia and Hindi symptom phrases. Expand Clinova's clinical translation dictionary (O2) and benchmark against local open-source AI4Bharat IndicTrans2 container (O3). | **Privacy:** Symptoms normalized on-device.<br>**Cost:** $0.00.<br>**Offline:** 100% local.<br>**Safety:** Transparent verbatim original text preserved. |
| **CAP-11** | Bounded Assistant Security Gate | `backend/app/services/assistant_service.py` (`AssistantService`) | **O2** | **O2** | **KEEP & BUILD OURSELVES** | Proprietary Clinova security boundary. Enforces role-based tool execution, blocks prompt injections, prevents unauthorized autonomous medical prescriptions, and triggers human-in-the-loop confirmation gates. | **Privacy:** 100% local server-side policy.<br>**Cost:** $0.00.<br>**Offline:** 100% local.<br>**Safety:** Primary defense against agentic abuse. |

---

## 3. Human Decision & Infrastructure Layers

| Layer | Component | Current Implementation | Authority / Enforcement |
|:---|:---|:---|:---|
| **Human Decision** | Case Review & Approval | `backend/app/api/v1/endpoints/review.py` | Licensed Clinician / Medical Officer must verify and approve every AI triage suggestion before assignment or referral. |
| **Human Decision** | Doctor SOAP Finalization | `backend/app/api/v1/endpoints/consultations.py` | Attending Doctor must edit, sign, and lock SOAP notes before they are entered into the legal medical record. |
| **Human Decision** | Action Confirmation Gate | `backend/app/services/assistant_service.py` (`confirm_clinical_action`) | Assistant explicitly blocks autonomous execution of consequential actions until user confirms. |
| **Database** | Relational Data Store | PostgreSQL 16 (Production) / SQLite + aiosqlite (Demo) | Stores patients, encounters, cases, audit logs, and AI run records. |
| **Cache & Bus** | Telemetry & Cache | Redis 7 / Memurai (Windows) / In-Memory Fallback | Manages real-time queue states and telemetry. |
| **Object Store** | Medical Document Storage | `backend/app/services/storage.py` (`local_object_store`) | Local encrypted disk storage with SHA-256 integrity hashing and antivirus scanning. |
