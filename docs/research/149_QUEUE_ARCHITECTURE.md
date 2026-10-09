# CLINOVA AI — Doctor Queue Prioritization & Routing Architecture

> **Document ID:** `RES-149`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Queue Operations Engineering Group  

---

## 1. The PostgreSQL Dynamic Column Invariant

In relational databases, developers frequently attempt to model dynamic elapsed wait time using stored generated columns:
```sql
-- DANGEROUS / INVALID POSTGRESQL DESIGN:
-- ALTER TABLE cases ADD COLUMN wait_minutes INTEGER 
-- GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (NOW() - queued_at))/60) STORED;
```

### The Architectural Violation & Database Reality
PostgreSQL strictly prohibits volatile or non-deterministic functions (such as `NOW()`, `CURRENT_TIMESTAMP`, or `clock_timestamp()`) in stored generated column expressions. The database engine rejects this DDL with:
```
ERROR: generation expression is not immutable
```
Even if a database permitted it, a stored generated column only evaluates when the row is written to (`INSERT` or `UPDATE`). As seconds and hours tick away, the stored value becomes stale, misleading triage staff about how long a patient has actually been waiting.

### Definitive Architectural Mandate
**Dynamic wait time MUST NOT be implemented as a stored generated column.**
CLINOVA AI evaluates dynamic wait times and priority rankings at **query time** via indexed datetime subtraction in an optimized SQL View or query projection:

```sql
-- Canonical Query-Time Wait Evaluation View
CREATE OR REPLACE VIEW v_active_doctor_queue AS
SELECT 
    c.id AS case_id,
    c.case_number,
    c.patient_id,
    c.facility_id,
    c.status,
    c.acuity_tier,
    c.risk_score,
    c.trajectory_slope,
    c.uncertainty_score,
    c.created_at,
    t.queued_at,
    -- Deterministic Query-Time Wait Time in Minutes:
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - t.queued_at)) / 60.0)::INTEGER AS wait_minutes
FROM cases c
JOIN triage_evaluations t ON t.case_id = c.id
WHERE c.status = 'STATE_DOCTOR_QUEUED';
```

---

## 2. Multi-Dimensional Queue Priority Scoring Formulation

The Doctor Queue prioritizes patients not by simple First-In-First-Out (FIFO) or static color triage tags, but through a multi-dimensional composite priority score $P \in \mathbb{R}^{+}$:

$$P = W_{\text{acuity}} + W_{\text{trajectory}} + W_{\text{wait}} + W_{\text{facility}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       QUEUE PRIORITY COMPONENT WEIGHTS                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. BASE ACUITY WEIGHT (W_acuity):                                          │
│     • CRITICAL (Red Flag / Shock / NEWS2 >= 7):       W_acuity = 10,000     │
│     • URGENT (Amber Alert / NEWS2 5–6):                W_acuity = 1,000      │
│     • MODERATE (Yellow / NEWS2 1–4):                   W_acuity = 200        │
│     • ROUTINE (Green / NEWS2 0):                       W_acuity = 50         │
│                                                                             │
│  2. PHYSIOLOGICAL TRAJECTORY WEIGHT (W_trajectory):                         │
│     • RAPIDLY_DETERIORATING (Slope > +0.25):           W_trajectory = +5,000 │
│     • DETERIORATING (Slope in [+0.05, +0.25]):         W_trajectory = +500   │
│     • STABLE / IMPROVING:                              W_trajectory = 0      │
│                                                                             │
│  3. DYNAMIC WAIT-TIME ESCALATION (W_wait):                                  │
│     • W_wait = wait_minutes * alpha(Acuity)                                 │
│     • alpha(URGENT) = 15.0 pts/min                                          │
│     • alpha(MODERATE) = 5.0 pts/min                                         │
│     • alpha(ROUTINE) = 1.0 pts/min                                          │
│     (Guarantees moderate cases advance steadily; prevents queue starvation)│
│                                                                             │
│  4. FACILITY CONTEXT ADJUSTMENT (W_facility):                               │
│     • Operational surge adjustments based on current ED congestion          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Epistemic Uncertainty Routing Refinement

A critical clinical safety insight established in Phase 7 and formalized in Phase 8 is that **uncertainty does not automatically imply emergency**.

### The Decoupling Law
$$\mathbf{Uncertainty\ (U_t) \neq Physiological\ Risk\ (R_t)}$$

- If a patient has a mild fungal rash and forgot to bring their previous ointment tube, epistemic uncertainty is high ($U_t = 0.65$), but physiological risk is zero ($R_t = 0.05$). Flagging this patient as a `CRITICAL EMERGENCY` would disrupt casualty resuscitations and induce clinical alert fatigue.
- Conversely, an unconscious trauma victim in hemorrhagic shock with known history has low uncertainty ($U_t = 0.10$), but critical physiological risk ($R_t = 0.95$).

### Definitive Routing Policy
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNCERTAINTY ROUTING DECISION MATRIX                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    PHYSIOLOGICAL RISK (R_t)                                 │
│                    LOW (R_t < 0.20)          HIGH (R_t >= 0.50)             │
│                 ┌─────────────────────────┬─────────────────────────┐       │
│   UNCERTAINTY   │ ROUTE A:                │ ROUTE B:                │       │
│   HIGH          │ NURSE MISSING-DATA      │ EMERGENCY CASUALTY CODE │       │
│   (U_t >= 0.40) │ WORKLIST                │ Immediate doctor exam   │       │
│                 │ (Targeted NBI questions;│ alongside bedside nurse │       │
│                 │ Does NOT ring ED alarms)│ gap closure             │       │
│                 ├─────────────────────────┼─────────────────────────┤       │
│   UNCERTAINTY   │ ROUTE C:                │ ROUTE D:                │       │
│   LOW           │ STANDARD DOCTOR QUEUE   │ RESUSCITATION WORKBENCH │       │
│   (U_t < 0.40)  │ Routine outpatient      │ Immediate critical care │       │
│                 │ priority                │ resuscitation           │       │
│                 └─────────────────────────┴─────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rule:** High uncertainty **primarily routes to missing-data resolution and bedside nurse verification**, unless an independent deterministic physiological rule (NEWS2 $\ge 7$, Shock Index $> 0.9$, or explicit Red Flag) triggers emergency escalation.
