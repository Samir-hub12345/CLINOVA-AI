# CLINOVA AI — User Need to Product Traceability Matrix

> **Document ID:** `RES-40`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Product Traceability Group  

---

## 1. Executive Summary & Traceability Mandate

This document establishes the **end-to-end bidirectional traceability matrix** connecting real-world frontline user needs to concrete product capabilities, data requirements, algorithmic mechanisms, human decisions, expected outcomes, verification test contracts, and future roadmap implementation phases.

> **CRITICAL ARCHITECTURAL DIRECTIVE:**  
> This matrix maps user needs to architectural specifications and future implementation targets.  
> **NO code, UI components, backend APIs, or database schemas are implemented in Phase 3.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    10-DIMENSION TRACEABILITY CHAIN                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  USER NEED ──> USER ROLE ──> REAL PROBLEM ──> PRODUCT CAPABILITY           │
│       │                                                                     │
│       ▼                                                                     │
│  DATA REQUIRED ──> AI / DETERMINISTIC SUPPORT ──> HUMAN DECISION GATE       │
│       │                                                                     │
│       ▼                                                                     │
│  EXPECTED CLINICAL OUTCOME ──> TEST REQUIREMENT ──> IMPLEMENTATION PHASE    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master User Need to Product Traceability Matrix

| # | User Need | User Role | Real Problem Faced | Product Capability | Data Required | AI / Deterministic Support | Human Decision Gate | Expected Outcome | Verification Test Requirement | Implementation Phase |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---:|
| **01** | Rapidly triage waiting patients without manual charting delay. | Primary Clinician (`ROLE_CLINICIAN`) | 90-second OPD consult time; spending 6 minutes typing EHR notes leads to doctor burnout and queue gridlock. | **Reviewer Dashboard & Structured Note Synthesis** (`B12`, `B18`) | Multimodal patient inputs, verified vitals, active red flags. | Local SLM (Qwen2.5-3B) synthesizes structured SBAR draft tagged `AI_INFERRED`. | Clinician verifies, modifies in-place, or discards note draft. | Intake review time reduced from 6 mins to $< 60$ seconds; zero unverified notes committed. | Test note synthesis; verify doctor can edit any field and sign off in $< 60$s. | **Phase 5** (Doctor UI) & **Phase 6** (Engine) |
| **02** | Detect deteriorating patients sitting unobserved in waiting halls. | Primary Clinician & Triage Nurse | Patients wait 2–5 hours; static triage tags miss progressive septic shock or internal bleeding. | **CAREGRAPH Dynamic Trajectory Engine** (`C01`) | Serial timestamped vitals readings (BP, HR, SpO2, RR, Temp). | Deterministic NEWS2 + temporal delta calculation ($\Delta R_t / \Delta t$) calculates trajectory slope. | Doctor reviews auto-promoted patient; immediately pulls forward to exam room. | Zero silent waiting-room deaths; deteriorating cases escalated within 60 seconds of vital update. | Ingest serial vitals with worsening HR/BP; verify patient jumps to top of queue with audible alert. | **Phase 6** (CAREGRAPH Core) |
| **03** | Verify raw evidence behind AI claims before trusting extracted facts. | Primary Clinician (`ROLE_CLINICIAN`) | Clinicians distrust black-box AI notes; cannot waste time searching through crumpled paper files. | **Multi-Source Evidence Provenance** (`C02`) | Raw audio recordings, document images, OCR bounding boxes. | Bounding-box and audio timecode linking engine connecting discrete facts to source snippets. | Doctor clicks fact chip to inspect cropped image or listen to audio waveform. | High clinician trust; extraction errors caught in $< 3$ seconds before ordering treatment. | Click discrete lab value; verify interface opens exact cropped image box of physical lab sheet in $< 300$ms. | **Phase 4** (Data Schema) & **Phase 5** (UI Provenance Drawer) |
| **04** | Prevent dangerous false certainty when critical vitals are missing. | Primary Clinician & Triage Nurse | Existing CDSS treat missing fields as normal, masking acute danger behind false confidence. | **Epistemic Uncertainty Engine ($U_t$)** (`C03`) | Extracted clinical entities vs syndrome-specific required checklist. | Conformal prediction principles calculating mathematical uncertainty scalar $U_t \in [0, 1]$. | Doctor sees prominent amber Uncertainty Card; orders physical measurement of missing vital. | Clinicians never act on false confidence; routine discharge blocked when critical fields unknown. | Ingest chest pain case missing BP and SpO2; verify $U_t > 0.50$ and routine discharge is disabled. | **Phase 6** (Uncertainty Core) |
| **05** | Eliminate "Blind Transfers" that arrive at hospitals without open beds. | Referral Staff & Medical Officer | Over 50% of rural emergency transfers arrive at facilities lacking ICU beds, ventilators, or surgeons. | **FACILITYGRAPH Care Feasibility Engine** (`C05`, `C06`) | Patient clinical requirements vs 5-tier institutional capability profiles. | Multi-tier boolean prerequisite matcher combined with Haversine distance travel optimization. | Doctor signs clinical transfer order; Referral Staff confirms destination bed via telephone. | 100% of referred patients routed to verified capable facilities; zero transit turn-aways. | Test referral matching for acute neuro trauma; verify facility lacking on-duty neurosurgeon is rejected. | **Phase 6** (FACILITYGRAPH Engine) |
| **06** | Receive real-time outbreak surge context while examining febrile patients. | Primary Clinician (`ROLE_CLINICIAN`) | Doctors submit disease tallies to IHIP/IDSP but receive zero real-time feedback during active triage. | **SIGNALGRAPH Telemetry Loop** (`C07`) | De-identified syndromic tags from surrounding clinics over 7-day rolling window. | Statistical moving-average anomaly detector calculating syndromic cluster $z$-scores ($z > 2.58$). | Doctor sees alert banner (e.g., *"3.4x Dengue Surge"*); heightens diagnostic suspicion. | Earlier recognition of epidemic clusters; timely ordering of confirmatory serology panels. | Simulate 20 febrile thrombocytopenia cases in 24h; verify banner alert appears on clinic dashboard. | **Phase 6** (SIGNALGRAPH Core) |
| **07** | Communicate symptoms in native vernacular speech without literacy barriers. | Patient (`ROLE_PATIENT`) | Rural patients in Odisha speaking colloquial Odia cannot type or understand English healthcare apps. | **Multilingual Vernacular Audio Intake** (`B01`, `B02`, `B09`) | Spoken microphone audio in Odia, Hindi, or Indian English. | Local faster-whisper speech-to-text combined with clinical concept normalization engine. | Patient confirms transcribed vernacular words; nurse assists if needed. | Illiterate citizens independently communicate symptoms; colloquial terms mapped to SNOMED concepts. | Ingest native Odia audio sample ("Mu mundabindha heuchi"); verify correct transcription and clinical mapping. | **Phase 4** (Audio Pipeline) & **Phase 5** (Intake Kiosk) |
| **08** | Rapidly collect objective vitals without creating duplicate patient charts. | Triage Nurse (`ROLE_NURSE`) | Frontline nurses forced to re-register patients across disconnected forms, fragmenting care records. | **Single Master Case Staff Checklist** (`B07`, `DOC-06`) | Synthetic patient ID (`PT-XXXXXX`), objective vital sign readings. | Real-time physiological range bounds checking (e.g., HR 20–260 bpm; SpO2 50–100%). | Nurse validates abnormal reading; signs off on vital signs entry. | All vitals append directly to existing Master Case; duplicate patient records eliminated. | Test nurse vital submission; verify vitals append to active `case_id` without generating a second record. | **Phase 4** (Case Model) & **Phase 5** (Nurse Station) |
| **09** | Close clinical information gaps without exhausting patient with long forms. | Patient & Nurse | 50-question clinical intake forms cause high abandonment rates and noisy, inaccurate responses. | **Next-Best Information (NBI) Engine** (`C04`, `B08`) | Identified clinical gaps from Missing Information Audit. | Value-of-Information (VOI) ranking algorithm selecting at most 3 maximum-yield clarifying questions. | Patient taps single-click radio button response in native language. | 80%+ uncertainty reduction achieved in $< 45$ seconds with zero patient questionnaire fatigue. | Ingest acute headache case; verify system asks duration and neck stiffness, ignoring unrelated questions. | **Phase 6** (NBI Algorithm) |
| **10** | Safeguard employee medical privacy from corporate HR and employer access. | Patient (Employee) & Company Clinic MO | Employees avoid corporate health clinics fearing health disclosures will impact jobs or appraisals. | **Role-Partitioned Privacy Gateway** (`DOC-23`, `RES-39`) | Occupational health consult records, fitness-to-work status. | In-flight PII scrubber and cryptographic role segregation gating medical narrative from HR. | Medical Officer signs binary "Fit / Unfit for Work" certificate. | Corporate HR receives strictly authorized fitness slip; 100% of clinical narrative remains encrypted. | Log in as Facility/HR Admin; verify attempt to read medical consultation narrative returns `403 FORBIDDEN`. | **Phase 4** (RBAC Middleware) |
| **11** | Prevent acute industrial trauma mortality during Golden Hour presentations. | Industrial Paramedic & Factory MO | Complex EHR documentation slows acute trauma resuscitation in factory/mining emergencies. | **Emergency Fast-Track & OT Workflow** (`DOC-16`, `RES-37`) | ABCD vitals, GCS/AVPU, toxic exposure tags, Golden Hour onset timestamp. | Instant Master Case provisioning ($< 200$ms); high-contrast 1-page Emergency Report synthesis. | Factory MO leads resuscitation; orders immediate specialty burn/trauma ambulance dispatch. | Acute trauma intake completed in $< 30$ seconds; rapid transit dispatch within 15 minutes. | Trigger emergency fast-track toggle; verify all routine history forms are bypassed and ABCD vitals displayed. | **Phase 5** (Emergency UI) & **Phase 6** (Fast-Track Engine) |
| **12** | Ensure zero-cost, fully offline deployment in remote rural clinics. | Facility Administrator & Health Worker | Cloud API costs ($500+/mo) and rural internet blackouts make commercial digital triage impossible. | **₹0 Native Open-Source Architecture** (`RES-18`, `DOC-21`) | Local SQLite database, local CPU/GPU runtime, local OpenStreetMap tiles. | Local Qwen SLM runtime, local faster-whisper, and local PaddleOCR running 100% on premise. | Staff operates platform with network cable disconnected; zero external API keys needed. | 100% operational uptime at ₹0 recurring software licensing cost across all rural outposts. | Pull network cable; execute complete voice intake, OCR, triage review, and referral printout with 0 errors. | **Phase 4** (Local Setup) & **Phase 7** (Offline Testing) |
| **13** | Track real-world patient recovery and close the longitudinal care loop. | Primary Clinician & Community Health Worker | Hospital systems terminate at discharge; doctors never learn if triage or referrals succeeded. | **Post-Disposition Outcome Loop** (`C10`, `DOC-17`) | 6 standardized recovery endpoints (`FULL_RECOVERY`, `STABILIZED`, `MORTALITY`, etc.). | Encrypts outcome into patient longitudinal timeline; computes model calibration Brier score. | Clinician or ASHA worker records verified recovery status during follow-up encounter. | Hospital tracks true clinical efficacy; algorithm calibration telemetry updated safely. | Submit verified outcome; verify case transitions from `ACTIVE` to `RESOLVED` and archives calibration record. | **Phase 6** (Outcome Engine) |
| **14** | Prevent unauthorized alteration of medical records or system audit logs. | System Administrator (`ROLE_SYS_ADMIN`) | Malicious tampering or post-incident alteration of triage records during medicolegal inquiries. | **Tamper-Evident Cryptographic Audit Ledger** (`B17`) | Actor ID, role, timestamp, old value, new value, override reason, SHA-256 hash. | Cryptographic hash chaining generating immutable append-only ledger entries for every transaction. | System Administrator inspects security log; cannot edit or delete entries. | 100% tamper-evident forensic auditability; full compliance with NMC and court standards. | Attempt SQL `UPDATE` or `DELETE` on audit ledger table; verify operation is rejected by database constraints. | **Phase 4** (Audit Ledger Schema) |

---

## 3. Implementation Phase Mapping Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   FUTURE IMPLEMENTATION PHASE ROADMAP                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: Data Schemas, RBAC Models & Core Technical Infrastructure         │
│           (Database schemas, Pydantic models, Local AI runtime, RBAC rules) │
│                                                                             │
│  PHASE 5: User Interface Engineering & High-Density Dashboards              │
│           (Doctor Workbench, Nurse Station, Intake Kiosk, Emergency Fast-UI)│
│                                                                             │
│  PHASE 6: Core Graph & Intelligence Engines Integration                     │
│           (CAREGRAPH Trajectory, FACILITYGRAPH Feasibility, SIGNALGRAPH)    │
│                                                                             │
│  PHASE 7: Comprehensive Multi-Environment Testing & System Validation       │
│           (Offline verification, E2E clinical workflows, Stress benchmarks) │
│                                                                             │
│  PHASE 8: Production Readiness, Demonstration Harness & Final Audit         │
│           (Synthetic showcase vignettes, Golden Hour demo, Final sign-off)  │
└─────────────────────────────────────────────────────────────────────────────┘
```
