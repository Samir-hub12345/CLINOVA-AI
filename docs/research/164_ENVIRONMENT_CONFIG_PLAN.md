# CLINOVA AI — Environment, Secrets & Configuration Foundation Research Plan

> **Document ID:** `RES-164`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Security Engineering & Clinical Configuration Group  

---

## 1. Executive Summary & Phase Objective

Phase 9 establishes the definitive, secure, and verifiable configuration, environment-variable, secret-management, runtime-profile, and environment-separation foundation for CLINOVA AI.

Following the completion of the Technical Architecture (Phase 8), this phase operates strictly within the **Atomic Phase Rule**:
- **No Phase 10 Execution:** No AI runtimes are integrated or initialized.
- **No Database Migrations:** No migration scripts are executed; schemas are not altered.
- **No Production UI Implementation:** No component trees or client-side application code are written.
- **No Production Authentication Implementation:** No auth flows or credential verification routines are deployed.
- **No External API Integration:** No third-party network connections are opened.
- **No Cloud Deployment:** System remains un-deployed.

Phase 9 defines the complete declarative configuration schema, prevents credentials and secrets from leaking into client bundles or version control, enforces synthetic data by default for development and evaluation, guarantees zero-cost operations across edge and cloud topologies, and formally reconciles architectural contradictions (specifically rejecting Tailwind CSS in favor of Next.js plain CSS variables and native layouts).

---

## 2. Research Plan & Methodological Workflow

The configuration research execution follows a strict 8-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 9 METHODOLOGICAL WORKFLOW                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1. INVENTORY]         Scan current repository .env, package.json, and     │
│                         backend settings; identify legacy drift.            │
│       │                                                                     │
│       ▼                                                                     │
│  [2. RECONCILE]         Reconcile Phase 4 Environment Profiles with         │
│                         Phase 8 Technical Architecture and Frontend stack.  │
│       │                                                                     │
│       ▼                                                                     │
│  [3. DESIGN]            Define strongly typed Pydantic Settings schemas,    │
│                         profile hierarchies, and Next.js public boundaries. │
│       │                                                                     │
│       ▼                                                                     │
│  [4. SECURITY AUDIT]    Execute STRIDE configuration threat model; classify │
│                         all secrets; establish rotation and leak protocols. │
│       │                                                                     │
│       ▼                                                                     │
│  [5. VALIDATION]        Formulate fail-safe startup validation rules,       │
│                         synthetic data guardrails, and error behaviors.     │
│       │                                                                     │
│       ▼                                                                     │
│  [6. DOCUMENTATION]     Produce 30 exhaustive research and decision docs.   │
│       │                                                                     │
│       ▼                                                                     │
│  [7. SELF-AUDIT]        Verify all 28 phase invariants and 40 report heads. │
│       │                                                                     │
│       ▼                                                                     │
│  [8. REPORT & HALT]     Deliver final summary; state READY FOR HUMAN REVIEW.│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 12 Fundamental Configuration Principles

Every configuration item, runtime profile, and environment variable in CLINOVA AI is governed by twelve inviolable laws:

1. **SAFE DEFAULTS:** Every variable defaults to the most secure, least privileged, and offline-resilient setting. If an environment variable is omitted, the system defaults to local offline, zero-cost, synthetic-data mode.
2. **EXPLICIT ENVIRONMENT:** Implicit environment guessing (e.g., detecting `NODE_ENV` or checking hostname) is strictly prohibited. The runtime deployment mode (`APP_ENV`) and facility profile (`CLINOVA_ENVIRONMENT_ID`) must be explicitly declared and validated at boot.
3. **NO SECRETS IN SOURCE CODE:** No private keys, passwords, database credentials, or JWT signing secrets may exist in source files, git commits, Dockerfiles, or client bundles.
4. **NO SERVICE-ROLE KEY IN BROWSER:** Under no circumstances is `SUPABASE_SERVICE_ROLE_KEY` or any administrative bypass credential exposed to client-side bundles or `NEXT_PUBLIC_*` prefixes.
5. **NO PRODUCTION CREDENTIALS IN LOCAL DEMO:** Local demo, development, and test environments are strictly forbidden from holding or connecting to live hospital or production databases.
6. **SYNTHETIC DATA BY DEFAULT:** All non-production environments default to `CLINOVA_DATA_MODE=synthetic`. Ingestion or display of real Protected Health Information (PHI) requires affirmative multi-key verification and production environment confirmation.
7. **ZERO-COST BY DEFAULT:** The default configuration profile requires zero paid external APIs (OpenAI, Gemini, paid cloud OCR, paid cloud speech, Google Maps). All core pipelines operate using local open-source models or deterministic rule sets.
8. **FAIL CLOSED FOR MISSING CRITICAL SECRETS:** In production mode, if a required cryptographic secret or database credential is missing or unvalidated, the backend terminates immediately at boot-time rather than operating in an unauthenticated or degraded state.
9. **CLEAR LOCAL/OFFLINE BEHAVIOR:** Edge deployments (PHC, Outreach Camps) must clearly define authoritative local server parameters (local SQLite WAL, local disk storage, local LAN endpoints) that operate without internet connectivity.
10. **ENVIRONMENT CONFIGURATION ≠ USER ROLE:** Environment configuration defines facility capabilities and operational modes. It must never be conflated with, or substitute for, user-level Role-Based Access Control (RBAC).
11. **ENVIRONMENT CONFIGURATION ≠ CLINICAL DECISION:** Configuration profiles alter queue limits, triage workflows, and device defaults, but CANNOT alter or disable clinical safety invariants (e.g., human-in-the-loop verification, deterministic NEWS2 scores, Section 63 BSA provenance chaining).
12. **CONFIGURATION VERSIONING:** Every deployed configuration profile must possess an immutable version identifier (`configuration_id`, `configuration_version`, `approved_by`) recorded in tamper-evident audit logs.

---

## 4. Key Upstream Reconciliations & Architectural Corrections

### 4.1 Frontend Technology Correction (Tailwind CSS Rejection)
In Phase 8 (`docs/research/136_FRONTEND_ARCHITECTURE.md`), styling was inadvertently noted as "Tailwind CSS with standardized clinical design tokens."  
**Correction:** As directed by project leadership, **Tailwind CSS is NOT approved** for CLINOVA AI. CLINOVA AI enforces:
- Next.js 15+ App Router
- TypeScript 5.6+ with strict typing
- Plain CSS with CSS Modules
- Native CSS Custom Properties (CSS variables) for clinical design tokens (e.g., `--color-slate-900`, `--color-acuity-red`, `--font-clinical-mono`)
- Native CSS Grid and Flexbox layouts
- Professional icon library (`lucide-react`)
This rejection is codified across Phase 9 to eliminate utility-class bloat, avoid CSS generation coupling, and maintain pure standards-based styling.

### 4.2 Canonical `cases` Table & Configuration Scope
Phase 8 reconciled the database entity name to `cases`. Phase 9 ensures that database configuration scripts and environment paths enforce single-database constraints without legacy table divergence.

### 4.3 Environment Token Standardization
Phase 4 defined six operational facility profiles: `ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_COMPANY_CLINIC`, `ENV_INDUSTRIAL_HEALTH`, `ENV_CAMPUS_HEALTH`. Phase 8 introduced deployment topology tokens: `DEV`, `LOCAL_DEMO`, `PHC_EDGE`, `DISTRICT_HOSPITAL`, `CLOUD_PREVIEW`, `TEST`.  
Phase 9 formally bifurcates and connects these two orthogonal dimensions:
- **`APP_ENV`:** The infrastructure deployment target (`dev`, `local_demo`, `phc_edge`, `district_hospital`, `cloud_preview`, `test`).
- **`CLINOVA_ENVIRONMENT_ID`:** The clinical facility operational profile (`ENV_GOV_HOSPITAL`, `ENV_PHC`, etc.).

---

## 5. Phase 9 Documentation Deliverables Matrix

Phase 9 authors exactly 30 authoritative specifications in `docs/research/`:

| Doc ID | Filename | Topic Scope |
| :--- | :--- | :--- |
| `RES-164` | `164_ENVIRONMENT_CONFIG_PLAN.md` | Executive foundation plan & principles |
| `RES-165` | `165_CONFIGURATION_SCHEMA.md` | Strongly typed Pydantic & Zod settings schema |
| `RES-166` | `166_SECRET_CLASSIFICATION.md` | Comprehensive taxonomy of secrets and credentials |
| `RES-167` | `167_FRONTEND_BACKEND_CONFIG_BOUNDARY.md` | Next.js `NEXT_PUBLIC_*` vs FastAPI server-only boundary |
| `RES-168` | `168_DEV_ENVIRONMENT.md` | Local developer workstation configuration |
| `RES-169` | `169_LOCAL_DEMO_ENVIRONMENT.md` | Single-laptop offline demonstration configuration |
| `RES-170` | `170_PHC_EDGE_ENVIRONMENT.md` | Rural Primary Health Centre edge Mini-PC configuration |
| `RES-171` | `171_DISTRICT_HOSPITAL_ENVIRONMENT.md` | Multi-workstation District Hospital on-prem configuration |
| `RES-172` | `172_CLOUD_PREVIEW_ENVIRONMENT.md` | Cloud preview & stakeholder evaluation configuration |
| `RES-173` | `173_TEST_ENVIRONMENT.md` | Automated CI/CD and regression test configuration |
| `RES-174` | `174_CLINOVA_ENVIRONMENT_PROFILES.md` | The 6 operational healthcare facility profiles |
| `RES-175` | `175_ENVIRONMENT_ID_MODEL.md` | Environment identity loading, validation & immutability |
| `RES-176` | `176_DATABASE_CONFIG_MODEL.md` | Dual SQLite WAL / PostgreSQL configuration & safety |
| `RES-177` | `177_STORAGE_CONFIG_MODEL.md` | Local filesystem & Supabase Storage abstractions |
| `RES-178` | `178_AI_CONFIG_BOUNDARY.md` | Pluggable local AI configuration & offline fallbacks |
| `RES-179` | `179_CORS_NETWORK_CONFIG.md` | Network ingress, CORS domains & TLS enforcement |
| `RES-180` | `180_OFFLINE_CONFIG_MODEL.md` | Offline autonomy, replication modes & state machine |
| `RES-181` | `181_SYNTHETIC_DATA_MODE.md` | Synthetic data safety flags & real-data gating |
| `RES-182` | `182_FEATURE_FLAG_MODEL.md` | Declarative feature flags & inviolable clinical gates |
| `RES-183` | `183_LOGGING_CONFIG_MODEL.md` | Zero-PHI structured logging & audit configurations |
| `RES-184` | `184_CONFIG_FAILURE_MODEL.md` | Configuration fault detection, recovery & fallbacks |
| `RES-185` | `185_CONFIGURATION_THREAT_MODEL.md` | STRIDE configuration threat analysis & mitigations |
| `RES-186` | `186_EDGE_CONFIG_MODEL.md` | Thin-client frontline device & local server topology |
| `RES-187` | `187_CLOUD_CONFIG_MODEL.md` | Central cloud hub & hybrid synchronization setup |
| `RES-188` | `188_ZERO_COST_CONFIG_MODEL.md` | ₹0 zero-cost open-source dependency verification |
| `RES-189` | `189_CONFIGURATION_VERSIONING.md` | Configuration audit trail & change management |
| `RES-190` | `190_CONFIGURATION_TRACEABILITY.md` | Bidirectional traceability to BPUT, NMC & DPDP |
| `RES-191` | `191_PHASE_9_CONCLUSION.md` | Final synthesis with 40 mandatory report sections |
| `SOURCES-9`| `SOURCES_PHASE_9.md` | Statutory, cryptographic & technical citations |
| `DECISIONS-9`| `PHASE_9_DECISIONS.md` | Formal configuration decision log (Decisions 9.1–9.16) |

---

## 6. Phase Completion Criteria

Phase 9 is deemed complete when:
1. All 30 specified markdown documents are authored and physically verified on disk.
2. The frontend styling correction rejecting Tailwind CSS is explicitly codified.
3. Every secret is categorized with zero leakage risk to client bundles.
4. Zero production application code in `frontend/` or `backend/` has been altered.
5. All 40 mandated sections of `191_PHASE_9_CONCLUSION.md` are documented.
6. The final phase status is unambiguously marked **READY FOR HUMAN REVIEW**.
