"""CLINOVA AI — Application AI Endpoints.

Phase 18: AI Application Integration.
Provides authenticated, role-governed endpoints for clinical AI advisory tasks.
Enforces:
1. DOC-03 Role & Permission checks (Patient restricted, Auditor read-only).
2. Deterministic facility-scope authorization per case.
3. Strict prohibition of autonomous actions (prescribing, admitting, discharging, procedure authorization).
4. Advisory-only contract with explicit provenance and non-binding disclaimers.
5. Medicolegal audit event recording for every inference.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.auth import (
    get_current_actor,
    ActorContext,
    ROLE_CLINICIAN,
    ROLE_DOCTOR,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
)
from app.core.errors import ClinovaAPIError
from app.core.rbac import PROHIBITED_CLINICAL_ACTIONS
from app.ai.orchestrator import AIApplicationOrchestrator
from app.ai.tasks import (
    TASK_CATALOG,
    TASK_CASE_SUMMARY,
    TASK_TIMELINE_SUMMARY,
    TASK_MISSING_INFORMATION,
    TASK_FOLLOWUP_QUESTIONS,
    TASK_TRIAGE_NOTE_DRAFT,
)

router = APIRouter(tags=["AI Application"])


class RunTaskRequest(BaseModel):
    task_id: str = Field(..., description="Task identifier from catalog")
    force_regenerate: bool = Field(default=False, description="Bypass cache and force regeneration")
    use_cache: bool = Field(default=True, description="Allow cached results if fresh")
    action: Optional[str] = Field(None, description="Client action (Prohibited clinical actions rejected)")


def check_prohibited_action(action: Optional[str]):
    """Strictly rejects autonomous clinical actions passed in API payloads."""
    if not action:
        return
    norm = action.strip().upper()
    if any(p in norm for p in ["PRESCRIBE", "ADMIT", "DISCHARGE", "AUTHORIZE_PROCEDURE", "PROCEDURE", "DIAGNOSE"]):
        raise ClinovaAPIError(
            code="PROHIBITED_CLINICAL_ACTION",
            message=f"Autonomous action '{action}' is strictly prohibited. AI cannot prescribe, admit, discharge, or authorize procedures.",
            status_code=403,
        )


@router.get("/tasks")
async def list_available_tasks(
    actor: ActorContext = Depends(get_current_actor),
):
    """Lists registered application AI advisory tasks."""
    return [
        {
            "task_id": t.task_id,
            "version": t.task_version,
            "prompt_id": t.prompt_id,
            "description": t.description,
            "allowed_roles": t.allowed_roles,
            "is_advisory_only": t.is_advisory_only,
        }
        for t in TASK_CATALOG.values()
    ]


@router.get("/cases/{case_id}/results")
async def get_case_ai_results(
    case_id: str = Path(..., description="Master Case UUID"),
    task_id: Optional[str] = Query(None, description="Optional task filter"),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Retrieves persisted AI advisory results for a case with real-time staleness tracking."""
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients are not permitted to access internal clinical AI advisory results.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.list_case_results(case_id=case_id, actor=actor, task_id=task_id)


@router.post("/cases/{case_id}/summary")
async def generate_case_summary(
    case_id: str = Path(...),
    force_regenerate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Generates or retrieves evidence-grounded AI case summary."""
    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot access internal clinical AI summaries.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=TASK_CASE_SUMMARY,
        actor=actor,
        force_regenerate=force_regenerate,
        correlation_id=x_correlation_id,
    )


@router.post("/cases/{case_id}/timeline-summary")
async def generate_timeline_summary(
    case_id: str = Path(...),
    force_regenerate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Generates or retrieves chronological timeline summary."""
    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot access internal clinical AI summaries.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=TASK_TIMELINE_SUMMARY,
        actor=actor,
        force_regenerate=force_regenerate,
        correlation_id=x_correlation_id,
    )


@router.post("/cases/{case_id}/missing-information")
async def analyze_missing_information(
    case_id: str = Path(...),
    force_regenerate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Analyzes missing clinical parameters and flags clinical gaps."""
    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot access internal clinical AI summaries.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=TASK_MISSING_INFORMATION,
        actor=actor,
        force_regenerate=force_regenerate,
        correlation_id=x_correlation_id,
    )


@router.post("/cases/{case_id}/follow-up-questions")
async def draft_follow_up_questions(
    case_id: str = Path(...),
    force_regenerate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Drafts targeted clarification questions grounded in clinical gaps."""
    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot access internal clinical AI summaries.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=TASK_FOLLOWUP_QUESTIONS,
        actor=actor,
        force_regenerate=force_regenerate,
        correlation_id=x_correlation_id,
    )


@router.post("/cases/{case_id}/triage-note")
async def draft_triage_note(
    case_id: str = Path(...),
    force_regenerate: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Drafts structured triage note for clinician review (marked is_ai_generated=True)."""
    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot access internal clinical AI summaries.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=TASK_TRIAGE_NOTE_DRAFT,
        actor=actor,
        force_regenerate=force_regenerate,
        correlation_id=x_correlation_id,
    )


@router.post("/cases/{case_id}/tasks/run")
async def run_ai_task(
    case_id: str = Path(...),
    request: RunTaskRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
    x_correlation_id: Optional[str] = Header(None),
):
    """Generic endpoint to execute any approved AI task from the catalog."""
    check_prohibited_action(request.action)

    if actor.role == ROLE_AUDITOR:
        raise ClinovaAPIError(
            code="FORBIDDEN_AUDITOR_MUTATION",
            message="Auditors have read-only permissions and cannot trigger AI generations.",
            status_code=403,
        )
    if actor.role == ROLE_PATIENT:
        raise ClinovaAPIError(
            code="FORBIDDEN_PATIENT_ACCESS",
            message="Patients cannot execute clinical AI tasks.",
            status_code=403,
        )

    orchestrator = AIApplicationOrchestrator(db=db)
    return await orchestrator.run_task(
        case_id=case_id,
        task_id=request.task_id,
        actor=actor,
        force_regenerate=request.force_regenerate,
        use_cache=request.use_cache,
        correlation_id=x_correlation_id,
    )
