# CLINOVA AI — Core Innovations & Continuous Care Intelligence Specification

> **Document ID:** `DOC-19`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. The Core Differentiator: Continuous Care Intelligence

While the 18 BPUT requirements (`B01`–`B18`) form the mandatory operational baseline, CLINOVA AI's defining innovation is the shift:

$$\mathbf{FROM\ ISOLATED\ TRIAGE} \Longrightarrow \mathbf{TO\ CONTINUOUS\ CARE\ INTELLIGENCE}$$

Conventional triage treats triage as a 90-second administrative snapshot that assigns a static color band and terminates. CLINOVA introduces an interconnected continuous intelligence architecture spanning eleven core innovations (`C01` through `C11`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLINOVA CORE INNOVATION SUITE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ PATIENT LEVEL ]                                                          │
│  ├── C01: CAREGRAPH Dynamic State Engine                                    │
│  ├── C02: Multi-Source Evidence Provenance & Confidence Intelligence        │
│  ├── C03: First-Class Uncertainty Quantification & Contradiction Detection  │
│  └── C04: Next-Best Information (NBI) Engine for Targeted Gap Closure       │
│                                                                             │
│  [ FACILITY LEVEL ]                                                         │
│  ├── C05: FACILITYGRAPH Dynamic Capability & Resource Modeling              │
│  └── C06: Real-Time Care Feasibility & Capability-Matched Routing          │
│                                                                             │
│  [ SYSTEM LEVEL ]                                                           │
│  └── C07: SIGNALGRAPH Privacy-Preserving Syndromic & Operational Telemetry  │
│                                                                             │
│  [ ACTION & DECISION LEVEL ]                                                │
│  ├── C08: Multi-Graph ORCHESTRATION Synthesis Engine                        │
│  └── C09: The Safest Achievable Care Pathway (Resource-Aware Guidance)      │
│                                                                             │
│  [ CONTINUITY & LEARNING LEVEL ]                                            │
│  ├── C10: Post-Disposition Continuity & Real Clinical Outcome Loop          │
│  └── C11: Clinician Decision Learning Signals & Evaluation Calibration      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Eleven Core Innovations (`C01`–`C11`)

### C01: CAREGRAPH Dynamic Patient State Engine
- **Innovation:** Replaces flat tabular records with an active state engine modeling physiological deviations, longitudinal trajectory ($\Delta \text{Vitals} / \Delta t$), and risk bands.
- **Why it matters:** Continuously tracks whether a patient is improving, stable, or deteriorating while waiting, automatically alerting staff to silent decompensations.

### C02: Evidence Provenance Intelligence
- **Innovation:** Binds every clinical value to its exact source modality (`VOICE`, `OCR`, `PATIENT`, `CLINICIAN`, `AI`), timestamp, and confidence score.
- **Why it matters:** Eliminates black-box claims; allows doctors to visually inspect raw source snippets and know exactly who verified the information.

### C03: Uncertainty Quantification & Contradiction Detection
- **Innovation:** Treats what is *unknown* or *conflicting* as a first-class clinical signal rather than silently assuming missing data equals absence of risk.
- **Why it matters:** Prevents diagnostic anchoring and algorithmic overconfidence, explicitly showing clinicians what data gaps exist before a decision is made.

### C04: Next-Best Information (NBI) Engine
- **Innovation:** Uses clinical value-of-information ranking to generate the single highest-yield question or diagnostic test that will collapse uncertainty.
- **Why it matters:** Avoids exhausting patients with endless generic questionnaires; asks only what is clinically decisive.

### C05: FACILITYGRAPH Capability Modeling
- **Innovation:** Models real-time facility capabilities (functioning equipment, ICU beds, oxygen pressure, on-duty specialists) across the regional network.
- **Why it matters:** Understands whether indicated interventions can physically happen at the current clinic or hospital.

### C06: Care Feasibility Engine
- **Innovation:** Synthesizes patient clinical need against facility capacity, geographic distance, and transit time.
- **Why it matters:** Replaces "blind transfers" with guaranteed capability-matched referrals, preventing patients from being sent to hospitals lacking ICU beds or surgeons.

### C07: SIGNALGRAPH System-Level Telemetry
- **Innovation:** Aggregates privacy-preserving syndromic and operational signals across all connected facilities.
- **Why it matters:** Automatically detects emerging infectious disease clusters (e.g., dengue surges) and hospital bottleneck choke points before crises escalate.

### C08: Multi-Graph ORCHESTRATION Synthesis Engine
- **Innovation:** Merges `CareGraph + Uncertainty + FacilityGraph + SignalGraph` into a unified decision-support engine.
- **Why it matters:** Delivers holistically informed candidate actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`) that account for both physiological urgency and physical resource availability.

### C09: The Safest Achievable Care Pathway
- **Innovation:** Reframes AI clinical guidance from an authoritative "diagnostic answer" to an explainable, resource-aware "safest achievable care pathway."
- **Why it matters:** Grounds clinical decision support in operational reality while keeping qualified clinicians firmly in control.

### C10: Post-Disposition Continuity & Outcome Loop
- **Innovation:** Connects decision → action → continuation → real-world clinical outcome back into the patient record.
- **Why it matters:** Eliminates the cliff-edge disconnect between outpatient triage, inpatient wards, referrals, and final patient recovery.

### C11: Clinician Verification Learning Signals
- **Innovation:** Tracks clinician verification, modifications, and overrides against AI advisories to generate calibration signals for model evaluation.
- **Why it matters:** Enables continuous system evaluation and post-hackathon fine-tuning without creating unsafe autonomous feedback loops in production.
