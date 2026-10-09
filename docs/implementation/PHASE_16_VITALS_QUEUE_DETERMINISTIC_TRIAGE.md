# CLINOVA AI — Phase 16 Architecture & Implementation Record: Vitals, Queue & Deterministic Triage Foundation

**Document ID:** CLINOVA-DOC-PHASE16-VITALS-QUEUE-TRIAGE  
**Status:** IMPLEMENTED & VERIFIED  
**Phase:** 16 (Strictly Atomic Phase 16 Boundary — Zero Phase 17/18 Leakage)  
**Security Level:** Production-Hardened Clinical Advisory & Workflow Triage Architecture  
**Dependencies:** Phase 13 Core Persistence, Phase 14 Auth & RBAC Hardening, Phase 15 Intake & Consent  
**Target Environment:** Local-First SQLite & Production PostgreSQL  

---

## 1. Executive Summary

Phase 16 delivers a deterministic, patient-safe, and fully auditable **Vital Signs Capture, Clinical Worklist Queue, and Deterministic Triage Engine** for CLINOVA AI. It bridges initial patient intake (Phase 15) with clinical bedside prioritization, executing standardized physiological scoring and operational priority assignment entirely without generative AI or stochastic model inference.

### Core Architectural Principles & Invariants:
1. **Zero AI / LLM for Clinical Scoring:**
   All physiological scoring (NEWS2 RCP 2017, Shock Index) and red-flag evaluations are computed using purely deterministic mathematical rules and lookup tables. No language models or probabilistic inference mechanisms participate in triage risk scoring or priority classification.
2. **Epistemic Uncertainty Separated from Physiological Risk:**
   Missing vitals or incomplete intake information elevates epistemic uncertainty (`uncertainty_score` >= 0.60, `uncertainty_level = HIGH`), but explicitly does **not** force emergency escalation (`P1_CRITICAL`) without deterministic physiological red flags or critical clinical criteria. This preserves clinical trust and prevents false-alarm alert fatigue while transparently highlighting data gaps.
3. **Canonical Vital Signs Capture & Validation:**
   Vital sign measurements are validated against strict physiological ranges (e.g., SBP [40–300], DBP [20–200], HR [20–300], SpO2 [40–100%]), reject systolic <= diastolic anomalies, reject future timestamps, and validate AVPU scale values.
4. **Provenance & Verification Governance:**
   Vital signs recorded with provenance `PATIENT_REPORTED` or `DEVICE_DERIVED` are never automatically marked as verified (`is_verified = False`). Verification requires explicit clinical confirmation by licensed staff.
5. **Freshness & Recency Classification:**
   Observations are evaluated against real-time clinical freshness thresholds:
   - `AVAILABLE`: Observed <= 2 hours ago.
   - `STALE`: Observed between 2 and 6 hours ago (bedside repeat recommended).
   - `MISSING` / `EXPIRED`: Observed > 6 hours ago or never recorded.
6. **Dynamic Query-Time Queue Waiting Time:**
   Patient waiting times are calculated dynamically at query execution (`now - intake_timestamp`). Waiting time is never persisted as a database column using `NOW()` or static timestamps.
7. **Deterministic Queue Ordering & Starvation Mitigation:**
   Queue ordering is strictly deterministic:
   - Primary: Operational priority tier (`P1_CRITICAL` > `P2_URGENT` > `P3_MODERATE` > `P4_ROUTINE`).
   - Secondary: Starvation mitigation flag (cases waiting > 120 minutes with moderate acuity receive boosted priority within tier).
   - Tertiary: Physiological acuity score (`risk_score` descending).
   - Quaternary: Dynamic waiting time descending.
   - Tie-breaker: Lexicographical `case_id` ascending.
8. **Multi-Tenant Facility Scoping & Role-Based Access Control:**
   Staff queue endpoints (`/cases/queue`) are strictly isolated to the authenticated user's assigned facility (or all facilities for system admins). Patients are barred with HTTP 403 `AUTHORIZATION_ERROR`.
9. **Strict Phase Boundary:**
   Zero Phase 17 (Differential Diagnostics) or Phase 18 (Treatment Planning) implementation logic is introduced.

---

## 2. Architecture & Data Flow

```
[ Bedside Nurse / Clinician ]               [ Patient Self-Reporting ]
            │                                           │
            ├─► POST /cases/{id}/vitals                 └─► POST /intake/submit
            │   (CLINICAL_OBSERVATION)                      (PATIENT_REPORTED)
            ▼                                           │
┌───────────────────────────────────────────────────────┴───────────────────────┐
│ FastAPI Router: app/api/v1/endpoints/foundation.py                           │
│  ├─► Validate ranges, SBP > DBP, future timestamp rejection                   │
│  ├─► Enforce provenance verification rules (PATIENT_REPORTED != verified)     │
│  └─► Persist to vitals table & log audit_event                                │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ Deterministic Triage Engine: app/domain/triage/engine.py                      │
│  ├─► Evaluate Vital Freshness (AVAILABLE <= 2h, STALE <= 6h, MISSING > 6h)   │
│  ├─► Calculate NEWS2 (RCP 2017 standard, explicit missing-component tracking) │
│  ├─► Calculate Shock Index (HR / SBP, safe division)                          │
│  ├─► Evaluate Red-Flag Rules (8 deterministic clinical rules)                 │
│  ├─► Compute Physiological Risk Score & Epistemic Uncertainty Score          │
│  └─► Assign Operational Priority (P1_CRITICAL, P2_URGENT, P3_MOD, P4_ROUTINE) │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│ Snapshot Persistence                 │  │ Clinical Worklist Queue              │
│  POST /cases/{id}/triage/calculate   │  │  GET /cases/queue                    │
│  GET /cases/{id}/triage/snapshot     │  │  ├─ Filter by user's facility        │
│  - Appends to triage_snapshots table │  │  ├─ Dynamic wait time calculation    │
│  - Never overwrites historical state │  │  └─ Deterministic priority sorting   │
└──────────────────────────────────────┘  └──────────────────────────────────────┘
```

---

## 3. Clinical Scoring & Rules Specification

### 3.1 Royal College of Physicians NEWS2 (2017)
The National Early Warning Score 2 (NEWS2) is calculated according to the official RCP 2017 guidelines:

| Parameter | 3 Points | 2 Points | 1 Point | 0 Points | 1 Point | 2 Points | 3 Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Respiration Rate (bpm)** | <= 8 | — | 9–11 | 12–20 | — | 21–24 | >= 25 |
| **SpO2 Scale 1 (%)** | <= 91 | 92–93 | 94–95 | >= 96 | — | — | — |
| **Supplemental Oxygen** | — | Yes (2 pts) | — | No (0 pts) | — | — | — |
| **Systolic BP (mmHg)** | <= 90 | 91–100 | 101–110 | 111–219 | — | — | >= 220 |
| **Heart Rate (bpm)** | <= 40 | — | 41–50 | 51–90 | 91–110 | 111–130 | >= 131 |
| **Consciousness (AVPU)**| — | — | — | Alert (A) | — | — | V, P, or U (3 pts) |
| **Temperature (°C)** | <= 35.0 | — | 35.1–36.0 | 36.1–38.0 | 38.1–39.0 | >= 39.1 | — |

**Clinical Invariant on Incomplete Data:** Missing parameters are never silently defaulted to zero. They are reported in `missing_components` and `is_complete = False`. Clinical risk interpretation:
- Aggregate score >= 7 or any single parameter = 3: **HIGH** clinical risk.
- Aggregate score 5–6: **MEDIUM** clinical risk.
- Aggregate score 1–4: **LOW** clinical risk.
- Aggregate score 0: **NORMAL** risk.

### 3.2 Shock Index
- Formula: $\text{Shock Index} = \frac{\text{Heart Rate (bpm)}}{\text{Systolic Blood Pressure (mmHg)}}$
- Normal: 0.5 – 0.7
- Mild Shock: 0.7 – 0.9
- Moderate Shock: 0.9 – 1.1
- Severe Shock: > 1.1
- Handled with zero-division protection and explicit missing-input flagging.

### 3.3 Deterministic Red-Flag Rules Suite (Version 1.0)
Eight deterministic clinical rules evaluate life-threatening physiological instability:
1. `RF-HYPOXIA`: Severe Hypoxemia ($\text{SpO}_2 < 90\%$). Severity: `CRITICAL`.
2. `RF-SHOCK`: Hemodynamic Shock ($\text{Shock Index} \ge 1.0$ or $\text{SBP} < 80\text{ mmHg}$). Severity: `CRITICAL`.
3. `RF-UNRESPONSIVE`: Altered Consciousness ($\text{AVPU} \in \{\text{P}, \text{U}\}$ or $\text{GCS} \le 8$). Severity: `CRITICAL`.
4. `RF-EXTREME-RR`: Extreme Respiratory Rate ($\text{RR} < 8$ or $\text{RR} > 30\text{ bpm}$). Severity: `CRITICAL`.
5. `RF-EXTREME-HR`: Severe Bradycardia / Extreme Tachycardia ($\text{HR} < 40$ or $\text{HR} > 140\text{ bpm}$). Severity: `CRITICAL`.
6. `RF-EXTREME-TEMP`: Severe Hypothermia / Hyperpyrexia ($\text{Temp} < 35.0^\circ\text{C}$ or $\text{Temp} \ge 40.0^\circ\text{C}$). Severity: `CRITICAL`.
7. `RF-AIRWAY`: Airway Compromise / Stridor / Choking from intake evidence. Severity: `CRITICAL`.
8. `RF-HEMORRHAGE`: Exsanguinating / Massive Hemorrhage from intake evidence. Severity: `CRITICAL`.

### 3.4 Operational Priority Mapping
- **`P1_CRITICAL`**: Case assigned to `EMERGENCY` pathway, or any triggered critical red flag, or NEWS2 aggregate score >= 7 with acute symptoms, or Shock Index >= 1.0.
- **`P2_URGENT`**: NEWS2 aggregate score 5–6, or single-parameter score of 3 without critical red flag, or Shock Index 0.8–0.99, or acute urgent complaint.
- **`P3_MODERATE`**: NEWS2 aggregate score 1–4, or mild abnormal vitals, or moderate symptoms.
- **`P4_ROUTINE`**: Standard outpatient presentation with normal vitals and absence of physiological flags.

---

## 4. Database Schema & Persistence

### 4.1 Triage Snapshot Record (`triage_snapshots`)
```sql
CREATE TABLE triage_snapshots (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    vital_id VARCHAR(36) REFERENCES vitals(id) ON DELETE SET NULL,
    pathway VARCHAR(50) NOT NULL,
    current_state VARCHAR(50) NOT NULL,
    news2_score INTEGER,
    news2_risk VARCHAR(20),
    news2_is_complete BOOLEAN NOT NULL DEFAULT 1,
    shock_index FLOAT,
    shock_index_category VARCHAR(30),
    has_critical_red_flags BOOLEAN NOT NULL DEFAULT 0,
    triggered_red_flags JSON,
    uncertainty_score FLOAT NOT NULL DEFAULT 0.0,
    uncertainty_level VARCHAR(20) NOT NULL DEFAULT 'LOW',
    missing_critical_vitals JSON,
    data_completeness_ratio FLOAT NOT NULL DEFAULT 1.0,
    vitals_freshness JSON,
    vitals_overall_status VARCHAR(20) NOT NULL DEFAULT 'MISSING',
    priority_tier VARCHAR(20) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    calculated_by VARCHAR(36) NOT NULL,
    calculator_version VARCHAR(20) NOT NULL DEFAULT '1.0'
);
```

### 4.2 Immutability & Audit Trail
- Repeated triage evaluations create new snapshot rows linked to `case_id`; historical snapshots are never mutated.
- All vital signs entries are permanent and immutable.
- Calculation actions log structured events in `audit_events` with `actor_id`, `facility_id`, and snapshot metadata.

---

## 5. API Surface

| Endpoint | Method | RBAC Permission | Description |
| :--- | :---: | :---: | :--- |
| `/cases/{case_id}/vitals` | `POST` | `CASE_UPDATE` | Records canonical vital signs. Validates bounds, timestamps, and enforces verification governance. |
| `/cases/{case_id}/vitals` | `GET` | `CASE_READ` | Lists all historical vital observations chronologically. |
| `/cases/{case_id}/vitals/latest` | `GET` | `CASE_READ` | Returns the most recent canonical vital signs observation. |
| `/cases/{case_id}/triage/calculate` | `POST` | `CASE_UPDATE` | Executes deterministic triage calculation, persists snapshot, and logs audit event. |
| `/cases/{case_id}/triage/snapshot` | `GET` | `CASE_READ` | Retrieves the latest stored deterministic triage snapshot. |
| `/cases/{case_id}/priority` | `GET` | `CASE_READ` | Retrieves current operational priority tier and breakdown. |
| `/cases/queue` | `GET` | `CASE_READ` (Staff only) | Returns deterministic clinical queue with dynamic query-time waiting times. |

---

## 6. Frontend Integration

1. **VitalCard Component (`frontend/src/components/ui/VitalCard.tsx`):**
   - Renders vital signs with clear units and normal reference ranges.
   - Highlights critical values in clinical emergency red and abnormal values in amber.
   - Displays real-time freshness badge (`AVAILABLE`, `STALE`, `MISSING`).
   - Surfaces data provenance (`CLINICAL_OBSERVATION`, `PATIENT_REPORTED`, `DEVICE_DERIVED`).
2. **NurseTriageQueue (`frontend/src/components/staff/NurseTriageQueue.tsx`):**
   - Displays counts across all four priority tiers (`P1` through `P4`).
   - Supports filtering by acuity tier (`ALL`, `CRITICAL`, `URGENT`, `MODERATE`, `ROUTINE`) and free-text search.
   - Formats dynamic waiting times (`Xm wait`) computed on load.
   - Indicates missing critical vitals directly in the worklist table.
3. **DoctorWorkbenchView (`frontend/src/components/staff/DoctorWorkbenchView.tsx`):**
   - Features a dedicated **Deterministic Triage Metrics** card with an explicit "Non-Diagnostic" badge.
   - Displays RCP NEWS2 2017 aggregate score and clinical risk category.
   - Displays Shock Index and hemodynamic status.
   - Renders red-flag trigger details and vital freshness indicators.

---

## 7. Verification & Regression Record

### 7.1 Phase 16 Dedicated Test Suite (`backend/tests/test_phase16_triage.py`)
54 rigorous test scenarios covering all functional and adversarial boundaries:
- **Scenarios A–G**: Vital creation, range validation, SBP > DBP check, malformed value rejection, provenance preservation, future timestamp rejection, latest vital retrieval.
- **Scenarios H–I**: Freshness evaluation (available, stale, missing).
- **Scenarios J–M**: NEWS2 RCP 2017 calculation, incomplete data handling, repeatability, component breakdown.
- **Scenarios N–P**: Shock Index calculation, missing inputs, division-by-zero protection.
- **Scenarios Q–T**: Deterministic red-flag triggers, explanations, and rule versioning.
- **Scenarios U–V**: Priority tiering across emergency and normal pathways.
- **Scenarios W–Z**: Deterministic queue ordering, query-time dynamic waiting time, tie-breaking, and facility scoping.
- **Scenarios AA–AD**: Role-based access control, patient rejection from queue, nurse/clinician authorization, cross-facility denial.
- **Scenarios AE–AH**: Separation of uncertainty from physiological risk, missing data surfacing.
- **Scenarios AI–AN**: Historical immutability, audit logging, transaction rollback, error schema shielding, synthetic mode verification.
- **Adversarial Tests**: Forged client priority ignored, client risk score override ignored, client news2/shock index ignored, client red flags ignored, facility scope spoofing denied, wait time manipulation denied, future-dated vitals rejected, duplicate submissions preserved, stale data manipulation denied, malformed inputs rejected.
- **Requirement 6 & 20 Verifications**: Provenance encounter_id preservation, auditable events for `triage.red_flag_triggered`, `triage.priority_changed`, `triage.missing_vital_detected`, `triage.stale_vital_detected`, and physiological indicators in priority breakdown.
- **Intake Governance Verifications**: Canonical Vital persistence in `/intake/text` and unverified patient-reported vitals generating initial deterministic snapshot in `/intake/submit`.

### 7.2 Full Regression Suite
```
backend/tests/test_phase13_foundation.py     26 passed
backend/tests/test_phase14_auth_rbac.py      30 passed
backend/tests/test_phase15_intake.py         31 passed
backend/tests/test_phase16_triage.py         54 passed
backend/tests/test_clinical_scenarios.py     17 passed
backend/tests/test_innovation_acceptance.py   5 passed
=============================================================
Total: 163 passed in 138.73s (100% pass rate)
```

### 7.3 Frontend Verification
- `npm --prefix frontend run typecheck`: **Clean pass (0 errors)**.
- `npm --prefix frontend run lint`: **Clean pass (0 errors, 0 warnings)**.
- `npm --prefix frontend run build`: **Compiled successfully (15/15 routes static/dynamic)**.

---

## 8. Clinical Safety & Non-Diagnostic Limitations

1. **Non-Diagnostic Tooling:**
   The deterministic scoring and priority calculations implemented in Phase 16 are clinical workflow management aids designed to assist licensed healthcare providers in organizing patient worklists. They do not formulate clinical diagnoses, do not recommend medical treatments, and cannot replace direct human clinical assessment.
2. **Incomplete Observations:**
   When vital signs are incomplete, the system raises uncertainty indicators and highlights missing components. Clinicians must verify vital observations before acting upon triage recommendations.
3. **Phase Boundary Integrity:**
   All diagnostic formulation and condition inference logic remains strictly cordoned off for Phase 17. No Phase 17 or Phase 18 capabilities have been implemented.
