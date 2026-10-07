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
async def inject_synthetic_event(req: InjectEventRequest):
    """
    Ingests synthetic clinical encounter signal into the real-time event pipeline.
    Used for automated scenario validation and outbreak simulation.
    """
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
