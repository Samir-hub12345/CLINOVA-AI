# CLINOVA AI — Appointments, Follow-Up & Closed-Loop Outcome Data Model

> **Document ID:** `RES-96`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: The Closed-Loop Reality Principle

Standard healthcare algorithms terminate their lifecycle the moment a triage score or diagnosis is generated. They never discover whether the patient got better, deteriorated, suffered an adverse drug reaction, or died. Without recording real-world outcomes, machine learning models and clinical rules cannot undergo continuous calibration.

As specified in Phase 5 (`RES-71`), CLINOVA AI formalizes the **Closed-Loop Outcome Architecture**, decoupling:
$$\mathbf{Planned\ Advice} \neq \mathbf{Actual\ Clinician\ Decision} \neq \mathbf{Actual\ Care\ Action} \neq \mathbf{Real\text{-}World\ Outcome}$$

All outpatient revisit appointments (`appointments`) and definitive clinical endpoints (`case_outcomes`) attach directly to the **SAME continuous Master Case** (`case_id`).

---

## 2. Standardized Clinical Outcome Taxonomy

Clinical endpoints are categorized into seven discrete medicolegal categories:

| Outcome Type | Clinical Definition | Operational Treatment |
| :--- | :--- | :--- |
| `RESOLVED` | Full recovery; patient asymptomatic; no active treatment required. | Case cleanly transitioned to `STATE_CLOSED`. |
| `IMPROVED` | Significant clinical progress; outpatient continuation required. | Linked to scheduled outpatient revisit. |
| `UNCHANGED` | Symptoms persist without acute decompensation; regimen review. | Escalated for secondary diagnostic audit. |
| `DETERIORATED` | Worsening physiology; requires higher acuity pathway escalation. | Triggers high-priority clinical review alert. |
| `TRANSFERRED_OUT` | Custody successfully handed over to destination referral hospital. | Bound to closed referral loop. |
| `LAMA` | Left Against Medical Advice; statutory refusal signed. | Statutory risk waiver recorded in audit log. |
| `EXPIRED` | Patient deceased; resuscitation attempted or terminal care. | Mandatory clinical mortality review audit triggered. |

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    APPOINTMENTS & CLOSED-LOOP OUTCOMES SCHEMA               │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── appointments (appointment_id PK, case_id FK)                         │
│    │     └── [Scheduled Date, Type (ROUTINE, SPECIALIST, LAB), Status]      │
│    │                                                                        │
│    └── case_outcomes (outcome_id PK, case_id FK)                            │
│          └── [Outcome Type, Alignment Delta, Disposition Summary, Feedback]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `appointments` Table

```sql
CREATE TABLE appointments (
    appointment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    patient_id UUID REFERENCES patients(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    scheduled_date DATE NOT NULL,
    time_slot_window VARCHAR(32) NOT NULL DEFAULT 'MORNING_OPD'
        CHECK (time_slot_window IN ('MORNING_OPD', 'AFTERNOON_OPD', 'SPECIALIST_CLINIC')),
    appointment_type VARCHAR(32) NOT NULL DEFAULT 'ROUTINE_FOLLOWUP'
        CHECK (appointment_type IN ('ROUTINE_FOLLOWUP', 'SPECIALIST_CONSULT', 'LAB_REVIEW', 'PROCEDURE_FOLLOWUP')),
    status VARCHAR(16) NOT NULL DEFAULT 'SCHEDULED'
        CHECK (status IN ('SCHEDULED', 'ATTENDED', 'MISSED', 'RESCHEDULED', 'CANCELLED')),
    booked_by_actor_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_appointments_case ON appointments(case_id);
CREATE INDEX ix_appointments_facility_date ON appointments(facility_id, scheduled_date, status);
```

### 4.2 `case_outcomes` Table

```sql
CREATE TABLE case_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    outcome_type VARCHAR(32) NOT NULL CHECK (outcome_type IN (
        'RESOLVED', 'IMPROVED', 'UNCHANGED', 'DETERIORATED', 
        'TRANSFERRED_OUT', 'LEFT_AGAINST_MEDICAL_ADVICE', 'EXPIRED'
    )),
    clinical_disposition_summary TEXT NOT NULL,
    planned_vs_actual_alignment VARCHAR(16) NOT NULL DEFAULT 'ALIGNED'
        CHECK (planned_vs_actual_alignment IN ('ALIGNED', 'MODIFIED', 'DIVERGENT')),
    alignment_divergence_reason TEXT,
    diagnostic_concordance BOOLEAN NOT NULL DEFAULT TRUE, -- Clinician diagnosis matches final discharge diagnosis
    feedback_notes TEXT,
    recorded_by_actor_id UUID NOT NULL REFERENCES users(id),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_outcomes_case ON case_outcomes(case_id);
CREATE INDEX ix_outcomes_type ON case_outcomes(outcome_type);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE appointments (
    appointment_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    patient_id TEXT REFERENCES patients(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    scheduled_date TEXT NOT NULL, -- YYYY-MM-DD
    time_slot_window TEXT NOT NULL DEFAULT 'MORNING_OPD' CHECK (time_slot_window IN ('MORNING_OPD', 'AFTERNOON_OPD', 'SPECIALIST_CLINIC')),
    appointment_type TEXT NOT NULL DEFAULT 'ROUTINE_FOLLOWUP' CHECK (appointment_type IN ('ROUTINE_FOLLOWUP', 'SPECIALIST_CONSULT', 'LAB_REVIEW', 'PROCEDURE_FOLLOWUP')),
    status TEXT NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'ATTENDED', 'MISSED', 'RESCHEDULED', 'CANCELLED')),
    booked_by_actor_id TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE TABLE case_outcomes (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    outcome_type TEXT NOT NULL CHECK (outcome_type IN (
        'RESOLVED', 'IMPROVED', 'UNCHANGED', 'DETERIORATED', 
        'TRANSFERRED_OUT', 'LEFT_AGAINST_MEDICAL_ADVICE', 'EXPIRED'
    )),
    clinical_disposition_summary TEXT NOT NULL,
    planned_vs_actual_alignment TEXT NOT NULL DEFAULT 'ALIGNED' CHECK (planned_vs_actual_alignment IN ('ALIGNED', 'MODIFIED', 'DIVERGENT')),
    alignment_divergence_reason TEXT,
    diagnostic_concordance INTEGER NOT NULL DEFAULT 1 CHECK (diagnostic_concordance IN (0, 1)),
    feedback_notes TEXT,
    recorded_by_actor_id TEXT NOT NULL REFERENCES users(id),
    recorded_at TEXT NOT NULL
);
```

---

## 6. Invariants Governing Outcomes

$$\begin{aligned}
\mathbf{Inv\ OUT\text{-}1} &: \quad \forall c \in \text{Cases}, \quad c.\text{current\_state} = \text{STATE\_RESOLVED} \implies \exists ! o \in \text{Outcomes} \text{ s.t. } o.\text{case\_id} = c.\text{id} \\
\mathbf{Inv\ OUT\text{-}2} &: \quad o.\text{outcome\_type} = \text{'EXPIRED'} \implies \text{Mandatory Quality Audit Flag Triggered} \\
\mathbf{Inv\ OUT\text{-}3} &: \quad o.\text{planned\_vs\_actual\_alignment} = \text{'DIVERGENT'} \implies o.\text{alignment\_divergence\_reason} \neq \text{NULL}
\end{aligned}$$
