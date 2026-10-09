# CLINOVA AI — Target User Role Analysis & Granular Specification

> **Document ID:** `RES-31`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Healthcare Human Factors Research Group  

---

## 1. Executive Summary

This document establishes the exhaustive, evidence-backed clinical, operational, and permission profiles for all eight user roles identified in CLINOVA AI.

Each role is evaluated systematically across **31 mandatory dimensions**, grounding theoretical capability claims in empirical Indian healthcare constraints, statutory regulations (NMC, MoHFW, ABDM), and the baseline contracts of the BPUT problem statement.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE 8 CLINOVA USER ROLES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  CLINICAL & CARE-DELIVERY ROLES                                             │
│  ├── 1. Primary Clinician / Medical Officer / Qualified Reviewer            │
│  ├── 2. Nurse / Frontline Health Worker (ANM / ASHA / Triage Nurse)         │
│  └── 3. Referral Coordinator / Transfer Desk Staff                          │
│                                                                             │
│  RECIPIENT & CARE-SEEKING ROLES                                             │
│  ├── 4. Patient                                                             │
│  └── 5. Caregiver / Attendant / Legal Guardian                              │
│                                                                             │
│  GOVERNANCE, INFRASTRUCTURE & RESEARCH ROLES                                │
│  ├── 6. Facility Administrator                                              │
│  ├── 7. System Administrator                                                │
│  └── 8. Research / Evaluation User                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Specification for Role 1: Primary Clinician / Medical Officer / Qualified Reviewer

### 2.1 Profile & Environmental Identity
- **1. Role Name:** Primary Clinician / Medical Officer / Qualified Reviewer (`ROLE_CLINICIAN`).
- **2. Real-World Responsibility:** Licensed physician (MBBS / MD / MS / DNB) registered with the State Medical Council / National Medical Commission (NMC). Holds ultimate medicolegal and ethical responsibility for patient assessment, diagnostic verification, therapeutic orders, and disposition.
- **3. Primary Environment:** Government District Hospital (Emergency & OPD), Primary Health Centre (PHC/CHC), Company Clinic, Industrial Health Unit, Campus Health Centre.

### 2.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Rapidly assess presenting patient acuity, prevent unrecognized clinical deterioration, verify underlying data fidelity, formulate accurate disposition plans, and clear congested queues without cognitive burnout.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 1.1:* Review high-acuity patients first using dynamically sorted queue rankings.
  - *JTBD 1.2:* Absorb complete multi-source patient context (vitals, timeline, lab slips) in under 30 seconds.
  - *JTBD 1.3:* Verify or correct AI-extracted clinical entities and discard hallucinations.
  - *JTBD 1.4:* Authorize binding care pathways (`ROUTINE_DISCHARGE`, `OBSERVATION`, `WARD_ADMIT`, `EMERGENCY_OT`, `INTER_FACILITY_REFERRAL`).
  - *JTBD 1.5:* Sign legally binding clinical encounter notes and referral packs.
- **6. Typical Operational Workflow:**
  $$\text{Open Doctor Queue} \to \text{Select Patient Card} \to \text{Inspect Trajectory \& Gaps} \to \text{Review Evidence Provenance} \to \text{Perform Bedside Exam} \to \text{Verify/Modify Parameters} \to \text{Select Pathway} \to \text{Digital Sign-Off}$$

### 2.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Clinical examination findings (auscultation, palpation, neurological exam), confirmed provisional diagnosis, medication orders, procedure notes, disposition decisions, override reasons.
- **8. Information Consumed:** Longitudinal timeline, serial vitals curves, CAREGRAPH acuity trajectory ($\Delta R_t / \Delta t$), epistemic uncertainty score ($U_t$), missing-data checklists, OCR bounding-box crops, audio waveforms, local facility capabilities (FACILITYGRAPH), regional syndromic alerts (SIGNALGRAPH).
- **9. Information Verified:** Extracted lab values (CBC, electrolytes), AI-normalized symptom entities, staff-acquired vitals, red-flag checklists.
- **10. Information Modified:** Any clinical entity, symptom onset timestamp, lab value, triage severity band, proposed referral destination, prescription order.

### 2.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Final triage acuity classification (`P1_CRITICAL`, `P2_URGENT`, `P3_ROUTINE`).
  - Ordering emergency resuscitation bundles, labs, imaging, or medications.
  - Direct admission to general ward, step-down, or ICU.
  - Direct surgical dispatch to Operation Theatre (OT).
  - Ordering inter-facility transfer with clinical justification.
  - Authorizing outpatient discharge with follow-up instructions.
  - Full override of AI-recommended care pathways.
- **12. Unauthorized Decisions:**
  - Modification of immutable system audit trails.
  - Alteration of past finalized records authored by other physicians without addendum logging.
  - Reconfiguration of institutional facility resource baselines or global RBAC policies.

### 2.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** Multimodal Extraction (`B03`-`B05`), CAREGRAPH Trajectory Engine (`C01`), Uncertainty Quantification (`C03`), Next-Best Information Engine (`C04`), FACILITYGRAPH Matching (`C05`), ORCHESTRATION Synthesis (`C08`).
- **14. Visible AI Outputs:** Synthesized structured triage note draft, trajectory trend badges, uncertainty gauge ($U_t$), suggested Next-Best questions, candidate care pathways with feasibility tags.
- **15. Restricted AI Controls:** System strictly prohibits autonomous AI execution of:
  - Automated patient discharge without doctor sign-off.
  - Autonomous drug prescription or order placement.
  - Automated referral dispatch without clinician signature.
- **16. Evidence/Provenance Requirements:** Every extracted finding must link directly to raw source evidence (audio timestamp, OCR crop, vitals log). Clinician must be able to verify raw provenance in $< 3$ seconds.
- **17. Uncertainty Requirements:** System must prominently surface $U_t \in [0, 1]$; critical unknown values must be visually highlighted in amber cards. System must never impute missing vitals.

### 2.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Immediate bedside resuscitation lead; activation of Code Red / Trauma protocol; manual override of standard documentation in favor of 30-second rapid intake.
- **19. Referral Responsibilities:** Formulation of clinical transfer rationale; sign-off on capability justification; selection of receiving facility tier.
- **20. Follow-up Responsibilities:** Definition of red-flag return warnings, review interval (e.g., 48 hours), and post-discharge self-care instructions.
- **21. Outcome Responsibilities:** Finalization of encounter resolution state (`FULL_RECOVERY`, `STABILIZED`, `TRANSFERRED`, `MORTALITY`) during case closure.

### 2.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** Full clinical access to identified case file during active consultation; governed by NMC Code of Medical Ethics and Digital Personal Data Protection (DPDP) Act 2023.
- **23. Access Sensitivity:** Tier 1 (Highest clinical data scope; strictly zero system administration rights).
- **24. Failure Scenarios:** Alert fatigue leading to rubber-stamping; tunnel vision / cognitive anchoring on AI draft; entering erroneous exam findings; abandoning queue during mass casualty surge.
- **25. Permission Risks:** Unauthorized clinical modification if terminal left unlocked at shared nursing station.
- **26. Human-Oversight Requirements:** Mandatory friction-calibrated justification capture when overriding AI trajectory or deterministic red flags.
- **27. Accessibility Requirements:** High-contrast screen support, keyboard shortcut navigation (TAB/ENTER navigation for high-throughput OPD).
- **28. Device & Connectivity Constraints:** Workstation desktop PC, hospital laptop, or Android tablet (min 4GB RAM); must support 100% offline local queue execution during grid outages.
- **29. Training & Digital Literacy Constraints:** 15-minute onboarding curve; zero medical informatics jargon; interface mirrors standard Indian OPD prescription slips.
- **30. Expected Frequency of Use:** Continuous during active shift (40–120 encounters per day).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Missed surgical abdomen, fatal delay in acute coronary syndrome, inappropriate referral causing transit death.
  - *Success Criteria:* Intake documentation time reduced from 6 mins to $< 60$s; zero unreviewed red-flag cases in waiting hall; 100% provenance auditability.
- **Evidence Tag:** `SUPPORTED` (NMC RMP Regulations 2023; IPHS 2022; BPUT B12, B18).

---

## 3. Granular Specification for Role 2: Nurse / Frontline Health Worker

### 3.1 Profile & Environmental Identity
- **1. Role Name:** Nurse / Frontline Health Worker (`ROLE_NURSE` / `ROLE_HEALTH_WORKER`).
- **2. Real-World Responsibility:** Registered General Nurse (GNM / B.Sc Nursing), Auxiliary Nurse Midwife (ANM), or Accredited Social Health Activist (ASHA). Frontline gatekeeper executing triage registration, vital signs measurement, symptom intake assistance, red-flag checklist completion, and immediate acute escalation.
- **3. Primary Environment:** Government Hospital (Triage Desk), PHC / Sub-Centre (Ayushman Arogya Mandir), Public Health Camp, Company Medical Room, Campus Clinic.

### 3.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Rapidly intake arriving patients, measure and record accurate vital signs, identify critical physiological distress within 60 seconds, ensure complete data collection for illiterate patients, and escalate deteriorating patients immediately.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 2.1:* Assist non-literate patients in recording vernacular voice or text symptom narratives (`B01`, `B02`).
  - *JTBD 2.2:* Measure and record objective vitals (BP, PR, SpO2, RR, Temp, Blood Glucose).
  - *JTBD 2.3:* Complete system-prompted Missing-Data Checklists (`B07`, `B08`) to resolve critical clinical uncertainty.
  - *JTBD 2.4:* Trigger immediate bedside emergency escalation when red-flag criteria are met (`TRIAGE-R01` to `TRIAGE-R06`).
  - *JTBD 2.5:* Escort and transfer physical custody of critical patients to the resuscitation bay.
- **6. Typical Operational Workflow:**
  $$\text{Receive Patient} \to \text{Capture Consent} \to \text{Assist Narrative/Voice} \to \text{Take Vitals} \to \text{Complete Checklist} \to \text{System Calculates Risk} \to \text{Route to Doctor Queue / Resuscitation}$$

### 3.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Measured vital signs, assisted symptom narratives, danger sign observations (e.g., stridor, cold clammy skin, capillary refill time), pain scores.
- **8. Information Consumed:** Intake prompts, missing-data checklists, immediate red-flag alerts, physiological validation ranges, patient identity.
- **9. Information Verified:** Basic physiological vitals; repeat abnormal vitals to eliminate measurement artifact.
- **10. Information Modified:** Intake drafts, self-recorded vitals, checklist selections prior to doctor handoff.

### 3.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Initiating an encounter record under synthetic patient ID.
  - Recording, validating, and submitting vital sign measurements.
  - Triggering immediate acute escalation (`ESCALATE_EMERGENCY`).
  - Marking missing-data items as `UNOBTAINABLE` (e.g., amputee cuff placement).
- **12. Unauthorized Decisions:**
  - Altering doctor's provisional diagnosis or clinical encounter notes.
  - Ordering prescription medications (except standing government emergency protocols like ORS, Zinc, IFA, or initial oxygen support).
  - Finalizing patient discharge or signing medical referral certificates.

### 3.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** Speech-to-Text (`B02`), Entity Extraction (`B05`), Missing-Information Detection (`B07`), Red-Flag Heuristics (`B10`).
- **14. Visible AI Outputs:** Real-time speech transcription, highlighted missing vital signs, red-flag alert banners, physiological outlier warnings.
- **15. Restricted AI Controls:** Cannot adjust AI model parameters, change clinical risk thresholds, or bypass mandatory vital sign input prompts.
- **16. Evidence/Provenance Requirements:** Entering manual vitals requires confirming whether reading was automated monitor or manual sphygmomanometer.
- **17. Uncertainty Requirements:** If nurse cannot obtain a vital sign, system forces selection of reason (`PATIENT_UNCOOPERATIVE`, `DEVICE_UNAVAILABLE`, `PHYSICAL_CONTRAINDICATION`) rather than leaving silent null.

### 3.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** First responder for triage arrest; immediate oxygen administration; call for emergency medical officer; bed allocation in triage bay.
- **19. Referral Responsibilities:** Gathering patient transfer file; ensuring vitals are recorded before ambulance departure; performing verbal handoff to ambulance paramedic.
- **20. Follow-up Responsibilities:** In PHC/Sub-centre setup, ANM/ASHA conducts community tracking of high-risk cases identified during clinic triage.
- **21. Outcome Responsibilities:** Recording patient departure or handoff confirmation in triage register.

### 3.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** High; handles intimate patient disclosures during physical assessment; must maintain curtain privacy.
- **23. Access Sensitivity:** Tier 2 (Intake, vitals, checklists, assigned patient records; zero access to system logs or facility configuration).
- **24. Failure Scenarios:** Inaccurate manual blood pressure entry; skipping respiratory rate measurement (frequently faked as "20/min"); failing to escalate atypical shock; double-entering patient creating duplicate case.
- **25. Permission Risks:** Attempting to alter doctor's clinical orders.
- **26. Human-Oversight Requirements:** All nurse-entered vitals and checklists must be explicitly verified or co-signed by examining physician.
- **27. Accessibility Requirements:** Large-tap touch targets on mobile tablets; vernacular voice prompts in Odia/Hindi for assisted screening.
- **28. Device & Connectivity Constraints:** Android tablet (7–10 inch) or ruggedized mobile handset; full functionality in offline caching mode.
- **29. Training & Digital Literacy Constraints:** Medium-low digital literacy; simplified single-page stepped workflow with visual color codes.
- **30. Expected Frequency of Use:** Continuous during shift (50–150 patients/shift).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Missed septic shock in pediatric patient; hypertensive crisis unflagged; duplicate records fracturing care continuity.
  - *Success Criteria:* Intake and vital acquisition completed in $< 90$ seconds; 100% of physiological red flags trigger instant escalation.
- **Evidence Tag:** `SUPPORTED` (MoHFW Indian Public Health Standards 2022; NHSRC ASHA Guidelines; BPUT B01, B02, B07).

---

## 4. Granular Specification for Role 3: Referral / Transfer Staff

### 4.1 Profile & Environmental Identity
- **1. Role Name:** Referral Coordinator / Transfer Desk Staff (`ROLE_REFERRAL_STAFF`).
- **2. Real-World Responsibility:** Dedicated hospital transfer coordinator, emergency liaison officer, or emergency ambulance (108) dispatch manager coordinating inter-facility patient transit.
- **3. Primary Environment:** Government District Hospital Referral Desk, Regional Health Directorate Transfer Hub, 108 Emergency Control Room, Industrial Ambulance Base.

### 4.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Ensure safe, capability-verified, and bed-confirmed transfer of acute patients from resource-insufficient facilities to capable receiving institutions, eliminating "blind referrals" and transit mortality.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 3.1:* Receive and review doctor-signed referral requisitions and capability justifications (`B13`, `C05`).
  - *JTBD 3.2:* Inspect FACILITYGRAPH destination recommendations for verified specialty, ICU bed, and surgical readiness.
  - *JTBD 3.3:* Contact receiving facility transfer desk to secure pre-arrival bed reservation.
  - *JTBD 3.4:* Dispatch medicalized transport (108 ALS/BLS ambulance) and attach structured Referral Pack.
  - *JTBD 3.5:* Track transit status (`DISPATCHED`, `IN_TRANSIT`, `ARRIVED`, `HANDOFF_CONFIRMED`).
- **6. Typical Operational Workflow:**
  $$\text{Receive Referral Order} \to \text{Inspect FACILITYGRAPH Matches} \to \text{Confirm Receiving Bed} \to \text{Assign Ambulance} \to \text{Transmit Digital Pack} \to \text{Track Transit} \to \text{Confirm Handoff}$$

### 4.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Ambulance vehicle ID, driver/paramedic contact, dispatch timestamp, estimated transit time (ETA), transit delay flags, arrival confirmation.
- **8. Information Consumed:** Doctor-signed Referral Summary, required clinical capabilities (e.g., ventilator, pediatric surgery, blood group match), receiving facility live feasibility status, transit route conditions.
- **9. Information Verified:** Receiving hospital bed acceptance acknowledgment; vehicle oxygen/equipment readiness.
- **10. Information Modified:** Logistical transit status, ambulance assignment, transit notes.

### 4.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Selecting final transport carrier (108 ALS vs BLS vs private ambulance).
  - Updating logistical status of referral lifecycle.
  - Flagging transit emergency delays to receiving facility.
- **12. Unauthorized Decisions:**
  - Initiating or canceling a clinical referral without physician authorization.
  - Modifying clinical diagnostic notes, medication regimens, or patient risk bands.

### 4.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** FACILITYGRAPH Matching Engine (`C05`, `C06`), Haversine Transit Optimization, Structured Referral Pack Synthesis (`B13`).
- **14. Visible AI Outputs:** Ranked list of capable destination hospitals with distance, travel time, and capability match scores.
- **15. Restricted AI Controls:** Cannot autonomously dispatch ambulances or alter clinical referral criteria.
- **16. Evidence/Provenance Requirements:** Referral pack must link to verified clinician signature and timestamped clinical reason.
- **17. Uncertainty Requirements:** System must highlight receiving facility capability uncertainties (e.g., *"ICU bed count unverified in $> 4$ hours"*).

### 4.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Expedited "Golden Hour" transfer dispatch for acute trauma, stroke, and STEMI cases within 15 minutes.
- **19. Referral Responsibilities:** End-to-end custody of logistical referral loop until physical handoff sign-off.
- **20. Follow-up Responsibilities:** Verification that patient actually arrived and was admitted at the target center.
- **21. Outcome Responsibilities:** Recording transfer completion status (`HANDOFF_SUCCESS`, `TRANSIT_DEATH`, `REFUSED_AT_DESTINATION`).

### 4.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** High; handles patient demographic and clinical summaries; must comply with data transit protections.
- **23. Access Sensitivity:** Tier 3 (Referral summary, logistical coordinates; zero access to full raw medical psychiatric or confidential notes).
- **24. Failure Scenarios:** Dispatching ambulance to facility that just ran out of ICU beds; transfer pack data lost during transit; ambulance breakdown without re-routing.
- **25. Permission Risks:** Dispatching referral without valid clinician sign-off.
- **26. Human-Oversight Requirements:** Transfer execution strictly gated by digital or verified verbal doctor order.
- **27. Accessibility Requirements:** Large-format map display, telephone one-click dialer integration for receiving hospital desks.
- **28. Device & Connectivity Constraints:** Desktop dispatch console or ruggedized mobile terminal with GPS; tolerant of variable mobile data.
- **29. Training & Digital Literacy Constraints:** Medium literacy; logistics/dispatch dashboard orientation.
- **30. Expected Frequency of Use:** Episodic to frequent (5–30 transfers/shift depending on facility tier).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Patient arrives in terminal state at hospital without functioning ventilator; turned away at gate.
  - *Success Criteria:* Zero blind referrals; 100% of dispatched transfers pre-acknowledged by destination facility.
- **Evidence Tag:** `SUPPORTED` (MoHFW National Ambulance Guidelines; NHSRC Referral Protocols 2022; BPUT B13, C05).

---

## 5. Granular Specification for Role 4: Patient

### 5.1 Profile & Environmental Identity
- **1. Role Name:** Patient (`ROLE_PATIENT`).
- **2. Real-World Responsibility:** Care-seeking citizen presenting with subjective symptoms, bodily distress, or acute trauma.
- **3. Primary Environment:** Self-service kiosk or waiting area mobile portal across all six operating environments.

### 5.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Clearly communicate symptoms in native language, avoid prolonged waiting room delays, understand clinical assessment, and receive clear, actionable post-consultation recovery instructions.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 4.1:* Describe symptoms freely using spoken vernacular (Odia/Hindi) or typed text (`B01`, `B02`).
  - *JTBD 4.2:* Upload photographs of physical prescriptions, lab slips, or hospital cards (`B03`, `B04`).
  - *JTBD 4.3:* Answer simple multiple-choice follow-up questions (`B08`) to clarify duration or red flags.
  - *JTBD 4.4:* Track position in doctor consultation queue transparently.
  - *JTBD 4.5:* Access clinician-approved discharge instructions, prescriptions, and follow-up appointment dates.
- **6. Typical Operational Workflow:**
  $$\text{Open Portal / Scan Kiosk QR} \to \text{Provide Consent} \to \text{Voice/Text Intake} \to \text{Upload Slips} \to \text{Answer Questions} \to \text{Wait in Queue} \to \text{Doctor Visit} \to \text{Receive Approved Plan}$$

### 5.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Symptom narrative, onset duration, pain description, uploaded medical document photos, question responses, emergency contact, demographic details.
- **8. Information Consumed:** Consent terms, queue status number, doctor-approved Master Clinical Report summary, vernacular care instructions, prescribed medication calendar, red-flag warning signs.
- **9. Information Verified:** Confirmation of own demographic identity, confirmed symptom onset timeline.
- **10. Information Modified:** Unsubmitted intake draft inputs; corrections to misspelled names or phone numbers.

### 5.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Granting or revoking digital consent for data processing (`B14`).
  - Choosing preferred language (English, Hindi, Odia).
  - Confirming or correcting self-reported symptom narrative.
  - Deciding to accept or refuse voluntary treatment / transfer.
- **12. Unauthorized Decisions:**
  - Modifying clinical diagnoses, triage acuity scores, or doctor's prescription orders.
  - Accessing internal doctor notes, unverified differential diagnoses, or raw AI risk heuristics.
  - Accessing other patients' data or operational facility metrics.

### 5.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** Vernacular Voice Speech-to-Text (`B02`), Language Translation (`B09`), Next-Best Clarification Prompts (`B08`).
- **14. Visible AI Outputs:** Vernacular transcript confirmation ("Did you say fever for 3 days?"), simplified multiple-choice clarification questions.
- **15. Restricted AI Controls:** System strictly conceals from the patient:
  - Raw mathematical uncertainty metrics ($U_t$) and complex risk vectors.
  - Probabilistic differential diagnostic rankings (to prevent anxiety and harmful self-medication).
- **16. Evidence/Provenance Requirements:** Can view thumbnail of uploaded lab slip confirming document capture.
- **17. Uncertainty Requirements:** If patient does not know an answer, system provides an explicit "I don't know" button rather than forcing a guess.

### 5.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Ability to trigger a "Call Nurse / I Feel Worse" distress button from the mobile waiting screen.
- **19. Referral Responsibilities:** Reviewing approved destination facility coordinates and instructions.
- **20. Follow-up Responsibilities:** Adhering to medication calendar; presenting for scheduled follow-up revisit.
- **21. Outcome Responsibilities:** Reporting recovery progress via simple SMS / portal post-discharge feedback prompt.

### 5.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** Maximum; primary data owner governed by Digital Personal Data Protection (DPDP) Act 2023.
- **23. Access Sensitivity:** Tier 4 (Confined strictly to own approved record; zero access to system/staff tiers).
- **24. Failure Scenarios:** Patient speaks colloquial dialect not recognized by Whisper; battery dies while waiting; inability to read text prompts; panic caused by misinterpreted medical terms.
- **25. Permission Risks:** Accessing another patient's records on shared waiting-room tablet.
- **26. Human-Oversight Requirements:** All patient-facing medical outputs must pass through licensed clinician sign-off.
- **27. Accessibility Requirements:** Large typography, high-contrast buttons, voice audio replay of all text instructions in Odia/Hindi for low-literacy users.
- **28. Device & Connectivity Constraints:** Cheap Android smartphone (2G/4G) or physical kiosk touch screen; must function with minimal data bandwidth.
- **29. Training & Digital Literacy Constraints:** Extreme variation (from completely illiterate rural laborers to tech-savvy urban students); zero learning curve permitted; voice-first design.
- **30. Expected Frequency of Use:** Episodic (1–4 visits per year).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Patient abandons queue due to incomprehensible UI; critical red flag concealed by poor translation.
  - *Success Criteria:* Intake completed in vernacular in $< 3$ minutes; 100% comprehension of post-consultation warning signs.
- **Evidence Tag:** `SUPPORTED` (ABDM Citizen Health Record Norms; DPDP Act 2023; BPUT B01, B02, B14).

---

## 6. Granular Specification for Role 5: Caregiver / Patient Attendant

### 6.1 Profile & Environmental Identity
- **1. Role Name:** Caregiver / Patient Attendant (`ROLE_CAREGIVER`).
- **2. Real-World Responsibility:** Family member, relative, guardian, or escort accompanying a pediatric, geriatric, unconscious, or acutely incapacitated patient.
- **3. Primary Environment:** Waiting area, triage desk, casualty resuscitation room, bedside in all six environments.

### 6.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Provide accurate history for an incapacitated family member, understand the patient's critical condition, coordinate transport and pharmacy, and manage post-discharge care.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 5.1:* Provide surrogate symptom narrative and chronic disease history on behalf of patient (`B01`, `B02`).
  - *JTBD 5.2:* Grant surrogate legal consent in pediatric cases or emergency surrogate protocol (`B14`).
  - *JTBD 5.3:* Upload past prescriptions, discharge summaries, or vaccination cards (`B03`, `B04`).
  - *JTBD 5.4:* Receive doctor-approved emergency instructions, pharmacy slips, and referral travel plans.
- **6. Typical Operational Workflow:**
  $$\text{Identify Relationship to Patient} \to \text{Provide Consent / Surrogate Auth} \to \text{Submit History} \to \text{Accompany to Exam} \to \text{Receive Approved Care Plan}$$

### 6.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Patient history, observed onset timeline, known allergies, chronic drugs, relationship to patient, guardian phone number.
- **8. Information Consumed:** Same scope as Patient role: doctor-approved Master Clinical Report summary, medication instructions, referral directions.
- **9. Information Verified:** Confirmation of patient identity and relationship.
- **10. Information Modified:** Unsubmitted intake draft inputs.

### 6.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Granting legal guardian consent for pediatric patients ($< 18$ years) or mentally incapacitated adults.
  - Submitting surrogate symptom descriptions.
- **12. Unauthorized Decisions:**
  - Any access to patient's confidential records without documented patient consent or legal surrogate authorization.
  - Modifying doctor's clinical diagnoses, orders, or prescriptions.

### 6.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** Vernacular Voice Intake (`B02`), Document OCR (`B04`), Follow-up Clarification Prompts (`B08`).
- **14. Visible AI Outputs:** Surrogate intake confirmation, simple follow-up questions.
- **15. Restricted AI Controls:** Same restrictions as Patient role; internal clinical reasoning and differential rankings are strictly concealed.
- **16. Evidence/Provenance Requirements:** History entered by caregiver is explicitly tagged `SOURCE_CAREGIVER_SURROGATE` in the provenance graph.
- **17. Uncertainty Requirements:** Explicit capture when caregiver is uncertain of exact medication names or dosages.

### 6.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Rapid provision of baseline medical history while resuscitation team works on patient.
- **19. Referral Responsibilities:** Physical escort during ambulance transit; custody of paper referral pack.
- **20. Follow-up Responsibilities:** Administration of home medications; bringing patient for scheduled review.
- **21. Outcome Responsibilities:** Reporting patient recovery state post-discharge.

### 6.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** High; handling another individual's health information; risk of family conflict over disclosure of sensitive conditions (e.g., pregnancy, psychiatric illness, HIV status).
- **23. Access Sensitivity:** Tier 4 (Tied strictly to designated patient's approved summary; zero staff-level access).
- **24. Failure Scenarios:** Caregiver provides incorrect medication history; caregiver withholds stigmatized illness; caregiver unauthorized by adult conscious patient.
- **25. Permission Risks:** Caregiver accessing adult patient's private reproductive or mental health records without consent.
- **26. Human-Oversight Requirements:** Clinician must verify surrogate consent and note patient's competence level.
- **27. Accessibility Requirements:** Audio playback in Odia/Hindi for illiterate caregivers.
- **28. Device & Connectivity Constraints:** Low-end smartphone or shared hospital kiosk.
- **29. Training & Digital Literacy Constraints:** Variable; intuitive voice-driven flow.
- **30. Expected Frequency of Use:** Episodic.
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Lethal drug interaction due to misreported caregiver history; unauthorized privacy breach.
  - *Success Criteria:* Seamless surrogate intake completed in $< 3$ mins with explicit provenance tagging.
- **Evidence Tag:** `SUPPORTED` (Indian Guardians and Wards Act; NMC Ethics Regulations 2023; BPUT B01, B14).

---

## 7. Granular Specification for Role 6: Facility Administrator

### 7.1 Profile & Environmental Identity
- **1. Role Name:** Facility Administrator (`ROLE_FACILITY_ADMIN`).
- **2. Real-World Responsibility:** Medical Superintendent, Hospital Director, Chief Medical Officer, or Clinic Operations Manager managing institutional resources, clinical capacity, bed allocations, and operational compliance.
- **3. Primary Environment:** Administrative Office across Government Hospitals, Large PHCs/CHCs, Corporate Health Centers, Industrial Plants.

### 7.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Maintain accurate real-time institutional capability profiles, eliminate waiting room bottlenecks, prevent departmental bed-blocking, ensure specialist coverage, and optimize referral throughput.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 6.1:* Maintain institutional FACILITYGRAPH profile (active ICU beds, functional ventilators, oxygen pressure, on-duty specialist roster) (`C05`).
  - *JTBD 6.2:* Monitor live departmental queue volumes, wait-time distributions, and acuity surges (`B11`).
  - *JTBD 6.3:* Reallocate nursing staff or open temporary observation surge beds during peak influx.
  - *JTBD 6.4:* Monitor inter-facility referral inbound acceptance and outbound dispatch metrics (`C06`).
  - *JTBD 6.5:* Generate statutory operational throughput and capacity utilization reports.
- **6. Typical Operational Workflow:**
  $$\text{Open Facility Ops Board} \to \text{Review Bed Occupancy \& Equipment} \to \text{Update On-Duty Roster} \to \text{Audit Queue Wait Times} \to \text{Adjust Capacity Thresholds}$$

### 7.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Facility tier classification, total/available bed counts, specialist on-duty schedules, functioning diagnostic modalities (X-ray, CT, Ultrasound, Lab), blood bank stock levels.
- **8. Information Consumed:** Aggregated department wait times, queue bottleneck alerts, referral turnaround statistics, syndromic surge alerts from SIGNALGRAPH.
- **9. Information Verified:** Staff shift rosters, diagnostic equipment operational status.
- **10. Information Modified:** Active bed availability, equipment maintenance status flags, department capacity thresholds.

### 7.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Declaring facility status as `CAPACITY_EXHAUSTED` or `DIVERT_NON_EMERGENCY`.
  - Reallocating clinical staff between outpatient and triage desks.
  - Modifying institutional capability parameters in FACILITYGRAPH.
- **12. Unauthorized Decisions:**
  - Viewing un-anonymized individual clinical encounter files (unless formally authorized for adverse event audit).
  - Overriding a clinician's individual medical diagnosis, prescription, or disposition order.
  - Altering immutable system audit records.

### 7.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** FACILITYGRAPH Care Feasibility Engine (`C05`), SIGNALGRAPH Epidemiological Aggregator (`C07`), Queue Flow Analytics (`B11`).
- **14. Visible AI Outputs:** 7-day rolling patient arrival forecasts, syndromic cluster alerts, regional referral flow heatmaps.
- **15. Restricted AI Controls:** Cannot autonomously adjust hospital bed capacity figures; figures must reflect real physical resources.
- **16. Evidence/Provenance Requirements:** Capacity adjustments must record timestamp and administrator user ID.
- **17. Uncertainty Requirements:** System must highlight unverified capacity metrics (e.g., *"Blood bank units not refreshed in 12 hours"*).

### 7.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Declaring internal disaster / mass casualty protocol; activating surge capacity beds.
- **19. Referral Responsibilities:** Establishing bilateral transfer MoUs with tertiary centers; auditing rejected referrals.
- **20. Follow-up Responsibilities:** Auditing overall department follow-up compliance rates.
- **21. Outcome Responsibilities:** Reviewing hospital-wide mortality and complication registries.

### 7.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** Medium; views aggregated institutional data and de-identified case counts; strictly barred from patient PII.
- **23. Access Sensitivity:** Tier 5 (Operational, capacity, and resource settings; zero individual patient chart access).
- **24. Failure Scenarios:** Failing to update ventilator out-of-order status, causing a diverted patient to arrive; inaccurate bed reporting.
- **25. Permission Risks:** Snooping on VIP patient records if un-anonymized access controls fail.
- **26. Human-Oversight Requirements:** All capacity and diversion declarations require manual administrator authorization.
- **27. Accessibility Requirements:** High-density desktop dashboard; responsive layout for management tablets.
- **28. Device & Connectivity Constraints:** Modern desktop PC / laptop; stable local network.
- **29. Training & Digital Literacy Constraints:** Medium-high digital literacy; hospital operations background.
- **30. Expected Frequency of Use:** Daily / shift-based (2–5 times per day).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Inaccurate facility profile leads to inbound patient death during transfer; departmental gridlock.
  - *Success Criteria:* Zero blind referrals received; facility capability state updated in $< 60$ seconds.
- **Evidence Tag:** `SUPPORTED` (MoHFW Hospital Management Guidelines; IPHS 2022; BPUT B11, C05).

---

## 8. Granular Specification for Role 7: System Administrator

### 8.1 Profile & Environmental Identity
- **1. Role Name:** System Administrator (`ROLE_SYSTEM_ADMIN`).
- **2. Real-World Responsibility:** Health informatics engineer, IT systems manager, or infrastructure specialist maintaining software reliability, user identity access, security credentials, database backups, and tamper-evident audit logging.
- **3. Primary Environment:** Server room, IT department, or remote terminal console.

### 8.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Maintain 99.9% platform availability, ensure zero-cost local execution operates reliably, enforce strict RBAC boundaries, safeguard cryptographic audit trails, and ensure compliance with DPDP 2023 24-hour ephemeral retention policies.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 7.1:* Provision and manage user accounts, roles, and credential lifecycles (`B17`).
  - *JTBD 7.2:* Monitor local AI runtime performance (Ollama/Qwen memory, Whisper CPU utilization).
  - *JTBD 7.3:* Execute automated ephemeral data purging (24-hour cleanup of raw voice recordings and OCR document scans) (`B16`).
  - *JTBD 7.4:* Maintain immutable append-only audit ledger integrity (`B17`).
  - *JTBD 7.5:* Configure local network endpoints and SQLite/PostgreSQL database backups.
- **6. Typical Operational Workflow:**
  $$\text{Login to System Console} \to \text{Review System Health \& Memory} \to \text{Audit Security Logs} \to \text{Manage User Roles} \to \text{Verify Ephemeral Cleanup}$$

### 8.3 Information Consumption, Provision & Verification
- **7. Information Provided:** System configurations, local runtime port bindings, user account creation, security key rotations.
- **8. Information Consumed:** Server CPU/RAM telemetry, local model inference latency, database error logs, authentication access logs, audit trail checksums.
- **9. Information Verified:** System integrity checksums, database schema migrations.
- **10. Information Modified:** Platform environment variables, active user role assignments, network settings.

### 8.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Revoking or suspending compromised user credentials.
  - Restarting backend services and local AI inference runners.
  - Triggering manual database backups and routine ephemeral purges.
- **12. Unauthorized Decisions:**
  - Strictly barred from viewing, modifying, or creating clinical case records, vitals, or diagnoses.
  - Barred from altering or deleting cryptographic audit log entries.
  - Barred from approving medical referrals or discharges.

### 8.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** None directly in clinical workflows; manages local model runtime processes (Ollama, CTranslate2).
- **14. Visible AI Outputs:** Model latency (ms/token), system memory allocation, batch inference error codes.
- **15. Restricted AI Controls:** Cannot manipulate AI clinical prompts or override safety bounds without clinical governance sign-off.
- **16. Evidence/Provenance Requirements:** Maintains immutable logging of all software version changes and model weights hashes.
- **17. Uncertainty Requirements:** Monitors system-level failure alerts (e.g., *"Local SLM timeout $\to$ fallback to deterministic rules"*).

### 8.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** Ensuring high-availability failover to local SQLite mode during network or power grid collapse.
- **19. Referral Responsibilities:** Ensuring inter-facility API sync endpoints remain functional.
- **20. Follow-up Responsibilities:** Ensuring backup integrity of longitudinal outcome databases.
- **21. Outcome Responsibilities:** Archiving de-identified outcome datasets for institutional audit.

### 8.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** Maximum infrastructure privilege; zero clinical access; must be prevented from inspecting decrypted patient PII.
- **23. Access Sensitivity:** Tier 6 (Platform infrastructure and security logs; zero access to clinical patient charts).
- **24. Failure Scenarios:** Accidental deletion of database; failure of local Whisper process causing audio intake stall; omission of 24h ephemeral purge.
- **25. Permission Risks:** Privilege escalation or unauthorized database dump containing patient data.
- **26. Human-Oversight Requirements:** All administrator actions are recorded in an independent, secondary, tamper-evident log.
- **27. Accessibility Requirements:** Standard technical console / CLI interface.
- **28. Device & Connectivity Constraints:** Server workstation or secure management laptop.
- **29. Training & Digital Literacy Constraints:** High technical digital literacy; Linux/Windows system administration competence.
- **30. Expected Frequency of Use:** Periodic (daily health check; on-call for incidents).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Complete platform crash during high-volume OPD; data breach of un-sanitized patient records.
  - *Success Criteria:* Zero platform downtime during clinical hours; 100% ephemeral purge compliance within 24 hours.
- **Evidence Tag:** `SUPPORTED` (ISO/IEC 27001; DPDP Act 2023; BPUT B15, B16, B17).

---

## 9. Granular Specification for Role 8: Research / Evaluation User

### 9.1 Profile & Environmental Identity
- **1. Role Name:** Research / Evaluation User (`ROLE_RESEARCHER`).
- **2. Real-World Responsibility:** Clinical AI researcher, academic biostatistician, or institutional AI safety auditor benchmarking extraction accuracy, calibration of uncertainty ($U_t$), algorithmic bias across dialects, and syndromic telemetry trends.
- **3. Primary Environment:** Academic research laboratory, university hospital AI unit, public health epidemiology department.

### 9.2 Goals, Jobs-To-Be-Done & Workflow
- **4. Primary Goals:** Rigorously evaluate algorithmic safety, detect clinical performance degradation across linguistic dialects (Odia vs Hindi vs English), calibrate uncertainty scoring against ground truth, and analyze macro syndromic signals in SIGNALGRAPH without exposing real patient identities.
- **5. Main Jobs-To-Be-Done (JTBD):**
  - *JTBD 8.1:* Run automated synthetic benchmark test suites evaluating model extraction precision, recall, and F1 scores (`C11`).
  - *JTBD 8.2:* Calculate agreement rates (Cohen's Kappa) between AI triage recommendations and qualified physician decisions.
  - *JTBD 8.3:* Evaluate epistemic uncertainty calibration ($U_t$) using Brier scores and calibration curves.
  - *JTBD 8.4:* Inspect macro-epidemiological syndromic anomalies in SIGNALGRAPH (`C07`).
  - *JTBD 8.5:* Perform algorithmic bias audits across demographic and geographic cohorts.
- **6. Typical Operational Workflow:**
  $$\text{Load Synthetic Benchmark Suite} \to \text{Execute Extraction Pipeline} \to \text{Compute Calibration Metrics} \to \text{Inspect Bias Distributions} \to \text{Export De-identified Evaluation Report}$$

### 9.3 Information Consumption, Provision & Verification
- **7. Information Provided:** Synthetic test vignettes, ground-truth clinical annotations, evaluation benchmark parameters.
- **8. Information Consumed:** De-identified synthetic case outputs, aggregate confusion matrices, calibration plots, macro SIGNALGRAPH telemetry.
- **9. Information Verified:** Verification of model accuracy against validated synthetic clinical benchmarks.
- **10. Information Modified:** Benchmark configuration files, synthetic dataset tags (strictly non-production).

### 9.4 Decision Authority Boundaries
- **11. Authorized Decisions:**
  - Flagging model performance degradation or linguistic bias.
  - Generating academic and safety evaluation reports.
  - Recommending algorithmic tuning or threshold updates to the clinical governance board.
- **12. Unauthorized Decisions:**
  - Absolute zero access to live, identified patient encounters.
  - Barred from altering production database records, active clinical queues, or clinical decisions.
  - Barred from modifying live production model weights or system prompts directly.

### 9.5 AI Interaction & Safety Constraints
- **13. Interacting AI Capabilities:** Offline evaluation runners for Extraction (`B03`-`B05`), CAREGRAPH (`C01`), Uncertainty Engine (`C03`), SIGNALGRAPH (`C07`).
- **14. Visible AI Outputs:** Aggregate performance metrics (precision, recall, AUROC, Brier score, Cohen's Kappa), macro heatmaps.
- **15. Restricted AI Controls:** Strictly isolated from production execution pipelines.
- **16. Evidence/Provenance Requirements:** Every benchmark result must record model checkpoint version, prompt hash, and benchmark dataset commit hash.
- **17. Uncertainty Requirements:** Evaluates whether model uncertainty correctly correlates with error rate (rejection accuracy).

### 9.6 Responsibilities Across Care Continuum
- **18. Emergency Responsibilities:** None during live operations.
- **19. Referral Responsibilities:** Evaluating aggregate referral matching efficiency across synthetic network graphs.
- **20. Follow-up Responsibilities:** Auditing long-term outcome concordance metrics.
- **21. Outcome Responsibilities:** Calculating system-wide Brier score on finalized case outcomes.

### 9.7 Privacy, Ergonomics & Failure Modes
- **22. Privacy Sensitivity:** Strict zero-PII boundary; governed by ICMR Ethical Guidelines for AI in Healthcare 2023.
- **23. Access Sensitivity:** Tier 7 (Confined strictly to synthetic data sandboxes and aggregated de-identified telemetry; zero live clinical access).
- **24. Failure Scenarios:** Evaluating models on biased synthetic datasets; leaking de-identified data through linkability attacks.
- **25. Permission Risks:** Attempting to query live production database from evaluation script.
- **26. Human-Oversight Requirements:** All research reports and safety findings must be reviewed by the clinical governance board.
- **27. Accessibility Requirements:** Data science dashboard (Jupyter/Streamlit or clean analytics dashboard).
- **28. Device & Connectivity Constraints:** Research workstation; local execution.
- **29. Training & Digital Literacy Constraints:** High technical literacy (data science, biostatistics).
- **30. Expected Frequency of Use:** Periodic / Milestone-based (weekly evaluation runs, post-hackathon grant studies).
- **31. Consequences of Incorrect Support & Success Criteria:**
  - *Consequences of Failure:* Undetected model drift causes severe real-world under-triage of acute illness; publication of invalid safety claims.
  - *Success Criteria:* 100% reproducible benchmark evaluation; zero exposure of live patient records.
- **Evidence Tag:** `SUPPORTED` (ICMR Ethical Guidelines for AI in Healthcare 2023; WHO AI Ethics Guidance; BPUT B18, C11).

---

## 10. Summary Role Comparison Matrix

| Dimension | 1. Clinician | 2. Nurse / Health Worker | 3. Referral Staff | 4. Patient | 5. Caregiver | 6. Facility Admin | 7. System Admin | 8. Researcher |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Medicolegal Authority** | **Supreme (Full)** | Support / Intake | Logistical | Self-agency | Surrogate agency | Operational | Technical | Zero |
| **Data Scope** | Full Master Case | Intake + Vitals | Referral Pack | Own Approved File | Patient Approved File | Aggregated Stats | System Telemetry | Synthetic / Aggregated |
| **Clinical Modification** | **YES (Unrestricted)** | Intake/Vitals Only | Logistical Only | Intake Draft Only | Intake Draft Only | NO | NO | NO |
| **Care Decision Gate** | **YES (Exclusive)** | NO | NO | NO | NO | Bed Allocation Only | NO | NO |
| **Emergency Escalation** | **YES** | **YES** | Logistics Flag | Distress Call | Distress Call | Disaster Protocol | Failover Mode | NO |
| **AI Output Visibility** | Full Triage + Provenance | Intake Prompts | Facility Match | Plain Summary | Plain Summary | Macro Queues | Latency/Errors | Benchmark Metrics |
| **PII Exposure** | Authorized Full | Authorized Full | Minimal Necessary | Own Only | Patient Only | Scrubbed / Aggregated | Scrubbed / Zero | Zero (Synthetic Only) |
| **Audit Ledger Impact** | Action Logged | Action Logged | Action Logged | Read Logged | Read Logged | Action Logged | Action Logged (Dual) | Benchmark Logged |
| **Hardware Baseline** | PC / Tablet (4GB+) | Android Tablet (2GB+) | Desktop / Phone | Phone / Kiosk | Phone / Kiosk | Desktop PC | Server Console | Research PC |
