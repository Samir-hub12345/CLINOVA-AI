"""CLINOVA AI — ORCHESTRATION ENGINE Router.

Connects CareGraph + Uncertainty + FacilityGraph + SignalGraph
to recommend the safest achievable care action.
Enforces the mandatory Qualified Clinician Review Gate (DOC-11).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import Case, Facility, ClinicianDecision, AuditLog, VitalReading, EvidenceRecord
from app.domain.caregraph.engine import evaluate_uncertainty_and_gaps, calculate_trajectory_slope
from app.domain.facilitygraph.engine import evaluate_feasibility
from app.domain.orchestration.engine import OrchestrationEngine

router = APIRouter()


class EvaluateOrchestrationRequest(BaseModel):
    case_id: str
    facility_id: Optional[str] = None


class ClinicianDecisionRequest(BaseModel):
    case_id: str
    action: str  # ASK, VERIFY, CONTINUE, OBSERVE, ESCALATE, REFER
    decision_type: str = "ACCEPT"  # ACCEPT, OVERRIDE
    clinician_id: str = "usr-doc-01"
    override_reason: Optional[str] = None
    notes: Optional[str] = None


@router.post("/evaluate", tags=["Orchestration Engine"])
async def evaluate_safest_action(req: EvaluateOrchestrationRequest, db: AsyncSession = Depends(get_db)):
    """
    Evaluates multi-dimensional inputs to derive the safest achievable advisory care action.
    Advisory and non-diagnostic; requires clinician sign-off.
    """
    case = await db.get(Case, req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    fac_id = req.facility_id or case.facility_id
    stmt = select(Facility).where(Facility.id == fac_id).options(selectinload(Facility.capabilities))
    fac = (await db.execute(stmt)).scalars().first()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found.")

    # 1. Fetch vitals and compute trajectory
    vitals_q = await db.execute(
        select(VitalReading).where(VitalReading.case_id == case.id).order_by(VitalReading.recorded_at)
    )
    all_vitals = vitals_q.scalars().all()
    v_history = [
        {
            "heart_rate": v.heart_rate,
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "spo2_percent": v.spo2_percent,
            "respiratory_rate": v.respiratory_rate,
            "temperature_celsius": v.temperature_celsius,
            "recorded_at": v.recorded_at,
        }
        for v in all_vitals
    ]
    latest_vital = v_history[-1] if v_history else {}
    slope, trend = calculate_trajectory_slope(v_history)

    # 2. Fetch Evidence & Uncertainty
    ev_q = await db.execute(select(EvidenceRecord).where(EvidenceRecord.case_id == case.id))
    all_ev = [
        {"confidence_score": e.confidence_score, "verification_status": e.verification_status}
        for e in ev_q.scalars().all()
    ]
    u_eval = evaluate_uncertainty_and_gaps(
        case.primary_syndrome or "GENERAL_ROUTINE",
        latest_vital,
        all_ev,
        narrative_text=case.presenting_complaint or "",
    )

    # 3. Facility Feasibility Predicate Phi
    fac_dict = {
        "id": fac.id,
        "name": fac.name,
        "tier": fac.tier,
        "icu_beds_available": fac.icu_beds_available,
        "general_beds_available": fac.general_beds_available,
        "capabilities": [(c.capability_code, c.is_operational) for c in fac.capabilities],
    }
    feasibility = evaluate_feasibility(fac_dict, case.required_bundle or "BUNDLE_ROUTINE_AMBULATORY")

    # 4. Orchestration Cognitive Synthesis
    case_state = {
        "risk_score": case.risk_score,
        "acuity_tier": case.acuity_tier,
        "trajectory_slope": slope,
        "required_bundle": case.required_bundle,
    }

    orchestration_result = OrchestrationEngine.evaluate(
        case_state=case_state,
        uncertainty_analysis=u_eval,
        feasibility_result=feasibility,
    )

    orchestration_result["case_id"] = case.id
    orchestration_result["facility_id"] = fac.id
    orchestration_result["facility_name"] = fac.name
    return orchestration_result


@router.post("/decision", tags=["Orchestration Engine"])
async def authorize_clinician_decision(req: ClinicianDecisionRequest, db: AsyncSession = Depends(get_db)):
    """
    Submits qualified clinician authorization or structured override.
    Drives the encounter finite state machine (DOC-07).
    """
    case = await db.get(Case, req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    # Validate override justification if overridden
    if req.decision_type == "OVERRIDE" and (not req.override_reason or not req.override_reason.strip()):
        raise HTTPException(
            status_code=422,
            detail="Mandatory clinician override justification is required when departing from advisory guidance.",
        )

    # Record Decision
    decision = ClinicianDecision(
        case_id=case.id,
        clinician_id=req.clinician_id,
        action_type=req.action.upper(),
        decision_type=req.decision_type.upper(),
        override_reason=req.override_reason,
        notes=req.notes,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(decision)

    # Transition Case State
    action_map = {
        "ESCALATE": "ESCALATE",
        "REFER": "REFER",
        "OBSERVE": "OBSERVE",
        "CONTINUE": "CONTINUE",
        "ASK": "INSUFFICIENT_DATA",
        "VERIFY": "CONFLICTING_DATA",
    }
    case.status = action_map.get(req.action.upper(), "CLINICIAN_REVIEW")
    case.updated_at = datetime.now(timezone.utc)

    # Audit Trail
    audit = AuditLog(
        actor_id=req.clinician_id,
        action="CLINICIAN_DECISION_RECORDED",
        entity_type="CASE",
        entity_id=case.id,
        details={
            "action": req.action,
            "decision_type": req.decision_type,
            "override_reason": req.override_reason,
            "new_case_status": case.status,
        },
    )
    db.add(audit)
    await db.commit()

    return {
        "decision_id": decision.id,
        "case_id": case.id,
        "case_status": case.status,
        "action_authorized": req.action,
        "decision_type": req.decision_type,
        "override_reason": req.override_reason,
        "status": "AUTHORIZED",
        "message": "Clinical action authorized by qualified clinician. Encounter state updated.",
    }
