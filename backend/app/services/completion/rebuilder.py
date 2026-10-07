"""Case Rebuild Coordinator for Phase 5 Intelligent Completion (Sub-Phase 5.10).

Executes Phase 3 Canonical Case Builder following answer evidence creation,
generating new immutable case snapshots and updating case version state.
"""

from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.canonical_case import CaseSnapshot, CaseBuildRun
from app.models.completion import CompletionSession
from app.services.case_builder import CaseBuilderService


class CaseRebuildCoordinator:
    """Coordinates canonical case recompilation upon receiving new interview evidence."""

    def __init__(self):
        self.builder = CaseBuilderService()

    async def rebuild_case(
        self,
        session: CompletionSession,
        db: AsyncSession,
    ) -> Tuple[CaseSnapshot, CaseBuildRun]:
        """Rebuilds the canonical case snapshot incorporating newly captured evidence."""
        snapshot, build_run = await self.builder.build_canonical_case(
            case_id=session.case_id,
            db=db,
            trigger_type="intelligent_completion_answer",
            force_rebuild=True,
        )

        session.case_version_current = snapshot.case_version
        await db.flush()

        return snapshot, build_run
