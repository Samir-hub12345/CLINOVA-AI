# CLINOVA AI — Event History & Audit Ledger Data Model

> **Document ID:** `RES-82`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: Append-Only Event Sourcing

In medicolegal clinical systems, maintaining an immutable record of **who knew what, and when they knew it** is essential. If a clinical system mutates records in place (e.g. overwriting an initial blood pressure or deleting an unverified symptom), investigating adverse events or proving diagnostic timelines during clinical audits becomes impossible.

CLINOVA AI enforces an **Append-Only Event Ledger** (`case_events`). Every state transition, vital sign acquisition, document extraction, AI inference, clinician modification, referral dispatch, and outcome registration is committed as an immutable event.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CRYPTOGRAPHIC EVENT HASH CHAIN                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Event 1: CASE_INITIALIZED]                                                │
│  Hash: H_1 = SHA256(GENESIS || event_id_1 || payload_1)                      │
│        │                                                                    │
│        ▼                                                                    │
│  [Event 2: VITALS_MEASURED]                                                 │
│  Hash: H_2 = SHA256(H_1 || event_id_2 || payload_2)                         │
│        │                                                                    │
│        ▼                                                                    │
│  [Event 3: AI_TRIAGE_GENERATED]                                             │
│  Hash: H_3 = SHA256(H_2 || event_id_3 || payload_3)                         │
│        │                                                                    │
│        ▼                                                                    │
│  [Event 4: CLINICIAN_MODIFICATION_APPLIED]                                  │
│  Hash: H_4 = SHA256(H_3 || event_id_4 || payload_4)                         │
│        │                                                                    │
│        ▼                                                                    │
│  [Event n: CASE_CLOSED_AND_SEALED]                                          │
│  Hash: H_n = Merkle Root Sealed Hash                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Event Ledger Schema Specification: `case_events`

### 2.1 Attribute Breakdown

| Field Name | Postgres Type | SQLite Type | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | `UUID PRIMARY KEY` | `TEXT PRIMARY KEY` | NO | Unique event identifier (`UUIDv4`). |
| `case_id` | `UUID REFERENCES cases(id)` | `TEXT REFERENCES cases(id)` | NO | Foreign key to Master Case root. |
| `encounter_id` | `UUID REFERENCES encounters(id)` | `TEXT REFERENCES encounters(id)` | NO | Foreign key to clinical encounter. |
| `facility_id` | `UUID REFERENCES facilities(id)` | `TEXT REFERENCES facilities(id)` | NO | Facility where event occurred. |
| `actor_id` | `UUID REFERENCES users(id)` | `TEXT REFERENCES users(id)` | NO | User or system daemon generating event. |
| `actor_role` | `VARCHAR(32)` | `TEXT` | NO | Role of actor at the time of event. |
| `event_type` | `VARCHAR(64)` | `TEXT` | NO | Canonical event type identifier. |
| `timestamp` | `TIMESTAMPTZ` | `TEXT` | NO | UTC ISO-8601 timestamp with microsecond precision. |
| `payload` | `JSONB` | `TEXT` | NO | Complete structured event payload. |
| `previous_event_id` | `UUID` | `TEXT` | YES | Pointer to immediate previous event in case chain (`NULL` for genesis). |
| `integrity_hash` | `VARCHAR(64)` | `TEXT` | NO | SHA-256 hash linking previous hash with current event content. |
| `digital_signature` | `TEXT` | `TEXT` | YES | Cryptographic signature of actor/device (Ed25519 or ECDSA). |

---

## 3. Relational DDL Specification

### 3.1 PostgreSQL DDL

```sql
CREATE TABLE case_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    actor_id UUID NOT NULL REFERENCES users(id),
    actor_role VARCHAR(32) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    previous_event_id UUID REFERENCES case_events(event_id),
    integrity_hash VARCHAR(64) NOT NULL,
    digital_signature TEXT,
    CONSTRAINT chk_event_payload_nonempty CHECK (payload != '{}'::jsonb)
);

-- Indices for performance and sequence auditing
CREATE INDEX ix_case_events_case_seq ON case_events(case_id, timestamp ASC);
CREATE INDEX ix_case_events_actor ON case_events(actor_id);
CREATE INDEX ix_case_events_type ON case_events(event_type);
CREATE INDEX ix_case_events_timestamp ON case_events(timestamp DESC);
```

### 3.2 SQLite DDL

```sql
CREATE TABLE case_events (
    event_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id TEXT NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    actor_id TEXT NOT NULL REFERENCES users(id),
    actor_role TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL, -- ISO-8601 UTC
    payload TEXT NOT NULL,   -- JSON text
    previous_event_id TEXT REFERENCES case_events(event_id),
    integrity_hash TEXT NOT NULL,
    digital_signature TEXT
);

CREATE INDEX ix_case_events_case_seq ON case_events(case_id, timestamp ASC);
CREATE INDEX ix_case_events_actor ON case_events(actor_id);
CREATE INDEX ix_case_events_type ON case_events(event_type);
CREATE INDEX ix_case_events_timestamp ON case_events(timestamp DESC);
```

---

## 4. Canonical Event Taxonomy

Every event in CLINOVA AI is strictly categorized:

| Category | Canonical `event_type` | Trigger Description |
| :--- | :--- | :--- |
| **Lifecycle** | `CASE_INITIALIZED` | Case instantiated in system; consent documented. |
| **Lifecycle** | `CASE_STATE_CHANGED` | FSM state transitioned from previous to new state. |
| **Lifecycle** | `CASE_SEALED` | Terminal `STATE_CLOSED` reached; Merkle root calculated. |
| **Ingestion** | `AUDIO_RECORDING_ATTACHED`| Vernacular audio uploaded with file hash and length. |
| **Ingestion** | `DOCUMENT_UPLOADED` | Prescription or lab document uploaded. |
| **Extraction** | `TRANSCRIPTION_COMPLETED` | Whisper completed; transcript payload attached. |
| **Extraction** | `OCR_EXTRACTION_COMPLETED`| PaddleOCR completed; bounding boxes and text extracted. |
| **Clinical** | `VITALS_RECORDED` | Frontline nurse or triage nurse measured physical vitals. |
| **Clinical** | `SYMPTOM_ASSERTED` | Symptom timeline updated with onset and severity. |
| **Clinical** | `SUFFICIENCY_AUDITED` | Missing information audited; sufficiency score computed. |
| **Clinical** | `QUESTION_PRESENTED` | NBI follow-up prompt displayed to user. |
| **Clinical** | `ANSWER_CAPTURED` | User responded to follow-up prompt. |
| **Synthesis** | `CAREGRAPH_EVALUATED` | Risk score, trajectory slope, and $U_t$ calculated. |
| **Synthesis** | `TRIAGE_NOTE_GENERATED` | Advisory triage note and differential conditions generated. |
| **Clinician** | `DOCTOR_REVIEW_STARTED` | Attending physician opened case on workbench. |
| **Clinician** | `FINDING_VERIFIED` | Clinician clicked VERIFY on clinical observation. |
| **Clinician** | `FINDING_MODIFIED` | Clinician altered AI or nurse finding with justification. |
| **Clinician** | `DISPOSITION_SIGNED` | RMP authorized final clinical disposition. |
| **Logistics** | `REFERRAL_INITIATED` | Inter-facility referral pack sent to destination hospital. |
| **Logistics** | `AMBULANCE_DISPATCHED` | Transport in transit; en-route tracking active. |
| **Logistics** | `WARD_ADMISSION_SIGNED` | Inpatient bed allocated; two-party SBAR sign-off complete. |
| **Logistics** | `OT_CHECKLIST_VERIFIED` | Surgical team executed WHO sign-in / time-out. |
| **Outcome** | `CLINICAL_OUTCOME_LOGGED`| Definitive clinical endpoint recorded (e.g. STABILIZED). |
| **Emergency** | `BREAK_GLASS_TRIGGERED` | Sudden patient collapse escalated to P1 Emergency. |
| **Identity** | `IDENTITY_LINK_BOUND` | Emergency anonymous case bound to discovered patient identity. |

---

## 5. Cryptographic Chaining & Tamper Detection

Each event computes its `integrity_hash` deterministically:

$$H_n = \text{SHA-256}\Big( H_{n-1} \parallel \text{event\_id} \parallel \text{case\_id} \parallel \text{timestamp} \parallel \text{CanonicalJSON}(\text{payload}) \Big)$$

For the initial event ($n=1$), $H_0 = \text{"0000000000000000000000000000000000000000000000000000000000000000"}$.

### 5.1 Verification Query
To verify the integrity of any case's history, the engine verifies the hash chain sequentially:
```sql
-- Hash Verification Query Logic
WITH RECURSIVE event_chain AS (
    SELECT event_id, case_id, timestamp, integrity_hash, previous_event_id, 1 as seq
    FROM case_events 
    WHERE case_id = :case_id AND previous_event_id IS NULL
    UNION ALL
    SELECT ce.event_id, ce.case_id, ce.timestamp, ce.integrity_hash, ce.previous_event_id, ec.seq + 1
    FROM case_events ce
    JOIN event_chain ec ON ce.previous_event_id = ec.event_id
)
SELECT * FROM event_chain ORDER BY seq ASC;
```

If any row's payload or timestamp was altered directly in the database, the hash verification will fail, flagging unauthorized tampering immediately.
