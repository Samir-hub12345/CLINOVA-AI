# CLINOVA AI — Cloud Preview Environment (`CLOUD_PREVIEW`) Specification

> **Document ID:** `RES-172`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Cloud Infrastructure, Web Security & Public Demonstration Group  

---

## 1. Environment Identity & Purpose

The **Cloud Preview (`CLOUD_PREVIEW`)** environment specifies a globally accessible, cloud-hosted preview sandbox (e.g., deployed on Vercel frontend, containerized FastAPI backend on Render/Fly.io/GCP Cloud Run, and managed Supabase persistence).

It allows health ministry officials, academic evaluators, hackathon review panels, and international health informatics partners to evaluate CLINOVA AI live from any web browser without local installation.

```
APP_ENV=cloud_preview
CLINOVA_ENVIRONMENT_ID=ENV_PHC  # Demonstrates rural primary care intelligence on cloud
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `CLOUD_PREVIEW` |
| :--- | :--- |
| **Database** | Managed Cloud PostgreSQL 15+ / Supabase. Connected via `postgresql+asyncpg` using transaction pooler. |
| **Media Storage** | Supabase Storage (`STORAGE_MODE=SUPABASE_STORAGE`). Private encrypted bucket (`clinova-preview-media`). Access strictly via 15-minute signed URLs. |
| **AI Runtime** | Pluggable: Cloud-hosted open-source vLLM endpoint (e.g. Qwen2.5-3B on serverless GPU) or deterministic `local_rules` fallback. |
| **Speech Runtime** | Serverless CPU/GPU `faster-whisper` endpoint or pre-recorded multimodal demo audio assets. |
| **OCR Runtime** | Containerized `PaddleOCR` worker or pre-cached high-fidelity bounding box extractions. |
| **Network Expectations**| Public Internet over HTTPS (TLS 1.3). Edge CDN caching for Next.js static shell. |
| **Offline Behavior** | Client detects continuous WAN connection; offline cache indicators set to standby. |
| **Sync Behavior** | `CLOUD_NATIVE`. Frontends communicate directly with central cloud backend; zero edge sync journal required. |
| **Logging & Tracing** | `LOG_LEVEL=INFO`. Structured JSON streaming to cloud log aggregation (e.g. Datadog / GCP Cloud Logging). |
| **Data Safety Mode** | `CLINOVA_DATA_MODE=synthetic` (**MANDATORY & ENFORCED**). Ingestion of real clinical records is strictly prevented. |
| **Security Mode** | Strict separation of Supabase credentials: `SUPABASE_SERVICE_ROLE_KEY` resides strictly in backend container; only `NEXT_PUBLIC_SUPABASE_ANON_KEY` reaches browser. |
| **Frontend Styling** | Plain CSS Modules + CSS Custom Properties. Fast rendering across desktop, tablet, and mobile browsers. |

---

## 3. Canonical `.env` Profile for `CLOUD_PREVIEW`

```ini
# ==============================================================================
# CLINOVA AI - Cloud Preview Sandbox Configuration (.env.cloud)
# ==============================================================================

# Identity & Deployment
APP_ENV=cloud_preview
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI — Cloud Clinical Intelligence Preview"
APP_VERSION=2.0.0
DEBUG=False
API_V1_STR=/api/v1

# Networking & Ingress
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_BASE_URL=https://api.preview.clinova.health/api/v1
FRONTEND_BASE_URL=https://preview.clinova.health
CORS_ORIGINS=["https://preview.clinova.health"]

# Frontend Inlined Variables (Injected during Vercel/Cloud build)
NEXT_PUBLIC_APP_ENV=cloud_preview
NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID=ENV_PHC
NEXT_PUBLIC_API_URL=https://api.preview.clinova.health/api/v1
NEXT_PUBLIC_APP_NAME="CLINOVA AI Preview"
NEXT_PUBLIC_VERSION="2.0.0"
NEXT_PUBLIC_DATA_MODE=synthetic
NEXT_PUBLIC_OFFLINE_MODE=false
NEXT_PUBLIC_SUPABASE_URL=https://xyzcompany.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.anon_public_key_preview...

# Backend Security & Cloud Secrets (SERVER-ONLY; NEVER EXPOSED TO CLIENT)
SECRET_KEY=cloud-preview-backend-master-jwt-signing-secret-key-64-bytes-entropy-minimum-99999999!
ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_ALGORITHM=HS256

# Supabase Admin Secret (SERVER-ONLY; NEVER in NEXT_PUBLIC_*)
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.anon_public_key_preview...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.service_role_admin_backend_only_key_99999...

# Persistence (Supabase PostgreSQL via Transaction Pooler)
DATABASE_URL=postgresql+asyncpg://postgres.xyzcompany:secure_preview_pass@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Storage (Supabase Storage Cloud Bucket)
STORAGE_MODE=SUPABASE_STORAGE
STORAGE_PATH=./data/cloud_tmp
MAX_UPLOAD_SIZE_BYTES=15728640
MEDIA_RETENTION_POLICY_DAYS=14

# Compliance & Clinical Safety
CLINOVA_DATA_MODE=synthetic
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Intelligence & Perception
OFFLINE_MODE=False
SYNC_MODE=CLOUD_NATIVE
AI_PROVIDER=local_rules
AI_MODEL=qwen2.5-3b-instruct-q4
WHISPER_MODEL=base-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Observability
LOG_LEVEL=INFO
LOG_DESTINATION=CONSOLE_JSON

# Feature Flags
FEATURE_VOICE=True
FEATURE_OCR=True
FEATURE_TRANSLATION=True
FEATURE_CAREGRAPH=True
FEATURE_FACILITYGRAPH=True
FEATURE_SIGNALGRAPH=True
FEATURE_ORCHESTRATION=True
FEATURE_OFFLINE_SYNC=False
FEATURE_EMERGENCY_MODE=True
```

---

## 4. Invariants Enforced in `CLOUD_PREVIEW`
1. **Inv-CLOUD-1 (No Service Role in Client):** Webpack/Turbopack build scripts must fail compilation if `SUPABASE_SERVICE_ROLE_KEY` is referenced in any file inside `frontend/src/`.
2. **Inv-CLOUD-2 (Strict Synthetic Banner):** The top-level clinical banner explicitly alerts users: *"Cloud Preview Sandbox — Synthetic Medical Data Only. Do Not Enter Real Patient Information."*
3. **Inv-CLOUD-3 (Ephemeral Signed URLs):** Media files stored in Supabase Storage are private; the frontend only receives presigned URLs with maximum 15-minute time-to-live (TTL).
