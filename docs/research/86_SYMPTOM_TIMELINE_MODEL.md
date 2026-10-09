# CLINOVA AI — Symptom Timeline & Trajectory Data Model

> **Document ID:** `RES-86`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Temporal Dynamics of Symptoms

In clinical medicine, symptoms are never static labels. A "cough" lasting 2 hours after choking has an entirely different differential diagnosis from a "cough" progressing over 3 months with hemoptysis and night sweats.

CLINOVA AI models symptoms as **Chronological Trajectory Entities**:
1. **Precise & Approximate Temporal Anchors:** Supports exact datetime onsets as well as vernacular colloquial anchors (*"started 3 days ago after dinner"*, *"last night around 2 AM"*).
2. **Trajectory Classification:** Tracks whether the symptom is `IMPROVING`, `STABLE`, `WORSENING`, or `FLUCTUATING`.
3. **Modulating Factors:** Formally records provoking triggers, relieving factors, and associated systemic manifestations.
4. **Epistemic Traceability:** Retains the exact extraction confidence and source modality.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYMPTOM TIMELINE SCHEMA                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── symptoms (symptom_id PK, case_id FK)                                 │
│    │     └── [Canonical Concept, Severity, Trajectory, Onset Anchor]        │
│    │                                                                        │
│    └── symptom_progression_events (event_id PK, symptom_id FK)              │
│          └── [Serial Severity Changes, Intervention Response, Fluctuation] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `symptoms` Table

```sql
CREATE TABLE symptoms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    symptom_name VARCHAR(128) NOT NULL,
    canonical_concept_code VARCHAR(64), -- SNOMED CT Concept ID (e.g., '29857009' for Chest Pain)
    anatomical_site VARCHAR(64),
    onset_exact TIMESTAMPTZ,
    onset_approximate_text VARCHAR(128), -- e.g., '3 days ago', 'after evening meal'
    duration_hours NUMERIC(6,1),
    severity VARCHAR(16) NOT NULL DEFAULT 'MODERATE'
        CHECK (severity IN ('MILD', 'MODERATE', 'SEVERE', 'CRITICAL')),
    trajectory VARCHAR(16) NOT NULL DEFAULT 'STABLE'
        CHECK (trajectory IN ('IMPROVING', 'STABLE', 'WORSENING', 'FLUCTUATING', 'UNCERTAIN')),
    triggers JSONB NOT NULL DEFAULT '[]'::jsonb,           -- e.g., ['EXERTION', 'COLD_WEATHER']
    relieving_factors JSONB NOT NULL DEFAULT '[]'::jsonb,  -- e.g., ['REST', 'NITROGLYCERIN']
    associated_symptoms JSONB NOT NULL DEFAULT '[]'::jsonb,-- e.g., ['DIAPHORESIS', 'NAUSEA']
    source_type VARCHAR(32) NOT NULL DEFAULT 'PATIENT_REPORTED'
        CHECK (source_type IN ('PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 'CLINICIAN_VERIFIED', 'AI_INFERRED')),
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 
        CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    is_chief_complaint BOOLEAN NOT NULL DEFAULT FALSE,
    is_red_flag BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_symptoms_case_chief ON symptoms(case_id, is_chief_complaint);
CREATE INDEX ix_symptoms_red_flag ON symptoms(case_id, is_red_flag);
CREATE INDEX ix_symptoms_concept ON symptoms(canonical_concept_code);
```

### 3.2 `symptom_progression_events` Table

```sql
CREATE TABLE symptom_progression_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symptom_id UUID NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity_at_epoch VARCHAR(16) NOT NULL
        CHECK (severity_at_epoch IN ('MILD', 'MODERATE', 'SEVERE', 'CRITICAL', 'RESOLVED')),
    clinical_note TEXT,
    recorded_by_actor_id UUID NOT NULL REFERENCES users(id)
);

CREATE INDEX ix_symptom_progression ON symptom_progression_events(symptom_id, observed_at ASC);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE symptoms (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    symptom_name TEXT NOT NULL,
    canonical_concept_code TEXT,
    anatomical_site TEXT,
    onset_exact TEXT, -- ISO-8601 UTC
    onset_approximate_text TEXT,
    duration_hours REAL,
    severity TEXT NOT NULL DEFAULT 'MODERATE' CHECK (severity IN ('MILD', 'MODERATE', 'SEVERE', 'CRITICAL')),
    trajectory TEXT NOT NULL DEFAULT 'STABLE' CHECK (trajectory IN ('IMPROVING', 'STABLE', 'WORSENING', 'FLUCTUATING', 'UNCERTAIN')),
    triggers TEXT NOT NULL DEFAULT '[]', -- JSON string
    relieving_factors TEXT NOT NULL DEFAULT '[]', -- JSON string
    associated_symptoms TEXT NOT NULL DEFAULT '[]', -- JSON string
    source_type TEXT NOT NULL DEFAULT 'PATIENT_REPORTED' CHECK (source_type IN ('PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 'CLINICIAN_VERIFIED', 'AI_INFERRED')),
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    is_chief_complaint INTEGER NOT NULL DEFAULT 0 CHECK (is_chief_complaint IN (0, 1)),
    is_red_flag INTEGER NOT NULL DEFAULT 0 CHECK (is_red_flag IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE symptom_progression_events (
    id TEXT PRIMARY KEY NOT NULL,
    symptom_id TEXT NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    observed_at TEXT NOT NULL,
    severity_at_epoch TEXT NOT NULL CHECK (severity_at_epoch IN ('MILD', 'MODERATE', 'SEVERE', 'CRITICAL', 'RESOLVED')),
    clinical_note TEXT,
    recorded_by_actor_id TEXT NOT NULL REFERENCES users(id)
);
```

---

## 5. Invariants Governing Symptom Timelines

$$\begin{aligned}
\mathbf{Inv\ SYMP\text{-}1} &: \quad \forall c \in \text{Cases}, \quad \text{Count}(\{s \in \text{Symptoms}(c) : s.\text{is\_chief\_complaint} = \text{TRUE}\}) \le 3 \\
\mathbf{Inv\ SYMP\text{-}2} &: \quad s.\text{is\_red\_flag} = \text{TRUE} \implies \text{Elevation of uncertainty and triage priority to at least } \text{'P2\_URGENT'} \\
\mathbf{Inv\ SYMP\text{-}3} &: \quad (s.\text{onset\_exact} = \text{NULL}) \implies (s.\text{onset\_approximate\_text} \neq \text{NULL}) \quad \text{(At least one temporal anchor required)}
\end{aligned}$$
