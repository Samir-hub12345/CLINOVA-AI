"""CLINOVA AI — CAREGRAPH Engine.

Patient-Level Clinical Intelligence & Longitudinal Trajectory.
Computes dynamic patient state, NEWS2-grounded acuity (R_t), trajectory slope (Delta R),
evidence uncertainty (U_t), protocol completeness, missing data detection,
targeted follow-up questions, conflict detection, and graph topology.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class ProvenanceType(str, Enum):
    PATIENT_REPORTED = "PATIENT_REPORTED"
    VOICE_TRANSCRIBED = "VOICE_TRANSCRIBED"
    OCR_EXTRACTED = "OCR_EXTRACTED"
    CLINICIAN_VERIFIED = "CLINICIAN_VERIFIED"
    AI_INFERRED = "AI_INFERRED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    CONFIRMED = "CONFIRMED"
    MODIFIED = "MODIFIED"
    DISPUTED = "DISPUTED"


# Protocol definitions for protocol completeness (C_data)
SYNDROME_PROTOCOLS: Dict[str, List[str]] = {
    "CHEST_PAIN": ["onset_duration", "pain_radiation", "pain_character", "heart_rate", "systolic_bp", "spo2_percent", "ecg_troponin"],
    "ACUTE_RESPIRATORY": ["respiratory_rate", "spo2_percent", "temperature_celsius", "cough_duration", "work_of_breathing", "auscultation"],
    "FEVER_HEMORRHAGIC": ["temperature_celsius", "fever_duration", "platelet_count", "bleeding_manifestation", "systolic_bp", "pulse_rate"],
    "TRAUMA": ["mechanism_of_injury", "systolic_bp", "heart_rate", "gcs_avpu", "external_hemorrhage", "respiratory_rate"],
    "STROKE_ACUTE": ["face_droop", "arm_weakness", "speech_difficulty", "last_known_well_time", "blood_glucose", "systolic_bp"],
    "GENERAL_ROUTINE": ["symptom_duration", "heart_rate", "systolic_bp", "temperature_celsius"],
}


def calculate_news2_score(
    rr: Optional[int] = None,
    spo2: Optional[int] = None,
    systolic_bp: Optional[int] = None,
    hr: Optional[int] = None,
    avpu: Optional[str] = "ALERT",
    temp: Optional[float] = None,
    supplemental_o2: bool = False,
) -> int:
    """Calculates standard National Early Warning Score 2 (NEWS2)."""
    score = 0

    # Respiration Rate (breaths/min)
    if rr is not None:
        if rr <= 8 or rr >= 25:
            score += 3
        elif 21 <= rr <= 24:
            score += 2
        elif 9 <= rr <= 11:
            score += 1

    # Oxygen Saturation (%)
    if spo2 is not None:
        if spo2 <= 91:
            score += 3
        elif 92 <= spo2 <= 93:
            score += 2
        elif 94 <= spo2 <= 95:
            score += 1

    if supplemental_o2:
        score += 2

    # Systolic Blood Pressure (mmHg)
    if systolic_bp is not None:
        if systolic_bp <= 90 or systolic_bp >= 220:
            score += 3
        elif 91 <= systolic_bp <= 100:
            score += 2
        elif 101 <= systolic_bp <= 110:
            score += 1

    # Pulse / Heart Rate (bpm)
    if hr is not None:
        if hr <= 40 or hr >= 131:
            score += 3
        elif 111 <= hr <= 130:
            score += 2
        elif (41 <= hr <= 50) or (91 <= hr <= 110):
            score += 1

    # Consciousness (AVPU)
    if avpu and avpu.upper() != "ALERT":
        score += 3

    # Temperature (°C)
    if temp is not None:
        if temp <= 35.0:
            score += 3
        elif temp >= 39.1:
            score += 2
        elif (35.1 <= temp <= 36.0) or (38.1 <= temp <= 39.0):
            score += 1

    return score


def calculate_risk_score(
    vitals: Dict[str, Any],
    red_flags: Optional[List[str]] = None,
) -> Tuple[float, str]:
    """Calculates composite normalized risk score R_t in [0.0, 1.0] and acuity tier."""
    news2 = calculate_news2_score(
        rr=vitals.get("respiratory_rate"),
        spo2=vitals.get("spo2_percent"),
        systolic_bp=vitals.get("systolic_bp"),
        hr=vitals.get("heart_rate"),
        avpu=vitals.get("avpu_score", "ALERT"),
        temp=vitals.get("temperature_celsius"),
        supplemental_o2=vitals.get("supplemental_o2", False),
    )

    penalty = 0
    if red_flags:
        for rf in red_flags:
            if rf in ["STRIDOR", "UNRESPONSIVE", "HYPOTENSIVE_SHOCK", "MASSIVE_BLEEDING", "ACUTE_PULMONARY_EDEMA"]:
                penalty += 5
            else:
                penalty += 2

    raw_score = news2 + penalty
    # Scale: raw_score of 7 is high risk (NEWS2 threshold), 12+ is maximum critical
    normalized_rt = min(1.0, max(0.05, round(raw_score / 10.0, 2)))

    if normalized_rt >= 0.70 or raw_score >= 7:
        acuity_tier = "CRITICAL"
    elif normalized_rt >= 0.40 or raw_score >= 4:
        acuity_tier = "URGENT"
    elif normalized_rt >= 0.20 or raw_score >= 2:
        acuity_tier = "MODERATE"
    else:
        acuity_tier = "ROUTINE"

    return normalized_rt, acuity_tier


def calculate_trajectory_slope(
    vitals_history: List[Dict[str, Any]],
) -> Tuple[float, str]:
    """
    Computes dynamic trajectory slope Delta R = (R(t2) - R(t1)) / Delta t (in points/hr).
    Returns (slope, trajectory_label).
    """
    if len(vitals_history) < 2:
        return 0.0, "STABLE"

    v1 = vitals_history[-2]
    v2 = vitals_history[-1]

    r1, _ = calculate_risk_score(v1)
    r2, _ = calculate_risk_score(v2)

    t1 = v1.get("recorded_at")
    t2 = v2.get("recorded_at")

    hours_diff = 0.5  # default 30 min window if timestamps not provided
    if t1 and t2:
        try:
            if isinstance(t1, str):
                t1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))
            if isinstance(t2, str):
                t2 = datetime.fromisoformat(t2.replace("Z", "+00:00"))
            if t1.tzinfo is not None and t2.tzinfo is None:
                t2 = t2.replace(tzinfo=t1.tzinfo)
            elif t1.tzinfo is None and t2.tzinfo is not None:
                t1 = t1.replace(tzinfo=t2.tzinfo)
            diff_secs = abs((t2 - t1).total_seconds())
            if diff_secs > 60:
                hours_diff = diff_secs / 3600.0
        except Exception:
            hours_diff = 0.5

    # Slope in normalized points per hour
    slope = round((r2 - r1) / max(0.1, hours_diff), 2)

    if slope >= 1.5:
        trend = "RAPID_DETERIORATION"
    elif slope >= 0.5:
        trend = "GRADUAL_DETERIORATION"
    elif slope <= -0.5:
        trend = "IMPROVING"
    else:
        trend = "STABLE"

    return slope, trend


def evaluate_uncertainty_and_gaps(
    syndrome: str,
    captured_data: Dict[str, Any],
    evidence_records: List[Dict[str, Any]],
    narrative_text: str = "",
) -> Dict[str, Any]:
    """
    Computes protocol completeness C_data, mean evidence quality Q_evidence,
    clinician verification ratio V_clinician, and overall uncertainty U_t:
    U_t = 1.0 - (0.40 * C_data + 0.35 * Q_evidence + 0.25 * V_clinician)
    """
    protocol_params = SYNDROME_PROTOCOLS.get(syndrome, SYNDROME_PROTOCOLS["GENERAL_ROUTINE"])
    present_params = []
    missing_params = []

    for param in protocol_params:
        val = captured_data.get(param)
        if val is not None and str(val).strip() != "":
            present_params.append(param)
        else:
            missing_params.append(param)

    c_data = len(present_params) / max(1, len(protocol_params))

    # Evidence Quality Mean
    if evidence_records:
        confidences = [e.get("confidence_score", 1.0) for e in evidence_records]
        q_evidence = sum(confidences) / len(confidences)
        verified_count = sum(1 for e in evidence_records if e.get("verification_status") == "CONFIRMED")
        v_clinician = verified_count / len(evidence_records)
    else:
        q_evidence = 0.8
        v_clinician = 0.0

    # Composite Uncertainty
    u_t = max(0.05, min(0.95, round(1.0 - (0.40 * c_data + 0.35 * q_evidence + 0.25 * v_clinician), 2)))

    # Missing Information Chips & Follow-Up Questions
    questions: List[Dict[str, str]] = []
    for missing in missing_params:
        if "duration" in missing:
            questions.append({"parameter": missing, "question": f"When exactly did the symptoms start and how long have they persisted?"})
        elif "radiation" in missing:
            questions.append({"parameter": missing, "question": "Does the discomfort radiate to the jaw, neck, left arm, or back?"})
        elif "character" in missing:
            questions.append({"parameter": missing, "question": "Is the pain crushing, burning, sharp, or dull pressure?"})
        elif "bleeding" in missing:
            questions.append({"parameter": missing, "question": "Are there any signs of spontaneous bleeding, gum bleeding, or petechial rash?"})
        elif "ecg" in missing or "troponin" in missing:
            questions.append({"parameter": missing, "question": "Has a 12-lead ECG or point-of-care cardiac troponin test been performed?"})
        elif "last_known_well" in missing:
            questions.append({"parameter": missing, "question": "What was the exact time the patient was last known to be symptom-free?"})
        else:
            questions.append({"parameter": missing, "question": f"Please verify clinical parameter: {missing.replace('_', ' ')}."})

    # Contradiction Detection
    conflicts: List[Dict[str, str]] = []
    # E.g. verbal claim "no fever" vs temp >= 38.5
    temp = captured_data.get("temperature_celsius")
    if temp and temp >= 38.5:
        if "no fever" in narrative_text.lower() or "afebrile" in narrative_text.lower():
            conflicts.append({
                "type": "FEVER_CONTRADICTION",
                "message": f"Narrative reports no fever, but recorded thermometer reading is {temp}°C (Hyperpyrexia)."
            })

    # E.g. verbal claim "asymptomatic/fine" vs SpO2 < 90
    spo2 = captured_data.get("spo2_percent")
    if spo2 and spo2 <= 90:
        if "asymptomatic" in narrative_text.lower() or "fine" in narrative_text.lower() or "normal" in narrative_text.lower():
            conflicts.append({
                "type": "SILENT_HYPOXIA_CONTRADICTION",
                "message": f"Patient reported feeling normal/asymptomatic, but SpO2 is dangerously low ({spo2}%)."
            })

    return {
        "uncertainty_score": u_t,
        "protocol_completeness": round(c_data, 2),
        "evidence_quality": round(q_evidence, 2),
        "clinician_verification_ratio": round(v_clinician, 2),
        "missing_parameters": missing_params,
        "follow_up_questions": questions,
        "conflicts": conflicts,
    }


def build_caregraph_view(
    case_data: Dict[str, Any],
    vitals_history: List[Dict[str, Any]],
    evidence_records: List[Dict[str, Any]],
    decisions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Assembles the full serialized CareGraph topology with nodes, edges, trajectory, and uncertainty."""
    nodes = []
    edges = []

    # 1. Patient Profile Node
    patient_node_id = f"node-pt-{case_data.get('patient_synthetic_id', 'unknown')}"
    nodes.append({
        "id": patient_node_id,
        "type": "PATIENT_PROFILE",
        "label": f"Patient ({case_data.get('patient_synthetic_id', 'SYN-PT')})",
        "data": {
            "synthetic_id": case_data.get("patient_synthetic_id"),
            "age_bracket": case_data.get("age_bracket", "40-49"),
            "biological_sex": case_data.get("biological_sex", "MALE"),
        },
        "provenance": ProvenanceType.SYSTEM_DERIVED,
        "status": VerificationStatus.CONFIRMED,
    })

    # 2. Encounter Node
    encounter_node_id = f"node-case-{case_data.get('id', 'new')}"
    nodes.append({
        "id": encounter_node_id,
        "type": "ENCOUNTER",
        "label": f"Case {case_data.get('case_number', 'PENDING')}",
        "data": {
            "status": case_data.get("status"),
            "acuity_tier": case_data.get("acuity_tier"),
            "risk_score": case_data.get("risk_score"),
            "uncertainty_score": case_data.get("uncertainty_score"),
            "trajectory_slope": case_data.get("trajectory_slope"),
        },
        "provenance": ProvenanceType.SYSTEM_DERIVED,
        "status": VerificationStatus.CONFIRMED,
    })
    edges.append({"source": patient_node_id, "target": encounter_node_id, "relation": "HAS_EPISODE"})

    # 3. Presenting Symptom Node
    complaint = case_data.get("presenting_complaint", "")
    if complaint:
        symptom_node_id = f"node-symp-{encounter_node_id}"
        nodes.append({
            "id": symptom_node_id,
            "type": "SYMPTOM",
            "label": "Presenting Complaint",
            "data": {"narrative": complaint, "syndrome": case_data.get("primary_syndrome")},
            "provenance": ProvenanceType.PATIENT_REPORTED,
            "status": VerificationStatus.UNVERIFIED,
        })
        edges.append({"source": encounter_node_id, "target": symptom_node_id, "relation": "REPORTS"})

    # 4. Vital Sign Nodes
    for idx, v in enumerate(vitals_history):
        vital_node_id = f"node-vital-{idx+1}"
        nodes.append({
            "id": vital_node_id,
            "type": "VITAL_SIGN",
            "label": f"Vitals T+{idx*15}m",
            "data": {
                "heart_rate": v.get("heart_rate"),
                "systolic_bp": v.get("systolic_bp"),
                "diastolic_bp": v.get("diastolic_bp"),
                "spo2_percent": v.get("spo2_percent"),
                "respiratory_rate": v.get("respiratory_rate"),
                "temperature_celsius": v.get("temperature_celsius"),
                "recorded_at": str(v.get("recorded_at")),
            },
            "provenance": ProvenanceType.SYSTEM_DERIVED,
            "status": VerificationStatus.CONFIRMED,
        })
        edges.append({"source": encounter_node_id, "target": vital_node_id, "relation": "EXHIBITS"})

    # 5. Evidence Nodes
    for idx, e in enumerate(evidence_records):
        ev_node_id = f"node-ev-{e.get('id', idx)}"
        nodes.append({
            "id": ev_node_id,
            "type": "EVIDENCE",
            "label": f"Evidence ({e.get('provenance_type')})",
            "data": {
                "source": e.get("source_filename"),
                "confidence": e.get("confidence_score"),
                "payload": e.get("extracted_payload"),
            },
            "provenance": e.get("provenance_type"),
            "status": e.get("verification_status", VerificationStatus.UNVERIFIED),
        })
        edges.append({"source": encounter_node_id, "target": ev_node_id, "relation": "DERIVED_FROM"})

    # 6. Clinician Decision Nodes
    for idx, d in enumerate(decisions):
        dec_node_id = f"node-dec-{idx+1}"
        nodes.append({
            "id": dec_node_id,
            "type": "CLINICAL_DECISION",
            "label": f"Action: {d.get('action_type')}",
            "data": {
                "decision_type": d.get("decision_type"),
                "override_reason": d.get("override_reason"),
                "notes": d.get("notes"),
                "timestamp": str(d.get("timestamp")),
            },
            "provenance": ProvenanceType.CLINICIAN_VERIFIED,
            "status": VerificationStatus.CONFIRMED,
        })
        edges.append({"source": encounter_node_id, "target": dec_node_id, "relation": "AUTHORIZES"})

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }
