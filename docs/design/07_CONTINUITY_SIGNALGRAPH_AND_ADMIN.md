# CLINOVA AI — Design Specifications: Cluster 7 (Continuity, SIGNALGRAPH & System Governance)

> **File:** `docs/design/07_CONTINUITY_SIGNALGRAPH_AND_ADMIN.md`  
> **Screens Covered:** Screens 37 through 40  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 37: Longitudinal Follow-up & Real Outcome Tracker

### 1. Specification
- **Route:** `/case/:id/outcome`
- **Purpose:** Record the real-world clinical endpoint of the patient encounter (Full Recovery, Stabilized, Referred, Adverse Event), closing the continuous care intelligence loop and feeding system evaluation.
- **Actor:** Medical Officer, Ward Nurse, Clinical Quality Auditor.
- **Entry Condition:** Patient completes inpatient stay, outpatient follow-up, or inter-facility transfer.
- **Inputs:** Final Clinical Endpoint dropdown (`FULL_RECOVERY`, `STABILIZED`, `REFERRED_HIGHER`, `COMPLICATION_MANAGED`, `CRITICAL_TRANSFER`, `ADVERSE_EVENT`), algorithm agreement radio (`AGREED`, `PARTIALLY_AGREED`, `OVERRIDDEN`), clinical outcome commentary text.
- **Outputs:** Summary of original triage risk vs. final clinical endpoint, calibration delta badge.
- **Actions:** "Log Real Outcome & Close Encounter", "Flag for Quality Audit", "Return to Case".
- **Navigation:** Closes active encounter; updates Master Case status to `CLOSED_RESOLVED`.
- **Graph Linkage:** Updates CAREGRAPH to `RESOLVED` and transmits de-identified telemetry to SIGNALGRAPH.

### 2. Wireframe (Screen 37)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Clinical Outcome Feedback Loop   [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RECORD REAL-WORLD CLINICAL ENDPOINT & CALIBRATION DATA                    │
│   Patient: 45M | Initial Presentation: Severe Febrile Illness with Shock    │
│   Initial AI Advisory: Resuscitate & HDU Admission (Agreed by Dr. Mohapatra)│
│                                                                             │
│   FINAL CLINICAL ENDPOINT:                                                  │
│   (X) FULL RECOVERY — Discharge home after 4 days HDU fluid management      │
│   ( ) STABILIZED — Transferred to general ward                              │
│   ( ) COMPLICATION MANAGED — Platelets normalized post-transfusion          │
│   ( ) ADVERSE EVENT — Unplanned ICU escalation / Decompensation             │
│                                                                             │
│   ALGORITHM AGREEMENT EVALUATION:                                           │
│   Did the initial Orchestration pathway match actual clinical needs?        │
│   (X) FULLY CONCORDANT   ( ) PARTIALLY CONCORDANT   ( ) DISCORDANT / WRONG   │
│                                                                             │
│   Clinical Outcome Notes:                                                   │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ Patient responded excellently to isotonic crystalloid resuscitation.  │ │
│   │ Platelets recovered from 42,000 to 118,000/μL on Day 4. No hemorrhage. │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   [ CLOSE & COMMIT TO CONTINUITY LEDGER [✓] ]                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 38: SIGNALGRAPH Regional Surveillance & Epidemic Heatmap

### 1. Specification
- **Route:** `/signals/surveillance`
- **Purpose:** Macro-level epidemiological intelligence dashboard aggregating privacy-preserving, de-identified clinical telemetry to answer *"What is happening across the connected healthcare environment?"*.
- **Actor:** Public Health Officer, District Epidemiologist, System Administrator.
- **Entry Condition:** Authenticated administrative or public health session.
- **Inputs:** Regional district filter (e.g., Khordha, Cuttack, Puri), syndromic cluster selector (Dengue, Diarrheal, Acute Respiratory).
- **Outputs:** Interactive Leaflet syndromic cluster map with bubble radii proportional to case velocity; rolling 7-day z-score epidemic surge alerts; network case volume trendlines.
- **Actions:** "Export Surveillance Report", "Filter by Syndrome", "Inspect Anomaly Signal".
- **Navigation:** Links to Screen 39.
- **Graph Linkage:** Direct visual projection of **SIGNALGRAPH** (C07).

### 2. Wireframe (Screen 38)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       SIGNALGRAPH Public Health Surveillance              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   REGIONAL SYNDROMIC SURVEILLANCE & OUTBREAK DETECTION                      │
│   Aggregating 1,420 Active Synthetic Encounters across 8 Regional Centers   │
│                                                                             │
│   🚨 ACTIVE EPIDEMIC SURGE ALERT (Z-SCORE: +3.14 — STATISTICALLY SIGNIFICANT)│
│   Syndrome: Acute Febrile Illness with Severe Thrombocytopenia              │
│   Cluster Epicenter: Bhubaneswar Sub-District (42 Cases in past 48 hours)   │
│                                                                             │
│   LEAFLET / OPENSTREETMAP REGIONAL SURVEILLANCE MAP:                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ [MAP: Bhubaneswar (🔴 Cluster 42 Cases) ──> Cuttack (🟠 Cluster 18) ]  │ │
│   │ OpenStreetMap Vector Layer | Privacy-Preserving De-Identified Telemetry│ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   SYNDROMIC BREAKDOWN:                                                      │
│   • Acute Febrile Illness (Dengue Suspect): 64% [Surging ↗]                 │
│   • Acute Watery Diarrheal Illness:        18% [Baseline →]                 │
│   • Severe Acute Respiratory Illness:       12% [Baseline →]                 │
│                                                                             │
│   [ EXPORT EPIDEMIOLOGICAL SITREP ]            [ VIEW FACILITY BOTTLENECKS] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 39: Facility & System Capacity Operational Analytics

### 1. Specification
- **Route:** `/analytics/capacity`
- **Purpose:** Network operational intelligence monitoring departmental congestion, queue wait times, bed occupancy velocity, and referral logjams across connected facilities.
- **Actor:** Hospital Superintendent, District Health Administrator, Referral Lead.
- **Entry Condition:** Authenticated administrator session.
- **Inputs:** Facility selector, time horizon toggle (Today, 7 Days, 30 Days).
- **Outputs:** Queue wait-to-doctor times ($M/M/c$ queuing metrics), bed occupancy bar charts, referral flow vectors showing bottleneck destinations.
- **Actions:** "Reallocate Triage Staff", "Trigger Referral Overflow Protocol", "Export Operational Audit".
- **Navigation:** Links to Screens 24, 38.
- **Graph Linkage:** Synthesizes `FACILITYGRAPH` telemetry across facilities into `SIGNALGRAPH`.

### 2. Wireframe (Screen 39)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Facility Operational Analytics   [ DISTRICT CONSOLE]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   NETWORK OPERATIONAL CONGESTION & CAPACITY TELEMETRY                       │
│                                                                             │
│   FACILITY NAME         OPD WAIT TIME   EMG BED OCCUPANCY   REFERRAL VOLUME │
│   ───────────────────── ─────────────── ─────────────────── ────────────────│
│   Capital District Hosp 58 Mins ⚠️      100% (4/4 FULL) 🚨  18 Dispatched ↗ │
│   SCB Medical College   84 Mins ⚠️       94% (32/34)    ⚠️  42 Received   🚨│
│   Jatni Community HC    18 Mins 🟢       40% (2/5)      🟢   4 Dispatched → │
│                                                                             │
│   CRITICAL BOTTLENECK SIGNAL:                                               │
│   Capital District Hospital has reached 100% emergency capacity and is      │
│   routing 80% of transfers to SCB Medical College, creating an intake logjam│
│                                                                             │
│   RECOMMENDED INTERVENTION:                                                 │
│   Activate secondary referral pathway diverting acute transfers to AIIMS.   │
│                                                                             │
│   [ RE-ROUTE REFERRAL OVERFLOW ]               [ EXPORT OPERATIONAL REPORT ]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 40: System Audit, Security & Safety Compliance Inspector

### 1. Specification
- **Route:** `/admin/audit-logs`
- **Purpose:** Cryptographically linked, tamper-evident audit ledger displaying system security events, clinical overrides, PII sanitization logs, and access histories for medicolegal compliance.
- **Actor:** System Administrator, Chief Compliance Officer, Clinical Auditor.
- **Entry Condition:** Authenticated system administrator session.
- **Inputs:** Filter by actor role, action type, date range, or synthetic case ID.
- **Outputs:** Paginated, cryptographically verifiable audit log entries with HMAC signatures.
- **Actions:** "Verify Cryptographic Hash Chain", "Export Audit Ledger (CSV/JSON)", "Inspect Modification Diff".
- **Navigation:** Links to Screen 03 (Logout) or administrative settings.
- **States:**
  - *Normal:* Clean tabular ledger showing timestamps, actor IDs, actions, and previous/new values.
  - *Integrity Confirmed:* Green shield icon: "Cryptographic Hash Chain Verified (Zero Tampering Detected)."
- **Graph Linkage:** Direct view of immutable `AuditEvent` ledger.

### 2. Wireframe (Screen 40)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Immutable System Audit Ledger    [ SYSTEM ADMIN ]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MEDICOLEGAL AUDIT LOG & COMPLIANCE INSPECTOR (DPDP / DISHA / HIPAA)       │
│   Ledger Integrity: 🛡️ CRYPTOGRAPHIC HASH CHAIN VERIFIED (TAMPER-EVIDENT)   │
│                                                                             │
│   TIMESTAMP (UTC)      ACTOR ID      ACTION TYPE        CASE ID   DETAILS   │
│   ──────────────────── ───────────── ────────────────── ───────── ──────────│
│   2026-10-08 01:22:45  DOC-OD-4402   CLINICAL_OVERRIDE  PT-94021  BP 110->88│
│   2026-10-08 01:20:12  NURSE-OD-102  VITALS_VERIFIED    PT-94021  HR 124 bpm│
│   2026-10-08 01:18:04  SYSTEM_ENGINE PII_SCRUBBED       PT-94021  Aadhaar[✓]│
│   2026-10-08 01:15:30  SYS-AUTH      LOGIN_SUCCESS      DOC-OD-4402 Capital │
│                                                                             │
│   INSPECTION DIFF (DOC-OD-4402 ON PT-94021):                                │
│   • Field: Systolic Blood Pressure                                          │
│   • Original Extracted: 110 mmHg                                            │
│   • Doctor Modified: 88 mmHg                                                │
│   • Justification: "Repeat manual auscultation confirmed severe hypotension"│
│   • HMAC-SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b78│
│                                                                             │
│   [ VERIFY INTEGRITY HASH ]                     [ EXPORT COMPLIANCE ARCHIVE]│
└─────────────────────────────────────────────────────────────────────────────┘
```
