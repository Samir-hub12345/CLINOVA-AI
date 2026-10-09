# CLINOVA AI — Operation Theatre (OT) Fast-Track Pathway Specification

> **Document ID:** `RES-70`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Acute Surgical Mandate & Ergonomic Filtering Law

When a patient presents with an acute surgical emergency (e.g., hemoperitoneum secondary to ruptured ectopic pregnancy, acute appendicular peritonitis with perforation, testicular torsion, open compound fracture with arterial compromise, or obstructed labor requiring emergent Cesarean section), clinical survival hinges on the velocity and precision of the surgical team.

CLINOVA AI establishes the **Operation Theatre (OT) Fast-Track Care Pathway**, governed by two absolute architectural laws:

1. **The Ergonomic Information Filtering Law:**  
   > **Architectural Law:** In an acute surgical crisis, the user interface MUST strictly suppress irrelevant outpatient narratives, childhood immunization histories, and non-acute lifestyle text.  
   > An operating surgeon and consultant anesthesiologist preparing for emergency laparotomy require instant, high-contrast access to **procedure-relevant parameters ONLY** (airway status, NPO fasting duration, blood cross-match, anticoagulant therapy, and anesthetic allergies).

2. **The Surgical Human Authorization Monopoly:**  
   > **Safety Guardrail:** Under NO circumstances shall CLINOVA AI autonomously schedule, book, or authorize an invasive surgical procedure.  
   > The initiation of the OT Pathway requires explicit digital authorization by a credentialed surgeon (`ROLE_CLINICIAN`), corroborated by dual-party sign-off under the WHO Surgical Safety Checklist.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OPERATION THEATRE (OT) PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1 ] EMERGENCY PROCEDURE NEED IDENTIFIED                             │
│       │     (Surgeon identifies surgical indication on Doctor Workbench)    │
│       ▼                                                                     │
│  [ STEP 2 ] PROCEDURE-RELEVANT SURGICAL DOSSIER ASSEMBLY                    │
│       │     (Airway, NPO status, cross-match, coagulation, consent)         │
│       ▼                                                                     │
│  [ STEP 3 ] STAT INVESTIGATIONS & BLOOD BANK AUDIT                          │
│       │     (Blood group, hemoglobin, platelet count, PRBC hold check)      │
│       ▼                                                                     │
│  [ STEP 4 ] WHO SURGICAL SAFETY CHECKLIST — "SIGN IN"                       │
│       │     (Patient identity, surgical site marking, allergy check)        │
│       ▼                                                                     │
│  [ STEP 5 ] OT THEATRE & SCRUB TEAM HANDOFF                                 │
│       │     (Dual sign-off: Transferring doctor + Scrub nurse / Anesthetist)│
│       ▼                                                                     │
│  [ STEP 6 ] INTRA-OPERATIVE SURGICAL PHASE                                  │
│       │     (Time Out prior to incision; Sign Out prior to closure)         │
│       ▼                                                                     │
│  [ STEP 7 ] OT OPERATIVE REPORT GENERATION (Report Type 6)                  │
│       │     (Findings, implants, blood loss, post-op destination)           │
│       ▼                                                                     │
│  [ STEP 8 ] SURGICAL OUTCOME RECORDING & RECOVERY HANDOFF                   │
│       │     (Transfer to PACU or Surgical ICU; telemetry logged)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step OT Pathway Execution

### Step 1: Emergency Procedure Need Identified
- **Actor:** Attending Surgeon / Obstetrician (`ROLE_CLINICIAN`).
- **Data State:** `STATE_ORCHESTRATION_PENDING` $\to$ `STATE_OT_PENDING`.
- **System Action:**
  - Clinician selects `PROCEDURE_OT_PATHWAY`.
  - Enters mandatory procedure metadata:
    - *Procedure Code / Description:* e.g., Emergency Exploratory Laparotomy / Cesarean Section.
    - *Surgical Urgency:* Immediate / Crash ($< 15$ mins) vs Urgent ($< 2$ hours).
    - *Primary Surgical Indication:* e.g., Ruptured Ectopic Pregnancy with Hemoperitoneum.

### Step 2: Procedure-Relevant Surgical Dossier Assembly
- **Engine:** Filters out general outpatient fluff and renders the high-contrast **Pre-Op Surgical HUD**:
  1. *Fasting / NPO Status:* Exact timestamp of last solid food and liquid ingestion (e.g., *"NPO since 6 hours"* vs *"Full stomach — Rapid Sequence Induction mandatory"*).
  2. *Airway Assessment (Mallampati Score):* Class I–IV, neck mobility, mouth opening, loose teeth, facial hair.
  3. *Hemostasis & Anticoagulant Status:* Platelet count, Prothrombin Time / INR, active antiplatelet/anticoagulant drugs (Aspirin, Clopidogrel, Warfarin).
  4. *Informed Surgical & Anesthetic Consent:* Signed digital or witnessed physical consent form.
  5. *Critical Allergies:* Penicillin, latex, intravenous contrast, muscle relaxants.

### Step 3: STAT Investigations & Blood Bank Allocation
- **Engine:** $\text{FACILITYGRAPH}$ audits on-site blood bank and stat lab:
  - Verifies ABO/Rh blood grouping and antibody screen.
  - Checks compatibility hold for Packed Red Blood Cells (PRBC) and Fresh Frozen Plasma (FFP).
  - Emits STAT alert to blood bank: *"Release 2 Units O-Negative PRBC to OT-1 for PT-59120."*

### Step 4: WHO Surgical Safety Checklist — Phase 1: "Sign In"
- **Timing:** Administered in the OT holding area before induction of anesthesia.
- **Participants:** Anesthesiologist, Holding Nurse, and Patient (if conscious).
- **Mandatory Verification Gates:**
  - Patient identity confirmed via synthetic wristband barcode and verbal confirmation.
  - Surgical site explicitly marked with permanent surgical marker (or marked "N/A" for midline laparotomy).
  - Anesthesia machine and medication safety check completed.
  - Pulse oximeter on patient and functioning.
  - Known allergy status confirmed.
  - Difficult airway / aspiration risk evaluated (equipment available).
  - Risk of blood loss $> 500\text{mL}$ evaluated ($> 7\text{mL/kg}$ in children) and 2 large-bore IVs confirmed.

### Step 5: OT Theatre & Scrub Team Handoff
- **Actors:**
  1. Transferring Clinician / Casualty Team.
  2. Receiving Scrub Nurse & Consultant Anesthesiologist (`ROLE_CLINICIAN` / `ROLE_NURSE`).
- **Data State:** `STATE_OT_PENDING` $\to$ `STATE_OT_HANDOFF`.
- **System Action:**
  - Dual electronic sign-off executed.
  - Patient physically rolled into Operation Theatre Room (e.g., `OT_THEATRE_02`).
  - Master Case timestamps the formal transfer of intra-operative custody.

### Step 6: Intra-Operative Execution (Time Out & Sign Out)
- **Phase 2: "Time Out" (Immediately before skin incision):**
  - Scrub team introduces themselves by name and role.
  - Surgeon states: Procedure name, anticipated critical steps, operative duration, expected blood loss.
  - Anesthesiologist states: Patient-specific concerns (hemodynamic instability, inotropic support).
  - Nursing team states: Sterility confirmation, instrument availability.
  - Antibiotic prophylaxis confirmed administered within past 60 minutes.
- **Phase 3: "Sign Out" (Before patient leaves operating room):**
  - Nurse verbally confirms: Instrument, sponge, and needle counts correct.
  - Surgical specimens labeled correctly.
  - Any equipment malfunctions flagged.
  - Surgeon and anesthesiologist review post-operative recovery and management plan.

### Step 7: OT Operative Report Generation (Report Type 6)
- **Artifact:** Operating surgeon signs off the **Operative Procedure Report (`Report Type 6`)**:
  - Detailed operative narrative: Findings, surgical technique, tissue resections, implants placed.
  - Estimated blood loss (EBL in mL) and intra-operative transfusions given.
  - Post-operative disposition order: Transfer to Post-Anesthesia Care Unit (PACU) or Surgical Intensive Care Unit (SICU).
  - Post-op analgesia, thromboprophylaxis, and fluid titration orders.

### Step 8: Surgical Outcome Recording & Recovery Handoff
- **Data State:** `STATE_OUTCOME_PENDING` $\to$ `STATE_RESOLVED`.
- **System Action:**
  - Patient safely transferred to recovery unit; receiving PACU nurse acknowledges intake.
  - Master Case updates surgical milestone.
  - Operative duration, blood loss, and intra-op complication metrics feed $\text{SIGNALGRAPH}$ surgical quality registry.
