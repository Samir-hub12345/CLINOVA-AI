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
from app.db.models import (
    Case,
    Patient,
    Facility,
    CaseOutcome,
    AuditLog,
    VitalReading,
    Vital,
    ClinicianDecision,
)
from app.domain.signalgraph.engine import signal_engine
from app.domain.triage import sort_clinical_queue, compute_deterministic_triage
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import (
    Permission,
    check_role_permission,
    ROLE_PATIENT,
    ROLE_SYSTEM_ADMIN,
    ROLE_AUDITOR,
)
from app.core.policy import authorize_case_access
from app.core.errors import ClinovaAPIError

router = APIRouter()


class CaseOutcomeRequest(BaseModel):
    disposition: str  # DISCHARGED_ROUTINE, TRANSFERRED_OUT, ADMITTED_INPATIENT, OBSERVATION_RESOLVED, UNKNOWN
    final_condition: str = "STABLE"  # STABLE, IMPROVED, DETERIORATED, CRITICAL, RECOVERED, UNKNOWN
    actual_action: Optional[str] = "UNKNOWN"  # TRANSFERRED, DISCHARGED, ADMITTED_LOCAL, OBSERVED, TREATMENT_COMPLETED, UNKNOWN
    outcome_status: Optional[str] = None  # RECOVERED, IMPROVED, STABLE, DETERIORATED, EXPIRED, UNKNOWN
    recommendation: Optional[str] = None
    professional_decision: Optional[str] = None
    notes: Optional[str] = None
    actor_id: Optional[str] = None
    is_corrected: bool = False


@router.get("/queue", tags=["Case Management"])
async def get_clinical_queue(
    department: Optional[str] = None,
    acuity: Optional[str] = None,
    status: Optional[str] = None,
    pathway: Optional[str] = None,
    has_red_flags: Optional[bool] = None,
    facility_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Returns prioritized clinical triage queue sorted deterministically:
    Emergency Pathway > Active Critical Red Flags > Priority Tier > Risk Score > Dynamic Query-Time Wait Time.
    """
    check_role_permission(actor.role, Permission.CASE_LIST)
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to view the clinical staff triage queue.",
            status_code=403,
        )

    # Cross-facility denial
    if facility_id:
        if actor.role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
            if actor.facility_id and actor.facility_id != facility_id:
                raise ClinovaAPIError(
                    category="NOT_FOUND",
                    message=f"Facility '{facility_id}' not found.",
                    status_code=404,
                )

    stmt = (
        select(Case)
        .options(
            selectinload(Case.patient),
            selectinload(Case.facility),
            selectinload(Case.vitals),
            selectinload(Case.vitals_list),
        )
    )

    # Enforce facility scoping
    if actor.role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR}:
        if actor.facility_id:
            stmt = stmt.where(Case.facility_id == actor.facility_id)
        else:
            stmt = stmt.where(Case.facility_id == "UNASSIGNED")
    elif facility_id:
        stmt = stmt.where(Case.facility_id == facility_id)

    if acuity:
        stmt = stmt.where(Case.acuity_tier == acuity.upper())
    if status:
        stmt = stmt.where(Case.status == status.upper())
    if pathway:
        stmt = stmt.where(Case.pathway == pathway.upper())

    res = await db.execute(stmt)
    cases = res.scalars().all()

    queue_items = []
    now = datetime.now(timezone.utc)
    for c in cases:
        # Calculate waiting time in minutes dynamically at query time
        created_time = c.created_at
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        wait_min = int((now - created_time).total_seconds() / 60.0)

        # Get latest vital reading
        latest_canonical = c.vitals_list[-1] if c.vitals_list else None
        latest_compat = c.vitals[-1] if c.vitals else None
        latest_vital = latest_canonical or latest_compat

        # Compute deterministic triage metrics
        triage_summary = compute_deterministic_triage(
            case_id=c.id,
            pathway=c.pathway,
            current_state=c.current_state,
            presenting_complaint=c.presenting_complaint,
            latest_vital=latest_canonical or latest_compat,
            now=now,
        )

        critical_rf_count = sum(
            1 for rf in triage_summary.get("red_flags", []) if rf.get("triggered") and rf.get("severity") == "CRITICAL"
        )
        has_crit_rf = critical_rf_count > 0 or triage_summary.get("has_critical_red_flags", False)

        # Optional red-flag filtering
        if has_red_flags is not None:
            if has_red_flags and not has_crit_rf:
                continue
            if not has_red_flags and has_crit_rf:
                continue

        # Authoritative query-time acuity, risk, and priority values
        acuity_val = triage_summary.get("acuity_tier", c.acuity_tier or "ROUTINE")
        risk_score_val = triage_summary.get("risk_score", c.risk_score)
        uncertainty_val = triage_summary.get("uncertainty_score", c.uncertainty_score)
        priority_tier_val = triage_summary.get("priority_tier", "P4_ROUTINE")

        # SLA calculation: Critical <= 10m, Urgent <= 30m, Moderate <= 60m, Routine <= 120m
        sla_limit = 10 if acuity_val == "CRITICAL" else (30 if acuity_val == "URGENT" else (60 if acuity_val == "MODERATE" else 120))
        sla_breached = wait_min > sla_limit

        latest_vitals_dict = None
        if latest_vital:
            latest_vitals_dict = {
                "hr": latest_vital.heart_rate,
                "bp": f"{latest_vital.systolic_bp}/{latest_vital.diastolic_bp}" if latest_vital.systolic_bp else None,
                "spo2": latest_vital.spo2_percent,
                "temp": latest_vital.temperature_celsius,
                "rr": getattr(latest_vital, "respiratory_rate", None),
                "avpu": getattr(latest_vital, "avpu_score", "ALERT"),
            }

        emergency_active = bool(c.pathway.upper().startswith("EMERGENCY") or has_crit_rf)
        prov_type = getattr(latest_vital, "source", "STAFF_ENTERED") if latest_vital else "SYSTEM_DERIVED"
        epistemic_status = "VERIFIED" if (acuity_val in ["CRITICAL", "URGENT"] and latest_vital) else ("KNOWN" if latest_vital else "UNKNOWN")
        next_action = "IMMEDIATE_RESUSCITATION" if emergency_active else (
            "TRIAGE_ASSESSMENT" if c.current_state in ["INTAKE_RECORDED", "TRIAGE_PENDING"] else "CLINICAL_REVIEW"
        )

        queue_items.append({
            "case_id": c.id,
            "case_number": c.case_number,
            "patient_synthetic_id": c.patient.synthetic_id if c.patient else "SYN-PT",
            "age_bracket": c.patient.age_bracket if c.patient else "40-49",
            "biological_sex": c.patient.biological_sex if c.patient else "MALE",
            "facility_id": c.facility_id,
            "facility_name": c.facility.name if c.facility else "Unknown",
            "pathway": c.pathway,
            "current_state": c.current_state,
            "status": c.status,
            "priority_tier": priority_tier_val,
            "acuity_tier": acuity_val,
            "risk_score": risk_score_val,
            "trajectory_slope": c.trajectory_slope,
            "uncertainty_score": uncertainty_val,
            "presenting_complaint": c.presenting_complaint,
            "primary_syndrome": c.primary_syndrome,
            "required_bundle": c.required_bundle,
            "waiting_minutes": wait_min,
            "sla_limit_minutes": sla_limit,
            "sla_breached": sla_breached,
            "emergency_active": emergency_active,
            "has_critical_red_flags": has_crit_rf,
            "critical_red_flags_count": critical_rf_count,
            "red_flags_count": critical_rf_count,
            "vitals_overall_status": triage_summary.get("vitals_overall_status", "MISSING"),
            "missing_critical_vitals": triage_summary.get("missing_critical_vitals", []),
            "latest_vitals": latest_vitals_dict,
            "epistemic_status": epistemic_status,
            "provenance_type": prov_type,
            "next_recommended_action": next_action,
            "created_at": c.created_at.isoformat(),
        })

    # Sort queue deterministically
    sorted_queue = sort_clinical_queue(queue_items, now=now)

    return {
        "total_cases": len(sorted_queue),
        "critical_count": sum(1 for q in sorted_queue if q["acuity_tier"] == "CRITICAL"),
        "urgent_count": sum(1 for q in sorted_queue if q["acuity_tier"] == "URGENT"),
        "moderate_count": sum(1 for q in sorted_queue if q["acuity_tier"] == "MODERATE"),
        "routine_count": sum(1 for q in sorted_queue if q["acuity_tier"] == "ROUTINE"),
        "queue": sorted_queue,
        "is_synthetic_mode": True,
        "generated_at": now.isoformat(),
    }


# Note: Master Case listing and detail retrieval are canonically handled
# by app.api.v1.endpoints.foundation router to guarantee Pydantic v2 schemas,
# deterministic state machine compliance, and comprehensive filtering.



@router.post("/{case_id}/outcome", tags=["Case Management"])
async def record_case_outcome(
    case_id: str,
    req: CaseOutcomeRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Closes the encounter loop by recording final clinical disposition.
    Strictly separates:
    - AI Recommendation
    - Professional Decision
    - Actual Action
    - Clinical Outcome
    Transitions FSM state to OUTCOME and feeds de-identified event to SignalGraph.
    """
    check_role_permission(actor.role, Permission.DISPOSITION_FINALIZE)
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message="Case not found.", status_code=404)

    await authorize_case_access(case, actor, required_permission=Permission.DISPOSITION_FINALIZE, db=db)

    # Resolve latest clinician decision if not explicitly supplied
    dec_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case.id).order_by(ClinicianDecision.timestamp.desc())
    latest_dec = (await db.execute(dec_stmt)).scalars().first()
    default_rec = latest_dec.decision_type if latest_dec else "NONE"
    default_prof = latest_dec.action_type if latest_dec else "NONE"

    recommendation = req.recommendation or default_rec
    professional_decision = req.professional_decision or default_prof
    actual_action = req.actual_action or "UNKNOWN"
    outcome_status = req.outcome_status or req.final_condition or "UNKNOWN"

    existing_outcome = (await db.execute(select(CaseOutcome).where(CaseOutcome.case_id == case.id))).scalars().first()
    if existing_outcome:
        if req.is_corrected:
            action = "CASE_OUTCOME_CORRECTED"
            existing_outcome.version += 1
            existing_outcome.is_corrected = True
        else:
            action = "CASE_OUTCOME_RECORDED"

        existing_outcome.disposition = req.disposition
        existing_outcome.final_condition = req.final_condition
        existing_outcome.actual_action = actual_action
        existing_outcome.recommendation = recommendation
        existing_outcome.professional_decision = professional_decision
        existing_outcome.outcome_status = outcome_status
        existing_outcome.notes = req.notes
        existing_outcome.recorded_by = actor.actor_id
        existing_outcome.actor_role = actor.role
        existing_outcome.recorded_at = datetime.now(timezone.utc)
        outcome = existing_outcome
    else:
        action = "CASE_OUTCOME_RECORDED"
        outcome = CaseOutcome(
            case_id=case.id,
            disposition=req.disposition,
            final_condition=req.final_condition,
            actual_action=actual_action,
            recommendation=recommendation,
            professional_decision=professional_decision,
            outcome_status=outcome_status,
            recorded_by=actor.actor_id,
            actor_role=actor.role,
            is_corrected=False,
            version=1,
            notes=req.notes,
        )
        db.add(outcome)

    case.status = "OUTCOME"
    case.updated_at = datetime.now(timezone.utc)
    await db.flush()

    # Audit Trail
    audit = AuditLog(
        actor_id=actor.actor_id,
        action=action,
        entity_type="CASE_OUTCOME",
        entity_id=outcome.id,
        details={
            "case_id": case.id,
            "disposition": outcome.disposition,
            "final_condition": outcome.final_condition,
            "actual_action": outcome.actual_action,
            "recommendation": outcome.recommendation,
            "professional_decision": outcome.professional_decision,
            "outcome_status": outcome.outcome_status,
            "is_corrected": outcome.is_corrected,
            "version": outcome.version,
        },
    )
    db.add(audit)
    await db.commit()
    await db.refresh(outcome)

    # Feed SignalGraph with idempotency key
    signal_engine.record_event(
        facility_id=case.facility_id,
        syndrome_tag=f"OUTCOME_{outcome.disposition}",
        acuity_tier=case.acuity_tier,
        source_event_id=outcome.id,
        disposition=outcome.disposition,
        actual_action=outcome.actual_action,
        outcome_status=outcome.outcome_status,
    )

    return {
        "outcome_id": outcome.id,
        "case_id": case.id,
        "case_number": case.case_number,
        "status": case.status,
        "recommendation": outcome.recommendation,
        "professional_decision": outcome.professional_decision,
        "actual_action": outcome.actual_action,
        "disposition": outcome.disposition,
        "final_condition": outcome.final_condition,
        "outcome_status": outcome.outcome_status,
        "is_corrected": outcome.is_corrected,
        "version": outcome.version,
        "recorded_by": outcome.recorded_by,
        "completed_at": outcome.recorded_at.isoformat() if outcome.recorded_at else datetime.now(timezone.utc).isoformat(),
        "message": "Encounter outcome recorded. Distinct stages preserved and telemetry routed to SignalGraph.",
    }


@router.get("/{case_id}/outcome", tags=["Case Management"])
async def get_case_outcome(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Retrieves persisted four-stage outcome details for a case."""
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError(category="NOT_FOUND", message="Case not found.", status_code=404)
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(CaseOutcome).where(CaseOutcome.case_id == case_id)
    outcome = (await db.execute(stmt)).scalars().first()
    if not outcome:
        raise ClinovaAPIError(category="NOT_FOUND", message="No outcome recorded for this case.", status_code=404)

    return {
        "outcome_id": outcome.id,
        "case_id": case.id,
        "case_number": case.case_number,
        "recommendation": outcome.recommendation,
        "professional_decision": outcome.professional_decision,
        "actual_action": outcome.actual_action,
        "disposition": outcome.disposition,
        "final_condition": outcome.final_condition,
        "outcome_status": outcome.outcome_status,
        "notes": outcome.notes,
        "recorded_by": outcome.recorded_by,
        "actor_role": outcome.actor_role,
        "is_corrected": outcome.is_corrected,
        "version": outcome.version,
        "recorded_at": outcome.recorded_at.isoformat() if outcome.recorded_at else None,
    }
