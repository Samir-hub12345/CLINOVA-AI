# CLINOVA AI — Runtime Model Card: Local Qwen SLM Foundation

> **Document ID:** `RES-216`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering, Clinical Safety & Regulatory Compliance Group  

---

```
================================================================================
                    CRITICAL REGULATORY & CLINICAL DISCLAIMERS
================================================================================
  ⚠️  NOT CLINICALLY VALIDATED
  ⚠️  NOT CERTIFIED AS A MEDICAL DEVICE
  ⚠️  NOT FOR AUTONOMOUS DIAGNOSIS
  ⚠️  NOT FOR AUTONOMOUS PRESCRIPTION
  ⚠️  NOT FOR AUTONOMOUS PATIENT ADMISSION OR DISCHARGE

  This model is an unvalidated open-weight language model component operated as
  an isolated advisory perception adapter. All outputs MUST be reviewed, validated,
  and signed off by a licensed Registered Medical Practitioner (RMP).
================================================================================
```

---

## 1. Model Details

- **Model Name:** CLINOVA Local Clinical SLM Adapter (`clinova-local-qwen3-4b`)
- **Base Model Source:** Qwen3-4B-Instruct (Alibaba Cloud open-weights repository)
- **Base Architecture:** Transformer decoder-only language model with RoPE embeddings
- **Parameter Count:** 4.02 Billion parameters
- **License:** Apache 2.0 (Open-Source, Permissive)
- **Model Version:** 1.0.0 (Phase 10 Foundation Baseline)
- **Quantization:** GGUF 4-bit medium (`Q4_K_M`)
- **Serving Runtimes:** llama.cpp / llama-server / Ollama local daemon
- **Authorship:** CLINOVA AI owns the runtime orchestration, defensive sanitization, and output validation framework. CLINOVA does NOT claim to have pre-trained or clinically fine-tuned the base model weights.

---

## 2. Intended Uses (Advisory Decision Support Only)

The model is strictly bounded to the following advisory and structuring tasks:
1. **Clinical Narrative Extraction:** Parsing unstructured symptom descriptions, reported durations, and explicit vital sign mentions from patient-reported text or speech transcripts.
2. **Timeline Summarization:** Synthesizing chronological progress notes from discrete episodic observations while declaring missing facts.
3. **Value-of-Information Inquiry:** Formulating 1–3 non-alarming clarification questions to close epistemic gaps.
4. **Vernacular Translation:** Translating Odia and Hindi colloquial speech into standardized English clinical descriptions while preserving regional somatic idioms verbatim.
5. **Terminology Normalization:** Proposing candidate mappings from colloquial terms to standardized vocabularies (SNOMED-CT, LOINC).
6. **Documentation Drafting:** Drafting non-binding SOAP clinical progress notes for attending physician editing and signature.

---

## 3. Strictly Prohibited Uses

Under Indian statutory law (NMC Regulations 2023, DPDP Act 2023) and CLINOVA architectural invariants, the model is **STRICTLY PROHIBITED** from:
1. Emitting definitive medical diagnoses.
2. Generating drug dosages or medical prescriptions (Rx).
3. Authorizing inpatient ward admissions or intensive care transfers.
4. Authorizing hospital discharge or emergency sign-offs.
5. Authorizing surgical procedures.
6. Overriding or modifying a human physician's clinical decision.
7. Self-verifying evidence records or altering system case states.
8. Generating synthetic clinical facts not present in source evidence.

---

## 4. Known Limitations & Failure Modes

1. **Hallucination Risk:** Generative language models may confabulate unsupported clinical entities or medical history if supplied with ambiguous context.
2. **Regional Dialect Nuances:** Extreme rural colloquialisms or mixed tribal dialects in southern and western Odisha may be misclassified or dropped during normalization.
3. **Probabilistic Reasoning Drift:** Generative models are sensitive to prompt phrasing variations and cannot guarantee deterministic triage classifications.
4. **Hardware Thermal Throttling:** On fanless edge Mini-PCs under high ambient temperatures ($>40^\circ\text{C}$), CPU throttling may increase latency from 2 seconds to $>6$ seconds.

---

## 5. Hardware & Privacy Assumptions

- **Hardware Assumption:** Minimum Intel Celeron N5105 / N100 or Core i5 CPU, $\ge 8\text{ GB}$ system RAM, $\ge 20\text{ GB}$ local SSD storage.
- **Network Boundary:** 100% On-Premise Localhost Loopback (`127.0.0.1`). Zero external cloud network connections.
- **Zero Egress:** Zero patient identifiable information (PHI) is ever transmitted to commercial third-party cloud APIs.
- **Evaluation Status:** Architecture validated via hermetic test harness double (`MockDeterministicAdapter`). Hardware-in-the-loop clinical trial pending Phase 11+.
