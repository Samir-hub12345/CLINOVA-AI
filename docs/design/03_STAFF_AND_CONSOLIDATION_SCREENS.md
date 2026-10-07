# CLINOVA AI — Design Specifications: Cluster 3 (Staff Workspace & Data Consolidation)

> **File:** `docs/design/03_STAFF_AND_CONSOLIDATION_SCREENS.md`  
> **Screens Covered:** Screens 13, 14, 15  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 13: Staff Assignment Workspace

### 1. Specification
- **Route:** `/staff/worklist`
- **Purpose:** Provide frontline triage nurses and health workers with a prioritized worklist of patient encounters requiring physical vital acquisition, missing-data resolution, or red-flag confirmation.
- **Actor:** Triage Nurse, Community Health Worker (ANM / ASHA).
- **Entry Condition:** Authenticated nurse session.
- **Inputs:** Filter by urgency band, search by synthetic ID.
- **Outputs:** Tabular worklist with priority badges, patient age/gender, pending missing parameters, wait time ticker.
- **Actions:** "Open Missing-Data Checklist" (routes to Screen 14), "Trigger Immediate Bedside Escalation".
- **Navigation:** Links to Screen 14.
- **States:**
  - *Normal:* List of pending cases sorted by missing parameter criticality and wait duration.
  - *Empty State:* "All triage intake cases complete. Zero pending vital acquisitions."
- **Graph Linkage:** Reads cases where `CareGraph.uncertainty_vector.unknown_count > 0` and critical vitals are absent.

### 2. Wireframe (Screen 13)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Nurse Triage Worklist            [ SISTER S. NAYAK ]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MISSING-DATA WORKLIST: PENDING PHYSICAL VITALS & CHECKLISTS               │
│                                                                             │
│   CASE ID    PATIENT     PRESENTATION      MISSING CRITICAL    WAIT    ACTION│
│   ────────── ─────────── ───────────────── ─────────────────── ─────── ──────│
│   PT-94021   45M, Odia   Severe Fever+Rash BP, SpO2, Cap Refill 12m     [OPEN]│
│   PT-94019   62F, Hindi  Chest Tightness   BP, 12-Lead ECG     18m     [OPEN]│
│   PT-94012   12M, Eng    Abdominal Pain    Temp, Guarding Check 25m     [OPEN]│
│                                                                             │
│   SINGLE MASTER CASE MANDATE: All nurse entries append directly to the      │
│   original Master Case. Never create a secondary patient record.            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 14: Staff Missing-Data & Vitals Checklist

### 1. Specification
- **Route:** `/staff/checklist/:id`
- **Purpose:** Frontline structured form for nurses to enter physical vital signs (BP, Pulse, SpO2, Temp, RR) and verify mandatory danger sign checklists.
- **Actor:** Triage Nurse, Community Health Worker.
- **Entry Condition:** Selected case from Screen 13.
- **Inputs:** SBP/DBP (mmHg), Pulse (bpm), SpO2 (%), Resp Rate (/min), Temp (°C), Blood Glucose (mg/dL), Red-flag danger sign checkboxes.
- **Outputs:** Real-time calculated Shock Index ($HR / SBP$) and MEWS score with color indicator.
- **Actions:** "Sign & Save Vitals to Master Case", "Trigger Immediate Red-Flag Bedside Alert".
- **Navigation:** On sign-off, advances to Screen 15.
- **States:**
  - *Abnormal Vitals:* Values out of physiological limits flash amber/red; extreme values require a "Confirm Reading" check.
- **Graph Linkage:** Directly mutates `MasterCase.vitals_series` and updates `CareGraphState`.

### 2. Wireframe (Screen 14)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Point-of-Care Vitals Checklist   [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ACQUIRE MISSING OBJECTIVE VITALS & CONFIRM DANGER SIGNS                   │
│   Patient: 45M | Chief Complaint: Acute Febrile Illness with Petechial Rash │
│                                                                             │
│   [1. Standard Physiological Vitals]                                        │
│   Blood Pressure:   [ 88 ] / [ 60 ] mmHg  ──> ⚠️ HYPOTENSIVE SHOCK RISK     │
│   Heart Rate:       [ 124 ] bpm           ──> ⚠️ SEVERE TACHYCARDIA         │
│   SpO2 (Room Air):  [ 97  ] %             ──> 🟢 Normal                     │
│   Respiratory Rate: [ 24  ] /min          ──> ⚠️ Tachypneic                 │
│   Temperature:      [ 39.2] °C            ──> ⚠️ High Grade Fever           │
│                                                                             │
│   [2. Dengue Red-Flag Checklist]                                            │
│   [X] Persistent Vomiting         [X] Postural Dizziness / Faintness        │
│   [X] Petechiae / Mucosal Bleed   [ ] Abdominal Tenderness                  │
│                                                                             │
│   Auto-Calculated Shock Index: 1.41 (CRITICAL >= 1.0) | MEWS Score: 6       │
│                                                                             │
│   [ 🚨 ESCALATE IMMEDIATELY ]                  [ VERIFY & ATTACH TO CASE ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 15: Consolidated Master Case View

### 1. Specification
- **Route:** `/case/:id/consolidated`
- **Purpose:** Comprehensive synthesized view combining multimodal intake narrative, OCR extractions, timeline, and nurse-verified vitals into an immutable, unified pre-review case file.
- **Actor:** Triage Nurse, Medical Officer.
- **Entry Condition:** Nurse vitals and checklists signed off from Screen 14.
- **Inputs:** None (Read-only consolidation).
- **Outputs:** Unified patient dossier summary, completeness score (100% of critical fields), computed risk band, trajectory arrow.
- **Actions:** "Submit to Doctor Queue", "Print Triage Slip", "Back to Intake".
- **Navigation:** Advances case to Screen 21 (`/doctor/queue`).
- **States:**
  - *Complete:* Green verified seal: "Master Case Consolidated & Ready for Medical Officer Review."
- **Graph Linkage:** Triggers CAREGRAPH compilation and pushes case to Doctor Queue.

### 2. Wireframe (Screen 15)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Consolidated Master Case File    [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CONSOLIDATED CLINICAL DOSSIER [STATUS: INTAKE COMPLETE]                   │
│                                                                             │
│   PATIENT SNAPSHOT: 45-Year-Old Male | Language: Odia | ID: PT-94021        │
│   Encounter: Oct 08, 2026, 10:14 AM | Origin: Capital District Hospital     │
│   Consent: Digital Witnessed [✓] | PII Scrub: Active [✓]                    │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ CLINICAL SUMMARY & RED-FLAG TRAJECTORY:                               │ │
│   │ Patient presents with 4-day acute febrile illness, petechial rash,    │ │
│   │ severe nausea, and postural dizziness. CBC confirms profound          │ │
│   │ thrombocytopenia (Platelets 42,000/μL, TLC 3,400/μL).                 │ │
│   │ Point-of-Care Vitals show decompensated shock: BP 88/60, HR 124,      │ │
│   │ Shock Index 1.41.                                                     │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   Acuity Band: 🔴 EMERGENCY / HIGH PRIORITY | Trajectory: ↘ WORSENING       │
│   Evidence Completeness: 100% Critical Fields Verified | Uncertainty: LOW  │
│                                                                             │
│   [ PRINT TRIAGE SLIP ]                     [ TRANSMIT TO DOCTOR QUEUE ──>] │
└─────────────────────────────────────────────────────────────────────────────┘
```
