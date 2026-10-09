# CLINOVA AI — CAREGRAPH Journey Specification

> **Document ID:** `RES-64`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Concept & Clinical Purpose

$\text{CAREGRAPH}$ is the core clinical reasoning engine of CLINOVA AI. It is an evolving, patient-centric graph representation of physiological states, clinical hypotheses, physiological trajectories, and epistemic uncertainties.

Rather than reducing a patient to a flat, static text note or an opaque scalar score, $\text{CAREGRAPH}$ models the patient encounter as a directed, attributed graph:
$$\mathcal{G}_{\text{care}}(t) = \langle \mathcal{V}_t, \mathcal{E}_t, \mathbf{R}_t, \boldsymbol{\tau}_t, U_t \rangle$$
Where:
- $\mathcal{V}_t$: Set of clinical entity nodes (symptoms, vital signs, laboratory findings, comorbidities, medications).
- $\mathcal{E}_t$: Directed edges representing physiological causality, temporal precedence, and pathophysiological correlation.
- $\mathbf{R}_t$: Dynamic physiological risk vector (NEWS2/MEWS composite acuity).
- $\boldsymbol{\tau}_t$: Physiological disease trajectory ($\text{IMPROVING}, \text{STABLE}, \text{DETERIORATING}, \text{CRITICAL}$).
- $U_t \in [0.0, 1.0]$: Epistemic uncertainty score quantifying the incompleteness or ambiguity of the clinical evidence base.

---

## 2. CAREGRAPH Journey Lifecycle & Invocation Points

$\text{CAREGRAPH}$ is not a one-time calculation. It evolves across nine discrete operational milestones throughout the Master Patient Journey:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAREGRAPH EVOLUTION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ EVENT 1: INSTANTIATION ] ────> S09 (STATE_CONSOLIDATED)                  │
│                                   Initial graph compiled from raw inputs.   │
│                                                                             │
│  [ EVENT 2: VITALS MODULATION ] ─> S07/S08 (STAFF_VERIFIED)                 │
│                                   Point-of-care vitals update risk/nodes.   │
│                                                                             │
│  [ EVENT 3: SYNTHESIS & SCORING ]> S10 (STATE_TRIAGE_READY)                 │
│                                   Computes baseline Risk, Trajectory, Ut.   │
│                                                                             │
│  [ EVENT 4: CLINICIAN DISPLAY ] ─> S12 (STATE_DOCTOR_REVIEWING)             │
│                                   Rendered as interactive topological HUD.  │
│                                                                             │
│  [ EVENT 5: DOCTOR MODIFICATION ]> S13 (STATE_CLINICIAN_VERIFIED)           │
│                                   Recalculates based on verified/edited data│
│                                                                             │
│  [ EVENT 6: REFERRAL HANDOFF ] ──> S20 (STATE_REFERRAL_PENDING)             │
│                                   Serialized as structural graph in pack.   │
│                                                                             │
│  [ EVENT 7: WARD ADMISSION ] ───> S19 (STATE_WARD_ADMITTED)                 │
│                                   Transferred to inpatient monitoring mode. │
│                                                                             │
│  [ EVENT 8: SERIAL OBSERVATION ] > S25 (STATE_OUTCOME_PENDING)              │
│                                   Dynamic trajectory tracking over time.    │
│                                                                             │
│  [ EVENT 9: OUTCOME CLOSURE ] ───> S26/S27 (STATE_RESOLVED / CLOSED)        │
│                                   Ground truth linked; delta updates model. │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Deep-Dive Specification of CAREGRAPH Milestones

### Milestone 1: Instantiation (`STATE_CONSOLIDATED`)
- **Trigger:** Consolidation of patient self-reported data, extracted OCR slips, and transcribed speech.
- **System Action:**
  - Seeds the graph structure with initial symptom nodes and temporal relationships.
  - Labels evidence sources with provenance tags (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`).
  - Initializes Epistemic Uncertainty:
    $$U_0 = 1.0 - \frac{\text{Known Critical Parameters}}{\text{Total Required Critical Parameters}}$$
  - At this stage, if baseline objective vitals are missing, $U_0$ is high ($U_0 \ge 0.60$), preventing overconfident clinical assertions.

### Milestone 2: Modulation by Frontline Vitals (`STATE_STAFF_VERIFIED`)
- **Trigger:** Frontline triage nurse records calibrated physical vitals (BP, SpO2, HR, RR, Temp).
- **System Action:**
  - Adds verified physiological nodes: `Node(SpO2: 94%)`, `Node(BP: 130/85)`, `Node(HR: 98)`.
  - Links vital signs to symptom nodes via physiological correlation edges (e.g., `Node(High Fever)` $\xrightarrow{\text{correlates}}$ `Node(Sinus Tachycardia)`).
  - Recalculates Epistemic Uncertainty: Drops sharply to $U_t < 0.25$ due to objective ground truth.
  - Computes Physiological Risk Score ($\mathbf{R}_t$).

### Milestone 3: Synthesis, Trajectory & Note Generation (`STATE_TRIAGE_READY`)
- **Trigger:** CAREGRAPH engine completes formal traversal.
- **Calculations:**
  - **Risk Stratification:** Classifies into 5 Acuity Bands (Red / P1, Orange / P2, Yellow / P3, Green / P4, Blue / P5).
  - **Physiological Trajectory ($\boldsymbol{\tau}_t$):**
    - `IMPROVING`: Vitals normalizing; symptoms subsiding.
    - `STABLE`: Physiological parameters within expected baselines.
    - `DETERIORATING`: Tachycardia worsening, SpO2 drifting downward, or widening pulse pressure.
    - `CRITICAL`: Overt decompensation; shock or impending respiratory arrest.
  - **Next-Best Information (NBI):** Determines which unmeasured diagnostic test would collapse the remaining diagnostic entropy.
- **Output:** Exports Structured Triage Note and Master Clinical Report (Report Type 1).

### Milestone 4: Clinician Visual Presentation (`STATE_DOCTOR_REVIEWING`)
- **Interface Behavior:** Rendered on the Doctor Review Workbench:
  - Topological graph visualization displaying clusters of related symptoms and physiological parameters.
  - Visual color-coding: Green (Normal), Amber (Borderline / Warning), Red (Critical Danger).
  - Edge thickness indicates strength of physiological correlation.
  - Prominent Uncertainty Gauge showing $U_t$.
  - Interactive click-through: Clicking any node reveals its underlying raw evidence crop (audio snippet, OCR scan, or nurse log).

### Milestone 5: Clinician Verification & Modification Recalculation (`STATE_CLINICIAN_VERIFIED`)
- **Trigger:** Registered Medical Practitioner executes `VERIFY`, `MODIFY`, or `ADD`.
- **System Action:**
  - If doctor modifies a value (e.g., corrects extracted *"fever for 2 weeks"* to *"fever for 2 days"* based on clinical interview):
    - Node attributes are updated with `CLINICIAN_APPROVED` provenance.
    - Previous value archived in tamper-evident modification ledger.
    - Trajectory and differential hypotheses are immediately re-evaluated.
  - If doctor adds bedside examination findings (e.g., auscultation reveals *"bilateral crepitations"* or palpation reveals *"right lower quadrant rebound tenderness"*):
    - New nodes added directly to graph.
    - Risk band and surgical suspicion flags recomputed.

### Milestone 6: Modulation by Inter-Facility Referral (`STATE_REFERRAL_PENDING`)
- **Trigger:** Clinician orders transfer to higher-level hospital.
- **System Action:**
  - Serializes the active $\text{CAREGRAPH}$ into a standardized JSON graph payload embedded in the Digital Referral Dossier (Report Type 2).
  - Encodes the baseline physiological state, trend vector, and pending diagnostic hypotheses so the receiving trauma center receives a rich, structural understanding of disease trajectory rather than flat, static paperwork.

### Milestone 7: Inpatient Ward Admission Transfer (`STATE_WARD_ADMITTED`)
- **Trigger:** Patient admitted to inpatient ward.
- **System Action:**
  - $\text{CAREGRAPH}$ switches from "Outpatient Triage Mode" to "Inpatient Longitudinal Monitoring Mode".
  - Nodes are configured to accept serial bedside nursing charts, automated IV infusion logs, and daily morning lab rounds.
  - Enables trend vector tracking across 12-hour and 24-hour observation windows.

### Milestone 8: Serial Inpatient Monitoring & Decompensation Alerting (`STATE_OUTCOME_PENDING`)
- **Trigger:** Bedside nurse charts repeated vitals or new lab results arrive.
- **System Action:**
  - Trajectory vector $\boldsymbol{\tau}_t$ evaluates the rate of change ($\frac{d\mathbf{R}}{dt}$).
  - If trajectory transitions from `STABLE` $\to$ `DETERIORATING`, the system triggers an early warning alert on the ward dashboard, prompting physician bedside review before overt cardiac arrest or septic collapse.

### Milestone 9: Outcome Resolution & Closed-Loop Delta (`STATE_RESOLVED`)
- **Trigger:** Clinical outcome is recorded (`FULL_RECOVERY`, `STABILIZED`, `COMPLICATION_MANAGED`, `REFERRED_HIGHER`, `ADVERSE_EVENT`).
- **System Action:**
  - The final clinical endpoint is bound to the original graph instance as ground truth.
  - Calculates the **Diagnostic & Triage Concordance Delta**:
    $$\Delta_{\text{care}} = f(\mathbf{R}_{\text{initial}}, \boldsymbol{\tau}_{\text{predicted}}, \text{Outcome}_{\text{actual}})$$
  - Links historical physiological response vectors to the synthetic patient ID, providing longitudinal continuity for subsequent visits.
  - Emits anonymized graph delta telemetry to $\text{SIGNALGRAPH}$ to calibrate system-wide triage weights.

---

## 4. Evolution of Trajectory & Uncertainty

The table below summarizes the formal mathematical evolution of Trajectory ($\boldsymbol{\tau}_t$) and Uncertainty ($U_t$) across key journey milestones:

| Journey Stage | State ID | Typical Uncertainty Range ($U_t$) | Primary Trajectory Driver | Clinical Safeguard |
| :--- | :--- | :---: | :--- | :--- |
| **Raw Intake** | `S02` | $0.70 - 0.95$ | Unstructured patient narrative | High uncertainty prevents early low-risk dismissal. |
| **Missing Audit** | `S05` | $0.50 - 0.85$ | Identified clinical data gaps | Hard blocks on critical missing vitals. |
| **Staff Vitals** | `S08` | $0.10 - 0.30$ | Calibrated physiological metrics | Physical verification collapses epistemic entropy. |
| **CAREGRAPH Ready** | `S10` | $0.05 - 0.20$ | Multi-parameter graph synthesis | Explicit risk band and trajectory vector output. |
| **Doctor Review** | `S13` | $0.00 - 0.05$ | Registered physician physical exam | Clinician sign-off represents authoritative truth. |
| **Inpatient Stay** | `S19` | $0.05 - 0.15$ | Serial vitals trend over time | Trajectory delta flags silent deterioration. |
| **Outcome Closure** | `S26` | $0.00$ | Final verified clinical endpoint | Ground truth recorded; feedback loop sealed. |
