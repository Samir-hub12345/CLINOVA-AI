# CLINOVA AI — SQLite WAL & PostgreSQL / Supabase Dual-Compatibility Specification

> **Document ID:** `RES-101`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Mandate: The Dual-Database Reality

To support both **zero-cost offline edge deployments** (rural PHCs running on a single fanless Mini-PC without internet) and **scalable regional cloud networks** (central District and Tertiary hospital clusters), CLINOVA AI maintains strict dual-compatibility:
- **Local Edge:** SQLite 3.45+ operating in Write-Ahead Logging (`WAL`) mode with `PRAGMA foreign_keys = ON`.
- **Central Cloud:** PostgreSQL 15+ / Supabase with native JSONB, UUID, TIMESTAMPTZ, and Row-Level Security (RLS).

No application logic, SQL query, or ORM model may rely on proprietary database extensions that break cross-engine compatibility.

---

## 2. Comprehensive Type & Syntax Mapping Matrix

| Data Concept | PostgreSQL / Supabase Dialect | SQLite Edge WAL Dialect | Serialization & Interop Standard |
| :--- | :--- | :--- | :--- |
| **Identifiers (PK / FK)** | `UUID DEFAULT gen_random_uuid()` | `TEXT(36) NOT NULL` | Standard RFC 4122 canonical UUIDv4 string (lowercase with hyphens). |
| **Timestamps** | `TIMESTAMPTZ DEFAULT NOW()` | `TEXT NOT NULL` | Strict ISO 8601 UTC string: `YYYY-MM-DDTHH:MM:SS.ffffffZ`. |
| **Dates** | `DATE` | `TEXT` | `YYYY-MM-DD` string. |
| **Booleans** | `BOOLEAN DEFAULT FALSE` | `INTEGER DEFAULT 0 CHECK (col IN (0,1))`| Truthy = `1` / `true`; Falsy = `0` / `false`. |
| **JSON Payloads** | `JSONB NOT NULL DEFAULT '{}'::jsonb`| `TEXT NOT NULL CHECK (json_valid(col))` | Canonical compact UTF-8 JSON text. |
| **Categorical Enums** | `VARCHAR(32) CHECK (col IN (...))` | `TEXT CHECK (col IN (...))` | String constants matching canonical enum tokens. |
| **Floating Precision** | `NUMERIC(4,3)` / `NUMERIC(10,3)` | `REAL` | Clamped by application boundary validation. |
| **Autoincrementing Sequences**| `BIGSERIAL PRIMARY KEY` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Normalized as 64-bit integer. |
| **Generated Columns** | `GENERATED ALWAYS AS (...) STORED` | `GENERATED ALWAYS AS (...) STORED` | Supported identically in SQLite $\ge 3.31$ and PG $\ge 12$. |

---

## 3. SQLite WAL Configuration Directives

For local Mini-PC nodes, SQLite must be initialized with the following high-concurrency PRAGMA configuration on every connection pool startup:

```sql
-- Mandatory SQLite Edge Initialization Script
PRAGMA journal_mode = WAL;          -- Concurrent reads alongside active writes
PRAGMA synchronous = NORMAL;        -- High durability with fast sub-millisecond writes
PRAGMA foreign_keys = ON;           -- Enforces strict relational foreign key constraints
PRAGMA busy_timeout = 5000;         -- 5-second lock timeout prevents SQLITE_BUSY crashes
PRAGMA cache_size = -64000;         -- 64MB memory page cache for instant queries
PRAGMA temp_store = MEMORY;         -- Temporary indices held in RAM
PRAGMA wal_autocheckpoint = 1000;   -- Checkpoint WAL every 1000 pages
```

---

## 4. Query & Filter Dialect Normalization Layer

When querying JSON fields or filtering dates across engines, the application layer uses unified SQLAlchemy constructs that compile cleanly to both dialects:

```python
# Cross-Engine Safe Date Comparisons in Python / SQLAlchemy
# PostgreSQL compiles to: (measured_at >= NOW() - INTERVAL '24 HOURS')
# SQLite compiles to:     (datetime(measured_at) >= datetime('now', '-24 hours'))

# Cross-Engine Safe JSON Extraction:
# PostgreSQL: payload->>'factor'
# SQLite:     json_extract(payload, '$.factor')
```

---

## 5. Invariants Governing Dual-Database Compatibility

$$\begin{aligned}
\mathbf{Inv\ DB\text{-}1} &: \quad \forall t \in \text{Timestamps}, \quad t \text{ matches regular expression } \text{`^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$`} \\
\mathbf{Inv\ DB\text{-}2} &: \quad \forall u \in \text{UUIDs}, \quad \text{Length}(u) = 36 \quad \land \quad u \text{ contains 4 hyphens} \\
\mathbf{Inv\ DB\text{-}3} &: \quad \text{Foreign key enforcement is MANDATORY: SQLite nodes must run } \text{`PRAGMA foreign_keys = ON`}.
\end{aligned}$$
