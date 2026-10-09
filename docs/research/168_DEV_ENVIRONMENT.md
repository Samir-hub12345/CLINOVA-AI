# CLINOVA AI — Development Environment (`DEV`) Specification

> **Document ID:** `RES-168`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Developer Experience, Systems Engineering & QA Group  

---

## 1. Environment Identity & Purpose

The **Development (`DEV`)** environment provides an agile, low-overhead local workstation runtime for engineers contributing to CLINOVA AI. It emphasizes fast hot-reloading, clear debug diagnostics, zero external cloud dependencies, and strict data isolation.

```
APP_ENV=dev
CLINOVA_ENVIRONMENT_ID=ENV_PHC  # Configurable to test any of the 6 facility profiles
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `DEV` |
| :--- | :--- |
| **Database** | Local SQLite 3.45+ (`clinova-dev.db`) via `aiosqlite`. WAL mode enabled. Foreign keys enforced via `PRAGMA foreign_keys = ON;`. |
| **Media Storage** | Local filesystem (`./data/storage/`). Local disk directories auto-created on startup. |
| **AI Runtime** | Pluggable: `local_rules` (deterministic rule mock) or local loopback SLM (`http://localhost:11434` / `vLLM`). |
| **Speech Runtime** | `faster-whisper` running locally on CPU (`base-int8` model) or deterministic mock transcripts. |
| **OCR Runtime** | `PaddleOCR` (v4 English/Hindi/Odia CPU) or deterministic mock bbox generator. |
| **Network Expectations**| Standalone localhost (`127.0.0.1`). Zero internet connectivity required. |
| **Offline Behavior** | 100% offline autonomous. Network failure probes are disabled or mocked. |
| **Sync Behavior** | `OFFLINE_ONLY`. Background sync daemons are disabled. Sync journals logged locally. |
| **Logging & Tracing** | `LOG_LEVEL=DEBUG`. Structured colored console logs. SQL statement query logging enabled. |
| **Data Safety Mode** | `CLINOVA_DATA_MODE=synthetic` (MANDATORY). Real patient data is strictly blocked. |
| **Security Mode** | Development JWT secrets (min 32 chars). Permissive CORS for `http://localhost:3000`. |
| **Frontend Styling** | Plain CSS Modules + CSS Custom Properties (`globals.css`). Hot-reloading active. |

---

## 3. Canonical `.env` Profile for `DEV`

```ini
# ==============================================================================
# CLINOVA AI - Development Configuration (.env)
# ==============================================================================

# Identity & Deployment
APP_ENV=dev
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI (Dev)"
APP_VERSION=2.0.0
DEBUG=True
API_V1_STR=/api/v1

# Networking & Hosts
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
API_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Frontend Inlined Variables
NEXT_PUBLIC_APP_ENV=dev
NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID=ENV_PHC
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="CLINOVA AI"
NEXT_PUBLIC_VERSION="2.0.0"
NEXT_PUBLIC_DATA_MODE=synthetic
NEXT_PUBLIC_OFFLINE_MODE=true

# Security & Secrets
SECRET_KEY=clinova-native-dev-secret-key-32chars-minimum-2026!
ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_ALGORITHM=HS256

# Persistence
DATABASE_URL=sqlite+aiosqlite:///./clinova-dev.db
LOCAL_DATABASE_PATH=./clinova-dev.db
DB_BUSY_TIMEOUT_MS=5000

# Storage
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=./data/storage
STORAGE_TEMP_PATH=./data/storage/tmp
MAX_UPLOAD_SIZE_BYTES=15728640
MEDIA_RETENTION_POLICY_DAYS=30

# Compliance & Clinical Safety
CLINOVA_DATA_MODE=synthetic
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Operations & Intelligence Providers
OFFLINE_MODE=True
SYNC_MODE=OFFLINE_ONLY
AI_PROVIDER=local_rules
AI_MODEL=qwen2.5-3b-instruct-q4
WHISPER_MODEL=base-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Observability
LOG_LEVEL=DEBUG
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

## 4. Invariants Enforced in `DEV`
1. **Inv-DEV-1 (Zero Cloud Dependency):** The system must cleanly start and pass all health checks with physical network adapters disabled.
2. **Inv-DEV-2 (Zero PHI Ingestion):** Any payload containing recognizable live Aadhaar or ABHA credentials without synthetic markers triggers validation warnings.
3. **Inv-DEV-3 (Non-Destructive Storage):** Storage directories (`./data/storage`) are created within the workspace, ignoring root OS paths.
