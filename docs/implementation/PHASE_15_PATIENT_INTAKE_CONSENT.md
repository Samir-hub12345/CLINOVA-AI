# CLINOVA AI — Phase 15 Architecture & Implementation Record: Patient Intake, Informed Consent & Persistence

**Document ID:** CLINOVA-DOC-PHASE15-INTAKE-CONSENT  
**Status:** IMPLEMENTED & VERIFIED  
**Phase:** 15 (Strictly Atomic Phase 15 Boundary — No Phase 16 Advance)  
**Security Level:** Production-Hardened Clinical Advisory Architecture  
**Dependencies:** Phase 13 Core Backend Foundation, Phase 14 Auth & RBAC Hardening  
**Target Environment:** Local-First SQLite & Production PostgreSQL  

---

## 1. Executive Summary

Phase 15 delivers an enterprise-grade, patient-safe **Patient Intake, Informed Consent, Multi-Entity Persistence, and Master Case Initialization Subsystem** for CLINOVA AI. It operationalizes the intake gate of the clinical workflow, linking the frontend intake wizard with the canonical relational persistence layer established in Phase 13 and secured in Phase 14.

### Foundational Principles Enforced:
1. **Master Case as Canonical Root Aggregate:**
   Every intake creates or attaches to a canonical `Case` entity (`cases` table) with initial state `INTAKE_RECORDED`, status `NEW`, and `state_version = 1`. All clinical, demographic, consent, and audit records trace back to this single root aggregate.
2. **Clinical Resuscitation Before Administrative Completion:**
   Emergency and acute pathways (`EMERGENCY`) are strictly non-blocking. An unresponsive, unidentified, or critically ill patient can be admitted without requiring demographic completeness (such as name, phone number, address, or national ID). In emergency mode, informed consent is automatically defaulted to `IMPLIED_EMERGENCY`.
3. **Mandatory Symptoms for Non-Emergency Intake:**
   Intake payloads must contain non-empty, non-whitespace clinical symptoms. Blank or whitespace-only chief complaints are rejected at the API schema boundary with HTTP 422.
4. **Mandatory Informed Consent for Standard Care:**
   Non-emergency care pathways (`REGULAR_STANDARD`, `OPD_GENERAL`, `MATERNAL_CHILD`, `CHRONIC_CARE`) strictly mandate patient or proxy informed consent (`INFORMED_VERBAL`, `INFORMED_WRITTEN`, `DIGITAL_SIGNATURE`, `PROXY_CONSENT`). Unconsented non-emergency intakes are rejected with HTTP 422.
5. **Authoritative Server-Side RBAC & Patient Self-Scope:**
   Intake requires valid authentication with `Permission.CASE_CREATE`. Authenticated `PATIENT` users are restricted to submitting intake for their own linked patient profile. Healthcare workers (`CHW_ASHA`, `TRIAGE_NURSE`, `MO_PHYSICIAN`, `ADMIN`) can submit staff-assisted intakes for any patient.
6. **Atomic Transactional Multi-Entity Persistence:**
   Intake submissions atomically persist the patient demographic record, identifiers, encounter, canonical master case, initial state transition, consent record, evidence records, vitals (if captured), timeline events, and immutable audit logs within a single database transaction. Any downstream exception triggers a clean rollback with zero partial orphan records.
7. **Strict Phase Boundary (Zero Phase 16 Leakage):**
   Phase 15 strictly isolates intake capture and persistence. No triage scoring, vitals normalization, NEWS2 calculations, urgency classification, or triage queues are computed in Phase 15 (reserved for Phase 16).

---

## 2. Architecture & Data Flow

```
[ Frontend: PatientIntakeWizard / Staff Portal ]
                       │
                       │ POST /api/v1/intake/submit
                       ▼
[ Gateway / FastAPI Router: app/api/v1/endpoints/intake.py ]
   ├─► 1. Authenticate Bearer JWT & Check Permission (Permission.CASE_CREATE)
   ├─► 2. Patient Self-Scope Check (Reject cross-patient submission if PATIENT role)
   ├─► 3. Validate Payload (Compulsory symptoms, valid pathway, consent rules)
   ├─► 4. Check Idempotency (client_submission_id deduplication)
   │
   ├─► 5. ATOMIC DATABASE TRANSACTION (Unit of Work)
   │       ├─► Insert / Resolve Patient (patients)
   │       ├─► Insert Patient Identifier (patient_identifiers, if provided)
   │       ├─► Insert Encounter (encounters)
   │       ├─► Insert Canonical Case (cases: state=INTAKE_RECORDED, status=NEW, ver=1)
   │       ├─► Insert Case State Transition (case_state_transitions: NULL -> INTAKE_RECORDED)
   │       ├─► Insert Consent Record (consents: INFORMED_* or IMPLIED_EMERGENCY)
   │       ├─► Insert Clinical Evidence (evidence & legacy evidence_records)
   │       ├─► Insert Baseline Vitals (vitals & vital_readings, if provided)
   │       ├─► Insert Timeline Event (timeline_events: INTAKE_SUBMITTED)
   │       └─► Insert Audit Event (audit_events: intake.submitted)
   │
   └─► 6. Commit Transaction & Return PatientIntakeResponse (HTTP 201)
```

---

## 3. Schemas & Domain Models

### 3.1 Request & Response Schemas (`backend/app/schemas/intake.py`)

- `PatientIntakeRequest`: Canonical structured intake payload:
  - `patient_id`: Optional UUID (for existing patients).
  - `facility_id`: Mandatory UUID or facility identifier.
  - `care_pathway`: Enum (`REGULAR_STANDARD`, `OPD_GENERAL`, `EMERGENCY`, `MATERNAL_CHILD`, `CHRONIC_CARE`).
  - `demographics`: Demographic detail object (`first_name`, `last_name`, `estimated_age`, `gender`, `phone_number`, `national_id`, `address`, etc.).
  - `clinical_symptoms`: Mandatory string or list of symptoms (non-empty, non-whitespace, max 20,000 chars).
  - `symptom_duration_days`: Optional integer duration.
  - `is_emergency`: Boolean emergency flag (automatically activates emergency pathway if true).
  - `consent`: Structured consent object (`consent_obtained`, `consent_type`, `obtained_by`, `consent_scope`, `metadata`).
  - `vitals`: Optional baseline vitals captured during intake.
  - `client_submission_id`: Optional idempotency token.
- `FrontendIntakeSubmissionRequest`: Compatibility wrapper adapting frontend wizard field names (`fullName`, `chiefComplaint`, `medicalHistory`, `emergencyFlag`) to canonical intake schemas.
- `PatientIntakeResponse`: Standardized response containing `case_id`, `patient_id`, `encounter_id`, `facility_id`, `current_state`, `status`, `care_pathway`, `submission_id`, `created_at`, and `message`.

### 3.2 Persisted Relational Entities

| Entity / Table | Purpose in Phase 15 | Key Fields Recorded |
| :--- | :--- | :--- |
| `patients` | Demographic record | Name, gender, DOB / estimated age, phone, synthetic flag |
| `patient_identifiers` | Official identity | Identifier type (GOV_ID/NATIONAL_ID), value, issuing authority |
| `encounters` | Clinical encounter | Facility ID, patient ID, encounter type (`OUTPATIENT`/`EMERGENCY`), start time |
| `cases` | **Canonical Root Aggregate** | Patient ID, encounter ID, facility ID, current state (`INTAKE_RECORDED`), status (`NEW`), version (`1`) |
| `case_state_transitions` | State machine audit | From state (`None`), To state (`INTAKE_RECORDED`), trigger (`INTAKE_SUBMITTED`), actor ID |
| `consents` | Legal & ethical consent | Consent type (`INFORMED_WRITTEN`/`IMPLIED_EMERGENCY`), scope (`INTAKE_AND_TRIAGE`), status (`ACTIVE`) |
| `evidence` | Clinical symptom records | Evidence type (`CHIEF_COMPLAINT`), source class (`PATIENT_REPORTED`/`STAFF_ENTERED`), payload JSON |
| `vitals` | Optional intake vitals | Recorded at, HR, SBP, DBP, RR, SpO2, Temperature |
| `timeline_events` | Longitudinal patient event | Event type (`INTAKE_SUBMITTED`), description, actor ID, payload JSON |
| `audit_events` | Regulatory compliance audit | Action (`intake.submitted`), actor ID, facility ID, resource type (`case`), client IP |

---

## 4. Clinical Safety & Error Recovery

### 4.1 Resuscitation Over Administration
In acute clinical presentations, seconds matter. Demanding a patient's full name, national identification number, or address before initiating an emergency case violates medical ethics.
- **Implementation:** When `care_pathway == "EMERGENCY"` or `is_emergency == True`:
  - Demographic fields default gracefully to anonymous placeholders (e.g., `"Unknown (Emergency)"`).
  - Consent requirement defaults to `ConsentType.IMPLIED_EMERGENCY` without blocking clinical care.
  - Case is immediately persisted and available for clinical intervention.

### 4.2 Compulsory Symptoms Validation
A clinical intake cannot be opened without documented complaints.
- Rejects missing `clinical_symptoms` field.
- Rejects whitespace-only strings (e.g., `"   "`).
- Rejects empty arrays (e.g., `[]`).
- Enforces character upper limit (20,000 characters) to prevent database denial-of-service.

### 4.3 Idempotency & Repeat Submissions
Intermittent connectivity in rural primary health centers (PHCs) frequently causes double-clicks or client retries.
- Every submission can supply a `client_submission_id`.
- If a submission with the same `client_submission_id` and `facility_id` has already been recorded within the deduplication window, the system returns the existing case without generating duplicate records.

### 4.4 Transaction Atomicity & Rollback Integrity
Intake updates 8+ tables. If any step fails (e.g., invalid data format, disk full, constraint violation):
- The entire transaction is rolled back via `db.rollback()`.
- Zero orphan `patients` or dangling `cases` remain in the database.
- A structured HTTP 500 or 422 error is returned to the client.

---

## 5. Frontend Integration & Error Transparency

### 5.1 API Client Hardening (`frontend/src/lib/api.ts`)
- Upgraded `safeFetch` to expose `isHttpError` and HTTP status codes (`status: response.status`).
- `submitPatientIntake`:
  - Automatically manages authentication, obtaining demo tokens if unauthenticated.
  - Distinguishes 4xx validation errors from network outages.
  - Directly propagates backend 4xx error messages (e.g., "Symptoms/chief complaints are mandatory") to the wizard UI so users can correct input errors.
  - Falls back to offline mock mode **only** on true network connection failures (when the server cannot be reached).

### 5.2 Patient Intake Wizard (`frontend/src/components/patient/PatientIntakeWizard.tsx`)
- Displays structured `AlertBanner` when the server returns validation errors.
- Retains user-entered form data across submission attempts so clinical staff or patients do not lose entered history.

---

## 6. Verification & Test Coverage Matrix

The Phase 15 implementation is verified by 31 dedicated automated test scenarios in `backend/tests/test_phase15_intake.py` and regression-tested against the Phase 13 and Phase 14 test suites.

| Scenario ID | Test Function | Purpose / Validation Checked | Result |
| :--- | :--- | :--- | :--- |
| **A** | `test_scenario_a_valid_patient_intake` | Valid self-service patient intake persists successfully | **PASSED** |
| **B** | `test_scenario_b_valid_staff_assisted_intake` | Valid staff-assisted intake persists successfully | **PASSED** |
| **C** | `test_scenario_c_regular_pathway_persisted` | Regular standard pathway persists correct metadata | **PASSED** |
| **D** | `test_scenario_d_emergency_pathway_persisted` | Emergency pathway sets implied consent and persists | **PASSED** |
| **E** | `test_scenario_e_missing_symptoms_rejected` | Missing symptoms field rejected with HTTP 422 | **PASSED** |
| **F** | `test_scenario_f_whitespace_only_symptoms_rejected` | Whitespace-only symptoms rejected with HTTP 422 | **PASSED** |
| **G** | `test_scenario_g_invalid_payload_rejected` | Invalid payload structure rejected with HTTP 422 | **PASSED** |
| **H** | `test_scenario_h_consent_required` | Non-emergency intake without consent rejected (422) | **PASSED** |
| **I** | `test_scenario_i_consent_persisted` | Consent record accurately persisted in database | **PASSED** |
| **J** | `test_scenario_j_consent_metadata_persisted` | Consent metadata (facility, timestamp) persisted | **PASSED** |
| **K** | `test_scenario_k_patient_persisted` | Patient record correctly created and queryable | **PASSED** |
| **L** | `test_scenario_l_encounter_persisted` | Encounter record created with correct facility scope | **PASSED** |
| **M** | `test_scenario_m_canonical_master_case_persisted` | Canonical root Case entity persisted with IDs | **PASSED** |
| **N** | `test_scenario_n_correct_initial_case_state` | Initial state is `INTAKE_RECORDED` and status `NEW` | **PASSED** |
| **O** | `test_scenario_o_correct_state_version` | Initial state version is exactly `1` | **PASSED** |
| **P** | `test_scenario_p_provenance_preserved` | Evidence source class tracks reported vs staff origin with KNOWN epistemic state | **PASSED** |
| **Q** | `test_scenario_q_timeline_event_created` | Timeline records all milestone events (INTAKE_SUBMITTED, CONSENT_RECORDED, CASE_CREATED) | **PASSED** |
| **R** | `test_scenario_r_audit_event_created` | Audit trail records patient, encounter, case, consent, and intake events | **PASSED** |
| **S** | `test_scenario_s_transaction_rollback_on_downstream_failure` | Exception during intake triggers full atomic rollback of patient and case | **PASSED** |
| **T** | `test_scenario_t_duplicate_repeat_handling` | Duplicate `client_submission_id` handled idempotently without creating orphan patients | **PASSED** |
| **U** | `test_scenario_u_unauthorized_patient_access_denied` | Unauthenticated request or role without CASE_CREATE rejected (401/403) | **PASSED** |
| **V** | `test_scenario_v_cross_patient_access_denied` | Patient cannot submit intake for a different patient ID or unlinked account (403) | **PASSED** |
| **W** | `test_scenario_w_staff_authorization_works` | Nurse / MO / ASHA authorized to submit assisted intake | **PASSED** |
| **X** | `test_scenario_x_old_actor_header_spoofing_cannot_bypass_phase14_security` | Old `X-Actor-Role` header spoofing rejected under strict Phase 14 auth | **PASSED** |
| **Y** | `test_scenario_y_synthetic_mode_preserved` | Synthetic patient flags and records preserved | **PASSED** |
| **Z** | `test_scenario_z_frontend_intake_api_integration` | Frontend payload format parsed and processed | **PASSED** |
| **AA** | `test_scenario_aa_structured_validation_errors` | Structured validation errors returned with details | **PASSED** |
| **AB** | `test_scenario_ab_backend_unavailable_handling` | Offline mock conformance and graceful 404 error recovery | **PASSED** |
| **AC** | `test_scenario_ac_emergency_administrative_incompleteness` | Resuscitation priority: empty demographics allowed in ER | **PASSED** |
| **AD** | `test_scenario_ad_no_secret_credential_leakage` | Intake responses leak zero secrets or tokens | **PASSED** |
| **AE** | `test_scenario_ae_no_real_pii_requirement` | Zero real PII required for synthetic clinical runs | **PASSED** |

---

## 7. Compliance & Phase Boundary Sign-Off

- **Phase 13 Invariants Maintained:** Case remains canonical root aggregate. Relational schema models preserved without breaking changes.
- **Phase 14 Invariants Maintained:** Server-side JWT authentication, facility isolation, RBAC role derivation, non-diagnostic guardrails, zero privilege escalation.
- **Phase 16 Exclusions:** No triage scores, NEWS2 calculations, vitals anomaly scores, or queue placements have been implemented.
- **Status:** **PHASE 15 STATUS: READY FOR HUMAN REVIEW**
