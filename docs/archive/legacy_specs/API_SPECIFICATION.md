# CLINOVA AI — REST API Specification

**Document Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api/v1`  
**OpenAPI / Interactive Docs:** `http://localhost:8000/docs`  
**ReDoc Reference:** `http://localhost:8000/redoc`  
**Schema Definition:** OpenAPI 3.1.0 via `/api/v1/openapi.json`

---

> [!WARNING]
> ### 🔒 Clinical Decision Support Notice
> **All API outputs from CLINOVA AI are strictly intended for clinical decision support and information organization. They do NOT constitute autonomous medical diagnoses, treatment prescriptions, or definitive triage dispositions.**
> Every triage suggestion, risk signal, and synthesized note requires physical inspection, clinical verification, and explicit sign-off by a qualified healthcare professional before taking medical action.

---

## Table of Contents

1. [Authentication & Authorization](#1-authentication--authorization)
2. [Global Error & Status Formats](#2-global-error--status-formats)
3. [API Endpoint Reference Matrix](#3-api-endpoint-reference-matrix)
4. [Service Health & System Status](#4-service-health--system-status)
5. [Authentication Endpoints (`/api/v1/auth`)](#5-authentication-endpoints-apiv1auth)
6. [Multimodal Intake Ingestion (`/api/v1/intake`)](#6-multimodal-intake-ingestion-apiv1intake)
7. [Triage Cases & Priority Queue (`/api/v1/cases`)](#7-triage-cases--priority-queue-apiv1cases)
8. [Clinical Review & Referral Support (`/api/v1/review`)](#8-clinical-review--referral-support-apiv1review)
9. [AI Clinical Decision Support (`/api/v1/ai`)](#9-ai-clinical-decision-support-apiv1ai)
10. [Patient Registry & EHR Charts (`/api/v1/patients`)](#10-patient-registry--ehr-charts-apiv1patients)
11. [Clinical Encounters & Consultations (`/api/v1/consultations`)](#11-clinical-encounters--consultations-apiv1consultations)
12. [Medicolegal Audit Trail (`/api/v1/audit-logs`)](#12-medicolegal-audit-trail-apiv1audit-logs)
13. [Planned But Not Yet Implemented Endpoints](#13-planned-but-not-yet-implemented-endpoints)

---

## 1. Authentication & Authorization

### 1.1 Authentication Protocol
CLINOVA AI uses **JSON Web Tokens (JWT)** signed via HMAC-SHA256 (`HS256`).

- **Header Name:** `Authorization`
- **Format:** `Bearer <token>`
- **Token Lifespan:** Configurable (default: 60 minutes via `ACCESS_TOKEN_EXPIRE_MINUTES`).

```http
GET /api/v1/auth/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.2 Role-Based Access Control (RBAC)
User permissions are enforced at the endpoint dependency level:

| Role Identifier | Permissions Scope |
| :--- | :--- |
| `doctor` | Unrestricted clinical access: review gate approval, patient EHR modifications, consultation finalization, patient record deletion. |
| `nurse` | Clinical triage operations: intake processing, triage queue access, consultation notes, patient registration. |
| `admin` | Administrative and system oversight: audit log analysis, facility user management. |
| `patient` | Restricted access: view personal linked EHR chart and personal consultation encounters only. |

*Note: Public endpoints (Intake ingestion `/api/v1/intake/*`, case submission `POST /api/v1/cases/`, and health checks) do not require Bearer tokens to support kiosk and walk-in patient workflows.*

---

## 2. Global Error & Status Formats

All error responses adhere to standard FastAPI JSON formatting with appropriate HTTP status codes.

### 2.1 Standard Error Response Structure
```json
{
  "detail": "Descriptive explanation of the error condition."
}
```

### 2.2 Common Status Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `204 No Content`: Resource successfully deleted.
- `400 Bad Request`: Validation failure, duplicate resource, or missing required parameter.
- `401 Unauthorized`: Missing, expired, or malformed JWT access token.
- `403 Forbidden`: Authenticated user lacks required clinical role privileges.
- `404 Not Found`: Resource ID does not exist in the database.
- `422 Unprocessable Entity`: Request body failed Pydantic schema validation.
- `500 Internal Server Error`: Unexpected server or database exception.

---

## 3. API Endpoint Reference Matrix

| Method | Endpoint Path | Tags | Access Control | Summary |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Root | Public | Root welcome status and service metadata |
| `GET` | `/api/v1/health` | Health | Public | Liveness probe and database service health |
| `POST` | `/api/v1/auth/register` | Authentication | Public | Register a new user account |
| `POST` | `/api/v1/auth/login` | Authentication | Public | Authenticate user and receive JWT access token |
| `GET` | `/api/v1/auth/me` | Authentication | Authenticated | Retrieve current user profile and role |
| `GET` | `/api/v1/auth/users` | Authentication | Admin | Retrieve all facility user accounts |
| `PUT` | `/api/v1/auth/users/{user_id}/status` | Authentication | Admin | Activate or deactivate a user account |
| `POST` | `/api/v1/intake/speech` | Multimodal Intake | Public / Kiosk | Transcribe spoken audio (Odia, Hindi, English) |
| `POST` | `/api/v1/intake/translate` | Multimodal Intake | Public / Kiosk | Normalize vernacular symptoms into clinical English |
| `POST` | `/api/v1/intake/ocr` | Multimodal Intake | Public / Kiosk | Parse CBC pathology reports with confidence metrics |
| `POST` | `/api/v1/cases/` | Triage Cases | Public / Patient | Create triage case with PII scrub and AI synthesis |
| `GET` | `/api/v1/cases/` | Triage Cases | Role-Enforced | List triage cases (isolated by patient_id for patients) |
| `GET` | `/api/v1/cases/{case_id}` | Triage Cases | Role-Enforced | Retrieve case (patient isolation enforced) |
| `POST` | `/api/v1/cases/{case_id}/assign` | Triage Cases | Clinician / Staff | Assign case to attending physician & department |
| `POST` | `/api/v1/cases/{case_id}/verify-intake` | Triage Cases | Clinician / Staff | Verify intake, record vitals, and hand off |
| `DELETE`| `/api/v1/cases/{case_id}` | Triage Cases | Clinician | One-click retention data purge |
| `POST` | `/api/v1/review/{case_id}/action`| Reviewer | Clinician (`doctor`, `nurse`, `admin`) | Execute human review action (Approve, Edit, Reject, Escalate) |
| `GET` | `/api/v1/review/{case_id}/referral`| Reviewer | Patient / Clinician | Retrieve structured printable referral support document |
| `POST` | `/api/v1/ai/triage` | AI Support | Clinician | Generate urgency score, emergency flags, and differentials |
| `POST` | `/api/v1/ai/soap-summary` | AI Support | Clinician | Synthesize clinical notes into structured SOAP format |
| `GET` | `/api/v1/patients` | Patients EHR | Clinician | Search and list patient registry records |
| `POST` | `/api/v1/patients` | Patients EHR | Clinician | Create a new patient EHR chart |
| `GET` | `/api/v1/patients/me` | Patients EHR | Authenticated | Retrieve current user's linked clinical chart |
| `GET` | `/api/v1/patients/{patient_id}` | Patients EHR | Authenticated | Retrieve patient medical chart and history |
| `PUT` | `/api/v1/patients/{patient_id}` | Patients EHR | Clinician | Update patient demographics and medical history |
| `DELETE`| `/api/v1/patients/{patient_id}` | Patients EHR | Doctor | Delete or archive a patient record |
| `GET` | `/api/v1/consultations` | Consultations | Authenticated | List consultations with optional status/urgency filters |
| `POST` | `/api/v1/consultations` | Consultations | Clinician | Create and schedule a new clinical consultation |
| `GET` | `/api/v1/consultations/{id}` | Consultations | Authenticated | Retrieve full consultation details and clinical notes |
| `PUT` | `/api/v1/consultations/{id}` | Consultations | Clinician | Update encounter vitals, triage level, or status |
| `PUT` | `/api/v1/consultations/{id}/soap` | Consultations | Clinician | Directly save and sign clinical SOAP notes |
| `GET` | `/api/v1/audit-logs` | Audit Trail | Clinician / Admin | Query immutable compliance audit logs |

---

## 4. Service Health & System Status

### 4.1 Root Welcome
- **Method:** `GET`
- **Path:** `/`
- **Access:** Public

#### Response Example (`200 OK`):
```json
{
  "message": "Welcome to Clinova AI API",
  "docs": "/docs",
  "version": "0.1.0",
  "status": "online"
}
```

### 4.2 Health Check
- **Method:** `GET`
- **Path:** `/api/v1/health`
- **Access:** Public

#### Response Example (`200 OK`):
```json
{
  "status": "healthy",
  "app_name": "Clinova AI",
  "environment": "development",
  "version": "0.1.0",
  "timestamp": "2026-09-18T19:30:00.000Z"
}
```

---

## 5. Authentication Endpoints (`/api/v1/auth`)

### 5.1 Register User Account
- **Method:** `POST`
- **Path:** `/api/v1/auth/register`
- **Access:** Public
- **Status Code:** `201 Created`

#### Request Body:
```json
{
  "email": "doctor.sharma@clinova.ai",
  "password": "SecurePassword2026!",
  "full_name": "Dr. Rajesh Sharma, MD",
  "role": "doctor"
}
```
*Valid roles: `"doctor"`, `"nurse"`, `"patient"`, `"admin"`.*

#### Response Example (`201 Created`):
```json
{
  "id": "c1f72a4e-1234-4567-89ab-cdef01234567",
  "email": "doctor.sharma@clinova.ai",
  "full_name": "Dr. Rajesh Sharma, MD",
  "role": "doctor",
  "is_active": true,
  "created_at": "2026-09-18T19:30:00.000Z",
  "updated_at": "2026-09-18T19:30:00.000Z"
}
```

### 5.2 User Login
- **Method:** `POST`
- **Path:** `/api/v1/auth/login`
- **Access:** Public
- **Input Formats:** Accepts JSON body (`LoginRequest`) or OAuth2 form-urlencoded (`username` & `password`).

#### Request Body (JSON):
```json
{
  "email": "doctor@clinova.ai",
  "password": "ClinovaDoctor2026!"
}
```

#### Response Example (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODQz...",
  "token_type": "bearer",
  "user": {
    "id": "d843bb35-512c-473d-bc69-26dcae32d0f5",
    "email": "doctor@clinova.ai",
    "full_name": "Dr. Sarah Chen, MD",
    "role": "doctor",
    "is_active": true,
    "created_at": "2026-09-18T19:00:00.000Z",
    "updated_at": "2026-09-18T19:00:00.000Z"
  }
}
```

### 5.3 Current User Profile
- **Method:** `GET`
- **Path:** `/api/v1/auth/me`
- **Access:** Authenticated (Bearer Token required)

#### Response Example (`200 OK`):
```json
{
  "id": "d843bb35-512c-473d-bc69-26dcae32d0f5",
  "email": "doctor@clinova.ai",
  "full_name": "Dr. Sarah Chen, MD",
  "role": "doctor",
  "is_active": true,
  "created_at": "2026-09-18T19:00:00.000Z",
  "updated_at": "2026-09-18T19:00:00.000Z"
}
```

---

## 6. Multimodal Intake Ingestion (`/api/v1/intake`)

### 6.1 Audio Speech Transcription
- **Method:** `POST`
- **Path:** `/api/v1/intake/speech`
- **Access:** Public / Kiosk
- **Content-Type:** `multipart/form-data`

#### Form Parameters:
- `file`: *(Optional)* Audio file upload (`.wav`, `.webm`, `.mp3`).
- `language_hint`: *(Optional)* Language code string (`"or"` for Odia, `"hi"` for Hindi, `"en"` for English). Default is `"en"`.

#### Response Example (`200 OK`):
```json
{
  "transcript": "ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି, ମୁଣ୍ଡ ବିନ୍ଧା ହେଉଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
  "detected_language": "Odia",
  "confidence": 0.94,
  "duration_seconds": 14.2,
  "is_demo_fallback": true,
  "disclaimer": "Speech transcription — review before submission."
}
```

### 6.2 Vernacular Translation & Normalization
- **Method:** `POST`
- **Path:** `/api/v1/intake/translate`
- **Access:** Public / Kiosk
- **Content-Type:** `application/json`

#### Request Body:
```json
{
  "text": "ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
  "source_language": "or"
}
```

#### Response Example (`200 OK`):
```json
{
  "original_text": "ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
  "original_language": "Odia",
  "translated_text": "Patient reports high fever for 3 days, severe headache, generalized body weakness, and progressive shortness of breath upon minimal exertion.",
  "target_language": "en",
  "normalization_summary": "Normalized from Odia regional dialect to clinical English representation.",
  "is_demo_fallback": true
}
```

### 6.3 Pathology Report OCR Extraction
- **Method:** `POST`
- **Path:** `/api/v1/intake/ocr`
- **Access:** Public / Kiosk
- **Content-Type:** `multipart/form-data`

#### Form Parameters:
- `file`: *(Optional)* Lab report image or document (`.png`, `.jpg`, `.pdf`).

#### Response Example (`200 OK`):
```json
{
  "report_filename": "report_sample.png",
  "fields": [
    {
      "field_name": "Hemoglobin (Hb)",
      "value": "12.4",
      "unit": "g/dL",
      "confidence": 0.94,
      "bounding_box": [140, 210, 360, 245],
      "verification_status": "pending",
      "source_reference": "Complete Blood Count (CBC) Panel"
    },
    {
      "field_name": "Total Leukocyte Count (WBC)",
      "value": "7.2",
      "unit": "x10^3/uL",
      "confidence": 0.91,
      "bounding_box": [140, 255, 360, 290],
      "verification_status": "pending",
      "source_reference": "Complete Blood Count (CBC) Panel"
    },
    {
      "field_name": "Platelet Count",
      "value": "220",
      "unit": "x10^3/uL",
      "confidence": 0.95,
      "bounding_box": [140, 300, 360, 335],
      "verification_status": "pending",
      "source_reference": "Complete Blood Count (CBC) Panel"
    },
    {
      "field_name": "Red Blood Cell Count (RBC)",
      "value": "4.5",
      "unit": "x10^6/uL",
      "confidence": 0.93,
      "bounding_box": [140, 345, 360, 380],
      "verification_status": "pending",
      "source_reference": "Complete Blood Count (CBC) Panel"
    }
  ],
  "raw_extracted_text": "CENTRAL PATHOLOGY LABORATORY - PUBLIC HEALTH FACILITY\nHemoglobin: 12.4 g/dL...",
  "confidence_average": 0.932,
  "is_synthetic_sample": true,
  "status": "success",
  "disclaimer": "Synthetic sample — not a real medical record. Requires qualified reviewer verification."
}
```

---

## 7. Triage Cases & Priority Queue (`/api/v1/cases`)

### 7.1 Submit Multimodal Triage Case
- **Method:** `POST`
- **Path:** `/api/v1/cases/`
- **Access:** Public / Kiosk
- **Status Code:** `201 Created`
- **Description:** Redacts PII in-flight, assigns synthetic ID (`CLV-DEMO-xxx`), matches deterministic rules (`TRIAGE-R01` to `R06`), and creates an intake record.

#### Request Body:
```json
{
  "facility_type": "Government District Hospital",
  "visit_type": "Outpatient Triage",
  "preferred_language": "or",
  "consent_acknowledged": true,
  "approximate_age": 21,
  "gender": "Male",
  "context_notes": "Student reporting acute fever in university hostel.",
  "raw_symptoms": "High fever for 3 days with shortness of breath. Phone: 9876543210",
  "speech_transcript": "ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
  "detected_language": "Odia",
  "report_filename": "cbc_sample.png",
  "report_ocr_data": [
    {
      "field_name": "Hemoglobin (Hb)",
      "value": "12.4",
      "unit": "g/dL",
      "confidence": 0.94,
      "verification_status": "pending"
    }
  ]
}
```

#### Response Example (`201 Created`):
```json
{
  "id": "e82d3e41-0123-4567-89ab-cdef01234567",
  "synthetic_case_id": "CLV-DEMO-482",
  "language": "or",
  "facility_type": "Government District Hospital",
  "visit_type": "Outpatient Triage",
  "status": "awaiting_review",
  "queue_category": "urgent-review",
  "queue_reason": "TRIAGE-R01: Potential breathing-related urgency signal detected",
  "consent_status": true,
  "approximate_age": 21,
  "gender": "Male",
  "context_notes": "Student reporting acute fever in university hostel.",
  "raw_symptoms": "High fever for 3 days with shortness of breath. Phone: [PHONE_REMOVED]",
  "normalized_symptoms": "Patient (21yo Male) presenting for Outpatient Triage at Government District Hospital. Reported symptoms: High fever for 3 days with shortness of breath. Phone: [PHONE_REMOVED]. Voice transcript captured. 1 laboratory parameters extracted via OCR. Organized for qualified medical officer evaluation.",
  "speech_transcript": "ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
  "detected_language": "Odia",
  "report_filename": "cbc_sample.png",
  "report_ocr_data": [
    {
      "field_name": "Hemoglobin (Hb)",
      "value": "12.4",
      "unit": "g/dL",
      "confidence": 0.94,
      "verification_status": "pending"
    }
  ],
  "missing_information": [
    "Subjective symptom severity score (1-10)",
    "Current daily prescription or over-the-counter medications"
  ],
  "follow_up_questions": [
    "On a scale of 1 to 10, how severe is the primary discomfort right now?",
    "Is the patient currently taking any daily medicines or home remedies?"
  ],
  "risk_signals": [
    {
      "rule_id": "TRIAGE-R01",
      "signal": "Potential breathing-related urgency signal detected",
      "source_text": "shortness of breath",
      "severity": "URGENT REVIEW",
      "timestamp": "19:35:10",
      "reviewer_confirmation_required": true,
      "status": "pending_confirmation"
    }
  ],
  "timeline_events": [
    {
      "day": "Day 1",
      "description": "Patient notes onset of primary discomfort and initial symptoms.",
      "source": "Patient history"
    },
    {
      "day": "Day 2",
      "description": "Symptoms persist; patient notes worsening discomfort.",
      "source": "Patient history"
    },
    {
      "day": "Day 3 (Today)",
      "description": "Presenting to Government District Hospital for clinical intake.",
      "source": "Current intake"
    }
  ],
  "waiting_minutes": 0,
  "is_deleted": false,
  "created_at": "2026-09-18T19:35:10.000Z",
  "updated_at": "2026-09-18T19:35:10.000Z"
}
```

### 7.2 List Prioritized Case Queue
- **Method:** `GET`
- **Path:** `/api/v1/cases/`
- **Access:** Public / Clinician
- **Query Parameters:**
  - `queue_category`: *(Optional)* Filter by category (`"urgent-review"`, `"priority"`, `"routine"`).
  - `status_filter`: *(Optional)* Filter by status (`"awaiting_review"`, `"in_review"`, `"approved"`, `"rejected"`, `"referred"`).
  - `limit`: *(Optional)* Integer ($1 - 100$, default: $50$).

#### Response Example (`200 OK`):
Returns an array of `CaseResponse` objects sorted by urgency and creation timestamp.

### 7.3 Get Triage Case by ID
- **Method:** `GET`
- **Path:** `/api/v1/cases/{case_id}`
- **Access:** Public / Clinician
- **Path Parameter:** `case_id` (Accepts either internal UUID or `synthetic_case_id`, e.g., `CLV-DEMO-001`).

### 7.4 Delete Case / Retention Data Purge
- **Method:** `DELETE`
- **Path:** `/api/v1/cases/{case_id}`
- **Access:** Clinician
- **Description:** Deletes temporary media, purges raw symptom text (`[DELETED PER RETENTION POLICY]`), and sets `is_deleted = True`.

#### Response Example (`200 OK`):
```json
{
  "status": "success",
  "case_id": "CLV-DEMO-001",
  "message": "Temporary media and intake symptoms purged successfully per privacy policy."
}
```

---

## 8. Clinical Review & Referral Support (`/api/v1/review`)

### 8.1 Execute Human Review Action
- **Method:** `POST`
- **Path:** `/api/v1/review/{case_id}/action`
- **Access:** Doctor / Nurse
- **Description:** Mandatory human gate interface for medical officers.

#### Request Body:
```json
{
  "action": "approve",
  "reviewer_notes": "Clinical summary reviewed and verified. Oxygen saturation stable at 97%.",
  "confirmed_queue_category": "priority",
  "edited_summary": null
}
```
*Valid actions: `"approve"`, `"edit"`, `"reject"`, `"escalate"`.*

#### Response Example (`200 OK`):
Returns updated `CaseResponse` object reflecting the new status (`"approved"`, `"in_review"`, `"rejected"`, or `"referred"`).

### 8.2 Retrieve Standardized Referral Note
- **Method:** `GET`
- **Path:** `/api/v1/review/{case_id}/referral`
- **Access:** Public / Clinician
- **Description:** Generates an official, printable referral support document for hospital transfer.

#### Response Example (`200 OK`):
```json
{
  "case_id": "e82d3e41-0123-4567-89ab-cdef01234567",
  "synthetic_case_id": "CLV-DEMO-001",
  "facility": "Campus Health Center",
  "visit_type": "Campus Fever Triage",
  "patient_reported_symptoms": "High fever for 3 days, headache, and shortness of breath upon exertion.",
  "timeline": [
    {
      "day": "Day 1",
      "description": "Onset of high fever",
      "source": "Patient history"
    }
  ],
  "available_report_data": [
    {
      "field_name": "Hemoglobin (Hb)",
      "value": "12.4",
      "unit": "g/dL",
      "confidence": 0.94,
      "verification_status": "confirmed"
    }
  ],
  "reviewer_confirmed_summary": "Patient reports high fever for 3 days with progressive shortness of breath.",
  "outstanding_questions": [
    "On a scale of 1 to 10, how severe is the primary discomfort right now?"
  ],
  "review_signals": [
    {
      "rule_id": "TRIAGE-R01",
      "signal": "Potential breathing-related urgency signal detected",
      "severity": "URGENT REVIEW",
      "source_text": "shortness of breath"
    }
  ],
  "reviewer_reason": "Clinical referral prepared for secondary healthcare facility review.",
  "reviewer_name": "Dr. S. Chen, Medical Officer",
  "reviewer_role": "Medical Officer",
  "timestamp": "2026-09-18 19:40:00 UTC",
  "footer_disclaimer": "AI-assisted organization of information. Not a diagnosis or treatment recommendation. Final referral decision is made by qualified healthcare staff."
}
```

---

## 9. AI Clinical Decision Support (`/api/v1/ai`)

### 9.1 Perform AI Triage Analysis
- **Method:** `POST`
- **Path:** `/api/v1/ai/triage`
- **Access:** Clinician
- **Query Parameter:** `consultation_id`: *(Optional)* UUID of linked consultation.

#### Request Body:
```json
{
  "patient_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "chief_complaint": "Acute retrosternal chest pain",
  "symptoms": ["chest pain", "sweating", "pain radiating to left arm"],
  "symptom_duration": "45 minutes",
  "age": 58,
  "gender": "Male",
  "relevant_medical_history": "Hypertension, Hyperlipidemia",
  "known_allergies": "Penicillin",
  "vitals": {
    "blood_pressure_systolic": 165,
    "blood_pressure_diastolic": 102,
    "heart_rate": 110,
    "respiratory_rate": 22,
    "oxygen_saturation": 95.0,
    "temperature": 37.1
  }
}
```

#### Response Example (`200 OK`):
```json
{
  "urgency_level": "CRITICAL",
  "urgency_color": "Rose",
  "emergency_red_flags": [
    "High suspicion of Acute Coronary Syndrome (ACS / STEMI)",
    "Severe chest pain radiating to left arm with diaphoresis"
  ],
  "differential_diagnoses": [
    {
      "condition": "Acute Coronary Syndrome (ACS / STEMI)",
      "probability": "High",
      "rationale": "Crushing chest pain with diaphoresis and radiation in a 58yo hypertensive male.",
      "recommended_workup": [
        "STAT 12-lead ECG within 10 minutes",
        "Serial High-Sensitivity Cardiac Troponin",
        "Chest Radiograph"
      ]
    },
    {
      "condition": "Aortic Dissection",
      "probability": "Moderate",
      "rationale": "Severe chest pain in the presence of elevated blood pressure.",
      "recommended_workup": ["CT Angiography of Chest"]
    }
  ],
  "immediate_actions": [
    "Acquire 12-lead ECG immediately",
    "Establish large-bore IV access",
    "Administer Aspirin 325mg orally if not contraindicated",
    "Initiate continuous cardiac telemetry"
  ],
  "clinical_reasoning": "Presentation meets high-acuity cardiovascular criteria.",
  "suggested_monitoring": [
    "Continuous Pulse Oximetry",
    "Serial Blood Pressure every 15 minutes"
  ],
  "disclaimer": "Educational prototype and clinical decision support only. Requires physician evaluation.",
  "source": "Clinova Clinical Decision Engine"
}
```

### 9.2 Synthesize SOAP Notes
- **Method:** `POST`
- **Path:** `/api/v1/ai/soap-summary`
- **Access:** Clinician

#### Request Body:
```json
{
  "patient_name": "James Miller",
  "age_and_gender": "42yo Male",
  "chief_complaint": "Follow-up for essential hypertension",
  "encounter_notes": "Patient reports taking Lisinopril regularly. Denies headaches, visual changes, or chest discomfort. BP today is 130/82 mmHg.",
  "medical_history": "Hypertension diagnosed 2018",
  "vitals": {
    "blood_pressure_systolic": 130,
    "blood_pressure_diastolic": 82,
    "heart_rate": 72,
    "oxygen_saturation": 98.0
  }
}
```

#### Response Example (`200 OK`):
```json
{
  "subjective": "PATIENT: James Miller\nCHIEF COMPLAINT: Follow-up for essential hypertension\nHISTORY: Compliant with Lisinopril. Denies acute symptoms.",
  "objective": "VITALS: BP 130/82 mmHg, HR 72 bpm, SpO2 98%.\nPHYSICAL EXAM: Alert, oriented, in no acute distress.",
  "assessment": "PRIMARY IMPRESSION: Essential hypertension, clinically stable on current medication regimen.",
  "plan": "1. Continue Lisinopril 10mg PO daily.\n2. Repeat lipid and metabolic panel in 6 months.\n3. Return for clinical check-up in 6 months.",
  "patient_friendly_summary": "Your blood pressure is currently well-controlled on your current medicine. Continue taking your daily pills and return in 6 months.",
  "disclaimer": "AI-generated clinical draft. Must be reviewed and signed by attending clinician."
}
```

---

## 10. Patient Registry & EHR Charts (`/api/v1/patients`)

### 10.1 List & Search Patients
- **Method:** `GET`
- **Path:** `/api/v1/patients`
- **Access:** Clinician
- **Query Parameters:**
  - `q`: *(Optional)* Name or MRN search query.
  - `skip`: *(Optional)* Offset integer (default: 0).
  - `limit`: *(Optional)* Count integer ($1 - 100$, default: 50).

#### Response Example (`200 OK`):
```json
{
  "total": 1,
  "items": [
    {
      "id": "a3b1c2d3-4567-89ab-cdef-0123456789ab",
      "mrn": "CLN-2026-10482",
      "first_name": "James",
      "last_name": "Miller",
      "date_of_birth": "1982-06-14",
      "gender": "Male",
      "blood_group": "O+",
      "phone": "+1 (555) 234-5678",
      "email": "patient@clinova.ai",
      "emergency_contact": "Sarah Miller (Spouse): +1 (555) 234-5679",
      "allergies": "Penicillin (Anaphylaxis)",
      "current_medications": "Lisinopril 10mg daily",
      "medical_history": "Hypertension",
      "created_at": "2026-09-18T19:00:00.000Z",
      "updated_at": "2026-09-18T19:00:00.000Z"
    }
  ]
}
```

### 10.2 Create Patient EHR Record
- **Method:** `POST`
- **Path:** `/api/v1/patients`
- **Access:** Clinician
- **Status Code:** `201 Created`

### 10.3 Get Patient Profile
- **Method:** `GET`
- **Path:** `/api/v1/patients/{patient_id}`
- **Access:** Authenticated (Clinicians, or Patient accessing their own record)

### 10.4 Update Patient Record
- **Method:** `PUT`
- **Path:** `/api/v1/patients/{patient_id}`
- **Access:** Clinician

### 10.5 Delete Patient Record
- **Method:** `DELETE`
- **Path:** `/api/v1/patients/{patient_id}`
- **Access:** Doctor only
- **Status Code:** `204 No Content`

---

## 11. Clinical Encounters & Consultations (`/api/v1/consultations`)

### 11.1 List Consultations
- **Method:** `GET`
- **Path:** `/api/v1/consultations`
- **Access:** Authenticated
- **Query Parameters:** `patient_id`, `status`, `triage_level`, `skip`, `limit`.

### 11.2 Create Consultation
- **Method:** `POST`
- **Path:** `/api/v1/consultations`
- **Access:** Clinician
- **Status Code:** `201 Created`

### 11.3 Get Consultation
- **Method:** `GET`
- **Path:** `/api/v1/consultations/{consultation_id}`
- **Access:** Authenticated

### 11.4 Update Consultation Details
- **Method:** `PUT`
- **Path:** `/api/v1/consultations/{consultation_id}`
- **Access:** Clinician

### 11.5 Save & Sign SOAP Notes
- **Method:** `PUT`
- **Path:** `/api/v1/consultations/{consultation_id}/soap`
- **Access:** Clinician

---

## 12. Medicolegal Audit Trail (`/api/v1/audit-logs`)

### 12.1 Query Audit Logs
- **Method:** `GET`
- **Path:** `/api/v1/audit-logs`
- **Access:** Clinician / Admin
- **Query Parameters:**
  - `action`: *(Optional)* Filter by event type (`USER_REGISTER`, `LOGIN_SUCCESS`, `CASE_INTAKE_CREATED`, `REVIEW_ACTION_APPROVE`, etc.).
  - `resource_type`: *(Optional)* Filter by resource (`TRIAGE_CASE`, `PATIENT`, `USER`, etc.).
  - `user_email`: *(Optional)* Filter by operator email.
  - `skip`: *(Optional)* Offset integer (default: 0).
  - `limit`: *(Optional)* Count integer ($1 - 200$, default: 50).

#### Response Example (`200 OK`):
```json
{
  "total": 1,
  "items": [
    {
      "id": "f5e4d3c2-b1a0-9876-5432-10fedcba9876",
      "user_id": "d843bb35-512c-473d-bc69-26dcae32d0f5",
      "user_email": "doctor@clinova.ai",
      "action": "REVIEW_ACTION_APPROVE",
      "resource_type": "TRIAGE_CASE",
      "resource_id": "CLV-DEMO-001",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "details": "Reviewer: Dr. S. Chen, Medical Officer | Action: APPROVE | Case: CLV-DEMO-001",
      "timestamp": "2026-09-18T19:40:00.000Z"
    }
  ]
}
```

---

## 13. Planned But Not Yet Implemented Endpoints

The following endpoints are specified in system architecture roadmaps (`ARCHITECTURE.md`, `CHANGELOG.md`) for upcoming releases and are **not yet implemented in the current backend**:

| Planned Method | Planned Path | Target Release | Planned Architectural Scope |
| :--- | :--- | :--- | :--- |
| `WS` | `/api/v1/intake/ws/speech` | v0.3.0 | Real-time bi-directional streaming WebSocket for live speech chunking and chunked transcription. |
| `POST` | `/api/v1/sync/crdt` | v0.3.0 | Batch reconciliation endpoint for client-side IndexedDB / SQLite CRDT offline intake queue synchronization. |
| `POST` | `/api/v1/abdm/link-abha` | v0.4.0 | Ayushman Bharat Health Account (ABHA) gateway verification and patient health record token linking. |
| `POST` | `/api/v1/abdm/consent` | v0.4.0 | ABDM electronic consent artifact request and verification flow. |
| `POST` | `/api/v1/intake/acoustic-biomarkers` | v0.4.0 | Audio spectrum analysis endpoint for acoustic respiratory biomarker extraction and cough frequency analysis. |
| `GET` | `/api/v1/telemetry/beds` | v0.5.0 | Regional district hospital real-time bed and oxygen availability query for referral capacity matching. |
