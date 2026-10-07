# CLINOVA AI — Relational & Domain Data Model

> **Document ID:** `DOC-14`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Data Modeling Architecture

CLINOVA AI employs a hybrid persistence strategy designed for extreme clinical resilience:
1. **Core Relational Schema (PostgreSQL / SQLite):** Stores structured administrative, encounter, audit, and facility metadata with full ACID guarantees.
2. **Dynamic In-Memory Graph (CareGraph & FacilityGraph):** Computes multi-hop topological distances, trajectory vectors, and feasibility matching in memory with serialized JSON snapshots persisted to the relational database.

---

## 2. Entity Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     User        │       │   Facility      │       │ FacilityCapab.  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ email           │       │ name            │       │ facility_id(FK) │
│ role (Enum)     │       │ tier (Enum)     │       │ capability_code │
│ facility_id(FK) ├──────>│ bed_capacity    │<──────┤ is_operational  │
└─────────────────┘       │ ed_wait_time    │       └─────────────────┘
                          └────────┬────────┘
                                   │
                                   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Patient (Syn)  │       │     Case        │       │    Consent      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ synthetic_id    │<──────┤ patient_id (FK) │       │ case_id (FK)    │
│ age_bracket     │       │ facility_id(FK) │       │ consent_granted │
│ biological_sex  │       │ status (FSM)    │       │ timestamp       │
└─────────────────┘       │ acuity_tier     │       └─────────────────┘
                          │ risk_score      │
                          │ uncertainty     │
                          └────────┬────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  VitalReading   │       │   SymptomNode   │       │ EvidenceRecord  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ case_id (FK)    │       │ case_id (FK)    │       │ case_id (FK)    │
│ hr, bp_sys, dia │       │ symptom_code    │       │ provenance_type │
│ spo2, rr, temp  │       │ severity (1-10) │       │ raw_uri         │
│ recorded_at     │       │ onset_time      │       │ confidence_score│
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ ClinicianDecis. │       │   Referral      │       │   CaseOutcome   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ case_id (FK)    │       │ case_id (FK)    │       │ case_id (FK)    │
│ clinician_id(FK)│       │ from_fac_id(FK) │       │ disposition     │
│ action_type     │       │ to_fac_id (FK)  │       │ final_condition │
│ decision_type   │       │ required_bundle │       │ recorded_at     │
│ override_reason │       │ sbar_summary    │       └─────────────────┘
└─────────────────┘       └─────────────────┘
```

---

## 3. Relational Table Definitions

### 3.1 `patients` (Synthetic Cohort)
- `id` (UUID, Primary Key)
- `synthetic_id` (VARCHAR(32), Unique, Indexed) — e.g. `SYN-PT-8821`
- `age_bracket` (VARCHAR(16)) — e.g. `40-49`, `60-69` (Minimizes re-identification risk)
- `biological_sex` (VARCHAR(8)) — `MALE`, `FEMALE`, `OTHER`
- `created_at` (TIMESTAMP WITH TIME ZONE, Default: NOW)

### 3.2 `cases` (Encounter State Machine)
- `id` (UUID, Primary Key)
- `case_number` (VARCHAR(32), Unique)
- `patient_id` (UUID, Foreign Key -> `patients.id`)
- `facility_id` (UUID, Foreign Key -> `facilities.id`)
- `status` (VARCHAR(32), Indexed) — State Machine Enum (`NEW`, `INTAKE`, `PROCESSING`, `REVIEW_REQUIRED`, `TRIAGED`, `CLINICIAN_REVIEW`, `DECISION`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`, `TRANSFER_PENDING`, `TRANSFER`, `COMPLETED`, `OUTCOME`)
- `acuity_tier` (VARCHAR(16)) — `ROUTINE`, `MODERATE`, `URGENT`, `CRITICAL`
- `risk_score` (FLOAT) — Range $[0.0, 1.0]$
- `trajectory_slope` (FLOAT) — Change per hour ($\Delta R$)
- `uncertainty_score` (FLOAT) — Range $[0.0, 1.0]$
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

### 3.3 `evidence_records` (Data Provenance)
- `id` (UUID, Primary Key)
- `case_id` (UUID, Foreign Key -> `cases.id`)
- `provenance_type` (VARCHAR(32)) — `PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `CLINICIAN_VERIFIED`, `AI_INFERRED`, `SYSTEM_DERIVED`
- `source_filename` (VARCHAR(255), Nullable)
- `extracted_payload` (JSONB) — Raw extracted entities and bounding boxes
- `confidence_score` (FLOAT) — Range $[0.0, 1.0]$
- `verification_status` (VARCHAR(16)) — `UNVERIFIED`, `CONFIRMED`, `MODIFIED`, `DISPUTED`
- `verified_by_user_id` (UUID, Foreign Key -> `users.id`, Nullable)
- `created_at` (TIMESTAMP WITH TIME ZONE)

### 3.4 `vital_readings` (Longitudinal Trajectory)
- `id` (UUID, Primary Key)
- `case_id` (UUID, Foreign Key -> `cases.id`)
- `heart_rate` (INTEGER, Nullable)
- `systolic_bp` (INTEGER, Nullable)
- `diastolic_bp` (INTEGER, Nullable)
- `spo2_percent` (INTEGER, Nullable)
- `respiratory_rate` (INTEGER, Nullable)
- `temperature_celsius` (FLOAT, Nullable)
- `avpu_score` (VARCHAR(8), Nullable) — `ALERT`, `VOICE`, `PAIN`, `UNRESPONSIVE`
- `recorded_at` (TIMESTAMP WITH TIME ZONE)

### 3.5 `facilities` & `facility_capabilities`
- `facilities`:
  - `id` (UUID, Primary Key)
  - `name` (VARCHAR(128))
  - `tier` (VARCHAR(32)) — `LEVEL_1_PHC`, `LEVEL_2_CHC`, `LEVEL_3_SDH`, `LEVEL_4_DH`, `LEVEL_5_TERTIARY`
  - `latitude` (FLOAT), `longitude` (FLOAT)
  - `icu_beds_total` (INTEGER), `icu_beds_available` (INTEGER)
  - `general_beds_total` (INTEGER), `general_beds_available` (INTEGER)
  - `ed_waiting_cases` (INTEGER), `ed_avg_wait_min` (INTEGER)
- `facility_capabilities`:
  - `id` (UUID, Primary Key)
  - `facility_id` (UUID, Foreign Key -> `facilities.id`)
  - `capability_code` (VARCHAR(64)) — e.g. `CT_SCAN_HEAD`, `TROPONIN_LAB`, `EMERGENCY_OT`, `BLOOD_BANK`
  - `is_operational` (BOOLEAN, Default: True)
  - `maintenance_note` (VARCHAR(255), Nullable)

### 3.6 `clinician_decisions`
- `id` (UUID, Primary Key)
- `case_id` (UUID, Foreign Key -> `cases.id`)
- `clinician_id` (UUID, Foreign Key -> `users.id`)
- `action_type` (VARCHAR(32)) — `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`
- `decision_type` (VARCHAR(16)) — `ACCEPT` or `OVERRIDE`
- `override_reason` (TEXT, Nullable)
- `notes` (TEXT, Nullable)
- `timestamp` (TIMESTAMP WITH TIME ZONE)

### 3.7 `referrals`
- `id` (UUID, Primary Key)
- `case_id` (UUID, Foreign Key -> `cases.id`)
- `origin_facility_id` (UUID, Foreign Key -> `facilities.id`)
- `destination_facility_id` (UUID, Foreign Key -> `facilities.id`)
- `required_bundle` (VARCHAR(64))
- `sbar_situation` (TEXT), `sbar_background` (TEXT), `sbar_assessment` (TEXT), `sbar_recommendation` (TEXT)
- `status` (VARCHAR(32)) — `REQUESTED`, `ACCEPTED`, `DISPATCHED`, `COMPLETED`, `REJECTED`
- `created_at` (TIMESTAMP WITH TIME ZONE)

### 3.8 `audit_logs` (Immutable Medicolegal Trail)
- `id` (BIGINT, Primary Key, Auto-Increment)
- `actor_id` (VARCHAR(64)) — User ID or `SYSTEM`
- `action` (VARCHAR(64)) — e.g. `INTAKE_CREATED`, `DECISION_AUTHORIZED`, `OVERRIDE_RECORDED`
- `entity_type` (VARCHAR(64)), `entity_id` (VARCHAR(64))
- `details` (JSONB) — Snapshot of previous state and applied change
- `ip_address` (VARCHAR(45), Nullable)
- `timestamp` (TIMESTAMP WITH TIME ZONE)
