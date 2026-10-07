# CLINOVA AI — Post-Doctor Disposition Pathways

> **Document ID:** `DOC-15`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Overview of Post-Doctor Clinical Trajectories

Following the licensed medical officer's comprehensive case review, verification, and sign-off, a patient encounter branches into one of three structured non-emergency disposition pathways:
1. **Pathway A: Routine Home Care & Scheduled Calendar Follow-up** (Recurring monitoring)
2. **Pathway B: Further Review & Single Revisit Scheduler** (Targeted follow-up for pending diagnostics or clinical reassessment)
3. **Pathway C: Urgency / Inpatient Ward Admission** (Formal bed request, staff verification, and SBAR handoff)

All three pathways maintain continuous cryptographic and data linkage to the original **Master Case**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      POST-DOCTOR DISPOSITION PATHWAYS                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                       QUALIFIED CLINICIAN DECISION GATE                     │
│                                       │                                     │
│        ┌──────────────────────────────┼──────────────────────────────┐      │
│        ▼                              ▼                              ▼      │
│  [ PATHWAY A ]                 [ PATHWAY B ]                  [ PATHWAY C ]  │
│  ROUTINE HOME CARE             FURTHER REVIEW                 WARD ADMISSION │
│        │                              │                              │      │
│        ▼                              ▼                              ▼      │
│  • Doctor Finalizes Discharge  • Doctor Finalizes Review Order • Admission Request  │
│  • Home Care Instructions      • Single Next Appointment Date • Past Records Attached│
│  • Recurring Calendar Schedule • Single Revisit Notification  • Medication List      │
│  • Follow-up Reminders         • Patient Revisits Facility    • Bed Assignment Check │
│  • Patient Attends Checkup     • New Diagnostic Data Added    • Staff Verification   │
│  • Clinical Outcome Logged     • Clinical Review & Re-eval    • Two-Party Sign-off   │
│                                • Clinical Outcome Logged      • Ward Handoff Report  │
│                                                               • Final Admission Record│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pathway A: Routine Home Care & Recurring Calendar Follow-Up

### 2.1 Clinical Purpose
For patients with non-emergent, self-limiting illnesses, or stable chronic disease presentations (e.g., uncomplicated viral upper respiratory infection, mild primary hypertension, routine follow-up) who can be safely managed in the community.

### 2.2 Operational Sequence
1. **Doctor Finalization:** Clinician confirms stable vitals, approves discharge medication orders, and selects `ROUTINE_HOME_CARE`.
2. **Patient Discharge Pack Generation:** System compiles the *Routine / Follow-up Report* (Report Type 3) in the patient's preferred language.
3. **Recurring Calendar Scheduling:**
   - Clinician defines the recurring monitoring protocol (e.g., *"Hypertension checkup every 3 months"* or *"Blood glucose log review monthly"*).
   - The system embeds the dates into the hospital outpatient scheduling calendar.
4. **Automated Notification Dispatch:**
   - Patient receives SMS / WhatsApp reminder containing appointment date, room number, and preparation guidelines (e.g., fasting requirement).
5. **Encounter Follow-Up Execution:**
   - Patient attends scheduled review; check-in links to existing Master Case history.
   - Real-world health status is logged, closing the continuous care intelligence loop.

---

## 3. Pathway B: Further Review & Single Revisit Scheduler

### 3.1 Distinct Clinical Purpose
> **Crucial Distinction:** Pathway B is NOT a recurring chronic care checkup.
> It is an episodic clinical pause where the doctor cannot definitively discharge the patient today because critical diagnostic results are pending (e.g., 48-hour blood culture, specialized biopsy, ultrasound scheduled for tomorrow morning), or the patient requires short-interval clinical reassessment (e.g., evaluating abdominal tenderness in 24 hours to rule out acute appendicitis).

### 3.2 Operational Sequence
1. **Doctor Finalization:** Clinician orders specific pending investigations and designates the case as `FURTHER_REVIEW`.
2. **Single Revisit Slot Allocation:**
   - System allocates a targeted single return appointment within a narrow clinical window (e.g., 24 hours, 48 hours, or 5 days).
3. **Single Targeted Notification:**
   - Patient receives a single focused notification: *"Please return to Room 4 on Thursday at 9:00 AM with your Ultrasound Report for Dr. S. Mohapatra."*
4. **Revisitation & Case Continuity:**
   - When the patient arrives, the clinic staff scans their synthetic QR code.
   - The system loads the **SAME Master Case**, displaying previous findings, pending items, and the new investigation results side-by-side.
5. **Reassessment & Final Disposition:**
   - Clinician performs targeted re-evaluation, updates CAREGRAPH, and converts the case to discharge, admission, or referral.
   - Outcome is logged.

---

## 4. Pathway C: Urgency / Inpatient Ward Admission

### 4.1 Clinical Purpose
For acute patients requiring continuous bedside nursing, intravenous therapy, parenteral medications, or close inpatient observation (e.g., moderate pneumonia, acute pyelonephritis, complicated dengue fever without shock).

### 4.2 Operational Sequence
1. **Doctor Admission Request:**
   - Doctor selects `WARD_ADMISSION`.
   - Doctor specifies: Target Service (Internal Medicine, General Surgery, Pediatrics), Ward Name (Male Medical Ward 2), and Clinical Urgency (Immediate / Within 2 hours).
2. **Automated Dossier Assembly:**
   - System automatically aggregates: past medical history, current vitals trend, active medication list, known drug allergies, and mandatory precautions (e.g., Fall Risk, Strict Fluid Restriction, Contact Isolation).
3. **Ward Staff Worklist Notification:**
   - Target ward nursing desk receives an incoming admission alert on the **Staff Admission Workspace**.
4. **Staff Admission Verification:**
   - Ward nurse verifies physical bed availability (e.g., Bed M-14).
   - Ward nurse reviews allergy flags and physician orders.
5. **Structured SBAR Handoff:**
   - Transferring triage nurse escorts patient to the ward.
   - Both staff members complete the digital **Handoff Checklist Screen**:
     - Identity confirmed.
     - Active IV line patent.
     - Vitals stable on arrival.
     - Chart and medication custody transferred.
6. **Ward Admission Report Sign-off:**
   - Both nurses execute digital dual sign-off on the *Ward Admission & Handoff Report* (Report Type 4).
   - Master Case status transitions to `INPATIENT_ADMITTED`.
