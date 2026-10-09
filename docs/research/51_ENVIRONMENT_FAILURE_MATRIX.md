# CLINOVA AI — Target Environment Failure & Exception Matrix

> **Document ID:** `RES-51`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Fault-Tolerance Methodology

Healthcare software operating across Indian primary, secondary, and occupational facilities is exposed to severe infrastructure volatility, extreme staffing shortages, device degradation, and chaotic clinical handoffs. 

Phase 4 defines a comprehensive **26-Failure Mode Operational Matrix**. For each failure mode, the system establishes a deterministic resilience chain:
$$\text{Environment} \longrightarrow \text{Failure Mode} \longrightarrow \text{User Affected} \longrightarrow \text{CLINOVA Behavior} \longrightarrow \text{Human Action} \longrightarrow \text{Data State} \longrightarrow \text{Safety Consequence} \longrightarrow \text{Audit Event} \longrightarrow \text{Recovery}$$

### Core Resilience Principles:
1. **Clinical Operations Must Never Halt:** Loss of internet, slow networks, or speech engine failures must never prevent a clinician from examining a patient, logging vitals, or authorizing emergency transfer.
2. **Local Autonomous Execution:** The Local Clinic Server on LAN maintains full read/write operational autonomy independent of external cloud connectivity.
3. **Explicit Epistemic Uncertainty Degradation:** When data, diagnostics, or telemetry fail, the system explicitly elevates epistemic uncertainty ($U_t \uparrow$), suppresses automated inferences, and prompts humans for direct verification.

---

## 2. Comprehensive 26-Failure Operational Matrix

### Failure Mode 1: No Internet (Complete WAN Blackout)
- **ENVIRONMENT:** All Environments (especially `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_GOV_HOSPITAL`).
- **USER AFFECTED:** All roles (Nurse, Doctor, Intake Staff).
- **CLINOVA BEHAVIOR:** Transparently switches to Local Offline Autonomous mode. UI displays non-intrusive offline badge: `🌐 Offline Mode (Local LAN Active)`. All Master Case creations, vitals logging, risk scores, and clinical notes write to local SQLite/PostgreSQL on the Local Clinic Server. Cloud sync requests are appended to an encrypted transactional queue.
- **HUMAN ACTION:** Continue clinical consultations, triage, and prescriptions without alteration or delay.
- **DATA STATE:** `SYNC_PENDING_LOCAL_STORED`. Full local consistency across LAN; zero data loss.
- **SAFETY CONSEQUENCE:** Zero negative impact on immediate patient care; external referral pre-notifications to outside hospitals are temporarily held or converted to local printable thermal passes.
- **AUDIT EVENT:** `SYS_NET_OFFLINE_DETECTED` logged with local timestamp.
- **RECOVERY:** Background daemon polls WAN gateway. When connectivity is restored ($> 60$s stable ping), executes mutual-TLS batch sync with central registry.

---

### Failure Mode 2: Slow Internet (Packet Loss / High Latency > 3000ms)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_PUBLIC_CAMP`.
- **USER AFFECTED:** Clinicians, Triage Nurses.
- **CLINOVA BEHAVIOR:** Automatically disables high-bandwidth background calls (e.g., non-critical telemetry telemetry, external document sync). Prioritizes lightweight JSON API payloads over local LAN. Imposes client-side timeout caps ($< 800$ms); if cloud response exceeds threshold, gracefully falls back to local cache without freezing the UI.
- **HUMAN ACTION:** Continue workflow; UI remains snappy due to local LAN routing.
- **DATA STATE:** `LOCAL_PRIMARY_BACKGROUND_SYNC_THROTTLED`.
- **SAFETY CONSEQUENCE:** Zero. UI responsiveness is preserved; prevents physician input latency and typing lag.
- **AUDIT EVENT:** `SYS_NET_LATENCY_SPIKE` logged.
- **RECOVERY:** Restores standard telemetry frequency once ping latency drops below 400ms.

---

### Failure Mode 3: Power Failure (Mains Grid Outage)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_GOV_HOSPITAL`.
- **USER AFFECTED:** All Facility Users.
- **CLINOVA BEHAVIOR:** Local Clinic Server and workstations running on battery/UPS detect power loss via AC-sensing daemon. UI activates **Low-Power High-Contrast Mode**, disabling non-essential background animations and background OCR tasks to preserve battery life. SQLite/PostgreSQL forces WAL (Write-Ahead-Log) checkpoint to prevent file corruption.
- **HUMAN ACTION:** In `ENV_PHC`, verify battery inverter level. In `ENV_PUBLIC_CAMP`, switch tablets to external 20,000 mAh power banks.
- **DATA STATE:** `POWER_DEGRADED_STATE_PRESERVED`. Active case drafts auto-saved in local storage.
- **SAFETY CONSEQUENCE:** Prevents total clinic blindness during rural power cuts.
- **AUDIT EVENT:** `SYS_POWER_GRID_FAILURE` logged.
- **RECOVERY:** When grid power returns or diesel generator stabilizes, system restores full operational profile and resumes background OCR/sync workers.

---

### Failure Mode 4: Local Server Failure (Hardware Crash / Disk Failure)
- **ENVIRONMENT:** All Environments.
- **USER AFFECTED:** Triage Nurses, Doctors, Facility Administrators.
- **CLINOVA BEHAVIOR:** Workstation client browsers detect lost connection to Local Clinic Server LAN IP. Client UI alerts: `⚠️ Local Server Unreachable — Switching to Standalone Client Mode`. The browser transitions into local IndexedDB storage, enabling the clinician to continue reading open cases and recording basic emergency notes.
- **HUMAN ACTION:** IT Administrator reboots server or swaps to backup mini-PC; staff prints emergency paper carbon forms if all terminals crash.
- **DATA STATE:** `STANDALONE_BROWSER_BUFFERED`.
- **SAFETY CONSEQUENCE:** Temporary loss of real-time multi-room queue synchronization; doctors coordinate verbally until server recovers.
- **AUDIT EVENT:** `SYS_LOCAL_SERVER_HEARTBEAT_LOST`.
- **RECOVERY:** When replacement server boots, browser client pushes buffered IndexedDB transactions to restore system consistency.

---

### Failure Mode 5: Device Failure (Tablet Battery Dies / Screen Cracks)
- **ENVIRONMENT:** `ENV_PUBLIC_CAMP`, `ENV_PHC`.
- **USER AFFECTED:** Frontline Nurse or ASHA.
- **CLINOVA BEHAVIOR:** Hardware drops off local LAN. The Master Case is not lost because all data was persisted server-side at the completion of each form step.
- **HUMAN ACTION:** Nurse picks up any spare tablet or smartphone, navigates to local server LAN URL, logs in, and immediately resumes the active case by entering the patient's token number.
- **DATA STATE:** `SESSION_MIGRATED_SERVER_INTACT`. Zero unpersisted data loss.
- **SAFETY CONSEQUENCE:** 60-second administrative delay to switch physical hardware; zero clinical risk.
- **AUDIT EVENT:** `AUTH_SESSION_RECONNECTED_NEW_DEVICE`.
- **RECOVERY:** Defective device sent for repair; hot-spare tablet assumes active shift role.

---

### Failure Mode 6: Missing Staff (Solo Doctor Absent)
- **ENVIRONMENT:** `ENV_PHC`.
- **USER AFFECTED:** Rural Patients, Staff Nurse / CHO.
- **CLINOVA BEHAVIOR:** System detects lack of `ROLE_CLINICIAN` active session. Environment config adjusts workflow: activates **Frontline Stabilization & Tele-Consult Protocol**. Prompts CHO/Nurse: `Clinician Unassigned — Cases Queued for Telemedicine Review or Capability-Matched Referral`. The system strictly enforces that non-physician staff cannot execute final prescription or discharge dispositions.
- **HUMAN ACTION:** CHO evaluates vital signs, performs point-of-care rapid diagnostics, initiates tele-consultation bridge via e-Sanjeevani/CLINOVA tele-node, or initiates transfer if patient is unstable.
- **DATA STATE:** `STAFF_VERIFIED_PENDING_CLINICAL_GATE`.
- **SAFETY CONSEQUENCE:** Prevents illegal automated prescribing by non-doctors; guarantees qualified clinical review.
- **AUDIT EVENT:** `WORKFLOW_STAFF_UNAVAILABLE_FALLBACK_ENGAGED`.
- **RECOVERY:** Arriving clinician or tele-reviewer authenticates and batches reviews queued cases.

---

### Failure Mode 7: Staff Overload (Waiting Queue Exceeds Capacity > 100)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PUBLIC_CAMP`.
- **USER AFFECTED:** Casualty Nurses, Outpatient Doctors.
- **CLINOVA BEHAVIOR:** Activates **Dynamic Acuity Backpressure Routing**. The queue sorting algorithm elevates the weighting of vital sign deterioration trajectory ($\Delta R_t / \Delta t$) and suppresses low-acuity routine follow-ups. System automatically highlights red-flag cohort at the very top of the screen in flashing amber/red badges, advising staff: `Mass Surge Detected: Prioritizing ESI Level 1-2 Cases`.
- **HUMAN ACTION:** Facility administrator opens secondary consultation room; triage nurses perform rapid spot-check vitals in waiting hall.
- **DATA STATE:** `QUEUE_BACKPRESSURE_ACTIVE`.
- **SAFETY CONSEQUENCE:** Prevents critically deteriorating patients (silent septic shock, atypical MI) from dying unnoticed in deep queues.
- **AUDIT EVENT:** `OPS_QUEUE_SURGE_THRESHOLD_EXCEEDED`.
- **RECOVERY:** Queue weightings normalize as throughput restores average waiting times below threshold.

---

### Failure Mode 8: Specialist Unavailable (Cardiologist / Surgeon Off-Duty)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_INDUSTRIAL_HEALTH`.
- **USER AFFECTED:** Duty Medical Officer, Patient.
- **CLINOVA BEHAVIOR:** When clinician selects candidate action `REFER_INTERNAL_SPECIALTY`, FACILITYGRAPH checks specialist roster. If status is `UNAVAILABLE`, system intercepts: `Cardiology Not Available On-Site. Recommended Action: Acute Medical Stabilization + External Referral via FACILITYGRAPH`. System auto-identifies the nearest tertiary facility with active cardiology coverage.
- **HUMAN ACTION:** Clinician initiates emergency medical stabilization (e.g., dual antiplatelet therapy, heparin, thrombolysis if indicated) and confirms external ambulance transfer.
- **DATA STATE:** `FACILITY_CAPABILITY_EXCEEDED_REFERRAL_MANDATED`.
- **SAFETY CONSEQUENCE:** Eliminates false assumptions of on-site specialist intervention, preventing delayed care.
- **AUDIT EVENT:** `FACILITY_RESOURCE_GAP_INTERCEPT`.
- **RECOVERY:** Receiving tertiary hospital acknowledges transfer and receives pre-arrival digital manifest.

---

### Failure Mode 9: Diagnostic Unavailable (X-Ray / Biochemistry Broken)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PHC`.
- **USER AFFECTED:** Clinician, Lab Technician.
- **CLINOVA BEHAVIOR:** Facility Admin or Lab Tech marks `CAP_XRAY` or `CAP_BIOCHEM` as `OFFLINE_MAINTENANCE` in FACILITYGRAPH. When clinician evaluates a case requiring imaging (e.g., suspected hip fracture), CLINOVA displays: `⚠️ On-Site X-Ray Non-Functional. Epistemic Uncertainty High (Ut = 0.72). Candidate Actions: Clinical Splinting + Outward Imaging Referral`.
- **HUMAN ACTION:** Doctor relies on physical examination maneuvers (Ottawa rules, clinical crepitus), immobilizes limb, and orders external imaging.
- **DATA STATE:** `EVIDENCE_UNAVAILABLE_UNCERTAINTY_ELEVATED`.
- **SAFETY CONSEQUENCE:** Prevents diagnostic paralysis and keeps clinicians aware of missing objective data.
- **AUDIT EVENT:** `CAPABILITY_STATUS_DEGRADED`.
- **RECOVERY:** Facility technician restores equipment; admin marks capability `VERIFIED`.

---

### Failure Mode 10: Bed Unavailable (Casualty Observation 100% Full)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`.
- **USER AFFECTED:** Triage Nurse, Casualty Medical Officer.
- **CLINOVA BEHAVIOR:** FACILITYGRAPH displays `OBSERVATION_BAY_SATURATED (Occupancy: 28/25)`. The `OBSERVE` candidate action is dynamically deprioritized. System prompts: `Observation Capacity Full. Consider: 1. Discharge Stable Cohort; 2. Expedited Inpatient Ward Transfer; 3. Tertiary Transfer`.
- **HUMAN ACTION:** Doctor reassesses previously stabilized patients to discharge convalescents or arranges corridor cots.
- **DATA STATE:** `CAPACITY_OVERFLOW_FLAGGED`.
- **SAFETY CONSEQUENCE:** Prevents accepting new acute admissions without physical space, avoiding unmonitored hallway deterioration.
- **AUDIT EVENT:** `FACILITY_BED_SATURATION_WARNING`.
- **RECOVERY:** Bed discharges decrement counter, unlocking standard `OBSERVE` pathways.

---

### Failure Mode 11: Referral Destination Unavailable (Tertiary Hospital Saturated)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_GOV_HOSPITAL`, `ENV_INDUSTRIAL_HEALTH`.
- **USER AFFECTED:** Referral Coordinator, Medical Officer.
- **CLINOVA BEHAVIOR:** During referral matching, receiving Tertiary Hospital A returns `ICU_BEDS: 0 / VENTILATORS: 0 (Status: CONFLICTING/STALE)`. CLINOVA rejects automatic routing to Hospital A and reroutes to **Rank-2 Alternative** Tertiary Hospital B (extra 18 km transit, but `ICU_BEDS: 3 VERIFIED`).
- **HUMAN ACTION:** Clinician and 108 ambulance driver agree to transport patient to Hospital B, preventing futile transport to Hospital A.
- **DATA STATE:** `REFERRAL_DESTINATION_REROUTED`.
- **SAFETY CONSEQUENCE:** Eliminates the "Blind Transfer Disaster" where ambulances arrive at hospitals that turn them away at the casualty gate.
- **AUDIT EVENT:** `REFERRAL_DESTINATION_OVERFLOW_REROUTE`.
- **RECOVERY:** Receiving Hospital B acknowledges digital reservation.

---

### Failure Mode 12: Emergency Surge (Mass Casualty Incident / Toxic Leak)
- **ENVIRONMENT:** `ENV_INDUSTRIAL_HEALTH`, `ENV_GOV_HOSPITAL`.
- **USER AFFECTED:** All Staff.
- **CLINOVA BEHAVIOR:** System Administrator or CMO triggers **MCI (Mass Casualty Incident) Emergency Mode**. The UI switches to **START (Simple Triage and Rapid Treatment) Disaster Grid**: Red (Immediate), Yellow (Delayed), Green (Minor), Black (Expectant). Routine intake forms are suppressed; minimum data set enforced (< 30 seconds per casualty).
- **HUMAN ACTION:** Staff divides into triage officer, resuscitation team, and transport coordinators.
- **DATA STATE:** `MCI_BATCH_TRIAGE_ACTIVE`.
- **SAFETY CONSEQUENCE:** Maximizes survival across the patient cohort by allocating scarce resources to salvageable victims.
- **AUDIT EVENT:** `EMERGENCY_MCI_DECLARED`.
- **RECOVERY:** CMO stands down disaster mode; cases return to standard Master Case tracking.

---

### Failure Mode 13: Duplicate Patient / Case (Multiple Open Records for Same Individual)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PUBLIC_CAMP`.
- **USER AFFECTED:** Registration Clerk, Triage Nurse.
- **CLINOVA BEHAVIOR:** System detects matching demographic markers (Phone + Gender + Age $\pm 2$ years) or matching ABHA identifier. Displays non-blocking merge alert: `Potential Duplicate: Case #1042 matches active Case #1018. Merge records or proceed as distinct encounter?`
- **HUMAN ACTION:** Staff inspects photo/face or asks verifying questions. Selects `MERGE` to consolidate or `NEW_ENCOUNTER` if separate visit.
- **DATA STATE:** `RECORDS_CONSOLIDATED_AUDITED`.
- **SAFETY CONSEQUENCE:** Prevents fragmented medical history, conflicting drug orders, and duplicate medication administration.
- **AUDIT EVENT:** `PATIENT_RECORD_DEDUPLICATION_MERGE`.
- **RECOVERY:** Combined record preserves full provenance of both data streams.

---

### Failure Mode 14: Unknown Identity (Unconscious / Unidentified Trauma Victim)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_INDUSTRIAL_HEALTH`.
- **USER AFFECTED:** Casualty Nurse, Police Officer, Clinician.
- **CLINOVA BEHAVIOR:** Registration allows instant 1-click **Emergency Alias Generation**: assigns deterministic temporary pseudonym (`UNKNOWN_MALE_20261008_01`), estimated age, estimated weight, and physical identifiers (tattoos, clothing). Full clinical care unlocked immediately without identity blocking.
- **HUMAN ACTION:** Paramedics initiate immediate resuscitation; police/relatives later present Aadhaar card.
- **DATA STATE:** `IDENTITY_UNVERIFIED_PSEUDONYM_ACTIVE`.
- **SAFETY CONSEQUENCE:** Eliminates any delay in life-saving treatment due to administrative paperwork.
- **AUDIT EVENT:** `PATIENT_IDENTITY_PSEUDONYM_CREATED`.
- **RECOVERY:** Once relatives identify the patient, staff executes `RECONCILE_IDENTITY`, securely linking the emergency pseudonym to the formal ABHA/Aadhaar record without modifying clinical timestamps.

---

### Failure Mode 15: Incomplete Records (Patient Arrives Without Prior History)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_GOV_HOSPITAL`.
- **USER AFFECTED:** Clinician, Nurse.
- **CLINOVA BEHAVIOR:** System flags missing critical baseline domains (Past Cardiac History: Unknown, Drug Allergies: Unknown). Elevates epistemic uncertainty ($U_t \uparrow$). AI suppresses specific drug recommendations that carry high allergy/interaction risks and surfaces safety checklist: `Confirm Penicillin Allergy Status Before Administering Beta-Lactam`.
- **HUMAN ACTION:** Clinician interrogates family attendant or performs test dose / selects safer alternative.
- **DATA STATE:** `EVIDENCE_PARTIAL_UNCERTAINTY_GATED`.
- **SAFETY CONSEQUENCE:** Prevents fatal adverse drug events caused by unrecorded patient allergies.
- **AUDIT EVENT:** `CLINICAL_MISSING_DATA_CHECKLIST_ENGAGED`.
- **RECOVERY:** Verified data entered into Master Case; baseline uncertainty normalizes.

---

### Failure Mode 16: Language Mismatch (Doctor & Patient Speak Different Languages)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL` (Migrant workers), `ENV_CAMPUS_HEALTH` (Out-of-state students).
- **USER AFFECTED:** Patient, Clinician.
- **CLINOVA BEHAVIOR:** Multilingual Vernacular Translation Pipeline kicks in. Patient speaks in Odia/Bengali; system transcribes and normalizes text into English clinical terminology on the doctor workbench while generating translated patient care instructions back into the patient's native dialect.
- **HUMAN ACTION:** Doctor confirms translated chief complaint with patient via simple visual confirmation gestures or hospital attendant.
- **DATA STATE:** `MULTILINGUAL_DUAL_STREAM_RECORDED`.
- **SAFETY CONSEQUENCE:** Eliminates catastrophic clinical miscommunication regarding symptom duration, pain location, and drug dosing.
- **AUDIT EVENT:** `NLP_VERNACULAR_TRANSLATION_ENGAGED`.
- **RECOVERY:** Patient confirms understanding via localized printed slip.

---

### Failure Mode 17: OCR Failure (Illegible Crumpled Prescription)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PHC`.
- **USER AFFECTED:** Triage Nurse, Clinician.
- **CLINOVA BEHAVIOR:** Local PaddleOCR/Tesseract engine encounters torn, blurred, or illegible handwriting; confidence score drops below threshold ($< 0.40$). System marks entity: `OCR_CONFIDENCE_LOW (Illegible Text Block)`. It **refuses to hallucinate drug names** and displays original cropped image snippet side-by-side with an empty input field.
- **HUMAN ACTION:** Staff glances at physical paper, types drug name manually, or asks patient what they take.
- **DATA STATE:** `OCR_REJECTED_MANUAL_VERIFICATION_REQUIRED`.
- **SAFETY CONSEQUENCE:** Completely prevents AI hallucination of incorrect medication dosages from distorted handwriting.
- **AUDIT EVENT:** `OCR_EXTRACTION_CONFIDENCE_REJECTION`.
- **RECOVERY:** Human entry updates Master Case with high provenance verification.

---

### Failure Mode 18: Speech Transcription Failure (Extreme Ambient Noise)
- **ENVIRONMENT:** `ENV_INDUSTRIAL_HEALTH` (> 80 dB machinery), `ENV_PUBLIC_CAMP` (Crowd noise).
- **USER AFFECTED:** Frontline Nurse, Volunteer.
- **CLINOVA BEHAVIOR:** Local faster-whisper speech recognition detects poor Signal-to-Noise Ratio (SNR) or empty transcription. UI displays warning: `⚠️ Audio Unclear Due to Background Noise. Switch to Tap-Based Symptom Checklist or Re-record Closer to Microphone`.
- **HUMAN ACTION:** Worker taps quick-select symptom buttons on touch screen or moves away from industrial generator.
- **DATA STATE:** `AUDIO_FALLBACK_TO_STRUCTURED_TAP`.
- **SAFETY CONSEQUENCE:** Zero data corruption; prevents misunderstood voice commands during clinical intake.
- **AUDIT EVENT:** `ASR_SNR_FAILURE_TOUCH_FALLBACK`.
- **RECOVERY:** Encounter continues seamlessly via touch buttons.

---

### Failure Mode 19: Wrong Facility Data (Database Claims X-Ray Exists, But Tube is Burnt)
- **ENVIRONMENT:** All Environments.
- **USER AFFECTED:** Clinician, Patient.
- **CLINOVA BEHAVIOR:** Doctor orders X-Ray based on outdated system record; technician informs doctor tube is burnt. Doctor clicks **1-Click Capability Feedback**: `Flag Capability Broken (X-Ray)`.
- **HUMAN ACTION:** Doctor updates status from workbench; system immediately updates local FACILITYGRAPH state to `OFFLINE_UNAVAILABLE`.
- **DATA STATE:** `CAPABILITY_STATUS_OVERRIDDEN_HUMAN`.
- **SAFETY CONSEQUENCE:** Prevents subsequent clinicians in other consultation rooms from ordering the broken diagnostic for remaining patients.
- **AUDIT EVENT:** `FACILITYGRAPH_RESOURCE_FLAGGED_BROKEN`.
- **RECOVERY:** Broadcasts capability degradation across all active clinic terminals.

---

### Failure Mode 20: Stale Facility Data (Bed Telemetry $> 12$ Hours Old)
- **ENVIRONMENT:** `ENV_PHC` (Referral network), `ENV_GOV_HOSPITAL`.
- **USER AFFECTED:** Referral Coordinator.
- **CLINOVA BEHAVIOR:** Destination hospital capability status displays in amber with warning icon: `⚠️ Receiving Hospital ICU: STALE (Updated 14h ago)`. Referral engine prompts: `Telephonic Verification Required Before Ambulance Departure. Dial Transfer Desk: +91-XXXXX`.
- **HUMAN ACTION:** Coordinator places quick 30-second telephone call to confirm bed availability before dispatching ambulance.
- **DATA STATE:** `STALE_DATA_WARNING_DISPLAYED`.
- **SAFETY CONSEQUENCE:** Forces human telephone confirmation, eliminating wasted ambulance transfers based on stale electronic data.
- **AUDIT EVENT:** `FACILITY_STALE_DATA_OVERRIDE`.
- **RECOVERY:** Telephonic confirmation updates node state to `VERIFIED`.

---

### Failure Mode 21: Patient Refusal (Patient Refuses Recommended Admission / Referral)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_GOV_HOSPITAL`, `ENV_COMPANY_CLINIC`.
- **USER AFFECTED:** Clinician, Patient, Caregiver.
- **CLINOVA BEHAVIOR:** When clinician selects `ADMIT` or `REFER`, patient declines. Clinician selects **LAMA / DAMA Protocol** (Left Against Medical Advice / Discharge Against Medical Advice). CLINOVA shifts UI into **Risk Counseling & Refusal Capture Mode**. Generates clear vernacular summary of risks explained to patient and logs signed digital/physical refusal.
- **HUMAN ACTION:** Clinician counsels patient on life-threatening consequences; obtains patient/caregiver physical signature or thumbprint on printed refusal slip.
- **DATA STATE:** `DISPOSITION_REFUSED_LAMA_CAPTURED`.
- **SAFETY CONSEQUENCE:** Protects clinician against medicolegal malpractice claims under NMC regulations while ensuring patient receives oral safety-net prescriptions.
- **AUDIT EVENT:** `MEDICOLEGAL_PATIENT_REFUSAL_LOGGED`.
- **RECOVERY:** Master Case closed with explicit LAMA disposition tag and emergency return warning signs.

---

### Failure Mode 22: Consent Unavailable (Unconscious Patient with No Relative)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_INDUSTRIAL_HEALTH`.
- **USER AFFECTED:** Casualty Medical Officer.
- **CLINOVA BEHAVIOR:** System invokes the **Statutory Emergency Doctrine Mode**. Consent requirement is formally waived; UI records: `Consent Waived: Life-Threatening Emergency under Section 92 IPC / NMC Regulations 2023`. Requires two-clinician sign-off or CMO emergency override.
- **HUMAN ACTION:** Doctors execute immediate intubation, thoracostomy, or emergency surgery.
- **DATA STATE:** `EMERGENCY_CONSENT_WAIVER_ACTIVE`.
- **SAFETY CONSEQUENCE:** Eliminates delay in emergency procedures for incapacitated patients.
- **AUDIT EVENT:** `LEGAL_CONSENT_EMERGENCY_WAIVER_INVOKED`.
- **RECOVERY:** When relatives arrive or patient regains consciousness, informed post-hoc consent is formally recorded.

---

### Failure Mode 23: Network Synchronization Conflict (Concurrent Edits Offline & Online)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_PUBLIC_CAMP`.
- **USER AFFECTED:** System Administrator, Clinician.
- **CLINOVA BEHAVIOR:** Offline tablet edits Master Case vitals while central server received a phone triage update. Upon reconnection, sync engine detects timestamp collision. CLINOVA executes **Deterministic Medical Conflict Resolution**:
  1. Append-only merge: Clinical events are timestamp-ordered into the timeline.
  2. Vitals never overwrite: Both readings are preserved with specific author tags.
  3. Acuity resolution: If conflict occurs in risk score, the system defaults to the **Higher Acuity Score** (fail-safe conservative bias).
- **HUMAN ACTION:** Clinician reviews merged timeline during final review.
- **DATA STATE:** `SYNC_CONFLICT_RESOLVED_CONSERVATIVE_MERGE`.
- **SAFETY CONSEQUENCE:** Eliminates clinical data loss; guarantees that an acute vital reading is never discarded by a lower reading.
- **AUDIT EVENT:** `SYNC_ENGINE_CONFLICT_RESOLVED`.
- **RECOVERY:** Unified Master Case synchronizes across all nodes.

---

### Failure Mode 24: Patient Leaves Before Completion (Walkout / Left Without Being Seen)
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`, `ENV_PUBLIC_CAMP`.
- **USER AFFECTED:** Triage Nurse, Doctor.
- **CLINOVA BEHAVIOR:** Patient called 3 times; no response. Nurse marks case: `LEFT_WITHOUT_BEING_SEEN (LWBS)`. System inspects triage acuity:
  - If initial risk was `GREEN` (Low Acuity): Case moves to archived dropouts.
  - If initial risk was `RED / ORANGE` (High Acuity / Abnormal Vitals): System triggers **Urgent Public Health Alert**: prompts nurse to notify hospital security/ASHA or call patient's phone number immediately.
- **HUMAN ACTION:** Nurse phones patient or family to verify safety; logs result.
- **DATA STATE:** `CASE_ABANDONED_LWBS_FLAGGED`.
- **SAFETY CONSEQUENCE:** Prevents critical patients who collapse in the parking lot or restroom from being silently forgotten.
- **AUDIT EVENT:** `PATIENT_LWBS_HIGH_ACUITY_ALERT`.
- **RECOVERY:** Case marked closed or reconciled if patient returns.

---

### Failure Mode 25: Referral Not Completed (Ambulance Broke Down / Patient Diverted)
- **ENVIRONMENT:** `ENV_PHC`, `ENV_INDUSTRIAL_HEALTH`.
- **USER AFFECTED:** Referral Coordinator, Originating Medical Officer.
- **CLINOVA BEHAVIOR:** Master Case maintains status `REFERRAL_DISPATCHED (Awaiting Receiving Confirmation)`. If receiving facility does not log arrival within expected transit time $+ 60$ minutes, system generates alert: `⚠️ Referral Overdue: Patient Transfer #804 Dispatched 90m Ago — Arrival Not Confirmed`.
- **HUMAN ACTION:** Coordinator contacts 108 ambulance dispatch or patient attendant to determine transport status.
- **DATA STATE:** `REFERRAL_OVERDUE_TRACKING_ACTIVE`.
- **SAFETY CONSEQUENCE:** Detects ambulance accidents, transit deterioration, or predatory private hospital diversion.
- **AUDIT EVENT:** `REFERRAL_LONGITUDINAL_AUDIT_BREACH`.
- **RECOVERY:** Handoff confirmed or secondary ambulance dispatched.

---

### Failure Mode 26: Follow-Up Lost (Patient Never Returns for Repeat Review)
- **ENVIRONMENT:** All Environments (especially `ENV_PHC`, `ENV_CAMPUS_HEALTH`, `ENV_GOV_HOSPITAL`).
- **USER AFFECTED:** Frontline Health Worker (ASHA), Outpatient Nurse.
- **CLINOVA BEHAVIOR:** Scheduled follow-up date expires without encounter registration. System automatically transitions Master Case status to `FOLLOWUP_OVERDUE`. Generates prioritized community outreach task for the local village ASHA worker via the community task dashboard or automated SMS reminder to the patient's phone.
- **HUMAN ACTION:** ASHA conducts home visit during weekly rounds to verify patient wellness and encourage clinic revisit.
- **DATA STATE:** `OUTCOME_PENDING_COMMUNITY_ESCALATION`.
- **SAFETY CONSEQUENCE:** Prevents chronic hypertension/diabetes patients and post-discharge surgical patients from developing silent complications at home.
- **AUDIT EVENT:** `LONGITUDINAL_CARE_FOLLOWUP_OVERDUE`.
- **RECOVERY:** ASHA logs home visit outcome or patient returns for scheduled review.
