# Clinova AI — Feature Specification Document

**Document Version:** 1.0.0  
**Target Platform:** Primary Health Centers (PHCs), Community Health Centers (CHCs), Government District Hospital OPDs, Outreach Camps, and Campus Health Clinics  
**Current Release:** v0.2.0 (Integrated Staging)  

---

> [!WARNING]
> ### 🔒 Clinical Safety & Non-Diagnostic Notice
> **Educational prototype and clinical decision support system only.** Clinova AI does not diagnose disease, prescribe pharmaceuticals, or make autonomous medical decisions. All AI-synthesized summaries, risk flags, and triage priority categories strictly require verification and explicit sign-off by a qualified medical professional before clinical action.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Feature Matrix: Implemented vs. Planned](#2-feature-matrix-implemented-vs-planned)
3. [Multimodal Patient Intake Pipeline](#3-multimodal-patient-intake-pipeline)
4. [Deterministic Clinical Risk Engine](#4-deterministic-clinical-risk-engine)
5. [Prioritized Reviewer Queue](#5-prioritized-reviewer-queue)
6. [Medical Officer Case Review & Human Gate](#6-medical-officer-case-review--human-gate)
7. [Standardized Clinical Referral Document](#7-standardized-clinical-referral-document)
8. [Interactive Clinical Demonstration Hub](#8-interactive-clinical-demonstration-hub)
9. [EHR Patient Registry & Consultations](#9-ehr-patient-registry--consultations)
10. [Accessibility & Low-Bandwidth Mode](#10-accessibility--low-bandwidth-mode)
11. [In-Flight Privacy & Medicolegal Audit](#11-in-flight-privacy--medicolegal-audit)

---

## 1. Executive Summary

**Clinova AI** is an explainable, multimodal, human-in-the-loop clinical decision support platform designed to assist frontline healthcare workers in resource-constrained public health settings. In high-volume outpatient clinics and community health camps, patients frequently present with vernacular speech, disorganized symptom timelines, and disparate handwritten or lab documents.

Clinova AI bridges the gap between walk-in patient presentations and attending clinicians by structuring multimodal inputs into standardized, explainable clinical documentation (SOAP format: Subjective, Objective, Assessment, Plan) alongside audited, deterministic urgency classifications.

---

## 2. Feature Matrix: Implemented vs. Planned

| Feature Area | Current Operational Status (v0.2.0) | Planned Roadmap Capability |
| :--- | :--- | :--- |
| **Intake Wizard** | 4-step wizard: Consent, Symptoms/Voice, CBC OCR, Final Review. | Native progressive web app (PWA) offline intake form. |
| **Voice Capture** | 6-state interactive MediaRecorder with Odia/Hindi sample playback. | Real-time WebSocket streaming transcription chunking. |
| **Speech-to-Text** | Dual architecture: Faster-Whisper adapter + local mock fallback. | Bhashini AI integration for additional scheduled Indian languages. |
| **Lab Report OCR** | Complete Blood Count (CBC) parsing with confidence scores & checkboxes. | Multi-page handwriting recognition for handwritten doctor slips. |
| **Risk Stratification** | 6 deterministic rules (`TRIAGE-R01` to `TRIAGE-R06`) with provenance tags. | Manchester Triage System (MTS) expanded pediatric scoring matrix. |
| **Queue Management** | Prioritized queue sorted by acuity (`URGENT REVIEW`, `PRIORITY`, `ROUTINE`). | Multi-facility automated load balancing & tele-triage routing. |
| **Review Gate** | Chronological symptom timeline, SOAP editor, confirm/reject/escalate. | Biometric digital signature integration for attending physicians. |
| **Referrals** | High-contrast printable transfer slips with print stylesheet & synthetic ID. | ABDM / Ayushman Bharat Digital Mission health exchange bridge. |
| **Demonstrations** | 6 pre-configured synthetic public health scenarios with 1-click loading. | Scenario builder UI for custom training and academic simulation. |
| **Data Privacy** | In-flight regex scrubbing (Aadhaar, mobile, email) & 1-click case purge. | Automated differential privacy masking for epidemiological telemetry. |
| **Adaptive Connectivity** | Real-time 4-state network monitoring (`GOOD`, `NORMAL`, `SLOW`, `OFFLINE`), 4-bar indicator, safe API retry policies, and clinical intake guards. | Local offline queue with deferred cryptographically-signed sync. |
| **Role-Isolated Dashboards** | 4 strictly isolated environments (Patient, Doctor, Staff, Admin) with zero feature leakage, role-based navigation, and backend object authorization. | Granular sub-departmental access delegation. |

---

## 3. Multimodal Patient Intake Pipeline

The intake pipeline (`frontend/src/app/intake/page.tsx` and `backend/app/api/v1/endpoints/intake.py`) standardizes intake collection across four sequential stages:

### 3.1 Step 1: Consent & Demographics
- **Clinical Consent Acknowledgement**: Mandatory checkbox confirming understanding of the educational/support nature of the system.
- **Demographic Context**:
  - Age, Gender (Male, Female, Other).
  - Facility Type: Primary Health Center (PHC), Community Health Center (CHC), Government District Hospital, Outreach Camp, Campus Health Center.
  - Visit Type: First Visit, Follow-up, Routine Screening, Acute Presentation.
  - Patient Preferred Language: Odia (`or`), Hindi (`hi`), English (`en`).

### 3.2 Step 2: Symptom Intake & Audio Recording
- **Autosizing Narrative Input**: Free-text symptom input area for patients or community health workers (ASHAs/ANMs).
- **6-State Audio Recorder Engine** (`frontend/src/components/intake/voice-recorder.tsx`):
  1. `idle`: Ready to capture.
  2. `requesting_permission`: Browser microphone permission negotiation.
  3. `recording`: Active audio stream recording with visual pulse indicator and elapsed timer.
  4. `paused`: Pause capability during long intakes.
  5. `transcribing`: Processing audio stream via Faster-Whisper or local mock service.
  6. `completed` / `error`: Transcript ready for review or graceful recovery prompt.
- **Pre-Recorded Sample Audio Playback**: Built-in Odia and Hindi test recordings allowing instant evaluation without requiring live microphone hardware.

### 3.3 Step 3: Pathology Report OCR Parsing
- **Document Ingestion** (`frontend/src/components/intake/report-uploader.tsx`):
  - Upload support for pathology report images (JPEG, PNG) and synthetic sample injection.
  - Extraction of key Complete Blood Count (CBC) hematological parameters:
    - **Hemoglobin (Hb)** (g/dL)
    - **Total Leukocyte / White Blood Cell Count (WBC)** (cells/μL)
    - **Platelet Count** (lakhs/μL or /μL)
    - **Red Blood Cell Count (RBC)** (million/μL)
    - **Hematocrit (PCV)** (%)
- **Clinician Verification Controls**:
  - Field-level OCR confidence score display (`88%`, `94%`, etc.).
  - Manual numerical override inputs.
  - Individual verification checkboxes ensuring no unverified laboratory data enters the case file.

### 3.4 Step 4: Verification Review & Queue Dispatch
- Consolidated preview of all multimodal inputs (demographics, vernacular transcripts, English translations, and confirmed laboratory values).
- Single-action submission generating an immutable triage case record dispatched to the clinical queue.

---

## 4. Deterministic Clinical Risk Engine

Clinova AI rejects opaque "black-box" risk scoring. Urgency stratification is executed by a deterministic symbolic rules engine (`backend/app/services/risk_engine.py`) that strictly adheres to published clinical safety thresholds:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                   DETERMINISTIC CLINICAL RULES ENGINE                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
[ TRIAGE-R01 ]               [ TRIAGE-R02 ]               [ TRIAGE-R03 ]
Severe Respiratory           Severe Hemorrhage            Altered Consciousness
Distress (Dyspnea/Stridor)   & Active Bleeding            & Neurological Crisis
      │                            │                            │
      └────────────────────────────┼────────────────────────────┘
                                   ▼
                            URGENT REVIEW
```

### 4.1 Rule Definitions & Triggers

| Rule Code | Clinical Trigger Criteria | Urgency Classification | Mandatory Action |
| :--- | :--- | :--- | :--- |
| **`TRIAGE-R01`** | Stridor, cyanosis, gasping, severe dyspnea, SpO2 < 90%. | **URGENT REVIEW** (Red) | Immediate oxygenation & airway evaluation. |
| **`TRIAGE-R02`** | Profuse arterial bleeding, active hemorrhage, coughing/vomiting blood. | **URGENT REVIEW** (Red) | Direct wound compression, large-bore IV access, STAT Hb. |
| **`TRIAGE-R03`** | Unconscious, syncope, ongoing seizure, convulsion, sudden confusion. | **URGENT REVIEW** (Red) | Airway protection, capillary blood glucose, neurological check. |
| **`TRIAGE-R04`** | Crushing retrosternal chest pain, radiation to left arm/jaw, diaphoresis. | **URGENT REVIEW** (Red) | STAT 12-lead ECG within 10 min, vitals, cardiac monitoring. |
| **`TRIAGE-R05`** | High sustained pyrexia (temp ≥ 103°F or fever for 3+ days with chills). | **PRIORITY** (Amber) | Hydration, antipyretic review, malaria/dengue/sepsis screening. |
| **`TRIAGE-R06`** | Severe acute abdominal pain, intense abdominal guarding or cramps. | **PRIORITY** (Amber) | Surgical abdomen evaluation, ultrasound/X-ray, NPO status. |
| *Standard* | Non-acute presentations (routine cough, mild rash, follow-up). | **ROUTINE** (Emerald) | Standard outpatient order of arrival. |

### 4.2 Transparent Provenance Attribution
Every risk signal attaches a provenance tag indicating:
- The exact input modality that triggered the flag (`PATIENT_VOICE`, `TYPED_NARRATIVE`, `LAB_REPORT_OCR`, `VITAL_SIGNS`).
- The verbatim text or numerical value that met the rule threshold.

---

## 5. Prioritized Reviewer Queue

The triage queue (`frontend/src/app/review/page.tsx`) provides attending clinical staff with an overview of all active patient cases:
- **Acuity Sorting**: Automatic prioritization placing `URGENT REVIEW` cases at the top of the queue, followed by `PRIORITY` and `ROUTINE`.
- **Transparent Rule Badges**: High-contrast badges displaying the triggered rule codes (`TRIAGE-R01`, `TRIAGE-R06`) so clinicians immediately understand *why* a case is elevated.
- **Queue Filtering**: Instant filters for urgency level, facility origin, and patient search.
- **Direct Session Launch**: One-click navigation into the dedicated clinical case review interface.

---

## 6. Medical Officer Case Review & Human Gate

The case review interface (`frontend/src/app/review/case/[caseId]/page.tsx`) serves as the core human-in-the-loop safety checkpoint:

### 6.1 Chronological Symptom Timeline
Transforms unstructured narrative history into a clean visual progression:
- **Day 1**: Onset of mild prodromal symptoms.
- **Day 2**: Progression of acute complaints and self-medication history.
- **Day 3 / Presentation Day**: Acute exacerbation triggering facility visit.

### 6.2 Provenance-Linked SOAP Note Editor
Presents an editable clinical note synthesized in standard SOAP format:
- **Subjective (S)**: Patient's chief complaint, history of presenting illness, and verbatim vernacular transcript.
- **Objective (O)**: Confirmed vitals and verified laboratory parameters (CBC).
- **Assessment (A)**: Syndromic categorization and deterministic risk rules triggered.
- **Plan (P)**: Recommended preliminary nursing interventions, required diagnostics, and referral options.
- *Full Editing Capability*: Attending medical officers can edit any section before finalizing.

### 6.3 Attending Clinician Human Gate
Four standardized review actions:
1. **Confirm & Approve Note**: Accepts the note, records clinician digital identity and UTC timestamp in audit logs, and marks case as `reviewed`.
2. **Edit Summary**: Saves manual clinician revisions to the SOAP note.
3. **Escalate**: Immediately marks the case for emergency physician or secondary facility transfer.
4. **Reject**: Marks triage summary as invalid with mandatory clinician feedback notes.

### 6.4 One-Click Privacy Data Purge
Attending clinicians can click **Delete Case Data** (`DELETE /api/v1/cases/{case_id}`) to immediately purge transient voice recordings and raw report scans from the server.

---

## 7. Standardized Clinical Referral Document

For cases requiring secondary or tertiary hospital transfer, Clinova AI generates a standardized referral note (`frontend/src/app/review/case/[caseId]/referral/page.tsx`):
- **High-Contrast Print Layout**: Tailored for black-and-white hospital thermal or laser printers using CSS `@media print`.
- **Institutional Header**: Facility name, synthetic patient code, date/time, attending officer name.
- **Clinical Summary Block**: Finalized SOAP note, verified lab parameters, and triggered emergency rule badges.
- **Non-Diagnostic Disclaimer**: Prominent header and footer notice stating that the document is a transfer triage summary and requires clinical evaluation at the receiving facility.
- **Browser Print / PDF Trigger**: One-click button initiating standard browser print or save-as-PDF dialog.

---

## 8. Interactive Clinical Demonstration Hub

The demonstration hub (`frontend/src/app/demo/page.tsx`) enables immediate evaluation of Clinova AI's capabilities without entering manual data:
- **6 Pre-Configured Synthetic Scenarios**:
  1. `CLV-DEMO-001`: Campus acute fever outbreak with dyspnea (Odia).
  2. `CLV-DEMO-002`: Agrarian deep laceration with active hemorrhage (Hindi).
  3. `CLV-DEMO-003`: Pediatric high fever and dehydration alert (Odia).
  4. `CLV-DEMO-004`: Geriatric crushing retrosternal chest pain (English).
  5. `CLV-DEMO-005`: Thrombocytopenia / Platelet deficiency alert (CBC OCR).
  6. `CLV-DEMO-006`: Routine corporate occupational health follow-up.
- **3-Minute Clinical Demonstration Workflow**: Guided step-by-step instructions showing the complete intake-to-referral lifecycle.

---

## 9. EHR Patient Registry & Consultations

In addition to acute triage, Clinova AI provides core electronic health record (EHR) foundations:
- **Patient Registry (`/patients`)**: Search, register, and manage synthetic patient profiles with demographics, contact data, and medical history.
- **Consultation Lifecycle (`/consultations`)**: Create and document clinician consultations linked to specific patient records, recording chief complaints, clinical observations, diagnoses, and prescriptions.

---

## 10. Adaptive Low-Bandwidth & Real-Time Network Monitoring

Designed for rural primary health clinics operating over unstable 2G/3G cellular networks, satellite links, or intermittent connectivity:

### 10.1 Centralized Connectivity State Engine
- **Engine Provider (`frontend/src/lib/connectivity.tsx`)**: Single source of truth React Context (`useConnectivity`) managing network telemetry and UI state across the entire application.
- **4 Discrete Connectivity States**:
  1. `GOOD` (4 bars: `[████]`, Green): RTT < 250ms, packet loss < 2%. Full interactive features, animations, and standard polling active.
  2. `NORMAL` (3 bars: `[███░]`, Teal/Blue): RTT 250ms–700ms. Standard operation with normal request timeouts (14s).
  3. `SLOW` (2 bars: `[██░░]`, Amber): RTT > 700ms or 2G/slow-2g reported by NetworkInformation API. Automatic low-bandwidth mode activates: decorative animations disabled, request timeouts extended to 30s, telemetry reduced, warning toasts displayed on high-payload actions.
  4. `OFFLINE` (0 bars: `[░░░░]`, Red): Complete loss of connectivity (`!navigator.onLine` or 3 consecutive failed health pings). Mutation buttons disabled, offline banners displayed.
- **Debouncing & Hysteresis**:
  - State upgrades require **3 consecutive samples** within target threshold to eliminate flickering and flip-flopping under jitter.
  - Latency calculated using a rolling median of the last 5 samples to resist transient spikes.
  - Active sampling: periodic heartbeat ping to lightweight `/api/v1/ping` endpoint (every 15s in normal operation, 45s when degraded, 5s during offline recovery probes).
  - Passive sampling: every `apiClient` HTTP request records round-trip duration and feeds into the median filter.

### 10.2 User Operating Modes
- **`AUTOMATIC` (Default)**: Automatically activates low-bandwidth optimizations when connection degrades to `SLOW` or `OFFLINE`, and restores full experience when connection recovers to `GOOD` or `NORMAL`.
- **`NORMAL`**: Forces standard interface regardless of network conditions (useful for diagnostic override).
- **`LOW_BANDWIDTH`**: Manually forces data-saver mode at all times (disables animations, simplifies layout rendering, minimizes polling).
- **Persistence**: User mode preference persisted in `localStorage` under `clinova_network_mode`.

### 10.3 Visual Network Indicator & Diagnostics Popover
- **Compact Header Badge (`frontend/src/components/common/network-indicator.tsx`)**:
  - Visual 4-bar signal strength graphic (`[████]`, `[███░]`, `[██░░]`, `[░░░░]`).
  - Acuity-coded color tokens (emerald green, sky blue, amber, crimson).
  - Real-time latency readout (e.g., `42 ms`) and state label.
- **Interactive Diagnostics Modal**:
  - Accessible via click on the header network badge.
  - Live diagnostics: Connection state, effective round-trip time (RTT), user-selected mode, downlink speed estimate, and system timestamp.
  - Mode switcher allowing one-click toggle between Automatic, Normal, and Forced Low-Bandwidth.
  - Immediate "Test Connection Now" ping trigger.

### 10.4 Safe API Behavior & Idempotency Rules
- **Idempotent Retry Only (`frontend/src/lib/api.ts`)**:
  - `GET` requests: Retried up to 2 times with exponential backoff on transient network failures (`fetch` exceptions, 502, 503, 504).
  - Mutation requests (`POST`, `PUT`, `DELETE`): **NEVER retried automatically**. Prevents duplicate patient records, duplicate case submissions, or conflicting triage state transitions during network hiccups.
- **Offline Fast-Fail**: API calls fail immediately with clear client error when `OFFLINE`, preventing hanging requests and unhelpful browser timeout delays.

### 10.5 Clinical Workflow Guards
- **Intake Submission (`/intake`)**: Submit button disabled while offline; shows warning banner with instructions to maintain browser tab open until connection restores.
- **Voice Symptom Recorder**: Offline capture blocked with warning banner; low-bandwidth mode displays notification that audio transcription may experience slight latency.
- **Lab Report OCR**: File upload blocked while offline; low-bandwidth mode increases upload timeout to 30s with progress indicator.
- **Review Queue & Dashboard (`/review`, `/dashboard`)**: Displays non-intrusive offline banner alerting clinicians that queue updates are paused until reconnection.

### 10.6 PHI Privacy Safeguard
- **Zero Local PHI Caching**: In accordance with medical privacy standards, patient intake data and clinical notes are **never** stored unencrypted in `localStorage` or `sessionStorage` as an "offline cache", preventing PHI leaks on shared clinical workstations.

---

## 11. In-Flight Privacy & Medicolegal Audit

- **In-Flight PII Redaction** (`backend/app/services/anonymizer.py`): Automatically detects and masks Indian 10-digit mobile numbers, email addresses, and 12-digit Indian Aadhaar numbers before storage or AI processing.
- **Immutable Audit Logging** (`backend/app/services/audit.py`): Every case intake, voice transcription, OCR extraction, clinician review approval, and data purge is logged with UTC timestamp, user ID, IP address, and cryptographic action description.
