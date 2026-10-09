# CLINOVA AI — Configuration Failure Lifecycle, Diagnostics & Recovery Model

> **Document ID:** `RES-184`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Site Reliability Engineering, Clinical Safety & Fault-Tolerance Group  

---

## 1. Architectural Failure Philosophy

In medical software, silent configuration failures can be catastrophic. If a system boots with a fallback to an unencrypted database, or defaults to an unauthenticated mode because a configuration key was mistyped, the compromise may go undetected for months.

**The Golden Law of Configuration Faults:**
$$\mathbf{FATAL\ BOOT\ HALT\ (Pre\text{-}Flight)} \quad \vee \quad \mathbf{EXPLICIT\ SAFE\ DEGRADATION\ (Runtime)}$$

1. **Pre-Flight Invariants:** If a security, persistence, or environment configuration is invalid at startup, the system **halts immediately (Exit Code 1)** before opening any network sockets.
2. **Runtime Invariants:** If an auxiliary service (such as edge AI or external sync) degrades after boot, the system degrades to a **deterministic rule mode**, alerts staff via a persistent banner, and continues core care.

---

## 2. Configuration Failure Lifecycle Matrix

Every configuration fault follows a strict five-stage response lifecycle:

```
[ STAGE 1: DETECTION ]
└── Validated via Pydantic validator, filesystem probe, or socket ping.
       │
       ▼
[ STAGE 2: FAIL-SAFE RESPONSE ]
└── Either immediate process termination (Fatal) or deterministic fallback (Non-Fatal).
       │
       ▼
[ STAGE 3: USER / ADMIN MESSAGE ]
└── Clear, actionable, un-cryptic message emitted to console or UI banner.
       │
       ▼
[ STAGE 4: AUDIT ]
└── Security exception recorded in local emergency error log.
       │
       ▼
[ STAGE 5: RECOVERY ]
└── Step-by-step remediation procedure for site engineers or technical officers.
```

---

## 3. Exhaustive Failure Scenarios

| Failure Scenario | Detection Mechanism | Fail-Safe Response | Admin / User Diagnostic Message | Recovery Action |
| :--- | :--- | :--- | :--- | :--- |
| **1. Missing `SECRET_KEY` in Prod** | Pydantic startup validator checks length in `district_hospital`. | **FATAL HALT (Exit 1)**. Backend refuses to boot. | `[BOOT_FATAL] SECRET_KEY must be provided and >= 64 characters in production!` | Inject high-entropy 64-char key into `/etc/clinova/secrets/`. |
| **2. Invalid `DATABASE_URL`** | SQLAlchemy engine creation fails regex parsing or scheme test. | **FATAL HALT (Exit 1)**. Prevents running unpersisted. | `[BOOT_FATAL] Invalid DATABASE_URL scheme. Supported: sqlite+aiosqlite or postgresql+asyncpg.` | Correct connection URI in `.env`. |
| **3. Invalid `ENVIRONMENT_ID`** | Enum validator finds unknown string token. | **FATAL HALT (Exit 1)**. Prevents running undefined clinic. | `[BOOT_FATAL] Unrecognized CLINOVA_ENVIRONMENT_ID: '{token}'. Must match 6 approved profiles.` | Set canonical profile (e.g. `ENV_PHC`). |
| **4. Invalid Database File Path** | OS write check fails on parent directory. | **FATAL HALT (Exit 1)**. SQLite cannot initialize. | `[BOOT_FATAL] Cannot write to LOCAL_DATABASE_PATH: Directory does not exist or permission denied.` | Execute `mkdir -p` and set directory permissions to `0750`. |
| **5. Storage Directory Read-Only** | Pre-flight `.clinova_probe` write test fails. | **FATAL HALT (Exit 1)**. Never fall back to public root. | `[BOOT_FATAL] STORAGE_PATH '/var/data/media' is read-only. Uploads cannot be safely stored.` | Grant write permissions to service account (`chown clinova`). |
| **6. Wildcard CORS in Production** | Field validator detects `*` in `CORS_ORIGINS`. | **FATAL HALT (Exit 1)**. Prevents credential theft. | `[BOOT_FATAL] Wildcard CORS ('*') is strictly prohibited in production environment!` | Enforce explicit domain whitelist in configuration. |
| **7. Local AI Endpoint Unreachable** | Loopback HTTP ping to `AI_BASE_URL` times out (10s). | **NON-FATAL DEGRADATION**. Switches to `local_rules`. | `[AI_DEGRADED] Local SLM unreachable. Core deterministic NEWS2 triage operating normally.` | Inspect llama.cpp service; check RAM/VRAM availability. |
| **8. District Hub Sync Unreachable** | Background sync ping to `SYNC_ENDPOINT` returns 502/timeout. | **NON-FATAL DEGRADATION**. Queues journals locally. | `[SYNC_STANDBY] District Hub unreachable. Accumulating sync journals locally on edge SQLite.` | Verify cellular/fiber WAN link; edge server continues offline. |
| **9. Forbidden Bypass Flag Passed** | Validator detects `DISABLE_DOCTOR_VERIFICATION=true`. | **FATAL HALT (Exit 1)**. Prevents safety corruption. | `[BOOT_FATAL] Forbidden safety bypass flag detected! Safety invariants cannot be disabled.` | Remove illicit override flag from deployment manifest. |

---

## 4. Diagnostics & Health Probe Endpoints

The backend provides four decoupled health endpoints allowing automated load balancers and systemd watchdogs to isolate configuration failures:

- **`GET /health`:** Basic process liveness check ($< 2\text{ms}$).
- **`GET /health/ready`:** Verifies database pool connectivity and storage write access. Returns 503 if persistence is locked.
- **`GET /health/ai`:** Reports current AI inference engine status (`LOCAL_RULES`, `LOCAL_QWEN`, or `DEGRADED`).
- **`GET /health/sync`:** Reports backlog of unsynced edge journals and district hub reachability.
