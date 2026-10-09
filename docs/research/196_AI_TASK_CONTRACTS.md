# CLINOVA AI — Task Contracts & Data Schemas

> **Document ID:** `RES-196`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Informatics & AI Contract Engineering Group  

---

## 1. Universal Base Response Contract

All machine-consumed responses returned by the local AI runtime inherit from `BaseAIResponse`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BaseAIResponse",
  "type": "object",
  "required": ["status", "model", "model_version", "generated_at", "epistemic_state", "validation_state", "payload"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["SUCCESS", "SUCCESS_CACHED", "REJECTED", "FALLBACK"]
    },
    "model": { "type": "string" },
    "model_version": { "type": "string" },
    "runtime": { "type": "string" },
    "prompt_id": { "type": "string" },
    "prompt_version": { "type": "string" },
    "generated_at": { "type": "string", "format": "date-time" },
    "epistemic_state": {
      "type": "string",
      "const": "AI_INFERRED"
    },
    "confidence": {
      "type": ["number", "null"],
      "minimum": 0.0,
      "maximum": 1.0
    },
    "validation_state": {
      "type": "string",
      "enum": ["VALID", "REJECTED_SCHEMA", "REJECTED_FORBIDDEN_ACTION", "REJECTED_UNGROUNDED", "REJECTED_OUT_OF_BOUNDS", "REJECTED_TIMEOUT", "REJECTED_OOM", "REJECTED_MALFORMED"]
    },
    "source_references": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["evidence_id"],
        "properties": {
          "evidence_id": { "type": "string" },
          "source_type": { "type": "string" }
        }
      }
    },
    "warnings": {
      "type": "array",
      "items": { "type": "string" }
    },
    "payload": { "type": "object" }
  }
}
```

---

## 2. Seven Specialized Task Payload Contracts

### 2.1 Task 1: Clinical Narrative Extraction (`EXTRACTION_RESULT`)
- **Purpose:** Parse symptoms, reported durations, anatomical sites, and explicit vital mentions from clinical text.
- **Payload Schema:**
  ```json
  {
    "symptoms": [
      {
        "name": "Chest Pain",
        "duration": "2 hours",
        "severity": "SEVERE",
        "body_site": "Retrosternal",
        "source_evidence_id": "ev-001"
      }
    ],
    "vital_mentions": [
      {
        "parameter": "HR",
        "value": 110.0,
        "unit": "bpm",
        "source_evidence_id": "ev-001"
      }
    ],
    "reported_allergies": ["Penicillin"],
    "reported_medications": ["Aspirin 75mg"],
    "identified_gaps": ["Cardiac enzyme baseline missing"]
  }
  ```
- **Validation Rules:**
  - Every symptom and vital mention must reference an existing `source_evidence_id`.
  - All vital values must satisfy physiological range boundaries ($20 \le \text{HR} \le 300$).

### 2.2 Task 2: Clinical Summarization (`SUMMARY_RESULT`)
- **Purpose:** Synthesize chronological history while explicitly articulating missing clinical facts.
- **Payload Schema:**
  ```json
  {
    "chief_complaint": "Acute substernal chest discomfort radiating to left arm",
    "brief_chronology": "Patient experienced sudden onset of severe pressure-like pain 2 hours prior to arrival.",
    "pertinent_positives": ["Diaphoresis", "Tachycardia"],
    "pertinent_negatives": ["No fever", "No cough"],
    "uncertainty_statement": "Prior cardiac baseline ECG and troponin markers are currently unrecorded."
  }
  ```
- **Validation Rules:**
  - `uncertainty_statement` must be non-empty.
  - Zero autonomous diagnoses or hospital dispositions.

### 2.3 Task 3: Value-of-Information Inquiry (`QUESTION_RESULT`)
- **Purpose:** Propose 1–3 non-alarming clarification questions to close epistemic ambiguity.
- **Payload Schema:**
  ```json
  {
    "candidate_questions": [
      {
        "question_text": "Did the chest pain start suddenly or build up gradually?",
        "language": "en",
        "information_gap": "Onset trajectory",
        "rationale": "Helps distinguish acute ischemic event from musculoskeletal etiology",
        "priority": 1
      }
    ],
    "total_gaps_identified": 1
  }
  ```
- **Validation Rules:**
  - Question text must not mention frightening diagnoses (e.g., "Are you having a fatal heart attack?").

### 2.4 Task 4: Vernacular Translation (`TRANSLATION_RESULT`)
- **Purpose:** Translate vernacular statements (Odia, Hindi) while preserving regional somatic idioms verbatim.
- **Payload Schema:**
  ```json
  {
    "source_text": "chhati re gapa gapa laguchi",
    "source_language": "od",
    "target_language": "en",
    "translated_text": "Patient describes severe chest tightness and heaviness.",
    "preserved_colloquialisms": {
      "gapa gapa": "colloquial Odia idiom for suffocating retrosternal constriction"
    }
  }
  ```
- **Validation Rules:**
  - `source_text` must match original input string exactly (zero data loss).

### 2.5 Task 5: Terminology Normalization (`NORMALIZATION_RESULT`)
- **Purpose:** Map colloquial complaints to standard clinical terminologies (SNOMED-CT, LOINC).
- **Payload Schema:**
  ```json
  {
    "entities": [
      {
        "colloquial_term": "chest tightness",
        "standard_concept": "Chest tightness (finding)",
        "coding_system": "SNOMED-CT",
        "concept_code": "29857009",
        "mapping_confidence": 0.92
      }
    ]
  }
  ```

### 2.6 Task 6: Clinical Documentation Draft (`DRAFT_NOTE_RESULT`)
- **Purpose:** Draft structured SOAP notes for attending physician review and modification.
- **Payload Schema:**
  ```json
  {
    "subjective_draft": "Patient presents with acute chest discomfort for 2 hours.",
    "objective_observations_draft": "HR 110 bpm, SBP 95 mmHg, SpO2 96%.",
    "advisory_considerations_draft": "Consider acute coronary syndrome; serial ECG and troponins recommended.",
    "disclaimer": "DRAFT ASSISTANT NOTE ONLY. NOT A FINAL CLINICAL RECORD. REQUIRES RMP REVIEW AND SIGN-OFF."
  }
  ```

### 2.7 Task 7: Clinical Advisory Reasoning (`ADVISORY_RESULT`)
- **Purpose:** Surface non-binding differential considerations with strict evidence linkages.
- **Payload Schema:**
  ```json
  {
    "candidate_signals": ["Cardiac", "Hemodynamic Alert"],
    "differential_considerations": [
      {
        "condition_name": "Acute Coronary Syndrome",
        "supporting_evidence_ids": ["ev-001", "ev-002"],
        "opposing_evidence_ids": [],
        "epistemic_note": "Candidate hypothesis based on symptom timeline and tachycardia."
      }
    ],
    "suggested_diagnostic_pathways": ["12-lead ECG", "Serum Troponin I"],
    "safety_reminders": ["RMP physical evaluation required before disposition."],
    "is_autonomous_diagnosis": false
  }
  ```
- **Validation Rules:**
  - `is_autonomous_diagnosis` must be `false` (enforced by Pydantic validator).
