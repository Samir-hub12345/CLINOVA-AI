# CLINOVA AI — Journey Permission Matrix & Role Governance Specification

> **Document ID:** `RES-73`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Meaningful Human Control (MHC)

Clinical healthcare systems manage life-and-death decisions. Software that grants autonomous agency to artificial intelligence models, allows administrative staff to edit clinical diagnoses, or conceals clinical actions behind anonymous logs violates the **NMC Registered Medical Practitioner Regulations 2023**, the **ICMR Ethical Guidelines for AI in Healthcare 2023**, and the **Digital Personal Data Protection (DPDP) Act 2023**.

CLINOVA AI establishes the **Journey Permission Matrix**, anchored in four inviolable governance laws:

1. **The Clinician Decision Monopoly:**  
   > **Inviolable Law:** Only a verified, registered medical practitioner (`ROLE_CLINICIAN`) can formulate medical diagnoses, sign e-prescriptions, authorize surgical procedures, sign inpatient ward admissions, execute inter-facility referrals, or issue formal hospital discharges.
2. **The Advisory AI Boundary:**  
   > **Inviolable Law:** Under NO circumstances can `ROLE_SYSTEM_AI` execute clinical orders, admit, discharge, or refer patients. The AI is strictly advisory (`SUGGEST`, `AUDIT`, `CALCULATE`).
3. **The Administrative Clinical Air-Gap:**  
   > **Inviolable Law:** Administrative staff (`ROLE_ADMIN`) and registration clerks can view and edit demographic, billing, and logistical data, but are strictly prohibited from viewing or editing sensitive clinical progress notes, physical exam findings, or medical diagnoses.
4. **The Auditable Break-Glass Emergency Privilege:**  
   > **Inviolable Law:** Any authenticated clinical user (`ROLE_NURSE`, `ROLE_HEALTH_WORKER`, `ROLE_CLINICIAN`) can trigger an emergency escalation from any screen. Every invocation creates an immutable cryptographic log recording user ID, station, timestamp, and clinical rationale.

---

## 2. Definitive Role Taxonomy

The platform enforces Role-Based Access Control (RBAC) across six canonical actor roles:

1. `ROLE_CLINICIAN`: Registered Medical Practitioner (MBBS / Specialist Doctor).
2. `ROLE_NURSE`: Registered General Nurse & Midwife (GNM / B.Sc Nursing) or Triage Nurse.
3. `ROLE_HEALTH_WORKER`: Auxiliary Nurse Midwife (ANM), Community Health Officer (CHO), or Accredited Social Health Activist (ASHA).
4. `ROLE_ADMIN`: Hospital Administrative Clerk, Registration Officer, Medical Records Technician.
5. `ROLE_PATIENT`: Patient, Legal Guardian, or Authorized Family Caregiver.
6. `ROLE_SYSTEM_AI`: Automated background microservices, quantized edge SLMs, deterministic rule engines.

---

## 3. Journey-Level Permission Matrix

The table below specifies permissions across the 11 core clinical actions:

| Canonical Action | `ROLE_CLINICIAN` | `ROLE_NURSE` | `ROLE_HEALTH_WORKER` | `ROLE_ADMIN` | `ROLE_PATIENT` | `ROLE_SYSTEM_AI` | Safety Guardrail & Clinical Constraint |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`VIEW`** | Full Clinical Dossier | Full Clinical Dossier | Triage & Vitals View | Demographic & Billing Only | Sanitized Patient Summary | Internal Data Buffers | Administrative roles cannot view HIV, psychiatric, or sensitive notes. |
| **`CREATE`** | Diagnoses, Orders, Notes | Vitals, Nursing Notes | Vitals, Screening Notes| Encounter, Demographics | Symptom Voice/Text | Draft Triage Notes | Patient creates raw inputs only; AI creates draft advisory notes. |
| **`EDIT`** | Full Clinical Edits | Nursing Entries Only | Screening Entries Only | Demographics Only | Self-Report Before Freeze | None | Administrative roles strictly blocked from editing clinical text. |
| **`VERIFY`** | Clinical Findings & Notes | Point-of-Care Vitals | Basic Vitals / Tests | Identity Proof Only | Self-Review Extraction | Extraction Completeness | Doctor verification carries permanent medico-legal signature. |
| **`ASSIGN`** | Ward Service, Specialist | Nurse Worklist Task | Field Follow-up Task | Registration Token | None | Queue Sorting Position | AI sorts queue dynamically, but cannot assign staff duties. |
| **`ESCALATE`** | Emergency Resuscitation | Emergency Resuscitation | Emergency Alert | Emergency Alert | Emergency Panic Button | Red-Flag Warning Banner | Any human actor can trigger emergency; AI flags red-flag alerts. |
| **`REFER`** | Inter-Facility Transfer | None (Assists Logistics)| None (Assists Transport)| Transport Booking Only | None | Capability Matching Advice| **CLINICIAN MONOPOLY:** Only a doctor can order a patient transfer. |
| **`ADMIT`** | Inpatient Ward Admission| Ward Intake Sign-In | None | Inpatient Bed Billing | None | Bed Feasibility Check | **CLINICIAN MONOPOLY:** Only a doctor can order inpatient admission. |
| **`DISCHARGE`** | Routine Hospital Discharge| None (Checks Paperwork) | None | Billing Discharge Seal | None | None | **CLINICIAN MONOPOLY:** Only a doctor can authorize discharge. |
| **`OVERRIDE`** | AI Advice / Nurse Vitals| AI Question Suggester | None | None | None | None | Doctor overrides require mandatory, auditable justification text. |
| **`RECORD_OUTCOME`**| Clinical Endpoint | Discharge / Vitals End | Community Follow-up | Telephonic Outcome | Wellness Survey Reply | Model Concordance Metric | Health professionals log clinical endpoints; AI calculates deltas. |

---

## 4. Deep-Dive Specification of Action Governance

### 1. `VIEW` Permission
- **Clinical Governance:**
  - `ROLE_CLINICIAN` and `ROLE_NURSE` have access to the complete clinical timeline, raw audio recordings, OCR document crops, lab trends, and CAREGRAPH topological views.
  - `ROLE_ADMIN` view is strictly air-gapped under DPDP Act compliance: can view name, age, gender, contact number, assigned token, and insurance status; clinical notes and diagnoses are cryptographically masked.
  - `ROLE_PATIENT` receives a sanitized, patient-facing view rendered in their native language, suppressing internal algorithmic debug metrics and ICD codes.

### 2. `CREATE` & `EDIT` Permissions
- **Clinical Governance:**
  - `ROLE_CLINICIAN` possesses unrestricted authority to create medical orders, prescribe drugs, and document physical exam findings.
  - Once signed by a clinician, clinical notes become **read-only**. Any subsequent corrections must be appended as timestamped addenda with explicit audit reasons.
  - `ROLE_SYSTEM_AI` generates drafts only; all AI outputs are prominently watermarked: `ADVISORY DRAFT — UNVERIFIED`.

### 3. `VERIFY` Permission
- **Clinical Governance:**
  - `ROLE_NURSE` verifies calibrated vital signs measured at the nursing desk (`STAFF_VERIFIED`).
  - `ROLE_CLINICIAN` verifies extracted entities, timeline chronology, and diagnostic formulations (`CLINICIAN_APPROVED`).
  - AI "verification" is strictly mathematical completeness checking ($S \ge 0.85$); it possesses zero legal clinical authority.

### 4. `ESCALATE` Permission (Break-Glass Protocol)
- **Clinical Governance:**
  - Any human actor can trigger the Emergency Fast-Track at any point.
  - If a patient collapses in the waiting area, a triage nurse, registration clerk, or community health worker can tap the prominent red **Break-Glass Emergency Button**.
  - The system instantly elevates case priority to `PRIORITY_CRITICAL_P1`, broadcasts audio-visual beacons, and transitions to `STATE_EMERGENCY_ACTIVE`.
  - The audit log records: Actor ID, Physical Station IP, Trigger Timestamp, and Initial Observations.

### 5. `REFER`, `ADMIT`, & `DISCHARGE` Monopolies
- **Clinical Governance:**
  - These three actions represent formal changes in legal custody and patient safety status.
  - Under Section 27 of the NMC Regulations 2023, only a Registered Medical Practitioner can legally execute them.
  - UI enforcement: The buttons for "Confirm Admission", "Authorize Transfer", and "Discharge Patient" are rendered **disabled and locked** unless the active session is authenticated with a verified `ROLE_CLINICIAN` credential token.

### 6. `OVERRIDE` Governance & Friction Calibration
- **Clinical Governance:**
  - Healthcare professionals must remain empowered to override algorithmic recommendations when their clinical judgment disagrees with the AI.
  - To prevent thoughtless overrides while avoiding dangerous cognitive friction, CLINOVA implements **Friction-Calibrated Override Logging**:
    - If a doctor chooses an alternative disposition (e.g., system suggests Routine Care, doctor orders Ward Admission), the UI displays a rapid 2-click modal:
      1. Select Overriding Reason: `Atypical Presentation`, `Subtle Clinical Distress`, `Social / Frailty Factor`, `Diagnostic Disagreement`, `Other`.
      2. Optional 1-sentence note.
    - The override is committed to the immutable audit log, feeding $\text{SIGNALGRAPH}$ model calibration telemetry.
