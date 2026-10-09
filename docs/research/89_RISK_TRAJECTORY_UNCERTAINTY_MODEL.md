# CLINOVA AI — Risk, Trajectory & Uncertainty Decoupling Data Model

> **Document ID:** `RES-89`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: The 3-Axis Clinical Decomposition

In safety-critical medicine, collapsing clinical status into a single scalar number (e.g. "Risk Score = 65%") creates fatal clinical blind spots:
1. **Conflating Risk with Trajectory:** A patient with severe chronic COPD who is currently stable is at High Static Risk, but has a Flat Trajectory. Conversely, a previously healthy child with a rapidly worsening asthma attack has Low Initial Risk but a Steeply Negative Trajectory.
2. **Conflating Low Risk with Incomplete Data (Uncertainty):** An algorithm that scores a patient with missing blood pressure and missing oxygen saturation as "Low Risk" is confusing **absence of data** with **absence of illness**.

CLINOVA AI strictly decouples evaluation across **Three Independent Orthogonal Axes**:

```
                              ▲ TRAJECTORY (Axis 2)
                              │  [IMPROVING, STABLE, DETERIORATING, RAPIDLY_DETERIORATING]
                              │
                              │         • High Risk, Rapid Deterioration, High Uncertainty
                              │           (Emergent Resuscitation & Diagnostic Aggression)
                              │
                              │
     ─────────────────────────┼─────────────────────────► RISK (Axis 1)
                              │                           [LOW, MODERATE, HIGH, CRITICAL]
                              │
                              │
                              ▼ UNCERTAINTY (Axis 3)
                                [LOW, MODERATE, HIGH, CRITICAL_UNCERTAINTY]
```

---

## 2. Explicit 3-Axis Taxonomy

### 2.1 Axis 1: Physiological Risk
Measures current acute physiological hazard and likelihood of decompensation:
- **`LOW`:** Vital signs within normal limits; no organ dysfunction; low risk of short-term mortality.
- **`MODERATE`:** Mild derangement (e.g. heart rate 105, BP 145/95); requires timely observation.
- **`HIGH`:** Severe single-organ derangement (e.g. SpO2 88% on room air, Shock Index 0.95).
- **`CRITICAL`:** Imminent cardiopulmonary arrest, severe shock, unresponsive GCS, or airway obstruction.

### 2.2 Axis 2: Physiological Trajectory
Measures the velocity and vector of clinical change over time:
- **`IMPROVING`:** Serial vitals and symptom markers normalizing following intervention.
- **`STABLE`:** Parameters unchanged over consecutive observation epochs.
- **`DETERIORATING`:** Progressive worsening (e.g. heart rate climbing, BP dropping over 30 minutes).
- **`RAPIDLY_DETERIORATING`:** Precipitous collapse requiring immediate escalation.
- **`UNCERTAIN`:** Insufficient serial timestamps to establish a mathematical slope.

### 2.3 Axis 3: Epistemic Uncertainty
Measures the confidence and completeness of the underlying data:
- **`LOW`:** All Tier 1 vitals measured; lab values verified; no contradictory sources.
- **`MODERATE`:** Non-critical history absent; minor OCR confidence warning ($< 0.80$).
- **`HIGH`:** Critical vital sign unmeasured or conflicting reports between patient and nurse.
- **`CRITICAL_UNCERTAINTY`:** Acute patient arrival with complete lack of history and unmeasured vitals.

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

```sql
CREATE TABLE clinical_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    evaluator_type VARCHAR(32) NOT NULL 
        CHECK (evaluator_type IN ('AI_MODEL', 'RULE_ENGINE', 'CLINICIAN')),
    evaluator_version VARCHAR(64) NOT NULL, -- e.g., 'caregraph-engine-v2.4'
    
    -- Axis 1: Risk
    risk_level VARCHAR(16) NOT NULL 
        CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    risk_score NUMERIC(4,3) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    risk_drivers JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., [{"factor": "SPO2_LOW", "val": 86}]
    
    -- Axis 2: Trajectory
    trajectory VARCHAR(32) NOT NULL 
        CHECK (trajectory IN ('IMPROVING', 'STABLE', 'DETERIORATING', 'RAPIDLY_DETERIORATING', 'UNCERTAIN')),
    trajectory_slope NUMERIC(5,3), -- Points/hour delta
    trajectory_indicators JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["HR_RISING_20BPM_PER_HOUR"]
    
    -- Axis 3: Uncertainty
    uncertainty_level VARCHAR(32) NOT NULL 
        CHECK (uncertainty_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL_UNCERTAINTY')),
    uncertainty_score NUMERIC(4,3) NOT NULL CHECK (uncertainty_score >= 0.0 AND uncertainty_score <= 1.0),
    uncertainty_drivers JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["MISSING_BP", "UNVERIFIED_OCR"]
    
    -- Recommended Triage Priority & Red Flags
    recommended_triage_priority VARCHAR(16) NOT NULL 
        CHECK (recommended_triage_priority IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    red_flags_detected JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["SHOCK_INDEX_ABOVE_1"]
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX ix_eval_case_active ON clinical_evaluations(case_id, is_active);
CREATE INDEX ix_eval_triage_priority ON clinical_evaluations(recommended_triage_priority);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE clinical_evaluations (
    evaluation_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TEXT NOT NULL,
    evaluator_type TEXT NOT NULL CHECK (evaluator_type IN ('AI_MODEL', 'RULE_ENGINE', 'CLINICIAN')),
    evaluator_version TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    risk_score REAL NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    risk_drivers TEXT NOT NULL DEFAULT '[]', -- JSON string
    trajectory TEXT NOT NULL CHECK (trajectory IN ('IMPROVING', 'STABLE', 'DETERIORATING', 'RAPIDLY_DETERIORATING', 'UNCERTAIN')),
    trajectory_slope REAL,
    trajectory_indicators TEXT NOT NULL DEFAULT '[]', -- JSON string
    uncertainty_level TEXT NOT NULL CHECK (uncertainty_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL_UNCERTAINTY')),
    uncertainty_score REAL NOT NULL CHECK (uncertainty_score >= 0.0 AND uncertainty_score <= 1.0),
    uncertainty_drivers TEXT NOT NULL DEFAULT '[]', -- JSON string
    recommended_triage_priority TEXT NOT NULL CHECK (recommended_triage_priority IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    red_flags_detected TEXT NOT NULL DEFAULT '[]', -- JSON string
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE INDEX ix_eval_case_active ON clinical_evaluations(case_id, is_active);
CREATE INDEX ix_eval_triage_priority ON clinical_evaluations(recommended_triage_priority);
```

---

## 5. Invariants Governing Risk, Trajectory, and Uncertainty

$$\begin{aligned}
\mathbf{Inv\ RTU\text{-}1} &: \quad \forall e \in \text{Evaluations}, \quad e.\text{uncertainty\_score} > 0.50 \implies e.\text{recommended\_triage\_priority} \in \{\text{'P1\_EMERGENCY'}, \text{'P2\_URGENT'}\} \\
& \quad \text{(High uncertainty automatically elevates priority to prevent delayed triage)} \\
\mathbf{Inv\ RTU\text{-}2} &: \quad e.\text{trajectory} = \text{'RAPIDLY\_DETERIORATING'} \implies e.\text{recommended\_triage\_priority} = \text{'P1\_EMERGENCY'} \\
\mathbf{Inv\ RTU\text{-}3} &: \quad \text{The three axes are computationally decoupled: changing uncertainty does NOT falsely compress risk.}
\end{aligned}$$
