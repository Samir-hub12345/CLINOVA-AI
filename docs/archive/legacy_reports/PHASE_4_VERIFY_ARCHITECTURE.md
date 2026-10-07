# CLINOVA AI — PHASE 4: VERIFY ARCHITECTURE SPECIFICATION

**Product:** Clinova AI  
**Phase:** 4 of 10  
**Phase Name:** VERIFY (Clinical Information Verification & Review Readiness Intelligence)  
**Status:** IMPLEMENTATION COMPLETE  
**Architecture Principle:**  
$$\text{EVIDENCE} \longrightarrow \text{VERIFICATION RULES} \longrightarrow \text{VERIFICATION FINDINGS} \longrightarrow \text{VERIFICATION STATE} \longrightarrow \text{REVIEW READINESS}$$
$$\text{Never: } \text{EVIDENCE} \longrightarrow \text{LLM} \longrightarrow \text{“LOOKS GOOD”}$$

---

## 1. Core Objective & Boundaries

Phase 4 takes the versioned Canonical Patient Case produced by Phase 3 (BUILD) and evaluates whether the information inside that case is:
- **Structurally valid & referentially sound**
- **Sufficiently complete** across critical clinical intake dimensions
- **Internally consistent**, explicitly detecting cross-source and cross-modal discrepancies
- **Temporally coherent** across chronology, milestones, and medication lifecycles
- **Source-traceable**, grounding every extracted fact into raw evidence character spans
- **Uncertainty-aware**, preserving approximations, qualifiers, and machine extractions
- **Ready for professional review**, computing an explainable readiness state

### Absolute Phase Boundaries
- **Strictly Non-Diagnostic:** The verification engine assesses **information quality and integrity** for healthcare professionals. It does not provide medical diagnoses, treatment suggestions, triage severity changes, or patient admission decisions.
- **Zero Phase 5 Bleed:** No adaptive follow-up questioning, no information-gain question selection, and no conversational stopping logic.
- **Zero Phase 7 Bleed:** No automated doctor dispatch or queue prioritization.
- **Human Authoritative:** Human clinician review remains authoritative. Discrepancies and uncertainties are preserved rather than silently overwritten.

---

## 2. Verification Data Pipeline

The Phase 4 engine executes a deterministic 20-stage pipeline:

```
CANONICAL PATIENT CASE
          │
          ▼
LOAD CURRENT CASE VERSION (CaseSnapshot vN)
          │
          ▼
LOAD ASSOCIATED EVIDENCE (CaseEvidence items with SHA-256)
          │
          ▼
LOAD CANONICAL FACTS & TIMELINE (CanonicalFact & TimelineEvent entities)
          │
          ▼
VERIFY STRUCTURAL INTEGRITY (Patient linkage, foreign keys, uniqueness)
          │
          ▼
VERIFY COMPLETENESS & REQUIRED INFORMATION (Identity, complaint, vitals, allergy)
          │
          ▼
VERIFY EVIDENCE STATUS & QUALITY (Presence ≠ verification, AI/OCR awareness)
          │
          ▼
VERIFY CROSS-SOURCE CONFLICTS (Patient text vs triage readings, value discrepancies)
          │
          ▼
VERIFY CROSS-MODAL CONFLICTS (Patient voice vs written text, OCR vs staff)
          │
          ▼
VERIFY TEMPORAL CONSISTENCY (Timeline sequence order, medication dates, onsets)
          │
          ▼
VERIFY PROVENANCE & SPAN GROUNDING (Anti-hallucination substring checks)
          │
          ▼
VERIFY UNCERTAINTY & CONFIDENCE (Preserve qualifiers, prevent false certainty)
          │
          ▼
GENERATE & DEDUPLICATE VERIFICATION FINDINGS
          │
          ▼
CLASSIFY & PRIORITIZE FINDINGS (BLOCKING, HIGH, MEDIUM, LOW, INFO)
          │
          ▼
CALCULATE EXPLAINABLE REVIEW READINESS (Level, score, and specific rationales)
          │
          ▼
GENERATE PERSISTENT VERIFICATION RUN & SNAPSHOT
          │
          ▼
DATABASE PERSISTENCE (verification_runs, verification_findings, verification_conflicts)
          │
          ▼
AUDIT LOGGING (tamper-evident audit_logs trail)
          │
          ▼
REST API EXPOSITION (/api/v1/cases/{case_id}/verify, /verification, /review-readiness)
          │
          ▼
CLINICIAN UI DISPLAY (VerificationPanel in Next.js review workflow)
```

---

## 3. Database Persistence Model

Phase 4 introduces three relational tables in the PostgreSQL/SQLite schema:

### 3.1 `verification_runs`
Tracks single executions of the verification engine linked to an exact `case_version`:
- `id` (UUID pk)
- `case_id` (FK `triage_cases.id`, CASCADE)
- `patient_id` (FK `patients.id`, SET NULL)
- `encounter_id` (FK `encounters.id`, SET NULL)
- `case_snapshot_id` (FK `case_snapshots.id`, SET NULL)
- `case_version` (Integer)
- `status` (`requested`, `validating`, `running`, `completed`, `partial`, `failed`)
- `engine_version` (`4.0.0`)
- `ruleset_version` (`4.0.0`)
- `review_readiness_status` (`not_ready`, `partially_ready`, `review_ready_with_flags`, `review_ready`)
- `review_readiness_score` (Float 0.0 – 1.0)
- `review_readiness_reasons` (JSON array of strings)
- Finding counters: `findings_count`, `blocking_findings_count`, `high_findings_count`, `medium_findings_count`, `low_findings_count`, `info_findings_count`, `unresolved_findings_count`, `resolved_findings_count`
- Subsystem statuses: `structural_integrity_status`, `completeness_status`, `consistency_status`, `temporal_status`, `provenance_status`, `uncertainty_status`
- `is_current` (Boolean)
- `latency_ms` (Integer)
- `summary` (JSON)
- `started_at`, `completed_at` (Timestamps)

### 3.2 `verification_findings`
Discrete clinical information quality findings:
- `id` (UUID pk)
- `verification_run_id` (FK `verification_runs.id`, CASCADE)
- `case_id` (FK `triage_cases.id`, CASCADE)
- `case_version` (Integer)
- `finding_type` (`STRUCTURAL`, `COMPLETENESS`, `CONFLICT`, `TEMPORAL`, `PROVENANCE`, `UNCERTAINTY`, `EVIDENCE_QUALITY`)
- `category` (`IDENTITY`, `ENCOUNTER`, `PRESENTING_INFORMATION`, `SYMPTOM_INFORMATION`, `TIMELINE`, `DOCUMENTS`, `MEASUREMENTS`, `HISTORY`, `SOURCE_METADATA`, `VERIFICATION`)
- `field_name` (e.g. `patient_id`, `blood_pressure`, `chief_complaint`)
- `severity` (`BLOCKING`, `HIGH`, `MEDIUM`, `LOW`, `INFO`)
- `status` (`UNRESOLVED`, `RESOLVED_BY_NEW_EVIDENCE`, `RESOLVED_BY_HUMAN_VERIFICATION`, `RESOLVED_BY_CORRECTION`, `DISMISSED_WITH_REASON`)
- `is_blocking` (Boolean)
- `title`, `description`, `explanation` (Text)
- `expected_information`, `observed_information` (Text)
- Traceability links: `source_evidence_ids` (JSON), `fact_ids` (JSON), `timeline_event_ids` (JSON)
- `rule_id`, `rule_version` (Strings)
- Resolution metadata: `resolved_by_user_id` (FK `users.id`), `resolved_at`, `resolution_notes`

### 3.3 `verification_conflicts`
Preserves explicit contradictory clinical records:
- `id` (UUID pk)
- `verification_run_id` (FK `verification_runs.id`, CASCADE)
- `case_id` (FK `triage_cases.id`, CASCADE)
- `conflict_type` (`VALUE_CONFLICT`, `TEMPORAL_CONFLICT`, `IDENTITY_CONFLICT`, `SOURCE_CONFLICT`, `MODALITY_CONFLICT`, `UNIT_CONFLICT`, `STATUS_CONFLICT`)
- `field_name` (String)
- Source A: `source_a_evidence_id`, `source_a_type`, `source_a_modality`, `source_a_value`, `source_a_timestamp`
- Source B: `source_b_evidence_id`, `source_b_type`, `source_b_modality`, `source_b_value`, `source_b_timestamp`
- Resolution: `resolution_state`, `resolution_notes`, `resolved_by_user_id`, `resolved_at`

---

## 4. Idempotency & Case Version Stale Detection

1. **Idempotency:** When `verify_case` is invoked on an unchanged `case_version`, the engine retrieves the existing completed `VerificationRun` if `force_reverify=False`.
2. **Historical Preservation:** Prior verification runs are never overwritten or deleted. They remain immutable records.
3. **Stale Result Detection:** If a case is rebuilt in Phase 3 (e.g. case advances from version 1 to version 2), the system detects that `verified_version (1) < current_version (2)`. The endpoint and UI immediately display the badge `STALE (v1 vs Current v2)`, prompting the clinician to re-verify.

---

## 5. Offline & Native Windows Operation

- Fully operable on Windows Native with Python 3.14 (.venv) and Next.js 15.
- Zero mandatory cloud dependencies: Runs 100% deterministically in offline ₹0 mode without external AI token charges.
