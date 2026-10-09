# CLINOVA AI — Data Retention, Archival & Purging Data Model

> **Document ID:** `RES-100`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Foundations: Indian Healthcare Retention Mandates

Health data retention in India is governed by strict statutory rules that supersede general consumer data deletion requests:
1. **National Medical Commission (NMC) Regulations 2023 (Regulation 28):** Inpatient medical records must be preserved for a minimum of **3 years** from the date of commencement of treatment.
2. **Indian Public Health Standards (IPHS 2022):** Medico-Legal Cases (MLC), post-mortem reports, and surgical records must be retained for **7 years** (or until completion of court litigation).
3. **Pediatric Rule:** Medical records of pediatric minors must be retained until the minor reaches the age of majority (18 years) plus 3 years (i.e. until age 21).
4. **DPDP Act 2023 (Section 12 - Right to Erasure Exception):** Personal data retention is legally permitted and required where retention is necessary for compliance with any law for the time being in force (such as NMC/IPHS retention mandates).

---

## 2. Four-Stage Data Archival Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FOUR-STAGE DATA LIFECYCLE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  [1. ACTIVE / OPERATIONAL] (0 to 90 Days)                                   │
│  └── Hot storage; sub-second query latency; full read/write active.         │
│        │                                                                    │
│        ▼                                                                    │
│  [2. COLD IN-DATABASE ARCHIVE] (90 Days to 3-7 Years)                       │
│  └── Read-only locked; compressed storage; indexed on case_id and patient_id│
│        │                                                                    │
│        ▼                                                                    │
│  [3. SEALED MERKLE OBJECT ARCHIVE] (Post Statutory Period)                 │
│  └── Cryptographically sealed tarball; exported to WORM cloud storage;      │
│      tombstone retained in relational DB.                                   │
│        │                                                                    │
│        ▼                                                                    │
│  [4. ANONYMIZED RESEARCH REDACTION]                                         │
│  └── PII stripped; epidemiological telemetry extracted for SIGNALGRAPH.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational Schema Architecture

```sql
CREATE TABLE data_retention_policies (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name VARCHAR(64) NOT NULL UNIQUE,
    case_category VARCHAR(32) NOT NULL CHECK (case_category IN (
        'OUTPATIENT_ROUTINE', 'INPATIENT_WARD', 'SURGICAL_OT', 'MEDICO_LEGAL_MLC', 'PEDIATRIC'
    )),
    retention_period_days INTEGER NOT NULL,
    statutory_authority VARCHAR(128) NOT NULL, -- e.g., 'NMC_REGULATIONS_2023_REG_28'
    auto_seal_after_inactivity_days INTEGER NOT NULL DEFAULT 30,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE archived_cases (
    archive_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    retention_policy_id UUID NOT NULL REFERENCES data_retention_policies(policy_id),
    lifecycle_stage VARCHAR(32) NOT NULL DEFAULT 'COLD_ARCHIVE'
        CHECK (lifecycle_stage IN ('COLD_ARCHIVE', 'SEALED_OBJECT', 'ANONYMIZED_RESEARCH', 'PURGED')),
    merkle_seal_hash VARCHAR(64) NOT NULL,
    archive_storage_uri VARCHAR(512), -- e.g., 's3://clinova-archive/2026/CAS-0042.tar.zst'
    retained_until_date DATE NOT NULL,
    is_legal_hold BOOLEAN NOT NULL DEFAULT FALSE, -- Litigation lock prevents purging
    legal_hold_justification TEXT,
    archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_archive_retention_date ON archived_cases(retained_until_date, lifecycle_stage);
CREATE INDEX ix_archive_legal_hold ON archived_cases(is_legal_hold);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE data_retention_policies (
    policy_id TEXT PRIMARY KEY NOT NULL,
    policy_name TEXT NOT NULL UNIQUE,
    case_category TEXT NOT NULL CHECK (case_category IN ('OUTPATIENT_ROUTINE', 'INPATIENT_WARD', 'SURGICAL_OT', 'MEDICO_LEGAL_MLC', 'PEDIATRIC')),
    retention_period_days INTEGER NOT NULL,
    statutory_authority TEXT NOT NULL,
    auto_seal_after_inactivity_days INTEGER NOT NULL DEFAULT 30,
    created_at TEXT NOT NULL
);

CREATE TABLE archived_cases (
    archive_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE RESTRICT,
    retention_policy_id TEXT NOT NULL REFERENCES data_retention_policies(policy_id),
    lifecycle_stage TEXT NOT NULL DEFAULT 'COLD_ARCHIVE' CHECK (lifecycle_stage IN ('COLD_ARCHIVE', 'SEALED_OBJECT', 'ANONYMIZED_RESEARCH', 'PURGED')),
    merkle_seal_hash TEXT NOT NULL,
    archive_storage_uri TEXT,
    retained_until_date TEXT NOT NULL, -- YYYY-MM-DD
    is_legal_hold INTEGER NOT NULL DEFAULT 0 CHECK (is_legal_hold IN (0, 1)),
    legal_hold_justification TEXT,
    archived_at TEXT NOT NULL
);
```

---

## 5. Invariants Governing Data Retention

$$\begin{aligned}
\mathbf{Inv\ RET\text{-}1} &: \quad \forall a \in \text{ArchivedCases}, \quad a.\text{is\_legal\_hold} = \text{TRUE} \implies a.\text{lifecycle\_stage} \neq \text{'PURGED'} \\
\mathbf{Inv\ RET\text{-}2} &: \quad \text{Today}() < a.\text{retained\_until\_date} \implies a.\text{lifecycle\_stage} \neq \text{'PURGED'} \quad \text{(Statutory Lock)} \\
\mathbf{Inv\ RET\text{-}3} &: \quad \text{Archival preserves Merkle verification hashes; zero loss of cryptographic proof.}
\end{aligned}$$
