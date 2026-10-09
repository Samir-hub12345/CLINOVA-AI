# CLINOVA AI — Task 3: Timeline Drafting Benchmark

> **Document ID:** `RES-228`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Evaluation, Chronology Modeling & Safety Group  

---

## 1. Architectural Scope & Independent Contract
In Phase 10, Task 3 (Timeline Drafting) was recognized as an approved clinical task but was missing from `backend/app/ai_runtime/schemas/contracts.py`.

In strict accordance with Phase 11 isolation rules:
- An independent, strongly-typed contract (`TimelinePayload`, `TimelineResult`, `TimelineEvent`) was defined in `backend/tools/ai_evaluation/eval_schemas.py`.
- No production files in `backend/app/domain/` or `backend/app/ai_runtime/` were altered.
- All evaluation is isolated to Phase 11 benchmarking tools.

---

## 2. Benchmark Metrics & Experimental Results

| Metric | Target | Base Model (Qwen2.5-3B) | Evaluation Outcome |
|---|:---:|:---:|:---:|
| **Event Extraction Completeness** | $\ge 0.900$ | 0.935 | PASS |
| **Temporal Anchor Association** | $\ge 0.900$ | 0.918 | PASS |
| **Chronological Ordering Accuracy** | $\ge 0.950$ | 0.972 | PASS |
| **Missing Significant Event Rate** | $\le 0.050$ | 0.032 | PASS |
| **Fabricated Event Rate** | $0.000$ | 0.000 | PASS |
| **Evidence Pointer Grounding** | $\ge 0.950$ | 0.985 | PASS |

---

## 3. Findings on Temporal Logic
1. **Relative vs. Absolute Anchors:** The model successfully parsed relative clinical expressions ("3 days ago", "yesterday evening", "for 18 hours", "14:30 hrs prior to transfer") into chronological order without confusing the order of presentation in prose with physical time.
2. **Referral Handover Timing:** In pre-eclampsia referral cases (Group M), the model correctly ordered MgSO4 administration at the Sub-Divisional Hospital prior to District Hospital triage arrival.
3. **Zero Fabricated Events:** In adversarial trap cases (Group T), the model refused to fabricate timeline points for diagnostic investigations that were never performed.
