# CLINOVA AI — FACILITYGRAPH Dynamic Capability & Resource Architecture

> **Document ID:** `RES-141`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Health Systems Operations & Clinical Network Engineering Group  

---

## 1. Architectural Mandate: Eliminating Blind Referrals

A fatal vulnerability in Indian district health networks is the **blind referral**: A Primary Health Centre (PHC) refers an acute trauma or septic patient to a higher facility without knowing whether that hospital's CT scanner is broken, its ICU beds are full, or its blood bank lacks O-negative units. Patients arrive in ambulances only to be turned away, frequently dying in transit (*Paschim Banga* emergency doctrine violation).

**FACILITYGRAPH** eliminates blind referrals by dynamically modeling:
1. Operational clinical capabilities at every regional facility
2. Resource availability (ventilators, ICU beds, oxygen pressure, specialists)
3. Telemetry freshness and operational verification status
4. Patient-specific care requirement bundles
5. Mathematical feasibility of transfer within the clinical golden hour

---

## 2. Capability & Resource Data Model

FACILITYGRAPH represents facilities not as static geographic pins, but as dynamic resource nodes in the regional health network:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FACILITYGRAPH RESOURCE HIERARCHY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ FACILITY NODE: `facilities` ]                                            │
│  ├── facility_code: "DH-KORAPUT-01"                                         │
│  ├── tier: LEVEL_4_DH (District Hospital)                                   │
│  ├── coordinates: (Lat: 18.8135, Long: 82.7123)                             │
│  ├── bed_capacity: {icu_total: 12, icu_free: 2, gen_total: 150, gen_free: 18}│
│  └── ed_status: {waiting_patients: 14, avg_wait_minutes: 25}                │
│                               │                                             │
│                               ▼                                             │
│  [ CAPABILITY ATOMS: `facility_capabilities` ]                              │
│  ├── CT_SCAN_24_7         ──► is_operational: True                          │
│  ├── BLOOD_BANK_PRBC      ──► is_operational: True                          │
│  ├── EMERGENCY_SURGERY_OT ──► is_operational: True                          │
│  ├── ICU_VENTILATOR_CARE  ──► is_operational: False (Compressor maintenance)│
│  └── PEDIATRIC_SNCU       ──► is_operational: True                          │
│                               │                                             │
│                               ▼                                             │
│  [ TELEMETRY VERIFICATION & FRESHNESS ]                                     │
│  ├── verification_status: VERIFIED (Attested by Facility Superintendent)    │
│  ├── reported_at: 2026-10-08T09:15:00Z                                      │
│  ├── freshness_window: 4 hours (Status: CURRENT / STALE)                    │
│  └── contact_number: "+91-6852-250100"                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Five Epistemic Freshness States
Facility telemetry is classified across five operational states to prevent reliance on outdated information:
1. `KNOWN`: Telemetry reported but pending formal administrative attestation.
2. `VERIFIED`: Explicitly attested by the on-duty facility administrator or automated telemetry probe within the freshness window ($T \le 4\text{ hours}$).
3. `STALE`: Telemetry older than the freshness window ($T > 4\text{ hours}$); flags that bed/equipment status must be confirmed by phone before dispatch.
4. `CONFLICTING`: Discrepancy between automated sensor data (e.g. bed occupancy sensor) and staff report.
5. `UNKNOWN`: No capability data received from facility within 24 hours; treated as unavailable for emergency routing.

---

## 3. Clinical Bundle Matching & Care Feasibility Synthesis

When a clinician reviews a patient, CLINOVA determines the **Required Clinical Care Bundle** ($B_{\text{req}}$) from the patient's presenting syndrome and acuity:

| Clinical Syndrome | Acuity Tier | Required Care Bundle ($B_{\text{req}}$) |
| :--- | :--- | :--- |
| **Acute Polytrauma / Shock** | CRITICAL | `EMERGENCY_SURGERY_OT` $\land$ `BLOOD_BANK_PRBC` $\land$ `CT_SCAN_24_7` $\land$ `ICU_VENTILATOR` |
| **Acute Myocardial Infarction** | CRITICAL | `TROPONIN_LAB` $\land$ `CARDIOLOGY_ICU` $\land$ `THROMBOLYSIS_STK` $\land$ `24_7_ECG` |
| **Severe Preeclampsia / Hemorrhage** | URGENT | `EMERGENCY_C_SECTION_OT` $\land$ `BLOOD_BANK` $\land$ `OBSTETRIC_SPECIALIST` |
| **Severe Pediatric Pneumonia** | URGENT | `PEDIATRIC_SNCU` $\land$ `HIGH_FLOW_OXYGEN` $\land$ `PAED_RESIDENT` |
| **Uncomplicated Cellulitis** | ROUTINE | `BASIC_PHARMACY` $\land$ `OUTPATIENT_DRESSING` |

### Feasibility Gating Formula
A target destination facility $F$ is mathematically feasible for patient $P$ if and only if:

$$\text{Feasible}(F, P) = \left(\bigwedge_{c \in B_{\text{req}}} \text{Operational}(F, c)\right) \land \left(\text{FreeBeds}(F, B_{\text{req}}) \ge 1\right) \land \left(T_{\text{transit}}(F_{\text{curr}}, F) \le T_{\text{golden\_hour}}(P)\right)$$

Where:
- $\text{Operational}(F, c)$ requires capability $c$ to be operational and in `CURRENT` or `VERIFIED` state.
- $T_{\text{transit}}$ is calculated using local Haversine distance and regional road speed factors.
- $T_{\text{golden\_hour}}$ is the physiological window before irreversible decompensation (e.g., 60 minutes for hemorrhagic shock; 120 minutes for ischemic stroke).

---

## 4. Integration with Care Pathways & Workflows

```
                          ┌───────────────────────────┐
                          │   Master Case & Bundle    │
                          │   Required: STROKE_CARE   │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │    FACILITYGRAPH Engine   │
                          │   Scans Regional Network  │
                          └─────────────┬─────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             │                          │                          │
             ▼                          ▼                          ▼
   [ LOCAL PHC EVALUATION ]   [ WARD / OT DISPATCH ]     [ INTER-FACILITY REFERRAL ]
   • Can PHC manage? NO       • Local DH has OT: YES     • Filters 6 nearby hospitals
   • Action: ROUTE_OUTWARD    • Local DH has ICU: NO     • Selects Dist. Hosp A:
                              • Action: PREP_REFERRAL    │  - CT: Operational (Verified)
                                                         │  - ICU Bed: 2 Available
                                                         │  - Transit: 42 min (< 60 min)
                                                         └──► Generates SBAR Transfer Pack
```

### Anti-Blind Referral Invariant
**Invariant FG-1:** Under no circumstances will CLINOVA generate an inter-facility referral recommendation targeting a destination facility that has status `UNKNOWN`, broken required equipment, or zero available required beds. If no regional facility meets 100% of the bundle, CLINOVA escalates to District Health Command with an explicit alert highlighting regional capacity failure.
