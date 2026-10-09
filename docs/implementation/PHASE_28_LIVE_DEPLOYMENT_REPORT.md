# CLINOVA AI — Phase 28 Live Deployment, Hosting Integration & Operational Status Report

> **System:** CLINOVA AI Continuous Care Intelligence System  
> **Milestone:** Phase 28 — Live Deployment, Hosting Integration & GitHub Auto-Deploy  
> **Status:** **BLOCKED AT OPERATOR ACCESS BOUNDARY & REPOSITORY IDENTITY GATE**  
> **Clinical Governance:** Strictly Non-Diagnostic | Advisory Only | Mandatory Human Verification  
> **Cost Profile:** Mandatory Free Tier (₹0 / $0 Cost Baseline) strictly enforced  
> **Phase Control Policy:** Rule 1.1 strictly maintained. In accordance with Phase 28 Acceptance Criteria, because external cloud credentials and repository-identity confirmation require human operator action, status is explicitly marked **BLOCKED** rather than falsely claiming production completion.

---

## 1. Executive Summary & Verification Boundary

Phase 28 aims to establish the live production deployment of CLINOVA AI across zero-cost cloud tiers (Vercel Hobby, Render Free Web Service, and Supabase Free PostgreSQL) backed by automated release propagation from GitHub.

In strict adherence to the project's non-negotiable security mandates:
1. **Repository Identity Gate Active:** The remote origin is configured as `https://github.com/Samir-hub12345/CLIVORA-AI.git`. A spelling discrepancy exists between the GitHub repository name (`CLIVORA-AI`) and the product/workspace name (`CLINOVA-AI`). Connecting production hosting services is paused until the human operator verifies this repository identity.
2. **External Authentication Boundary:** The local environment lacks authenticated cloud credentials. Vercel CLI reports an expired/missing token (`Error: The specified token is not valid. Use vercel login`), Render does not offer an authenticated CLI or environment token, and Supabase database credentials cannot be requested or stored in plain conversation text.
3. **Hermetic Local Quality Gates:** Local builds, TypeScript typechecks, linting, offline edge synchronization unit tests, foundation safety tests, and regression test suites were executed with 100% pass rates.

---

## 2. Mandatory Repository-Identity Gate Findings

| Inspection Target | Discovered Value | Verification Status | Analysis & Risk Assessment |
|:---|:---|:---:|:---|
| **Git Remote Origin URL** | `https://github.com/Samir-hub12345/CLIVORA-AI.git` | Configured | Configured in Git config; local `origin/master` matches local `master` at commit `558c9a2`. Outbound remote network check (`git ls-remote`) encountered sandbox network isolation (`curl 7: Could not connect to github.com:443`). |
| **Active Local Branch** | `master` | Synchronized | Exactly matches tracked `origin/master` at commit `558c9a2`. |
| **Working Tree Status** | Clean | Verified | Zero uncommitted changes; all Phase 1–27 assets safely tracked. |
| **Remote Repository Name** | `CLIVORA-AI` | **DISCREPANCY** | Spelled with an **"R"** (`CLIVORA`) rather than an **"N"** (`CLINOVA`). |
| **Product & System Identity** | `CLINOVA AI` | Verified | Frontend `package.json`, `app.main`, config files, and tests refer to CLINOVA AI. |
| **Local Workspace Directory** | `c:\Users\admin\CLINOVA-AI` | Verified | Root directory uses correct spelling. |
| **Git User Attribution** | `Samir_Workspace` (`samirnjenaclasscrollno@gmail.com`) | Matched | Commits align with repo owner `Samir-hub12345`. |

### Gate Decision:
In accordance with Section 1 of Phase 28 rules:
> *"The Phase 27 report names `Samir-hub12345/CLIVORA-AI`, while the product is CLINOVA AI. Do NOT assume that repository is correct. Compare the actual Git remote, repository URL, ownership, default branch, and project contents... If the remote is missing, inaccessible, unexpectedly points to another project, or cannot be reconciled with the deployment documentation, STOP before connecting production hosting."*

**Action Required from Operator:** Confirm whether `https://github.com/Samir-hub12345/CLIVORA-AI.git` is the intended authoritative GitHub repository for production deployment, or if the repository should be renamed on GitHub to `CLINOVA-AI`.

---

## 3. Zero-Cost Cloud Provider Compatibility Audit

The prototype architecture strictly enforces a ₹0 / $0 budget:

### 3.1 Frontend: Vercel Hobby Free Tier
- **Architecture:** Next.js 15 App Router static/dynamic hybrid deployment.
- **Limits & Constraints:** 100GB monthly bandwidth, unlimited automatic preview deployments, global CDN edge routing, automatic SSL termination.
- **Cost:** ₹0 mandatory cost.
- **Compatibility:** Fully compatible. Production build verified locally (`npm run build` compiles 15 routes in 2.9s).
- **Authentication State:** **BLOCKED**. `vercel whoami` indicates: `Error: The specified token is not valid. Use vercel login to generate a new token.`

### 3.2 Backend: Render Free Web Service Tier
- **Architecture:** FastAPI ASGI web service on Python 3.12+ runtime via Uvicorn.
- **Limits & Constraints:** 512MB RAM, 0.1 CPU core. Spins down after 15 minutes of zero HTTP traffic. Cold start takes 40–50 seconds. Ephemeral filesystem (uploads in `/storage/documents` are discarded on restart).
- **Mitigation:**
  - Clinical data, case lifecycles, and audit logs are persisted exclusively in PostgreSQL, not local disk.
  - Frontend client features a graceful connection status indicator with automatic retry backoff.
- **Cost:** ₹0 mandatory cost.
- **Compatibility:** Fully compatible. Dynamic port resolution binds to `$PORT` via `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Authentication State:** **BLOCKED**. No Render CLI or API token is present in the local environment; requires dashboard authorization.

### 3.3 Database: Supabase Free PostgreSQL Tier
- **Architecture:** Dedicated PostgreSQL 16 database accessed via `asyncpg` with connection pooling.
- **Limits & Constraints:** 500MB storage cap, connection pooling via port 6543 (transaction pooler) or port 5432 (session pooler). Pauses after 7 days of inactivity (one-click unpause in dashboard).
- **Mitigation:**
  - Configured `statement_cache_size: 0` in asyncpg to prevent prepared statement collisions on Supabase/PgBouncer poolers.
  - Configured `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`.
- **Cost:** ₹0 mandatory cost.
- **Compatibility:** Fully compatible with SQLAlchemy 2.0 async models and Alembic migrations.
- **Provisioning State:** **BLOCKED**. Requires operator to provision a free project in Supabase dashboard and inject connection string into Render.

---

## 4. Local Pre-Deployment Quality & Verification Record

All pre-deployment automated checks have been executed and verified in the local workspace:

### 4.1 Frontend Quality Gates
- **TypeScript Static Typecheck (`tsc --noEmit`):**
  - Result: **0 errors**.
- **ESLint Validation (`next lint`):**
  - Result: **0 errors, 0 warnings**.
- **Client Offline Queue Tests (`npm run test:offline`):**
  - Result: **6 / 6 passed**:
    1. Node ID generation and caching: `PASSED`
    2. Payload credential sanitization: `PASSED`
    3. User scoping and isolation: `PASSED`
    4. TTL retention pruning (>7 days): `PASSED`
    5. User queue clearing on session logout: `PASSED`
    6. Sync reconciliation and conflict tracking: `PASSED`
- **Next.js Production Build (`next build`):**
  - Result: **15 authentic routes compiled in 2.9s**:
    - `○ /` (Homepage / Hero) — 173 B (106 kB JS)
    - `○ /_not-found` (404 Page) — 131 B (103 kB JS)
    - `○ /about` (System Architecture & Principles) — 173 B (106 kB JS)
    - `○ /disclaimer` (Clinical Safety & Legal Disclaimers) — 131 B (103 kB JS)
    - `○ /facilities` (Facility Capability Directory) — 2.66 kB (124 kB JS)
    - `○ /patient` (Patient Portal Dashboard) — 173 B (106 kB JS)
    - `ƒ /patient/case/[caseId]` (Patient Case Tracker) — 173 B (106 kB JS)
    - `○ /patient/intake` (Patient Intake & Digital Consent) — 10.2 kB (129 kB JS)
    - `○ /privacy` (Privacy Policy & PII Shielding) — 131 B (103 kB JS)
    - `○ /referrals` (Referral & Transfer Coordination) — 3.3 kB (124 kB JS)
    - `○ /staff` (Staff Multi-Role Portal) — 2.9 kB (124 kB JS)
    - `ƒ /staff/cases/[caseId]` (Case Detail & Full Timeline) — 20.6 kB (139 kB JS)
    - `○ /staff/review` (Attending Physician Workstation) — 5.95 kB (127 kB JS)
    - `○ /staff/triage` (Nurse Triage & NEWS2 Queue) — 7.81 kB (129 kB JS)
    - `○ /system` (System Admin Telemetry & Health) — 5.6 kB (126 kB JS)
  - Total shared JS bundle: **103 kB**.

### 4.2 Backend Foundation & Safety Probes (`test_foundation.py`)
- **Execution Command:** `pytest backend/tests/test_foundation.py -v`
- **Result:** **9 / 9 passed in 1.29s**:
  1. `test_root_endpoint_and_safety_headers`: Verified root metadata and mandatory clinical safety headers (`X-Clinical-Safety`, `X-Human-In-The-Loop`).
  2. `test_health_endpoint`: Verified legacy health endpoint.
  3. `test_api_status_and_safety`: Verified API v1 status contract.
  4. `test_liveness_probes`: Verified `/health/live` returns HTTP 200 without database overhead.
  5. `test_readiness_probe_success`: Verified `/health/ready` returns HTTP 200 with database ping.
  6. `test_readiness_probe_failure`: Verified `/health/ready` returns HTTP 503 upon database failure with zero leaked credentials or stack traces.
  7. `test_production_config_validation`: Verified production settings require 32+ char high-entropy `SECRET_KEY`, disable `DEBUG`, and block legacy bypasses.
  8. `test_database_url_dialect_adaptation`: Verified auto-conversion from `postgresql://` to `postgresql+asyncpg://`.
  9. `test_alembic_schema_version_at_head`: Verified Alembic head revision is `b84f3782910c`.

### 4.3 Full Backend Regression Test Suite
- **Execution Command:** `pytest backend/tests/ -v --tb=short`
- **Result:** **400 / 400 passed in 412.60s (100% pass rate)** across all 23 suites:
  - `ai_dataset/test_data_quality_audit.py`: 1 passed
  - `ai_dataset/test_dataset_schema.py`: 8 passed
  - `ai_evaluation/test_eval_metrics.py`: 6 passed
  - `ai_evaluation/test_evaluator_harness.py`: 3 passed
  - `ai_runtime/test_ai_runtime_harness.py`: 20 passed
  - `test_clinical_scenarios.py`: 17 passed
  - `test_foundation.py`: 9 passed
  - `test_innovation_acceptance.py`: 5 passed
  - `test_phase13_foundation.py`: 26 passed
  - `test_phase14_auth_rbac.py`: 30 passed
  - `test_phase15_intake.py`: 31 passed
  - `test_phase16_triage.py`: 54 passed
  - `test_phase17_human_review.py`: 61 passed
  - `test_phase18_ai_application.py`: 45 passed
  - `test_phase19_voice_stt.py`: 13 passed
  - `test_phase20_ocr_extraction.py`: 6 passed
  - `test_phase21_translation.py`: 12 passed
  - `test_phase22_facilitygraph_referral.py`: 7 passed
  - `test_phase23_migration.py`: 3 passed
  - `test_phase23_outcome_signalgraph.py`: 9 passed
  - `test_phase24_offline_sync.py`: 10 passed
  - `test_phase25_security_privacy.py`: 20 passed
  - `test_phase26_integration_e2e.py`: 4 passed (Journeys A, B, C, D)
- **Status:** Complete system regression verification confirmed with 0 failures, 0 errors, 0 skips.

---

## 5. Database Schema & Migration Verification

### 5.1 Migration Strategy & Head Revision
- **Alembic Head Revision:** `b84f3782910c`
- **Model Authority:** SQLAlchemy declarative models in `app.db.models` define all relational tables (`users`, `patients`, `consents`, `cases`, `vitals`, `triage_notes`, `evidence`, `clinical_decisions`, `referrals`, `facilities`, `timeline_events`, `audit_events`, `documents`, `sync_journals`, `sync_conflicts`).
- **Bootstrap Initialization:** `app.db.init_db.init_db()` provides idempotent startup schema initialization, seeds 5 baseline regional healthcare facilities and synthetic role personas, and stamps `alembic_version` to head (`b84f3782910c`).
- **Release Migration Command:**
  ```bash
  python -m alembic -c backend/alembic.ini upgrade head
  ```
- **PostgreSQL Compatibility Guards:**
  - Migrations `0002` (`a3dcfe723965`) and `0003` (`b4edef189201`) isolate PostgreSQL PL/pgSQL (`DO $$`) and `ALTER TYPE` statements behind dialect checks.
  - Dialect normalization in `app/core/config.py` standardizes `postgres://` or `postgresql://` URIs to `postgresql+asyncpg://`.

---

## 6. GitHub Auto-Deployment Architecture (GitOps)

The automated release workflow is designed as follows:

```
                  ┌───────────────────────────────┐
                  │ Local Development & Testing   │
                  │ Tests pass, commits verified  │
                  └───────────────┬───────────────┘
                                  │ git push origin master
                                  ▼
                  ┌───────────────────────────────┐
                  │ GitHub Repository (master)    │
                  │   Samir-hub12345/CLIVORA-AI   │
                  └───────┬───────────────┬───────┘
                          │               │
            Push / PR CI  │               │ Webhook Trigger
                          ▼               ▼
         ┌────────────────────────┐  ┌────────────────────────────────────┐
         │ GitHub Actions CI      │  │ Cloud Provider Release Deployment  │
         │ (.github/workflows/    │  │                                    │
         │  ci.yml)               │  ├─────────────────┬──────────────────┤
         │ - Flake8 Lint          │  │ Vercel          │ Render           │
         │ - Full Pytest Suite    │  │ Root: frontend  │ Root: backend    │
         │ - TypeScript Typecheck │  │ npm run build   │ Uvicorn ASGI     │
         │ - Offline Queue Tests  │  │ Next.js App     │ FastAPI Service  │
         │ - Next.js Prod Build   │  └────────┬────────┴────────┬─────────┘
         │ - Docker Spec Validate │           │                 │
         └────────────────────────┘           ▼                 ▼
                                         Health Check      Health Check
                                         (HTTP 200)        /health/live
```

---

## 7. Synthetic Demo Operator Workflow & Access Credentials

To allow demonstration and evaluation without compromising privacy, the application utilizes strictly synthetic demonstration personas seeded by `init_db`:

| Role Persona | Synthetic Email | Default Demo Password | Permissions & Boundary |
|:---|:---|:---|:---|
| **System Administrator** | `sysadmin@clinova.local` | `AdminDemoPass2026!` | System-wide audit logs, facility network topology, offline edge sync management. Non-clinical. |
| **Attending Physician** | `doctor@clinova.local` | `DoctorDemoPass2026!` | Clinical decision workstation, human review sign-off, SBAR referral creation, conflict resolution. |
| **Triage Nurse** | `nurse@clinova.local` | `NurseDemoPass2026!` | Patient intake queue, vital signs capture, NEWS2 calculation, triage progression. |
| **Regular Patient** | `patient@clinova.local` | `PatientDemoPass2026!` | Digital intake, informed consent, personal case tracker, symptom review. Restricted to own data. |
| **Facility Admin** | `facadmin@clinova.local` | `FacilityAdmin2026!` | Regional facility bed capacity, capability flags, transfer dispatch tracking. |

> [!NOTE]
> Demo passwords can be customized before running `init_db` or overridden securely via environment variables.

---

## 8. Clinical Safety & Boundary Safeguards

1. **Non-Diagnostic Advisory Only:** The application operates strictly as a clinical decision-support intelligence tool.
2. **Autonomous Clinical Actions Prohibited:** The API rejects any attempt to bypass human review (`AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE`) with HTTP 422 (`UNSUPPORTED_OPERATION`).
3. **Mandatory Security Headers on All Responses:**
   - `X-Clinical-Safety: Non-Diagnostic-Advisory-Only`
   - `X-Human-In-The-Loop: Required-Before-Action`
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
4. **Synthetic Data Policy:** Zero real patient data or personally identifiable information is ever processed or accepted.

---

## 9. Comprehensive Work Status: Completed vs Unverified vs Blocked

| Workflow Item | Verification Status | Details |
|:---|:---:|:---|
| **Git Remote Inspection** | **COMPLETED** | Inspected `origin` at `https://github.com/Samir-hub12345/CLIVORA-AI.git`, branch `master`. |
| **Repository Identity Gate** | **PAUSED (AWAITING OPERATOR)** | Discrepancy between GitHub repo name (`CLIVORA-AI`) and product name (`CLINOVA AI`) requires operator confirmation. |
| **Zero-Cost Constraint Audit** | **COMPLETED** | Verified free-tier compatibility across Vercel Hobby, Render Web Service, and Supabase PostgreSQL. |
| **Frontend Production Build** | **COMPLETED** | `next build` compiled 15 routes in 2.9s with 0 errors. |
| **Frontend Offline Queue Tests** | **COMPLETED** | 6/6 tests passed in `offlineQueue.test.mjs`. |
| **Backend Foundation Tests** | **COMPLETED** | 9/9 tests passed in `test_foundation.py`. |
| **Backend Health Probes** | **COMPLETED** | `/health/live` (200) and `/health/ready` (200/503 non-leaking) verified in code. |
| **Production Config Validation** | **COMPLETED** | Strict enforcement of `SECRET_KEY`, `DEBUG=False`, and disabling legacy bypass headers verified. |
| **Alembic Schema & Migrations** | **COMPLETED** | Head revision `b84f3782910c` verified with PostgreSQL compatibility guards. |
| **CI/CD Pipeline Configuration** | **COMPLETED** | `.github/workflows/ci.yml` verified for multi-stage regression testing. |
| **Supabase PostgreSQL Provisioning** | **BLOCKED** | Requires operator to create free project in Supabase dashboard. |
| **Render Web Service Deployment** | **BLOCKED** | Requires operator to link GitHub repository in Render dashboard and set secrets. |
| **Vercel Frontend Deployment** | **BLOCKED** | Requires operator authentication (`vercel login` or GitHub-Vercel integration). |
| **Live Smoke Testing on Public URLs** | **UNVERIFIED (BLOCKED BY DEPLOY)** | Cannot be performed until public URLs are live and connected. |

---

## 10. Operator Action Runbook to Complete Live Deployment

To complete Phase 28 and launch the live application, the human operator should execute the following secure steps outside chat:

### Step 1: Verify Repository Identity
Confirm that `https://github.com/Samir-hub12345/CLIVORA-AI` is the intended GitHub repository for CLINOVA AI. If desired, rename the repository on GitHub under **Settings -> Repository name** to `CLINOVA-AI` and update git remote locally:
```bash
git remote set-url origin https://github.com/Samir-hub12345/CLINOVA-AI.git
```

### Step 2: Provision Free Supabase Database
1. Go to [https://supabase.com](https://supabase.com) and create a free project named `clinova-ai-prod`.
2. Navigate to **Project Settings -> Database -> Connection string**.
3. Copy the **URI** (Transaction pooler on port 6543):
   `postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`

### Step 3: Create Free Render Web Service
1. Go to [https://render.com](https://render.com) and click **New -> Web Service**.
2. Connect the GitHub repository `Samir-hub12345/CLIVORA-AI` (or `CLINOVA-AI`).
3. Set configuration:
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
4. Set Environment Variables in Render:
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `false`
   - `DATABASE_URL` = `[Supabase connection string from Step 2]`
   - `SECRET_KEY` = `[Generate 32+ hex characters]`
   - `CORS_ORIGINS` = `https://clinova-ai.vercel.app`
   - `ALLOW_LEGACY_ACTOR_HEADERS` = `false`
   - `ALLOW_LEGACY_ANONYMOUS_FALLBACK` = `false`
   - `AI_PROVIDER_MODE` = `MOCK_DETERMINISTIC`
5. Set Health Check Path: `/health/live`.
6. Deploy service and note backend URL (e.g., `https://clinova-backend.onrender.com`).

### Step 4: Deploy Next.js Frontend on Vercel
1. Go to [https://vercel.com](https://vercel.com) and click **Add New -> Project**.
2. Import the GitHub repository `Samir-hub12345/CLIVORA-AI` (or `CLINOVA-AI`).
3. Set configuration:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `frontend`
4. Set Environment Variables in Vercel:
   - `NEXT_PUBLIC_API_URL` = `https://clinova-backend.onrender.com/api/v1` (or `NEXT_PUBLIC_API_BASE_URL` = `https://clinova-backend.onrender.com`)
     *(Note: Both variables are fully supported. The frontend client in `frontend/src/lib/api.ts` and `frontend/next.config.mjs` automatically inspects both variables and safely normalizes trailing `/api/v1` suffixes, ensuring direct client fetch calls and Next.js proxy rewrites operate identically regardless of whether `/api/v1` is explicitly appended).*
   - `NEXT_PUBLIC_APP_URL` = `https://clinova-ai.vercel.app`
5. Click **Deploy**.

### Step 5: Execute Live Verification
Once both URLs are online:
1. Probe `GET https://clinova-backend.onrender.com/health/live` (expect 200).
2. Probe `GET https://clinova-backend.onrender.com/health/ready` (expect 200).
3. Access `https://clinova-ai.vercel.app` and test login using synthetic credentials (`doctor@clinova.local` / `DoctorDemoPass2026!`).
4. Test the regular patient intake and clinician review flow.
