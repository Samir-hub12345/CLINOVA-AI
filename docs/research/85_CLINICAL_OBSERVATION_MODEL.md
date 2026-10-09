# CLINOVA AI — Clinical Observations & Serial Vitals Data Model

> **Document ID:** `RES-85`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Serial Physiology & Epistemic Tracking

In emergency and acute triage, vital signs are **time-series physiological vectors**, never static single measurements. A patient presenting with a systolic BP of 110 mmHg who drops to 85 mmHg 20 minutes later is in decompensating hemorrhagic shock, even though both individual numbers might look benign in isolation.

CLINOVA AI models:
1. **Serial Vital Readings:** Captures multiple repeated vitals snapshots across intake, waiting room, resuscitation, ward, and transit epochs.
2. **Discrete Clinical Observations:** Standardized observation entities covering physical signs, bedside labs (glucometer, malaria rapid strip), and auscultation findings.
3. **Epistemic & Verification Bounds:** Explicitly binds observer identity, instrument modality, reference ranges, and clinician verification status.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CLINICAL OBSERVATIONS & VITALS SCHEMA                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── vital_readings (id PK, case_id FK)                                   │
│    │     └── [Serial BP, HR, SpO2, RR, Temp, AVPU, Shock Index, NEWS2]     │
│    │                                                                        │
│    └── clinical_observations (observation_id PK, case_id FK)               │
│          └── [VITAL, SYMPTOM, LAB, SIGN, FINDING]                           │
│                └── (LOINC / SNOMED CT Codes, Reference Ranges, Provenance)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `vital_readings` Table (Serial Time-Series Vitals)

```sql
CREATE TABLE vital_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    epoch_type VARCHAR(32) NOT NULL DEFAULT 'INTAKE_TRIAGE'
        CHECK (epoch_type IN ('INTAKE_TRIAGE', 'WAITING_ROOM', 'RESUSCITATION', 'PROCEDURE_PREP', 'INPATIENT_ROUND', 'TRANSIT_ENROUTE')),
    heart_rate INTEGER CHECK (heart_rate > 0 AND heart_rate < 300),
    systolic_bp INTEGER CHECK (systolic_bp > 20 AND systolic_bp < 320),
    diastolic_bp INTEGER CHECK (diastolic_bp > 10 AND diastolic_bp < 220),
    spo2_percent INTEGER CHECK (spo2_percent >= 0 AND spo2_percent <= 100),
    respiratory_rate INTEGER CHECK (respiratory_rate > 0 AND respiratory_rate < 100),
    temperature_celsius NUMERIC(4,1) CHECK (temperature_celsius >= 25.0 AND temperature_celsius <= 45.0),
    avpu_score VARCHAR(16) NOT NULL DEFAULT 'ALERT'
        CHECK (avpu_score IN ('ALERT', 'VOICE', 'PAIN', 'UNRESPONSIVE')),
    shock_index NUMERIC(4,2) GENERATED ALWAYS AS (
        CASE WHEN systolic_bp IS NOT NULL AND systolic_bp > 0 
             THEN ROUND((heart_rate::numeric / systolic_bp::numeric), 2)
             ELSE NULL END
    ) STORED,
    news2_score INTEGER CHECK (news2_score >= 0 AND news2_score <= 20),
    measurement_device VARCHAR(64), -- e.g., 'Omron_M2_Basic', 'Manual_Cuff'
    recorded_by_actor_id UUID NOT NULL REFERENCES users(id),
    source_type VARCHAR(32) NOT NULL DEFAULT 'STAFF_ENTERED'
        CHECK (source_type IN ('STAFF_ENTERED', 'PATIENT_REPORTED', 'SENSOR_TELEMETRY', 'CLINICIAN_VERIFIED')),
    verification_status VARCHAR(16) NOT NULL DEFAULT 'CONFIRMED'
        CHECK (verification_status IN ('UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED')),
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_vitals_case_measured ON vital_readings(case_id, measured_at ASC);
CREATE INDEX ix_vitals_shock_index ON vital_readings(case_id, shock_index);
```

### 3.2 `clinical_observations` Table (Generic Clinical Entities)

```sql
CREATE TABLE clinical_observations (
    observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    observation_type VARCHAR(32) NOT NULL 
        CHECK (observation_type IN ('VITAL', 'SYMPTOM', 'LAB', 'SIGN', 'FINDING')),
    canonical_concept_code VARCHAR(64), -- LOINC or SNOMED CT
    concept_name VARCHAR(128) NOT NULL, -- e.g., 'Capillary Blood Glucose'
    value_numeric NUMERIC(10,3),
    value_text TEXT,
    unit VARCHAR(32),                   -- 'mg/dL', 'mmol/L', 'bpm'
    normal_range_low NUMERIC(10,3),
    normal_range_high NUMERIC(10,3),
    is_abnormal BOOLEAN GENERATED ALWAYS AS (
        CASE 
            WHEN value_numeric IS NOT NULL AND normal_range_low IS NOT NULL AND value_numeric < normal_range_low THEN TRUE
            WHEN value_numeric IS NOT NULL AND normal_range_high IS NOT NULL AND value_numeric > normal_range_high THEN TRUE
            ELSE FALSE
        END
    ) STORED,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_id UUID NOT NULL REFERENCES users(id),
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN (
        'PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 
        'CLINICIAN_VERIFIED', 'STAFF_ENTERED', 'AI_INFERRED', 
        'SYSTEM_DERIVED', 'EXTERNAL_RECORD'
    )),
    epistemic_status VARCHAR(16) NOT NULL DEFAULT 'KNOWN' CHECK (epistemic_status IN (
        'KNOWN', 'UNKNOWN', 'CONFLICTING', 'UNRELIABLE', 'VERIFIED', 'INFERRED'
    )),
    verification_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED', 'REJECTED'
    )),
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ
);

CREATE INDEX ix_obs_case_concept ON clinical_observations(case_id, canonical_concept_code);
CREATE INDEX ix_obs_abnormal ON clinical_observations(case_id, is_abnormal);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE vital_readings (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id TEXT NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    epoch_type TEXT NOT NULL DEFAULT 'INTAKE_TRIAGE' CHECK (epoch_type IN ('INTAKE_TRIAGE', 'WAITING_ROOM', 'RESUSCITATION', 'PROCEDURE_PREP', 'INPATIENT_ROUND', 'TRANSIT_ENROUTE')),
    heart_rate INTEGER CHECK (heart_rate IS NULL OR (heart_rate > 0 AND heart_rate < 300)),
    systolic_bp INTEGER CHECK (systolic_bp IS NULL OR (systolic_bp > 20 AND systolic_bp < 320)),
    diastolic_bp INTEGER CHECK (diastolic_bp IS NULL OR (diastolic_bp > 10 AND diastolic_bp < 220)),
    spo2_percent INTEGER CHECK (spo2_percent IS NULL OR (spo2_percent >= 0 AND spo2_percent <= 100)),
    respiratory_rate INTEGER CHECK (respiratory_rate IS NULL OR (respiratory_rate > 0 AND respiratory_rate < 100)),
    temperature_celsius REAL CHECK (temperature_celsius IS NULL OR (temperature_celsius >= 25.0 AND temperature_celsius <= 45.0)),
    avpu_score TEXT NOT NULL DEFAULT 'ALERT' CHECK (avpu_score IN ('ALERT', 'VOICE', 'PAIN', 'UNRESPONSIVE')),
    shock_index REAL, -- Calculated by client/trigger
    news2_score INTEGER CHECK (news2_score IS NULL OR (news2_score >= 0 AND news2_score <= 20)),
    measurement_device TEXT,
    recorded_by_actor_id TEXT NOT NULL REFERENCES users(id),
    source_type TEXT NOT NULL DEFAULT 'STAFF_ENTERED' CHECK (source_type IN ('STAFF_ENTERED', 'PATIENT_REPORTED', 'SENSOR_TELEMETRY', 'CLINICIAN_VERIFIED')),
    verification_status TEXT NOT NULL DEFAULT 'CONFIRMED' CHECK (verification_status IN ('UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED')),
    measured_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE clinical_observations (
    observation_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id TEXT NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    observation_type TEXT NOT NULL CHECK (observation_type IN ('VITAL', 'SYMPTOM', 'LAB', 'SIGN', 'FINDING')),
    canonical_concept_code TEXT,
    concept_name TEXT NOT NULL,
    value_numeric REAL,
    value_text TEXT,
    unit TEXT,
    normal_range_low REAL,
    normal_range_high REAL,
    is_abnormal INTEGER NOT NULL DEFAULT 0 CHECK (is_abnormal IN (0, 1)),
    measured_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    actor_id TEXT NOT NULL REFERENCES users(id),
    source_type TEXT NOT NULL CHECK (source_type IN (
        'PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 
        'CLINICIAN_VERIFIED', 'STAFF_ENTERED', 'AI_INFERRED', 
        'SYSTEM_DERIVED', 'EXTERNAL_RECORD'
    )),
    epistemic_status TEXT NOT NULL DEFAULT 'KNOWN' CHECK (epistemic_status IN (
        'KNOWN', 'UNKNOWN', 'CONFLICTING', 'UNRELIABLE', 'VERIFIED', 'INFERRED'
    )),
    verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED', 'REJECTED'
    )),
    verified_by TEXT REFERENCES users(id),
    verified_at TEXT
);
```

---

## 5. Invariants Governing Observations & Vitals

$$\begin{aligned}
\mathbf{Inv\ OBS\text{-}1} &: \quad \forall v \in \text{VitalReadings}, \quad (v.\text{systolic\_bp} \neq \text{NULL} \land v.\text{diastolic\_bp} \neq \text{NULL}) \implies v.\text{systolic\_bp} > v.\text{diastolic\_bp} \\
\mathbf{Inv\ OBS\text{-}2} &: \quad v.\text{spo2\_percent} < 85 \implies \text{Trigger Emergency Jump to } \text{STATE\_EMERGENCY\_ACTIVE} \\
\mathbf{Inv\ OBS\text{-}3} &: \quad v.\text{shock\_index} = \frac{v.\text{heart\_rate}}{v.\text{systolic\_bp}} > 1.0 \implies \text{Flag Critical Hypoperfusion Hazard} \\
\mathbf{Inv\ OBS\text{-}4} &: \quad \text{Serial vitals form a strictly chronological sequence: } \forall i < j, \quad v_i.\text{measured\_at} \le v_j.\text{measured\_at}
\end{aligned}$$
