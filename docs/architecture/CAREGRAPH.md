# CAREGRAPH — Patient-Level Clinical State & Longitudinal Intelligence

## 1. Domain Purpose
`CareGraph` models the patient-level clinical state as an explainable, temporal knowledge representation. Unlike single-shot triage forms that discard context after assigning a priority tag, CareGraph maintains longitudinal continuity while strictly maintaining a **non-diagnostic** stance.

---

## 2. Core Entities & Graph Schema

```
┌────────────────────────────────────────────────────────┐
│                      CAREGRAPH NODE                    │
├────────────────────────────────────────────────────────┤
│ • Patient State ID (Synthetic, e.g. CG-xxxx)           │
│ • Episode Identifier & Encounter Context               │
│ • Modality Provenance (Voice, Narrative, Lab OCR)     │
│ • Temporal Sequence (Onset, Progression, Remission)   │
│ • Evidence Uncertainty Score (Low, Moderate, High)     │
│ • Missing Clinical Data Attributes                     │
└────────────────────────────────────────────────────────┘
```

### Key Dimensions:
1. **Symptom Chronology:** Structured timeline of reported sensations, anatomical locations, and duration curves.
2. **Clinical Observations:** Discrete quantitative metrics extracted from reports (e.g. hemoglobin, leukocyte count, platelet levels) annotated with extraction confidence.
3. **Uncertainty Quantification:** Flags contradictory patient narratives, missing duration data, or ambiguous vernacular idioms.
4. **Information Gap Detection:** Systematically identifies critical missing inputs needed for safe triage (e.g. onset duration, allergy history, chest pain radiation).

---

## 3. Strict Non-Diagnostic Constraints
- Nodes store **observations**, **reported symptoms**, and **extracted parameters**—never finalized disease classifications.
- Generative text outputs are restricted to clinical summaries and structured SOAP-aligned notes for attending medical officers.
