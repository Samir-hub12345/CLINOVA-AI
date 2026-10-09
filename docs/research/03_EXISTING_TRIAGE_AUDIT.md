# CLINOVA AI — Existing Triage Solutions Audit & Comparative Analysis

> **Document ID:** `RES-03`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary

This audit evaluates the global and domestic landscape of clinical triage systems. It covers traditional clinical scoring frameworks (ESI, MTS, CTAS), commercial consumer digital triage platforms (Ada Health, Infermedica, Buoy Health, K Health), specialized ambient audio triage (Corti), and historical cautionary precedents (Babylon Health).

The audit assesses each system across eleven standardized technical criteria to uncover the exact boundaries of current technology and define the remaining clinical gap.

---

## 2. Master Triage Systems Comparative Audit

| System Name & Origin | System Type & Method | Primary Inputs | Primary Outputs | Uncertainty Handling | Longitudinal Trajectory | Facility Capability Aware? | Closed-Loop Referral? | Outcome Tracking? | Documented Limitations | Evidence Grade |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Emergency Severity Index (ESI v4/v5)** *(USA / AHRQ)* | Deterministic 5-level clinical rule algorithm (Non-AI). | Chief complaint, vital signs, anticipated resource needs. | Acuity Band 1 to 5; recommended queue placement. | **None.** Assumes complete, accurate vitals available at desk. | **None.** Static snapshot; no temporal recalculation while waiting. | **Implicit only.** Based on generic resource availability (IV, labs, CT). | **None.** Terminal triage decision within single facility. | **None.** No outcome loop built into protocol. | High inter-rater variability (kappa 0.65–0.78); under-triages elderly and atypical presentations. | **Grade A** (Gilboy et al., AHRQ, 2020) |
| **Manchester Triage System (MTS)** *(UK / Europe)* | Flowchart-based deterministic decision tree (53 flowcharts). | Specific presentation flowchart, discriminators, vitals. | 5 color priority codes (Red, Orange, Yellow, Green, Blue). | **None.** Strict binary discriminator evaluation. | **None.** Requires manual re-triage by nurse on fixed schedule. | **None.** Assumes all receiving emergency rooms have identical capability. | **None.** Local emergency department prioritization only. | **None.** No longitudinal tracking after triage nurse stamp. | High nurse subjectivity; rigid flowcharts struggle with complex multimorbidity. | **Grade A** (Mackway-Jones et al., BMJ, 2014) |
| **Canadian Triage & Acuity Scale (CTAS)** *(Canada)* | Symptom-based protocol with physiological modifiers. | Chief complaint code, Canadian ED Information System (CEDIS) list, vitals. | 5 acuity levels with target time-to-doctor windows. | **None.** Assumes unrecorded vitals are non-critical. | **Manual periodic reassessment.** No continuous trajectory slope. | **None.** Blind to receiving facility resource saturation. | **None.** Confined to intake department. | **None.** Terminates at physician handoff. | Documentation burden high; often compressed during ED crowding surges. | **Grade A** (Beveridge et al., CJEM, 2016) |
| **Ada Health** *(Germany / Global)* | Probabilistic Bayesian inference network + Medical Knowledge Graph. | Natural language text, age, biological sex, structured symptom Q&A. | Differential probability list; recommended care level (Self-care, GP, ER). | **Implicit.** Uses probabilistic rankings; does not expose epistemic uncertainty. | **Minimal.** Multi-session user history; no real-time physiological delta. | **No.** Recommends abstract care levels (e.g., "See a doctor within 24h") without knowing local facility state. | **No.** Provides consumer advice; no direct EHR/facility referral dispatch. | **Self-reported only.** In-app user surveys; no verified clinical endpoint. | Propensity to over-refer mild symptoms to urgent care to minimize medicolegal liability. | **Grade A** (Nature Digital Medicine, 2020) |
| **Infermedica** *(Poland / Global)* | Medical Knowledge Engine (Bayesian network + expert clinical curation). | Structured symptom inputs, demographics, risk factors, lab values. | Triage level (Emergency, Consultation, Self-care); summary report. | **Heuristic confidence scores.** Missing fields simply omitted from prior calculation. | **No.** Single-session evaluation. | **Partial (API-level).** Can be mapped to client provider rosters, but lacks live telemetry. | **Partial.** Can trigger API appointment booking; no capability-matched hospital transfer. | **No.** Platform operates as headless API; outcomes retained by client EHR. | Requires manual configuration by health system; cannot ingest raw unformatted lab images directly. | **Grade B** (Infermedica Whitepaper & Clinical Validation, 2023) |
| **Corti** *(Denmark / USA)* | Ambient Speech NLP + Machine Learning (Audio emergency calls). | Live 911 / 112 emergency telephone audio stream. | Real-time diagnostic prompts (e.g., Cardiac Arrest alert) to dispatcher. | **Acoustic confidence score.** Flags ambiguous speech or background noise. | **Intra-call temporal tracking.** Tracks evolving caller description during 3-min call. | **No.** Focused exclusively on caller audio; blind to hospital ICU/ER bed capacity. | **Partial.** Informs ambulance dispatch priority; no receiving facility reservation. | **Dispatcher validation.** Records if paramedic confirmed arrest on scene. | Highly dependent on audio fidelity; high English/Danish optimization; low Indian vernacular support. | **Grade A** (Blomberg et al., Resuscitation, 2019) |
| **Babylon Health (GP at Hand)** *(UK / Cautionary Precedent)* | Generative chatbot + Decision trees (Defunct / Restructured 2023). | Free-text symptom chat, patient demographic profile. | Automated triage advice, direct video GP consultation booking. | **Poor.** Masked uncertainty behind authoritative chatbot answers. | **None.** Disconnected episodic chat sessions. | **No.** Assumed NHS England general practice availability. | **NHS GP booking.** Did not orchestrate inter-facility capability matching. | **Audit-driven.** Subject to NHS clinical safety investigations. | **Catastrophic failure:** Over-promoted AI diagnosis; failed safety audits in chest pain/pregnancy; collapsed financially. | **Grade A** (BMJ Investigation, 2018; Forbes/FT, 2023) |
| **K Health** *(USA)* | Machine Learning trained on anonymized Israeli HMO data (Maccabi). | Structured symptom intake dialog, medical history. | Predicted diagnosis probabilities, virtual physician chat routing. | **Statistical confidence intervals.** | **Cross-encounter record.** Longitudinal medical history stored. | **No.** Routes strictly into virtual telemedicine clinic. | **Virtual to in-person suggestion only.** No hospital transfer orchestration. | **In-app medical chart.** Follow-up chats within virtual platform. | Data derived from Israeli healthcare population; questionable generalizability to rural India. | **Grade B** (K Health Clinical Publications, 2022) |

---

## 3. Deep-Dive Findings & Innovation Gaps

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE STRUCTURAL TRIAGE VACUUM AUDIT                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. STATIC ACUITY TRAP:                                                     │
│     All major hospital triage systems (ESI, MTS, CTAS) produce a STATIC     │
│     number at minute zero and abandon the patient in the waiting room.      │
│                                                                             │
│  2. UNCERTAINTY BLINDNESS:                                                  │
│     Missing vital signs or omitted clinical qualifiers are either ignored   │
│     or imputed as normal, masking acute diagnostic risk.                    │
│                                                                             │
│  3. FACILITY RESOURCE BLINDNESS:                                            │
│     Every existing triage platform operates in an abstract clinical vacuum, │
│     recommending "Immediate ICU" even if the hospital has zero open beds.   │
│                                                                             │
│  4. UNIDIRECTIONAL TERMINATION:                                             │
│     Triage systems hand off to the waiting room and terminate; they never   │
│     track whether the patient survived, deteriorated, or was admitted.      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 The Static Acuity Trap
In high-volume public hospitals across Odisha and India, patients frequently wait 2 to 5 hours after triage. ESI and MTS treat triage as an intake administrative gate. If a patient presenting with stable vitals begins decompensating (e.g., silent hemorrhage, expanding intracranial bleed, or progressive sepsis), the static ESI score of "Level 3" remains unchanged on the whiteboard until the patient collapses.
- **CLINOVA Countermeasure:** CAREGRAPH computes a dynamic trajectory slope ($\Delta \text{Vitals} / \Delta t$) and temporal risk escalation, automatically elevating queue priority when wait times exceed clinical thresholds.

### 3.2 The Epistemic Uncertainty Gap
Commercial symptom checkers (Ada, Infermedica) collect symptoms but treat unasked questions as absent symptoms. In clinical practice, the absence of an assessment is **not** the same as the absence of a symptom.
- **CLINOVA Countermeasure:** Explicit representation of uncertainty vectors (`KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`) and active Next-Best Information (NBI) generation to proactively close high-stakes gaps.

### 3.3 The Disconnection from Facility Reality
Existing triage tools recommend care levels (e.g., "Tertiary Emergency Care") without verifying whether the facility actually possesses the equipment, specialists, or beds to execute that care.
- **CLINOVA Countermeasure:** Direct integration with FACILITYGRAPH to assess care feasibility in real time, preventing futile admissions and dangerous blind referrals.
