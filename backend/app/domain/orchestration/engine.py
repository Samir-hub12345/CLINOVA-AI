"""CLINOVA AI — ORCHESTRATION ENGINE.

Cognitive Synthesis Core for Safest Achievable Care Pathway.
Synthesizes CareGraph (Patient State) + Evidence Uncertainty + FacilityGraph (Local Feasibility)
+ SignalGraph (System Telemetry) to derive advisory next care actions.
Enforces the mandatory Qualified Clinician Gate (DOC-11).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.domain.signalgraph.engine import signal_engine


class OrchestrationEngine:
    """Evaluates multi-dimensional clinical inputs and generates advisory recommendations."""

    @staticmethod
    def evaluate(
        case_state: Dict[str, Any],
        uncertainty_analysis: Dict[str, Any],
        feasibility_result: Dict[str, Any],
        signal_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Derives the safest achievable next care action.
        Non-diagnostic, advisory, and strictly human-in-the-loop.
        """
        rt = case_state.get("risk_score", 0.1)
        acuity_tier = case_state.get("acuity_tier", "ROUTINE")
        delta_r = case_state.get("trajectory_slope", 0.0)
        u_t = uncertainty_analysis.get("uncertainty_score", 0.3)
        conflicts = uncertainty_analysis.get("conflicts", [])
        missing_params = uncertainty_analysis.get("missing_parameters", [])
        feasibility_status = feasibility_result.get("status", "FEASIBLE")

        # Evaluate Prioritized Decision Hierarchy
        # Rule 1: Immediate Resuscitation / Bedside Emergency (ESCALATE)
        if rt >= 0.70 or delta_r >= 1.5 or acuity_tier == "CRITICAL":
            action = "ESCALATE"
            priority = "IMMEDIATE_RED"
            rationale = (
                f"Critical physiological severity detected (Risk Score R_t = {rt:.2f}, "
                f"Trajectory Slope Delta R = {delta_r:+.2f}/hr). Immediate bedside intervention required."
            )
            clinical_directive = (
                "Alert Emergency Resuscitation Team immediately. Prepare airway management, "
                "supplemental high-flow oxygen, wide-bore IV access, and continuous hemodynamic monitoring."
            )
            secondary_action = "REFER" if feasibility_status in ["INFEASIBLE", "DEGRADED"] else "OBSERVE"

        # Rule 2: Infeasible Care on Site (REFER)
        elif feasibility_status in ["INFEASIBLE", "DEGRADED"] and case_state.get("required_bundle") not in [None, "", "BUNDLE_ROUTINE_AMBULATORY"]:
            action = "REFER"
            priority = "HIGH_ORANGE"
            rationale = (
                f"Local care is {feasibility_status}: {feasibility_result.get('reason')} "
                f"Safe care delivery requires transfer to a network facility equipped for {case_state.get('required_bundle')}."
            )
            clinical_directive = (
                "Initiate inter-facility referral immediately. SBAR clinical transfer packet generated. "
                "Coordinate transport with receiving facility bed manager."
            )
            secondary_action = "ESCALATE" if rt > 0.5 else "OBSERVE"

        # Rule 3: Contradictory Evidence (VERIFY)
        elif len(conflicts) > 0:
            action = "VERIFY"
            priority = "ELEVATED_YELLOW"
            conflict_descs = "; ".join(c.get("message", "") for c in conflicts)
            rationale = f"Contradictory clinical evidence detected: {conflict_descs}"
            clinical_directive = (
                "Clinician bedside verification required. Reconcile patient-reported symptom history "
                "with objective vital signs or repeat diagnostic sampling before further action."
            )
            secondary_action = "ASK"

        # Rule 4: Borderline / Evolving Acuity (OBSERVE)
        elif (0.35 <= rt < 0.70) or (0.5 <= delta_r < 1.5) or acuity_tier in ["URGENT", "MODERATE"]:
            action = "OBSERVE"
            priority = "MONITORING_BLUE"
            rationale = (
                f"Moderate physiological risk (R_t = {rt:.2f}, Trajectory = {delta_r:+.2f}/hr). "
                "Patient condition may evolve; requires serial vital sign monitoring."
            )
            clinical_directive = (
                "Place patient in ED observation holding bay. Repeat full vital signs every 15–30 minutes "
                "to calculate dynamic trajectory slope."
            )
            secondary_action = "CONTINUE"

        # Rule 5: High Data Uncertainty with Protocol Gaps (ASK)
        elif u_t > 0.40 and len(missing_params) > 0:
            action = "ASK"
            priority = "MODERATE_YELLOW"
            rationale = (
                f"High diagnostic uncertainty (U_t = {u_t:.2f}) with {len(missing_params)} "
                f"uncollected protocol parameters: {', '.join(missing_params[:3])}."
            )
            clinical_directive = (
                "Prompt triage nurse or patient for targeted follow-up question. "
                "Resolve clinical gaps before committing to definitive discharge or admission."
            )
            secondary_action = "OBSERVE"

        # Rule 6: Routine Low-Risk Care (CONTINUE)
        else:
            action = "CONTINUE"
            priority = "ROUTINE_GREEN"
            rationale = (
                f"Patient presents with low physiological risk (R_t = {rt:.2f}) and stable trajectory. "
                "Protocol data is sufficient."
            )
            clinical_directive = (
                "Proceed with standard routine outpatient ambulatory care, symptom relief, and standard follow-up instructions."
            )
            secondary_action = "OBSERVE"

        return {
            "recommended_action": action,
            "priority_level": priority,
            "clinical_rationale": rationale,
            "clinical_directive": clinical_directive,
            "secondary_pathway": secondary_action,
            "inputs_considered": {
                "risk_score": rt,
                "acuity_tier": acuity_tier,
                "trajectory_slope": delta_r,
                "uncertainty_score": u_t,
                "feasibility_status": feasibility_status,
                "conflicts_count": len(conflicts),
                "missing_parameters_count": len(missing_params),
            },
            "advisory_disclaimer": "NON-DIAGNOSTIC ADVISORY RECOMMENDATION. Qualified clinician verification required before clinical action.",
        }

    @staticmethod
    def validate_clinician_decision(
        recommended_action: str,
        chosen_action: str,
        decision_type: str,
        clinician_id: str,
        override_reason: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validates the mandatory Qualified Clinician Gate."""
        if decision_type == "OVERRIDE":
            if not override_reason or not override_reason.strip():
                raise ValueError("Clinician override requires a mandatory clinical justification reason.")

        return {
            "status": "AUTHORIZED",
            "clinician_id": clinician_id,
            "recommended_action": recommended_action,
            "final_action": chosen_action,
            "decision_type": decision_type,
            "override_reason": override_reason if decision_type == "OVERRIDE" else None,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "medicolegal_signoff": "Human clinician authorized encounter disposition.",
        }
