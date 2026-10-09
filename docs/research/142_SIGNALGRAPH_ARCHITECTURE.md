# CLINOVA AI — SIGNALGRAPH Local & Operational Telemetry Architecture

> **Document ID:** `RES-142`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Public Health Informatics & Operational Telemetry Engineering Group  

---

## 1. Architectural Boundary: Local Operational & Syndromic Intelligence

A frequent failure of healthcare IT is over-promising nationwide epidemiologic surveillance. **SIGNALGRAPH is strictly bounded to local, campus, and facility-level operational and syndromic aggregate telemetry.**

### What SIGNALGRAPH Is:
- A local early warning system detecting localized syndrome clusters (e.g., sudden surge of acute gastroenteritis in a residential campus, or hemorrhagic fever cases in an agricultural block).
- An operational bottleneck monitor tracking emergency room wait times, bed occupancy choke points, and staffing strain across a connected hospital cluster.
- A frontline decision context provider that alerts doctors: *"Note: 8 confirmed Dengue presentations recorded in this block over the last 48 hours."*

### What SIGNALGRAPH Is NOT:
- **NOT a National Surveillance Replacement:** It does not replace the Integrated Disease Surveillance Programme (IDSP) or Integrated Health Information Platform (IHIP).
- **NOT an Individual Patient Tracker:** It operates exclusively on de-identified, k-anonymized aggregate event counts.

---

## 2. End-to-End SIGNALGRAPH Telemetry Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SIGNALGRAPH TELEMETRY PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: INDIVIDUAL CLINICAL EVENTS ]                                     │
│  ├── Master Case arrival, presenting complaint, and primary syndrome tag   │
│  └── Example: Case #1042 -> Syndrome: "ACUTE_FEBRILE_ILLNESS_THROMBOCYTOPENIA"│
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 2: IN-FLIGHT DE-IDENTIFICATION & PRIVACY SCRUBBING ]                │
│  ├── Strip all 18 HIPAA / DPDP identifiers: Name, Phone, ABHA, Address      │
│  ├── Generalize geographic location to District Block / Pincode prefix       │
│  └── Discard direct patient links; produce anonymous telemetry payload:     │
│      `{syndrome: "AFI_THROMBO", age_bracket: "20-29", facility: "FAC-01"}`  │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 3: TIME-WINDOWED AGGREGATION ENGINE ]                               │
│  ├── Rolling temporal buckets: 6-hour, 24-hour, and 7-day windows           │
│  └── Grouped counts stored in `signal_events` and aggregate cache           │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 4: SIGNAL CALCULATION & ANOMALY DETECTION ]                         │
│  ├── Computes z-score against historical 30-day baseline moving average:    │
│  │   Z = (Count_current - Mean_baseline) / StdDev_baseline                  │
│  └── Threshold Check: If Z >= 2.5 => CLUSTER_ALERT Triggered                 │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 5: DUAL OPERATIONAL DISTRIBUTION ]                                  │
│  ├── Channel A: Operational Dashboard (Facility bottleneck alerts)          │
│  └── Channel B: Frontline Clinical Context Badge on Doctor Workbench        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Privacy & Zero-PHI Leakage Invariants

To guarantee absolute compliance with the Digital Personal Data Protection (DPDP) Act 2023:

$$\mathbf{Inv\ SG\text{-}1} \quad (\text{Zero Direct Identifiers}): \quad \forall e \in \text{signal\_events}, \quad e.\text{payload} \cap \text{PHI\_FIELDS} = \emptyset$$

$$\mathbf{Inv\ SG\text{-}2} \quad (\text{k-Anonymity Gating}): \quad \text{Count}(\text{Cluster}) < 3 \implies \text{Suppressed from public telemetry views}$$

- **No Reverse Deanonymization:** Aggregated signal records contain zero foreign keys back to `cases.id` or `patients.id`. Once a signal event is emitted to the telemetry buffer, the link to the patient identity is permanently severed.
- **Differential Privacy Jitter:** For public-facing camp reports, small random Laplacian noise ($\epsilon = 0.5$) is added to count aggregates to prevent small-cell re-identification.

---

## 4. Integration with Frontline Care: The Contextual Tripwire

Rather than keeping epidemiologic data locked in administrative reports, SIGNALGRAPH feeds operational intelligence directly into the **Doctor Reviewer Workbench** and **Nurse Triage Workstation**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             DOCTOR WORKBENCH — ACTIVE EPIDEMIOLOGIC CONTEXT                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚠️ LOCAL SURGE DETECTED (Koraput Block B):                                 │
│  14 cases of Acute Febrile Illness with Petechial Rash recorded in the      │
│  last 36 hours (Z = +3.1, Elevated above baseline).                         │
│                                                                             │
│  CLINICAL ACTION TRIPWIRE:                                                  │
│  Consider early Platelet count & Dengue NS1 / IgM rapid testing for any     │
│  patient presenting with fever > 38.5°C and severe myalgia.                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Operational Choke Point Alerts
When emergency department wait times or bed occupancies exceed safety thresholds:
- `ED_CONGESTION_LEVEL_3`: Average wait time for Moderate cases exceeds 60 minutes.
- `ICU_BED_EXHAUSTION`: Regional ICU capacity drops below 10%.
- The Orchestration Engine uses these signals to automatically adjust transfer feasibility, diverting incoming ambulance referrals to alternative regional hospitals.
