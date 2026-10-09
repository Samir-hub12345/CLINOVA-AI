# CLINOVA AI — Epistemic Uncertainty & AI Confidence Boundary

> **Document ID:** `RES-203`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Informatics, Mathematical Modeling & Safety Systems Group  

---

## 1. The Separation Law: Confidence $\neq$ Certainty $\neq$ Risk

In machine learning, confidence typically denotes the softmax output probability or token log-likelihood. In clinical medicine, however, confidence, epistemic uncertainty, clinical risk, and evidentiary verification represent fundamentally distinct concepts:

$$\mathbf{AI\ Confidence} \neq \mathbf{Epistemic\ Uncertainty\ (}U_t\mathbf{)} \neq \mathbf{Clinical\ Risk} \neq \mathbf{Evidentiary\ Verification}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE FOUR-WAY CLINICAL SEPARATION                      │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ 1. AI Confidence    │ Statistical probability emitted by language model     │
│                     │ $C \in [0.0, 1.0]$. Indicates token sequence stability.│
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 2. Epistemic        │ Mathematical measure of missing clinical evidence     │
│    Uncertainty ($U_t$)│ $U_t \in [0.0, 1.0]$. Based on syndrome protocols.   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 3. Clinical Risk    │ Physiological instability (NEWS2, Shock Index, Red    │
│                     │ Flags). E.g. Acute STEMI has HIGH risk, regardless    │
│                     │ of model confidence.                                  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 4. Evidentiary      │ Human physician verification state (VERIFIED,         │
│    Verification     │ CLINICIAN_APPROVED, AI_INFERRED).                     │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 2. Inviolable Rule: LLM Confidence Never Lowers $U_t$

$$\mathbf{AN\ LLM\ SOUNDING\ CONFIDENT\ MUST\ NEVER\ DECREASE\ } U_t$$

Large language models frequently express fluent, authoritative prose even when essential clinical facts are absent.

**The Golden Epistemic Invariant:**
$$\frac{\partial U_t}{\partial C_{\text{LLM}}} = 0$$

Under no circumstance will an AI model emitting a high confidence score ($C = 0.98$) cause the case's mathematical uncertainty score ($U_t$) to decrease. $U_t$ is computed **strictly deterministically** from objective missing data items:

$$U_t = \sum_{k=1}^{N} w_k \cdot \mathbf{1}_{\{\text{data\_element}_k \text{ is missing}\}}$$

Only the collection of verified factual evidence (a confirmed 12-lead ECG, an automated blood pressure measurement, a serum troponin result) can reduce $U_t$.

---

## 3. Explicit Data Model Separation

In all AI response schemas and database tables, these dimensions are partitioned into isolated fields:

```python
class CanonicalCaseEpistemicRecord(BaseModel):
    case_id: str
    
    # 1. Deterministic Physiological Score
    news2_score: int                        # Pure deterministic integer [0..20]
    clinical_risk_tier: str                 # ROUTINE, URGENT, RESUSCITATION
    
    # 2. Deterministic Epistemic Uncertainty
    epistemic_uncertainty_score: float      # U_t in [0.0, 1.0]
    missing_protocol_elements: List[str]   # ['troponin_i', 'ecg_baseline']
    
    # 3. Model Inference Telemetry (Isolated)
    ai_predictive_confidence: float         # C in [0.0, 1.0]
    ai_epistemic_state: str                 # Strictly 'AI_INFERRED'
    
    # 4. Human Verification Status
    is_clinician_verified: bool             # Strictly FALSE until RMP signs
```

This strict separation guarantees that probabilistic machine predictions never pollute or override deterministic clinical safety metrics.
