# CLINOVA AI — Deterministic System-Derived Data Provenance Model

> **Document ID:** `RES-121`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Epistemic Status of Derived Metrics

In clinical informatics, clinical scores (such as NEWS2, Shock Index, or pediatric triage bands) are frequently treated as if they were independent primary observations. A clinician or nurse might chart: *"Patient's NEWS2 is 8"*, without documenting the underlying heart rate, blood pressure, respiratory rate, or oxygen saturation that produced that number.

This creates severe clinical and architectural hazards:
1. **Unverifiability:** If the input vitals are later found to be corrupted (e.g. an SpO2 probe slipped off the finger, causing a false drop to 82%), the derived score remains frozen in the database as an artificial emergency alert.
2. **Conflation of Derived with Primary:** A derived score is **not raw clinical evidence**; it is an arithmetic projection of an evidence vector through a deterministic formula.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL DERIVED DATA SAFETY INVARIANT                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  A DERIVED VALUE IS NOT RAW CLINICAL EVIDENCE.              │
│                                                                             │
│   Every system-derived metric must explicitly point to its exact input      │
│   evidence record IDs, its formula identifier, and its engine version.      │
│   If any input evidence record is updated, amended, or disputed,            │
│   the derived value must be deterministically re-evaluated.                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Eight Canonical Deterministic Derived Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EIGHT SYSTEM-DERIVED CLINICAL METRICS                   │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Metric Identifier        │ Mathematical Formula & Guideline Standard        │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 1. NEWS2 Composite       │ Royal College of Physicians (2017) 7-parameter   │
│ 2. Shock Index (SI)      │ $\text{SI} = \text{HR} / \text{SBP}$ (Normal: 0.5 – 0.7)          │
│ 3. Modified Shock Index  │ $\text{MSI} = \text{HR} / \text{MAP}$                            │
│ 4. Sufficiency Score (S) │ $S = \sum w_i I_i / \sum w_i$ (Gated at 0.85)    │
│ 5. Uncertainty ($U_t$)   │ $U_t = \sum w_k \phi_k(t)$ (8 evidence contributors)│
│ 6. Queue Priority $P(t)$ │ $P(t) = w_R R_t + w_{\text{wait}} f(t) + w_U U_t$│
│ 7. Trajectory Slope      │ $\Delta \text{Severity} / \Delta t$ (Time-series fit)│
│ 8. Facility Feasibility  │ $\text{Req} \subseteq \text{Cap}_{\text{fresh}}$ │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 3. Strict Derivation Provenance Requirements

Every deterministic calculation executed by CLINOVA AI captures five invariant provenance attributes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SYSTEM DERIVATION PROVENANCE VECTORS                    │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Input Snapshot    │ Immutable array of evidence_record UUIDs & values    │
│ 2. Formula ID        │ Canonical formula key (e.g. FORMULA_NEWS2_RCP_2017) │
│ 3. Rule Version      │ Semantic version string of rule engine (e.g. 1.2.0)  │
│ 4. Compute Timestamp │ Microsecond timestamp when calculation occurred      │
│ 5. Invalidation Hook │ Trigger linkage to auto-recompute upon input changes │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 4. Automatic Invalidation and Reactive Re-Derivation

Because derived values depend entirely on underlying primary evidence, any mutation to an input record triggers an automatic reactive cascade:

```
[1. Mutation Event]     Nurse corrects SpO2 typo: 82% --> 98% (Record #ev_812)
         │
[2. Dependency Graph]   System inspects all derived records citing #ev_812
                        Identified: NEWS2 Calculation #calc_904 (Score: 9, High Risk)
         │
[3. Invalidation]       #calc_904 marked is_superseded = TRUE
         │
[4. Re-Derivation]      System re-executes FORMULA_NEWS2_RCP_2017 with fresh vector:
                        SpO2 (98%), HR (78), SBP (122), RR (16), Temp (36.8), AVPU (Alert)
         │
[5. New Derived Record] Fresh calculation committed: #calc_905 (Score: 0, Low Risk)
         │
[6. Queue Update]       Doctor Queue Priority dynamically recalculated in < 50ms
```

---

## 5. Canonical System-Derived Relational Schema

```sql
CREATE TABLE system_derived_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    calculation_type VARCHAR(32) NOT NULL CHECK (calculation_type IN (
        'NEWS2_COMPOSITE', 'SHOCK_INDEX', 'MODIFIED_SHOCK_INDEX', 
        'INFORMATION_SUFFICIENCY', 'UNCERTAINTY_SCORE', 'QUEUE_PRIORITY', 
        'TRAJECTORY_CLASSIFICATION', 'FACILITY_FEASIBILITY'
    )),
    
    formula_identifier VARCHAR(64) NOT NULL, -- e.g. 'RCP_NEWS2_2017_STANDARD'
    rule_engine_version VARCHAR(32) NOT NULL,
    
    -- Input Snapshot (Preserves exact inputs used to prevent temporal skew)
    input_evidence_record_ids JSONB NOT NULL, -- ["uuid1", "uuid2", ...]
    input_values_snapshot JSONB NOT NULL,     -- { "hr": 120, "sbp": 80, ... }
    
    -- Output Result
    calculated_numeric_value NUMERIC(10,3),
    calculated_categorical_value VARCHAR(32), -- e.g. 'HIGH_RISK', 'FEASIBLE'
    calculation_breakdown JSONB NOT NULL,     -- Sub-scores: { "spo2_points": 3, "rr_points": 2 }
    
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Invalidation State
    is_superseded BOOLEAN NOT NULL DEFAULT FALSE,
    superseded_by_calculation_id UUID REFERENCES system_derived_calculations(id),
    superseded_at TIMESTAMPTZ,
    invalidation_reason VARCHAR(64)
);

CREATE INDEX ix_derived_case ON system_derived_calculations(case_id);
CREATE INDEX ix_derived_type ON system_derived_calculations(calculation_type);
CREATE INDEX ix_derived_active ON system_derived_calculations(case_id, is_superseded);
```

---

## 6. Doctor Workbench Presentation Experience

On the Doctor Workbench, derived scores are never displayed as ungrounded black boxes:
- Clicking on **NEWS2: 7 (High Acuity)** opens an interactive breakdown modal:
  ```
  NEWS2 Composite Score: 7 [HIGH CLINICAL RISK]
  ├── Respiratory Rate: 26 bpm  --> 2 points  (Source: Nurse Anita [10:24 AM])
  ├── SpO2: 91% on Air          --> 3 points  (Source: Sensor #SN-91 [10:24 AM])
  ├── Systolic BP: 104 mmHg     --> 1 point   (Source: Nurse Anita [10:24 AM])
  ├── Heart Rate: 98 bpm        --> 0 points  (Source: Sensor #SN-91 [10:24 AM])
  ├── Consciousness: Alert      --> 0 points  (Source: Nurse Anita [10:24 AM])
  └── Temperature: 38.4 °C      --> 1 point   (Source: Nurse Anita [10:24 AM])
  Computed by: RCP_NEWS2_2017_STANDARD v1.2.0 at 10:24:12 UTC
  ```
This radical transparency allows physicians to verify the arithmetic in seconds, identify flawed inputs instantly, and trust the clinical intelligence layer.
