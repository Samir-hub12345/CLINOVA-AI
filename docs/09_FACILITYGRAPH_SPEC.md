# CLINOVA AI — FACILITYGRAPH Detailed Technical Specification

> **Document ID:** `DOC-09`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Architectural Role & Core Purpose

**FacilityGraph** is the facility-level care feasibility and network intelligence engine of CLINOVA AI. It models healthcare facilities, equipment availability, staff specialties, bed capacities, and inter-facility transit times across a coordinated regional network.

FacilityGraph answers the decisive operational question:
$$\mathbf{Can\ the\ required\ care\ actually\ be\ delivered\ here,\ and\ where\ else\ can\ it\ safely\ happen?}$$

In acute care, recommending an intervention that the current facility cannot physically execute (e.g., emergent cardiac catheterization at a rural PHC) is dangerous. FacilityGraph ensures that every clinical pathway suggested by CLINOVA AI is **operationally feasible** on-site or intelligently routed to a capable destination.

---

## 2. Regional Facility Network Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FACILITYGRAPH REGIONAL NETWORK MODEL                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ Rural PHC Alpha ] ────── 18 km / 25 min ──────> [ CHC Beta ]            │
│          │                                                │                 │
│          │ 42 km / 55 min                                 │ 32 km / 40 min  │
│          ▼                                                ▼                 │
│   [ Sub-District Hospital Gamma ] ─── 22 km / 30 min ───> [ District Hosp ] │
│                                                                   │         │
│                                                                   │ 58 km   │
│                                                                   ▼ 70 min  │
│                                                       [ Tertiary Med Coll ] │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The 5 Representative Network Tiers

| Facility ID | Facility Name | Tier | Core Capabilities | Diagnostic Labs & Imaging | Critical Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FAC-PHC-01` | Angul Rural PHC | Level 1 (PHC) | Outpatient triage, Oral meds, Basic wound care, Normal delivery | Point-of-care capillary glucose, Urine dipstick, Malarial RDT | Zero blood bank, No X-ray, No CT, No ICU, No surgeon. |
| `FAC-CHC-02` | Talcher Community Health Center | Level 2 (CHC) | Resuscitation bay, Minor OT, Oxygen concentrators, 4-bed maternity | Plain X-ray, Basic microscopy, CBC analyzer, Biochemistry | No CT scanner, No ICU, Blood storage limited to 4 units. |
| `FAC-SDH-03` | Dhenkanal Sub-District Hospital | Level 3 (SDH) | General Surgery, Emergency Room, Blood Storage Center, HDU (4 beds) | Ultrasound, Digital X-ray, Automated Hematology, ECG | CT scanner offline after 8 PM, No pediatric intensivist. |
| `FAC-DH-04` | Cuttack District Headquarters Hospital | Level 4 (DH) | Full Emergency Dept, 12-bed ICU, Blood Bank (PRBC, FFP), Multi-specialty OT | 24/7 CT Scanner, Arterial Blood Gas, Troponin, Ultrasound, Microbiology | High queue pressure (ED wait times 90–150 min), ICU occupancy ~90%. |
| `FAC-TMC-05` | SCB Medical College & Hospital | Level 5 (Tertiary) | Level 1 Trauma Center, Neuro-trauma ICU, Cardiac Cath Lab, Dialysis, PICU/NICU | MRI, 128-slice CT, Comprehensive Blood Bank with Platelets, Pathology | Heavy regional tertiary load; reserved for complex/critical transfers. |

---

## 3. Care Feasibility Matching Algorithm

When CareGraph identifies an acute clinical syndrome, the Orchestration Engine derives a **Required Clinical Care Bundle** ($\mathcal{B}_{\text{req}}$).

### 3.1 Care Bundle Typology
Examples of required bundles:
- `BUNDLE_STROKE_ACUTE`: `{"IMAGING": "CT_HEAD_NON_CONTRAST", "SPECIALTY": "NEUROLOGY", "CRITICAL_CARE": "ICU_BED", "THERAPEUTIC": "THROMBOLYTICS"}`
- `BUNDLE_STEMI_CARDIAC`: `{"DIAGNOSTIC": "12_LEAD_ECG", "LAB": "TROPONIN_I", "SPECIALTY": "CARDIOLOGY", "INTERVENTION": "CATH_LAB", "CRITICAL_CARE": "CCU_BED"}`
- `BUNDLE_SEPSIS_SEVERE`: `{"LAB": "BLOOD_CULTURES_LACTATE", "THERAPEUTIC": "IV_BROAD_SPECTRUM", "RESUSCITATION": "OXYGEN_HIGH_FLOW", "CRITICAL_CARE": "HDU_BED"}`
- `BUNDLE_SNAKEBITE_ENVENOMATION`: `{"PHARMACY": "POLYVALENT_ANTIVENOM", "RESUSCITATION": "MECHANICAL_VENTILATOR", "MONITORING": "WHOLE_BLOOD_CLOTTING_TEST"}`

### 3.2 Dynamic Feasibility Assessment

For facility $F$ and bundle $\mathcal{B}_{\text{req}}$:
```python
def evaluate_feasibility(facility: Facility, bundle: CareBundle) -> FeasibilityResult:
    # 1. Structural Capability Check
    missing_capabilities = []
    for cap in bundle.required_capabilities:
        if not facility.has_capability(cap) or not facility.is_equipment_operational(cap):
            missing_capabilities.append(cap)
            
    if missing_capabilities:
        return FeasibilityResult(
            status="INFEASIBLE",
            reason=f"Facility lacks required capabilities: {missing_capabilities}"
        )
        
    # 2. Operational Capacity Check
    critical_bed_type = bundle.required_bed_type
    available_beds = facility.get_available_beds(critical_bed_type)
    if available_beds <= 0:
        return FeasibilityResult(
            status="DEGRADED",
            reason=f"Facility has capability but 0 available {critical_bed_type} beds (Occupancy: 100%)"
        )
        
    # 3. Consumable Stock Check
    for consumable, min_qty in bundle.required_consumables.items():
        if facility.get_stock(consumable) < min_qty:
            return FeasibilityResult(
                status="DEGRADED",
                reason=f"Critical consumable shortage: {consumable}"
            )
            
    return FeasibilityResult(
        status="FEASIBLE",
        available_beds=available_beds,
        estimated_wait_minutes=facility.ed_wait_time
    )
```

---

## 4. Network Referral Routing & Ranking

When current facility feasibility is `INFEASIBLE` or `DEGRADED`, FacilityGraph executes multi-criteria network ranking across all reachable facilities:

### 4.1 Safe Referral Suitability Score ($\mathcal{S}_{\text{referral}}$)
$$\mathcal{S}_{\text{referral}}(F_i) = w_1 \cdot \text{FeasibilityScore}(F_i) + w_2 \cdot \left(1.0 - \frac{T_{\text{transit}}(F_i)}{T_{\text{max\_safe}}}\right) + w_3 \cdot \left(1.0 - \text{CongestionFactor}(F_i)\right)$$

Where:
- $\text{FeasibilityScore}(F_i) \in \{1.0 \text{ (Feasible)}, 0.5 \text{ (Degraded)}, 0.0 \text{ (Infeasible)}\}$
- $T_{\text{transit}}(F_i)$: Estimated emergency ground transport transit time in minutes.
- $T_{\text{max\_safe}}$: Clinical golden-hour ceiling for the presenting condition (e.g., 60 min for acute stroke, 90 min for STEMI).
- $\text{CongestionFactor}(F_i)$: Real-time facility queue saturation ($\in [0.0, 1.0]$).

---

## 5. Downstream Deliverables

1. **Care Pathway Influencing:** Directly informs the Orchestration Engine whether the safest action is to `CONTINUE` treatment on-site or initiate immediate `REFER`.
2. **SBAR Transfer Packet:** Automatically pre-fills receiving hospital details, clinical justification, and bed reservation requests.
3. **Capacity Warning Feed:** Broadcasts facility strain events directly into **SignalGraph**.
