# CLINOVA AI — Target Users Specification

> **Document ID:** `DOC-02`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Overview of Stakeholder Architecture

CLINOVA AI models eight distinct user personas across three functional tiers: **Primary Clinical Users**, **Secondary Care Journey Users**, and **System & Research Users**. 

Every persona operates within strictly defined clinical boundaries, user interfaces, and information access tiers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA AI STAKEHOLDER TIERS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  PRIMARY CLINICAL USERS                                                     │
│  ├── 1. Clinician / Medical Officer / Qualified Reviewer (Autonomous Gate) │
│  └── 2. Nurse / Community Health Worker (Intake, Vitals, Checklists)        │
│                                                                             │
│  SECONDARY CARE JOURNEY USERS                                               │
│  ├── 3. Referral Coordinator / Transfer Desk Staff (Inter-Facility Logistics)│
│  ├── 4. Patient (Intake Narrative, Question Responses, Approved Reports)    │
│  └── 5. Caregiver / Attendant (Assisted Narrative, Approved Care Guidance)  │
│                                                                             │
│  SYSTEM & GOVERNANCE USERS                                                  │
│  ├── 6. Facility Administrator (Bed Capacity, Resources, Shift Schedules)   │
│  ├── 7. System Administrator (RBAC, Audit Logs, Security Policies)          │
│  └── 8. Researcher / Clinical Evaluator (Synthetic Evaluation, Bias Audits) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Primary Clinical Users

### 2.1 Clinician / Medical Officer / Qualified Reviewer
The licensed physician, medical officer, emergency doctor, or qualified clinical reviewer holds ultimate medicolegal responsibility.

- **Primary Responsibilities:**
  - Case review: Review patient encounters in the prioritized doctor queue.
  - State inspection: Understand the synthesized clinical state within CAREGRAPH.
  - Evidence audit: Inspect raw source provenance, confidence tags, and timeline events.
  - Uncertainty audit: Inspect data gaps, conflicting lab values, and unverified parameters.
  - Clinical Verification: Formally verify, modify, or add discrete clinical parameters.
  - AI Output Review: Scrutinize AI-generated triage notes, summaries, and action recommendations.
  - Facility Context Review: Check local facility capabilities (FACILITYGRAPH) against patient requirements.
  - Final Decision Making: Execute binding clinical decisions (`APPROVE`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`, `ADMIT`).
  - Record Finalization: Sign off on final Master Clinical Reports and handoff notes.
- **Authority Boundary:** Full read/write/verify authority over clinical fields; absolute veto authority over AI advisories.

### 2.2 Nurse / Health Worker (ANM / ASHA / Community Triage)
The frontline nurse, auxiliary nurse midwife (ANM), or community health worker who initiates triage and supports clinical intake.

- **Primary Responsibilities:**
  - Assisted Intake: Assist illiterate or non-technical patients with text or voice symptom recording.
  - Missing-Information Collection: Work through the system-generated missing-data checklist.
  - Vital Sign Acquisition: Measure and enter standardized vitals (BP, pulse, SpO2, respiratory rate, temperature, blood glucose).
  - Permitted Value Verification: Confirm abnormal readings by repeating measurements.
  - Checklist Completion: Execute mandatory triage checklists (e.g., chest pain red flags, pediatric danger signs).
  - Authorized Field Updates: Update assigned intake fields, pain scores, and triage notes.
  - Immediate Escalation: Trigger instant bedside clinical alerts when red flags or shock criteria are met.
  - Handoff Support: Escort deteriorating patients and transfer custody to the medical officer or resuscitation team.
- **Authority Boundary:** Can enter, update, and verify assigned intake and vital sign parameters; cannot finalize diagnoses or order unauthorized discharges.

---

## 3. Secondary Care Journey Users

### 3.1 Referral Staff / Transfer Coordinator
Dedicated hospital transfer desk staff or regional referral dispatchers coordinating inter-facility movement.

- **Primary Responsibilities:**
  - Referral Review: Inspect doctor-approved referral requests and capability justifications.
  - Destination Matching: Inspect FACILITYGRAPH recommendations for nearest capable facility with verified bed and specialty availability.
  - Transfer Coordination: Contact receiving facility transfer desk, arrange transport/ambulance, and transmit structured referral pack.
  - Status Tracking: Monitor transfer progress (`DISPATCHED`, `IN_TRANSIT`, `ARRIVED`, `HANDOFF_CONFIRMED`).
  - Handoff Verification: Confirm safe physical arrival and handover of clinical custody.
- **Authority Boundary:** Read access to referral summaries and logistical coordinates; cannot alter clinical notes.

### 3.2 Patient
The individual seeking healthcare consultation or emergency triage.

- **Primary Responsibilities:**
  - Information Submission: Provide symptom narrative in spoken regional dialect or typed text.
  - Document Upload: Upload physical prescriptions, lab slips, or discharge summaries via camera/scanner.
  - Question Answering: Respond to high-priority follow-up clarification prompts.
  - Information Review: Review clinician-approved discharge summaries, care instructions, and appointments.
  - Appointment Management: View scheduled revisit slots or telemedicine follow-up dates.
- **Authority Boundary:** Can view own approved case summary; zero access to internal clinician scratchpads, unverified differential considerations, or other patients' records.

### 3.3 Caregiver / Patient Attendant
Family members, emergency contacts, or accompanying guardians.

- **Primary Responsibilities:**
  - Assisted Submission: Submit symptom narrative and upload past medical history on behalf of pediatric, elderly, unconscious, or incapacitated patients.
  - Approved Communication: Receive clinician-approved emergency instructions, pharmacy guidance, and referral coordinates.
- **Authority Boundary:** Access governed by explicit patient consent or emergency surrogate protocol; identical view permissions to the patient.

---

## 4. System & Governance Users

### 4.1 Facility Administrator
Hospital superintendent, nursing supervisor, or clinic operational manager.

- **Primary Responsibilities:**
  - Capability Configuration: Maintain FACILITYGRAPH profile (available diagnostic equipment, active ICU beds, on-duty specialists, oxygen stock).
  - Capacity & Queue Oversight: Monitor live department queue lengths, average wait times, and emergency bed occupancy.
  - Bottleneck Remediation: Reallocate triage nursing staff or open overflow observation beds during demand surges.
  - Referral Performance Tracking: Monitor referral turnaround times and receiving hospital acceptance rates.
- **Authority Boundary:** Full operational and resource management access; restricted from viewing individual un-anonymized clinical case records unless authorized for clinical audit.

### 4.2 System Administrator
IT and clinical informatics infrastructure engineer.

- **Primary Responsibilities:**
  - Access Governance: Manage user accounts, role assignments, and authentication security.
  - System Monitoring: Monitor backend health, local model runtime availability, and database performance.
  - Audit Log Review: Maintain immutable audit trails of data access, PII redaction, and clinical overrides.
  - Security Enforcement: Ensure zero-leakage ephemeral storage policies (24-hour cleanup) and air-gapped configuration.
- **Authority Boundary:** Full platform infrastructure and audit log access; strictly barred from modifying medical case records or overriding clinical decisions.

### 4.3 Researcher / Clinical Evaluator
Academic, epidemiologist, or AI safety researcher assessing algorithm calibration.

- **Primary Responsibilities:**
  - Synthetic Evaluation: Benchmark local SLM extraction accuracy, risk calibration, and uncertainty scoring against synthetic benchmark sets.
  - Signal Analysis: Analyze macro-level SIGNALGRAPH syndromic patterns for public health trend detection.
  - Bias & Error Auditing: Audit performance across linguistic dialects (Odia vs Hindi vs English) and clinical subcategories.
  - Safety Metric Reporting: Compute agreement rates between AI advisory recommendations and actual clinician decisions.
- **Authority Boundary:** Access strictly confined to synthetic datasets, de-identified telemetry, and aggregated analytics; absolute zero access to any live or identifiable patient encounters.
