# CLINOVA AI — ORCHESTRATION Engine Gap Audit & Synthesis Defensibility

> **Document ID:** `RES-13`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Highest-Priority Audit Mandate

The **ORCHESTRATION Engine** represents the core synthesis brain of CLINOVA AI. Phase 1 proposed a definitive unified orchestration model:

$$\begin{aligned}
&\Big(\mathbf{Patient\ State} + \mathbf{Evidence\ Quality} + \mathbf{Risk} + \mathbf{Trajectory} + \mathbf{Uncertainty} \\
&\quad + \mathbf{Facility\ Capability} + \mathbf{Facility\ Capacity} + \mathbf{System\ Context}\Big) \\
&\Longrightarrow \Big[\mathbf{ASK}\ |\ \mathbf{VERIFY}\ |\ \mathbf{CONTINUE}\ |\ \mathbf{OBSERVE}\ |\ \mathbf{ESCALATE}\ |\ \mathbf{REFER}\Big]
\end{aligned}$$

This audit tests whether this complete multi-factor model exists anywhere in commercial healthcare technology or academic literature. It audits:
1. "Next-Best-Action" (NBA) algorithms in clinical medicine.
2. Clinical autonomous agents and LLM care pathway planners.
3. Resource-aware Clinical Decision Support Systems (CDSS).
4. Adaptive clinical workflow orchestration.

---

## 2. Adversarial Mapping: Do Existing Systems Execute this Synthesis?

| System / Domain | What is Synthesized? | What is Generated? | How Decisions are Made | Missing Factors from the CLINOVA Equation | Novelty Classification |
|:---|:---|:---|:---|:---|:---|
| **Commercial CDSS (UpToDate, Isabel, DXplain)** | Patient symptoms, signs, laboratory values, age, sex. | Differential diagnosis list, recommended diagnostic tests. | Knowledge-base ontology matching; rule-based guidelines. | **Completely blind to facility capacity, equipment, blood banks, and queue wait times.** Recommends tests regardless of whether the local lab can perform them. | **Category A:** Diagnostic recommendation is established; **resource feasibility is completely absent**. |
| **Enterprise Clinical Next-Best-Action (Optum, Pega Healthcare)** | Health insurance claims, historical EHR diagnosis codes, gaps in care. | Recommended preventative screenings (e.g., mammogram due, HbA1c test needed). | Predictive machine learning models trained on payer claims. | **Acute physiological trajectory and emergency facility capabilities.** Designed for outpatient health maintenance and payer cost management; **not for acute emergency intake**. | **Category A / B:** Outpatient payer NBA is common; **absent in acute emergency triage**. |
| **Agentic Clinical LLMs (Research: Med-PaLM 2, AgentClinic, CoAuthor)** | Free-text clinical dialogue or multi-turn patient vignette. | Conversational response, simulated diagnosis, treatment plan. | Autoregressive LLM generation with Chain-of-Thought (CoT) prompting. | **Rigid deterministic red-flag boundaries, verified evidence provenance, live bed capacity.** Vulnerable to catastrophic hallucinations; lacks grounded institutional constraints. | **Category D:** Active academic research frontier; **lacks deterministic safety invariants for production healthcare**. |
| **Hospital ED Operations Orchestration (Qventus, LeanTaaS)** | Bed turnaround times, pending lab orders, transport delays. | Prioritized task alerts for charge nurses (e.g., "Expedite MRI for Bed 12"). | Predictive queuing models and EHR status event triggers. | **Individual clinical diagnostic reasoning and explicit uncertainty quantification.** Focuses strictly on administrative throughput efficiency rather than clinical safety. | **Category B:** Operational task alerting is established; **decoupled from patient physiological diagnostic uncertainty**. |

---

## 3. The Definitive Grill: Does the Complete Combination Exist?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE 8-FACTOR ORCHESTRATION EQUATION GRILL                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FACTOR 1: Patient Clinical State       ───> Solved by EHRs & CDSS          │
│  FACTOR 2: Evidence Quality Provenance  ───> Solved by Abridge (audio only) │
│  FACTOR 3: Acute Physiological Risk     ───> Solved by NEWS2 / ESI          │
│  FACTOR 4: Longitudinal Trajectory      ───> Solved in ICUs (absent in OPD) │
│  FACTOR 5: Epistemic Uncertainty        ───> Solved in Academic Papers (UQ) │
│  FACTOR 6: Facility Clinical Capability ───> Solved by Transfer Nurses      │
│  FACTOR 7: Real-Time Bed/Queue Capacity ───> Solved by Operations Telemetry │
│  FACTOR 8: System Epidemiological Surge ───> Solved by Public Health (IHIP) │
│                                                                             │
│  THE FINDING:                                                               │
│  Individually, all 8 factors have existing academic or commercial solutions.│
│                                                                             │
│  HOWEVER:                                                                   │
│  There is NOT A SINGLE DEPLOYED HEALTHCARE SYSTEM IN THE WORLD that synthesizes│
│  all 8 factors simultaneously into candidate next clinical actions          │
│  [ASK / VERIFY / CONTINUE / OBSERVE / ESCALATE / REFER]                     │
│  at the point of frontline clinical intake!                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Why Existing Systems Remain Siloed
1. **Commercial Payer Silos:** Pega and Optum build NBA engines for insurance companies to prompt mammograms, not to triage hemorrhagic dengue in a rural clinic.
2. **Academic AI Benchmark Silos:** Academic AI researchers benchmark models on static question-answering benchmarks (USMLE, MedQA) rather than real-world messy workflow orchestration under missing data and resource constraints.
3. **Operational Silos:** Hospital IT vendors sell bed management software to the Chief Operating Officer and clinical documentation software to the Chief Medical Officer—and the two software suites **never share state**.

---

## 4. The Six Action Categories Grounded in Reality

CLINOVA's six orchestration outputs are **not generic suggestions**; they are strictly mapped to operational clinical protocols:

| Action Category | System Behavior & Clinical Rationale | Governing Invariant |
|:---|:---|:---|
| **`ASK`** | Prompts 1–3 high-yield questions via Next-Best Information (NBI) engine when critical data is `UNKNOWN`. | Cannot ask more than 3 questions (prevents patient cognitive fatigue). |
| **`VERIFY`** | Triggers bedside staff re-measurement when conflicting data or extreme physiological outliers occur. | Blocks automatic queue placement until clinician confirms extreme vital sign. |
| **`CONTINUE`** | Confirms routine outpatient management when risk is low, trajectory is stable, and local facility is capable. | Issues structured draft consultation note for physician review. |
| **`OBSERVE`** | Directs patient to short-stay observation bay with mandatory serial vital check in 30–60 minutes. | Escalates queue priority if reassessment vitals are overdue by > 30 minutes. |
| **`ESCALATE`** | Flashes emergency red alert on doctor queue; sounds workstation chime; triggers immediate bedside review. | Deterministic red flags (`TRIAGE-R01` to `TRIAGE-R06`) enforce instant escalation regardless of LLM output. |
| **`REFER`** | Filters regional network via FACILITYGRAPH; matches nearest capable hospital; compiles structured transfer file. | Blocks referral to facilities with zero open ICU beds or offline critical diagnostics. |

---

## 5. Audit Conclusion on Orchestration

- **Novelty Classification:** **CATEGORY C (Meaningful Combination / Integration)** at the architectural level, with a genuine **CATEGORY D / E Research Contribution** in formulating the mathematical objective function:
  $$\mathbf{Pathway} = \operatorname{ArgMin}_{P \in \mathcal{P}} \Big( \mathbf{RiskLoss}(P) + \mathbf{UncertaintyPenalty}(P) + \mathbf{FeasibilityFriction}(P) \Big)$$
- **Defensible Value:** The Orchestration Engine does **not** replace the physician's clinical judgment. It acts as an **intelligent safety and feasibility filter**, ensuring that before the doctor commits to an action, all clinical risks, missing evidence gaps, and institutional resource constraints have been surfaced and accounted for.
