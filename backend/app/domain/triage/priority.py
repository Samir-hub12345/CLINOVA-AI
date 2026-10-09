"""CLINOVA AI — Deterministic Triage Priority & Operational Queue Ordering.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.

Core Invariants:
1. Physical Physiological Risk is distinct from Evidence Uncertainty.
2. High uncertainty does NOT automatically force emergency escalation.
3. Starvation control prevents lower-priority patients from being starved indefinitely.
4. Dynamic waiting times are computed at query time (never generated DB column).
5. Queue ordering is 100% deterministic with strict tie-breaking.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

PRIORITY_RULES_VERSION = "PRIORITY-RULES-v1.0"
STARVATION_THRESHOLD_MINUTES = 120  # Operational wait time threshold for priority boost


def evaluate_priority_tier(
    pathway: str,
    news2_result: Dict[str, Any],
    shock_index_result: Dict[str, Any],
    red_flags: List[Dict[str, Any]],
    vitals_freshness: Dict[str, str],
    evaluated_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Evaluates deterministic priority tier and acuity tier.

    Priority Tiers:
    - P1_CRITICAL (Immediate): Life-threatening instability, active critical red flag,
      or emergency resuscitation pathway.
    - P2_URGENT (Very Urgent): Urgent red flag, NEWS2 >= 7 (without critical red flag),
      single vital score = 3, or Shock Index >= 0.9.
    - P3_MODERATE (Urgent): NEWS2 5-6, moderate physiological derangement.
    - P4_ROUTINE (Standard): NEWS2 0-4, stable physiology, no red flags.

    Critical Phase 7 Invariant:
    If NEWS2 is incomplete due to missing/stale vitals, missing data is NOT treated
    as an emergency. Priority reflects observed physiology, and missing data is surfaced
    as an operational data-collection prompt.
    """
    if evaluated_at is None:
        evaluated_at = datetime.now(timezone.utc)

    triggered_rf = [rf for rf in red_flags if rf.get("triggered", False)]
    critical_rf = [rf for rf in triggered_rf if rf.get("severity") == "CRITICAL"]
    urgent_rf = [rf for rf in triggered_rf if rf.get("severity") == "URGENT"]

    reasons: List[str] = []
    is_emergency_pathway = pathway.upper().startswith("EMERGENCY")

    # Check P1_CRITICAL conditions
    if critical_rf:
        for rf in critical_rf:
            reasons.append(f"Critical Red Flag: {rf.get('name')} ({rf.get('rule_id')})")
        tier = "P1_CRITICAL"
        acuity = "CRITICAL"
        risk_score = 0.95
    elif is_emergency_pathway:
        reasons.append(f"Direct Emergency Pathway: {pathway}")
        tier = "P1_CRITICAL"
        acuity = "CRITICAL"
        risk_score = 0.90
    elif shock_index_result.get("is_complete") and (shock_index_result.get("score") or 0) >= 1.0:
        reasons.append(f"Severe Shock Index: {shock_index_result.get('score')} >= 1.0")
        tier = "P1_CRITICAL"
        acuity = "CRITICAL"
        risk_score = 0.85
    # Check P2_URGENT conditions
    elif urgent_rf:
        for rf in urgent_rf:
            reasons.append(f"Urgent Red Flag: {rf.get('name')} ({rf.get('rule_id')})")
        tier = "P2_URGENT"
        acuity = "URGENT"
        risk_score = 0.65
    elif news2_result.get("is_complete") and (news2_result.get("score") or 0) >= 7:
        reasons.append(f"High Clinical Risk: Complete NEWS2 score {news2_result.get('score')} >= 7")
        tier = "P2_URGENT"
        acuity = "URGENT"
        risk_score = 0.70
    elif news2_result.get("is_complete") and news2_result.get("risk_level") == "LOW_MEDIUM":
        reasons.append("Extreme Single Parameter: NEWS2 parameter scored 3 points (Urgent Review)")
        tier = "P2_URGENT"
        acuity = "URGENT"
        risk_score = 0.55
    elif any(v == 3 for v in news2_result.get("component_scores", {}).values() if v is not None):
        reasons.append("Extreme Single Parameter: Observed vital parameter scored 3 points (Urgent Review)")
        tier = "P2_URGENT"
        acuity = "URGENT"
        risk_score = 0.55
    elif shock_index_result.get("is_complete") and (shock_index_result.get("score") or 0) >= 0.9:
        reasons.append(f"Elevated Shock Index: {shock_index_result.get('score')} (High Shock Risk)")
        tier = "P2_URGENT"
        acuity = "URGENT"
        risk_score = 0.50
    # Check P3_MODERATE conditions
    elif news2_result.get("is_complete") and 5 <= (news2_result.get("score") or 0) <= 6:
        reasons.append(f"Medium Clinical Risk: Complete NEWS2 score {news2_result.get('score')}")
        tier = "P3_MODERATE"
        acuity = "MODERATE"
        risk_score = 0.35
    # Standard P4_ROUTINE
    else:
        tier = "P4_ROUTINE"
        acuity = "ROUTINE"
        if news2_result.get("is_complete"):
            reasons.append(f"Stable Physiology: Complete NEWS2 score {news2_result.get('score')} (Low Risk)")
            risk_score = max(0.05, round((news2_result.get("score") or 0) / 20.0, 2))
        else:
            reasons.append("Stable or Partial Physiology: No critical physiological red flags triggered")
            risk_score = 0.15

    # Check for missing critical vitals and flag explicitly
    critical_params = ["heart_rate", "systolic_bp", "spo2_percent", "respiratory_rate", "temperature_celsius"]
    missing_vitals = [p for p in critical_params if vitals_freshness.get(p) in ["MISSING", "EXPIRED"]]
    stale_vitals = [p for p in critical_params if vitals_freshness.get(p) == "STALE"]

    if missing_vitals:
        reasons.append(f"Data Limitation: Missing critical vital(s) [{', '.join(missing_vitals)}]; bedside completion prioritized")
    if stale_vitals:
        reasons.append(f"Data Limitation: Stale vital(s) [{', '.join(stale_vitals)}]; repeat acquisition recommended")

    return {
        "priority_tier": tier,
        "acuity_tier": acuity,
        "risk_score": risk_score,
        "priority_reasons": reasons,
        "ruleset_version": PRIORITY_RULES_VERSION,
        "evaluated_at": evaluated_at,
    }


def sort_clinical_queue(
    queue_items: List[Dict[str, Any]],
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Sorts clinical queue deterministically.

    Deterministic Sort Key Hierarchy:
    1. Emergency Pathway Status (EMERGENCY_* before REGULAR_*)
    2. Active Critical Red Flags (presence of active critical red flags first)
    3. Operational Priority Rank (P1 > P2 > P3 > P4) with starvation mitigation
    4. Normalized Physiological Risk Score (descending)
    5. Case State (active intake/triage states before downstream states)
    6. Dynamic Waiting Time (longest waiting first within tier)
    7. Strict Tie-Breakers: created_at (ascending), then case_id (lexicographic)
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    def _sort_key(item: Dict[str, Any]) -> Tuple:
        pathway = str(item.get("pathway") or "").upper()
        is_emergency = 0 if pathway.startswith("EMERGENCY") else 1

        has_crit_rf = 0 if item.get("has_critical_red_flags", False) else 1

        tier = str(item.get("priority_tier") or item.get("acuity_tier") or "ROUTINE").upper()
        tier_ranks = {
            "P1_CRITICAL": 1,
            "CRITICAL": 1,
            "P2_URGENT": 2,
            "URGENT": 2,
            "P3_MODERATE": 3,
            "MODERATE": 3,
            "P4_ROUTINE": 4,
            "ROUTINE": 4,
        }
        raw_rank = tier_ranks.get(tier, 4)

        # Starvation mitigation:
        # Lower-priority patients waiting > 120 mins gain 1 operational queue position
        wait_min = item.get("waiting_minutes", 0)
        effective_rank = raw_rank
        if raw_rank >= 3 and wait_min >= STARVATION_THRESHOLD_MINUTES:
            effective_rank = raw_rank - 1

        risk_score = float(item.get("risk_score", 0.0))

        # Case state priority ranking:
        # Triage and intake active states have priority over downstream or pending states
        state = str(item.get("current_state") or "").upper()
        state_ranks = {
            "INTAKE_RECORDED": 1,
            "TRIAGE_PENDING": 1,
            "TRIAGE_IN_PROGRESS": 1,
            "PENDING_INFORMATION": 2,
            "CLINICIAN_REVIEW_REQUIRED": 3,
            "REVIEW_IN_PROGRESS": 3,
            "DISPOSITION_PENDING": 4,
            "CLOSED": 5,
        }
        state_rank = state_ranks.get(state, 2)

        # Tie breakers
        created_str = str(item.get("created_at") or "")
        case_id = str(item.get("case_id") or "")

        return (
            is_emergency,
            has_crit_rf,
            effective_rank,
            -round(risk_score, 3),
            state_rank,
            -wait_min,
            created_str,
            case_id,
        )

    return sorted(queue_items, key=_sort_key)
