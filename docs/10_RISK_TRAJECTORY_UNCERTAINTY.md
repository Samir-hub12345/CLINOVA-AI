# CLINOVA AI — Risk Stratification, Trajectory & Uncertainty Model

> **Document ID:** `DOC-10`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Principles of Explainable Clinical Risk

### 1.1 The Anti-Black-Box Law
> **Core Architectural Law:** Risk must NEVER be displayed as an arbitrary, unexplained percentage (e.g., *"Patient Risk: 87.4%"*).
>
> In real clinical medicine, an unexplained percentage is dangerous and unusable. Clinicians need to know **why** risk is elevated, **what evidence** triggered the elevation, **which trajectory** the patient is following, **what information is missing**, and **what concrete action** should be taken next.

### 1.2 The Standard Clinical Risk Display Contract
Every risk assessment in CLINOVA AI must communicate the mandatory six-part tuple:

$$\mathbf{Risk\ Tuple} = \langle \mathbf{CURRENT\ RISK},\ \mathbf{REASON},\ \mathbf{EVIDENCE},\ \mathbf{TRAJECTORY},\ \mathbf{UNCERTAINTY},\ \mathbf{NEXT\ ACTION} \rangle$$

#### Canonical UI Representation:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLINICAL STATUS CARD                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Risk Level:          HIGH PRIORITY (Red Flag Warning)                      │
│  Acuity Trajectory:   WORSENING (Pulse rising, BP narrowing over 45 mins)   │
│  Evidence Confidence: MODERATE (0.76 — Partial Point-of-Care Data)          │
├─────────────────────────────────────────────────────────────────────────────┤
│  KNOWN EVIDENCE                                                             │
│  • Verified SBP: 88 mmHg (Hypotension confirmed by Nurse Desk at 10:14 AM) │
│  • Verified Heart Rate: 124 bpm (Tachycardia confirmed)                     │
│  • Lab Extraction: Platelets 42,000/μL (CBC report verified from District Lab)│
├─────────────────────────────────────────────────────────────────────────────┤
│  UNKNOWN (INFORMATION GAPS)                                                 │
│  • Missing Critical Vital: Postural dizziness / Capillary refill time       │
│  • Missing History: Day of fever onset vs rash appearance                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  CONFLICTING EVIDENCE                                                       │
│  • Patient reports fever for 2 days; uploaded prescription slip shows        │
│    antibiotics prescribed 10 days ago                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  RECOMMENDED NEXT ACTION (ADVISORY ONLY)                                    │
│  • VERIFY missing capillary refill & obtain immediate IV access             │
│  • Screen for Dengue Shock Syndrome protocol                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Acuity Trajectory Modeling

Human physiology is dynamic. A single normal vital reading during intake can create false reassurance in a deteriorating patient. CLINOVA models trajectory longitudinally across serial observations.

### 2.1 The Four Trajectory States
1. $\mathbf{WORSENING}$:
   - Physiological criteria: Shock Index ($HR / SBP$) climbing $> 0.9$; SpO2 dropping $> 3\%$ over serial measurements; MEWS score increasing by $\ge 2$ points; respiratory rate accelerating $> 28$ bpm.
   - Action trigger: Triggers automated bedside review alert and escalates case priority in the Doctor Queue.
2. $\mathbf{STABLE}$:
   - Physiological criteria: Vital signs remain within physiological tolerances ($\pm 10\%$ delta) without escalating oxygen requirement or pain progression.
   - Action trigger: Maintains scheduled queue position.
3. $\mathbf{IMPROVING}$:
   - Physiological criteria: Normalization of vitals post-intervention (e.g., HR drops from 120 to 88 following IV hydration; SpO2 recovers to $98\%$ on room air).
   - Action trigger: Prompts clinician consideration for routine step-down or discharge planning.
4. $\mathbf{UNKNOWN}$:
   - Physiological criteria: Exactly one vital snapshot present; zero longitudinal temporal delta exists.
   - Action trigger: Prompts staff for repeat measurement within 30–60 minutes to establish trajectory.

### 2.2 Trajectory Derivation Mathematical Model
Given time-stamped observations $S(t_1)$ and $S(t_2)$ where $\Delta t = t_2 - t_1 \ge 15 \text{ mins}$:
$$\Delta \mathbf{Acuity} = w_1 \Delta \text{ShockIndex} + w_2 \Delta \text{SpO}_2^{-1} + w_3 \Delta \text{MEWS} + w_4 \Delta \text{GCS}^{-1}$$
$$\text{Trajectory} = \begin{cases} 
\text{WORSENING} & \text{if } \Delta \mathbf{Acuity} > +\theta_{\text{worsen}} \\
\text{IMPROVING} & \text{if } \Delta \mathbf{Acuity} < -\theta_{\text{improve}} \\
\text{STABLE} & \text{if } |\Delta \mathbf{Acuity}| \le \epsilon \\
\text{UNKNOWN} & \text{if } \text{Count}(\text{Snapshots}) < 2
\end{cases}$$

---

## 3. Uncertainty as a First-Class Clinical Object

In clinical decision support, what the system **does not know** is just as critical as what it **does know**. Ignoring uncertainty leads to dangerous algorithmic overconfidence.

### 3.1 Dimensions of Uncertainty
For every patient case, the system explicitly computes and renders:
1. **What is Known:** Complete, high-confidence, verified clinical parameters.
2. **What is Unknown:** Essential diagnostic inputs that have not been provided or measured.
3. **What is Conflicting:** Incompatible values across modalities (e.g., speech says "no allergies", but uploaded slip lists "penicillin allergy").
4. **What is Unreliable:** Low-confidence OCR extractions (e.g., smudged lab numbers with confidence $< 0.65$) or muffled speech transcripts.
5. **What is Inferred:** AI-derived clinical entities awaiting licensed clinician verification.
6. **Why Uncertainty Exists:** Explicit plain-language explanation (e.g., *"Uncertainty is high because patient could not report symptom duration and no blood pressure was recorded"*).
7. **How to Reduce Uncertainty:** The concrete diagnostic step that would resolve the ambiguity.

### 3.2 Confidence Metric Rules
- Every displayed confidence score must link to a defined, mathematically grounded derivation (e.g., OCR character recognition probability, acoustic model phoneme confidence, or deterministic completeness index).
- Synthetic or arbitrary random numbers are strictly forbidden.

---

## 4. Next-Best Information (NBI) Engine

When clinical uncertainty is elevated, the Next-Best Information Engine identifies the single highest-yield diagnostic parameter needed to collapse uncertainty and secure the care pathway.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NEXT-BEST INFORMATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ CURRENT CLINICAL STATE ]                                                │
│               │                                                             │
│               ▼                                                             │
│   [ UNCERTAINTY PROFILE: Gaps & Contradictions Identified ]                 │
│               │                                                             │
│               ▼                                                             │
│   [ CANDIDATE INFORMATION POOL: What could we measure or ask? ]             │
│               │                                                             │
│               ▼                                                             │
│   [ VALUE-OF-INFORMATION RANKING: Which input resolves the most risk? ]     │
│               │                                                             │
│               ▼                                                             │
│   [ ACTIONABLE NBI TARGET: "Measure SpO2" or "Ask for chest pain radiation"]│
│               │                                                             │
│               ▼                                                             │
│   [ UPDATE STATE: Convert UNKNOWN to KNOWN, Re-stratify Risk ]              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Value-of-Information (VOI) Ranking
The NBI engine ranks information gaps using a clinical utility function:
$$\text{VOI}(g_i) = \text{RiskSeverity}(\text{Syndrome}) \times \text{DiagnosticSensitivity}(g_i) \times \frac{1}{\text{AcquisitionBurden}(g_i)}$$
- A non-invasive, 15-second vital measurement (e.g., Pulse Oximetry) has near-zero acquisition burden and massive diagnostic sensitivity in dyspneic patients, giving it top priority.
- A complex, expensive CT scan has higher burden and is suggested only when basic physiological stabilization is confirmed.
