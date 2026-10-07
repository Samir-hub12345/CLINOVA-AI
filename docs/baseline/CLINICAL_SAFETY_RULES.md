# CLINOVA AI — Clinical Safety & Deterministic Rules Specification

## 1. Non-Diagnostic Design Mandate
CLINOVA AI operates exclusively as a **Clinical Decision Support System (CDSS)**. Under no operational circumstance does the software:
- Output a definitive medical diagnosis.
- Prescribe pharmaceutical dosages or clinical treatments.
- Discharge or transfer a patient autonomously.

---

## 2. Deterministic Red-Flag Safety Rules

Generative or machine learning models may experience hallucinations or uncertainty. To protect patient safety, hardcoded deterministic rules **strictly override** all algorithmic recommendations.

```
┌─────────────┬─────────────────────────────────┬───────────────────┬──────────────────────┐
│ Rule ID     │ Clinical Presentation Criteria   │ Urgency Level     │ Immediate Action     │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R01  │ Severe Respiratory Distress,     │ EMERGENCY (RED)   │ Immediate Oxygen &   │
│             │ Stridor, Central Cyanosis        │                   │ Casualty Transfer    │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R02  │ Acute Crushing Chest Pain,       │ EMERGENCY (RED)   │ Urgent ECG &         │
│             │ Left Arm Radiation, Diaphoresis  │                   │ Medical Officer Stat │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R03  │ Uncontrolled Active Hemorrhage,  │ EMERGENCY (RED)   │ Pressure Hemostasis, │
│             │ Severe Shock, Hypotension        │                   │ IV Resuscitation     │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R04  │ Sudden Neurological Deficit,     │ EMERGENCY (RED)   │ Stroke Code Alert,   │
│             │ Facial Droop, Unilateral Weakness│                   │ Urgent Neuro Eval    │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R05  │ Altered Consciousness, GCS < 13, │ EMERGENCY (RED)   │ Airway Protection,   │
│             │ Active Convulsions / Seizure     │                   │ Immediate Casualty   │
├─────────────┼─────────────────────────────────┼───────────────────┼──────────────────────┤
│ TRIAGE-R06  │ Anaphylaxis Symptoms, Urticaria, │ EMERGENCY (RED)   │ Epinephrine Alert,   │
│             │ Laryngeal Edema, Dyspnea         │                   │ Critical Care Bay    │
└─────────────┴─────────────────────────────────┴───────────────────┴──────────────────────┘
```

---

## 3. Human-in-the-Loop Override Hierarchy
- Every generated clinical note must display the rule provenance.
- The attending medical officer has absolute authority to:
  1. Confirm the recommendation.
  2. Upgrade or downgrade the urgency level.
  3. Modify the clinical summary.
  4. Reject the recommendation and log the clinical rationale.
