# CLINOVA AI — FACILITYGRAPH Journey Specification

> **Document ID:** `RES-65`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Concept & The Anti-Blind-Transfer Doctrine

In peripheral and district healthcare across India, a primary driver of preventable mortality is the phenomenon of **"blind transfers"**—dispatching critically ill or surgically urgent patients in an ambulance to a higher center without knowing whether the destination facility possesses an available ICU bed, functioning ventilator, matched blood units, or on-duty specialists.

$\text{FACILITYGRAPH}$ is CLINOVA's real-time, resource-aware operational network engine. It maps the multidimensional clinical requirements of a patient against the dynamic, verified operational capability of healthcare facilities across a regional referral network:

$$\text{Patient Needs Vector } \mathbf{N}_{\text{pt}} \quad \overset{\text{FACILITYGRAPH}}{\longleftrightarrow} \quad \text{Facility Capability Matrix } \mathbf{M}_{\text{fac}}$$

$$\Phi_{\text{feasibility}} = \min_{k} \left( \frac{\text{Resource}_{k,\text{available}}}{\text{Resource}_{k,\text{required}}} \right) \in [0.0, 1.0]$$

Where:
- $\Phi_{\text{feasibility}} = 1.0$: Fully feasible on-site.
- $\Phi_{\text{feasibility}} < 1.0$: Clinical deficit exists; requires external referral or emergency transfer.

---

## 2. Invocations Across the Master Patient Journey

$\text{FACILITYGRAPH}$ is dynamically invoked across six distinct journey stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FACILITYGRAPH INVOCATION POINTS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ INVOCATION 1: EMERGENCY TRIAGE CHECK ] ──> S22 (STATE_EMERGENCY_ACTIVE) │
│  Rapid sub-100ms check for immediate life-support capabilities.             │
│                                                                             │
│  [ INVOCATION 2: CLINICIAN REVIEW HUD ] ───> S12 (STATE_DOCTOR_REVIEWING)  │
│  Surfaces local diagnostic/bed availability to attending doctor.            │
│                                                                             │
│  [ INVOCATION 3: CARE FEASIBILITY AUDIT ] ──> S14 (STATE_FACILITY_EVALUATING)│
│  Computes Feasibility Index Phi comparing patient needs to local stock.     │
│                                                                             │
│  [ INVOCATION 4: INPATIENT WARD ROUTING ] ──> S18 (STATE_WARD_REQUESTED)    │
│  Verifies physical bed availability and ward staffing before order.         │
│                                                                             │
│  [ INVOCATION 5: INTER-FACILITY REFERRAL ] ─> S20 (STATE_REFERRAL_PENDING)  │
│  Multi-facility matching based on capability, distance, and transit time.   │
│                                                                             │
│  [ INVOCATION 6: SURGICAL THEATRE AUDIT ] ──> S23 (STATE_OT_PENDING)        │
│  Verifies scrub team, blood bank reserve, and anesthesia readiness.         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Deep-Dive Analysis of Operational Invocations

### 1. Emergency Acuity Invocation (`STATE_EMERGENCY_ACTIVE`)
- **Trigger:** Immediate presentation of life-threatening condition (e.g., severe polytrauma, eclampsia, acute coronary syndrome).
- **Evaluation:** Sub-100ms audit of mandatory resuscitation assets:
  - Is an emergency resuscitation bay staffed?
  - Is medical oxygen pressure adequate?
  - Are emergency endotracheal intubation supplies and defibrillators operational?
- **Behavior:** If local facility lacks essential life-support (e.g., peripheral rural PHC without blood or ventilator), $\text{FACILITYGRAPH}$ instantly generates an **Emergency Evacuation Corridor**, alerting the state emergency medical ambulance service (108) while local staff initiates bedside stabilization.

### 2. Routine Doctor Review HUD (`STATE_DOCTOR_REVIEWING`)
- **Trigger:** Clinician opens patient dossier for consultation.
- **Evaluation:** Visual HUD displays current hospital operational posture:
  - Local laboratory status: CBC turnaround time, biochemistry running.
  - Radiology status: X-ray technician present, USG operational.
  - Inpatient census: Total available male/female medical beds.
- **Benefit:** Clinician knows immediately whether ordering an ultrasound or admitting a patient is achievable today, preventing hours of patient administrative confusion.

### 3. Care Feasibility Gate (`STATE_FACILITY_EVALUATING`)
- **Trigger:** Clinician completes clinical verification (`STATE_CLINICIAN_VERIFIED`).
- **Evaluation:** Synthesizes patient requirements ($\mathbf{N}_{\text{pt}}$) against local resources:
  - *Example:* Patient diagnosed with severe acute pancreatitis requires: CT scan, ICU monitoring, IV octreotide, parenteral nutrition.
  - *Local Capability:* District hospital has HDU but no functional CT scanner (under maintenance) and no parenteral nutrition stock.
  - *Output:* Feasibility Index $\Phi_{\text{local}} = 0.00$ (Deficit: CT Scanner, TPN).
- **Result:** Automatically feeds Orchestration Engine to recommend **Inter-Facility Referral** to the nearest Medical College Hospital.

### 4. Inpatient Ward Bed Allocation (`STATE_WARD_REQUESTED`)
- **Trigger:** Clinician orders inpatient admission.
- **Evaluation:** Real-time bed occupancy audit across internal wards:
  - Verifies exact bed availability (e.g., Male Medical Ward: Bed M-04 is clean and unoccupied).
  - Verifies nurse-to-patient staffing ratio within safety standards (IPHS 2022).
- **Fallback:** If ward is 100% saturated, system flags: *"Male Medical Ward at capacity. Alternative: Step-Down Bay 2 or initiate transfer protocol."*

### 5. Inter-Facility Referral Destination Matching (`STATE_REFERRAL_PENDING`)
- **Trigger:** Clinician decides to transfer patient to higher center.
- **Matching Algorithm:** Ranks regional receiving hospitals using a multi-criteria optimization function:
  $$\text{Score}(\text{Fac}_j) = w_c \cdot \text{CapabilityMatch}_j + w_b \cdot \text{BedReadiness}_j - w_d \cdot \text{TravelTime}(\text{Transit}_j) - w_s \cdot \text{StalenessPenalty}_j$$
- **Output:** Returns a prioritized ranked list of candidate facilities with real-time contact details, distance, verified available beds, and active specialist rosters.

### 6. Emergency Surgical Theatre Gate (`STATE_OT_PENDING`)
- **Trigger:** Clinician orders emergent surgical intervention (e.g., laparotomy, emergency Cesarean section).
- **Evaluation:** Audits the 4 pillars of surgical readiness:
  1. *Operating Theatre Status:* Room sterile, scrub nurse on active duty.
  2. *Anesthesia Capability:* Anesthesiologist on-site or within 15-minute call-in radius.
  3. *Blood Bank Inventory:* Minimum 2 units of ABO/Rh-compatible packed red blood cells cross-matched or immediately cross-matchable.
  4. *Post-Operative Recovery:* Ventilated surgical ICU bed available for post-op emergence.

---

## 4. Resilience & Exception Handling in FACILITYGRAPH

Real-world healthcare infrastructure is volatile. $\text{FACILITYGRAPH}$ models six critical resource failure scenarios:

| Failure / Exception Scenario | Operational Detection | System Automated Response | Mandatory Human Action |
| :--- | :--- | :--- | :--- |
| **Unavailable Capability** | Local facility lacks required specialty or imaging modality. | Immediately sets Feasibility Index $\Phi_{\text{local}} = 0.0$; blocks local routine queue; promotes referral engine. | Attending doctor reviews candidate transfer destinations. |
| **Stale Capability Data** | Facility telemetry has not synced in $> 12\text{ hours}$. | Displays prominent amber `STALE TELEMETRY` warning badge; applies staleness penalty to ranking score. | Referral desk coordinator must execute mandatory phone verification before dispatch. |
| **Conflicting Resource Data** | Portal reports bed available, but nurse reports ward full. | Conflict arbitration: Physical nurse report takes precedence over digital portal data. | Ward sister confirms physical bed status via one-click toggle. |
| **Referral Rejected** | Destination hospital reports sudden ICU saturation upon inquiry. | Automatically removes facility from candidate pool; recalculates next-best facility in corridor. | Clinician approves alternate destination hospital. |
| **Transport / Ambulance Failure** | Dispatched ambulance suffers mechanical breakdown or delays $> 45\text{m}$. | Triggers transport SOS alert; re-queries 108 central dispatch for backup ambulance. | Health worker maintains bedside stabilization and re-checks vitals. |
| **Patient Refusal / AMA** | Patient/family refuses inter-facility transfer due to distance/cost. | System switches to **Maximum Safe On-Site Stabilization Mode**; logs Against Medical Advice (AMA) consent. | Clinician documents risk counseling; orders best-available oral/parenteral regimen. |

---

## 5. Patient State $\to$ Facility Feasibility Handoff Contract

The interface between clinical reasoning ($\text{CAREGRAPH}$) and operational resources ($\text{FACILITYGRAPH}$) is defined by a strict mathematical contract:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAREGRAPH ──> FACILITYGRAPH CONTRACT                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CAREGRAPH EXPORTS ]                                                      │
│  • Clinical Trajectory: DETERIORATING                                       │
│  • Physiological Acuity: P2 (Emergency Ward / HDU)                          │
│  • Specific Service Needs: [INVASIVE_VENTILATION, DIALYSIS_CAPABLE]         │
│  • Medication Needs: [IV_NORADRENALINE, STAT_CEFTRIAXONE]                   │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│  [ FACILITYGRAPH MATCHING ]                                                 │
│  • Evaluates Local Facility: Lacks Hemodialysis Unit                        │
│  • Phi_local = 0.0 (Dialysis Deficit)                                       │
│  • Queries Regional Graph:                                                  │
│    - District Hospital (28 km, Travel: 45 min): 2 HDU Beds, Dialysis OPEN   │
│    - Medical College (65 km, Travel: 90 min): 8 ICU Beds, Dialysis OPEN     │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│  [ ORCHESTRATION OUTPUT ]                                                   │
│  • Safest Achievable Pathway: Inter-Facility Referral to District Hospital  │
│  • Transport Class: Advanced Life Support (ALS) Ambulance with O2           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
