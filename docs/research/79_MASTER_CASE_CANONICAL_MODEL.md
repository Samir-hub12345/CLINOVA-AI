# CLINOVA AI — Master Case Canonical Data Model

> **Document ID:** `RES-79`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. The Single Continuous Master Case Invariant

The central foundation of CLINOVA AI is the **Single Continuous Master Case Invariant**:

$$\forall \text{ clinical encounter } e, \quad \exists ! \text{ canonical identifier } \mathbf{case\_id} \in \text{UUIDv4}$$

### 1.1 The Anti-Fragmentation Mandate
Traditional hospital information systems (HIS) suffer from severe record fragmentation. When a patient arrives, the reception desk opens a registration ticket; the triage nurse fills an isolated paper or digital triage form; the outpatient physician opens a separate OPD consultation note; if referred, the ambulance and referral desk create a new transfer voucher; if admitted, the ward creates an independent inpatient chart; and if operated on, the OT creates a surgical log.

This fragmentation causes lost clinical context, overlooked drug allergies, delayed resuscitation, and blind referrals. 

In CLINOVA AI, **all clinical and operational artifacts belong to the SAME continuous Master Case**. The intake audio, OCR scans, point-of-care vitals, doctor review, facility feasibility check, referral manifest, ward admission, OT checklist, and outcome resolution are all dynamically linked facets of a single Master Case anchored by `case_id`.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CANONICAL MASTER CASE ROOT                                 │
│                                  `case_id`: UUIDv4 (PRIMARY KEY)                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  ├── Identity & Context     ──> `patient_id` (FK), `encounter_id` (FK), `facility_id` (FK)   │
│  ├── Consent State          ──> `patient_consents` (FK: case_id)                            │
│  ├── Multimodal Media       ──> `audio_recordings`, `documents` (FK: case_id)               │
│  ├── OCR Extractions        ──> `document_ocr_pages`, `ocr_extracted_snippets` (FK: case_id)│
│  ├── Evidence Ledger        ──> `evidence_records`, `evidence_links` (FK: case_id)          │
│  ├── Objective Vitals       ──> `vital_readings`, `clinical_observations` (FK: case_id)     │
│  ├── Symptom Trajectory     ──> `symptoms`, `symptom_events` (FK: case_id)                  │
│  ├── Epistemic Gaps         ──> `missing_information_items` (FK: case_id)                   │
│  ├── Interactive Q&A        ──> `followup_questions`, `followup_answers` (FK: case_id)      │
│  ├── CAREGRAPH Evaluation   ──> `clinical_evaluations` [Risk, Traj, Uncertainty] (FK: case_id)│
│  ├── Triage Synthesis       ──> `triage_notes` (FK: case_id)                                │
│  ├── Clinician Review       ──> `clinician_reviews`, `clinician_modifications` (FK: case_id)│
│  ├── Facility Feasibility   ──> `care_requirements`, `feasibility_evaluations` (FK: case_id) │
│  ├── Orchestration Advisory ──> `orchestration_recommendations`, `care_pathways` (FK: case_id)│
│  ├── Referral & Transfer    ──> `referrals` (FK: case_id)                                   │
│  ├── Inpatient / OT Care    ──> `ward_admissions`, `surgical_procedures` (FK: case_id)      │
│  ├── Follow-Up & Outcome    ──> `appointments`, `case_outcomes` (FK: case_id)               │
│  ├── Event Sourcing Trail   ──> `case_events` [Append-Only Event Ledger] (FK: case_id)      │
│  └── State Machine History  ──> `case_state_transitions` [27 Canonical States] (FK: case_id) │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Case Entity Definition (`cases`)

The root relational entity `cases` manages the overall lifecycle, acuity summary, and state coordination for an encounter.

### 2.1 Relational Schema Attributes

| Column Name | Data Type (Postgres / SQLite) | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` / `TEXT(36)` | NO | `gen_random_uuid()` | Immutable canonical primary key (`case_id`). |
| `case_number` | `VARCHAR(32)` / `TEXT` | NO | None (Unique) | Human-readable identifier (e.g. `CAS-20261008-0042`). |
| `patient_id` | `UUID` / `TEXT(36)` | YES | `NULL` | Foreign key to `patients.id`. Nullable for emergency anonymous arrivals. |
| `encounter_id` | `UUID` / `TEXT(36)` | NO | None | Foreign key to `encounters.id`. Links physical encounter boundaries. |
| `originating_facility_id` | `UUID` / `TEXT(36)` | NO | None | Foreign key to `facilities.id`. Facility where case was created. |
| `current_facility_id` | `UUID` / `TEXT(36)` | NO | None | Facility currently holding physical custody of the patient. |
| `current_state` | `VARCHAR(32)` / `TEXT` | NO | `'STATE_NEW'` | One of 27 canonical state identifiers. |
| `previous_state` | `VARCHAR(32)` / `TEXT` | YES | `NULL` | Immediate preceding canonical state. |
| `state_version` | `INTEGER` / `INTEGER` | NO | `1` | Monotonically increasing version counter for optimistic concurrency. |
| `intake_mode` | `VARCHAR(32)` / `TEXT` | NO | `'REGULAR'` | `'REGULAR'` or `'EMERGENCY'`. |
| `acuity_tier` | `VARCHAR(16)` / `TEXT` | NO | `'ROUTINE'` | `'ROUTINE'`, `'PRIORITY'`, `'URGENT'`, `'EMERGENCY'`. |
| `risk_score` | `NUMERIC(4,3)` / `REAL` | YES | `NULL` | Composite physiological risk score $[0.000, 1.000]$. |
| `trajectory_slope` | `NUMERIC(5,3)` / `REAL`| YES | `NULL` | Rate of clinical change (points/hour). Negative = worsening. |
| `uncertainty_score` | `NUMERIC(4,3)` / `REAL`| YES | `NULL` | Epistemic uncertainty score $U_t \in [0.000, 1.000]$. |
| `presenting_complaint` | `TEXT` / `TEXT` | NO | `''` | Sanitized natural language complaint summary. |
| `primary_syndrome` | `VARCHAR(64)` / `TEXT` | YES | `NULL` | Suspected clinical syndrome tag (e.g., `ACUTE_CORONARY_SYNDROME`). |
| `required_bundle` | `VARCHAR(64)` / `TEXT` | YES | `NULL` | Resource bundle required (e.g., `RESUSCITATION_ICU_BUNDLE`). |
| `active_pathway` | `VARCHAR(32)` / `TEXT` | YES | `NULL` | Active disposition pathway (`ROUTINE`, `WARD`, `REFERRAL`, `OT`, `EMERGENCY`). |
| `is_anonymous` | `BOOLEAN` / `INTEGER` | NO | `FALSE` | Set to `TRUE` if created under emergency anonymous protocol. |
| `is_sealed` | `BOOLEAN` / `INTEGER` | NO | `FALSE` | Set to `TRUE` when transition to `STATE_CLOSED` occurs. Locks all edits. |
| `sealed_at` | `TIMESTAMPTZ` / `TEXT` | YES | `NULL` | Exact timestamp when cryptographic seal was applied. |
| `merkle_root_hash` | `VARCHAR(64)` / `TEXT` | YES | `NULL` | SHA-256 root hash of the complete case event history ledger. |
| `created_at` | `TIMESTAMPTZ` / `TEXT` | NO | `NOW()` | Timestamp of case instantiation. |
| `updated_at` | `TIMESTAMPTZ` / `TEXT` | NO | `NOW()` | Timestamp of most recent mutation. |

---

## 3. Relational DDL Specification

### 3.1 PostgreSQL / Supabase DDL

```sql
-- Canonical Master Case Table in PostgreSQL / Supabase
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(32) NOT NULL UNIQUE,
    patient_id UUID REFERENCES patients(id) ON DELETE RESTRICT,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    originating_facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    current_facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    current_state VARCHAR(32) NOT NULL DEFAULT 'STATE_NEW',
    previous_state VARCHAR(32),
    state_version INTEGER NOT NULL DEFAULT 1,
    intake_mode VARCHAR(32) NOT NULL DEFAULT 'REGULAR' 
        CHECK (intake_mode IN ('REGULAR', 'EMERGENCY')),
    acuity_tier VARCHAR(16) NOT NULL DEFAULT 'ROUTINE'
        CHECK (acuity_tier IN ('ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY')),
    risk_score NUMERIC(4,3) CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    trajectory_slope NUMERIC(5,3),
    uncertainty_score NUMERIC(4,3) CHECK (uncertainty_score >= 0.0 AND uncertainty_score <= 1.0),
    presenting_complaint TEXT NOT NULL DEFAULT '',
    primary_syndrome VARCHAR(64),
    required_bundle VARCHAR(64),
    active_pathway VARCHAR(32)
        CHECK (active_pathway IS NULL OR active_pathway IN ('ROUTINE', 'WARD', 'REFERRAL', 'OT', 'EMERGENCY', 'FOLLOW_UP')),
    is_anonymous BOOLEAN NOT NULL DEFAULT FALSE,
    is_sealed BOOLEAN NOT NULL DEFAULT FALSE,
    sealed_at TIMESTAMPTZ,
    merkle_root_hash VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indices for rapid lookup and triage queue queries
CREATE INDEX ix_cases_patient_id ON cases(patient_id);
CREATE INDEX ix_cases_encounter_id ON cases(encounter_id);
CREATE INDEX ix_cases_current_facility ON cases(current_facility_id);
CREATE INDEX ix_cases_state ON cases(current_state);
CREATE INDEX ix_cases_acuity ON cases(acuity_tier);
CREATE INDEX ix_cases_facility_state ON cases(current_facility_id, current_state);
CREATE INDEX ix_cases_created_at ON cases(created_at DESC);
```

### 3.2 SQLite Dialect DDL (Local Edge Mini-PC / WAL)

```sql
-- Canonical Master Case Table in SQLite (WAL Mode)
CREATE TABLE cases (
    id TEXT PRIMARY KEY NOT NULL, -- UUIDv4 string
    case_number TEXT NOT NULL UNIQUE,
    patient_id TEXT REFERENCES patients(id) ON DELETE RESTRICT,
    encounter_id TEXT NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    originating_facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    current_facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    current_state TEXT NOT NULL DEFAULT 'STATE_NEW',
    previous_state TEXT,
    state_version INTEGER NOT NULL DEFAULT 1,
    intake_mode TEXT NOT NULL DEFAULT 'REGULAR' CHECK (intake_mode IN ('REGULAR', 'EMERGENCY')),
    acuity_tier TEXT NOT NULL DEFAULT 'ROUTINE' CHECK (acuity_tier IN ('ROUTINE', 'PRIORITY', 'URGENT', 'EMERGENCY')),
    risk_score REAL CHECK (risk_score IS NULL OR (risk_score >= 0.0 AND risk_score <= 1.0)),
    trajectory_slope REAL,
    uncertainty_score REAL CHECK (uncertainty_score IS NULL OR (uncertainty_score >= 0.0 AND uncertainty_score <= 1.0)),
    presenting_complaint TEXT NOT NULL DEFAULT '',
    primary_syndrome TEXT,
    required_bundle TEXT,
    active_pathway TEXT CHECK (active_pathway IS NULL OR active_pathway IN ('ROUTINE', 'WARD', 'REFERRAL', 'OT', 'EMERGENCY', 'FOLLOW_UP')),
    is_anonymous INTEGER NOT NULL DEFAULT 0 CHECK (is_anonymous IN (0, 1)),
    is_sealed INTEGER NOT NULL DEFAULT 0 CHECK (is_sealed IN (0, 1)),
    sealed_at TEXT, -- ISO-8601 UTC
    merkle_root_hash TEXT,
    created_at TEXT NOT NULL, -- ISO-8601 UTC
    updated_at TEXT NOT NULL  -- ISO-8601 UTC
);

CREATE INDEX ix_cases_patient_id ON cases(patient_id);
CREATE INDEX ix_cases_encounter_id ON cases(encounter_id);
CREATE INDEX ix_cases_current_facility ON cases(current_facility_id);
CREATE INDEX ix_cases_state ON cases(current_state);
CREATE INDEX ix_cases_acuity ON cases(acuity_tier);
CREATE INDEX ix_cases_facility_state ON cases(current_facility_id, current_state);
CREATE INDEX ix_cases_created_at ON cases(created_at DESC);
```

---

## 4. Sub-Record Attachment Architecture

To guarantee the Single Master Case Invariant across the care continuum, all child entities enforce relational integrity back to `cases.id`:

```
                                  ┌──────────────┐
                                  │    cases     │
                                  │ (case_id PK) │
                                  └──────┬───────┘
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│  patient_consents│           │  audio_recordings  │          │    documents     │
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────────────────┘          └────────┬─────────┘
         │                               │                               │
         │                               │                     ┌────────▼─────────┐
         │                               │                     │document_ocr_pages│
         │                               │                     └────────┬─────────┘
         │                               │                               │
         │                               │                     ┌────────▼─────────┐
         │                               │                     │ocr_extracted_    │
         │                               │                     │   snippets       │
         │                               │                     └──────────────────┘
         │                               │                               │
         ├───────────────────────────────┼───────────────────────────────┤
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│  vital_readings  │           │clinical_observat'ns│          │     symptoms     │
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────────────────┘          └────────┬─────────┘
         │                               │                               │
         │                               │                     ┌────────▼─────────┐
         │                               │                     │  symptom_events  │
         │                               │                     └──────────────────┘
         │                               │                               │
         ├───────────────────────────────┼───────────────────────────────┤
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│missing_info_items│           │ followup_questions │          │clinical_evaluat's│
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────┬───────────┘          └──────────────────┘
                                         │                               │
                               ┌────────▼──────────┐                     │
                               │ followup_answers  │                     │
                               └───────────────────┘                     │
         ├───────────────────────────────┼───────────────────────────────┤
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│   triage_notes   │           │ clinician_reviews  │          │care_requirements │
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────┬───────────┘          └────────┬─────────┘
                                         │                               │
                               ┌────────▼──────────┐           ┌────────▼─────────┐
                               │clinician_modificat│           │feasibility_evals │
                               └───────────────────┘           └──────────────────┘
         ├───────────────────────────────┼───────────────────────────────┤
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│orchestration_recs│           │   care_pathways    │          │    referrals     │
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────────────────┘          └──────────────────┘
         │                               │                               │
         ├───────────────────────────────┼───────────────────────────────┤
         │                               │                               │
┌────────▼─────────┐           ┌─────────▼──────────┐          ┌────────▼─────────┐
│ ward_admissions  │           │surgical_procedures │          │  case_outcomes   │
│  (case_id FK)    │           │  (case_id FK)      │          │  (case_id FK)    │
└──────────────────┘           └────────────────────┘          └──────────────────┘
         │                               │                               │
         └───────────────────────────────┼───────────────────────────────┘
                                         │
                               ┌─────────▼──────────┐
                               │    case_events     │
                               │  (case_id FK)      │
                               │ [Append-Only Log]  │
                               └────────────────────┘
```

### 4.2 Sub-Record Attachment Invariant Rules

1. **Direct Root Linkage:** Every child record representing an clinical finding, diagnostic observation, decision, or logistic event MUST hold an indexed foreign key directly to `cases(id)`.
2. **Cascade Restrictions (`ON DELETE RESTRICT`):** `cases` records must NEVER be deleted if child clinical data exists. In local demo testing, cases are archived, never physically dropped.
3. **Session Exclusivity:** Only one clinician or staff actor may mutate clinical review state on a `case_id` simultaneously, governed by optimistic concurrency control (`state_version`).
4. **No Sidecar Enounters:** When a patient is transferred from a rural PHC to a District Hospital, the destination hospital DOES NOT create a new case. They intake the **SAME `case_id`**, updating `cases.current_facility_id` to the District Hospital UUID and transitioning state from `STATE_TRANSFER_IN_TRANSIT` to `STATE_OUTCOME_PENDING` or `STATE_WARD_ADMITTED`.

---

## 5. Master Clinical Dossier JSON Schema

For inter-facility transmission, offline caching in IndexedDB, and API serialization, the Master Case provides a standardized JSON export format:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ClinovaMasterCaseDossier",
  "type": "object",
  "required": [
    "case_id",
    "case_number",
    "encounter_id",
    "originating_facility_id",
    "current_state",
    "state_version",
    "acuity_tier",
    "created_at"
  ],
  "properties": {
    "case_id": { "type": "string", "format": "uuid" },
    "case_number": { "type": "string" },
    "patient_id": { "type": ["string", "null"], "format": "uuid" },
    "encounter_id": { "type": "string", "format": "uuid" },
    "originating_facility_id": { "type": "string", "format": "uuid" },
    "current_facility_id": { "type": "string", "format": "uuid" },
    "current_state": { "type": "string" },
    "state_version": { "type": "integer", "minimum": 1 },
    "intake_mode": { "type": "string", "enum": ["REGULAR", "EMERGENCY"] },
    "acuity_tier": { "type": "string", "enum": ["ROUTINE", "PRIORITY", "URGENT", "EMERGENCY"] },
    "risk_score": { "type": ["number", "null"], "minimum": 0.0, "maximum": 1.0 },
    "trajectory_slope": { "type": ["number", "null"] },
    "uncertainty_score": { "type": ["number", "null"], "minimum": 0.0, "maximum": 1.0 },
    "presenting_complaint": { "type": "string" },
    "primary_syndrome": { "type": ["string", "null"] },
    "consent": { "$ref": "#/$defs/ConsentRecord" },
    "multimodal_inputs": { "$ref": "#/$defs/MultimodalInputs" },
    "vitals_series": { "type": "array", "items": { "$ref": "#/$defs/VitalReading" } },
    "symptoms": { "type": "array", "items": { "$ref": "#/$defs/SymptomRecord" } },
    "missing_information": { "type": "array", "items": { "$ref": "#/$defs/MissingInfoItem" } },
    "triage_summary": { "$ref": "#/$defs/TriageNote" },
    "clinician_review": { "$ref": "#/$defs/ClinicianReview" },
    "orchestration": { "$ref": "#/$defs/OrchestrationRecommendation" },
    "active_pathway_record": { "type": ["object", "null"] },
    "outcome": { "$ref": "#/$defs/CaseOutcome" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 6. Mathematical Invariants of the Master Case

$$\begin{aligned}
\mathbf{Inv\ 1} &: \quad \forall c \in \text{Cases}, \quad c.\text{state\_version} \ge 1 \quad \land \quad c.\text{state\_version} \in \mathbb{N} \\
\mathbf{Inv\ 2} &: \quad c.\text{is\_sealed} = \text{TRUE} \implies \left( c.\text{current\_state} = \text{STATE\_CLOSED} \quad \land \quad c.\text{merkle\_root\_hash} \neq \text{NULL} \right) \\
\mathbf{Inv\ 3} &: \quad \forall r \in \text{ChildRecords}, \quad r.\text{case\_id} = c.\text{id} \quad \text{(Strict Single Master Case)} \\
\mathbf{Inv\ 4} &: \quad c.\text{is\_anonymous} = \text{TRUE} \iff c.\text{patient\_id} = \text{NULL} \quad \lor \quad \text{Patient}(c.\text{patient\_id}).\text{is\_anonymous} = \text{TRUE}
\end{aligned}$$
