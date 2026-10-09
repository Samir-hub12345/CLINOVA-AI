# CLINOVA AI — Identity & Encounter Separation Data Model

> **Document ID:** `RES-80`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: Strict Entity Separation

In healthcare information architecture, conflating a human being's biological identity with a specific visit or acute crisis leads to catastrophic edge cases:
- Unconscious trauma victims are turned away or delayed at registration desks because "name and Aadhaar are required fields."
- Patients returning for routine care have their previous medical history overwritten or fragmented across duplicate records.
- Records merged haphazardly suffer from destructive data deletion, making medicolegal audits impossible.

To resolve these systemic failures, CLINOVA AI enforces **strict architectural separation** between five fundamental concepts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STRICT FIVE-WAY ENTITY SEPARATION                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. PATIENT IDENTITY (`patients`, `patient_identifiers`)                   │
│     └── The enduring biological individual across time and facilities.      │
│  2. ENCOUNTER (`encounters`)                                                │
│     └── The bounded operational episode of healthcare delivery at a facility.│
│  3. MASTER CASE (`cases`)                                                   │
│     └── The continuous clinical problem, evaluation, and trajectory graph.  │
│  4. FACILITY (`facilities`)                                                 │
│     └── The physical institution (PHC, CHC, DH) providing custody and care. │
│  5. ACTOR (`users`, `actors`)                                               │
│     └── The human staff member or system agent interacting with the record. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six Canonical Identity Modes

The CLINOVA data model provides explicit mathematical and schema-level mechanisms to handle all six operational identity scenarios:

### 2.1 Mode 1: Fully Identified Patient
- **Scenario:** The patient presents with verified national credentials (ABHA / Ayushman Bharat Health Account ID, Aadhaar-linked demographic token, or unique Hospital MRN).
- **Behavior:** Record created or fetched in `patients` with verified demographic details (`full_name`, `dob`, `gender`, `phone_hash`, `address`). The national ID is linked in `patient_identifiers` with `is_primary = TRUE` and `verification_status = 'VERIFIED'`.
- **Encounter Link:** `cases.patient_id` directly points to `patients.id`. `cases.is_anonymous = FALSE`.

### 2.2 Mode 2: Partially Identified Patient
- **Scenario:** Patient or caregiver states first name or village, but has no government ID, phone number, or known birthdate (e.g., elderly rural resident or migrant worker).
- **Behavior:** `patients` record is created with approximate age (`estimated_age_years`), stated name, and `is_partially_identified = TRUE`.
- **Encounter Link:** Linked directly to `cases.patient_id`. Gaps in official demographics do NOT block clinical progression or doctor review.

### 2.3 Mode 3: Emergency Anonymous Patient
- **Scenario:** Unconscious, delirious, or unassisted trauma victim arrives at emergency triage. Delaying care for identification is illegal under the Supreme Court *Paschim Banga* doctrine.
- **Behavior:** 
  1. Instant generation ($< 200\text{ms}$) of an **Anonymous Emergency Token**: `EMG-YYYYMMDD-XXXX` (e.g. `EMG-20261008-0104`).
  2. A temporary placeholder patient record is created with `is_anonymous = TRUE` and `synthetic_identifier = 'EMG-20261008-0104'`.
  3. `cases` is instantiated immediately with `is_anonymous = TRUE`, `intake_mode = 'EMERGENCY'`, and `acuity_tier = 'EMERGENCY'`.
  4. Clinical resuscitation proceeds without a single mandatory administrative demographic field.

### 2.4 Mode 4: Identity Discovered Later (Late Identity Binding)
- **Scenario:** The emergency patient is stabilized in the resuscitation bay or ICU. 6 hours later, a family member arrives with the patient's Aadhaar card and hospital records.
- **Behavior:**
  - The system MUST NOT delete the emergency case or spawn a new case.
  - The true patient profile (`patients`) is located or created.
  - An immutable **Identity Link Event** (`identity_link_events`) is recorded, cryptographically binding the emergency token `EMG-YYYYMMDD-XXXX` to the verified `patient_id`.
  - `cases.patient_id` is updated from the temporary placeholder to the permanent patient ID.
  - `cases.is_anonymous` is updated to `FALSE`.
  - All existing vital sign readings, medications, and resuscitation events remain perfectly intact under the SAME `case_id`.

### 2.5 Mode 5: Accidental Duplicate Identity Detection
- **Scenario:** A patient visits a PHC under a misspelled name ("Ramesh Pradhan"), and later visits the District Hospital registered as "Ramesh Kumar Pradhan", creating two distinct `patient_id` entries.
- **Behavior:**
  - The system's record linkage engine or hospital registrar flags a potential duplicate candidate based on phonetic name matching (Double Metaphone), age window ($\pm 2$ years), village code, and gender.
  - A pending duplicate flag is raised in `patient_merge_candidates`.

### 2.6 Mode 6: Identity Merge Architecture (Non-Destructive)
- **Scenario:** Hospital registrar or medical records officer confirms that `patient_A` and `patient_B` are the same physical individual.
- **Behavior:**
  - **Inviolable Law:** Data is NEVER destructively deleted.
  - The surviving record is designated as `canonical_patient_id` (e.g., `patient_A`).
  - The deprecated record (`patient_B`) is updated: `is_merged = TRUE`, `merged_into_patient_id = patient_A.id`.
  - A permanent audit log is written into `patient_merges`: records who authorized the merge, timestamp, and Merkle snapshot of both profiles.
  - Foreign keys in historical `cases` and `encounters` are updated to point to `patient_A.id`, but the historical `case_events` retain the original identifier in the event payload for auditability.
  - The deprecated ID acts as a persistent tombstone/alias: any future lookup for `patient_B` automatically resolves to `patient_A`.

---

## 3. Relational Schema Specification

### 3.1 `patients` Table Specification

| Column | Type (PG / SQLite) | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` / `TEXT(36)` | NO | `gen_random_uuid()` | Immutable primary key. |
| `synthetic_id` | `VARCHAR(32)` / `TEXT` | NO | None (Unique) | Internal human-readable identifier (e.g. `PT-2026-90412`). |
| `abha_id` | `VARCHAR(32)` / `TEXT` | YES | `NULL` | Indian National ABHA address (e.g. `user@abdm`). |
| `full_name` | `VARCHAR(128)` / `TEXT` | YES | `NULL` | Legal or stated full name. |
| `gender` | `VARCHAR(16)` / `TEXT` | NO | `'UNKNOWN'` | `'MALE'`, `'FEMALE'`, `'OTHER'`, `'UNKNOWN'`. |
| `dob` | `DATE` / `TEXT` | YES | `NULL` | Date of birth if known. |
| `estimated_age_years`| `INTEGER` / `INTEGER` | YES | `NULL` | Estimated age if DOB is unknown. |
| `phone_hash` | `VARCHAR(64)` / `TEXT` | YES | `NULL` | SHA-256 hash of mobile phone number (for lookup without storing raw PII). |
| `is_anonymous` | `BOOLEAN` / `INTEGER` | NO | `FALSE` | `TRUE` if created as an emergency anonymous placeholder. |
| `is_partially_identified`| `BOOLEAN` / `INTEGER` | NO | `FALSE` | `TRUE` if only partial demographic attributes are known. |
| `is_merged` | `BOOLEAN` / `INTEGER` | NO | `FALSE` | `TRUE` if this profile has been merged into another profile. |
| `merged_into_patient_id`| `UUID` / `TEXT(36)` | YES | `NULL` | Target canonical `patient_id` if merged. |
| `created_at` | `TIMESTAMPTZ` / `TEXT` | NO | `NOW()` | Profile creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` / `TEXT` | NO | `NOW()` | Profile update timestamp. |

### 3.2 `patient_identifiers` Table Specification

Supports arbitrary national, regional, and hospital-specific credential types without schema migrations.

```sql
CREATE TABLE patient_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    identifier_type VARCHAR(32) NOT NULL 
        CHECK (identifier_type IN ('ABHA_NUMBER', 'ABHA_ADDRESS', 'MRN', 'AADHAAR_HASH', 'EMERGENCY_TOKEN', 'DRIVING_LICENSE', 'VOTER_ID')),
    identifier_value VARCHAR(128) NOT NULL,
    issuing_authority VARCHAR(128) NOT NULL DEFAULT 'SYSTEM',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    verification_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED'
        CHECK (verification_status IN ('UNVERIFIED', 'VERIFIED', 'REVOKED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_patient_identifier UNIQUE (patient_id, identifier_type, identifier_value)
);
CREATE INDEX ix_patient_identifiers_lookup ON patient_identifiers(identifier_type, identifier_value);
```

### 3.3 `encounters` Table Specification

The physical or virtual care encounter, bounding the visit duration, admission location, and attending clinician.

```sql
CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_number VARCHAR(32) NOT NULL UNIQUE,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    attending_clinician_id UUID REFERENCES users(id) ON DELETE SET NULL,
    encounter_type VARCHAR(32) NOT NULL DEFAULT 'OUTPATIENT'
        CHECK (encounter_type IN ('OUTPATIENT', 'EMERGENCY', 'INPATIENT', 'FIELD_CAMP', 'TELECONSULT')),
    status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS'
        CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED')),
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_encounters_patient_id ON encounters(patient_id);
CREATE INDEX ix_encounters_facility_status ON encounters(facility_id, status);
```

### 3.4 `identity_link_events` Table Specification (Late Identity Discovery)

```sql
CREATE TABLE identity_link_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    anonymous_token VARCHAR(32) NOT NULL,
    linked_patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    authorized_by_actor_id UUID NOT NULL REFERENCES users(id),
    verification_document_type VARCHAR(32) NOT NULL,
    verification_notes TEXT,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_identity_link_case_id ON identity_link_events(case_id);
```

### 3.5 `patient_merges` Table Specification (Identity Deduplication)

```sql
CREATE TABLE patient_merges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    target_patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    authorized_by_actor_id UUID NOT NULL REFERENCES users(id),
    merge_reason TEXT NOT NULL,
    source_patient_snapshot JSONB NOT NULL,
    target_patient_snapshot JSONB NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_patient_merges_source ON patient_merges(source_patient_id);
CREATE INDEX ix_patient_merges_target ON patient_merges(target_patient_id);
```

---

## 4. SQLite Dialect Implementation

```sql
-- SQLite Schema for Identity and Encounter Management
CREATE TABLE patients (
    id TEXT PRIMARY KEY NOT NULL,
    synthetic_id TEXT NOT NULL UNIQUE,
    abha_id TEXT,
    full_name TEXT,
    gender TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (gender IN ('MALE', 'FEMALE', 'OTHER', 'UNKNOWN')),
    dob TEXT,
    estimated_age_years INTEGER,
    phone_hash TEXT,
    is_anonymous INTEGER NOT NULL DEFAULT 0 CHECK (is_anonymous IN (0, 1)),
    is_partially_identified INTEGER NOT NULL DEFAULT 0 CHECK (is_partially_identified IN (0, 1)),
    is_merged INTEGER NOT NULL DEFAULT 0 CHECK (is_merged IN (0, 1)),
    merged_into_patient_id TEXT REFERENCES patients(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE patient_identifiers (
    id TEXT PRIMARY KEY NOT NULL,
    patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('ABHA_NUMBER', 'ABHA_ADDRESS', 'MRN', 'AADHAAR_HASH', 'EMERGENCY_TOKEN', 'DRIVING_LICENSE', 'VOTER_ID')),
    identifier_value TEXT NOT NULL,
    issuing_authority TEXT NOT NULL DEFAULT 'SYSTEM',
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN ('UNVERIFIED', 'VERIFIED', 'REVOKED')),
    created_at TEXT NOT NULL,
    CONSTRAINT uq_patient_identifier UNIQUE (patient_id, identifier_type, identifier_value)
);

CREATE TABLE encounters (
    id TEXT PRIMARY KEY NOT NULL,
    encounter_number TEXT NOT NULL UNIQUE,
    patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    attending_clinician_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    encounter_type TEXT NOT NULL DEFAULT 'OUTPATIENT' CHECK (encounter_type IN ('OUTPATIENT', 'EMERGENCY', 'INPATIENT', 'FIELD_CAMP', 'TELECONSULT')),
    status TEXT NOT NULL DEFAULT 'IN_PROGRESS' CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED')),
    start_time TEXT NOT NULL,
    end_time TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE identity_link_events (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    anonymous_token TEXT NOT NULL,
    linked_patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    authorized_by_actor_id TEXT NOT NULL REFERENCES users(id),
    verification_document_type TEXT NOT NULL,
    verification_notes TEXT,
    linked_at TEXT NOT NULL
);

CREATE TABLE patient_merges (
    id TEXT PRIMARY KEY NOT NULL,
    source_patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    target_patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    authorized_by_actor_id TEXT NOT NULL REFERENCES users(id),
    merge_reason TEXT NOT NULL,
    source_patient_snapshot TEXT NOT NULL, -- JSON text
    target_patient_snapshot TEXT NOT NULL, -- JSON text
    merged_at TEXT NOT NULL
);
```

---

## 5. Invariants Governing Identity & Encounters

$$\begin{aligned}
\mathbf{Inv\ ID\text{-}1} &: \quad \forall p \in \text{Patients}, \quad p.\text{is\_merged} = \text{TRUE} \implies p.\text{merged\_into\_patient\_id} \neq \text{NULL} \\
\mathbf{Inv\ ID\text{-}2} &: \quad p.\text{is\_anonymous} = \text{TRUE} \implies \exists i \in \text{Identifiers} \text{ s.t. } i.\text{identifier\_type} = \text{'EMERGENCY\_TOKEN'} \\
\mathbf{Inv\ ID\text{-}3} &: \quad \text{Identity Merge is strictly idempotent and acyclic: } \\
& \quad \forall p_1, p_2, \quad \text{merged}(p_1 \to p_2) \implies \neg \text{merged}(p_2 \to p_1) \\
\mathbf{Inv\ ID\text{-}4} &: \quad \text{Late identity discovery updates } c.\text{patient\_id} \text{ without altering historical event payloads.}
\end{aligned}$$
