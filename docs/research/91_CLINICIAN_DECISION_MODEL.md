# CLINOVA AI — Clinician Review, Modifications & Decision Data Model

> **Document ID:** `RES-91`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: Non-Destructive Clinician Control

Under Section 27 of the National Medical Commission (NMC) Regulations 2023, only a Registered Medical Practitioner (RMP) holds the legal authority to diagnose, prescribe, admit, operate on, or refer a patient.

When an RMP reviews an encounter on the **Doctor Review Workbench**, they execute one of three actions on each element:
1. **`VERIFY`:** Accept the AI extraction or nurse measurement as clinically accurate.
2. **`MODIFY`:** Alter a value (e.g. changing an algorithmic suspected diagnosis from "Bronchitis" to "Asthma Exacerbation", or altering an erroneous OCR medication dosage).
3. **`ADD`:** Attach bedside physical examination findings (auscultation, palpation) and definitive diagnostic orders.

### 1.1 Non-Destructive Modification Invariant
$$\text{A clinician modification MUST NEVER overwrite or destroy the original AI suggestion.}$$
Both the original machine recommendation and the clinician's override, along with the doctor's explicit medical rationale, are permanently and immutably preserved in `clinician_modifications`. This enables rigorous algorithmic auditing, medico-legal defense, and closed-loop continuous learning.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINICIAN DECISION SCHEMA                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── clinician_reviews (review_id PK, case_id FK)                         │
│    │     ├── [Assigned Priority, Diagnosis Impressions, Disposition Decision]│
│    │     │                                                                  │
│    │     └── clinician_modifications (modification_id PK, review_id FK)     │
│    │           └── [Field Path, Original AI Value, New Value, Rationale]     │
│    │                                                                        │
│    └── clinician_orders (order_id PK, review_id FK)                         │
│          └── [Prescriptions, Lab Orders, Nursing Instructions]              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `clinician_reviews` Table

```sql
CREATE TABLE clinician_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    triage_id UUID REFERENCES triage_notes(triage_id),
    reviewer_id UUID NOT NULL REFERENCES users(id),
    priority_assigned VARCHAR(16) NOT NULL 
        CHECK (priority_assigned IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    clinician_diagnosis_impressions JSONB NOT NULL DEFAULT '[]'::jsonb, -- Primary & secondary ICD-11 codes
    clinician_notes TEXT NOT NULL,
    physical_exam_findings JSONB NOT NULL DEFAULT '{}'::jsonb, -- { "chest": "bilateral wheeze", "cvs": "S1 S2 normal" }
    disposition_decision VARCHAR(32) NOT NULL 
        CHECK (disposition_decision IN ('DISCHARGE', 'ADMIT', 'REFER', 'OBSERVE', 'PROCEDURE', 'ESCALATE')),
    verification_state VARCHAR(16) NOT NULL DEFAULT 'CLINICIAN_VERIFIED'
        CHECK (verification_state IN ('CLINICIAN_VERIFIED', 'PROVISIONAL', 'REJECTED')),
    is_concordant_with_ai BOOLEAN NOT NULL DEFAULT TRUE,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_clin_reviews_case ON clinician_reviews(case_id);
CREATE INDEX ix_clin_reviews_reviewer ON clinician_reviews(reviewer_id);
CREATE INDEX ix_clin_reviews_disposition ON clinician_reviews(disposition_decision);
```

### 3.2 `clinician_modifications` Table (Audit of Overrides)

```sql
CREATE TABLE clinician_modifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES clinician_reviews(review_id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_path VARCHAR(128) NOT NULL, -- e.g., 'triage_notes.suspected_conditions', 'vitals.systolic_bp'
    original_value JSONB NOT NULL,    -- Exact snapshot of value before clinician modification
    new_value JSONB NOT NULL,         -- Value assigned by clinician
    modification_category VARCHAR(32) NOT NULL CHECK (modification_category IN (
        'DIAGNOSTIC_OVERRIDE', 'ACUITY_OVERRIDE', 'VITALS_CORRECTION', 'PRESCRIPTION_CHANGE', 'OTHER'
    )),
    clinical_justification TEXT NOT NULL,
    modified_by_clinician_id UUID NOT NULL REFERENCES users(id),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_modifications_review ON clinician_modifications(review_id);
CREATE INDEX ix_modifications_field ON clinician_modifications(field_path);
```

### 3.3 `clinician_orders` Table

```sql
CREATE TABLE clinician_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES clinician_reviews(review_id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    order_type VARCHAR(32) NOT NULL 
        CHECK (order_type IN ('MEDICATION', 'LAB_INVESTIGATION', 'RADIOLOGY', 'NURSING_PROCEDURE')),
    order_payload JSONB NOT NULL, -- Details: drug, dose, frequency, route, duration
    order_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
        CHECK (order_status IN ('ACTIVE', 'DISPENSED', 'COMPLETED', 'DISCONTINUED')),
    ordered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_orders_case ON clinician_orders(case_id);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE clinician_reviews (
    review_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    triage_id TEXT REFERENCES triage_notes(triage_id),
    reviewer_id TEXT NOT NULL REFERENCES users(id),
    priority_assigned TEXT NOT NULL CHECK (priority_assigned IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    clinician_diagnosis_impressions TEXT NOT NULL DEFAULT '[]', -- JSON string
    clinician_notes TEXT NOT NULL,
    physical_exam_findings TEXT NOT NULL DEFAULT '{}',          -- JSON string
    disposition_decision TEXT NOT NULL CHECK (disposition_decision IN ('DISCHARGE', 'ADMIT', 'REFER', 'OBSERVE', 'PROCEDURE', 'ESCALATE')),
    verification_state TEXT NOT NULL DEFAULT 'CLINICIAN_VERIFIED' CHECK (verification_state IN ('CLINICIAN_VERIFIED', 'PROVISIONAL', 'REJECTED')),
    is_concordant_with_ai INTEGER NOT NULL DEFAULT 1 CHECK (is_concordant_with_ai IN (0, 1)),
    reviewed_at TEXT NOT NULL
);

CREATE TABLE clinician_modifications (
    id TEXT PRIMARY KEY NOT NULL,
    review_id TEXT NOT NULL REFERENCES clinician_reviews(review_id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_path TEXT NOT NULL,
    original_value TEXT NOT NULL, -- JSON string
    new_value TEXT NOT NULL,      -- JSON string
    modification_category TEXT NOT NULL CHECK (modification_category IN (
        'DIAGNOSTIC_OVERRIDE', 'ACUITY_OVERRIDE', 'VITALS_CORRECTION', 'PRESCRIPTION_CHANGE', 'OTHER'
    )),
    clinical_justification TEXT NOT NULL,
    modified_by_clinician_id TEXT NOT NULL REFERENCES users(id),
    modified_at TEXT NOT NULL
);

CREATE TABLE clinician_orders (
    order_id TEXT PRIMARY KEY NOT NULL,
    review_id TEXT NOT NULL REFERENCES clinician_reviews(review_id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    order_type TEXT NOT NULL CHECK (order_type IN ('MEDICATION', 'LAB_INVESTIGATION', 'RADIOLOGY', 'NURSING_PROCEDURE')),
    order_payload TEXT NOT NULL, -- JSON string
    order_status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (order_status IN ('ACTIVE', 'DISPENSED', 'COMPLETED', 'DISCONTINUED')),
    ordered_at TEXT NOT NULL
);
```

---

## 5. Invariants Governing Clinician Reviews & Modifications

$$\begin{aligned}
\mathbf{Inv\ REV\text{-}1} &: \quad \forall r \in \text{ClinicianReviews}, \quad \text{User}(r.\text{reviewer\_id}).\text{role} = \text{'ROLE\_CLINICIAN'} \quad \text{(RMP Monopoly Law)} \\
\mathbf{Inv\ REV\text{-}2} &: \quad r.\text{priority\_assigned} \neq \text{TriageNotes}(r.\text{triage\_id}).\text{priority\_suggested} \\
& \quad \implies \exists m \in \text{Modifications}(r) \text{ s.t. } m.\text{field\_path} = \text{'priority'} \\
\mathbf{Inv\ REV\text{-}3} &: \quad \text{Clinician modifications are additive and immutable: } m.\text{original\_value} \text{ matches pre-review snapshot.}
\end{aligned}$$
