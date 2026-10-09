# CLINOVA AI — Layered Hallucination Control Architecture

> **Document ID:** `RES-202`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Safety Engineering & Clinical Epistemic Integrity Group  

---

## 1. Clinical Hallucination Threat Taxonomy

In clinical medicine, hallucinations are not merely stylistic anomalies; they represent serious patient safety hazards. CLINOVA categorizes hallucinations into four clinical risk tiers:

1. **Entity Invention:** Generating unstated clinical signs (e.g., claiming "patient has jaundice" when the patient only complained of fever).
2. **Timeline & Trajectory Fabrication:** Inventing duration or sequence (e.g., converting "pain started today" into "chronic pain for 6 months").
3. **Citation Spoofing:** Citing real evidence IDs (`ev-001`) for assertions that do not exist anywhere in that evidence record.
4. **False Certainty / Uncertainty Suppression:** Declaring a definitive diagnosis when laboratory or imaging evidence is completely absent.

---

## 2. The Seven-Layer Hallucination Control Perimeter

To suppress and intercept hallucinations, CLINOVA enforces seven concentric defensive layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE SEVEN-LAYER HALLUCINATION CONTROL PERIMETER             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: EVIDENCE-GROUNDED CONTEXT ASSEMBLY                                │
│  • Only verified episodic observations are fed to the model context.        │
│  • Outdated or unrelated history is pruned to avoid associative confabulation│
│                                                                             │
│  LAYER 2: EXPLICIT SOURCE REFERENCE BINDING                                 │
│  • System prompts mandate that every extracted entity cite an evidence ID.  │
│                                                                             │
│  LAYER 3: GRAMMAR-CONSTRAINED SCHEMA VALIDATION                             │
│  • Strict Pydantic types prevent the model from adding hallucinated keys.   │
│                                                                             │
│  LAYER 4: DETERMINISTIC EVIDENCE-LINK VALIDATION                            │
│  • OutputValidator verifies that every cited ID is member of Context Pack.  │
│  • Phantom citations trigger immediate REJECTED_UNGROUNDED status.          │
│                                                                             │
│  LAYER 5: FORBIDDEN-ACTION & CLAIMS SCANNER                                 │
│  • Regex filters reject prescriptions, definitive diagnoses, and admissions.│
│                                                                             │
│  LAYER 6: MANDATORY UNCERTAINTY MARKING                                     │
│  • Prompts require explicit 'uncertainty_statement' declaring missing data. │
│  • Hypotheses without evidence are labeled candidate advisory thoughts.     │
│                                                                             │
│  LAYER 7: MANDATORY HUMAN-IN-THE-LOOP (RMP) REVIEW                          │
│  • All inferences presented as advisory suggestions requiring physician sign│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Ungrounded Hypothesis Policy

If a generative model surfaces a differential diagnosis consideration that lacks supporting evidence in the case record:
1. **Advisory Rule:** If the model proposes an ungrounded consideration without citing an evidence ID, `OutputValidator` rejects the advisory item (`REJECTED_UNGROUNDED`).
2. **No Autonomous Assertion:** Under no circumstances is an ungrounded inference promoted to the clinical diagnosis column.
3. **Telemetry Capture:** Rejected hallucinations are preserved in technical telemetry for model fine-tuning audits.
