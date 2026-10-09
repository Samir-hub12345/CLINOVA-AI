# CLINOVA AI — Master Case Bidirectional Traceability Matrix

> **Document ID:** `RES-104`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Traceability Scope & Verification Objectives

This matrix establishes complete **Bidirectional Traceability** linking:
- **Phase 5 Journey States (`RES-61`)**
- **Phase 6 Canonical Database Entities & Tables**
- **Data Attributes & Foreign Key Linkages**
- **Data Integrity Invariants (`INV-01` to `INV-12`)**
- **Validation Test Scenarios (Cases A through J)**
- **Future Implementation Targets (Phase 7 Schema Migration & Repository Integration)**

---

## 2. Master Case Bidirectional Traceability Matrix

| State Code | Phase 5 Journey State | Primary Relational Entity | Core DB Attributes | Invariant Enforced | Validation Scenario | Phase 7 Implementation Target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `S01` | `STATE_NEW` | `cases`, `encounters`, `patient_consents` | `case_id`, `encounter_id`, `facility_id`, `intake_mode`, `consent_type` | `INV-01`, `INV-11` | Case A, D | `backend/app/db/models/case.py` |
| `S02` | `STATE_INTAKE_COLLECTING`| `audio_recordings`, `documents` | `file_path`, `file_hash`, `file_size_bytes`, `duration_seconds` | `INV-01`, `INV-06` | Case A | `backend/app/db/models/media.py` |
| `S03` | `STATE_EXTRACTING` | `audio_transcripts`, `document_ocr_pages` | `raw_transcript_native`, `english_translation`, `ocr_raw_text` | `INV-05`, `INV-06` | Case A | `backend/app/db/models/extraction.py`|
| `S04` | `STATE_EXTRACTION_REVIEW`| `ocr_extracted_snippets`, `evidence_records`| `bounding_box`, `normalized_value`, `review_status`, `confidence` | `INV-06`, `INV-08` | Case A, F | `backend/app/db/models/snippet.py` |
| `S05` | `STATE_MISSING_AUDIT` | `missing_information_items`, `info_suff_evals`| `information_domain`, `item_name`, `weight`, `sufficiency_score` | `INV-02`, `INV-07` | Case B | `backend/app/db/models/audit_gap.py`|
| `S06` | `STATE_FOLLOW_UP_PENDING`| `completion_sessions`, `followup_questions` | `turn_number`, `target_respondent`, `response_type`, `options_json` | `INV-01`, `INV-05` | Case A | `backend/app/db/models/completion.py`|
| `S07` | `STATE_STAFF_DATA_PENDING`| `missing_information_items` | `status = 'REQUESTED'`, `clinical_importance = 'CRITICAL'` | `INV-02` | Case B | `backend/app/db/models/worklist.py` |
| `S08` | `STATE_STAFF_VERIFIED` | `vital_readings`, `evidence_records` | `heart_rate`, `systolic_bp`, `spo2_percent`, `source_type` | `INV-02`, `INV-06` | Case B, F | `backend/app/db/models/vitals.py` |
| `S09` | `STATE_CONSOLIDATED` | `cases`, `case_events` | `state_version`, `integrity_hash`, `payload_snapshot` | `INV-01`, `INV-03` | Case A, B | `backend/app/db/models/event.py` |
| `S10` | `STATE_TRIAGE_READY` | `clinical_evaluations`, `triage_notes` | `risk_score`, `trajectory_slope`, `uncertainty_score`, `priority` | `INV-05`, `INV-07` | Case A, B | `backend/app/db/models/evaluation.py`|
| `S11` | `STATE_DOCTOR_QUEUED` | `doctor_queue_entries` | `priority_score`, `wait_minutes_elapsed`, `queue_status` | `INV-07` | Case A, C | `backend/app/db/models/queue.py` |
| `S12` | `STATE_DOCTOR_REVIEWING`| `cases` (`state_version` OCC lock) | `current_state = 'STATE_DOCTOR_REVIEWING'`, `updated_at` | `INV-04` | Case A, I | `backend/app/db/models/case.py` |
| `S13` | `STATE_CLINICIAN_VERIFIED`| `clinician_reviews`, `clinician_modifications`| `priority_assigned`, `clinician_notes`, `original_value`, `new_value`| `INV-04`, `INV-08` | Case A, G | `backend/app/db/models/review.py` |
| `S14` | `STATE_FACILITY_EVALUATING`| `care_requirements`, `feasibility_evaluations` | `required_specialties`, `required_diagnostics`, `is_feasible` | `INV-09` | Case A, E | `backend/app/db/models/facility.py` |
| `S15` | `STATE_ORCHESTRATION_PENDING`| `orchestration_recommendations` | `suggested_action`, `rationale`, `human_review_required = TRUE` | `INV-05` | Case A, G | `backend/app/db/models/orchestration.py`|
| `S16` | `STATE_ROUTINE_CARE` | `clinician_orders`, `appointments` | `order_type = 'MEDICATION'`, `scheduled_date`, `time_slot_window` | `INV-01`, `INV-04` | Case A | `backend/app/db/models/orders.py` |
| `S17` | `STATE_FURTHER_REVIEW` | `appointments`, `care_pathways` | `appointment_type = 'LAB_REVIEW'`, `pathway_type = 'FOLLOW_UP'` | `INV-01` | Case I | `backend/app/db/models/appointments.py`|
| `S18` | `STATE_WARD_REQUESTED` | `ward_admissions` | `requested_ward_type`, `admitting_clinician_id`, `status` | `INV-01`, `INV-04` | Case C, D | `backend/app/db/models/ward.py` |
| `S19` | `STATE_WARD_ADMITTED` | `ward_admissions` | `assigned_bed_id`, `sbar_handoff_signed_at`, `status = 'ADMITTED'` | `INV-01` | Case C, D | `backend/app/db/models/ward.py` |
| `S20` | `STATE_REFERRAL_PENDING`| `referrals`, `referral_rejections` | `destination_facility_id`, `clinical_summary_pack`, `status` | `INV-09` | Case A, E | `backend/app/db/models/referral.py` |
| `S21` | `STATE_TRANSFER_IN_TRANSIT`| `transfer_transit_logs` | `paramedic_actor_id`, `enroute_spo2`, `enroute_systolic_bp` | `INV-06`, `INV-09` | Case A, E | `backend/app/db/models/transit.py` |
| `S22` | `STATE_EMERGENCY_ACTIVE`| `privacy_break_glass_audits`, `vital_readings` | `emergency_justification`, `avpu_score`, `shock_index` | `INV-10`, `INV-11` | Case C, D | `backend/app/db/models/emergency.py`|
| `S23` | `STATE_OT_PENDING` | `surgical_procedures` | `procedure_name`, `booking_urgency`, `lead_surgeon_id` | `INV-01`, `INV-04` | Case J | `backend/app/db/models/surgery.py` |
| `S24` | `STATE_OT_HANDOFF` | `surgical_procedures` | `who_checklist_signin`, `who_checklist_timeout`, `dual_signoff`| `INV-04` | Case J | `backend/app/db/models/surgery.py` |
| `S25` | `STATE_OUTCOME_PENDING` | `care_pathways` | `current_status = 'ACTIVE'`, `pathway_type` | `INV-01` | Case A, I, J | `backend/app/db/models/carepath.py` |
| `S26` | `STATE_RESOLVED` | `case_outcomes` | `outcome_type`, `clinical_disposition_summary`, `alignment` | `INV-01`, `INV-04` | Case A, I, J | `backend/app/db/models/outcome.py` |
| `S27` | `STATE_CLOSED` | `cases`, `archived_cases` | `is_sealed = TRUE`, `merkle_root_hash`, `lifecycle_stage` | `INV-01`, `INV-03` | Case A, I, J | `backend/app/db/models/archive.py` |

---

## 3. Verification Completeness Statement

Every canonical state in the 27-state machine maps directly to:
1. An authoritative database table holding primary clinical custody.
2. Explicit foreign key integrity to the root `cases(id)`.
3. Guardrails enforcing the 12 data invariants.
4. Concrete test coverage in Cases A through J.
