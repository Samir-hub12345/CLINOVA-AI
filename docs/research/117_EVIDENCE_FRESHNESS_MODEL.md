# CLINOVA AI — Evidence Temporal Freshness & Decay Model

> **Document ID:** `RES-117`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Peril of Temporal Atrophy in Clinical Data

Human physiology is dynamic, volatile, and time-dependent. An arterial blood gas or serum potassium level is not an immutable mathematical constant; it is a fleeting snapshot of cellular respiration at an exact microsecond in time.

In legacy electronic health records, systems commit a lethal error: **treating stale historical observations as current clinical truth**.
- A blood pressure of $120/80\text{ mmHg}$ recorded at 8:00 AM during outpatient registration is blindly pulled into an emergency triage risk calculator at 2:30 PM, masking acute hemorrhagic shock.
- An ICU bed telemetry entry stating *"2 Ventilator Beds Available"* recorded 18 hours ago is relied upon to launch an emergency inter-facility ambulance transfer, resulting in a dead-on-arrival catastrophe when the patient arrives at a saturated receiving hospital.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL EVIDENCE FRESHNESS INVARIANT                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│          DO NOT BLINDLY REUSE STALE EVIDENCE AS CURRENT CLINICAL FACT.      │
│                                                                             │
│   Every clinical datum has an operational shelf-life determined by its      │
│   physiological volatility. When a datum crosses its staleness threshold,   │
│   its epistemic authority decays, and active decision algorithms must       │
│   demand a fresh physical measurement.                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Four Canonical Freshness States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FOUR CANONICAL FRESHNESS STATES                       │
├──────────────────┬──────────────────────────────────────────────────────────┤
│ Freshness State  │ Operational & Epistemic Definition                       │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ CURRENT          │ Captured within clinical validity window; fully active.   │
│ STALE            │ Exceeded optimal window; usable only with warning prompt.│
│ EXPIRED          │ Statistically detached from physiology; unusable for risk│
│ UNKNOWN          │ Timestamp missing or corrupted; treated as unverified.   │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 3. Physiological Volatility Tiers & Freshness Thresholds

Different biological domains decay at radically different mathematical velocities. CLINOVA AI stratifies clinical evidence into five **Volatility Tiers**:

| Evidence Category | Example Parameters | CURRENT Window | STALE Window | EXPIRED Window | Operational Gating Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier A: Hyper-Volatile** | Blood Glucose in Shock, Arterial Blood Gas, Capillary Refill | $< 30\text{ min}$ | $30\text{ min} - 2\text{ h}$ | $> 2\text{ hours}$ | Hard-blocks insulin titration; triggers nurse re-check alert. |
| **Tier B: Acute Vitals** | Heart Rate, Blood Pressure, SpO2, Respiratory Rate, Temp | $< 2\text{ hours}$ | $2 - 6\text{ hours}$ | $> 6\text{ hours}$ | Excludes from active NEWS2 calculation; prompts bedside vitals. |
| **Tier C: Acute Labs** | Serum Potassium, Troponin-I, Hemoglobin in Active Bleed | $< 4\text{ hours}$ | $4 - 12\text{ hours}$ | $> 12\text{ hours}$ | Blocks procedural clearance; requires repeat stat lab order. |
| **Tier D: Facility Telemetry**| Oxygen manifold pressure, ICU bed availability, Blood bank stock| $< 4\text{ hours}$ | $4 - 12\text{ hours}$ | $> 12\text{ hours}$ | Blocks automated transfer booking; requires voice confirmation. |
| **Tier E: Baseline Imaging** | 12-lead ECG, Chest X-ray, Baseline Serum Creatinine, HbA1c | $< 24\text{ hours}$ (Inpatient) / $< 90\text{ days}$ (OPD) | $1 - 7\text{ days}$ (Inpatient) / $90 - 365\text{ days}$ (OPD) | $> 7\text{ days}$ (Inpatient) / $> 1\text{ year}$ (OPD) | Demotes from active baseline to historical contextual archive. |

---

## 4. Mathematical Freshness Decay Function

The temporal freshness factor $\gamma(t) \in [0.0, 1.0]$ for an evidence record $e$ captured at $t_{\text{capture}}$ is formulated as a sigmoid half-life decay function:

$$\Delta t = t_{\text{current}} - t_{\text{capture}}$$
$$\gamma(e, t) = \frac{1}{1 + \exp\left( \frac{\Delta t - \tau_{\text{stale}}}{\kappa} \right)}$$

Where:
- $\tau_{\text{stale}}$ is the half-life threshold corresponding to the parameter's volatility tier.
- $\kappa$ is the steepness parameter governing transition velocity.

### Operational State Mapping:
$$\text{Freshness}(e, t) = \begin{cases} 
\text{CURRENT} & \text{if } \gamma(e, t) \ge 0.70 \\ 
\text{STALE} & \text{if } 0.20 \le \gamma(e, t) < 0.70 \\ 
\text{EXPIRED} & \text{if } \gamma(e, t) < 0.20 \\ 
\text{UNKNOWN} & \text{if } t_{\text{capture}} \text{ is NULL or uncalibrated} 
\end{cases}$$

---

## 5. Freshness Impact on Clinical Decision Support

1. **Active Gating in Risk Scoring:** If any component vital sign required for NEWS2 is `EXPIRED` ($> 6\text{ hours}$ old), the score is NOT computed with stale data. Instead, NEWS2 outputs `NULL`, and the system surfaces an explicit missing-data divert:
   ```
   [!] NEWS2 CALCULATION BLOCKED:
       - Systolic Blood Pressure EXPIRED (Captured 7h 12m ago at 08:15 AM)
       - Action: Nurse Anita must log fresh vitals to compute active acuity score.
   ```
2. **Inter-Facility Referral Feasibility:** When FACILITYGRAPH evaluates whether District Hospital Dhenkanal has available ventilator beds:
   - If telemetry is `CURRENT` ($< 4\text{ hours}$): System marks transfer destination as `FEASIBLE_AUTO_CONFIRMED`.
   - If telemetry is `STALE` ($4\text{--}12\text{ hours}$): System marks destination as `FEASIBLE_VERIFICATION_REQUIRED` (requires telephonic nurse-to-nurse call).
   - If telemetry is `EXPIRED` ($> 12\text{ hours}$): Destination is excluded from automated recommendations to prevent blind transfers.

---

## 6. Freshness Relational Specification

```sql
-- Schema embedding temporal freshness in evidence_records
ALTER TABLE evidence_records
ADD COLUMN capture_timestamp TIMESTAMPTZ NOT NULL,
ADD COLUMN freshness_status VARCHAR(16) NOT NULL DEFAULT 'CURRENT' CHECK (freshness_status IN (
    'CURRENT', 'STALE', 'EXPIRED', 'UNKNOWN'
)),
ADD COLUMN staleness_threshold_minutes INTEGER NOT NULL DEFAULT 120,
ADD COLUMN last_freshness_evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Periodic or on-read SQL expression for dynamic evaluation:
-- UPDATE evidence_records
-- SET freshness_status = CASE 
--     WHEN EXTRACT(EPOCH FROM (NOW() - capture_timestamp))/60 <= staleness_threshold_minutes THEN 'CURRENT'
--     WHEN EXTRACT(EPOCH FROM (NOW() - capture_timestamp))/60 <= (staleness_threshold_minutes * 3) THEN 'STALE'
--     ELSE 'EXPIRED'
-- END;
```

This guarantees that temporal atrophy is continuously monitored, preventing outdated records from compromising live patient care.
