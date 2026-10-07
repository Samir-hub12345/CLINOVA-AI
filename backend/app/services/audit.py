import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_factory
from app.models.audit import AuditLog
from app.models.user import User

logger = logging.getLogger("clinova.audit")


class AuditService:
    @staticmethod
    async def log_event(
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user: Optional[User] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Optional[AuditLog]:
        """Record an immutable PHI access or system event using an isolated session for HIPAA-ready auditing."""
        try:
            effective_user_id = user.id if user else user_id
            effective_user_email = user.email if user else user_email

            audit_entry = AuditLog(
                user_id=effective_user_id,
                user_email=effective_user_email,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
            )
            if db is not None:
                db.add(audit_entry)
                await db.commit()
            else:
                async with async_session_factory() as session:
                    session.add(audit_entry)
                    await session.commit()
            return audit_entry
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}", exc_info=True)
            return None
