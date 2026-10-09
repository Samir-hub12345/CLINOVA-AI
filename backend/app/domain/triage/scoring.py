"""CLINOVA AI — Deterministic Physiological Scoring.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.

Authoritative Standards:
- NEWS2: Royal College of Physicians (RCP), 2017. National Early Warning Score 2.
- Shock Index: Allgöwer & Burri (1967). Shock Index = Heart Rate / Systolic Blood Pressure.
- Freshness: DOC-08 Evidence Freshness & Decay Specification.

Zero LLM / AI dependencies. Sub-millisecond deterministic calculation.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

NEWS2_VERSION = "NEWS2-RCP-2017"
SHOCK_INDEX_VERSION = "SHOCK-INDEX-v1.0"

FRESH_THRESHOLD_MINUTES = 120.0   # <= 2 hours: FRESH / AVAILABLE
STALE_THRESHOLD_MINUTES = 360.0   # 2 - 6 hours: STALE; > 6 hours: EXPIRED

NEWS2_REQUIRED_PARAMETERS = [
    "respiratory_rate",
    "spo2_percent",
    "systolic_bp",
    "heart_rate",
    "temperature_celsius",
    "avpu_score",
]


def evaluate_vital_freshness(
    recorded_at: Optional[datetime],
    parameter_values: Dict[str, Any],
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Evaluates physiological observation freshness per parameter.
    Returns:
    - freshness_by_parameter: Dict[str, str] ('AVAILABLE', 'STALE', 'MISSING')
    - age_minutes: Optional[float]
    - overall_status: str ('AVAILABLE', 'STALE', 'MISSING')
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    if recorded_at is None:
        age_minutes = None
    else:
        rec = recorded_at
        if rec.tzinfo is None:
            rec = rec.replace(tzinfo=timezone.utc)
        age_minutes = max(0.0, (now - rec).total_seconds() / 60.0)

    freshness_by_param: Dict[str, str] = {}
    standard_params = [
        "heart_rate",
        "systolic_bp",
        "diastolic_bp",
        "spo2_percent",
        "respiratory_rate",
        "temperature_celsius",
        "avpu_score",
    ]

    for p in standard_params:
        val = parameter_values.get(p)
        if val is None or str(val).strip() == "":
            freshness_by_param[p] = "MISSING"
        elif age_minutes is None:
            freshness_by_param[p] = "AVAILABLE"
        elif age_minutes <= FRESH_THRESHOLD_MINUTES:
            freshness_by_param[p] = "AVAILABLE"
        elif age_minutes <= STALE_THRESHOLD_MINUTES:
            freshness_by_param[p] = "STALE"
        else:
            freshness_by_param[p] = "MISSING"  # Expired (> 6 hrs) is clinically missing for acute triage

    # Overall status
    available_count = sum(1 for status in freshness_by_param.values() if status == "AVAILABLE")
    stale_count = sum(1 for status in freshness_by_param.values() if status == "STALE")

    if available_count >= 4:
        overall_status = "AVAILABLE"
    elif stale_count > 0:
        overall_status = "STALE"
    else:
        overall_status = "MISSING"

    return {
        "freshness_by_parameter": freshness_by_param,
        "age_minutes": round(age_minutes, 1) if age_minutes is not None else None,
        "overall_status": overall_status,
    }


def score_respiratory_rate(rr: Optional[int]) -> Optional[int]:
    """NEWS2 Respiration Rate (breaths/min)."""
    if rr is None:
        return None
    if rr <= 8 or rr >= 25:
        return 3
    if 21 <= rr <= 24:
        return 2
    if 9 <= rr <= 11:
        return 1
    return 0  # 12-20


def score_spo2(spo2: Optional[int]) -> Optional[int]:
    """NEWS2 Oxygen Saturation (%) Scale 1."""
    if spo2 is None:
        return None
    if spo2 <= 91:
        return 3
    if 92 <= spo2 <= 93:
        return 2
    if 94 <= spo2 <= 95:
        return 1
    return 0  # >= 96


def score_supplemental_o2(supp_o2: bool) -> int:
    """NEWS2 Air or Oxygen (+2 points if supplemental oxygen prescribed/administered)."""
    return 2 if supp_o2 else 0


def score_systolic_bp(sbp: Optional[int]) -> Optional[int]:
    """NEWS2 Systolic Blood Pressure (mmHg)."""
    if sbp is None:
        return None
    if sbp <= 90 or sbp >= 220:
        return 3
    if 91 <= sbp <= 100:
        return 2
    if 101 <= sbp <= 110:
        return 1
    return 0  # 111-219


def score_heart_rate(hr: Optional[int]) -> Optional[int]:
    """NEWS2 Pulse / Heart Rate (bpm)."""
    if hr is None:
        return None
    if hr <= 40 or hr >= 131:
        return 3
    if 111 <= hr <= 130:
        return 2
    if (41 <= hr <= 50) or (91 <= hr <= 110):
        return 1
    return 0  # 51-90


def score_avpu(avpu: Optional[str]) -> Optional[int]:
    """NEWS2 Consciousness (AVPU / ACVPU)."""
    if avpu is None or not avpu.strip():
        return None
    norm = avpu.strip().upper()
    if norm == "ALERT":
        return 0
    # Any new confusion, voice, pain, unresponsive = 3
    return 3


def score_temperature(temp: Optional[float]) -> Optional[int]:
    """NEWS2 Core Temperature (°C)."""
    if temp is None:
        return None
    if temp <= 35.0:
        return 3
    if temp >= 39.1:
        return 2
    if (35.1 <= temp <= 36.0) or (38.1 <= temp <= 39.0):
        return 1
    return 0  # 36.1-38.0


def calculate_deterministic_news2(
    respiratory_rate: Optional[int] = None,
    spo2_percent: Optional[int] = None,
    supplemental_o2: bool = False,
    systolic_bp: Optional[int] = None,
    heart_rate: Optional[int] = None,
    avpu_score: Optional[str] = "ALERT",
    temperature_celsius: Optional[float] = None,
    is_expired: bool = False,
    calculated_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Calculates Royal College of Physicians NEWS2 composite score deterministically.

    Incomplete Data Policy:
    If any required physiological parameter is missing or marked expired:
    - is_complete = False
    - score = None (does NOT silently treat missing data as zero)
    - missing_components = list of missing parameter names
    - risk_level = None (limitation surfaced clearly)

    When all required inputs are present:
    - is_complete = True
    - score = integer sum in [0, 20]
    - risk_level in ["LOW", "LOW_MEDIUM", "MEDIUM", "HIGH"]
    """
    if calculated_at is None:
        calculated_at = datetime.now(timezone.utc)
    elif calculated_at.tzinfo is None:
        calculated_at = calculated_at.replace(tzinfo=timezone.utc)

    # If entire observation is expired (> 6 hours old), do not compute acute score
    if is_expired:
        return {
            "score": None,
            "is_complete": False,
            "risk_level": None,
            "component_scores": {
                "respiratory_rate": None,
                "spo2": None,
                "supplemental_o2": 0,
                "systolic_bp": None,
                "heart_rate": None,
                "avpu": None,
                "temperature": None,
            },
            "missing_components": list(NEWS2_REQUIRED_PARAMETERS),
            "version": NEWS2_VERSION,
            "calculated_at": calculated_at,
            "limitation": "Observation expired (> 6 hours). Fresh bedside vitals required.",
        }

    c_rr = score_respiratory_rate(respiratory_rate)
    c_spo2 = score_spo2(spo2_percent)
    c_o2 = score_supplemental_o2(supplemental_o2)
    c_sbp = score_systolic_bp(systolic_bp)
    c_hr = score_heart_rate(heart_rate)
    c_avpu = score_avpu(avpu_score)
    c_temp = score_temperature(temperature_celsius)

    component_scores = {
        "respiratory_rate": c_rr,
        "spo2": c_spo2,
        "supplemental_o2": c_o2,
        "systolic_bp": c_sbp,
        "heart_rate": c_hr,
        "avpu": c_avpu,
        "temperature": c_temp,
    }

    missing = []
    if c_rr is None:
        missing.append("respiratory_rate")
    if c_spo2 is None:
        missing.append("spo2_percent")
    if c_sbp is None:
        missing.append("systolic_bp")
    if c_hr is None:
        missing.append("heart_rate")
    if c_avpu is None:
        missing.append("avpu_score")
    if c_temp is None:
        missing.append("temperature_celsius")

    if missing:
        return {
            "score": None,
            "is_complete": False,
            "risk_level": None,
            "component_scores": component_scores,
            "missing_components": missing,
            "version": NEWS2_VERSION,
            "calculated_at": calculated_at,
            "limitation": f"Incomplete vital signs vector. Missing: {', '.join(missing)}.",
        }

    # All components present
    total_score = c_rr + c_spo2 + c_o2 + c_sbp + c_hr + c_avpu + c_temp

    # Clinical risk category per RCP NEWS2 guidelines
    has_extreme_single = any(s == 3 for s in [c_rr, c_spo2, c_sbp, c_hr, c_avpu, c_temp])

    if total_score >= 7:
        risk_level = "HIGH"
    elif 5 <= total_score <= 6:
        risk_level = "MEDIUM"
    elif has_extreme_single:
        risk_level = "LOW_MEDIUM"  # Single score 3 triggers urgent medical review despite total <= 4
    else:
        risk_level = "LOW"

    return {
        "score": total_score,
        "is_complete": True,
        "risk_level": risk_level,
        "component_scores": component_scores,
        "missing_components": [],
        "version": NEWS2_VERSION,
        "calculated_at": calculated_at,
        "limitation": None,
    }


def calculate_deterministic_shock_index(
    heart_rate: Optional[int] = None,
    systolic_bp: Optional[int] = None,
    calculated_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Calculates Allgöwer & Burri Shock Index (Heart Rate / Systolic Blood Pressure).

    Requirements:
    - Pure deterministic division
    - Safe zero/negative division rejection
    - Missing inputs detection
    - Threshold interpretation:
      < 0.7: NORMAL
      0.7 - < 0.9: MILD_ELEVATED
      0.9 - < 1.0: HIGH_SHOCK_RISK
      >= 1.0: CRITICAL_SHOCK_RISK
    """
    if calculated_at is None:
        calculated_at = datetime.now(timezone.utc)
    elif calculated_at.tzinfo is None:
        calculated_at = calculated_at.replace(tzinfo=timezone.utc)

    missing = []
    if heart_rate is None:
        missing.append("heart_rate")
    if systolic_bp is None:
        missing.append("systolic_bp")

    if missing:
        return {
            "score": None,
            "is_complete": False,
            "interpretation": "MISSING_INPUTS",
            "missing_components": missing,
            "version": SHOCK_INDEX_VERSION,
            "calculated_at": calculated_at,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }

    if systolic_bp <= 0:
        return {
            "score": None,
            "is_complete": False,
            "interpretation": "INVALID_INPUTS",
            "missing_components": [],
            "version": SHOCK_INDEX_VERSION,
            "calculated_at": calculated_at,
            "error": f"Invalid systolic blood pressure {systolic_bp} mmHg (must be > 0).",
        }

    si = round(heart_rate / systolic_bp, 2)

    if si >= 1.0:
        interpretation = "CRITICAL_SHOCK_RISK"
    elif si >= 0.9:
        interpretation = "HIGH_SHOCK_RISK"
    elif si >= 0.7:
        interpretation = "MILD_ELEVATED"
    else:
        interpretation = "NORMAL"

    return {
        "score": si,
        "is_complete": True,
        "interpretation": interpretation,
        "missing_components": [],
        "version": SHOCK_INDEX_VERSION,
        "calculated_at": calculated_at,
        "error": None,
    }
