# CLINOVA AI — High-Level System Architecture Specification

> **Document ID:** `RES-135`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Distributed Systems Engineering Group  

---

## 1. Architectural Topology Overview

CLINOVA AI is architected as an **Offline-First, Edge-Capable Modular Monolith** designed for continuous healthcare intelligence across resource-constrained clinical settings. The system completely decouples user-facing presentation, deterministic clinical safety enforcement, persistent event state, and statistical AI inferences into clear architectural tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HIGH-LEVEL SYSTEM TOPOLOGY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: CLIENT LAYER ]                                                   │
│  ├── Patient Intake Web / Tablet App (Next.js / React 19 Client Components) │
│  ├── Nurse Triage Workstation (Next.js Server & Client Components)          │
│  └── Doctor Reviewer Workbench (Next.js Server-Rendered Shell + Dynamic)    │
│                                  │                                          │
│                                  │ HTTP / JSON / WebSocket (Local LAN)      │
│                                  ▼                                          │
│  [ TIER 2: API GATEWAY & REVERSE PROXY ]                                    │
│  ├── Nginx / Uvicorn ASGI Server                                            │
│  ├── Rate Limiting & Request Normalization                                  │
│  ├── Authentication & Session Validation (JWT / Supabase Auth)              │
│  └── Non-Diagnostic Clinical Safety Header Middleware                       │
│                                  │                                          │
│                                  │ Dependency Injection                     │
│                                  ▼                                          │
│  [ TIER 3: DOMAIN SERVICES & CLINICAL ENGINE ]                              │
│  ├── Master Case Lifecycle & State Machine Engine (27 States)               │
│  ├── Deterministic Clinical Safety Services (NEWS2, Shock Index, Red Flags) │
│  ├── CAREGRAPH Dynamic Projection Engine (Vitals, Trajectory, Uncertainty)  │
│  ├── FACILITYGRAPH Resource & Freshness Evaluator                           │
│  ├── Multi-Graph Orchestration Engine (Advisory Action Synthesis)           │
│  └── Provenance & Conflict Adjudication Service                             │
│                  │                               │                          │
│                  │ Internal Async Bus            │ Data Mapping             │
│                  ▼                               ▼                          │
│  [ TIER 4: AI & PERCEPTUAL ADAPTERS ]     [ TIER 5: PERSISTENCE LAYER ]     │
│  ├── Local SLM Runtime (Qwen3-4B via      ├── Dual Relational Engine:        │
│  │   Ollama / llama.cpp REST)             │   • Edge: SQLite 3.45+ (WAL)    │
│  ├── Acoustic Pipeline (faster-whisper)   │   • Cloud: PostgreSQL 15+       │
│  ├── Optical Pipeline (PaddleOCR/Tess)    ├── Append-Only Event Ledger      │
│  └── Regional Translation Engine          └── Cryptographic Merkle Chain    │
│                  │                               │                          │
│                  └───────────────┬───────────────┘                          │
│                                  ▼                                          │
│  [ TIER 6: STORAGE & AUDIT ARCHIVE ]                                        │
│  ├── File System / Object Storage (Media Binaries: WAV, JPEG, PDF)          │
│  ├── Offline Sync Journal Manager (Bi-directional Delta Synchronization)    │
│  └── Legal Audit Ledger (Section 63 BSA 2023 Forensic Hash Chain)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier-by-Tier Architectural Breakdown

### 2.1 Tier 1: Client Layer (Presentation & Capture)
- **Technology:** Next.js (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Leaflet.js.
- **Responsibilities:**
  - Rendering responsive, ergonomic user interfaces tailored to user roles (Intake, Triage, Review).
  - Capturing raw multimodal inputs: vernacular audio via browser MediaStream API, document images via HTML5 Canvas/File API, typed symptom text.
  - Providing client-side validation for form constraints (ranges, non-empty fields).
  - Transient offline caching via browser IndexedDB and Cache API for draft persistence during brief network blips.
  - Side-by-side visualization of clinical facts with visual bounding boxes $[0, 1000]^2$ and audio playback segments.
- **Strict Boundary Enforcements:**
  - **Zero Security Decisions:** The client never authorizes state transitions or overrides permissions.
  - **Zero Clinical Safety Calculations:** Physiological risk bands, early warning scores, and triage classifications are NEVER computed exclusively on the client.

### 2.2 Tier 2: API Gateway & Reverse Proxy
- **Technology:** Nginx (Edge/Production) + FastAPI (Uvicorn ASGI).
- **Responsibilities:**
  - Request routing, TLS termination (HTTPS/WSS), and CORS header enforcement.
  - Session authentication: Validating JWT claims and extracting `actor_id`, `actor_role`, and `facility_id`.
  - Global Safety Middleware: Injects mandatory non-diagnostic headers:
    - `X-Clinical-Safety: Non-Diagnostic-Advisory-Only`
    - `X-Human-In-The-Loop: Required-Before-Action`
  - Request logging and correlation tracing via `X-Request-ID` (UUIDv4).

### 2.3 Tier 3: Domain Services & Clinical Engine Layer
- **Technology:** Python 3.11+ Async Modular Monolith Services.
- **Responsibilities:**
  - **Master Case Management:** State transitions across all 27 canonical states, enforced via Optimistic Concurrency Control (`state_version`).
  - **Deterministic Safety Engine:** Pure, deterministic algorithms evaluating vital sign abnormalities, Shock Index ($\text{HR} / \text{SBP}$), NEWS2 scores, pediatric triage bands, and clinical red flags.
  - **CAREGRAPH Service:** Computes physiological risk, longitudinal trajectory slope ($\Delta \text{Vitals} / \Delta t$), and epistemic uncertainty ($U_t$) over time.
  - **FACILITYGRAPH Service:** Evaluates operational capabilities, bed capacity, and telemetry freshness.
  - **Orchestration Service:** Synthesizes patient need and facility capability into advisory candidate actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`).
  - **Provenance Engine:** Enforces the 9-stage lineage chain, creates conflict records, and manages RMP verification attestations.
- **Strict Boundary Enforcements:**
  - Deterministic clinical safety rules execute independently of statistical AI models. If the AI runtime crashes, the clinical safety engine continues operating without degradation.

### 2.4 Tier 4: AI & Perceptual Adapters
- **Technology:** Local Open-Source AI runtimes (Ollama, llama.cpp, faster-whisper, PaddleOCR) encapsulated behind an abstract `AIAdapter` interface.
- **Responsibilities:**
  - Unstructured narrative entity extraction and SNOMED-CT / LOINC normalization.
  - Speech-to-text transcription with word-level acoustic timecodes $[t_{\text{start}}, t_{\text{end}}]$.
  - Optical character recognition with spatial bounding box detection $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$.
  - Regional language translation (Odia/Hindi to clinical English).
  - Draft synthesis for clinical triage summaries and follow-up question candidates.
- **Strict Boundary Enforcements:**
  - All outputs are labeled `AI_INFERRED` with calibrated confidence scores ($C \in [0.0, 1.0]$).
  - Statistical models are strictly forbidden from diagnosing, prescribing, admitting, discharging, or self-verifying.

### 2.5 Tier 5: Persistence Layer (Relational & Event State)
- **Technology:** Dual Relational Engine via SQLAlchemy 2.0:
  - **Edge Mode:** SQLite 3.45+ with Write-Ahead Logging (`WAL`) and `PRAGMA foreign_keys = ON`.
  - **Cloud/Hub Mode:** PostgreSQL 15+ / Supabase with native JSONB, UUID, and Row-Level Security.
- **Responsibilities:**
  - Canonical relational storage of Master Case records (`cases`, `patients`, `vital_readings`, `evidence_records`, `facilities`).
  - Immutable, append-only event logging (`case_events`, `audit_logs`).
  - Cryptographic Merkle hash chaining ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$) guaranteeing tamper-evidence under Section 63 BSA 2023.

### 2.6 Tier 6: Storage & Audit Archive
- **Technology:** Local File System (`/var/data/clinova/media/`) or Supabase Storage (S3-compatible) + Local Sync Journals (`sync_journals`).
- **Responsibilities:**
  - Storing raw binary artifacts (audio recordings, image scans, generated PDF reports) outside the relational database to prevent WAL lock contention.
  - Tracking data retention lifecycles under DPDP Act 2023 (30-day raw media purge to `HASH_ONLY` state).
  - Bi-directional sync journal management between offline edge nodes and central hubs.

---

## 3. Clear Trust Boundaries & Data Flow

```
[ UNTRUSTED ZONE ] ──► Internet / Frontline Tablets / Patient Input Devices
       │
       ▼ (Boundary 1: Authentication, Input Validation & Sanitization)
[ RESTRICTED ZONE ] ──► API Gateway / Reverse Proxy / Nginx
       │
       ▼ (Boundary 2: Role Authorization, Session Scoping, Tenant Verification)
[ TRUSTED CLINICAL CORE ] ──► Domain Services & Deterministic Safety Engine
       │                 │
       │ (Isolated IPC)  │ (Transactional SQL Pool)
       ▼                 ▼
[ STATISTICAL AI ]  [ PERSISTENCE & AUDIT ]
(Read-Only Prompts, (Immutable Ledgers,
 Sandboxed Runtimes) Cryptographic Chains)
```

1. **Client to API Gateway (Boundary 1):** All input from web browsers or mobile tablets is treated as untrusted. Payloads are subjected to strict Pydantic schema validation, size limits (e.g. max 10MB audio, max 15MB images), and sanitization before entering domain services.
2. **Gateway to Domain Services (Boundary 2):** Calls require valid cryptographic JWT tokens. Role permissions are verified against the canonical role matrix (NMC Reg 27). No clinical command executes without an explicit `actor_id` and verified role.
3. **Domain Core to AI Adapters (Isolated IPC):** Communication with local SLM/Whisper/OCR runtimes occurs via isolated loopback HTTP/IPC calls. Raw prompt injection vectors are neutralized via strict schema-constrained output decoding (JSON Schema enforcement).
4. **Domain Core to Persistence:** Database access utilizes scoped connection pools. Triggers enforce immutability on audit and event tables; application-level logic cannot bypass hash chaining.

---

## 4. Communication Protocols & Inter-Service Contracts

| Channel | Protocol | Payload Standard | Durability & Fallback |
| :--- | :--- | :--- | :--- |
| **Client $\to$ API** | HTTPS / REST | JSON (RFC 8259) / Multipart | Client retries with exponential backoff; local draft saved to IndexedDB |
| **Telemetry $\to$ Workbench** | WebSocket / SSE | JSON Event Stream | Heartbeat ping every 15s; auto-reconnect falls back to 5s polling |
| **Domain $\to$ Relational DB** | TCP / UNIX Socket | SQL (SQLAlchemy 2.0 Async) | Connection pooling with automatic reconnection and busy timeout |
| **Domain $\to$ Local AI** | HTTP REST (127.0.0.1) | JSON (Structured Prompts) | 3-second timeout; automatic fallback to deterministic clinical rules |
| **Edge $\to$ Central Cloud** | HTTPS (mTLS) | Gzip Compressed JSON Journal | Asynchronous, idempotent push/pull; resilient to weeks of network outage |
