"""CLINOVA AI — SIGNALGRAPH Operational Telemetry Router.

Exposes regional epidemiological clusters, Z-score alerts,
facility load monitoring, and event injection for scenario verification (DOC-10).
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import Facility
from app.domain.signalgraph.engine import signal_engine
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import (
    ROLE_SYSTEM_ADMIN,
    ROLE_AUDITOR,
    ROLE_PATIENT,
)
from app.core.errors import ClinovaAPIError

router = APIRouter()


class InjectEventRequest(BaseModel):
    facility_id: str = "FAC-DH-04"
    syndrome_tag: str = "SYNDROME_HEMORRHAGIC_FEVER"
    acuity_tier: str = "URGENT"


@router.get("/surges", tags=["SignalGraph"])
async def get_syndromic_surges(window_hours: int = 48):
    """Returns regional syndromic clusters and Z-score outbreak alarms."""
    return signal_engine.get_syndromic_clusters(window_hours=window_hours)


@router.get("/load", tags=["SignalGraph"])
async def get_facility_load(db: AsyncSession = Depends(get_db)):
    """Returns network facility bed occupancy and ED waiting times."""
    stmt = select(Facility)
    res = await db.execute(stmt)
    facs = res.scalars().all()
    fac_data = [
        {
            "id": f.id,
            "name": f.name,
            "tier": f.tier,
            "icu_beds_total": f.icu_beds_total,
            "icu_beds_available": f.icu_beds_available,
            "general_beds_total": f.general_beds_total,
            "general_beds_available": f.general_beds_available,
            "ed_waiting_cases": f.ed_waiting_cases,
            "ed_avg_wait_min": f.ed_avg_wait_min,
        }
        for f in facs
    ]
    return signal_engine.get_facility_load_metrics(fac_data)


@router.get("/summary", tags=["SignalGraph"])
async def get_macro_summary(db: AsyncSession = Depends(get_db)):
    """Provides high-level system operations and epidemiological summary."""
    stmt = select(Facility)
    res = await db.execute(stmt)
    facs = res.scalars().all()
    fac_data = [
        {
            "id": f.id,
            "name": f.name,
            "tier": f.tier,
            "icu_beds_total": f.icu_beds_total,
            "icu_beds_available": f.icu_beds_available,
            "general_beds_total": f.general_beds_total,
            "general_beds_available": f.general_beds_available,
            "ed_waiting_cases": f.ed_waiting_cases,
            "ed_avg_wait_min": f.ed_avg_wait_min,
        }
        for f in facs
    ]
    return signal_engine.get_macro_summary(fac_data)


@router.post("/inject-event", tags=["SignalGraph"])
async def inject_synthetic_event(
    req: InjectEventRequest,
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Ingests synthetic clinical encounter signal into the real-time event pipeline.
    Used for automated scenario validation and outbreak simulation.
    """
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            category="AUTHORIZATION_ERROR",
            message="Patients are not authorized to inject operational telemetry signals.",
            status_code=403,
        )

    if actor.role not in {ROLE_SYSTEM_ADMIN, ROLE_AUDITOR, "RESEARCHER", "HARNESS"}:
        if actor.facility_id and req.facility_id and actor.facility_id != req.facility_id:
            raise ClinovaAPIError(
                category="AUTHORIZATION_ERROR",
                message=f"Cannot inject telemetry signal for out-of-scope facility '{req.facility_id}'.",
                status_code=403,
            )

    ev = signal_engine.record_event(
        facility_id=req.facility_id,
        syndrome_tag=req.syndrome_tag,
        acuity_tier=req.acuity_tier,
    )
    return {
        "status": "EVENT_INJECTED",
        "event": ev,
        "current_clusters": signal_engine.get_syndromic_clusters()["clusters"],
    }


@router.get("/outcomes", tags=["SignalGraph"])
async def get_outcome_telemetry(
    facility_id: Optional[str] = None,
    window_hours: int = 48,
):
    """
    Returns aggregated de-identified outcome telemetry across facilities.
    Strictly zero PHI. Preserves unknown status without false optimism.
    """
    return signal_engine.get_outcome_metrics(facility_id=facility_id, window_hours=window_hours)

