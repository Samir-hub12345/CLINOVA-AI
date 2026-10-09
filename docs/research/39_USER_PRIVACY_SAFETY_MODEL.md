# CLINOVA AI — User Privacy, Safety & Information Boundary Specification

> **Document ID:** `RES-39`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Healthcare Information Privacy, Safety & Regulatory Governance Group  

---

## 1. Executive Summary & Legal Framework

This document establishes the conceptual **privacy, safety, and information governance boundaries** for CLINOVA AI.

The specification is strictly aligned with:
1. **The Digital Personal Data Protection (DPDP) Act 2023 (India)**: Enforcing purpose limitation, data minimization, consent lifecycle, and rights of Data Principals.
2. **Ayushman Bharat Digital Mission (ABDM) Health Data Management Policy**: Establishing federated architecture, Health Information Provider (HIP) and Health Information User (HIU) boundaries, and explicit consent artifact binding.
3. **National Medical Commission (NMC) Professional Conduct Regulations 2023**: Governing physician-patient confidentiality and digital telemedicine records.
4. **Mandatory BPUT Baseline Contracts**: Specifically `B14` (Consent Capture), `B15` (Privacy & Anonymization), `B16` (24-Hour Ephemeral Retention), `B17` (Auditability), and `B18` (Non-Diagnostic Advisory Safeguards).

> **CRITICAL ARCHITECTURAL DIRECTIVE:**  
> This specification defines the **conceptual privacy model only**.  
> No cryptographic software, tokenization libraries, or database migration code is implemented in this phase.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA PRIVACY & GOVERNANCE ARCHITECTURE             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ RAW INGESTION ] ──> In-Flight PII Redaction & Synthetic Tokenization     │
│           │                                                                 │
│           ▼                                                                 │
│  [ ROLE PARTITIONING ] ──> Minimum Necessary Standard Across 8 Roles        │
│           │                                                                 │
│           ▼                                                                 │
│  [ CONSENT ENGINE ] ──> Digital, Verbal, Surrogate & Emergency Implied      │
│           │                                                                 │
│           ▼                                                                 │
│  [ RETENTION DISPOSAL ] ──> 24-Hour Ephemeral Purge of Voice & Scans        │
│           │                                                                 │
│           ▼                                                                 │
│  [ AUDIT LEDGER ] ──> Immutable Cryptographic Append-Only Ledger            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Personally Identifiable Information (PII) Exposure Risks & Containment

In frontline hospital triage, patients routinely share sensitive personal identifiers: government ID numbers (Aadhaar, Voter ID, Ration Card), mobile phone numbers, street addresses, and workplace information.

### 2.1 Threat Vector Matrix

| PII Attribute | Raw Exposure Point | Threat Vector | System Containment Mechanism |
|:---|:---|:---|:---|
| **Phone Number** | Spoken in voice intake or typed in contact field. | Unsolicited calls, stalking, commercial data broker leaks. | In-flight regex redaction; replaced with synthetic token `TEL-[REDACTED]`; accessible only in emergency call module. |
| **Government ID (Aadhaar / ABHA)** | Written on uploaded physical OPD cards or lab slips. | Identity theft, fraudulent health benefit claims. | Computer vision OCR masking; redacts 12-digit Aadhaar to `XXXX-XXXX-1234`; ABHA preserved only in cryptographically hashed index. |
| **Full Legal Name** | Spoken or typed during registration. | Waiting room identity exposure; social stigma (HIV, psych). | Displayed only on direct examining physician terminal; public queue boards show strictly `Token #XX` or `PT-XXXXXX`. |
| **Facial Imagery** | Uploaded document photos containing passport pictures. | Facial recognition surveillance; non-consensual tracking. | Automatic image pre-processing crops only the clinical table/text; discards peripheral portrait photos. |
| **Voice Audio Biometrics** | Spoken symptom recording. | Voiceprint harvesting and biometric profiling. | **24-Hour Ephemeral Disposal Rule (`B16`)**: Raw audio files are permanently purged 24 hours post-consultation. |

---

## 3. The Minimum Necessary Access Standard

Access to patient data is governed by the statutory **Minimum Necessary Standard**: a user may only view the exact data attributes required to perform their specific operational duty.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA VISIBILITY BOUNDARIES BY USER ROLE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ROLE_CLINICIAN      │ FULL ACCESS (All clinical parameters, raw evidence)  │
│  ROLE_NURSE          │ PARTIAL (Assigned intake, vitals, checklists)        │
│  ROLE_REFERRAL_STAFF │ LOGISTICAL ONLY (Referral summary, required facility)│
│  ROLE_PATIENT        │ OWN APPROVED ONLY (Doctor-signed summary & advice)   │
│  ROLE_CAREGIVER      │ AUTHORIZED ONLY (Same scope as patient)              │
│  ROLE_FACILITY_ADMIN │ AGGREGATED ONLY (Queue wait times, bed counts, zero PII)│
│  ROLE_SYSTEM_ADMIN   │ INFRASTRUCTURE ONLY (System health, error logs, zero PII)│
│  ROLE_RESEARCHER     │ SYNTHETIC ONLY (Zero production data, de-identified) │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Granular Data Visibility Breakdown

| Data Domain | Clinician | Nurse | Referral Staff | Patient / Caregiver | Facility Admin | System Admin | Researcher |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Demographics (Name, Age, Sex)** | **FULL** | **FULL** | Minimal (Age/Sex) | **OWN** | Zero | Zero | Zero (Synthetic) |
| **Raw Voice Audio & Document Scans** | **FULL** | Assigned Only | ❌ DENIED | Own Uploads | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| **Extracted Discrete Vitals & Labs** | **FULL** | Assigned Only | Pertinent Only | Approved Only | Aggregated Only| Zero | De-identified |
| **Longitudinal Clinical Timeline** | **FULL** | Assigned Only | Summary Only | Approved Only | Zero | Zero | De-identified |
| **AI Trajectory & Uncertainty ($U_t$)**| **FULL** | Red Flags Only | Feasibility Tag | ❌ DENIED | Zero | Zero | Calibration Stats |
| **AI Draft Triage Notes** | **FULL** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | Benchmark Runs |
| **Doctor Confidential Scratchpad** | **FULL** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| **Hospital Capacity & Bed Counts** | Pertinent | Triage Bay | Destination | ❌ DENIED | **FULL** | System Telemetry | Zero |
| **Cryptographic Security Audit Log** | Case Trail | Own Action | Transfer Log | Own Access Rec | Departmental | **FULL LEDGER** | ❌ DENIED |

---

## 4. Multi-Modal Consent Lifecycle (`B14`)

Under the DPDP Act 2023, consent must be free, specific, informed, unconditional, and unambiguous with clear affirmative action.

CLINOVA establishes four distinct consent modalities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FOUR CONSENT ARCHETYPES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. DIRECT DIGITAL CONSENT (Self-Service Kiosk / Mobile App)                │
│     Clear vernacular checkboxes; affirmative tap; revocable at any time.    │
│                                                                             │
│  2. STAFF-ATTESTED VERBAL CONSENT (Frontline Assisted Intake)               │
│     Nurse reads standardized vernacular script; checks "Verbal Consent Given"│
│                                                                             │
│  3. SURROGATE LEGAL CONSENT (Pediatric / Incapacitated)                     │
│     Documented guardian or accompanying relative attests to representation. │
│                                                                             │
│  4. EMERGENCY IMPLIED CONSENT (Unconscious / Critical Trauma)               │
│     Statutory doctrine of necessity; life-saving care without digital gate. │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Right to Revoke Consent
A patient may revoke consent prior to clinical finalization. Upon revocation:
- Active intake draft is purged immediately from local memory.
- Case status transitions to `ENCOUNTER_CANCELLED_BY_PATIENT`.
- An immutable audit entry records the revocation event without storing clinical text.

---

## 5. 24-Hour Ephemeral Retention Policy (`B16`)

A core privacy differentiator of CLINOVA AI is its **Zero-Data-Hoarding Principle**:

> **The Ephemeral Disposal Invariant:**  
> Raw multi-modal media artifacts (raw audio recordings, raw microphone waveforms, camera document scans, and un-redacted OCR image crops) are retained strictly on ephemeral local storage for a maximum of **24 hours** post-encounter finalization.

### 5.1 Disposal Protocol
1. **At Final Sign-Off:** Clinician reviews raw audio and OCR crops; confirms discrete clinical parameters; digitally signs the Master Clinical Report.
2. **Discrete Parameter Preservation:** The verified clinical values (e.g., "Hemoglobin: 11.2 g/dL", "Heart Rate: 84 bpm") are persisted in the encrypted Master Case record.
3. **Automated Purge Cron:** An automated local script executes every 60 minutes:
   - Scans media directory for artifacts where `encounter_finalized_timestamp < now() - 24 hours`.
   - Executes multi-pass cryptographic shredding of the raw audio (`.wav`) and document scan (`.png`, `.pdf`) files.
   - Updates `EvidenceNode` record to replace raw file binary with permanent SHA-256 integrity hash: `RAW_ARTIFACT_EXPIRATION_PURGED`.

---

## 6. Staff-to-Staff Information Sharing & Shift Handoff Safety

In 24/7 hospital casualty setups, patients frequently span multiple staff shifts. Miscommunication during nursing or doctor handoffs is a leading cause of adverse clinical events.

### 6.1 Shift Handoff Protocol
1. **Single Master Case State:** Arriving doctors do not receive second-hand verbal notes; they log into the terminal and view the identical, live CAREGRAPH state.
2. **Session Termination Gate:** At shift conclusion, departing doctors click "End Shift / Handoff". The system forces review of any un-finalized cases in their active queue.
3. **Handoff Custody Transfer:** Departing doctor assigns active cases to incoming doctor ID. Case audit trail records `CUSTODY_TRANSFERRED(from: DOC_A, to: DOC_B)`.

---

## 7. Data Export Restrictions & Anti-Exfiltration Controls

To prevent bulk clinical data exfiltration and illegal commercial harvesting:

1. **Strict Prohibition on Bulk CSV / JSON Exports:** Frontline clinical and nursing roles have zero ability to execute bulk database queries or download bulk patient spreadsheets.
2. **Individual Watermarked PDF Exports Only:**
   - Single-case exports (Master Clinical Report, Emergency Pack, Referral File) are generated as watermarked PDF documents.
   - Watermark embeds: Requesting Clinician User ID, Medical Registration Number, Timestamp, and Patient Synthetic ID.
3. **Role-Gated Download Rights:** Only licensed clinicians can export full medical reports. Administrative staff can only export aggregated, non-clinical operational metrics.
