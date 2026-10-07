"""CLINOVA AI — API v1 Master Router.

Continuous Care Intelligence System.
Mounts all four innovation pillars and BPUT baseline routers:
- Multimodal Intake (/intake)
- Clinical Queue & Case Management (/cases)
- CareGraph Workstation (/caregraph)
- FacilityGraph & Care Feasibility (/facilities)
- Clinical Referrals & SBAR (/referrals)
- SignalGraph Operational Telemetry (/signalgraph)
- Orchestration Cognitive Synthesis (/orchestration)
- Medicolegal Audit Trail (/audit)
- Authentication & Clinical Personas (/auth)
"""

from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.intake import router as intake_router
from app.api.v1.endpoints.cases import router as cases_router
from app.api.v1.endpoints.caregraph import router as caregraph_router
from app.api.v1.endpoints.facilities import router as facilities_router
from app.api.v1.endpoints.referrals import router as referrals_router
from app.api.v1.endpoints.signalgraph import router as signalgraph_router
from app.api.v1.endpoints.orchestration import router as orchestration_router
from app.api.v1.endpoints.audit import router as audit_router

api_router = APIRouter()


@api_router.get("/status", tags=["System"])
async def get_system_status():
    """Returns the operational status of Clinova AI core subsystems."""
    return {
        "status": "operational",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "mode": {
            "demo_mode": settings.DEMO_MODE,
            "offline_mode": settings.OFFLINE_MODE,
            "synthetic_data_only": settings.SYNTHETIC_DATA_ONLY,
        },
        "pillars": {
            "caregraph": "active",
            "facilitygraph": "active",
            "signalgraph": "active",
            "orchestration_engine": "active",
            "bput_baseline": "active",
        },
    }


@api_router.get("/safety", tags=["Clinical Safety"])
async def get_clinical_safety_policy():
    """Returns the non-diagnostic mandate and human-in-the-loop governance policies."""
    return {
        "non_diagnostic_mandate": True,
        "role": "Clinical Decision Support & Care Intelligence",
        "human_in_the_loop_required": True,
        "autonomous_action_allowed": False,
        "disclaimer": (
            "CLINOVA AI is a clinical decision-support and care intelligence system. "
            "It does NOT diagnose, prescribe treatment, or operate autonomously. "
            "All recommendations require qualified clinician verification before action."
        ),
        "data_governance": {
            "anonymization_enforced": settings.ANONYMIZATION_ENABLED,
            "audit_logging": settings.AUDIT_LOGGING_ENABLED,
            "retention_hours": settings.DATA_RETENTION_HOURS,
            "synthetic_data_guarantee": settings.SYNTHETIC_DATA_ONLY,
        },
    }


# Mount subrouters
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(intake_router, prefix="/intake")
api_router.include_router(cases_router, prefix="/cases")
api_router.include_router(caregraph_router, prefix="/caregraph")
api_router.include_router(facilities_router, prefix="/facilities")
api_router.include_router(referrals_router, prefix="/referrals")
api_router.include_router(signalgraph_router, prefix="/signalgraph")
api_router.include_router(orchestration_router, prefix="/orchestration")
api_router.include_router(audit_router, prefix="/audit")
