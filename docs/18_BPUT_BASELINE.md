# CLINOVA AI — Official BPUT Baseline Capabilities Specification

> **Document ID:** `DOC-18`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Executive Summary & Mandatory Baseline Principle

The official BPUT (Biju Patnaik University of Technology) problem statement establishes the **mandatory operational baseline** for CLINOVA AI.

> **Foundational Principle:**
> All 18 baseline capabilities specified by BPUT are required and must be genuinely integrated into the working product.
>
> However, **do NOT present baseline capabilities as the main CLINOVA innovation**.
> The baseline is the foundation upon which CLINOVA builds **Continuous Care Intelligence**.

---

## 2. The 18 Mandatory BPUT Baseline Capabilities

Every requirement is assigned a unique identifier (`B01` through `B18`):

| ID | Baseline Capability | BPUT Problem Statement Specification | Implementation Contract in CLINOVA |
| :--- | :--- | :--- | :--- |
| **B01** | **Text Symptom Intake** | Structured and free-text narrative symptom collection from patient or health worker. | Multilingual input box with auto-sizing textarea, duration capture, and anatomical symptom tagger. |
| **B02** | **Voice Symptom Intake** | Speech audio capture for low-literacy or regional vernacular presentations. | Local browser audio recording converted via local Whisper / faster-whisper; native Odia/Hindi transcripts stored with audio waveform. |
| **B03** | **Medical Report Extraction** | Automated parsing of laboratory documents and clinical reports. | Discrete parameter extraction for hematology (CBC), biochemistry (electrolytes, creatinine), and rapid serology tests. |
| **B04** | **Optical Character Recognition (OCR)** | Computer vision extraction of printed and scanned medical records. | Local PaddleOCR / Tesseract pipeline extracting text, numbers, and dates from images and PDFs with bounding-box confidence scores. |
| **B05** | **Extraction & Structuring** | Transforming raw multimodal inputs into standardized clinical content. | Normalization of colloquial phrases into standardized clinical entities (SNOMED-CT / ICD-11 concepts) with units and dates. |
| **B06** | **Timeline Summarization** | Chronological ordering of symptom onset, previous medications, and interventions. | Interactive longitudinal timeline displaying clinical events with exact timestamps, source provenance, and verification flags. |
| **B07** | **Missing-Information Detection** | Algorithmic scanning for missing critical clinical qualifiers and vitals. | First-class clinical gap audit categorizing fields as `KNOWN`, `UNKNOWN`, `CONFLICTING`, or `UNRELIABLE`. |
| **B08** | **Follow-up Question Generation** | Generation of focused clarifying questions to close identified information gaps. | Dynamic Next-Best Information engine presenting 1–3 high-yield multiple-choice questions to reduce case uncertainty. |
| **B09** | **Language / Translation Support** | Vernacular language translation between English, Hindi, and regional languages. | Local open-source translation layer mapping regional dialects (Odia, Hindi) into standardized clinical English. |
| **B10** | **Risk-Category Support** | Transparent risk bands: Emergency / Red Flag, Urgent Priority, Routine Assessment. | Explainable risk stratification combining rule-based clinical red flags (MEWS, shock index) with objective physiological vitals. |
| **B11** | **Queue Prioritization** | Dynamic facility queue ordering based on clinical risk score and wait duration. | Multi-dimensional priority queue ranking patients based on risk band, physiological trajectory, and wait-time penalty. |
| **B12** | **Reviewer Dashboard** | One-screen clinical review workstation displaying synthesized notes, provenance, and override controls. | Comprehensive Doctor Workbench displaying patient overview, timeline, raw evidence, CAREGRAPH, and verification controls. |
| **B13** | **Referral Preparation** | Automated synthesis of structured inter-facility transfer documentation. | Capability-aware referral pack generated when facility feasibility fails, complete with destination matching via FACILITYGRAPH. |
| **B14** | **Consent Capture** | Explicit digital/verbal consent recorded prior to intake and data processing. | Mandatory consent checkbox and audio recording confirmation gate; blocks data persistence if unconfirmed. |
| **B15** | **Privacy & Anonymization** | Scrubbing of phone numbers, emails, government IDs, and direct identifiers. | In-flight regex and NLP redaction engine replacing identifiers with synthetic anonymous tokens (`PT-XXXXXX`). |
| **B16** | **Minimal Data Retention** | Automated retention policy with secure ephemeral disposal of transient files. | 24-hour ephemeral retention rule for raw audio and document image uploads in compliance with public health norms. |
| **B17** | **Auditability** | Tamper-evident logging of intake timestamps, model inferences, and clinician overrides. | Cryptographically linked immutable audit ledger tracking actor ID, action type, timestamp, old value, and new value. |
| **B18** | **Non-Diagnostic Advisory Behavior** | Strict HITL gate; system is explicitly non-diagnostic and cannot prescribe treatment. | Enforced architectural invariant: all AI outputs are labeled advisory, and case closing requires a licensed medical officer sign-off. |

---

## 3. Strict Compliance Guidelines

1. **Synthetic / Public Data Only:** The prototype processes synthetic patient records and simulated facility telemetry exclusively. No real private patient records are ever used or committed.
2. **Prominent Educational Prototype Disclaimer:** Every user interface and report contains the mandatory non-diagnostic disclaimer:
   > *"Educational Prototype & Triage Support System Only. Non-Diagnostic. All outputs are advisory and reviewer-facing."*
3. **Traceability to Master Case:** Every baseline feature must directly read from or write to the unified **Master Case** record.
