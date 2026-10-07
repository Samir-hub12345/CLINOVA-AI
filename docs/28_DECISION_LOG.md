# CLINOVA AI — Architecture Decision Record (ADR) Log

> **Document ID:** `DOC-28`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Governance & Purpose

This log documents all foundational architectural, technical, clinical safety, and governance decisions established for CLINOVA AI. Any future change to core architectural contracts or boundaries must be recorded here as a numbered ADR.

---

## 2. Master Architecture Decision Records

### ADR-001: Legacy Prototype Reset & Clean Architecture
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** The legacy prototype had accumulated duplicate nested directories, conflicting dependencies, and unverified mockups that contradicted the core product definition.
- **Decision:** Reset the repository to a clean application foundation with strict phase gating. Rebuild cleanly using FastAPI (backend) and Next.js (frontend).
- **Consequences:** Eliminates technical debt, guarantees that every committed feature satisfies the 11-point integration contract, and ensures stable engineering velocity.

### ADR-002: Dual Database Strategy (SQLite Dev / PostgreSQL Production)
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Evaluators and rural clinics need to run the system with zero database setup friction, while institutional deployments require multi-user relational concurrency.
- **Decision:** Utilize SQLAlchemy 2.0 async with `aiosqlite` for zero-install local development, and PostgreSQL (`asyncpg`) hosted on Supabase Free for multi-user staging and production.
- **Consequences:** Developers run the full system immediately with zero setup; production switches via a single environment variable (`DATABASE_URL`).

### ADR-003: Non-Diagnostic Mandate & Network-Layer Safety Headers
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Healthcare software risks severe medicolegal liability and patient harm if users mistake advisory suggestions for definitive medical diagnoses.
- **Decision:** Enforce non-diagnostic governance at the network layer. ASGI middleware injects `X-Clinical-Safety: Non-Diagnostic-Advisory-Only` and `X-Human-In-The-Loop: Required-Before-Action` on 100% of API responses.
- **Consequences:** Clinicians and evaluators are constantly reminded that qualified human oversight is mandatory. Prevents autonomous clinical routing.

### ADR-004: Clean Separation of Public Website and Operational Workspace
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Public visitors (judges, researchers, public health leaders) require a serious, clear explanation of the platform's innovation, while hospital staff need high-density, distraction-free clinical workstations.
- **Decision:** Serve the public technology portal at `/` and `/innovation`, and isolate operational clinical tools into role-scoped workspaces (`/doctor`, `/nurse`, `/referrals`, `/facilities`, `/signals`).
- **Consequences:** Prevents clinical workstations from looking like consumer marketing pages while ensuring public evaluators grasp the core innovations.

### ADR-005: Zero-Cost Open-Source AI Strategy (Local Qwen3-4B, Whisper, PaddleOCR)
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Commercial cloud LLM and vision APIs introduce recurring per-token fees, latency spikes, and internet dependency incompatible with rural Indian clinics.
- **Decision:** Standardize on local, open-source models: Qwen3-4B local runtime for structured clinical NLP, local Whisper / faster-whisper for speech transcription, and local PaddleOCR / Tesseract for document extraction, with deterministic rule fallbacks.
- **Consequences:** Guarantees ₹0 operating cost, preserves patient privacy, enables air-gapped on-premise deployment, and eliminates vendor lock-in.

### ADR-006: Synthetic Patient Data & Strict PII Minimization
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Using real patient records introduces severe data privacy and HIPAA/DPDP breach risks.
- **Decision:** Mandate 100% synthetic patient cohorts (`PT-XXXXXX`) and simulated facility telemetry. Scrub all accidental direct identifiers at the intake gateway via the `AnonymizerService`.
- **Consequences:** Guarantees zero compliance risk during public demonstrations, open-source auditing, and institutional evaluations.

### ADR-007: Zero-Cost Mapping & Geospatial Strategy (Leaflet + OpenStreetMap)
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Commercial mapping APIs (Google Maps Platform) require paid billing accounts and incur charges per map load and routing query.
- **Decision:** Deploy Leaflet.js with public OpenStreetMap tile layers, utilizing local Haversine calculations and road-type travel time heuristics for all network facility navigation.
- **Consequences:** 100% free mapping, zero external API keys, offline tile caching support, and complete operational independence.

### ADR-008: Google Cloud & Google AI Independence
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** The baseline prototype must remain sustainable, open, and accessible to any public health institution without requiring proprietary Google Cloud contracts.
- **Decision:** Google Cloud Platform (GCP) and Google AI APIs are NOT mandatory components. The core application runs locally with zero GCP dependencies.
- **Consequences:** Unrestricted open-source deployment on standard Linux/Windows hardware and free cloud tiers.

### ADR-009: Single Master Case Architecture & Derived Purpose-Specific Reports
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Fragmented documentation causes critical information loss when patients move between triage, nursing, doctor review, inpatient wards, and referrals.
- **Decision:** Every patient encounter possesses exactly ONE Master Case record. All 6 report types (`Comprehensive`, `Vitals Addendum`, `Routine`, `Ward Admission`, `Emergency`, `OT`) derive dynamically from the Master Case state.
- **Consequences:** Eliminates disconnected medical data silos and guarantees end-to-end clinical traceability.

### ADR-010: Dynamic Mid-Encounter Escalation & Dual Entry Routing
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Patients who appear stable at registration may rapidly decompensate while completing questionnaires or waiting in line.
- **Decision:** Implement dual entry modes (`Regular` vs `Emergency Fast-Track`) and enforce the dynamic escalation invariant: any regular encounter immediately promotes to emergency status the instant a red flag or abnormal vital is detected.
- **Consequences:** Guarantees a deteriorating patient is never trapped in a non-emergency queue.

### ADR-011: Strict Phase Control & Human-in-the-Loop Progression Gate
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Complex software systems suffer architectural degradation when implementation begins before product contracts are fully approved.
- **Decision:** Enforce the single-phase execution rule. Phase 1 authoring produces documentation and static design wireframes only. Transition to Phase 2 implementation strictly requires human review approval.
- **Consequences:** Prevents unverified feature drift and guarantees complete alignment with the official BPUT problem statement.

### ADR-012: Framing Output as "The Safest Achievable Care Pathway"
- **Date:** October 2026 | **Status:** ACCEPTED
- **Context:** Describing AI outputs as "The AI's Diagnosis" creates unrealistic clinical expectations, triggers medicolegal liabilities, and ignores physical facility constraints.
- **Decision:** Formally label the Orchestration Engine output as **"The Safest Achievable Next Care Pathway"**, evaluating clinical need, evidence uncertainty, facility capability, and system demand.
- **Consequences:** Establishes an explainable, resource-grounded decision support model that keeps qualified medical officers in absolute control.
