# CLINOVA AI — Design Specifications: Cluster 2 (Intake, Extraction & Triage Gap Audit)

> **File:** `docs/design/02_INTAKE_AND_EXTRACTION_SCREENS.md`  
> **Screens Covered:** Screens 05 through 12  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 05: Patient Entry Mode Selector (Regular vs. Emergency)

### 1. Specification
- **Route:** `/encounter/new`
- **Purpose:** Provide an unambiguous entry junction that routes incoming presentations to either Standard Multimodal Intake or the Emergency Fast-Track.
- **Actor:** Triage Nurse, Registration Clerk, Patient, Emergency Paramedic.
- **Entry Condition:** Authenticated staff session or public walk-in kiosk.
- **Inputs:** Binary decision button click (`STANDARD` vs `EMERGENCY`).
- **Outputs:** Visual guidance detailing the criteria for emergency vs. standard intake.
- **Actions:** "Start Regular / Standard Intake", "ACTIVATE EMERGENCY FAST-TRACK".
- **Navigation:** Regular routes to `/encounter/intake`; Emergency routes to `/emergency/fast-track`.
- **States:**
  - *Normal:* Two prominent, high-contrast cards. Left card: Calm slate/blue (Regular). Right card: High-contrast red with flashing warning border (Emergency).
  - *Mobile:* Stacked vertically with oversized touch targets.
- **Graph Linkage:** Sets `intake_mode` on newly provisioned `MasterCase`.

### 2. Wireframe (Screen 05)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Station: Triage Desk 1           [ DR. MOHAPATRA ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INITIAL ENCOUNTER ROUTING: SELECT PRESENTATION MODE                       │
│                                                                             │
│   ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│   │ 📋 REGULAR / STANDARD INTAKE │  │ 🚨 EMERGENCY FAST-TRACK      │        │
│   │                              │  │                              │        │
│   │ • Conscious, stable vitals   │  │ • SEVERE BREATHLESSNESS / O2 │        │
│   │ • Multimodal narrative entry │  │ • CHEST PAIN / SEVERE SHOCK  │        │
│   │ • Report OCR & verification  │  │ • MASSIVE BLEEDING / TRAUMA  │        │
│   │ • Full timeline & gap audit  │  │ • UNCONSCIOUS / GCS < 9      │        │
│   │                              │  │                              │        │
│   │ [ PROCEED TO STANDARD INTAKE]│  │ [ ACTIVATE EMERGENCY NOW ]   │        │
│   └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                             │
│   SAFETY INVARIANT: Regular encounters automatically escalate to Emergency  │
│   at any millisecond if acute danger signs or panic vitals are detected.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 06: Patient Information & Narrative Intake

### 1. Specification
- **Route:** `/encounter/intake`
- **Purpose:** Collect demographic qualifiers, capture mandatory informed consent, and record the chief complaint narrative.
- **Actor:** Patient, Caregiver, Triage Nurse.
- **Entry Condition:** Regular mode selected from Screen 05.
- **Inputs:** Synthetic ID / Name, Age, Gender, Preferred Language (Odia/Hindi/English), Consent Checkbox, Chief Complaint text.
- **Outputs:** Auto-calculated duration tag, in-flight PII redaction preview token.
- **Actions:** "Record Voice Instead" (routes to Screen 07), "Upload Past Reports" (routes to Screen 08), "Continue to Extraction" (routes to Screen 09).
- **Navigation:** Advances to Screen 09.
- **States:**
  - *Consent Missing:* "Continue" button is disabled until consent checkbox is confirmed.
  - *Error:* Red outline if age < 0 or > 120.
- **Graph Linkage:** Initializes `MasterCase.demographics` and `MasterCase.raw_symptom_narrative`.

### 2. Wireframe (Screen 06)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Encounter: PT-94021 [NEW]        [ LANG: ODIA ▼ ]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PATIENT INTAKE & CHIEF COMPLAINT                                          │
│                                                                             │
│   [1. Demographics & Consent]                                               │
│   Age: [ 45 ]  Gender: [ Male ▼ ]  Language: [ Odia ▼ ]                     │
│   [X] I give informed consent for AI-assisted clinical triage processing.  │
│                                                                             │
│   [2. Chief Complaint Narrative]                                            │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ Patient reports severe fever for 4 days with joint pain and dark rash │ │
│   │ appearing on forearms this morning. Complains of sudden weakness and  │ │
│   │ severe nausea.                                                        │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│   [ 🎤 Record Spoken Narrative ]     [ 📄 Upload Past Prescriptions/Labs ]  │
│                                                                             │
│   PII Sanitization Active: Aadhaar & Phone numbers automatically scrubbed.  │
│                                                                             │
│   [ CANCEL ]                                  [ PROCEED TO EXTRACTION ──>]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 07: Voice Symptom Intake (Whisper Audio)

### 1. Specification
- **Route:** `/encounter/voice`
- **Purpose:** Audio voice recording interface for non-literate patients or vernacular speech dictation (Odia, Hindi, English).
- **Actor:** Patient, Nurse, Community Health Worker.
- **Entry Condition:** Initiated from Screen 06.
- **Inputs:** Audio input waveform stream via browser microphone.
- **Outputs:** Live recording timer, audio visualizer, real-time vernacular transcript, detected language, confidence score.
- **Actions:** "Start Recording", "Pause / Stop", "Re-record", "Confirm & Transcribe".
- **Navigation:** Returns to Screen 06 or advances to Screen 09.
- **States:**
  - *Idle:* Large circular mic button.
  - *Recording:* Pulsing red ring, active timer (`00:24`), live waveform.
  - *Transcribing:* Spinner stating "Transcribing locally via Whisper...".
  - *Verified:* Transcript rendered with translated English preview.
- **Graph Linkage:** Populates `MasterCase.voice_recordings` with transcript and confidence.

### 2. Wireframe (Screen 07)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Voice Triage Ingestion           [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   VERNACULAR VOICE INTAKE (ODIA / HINDI / ENGLISH)                          │
│                                                                             │
│                         ┌───────────────────────┐                           │
│                         │       🔴 00:28        │                           │
│                         │   [ ⏹ STOP RECORD ]   │                           │
│                         └───────────────────────┘                           │
│                       Waveform: ▃▅▇█▇▆▅▃▂ ▃▅▇█▇▆▃                           │
│                                                                             │
│   LIVE TRANSCRIPT (ODIA NATIVE):                                            │
│   "ମୋତେ ୪ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ହେଉଛି ଏବଂ ହାତରେ ନାଲି ଦାଗ ଦେଖାଯାଇଛି..."      │
│                                                                             │
│   CLINICAL TRANSLATION (ENGLISH):                                           │
│   "Severe fever for 4 days with red rash appearing on arms..."              │
│   Detected Language: Odia (98% confidence) | Engine: Local Faster-Whisper   │
│                                                                             │
│   [ RE-RECORD AUDIO ]                           [ ATTACH TO MASTER CASE ]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 08: Medical Report & Prescription Upload

### 1. Specification
- **Route:** `/encounter/upload`
- **Purpose:** File ingestion dropzone for printed lab sheets (CBC, Widal, electrolytes), prescriptions, and ECG photos.
- **Actor:** Patient, Caregiver, Nurse.
- **Entry Condition:** Initiated from Screen 06.
- **Inputs:** File drag-and-drop or camera capture (PNG, JPG, PDF; max 15MB).
- **Outputs:** File thumbnail, file size, MIME-type validation badge, upload progress bar.
- **Actions:** "Browse Files", "Capture with Camera", "Run Local OCR Extraction", "Delete File".
- **Navigation:** Advances to Screen 09.
- **States:**
  - *Empty:* Dashed dropzone with folder and camera icons.
  - *Uploading:* Progress bar (0–100%).
  - *Error:* "Corrupt or unsupported file type. Please upload a clear photo or PDF."
- **Graph Linkage:** Appends files to `MasterCase.uploaded_documents`.

### 2. Wireframe (Screen 08)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Document & Lab Upload            [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   UPLOAD MEDICAL REPORTS, PRESCRIPTIONS & LAB SLIPS                         │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                   📂 DRAG & DROP CLINICAL FILES HERE                  │ │
│   │                Supports Clear Photos (JPG, PNG) or PDFs               │ │
│   │                     [ BROWSE LOCAL FILES ]  [ 📷 CAMERA ]             │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   ATTACHED DOCUMENTS (2):                                                   │
│   1. [📄] cbc_report_oct07.jpg (1.8 MB) ──> [✓ UPLOADED] [ RUN OCR ] [🗑]  │
│   2. [📄] opd_slip_oct03.pdf    (0.4 MB) ──> [✓ UPLOADED] [ RUN OCR ] [🗑]  │
│                                                                             │
│   Storage Notice: Raw files purged in 24 hours under minimal retention rule.│
│                                                                             │
│   [ BACK TO INTAKE ]                           [ PROCEED TO EXTRACTION ──>] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 09: Extraction & Visual Entity Review

### 1. Specification
- **Route:** `/encounter/extraction`
- **Purpose:** Side-by-side inspection of raw input text/images against extracted discrete clinical entities. Rejects black-box outputs.
- **Actor:** Triage Nurse, Reviewing Medical Officer.
- **Entry Condition:** Ingestion complete from Screens 06, 07, or 08.
- **Inputs:** Interactive entity verification checkboxes; inline value corrections.
- **Outputs:** Detected symptoms, physiological values, units, extracted dates, bounding boxes, extraction confidence scores.
- **Actions:** "Verify Entity", "Edit Value", "Reject Entity", "Add Missing Entity", "Proceed to Timeline".
- **Navigation:** Advances to Screen 10.
- **States:**
  - *Normal:* Two-column layout: Left = Raw source snippet with highlighted bounding boxes. Right = Extracted clinical entity cards.
  - *Low Confidence:* Amber border badge: "Low OCR confidence (0.62). Please verify value manually."
- **Graph Linkage:** Commits discrete entities to `MasterCase.extracted_entities`.

### 2. Wireframe (Screen 09)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Visual Extraction Review         [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RAW SOURCE EVIDENCE                      EXTRACTED CLINICAL ENTITIES      │
│   ┌────────────────────────────────────┐   ┌──────────────────────────────┐ │
│   │ [CBC SCAN SNIPPET]                 │   │ Parameter: Platelet Count    │ │
│   │  Platelet Count: 42,000 /uL        │   │ Extracted Value: 42,000      │ │
│   │  Hb: 13.2 g/dL                     │   │ Unit: /μL | Normal: 150-450k │ │
│   │  TLC: 3,400 /uL                    │   │ Status: ⚠️ SEVERE THROMBOCYT │ │
│   │                                    │   │ Conf: 96% | Source: OCR [✓]  │ │
│   │ Source: cbc_report_oct07.jpg       │   │ [ VERIFY ] [ EDIT ] [REJECT] │ │
│   └────────────────────────────────────┘   └──────────────────────────────┘ │
│   ┌────────────────────────────────────┐   ┌──────────────────────────────┐ │
│   │ [VOICE TRANSCRIPT SNIPPET]         │   │ Symptom: Acute Febrile Illn. │ │
│   │ "...severe fever for 4 days with   │   │ Onset: 4 Days Ago            │ │
│   │  petechial rash on forearms..."    │   │ Modifier: Petechial Rash     │ │
│   │                                    │   │ Conf: 98% | Source: Voice[✓] │ │
│   └────────────────────────────────────┘   └──────────────────────────────┘ │
│                                                                             │
│   [ ADD MANUAL ENTITY ]                        [ VIEW LONGITUDINAL TIMELINE]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 10: Longitudinal Patient Timeline

### 1. Specification
- **Route:** `/encounter/timeline`
- **Purpose:** Chronologically visualize symptom onset, prior interventions, laboratory milestones, and acute deterioration.
- **Actor:** Triage Nurse, Doctor.
- **Entry Condition:** Discrete entities extracted from Screen 09.
- **Inputs:** Zoom controls (Hours / Days / Weeks), filter toggles (Vitals, Symptoms, Labs).
- **Outputs:** Chronological visual timeline with verified milestones.
- **Actions:** "Add Milestone", "Verify Timestamp", "Proceed to Gap Audit".
- **Navigation:** Advances to Screen 11.
- **States:**
  - *Normal:* Horizontal or vertical swimlane showing date-stamped clinical events.
  - *Conflict State:* Red jagged indicator showing contradictory dates across records.
- **Graph Linkage:** Commits to `MasterCase.timeline_events` and feeds CAREGRAPH temporal context.

### 2. Wireframe (Screen 10)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Longitudinal Patient Timeline    [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CHRONOLOGICAL DISEASE PROGRESSION (4-DAY ONSET WINDOW)                    │
│                                                                             │
│   OCT 04 (Day 1)      OCT 06 (Day 3)      OCT 07 (Day 4)     OCT 08 (TODAY) │
│   ───────●──────────────────●───────────────────●──────────────────●─────── │
│          │                  │                   │                  │        │
│      Fever Onset        Took PCM 650mg      CBC Drawn:         Presents at  │
│      High grade,        Mild relief,        Platelets 42k,     PHC with BP  │
│      chills reported    body aches persist  TLC 3,400          88/60, Rash  │
│      Source: Voice      Source: OPD Slip    Source: Lab OCR    Source: Desk │
│      [VERIFIED]         [VERIFIED]          [VERIFIED]         [VERIFIED]   │
│                                                                             │
│   Trajectory Signal: Rapid platelet drop over 24 hours with narrowing BP.  │
│                                                                             │
│   [ EXPORT TIMELINE SLIP ]                     [ RUN MISSING DATA AUDIT ──>]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 11: Missing Information & Contradiction Audit

### 1. Specification
- **Route:** `/encounter/audit`
- **Purpose:** Algorithmic audit categorizing clinical parameters into `KNOWN`, `UNKNOWN`, `CONFLICTING`, and `UNRELIABLE`. Highlights critical clinical omissions.
- **Actor:** Triage Nurse, Doctor.
- **Entry Condition:** Timeline and extractions complete.
- **Inputs:** None (Automated safety rule evaluation).
- **Outputs:** Status badges across critical, important, and optional clinical fields; explicit contradiction alerts.
- **Actions:** "Generate Follow-up Questions" (Screen 12), "Assign to Nurse Vitals Desk" (Screen 13).
- **Navigation:** If sufficient $\rightarrow$ Screen 15. If gaps exist $\rightarrow$ Screen 12.
- **States:**
  - *Gaps Present:* High-contrast amber/red alert callout indicating critical missing vitals.
  - *Contradiction Detected:* High-contrast card showing conflicting data.
- **Graph Linkage:** Computes `CareGraph.uncertainty_vector`.

### 2. Wireframe (Screen 11)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Evidence Completeness Audit      [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CLINICAL EVIDENCE AUDIT: UNCERTAINTY & GAP ANALYSIS                       │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ 🔴 CRITICAL INFORMATION GAPS (2 UNKNOWN):                             │ │
│   │ • Blood Pressure: UNKNOWN (Critical vital missing)                    │ │
│   │ • Capillary Refill Time: UNKNOWN (Essential for shock assessment)     │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ ⚠️ CONFLICTING EVIDENCE DETECTED (1 CONFLICT):                         │ │
│   │ • Fever Duration: Patient reports 4 days; OPD Slip indicates 10 days  │ │
│   │   [ CLINICIAN RESOLUTION REQUIRED BEFORE DISCHARGE ]                  │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ 🟢 KNOWN & VERIFIED (4 PARAMETERS):                                   │ │
│   │ • Platelets: 42,000/μL | TLC: 3,400/μL | Rash: Petechial | Age: 45    │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   Uncertainty Score: 0.68 (HIGH) | Decision Safety Gate: BLOCKED            │
│                                                                             │
│   [ RESOLVE VIA QUESTIONS (NBI) ]        [ ASSIGN TO NURSE WORKLIST (DESK) ]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 12: Dynamic Follow-up Question Engine (NBI)

### 1. Specification
- **Route:** `/encounter/follow-up`
- **Purpose:** Present 1–3 prioritized Next-Best Information questions directly to the patient or nurse to collapse clinical uncertainty.
- **Actor:** Patient, Caregiver, Nurse.
- **Entry Condition:** Audit identifies resolvable information gaps.
- **Inputs:** Radio button selections, numerical inputs.
- **Outputs:** Targeted questions in patient's preferred language with clinical utility justification.
- **Actions:** "Submit Answers", "Skip to Nurse Desk".
- **Navigation:** Answers submitted $\rightarrow$ If critical fields still missing $\rightarrow$ Screen 13. If complete $\rightarrow$ Screen 15.
- **States:**
  - *Normal:* 1 to 3 clean radio cards with high-contrast choices.
  - *Submitting:* Re-evaluating information completeness threshold.
- **Graph Linkage:** Reduces uncertainty in `CareGraph.uncertainty_vector`.

### 2. Wireframe (Screen 12)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Targeted Clinical Follow-up      [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   NEXT-BEST INFORMATION: TARGETED CLARIFYING QUESTIONS                      │
│   Please answer these 2 safety questions to assist the clinical team:       │
│                                                                             │
│   Q1. Are you experiencing any active bleeding from gums, nose, or urine?   │
│   ( ) YES — Active bleeding noted                                           │
│   ( ) NO — No bleeding noted                                                │
│   ( ) Unsure / Caregiver cannot confirm                                     │
│                                                                             │
│   Q2. When you stand up, do you feel severe dizziness or fainting?          │
│   ( ) YES — Severe postural dizziness                                       │
│   ( ) NO — No dizziness on standing                                         │
│                                                                             │
│   Clinical Purpose: Evaluates Dengue Hemorrhagic Shock risk criteria.       │
│                                                                             │
│   [ SKIP QUESTIONS (NURSE WILL ASSESS) ]         [ SUBMIT & RE-EVALUATE ]   │
└─────────────────────────────────────────────────────────────────────────────┘
```
