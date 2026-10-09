# CLINOVA AI — Patient Requirements & Facility Feasibility Data Model

> **Document ID:** `RES-92`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Grounding Care in Real-World Resources

Clinical triage in traditional systems operates in an operational vacuum. A guideline may correctly suggest *"Immediate contrast-enhanced CT scan and emergency burr hole surgery"*, but if the local facility is a rural Primary Health Centre with no CT machine and no surgeon, the recommendation is clinically useless and dangerous.

CLINOVA AI couples biological need with operational reality via **FACILITYGRAPH**:
1. **Patient Care Requirements (`care_requirements`):** What specialties, diagnostic modalities, and interventions does this patient urgently need?
2. **Facility Capability State (`facility_capabilities`):** What resources does the facility currently possess, what is their verification freshness status, and are critical assets operational?
3. **Feasibility Index Evaluation (`feasibility_evaluations`):** Can this patient be managed locally, do they need bedside stabilization before transfer, or do they require immediate inter-facility transfer?

---

## 2. Telemetry Freshness & Stale Capability Detection

In rural public healthcare, equipment breaks down (e.g., CT tube failure, X-ray power outage) and bed counts fluctuate constantly.

The data model tracks capability freshness explicitly:
- **`FRESH`:** Capability verified within the last 4 hours (active shift confirmation).
- **`STALE`:** Last verified between 4 and 12 hours ago; system displays yellow warning and prompts staff telephonic re-confirmation.
- **`UNVERIFIED`:** Unverified for $> 12$ hours; cannot be trusted for emergent surgical/ICU transfers without manual confirmation.

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CARE REQUIREMENTS & FEASIBILITY SCHEMA                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── care_requirements (requirement_id PK, case_id FK)                   │
│    │     └── [Specialties, Diagnostics, Interventions, Urgency Timeframe]   │
│    │                                                                        │
│    └── feasibility_evaluations (evaluation_id PK, case_id FK)               │
│          └── [Local vs Referral Match, Unmet Needs, Recommendation]        │
│                                                                             │
│  facilities (facility_id PK)                                                │
│    └── facility_capabilities (id PK, facility_id FK)                        │
│          └── [Capability Code, Operational Status, Freshness, Source]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `care_requirements` Table

```sql
CREATE TABLE care_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    required_specialties JSONB NOT NULL DEFAULT '[]'::jsonb,  -- e.g., ['CARDIOLOGY', 'GENERAL_SURGERY']
    required_diagnostics JSONB NOT NULL DEFAULT '[]'::jsonb,  -- e.g., ['12_LEAD_ECG', 'TROPONIN_I', 'CT_HEAD']
    required_interventions JSONB NOT NULL DEFAULT '[]'::jsonb,-- e.g., ['MECHANICAL_VENTILATION', 'BLOOD_TRANSFUSION']
    urgency_timeframe_minutes INTEGER NOT NULL DEFAULT 60,   -- Window within which care must begin
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_care_req_case ON care_requirements(case_id);
```

### 4.2 `facility_capabilities` Table

```sql
CREATE TABLE facility_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    capability_name VARCHAR(64) NOT NULL, -- e.g., 'CT_SCAN_24_7', 'BLOOD_BANK', 'OXYGEN_MANIFOLD'
    current_status VARCHAR(16) NOT NULL DEFAULT 'AVAILABLE'
        CHECK (current_status IN ('AVAILABLE', 'UNAVAILABLE', 'LIMITED', 'UNKNOWN')),
    last_verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verification_source VARCHAR(32) NOT NULL DEFAULT 'STAFF_SHIFT_REPORT'
        CHECK (verification_source IN ('STAFF_SHIFT_REPORT', 'IOT_SENSOR', 'API_INTEGRATION', 'TELEPHONE_AUDIT')),
    freshness_status VARCHAR(16) NOT NULL DEFAULT 'FRESH'
        CHECK (freshness_status IN ('FRESH', 'STALE', 'UNVERIFIED')),
    maintenance_note TEXT,
    CONSTRAINT uq_facility_capability UNIQUE (facility_id, capability_name)
);

CREATE INDEX ix_fac_caps ON facility_capabilities(facility_id, capability_name, current_status);
```

### 4.3 `feasibility_evaluations` Table

```sql
CREATE TABLE feasibility_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    is_feasible BOOLEAN NOT NULL,
    unmet_requirements JSONB NOT NULL DEFAULT '[]'::jsonb, -- Missing assets preventing local care
    capacity_status VARCHAR(32) NOT NULL DEFAULT 'ADEQUATE'
        CHECK (capacity_status IN ('ADEQUATE', 'SATURATED', 'OVERFLOW_CRITICAL')),
    recommendation VARCHAR(32) NOT NULL 
        CHECK (recommendation IN ('LOCAL_CARE', 'STABILIZE_AND_TRANSFER', 'IMMEDIATE_TRANSFER')),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_feasibility_case ON feasibility_evaluations(case_id, facility_id);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE care_requirements (
    requirement_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    required_specialties TEXT NOT NULL DEFAULT '[]', -- JSON string
    required_diagnostics TEXT NOT NULL DEFAULT '[]', -- JSON string
    required_interventions TEXT NOT NULL DEFAULT '[]', -- JSON string
    urgency_timeframe_minutes INTEGER NOT NULL DEFAULT 60,
    evaluated_at TEXT NOT NULL
);

CREATE TABLE facility_capabilities (
    id TEXT PRIMARY KEY NOT NULL,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    capability_name TEXT NOT NULL,
    current_status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (current_status IN ('AVAILABLE', 'UNAVAILABLE', 'LIMITED', 'UNKNOWN')),
    last_verified_at TEXT NOT NULL,
    verification_source TEXT NOT NULL DEFAULT 'STAFF_SHIFT_REPORT' CHECK (verification_source IN ('STAFF_SHIFT_REPORT', 'IOT_SENSOR', 'API_INTEGRATION', 'TELEPHONE_AUDIT')),
    freshness_status TEXT NOT NULL DEFAULT 'FRESH' CHECK (freshness_status IN ('FRESH', 'STALE', 'UNVERIFIED')),
    maintenance_note TEXT,
    CONSTRAINT uq_facility_capability UNIQUE (facility_id, capability_name)
);

CREATE TABLE feasibility_evaluations (
    evaluation_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    is_feasible INTEGER NOT NULL CHECK (is_feasible IN (0, 1)),
    unmet_requirements TEXT NOT NULL DEFAULT '[]', -- JSON string
    capacity_status TEXT NOT NULL DEFAULT 'ADEQUATE' CHECK (capacity_status IN ('ADEQUATE', 'SATURATED', 'OVERFLOW_CRITICAL')),
    recommendation TEXT NOT NULL CHECK (recommendation IN ('LOCAL_CARE', 'STABILIZE_AND_TRANSFER', 'IMMEDIATE_TRANSFER')),
    evaluated_at TEXT NOT NULL
);
```

---

## 6. Invariants Governing Feasibility Evaluations

$$\begin{aligned}
\mathbf{Inv\ FEAS\text{-}1} &: \quad \text{Length}(e.\text{unmet\_requirements}) > 0 \implies e.\text{is\_feasible} = \text{FALSE} \\
\mathbf{Inv\ FEAS\text{-}2} &: \quad e.\text{is\_feasible} = \text{FALSE} \implies e.\text{recommendation} \in \{\text{'STABILIZE\_AND\_TRANSFER'}, \text{'IMMEDIATE\_TRANSFER'}\} \\
\mathbf{Inv\ FEAS\text{-}3} &: \quad \text{Capability telemetry with } c.\text{freshness\_status} = \text{'STALE'} \text{ requires telephonic confirmation before transfer lock.}
\end{aligned}$$
