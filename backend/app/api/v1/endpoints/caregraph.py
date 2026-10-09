"""CLINOVA AI — CAREGRAPH Workstation Router.

Provides patient-level clinical state endpoints:
- Full CareGraph graph view (nodes, edges, trajectory, uncertainty)
- Serial vital sign entry and real-time trajectory slope (Delta R) recalculation
- Missing protocol parameters and targeted follow-up question generation
- Clinician node verification gate
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import (
    Case,
    Patient,
    VitalReading,
    EvidenceRecord,
    ClinicianDecision,
    AuditLog,
    Facility,
)
from app.domain.caregraph.engine import (
    calculate_risk_score,
    calculate_trajectory_slope,
    evaluate_uncertainty_and_gaps,
    build_caregraph_view,
    VerificationStatus,
)
from app.domain.signalgraph.engine import signal_engine
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import Permission, check_role_permission
from app.core.policy import authorize_case_access
from app.core.errors import ClinovaAPIError

router = APIRouter()


class VitalSignRequest(BaseModel):
    heart_rate: Optional[int] = Field(None, ge=20, le=260)
    systolic_bp: Optional[int] = Field(None, ge=30, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=20, le=200)
    spo2_percent: Optional[int] = Field(None, ge=30, le=100)
    respiratory_rate: Optional[int] = Field(None, ge=4, le=80)
    temperature_celsius: Optional[float] = Field(None, ge=28.0, le=44.0)
    avpu_score: Optional[str] = "ALERT"
    supplemental_o2: bool = False


class VerifyEvidenceRequest(BaseModel):
    evidence_id: str
    verification_status: str = "CONFIRMED"  # CONFIRMED, MODIFIED, DISPUTED
    clinician_id: str = "usr-doc-01"
    notes: Optional[str] = None


@router.get("/{case_id}", tags=["CareGraph"])
async def get_case_caregraph(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Returns the full dynamic CareGraph topology, trajectory, and uncertainty for a case."""
    stmt = (
        select(Case)
        .where(Case.id == case_id)
        .options(
            selectinload(Case.patient),
            selectinload(Case.facility),
            selectinload(Case.vitals),
            selectinload(Case.evidence_records),
            selectinload(Case.decisions),
            selectinload(Case.outcome),
        )
    )
    res = await db.execute(stmt)
    case = res.scalars().first()
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case {case_id} not found.", status_code=404)
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    vitals_history = [
        {
            "id": v.id,
            "heart_rate": v.heart_rate,
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "spo2_percent": v.spo2_percent,
            "respiratory_rate": v.respiratory_rate,
            "temperature_celsius": v.temperature_celsius,
            "avpu_score": v.avpu_score,
            "recorded_at": v.recorded_at,
        }
        for v in case.vitals
    ]

    ev_records = [
        {
            "id": e.id,
            "provenance_type": e.provenance_type,
            "source_filename": e.source_filename,
            "extracted_payload": e.extracted_payload,
            "confidence_score": e.confidence_score,
            "verification_status": e.verification_status,
            "verified_by": e.verified_by,
        }
        for e in case.evidence_records
    ]

    decisions_list = [
        {
            "id": d.id,
            "action_type": d.action_type,
            "decision_type": d.decision_type,
            "override_reason": d.override_reason,
            "notes": d.notes,
            "timestamp": d.timestamp,
        }
        for d in case.decisions
    ]

    # Compute trajectory slope
    slope, trend = calculate_trajectory_slope(vitals_history)

    # Compute uncertainty
    latest_vitals = vitals_history[-1] if vitals_history else {}
    u_eval = evaluate_uncertainty_and_gaps(
        case.primary_syndrome or "GENERAL_ROUTINE",
        latest_vitals,
        ev_records,
        narrative_text=case.presenting_complaint or "",
    )

    case_data_dict = {
        "id": case.id,
        "case_number": case.case_number,
        "patient_synthetic_id": case.patient.synthetic_id if case.patient else "SYN-PT",
        "age_bracket": case.patient.age_bracket if case.patient else "40-49",
        "biological_sex": case.patient.biological_sex if case.patient else "MALE",
        "status": case.status,
        "acuity_tier": case.acuity_tier,
        "risk_score": case.risk_score,
        "uncertainty_score": u_eval["uncertainty_score"],
        "trajectory_slope": slope,
        "presenting_complaint": case.presenting_complaint,
        "primary_syndrome": case.primary_syndrome,
        "required_bundle": case.required_bundle,
    }

    outcome_dict = None
    if case.outcome:
        outcome_dict = {
            "id": case.outcome.id,
            "disposition": case.outcome.disposition,
            "final_condition": case.outcome.final_condition,
            "actual_action": case.outcome.actual_action,
            "recommendation": case.outcome.recommendation,
            "professional_decision": case.outcome.professional_decision,
            "outcome_status": case.outcome.outcome_status,
            "recorded_by": case.outcome.recorded_by,
            "actor_role": case.outcome.actor_role,
            "is_corrected": case.outcome.is_corrected,
            "version": case.outcome.version,
            "notes": case.outcome.notes,
            "recorded_at": case.outcome.recorded_at.isoformat() if case.outcome.recorded_at else None,
        }

    graph_view = build_caregraph_view(
        case_data_dict,
        vitals_history,
        ev_records,
        decisions_list,
        outcome_data=outcome_dict,
    )

    return {
        "case": case_data_dict,
        "trajectory": {
            "slope": slope,
            "trend": trend,
            "readings_count": len(vitals_history),
        },
        "uncertainty": u_eval,
        "graph": graph_view,
        "evidence_records": ev_records,
        "vitals_history": vitals_history,
        "outcome": outcome_dict,
    }


@router.post("/{case_id}/vitals", tags=["CareGraph"])
async def append_vital_reading(
    case_id: str,
    req: VitalSignRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Appends serial vital signs.
    Recalculates NEWS2 composite score, R_t, and dynamic trajectory slope Delta R.
    """
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message=f"Case {case_id} not found.", status_code=404)
    await authorize_case_access(case, actor, required_permission=Permission.VITALS_RECORD, db=db)

    new_vital = VitalReading(
        case_id=case.id,
        heart_rate=req.heart_rate,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        spo2_percent=req.spo2_percent,
        respiratory_rate=req.respiratory_rate,
        temperature_celsius=req.temperature_celsius,
        avpu_score=req.avpu_score,
    )
    db.add(new_vital)
    await db.flush()

    # Fetch all vitals to compute trajectory slope
    vitals_q = await db.execute(
        select(VitalReading).where(VitalReading.case_id == case_id).order_by(VitalReading.recorded_at)
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
            "avpu_score": v.avpu_score,
            "recorded_at": v.recorded_at,
        }
        for v in all_vitals
    ]

    # Recalculate Risk & Acuity Tier
    new_rt, new_tier = calculate_risk_score(req.model_dump())
    new_slope, trend = calculate_trajectory_slope(v_history)

    # Update case
    case.risk_score = new_rt
    case.acuity_tier = new_tier
    case.trajectory_slope = new_slope
    case.updated_at = datetime.now(timezone.utc)

    # Log Audit
    audit = AuditLog(
        actor_id=actor.actor_id,
        action="VITALS_APPENDED",
        entity_type="CASE",
        entity_id=case.id,
        details={
            "new_risk_score": new_rt,
            "acuity_tier": new_tier,
            "trajectory_slope": new_slope,
            "trend": trend,
        },
    )
    db.add(audit)
    await db.commit()

    return {
        "case_id": case.id,
        "updated_risk_score": new_rt,
        "updated_acuity_tier": new_tier,
        "trajectory_slope": new_slope,
        "trajectory_trend": trend,
        "vital_reading_id": new_vital.id,
        "alert": "RAPID_DETERIORATION" if new_slope >= 1.5 else ("HIGH_ACUITY" if new_rt >= 0.70 else "NORMAL"),
    }


@router.get("/{case_id}/missing", tags=["CareGraph"])
async def get_missing_protocol_parameters(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Returns missing parameters and diagnostic uncertainty score."""
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message="Case not found.", status_code=404)
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    vitals_q = await db.execute(
        select(VitalReading).where(VitalReading.case_id == case_id).order_by(VitalReading.recorded_at.desc())
    )
    latest_vital = vitals_q.scalars().first()
    v_dict = {
        "heart_rate": latest_vital.heart_rate if latest_vital else None,
        "systolic_bp": latest_vital.systolic_bp if latest_vital else None,
        "spo2_percent": latest_vital.spo2_percent if latest_vital else None,
        "respiratory_rate": latest_vital.respiratory_rate if latest_vital else None,
        "temperature_celsius": latest_vital.temperature_celsius if latest_vital else None,
    }

    ev_q = await db.execute(select(EvidenceRecord).where(EvidenceRecord.case_id == case_id))
    ev_list = [
        {"confidence_score": e.confidence_score, "verification_status": e.verification_status}
        for e in ev_q.scalars().all()
    ]

    u_eval = evaluate_uncertainty_and_gaps(
        case.primary_syndrome or "GENERAL_ROUTINE",
        v_dict,
        ev_list,
        narrative_text=case.presenting_complaint or "",
    )

    return u_eval


@router.post("/{case_id}/questions", tags=["CareGraph"])
async def generate_targeted_questions(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Generates targeted follow-up questions to resolve diagnostic gaps."""
    missing_data = await get_missing_protocol_parameters(case_id, db, actor)
    return {"follow_up_questions": missing_data["follow_up_questions"]}


@router.post("/{case_id}/verify", tags=["CareGraph"])
async def verify_evidence_node(
    case_id: str,
    req: VerifyEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Promotes an evidence node to Clinician-Verified status.
    Decreases diagnostic uncertainty U_t by improving V_clinician ratio.
    """
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message="Case not found.", status_code=404)
    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)
    if not actor.is_clinician():
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Evidence verification requires a licensed clinician.",
            status_code=403,
        )

    ev = await db.get(EvidenceRecord, req.evidence_id)
    if not ev or ev.case_id != case_id:
        raise ClinovaAPIError(category="NOT_FOUND", message="Evidence record not found.", status_code=404)

    ev.verification_status = req.verification_status
    ev.verified_by = actor.actor_id

    # Recalculate uncertainty and update Case model
    ev_q = await db.execute(select(EvidenceRecord).where(EvidenceRecord.case_id == case_id))
    all_ev = ev_q.scalars().all()

    verified_count = sum(1 for e in all_ev if e.verification_status == "CONFIRMED")
    v_ratio = verified_count / max(1, len(all_ev))

    if case:
        v_q = await db.execute(
            select(VitalReading).where(VitalReading.case_id == case_id).order_by(VitalReading.recorded_at.desc())
        )
        latest_vital = v_q.scalars().first()
        v_dict = {
            "heart_rate": latest_vital.heart_rate if latest_vital else None,
            "systolic_bp": latest_vital.systolic_bp if latest_vital else None,
            "spo2_percent": latest_vital.spo2_percent if latest_vital else None,
            "respiratory_rate": latest_vital.respiratory_rate if latest_vital else None,
            "temperature_celsius": latest_vital.temperature_celsius if latest_vital else None,
        }
        ev_dicts = [
            {"confidence_score": e.confidence_score, "verification_status": e.verification_status}
            for e in all_ev
        ]
        u_eval = evaluate_uncertainty_and_gaps(
            case.primary_syndrome or "GENERAL_ROUTINE",
            v_dict,
            ev_dicts,
            narrative_text=case.presenting_complaint or "",
        )
        case.uncertainty_score = u_eval["uncertainty_score"]
        case.updated_at = datetime.now(timezone.utc)

    # Audit
    audit = AuditLog(
        actor_id=actor.actor_id,
        action="EVIDENCE_VERIFIED",
        entity_type="EVIDENCE_RECORD",
        entity_id=ev.id,
        details={
            "new_status": req.verification_status,
            "notes": req.notes,
            "new_verification_ratio": round(v_ratio, 2),
            "new_uncertainty_score": case.uncertainty_score if case else None,
        },
    )
    db.add(audit)
    await db.commit()

    return {
        "evidence_id": ev.id,
        "verification_status": ev.verification_status,
        "verified_by": ev.verified_by,
        "new_verification_ratio": round(v_ratio, 2),
        "updated_uncertainty_score": case.uncertainty_score if case else None,
        "message": "Evidence node successfully verified by clinician. Diagnostic uncertainty reduced.",
    }
