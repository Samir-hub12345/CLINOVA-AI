# CLINOVA AI — Static Design Wireframes & Screen Specifications Atlas

> **Directory:** `docs/design/`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Design Atlas Organization

This directory contains the exhaustive static visual wireframes, information hierarchies, state transitions, and interaction specifications for all **40 screens** defined in the CLINOVA AI platform.

These design specifications serve as the immutable visual contract for Phase 3 frontend implementation. In accordance with the **Strict Phase 1 Boundaries**, these documents represent static design specifications and structural ASCII wireframes; no production application UI code has been implemented in Phase 1.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA DESIGN ATLAS STRUCTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ├── README.md (This Directory Index & Global Design Tokens)               │
│  ├── 01_PUBLIC_AND_AUTH_SCREENS.md (Screens 01–04)                          │
│  │   ├── Screen 01: Public Landing Page                                     │
│  │   ├── Screen 02: Product & Innovation Page                               │
│  │   ├── Screen 03: User Login                                              │
│  │   └── Screen 04: Role Selection                                          │
│  ├── 02_INTAKE_AND_EXTRACTION_SCREENS.md (Screens 05–12)                    │
│  │   ├── Screen 05: Patient Entry Mode Selector (Regular vs Emergency)      │
│  │   ├── Screen 06: Patient Information & Narrative Intake                  │
│  │   ├── Screen 07: Voice Symptom Intake (Whisper Audio)                    │
│  │   ├── Screen 08: Medical Report & Prescription Upload                    │
│  │   ├── Screen 09: Extraction & Visual Entity Review                       │
│  │   ├── Screen 10: Longitudinal Patient Timeline                           │
│  │   ├── Screen 11: Missing Information & Contradiction Audit               │
│  │   └── Screen 12: Dynamic Follow-up Question Engine (NBI)                 │
│  ├── 03_STAFF_AND_CONSOLIDATION_SCREENS.md (Screens 13–15)                  │
│  │   ├── Screen 13: Staff Assignment Workspace                              │
│  │   ├── Screen 14: Staff Missing-Data & Vitals Checklist                   │
│  │   └── Screen 15: Consolidated Master Case View                           │
│  ├── 04_CAREGRAPH_AND_DOCTOR_WORKBENCH.md (Screens 16–23)                   │
│  │   ├── Screen 16: CAREGRAPH Interactive Patient State View                │
│  │   ├── Screen 17: Risk & Acuity Trajectory Monitor                        │
│  │   ├── Screen 18: Uncertainty & Evidence Provenance Inspector             │
│  │   ├── Screen 19: Structured Triage Note Editor                           │
│  │   ├── Screen 20: Master Clinical Report (View / Download / Print)        │
│  │   ├── Screen 21: Doctor Prioritized Queue                                │
│  │   ├── Screen 22: Doctor Comprehensive Case Overview                      │
│  │   └── Screen 23: Doctor Verify / Modify / Add Audit Workspace            │
│  ├── 05_FACILITY_ORCHESTRATION_AND_PATHWAYS.md (Screens 24–31)              │
│  │   ├── Screen 24: FACILITYGRAPH Local Capability Inspector                │
│  │   ├── Screen 25: Facility Comparison & Care Feasibility Matrix           │
│  │   ├── Screen 26: ORCHESTRATION Engine Recommendation Screen              │
│  │   ├── Screen 27: Routine Home Care & Follow-up Calendar (Pathway A)      │
│  │   ├── Screen 28: Further Review & Single Revisit Scheduler (Pathway B)   │
│  │   ├── Screen 29: Inpatient Ward Admission Request (Pathway C)            │
│  │   ├── Screen 30: Staff Admission Verification                            │
│  │   └── Screen 31: Transfer & SBAR Handoff Screen                          │
│  ├── 06_EMERGENCY_AND_OT_SCREENS.md (Screens 32–36)                         │
│  │   ├── Screen 32: Emergency Fast-Track Intake                             │
│  │   ├── Screen 33: Emergency Resuscitation Bay Workspace                  │
│  │   ├── Screen 34: Operation Theatre (OT) Surgical Safety Checklist        │
│  │   ├── Screen 35: Purpose-Specific Emergency Report (Report Type 5)       │
│  │   └── Screen 36: Purpose-Specific OT Surgical Report (Report Type 6)      │
│  └── 07_CONTINUITY_SIGNALGRAPH_AND_ADMIN.md (Screens 37–40)                 │
│      ├── Screen 37: Longitudinal Follow-up & Real Outcome Tracker           │
│      ├── Screen 38: SIGNALGRAPH Regional Surveillance & Epidemic Heatmap    │
│      ├── Screen 39: Facility & System Capacity Operational Analytics        │
│      └── Screen 40: System Audit, Security & Safety Compliance Inspector    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Standard Screen Specification Template

Every screen specification in this atlas documents fourteen explicit engineering dimensions:
1. **Purpose:** The clinical or operational reason for the screen's existence.
2. **Actor:** Authorized roles permitted to view and interact with the screen.
3. **Entry Condition:** Pre-requisite state or authentication gate required to navigate to the screen.
4. **Inputs:** User-entered forms, uploads, or state queries.
5. **Outputs:** Rendered information, clinical cards, charts, and tables.
6. **Actions:** Primary and secondary button actions available to the user.
7. **Navigation:** Incoming routes and forward destination routes.
8. **Normal State:** Visual layout and content in standard operational state.
9. **Loading State:** Skeleton UI structure displayed during asynchronous fetches.
10. **Empty State:** Descriptive message and recovery action when zero data exists.
11. **Error State:** Explainable error card with retry/fallback options.
12. **Permission State:** Security notice displayed when unauthorized roles attempt access.
13. **Mobile Behavior:** Responsive reflow rules for tablet and smartphone viewports.
14. **Master Case & Graph Linkage:** Direct relationship to `case_id`, CAREGRAPH, FACILITYGRAPH, SIGNALGRAPH, and ORCHESTRATION.
