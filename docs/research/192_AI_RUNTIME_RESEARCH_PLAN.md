# CLINOVA AI — AI Runtime Research & Execution Plan

> **Document ID:** `RES-192`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Architecture, Clinical Safety Informatics & Local Runtime Group  

---

## 1. Executive Summary & Atomic Phase Rule

In strict accordance with the **Atomic Phase Rule**, Phase 10 establishes the **authoritative LOCAL AI runtime foundation and safe inference architecture** for CLINOVA AI.

```
================================================================================
ATOMIC PHASE BOUNDARY RULE — PHASE 10 ONLY
================================================================================
Do NOT execute Phase 11 or any later phase.
Do NOT implement live patient intake workflows.
Do NOT implement live voice intake.
Do NOT implement live OCR workflows.
Do NOT implement doctor queues.
Do NOT implement CAREGRAPH UI, FACILITYGRAPH UI, or ORCHESTRATION UI.
Do NOT implement production clinical features.
Do NOT execute database migrations.
Do NOT deploy services.

Phase 10 establishes the AI RUNTIME FOUNDATION.
It defines and validates the runtime architecture and creates isolated non-production
runtime scaffolding ONLY under backend/app/ai_runtime/ and backend/tests/ai_runtime/.
Do NOT integrate the runtime into production patient workflows yet.
================================================================================
```

---

## 2. Research & Architectural Objectives

The primary objective of Phase 10 is to decouple clinical application logic from probabilistic generative models while providing a modular, local-first runtime foundation. The local AI runtime must support future:
1. **Narrative Understanding:** Parsing unstructured colloquial medical descriptions.
2. **Structured Extraction:** Extracting symptoms, vitals, reported medications, and allergies.
3. **Summarization:** Synthesizing clinical timelines while preserving epistemic uncertainty.
4. **Follow-up Question Generation:** Formulating Value-of-Information (VOI) clarification questions.
5. **Translation:** Translating regional vernacular narratives (Odia, Hindi) to English.
6. **Normalization:** Mapping colloquial terms to standard terminologies (SNOMED-CT, LOINC).
7. **Note Drafting:** Drafting non-diagnostic SOAP progress notes for physician review.
8. **Advisory Reasoning:** Surfacing candidate differential considerations and safety reminders.

---

## 3. The Core AI Runtime Principle

$$\mathbf{The\ LLM\ is\ a\ COMPONENT.\ It\ is\ NOT\ the\ CLINOVA\ Brain.}$$

Generative models are treated as **untrusted, external perceptual adapters**. Under no operational, emergency, or network circumstance does a generative model make an autonomous clinical decision.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CANONICAL CLINICAL INFERENCE PIPELINE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   UNTRUSTED INPUT                                                           │
│   (Patient Voice, Text, OCR)                                                │
│          │                                                                  │
│          ▼                                                                  │
│   CONTENT SANITIZATION & DELIMITED CONTEXT PACK                             │
│   (Delimited passive data; injection attacks stripped and escaped)          │
│          │                                                                  │
│          ▼                                                                  │
│   LOCAL MODEL INFERENCE (Qwen Open-Weight SLM)                              │
│   (llama.cpp / Ollama on CPU/GPU; zero external API calls; zero fees)       │
│          │                                                                  │
│          ▼                                                                  │
│   STRUCTURED OUTPUT (JSON Grammar Enforcement)                              │
│          │                                                                  │
│          ▼                                                                  │
│   DETERMINISTIC VALIDATION GATEKEEPER                                       │
│   (Schema checks, physiological boundaries, forbidden clinical actions)     │
│          │                                                                  │
│          ▼                                                                  │
│   PROVENANCE & UNCERTAINTY BINDING                                          │
│   (Source citations, calibrated confidence, epistemic state: AI_INFERRED)   │
│          │                                                                  │
│          ▼                                                                  │
│   HUMAN REGISTERED MEDICAL PRACTITIONER (RMP) REVIEW                        │
│   (Sole authority to ACCEPT, MODIFY, or REJECT)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Methodology & Execution Stages

Phase 10 proceeds through ten sequential research and engineering stages:

1. **READ & RECONCILE:** Reconcile statutory Indian medical regulations (NMC 2023, BSA 2023, DPDP 2023) and upstream architectural baselines (Phases 1–9).
2. **MODEL SELECTION:** Evaluate open-weight model families (Qwen2.5 / Qwen3, Llama 3.2, BioMistral) for offline edge feasibility.
3. **RUNTIME DESIGN:** Design runtime abstractions (`AIAdapter` $\to$ `RuntimeAdapter` $\to$ `Model`) supporting Ollama, llama.cpp, and mock doubles.
4. **SAFETY & INJECTION ANALYSIS:** Formulate defensive prompt injection barriers, content delimiters, and forbidden clinical action filters.
5. **RESOURCE & FALLBACK DESIGN:** Define resource budgets (RAM/CPU/VRAM), queuing policies, and safe degradation when AI is offline.
6. **STRUCTURED CONTRACTS:** Define strongly-typed Pydantic schemas for all 7 permitted machine-consumed tasks.
7. **VALIDATION & GROUNDING:** Implement fail-closed output validation and evidence-linkage verification.
8. **ISOLATED SCAFFOLDING:** Build hermetic runtime adapters and test double in `backend/app/ai_runtime/`.
9. **TEST HARNESS EXECUTION:** Execute 20 isolated test scenarios in `backend/tests/ai_runtime/`.
10. **DOCUMENTATION & SELF-AUDIT:** Author all 30 research documents, record decisions, and issue final completion report with status `READY FOR HUMAN REVIEW`.

---

## 5. Non-Negotiable Invariants

| Invariant ID | Rule Description | Enforcement Mechanism |
|:---|:---|:---|
| **INV-AI-01** | Zero Autonomous Medical Decisions | OutputValidator rejects prescriptions, admissions, discharges, surgeries. |
| **INV-AI-02** | Zero Mandatory External Paid APIs | Local Ollama / llama.cpp runtime; zero dependence on Google Gemini or OpenAI. |
| **INV-AI-03** | Total Architectural Isolation | AI runtime modules live solely in `backend/app/ai_runtime/` and are not imported by live patient workflows. |
| **INV-AI-04** | Fail-Closed Deterministic Fallback | When AI fails (timeout, OOM, crash), deterministic triage (NEWS2, red flags) continues 100%. |
| **INV-AI-05** | Anti-Hallucination Grounding | Every clinical deduction must cite a valid `source_evidence_id` present in context. |
| **INV-AI-06** | Epistemic Uncertainty Independence | AI confidence score never reduces clinical uncertainty ($U_t$). |
| **INV-AI-07** | Multilingual Vernacular Preservation | Original colloquial terms (Odia, Hindi) are preserved verbatim alongside translations. |
