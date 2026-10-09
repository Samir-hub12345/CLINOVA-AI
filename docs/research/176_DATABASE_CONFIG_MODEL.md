# CLINOVA AI — Database Configuration & Dual-Engine Persistence Model

> **Document ID:** `RES-176`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Persistence Engineering, Database Reliability & Systems Safety Group  

---

## 1. Architectural Persistence Dual-Engine Foundation

As codified in Phase 8 (`docs/research/150_DATABASE_ARCHITECTURE.md`), CLINOVA AI supports exactly two relational persistence engines:
1. **SQLite 3.45+ (WAL Mode):** For single-facility Edge Mini-PCs (`PHC_EDGE`), single-laptop demonstrations (`LOCAL_DEMO`), local workstations (`DEV`), and automated suites (`TEST`).
2. **PostgreSQL 15+ / Supabase:** For multi-workstation secondary/tertiary facilities (`DISTRICT_HOSPITAL`) and cloud sandbox evaluations (`CLOUD_PREVIEW`).

Phase 9 defines the strict configuration schemas, validation rules, connection pool boundaries, and safety tripwires governing both engines without applying database migrations.

---

## 2. Accidental Production Connection Prevention

A primary catastrophe in medical software development is an engineer's local development machine inadvertently executing against a live hospital or cloud database, corrupting real clinical episodes or writing synthetic test records into permanent medical records.

### Dual-Layer Connection Safeguards

```
[ LAYER 1: SCHEME & HOST SANITIZATION (BOOT TIME) ]
├── In `dev`, `local_demo`, and `test`:
│   ├── `DATABASE_URL` MUST use `sqlite` or `sqlite+aiosqlite`.
│   └── Any PostgreSQL URL containing hostnames `*.gov.in`, `*.internal`, `*.supabase.co`,
│       or containing words `prod`, `live`, `hospital` raises an uncatchable `ConfigError`.
│
[ LAYER 2: ENVIRONMENT TAGGING & CONNECTION PROBE ]
├── Upon opening the initial database connection:
│   ├── The backend executes: `SELECT config_value FROM system_metadata WHERE key = 'environment_tag';`
│   └── If `system_metadata.environment_tag != settings.APP_ENV`, the connection terminates immediately.
```

---

## 3. SQLite Configuration & Tuning Parameters

When running on low-cost fanless Mini-PCs or developer workstations:

### 3.1 Driver & Path Rules
- **Driver:** `sqlite+aiosqlite:///` (Asynchronous I/O via Python's asyncio).
- **Filesystem Path Safety:** `LOCAL_DATABASE_PATH` must resolve to an absolute path within approved directories (`./`, `./data/`, or `/var/data/clinova/db/`). Path traversal sequences (`../..`) are strictly rejected.

### 3.2 Mandatory PRAGMA Invariants
Every SQLite database connection opened by the application pool must immediately execute the following four PRAGMAs:
```sql
-- 1. Enable Write-Ahead Logging for high-concurrency read/write operations
PRAGMA journal_mode = WAL;

-- 2. Synchronous normal provides optimal durability without SSD thrashing
PRAGMA synchronous = NORMAL;

-- 3. Strict foreign key enforcement (SQLite disables foreign keys by default!)
PRAGMA foreign_keys = ON;

-- 4. Bounded lock waiting: prevents immediate SQLITE_BUSY errors during peak triage
PRAGMA busy_timeout = 5000;
```

---

## 4. PostgreSQL / Supabase Configuration & Tuning Parameters

When running on enterprise hospital servers or managed cloud instances:

### 4.1 Driver & Connection Schema
- **Driver:** `postgresql+asyncpg://` (High-performance native async driver).
- **SSL Enforcement:** In `district_hospital` and `cloud_preview`, SSL mode must be set to `require` or `verify-full`.

### 4.2 Connection Pool Configuration
```python
# PostgreSQL Connection Pool Settings
DB_POOL_SIZE: int = 10         # Persistent open connections
DB_MAX_OVERFLOW: int = 20      # Ephemeral burst connections during casualty surges
DB_POOL_TIMEOUT: int = 30      # Seconds to wait before raising pool timeout
DB_POOL_RECYCLE: int = 1800    # Recycle connections after 30 minutes to drop stale sockets
STATEMENT_TIMEOUT_MS: int = 5000 # Terminate queries running > 5s to prevent lock exhaustion
```

---

## 5. Migration Configuration & Safety Boundaries

Phase 9 strictly **does not run migrations**, but formalizes the configuration boundary for Alembic:

1. **Explicit Migration Runner:** Migrations may only be executed via a dedicated, authenticated CLI command (`python -m clinova.db.migrate`).
2. **Never Run Auto-Migrations on Boot:** The backend web server MUST NOT execute schema migrations automatically during container startup. Automatic migrations in distributed systems cause race conditions and table deadlocks.
3. **Environment Tag Assertion:** Alembic scripts verify that the active database matches the intended target environment before applying DDL migrations.
