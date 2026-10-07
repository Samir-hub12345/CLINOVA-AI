# Clinova AI — Native Windows Migration Audit (Phase 0)

**Document Version:** 1.0  
**Target Environment:** Native Microsoft Windows 11 / Windows Server  
**Primary Orchestrator:** PowerShell (`scripts/clinova.ps1`)  
**Status:** Audit Completed / Ready for Migration  

---

## 1. Executive Summary & Migration Inventory

Clinova AI is transitioning its local developer runtime environment from containerized Docker Compose orchestration to a high-performance native Windows development environment orchestrated by PowerShell.

This audit inventories all existing Docker assets, network topologies, services, ports, environment variables, persistence volumes, and health mechanisms prior to infrastructure migration.

---

## 2. Service Migration Matrix

| Service | Current Method | Current Command | Port | Data Persistence | Dependencies | Native Replacement | Migration Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | Docker Container (`postgres:16-alpine`) | `postgres` | `5432` | Volume `postgres_data:/var/lib/postgresql/data` | None | Native Windows PostgreSQL Service (`postgresql-x64-16`) or local SQLite async driver (`sqlite+aiosqlite:///./clinova-demo.db`) | **PLANNED** |
| **Redis** | Docker Container (`redis:7-alpine`) | `redis-server` | `6379` | Volume `redis_data:/data` | None | Native Windows Redis / Memurai Service or in-memory graceful fallback (`app.core.redis`) | **PLANNED** |
| **FastAPI Backend** | Docker Container (Python 3.12-slim) | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` | `8000` | Local bind mount `./backend:/app`, volume `storage_data` | PostgreSQL, Redis | Native Windows Python (`.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`) | **PLANNED** |
| **Next.js Frontend** | Docker Container (`node:20-alpine`) | `npm run dev` | `3000` (also `3001` in CORS) | Local bind mount `./frontend:/app` | FastAPI Backend | Native Windows Node.js (`npm run dev` in `frontend/`) | **PLANNED** |
| **AI / Speech / OCR** | Server-side Python modules (`google-genai`) | In-process execution | N/A | Local temp directories | FastAPI Backend, Google Gemini API | Server-side native Python integration via `google-genai` SDK with offline heuristic fallbacks | **PLANNED** |
| **Background Tasks** | In-process `TaskManager` (FastAPI background) | In-process async tasks | N/A | DB table `background_jobs` | PostgreSQL | Native in-process execution via FastAPI asyncio background tasks (No Celery/RQ required) | **VERIFIED** |

---

## 3. Docker File Inventory & Classification

| File Path | Original Purpose | Classification | Action in Migration |
| :--- | :--- | :--- | :--- |
| `docker-compose.yml` | Local developer multi-container stack | **STALE LOCAL DEV** | Decommission & remove after native verification |
| `backend/Dockerfile` | Container build image for FastAPI | **STALE LOCAL DEV** | Decommission & remove after native verification |
| `frontend/Dockerfile` | Container build image for Next.js | **STALE LOCAL DEV** | Decommission & remove after native verification |
| `infrastructure/docker/docker-compose.prod.yml` | Production server deployment container stack | **DEPLOYMENT ONLY** | **PRESERVED** (documented for production cloud deployment) |
| `infrastructure/nginx/nginx.conf` | Reverse proxy configuration for production | **DEPLOYMENT ONLY** | **PRESERVED** |
| `start-dev.ps1` | Historical helper invoking `docker compose up` | **OBSOLETE HELPER** | Update to delegate to `scripts/clinova.ps1 start` |
| `start-dev.bat` | Historical helper invoking `docker compose up` | **OBSOLETE HELPER** | Update to delegate to `scripts/clinova.ps1 start` |

---

## 4. Port Configuration

| Port | Service | Host Binding | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `8000` | FastAPI Backend | `127.0.0.1` | HTTP / REST | API endpoints, OpenAPI Swagger (`/docs`), health checks |
| `3000` | Next.js Frontend | `localhost` | HTTP / HTML | Clinova clinical workstation UI, patient triage portal |
| `5432` | PostgreSQL | `127.0.0.1` | TCP / Postgres wire | Relational database (patients, users, cases, audit logs) |
| `6379` | Redis | `127.0.0.1` | TCP / RESP | Cache, session storage, rate limiting (with graceful local fallback) |

---

## 5. Environment Variable Audit

### Application & Environment Settings
- `APP_NAME`: `Clinova AI`
- `ENVIRONMENT`: `development` (options: `development`, `testing`, `staging`, `production`)
- `DEBUG`: `True`
- `API_V1_STR`: `/api/v1`
- `SECRET_KEY`: Cryptographic signing key for JWT tokens.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`

### Database & Cache
- `DATABASE_URL`:
  - Native PostgreSQL: `postgresql+asyncpg://postgres:postgres@localhost:5432/clinova`
  - Zero-Config Native SQLite: `sqlite+aiosqlite:///./clinova-demo.db`
- `REDIS_URL`: `redis://localhost:6379/0`

### Object Storage & Document Ingestion
- `STORAGE_PROVIDER`: `local_object_store`
- `STORAGE_LOCAL_DIR`: `storage_data`
- `STORAGE_BUCKET`: `medical-documents`
- `MAX_FILE_SIZE_BYTES`: `524288000` (500 MB)
- `PRESIGNED_URL_TTL_SECONDS`: `900`
- `SCAN_ENABLED`: `True`

### CORS Security
- `CORS_ORIGINS`: `["http://localhost:3000","http://127.0.0.1:3000","http://localhost:3001","http://127.0.0.1:3001"]`

### AI & Clinical Model Settings
- `DEMO_MODE`: `True`
- `OFFLINE_DEMO`: `False` (set to `True` for zero-API offline demo)
- `GEMINI_API_KEY`: Server-side API key for Google Gemini (`gemini-2.5-flash`). Kept strictly server-side.
- `LLM_PROVIDER`: `mock` or `gemini`
- `STT_PROVIDER`: `local` (options: `local`, `faster-whisper`, `mock`)
- `OCR_PROVIDER`: `local` (options: `local`, `paddleocr`, `mock`)
- `TRANSLATION_PROVIDER`: `local` (options: `local`, `indictrans2`, `mock`)

### Frontend Public Settings
- `NEXT_PUBLIC_API_URL`: `http://localhost:8000`
- `NEXT_PUBLIC_APP_NAME`: `Clinova AI`

---

## 6. Health & Diagnostic Endpoints

The native stack provides granular health monitoring:
- `GET /api/v1/health`: Basic operational metadata.
- `GET /api/v1/health/live`: Liveness probe for process uptime verification.
- `GET /api/v1/health/ready`: Deep readiness probe checking PostgreSQL and Redis latency.
- `GET /api/v1/ping`: Ultra-lightweight latency probe.
- `GET /api/v1/metrics`: Prometheus exposition metrics.

---

## 7. Migration Acceptance Criteria Checklist

- [x] All Docker files and compose configurations audited and classified.
- [x] All service commands, ports, and environment variables identified.
- [x] Database persistence and schema initialization verified (`create_all` + `upgrade_ownership` + `seed_initial_data`).
- [x] Redis usage inspected: graceful local fallback confirmed when Redis is not running.
- [x] Background tasks inspected: confirmed in-process FastAPI async tasks (no separate Celery daemon needed).
- [x] AI integration inspected: confirmed server-side Gemini 2.5 Flash with offline heuristic rule fallbacks.
- [x] Native Windows prerequisites verified: Git, Node.js (v24), npm (v11), Python (v3.14).
