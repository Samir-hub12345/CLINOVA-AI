# CLINOVA AI — Continuity of Care & Outcome Feedback Loop

> **Document ID:** `DOC-17`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. The Post-Encounter Continuity Mandate

> **Core Product Principle:** The patient journey does NOT end at Doctor Approval, Referral Dispatch, Inpatient Admission, or Hospital Discharge.
>
> In conventional triage systems, the software's job finishes the moment a triage category is assigned or a patient walks out of the triage room. CLINOVA AI establishes a continuous care intelligence architecture that tracks what happens **after** the clinical decision:

$$\begin{aligned}
\mathbf{DECISION} &\longrightarrow \mathbf{ACTION} \longrightarrow \mathbf{REFERRAL\ /\ APPOINTMENT\ /\ ADMISSION} \\
&\longrightarrow \mathbf{CONTINUATION} \longrightarrow \mathbf{OUTCOME} \longrightarrow \mathbf{CAREGRAPH\ UPDATE} \longrightarrow \mathbf{SIGNALGRAPH\ UPDATE}
\end{aligned}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONTINUOUS CARE INTELLIGENCE LOOP                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        1. CLINICAL DECISION SIGNED                          │
│                        (Doctor approves care pathway)                       │
│                                       │                                     │
│                                       ▼                                     │
│                        2. CARE ACTION EXECUTED                              │
│                        (Medication, Admission, Referral)                    │
│                                       │                                     │
│                                       ▼                                     │
│                        3. PATHWAY EXECUTION & HANDOFF                       │
│                        (Ambulance dispatch, Bed assignment)                 │
│                                       │                                     │
│                                       ▼                                     │
│                        4. CLINICAL CONTINUATION                             │
│                        (Inpatient stay, Revisit, Transfer)                  │
│                                       │                                     │
│                                       ▼                                     │
│                        5. REAL-WORLD OUTCOME RECORDING                      │
│                        (Full recovery, Complication, Re-triage)             │
│                                       │                                     │
│                     ┌─────────────────┴─────────────────┐                   │
│                     ▼                                   ▼                   │
│          6. CAREGRAPH STATE UPDATE          7. SIGNALGRAPH UPDATE           │
│          • Long-term patient record delta   • Network epidemiological signal│
│          • Resolves pending uncertainties   • Facility referral effectiveness│
│          • Closes active encounter          • Model calibration feedback     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six Post-Encounter State Transitions

A Master Case transitions through explicit lifecycle states following doctor sign-off:

1. `DECISION_SIGNED`: Clinician confirms the care plan and executes the digital signature.
2. `ACTION_DISPATCHED`: Prescriptions sent to dispensary; bed requested; referral manifest transmitted.
3. `IN_TRANSIT_OR_HANDOFF`: Patient being transported to ward or receiving hospital.
4. `CONTINUATION_ACTIVE`: Patient under active inpatient management or following outpatient schedule.
5. `OUTCOME_RESOLVED`: Real clinical endpoint recorded by healthcare team.
6. `CLOSED_AND_ARCHIVED`: Encounter finalized; data retained according to compliance policies; anonymized telemetry exported to SIGNALGRAPH.

---

## 3. Real Clinical Outcome Taxonomy

CLINOVA categorizes outcomes to measure clinical efficacy and algorithmic safety:

| Outcome Category | Operational Definition | Clinical Example | Telemetry Impact |
| :--- | :--- | :--- | :--- |
| `FULL_RECOVERY` | Complete resolution of acute illness without complications. | Viral fever resolves in 72 hours; patient returns to work. | Reinforces baseline triage specificity. |
| `STABILIZED` | Chronic condition or acute flare controlled within acceptable parameters. | Hypertensive crisis normalized with oral meds; outpatient follow-up set. | Confirms routine pathway validity. |
| `COMPLICATION_MANAGED` | Secondary complication developed but safely caught and treated on-site. | Dengue fever developed mild mucosal bleeding; managed in HDU. | Evaluates early trajectory warning sensitivity. |
| `REFERRED_HIGHER` | Patient safely transferred to tertiary center following planned stabilization. | Acute abdomen transferred to medical college; successful laparotomy. | Validates FACILITYGRAPH referral recommendation. |
| `CRITICAL_TRANSFER` | Unplanned emergency escalation requiring rapid evacuation. | Outpatient waiting in OPD collapsed with massive pulmonary embolism. | Triggers failure analysis of initial triage. |
| `ADVERSE_EVENT` | Avoidable deterioration, delayed transfer, or unexpected mortality. | Patient discharged as low-risk returned in septic shock within 12 hours. | **High-priority safety audit trigger:** Prompts root-cause review. |

---

## 4. Closing the Loop: Two-Tier Graph Updates

### 4.1 Tier 1: CAREGRAPH Longitudinal Update
When an outcome is recorded:
- The active CAREGRAPH instance for the encounter transitions from `ACTIVE` to `RESOLVED`.
- Historical physiological responses to specific interventions are linked to the synthetic patient ID, providing longitudinal context for future encounters.
- All unverified or pending hypotheses are marked as resolved, providing ground-truth data for clinical audits.

### 4.2 Tier 2: SIGNALGRAPH & System Intelligence Update
The recorded outcome immediately propagates to the macro-level intelligence layer:
- **Referral Efficacy Scoring:** Did the receiving facility successfully admit and treat the referred patient without rejection?
- **Triage Calibration Signals:** Computes statistical concordance between the AI's initial advisory risk band and the patient's actual clinical endpoint.
- **Epidemiological Cluster Resolution:** Tracks the resolution velocity of syndromic clusters, alerting public health authorities when disease outbreaks subside.
