# CLINOVA AI — Comprehensive Feature Inventory

> **Document ID:** `DOC-05`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Feature Architecture Taxonomy

Every feature in CLINOVA AI belongs to one of seven functional layers:
- `LAYER-01`: Public Clinical Technology Website
- `LAYER-02`: Identity, Authentication & Role-Based Workspaces
- `LAYER-03`: BPUT Multimodal Intake & Baseline Capabilities
- `LAYER-04`: CareGraph (Patient State, Trajectory & Evidence)
- `LAYER-05`: FacilityGraph (Care Feasibility & Network Routing)
- `LAYER-06`: SignalGraph (System Telemetry & Epidemiological Surges)
- `LAYER-07`: Orchestration Engine & Clinical Decision Workstation

---

## 2. Feature Inventory Matrix

| Feature ID | Feature Name | Layer | UI Component | API Route | Data Model | Downstream Effect | Integration Criteria Satisfied? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FEAT-001** | Public Clinical Landing | `LAYER-01` | `src/app/page.tsx` | `GET /` | N/A | Explains 4 pillars & BPUT baseline | In Progress (Phase 1 clean baseline) |
| **FEAT-002** | System Status & Safety API | `LAYER-02` | Status Header Banner | `GET /api/v1/status` | Settings | Informs client of operational mode | Fully Integrated |
| **FEAT-003** | Clinical Safety Policy Endpoint | `LAYER-02` | Safety Modal Banner | `GET /api/v1/safety` | Settings | Enforces non-diagnostic governance | Fully Integrated |
| **FEAT-004** | Role-Based Auth & Session | `LAYER-02` | Auth Workspace Selector | `POST /api/v1/auth/*` | `User`, `Role` | Restricts access by clinical role | Planned (Phase 10) |
| **FEAT-005** | Text Symptom Intake Form | `LAYER-03` | Intake Narrative Input | `POST /api/v1/intake/text` | `Symptom`, `Case` | Ingests symptoms into CareGraph | Planned (Phase 11) |
| **FEAT-006** | Voice Symptom Recorder & STT | `LAYER-03` | Audio Mic & Visualizer | `POST /api/v1/intake/voice` | `Evidence` | Generates transcribed symptoms | Planned (Phase 11) |
| **FEAT-007** | Medical Document Uploader & OCR | `LAYER-03` | Drag-and-drop File Upload | `POST /api/v1/intake/ocr` | `Report`, `Evidence` | Parses report text into lab values | Planned (Phase 11) |
| **FEAT-008** | Missing Information Detection | `LAYER-03` | Missing Parameter Chips | `GET /api/v1/cases/{id}/missing` | `Uncertainty` | Triggers follow-up questions | Planned (Phase 11) |
| **FEAT-009** | Follow-up Question Prompter | `LAYER-03` | Targeted Q&A Accordion | `POST /api/v1/cases/{id}/questions` | `Question` | Answers lower CareGraph uncertainty | Planned (Phase 11) |
| **FEAT-010** | Multilingual Intake Engine | `LAYER-03` | Language Switcher | `POST /api/v1/intake/translate` | N/A | Translates text/prompts for patient | Planned (Phase 11) |
| **FEAT-011** | Dynamic Priority Queue | `LAYER-03` | Clinical Priority Waitlist | `GET /api/v1/cases/queue` | `CaseQueue` | Orders patients by risk & SLA | Planned (Phase 11) |
| **FEAT-012** | Informed Consent Gate | `LAYER-03` | Patient Consent Modal | `POST /api/v1/intake/consent` | `Consent` | Blocks intake until signed | Planned (Phase 11) |
| **FEAT-013** | PII Scrubber & Pseudonymizer | `LAYER-03` | Sanitization Badge | Internal Middleware | `Patient` | Generates `SYN-PT-XXXX` identifiers | Planned (Phase 11) |
| **FEAT-014** | CareGraph State Visualizer | `LAYER-04` | Graph & Timeline Canvas | `GET /api/v1/caregraph/{id}` | `CareGraph` | Visualizes patient trajectory | Planned (Phase 12) |
| **FEAT-015** | Risk Trajectory Calculator | `LAYER-04` | Trajectory Sparkline & Badge | `POST /api/v1/caregraph/{id}/eval`| `RiskScore` | Computes $\Delta R$ deterioration | Planned (Phase 12) |
| **FEAT-016** | Evidence Provenance Inspector | `LAYER-04` | Provenance Badge & Drawer | `GET /api/v1/cases/{id}/evidence` | `Evidence` | Distinguishes verified vs inferred | Planned (Phase 12) |
| **FEAT-017** | Uncertainty Quantification | `LAYER-04` | Uncertainty Meter ($\mathcal{U}_t$) | `GET /api/v1/caregraph/{id}/uncertainty`| `Uncertainty` | Feeds Orchestration Engine | Planned (Phase 12) |
| **FEAT-018** | Facility Capability Registry | `LAYER-05` | Facility Directory Table | `GET /api/v1/facilities` | `Facility` | Stores equipment, labs, bed types | Planned (Phase 13) |
| **FEAT-019** | Real-Time Feasibility Matcher | `LAYER-05` | Feasibility Matrix Card | `POST /api/v1/facilities/match`| `Capability` | Evaluates if care is deliverable | Planned (Phase 13) |
| **FEAT-020** | Network Referral Navigator | `LAYER-05` | Referral Route Map & List | `GET /api/v1/facilities/referrals` | `Referral` | Ranks feasible destination hospitals | Planned (Phase 13) |
| **FEAT-021** | SBAR Transfer Packet Generator | `LAYER-05` | Transfer Packet Preview | `POST /api/v1/referrals/sbar` | `Transfer` | Auto-generates SBAR packet | Planned (Phase 13) |
| **FEAT-022** | SignalGraph Surge Heatmap | `LAYER-06` | Network Telemetry Map | `GET /api/v1/signalgraph/surges`| `Signal` | Flags regional syndromic clusters | Planned (Phase 14) |
| **FEAT-023** | Bottleneck & Capacity Telemetry | `LAYER-06` | Department Load Gauges | `GET /api/v1/signalgraph/load` | `FacilityLoad`| Alerts on overloaded ED queues | Planned (Phase 14) |
| **FEAT-024** | Orchestration Next-Action Recommender | `LAYER-07` | Advisory Action Card | `POST /api/v1/orchestration/evaluate` | `Action` | Suggests `ASK`, `VERIFY`, `ESCALATE` | Planned (Phase 15) |
| **FEAT-025** | Clinician Decision Sign-off Gate | `LAYER-07` | 1-Click Action / Override Bar | `POST /api/v1/orchestration/decision` | `ClinicianDecision` | Human-in-the-loop mandatory lock | Planned (Phase 15) |
| **FEAT-026** | Outcome & Follow-up Recorder | `LAYER-07` | Outcome Disposition Modal | `POST /api/v1/cases/{id}/outcome` | `Outcome` | Closes case; feeds SignalGraph | Planned (Phase 16) |
| **FEAT-027** | Medicolegal Audit Event Log | `LAYER-07` | Audit Event Feed | `GET /api/v1/audit/logs` | `AuditLog` | Verifies full compliance history | Planned (Phase 17) |

---

## 3. Mandatory Integration Standard

Every feature committed in this project must adhere strictly to Section 13 of the Master Contract:
1. UI component exists and renders properly in dark/light mode.
2. Backend API route exists and returns strict Pydantic schemas.
3. Database model stores state changes persistently.
4. Data flows seamlessly across the end-to-end journey.
5. Connected to upstream and downstream clinical steps.
6. Handles happy paths, edge cases, and graceful degradation modes.
7. Verified in automated test suites and live browser verification.
