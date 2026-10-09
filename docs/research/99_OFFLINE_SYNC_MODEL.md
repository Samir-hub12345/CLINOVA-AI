# CLINOVA AI — Offline Edge Synchronization & Conflict Resolution Model

> **Document ID:** `RES-99`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Edge-First Resilience

In rural primary health centres (PHCs) and community outreach camps across Odisha, electrical power outages and cellular uplink failures are routine. A clinical system that requires continuous cloud internet connectivity will freeze during monsoon storms, abandoning patients in waiting rooms.

CLINOVA AI enforces an **Offline Edge-First Architecture**:
- **Local Edge Node:** A low-cost fanless Mini-PC running SQLite in WAL mode hosts the local application, SLM inferencing (Whisper + PaddleOCR + Qwen3-4B), and full database persistence.
- **Central Cloud Hub:** Central PostgreSQL / Supabase cluster serves regional aggregation, multi-facility coordination, and tertiary hospital receiving portals.
- **Bi-Directional Synchronization:** When uplink connectivity is restored, the local node synchronizes incremental transactions with the cloud via an idempotent journal.

---

## 2. Four Canonical Conflict Resolution Strategies

When edge nodes operate offline, concurrent updates between local edge and central cloud can occur (e.g. an offline nurse records an observation while a teleconsultant reviews an earlier snapshot).

The data model resolves conflicts using four explicit strategies:

| Strategy Code | Name | Application Scope | Resolution Rule |
| :--- | :--- | :--- | :--- |
| `STRAT_APPEND` | **Append-Only Merging** | Events, Vitals, Timeline, Audio, Docs | Default. Non-destructive union; both records preserved in sequence. |
| `STRAT_CLINICIAN`| **Clinician Monopoly Wins** | Triage Priority, Diagnosis, Disposition | Human doctor's decision always supersedes AI inference or staff draft. |
| `STRAT_LWW` | **Last-Write-Wins (Wall Clock)** | Non-clinical metadata, phone numbers | Highest UTC timestamp prevails; older update tombstoned. |
| `STRAT_MANUAL` | **Manual Reconciliation Gate** | Demographics merge, conflicting allergies | Conflict frozen in `sync_conflicts`; surfaces for human sign-off. |

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYNCHRONIZATION JOURNAL SCHEMA                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  sync_journals (sync_id PK)                                                 │
│    ├── [Entity Type, Entity ID, Operation (INSERT/UPDATE), Local/Remote Ver]│
│    ├── [Sync Status (PENDING_UPLOAD, SYNCED, CONFLICT, FAILED)]             │
│    └── [Payload Snapshot, Hash, Conflict Resolution Strategy]              │
│                                                                             │
│  sync_conflicts (conflict_id PK, sync_id FK)                                │
│    └── [Local Entity Snapshot, Remote Entity Snapshot, Resolution Choice]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL & SQLite)

### 4.1 PostgreSQL DDL (Central Cloud Hub)

```sql
CREATE TABLE sync_journals (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id VARCHAR(64) NOT NULL, -- e.g., 'PHC-ODISHA-KALAHANDI-04'
    entity_type VARCHAR(64) NOT NULL, -- 'cases', 'vital_readings', 'evidence_records'
    entity_id VARCHAR(64) NOT NULL,   -- UUID of target record
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    operation VARCHAR(16) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'TOMBSTONE')),
    local_version INTEGER NOT NULL,
    remote_version INTEGER NOT NULL DEFAULT 1,
    sync_status VARCHAR(16) NOT NULL DEFAULT 'SYNCED'
        CHECK (sync_status IN ('PENDING_UPLOAD', 'SYNCED', 'CONFLICT', 'FAILED')),
    payload_snapshot JSONB NOT NULL,
    conflict_strategy VARCHAR(32) NOT NULL DEFAULT 'APPEND_ONLY'
        CHECK (conflict_strategy IN ('APPEND_ONLY', 'CLINICIAN_WINS', 'LAST_WRITE_WINS', 'MANUAL_GATE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sync_node_status ON sync_journals(node_id, sync_status);
CREATE INDEX ix_sync_entity ON sync_journals(entity_type, entity_id);
```

### 4.2 SQLite DDL (Local Edge Mini-PC)

```sql
CREATE TABLE sync_journals (
    sync_id TEXT PRIMARY KEY NOT NULL,
    node_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'TOMBSTONE')),
    local_version INTEGER NOT NULL,
    remote_version INTEGER NOT NULL DEFAULT 0,
    sync_status TEXT NOT NULL DEFAULT 'PENDING_UPLOAD'
        CHECK (sync_status IN ('PENDING_UPLOAD', 'SYNCED', 'CONFLICT', 'FAILED')),
    payload_snapshot TEXT NOT NULL, -- JSON string
    conflict_strategy TEXT NOT NULL DEFAULT 'APPEND_ONLY'
        CHECK (conflict_strategy IN ('APPEND_ONLY', 'CLINICIAN_WINS', 'LAST_WRITE_WINS', 'MANUAL_GATE')),
    created_at TEXT NOT NULL,
    synced_at TEXT
);

CREATE TABLE sync_conflicts (
    conflict_id TEXT PRIMARY KEY NOT NULL,
    sync_id TEXT NOT NULL REFERENCES sync_journals(sync_id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    local_payload TEXT NOT NULL,  -- JSON string
    remote_payload TEXT NOT NULL, -- JSON string
    resolution_status TEXT NOT NULL DEFAULT 'PENDING_HUMAN_REVIEW'
        CHECK (resolution_status IN ('PENDING_HUMAN_REVIEW', 'RESOLVED_LOCAL', 'RESOLVED_REMOTE', 'RESOLVED_MERGED')),
    resolved_by_actor_id TEXT REFERENCES users(id),
    resolved_at TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_sync_status ON sync_journals(sync_status);
CREATE INDEX ix_sync_entity ON sync_journals(entity_type, entity_id);
```

---

## 5. Invariants Governing Offline Synchronization

$$\begin{aligned}
\mathbf{Inv\ SYNC\text{-}1} &: \quad \forall j \in \text{SyncJournals}, \quad j.\text{sync\_status} = \text{'SYNCED'} \implies j.\text{synced\_at} \neq \text{NULL} \\
\mathbf{Inv\ SYNC\text{-}2} &: \quad \text{Clinical events and vital readings are strictly APPEND\_ONLY; they cannot be overwritten by sync.} \\
\mathbf{Inv\ SYNC\text{-}3} &: \quad \text{Primary keys across all tables are UUIDv4; zero ID collisions between disconnected nodes.}
\end{aligned}$$
