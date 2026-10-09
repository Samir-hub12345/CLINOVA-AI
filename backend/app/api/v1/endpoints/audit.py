"""CLINOVA AI — Medicolegal Audit Trail Router.

Provides immutable audit log access for clinical governance,
accreditation review, and medicolegal verification (DOC-14).
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models import AuditLog
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import Permission, check_role_permission

router = APIRouter()


@router.get("/logs", tags=["Audit Trail"])
async def get_audit_logs(
    case_id: Optional[str] = None,
    action: Optional[str] = None,
    actor_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Returns immutable medicolegal audit entries."""
    check_role_permission(actor.role, Permission.AUDIT_READ)
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)

    if case_id:
        stmt = stmt.where(AuditLog.entity_id == case_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)

    res = await db.execute(stmt)
    logs = res.scalars().all()

    return {
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "actor_id": log.actor_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
