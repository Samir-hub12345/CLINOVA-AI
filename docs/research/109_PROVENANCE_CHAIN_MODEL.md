# CLINOVA AI — End-to-End Provenance Chain & Raw Source Model

> **Document ID:** `RES-109`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Principle of Complete Lineage

A clinical decision is only as sound as the chain of evidence supporting it. When an emergency physician decides to administer IV thrombolysis, perform an emergency laparotomy, or transfer a patient 60 kilometers to a tertiary facility, they must not be presented with a disconnected number or an ungrounded text summary.

Every fact in CLINOVA AI maintains an unbroken, tamper-evident **Provenance Chain** spanning nine canonical evolutionary stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   NINE-STAGE CANONICAL PROVENANCE CHAIN                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. RAW SOURCE      ──> Acoustic wave, optical pixel, physical sensor touch │
│  2. INGESTION       ──> Capture, hardware buffering, local disk persist     │
│  3. TRANSFORMATION  ──> Audio decode, denoising, image unskew/contrast      │
│  4. EXTRACTION      ──> Speech-to-text tokenization, OCR character bounding │
│  5. NORMALIZATION   ──> Concept mapping (SNOMED/LOINC), unit normalization  │
│  6. VERIFICATION    ──> Human staff/clinician review and attestation signoff│
│  7. CLINICAL USE    ──> Integration into NEWS2, triage queue, CAREGRAPH     │
│  8. DECISION        ──> Physician disposition, order, prescription, referral│
│  9. OUTCOME         ──> Real-world physiological response, recovery, audit  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage-by-Stage Lineage Metadata Retention

For every state transition along the provenance pipeline, specific immutable metadata attributes are captured and chained into the audit ledger:

| Pipeline Transition | Input Artefact | Output Artefact | Invariant Metadata Retained |
| :--- | :--- | :--- | :--- |
| **1 $\to$ 2: Ingestion** | Physical event / media | Buffered raw file | `source_id`, `device_id`, `capture_time`, `ingestion_time`, `sha256_hash`, `mime_type`, `file_size_bytes` |
| **2 $\to$ 3: Transformation** | Raw media file | Preprocessed media | `pipeline_version`, `transformation_type` (denoise/rotate), `transform_params`, `output_hash`, `reversibility` |
| **3 $\to$ 4: Extraction** | Preprocessed media | Unstructured text/boxes | `model_name`, `model_version`, `bounding_box_coords`, `word_timestamps`, `extraction_confidence`, `raw_text` |
| **4 $\to$ 5: Normalization** | Raw text / numbers | Structured concept | `canonical_concept_code` (LOINC/SNOMED), `normalized_value`, `standard_unit`, `conversion_factor_applied` |
| **5 $\to$ 6: Verification** | Unverified entity | Verified evidence | `verifier_actor_id`, `verifier_role`, `verification_status`, `attestation_timestamp`, `modification_delta` |
| **6 $\to$ 7: Clinical Use** | Verified evidence | Dynamic clinical score | `algorithm_version`, `formula_id`, `snapshot_input_ids`, `score_output`, `triage_priority_assigned` |
| **7 $\to$ 8: Decision** | Clinical synthesis | Medical order / action | `clinician_actor_id`, `nmr_number`, `decision_timestamp`, `order_type`, `clinical_rationale`, `override_flag` |
| **8 $\to$ 9: Outcome** | Action executed | Clinical resolution | `outcome_timestamp`, `outcome_category` (Resolved/Referred), `discharge_summary_id`, `audit_closed_hash` |

---

## 3. Concrete Worked Exemplars

### Exemplar A: Vernacular Voice $\to$ Transcript $\to$ Symptom $\to$ Review
```
[1. RAW SOURCE]     Patient speaks Odia: "ମୋ ଛାତିରେ ଭୀଷଣ କଷ୍ଟ ହେଉଛି ୩ ଘଣ୍ଟା ହେଲା" (Mo chhati-re bhishana kashta heuchhi 3 ghanta hela)
         │
[2. INGESTION]      Android Tablet Mic -> /var/data/clinova/audio/aud_89f1.wav (SHA-256: e4b2...19a0, 48kHz, mono)
         │
[3. TRANSFORM]      Denoise filter applied (SNR improved from 12 dB to 28 dB)
         │
[4. EXTRACTION]     multilingual-whisper-v3-edge -> Transcript: "ମୋ ଛାତିରେ ଭୀଷଣ କଷ୍ଟ ହେଉଛି ୩ ଘଣ୍ଟା ହେଲା"
                    Time offsets: [00:01.200 - 00:04.500], Word confidence: 0.942
         │
[5. NORMALIZATION]  LLM Extraction -> Concept: SNOMED CT 29857009 (Chest Pain)
                    Severity: SEVERE (pain score 8/10), Duration: 180 minutes, Trajectory: ACUTE_WORSENING
         │
[6. VERIFICATION]   Triage Nurse Anita, RN listens to 3-second audio crop -> Clicks "Confirm Symptom" (STATE_STAFF_VERIFIED)
         │
[7. CLINICAL USE]   NEWS2 / Triage Engine correlates Chest Pain + Diaphoresis -> Triggers "Suspected Acute Coronary Syndrome"
                    Queue Priority elevated to IMMEDIATE_RED
         │
[8. DECISION]       Dr. P. K. Patnaik, MD orders Emergency ECG + Aspirin 300mg + Clopidogrel 300mg stat
         │
[9. OUTCOME]        ECG confirms STEMI -> Patient transferred via cardiac ambulance to SCB Medical College Cuttack (Pathway E)
```

---

### Exemplar B: Paper Document $\to$ OCR Region $\to$ Extracted BP $\to$ Verification
```
[1. RAW SOURCE]     Paper discharge slip from rural clinic with handwritten and printed text
         │
[2. INGESTION]      Smartphone Camera Scan -> /var/data/clinova/docs/doc_a17c.jpg (SHA-256: 7f3d...98b1, 300 DPI)
         │
[3. TRANSFORM]      Auto-perspective correction, deskew (+4.2 degrees), adaptive thresholding
         │
[4. EXTRACTION]     PaddleOCR Engine -> Bounding Box [ymin: 420, xmin: 110, ymax: 455, xmax: 310]
                    Raw text: "B.P: 160/100 mmHg", Box confidence: 0.884
         │
[5. NORMALIZATION]  Extracted Entities: LOINC 8480-6 (Systolic BP = 160 mmHg), LOINC 8462-4 (Diastolic BP = 100 mmHg)
                    Epistemic status: INFERRED (Confidence: 0.884)
         │
[6. VERIFICATION]   Doctor Workbench displays 160/100 alongside cropped JPEG of bounding box.
                    Clinician clicks "Approve Extraction" -> Transitions to CLINICIAN_VERIFIED
         │
[7. CLINICAL USE]   Hypertension Grade 2 added to longitudinal cardiovascular risk profile
         │
[8. DECISION]       Clinician prescribes Amlodipine 5mg OD, orders Serum Creatinine and Electrolytes
         │
[9. OUTCOME]        Follow-up at 14 days: BP controlled at 128/82 mmHg; adherence confirmed
```

---

### Exemplar C: Bedside Vital Monitor $\to$ Observation $\to$ Risk Score $\to$ Disposition
```
[1. RAW SOURCE]     Pulse Oximeter finger sensor emits infrared absorption pulses on Patient Arm
         │
[2. INGESTION]      USB/Bluetooth Serial Port reads packet -> SpO2: 84%, Pulse: 118 bpm, PI: 1.2%
         │
[3. TRANSFORM]      Checksum validation; CRC-16 valid; raw packet parsed
         │
[4. EXTRACTION]     Instantaneous telemetry reading at 14:22:10 UTC
         │
[5. NORMALIZATION]  LOINC 59408-5 (Oxygen Saturation = 84%), LOINC 8867-4 (Heart Rate = 118 bpm)
                    Status: KNOWN, Source: STAFF_ENTERED (Auto-device capture)
         │
[6. VERIFICATION]   Triage Nurse performs visual check of plethysmograph waveform -> Confirms reading in 15 seconds
         │
[7. CLINICAL USE]   Deterministic System Derivation: NEWS2 Score jumps from 3 to 9 (High Clinical Risk Tier)
                    System generates: URGENT_ESCALATION advisory
         │
[8. DECISION]       Clinician initiates high-flow oxygen via non-rebreather mask at 15 L/min; orders ABG and portable CXR
         │
[9. OUTCOME]        Repeat SpO2 improves to 94% at 14:35:00; patient stabilized, avoided invasive mechanical ventilation
```

---

## 4. Canonical Raw Source Relational Specification

To uphold system performance and SQLite WAL operational constraints, **binary multimedia files are NEVER stored directly within relational table rows as BLOBs**. Relational records store immutable URI pointers, cryptographic hashes, and spatial/acoustic offsets.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAW SOURCE POINTER MODEL                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  storage_reference  ──> "file:///var/data/clinova/media/aud_89f1.wav"       │
│  checksum_sha256    ──> "e4b2a3c7f9910d88b47219ac09214b7e88..."             │
│  mime_type          ──> "audio/wav" (or "image/jpeg", "application/pdf")    │
│  bounding_offset    ──> "[ymin, xmin, ymax, xmax]" OR "[start_ms, end_ms]"  │
│  integrity_status   ──> VERIFIED_ON_DISK (Hash matches database at runtime) │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Relational Table Design: `raw_evidence_sources`

```sql
CREATE TABLE raw_evidence_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN (
        'AUDIO_RECORDING', 'DOCUMENT_IMAGE', 'SCANNED_PDF', 
        'OCR_REGION_CROP', 'TRANSCRIPT_SEGMENT', 'MANUAL_ENTRY_FORM', 
        'EXTERNAL_FHIR_BUNDLE', 'VITAL_MONITOR_TELEMETRY', 'CLINICIAN_NOTE'
    )),
    capture_time TIMESTAMPTZ NOT NULL,
    ingestion_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_id UUID NOT NULL REFERENCES users(id),
    device_id VARCHAR(64) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    storage_reference VARCHAR(512) NOT NULL,
    mime_type VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
    source_quality_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 
        CHECK (source_quality_score >= 0.0 AND source_quality_score <= 1.0),
    retention_class VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (retention_class IN (
        'ACTIVE', 'RETAINED', 'PURGED', 'HASH_ONLY', 'ARCHIVED'
    )),
    verification_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'STAFF_VERIFIED', 'CLINICIAN_APPROVED', 'REJECTED'
    ))
);

CREATE INDEX ix_raw_src_case ON raw_evidence_sources(case_id);
CREATE INDEX ix_raw_src_hash ON raw_evidence_sources(checksum_sha256);
CREATE INDEX ix_raw_src_retention ON raw_evidence_sources(retention_class);
```

---

## 5. Invariant Lineage Linkage

Every row in `evidence_records` points back to its immediate parent in `raw_evidence_sources`:
$$\forall e \in \text{EvidenceRecords}, \quad e.\text{source\_raw\_id} \in \text{raw\_evidence\_sources(id)}$$

If an evidence record was derived from a secondary extraction (e.g., an LLM symptom extracted from a transcript, which was transcribed from an audio recording), the lineage is recursively traceable via `transformation_events`:
$$\text{EvidenceRecord} \xrightarrow{\text{derived\_from}} \text{TranscriptSegment} \xrightarrow{\text{extracted\_from}} \text{AudioRecording}$$

This ensures zero ambiguity: at any point in the patient’s care, an auditor, judge, or consulting specialist can click on any clinical parameter and immediately inspect the exact millisecond of audio or pixel bounding box from which it originated.
