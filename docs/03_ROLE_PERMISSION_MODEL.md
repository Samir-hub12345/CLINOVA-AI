# CLINOVA AI — Role-Based Access Control (RBAC) & Permission Model

> **Document ID:** `DOC-03`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Governance Principles

1. **Principle of Least Privilege:** Users receive strictly the minimum permissions required to execute their clinical or administrative duty.
2. **Explicit Authority Principle:** No user or role receives permissions merely because an interface component or dashboard exists. All actions are authorized at the API layer.
3. **Clinician Invariant:** Only a qualified Clinician / Medical Officer possesses `APPROVE`, `MODIFY_CLINICAL`, and binding `CARE_DECISION` authority. No automated process or non-clinician role may discharge, prescribe, or close a case.
4. **Audit Immutability:** Every permission check, data access, modification, and clinical sign-off generates an unalterable audit record containing actor ID, role, timestamp, case ID, previous value, new value, and justification.

---

## 2. Complete 13-Dimension Permission Matrix

| Permission Dimension | Clinician / Reviewer | Nurse / Health Worker | Referral Staff | Patient | Caregiver | Facility Admin | System Admin | Researcher |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Entry Point** | `/doctor/queue`, `/doctor/case/:id` | `/nurse/intake`, `/nurse/worklist` | `/referrals/desk`, `/referrals/:id` | `/portal/intake`, `/portal/my-care` | `/portal/caregiver/:id` | `/admin/facility`, `/admin/capacity` | `/system/console`, `/system/security` | `/research/evaluation`, `/research/signals` |
| **2. Default Dashboard** | Prioritized Clinical Queue & Workbench | Intake Station & Missing-Data Worklist | Regional Transfer Coordination Board | Patient Personal Care Summary | Attendant Assisted Portal | Facility Resource & Bed Board | Infrastructure, Auth & Audit Console | Benchmark Evaluation & Signal Telemetry |
| **3. Visible Data Scope** | Full Master Case (Raw, OCR, Vitals, Timeline, CAREGRAPH, AI Prompts) | Assigned Case Intake, Vitals, Triage Flags, Missing Checklist | Referral Summary, Destination Options, Ambulance Logistics | Own verified symptom inputs, doctor-approved report, appointment | Associated patient approved summary, appointment coordinates | Aggregated department stats, bed counts, un-anonymized only on incident | System logs, telemetry, zero medical records | De-identified synthetic data only, macro aggregated statistics |
| **4. Create Permissions** | Cases, Triage Notes, Orders, Referrals, Admissions, Prescriptions | Cases, Vitals Entries, Checklist Responses, Follow-up Inputs | Referral Logistics Records, Ambulance Dispatches | Intake Submissions, Upload Documents, Question Responses | Assisted Intake Submissions, Question Responses | Facility Capabilities, Bed Categories, Shifts | User Accounts, Roles, Security Keys | Evaluation Runs, Model Benchmark Jobs |
| **5. Read Permissions** | All assigned and departmental cases, all clinical graphs | Assigned intake cases, triage checklists, vitals history | Doctor-approved referral files and transfer logs | Own submitted data, final approved clinical summaries | Associated patient approved clinical summaries | Facility resource utilization, wait-time telemetry | System logs, performance metrics, auth tables | Synthetic test cases, SIGNALGRAPH aggregated heatmaps |
| **6. Edit Permissions** | All clinical parameters, notes, diagnoses, risk qualifiers | Intake narrative, self-recorded vitals, checklist items | Transport notes, arrival timestamps, receiving bed ID | Unsubmitted intake draft only | Unsubmitted intake draft only | Facility capability settings, bed availability | User account statuses, system configurations | Benchmark configs, synthetic dataset tags |
| **7. Verification Permissions** | **YES (Full):** Can verify lab results, symptoms, AI inferences, vitals | **PARTIAL:** Can verify vitals and baseline checklist items | **NO:** Read-only clinical status | **NO:** Cannot verify clinical data | **NO:** Cannot verify clinical data | **NO:** Cannot verify clinical data | **NO:** Cannot verify clinical data | **NO:** Cannot verify clinical data |
| **8. Approval Permissions** | **YES (Exclusive):** Final care decisions, discharge, admission, referral | **NO:** Cannot approve care plans | **NO:** Cannot approve care plans | **NO** | **NO** | **YES:** Operational bed allocations | **NO:** Zero clinical approval rights | **NO** |
| **9. Escalation Permissions** | **YES:** Can escalate to Resuscitation, OT, ICU, Senior Consultant | **YES:** Can trigger immediate bedside doctor call / red flag alert | **NO:** Can flag logistical transfer delays | **NO:** Can request nurse assistance | **NO:** Can request nurse assistance | **NO** | **NO** | **NO** |
| **10. Referral Permissions** | **YES:** Can order inter-facility transfer with clinical justification | **NO:** Cannot initiate medical referral | **YES:** Can execute logistics of doctor-approved referral | **NO** | **NO** | **NO** | **NO** | **NO** |
| **11. Download Permissions** | Master Clinical Report, Emergency Pack, Referral File, OT Note | Vitals Slip, Intake Summary, Transfer Checklist | Transport Manifest, Approved Referral Document | Approved Personal Triage Report, Appointment Slip | Approved Personal Triage Report, Appointment Slip | Operational Reports, Capacity Audits | System Audit Logs, Error Reports | Synthetic Benchmark Results, Aggregated Trends |
| **12. Notification Permissions** | Critical red-flag alerts, worsening trajectory alarms, queue escalations | Critical vital sign warnings, missing-data assignments | Incoming transfer approvals, transport dispatch alerts | Appointment reminders, follow-up notifications | Appointment reminders, medication schedule alerts | Bed exhaustion alarms, departmental congestion alerts | Server health failures, security intrusion alerts | Evaluation completion alerts |
| **13. Audit Visibility** | Full case clinical audit trail (modifications, actor history) | Own action log and assigned case intake events | Transfer handoff timestamp log | View record of who accessed their file | View record of who accessed the file | Operational throughput and referral timeline logs | Complete system-wide immutable audit ledger | Zero audit ledger access (de-identified only) |

---

## 3. Detailed Role Definitions & Behavioral Constraints

### 3.1 Clinician / Medical Officer / Qualified Reviewer (`ROLE_CLINICIAN`)
- **Authority:** Supreme clinical decision-maker.
- **Enforced Constraints:**
  - Cannot approve a case without reviewing the highlighted evidence uncertainty.
  - Modifying an AI-inferred entity requires logging the explicit reason (`CORRECTION_ERROR`, `NEW_EXAMINATION_FINDING`, `PATIENT_CLARIFICATION`).
  - Cannot be bypassed by any automated rule or system setting.

### 3.2 Nurse / Health Worker (`ROLE_NURSE`)
- **Authority:** Frontline intake, vitals acquisition, missing-data resolution, and immediate escalation.
- **Enforced Constraints:**
  - Cannot alter clinical notes written by a medical officer.
  - Permitted vital ranges are bounded by physiological validation rules (e.g., HR 20–260 bpm); extreme values force mandatory re-check confirmation.
  - Escalation button immediately routes the patient to the top of the Doctor Queue with an audible/visual badge.

### 3.3 Referral Coordinator (`ROLE_REFERRAL_STAFF`)
- **Authority:** Transfer logistics, transport dispatch, and handoff monitoring.
- **Enforced Constraints:**
  - Cannot create or initiate a medical referral without a signed digital order from a licensed clinician.
  - Must record receiving facility acknowledgment before dispatching inter-facility transport.

### 3.4 Patient (`ROLE_PATIENT`)
- **Authority:** Self-service symptom entry, question answering, and reviewing final approved records.
- **Enforced Constraints:**
  - Read access is strictly locked until a clinician reviews and signs off on the Master Clinical Report.
  - Internal AI reasoning steps, differential diagnostic drafts, and raw risk heuristics are never exposed in patient-facing views to avoid distress and unguided self-treatment.

### 3.5 Caregiver (`ROLE_CAREGIVER`)
- **Authority:** Assisted narrative entry and access to approved patient instructions.
- **Enforced Constraints:**
  - Requires documented patient consent or emergency legal guardian override.
  - Permissions strictly match the Patient role.

### 3.6 Facility Administrator (`ROLE_FACILITY_ADMIN`)
- **Authority:** Operational capacity, facility capabilities, and staff allocations.
- **Enforced Constraints:**
  - Barred from viewing identifiable clinical case files unless an adverse event investigation is authorized with Dual-Key System Administrator approval.

### 3.7 System Administrator (`ROLE_SYSTEM_ADMIN`)
- **Authority:** Technical platform governance, security keys, and user lifecycle.
- **Enforced Constraints:**
  - Strictly forbidden from modifying clinical data or case state fields.
  - Actions are subject to independent secondary audit logging.

### 3.8 Researcher / Evaluator (`ROLE_RESEARCHER`)
- **Authority:** Synthetic benchmark execution, algorithm calibration, and public health telemetry analysis.
- **Enforced Constraints:**
  - Zero access to production databases or live patient identifiers.
  - Restricted entirely to synthetic test benches and aggregated SIGNALGRAPH streams.
