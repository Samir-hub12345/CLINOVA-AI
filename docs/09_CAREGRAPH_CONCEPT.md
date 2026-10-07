# CLINOVA AI — CAREGRAPH Concept Specification

> **Document ID:** `DOC-09`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. What is CAREGRAPH?

> **Core Definition:** CAREGRAPH is an active, functional clinical state engine—not merely a decorative UI network diagram.
>
> It continuously synthesizes multimodal patient observations into a dynamic, stateful clinical representation that answers the single paramount question:
> $$\mathbf{WHAT\ IS\ HAPPENING\ TO\ THIS\ PATIENT\ RIGHT\ NOW?}$$

CAREGRAPH binds eight core dimensions into an interconnected graph:

$$\begin{aligned}
\mathbf{CAREGRAPH} = &\ \mathbf{PATIENT\ STATE} + \mathbf{EVIDENCE} + \mathbf{RISK} + \mathbf{TRAJECTORY} \\
&+ \mathbf{UNCERTAINTY} + \mathbf{MISSING\ INFORMATION} + \mathbf{DECISIONS} + \mathbf{ACTIONS} + \mathbf{OUTCOMES}
\end{aligned}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CAREGRAPH ENGINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                   ┌──────────────────────────────────┐                      │
│                   │      PATIENT PHYSIOLOGICAL       │                      │
│                   │         & SYNDROMIC STATE        │                      │
│                   └────────────────┬─────────────────┘                      │
│                                    │                                        │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          ▼                         ▼                         ▼              │
│   [ EVIDENCE NODES ]        [ RISK & ACUITY ]       [ TRAJECTORY VECTOR ]   │
│   • Source Provenance       • Acuity Score (0-10)   • Improving             │
│   • Confidence (0-1)        • Red-Flag Triggers     • Stable                │
│   • Verification State      • Shock Index           • Worsening             │
│          │                         │                • Unknown               │
│          └─────────────────────────┼─────────────────────────┘              │
│                                    │                                        │
│          ┌─────────────────────────┴─────────────────────────┐              │
│          ▼                                                   ▼              │
│   [ UNCERTAINTY PROFILE ]                             [ MISSING DATA AUDIT ]│
│   • Known / Unknown Ratio                             • Critical Gaps       │
│   • Conflicting Observations                          • Important Gaps      │
│   • Unreliable Extractions                            • Next-Best Info      │
│          │                                                   │              │
│          └─────────────────────────┬─────────────────────────┘              │
│                                    │                                        │
│                                    ▼                                        │
│                   ┌──────────────────────────────────┐                      │
│                   │      CLINICAL DECISIONS & ACTIONS│                      │
│                   │   (Ask, Verify, Escalate, Refer) │                      │
│                   └────────────────┬─────────────────┘                      │
│                                    │                                        │
│                                    ▼                                        │
│                   ┌──────────────────────────────────┐                      │
│                   │     REAL CLINICAL OUTCOMES       │                      │
│                   │ (Recovery, Transfer, Complication│                      │
│                   └──────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dynamic State Engine Behavior

CAREGRAPH is reactive: it recomputes dynamically whenever meaningful clinical evidence, vital sign streams, or clinician actions change.

### Dynamic Triggers for Graph Mutation:
1. **New Multimodal Ingestion:** Ingestion of a newly uploaded lab report or speech transcript adds new observation nodes.
2. **Serial Vital Acquisition:** A second or third blood pressure / SpO2 reading computes the rate-of-change and mutates the **Trajectory Vector** (e.g., from `STABLE` to `WORSENING`).
3. **Clinician Modification:** When a doctor overrides an AI extraction or enters bedside physical exam findings, the node's verification state transitions to `CLINICIAN_VERIFIED`, and uncertainty drops.
4. **Follow-up Q&A Completion:** Answering a high-priority gap question converts an `UNKNOWN` node into a `KNOWN` node, shrinking the uncertainty vector.
5. **Time Decay:** If an un-admitted patient remains in the waiting queue without updated vitals for over 90 minutes, the temporal uncertainty score automatically escalates, prompting re-triage.

---

## 3. Core Graph Components

### 3.1 Patient Physiological & Syndromic State
- **Syndromic Cluster:** Groups related symptoms into standardized clinical syndromes (e.g., *Acute Febrile Illness with Thrombocytopenia*, *Acute Coronary Syndrome Suspect*, *Acute Respiratory Distress*).
- **Physiological Parameter Nodes:** Quantitative and qualitative nodes representing vitals, biomarkers, lab panels, and pain scores.

### 3.2 Evidence Provenance Links
Every parameter node maintains a direct pointer to its underlying `EvidenceNode`, displaying source modality, confidence, raw text/image snippet, and verification status.

### 3.3 Risk & Acuity Stratification
Synthesizes clinical signs and red-flag rules into explainable risk bands:
- `EMERGENCY_RED`: Immediate life threat; resuscitation required.
- `URGENT_AMBER`: High risk of rapid deterioration; bedside review in < 15 mins.
- `OBSERVE_YELLOW`: Moderate risk; requires point-of-care workup and serial vitals.
- `ROUTINE_GREEN`: Low acute risk; suitable for standard outpatient consultation.

### 3.4 Longitudinal Trajectory Vector
Evaluates delta trends over time ($\Delta \text{Vitals} / \Delta t$) rather than isolated snapshots:
- $\mathbf{T} = \text{WORSENING}$: Heart rate climbing, SpO2 dropping, pulse pressure narrowing, increasing pain score.
- $\mathbf{T} = \text{STABLE}$: Parameters within expected baseline tolerances across serial measurements.
- $\mathbf{T} = \text{IMPROVING}$: Normalization of vitals post-intervention.
- $\mathbf{T} = \text{UNKNOWN}$: Single snapshot available; insufficient longitudinal data to establish trend.

### 3.5 Uncertainty & Missing Information Matrix
Quantifies what the clinical team does not know:
- Categorizes all clinical dimensions into `KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`.
- Computes overall case uncertainty score $U \in [0.0, 1.0]$.
- Prioritizes **Next-Best Information (NBI)** targets to guide high-value data collection.

### 3.6 Decisions, Actions, and Outcomes
- Records all clinician verification actions, orders, prescriptions, and disposition instructions.
- Tracks real-world longitudinal outcomes (discharge status, surgical findings, referral acceptance, 48-hour recovery).
- Feeds back into system evaluation and model calibration.

---

## 4. UI Representation of CAREGRAPH

The CAREGRAPH interface must avoid confusing, tangled "spaghetti graphs" and instead deliver a clear, structured clinical visual workspace:
1. **Current State Banner:** Displays current syndrome, risk band, trajectory arrow, and uncertainty badge at a single glance.
2. **State Progression Timeline:** Visualizes state changes across time as a horizontal swimlane.
3. **Evidence & Provenance Explorer:** Visual badges indicating source and verification status on every parameter.
4. **Uncertainty & Gaps Callout:** Dedicated high-contrast panel listing critical missing data and contradictions.
5. **Recommended Next Actions:** Explainable next-step guidance generated by the Orchestration Engine.
