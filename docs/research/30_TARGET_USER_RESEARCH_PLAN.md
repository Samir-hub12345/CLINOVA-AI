# CLINOVA AI — Phase 3 Target Users Research Plan & Specification Methodology

> **Document ID:** `RES-30`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Healthcare Human Factors Research Group  

---

## 1. Executive Summary & Objective

Phase 3 transitions CLINOVA AI from the **adversarial architectural & innovation audit** completed in Phase 2 into a **rigorous, evidence-backed user-role and human-system interaction specification**.

The primary objective of Phase 3 is to establish an unshakeable, defensible user model prior to any interface engineering, backend implementation, or database migration:
> **Core Mandate:** Define exactly **WHO** uses CLINOVA, **WHY** they use it, **WHAT** clinical and operational decisions they execute, **WHAT** information they consume and supply, **WHAT** permission boundaries constrain them, **WHAT** failure modes threaten them, and **HOW** each role exercises **Meaningful Human Control (MHC)** over the continuous care pathway.

### 1.1 Guiding Core Principle
CLINOVA connects patient risk, evidence uncertainty, facility capability, system demand, and longitudinal outcomes to identify the **safest achievable care pathway** while keeping qualified healthcare professionals in ultimate medicolegal control. The user model must reflect frontline clinical reality—especially high-throughput, resource-constrained Indian public and private healthcare environments—rather than an idealized, frictionless academic environment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 3 RESEARCH WORKFLOW ARCHITECTURE                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: FOUNDATIONAL TAXONOMY ] ──> Define 8 Roles & 31 Dimensions       │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 2: MULTI-ENVIRONMENT MAPPING ] ──> Cross-examine 6 Target Settings  │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 3: MASTER CASE JOURNEY ] ──> Trace Roles Across 21 Lifecycle Stages │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 4: GOVERNANCE & CONTROL ] ──> Meaningful Human Control & RBAC       │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 5: SAFETY & EXCEPTIONS ] ──> Emergency, Failure & Privacy Analysis  │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 6: MVP SYNTHESIS ] ──> Core vs Supporting MVP Roles & Traceability  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Research Hierarchy & Evidence Taxonomy

To prevent subjective speculation and feature bloat, Phase 3 evaluates all user roles against an authoritative evidence hierarchy:

1. **Tier 1: Baseline Mandate:** Official BPUT Problem Statement (`B01` through `B18`).
2. **Tier 2: Statutory Indian Standards:**
   - Ministry of Health & Family Welfare (MoHFW) Indian Public Health Standards (IPHS 2022).
   - National Health Authority (NHA) & Ayushman Bharat Digital Mission (ABDM) User & Actor Specifications.
   - National Medical Commission (NMC) Registered Medical Practitioner (RMP) Regulations & Telemedicine Guidelines.
   - National Health Systems Resource Centre (NHSRC) Guidelines on Comprehensive Primary Health Care & Referral Protocols.
   - Indian Council of Medical Research (ICMR) Ethical Guidelines for AI in Healthcare (2023).
3. **Tier 3: Global Clinical Safety & Human Factors Norms:**
   - World Health Organization (WHO) Guidance on Ethics and Governance of AI for Health.
   - ISO 9241-210 (Human-Centred Design for Interactive Systems).
   - Emergency Severity Index (ESI) Implementation Handbook & Manchester Triage System (MTS).
4. **Tier 4: Audited Project Artefacts:** Phase 1 Product Source of Truth (`DOC-00` to `DOC-28`) and Phase 2 Research Conclusions (`RES-00` to `RES-24`).
5. **Tier 5: Peer-Reviewed Clinical Ergonomics Literature:** Studies from *The Lancet Global Health*, *JAMIA*, *BMJ Quality & Safety*, and *Annals of Emergency Medicine* examining physician burnout, alert fatigue, and triage error rates in low-resource settings.

### Evidence Quality Classification
Every finding, workflow stage, and user assumption is tagged:
- **`SUPPORTED`**: Confirmed by statutory regulation, empirical study, or explicit BPUT contract.
- **`PARTIAL`**: Documented in academic literature or guidelines but lacks uniform field implementation.
- **`UNKNOWN`**: Insufficient empirical data available; requires observational pilot validation.
- **`UNSUPPORTED`**: Hypothesis or marketing assertion explicitly disproven by real-world clinical practice.

---

## 3. Investigated User Groups (The 8 Candidate Roles)

Phase 3 investigates eight candidate user roles spanning primary care, logistics, recipient stakeholders, and operational governance:

1. **Primary Clinician / Medical Officer / Qualified Reviewer (`ROLE_CLINICIAN`):** Licensed MBBS physician, casualty medical officer (CMO), or specialist holding legal responsibility for diagnostic verification and pathway authorization.
2. **Nurse / Health Worker (`ROLE_NURSE` / `ROLE_HEALTH_WORKER`):** Staff Nurse, Auxiliary Nurse Midwife (ANM), or Accredited Social Health Activist (ASHA) conducting intake, vitals acquisition, checklist completion, and immediate acute escalation.
3. **Referral / Transfer Staff (`ROLE_REFERRAL_STAFF`):** Hospital transfer coordinator, emergency dispatch desk staff, or 108 ambulance liaison managing inter-facility logistics.
4. **Patient (`ROLE_PATIENT`):** The individual presenting with symptoms, answering clarifying questions, uploading medical records, and consuming approved discharge instructions.
5. **Caregiver / Patient Attendant (`ROLE_CAREGIVER`):** Family member or legal guardian acting on behalf of pediatric, elderly, unconscious, or incapacitated patients.
6. **Facility Administrator (`ROLE_FACILITY_ADMIN`):** Medical Superintendent, Chief Medical Officer, or Hospital Ops Manager configuring beds, equipment, shift rosters, and tracking department queues.
7. **System Administrator (`ROLE_SYSTEM_ADMIN`):** Infrastructure engineer managing deployment, system health, local AI runtime availability, user credentials, and security audit logs.
8. **Research / Evaluation User (`ROLE_RESEARCHER`):** Clinical informaticist, epidemiologist, or AI safety auditor running synthetic benchmarks, bias audits, and aggregated syndromic analysis.

---

## 4. The 31 Evaluation Dimensions per Role

To ensure total analytical completeness, each of the eight roles is subjected to a structured 31-point evaluation in `docs/research/31_USER_ROLE_ANALYSIS.md`:

```
 1. Role Name                          17. Uncertainty Requirements
 2. Real-World Responsibility          18. Emergency Responsibilities
 3. Primary Operating Environment      19. Referral Responsibilities
 4. Primary Goals                      20. Follow-up Responsibilities
 5. Main Jobs-To-Be-Done (JTBD)        21. Outcome Responsibilities
 6. Typical Operational Workflow       22. Privacy Sensitivity
 7. Information They Provide           23. Access Sensitivity
 8. Information They Consume           24. Primary Failure Scenarios
 9. Information They Verify            25. Permission Boundary Risks
10. Information They Modify            26. Human-Oversight Requirements
11. Authorized Decisions               27. Accessibility Requirements
12. Unauthorized Decisions             28. Device & Connectivity Constraints
13. Interacting AI Capabilities        29. Training & Digital Literacy Constraints
14. Visible AI Outputs                 30. Expected Frequency of Use
15. Restricted AI Controls             31. Consequences of Incorrect Support & Success Criteria
16. Evidence/Provenance Requirements
```

---

## 5. Investigated Operating Environments

User roles are evaluated across six distinct operational environments in `docs/research/33_ENVIRONMENT_USER_MATRIX.md`:

1. **Government Hospital (District Hospital / SDH / Medical College):** Extreme volume (500–2,000 OPD/day), severe queue congestion, multi-tier staff hierarchy, chaotic physical triage.
2. **Primary Health Centre (PHC / Ayushman Arogya Mandir):** Rural/semi-urban outpost, single Medical Officer, heavy ANM/ASHA reliance, limited diagnostics, intermittent power/internet, acute referral dependency.
3. **Public Health Camp (Mobile Outreach / Screening Camp):** Episodic pop-up camp, high throughput (300–800 patients in 6 hours), battery/tablet operation, offline requirement, high loss-to-follow-up risk.
4. **Company Clinic (Corporate / IT Park Health Centre):** Low acute volume (20–50/day), occupational health emphasis, high privacy sensitivity regarding employer data exposure, high digital literacy.
5. **Industrial Health Unit (Factory / Mining / Chemical Plant):** High hazard environment, acute industrial trauma, toxic exposures, strict statutory reporting (Factories Act 1948), fast-track specialty transfer.
6. **Campus Health Centre (University / Residential College):** High-frequency minor illness, contagious dorm outbreaks (dengue, gastroenteritis), student mental health crises, parent/guardian coordination.

---

## 6. Meaningful Human Control (MHC) Charter

A central failure of commercial CDSS and prior triage systems identified in Phase 2 is **"Fake Human-in-the-Loop" (Rubber-Stamping)**, where overloaded doctors blindly click "Accept" on AI suggestions under extreme time pressure.

Phase 3 defines the technical and behavioral architecture for **Meaningful Human Oversight** across nine mandatory capabilities:
1. **Visibility:** Immediate, un-occluded view of extracted data, confidence scores, and source provenance.
2. **Understanding:** Transparent trajectory slope ($\Delta R_t / \Delta t$) and uncertainty metrics ($U_t$) instead of uncalibrated probabilistic guesses.
3. **Authority:** Medicolegal sign-off is exclusive to licensed physicians; AI has zero autonomous ordering or disposition rights.
4. **Ability to Intervene:** Clinicians can pause queues, pull emergency cases ahead, or freeze automated pipelines.
5. **Ability to Modify:** Clinicians can edit, re-classify, or delete any discrete clinical entity.
6. **Ability to Reject:** Clinicians can discard AI triage drafts or diagnostic notes with a single action.
7. **Ability to Override:** Clinicians can override algorithmic pathway recommendations; deterministic red flags strictly bound AI text.
8. **Reason Capture:** Friction-calibrated justification capture when overriding recommendations or correcting extractions.
9. **Audit Trail:** Tamper-evident, cryptographically linked append-only ledger recording all overrides and edits.

---

## 7. Scope Boundaries & Anti-Scope Guardrails

### 7.1 Strictly Included in Phase 3
- Exhaustive empirical research and user-role specification.
- Granular mapping of all 8 roles across 31 dimensions.
- End-to-end Master Case journey tracing by role.
- Six-environment operational matrix.
- Conceptual 16-verb Permission Matrix (RBAC).
- Meaningful Human Control framework and anti-rubber-stamping ergonomics.
- Patient and caregiver access and boundary rules.
- Emergency role and fast-track protocol.
- User failure and exception matrix (22 distinct clinical failure cases).
- Privacy, safety, and PII containment model.
- User Need → Product Traceability matrix.
- Hackathon MVP role rationalization and minimization decision.

### 7.2 Strictly Excluded from Phase 3 (Anti-Scope)
- ❌ **No Phase 4 or subsequent roadmap phase execution.**
- ❌ **No production UI or frontend component implementation.**
- ❌ **No backend API routes, endpoints, or controllers.**
- ❌ **No database schema creation, table migrations, or ORM models.**
- ❌ **No authentication or authorization implementation (OAuth, JWT, RBAC code).**
- ❌ **No AI model integration or prompt execution.**
- ❌ **No cloud or on-premise infrastructure deployment.**
- ❌ **No modification to existing application code.**
- ❌ **No presentation decks or marketing artifacts.**

Phase 3 produces strictly **documentation and research artifacts** under `docs/research/`, terminating in the status **READY FOR HUMAN REVIEW**.
