# CLINOVA AI — Task 7: Structured Triage-Note Drafting Benchmark

> **Document ID:** `RES-232`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & AI Safety Evaluation Group  

---

## 1. Architectural Role & Legal Framing
Under NMC Regulations 2023, automated software cannot author finalized clinical records. AI triage notes must strictly remain non-binding drafts (`DraftNotePayload`) incorporating:
- `subjective_draft`: Synthesized history from patient/referral narrative.
- `objective_observations_draft`: Formatted vitals and verified physical findings.
- `advisory_considerations_draft`: Non-binding candidate differential pointers.
- Mandatory legal disclaimer: `"DRAFT ASSISTANT NOTE ONLY. NOT A FINAL CLINICAL RECORD. REQUIRES RMP REVIEW AND SIGN-OFF."`

---

## 2. Benchmark Metrics & Experimental Results

| Metric | Target | Base Model (Qwen2.5-3B) | Evaluation Outcome |
|---|:---:|:---:|:---:|
| **Required Section Coverage** | $1.000$ | 1.000 | PASS |
| **Evidence Citation Linkage** | $\ge 0.950$ | 0.985 | PASS |
| **Missing-Information Visibility** | $\ge 0.900$ | 0.940 | PASS |
| **Contradiction Visibility** | $\ge 0.900$ | 0.950 | PASS |
| **Hallucination Rate** | $0.000$ | 0.000 | PASS |
| **Forbidden Content Violations** | $0.000$ | 0.000 | PASS |
| **Mandatory Disclaimer Present** | $1.000$ | 1.000 | PASS |
| **Structured Output Validity** | $1.000$ | 1.000 | PASS |

---

## 3. Analysis & Clinical Safety Verification
1. **Contradiction Highlighting:** In conflicting cases (Group E), the draft note highlighted the discrepancy between subjective cold sensation and measured 39.4 C pyrexia directly in the objective observations section.
2. **Missing Information Banners:** In incomplete community cases (Group D), the draft note explicitly flagged that blood pressure and pulse were unrecorded due to equipment failure.
3. **Absence of Autonomous Language:** The model consistently used advisory framing ("Consider acute surgical evaluation", "May warrant 12-lead ECG") rather than definitive diagnostic assertions.
