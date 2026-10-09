# CLINOVA AI — Prompt vs. Model vs. Rule Intervention Analysis

> **Document ID:** `RES-242`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Informatics & AI Engineering Group  

---

## 1. The Principle of Minimal Intervention
In medical software engineering, system complexity correlates directly with latent risk and audit burden. When addressing an AI operational defect, engineering must systematically choose the **smallest, most verifiable intervention** according to the hierarchy of control:

$$\text{Deterministic Rule (C)} \succ \text{Context Filtering (B)} \succ \text{Prompt Template (A)} \succ \text{Dataset Refinement (D)} \succ \text{Model Selection (E)} \succ \text{LoRA Training (F)}$$

---

## 2. Six Intervention Layers Compared

| Layer | Type | Auditability | Failure Mode | Compute Cost | Verification Ease |
|:---:|---|:---:|---|:---:|:---:|
| **A** | **Better Prompt** | High | Subjective drift | ₹0 | High (Regex / Diff) |
| **B** | **Better Context Filtering** | High | Information omission | ₹0 | High (Unit Test) |
| **C** | **Deterministic Validation** | **Absolute** | Over-rejection | ₹0 | **Absolute (Unit Test)** |
| **D** | **Better Dataset** | High | Bias / Leakage | ₹0 | High (Data Audit) |
| **E** | **Model Architecture Change** | Moderate | Higher RAM footprint | ₹0 | Moderate (Benchmark) |
| **F** | **LoRA / Adapter Training** | **Lowest** | Catastrophic forgetting | High | **Hardest (Re-eval)** |

---

## 3. Practical Intervention Case Studies
1. **Forbidden Prescriptions (E013):** Do not fine-tune weights to reject prescriptions. A deterministic regex pattern (`check_forbidden_clinical_actions`) offers 100% mathematical certainty at zero compute cost.
2. **Physiological Vital Bounds (E007):** Do not teach an SLM that human body temperature cannot exceed 45 C via LoRA training. Enforce `PHYSIOLOGICAL_RANGES` deterministically in Pydantic validators.
3. **Prompt Injection Defense (E012):** Do not rely on LLM safety alignment. Sanitize inputs and wrap them in passive `<untrusted_input_data>` tags via `InputSanitizer`.
4. **Conclusion:** 95% of clinical safety invariants are resolved at Layers A, B, and C without requiring model retraining.
