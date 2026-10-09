# CLINOVA AI — Technical Architecture & System Design Plan

> **Document ID:** `RES-134`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Distributed Systems Engineering Group  

---

## 1. Executive Summary & Phase 8 Mandate

Phase 8 translates the approved clinical product specifications, user journeys, operational environments, Master Case relational models, and evidence provenance foundations established across Phases 1 through 7 into a rigorous, complete, and validated **Technical Architecture & System Design**.

This phase is strictly an **Architecture Design, Reconciliation, Validation, and Documentation Phase**. Under the non-negotiable Atomic Phase Rule:
- No production application code is implemented or refactored.
- No user interface components are created or modified.
- No database migrations are generated or applied to live instances.
- No third-party AI models or live API endpoints are connected.
- No deployments are triggered.
- All technical specifications must be grounded in verified codebase reality and approved upstream documentation.

---

## 2. Upstream Specification Traceability

Phase 8 directly synthesizes and formalizes architectural decisions from the complete sequence of upstream research and product specifications:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       UPSTREAM SOURCE OF TRUTH PIPELINE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: Product Definition & Governance (DOC-00 through DOC-28)           │
│  ├── 18 BPUT Baseline Capabilities (B01–B18)                                │
│  ├── 11 Core Continuous Care Innovations (C01–C11)                          │
│  ├── AI Behavior Contract (Advisory Only; Human-in-the-Loop)                │
│  └── ₹0 Zero-Cost Open Source Technology Stack Mandate                      │
│                                                                             │
│  Phase 2: Innovation & Gap Analysis (RES-00 through RES-24)                 │
│  ├── Shift from 90-second static triage to Continuous Care Intelligence     │
│  └── Grounding in rural Odisha district health reality                      │
│                                                                             │
│  Phase 3: Target Users & Clinical Permissions (RES-30 through RES-42)       │
│  ├── RMP Monopoly under NMC Regulations 2023 (Reg 27 & 28)                  │
│  └── 3 Primary Interfaces: Patient Intake, Nurse Triage, Doctor Workbench   │
│                                                                             │
│  Phase 4: Target Healthcare Environments (RES-43 through RES-56)            │
│  ├── 6 Environments: Gov Hospital, PHC, Health Camp, Company Clinic,        │
│  │   Industrial Health, Campus Health                                       │
│  └── One Codebase, Configured Environments Principle                        │
│                                                                             │
│  Phase 5: Master Patient Journey (RES-57 through RES-77)                   │
│  └── 27 Canonical Patient States (S01 to S27) Across 6 Longitudinal Epochs  │
│                                                                             │
│  Phase 6: Master Case Canonical Data Model (RES-78 through RES-105)         │
│  ├── Root Entity `cases` with Dual SQLite WAL / PostgreSQL Compatibility     │
│  └── Longitudinal Continuity across all 17 clinical sub-systems             │
│                                                                             │
│  Phase 7: Evidence, Provenance & Uncertainty (RES-106 through RES-133)      │
│  ├── 8 Evidence Sources, 6 Epistemic States, 9-Stage Lineage Chain          │
│  ├── Normalized [0, 1000] Bounding Boxes & Word-Level Acoustic Grounding    │
│  └── Decoupling of Uncertainty (U_t) from Risk Severity (R_t)               │
│                                                                             │
│  PHASE 8: TECHNICAL ARCHITECTURE & SYSTEM DESIGN (RES-134 through RES-163)  │
│  └── Translation of all product logic into modular technical architecture   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Architectural Principles

Phase 8 adheres strictly to fourteen non-negotiable architectural principles:

1. **ONE CLINOVA CORE:** A single unified domain core powers all operational interfaces and workflows; no splintered applications.
2. **ONE MASTER CASE:** Exactly one continuous canonical Master Case entity coordinates an entire clinical episode from arrival to discharge.
3. **ONE CODEBASE:** A single modular codebase serves all deployment scenarios via dynamic configuration; zero code bifurcations.
4. **CONFIGURED ENVIRONMENTS:** Deployment-time configuration profiles adapt facility capabilities and UI workflows without code branching.
5. **HUMAN CONTROL:** Qualified human healthcare professionals retain absolute monopoly over all clinical decisions; AI is strictly advisory.
6. **ZERO-IMPUTATION LAW:** Missing clinical data is explicitly modeled as `UNKNOWN`; algorithms never silently fabricate normal values.
7. **INFERRED ≠ VERIFIED:** Statistical model deductions are permanently tagged `AI_INFERRED` and cannot transition to `VERIFIED` without an RMP sign-off.
8. **NON-DESTRUCTIVE HISTORY:** Conflicting measurements, edits, and overrides are recorded as new immutable events; clinical facts are never overwritten.
9. **ADVISORY-ONLY AI:** Machine intelligence generates candidate actions and structural drafts; it cannot prescribe, diagnose, or admit.
10. **OFFLINE-FIRST CAPABILITY:** Edge clinics operate 100% autonomously on local hardware with local SQLite persistence and local inference.
11. **AUDITABILITY:** All mutations produce tamper-evident, cryptographically chained event records complying with Section 63 BSA 2023.
12. **PROVENANCE:** Every clinical assertion maintains bidirectional links to raw sensory inputs (audio timecodes, image bounding boxes).
13. **SAFE FAILURE:** System degradation falls back cleanly to deterministic medical rules, paper procedures, and human manual workflows.
14. **CLEAR TRUST BOUNDARIES:** Security, clinical validation, and authentication are strictly enforced server-side; clients are untrusted.

---

## 4. Key Architectural Conflicts to Resolve

Previous phase audits (specifically Phase 6 and Phase 7 conclusions) identified four concrete technical tensions that must be formally resolved in Phase 8:

### 4.1 Reconciliation of `triage_cases` vs. Canonical `cases` Table
- **Codebase Reality:** Early Alembic migrations (`0001` through `0009`) defined a table named `triage_cases` with foreign key relationships from child tables.
- **Specification Reality:** Phase 6 canonical data models (`RES-79`) and `backend/app/db/models.py` specify `cases` as the root entity for the Master Case.
- **Resolution Strategy:** Designate `cases` as the single canonical Master Case table. Architectural models, domain layers, and documentation will standardize on `cases`. Phase 9 migration plan will introduce a non-destructive migration that standardizes the schema and provides a backward-compatible view `v_legacy_triage_cases`.

### 4.2 Dynamic Doctor Queue Wait-Time Calculation
- **Database Reality:** PostgreSQL prohibits non-deterministic functions (such as `NOW()`, `CURRENT_TIMESTAMP`, or `clock_timestamp()`) in `STORED GENERATED ALWAYS AS` column expressions, raising `ERROR: generation expression is not immutable`.
- **Resolution Strategy:** Explicitly eliminate any stored generated wait-time column. Dynamic wait time and composite queue priority will be evaluated at **query time** via indexed datetime subtraction (`clock_timestamp() - queued_at`) or encapsulated in a high-performance database view `v_active_doctor_queue`.

### 4.3 Asynchronous Dual-Review Deadlock Resolution
- **Workflow Reality:** Phase 7 identified that high-risk actions (e.g., thrombolysis sign-off) requiring dual physician review (`DUAL_REVIEW_REQUIRED`) cause an immediate insert-time deadlock if the database schema requires both primary and secondary signatures at row creation.
- **Resolution Strategy:** Formalize an asynchronous state lifecycle: `PENDING_SECONDARY_REVIEW` $\to$ `SECONDARY_REVIEW_INVITED` $\to$ `SECONDARY_REVIEW_COMMITTED` $\to$ `VERIFIED` / `REJECTED`. The primary clinician submits their verification independently, moving the record to `PENDING_SECONDARY_REVIEW`, which alerts the secondary reviewer without blocking database writes.

### 4.4 Automated Retention Daemon Trigger Authorization
- **Database Reality:** Immutable evidence ledgers feature database triggers that raise exceptions on `UPDATE` or `DELETE` operations. However, statutory retention policies (DPDP Act 2023 Section 8(7)) require raw media to be purged to `HASH_ONLY` state after the retention period.
- **Resolution Strategy:** Architect an authorized retention exception mechanism. The retention daemon operates under a dedicated database role or sets a localized transaction-scoped session variable (`SET LOCAL clinova.retention_daemon_active = 'true'`), allowing the trigger to permit retention status and purge certificate updates while strictly prohibiting content modifications.

---

## 5. Architectural Deliverables Inventory

Phase 8 produces thirty-two authoritative architectural specifications:

| Doc ID | File Name | Core Architectural Scope |
| :--- | :--- | :--- |
| `RES-134` | `134_TECHNICAL_ARCHITECTURE_PLAN.md` | Master execution plan, principles, and conflict roadmap |
| `RES-135` | `135_SYSTEM_ARCHITECTURE.md` | End-to-end system topology, tiers, trust boundaries, and protocols |
| `RES-136` | `136_FRONTEND_ARCHITECTURE.md` | Next.js App Router, state, routes, 3 core workbenches, and drawers |
| `RES-137` | `137_BACKEND_ARCHITECTURE.md` | FastAPI modular monolith, layering, CQRS patterns, and safety services |
| `RES-138` | `138_DOMAIN_MODULE_ARCHITECTURE.md`| Detailed domain module boundaries, interfaces, and data ownership |
| `RES-139` | `139_MASTER_CASE_ARCHITECTURE.md` | Master Case dependency graph, 27-state machine, and OCC engine |
| `RES-140` | `140_CAREGRAPH_ARCHITECTURE.md` | Computed projection architecture for dynamic patient trajectory |
| `RES-141` | `141_FACILITYGRAPH_ARCHITECTURE.md`| Capability freshness, resource verification, and care feasibility |
| `RES-142` | `142_SIGNALGRAPH_ARCHITECTURE.md` | Local/campus operational & syndromic telemetry with de-identification |
| `RES-143` | `143_ORCHESTRATION_ARCHITECTURE.md`| Multi-graph advisory synthesis, candidate actions, and human gating |
| `RES-144` | `144_AI_BOUNDARY_ARCHITECTURE.md` | Adapter boundaries, permitted scope, validation, and offline fallback |
| `RES-145` | `145_PROVENANCE_ARCHITECTURE.md` | Nine-stage lineage pipeline, spatial/acoustic grounding, and conflicts |
| `RES-146` | `146_MEDIA_PROCESSING_ARCHITECTURE.md`| Asynchronous OCR/ASR pipeline, storage abstraction, and job queues |
| `RES-147` | `147_OFFLINE_FIRST_ARCHITECTURE.md` | Edge Mini-PC architecture, SQLite WAL, and local network operations |
| `RES-148` | `148_SYNC_ARCHITECTURE.md` | Append-only sync journals, two-phase sync protocol, and conflict rules |
| `RES-149` | `149_QUEUE_ARCHITECTURE.md` | Query-time wait calculation, multi-dimensional priority, and routing |
| `RES-150` | `150_DATABASE_ARCHITECTURE.md` | Relational schema, dual SQLite/PG compatibility, and table reconciliation |
| `RES-151` | `151_RETENTION_ARCHITECTURE.md` | DPDP retention cycles, HASH_ONLY transition, and daemon bypass |
| `RES-152` | `152_DUAL_REVIEW_ARCHITECTURE.md` | Asynchronous dual-review state machine and independent validation |
| `RES-153` | `153_SECURITY_ARCHITECTURE.md` | Zero-trust authentication, RBAC, secret isolation, and break-glass |
| `RES-154` | `154_ENVIRONMENT_CONFIGURATION_ARCHITECTURE.md`| 6 environment profiles, deployment injection, and feature flags |
| `RES-155` | `155_OBSERVABILITY_ARCHITECTURE.md`| PHI-safe structured logging, health probes, metrics, and audit export |
| `RES-156` | `156_FAILURE_ARCHITECTURE.md` | Eleven-scenario failure matrix, graceful degradation, and manual modes |
| `RES-157` | `157_THREAT_MODEL.md` | 14-point healthcare threat analysis, mitigations, and residual risks |
| `RES-158` | `158_PERFORMANCE_ARCHITECTURE.md`| Concrete design targets separated from unmeasured benchmark claims |
| `RES-159` | `159_ZERO_COST_ARCHITECTURE.md` | Complete ₹0 open-source dependency audit and hardware sizing |
| `RES-160` | `160_DEPLOYMENT_TOPOLOGY.md` | Dev, Local Demo, PHC Edge, District Hospital, and Cloud topologies |
| `RES-161` | `161_ARCHITECTURE_DECISION_RECORD.md`| Formal Architecture Decision Records (ADR 8.1 through 8.10) |
| `RES-162` | `162_ARCHITECTURE_TRACEABILITY.md` | Bidirectional traceability matrix across all phases and requirements |
| `RES-163` | `163_PHASE_8_CONCLUSION.md` | Comprehensive 40-section conclusion report and final status |
| `SOURCES` | `SOURCES_PHASE_8.md` | Authoritative literature, statutory frameworks, and engineering standards |
| `DECISIONS`| `PHASE_8_DECISIONS.md` | Executive log of all Phase 8 architectural resolutions |

---

## 6. Execution Protocol & Completion Criteria

Phase 8 follows a strict linear sequence:
1. **Analyze:** Inspect codebase manifests (`package.json`, `requirements.txt`, models, existing routers, and migrations).
2. **Reconcile:** Align architectural models with upstream statutory, clinical, and data models (Phases 1–7).
3. **Design:** Detail module boundaries, data structures, interaction contracts, and safety invariants.
4. **Audit:** Subject the architecture to threat modeling, failure mode analysis, and performance sanity checks.
5. **Document:** Author all 32 specification artifacts in `docs/research/`.
6. **Verify:** Confirm that zero production code was modified and all 40 conclusion headings are populated.
7. **Stop:** Mark status strictly as `READY FOR HUMAN REVIEW`.
