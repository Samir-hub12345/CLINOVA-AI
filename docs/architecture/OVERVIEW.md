# CLINOVA AI — Continuous Care Intelligence Architecture

## 1. Paradigm Shift: From Isolated Triage to Continuous Care Intelligence

In traditional clinical intake systems, triage is treated as an isolated, static event: a patient describes symptoms, an algorithm generates an urgency score or differential list, and the interaction terminates. 

In resource-constrained institutional healthcare—such as Indian District Hospitals, Primary Health Centers (PHCs), Community Health Centers (CHCs), and casualty triage units—isolated triage fails because:
1. **Clinical State is Longitudinal:** A patient's clinical picture evolves over hours, days, and multiple visits. A single snapshot misses symptom trajectory, treatment response, and diagnostic drift.
2. **Care Feasibility is Facility-Dependent:** Recommending a specialized intervention is useless—and potentially hazardous—if the target facility lacks oxygen supply, ICU beds, laboratory reagents, or on-duty surgical specialists.
3. **Operational Context Dictates Safe Timelines:** Patient wait times and risk escalation are heavily modulated by facility congestion, staffing shortages, and regional epidemic surges.
4. **Uncertainty Must Be Explicit:** Low data completeness, ambiguous patient statements, and blurry lab scans produce uncertainty that must guide follow-up rather than being masked by synthetic confidence.

**CLINOVA AI resolves these systemic failures by transitioning from Isolated Triage to Continuous Care Intelligence.**

---

## 2. The Four Architectural Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA AI ARCHITECTURAL ENGINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐                   ┌─────────────────────────┐  │
│  │        CAREGRAPH        │                   │      FACILITYGRAPH      │  │
│  │ Patient Clinical State  │                   │ Facility Capability &   │  │
│  │ Longitudinal Trajectory │                   │ Care Feasibility        │  │
│  │ Evidence Uncertainty    │                   │ Live Capacity Metrics   │  │
│  └────────────┬────────────┘                   └────────────┬────────────┘  │
│               │                                             │               │
│               └──────────────────────┬──────────────────────┘               │
│                                      ▼                                      │
│                        ┌───────────────────────────┐                        │
│                        │   ORCHESTRATION ENGINE    │                        │
│                        │ Safest Achievable Action  │                        │
│                        │ Explainable Rationale     │                        │
│                        │ Human-in-the-Loop Review  │                        │
│                        └─────────────┬─────────────┘                        │
│                                      ▲                                      │
│               ┌──────────────────────┴──────────────────────┐               │
│               │                                             │               │
│  ┌────────────┴────────────┐                   ┌────────────┴────────────┐  │
│  │       SIGNALGRAPH       │                   │      BPUT BASELINE      │  │
│  │ Aggregated Telemetry    │                   │ Intake, Voice, OCR,     │  │
│  │ Regional Disease Trends │                   │ Translation, Consent,   │  │
│  │ Operational Congestion  │                   │ Reviewer Gate           │  │
│  └─────────────────────────┘                   └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pillar 1: CAREGRAPH
- Models the patient's longitudinal clinical state across encounters.
- Maintains temporal graphs of reported symptoms, extracted lab vitals, and physician observations.
- Explicitly quantifies evidence uncertainty and missing information gaps.
- Strictly non-diagnostic: organizes observations into clinical trajectories without asserting definitive pathology.

### Pillar 2: FACILITYGRAPH
- Models the healthcare facility's operational capabilities (e.g. emergency resuscitation, neonatal care, blood bank, CT scanner, dialysis).
- Tracks live operational capacity, staffed bed occupancy, and transfer feasibility.
- Validates whether an indicated care pathway is achievable at the current facility or requires structured referral.

### Pillar 3: SIGNALGRAPH
- Aggregates de-identified, synthetic epidemiological and operational signals across facilities.
- Detects syndromic surges (e.g. rising acute respiratory illness, vector-borne febrile spikes) to contextualize patient presentations.
- Monitors queue backlog pressure and facility throughput delays.

### Pillar 4: ORCHESTRATION ENGINE
- Synthesizes patient state (CareGraph), care feasibility (FacilityGraph), and system context (SignalGraph).
- Recommends the **safest achievable next care action** (e.g. immediate casualty stabilization, priority outpatient queue, specialized tertiary referral with advance capability match).
- Enforces mandatory qualified human verification before any recommendation is finalized.

---

## 3. Core Safety Mandates

1. **Non-Diagnostic:** The system never issues autonomous medical diagnoses or prescribes treatment regimens.
2. **Advisory & Reviewer-Facing:** All outputs are formatted as clinical decision-support summaries for licensed healthcare workers.
3. **Deterministic Urgency Overrides:** Hardcoded safety rules immediately flag red-flag presentations (respiratory compromise, shock, acute hemorrhage, altered mental status) regardless of AI model outputs.
4. **Privacy-First:** Automatic PII scrubbing, synthetic identifiers, minimal 24-hour data retention, and zero external patient data leakage.
