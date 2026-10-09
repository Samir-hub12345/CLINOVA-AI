# CLINOVA AI — Phase 9 Formal Decision Log

> **Document ID:** `DECISION-LOG-PHASE-9`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Security Governance & Engineering Leadership  

---

## 1. Executive Summary

This document formally records the sixteen authoritative architectural, security, and configuration decisions adopted during Phase 9. These decisions bind all subsequent phases (Phase 10 AI runtime, Phase 11 database, Phase 12 UI) and cannot be altered without formal Architecture Decision Record (ADR) review.

---

## 2. Phase 9 Formal Decision Registry

### Decision 9.1: Two-Dimensional Environment Identity Model
- **Decision:** Bifurcate runtime identity into `APP_ENV` (infrastructure topology: `dev`, `local_demo`, `phc_edge`, `district_hospital`, `cloud_preview`, `test`) and `CLINOVA_ENVIRONMENT_ID` (clinical facility profile: `ENV_GOV_HOSPITAL` through `ENV_CAMPUS_HEALTH`).
- **Rationale:** Decouples where the software runs (e.g. edge Mini-PC vs. cloud sandbox) from how the clinical facility operates (e.g. rural PHC vs. corporate clinic).

### Decision 9.2: Rejection of Tailwind CSS in Favor of Native CSS & Design Tokens
- **Decision:** Formally reject Tailwind CSS for the CLINOVA frontend. Enforce Next.js 15+ App Router, TypeScript 5.6+, plain CSS Modules, W3C CSS Custom Properties (CSS variables) for clinical tokens, and native CSS Grid / Flexbox.
- **Rationale:** Healthcare interfaces require rigid, unpolluted design tokens for triage acuity tiers (Red/Amber/Yellow/Green) and high-contrast readability. Plain CSS eliminates compilation bloat, external build dependencies, and utility-class churn over multi-decade clinical lifecycles.

### Decision 9.3: Absolute Prohibition of `SUPABASE_SERVICE_ROLE_KEY` in Frontend
- **Decision:** Strictly forbid `SUPABASE_SERVICE_ROLE_KEY` or any administrative bypass credential from being referenced in client code, passed via `NEXT_PUBLIC_*`, or included in frontend Docker images.
- **Rationale:** The service-role key completely bypasses Supabase Row Level Security. Leaking it grants total read/write/drop control over all hospital patient records.

### Decision 9.4: Synthetic Data by Default for Non-Certified Deployments
- **Decision:** Enforce `CLINOVA_DATA_MODE=synthetic` by default across `dev`, `local_demo`, `cloud_preview`, and `test`. Switching to `live` requires explicit multi-key confirmation and is permitted solely in certified physical installations (`district_hospital` and `phc_edge`).
- **Rationale:** Eliminates accidental ingestion, processing, or leakage of real patient Protected Health Information (PHI) under DPDP Act 2023 penalties.

### Decision 9.5: Zero-Cost Core Mandate (₹0 / Month OpEx)
- **Decision:** Ensure that the entire clinical workflow (intake, triage, NEWS2, queueing, doctor verification, prescription sign-off) operates with zero mandatory paid third-party APIs (OpenAI, Gemini, paid cloud OCR, paid cloud speech, Google Maps).
- **Rationale:** Guarantees rural public health facilities can operate perpetually without subscription churn when grant or pilot budgets lapse.

### Decision 9.6: Fail-Closed Pre-Flight Boot Validation
- **Decision:** If any required secret, database connection, storage path, or environment token fails validation during server boot, the process terminates immediately (Exit Code 1).
- **Rationale:** Prevents the application from running in an insecure, unauthenticated, or unpersisted state.

### Decision 9.7: Session Immutability Invariant
- **Decision:** Prohibit dynamic, in-app switching of the environment profile by end-users or clinicians during active shifts.
- **Rationale:** Mid-session environment switching corrupts active clinical queues, disables required hazard screenings, and invalidates cryptographic forensic audit chains.

### Decision 9.8: Local Clinic Server Authoritative Persistence
- **Decision:** Designate the Local Clinic Server (fanless Mini-PC hosting SQLite) as the sole authoritative persistence core for rural edge clinics; frontline staff tablets act as thin clients.
- **Rationale:** Prevents distributed database split-brain conditions across low-cost tablets while ensuring 100% autonomous operation during weeks of internet blackout.

### Decision 9.9: Dual Database Engine Configuration Boundary
- **Decision:** Restrict supported persistence engines to SQLite 3.45+ WAL mode (edge, demo, dev, test) and PostgreSQL 15+ asyncpg (district hospital, cloud preview).
- **Rationale:** Matches low-power hardware constraints on edge while providing enterprise concurrency in large hospitals without codebase divergence.

### Decision 9.10: Media Storage Isolation & Private Access
- **Decision:** Forbid saving raw audio or medical slip photos to public static web directories. Use isolated local filesystem paths (`0750` permissions) or private cloud buckets with signed 15-minute URLs.
- **Rationale:** Prevents unauthenticated scraping or search engine indexing of sensitive patient diagnostic documents.

### Decision 9.11: AI Unavailable Degradation Law
- **Decision:** When local SLM, Whisper, or OCR engines fail or are disabled, the system enters `AI_UNAVAILABLE` mode; core deterministic triage continues uninterrupted, staff are notified via an explicit badge, and zero simulated/fake AI results are generated.
- **Rationale:** Upholds clinical safety: never simulate intelligence; always maintain transparent manual entry.

### Decision 9.12: Absolute Prohibition of Wildcard CORS in Production
- **Decision:** Strictly reject `allow_origins=["*"]` in `district_hospital` and `cloud_preview` configurations.
- **Rationale:** Prevents malicious third-party websites from executing cross-origin authenticated requests against internal hospital APIs.

### Decision 9.13: Hardcoded Clinical Safety Rules Immune to Feature Flags
- **Decision:** Formally ban feature flags that attempt to disable doctor verification gates, deterministic NEWS2 scores, Section 63 BSA audit logging, or zero-imputation rules.
- **Rationale:** Statutory clinical safety standards (NMC Reg 27, BSA 2023) are immutable legal requirements that cannot be bypassed by operational tunables.

### Decision 9.14: Strict Operational Log Sanitization (Zero PHI)
- **Decision:** Enforce automated regex redaction filters across all application log sinks, stripping patient names, Aadhaar, ABHA, and phone numbers before serialization.
- **Rationale:** Protects patient privacy by preventing sensitive medical data from entering unencrypted developer consoles or log aggregators.

### Decision 9.15: DPDP Act Storage Limitation Retention Policy
- **Decision:** Cap raw media storage retention at 30 days (PHC) or 90 days (hospital), after which an authorized daemon purges raw binary images/audio, retaining solely the cryptographic SHA-256 hash.
- **Rationale:** Adheres to Section 8(7) of the DPDP Act 2023, minimizing long-term data breach exposure while preserving legal forensic proof.

### Decision 9.16: Mandatory Configuration Manifest Versioning
- **Decision:** Require every deployed configuration profile to maintain an immutable metadata manifest (`configuration_id`, `version`, `approved_by`, `change_reason`, `config_hash`) recorded in the audit ledger.
- **Rationale:** Guarantees regulatory compliance under Section 63 BSA 2023 by proving that computing systems were operating under approved, un-tampered configurations.
