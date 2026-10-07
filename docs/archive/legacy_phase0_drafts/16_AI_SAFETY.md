# CLINOVA AI — AI Clinical Safety & Governance Mandate

> **Document ID:** `DOC-16`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. The Clinical Safety Mandate

In healthcare applications, unconstrained probabilistic AI systems pose severe hazards: hallucinated symptoms, ungrounded diagnostic claims, missed red flags, and hidden diagnostic uncertainty.

**CLINOVA AI operates under a strict, non-negotiable Clinical Safety Mandate:**
$$\mathbf{Non\text{-}Diagnostic \quad\vert\quad Advisory\ Only \quad\vert\quad Mandatory\ Human\text{-}in\text{-}the\text{-}Loop}$$

The system is engineered as an **Adaptive Clinical Care Intelligence & Navigation Platform**, designed to augment qualified healthcare professionals, eliminate cognitive fatigue, and prevent operational blind spots—never to replace human clinical judgment.

---

## 2. Permitted vs Prohibited AI Operations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINICAL AI CAPABILITY BOUNDARY                       │
├─────────────────────────────────────────┬───────────────────────────────────┤
│ PERMITTED AI ASSISTANCE                 │ STRICTLY PROHIBITED AI ACTIONS    │
├─────────────────────────────────────────┼───────────────────────────────────┤
│ ✓ Clinical entity extraction            │ ✗ Authoritative medical diagnosis │
│ ✓ Longitudinal timeline summarization   │ ✗ Drug or dosage prescription     │
│ ✓ Multi-language translation            │ ✗ Autonomous clinical orders      │
│ ✓ OCR key-value tabular parsing         │ ✗ Overriding a qualified doctor   │
│ ✓ Identifying missing protocol data     │ ✗ Hallucinating patient facts     │
│ ✓ Generating targeted follow-up prompts │ ✗ Hiding evidence uncertainty     │
│ ✓ Early warning risk stratification     │ ✗ Unsupervised emergency routing  │
│ ✓ Facility capability-matching          │ ✗ Converting inference to fact    │
└─────────────────────────────────────────┴───────────────────────────────────┘
```

---

## 3. Anti-Hallucination & Evidence Grounding Engine

Every clinical attribute presented in CLINOVA AI must be strictly grounded in documented evidence:

1. **Explicit Provenance Binding:**
   No symptom, vital sign, or lab result can exist in CareGraph without a direct provenance edge (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, or `CLINICIAN_VERIFIED`).
2. **Confidence-Weighted Extraction:**
   Every extraction carries a numeric confidence score ($[0.0, 1.0]$). Extractions below $0.70$ are flagged with an unverified warning badge and do not trigger aggressive acuity scoring.
3. **First-Class Uncertainty:**
   When evidence is incomplete, the system refuses to "guess." Instead, it formally transitions to `INSUFFICIENT_DATA` or raises an `ASK` recommendation to prompt the human user for clarifying input.

---

## 4. Clinician Override & Auditability

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLINICIAN OVERRIDE WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ Orchestration Advisory Recommendation ]                                 │
│   "Safest Next Action: REFER to District Hospital (Cardiac ICU Feasible)"    │
│                                │                                            │
│                                ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    QUALIFIED CLINICIAN EVALUATION                   │   │
│   │  Doctor examines patient bedside; identifies atypical presentation. │   │
│   │                                                                     │   │
│   │  [ ACCEPT RECOMMENDATION ]          [ OVERRIDE RECOMMENDATION ]     │   │
│   └───────────────────────────────────────────────┬─────────────────────┘   │
│                                                   │                         │
│                                                   ▼                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    STRUCTURED OVERRIDE CAPTURE                      │   │
│   │  Mandatory Rationale Selection:                                     │   │
│   │  - [x] Bedside clinical exam contradicts triage telemetry           │   │
│   │  - [ ] Patient family declines inter-facility transfer              │   │
│   │  - [ ] Specialized consultant available on-site immediately        │   │
│   │  Free-text Doctor Note: "Bedside ultrasound shows normal LV function│   │
│   │  and pericardial effusion; managing locally with pericardiocentesis."│  │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│   [ Immutable Medicolegal Audit Entry & CareGraph State Transition ]        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Systemic Governance & Middleware Enforcement

1. **HTTP Safety Headers:**
   All HTTP responses automatically inject:
   - `X-Clinical-Safety: Non-Diagnostic-Advisory-Only`
   - `X-Human-In-The-Loop: Required-Before-Action`
2. **Persistent Visual Disclaimer:**
   Every page, modal, and report in the UI displays a clear clinical advisory banner warning that recommendations require authorized physician verification before clinical action.
