# CLINOVA AI — Local Demo Environment (`LOCAL_DEMO`) Specification

> **Document ID:** `RES-169`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Product, Demonstration Engineering & Operations Group  

---

## 1. Environment Identity & Purpose

The **Local Demo (`LOCAL_DEMO`)** environment provides a turnkey, bulletproof, zero-latency showcase runtime designed for single-laptop presentations before hospital administrators, clinical evaluation committees, BPUT evaluators, and rural health officials.

It guarantees **100% deterministic reproducibility**, works flawlessly in conference halls with zero Wi-Fi, requires ₹0 in external API subscriptions, and pre-seeds rich synthetic multi-modal patient episodes.

```
APP_ENV=local_demo
CLINOVA_ENVIRONMENT_ID=ENV_PHC  # Demonstrates rural offline care intelligence
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `LOCAL_DEMO` |
| :--- | :--- |
| **Database** | Pre-seeded SQLite 3.45+ (`clinova-demo.db`). Bundles approved synthetic Master Cases (STEMI, Pediatric Shock, COPD, Maternal Sepsis). |
| **Media Storage** | Local filesystem (`./data/demo_storage/`). Bundles synthetic slip photos (JPG/PNG) and synthetic audio recordings (WAV). |
| **AI Runtime** | `local_rules` (Deterministic rule engines guarantee instant $< 5\text{ms}$ responses with zero GPU requirements). |
| **Speech Runtime** | Local `faster-whisper` (`base-int8` on CPU) with deterministic fallback transcripts for pre-loaded audio clips. |
| **OCR Runtime** | Local `PaddleOCR` (v4 on CPU) with pre-cached bounding boxes $[0, 1000]^2$ for flawless side-by-side presentation. |
| **Network Expectations**| Standalone laptop (`localhost` or optional local Wi-Fi hotspot for tablet companion). Zero internet required. |
| **Offline Behavior** | 100% autonomous offline mode. Prominent green "OFFLINE READY" badge displayed. |
| **Sync Behavior** | `OFFLINE_ONLY`. Displays pending sync journal count in developer drawer without transmitting external packets. |
| **Logging & Tracing** | `LOG_LEVEL=INFO`. High-signal clinical event logging; debug stack traces silenced. |
| **Data Safety Mode** | `CLINOVA_DATA_MODE=synthetic` (LOCKED). Prominent demo banner displayed across all screens. |
| **Security Mode** | Pre-configured demonstration roles (`Dr. Priya Sharma (RMP)`, `Staff Nurse Sunita`, `ASHA Anjali`). Instant one-click login. |
| **Frontend Styling** | Plain CSS Modules + CSS Custom Properties. Polished high-contrast clinical UI tokens. |

---

## 3. Canonical `.env` Profile for `LOCAL_DEMO`

```ini
# ==============================================================================
# CLINOVA AI - Local Demo Configuration (.env.demo)
# ==============================================================================

# Identity & Deployment
APP_ENV=local_demo
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI — Clinical Intelligence Workstation"
APP_VERSION=2.0.0
DEBUG=False
API_V1_STR=/api/v1

# Networking & Hosts
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://192.168.1.*"]

# Frontend Inlined Variables
NEXT_PUBLIC_APP_ENV=local_demo
NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID=ENV_PHC
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="CLINOVA AI"
NEXT_PUBLIC_VERSION="2.0.0"
NEXT_PUBLIC_DATA_MODE=synthetic
NEXT_PUBLIC_OFFLINE_MODE=true

# Security & Secrets
SECRET_KEY=clinova-offline-demo-secret-key-salt-9876543210-fixed!
ACCESS_TOKEN_EXPIRE_MINUTES=480
JWT_ALGORITHM=HS256

# Persistence
DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db
LOCAL_DATABASE_PATH=./clinova-demo.db
DB_BUSY_TIMEOUT_MS=10000

# Storage
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=./data/demo_storage
STORAGE_TEMP_PATH=./data/demo_storage/tmp
MAX_UPLOAD_SIZE_BYTES=15728640
MEDIA_RETENTION_POLICY_DAYS=90

# Compliance & Clinical Safety
CLINOVA_DATA_MODE=synthetic
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Intelligence & Perception
OFFLINE_MODE=True
SYNC_MODE=OFFLINE_ONLY
AI_PROVIDER=local_rules
AI_MODEL=qwen2.5-3b-instruct-q4
WHISPER_MODEL=base-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Observability
LOG_LEVEL=INFO
LOG_DESTINATION=CONSOLE_JSON

# Feature Flags (All Innovations Showcased)
FEATURE_VOICE=True
FEATURE_OCR=True
FEATURE_TRANSLATION=True
FEATURE_CAREGRAPH=True
FEATURE_FACILITYGRAPH=True
FEATURE_SIGNALGRAPH=True
FEATURE_ORCHESTRATION=True
FEATURE_OFFLINE_SYNC=True
FEATURE_EMERGENCY_MODE=True
```

---

## 4. Invariants Enforced in `LOCAL_DEMO`
1. **Inv-DEMO-1 (Zero Network Dependency):** Must execute smoothly during airplane mode; all assets (fonts, icons, styles, datasets) served locally.
2. **Inv-DEMO-2 (Strict Synthetic Enforcement):** Database is re-initialized to verified synthetic records with one command (`npm run demo:reset`).
3. **Inv-DEMO-3 (Rapid Role Switching):** Login portal provides pre-authenticated 1-click clinical identity switcher for smooth presentation flow.
