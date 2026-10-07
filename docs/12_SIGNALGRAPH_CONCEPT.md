# CLINOVA AI — SIGNALGRAPH Concept & System-Level Telemetry

> **Document ID:** `DOC-12`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. What is SIGNALGRAPH?

> **Core Definition:** SIGNALGRAPH is the macro-level operational and epidemiological intelligence engine of CLINOVA AI.
>
> While CAREGRAPH monitors individual patients and FACILITYGRAPH monitors individual health centers, SIGNALGRAPH aggregates privacy-preserving, de-identified telemetry from across the entire network of clinics, PHCs, and hospitals to answer:
> $$\mathbf{WHAT\ IS\ HAPPENING\ ACROSS\ THE\ CONNECTED\ HEALTHCARE\ ENVIRONMENT?}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SIGNALGRAPH ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ PRIVACY-PRESERVING TELEMETRY INGESTION ]                                │
│   • De-Identified Syndromic Encodings (Fever + Rash, Respiratory Distress)  │
│   • Facility Queue Wait Times & Throughput Rates                            │
│   • Bed Occupancy & Resource Depletion Velocity                             │
│   • Inter-Facility Referral Volumes & Dispatch Vectors                      │
│   • Antibiotic & Point-of-Care Diagnostic Consumption Rates                 │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│   [ DYNAMIC TELEMETRY SYNTHESIS ]                                           │
│   Statistical Anomaly Detection + Clustering + Demand Forecasting           │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│   [ NETWORK-LEVEL SYSTEM SIGNALS ]                                          │
│   ├── 1. EPIDEMIOLOGICAL SURGE SIGNALS (Syndromic Outbreak Detection)       │
│   ├── 2. OPERATIONAL BOTTLENECK SIGNALS (Departmental Queue Exhaustion)     │
│   ├── 3. REFERRAL PRESSURE SIGNALS (Logjams & Destination Overload)         │
│   ├── 4. RESOURCE DEPLETION SIGNALS (Critical Supply Stock-outs)            │
│   └── 5. QUALITY & DISPARITY SIGNALS (Triage Override & Outcome Variances)  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Derivation Mandate (No Hardcoded Fake Analytics)

> **Architectural Law:** SIGNALGRAPH signals must NEVER be hardcoded fake dashboard numbers or static mock JSON.
>
> All signals must dynamically aggregate and compute from real application events generated during user sessions and test suites:
> - Ingested synthetic Master Cases
> - Recorded clinical encounters and vital sign entries
> - Actual queue wait durations in database tables
> - Logged inter-facility referral transfers
> - Logged medication dispenses and bed status updates

---

## 3. Five Core Signal Archetypes

### 3.1 Syndromic Outbreak & Epidemiological Cluster Signals
- **Mechanism:** Monitors spatial and temporal density of clinical syndromes (e.g., *Acute Febrile Illness + Thrombocytopenia*, *Acute Watery Diarrhea*, *Severe Acute Respiratory Infection [SARI]*).
- **Statistical Detector:** Moving-average z-score detection over a 7-day rolling window:
  $$z = \frac{C_{\text{today}} - \mu_{7\text{d}}}{\sigma_{7\text{d}}}$$
  If $z > 2.58$ ($p < 0.01$), the system flags a **Syndromic Cluster Alert** indicating a probable regional outbreak (e.g., Dengue, Cholera, Influenza).

### 3.2 Departmental Bottleneck & Queue Congestion Signals
- **Mechanism:** Computes the ratio of arrival rate $\lambda$ to service rate $\mu$ in outpatient and emergency triage queues ($M/M/c$ queuing model telemetry).
- **Signal Output:** Flags facilities operating in saturation regimes ($\rho = \lambda / (c \cdot \mu) \ge 0.90$), notifying administrators before waiting rooms experience clinical decompensation events.

### 3.3 Referral Pressure & Logjam Signals
- **Mechanism:** Tracks inter-facility transfer vectors ($A \longrightarrow B$).
- **Signal Output:** Identifies secondary hospitals dispatching $> 60\%$ of acute cases to a single overburdened tertiary hospital, revealing localized diagnostic deficits (e.g., offline CT scanner in District Sub-Hospital causing tertiary emergency paralysis).

### 3.4 Resource Depletion & Stock-Out Velocity
- **Mechanism:** Monitors inventory consumption rates against remaining stock for critical life-saving consumables (e.g., snake antivenom, O-negative blood units, pediatric IV cannulae, oxygen manifold pressure).
- **Signal Output:** Predicts "Days to Exhaustion" and prompts re-stocking or re-routing before zero-stock is reached.

### 3.5 Clinician Override & Calibration Signals
- **Mechanism:** Aggregates rate at which clinicians modify or reject AI-inferred triage bands across clinical syndromes.
- **Signal Output:** Feeds back into system calibration: if clinicians consistently downgrade an AI-suggested "Urgent" flag for a specific symptom combination, the model's calibration error is flagged for the researcher benchmark suite.

---

## 4. UI Representation of SIGNALGRAPH

The SIGNALGRAPH dashboard provides public health officers and hospital administrators with high-density, actionable operational intelligence:
1. **Network Status Ticker:** Displays real-time counts of active encounters, network bed utilization, and queue pressure across connected centers.
2. **Syndromic Cluster Heatmap:** Interactive Leaflet map visualizing geographic clusters of infectious syndromes with bubble radii proportional to case volume and color indicating surge velocity.
3. **Department Throughput Swimlanes:** Visualizes average wait-to-doctor times across OPD, Emergency, and Pediatric departments with congestion threshold lines.
4. **Referral Flow Sankey / Chord Diagram:** Visualizes inter-facility patient movements, identifying transfer bottlenecks and receiving hospital burdens.
5. **Emerging Anomaly Feed:** Feed of system-detected anomalies with explicit plain-language rationale and drill-down links to de-identified aggregate data.
