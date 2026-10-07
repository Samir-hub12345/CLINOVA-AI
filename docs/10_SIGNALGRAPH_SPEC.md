# CLINOVA AI — SIGNALGRAPH Detailed Technical Specification

> **Document ID:** `DOC-10`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Architectural Role & Core Purpose

**SignalGraph** is the system-level operational and epidemiological telemetry engine of CLINOVA AI. It continuously aggregates privacy-preserving, synthetic signals produced by live patient intakes, CareGraph state transitions, and FacilityGraph capacity shifts.

SignalGraph answers the macro-level intelligence question:
$$\mathbf{What\ is\ happening\ across\ the\ connected\ healthcare\ environment?}$$

In public healthcare systems, administrative leadership is often blind to early-stage disease outbreaks and regional department gridlocks until emergency rooms are overwhelmed. SignalGraph closes this gap by transforming discrete, de-identified clinical events into actionable real-time telemetry.

---

## 2. Event Ingestion Pipeline & Privacy Boundary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SIGNALGRAPH TELEMETRY PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ Patient Encounter ] ──> Intake / CareGraph State Change                │
│                                      │                                      │
│                                      ▼                                      │
│                ┌───────────────────────────────────────────┐                │
│                │     PRIVACY & DE-IDENTIFICATION GATE      │                │
│                │  - Strips all synthetic names/IDs         │                │
│                │  - Generalizes Age -> 10-year bracket     │                │
│                │  - Retains: SyndromeTag, FacilityID, Time │                │
│                └─────────────────────┬─────────────────────┘                │
│                                      │                                      │
│                                      ▼                                      │
│                      [ Signal Event Bus (In-Memory) ]                       │
│                                      │                                      │
│          ┌───────────────────────────┼───────────────────────────┐          │
│          ▼                           ▼                           ▼          │
│   [ Syndromic Cluster ]      [ Facility Pressure ]     [ Referral Heatmap ] │
│     Detection Engine           Bottleneck Monitor        Routing Telemetry  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Strictly Dynamic: No Hardcoded Statistics
SignalGraph is **prohibited from displaying static, hardcoded numbers**. Every metric rendered on the dashboard derives directly from:
1. Actual synthetic patient cases created in the system during current and baseline execution.
2. Actual facility state objects and bed occupancy counters updated by user or scenario actions.
3. Actual referral transfers initiated in the clinical workflow.

---

## 3. Telemetry Signal Categories

### 3.1 Category 1: Syndromic Surges & Outbreak Clusters
- **Definition:** Statistical elevation of specific symptom combinations within a geographic catchment area over rolling time windows (e.g., 24h, 48h, 7 days).
- **Syndrome Taxonomies Tracked:**
  - `SYNDROME_ACUTE_RESPIRATORY`: Cough + Shortness of breath + Hypoxia / Fever.
  - `SYNDROME_HEMORRHAGIC_FEVER`: High fever + Thrombocytopenia / Petechiae / Bleeding (Dengue / Vector-borne).
  - `SYNDROME_ACUTE_GASTROENTERITIS`: Profuse diarrhea + Dehydration + Vomiting (Cholera / Water-borne).
  - `SYNDROME_ENCEPHALITIS_ALTERED_SENSORIUM`: Acute fever + Altered mental status + Seizures.
- **Cluster Detection Metric (Z-Score):**
  $$Z_{\text{syndrome}} = \frac{C_{\text{observed}} - \mu_{\text{baseline}}}{\sigma_{\text{baseline}}}$$
  - $Z \ge 2.5$: **Elevated Cluster Warning** (Yellow alert on network map).
  - $Z \ge 3.5$: **Outbreak Surge Alert** (Red emergency notification to Chief Medical Officer).

### 3.2 Category 2: Department Bottlenecks & Operational Congestion
- **ED Queue Pressure:** Ratio of active waiting patients to staffed resuscitation bays.
- **Triage Delay SLA Breach:** Percentage of triage cases waiting $> 45\text{ min}$ without clinician review.
- **ICU Bed Depletion:** Real-time warning when network-wide critical care occupancy exceeds $90\%$.

### 3.3 Category 3: Referral Network Pressures
- **Inter-Facility Transfer Vector Volume:** Density of referral arrows traveling between PHC/CHC nodes and Tertiary hospitals.
- **Destination Rejection / Delay Rate:** Frequency of `REFERRAL_FAILED` or `TRANSFER_PENDING` delays indicating receiving center saturation.

---

## 4. Synthetic vs Real-World Data Transparency

SignalGraph prominently displays a persistent clinical telemetry header:
$$\mathbf{[SYNTHETIC\ TELEMETRY\ MODE]}$$
All counts, geographic coordinates, and cluster alarms explicitly state:
*"Generated from synthetic and simulated clinical scenarios for institutional evaluation. Zero real-world PHI utilized."*

---

## 5. Downstream Feedback to Orchestration

SignalGraph does not operate in a vacuum. Its telemetry feeds directly back into the **Orchestration Engine**:
- When SignalGraph flags `Dengue Outbreak Cluster` in a region, CareGraph increases the diagnostic weight of serial platelet counts for febrile patients.
- When SignalGraph flags `District Hospital ED Saturation`, FacilityGraph automatically discounts District Hospital in referral suitability ranking, prioritizing alternative regional centers.
