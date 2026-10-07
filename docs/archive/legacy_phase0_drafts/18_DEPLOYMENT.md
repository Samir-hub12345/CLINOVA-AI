# CLINOVA AI — Deployment & Infrastructure Specification

> **Document ID:** `DOC-18`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Deployment Topology

CLINOVA AI is architected for dual-target deployment:
1. **Local Edge / Air-Gapped Clinic Deployment:** A single-machine or local LAN appliance running Docker Compose with SQLite/aiosqlite and deterministic rule engines.
2. **Cloud / Institutional Hospital Network:** Multi-container deployment on Kubernetes or container engines with managed PostgreSQL, Redis caching, and TLS termination.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PRODUCTION DEPLOYMENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  [ Internet / Hospital Intranet Clients ]                   │
│                                     │                                       │
│                                     ▼ (Port 443 / HTTPS)                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    REVERSE PROXY (Nginx / Caddy)                    │   │
│   │  - TLS 1.3 Termination & Automated Let's Encrypt / Hospital Certs   │   │
│   │  - Security Headers & Compression (Gzip / Brotli)                   │   │
│   │  - Rate Limiting: 100 req/min per IP                                │   │
│   └──────────────────┬───────────────────────────────┬──────────────────┘   │
│                      │                               │                      │
│       Path: /api/*   │                               │ Path: /*             │
│                      ▼                               ▼                      │
│   ┌─────────────────────────────┐     ┌─────────────────────────────┐       │
│   │     BACKEND CONTAINER       │     │     FRONTEND CONTAINER      │       │
│   │  - FastAPI (Python 3.11)    │     │  - Next.js 15 (Node.js 20)  │       │
│   │  - Uvicorn ASGI Server      │     │  - Production Standalone    │       │
│   │  - Port 8000 (Internal)     │     │  - Port 3000 (Internal)     │       │
│   └──────────────┬──────────────┘     └─────────────────────────────┘       │
│                  │                                                          │
│                  ▼                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                  PERSISTENT STORAGE VOLUMES                     │       │
│   │  - Primary DB: PostgreSQL 16 (or local SQLite volume)           │       │
│   │  - Object Vault: Encrypted directory for PDF/audio records      │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Container Specifications

### 2.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 3. Production Environment Checklist

Before declaring production readiness, verify:
- [x] `SECRET_KEY` configured with random 64-character entropy.
- [x] `DEBUG=False` enforced in production configuration.
- [x] Mandatory clinical safety headers active on all routes.
- [x] Database migrations up to date (`alembic upgrade head`).
- [x] CORS origins restricted strictly to authorized client domains.
- [x] Container health check probe responds with HTTP 200 at `/health`.

---

## 4. Runbooks

### 4.1 Local Development Startup
```powershell
# Quickstart using root launchers
.\start-dev.ps1
# Or individual services:
# Terminal 1: Backend
cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000
# Terminal 2: Frontend
cd frontend && npm run dev
```

### 4.2 Production Docker Startup
```bash
docker compose up -d --build
docker compose ps
curl -i http://localhost:8000/health
```
