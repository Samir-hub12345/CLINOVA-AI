# CLINOVA AI — Master Case User Journey Across Lifecycle Stages

> **Document ID:** `RES-32`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Healthcare Human Factors Research Group  

---

## 1. Executive Summary

This document traces the complete, end-to-end user involvement across the **21 continuous lifecycle stages** of the single **Master Case**.

Unlike fragmented legacy EHRs where different staff members open disconnected forms and duplicate records, CLINOVA AI operates on a single unified state engine:
$$\mathbf{CaseModel}(t) \to \mathbf{CAREGRAPH}(t) \to \mathbf{FACILITYGRAPH}(t) \to \mathbf{SIGNALGRAPH}(t)$$

Every primary actor (`Clinician`, `Nurse/Health Worker`, `Referral Staff`, `Patient/Caregiver`) interacts with the identical Master Case, bounded by strict permission boundaries, explicit handoffs, and Meaningful Human Control.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      21-STAGE MASTER CASE LIFECYCLE FLOW                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  STAGE 01: NEW ENCOUNTER                STAGE 12: DOCTOR QUEUE              │
│  STAGE 02: PATHWAY SELECTION            STAGE 13: DOCTOR REVIEW             │
│  STAGE 03: INFORMATION COLLECTION       STAGE 14: VERIFY / MODIFY / ADD     │
│  STAGE 04: EXTRACTION & STRUCTURING     STAGE 15: FACILITYGRAPH EVALUATION  │
│  STAGE 05: TIMELINE SUMMARIZATION       STAGE 16: ORCHESTRATION GUIDANCE    │
│  STAGE 06: MISSING INFORMATION AUDIT    STAGE 17: CARE PATHWAY SELECTION    │
│  STAGE 07: FOLLOW-UP QUESTION ENGINE    STAGE 18: DISPOSITION EXECUTION     │
│  STAGE 08: DATA CONSOLIDATION           STAGE 19: OUTCOME RECORDING         │
│  STAGE 09: CAREGRAPH INITIALIZATION     STAGE 20: CAREGRAPH FINAL UPDATE    │
│  STAGE 10: RISK, TRAJECTORY, UNCERTAINTYSTAGE 21: SIGNALGRAPH TELEMETRY     │
│  STAGE 11: TRIAGE NOTE SYNTHESIS                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Stage-by-Stage Lifecycle Decomposition

### Stage 01: NEW ENCOUNTER
- **Actor:** Patient, Caregiver, or Nurse / Health Worker.
- **Responsibility:** Initiate the clinical encounter, capture explicit patient consent, and provision the synthetic Master Case ID (`PT-XXXXXX`).
- **Input:** Patient arrival, registration mode selection, digital/verbal consent confirmation.
- **Expected System Support:** Provisions immutable `case_id` in $< 200$ms; verifies consent checkbox; assigns initial timestamp.
- **Human Decision:** Patient/Caregiver agrees to triage screening; Nurse confirms patient physical presence.
- **Output:** Initialized `CaseModel` with state `ENCOUNTER_INITIALIZED` and captured `consent_record`.
- **Handoff:** Passes immediately to Stage 02.
- **Failure Risk:** Patient refuses consent; system duplicates case for an already active patient.
- **Permission Boundary:** `CREATE` encounter authorized for `ROLE_PATIENT`, `ROLE_CAREGIVER`, `ROLE_NURSE`, `ROLE_CLINICIAN`.
- **Evidence Tag:** `SUPPORTED` (BPUT B14, B15; DPDP Act 2023).

---

### Stage 02: PATHWAY SELECTION
- **Actor:** Nurse / Health Worker, Patient, or Triage Officer.
- **Responsibility:** Select between `REGULAR_TRIAGE` and `EMERGENCY_FAST_TRACK`.
- **Input:** Visual acuity assessment, presenting complaint severity (e.g., active seizure, massive bleeding, chest pain).
- **Expected System Support:** Large high-contrast two-path toggle; single tap routes instantly to emergency protocol if flagged.
- **Human Decision:** Nurse determines whether patient can sit for standard intake or requires immediate resuscitation bed.
- **Output:** Encounter pathway tag set to `REGULAR` or `EMERGENCY`.
- **Handoff:** If `EMERGENCY`, triggers immediate audio-visual alert on Doctor Queue and branches to Emergency Protocol (Stage 13 bypass). If `REGULAR`, proceeds to Stage 03.
- **Failure Risk:** High-acuity patient misrouted to routine path; delayed emergency recognition.
- **Permission Boundary:** `ROLE_NURSE`, `ROLE_CLINICIAN` can select either; `ROLE_PATIENT` defaults to regular with emergency red-button override.
- **Evidence Tag:** `SUPPORTED` (ESI Handbook; Indian Emergency Triage Protocols).

---

### Stage 03: INFORMATION COLLECTION
- **Actor:** Patient (self-service), Caregiver (surrogate), or Nurse / Health Worker (assisted).
- **Responsibility:** Provide unstructured symptom narrative, duration, pain severity, and upload physical medical records.
- **Input:** Spoken audio in regional language (Odia, Hindi, English), typed free text, camera capture of physical prescriptions/lab slips.
- **Expected System Support:** Web Audio API streaming with live waveform; multilingual input text area; document scanner with image compression.
- **Human Decision:** Patient narrates illness in own words; Nurse selects correct document type (`LAB_REPORT`, `PRESCRIPTION`, `DISCHARGE_SUMMARY`).
- **Output:** Raw audio file, raw text string, and document image artifacts attached to Master Case with timestamp and source tags.
- **Handoff:** Ingestion stream triggers asynchronous processing in Stage 04.
- **Failure Risk:** Poor audio quality / high background ambient noise; blurry camera photo; patient withholds critical past history.
- **Permission Boundary:** `CREATE_INPUT` authorized for Patient, Caregiver, Nurse, Clinician.
- **Evidence Tag:** `SUPPORTED` (BPUT B01, B02, B03, B04).

---

### Stage 04: EXTRACTION & ENTITY RESOLUTION
- **Actor:** Automated System (Supervised by Nurse / Health Worker).
- **Responsibility:** Transcribe voice, OCR documents, extract discrete clinical entities, and normalize colloquial terms to standard clinical concepts.
- **Input:** Raw audio recordings, document images, free-text strings.
- **Expected System Support:** Local faster-whisper speech-to-text; local PaddleOCR bounding-box extraction; local SLM clinical entity normalizer.
- **Human Decision:** Nurse monitors extraction status; can re-record audio or re-take image if extraction fails.
- **Output:** Structured discrete entities (`symptoms`, `vitals`, `labs`, `medications`) with source bounding coordinates, audio timecodes, and confidence scores ($[0.0, 1.0]$).
- **Handoff:** Extracted entities flow into Timeline (Stage 05) and Missing Information Engine (Stage 06).
- **Failure Risk:** OCR misreads decimal points (e.g., Creatinine "1.0" read as "10"); Whisper transcribes drug names incorrectly.
- **Permission Boundary:** System execution; Nurse/Doctor have `VIEW_EXTRACTION` rights.
- **Evidence Tag:** `SUPPORTED` (BPUT B02, B04, B05).

---

### Stage 05: TIMELINE SUMMARIZATION
- **Actor:** Automated System (Reviewed by Clinician / Nurse).
- **Responsibility:** Synthesize a chronological longitudinal sequence of symptom onset, previous clinic visits, medication trials, and diagnostic investigations.
- **Input:** Extracted date entities, temporal qualifiers ("3 days ago", "since yesterday morning"), and historic lab dates.
- **Expected System Support:** Longitudinal timeline builder sorting milestones chronologically, highlighting symptom duration and disease progression rate.
- **Human Decision:** Clinician visually scans timeline milestones to identify acute versus chronic disease patterns.
- **Output:** Structured `TimelineArray` containing milestone nodes with exact relative/absolute timestamps and provenance links.
- **Handoff:** Supplies chronological context to CAREGRAPH (Stage 09).
- **Failure Risk:** Inverted sequence of events (e.g., attributing fever after antibiotics rather than before).
- **Permission Boundary:** System constructs; Clinician has `EDIT_TIMELINE` authority.
- **Evidence Tag:** `SUPPORTED` (BPUT B06).

---

### Stage 06: MISSING INFORMATION AUDIT
- **Actor:** Automated System (Audited by Nurse / Health Worker).
- **Responsibility:** Scan extracted patient state against clinical protocol requirements to classify every parameter as `KNOWN`, `UNKNOWN`, `CONFLICTING`, or `UNRELIABLE`.
- **Input:** Current extracted entity set vs syndrome-specific clinical checklist (e.g., chest pain checklist requires BP, SpO2, radiation, onset).
- **Expected System Support:** Deterministic checklist validator calculating completeness ratio and identifying high-priority clinical gaps.
- **Human Decision:** Nurse reviews highlighted gaps; decides whether to collect physically or trigger clarifying questions.
- **Output:** Categorized `MissingDataAudit` object listing high-priority, medium-priority, and optional gaps.
- **Handoff:** Feeds into Follow-Up Question Engine (Stage 07) or Nurse Worklist.
- **Failure Risk:** Treating an unknown critical vital as normal (false negative); ignoring conflicting dates across documents.
- **Permission Boundary:** Read access across all roles; system enforces non-imputation invariant.
- **Evidence Tag:** `SUPPORTED` (BPUT B07; Phase 2 RES-04).

---

### Stage 07: FOLLOW-UP QUESTIONS (Next-Best Information)
- **Actor:** Patient or Caregiver (Supported by Nurse if non-literate).
- **Responsibility:** Answer 1–3 focused clarification questions designed to close high-uncertainty clinical gaps.
- **Input:** Identified high-priority information gaps from Stage 06.
- **Expected System Support:** Next-Best Information (NBI) engine selects maximum uncertainty-reducing questions; renders simple multiple-choice cards in patient's language.
- **Human Decision:** Patient selects true response ("Yes, radiating to left arm", "No", "Don't know"); Nurse assists if needed.
- **Output:** User responses appended directly to the existing Master Case.
- **Handoff:** Case proceeds to Data Consolidation (Stage 08) if critical fields satisfied; otherwise routes to Nurse Desk.
- **Failure Risk:** Patient answers randomly due to confusion; excessive questions causing drop-out (capped strictly at 3).
- **Permission Boundary:** `ROLE_PATIENT`, `ROLE_CAREGIVER` provide responses; `ROLE_NURSE` can enter responses on patient's behalf.
- **Evidence Tag:** `SUPPORTED` (BPUT B08; Phase 2 RES-04).

---

### Stage 08: DATA CONSOLIDATION
- **Actor:** Nurse / Frontline Health Worker.
- **Responsibility:** Review consolidated intake, perform physical vital signs measurement (BP, SpO2, PR, RR, Temp, Blood Sugar), and verify checklist.
- **Input:** Patient self-intake draft, physical diagnostic instruments (sphygmomanometer, pulse oximeter, thermometer).
- **Expected System Support:** Staff Missing-Data Checklist screen; single-page data entry with physiological range validation bounds.
- **Human Decision:** Nurse verifies abnormal vitals by repeating measurement; enters objective bedside readings.
- **Output:** Verified baseline vitals and red-flag checklists appended to Master Case (`vitals_verified = true`).
- **Handoff:** Case transitions to CAREGRAPH synthesis (Stage 09) and enters Doctor Queue.
- **Failure Risk:** Nurse skips respiratory rate; transposes systolic and diastolic blood pressure.
- **Permission Boundary:** `ROLE_NURSE` authorized to write vitals and verify checklist; strictly prohibited from creating second duplicate case.
- **Evidence Tag:** `SUPPORTED` (BPUT B05, B07; IPHS 2022).

---

### Stage 09: CAREGRAPH ENGINE INITIALIZATION
- **Actor:** Automated System.
- **Responsibility:** Instantiate the dynamic patient state graph, linking all validated symptoms, timeline events, objective vitals, and lab parameters.
- **Input:** Consolidated Master Case record from Stage 08.
- **Expected System Support:** Dynamic state graph constructor mapping physiological state and historical baselines into active clinical graph nodes.
- **Human Decision:** None (system automated state binding).
- **Output:** Initialized `CareGraphState` object containing clinical entity graph and temporal link topology.
- **Handoff:** Feeds into Risk, Trajectory & Uncertainty computation (Stage 10).
- **Failure Risk:** Memory leak or graph cyclic dependency (mitigated by clean directed acyclic graph structure).
- **Permission Boundary:** System core execution.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-10; C01).

---

### Stage 10: RISK, TRAJECTORY & UNCERTAINTY COMPUTATION
- **Actor:** Automated System.
- **Responsibility:** Calculate multi-dimensional physiological acuity ($R_t$), temporal trajectory slope ($\Delta R_t / \Delta t$), and mathematical epistemic uncertainty ($U_t \in [0, 1]$).
- **Input:** Serial vitals vector, NEWS2 / MEWS scoring tables, missing protocol field weights, deterministic red-flag rules.
- **Expected System Support:** Deterministic clinical scoring engine; calculates trajectory status (`IMPROVING`, `STABLE`, `WORSENING`, `CRITICAL`); computes $U_t$.
- **Human Decision:** None (deterministic computation); bounds AI probabilistic generation.
- **Output:** `AcuityVector = {score, band, trajectory_slope, uncertainty_u_t, active_red_flags}`.
- **Handoff:** Drives Doctor Queue ordering (Stage 12) and Triage Note synthesis (Stage 11).
- **Failure Risk:** Failure to escalate worsening trajectory due to stale timestamp; scoring calculation error.
- **Permission Boundary:** System calculation; strictly transparent and inspectable by Clinician.
- **Evidence Tag:** `SUPPORTED` (BPUT B10; Phase 2 RES-09, RES-10; C01, C03).

---

### Stage 11: TRIAGE NOTE SYNTHESIS
- **Actor:** Automated System (Local SLM).
- **Responsibility:** Synthesize a structured, concise clinical triage note draft conforming to standard SBAR/SOAP medical documentation.
- **Input:** Consolidated patient history, verified vitals, timeline summary, trajectory status, and active red flags.
- **Expected System Support:** Local SLM (Qwen2.5/3B) prompt execution; generates structured markdown draft with explicit provenance tags (`AI_INFERRED`).
- **Human Decision:** None (automated drafting); note is explicitly marked non-final until doctor review.
- **Output:** Draft `TriageNote` containing Chief Complaint, HPI, Vitals Summary, Red Flags, and Suggested Next Steps.
- **Handoff:** Placed into Doctor Review workbench (Stage 13).
- **Failure Risk:** LLM hallucination of clinical signs; verbose unstructured narrative defeating rapid reading.
- **Permission Boundary:** Advisory output; strictly prohibited from autonomous finalization.
- **Evidence Tag:** `SUPPORTED` (BPUT B05, B18; Phase 2 RES-04).

---

### Stage 12: DOCTOR QUEUE PRIORITIZATION
- **Actor:** Primary Clinician / Medical Officer (Observing prioritized queue).
- **Responsibility:** Monitor waiting cohort and select next patient for clinical consultation based on dynamic acuity ranking.
- **Input:** Departmental waiting list, calculated Acuity Vectors, wait duration ($\Delta t_{\text{wait}}$).
- **Expected System Support:** Dynamic queue sorting algorithm combining risk band, trajectory slope, and wait-time penalty function; surfaces audible/visual alerts on critical arrivals.
- **Human Decision:** Clinician selects top-priority patient; can manually pull forward any emergency presentation.
- **Output:** Case status changes from `IN_QUEUE` to `UNDER_CLINICAL_REVIEW`; assigned to examining doctor ID.
- **Handoff:** Opens Doctor Review Workbench (Stage 13).
- **Failure Risk:** Queue starvation of moderate-risk patients waiting prolonged hours; unmonitored deterioration in waiting area.
- **Permission Boundary:** `VIEW_QUEUE` authorized for Clinician, Nurse, Admin; `CLAIM_CASE` authorized for Clinician.
- **Evidence Tag:** `SUPPORTED` (BPUT B11; Phase 2 RES-03).

---

### Stage 13: DOCTOR CASE REVIEW
- **Actor:** Primary Clinician / Medical Officer / Qualified Reviewer.
- **Responsibility:** Review consolidated patient snapshot, inspect longitudinal timeline, audit evidence provenance, and examine uncertainty gauge within 30 seconds.
- **Input:** Synthesized Doctor Workbench displaying patient card, raw evidence thumbnails, CAREGRAPH state, and draft triage note.
- **Expected System Support:** High-contrast one-screen dashboard; clickable provenance drawers opening raw audio and OCR crops in $< 3$ seconds.
- **Human Decision:** Clinician correlates patient physical appearance with data; identifies contradictory or missing facts; forms clinical hypothesis.
- **Output:** Clinician cognitive assimilation of patient state.
- **Handoff:** Directly transitions to Clinical Verification/Modification (Stage 14).
- **Failure Risk:** Doctor skims without checking uncertainty gauge; automation bias accepting inaccurate AI triage note.
- **Permission Boundary:** `ROLE_CLINICIAN` exclusive full clinical inspection.
- **Evidence Tag:** `SUPPORTED` (BPUT B12, B18; NMC Regulations 2023).

---

### Stage 14: VERIFICATION / MODIFICATION / ADDITION (`VERIFY`, `MODIFY`, `ADD`)
- **Actor:** Primary Clinician / Medical Officer.
- **Responsibility:** Exercise Meaningful Human Control: verify accurate parameters, correct inaccurate extractions, and input bedside physical examination findings.
- **Input:** Bedside clinical examination (auscultation, palpation, GCS), doctor's diagnostic judgment.
- **Expected System Support:** In-place editable fields; one-click "Verify All" button for checked items; mandatory justification capture modal when altering extracted values.
- **Human Decision:**
  - `VERIFY`: Confirm AI extraction or nurse vital is clinically accurate.
  - `MODIFY`: Change incorrect value (e.g., correct pulse from 120 to 82), entering reason (`MEASUREMENT_ERROR`, `NEW_FINDING`).
  - `ADD`: Input physical examination findings (e.g., "Bilateral crackles at lung bases, pedal edema").
- **Output:** Master Case updated with clinician-verified parameters; audit log captures actor ID, timestamp, old value, new value, and rationale.
- **Handoff:** Verified clinical state feeds into FACILITYGRAPH Evaluation (Stage 15).
- **Failure Risk:** Doctor fails to correct hallucinated finding; doctor bypasses reason capture with meaningless keystrokes.
- **Permission Boundary:** `ROLE_CLINICIAN` exclusive write/verify authority.
- **Evidence Tag:** `SUPPORTED` (BPUT B12, B17, B18; Phase 2 RES-09).

---

### Stage 15: FACILITYGRAPH EVALUATION
- **Actor:** Automated System (Reviewed by Clinician).
- **Responsibility:** Evaluate verified patient clinical requirements against local institutional capabilities (5-tier facility model, on-duty specialists, available ICU beds, blood bank stock).
- **Input:** Verified patient acuity and procedure requirements vs local `FacilityModel` capability profile.
- **Expected System Support:** Deterministic Care Feasibility Engine matches patient needs against local assets; generates status (`CAPABILITY_ADEQUATE`, `BEDS_EXHAUSTED`, `SPECIALIST_UNAVAILABLE`, `CURRENT_FACILITY_INSUFFICIENT`).
- **Human Decision:** Clinician reviews local feasibility status; confirms whether patient can be safely managed on-site or requires transfer.
- **Output:** Care feasibility declaration attached to Master Case.
- **Handoff:** Feeds into Orchestration Guidance (Stage 16).
- **Failure Risk:** Outdated facility capability profile (e.g., oxygen plant failure not updated in system).
- **Permission Boundary:** System evaluates; Clinician reviews; Facility Admin configures.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-07, RES-11; C05).

---

### Stage 16: ORCHESTRATION GUIDANCE SYNTHESIS
- **Actor:** Automated System (Synthesized for Clinician).
- **Responsibility:** Synthesize patient trajectory, epistemic uncertainty, local facility feasibility, and regional syndromic alerts into ranked candidate care actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`).
- **Input:** CAREGRAPH state, FACILITYGRAPH feasibility, SIGNALGRAPH surge alerts.
- **Expected System Support:** Unified Orchestration Engine (`C08`) renders high-contrast Action Cards with explicit rationales, feasibility tags, and risk explanations.
- **Human Decision:** None (guidance synthesis); action cards are strictly advisory recommendations.
- **Output:** Display of candidate next care pathways on Doctor Workbench.
- **Handoff:** Clinician selects binding Care Pathway (Stage 17).
- **Failure Risk:** Probabilistic guidance suggesting inappropriate discharge; system recommending referral to a closed hospital.
- **Permission Boundary:** System advisory only; zero autonomous commitment.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-13; C08, C09).

---

### Stage 17: CARE PATHWAY SELECTION & SIGN-OFF
- **Actor:** Primary Clinician / Medical Officer / Qualified Reviewer.
- **Responsibility:** Execute final binding clinical decision, selecting the definitive care pathway and digitally signing the Master Clinical Report.
- **Input:** Clinical judgment, patient preference, Orchestration Guidance cards.
- **Expected System Support:** Pathway action buttons (`ROUTINE_DISCHARGE`, `OBSERVATION`, `WARD_ADMIT`, `EMERGENCY_OT`, `INTER_FACILITY_REFERRAL`); automated generation of appropriate report pack.
- **Human Decision:** Clinician selects pathway; may accept AI guidance or execute complete override with documented clinical reason.
- **Output:** Binding clinical disposition committed to Master Case; Master Clinical Report signed with cryptographic clinician credential.
- **Handoff:** Case routes to chosen disposition pathway execution (Stage 18).
- **Failure Risk:** Premature discharge of unstable patient; delayed decision causing queue gridlock.
- **Permission Boundary:** `ROLE_CLINICIAN` exclusive binding authority (`CARE_DECISION`).
- **Evidence Tag:** `SUPPORTED` (BPUT B18; NMC Code of Ethics 2023).

---

### Stage 18: DISPOSITION PATHWAY EXECUTION
- **Actor:** Clinician, Nurse, Referral Staff, Ward Staff, or Surgeon depending on selected pathway.
- **Responsibility:** Execute the logistical and clinical actions mandated by the chosen disposition:
  1. `ROUTINE_DISCHARGE`: Nurse dispenses medications; patient receives vernacular care slip and follow-up appointment date.
  2. `OBSERVATION`: Transferred to short-stay observation bed with repeat vitals timer.
  3. `WARD_ADMIT`: Ward transfer coordination; structured Inpatient Admission Dossier transmitted to receiving ward nurse.
  4. `EMERGENCY_OT`: Surgical fast-track; WHO Surgical Safety Checklist initiated; procedure-relevant dossier transmitted to scrub team.
  5. `INTER_FACILITY_REFERRAL`: Referral Staff accesses FACILITYGRAPH-matched destination; confirms bed; dispatches 108 ambulance with Structured Referral Pack.
- **Input:** Clinician-signed disposition order.
- **Expected System Support:** Purpose-specific report generation (Report Types 1–6); ambulance dispatch integration; appointment booking module.
- **Human Decision:** Staff execute physical bed placement, transport loading, or medication counseling.
- **Output:** Executed disposition records; transition of case status to `DISPOSITION_COMPLETED` or `IN_TRANSIT`.
- **Handoff:** Transitions to longitudinal outcome tracking (Stage 19).
- **Failure Risk:** Patient refused at receiving hospital gate; ambulance delay; patient leaves against medical advice (LAMA).
- **Permission Boundary:** Role-gated by department (e.g., Referral Staff executes transfer logistics; Ward Nurse executes bed check-in).
- **Evidence Tag:** `SUPPORTED` (BPUT B13; Phase 1 DOC-15, DOC-16).

---

### Stage 19: OUTCOME RECORDING & CLOSURE
- **Actor:** Primary Clinician, Inpatient Nurse, Referral Staff, or Community Health Worker (ASHA).
- **Responsibility:** Record actual longitudinal patient clinical outcome, closing the care loop.
- **Input:** Follow-up revisit findings, discharge outcome, transfer arrival status, or community recovery report.
- **Expected System Support:** Outcome recording modal capturing standardized endpoints:
  - `FULL_RECOVERY`
  - `STABILIZED_MANAGED`
  - `COMPLICATION_DEVELOPED`
  - `UNPLANNED_RE_ENCOUNTER`
  - `TRANSFERRED_OUT`
  - `MORTALITY`
- **Human Decision:** Clinician or health worker confirms final verified clinical status.
- **Output:** Master Case updated with `outcome_record`; case status transitions from `ACTIVE` to `RESOLVED`.
- **Handoff:** Feeds into CAREGRAPH final update (Stage 20) and SIGNALGRAPH telemetry (Stage 21).
- **Failure Risk:** Patient lost to follow-up; outcome unrecorded leaving case open indefinitely.
- **Permission Boundary:** `RECORD_OUTCOME` authorized for Clinician, Nurse, Referral Staff.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-14; C10).

---

### Stage 20: CAREGRAPH LONGITUDINAL UPDATE
- **Actor:** Automated System.
- **Responsibility:** Anchor recorded clinical outcome to the patient's longitudinal trajectory history, updating the synthetic calibration benchmark.
- **Input:** Final verified clinical outcome from Stage 19.
- **Expected System Support:** Longitudinal graph engine updates patient historical node; computes Brier calibration discordance score.
- **Human Decision:** None (system automated graph update).
- **Output:** Completed, cryptographically finalized Master Case record archived to local SQLite/PostgreSQL.
- **Handoff:** Aggregated into SIGNALGRAPH telemetry (Stage 21).
- **Failure Risk:** Database write corruption during archival.
- **Permission Boundary:** System core execution.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-14; C10).

---

### Stage 21: SIGNALGRAPH TELEMETRY FEED
- **Actor:** Automated System (Monitored by Facility Admin & Researcher).
- **Responsibility:** Strip all PII, extract syndromic signals (e.g., febrile thrombocytopenia cluster, pediatric wheeze surge), and update regional rolling 7-day $z$-score epidemiological telemetry.
- **Input:** Anonymized syndromic tags and geocodes from resolved/active encounters.
- **Expected System Support:** SQL aggregation views calculating rolling moving averages; statistical anomaly detector ($z > 2.58$) triggering epidemiological surge flags.
- **Human Decision:** Facility Admin reviews regional surge warnings to prepare bed/medication stocks; Researcher evaluates outbreak signals.
- **Output:** Updated SIGNALGRAPH telemetry stream; publishes syndromic alert badges to Doctor Workstations.
- **Handoff:** Closes the macro loop by enriching future triage encounters (Stage 10/16).
- **Failure Risk:** False alarm due to anomalous reporting spike; PII leakage in aggregated telemetry.
- **Permission Boundary:** Strictly anonymized; `ROLE_FACILITY_ADMIN`, `ROLE_RESEARCHER`, `ROLE_CLINICIAN` have read access.
- **Evidence Tag:** `SUPPORTED` (Phase 2 RES-08, RES-12; C07).

---

## 3. Cross-Role Handoff & Interface Points

| Handoff Boundary | From Actor | To Actor | Artifact Transferred | Verification / Safety Gate |
|:---|:---|:---|:---|:---|
| **Intake $\to$ Vitals** | Patient / Caregiver | Nurse / Health Worker | Self-Reported Draft (`case_id`) | Nurse verifies identity; checks missing vitals checklist. |
| **Triage $\to$ Consultation** | Nurse / Health Worker | Primary Clinician | Consolidated Case + Vitals | System validates physiological ranges; queue sorts by acuity. |
| **Consultation $\to$ Ward** | Primary Clinician | Inpatient Ward Nurse | Inpatient Admission Dossier | Clinician digital signature required; bed reservation checked. |
| **Consultation $\to$ OT** | Primary Clinician | Surgeon / Scrub Team | Procedure-Relevant Dossier | WHO Surgical Safety Checklist sign-in gate. |
| **Consultation $\to$ Transfer** | Primary Clinician | Referral Coordinator | Structured Referral Pack | Capability justification signed; destination feasibility verified. |
| **Transfer $\to$ Destination** | Referral Coordinator | Receiving Hospital Desk | Handoff Manifest + Vital Log | Pre-arrival bed acceptance acknowledgment. |
| **Discharge $\to$ Community** | Primary Clinician / Nurse | Patient / ASHA Worker | Vernacular Care Slip & Warning Signs | Patient/Attendant verbal acknowledgment of warning signs. |
| **Encounter $\to$ Surveillance**| Clinician Closure | SIGNALGRAPH Engine | De-identified Syndromic Record | Automated PII scrubber gate (24h ephemeral policy). |
