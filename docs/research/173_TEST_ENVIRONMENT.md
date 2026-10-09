# CLINOVA AI — Automated Test Environment (`TEST`) Specification

> **Document ID:** `RES-173`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Quality Assurance, Test Automation & CI/CD Systems Group  

---

## 1. Environment Identity & Purpose

The **Test (`TEST`)** environment provides an isolated, deterministic, high-speed execution sandbox for automated unit tests, integration suites, regression harnesses, adversarial clinical fuzzing, and CI/CD pipelines (e.g. GitHub Actions).

It executes in seconds, creates zero persistent state on developer workstations, blocks all outbound network requests, and eliminates heavy machine-learning model weights by using pure deterministic test doubles.

```
APP_ENV=test
CLINOVA_ENVIRONMENT_ID=ENV_PHC  # Dynamically parameterized during test suite execution
```

---

## 2. Technical Profile Specification

| Operational Dimension | Specification in `TEST` |
| :--- | :--- |
| **Database** | In-memory or ephemeral file SQLite (`sqlite+aiosqlite:///:memory:` or `./clinova-test.db`). Re-created per test session. |
| **Media Storage** | Ephemeral temporary directory (`./data/test_storage/`). Automatically purged upon test suite completion. |
| **AI Runtime** | `mock` / `local_rules`. Deterministic test doubles return instant fixtures in $< 1\text{ms}$. Zero GPU or SLM memory consumption. |
| **Speech Runtime** | Mock audio transcriber returning pre-configured test strings with synthetic word timestamps. |
| **OCR Runtime** | Mock document parser returning deterministic bounding boxes and synthetic lab values. |
| **Network Expectations**| Complete network isolation. Outbound socket connections raise test assertion errors. |
| **Offline Behavior** | Simulated programmatically via test fixtures (testing both online and partitioned states). |
| **Sync Behavior** | Isolated local sync journal validation; tests push/pull protocols against in-memory mock endpoints. |
| **Logging & Tracing** | `LOG_LEVEL=WARNING`. Mutes noisy informational logging during test runs; records errors only. |
| **Data Safety Mode** | `CLINOVA_DATA_MODE=synthetic` (**STRICT & IMMUTABLE**). Attempts to load non-synthetic fixtures fail immediately. |
| **Security Mode** | Standardized ephemeral test keys (`clinova-test-secret-key-32chars-minimum!`). Short-lived JWTs (5 min). |
| **Frontend Styling** | Headless DOM (Jest / Vitest / Playwright). Component tests evaluate pure CSS Module classes without visual rendering stalls. |

---

## 3. Canonical Configuration Profile for `TEST`

```ini
# ==============================================================================
# CLINOVA AI - Automated Test Environment Configuration (.env.test)
# ==============================================================================

# Identity & Deployment
APP_ENV=test
CLINOVA_ENVIRONMENT_ID=ENV_PHC
APP_NAME="CLINOVA AI (Automated Test)"
APP_VERSION=2.0.0
DEBUG=True
API_V1_STR=/api/v1

# Networking & Sockets
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8888
API_BASE_URL=http://127.0.0.1:8888
FRONTEND_BASE_URL=http://127.0.0.1:3333
CORS_ORIGINS=["http://127.0.0.1:3333"]

# Security & Secrets
SECRET_KEY=clinova-test-secret-key-32chars-minimum-salt-for-testing-only!
ACCESS_TOKEN_EXPIRE_MINUTES=5
JWT_ALGORITHM=HS256

# Persistence (Ephemeral SQLite In-Memory)
DATABASE_URL=sqlite+aiosqlite:///:memory:
LOCAL_DATABASE_PATH=null
DB_BUSY_TIMEOUT_MS=1000

# Storage (Temporary Test Directory)
STORAGE_MODE=LOCAL_FS
STORAGE_PATH=./data/test_storage
STORAGE_TEMP_PATH=./data/test_storage/tmp
MAX_UPLOAD_SIZE_BYTES=5242880
MEDIA_RETENTION_POLICY_DAYS=1

# Compliance & Safety
CLINOVA_DATA_MODE=synthetic
ANONYMIZATION_ENABLED=True
AUDIT_MODE=True
PHI_LOGGING_POLICY=STRICT_REDACTION

# Intelligence & Perception (Deterministic Mock Doubles)
OFFLINE_MODE=True
SYNC_MODE=OFFLINE_ONLY
AI_PROVIDER=mock
AI_MODEL=test-mock-model
WHISPER_MODEL=test-mock-whisper
OCR_ENGINE=test-mock-ocr
TRANSLATION_ENGINE=test-mock-trans

# Observability
LOG_LEVEL=WARNING
LOG_DESTINATION=CONSOLE_JSON

# Feature Flags (All Enabled for Comprehensive Test Coverage)
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

## 4. Invariants Enforced in `TEST`
1. **Inv-TEST-1 (Complete State Hermeticity):** Every test case or suite executes in an isolated transaction or ephemeral in-memory database; state cannot leak across tests.
2. **Inv-TEST-2 (Zero Socket Leakage):** Unit tests must execute cleanly without internet connectivity or access to port 5432/8000.
3. **Inv-TEST-3 (Determinism):** Every clinical calculation (NEWS2, Shock Index, Epistemic Uncertainty, CAREGRAPH slope) must yield identical output across identical inputs across 1,000 runs.
