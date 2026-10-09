# CLINOVA AI — Advisory Care Orchestration & Pathways Data Model

> **Document ID:** `RES-93`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: The Advisory-Only Boundary

The Orchestration Engine synthesizes patient biological state from **CAREGRAPH** with real-world infrastructure constraints from **FACILITYGRAPH** to recommend the **Safest Achievable Care Pathway**.

Under the **Advisory-Only Invariant**:
$$\text{The system CANNOT independently execute admissions, referrals, surgical bookings, or discharges.}$$
Every orchestration output carries `human_review_required = TRUE`. The clinical user retains absolute authority to accept, modify, override, or reject the advisory path.

---

## 2. Six Canonical Advisory Actions

The Orchestration Engine selects one of six canonical advisory actions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SIX CANONICAL ADVISORY ACTIONS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. ASK       ──> Present targeted follow-up prompt to resolve gap          │
│  2. VERIFY    ──> Request nurse bedside vital sign measurement              │
│  3. CONTINUE  ──> Advance case along current regular outpatient pathway     │
│  4. OBSERVE   ──> Hold patient in observation bay; repeat vitals in 30 mins │
│  5. ESCALATE  ──> Immediate bedside physician call; divert to Resuscitation │
│  6. REFER     ──> Initiate closed-loop transfer to capable higher facility  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION & CARE PATHWAYS SCHEMA                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── orchestration_recommendations (orchestration_id PK, case_id FK)      │
│    │     └── [Suggested Action, Rationale, Safety Constraints, Doctor Status│
│    │                                                                        │
│    └── care_pathways (pathway_id PK, case_id FK)                            │
│          └── [Pathway Type (ROUTINE, WARD, REFERRAL, OT, EMG), Status]      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `orchestration_recommendations` Table

```sql
CREATE TABLE orchestration_recommendations (
    orchestration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    suggested_action VARCHAR(32) NOT NULL 
        CHECK (suggested_action IN ('ASK', 'VERIFY', 'CONTINUE', 'OBSERVE', 'ESCALATE', 'REFER')),
    rationale TEXT NOT NULL,
    safety_constraints JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["DO_NOT_DISCHARGE_WITHOUT_REPEAT_BP"]
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE,  -- Inviolable constraint: always TRUE
    status VARCHAR(16) NOT NULL DEFAULT 'PROPOSED'
        CHECK (status IN ('PROPOSED', 'ACCEPTED', 'MODIFIED', 'OVERRIDDEN', 'REJECTED')),
    decided_by UUID REFERENCES users(id),
    decided_at TIMESTAMPTZ,
    override_reason TEXT,
    engine_version VARCHAR(64) NOT NULL DEFAULT 'clinova-orchestration-v2'
);

CREATE INDEX ix_orch_case ON orchestration_recommendations(case_id);
CREATE INDEX ix_orch_status ON orchestration_recommendations(status);
```

### 4.2 `care_pathways` Table

```sql
CREATE TABLE care_pathways (
    pathway_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    pathway_type VARCHAR(32) NOT NULL 
        CHECK (pathway_type IN ('ROUTINE', 'WARD', 'REFERRAL', 'EMERGENCY', 'OT', 'FOLLOW_UP')),
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    initiated_by UUID NOT NULL REFERENCES users(id),
    current_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'
        CHECK (current_status IN ('ACTIVE', 'SUSPENDED', 'TRANSFERRED', 'COMPLETED', 'ABORTED')),
    completed_at TIMESTAMPTZ,
    pathway_metadata JSONB NOT NULL DEFAULT '{}'::jsonb -- Stores pathway-specific references
);

CREATE INDEX ix_care_pathways_case ON care_pathways(case_id, current_status);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE orchestration_recommendations (
    orchestration_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evaluated_at TEXT NOT NULL,
    suggested_action TEXT NOT NULL CHECK (suggested_action IN ('ASK', 'VERIFY', 'CONTINUE', 'OBSERVE', 'ESCALATE', 'REFER')),
    rationale TEXT NOT NULL,
    safety_constraints TEXT NOT NULL DEFAULT '[]', -- JSON string
    human_review_required INTEGER NOT NULL DEFAULT 1 CHECK (human_review_required = 1),
    status TEXT NOT NULL DEFAULT 'PROPOSED' CHECK (status IN ('PROPOSED', 'ACCEPTED', 'MODIFIED', 'OVERRIDDEN', 'REJECTED')),
    decided_by TEXT REFERENCES users(id),
    decided_at TEXT,
    override_reason TEXT,
    engine_version TEXT NOT NULL DEFAULT 'clinova-orchestration-v2'
);

CREATE TABLE care_pathways (
    pathway_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    pathway_type TEXT NOT NULL CHECK (pathway_type IN ('ROUTINE', 'WARD', 'REFERRAL', 'EMERGENCY', 'OT', 'FOLLOW_UP')),
    initiated_at TEXT NOT NULL,
    initiated_by TEXT NOT NULL REFERENCES users(id),
    current_status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (current_status IN ('ACTIVE', 'SUSPENDED', 'TRANSFERRED', 'COMPLETED', 'ABORTED')),
    completed_at TEXT,
    pathway_metadata TEXT NOT NULL DEFAULT '{}' -- JSON string
);
```

---

## 6. Invariants Governing Orchestration

$$\begin{aligned}
\mathbf{Inv\ ORCH\text{-}1} &: \quad \forall o \in \text{Recommendations}, \quad o.\text{human\_review\_required} = \text{TRUE} \quad \text{(Advisory-Only Invariant)} \\
\mathbf{Inv\ ORCH\text{-}2} &: \quad o.\text{status} \in \{\text{'OVERRIDDEN'}, \text{'REJECTED'}\} \implies o.\text{override\_reason} \neq \text{NULL} \\
\mathbf{Inv\ ORCH\text{-}3} &: \quad \text{Only one active care pathway branch may exist per Master Case simultaneously: } \\
& \quad \forall c, \quad \text{Count}(\{p \in \text{CarePathways}(c) : p.\text{current\_status} = \text{'ACTIVE'}\}) \le 1
\end{aligned}$$
