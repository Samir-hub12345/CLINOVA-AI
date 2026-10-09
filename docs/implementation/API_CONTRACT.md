# CLINOVA AI — Core API Contract Specification

> **Document ID:** `API-CONTRACT-V1`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 13 — Core Backend Foundation, Master Case Persistence & API Layer  
> **Version:** 2.0.0  
> **Base URL:** `/api/v1`  
> **OpenAPI Schema:** `/docs` (FastAPI Swagger UI)  

---

## 1. Governance Principles & API Conventions

1. **Non-Diagnostic Mandate:** Clinova AI provides continuous care intelligence and clinical decision support. All recommendations require qualified clinician verification prior to action.
2. **Canonical Master Case Invariant:** There is exactly ONE root aggregate: `cases`. All downstream clinical entities (`evidence`, `vitals`, `timeline_events`, `consents`, `follow_up_questions`, `triage_notes`, `review_actions`, `audit_events`) foreign-key directly to `cases.id`.
3. **Structured Error Contract:** All errors follow the standardized envelope:
   ```json
   {
     "error": {
       "code": "VALIDATION_ERROR | NOT_FOUND | AUTHORIZATION_ERROR | CONFLICT | INVALID_STATE_TRANSITION | DATABASE_ERROR | UNSUPPORTED_OPERATION",
       "message": "Human-readable description",
       "details": {},
       "correlation_id": "corr-uuid"
     }
   }
   ```
4. **Information Shielding:** Zero stack traces, raw SQL queries, database credentials, filesystem paths, or internal secrets are exposed in API responses.
5. **UTC Timestamps:** All timestamps are ISO 8601 UTC strings (e.g., `2026-10-08T18:00:00Z`).
6. **Optimistic Concurrency:** State transitions enforce monotonic `state_version` matching. Conflicts return HTTP 409 `CONFLICT`.

---

## 2. Authentication & Authorization Headers

| Header | Format | Description | Default Fallback |
| :--- | :--- | :--- | :--- |
| `X-Actor-Id` | String (`usr-...`) | Identity of calling staff member or system actor | `usr-doc-01` |
| `X-Actor-Role` | String | Role: `CLINICIAN`, `NURSE`, `PATIENT`, `FACILITY_ADMIN`, `AUDITOR`, `SYSTEM` | `CLINICIAN` |
| `X-Facility-Id` | String (`FAC-...`) | Operating facility context | `FAC-DH-04` |

---

## 3. Authoritative Endpoint Inventory

### 3.1 System & Health

#### `GET /health`
- **Operation:** `get_health`
- **Description:** Health check for orchestrators, containers, and monitoring.
- **Request:** None
- **Response:**
  ```json
  {
    "status": "healthy",
    "app": "Clinova AI",
    "version": "2.0.0",
    "environment": "development"
  }
  ```

#### `GET /api/v1/status`
- **Operation:** `get_system_status`
- **Description:** Subsystem operational status and mode flags.
- **Response:** Status, environment, synthetic mode flags, four pillars active.

---

### 3.2 Patient Management

#### `POST /api/v1/patients`
- **Operation:** `create_patient`
- **Description:** Registers demographic profile and synthetic identifier.
- **Request Schema:**
  ```json
  {
    "synthetic_id": "PT-SYN-1042",
    "age_bracket": "40-49",
    "biological_sex": "MALE",
    "is_synthetic": true
  }
  ```
- **Response Schema:** `PatientRead` (UUID `id`, `synthetic_id`, `age_bracket`, timestamps).
- **Errors:** 422 `VALIDATION_ERROR`.

#### `GET /api/v1/patients/{patient_id}`
- **Operation:** `get_patient`
- **Description:** Retrieves patient demographic context by UUID.
- **Response Schema:** `PatientRead`.
- **Errors:** 404 `NOT_FOUND`.

---

### 3.3 Encounter Management

#### `POST /api/v1/encounters`
- **Operation:** `create_encounter`
- **Description:** Initializes an encounter linking patient to facility.
- **Request Schema:**
  ```json
  {
    "patient_id": "uuid",
    "facility_id": "FAC-DH-04",
    "environment": "development",
    "pathway": "REGULAR_STANDARD"
  }
  ```
- **Response Schema:** `EncounterRead`.
- **Errors:** 404 `NOT_FOUND` (if patient or facility does not exist).

#### `GET /api/v1/encounters/{encounter_id}`
- **Operation:** `get_encounter`
- **Description:** Retrieves encounter record by UUID.
- **Response Schema:** `EncounterRead`.
- **Errors:** 404 `NOT_FOUND`.

---

### 3.4 Canonical Master Case Management

#### `POST /api/v1/cases`
- **Operation:** `create_case`
- **Description:** Establishes the single Master Case aggregate root for an encounter.
- **Request Schema:**
  ```json
  {
    "patient_id": "uuid",
    "facility_id": "FAC-DH-04",
    "encounter_id": "uuid",
    "pathway": "REGULAR_STANDARD",
    "acuity_tier": "URGENT",
    "presenting_complaint": "Severe chest pain",
    "primary_syndrome": "Acute Coronary Syndrome",
    "required_bundle": "BUNDLE_ACS_THROMBOLYSIS_PCI"
  }
  ```
- **Response Schema:** `CaseRead` (UUID `id`, `case_number`, `state_version` = 1, `current_state` = `INTAKE_RECORDED`).
- **Errors:** 404 `NOT_FOUND`, 422 `VALIDATION_ERROR`.

#### `GET /api/v1/cases`
- **Operation:** `list_cases`
- **Description:** Lists recent cases with optional filtering (`acuity`, `state`, `facility_id`, `limit`).
- **Response Schema:** `List[CaseRead]`.

#### `GET /api/v1/cases/{case_id}`
- **Operation:** `get_case`
- **Description:** Retrieves canonical Master Case by UUID.
- **Response Schema:** `CaseRead`.
- **Errors:** 404 `NOT_FOUND`.

---

### 3.5 Evidence & Provenance

#### `POST /api/v1/cases/{case_id}/evidence`
- **Operation:** `add_case_evidence`
- **Description:** Records discrete clinical evidence with source class, epistemic state, confidence, and provenance metadata.
- **Request Schema:**
  ```json
  {
    "source_class": "PATIENT_REPORTED | VOICE_TRANSCRIBED | OCR_EXTRACTED | CLINICIAN_VERIFIED | STAFF_ENTERED | AI_INFERRED | SYSTEM_DERIVED | EXTERNAL_RECORD",
    "epistemic_state": "KNOWN | UNKNOWN | CONFLICTING | UNRELIABLE | VERIFIED | INFERRED",
    "parameter_name": "fever_duration_days",
    "content_value": 3,
    "unit": "days",
    "confidence_score": 0.95,
    "provenance_metadata": {}
  }
  ```
- **Invariant:** `VERIFIED` state requires clinician role.
- **Response Schema:** `EvidenceRead`.
- **Errors:** 403 `AUTHORIZATION_ERROR`, 404 `NOT_FOUND`, 422 `VALIDATION_ERROR`.

#### `GET /api/v1/cases/{case_id}/evidence`
- **Operation:** `get_case_evidence`
- **Description:** Lists all evidence items persisted for the case.
- **Response Schema:** `List[EvidenceRead]`.

---

### 3.6 Vitals Persistence

#### `POST /api/v1/cases/{case_id}/vitals`
- **Operation:** `record_case_vitals`
- **Description:** Appends physiological vitals with strict boundary validation (HR 20–260, SBP 30–300, DBP 20–200, SBP > DBP, SpO2 30–100, RR 4–80, Temp 28.0–44.0).
- **Request Schema:**
  ```json
  {
    "heart_rate": 88,
    "systolic_bp": 120,
    "diastolic_bp": 80,
    "spo2_percent": 98,
    "respiratory_rate": 16,
    "temperature_celsius": 37.0,
    "avpu_score": "ALERT"
  }
  ```
- **Response Schema:** `VitalRead`.
- **Errors:** 422 `VALIDATION_ERROR` (on physiological impossibility or inversion), 404 `NOT_FOUND`.

#### `GET /api/v1/cases/{case_id}/vitals`
- **Operation:** `get_case_vitals`
- **Description:** Chronological series of vital readings.
- **Response Schema:** `List[VitalRead]`.

---

### 3.7 Longitudinal Timeline

#### `GET /api/v1/cases/{case_id}/timeline`
- **Operation:** `get_case_timeline`
- **Description:** Chronologically ordered timeline milestones with explicit conflict flags.
- **Response Schema:** `List[TimelineEventRead]`.

#### `POST /api/v1/cases/{case_id}/timeline`
- **Operation:** `add_timeline_event`
- **Description:** Adds discrete milestone to case timeline.
- **Request Schema:** `TimelineEventCreate`.
- **Response Schema:** `TimelineEventRead`.

---

### 3.8 Informed Consent

#### `POST /api/v1/cases/{case_id}/consent`
- **Operation:** `record_case_consent`
- **Description:** Persists patient informed consent status, channel, language, and hash.
- **Request Schema:**
  ```json
  {
    "purpose": "CLINICAL_CARE_TRIAGE",
    "language": "en",
    "channel": "DIGITAL_APP",
    "status": "GRANTED"
  }
  ```
- **Response Schema:** `ConsentRead`.

#### `GET /api/v1/cases/{case_id}/consent`
- **Operation:** `get_case_consent`
- **Description:** Retrieves consent record for case.
- **Response Schema:** `ConsentRead`.

---

### 3.9 Follow-up Questions & Answers

#### `POST /api/v1/cases/{case_id}/follow-up`
- **Operation:** `create_case_follow_up`
- **Description:** Adds targeted question to resolve missing clinical parameters.
- **Request Schema:**
  ```json
  {
    "question_text": "Do you have chest pain during rest?",
    "reason": "Resolve missing rest angina symptom",
    "priority": "CRITICAL"
  }
  ```
- **Response Schema:** `FollowUpQuestionRead`.

#### `POST /api/v1/cases/{case_id}/follow-up/answer`
- **Operation:** `answer_follow_up`
- **Description:** Records patient or staff response to an outstanding question.
- **Request Schema:**
  ```json
  {
    "question_id": "uuid",
    "answer_text": "Pain occurs only on climbing stairs."
  }
  ```
- **Response Schema:** `FollowUpAnswerRead`.

#### `GET /api/v1/cases/{case_id}/follow-up`
- **Operation:** `get_case_follow_ups`
- **Description:** Lists all follow-up questions for a case.
- **Response Schema:** `List[FollowUpQuestionRead]`.

---

### 3.10 Triage Notes

#### `POST /api/v1/cases/{case_id}/triage-note`
- **Operation:** `add_triage_note`
- **Description:** Persists structured triage note. Enforces that AI advisory notes are never marked as clinician-reviewed.
- **Request Schema:**
  ```json
  {
    "summary": "Patient presented with acute dyspnea.",
    "acuity_assessment": "URGENT",
    "clinical_concerns": ["Pulmonary Edema"],
    "suggested_next_steps": ["Chest X-Ray", "IV Furosemide"],
    "author_type": "STAFF_ENTERED",
    "is_ai_generated": false
  }
  ```
- **Response Schema:** `TriageNoteRead`.

#### `GET /api/v1/cases/{case_id}/triage-note`
- **Operation:** `get_triage_notes`
- **Description:** Lists triage notes for a case.
- **Response Schema:** `List[TriageNoteRead]`.

---

### 3.11 Human Review Actions

#### `POST /api/v1/cases/{case_id}/review-actions`
- **Operation:** `submit_human_review_action`
- **Description:** Records qualified human review actions.
- **Allowed Vocabulary:** `VERIFY`, `MODIFY`, `REJECT`, `RESOLVE_CONFLICT`, `REQUEST_INFORMATION`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- **Server-Side Prohibited Actions:** `AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE` (Rejected with 422 `UNSUPPORTED_OPERATION`).
- **Request Schema:**
  ```json
  {
    "action": "VERIFY",
    "target_entity_type": "CASE",
    "target_entity_id": "uuid",
    "reason": "Clinician confirmed vitals and presentation",
    "notes": "Admitted for observation"
  }
  ```
- **Response Schema:** `ReviewActionRead`.

---

### 3.12 State Machine Transitions

#### `POST /api/v1/cases/{case_id}/transitions`
- **Operation:** `transition_case_state_endpoint`
- **Description:** Advances case workflow state via deterministic FSM with optimistic concurrency checking.
- **Allowed State Graph:**
  - `INTAKE_RECORDED` -> `START_TRIAGE` -> `TRIAGE_IN_PROGRESS`
  - `INTAKE_RECORDED` -> `ESCALATE` -> `CLINICIAN_REVIEW_REQUIRED`
  - `TRIAGE_IN_PROGRESS` -> `SUBMIT_TRIAGE` -> `CLINICIAN_REVIEW_REQUIRED`
  - `TRIAGE_IN_PROGRESS` -> `REQUEST_INFORMATION` -> `PENDING_INFORMATION`
  - `PENDING_INFORMATION` -> `PROVIDE_INFORMATION` -> `TRIAGE_IN_PROGRESS`
  - `CLINICIAN_REVIEW_REQUIRED` -> `START_REVIEW` -> `REVIEW_IN_PROGRESS`
  - `REVIEW_IN_PROGRESS` -> `CONTINUE` | `OBSERVE` | `ESCALATE` | `REFER` -> `DISPOSITION_PENDING`
  - `DISPOSITION_PENDING` -> `CLOSE_CASE` | `FINALIZE_DISPOSITION` -> `CLOSED`
- **Request Schema:**
  ```json
  {
    "action": "START_TRIAGE",
    "reason": "Nurse triage station intake",
    "expected_state_version": 1
  }
  ```
- **Response Schema:** `StateTransitionRead`.
- **Errors:** 409 `CONFLICT` (on version mismatch), 422 `INVALID_STATE_TRANSITION`, 403 `AUTHORIZATION_ERROR`.

---

### 3.13 Audit Ledger

#### `GET /api/v1/cases/{case_id}/audit`
- **Operation:** `get_case_audit_trail`
- **Description:** Retrieves immutable audit trail for a case (WHO, WHAT, WHEN, CASE, OBJECT, RESULT, CORRELATION ID).
- **Response Schema:** `List[AuditEventRead]`.
