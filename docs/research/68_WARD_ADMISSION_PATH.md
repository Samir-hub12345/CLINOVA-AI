# CLINOVA AI — Inpatient Ward Admission Pathway Specification

> **Document ID:** `RES-68`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & Clinical Scope

When a patient's clinical presentation requires continuous parenteral medications, intravenous hydration, frequent serial vital signs monitoring, or close inpatient observation (e.g., moderate lobar pneumonia, complicated dengue fever without shock, acute pyelonephritis, poorly controlled diabetes with ketosis), the attending clinician initiates **Pathway C: Inpatient Ward Admission**.

The Inpatient Ward Admission Pathway governs the structured transition of clinical custody from the outpatient/casualty department to the inpatient nursing unit, ensuring that no vital history, drug allergy, or physician order is lost during the handoff.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INPATIENT WARD ADMISSION PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1 ] DOCTOR WARD ADMISSION REQUEST                                   │
│       │     (Selects target ward, priority, admission diagnosis)            │
│       ▼                                                                     │
│  [ STEP 2 ] AUTOMATED INPATIENT DOSSIER COMPILATION                         │
│       │     (Past records, active meds, allergy flags, precautions)         │
│       ▼                                                                     │
│  [ STEP 3 ] FACILITYGRAPH BED & WARD VERIFICATION                           │
│       │     (Allocates physical bed: e.g., Male Medical Ward Bed M-08)      │
│       ▼                                                                     │
│  [ STEP 4 ] WARD NURSING DESK NOTIFICATION                                  │
│       │     (Alerts ward sister console; bedside preparation)               │
│       ▼                                                                     │
│  [ STEP 5 ] STRUCTURED SBAR HANDOFF CHECKLIST                               │
│       │     (Situation, Background, Assessment, Recommendation)             │
│       ▼                                                                     │
│  [ STEP 6 ] WARD REPORT GENERATION (Report Type 4)                          │
│       │     (Inpatient Dossier printed / digital sign-off)                  │
│       ▼                                                                     │
│  [ STEP 7 ] TWO-PARTY CLINICAL HANDOFF SIGN-OFF                             │
│       │     (Transferring doctor/nurse + Receiving ward nurse)              │
│       ▼                                                                     │
│  [ STEP 8 ] INPATIENT MONITORING & LONGITUDINAL OBSERVATION                 │
│       │     (Serial vitals charted into CAREGRAPH inpatient view)           │
│       ▼                                                                     │
│  [ STEP 9 ] INPATIENT CLINICAL OUTCOME RESOLUTION                           │
│       │     (Discharge, Step-Down, Transfer, or Escalation)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step Admission Execution

### Step 1: Doctor Ward Admission Request
- **Actor:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Data State:** `STATE_ORCHESTRATION_PENDING` $\to$ `STATE_WARD_REQUESTED`.
- **System Action:**
  - Clinician selects `WARD_ADMISSION` on Doctor Review Workbench.
  - Clinician inputs mandatory admission metadata:
    - *Target Service:* Internal Medicine, General Surgery, Pediatrics, Orthopedics, Obstetrics & Gynecology.
    - *Required Ward Level:* General Ward, High Dependency Unit (HDU), Isolation Ward.
    - *Clinical Urgency Tier:* Immediate (Transfer within 15 mins) vs Planned (Transfer within 2 hours).
    - *Primary Admission Diagnosis:* Coded in ICD-11 / SNOMED-CT.

### Step 2: Automated Inpatient Dossier Compilation
- **Engine:** Automated synthesis engine compiles the pre-admission clinical packet from the existing Master Case:
  1. *Complete Medication Orders:* Drug name, formulation, dose, route, frequency, and duration.
  2. *Active Allergy Flags:* Highlighted in prominent red banner (e.g., `ALLERGY: Penicillin — Anaphylaxis`).
  3. *Mandatory Inpatient Precautions Checklist:*
     - Fall Risk: High / Moderate / Low (Morse Fall Scale).
     - Isolation Precautions: Standard, Contact, Airborne (e.g., active pulmonary TB).
     - Dietary Orders: NPO (Nil per os), Diabetic Diet, Strict Salt Restriction ($<2\text{g/day}$), Renal Diet.
     - Fluid Balance: Strict Intake/Output chart, Daily weight monitoring.

### Step 3: FACILITYGRAPH Bed & Resource Allocation
- **Engine:** $\text{FACILITYGRAPH}$ audits real-time inpatient census:
  - Verifies bed availability in target ward.
  - Matches clinical isolation requirements (e.g., negative pressure room for suspected multidrug-resistant tuberculosis).
  - Assigns specific physical bed identifier: `Bed_ID: WARD-MED2-BED-14`.
- **Exception Rule:** If target ward is at 100% occupancy:
  - System notifies doctor: *"Male Medical Ward full (24/24 beds occupied)."*
  - Prompts alternative: *"Step-Down HDU Bed 2 available"* or *"Initiate inter-facility transfer"*.

### Step 4: Ward Nursing Worklist Notification
- **Actor:** Ward Sister / Staff Nurse (`ROLE_NURSE`).
- **Workspace:** Ward Admission Worklist screen.
- **System Action:**
  - Emits audible ping and visual banner on target ward console: *"Incoming Admission: PT-847291 (Male, 54y, Severe Community-Acquired Pneumonia) $\longrightarrow$ Assigned Bed 14."*
  - Ward staff prepares bed, oxygen delivery apparatus, and bedside monitors.

### Step 5: Structured SBAR Handoff Checklist
To eliminate communication errors during departmental transfers, the platform enforces the standardized **SBAR (Situation, Background, Assessment, Recommendation)** handoff protocol:
- **S (Situation):** Patient name, age, primary reason for admission, current vital signs summary.
- **B (Background):** Onset timeline, past medical comorbidities, home medications, known allergies.
- **A (Assessment):** Attending physician's working diagnosis, CAREGRAPH trajectory (`DETERIORATING` vs `STABLE`), critical lab abnormalities (e.g., WBC = 18,500/μL, Serum Creatinine = 2.1 mg/dL).
- **R (Recommendation):** Immediate nursing orders, STAT IV antibiotics due time, frequency of vitals checks (e.g., Q2H blood pressure monitoring), red-flag thresholds for calling the medical registrar.

### Step 6: Ward Report Generation (Report Type 4)
- **Artifact:** Generates the **Inpatient Ward Dossier / Handoff Report (`Report Type 4`)**:
  - Encodes complete clinical timeline, verified baseline vitals, and physician treatment plan.
  - Includes scannable QR code linking to digital inpatient charting view.
  - Can be printed for paper hospital clipboards or viewed on ward tablets.

### Step 7: Two-Party Clinical Handoff Sign-Off
- **Actors:** 
  1. Transferring Staff: Outpatient / Casualty Nurse or Doctor.
  2. Receiving Staff: Ward Sister (`ROLE_NURSE`).
- **Data State:** `STATE_WARD_REQUESTED` $\to$ `STATE_WARD_ADMITTED`.
- **Safety Gate:** Both healthcare professionals must input their employee credentials and sign the digital handoff checklist. This establishes an unalterable legal transition of patient custody.

### Step 8: Bedside Inpatient Monitoring & Longitudinal Tracking
- **Data State:** `STATE_OUTCOME_PENDING`.
- **Operational Mode:**
  - $\text{CAREGRAPH}$ transitions into Inpatient Longitudinal Mode.
  - Ward nurses record serial vitals, administered medication doses, and intake/output balance directly into the Master Case.
  - Early Warning System (NEWS2) monitors for silent clinical deterioration:
    - If composite score rises by $\ge 2$ points, system triggers an amber bedside alert.
    - If patient collapses, staff taps "Emergency Fast-Track", triggering immediate resuscitation mode (`STATE_EMERGENCY_ACTIVE`).

### Step 9: Inpatient Clinical Outcome Resolution
- **Actor:** Inpatient Attending Physician (`ROLE_CLINICIAN`).
- **Data State:** `STATE_RESOLVED` $\to$ `STATE_CLOSED`.
- **Outcome Resolution:**
  - When the inpatient stay concludes, the doctor logs the definitive outcome:
    - `FULL_RECOVERY`: Disease resolved; patient discharged home.
    - `STABILIZED`: Acute flare controlled; outpatient follow-up scheduled.
    - `COMPLICATION_MANAGED`: Complication managed successfully on-site.
    - `REFERRED_HIGHER`: Patient deteriorated or required tertiary care; transferred.
    - `ADVERSE_EVENT`: Unexpected clinical deterioration or mortality.
  - System generates formal Discharge Summary, seals the encounter audit trail, and exports anonymized telemetry to $\text{SIGNALGRAPH}$.
