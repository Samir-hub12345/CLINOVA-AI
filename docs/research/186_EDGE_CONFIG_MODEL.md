# CLINOVA AI — Local PHC Edge Topology & Configuration Model

> **Document ID:** `RES-186`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Edge Infrastructure, Embedded Linux & Rural Informatics Group  

---

## 1. Physical Edge Architecture Overview

In a rural Primary Health Centre (PHC), the computing infrastructure consists of:
1. **Local Clinic Server:** A ₹12,000–₹16,000 fanless industrial Mini-PC (Intel Celeron N5105, 8GB RAM, 128GB SSD, dual Ethernet/Wi-Fi) powered by a 12V DC battery backup.
2. **Local Wi-Fi Router:** An un-metered, private wireless access point (`192.168.1.1/24`) operating completely air-gapped from the public internet.
3. **Frontline Staff Devices:** 2 to 4 low-cost Android tablets or refurbished iPads used by Staff Nurses, Medical Officers, and Registration Clerks.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LOCAL PHC EDGE TOPOLOGY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ FRONTLINE TABLETS (Thin Clients) ]                                       │
│  ├── Nurse Triage Tablet    (Web Browser / PWA)                             │
│  ├── Doctor Review Tablet   (Web Browser / PWA)                             │
│  └── Registration Tablet    (Web Browser / PWA)                             │
│          │                                                                  │
│          ▼ Local Wi-Fi LAN (WPA3 / 192.168.1.0/24)                          │
│  [ LOCAL CLINIC SERVER (Fanless Mini-PC) ]                                  │
│  ├── Ingress Gateway: Nginx / Caddy (`192.168.1.10:80 / :443`)              │
│  ├── Application: FastAPI Modular Monolith (`127.0.0.1:8000`)               │
│  ├── Local AI Loopback: llama.cpp / vLLM (`127.0.0.1:8080`)                 │
│  ├── Local Persistence: SQLite 3.45 WAL (`/var/data/clinova/db/`)           │
│  └── Local Media Storage: Ext4 Partition (`/var/data/clinova/media/`)       │
│          │                                                                  │
│          ▼ Intermittent Cellular / WAN (When Available)                     │
│  [ DISTRICT HOSPITAL CENTRAL SYNC HUB ]                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontline Device Thin-Client Boundaries

A critical requirement is that **Frontline Tablets remain Thin Clients**:
- **Zero Local Database:** Frontline tablets do not host SQLite or run backend microservices.
- **Transient Draft Storage Only:** Tablets use browser `localStorage` solely to buffer dirty form drafts for 5 minutes in case the tablet screen sleeps or reloads.
- **Zero Raw Secrets:** Tablets receive only short-lived clinician session JWTs. They hold zero database passwords, zero encryption master keys, and zero sync credentials.
- **Display Resolution & Touch:** Optimized for 10-inch tablets (1280x800 resolution) with minimum touch targets of 48px.

---

## 3. Server Address Discovery & Connectivity Configuration

When a frontline tablet connects to the clinic Wi-Fi, it discovers the Local Clinic Server using a three-tier fallback mechanism:

1. **Tier 1 (mDNS / Zeroconf):** `http://clinova-phc.local:8000` (Zero-configuration discovery across Apple/Android devices).
2. **Tier 2 (Static Local DNS):** The clinic router assigns a static reservation `192.168.1.10` mapped to `clinova.local`.
3. **Tier 3 (Hardcoded LAN IP Fallback):** Direct access via `http://192.168.1.10:8000`.

---

## 4. Edge Service Configuration Manifest (`/etc/clinova/clinova.env`)

```ini
# Edge Node Identity
APP_ENV=phc_edge
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI — Rural Primary Health Centre"
DEBUG=False

# Network Bindings
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
API_BASE_URL=http://192.168.1.10:8000
FRONTEND_BASE_URL=http://192.168.1.10:3000
CORS_ORIGINS=["http://192.168.1.*","http://localhost:3000"]

# Local Persistence (Encrypted Ext4 Partition)
DATABASE_URL=sqlite+aiosqlite:////var/data/clinova/db/clinova_phc.db
LOCAL_DATABASE_PATH=/var/data/clinova/db/clinova_phc.db
DB_BUSY_TIMEOUT_MS=5000

# Local Media Storage
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=/var/data/clinova/media
STORAGE_TEMP_PATH=/var/data/clinova/media/tmp
MAX_UPLOAD_SIZE_BYTES=10485760
MEDIA_RETENTION_POLICY_DAYS=30

# Local AI Engine Loopback (llama.cpp CPU server)
AI_PROVIDER=local_qwen
AI_BASE_URL=http://127.0.0.1:8080/v1
AI_MODEL=qwen2.5-3b-instruct-q4
WHISPER_MODEL=base-int8
OCR_ENGINE=paddleocr-v4
TRANSLATION_ENGINE=indic-trans-v2

# Central District Synchronization (Asynchronous Push/Pull)
OFFLINE_MODE=True
SYNC_MODE=BIDIRECTIONAL
SYNC_ENDPOINT=https://hub.district-health.gov.in/api/v1/sync
SYNC_BATCH_SIZE=25
SYNC_POLL_INTERVAL_SECONDS=300

# Observability
LOG_LEVEL=INFO
LOG_DESTINATION=FILE_ROTATING_JSON
```

---

## 5. Edge Power & Hardware Resilience Invariants
1. **Inv-EDGE-1 (UPS Safe Shutdown):** The local server monitors battery telemetry via `apcupsd` or DC telemetry. At $< 10\%$ battery reserve, the system flushes SQLite WAL buffers to disk, issues a clean `WAL_CHECKPOINT(TRUNCATE)`, and halts safely to prevent filesystem corruption.
2. **Inv-EDGE-2 (Memory Pressure Throttling):** If available system RAM drops below 1.0 GB, the background AI perception service suspends OCR queueing to guarantee zero interference with active doctor triage.
