# Contributing to CLINOVA AI

Welcome to the **CLINOVA AI** project! We are thrilled that you are interested in contributing. Whether you are fixing a bug, adding a new feature, improving documentation, or adding test cases, your help is essential in building an accessible, reliable, and clinically grounded triage-support platform.

This guide provides comprehensive, step-by-step instructions to help you set up your local development environment, understand the system architecture, write clean and safe code, run automated tests, and submit high-quality pull requests.

---

## Table of Contents

1. [Overview & Guiding Principles](#1-overview--guiding-principles)
2. [Repository Architecture](#2-repository-architecture)
3. [Prerequisites & Tooling](#3-prerequisites--tooling)
4. [Cloning & Workspace Setup](#4-cloning--workspace-setup)
5. [Environment Variables](#5-environment-variables)
6. [Backend Setup (FastAPI)](#6-backend-setup-fastapi)
7. [Frontend Setup (Next.js)](#7-frontend-setup-nextjs)
8. [Database & Services Setup (Docker)](#8-database--services-setup-docker)
9. [Running the Full Application](#9-running-the-full-application)
10. [Daily Development Workflow](#10-daily-development-workflow)
11. [Branching Strategy](#11-branching-strategy)
12. [Making Safe Code Changes](#12-making-safe-code-changes)
13. [Testing & Quality Assurance](#13-testing--quality-assurance)
14. [Pre-Submission Validation Checklist](#14-pre-submission-validation-checklist)
15. [Common Git Commands Reference](#15-common-git-commands-reference)
16. [Commit Message Guidelines](#16-commit-message-guidelines)
17. [Pull Request (PR) Process](#17-pull-request-pr-process)
18. [Healthcare Safety & Non-Diagnostic Principles](#18-healthcare-safety--non-diagnostic-principles)

---

## 1. Overview & Guiding Principles

**CLINOVA AI** is an explainable, multimodal, human-in-the-loop healthcare triage assistant engineered for government district hospitals, primary health centers (PHCs), public health outreach camps, industrial clinics, and university health centers.

### Core Capabilities
- **Multimodal Intake**: Voice recording (6-state audio capture), typed symptom narratives, and CBC lab report uploads.
- **Regional Language Normalization**: Preserves vernacular patient inputs (**Odia**, **Hindi**) while generating structured English representations for attending medical officers.
- **Deterministic Risk Signal Engine**: Transparent, explainable rule checks (`TRIAGE-R01` through `TRIAGE-R06`) that flag acute respiratory, cardiovascular, hemorrhage, neurological, or infectious distress.
- **Report OCR Parameter Parsing**: Extracts Complete Blood Count (CBC) parameters with field-level confidence scores and clinician verification checkboxes.
- **Human-in-the-Loop Review Gate**: Review dashboard where qualified clinicians confirm, edit, reject, or escalate AI-generated notes.
- **Referral Note Generation**: Instant creation of printable, standardized clinical referral notes for secondary or tertiary care transfer.
- **Privacy by Design**: In-flight PII masking (phone numbers, email addresses, 12-digit government IDs like Aadhaar), short retention buffers, and one-click data purge.
- **Zero-Dependency Demo Fallback**: Functions 100% offline out-of-the-box using local mock services (`DEMO_MODE=True`) without requiring external cloud API keys.

---

## 2. Repository Architecture

The project is structured as an integrated monorepo containing a FastAPI backend, a Next.js frontend, Docker Compose orchestration, and an automated test suite.

```text
CLINOVA-AI/
├── .env.example              # Root environment template
├── .gitignore                # Git ignore patterns (Node, Python, Next.js, env)
├── README.md                 # Project executive summary and quickstart
├── FEATURES.md               # Multimodal intake & clinical triage feature specifications
├── INFRASTRUCTURE.md         # Systems topology, Docker, PM2 & hardware profiles
├── SECURITY.md               # DISHA/ABDM healthcare security, PII & audit policy
├── TESTING.md                # Pytest QA handbook & clinical safety regression suite
├── ROADMAP.md                # Strategic clinical informatics roadmap (2026-2027)
├── ARCHITECTURE.md           # Central technical architecture specification
├── clinical-rules.md         # Deterministic clinical rules & triage thresholds
├── API_SPECIFICATION.md      # Authoritative REST API endpoint specification
├── deploy.md                 # Production deployment & operations manual
├── CONTRIBUTING.md           # This contributor handbook
├── scripts/
│   ├── clinova.ps1           # Master native Windows PowerShell orchestrator (start, stop, doctor)
│   ├── backup_db.ps1         # Automated database backup utility
│   └── verify_restore.ps1    # Backup restore and integrity verification
├── docker-compose.yml        # Local Docker Compose deprecated (use infrastructure/docker/ for prod)
│
├── backend/                  # FastAPI Application Service
│   ├── app/
│   │   ├── api/v1/           # Version 1 API routers
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py         # Service readiness & health probes
│   │   │   │   ├── auth.py           # JWT authentication & user login
│   │   │   │   ├── patients.py       # EHR Patient chart records
│   │   │   │   ├── consultations.py  # Clinical encounter records
│   │   │   │   ├── cases.py          # Triage case queue & status management
│   │   │   │   ├── intake.py         # Speech-to-text, translation, and OCR
│   │   │   │   ├── review.py         # Medical officer sign-off & referral notes
│   │   │   │   ├── ai_assist.py      # Clinical summary & differential support
│   │   │   │   └── audit.py          # Immutable audit trail queries
│   │   │   └── api.py                # Router aggregator
│   │   ├── core/             # Configuration settings, security, and dependencies
│   │   │   ├── config.py             # Pydantic BaseSettings & env loader
│   │   │   ├── security.py           # Bcrypt password hashing & JWT tokens
│   │   │   └── deps.py               # Authentication & DB session dependencies
│   │   ├── db/               # Database engine & session management
│   │   │   ├── base.py               # Declarative SQLAlchemy base
│   │   │   └── session.py            # Async engine & session factory
│   │   ├── models/           # SQLAlchemy ORM database models
│   │   │   ├── user.py               # User and UserRole (Doctor, Nurse, Patient, Admin)
│   │   │   ├── patient.py            # EHR Patient demographics and records
│   │   │   ├── consultation.py       # Clinical consultations and vitals
│   │   │   ├── case.py               # TriageCase, queue category, timeline, lab data
│   │   │   └── audit_log.py          # Immutable audit log entries
│   │   ├── schemas/          # Pydantic validation request/response schemas
│   │   ├── services/         # Business logic and external service adapters
│   │   │   ├── anonymizer.py         # PII masking (phones, emails, IDs)
│   │   │   ├── risk_engine.py        # Deterministic triage rules (TRIAGE-R01 to R06)
│   │   │   ├── speech_service.py     # Multilingual voice transcription & Odia/Hindi audio
│   │   │   ├── translation_service.py# Regional language normalization
│   │   │   ├── ocr_service.py        # CBC report parameter extraction
│   │   │   └── ai/
│   │   │       └── gemini_service.py # Gemini API integration with mock fallback
│   │   └── main.py           # FastAPI factory, lifespan, CORS, and demo seed data
│   ├── tests/                # Automated pytest suite
│   │   ├── conftest.py               # Async test client & authentication fixtures
│   │   ├── test_health.py            # Health check tests
│   │   ├── test_auth.py              # Login and token tests
│   │   ├── test_patients.py          # EHR patient management tests
│   │   ├── test_consultations.py     # Consultation workflow tests
│   │   ├── test_risk_engine.py       # Triage rule engine tests (R01 - R06)
│   │   ├── test_ai.py                # Anonymization & AI triage synthesis tests
│   │   └── test_audit.py             # Audit log generation tests
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container build for backend
│
└── frontend/                 # Next.js 14 Web Application
    ├── src/
    │   ├── app/              # Next.js App Router pages
    │   │   ├── page.tsx                      # Landing page with clinical disclaimer
    │   │   ├── layout.tsx                    # Root layout with header and footer
    │   │   ├── intake/page.tsx               # 4-step Multimodal Intake Wizard
    │   │   ├── review/page.tsx               # Prioritized Reviewer Queue
    │   │   ├── review/case/[caseId]/page.tsx # Case Review & Clinician Gate
    │   │   ├── review/case/[caseId]/referral/page.tsx # Printable Referral Note
    │   │   ├── demo/page.tsx                 # 6 Public Health Demo Scenarios
    │   │   ├── dashboard/page.tsx            # Clinical metrics & analytics
    │   │   ├── patients/page.tsx             # Patient registry
    │   │   ├── consultations/page.tsx        # Consultation history
    │   │   ├── audit/page.tsx                # Compliance audit log viewer
    │   │   ├── login/page.tsx                # Clinician authentication
    │   │   └── register/page.tsx             # New account registration
    │   ├── components/
    │   │   ├── clinical/                     # Specialized healthcare widgets
    │   │   │   ├── disclaimer.tsx            # Mandatory amber safety warning banner
    │   │   │   ├── voice-recorder.tsx        # 6-state speech capture component
    │   │   │   ├── report-uploader.tsx       # Lab report OCR viewer & verification
    │   │   │   ├── timeline-view.tsx         # Chronological symptom trajectory
    │   │   │   └── provenance-badge.tsx      # Transparent rule attribution badge
    │   │   ├── common/                       # Header, footer, navbar
    │   │   └── ui/                           # Badges, buttons, cards, modals
    │   ├── lib/              # API fetch client, token management, auth context
    │   └── types/            # TypeScript interfaces and clinical data models
    ├── package.json          # Node dependencies and scripts
    ├── tsconfig.json         # TypeScript compiler configuration
    ├── tailwind.config.ts    # Tailwind CSS design system tokens
    └── Dockerfile            # Container build for frontend
```

---

## 3. Prerequisites & Tooling

Ensure the following tools are installed on your machine before setting up the project:

| Tool | Recommended Version | Purpose | Verification Command |
| :--- | :--- | :--- | :--- |
| **Git** | 2.38+ | Version control | `git --version` |
| **Python** | 3.11, 3.12, or 3.14 | FastAPI backend runtime | `python --version` |
| **Node.js** | 18 LTS or 20 LTS | Next.js frontend runtime | `node --version` |
| **npm** | 9+ or 10+ | Frontend package manager | `npm --version` |
| **Docker** | 24+ | Container runtime (optional for local run) | `docker --version` |
| **Docker Compose** | 2.20+ | Multi-service orchestration | `docker compose version` |

> [!NOTE]
> Windows users should run all terminal commands inside **PowerShell** or **Git Bash**. Avoid older `cmd.exe` where script execution syntax differs.

---

## 4. Cloning & Workspace Setup

Clone the repository and open the workspace in your code editor:

### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/Samir-hub12345/CLINOVA-AI.git

# Navigate into the project root
cd CLINOVA-AI
```

### macOS / Linux (Bash or Zsh)
```bash
# Clone the repository
git clone https://github.com/Samir-hub12345/CLINOVA-AI.git

# Navigate into the project root
cd CLINOVA-AI
```

---

## 5. Environment Variables

Clinova AI provides a pre-configured `.env.example` template at the root of the repository.

### Initializing Environment Files
Copy `.env.example` to create `.env` in the root directory:

#### Windows PowerShell
```powershell
Copy-Item .env.example .env
```

#### macOS / Linux
```bash
cp .env.example .env
```

### Configuration Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `BACKEND_PORT` | `8000` | Port on which the FastAPI application listens. |
| `FRONTEND_PORT` | `3000` | Port on which the Next.js development server runs. |
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `production`, `test`). |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/clinova` | Asynchronous connection string for PostgreSQL. (When running full Docker Compose, use `db:5432`). |
| `REDIS_URL` | `redis://localhost:6379/0` | Connection string for Redis cache. (When running full Docker Compose, use `redis:6379/0`). |
| `SECRET_KEY` | `change-this-in-production...` | Secret key used for signing HS256 JWT tokens. |
| `GEMINI_API_KEY` | `your-gemini-api-key-here` | *(Optional)* Google Gemini API key. If left blank, Clinova AI seamlessly uses local deterministic mock models. |
| `NEXT_PUBLIC_API_URL`| `http://localhost:8000` | Base API URL called by the browser frontend. |

> [!IMPORTANT]
> Never commit real secrets or API keys to version control. The `.gitignore` file is configured to ignore all `.env*` local files.

---

## 6. Backend Setup (FastAPI)

The backend provides the RESTful API, database models, deterministic risk scoring, and triage note generation.

### 1. Navigate to the backend directory
```powershell
cd backend
```

### 2. Create a Python Virtual Environment
```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(If PowerShell gives a script execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Windows (Command Prompt)**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Launch the FastAPI Development Server
```powershell
uvicorn app.main:app --reload --port 8000
```

### 6. Verify Backend Health
Open your browser or run curl to test the endpoints:
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Root Welcome Endpoint**: [http://localhost:8000/](http://localhost:8000/)

> [!TIP]
> On startup, the backend `lifespan` handler automatically initializes all database tables via SQLAlchemy metadata and seeds initial demo users, patients, and 6 synthetic public health triage cases (`CLV-DEMO-001` through `CLV-DEMO-006`).

---

## 7. Frontend Setup (Next.js)

The frontend is a responsive Next.js 14 application written in TypeScript and styled with Tailwind CSS.

### 1. Open a new terminal and navigate to the frontend directory
```powershell
cd frontend
```

### 2. Install Node Dependencies
```powershell
npm install
```

### 3. Start the Next.js Development Server
```powershell
npm run dev
```

### 4. Access the Web Application
Open your browser and visit:
- **Web App**: [http://localhost:3000](http://localhost:3000)
- **Public Health Demo Scenarios**: [http://localhost:3000/demo](http://localhost:3000/demo)
- **Patient Intake Wizard**: [http://localhost:3000/intake](http://localhost:3000/intake)
- **Reviewer Queue**: [http://localhost:3000/review](http://localhost:3000/review)

### Available Frontend Scripts
- `npm run dev` — Starts local development server with Hot Module Replacement on port 3000.
- `npm run build` — Compiles and optimizes the application for production.
- `npm run start` — Starts a production server after building.
- `npm run lint` — Runs Next.js ESLint checks.

---

## 8. Native Windows Orchestration & Local Stack

Clinova AI runs natively on Windows using PowerShell orchestration.

### One-Command Local Startup (Recommended)

Start the entire local development stack (Backend + Frontend + PostgreSQL/SQLite + Redis) with a single PowerShell command:

```powershell
# From the project root
.\scripts\clinova.ps1 start
```

Or start and automatically open the application in your default browser:
```powershell
.\scripts\clinova.ps1 start -Open
```

- **PostgreSQL**: Bound to `localhost:5432` (or zero-install SQLite fallback via `DATABASE_URL`)
- **Redis**: Bound to `localhost:6379` (or graceful in-memory fallback)
- **FastAPI Backend**: Bound to `http://localhost:8000` (Swagger docs: `/docs`)
- **Next.js Frontend**: Bound to `http://localhost:3000`

To inspect running services, ports, and health status:
```powershell
.\scripts\clinova.ps1 status
```

To view live application logs:
```powershell
.\scripts\clinova.ps1 logs
```

To stop all services:
```powershell
.\scripts\clinova.ps1 stop
```

---

## 9. Developer Commands Reference

| Task | Command | Description |
| :--- | :--- | :--- |
| **First-Time Setup** | `.\scripts\clinova.ps1 setup` | Prepares Python `.venv`, installs requirements, and sets up `.env` |
| **Start Stack** | `.\scripts\clinova.ps1 start` | Starts all services in dependency order |
| **Stop Stack** | `.\scripts\clinova.ps1 stop` | Gracefully stops all Clinova processes |
| **Restart Stack** | `.\scripts\clinova.ps1 restart` | Cleanly restarts all services |
| **Inspect Status** | `.\scripts\clinova.ps1 status` | Displays process PIDs and port listeners |
| **System Diagnostics** | `.\scripts\clinova.ps1 doctor` | Diagnoses missing tools, ports, and configuration |
| **Health Probe** | `.\scripts\clinova.ps1 health` | Evaluates backend readiness and component latencies |

---

## 10. Daily Development Workflow

When contributing a feature or bug fix, follow this typical daily routine:

1. **Pull Latest Changes**:
   ```powershell
   git checkout main
   git pull origin main
   ```
2. **Start Clinova Stack**:
   ```powershell
   .\scripts\clinova.ps1 start
   ```
3. **Develop and Test**: Make code changes; frontend features hot-reload in Next.js, and backend updates apply via Uvicorn.
4. **Execute Automated Tests**: Run pytest and linting before staging changes:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest backend/tests -v
   ```
5. **Stop Stack When Done**:
   ```powershell
   .\scripts\clinova.ps1 stop
   ```

---

## 11. Branching Strategy

We follow a simple, organized branching convention based on GitHub Flow:

- `main` is our production-ready, stable branch. Direct commits to `main` are prohibited.
- Always create a descriptive branch off of the latest `main`:

| Branch Prefix | Usage | Example |
| :--- | :--- | :--- |
| `feature/` | New clinical features, endpoints, or UI screens | `feature/intake-audio-waveform` |
| `fix/` | Bug fixes and correction of errors | `fix/r02-cardiac-flag-boundary` |
| `docs/` | Documentation additions or edits | `docs/contributing-guidelines` |
| `refactor/` | Code refactoring without changing behavior | `refactor/anonymizer-regex` |
| `test/` | Adding or updating unit tests | `test/intake-endpoint-coverage` |

### Creating a New Branch
```powershell
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

---

## 12. Making Safe Code Changes

### Backend Guidelines (FastAPI & Python)
1. **Type Annotations**: Always use standard Python 3.10+ type hints (`str`, `int | None`, `list[dict]`, etc.).
2. **Pydantic Validation**: All API request bodies and responses must declare explicit Pydantic v2 schemas in `backend/app/schemas/`.
3. **SQLAlchemy 2.0 Async**: Always use modern asynchronous SQLAlchemy syntax (`select(Model).where(...)`, `await db.execute(...)`, `await db.commit()`). Avoid legacy `query.get()` patterns.
4. **Error Handling**: Raise standard FastAPI `HTTPException` with informative error detail rather than unhandled Python exceptions.
5. **No Secrets in Code**: Never hardcode credentials, passwords, or API keys in code. Use `backend/app/core/config.py`.

### Frontend Guidelines (Next.js & TypeScript)
1. **Strict TypeScript**: Avoid `any`. Define clean interfaces in `src/types/` for all clinical data structures.
2. **Clinical Safety Banner**: Any new clinical review screen must import and display `<SafetyDisclaimer />` from `src/components/clinical/disclaimer.tsx`.
3. **Responsive Design**: Ensure mobile, tablet, and desktop layouts render cleanly using Tailwind utility classes (`sm:`, `md:`, `lg:`).
4. **Accessibility (a11y)**: Provide semantic HTML tags, accessible form labels, and appropriate `aria-*` attributes for screen readers.

### Privacy & Data Safety Guidelines
- **PII Scrubbing**: Any user-entered free text must pass through `anonymize_text` from `backend/app/services/anonymizer.py` before being stored or processed by an LLM.
- **Synthetic Data**: Use only synthetic identifiers (`CLV-DEMO-xxx`) and synthetic patient names for demonstrations and tests. Never import or use real patient health information (PHI).

---

## 13. Testing & Quality Assurance

All PRs must maintain or improve test coverage. 

### Running Backend Pytest Suite

#### When running in local virtual environment:
```powershell
# From the backend directory with virtualenv active
pytest -v
```

#### When running via Docker Compose:
```powershell
# From the project root
docker compose exec backend pytest -v
```

### Current Test Coverage (15 Passing Tests)
- `test_health.py`: Verifies `/api/v1/health` and database connectivity status.
- `test_auth.py`: Tests user registration, doctor/patient login, and JWT access tokens.
- `test_patients.py`: Verifies EHR patient record creation, fetching, and search.
- `test_consultations.py`: Tests patient-doctor encounter recording and triage leveling.
- `test_risk_engine.py`: Rigorously tests deterministic triage rules `TRIAGE-R01` through `TRIAGE-R06`:
  - `TRIAGE-R01`: Severe respiratory distress trigger.
  - `TRIAGE-R02`: Acute cardiac chest pain trigger.
  - `TRIAGE-R03`: Severe acute hemorrhage trigger.
  - `TRIAGE-R04`: Neurological sudden deficit trigger.
  - `TRIAGE-R05`: High sustained fever / infectious outbreak flag.
  - `TRIAGE-R06`: Routine non-urgent clinical presentation.
- `test_ai.py`: Tests PII anonymization (masking Indian phone numbers, emails, and 12-digit Aadhaar patterns) and non-diagnostic summary generation.
- `test_audit.py`: Confirms immutable audit records are written on clinical operations.

### Running Frontend Checks & Linters
```powershell
# From the frontend directory
npm run lint

# Build test (ensures no TypeScript compile errors)
npm run build
```

---

## 14. Pre-Submission Validation Checklist

Before submitting a Pull Request, verify each item on this checklist:

- [ ] **Tests Passing**: Ran `pytest -v` and all 15+ backend tests pass with zero failures.
- [ ] **Frontend Builds**: Ran `npm run build` inside `frontend/` without any TypeScript or bundling errors.
- [ ] **Linting Clean**: Ran `npm run lint` inside `frontend/` with no unresolved errors.
- [ ] **Safety Disclaimer Intact**: The mandatory amber non-diagnostic warning banner remains visible on all patient-facing and clinician-facing review pages.
- [ ] **PII Anonymization Preserved**: Any new symptom input pipeline invokes the anonymizer service before processing.
- [ ] **No Secrets Committed**: Checked `git diff` to ensure no API keys, private passwords, or personal credentials are included.
- [ ] **Deterministic Fallback Functional**: App works without crashing when `GEMINI_API_KEY` is omitted (`DEMO_MODE=True`).
- [ ] **Clean Git History**: Commits are structured logically with clear Conventional Commit messages.

---

## 15. Common Git Commands Reference

A quick reference of essential Git commands for contributors:

```powershell
# Check current status and modified files
git status

# Switch to a new feature branch
git checkout -b feature/my-feature

# Stage specific modified files
git add backend/app/services/risk_engine.py

# Stage all tracked changes
git add .

# Commit staged changes with message
git commit -m "feat(risk): add pediatric respiratory threshold rule"

# View recent commit log
git log --oneline -n 5

# Pull latest main changes into your branch
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main

# Push branch to remote repository
git push -u origin feature/my-feature
```

---

## 16. Commit Message Guidelines

We enforce the **Conventional Commits** specification. This maintains a readable changelog and clear git history.

### Commit Format
```text
<type>(<scope>): <short description in imperative mood>

[optional longer body explaining WHY the change was made]

[optional issue reference, e.g., Closes #42]
```

### Commit Types
- `feat`: A new user-facing feature or API endpoint.
- `fix`: A bug fix or correction of faulty logic.
- `docs`: Documentation updates or additions.
- `test`: Adding new unit tests or updating existing tests.
- `refactor`: Code restructuring without modifying behavior or public APIs.
- `style`: Formatting, missing semicolons, white-space cleanup.
- `chore`: Dependency updates, tooling configuration, or build adjustments.

### Examples of Great Commit Messages
- `feat(intake): add Odia language voice recording sample playback`
- `fix(ocr): handle comma separators in platelet count extraction`
- `test(risk): add unit test for TRIAGE-R03 hemorrhage detection`
- `docs(contributing): clarify Docker Compose setup commands for Windows`
- `refactor(anonymizer): streamline Aadhaar 12-digit regex matching`

---

## 17. Pull Request (PR) Process

1. **Push your branch to GitHub**:
   ```powershell
   git push -u origin feature/your-feature-name
   ```
2. **Open a Pull Request**:
   - Navigate to the repository on GitHub: `https://github.com/Samir-hub12345/CLINOVA-AI`.
   - Click the green **Compare & pull request** button.
3. **Complete the PR Template**:
   - **Title**: Use the Conventional Commit format (e.g., `feat(ui): add printable referral summary`).
   - **Summary**: Describe what changed and why.
   - **Testing Done**: List exact commands run (`pytest -v`, `npm run build`) and manual verification steps.
   - **Screenshots / Recordings**: If you modified UI components, include before/after screenshots.
4. **Code Review & Feedback**:
   - Maintainers will review your PR for architecture fit, clinical safety adherence, code cleanliness, and test coverage.
   - Address any reviewer comments by pushing updates to your branch.
5. **Merge**:
   - Once approved and CI checks pass, a maintainer will squash and merge your PR into `main`.

---

## 18. Healthcare Safety & Non-Diagnostic Principles

All contributors must uphold the core clinical safety tenets of Clinova AI:

> [!WARNING]
> ### 🔒 Non-Negotiable Clinical Safety Principles
> 1. **Non-Diagnostic Assistance Only**: Clinova AI is an educational prototype and administrative triage-support system. It does **not** diagnose diseases, prescribe pharmaceuticals, or make autonomous medical judgments.
> 2. **Human-in-the-Loop Gate**: AI outputs (summaries, timelines, risk signals) are always presented as *proposals for clinician review*. No automated medical action may bypass the attending medical officer.
> 3. **Explainable Deterministic Rules**: Risk categories (`URGENT REVIEW`, `PRIORITY`, `ROUTINE`) are driven by deterministic, audited logic (`TRIAGE-R01` to `TRIAGE-R06`) with transparent provenance tags—never opaque black-box probability scores.
> 4. **Persistent Safety Disclaimers**: The standard amber disclaimer banner must never be hidden, dismissed permanently, or removed from clinical user interfaces:
>    > *"Educational prototype and triage-support purposes only. This system does not diagnose, prescribe treatment, or replace a qualified healthcare professional. All AI-generated information requires human review before clinical action."*
> 5. **Privacy and Synthetic Data**: Never use or commit real patient health information (PHI) or personally identifiable information (PII). All automated tests, sample reports, and demo scenarios must use synthetic records.

---

### Need Help?
- **Issue Tracker**: Found a bug or have a feature proposal? Open an issue on GitHub.
- **Code of Conduct**: Treat all contributors and community members with empathy, respect, and professionalism.

Thank you for contributing to **CLINOVA AI**! Together, we can make clinical triage safer, faster, and more accessible for healthcare facilities worldwide.
