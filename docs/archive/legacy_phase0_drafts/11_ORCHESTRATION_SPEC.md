# CLINOVA AI — ORCHESTRATION ENGINE Detailed Technical Specification

> **Document ID:** `DOC-11`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Architectural Role & Core Purpose

The **Orchestration Engine** is the cognitive synthesis core of CLINOVA AI. It integrates:
$$\mathbf{CareGraph} + \mathbf{Evidence\ Uncertainty} + \mathbf{FacilityGraph} + \mathbf{SignalGraph}$$
to evaluate and recommend:
$$\mathbf{THE\ SAFEST\ ACHIEVABLE\ CARE\ ACTION}$$

The Orchestration Engine is strictly **advisory**. It never executes actions autonomously. A qualified human clinician retains final authority and responsibility for all medical and administrative decisions.

---

## 2. Multi-Dimensional Synthesis Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION ENGINE COGNITIVE SYNTHESIS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CAREGRAPH ] ────────> Patient Risk ($R_t$) & Trajectory ($\Delta R$)    │
│                                      │                                      │
│  [ EVIDENCE UNCERTAINTY ] ──> Data Gaps ($\mathcal{U}_t$) & Conflicts      │
│                                      │                                      │
│  [ FACILITYGRAPH ] ────> On-Site Feasibility & Network Referral Ranks       │
│                                      │                                      │
│  [ SIGNALGRAPH ] ──────> Outbreak Context & Facility Queue Saturation       │
│                                      │                                      │
│                                      ▼                                      │
│                   ┌──────────────────────────────────────┐                  │
│                   │   ORCHESTRATION MULTI-CRITERIA FSM   │                  │
│                   └──────────────────┬───────────────────┘                  │
│                                      │                                      │
│                                      ▼                                      │
│           [ ADVISORY CANDIDATE ACTION RECOMMENDATION ]                      │
│           - ASK       (Resolve critical information gap)                    │
│           - VERIFY    (Reconcile contradictory findings)                    │
│           - CONTINUE  (Maintain current low-risk care plan)                 │
│           - OBSERVE   (Schedule repeat vitals / serial trajectory)          │
│           - ESCALATE  (Immediate bedside emergency resuscitation)          │
│           - REFER     (Intelligent transfer to capable receiving center)    │
│                                      │                                      │
│                                      ▼                                      │
│                   ┌──────────────────────────────────────┐                  │
│                   │       QUALIFIED CLINICIAN GATE       │                  │
│                   │  [Accept Action]  or  [Override + Note]│                  │
│                   └──────────────────────────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Decision Logic & Action Selection Taxonomy

The engine applies a prioritized, deterministic rule-and-heuristic evaluation tree to select the primary candidate action:

### Rule 1: Immediate Resuscitation / Bedside Emergency (`ESCALATE`)
- **Trigger Condition:**
  - $R_t \ge 0.70$ (NEWS2 $\ge 7$ or systolic BP $< 90$ with altered mental status) **OR**
  - $\Delta R \ge +1.5/\text{hr}$ (Rapid physiological deterioration) **OR**
  - Active life-threat red flag present (e.g., massive hematemesis, stridor, acute severe respiratory distress).
- **Advisory Recommendation:** `ESCALATE`
- **Clinical Directive:** "Alert Resuscitation Team immediately. Prepare airway, IV access, and continuous monitor."

### Rule 2: Infeasible Care on Site (`REFER`)
- **Trigger Condition:**
  - Case requires urgent intervention bundle $\mathcal{B}_{\text{req}}$ (e.g., emergency neurosurgery, hemodialysis, thrombolysis) **AND**
  - Current facility feasibility evaluates to `INFEASIBLE` or `DEGRADED` (e.g., CT scanner offline or ICU full) **AND**
  - Patient is stabilized sufficiently for transport.
- **Advisory Recommendation:** `REFER`
- **Clinical Directive:** "Transfer required. FacilityGraph indicates nearest capable center is District Hospital (22 min transit). SBAR packet generated."

### Rule 3: High Data Uncertainty (`ASK`)
- **Trigger Condition:**
  - Risk is non-critical ($R_t < 0.70$) **BUT**
  - Uncertainty $\mathcal{U}_t > 0.40$ **AND**
  - Protocol-critical parameter is absent (e.g., chest pain duration unknown, diabetes status absent).
- **Advisory Recommendation:** `ASK`
- **Clinical Directive:** "High clinical uncertainty. Prompt intake staff for targeted follow-up question before determining final care disposition."

### Rule 4: Contradictory Evidence (`VERIFY`)
- **Trigger Condition:**
  - Active conflicting clinical findings detected (e.g., verbal report of 'asymptomatic' vs SpO2 of 86%, or OCR lab hemoglobin of 3.2 g/dL without signs of shock).
- **Advisory Recommendation:** `VERIFY`
- **Clinical Directive:** "Conflicting evidence flagged. Clinician verification of vital signs or repeated laboratory sampling required."

### Rule 5: Borderline / Evolving Acuity (`OBSERVE`)
- **Trigger Condition:**
  - Moderate risk ($0.35 \le R_t < 0.70$) **OR**
  - Borderline worsening trajectory ($0.5 \le \Delta R < 1.5/\text{hr}$) **AND**
  - Current facility has holding bed capacity.
- **Advisory Recommendation:** `OBSERVE`
- **Clinical Directive:** "Place in observation bay. Repeat complete vital sign battery in 20 minutes to establish dynamic trajectory."

### Rule 6: Low Risk & Routine Care Feasible (`CONTINUE`)
- **Trigger Condition:**
  - Low risk ($R_t < 0.35$), physiological stability ($\Delta R \approx 0.0$), low uncertainty ($\mathcal{U}_t \le 0.40$), and required care bundle fully feasible on-site.
- **Advisory Recommendation:** `CONTINUE`
- **Clinical Directive:** "Maintain routine outpatient or ambulatory management. Re-evaluate if new symptoms emerge."

---

## 4. Clinician Decision Gate & Structured Override Protocol

The Orchestration Engine enforces a mandatory human sign-off gate before any care action is recorded:

```python
class ClinicianDecisionRequest(BaseModel):
    case_id: str
    clinician_id: str
    clinician_name: str
    decision_type: str # 'ACCEPT' or 'OVERRIDE'
    chosen_action: str # 'ASK', 'VERIFY', 'CONTINUE', 'OBSERVE', 'ESCALATE', 'REFER'
    override_reason: Optional[str] = None # Mandatory if decision_type == 'OVERRIDE'
    clinical_notes: Optional[str] = None
    timestamp: datetime
```

### 4.1 Medicolegal Override Logging
When a clinician overrides an advisory recommendation:
1. The override is flagged with a prominent badge in the CareGraph.
2. The clinician's explicit textual rationale is stored permanently in the audit trail.
3. The override event is dispatched to SignalGraph quality assurance metrics to detect potential algorithmic drift or system miscalibration.

---

## 5. Continuous Loop Feedback

Once the clinician authorizes an action and the care is delivered, the recorded **Patient Outcome** loops back into CareGraph (advancing state to `COMPLETED` or `OUTCOME`) and transmits an de-identified episode packet to **SignalGraph**, completing the continuous care cycle.
