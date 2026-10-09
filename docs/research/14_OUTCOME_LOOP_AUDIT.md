# CLINOVA AI — Outcome-Loop & Continuous Learning Audit

> **Document ID:** `RES-14`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Audit Mandate

This audit investigates how deployed clinical artificial intelligence systems and Clinical Decision Support Systems (CDSS) globally connect:

$$\mathbf{AI\ RECOMMENDATION} \longrightarrow \mathbf{CLINICIAN\ DECISION} \longrightarrow \mathbf{ACTUAL\ ACTION} \longrightarrow \mathbf{PATIENT\ OUTCOME}$$

The audit tests whether existing systems:
1. Systematically capture real clinical endpoints (recovery, deterioration, complication, mortality).
2. Record clinician modifications and overrides with structured reasoning.
3. Retrospectively evaluate algorithmic concordance against ground-truth outcomes.
4. Safely calibrate model parameters based on clinician disagreement without unsafe autonomous online fine-tuning.
5. Track closed-loop referral completion and transfer outcomes.

---

## 2. Adversarial Mapping: How Deployed AI Handles the Outcome Chain

| AI System / Platform Category | Are Actual Patient Outcomes Collected? | Are Clinician Overrides Recorded? | Are Recommendations Retrospectively Evaluated? | Does System Learn from Disagreement? | Is Referral Completion Tracked? | Documented Industry Limitations | Evidence Grade |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **EHR Sepsis Prediction Models (Epic Sepsis Model - ESM)** | **Yes (Administrative).** ICD-10 billing codes and hospital discharge records captured in EHR. | **Partial.** Nurse clicks "Acknowledge" or "Dismiss" on pop-up alert; rarely records clinical rationale. | **Retrospectively via Academic Studies.** Vendor does not run automated real-time evaluation loops. | **No (Static Weights).** Models remain static; require manual re-training and re-validation cycles by data scientists. | **No.** Internal hospital alert; decoupled from inter-facility transfer. | Famous external validation study by Wong et al. (*JAMA Internal Medicine*, 2021) revealed ESM had a PPV of only 12% and missed 67% of sepsis cases because feedback loops were absent. | **Grade A** (Wong et al., JAMA, 2021) |
| **Consumer Symptom Checkers (Ada Health, Babylon, Buoy)** | **Self-reported only.** In-app voluntary user survey ("Did you see a doctor? Did your symptoms improve?"). | **No.** No physician involved in the loop during direct-to-consumer mobile app use. | **Internal benchmark studies.** Evaluated on static clinical vignettes created by doctors, not live patient outcomes. | **Manual dataset curation.** Feedback is aggregated periodically by medical directors to update Bayesian priors. | **No.** Suggests user visit a clinic, but cannot track whether user actually attended or survived. | Severe loss-to-follow-up (> 90% of app users never complete the follow-up survey); prone to massive volunteer response bias. | **Grade A** (Nature Digital Medicine, 2020) |
| **Ambient AI Scribes (Nuance DAX, Abridge, Suki)** | **No.** Scribe software terminates at the point of signed progress note in the EHR. | **Yes (Text edits).** Scribe records how many words or sentences the physician edited before signing. | **Yes (Documentation accuracy).** Tracks word error rate (WER) and doctor editing time; **does NOT evaluate patient health outcomes**. | **Fine-tuning on text edits.** Vendor uses physician text corrections to improve future speech-to-text models. | **No.** Scribe creates referral letter text; does not monitor whether the transfer took place. | Optimizes for physician convenience and billing accuracy rather than clinical outcomes or diagnostic safety. | **Grade B** (Abridge & Nuance Whitepapers, 2024) |
| **Diagnostic Radiology AI (Aidoc, Viz.ai, RapidAI)** | **Yes (High in Stroke/Bleed).** Tracks whether CT findings correlated with surgical thrombectomy or craniotomy. | **Yes.** Radiologist clicks "Agree" or "Disagree" with AI bounding box annotation. | **Yes.** Continuous quality assurance dashboards track false positive and false negative rates. | **Periodic model re-training.** Vendor releases versioned updates (e.g., v2.1) following FDA clearance. | **Yes (Stroke networks).** Viz.ai coordinates acute ischemic stroke transfers across hub-and-spoke hospitals. | Highly specialized point solutions for neurovascular and trauma imaging; completely absent from general outpatient and PHC workflows. | **Grade A** (Radiology AI Clinical Impact Audits, 2023) |

---

## 3. The Broken Clinical Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE UNCLOSED CLINICAL AI FEEDBACK LOOP                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CURRENT CLINICAL PRACTICE:                                                 │
│                                                                             │
│  AI Recommendation ────> Doctor Overrides ────> Patient Discharged          │
│         │                      │                          │                 │
│         ▼                      ▼                          ▼                 │
│   (Logged in DB)       (Dismiss Button)            (Outcome Lost)           │
│                                                           │                 │
│  • The hospital has NO IDEA whether the overridden patient:                 │
│    - Fully recovered at home,                                               │
│    - Died 12 hours later of septic shock, or                                │
│    - Was admitted to an ICU in a neighboring district.                      │
│                                                                             │
│  • The AI model continues offering the exact same flawed advice forever     │
│    because the real-world consequence is completely invisible!              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Why Existing Systems Fail to Close the Loop
1. **The Cross-Facility Chasm:** If a patient triaged at a rural PHC is referred to a District Hospital, the PHC doctor almost never receives a discharge summary or mortality report. The PHC has zero way of knowing if their initial triage assessment was accurate.
2. **The Autonomous Feedback Danger:** Clinical AI systems **must not execute autonomous online learning in production**. If an AI immediately updates its weights every time a single doctor disagrees, a single idiosyncratic clinician could poison the model for the entire hospital network, introducing catastrophic errors.

---

## 4. The CLINOVA Two-Tier Closed-Loop Architecture

CLINOVA solves this through a **two-tier architecture** that closes the feedback loop while preserving absolute clinical safety:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CLINOVA TWO-TIER FEEDBACK ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TIER 1: PATIENT-LEVEL LONGITUDINAL UPDATE (Immediate & Safe)               │
│  When patient outcome is recorded (Recovery, Complication, Transfer):       │
│  • Active CAREGRAPH instance transitions to RESOLVED.                       │
│  • Clinical outcome is appended to synthetic Master Case history.           │
│  • Closes encounter without modifying core algorithmic weights.             │
│                                                                             │
│  TIER 2: SYSTEM CALIBRATION & RESEARCH BENCHMARK (Batch & Governed)         │
│  Clinician overrides and ground-truth outcomes propagate to SIGNALGRAPH:    │
│  • Computes Brier score, calibration curve, and Discordance Rate.           │
│  • Generates de-identified evaluation datasets for researcher audits.       │
│  • Future fine-tuning (LoRA / PEFT) occurs strictly OFFLINE in Phase 3/4    │
│    under clinical review committee supervision!                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Granular Outcome Taxonomy
Outcomes are categorized into six standardized operational states (`DOC-17`):
1. `FULL_RECOVERY`: Complete resolution; validates low-risk triage specificity.
2. `STABILIZED`: Controlled chronic condition; confirms routine outpatient pathway.
3. `COMPLICATION_MANAGED`: Secondary complication caught early; validates trajectory warning sensitivity.
4. `REFERRED_HIGHER`: Planned tertiary transfer; validates FACILITYGRAPH capability matching.
5. `CRITICAL_TRANSFER`: Unplanned emergency crash; triggers failure review of initial intake triage.
6. `ADVERSE_EVENT`: Unexpected deterioration or mortality; **mandatory high-priority audit trigger**.

---

## 5. Audit Conclusion on Outcome Loops

- **Novelty Classification:** **CATEGORY C (Meaningful Integration)** with a **CATEGORY D Research Framework**.
- **Defensible Value:** CLINOVA does **not** perform dangerous real-time weight adaptation. It establishes an immutable, auditable provenance loop where clinician decisions and real outcomes are structured into a standardized evaluation dataset, enabling measurable model calibration and healthcare quality assurance.
