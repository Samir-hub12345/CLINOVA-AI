# CLINOVA AI — Inpatient Ward Admission & Operation Theatre Data Model

> **Document ID:** `RES-95`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Procedural & Inpatient Pathways

When an outpatient presentation requires escalation to institutional inpatient care or acute surgical intervention, traditional electronic systems spawn disconnected ward charts or paper operative notes.

In CLINOVA AI, both **Inpatient Ward Admissions** (Pathway C) and **Operation Theatre Procedures** (Pathway F) attach directly to the **SAME Master Case** (`case_id`).

### 1.1 Ward Admission Invariants
- Enforces two-party SBAR handoff sign-off between transferring outpatient staff and receiving ward nurse.
- Carries forward active medications, drug allergies, and isolation precautions without re-entry.

### 1.2 Surgical OT Invariants
- Ergonomic filtering: suppresses general outpatient text in favor of acute surgical safety parameters (airway Mallampati score, NPO fasting duration, blood cross-match hold, coagulation profile).
- Enforces the 3-phase **WHO Surgical Safety Checklist** (Sign In, Time Out, Sign Out) with dual surgeon/anesthesiologist sign-off.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WARD & OT PATHWAYS SCHEMA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── ward_admissions (admission_id PK, case_id FK)                        │
│    │     └── [Ward Type, Bed ID, SBAR Handoff, Dual Sign-off, Status]       │
│    │                                                                        │
│    └── surgical_procedures (procedure_id PK, case_id FK)                    │
│          └── [Surgeon ID, Anesthesiologist ID, Urgency, WHO Checklist, OT]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `ward_admissions` Table

```sql
CREATE TABLE ward_admissions (
    admission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    requested_ward_type VARCHAR(32) NOT NULL 
        CHECK (requested_ward_type IN ('GENERAL_MALE', 'GENERAL_FEMALE', 'STEP_DOWN', 'ICU', 'ISOLATION', 'PEDIATRIC')),
    admitting_clinician_id UUID NOT NULL REFERENCES users(id),
    admitting_diagnosis VARCHAR(256) NOT NULL,
    assigned_bed_id VARCHAR(32), -- e.g., 'WARD-3-BED-14'
    admission_checklist JSONB NOT NULL DEFAULT '{}'::jsonb,
    medication_orders JSONB NOT NULL DEFAULT '[]'::jsonb,
    special_precautions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ['FALL_RISK', 'CONTACT_ISOLATION']
    transferring_staff_id UUID REFERENCES users(id),
    receiving_ward_nurse_id UUID REFERENCES users(id),
    sbar_handoff_signed_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'REQUESTED'
        CHECK (status IN ('REQUESTED', 'BED_ASSIGNED', 'ADMITTED', 'DISCHARGED', 'TRANSFERRED', 'CANCELLED')),
    admitted_at TIMESTAMPTZ,
    discharged_at TIMESTAMPTZ
);

CREATE INDEX ix_ward_admissions_case ON ward_admissions(case_id);
CREATE INDEX ix_ward_admissions_bed ON ward_admissions(facility_id, assigned_bed_id);
```

### 3.2 `surgical_procedures` Table

```sql
CREATE TABLE surgical_procedures (
    procedure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    procedure_name VARCHAR(256) NOT NULL,
    procedure_code VARCHAR(32), -- ICD-10-PCS or CPT
    booking_urgency VARCHAR(32) NOT NULL DEFAULT 'URGENT_TODAY'
        CHECK (booking_urgency IN ('EMERGENCY_IMMEDIATE', 'URGENT_TODAY', 'ELECTIVE')),
    lead_surgeon_id UUID NOT NULL REFERENCES users(id),
    lead_anesthesiologist_id UUID REFERENCES users(id),
    npo_fasting_hours NUMERIC(4,1),
    blood_crossmatch_units_held INTEGER NOT NULL DEFAULT 0,
    who_checklist_signin JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Sign-In: patient ID, site, anesthesia safety
    who_checklist_timeout JSONB NOT NULL DEFAULT '{}'::jsonb, -- Time-Out: team intros, surgical risks, antibiotics
    who_checklist_signout JSONB NOT NULL DEFAULT '{}'::jsonb, -- Sign-Out: instrument count, specimen label
    dual_signoff_verified BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(32) NOT NULL DEFAULT 'BOOKED'
        CHECK (status IN ('BOOKED', 'IN_PREP', 'IN_PROCEDURE', 'POST_OP_RECOVERY', 'COMPLETED', 'CANCELLED')),
    booked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    incision_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX ix_surgical_procedures_case ON surgical_procedures(case_id);
CREATE INDEX ix_surgical_procedures_surgeon ON surgical_procedures(lead_surgeon_id);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE ward_admissions (
    admission_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    requested_ward_type TEXT NOT NULL CHECK (requested_ward_type IN ('GENERAL_MALE', 'GENERAL_FEMALE', 'STEP_DOWN', 'ICU', 'ISOLATION', 'PEDIATRIC')),
    admitting_clinician_id TEXT NOT NULL REFERENCES users(id),
    admitting_diagnosis TEXT NOT NULL,
    assigned_bed_id TEXT,
    admission_checklist TEXT NOT NULL DEFAULT '{}', -- JSON string
    medication_orders TEXT NOT NULL DEFAULT '[]',    -- JSON string
    special_precautions TEXT NOT NULL DEFAULT '[]',  -- JSON string
    transferring_staff_id TEXT REFERENCES users(id),
    receiving_ward_nurse_id TEXT REFERENCES users(id),
    sbar_handoff_signed_at TEXT,
    status TEXT NOT NULL DEFAULT 'REQUESTED' CHECK (status IN ('REQUESTED', 'BED_ASSIGNED', 'ADMITTED', 'DISCHARGED', 'TRANSFERRED', 'CANCELLED')),
    admitted_at TEXT,
    discharged_at TEXT
);

CREATE TABLE surgical_procedures (
    procedure_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    procedure_name TEXT NOT NULL,
    procedure_code TEXT,
    booking_urgency TEXT NOT NULL DEFAULT 'URGENT_TODAY' CHECK (booking_urgency IN ('EMERGENCY_IMMEDIATE', 'URGENT_TODAY', 'ELECTIVE')),
    lead_surgeon_id TEXT NOT NULL REFERENCES users(id),
    lead_anesthesiologist_id TEXT REFERENCES users(id),
    npo_fasting_hours REAL,
    blood_crossmatch_units_held INTEGER NOT NULL DEFAULT 0,
    who_checklist_signin TEXT NOT NULL DEFAULT '{}',  -- JSON string
    who_checklist_timeout TEXT NOT NULL DEFAULT '{}', -- JSON string
    who_checklist_signout TEXT NOT NULL DEFAULT '{}', -- JSON string
    dual_signoff_verified INTEGER NOT NULL DEFAULT 0 CHECK (dual_signoff_verified IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'BOOKED' CHECK (status IN ('BOOKED', 'IN_PREP', 'IN_PROCEDURE', 'POST_OP_RECOVERY', 'COMPLETED', 'CANCELLED')),
    booked_at TEXT NOT NULL,
    incision_at TEXT,
    completed_at TEXT
);
```

---

## 5. Invariants Governing Ward and OT Pathways

$$\begin{aligned}
\mathbf{Inv\ WARD\text{-}1} &: \quad w.\text{status} = \text{'ADMITTED'} \implies (w.\text{assigned\_bed\_id} \neq \text{NULL} \land w.\text{sbar\_handoff\_signed\_at} \neq \text{NULL}) \\
\mathbf{Inv\ OT\text{-}1} &: \quad p.\text{status} = \text{'IN\_PROCEDURE'} \implies (p.\text{dual\_signoff\_verified} = \text{TRUE} \land p.\text{incision\_at} \neq \text{NULL}) \\
\mathbf{Inv\ OT\text{-}2} &: \quad \text{The WHO Surgical Safety Checklist (Sign-In, Time-Out, Sign-Out) is mandatory and non-bypassable.}
\end{aligned}$$
