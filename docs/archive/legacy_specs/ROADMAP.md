# CLINOVA AI — Product & Clinical Informatics Roadmap

**Document Version:** 1.0.0  
**Status:** Living Strategy Document  
**Current Baseline:** v0.2.0 (Integrated Staging)  
**Planning Horizon:** 2026 – 2027  

---

> [!WARNING]
> ### 🔒 Clinical Safety & Non-Diagnostic Roadmap Mandate
> **Strict Adherence to Non-Autonomous Triage.** All future architectural and functional additions to CLINOVA AI must strictly adhere to the human-in-the-loop clinical safety mandate: the system is an educational and decision-support assistant; it must **never** make autonomous medical diagnoses, issue unvalidated drug prescriptions, or bypass qualified attending healthcare personnel.

---

## Table of Contents

1. [Current Operational Baseline (v0.2.0)](#1-current-operational-baseline-v020)
2. [Strategic Vision & Architectural Pillars](#2-strategic-vision--architectural-pillars)
3. [Phase 1: Near-Term Enhancements (Q4 2026)](#3-phase-1-near-term-enhancements-q4-2026)
4. [Phase 2: Mid-Term Capabilities (Q1–Q2 2027)](#4-phase-2-mid-term-capabilities-q1q2-2027)
5. [Phase 3: Long-Term Ecosystem Integration (Q3–Q4 2027)](#5-phase-3-long-term-ecosystem-integration-q3q4-2027)
6. [Feature Prioritization Matrix](#6-feature-prioritization-matrix)
7. [Clinical Governance & Ethics Review](#7-clinical-governance--ethics-review)

---

## 1. Current Operational Baseline (v0.2.0)

As of release **v0.2.0**, the following core capabilities are verified and operational within the repository:

- **Multimodal Intake Wizard (`/intake`)**: 4-step workflow capturing patient demographics, 6-state browser audio recordings with Odia/Hindi samples, and Complete Blood Count (CBC) report OCR extraction with confidence verification.
- **Deterministic Risk Signal Engine (`risk_engine.py`)**: 6 auditable rules (`TRIAGE-R01` to `TRIAGE-R06`) driving priority categorization (`URGENT REVIEW`, `PRIORITY`, `ROUTINE`) with transparent provenance tags.
- **Prioritized Review Queue (`/review`)**: Acuity-sorted dashboard for attending clinical personnel with filter and search capabilities.
- **Case Review & Human Gate (`/review/case/[caseId]`)**: Symptom progression timeline, editable SOAP summary generator, human confirmation/rejection gate, and one-click data purge.
- **Printable Referral Note (`/referral`)**: Standardized high-contrast transfer slip for secondary care facility handoff.
- **Synthetic Demonstration Scenarios (`/demo`)**: 6 pre-configured public health cases and 3-minute clinical evaluation script.
- **Security & Privacy Layer**: In-flight PII redaction (Aadhaar, mobile, email), JWT HS256 authentication, and append-only medicolegal audit logging.
- **Zero-Cloud Offline Reliability**: Deterministic mock fallbacks (`DEMO_MODE=True`) allowing complete offline operation without cloud API keys.

---

## 2. Strategic Vision & Architectural Pillars

CLINOVA AI evolves around four guiding principles designed for public health resilience in India:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                       FOUR ARCHITECTURAL PILLARS                        │
├───────────────────┬───────────────────┬───────────────────┬─────────────┤
│ 1. Zero-Bypass    │ 2. Vernacular     │ 3. Edge-First     │ 4. ABDM     │
│    Human Gate     │    Inclusivity    │    Offline Sync   │    Aligned  │
│                   │                   │                   │             │
│ Clinician retains │ Native Indian     │ Fully operational │ Seamless    │
│ final decision    │ languages without │ in air-gapped     │ national    │
│ authority on all  │ translation       │ rural health      │ health data │
│ clinical actions. │ latency.          │ sub-centers.      │ exchange.   │
└───────────────────┴───────────────────┴───────────────────┴─────────────┘
```

---

## 3. Phase 1: Near-Term Enhancements (Q4 2026)

### 3.1 Manchester Triage System (MTS) Pediatric Matrix
- Expand the deterministic risk engine to include age-stratified pediatric discriminators:
  - Pediatric tachypnea thresholds (age-adjusted breaths/min).
  - Capillary refill time (> 3 seconds indicating circulatory shock).
  - Lethargy and sunken fontanelle dehydration scoring in infants.

### 3.2 Offline Progressive Web App (PWA)
- Installable web app for Android tablets used by Accredited Social Health Activists (ASHAs) and Auxiliary Nurse Midwives (ANMs).
- Client-side IndexedDB storage buffering walk-in intake forms locally during community outreach camps.

### 3.3 Vernacular Dialect Dictionaries
- Expansion of phonetic matching dictionaries to cover sub-regional dialects:
  - Odia: Sambalpuri, Desia, and Cuttacki vernacular medical idioms.
  - Hindi: Bhojpuri, Maithili, and Bundelkhandi colloquial symptom expressions.

### 3.4 Cryptographic Clinician Sign-Off (FIDO2 / Biometric)
- Integration of WebAuthn / FIDO2 biometric authentication allowing attending medical officers to sign referral notes using USB fingerprint readers or device biometric sensors.

---

## 4. Phase 2: Mid-Term Capabilities (Q1–Q2 2027)

### 4.1 Real-Time Streaming Audio Transcription
- Upgrade from batch audio submission to live WebSocket chunked streaming:
  - Sub-second transcription display as the patient speaks.
  - Automatic silence and hesitation detection to guide clinical interview pacing.

### 4.2 Bhashini AI Ecosystem Integration
- Native integration with Project Bhashini (National Language Translation Mission of India):
  - Ingestion and synthesis support for additional 22 scheduled Indian languages (Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, and Punjabi).

### 4.3 Multi-Page Handwritten Prescription Vision Pipeline
- Fine-tuned optical recognition using PaddleOCR and specialized handwriting transformers:
  - Digitizing handwritten OPD prescription slips from primary care doctors.
  - Extracting prior medication regimens, allergies, and surgical histories.

### 4.4 Conflict-Free Replicated Data Types (CRDT) Multi-Device Sync
- Peer-to-peer and local mesh network synchronization enabling multiple triage tablets at a remote health camp to synchronize intake records without requiring an active internet connection.

---

## 5. Phase 3: Long-Term Ecosystem Integration (Q3–Q4 2027)

### 5.1 ABDM / Ayushman Bharat Digital Mission Gateway
- Full compliance with national health exchange milestones:
  - **Milestone 1 (M1)**: ABHA (Ayushman Bharat Health Account) creation and QR-code patient verification at check-in.
  - **Milestone 2 (M2)**: Health Information Provider (HIP) capability to publish verified triage notes to the patient's personal health record (PHR).
  - **Milestone 3 (M3)**: Health Information User (HIU) integration to securely pull longitudinal clinical history across hospitals.

### 5.2 Acoustic Respiratory Biomarker Profiling
- Advanced audio signal processing on voluntary cough sounds and breath audio:
  - Pre-screening triage assistance for pediatric wheezing, asthma exacerbations, and suspected tuberculosis (TB) in rural screening camps.

### 5.3 District Hospital Bed & Telemetry Integration
- Live API integration with district hospital admission and bed tracking dashboards:
  - Automated referral recommendation based on real-time ICU, ventilator, and oxygen bed availability at receiving facilities.

### 5.4 Privacy-Preserving Syndromic Cluster Surveillance
- Federated, zero-knowledge telemetry aggregation:
  - Anonymized epidemiological cluster detection (e.g., sudden spikes in acute diarrheal illness or high-fever presentations within a specific pin code) alerting district public health surveillance officers.

---

## 6. Feature Prioritization Matrix

| Roadmap Feature | Target Phase | Clinical Safety Impact | Technical Complexity | Regulatory Requirement |
| :--- | :---: | :---: | :---: | :---: |
| **MTS Pediatric Triage Matrix** | Phase 1 (Q4 2026) | High | Medium | Clinical Advisory Board Approval |
| **Offline PWA Intake Form** | Phase 1 (Q4 2026) | Medium | Low | DISHA Storage Compliance |
| **Vernacular Dialect Expansion** | Phase 1 (Q4 2026) | High | Medium | Linguistic Validation Review |
| **Streaming WebSocket STT** | Phase 2 (Q1 2027) | Medium | High | Data In-Transit Security |
| **Bhashini AI Integration** | Phase 2 (Q2 2027) | High | Medium | Bhashini API Licensing |
| **Handwritten Prescription OCR** | Phase 2 (Q2 2027) | High | High | Accuracy Benchmarking (>92%) |
| **Offline Mesh CRDT Sync** | Phase 2 (Q2 2027) | High | High | Data Conflict Invariant Audit |
| **ABDM / ABHA Gateway (M1-M3)** | Phase 3 (Q3 2027) | High | High | NHA Sandbox Certification |
| **Acoustic Cough Biomarkers** | Phase 3 (Q3 2027) | Critical | High | Clinical Trial & CDSCO Clearance |
| **Hospital Bed Telemetry** | Phase 3 (Q4 2027) | High | Medium | State Health Department MOU |

---

## 7. Clinical Governance & Ethics Review

Every roadmap milestone that touches clinical rule thresholds, language models, or medical recommendations must pass a four-stage review gate:

1. **Deterministic Clinical Audit**: Verification that deterministic safety rules override statistical model predictions in all edge cases.
2. **Clinical Advisory Review**: Review and sign-off by licensed physicians (MD / MS) on clinical terminology and referral criteria.
3. **Medicolegal Compliance Check**: Verification against DISHA, ABDM, and Indian medical council guidelines.
4. **Synthetic Regression Testing**: Automated execution of synthetic edge-case test suites asserting zero triage safety regressions.
