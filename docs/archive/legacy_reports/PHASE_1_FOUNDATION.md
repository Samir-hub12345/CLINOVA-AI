# Clinova AI — Phase 1: Project Foundation & Architecture Freeze

## 1. Executive Summary & Purpose
Phase 1 establishes a production-grade, secure, reproducible, and verifiable engineering foundation for **Clinova AI**. 
The objective of Phase 1 is **NOT** to prematurely implement full clinical intelligence or production infrastructure, but rather to eliminate architectural bottlenecks, enforce server-side security boundaries (RBAC + IDOR protection), establish proper database migration controls (Alembic), create an object storage architecture for medical documents, decouple long-running jobs (workers/queues), and provide dependable system health and telemetry monitoring.

---

## 2. Verified System Architecture

```text
                                 CLIENT BROWSERS
                    (Desktop Workstations, Tablets, Mobile Triage)
                                        │
                                        ▼ HTTP/3000
                       ┌─────────────────────────────────┐
                       │        Next.js 14 Frontend      │
                       │   - App Router (React 18 / TS)  │
                       │   - Tailwind CSS                │
                       │   - Adaptive Network Monitor    │
                       │   - Local Offline Queue         │
                       └────────────────┬────────────────┘
                                        │
                                        ▼ REST API / HTTP/8000
                       ┌─────────────────────────────────┐
                       │        FastAPI Backend API      │
                       │   - /api/v1/auth                │
                       │   - /api/v1/facilities (Tenants)│
                       │   - /api/v1/patients            │
                       │   - /api/v1/consultations       │
                       │   - /api/v1/cases (Triage)      │
                       │   - /api/v1/documents (Storage) │
                       │   - /api/v1/jobs (Async Tasks)  │
                       │   - /api/v1/health (Live/Ready) │
                       │   - /api/v1/audit-logs          │
                       └────────┬───────────────┬────────┘
                                │               │
              PostgreSQL (5432) │               │ Redis (6379)
                                ▼               ▼
                     ┌──────────────────┐  ┌──────────────────┐
                     │   PostgreSQL 16  │  │     Redis 7      │
                     │  - Alembic DDL   │  │  - Cache Client  │
                     │  - Users & Roles │  │  - Pub/Sub Queue │
                     │  - Facilities    │  │  - Rate Limiter  │
                     │  - Patients      │  │  - Health Ping   │
                     │  - Consultations │  └──────────────────┘
                     │  - Triage Cases  │
                     │  - Documents     │
                     │  - BackgroundJobs│
                     │  - Audit Logs    │
                     └─────────┬────────┘
                               │
                               ▼
                     ┌──────────────────┐
                     │  Object Storage  │
                     │ (storage_data/   │
                     │  Persistent Vol) │
                     │  - Scanned PDFs  │
                     │  - Blood Reports │
                     │  - Audio WAVs    │
                     └──────────────────┘
```

---

## 3. Implemented Phase 1 Deliverables

### A. Database Migrations (Alembic)
* **Framework:** Alembic 1.20 configured with asynchronous engine (`asyncpg`).
* **Environment Configuration:** `backend/alembic/env.py` dynamically sources database credentials from `app.core.config.settings.DATABASE_URL` and registers all declarative models via `Base.metadata`.
* **Migration 001:** `alembic/versions/e2c6c0aad9de_initial_phase1_foundation.py` autogenerates and manages all tables (`facilities`, `documents`, `background_jobs`, `users`, `patients`, `consultations`, `triage_cases`, `audit_logs`).
* **Execution Command:** `docker compose exec backend alembic upgrade head` or `alembic current`.

### B. Object Storage Architecture (Decoupled File Storage)
* **Separation of Concerns:** Binary medical documents (PDFs, pathology lab prints, images) are never stored in raw PostgreSQL database rows.
* **Metadata Store (PostgreSQL):** Model `Document` stores file metadata:
  * `id`: UUID primary key
  * `patient_id`, `case_id`, `encounter_id`, `facility_id`
  * `document_type`: Pathology Report, Lab Result, Imaging Scan, Clinical Note, Referral Letter, Prescription
  * `filename`: Original display name
  * `mime_type`: Validated MIME type
  * `file_size_bytes`: Integer size in bytes (max 50 MB)
  * `checksum_sha256`: SHA-256 cryptographic hash of contents
  * `storage_key`: Non-guessable path (`facilities/{fac_id}/patients/{pat_id}/documents/{doc_id}/{slug}`)
  * `storage_provider`: Local object storage provider (ready for S3/MinIO driver swap)
  * `status`: `STORED`, `PENDING_SCAN`, `PROCESSING`, `PROCESSED`, `FAILED`, `ARCHIVED`
* **Binary Storage Service:** `backend/app/services/storage.py` validates file size, checks MIME whitelist (`application/pdf`, `image/png`, `image/jpeg`, `image/webp`, `image/tiff`), calculates SHA-256 hash, and prevents directory traversal attacks via path normalization.
* **REST Endpoints:**
  * `POST /api/v1/documents/upload`: Upload file and register metadata.
  * `GET /api/v1/documents/{id}`: Retrieve document metadata.
  * `GET /api/v1/documents/{id}/download`: Stream original binary content with authorization check.
  * `GET /api/v1/documents`: List documents with patient isolation.

### C. Background Task & Worker Queue Architecture
* **Non-Blocking Execution:** CPU-bound and network-bound clinical processing (OCR parsing, audio speech transcription, AI clinical synthesis) are decoupled from the web request loop.
* **Job Model (`background_jobs`):**
  * `id`: Job UUID
  * `job_type`: `DOCUMENT_OCR`, `AUDIO_TRANSCRIPTION`, `AI_TRIAGE_SYNTHESIS`, `EXPORT`, `NOTIFICATION`
  * `status`: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `RETRYING`, `CANCELLED`
  * `payload_json`, `result_json`, `error_message`, `retry_count`, `max_retries`
  * `created_at`, `started_at`, `completed_at`
* **REST Endpoints:**
  * `POST /api/v1/jobs`: Enqueue long-running task (returns HTTP 202 ACCEPTED with job ID).
  * `GET /api/v1/jobs/{job_id}`: Poll status, duration, and output.

### D. Multi-Facility / Tenant Foundation
* **Tenant Isolation Model (`facilities`):**
  * `id`: UUID primary key
  * `facility_code`: Unique clinical identifier (e.g., `FAC-DISTRICT-01`)
  * `name`: Facility title (e.g., "Government District Hospital")
  * `facility_type`: "District Hospital", "Primary Health Center", "Casualty / ER", "Tele-Triage Hub"
  * `address`, `contact_phone`, `contact_email`, `is_active`
* **REST Endpoints:**
  * `GET /api/v1/facilities`: List active facilities.
  * `POST /api/v1/facilities`: Register facility node (Admin only).
  * `GET /api/v1/facilities/{id}`: Facility profile lookup.

### E. Security, IDOR Protection & RBAC Hardening
* **IDOR Resolution in Consultations:** Fixed `GET /api/v1/consultations/{consultation_id}` by introducing strict resource-level verification:
  ```python
  if current_user.role == UserRole.PATIENT:
      if not consultation.patient or consultation.patient.email != current_user.email:
          raise HTTPException(status_code=403, detail="Access denied to another patient's consultation records.")
  ```
* **Production Configuration Safeguards:** Added model validator in `backend/app/core/config.py` preventing execution with `DEBUG=True` or default development `SECRET_KEY` when `ENVIRONMENT=production`.

### F. Health & Telemetry Probes
* `GET /api/v1/health`: Basic operational metadata.
* `GET /api/v1/health/live`: Liveness probe for Kubernetes / Docker daemon.
* `GET /api/v1/health/ready`: Deep dependency readiness probe actively querying PostgreSQL (`SELECT 1`) and Redis (`PING`). Returns HTTP 503 if PostgreSQL is unreachable.

### G. Redis Integration & Failure Resilience
* Async connection pooling using `redis.asyncio` in `backend/app/core/redis.py`.
* Graceful degradation: If Redis is offline or disconnected, application logs a warning and falls back to in-memory state rather than throwing unhandled 500 exceptions.

---

## 4. Verification Evidence

* **Backend Pytest Suite:** 23 out of 23 tests passing (100% pass rate).
  * 17 existing integration tests
  * 6 new security, IDOR, health readiness, and object storage tests
* **Frontend TypeScript Compilation:** `npx tsc --noEmit` exited with code 0 (0 errors, 0 warnings).
* **Frontend Production Build:** `npm run build` compiled 15 static/dynamic routes successfully.
* **Database State:** 7 relational tables managed via Alembic `e2c6c0aad9de (head)`.

---

## 5. Architectural Decisions & Principles

1. **PostgreSQL Is the Sole Source of Truth:** All structured clinical records, audit events, and document metadata reside in PostgreSQL. Redis is strictly a cache and ephemeral queue; its loss never compromises clinical data integrity.
2. **AI Is Assistive, Non-Diagnostic Decision Support:** AI outputs do not formulate final medical diagnoses. Every recommendation requires human clinician sign-off.
3. **Defense in Depth for File Storage:** No medical file is trusted. File sizes are capped at 50 MB, MIME types are strictly verified, SHA-256 hashes are computed for integrity, and filenames are converted to safe slugs to prevent directory traversal.
4. **Offline Conflict Principle:** Synchronizable records must track `record_version`, `device_id`, `sync_id`, and `updated_at`. When multi-device conflicts occur, the server must flag a conflict state rather than silently overwriting clinical history.

---

## 6. Phase 1 Exit Status: GO

Phase 1 has achieved its objectives. The repository is reproducible, migration-ready, testable, type-safe, and ready to progress into Phase 2 (Clinical Database Architecture).
