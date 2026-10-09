# CLINOVA AI — Evidence-to-Decision Traceability & Closed-Loop Governance

> **Document ID:** `RES-122`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Closed-Loop Traceability Mandate

In clinical governance and hospital quality assurance, unexplained variation and ungrounded decisions represent the leading causes of preventable patient mortality and legal exposure. When an adverse event occurs (e.g. an emergency patient suffers a cardiac arrest in a transit corridor), hospital audit committees and medicolegal courts examine a single fundamental question:
> *"Why did the care team make this specific clinical decision, on what exact evidence was it based, and what did the computerized decision support system recommend at that precise moment?"*

In standard healthcare software, this backward audit trail is impossible to reconstruct because systems store only the final state, erasing intermediate algorithmic recommendations, doctor overrides, and the specific vitals available at the decision timestamp.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL DECISION TRACEABILITY INVARIANT               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  EVERY CLINICALLY MEANINGFUL DECISION MUST                  │
│                   BE TRACEABLE BACKWARDS TO PRIMARY EVIDENCE.               │
│                                                                             │
│   The system maintains an unbroken, bi-directional traceability graph:      │
│   EVIDENCE ──> RISK ──> TRAJECTORY ──> UNCERTAINTY ──> RECOMMENDATION       │
│   ──> CLINICIAN DECISION ──> PHYSICAL ACTION ──> CLINICAL OUTCOME.          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Eight-Node Decision Traceability Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE EIGHT-NODE DECISION LINEAGE CHAIN                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ [1. PRIMARY EVIDENCE]        Raw observations, vitals, symptoms, OCR crops  │
│          │                                                                  │
│          ▼                                                                  │
│ [2. COMPOSITE RISK]          NEWS2, Shock Index, physiological hazard       │
│          │                                                                  │
│          ▼                                                                  │
│ [3. TRAJECTORY SLOPE]        Rate and direction of clinical progression     │
│          │                                                                  │
│          ▼                                                                  │
│ [4. EPISTEMIC UNCERTAINTY]   Data gaps, active conflicts, perceptual bounds │
│          │                                                                  │
│          ▼                                                                  │
│ [5. ORCHESTRATION ADVISORY]  AI & Guideline recommended pathway (CAREGRAPH) │
│          │                                                                  │
│          ▼                                                                  │
│ [6. CLINICIAN DECISION]      Attending RMP disposition, order, Rx, sign-off │
│          │                                                                  │
│          ▼                                                                  │
│ [7. PHYSICAL ACTION]         Actual medication infused, transfer dispatched │
│          │                                                                  │
│          ▼                                                                  │
│ [8. CLINICAL OUTCOME]        Physiological stabilization, cure, or mortality│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Decoupling Intent, Decision, Action, and Reality

A critical conceptual breakthrough formalized in Phase 6 (`RES-96`) and expanded in Phase 7 is the **strict decoupling of four distinct clinical dimensions**:

$$\mathbf{Planned\ Advice} \neq \mathbf{Actual\ Clinician\ Decision} \neq \mathbf{Actual\ Care\ Action} \neq \mathbf{Real\text{-}World\ Outcome}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Planned Advice (Machine Advisory):                                       │
│    Orchestration Engine recommends: "IMMEDIATE_TRANSFER to SCB Cuttack"     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Actual Clinician Decision (RMP Judgment):                                │
│    Dr. Patnaik, MD decides: "STABILIZE_LOCALLY with IV Furosemide first"    │
│    (Recorded with medical override justification in clinician_modifications)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Actual Care Action (Physical Execution):                                 │
│    Nurse administers 40mg Furosemide IV at 10:45 AM (Logged in eMAR)        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Real-World Outcome (Biological Response):                                │
│    Patient diureses 1200 mL; SpO2 improves to 96%; transfer avoided!        │
│    (Recorded in case_outcomes as RESOLVED_SUCCESS)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

By decoupling these four nodes, the system creates a rich, tamper-evident learning loop:
- It proves that Dr. Patnaik made a conscious, justified clinical override.
- It proves that the physical drug was administered correctly.
- It proves that the clinical outcome was positive, feeding valuable real-world alignment data back into the CAREGRAPH knowledge base.

---

## 4. Comprehensive Bidirectional Traceability Matrix

| Node | Canonical Relational Entity | Foreign Key Linkages | Primary Epistemic Role |
| :--- | :--- | :--- | :--- |
| **1. Evidence** | `evidence_records`, `vital_readings` | `case_id`, `raw_source_id` | Ground-truth empirical foundation |
| **2. Risk** | `clinical_evaluations` | `case_id`, `input_vital_ids` | Physiological hazard assessment ($R_t$) |
| **3. Trajectory** | `symptoms`, `symptom_progression_events`| `case_id`, `symptom_id` | Disease velocity ($\Delta\text{Severity} / \Delta t$) |
| **4. Uncertainty** | `clinical_evaluations` | `case_id`, `conflict_ids` | Epistemic incompleteness penalty ($U_t$) |
| **5. Advisory** | `orchestration_recommendations` | `case_id`, `evaluation_id` | Safest achievable guideline pathway |
| **6. Decision** | `clinician_reviews`, `clinician_orders` | `case_id`, `recommendation_id`| Legally binding RMP sign-off |
| **7. Action** | `referrals`, `ward_admissions`, `surgeries`| `case_id`, `order_id` | Physical execution of care |
| **8. Outcome** | `case_outcomes` | `case_id`, `action_ids` | Definitive biological & audit resolution |

---

## 5. Decision Lineage Relational Specification

```sql
CREATE TABLE decision_traceability_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    -- Forward / Backward Linkages
    evidence_record_ids JSONB NOT NULL,       -- Primary inputs
    clinical_evaluation_id UUID NOT NULL REFERENCES clinical_evaluations(id),
    orchestration_recommendation_id UUID NOT NULL REFERENCES orchestration_recommendations(id),
    clinician_review_id UUID NOT NULL REFERENCES clinician_reviews(id),
    clinician_order_id UUID REFERENCES clinician_orders(id),
    physical_action_id UUID, -- References referrals(id) or ward_admissions(id)
    case_outcome_id UUID REFERENCES case_outcomes(id),
    
    -- Alignment Evaluation
    recommendation_decision_alignment VARCHAR(24) NOT NULL CHECK (recommendation_decision_alignment IN (
        'FULL_ALIGNMENT', 'PARTIAL_ALIGNMENT', 'CLINICIAN_OVERRIDE', 'EMERGENCY_DIVERGENCE'
    )),
    
    established_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_dec_trace_case ON decision_traceability_links(case_id);
CREATE INDEX ix_dec_trace_rev ON decision_traceability_links(clinician_review_id);
```

This end-to-end traceability matrix guarantees complete forensic transparency: every dose of medication, surgical incision, or inter-facility transfer can be traced backwards to the exact sensor reading or patient symptom that initiated the cascade.
