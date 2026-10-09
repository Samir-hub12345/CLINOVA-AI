# CLINOVA AI — Architecture Traceability Matrix & Specification Mapping

> **Document ID:** `RES-162`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Quality Assurance & Traceability Group  

---

## 1. Traceability Framework & Scope

This document establishes the **Complete Bidirectional Traceability Matrix** linking approved upstream requirements (Phase 1 BPUT Baseline `B01`–`B18`, Innovations `C01`–`C11`, Phase 3 User Roles, Phase 4 Environments, Phase 5 Master Journey, Phase 6 Data Models, and Phase 7 Provenance Specifications) to Phase 8 architectural artifacts (`RES-134` through `RES-161`), backend domain modules, and frontend workbenches.

$$\mathbf{UPSTREAM\ REQUIREMENTS} \quad \Longleftrightarrow \quad \mathbf{PHASE\ 8\ ARCHITECTURAL\ SPECS} \quad \Longleftrightarrow \quad \mathbf{TARGET\ SYSTEM\ IMPLEMENTATION}$$

---

## 2. BPUT Baseline Capabilities (`B01`–`B18`) Traceability Matrix

| ID | Baseline Requirement | Phase 8 Specification Document | Target Backend Domain Module | Target Frontend Interface Component | Safety & Architectural Enforcement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B01** | Text Symptom Intake | `RES-136`, `RES-138` | `app.domain.intake_stream` | `PatientIntakePortal/TextNarrativeBox` | Auto-resizing textarea; PII redaction filter |
| **B02** | Voice Symptom Intake | `RES-144`, `RES-146` | `app.domain.multimodal_media` | `PatientIntakePortal/AudioStreamRecorder` | Word-level timecodes $[t_{\text{start}}, t_{\text{end}}]$; raw audio uncorrupted |
| **B03** | Medical Report Extraction | `RES-144`, `RES-145` | `app.domain.multimodal_media` | `DoctorWorkbench/LabReportViewer` | Normalized LOINC coding; physiological bounds check |
| **B04** | Optical Character Recognition | `RES-144`, `RES-146` | `app.domain.multimodal_media` | `DoctorWorkbench/PerceptualCropViewer` | Spatial bounding box $[0, 1000]^2$; side-by-side preview |
| **B05** | Extraction & Structuring | `RES-138`, `RES-144` | `app.domain.evidence_provenance` | `DoctorWorkbench/StructuredEntityList` | Standardized SNOMED CT concepts; units normalization |
| **B06** | Timeline Summarization | `RES-139`, `RES-140` | `app.domain.clinical_observations`| `DoctorWorkbench/LongitudinalTimeline` | Temporal clock decoupling; serial vital plotting |
| **B07** | Missing-Information Detection | `RES-138`, `RES-149` | `app.domain.gap_resolution` | `NurseWorkstation/MissingDataWorklist` | Zero-Imputation Law; sufficiency score $S \ge 0.85$ |
| **B08** | Follow-up Question Generation| `RES-138`, `RES-143` | `app.domain.gap_resolution` | `PatientIntakePortal/NBIQuestionCard` | Capped at 1–3 high-yield Next-Best Info questions |
| **B09** | Language & Translation | `RES-136`, `RES-144` | `app.domain.multimodal_media` | `GlobalAppShell/LanguageSelector` | Vernacular Odia/Hindi dictionary; source text preserved |
| **B10** | Risk-Category Support | `RES-137`, `RES-140` | `app.domain.triage_review` | `GlobalAppShell/AcuityBadge` | Deterministic NEWS2 + Shock Index (Decoupled from LLM) |
| **B11** | Queue Prioritization | `RES-149` | `app.domain.triage_review` | `DoctorWorkbench/DoctorQueueTable` | Query-time dynamic wait evaluation; no stored `NOW()` |
| **B12** | Reviewer Dashboard | `RES-136`, `RES-139` | `app.domain.triage_review` | `DoctorWorkbench/DoctorReviewerScreen` | One-screen holistic review; RMP sign-off controls |
| **B13** | Referral Preparation | `RES-141`, `RES-143` | `app.domain.care_pathways` | `ReferralCoordinationDrawer` | Anti-blind referral gating; capability-matched SBAR |
| **B14** | Consent Capture | `RES-138`, `RES-153` | `app.domain.intake_stream` | `PatientIntakePortal/ConsentCheckboxModal` | Blocks data persistence if consent unconfirmed (DPDP) |
| **B15** | Privacy & Anonymization | `RES-142`, `RES-153` | `app.domain.identity_registry` | `GlobalAppShell/PatientHeader` | Synthetic tokens (`SYN-PT-1042`); in-flight PII redaction |
| **B16** | Minimal Data Retention | `RES-151` | `app.domain.governance_sync` | `AuditDrawer/RetentionPolicyBanner` | 30-day raw media purge to `HASH_ONLY`; daemon bypass |
| **B17** | Auditability | `RES-137`, `RES-153` | `app.domain.governance_sync` | `AuditDeveloperConsoleDrawer` | Section 63 BSA 2023 Merkle hash chaining ($H_n$) |
| **B18** | Non-Diagnostic Advisory Gate | `RES-135`, `RES-144` | `app.core.middleware` | `GlobalAppShell/ClinicalSafetyBanner` | Mandatory `X-Clinical-Safety` header; RMP monopoly |

---

## 3. Core Continuous Care Innovations (`C01`–`C11`) Traceability Matrix

| ID | Core Innovation | Phase 8 Specification Document | Target Backend Domain Module | Target Architectural Pattern | Verification & Safety Enforcement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | CAREGRAPH Dynamic State Engine | `RES-140` | `app.domain.continuous_graphs` | Computed In-Memory Projection | Sub-2ms projection over serial vitals; slope $\Delta R / \Delta t$ |
| **C02** | Evidence Provenance Intelligence | `RES-145` | `app.domain.evidence_provenance`| 9-Stage Lineage Pipeline | 8 sources; spatial bounding box $[0, 1000]^2$; audio alignment |
| **C03** | Uncertainty & Contradictions | `RES-140`, `RES-149` | `app.domain.evidence_provenance`| Epistemic State Machine | Decoupling $U_t \neq R_t$; safety-pessimistic conflict gating |
| **C04** | Next-Best Information (NBI) Engine| `RES-138` | `app.domain.gap_resolution` | Value-of-Information Scoring | 1–3 focused clarifying questions; collapses uncertainty |
| **C05** | FACILITYGRAPH Capability Modeling| `RES-141` | `app.domain.continuous_graphs` | Resource Topology Network | 5-state freshness (`KNOWN`, `VERIFIED`, `STALE`, etc.) |
| **C06** | Care Feasibility Synthesis | `RES-141`, `RES-143` | `app.domain.continuous_graphs` | Mathematical Feasibility Gating | Clinical bundle matching $B_{\text{req}}$; transit $\le$ golden hour |
| **C07** | SIGNALGRAPH Telemetry | `RES-142` | `app.domain.continuous_graphs` | Privacy-Preserving Aggregator | Local syndromic z-scores; zero PHI in aggregate counts |
| **C08** | Multi-Graph Orchestration | `RES-143` | `app.domain.continuous_graphs` | Synthesis Engine | Evaluates 6 candidate actions (`ASK`, `VERIFY`, `CONTINUE`...) |
| **C09** | Safest Achievable Care Pathway | `RES-143` | `app.domain.care_pathways` | Resource-Grounded Advisory | Ranks feasible care actions within operational reality |
| **C10** | Post-Disposition Continuity Loop | `RES-139`, `RES-140` | `app.domain.care_pathways` | 27-State Master Case Machine | Eliminates triage cliff-edge; tracks outcome back to chart |
| **C11** | Clinician Decision Calibration | `RES-137`, `RES-143` | `app.domain.triage_review` | Non-Destructive Override Ledger| Captures physician overrides to evaluate model safety |

---

## 4. Upstream Phases 3–7 Traceability Linkages

| Upstream Specification Phase | Upstream Key Findings & Decisions | Phase 8 Architectural Synthesis Document |
| :--- | :--- | :--- |
| **Phase 3: User Roles (`RES-30`–`42`)** | RMP monopoly under NMC Reg 27; 3 primary interfaces; emergency role escalation | `RES-136` (Frontend Workbenches), `RES-153` (RBAC Security) |
| **Phase 4: Environments (`RES-43`–`56`)**| 6 environments; one codebase, configured profiles; rural PHC edge realities | `RES-154` (Environment Architecture), `RES-160` (Topologies) |
| **Phase 5: Master Journey (`RES-57`–`77`)**| 27 canonical states ($S01$–$S27$); 6 longitudinal care epochs; anti-fragmentation | `RES-139` (Master Case State Machine & OCC Versioning) |
| **Phase 6: Master Case (`RES-78`–`105`)** | Root `cases` entity; dual SQLite WAL / PostgreSQL compatibility; event history | `RES-139` (Dependency Graph), `RES-150` (Table Reconciliation) |
| **Phase 7: Provenance (`RES-106`–`133`)**| $\text{INFERRED} \neq \text{VERIFIED}$; 8 sources; 6 epistemic states; DPDP raw media purge | `RES-145` (Lineage), `RES-151` (Retention), `RES-152` (Dual Review) |

**Traceability Integrity Certification:** 100% of upstream clinical requirements, statutory constraints, and data models are mapped to explicit technical architecture specifications in Phase 8 without orphaned concepts or unsupported claims.
