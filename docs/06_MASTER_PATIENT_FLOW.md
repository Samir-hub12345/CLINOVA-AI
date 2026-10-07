# CLINOVA AI — Master Patient Workflow Specification

> **Document ID:** `DOC-06`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Primary End-to-End Workflow

The Master Patient Workflow orchestrates multimodal ingestion, uncertainty resolution, clinical review, and resource-aware navigation into a unified continuous sequence.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MASTER PATIENT WORKFLOW PIPELINE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                                  PATIENT                                    │
│                                     │                                       │
│                                     ▼                                       │
│                       ENTRY MODE (Regular / Emergency)                      │
│                                     │                                       │
│                                     ▼                                       │
│                     SCATTERED MULTIMODAL INFORMATION                        │
│                 (Voice Audio, Typed Narrative, OCR Reports)                 │
│                                     │                                       │
│                                     ▼                                       │
│                      EXTRACTION & ENTITY RESOLUTION                         │
│                                     │                                       │
│                                     ▼                                       │
│                         VISUAL EXTRACTION REVIEW                            │
│                     (Inspect Provenance, Tags, Scores)                      │
│                                     │                                       │
│                                     ▼                                       │
│                          TIMELINE SUMMARIZATION                             │
│                                     │                                       │
│                                     ▼                                       │
│                        MISSING INFORMATION AUDIT                            │
│                 (Known, Unknown, Conflicting, Unreliable)                   │
│                                     │                                       │
│                                     ▼                                       │
│                        FOLLOW-UP QUESTION ENGINE                            │
│                                     │                                       │
│                      [ INFORMATION SUFFICIENCY GATE ]                       │
│                                     │                                       │
│                  ┌──────────────────┴──────────────────┐                    │
│                  ▼                                     ▼                    │
│      [ IF SUFFICIENT (>= Threshold) ]     [ IF INSUFFICIENT (< Threshold) ] │
│                  │                                     │                    │
│                  │                         STAFF ASSIGNMENT                 │
│                  │                         (Nurse / Health Worker Desk)     │
│                  │                                     │                    │
│                  │                         MISSING-DATA CHECKLIST           │
│                  │                         & POINT-OF-CARE VITALS           │
│                  │                                     │                    │
│                  │                         STAFF VERIFICATION               │
│                  │                                     │                    │
│                  │                         ATTACH TO SAME MASTER CASE       │
│                  │                         (Never create second case!)      │
│                  │                                     │                    │
│                  └──────────────────┬──────────────────┘                    │
│                                     ▼                                       │
│                            DATA CONSOLIDATION                               │
│                                     │                                       │
│                                     ▼                                       │
│                       CAREGRAPH ENGINE SYNTHESIS                            │
│               (State, Risk, Trajectory, Uncertainty, NBI)                   │
│                                     │                                       │
│                                     ▼                                       │
│                         STRUCTURED TRIAGE NOTE                              │
│                                     │                                       │
│                                     ▼                                       │
│                         MASTER CLINICAL REPORT                              │
│                                     │                                       │
│                                     ▼                                       │
│                            DOCTOR QUEUE ORDERING                            │
│                                     │                                       │
│                                     ▼                                       │
│                            DOCTOR CASE REVIEW                               │
│                                     │                                       │
│                                     ▼                                       │
│                       DOCTOR VERIFY / MODIFY / ADD                          │
│                                     │                                       │
│                                     ▼                                       │
│                        FACILITYGRAPH EVALUATION                             │
│                                     │                                       │
│                                     ▼                                       │
│                       ORCHESTRATION ENGINE GUIDANCE                         │
│                                     │                                       │
│                                     ▼                                       │
│                      SAFEST ACHIEVABLE CARE PATHWAY                         │
│              (Routine / Further Review / Ward / OT / Referral)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion, Extraction, and Visual Review

### 2.1 Raw Multimodal Input Ingestion
Patients or health workers present input across three concurrent modalities:
- **Audio Recording:** Regional vernacular speech (Odia, Hindi, Indian English) processed via local Whisper / faster-whisper.
- **Typed Free-Text:** Symptom narratives entered via standard keyboard or mobile touch screen.
- **Document & Image Files:** Prescriptions, discharge summaries, or printed lab sheets processed via local PaddleOCR / Tesseract.

### 2.2 Extraction & Structuring
Raw input undergoes deterministic and local SLM entity extraction:
- **Detected Symptoms:** Extracted entities normalized to standard clinical terms with severity, onset, and duration.
- **Detected Physiological Values:** Numerical values extracted and paired with standard physiological units (e.g., BP in mmHg, SpO2 in %).
- **Detected Dates & Timestamps:** Chronological points extracted and normalized to ISO 8601 timestamps.
- **Clinical Modifiers:** Anatomical location, radiation, aggravating/relieving factors.

### 2.3 Visual Extraction Review
The interface strictly rejects "black-box" outputs. The user and reviewer can inspect:
- The original source snippet side-by-side with the extracted entity.
- The extraction confidence score (0.00–1.00).
- The evidence source tag (`VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `PATIENT_REPORTED`).
- Verification status toggle (`PENDING_REVIEW`, `VERIFIED`, `REJECTED`).

---

## 3. Timeline Summarization

The system synthesizes a chronologically ordered longitudinal patient journey from verified and extracted dates:
- **Event Node Structure:**
  - `timestamp`: Date and time of symptom onset, medication, or investigation.
  - `event_label`: Discrete clinical event (e.g., "Onset of high fever", "Took Paracetamol 650mg", "Platelets measured at 45,000/μL").
  - `evidence_source`: Source document or transcript line.
  - `confidence_score`: Extraction certainty.
  - `verification_status`: Verified by clinician or inferred by parser.
- **Visual Display:** Interactive horizontal/vertical milestone timeline illustrating disease progression.

---

## 4. Missing Information Audit & Follow-Up Engine

### 4.1 Categorization of Information State
The engine audits all clinical fields against clinical safety checklists, categorizing every parameter into one of five states:
- `KNOWN`: Verified value present with high-confidence source.
- `UNKNOWN`: Parameter is completely absent from the encounter.
- `CONFLICTING`: Mutually incompatible values exist across sources (e.g., patient states fever for 2 days; uploaded clinic slip shows fever for 2 weeks).
- `UNRELIABLE`: Low-confidence OCR extraction or mumbled audio transcript.
- `NEEDS_VERIFICATION`: Self-reported extreme or abnormal value requiring clinical confirmation.

### 4.2 Importance Stratification
Missing parameters are stratified by clinical importance:
- **CRITICAL:** Red-flag danger signs and vital signs (SpO2, BP, chest pain radiation, pregnancy status in reproductive females, severe allergy history).
- **IMPORTANT:** Symptom duration, past medical comorbidities (diabetes, hypertension, CAD), current medications.
- **OPTIONAL:** Occupational details, family medical history of non-acute illness.

> **Absolute Invariant:** The system NEVER invents, fabricates, or imputes missing values. Gaps remain explicitly flagged as `UNKNOWN`.

### 4.3 Dynamic Follow-Up Question Engine
The engine computes the **Next-Best Information** required to resolve uncertainty:
- Generates 1–3 targeted candidate questions aimed strictly at closing high-uncertainty gaps.
- Questions are rendered in the patient's preferred language with simplified multiple-choice or short-input formats.
- **Sufficiency Evaluation:** When the patient answers:
  - If information sufficiency crosses the clinical safety threshold ($\ge 0.85$ completeness for critical fields), the case proceeds directly to **Data Consolidation**.
  - If critical fields remain unknown (e.g., patient skipped SpO2 or could not measure BP), the workflow routes immediately to the **Staff Missing-Data Path**.

---

## 5. Staff Missing-Data Path (Frontline Nurse / Health Worker)

### 5.1 Staff Assignment & Workspace
When automated intake leaves critical parameters missing, the case is assigned to the frontline triage nursing desk:
- Case appears in the **Nurse Missing-Data Worklist**.
- Nurse opens the **Staff Missing-Data Checklist Screen**.

### 5.2 Mandatory Single Master Case Invariant
> **CRITICAL LAW:** The staff member must NEVER create a second or duplicate patient case.
> All newly acquired vitals, verified physical signs, and corrected details MUST be appended directly to the existing Master Case via `case_id`.

### 5.3 Staff Action Flow
1. Staff verifies patient identity via synthetic case ID.
2. Staff uses physical instruments to measure missing critical vitals (BP, SpO2, pulse, temperature, blood glucose).
3. Staff completes mandatory red-flag checklist.
4. Staff signs off on the data collection.
5. The Master Case updates instantly:
   - CAREGRAPH re-evaluates risk, trajectory, and uncertainty.
   - Master Clinical Report updates dynamically.
   - Case is promoted into the **Doctor Queue**.

---

## 6. Doctor Queue, Review, and Decision Gate

### 6.1 Multi-Dimensional Queue Prioritization
Doctor Queue dynamically sorts cases using a composite priority vector:
$$\mathbf{Priority} = f(\text{Emergency Status}, \text{Risk Level}, \text{Trajectory}, \text{Wait Duration}, \text{Uncertainty Score})$$
Cases with worsening trajectories or red-flag escalations automatically jump to the top of the queue.

### 6.2 Doctor Comprehensive Case Overview
The clinician reviews the unified workbench displaying:
- Patient Snapshot & Demographics
- Longitudinal Timeline
- Multimodal Evidence & Raw Attachments
- CAREGRAPH Visual State & Physiological Trajectory
- Evidence Uncertainty & Known/Unknown Audit
- AI-Generated Structured Triage Note Draft
- FACILITYGRAPH Local Capability & Referral Feasibility

### 6.3 Doctor Verification (`VERIFY`, `MODIFY`, `ADD`)
The doctor interacts with all discrete parameters:
- **VERIFY:** Doctor confirms an extracted parameter as clinically accurate.
- **MODIFY:** Doctor corrects an inaccurate value, entering an audit reason.
- **ADD:** Doctor inputs on-site examination findings (auscultation, palpation, bedside ultrasound).

### 6.4 Care Pathway Execution
The doctor reviews the Orchestration Engine's recommendation for **The Safest Achievable Next Care Pathway** and issues the binding disposition:
- `ROUTINE_HOME_CARE`: Home management with scheduled follow-up calendar.
- `FURTHER_REVIEW`: Return visit scheduled for re-examination or pending lab review.
- `WARD_ADMISSION`: Direct inpatient ward admission with structured handoff report.
- `EMERGENCY_OT`: Immediate emergency resuscitation or surgical theatre transfer.
- `INTER_FACILITY_REFERRAL`: Feasibility-verified transfer to a capable receiving hospital.
