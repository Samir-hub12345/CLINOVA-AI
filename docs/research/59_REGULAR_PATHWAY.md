# CLINOVA AI — Regular Master Care Pathway Specification

> **Document ID:** `RES-59`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & Clinical Scope

The **Regular Master Care Pathway** models the complete trajectory for non-emergent, elective, outpatient, and ambulatory patient encounters. It governs walk-in presentations, primary health centre consultations, public health camp screenings, and planned revisits.

The pathway systematically transforms unstructured multimodal patient inputs (regional vernacular voice, handwritten clinic slips, printed lab reports, and typed narratives) into a highly structured, uncertainty-quantified, and clinician-verified Master Clinical Dossier.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REGULAR MASTER CARE PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1 ] NEW ENCOUNTER & CONSENT                                         │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 2 ] MULTIMODAL INGESTION (Voice, Free-Text, OCR Uploads)            │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 3 ] LOCAL EXTRACTION & ENTITY NORMALIZATION                         │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 4 ] VISUAL EXTRACTION REVIEW (Snippet, Confidence, Provenance)      │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 5 ] CHRONOLOGICAL TIMELINE SYNTHESIS                                │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 6 ] MISSING INFORMATION AUDIT (Known, Unknown, Conflicting)         │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 7 ] TARGETED FOLLOW-UP QUESTION ENGINE                              │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 8 ] MATHEMATICAL SUFFICIENCY GATE ($S \ge 0.85$)                    │
│       ├── Sufficient ──────────────┐                                        │
│       ▼                            ▼                                        │
│  Insufficient              DATA CONSOLIDATION                               │
│       │                            │                                        │
│       ▼                            │                                        │
│  [ STEP 9 ] STAFF WORKLIST         │                                        │
│  Point-of-Care Vitals & Checklist  │                                        │
│       │                            │                                        │
│       ▼                            │                                        │
│  Staff Verification                │                                        │
│       │                            │                                        │
│       └────────────────────────────┘                                        │
│                                    │                                        │
│                                    ▼                                        │
│  [ STEP 10 ] CAREGRAPH ENGINE (Risk, Trajectory, Uncertainty, NBI)          │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 11 ] STRUCTURED TRIAGE NOTE & MASTER CLINICAL REPORT                │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 12 ] DYNAMIC DOCTOR QUEUE (Priority Vector)                         │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 13 ] DOCTOR WORKBENCH (Comprehensive Multi-Panel View)              │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 14 ] CLINICAL ACTION GATE (VERIFY / MODIFY / ADD)                   │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 15 ] FACILITYGRAPH CAPABILITY & CARE FEASIBILITY                    │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 16 ] ORCHESTRATION ADVISORY RECOMMENDATION                          │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 17 ] CLINICIAN DISPOSITION SELECTION                                │
│       ├── Branch A: Routine Home Care & Follow-Up Calendar                  │
│       ├── Branch B: Further Review & Single Revisit Slot                    │
│       ├── Branch C: Inpatient Ward Admission                                │
│       ├── Branch D: Inter-Facility Referral & Transfer                      │
│       ├── Branch E: Dynamic Emergency Escalation                            │
│       └── Branch F: Operation Theatre (OT) Fast-Track                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step Pathway Execution

### Step 1: New Encounter Creation & Consent Gate
- **Actor:** Patient, Caregiver, or Registration Desk Clerk (`ROLE_ADMIN` / `ROLE_HEALTH_WORKER`).
- **Data State:** `STATE_NEW` $\to$ `STATE_INTAKE_COLLECTING`.
- **System Action:**
  - Instantiates a new globally unique Master Case (`case_id: UUIDv4`).
  - Generates an anonymous synthetic identifier (`PT-XXXXXX`).
  - Records DPDP-compliant explicit consent (`VERBAL_WITNESSED`, `DIGITAL_SIGNATURE`, or `GUARDIAN_CONSENT`).
  - Captures demographic basics: age, gender, preferred language (Odia, Hindi, English).
- **Safety Gate:** If consent is withheld, non-emergency processing aborts; encounter cannot be stored.

### Step 2: Multimodal Information Ingestion
- **Input Modalities:**
  1. *Vernacular Voice Audio:* Frontline speech in native dialect captured via microphone (16kHz PCM).
  2. *Free-Text Narrative:* Symptoms entered by patient or typist.
  3. *Document / Image Files:* Mobile phone camera photo or scanner upload of prior prescriptions, discharge summaries, or printed lab slips.
- **Data State:** Appends raw files to `MasterCase.multimodal_inputs`.
- **Safety Gate:** File virus scan, file size limits ($\le 15\text{MB}$), and format validation (JPEG, PNG, PDF, WAV).

### Step 3: Local Extraction & Entity Structuring
- **Engine:** On-device / local server edge processing using quantized Faster-Whisper, PaddleOCR / Tesseract, and deterministic rule engines.
- **Extracted Schema:**
  - `symptoms`: Canonical term, anatomical site, onset date, duration, severity scale (1–10).
  - `vital_signs`: Physiological metrics with standardized units (mmHg, %, bpm, °F).
  - `medications`: Drug name, dosage, frequency, route, duration.
  - `allergies`: Specific allergen, reaction severity.
  - `comorbidities`: Prior diagnosed conditions (e.g., Type 2 Diabetes, Hypertension).
- **Data State:** `STATE_EXTRACTING`.

### Step 4: Visual Extraction Review
- **Actor:** Patient, ASHA, or Frontline Staff.
- **Interface Behavior:** High-transparency side-by-side inspection layout:
  - Displays the extracted structured entity immediately adjacent to the raw image crop or audio transcript snippet.
  - Displays extraction confidence score ($0.00 - 1.00$).
  - Allows human reviewer to toggle: `VERIFIED`, `MODIFIED`, or `REJECTED`.
- **Data State:** `STATE_EXTRACTION_REVIEW`.

### Step 5: Chronological Timeline Construction
- **Engine:** Timeline Ordering Engine normalizes all relative temporal phrases (*"fever started 3 days ago"*, *"vomited twice yesterday evening"*) into discrete ISO 8601 timestamps.
- **Structure:** Synthesizes an interactive horizontal progression of clinical milestones.
- **Safety Gate:** Chronological anomaly detection flags impossible date sequences (e.g., medication taken after encounter creation).

### Step 6: Missing Information Audit
- **Engine:** Audits extracted parameters against clinical safety checklists:
  - `KNOWN`: High-confidence verified parameter present.
  - `UNKNOWN`: Critical or important parameter completely absent.
  - `CONFLICTING`: Mutually incompatible claims detected across modalities (e.g., patient states 2 days of fever, prescription shows 14 days of antibiotics).
  - `UNRELIABLE`: Low-confidence OCR reading or mumbled speech segment.
- **Categorization:**
  - *Critical:* Red flags, hemodynamic vitals, pregnancy status, allergy history.
  - *Important:* Onset duration, comorbidities, current drug therapies.
  - *Optional:* Non-acute social history, family history.
- **Data State:** `STATE_MISSING_AUDIT`.

### Step 7: Targeted Follow-Up Question Engine
- **Engine:** Dynamic Next-Best-Information (NBI) generator computes which missing parameter will maximize diagnostic certainty.
- **Operational Constraint:** Restricts follow-up to a maximum of **1 to 3 targeted questions** to prevent cognitive fatigue.
- **Presentation:** Rendered in patient's preferred vernacular language with structured tap-to-select chips.
- **Data State:** `STATE_FOLLOW_UP_PENDING`.

### Step 8: Mathematical Sufficiency Gate
- **Formula:**
  $$S = \frac{\sum_{i \in \text{Critical}} w_i \cdot \delta_i + \sum_{j \in \text{Important}} w_j \cdot \delta_j}{\sum w_i + \sum w_j}, \quad \text{where } \delta \in \{0, 1\}$$
- **Branching Decision:**
  - If $S \ge 0.85$ AND all Critical Red-Flags are addressed $\longrightarrow$ Direct to **Data Consolidation** (`STATE_CONSOLIDATED`).
  - If $S < 0.85$ OR any Critical Vital is `UNKNOWN` $\longrightarrow$ Route to **Staff Missing-Data Worklist** (`STATE_STAFF_DATA_PENDING`).

### Step 9: Staff Assignment & Point-of-Care Vitals (Conditional Branch)
- **Actor:** Triage Nurse / Frontline Health Worker (`ROLE_NURSE` / `ROLE_HEALTH_WORKER`).
- **Workspace:** Staff Missing-Data Checklist screen.
- **Mandatory Invariant:** Staff **NEVER** creates a secondary case. Staff inputs BP, SpO2, HR, Respiratory Rate, and Temperature directly into the existing `case_id`.
- **Physical Checklist:** Staff performs physical red-flag inspection (pallor, cyanosis, cold extremities, respiratory distress).
- **Staff Sign-Off:** Nurse validates inputs, transitioning state to `STATE_STAFF_VERIFIED`.

### Step 10: Data Consolidation & CAREGRAPH Synthesis
- **Engine:** $\text{CAREGRAPH}$ instantiates a physiological graph model for the encounter:
  - Calculates Physiological Risk Score (NEWS2 / MEWS baseline).
  - Evaluates Disease Trajectory ($\tau_t \in \{\text{IMPROVING}, \text{STABLE}, \text{DETERIORATING}, \text{CRITICAL}\}$).
  - Computes Epistemic Uncertainty ($U_t \in [0.0, 1.0]$).
  - Identifies clinical differential hypotheses.
- **Data State:** `STATE_CONSOLIDATED` $\to$ `STATE_TRIAGE_READY`.

### Step 11: Structured Triage Note & Master Clinical Report Generation
- **Engine:** Synthesizes two core artifacts:
  1. *Structured Triage Note:* Standardized clinical summary (Chief Complaint, HPI, Vitals, Allergies, Risk Band, Trajectory).
  2. *Master Clinical Report (Report Type 1):* Multi-panel comprehensive dossier.
- **Advisory Tagging:** Explicitly watermarked: `AI-GENERATED ADVISORY DRAFT — REQUIRES CLINICAL VERIFICATION`.

### Step 12: Dynamic Doctor Queue
- **Engine:** Dynamic Queue Prioritization Engine sorts pending patients using a composite multi-parameter vector:
  $$\mathbf{Priority} = w_{\text{risk}} \cdot \text{Risk} + w_{\tau} \cdot \text{Trajectory} + w_{\text{wait}} \cdot t_{\text{waiting}} + w_U \cdot U_t$$
- **Behavior:** Patients with deteriorating trajectories or high uncertainty rise dynamically above stable patients, preventing waiting-room decompensation.
- **Data State:** `STATE_DOCTOR_QUEUED`.

### Step 13: Doctor Comprehensive Case Review
- **Actor:** Registered Medical Practitioner (`ROLE_CLINICIAN`).
- **Workspace:** Doctor Review Workbench:
  - Panel 1: Patient Summary & Demographics.
  - Panel 2: Visual Timeline.
  - Panel 3: Multimodal Evidence with provenance viewer.
  - Panel 4: CAREGRAPH Visual State & Trajectory.
  - Panel 5: Missing Information & Uncertainty Breakdown.
  - Panel 6: Draft Triage Note.
  - Panel 7: FACILITYGRAPH Local Capability HUD.
- **Data State:** `STATE_DOCTOR_REVIEWING`.

### Step 14: Doctor Clinical Action Gate (`VERIFY`, `MODIFY`, `ADD`)
- **Actions:**
  - `VERIFY`: Clinician validates extracted findings and vitals.
  - `MODIFY`: Clinician edits inaccurate values, recording an explicit rationale.
  - `ADD`: Clinician records on-site physical examination findings (auscultation, palpation, neurological reflexes, point-of-care ultrasound).
- **Data State:** `STATE_CLINICIAN_VERIFIED`.

### Step 15: FACILITYGRAPH Capability & Feasibility Evaluation
- **Engine:** $\text{FACILITYGRAPH}$ cross-references patient's clinical requirements against local hospital capability:
  - Are required diagnostic modalities available on-site (e.g., CT scanner, blood bank, ultrasound)?
  - Are appropriate inpatient beds staffed and open (ICU, HDU, General Ward)?
  - Are required specialist medical officers on active duty?
- **Output:** Outputs Feasibility Index ($\Phi_{\text{local}} \in [0.0, 1.0]$).
- **Data State:** `STATE_FACILITY_EVALUATING`.

### Step 16: Orchestration Advisory Recommendation
- **Engine:** $\text{ORCHESTRATION}$ engine synthesizes $\text{CAREGRAPH}$ patient state with $\text{FACILITYGRAPH}$ resource availability to suggest the **Safest Achievable Care Pathway**:
  - `SUGGEST_ROUTINE_CARE` (Low risk, stable trajectory, managed on-site).
  - `SUGGEST_FURTHER_REVIEW` (Moderate risk, pending investigations).
  - `SUGGEST_WARD_ADMISSION` (Requires inpatient stay, local bed available).
  - `SUGGEST_REFERRAL` (Local capability deficit, transfer required).
  - `SUGGEST_EMERGENCY_ESCALATION` (Physiological instability detected).
- **Invariant:** Advisory ONLY. Clinician may accept, modify, or reject.
- **Data State:** `STATE_ORCHESTRATION_PENDING`.

### Step 17: Clinician Disposition & Pathway Execution
The attending doctor issues the final, binding legal disposition, routing the patient into one of six structured branches:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SIX POST-DOCTOR CARE BRANCHES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ BRANCH A: ROUTINE / HOME CARE ] ──> Discharge pack, prescription,        │
│                                        recurring calendar schedule.         │
│                                                                             │
│  [ BRANCH B: FURTHER REVIEW ] ──> Single revisit slot for pending labs or   │
│                                   24-48h clinical reassessment.             │
│                                                                             │
│  [ BRANCH C: WARD ADMISSION ] ──> Formal inpatient bed request, automated   │
│                                   medication list, nurse SBAR handoff.      │
│                                                                             │
│  [ BRANCH D: REFERRAL / TRANSFER ] ──> Capability-matched destination       │
│                                        selection, digital referral pack.    │
│                                                                             │
│  [ BRANCH E: EMERGENCY ESCALATION ] ──> Dynamic jump to acute resuscitation │
│                                         due to acute decompensation.        │
│                                                                             │
│  [ BRANCH F: OT / PROCEDURE PATHWAY ] ──> Surgical checklist, pre-op        │
│                                           dossier, theatre scrub handoff.   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dynamic Escalation Invariant

At any point during the Regular Pathway—whether during voice intake, nurse vitals check, or waiting in the doctor queue—if a patient exhibits acute clinical deterioration ($\text{SpO}_2 < 85\%$, altered consciousness, crushing chest pain, anaphylaxis, or sudden collapse):

1. Any healthcare worker can trigger the **Emergency Fast-Track Escalation**.
2. The current regular state is instantly preempted.
3. The Master Case transitions directly to `STATE_EMERGENCY_ACTIVE`.
4. High-contrast acute alerts trigger across nursing and doctor consoles.
5. Patient enters the **Emergency Master Journey** immediately.
