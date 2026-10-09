# CLINOVA AI — Closed-Loop Referral & Transfer Logistics Data Model

> **Document ID:** `RES-94`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: The Anti-Blind-Transfer Mandate

In developing public healthcare networks, over 60% of inter-facility transfers are **blind transfers**:
- A rural PHC sends a deteriorating patient in an auto-rickshaw to a District Hospital without verifying if the hospital has an available ICU bed, ventilator, or blood cross-match.
- The patient arrives hours later only to be turned away because the facility is saturated, dying en route to a third hospital (*"referral death loop"*).
- Paper referral slips get soaked, lost, or lack vital baseline signs.

CLINOVA AI models **Closed-Loop Inter-Facility Transfers**:
1. **Capability-Matched Destination Pre-Lock:** The destination hospital is selected based on verified $\text{FACILITYGRAPH}$ capacity.
2. **Digital SBAR Referral Pack:** Transmits situation, background, verified vitals, and medication history digitally *before* the ambulance departs.
3. **Continuous Lifecycle Tracking:** Models transit states from `INITIATED` $\to$ `ACCEPTED` $\to$ `IN_TRANSIT` $\to$ `ARRIVED` $\to$ `COMPLETED`.
4. **Zero-Reentry Reception:** The receiving hospital opens the **SAME `case_id`** upon physical arrival.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REFERRAL & TRANSFER LOGISTICS SCHEMA                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── referrals (referral_id PK, case_id FK)                               │
│    │     ├── [Referring & Destination Facilities, Priority, SBAR Pack]      │
│    │     │                                                                  │
│    │     └── transfer_transit_logs (log_id PK, referral_id FK)              │
│    │           └── [En-Route Serial Vitals, GPS Geolocation, Paramedic ID]  │
│    │                                                                        │
│    └── referral_rejections (rejection_id PK, referral_id FK)                │
│          └── [Rejection Reason, Destination Bed Saturation, Reroute Pointer]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `referrals` Table

```sql
CREATE TABLE referrals (
    referral_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    referring_facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    destination_facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    referring_clinician_id UUID NOT NULL REFERENCES users(id),
    receiving_clinician_id UUID REFERENCES users(id),
    priority VARCHAR(16) NOT NULL DEFAULT 'URGENT'
        CHECK (priority IN ('ROUTINE', 'URGENT', 'EMERGENCY')),
    clinical_summary_pack JSONB NOT NULL, -- SBAR: { situation, background, assessment, recommendation }
    required_capabilities JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["ICU_VENTILATOR", "CT_SCAN"]
    transfer_urgency_minutes INTEGER NOT NULL DEFAULT 60,
    transport_mode VARCHAR(32) NOT NULL DEFAULT 'GOVERNMENT_108_AMBULANCE'
        CHECK (transport_mode IN ('GOVERNMENT_108_AMBULANCE', 'ALS_AMBULANCE', 'BLS_AMBULANCE', 'PRIVATE_VEHICLE', 'AIR_AMBULANCE')),
    status VARCHAR(32) NOT NULL DEFAULT 'INITIATED'
        CHECK (status IN ('DRAFT', 'INITIATED', 'ACCEPTED', 'REJECTED', 'IN_TRANSIT', 'ARRIVED', 'COMPLETED', 'CANCELLED')),
    rejection_reason TEXT,
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    departed_at TIMESTAMPTZ,
    arrival_confirmed_at TIMESTAMPTZ,
    outcome_id UUID REFERENCES case_outcomes(id)
);

CREATE INDEX ix_referrals_case ON referrals(case_id);
CREATE INDEX ix_referrals_dest_status ON referrals(destination_facility_id, status);
```

### 3.2 `transfer_transit_logs` Table

```sql
CREATE TABLE transfer_transit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID NOT NULL REFERENCES referrals(referral_id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    paramedic_actor_id UUID NOT NULL REFERENCES users(id),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    enroute_heart_rate INTEGER,
    enroute_spo2 INTEGER,
    enroute_systolic_bp INTEGER,
    oxygen_flow_liters_min NUMERIC(3,1),
    clinical_event_note TEXT
);

CREATE INDEX ix_transit_logs_referral ON transfer_transit_logs(referral_id, logged_at ASC);
```

### 3.3 `referral_rejections` Table (Rerouting Audit)

```sql
CREATE TABLE referral_rejections (
    rejection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID NOT NULL REFERENCES referrals(referral_id) ON DELETE RESTRICT,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    rejected_facility_id UUID NOT NULL REFERENCES facilities(id),
    rejection_reason_code VARCHAR(32) NOT NULL CHECK (rejection_reason_code IN (
        'NO_ICU_BED', 'VENTILATOR_UNAVAILABLE', 'SPECIALIST_UNAVAILABLE', 'OXYGEN_SHORTAGE', 'OTHER'
    )),
    rejection_notes TEXT NOT NULL,
    rejected_by_actor_id UUID NOT NULL REFERENCES users(id),
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rerouted_referral_id UUID REFERENCES referrals(referral_id)
);

CREATE INDEX ix_ref_rejections ON referral_rejections(referral_id);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE referrals (
    referral_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    referring_facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    destination_facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    referring_clinician_id TEXT NOT NULL REFERENCES users(id),
    receiving_clinician_id TEXT REFERENCES users(id),
    priority TEXT NOT NULL DEFAULT 'URGENT' CHECK (priority IN ('ROUTINE', 'URGENT', 'EMERGENCY')),
    clinical_summary_pack TEXT NOT NULL, -- JSON string
    required_capabilities TEXT NOT NULL DEFAULT '[]', -- JSON string
    transfer_urgency_minutes INTEGER NOT NULL DEFAULT 60,
    transport_mode TEXT NOT NULL DEFAULT 'GOVERNMENT_108_AMBULANCE' CHECK (transport_mode IN ('GOVERNMENT_108_AMBULANCE', 'ALS_AMBULANCE', 'BLS_AMBULANCE', 'PRIVATE_VEHICLE', 'AIR_AMBULANCE')),
    status TEXT NOT NULL DEFAULT 'INITIATED' CHECK (status IN ('DRAFT', 'INITIATED', 'ACCEPTED', 'REJECTED', 'IN_TRANSIT', 'ARRIVED', 'COMPLETED', 'CANCELLED')),
    rejection_reason TEXT,
    initiated_at TEXT NOT NULL,
    accepted_at TEXT,
    departed_at TEXT,
    arrival_confirmed_at TEXT,
    outcome_id TEXT REFERENCES case_outcomes(id)
);

CREATE TABLE transfer_transit_logs (
    log_id TEXT PRIMARY KEY NOT NULL,
    referral_id TEXT NOT NULL REFERENCES referrals(referral_id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    logged_at TEXT NOT NULL,
    paramedic_actor_id TEXT NOT NULL REFERENCES users(id),
    latitude REAL,
    longitude REAL,
    enroute_heart_rate INTEGER,
    enroute_spo2 INTEGER,
    enroute_systolic_bp INTEGER,
    oxygen_flow_liters_min REAL,
    clinical_event_note TEXT
);

CREATE TABLE referral_rejections (
    rejection_id TEXT PRIMARY KEY NOT NULL,
    referral_id TEXT NOT NULL REFERENCES referrals(referral_id) ON DELETE RESTRICT,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    rejected_facility_id TEXT NOT NULL REFERENCES facilities(id),
    rejection_reason_code TEXT NOT NULL CHECK (rejection_reason_code IN (
        'NO_ICU_BED', 'VENTILATOR_UNAVAILABLE', 'SPECIALIST_UNAVAILABLE', 'OXYGEN_SHORTAGE', 'OTHER'
    )),
    rejection_notes TEXT NOT NULL,
    rejected_by_actor_id TEXT NOT NULL REFERENCES users(id),
    rejected_at TEXT NOT NULL,
    rerouted_referral_id TEXT REFERENCES referrals(referral_id)
);
```

---

## 5. Invariants Governing Referrals & Transfers

$$\begin{aligned}
\mathbf{Inv\ REF\text{-}1} &: \quad \forall r \in \text{Referrals}, \quad r.\text{referring\_facility\_id} \neq r.\text{destination\_facility\_id} \\
\mathbf{Inv\ REF\text{-}2} &: \quad r.\text{status} = \text{'IN\_TRANSIT'} \implies r.\text{departed\_at} \neq \text{NULL} \\
\mathbf{Inv\ REF\text{-}3} &: \quad r.\text{status} = \text{'ARRIVED'} \implies \left( r.\text{arrival\_confirmed\_at} \neq \text{NULL} \land \text{Cases}(r.\text{case\_id}).\text{current\_facility\_id} = r.\text{destination\_facility\_id} \right) \\
\mathbf{Inv\ REF\text{-}4} &: \quad \text{Destination rejection mandates immediate FACILITYGRAPH alternative facility recalculation.}
\end{aligned}$$
