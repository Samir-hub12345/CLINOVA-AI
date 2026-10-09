# CLINOVA AI — AI Runtime Bidirectional Traceability Matrix

> **Document ID:** `RES-218`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Traceability & Quality Assurance Group  

---

## 1. Traceability Methodology

This matrix establishes bidirectional traceability linking:
1. **Statutory Indian Frameworks:** NMC Regulations 2023, BSA 2023, DPDP Act 2023, Supreme Court *Paschim Banga* (1996).
2. **BPUT Baseline Requirements:** Problem statements `B01` through `B18`.
3. **Core Architectural Innovations:** Innovations `C01` through `C11`.
4. **Upstream Foundation Phases:** Phases 1 through 9.
5. **Phase 10 AI Runtime Components:** Files in `backend/app/ai_runtime/` and specifications in `docs/research/192`–`217`.

---

## 2. Master Bidirectional Traceability Matrix

| Requirement / Mandate ID | Description | Upstream Phase Baseline | Phase 10 Architectural Component | Verification Invariant |
|:---|:---|:---|:---|:---|
| **NMC Reg. 27 & 28** | Physician Monopoly: Only RMP may diagnose/prescribe. | Phase 3 (`RES-34`), Phase 7 (`RES-120`) | `OutputValidator.check_forbidden_clinical_actions` | `chk_ai_never_autonomous`, `REJECTED_FORBIDDEN_ACTION` |
| **BSA 2023 Sec. 63** | Forensic Cryptographic Traceability of Digital Evidence. | Phase 7 (`RES-107`, `RES-122`) | `ai_inferences` schema, `ModelDescriptor` | `weights_sha256`, `prompt_git_commit_hash` |
| **DPDP Act 2023 Sec. 6** | Purpose Limitation & Data Minimisation (Zero PHI Egress). | Phase 4 (`RES-39`), Phase 9 (`RES-166`) | `InputSanitizer`, `AIRuntimeService` | Zero outbound internet sockets; local loopback only. |
| **Paschim Banga (1996)** | Emergency Non-Refusal & Zero Latency Obstruction. | Phase 1 (`RES-01`), Phase 5 (`RES-60`) | Priority Scheduling, Fallback Mode | AI timeout never blocks NEWS2 or red-flag alerts. |
| **BPUT B01 / B02** | Multilingual Vernacular Intake (Odia / Hindi). | Phase 2 (`RES-19`), Phase 8 (`RES-146`) | `PROMPT_TRANSLATION_V1`, `TranslationPayload` | Colloquial idioms preserved in `preserved_colloquialisms`. |
| **BPUT B04 / B05** | Real-time Vital Risk Scoring & Triage. | Phase 2 (`RES-03`), Phase 6 (`RES-89`) | Decoupled pure Python engine in `domain/caregraph` | AI never calculates NEWS2; deterministic scoring isolated. |
| **BPUT B07** | Automated Clinical Note Drafting for Overburdened Doctors. | Phase 2 (`RES-04`), Phase 8 (`RES-144`) | `PROMPT_TRIAGE_DRAFT_V1`, `DraftNotePayload` | Draft marked with legal non-diagnostic disclaimer. |
| **Core Innovation C01** | Zero-Cost Pure Local Open-Source Architecture. | Phase 2 (`RES-18`), Phase 9 (`RES-188`) | `OllamaRuntimeAdapter`, `LlamaCppRuntimeAdapter` | Zero paid APIs; ₹0 recurring monthly software OpEx. |
| **Core Innovation C02** | Epistemic Uncertainty Quantification ($U_t$). | Phase 6 (`RES-89`), Phase 7 (`RES-116`) | `OutputValidator`, `CanonicalCaseEpistemicRecord` | AI confidence $C$ cannot lower epistemic uncertainty $U_t$. |
| **Core Innovation C03** | Anti-Hallucination Grounding & Evidence Citations. | Phase 7 (`RES-113`), Phase 8 (`RES-144`) | `OutputValidator.check_grounding_references` | `REJECTED_UNGROUNDED` triggered if cited ID is missing. |
| **Core Innovation C04** | Prompt Injection Defense for Untrusted Transcripts/OCR. | Phase 8 (`RES-157`), Phase 9 (`RES-185`) | `InputSanitizer.sanitize` | Role `PASSIVE_DATA_ONLY`, XML escaping, injection tags. |
| **Core Innovation C05** | Immutable Clinician Modification Ledger. | Phase 7 (`RES-122`), Phase 8 (`RES-152`) | `ClinicianOverrideRecord`, `clinician_modifications` | Original AI output & clinician edits preserved. |
