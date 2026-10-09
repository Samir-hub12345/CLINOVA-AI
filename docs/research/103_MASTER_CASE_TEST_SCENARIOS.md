# CLINOVA AI — Master Case Validation Scenarios (Cases A – J)

> **Document ID:** `RES-103`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Validation Methodology & Scenario Objectives

To rigorously prove that the canonical data model satisfies all clinical safety, relational integrity, epistemic, and synchronization requirements, the schema is evaluated against **Ten End-to-End Clinical Test Scenarios (Cases A through J)**.

Each scenario walks through:
1. **Initial Clinical Presentation & Database State**
2. **Step-by-Step State Machine Progression across the 27 Canonical States**
3. **Database Entities Created, Foreign Key Linkages, and Mutations**
4. **Data Invariants Exercised & Preserved**
5. **Final Database State & Tamper-Evident Verification**

---

## 2. Comprehensive Walkthrough of Cases A through J

---

### Case A: Routine PHC Patient $\to$ Doctor Review $\to$ Referral $\to$ District Hospital $\to$ Outcome

- **Clinical Scenario:** 52-year-old male presents to rural PHC with 4-day chest tightness and shortness of breath. Vernacular Odia audio recorded; prescription slip photographed. Doctor reviews, identifies acute coronary syndrome requiring cardiac care; PHC lacks troponin/ICU; patient referred to District Hospital; arrives, stabilized in ward, discharged improved.
- **State Machine Progression:**
  $$\begin{aligned}
  &S01: \text{STATE\_NEW} \longrightarrow S02: \text{STATE\_INTAKE\_COLLECTING} \longrightarrow S03: \text{STATE\_EXTRACTING} \longrightarrow S04: \text{STATE\_EXTRACTION\_REVIEW} \\
  &\longrightarrow S05: \text{STATE\_MISSING\_AUDIT} \longrightarrow S06: \text{STATE\_FOLLOW\_UP\_PENDING} \longrightarrow S08: \text{STATE\_STAFF\_VERIFIED} \longrightarrow S09: \text{STATE\_CONSOLIDATED} \\
  &\longrightarrow S10: \text{STATE\_TRIAGE\_READY} \longrightarrow S11: \text{STATE\_DOCTOR\_QUEUED} \longrightarrow S12: \text{STATE\_DOCTOR\_REVIEWING} \longrightarrow S13: \text{STATE\_CLINICIAN\_VERIFIED} \\
  &\longrightarrow S14: \text{STATE\_FACILITY\_EVALUATING} \longrightarrow S15: \text{STATE\_ORCHESTRATION\_PENDING} \longrightarrow S20: \text{STATE\_REFERRAL\_PENDING} \\
  &\longrightarrow S21: \text{STATE\_TRANSFER\_IN\_TRANSIT} \longrightarrow S25: \text{STATE\_OUTCOME\_PENDING} \longrightarrow S26: \text{STATE\_RESOLVED} \longrightarrow S27: \text{STATE\_CLOSED}
  \end{aligned}$$
- **Data Model Verification:**
  - Exactly **ONE `case_id`** (`c1`) anchors all records across BOTH facilities.
  - At District Hospital reception, no new case is spawned: `cases.current_facility_id` updates from PHC UUID to DH UUID.
  - `referrals` record links `referring_facility_id = PHC_ID` and `destination_facility_id = DH_ID`.
  - `case_outcomes` links directly to `c1` with `outcome_type = 'IMPROVED'`.
- **Invariants Preserved:** `INV-01` (Single Case), `INV-04` (Clinician Monopoly), `INV-09` (Closed-Loop Referral).

---

### Case B: Routine Patient $\to$ Missing Critical Vitals $\to$ Nurse Verification $\to$ Doctor Review

- **Clinical Scenario:** 34-year-old female presents at busy outpatient desk with severe dizzy spells. Self-service voice intake transcribes dizziness, but blood pressure is absent.
- **State Machine Progression:**
  $$\begin{aligned}
  &S01: \text{STATE\_NEW} \longrightarrow S02: \text{STATE\_INTAKE\_COLLECTING} \longrightarrow S03: \text{STATE\_EXTRACTING} \longrightarrow S04: \text{STATE\_EXTRACTION\_REVIEW} \\
  &\longrightarrow S05: \text{STATE\_MISSING\_AUDIT} \longrightarrow S07: \text{STATE\_STAFF\_DATA\_PENDING} \longrightarrow S08: \text{STATE\_STAFF\_VERIFIED} \\
  &\longrightarrow S09: \text{STATE\_CONSOLIDATED} \longrightarrow S10: \text{STATE\_TRIAGE\_READY} \longrightarrow S11: \text{STATE\_DOCTOR\_QUEUED} \longrightarrow S12: \text{STATE\_DOCTOR\_REVIEWING}
  \end{aligned}$$
- **Data Model Verification:**
  - In $S05$, `information_sufficiency_evaluations` calculates $S = 0.58 < 0.85$ (BP, HR missing).
  - `missing_information_items` creates row for `systolic_bp` with `clinical_importance = 'CRITICAL'`.
  - Case CANNOT enter $S11$; state machine diverts directly to $S07$ (`STATE_STAFF_DATA_PENDING`).
  - Nurse measures BP (80/50 mmHg, severe hypotension), writing to `vital_readings`. Row in `missing_information_items` resolves to `ANSWERED`.
  - Sufficiency recalculates to $S = 0.94$, unblocking promotion to Doctor Queue.
- **Invariants Preserved:** `INV-02` (Zero-Imputation Law), `INV-06` (Epistemic Provenance).

---

### Case C: Routine Patient $\to$ Waiting Room Deterioration $\to$ Emergency Escalation

- **Clinical Scenario:** 60-year-old male with mild dyspnea waiting in OPD queue. While waiting, patient suddenly collapses with acute pulmonary edema. Staff triggers emergency break-glass.
- **State Machine Progression:**
  $$\begin{aligned}
  &S11: \text{STATE\_DOCTOR\_QUEUED} \quad \xrightarrow[\text{Trigger: BREAK\_GLASS\_EMERGENCY}]{\text{Instant Jump}} \quad S22: \text{STATE\_EMERGENCY\_ACTIVE} \\
  &\longrightarrow S13: \text{STATE\_CLINICIAN\_VERIFIED} \longrightarrow S18: \text{STATE\_WARD\_REQUESTED} \longrightarrow S19: \text{STATE\_WARD\_ADMITTED}
  \end{aligned}$$
- **Data Model Verification:**
  - Instant transition from $S11 \to S22$ recorded in `case_state_transitions`.
  - `privacy_break_glass_audits` logs actor ID, timestamp, and justification (`COLLAPSE_IN_WAITING_ROOM`).
  - `vital_readings` captures 30s rapid ABCD vitals ($\text{SpO}_2 = 74\%$, $\text{HR} = 142\text{ bpm}$).
  - `cases.acuity_tier` elevated to `'EMERGENCY'`.
- **Invariants Preserved:** `INV-03` (Event Immutability), `INV-10` (Break-Glass Emergency Privilege).

---

### Case D: Emergency Anonymous Patient $\to$ Resuscitation $\to$ Identity Discovered $\to$ Ward

- **Clinical Scenario:** Unconscious hit-and-run victim brought in by passersby. No identification. Stabilized; family arrives later with Aadhaar card; patient admitted to ICU.
- **State Machine Progression:**
  $$\begin{aligned}
  &S01: \text{STATE\_NEW} \longrightarrow S22: \text{STATE\_EMERGENCY\_ACTIVE} \longrightarrow S13: \text{STATE\_CLINICIAN\_VERIFIED} \\
  &\longrightarrow S18: \text{STATE\_WARD\_REQUESTED} \longrightarrow S19: \text{STATE\_WARD\_ADMITTED}
  \end{aligned}$$
- **Data Model Verification:**
  - Case instantiated in $< 200\text{ms}$ with `is_anonymous = TRUE` and `patient_id = NULL`.
  - `patient_identifiers` creates token `EMG-20261008-0841`.
  - Post-stabilization, family presents Aadhaar. Registrar creates `patients` record (`p_true`).
  - `identity_link_events` records cryptographic binding between `EMG-20261008-0841` and `p_true.id`.
  - `cases.patient_id` set to `p_true.id` and `cases.is_anonymous = FALSE`.
  - Zero loss or splintering of resuscitation vitals.
- **Invariants Preserved:** `INV-01` (Single Case), `INV-11` (Emergency Implied Consent).

---

### Case E: Referral Destination Saturated $\to$ Automated Re-routing to Alternate Facility

- **Clinical Scenario:** PHC initiates urgent referral to District Hospital A for pediatric meningitis. Hospital A responds with bed saturation (ICU full). System reroutes to Sub-Divisional Hospital B.
- **State Machine Progression:**
  $$\begin{aligned}
  &S20: \text{STATE\_REFERRAL\_PENDING} \quad \xrightarrow{\text{Destination Saturation}} \quad \text{Reroute Evaluation} \\
  &\longrightarrow S20: \text{STATE\_REFERRAL\_PENDING (Hospital B)} \longrightarrow S21: \text{STATE\_TRANSFER\_IN\_TRANSIT}
  \end{aligned}$$
- **Data Model Verification:**
  - `referrals` row 1 marked `status = 'REJECTED'`, `rejection_reason = 'NO_ICU_BED'`.
  - `referral_rejections` captures audit record with `rejected_facility_id = Hospital_A_ID`.
  - `feasibility_evaluations` re-evaluates regional matrix; recommends Hospital B.
  - `referrals` row 2 created with `destination_facility_id = Hospital_B_ID`, linked via `rerouted_referral_id`.
- **Invariants Preserved:** `INV-09` (Anti-Blind-Transfer Integrity).

---

### Case F: Conflicting Evidence (Patient Self-Report vs Nurse Point-of-Care Vital)

- **Clinical Scenario:** Patient states: *"My BP is fine, around 120."* Nurse cuff measures $195/115\text{ mmHg}$.
- **Data Model Verification:**
  - Row 1 created in `evidence_records`: `source_type = 'PATIENT_REPORTED'`, `value_raw = '120'`, `epistemic_status = 'KNOWN'`.
  - Row 2 created in `evidence_records`: `source_type = 'STAFF_ENTERED'`, `value_raw = '195/115'`, `epistemic_status = 'VERIFIED'`.
  - Neither row is deleted or overwritten.
  - `evidence_conflicts` row created with pointer to Row 1 and Row 2.
  - Workbench highlights conflict in red; clinician explicitly selects Row 2 for active CAREGRAPH calculations.
- **Invariants Preserved:** `INV-02` (Zero Imputation), `INV-06` (Epistemic Provenance), `INV-08` (Non-Destructive Overrides).

---

### Case G: Clinician Overrides Machine Recommendation

- **Clinical Scenario:** AI suggests `SUGGEST_ROUTINE_CARE` for 45-year-old with epigastric discomfort. Doctor suspects atypical myocardial infarction and overrides disposition to `ADMIT_OBSERVATION` with serial troponins.
- **Data Model Verification:**
  - `orchestration_recommendations` row preserved with `suggested_action = 'CONTINUE'`, `status = 'OVERRIDDEN'`.
  - `clinician_reviews` captures `disposition_decision = 'OBSERVE'`, `is_concordant_with_ai = FALSE`.
  - `clinician_modifications` records `field_path = 'disposition'`, `original_value = 'CONTINUE'`, `new_value = 'OBSERVE'`, `clinical_justification = 'High suspicion of atypical ACS; ECG shows subtle T-wave flattening'`.
- **Invariants Preserved:** `INV-04` (Clinician Monopoly), `INV-05` (Advisory-Only AI), `INV-08` (Non-Destructive Overrides).

---

### Case H: Offline Edge Node $\to$ Reconnect $\to$ Synchronization & Conflict Resolution

- **Clinical Scenario:** Rural PHC node loses cellular WAN for 6 hours. 18 patient encounters created in local SQLite WAL. Uplink restored; transactions synced to central cloud.
- **Data Model Verification:**
  - Local transactions logged in SQLite `sync_journals` with `sync_status = 'PENDING_UPLOAD'`.
  - Central Postgres receives JSON payloads; matches on RFC 4122 `UUIDv4`.
  - Append-only clinical events merge cleanly with zero primary key collisions.
  - `sync_journals.sync_status` transitions to `'SYNCED'`.
- **Invariants Preserved:** `INV-03` (Event Immutability), `INV-12` (Idempotent Synchronization).

---

### Case I: Further Review (Pathway B) $\to$ Revisit Check-In $\to$ Same Master Case Resumed

- **Clinical Scenario:** Outpatient physician orders 48-hour sputum AFB and liver panel; sets revisit slot. Patient returns 2 days later with lab results.
- **State Machine Progression:**
  $$\begin{aligned}
  &S15 \longrightarrow S17: \text{STATE\_FURTHER\_REVIEW} \longrightarrow S25: \text{STATE\_OUTCOME\_PENDING} \\
  &\quad \xrightarrow{\text{Patient Physical Revisit}} \quad S12: \text{STATE\_DOCTOR\_REVIEWING} \longrightarrow S26: \text{STATE\_RESOLVED} \longrightarrow S27: \text{STATE\_CLOSED}
  \end{aligned}$$
- **Data Model Verification:**
  - Patient revisit check-in DOES NOT generate a new case. Reception searches and resumes the **SAME `case_id`**.
  - New lab results attached directly to existing `cases(id)`.
  - `case_state_transitions` records transition from $S25 \to S12$.
  - Case resolved with antibiotic prescription; final Merkle seal applied in $S27$.
- **Invariants Preserved:** `INV-01` (Single Continuous Case Invariant).

---

### Case J: Operation Theatre (OT) Fast-Track $\to$ WHO Checklist $\to$ Post-Op Outcome

- **Clinical Scenario:** 28-year-old female with acute ruptured appendicitis requiring emergency appendectomy.
- **State Machine Progression:**
  $$\begin{aligned}
  &S13: \text{STATE\_CLINICIAN\_VERIFIED} \longrightarrow S23: \text{STATE\_OT\_PENDING} \longrightarrow S24: \text{STATE\_OT\_HANDOFF} \\
  &\longrightarrow S25: \text{STATE\_OUTCOME\_PENDING} \longrightarrow S26: \text{STATE\_RESOLVED} \longrightarrow S27: \text{STATE\_CLOSED}
  \end{aligned}$$
- **Data Model Verification:**
  - `surgical_procedures` row created with `booking_urgency = 'EMERGENCY_IMMEDIATE'`.
  - Ergonomic filtering suppresses non-surgical history; highlights NPO time and cross-match hold.
  - Scrub nurse and surgeon complete `who_checklist_signin`, `who_checklist_timeout`, and `who_checklist_signout`.
  - `dual_signoff_verified = TRUE` required before state advances to $S25$.
  - Patient recovers in surgical ward; outcome logged as `RESOLVED`.
- **Invariants Preserved:** `INV-01` (Single Case), `INV-04` (Clinician Monopoly).
