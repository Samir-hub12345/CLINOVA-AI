# FACILITYGRAPH — Facility Capability, Capacity & Care-Feasibility Intelligence

## 1. Domain Purpose
`FacilityGraph` models the operational capability and dynamic capacity of healthcare facilities across the care network. In rural and semi-urban health delivery, clinical urgency cannot be separated from care availability: routing a critical patient to a facility that lacks oxygen or emergency surgical coverage introduces lethal delays.

---

## 2. Core Entities & Topology

```
┌────────────────────────────────────────────────────────┐
│                   FACILITYGRAPH NODE                   │
├────────────────────────────────────────────────────────┤
│ • Facility Identifier & Tier (PHC / CHC / District)    │
│ • Service Capabilities:                                │
│   - Emergency Resuscitation & Oxygen Pipeline          │
│   - Intensive Care (ICU / HDU / NICU)                  │
│   - Diagnostic Lab Services (CBC, Biochemistry)        │
│   - Blood Storage / Blood Bank                         │
│   - Surgical Suites & Anesthesia On-Call               │
│ • Dynamic Operational Metrics:                         │
│   - Available Staffed Beds                             │
│   - Triage Queue Wait Estimate                         │
│   - Active Duty Roster (Medical Officer, Specialist)   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Care-Feasibility Validation Engine
Before any care action recommendation is generated:
1. The patient's clinical urgency and required care resources are matched against the current facility's `FacilityGraph` capabilities.
2. If the current facility **can** feasibly deliver the necessary intervention, local treatment pathways are prioritized.
3. If the required intervention exceeds local capability (e.g. emergency laparotomy at a rural PHC), the Orchestration Engine identifies the nearest reachable facility with verified capability and bed availability, generating a structured referral document.
