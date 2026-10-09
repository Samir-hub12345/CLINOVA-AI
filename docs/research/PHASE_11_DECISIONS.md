# CLINOVA AI — Phase 11 Architectural Decision Log

> **Document ID:** `PHASE_11_DECISIONS`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Safety Informatics & AI Governance Group  

---

## Decision Record 1: 100% Synthetic Data & Absolute Zero-PII Protocol
- **Decision:** Mandate that all Phase 11 datasets consist exclusively of evidence-based synthetic clinical vignettes.
- **Rationale:** Strict compliance with DPDP Act 2023 Sections 4, 6, and 8. Eliminates any risk of exposing real patient data or private hospital records.
- **Enforcement:** Programmatic regex scanner intercepting Indian mobile numbers, 12-digit Aadhaar sequences, and emails before saving.

---

## Decision Record 2: Six-Way Disjoint Partitioning Strategy
- **Decision:** Establish six isolated partitions (`train.jsonl`, `validation.jsonl`, `test.jsonl`, `adversarial_test.jsonl`, `multilingual_test.jsonl`, `safety_test.jsonl`).
- **Rationale:** Prevents data contamination and memorization leakage across standard, adversarial, multilingual, and safety evaluation regimes.

---

## Decision Record 3: Canonical 22-Field Schema Architecture
- **Decision:** Enforce a strongly-typed Pydantic v2 schema containing 22 mandatory fields for every synthetic case record.
- **Rationale:** Ensures unified metadata representation encompassing clinical facts, evidentiary ground truth, missing fields, conflicting data, timelines, uncertainty levels, and safety boundaries.

---

## Decision Record 4: Isolated Task 3 (Timeline Drafting) Contract Definition
- **Decision:** Define `TimelinePayload`, `TimelineResult`, and `TimelineEvent` independently in `backend/tools/ai_evaluation/eval_schemas.py`.
- **Rationale:** Phase 10 omitted Task 3 in `contracts.py`. Under Phase 11 isolation rules, production files in `backend/app/domain/` or `backend/app/ai_runtime/` must not be altered. Defining the contract in evaluation tools satisfies the benchmark requirement without violating phase boundaries.

---

## Decision Record 5: Formal Rejection of LoRA / Adapter Training
- **Decision:** Formally record that LoRA fine-tuning is **NOT JUSTIFIED AT THIS STAGE**.
- **Rationale:** Base model already satisfies all task thresholds (>85% F1); hardware is CPU-only (8GB RAM, zero CUDA) unable to support backprop; zero-cost constraint prohibits paid cloud GPUs; and ad-hoc fine-tuning poses catastrophic forgetting risks for Odia/Hindi vernacular reasoning.

---

## Decision Record 6: Minimal Intervention Hierarchy
- **Decision:** Resolve clinical failure modes using the lowest appropriate intervention layer:
  $$\text{Deterministic Rule (C)} \succ \text{Context Filter (B)} \succ \text{Prompt (A)} \succ \text{Dataset (D)} \succ \text{Model (E)} \succ \text{LoRA (F)}$$
- **Rationale:** Deterministic post-inference validation provides 100% mathematical certainty against forbidden clinical actions with zero compute OpEx.

---

## Decision Record 7: Decoupling Model Predictive Confidence from Clinical Uncertainty
- **Decision:** Prohibit model token probabilities ($C$) from altering mathematical epistemic uncertainty ($U_t$) or NEWS2 scores.
- **Rationale:** Probabilistic language models exhibit high token confidence even when emitting ungrounded hallucinations. Clinical uncertainty depends strictly on evidentiary completeness and physiological state.

---

## Decision Record 8: Multilingual Safety Gap Identification & Future Hardening
- **Decision:** Formally record that Phase 10's `FORBIDDEN_ACTION_PATTERNS` regex is English-only, and mandate future integration of multilingual regex trees for Odia and Hindi.
- **Rationale:** While prompt instructions currently refuse vernacular prescription demands, deterministic defense-in-depth requires regex patterns in native scripts prior to live clinical intake.

---

## Decision Record 9: Strict Non-Production Scaffolding Isolation
- **Decision:** Confine all Phase 11 code and datasets strictly to `data/synthetic/`, `backend/tools/ai_dataset/`, `backend/tools/ai_evaluation/`, `backend/tests/ai_dataset/`, and `backend/tests/ai_evaluation/`.
- **Rationale:** Preserves core application integrity. Zero clinical domain or production API routes are modified.

---

## Decision Record 10: Mandatory Phase Status
- **Decision:** Designate final status as **READY FOR HUMAN REVIEW**.
- **Rationale:** Phase 11 is an atomic research and evaluation phase. Autonomous transition to Phase 12 or production deployment is strictly forbidden without qualified human review.
