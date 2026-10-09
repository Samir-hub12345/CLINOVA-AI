# CLINOVA AI — Orchestration Engine Journey Specification

> **Document ID:** `RES-66`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Role: The Advisory Navigation Synthesizer

The **Orchestration Engine** is the cross-engine synthesis layer of CLINOVA AI. It operates as an intelligent care navigation advisor that couples the patient's biological state ($\text{CAREGRAPH}$) with the operational reality of the health system ($\text{FACILITYGRAPH}$).

$$\mathbf{Orchestration}(\mathbf{S}_{\text{pt}}, \mathbf{E}, U_t, \boldsymbol{\tau}_t, \mathbf{F}) \longrightarrow \mathbf{Action}_{\text{advisory}}$$

### 1.1 The Advisory-Only Invariant
> **Absolute Inviolable Rule:**  
> The Orchestration Engine is strictly **ADVISORY**.  
> The engine CANNOT autonomously execute clinical orders, discharge patients, book surgeries, or initiate transfers. Every orchestration output is presented to a qualified human healthcare professional as a recommended clinical pathway, requiring explicit human validation, friction-calibrated modification, or override.

---

## 2. The Six Canonical Orchestration Actions

The Orchestration Engine evaluates the clinical state across all journey steps and recommends one of **six canonical actions**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SIX CANONICAL ORCHESTRATION ACTIONS                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ 1. ASK ] ───────> Epistemic gap present; queries patient for details.    │
│                                                                             │
│  [ 2. VERIFY ] ────> Objective vital or red-flag missing; summons nurse.    │
│                                                                             │
│  [ 3. CONTINUE ] ──> Clinical trajectory stable; proceeds with current plan.│
│                                                                             │
│  [ 4. OBSERVE ] ───> Trajectory uncertain; orders serial bedside monitoring.│
│                                                                             │
│  [ 5. ESCALATE ] ──> Decompensation detected; triggers emergency fast-track.│
│                                                                             │
│  [ 6. REFER ] ─────> Local facility capability deficit; initiates transfer. │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Deep-Dive Specification of the Six Actions

---

### Action 1: `ASK` (Targeted Information Gathering)
- **Clinical Intent:** Resolves epistemic ambiguity by soliciting targeted self-reported information directly from the patient or caregiver.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Non-emergent, conscious, oriented, ambulatory.
- **Evidence Status ($\mathbf{E}$):** `PARTIALLY_SUFFICIENT`; core complaint known, but symptom duration, medication dosages, or comorbidity details absent.
- **Uncertainty ($U_t$):** Moderate to High ($0.40 \le U_t < 0.70$).
- **Trajectory ($\boldsymbol{\tau}_t$):** `STABLE` or `UNKNOWN`.
- **Facility Context ($\mathbf{F}$):** Any operating environment.
- **Human Reviewer:** Patient / Caregiver (`ROLE_PATIENT`) or Health Worker (`ROLE_HEALTH_WORKER`).
- **Safety Gate:** Maximum question limit cap: Hard stop at 3 questions. Cannot be used if vital red flags are present.
- **Possible Override:** Patient can tap "Skip / Proceed to Nurse", bypassing questions without error.
- **Resulting Next State:** Transitions to `STATE_FOLLOW_UP_PENDING`.

---

### Action 2: `VERIFY` (Frontline Objective Physical Verification)
- **Clinical Intent:** Collapses critical diagnostic entropy by mandating calibrated, in-person vital signs measurement and physical red-flag inspection.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Walking wounded, non-acute presentation, but lacking physical baseline measurements.
- **Evidence Status ($\mathbf{E}$):** `INSUFFICIENT`, `CONFLICTING`, or `UNRELIABLE`.
- **Uncertainty ($U_t$):** Critical ($U_t \ge 0.65$ due to absent objective measurements).
- **Trajectory ($\boldsymbol{\tau}_t$):** Undefined until baseline physiological vitals established.
- **Facility Context ($\mathbf{F}$):** Facility with triage nursing staff or community health worker.
- **Human Reviewer:** Frontline Triage Nurse (`ROLE_NURSE`) or Community Health Worker (`ROLE_HEALTH_WORKER`).
- **Safety Gate:** Physiological bounds check; dynamic red-flag escalation if $\text{SpO}_2 < 85\%$ or $\text{Shock Index} > 1.0$.
- **Possible Override:** Doctor can perform on-site vitals during consultation, bypassing nursing queue.
- **Resulting Next State:** Transitions to `STATE_STAFF_DATA_PENDING`.

---

### Action 3: `CONTINUE` (Execute Standard Approved Care)
- **Clinical Intent:** Endorses completion of the current care plan for stable patients within local hospital capability.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Acuity P4 (Routine) or P5 (Non-urgent); stable chronic condition or minor self-limiting illness.
- **Evidence Status ($\mathbf{E}$):** `SUFFICIENT` and `CLINICIAN_VERIFIED`.
- **Uncertainty ($U_t$):** Minimal ($U_t \le 0.15$).
- **Trajectory ($\boldsymbol{\tau}_t$):** `STABLE` or `IMPROVING`.
- **Facility Context ($\mathbf{F}$):** Local facility has complete diagnostic and therapeutic stock ($\Phi_{\text{local}} = 1.0$).
- **Human Reviewer:** Registered Medical Practitioner (`ROLE_CLINICIAN`).
- **Safety Gate:** Drug-drug interaction and allergy cross-reference check prior to discharge print.
- **Possible Override:** Clinician may alter prescribed medications, dosages, or follow-up duration.
- **Resulting Next State:** Transitions to `STATE_ROUTINE_CARE` (Pathway A).

---

### Action 4: `OBSERVE` (Bedside Serial Monitoring / Further Review)
- **Clinical Intent:** Implements an intentional clinical pause to monitor disease trajectory over time or await pending laboratory investigations.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Borderline clinical presentation (e.g., equivocal acute abdomen, moderate dehydration undergoing oral rehydration, awaiting blood culture).
- **Evidence Status ($\mathbf{E}$):** `PARTIALLY_SUFFICIENT` (Awaiting definitive diagnostic confirmation).
- **Uncertainty ($U_t$):** Moderate ($0.25 \le U_t \le 0.45$).
- **Trajectory ($\boldsymbol{\tau}_t$):** `STABLE` but carrying risk of sudden deterioration.
- **Facility Context ($\mathbf{F}$):** Facility possesses observation beds (Casualty Day Care, HDU, or Day Ward).
- **Human Reviewer:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Safety Gate:** Time-capped observation protocol: Maximum 6 hours for OPD observation; beyond 6 hours mandates either formal inpatient admission (`STATE_WARD_REQUESTED`) or revisit slot (`STATE_FURTHER_REVIEW`).
- **Possible Override:** Doctor may convert case to immediate ward admission or routine discharge at any moment.
- **Resulting Next State:** Transitions to `STATE_FURTHER_REVIEW` (Pathway B) or `STATE_WARD_REQUESTED` (Pathway C).

---

### Action 5: `ESCALATE` (Immediate Emergency Fast-Track Resuscitation)
- **Clinical Intent:** Instantly shifts platform into acute life-support mode, bypassing all non-essential documentation.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Acuity P1 (Resuscitation) or P2 (Emergent); circulatory collapse, agonal breathing, severe hypoxia, acute trauma.
- **Evidence Status ($\mathbf{E}$):** `EMERGENCY_OVERRIDDEN`.
- **Uncertainty ($U_t$):** Irrelevant (Clinical emergency overrides epistemic completeness).
- **Trajectory ($\boldsymbol{\tau}_t$):** `DETERIORATING` or `CRITICAL`.
- **Facility Context ($\mathbf{F}$):** Any environment (Resuscitation occurs immediately on-site regardless of facility level).
- **Human Reviewer:** Any authenticated healthcare worker (Nurse, Doctor, Paramedic).
- **Safety Gate:** Resuscitation Monopoly Gate: All administrative forms frozen; emergency HUD activated.
- **Possible Override:** Clinician can de-escalate once patient is stabilized ($\text{Shock Index} < 1.0$, $\text{SpO}_2 > 95\%$).
- **Resulting Next State:** Transitions immediately to `STATE_EMERGENCY_ACTIVE` (Pathway E).

---

### Action 6: `REFER` (Inter-Facility Capability-Matched Transfer)
- **Clinical Intent:** Initiates a structured, verified inter-facility transfer because patient requirements exceed local facility capability.
- **Patient State ($\mathbf{S}_{\text{pt}}$):** Acuity P1, P2, or P3 requiring specialized diagnostics, surgery, ICU care, or hemodialysis.
- **Evidence Status ($\mathbf{E}$):** `SUFFICIENT` or `EMERGENCY_OVERRIDDEN` with verified clinical deficit.
- **Uncertainty ($U_t$):** Variable; but clinical requirement is clear.
- **Trajectory ($\boldsymbol{\tau}_t$):** `DETERIORATING` or high risk of deterioration without specialized intervention.
- **Facility Context ($\mathbf{F}$):** Feasibility Index $\Phi_{\text{local}} = 0.0$ (Proven capability deficit at local facility).
- **Human Reviewer:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Safety Gate:** Anti-Blind-Transfer Gate: Enforces receiving facility identification, bed confirmation, and transport match.
- **Possible Override:** Clinician may select a different destination hospital or manage on-site if transport is impossible.
- **Resulting Next State:** Transitions to `STATE_REFERRAL_PENDING` (Pathway D).

---

## 4. Multi-Dimensional Decision Matrix

The logic table governing Orchestration evaluations is synthesized below:

| Condition # | Risk Band | Trajectory ($\boldsymbol{\tau}$) | Uncertainty ($U_t$) | Local Feasibility ($\Phi$) | Recommended Advisory Action | Primary Human Gate | Target State |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **C1** | Any | Any | $> 0.60$ | Any | `VERIFY` | Triage Nurse | `STATE_STAFF_DATA_PENDING` |
| **C2** | Low | Stable | $< 0.20$ | $1.0$ (Complete) | `CONTINUE` | Attending Clinician | `STATE_ROUTINE_CARE` |
| **C3** | Moderate | Stable | $0.20 - 0.40$| $1.0$ (Complete) | `OBSERVE` | Attending Clinician | `STATE_FURTHER_REVIEW` |
| **C4** | High | Deteriorating | Any | $1.0$ (Complete) | `OBSERVE` / `ADMIT`| Attending Clinician | `STATE_WARD_REQUESTED` |
| **C5** | Critical | Critical | Any | Any | `ESCALATE` | Emergency Doctor / Nurse | `STATE_EMERGENCY_ACTIVE` |
| **C6** | Any | Any | Any | $0.0$ (Deficit) | `REFER` | Attending Clinician | `STATE_REFERRAL_PENDING` |
