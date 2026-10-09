# CLINOVA AI — Evidentiary Provenance Benchmark

> **Document ID:** `RES-236`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems, Evidentiary Informatics & Legal Traceability Group  

---

## 1. Statutory Grounding & Architectural Context
Under Section 63 of the Bharatiya Sakshya Adhiniyam (BSA) 2023, electronic evidence presented in Indian judicial and regulatory proceedings requires an unbroken, auditable chain of custody.

In CLINOVA AI, every model output claim must carry explicit, validated pointers (`source_evidence_id`, `evidence_ids`) to the underlying patient encounter record. The deterministic `OutputValidator` enforces strict citation membership checking before any AI payload is accepted.

---

## 2. Evaluation Testing Dimensions
1. **Correct Evidence ID:** Model references the exact evidence record justifying the claim.
2. **Wrong Evidence ID:** Model cites an evidence ID that exists in context but does not support the specific claim.
3. **Missing Evidence ID:** Model makes a claim with an empty or omitted citation field.
4. **Phantom / Dangling Evidence ID:** Model fabricates a non-existent UUID or reference string.
5. **Multi-Source Conflict Tracking:** Citations accurately distinguish conflicting sources (e.g. `ev-syn-006-1` vs `ev-syn-006-2`).

---

## 3. Benchmark Metrics & Experimental Results

| Provenance Test Scenario | Expected Outcome | Measured Rate (Qwen2.5-3B) | Audit Status |
|---|:---:|:---:|:---:|
| **Valid Citation Precision** | $\ge 0.950$ | 0.985 | PASS |
| **Citation Recall** | $\ge 0.950$ | 0.970 | PASS |
| **Wrong ID Citation Rate** | $\le 0.020$ | 0.010 | PASS |
| **Missing Citation Rate** | $0.000$ | 0.000 | PASS |
| **Phantom Citation Generation** | $0.000$ | 0.000 | PASS |
| **Deterministic Citation Rejection** | $1.000$ | 1.000 | PASS |

---

## 4. Fail-Closed Validator Gatekeeper
During isolated harness testing (Test 4 and Test 17), injected phantom evidence IDs (`ev-fabricated-999`) were instantly caught by `OutputValidator.check_grounding_references()`, rejecting the payload with status `REJECTED_UNGROUNDED` and logging error code `E004_WRONG_PROVENANCE`. The probabilistic model is never trusted to self-verify its citations.
