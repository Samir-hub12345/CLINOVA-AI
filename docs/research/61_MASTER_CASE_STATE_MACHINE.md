# CLINOVA AI — Master Case State Machine Specification

> **Document ID:** `RES-61`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. State Machine Architectural Foundations

The **Master Case State Machine** provides a formal, deterministic mathematical model governing the entire lifecycle of a patient encounter in CLINOVA AI.

### 1.1 Mathematical Definition
The Master Case lifecycle is defined as a 6-tuple Finite State Machine:
$$\mathcal{M} = \langle \mathcal{S}, \Sigma, \delta, s_0, \mathcal{F}, \mathcal{G} \rangle$$
Where:
- $\mathcal{S}$ is the finite set of **27 Canonical States**.
- $\Sigma$ is the set of valid **Transition Triggers** (human actions, sensor arrivals, system events, timeouts).
- $\delta: \mathcal{S} \times \Sigma \times \mathcal{G} \longrightarrow \mathcal{S}$ is the state transition function.
- $s_0 = \text{STATE\_NEW}$ is the unique initial state.
- $\mathcal{F} = \{\text{STATE\_CLOSED}\}$ is the terminal absorption state.
- $\mathcal{G}$ is the set of **Safety Guardrails & Permission Predicates** (RBAC constraints, clinical safety gates, sufficiency thresholds).

---

## 2. State Taxonomy & Candidate Rationalization Evaluation

The candidate state list was rigorously evaluated against clinical workflows, resulting in the following rationalization:

| Candidate State | Verdict | Canonical Identifier | Clinical Rationale & Boundary |
| :--- | :--- | :--- | :--- |
| `NEW` | **KEEP** | `STATE_NEW` | Initial encounter instantiation and demographic consent recording. |
| `INTAKE` | **KEEP** | `STATE_INTAKE_COLLECTING` | Active collection of raw vernacular speech, free text, and image files. |
| `EXTRACTING` | **KEEP** | `STATE_EXTRACTING` | Local asynchronous Whisper/OCR entity parsing. |
| `REVIEW_PENDING` | **RENAME** | `STATE_EXTRACTION_REVIEW` | Visual inspection of extracted entities side-by-side with raw crops. |
| `MISSING_INFORMATION`| **RENAME** | `STATE_MISSING_AUDIT` | Algorithmic audit identifying Known, Unknown, Conflicting, Unreliable fields. |
| `FOLLOW_UP_PENDING` | **KEEP** | `STATE_FOLLOW_UP_PENDING` | Patient/caregiver presented with 1–3 targeted NBI follow-up questions. |
| `STAFF_DATA_PENDING` | **KEEP** | `STATE_STAFF_DATA_PENDING` | Triage nurse worklist for missing point-of-care vitals and red-flag checks. |
| `VERIFICATION_PENDING`| **MERGE** | `STATE_STAFF_VERIFIED` | Merged into explicit staff sign-off state validating point-of-care data. |
| `CONSOLIDATED` | **KEEP** | `STATE_CONSOLIDATED` | Aggregation of patient inputs, staff vitals, and verified timeline. |
| `TRIAGE_READY` | **KEEP** | `STATE_TRIAGE_READY` | CAREGRAPH synthesis complete; risk, trajectory, and uncertainty calculated. |
| `DOCTOR_QUEUE` | **KEEP** | `STATE_DOCTOR_QUEUED` | Case positioned in multi-factor prioritized clinician queue. |
| `DOCTOR_REVIEW` | **KEEP** | `STATE_DOCTOR_REVIEWING` | Registered Medical Practitioner actively reviewing dossier on workbench. |
| `CLINICIAN_VERIFIED`| **KEEP** | `STATE_CLINICIAN_VERIFIED` | Clinician executes VERIFY / MODIFY / ADD on clinical findings. |
| `FACILITY_EVALUATION`| **KEEP** | `STATE_FACILITY_EVALUATING` | FACILITYGRAPH computes local capability and referral care feasibility. |
| `ORCHESTRATION_PENDING`| **KEEP** | `STATE_ORCHESTRATION_PENDING` | Advisory care pathway synthesized; awaiting clinician decision. |
| `ROUTINE_CARE` | **KEEP** | `STATE_ROUTINE_CARE` | Pathway A: Discharge pack, prescription, recurring follow-up calendar. |
| `FOLLOW_UP` | **SPLIT** | `STATE_FURTHER_REVIEW` | Pathway B: Single revisit slot for pending investigations/reassessment. |
| `WARD_REQUEST` | **KEEP** | `STATE_WARD_REQUESTED` | Pathway C: Inpatient bed request issued; SBAR handoff dossier prepped. |
| `ADMISSION` | **KEEP** | `STATE_WARD_ADMITTED` | Inpatient bed confirmed; two-party handoff signed; patient in ward. |
| `REFERRAL_PENDING` | **KEEP** | `STATE_REFERRAL_PENDING` | Pathway D: Destination hospital selected; referral pack transmitted. |
| `TRANSFER` | **KEEP** | `STATE_TRANSFER_IN_TRANSIT`| Ambulance / transport dispatched; patient physically in transit. |
| `EMERGENCY` | **KEEP** | `STATE_EMERGENCY_ACTIVE` | Pathway E: High-acuity resuscitation, 30s ABCD vitals, red-flag bundle. |
| `OT_PENDING` | **KEEP** | `STATE_OT_PENDING` | Pathway F: Procedure required; surgical dossier compiled; WHO checklist. |
| `OT_HANDOFF` | **KEEP** | `STATE_OT_HANDOFF` | Theatre transfer; anesthesia/scrub sign-in executed. |
| `OUTCOME_PENDING` | **KEEP** | `STATE_OUTCOME_PENDING` | Post-disposition clinical continuation; tracking real-world progress. |
| `RESOLVED` | **KEEP** | `STATE_RESOLVED` | Definitive clinical outcome recorded; CAREGRAPH delta finalized. |
| `CLOSED` | **KEEP** | `STATE_CLOSED` | Cryptographic seal applied; SIGNALGRAPH telemetry emitted; archived. |

---

## 3. Comprehensive Specification of All 27 Canonical States

---

### S01: `STATE_NEW`
- **Entry Condition:** Patient arrives at physical facility or opens intake console.
- **Exit Condition:** Demographic basics recorded and consent confirmed (or emergency triggered).
- **Allowed Actors:** `ROLE_PATIENT`, `ROLE_HEALTH_WORKER`, `ROLE_ADMIN`, `ROLE_NURSE`, `ROLE_CLINICIAN`.
- **Required Data:** `facility_id`, `encounter_timestamp`.
- **Optional Data:** `synthetic_patient_id`, `preferred_language`.
- **Safety Gate:** DPDP Consent Gate (Must record explicit consent or emergency implied waiver).
- **Audit Event:** `CASE_INITIALIZED` (Logs IP, actor ID, timestamp, consent type).
- **Failure Behavior:** If user aborts, record discarded from memory; no persistence.
- **Re-entry Behavior:** Never re-entered; initial state only.
- **Downstream Consequence:** Generates immutable `case_id` UUIDv4.

---

### S02: `STATE_INTAKE_COLLECTING`
- **Entry Condition:** Consent verified; regular intake session started.
- **Exit Condition:** Patient/operator clicks "Submit Details" or uploads last document.
- **Allowed Actors:** `ROLE_PATIENT`, `ROLE_HEALTH_WORKER`, `ROLE_NURSE`.
- **Required Data:** At least one input modality (Voice recording, typed narrative, or document file).
- **Optional Data:** Prior prescription slips, lab PDFs, chief complaint tag.
- **Safety Gate:** Antivirus validation; payload size limit ($\le 15\text{MB}$ per file).
- **Audit Event:** `INTAKE_PAYLOAD_ATTACHED` (Records file hash, mime type, byte size).
- **Failure Behavior:** If network disconnects, files cached in IndexedDB/Local storage.
- **Re-entry Behavior:** Allowed if patient returns to add more documents before triage freeze.
- **Downstream Consequence:** Triggers local asynchronous OCR and Whisper transcription workers.

---

### S03: `STATE_EXTRACTING`
- **Entry Condition:** Raw inputs submitted to extraction worker queue.
- **Exit Condition:** OCR text extracted and speech transcribed into normalized entity schema.
- **Allowed Actors:** `ROLE_SYSTEM_AI` (Background worker).
- **Required Data:** Raw audio or document image file pointers.
- **Optional Data:** Historical profile dictionary.
- **Safety Gate:** Sub-3-second timeout for local quantized SLM models; deterministic fallback on OCR.
- **Audit Event:** `EXTRACTION_COMPLETED` (Records engine version, extraction duration, entity count).
- **Failure Behavior:** If OCR fails or speech garbled, entities flagged as `UNRELIABLE` or `UNKNOWN`.
- **Re-entry Behavior:** Triggered when additional files are uploaded in later stages.
- **Downstream Consequence:** Generates raw candidate entity list with confidence scores.

---

### S04: `STATE_EXTRACTION_REVIEW`
- **Entry Condition:** Entity extraction complete.
- **Exit Condition:** Reviewer confirms, edits, or approves entity list.
- **Allowed Actors:** `ROLE_PATIENT`, `ROLE_HEALTH_WORKER`, `ROLE_NURSE`.
- **Required Data:** Extracted entity objects paired with source crop coordinates.
- **Optional Data:** User textual edits.
- **Safety Gate:** Visual transparency gate: Entities cannot be hidden without manual rejection tag.
- **Audit Event:** `EXTRACTION_REVIEW_CONFIRMED` (Records human edits and confidence overrides).
- **Failure Behavior:** If skipped by user, entities advance with `UNVERIFIED` provenance tag.
- **Re-entry Behavior:** Allowed during clinical review.
- **Downstream Consequence:** Feeds normalized entity objects to timeline generator.

---

### S05: `STATE_MISSING_AUDIT`
- **Entry Condition:** Extraction review completed.
- **Exit Condition:** Completeness evaluation finishes; Known/Unknown/Conflicting vector computed.
- **Allowed Actors:** `ROLE_SYSTEM_AI` (Deterministic Rule Engine).
- **Required Data:** Extracted clinical entity set.
- **Optional Data:** Previous facility records.
- **Safety Gate:** Zero Imputation Law: Missing parameters are permanently stored as `UNKNOWN`.
- **Audit Event:** `MISSING_AUDIT_EVALUATED` (Logs count of critical, important, and optional gaps).
- **Failure Behavior:** System error forces case directly to `STATE_STAFF_DATA_PENDING`.
- **Re-entry Behavior:** Re-evaluated whenever new vitals or history are attached.
- **Downstream Consequence:** Triggers Next-Best-Information (NBI) candidate question ranking.

---

### S06: `STATE_FOLLOW_UP_PENDING`
- **Entry Condition:** Missing audit identifies critical/important gaps suitable for patient self-report.
- **Exit Condition:** Patient answers 1–3 targeted questions or clicks "Skip / Proceed to Nurse".
- **Allowed Actors:** `ROLE_PATIENT`, `ROLE_HEALTH_WORKER`.
- **Required Data:** Rendered NBI questions in preferred language.
- **Optional Data:** Patient responses.
- **Safety Gate:** Question limit: Hard cap at 3 questions to prevent cognitive abandonment.
- **Audit Event:** `FOLLOW_UP_PROCESSED` (Logs presented prompts and captured patient choices).
- **Failure Behavior:** Inactivity timeout (120 seconds) automatically advances case to Staff Queue.
- **Re-entry Behavior:** Maximum 1 follow-up cycle per encounter.
- **Downstream Consequence:** Inputs feed Sufficiency Gate calculus ($S \ge 0.85$).

---

### S07: `STATE_STAFF_DATA_PENDING`
- **Entry Condition:** Sufficiency score $S < 0.85$ OR critical vital sign is `UNKNOWN`.
- **Exit Condition:** Frontline nurse/worker measures vitals and completes missing-data checklist.
- **Allowed Actors:** `ROLE_NURSE`, `ROLE_HEALTH_WORKER`.
- **Required Data:** Measured physical vitals (BP, SpO2, Pulse, Temp, RR) and red-flag sign checklist.
- **Optional Data:** Bedside point-of-care capillary blood glucose, rapid malaria strip test.
- **Safety Gate:** Dynamic Red-Flag Gate: If $\text{SpO}_2 < 85\%$ or $\text{Shock Index} > 1.0$, instant escalation to `STATE_EMERGENCY_ACTIVE`.
- **Audit Event:** `STAFF_MEASUREMENTS_RECORDED` (Logs staff actor ID, physical instrument readings).
- **Failure Behavior:** Case remains highlighted on nurse worklist; alerts after 15 minutes of inactivity.
- **Re-entry Behavior:** Re-entered if doctor requests repeated vitals during observation.
- **Downstream Consequence:** Appends `STAFF_VERIFIED` vitals directly to the SAME Master Case.

---

### S08: `STATE_STAFF_VERIFIED`
- **Entry Condition:** Nurse submits completed vitals checklist.
- **Exit Condition:** System validates physiological bounds and signs off staff dataset.
- **Allowed Actors:** `ROLE_NURSE`, `ROLE_HEALTH_WORKER`.
- **Required Data:** Staff actor ID, timestamp, verified vitals vector.
- **Optional Data:** Nursing clinical observations note.
- **Safety Gate:** Physiological bounds check (e.g., rejecting Systolic BP = 400 mmHg as input typo).
- **Audit Event:** `STAFF_WORKFLOW_SIGNED` (Cryptographic hash of staff dataset).
- **Failure Behavior:** Flagged invalid input prompts immediate re-entry screen to staff.
- **Re-entry Behavior:** Never directly re-entered; transient verification milestone.
- **Downstream Consequence:** Unblocks pipeline to proceed to Data Consolidation.

---

### S09: `STATE_CONSOLIDATED`
- **Entry Condition:** Case meets sufficiency threshold OR staff verification is signed off.
- **Exit Condition:** All patient, OCR, and nursing data merged into Master Clinical Dossier.
- **Allowed Actors:** `ROLE_SYSTEM_AI`.
- **Required Data:** Master Case schema components 1 through 8 (Inputs, extractions, vitals, timeline).
- **Optional Data:** Historical trend delta.
- **Safety Gate:** Data Integrity Invariant: All elements must reference valid `case_id`.
- **Audit Event:** `DOSSIER_CONSOLIDATED` (Records consolidated entity manifest).
- **Failure Behavior:** Corrupted record triggers automatic rollback to previous state with alert.
- **Re-entry Behavior:** Triggered whenever new clinical data is appended to Master Case.
- **Downstream Consequence:** Triggers CAREGRAPH synthesis and physiological risk computation.

---

### S10: `STATE_TRIAGE_READY`
- **Entry Condition:** CAREGRAPH calculation finishes successfully.
- **Exit Condition:** Structured Triage Note and Master Clinical Report compiled.
- **Allowed Actors:** `ROLE_SYSTEM_AI`.
- **Required Data:** CAREGRAPH state node, Risk Band, Trajectory, Uncertainty Score ($U_t$).
- **Optional Data:** Differential diagnostic hypotheses.
- **Safety Gate:** Advisory Watermark Gate: All generated text must carry mandatory AI advisory labels.
- **Audit Event:** `TRIAGE_NOTE_GENERATED` (Records generated note hash and risk category).
- **Failure Behavior:** Engine failure defaults risk band to `HIGH_UNCERTAINTY` and notifies clinician.
- **Re-entry Behavior:** Re-calculated if vitals or physical exam findings change.
- **Downstream Consequence:** Moves case immediately into prioritized doctor queue.

---

### S11: `STATE_DOCTOR_QUEUED`
- **Entry Condition:** Master Clinical Report ready.
- **Exit Condition:** Clinician opens case on Doctor Review Workbench.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Composite Priority Vector ($\mathbf{Priority}$).
- **Optional Data:** Department allocation tag.
- **Safety Gate:** Deterioration Alert Gate: Time-decay function elevates queue priority as wait time exceeds clinical safety thresholds.
- **Audit Event:** `CASE_QUEUED` (Records queue position, calculated priority score, entry timestamp).
- **Failure Behavior:** If patient leaves facility before review, marked `PATIENT_WALKOUT`.
- **Re-entry Behavior:** Re-entered if doctor temporarily parks case to review emergent arrival.
- **Downstream Consequence:** Surfaces case on active clinician outpatient console.

---

### S12: `STATE_DOCTOR_REVIEWING`
- **Entry Condition:** Clinician clicks and opens case dossier.
- **Exit Condition:** Clinician completes clinical review and verification.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Clinician session token, active terminal ID.
- **Optional Data:** Audio recording of doctor-patient encounter.
- **Safety Gate:** Session exclusivity lock: Only one clinician can review a case at a time.
- **Audit Event:** `DOCTOR_REVIEW_STARTED` (Logs doctor ID, terminal IP, timestamp).
- **Failure Behavior:** If browser crashes, lock auto-releases after 180 seconds.
- **Re-entry Behavior:** Standard workflow if clinician pauses to await bedside test.
- **Downstream Consequence:** Enables Doctor Action Gate (`VERIFY`, `MODIFY`, `ADD`).

---

### S13: `STATE_CLINICIAN_VERIFIED`
- **Entry Condition:** Clinician completes physical exam and verifies/modifies parameters.
- **Exit Condition:** Clinician signs off verified clinical state.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Verified diagnoses, physical exam notes, clinician ID.
- **Optional Data:** Prescriptions, investigation orders.
- **Safety Gate:** Human Responsibility Gate: Requires active click confirming clinical review.
- **Audit Event:** `CLINICAL_VERIFICATION_SIGNED` (Cryptographic signature of attending doctor).
- **Failure Behavior:** Unsaved edits preserved in local draft buffer.
- **Re-entry Behavior:** Allowed if patient condition evolves during consultation.
- **Downstream Consequence:** Triggers FACILITYGRAPH care feasibility check.

---

### S14: `STATE_FACILITY_EVALUATING`
- **Entry Condition:** Clinician verification signed.
- **Exit Condition:** Local capability and referral feasibility calculated.
- **Allowed Actors:** `ROLE_SYSTEM_AI`.
- **Required Data:** Required clinical capabilities vector vs local facility capability matrix.
- **Optional Data:** Regional hospital bed registry data.
- **Safety Gate:** Stale Data Warning: If receiving hospital data $> 12\text{h}$ old, flags telephonic verification mandate.
- **Audit Event:** `FACILITY_FEASIBILITY_EVALUATED` (Logs Feasibility Index $\Phi_{\text{local}}$).
- **Failure Behavior:** Capability registry offline $\longrightarrow$ System displays static capability profile with warning.
- **Re-entry Behavior:** Re-run if required investigations change.
- **Downstream Consequence:** Feeds Orchestration Engine with resource constraints.

---

### S15: `STATE_ORCHESTRATION_PENDING`
- **Entry Condition:** Feasibility calculated; Orchestration generates recommendation.
- **Exit Condition:** Clinician selects and confirms final disposition.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Orchestration recommendation (`SUGGEST_ROUTINE`, `SUGGEST_WARD`, etc.).
- **Optional Data:** Alternative pathway rationale.
- **Safety Gate:** Meaningful Human Control Gate: System CANNOT auto-select disposition.
- **Audit Event:** `ORCHESTRATION_RECOMMENDATION_SURFACED` (Logs system advice and confidence).
- **Failure Behavior:** System failure leaves standard disposition dropdown active for doctor.
- **Re-entry Behavior:** Re-entered if initial disposition cannot be fulfilled (e.g., ward bed full).
- **Downstream Consequence:** Routes Master Case into one of the 6 disposition branches.

---

### S16: `STATE_ROUTINE_CARE` (Pathway A)
- **Entry Condition:** Clinician selects Routine / Home Care disposition.
- **Exit Condition:** Discharge pack generated and recurring follow-up calendar booked.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Outpatient discharge instructions, prescribed medications, follow-up interval.
- **Optional Data:** Dietary instructions, exercise advice.
- **Safety Gate:** Medication Allergy Conflict Gate: Checks prescribed drugs against known allergies.
- **Audit Event:** `ROUTINE_CARE_DISCHARGED` (Logs prescription hash, scheduled return interval).
- **Failure Behavior:** Failed calendar sync logs local appointment; prints physical paper slip.
- **Re-entry Behavior:** Allowed if patient returns with acute symptoms before discharge.
- **Downstream Consequence:** Advances case to `STATE_OUTCOME_PENDING`.

---

### S17: `STATE_FURTHER_REVIEW` (Pathway B)
- **Entry Condition:** Clinician selects Further Review / Pending Lab Reassessment.
- **Exit Condition:** Single revisit slot booked; targeted patient notification dispatched.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Ordered pending investigations, revisit target time (e.g., 24h / 48h).
- **Optional Data:** Interim home precautions.
- **Safety Gate:** Max revisit window: Hard cap at 7 days; beyond 7 days requires formal discharge/routine flow.
- **Audit Event:** `FURTHER_REVIEW_SCHEDULED` (Logs ordered lab tests and return slot).
- **Failure Behavior:** Notification gateway failure flags clinic desk to issue physical reminder slip.
- **Re-entry Behavior:** Re-entered when patient physically presents for revisit.
- **Downstream Consequence:** Advances case to `STATE_OUTCOME_PENDING`.

---

### S18: `STATE_WARD_REQUESTED` (Pathway C)
- **Entry Condition:** Clinician orders Inpatient Ward Admission.
- **Exit Condition:** Target ward confirmed and admission dossier transmitted.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Target ward service (Medicine, Surgery, Peds), urgency tier, admission diagnosis.
- **Optional Data:** Bed preference, isolation requirement.
- **Safety Gate:** Bed Availability Gate: Inpatient bed must be physically allocated.
- **Audit Event:** `WARD_ADMISSION_REQUESTED` (Logs requesting doctor, target ward ID, priority).
- **Failure Behavior:** Ward full $\longrightarrow$ Alerts clinician; prompts alternative ward or referral.
- **Re-entry Behavior:** Re-entered if ward transfer is requested.
- **Downstream Consequence:** Notifies ward nursing station worklist.

---

### S19: `STATE_WARD_ADMITTED` (Pathway C)
- **Entry Condition:** Ward nurse accepts patient and verifies bed assignment.
- **Exit Condition:** Two-party SBAR handoff checklist signed; patient in bed.
- **Allowed Actors:** `ROLE_NURSE`, `ROLE_CLINICIAN`.
- **Required Data:** Assigned Bed ID, Ward Sister ID, incoming vitals verification.
- **Optional Data:** Inpatient nursing care plan.
- **Safety Gate:** Two-Party Sign-Off Gate: Both transferring and receiving staff must sign.
- **Audit Event:** `WARD_ADMISSION_CONFIRMED` (Records bed allocation, dual sign-off).
- **Failure Behavior:** Patient deteriorates en route $\longrightarrow$ Instant divert to `STATE_EMERGENCY_ACTIVE`.
- **Re-entry Behavior:** Re-entered if transferred to step-down or secondary ward.
- **Downstream Consequence:** Advances case to `STATE_OUTCOME_PENDING`.

---

### S20: `STATE_REFERRAL_PENDING` (Pathway D)
- **Entry Condition:** Clinician orders Inter-Facility Referral.
- **Exit Condition:** Receiving hospital confirmed and transport dispatched.
- **Allowed Actors:** `ROLE_CLINICIAN`.
- **Required Data:** Destination facility ID, clinical referral reason, transport urgency.
- **Optional Data:** Escorting paramedic name, oxygen requirement.
- **Safety Gate:** Supreme Court Emergency Law Gate: Critical transfer requires receiving confirmation or designated trauma center dispatch.
- **Audit Event:** `REFERRAL_DISPATCH_INITIATED` (Logs destination hospital, referral pack hash).
- **Failure Behavior:** Destination rejects $\longrightarrow$ FACILITYGRAPH reroutes to next capable center.
- **Re-entry Behavior:** Allowed if multiple facilities must be queried.
- **Downstream Consequence:** Advances case to `STATE_TRANSFER_IN_TRANSIT`.

---

### S21: `STATE_TRANSFER_IN_TRANSIT` (Pathway D)
- **Entry Condition:** Patient loaded into ambulance / transport.
- **Exit Condition:** Arrival and physical intake at receiving hospital.
- **Allowed Actors:** `ROLE_NURSE`, `ROLE_HEALTH_WORKER`, `ROLE_CLINICIAN`.
- **Required Data:** Departure timestamp, vehicle ID, en-route monitoring logs.
- **Optional Data:** En-route GPS coordinates, serial vitals.
- **Safety Gate:** En-Route Deterioration Protocol: Ambulance staff can update emergency vitals.
- **Audit Event:** `TRANSFER_IN_TRANSIT_LOGGED` (Logs departure time, en-route handoff).
- **Failure Behavior:** Ambulance breakdown $\longrightarrow$ SOS alert; backup vehicle dispatched.
- **Re-entry Behavior:** Never re-entered; unidirectional transfer stage.
- **Downstream Consequence:** Advances case to `STATE_OUTCOME_PENDING`.

---

### S22: `STATE_EMERGENCY_ACTIVE` (Pathway E)
- **Entry Condition:** Emergency Fast-Track presentation OR mid-encounter red-flag escalation.
- **Exit Condition:** Acute resuscitation completed; emergency disposition signed.
- **Allowed Actors:** `ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_HEALTH_WORKER`.
- **Required Data:** 30-second ABCD vitals, emergency priority token (`EMG-XXXX`).
- **Optional Data:** Bedside point-of-care blood glucose, 12-lead ECG strip.
- **Safety Gate:** Resuscitation Monopoly Gate: All administrative tasks locked; emergency HUD active.
- **Audit Event:** `EMERGENCY_ESCALATION_TRIGGERED` (Logs trigger reason, actor, timestamp).
- **Failure Behavior:** Loss of connectivity $\longrightarrow$ System runs 100% offline on local LAN emergency cache.
- **Re-entry Behavior:** Can be re-entered from ANY state in the platform upon collapse.
- **Downstream Consequence:** Branches to Emergency ICU, Emergency OT, or Critical Transfer.

---

### S23: `STATE_OT_PENDING` (Pathway F)
- **Entry Condition:** Clinician orders emergent/urgent surgical procedure.
- **Exit Condition:** Surgical dossier prepped and WHO Surgical Checklist initiated.
- **Allowed Actors:** `ROLE_CLINICIAN` (Surgeon / Anesthesiologist).
- **Required Data:** Surgical indication, NPO status, blood cross-match, consent form.
- **Optional Data:** Pre-op chest X-ray, coagulation profile.
- **Safety Gate:** Surgeon Authorization Gate: System cannot book OT without credentialed surgeon ID.
- **Audit Event:** `OT_PROCEDURE_REQUESTED` (Logs procedure code, operating surgeon).
- **Failure Behavior:** Missing cross-match $\longrightarrow$ Flags critical alert to blood bank.
- **Re-entry Behavior:** Allowed if surgery postponed due to stabilization needs.
- **Downstream Consequence:** Advances case to `STATE_OT_HANDOFF`.

---

### S24: `STATE_OT_HANDOFF` (Pathway F)
- **Entry Condition:** Patient transferred to Operation Theatre holding bay.
- **Exit Condition:** WHO Surgical Safety Checklist "Sign In" completed; transfer to scrub team.
- **Allowed Actors:** `ROLE_CLINICIAN`, `ROLE_NURSE`.
- **Required Data:** Signed anesthesia assessment, surgical site confirmation, allergy check.
- **Optional Data:** Antibiotic prophylaxis timestamp.
- **Safety Gate:** WHO Surgical "Time Out" verification prior to incision.
- **Audit Event:** `OT_HANDOFF_VERIFIED` (Dual sign-off of anesthesiologist and scrub nurse).
- **Failure Behavior:** Patient instability en route $\longrightarrow$ Resuscitation pause in theatre.
- **Re-entry Behavior:** Never re-entered; procedure phase.
- **Downstream Consequence:** Advances case to `STATE_OUTCOME_PENDING`.

---

### S25: `STATE_OUTCOME_PENDING`
- **Entry Condition:** Post-disposition care active (home, ward, transfer, or post-op).
- **Exit Condition:** Clinical endpoint recorded or follow-up window expires.
- **Allowed Actors:** `ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_HEALTH_WORKER`, `ROLE_SYSTEM_AI`.
- **Required Data:** Expected outcome milestone date.
- **Optional Data:** Interim patient check-in responses, ward progress notes.
- **Safety Gate:** Timeout Gate: If no outcome recorded after 14 days, case flags for community worker review.
- **Audit Event:** `CONTINUATION_MONITORED` (Logs monitoring status).
- **Failure Behavior:** Lost to follow-up $\longrightarrow$ Marked `LOST_TO_FOLLOWUP` after protocol grace period.
- **Re-entry Behavior:** Remains active until definitive outcome resolution.
- **Downstream Consequence:** Transitions to `STATE_RESOLVED`.

---

### S26: `STATE_RESOLVED`
- **Entry Condition:** Healthcare professional logs definitive clinical outcome.
- **Exit Condition:** CAREGRAPH longitudinal delta calculated; outcome audited.
- **Allowed Actors:** `ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_HEALTH_WORKER`.
- **Required Data:** Outcome Category (`FULL_RECOVERY`, `STABILIZED`, `COMPLICATION_MANAGED`, `REFERRED_HIGHER`, `CRITICAL_TRANSFER`, `ADVERSE_EVENT`).
- **Optional Data:** Clinical outcome notes, discharge summary.
- **Safety Gate:** Adverse Event Flag: `ADVERSE_EVENT` triggers mandatory root-cause quality audit.
- **Audit Event:** `OUTCOME_RECORDED` (Logs outcome category, actor ID, diagnostic concordance).
- **Failure Behavior:** Network failure stores outcome in local append-log until sync.
- **Re-entry Behavior:** Never re-entered; terminal clinical resolution state.
- **Downstream Consequence:** Transitions to terminal state `STATE_CLOSED`.

---

### S27: `STATE_CLOSED`
- **Entry Condition:** Master Case sealed; all clinical and administrative actions complete.
- **Exit Condition:** None (Terminal Absorption State).
- **Allowed Actors:** `ROLE_SYSTEM_AI` (Automated governance).
- **Required Data:** Cryptographic SHA-256 seal of all audit events.
- **Optional Data:** Anonymized epidemiological telemetry.
- **Safety Gate:** Read-Only Immutability Gate: Record permanently locked; zero edits permitted.
- **Audit Event:** `CASE_CLOSED_AND_SEALED` (Stores final Merkle root and archival timestamp).
- **Failure Behavior:** System crash during seal $\longrightarrow$ Sealed on next node reboot.
- **Re-entry Behavior:** Impossible. New presentations spawn a new encounter linked to the patient ID.
- **Downstream Consequence:** Exports anonymized telemetry to $\text{SIGNALGRAPH}$ macro network.
