# CLINOVA AI — Phase 5 Master Patient Journey Research Plan & Specification Methodology

> **Document ID:** `RES-57`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Objective

Phase 5 represents the definitive operational and clinical synthesis of the CLINOVA AI platform. Having completed the **Product Definition & Architecture Foundation** (Phase 1), the **Clinical AI & Health Informatics Innovation Audit** (Phase 2), the **Target User Roles & Human Control Specification** (Phase 3), and the **Target Environments & Operational Context Specification** (Phase 4), Phase 5 models the living, end-to-end reality of clinical care delivery:

$$\mathbf{THE\ MASTER\ PATIENT\ JOURNEY}$$

The primary objective of Phase 5 is to establish with empirical defensibility, mathematical precision, and clinical rigor:
> **Core Objective:** Specify the complete CLINOVA Master Patient Journey from initial presentation through clinical stabilization, disposition, referral, ward admission, surgical escalation, and longitudinal outcome feedback.

### 1.1 The Seven Pillars of the Journey
The journey is strictly architected to be:
1. **CONTINUOUS:** Triage is NOT modeled as an isolated, transient gatekeeping event. Care is a continuous, evolving trajectory where patient state updates dynamically across multiple handoffs.
2. **STATEFUL:** Every clinical entity, physiological observation, and administrative transition is tracked in a formally specified, deterministic finite state machine.
3. **HUMAN-CONTROLLED:** Registered healthcare professionals retain absolute, uncompromised monopoly over diagnostic formulation, prescription orders, and clinical disposition. The AI is advisory, transparent, and friction-calibrated.
4. **EVIDENCE-AWARE:** Every piece of extracted clinical data carries immutable provenance pointers to its raw physical origin (audio timestamp, OCR crop, or manual entry).
5. **UNCERTAINTY-AWARE:** Missing, ambiguous, or unverified information is mathematically scored via Epistemic Uncertainty ($U_t$). Missing clinical data is NEVER treated as negative or normal.
6. **ENVIRONMENT-AWARE:** The operational flow adapts to local facility constraints (PHC vs District Hospital vs Health Camp vs Industrial Clinic) without code fragmentation.
7. **RESOURCE-AWARE:** Clinical recommendations are grounded in verified real-time facility capabilities ($\text{FACILITYGRAPH}$) to prevent fatal "blind transfers".
8. **OUTCOME-AWARE:** The platform tracks what happens *after* the disposition, capturing real clinical endpoints to continuously close the feedback loop for $\text{CAREGRAPH}$ and $\text{SIGNALGRAPH}$.

---

## 2. Foundational Core Invariant

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA CORE MASTER INVARIANT                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                            ONE MASTER CASE                                  │
│                                   │                                         │
│                                   ▼                                         │
│                       ONE CONTINUOUS JOURNEY                                │
│                                   │                                         │
│                                   ▼                                         │
│                      MULTIPLE HUMAN HANDOFFS                                │
│                                   │                                         │
│                                   ▼                                         │
│                      MULTIPLE CARE PATHWAYS                                 │
│                                   │                                         │
│                                   ▼                                         │
│                      ONE AUDITABLE HISTORY                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **The Single Master Case Law:**  
> Under NO circumstances shall any subsystem, healthcare worker, triage desk, emergency fast-track, ward station, or referral desk spawn an isolated, disconnected secondary record for the same patient encounter.  
> Voice audio, OCR document crops, bedside nursing vitals, doctor review notes, facility capability checks, referral packets, and post-discharge outcomes MUST attach directly to the single, cryptographically auditable Master Case (`case_id`).

---

## 3. Methodology & Research Structure

Phase 5 synthesizes 56 prior research artifacts and 29 product specification documents across 12 analytical research axes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 5 RESEARCH ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ AXIS 1: DUAL-TRACK ENTRY MODEL ] ──> Regular vs Emergency Decoupling     │
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 2: REGULAR INTAKE & EXTRACTION ] ──> Multimodal Ingestion Pipeline  │
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 3: SUFFICIENCY & FRONTLINE WORKFLOW ] ──> Nurse Point-of-Care Vitals│
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 4: CARE ENGINES & DOCTOR WORKBENCH ] ──> CAREGRAPH & Doctor Verification
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 5: DISPOSITION & PATHWAY BRANCHES ] ──> Routine / Ward / Referral / OT
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 6: STATE MACHINE & TRANSITION MATRIX ] ──> 27 Canonical States      │
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 7: RESILIENCE & PERMISSION GOVERNANCE ] ──> 30 Failures & Role RBAC │
│             │                                                               │
│             ▼                                                               │
│  [ AXIS 8: MVP RATIONALIZATION & CLOSURE ] ──> PHC-to-Hospital Demo Flow    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Research Axes & Deliverable Mapping
- **Axis 1: Macro Journey & Dual-Track Entry (`RES-58`, `RES-59`, `RES-60`):** Decouples regular scheduled/walk-in patient flows from acute emergency fast-tracks. Formalizes the principle: *"Clinical Resuscitation BEFORE Administrative Completion"*.
- **Axis 2: State-Transition Modeling (`RES-61`, `RES-62`):** Formalizes a 27-state deterministic state machine. Evaluates every candidate state (`KEEP`, `MERGE`, `SPLIT`, `REMOVE`, `ADD`) and documents all state transitions, triggers, actors, and fallback states.
- **Axis 3: Epistemic Information Sufficiency (`RES-63`):** Defines mathematical criteria for information completeness, categorizing patient data into 6 operational states (`SUFFICIENT`, `PARTIALLY_SUFFICIENT`, `INSUFFICIENT`, `CONFLICTING`, `UNRELIABLE`, `EMERGENCY_OVERRIDDEN`).
- **Axis 4: Multi-Graph Engine Coupling (`RES-64`, `RES-65`, `RES-66`):** Maps the precise points in the patient journey where $\text{CAREGRAPH}$, $\text{FACILITYGRAPH}$, and the $\text{ORCHESTRATION}$ engine are instantiated, updated, queried, and verified.
- **Axis 5: Detailed Post-Doctor Pathways (`RES-67`, `RES-68`, `RES-69`, `RES-70`):** Deep dives into Routine Home Care & Scheduled Calendar Follow-Up, Inpatient Ward Admission, Inter-Facility Referral & Transport, and Emergency Operation Theatre (OT) Fast-Track.
- **Axis 6: Closed-Loop Outcome Architecture (`RES-71`):** Delineates Planned Action vs Actual Clinician Decision vs Real World Clinical Endpoint, feeding telemetry into $\text{SIGNALGRAPH}$.
- **Axis 7: Failure Modes, Exceptions & Permissions (`RES-72`, `RES-73`):** Catalogs 30 infrastructure, clinical, and human failure modes with concrete recovery behaviors, alongside role-based permission boundaries.
- **Axis 8: Environmental Modulation & Hackathon MVP Corridor (`RES-74`, `RES-75`, `RES-76`, `RES-77`):** Analyzes journey invariants across 6 environments, defines the PHC $\to$ District Hospital hackathon demonstration corridor, and provides end-to-end traceability.

---

## 4. Source Hierarchy & Statutory Reconciliation

Phase 5 reconciles and grounds all workflow specifications in authoritative standards:
1. **Statutory Clinical Guidelines:**
   - Indian Public Health Standards (IPHS 2022) for District Hospitals and Primary Health Centres.
   - ICMR Guidelines for AI in Healthcare (2023) — Principle of Autonomy, Safety, and Human Oversight.
   - WHO Essential Emergency and Critical Care (EECC) Framework.
   - Emergency Severity Index (ESI Version 4) Implementation Handbook.
   - WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out).
2. **Statutory Legal & Privacy Standards:**
   - Digital Personal Data Protection (DPDP) Act, 2023 — Purpose limitation, explicit parental consent, and data fiduciary duties.
   - National Medical Commission (NMC) Registered Medical Practitioner Regulations (2023).
   - Supreme Court of India emergency health rulings (*Paschim Banga Khet Mazdoor Samity v. State of West Bengal*, AIR 1996 SC 2426 — Constitutional mandate that lack of beds cannot justify turning away emergency patients without stabilization).
3. **Internal Architectural Truths:**
   - Phase 1 Product Definition & Technical Architecture (`DOC-00` through `DOC-28`).
   - Phase 2 Scientific & Engineering Gap Audits (`RES-00` through `RES-24`).
   - Phase 3 Target User Roles, Human Control & Break-Glass Models (`RES-30` through `RES-42`).
   - Phase 4 Target Environments & Environmental Failure Models (`RES-43` through `RES-56`).

---

## 5. Execution Rules & Scope Boundaries

As an authoritative, non-generative Phase 5 specification:
- **Phase 5 Only:** All work is confined to journey analysis, state-machine formulation, safety verification, and architectural documentation.
- **Zero Code Modification:** No production UI code (`frontend/`), backend business logic (`backend/`), or database schema scripts shall be created or altered.
- **No Autonomous Agency:** AI components remain strictly advisory throughout the journey. Under no condition can the system independently authorize medical discharge, order invasive surgery, or dispatch emergency patient transfers without licensed clinician sign-off.
- **Final Status:** The completion status shall be strictly reported as `READY FOR HUMAN REVIEW`.
