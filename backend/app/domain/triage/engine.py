"""CLINOVA AI — Deterministic Triage Engine.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.

Synthesizes:
- Physiological parameters & freshness
- Deterministic NEWS2 (RCP 2017)
- Deterministic Shock Index (Allgöwer & Burri)
- Rule-based red-flag evaluation
- Uncertainty & data completeness
- Operational queue priority

No LLM involvement. 100% Deterministic, testable, reproducible.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.domain.triage.scoring import (
    calculate_deterministic_news2,
    calculate_deterministic_shock_index,
    evaluate_vital_freshness,
    NEWS2_VERSION,
    SHOCK_INDEX_VERSION,
)
from app.domain.triage.red_flags import (
    evaluate_deterministic_red_flags,
    RED_FLAGS_VERSION,
)
from app.domain.triage.priority import (
    evaluate_priority_tier,
    PRIORITY_RULES_VERSION,
)

MASTER_RULESET_VERSION = f"{NEWS2_VERSION}+{SHOCK_INDEX_VERSION}+{RED_FLAGS_VERSION}+{PRIORITY_RULES_VERSION}"


def make_json_safe(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_safe(x) for x in obj]
    return obj


def compute_deterministic_triage(
    case_id: str,
    pathway: str,
    current_state: str,
    presenting_complaint: str = "",
    latest_vital: Optional[Any] = None,
    extracted_symptoms: Optional[List[str]] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Computes complete deterministic triage snapshot for a clinical case.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    # Extract vital parameters
    vital_dict: Dict[str, Any] = {}
    recorded_at: Optional[datetime] = None
    vital_id: Optional[str] = None

    if latest_vital is not None:
        if isinstance(latest_vital, dict):
            vital_dict = dict(latest_vital)
            recorded_at = latest_vital.get("recorded_at")
            vital_id = latest_vital.get("id")
        else:
            vital_dict = {
                "heart_rate": getattr(latest_vital, "heart_rate", None),
                "systolic_bp": getattr(latest_vital, "systolic_bp", None),
                "diastolic_bp": getattr(latest_vital, "diastolic_bp", None),
                "spo2_percent": getattr(latest_vital, "spo2_percent", None),
                "respiratory_rate": getattr(latest_vital, "respiratory_rate", None),
                "temperature_celsius": getattr(latest_vital, "temperature_celsius", None),
                "avpu_score": getattr(latest_vital, "avpu_score", "ALERT"),
                "supplemental_o2": getattr(latest_vital, "supplemental_o2", False),
            }
            recorded_at = getattr(latest_vital, "recorded_at", None)
            vital_id = getattr(latest_vital, "id", None)

    # 1. Freshness evaluation
    freshness_res = evaluate_vital_freshness(recorded_at, vital_dict, now=now)
    param_freshness = freshness_res["freshness_by_parameter"]
    age_min = freshness_res["age_minutes"]
    is_expired = (age_min is not None and age_min > 360.0)

    # 2. Shock Index calculation
    si_res = calculate_deterministic_shock_index(
        heart_rate=vital_dict.get("heart_rate"),
        systolic_bp=vital_dict.get("systolic_bp"),
        calculated_at=now,
    )

    # 3. NEWS2 calculation
    news2_res = calculate_deterministic_news2(
        respiratory_rate=vital_dict.get("respiratory_rate"),
        spo2_percent=vital_dict.get("spo2_percent"),
        supplemental_o2=vital_dict.get("supplemental_o2", False),
        systolic_bp=vital_dict.get("systolic_bp"),
        heart_rate=vital_dict.get("heart_rate"),
        avpu_score=vital_dict.get("avpu_score", "ALERT"),
        temperature_celsius=vital_dict.get("temperature_celsius"),
        is_expired=is_expired,
        calculated_at=now,
    )

    # 4. Red-flag evaluation
    red_flags = evaluate_deterministic_red_flags(
        vitals=vital_dict,
        shock_index=si_res.get("score"),
        presenting_complaint=presenting_complaint,
        extracted_symptoms=extracted_symptoms,
        evaluated_at=now,
    )
    has_critical_red_flags = any(rf["triggered"] and rf["severity"] == "CRITICAL" for rf in red_flags)

    # 5. Missing critical vitals & uncertainty
    required_vitals = ["heart_rate", "systolic_bp", "spo2_percent", "respiratory_rate", "temperature_celsius"]
    missing_critical = [p for p in required_vitals if param_freshness.get(p) in ["MISSING", "EXPIRED"]]

    standard_count = len(required_vitals)
    present_count = standard_count - len(missing_critical)
    completeness_ratio = round(present_count / max(1, standard_count), 2)

    # Calculate Uncertainty U_t explicitly separated from physiological risk
    # High uncertainty = high missingness, NOT high physiological acuity
    uncertainty_score = max(0.05, min(0.95, round(1.0 - (completeness_ratio * 0.80), 2)))
    if uncertainty_score >= 0.60:
        uncertainty_level = "HIGH"
    elif uncertainty_score >= 0.30:
        uncertainty_level = "MODERATE"
    else:
        uncertainty_level = "LOW"

    # 6. Priority tier calculation
    priority_res = evaluate_priority_tier(
        pathway=pathway,
        news2_result=news2_res,
        shock_index_result=si_res,
        red_flags=red_flags,
        vitals_freshness=param_freshness,
        evaluated_at=now,
    )

    raw_snapshot = {
        "case_id": case_id,
        "vital_id": vital_id,
        "pathway": pathway,
        "current_state": current_state,
        "vitals_summary": vital_dict,
        "vitals_freshness": param_freshness,
        "vitals_overall_status": freshness_res["overall_status"],
        "vital_age_minutes": age_min,
        "news2": news2_res,
        "shock_index": si_res,
        "red_flags": red_flags,
        "has_critical_red_flags": has_critical_red_flags,
        "uncertainty_score": uncertainty_score,
        "uncertainty_level": uncertainty_level,
        "missing_critical_vitals": missing_critical,
        "data_completeness_ratio": completeness_ratio,
        "priority_tier": priority_res["priority_tier"],
        "acuity_tier": priority_res["acuity_tier"],
        "risk_score": priority_res["risk_score"],
        "priority_reasons": priority_res["priority_reasons"],
        "ruleset_version": MASTER_RULESET_VERSION,
        "calculated_at": now,
    }

    return make_json_safe(raw_snapshot)
