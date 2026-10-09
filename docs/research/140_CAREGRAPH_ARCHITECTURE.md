# CLINOVA AI — CAREGRAPH Dynamic Patient State Architecture

> **Document ID:** `RES-140`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Physiological Dynamics Engineering Group  

---

## 1. Concept & Architectural Categorization: No Graph Database Required

In conventional clinical systems, patient records are either static snapshots (a single set of vitals taken at triage) or unstructured chronological text notes.

**CAREGRAPH** is CLINOVA AI's continuous product intelligence layer that models:
- Dynamic physiological deviation from baseline
- Serial trajectory slope ($\Delta \text{Vitals} / \Delta t$)
- Epistemic data completeness and uncertainty ($U_t$)
- Clinical risk bands and transitions over time

### Architectural Classification Decision
**CAREGRAPH is architected as an in-memory Computed Projection & Domain Service over Relational State.**

- **Explicit Rejection of Graph Databases:** CAREGRAPH does **NOT** require Neo4j, AWS Neptune, or any specialized graph database engine.
- **Rationale:** The "graph" in CAREGRAPH refers to the *conceptual multi-dimensional state space and semantic care journey* of the patient, not a network topology requiring Cypher graph queries. Introducing Neo4j into a rural Primary Health Centre running on a fanless Mini-PC would introduce fatal operational overhead, massive RAM consumption ($> 2\text{GB}$), and dual-database distributed transaction failures.
- **Simplest Safe Architecture:** CAREGRAPH is computed on-demand as a deterministic projection from existing relational tables (`vital_readings`, `clinical_observations`, `missing_information_items`, `evidence_conflicts`) and cached as a lightweight state snapshot in `caregraph_states`.

---

## 2. End-to-End CAREGRAPH Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAREGRAPH DATA PROJECTION PIPELINE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: INPUT EVIDENCE ]                                                 │
│  ├── Multimodal observations (Vitals, Lab tests, Reported symptoms)         │
│  └── Epistemic states (KNOWN, UNKNOWN, CONFLICTING, UNRELIABLE)             │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 2: CHRONOLOGICAL OBSERVATION VECTOR ]                               │
│  ├── Serial time-series vitals sorted by physical Event Time                │
│  └── Discrete laboratory measurements normalized to LOINC                   │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 3: PHYSIOLOGICAL DEVIATION & RISK SCORING ]                         │
│  ├── Deterministic NEWS2 Composite Early Warning Score (0 to 20)            │
│  ├── Shock Index (SI = HR / SBP; Normal: 0.5–0.7; Shock: > 0.9)             │
│  └── Physiological Risk Score: R_t in [0.0, 1.0]                            │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 4: LONGITUDINAL TRAJECTORY CALCULATION ]                            │
│  ├── First-order derivative of composite acuity: slope = Delta R / Delta t   │
│  └── Directional classification: IMPROVING, STABLE, DETERIORATING, RAPID     │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 5: EPISTEMIC UNCERTAINTY QUANTIFICATION ]                           │
│  ├── Normalized gap score: U_t in [0.0, 1.0]                                │
│  └── Evaluated independently of risk (Uncertainty != Physiological Risk)    │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 6: STATE TRANSITION & CLINICAL ACTION ADVISORY ]                    │
│  ├── Informs Case State Machine (e.g. S10 -> S11 -> S22 Emergency code)    │
│  └── Supplies contextual vector to Multi-Graph Orchestration Engine         │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 7: OUTCOME CONTINUITY LOOP ]                                        │
│  └── Feeds serial trajectory changes back to calibrate triage accuracy      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical Formulation of CAREGRAPH Projections

### 3.1 Composite Physiological Risk ($R_t$)
Let $\mathbf{V}_t = (\text{HR}_t, \text{SBP}_t, \text{RR}_t, \text{SpO2}_t, \text{Temp}_t, \text{AVPU}_t)$ be the latest verified vital reading at time $t$. The composite risk score $R_t \in [0.0, 1.0]$ is computed deterministically:

$$R_t = \min\left(1.0, \; \frac{\text{NEWS2}(\mathbf{V}_t)}{14.0} + 0.3 \cdot \mathbb{I}(\text{SI}_t > 0.9) + 0.2 \cdot \mathbb{I}(\text{RedFlag})\right)$$

Where:
- $\text{NEWS2}(\mathbf{V}_t)$ is the Royal College of Physicians composite early warning score (capped at 14 for normalization).
- $\text{SI}_t = \text{HR}_t / \text{SBP}_t$ is the Shock Index.
- $\mathbb{I}(\cdot)$ is the binary indicator function.

### 3.2 Longitudinal Trajectory Slope ($\Delta R / \Delta t$)
When multiple serial readings exist across time window $\Delta t = t_k - t_{k-1}$ (in hours):

$$\text{Slope} = \frac{R_{t_k} - R_{t_{k-1}}}{\max(0.1, \; t_k - t_{k-1})} \quad (\text{points / hour})$$

- $\text{Slope} > +0.25$: `RAPIDLY_DETERIORATING` (Immediate clinical emergency tripwire)
- $+0.05 < \text{Slope} \le +0.25$: `DETERIORATING` (Queue priority escalation)
- $-0.05 \le \text{Slope} \le +0.05$: `STABLE`
- $\text{Slope} < -0.05$: `IMPROVING`

### 3.3 Epistemic Uncertainty ($U_t$)
Uncertainty reflects missing information and data conflicts, **strictly decoupled from risk**:

$$U_t = \sum_{i=1}^{M} w_i \cdot g_i \in [0.0, 1.0]$$

Where:
- Missing Tier 1 critical vitals ($w=0.30$)
- Active unresolved clinical conflicts ($w=0.20$)
- Low-confidence OCR extractions ($w=0.10$)
- Low SNR vernacular audio transcriptions ($w=0.10$)
- Stale historical records ($w=0.08$)
- Unverified free text assertions ($w=0.08$)
- Incomplete timeline qualifiers ($w=0.07$)
- Unavailable diagnostic tests ($w=0.07$)

---

## 4. Invalidation & Reactive Re-Computation Semantics

1. **Reactive Triggers:** CAREGRAPH projections are re-computed automatically whenever:
   - A new row is inserted into `vital_readings`.
   - An `evidence_records` item is modified, attested, or marked disputed.
   - An `evidence_conflicts` record is created or resolved by an RMP.
   - A `missing_information_items` entry is resolved via follow-up response.
2. **Sub-Millisecond Computation:** Because the projection logic consists of pure mathematical evaluations over 5–10 recent vital rows, execution takes $< 2\text{ms}$ in Python, allowing instantaneous re-computation during the database transaction.
3. **Historical Snapshots:** The updated state is saved into `caregraph_states` linked to `cases.id`, creating a complete longitudinal record of patient trajectory over time.
