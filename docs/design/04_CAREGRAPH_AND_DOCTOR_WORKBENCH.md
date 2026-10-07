# CLINOVA AI — Design Specifications: Cluster 4 (CAREGRAPH & Doctor Review Workbench)

> **File:** `docs/design/04_CAREGRAPH_AND_DOCTOR_WORKBENCH.md`  
> **Screens Covered:** Screens 16 through 23  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 16: CAREGRAPH Interactive Patient State View

### 1. Specification
- **Route:** `/case/:id/caregraph`
- **Purpose:** Interactive clinical state engine visualization answering *"What is happening to this patient right now?"*.
- **Actor:** Medical Officer, Clinical Reviewer, Emergency Registrar.
- **Entry Condition:** Master Case consolidated.
- **Inputs:** Interactive node selector (click nodes for evidence provenance), zoom controls.
- **Outputs:** Visual rendering of current physiological state, syndromic cluster, longitudinal trajectory arrow, and uncertainty indicators.
- **Actions:** "Inspect Node Provenance", "Filter by Organ System", "Jump to Doctor Workbench".
- **Navigation:** Links to Screens 17, 18, 22.
- **States:**
  - *Normal:* Organized clinical network with state transitions, verified parameters in green, unverified inferences in dotted amber, and red-flag alerts in pulsing crimson.
- **Graph Linkage:** Direct interactive visual projection of `CareGraphState`.

### 2. Wireframe (Screen 16)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       CAREGRAPH Engine Visualizer      [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CAREGRAPH: ACTIVE PHYSIOLOGICAL & SYNDROMIC STATE                         │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ CURRENT SYNDROME: ACUTE FEBRILE ILLNESS WITH THROMBOCYTOPENIA & SHOCK │ │
│   │ Acuity: 🔴 RED (Emergency) | Trajectory: ↘ WORSENING | Shock Idx: 1.41│ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│     [ FEVER (39.2°C) ] ───────> [ THROMBOCYTOPENIA ] ──────> [ PETECHIAE ]  │
│        (Source: Desk)              (42,000 /μL - OCR)          (Forearms)   │
│              │                            │                                 │
│              ▼                            ▼                                 │
│     [ TACHYCARDIA (124 bpm) ] ──> [ HYPOTENSION (88/60) ] ──> [ SHOCK STATE]│
│        (Verified Nurse)             (Hypovolemic / Dengue)      (ALERT!)    │
│                                                                             │
│   NODE INSPECTOR: Click any parameter node to view source document and actor│
│                                                                             │
│   [ VIEW RISK TRAJECTORY ]                   [ OPEN DOCTOR CASE OVERVIEW ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 17: Risk & Acuity Trajectory Monitor

### 1. Specification
- **Route:** `/case/:id/trajectory`
- **Purpose:** Monitor serial vital sign trends over time, calculate rate-of-change ($\Delta \text{Vitals} / \Delta t$), and enforce the explainable risk tuple.
- **Actor:** Medical Officer, Triage Nurse.
- **Entry Condition:** At least one vital snapshot present in Master Case.
- **Inputs:** Time-interval selector (15m, 30m, 1h, 4h).
- **Outputs:** Longitudinal line charts for BP, HR, SpO2; explainable risk card with the 6-part tuple (Risk, Reason, Evidence, Trajectory, Uncertainty, Next Action).
- **Actions:** "Record Repeat Vitals", "Acknowledge Worsening Alarm", "Proceed to Doctor Overview".
- **Navigation:** Links to Screens 14, 22.
- **Graph Linkage:** Binds to `CareGraphState.trajectory` and `CareGraphState.risk_level`.

### 2. Wireframe (Screen 17)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Risk & Trajectory Monitor        [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PHYSIOLOGICAL TRAJECTORY & RISK STRATIFICATION                            │
│                                                                             │
│   Pulse Rate (bpm):     98 (10:00 AM) ──> 112 (10:20 AM) ──> 124 (10:45 AM)  │
│   Systolic BP (mmHg):  110 (10:00 AM) ──>  96 (10:20 AM) ──>  88 (10:45 AM)  │
│   Shock Index:        0.89 (Normal)   ──> 1.16 (Elevated)──> 1.41 (CRITICAL)│
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ EXPLAINABLE RISK TUPLE                                                │ │
│   │ • CURRENT RISK: 🔴 EMERGENCY / HIGH PRIORITY                          │ │
│   │ • REASON: Narrowing pulse pressure, tachycardia, severe thrombocytop. │ │
│   │ • EVIDENCE: Nurse auscultation (10:45), District Lab CBC slip [✓]     │ │
│   │ • TRAJECTORY: ↘ WORSENING (Decompensating hemodynamics over 45 mins)  │ │
│   │ • UNCERTAINTY: LOW (0.12 — All critical shock parameters verified)    │ │
│   │ • NEXT ACTION: Immediate IV fluid resuscitation & Dengue protocol     │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   [ RECORD REPEAT VITALS ]                     [ DOCTOR REVIEW WORKBENCH ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 18: Uncertainty & Evidence Provenance Inspector

### 1. Specification
- **Route:** `/case/:id/evidence`
- **Purpose:** Deep clinical audit of data quality, showing exact provenance for every parameter, why uncertainty exists, and what would reduce it.
- **Actor:** Medical Officer, Clinical Auditor.
- **Entry Condition:** Master Case loaded.
- **Inputs:** Filter by status (`KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`).
- **Outputs:** Provenance matrix showing parameter name, extracted value, source modality, timestamp, responsible actor, and confidence score.
- **Actions:** "Re-evaluate Uncertainty", "Resolve Conflict", "Override Confidence".
- **Navigation:** Returns to Screen 22.
- **Graph Linkage:** Direct view of `EvidenceNode` table and `CareGraph.uncertainty_vector`.

### 2. Wireframe (Screen 18)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Evidence Provenance & Gaps       [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   EVIDENCE PROVENANCE LEDGER & UNCERTAINTY PROFILE                          │
│                                                                             │
│   PARAMETER    VALUE    SOURCE    CONF. VERIFIED BY       AUDIT TRAIL / SNIP│
│   ──────────── ──────── ───────── ───── ───────────────── ──────────────────│
│   Platelets    42,000   OCR Lab   96%   Dr. S. Mohapatra  [📄 cbc_scan.jpg] │
│   Systolic BP  88 mmHg  Nurse Desk100%  Sister S. Nayak   [✓ Digital Cuff]  │
│   Heart Rate   124 bpm  Nurse Desk100%  Sister S. Nayak   [✓ Palpated Radial│
│   Symptom Onset4 Days   Voice STT 98%   Patient Self-rep. [🔊 audio_01.wav] │
│                                                                             │
│   RESOLVED CONFLICTS:                                                       │
│   • Fever Duration: Resolved to 4 days acute exacerbation by Dr. Mohapatra  │
│     (Previous prescription was for unrelated dental pain 10 days ago).      │
│                                                                             │
│   [ CLOSE INSPECTOR ]                          [ RETURN TO DOCTOR OVERVIEW] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 19: Structured Triage Note Editor

### 1. Specification
- **Route:** `/case/:id/triage-note`
- **Purpose:** Review, edit, and finalize the structured clinical triage note drafted by local Qwen3-4B. Rejects unstructured walls of text.
- **Actor:** Medical Officer.
- **Entry Condition:** Doctor review in progress.
- **Inputs:** Editable rich-text sections for Subjective, Objective, Assessment, Plan.
- **Outputs:** Formatted clinical note adhering to clinical documentation standards.
- **Actions:** "Accept AI Draft", "Regenerate with New Findings", "Save & Sign Note".
- **Navigation:** Saves to Master Case; returns to Screen 22.
- **Graph Linkage:** Commits signed text to `MasterCase.doctor_triage_notes`.

### 2. Wireframe (Screen 19)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Structured Triage Note Editor    [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STRUCTURED CLINICAL TRIAGE NOTE (NON-DIAGNOSTIC ADVISORY DRAFT)           │
│                                                                             │
│   SUBJECTIVE (Patient History & Timeline):                                  │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ 45yo male presents with 4-day high-grade fever, nausea, and petechial  │ │
│   │ rash on forearms. Complains of lightheadedness upon standing.          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   OBJECTIVE (Verified Vitals & Laboratory Findings):                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ Vitals: BP 88/60, HR 124, SpO2 97%, RR 24, Temp 39.2°C. Shock Idx: 1.41│ │
│   │ Labs: Platelets 42,000/μL, TLC 3,400/μL, Hematocrit 48% (Hemoconcentr)│ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   ASSESSMENT & PLAN:                                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ High-risk acute febrile illness with severe thrombocytopenia and early │ │
│   │ hypotensive shock (Dengue Shock Syndrome Suspect). STAT IV fluids.    │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   [ DISCARD CHANGES ]                          [ SIGN & ATTACH NOTE [✓] ]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 20: Master Clinical Report

### 1. Specification
- **Route:** `/case/:id/master-report`
- **Purpose:** Definitive comprehensive triage document derived from Master Case.
- **Actor:** Medical Officer, Auditor, Referral Desk.
- **Entry Condition:** Case finalized or under formal review.
- **Inputs:** None (Read-only formatted document).
- **Outputs:** Complete multi-section A4 clinical dossier with provenance QR code.
- **Actions:** "View On-Screen", "Download PDF", "Print (A4 / Thermal CSS)".
- **Navigation:** Returns to Screen 22.
- **Graph Linkage:** Dynamic rendering of complete Master Case state.

### 2. Wireframe (Screen 20)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Master Clinical Triage Report    [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│  [ 🖨️ PRINT REPORT ]      [ 📥 DOWNLOAD PDF ]           [ < BACK TO CASE ]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CLINOVA AI — COMPREHENSIVE CLINICAL TRIAGE REPORT                         │
│   Facility: Capital District Hospital | Date: 08-Oct-2026 | ID: PT-94021    │
│   ────────────────────────────────────────────────────────────────────────  │
│   PATIENT: 45M | Consent: Witnessed [✓] | Reviewer: Dr. S. Mohapatra, MO    │
│   RISK BAND: 🔴 EMERGENCY / RED FLAG | TRAJECTORY: ↘ WORSENING              │
│                                                                             │
│   1. CHIEF COMPLAINT: Acute Febrile Illness (4 days) with Petechial Rash    │
│   2. VERIFIED VITALS: BP 88/60, HR 124, SpO2 97%, RR 24, Temp 39.2°C       │
│   3. LAB EXTRACTIONS: Platelets 42,000/μL (CBC OCR [✓]), TLC 3,400/μL      │
│   4. CAREGRAPH SUMMARY: Hypovolemic/Dengue Shock with hemoconcentration     │
│   5. EVIDENCE AUDIT: 100% Critical Fields Verified | Zero Unresolved Gaps   │
│   6. FINAL DISPOSITION: ADMIT TO RESUSCITATION BAY / PREPARE HDU TRANSFER   │
│                                                                             │
│   Digital Signature: Dr. S. Mohapatra, MD [VERIFIED 10:48 AM UTC]           │
│   QR Code: [▓▓▓▓▓] (Cryptographically links to immutable audit record)      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Educational Prototype Only | Non-Diagnostic | Qualified Human Gate Enforced│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 21: Doctor Prioritized Queue

### 1. Specification
- **Route:** `/doctor/queue`
- **Purpose:** Dynamic, prioritized clinical queue ranking waiting patients based on composite risk, physiological trajectory, and wait duration.
- **Actor:** Medical Officer, Senior Resident, Triage Registrar.
- **Entry Condition:** Authenticated doctor session.
- **Inputs:** Filter by Risk Band (Red/Amber/Yellow/Green), search by ID, sort toggle.
- **Outputs:** Prioritized table with urgency badges, trajectory arrows, patient age/gender, wait timer, and red-flag callouts.
- **Actions:** "Review Case" (routes to Screen 22), "Quick Vitals Inspect", "Trigger Transfer".
- **Navigation:** Advances to Screen 22.
- **States:**
  - *Dynamic Jump:* When a nurse enters abnormal vitals on Screen 14, the case automatically jumps to the pinned top of the queue with an audible chime and amber flashing border.
- **Graph Linkage:** Ordered by `QueueOrderVector` computed from CAREGRAPH.

### 2. Wireframe (Screen 21)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Doctor Clinical Queue            [ DR. MOHAPATRA ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PRIORITIZED CLINICAL QUEUE [7 PATIENTS WAITING]                           │
│   Filters: [ All ] [ 🔴 Red (2) ] [ 🟠 Amber (3) ] [ 🟢 Routine (2) ]       │
│                                                                             │
│   PRIORITY  CASE ID   PATIENT   PRESENTATION       TRAJECTORY  WAIT  ACTION │
│   ───────── ───────── ───────── ────────────────── ─────────── ───── ───────│
│   🔴 P1-EMG PT-94021  45M, Odia Fever, Shock, Rash ↘ WORSENING 14m   [REVIEW│
│   🔴 P1-EMG PT-94019  62F, Hin  Chest Tightness    ↘ WORSENING 22m   [REVIEW│
│   🟠 P2-URG PT-94012  12M, Eng  Acute Abdomen      → STABLE    34m   [REVIEW│
│   🟠 P2-URG PT-94008  28F, Odia Post-partum Bleed  → STABLE    41m   [REVIEW│
│   🟢 P3-ROU PT-94002  34M, Hin  Mild Cough / Cold  ↗ IMPROVING 58m   [REVIEW│
│                                                                             │
│   Auto-Refresh Active (Every 15s) | Decompensating cases auto-elevate to top│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 22: Doctor Comprehensive Case Overview

### 1. Specification
- **Route:** `/doctor/case/:id`
- **Purpose:** The primary clinical review workstation. Allows the physician to understand the complete patient state, inspect timeline, review CAREGRAPH, and examine facility feasibility on a single unified screen without navigating away.
- **Actor:** Medical Officer.
- **Entry Condition:** Selected case from Screen 21.
- **Inputs:** Tab navigation (Overview / CareGraph / Evidence / Triage Note / Feasibility).
- **Outputs:** Complete 3-column clinical layout: Left = Patient snapshot & Vitals; Center = CAREGRAPH & Timeline; Right = Orchestration guidance & Disposition buttons.
- **Actions:** "Verify / Modify Data" (Screen 23), "Open Master Report" (Screen 20), "Approve Care Pathway" (Screen 26).
- **Navigation:** Links to Screens 20, 23, 24, 26.
- **Graph Linkage:** Primary unified workstation reading all four graphs.

### 2. Wireframe (Screen 22)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Doctor Case Overview             [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│  PT-94021 | 45M, Odia | Acuity: 🔴 EMERGENCY | Trajectory: ↘ WORSENING      │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  COLUMN 1: PATIENT & VITALS          │  COLUMN 2: CAREGRAPH & TIMELINE      │
│  • BP: 88/60 mmHg (Hypotension [✓])  │  • Current State: Dengue Shock Suspect│
│  • Pulse: 124 bpm (Tachycardia [✓])  │  • Timeline: 4-day fever ──> rash ──>│
│  • SpO2: 97% | Temp: 39.2°C          │    decompensated vitals this AM      │
│  • Platelets: 42,000/μL (CBC OCR [✓])│  • Evidence: 100% Verified [✓]       │
│  • Shock Index: 1.41 (CRITICAL)      │  • Uncertainty: LOW (0.12)           │
│                                      │                                      │
│  [ VERIFY / MODIFY / ADD DATA ]      │  [ INSPECT EVIDENCE PROVENANCE ]     │
├──────────────────────────────────────┴──────────────────────────────────────┤
│  COLUMN 3: ORCHESTRATION ADVISORY & FACILITY FEASIBILITY                    │
│  • Recommended Action: ESCALATE TO RESUSCITATION BAY & STAT IV CRYSTALLOIDS │
│  • Local Facility Feasibility: ⚠️ SUITABLE FOR INITIAL STABILIZATION ONLY   │
│    (Capital Hospital has zero open HDU/ICU beds; prepare referral standby) │
│                                                                             │
│  [ EXECUTE RESUSCITATION PATHWAY ]  [ PREPARE TERTIARY REFERRAL ]  [ MORE ]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 23: Doctor Verify / Modify / Add Audit Workspace

### 1. Specification
- **Route:** `/doctor/case/:id/audit`
- **Purpose:** Interactive clinical modification workspace where the doctor explicitly verifies, corrects, or supplements discrete data points with required audit justifications. Rejects unverified AI output.
- **Actor:** Medical Officer.
- **Entry Condition:** Doctor review in progress.
- **Inputs:** Editable numerical fields, examination findings text, modification reason dropdown (`Correction of Extraction`, `New Bedside Examination`, `Patient Clarification`).
- **Outputs:** Audit diff showing original value vs. modified value.
- **Actions:** "Verify As Correct", "Commit Clinical Modification", "Add Physical Exam Note", "Cancel".
- **Navigation:** Returns to Screen 22 with updated CAREGRAPH state.
- **Graph Linkage:** Commits to `MasterCase.clinician_review.verification_actions` and logs `AuditEvent`.

### 2. Wireframe (Screen 23)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Clinical Verification & Override [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   DOCTOR CLINICAL VERIFICATION WORKSPACE                                    │
│   All modifications are permanently logged to the immutable audit ledger.   │
│                                                                             │
│   FIELD            EXTRACTED VALUE   DOCTOR MODIFICATION  AUDIT REASON      │
│   ──────────────── ───────────────── ─────────────────── ───────────────────│
│   Systolic BP      88 mmHg           [ 88 ] mmHg [✓ VER]  Confirmed manual  │
│   Fever Duration   10 Days (Slip)    [ 4  ] Days [✓ MOD]  Patient clarified │
│   Abdominal Exam   Unassessed        [ Soft, Epigastric ] New Exam Finding  │
│                                        Tenderness (+)                       │
│                                                                             │
│   Audit Justification Note:                                                 │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ Repeat bedside examination confirms narrow pulse pressure and epigastric│ │
│   │ tenderness. Patient clarifies acute fever began 4 days ago.          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   [ CANCEL ]                                   [ COMMIT VERIFICATION [✓] ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```
