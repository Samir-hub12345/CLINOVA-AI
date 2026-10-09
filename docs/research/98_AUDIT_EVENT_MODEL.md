# CLINOVA AI — Tamper-Evident Medico-Legal Audit Ledger Model

> **Document ID:** `RES-98`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Foundations: Section 65B Indian Evidence Act Compliance

In Indian jurisprudence, digital evidence submitted in medical malpractice, accident claim (MACT), or criminal inquest trials must satisfy **Section 65B of the Indian Evidence Act, 1872** (now Section 63 of Bharatiya Sakshya Adhiniyam, 2023):
1. **Uninterrupted Electronic Device Integrity:** Proof that the computer system was operating properly without unauthorized software alteration.
2. **Immutable Audit Trail:** Continuous chain of custody establishing who recorded or altered clinical entries.
3. **Cryptographic Integrity Hash:** Algorithmic verification that historical records have not been retroactively edited or purged after an adverse patient outcome.

CLINOVA AI implements a dedicated **Tamper-Evident Medico-Legal Audit Ledger** (`audit_events`), providing cryptographically verifiable proof of all clinical, administrative, and AI interactions.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MEDICO-LEGAL AUDIT LEDGER SCHEMA                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    └── audit_events (audit_id PK, case_id FK)                               │
│          ├── [Action Type, Resource Type, Resource ID, Actor ID, Role]      │
│          ├── [Terminal ID, IP Address, Client User-Agent]                   │
│          └── [Cryptographic Hash, Prev Hash, Sec 65B Certificate Meta]      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

```sql
CREATE TABLE audit_events (
    audit_id BIGSERIAL PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    actor_id UUID NOT NULL REFERENCES users(id),
    actor_role VARCHAR(32) NOT NULL,
    action_type VARCHAR(64) NOT NULL, -- e.g., 'VIEW_DOSSIER', 'CLINICIAN_MODIFY', 'SIGN_DISPOSITION'
    resource_type VARCHAR(64) NOT NULL, -- 'cases', 'vital_readings', 'triage_notes'
    resource_id VARCHAR(64) NOT NULL,
    delta_payload JSONB NOT NULL DEFAULT '{}'::jsonb, -- Diff of changes: { before: {...}, after: {...} }
    client_ip_address VARCHAR(45) NOT NULL,
    terminal_identifier VARCHAR(64) NOT NULL, -- Hardware MAC / station token
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    prev_audit_hash VARCHAR(64) NOT NULL,
    integrity_hash VARCHAR(64) NOT NULL,
    sec65b_device_id VARCHAR(64) NOT NULL DEFAULT 'CLINOVA-NODE-01'
);

CREATE INDEX ix_audit_case ON audit_events(case_id, timestamp ASC);
CREATE INDEX ix_audit_actor ON audit_events(actor_id, timestamp DESC);
CREATE INDEX ix_audit_action ON audit_events(action_type);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE audit_events (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    encounter_id TEXT NOT NULL REFERENCES encounters(id) ON DELETE RESTRICT,
    facility_id TEXT NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
    actor_id TEXT NOT NULL REFERENCES users(id),
    actor_role TEXT NOT NULL,
    action_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    delta_payload TEXT NOT NULL DEFAULT '{}', -- JSON string
    client_ip_address TEXT NOT NULL,
    terminal_identifier TEXT NOT NULL,
    timestamp TEXT NOT NULL, -- ISO-8601 UTC
    prev_audit_hash TEXT NOT NULL,
    integrity_hash TEXT NOT NULL,
    sec65b_device_id TEXT NOT NULL DEFAULT 'CLINOVA-NODE-01'
);

CREATE INDEX ix_audit_case ON audit_events(case_id, timestamp ASC);
CREATE INDEX ix_audit_actor ON audit_events(actor_id, timestamp DESC);
CREATE INDEX ix_audit_action ON audit_events(action_type);
```

---

## 5. Invariants Governing Audit Ledgers

$$\begin{aligned}
\mathbf{Inv\ AUDIT\text{-}1} &: \quad \forall a_n \in \text{AuditEvents}, \quad a_n.\text{integrity\_hash} = \text{SHA256}(a_n.\text{prev\_audit\_hash} \parallel a_n.\text{audit\_id} \parallel a_n.\text{delta\_payload}) \\
\mathbf{Inv\ AUDIT\text{-}2} &: \quad \text{Audit log records are immutable and append-only: ZERO updates or deletions allowed.} \\
\mathbf{Inv\ AUDIT\text{-}3} &: \quad \text{Every clinician modification and break-glass emergency event MUST trigger an audit row.}
\end{aligned}$$
