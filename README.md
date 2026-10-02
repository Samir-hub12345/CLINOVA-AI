# CLINOVA AI

**Multimodal Healthcare Triage Assistant for Government and Institutional Health Facilities**  

---

> [!WARNING]
> ### 🔒 Mandatory Safety & Non-Diagnostic Disclaimer
> **Educational prototype and triage-support purposes only.** This system does **not** diagnose, prescribe treatment, or replace a qualified healthcare professional. All AI-generated information requires human review before clinical action.

---

## 📋 Executive Overview

**CLINOVA AI** is an explainable, multimodal, human-in-the-loop healthcare triage support platform engineered for government district hospitals, primary health centers (PHCs), public health outreach camps, industrial health units, and campus clinics. 

The system organizes high-volume patient inputs into structured, reviewer-facing notes to accelerate qualified clinician decision-making:
* **Multimodal Intake**: Voice recording (6-state audio capture), autosizing text symptom narratives, and sample pathology report uploads.
* **Multilingual Normalization**: Preserves regional languages (**Odia**, **Hindi**) while presenting structured English representations for clinician efficiency.
* **Deterministic Risk Signal Engine**: Transparent, explainable rule checks (`TRIAGE-R01` to `TRIAGE-R06`) for immediate breathing, cardiovascular, and hemorrhage attention flags.
* **Report OCR Extraction**: Automatic parameter parsing (e.g. Complete Blood Count / CBC) with confidence scores and verification states.
* **Human-in-the-Loop Review Gate**: Mandatory review interface where medical officers confirm, edit, reject, or escalate notes.
* **Referral Note Preparation**: One-click generation of printable referral support documents for secondary and tertiary healthcare handoffs.
* **Privacy by Design**: Anonymization layer redacting phone numbers, emails, and identification sequences; short retention policy with one-click data deletion.
* **100% Offline / DEMO MODE**: Operates out of the box with zero external API key requirements.

---

## 🏛️ Architecture & Data Flow

```text
Patient / Kiosk / Health Worker
               │
               ▼
┌──────────────────────────────────────────────┐
│             DEMO CONSENT & CONTEXT           │
│  Age • Gender • Facility • Preferred Lang    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│           MULTIMODAL INTAKE PIPELINE         │
│  Voice (Speech-to-Text) • Typed Narrative    │
│  Report OCR (CBC Panel) • Basic Visuals      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│        ANONYMIZATION & PRIVACY LAYER         │
│  PII Redaction • Synthetic Case ID (CLV-xxx) │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│        INTELLIGENCE & EXTRACTION ENGINE      │
│  Language Normalization (Odia/Hindi -> Eng)  │
│  Timeline Synthesis • Missing Info Detection │
│  Deterministic Urgency Rules (R01 - R06)     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│          STRUCTURED REVIEWER NOTE            │
│  Chief Concern • Timeline • OCR Data • Flags │
│      *AI GENERATED — HUMAN REVIEW REQUIRED*  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             HUMAN REVIEW GATE                │
│       Medical Officer Review Dashboard       │
│    Confirm  •  Edit  •  Reject  •  Escalate  │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│           ACTION & REFERRAL HANDOFF          │
│   Official Referral Note • Facility Handoff  │
│      Immutable Audit Trail • Data Purge      │
└──────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

* **Frontend**: Next.js 15+ (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons.
* **Backend**: FastAPI (Python 3.12/3.14 on Uvicorn ASGI), Pydantic v2 validation, SQLAlchemy 2.0 (async).
* **Database & Cache**: PostgreSQL 16 (or async SQLite local zero-install mode) & Redis 7 (with graceful in-memory fallback).
* **AI & Rules Engine**: Modular provider architecture with Google Gemini 2.5 Flash API integration and deterministic local heuristic rule engine fallback (`DEMO_MODE=true`).
* **Local Orchestration**: Native Windows PowerShell orchestrator (`scripts/clinova.ps1`). Production deployment supports Docker (`infrastructure/docker/docker-compose.prod.yml`).

---

## 📚 Documentation Index

CLINOVA AI maintains a comprehensive, production-grade technical and clinical documentation suite:

### Core Architecture & System Guides
| Document | Primary Focus | Target Audience |
| :--- | :--- | :--- |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | End-to-end data flow, neuro-symbolic patterns, subsystem architecture. | Software Architects, Full-Stack Devs |
| **[API_SPECIFICATION.md](API_SPECIFICATION.md)**| REST API endpoints, schemas, authentication, status codes, examples. | Backend & Frontend API Integrators |
| **[clinical-rules.md](clinical-rules.md)** | Deterministic triage rules (`TRIAGE-R01`–`R06`), safety thresholds. | Medical Officers, Informatics Reviewers |
| **[FEATURES.md](FEATURES.md)** | Multimodal intake, risk engine, queue, review gate, referrals, demo hub. | Clinicians, Product Owners, Developers |
| **[INFRASTRUCTURE.md](INFRASTRUCTURE.md)** | Topology, Docker Compose, ports, PM2, systemd, TLS, hardware profiles. | DevOps, SREs, Systems Administrators |
| **[SECURITY.md](SECURITY.md)** | DISHA/ABDM compliance, PII/Aadhaar scrubbing, JWT, audit logs, purge. | Security Engineers, Compliance Officers |
| **[TESTING.md](TESTING.md)** | Automated test suite (66 tests), Docker testing, frontend build, checklist. | QA Engineers, Backend Developers |
| **[ROADMAP.md](ROADMAP.md)** | Phased roadmap: MTS pediatric matrix, PWA, Bhashini, ABDM, biomarkers. | Clinical Informatics, Engineering Leads |
| **[deploy.md](deploy.md)** | Step-by-step production deployment, Docker, bare-metal, disaster recovery. | Infrastructure & DevOps Teams |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contributor setup, branching, git guidelines, validation checklist. | Open-Source Contributors |
| **[CHANGELOG.md](CHANGELOG.md)** | Semantic release history and implemented vs. planned status matrix. | Maintainers & Evaluators |

### Clinical Specifications & Phase Reports (`docs/`)
| Document | Primary Focus | Target Audience |
| :--- | :--- | :--- |
| **[docs/DATABASE_ARCHITECTURE.md](docs/DATABASE_ARCHITECTURE.md)** | Full clinical database specification: 18 tables, Mermaid ERD, lifecycles, and indexes. | System Architects, Database Engineers |
| **[docs/DOCUMENT_ARCHITECTURE.md](docs/DOCUMENT_ARCHITECTURE.md)** | Medical document architecture: magic byte validation, quarantine vault, immutable amendments. | Backend Engineers, Security Auditors |
| **[docs/OBJECT_STORAGE_ARCHITECTURE.md](docs/OBJECT_STORAGE_ARCHITECTURE.md)** | Storage backend abstraction, bucket key hierarchy, chunked streaming, HMAC presigned URLs. | Infrastructure & Backend Engineers |
| **[docs/DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md)** | RTO/RPO targets, automated database backup, restore verification protocols. | DevOps, SREs, Site Administrators |
| **[docs/PHASE_3_COMPLETION_REPORT.md](docs/PHASE_3_COMPLETION_REPORT.md)** | Phase 3 completion report: object storage, document security, verification evidence. | Engineering Leads, Evaluators |
| **[docs/PHASE_3_INSPECTION_REPORT.md](docs/PHASE_3_INSPECTION_REPORT.md)** | Phase 3 baseline freeze and pre/post audit matrix. | System Architects, Auditors |
| **[docs/PHASE_2_COMPLETION_REPORT.md](docs/PHASE_2_COMPLETION_REPORT.md)** | Phase 2 completion report: clinical data model, observations, notes, referrals. | Technical Leads, Evaluators |
| **[docs/PHASE_2_INSPECTION_REPORT.md](docs/PHASE_2_INSPECTION_REPORT.md)** | Phase 2 pre/post audit, schema gap analysis, and before-vs-after comparison matrix. | System Architects, Auditors |
| **[docs/PHASE_1_COMPLETION_REPORT.md](docs/PHASE_1_COMPLETION_REPORT.md)** | Official Phase 1 completion declaration, verification matrix, test evidence, GO verdict. | Engineering Leads, Evaluators |
| **[docs/PHASE_1_FOUNDATION.md](docs/PHASE_1_FOUNDATION.md)** | Phase 1 technical specification: migrations, object storage, workers, multi-facility. | Backend Engineers, SREs |
| **[docs/PHASE_1_INSPECTION_REPORT.md](docs/PHASE_1_INSPECTION_REPORT.md)** | Baseline freeze and re-inspection matrix for Phase 1 foundation. | System Architects, Auditors |
| **[docs/CLEANUP_INSPECTION_REPORT.md](docs/CLEANUP_INSPECTION_REPORT.md)** | Safe codebase cleanup baseline report, duplicate inventory, and reference audit. | Quality Engineers, Maintainers |

### Clinical Governance & Compliance Policies (`docs/compliance/`)
| Policy Document | Scope & Purpose | Target Audience |
| :--- | :--- | :--- |
| **[docs/compliance/CLINICAL_VALIDATION_PROTOCOL.md](docs/compliance/CLINICAL_VALIDATION_PROTOCOL.md)** | Formal clinical validation protocol, sensitivity/specificity benchmarks, HITL gate mandate. | Medical Officers, Clinical Reviewers |
| **[docs/compliance/HIPAA_COMPLIANCE_MAPPING.md](docs/compliance/HIPAA_COMPLIANCE_MAPPING.md)** | Administrative, physical, and technical safeguards mapping for clinical data protection. | Compliance Officers, Security Teams |
| **[docs/compliance/DATA_RETENTION_AND_DISPOSAL_POLICY.md](docs/compliance/DATA_RETENTION_AND_DISPOSAL_POLICY.md)** | Automated retention sweeps, cryptographic shredding, and media purge policies. | Data Protection Officers, SREs |
| **[docs/compliance/INCIDENT_RESPONSE_POLICY.md](docs/compliance/INCIDENT_RESPONSE_POLICY.md)** | Security incident classification, containment, forensics, and notification timelines. | SecOps, System Administrators |
| **[docs/compliance/PRIVACY_POLICY.md](docs/compliance/PRIVACY_POLICY.md)** | Patient data sovereignty, PII de-identification, and consent management. | Privacy Officers, Legal Counsel |
| **[docs/compliance/PRODUCTION_LAUNCH_CHECKLIST.md](docs/compliance/PRODUCTION_LAUNCH_CHECKLIST.md)** | Comprehensive 8-category go-live verification checklist for healthcare deployments. | Lead Engineers, Facility Directors |

---

## 📁 Repository Structure

```text
CLINOVA-AI/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                             # Polished healthcare landing page
│   │   │   ├── intake/page.tsx                      # 4-step Multimodal Intake Wizard
│   │   │   ├── triage/page.tsx                      # Triage assessment portal
│   │   │   ├── review/page.tsx                      # Prioritized Reviewer Queue
│   │   │   ├── review/case/[caseId]/page.tsx        # Case Review & Human Gate
│   │   │   ├── review/case/[caseId]/referral/page.tsx # Printable Referral Note
│   │   │   ├── dashboard/page.tsx                   # Unified role-adaptive clinical dashboard
│   │   │   ├── patients/page.tsx                    # Patient directory (EHR)
│   │   │   ├── patients/[id]/page.tsx               # Patient chart detail
│   │   │   ├── consultations/page.tsx               # Consultations list
│   │   │   ├── documents/page.tsx                   # Medical documents repository
│   │   │   ├── audit/page.tsx                       # Audit trail viewer
│   │   │   ├── demo/page.tsx                        # 6 Public Health Demo Scenarios
│   │   │   └── login/page.tsx                       # Authentication & role switcher
│   │   ├── components/
│   │   │   ├── assistant/                           # Floating Health Assistant
│   │   │   ├── clinical/                            # Safety banner, voice recorder, OCR uploader, timeline
│   │   │   ├── common/                              # Header, footer, navigation, network indicators
│   │   │   └── ui/                                  # Badges, buttons, cards
│   │   ├── lib/                                     # API client, auth provider, offline queue
│   │   └── types/                                   # TypeScript definitions
│   ├── package.json
│   └── Dockerfile
│
├── backend/
│   ├── alembic/                                     # Database schema migrations (Alembic async)
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── cases.py                             # Triage cases CRUD & queue
│   │   │   ├── intake.py                            # Speech, translation & OCR endpoints
│   │   │   ├── review.py                            # Review actions & referral generation
│   │   │   ├── auth.py                              # Authentication & JWT
│   │   │   ├── patients.py                          # EHR patient charts & multi-identifiers
│   │   │   ├── encounters.py                        # Clinical encounters lifecycle & visits
│   │   │   ├── clinical.py                          # Observations/vitals, allergies, meds, notes, diagnoses, referrals
│   │   │   ├── audit.py                             # HIPAA-ready audit logging
│   │   │   ├── documents.py                         # Object storage upload/download & metadata
│   │   │   ├── facilities.py                        # Multi-facility & tenant management
│   │   │   ├── jobs.py                              # Background asynchronous task queue
│   │   │   ├── assistant.py                         # Floating clinical assistant endpoint
│   │   │   └── health.py                            # Liveness & Readiness health probes
│   │   ├── core/                                    # Config, security, dependencies, Redis pool
│   │   ├── models/                                  # 18 Normalized Entities (Facility, User, Patient, Encounter, etc.)
│   │   ├── schemas/                                 # Pydantic request/response models & clinical schemas
│   │   ├── services/                                # Anonymizer, RiskEngine, Speech, OCR, Gemini, Storage, TaskManager
│   │   └── main.py                                  # FastAPI factory, DB lifecycle & synthetic seed data
│   ├── tests/                                       # Automated Pytest suite (66 passing tests)
│   ├── manage.py                                    # Administrative CLI management utility
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                                            # Clinical architecture & phase reports
│   ├── compliance/                                  # Governance & compliance policies
│   ├── DATABASE_ARCHITECTURE.md                     # Comprehensive ER diagram, schemas, lifecycles, and indexes
│   ├── DOCUMENT_ARCHITECTURE.md                     # Medical document security & storage specification
│   ├── OBJECT_STORAGE_ARCHITECTURE.md               # Storage backend, streaming pipeline, HMAC presigned URLs
│   ├── DISASTER_RECOVERY.md                         # Backup/restore protocols and RTO/RPO metrics
│   └── CLEANUP_INSPECTION_REPORT.md                 # Baseline cleanup inspection report
│
├── infrastructure/                                  # Production deployment assets (Nginx, Docker Compose)
├── scripts/                                         # Database backup and verification scripts
├── docker-compose.yml
├── .env.example
├── README.md
├── FEATURES.md
├── INFRASTRUCTURE.md
├── SECURITY.md
├── TESTING.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── API_SPECIFICATION.md
├── clinical-rules.md
├── deploy.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## ⚡ Quickstart Commands (Windows PowerShell)

Clinova AI runs natively on Windows using PowerShell orchestration. No Docker Desktop, WSL, or Linux containers are required for local development.

### 🚀 One-Command Native Windows Startup (Recommended)

Start all local services (PostgreSQL/SQLite, Redis, FastAPI Backend, Next.js Frontend):

```powershell
.\scripts\clinova.ps1 start
```

To automatically launch the frontend in your default browser upon startup:

```powershell
.\scripts\clinova.ps1 start -Open
```

Access the services:
* **Frontend Web App**: [http://localhost:3000](http://localhost:3000)
* **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Backend Root Health**: [http://localhost:8000/health](http://localhost:8000/health)
* **Process Liveness Probe**: [http://localhost:8000/api/v1/health/live](http://localhost:8000/api/v1/health/live)
* **System Readiness Probe**: [http://localhost:8000/api/v1/health/ready](http://localhost:8000/api/v1/health/ready) *(validates PostgreSQL query + Redis ping)*

---

### 🛠️ Developer Lifecycle & Management Commands

| Command | Action |
| :--- | :--- |
| `.\scripts\clinova.ps1 start` | Start all local services in dependency order |
| `.\scripts\clinova.ps1 start -Open` | Start services and open frontend in browser |
| `.\scripts\clinova.ps1 stop` | Gracefully stop all Clinova-managed processes |
| `.\scripts\clinova.ps1 restart` | Stop and restart the local stack |
| `.\scripts\clinova.ps1 status` | Display process PIDs, port availability, and health |
| `.\scripts\clinova.ps1 doctor` | Run comprehensive prerequisite and port diagnostics |
| `.\scripts\clinova.ps1 health` | Probe live health and latency metrics |
| `.\scripts\clinova.ps1 logs` | Inspect backend and frontend log streams |
| `.\scripts\clinova.ps1 setup` | Automated environment setup (venv, pip, npm, .env) |

---

### 📦 Production Deployment (Docker)

For staging/production server deployments with Docker and Nginx, refer to [deploy.md](deploy.md) and [infrastructure/docker/docker-compose.prod.yml](infrastructure/docker/docker-compose.prod.yml).

---

## 🧪 Running Automated Tests

### Backend Pytest Suite (66 Tests — 100% Pass Rate)

Run the full automated test suite:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -v
```

*Test suites cover:*
* **Phase 4 Enterprise Readiness & Scale (6 tests):** Keyset cursor-based pagination encode/decode, Prometheus telemetry metrics collection, bulk CSV patient import preview and execution, bulk FHIR bundle import, patient deduplication & chart merge with provenance tracking, and automated retention sweeps.
* **Phase 3 Medical Documents & Object Storage (13 tests):** Valid PDF/image uploads with SHA-256 integrity, magic byte file signature validation (PDF, PNG, JPEG, TIFF, WEBP, DICOM) and disguised executable/script rejection (`MZ`, `ELF`, shell), path traversal sanitization, anti-malware scanning with unmapped quarantine vault isolation & HTTP 403 blocks, IDOR cross-patient isolation, HMAC-SHA256 presigned access tokens, document versioning & clinical amendment lineage (`POST /{id}/amend`), derived analytical artifacts (`document_artifacts`), soft deletion & retention compliance, zero-buffering 64KB chunked large file streaming (10MB–500MB), cross-facility multi-tenant isolation, anonymous denial, and search/filtering/pagination.
* **Phase 2 Clinical Architecture (11 tests):** Clinical encounters lifecycle, discrete observations/vitals & LOINC verification, allergies & intolerances, medication regimens, diagnoses with AI attribution & clinician verification, clinical notes immutability & amendment audit tracking, referral management, multi-tenancy cross-facility isolation, patient multi-system identifiers & auto-MRN, longitudinal patient timeline aggregation, and synthetic scale benchmark (1,000+ observations < 5ms).
* **Phase 1 Foundation & Security (23 tests):** Anonymization, Aadhaar redaction, Risk engine breathing/cardiovascular rules, Routine presentations, Non-diagnostic triage note synthesis, Consultation lifecycle, EHR patient CRUD, Authentication, IDOR cross-patient isolation (OWASP API1:2023), Health liveness & readiness (PostgreSQL + Redis ping), Multi-facility scoping, Object storage lifecycle & MIME/traversal validation, and Asynchronous background task queues.
* **AI Decision Support & Assistant (5 tests):** Assistant capabilities and preferences, prompt injection defense, medical boundary and emergency escalation enforcement, multilingual support (English, Hindi, Odia), and RBAC tool execution boundaries.
* **Role Workflows & Authorization Matrix (8 tests):** Private endpoints auth enforcement, full 4-role endpoint permission matrix (Admin, Doctor, Nurse, Patient), self-registration staff protection, patient intake review and isolation, EHR chart ID isolation, encounter doctor ownership, and immutable patient notes.

### Frontend TypeScript & Build Verification

```powershell
cd frontend
npx tsc --noEmit
npm run build
```

---

## 🎭 3-Minute Clinical Demonstration Workflow

1. **Landing Page (`/`)**: Notice the prominent amber Non-Diagnostic Disclaimer, feature pillars, and India-wide facility relevance.
2. **Start Intake (`/intake`)**:
   * Review demo consent and proceed.
   * Select **Odia** or **Hindi** as patient language.
   * Click **Start Voice Recording** to demonstrate the 6-state speech capture engine.
   * Click **Load Synthetic CBC Sample** to extract lab report parameters with confidence scores and verification checkboxes.
   * Click **Submit for Qualified Review**.
3. **Reviewer Queue (`/review`)**:
   * Inspect prioritized sorting (`URGENT REVIEW`, `PRIORITY`, `ROUTINE`).
   * Observe transparent rule badges (`TRIAGE-R01`, `TRIAGE-R04`) based on deterministic criteria without black-box scores.
4. **Case Review & Human Gate (`/review/case/[caseId]`)**:
   * Verify the symptom progression timeline (Day 1, Day 2, Day 3).
   * Review the explainable provenance badges.
   * Click **Edit Summary** or **Confirm & Approve Note**.
5. **Referral Support Note (`/review/case/[caseId]/referral`)**:
   * Review the clean, printable referral support document ready for secondary care facility handoff.
   * Click **Print / Save Referral PDF**.
6. **Privacy & Data Purge**:
   * Return to the case review screen and click **Delete Case Data** to verify retention data purging.

---

## 👥 Role-Isolated Dashboard Environments & Credentials

Clinova AI strictly isolates authenticated users into four distinct environments based on verified session roles, ensuring zero feature leakage and independent backend object authorization:

| Environment | Role Claim | Dashboard Route | Pre-Seeded Credentials | Primary Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Patient** | `patient` | `/dashboard/patient` | `patient@clinova.ai` / `ClinovaPatient2026!` | Personal intake submissions, profile management (`/portal/profile`), recorded vitals review, medical document access. Zero staff/doctor controls. |
| **Doctor / Clinician** | `doctor` | `/dashboard/doctor` | `doctor@clinova.ai` / `ClinovaDoctor2026!` | Clinical decision center, priority review queue (`/review`), case inspection with real vitals & AI support, note approval/rejection/referral, EHR directory, consultations. |
| **Staff / Nurse** | `nurse` | `/dashboard/nurse`<br>*(alias: `/dashboard/staff`)* | `staff@clinova.ai` / `ClinovaStaff2026!` | Frontline operational intake, patient registration, identity verification, rapid vitals documentation (BP, HR, SpO2, Temp, RR), departmental physician routing and handoffs. |
| **Admin** | `admin` | `/dashboard/admin` | `admin@clinova.ai` / `ClinovaAdmin2026!` | Institutional governance, user accounts & activation toggles, HIPAA data retention disposal lifecycle sweeps, system health & Prometheus telemetry, immutable audit logs (`/audit`). |

*Direct visits to `/dashboard` automatically route users to their authorized environment. Direct visits to unauthorized routes are rejected by frontend `RoleGuard` and independently defended by backend HTTP 403 API dependencies.*

---

## 🔒 Security & Privacy Controls

* **Anonymization Layer**: Direct personal identifiers (phone numbers, email addresses, 12-digit Aadhaar sequences) are masked with `[PHONE_REMOVED]`, `[EMAIL_REDACTED]`, and `[GOVT_ID_REDACTED]`.
* **Synthetic Identifiers**: Cases use anonymous IDs (`CLV-DEMO-001`).
* **Data Retention Policy**: Audio recordings and report scans are stored in temporary buffers and can be purged via one-click retention controls.
* **Immutable Audit Trail**: All intake events, translations, OCR readings, and reviewer sign-offs are immutably logged with actor, timestamp, and IP address.
