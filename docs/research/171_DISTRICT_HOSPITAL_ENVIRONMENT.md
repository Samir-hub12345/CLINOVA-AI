# CLINOVA AI — District Hospital Environment (`DISTRICT_HOSPITAL`) Specification

> **Document ID:** `RES-171`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Hospital Systems Architecture, Enterprise Informatics & Clinical Operations Group  

---

## 1. Environment Identity & Purpose

The **District Hospital (`DISTRICT_HOSPITAL`)** environment specifies the on-premise multi-workstation deployment for major secondary and tertiary public healthcare facilities (IPHS Level 4 District Hospitals, Sub-Divisional Hospitals, and Medical College Hospitals with 100–500 beds).

In this environment, CLINOVA AI coordinates dozens of concurrent clinical terminals: Registration Kiosks, Triage Desks, Casualty Resuscitation Bays, Specialty Outpatient Clinics (Cardiology, Orthopedics, General Medicine), Inpatient Wards, and Referral Operations Desks.

```
APP_ENV=district_hospital
CLINOVA_ENVIRONMENT_ID=ENV_GOV_HOSPITAL
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `DISTRICT_HOSPITAL` |
| :--- | :--- |
| **Database** | High-availability PostgreSQL 15+ cluster via `postgresql+asyncpg`. Connection pooling configured via PgBouncer. `DB_POOL_SIZE=20, DB_MAX_OVERFLOW=30`. |
| **Media Storage** | High-capacity on-premise Enterprise NAS / SAN mount (`/mnt/hospital_san/clinova/media/`) or internal on-prem MinIO cluster. |
| **AI Runtime** | Dedicated on-premise inference server hosting `qwen2.5-7b-instruct-q4` (or 14B) on workstation GPU/NPU or multi-socket Xeon CPU. |
| **Speech Runtime** | `faster-whisper` (`medium-int8` / `large-v3-turbo`) supporting simultaneous concurrent audio transcriptions across casualty desks. |
| **OCR Runtime** | Multi-worker `PaddleOCR` cluster handling batch document ingestion for prior discharge summaries and government lab sheets. |
| **Network Expectations**| Hospital campus Ethernet/Wi-Fi LAN (Gigabit backbone). Redundant dual-ISP fiber uplink to State Data Centre. |
| **Offline Behavior** | Hospital LAN remains 100% operational during external internet blackouts. All departments continue active care. |
| **Sync Behavior** | `CLOUD_NATIVE` / `HUB_MASTER`. Serves as the aggregation target for peripheral rural PHC sync journals while pushing state indicators to SDC. |
| **Logging & Tracing** | `LOG_LEVEL=INFO`. Centralized syslog/Prometheus exporter. Zero raw PHI in logs. |
| **Data Safety Mode** | `CLINOVA_DATA_MODE=live` (Production clinical operations). Requires validated hospital RMP credentials. |
| **Security Mode** | Production-hardened 64-character cryptographic keys. Mandatory HTTPS (TLS 1.3). Strict CORS restricted to hospital domain. |
| **Frontend Styling** | Plain CSS Modules + CSS Custom Properties. Ultra-fast rendering across dual-monitor clinical workstations. |

---

## 3. Canonical `.env` Profile for `DISTRICT_HOSPITAL`

```ini
# ==============================================================================
# CLINOVA AI - District Hospital On-Premise Configuration (/etc/clinova/hospital.env)
# ==============================================================================

# Identity & Deployment
APP_ENV=district_hospital
CLINOVA_ENVIRONMENT_ID=ENV_GOV_HOSPITAL
APP_NAME="CLINOVA AI — District Hospital Clinical Command Center"
APP_VERSION=2.0.0
DEBUG=False
API_V1_STR=/api/v1

# Networking & Ingress (Hospital Enterprise LAN)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_BASE_URL=https://clinova.hospital.internal/api/v1
FRONTEND_BASE_URL=https://clinova.hospital.internal
CORS_ORIGINS=["https://clinova.hospital.internal","https://triage.hospital.internal","https://doctor.hospital.internal"]

# Frontend Inlined Variables (Injected during production build)
NEXT_PUBLIC_APP_ENV=district_hospital
NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID=ENV_GOV_HOSPITAL
NEXT_PUBLIC_API_URL=https://clinova.hospital.internal/api/v1
NEXT_PUBLIC_APP_NAME="CLINOVA AI — District Hospital"
NEXT_PUBLIC_VERSION="2.0.0"
NEXT_PUBLIC_DATA_MODE=live
NEXT_PUBLIC_OFFLINE_MODE=false

# Security & Secrets (Injected via Linux Systemd / Vault)
SECRET_KEY=district-hospital-prod-super-secure-key-64-bytes-entropy-minimum-91823746192837461928374619283746!
ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_ALGORITHM=HS256

# Persistence (PostgreSQL 15 Cluster)
DATABASE_URL=postgresql+asyncpg://clinova_app:secure_db_pass_9281@10.0.10.50:5432/clinova_hospital_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Storage (Enterprise NAS Mount)
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=/mnt/hospital_san/clinova/media
STORAGE_TEMP_PATH=/mnt/hospital_san/clinova/media/tmp
MAX_UPLOAD_SIZE_BYTES=26214400
MEDIA_RETENTION_POLICY_DAYS=90

# Compliance & Clinical Safety
CLINOVA_DATA_MODE=live
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Intelligence & Perception
OFFLINE_MODE=False
SYNC_MODE=CLOUD_NATIVE
SYNC_ENDPOINT=https://sdc.health.state.gov.in/api/v1/sync
SYNC_BATCH_SIZE=100

AI_PROVIDER=local_qwen
AI_BASE_URL=http://10.0.10.80:8000/v1
AI_MODEL=qwen2.5-7b-instruct-q4
WHISPER_MODEL=medium-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Observability
LOG_LEVEL=INFO
LOG_DESTINATION=REMOTE_SYSLOG_JSON

# Feature Flags (Enterprise Hospital Flow)
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

## 4. Invariants Enforced in `DISTRICT_HOSPITAL`
1. **Inv-DH-1 (Mandatory Dual Review):** In a tertiary facility with multiple doctors on duty, the secondary physician verification gate for thrombolysis, major surgery, and blood transfusion cannot be bypassed.
2. **Inv-DH-2 (Subordinate Facility Sync Authority):** The hospital server maintains separate cryptographic sync journals for each subordinate PHC node, verifying Merkle proofs before applying peripheral batch records.
3. **Inv-DH-3 (Zero Public Storage Leakage):** Storage paths reside on isolated internal storage networks; zero media URLs are accessible outside the hospital perimeter firewall.
