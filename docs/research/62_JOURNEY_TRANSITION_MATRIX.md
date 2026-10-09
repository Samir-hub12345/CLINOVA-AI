# CLINOVA AI — Journey Transition Matrix Specification

> **Document ID:** `RES-62`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & Formal Transition Semantics

The **Journey Transition Matrix** specifies the complete state-transition dynamics of the CLINOVA Master Case. For every valid state change, the matrix defines the triggering event, the responsible human or system actor, required data inputs, validation criteria, branching decisions, fallback/failure states, immutable audit records, user notifications, and downstream clinical impacts.

### 1.1 Transition Rule Formalism
Every transition rule $T_k$ is modeled as:
$$T_k: \langle s_{\text{curr}}, \tau, \alpha, \mathcal{I}_{\text{req}}, \mathcal{V}, \mathcal{D} \rangle \longrightarrow \langle s_{\text{next}}, s_{\text{fail}}, \mathcal{A}, \mathcal{N}, \mathcal{E} \rangle$$
Where:
- $s_{\text{curr}} \in \mathcal{S}$: Current state from the 27 canonical states.
- $\tau \in \Sigma$: Triggering event.
- $\alpha$: Allowed actor role (`ROLE_CLINICIAN`, `ROLE_NURSE`, `ROLE_HEALTH_WORKER`, `ROLE_ADMIN`, `ROLE_PATIENT`, `ROLE_SYSTEM_AI`).
- $\mathcal{I}_{\text{req}}$: Required data elements.
- $\mathcal{V}$: Validation constraints and safety predicates.
- $\mathcal{D}$: Decision / condition evaluated.
- $s_{\text{next}} \in \mathcal{S}$: Success state.
- $s_{\text{fail}} \in \mathcal{S}$: Failure / fallback state.
- $\mathcal{A}$: Audit event type written to immutable ledger.
- $\mathcal{N}$: User notification message dispatched.
- $\mathcal{E}$: Downstream clinical / system impact.

---

## 2. Exhaustive State-Transition Matrix

| # | Current State | Trigger | Actor | Required Info | Validation | Decision / Condition | Next State | Failure State | Audit Record | User Notification | Downstream Impact |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | `STATE_NEW` | `INITIATE_REGULAR_INTAKE` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Facility ID, Language | Consent verified | Normal intake path | `STATE_INTAKE_COLLECTING` | `STATE_NEW` | `ENCOUNTER_CREATED` | "Encounter initiated. Please speak or enter symptoms." | Allocates `case_id` UUIDv4. |
| **T02** | `STATE_NEW` | `TRIGGER_EMERGENCY_FAST_TRACK` | Any Human Role | Emergency flag | Implied consent | Immediate life threat | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY_ACTIVE` | `EMERGENCY_FAST_TRACK_TRIGGERED` | **"EMERGENCY FAST-TRACK ACTIVATED. ATTEND PATIENT STAT."** | Bypasses admin intake; alerts trauma team. |
| **T03** | `STATE_INTAKE_COLLECTING` | `SUBMIT_RAW_INPUTS` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Audio / Text / OCR file | File size $\le 15$MB; valid format | At least 1 modality present | `STATE_EXTRACTING` | `STATE_INTAKE_COLLECTING` | `INPUTS_SUBMITTED` | "Analyzing symptoms and documents..." | Spawns local Whisper & OCR workers. |
| **T04** | `STATE_INTAKE_COLLECTING` | `PATIENT_COLLAPSED` | Any Role | Physical collapse observation | Vital sign abnormal | Acute deterioration during entry | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY_ACTIVE` | `INTAKE_EMERGENCY_ESCALATION` | **"ACUTE DETERIORATION DETECTED. CRITICAL ALERT."** | Freezes intake; switches console to Emergency HUD. |
| **T05** | `STATE_EXTRACTING` | `EXTRACTION_FINISHED` | `ROLE_SYSTEM_AI` | Extracted entity list | Entity schema bounds | Normal extraction | `STATE_EXTRACTION_REVIEW` | `STATE_MISSING_AUDIT` | `ENTITIES_EXTRACTED` | "Extraction complete. Please review identified details." | Renders side-by-side snippet review. |
| **T06** | `STATE_EXTRACTING` | `EXTRACTION_ENGINE_ERROR` | `ROLE_SYSTEM_AI` | Error code | Model timeout $> 5$s | Extraction failure | `STATE_MISSING_AUDIT` | `STATE_STAFF_DATA_PENDING` | `EXTRACTION_FAILED` | "Automated extraction incomplete. Routing to clinical staff." | Sets extraction confidence to 0.00; flags all as unknown. |
| **T07** | `STATE_EXTRACTION_REVIEW` | `CONFIRM_EXTRACTION` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Confirmed entity list | Validated tags | Review completed | `STATE_MISSING_AUDIT` | `STATE_EXTRACTION_REVIEW` | `EXTRACTION_REVIEWED` | "Review saved. Checking completeness..." | Generates chronological timeline nodes. |
| **T08** | `STATE_EXTRACTION_REVIEW` | `EDIT_EXTRACTED_ENTITY` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Entity ID, new value | Value in range | User correction | `STATE_EXTRACTION_REVIEW` | `STATE_EXTRACTION_REVIEW` | `ENTITY_MODIFIED_AT_REVIEW` | "Detail updated." | Overwrites extracted value; sets provenance to `USER_EDITED`. |
| **T09** | `STATE_MISSING_AUDIT` | `EVALUATE_COMPLETENESS` | `ROLE_SYSTEM_AI` | Verified entity set | Completeness formula | $S < 0.85$ & self-reportable gaps exist | `STATE_FOLLOW_UP_PENDING` | `STATE_STAFF_DATA_PENDING` | `MISSING_AUDIT_EVALUATED` | "A few clarifying questions..." | Generates 1–3 Next-Best-Information prompts. |
| **T10** | `STATE_MISSING_AUDIT` | `EVALUATE_COMPLETENESS` | `ROLE_SYSTEM_AI` | Verified entity set | Completeness formula | $S \ge 0.85$ & no critical gaps | `STATE_CONSOLIDATED` | `STATE_STAFF_DATA_PENDING` | `SUFFICIENCY_PASSED` | "Information sufficient for clinical synthesis." | Direct unblocked route to Data Consolidation. |
| **T11** | `STATE_MISSING_AUDIT` | `EVALUATE_COMPLETENESS` | `ROLE_SYSTEM_AI` | Verified entity set | Critical vitals missing | Critical gap (SpO2, BP unknown) | `STATE_STAFF_DATA_PENDING` | `STATE_STAFF_DATA_PENDING` | `STAFF_INTERVENTION_REQUIRED` | "Please proceed to Nursing Triage Desk for vitals." | Case added to Nurse Worklist. |
| **T12** | `STATE_FOLLOW_UP_PENDING` | `SUBMIT_FOLLOW_UP_ANSWERS` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Answer responses | Input validation | Re-evaluate sufficiency: $S \ge 0.85$ | `STATE_CONSOLIDATED` | `STATE_STAFF_DATA_PENDING` | `FOLLOW_UP_ANSWERED` | "Thank you. Processing your health summary..." | Closes information gaps with patient responses. |
| **T13** | `STATE_FOLLOW_UP_PENDING` | `SKIP_FOLLOW_UP` / `TIMEOUT` | `ROLE_PATIENT` / `ROLE_SYSTEM_AI` | Skip event / Timeout $>120$s | Safety default | Gaps remain unclosed | `STATE_STAFF_DATA_PENDING` | `STATE_STAFF_DATA_PENDING` | `FOLLOW_UP_SKIPPED` | "Routing directly to triage staff." | Preserves missing fields as `UNKNOWN`. |
| **T14** | `STATE_STAFF_DATA_PENDING` | `RECORD_STAFF_VITALS` | `ROLE_NURSE` / `ROLE_HEALTH_WORKER` | BP, HR, SpO2, RR, Temp | Physiological range check | Vitals within non-emergency bounds | `STATE_STAFF_VERIFIED` | `STATE_STAFF_DATA_PENDING` | `STAFF_VITALS_RECORDED` | "Vitals verified and recorded." | Appends `STAFF_VERIFIED` vitals to SAME Master Case. |
| **T15** | `STATE_STAFF_DATA_PENDING` | `RED_FLAG_TRIGGERED` | `ROLE_NURSE` / `ROLE_HEALTH_WORKER` | Vital values | $\text{SpO}_2 < 85\%$ or $\text{SI} > 1.0$ | Physiological red flag tripped | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY_ACTIVE` | `VITALS_RED_FLAG_ESCALATION` | **"CRITICAL VITALS DETECTED. IMMEDIATE RESUSCITATION."** | Alerts casualty team; initiates resuscitation bundle. |
| **T16** | `STATE_STAFF_VERIFIED` | `SIGN_OFF_STAFF_DOSSIER` | `ROLE_NURSE` | Staff ID, Sign-off timestamp | RBAC check | Staff dataset validated | `STATE_CONSOLIDATED` | `STATE_STAFF_DATA_PENDING` | `STAFF_SIGN_OFF_EXECUTED` | "Nursing triage completed." | Unblocks pipeline for consolidation. |
| **T17** | `STATE_CONSOLIDATED` | `RUN_CAREGRAPH_SYNTHESIS` | `ROLE_SYSTEM_AI` | Consolidated clinical dossier | Graph consistency | Risk, trajectory, uncertainty calculated | `STATE_TRIAGE_READY` | `STATE_DOCTOR_QUEUED` | `CAREGRAPH_SYNTHESIZED` | "Clinical analysis ready for physician review." | Compiles Structured Triage Note & Report Type 1. |
| **T18** | `STATE_TRIAGE_READY` | `ENQUEUE_FOR_DOCTOR` | `ROLE_SYSTEM_AI` | Priority score vector | Queue algorithm | Normal queue placement | `STATE_DOCTOR_QUEUED` | `STATE_DOCTOR_QUEUED` | `CASE_ENQUEUED` | "Added to Doctor Queue. Priority token issued." | Dynamically positions case by clinical acuity. |
| **T19** | `STATE_DOCTOR_QUEUED` | `PATIENT_DECOMPENSATES_IN_QUEUE` | Any Role | Nurse alert / Emergency button | Clinical observation | Acute collapse in waiting area | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY_ACTIVE` | `WAITING_ROOM_DETERIORATION` | **"WAITING PATIENT COLLAPSE. CRITICAL ESCALATION."** | Pops to top of emergency board; summons crash team. |
| **T20** | `STATE_DOCTOR_QUEUED` | `OPEN_CASE_ON_WORKBENCH` | `ROLE_CLINICIAN` | Doctor ID, Terminal ID | Clinician credentials | Doctor initiates consultation | `STATE_DOCTOR_REVIEWING` | `STATE_DOCTOR_QUEUED` | `DOCTOR_REVIEW_OPENED` | "Doctor review in progress." | Locks case to active doctor terminal. |
| **T21** | `STATE_DOCTOR_REVIEWING` | `MODIFY_OR_ADD_CLINICAL_DATA` | `ROLE_CLINICIAN` | Param ID, new value, clinical note | Text not empty | Doctor physical exam / correction | `STATE_DOCTOR_REVIEWING` | `STATE_DOCTOR_REVIEWING` | `DOCTOR_VERIFIED_PARAM` | "Clinical record updated by physician." | Recalculates CAREGRAPH trajectory with doctor input. |
| **T22** | `STATE_DOCTOR_REVIEWING` | `SIGN_CLINICIAN_VERIFICATION` | `ROLE_CLINICIAN` | Diagnosis, verified signs | Mandatory diagnosis entered | Clinical verification approved | `STATE_CLINICIAN_VERIFIED` | `STATE_DOCTOR_REVIEWING` | `CLINICIAN_SIGN_OFF` | "Physician verification signed." | Freezes clinical review; advances to feasibility check. |
| **T23** | `STATE_CLINICIAN_VERIFIED` | `QUERY_FACILITY_CAPABILITY` | `ROLE_SYSTEM_AI` | Required capabilities | Capability registry query | Feasibility computed | `STATE_FACILITY_EVALUATING` | `STATE_ORCHESTRATION_PENDING`| `FACILITY_FEASIBILITY_RUN` | "Checking care feasibility..." | Computes Feasibility Index $\Phi_{\text{local}}$. |
| **T24** | `STATE_FACILITY_EVALUATING` | `GENERATE_ORCHESTRATION_GUIDANCE`| `ROLE_SYSTEM_AI` | Patient state, feasibility | Multi-graph synthesis | Safest Achievable Pathway formulated | `STATE_ORCHESTRATION_PENDING`| `STATE_ORCHESTRATION_PENDING`| `ORCHESTRATION_SUGGESTED` | "Orchestration advice available." | Displays advisory guidance to doctor. |
| **T25** | `STATE_ORCHESTRATION_PENDING`| `SELECT_ROUTINE_CARE` | `ROLE_CLINICIAN` | Rx orders, follow-up interval | No allergy conflict | Doctor confirms Routine Home Care | `STATE_ROUTINE_CARE` | `STATE_ORCHESTRATION_PENDING`| `DISPOSITION_ROUTINE_SELECTED`| "Routine home care finalized. Discharge pack printed." | Generates Report Type 3; schedules calendar. |
| **T26** | `STATE_ORCHESTRATION_PENDING`| `SELECT_FURTHER_REVIEW` | `ROLE_CLINICIAN` | Pending lab order, revisit date | Revisit $\le 7$ days | Doctor orders pending investigation | `STATE_FURTHER_REVIEW` | `STATE_ORCHESTRATION_PENDING`| `DISPOSITION_REVIEW_SELECTED` | "Further review appointment booked." | Allocates single revisit slot; sends notification. |
| **T27** | `STATE_ORCHESTRATION_PENDING`| `SELECT_WARD_ADMISSION` | `ROLE_CLINICIAN` | Target ward, admission diagnosis | Bed availability confirmed | Doctor orders inpatient admission | `STATE_WARD_REQUESTED` | `STATE_ORCHESTRATION_PENDING`| `DISPOSITION_WARD_REQUESTED` | "Inpatient admission requested. SBAR prepped." | Generates Report Type 4; alerts ward desk. |
| **T28** | `STATE_ORCHESTRATION_PENDING`| `SELECT_INTER_FACILITY_REFERRAL` | `ROLE_CLINICIAN` | Target facility, referral rationale | Transport requirement specified | Doctor orders transfer | `STATE_REFERRAL_PENDING` | `STATE_ORCHESTRATION_PENDING`| `DISPOSITION_REFERRAL_REQUESTED`| "Inter-facility referral initiated." | Generates Report Type 2; queries receiving hospital. |
| **T29** | `STATE_ORCHESTRATION_PENDING`| `SELECT_EMERGENCY_ESCALATION` | `ROLE_CLINICIAN` | Resuscitation rationale | Acute diagnosis | Doctor orders acute resuscitation | `STATE_EMERGENCY_ACTIVE` | `STATE_EMERGENCY_ACTIVE` | `DOCTOR_EMERGENCY_ESCALATION` | **"PATIENT TRANSFERRED TO RESUSCITATION BAY."** | Switches case to emergency fast-track. |
| **T30** | `STATE_ORCHESTRATION_PENDING`| `SELECT_SURGICAL_OT` | `ROLE_CLINICIAN` (Surgeon) | Surgical procedure, NPO status | Surgeon credential valid | Doctor orders emergency surgery | `STATE_OT_PENDING` | `STATE_ORCHESTRATION_PENDING`| `DISPOSITION_OT_ORDERED` | "Emergency surgery ordered. OT dossier compiling." | Compiles procedure dossier; initiates WHO checklist. |
| **T31** | `STATE_ROUTINE_CARE` | `DISPATCH_DISCHARGE_PACK` | `ROLE_CLINICIAN` / `ROLE_NURSE` | Discharge pack printed / sent | Patient acknowledgment | Discharge complete | `STATE_OUTCOME_PENDING` | `STATE_ROUTINE_CARE` | `DISCHARGE_PACK_ISSUED` | "Take-home instructions and follow-up sent." | Activates automated post-care outcome tracker. |
| **T32** | `STATE_FURTHER_REVIEW` | `REVISIT_ARRIVAL` | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | Synthetic QR scan | Same `case_id` matched | Patient arrives for scheduled revisit | `STATE_DOCTOR_QUEUED` | `STATE_FURTHER_REVIEW` | `REVISIT_CHECKIN_EXECUTED` | "Welcome back. Revisit case loaded for doctor." | Resumes SAME Master Case with pending lab results. |
| **T33** | `STATE_WARD_REQUESTED` | `ACCEPT_WARD_BED` | `ROLE_NURSE` (Ward Sister) | Assigned bed ID | Bed unoccupied | Ward confirms bed readiness | `STATE_WARD_ADMITTED` | `STATE_WARD_REQUESTED` | `WARD_BED_CONFIRMED` | "Bed allocated. Ready for patient transfer." | Unblocks physical transfer to ward. |
| **T34** | `STATE_WARD_ADMITTED` | `SIGN_SBAR_HANDOFF` | `ROLE_NURSE` & `ROLE_CLINICIAN` | Dual signatures, handoff notes | Two-party verification | Patient safely received in bed | `STATE_OUTCOME_PENDING` | `STATE_WARD_ADMITTED` | `WARD_HANDOFF_COMPLETED` | "Inpatient admission verified and complete." | Transfers custody to inpatient care team. |
| **T35** | `STATE_REFERRAL_PENDING` | `RECEIVING_FACILITY_ACCEPTS` | Receiving Doctor / Dispatcher | Confirmation ID, receiving doctor | Capability verified | Transfer authorized | `STATE_TRANSFER_IN_TRANSIT` | `STATE_REFERRAL_PENDING` | `REFERRAL_ACCEPTED` | "Receiving hospital confirmed. Transport en route." | Dispatches ambulance; transmits referral dossier. |
| **T36** | `STATE_REFERRAL_PENDING` | `RECEIVING_FACILITY_REJECTS` | Receiving Dispatcher | Rejection reason (no beds) | Telephonic / digital flag | Destination hospital saturated | `STATE_REFERRAL_PENDING` | `STATE_CLINICIAN_VERIFIED` | `REFERRAL_REJECTED` | "Destination full. FACILITYGRAPH finding next hospital."| Reroutes to next capable hospital in network. |
| **T37** | `STATE_TRANSFER_IN_TRANSIT` | `HANDOFF_AT_DESTINATION` | Transport Paramedic & Receiving Staff | Destination intake sign-off | Patient physically received | Transfer completed | `STATE_OUTCOME_PENDING` | `STATE_TRANSFER_IN_TRANSIT` | `TRANSFER_COMPLETED` | "Patient safely received at destination hospital." | Closes local transfer leg; tracks destination care. |
| **T38** | `STATE_EMERGENCY_ACTIVE` | `STABILIZATION_ACHIEVED` | `ROLE_CLINICIAN` | Stabilized vitals ($\text{SI} < 1.0$) | Physician clinical sign-off | Patient successfully resuscitated | `STATE_WARD_REQUESTED` | `STATE_EMERGENCY_ACTIVE` | `RESUSCITATION_STABILIZED` | "Patient stabilized. Transferring to ICU/HDU." | Advances to inpatient admission or surgery. |
| **T39** | `STATE_OT_PENDING` | `COMPLETE_WHO_SIGN_IN` | Operating Surgeon & Anesthesiologist| WHO checklist, surgical site | Dual clinician sign-off | Patient cleared for theatre | `STATE_OT_HANDOFF` | `STATE_OT_PENDING` | `WHO_SIGN_IN_VERIFIED` | "Surgical sign-in complete. Patient entering OT." | Generates Report Type 6; scrub team takes over. |
| **T40** | `STATE_OT_HANDOFF` | `COMPLETE_SURGERY` | Operating Surgeon | Operative note, post-op vitals | Surgeon sign-off | Procedure successfully concluded | `STATE_OUTCOME_PENDING` | `STATE_OT_HANDOFF` | `SURGERY_COMPLETED` | "Procedure finished. Patient moving to recovery." | Transfers to post-anesthesia recovery unit. |
| **T41** | `STATE_OUTCOME_PENDING` | `RECORD_CLINICAL_ENDPOINT` | `ROLE_CLINICIAN` / `ROLE_NURSE` | Outcome category, clinical notes | Authorized health role | Clinical outcome known | `STATE_RESOLVED` | `STATE_OUTCOME_PENDING` | `CLINICAL_OUTCOME_LOGGED` | "Outcome recorded. Case resolved." | Updates CAREGRAPH longitudinal delta. |
| **T42** | `STATE_RESOLVED` | `SEAL_AND_ARCHIVE_CASE` | `ROLE_SYSTEM_AI` | Final Merkle root, audit ledger | Complete audit trail validated | Encounter finalized | `STATE_CLOSED` | `STATE_RESOLVED` | `CASE_ARCHIVED_AND_SEALED` | "Case sealed and archived." | Terminal state; exports telemetry to SIGNALGRAPH. |

---

## 3. Exception & Rollback Transition Rules

The state machine strictly models abnormal paths, synchronization collisions, and permission denials:

1. **Permission Denial Transition:**  
   If an unauthorized actor attempts a gated transition (e.g., `ROLE_NURSE` attempting `SELECT_ROUTINE_CARE` discharge or `ROLE_ADMIN` attempting clinical data modification):
   $$\langle s_{\text{curr}}, \tau_{\text{unauth}}, \alpha_{\text{unauth}} \rangle \longrightarrow \langle s_{\text{curr}}, \text{AUDIT\_PERMISSION\_VIOLATION}, \text{ALERT\_DENIED} \rangle$$
   The state remains unchanged; a security violation is logged to the tamper-evident audit ledger.

2. **Concurrent Modification Collision:**  
   If two workstations attempt simultaneous state updates on the same `case_id`:
   - Enforces optimistic concurrency control using version vector timestamping ($\text{version}_{\text{case}}$).
   - The second transaction is rejected with `STATE_CONFLICT_RETRY`.
   - The user interface reloads the latest state without data corruption.

3. **Break-Glass Emergency Jump:**  
   From ANY state $s \in \mathcal{S} \setminus \{\text{STATE\_CLOSED}\}$:
   - Any authenticated health worker can invoke `TRIGGER_EMERGENCY_FAST_TRACK`.
   - Current execution freezes; state transitions immediately to `STATE_EMERGENCY_ACTIVE`.
   - Audit event `BREAK_GLASS_EMERGENCY_TRANSITION` records actor ID, previous state, and timestamp.
