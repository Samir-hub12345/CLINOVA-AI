"""Case Re-Verification Coordinator for Phase 5 Intelligent Completion (Sub-Phase 5.11).

Executes Phase 4 Clinical Verification Engine on the rebuilt case snapshot,
updating verification telemetry, checking finding resolutions, and scoring review readiness.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.completion import CompletionSession
from app.models.verification import VerificationRun
from app.models.user import User
from app.services.verification import CaseVerificationService


class CaseReverificationCoordinator:
    """Coordinates deterministic reverification of a newly compiled case snapshot."""

    def __init__(self):
        self.verifier = CaseVerificationService()

    async def reverify_case(
        self,
        session: CompletionSession,
        db: AsyncSession,
        actor: Optional[User] = None,
    ) -> VerificationRun:
        """Executes verification for the updated case version and updates session telemetry."""
        verification_run = await self.verifier.verify_case(
            case_id=session.case_id,
            db=db,
            actor=actor,
            force_reverify=True,
            include_ai_checks=True,
        )

        session.latest_verification_run_id = verification_run.id
        session.current_readiness_score = verification_run.review_readiness_score
        await db.flush()

        return verification_run
