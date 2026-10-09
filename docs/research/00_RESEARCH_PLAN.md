# CLINOVA AI — Phase 2 Research Plan & Audit Methodology

> **Document ID:** `RES-00`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  
> **Authors:** Clinical AI Research Team & Systems Architecture Group  

---

## 1. Executive Summary & Audit Purpose

Phase 2 constitutes the **rigorous adversarial audit** of the product assumptions, clinical claims, and architectural models established during Phase 1 of CLINOVA AI.

The primary directive of Phase 2 is **not** to uncritically defend CLINOVA's uniqueness, but rather to **actively attempt to disprove its novelty** against established literature, commercial products, open-source repositories, and government health platforms globally and within India.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 2 RESEARCH & AUDIT WORKFLOW                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: FOUNDATION ] ──> Establish Sources of Truth & Evidence Taxonomy  │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 2: DISPROVE ]   ──> Map Existing Commercial & Academic Solutions     │
│             │               (Triage, Scribes, Referral, Capacity, Systems)  │
│             ▼                                                               │
│  [ STEP 3: CONTEXT ]    ──> Deep-Dive India Healthcare & Target Environments│
│             │               (ABDM, eSanjeevani, IHIP, PHC/Hospitals)         │
│             ▼                                                               │
│  [ STEP 4: PILLARS ]    ──> Grill the 4 Graphs & Orchestration Engine       │
│             │               (CareGraph, FacilityGraph, SignalGraph, Orch)   │
│             ▼                                                               │
│  [ STEP 5: SYNTHESIS ]  ──> Defensible Contribution & Traceability Matrices │
│             │                                                               │
│             ▼                                                               │
│  [ STEP 6: VERDICT ]    ──> Final Innovation Decisions:                     │
│                             KEEP / MODIFY / REMOVE / FUTURE                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Research Hierarchy & Sources of Truth

In accordance with Phase 2 contract directives, evidence is collected and weighted strictly across eight ranked tiers:

1. **Official BPUT Problem Statement:** Mandatory baseline operational requirements (`B01`–`B18`).
2. **Phase 1 CLINOVA Product Definition Documents:** System contracts (`DOC-00` through `DOC-28`).
3. **Legacy CLINOVA Archive:** Context on historical prototype code and architectural iterations.
4. **Official Government & Health-System Documentation:** Ministry of Health & Family Welfare (MoHFW), National Health Authority (NHA / ABDM), World Health Organization (WHO), US FDA, UK NHS Digital.
5. **Peer-Reviewed Academic Literature:** PubMed, IEEE, ACM, Nature Medicine, The Lancet Digital Health, JAMIA, Annals of Emergency Medicine.
6. **Official Vendor Product Documentation:** Epic Systems, Oracle Health (Cerner), TeleTracking, LeanTaaS, Qventus, Ada Health, Infermedica, Abridge, Nuance/Microsoft.
7. **Reputable Technical & Industry Standards:** HL7 FHIR standards, DICOM, SNOMED-CT, OLS, CTranslate2, Ollama, HuggingFace.
8. **Supplementary Public Sources:** Clearly flagged, never treated as primary ground truth.

---

## 3. Evidence Quality & Novelty Classification Scheme

### 3.1 Evidence Quality Tiers
Every substantive external claim in Phase 2 documentation carries an explicit evidence tag:
- **Grade A:** Official government standard or peer-reviewed primary literature with high sample sizes and randomized/controlled benchmarks.
- **Grade B:** Reputable technical vendor documentation, established industry whitepapers, or large observational studies.
- **Grade C:** Preliminary academic research, preprint, workshop paper, or limited-scope prototype trial.
- **Grade D:** CLINOVA proposal, internal technical inference, or engineering deduction.
- **Grade E:** Unvalidated operational assumption requiring field testing.

### 3.2 Novelty Classification Categories
Every claimed capability in CLINOVA is audited under the following classification:
- **Category A (Established / Common Capability):** Solved and widely deployed across commercial or open-source software (e.g., speech-to-text, OCR, rule-based MEWS calculation).
- **Category B (Existing Capability, Different Implementation):** Exists commercially, but CLINOVA implements via local ₹0 open-source alternatives (e.g., local faster-whisper instead of Nuance DAX API).
- **Category C (Meaningful Combination / Integration):** Individual elements exist separately in silos; uniting them into a coherent single-screen workflow solves a documented gap.
- **Category D (Research-Level Opportunity):** Active academic frontier with theoretical papers but no widespread turnkey clinical deployment (e.g., dynamic multi-graph orchestration under explicit uncertainty).
- **Category E (CLINOVA-Proposed Contribution):** The defensible, bounded core innovation introduced by the CLINOVA architecture.
- **Category F (Unvalidated Assumption):** Hypothesis lacking empirical support, slated for modification or de-scoping.

---

## 4. Central & Secondary Research Questions

### 4.1 Central Research Question
> *"How can healthcare technology continuously connect patient-level clinical state and evidence uncertainty with facility-level care capability and system-level demand to support the safest achievable care pathway from initial intake through outcome, while preserving meaningful human oversight?"*

### 4.2 The 12 Secondary Research Questions (RQ1–RQ12)
- **RQ1 (Information Fragmentation):** How are current systems resolving disconnected multimodal intake data?
- **RQ2 (AI Triage Prioritization):** What are the objective performance characteristics and pitfalls of modern AI triage algorithms?
- **RQ3 (Uncertainty & Gaps):** How do existing systems represent missing evidence, conflicting inputs, and epistemic uncertainty?
- **RQ4 (Longitudinal Trajectory):** How do current systems model the temporal velocity ($\Delta \text{State} / \Delta t$) of a waiting patient?
- **RQ5 (Referrals & Care Navigation):** How do modern closed-loop referral systems coordinate inter-facility transfers?
- **RQ6 (Capability Matching):** How do systems evaluate whether a receiving facility possesses the clinical prerequisites for a specific patient?
- **RQ7 (Capacity & Constraints):** How do capacity command centers incorporate bed occupancy and queue saturation into intake routing?
- **RQ8 (Frontline-to-System Telemetry):** How do national surveillance systems (e.g., IHIP/IDSP) ingest and reflect frontline syndromic signals?
- **RQ9 (Outcome Closure):** How do current systems track whether an initial AI recommendation aligned with ultimate clinical recovery or adverse outcomes?
- **RQ10 (Meaningful Human Oversight):** How is human-in-the-loop governance structured to prevent automation bias and normative compression?
- **RQ11 (India-Specific Constraints):** What infrastructure, bandwidth, linguistic, and regulatory constraints dictate architecture in Indian public health?
- **RQ12 (Novelty Partitioning):** Which specific sub-components of CLINOVA are genuinely novel versus standard baseline integrations?

---

## 5. Audit Deliverables Inventory

Phase 2 generates 25 structured audit reports within `docs/research/`:

| Doc ID | Deliverable File | Core Audit Focus |
|:---|:---|:---|
| `RES-00` | `00_RESEARCH_PLAN.md` | Master audit charter, methodology, and classification standards. |
| `RES-01` | `01_PATIENT_JOURNEY_RESEARCH.md` | 15-stage clinical journey decomposition across 6 care settings. |
| `RES-02` | `02_ROOT_CAUSE_EVIDENCE.md` | 9-domain root cause validation with empirical literature. |
| `RES-03` | `03_EXISTING_TRIAGE_AUDIT.md` | Deep dive into ESI, MTS, CTAS, Ada, Infermedica, Corti, Babylon. |
| `RES-04` | `04_CLINICAL_DOCUMENTATION_AUDIT.md` | Audit of AI scribes (DAX, Abridge, Ambience, Suki) vs care actions. |
| `RES-05` | `05_REFERRAL_CARE_NAVIGATION_AUDIT.md` | Audit of closed-loop referral platforms (AristaMD, Kyruus, ReferralMD). |
| `RES-06` | `06_EHR_CARE_COORDINATION_AUDIT.md` | Audit of enterprise EHRs (Epic, Cerner) and siloed transitions. |
| `RES-07` | `07_FACILITY_RESOURCE_AUDIT.md` | Audit of capacity systems (TeleTracking, LeanTaaS, Qventus). |
| `RES-08` | `08_SYSTEM_SIGNAL_AUDIT.md` | Audit of national surveillance (IHIP/IDSP, CDC ESSENCE, EIOS). |
| `RES-09` | `09_CLINICAL_AI_SAFETY_AUDIT.md` | Audit of uncertainty quantification, automation bias, and EU/FDA HITL. |
| `RES-10` | `10_CAREGRAPH_GAP.md` | Defensibility grill of dynamic patient state and trajectory modeling. |
| `RES-11` | `11_FACILITYGRAPH_GAP.md` | Defensibility grill of real-time capability and care feasibility. |
| `RES-12` | `12_SIGNALGRAPH_GAP.md` | Defensibility grill of frontline syndromic telemetry aggregation. |
| `RES-13` | `13_ORCHESTRATION_GAP.md` | Defensibility grill of multi-graph candidate action synthesis. |
| `RES-14` | `14_OUTCOME_LOOP_AUDIT.md` | Defensibility grill of continuous outcome tracking and calibration. |
| `RES-15` | `15_ENVIRONMENT_GAP_MATRIX.md` | Detailed breakdown across 6 distinct Indian care environments. |
| `RES-16` | `16_COMPETITOR_MATRIX.md` | 27-column master comparison matrix against commercial & academic tools. |
| `RES-17` | `17_FEATURE_NOVELTY_MATRIX.md` | Granular classification of all 18 BPUT baseline & 11 core innovations. |
| `RES-18` | `18_ZERO_COST_FEASIBILITY.md` | Rigorous architectural validation of ₹0 open-source infrastructure. |
| `RES-19` | `19_AI_MODEL_FEASIBILITY.md` | Local inference benchmarks (Qwen family, CPU/GPU, quantization). |
| `RES-20` | `20_RESEARCH_GAP.md` | Empirical synthesis of what exists vs what remains broken globally. |
| `RES-21` | `21_CLINOVA_CONTRIBUTION.md` | Formulation of the smallest defensible, honest innovation claim. |
| `RES-22` | `22_INNOVATION_ARCHITECTURE_DECISION.md` | Explicit KEEP / MODIFY / REMOVE / FUTURE verdict per component. |
| `RES-23` | `23_RESEARCH_TRACEABILITY.md` | Research finding to product specification traceability table. |
| `RES-24` | `24_PHASE_2_CONCLUSION.md` | Executive synthesis answering the 11 critical reviewer questions. |
