"""CLINOVA AI — Clinical Referral & SBAR Packet Router.

Manages inter-facility patient transfer preparation, automated SBAR report generation,
and dispatch state tracking (DOC-09, DOC-13).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import Case, Facility, Referral, AuditLog, VitalReading
from app.domain.facilitygraph.engine import generate_sbar_packet, haversine_transit_estimate
from app.domain.signalgraph.engine import signal_engine

router = APIRouter()


class GenerateSBARRequest(BaseModel):
    case_id: str
    destination_facility_id: str


class CreateReferralRequest(BaseModel):
    case_id: str
    origin_facility_id: str
    destination_facility_id: str
    required_bundle: str
    sbar_situation: str
    sbar_background: str
    sbar_assessment: str
    sbar_recommendation: str


class UpdateReferralStatusRequest(BaseModel):
    status: str  # ACCEPTED, DISPATCHED, COMPLETED, REJECTED


@router.post("/sbar", tags=["Referrals"])
async def prepare_sbar_packet(req: GenerateSBARRequest, db: AsyncSession = Depends(get_db)):
    """Generates standardized SBAR clinical transfer packet for inter-facility handoff."""
    case_stmt = select(Case).where(Case.id == req.case_id).options(selectinload(Case.patient))
    case = (await db.execute(case_stmt)).scalars().first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    origin_fac = await db.get(Facility, case.facility_id)
    dest_fac = await db.get(Facility, req.destination_facility_id)
    if not dest_fac:
        raise HTTPException(status_code=404, detail="Destination facility not found.")

    vitals_q = await db.execute(
        select(VitalReading).where(VitalReading.case_id == req.case_id).order_by(VitalReading.recorded_at.desc())
    )
    latest_vital = vitals_q.scalars().first()

    _, transit_min = haversine_transit_estimate(
        origin_fac.latitude if origin_fac else 20.5,
        origin_fac.longitude if origin_fac else 85.5,
        dest_fac.latitude,
        dest_fac.longitude,
    )

    synthetic_id = case.patient.synthetic_id if case.patient else f"SYN-PT-{case.id[:4]}"
    case_summary = {
        "patient_synthetic_id": synthetic_id,
        "primary_syndrome": case.primary_syndrome,
        "acuity_tier": case.acuity_tier,
        "presenting_complaint": case.presenting_complaint,
        "risk_score": case.risk_score,
        "trajectory_slope": case.trajectory_slope,
        "transit_minutes": transit_min,
        "vitals": {
            "heart_rate": latest_vital.heart_rate if latest_vital else "N/A",
            "systolic_bp": latest_vital.systolic_bp if latest_vital else "N/A",
            "diastolic_bp": latest_vital.diastolic_bp if latest_vital else "N/A",
            "spo2_percent": latest_vital.spo2_percent if latest_vital else "N/A",
        },
    }

    orig_dict = {"name": origin_fac.name if origin_fac else "Origin Facility", "tier": origin_fac.tier if origin_fac else "PHC"}
    dest_dict = {"name": dest_fac.name, "tier": dest_fac.tier}

    sbar = generate_sbar_packet(case_summary, orig_dict, dest_dict, case.required_bundle or "BUNDLE_ROUTINE_AMBULATORY")
    sbar["origin_facility_name"] = orig_dict["name"]
    sbar["destination_facility_name"] = dest_dict["name"]
    sbar["estimated_transit_minutes"] = transit_min
    return sbar


@router.post("/create", tags=["Referrals"])
async def create_referral(req: CreateReferralRequest, db: AsyncSession = Depends(get_db)):
    """Persists inter-facility referral and marks encounter as TRANSFER_PENDING."""
    case = await db.get(Case, req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    existing_ref = (await db.execute(select(Referral).where(Referral.case_id == case.id))).scalars().first()
    if existing_ref:
        existing_ref.origin_facility_id = req.origin_facility_id
        existing_ref.destination_facility_id = req.destination_facility_id
        existing_ref.required_bundle = req.required_bundle
        existing_ref.sbar_situation = req.sbar_situation
        existing_ref.sbar_background = req.sbar_background
        existing_ref.sbar_assessment = req.sbar_assessment
        existing_ref.sbar_recommendation = req.sbar_recommendation
        existing_ref.status = "REQUESTED"
        referral = existing_ref
    else:
        referral = Referral(
            id=str(uuid.uuid4()),
            case_id=case.id,
            origin_facility_id=req.origin_facility_id,
            destination_facility_id=req.destination_facility_id,
            required_bundle=req.required_bundle,
            sbar_situation=req.sbar_situation,
            sbar_background=req.sbar_background,
            sbar_assessment=req.sbar_assessment,
            sbar_recommendation=req.sbar_recommendation,
            status="REQUESTED",
        )
        db.add(referral)

    case.status = "TRANSFER_PENDING"
    case.updated_at = datetime.now(timezone.utc)
    await db.flush()

    audit = AuditLog(
        actor_id="CLINICIAN",
        action="REFERRAL_DISPATCHED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        details={
            "case_id": case.id,
            "destination_facility_id": req.destination_facility_id,
            "bundle": req.required_bundle,
        },
    )
    db.add(audit)
    await db.commit()

    return {
        "referral_id": referral.id,
        "case_id": case.id,
        "case_status": case.status,
        "referral_status": referral.status,
        "message": "Referral created. Ambulance transit coordination pending.",
    }


@router.post("/{referral_id}/status", tags=["Referrals"])
async def update_referral_status(
    referral_id: str,
    req: UpdateReferralStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """Updates referral status and drives case state machine."""
    ref = await db.get(Referral, referral_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found.")

    ref.status = req.status
    case = await db.get(Case, ref.case_id)

    if case:
        if req.status == "COMPLETED":
            case.status = "COMPLETED"
        elif req.status == "DISPATCHED":
            case.status = "TRANSFER"
        elif req.status == "REJECTED":
            case.status = "REFERRAL_FAILED"
        case.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        actor_id="REFERRAL_COORDINATOR",
        action="REFERRAL_STATUS_UPDATED",
        entity_type="REFERRAL",
        entity_id=ref.id,
        details={"status": req.status, "case_id": ref.case_id},
    )
    db.add(audit)
    await db.commit()

    return {
        "referral_id": ref.id,
        "referral_status": ref.status,
        "case_status": case.status if case else None,
    }
