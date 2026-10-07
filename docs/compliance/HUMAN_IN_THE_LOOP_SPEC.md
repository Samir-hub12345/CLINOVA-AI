# CLINOVA AI — Human-in-the-Loop (HITL) Specification

## 1. Regulatory Context & Governance
In accordance with WHO AI Health Guidance, ABDM (Ayushman Bharat Digital Mission) standards, and medical device software regulations:
- Automated clinical prioritization tools must maintain continuous clinician supervision.
- Software recommendations cannot replace professional medical judgment.

---

## 2. Reviewer Gate Workflow

```
[Patient Intake & Multi-Modal Capture]
                  │
                  ▼
[Continuous Care Synthesis (CareGraph + FacilityGraph)]
                  │
                  ▼
[Orchestration Engine Recommendation]
                  │
                  ▼
┌──────────────────────────────────────────────┐
│        MANDATORY REVIEWER DASHBOARD          │
│                                              │
│ • Review clinical narrative & extracted vitals│
│ • Inspect evidence provenance & uncertainty  │
│ • Confirm, edit, or reject care action       │
│ • Sign with clinician credentials            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
        [Finalized Clinical Care Order]
```

---

## 3. Reviewer Verification States
1. **PENDING_REVIEW:** Initial synthesized state. Case is visible in the doctor/nurse triage queue. No downstream actions are dispatched.
2. **VERIFIED:** Attending clinician reviews all parameters and signs off on the recommended care action without modification.
3. **MODIFIED:** Attending clinician updates urgency tier, notes, or target facility, providing clinical justification.
4. **REJECTED:** Attending clinician invalidates the recommendation (e.g. spurious report artifact, clinical disagreement), escalating to custom management.
