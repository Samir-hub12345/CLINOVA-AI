"""CLINOVA AI — Deterministic Clinical Red-Flag Evaluator.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.

Core Principles:
- Rule-based, decoupled from LLM.
- Auditable: exposes rule_id, rule_version, severity, explanation, observed inputs.
- Never infers or diagnoses diseases.
- Surfaces life-threatening physiological and safety hazards immediately.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

RED_FLAGS_VERSION = "REDFLAGS-CLINOVA-v1.0"


def evaluate_deterministic_red_flags(
    vitals: Dict[str, Any],
    shock_index: Optional[float] = None,
    presenting_complaint: str = "",
    extracted_symptoms: Optional[List[str]] = None,
    evaluated_at: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Evaluates configured deterministic clinical red-flag rules against observed vitals and symptoms.

    Returns list of evaluated rule results. Only triggered rules or full rule results.
    Each result contains:
    - rule_id: str
    - rule_version: str
    - name: str
    - severity: 'CRITICAL' | 'URGENT' | 'WARNING'
    - triggered: bool
    - explanation: str
    - observed_inputs: Dict[str, Any]
    - vital_references: List[str]
    - timestamp: datetime
    """
    if evaluated_at is None:
        evaluated_at = datetime.now(timezone.utc)
    elif evaluated_at.tzinfo is None:
        evaluated_at = evaluated_at.replace(tzinfo=timezone.utc)

    extracted_symptoms = extracted_symptoms or []
    narrative_lower = (presenting_complaint or "").lower()
    symptoms_lower = [s.lower() for s in extracted_symptoms]
    all_text = narrative_lower + " " + " ".join(symptoms_lower)

    hr = vitals.get("heart_rate")
    sbp = vitals.get("systolic_bp")
    dbp = vitals.get("diastolic_bp")
    spo2 = vitals.get("spo2_percent")
    rr = vitals.get("respiratory_rate")
    temp = vitals.get("temperature_celsius")
    avpu = str(vitals.get("avpu_score") or "ALERT").strip().upper()

    results: List[Dict[str, Any]] = []

    # 1. RF-PHYSIO-HYPOXIA (Critical)
    rf_hypoxia_triggered = (spo2 is not None and spo2 <= 88)
    results.append({
        "rule_id": "RF-PHYSIO-HYPOXIA",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Severe Hypoxemic Respiratory Failure",
        "severity": "CRITICAL",
        "triggered": rf_hypoxia_triggered,
        "explanation": f"Observed SpO2 {spo2}% <= 88% represents critical arterial hypoxemia." if rf_hypoxia_triggered else "SpO2 within acceptable non-critical threshold or not recorded.",
        "observed_inputs": {"spo2_percent": spo2},
        "vital_references": ["spo2_percent"],
        "timestamp": evaluated_at,
    })

    # 2. RF-PHYSIO-SHOCK (Critical)
    rf_shock_triggered = False
    shock_reason = ""
    if sbp is not None and sbp <= 80:
        rf_shock_triggered = True
        shock_reason = f"Systolic BP {sbp} mmHg <= 80 mmHg indicates severe circulatory shock."
    elif shock_index is not None and shock_index >= 1.0:
        rf_shock_triggered = True
        shock_reason = f"Shock Index {shock_index} >= 1.0 indicates critical occult or decompensated hypoperfusion."
    results.append({
        "rule_id": "RF-PHYSIO-SHOCK",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Decompensated Circulatory Shock / Severe Hypotension",
        "severity": "CRITICAL",
        "triggered": rf_shock_triggered,
        "explanation": shock_reason if rf_shock_triggered else "Blood pressure and Shock Index within non-critical range.",
        "observed_inputs": {"systolic_bp": sbp, "shock_index": shock_index},
        "vital_references": ["systolic_bp", "heart_rate"],
        "timestamp": evaluated_at,
    })

    # 3. RF-PHYSIO-UNRESPONSIVE (Critical)
    rf_avpu_triggered = avpu in ["UNRESPONSIVE", "PAIN"]
    results.append({
        "rule_id": "RF-PHYSIO-UNRESPONSIVE",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Severe Depression of Consciousness / Coma",
        "severity": "CRITICAL",
        "triggered": rf_avpu_triggered,
        "explanation": f"Consciousness score {avpu} indicates inability to maintain airway or profound encephalopathy." if rf_avpu_triggered else f"Consciousness score {avpu} is alert or voice-responsive.",
        "observed_inputs": {"avpu_score": avpu},
        "vital_references": ["avpu_score"],
        "timestamp": evaluated_at,
    })

    # 4. RF-PHYSIO-EXTREME-RR (Critical)
    rf_rr_triggered = (rr is not None and (rr <= 8 or rr >= 35))
    results.append({
        "rule_id": "RF-PHYSIO-EXTREME-RR",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Impending Respiratory Arrest / Extreme Tachypnea",
        "severity": "CRITICAL",
        "triggered": rf_rr_triggered,
        "explanation": f"Observed respiratory rate {rr} breaths/min is outside critical limits (<= 8 or >= 35)." if rf_rr_triggered else "Respiratory rate within non-critical boundaries or not recorded.",
        "observed_inputs": {"respiratory_rate": rr},
        "vital_references": ["respiratory_rate"],
        "timestamp": evaluated_at,
    })

    # 5. RF-PHYSIO-EXTREME-HR (Critical)
    rf_hr_triggered = (hr is not None and (hr <= 35 or hr >= 150))
    results.append({
        "rule_id": "RF-PHYSIO-EXTREME-HR",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Extreme Bradycardia / Malignant Tachyarrhythmia",
        "severity": "CRITICAL",
        "triggered": rf_hr_triggered,
        "explanation": f"Heart rate {hr} bpm is outside critical survival limits (<= 35 or >= 150)." if rf_hr_triggered else "Heart rate within non-critical limits.",
        "observed_inputs": {"heart_rate": hr},
        "vital_references": ["heart_rate"],
        "timestamp": evaluated_at,
    })

    # 6. RF-PHYSIO-HYPERPYREXIA (Critical)
    rf_temp_triggered = (temp is not None and (temp >= 40.5 or temp <= 34.0))
    results.append({
        "rule_id": "RF-PHYSIO-HYPERPYREXIA",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Malignant Hyperpyrexia / Severe Hypothermia",
        "severity": "CRITICAL",
        "triggered": rf_temp_triggered,
        "explanation": f"Core body temperature {temp}°C is critically dangerous (>= 40.5°C or <= 34.0°C)." if rf_temp_triggered else "Body temperature within survivable range.",
        "observed_inputs": {"temperature_celsius": temp},
        "vital_references": ["temperature_celsius"],
        "timestamp": evaluated_at,
    })

    # 7. RF-CLINICAL-AIRWAY (Critical)
    rf_airway_triggered = any(k in all_text for k in ["stridor", "airway compromise", "choking", "laryngeal edema", "foreign body aspiration"])
    results.append({
        "rule_id": "RF-CLINICAL-AIRWAY",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Upper Airway Compromise / Stridor",
        "severity": "CRITICAL",
        "triggered": rf_airway_triggered,
        "explanation": "Presentation indicates immediate airway compromise requiring resuscitation." if rf_airway_triggered else "No upper airway obstruction keywords identified in clinical presentation.",
        "observed_inputs": {"narrative": presenting_complaint, "symptoms": extracted_symptoms},
        "vital_references": [],
        "timestamp": evaluated_at,
    })

    # 8. RF-CLINICAL-MASSIVE-BLEEDING (Critical)
    rf_bleeding_triggered = any(k in all_text for k in ["massive bleeding", "postpartum hemorrhage", "arterial bleeding", "exsanguinating", "severe bleeding", "active hemorrhage"])
    results.append({
        "rule_id": "RF-CLINICAL-MASSIVE-BLEEDING",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Active Massive Hemorrhage",
        "severity": "CRITICAL",
        "triggered": rf_bleeding_triggered,
        "explanation": "Active severe or postpartum hemorrhage identified requiring emergency hemostasis." if rf_bleeding_triggered else "No massive hemorrhage documented.",
        "observed_inputs": {"narrative": presenting_complaint, "symptoms": extracted_symptoms},
        "vital_references": [],
        "timestamp": evaluated_at,
    })

    # 9. RF-PHYSIO-HYPERTENSIVE-CRISIS (Urgent)
    rf_bp_crisis_triggered = (sbp is not None and sbp >= 220)
    results.append({
        "rule_id": "RF-PHYSIO-HYPERTENSIVE-CRISIS",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Severe Hypertensive Urgency / Crisis",
        "severity": "URGENT",
        "triggered": rf_bp_crisis_triggered,
        "explanation": f"Systolic BP {sbp} mmHg >= 220 mmHg represents acute hypertensive crisis." if rf_bp_crisis_triggered else "Systolic blood pressure below hypertensive crisis threshold.",
        "observed_inputs": {"systolic_bp": sbp},
        "vital_references": ["systolic_bp"],
        "timestamp": evaluated_at,
    })

    # 10. RF-PHYSIO-SEVERE-TACHYCARDIA (Urgent)
    rf_tachy_triggered = (hr is not None and 130 <= hr < 150)
    results.append({
        "rule_id": "RF-PHYSIO-SEVERE-TACHYCARDIA",
        "rule_version": RED_FLAGS_VERSION,
        "name": "Severe Resting Tachycardia",
        "severity": "URGENT",
        "triggered": rf_tachy_triggered,
        "explanation": f"Heart rate {hr} bpm is severely elevated (130-149 bpm)." if rf_tachy_triggered else "Heart rate within standard operational bounds.",
        "observed_inputs": {"heart_rate": hr},
        "vital_references": ["heart_rate"],
        "timestamp": evaluated_at,
    })

    return results
