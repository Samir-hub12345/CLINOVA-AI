# CLINOVA AI — Minimum-Necessary Context & Grounding Model

> **Document ID:** `RES-199`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering, Clinical Data Protection & Privacy Group  

---

## 1. The Minimum-Necessary Context Principle

$$\mathbf{NEVER\ SEND\ THE\ WHOLE\ PATIENT\ RECORD\ TO\ THE\ MODEL}$$

Language models supplied with massive context windows suffer from "attention dilution," increased inference latency, and heightened risk of privacy leakage.

Under the **Digital Personal Data Protection (DPDP) Act 2023** (Section 6: Purpose Limitation & Data Minimisation), clinical software must limit data processing strictly to what is necessary for the specific operational purpose.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CANONICAL GROUNDING PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ MASTER CASE RECORD ]                                                     │
│  • Full patient chart, billing history, national ID, administrative logs    │
│  • Clinician private notes, prior years' unrelated consultations            │
│          │                                                                  │
│          ▼                                                                  │
│  [ EPISODIC EVIDENCE FILTER ]                                               │
│  • Selects ONLY evidence records tagged to current acute intake episode     │
│  • Strips Aadhaar, phone numbers, billing insurance IDs                     │
│  • Excludes hidden private clinician notes and sensitive tags               │
│          │                                                                  │
│          ▼                                                                  │
│  [ ASSEMBLED CONTEXT PACK ]                                                 │
│  • Pure clinical observations (Vitals, Transcript, Chief Complaint)        │
│  • Explicit UUIDs tagged to each evidence record (`ev-001`, `ev-002`)       │
│  • Wrapped in defensive untrusted data blocks                               │
│          │                                                                  │
│          ▼                                                                  │
│  [ LOCAL AI RUNTIME ] (Qwen SLM)                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Category-Level Context Inclusion Matrix

| Data Category | Included in Context? | Minimisation & Privacy Rationale |
|:---|:---|:---|
| **Direct Patient Identifiers** (Name, Aadhaar, Phone, Address) | **STRICTLY EXCLUDED** | High risk of privacy breach; zero utility for symptom extraction or triage. |
| **Administrative & Billing Data** (Insurance, ABHA ID, Payments) | **STRICTLY EXCLUDED** | Irrelevant to acute clinical condition. |
| **Confidential / Private Clinician Notes** | **STRICTLY EXCLUDED** | Doctor-only private notes protected under medical privilege. |
| **Historical Records $\ge 1\text{ Year Old}$ (Unrelated)** | **EXCLUDED** | Prevents context pollution; old orthopedic surgeries irrelevant to acute chest pain. |
| **Active Episode Vitals & Timecodes** | **INCLUDED** | Critical for physiological trajectory evaluation. |
| **Current Intake Audio Transcript / Narrative** | **INCLUDED** | Primary perceptual signal required for entity extraction. |
| **Known Allergies & Active Medications** | **INCLUDED** | Safety critical for drug interaction detection. |
| **Relevant Chronic Comorbidities** (Diabetes, HTN) | **INCLUDED** | Contextual risk modifiers. |

---

## 3. Evidence Pointer & Grounding Verification

Every entity emitted by the model must cite the unique identifier of the evidence item that justified it:

```json
{
  "name": "Dyspnea",
  "duration": "4 hours",
  "source_evidence_id": "ev-transcript-acute-001"
}
```

### Deterministic Linkage Audit
During post-inference validation, `OutputValidator.check_grounding_references()` executes a set membership check:
$$\forall \text{ cited\_id} \in \text{Output}, \quad \text{cited\_id} \in \mathbf{AllowedEvidenceIDs}$$

If the model produces a phantom UUID or attributes a symptom to an evidence item not present in the supplied Context Pack:
1. The output fails validation with `REJECTED_UNGROUNDED`.
2. The hallucination is intercepted before clinical presentation.
3. The system records an epistemic grounding alert in audit telemetry.
