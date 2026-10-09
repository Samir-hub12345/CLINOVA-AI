# CLINOVA AI — Triage Note Synthesis & Prioritization Data Model

> **Document ID:** `RES-90`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Advisory Triage Synthesis

When clinical inputs, OCR extractions, and point-of-care nursing vitals are consolidated, CLINOVA AI synthesizes the **Master Triage Note** (`triage_notes`). 

Under the **Advisory-Only Invariant** (NMC Regulations 2023 & ICMR AI Ethics 2023):
$$\text{AI recommendations are non-prescriptive hypotheses; they CANNOT execute final clinical actions autonomously.}$$
Every synthesized triage note must carry an immutable advisory watermark, explicitly articulate suspected differential conditions with evidence pointers, surface detected red-flag physiological triggers, and position the patient in the multi-factor prioritized Doctor Review Queue.

---

## 2. Multi-Factor Prioritized Doctor Queue Algorithm

In high-volume public hospitals, a simple First-In-First-Out (FIFO) queue causes waiting-room deaths, while a static triage score starves lower-acuity patients who subsequently deteriorate unnoticed.

The data model supports dynamic queue sorting via the **Composite Priority Function** $P(t)$:

$$P(t) = \alpha \cdot \text{AcuityScore} + \beta \cdot \text{TrajectoryPenalty} + \gamma \cdot \text{WaitTimeDecay}(t) + \delta \cdot \text{UncertaintyPenalty}$$

Where:
- $\text{AcuityScore} \in \{1000 \text{ for P1}, 500 \text{ for P2}, 200 \text{ for P3}, 50 \text{ for P4}\}$.
- $\text{TrajectoryPenalty} = 250$ if trajectory is `DETERIORATING`.
- $\text{WaitTimeDecay}(t) = \min(300, \lambda \cdot \Delta t_{\text{wait}})$, dynamically escalating waiting cases before physiological collapse.
- $\text{UncertaintyPenalty} = 150 \cdot U_t$, prioritizing unverified patients for early doctor assessment.

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TRIAGE SYNTHESIS SCHEMA                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── triage_notes (triage_id PK, case_id FK)                              │
│    │     └── [Suggested Priority, Differential Conditions, Red Flags]       │
│    │                                                                        │
│    └── doctor_queue_entries (queue_id PK, case_id FK)                       │
│          └── [Dynamic Priority P(t), Wait Minutes, Department Routing]      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `triage_notes` Table

```sql
CREATE TABLE triage_notes (
    triage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    priority_suggested VARCHAR(16) NOT NULL 
        CHECK (priority_suggested IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    clinical_summary TEXT NOT NULL,
    suspected_conditions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., [{"condition": "NSTEMI", "probability": 0.82}]
    red_flags JSONB NOT NULL DEFAULT '[]'::jsonb,            -- e.g., ["Severe Hypoxia", "Shock Index > 1.0"]
    suggested_next_action VARCHAR(64) NOT NULL,              -- e.g., 'IMMEDIATE_ECG_AND_OXYGEN'
    acuity_tier VARCHAR(16) NOT NULL,
    generator_engine VARCHAR(64) NOT NULL,                  -- 'clinova-triage-qwen3-4b-v1'
    advisory_watermark_verified BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX ix_triage_notes_case ON triage_notes(case_id, is_active);
CREATE INDEX ix_triage_notes_priority ON triage_notes(priority_suggested);
```

### 4.2 `doctor_queue_entries` Table

```sql
CREATE TABLE doctor_queue_entries (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    department_code VARCHAR(32) NOT NULL DEFAULT 'GENERAL_OPD',
    priority_score NUMERIC(7,2) NOT NULL DEFAULT 50.00,
    queue_status VARCHAR(16) NOT NULL DEFAULT 'QUEUED'
        CHECK (queue_status IN ('QUEUED', 'BEING_REVIEWED', 'PARKED', 'COMPLETED', 'WALKOUT')),
    queued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    review_started_at TIMESTAMPTZ,
    assigned_clinician_id UUID REFERENCES users(id),
    wait_minutes_elapsed INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (NOW() - queued_at)) / 60
    ) STORED
);

CREATE INDEX ix_queue_facility_status ON doctor_queue_entries(facility_id, queue_status, priority_score DESC);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE triage_notes (
    triage_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    generated_at TEXT NOT NULL,
    priority_suggested TEXT NOT NULL CHECK (priority_suggested IN ('P1_EMERGENCY', 'P2_URGENT', 'P3_PRIORITY', 'P4_ROUTINE')),
    clinical_summary TEXT NOT NULL,
    suspected_conditions TEXT NOT NULL DEFAULT '[]', -- JSON string
    red_flags TEXT NOT NULL DEFAULT '[]',            -- JSON string
    suggested_next_action TEXT NOT NULL,
    acuity_tier TEXT NOT NULL,
    generator_engine TEXT NOT NULL,
    advisory_watermark_verified INTEGER NOT NULL DEFAULT 1 CHECK (advisory_watermark_verified IN (0, 1)),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE doctor_queue_entries (
    queue_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    department_code TEXT NOT NULL DEFAULT 'GENERAL_OPD',
    priority_score REAL NOT NULL DEFAULT 50.0,
    queue_status TEXT NOT NULL DEFAULT 'QUEUED' CHECK (queue_status IN ('QUEUED', 'BEING_REVIEWED', 'PARKED', 'COMPLETED', 'WALKOUT')),
    queued_at TEXT NOT NULL,
    review_started_at TEXT,
    assigned_clinician_id TEXT REFERENCES users(id)
);

CREATE INDEX ix_queue_facility_status ON doctor_queue_entries(facility_id, queue_status, priority_score DESC);
```

---

## 6. Invariants Governing Triage Notes & Doctor Queues

$$\begin{aligned}
\mathbf{Inv\ TRIAGE\text{-}1} &: \quad \forall n \in \text{TriageNotes}, \quad n.\text{advisory\_watermark\_verified} = \text{TRUE} \quad \text{(Advisory Watermark Law)} \\
\mathbf{Inv\ TRIAGE\text{-}2} &: \quad \text{Length}(n.\text{red\_flags}) > 0 \implies n.\text{priority\_suggested} \in \{\text{'P1\_EMERGENCY'}, \text{'P2\_URGENT'}\} \\
\mathbf{Inv\ TRIAGE\text{-}3} &: \quad \text{Cases with P1\_EMERGENCY priority preempt all lower-acuity cases in the clinician queue.}
\end{aligned}$$
