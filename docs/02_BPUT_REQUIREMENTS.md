# CLINOVA AI — BPUT Baseline Requirements Matrix

> **Document ID:** `DOC-02`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  
> **Compliance:** Mandatory Baseline Requirements Specification  

---

## 1. Baseline Overview

The BPUT problem statement forms the **mandatory operational baseline** for CLINOVA AI. Every capability in this matrix must be genuinely implemented in the software architecture, backed by API contracts, database persistence, and browser-verified user workflows.

UI-only mockups, stubbed buttons, or simulated animations without downstream logic are strictly prohibited.

---

## 2. Requirements Traceability Matrix (18 Baseline Capabilities)

| Req ID | Capability Name | Description | Acceptance Criteria | Downstream Effect in CLINOVA |
| :--- | :--- | :--- | :--- | :--- |
| **BPUT-01** | **Text Symptom Intake** | Structured and unstructured free-text symptom description input by patient or intake worker. | Accepts clinical narratives; parses into clinical entities with confidence scores. | Feeds CareGraph symptom nodes and triggers missing-info checks. |
| **BPUT-02** | **Voice Symptom Intake** | Audio recording and transcription of spoken symptom narratives in multiple regional accents/dialects. | Audio buffer converted to text via pluggable STT; graceful fallback to text if STT offline. | Stored with `VOICE_TRANSCRIBED` provenance; extracted symptoms update CareGraph. |
| **BPUT-03** | **Medical Report Upload/Extraction** | File ingestion for PDF/image lab results, discharge summaries, and referral slips. | Multi-format upload (PDF, PNG, JPEG); validation of file signatures; text parsing. | Report entities extracted into CareGraph lab and observation nodes. |
| **BPUT-04** | **Optical Character Recognition (OCR)** | Extraction of printed and handwritten medical text from uploaded clinical records. | Bounding box / structured key-value extraction for vitals, lab values, and doctor notes. | Extracted tokens tagged with `OCR_EXTRACTED` provenance and confidence score. |
| **BPUT-05** | **Timeline Summarization** | Chronological ordering and longitudinal synthesis of symptoms, onset times, and test dates. | Formats historical progression into a clear clinical timeline view with delta highlights. | Direct timeline visualization in CareGraph; informs risk trajectory calculations. |
| **BPUT-06** | **Missing-Information Detection** | Systematic identification of absent clinical parameters needed for safe triage (e.g., onset duration, allergy status). | Generates deterministic flags when protocol-critical data points are absent. | Directly populates Uncertainty metric; drives Orchestration `ASK` actions. |
| **BPUT-07** | **Follow-up Question Generation** | Dynamic generation of targeted, clinically relevant questions to resolve identified data gaps. | Context-aware prompts offered to intake staff to elicit high-value missing details. | Staff answers immediately resolve missing data in CareGraph and lower uncertainty. |
| **BPUT-08** | **Translation / Multilingual Support** | Clinical narrative and symptom intake support across English, Hindi, and regional languages. | Bidirectional translation of intake prompts and responses; maintains semantic clinical accuracy. | Enables accessible patient interaction while presenting standardized clinical terms to doctors. |
| **BPUT-09** | **Risk-Category Support** | Stratification of case acuity into standardized clinical tiers (Routine, Moderate, Urgent, Critical). | Deterministic physiological rule evaluation + advisory clinical score; never autonomous diagnosis. | Establishes baseline case priority in clinical queue and triggers rapid alerts. |
| **BPUT-10** | **Queue Prioritization** | Dynamic sorting of department/facility patient waitlists based on risk tier and waiting time. | High-risk/deteriorating cases automatically elevated to top of queue; SLA timers displayed. | Ensures medical officers review the sickest patients first across all departments. |
| **BPUT-11** | **Referral Preparation** | Structured clinical handover packet generation containing patient summary, trajectory, and required care. | Auto-populates standardized SBAR (Situation, Background, Assessment, Recommendation) referral letter. | Bundles CareGraph state and routes packet via FacilityGraph to capable receiving center. |
| **BPUT-12** | **Reviewer Dashboard / Workflow** | Dedicated clinical workstation for verified medical officers to inspect, review, and act on cases. | High-density, calm UI displaying patient state, evidence provenance, uncertainty, and actions. | Serves as the primary operational gateway for human-in-the-loop decision-making. |
| **BPUT-13** | **Informed Patient Consent** | Explicit consent capture before collecting personal, medical, or photographic information. | Multi-language consent modal with clear disclosures on data usage, privacy, and non-diagnostic nature. | Blocks intake workflow until valid consent record with timestamp is recorded. |
| **BPUT-14** | **Anonymization / PII Minimization** | Automatic scrubbing/redaction of direct identifiers (names, phone numbers, Aadhaar/Govt IDs). | Replaces patient identifiers with synthetic pseudonyms (`SYN-PT-XXXX`) before persistence. | Guarantees compliance with healthcare privacy laws; prevents PII exposure in downstream logs. |
| **BPUT-15** | **Minimal Data Retention** | Automated lifecycle policies archiving or purging non-essential temporary intake data after active care. | Configurable TTL (e.g., 24-hour dev retention, automated archiving for production audit). | Mitigates breach liability and ensures lean operational database footprint. |
| **BPUT-16** | **Medicolegal Auditability** | Immutable logging of every system transaction, data extraction, AI suggestion, and clinician action. | Cryptographically timestamped audit log capturing Actor, Action, Target, and Decision Rationale. | Enables complete post-hoc medicolegal review and quality assurance auditing. |
| **BPUT-17** | **Qualified Human Handoff** | Explicit mechanism ensuring patient care is actively accepted by a designated clinician or facility. | Requisite clinician digital sign-off before case closure or dispatch; escalation timeout alerts. | Eliminates "dropped baton" handoff failures between triage and active clinical care. |
| **BPUT-18** | **Non-Diagnostic Advisory Mandate** | System-wide constraint preventing autonomous diagnostic claims or prescription orders. | Header enforcement (`X-Clinical-Safety`), prominent UI banners, and refusal to output final diagnostic labels. | Protects patient safety and maintains adherence to medical device regulatory frameworks. |

---

## 3. Graceful Degradation Standards for Baseline Capabilities

In public health environments, network connectivity and cloud APIs are unreliable. Every baseline capability must implement a deterministic local fallback:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GRACEFUL DEGRADATION MATRIX                            │
├─────────────────────────┬─────────────────────────┬─────────────────────────┤
│ Baseline Capability     │ Primary Mode (Online)   │ Fallback Mode (Offline) │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ Voice Symptom Intake    │ Cloud Neural STT        │ Direct Text Entry UI    │
│ OCR Extraction          │ Cloud Multi-modal OCR   │ Manual Parameter Entry  │
│ Follow-up Questions     │ Dynamic Contextual LLM  │ Deterministic Rule Tree │
│ Multilingual Intake     │ Neural Cloud Translate  │ Pre-translated Lexicon  │
│ Risk Stratification     │ Hybrid Rule + NLP       │ Deterministic MEWS/NEWS │
│ Facility Telemetry      │ Real-Time Network Sync  │ Cached Local Baselines  │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

## 4. Acceptance Gate

A baseline capability is considered **Done** only when:
1. Operational API endpoint returns structured responses.
2. Clinical frontend component renders and interacts smoothly with zero console errors.
3. Edge cases (empty payload, corrupt file, invalid language code) return safe error states.
4. Downstream state in CareGraph or clinical queue reflects the input accurately.
