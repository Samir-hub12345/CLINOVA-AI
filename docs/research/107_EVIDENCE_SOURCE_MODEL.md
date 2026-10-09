# CLINOVA AI — Canonical Evidence Source Model

> **Document ID:** `RES-107`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Core Source Principle: Source Class $\neq$ Clinical Truth

In legacy electronic medical record systems and naive AI health applications, a dangerous epistemic fallacy is frequently committed: **conflating the data source modality with objective truth**. 
- A vital sign entered by a triage nurse is presumed infallible, ignoring cuff misplacement, sensor decalibration, or transcription typos.
- A patient’s self-reported narrative is dismissed as uncorroborated noise, ignoring that subjective perception (e.g., severe tearing chest pain) is the primary diagnostic indicator of life-threatening aortic dissection.
- An optical character recognition (OCR) parsing of a government lab report is treated as verified fact, ignoring smudged decimal places or inverted reference ranges.
- An AI-inferred clinical entity is treated as authoritative, ignoring potential hallucinations or language-model confabulations.

**The Foundational Law of Evidence in CLINOVA AI:**
$$\text{Source Class } S \neq \text{Objective Truth } \Omega$$
$$\forall e \in \text{EvidenceRecords}, \quad \text{Reliability}(e) = f(\text{SourceType}, \text{Quality}, \text{Corroboration}, \text{HumanVerification}, \text{Freshness})$$

Every clinical datum captured in CLINOVA must be tagged with its immutable **Source Class**, establishing its legal origin, epistemic weight, downstream eligibility, and mandatory verification hurdles without prejudging its absolute accuracy.

---

## 2. The Eight Canonical Evidence Source Classes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EIGHT CANONICAL EVIDENCE SOURCES                        │
├──────────────────────┬────────────────────────┬─────────────────────────────┤
│ Source Class Code    │ Origin Modality        │ Primary Actor / Engine      │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ PATIENT_REPORTED     │ Subjective Narrative   │ Patient / Informal Caregiver│
│ VOICE_TRANSCRIBED    │ Acoustic Speech        │ Whisper Edge SLM Engine     │
│ OCR_EXTRACTED        │ Optical Scan / Crop    │ PaddleOCR / Tesseract SLM   │
│ CLINICIAN_VERIFIED   │ Exam / Order / Signoff │ Registered Medical Pract.   │
│ STAFF_ENTERED        │ Bedside Measurement    │ Staff Nurse / ANM / ASHA    │
│ AI_INFERRED          │ Algorithmic Deduction  │ Clinical LLM / Classifier   │
│ SYSTEM_DERIVED       │ Mathematical Score     │ Deterministic Rule Engine   │
│ EXTERNAL_RECORD      │ Inter-Facility Record  │ ABDM Gateway / Health Locker│
└──────────────────────┴────────────────────────┴─────────────────────────────┘
```

---

## 3. Exhaustive Source Class Specifications

### 3.1 `PATIENT_REPORTED`
- **Formal Definition:** Any symptom, timeline description, past medical history, medication list, or functional status communicated directly by the patient or their immediate informal caregiver via direct app entry, vernacular kiosk form, or conversational elicitation.
- **Allowed Clinical Use:** Primary source for presenting complaint, symptom onset timing, pain characterization, functional limitations, allergies, and treatment adherence history. Eligible for preliminary triage symptom mapping.
- **Reliability Assumptions:** Highly authoritative regarding subjective internal experiences (pain intensity, nausea, dyspnea sensation); variable reliability regarding numerical medical history (exact medication dosage, laboratory values, past surgical dates). Subject to recall bias, health literacy limitations, and emotional distress.
- **System Visibility:** Prominently surfaced on the Nurse Intake screen and Doctor Workbench with a distinctive "Patient Reported" tag.
- **Verification Requirements:** Mandatory nursing or clinician review before inclusion in formal diagnostic impression or medication reconciliation.
- **Downstream Eligibility:** Eligible to trigger red-flag triage alerts and calculate preliminary symptom trajectories. Ineligible to authorize invasive procedures, write prescriptions, or sign off hospital discharges.
- **Audit Requirements:** Full timestamp, respondent relationship (Self vs Caregiver), input interface session ID, language code, and raw unedited text string.

---

### 3.2 `VOICE_TRANSCRIBED`
- **Formal Definition:** Raw vernacular speech captured via mobile microphone or consultation room recorder, converted into textual transcripts by edge speech-to-text models (e.g., multilingual Whisper engine optimized for Odia, Hindi, and Indian English).
- **Allowed Clinical Use:** Audio documentation acceleration, verbatim dialogue preservation, ambient intake capture, and source grounding for extracted clinical entities.
- **Reliability Assumptions:** Subject to acoustic degradation, environmental ambient noise (PHC waiting rooms), overlapping speakers, phoneme confusions ("hyper" vs "hypo"), and dialectical code-switching. Acoustic transcript is NOT equivalent to verified medical history.
- **System Visibility:** Visualized in the transcription panel with word-level confidence shading. Word timestamps link directly to underlying raw audio snippets.
- **Verification Requirements:** Requires human staff or clinician confirmation during `STATE_EXTRACTION_REVIEW` ($S04$).
- **Downstream Eligibility:** Ineligible for direct physiological risk scoring until clinical entities are extracted, normalized, and verified.
- **Audit Requirements:** Complete recording session ID, microphone hardware device ID, audio duration, SHA-256 audio file hash, transcription engine version, word-level confidence scores, and timecode offsets.

---

### 3.3 `OCR_EXTRACTED`
- **Formal Definition:** Structured text, numeric lab results, medication names, or physician signatures extracted from physical documents (paper referral slips, OPD cards, laboratory printouts) via optical character recognition and layout analysis engines.
- **Allowed Clinical Use:** Rapid ingestion of historical clinical documents, past lab records, discharge summaries, and referral letters.
- **Reliability Assumptions:** Vulnerable to skewed scans, crumpled paper, low-light photography, smudged printer ink, font ambiguities (confusing 1, l, and I, or 0 and O), and handwritten doctor notes. Baseline reliability is unverified until visually checked.
- **System Visibility:** Surfaces alongside a side-by-side cropped preview of the physical document image highlighting the exact bounding box $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$.
- **Verification Requirements:** Acuity-proportional review. Tier 1 lab values (e.g. Potassium, Troponin, Hemoglobin) and drug dosages require mandatory human verification before ingestion into active clinical calculations.
- **Downstream Eligibility:** Extracted values are tagged `UNVERIFIED` or `INFERRED`. Eligible to trigger diagnostic warnings; ineligible to alter patient baseline without verification.
- **Audit Requirements:** Source document ID, page number, image resolution (DPI), bounding box coordinates, OCR engine version, text extraction confidence score, and raw unparsed OCR string.

---

### 3.4 `CLINICIAN_VERIFIED`
- **Formal Definition:** Clinical findings, physical examination signs, confirmed diagnoses, orders, or validated inferences explicitly approved or documented by a Registered Medical Practitioner (RMP) holding a valid National Medical Register (NMR) credential.
- **Allowed Clinical Use:** Gold-standard medical fact within the case episode. Unlocks definitive care pathways, formal diagnostic coding (ICD-11), prescription issuance, ward admission, surgical booking, and discharge sign-off under NMC Regulations 2023.
- **Reliability Assumptions:** Highest statutory and epistemic authority in the system. Assumed legally valid and clinically sound, but still subject to retrospective correction via non-destructive amendment events if clinical conditions evolve.
- **System Visibility:** Displayed with an authoritative green badge ("Clinician Confirmed"), displaying the RMP's name, registration number, and timestamp.
- **Verification Requirements:** Self-verifying by definition.
- **Downstream Eligibility:** Unrestricted eligibility across all diagnostic, prognostic, and therapeutic orchestration pipelines.
- **Audit Requirements:** Clinician User UUID, NMR registration number, digital signature/session authentication token, exact sign-off timestamp, and immutable snapshot of reviewed data.

---

### 3.5 `STAFF_ENTERED`
- **Formal Definition:** Objective physiological measurements, vital signs, point-of-care rapid test results, or nursing observations physically captured and entered by licensed healthcare staff (Staff Nurses, ANMs, ASHAs, Paramedics).
- **Allowed Clinical Use:** Physiological risk calculation (NEWS2, Shock Index, Pediatric Triage Score), triage queue prioritization, and resuscitation protocol activation.
- **Reliability Assumptions:** High reliability for calibrated physical measurements (blood pressure, pulse oximetry, respiratory rate, temperature, blood glucose). Minor risk of manual transcription typos or sensor motion artifacts.
- **System Visibility:** Labeled with staff member's name, professional role, and acquisition timestamp.
- **Verification Requirements:** Considered operationally valid for initial triage and monitoring (`STAFF_VERIFIED`). High-risk abnormalities (e.g. SBP < 80 mmHg or SpO2 < 90%) trigger immediate clinical notification and clinician review.
- **Downstream Eligibility:** Fully eligible for physiological risk and triage priority calculations. Ineligible for autonomous final discharge or invasive procedural orders.
- **Audit Requirements:** Staff User UUID, role designation, facility ID, measurement device ID (if Bluetooth/serial integrated), and capture timestamp.

---

### 3.6 `AI_INFERRED`
- **Formal Definition:** Synthesized entities, differential diagnostic hypotheses, clinical risk projections, red-flag indicators, or missing data alerts generated by artificial intelligence models (multilingual SLMs, transformer encoders, or predictive classifiers).
- **Allowed Clinical Use:** Strictly advisory clinical decision support, triage assistance, missing-information identification, and care pathway recommendations.
- **Reliability Assumptions:** Probabilistic and non-deterministic. Vulnerable to out-of-distribution drift, nuanced medical edge cases, atypical disease presentations, and language hallucinations. **AI inferences have zero autonomous clinical authority.**
- **System Visibility:** Visually demarcated with a mandatory amber watermark and clinical disclaimer: *"AI-Generated Advisory — Requires Clinical Verification"*.
- **Verification Requirements:** Mandatory human review. Under no circumstances can an AI inference transition to `VERIFIED` without explicit clinician or staff confirmation.
- **Downstream Eligibility:** Prohibited from autonomously creating legal diagnoses, writing medical prescriptions, executing patient admissions, or initiating surgical procedures (NMC Regulation 27 compliance).
- **Audit Requirements:** Model architecture name, provider/runtime version, prompt template version hash, input token count, output confidence distribution, inference latency, and exact generation timestamp.

---

### 3.7 `SYSTEM_DERIVED`
- **Formal Definition:** Deterministic, non-probabilistic clinical and operational calculations computed by hardcoded mathematical algorithms, guideline-based scoring formulas, or graph aggregators (e.g., Shock Index, NEWS2 composite score, Information Sufficiency Score $S$, Queue Priority Index $P(t)$, FACILITYGRAPH feasibility).
- **Allowed Clinical Use:** Standardized physiological acuity stratification, automated queue sorting, and missing-data gating.
- **Reliability Assumptions:** Computationally deterministic ($100\%$ reproducible given the same inputs). Reliability is entirely dependent on the quality and freshness of the underlying input evidence records.
- **System Visibility:** Displayed with an expandable calculation formula breakdown showing raw input values, scoring tables, and component points.
- **Verification Requirements:** No independent clinical review required for the arithmetic computation itself; however, changes to underlying input vitals automatically trigger real-time re-derivation.
- **Downstream Eligibility:** Directly drives automated triage queue re-ranking and nurse worklist gating.
- **Audit Requirements:** Rule engine version, mathematical formula identifier, timestamp, and array of foreign keys pointing to all source input `evidence_records`.

---

### 3.8 `EXTERNAL_RECORD`
- **Formal Definition:** Historical health records, previous encounter summaries, immunization logs, or diagnostic reports retrieved from external healthcare facilities via the Ayushman Bharat Digital Mission (ABDM) Unified Health Interface (UHI), Health Information Exchange (HIE), or scanned past hospital cards.
- **Allowed Clinical Use:** Baseline medical history comparison, chronic disease longitudinal tracking, previous allergy checks, and retrospective clinical correlation.
- **Reliability Assumptions:** Variable freshness and authenticity. Assumed to represent a valid historical record at the time of creation, but may be clinically stale, incomplete, or recorded under unverified patient identity.
- **System Visibility:** Displayed in a dedicated "External / Historical Records" timeline tab with originating facility name and encounter date.
- **Verification Requirements:** Must be reconciled by attending clinical staff during intake or review before being treated as current baseline physiology.
- **Downstream Eligibility:** Ineligible to represent current acute vital signs. Highly eligible to populate chronic disease and allergy alerts.
- **Audit Requirements:** ABDM Consent Artefact ID, originating HIP (Health Information Provider) ID, FHIR Bundle ID, digital signature validation status, and ingestion timestamp.

---

## 4. Source Class Comparative Governance Matrix

| Source Class | Origin Actor / System | Epistemic Weight | Advisory vs Decisional | Direct Risk Scoring | Final Disposition Rights |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PATIENT_REPORTED` | Patient / Caregiver | Subjective ($w=0.60$) | Advisory | Conditional (Symptoms) | Prohibited |
| `VOICE_TRANSCRIBED` | Edge Whisper Engine | Perceptual ($w=0.70$) | Raw Capture | Prohibited (Pre-extract) | Prohibited |
| `OCR_EXTRACTED` | PaddleOCR / Tesseract | Perceptual ($w=0.75$) | Raw Capture | Prohibited (Pre-verify) | Prohibited |
| `CLINICIAN_VERIFIED` | Registered Medical Pract. | Gold-Standard ($w=1.00$)| Decisional | Fully Eligible | Exclusive Authority |
| `STAFF_ENTERED` | Staff Nurse / Paramedic | Objective ($w=0.95$) | Operational | Fully Eligible | Emergency Escalation Only |
| `AI_INFERRED` | LLM / Classifier | Statistical ($w=0.50$) | Strictly Advisory | Prohibited Autonomously | Prohibited |
| `SYSTEM_DERIVED` | Deterministic Algorithm | Deterministic ($w=1.00$)| Procedural | Fully Eligible (Formulas)| Ineligible |
| `EXTERNAL_RECORD` | ABDM / Prior Facility | Historical ($w=0.80$) | Contextual | Historical Baseline | Prohibited for Acute Care |

---

## 5. Relational Schema Representation

To enforce source constraints at the database layer without altering Phase 6 relational models, the `evidence_records` schema enforces source validation via standard PostgreSQL and SQLite check constraints:

```sql
-- Formal source constraint definition
ALTER TABLE evidence_records
ADD CONSTRAINT chk_ev_source_validity
CHECK (
    source_type IN (
        'PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED',
        'CLINICIAN_VERIFIED', 'STAFF_ENTERED', 'AI_INFERRED',
        'SYSTEM_DERIVED', 'EXTERNAL_RECORD'
    )
);

-- Invariant: AI_INFERRED records can NEVER have verification_status = 'CONFIRMED'
-- without a valid verified_by_actor_id belonging to a registered human user
ALTER TABLE evidence_records
ADD CONSTRAINT chk_ai_never_self_verified
CHECK (
    NOT (source_type = 'AI_INFERRED' AND verification_status = 'CONFIRMED' AND verified_by_actor_id IS NULL)
);
```

This ensures that the source class is preserved as an unalterable attribute of the data record, guaranteeing absolute downstream transparency.
