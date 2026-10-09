# CLINOVA AI — Closed-Loop Outcome Architecture & Feedback Specification

> **Document ID:** `RES-71`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Philosophy: The Reality-Grounding Principle

In traditional healthcare IT and clinical decision support systems, the software workflow abruptly terminates when a triage code is printed or a doctor clicks "Sign Order". This creates a fatal blind spot: **the system never knows whether its advice was clinically sound, whether its risk predictions were accurate, or whether the patient survived.**

CLINOVA AI establishes the **Closed-Loop Outcome Architecture**, founded on the **Reality-Grounding Principle**:

$$\begin{aligned}
\mathbf{PLANNED\ ADVICE} &\neq \mathbf{ACTUAL\ CLINICIAN\ DECISION} \\
\mathbf{ACTUAL\ CLINICIAN\ DECISION} &\neq \mathbf{ACTUAL\ CARE\ ACTION} \\
\mathbf{ACTUAL\ CARE\ ACTION} &\neq \mathbf{REAL-WORLD\ CLINICAL\ OUTCOME}
\end{aligned}$$

The platform never assumes that an algorithmic recommendation was accepted, nor does it assume that a prescribed clinical action was successfully completed. It explicitly measures the delta across each link of the chain of care.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLOSED-LOOP OUTCOME CONTINUUM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1 ] AI ADVISORY RECOMMENDATION (Planned Guidance)                   │
│       │                                                                     │
│       ▼                                                                     │
│  [ STEP 2 ] ACTUAL CLINICIAN DECISION (Adoption Tracking)                   │
│       │     • ACCEPTED / MODIFIED / OVERRIDDEN / REJECTED                   │
│       ▼                                                                     │
│  [ STEP 3 ] ACTUAL CARE ACTION EXECUTION (Fulfillment Tracking)             │
│       │     • Dispatched / Delayed / Interrupted / NOT_COMPLETED            │
│       ▼                                                                     │
│  [ STEP 4 ] CLINICAL CONTINUATION & MONITORING                              │
│       │     • Home Recovery / Inpatient Stay / In-Transit Telemetry         │
│       ▼                                                                     │
│  [ STEP 5 ] REAL-WORLD CLINICAL ENDPOINT RECORDING                          │
│       │     • Full Recovery / Stabilized / Complication / Adverse Event     │
│       ▼                                                                     │
│  [ STEP 6 ] TWO-TIER GRAPH FEEDBACK PROPAGATION                             │
│       ├── Tier 1: CAREGRAPH Individual Longitudinal Delta                   │
│       └── Tier 2: SIGNALGRAPH Regional Epidemiological & Quality Aggregation│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decoupling Planned vs Actual vs Outcome

To achieve mathematical and clinical defensibility, the platform models three discrete operational vectors for every clinical decision point:

### Vector 1: $\mathbf{A}_{\text{planned}}$ (The Advisory Guidance)
- Synthesized by the Orchestration Engine based on initial multimodal evidence, $\text{CAREGRAPH}$ risk, and $\text{FACILITYGRAPH}$ feasibility.
- *Example:* `SUGGEST_WARD_ADMISSION` (Pneumonia with Moderate Hypoxia).

### Vector 2: $\mathbf{D}_{\text{clinician}}$ (The Actual Clinician Decision)
- The legally binding choice executed by the Registered Medical Practitioner.
- Tracked via one of five explicit adherence states:
  1. `ACCEPTED`: Clinician adopts system advice without modification.
  2. `MODIFIED`: Clinician adopts general pathway but alters specific dosage, ward tier, or follow-up duration.
  3. `OVERRIDDEN`: Clinician explicitly chooses an alternative pathway (e.g., system suggested Routine Home Care, doctor orders Ward Admission due to subtle clinical signs).
  4. `REJECTED`: Clinician dismisses recommendation as clinically inappropriate, logging a required reason.
  5. `NOT_COMPLETED`: Clinician initiated disposition, but encounter was aborted (patient walked out AMA before sign-off).

### Vector 3: $\mathbf{C}_{\text{actual}}$ (The Actual Care Action Executed)
- What physically occurs in the hospital or community:
  - Did the pharmacy dispense the medication?
  - Did the ward nurse admit the patient into Bed M-14?
  - Did the ambulance arrive and transport the patient to the tertiary hospital?
  - Was the action delayed, cancelled, or completed?

### Vector 4: $\mathbf{O}_{\text{clinical}}$ (The Real-World Clinical Outcome)
- The biological and health status of the patient at the conclusion of the episode.

---

## 3. Real Clinical Outcome Taxonomy

CLINOVA classifies clinical endpoints using a standardized, 6-tier outcome taxonomy:

| Outcome State | Operational Definition | Clinical Example | Algorithmic Impact |
| :--- | :--- | :--- | :--- |
| `FULL_RECOVERY` | Complete resolution of acute pathology; return to baseline health. | Acute viral gastroenteritis resolved within 48h; patient eating normally. | Validates baseline triage specificity; calibrates low-risk thresholds. |
| `STABILIZED` | Chronic flare or acute illness brought under safe clinical control. | Hypertensive urgency normalized with oral amlodipine; BP stable at 130/80. | Confirms routine outpatient management pathway. |
| `COMPLICATION_MANAGED`| Secondary clinical complication arose during care, but was safely managed on-site. | Patient admitted with dengue developed epistaxis; managed with nasal packing. | Tests early warning trajectory sensitivity; refines HDU triggers. |
| `REFERRED_HIGHER` | Patient successfully stabilized and transferred to tertiary center without mortality. | Acute appendicitis referred from PHC to District Hospital; surgery completed. | Validates FACILITYGRAPH referral matching accuracy. |
| `CRITICAL_TRANSFER` | Emergency evacuation required due to unexpected, rapid in-hospital deterioration. | Patient admitted to general ward suffered sudden massive pulmonary embolism. | Triggers high-priority safety audit of initial ward admission criteria. |
| `ADVERSE_EVENT` | Avoidable patient deterioration, delayed transfer harm, or unexpected mortality. | Patient discharged home returned 8 hours later in septic shock. | **CRITICAL SAFETY AUDIT:** Triggers Root-Cause Analysis (RCA) and algorithmic review. |

---

## 4. Two-Tier Graph Feedback Propagation

When an outcome is logged, it propagates across two distinct intelligence tiers:

```
                                [ OUTCOME LOGGED ]
                         (Recorded by Doctor / Nurse)
                                      │
               ┌──────────────────────┴──────────────────────┐
               │                                             │
               ▼                                             ▼
     [ TIER 1: CAREGRAPH ]                        [ TIER 2: SIGNALGRAPH ]
   (Individual Patient Level)                     (System / Regional Level)
               │                                             │
  • Bounds outcome to case_id                   • Aggregates syndromic telemetry
  • Calculates Concordance Delta                • Tracks referral acceptance rate
  • Resolves pending hypotheses                 • Computes triage calibration
  • Enriches longitudinal record                • Emits public health cluster alerts
```

### Tier 1: CAREGRAPH Longitudinal Delta
- **Encounter Binding:** The verified outcome is appended to `MasterCase.outcome_record`.
- **Hypothesis Resolution:** Pending clinical hypotheses are resolved (e.g., hypothesis `Suspected Enteric Fever` resolved as `Confirmed Salmonella Typhi on Blood Culture`).
- **Longitudinal Enrichment:** The patient's longitudinal record records individual pharmacological responses (e.g., *"Patient responded safely to oral Cefixime without allergic reaction"*), informing future visits.
- **Concordance Delta Score:**
  $$\text{Delta}_{\text{concordance}} = 1.0 - \left| \text{Risk}_{\text{initial}} - \text{Severity}_{\text{actual}} \right|$$
  Measures algorithmic calibration.

### Tier 2: SIGNALGRAPH Macro System Intelligence
- **Referral Corridor Efficacy:** Tracks which receiving tertiary hospitals deliver the fastest transfer acceptance and lowest mortality, dynamically updating $\text{FACILITYGRAPH}$ transfer weights.
- **Triage Safety Monitoring:** Tracks false-negative rates (patients classified as low-risk who experienced `ADVERSE_EVENT` or `CRITICAL_TRANSFER`). If false-negative rate exceeds $0.5\%$, the system flags an urgent calibration review for hospital leadership.
- **Syndromic Outbreak Tracking:** As dozens of patients in a geographic cluster present with similar symptoms and recover, $\text{SIGNALGRAPH}$ monitors the epidemic curve, providing automated surveillance of dengue, cholera, or viral surges to district health officers (IDSP integration).

---

## 5. Closure & Archival Invariant

Following outcome recording and graph feedback propagation:
- The Master Case state transitions to `STATE_CLOSED`.
- The case dossier is cryptographically hashed (SHA-256) and sealed.
- All subsequent access transitions to strictly read-only mode.
- Future patient presentations generate a **NEW Master Case** that links back to the patient's permanent longitudinal ID, preserving unbroken continuity of care.
