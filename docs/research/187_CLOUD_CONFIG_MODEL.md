# CLINOVA AI — Central Cloud Hub & Hybrid Synchronization Configuration Model

> **Document ID:** `RES-187`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Cloud Systems Architecture, Distributed Data & Platform Engineering Group  

---

## 1. Cloud Architecture & Hybrid Topology

CLINOVA AI supports a modern hybrid healthcare cloud topology where peripheral rural facilities (`PHC_EDGE`) operate autonomously while synchronizing structured clinical events and telemetry with a **Central Cloud Hub** (`CLOUD_PREVIEW` or State Health Data Centre).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CENTRAL CLOUD HUB ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CLIENT BROWSER LAYER (Vercel / Cloudflare Pages) ]                       │
│  ├── Next.js 15+ App Router                                                 │
│  └── Ingests strictly `NEXT_PUBLIC_*` configuration                         │
│          │                                                                  │
│          ▼ HTTPS / TLS 1.3 (Public Cloud Ingress)                           │
│  [ APPLICATION BACKEND LAYER (Containerized FastAPI on Cloud Run / Fly) ]   │
│  ├── Ingests SERVER_ONLY secrets (`SECRET_KEY`, `DATABASE_URL`)             │
│  └── Holds `SUPABASE_SERVICE_ROLE_KEY` securely in memory                   │
│          │                                                                  │
│          ▼ Encrypted Cloud VPC Connection                                   │
│  [ PERSISTENCE & STORAGE (Supabase Managed Cloud Infrastructure) ]           │
│  ├── Managed PostgreSQL 15+ (Row Level Security Active)                     │
│  ├── Supabase Storage (Private Encrypted Buckets)                           │
│  └── Edge Replication Gateway (Sync Journal Ingestion Desk)                 │
│          ▲                                                                  │
│          │ Periodic Encrypted Sync Batches (HMAC-SHA256 Authenticated)      │
│  [ REMOTE PHC EDGE MINI-PC NODES ]                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Shared vs. Environment-Specific Configuration Matrix

A key architectural rule is ensuring complete clarity on which configurations are **immutable system standards** versus which are **injected per environment**:

| Configuration Element | Nature | Where Defined | Rationale |
| :--- | :--- | :--- | :--- |
| **Clinical Safety Rules (NEWS2, Shock Index)** | **SHARED** | `backend/app/domain/safety.py` | Universal physiological formulas; cannot differ across environments. |
| **Pydantic / Zod Schemas** | **SHARED** | Shared TypeScript / Python packages | Type safety and API contracts must be 100% consistent. |
| **Clinical Design Tokens (CSS)** | **SHARED** | `frontend/src/app/globals.css` | Acuity colors and touch target standards are identical everywhere. |
| **API Route URLs (`/api/v1/*`)** | **SHARED** | FastAPI Router definitions | API contracts remain identical across edge and cloud. |
| **`DATABASE_URL`** | **ENVIRONMENT-SPECIFIC** | Injected via `.env` / Container Vault | SQLite path on edge vs. PostgreSQL connection string in cloud. |
| **`STORAGE_MODE`** | **ENVIRONMENT-SPECIFIC** | Injected via `.env` / Container Vault | `LOCAL_FS` on edge Mini-PCs vs. `SUPABASE_STORAGE` in cloud. |
| **`SECRET_KEY`** | **ENVIRONMENT-SPECIFIC** | Injected via Host Vault | Unique cryptographic signing key per deployment instance. |
| **`CORS_ORIGINS`** | **ENVIRONMENT-SPECIFIC** | Injected via Host Vault | Tailored to local clinic router IP or hospital domain. |

---

## 3. Supabase Cloud Service Configuration

When deployed in `CLOUD_PREVIEW` or central cloud environments:

### 3.1 Managed PostgreSQL & Connection Pooling
- **Connection URL:** Uses Supabase's transaction pooler (`aws-0-ap-south-1.pooler.supabase.com:6543`) to prevent connection starvation during concurrent load.
- **Row Level Security (RLS):** Default-deny RLS policies restrict cross-facility record queries.

### 3.2 Private Supabase Storage Bucket
- **Bucket Identification:** `clinova-media-private`.
- **Public Access:** Disabled (`public = false`).
- **Access Protocol:** Client receives signed URLs with 15-minute TTL generated exclusively by the backend service.

### 3.3 Credential Isolation Guardrail
- `SUPABASE_URL`: Publicly readable (`NEXT_PUBLIC_SUPABASE_URL`).
- `SUPABASE_ANON_KEY`: Publicly readable (`NEXT_PUBLIC_SUPABASE_ANON_KEY`), restricted to RLS policies.
- `SUPABASE_SERVICE_ROLE_KEY`: Strictly backend server memory; **never dispatched across HTTP or built into client JS bundles**.

---

## 4. Edge-to-Cloud Synchronization Configuration

When an edge node connects to the central cloud gateway:
- **Authentication:** Edge node authenticates using a pre-shared cryptographic key (`EDGE_SYNC_HMAC_SECRET`).
- **Batch Serialization:** Transmits append-only sync journals containing Merkle-chained event hashes and state differentials.
- **Privacy Enforcement:** Raw media is NOT replicated to cloud by default; only cryptographic hashes and normalized clinical concepts are synced, preserving rural patient data sovereignty.
