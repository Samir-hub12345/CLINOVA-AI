# CLINOVA AI — Gold Labeling & Human-Reviewed Annotation Model

> **Document ID:** `RES-224`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Informatics, Medical Annotation & Safety Group  

---

## 1. Overview & Epistemic Stance
Clinical narratives possess inherent linguistic variation. Unlike synthetic computer vision benchmarks where absolute pixel bounding boxes exist, clinical documentation allows multiple grammatically correct expressions for the same observation.

CLINOVA establishes a dual-tier gold labeling model:
1. **Objective Hard Labels:** Strict deterministic truth for vital signs, numerical parameters, exact source citations, forbidden action triggers, and injection flags.
2. **Human-Reviewed Expected Output:** Semantically verified targets for narrative summaries, question rationales, and vernacular translations.

---

## 2. Task-Specific Gold Label Definitions
- **Entity Extraction:** Exact entity names, reported duration, severity level, and specific evidence pointer IDs.
- **Source Attribution:** Mandatory citation linking extracted facts to valid `evidence_ids`.
- **Missing Information:** Explicit identification of unrecorded parameters (e.g. unmeasured blood pressure in community clinic).
- **Conflict Handling:** Explicit flag identifying contradictory claims (e.g., subjective cold vs measured 39.4 C).
- **Timeline Sequencing:** Chronological events ordered by physical timeline, rather than presentation sequence in narrative prose.
- **Follow-up Questions:** Value-of-information inquiries targeting specific missing diagnostic gaps rather than generic inquiries.
- **Vernacular Idiom Capture:** Verbatim preservation of Odia and Hindi somatic expressions (e.g., Odia `ଛାତିରେ ଗପ ଗପ` [chhati re gapa gapa], Hindi `तेज बुखार और कंपकंपी`).
- **Advisory Action Class:** Exact categorization into approved actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`).

---

## 3. Human Review Designation
Where subjective clinical prose is involved, records are explicitly tagged:
```json
"annotation_version": "v1.0.0-synthetic-gold"
```
The documentation explicitly records that CLINOVA does not claim singular absolute medical truth for subjective narrative style; all outputs are evaluated as non-binding drafts requiring Registered Medical Practitioner (RMP) review under NMC Regulations 2023.
