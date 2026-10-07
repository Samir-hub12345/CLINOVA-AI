# CLINOVA AI — Design Specifications: Cluster 6 (Emergency Fast-Track & Operation Theatre)

> **File:** `docs/design/06_EMERGENCY_AND_OT_SCREENS.md`  
> **Screens Covered:** Screens 32 through 36  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 32: Emergency Fast-Track Intake

### 1. Specification
- **Route:** `/emergency/fast-track`
- **Purpose:** Ultra-rapid (< 30 seconds) emergency registration and immediate ABCD vital acquisition. Bypasses non-essential questionnaires.
- **Actor:** Emergency Triage Nurse, Emergency Medical Officer, Paramedic.
- **Entry Condition:** Triggered by Emergency button on Screen 05 or dynamic escalation.
- **Inputs:** ABCD vitals (Airway state, RR, SpO2, SBP/DBP, Heart Rate, GCS), Primary Emergency Category selector (Cardiac, Sepsis, Trauma, Respiratory, Neurological).
- **Outputs:** High-contrast red flashing interface, instant bedside audible alert, instant Master Case ID provisioning (< 200ms).
- **Actions:** "ACTIVATE RESUSCITATION BAY", "DISPATCH EMERGENCY DOCTOR CALL".
- **Navigation:** Advances to Screen 33 (`/emergency/bay/:id`).
- **Graph Linkage:** Instantly creates `MasterCase` flagged with `PRIORITY_CRITICAL_P1`.

### 2. Wireframe (Screen 32)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🚨 EMERGENCY FAST-TRACK INTAKE 🚨                    [ EMERGENCY BAY DESK ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INSTANT ENCOUNTER PROVISIONING: PT-EMG-0881 (< 200 ms)                    │
│                                                                             │
│   PRIMARY EMERGENCY CATEGORY:                                               │
│   [ 🫀 CARDIAC / STEMI ] [ 🩸 SEVERE TRAUMA ] [ 🦠 SEPTIC SHOCK ] [ 🧠 STROKE]│
│                                                                             │
│   RAPID ABCD PHYSIOLOGICAL VITALS (30-SECOND TARGET):                       │
│   • Airway / Breathing:  SpO2: [ 84 ] % (Cyanotic) | RR: [ 32 ] /min        │
│   • Circulation:         BP:   [ 72 / 44 ] mmHg   | HR: [ 138 ] bpm         │
│   • Disability:          GCS:  [ 7 / 15 ] (E2 V2 M3 — Comatose)             │
│                                                                             │
│   Shock Index: 1.91 (SEVERE HEMODYNAMIC COLLAPSE)                           │
│                                                                             │
│   [ CANCEL EMERGENCY ]               [ 🚨 ACTIVATE RESUSCITATION TEAM NOW ] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 33: Emergency Resuscitation Bay Workspace

### 1. Specification
- **Route:** `/emergency/bay/:id`
- **Purpose:** High-contrast acute resuscitation workstation displaying active resuscitation bundles, live vital telemetry, and stat emergency orders.
- **Actor:** Emergency Physician, Resuscitation Nursing Lead.
- **Entry Condition:** Resuscitation activated from Screen 32.
- **Inputs:** Resuscitation bundle checkboxes (Endotracheal tube size, IV fluid volume, STAT vasopressor start, Blood cross-match request).
- **Outputs:** Live continuous vital stream, Shock index trend, Golden-hour countdown timer (`00:18:42`).
- **Actions:** "Generate Emergency Report (Type 5)", "Route to Surgical OT", "Route to ICU".
- **Navigation:** Advances to Screen 34 (OT) or Screen 35 (Emergency Report).
- **Graph Linkage:** Commits to `MasterCase.emergency_ot_record`.

### 2. Wireframe (Screen 33)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🚨 RESUSCITATION BAY 1 [CRITICAL ACUTE] 🚨           [ DR. MOHAPATRA, MO ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│  CASE: PT-EMG-0881 | 58M | GOLDEN-HOUR TIMER: 00:14:22 | SHOCK INDEX: 1.91 │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  LIVE VITALS MONITOR TELEMETRY       │  ACTIVE STAT EMERGENCY BUNDLE        │
│  • Heart Rate: 138 bpm (Sinus Tach)  │  [X] Bag-Valve-Mask O2 @ 15 L/min    │
│  • BP: 72/44 mmHg (Severe Shock)     │  [X] 2x 16G IV Lines Inserted (Bilat)│
│  • SpO2: 89% (Rising on O2)          │  [X] 1000 mL Ringer's Lactate STAT   │
│  • GCS: 7/15 (Airway at Risk)        │  [ ] Endotracheal Intubation (7.5 ET)│
│                                      │  [ ] Noradrenaline Infusion Standby  │
├──────────────────────────────────────┴──────────────────────────────────────┤
│  STAT LABS & CROSS-MATCH: Bedside Glu: 48 mg/dL | Blood Group: O-Neg STAT   │
│                                                                             │
│  [ TRANSFER TO OT (SURGICAL) ]          [ GENERATE EMERGENCY REPORT (TYPE 5)]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 34: Operation Theatre (OT) Surgical Safety Checklist

### 1. Specification
- **Route:** `/ot/checklist/:id`
- **Purpose:** Procedure-specific pre-operative safety checklist complying with the WHO Surgical Safety Checklist. Strips away non-essential outpatient history.
- **Actor:** Consultant Surgeon, Anesthesiologist, OT Scrub Nurse.
- **Entry Condition:** Acute surgical case booked for OT.
- **Inputs:** Sign-In, Time-Out, and Sign-Out confirmation checkboxes, surgical site mark confirmed, surgical team names.
- **Outputs:** Clean, high-contrast surgical dossier showing airway risk, NPO hours, reserved blood units, and implant readiness.
- **Actions:** "Sign In (Before Induction)", "Time Out (Before Incision)", "Sign Out (Before Departure)", "Generate OT Report (Type 6)".
- **Navigation:** Advances to Screen 36 (`/ot/report/:id`).
- **Graph Linkage:** Sets `MasterCase.emergency_ot_record.surgical_safety_checklist_completed = True`.

### 2. Wireframe (Screen 34)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       WHO Surgical Safety Checklist    [ OT SUITE 2 ]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SURGICAL SAFETY DOSSIER: EMERGENCY EXPLORATORY LAPAROTOMY                 │
│   Patient: PT-EMG-0881 | Surgeon: Dr. R. Patnaik | Anesth: Dr. K. Mishra    │
│                                                                             │
│   [1. SIGN IN (Before Induction of Anesthesia)]                             │
│   [X] Patient identity, surgical site (Abdomen), and consent confirmed      │
│   [X] Surgical site marked by operating surgeon                             │
│   [X] Anesthesia machine & medication check complete                        │
│   [X] Pulse oximeter on patient and functioning                             │
│   [X] Known allergy check: No Known Drug Allergies                          │
│   [X] Difficult airway / aspiration risk evaluated (Mallampati 3)           │
│   [X] Blood loss risk (>500 mL) evaluated: 4 Units PRBC Cross-Matched [✓]   │
│                                                                             │
│   [2. TIME OUT (Before Skin Incision)]                                      │
│   [X] Team verbal introduction: Surgeon, Anesthetist, Scrub Nurse           │
│   [X] Antibiotic prophylaxis administered within past 60 minutes            │
│                                                                             │
│   [ PROCEED TO INCISION ]                 [ COMPLETE OT SURGICAL REPORT ──>]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 35: Purpose-Specific Emergency Report (Report Type 5)

### 1. Specification
- **Route:** `/emergency/report/:id`
- **Purpose:** Ultra-concise, high-contrast 1-page emergency summary engineered for instant scanning (< 15 seconds) under acute resuscitation conditions.
- **Actor:** Emergency Physician, Resuscitation Team, ICU Registrar.
- **Entry Condition:** Generated from Screen 33.
- **Inputs:** None (Read-only formatted summary).
- **Outputs:** Single-page emergency dossier with high-contrast red alert banner, verified ABCD vitals, golden-hour onset, panic lab values, and administered interventions.
- **Actions:** "Print Instant Emergency Sheet", "Transmit to ICU Desk", "Back to Bay".
- **Navigation:** Returns to Screen 33.
- **Graph Linkage:** Dynamic rendering of Report Type 5 from Master Case.

### 2. Wireframe (Screen 35)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [PRINT EMERGENCY SHEET]     [TRANSMIT TO ICU]               [< BACK TO BAY] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   🚨 CLINOVA AI — EMERGENCY FAST-TRACK RESUSCITATION DOSSIER 🚨             │
│   Facility: Capital Hospital | Time: 11:28 AM | Case: PT-EMG-0881           │
│   ────────────────────────────────────────────────────────────────────────  │
│   CRITICAL PRESENTATION: MASSIVE UPPER GI HEMORRHAGE & HYPOVOLEMIC SHOCK    │
│   ONSET WINDOW: 90 Minutes Ago | GOLDEN HOUR STATUS: ACTIVE                 │
│                                                                             │
│   CRITICAL ABCD VITALS (ON ARRIVAL):                                        │
│   • Blood Pressure: 72/44 mmHg (MAP 53) ──> SEVERE SHOCK                    │
│   • Heart Rate: 138 bpm (Tachycardia)   ──> Shock Index: 1.91 (CRITICAL)    │
│   • SpO2: 89% Room Air / 98% on 15L O2 | GCS: 7/15 (E2 V2 M3)               │
│                                                                             │
│   PANIC LAB FINDINGS: Bedside Hb: 5.8 g/dL | Blood Glucose: 48 mg/dL        │
│   BLOOD BANK STATUS: 4 Units O-Negative PRBC Reserved at Blood Bank [✓]     │
│   ALLERGIES: None Known | ANTICOAGULATION: Patient on Aspirin (Confirmed)   │
│                                                                             │
│   RESUSCITATION ADMINISTERED:                                               │
│   • 2x 16G IV access | 1000 mL Ringer's Lactate infused | 25% Dextrose 100mL│
│   • ET Intubation complete (Size 7.5 cuffed tube confirmed via ETCO2)       │
│                                                                             │
│   Attending Physician: Dr. S. Mohapatra, MD [SIGNED 11:32 AM]               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 36: Purpose-Specific OT Surgical Report (Report Type 6)

### 1. Specification
- **Route:** `/ot/report/:id`
- **Purpose:** Formal surgical operative report detailing surgical procedure performed, intraoperative findings, blood loss, specimen pathology, and post-anesthesia recovery orders.
- **Actor:** Operating Surgeon, Anesthesiologist.
- **Entry Condition:** Surgical procedure concluded.
- **Inputs:** Operative findings text, estimated blood loss (mL), surgical specimen labels, post-op destination (Surgical ICU / Step-Down).
- **Outputs:** Formatted operative surgical pack complying with hospital surgical records.
- **Actions:** "Sign Operative Report", "Print Surgical Summary", "Transmit to Surgical ICU".
- **Navigation:** Completes surgical encounter; transfers case to Inpatient ICU.
- **Graph Linkage:** Commits Report Type 6 to Master Case.

### 2. Wireframe (Screen 36)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [PRINT OT REPORT]           [TRANSMIT TO SURGICAL ICU]       [< BACK TO OT] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CLINOVA AI — OPERATION THEATRE (OT) OPERATIVE REPORT                      │
│   Facility: Capital Hospital OT Suite 2 | Date: 08-Oct-2026 | ID: PT-EMG-0881│
│   ────────────────────────────────────────────────────────────────────────  │
│   PROCEDURE: EMERGENCY EXPLORATORY LAPAROTOMY & DUODENAL ULCER UNDERRUNNING │
│   SURGEON: Dr. R. Patnaik, MS | ANESTHESIOLOGIST: Dr. K. Mishra, MD         │
│                                                                             │
│   1. INTRAOPERATIVE FINDINGS:                                               │
│      2cm bleeding Forrest 1A peptic ulcer on posterior duodenal bulb.       │
│      Hemoperitoneum: 800 mL fresh blood evacuated.                          │
│                                                                             │
│   2. SURGICAL PROCEDURE DETAILS:                                            │
│      Longitudinal duodenotomy performed; bleeding gastroduodenal artery     │
│      transfixed with 2-0 silk sutures. Heineke-Mikulicz pyloroplasty done.  │
│                                                                             │
│   3. ESTIMATED BLOOD LOSS: 950 mL | TRANSFUSION: 2 Units PRBC intra-op.     │
│   4. SPECIMENS SENT: Duodenal margin biopsy to Histopathology.              │
│   5. POST-OP DISPOSITION: TRANSFER TO SURGICAL ICU (VENTILATED / STABILIZED)│
│                                                                             │
│   Operating Surgeon Signature: Dr. R. Patnaik, MS [SIGNED 01:15 PM]         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
