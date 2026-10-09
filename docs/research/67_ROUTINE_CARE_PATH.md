# CLINOVA AI — Routine Care & Further Review Pathways Specification

> **Document ID:** `RES-67`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & Clinical Scope

Following clinical review, verified physical examination, and diagnostic synthesis, the vast majority of outpatient encounters ($70–85\%$) do not require acute inpatient admission or emergency surgical intervention.

CLINOVA AI models two distinct, non-emergent ambulatory care trajectories:
- **Pathway A: Routine Home Care & Recurring Calendar Follow-Up** (Chronic disease monitoring & self-limiting acute illnesses).
- **Pathway B: Further Review & Single Revisit Scheduler** (Short-interval clinical reassessment or pending laboratory result review).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TWO DISTINCT AMBULATORY CARE BRANCHES                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                       QUALIFIED CLINICIAN DECISION                          │
│                                     │                                       │
│                  ┌──────────────────┴──────────────────┐                    │
│                  ▼                                     ▼                    │
│       [ PATHWAY A: ROUTINE CARE ]           [ PATHWAY B: FURTHER REVIEW ]   │
│       • Full discharge from active episode  • Active episode held in pause │
│       • Prescriptions finalized             • Diagnostics pending           │
│       • Recurring calendar schedule         • Single targeted revisit slot  │
│       • Automated wellness reminders        • Focused clinical re-eval      │
│       • Outcome tracking at milestone       • Final disposition determined  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Essential Clinical Distinction

| Operational Dimension | Pathway A: Routine Home Care | Pathway B: Further Review |
| :--- | :--- | :--- |
| **Clinical Purpose** | Discharge for home recovery or routine chronic disease monitoring. | Targeted clinical reassessment or review of pending investigations. |
| **Clinical Examples** | Uncomplicated viral pharyngitis, stable primary hypertension (3-month refill), osteoarthritis knee. | Acute abdominal pain (rule out appendicitis in 24h), pending 48h blood culture, thyroid biopsy review. |
| **Episode Status** | **DISCHARGED** (Episode completed; moved to scheduled follow-up). | **PAUSED / ACTIVE** (Episode incomplete; awaiting definitive results). |
| **Revisit Structure** | Recurring cyclical schedule (e.g., every 3 months or as needed). | **Single specific return appointment slot** within a narrow window ($\le 7$ days). |
| **Notification Content** | "Take your medications as directed. Your next routine refill is in 90 days." | "Return to Room 4 on Thursday at 9:00 AM with your Ultrasound Report." |
| **Case Model Action** | Generates Report Type 3 (Routine Pack); schedules calendar. | Retains open investigative order on Master Case; sets alert beacon. |

---

## 3. Pathway A: Routine Home Care & Recurring Calendar Follow-Up

### Step A.1: Doctor Disposition Finalization
- **Actor:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Data State:** `STATE_ROUTINE_CARE`.
- **System Action:**
  - Clinician approves final diagnosis and signs outpatient e-prescription.
  - System executes automated safety audits: Drug-allergy check, drug-drug interaction check, age/weight dose validation.
  - Generates the **Routine / Follow-Up Pack (Report Type 3)** in the patient's preferred language (Odia, Hindi, English).

### Step A.2: Outpatient Discharge Dossier & Patient Education
- **Content of Report Type 3:**
  - Prescribed medications with iconographic timing aids (morning, afternoon, night, before/after meals).
  - Clear, vernacular "Red Flag Return Warnings" (*"Return immediately to Casualty if: High fever $> 103^\circ\text{F}$, breathlessness, inability to drink fluids"*).
  - Dietary and self-care lifestyle instructions.

### Step A.3: Recurring Calendar Follow-Up Scheduling
- **Engine:** Outpatient Scheduling Engine embeds planned checkup dates into the facility outpatient calendar:
  - Supports chronic care intervals: 1 month (Diabetes titration), 3 months (Hypertension), 6 months (Annual wellness).
  - Integrates with public health registries (e.g., NCD portal for hypertension/diabetes tracking).

### Step A.4: Automated Omnichannel Notification Dispatch
- **Delivery:** Sends automated reminders via SMS, WhatsApp, or IVR voice call:
  - *Initial SMS (Day 0):* Summary of prescription and download link for digital discharge slip.
  - *Reminder SMS (T - 2 Days):* Appointment reminder with date, room number, and preparation requirements (e.g., 12-hour fasting for blood glucose).

### Step A.5: Milestone Outcome Recording & Telemetry
- **Resolution:**
  - When the patient attends the routine check-up, the check-in desk scans the synthetic QR code, linking directly to the existing Master Case history.
  - If patient does not attend, automated SMS inquires about wellness: *"Are your symptoms resolved? Reply 1 for Yes, 2 for No."*
  - Responses update the Master Case outcome field (`FULL_RECOVERY` or `STABILIZED`), closing the learning loop.

---

## 4. Pathway B: Further Review & Single Revisit Scheduler

### Step B.1: Distinct Clinical Intent & Investigation Order
- **Actor:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Data State:** `STATE_FURTHER_REVIEW`.
- **System Action:**
  - Clinician determines that definitive diagnosis or safe discharge is impossible today because critical investigations are pending (e.g., USG Abdomen scheduled for tomorrow morning, 48-hour microbial culture, histopathology report).
  - Clinician orders specific pending tests and selects `FURTHER_REVIEW`.

### Step B.2: Single Targeted Revisit Slot Allocation
- **Scheduling Rules:**
  - The system allocates a **single, non-recurring appointment slot** within a clinically determined window (24 hours, 48 hours, or up to 7 days).
  - Hard limit: Revisit window cannot exceed 7 days; cases beyond 7 days must be routed to Routine Discharge or Ward Admission.

### Step B.3: Single Focused Patient Notification
- **Dispatch:** Patient receives a targeted SMS/WhatsApp notification:
  > *"CLINOVA Health Alert: Please collect your Ultrasound Report from Room 12 and return to Room 4 to see Dr. S. Mohapatra on Thursday, Oct 10 at 9:30 AM."*

### Step B.4: Revisit Physical Check-in & Master Case Continuity
- **Mandatory Invariant:** **THE CLINICIAN MUST RESUME THE SAME MASTER CASE.**
- **Operational Execution:**
  - Patient returns to facility; triage desk scans synthetic QR code.
  - The system loads `case_id`, displaying the **Split Comparative View**:
    - *Left Panel:* Initial presentation findings, baseline vitals, and physician notes from Day 1.
    - *Right Panel:* Newly attached diagnostic lab reports, updated physical exam findings, and current vitals.

### Step B.5: Differential Adjudication & Definitive Disposition
- **Clinical Review:**
  - Clinician examines the newly arrived report.
  - CAREGRAPH recalculates trajectory with the new evidence.
  - Clinician converts the case into a final disposition:
    - *Scenario 1 (Normal findings):* Patient converted to `STATE_ROUTINE_CARE` and discharged.
    - *Scenario 2 (Acute findings, e.g., acute appendicitis on USG):* Patient converted to `STATE_OT_PENDING` or `STATE_WARD_REQUESTED`.
    - *Scenario 3 (Complex disease):* Patient referred to higher tertiary center (`STATE_REFERRAL_PENDING`).
  - Definitive clinical outcome is logged, completing the episode.
