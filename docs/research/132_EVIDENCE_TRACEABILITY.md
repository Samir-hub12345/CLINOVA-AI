# CLINOVA AI — Comprehensive Evidence & Provenance Bidirectional Traceability Matrix

> **Document ID:** `RES-132`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Traceability Scope & Verification Objectives

This document establishes the authoritative **Bidirectional Traceability Matrix** connecting:
1. **Phase 7 Research Specifications (`RES-106` through `RES-131`)**
2. **Upstream Phase 6 Master Case Relational Tables (`RES-79` through `RES-102`)**
3. **Canonical Evidence Source Classes (8 Sources)**
4. **Epistemic States (6 States)**
5. **Data Integrity Invariants (`INV-PROV-01` to `INV-PROV-18`)**
6. **Adversarial Stress Test Scenarios (Scenarios A through N)**
7. **Downstream Implementation Targets (Future Engine Repositories & Schemas)**

---

## 2. Comprehensive Bidirectional Traceability Matrix

| Spec ID | Research Topic | Primary Relational Entity | Upstream Phase 6 Anchor | Invariant Enforced | Adversarial Scenario | Downstream Implementation Target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RES-106` | Research Plan & Scope | *System Architectural Boundary*| `RES-78`, `RES-105` | *All Invariants* | *All Cases* | Project Architecture Baseline |
| `RES-107` | 8 Evidence Sources | `evidence_records.source_type` | `RES-83` (Sec 2) | `INV-PROV-01` | Case D, H | `backend/app/db/models/evidence.py` |
| `RES-108` | 6 Epistemic States | `evidence_records.epistemic_status`| `RES-83` (Sec 3) | `INV-PROV-01`, `INV-PROV-05`| Case E, F | `backend/app/domain/epistemic_fsm.py` |
| `RES-109` | 9-Stage Lineage Chain | `raw_evidence_sources` | `RES-82`, `RES-84` | `INV-PROV-02`, `INV-PROV-10`| Case B, C | `backend/app/services/lineage_tracer.py` |
| `RES-110` | OCR Spatial Provenance | `ocr_extracted_snippets` | `RES-84` (Sec 4) | `INV-PROV-06`, `INV-PROV-09`| Case B, H | `backend/app/services/ocr_service.py` |
| `RES-111` | Voice & Vernacular Grounding | `audio_recordings`, `audio_transcripts`| `RES-84` (Sec 3) | `INV-PROV-07`, `INV-PROV-11`| Case C, I | `backend/app/services/whisper_service.py` |
| `RES-112` | Manual Entry Attribution | `manual_entry_audit_logs` | `RES-80`, `RES-82` | `INV-PROV-02`, `INV-PROV-10`| Case D, L | `backend/app/services/audit_service.py` |
| `RES-113` | Acuity-Proportional Review| `verification_events` | `RES-91` (Sec 3) | `INV-PROV-11`, `INV-PROV-13`| Case F, L | `backend/app/services/verification.py` |
| `RES-114` | Evidence Conflict Model | `evidence_conflicts` | `RES-83` (Sec 5) | `INV-PROV-04`, `INV-PROV-08`| Case A, D | `backend/app/services/conflict_resolver.py`|
| `RES-115` | Decoupled Quality & Conf. | `evidence_records` (Quality/Conf)| `RES-83`, `RES-89` | `INV-PROV-01`, `INV-PROV-06`| Case B, C | `backend/app/services/calibration.py` |
| `RES-116` | Epistemic Uncertainty ($U_t$)| `clinical_evaluations` ($U_t$) | `RES-89` (Sec 4) | `INV-PROV-04`, `INV-PROV-08`| Case A, M | `backend/app/services/uncertainty.py` |
| `RES-117` | Evidence Temporal Freshness | `evidence_records` (Freshness) | `RES-92` (Sec 3) | `INV-PROV-10` | Case A, D | `backend/app/services/freshness_daemon.py` |
| `RES-118` | Multi-Clock Quad-Time | `temporal_provenance_ledgers` | `RES-82` (Sec 4) | `INV-PROV-10` | Case A, J | `backend/app/services/temporal_clock.py` |
| `RES-119` | Transformation Lineage | `transformation_lineage_events`| `RES-84`, `RES-86` | `INV-PROV-02`, `INV-PROV-07`| Case B, C | `backend/app/services/transformer.py` |
| `RES-120` | AI Inference Guardrails | `ai_inferences` | `RES-90`, `RES-93` | `INV-PROV-05`, `INV-PROV-12`| Case E, F | `backend/app/services/ai_guardrails.py` |
| `RES-121` | Deterministic Derived Data| `system_derived_calculations` | `RES-85`, `RES-90` | `INV-PROV-18` | Case D, G | `backend/app/services/scoring_engine.py` |
| `RES-122` | Decision Traceability | `decision_traceability_links` | `RES-91`, `RES-96` | `INV-PROV-13` | Case F, L | `backend/app/services/decision_tracer.py` |
| `RES-123` | Report Provenance & PDF | `clinical_reports` | `RES-94`, `RES-96` | `INV-PROV-11`, `INV-PROV-16`| Case I, N | `backend/app/services/report_generator.py` |
| `RES-124` | Provenance UI Experience | *Conceptual UI Ergonomics* | `RES-32`, `RES-34` | `INV-PROV-06`, `INV-PROV-09`| Case B, C | `frontend/src/components/provenance/` |
| `RES-125` | Retention & Purge Model | `media_purge_audit_events` | `RES-100` (Sec 3) | `INV-PROV-16` | Case I | `backend/app/services/retention_worker.py` |
| `RES-126` | Offline Edge Provenance | `sync_journals` | `RES-99` (Sec 3) | `INV-PROV-17` | Case J, K | `backend/app/services/offline_sync.py` |
| `RES-127` | Tamper Resistance & BSA | `security_tamper_audit_logs` | `RES-98`, `RES-102` | `INV-PROV-02`, `INV-PROV-14`| Case N | `backend/app/services/merkle_auditor.py` |
| `RES-128` | Provenance Access Control | *Conceptual Permission Matrix* | `RES-34`, `RES-97` | `INV-PROV-11` | Case H, N | `backend/app/services/permission_guard.py` |
| `RES-129` | Failure Matrix (25 Cases) | *System Exception Handlers* | `RES-38`, `RES-103` | *All Invariants* | Cases 1–25 | `backend/app/core/exceptions.py` |
| `RES-130` | Adversarial Stress Tests | *Adversarial Test Suite* | `RES-103` (Sec 2) | *All Invariants* | Cases A–N | `tests/adversarial/` (Future) |
| `RES-131` | Mathematical Invariants | *Relational Table Constraints* | `RES-102` | `INV-PROV-01`–`18`| *All Cases* | Database DDL & Engine Triggers |

---

## 3. Verification Completeness Statement

Every requirement specified in the Phase 7 mandate has been systematically addressed:
- **Zero Orphaned Specifications:** Every research document binds to a relational table, a mathematical invariant, an adversarial validation scenario, and a downstream implementation path.
- **Bi-directional Integrity:** Any future developer, clinical auditor, or court examiner can begin at a downstream software component or database row and traverse backwards through this matrix directly to the authoritative clinical research and legal justifications.
