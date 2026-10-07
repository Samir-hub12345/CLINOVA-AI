# CLINOVA AI — Core Innovation Specification

> **Document ID:** `DOC-03`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Beyond Isolated Triage: The Quad-Graph Paradigm

Conventional health software operates in disconnected silos: electronic health records (EHRs) store historic documentation, triage desks log static acuity numbers, bed management tools track census counts, and public health dashboards display retrospective case registries.

**CLINOVA AI** unifies these dimensions into an **Adaptive Clinical Care Intelligence** architecture composed of four dynamically interacting graphs:

```
                  ┌─────────────────────────────────────────┐
                  │               CAREGRAPH                 │
                  │   Patient Clinical State & Trajectory   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
 ┌───────────────────────┐   ┌───────────────────┐   ┌────────────────────────┐
 │     FACILITYGRAPH     │──>│   ORCHESTRATION   │<──│      SIGNALGRAPH       │
 │   Care Feasibility    │   │      ENGINE       │   │   System Telemetry     │
 │ & Real-Time Capacity  │   │  Safest Pathway   │   │  & Surge Intelligence  │
 └───────────────────────┘   └─────────┬─────────┘   └────────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ QUALIFIED CLINICIAN GATE  │
                         │   Human-in-the-Loop Sign  │
                         └───────────────────────────┘
```

---

## 2. Pillar 1: CAREGRAPH (Patient-Level Clinical State)

### 2.1 Definition & Objective
CareGraph is a dynamic, longitudinal state representation of an individual patient encounter. It continuously answers the core clinical question:
$$\mathbf{What\ is\ happening\ to\ this\ patient\ right\ now?}$$

CareGraph is **not** a decorative static graphic; it is an active graph database model that recalculates risk, trajectory, and uncertainty every time a new clinical data point (vital, symptom, lab value, or observation) is introduced.

### 2.2 Core Node & Edge Typology
- **Nodes:**
  - `PatientProfile`: Pseudonymized baseline (age group, biological sex, pregnancy status, known chronic conditions).
  - `SymptomNode`: Subjective complaint, anatomical region, severity (1–10), onset timestamp.
  - `VitalSignNode`: Objective physiological metrics (Heart Rate, Systolic/Diastolic BP, SpO2, Respiratory Rate, Temperature, GCS).
  - `DiagnosticNode`: Point-of-care or laboratory findings (Blood Glucose, Troponin, Hemoglobin, Chest X-Ray findings).
  - `EvidenceNode`: Attached file or document origin (raw voice audio, OCR slip, clinician direct entry).
  - `DecisionNode`: Qualified clinician intervention, sign-off, or override.
- **Edges:**
  - `PRECEDES` / `EVOLVES_TO`: Temporal relationship between longitudinal measurements.
  - `DERIVED_FROM`: Provenance link associating an extracted vital to its source document.
  - `AGGRAVATES` / `CORRELATES_WITH`: Clinical interaction between physiological findings.
  - `VALIDATED_BY`: Clinician verification link promoting raw data to verified clinical evidence.

### 2.3 Mathematical Formulations
1. **Risk Score ($R_t$):**
   $$R_t = f(\text{Vitals}_t, \text{RedFlags}_t, \text{Comorbidities}) \in [0.0, 1.0]$$
   Computed via deterministic clinical scoring rules (modified National Early Warning Score - NEWS2) coupled with red-flag keyword triggers.
2. **Trajectory Slope ($\Delta R$):**
   $$\Delta R = \frac{R_t - R_{t-\Delta t}}{\Delta t}$$
   - $\Delta R > +0.15/\text{hr}$: Rapid Deterioration (Triggers immediate clinical alert).
   - $-0.05 \le \Delta R \le +0.05$: Stable.
   - $\Delta R < -0.10/\text{hr}$: Improving.
3. **Evidence Uncertainty ($\mathcal{U}_t$):**
   $$\mathcal{U}_t = 1.0 - \left( w_1 \cdot \mathcal{C}_{\text{data}} + w_2 \cdot \mathcal{Q}_{\text{prov}} - w_3 \cdot \mathcal{M}_{\text{crit}} \right)$$
   Where:
   - $\mathcal{C}_{\text{data}}$: Completeness ratio of protocol-required parameters.
   - $\mathcal{Q}_{\text{prov}}$: Mean confidence score of raw evidence (OCR confidence, transcription quality).
   - $\mathcal{M}_{\text{crit}}$: Penalty for missing critical exclusionary markers (e.g., chest pain without ECG or troponin).

---

## 3. Pillar 2: FACILITYGRAPH (Care Feasibility Intelligence)

### 3.1 Definition & Objective
FacilityGraph models the operational reality of healthcare facilities across a coordinated network. It answers the fundamental operational question:
$$\mathbf{Can\ the\ required\ care\ actually\ be\ delivered\ here,\ and\ where\ else\ can\ it\ safely\ happen?}$$

A patient exhibiting signs of an acute ischemic stroke requires immediate non-contrast head CT and thrombolytic capability. If the presenting PHC lacks a working CT scanner, recommending "on-site admission" is a clinical failure. FacilityGraph evaluates care feasibility before actions are suggested.

### 3.2 Facility Node Attributes
- **Facility Identity:** Facility ID, Name, Tier (PHC, CHC, Sub-District Hospital, District Hospital, Tertiary Medical College), Geolocation.
- **Service & Specialty Capabilities:**
  - Emergency / Resuscitation Bay (Active/Inactive)
  - Critical Care: Adult ICU, PICU, NICU (Bed Count, Occupancy)
  - Diagnostic Labs: 24/7 Point-of-Care, Arterial Blood Gas, Troponin, CBC, Microbiology
  - Imaging Capabilities: Ultrasound, X-Ray, CT Scanner (Operating Status: Online / Offline / Maintenance)
  - Surgical & Interventional: Emergency OT, General Surgery, Orthopedics, Obstetrics
  - Critical Consumables: Blood Bank (Packed Red Cells, Platelets), Medical Oxygen Reserves, Antivenom
- **Real-Time Operational Pressures:**
  - Bed Occupancy Rate ($\%$)
  - Emergency Department Queue Backlog (Waiting patient count, average wait time in minutes)
  - On-Duty Staffing Ratio (Medical officers, emergency nurses, intensivists available)

### 3.3 Care Feasibility Evaluation Function
For a required clinical intervention bundle $\mathcal{I}_{\text{req}}$ (e.g., $\{\text{CT\_HEAD}, \text{ICU\_BED}, \text{NEURO\_EVAL}\}$):
$$\text{Feasibility}(F, \mathcal{I}_{\text{req}}) = \begin{cases} 
\text{FEASIBLE} & \text{if } \forall i \in \mathcal{I}_{\text{req}}, \text{Capability}(F, i) = \text{TRUE} \land \text{Capacity}(F, i) > 0 \\
\text{DEGRADED} & \text{if } \text{Capability}(F, i) = \text{TRUE} \land \text{Capacity}(F, i) \approx 0 \\
\text{INFEASIBLE} & \text{if } \exists i \in \mathcal{I}_{\text{req}}, \text{Capability}(F, i) = \text{FALSE}
\end{cases}$$

---

## 4. Pillar 3: SIGNALGRAPH (System Telemetry & Surge Intelligence)

### 4.1 Definition & Objective
SignalGraph aggregates privacy-preserving, synthetic telemetry from all patient intake events and facility status changes across the healthcare cluster. It answers:
$$\mathbf{What\ is\ happening\ across\ the\ connected\ healthcare\ environment?}$$

### 4.2 Aggregated Telemetry Dimensions
1. **Syndromic Clusters:** Temporal and geographic spikes in correlated symptoms (e.g., sudden $300\%$ increase in acute respiratory distress across three adjacent sub-districts).
2. **Facility Queue Pressures:** Cascading bottlenecks where District Hospital ED wait times exceed 180 minutes, creating diversion pressure on secondary centers.
3. **Resource Exhaustion Signals:** Real-time warnings when regional antivenom stocks drop below 5 vials or blood bank O-negative units fall into critical shortage.

### 4.3 Privacy Preservation Standard
SignalGraph strictly consumes **de-identified aggregate metrics**. Individual patient PII, exact timestamps, and personal notes are never ingested into the SignalGraph node tree. Only anonymized syndrome tags, age brackets, and geographic facility IDs are broadcast.

---

## 5. Pillar 4: ORCHESTRATION ENGINE (Decision & Action Synthesis)

### 5.1 Definition & Objective
The Orchestration Engine is the cognitive synthesis core of CLINOVA AI. It unifies:
$$\mathbf{CareGraph} + \mathbf{Evidence\ Uncertainty} + \mathbf{FacilityGraph} + \mathbf{SignalGraph}$$
to recommend:
$$\mathbf{THE\ SAFEST\ ACHIEVABLE\ CARE\ ACTION}$$

### 5.2 Action Vocabulary
The engine evaluates and proposes candidate actions strictly within a bounded clinical taxonomy:

| Action Code | Clinical Meaning | Trigger Conditions |
| :--- | :--- | :--- |
| `ASK` | Elicit high-value missing information | High uncertainty ($\mathcal{U}_t > 0.40$), critical protocol parameter absent. |
| `VERIFY` | Resolve contradictory findings | Discrepancy detected (e.g., patient reports normal breathing but SpO2 = 84%). |
| `CONTINUE` | Maintain current monitoring/care | Patient stable, low risk, routine care pathway confirmed feasible on-site. |
| `OBSERVE` | Close surveillance & serial vitals | Moderate risk or borderline trajectory; repeat vitals scheduled within 30 min. |
| `ESCALATE` | Immediate bedside clinician intervention | High risk ($R_t \ge 0.70$) or rapid worsening trajectory ($\Delta R > +0.15/\text{hr}$). |
| `REFER` | Transfer to capable network facility | Infeasible care at current facility ($\text{Feasibility} = \text{INFEASIBLE}$) + urgent clinical need. |

### 5.3 Human-in-the-Loop Clinical Gate
The Orchestration Engine never executes actions autonomously. Every candidate action requires review and one-click authorization by a licensed healthcare professional. When a clinician disagrees, they submit an **Override with Rationale**, which updates the CareGraph and refines future decision weighting.
