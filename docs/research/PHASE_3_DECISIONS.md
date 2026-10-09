# CLINOVA AI — Phase 3 Architectural & User Specification Decision Log

> **Document ID:** `DEC-PHASE-03`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Governance Group  

---

## 1. Executive Summary

This document establishes the official **Decision Log** capturing all fundamental architectural, ergonomic, and governance decisions formulated during Phase 3 (Target Users Research & User-Role Specification).

Every decision records its unique Identifier, Context, Alternatives Considered, Chosen Decision, Clinical/Technical Rationale, and Evidence Trace.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 3 DECISION SUMMARY LOG                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  DEC-301: Exhaustive 8-Role & 31-Dimension Evaluation Framework             │
│  DEC-302: Six-Environment Healthcare Grounding (Anti-Urban-Bias)            │
│  DEC-303: 21-Stage Single Master Case Continuous Lifecycle Tracing         │
│  DEC-304: 9-Pillar Meaningful Human Control & Rejection of Fake-HITL        │
│  DEC-305: 16-Verb RBAC Model & Exclusive Clinician Disposition Monopoly     │
│  DEC-306: Strict Patient/Caregiver Boundaries (Concealing Differentials)   │
│  DEC-307: Emergency Non-Equivalence Law & Dedicated Acute Pathways          │
│  DEC-308: 22-Scenario User Failure & Clinical Exception Matrix              │
│  DEC-309: Privacy, Consent Lifecycle & 24-Hour Ephemeral Media Purge        │
│  DEC-310: Bidirectional User Need to Product Traceability Matrix            │
│  DEC-311: Hackathon MVP Role Rationalization & 3-Core-UI Minimization       │
│  DEC-312: Strict Zero-Code Implementation Guardrail for Phase 3             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Decision Records

### Decision DEC-301: Exhaustive 8-Role & 31-Dimension Evaluation Framework
- **Context:** User specification required defining who uses CLINOVA, why they use it, and what permissions they hold without superficial stereotyping.
- **Alternatives Considered:**
  1. *High-level 3-role persona summary (Doctor, Nurse, Patient).* (Rejected: Misses referral bottlenecks, administrative governance, and research audits).
  2. *Exhaustive 8-role analysis across 31 structured dimensions.* (**Accepted**).
- **Chosen Decision:** Subject all eight candidate roles (`Clinician`, `Nurse`, `Referral Staff`, `Patient`, `Caregiver`, `Facility Admin`, `System Admin`, `Researcher`) to a 31-point evaluation in `RES-31`.
- **Rationale:** Ensures complete clinical ergonomics, privacy, and medicolegal analysis before any interface or schema design begins.
- **Trace:** `RES-30`, `RES-31`; NMC Regulations 2023.

---

### Decision DEC-302: Six-Environment Grounding (Anti-Urban Bias)
- **Context:** Many healthcare software products fail because they assume high-speed fiber internet, multi-monitor setups, and abundant specialists.
- **Alternatives Considered:**
  1. *Design solely for an urban Tertiary Government Hospital.* (Rejected: Causes complete failure when deployed in rural PHCs or health camps).
  2. *Cross-map every role across 6 distinct environments.* (**Accepted**).
- **Chosen Decision:** Formulate explicit operational constraints across: (1) Government Hospital, (2) PHC, (3) Public Health Camp, (4) Company Clinic, (5) Industrial Health Unit, and (6) Campus Health Centre in `RES-33`.
- **Rationale:** Forces the product architecture to be 100% offline-tolerant, multilingual (Odia/Hindi/English), and capable of running on low-resource hardware.
- **Trace:** `RES-33`; MoHFW IPHS 2022; NHSRC PHC Guidelines.

---

### Decision DEC-303: 21-Stage Single Master Case Continuous Lifecycle Tracing
- **Context:** Legacy hospital software creates disconnected records across departments (Registration ticket $\ne$ Triage slip $\ne$ Doctor note $\ne$ Referral slip).
- **Alternatives Considered:**
  1. *Allow each user role to create independent department-specific forms.* (Rejected: Fractures patient trajectory; causes duplicate entry errors).
  2. *Trace every role's interactions across a single continuous 21-stage Master Case lifecycle.* (**Accepted**).
- **Chosen Decision:** Mandate the **Single Master Case Invariant**: every user action, vital sign, checklist item, and clinical verification appends directly to the unified `CaseModel` in `RES-32`.
- **Rationale:** Enables continuous trajectory tracking ($\Delta R_t / \Delta t$) and eliminates fractured records.
- **Trace:** `RES-32`; Phase 1 `DOC-06`, `DOC-07`.

---

### Decision DEC-304: Meaningful Human Control (MHC) & Rejection of Fake-HITL
- **Context:** In high-volume clinics, "Human-in-the-Loop" degrades into doctors clicking "Approve AI" without reading due to cognitive overload.
- **Alternatives Considered:**
  1. *Standard binary modal ("Approve AI Triage Note: Yes / No").* (Rejected: Promotes dangerous automation bias and rubber-stamping).
  2. *Architectural 9-pillar Meaningful Human Control model with cognitive forcing functions.* (**Accepted**).
- **Chosen Decision:** Implement visibility (provenance in $< 300$ms), explainable uncertainty ($U_t$), in-place editing, one-click draft rejection, and friction-calibrated reason capture in `RES-35`.
- **Rationale:** Preserves physician autonomy, complies with WHO and ICMR ethical guidelines, and protects clinical safety.
- **Trace:** `RES-35`; WHO AI Ethics 2021; ICMR AI Guidelines 2023.

---

### Decision DEC-305: 16-Verb RBAC Model & Exclusive Clinician Monopoly on Dispositions
- **Context:** Defining the conceptual security model governing clinical and administrative operations.
- **Alternatives Considered:**
  1. *Allow senior triage nurses or algorithms to issue routine discharges.* (Rejected: Illegal under Indian law; severe medicolegal risk).
  2. *Strict Clinician Monopoly: Only licensed physicians can execute binding clinical dispositions.* (**Accepted**).
- **Chosen Decision:** Establish a 16-verb permission matrix in `RES-34`. `DISCHARGE`, `ADMIT`, `REFER`, and `OVERRIDE` are legally and architecturally exclusive to `ROLE_CLINICIAN`.
- **Rationale:** Maintains compliance with the NMC Code of Medical Ethics and establishes clear medicolegal liability.
- **Trace:** `RES-34`; NMC Professional Conduct Regulations 2023; BPUT B18.

---

### Decision DEC-306: Strict Patient/Caregiver Boundaries (Concealing Differentials)
- **Context:** Determining what clinical data should be visible to patients and family caregivers.
- **Alternatives Considered:**
  1. *Full transparency: Expose all raw AI differential diagnoses and uncertainty metrics to the patient.* (Rejected: Causes acute panic, unguided self-medication, and confusion).
  2. *Curated Patient View: Display only clinician-approved diagnosis, plain vernacular instructions, pictographic medication schedules, and red-flag return warnings.* (**Accepted**).
- **Chosen Decision:** Conceal probabilistic differential lists, raw $U_t$ metrics, and internal clinician scratchpads from patient/caregiver views in `RES-36`.
- **Rationale:** Prioritizes patient psychological safety and clinical clarity while preserving physician-patient communication.
- **Trace:** `RES-36`; DPDP Act 2023; Indian Medical Informatics Norms.

---

### Decision DEC-307: Emergency Non-Equivalence Law & Dedicated Acute Pathways
- **Context:** Emergency and surgical triage cannot be treated as a routine outpatient form with high priority.
- **Alternatives Considered:**
  1. *Use standard 40-field intake form with a red "STAT" badge.* (Rejected: Documentation delays resuscitation during the Golden Hour).
  2. *Dedicated Emergency Fast-Track and OT Fast-Track pathways.* (**Accepted**).
- **Chosen Decision:** Formulate dedicated acute pathways in `RES-37` that provision cases in $< 200$ms, require only 30-second ABCD vitals, suppress non-essential narrative, and surface procedure-relevant surgical dossiers.
- **Rationale:** Maximizes patient survival during acute cardiovascular, septic, and trauma emergencies.
- **Trace:** `RES-37`; Phase 1 `DOC-16`; WHO Essential Trauma Guidelines.

---

### Decision DEC-308: 22-Scenario Comprehensive Failure & Exception Matrix
- **Context:** System specification must account for real-world operational breakdowns.
- **Alternatives Considered:**
  1. *Generic 3-case error handling (Server error, Invalid input, 404).* (Rejected: Inadequate for clinical safety).
  2. *Exhaustive 22-scenario clinical and infrastructural exception matrix.* (**Accepted**).
- **Chosen Decision:** Map 22 distinct failure modes across `Actor` $\to$ `Failure` $\to$ `Risk` $\to$ `System Behavior` $\to$ `Human Response` $\to$ `Audit Requirement` in `RES-38`.
- **Rationale:** Guarantees predictable, safe fail-soft behavior during power blackouts, unconscious arrivals, OCR smudges, and referral rejections.
- **Trace:** `RES-38`; ISO/IEC 25010; Supreme Court Emergency Precedents.

---

### Decision DEC-309: Privacy, Consent Lifecycle & 24-Hour Ephemeral Media Purge
- **Context:** Processing audio voiceprints and physical medical document photos carries high PII leak risks.
- **Alternatives Considered:**
  1. *Indefinite storage of raw audio recordings and document photos.* (Rejected: Severe privacy liability under DPDP 2023).
  2. *Strict 24-Hour Ephemeral Retention Policy.* (**Accepted**).
- **Chosen Decision:** Mandate automated cryptographic purging of raw audio files and scanned document images 24 hours post-consultation (`B16`), retaining only discrete verified clinical entities in `RES-39`.
- **Rationale:** Delivers zero-data-hoarding compliance with the DPDP Act 2023 and BPUT requirement `B16`.
- **Trace:** `RES-39`; DPDP Act 2023; BPUT B15, B16.

---

### Decision DEC-310: Bidirectional User Need to Product Traceability Matrix
- **Context:** Ensuring every product requirement traces to an empirical user problem, and vice-versa.
- **Alternatives Considered:**
  1. *Unlinked product feature list.* (Rejected: Fails auditability and project governance standards).
  2. *10-dimension bidirectional traceability matrix.* (**Accepted**).
- **Chosen Decision:** Author `RES-40` establishing end-to-end traceability for 14 core user needs, connecting them to verification tests and future roadmap phases (Phases 4 through 8).
- **Rationale:** Guarantees zero orphaned features and 100% research groundedness.
- **Trace:** `RES-40`; Phase 2 `RES-23`.

---

### Decision DEC-311: Hackathon MVP Role Rationalization & 3-Core-UI Minimization
- **Context:** Determining the role set for the hackathon demonstration without engineering bloat or presentation failure.
- **Alternatives Considered:**
  1. *Implement all 8 roles as independent web portals with separate authentication logins.* (Rejected: Excessive demo overhead, high failure risk during live judging).
  2. *Consolidate into 3 Core Visual Interfaces with supporting roles integrated as modes and drawers.* (**Accepted**).
- **Chosen Decision:** Establish the **Minimum Viable Role Set** in `RES-41`: (1) Patient/Caregiver Intake Portal, (2) Nurse Triage Workstation, and (3) Doctor Reviewer Workbench, with Referral Desk and Facility Settings integrated as contextual tabs/drawers. Remove non-triage roles (Pharmacist, Billing, Lab Tech).
- **Rationale:** Enables a complete, convincing 4-minute demonstration of all 18 BPUT requirements and 10 innovation capabilities without login friction.
- **Trace:** `RES-41`; BPUT B01–B18.

---

### Decision DEC-312: Strict Zero-Code Implementation Guardrail for Phase 3
- **Context:** Adhering strictly to the atomic phase boundary of Phase 3.
- **Alternatives Considered:**
  1. *Begin drafting React components or FastAPI endpoints for user roles.* (Rejected: Violates atomic phase mandate; premature implementation before user specification audit).
  2. *Strict zero-code policy: Author documentation artifacts only.* (**Accepted**).
- **Chosen Decision:** Zero production UI, backend routes, database migrations, authentication logic, or AI integrations are executed. Phase 3 produces documentation exclusively and concludes with status **READY FOR HUMAN REVIEW**.
- **Rationale:** Protects architectural integrity and enforces disciplined phase progression.
- **Trace:** Phase 3 Charter; `RES-30`, `RES-42`.
