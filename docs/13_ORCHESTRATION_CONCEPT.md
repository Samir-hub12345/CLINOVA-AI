# CLINOVA AI — ORCHESTRATION Engine & Care Pathway Synthesis

> **Document ID:** `DOC-13`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. What is the ORCHESTRATION Engine?

> **Core Definition:** The ORCHESTRATION Engine is the decision-synthesis core of CLINOVA AI.
>
> It continuously unifies patient-level clinical state (`CAREGRAPH`), evidence reliability and uncertainty, facility feasibility (`FACILITYGRAPH`), and macro-level operational context (`SIGNALGRAPH`) to answer the definitive question:
> $$\mathbf{WHAT\ IS\ THE\ SAFEST\ ACHIEVABLE\ NEXT\ CARE\ ACTION?}$$
>
> **The System Recommends. The Qualified Clinician Decides.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION SYNTHESIS CORE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────┐       │
│   │         CAREGRAPH         │         │       FACILITYGRAPH       │       │
│   │ Clinical State, Vitals,   │         │ Capability, Bed Capacity, │       │
│   │ Trajectory, Risk Band     │         │ On-duty Specialists       │       │
│   └─────────────┬─────────────┘         └─────────────┬─────────────┘       │
│                 │                                     │                     │
│                 ├──────────────────┬──────────────────┤                     │
│                 ▼                  ▼                  ▼                     │
│          [ UNCERTAINTY ]    [ ORCHESTRATION ]   [ SIGNALGRAPH ]             │
│          Gaps, Conflicts,   [  SYNTHESIS    ]   Network Demand,             │
│          Unreliable Points  [    ENGINE     ]   Epidemic Surges             │
│                 ▲                  ▲                  ▲                     │
│                 │                  │                  │                     │
│                 └──────────────────┼──────────────────┘                     │
│                                    ▼                                        │
│                      [ CANDIDATE ACTION CATEGORIES ]                        │
│                      ├── ASK      (Prompt for missing high-value data)      │
│                      ├── VERIFY   (Confirm conflicting / extreme readings)  │
│                      ├── CONTINUE (Maintain active outpatient care plan)    │
│                      ├── OBSERVE  (Short-stay monitoring & serial vitals)   │
│                      ├── ESCALATE (Immediate bedside doctor / OT alert)     │
│                      └── REFER    (Feasibility-verified hospital transfer)  │
│                                    │                                        │
│                                    ▼                                        │
│                   ┌──────────────────────────────────┐                      │
│                   │  THE SAFEST ACHIEVABLE CARE      │                      │
│                   │             PATHWAY              │                      │
│                   │ (Qualified, Explainable Advisory)│                      │
│                   └────────────────┬─────────────────┘                      │
│                                    │                                        │
│                                    ▼                                        │
│                   ┌──────────────────────────────────┐                      │
│                   │     MANDATORY CLINICIAN GATE     │                      │
│                   │ (Accept, Modify, Override, Sign) │                      │
│                   └──────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Naming Invariant: "The Safest Achievable Care Pathway"

> **Architectural Law:** The output of the Orchestration Engine must NEVER be labeled as *"The AI's Diagnosis"*, *"The Final Answer"*, or *"Automated Care Plan"*.
>
> The output is strictly termed:
> $$\mathbf{THE\ SAFEST\ ACHIEVABLE\ NEXT\ CARE\ PATHWAY}$$
>
> This terminology reinforces the two essential realities of clinical decision support:
> 1. It is **safety-first** rather than diagnostically definitive.
> 2. It is **achievable** within the physical capability and capacity constraints of the accessible healthcare network.

---

## 3. Six Action Categories

Every orchestration candidate action maps to one of six standardized categories:

| Action Category | Operational Definition | Clinical Trigger | System Behavior |
| :--- | :--- | :--- | :--- |
| `ASK` | Target high-value information gaps to collapse clinical uncertainty. | Critical parameters absent ($U_{\text{critical}} > 0$); patient can provide input. | Generates targeted follow-up question via Next-Best Information engine. |
| `VERIFY` | Resolve contradictory findings or confirm extreme vital measurements. | Conflicting data across sources; extreme vital values (e.g., SBP 60 mmHg). | Displays conflict callout; prompts staff to re-measure and sign off. |
| `CONTINUE` | Maintain current routine outpatient trajectory. | Low acute risk; stable trajectory; complete evidence; local facility capable. | Generates routine consultation note and follow-up calendar reminder. |
| `OBSERVE` | Retain patient for serial vital monitoring and short-stay evaluation. | Intermediate risk; trajectory is stable but high uncertainty or borderline vitals. | Schedules repeat vitals in 30–60 minutes in triage observation bay. |
| `ESCALATE` | Trigger instant bedside clinician intervention or immediate surgical handoff. | Red-flag danger sign; worsening trajectory; shock criteria; panic lab value. | Flashes emergency alert on Doctor Queue; triggers audible workstation alarm. |
| `REFER` | Coordinate inter-facility transfer to a capable receiving hospital. | Care requirement exceeds local facility capability or ICU capacity exhausted. | Filters network via FACILITYGRAPH, selects nearest capable hospital, prepares referral file. |

---

## 4. Care Pathway Evaluation Function

The Orchestration Engine synthesizes the pathway using an explainable multi-factor evaluation function:

$$\mathbf{Pathway} = \operatorname{ArgMin}_{P \in \mathcal{P}} \Big( \mathbf{RiskLoss}(P) + \mathbf{UncertaintyPenalty}(P) + \mathbf{FeasibilityFriction}(P) \Big)$$

Where:
- $\mathbf{RiskLoss}(P)$: Evaluates the potential physiological danger of delaying action (e.g., waiting in OPD vs. immediate resuscitation).
- $\mathbf{UncertaintyPenalty}(P)$: Penalizes premature definitive dispositions when critical diagnostic parameters remain unknown.
- $\mathbf{FeasibilityFriction}(P)$: Evaluates whether the facility has the open beds, blood bank stock, and on-duty specialists required by pathway $P$.

---

## 5. Clinician Governance & Human-in-the-Loop Mandate

The Orchestration Engine never executes actions autonomously:
1. **Explainable Rationale:** Every recommendation displays the explicit evidence nodes, uncertainty considerations, and facility resource checks that justified the recommendation.
2. **Reviewer Override:** The clinician can accept the recommended pathway, select an alternative pathway, or enter an entirely custom disposition.
3. **Audit Justification:** If a clinician overrides a safety recommendation (e.g., discharging a patient flagged as `HIGH_RISK_WORSENING`), the system requires entering a mandatory clinical rationale (`CLINICAL_JUDGMENT_OVERRIDE`), permanently committed to the immutable audit trail.
