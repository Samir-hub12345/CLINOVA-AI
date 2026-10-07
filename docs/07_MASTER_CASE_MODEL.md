# CLINOVA AI — Master Case Data Model Specification

> **Document ID:** `DOC-07`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. The Master Case Principle

> **Core Architectural Law:** Every patient encounter must possess exactly **ONE** Master Case record.
> 
> No subsystem, staff member, emergency workflow, referral desk, or outpatient clinic may create a disconnected secondary patient record for the same encounter. All downstream clinical artifacts (triage notes, lab addendums, ward handoffs, emergency packs, referral letters, and real outcome logs) are dynamically derived views rooted in the single Master Case.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MASTER CASE RECORD                               │
│                         `case_id`: UUID (Primary Key)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── 1. Patient Context & Consent (Pseudonym, Age, Gender, Language)        │
│  ├── 2. Multimodal Inputs (Voice Audio, Transcripts, Uploaded Files)        │
│  ├── 3. OCR & Extracted Clinical Entities (Discrete Symptoms, Units)        │
│  ├── 4. Longitudinal Timeline (Normalized Chronological Events)             │
│  ├── 5. Interactive Q&A Session (Prompts, Patient Responses, Timestamps)    │
│  ├── 6. Objective Observations & Vitals (Serial BP, HR, SpO2, Temp, RR)    │
│  ├── 7. Laboratory & Diagnostic Panels (Hematology, Biochemistry, ECG)     │
│  ├── 8. Evidence Provenance Ledger (Source, Actor, Quality, Verification)   │
│  ├── 9. CAREGRAPH State (Physiological Nodes, Trajectory, Uncertainty Vector)│
│  ├── 10. Risk Stratification (Acuity Score, Risk Band, Reasoning Flags)     │
│  ├── 11. Clinician Audit & Modification Log (Original, Modified, Justify)   │
│  ├── 12. FACILITYGRAPH Feasibility Evaluation (Capability, Bed Availability)│
│  ├── 13. Orchestration Recommendation (Safest Achievable Care Pathway)      │
│  ├── 14. Clinical Decision & Disposition (Approve, Refer, Admit, Escalate)  │
│  ├── 15. Pathway Execution Sub-Records:                                     │
│  │   ├── Referral Logistics Record (Destination, Transport, Handoff)        │
│  │   ├── Inpatient Ward Admission Record (Ward ID, Bed ID, Handoff Pack)    │
│  │   ├── Emergency Fast-Track & Resuscitation Bundle                        │
│  │   ├── Operation Theatre (OT) Pre-Op Checklist Record                     │
│  │   └── Scheduled Follow-up & Appointment Tracker                          │
│  ├── 16. Longitudinal Outcome Log (Real Clinical Endpoint, Delta Evaluation)│
│  └── 17. Cryptographic Audit Event Ledger (Immutable Timestamped History)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Case Schema Specification

### 2.1 Core Identity & Demographics
- `case_id`: UUID (v4) — Immutable globally unique encounter identifier.
- `synthetic_patient_id`: String (`PT-XXXXXX`) — Anonymized patient identifier.
- `encounter_timestamp`: ISO 8601 UTC timestamp of initial intake.
- `facility_id`: String — ID of the originating healthcare facility.
- `intake_mode`: Enum (`REGULAR_STANDARD`, `EMERGENCY_FAST_TRACK`).
- `demographics`:
  - `age`: Integer.
  - `gender`: Enum (`MALE`, `FEMALE`, `OTHER`, `UNKNOWN`).
  - `preferred_language`: Enum (`ODIA`, `HINDI`, `ENGLISH`, `REGIONAL_OTHER`).
  - `consent_recorded`: Boolean (Strict gate: must be `True` to persist).
  - `consent_type`: Enum (`DIGITAL_SIGNATURE`, `VERBAL_WITNESSED`, `EMERGENCY_IMPLIED`).

### 2.2 Multimodal Raw Inputs & Extractions
- `raw_symptom_narrative`: String (Sanitized free-text entered by patient or staff).
- `voice_recordings`: List of Objects:
  - `recording_id`: UUID.
  - `storage_path`: String (Supabase / local ephemeral path).
  - `audio_duration_seconds`: Float.
  - `transcript_text`: String (Native vernacular transcript).
  - `translated_text`: String (Standardized clinical English).
  - `transcription_confidence`: Float (0.00–1.00).
- `uploaded_documents`: List of Objects:
  - `document_id`: UUID.
  - `file_type`: Enum (`PRESCRIPTION_IMAGE`, `LAB_REPORT_PDF`, `DISCHARGE_SUMMARY`, `OTHER`).
  - `ocr_raw_text`: String.
  - `ocr_engine`: Enum (`PADDLE_OCR`, `TESSERACT`, `SYNTHETIC_MOCK`).
  - `ocr_confidence`: Float (0.00–1.00).

### 2.3 Discrete Extracted Entities & Timeline
- `extracted_entities`: List of Objects:
  - `entity_id`: UUID.
  - `entity_type`: Enum (`SYMPTOM`, `VITAL_SIGN`, `LAB_VALUE`, `MEDICATION`, `ALLERGY`, `COMORBIDITY`).
  - `canonical_name`: String (SNOMED-CT / ICD-11 normalized concept).
  - `value`: Any (Number, string, boolean).
  - `unit`: String (mmHg, %, mg, etc.).
  - `provenance_source`: Enum (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `CLINICIAN_VERIFIED`, `AI_INFERRED`, `SYSTEM_DERIVED`).
  - `verification_status`: Enum (`UNVERIFIED`, `CLINICIAN_VERIFIED`, `MODIFIED`, `REJECTED`).
- `timeline_events`: List of Objects:
  - `event_id`: UUID.
  - `timestamp`: ISO 8601 UTC.
  - `event_description`: String.
  - `evidence_pointer`: String (Reference to `entity_id` or `document_id`).
  - `is_verified`: Boolean.

### 2.4 Clinical State & CAREGRAPH Vector
- `vitals_series`: List of Vitals Snapshots:
  - `timestamp`: ISO 8601 UTC.
  - `recorded_by`: String (`actor_id` of nurse/doctor).
  - `blood_pressure_systolic`: Integer (mmHg).
  - `blood_pressure_diastolic`: Integer (mmHg).
  - `heart_rate`: Integer (bpm).
  - `respiratory_rate`: Integer (bpm).
  - `oxygen_saturation`: Integer (% SpO2).
  - `temperature_celsius`: Float (°C).
  - `blood_glucose_mg_dl`: Optional Float.
  - `gcs_score`: Integer (3–15).
- `caregraph_state`:
  - `physiological_state_summary`: String.
  - `risk_level`: Enum (`EMERGENCY_CRITICAL`, `HIGH_PRIORITY`, `MODERATE_OBSERVE`, `ROUTINE_LOW`).
  - `acuity_score`: Float (0.00–10.00 composite score).
  - `trajectory`: Enum (`IMPROVING`, `STABLE`, `WORSENING`, `UNKNOWN`).
  - `uncertainty_vector`:
    - `known_count`: Integer.
    - `unknown_count`: Integer.
    - `conflicting_count`: Integer.
    - `unreliable_count`: Integer.
    - `overall_uncertainty_score`: Float (0.00 = complete certainty, 1.00 = extreme uncertainty).
  - `next_best_information_targets`: List of Strings (e.g., `["troponin_i", "chest_xray", "serial_bp_15min"]`).

### 2.5 Clinical Decision & Verification History
- `clinician_review`:
  - `reviewer_id`: String (Medical officer ID).
  - `review_timestamp`: ISO 8601 UTC.
  - `verification_actions`: List of Objects:
    - `target_field`: String.
    - `original_value`: Any.
    - `verified_or_modified_value`: Any.
    - `modification_reason`: String.
  - `doctor_triage_notes`: String (Free-text clinical commentary).
  - `final_clinical_decision`: Enum (`ROUTINE_HOME_CARE`, `FURTHER_REVIEW`, `WARD_ADMISSION`, `EMERGENCY_RESUSCITATION`, `OT_TRANSFER`, `INTER_FACILITY_REFERRAL`).

### 2.6 Execution Sub-Records & Outcomes
- `referral_record`: Optional Object (`target_facility_id`, `transport_type`, `departure_time`, `arrival_time`, `receiving_clinician_id`, `handoff_status`).
- `admission_record`: Optional Object (`ward_name`, `bed_id`, `admitting_doctor_id`, `handoff_checklist_confirmed`).
- `emergency_ot_record`: Optional Object (`emergency_ward_id`, `surgical_procedure_planned`, `surgical_safety_checklist_completed`, `surgeon_id`).
- `follow_up_record`: Optional Object (`scheduled_date`, `revisit_type`, `reminder_sent`, `patient_attended`).
- `longitudinal_outcome`: Optional Object:
  - `outcome_timestamp`: ISO 8601 UTC.
  - `final_clinical_endpoint`: Enum (`FULL_RECOVERY`, `STABILIZED`, `REFERRED_HIGHER`, `COMPLICATION_MANAGED`, `CRITICAL_TRANSFER`, `ADVERSE_EVENT`).
  - `algorithm_agreement`: Boolean (Did final doctor action match AI advisory pathway?).
  - `calibration_notes`: String.

### 2.7 Immutable Audit Ledger
- `audit_events`: List of Objects:
  - `event_id`: UUID.
  - `timestamp`: ISO 8601 UTC.
  - `actor_id`: String.
  - `actor_role`: String.
  - `action`: String (`INTAKE_CREATED`, `OCR_PARSED`, `VITAL_ENTERED`, `AI_INFERENCE_GENERATED`, `DOCTOR_VERIFIED`, `DECISION_SIGNED`, `REFERRAL_DISPATCHED`).
  - `hash_signature`: String (Cryptographic hash tying to previous event).

---

## 3. Data Integrity & Lifecycle Invariants

1. **Uniqueness:** One patient visit = exactly one `case_id`. All staff actions append to this ID.
2. **Derivation Exclusivity:** All 6 report types (`Comprehensive`, `Vitals Addendum`, `Routine`, `Ward Admission`, `Emergency`, `OT`) must generate dynamically from the Master Case state. They never store unlinked detached clinical data.
3. **Immutability of Historical Evidence:** When a clinician modifies an AI extraction, the original extracted value and the clinician's modification are both permanently preserved in `verification_actions` and `audit_events`.
4. **Data Minimization:** Raw audio files and uploaded report images adhere to the 24-hour ephemeral retention rule in production, while extracted discrete clinical nodes and audit trails are persisted for clinical continuity.
