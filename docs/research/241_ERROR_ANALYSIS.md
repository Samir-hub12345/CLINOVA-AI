# CLINOVA AI — Root Cause Error Analysis

> **Document ID:** `RES-241`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems, Clinical Safety & Root Cause Engineering Group  

---

## 1. Analysis Methodology
Whenever an error is logged under the E001–E020 taxonomy, engineering must establish its true root cause rather than reflexively proposing model fine-tuning.

Potential root causes include:
1. **Prompt Problem:** Ambiguous system instructions or missing negative constraints.
2. **Context Construction:** Context window bloat, missing evidence delimiters, or ordering artifacts.
3. **Validator Gap:** Weak regex patterns or missing schema constraints.
4. **Source Format Anomaly:** Severe OCR noise or unpunctuated ASR audio transcripts.
5. **Deterministic Logic Missing:** Expecting a probabilistic model to do arithmetic or NEWS2 calculation instead of using deterministic code.
6. **Intrinsic Model Limitation:** Attention degradation over long contexts or lack of pre-training representation for rare tribal dialects.

---

## 2. High-Impact Error Analysis Table

| Error Code | Primary Observed Cause | Recommended Intervention Layer | Justification |
|---|---|:---:|---|
| **E004 (Wrong provenance)** | Model generates generic citation when evidence ID is buried in dense prose. | **Context Filtering** | Present evidence as structured JSON items rather than raw narrative blobs. |
| **E007 (Wrong numerical vital)**| Minor OCR digit confusion (`18O` vs `180`). | **Deterministic Validator** | Check extracted vitals against plausible human physiological bounds. |
| **E012 (Prompt injection)** | User prompt mimics system instructions (`[SYSTEM OVERRIDE]`). | **Input Sanitizer** | Passive delimitation (`<untrusted_input_data>`) completely neutralizes injection. |
| **E013 (Forbidden action)** | Conversational user explicitly asks "write me a prescription". | **Deterministic Output Gate** | Hard regex pattern intercepts and refuses prescription tokens. |
| **E018 (Conflict mishandling)**| Two contradictory vitals present in same context. | **System Prompt Template** | Instruct model to explicitly highlight discrepancies in `uncertainty_statement`. |

---

## 3. Core Finding: Fine-Tuning is the Wrong Tool for Safety Gates
Attempting to fix safety violations (E012, E013) or numerical errors (E007) via fine-tuning is fundamentally flawed. Weight adaptation cannot provide mathematical 100% guarantees against jailbreaks or arithmetic drift. Deterministic post-inference validation is strictly required and vastly more reliable.
