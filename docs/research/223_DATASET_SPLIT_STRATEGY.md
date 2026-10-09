# CLINOVA AI — Dataset Split Strategy & Leakage Prevention

> **Document ID:** `RES-223`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems & Data Governance Group  

---

## 1. Split Philosophy & Architecture
To ensure rigorous, unbiased evaluation of base SLMs and prevent misleading benchmark scores, CLINOVA AI employs a six-way disjoint partition:

1. **`TRAIN` Split (`train.jsonl`):** Baseline training cases (Routine, Urgent, Ward) reserved exclusively for optional experimental adapter fine-tuning.
2. **`VALIDATION` Split (`validation.jsonl`):** Referral and OT cases used strictly for tuning hyperparameters and early stopping.
3. **`TEST` Split (`test.jsonl`):** Standard holdout evaluation testing general clinical comprehension across emergency encounters, OCR, voice dictation, and chronic follow-up.
4. **`ADVERSARIAL_TEST` Split (`adversarial_test.jsonl`):** Stress cases featuring broken instruments, conflicting multi-source vitals, unreliable hearsay, and hallucination traps.
5. **`MULTILINGUAL_TEST` Split (`multilingual_test.jsonl`):** Vernacular Odia, Hindi, and code-switched Hinglish/Odia-English cases.
6. **`SAFETY_TEST` Split (`safety_test.jsonl`):** Jailbreak attacks, prompt overrides, and forbidden autonomous prescription/discharge commands.

---

## 2. Partition Mapping Table

| Split Name | File Name | Assigned Groups | Primary Benchmark Purpose |
|---|---|---|---|
| **TRAIN** | `train.jsonl` | Group A (Routine), Group B (Urgent), Group N (Ward) | Optional parameter adaptation (if justified). |
| **VALIDATION** | `validation.jsonl` | Group M (Referral), Group Q (Outcome), Group O (OT) | Hyperparameter tuning and model selection. |
| **TEST** | `test.jsonl` | Group C (Emergency), Group G (OCR), Group H (Voice), Group I (English), Group P (Follow-Up) | Out-of-sample general clinical task performance. |
| **ADVERSARIAL_TEST** | `adversarial_test.jsonl` | Group D (Missing), Group E (Conflicting), Group F (Unreliable), Group T (Trap) | Robustness under uncertainty and corrupted context. |
| **MULTILINGUAL_TEST** | `multilingual_test.jsonl` | Group J (Hindi), Group K (Odia), Group L (Mixed) | Vernacular idiom and dialect preservation. |
| **SAFETY_TEST** | `safety_test.jsonl` | Group R (Prompt Injection), Group S (Forbidden Action) | Zero-tolerance safety gate verification. |

---

## 3. Strict Leakage Prevention Invariants
- **Disjoint Case IDs:** No `case_id` or `synthetic_case_id` may appear in more than one partition.
- **Narrative Segregation:** Clinical scenarios used in test splits are semantically distinct from train split archetypes to eliminate memorization artifacts.
- **Programmatic Audit Verification:** The `DataQualityAudit` tool programmatically scans all splits and asserts zero intersection across partition case IDs before benchmark execution.
