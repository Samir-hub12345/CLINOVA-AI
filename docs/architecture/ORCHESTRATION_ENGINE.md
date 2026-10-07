# ORCHESTRATION ENGINE — Safest Achievable Care Action Recommendation

## 1. Domain Purpose
The `Orchestration Engine` is the central synthesis layer of CLINOVA AI. It combines:
1. Patient clinical state & uncertainty from **CareGraph**
2. Facility capabilities & live capacity from **FacilityGraph**
3. Aggregate system pressures & trends from **SignalGraph**

Its objective is to recommend the **Safest Achievable Next Care Action** for clinician review.

---

## 2. Decision Synthesis Loop

```
           [CareGraph]                  [FacilityGraph]
       Patient State & Risk          Capacity & Capabilities
                │                               │
                └───────────────┬───────────────┘
                                ▼
                   ┌─────────────────────────┐
                   │   CARE FEASIBILITY      │
                   │   VALIDATION            │
                   └────────────┬────────────┘
                                │
                        [SignalGraph]
                     Operational Context
                                │
                                ▼
                   ┌─────────────────────────┐
                   │   ORCHESTRATION ENGINE  │
                   │  Safest Next Care Step  │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  HUMAN-IN-THE-LOOP      │
                   │  MANDATORY REVIEW GATE  │
                   │  (Doctor Confirmation)  │
                   └─────────────────────────┘
```

---

## 3. Recommended Action Categories
- **Immediate Casualty Redirection:** Hardcoded red-flag triggers (TRIAGE-R01 to R06) diverting to emergency stabilization.
- **Priority Outpatient Review:** Elevated risk cases expedited within the facility queue.
- **Routine Longitudinal Assessment:** Standard outpatient queue with follow-up question prompts to close information gaps.
- **Structured Inter-Facility Referral:** Comprehensive transfer packet prepared when local facility capability cannot meet required intervention standards.

---

## 4. Human-in-the-Loop Review Gate
- Recommendations are strictly advisory.
- No recommendation takes effect without a qualified healthcare professional's active confirmation, modification, or rejection.
- All actions generate an immutable medicolegal audit trail.
