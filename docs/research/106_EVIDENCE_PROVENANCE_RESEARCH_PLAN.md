# CLINOVA AI — Evidence, Provenance, Verification & Uncertainty Foundation Research Plan

> **Document ID:** `RES-106`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Executive Summary & Research Mandate

Clinical intelligence systems routinely fail in real-world healthcare environments not because algorithmic models lack statistical capability, but because **epistemic provenance is collapsed or ignored**. In standard electronic health records and conversational AI wrappers:
1. Subjective patient assertions are conflated with calibrated sensor measurements.
2. Machine-generated optical character recognition (OCR) and speech-to-text extractions are silently promoted to clinical facts.
3. Conflicting data points are destructively overwritten by the most recent entry.
4. Epistemic uncertainty ($U_t$) is confused with physiological acuity ($R_t$).
5. Downstream algorithmic inferences are presented without transparent lineage back to raw perceptual media.

**Phase 7** establishes the formal specification and validation of the **CLINOVA Evidence, Provenance, Verification & Uncertainty Foundation**. This layer answers ten non-negotiable safety questions for every clinical datum across the entire patient lifecycle:
- *Where did this fact come from?*
- *Who entered it?*
- *When was it captured versus when did the underlying physiological event occur?*
- *How was it transformed, translated, or normalized?*
- *Was it verified, and by whom?*
- *What other evidence in the record directly contradicts or conflicts with it?*
- *Is it patient-reported, staff-verified, clinician-approved, AI-inferred, or system-derived?*
- *How reliable is the source, and what is its calibrated confidence?*
- *What must a Registered Medical Practitioner (RMP) see before acting upon it?*
- *Can this fact be safely relied upon after raw source media is purged under statutory retention policies?*

---

## 2. Atomic Phase Scope & Boundary Conditions

Phase 7 is strictly an architectural, mathematical, and data-modeling specification phase. To preserve phase boundaries:
- **Phase 7 ONLY:** Does not initiate Phase 8 (Model Fine-Tuning & Pipeline Integration) or any subsequent implementation phase.
- **No Production Code:** Zero application code is committed to `backend/app` or `frontend/src`.
- **No Database Migrations Applied:** No Alembic or PostgreSQL/SQLite migration commands are executed against active database environments.
- **No UI Implementation:** The user interface experience is specified conceptually (interaction models, bounding box overlays, conflict widgets) without frontend component construction.
- **No Production AI Integration:** Model schemas, prompt task versions, and inference constraints are specified without running live LLM/SLM inference services.
- **No Deployment:** Artifacts remain authoritative architectural and health informatics specifications within `docs/research/`.

---

## 3. Statutory, Regulatory & Informatics Source Reconciliation

Phase 7 builds upon the foundational research of Phases 1 through 6, synthesizing Indian public health jurisprudence with international clinical informatics standards:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 7 UPSTREAM BASELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 1 Product Definition (DOC-00 – DOC-28)                                │
│  Phase 2 Innovation & Gap Audits (RES-00 – RES-24)                          │
│  Phase 3 Target-User & Role Specifications (RES-30 – RES-42)                │
│  Phase 4 Healthcare Environment Specifications (RES-43 – RES-56)             │
│  Phase 5 Master Patient Journey 27-State Machine (RES-57 – RES-77)          │
│  Phase 6 Master Case & Canonical Relational Schema (RES-78 – RES-105)        │
│  BPUT Smart Odisha Problem Statement (Rural Emergency Decision Support)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STATUTORY & INFORMATICS JURISPRUDENCE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  • NMC RMP Regulations 2023 (Reg 27: RMP Monopoly; Reg 28: 3-Year Records)   │
│  • Bharatiya Sakshya Adhiniyam (BSA) 2023 Sec 63 / IEA 1872 Sec 65B (Hash)  │
│  • Digital Personal Data Protection (DPDP) Act 2023 (Sec 4, 6, 7, 9)        │
│  • IPHS 2022 Guidelines (7-Year Medico-Legal Records; PHC/CHC Equipment)    │
│  • W3C PROV-O Recommendation (wasDerivedFrom, wasAttributedTo, wasGenBy)    │
│  • HL7 FHIR R5 (Provenance, Observation, Condition, VerificationResult)      │
│  • SNOMED CT / LOINC Standard Vocabularies & Concept Normalization          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Methodological Workflow & Execution Pipeline

The investigation follows an eight-stage sequential validation pipeline:

```
  1. ANALYZE
     ├── Extract evidence semantics from Phase 6 relational schemas (RES-83, RES-84)
     └── Catalog all modalities: Voice, Image, OCR, Manual, Device, AI, System
         │
         ▼
  2. RESEARCH
     ├── Evaluate acoustic uncertainty, OCR degradation, and linguistic code-switching
     └── Establish calibration standards for quantitative and qualitative confidence
         │
         ▼
  3. MODEL
     ├── Formalize 8 Source Classes, 6 Epistemic States, and 4 Verification Tiers
     └── Specify full 9-stage Provenance Chain and conflict resolution event models
         │
         ▼
  4. VALIDATE
     ├── Verify SQLite WAL and PostgreSQL compatibility for provenance tables
     └── Test bi-directional traceability across the 27 journey states
         │
         ▼
  5. ADVERSARIAL AUDIT
     ├── Stress-test 14 adversarial safety scenarios (Scenarios A through N)
     └── Exhaustively analyze 25 real-world failure and exception modes
         │
         ▼
  6. DOCUMENT
     ├── Author all 30 authoritative Phase 7 markdown specifications in docs/research/
     └── Ground every claim in statutory, clinical, or technical literature
         │
         ▼
  7. SELF-AUDIT
     ├── Verify 38 strict phase compliance checklist items
     └── Reconcile all terminology against BSA 2023, DPDP 2023, and NMC 2023
         │
         ▼
  8. FINAL REPORT & STOP
     ├── Publish RES-133 Phase 7 Conclusion with 37 mandatory reporting sections
     └── Mark final status: READY FOR HUMAN REVIEW (Cease execution)
```

---

## 5. Key Research Questions & Sub-Topics

To ensure exhaustive domain coverage, Phase 7 investigates and formally resolves fifteen critical sub-topics:

1. **Source Disambiguation:** How to distinguish subjective narrative, nurse measurement, machine perception, and AI synthesis without conflating source with truth? (`RES-107`)
2. **Epistemic Dynamics:** What state machine governs `KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`, and `INFERRED`, and why must `INFERRED \neq VERIFIED` be an absolute system invariant? (`RES-108`)
3. **End-to-End Lineage:** How to trace an observation from acoustic wave or optical pixel down to clinical disposition and long-term health outcome? (`RES-109`)
4. **Degraded Perceptual Anchoring:** How to represent spatial bounding boxes and acoustic time intervals under noisy, smudged, rotated, or overlapping real-world conditions? (`RES-110`, `RES-111`)
5. **Human Attribution:** How to track manual data entry across patients, caregivers, community health workers (ASHAs), triage nurses, and physicians without adding clinical friction? (`RES-112`)
6. **Acuity-Proportional Review:** How to structure verification across four risk tiers (`NO_REVIEW`, `STAFF_REVIEW`, `CLINICIAN_REVIEW`, `DUAL_REVIEW`) so low-risk data flows efficiently while high-risk facts require mandatory human sign-off? (`RES-113`)
7. **Conflict Persistence:** How to store contradictory facts side-by-side without silent overwrites, enabling high-acuity values to act as safety tripwires without being falsely declared verified? (`RES-114`)
8. **Decoupled Quality & Confidence:** Why must source quality (physical integrity) and model confidence (probabilistic output) never be collapsed into a single metric? (`RES-115`)
9. **Epistemic Uncertainty ($U_t$):** How do data gaps, conflicting evidence, and low-quality perceptual sources mathematically alter the uncertainty score $U_t \in [0, 1]$? (`RES-116`)
10. **Temporal Quad-Time:** Why must every clinical record decouple Event Time, Capture Time, Ingestion Time, Verification Time, and Decision Time? (`RES-118`)
11. **Transformation Lineage:** How to ensure translations, unit conversions, and LLM extractions remain completely reversible back to raw source text? (`RES-119`)
12. **AI Advisory Guardrails:** How to guarantee that AI inferences remain legally and architecturally advisory under NMC Regulation 27? (`RES-120`)
13. **Deterministic System Derivations:** How to trace physiological scores (NEWS2, Shock Index) back to the exact snapshot of input vitals? (`RES-121`)
14. **Post-Purge Hash Preservation:** How to maintain legal chain-of-custody and audit integrity when raw multimedia files are purged under DPDP Act storage limitation rules? (`RES-125`)
15. **Offline Provenance Merging:** How to prevent UUID collisions, logical timestamp inversion, and provenance detachment when disconnected rural edge tablets synchronize with cloud clusters? (`RES-126`, `RES-127`)

---

## 6. Deliverable Inventory

Phase 7 commits exactly 30 authoritative markdown research documents under `docs/research/`:
- `RES-106`: Evidence & Provenance Research Plan
- `RES-107`: Evidence Source Model
- `RES-108`: Epistemic State Model
- `RES-109`: Provenance Chain Model
- `RES-110`: OCR Provenance Model
- `RES-111`: Voice Provenance Model
- `RES-112`: Manual Entry Provenance Model
- `RES-113`: Verification Model
- `RES-114`: Evidence Conflict Model
- `RES-115`: Evidence Quality & Confidence Model
- `RES-116`: Uncertainty Provenance Model
- `RES-117`: Evidence Freshness Model
- `RES-118`: Temporal Provenance Model
- `RES-119`: Transformation Lineage Model
- `RES-120`: AI Inference Provenance Model
- `RES-121`: System-Derived Provenance Model
- `RES-122`: Evidence-to-Decision Traceability Model
- `RES-123`: Report Provenance Model
- `RES-124`: Provenance UI Conceptual Specification
- `RES-125`: Retention & Purge Provenance Model
- `RES-126`: Offline Edge Provenance Model
- `RES-127`: Provenance Security & Tamper Resistance Model
- `RES-128`: Provenance Permission & Access Control Model
- `RES-129`: Evidence Failure & Exception Matrix (25 Scenarios)
- `RES-130`: Adversarial Stress Tests (Scenarios A through N)
- `RES-131`: Evidence Data Integrity Invariants (`INV-PROV-01` to `INV-PROV-18`)
- `RES-132`: Comprehensive Evidence Traceability Matrix
- `RES-133`: Phase 7 Final Conclusion Report (37 Mandated Sections)
- `SOURCES_PHASE_7.md`: Authoritative Evidence & Informatics Literature Inventory
- `PHASE_7_DECISIONS.md`: Formal Architectural Decision Log (Decisions 7.1 – 7.16)

---

## 7. Operational Standards & Verification Gate

The research adheres to strict verification criteria:
- Every external clinical and legal claim is explicitly cross-referenced to `SOURCES_PHASE_7.md`.
- No simulated or fabricated machine-learning performance metrics are reported.
- Modern Indian statutory terminology (Bharatiya Sakshya Adhiniyam 2023, Digital Personal Data Protection Act 2023, NMC RMP Regulations 2023) is used throughout.
- All 18 Evidence Integrity Invariants are mathematically specified and cross-checked against Phase 6 relational schemas.
- Final phase status must conclude as `READY FOR HUMAN REVIEW`.
