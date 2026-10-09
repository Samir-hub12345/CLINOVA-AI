# CLINOVA AI — Relational Database Architecture & Schema Reconciliation

> **Document ID:** `RES-150`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Database Systems Architecture & Healthcare Persistence Engineering Group  

---

## 1. Dual-Engine Relational Persistence Architecture

CLINOVA AI maintains strict dual-compatibility across two database backends:
1. **Edge Deployment (Primary Rural Target):** SQLite 3.45+ operating in Write-Ahead Logging (`WAL`) mode with `PRAGMA foreign_keys = ON` on local fanless Mini-PCs.
2. **Cloud / Regional Hub (Secondary Target):** PostgreSQL 15+ / Supabase utilizing native UUID, TIMESTAMPTZ, JSONB, and Row-Level Security (RLS).

No query, schema migration, or ORM model may utilize proprietary dialect features that break cross-engine compatibility.

---

## 2. Table Reconciliation: `triage_cases` vs. Canonical `cases`

### 2.1 The Architectural Conflict
- Early Alembic migrations (`0001` through `0009`) in the existing repository defined a central table named `triage_cases`.
- In contrast, the Phase 6 canonical data model specification (`RES-79`), Phase 7 provenance models, and `backend/app/db/models.py` specify `cases` as the root entity of the Master Case.
- Maintaining two conflicting names in the codebase introduces confusion, broken foreign keys, and mental fragmentation.

### 2.2 Definitive Architectural Resolution
1. **The Sole Canonical Table is `cases`:**
   - The architecture definitively designates `cases` as the single canonical table representing the continuous Master Case.
   - The name `triage_cases` is deprecated because CLINOVA is **Continuous Care Intelligence**, not merely a 90-second triage tool.
2. **Phase 9 Migration Roadmap (Zero-Downtime Strategy):**
   - In Phase 9, an Alembic migration will execute:
     ```sql
     -- Atomic table rename preserving all existing rows, constraints, and data
     ALTER TABLE triage_cases RENAME TO cases;
     
     -- Backward-compatibility view for any legacy reporting queries
     CREATE OR REPLACE VIEW v_legacy_triage_cases AS SELECT * FROM cases;
     ```
   - All child foreign key constraints across `vital_readings`, `evidence_records`, `caregraph_states`, `referrals`, and `case_events` will standardize on `cases(id)`.
   - **Non-Execution Invariant:** Under the Phase 8 atomic phase rule, this migration is **NOT applied or executed now**. It is documented and scheduled for Phase 9 implementation.

---

## 3. Relational Schema Standards & Engineering Invariants

| Architectural Domain | PostgreSQL / Supabase Hub | SQLite Edge WAL Engine | Unifying Contract |
| :--- | :--- | :--- | :--- |
| **Primary Keys (PK)** | `UUID DEFAULT gen_random_uuid()` | `TEXT(36) NOT NULL` | Canonical RFC 4122 UUIDv4 string (lowercase with hyphens). Generated in Python domain layer before insert. |
| **Foreign Keys (FK)** | `UUID REFERENCES table(id)` | `TEXT(36) REFERENCES table(id)` | `ON DELETE RESTRICT` for clinical history; `PRAGMA foreign_keys = ON` mandatory on SQLite edge startup. |
| **Timestamps** | `TIMESTAMPTZ DEFAULT NOW()` | `TEXT NOT NULL` | Canonical ISO 8601 UTC string: `YYYY-MM-DDTHH:MM:SS.ffffffZ`. Parsed and formatted via Python `datetime.now(timezone.utc)`. |
| **JSON Payloads** | `JSONB NOT NULL DEFAULT '{}'` | `TEXT NOT NULL DEFAULT '{}'` | SQLAlchemy `JSON` type. Compact canonical UTF-8 JSON text. |
| **Boolean Flags** | `BOOLEAN DEFAULT FALSE` | `INTEGER DEFAULT 0` | Mapped via SQLAlchemy `Boolean` type (1/0 in SQLite; true/false in PG). |
| **Autoincrementing Counters**| `BIGSERIAL PRIMARY KEY` | `INTEGER PRIMARY KEY AUTOINCREMENT` | 64-bit integer normalized across both engines. |

---

## 4. Concurrency, Immutability & Event Ledger Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MUTABLE ENTITY VS. IMMUTABLE LEDGER                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MUTABLE ENTITIES (Governed by Optimistic Concurrency Control):            │
│   • `cases`:              Tracks current status, acuity_tier, state_version │
│   • `facilities`:         Tracks current operational bed counts & status    │
│   • `facility_capabilities`: Tracks current operational equipment flags     │
│                                                                             │
│   IMMUTABLE EVENT LEDGERS (Append-Only; UPDATE & DELETE Prohibited):        │
│   • `case_events`:        Complete clinical mutation ledger                 │
│   • `audit_logs`:         Forensic compliance ledger (Section 63 BSA 2023)   │
│   • `vital_readings`:     Serial physiological time-series readings         │
│   • `evidence_records`:   Multimodal facts with spatial/acoustic pointers   │
│   • `clinician_decisions`: Physician review, override & sign-off events     │
│   • `sync_journals`:      Offline edge-to-hub replication journal           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Optimistic Concurrency Control (OCC)
To prevent lost updates when concurrent clinicians interact with the same Master Case:
```sql
UPDATE cases
SET status = :new_status,
    state_version = state_version + 1,
    updated_at = :utc_now
WHERE id = :case_id AND state_version = :current_version;
```
If row count $= 0$, the transaction rolls back and prompts the user to refresh the latest case state.

### Soft Delete vs. Tombstones
Clinical data is **never physically deleted** during active operations. If an observation is determined to be entered in error:
1. The original `evidence_records` row remains immutable.
2. A new `evidence_records` row is appended with epistemic status `UNRELIABLE` or `DISPUTED`.
3. A tombstone event is logged in `case_events` with the clinician's explicit justification.

---

## 5. Indexing & Query Optimization Strategy

To guarantee sub-100ms response times for the Doctor Queue and Clinical Review screens:

1. **Active Queue Partial Index:**
   ```sql
   -- Speeds up doctor queue queries by indexing only active cases
   CREATE INDEX ix_cases_active_queue 
   ON cases (facility_id, acuity_tier, created_at) 
   WHERE status = 'STATE_DOCTOR_QUEUED';
   ```
2. **Serial Vitals Time-Series Index:**
   ```sql
   CREATE INDEX ix_vital_readings_case_time 
   ON vital_readings (case_id, recorded_at DESC);
   ```
3. **Evidence Lineage Index:**
   ```sql
   CREATE INDEX ix_evidence_records_case_source 
   ON evidence_records (case_id, provenance_type, verification_status);
   ```
4. **Facility Capability Lookup Index:**
   ```sql
   CREATE INDEX ix_facility_capabilities_lookup 
   ON facility_capabilities (facility_id, capability_code, is_operational);
   ```
