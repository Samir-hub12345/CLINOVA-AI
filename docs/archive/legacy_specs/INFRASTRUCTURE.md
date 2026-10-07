# CLINOVA AI — Infrastructure & Systems Architecture

**Document Version:** 1.0.0  
**Target Environments:** Rural Primary Health Centers (PHCs), Community Health Centers (CHCs), Government District Hospital OPDs, Campus Clinics, and Cloud Staging  
**Current Release:** v0.2.0 (Integrated Staging)  

---

> [!WARNING]
> ### 🔒 Clinical Safety & Operational Mandate
> **Educational prototype and clinical decision support system only.** Infrastructure configurations must maintain the persistent amber non-diagnostic clinical disclaimer banner across all deployment tiers and ensure attending clinician sign-off gates are active before clinical use.

---

## Table of Contents

1. [Architectural Topology](#1-architectural-topology)
2. [Network & Port Allocation Reference](#2-network--port-allocation-reference)
3. [Container Orchestration (Docker Compose)](#3-container-orchestration-docker-compose)
4. [Bare-Metal & Process Supervision (PM2 / systemd)](#4-bare-metal--process-supervision-pm2--systemd)
5. [Reverse Proxy, Ingress & TLS Configuration](#5-reverse-proxy-ingress--tls-configuration)
6. [Environment Variables Reference](#6-environment-variables-reference)
7. [Tiered Hardware Sizing Profiles](#7-tiered-hardware-sizing-profiles)
8. [Storage Persistence & Data Lifecycle](#8-storage-persistence--data-lifecycle)
9. [Observability, Healthchecks & Telemetry](#9-observability-healthchecks--telemetry)
10. [Disaster Recovery & Backup Procedures](#10-disaster-recovery--backup-procedures)

---

## 1. Architectural Topology

CLINOVA AI is architected as an interconnected four-tier service stack optimized for high availability, low latency, and zero-cloud offline survivability:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT INGRESS                                 │
│          Web Browser (Desktop / Tablet / Low-Bandwidth Mobile Kiosk)        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / HTTPS (Port 80/443)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               REVERSE PROXY & TLS TERMINATION (Nginx / Caddy)               │
│                  - TLS 1.3 / HSTS / Static Asset Caching                     │
│                  - Request Rate Limiting / CORS Enforcement                 │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │ /                             │ /api/v1
                       ▼                               ▼
┌──────────────────────────────┐              ┌───────────────────────────────┐
│     FRONTEND APPLICATION     │              │      BACKEND REST SERVICE     │
│   Next.js 14 (Node.js 18+)   │              │   FastAPI (Python 3.12/3.14)  │
│   - SSR & React 18 UI        │              │   - Async Uvicorn ASGI Server │
│   - Tailwind CSS & Lucide    │              │   - Pydantic v2 Validation    │
│   - Port: 3000               │              │   - Risk Signal Engine (R01+) │
│   Container: clinova-frontend│              │   - Port: 8000                │
└──────────────────────────────┘              │   Container: clinova-backend  │
                                              └───────┬───────────────┬───────┘
                                                      │               │
                              SQLAlchemy 2.0 (asyncpg)│               │ aioredis
                                                      ▼               ▼
                                              ┌───────────────┐ ┌─────────────┐
                                              │  DATABASE     │ │ IN-MEMORY   │
                                              │  PostgreSQL 16│ │ CACHE       │
                                              │  Port: 5432   │ │ Redis 7     │
                                              │  Container:   │ │ Port: 6379  │
                                              │  clinova-db   │ │ Container:  │
                                              │  DB: clinova  │ │ clinova-    │
                                              │               │ │ redis       │
                                              └───────────────┘ └─────────────┘
```

---

## 2. Network & Port Allocation Reference

All services operate on standardized, isolated network ports to eliminate port collision across deployment environments:

| Service | Technology Stack | Host Port | Container Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Next.js 14 (Node.js) | `3000` | `3000` | HTTP / WS | Web client UI, SSR, intake wizard, review queue. |
| **Backend** | FastAPI / Uvicorn ASGI | `8000` | `8000` | HTTP | Core REST API, risk engine, OCR & STT adapters. |
| **Database** | PostgreSQL 16 (Alpine) | `5432` | `5432` | TCP (Postgres) | Relational EHR, triage cases, audit log trail. |
| **Cache / Queue** | Redis 7 (Alpine) | `6379` | `6379` | TCP (RESP) | Fast cache buffer, session keys, rate limiting. |

---

## 3. Container Orchestration (Production Server Deployment)

*Note: For local Windows development, Clinova AI runs natively via PowerShell: `.\scripts\clinova.ps1 start` (see [docs/NATIVE_WINDOWS_MIGRATION.md](docs/NATIVE_WINDOWS_MIGRATION.md)). The containerized multi-service topology below applies to production server deployments using `infrastructure/docker/docker-compose.prod.yml`:*

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: clinova-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: clinova-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: clinova-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=clinova
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: clinova-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3.1 Common Management Commands
```bash
# Build and start all services in detached mode
docker compose up -d --build

# View real-time aggregated logs
docker compose logs -f

# Check container health status
docker compose ps

# Graceful stop
docker compose stop

# Teardown containers and internal networks (preserving volumes)
docker compose down
```

---

## 4. Bare-Metal & Process Supervision (PM2 / systemd)

For institutional deployments running without container virtualization on dedicated Linux servers (Ubuntu 22.04/24.04 LTS):

### 4.1 Process Management with PM2
```bash
# Install PM2 globally
sudo npm install -g pm2

# Start Backend via PM2
cd /opt/clinova/CLINOVA-AI
pm2 start "venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" \
  --name clinova-backend \
  --cwd ./backend

# Start Frontend via PM2
pm2 start "npm start -- -p 3000" \
  --name clinova-frontend \
  --cwd ./frontend

# Freeze process list & configure reboot startup
pm2 save
sudo pm2 startup systemd
```

### 4.2 Systemd Unit File (`/etc/systemd/system/clinova-backend.service`)
```ini
[Unit]
Description=CLINOVA AI FastAPI Backend Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=clinova
WorkingDirectory=/opt/clinova/CLINOVA-AI/backend
ExecStart=/opt/clinova/CLINOVA-AI/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5s
EnvironmentFile=/opt/clinova/CLINOVA-AI/.env

[Install]
WantedBy=multi-user.target
```

---

## 5. Reverse Proxy, Ingress & TLS Configuration

In production, neither FastAPI nor Next.js should be directly exposed to the public internet. All ingress must pass through a hardened reverse proxy:

### 5.1 Nginx Reference Configuration (`/etc/nginx/sites-available/clinova.conf`)
```nginx
server {
    listen 80;
    server_name triage.hospital.gov.in;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name triage.hospital.gov.in;

    ssl_certificate /etc/ssl/certs/clinova.crt;
    ssl_certificate_key /etc/ssl/private/clinova.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend Route
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API Route
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 6. Environment Variables Reference

Verified against `backend/app/core/config.py` and `.env.example`:

| Environment Variable | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `BACKEND_PORT` | No | `8000` | Port for FastAPI Uvicorn listener. |
| `FRONTEND_PORT` | No | `3000` | Port for Next.js Node server. |
| `ENVIRONMENT` | Yes | `production` | Runtime mode (`development`, `staging`, `production`). |
| `DEBUG` | No | `false` | When `false`, suppresses SQL query logs and debug traces. |
| `SECRET_KEY` | **Yes** | *[Cryptographic Key]* | Secret key used for signing HS256 JWT access tokens. |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://postgres:postgres@localhost:5432/clinova` | Asynchronous SQLAlchemy database connection string. |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Connection URI for Redis cache instance. |
| `CORS_ORIGINS` | **Yes** | `["http://localhost:3000"]` | Allowed origins for browser fetch requests. |
| `GEMINI_API_KEY` | No | `""` (Empty) | Optional Google Gemini key. Defaults to deterministic mocks if empty. |
| `DEMO_MODE` | No | `true` | When `true`, activates public health demo scenarios and local mocks. |
| `LLM_PROVIDER` | No | `mock` (or `gemini`) | Provider adapter for narrative SOAP summary generation. |
| `STT_PROVIDER` | No | `local` | Speech-to-text adapter (`local`, `faster-whisper`, `mock`). |
| `OCR_PROVIDER` | No | `local` | Document OCR parsing adapter (`local`, `paddleocr`, `mock`). |
| `TRANSLATION_PROVIDER`| No | `local` | Regional translation adapter (`local`, `indictrans2`, `mock`). |
| `DEFAULT_FACILITY` | No | `Government District Hospital` | Default facility name attached to intake cases. |
| `RETENTION_HOURS` | No | `24` | Hours before temporary media and unlinked blobs expire. |
| `NEXT_PUBLIC_API_URL`| **Yes** | `http://localhost:8000` | Browser-accessible base URL of the backend API. |

---

## 7. Tiered Hardware Sizing Profiles

CLINOVA AI is designed to run across three distinct deployment tiers:

### Tier 1: Rural PHC / Outreach Laptop (Edge Mode)
- **Target Context**: Sub-centers, mobile outreach camps, intermittent power.
- **Hardware**: Single laptop or mini-PC (Intel Core i3/i5 or AMD Ryzen 3, 4–8 GB RAM, 64 GB SSD).
- **Runtime Configuration**: Standalone Docker Compose stack with `DEMO_MODE=True`, lightweight local mocks for STT/OCR, low-bandwidth mode enabled on client browser.
- **Concurrent Users**: 1–5 intake kiosks or tablets.

### Tier 2: Community Health Center (CHC) / Campus Clinic (Standard Mode)
- **Target Context**: Institutional clinic with dedicated local area network (LAN).
- **Hardware**: On-premise departmental server (4–8 vCPUs, 16 GB RAM, 256 GB NVMe SSD).
- **Runtime Configuration**: Docker Compose stack with `faster-whisper` and local OCR service workers.
- **Concurrent Users**: 10–25 intake tablets and clinician review terminals.

### Tier 3: District Hospital OPD / High-Volume Urban Center (Enterprise Mode)
- **Target Context**: Tertiary referral hospital OPD handling 1,000+ daily walk-ins.
- **Hardware**: Dedicated VM or physical cluster (16+ vCPUs, 32+ GB RAM, redundant 1 TB NVMe RAID-10).
- **Runtime Configuration**: Multi-worker Uvicorn ASGI cluster behind Nginx load balancer; managed PostgreSQL cluster with automated WAL archiving and read-replicas.
- **Concurrent Users**: 50+ concurrent medical officers and intake triage desks.

---

## 8. Storage Persistence & Data Lifecycle

### 8.1 PostgreSQL Volume (`postgres_data`)
- Houses permanent EHR patient registry, consultation records, finalized triage cases, and the append-only `audit_logs` table.
- Default path inside container: `/var/lib/postgresql/data`.

### 8.2 Redis Volume (`redis_data`)
- Retains cache keys and temporary rate-limiting buckets across container restarts.
- Default path inside container: `/data`.

### 8.3 Transient Media Buffers
- Audio recordings and raw lab report image uploads are stored in temporary memory/disk buffers governed by `RETENTION_HOURS=24`.
- Clinicians can trigger immediate deletion via the **Delete Case Data** button in the case review view (`DELETE /api/v1/cases/{case_id}`).

---

## 9. Observability, Healthchecks & Telemetry

### 9.1 Service Health Endpoints
- **Liveness & Readiness**: `GET /api/v1/health`
  ```bash
  curl -s http://localhost:8000/api/v1/health | jq .
  ```
  Response:
  ```json
  {
    "status": "healthy",
    "version": "0.2.0",
    "database": "connected",
    "redis": "connected",
    "mode": "demo"
  }
  ```

- **Ultra-Lightweight Latency Ping**: `GET /api/v1/ping`
  ```bash
  curl -s http://localhost:8000/api/v1/ping | jq .
  ```
  Response:
  ```json
  {
    "status": "ok",
    "timestamp": 1742491200.123
  }
  ```
  > **Architectural Note:** The `/api/v1/ping` endpoint bypasses database queries and session caches to provide sub-millisecond ASGI response times specifically for accurate client-side round-trip time (RTT) calculation without adding backend load.

### 9.2 Network Telemetry & Adaptive Connectivity Architecture
- **Active Heartbeat Ping Frequency**:
  - `GOOD` / `NORMAL`: Sampled every 15 seconds.
  - `SLOW`: Backed off to every 45 seconds to preserve scarce bandwidth.
  - `OFFLINE`: Probed every 5 seconds for fast recovery detection.
- **Client Latency Smoothing**: Rolling median of the last 5 RTT measurements with 3-consecutive-sample debouncing to eliminate false-positive mode switching.
- **Zero-PHI Client Invariant**: No unencrypted patient intake or triage data is stored in browser persistent storage (`localStorage` / `IndexedDB`) during offline states.

### 9.3 Docker Log Inspection
```bash
# Follow backend API logs
docker compose logs -f backend

# Inspect database container queries & connections
docker compose logs -f db
```

---

## 10. Disaster Recovery & Backup Procedures

### 10.1 Daily Automated PostgreSQL Backup Script (`backup_db.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/var/backups/clinova"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/clinova_backup_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

docker compose exec -T db pg_dump -U postgres clinova | gzip > "$FILENAME"
chmod 600 "$FILENAME"

# Keep 30 days of retention
find "$BACKUP_DIR" -type f -name "clinova_backup_*.sql.gz" -mtime +30 -delete
```

### 10.2 Database Restoration
```bash
# Decompress and restore into running database container
gunzip < /var/backups/clinova/clinova_backup_20260918_120000.sql.gz | \
  docker compose exec -T db psql -U postgres -d clinova
```
