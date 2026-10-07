# CLINOVA AI — AI Model Strategy & Safety Contract

> **Document ID:** `DOC-20`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Zero-Cost / Open-Source Model Strategy

CLINOVA AI is architected from the ground up to operate with zero dependency on expensive, proprietary cloud AI APIs (e.g., OpenAI, Google Gemini, Anthropic).

### 1.1 Development Base Model
- **Base Model Candidate:** **Qwen3-4B** (or Llama-3.2-3B / BioMistral-7B) running in a **local runtime** (via Ollama, llama.cpp, or HuggingFace Transformers).
- **Naming Invariant:** In Phase 1 and the development prototype, this model must strictly be referred to as the **"Open-Source Development Base Model"** or **"Local SLM Runtime"**. It must **NEVER** be marketed or described as a *"clinically validated CLINOVA proprietary medical foundation model"*.
- **Development Pipeline:**
  $$\mathbf{Qwen3\text{-}4B} + \mathbf{Structured\ Clinical\ Prompts} + \mathbf{Strict\ JSON\ Schemas} + \mathbf{Deterministic\ Clinical\ Rules} + \mathbf{CAREGRAPH\ Context}$$

### 1.2 Future Model Development & Fine-Tuning Contract
Model training and fine-tuning do **NOT** take place in Phase 1. Phase 1 defines the architectural contract for future post-hackathon model training:

```
[ BASE SLM: Qwen3-4B ]
       │
       ▼
[ SYNTHETIC CLINOVA DATASET ] ──> Multi-dialect Indian clinical triage vignettes
       │
       ▼
[ BENCHMARK EVALUATION & ERROR AUDIT ] ──> Measure extraction accuracy & safety
       │
       ▼
[ LoRA / PEFT ADAPTER TRAINING ] ──> Train low-rank adapters on structured clinical tasks
       │
       ▼
[ POST-TRAINING CLINICAL EVALUATION ] ──> Verify absence of catastrophic hallucinations
       │
       ▼
[ CLINOVA-SPECIFIC MODEL CANDIDATE ]
```

### 1.3 Anti-Single-Point-of-Failure Law
The application is designed so that the local AI model is **never a single point of failure**. If the local SLM runtime is stopped, out of memory, or crashes, the system automatically falls back to:
- Deterministic clinical heuristic rules (MEWS calculation, shock index, red-flag regexes).
- Structured template synthesis for clinical notes.
- Rule-based missing data checklists.
The clinical workflow remains 100% operational in offline/fallback mode.

---

## 2. The AI Safety Contract (Permitted vs. Forbidden Behaviors)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLINOVA AI SAFETY CONTRACT                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT AI IS PERMITTED TO DO               WHAT AI IS STRICTLY FORBIDDEN    │
│   (Advisory & Structuring Scope)           FROM DOING (Non-Negotiable)      │
│   ──────────────────────────────────       ───────────────────────────────  │
│   ✅ Extract entities from text/voice/OCR   ❌ NEVER autonomously diagnose    │
│   ✅ Normalize vernacular to clinical terms ❌ NEVER prescribe medications    │
│   ✅ Summarize longitudinal timelines       ❌ NEVER replace a human doctor   │
│   ✅ Identify missing critical qualifiers   ❌ NEVER override a clinician     │
│   ✅ Generate candidate follow-up questions ❌ NEVER invent/hallucinate facts │
│   ✅ Highlight clinical urgency signals     ❌ NEVER fabricate lab evidence   │
│   ✅ Draft structured triage notes for MD   ❌ NEVER hide data uncertainty    │
│   ✅ Recommend safest achievable pathways   ❌ NEVER present AI as verified   │
│                                            ❌ NEVER claim clinical validation │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Permitted Behaviors (`AI_PERMITTED`)
1. **Extraction:** Parse unstructured text, audio transcripts, and OCR text to extract clinical entities (symptoms, durations, medications).
2. **Normalization:** Map regional and colloquial terms (e.g., *"chhati re jantrana"*, *"chhati mein dard"*) into standardized medical terms (e.g., *"acute central chest pain"*).
3. **Summarization:** Condense multi-page records into chronological timelines and structured triage note drafts.
4. **Gap Identification:** Detect missing critical parameters required by clinical triage protocols.
5. **Question Generation:** Propose 1–3 focused clarification questions for patient or nurse review.
6. **Prioritization Support:** Calculate objective risk indicators (shock index, MEWS) to inform queue sorting.
7. **Action Recommendation:** Suggest candidate actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`) for clinician consideration.

### 2.2 Strictly Forbidden Behaviors (`AI_FORBIDDEN`)
1. **NO Autonomous Diagnosis:** AI must never issue a binding diagnostic pronouncement (e.g., stating *"You have Dengue Shock Syndrome"*). It may only describe syndromes and physiological risk bands (e.g., *"High-risk acute febrile illness with thrombocytopenia"*).
2. **NO Prescription:** AI must never specify drug dosages, write prescriptions, or order invasive procedures autonomously.
3. **NO Clinician Replacement:** AI must never discharge, admit, or transfer a patient without a licensed human medical officer's digital sign-off.
4. **NO Clinician Override:** AI cannot prevent a doctor from overriding any system recommendation or changing any clinical field.
5. **NO Hallucination or Data Fabrication:** When data is absent, AI must label it `UNKNOWN`. It is strictly forbidden from imputing normal values (e.g., assuming normal blood pressure when unmeasured).
6. **NO Obscured Uncertainty:** AI must never conceal evidence gaps, low confidence scores, or contradictory findings behind false certainty metrics.
7. **NO False Verification Claims:** AI output must always be badged as `AI_INFERRED`; it must never masquerade as `CLINICIAN_VERIFIED`.
