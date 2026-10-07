# CLINOVA AI — Implementation Rules, Definition of Done & Phase Control

> **Document ID:** `DOC-27`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Strict Phase Control Invariant

> **Rule 1.1:** ONLY ONE NUMBERED PHASE MAY BE EXECUTED AT A TIME.
>
> An AI agent, engineer, or team must never automatically transition to the next numbered implementation phase without explicit, written human review and approval. Multiple phases must NEVER be collapsed or executed concurrently.

### The Mandatory 16-Step Execution Protocol for Every Phase
Before and during the execution of any numbered phase, the team must strictly follow:
1. **ANALYZE:** Deeply inspect existing repository state, contracts, and requirements.
2. **AUDIT ALL POSSIBLE OUTCOMES:** Enumerate every theoretical path and consequence.
3. **IDENTIFY NORMAL PATH:** Map standard happy-path clinical flow.
4. **IDENTIFY INCOMPLETE PATH:** Map paths where user inputs or vitals are partial.
5. **IDENTIFY EXCEPTION PATH:** Map clinical red-flag triggers and edge-case exceptions.
6. **IDENTIFY FAILURE PATH:** Map software, hardware, network, and model failures.
7. **IDENTIFY SECURITY/PERMISSION PATH:** Audit role authorization and data boundaries.
8. **IDENTIFY DOWNSTREAM EFFECT:** Map graph mutations on CAREGRAPH, FACILITYGRAPH, and SIGNALGRAPH.
9. **CREATE IMPLEMENTATION PLAN:** Write formal design document and artifact.
10. **STOP FOR REVIEW:** Solicit user/stakeholder review on the implementation plan.
11. **IMPLEMENT ONLY THAT PHASE:** Execute strictly the scope bounded by that phase.
12. **TEST:** Execute automated unit, integration, and contract test suites.
13. **BROWSER VERIFY:** Verify interactive rendering, responsive layouts, and accessibility in the browser.
14. **DOCUMENT:** Update documentation, feature inventories, and ADR logs.
15. **REPORT:** Provide formal completion report matching the specified schema.
16. **STOP:** Terminate turn and await explicit human authorization for the subsequent phase.

---

## 2. Definition of Done (DoD) for Future Implementation

> **Rule 2.1:** A screen alone is NOT a completed feature.  
> **Rule 2.2:** A button alone is NOT a completed feature.  
> **Rule 2.3:** A mock AI result is NOT a completed feature.  
> **Rule 2.4:** A disconnected dashboard is NOT a completed feature.

A feature is recognized as **DONE** if and only if all ten applicable engineering dimensions are completely verified:

$$\mathbf{Done} \iff \begin{aligned}
&\mathbf{UI} \wedge \mathbf{Data\ Model} \wedge \mathbf{Backend/API} \wedge \mathbf{Business\ Logic} \wedge \mathbf{Integration} \\
&\wedge\ \mathbf{Validation} \wedge \mathbf{Failure\ Handling} \wedge \mathbf{Automated\ Tests} \wedge \mathbf{Browser\ Verification} \wedge \mathbf{Documentation}
\end{aligned}$$

| Dimension | Verification Standard |
| :--- | :--- |
| **1. UI** | Responsive, accessible (WCAG AA), adhering to clinical palette tokens and 48px touch targets. |
| **2. Data Model** | Strongly typed entity model persisted in PostgreSQL / SQLite; bound to Master Case. |
| **3. Backend / API** | FastAPI endpoint with asynchronous execution, Pydantic v2 schemas, and OpenAPI documentation. |
| **4. Business Logic** | Deterministic clinical rules executed; zero ungrounded heuristic hallucinations. |
| **5. Integration** | Seamless end-to-end integration across frontend, API layer, database, and local inference runtimes. |
| **6. Validation** | Input sanitization, PII scrubbing, physiological range checks, and mandatory consent enforcement. |
| **7. Failure Handling** | Graceful degradation, fallback to rule heuristics, clear user error recovery cards. |
| **8. Tests** | Automated unit tests (`pytest`), schema validations, and mock ingestion test suites passing with zero errors. |
| **9. Browser Verification** | Real browser verification confirming zero console errors, zero layout shifts, and functional state changes. |
| **10. Documentation** | Feature matrix updated in `docs/FEATURE_INVENTORY.md` with concrete evidence. |

---

## 3. Failure & Exception Handling Principles

Every single workflow must account for the fourteen foundational clinical and system exception states:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FOURTEEN FAILURE & EXCEPTION MODES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Incomplete Information    ──> Hand off to Nurse Missing-Data Checklist │
│  2. Conflicting Observations ──> Surface Conflict Alert; Require Verification│
│  3. Unreliable Evidence       ──> Badge as UNRELIABLE; Require Manual Entry │
│  4. Local OCR Failure         ──> Surface retry card; Enable Manual Typing  │
│  5. Voice Transcription Fail  ──> Fallback to Text Input Box                │
│  6. Local SLM Unavailable     ──> Automatic fallback to Deterministic Rules │
│  7. Database Connection Drop  ──> Local offline queue; Retry synchronization│
│  8. Invalid / Corrupt File    ──> Reject file with clear MIME-type guidance │
│  9. Referral Target Rejection ──> Re-query FACILITYGRAPH for next-best dest │
│ 10. Local Facility Deficit    ──> Immediate Capability-Matched Referral Path│
│ 11. Bed Capacity Exhausted    ──> Escalate to Facility Admin; Queue Holding │
│ 12. Missed Appointment        ──> Automated SMS reminder; Revisit Re-queue  │
│ 13. Failed Ward/OT Handoff    ──> Block transfer sign-off until both agree  │
│ 14. Mid-Encounter Red Flag    ──> Instant Dynamic Escalation to Emergency   │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **The Anti-Fabrication Law:** The system must detect, explain, recover, or safely halt rather than silently fabricate or impute data during any failure.

---

## 4. Hackathon Foundation vs. Future Grant/Finals Track

1. **Hackathon Invariant:** The hackathon baseline must deliver a complete, genuinely working prototype spanning multimodal intake, CAREGRAPH, FACILITYGRAPH, SIGNALGRAPH, Orchestration, doctor workbench, and referral generation. **No unfinished core functionality may be deferred to the "Future Track".**
2. **Future Grant / Post-Hackathon Scope:**
   - Multi-center clinical trials and formal prospective clinical validation.
   - Domain-specific LoRA fine-tuning on millions of multilingual clinical records.
   - HL7 FHIR / ABDM (Ayushman Bharat Digital Mission) nationwide integration.
   - Live telemetry IoT integrations with hospital monitoring equipment.
