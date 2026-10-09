# CLINOVA AI — Phase 6 Master Case Data Model Research & Specification Plan

> **Document ID:** `RES-78`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Phase 6 Mandate

Phase 6 of the CLINOVA AI roadmap establishes the **Canonical Data Model Specification** for the platform. It translates the end-to-end clinical workflows, 27-state deterministic state machine, and multi-actor handoffs defined in Phase 5 into a mathematically rigorous, relational, provenance-aware, uncertainty-aware, and synchronization-safe data architecture.

The overarching design mandate is the **Single Continuous Master Case Invariant**:
$$\forall \text{ clinical encounter } e, \quad \exists ! \text{ canonical identifier } \mathbf{case\_id}$$
Under no operational circumstance may intake notes, vernacular audio recordings, document OCR crops, point-of-care nursing vitals, doctor modifications, facility feasibility evaluations, referral packs, ward charts, surgical checklists, or outcome records diverge into isolated or disconnected database records. All clinical and operational artifacts across the care continuum MUST be intrinsically bound to the SAME continuous Master Case.

Phase 6 is strictly a **Data Model Design and Validation Phase**. It does not construct production application endpoints, write UI components, or apply schema changes to active production databases. Instead, it produces exhaustive, defensible architectural specifications, relational schemas in dual SQLite/PostgreSQL dialects, formal invariants, and scenario validation matrices.

---

## 2. Upstream Reconciliation & Source of Truth

Phase 6 directly reconciles and synthesizes seven authoritative upstream inputs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       UPSTREAM SOURCE OF TRUTH HIERARCHY                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Phase 5 Master Journey & State Machine (RES-57 to RES-77) [IMMEDIATE]   │
│     └── 27 Canonical States, Sufficiency Gate (S >= 0.85), 6 Pathways        │
│  2. Phase 4 Target Environment Specification (RES-43 to RES-56)             │
│     └── 6 Operating Settings, Single Codebase, Resource Matrix               │
│  3. Phase 3 Target User Specification (RES-30 to RES-42)                    │
│     └── 6 Human Roles, Permission Model, RMP Clinician Monopoly              │
│  4. Phase 2 Innovation & Research Audits (RES-00 to RES-24)                 │
│     └── CAREGRAPH, FACILITYGRAPH, SIGNALGRAPH, Closed-Loop Outcomes         │
│  5. Phase 1 Product Definition & Architecture (DOC-00 to DOC-28)            │
│     └── Master Case Concept (DOC-07), Provenance Model (DOC-08)             │
│  6. BPUT Problem Statement & Regional Context                               │
│     └── Odisha Public Health Realities, Dual-Facility Demo Corridor         │
│  7. Existing Repository Architecture & Alembic Migrations                    │
│     └── Migrations 0001-0009, Baseline Models, SQLAlchemy Typing             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Upstream Synthesis Matrix

| Source Document | Core Input to Phase 6 Data Model | Data Architectural Translation |
| :--- | :--- | :--- |
| **Phase 5 (`RES-61`)** | 27 Canonical States (`STATE_NEW` to `STATE_CLOSED`) | Relational `case_state_transitions` table with optimistic locking (`state_version`). |
| **Phase 5 (`RES-63`)** | Zero-Imputation Law & Sufficiency Metric ($S \ge 0.85$) | Explicit `missing_information_items` with discrete epistemic states (`KNOWN`, `UNKNOWN`, `CONFLICTING`). |
| **Phase 5 (`RES-64`)** | CAREGRAPH Multi-Axis Risk Decomposition | Decoupled storage of Risk Score, Trajectory Slope, and Uncertainty Score ($U_t$). |
| **Phase 5 (`RES-65`)** | FACILITYGRAPH Resource Verification | `facility_capabilities` with telemetry freshness tracking (`FRESH`, `STALE`, `UNVERIFIED`). |
| **Phase 5 (`RES-66`)** | Advisory Orchestration & Human Control Gate | `orchestration_recommendations` storing AI advice with mandatory `human_review_required = TRUE`. |
| **Phase 5 (`RES-69`)** | Closed-Loop Inter-Facility Referrals | `referrals` with SBAR clinical summary pack, destination hospital lock, and transport log. |
| **Phase 5 (`RES-70`)** | Operation Theatre Fast-Track & WHO Checklist | `surgical_procedures` storing 3-phase WHO surgical safety checklist and dual sign-off. |
| **Phase 5 (`RES-71`)** | Closed-Loop Outcome Architecture | `case_outcomes` tracking Planned Advice vs Clinician Decision vs Care Action vs Real Outcome. |
| **Phase 4 (`RES-50`)** | Single Codebase Doctrine across 6 Environments | Database schemas independent of environment; environmental behavior driven by `facilities.tier`. |
| **Phase 3 (`RES-34`)** | NMC 2023 Clinician Monopoly over Orders | Schema-level foreign key and role validation enforcing `ROLE_CLINICIAN` on dispositions. |
| **Phase 1 (`DOC-07`)** | Master Case Principle | Single immutable `case_id` UUIDv4 anchoring all child tables. |
| **Existing Codebase** | Alembic 0001–0009 & `models.py` | Full backward-compatible expansion mapping existing schemas to the canonical standard. |

---

## 3. Core Architectural Principles of the Data Model

The CLINOVA data model is built upon ten foundational engineering principles:

1. **Single Master Case Invariant:** Every clinical event belongs to exactly one `case_id`. All records link back to this key.
2. **Strict Identity and Encounter Decoupling:** Patient Identity, Clinical Encounter, Master Case, Facility, and Actor are separate relational entities. Anonymous emergency patients are fully supported without blocking care.
3. **Append-Only Event Sourcing & Auditability:** Clinical and state transitions are recorded as immutable event streams. No destructive in-place updates of historical evidence.
4. **Explicit Epistemic States & Provenance:** Every clinical data point carries provenance (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `STAFF_ENTERED`, `CLINICIAN_VERIFIED`, `AI_INFERRED`, `SYSTEM_DERIVED`) and epistemic status (`KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`, `INFERRED`).
5. **Zero-Imputation Law:** Absence of data is NEVER treated as normal or negative. Missing values are recorded explicitly as `UNKNOWN`.
6. **Strict 3-Axis Clinical Decomposition:** Risk (physiological hazard), Trajectory (rate and direction of change), and Uncertainty (data completeness) are stored as separate, uncoupled vectors.
7. **Advisory AI Boundaries & Non-Destructive Modifications:** Machine recommendations are immutable. When a clinician alters a suggestion, both the original AI recommendation and the doctor's override are permanently stored.
8. **Closed-Loop Referral & Care Logistics:** Referrals model the entire physical transfer lifecycle, from digital dispatch and ambulance transit to destination acceptance and arrival.
9. **Offline Edge Resilience & Sync Safety:** The schema operates cleanly in local SQLite WAL on edge Mini-PCs and synchronizes seamlessly with central PostgreSQL/Supabase without ID collisions.
10. **DPDP Compliance & Emergency Air-Gapping:** Demographic identity is logically separated from clinical research/signal extraction, with auditable break-glass emergency consent overrides.

---

## 4. Phase 6 Deliverables Breakdown (30 Artifacts)

Phase 6 authors 30 comprehensive specification, model, compatibility, validation, and traceability documents:

```
docs/research/
├── 78_MASTER_CASE_DATA_MODEL_PLAN.md              [Current Document]
├── 79_MASTER_CASE_CANONICAL_MODEL.md              [The Core Master Case Entity & ERD]
├── 80_IDENTITY_MODEL.md                           [Identity, Encounter, Anonymity, Merge]
├── 81_CASE_LIFECYCLE_MODEL.md                     [27 Canonical States & Transition Model]
├── 82_EVENT_HISTORY_MODEL.md                      [Append-Only Ledger & Merkle Chaining]
├── 83_EVIDENCE_PROVENANCE_MODEL.md                [Sources, Epistemic States, Conflict Model]
├── 84_MEDIA_DOCUMENT_MODEL.md                     [Audio, Transcripts, Documents, OCR Crops]
├── 85_CLINICAL_OBSERVATION_MODEL.md               [Serial Vitals, Labs, Signs, Observations]
├── 86_SYMPTOM_TIMELINE_MODEL.md                   [Chronological Symptom Trajectory]
├── 87_MISSING_INFORMATION_MODEL.md                [Gaps, Sufficiency Metric, Zero Imputation]
├── 88_FOLLOWUP_QUESTION_MODEL.md                  [Adaptive Q&A, Respondent Targeting]
├── 89_RISK_TRAJECTORY_UNCERTAINTY_MODEL.md        [3-Axis Decoupled Clinical Evaluation]
├── 90_TRIAGE_REVIEW_MODEL.md                      [Triage Notes, Differential Hypotheses]
├── 91_CLINICIAN_DECISION_MODEL.md                 [Workbench Actions, Overrides, Verification]
├── 92_FACILITY_REQUIREMENT_MODEL.md               [Care Requirements, Facility Feasibility]
├── 93_ORCHESTRATION_RECOMMENDATION_MODEL.md       [Advisory Pathways, Human Control]
├── 94_REFERRAL_TRANSFER_MODEL.md                  [Closed-Loop Transfer, Transport Logistics]
├── 95_WARD_OT_MODEL.md                            [Inpatient Admissions, WHO OT Checklist]
├── 96_APPOINTMENT_OUTCOME_MODEL.md                [Follow-Ups, Closed-Loop Outcomes]
├── 97_CONSENT_PRIVACY_MODEL.md                    [DPDP Consent, Break-Glass, Air-Gapping]
├── 98_AUDIT_EVENT_MODEL.md                        [Tamper-Evident Medico-Legal Ledger]
├── 99_OFFLINE_SYNC_MODEL.md                       [SQLite to Postgres Sync, Conflict Matrix]
├── 100_DATA_RETENTION_MODEL.md                    [Retention Policies, Legal Archival]
├── 101_SQLITE_POSTGRES_COMPATIBILITY.md           [Dual-Dialect Type & Syntax Mapping]
├── 102_DATA_INTEGRITY_INVARIANTS.md               [The 12 Core Invariants & DB Constraints]
├── 103_MASTER_CASE_TEST_SCENARIOS.md              [Scenario Validation across Cases A - J]
├── 104_MASTER_CASE_TRACEABILITY.md                [End-to-End Bidirectional Matrix]
├── 105_PHASE_6_CONCLUSION.md                      [Final Report with 31 Major Headings]
├── SOURCES_PHASE_6.md                             [Statutory & Informatics Bibliography]
└── PHASE_6_DECISIONS.md                           [Formal Decisions Log 6.1 - 6.12]
```

---

## 5. Methodological Execution Workflow

To ensure total completeness, Phase 6 executes the following disciplined pipeline:

$$\mathbf{ANALYZE} \longrightarrow \mathbf{MODEL} \longrightarrow \mathbf{VALIDATE} \longrightarrow \mathbf{DOCUMENT} \longrightarrow \mathbf{SELF\text{-}AUDIT} \longrightarrow \mathbf{REPORT} \longrightarrow \mathbf{STOP}$$

1. **ANALYZE:** Inspect existing database tables (`alembic/versions/` 0001–0009 and `db/models.py`) and reconcile with Phase 5 requirements.
2. **MODEL:** Formulate clean, normalized, robust relational schemas in dual SQLite and PostgreSQL DDL, defining primary keys, foreign keys, constraints, and indexes.
3. **VALIDATE:** Execute rigorous paper validation of the schema against all 10 clinical benchmark scenarios (Cases A through J).
4. **DOCUMENT:** Author all 30 markdown specifications with full schemas, schemas definitions, and clinical rationales.
5. **SELF-AUDIT:** Verify that every state, entity, and invariant requested in the contract is addressed without omissions.
6. **REPORT:** Synthesize findings into the 31-heading conclusion document (`105_PHASE_6_CONCLUSION.md`) and notify caller.
7. **STOP:** Complete Phase 6 without touching production runtime code.
