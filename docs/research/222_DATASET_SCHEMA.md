# CLINOVA AI — Canonical Dataset Schema Specification

> **Document ID:** `RES-222`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Architecture, Data Engineering & Schema Standards Group  

---

## 1. Overview & Architectural Role
The CLINOVA synthetic evaluation corpus adopts a strict 22-field canonical schema implemented via Pydantic v2 in `backend/tools/ai_dataset/schema.py`. This schema ensures that every synthetic record encapsulates all evidentiary, clinical, and safety attributes necessary for multi-task benchmarking.

---

## 2. Canonical 22-Field Specification Table

| # | Field Name | Data Type | Required | Description |
|---|---|---|:---:|---|
| 1 | `case_id` | `string` | Yes | Unique case identifier (e.g. `syn-case-001`). |
| 2 | `synthetic_case_id` | `string` | Yes | Globally unique lineage identifier (e.g. `syn-case-001-grp-a-01`). |
| 3 | `environment` | `string` | Yes | Clinical environment (`OPD`, `EMERGENCY_DEPT`, `WARD`, `OT`, `COMMUNITY_HEALTH`, `TELEMEDICINE`). |
| 4 | `language` | `string` | Yes | Source language (`en`, `hi`, `od`, `mixed`). |
| 5 | `input_type` | `string` | Yes | Input modality (`TYPED_NARRATIVE`, `OCR_DERIVED`, `VOICE_DERIVED`, `STRUCTURED_ENTRY`). |
| 6 | `source_type` | `string` | Yes | Information source origin (`PATIENT_STATEMENT`, `TRIAGE_NURSE_ENTRY`, `REFERRAL_LETTER`, etc.). |
| 7 | `source_text` | `string` | Yes | Raw narrative provided as input to the AI model. Zero PII enforced. |
| 8 | `structured_truth` | `dict` | Yes | Verified clinical facts (symptoms, vitals, labs) used as gold labels. |
| 9 | `evidence_ids` | `list[string]` | Yes | Permitted evidence identifiers grounding this encounter. |
| 10 | `required_fields` | `list[string]` | Yes | Minimum clinical elements required for task completeness. |
| 11 | `missing_fields` | `list[string]` | Yes | Elements genuinely absent from context (e.g. unrecorded vitals). |
| 12 | `conflicting_fields` | `list[string]` | Yes | Elements with contradictory multi-source claims. |
| 13 | `expected_timeline` | `list[dict]` | Yes | Gold chronological sequence with timestamps and evidence IDs. |
| 14 | `expected_questions` | `list[dict]` | Yes | High-value follow-up questions targeting specific information gaps. |
| 15 | `expected_summary` | `dict` | Yes | Gold non-diagnostic chief complaint and positive/negative tables. |
| 16 | `expected_uncertainty` | `dict` | Yes | Epistemic uncertainty level (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) and known unknowns. |
| 17 | `expected_provenance` | `list[dict]` | Yes | Grounding mapping linking every output claim to a valid evidence ID. |
| 18 | `expected_advisory_behavior` | `dict` | Yes | Approved action class (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`) and considerations. |
| 19 | `safety_constraints` | `list[string]` | Yes | Mandated clinical safety boundaries (e.g. `NO_AUTONOMOUS_DIAGNOSIS`, `NO_PRESCRIPTION`). |
| 20 | `gold_output` | `dict` | Yes | Human-reviewed expected output across target tasks. |
| 21 | `annotation_version` | `string` | Yes | Semantic annotation protocol version tag (`v1.0.0-synthetic-gold`). |
| 22 | `dataset_version` | `string` | Yes | Dataset release version (`v1.0.0-phase11`). |

---

## 3. Structural Invariants & Validation Rules
- **Cross-Reference Invariant:** Every evidence ID referenced in `expected_provenance` or `expected_timeline` must exist in `evidence_ids`.
- **Zero-PII Invariant:** Any match against phone numbers, 12-digit numbers, or email strings triggers validation failure.
- **Safety Boundary Invariant:** A record with an empty `safety_constraints` array is rejected immediately.
