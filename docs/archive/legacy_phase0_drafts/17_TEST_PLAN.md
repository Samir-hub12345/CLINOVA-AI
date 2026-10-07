# CLINOVA AI — Comprehensive Master Test Plan

> **Document ID:** `DOC-17`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Testing Philosophy & Verification Standard

Testing in CLINOVA AI is not an afterthought; it is a **continuous verification contract**. 
- No feature is marked complete based on visual rendering alone.
- Every clinical scenario must execute through the full application stack:
  $$\text{Intake API} \longrightarrow \text{CareGraph} \longrightarrow \text{FacilityGraph} \longrightarrow \text{Orchestration} \longrightarrow \text{Clinician Gate} \longrightarrow \text{SignalGraph}$$
- Tests must assert on actual state transitions, mathematical delta calculations, and data provenance.

---

## 2. Test Pyramid & Execution Tiers

```
           / \
          /   \     E2E Browser Scenarios (Playwright / Chromium)
         / E2E \    - Full clinical journeys (Intake to Outcome)
        /───────\
       /         \    Integration & Scenario Tests (pytest + httpx)
      /  Scenario \   - 17 Mandatory Clinical Scenarios
     /─────────────\
    /               \   Unit Tests (pytest)
   /      Unit       \  - Acuity calculation, Trajectory delta,
  /───────────────────\   Uncertainty score, Feasibility matching
```

---

## 3. The 17 Mandatory Clinical Test Scenarios

| Scenario ID | Clinical Persona / Condition | Key Test Characteristics & Assertions | Expected Final State |
| :--- | :--- | :--- | :--- |
| **SCEN-01** | **Routine Ambulatory Case** | Young adult with mild seasonal coryza; normal vitals ($R_t = 0.05$). | Action: `CONTINUE` -> Discharged |
| **SCEN-02** | **Urgent Non-Critical Case** | Middle-aged adult with high fever ($39^\circ\text{C}$), stable vitals ($R_t = 0.35$). | Action: `OBSERVE` -> Serial vitals scheduled |
| **SCEN-03** | **Critical Resuscitation Case** | Polytrauma patient with severe hypotension (BP 70/40, HR 140, $R_t = 0.90$). | Action: `ESCALATE` -> Emergency Resuscitation alert |
| **SCEN-04** | **Incomplete Information Case** | Vague chest discomfort; no onset time, no cardiac history ($\mathcal{U}_t = 0.65$). | State: `INSUFFICIENT_DATA` -> Action: `ASK` |
| **SCEN-05** | **Conflicting Evidence Case** | Verbal narrative reports "asymptomatic", but pulse oximeter shows SpO2 $82\%$. | State: `CONFLICTING_DATA` -> Action: `VERIFY` |
| **SCEN-06** | **Low-Confidence OCR Case** | Faded, smudged discharge slip; OCR confidence $0.42 < 0.70$. | State: `OCR_FAILED` -> Fallback to manual entry |
| **SCEN-07** | **Voice Transcription Workflow** | Audio intake in Hindi; translated and parsed with `VOICE_TRANSCRIBED` provenance. | Symptoms extracted with audio URI linked |
| **SCEN-08** | **New Evidence Changing Risk** | Stable asthma patient receives lab showing PaCO2 $65\text{ mmHg}$ ($R_t: 0.20 \to 0.85$). | Immediate CareGraph update & alert push |
| **SCEN-09** | **Deteriorating Trajectory Case**| Serial vitals over 30 min show $\Delta R = +2.1/\text{hr}$ (Rapid Deterioration). | Action transitions from `OBSERVE` to `ESCALATE` |
| **SCEN-10** | **Clinician Override Case** | System advises `OBSERVE`; doctor examines bedside and overrides to `ESCALATE`. | Override recorded with doctor's mandatory rationale |
| **SCEN-11** | **Referral Required Case** | Acute ischemic stroke arriving at rural PHC without CT scanner. | FacilityGraph marks local care `INFEASIBLE` |
| **SCEN-12** | **Current Facility Unsuitable** | Emergency obstetric hemorrhage at facility with 0 units of O-negative blood. | Identifies blood stock failure; initiates routing |
| **SCEN-13** | **Alternative Facility Match** | FacilityGraph evaluates 4 network hospitals; ranks District Hospital #1. | Generates auto-populated SBAR transfer packet |
| **SCEN-14** | **Referral Completion Case** | Ambulance transfer arrives at receiving hospital; digital handoff accepted. | State transitions to `COMPLETED` |
| **SCEN-15** | **Follow-up & Outcome Loop** | Patient discharge outcome recorded; feeds back into CareGraph archive. | State transitions to `OUTCOME` |
| **SCEN-16** | **Facility Demand Increase** | 10 simulated admissions saturate District Hospital ICU ($100\%$ full). | FacilityGraph immediately updates referral ranks |
| **SCEN-17** | **System Signal Generation** | 8 acute hemorrhagic fever cases ingested across 2 facilities within 24h. | SignalGraph raises Dengue cluster alert ($Z > 3.0$) |

---

## 4. The 5 Core Innovation Acceptance Tests

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CORE INNOVATION ACCEPTANCE GATES                         │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Innovation Gate │ Mandatory Acceptance Test Criteria                        │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **CAREGRAPH**   │ When new vitals or symptoms are added, the patient's      │
│                 │ CareGraph nodes, trajectory slope ($\Delta R$), and       │
│                 │ uncertainty ($\mathcal{U}_t$) MUST recalculate instantly. │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **FACILITYGRAPH**│ Toggling a facility's equipment status (e.g., setting CT  │
│                 │ Scanner offline) MUST immediately flip care feasibility   │
│                 │ from `FEASIBLE` to `INFEASIBLE` and trigger referral.     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **SIGNALGRAPH** │ Live synthetic intake cases MUST dynamically update the   │
│                 │ real-time SignalGraph cluster count without page refresh. │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **ORCHESTRATION**│ Synthesizing patient risk + uncertainty + facility state  │
│                 │ MUST produce a valid advisory recommendation (`ASK`,      │
│                 │ `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`).    │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **OUTCOME LOOP**│ Recording final patient disposition MUST update the       │
│                 │ encounter FSM and transmit an de-identified episode packet │
│                 │ to SignalGraph macro analytics.                           │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 5. Verification Commands

```bash
# Backend Unit & Scenario Test Suite
pytest backend/tests -v --asyncio-mode=auto

# Code Quality & Linting
flake8 backend/app
black --check backend/app

# Frontend Type-check & Production Build
cd frontend && npm run build
```
