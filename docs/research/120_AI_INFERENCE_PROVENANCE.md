# CLINOVA AI — Artificial Intelligence Inference Provenance & Advisory Guardrails

> **Document ID:** `RES-120`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Statutory Framework: Physician Monopoly under NMC Regulations 2023

Under the **National Medical Commission (Registered Medical Practitioner — Professional Conduct) Regulations, 2023** (Regulations 27 & 28), the practice of medicine in India is strictly reserved for qualified humans registered on the National Medical Register (NMR):
- Only an RMP may issue a valid medical prescription.
- Only an RMP may sign off on a formal clinical diagnosis.
- Only an RMP may authorize hospital admission, surgical intervention, or patient discharge.

Any software system that executes autonomous medical decisions violates Indian law, constitutes illegal medical practice, and exposes healthcare providers to criminal and civil liability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL AI ADVISORY SAFETY INVARIANT                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│          AI INFERENCE IS STRICTLY ADVISORY DECISION SUPPORT.                │
│                                                                             │
│   Under no operational, technical, or emergency circumstance may an AI      │
│   model autonomously create, sign, or transition any of the following:      │
│     1. VERIFIED or CLINICIAN_APPROVED status                                │
│     2. Medical Diagnosis (ICD-11)                                           │
│     3. Drug Prescription (Rx)                                               │
│     4. Inpatient Ward Admission                                             │
│     5. Hospital Discharge Sign-off                                          │
│     6. Surgical Procedure Authorization                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory AI Inference Provenance Metadata

To ensure that machine intelligence remains fully auditable and transparent, every AI-generated inference (differential hypothesis, red-flag alert, symptom extraction, or care pathway recommendation) must record eight immutable provenance attributes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MANDATORY AI INFERENCE METADATA                         │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Model & Provider  │ Architecture name (e.g. clinova-clinical-slm-8b)     │
│ 2. Checkpoint Hash   │ SHA-256 hash of model weights or quantized edge GGUF │
│ 3. Prompt Template   │ Git commit hash and template ID of prompt system     │
│ 4. Generation Time   │ Exact UTC timestamp of inference completion          │
│ 5. Source Evidence   │ Array of input evidence_record UUIDs fed to context  │
│ 6. Model Confidence  │ Calibrated predictive probability score C in [0, 1]  │
│ 7. Model Entropy     │ Token entropy or ensemble variance uncertainty score │
│ 8. Review Status     │ Human disposition: PENDING, ACCEPTED, MODIFIED, REJ. │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 3. Grounding Integrity: Anti-Hallucination Evidence Pointers

A language model must never be permitted to produce "ungrounded" clinical hypotheses. If an AI model asserts:
> *"Patient is presenting with features suggestive of Acute Appendicitis."*

The inference record MUST store the explicit list of input evidence records that justified this deduction:
- `source_evidence_ids = [uuid_rlq_pain, uuid_vomiting, uuid_fever, uuid_rebound_tenderness]`

If the model produces a diagnosis or assertion that is **NOT grounded** in any underlying evidence record in the case, the system’s Epistemic Safety Validator intercepts the payload, flags it as `UNGROUNDED_MODEL_ASSERTION`, suppresses it from the primary clinical interface, and diverts it to the model safety telemetry pipeline.

---

## 4. Human-in-the-Loop Review Disposition Dynamics

Every AI inference presented on the Doctor Workbench exists in one of four human review states:

```
┌──────────────┐     Clinician Accepts As-Is     ┌──────────────┐
│   PENDING    │ ──────────────────────────────► │   ACCEPTED   │ (Promoted to Draft Order/Dx)
└──────┬───────┘                                 └──────────────┘
       │
       ├──────────── Clinician Overrides/Edits ──►┌──────────────┐
       │                                         │   MODIFIED   │ (Preserves both AI & Doctor text)
       │                                         └──────────────┘
       │
       └──────────── Clinician Rejects ──────────►┌──────────────┐
                                                 │   REJECTED   │ (Suppressed from clinical flow)
                                                 └──────────────┘
```

### The Modification Ledger Principle
When an RMP modifies or rejects an AI recommendation:
1. The original AI inference text, confidence, and model version are **NEVER overwritten or deleted**.
2. An immutable row is written to `clinician_modifications`, recording:
   - `original_ai_payload`: The exact machine suggestion.
   - `clinician_replacement_value`: What the doctor actually ordered/diagnosed.
   - `override_reason`: Structured clinical explanation (e.g., *"Patient has atypical contraindication not recognized by model"*).
   - `clinician_id`: Attending physician’s user ID and NMR registration number.

---

## 5. Canonical AI Inference Relational Schema

```sql
CREATE TABLE ai_inferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    inference_type VARCHAR(32) NOT NULL CHECK (inference_type IN (
        'SYMPTOM_EXTRACTION', 'DIFFERENTIAL_HYPOTHESIS', 'RED_FLAG_DETECTION', 
        'MISSING_DATA_RECOMMENDATION', 'ORCHESTRATION_ADVICE', 'RISK_PROJECTION'
    )),
    
    -- Model Identification & Provenance
    model_name VARCHAR(64) NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    model_weights_sha256 CHAR(64) NOT NULL,
    prompt_template_id VARCHAR(64) NOT NULL,
    prompt_git_commit_hash CHAR(40) NOT NULL,
    runtime_environment VARCHAR(32) NOT NULL DEFAULT 'EDGE_ONNX_LOCAL' CHECK (runtime_environment IN (
        'EDGE_ONNX_LOCAL', 'EDGE_LLAMA_CPP', 'CENTRAL_CLOUD_API'
    )),
    
    -- Grounding Evidence Links (Mandatory)
    grounding_evidence_ids JSONB NOT NULL, -- Array of UUIDs: ["uuid1", "uuid2"]
    
    -- Inference Output & Statistical Measures
    generated_payload JSONB NOT NULL,
    calibrated_confidence NUMERIC(4,3) NOT NULL CHECK (calibrated_confidence >= 0.0 AND calibrated_confidence <= 1.0),
    model_uncertainty_score NUMERIC(4,3) NOT NULL CHECK (model_uncertainty_score >= 0.0 AND model_uncertainty_score <= 1.0),
    inference_latency_ms INTEGER NOT NULL CHECK (inference_latency_ms >= 0),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Human Review & Governance
    review_status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (review_status IN (
        'PENDING', 'ACCEPTED', 'MODIFIED', 'REJECTED'
    )),
    reviewed_by_clinician_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    clinician_override_justification TEXT,
    
    -- Legal Guardrail Check: Prohibit autonomous clinical sign-off
    CONSTRAINT chk_ai_never_autonomous CHECK (
        review_status != 'ACCEPTED' OR (reviewed_by_clinician_id IS NOT NULL AND reviewed_at IS NOT NULL)
    )
);

CREATE INDEX ix_ai_inf_case ON ai_inferences(case_id);
CREATE INDEX ix_ai_inf_status ON ai_inferences(review_status);
CREATE INDEX ix_ai_inf_type ON ai_inferences(inference_type);
```

By enforcing these cryptographic, structural, and legal constraints, CLINOVA AI empowers doctors with cutting-edge artificial intelligence while remaining $100\%$ compliant with statutory Indian medical jurisprudence.
