# CLINOVA AI

**Continuous Care Intelligence System for Institutional Healthcare Facilities**

---

> [!WARNING]
> ### 🔒 Mandatory Clinical Safety & Non-Diagnostic Disclaimer
> **Educational prototype and clinical decision-support purposes only.** This system does **not** diagnose, prescribe therapeutic regimens, or replace a licensed medical practitioner. All recommendations strictly require verification by a qualified healthcare professional before clinical or administrative action.

---

## 📋 Executive Overview

**CLINOVA AI** represents a structural evolution in clinical decision support:

$$\text{From Isolated Triage} \longrightarrow \text{To Continuous Care Intelligence}$$

In high-volume public hospitals, rural Primary Health Centers (PHCs), and community clinics, isolated single-shot triage fails to capture evolving patient trajectories, resource feasibility constraints, or systemic operational pressures. 

CLINOVA AI synthesizes patient clinical trajectory, facility operational capacity, and epidemiological signals to recommend the **safest achievable next care action** under continuous qualified human supervision.

---

## 🏛️ Core Architectural Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA AI FOUNDATION ARCHITECTURE                    │
│                 FROM ISOLATED TRIAGE → CONTINUOUS CARE INTELLIGENCE         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────┐                    ┌──────────────────────────┐  │
│  │       CAREGRAPH       │                    │      FACILITYGRAPH       │  │
│  │ Patient Clinical State│                    │ Healthcare Capability &  │  │
│  │ Longitudinal Context  │                    │ Live Care Feasibility    │  │
│  └───────────┬───────────┘                    └────────────┬─────────────┘  │
│              │                                             │                │
│              └──────────────────────┬──────────────────────┘                │
│                                     ▼                                       │
│                       ┌───────────────────────────┐                         │
│                       │   ORCHESTRATION ENGINE    │                         │
│                       │ Safest Achievable Action  │                         │
│                       │ Human-in-the-Loop Review  │                         │
│                       └─────────────┬─────────────┘                         │
│                                     ▲                                       │
│              ┌──────────────────────┴──────────────────────┐                │
│              │                                             │                │
│  ┌───────────┴───────────┐                    ┌────────────┴─────────────┐  │
│  │      SIGNALGRAPH      │                    │      BPUT BASELINE       │  │
│  │ Aggregated Signals &  │                    │ Intake, Voice, OCR,      │  │
│  │ Operational Trends    │                    │ Translation, Reviewer    │  │
│  └───────────────────────┘                    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **CAREGRAPH (`backend/app/domain/caregraph/`):**
   - Models patient-level clinical state, temporal progression, and evidence uncertainty.
   - Preserves non-diagnostic posture: tracks observations and findings without asserting definitive pathology.
2. **FACILITYGRAPH (`backend/app/domain/facilitygraph/`):**
   - Models health facility capabilities (emergency resuscitation, ICU beds, oxygen, surgical suites).
   - Validates care feasibility: determines if an indicated intervention can actually be performed locally.
3. **SIGNALGRAPH (`backend/app/domain/signalgraph/`):**
   - Aggregates de-identified, synthetic epidemiological signals and queue backlog telemetry across the network.
   - Contextualizes patient presentations during seasonal disease outbreaks and casualty surges.
4. **ORCHESTRATION ENGINE (`backend/app/domain/orchestration/`):**
   - Synthesizes patient state, uncertainty, facility constraints, and system signals to recommend the safest achievable care handoff.
   - Enforces deterministic red-flag overrides (`TRIAGE-R01` to `TRIAGE-R06`).

---

## ⚙️ Mandatory Baseline Operational Capabilities

CLINOVA AI integrates all required baseline features into its continuous architecture:
- **Multimodal Ingestion:** Text symptom narratives, voice audio capture, and medical report document extraction (e.g. CBC panels via OCR).
- **Linguistic Support:** Multilingual normalization for Odia, Hindi, and English.
- **Explainable Prioritization:** Deterministic urgency flags, uncertainty quantification, and queue prioritization.
- **Reviewer Workspace:** One-screen clinician review dashboard with provenance inspection and digital sign-off.
- **Privacy & Governance:** Automated PII scrubbing, synthetic identifiers, minimal 24-hour retention, and immutable audit logs.

---

## 🗂️ Clean Repository Structure

```
CLINOVA-AI/
├── .github/                      # CI/CD automation workflows
├── backend/
│   ├── app/
│   │   ├── api/v1/router.py      # Foundation system & safety discovery endpoints
│   │   ├── baseline/             # Operational adapters (intake, extraction, review)
│   │   ├── core/                 # Clean settings & logging configuration
│   │   ├── db/                   # Async SQLAlchemy engine & DeclarativeBase
│   │   ├── domain/               # Core pillars: CareGraph, FacilityGraph, SignalGraph, Orchestration
│   │   └── main.py               # Clean FastAPI entrypoint with safety middleware
│   ├── tests/                    # Foundation verification test suite
│   ├── pytest.ini                # Pytest configuration
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── public/branding/          # Retained visual identity & brand marks
│   ├── src/
│   │   ├── app/                  # App Router shell (layout.tsx, page.tsx, globals.css)
│   │   ├── components/           # Common components (Header, Footer, SafetyBanner, UI)
│   │   ├── lib/                  # Utilities (clsx, twMerge)
│   │   └── types/                # Domain TypeScript contracts
│   ├── package.json              # Next.js 15, React 18, Tailwind CSS
│   └── tsconfig.json             # TypeScript configuration
├── docs/
│   ├── architecture/             # Pillar specifications (CareGraph, FacilityGraph, etc.)
│   ├── baseline/                 # Operational requirements & clinical safety rules
│   ├── compliance/               # Human-in-the-loop & privacy specifications
│   ├── roadmap/                  # Phased implementation plan
│   └── archive/                  # Documented archive of legacy phase reports and specs
├── scripts/
│   ├── clinova.ps1               # Native Windows developer orchestrator
│   ├── backup_db.ps1             # Database backup script
│   └── verify_restore.ps1        # Database restore verification script
├── .env.example                  # Clean environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project overview and architectural manual
```

---

## 🚀 Quick Start (Native Windows)

### 1. Requirements
- Python 3.12+ (or 3.14)
- Node.js 20+ & npm
- PowerShell 7+ or Windows PowerShell 5.1

### 2. Environment Configuration
Copy the clean template:
```powershell
Copy-Item .env.example .env
```

### 3. Verify Foundation Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_foundation.py -v
```

### 4. Verify Frontend Typecheck
```powershell
cd frontend
npm run typecheck
```

---

## ⚖️ Legal & Medical Disclaimer

CLINOVA AI is an educational clinical decision-support prototype. It does not provide medical diagnoses, treatment advice, or autonomous patient disposition. Any simulated or real use must be conducted under the direct supervision of licensed medical practitioners.
