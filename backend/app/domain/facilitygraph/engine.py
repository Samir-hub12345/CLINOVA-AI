"""CLINOVA AI — FACILITYGRAPH Engine.

Facility-Level Care Feasibility & Regional Referral Intelligence.
Evaluates local facility capability against required clinical care bundles,
computes dynamic feasibility predicate Phi(F, B), ranks capable network destinations,
and generates standardized SBAR inter-facility transfer documentation.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


CARE_BUNDLES: Dict[str, Dict[str, Any]] = {
    "BUNDLE_STROKE_ACUTE": {
        "name": "Acute Ischemic Stroke Protocol",
        "required_capabilities": ["CT_SCAN_24_7", "ICU_BEDS", "THROMBOLYTICS"],
        "critical_bed_type": "ICU",
        "clinical_urgency": "EMERGENT_30_MIN",
    },
    "BUNDLE_STEMI_CARDIAC": {
        "name": "Acute STEMI / Cardiogenic Shock Protocol",
        "required_capabilities": ["ECG", "TROPONIN_LAB", "CARDIAC_CATH_LAB", "ICU_BEDS"],
        "critical_bed_type": "ICU",
        "clinical_urgency": "EMERGENT_60_MIN",
    },
    "BUNDLE_OBSTETRIC_HEMORRHAGE": {
        "name": "Emergency Obstetric Hemorrhage Protocol",
        "required_capabilities": ["BLOOD_BANK", "EMERGENCY_OT"],
        "critical_bed_type": "GENERAL",
        "clinical_urgency": "EMERGENT_15_MIN",
    },
    "BUNDLE_SEPSIS_SEVERE": {
        "name": "Severe Sepsis & Septic Shock Protocol",
        "required_capabilities": ["BLOOD_STORAGE", "HDU_BEDS", "OXYGEN_CONCENTRATOR"],
        "critical_bed_type": "HDU",
        "clinical_urgency": "URGENT_1_HOUR",
    },
    "BUNDLE_SNAKEBITE_ENVENOMATION": {
        "name": "Venomous Snakebite Envenomation Protocol",
        "required_capabilities": ["RESUSCITATION_BAY", "OXYGEN_CONCENTRATOR"],
        "critical_bed_type": "GENERAL",
        "clinical_urgency": "URGENT_1_HOUR",
    },
    "BUNDLE_TRAUMA_CRITICAL": {
        "name": "Polytrauma Critical Resuscitation Protocol",
        "required_capabilities": ["LEVEL_1_TRAUMA", "BLOOD_BANK", "ICU_BEDS", "EMERGENCY_OT"],
        "critical_bed_type": "ICU",
        "clinical_urgency": "IMMEDIATE_LIFE_THREAT",
    },
    "BUNDLE_ROUTINE_AMBULATORY": {
        "name": "Standard Outpatient Ambulatory Protocol",
        "required_capabilities": ["OUTPATIENT_TRIAGE", "ORAL_MEDS"],
        "critical_bed_type": "GENERAL",
        "clinical_urgency": "ROUTINE",
    },
}


def haversine_transit_estimate(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, int]:
    """
    Computes geographical distance in km and estimated ambulance transit in minutes
    accounting for regional road topography (rural factor 1.3, avg speed 45 km/h).
    """
    radius = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    distance_km = round(radius * c * 1.3, 1)  # 1.3 road tortuosity
    transit_minutes = max(5, int((distance_km / 45.0) * 60.0))
    return distance_km, transit_minutes


def evaluate_feasibility(
    facility: Dict[str, Any],
    bundle_code: str,
) -> Dict[str, Any]:
    """
    Evaluates the care feasibility predicate Phi(F, B).
    Returns status: FEASIBLE, DEGRADED, or INFEASIBLE with concrete reasons.
    """
    bundle = CARE_BUNDLES.get(bundle_code)
    if not bundle:
        return {
            "status": "FEASIBLE",
            "reason": f"Generic protocol without specific specialized capability constraints.",
            "missing_capabilities": [],
            "available_beds": facility.get("general_beds_available") or 1,
        }

    operational_caps = set()
    for cap in facility.get("capabilities", []):
        if isinstance(cap, dict):
            if cap.get("is_operational", True):
                operational_caps.add(cap.get("capability_code"))
        elif isinstance(cap, (tuple, list)):
            if len(cap) >= 2 and cap[1]:
                operational_caps.add(cap[0])
            elif len(cap) == 1:
                operational_caps.add(cap[0])
        elif hasattr(cap, "capability_code"):
            if getattr(cap, "is_operational", True):
                operational_caps.add(getattr(cap, "capability_code"))
        elif isinstance(cap, str):
            operational_caps.add(cap)

    missing_caps = [c for c in bundle["required_capabilities"] if c not in operational_caps]

    # 1. Structural Check
    if missing_caps:
        return {
            "status": "INFEASIBLE",
            "reason": f"Facility lacks essential operational capabilities: {', '.join(missing_caps)}",
            "missing_capabilities": missing_caps,
            "critical_bed_type": bundle["critical_bed_type"],
            "available_beds": 0,
        }

    # 2. Bed Capacity Check
    critical_bed_type = bundle["critical_bed_type"]
    if critical_bed_type == "ICU":
        available_beds = facility.get("icu_beds_available") or 0
    else:
        available_beds = facility.get("general_beds_available") or 0

    if available_beds <= 0:
        return {
            "status": "DEGRADED",
            "reason": f"Facility possesses required capabilities, but 0 available {critical_bed_type} beds (100% capacity saturation).",
            "missing_capabilities": [],
            "critical_bed_type": critical_bed_type,
            "available_beds": 0,
        }

    return {
        "status": "FEASIBLE",
        "reason": f"All required clinical capabilities active and {available_beds} {critical_bed_type} beds available on site.",
        "missing_capabilities": [],
        "critical_bed_type": critical_bed_type,
        "available_beds": available_beds,
    }


def rank_referral_destinations(
    current_facility: Dict[str, Any],
    network_facilities: List[Dict[str, Any]],
    bundle_code: str,
) -> List[Dict[str, Any]]:
    """
    Ranks destination facilities across the regional network based on capability match,
    bed capacity, ED queue wait times, and transit duration.
    """
    ranked = []
    curr_lat = current_facility.get("latitude", 20.5)
    curr_lon = current_facility.get("longitude", 85.5)

    for fac in network_facilities:
        if fac.get("id") == current_facility.get("id"):
            continue

        feasibility = evaluate_feasibility(fac, bundle_code)
        dist_km, transit_min = haversine_transit_estimate(
            curr_lat, curr_lon, fac.get("latitude", 20.5), fac.get("longitude", 85.5)
        )

        # Suitability Score Calculation
        score = 0.0
        if feasibility["status"] == "FEASIBLE":
            score += 100.0
        elif feasibility["status"] == "DEGRADED":
            score += 35.0
        else:
            score -= 100.0

        # Penalties and bonuses
        score -= (transit_min * 0.4)
        score += (feasibility.get("available_beds", 0) * 2.0)
        score -= (fac.get("ed_avg_wait_min", 20) * 0.15)

        ranked.append({
            "facility_id": fac.get("id"),
            "facility_name": fac.get("name"),
            "tier": fac.get("tier"),
            "feasibility_status": feasibility["status"],
            "feasibility_reason": feasibility["reason"],
            "missing_capabilities": feasibility["missing_capabilities"],
            "available_beds": feasibility.get("available_beds", 0),
            "distance_km": dist_km,
            "transit_minutes": transit_min,
            "ed_avg_wait_min": fac.get("ed_avg_wait_min", 20),
            "suitability_score": round(score, 1),
        })

    # Sort descending by suitability score
    ranked.sort(key=lambda x: x["suitability_score"], reverse=True)
    return ranked


def generate_sbar_packet(
    case_summary: Dict[str, Any],
    origin_facility: Dict[str, Any],
    destination_facility: Dict[str, Any],
    bundle_code: str,
) -> Dict[str, str]:
    """Generates a standardized SBAR clinical transfer packet."""
    bundle = CARE_BUNDLES.get(bundle_code, {"name": "Clinical Transfer", "clinical_urgency": "URGENT"})

    situation = (
        f"Inter-facility referral for patient {case_summary.get('patient_synthetic_id', 'SYN-PT')} "
        f"presenting with {case_summary.get('primary_syndrome', 'acute syndrome')} and acuity {case_summary.get('acuity_tier', 'URGENT')}. "
        f"Originating facility {origin_facility.get('name')} lacks on-site feasibility for {bundle['name']}."
    )

    background = (
        f"Patient presented with: '{case_summary.get('presenting_complaint', 'Symptoms reported')}'. "
        f"Baseline Acuity Score R_t = {case_summary.get('risk_score', 0.5)}, Trajectory slope Delta R = {case_summary.get('trajectory_slope', 0.0)}/hr. "
        f"Initial triage performed at {origin_facility.get('name')} ({origin_facility.get('tier')})."
    )

    assessment = (
        f"Clinical condition requires {bundle['name']}. "
        f"Latest vitals: HR {case_summary.get('vitals', {}).get('heart_rate', 'N/A')}, "
        f"BP {case_summary.get('vitals', {}).get('systolic_bp', 'N/A')}/{case_summary.get('vitals', {}).get('diastolic_bp', 'N/A')}, "
        f"SpO2 {case_summary.get('vitals', {}).get('spo2_percent', 'N/A')}%. "
        f"Local on-site care is INFEASIBLE. Receiving center {destination_facility.get('name')} confirmed capable."
    )

    recommendation = (
        f"Requesting immediate bed reservation and medical receiving team dispatch at {destination_facility.get('name')}. "
        f"Estimated road transit: ~{case_summary.get('transit_minutes', 30)} minutes via BLS/ALS ambulance. "
        f"Prepare on-arrival bundle: {', '.join(bundle.get('required_capabilities', []))}."
    )

    return {
        "sbar_situation": situation,
        "sbar_background": background,
        "sbar_assessment": assessment,
        "sbar_recommendation": recommendation,
        "required_bundle": bundle_code,
    }
