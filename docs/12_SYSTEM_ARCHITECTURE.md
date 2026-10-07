# CLINOVA AI — System Technical Architecture

> **Document ID:** `DOC-12`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Architectural Principles

1. **Separation of Public Showcase and Operational Workspace:** The public clinical technology website (`/`) communicates the philosophy and architectural pillars to evaluators, researchers, and administrators, while dedicated operational routes (`/workspace`, `/intake`, `/cases`, `/reviewer`, `/signalgraph`) provide the production clinical workflows.
2. **Resilience & Local-First Determinism:** The system is engineered to run seamlessly in offline/local environments without requiring external cloud AI APIs. When cloud providers (Gemini, Groq, Sarvam) are configured, they enhance capability; when absent, deterministic clinical rule engines ensure 100% functionality without interruption.
3. **Strict Non-Diagnostic Safety Governance:** Every API response carries non-diagnostic safety headers (`X-Clinical-Safety: Non-Diagnostic-Advisory-Only`, `X-Human-In-The-Loop: Required-Before-Action`).
4. **Clean Decoupling:** Complete separation of concerns between presentation (Next.js 15), backend application services (FastAPI), domain graphs (CareGraph, FacilityGraph, SignalGraph, Orchestration), and persistence (SQLAlchemy async).

---

## 2. High-Level Component Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA AI APPLICATION TOPOLOGY                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ Modern Web Browser / Triage Workstation / Tablet Kiosk ]                │
│                                │                                            │
│                                ▼ (HTTP / HTTPS / WebSocket)                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                 FRONTEND WORKSTATION (Next.js 15)                   │   │
│   │  - App Router / React Server Components + Client Workspaces         │   │
│   │  - Tailwind CSS + Lucide Icons + Radix UI Primitives                │   │
│   │  - Dedicated Roles: Triage Nurse, Clinician Reviewer, Admin, Public │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼ (REST API / JSON / SSE)              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                  BACKEND CORE API (FastAPI Python)                  │   │
│   │  - Async ASGI Runtime (Uvicorn)                                     │   │
│   │  - Pydantic V2 Request/Response Schemas & Input Sanitization        │   │
│   │  - CORS Middleware & Clinical Safety Header Middleware              │   │
│   │  - Structured JSON Logging & Medicolegal Audit Logger               │   │
│   └──────────┬───────────────────────┬───────────────────────┬──────────┘   │
│              │                       │                       │              │
│              ▼                       ▼                       ▼              │
│   ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐   │
│   │   CAREGRAPH CORE    │ │  FACILITYGRAPH CORE │ │  SIGNALGRAPH CORE   │   │
│   │ Trajectory, Vitals, │ │ Capabilities, Beds, │ │ Aggregated Surges,  │   │
│   │ Evidence Provenance │ │ Feasibility Match   │ │ Outbreak Clusters   │   │
│   └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘   │
│              │                       │                       │              │
│              └───────────────────────┼───────────────────────┘              │
│                                      ▼                                      │
│                       ┌─────────────────────────────┐                       │
│                       │    ORCHESTRATION ENGINE     │                       │
│                       │ Multi-Criteria Action FSM   │                       │
│                       └──────────────┬──────────────┘                       │
│                                      │                                      │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    PERSISTENCE & STORAGE LAYER                      │   │
│   │  - Primary DB: SQLite (Local Dev) / PostgreSQL (Production)         │   │
│   │  - Async ORM: SQLAlchemy 2.0 (asyncio + aiosqlite / asyncpg)        │   │
│   │  - Document Vault: Encrypted Local Storage / S3-compatible          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Resilience & Graceful Degradation Architecture

To guarantee high clinical availability in resource-constrained environments, the backend adheres to a three-tier execution hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXECUTION DEGRADATION HIERARCHY                        │
├───────────────────┬─────────────────────────────────┬───────────────────────┤
│ Tier              │ Capabilities Active             │ Triggers              │
├───────────────────┼─────────────────────────────────┼───────────────────────┤
│ **Tier 1: Full**  │ Neural Speech-to-Text (STT)     │ External APIs healthy │
│                   │ Multimodal Vision OCR           │ Internet connected    │
│                   │ Contextual Clinical Q&A LLM     │ Valid API credentials │
├───────────────────┼─────────────────────────────────┼───────────────────────┤
│ **Tier 2: Local** │ Local Tesseract OCR (if inst)   │ External API latency  │
│                   │ Deterministic Rule Follow-ups   │ Cloud rate limits     │
│                   │ Local Regex Entity Extraction   │ External service down │
├───────────────────┼─────────────────────────────────┼───────────────────────┤
│ **Tier 3: Safe**  │ Manual Structured Data Entry    │ Complete offline mode │
│                   │ Hardened Deterministic NEWS2    │ Zero external network │
│                   │ Static Protocol Questionnaires  │ Emergency field triage│
└───────────────────┴─────────────────────────────────┴───────────────────────┘
```

---

## 4. Frontend Component Architecture

```
frontend/src/
├── app/
│   ├── layout.tsx             # Root layout with clinical header & safety banner
│   ├── page.tsx               # Public institutional landing & 4 pillars showcase
│   ├── intake/                # Multimodal patient intake workspace
│   ├── reviewer/              # Clinician Reviewer workstation & CareGraph viewer
│   ├── facilities/            # FacilityGraph network navigation & bed tracker
│   ├── signalgraph/           # System-level operational & surge telemetry
│   └── audit/                 # Medicolegal compliance & event log browser
├── components/
│   ├── ui/                    # Reusable calm, accessible design primitives
│   ├── caregraph/             # Trajectory sparklines, provenance badges, node graph
│   ├── facilitygraph/         # Bed status indicators, feasibility matrix card
│   ├── signalgraph/           # Regional surge maps, queue congestion gauges
│   └── orchestration/         # Action recommendation bar & clinician sign-off modal
├── lib/
│   ├── api.ts                 # Type-safe Fetch client with automatic retry
│   └── utils.ts               # Clinical formatting & class merges
└── types/
    └── index.ts               # TypeScript mirror of Pydantic domain models
```

---

## 5. Security Boundaries

- **CORS Configuration:** Restricted to designated frontend origins (`http://localhost:3000` in dev).
- **Audit Logging:** Every mutating request logs actor ID, IP address, target case ID, and cryptographic timestamp.
- **Header Injection:** Reverse proxies and ASGI middleware inject `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `X-Clinical-Safety`.
