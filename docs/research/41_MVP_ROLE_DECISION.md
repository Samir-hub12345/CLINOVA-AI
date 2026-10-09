# CLINOVA AI — Hackathon MVP Role Rationalization & Minimization Decision

> **Document ID:** `RES-41`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Hackathon Product Strategy Group  

---

## 1. Executive Summary & Minimization Charter

A critical failure pattern in competitive hackathon engineering is **"Role Inflation"**: proliferating dozens of user roles and disconnected portals (Billing Clerk, Pharmacist, Radiologist, Insurance Auditor, Head Nurse, Hospital CEO) simply to make the product appear sophisticated on paper.

In reality, role inflation produces:
1. Fractured, half-implemented user interfaces with dead buttons.
2. Complex authentication overhead that breaks during live judge demonstrations.
3. Diffusion of engineering focus away from the core clinical problem: **Continuous Care Intelligence and Meaningful Human Control**.

> **The Hackathon Minimization Charter:**  
> Identify the **absolute minimum viable set of user roles** required to convincingly and flawlessly demonstrate the end-to-end CLINOVA care continuum (`B01` through `B18` + `C01` through `C10`), while strictly eliminating or combining non-essential personas.

---

## 2. Evaluation & Classification of Candidate Roles

Every proposed user role is evaluated against four strict criteria:
1. *Is it mandated by the BPUT problem statement?*
2. *Is it essential to demonstrate the core clinical innovations (CAREGRAPH, FACILITYGRAPH, SIGNALGRAPH, ORCHESTRATION)?*
3. *Can its functionality be integrated into an existing primary workflow without loss of fidelity?*
4. *Does maintaining a separate standalone interface add net negative demonstration complexity?*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ROLE CLASSIFICATION SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  CORE MVP ROLE       │ Mandatory for live hackathon demonstration           │
│  SUPPORTING MVP ROLE │ Integrated as a tab / mode within a core interface   │
│  OPTIONAL MVP ROLE   │ Config drawer / developer utility for evaluation     │
│  FUTURE ROLE         │ Post-hackathon grant / enterprise deployment roadmap │
│  REMOVE              │ Out of scope; explicitly excluded from product       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Granular Role Classification Table

| Candidate Role | Hackathon MVP Classification | Analytical Justification & Architectural Decision |
|:---|:---:|:---|
| **1. Primary Clinician / Medical Officer / Qualified Reviewer** | **CORE MVP ROLE** | **MANDATORY.** Supreme clinical decision-maker. Required for BPUT Reviewer Dashboard (`B12`), non-diagnostic HITL sign-off (`B18`), CAREGRAPH inspection (`C01`), FACILITYGRAPH review (`C05`), and Orchestration sign-off (`C08`). The Doctor Workbench is the central demonstration interface. |
| **2. Nurse / Frontline Health Worker (ANM / ASHA)** | **CORE MVP ROLE** | **MANDATORY.** Frontline intake gatekeeper. Required for BPUT Voice/Text Intake (`B01`, `B02`), document scanning (`B03`, `B04`), Missing-Data Checklist (`B07`), vital signs acquisition, red-flag checklists, and emergency escalation. |
| **3. Patient** | **CORE MVP ROLE** | **MANDATORY.** Frontline intake initiator. Required for self-service intake demonstration, multilingual vernacular voice entry (Odia/Hindi), document upload, answering clarifying questions (`B08`), and receiving the final approved care summary. |
| **4. Caregiver / Patient Attendant** | **SUPPORTING MVP ROLE** | **COMBINED WITH PATIENT.** Does NOT require an independent standalone codebase. Caregiver workflows are modeled as an **"Assisted / Attendant Mode" toggle** within the Patient Intake Portal (`DOC-02`, `RES-36`), capturing surrogate consent and guardian relationships cleanly without UI duplication. |
| **5. Referral / Transfer Staff** | **SUPPORTING MVP ROLE** | **COMBINED WITH CLINICIAN / WARD DESK.** Crucial for demonstrating FACILITYGRAPH destination matching (`C05`, `C06`) and 108 ambulance dispatch (`B13`). However, to avoid tab-switching chaos during a 5-minute live demo, referral logistics are surfaced directly as a dedicated **"Referral & Transfer Coordination Tab"** accessible from the Doctor Workbench. |
| **6. Facility Administrator** | **SUPPORTING MVP ROLE** | **SIMPLIFIED CONFIG DRAWER.** Essential for demonstrating how changes in institutional capacity (e.g., toggling ICU beds from 2 to 0) alter algorithmic care feasibility in FACILITYGRAPH. Implemented as an elegant **"Facility Resource Drawer / Demo Controls"** modal rather than an entire enterprise administrative sub-app. |
| **7. System Administrator** | **OPTIONAL MVP ROLE** | **DEVELOPER SETTINGS DRAWER.** Handled via a streamlined Settings modal displaying server health, local SQLite database status, local Ollama/Whisper latency metrics, and cryptographic audit log views (`B17`). |
| **8. Research / Evaluation User** | **FUTURE ROLE** | **DEFERRED TO OFFLINE HARNESS.** Continuous model fine-tuning (`C11`) and massive batch evaluation belong to offline research scripts (`tests/` and CLI evaluation runners). Does not require a multi-tenant production UI role during the live hackathon demonstration. |
| **9. Pharmacist** | **REMOVE** | **OUT OF SCOPE.** Routine dispensary billing and pharmaceutical inventory management is standard ERP functionality that distracts from acute triage and care navigation. |
| **10. Billing / Insurance Clerk** | **REMOVE** | **OUT OF SCOPE.** Financial claims processing is explicitly outside the clinical care intelligence mandate. |
| **11. Radiologist / Lab Technician** | **REMOVE** | **OUT OF SCOPE.** Discrete lab extraction is demonstrated via the document OCR ingestion pipeline (`B03`, `B04`); building a separate Laboratory Information System (LIS) workstation bloats the project. |

---

## 3. The Minimum Viable Role Set for Hackathon Demonstration

By consolidating supporting roles into contextual modes and drawers, the hackathon MVP is reduced to **exactly THREE primary visual interfaces**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE MINIMUM VIABLE ROLE SET (3 CORE UIs)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ INTERFACE 1: INTAKE PORTAL ]                                             │
│  ├── Actor: Patient / Caregiver / Health Worker                             │
│  ├── Modes: Self-Service Kiosk  |  Assisted Triage  |  Vernacular Voice     │
│  └── Capabilities: Voice (Odia/Hindi), OCR Upload, NBI Questions, Consent   │
│                                                                             │
│  [ INTERFACE 2: NURSE TRIAGE WORKSTATION ]                                  │
│  ├── Actor: Triage Nurse / ANM / Community Health Worker                    │
│  ├── Modes: Missing-Data Worklist  |  Bedside Vitals  |  Red Flag Escalation │
│  └── Capabilities: Serial vitals, Checklist completion, Single Master Case  │
│                                                                             │
│  [ INTERFACE 3: DOCTOR REVIEWER WORKBENCH ]                                 │
│  ├── Actor: Primary Clinician / Medical Officer / Qualified Reviewer        │
│  ├── Integrated Tabs: Dynamic Queue  |  CAREGRAPH State  |  Evidence Drawer │
│  │                   FACILITYGRAPH Matching  |  Referral Desk               │
│  └── Capabilities: Verify/Modify/Add, Sign-off, MHC Overrides, Outcome Loop │
│                                                                             │
│  [ GLOBAL OVERLAY: DEMO & FACILITY SETTINGS DRAWER ]                        │
│  ├── Actor: Evaluator / Facility Admin / System Inspector                   │
│  └── Capabilities: Toggle ICU beds, simulate Dengue surge, inspect Audit Log│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Demonstration Flow Across the Minimal Role Set

This consolidated architecture allows a judge or reviewer to witness the **entire continuous care continuum in under 4 minutes** without logging in and out of 8 different accounts:

1. **Step 1 (Intake Station):** Reviewer speaks symptoms in Odia (*"Mu mundabindha heuchi, 3 dina heba jwara"*); system transcribes audio; OCR parses uploaded CBC slip; patient answers 2 clarifying questions.
2. **Step 2 (Nurse Station):** Case appears in Nurse Missing-Data Worklist; nurse enters BP and SpO2; CAREGRAPH updates; case promoted into Doctor Queue.
3. **Step 3 (Doctor Workbench):** Doctor opens patient; reviews 30-second summary; clicks CBC platelet value to inspect raw OCR crop in $< 300$ms; trajectory shows `WORSENING`; uncertainty shows missing chest X-ray.
4. **Step 4 (Facility & Referral Demo):** Doctor opens FACILITYGRAPH tab; local PHC shows `INSUFFICIENT`; system matches nearest District Hospital with verified open ICU bed; doctor signs Structured Referral Pack.
5. **Step 5 (Simulation Drawer):** Reviewer opens Demo Drawer; inspects immutable SHA-256 audit log entry of doctor's sign-off; toggles SIGNALGRAPH Dengue surge to observe live clinic banner.

---

## 5. Architectural Verdict

The 3-Interface / 3-Core-Role architecture represents the **optimal balance of clinical rigor and demonstration reliability**:
- It delivers **100% of the 18 BPUT Baseline requirements** (`B01`–`B18`).
- It demonstrates **all 10 verified Innovation Capabilities** (`C01`–`C10`).
- It completely eliminates redundant codebase bloat, permission collision risks, and presentation failures.
