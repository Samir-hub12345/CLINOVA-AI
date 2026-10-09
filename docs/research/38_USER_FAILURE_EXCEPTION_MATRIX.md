# CLINOVA AI — User Failure & Clinical Exception Matrix

> **Document ID:** `RES-38`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Safety & Exception Engineering Group  

---

## 1. Executive Summary

Clinical systems in high-stress, low-resource Indian public health settings frequently fail not because of mathematical algorithm errors, but due to **human, infrastructural, and operational failure states**: power grid blackouts, missing staff, uncooperative or unconscious patients, conflicting lab values, and referral rejections.

This document establishes the exhaustive failure and exception matrix across **22 mandatory operational failure scenarios**.

Every scenario is formally decomposed across a 6-stage causal chain:
$$\mathbf{ACTOR} \to \mathbf{FAILURE} \to \mathbf{RISK} \to \mathbf{REQUIRED\ SYSTEM\ BEHAVIOR} \to \mathbf{HUMAN\ RESPONSE} \to \mathbf{AUDIT\ REQUIREMENT}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       22 MANDATORY FAILURE MODES MAPPED                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE & ENVIRONMENT       PATIENT & IDENTITY EXCEPTIONS           │
│  ├── 01. No Internet / Grid Outage  ├── 08. Unconscious Patient             │
│  ├── 02. Device Hardware Failure    ├── 09. Patient Without Identity        │
│  ├── 03. Missing Staff on Shift     ├── 10. Wrong Patient Selected          │
│  ├── 04. Overloaded Clinical Staff  ├── 11. Duplicate Case Created          │
│  │                                  ├── 12. Caregiver Unavailable           │
│  CLINICAL DATA & AI FAILURES        ├── 13. Consent Unavailable             │
│  ├── 05. Conflicting Lab / History  ├── 14. Patient Refuses Care (LAMA)     │
│  ├── 06. Incorrect OCR Extraction   │                                       │
│  ├── 07. Incorrect Transcription    FACILITY & LOGISTICAL BOTTLENECKS       │
│  ├── 15. Incorrect Translation      ├── 18. Unavailable Specialist          │
│  ├── 16. Missing Critical Vitals    ├── 19. Unavailable Diagnostic Facility │
│  ├── 17. Wrong User Account Active  ├── 20. Unavailable Destination Hospital│
│                                     ├── 21. Emergency Escalation Surge      │
│                                     └── 22. Referral Rejection at Gate      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master 22-Scenario Failure & Exception Decomposition

### Scenario 01: No Internet / Total Network Grid Outage
- **Actor:** All frontline users (`ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_PATIENT`).
- **Failure:** Fiber cable cut or rural mobile cell tower blackout during active clinical hours.
- **Risk:** Complete system freeze; inability to access patient queue or triage records.
- **Required System Behavior:**
  - Automatic seamless fallback to **Local Standalone Mode** (`OFFLINE_ISLAND_MODE`).
  - Frontend continues querying local SQLite database (`clinova-dev.db`) and local SLM/Whisper instances running natively on workstation or local server.
  - Inter-facility network API calls are queued locally in an append-only outbound sync queue.
  - Persistent amber banner: *"Offline Mode Active — Operating on Local Secure Database"*.
- **Human Response:** Clinicians and nurses continue standard triage without interruption; transfer desk uses cellular telephone voice backup for receiving hospital coordination.
- **Audit Requirement:** System logs network disconnection and reconnection timestamps with total queue items cached.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-18; BPUT B18).

---

### Scenario 02: Hardware Device Failure (Terminal Crash or Battery Drain)
- **Actor:** Triage Nurse or Examining Clinician.
- **Failure:** Tablet battery drains completely or workstation PC encounters OS crash mid-encounter.
- **Risk:** Uncommitted clinical vitals, patient narrative, or exam notes lost; consultation delayed.
- **Required System Behavior:**
  - Continuous incremental local draft auto-saving (every keystroke / field blur persisted to local IndexedDB / SQLite).
  - Encrypted state restoration key generated per `case_id`.
  - When new device logs in under the same clinician/nurse session, system prompts: *"Incomplete encounter detected for PT-XXXXXX. Restore draft?"*.
- **Human Response:** Staff switches to secondary workstation or mobile tablet; inputs credentials and clicks "Restore Draft".
- **Audit Requirement:** Log event `SESSION_ABRUPT_TERMINATION` and `DRAFT_RESTORED_ON_NEW_TERMINAL`.
- **Evidence Tag:** `SUPPORTED` (ISO/IEC 25010 Reliability Norms).

---

### Scenario 03: Missing Staff (Single Doctor Absent at Rural PHC)
- **Actor:** Nurse / Health Worker (ANM / CHO) & Arriving Patients.
- **Failure:** Single Medical Officer called away for emergency post-mortem or absent due to illness.
- **Risk:** Unexamined patients wait indefinitely; high-acuity deterioration missed.
- **Required System Behavior:**
  - Triage desk allows activating `AUTONOMOUS_TRIAGE_SUPPORT_MODE` by Community Health Officer (CHO).
  - System enforces strict protocolized danger sign checklists.
  - If red flags detected, system immediately unlocks the **Tele-Consultation Queue** or flags for **Immediate Primary Referral**.
- **Human Response:** Nurse stabilizes high-acuity patients, triggers eSanjeevani tele-consultation hub, or initiates ambulance referral.
- **Audit Requirement:** Log `STAFF_ABSENCE_OVERRIDE` with CHO user signature.
- **Evidence Tag:** `SUPPORTED` (NHSRC PHC Operational Guidelines 2022).

---

### Scenario 04: Overloaded Clinical Staff (Mass Casualty / Epidemic Surge)
- **Actor:** Primary Clinician & Triage Nurses.
- **Failure:** 400+ patients arrive following a train collision or seasonal dengue surge; 1 doctor per 150 patients.
- **Risk:** Severe alert fatigue; cognitive burnout; complete queue breakdown; rubber-stamping.
- **Required System Behavior:**
  - System switches UI to **High-Density Surge Mode**: suppresses all non-critical narrative; expands triage token view; enforces 20-second vital check.
  - CAREGRAPH trajectory engine aggressively sorts patients, surfacing only `WORSENING` or `CRITICAL` cases to top banner.
- **Human Response:** Medical Superintendent reallocates administrative doctors to casualty; doctors review high-risk queue first.
- **Audit Requirement:** Log `MASS_CASUALTY_SURGE_ACTIVATED` and calculate queue wait-time metrics.
- **Evidence Tag:** `SUPPORTED` (WHO Mass Casualty Triage Protocols).

---

### Scenario 05: Conflicting Clinical Information Across Sources
- **Actor:** Primary Clinician / Automated Parser.
- **Failure:** Uploaded handwritten clinic slip states "Fever x 3 weeks", while patient's voice recording states "Fever began yesterday".
- **Risk:** Misdiagnosing chronic pyrexia of unknown origin as acute viral infection.
- **Required System Behavior:**
  - Missing-Data / Conflict Engine categorizes field as `CONFLICTING`.
  - CAREGRAPH displays prominent amber **Divergence Card** showing both values side-by-side with source snippets.
  - Disables automated risk categorization until clinician selects the verified value.
- **Human Response:** Doctor asks patient directly during consultation; clarifies timeline; clicks verified value.
- **Audit Requirement:** Log `CONFLICT_RESOLVED` capturing old values, chosen value, and doctor rationale.
- **Evidence Tag:** `SUPPORTED` (Phase 1 DOC-08; BPUT B07).

---

### Scenario 06: Incorrect OCR Extraction (Smudged Lab Slip)
- **Actor:** Automated OCR Engine / Primary Clinician.
- **Failure:** OCR misreads smudged CBC report: Platelet count of "15,000" extracted as "150,000".
- **Risk:** Catastrophic failure to recognize severe dengue hemorrhagic shock risk; patient sent home.
- **Required System Behavior:**
  - Multi-Source Evidence Provenance drawer displays raw cropped image of CBC report alongside extracted "150,000" with low OCR confidence tag (`0.42`).
  - Flagged with amber chip `LOW_CONFIDENCE_OCR`.
- **Human Response:** Doctor clicks value, observes cropped image showing "15,000", overrides value to `15,000`, enters reason `CORRECTION_OCR_ERROR`.
- **Audit Requirement:** Log `CLINICAL_VALUE_OVERRIDE` with bounding-box image reference and user ID.
- **Evidence Tag:** `SUPPORTED` (BPUT B04, B12, B17).

---

### Scenario 07: Incorrect Vernacular Speech Transcription (Mumbled Audio)
- **Actor:** Faster-Whisper Engine / Nurse / Patient.
- **Failure:** Patient speaking colloquial Odia ("Mu mundabindha heuchi" - I have headache) transcribed as unrelated word due to crying child background noise.
- **Risk:** Irrelevant symptom tagged; real symptom missed.
- **Required System Behavior:**
  - Audio transcription confidence score drops below threshold ($< 0.50$).
  - System displays audio transcript draft to nurse/patient with high-contrast prompt: *"Please confirm: Did you say 'headache'?"*.
  - Raw audio waveform remains playable with one click.
- **Human Response:** Nurse plays audio snippet; manually types "Headache" in the symptom box.
- **Audit Requirement:** Log `TRANSCRIPTION_CORRECTED` with audio timestamp.
- **Evidence Tag:** `SUPPORTED` (BPUT B02, B05).

---

### Scenario 08: Unconscious Patient (Unresponsive Presentation)
- **Actor:** Triage Nurse & Casualty Medical Officer.
- **Failure:** Patient arrives unconscious (GCS 3–5) via ambulance with no accompanying relatives.
- **Risk:** Inability to obtain symptom history or consent; acute life threat.
- **Required System Behavior:**
  - System activates **Emergency Fast-Track Protocol (`DOC-16`)**.
  - Bypasses all standard narrative and consent inputs (`EMERGENCY_IMPLIED_CONSENT`).
  - Prompts strictly for ABCD vitals and GCS score.
  - Automatically provisions temporary `UNKNOWN_EMERGENCY_CASE` record.
- **Human Response:** Nurse places patient in resuscitation bay; doctor initiates intubation / IV access.
- **Audit Requirement:** Log `EMERGENCY_IMPLIED_CONSENT_OVERRIDE` signed by attending MO.
- **Evidence Tag:** `SUPPORTED` (Indian Emergency Medical Services Protocols; NMC Ethics 2023).

---

### Scenario 09: Patient Without Identity (John Doe Presentation)
- **Actor:** Registration Staff & Triage Nurse.
- **Failure:** Unidentified trauma victim found on highway without documents, phone, or identity.
- **Risk:** Inability to link past history; confusion with other unidentified patients.
- **Required System Behavior:**
  - Generates standardized Anonymous Temporary Identifier: `PT-UNKNOWN-YYYYMMDD-XXXX`.
  - Captures physical descriptors (estimated age, gender, clothing, identifying marks).
  - Allows subsequent merging of identity record once patient or relatives are identified.
- **Human Response:** Staff applies physical wristband matching the synthetic ID; proceeds with clinical care.
- **Audit Requirement:** Log `TEMPORARY_IDENTITY_PROVISIONED` with staff user ID.
- **Evidence Tag:** `SUPPORTED` (MoHFW Medico-Legal Care Guidelines).

---

### Scenario 10: Wrong Patient Selected at Doctor Workbench
- **Actor:** Primary Clinician.
- **Failure:** Doctor examining Patient B while Patient A's file remains open on the screen.
- **Risk:** Incorrect diagnosis or medications entered into wrong patient record.
- **Required System Behavior:**
  - Persistent high-contrast Top Patient Header displaying Patient Synthetic ID, Name/Token, Age, Gender, and Photo/Avatar.
  - Consultation screen auto-prompts for confirmation: *"Now examining Token #45 (PT-91823)?"* on opening.
- **Human Response:** Doctor notices discrepancy; clicks "Switch Patient" and claims correct record from queue.
- **Audit Requirement:** Log `CASE_OPENED` and `CASE_CLOSED_WITHOUT_COMMITTING`.
- **Evidence Tag:** `SUPPORTED` (WHO Patient Identification Safety Solutions).

---

### Scenario 11: Duplicate Case Created for Existing Patient
- **Actor:** Frontline Health Worker / Registration Desk.
- **Failure:** Nurse creates a second new case for a patient who already had an active encounter initiated 2 hours earlier.
- **Risk:** Fractured care history; serial vitals trajectory calculations split across two disconnected records.
- **Required System Behavior:**
  - System executes duplicate detection based on active token, ABHA ID, or name + phone match.
  - Displays alert: *"Active encounter already open for this patient (PT-44012). Append data to existing case?"*.
  - Enforces **Single Master Case Invariant**: blocks duplicate creation.
- **Human Response:** Staff clicks "Append to Active Case"; vitals are merged into existing CAREGRAPH.
- **Audit Requirement:** Log `DUPLICATE_CASE_PREVENTED` with merged case ID.
- **Evidence Tag:** `SUPPORTED` (Phase 1 DOC-06, DOC-07).

---

### Scenario 12: Caregiver Unavailable (Pediatric Patient Escorted by Stranger)
- **Actor:** Triage Nurse / Clinician.
- **Failure:** 6-year-old child brought to clinic by neighbor after school injury; parents uncontactable.
- **Risk:** Lack of legal guardian consent; missing allergy and chronic illness history.
- **Required System Behavior:**
  - Prompts for `ESCORT_RELATIONSHIP = GOOD_SAMARITAN / NEIGHBOR`.
  - System activates **Emergency Minor Treatment Protocol** under Indian law (emergency doctrine permits life-saving care without parent).
  - Flags case for social work / hospital welfare tracking.
- **Human Response:** Doctor stabilizes child; hospital staff attempts phone contact with school/parents.
- **Audit Requirement:** Log `SURROGATE_ABSENT_EMERGENCY_AUTHORIZATION` with doctor co-signature.
- **Evidence Tag:** `SUPPORTED` (The Protection of Children from Sexual Offences / IPC Emergency Provisions).

---

### Scenario 13: Consent Unavailable (Refusal to Provide Digital Consent)
- **Actor:** Patient & Nurse.
- **Failure:** Patient refuses to click digital consent checkbox due to distrust of digital systems.
- **Risk:** Inability to initiate digital triage record.
- **Required System Behavior:**
  - System provides alternative option: **Verbal Consent Captured by Staff** (`VERBAL_CONSENT_CONFIRMED`).
  - If patient refuses all data processing: System provides physical paper fallback printout and flags case as `ANONYMOUS_UNSAVED_LOCAL`.
- **Human Response:** Nurse explains that data is kept locally and securely; captures verbal consent or reverts to paper ticket.
- **Audit Requirement:** Log `CONSENT_TYPE = VERBAL_STAFF_ATTESTED` or `DATA_PROCESSING_DECLINED`.
- **Evidence Tag:** `SUPPORTED` (BPUT B14; DPDP Act 2023).

---

### Scenario 14: Patient Refuses Care / Leaves Against Medical Advice (LAMA)
- **Actor:** Patient, Caregiver & Clinician.
- **Failure:** High-risk chest pain patient insists on leaving hospital despite doctor advising emergency admission.
- **Risk:** Out-of-hospital cardiac arrest; hospital blamed for negligence.
- **Required System Behavior:**
  - Clinician selects disposition: `LEAVING_AGAINST_MEDICAL_ADVICE` (LAMA).
  - System auto-generates high-contrast statutory LAMA form documenting explained risks, witness signature fields, and date/time stamp.
- **Human Response:** Clinician counsels patient; obtains physical/digital thumbprint on LAMA form; dispenses basic emergency aspirin.
- **Audit Requirement:** Log `DISPOSITION_LAMA` with mandatory doctor clinical note and signed form attachment.
- **Evidence Tag:** `SUPPORTED` (NMC Medicolegal Practice Guidelines).

---

### Scenario 15: Incorrect Dialect Translation
- **Actor:** Local Language Translation Engine (`B09`) / Clinician.
- **Failure:** Regional colloquial phrase translated with altered clinical meaning (e.g., "chhati jwalan" translated as "chest burn" instead of "heartburn/acidity").
- **Risk:** Misinterpretation of cardiac versus gastrointestinal symptom.
- **Required System Behavior:**
  - Both original regional language phrase and translated English term are rendered side-by-side on the Doctor Workbench.
  - Hovering/clicking reveals original vernacular audio recording.
- **Human Response:** Doctor reads original vernacular text or plays audio; clarifies directly with patient.
- **Audit Requirement:** Log `TRANSLATION_OVERRIDE` if clinician edits translated concept.
- **Evidence Tag:** `SUPPORTED` (BPUT B09; Phase 2 RES-10).

---

### Scenario 16: Missing Critical Vitals (Patient Refuses BP Cuff)
- **Actor:** Patient & Nurse.
- **Failure:** Extremely agitated or burned patient cannot tolerate blood pressure cuff placement.
- **Risk:** Missing BP causes false-negative triage score if treated as normal.
- **Required System Behavior:**
  - System explicitly forbids imputing BP as 120/80.
  - Nurse marks BP field as `UNOBTAINABLE` with mandatory reason (`SEVERE_AGITATION`, `PHYSICAL_INJURY`).
  - Uncertainty score escalates ($U_t \ge 0.50$); CAREGRAPH renders high-priority warning card.
- **Human Response:** Nurse palpates radial pulse to estimate crude perfusion; informs doctor immediately.
- **Audit Requirement:** Log `VITAL_UNOBTAINABLE_EXCEPTION` with specific reason tag.
- **Evidence Tag:** `SUPPORTED` (Phase 1 DOC-07, DOC-10; C03).

---

### Scenario 17: Wrong User Account Active on Shared Station
- **Actor:** Nurse B using Doctor A's unlocked terminal.
- **Failure:** Staff nurse enters vitals or modifications while logged into a doctor's active session.
- **Risk:** Audit trail records doctor ID for nurse actions; privilege escalation.
- **Required System Behavior:**
  - Idle session timeout (locks screen after 5 minutes of inactivity).
  - High-visibility user badge with avatar and role chip on top bar (`DR. SHARMA — CLINICIAN`).
  - One-click "Lock Station / Switch User" button.
- **Human Response:** Staff immediately locks station; logs in under own PIN / credentials.
- **Audit Requirement:** Log `AUTO_LOCK_TRIGGERED` and `USER_SWITCH_EVENT`.
- **Evidence Tag:** `SUPPORTED` (ISO/IEC 27001 Access Control).

---

### Scenario 18: Unavailable Specialist (On-Duty Surgeon Off-Site)
- **Actor:** Primary Clinician & Facility Administrator.
- **Failure:** Acute appendicitis requiring emergency surgery, but on-duty general surgeon called away for off-site emergency.
- **Risk:** Patient booked for OT on-site, waiting hours until appendix perforates.
- **Required System Behavior:**
  - FACILITYGRAPH profile reflects `SURGICAL_SPECIALIST = UNAVAILABLE`.
  - When clinician considers admission, system triggers warning: *"General Surgery unavailable on-site. Care Feasibility: INSUFFICIENT"*.
  - System surfaces nearest capable surgical facility with active surgeon.
- **Human Response:** Doctor immediately converts disposition to `INTER_FACILITY_REFERRAL`.
- **Audit Requirement:** Log `SPECIALIST_UNAVAILABLE_FACILITYGRAPH_TRIGGER`.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-07, RES-11; C05).

---

### Scenario 19: Unavailable Diagnostic Facility (X-Ray Tube Burnout)
- **Actor:** Primary Clinician & Radiographer.
- **Failure:** Suspected compound tibial fracture arrives; hospital X-ray machine broken.
- **Risk:** Blind splinting without imaging; delayed compartment syndrome recognition.
- **Required System Behavior:**
  - Facility Administrator toggles X-Ray status to `OFFLINE_MAINTENANCE` in FACILITYGRAPH.
  - System disables on-site X-Ray ordering and flags diagnostic bottleneck on doctor screen.
- **Human Response:** Doctor splints limb, performs neurovascular check, and routes patient to nearest facility with active imaging.
- **Audit Requirement:** Log `FACILITY_RESOURCE_STATUS_CHANGE` signed by Administrator.
- **Evidence Tag:** `SUPPORTED` (Phase 1 DOC-11; C05).

---

### Scenario 20: Unavailable Destination Hospital (Regional Tertiary ICU Full)
- **Actor:** Referral Coordinator & Primary Clinician.
- **Failure:** District Hospital attempts to refer intubated ARDS patient to Medical College, but Medical College ICU is at 100% occupancy.
- **Risk:** Patient dispatched in ambulance, arrives at tertiary hospital, and is turned away at the gate.
- **Required System Behavior:**
  - FACILITYGRAPH displays Medical College ICU status as `OCCUPANCY_100%_DIVERT`.
  - Algorithmic referral matcher excludes full hospital and ranks next-nearest capable facility (e.g., Regional Specialty Hospital 15 km further).
- **Human Response:** Referral staff calls secondary facility, confirms bed, and dispatches ambulance to capable destination.
- **Audit Requirement:** Log `REFERRAL_DESTINATION_DIVERTED` capturing full hospital ID and alternative selected.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-05; C05, C06).

---

### Scenario 21: Emergency Escalation Surge (Waiting Room Arrest)
- **Actor:** Waiting Room Patient, Caregiver & Triage Nurse.
- **Failure:** Patient triaged as "Routine" 45 minutes earlier suddenly collapses in waiting room.
- **Risk:** Fatal waiting room cardiac arrest without staff awareness.
- **Required System Behavior:**
  - Attendant or nurse hits "Emergency Bedside Escalation" on terminal or waiting portal.
  - Case immediately promoted to `P1_CRITICAL`; triggers visual and audio alarm across all doctor workstations.
  - Case jumps to position #1 in Doctor Queue.
- **Human Response:** Resuscitation team runs to waiting area with crash cart; moves patient to ERR bay.
- **Audit Requirement:** Log `DYNAMIC_QUEUE_ESCALATION` with timestamp and user ID.
- **Evidence Tag:** `SUPPORTED` (Phase 1 DOC-06, DOC-16).

---

### Scenario 22: Referral Rejection at Receiving Facility Gate
- **Actor:** Referral Coordinator, Ambulance Paramedic & Receiving Hospital CMO.
- **Failure:** Ambulance arrives at receiving hospital; receiving doctor attempts to refuse admission due to bed shortage.
- **Risk:** Patient stranded in ambulance driveway; fatal hypoxia.
- **Required System Behavior:**
  - Paramedic taps `HANDOFF_DISPUTED / ADMISSION_REFUSED` on ambulance tablet.
  - Broadcasts critical escalation alert back to dispatching facility transfer desk.
  - Displays pre-authorized secondary facility diversion route.
- **Human Response:** Dispatching Medical Superintendent calls receiving Medical Superintendent; statutory emergency duty-to-care invoked under Supreme Court rulings (Paschim Banga Khet Mazdoor Samity v. State of WB).
- **Audit Requirement:** Log `REFERRAL_HANDOFF_DISPUTED` with timestamps, vehicle ID, and receiving officer name.
- **Evidence Tag:** `SUPPORTED` (Supreme Court of India Emergency Healthcare Precedents; MoHFW Referral Protocols).
