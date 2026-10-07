"""CLINOVA AI — Clinical Case Queue & Encounter Router.

Provides prioritized clinical queue management, case lookups,
and encounter outcome closure (DOC-07).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import Case, Patient, Facility, CaseOutcome, AuditLog, VitalReading
from app.domain.signalgraph.engine import signal_engine

router = APIRouter()


class CaseOutcomeRequest(BaseModel):
    disposition: str  # DISCHARGED_ROUTINE, TRANSFERRED_OUT, ADMITTED_INPATIENT, OBSERVATION_RESOLVED
    final_condition: str = "STABLE"  # STABLE, IMPROVED, CRITICAL, REFERRED
    notes: Optional[str] = None
    actor_id: str = "usr-doc-01"


@router.get("/queue", tags=["Case Management"])
async def get_clinical_queue(
    department: Optional[str] = None,
    acuity: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns prioritized clinical triage queue sorted by acuity tier (Critical > Urgent > Moderate > Routine)
    and waiting SLA duration.
    """
    stmt = (
        select(Case)
        .options(
            selectinload(Case.patient),
            selectinload(Case.facility),
            selectinload(Case.vitals),
        )
        .order_by(
            desc(Case.risk_score),
            desc(Case.trajectory_slope),
            Case.created_at,
        )
    )
    if acuity:
        stmt = stmt.where(Case.acuity_tier == acuity.upper())
    if status:
        stmt = stmt.where(Case.status == status.upper())

    res = await db.execute(stmt)
    cases = res.scalars().all()

    queue_items = []
    now = datetime.now(timezone.utc)
    for c in cases:
        # Calculate waiting time in minutes
        created_time = c.created_at
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        wait_min = int((now - created_time).total_seconds() / 60.0)

        # SLA calculation: Critical <= 10m, Urgent <= 30m, Moderate <= 60m, Routine <= 120m
        sla_limit = 10 if c.acuity_tier == "CRITICAL" else (30 if c.acuity_tier == "URGENT" else (60 if c.acuity_tier == "MODERATE" else 120))
        sla_breached = wait_min > sla_limit

        latest_vitals = c.vitals[-1] if c.vitals else None

        queue_items.append({
            "case_id": c.id,
            "case_number": c.case_number,
            "patient_synthetic_id": c.patient.synthetic_id if c.patient else "SYN-PT",
            "age_bracket": c.patient.age_bracket if c.patient else "40-49",
            "biological_sex": c.patient.biological_sex if c.patient else "MALE",
            "facility_name": c.facility.name if c.facility else "Unknown",
            "status": c.status,
            "acuity_tier": c.acuity_tier,
            "risk_score": c.risk_score,
            "trajectory_slope": c.trajectory_slope,
            "uncertainty_score": c.uncertainty_score,
            "presenting_complaint": c.presenting_complaint,
            "primary_syndrome": c.primary_syndrome,
            "required_bundle": c.required_bundle,
            "waiting_minutes": wait_min,
            "sla_limit_minutes": sla_limit,
            "sla_breached": sla_breached,
            "latest_vitals": {
                "hr": latest_vitals.heart_rate if latest_vitals else None,
                "bp": f"{latest_vitals.systolic_bp}/{latest_vitals.diastolic_bp}" if latest_vitals and latest_vitals.systolic_bp else None,
                "spo2": latest_vitals.spo2_percent if latest_vitals else None,
                "temp": latest_vitals.temperature_celsius if latest_vitals else None,
            } if latest_vitals else None,
            "created_at": c.created_at.isoformat(),
        })

    return {
        "total_cases": len(queue_items),
        "critical_count": sum(1 for q in queue_items if q["acuity_tier"] == "CRITICAL"),
        "urgent_count": sum(1 for q in queue_items if q["acuity_tier"] == "URGENT"),
        "queue": queue_items,
    }


@router.get("", tags=["Case Management"])
async def list_cases(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Lists recent clinical encounters."""
    stmt = (
        select(Case)
        .options(selectinload(Case.patient), selectinload(Case.facility))
        .order_by(desc(Case.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    cases = res.scalars().all()
    return [
        {
            "id": c.id,
            "case_number": c.case_number,
            "patient_synthetic_id": c.patient.synthetic_id if c.patient else "SYN-PT",
            "status": c.status,
            "acuity_tier": c.acuity_tier,
            "risk_score": c.risk_score,
            "uncertainty_score": c.uncertainty_score,
            "primary_syndrome": c.primary_syndrome,
            "facility_name": c.facility.name if c.facility else "Unknown",
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ]


@router.get("/{case_id}", tags=["Case Management"])
async def get_case_detail(case_id: str, db: AsyncSession = Depends(get_db)):
    """Returns encounter summary and active clinical state."""
    stmt = select(Case).where(Case.id == case_id).options(selectinload(Case.patient), selectinload(Case.facility))
    res = await db.execute(stmt)
    case = res.scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    return {
        "id": case.id,
        "case_number": case.case_number,
        "patient": {
            "synthetic_id": case.patient.synthetic_id if case.patient else "SYN-PT",
            "age_bracket": case.patient.age_bracket if case.patient else "40-49",
            "biological_sex": case.patient.biological_sex if case.patient else "MALE",
        },
        "facility": {
            "id": case.facility.id if case.facility else None,
            "name": case.facility.name if case.facility else "Unknown",
            "tier": case.facility.tier if case.facility else "Unknown",
        },
        "status": case.status,
        "acuity_tier": case.acuity_tier,
        "risk_score": case.risk_score,
        "trajectory_slope": case.trajectory_slope,
        "uncertainty_score": case.uncertainty_score,
        "presenting_complaint": case.presenting_complaint,
        "primary_syndrome": case.primary_syndrome,
        "required_bundle": case.required_bundle,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
    }


@router.post("/{case_id}/outcome", tags=["Case Management"])
async def record_case_outcome(
    case_id: str,
    req: CaseOutcomeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Closes the encounter loop by recording final clinical disposition.
    Transitions FSM state to OUTCOME and feeds de-identified event to SignalGraph.
    """
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    existing_outcome = (await db.execute(select(CaseOutcome).where(CaseOutcome.case_id == case.id))).scalars().first()
    if existing_outcome:
        existing_outcome.disposition = req.disposition
        existing_outcome.final_condition = req.final_condition
        existing_outcome.notes = req.notes
        existing_outcome.recorded_at = datetime.now(timezone.utc)
        outcome = existing_outcome
    else:
        outcome = CaseOutcome(
            case_id=case.id,
            disposition=req.disposition,
            final_condition=req.final_condition,
            notes=req.notes,
        )
        db.add(outcome)

    case.status = "OUTCOME"
    case.updated_at = datetime.now(timezone.utc)

    # Audit Trail
    audit = AuditLog(
        actor_id=req.actor_id,
        action="CASE_OUTCOME_RECORDED",
        entity_type="CASE",
        entity_id=case.id,
        details={
            "disposition": req.disposition,
            "final_condition": req.final_condition,
            "notes": req.notes,
        },
    )
    db.add(audit)
    await db.commit()

    # Feed SignalGraph
    signal_engine.record_event(
        facility_id=case.facility_id,
        syndrome_tag=f"OUTCOME_{req.disposition}",
        acuity_tier=case.acuity_tier,
    )

    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "status": case.status,
        "disposition": req.disposition,
        "final_condition": req.final_condition,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "message": "Encounter closed. Outcome logged and de-identified telemetry routed to SignalGraph.",
    }
