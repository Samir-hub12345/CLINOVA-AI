# CLINOVA AI — PHASE 4: VERIFICATION RULES SPECIFICATION

This document details the modular rules implemented in the Phase 4 Clinical Verification Engine (`app/services/verification/rules/`).

---

## 1. Rule Directory

| Rule Module | Rule ID | Scope & Purpose | Typical Severities |
| :--- | :--- | :--- | :--- |
| `structural_rule.py` | `structural_integrity_rule` | Validates patient linkage, snapshot existence, non-null constraints, and foreign key references. | `BLOCKING`, `HIGH` |
| `completeness_rule.py` | `clinical_completeness_rule` | Evaluates completeness of demographics, chief complaints, core vitals, and allergy documentation. | `BLOCKING`, `HIGH`, `MEDIUM`, `LOW` |
| `evidence_status_rule.py` | `evidence_status_awareness_rule` | Enforces origin awareness: presence ≠ verification. Flags unverified AI or OCR extractions. | `MEDIUM`, `LOW` |
| `conflict_rule.py` | `cross_source_conflict_rule` | Detects cross-source and cross-modal discrepancies (e.g. text vs voice, device vs patient). Preserves both. | `HIGH` |
| `temporal_rule.py` | `temporal_consistency_rule` | Validates sequence ordering, timeline day progression, and medication lifecycle events. | `HIGH`, `MEDIUM` |
| `provenance_rule.py` | `source_provenance_rule` | Anti-hallucination span validation. Ensures all facts anchor to verifiable evidence substrings. | `HIGH`, `MEDIUM` |
| `uncertainty_rule.py` | `uncertainty_representation_rule` | Preserves clinical qualifiers (`UNCERTAIN`, `APPROXIMATE`) and prevents false machine certainty. | `INFO`, `LOW` |
| `review_readiness_rule.py` | `review_readiness_calculator` | Synthesizes subsystem findings into an explainable review readiness level, score, and rationales. | Evaluator |

---

## 2. Rule Specifications

### 2.1 Structural Integrity Rule (`StructuralIntegrityRule`)
- **Evaluates:**
  1. `case.patient_id` presence: If missing, generates `BLOCKING` finding.
  2. `case_snapshot` presence: If missing, generates `BLOCKING` finding.
  3. Evidence ID uniqueness: Rejects duplicate UUIDs inside a case evidence graph (`HIGH`).
  4. Referential resolution: Verifies that every `fact.source_evidence_id` and `timeline_event.source_evidence_id` resolves to an existent entity in `case_evidence` (`HIGH`).
  5. Timestamp sanity: Rejects evidence observation timestamps occurring in the future (`MEDIUM`).

### 2.2 Clinical Completeness Rule (`CompletenessRule`)
- **Evaluates categories:**
  - `IDENTITY`: Verifies patient age/DOB (`HIGH` if missing) and biological sex (`MEDIUM` if missing).
  - `PRESENTING_INFORMATION`: Verifies presence of a chief complaint or active symptoms. Missing complaint is strictly `BLOCKING`.
  - `SYMPTOM_INFORMATION`: Checks for explicit duration or onset timing qualifiers (e.g. 'for 3 days'). Generates `MEDIUM` if omitted.
  - `MEASUREMENTS`: Checks for objective vital signs. If zero vitals exist, generates `HIGH`. If partial core vitals (BP, HR, Temp) are missing, generates `LOW`.
  - `HISTORY`: Checks for drug/substance allergy documentation. Generates `MEDIUM` if unrecorded.
  - `TIMELINE`: Checks for milestone timeline events (`LOW` if empty).

### 2.3 Evidence Status Awareness Rule (`EvidenceStatusRule`)
- **Principle:** Presence does not equal verification.
- **Evaluates:**
  - `AI_EXTRACTED` or `AI_INFERRED` facts: Flagged as `MEDIUM` unverified machine outputs until reviewed.
  - `OCR_DERIVED` measurements: Flagged as `LOW` unverified document readings until staff verification.
  - `PATIENT_REPORTED` vitals: Flagged as `LOW` self-reported claims, distinguishing them from calibrated clinic instruments.

### 2.4 Cross-Source & Cross-Modal Conflict Rule (`CrossSourceConflictRule`)
- **Evaluates:**
  - Facts with `has_conflict = True` from Phase 3 Multimodal Fusion.
  - Discrepancies between modalities: `PATIENT_TEXT`, `PATIENT_VOICE`, `DOCUMENT_OCR`, `CLINICIAN_ENTRY`.
  - Polarity contradictions: Concept affirmed in Record A and negated in Record B (`STATUS_CONFLICT`, `HIGH`).
  - Temporal duration discrepancies: Voice recording says "3 days" while text intake says "yesterday" (`TEMPORAL_CONFLICT`, `HIGH`).
- **Preservation Contract:** Both conflicting records are stored in `verification_conflicts` with exact values, timestamps, and modalities. Neither is deleted or averaged.

### 2.5 Temporal Consistency Rule (`TemporalConsistencyRule`)
- **Evaluates:**
  - Chronological sequence: Identifies cases where Day N+K is ordered before Day N (`HIGH`).
  - Conflicting onset phrases: Flags disparate duration phrases across the same symptom (`MEDIUM`).
  - Medication lifecycle: Flags situations where a medication discontinuation event precedes its initiation event (`HIGH`).

### 2.6 Source Provenance Rule (`ProvenanceRule`)
- **Evaluates:**
  - Traceability: Flags canonical facts lacking `source_evidence_id` (`HIGH`).
  - Span existence: Flags facts lacking `source_span` (`MEDIUM`).
  - Anti-hallucination span validation: Checks whether `source_span` is a true substring of the raw or normalized source evidence text. Ungrounded spans generate `HIGH` provenance findings.
  - OCR document linkage: Verifies that OCR evidence items maintain links to underlying file storage artifacts (`LOW`).

### 2.7 Uncertainty Representation Rule (`UncertaintyRule`)
- **Evaluates:**
  - Preserves clinical qualifiers (`certainty = UNCERTAIN`, `certainty = APPROXIMATE`) as `INFO` and `LOW` findings.
  - Guarantees that downstream clinical review sees exactly what was hedged by the patient or clinician.

### 2.8 Review Readiness Calculator (`ReviewReadinessCalculator`)
- **Formula:**
  $$\text{Base Score} = 1.0$$
  $$\text{Score} = \max(0.0, 1.0 - \text{penalties})$$
  - Any `BLOCKING` finding $\rightarrow$ `NOT_READY`, score $\le 0.20$
  - Partial completeness $\rightarrow -0.15$
  - Unresolved conflicts $\rightarrow -0.20$
  - Temporal anomalies $\rightarrow -0.15$
  - Provenance gaps $\rightarrow -0.15$
- **Level Mapping:**
  - `BLOCKING` issues $\rightarrow$ `NOT_READY`
  - Score $< 0.70 \rightarrow$ `PARTIALLY_READY`
  - Unresolved conflicts or `HIGH` findings present $\rightarrow$ `REVIEW_READY_WITH_FLAGS`
  - Clean, grounded case with score $\ge 0.70 \rightarrow$ `REVIEW_READY`
- **Output:** Returns human-readable, explainable reasons for every deduction.
