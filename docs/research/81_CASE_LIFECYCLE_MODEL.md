# CLINOVA AI — Case Lifecycle & State Machine Mapping Model

> **Document ID:** `RES-81`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: 27 Canonical States

The lifecycle of an encounter in CLINOVA AI is governed by a **Deterministic Finite State Machine (FSM)**. As specified in Phase 5 (`RES-61` and `RES-62`), the lifecycle encompasses exactly **27 Canonical States**.

In the data model, every state transition is recorded in an immutable, append-only ledger (`case_state_transitions`). The root `cases` record tracks `current_state`, `previous_state`, and an optimistic concurrency version counter (`state_version`).

### 1.1 Canonical State Taxonomy & Alias Reconciliation

To ensure flawless interoperability between candidate specifications and Phase 5 formal state identifiers, both naming sets are explicitly mapped in the data model:

| State Code | Canonical DB Identifier | Upstream Candidate Identifier | State Category | Clinical Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `S01` | `STATE_NEW` | `STATE_NEW` | Initial | Initial intake encounter instantiated; consent verified. |
| `S02` | `STATE_INTAKE_COLLECTING` | `STATE_INTAKE` | Multimodal | Ingesting vernacular voice, free text narrative, and files. |
| `S03` | `STATE_EXTRACTING` | `STATE_EXTRACTING` | AI Processing | Local Whisper transcription and PaddleOCR entity parsing. |
| `S04` | `STATE_EXTRACTION_REVIEW` | `STATE_REVIEW_PENDING` | Verification | Operator / patient reviews extracted entities with raw crops. |
| `S05` | `STATE_MISSING_AUDIT` | `STATE_MISSING_INFORMATION`| Quality Gate | Epistemic audit evaluating Known, Unknown, Conflicting gaps. |
| `S06` | `STATE_FOLLOW_UP_PENDING`| `STATE_FOLLOW_UP_PENDING` | Interactive Q&A | Adaptive presentation of 1–3 targeted follow-up prompts. |
| `S07` | `STATE_STAFF_DATA_PENDING`| `STATE_STAFF_DATA_PENDING` | Frontline Gate | Sufficiency $< 0.85$; nurse worklist for missing vitals. |
| `S08` | `STATE_STAFF_VERIFIED` | `STATE_VERIFICATION_PENDING`| Clinical Sign-Off| Frontline nurse signs off bedside physical measurements. |
| `S09` | `STATE_CONSOLIDATED` | `STATE_CONSOLIDATED` | Aggregation | Master clinical dossier merged and locked for CAREGRAPH. |
| `S10` | `STATE_TRIAGE_READY` | `STATE_TRIAGE_READY` | Synthesis | Risk, trajectory slope, and uncertainty score $U_t$ compiled. |
| `S11` | `STATE_DOCTOR_QUEUED` | `STATE_DOCTOR_QUEUE` | Queuing | Positioned in multi-factor prioritized clinician review queue. |
| `S12` | `STATE_DOCTOR_REVIEWING` | `STATE_DOCTOR_REVIEW` | Clinician | RMP physician actively examining patient and dossier. |
| `S13` | `STATE_CLINICIAN_VERIFIED`| `STATE_CLINICIAN_VERIFIED` | Authorization | Clinician signs off verified clinical state and exam findings. |
| `S14` | `STATE_FACILITY_EVALUATING`| `STATE_FACILITY_EVALUATION`| Resource Gate | FACILITYGRAPH computes local capability and bed feasibility. |
| `S15` | `STATE_ORCHESTRATION_PENDING`| `STATE_ORCHESTRATION_PENDING`| Advisory | System synthesizes recommended care pathway for doctor. |
| `S16` | `STATE_ROUTINE_CARE` | `STATE_ROUTINE_CARE` | Pathway A | Outpatient prescription and recurring follow-up schedule. |
| `S17` | `STATE_FURTHER_REVIEW` | `STATE_FOLLOW_UP_SCHEDULED`| Pathway B | Single revisit slot ($\le 7$ days) for pending lab reassessment. |
| `S18` | `STATE_WARD_REQUESTED` | `STATE_WARD_REQUESTED` | Pathway C | Inpatient ward bed reservation requested; SBAR pack ready. |
| `S19` | `STATE_WARD_ADMITTED` | `STATE_ADMISSION` | Pathway C | Inpatient bed allocated; two-party SBAR handoff signed. |
| `S20` | `STATE_REFERRAL_PENDING` | `STATE_REFERRAL_PENDING` | Pathway D | Destination hospital selected; digital referral pack sent. |
| `S21` | `STATE_TRANSFER_IN_TRANSIT`| `STATE_TRANSFER` | Pathway D | Ambulance dispatched; patient physically en route. |
| `S22` | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY` | Pathway E | Acute resuscitation active; 30s ABCD vitals protocol. |
| `S23` | `STATE_OT_PENDING` | `STATE_OT_PENDING` | Pathway F | Surgical procedure booked; WHO checklist pre-op hold. |
| `S24` | `STATE_OT_HANDOFF` | `STATE_OT_HANDOFF` | Pathway F | Operation theatre holding bay; scrub team sign-in signed. |
| `S25` | `STATE_OUTCOME_PENDING` | `STATE_OUTCOME_PENDING` | Continuation | Post-disposition monitoring active (home, ward, transfer). |
| `S26` | `STATE_RESOLVED` | `STATE_RESOLVED` | Resolution | Definitive clinical endpoint recorded; CAREGRAPH finalized. |
| `S27` | `STATE_CLOSED` | `STATE_CLOSED` | Terminal | Cryptographic Merkle seal applied; case locked; telemetry out. |

---

## 2. Relational Schema: `case_state_transitions`

Every state mutation generates an immutable record in `case_state_transitions`. This guarantees that the entire historical journey of a case can be replayed and mathematically audited.

### 2.1 Table Structure

| Column Name | PostgreSQL Type | SQLite Type | Nullable | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID PRIMARY KEY` | `TEXT PRIMARY KEY` | NO | Unique transition identifier. |
| `case_id` | `UUID REFERENCES cases(id)` | `TEXT REFERENCES cases(id)` | NO | Foreign key to Master Case root. |
| `state_version` | `INTEGER` | `INTEGER` | NO | The `state_version` of the case resulting from this transition. |
| `previous_state` | `VARCHAR(32)` | `TEXT` | YES | State exited (`NULL` for `STATE_NEW`). |
| `current_state` | `VARCHAR(32)` | `TEXT` | NO | State entered. |
| `transition_trigger`| `VARCHAR(64)` | `TEXT` | NO | Trigger identifier (e.g., `NURSE_SUBMIT_VITALS`, `BREAK_GLASS_EMERGENCY`). |
| `state_transition_reason`| `TEXT` | `TEXT` | YES | Clinical or operational justification. |
| `actor_id` | `UUID REFERENCES users(id)` | `TEXT REFERENCES users(id)` | NO | Responsible staff member or system service agent. |
| `actor_role` | `VARCHAR(32)` | `TEXT` | NO | Role of actor (`ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_SYSTEM_AI`, etc.). |
| `transition_event_id`| `UUID` | `TEXT` | NO | Pointer to corresponding event in `case_events`. |
| `entered_at` | `TIMESTAMPTZ` | `TEXT` | NO | Exact timestamp state was entered. |
| `exited_at` | `TIMESTAMPTZ` | `TEXT` | YES | Timestamp state was exited (`NULL` while currently active). |
| `duration_seconds` | `INTEGER` | `INTEGER` | YES | Total seconds spent in this state. |

---

## 3. Relational DDL Specification

### 3.1 PostgreSQL DDL

```sql
CREATE TABLE case_state_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    state_version INTEGER NOT NULL,
    previous_state VARCHAR(32),
    current_state VARCHAR(32) NOT NULL,
    transition_trigger VARCHAR(64) NOT NULL,
    state_transition_reason TEXT,
    actor_id UUID NOT NULL REFERENCES users(id),
    actor_role VARCHAR(32) NOT NULL,
    transition_event_id UUID NOT NULL,
    entered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    exited_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    CONSTRAINT uq_case_version UNIQUE (case_id, state_version)
);

CREATE INDEX ix_cst_case_id ON case_state_transitions(case_id);
CREATE INDEX ix_cst_current_state ON case_state_transitions(current_state);
CREATE INDEX ix_cst_entered_at ON case_state_transitions(entered_at);
```

### 3.2 SQLite DDL

```sql
CREATE TABLE case_state_transitions (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    state_version INTEGER NOT NULL,
    previous_state TEXT,
    current_state TEXT NOT NULL,
    transition_trigger TEXT NOT NULL,
    state_transition_reason TEXT,
    actor_id TEXT NOT NULL REFERENCES users(id),
    actor_role TEXT NOT NULL,
    transition_event_id TEXT NOT NULL,
    entered_at TEXT NOT NULL,
    exited_at TEXT,
    duration_seconds INTEGER,
    CONSTRAINT uq_case_version UNIQUE (case_id, state_version)
);

CREATE INDEX ix_cst_case_id ON case_state_transitions(case_id);
CREATE INDEX ix_cst_current_state ON case_state_transitions(current_state);
CREATE INDEX ix_cst_entered_at ON case_state_transitions(entered_at);
```

---

## 4. State Machine Transition Execution & Concurrency Control

### 4.1 Optimistic Concurrency Control (OCC)
In multi-actor environments (e.g., triage nurse recording vitals while doctor opens review screen), concurrent updates must not clobber state.

When transitioning state, the database transaction executes an atomic compare-and-swap on `cases`:

```sql
-- Atomic OCC Transition Query
UPDATE cases
SET 
    previous_state = current_state,
    current_state = :new_state,
    state_version = state_version + 1,
    updated_at = NOW()
WHERE 
    id = :case_id 
    AND state_version = :expected_state_version;
```

If zero rows are updated, an `OptimisticLockConflictException` is thrown. The client refreshes the case and prompts the user with the updated state.

### 4.2 Break-Glass Emergency Jump Predicate
Unlike standard forward transitions, the transition trigger `BREAK_GLASS_EMERGENCY` is permitted from **ANY active state** ($S01$ through $S25$) directly to `STATE_EMERGENCY_ACTIVE` ($S22$).

```sql
-- Valid Emergency Transition Check
CREATE OR REPLACE FUNCTION validate_emergency_jump(
    p_current_state VARCHAR,
    p_target_state VARCHAR,
    p_trigger VARCHAR
) RETURNS BOOLEAN AS $$
BEGIN
    IF p_target_state = 'STATE_EMERGENCY_ACTIVE' AND p_trigger = 'BREAK_GLASS_EMERGENCY' THEN
        -- Allowed from any state except terminal CLOSED or RESOLVED
        IF p_current_state NOT IN ('STATE_RESOLVED', 'STATE_CLOSED') THEN
            RETURN TRUE;
        END IF;
    END IF;
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
```

---

## 5. Mathematical Invariants of State Transitions

$$\begin{aligned}
\mathbf{Inv\ SM\text{-}1} &: \quad \forall t \in \text{Transitions}, \quad t.\text{state\_version} = \text{Cases}(t.\text{case\_id}).\text{state\_version} \\
\mathbf{Inv\ SM\text{-}2} &: \quad t.\text{current\_state} = \text{STATE\_CLOSED} \implies t.\text{exited\_at} = \text{NULL} \quad \text{(Absorption state)} \\
\mathbf{Inv\ SM\text{-}3} &: \quad \forall t_1, t_2 \in \text{Transitions}(c), \quad t_1.\text{state\_version} < t_2.\text{state\_version} \implies t_1.\text{entered\_at} \le t_2.\text{entered\_at} \\
\mathbf{Inv\ SM\text{-}4} &: \quad \text{Transitions are strictly append-only: } \text{DELETE / UPDATE on historical transition records is prohibited.}
\end{aligned}$$
