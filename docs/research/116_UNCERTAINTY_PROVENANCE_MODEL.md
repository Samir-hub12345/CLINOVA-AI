# CLINOVA AI — Epistemic Uncertainty Provenance Model ($U_t$)

> **Document ID:** `RES-116`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Decoupling Epistemic Uncertainty from Physiological Acuity

In conventional clinical triage algorithms and medical machine learning benchmarks, a fundamental category mistake is routinely made: **confusing epistemic uncertainty ($U_t$) with physiological acuity ($R_t$)**.

- **Scenario 1:** A 22-year-old athlete visits the outpatient department for an ankle sprain. The electronic intake was skipped, meaning their blood pressure, blood glucose, and family history are missing. The system has **High Epistemic Uncertainty ($U_t \approx 0.75$)** because critical data fields are absent. However, their **Physiological Risk is Minimal ($R_t \approx 0.05$)**. Rushing this patient to the resuscitation bay would be absurd.
- **Scenario 2:** An 84-year-old patient presents with crushing substernal chest pain, cold clammy skin, heart rate $142\text{ bpm}$, and blood pressure $70/40\text{ mmHg}$. A 12-lead ECG confirms anterior ST-elevation myocardial infarction. The system has **Zero Epistemic Uncertainty ($U_t \approx 0.02$)** because the clinical picture is complete and unequivocal. Yet their **Physiological Risk is Lethal ($R_t \approx 0.98$)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CARDINAL LAW OF UNCERTAINTY DECOUPLING                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  UNCERTAINTY ABOUT EVIDENCE  ≠  RISK SEVERITY               │
│                                                                             │
│   Epistemic uncertainty (Ut) measures the incompleteness, discordance,      │
│   and degradation of the evidence base.                                     │
│   Physiological risk (Rt) measures the biological hazard to the patient.    │
│   Never allow high uncertainty to automatically imply clinical danger.      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Eight Canonical Contributors to Epistemic Uncertainty ($U_t$)

Epistemic uncertainty is not a subjective heuristic; it is a mathematically computable composite metric derived from eight concrete evidence states:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               EIGHT CONTRIBUTORS TO EPISTEMIC UNCERTAINTY (Ut)              │
├────────────────────────────┬─────────┬──────────────────────────────────────┤
│ Evidence Contributor       │ Weight  │ Mathematical Formulation             │
├────────────────────────────┼─────────┼──────────────────────────────────────┤
│ 1. Missing Critical Data   │ $w_1=0.30$│ Ratio of unmeasured Tier 1 vitals    │
│ 2. Conflicting Evidence    │ $w_2=0.20$│ Count of active unresolved conflicts │
│ 3. Low-Quality OCR Crop    │ $w_3=0.10$│ Penalty for blur/smudged lab scans   │
│ 4. Low-Confidence Voice    │ $w_4=0.10$│ Penalty for low SNR / inaudible gaps │
│ 5. Stale External Records  │ $w_5=0.08$│ Temporal decay of historical reports │
│ 6. Unverified Patient Text │ $w_6=0.08$│ Subjective narrative uncorroborated  │
│ 7. Incomplete Timeline     │ $w_7=0.07$│ Missing onset datetime / progression │
│ 8. Unavailable Diagnostics │ $w_8=0.07$│ Pending critical bedside lab/imaging │
└────────────────────────────┴─────────┴──────────────────────────────────────┘
```

---

## 3. Mathematical Formulation of $U_t$

The instantaneous Case Uncertainty Score $U_t \in [0.00, 1.00]$ is computed as the normalized weighted sum of its eight evidence penalties:

$$U_t = \min\left(1.0, \; \sum_{k=1}^8 w_k \cdot \phi_k(t)\right)$$

Where each component penalty $\phi_k(t) \in [0.0, 1.0]$ is defined as:

1. **Missing Critical Data Penalty ($\phi_1$):**
   $$\phi_1 = 1.0 - \frac{\sum_{i \in \text{Tier1}} \mathbb{I}(e_i \neq \text{UNKNOWN})}{|\text{Tier1}|}$$
   If any of the 4 core Tier 1 vitals (Heart Rate, SBP, SpO2, Respiratory Rate) is missing, $\phi_1 \ge 0.25$.

2. **Conflicting Evidence Penalty ($\phi_2$):**
   $$\phi_2 = \min\left(1.0, \; \sum_{c \in \text{Conflicts}} \frac{\text{AcuityWeight}(c)}{2.0}\right)$$
   Active unresolved conflicts across vital signs or allergies directly inflate $\phi_2$.

3. **Low-Quality OCR Penalty ($\phi_3$):**
   $$\phi_3 = \frac{1}{|\text{OCR}|} \sum_{j \in \text{OCR}} \max(0.0, \; 0.80 - Q_j)$$

4. **Low-Confidence Audio Penalty ($\phi_4$):**
   $$\phi_4 = \frac{1}{|\text{Transcripts}|} \sum_{m} \max(0.0, \; 0.85 - C_m)$$

5. **Stale Records Penalty ($\phi_5$):**
   $$\phi_5 = \frac{\text{StaleCount}}{\text{TotalExternalCount}}$$

6. **Unverified Patient Report Penalty ($\phi_6$):**
   $$\phi_6 = \frac{|\{e \mid \text{source} = \text{'PATIENT\_REPORTED'} \land \text{status} = \text{'UNVERIFIED'}\}|}{|\text{AllSymptoms}|}$$

7. **Incomplete Timeline Penalty ($\phi_7$):**
   $$\phi_7 = \begin{cases} 0.0 & \text{if onset datetime and trajectory slope are known} \\ 0.5 & \text{if onset approximate ("few days")} \\ 1.0 & \text{if onset completely unrecorded} \end{cases}$$

8. **Unavailable Diagnostics Penalty ($\phi_8$):**
   $$\phi_8 = \frac{|\text{PendingCriticalOrders}|}{|\text{TotalOrders}|}$$

---

## 4. Uncertainty Stratification & Orchestration Constraints

The composite score $U_t$ maps into four discrete operational uncertainty bands that directly constrain automated system actions:

| Uncertainty Band | Score Range | Clinical Meaning | Orchestration Constraint | Clinician Workbench Visual |
| :--- | :--- | :--- | :--- | :--- |
| **`LOW_UNCERTAINTY`** | $U_t < 0.20$ | High-fidelity, complete clinical picture. | Full automated queue promotion; normal CAREGRAPH recommendations. | Clean green status badge; zero warning banners. |
| **`MODERATE_UNCERTAINTY`**| $0.20 \le U_t < 0.45$| Minor gaps (e.g. approximate onset time). | Allowed into doctor queue; missing fields highlighted. | Amber informational tag: *"Onset timing approximate."* |
| **`HIGH_UNCERTAINTY`** | $0.45 \le U_t < 0.70$| Critical vital unmeasured or conflict active. | Hard-blocked from routine doctor queue; diverted to Nurse Worklist. | Bright orange warning: *"Vital signs missing — nurse triage required."* |
| **`CRITICAL_UNCERTAINTY`**| $U_t \ge 0.70$ | Acute perceptual voids; ungrounded case. | Emergency fast-track review to rule out occult decompensation. | Flashing red banner: *"High epistemic uncertainty — assess in person."* |

---

## 5. Interaction Between Uncertainty ($U_t$) and Queue Priority $P(t)$

In Phase 6 (`RES-90`), the dynamic doctor queue priority function $P(t)$ was formulated as:
$$P(t) = w_R R_t + w_{\text{wait}} f(\text{wait\_time}) + w_{\text{traj}} \text{Slope} + w_U U_t$$

### The Safety Role of Uncertainty in Waiting Rooms
Why does $U_t$ enter the priority equation positively ($+ w_U U_t$)?
- If a patient has been waiting in a crowded emergency lobby for 45 minutes and their vitals have NEVER been measured, their physiological risk $R_t$ is technically unknown.
- If $U_t$ were ignored, the patient would linger at the bottom of the queue with $R_t = 0$.
- By incorporating $+ w_U U_t$, the system recognizes that **unmeasured patients represent hidden danger**. The uncertainty penalty gradually escalates their queue position, forcing a triage nurse to measure their vitals before they silently decompensate in the waiting room.

---

## 6. Uncertainty Relational Specification

In the canonical schema, `clinical_evaluations` stores $U_t$ alongside the decoupled risk and trajectory vectors:

```sql
-- Formal uncertainty columns in clinical_evaluations
ALTER TABLE clinical_evaluations
ADD COLUMN uncertainty_score NUMERIC(4,3) NOT NULL CHECK (uncertainty_score >= 0.0 AND uncertainty_score <= 1.0),
ADD COLUMN uncertainty_band VARCHAR(24) NOT NULL CHECK (uncertainty_band IN (
    'LOW_UNCERTAINTY', 'MODERATE_UNCERTAINTY', 'HIGH_UNCERTAINTY', 'CRITICAL_UNCERTAINTY'
)),
ADD COLUMN uncertainty_contributors JSONB NOT NULL; 
-- Stores breakdown: { "missing_critical": 0.25, "active_conflicts": 0.20, "low_quality_ocr": 0.05, ... }
```

This mathematical structure guarantees that epistemic uncertainty is never swept under the rug, never fabricated, and never confused with biological severity.
