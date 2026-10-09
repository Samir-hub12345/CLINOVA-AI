# CLINOVA AI — Comprehensive Production Deployment Guide

> **System:** CLINOVA AI Continuous Care Intelligence System  
> **Milestone:** Phase 27 — Deployment Readiness & Automated Release Preparation  
> **Target Production Profile:** Zero-Mandatory-Paid-Cost Hackathon / Prototype Deployment  
> **Authoritative Repository:** [Samir-hub12345/CLIVORA-AI](https://github.com/Samir-hub12345/CLIVORA-AI.git) (`master` branch)  
> **Clinical Governance:** Strictly Non-Diagnostic | Advisory Only | Mandatory Human Verification  

---

## 1. Architectural Baseline & Deployment Topology

CLINOVA AI is structured as a decoupled multi-tier architecture, designed for reliable, zero-mandatory-cost operation across industry-standard free cloud tiers:

```
                          ┌────────────────────────────────┐
                          │         Browser Client         │
                          │   (Desktop / Mobile Safari)    │
                          └──────────────┬─────────────────┘
                                         │ HTTPS
                                         ▼
                          ┌────────────────────────────────┐
                          │        Vercel (Edge/CDN)       │
                          │   Next.js 15 App (Static/SSR)  │
                          │   clinova-ai.vercel.app        │
                          └──────────────┬─────────────────┘
                                         │ HTTPS / REST API
                                         ▼
                          ┌────────────────────────────────┐
                          │        Render (PaaS)           │
                          │   FastAPI ASGI Application     │
                          │   Python 3.12+ / Uvicorn       │
                          │   clinova-backend.onrender.com │
                          └───────┬──────────────┬─────────┘
                                  │              │
                   SQL (asyncpg)  │              │ Ephemeral File Store
                                  ▼              ▼
           ┌────────────────────────────┐  ┌─────────────────────────┐
           │     Supabase / Render      │  │ Render Container Temp   │
           │      PostgreSQL 16         │  │   /storage/documents    │
           │   (Persistent Relational)  │  │ (Scrubbed on Container  │
           └────────────────────────────┘  │         Restart)        │
                                           └─────────────────────────┘
```

### Component Breakdown
| Tier | Technology Stack | Hosting Target | Free Tier Availability & Constraints |
|:---|:---|:---|:---|
| **Frontend** | Next.js 15.5 (App Router), React 18, TypeScript 5.6 | **Vercel** | Free Hobby tier. Unlimited preview deployments, automatic SSL, global CDN edge routing. 100GB monthly bandwidth limit. |
| **Backend** | FastAPI 0.115, Uvicorn, Python 3.12+, Pydantic v2 | **Render** | Free Web Service tier. 512MB RAM, 0.1 CPU core. Spins down after 15 min of inactivity (cold start: 40–50s). Ephemeral filesystem without persistent disk. |
| **Database** | PostgreSQL 16 with async SQLAlchemy & asyncpg | **Supabase** (or Render Postgres) | Free tier: 500MB storage, connection pooler (port 6543 / 5432). Pauses after 7 days of inactivity (unpause in 1 click). Zero cost. |
| **CI/CD** | GitHub Actions & Provider-Native Git Webhooks | **GitHub** | 2,000 free runner minutes/month. Automated branch builds, PR verification, and push-to-deploy triggers. |

---

## 2. Free-Tier Constraints, Resource Limits & Mitigation

To maintain the **zero-mandatory-paid-cost constraint**, the deployment architecture respects all cloud provider limitations:

1. **Render Web Service Inactivity Spin-Down**:
   - *Limitation:* Free instances spin down after 15 minutes of zero HTTP traffic. The subsequent incoming request experiences a 40–50 second cold start latency.
   - *Mitigation:* The frontend client implements a non-blocking liveness probe (`/health/live`) with retry backoff and displays an explicit, friendly cold-start banner (`"Connecting to backend service..."`) rather than an opaque failure screen.
2. **Ephemeral Backend Filesystem**:
   - *Limitation:* Free Render containers do not provide persistent disk volumes. Any uploaded test files or generated OCR artifacts stored in `/storage/documents` are discarded upon container restart or deployment.
   - *Mitigation:* All authoritative patient clinical states, triage snapshots, clinician decisions, audit logs, and timeline events are persisted in the **remote PostgreSQL database**. Local file uploads serve solely as ephemeral staging buffers.
3. **Database Connection Pooling**:
   - *Limitation:* Free PostgreSQL tiers enforce max connection caps (e.g., Supabase enforces ~60 direct connections; Render free database enforces 50 connections).
   - *Mitigation:* The backend engine in `app/db/session.py` configures connection pooling with `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, and `pool_timeout=30`, preventing stale-connection leakage and connection exhaustion.
4. **Client-Side Storage Boundary**:
   - *Limitation:* Browser offline queue uses `sessionStorage` and `localStorage`, which are unencrypted at rest on local hardware.
   - *Mitigation:* Sensitive authentication tokens and credentials are automatically scrubbed from offline queues (`frontend/src/lib/offlineQueue.ts`), a 7-day TTL pruning policy is enforced, and queues are purged upon session logout.

---

## 3. Environment Variable Specification

### 3.1 Backend Configuration (`backend/.env` / Render Dashboard)

| Variable | Type | Required | Default / Example | Purpose & Boundary |
|:---|:---|:---:|:---|:---|
| `ENVIRONMENT` | string | **Yes** | `production` | Switches environment mode. Enforces strict production safety validation. |
| `DEBUG` | boolean | **Yes** | `false` | Must be `false` in production. Prevents internal traceback disclosure. |
| `DATABASE_URL` | string | **Yes** | `postgresql+asyncpg://...` | Connection URI for hosted PostgreSQL. Automatically standardizes `postgres://` or `postgresql://` to `postgresql+asyncpg://`. |
| `SECRET_KEY` | string | **Yes** | *[High-Entropy Secret]* | **32+ random characters**. Required for JWT signing. Deployment fails fast if default dev key is supplied. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | No | `60` | JWT token validity window in minutes. |
| `CORS_ORIGINS` | string / JSON | **Yes** | `https://clinova-ai.vercel.app` | Comma-separated or JSON list of authorized frontend origins. Prevents unauthorized cross-origin browser requests. |
| `BACKEND_HOST` | string | No | `0.0.0.0` | Container network bind address. Defaults to `0.0.0.0` in production. |
| `BACKEND_PORT` | integer | No | `8000` | Port for Uvicorn. Automatically synchronized with Render's `$PORT` environment variable. |
| `UPLOAD_DIR` | string | No | `storage/documents` | Filesystem location for temporary document upload processing. |
| `AI_PROVIDER_MODE` | string | No | `MOCK_DETERMINISTIC` | `MOCK_DETERMINISTIC` maintains $0 hermetic operation. `LOCAL_OLLAMA` enables local on-prem inference where supported. |
| `ALLOW_LEGACY_ACTOR_HEADERS` | boolean | **Yes** | `false` | Disables legacy header actor injection in production. Strict JWT bearer authorization only. |
| `ALLOW_LEGACY_ANONYMOUS_FALLBACK` | boolean | **Yes** | `false` | Blocks unauthenticated anonymous access. |

### 3.2 Frontend Configuration (`frontend/.env` / Vercel Dashboard)

| Variable | Type | Required | Example | Purpose & Boundary |
|:---|:---|:---:|:---|:---|
| `NEXT_PUBLIC_API_URL` | string | **Yes** | `https://clinova-backend.onrender.com/api/v1` | Public API base URL used by client-side fetchers and Next.js rewrites. |
| `NEXT_PUBLIC_APP_URL` | string | **Yes** | `https://clinova-ai.vercel.app` | Canonical public application URL for metadata and OpenGraph resolution. |

> [!CAUTION]
> **Zero Secrets in Frontend**: `NEXT_PUBLIC_` variables are baked into browser-facing JavaScript bundles. **Never** define `SECRET_KEY`, `DATABASE_URL`, or administrative API tokens in the frontend configuration.

---

## 4. Health, Liveness & Readiness Probes

CLINOVA AI exposes standardized, probe-ready health endpoints adhering to cloud orchestrator standards:

### 4.1 Liveness Endpoint: `GET /health/live` (and legacy `GET /health`)
- **Path:** `/health/live` (or `/api/v1/health/live`)
- **Status Code:** `200 OK`
- **Response Contract:**
  ```json
  {
    "status": "healthy",
    "liveness": "alive",
    "app": "Clinova AI",
    "version": "2.0.0",
    "environment": "production"
  }
  ```
- **Use Case:** Used by Render and container orchestrators to detect process responsiveness. Does not touch backend persistence layer.

### 4.2 Readiness Endpoint: `GET /health/ready`
- **Path:** `/health/ready` (or `/api/v1/health/ready`)
- **Status Code (Healthy):** `200 OK`
  ```json
  {
    "status": "ready",
    "database": "connected",
    "app": "Clinova AI",
    "version": "2.0.0",
    "environment": "production"
  }
  ```
- **Status Code (Unhealthy):** `503 Service Unavailable`
  ```json
  {
    "status": "unready",
    "database": "unavailable",
    "app": "Clinova AI",
    "version": "2.0.0",
    "environment": "production"
  }
  ```
- **Security & Privacy Boundary:** The readiness probe executes a fast `SELECT 1` ping with a 3.0-second timeout. If the database connection fails, the probe logs the failure server-side and returns a generic `503 Service Unavailable` payload. **No database credentials, hostnames, SQL statements, or stack traces are ever exposed in the response.**

---

## 5. Step-by-Step Deployment Procedure

### Step 1: Hosted PostgreSQL Database Provisioning (Supabase)
1. Log in to [Supabase](https://supabase.com) (free tier).
2. Create a new project: `clinova-ai-prod` (select region close to your target users, e.g., Mumbai / Singapore).
3. Set a strong database password and record it securely outside Git.
4. In **Project Settings -> Database -> Connection string**, select the **URI** format under **Transaction Pooler** (or Session pooler):
   `postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`
5. Note: CLINOVA AI automatically adapts `postgresql://` to `postgresql+asyncpg://` at runtime.

### Step 2: Database Initialization & Migration Strategy
CLINOVA AI separates **initial schema creation** from **incremental release migrations**:

#### 2.1 Fresh Database Provisioning (Initial Setup)
Foundational relational tables (`users`, `patients`, `consents`, `cases`, `facilities`) are defined authoritatively in SQLAlchemy models (`app.db.models`). On a fresh hosted PostgreSQL database, initialize the full schema and seed baseline facilities and test personas:

```bash
# Option A: Run bootstrap CLI locally pointing to hosted database
$env:DATABASE_URL="postgresql+asyncpg://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres"
python -m app.db.init_db

# Option B: Automatic Startup Initialization
# CLINOVA AI automatically bootstraps all required schemas, facilities, and synthetic
# clinical baseline profiles on first container startup via app.db.init_db.init_db().
```
`init_db` creates all tables, seeds the 5 baseline facilities and synthetic accounts, and stamps `alembic_version` to head (`b84f3782910c`).

#### 2.2 Incremental Release Migrations (Subsequent Releases)
For any schema changes introduced after initial provisioning:
```bash
python -m alembic -c backend/alembic.ini upgrade head
```
*(Note: `app/db/session.py` configures `statement_cache_size: 0` in asyncpg to prevent duplicate prepared statement errors on Supabase/PgBouncer transaction poolers on port 6543).*

### Step 3: Backend Deployment (Render)
1. Log in to [Render](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `Samir-hub12345/CLIVORA-AI`.
4. Configure service parameters:
   - **Name:** `clinova-backend`
   - **Region:** Frankfurt / Singapore / Oregon (match database region)
   - **Branch:** `master`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. Configure Environment Variables in Render Dashboard:
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `false`
   - `DATABASE_URL` = `[Supabase connection string from Step 1]`
   - `SECRET_KEY` = `[Generate via: python -c "import secrets; print(secrets.token_hex(32))"]`
   - `CORS_ORIGINS` = `https://clinova-ai.vercel.app`
   - `ALLOW_LEGACY_ACTOR_HEADERS` = `false`
   - `ALLOW_LEGACY_ANONYMOUS_FALLBACK` = `false`
   - `AI_PROVIDER_MODE` = `MOCK_DETERMINISTIC`
6. In **Advanced Settings**, configure Health Check:
   - **Health Check Path:** `/health/live`
7. Click **Create Web Service**. Wait for build completion and note the backend URL (e.g., `https://clinova-backend.onrender.com`).

### Step 4: Frontend Deployment (Vercel)
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Select your GitHub repository: `Samir-hub12345/CLIVORA-AI`.
4. Configure project settings:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm ci`
5. Configure Environment Variables in Vercel Dashboard:
   - `NEXT_PUBLIC_API_URL` = `https://clinova-backend.onrender.com/api/v1`
   - `NEXT_PUBLIC_APP_URL` = `https://clinova-ai.vercel.app`
6. Click **Deploy**.
7. Once deployed, copy your assigned Vercel domain (e.g., `https://clinova-ai.vercel.app`) and ensure it matches the `CORS_ORIGINS` set in Render in Step 3.

---

## 6. GitHub-Connected Automatic Deployment Pipeline

CLINOVA AI is configured for GitOps release propagation from GitHub:

```
                  ┌───────────────────────────────┐
                  │ Local Development & Testing   │
                  │ npm test / pytest 397 passing │
                  └───────────────┬───────────────┘
                                  │ git push origin master
                                  ▼
                  ┌───────────────────────────────┐
                  │ GitHub Repository (master)    │
                  │ Trigger Actions CI & Webhooks │
                  └───────┬───────────────┬───────┘
                          │               │
            PR / Push CI  │               │ Webhook Trigger
                          ▼               ▼
         ┌────────────────────────┐  ┌────────────────────────────────────┐
         │ GitHub Actions CI      │  │ Cloud Provider Release Deployment  │
         │ - Flake8 / Lint        │  │                                    │
         │ - 397 Pytest Matrix    │  ├─────────────────┬──────────────────┤
         │ - TS Typecheck         │  │ Vercel          │ Render           │
         │ - Offline Queue Unit   │  │ Rebuilds        │ Rebuilds         │
         │ - Next.js Prod Build   │  │ Frontend App    │ Backend ASGI     │
         └────────────────────────┘  └────────┬────────┴────────┬─────────┘
                                              │                 │
                                              ▼                 ▼
                                         Health Check      Health Check
                                         (HTTP 200)        /health/live
```

### Automation Policy:
1. **Pull Requests & Non-Master Branches**:
   - Vercel automatically deploys ephemeral **Preview Deployments** for pull requests.
   - GitHub Actions runs typechecks, linter, offline queue unit tests, and the 397 backend test regression matrix.
2. **Master Branch Pushes**:
   - Triggers automated production deployment on both Vercel and Render.
   - Render detects changes within `backend/` and triggers a blue-green zero-downtime container swap.
   - Vercel detects changes within `frontend/` and redeploys the edge build.
3. **Database Migration Policy**:
   - Migrations are **never** executed by frontend builds or distributed workers independently.
   - Schema updates are managed explicitly through controlled release steps (`alembic upgrade head`) or the idempotent startup initializer (`app.db.init_db.init_db()`).

---

## 7. Operational Runbooks & Recovery

### 7.1 Inspecting Logs & Health Failures
- **Backend Logs:** Render Dashboard -> `clinova-backend` -> **Logs** tab. Live stdout/stderr streaming includes structured startup notices and clinical safety governance logs.
- **Frontend Logs:** Vercel Dashboard -> `clinova-frontend` -> **Deployments** -> Select deployment -> **Runtime Logs** or **Build Logs**.
- **Readiness Probes:** Query `https://clinova-backend.onrender.com/health/ready`. A `503` indicates database unreachable; verify Supabase project is active and connection strings match.

### 7.2 Rollback Procedure
If a production release introduces unexpected runtime errors:
1. **Frontend Instant Rollback (Vercel):**
   - Go to Vercel Dashboard -> **Deployments**.
   - Find the previous known-good deployment.
   - Click **...** -> **Promote to Production**. Instant edge rollback occurs within seconds.
2. **Backend Rollback (Render):**
   - Go to Render Dashboard -> **Deploys**.
   - Select the last successful build.
   - Click **Rollback to this deploy**.
3. **Git Revert:**
   - Execute `git revert HEAD` locally, verify tests, and push to `master`.

---

## 8. Clinical Safety Mandates & Disclaimers

CLINOVA AI operates under strict clinical safety boundaries:
1. **Non-Diagnostic Policy:** The software provides clinical decision-support and care feasibility intelligence. It **does not** formulate autonomous diagnoses, issue automatic prescriptions, or admit/discharge patients.
2. **Human-in-the-Loop Requirement:** All clinical disposition actions require explicit authentication, credential verification, and authoritative review by qualified healthcare personnel.
3. **Security Headers:** Every HTTP response strictly delivers:
   - `X-Clinical-Safety: Non-Diagnostic-Advisory-Only`
   - `X-Human-In-The-Loop: Required-Before-Action`
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
4. **Synthetic Data Policy:** The system operates strictly with synthetic patient data and simulated regional facility capabilities.
