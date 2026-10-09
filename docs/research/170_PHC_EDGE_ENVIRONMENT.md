# CLINOVA AI — Primary Health Centre Edge (`PHC_EDGE`) Specification

> **Document ID:** `RES-170`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Rural Edge Systems, Embedded Hardware & Clinical Informatics Group  

---

## 1. Environment Identity & Purpose

The **Primary Health Centre Edge (`PHC_EDGE`)** environment defines the operational configuration for rural, sub-divisional, and remote health facilities across India (e.g., Koraput, Rayagada, Kalahandi).

Operating on a **₹12,000–₹16,000 fanless industrial Mini-PC** (Intel Celeron N5105 / 8GB RAM / 128GB SSD / 12V DC battery backup) acting as the Local Clinic Server, it serves 2–4 frontline staff tablets (Staff Nurse, Medical Officer, Registration Clerk) over an isolated local Wi-Fi router. It provides complete clinical autonomy during weeks of internet blackout.

```
APP_ENV=phc_edge
CLINOVA_ENVIRONMENT_ID=ENV_PHC
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `PHC_EDGE` |
| :--- | :--- |
| **Database** | Local SQLite 3.45+ (`/var/data/clinova/db/clinova_phc.db`). WAL mode enabled. `PRAGMA synchronous = NORMAL; PRAGMA busy_timeout = 5000;`. |
| **Media Storage** | Local Linux filesystem (`/var/data/clinova/media/`). High-endurance ext4 partition. Directory permissions `0750`. |
| **AI Runtime** | Pluggable local execution: `local_qwen` (Qwen2.5-3B-Instruct Q4 quantized running via llama.cpp/vLLM on CPU) with automatic fallback to `local_rules`. |
| **Speech Runtime** | `faster-whisper` (`base-int8` running on CPU cores 2 & 3). Local Indian English, Hindi, and Odia acoustic models. |
| **OCR Runtime** | `PaddleOCR` (v4 lightweight CPU models). Ingestion queue bounded to 1 concurrent job to prevent CPU throttling. |
| **Network Expectations**| Local LAN only (`192.168.1.0/24`). Internet link is intermittent, high-latency, or absent. Frontline tablets connect via local Wi-Fi. |
| **Offline Behavior** | **100% Autonomous Operational Authority.** Local server is the authoritative source of truth for the facility. |
| **Sync Behavior** | `BIDIRECTIONAL`. Background daemon polls for district hub reachability every 300s; pushes append-only `sync_journals` when WAN connects. |
| **Logging & Tracing** | `LOG_LEVEL=INFO`. Structured JSON written to rotating local log files (`/var/log/clinova/`). Zero PHI in logs. |
| **Data Safety Mode** | Configurable: Starts in `synthetic` during initial commissioning; switches to `live` only upon affirmative Medical Officer sign-off. |
| **Security Mode** | Strong hardware-bound `SECRET_KEY` stored in `/etc/clinova/secrets/jwt.key` (`chmod 600`). Local LAN HTTPS self-signed cert. |
| **Frontend Styling** | Plain CSS Modules + CSS Custom Properties. Fast rendering on low-cost Android/iPad tablets. |

---

## 3. Canonical `.env` Profile for `PHC_EDGE`

```ini
# ==============================================================================
# CLINOVA AI - PHC Edge Node Configuration (/etc/clinova/clinova.env)
# ==============================================================================

# Identity & Deployment
APP_ENV=phc_edge
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI — Rural Primary Health Centre Workstation"
APP_VERSION=2.0.0
DEBUG=False
API_V1_STR=/api/v1

# Networking & Hosts (Bound to Local Clinic Server LAN IP)
BACKEND_HOST=192.168.1.10
BACKEND_PORT=8000
API_BASE_URL=http://192.168.1.10:8000
FRONTEND_BASE_URL=http://192.168.1.10:3000
CORS_ORIGINS=["http://192.168.1.*","http://localhost:3000"]

# Frontend Inlined Variables (Injected during Docker/Node container boot)
NEXT_PUBLIC_APP_ENV=phc_edge
NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID=ENV_PHC
NEXT_PUBLIC_API_URL=http://192.168.1.10:8000
NEXT_PUBLIC_APP_NAME="CLINOVA AI — PHC Workstation"
NEXT_PUBLIC_VERSION="2.0.0"
NEXT_PUBLIC_DATA_MODE=live
NEXT_PUBLIC_OFFLINE_MODE=true

# Security & Secrets (Loaded securely from host vault)
SECRET_KEY=phc-edge-hardened-jwt-secret-salt-847291048201-kalahandi-phc-01!
ACCESS_TOKEN_EXPIRE_MINUTES=480
JWT_ALGORITHM=HS256

# Persistence (Local SQLite WAL Engine)
DATABASE_URL=sqlite+aiosqlite:////var/data/clinova/db/clinova_phc.db
LOCAL_DATABASE_PATH=/var/data/clinova/db/clinova_phc.db
DB_BUSY_TIMEOUT_MS=5000

# Storage (Local Filesystem on Edge Mini-PC)
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=/var/data/clinova/media
STORAGE_TEMP_PATH=/var/data/clinova/media/tmp
MAX_UPLOAD_SIZE_BYTES=10485760
MEDIA_RETENTION_POLICY_DAYS=30

# Compliance & Clinical Safety
CLINOVA_DATA_MODE=live
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Operations & Intelligence Providers
OFFLINE_MODE=True
SYNC_MODE=BIDIRECTIONAL
SYNC_ENDPOINT=https://hub.district-health.gov.in/api/v1/sync
SYNC_BATCH_SIZE=25

AI_PROVIDER=local_qwen
AI_BASE_URL=http://127.0.0.1:8080/v1
AI_MODEL=qwen2.5-3b-instruct-q4
WHISPER_MODEL=base-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Observability
LOG_LEVEL=INFO
LOG_DESTINATION=FILE_ROTATING_JSON

# Feature Flags (Optimized for Rural Facility Flow)
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

## 4. Invariants Enforced in `PHC_EDGE`
1. **Inv-PHC-1 (Local Clinical Finality):** Triage decisions, vital readings, and doctor prescriptions are committed to local SQLite immediately; zero operations block waiting for internet or cloud sync.
2. **Inv-PHC-2 (Low-Power Hardware Bounds):** Background AI perception processes run with lowered OS scheduling priority (`nice -n 10`) to prevent starvation of the core triage database and HTTP event loop.
3. **Inv-PHC-3 (Rural Single-Doctor Override):** In single-doctor rural facilities during night shifts, the secondary doctor sign-off requirement for thrombolysis/transfusion may be bypassed with automated escalation flags.
