# CLINOVA AI — Deployment & Operations Guide

**Document Version:** 1.0.0  
**Target Platform:** Primary Health Centers (PHCs), District Hospitals, Outreach Clinics, Campus Health Centers  
**Applicability:** Production, Staging, and Local Demonstration Environments  
**Problem Scope:** Multimodal Healthcare Triage Specification (PS03)

---

> [!WARNING]
> ### 🔒 Clinical Safety & Operational Mandate
> **Educational prototype and triage-support platform only.** CLINOVA AI does not diagnose, prescribe treatment, or replace qualified medical professionals. All deployment environments must retain the persistent amber clinical safety banner on all screens and ensure human clinician sign-off gates are active before clinical use.

---

## Table of Contents

1. [Deployment Overview](#1-deployment-overview)
2. [Prerequisites & System Requirements](#2-prerequisites--system-requirements)
3. [Environment Variables Reference](#3-environment-variables-reference)
4. [Production Configuration Guidelines](#4-production-configuration-guidelines)
5. [Database Setup & Data Lifecycle](#5-database-setup--data-lifecycle)
6. [Backend Deployment (FastAPI)](#6-backend-deployment-fastapi)
7. [Frontend Deployment (Next.js)](#7-frontend-deployment-nextjs)
8. [Docker Compose Deployment (Recommended)](#8-docker-compose-deployment-recommended)
9. [Non-Docker / Bare-Metal Deployment Steps](#9-non-docker--bare-metal-deployment-steps)
10. [Deployment Order & Dependency Graph](#10-deployment-order--dependency-graph)
11. [Production Verification & Smoke Testing](#11-production-verification--smoke-testing)
12. [Troubleshooting & Diagnostics](#12-troubleshooting--diagnostics)
13. [Security & Healthcare Data Considerations](#13-security--healthcare-data-considerations)
14. [Backup, Rollback & Disaster Recovery](#14-backup-rollback--disaster-recovery)
15. [Post-Deployment Monitoring & Telemetry](#15-post-deployment-monitoring--telemetry)
16. [Comprehensive Deployment Checklist](#16-comprehensive-deployment-checklist)

---

## 1. Deployment Overview

CLINOVA AI is packaged as an interconnected multi-tier application comprising:
1. **Next.js 14 Frontend**: SSR and static web client running on Node.js 18/20 LTS, listening on port `3000`.
2. **FastAPI Backend**: Asynchronous REST API service powered by Uvicorn ASGI on Python 3.12+, listening on port `8000`.
3. **PostgreSQL 16 Database**: Relational persistence for electronic health records (EHR), triage cases, clinical encounters, and immutable audit logs, listening on port `5432`.
4. **Redis 7 In-Memory Cache**: High-speed key-value cache and queue management, listening on port `6379`.

### Architecture Topology

```text
       Internet / Hospital Intranet
                     │
                     ▼
          ┌─────────────────────┐
          │ Reverse Proxy / TLS │ (e.g., Nginx / Caddy on 80/443)
          └──────────┬──────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│ Next.js Frontend │   │  FastAPI Backend │
│ (Port 3000)      │   │  (Port 8000)     │
└──────────────────┘   └─────────┬────────┘
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
            ┌──────────────────┐   ┌──────────────────┐
            │  PostgreSQL 16   │   │     Redis 7      │
            │  (Port 5432)     │   │   (Port 6379)    │
            └──────────────────┘   └──────────────────┘
```

---

## 2. Prerequisites & System Requirements

### 2.1 Hardware Requirements

| Resource | Minimum (Demo / Testing) | Recommended (Production / District Hospital) |
| :--- | :--- | :--- |
| **CPU** | 2 vCPU / Cores | 4+ vCPU / Cores |
| **Memory (RAM)** | 4 GB RAM | 8 GB - 16 GB RAM |
| **Disk Storage** | 20 GB SSD | 50 GB - 100 GB NVMe SSD |
| **Network** | 10 Mbps LAN | 100 Mbps+ LAN (Gigabit Ethernet recommended) |

### 2.2 Software Requirements

| Dependency | Minimum Version | Verified Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Docker** | 24.0+ | Docker Engine 26.x | Containerized runtime |
| **Docker Compose**| 2.20+ | Docker Compose v2.27+ | Multi-container orchestration |
| **Node.js** | 18.17.0+ LTS | Node.js 20.x Alpine | Non-Docker frontend build |
| **Python** | 3.11+ | Python 3.12 / 3.14 | Non-Docker backend runtime |
| **PostgreSQL** | 15+ | PostgreSQL 16 Alpine | Primary relational EHR database |
| **Redis** | 6.2+ | Redis 7.2 Alpine | Caching and session state |

---

## 3. Environment Variables Reference

All runtime configuration is managed through environment variables loaded from the root `.env` file or injected via container orchestration.

### 3.1 Master Configuration Matrix

| Variable Name | Required | Default / Example Value | Description |
| :--- | :---: | :--- | :--- |
| `BACKEND_PORT` | No | `8000` | Port on which FastAPI / Uvicorn listens. |
| `FRONTEND_PORT` | No | `3000` | Port on which Next.js Node server listens. |
| `ENVIRONMENT` | Yes | `production` | Deployment environment (`development`, `staging`, `production`). |
| `DEBUG` | No | `false` | When `false`, suppresses SQL query logs and debug traces. |
| `SECRET_KEY` | **Yes** | *[Generate with openssl]* | Secret key used for signing HS256 JWT access tokens. |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://postgres:postgres@localhost:5432/clinova` | Asynchronous SQLAlchemy database connection string. |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Connection string for Redis cache instance. |
| `CORS_ORIGINS` | **Yes** | `["http://localhost:3000"]` | Allowed CORS origins for browser fetch requests. In production, set to public hospital domain. |
| `GEMINI_API_KEY` | No | `""` (Empty) | Google Gemini API key. If left blank, Clinova AI seamlessly uses local deterministic mock models (`DEMO_MODE=True`). |
| `DEMO_MODE` | No | `true` | When `true`, enables built-in public health demo scenarios and deterministic mock fallbacks. |
| `LLM_PROVIDER` | No | `mock` (or `gemini`) | Provider adapter for narrative SOAP summary synthesis. |
| `STT_PROVIDER` | No | `local` | Speech-to-text provider adapter (`local`, `faster-whisper`, `mock`). |
| `OCR_PROVIDER` | No | `local` | Document OCR parsing adapter (`local`, `paddleocr`, `mock`). |
| `TRANSLATION_PROVIDER`| No | `local` | Regional language translation adapter (`local`, `indictrans2`, `mock`). |
| `DEFAULT_FACILITY`| No | `Government District Hospital` | Default facility name pre-filled on intake cases. |
| `RETENTION_HOURS` | No | `24` | Hours before temporary media and unapproved case buffers expire. |
| `NEXT_PUBLIC_API_URL`| **Yes**| `http://localhost:8000` | Browser-accessible base URL of the FastAPI backend. |

---

## 4. Production Configuration Guidelines

### 4.1 Generating Production Secrets
In production, you **must never** use default secret keys. Generate a cryptographically secure 64-character secret:

```bash
# Using OpenSSL (Linux/macOS/Git Bash)
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Set this output as `SECRET_KEY` in your production `.env` file.

### 4.2 Configuring CORS Origins
In `backend/app/core/config.py`, `CORS_ORIGINS` accepts either a comma-separated list or a JSON array string:
```bash
# Example for district hospital intranet deployment
CORS_ORIGINS="https://triage.districthospital.gov.in,https://10.0.1.50:3000"
```

### 4.3 Offline / Air-Gapped Mode
For rural Primary Health Centers (PHCs) or field health camps operating without active internet connectivity:
1. Leave `GEMINI_API_KEY=""`.
2. Set `DEMO_MODE=true`.
3. Set `LLM_PROVIDER=mock`, `STT_PROVIDER=local`, `OCR_PROVIDER=local`, `TRANSLATION_PROVIDER=local`.
4. The system functions 100% offline with zero external cloud dependencies.

---

## 5. Database Setup & Data Lifecycle

### 5.1 Database Specifications
- **Engine:** PostgreSQL 16 (Alpine)
- **Database Name:** `clinova`
- **Default User:** `postgres`
- **Driver:** `asyncpg` via SQLAlchemy 2.0 async engine.

### 5.2 Automatic Lifespan Initialization & Seeding
On backend startup, the FastAPI `lifespan` handler (`backend/app/main.py`) performs automated bootstrapping:
1. **Schema Creation:** Executes `await conn.run_sync(Base.metadata.create_all)` to create all required tables (`users`, `patients`, `consultations`, `triage_cases`, `audit_logs`).
2. **Initial Seed Verification:** Inspects the `users` and `triage_cases` tables.
3. **Demo Account Provisioning:** If the database is fresh, it automatically seeds:
   - Clinical accounts: `doctor@clinova.ai`, `patient@clinova.ai`, `admin@clinova.ai`.
   - Sample patient charts: `CLN-2026-10482`, `CLN-2026-21890`, `CLN-2026-34901`.
   - 6 Synthetic public health triage cases: `CLV-DEMO-001` to `CLV-DEMO-006`.

### 5.3 Manual Database Creation (if self-hosted)
If using an existing PostgreSQL cluster rather than Docker:
```sql
CREATE DATABASE clinova;
CREATE USER clinova_user WITH ENCRYPTED PASSWORD 'StrongSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE clinova TO clinova_user;
```
Then configure:
```bash
DATABASE_URL="postgresql+asyncpg://clinova_user:StrongSecurePassword123!@localhost:5432/clinova"
```

---

## 6. Backend Deployment (FastAPI)

### 6.1 Containerized Execution
The backend `Dockerfile` uses `python:3.12-slim`:
- Installs `build-essential` and `curl`.
- Installs Python dependencies via `pip install --no-cache-dir -r requirements.txt`.
- Exposes port `8000`.
- In production containers, run Uvicorn with multiple workers:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```

### 6.2 Health Verification
Test backend health immediately after starting:
```bash
curl -f http://localhost:8000/api/v1/health
```

---

## 7. Frontend Deployment (Next.js)

### 7.1 Multi-Stage Production Build
The frontend `Dockerfile` implements a high-efficiency multi-stage build using `node:20-alpine`:
1. `deps`: Installs production and build dependencies via `npm install`.
2. `builder`: Executes `npm run build` to compile the Next.js 14 App Router application.
3. `runner`: Sets `NODE_ENV=production`, copies optimized `.next` and `public` assets, and starts the Next.js standalone server on port `3000` via `npm start`.

### 7.2 API Endpoint Binding
During build and runtime, the frontend communicates with the backend via `NEXT_PUBLIC_API_URL`:
- **Local Development:** `http://localhost:8000` (browser directly reaches backend port 8000).
- **Production Domain:** `https://api.triage.districthospital.gov.in`

---

## 8. Production Docker Compose Deployment (Server / Cloud)

*Note: For local Windows development, use native PowerShell orchestration: `.\scripts\clinova.ps1 start` (see [docs/NATIVE_WINDOWS_MIGRATION.md](docs/NATIVE_WINDOWS_MIGRATION.md)). Docker Compose is used for staging and production server environments using `infrastructure/docker/docker-compose.prod.yml`.*

### 8.1 Initialize Configuration
From the project root:
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Modify .env with your production secrets
# (Set SECRET_KEY, CORS_ORIGINS, NEXT_PUBLIC_API_URL)
```

### 8.2 Build and Launch Production Containers
```bash
# Launch production stack using production compose file
docker compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
```

### 8.3 Verify Container Status
```bash
docker compose ps
```
Expected output:
```text
NAME                IMAGE               STATUS              PORTS
clinova-backend     clinova-backend     Up (healthy)        0.0.0.0:8000->8000/tcp
clinova-db          postgres:16-alpine  Up                  0.0.0.0:5432->5432/tcp
clinova-frontend    clinova-frontend    Up                  0.0.0.0:3000->3000/tcp
clinova-redis       redis:7-alpine      Up                  0.0.0.0:6379->6379/tcp
```

### 8.4 Inspect Container Logs
```bash
# Follow backend logs
docker compose logs -f backend

# Follow frontend logs
docker compose logs -f frontend

# Follow database logs
docker compose logs -f db
```

### 8.5 Stop or Restart Services
```bash
# Graceful stop
docker compose down

# Stop and wipe database data (clean slate reset)
docker compose down -v
```

---

## 9. Non-Docker / Bare-Metal Deployment Steps

For environments where container runtimes cannot be installed, follow these bare-metal setup instructions:

### Step 1: Install System Prerequisites
- Ubuntu/Debian:
  ```bash
  sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv python3-pip nodejs npm postgresql postgresql-contrib redis-server
  ```
- Windows: Ensure Python 3.12+, Node.js 20 LTS, PostgreSQL 16, and Redis are installed.

### Step 2: Database & Cache Initialization
Start and enable PostgreSQL and Redis services:
```bash
# Linux systemd
sudo systemctl enable --now postgresql
sudo systemctl enable --now redis-server
```

### Step 3: Backend Setup
```bash
cd backend
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate    # Linux/macOS
# .\.venv\Scripts\Activate.ps1 # Windows PowerShell

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run build
npm start -- -p 3000
```

### Step 5: Process Management with PM2 (Optional)
To keep processes alive across reboots:
```bash
sudo npm install -g pm2

# Start Backend via PM2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name clinova-backend

# Start Frontend via PM2
pm2 start "npm start -- -p 3000" --name clinova-frontend --cwd ./frontend

# Save process list
pm2 save
pm2 startup
```

---

## 10. Deployment Order & Dependency Graph

To prevent connection race conditions, services must start in the following strict order:

```text
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: INFRASTRUCTURE CORE                            │
│ - PostgreSQL 16 (Port 5432)                             │
│ - Redis 7 (Port 6379)                                   │
│ [Verification: 'pg_isready' & 'redis-cli ping']         │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 2: FASTAPI BACKEND SERVICE                        │
│ - DB connection pool established                        │
│ - Lifespan executes: 'Base.metadata.create_all'         │
│ - Initial demo seeds provisioned                        │
│ [Verification: GET http://localhost:8000/api/v1/health] │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 3: NEXT.JS FRONTEND APPLICATION                   │
│ - Assets loaded, routes pre-rendered                    │
│ - Communicates with backend via NEXT_PUBLIC_API_URL     │
│ [Verification: GET http://localhost:3000]               │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 4: REVERSE PROXY & TLS TERMINATION                │
│ - Nginx / Caddy binds port 80/443                       │
│ - SSL/TLS certificates active                           │
│ [Verification: End-to-end browser walkthrough]          │
└─────────────────────────────────────────────────────────┘
```

---

## 11. Production Verification & Smoke Testing

After launching the services, execute these 5 smoke tests before releasing the platform to clinical users:

### Smoke Test 1: Service Health Probe
```bash
curl -s http://localhost:8000/api/v1/health | grep '"status":"healthy"'
```
*Pass Criteria:* Returns `{"status":"healthy", ...}` with HTTP status `200`.

### Smoke Test 2: Database Schema & Seed Verification
```bash
curl -s http://localhost:8000/api/v1/cases/ | grep 'CLV-DEMO-001'
```
*Pass Criteria:* Returns array of seeded demo cases.

### Smoke Test 3: Run Automated Test Suite
```bash
# In Docker
docker compose exec backend pytest -v

# Bare-metal
cd backend && pytest -v
```
*Pass Criteria:* All 15 tests pass with 0 failures.

### Smoke Test 4: Frontend UI Availability
```bash
curl -I http://localhost:3000
```
*Pass Criteria:* Returns HTTP `200 OK`.

### Smoke Test 5: Clinical Safety Banner Verification
Open `http://localhost:3000` in a web browser:
1. Verify the persistent amber **Non-Diagnostic Safety Disclaimer** is clearly visible at the top of the screen.
2. Navigate to `/intake` and verify demo consent checkbox is present.
3. Navigate to `/review` and verify deterministic rule flags (`TRIAGE-R01` to `R06`) render accurately.

---

## 12. Troubleshooting & Diagnostics

### Problem 1: Backend Fails with Database Connection Timeout
- **Symptom:** `asyncpg.exceptions.CannotConnectNowError` or `ConnectionRefusedError: [Errno 111]`.
- **Cause:** PostgreSQL container has not completed initialization when backend starts.
- **Resolution:** Check `docker compose logs db`. Ensure PostgreSQL port `5432` is listening. If running non-Docker, verify PostgreSQL service is active via `sudo systemctl status postgresql`.

### Problem 2: CORS Header Blocking in Browser
- **Symptom:** Browser console displays `Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource`.
- **Cause:** Request origin is not listed in `CORS_ORIGINS`.
- **Resolution:** In `.env`, add the exact protocol and hostname to `CORS_ORIGINS`:
  ```bash
  CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com"
  ```
  Restart backend container.

### Problem 3: Port Collision (Port 8000 or 3000 Already in Use)
- **Symptom:** `bind: address already in use` or `Error: listen EADDRINUSE: address already in use :::3000`.
- **Resolution:**
  - On Windows: Run `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force`.
  - On Linux: Run `sudo fuser -k 8000/tcp`.

### Problem 4: Redis Connection Failure
- **Symptom:** `ConnectionError: Error 111 connecting to localhost:6379. Connection refused.`
- **Resolution:** Check if Redis is running via `docker compose ps clinova-redis` or `redis-cli ping`. If using Docker, ensure `REDIS_URL` in the container points to `redis://redis:6379/0` rather than `localhost`.

---

## 13. Security & Healthcare Data Considerations

### 13.1 DISHA & ABDM Alignment
CLINOVA AI is designed to align with the Digital Information Security in Healthcare Act (DISHA) and Ayushman Bharat Digital Mission (ABDM) standards:
- **Zero Raw PHI Exposure:** The in-flight anonymizer (`backend/app/services/anonymizer.py`) scrubs 10-digit mobile numbers, emails, and 12-digit Indian Aadhaar sequences prior to storage.
- **Synthetic Identifiers:** Patients are assigned synthetic codes (`CLV-DEMO-xxx`) for triage slips.

### 13.2 TLS / HTTPS Enforcement
In production, CLINOVA AI must sit behind a reverse proxy (e.g., Nginx, Caddy, or AWS ALB) with SSL/TLS termination:
- Enforce TLS 1.3.
- Enforce HTTP Strict Transport Security (HSTS).
- Configure proxy headers (`X-Forwarded-For`, `X-Forwarded-Proto`).

### 13.3 Medicolegal Audit Logging
All clinical record access, intake creations, reviewer approvals, overrides, and data deletions are recorded in the immutable `audit_logs` table (`backend/app/services/audit.py`) with IP address, user email, action code, and UTC timestamp.

### 13.4 Short-Term Retention Buffers
Temporary audio recordings and raw lab report scans are buffered under a 24-hour default retention policy (`RETENTION_HOURS = 24`). Attending medical officers can trigger immediate data purging using the **Delete Case Data** button in the review interface (`DELETE /api/v1/cases/{case_id}`).

---

## 14. Backup, Rollback & Disaster Recovery

### 14.1 Database Backup Strategy
Schedule daily automated backups using `pg_dump`:

```bash
# Automated backup script (Linux/macOS)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
docker compose exec -T db pg_dump -U postgres clinova > /var/backups/clinova_${TIMESTAMP}.sql
```

### 14.2 Database Restoration
To restore from a backup:
```bash
# Stop backend to prevent concurrent writes
docker compose stop backend

# Restore database
cat /var/backups/clinova_backup.sql | docker compose exec -T db psql -U postgres -d clinova

# Restart backend
docker compose -f infrastructure/docker/docker-compose.prod.yml start backend
```

### 14.3 Container Image Rollback
If a newly deployed image introduces an issue:
```bash
# Rollback to previous git release tag
git checkout v0.1.0

# Re-build and start previous stable containers
docker compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
```

---

## 15. Post-Deployment Monitoring & Telemetry

### 15.1 Real-Time Health & Uptime Probes
Configure your hospital infrastructure monitoring tool (e.g., Prometheus, Uptime Kuma, Zabbix) to poll the following probe every 60 seconds:
- **Target URL:** `http://<server-ip>:8000/api/v1/health`
- **Expected HTTP Code:** `200`
- **Expected Payload:** Contains `"status":"healthy"`

### 15.2 Log Streaming
Monitor live container logs for unhandled errors:
```bash
# Stream error-level logs from all containers
docker compose logs -f --tail=100 | grep -i "error\|exception"
```

### 15.3 Clinical Queue & Audit Inspection
Review recent compliance events via the API:
```bash
curl -H "Authorization: Bearer <ADMIN_TOKEN>" http://localhost:8000/api/v1/audit-logs?limit=10
```

---

## 16. Comprehensive Deployment Checklist

### Pre-Deployment Phase
- [ ] Hardware and memory verified against minimum requirements (4 GB+ RAM).
- [ ] Ports `8000`, `3000`, `5432`, `6379` available and unblocked by firewall.
- [ ] `.env` created from `.env.example` with a unique, cryptographically random `SECRET_KEY`.
- [ ] `CORS_ORIGINS` configured to match the production domain.
- [ ] `NEXT_PUBLIC_API_URL` set to the accessible backend URL.
- [ ] Database credentials configured and secured.

### Deployment Phase
- [ ] Backing services (PostgreSQL 16 and Redis 7) launched and healthy.
- [ ] FastAPI backend launched; tables auto-initialized and seeded via `lifespan`.
- [ ] Next.js frontend built and launched on port `3000`.
- [ ] Reverse proxy (Nginx/Caddy) configured with valid SSL/TLS certificates.

### Post-Deployment Verification Phase
- [ ] `/api/v1/health` returns `200 OK` and `"status":"healthy"`.
- [ ] Automated test suite (`pytest -v`) passes with 15 successful tests.
- [ ] Web browser successfully loads `http://localhost:3000`.
- [ ] Persistent amber Non-Diagnostic Disclaimer verified on all screens.
- [ ] Multimodal intake flow tested (symptom submission $\rightarrow$ queue appearance).
- [ ] Human review gate tested (`approve`, `edit`, or `escalate` action).
- [ ] Daily database backup cron job verified.
