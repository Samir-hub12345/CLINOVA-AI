# CLINOVA AI — Missing Information & Epistemic Gap Data Model

> **Document ID:** `RES-87`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: The Zero-Imputation Law

In standard clinical algorithms, an empty input field is commonly treated as negative or normal (e.g. if allergy is blank, assume no allergy; if blood pressure is blank, assume normal hemodynamics). In high-volume emergency and rural outpatient care, **imputing missing data as normal kills patients**.

CLINOVA AI establishes the **Zero-Imputation Law**:
$$\text{Absence of evidence is NEVER evidence of absence.}$$
Every unmeasured vital sign, omitted historical allergy, or unelicited symptom is stored explicitly as an **Epistemic Gap** with status `UNKNOWN`. The system mathematically scores case completeness via the **Information Sufficiency Metric** ($S$), blocking cases from automatic doctor review if critical parameters are unknown.

---

## 2. Mathematical Information Sufficiency Model

As formalized in Phase 5 (`RES-63`), the sufficiency score $S$ is computed dynamically across all required clinical domains:

$$S = \frac{\sum_{i=1}^{N} w_i \cdot \delta_i}{\sum_{i=1}^{N} w_i}$$

Where:
- $\delta_i \in \{0, 1\}$ represents parameter presence:
  $$\delta_i = \begin{cases} 1 & \text{if parameter } i \text{ has epistemic status } \in \{\text{KNOWN}, \text{VERIFIED}\} \\ 0 & \text{if parameter } i \text{ has epistemic status } \in \{\text{UNKNOWN}, \text{CONFLICTING}, \text{UNRELIABLE}\} \end{cases}$$
- $w_i$ represents clinical importance weight:
  - **Tier 1 (CRITICAL):** $w_i = 3.0$ (Systolic BP, SpO2, Heart Rate, Respiratory Rate, AVPU, Severe Chest Pain / Shock symptoms).
  - **Tier 2 (IMPORTANT):** $w_i = 1.5$ (Temperature, Known Drug Allergies, Active Cardiac / Diabetic Medications).
  - **Tier 3 (ROUTINE):** $w_i = 0.5$ (Previous hospital discharge summaries, dietary habits, minor past surgeries).

### 2.1 The Sufficiency Hard Gate
$$\mathbf{Gate\ Rule:} \quad \text{Case advances to Doctor Queue } \iff \left( S \ge 0.85 \quad \land \quad \forall i \in \text{Tier 1}, \ \delta_i = 1 \right)$$
If $S < 0.85$ OR any Tier 1 vital sign is `UNKNOWN`, the state machine hard-diverts the case to `STATE_STAFF_DATA_PENDING` (Nurse Missing-Data Worklist).

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MISSING INFORMATION SCHEMA                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── missing_information_items (missing_item_id PK, case_id FK)           │
│    │     └── [Domain, Item Name, Clinical Importance, Status, Justification]│
│    │                                                                        │
│    └── information_sufficiency_evaluations (eval_id PK, case_id FK)         │
│          └── [Sufficiency Score S, Critical Gaps Count, Gate Status]        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `missing_information_items` Table

```sql
CREATE TABLE missing_information_items (
    missing_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    information_domain VARCHAR(32) NOT NULL CHECK (information_domain IN (
        'SYMPTOM', 'VITAL', 'MEDICAL_HISTORY', 'ALLERGY', 'MEDICATION', 'RED_FLAG'
    )),
    item_name VARCHAR(128) NOT NULL, -- e.g., 'systolic_blood_pressure', 'penicillin_allergy'
    canonical_concept_code VARCHAR(64),
    clinical_importance VARCHAR(16) NOT NULL DEFAULT 'IMPORTANT' CHECK (clinical_importance IN (
        'CRITICAL', 'IMPORTANT', 'ROUTINE', 'OPTIONAL'
    )),
    weight NUMERIC(3,1) NOT NULL DEFAULT 1.5,
    status VARCHAR(16) NOT NULL DEFAULT 'UNKNOWN' CHECK (status IN (
        'UNKNOWN', 'REQUESTED', 'ANSWERED', 'DEFERRED', 'UNRETRIEVABLE'
    )),
    clinical_justification TEXT NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by_actor_id UUID REFERENCES users(id),
    resolution_evidence_id UUID REFERENCES evidence_records(id)
);

CREATE INDEX ix_missing_items_case ON missing_information_items(case_id);
CREATE INDEX ix_missing_items_status ON missing_information_items(case_id, status);
CREATE INDEX ix_missing_items_critical ON missing_information_items(case_id, clinical_importance);
```

### 4.2 `information_sufficiency_evaluations` Table

```sql
CREATE TABLE information_sufficiency_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sufficiency_score NUMERIC(4,3) NOT NULL CHECK (sufficiency_score >= 0.0 AND sufficiency_score <= 1.0),
    total_weighted_points NUMERIC(6,2) NOT NULL,
    acquired_weighted_points NUMERIC(6,2) NOT NULL,
    critical_gaps_count INTEGER NOT NULL,
    important_gaps_count INTEGER NOT NULL,
    is_sufficient BOOLEAN NOT NULL,
    divert_to_nurse_worklist BOOLEAN NOT NULL,
    evaluated_by_engine_version VARCHAR(64) NOT NULL
);

CREATE INDEX ix_sufficiency_case ON information_sufficiency_evaluations(case_id, evaluated_at DESC);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE missing_information_items (
    missing_item_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    information_domain TEXT NOT NULL CHECK (information_domain IN (
        'SYMPTOM', 'VITAL', 'MEDICAL_HISTORY', 'ALLERGY', 'MEDICATION', 'RED_FLAG'
    )),
    item_name TEXT NOT NULL,
    canonical_concept_code TEXT,
    clinical_importance TEXT NOT NULL DEFAULT 'IMPORTANT' CHECK (clinical_importance IN (
        'CRITICAL', 'IMPORTANT', 'ROUTINE', 'OPTIONAL'
    )),
    weight REAL NOT NULL DEFAULT 1.5,
    status TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (status IN (
        'UNKNOWN', 'REQUESTED', 'ANSWERED', 'DEFERRED', 'UNRETRIEVABLE'
    )),
    clinical_justification TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    resolved_at TEXT,
    resolved_by_actor_id TEXT REFERENCES users(id),
    resolution_evidence_id TEXT REFERENCES evidence_records(id)
);

CREATE TABLE information_sufficiency_evaluations (
    evaluation_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TEXT NOT NULL,
    sufficiency_score REAL NOT NULL CHECK (sufficiency_score >= 0.0 AND sufficiency_score <= 1.0),
    total_weighted_points REAL NOT NULL,
    acquired_weighted_points REAL NOT NULL,
    critical_gaps_count INTEGER NOT NULL,
    important_gaps_count INTEGER NOT NULL,
    is_sufficient INTEGER NOT NULL CHECK (is_sufficient IN (0, 1)),
    divert_to_nurse_worklist INTEGER NOT NULL CHECK (divert_to_nurse_worklist IN (0, 1)),
    evaluated_by_engine_version TEXT NOT NULL
);
```

---

## 6. Invariants Governing Missing Information

$$\begin{aligned}
\mathbf{Inv\ GAP\text{-}1} &: \quad \forall g \in \text{MissingItems}, \quad g.\text{status} = \text{'ANSWERED'} \implies g.\text{resolved\_at} \neq \text{NULL} \\
\mathbf{Inv\ GAP\text{-}2} &: \quad \exists g \in \text{MissingItems}(c) \text{ with } (g.\text{clinical\_importance} = \text{'CRITICAL'} \land g.\text{status} \neq \text{'ANSWERED'}) \\
& \quad \implies \text{Cases}(c).\text{current\_state} \neq \text{STATE\_DOCTOR\_QUEUED} \\
\mathbf{Inv\ GAP\text{-}3} &: \quad \text{Zero-Imputation Law: Missing records never evaluate to default physiological values.}
\end{aligned}$$
