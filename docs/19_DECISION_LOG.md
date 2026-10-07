# CLINOVA AI — Architecture Decision Record (ADR) Log

> **Document ID:** `DOC-19`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Decision Log Overview

This log documents all foundational architectural, technical, and governance decisions made during the reconstruction of CLINOVA AI. Changes to core architectural patterns must be appended here as structured Architecture Decision Records (ADRs).

---

## 2. Architectural Decision Records

### ADR-001: Legacy Prototype Reset & Clean Foundation
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** The legacy prototype had accumulated duplicate nested directories (`CLIVORA-AI`, `CLIVORA-AI - Copy`), fractured routes, circular dependencies, and unverified mockups that contradicted the core product definition.
- **Decision:** Reset the legacy prototype to a clean application foundation. Preserve legacy history via Git tag `legacy-prototype-checkpoint`. Rebuild cleanly using FastAPI (backend) and Next.js 15 (frontend).
- **Consequences:** Eliminates technical debt, guarantees that every committed feature satisfies the 11-point integration contract, and ensures a stable development velocity.

### ADR-002: Dual Database Strategy (SQLite Dev / PostgreSQL Production)
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** Evaluators, hackathon judges, and local clinic nurses need to test the system with zero database setup friction, while institutional deployments require enterprise concurrency.
- **Decision:** Utilize SQLAlchemy 2.0 async with `aiosqlite` as the zero-config default development driver, with seamless environment variable switching to `asyncpg` for PostgreSQL in staging and production.
- **Consequences:** Developers can run the entire platform immediately with zero external services; production instances switch via a single `.env` change (`DATABASE_URL`).

### ADR-003: Non-Diagnostic Mandate & HTTP Header Enforcement
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** Healthcare software risks severe medicolegal liability and patient harm if users mistake advisory suggestions for definitive medical diagnoses.
- **Decision:** Enforce non-diagnostic governance at the network layer. ASGI middleware injects `X-Clinical-Safety: Non-Diagnostic-Advisory-Only` and `X-Human-In-The-Loop: Required-Before-Action` on 100% of API responses.
- **Consequences:** Clinicians and evaluators are constantly reminded that qualified human oversight is mandatory. Prevents autonomous clinical routing.

### ADR-004: Clean Separation of Public Website and Operational Workspace
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** Public visitors (judges, researchers, health system leaders) require a serious, clear explanation of the platform's innovation, while hospital staff need high-density, distraction-free clinical workstations.
- **Decision:** Serve the public technology portal at `/` and isolate operational clinical tools into role-scoped routes (`/intake`, `/reviewer`, `/facilities`, `/signalgraph`).
- **Consequences:** Prevents clinical workstations from looking like consumer marketing pages while ensuring public evaluators grasp the core innovations.

### ADR-005: Local-First Deterministic Fallbacks for All AI Integrations
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** Cloud AI APIs (Gemini, Groq, Sarvam, OCR Space) can experience latency spikes, rate limits, or network disconnection in remote rural clinics.
- **Decision:** Every multimodal and reasoning capability must implement an immediate, deterministic local fallback (e.g., standard NEWS2 scoring when LLM offline, manual key-value entry when OCR unavailable).
- **Consequences:** The core patient triage workflow remains 100% operational under all network failure conditions.

### ADR-006: Synthetic Patient Data & Strict PII Minimization
- **Date:** October 2026
- **Status:** ACCEPTED
- **Context:** Developing and testing healthcare systems using real patient records introduces severe data privacy and HIPAA/DPDP breach risks.
- **Decision:** Mandate 100% synthetic patient cohorts (`SYN-PT-XXXX`) and simulated facility telemetry. Scrub all accidental direct identifiers at the intake gateway.
- **Consequences:** Guarantees zero compliance risk during public demonstrations, open-source auditing, and institutional evaluations.

---

## 3. Unresolved Technical Decisions (Pending Architectural Gates)

Per Section 27 (Item 13) of the Master Contract, the following key architectural decisions remain open and must be evaluated against clinical trade-offs before Phase 10/11 commitment:

### UTD-001: Speech-to-Text (STT) Architecture & Multi-Dialect Handling
- **Context:** Rural and peripheral triage settings experience high packet loss, low bandwidth, and distinct regional Indian accents (Odia, Hindi, Bengali).
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 10 (Frontend/Backend Foundations) & Phase 11 (BPUT Baseline)
- **Options Under Evaluation:**
  1. *Option A (Browser Web Speech API):* Zero server compute; native Indian English/Hindi support in Chromium; fails on Firefox/Safari and requires active internet.
  2. *Option B (Local Whisper ONNX / Faster-Whisper):* 100% air-gapped; privacy preserving; requires ~500MB model download and CPU/GPU resources on client/server.
  3. *Option C (Cloud API - Sarvam AI / Gemini Multimodal Audio):* High accuracy on Indian vernaculars; requires external API keys and network connectivity.
- **Architectural Trade-Off:** Option A provides instant prototype velocity with zero backend burden; Option B guarantees true offline resilience; Option C delivers peak dialect accuracy.
- **Provisional Direction:** Hybrid ladder: Default to Web Speech API in browser with graceful fallback to manual text entry, while exposing backend adapter for Sarvam/Whisper when configured.

### UTD-002: Medical Document OCR Engine Selection
- **Context:** Uploaded clinical documents consist of crumpled prescription slips, thermal ECG strips, and printed CBC tables with varying fonts and resolutions.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 8 (Database & API Contracts) & Phase 11 (BPUT Baseline)
- **Options Under Evaluation:**
  1. *Option A (Client-side Tesseract.js WebAssembly):* Completely private; runs entirely in browser memory; poor performance on non-standard table geometries.
  2. *Option B (Server-side PyTesseract / Tesseract OCR):* Open-source; requires system binary installation in Docker container; modest table-structure recognition without layout models.
  3. *Option C (Cloud Multimodal Vision - Gemini 1.5 Flash / Google Cloud Document AI):* Superb clinical entity recognition and key-value extraction; requires active internet and API credentials.
- **Architectural Trade-Off:** High-fidelity cloud vision vs zero-install container portability.
- **Provisional Direction:** Multi-tier fallback: Deterministic key-value parser + local Tesseract fallback when offline; Cloud Vision when API key provided. Always require manual verification before committing to CareGraph.

### UTD-003: CareGraph Graph Persistence Topology
- **Context:** Individual patient encounters generate directed graphs of 20–100 nodes (symptoms, vitals, labs, observations) with temporal and causal edges.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 8 (Database & API Contracts) & Phase 12 (CareGraph Integration)
- **Options Under Evaluation:**
  1. *Option A (Pure In-Memory NetworkX Graph + Relational JSON Column):* Ephemeral graph computed in memory on encounter load; serialized snapshot stored in `cases.caregraph_snapshot` JSON column in SQLite/PostgreSQL. Zero external dependencies.
  2. *Option B (Relational Adjacency Tables):* Normalized SQL tables (`caregraph_nodes`, `caregraph_edges`). Standard relational queries; multi-hop recursive queries require CTEs.
  3. *Option C (Dedicated Graph Database - Neo4j / Kuzu Embedded):* Native graph traversals and Cypher queries; adds external container dependency and operational overhead.
- **Architectural Trade-Off:** Operational simplicity vs native graph traversal query power.
- **Provisional Direction:** Option A (In-memory NetworkX with relational JSON snapshot). Encapsulates graph logic inside Python domain service with zero runtime operational overhead.

### UTD-004: Real-time Telemetry Push Mechanism for SignalGraph & Waitlist
- **Context:** Clinical workstations must receive dynamic priority updates when a patient deteriorates or when regional bed capacity saturates.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 10 (Frontend/Backend Foundations) & Phase 14 (SignalGraph)
- **Options Under Evaluation:**
  1. *Option A (Server-Sent Events - SSE):* Lightweight unidirectional push over standard HTTP/2; native browser reconnection; firewall friendly; no external broker needed.
  2. *Option B (Full-duplex WebSockets):* Low latency bidirectional communication; requires WebSocket connection state management, heartbeat pinging, and sticky sessions.
  3. *Option C (Short Polling via SWR / React Query):* Periodic fetch (every 5-10 seconds); dead simple; slightly higher HTTP overhead and server query volume.
- **Architectural Trade-Off:** Simplicity and robustness in resource-constrained clinic LANs vs true sub-second push.
- **Provisional Direction:** Option A (SSE) for priority alerts and SignalGraph telemetry, with Option C (SWR polling) as automatic browser fallback.

### UTD-005: Medical Document & Audio Blob Vault Storage
- **Context:** Triage intake captures voice recordings (WAV/WEBM) and report scans (PDF/JPEG) that contain sensitive clinical evidence.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 8 (Database & API Contracts)
- **Options Under Evaluation:**
  1. *Option A (Encrypted Local Filesystem Directory):* Simple file storage in `uploads/vault` with UUID-based hashing, restricted permissions, and automated 24h retention cleanup. Zero cloud dependency.
  2. *Option B (S3-Compatible Object Store - MinIO / Cloud Storage):* Standard enterprise object storage with presigned URLs; requires MinIO container or cloud bucket configuration.
- **Architectural Trade-Off:** Local prototype portability vs enterprise multi-node scalability.
- **Provisional Direction:** Abstract `StorageVaultInterface` with local encrypted directory implementation for default dev/local deployment, swappable to S3 via configuration.

### UTD-006: User Authentication & Clinical Session Security
- **Context:** Clinicians, triage nurses, and administrators require distinct permissions, but rural clinics cannot afford slow, complex enterprise SSO onboarding during emergencies.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 10 (Frontend/Backend Foundations)
- **Options Under Evaluation:**
  1. *Option A (Stateless JWT with Local Argon2/Bcrypt Passwords):* Fast, self-contained, no external auth service, role claims embedded in signed tokens.
  2. *Option B (Third-Party Identity Provider - Keycloak / Supabase Auth / Clerk):* Enterprise SSO and OAuth2; adds external service dependency.
- **Architectural Trade-Off:** Zero-config self-containment vs enterprise identity federation.
- **Provisional Direction:** Option A (JWT with local role claims and quick-switch test personas for demonstration).

### UTD-007: Clinical NLP Entity Extraction Fallback Engine
- **Context:** Unstructured symptom narratives (e.g., "patient feels crushing retrosternal pain radiating to left jaw for 2 hours") must be parsed into structured entities.
- **Status:** OPEN / UNRESOLVED
- **Target Resolution Phase:** Phase 11 (BPUT Baseline Workflow)
- **Options Under Evaluation:**
  1. *Option A (Deterministic Clinical Regex & Synonym Taxonomy):* 100% deterministic, zero latency, runs offline, zero hallucination; limited handling of complex syntactic phrasing.
  2. *Option B (Local Quantized SLM - Llama 3.2 3B / BioMistral via Ollama/llama-cpp):* Handles complex linguistic variations offline; requires substantial RAM (~3-4GB) and slow on low-end machines.
  3. *Option C (Cloud LLM - Gemini 1.5 Flash / Groq Llama 3):* Instant structured JSON output; requires API key and network connectivity.
- **Architectural Trade-Off:** Deterministic safety & zero dependencies vs linguistic generalization.
- **Provisional Direction:** Multi-layer pipeline: Deterministic regex/dictionary parser as mandatory baseline foundation, supplemented by Cloud LLM when configured, with mandatory clinician confirmation.

