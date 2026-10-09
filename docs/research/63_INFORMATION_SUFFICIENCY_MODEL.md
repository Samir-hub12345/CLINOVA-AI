# CLINOVA AI — Information Sufficiency Model & Decision Calculus

> **Document ID:** `RES-63`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Epistemic Foundations & The Zero-Imputation Law

In clinical medicine, automated systems frequently suffer from **automation bias** and **hallucinatory completeness**—assuming that because an electronic form lacks a recorded symptom or vital sign, the patient is healthy and free of disease.

CLINOVA AI establishes the **Epistemic Information Sufficiency Model**, anchored in two absolute clinical laws:

1. **The Inviolable Law of Clinical Gaps:**  
   $$\mathbf{Absence\ of\ evidence\ is\ NEVER\ evidence\ of\ absence.}$$
   If a vital sign, laboratory test, or clinical history element is missing, the system MUST permanently designate it as `UNKNOWN`. Under NO circumstances shall the platform impute a normal value, assume a negative finding, or calculate a false reassurance score based on absent data.

2. **The Epistemic Uncertainty Mandate ($U_t$):**  
   Diagnostic and triage certainty is dynamically discounted as a mathematical function of missing critical evidence:
   $$U_t = 1.0 - \frac{\sum_{i=1}^N w_i \cdot \mathbb{I}(\text{param}_i \in \{\text{KNOWN}, \text{VERIFIED}\})}{\sum_{i=1}^N w_i}$$
   When uncertainty $U_t \ge 0.50$, the system is strictly prohibited from asserting definitive low-acuity classifications.

---

## 2. Six Operational Sufficiency Decision States

The system evaluates incoming patient information and categorizes the encounter into one of **six explicit sufficiency states**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIX SUFFICIENCY DECISION STATES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ 1. SUFFICIENT ] ─────────────────> Critical vitals & red flags verified. │
│                                       Proceeds directly to consolidation.   │
│                                                                             │
│  [ 2. PARTIALLY SUFFICIENT ] ───────> Core complaint clear; non-critical    │
│                                       parameters absent. Triggers follow-up.│
│                                                                             │
│  [ 3. INSUFFICIENT ] ───────────────> Critical vitals missing (BP, SpO2).   │
│                                       Routes to Nurse Point-of-Care Desk.   │
│                                                                             │
│  [ 4. CONFLICTING ] ────────────────> Incompatible cross-modal claims.      │
│                                       Requires mandatory staff verification.│
│                                                                             │
│  [ 5. UNRELIABLE ] ─────────────────> Low-confidence OCR or mumbled audio.  │
│                                       Requires human physical review.       │
│                                                                             │
│  [ 6. EMERGENCY-OVERRIDDEN ] ───────> Acute life threat detected.           │
│                                       All sufficiency gates bypassed.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specification of Sufficiency States

### 1. `SUFFICIENT`
- **Definition:** The encounter possesses complete objective data across all critical red flags and vital signs, alongside a coherent clinical timeline and medication history.
- **Sufficiency Score:** $S \ge 0.85$ AND Critical Gap Count = 0.
- **Allowed Action:** Case proceeds directly to **Data Consolidation** and **CAREGRAPH Synthesis** without intermediate nursing intervention.
- **Safety Boundary:** The patient is placed in the Doctor Queue; clinician still performs mandatory review.

### 2. `PARTIALLY SUFFICIENT`
- **Definition:** The patient has provided a clear chief complaint and basic history, but secondary important parameters (e.g., exact fever duration, past medication dosages, previous allergy history) are absent.
- **Sufficiency Score:** $0.65 \le S < 0.85$ with NO critical red-flag gaps.
- **Allowed Action:** Triggers the **Follow-Up Question Engine** to ask 1–3 targeted multiple-choice questions in the patient's vernacular language.
- **Next Step:** If patient answers resolve the gaps, advances to `SUFFICIENT`; if unanswered or skipped, routes to staff triage.

### 3. `INSUFFICIENT`
- **Definition:** Critical physiological parameters (Blood Pressure, SpO2, Pulse Rate, Respiratory Rate) or cardinal red-flag questions are completely absent.
- **Sufficiency Score:** $S < 0.65$ OR any Critical Parameter is `UNKNOWN`.
- **Allowed Action:** The case CANNOT proceed to doctor review or automated triage.
- **Mandatory Routing:** The system assigns the case to the **Staff Missing-Data Worklist** (`STATE_STAFF_DATA_PENDING`). A triage nurse or health worker must physically measure and input the missing vitals using calibrated instruments.

### 4. `CONFLICTING`
- **Definition:** Mutually incompatible claims exist across modalities or historical records.
  - *Example 1:* Patient audio transcript states: *"Fever began yesterday"*, while uploaded doctor prescription shows: *"Amoxicillin prescribed 10 days ago for severe fever"*.
  - *Example 2:* Uploaded lab slip shows Blood Glucose = $450\text{ mg/dL}$, while patient questionnaire states *"No history of diabetes"*.
- **Sufficiency Score:** Undefined (Conflict flag overrides mathematical score).
- **Mandatory Routing:** The system flags the parameter with a prominent high-contrast yellow `CONFLICTING` badge. Requires mandatory human staff verification and clinical adjudication on the Doctor Workbench.

### 5. `UNRELIABLE`
- **Definition:** Information is present but extracted with low algorithmic confidence:
  - Speech transcription confidence $< 0.60$ (heavy background noise, whispering, overlapping voices).
  - OCR document recognition confidence $< 0.70$ (blurred mobile photo, torn prescription slip, illegible cursive).
  - Patient self-reports an extreme, physiologically improbable value (e.g., Pulse = 300 bpm, SpO2 = 15% in a conscious talking patient).
- **Mandatory Routing:** The entity is preserved with an `UNRELIABLE` tag. The interface displays the raw image snippet or audio crop side-by-side and requires frontline nursing or doctor confirmation before incorporation into CAREGRAPH.

### 6. `EMERGENCY-OVERRIDDEN`
- **Definition:** The patient presents with acute physiological collapse ($\text{SpO}_2 < 85\%$, $\text{Shock Index} > 1.0$, pediatric stridor, active arterial hemorrhage, GCS $< 13$).
- **Operational Rule:** **ALL INFORMATION SUFFICIENCY GATES ARE INSTANTLY SUSPENDED.**
- **Mandatory Action:** The case immediately jumps to `STATE_EMERGENCY_ACTIVE`. The system does NOT wait for missing medical history, does not prompt follow-up questions, and does not require demographic verification. Resuscitation proceeds instantly.

---

## 4. Parameter Stratification & Clinical Weighting Matrix

To compute the Sufficiency Metric ($S$), clinical parameters are stratified into three rigid tiers:

$$\mathbf{S} = \frac{\sum_{i=1}^{M_{\text{crit}}} 3.0 \cdot \delta_i + \sum_{j=1}^{M_{\text{imp}}} 1.5 \cdot \delta_j + \sum_{k=1}^{M_{\text{opt}}} 0.5 \cdot \delta_k}{\sum 3.0 + \sum 1.5 + \sum 0.5}, \quad \delta \in \{0, 1\}$$

| Parameter Tier | Weight ($w$) | Clinical Elements | Missing Consequence |
| :--- | :---: | :--- | :--- |
| **Tier 1: CRITICAL** | **3.0** | • Blood Pressure (Systolic & Diastolic)<br>• Oxygen Saturation ($\text{SpO}_2$)<br>• Heart Rate / Pulse<br>• Respiratory Rate<br>• Severe Chest Pain / Radiation<br>• Active Bleeding / Shock Signs<br>• Pregnancy Status (Reproductive Female)<br>• Severe Anaphylaxis / Drug Allergy | **HARD BLOCK:** Case cannot reach doctor queue without Staff Point-of-Care Vitals. If abnormal, triggers emergency escalation. |
| **Tier 2: IMPORTANT** | **1.5** | • Chief Complaint duration and onset<br>• Exact temperature reading<br>• Current active prescription medications<br>• Comorbidities (Diabetes, Hypertension, CAD)<br>• Associated symptoms (vomiting, dysuria)<br>• Functional status / mobility | **SOFT BLOCK:** Triggers 1–3 targeted vernacular follow-up questions. If unanswered, flagged on doctor review screen. |
| **Tier 3: OPTIONAL** | **0.5** | • Family medical history of non-acute illness<br>• Occupational history<br>• Non-acute surgical history ($>5$ years prior)<br>• Dietary and lifestyle habits | **NO BLOCK:** Displayed as unknown; does not interrupt triage progression. |

---

## 5. Clinical Action Routing Matrix

Based on the evaluated information state, the system executes deterministic routing behaviors:

| Clinical Information State | Automated System Response | Mandatory Human Actor | Permitted Next State |
| :--- | :--- | :--- | :--- |
| **`SUFFICIENT`** | Compiles Master Clinical Report; computes CAREGRAPH vector. | Registered Medical Practitioner (`ROLE_CLINICIAN`) | `STATE_CONSOLIDATED` $\to$ `STATE_DOCTOR_QUEUED` |
| **`PARTIALLY_SUFFICIENT`** | Generates 1–3 Next-Best-Information questions. | Patient / Caregiver (`ROLE_PATIENT`) | `STATE_FOLLOW_UP_PENDING` |
| **`INSUFFICIENT`** | Blocks queue promotion; creates nursing task item. | Triage Nurse (`ROLE_NURSE`) | `STATE_STAFF_DATA_PENDING` |
| **`CONFLICTING`** | High-contrast visual conflict banner; side-by-side snippet preview. | Nurse or Attending Doctor | `STATE_EXTRACTION_REVIEW` / `STATE_DOCTOR_REVIEWING` |
| **`UNRELIABLE`** | Watermarks entity as unverified; requires manual re-entry. | Triage Nurse (`ROLE_NURSE`) | `STATE_STAFF_DATA_PENDING` |
| **`EMERGENCY_OVERRIDDEN`** | Bypasses all documentation; initiates 30s ABCD vitals. | Emergency Casualty Team | `STATE_EMERGENCY_ACTIVE` |
