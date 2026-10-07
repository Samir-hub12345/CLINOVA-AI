# CLINOVA AI — PHASE 4: VERIFY TESTING SPECIFICATION

This document details the test matrix, coverage, and acceptance scenarios implemented in `tests/test_phase4_verification_engine.py`.

---

## 1. Test Suite Architecture

The test suite validates the verification engine across 3 testing tiers:
1. **Isolated Modular Rule Tests:** Validating each of the 8 rules independently against synthetic contexts.
2. **12 Acceptance Scenarios (Scenarios A through L):** Validating the complete integrated clinical workflow under diverse conditions.
3. **Enterprise & Operational Integrity Tests:** Idempotency, stale versioning, cold restart persistence, anti-hallucination / no-invention audits, and RBAC / IDOR security isolation.

---

## 2. Test Matrix

| Test Function | Target Rule / Feature | Scope & Assertions |
| :--- | :--- | :--- |
| `test_structural_integrity_rule_isolated` | `StructuralIntegrityRule` | Verifies patient association, snapshot presence, foreign keys, and unique evidence IDs. Missing patient triggers `BLOCKING`. |
| `test_completeness_rule_isolated` | `CompletenessRule` | Verifies identity, presenting symptoms, vitals, and allergy documentation. Missing chief complaint triggers `BLOCKING`. |
| `test_evidence_status_rule_isolated` | `EvidenceStatusRule` | Verifies quality origin tagging. Flags unverified AI extractions and OCR values without dropping origin. |
| `test_conflict_rule_cross_source_and_cross_modal` | `CrossSourceConflictRule` | Verifies contradiction detection. Ensures both values are preserved in `verification_conflicts` with `UNRESOLVED` state. |
| `test_temporal_consistency_rule_isolated` | `TemporalConsistencyRule` | Verifies sequence ordering and relative day progression. Detects inverted chronology (Day 5 before Day 2). |
| `test_provenance_rule_isolated` | `ProvenanceRule` | Verifies anti-hallucination grounding. Detects candidate facts whose source spans do not appear in raw evidence text. |
| `test_uncertainty_rule_isolated` | `UncertaintyRule` | Verifies that clinical hedging (`UNCERTAIN`, `APPROXIMATE`) is preserved rather than flattened to boolean truth. |
| `test_review_readiness_calculator_explainability` | `ReviewReadinessCalculator` | Verifies explainable readiness calculation. Non-medical scoring based strictly on information package integrity. |

---

## 3. The 12 Synthetic Clinical Acceptance Scenarios

| Scenario | Objective | Expected Result |
| :--- | :--- | :--- |
| **Scenario A** | Complete clean case intake | Status: `completed`, 0 blocking findings, review readiness `review_ready`, score $\ge 0.70$. |
| **Scenario B** | Missing information detection | Status: `not_ready`, flags missing patient ID, demographics, vitals; categorizes each missing field. |
| **Scenario C** | Conflicting clinical values | Contradictory values (39.0 °C vs 36.8 °C) preserved in `verification_conflicts`; no silent overwrites. |
| **Scenario D** | Temporal contradiction | Detects medication discontinuation sequenced before medication initiation; generates `TEMPORAL` finding. |
| **Scenario E** | OCR vs Patient Voice discrepancy | Detects cross-modal conflict between scanned lab slip and oral voice transcript; preserves modalities. |
| **Scenario F** | Multilingual translation provenance | Odia/Hindi input text preserved; translation linked; provenance status confirmed `COMPLETE`. |
| **Scenario G** | Missing provenance detection | Fact lacking `source_evidence_id` or with ungrounded span is identified and flagged as `PROVENANCE` gap. |
| **Scenario H** | Unverified AI extraction | AI-derived diagnostic inference preserved with explicit `unverified` status and `EVIDENCE_QUALITY` flag. |
| **Scenario I** | Staff verification resolves finding | Clinician submits resolution with rationale; finding state transitions to `RESOLVED_BY_HUMAN_VERIFICATION`. |
| **Scenario J** | Broken case structure handling | Non-existent case or invalid relations fail gracefully with safe exception handling without crashing backend. |
| **Scenario K** | Offline ₹0 development mode | Deterministic checks complete 100% offline without third-party AI provider calls or cost bleed. |
| **Scenario L** | Cross-patient IDOR security attempt | Patient B attempting to access Patient A's verification is rejected with `403 Forbidden` / `404 Not Found`. |

---

## 4. Operational & Security Tests

1. **Idempotency & Stale Detection (`test_verification_idempotency_and_stale_detection`):**
   - Re-verifying unchanged case version returns identical cached run.
   - Advancing case version via Phase 3 build immediately flags prior verification as `is_stale = true`.
2. **Cold Restart Persistence (`test_cold_restart_persistence`):**
   - Verification runs, findings, and conflicts reloaded from a brand new database session maintain identical state.
3. **No-Invention Anti-Hallucination Audit (`test_no_invention_anti_hallucination_verification`):**
   - Verifies that verification findings only report on actual evidence data and never inject fabricated diagnoses.
