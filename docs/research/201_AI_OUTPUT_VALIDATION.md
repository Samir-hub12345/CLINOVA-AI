# CLINOVA AI — Deterministic AI Output Validation & Safety Barriers

> **Document ID:** `RES-201`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Safety Engineering & Clinical Validation Working Group  

---

## 1. The Output Validation Law

$$\mathbf{NEVER\ SILENTLY\ REPAIR\ MEDICALLY\ MEANINGFUL\ AI\ OUTPUT}$$

If a machine learning model generates an impossible heart rate ($999\text{ bpm}$), fabricates an ungrounded evidence citation, or attempts to prescribe antibiotics, the system **MUST NOT guess or silently sanitize the data**.

Silently altering a clinical output can mask systemic model degradation, introduce subtle physician confusion, or misrepresent patient status.

**The Golden Law of Output Validation:**
Any response failing deterministic safety validation is **INSTANTLY REJECTED**, recorded in the clinical audit ledger as an anomaly event, and diverted to **SAFE DETERMINISTIC FALLBACK**.

---

## 2. The Five-Stage Validation Gatekeeper Pipeline

Before any AI output is exposed to the application layer or persisted in case state, it must survive five sequential deterministic filters:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE DETERMINISTIC VALIDATION PIPELINE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RAW LLM TEXT COMPLETION                                                   │
│          │                                                                  │
│          ▼                                                                  │
│   [ GATE 1: JSON SYNTAX VALIDATION ]                                        │
│   • Parses string; strips markdown code fences                              │
│   • Rejects unclosed brackets, missing commas (`REJECTED_MALFORMED`)        │
│          │                                                                  │
│          ▼                                                                  │
│   [ GATE 2: FORBIDDEN CLINICAL ACTION SCAN ]                                │
│   • Rejects prescriptions, admission orders, discharge orders               │
│   • Rejects autonomous diagnostic assertions (`REJECTED_FORBIDDEN_ACTION`)  │
│          │                                                                  │
│          ▼                                                                  │
│   [ GATE 3: PHYSIOLOGICAL RANGE BARRIER ]                                   │
│   • Rejects biologically impossible vitals:                                 │
│     - HR not in [20, 300] bpm                                               │
│     - SBP not in [30, 300] mmHg                                             │
│     - SpO2 not in [30, 100] %                                               │
│     - Temp not in [25.0, 45.0] °C (`REJECTED_OUT_OF_BOUNDS`)                │
│          │                                                                  │
│          ▼                                                                  │
│   [ GATE 4: EVIDENCE GROUNDING & CITATION VERIFICATION ]                   │
│   • Verifies all `source_evidence_id`s exist in Context Pack                │
│   • Rejects phantom UUIDs or ungrounded claims (`REJECTED_UNGROUNDED`)      │
│          │                                                                  │
│          ▼                                                                  │
│   [ GATE 5: PYDANTIC SCHEMA & TYPE ENFORCEMENT ]                            │
│   • Verifies non-null required fields, array bounds, enum values            │
│   • Rejects missing schema fields (`REJECTED_SCHEMA`)                       │
│          │                                                                  │
│          ▼                                                                  │
│   VALIDATED PAYLOAD -> PROVENANCE BINDING -> PRESENTATION                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Physiological Range Specification

Vitals extracted by generative models must fall within biological human feasibility:

| Parameter | Minimum Viable Value | Maximum Viable Value | Unit | Action on Breach |
|:---|:---|:---|:---|:---|
| **Heart Rate (HR)** | $20.0$ | $300.0$ | bpm | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Systolic Blood Pressure (SBP)** | $30.0$ | $300.0$ | mmHg | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Diastolic Blood Pressure (DBP)** | $20.0$ | $200.0$ | mmHg | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Respiratory Rate (RR)** | $4.0$ | $80.0$ | breaths/min | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Oxygen Saturation (SpO2)** | $30.0$ | $100.0$ | % | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Body Temperature (Celsius)** | $25.0$ | $45.0$ | °C | Reject (`REJECTED_OUT_OF_BOUNDS`) |
| **Body Temperature (Fahrenheit)**| $77.0$ | $113.0$ | °F | Reject (`REJECTED_OUT_OF_BOUNDS`) |

---

## 4. Rejection Handling & Fallback Flow

When validation fails:
1. `status` is set to `"REJECTED"`.
2. `validation_state` records the exact rejection code.
3. The `errors` array captures detailed diagnostic reasons.
4. The invalid AI payload is **suppressed from clinical view**.
5. The application notifies the user via an unobtrusive informational warning and keeps manual entry fields accessible.
