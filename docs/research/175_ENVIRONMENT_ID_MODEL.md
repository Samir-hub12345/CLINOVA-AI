# CLINOVA AI — Environment Identity Loading, Validation & Session Immutability Model

> **Document ID:** `RES-175`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Security Governance & Runtime Engineering Group  

---

## 1. Architectural Reconciliation: `APP_ENV` vs. `CLINOVA_ENVIRONMENT_ID`

Phase 4 introduced facility operational contexts (`ENV_GOV_HOSPITAL` through `ENV_CAMPUS_HEALTH`), while Phase 8 introduced deployment topologies (`DEV`, `LOCAL_DEMO`, `PHC_EDGE`, `DISTRICT_HOSPITAL`, `CLOUD_PREVIEW`, `TEST`).

Phase 9 establishes the definitive two-dimensional identity model:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TWO-DIMENSIONAL IDENTITY MODEL                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   DIMENSION 1: INFRASTRUCTURE TOPOLOGY (`APP_ENV`)                          │
│   ├── Determines database drivers, network hosts, log sinks, and TLS.       │
│   └── Values: `dev` | `local_demo` | `phc_edge` | `district_hospital` |     │
│               `cloud_preview` | `test`                                      │
│                                                                             │
│   DIMENSION 2: CLINICAL FACILITY PROFILE (`CLINOVA_ENVIRONMENT_ID`)          │
│   ├── Determines clinical queue depth, specialist routing, and intake mode. │
│   └── Values: `ENV_GOV_HOSPITAL` | `ENV_PHC` | `ENV_PUBLIC_CAMP` |          │
│               `ENV_COMPANY_CLINIC` | `ENV_INDUSTRIAL_HEALTH` |              │
│               `ENV_CAMPUS_HEALTH`                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Both variables must be explicitly defined and validated at system startup.

---

## 2. Boot-Time Loading & Ingestion Pipeline

The environment identity loading pipeline executes in four deterministic stages before any application service binds to a port:

```
[ STAGE 1: OS ENVIRONMENT & FILE DISCOVERY ]
├── Read host environment variables (systemd / container environment).
├── If running locally, ingest `.env` or `.env.local` via python-dotenv / Pydantic.
└── Parse raw string tokens for `APP_ENV` and `CLINOVA_ENVIRONMENT_ID`.
       │
       ▼
[ STAGE 2: ENUMERATION & REGISTRY VALIDATION ]
├── Assert `APP_ENV` exists within canonical `AppEnv` enumeration.
├── Assert `CLINOVA_ENVIRONMENT_ID` exists within `ClinovaFacilityProfile`.
└── Retrieve corresponding `FacilityProfileConfig` from internal registry.
       │
       ▼
[ STAGE 3: CROSS-DIMENSION SANITY VALIDATION ]
├── Verify compatibility: e.g., `APP_ENV=phc_edge` must not run `ENV_GOV_HOSPITAL` without explicit flag.
├── Verify secret strength against `APP_ENV` requirements (e.g. 64-char key for production).
└── Verify data mode: `CLINOVA_DATA_MODE=live` is rejected if `APP_ENV` in [`dev`, `local_demo`, `test`].
       │
       ▼
[ STAGE 4: IMMUTABLE SINGLETON FREEZING ]
├── Freeze settings object as read-only singleton in `app.core.config.settings`.
└── Log configuration fingerprint (SHA-256 hash of non-secret settings) to console.
```

---

## 3. Session Immutability Invariant: Prohibition of Dynamic Switching

A catastrophic vulnerability in multi-tenant or multi-facility medical software is allowing clinicians or nurses to toggle the system environment profile via an in-app dropdown or URL query parameter during an active shift.

**The Session Immutability Invariant:**
$$\mathbf{Inv\ ENV\text{-}1}: \quad \forall \text{ active encounter } e, \quad e.\text{environment} = \text{BootEnvironment} = \mathbf{Constant}$$

### Why Dynamic Switching is Strictly Prohibited:
1. **Queue Corruption:** If an operator switches a District Hospital queue into a Rural PHC mode, specialist triage routing is suddenly suppressed, and critical cardiac patients would be relegated to general single-doctor queues.
2. **Hazard Screening Bypass:** In an industrial plant (`ENV_INDUSTRIAL_HEALTH`), switching to `ENV_COMPANY_CLINIC` suppresses toxic gas and chemical exposure questionnaires, leading to misdiagnosed industrial poisonings.
3. **Audit Ledger Invalidation:** Changing the environment identifier mid-session corrupts the cryptographic Merkle chain provenance required under Section 63 Bharatiya Sakshya Adhiniyam 2023.

**Remedy for Facility Re-Assignment:**  
Altering `CLINOVA_ENVIRONMENT_ID` requires an authorized administrator to update the server's configuration file, log the change in the administrative audit ledger, and execute a **full application service restart**.

---

## 4. Behavior on Invalid or Conflicting Identity Tokens

If an un-recognized, malformed, or malicious identity string is supplied (e.g., `APP_ENV=production_hack` or `CLINOVA_ENVIRONMENT_ID=DROP_TABLE`):

```
1. FATAL LOG EMISSION:
   [CRITICAL] [BOOT_HALT] Invalid environment configuration detected!
   Field: 'CLINOVA_ENVIRONMENT_ID' | Value: 'UNKNOWN_VAL'
   Error: Value is not a valid ClinovaFacilityProfile enumeration.

2. FAIL-SAFE TERMINATION:
   Process terminates immediately with Exit Code 1.
   Zero network ports are opened.
   Zero database connections are initialized.

3. PRESERVATION OF INVARIANTS:
   No fallback to an assumed default is permitted if the explicitly passed token is invalid.
   The system fails closed.
```

---

## 5. Protection of Test & Staging Environments

To guarantee that automated test suites or developer machines never accidentally connect to live hospital databases or write synthetic records into production archives:

1. **Production URL Blocklist:** If `APP_ENV` is `test`, `dev`, or `local_demo`, any `DATABASE_URL` containing `.internal`, `.gov.in`, `prod`, or live IP ranges causes an immediate validation failure.
2. **Database Suffix Enforcement:** In `test`, the database path must match `:memory:` or end with `-test.db` / `_test`.
3. **Synthetic Data Guardrail:** In `dev`, `local_demo`, and `test`, setting `CLINOVA_DATA_MODE=live` raises an unrecoverable `ConfigurationError` during settings initialization.
