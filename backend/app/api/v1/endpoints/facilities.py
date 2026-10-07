"""CLINOVA AI — FACILITYGRAPH Network & Feasibility Router.

Provides facility network topology, capability checking, care feasibility predicate (Phi),
interactive capability toggles (e.g. setting CT scanner offline), and capacity updates.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import Facility, FacilityCapability, AuditLog
from app.domain.facilitygraph.engine import (
    evaluate_feasibility,
    rank_referral_destinations,
    CARE_BUNDLES,
)

router = APIRouter()


class MatchCareRequest(BaseModel):
    facility_id: str
    required_bundle: str


class ReferralRankRequest(BaseModel):
    current_facility_id: str
    required_bundle: str


class ToggleCapabilityRequest(BaseModel):
    capability_code: str
    is_operational: bool
    maintenance_note: Optional[str] = None


class UpdateCapacityRequest(BaseModel):
    icu_beds_available: Optional[int] = None
    general_beds_available: Optional[int] = None
    ed_waiting_cases: Optional[int] = None
    ed_avg_wait_min: Optional[int] = None


@router.get("", tags=["FacilityGraph"])
async def list_facilities(db: AsyncSession = Depends(get_db)):
    """Lists all network healthcare facilities, bed availability, and operational capabilities."""
    stmt = select(Facility).options(selectinload(Facility.capabilities))
    res = await db.execute(stmt)
    facs = res.scalars().all()

    output = []
    for f in facs:
        output.append({
            "id": f.id,
            "facility_code": f.facility_code,
            "name": f.name,
            "tier": f.tier,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "icu_beds_total": f.icu_beds_total,
            "icu_beds_available": f.icu_beds_available,
            "general_beds_total": f.general_beds_total,
            "general_beds_available": f.general_beds_available,
            "ed_waiting_cases": f.ed_waiting_cases,
            "ed_avg_wait_min": f.ed_avg_wait_min,
            "capabilities": [
                {
                    "capability_code": c.capability_code,
                    "is_operational": c.is_operational,
                    "maintenance_note": c.maintenance_note,
                }
                for c in f.capabilities
            ],
        })
    return output


@router.get("/bundles", tags=["FacilityGraph"])
async def list_care_bundles():
    """Lists supported clinical care bundle specifications."""
    return CARE_BUNDLES


@router.get("/{facility_id}", tags=["FacilityGraph"])
async def get_facility(facility_id: str, db: AsyncSession = Depends(get_db)):
    """Returns facility status and full capabilities list."""
    stmt = select(Facility).where(Facility.id == facility_id).options(selectinload(Facility.capabilities))
    res = await db.execute(stmt)
    f = res.scalars().first()
    if not f:
        raise HTTPException(status_code=404, detail="Facility not found.")

    return {
        "id": f.id,
        "name": f.name,
        "tier": f.tier,
        "latitude": f.latitude,
        "longitude": f.longitude,
        "icu_beds": {"total": f.icu_beds_total, "available": f.icu_beds_available},
        "general_beds": {"total": f.general_beds_total, "available": f.general_beds_available},
        "ed_status": {"waiting": f.ed_waiting_cases, "avg_wait_min": f.ed_avg_wait_min},
        "capabilities": [
            {"code": c.capability_code, "is_operational": c.is_operational}
            for c in f.capabilities
        ],
    }


@router.post("/match", tags=["FacilityGraph"])
async def check_local_feasibility(req: MatchCareRequest, db: AsyncSession = Depends(get_db)):
    """
    Evaluates the care feasibility predicate Phi(F, B) for a specific facility and clinical bundle.
    Returns status (FEASIBLE, DEGRADED, INFEASIBLE).
    """
    stmt = select(Facility).where(Facility.id == req.facility_id).options(selectinload(Facility.capabilities))
    res = await db.execute(stmt)
    f = res.scalars().first()
    if not f:
        raise HTTPException(status_code=404, detail="Facility not found.")

    fac_dict = {
        "id": f.id,
        "name": f.name,
        "tier": f.tier,
        "icu_beds_available": f.icu_beds_available,
        "general_beds_available": f.general_beds_available,
        "capabilities": [(c.capability_code, c.is_operational) for c in f.capabilities],
    }

    feasibility = evaluate_feasibility(fac_dict, req.required_bundle)
    return {
        "facility_id": f.id,
        "facility_name": f.name,
        "required_bundle": req.required_bundle,
        "feasibility": feasibility,
    }


@router.post("/referral-rank", tags=["FacilityGraph"])
async def rank_network_referrals(req: ReferralRankRequest, db: AsyncSession = Depends(get_db)):
    """Ranks alternative network receiving centers based on feasibility, capacity, and transit time."""
    stmt = select(Facility).options(selectinload(Facility.capabilities))
    res = await db.execute(stmt)
    all_facs = res.scalars().all()

    current_fac = next((f for f in all_facs if f.id == req.current_facility_id), None)
    if not current_fac:
        raise HTTPException(status_code=404, detail="Current facility not found.")

    curr_dict = {
        "id": current_fac.id,
        "name": current_fac.name,
        "latitude": current_fac.latitude,
        "longitude": current_fac.longitude,
    }

    network_list = []
    for f in all_facs:
        network_list.append({
            "id": f.id,
            "name": f.name,
            "tier": f.tier,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "icu_beds_available": f.icu_beds_available,
            "general_beds_available": f.general_beds_available,
            "ed_avg_wait_min": f.ed_avg_wait_min,
            "capabilities": [(c.capability_code, c.is_operational) for c in f.capabilities],
        })

    ranked = rank_referral_destinations(curr_dict, network_list, req.required_bundle)
    return {
        "origin_facility": curr_dict,
        "required_bundle": req.required_bundle,
        "ranked_destinations": ranked,
    }


@router.post("/{facility_id}/toggle-capability", tags=["FacilityGraph"])
async def toggle_facility_capability(
    facility_id: str,
    req: ToggleCapabilityRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Enables/disables a capability (e.g., setting CT scanner offline).
    Used to demonstrate dynamic care feasibility flipping.
    """
    stmt = (
        select(FacilityCapability)
        .where(
            FacilityCapability.facility_id == facility_id,
            FacilityCapability.capability_code == req.capability_code,
        )
    )
    res = await db.execute(stmt)
    cap = res.scalars().first()
    if not cap:
        # Create it if doesn't exist
        cap = FacilityCapability(
            facility_id=facility_id,
            capability_code=req.capability_code,
            is_operational=req.is_operational,
            maintenance_note=req.maintenance_note,
        )
        db.add(cap)
    else:
        cap.is_operational = req.is_operational
        cap.maintenance_note = req.maintenance_note

    audit = AuditLog(
        actor_id="FACILITY_ADMIN",
        action="CAPABILITY_TOGGLED",
        entity_type="FACILITY",
        entity_id=facility_id,
        details={
            "capability_code": req.capability_code,
            "is_operational": req.is_operational,
            "maintenance_note": req.maintenance_note,
        },
    )
    db.add(audit)
    await db.commit()

    return {
        "facility_id": facility_id,
        "capability_code": req.capability_code,
        "is_operational": cap.is_operational,
        "message": f"Capability {req.capability_code} status updated to {req.is_operational}.",
    }


@router.post("/{facility_id}/update-capacity", tags=["FacilityGraph"])
async def update_facility_capacity(
    facility_id: str,
    req: UpdateCapacityRequest,
    db: AsyncSession = Depends(get_db),
):
    """Updates real-time bed availability and ED wait time to test capacity shifts."""
    fac = await db.get(Facility, facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found.")

    if req.icu_beds_available is not None:
        fac.icu_beds_available = req.icu_beds_available
    if req.general_beds_available is not None:
        fac.general_beds_available = req.general_beds_available
    if req.ed_waiting_cases is not None:
        fac.ed_waiting_cases = req.ed_waiting_cases
    if req.ed_avg_wait_min is not None:
        fac.ed_avg_wait_min = req.ed_avg_wait_min

    audit = AuditLog(
        actor_id="FACILITY_ADMIN",
        action="CAPACITY_UPDATED",
        entity_type="FACILITY",
        entity_id=facility_id,
        details=req.model_dump(exclude_none=True),
    )
    db.add(audit)
    await db.commit()

    return {
        "facility_id": facility_id,
        "icu_beds_available": fac.icu_beds_available,
        "general_beds_available": fac.general_beds_available,
        "ed_waiting_cases": fac.ed_waiting_cases,
        "ed_avg_wait_min": fac.ed_avg_wait_min,
        "message": "Facility capacity updated successfully.",
    }
