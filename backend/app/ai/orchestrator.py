"""CLINOVA AI — Application AI Orchestrator.

Phase 18: AI Application Integration.
Orchestrates AI tasks against the Master Case while enforcing:
1. Deterministic Safety Primacy (NEWS2, Shock Index, Red Flags calculated outside LLM).
2. Zero Autonomous Action (No auto-admit, auto-discharge, auto-prescribe, auto-state transition).
3. Grounding & Anti-Hallucination verification against case evidence.
4. Epistemic Isolation (AI content is strictly AI_INFERRED, never auto-verified).
5. Immutable Result Persistence & Fingerprinted Cache Invalidation.
6. Safe Degradation (AI downtime or timeout never blocks human or deterministic workflows).
"""

import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.models import (
    Case,
    Evidence,
    Vital,
    TriageNote,
    AIResultRecord,
    AuditEvent,
    utc_now,
)
from app.core.auth import ActorContext
from app.core.policy import (
    authorize_case_access,
    record_security_audit_event,
)
from app.core.errors import ClinovaAPIError
from app.ai_runtime.service import AIRuntimeService
from app.ai_runtime.models import ValidationStatus
from app.ai_runtime.validation.output_validator import OutputValidator
from app.ai.runtime_factory import build_runtime_service
from app.ai.tasks import (
    TASK_CATALOG,
    TASK_CASE_SUMMARY,
    TASK_TIMELINE_SUMMARY,
    TASK_MISSING_INFORMATION,
    TASK_FOLLOWUP_QUESTIONS,
    TASK_TRIAGE_NOTE_DRAFT,
    AITaskDefinition,
    get_task_definition,
)
from app.ai.context_builder import AIContextBuilder, AIContextPack


class AIApplicationOrchestrator:
    """Safe, isolated coordinator bridging Master Case data to Local AI Runtime."""

    def __init__(self, db: AsyncSession, runtime_service: Optional[AIRuntimeService] = None):
        self.db = db
        self.runtime = runtime_service or build_runtime_service()

    async def run_task(
        self,
        case_id: str,
        task_id: str,
        actor: ActorContext,
        force_regenerate: bool = False,
        use_cache: bool = True,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executes an authorized clinical AI task against the canonical Master Case."""
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # 1. Resolve Task Definition
        task_def = get_task_definition(task_id)
        if not task_def:
            raise ClinovaAPIError(
                code="UNKNOWN_AI_TASK",
                message=f"AI task '{task_id}' is not recognized in the task catalog.",
                status_code=400,
            )

        # 2. Verify Role Authorization for AI Task
        actor_role = getattr(actor, "role", getattr(actor, "actor_role", None))
        if actor_role not in task_def.allowed_roles:
            raise ClinovaAPIError(
                code="FORBIDDEN_AI_TASK_ROLE",
                message=f"Role '{actor_role}' is not authorized to execute task '{task_def.task_id}'.",
                status_code=403,
            )

        # 3. Load Master Case
        stmt = (
            select(Case)
            .options(
                selectinload(Case.evidence_items),
                selectinload(Case.vitals_list),
                selectinload(Case.timeline),
                selectinload(Case.triage_notes),
            )
            .where(Case.id == case_id)
        )
        res = await self.db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise ClinovaAPIError(
                code="CASE_NOT_FOUND",
                message=f"Master Case '{case_id}' does not exist.",
                status_code=404,
            )

        # 4. Authorize Case Access (Facility Scope Enforcement)
        await authorize_case_access(case, actor, db=self.db, correlation_id=correlation_id)

        # 5. Build Controlled, Sanitized AI Context Pack
        context_pack: AIContextPack = await AIContextBuilder.build(case, self.db)

        # 6. Check Cache and Existing Persisted Results
        if not force_regenerate and use_cache:
            existing_stmt = (
                select(AIResultRecord)
                .where(
                    AIResultRecord.case_id == case.id,
                    AIResultRecord.task_id == task_def.task_id,
                    AIResultRecord.status.in_(["SUCCESS", "SUCCESS_CACHED"]),
                    AIResultRecord.is_stale.is_(False),
                )
                .order_by(desc(AIResultRecord.created_at))
            )
            existing_res = await self.db.execute(existing_stmt)
            existing_record = existing_res.scalars().first()

            if existing_record:
                if existing_record.context_fingerprint == context_pack.context_fingerprint:
                    # Return cached result with explicit status
                    return self._format_result_response(
                        record=existing_record,
                        is_cached=True,
                        is_stale=False,
                        deterministic_context=context_pack.deterministic_safety_context,
                        correlation_id=correlation_id,
                    )
                else:
                    # Mark existing record as stale since context fingerprint has drifted
                    existing_record.is_stale = True
                    await self.db.flush()

        # 7. Execute Task via Local AI Runtime Service
        runtime_raw_res: Dict[str, Any] = {}
        try:
            runtime_raw_res = await self.runtime.execute_task(
                case_id=case.id,
                task_prompt_id=task_def.prompt_id,
                evidence_items=context_pack.evidence_items_for_runtime,
                target_schema=task_def.target_schema,
                use_cache=(use_cache and not force_regenerate),
            )
        except Exception as exc:
            # Safe Fallback Degradation (Runtime Failure Never Blocks Patient Workflow)
            runtime_raw_res = {
                "status": "FALLBACK",
                "validation_state": ValidationStatus.REJECTED_UNAVAILABLE,
                "errors": [f"AI runtime failure: {str(exc)}"],
                "model": "qwen3-4b-instruct",
                "model_version": "1.0.0",
                "payload": {},
                "source_references": [],
                "warnings": ["AI assistant offline; deterministic care continues."],
            }

        # 8. Post-Execution Safety & Grounding Validation
        status = runtime_raw_res.get("status", "SUCCESS")
        val_state = runtime_raw_res.get("validation_state", ValidationStatus.VALID)
        payload = runtime_raw_res.get("payload", {})
        errors = list(runtime_raw_res.get("errors", []))
        warnings = list(runtime_raw_res.get("warnings", []))

        # Check for adversarial or forbidden clinical actions in payload
        if payload and status == "SUCCESS":
            forbidden_actions = OutputValidator.check_forbidden_clinical_actions(payload)
            if forbidden_actions:
                status = "REJECTED"
                val_state = ValidationStatus.REJECTED_FORBIDDEN_ACTION
                errors.extend(forbidden_actions)

            grounding_errs = OutputValidator.check_grounding_references(
                payload, context_pack.allowed_evidence_ids
            )
            if grounding_errs:
                status = "REJECTED"
                val_state = ValidationStatus.REJECTED_UNGROUNDED
                errors.extend(grounding_errs)

        # 9. Persist AI Result Record to Canonical Case
        ai_record = AIResultRecord(
            id=str(uuid.uuid4()),
            case_id=case.id,
            task_id=task_def.task_id,
            task_version=task_def.task_version,
            model_id=runtime_raw_res.get("model", "qwen3-4b-instruct"),
            model_version=runtime_raw_res.get("model_version", "1.0.0"),
            prompt_id=task_def.prompt_id,
            prompt_version=task_def.prompt_version,
            status=status,
            validation_state=val_state.value if hasattr(val_state, "value") else str(val_state),
            epistemic_state="AI_INFERRED",  # Absolute rule: Never VERIFIED
            is_stale=False,
            context_fingerprint=context_pack.context_fingerprint,
            case_version=case.state_version,
            source_evidence_references=runtime_raw_res.get("source_references", []),
            payload=payload,
            errors=errors,
            warnings=warnings,
            confidence=runtime_raw_res.get("confidence", 0.85 if status == "SUCCESS" else None),
            generated_at=utc_now(),
        )
        self.db.add(ai_record)

        # 10. Task-Specific Integrations
        # For Triage Note Draft: Create AI draft triage note in database if valid
        if task_def.task_id == TASK_TRIAGE_NOTE_DRAFT and status == "SUCCESS":
            draft_note = TriageNote(
                id=str(uuid.uuid4()),
                case_id=case.id,
                author_id="ai-system-qwen",
                author_role="AI_ADVISORY",
                author_type="AI_ADVISORY",
                summary=(
                    f"Subjective: {payload.get('subjective_draft', '')}\n\n"
                    f"Objective: {payload.get('objective_observations_draft', '')}"
                ),
                acuity_assessment="ADVISORY_PENDING_REVIEW",
                clinical_concerns=payload.get("clinical_concerns", []),
                suggested_next_steps=payload.get("suggested_next_steps", []),
                is_ai_generated=True,
                created_at=utc_now(),
            )
            self.db.add(draft_note)

        # 11. Record Medicolegal Audit Event
        audit_event = AuditEvent(
            case_id=case.id,
            actor_id=actor.actor_id,
            actor_role=actor_role or "UNKNOWN",
            action=f"AI_TASK_EXECUTED:{task_def.task_id}",
            object_type="AI_RESULT",
            object_id=ai_record.id,
            result="SUCCESS" if status in ("SUCCESS", "SUCCESS_CACHED") else "FAILURE",
            correlation_id=correlation_id,
            details={
                "task_id": task_def.task_id,
                "model_id": ai_record.model_id,
                "prompt_id": task_def.prompt_id,
                "status": status,
                "validation_state": val_state.value if hasattr(val_state, "value") else str(val_state),
                "context_fingerprint": context_pack.context_fingerprint,
                "is_suspicious_input": context_pack.is_suspicious_input,
                "detected_injections": context_pack.detected_injections,
            },
        )
        self.db.add(audit_event)
        await self.db.commit()

        # 12. Return Formatted Advisory Response
        return self._format_result_response(
            record=ai_record,
            is_cached=False,
            is_stale=False,
            deterministic_context=context_pack.deterministic_safety_context,
            correlation_id=correlation_id,
        )

    async def list_case_results(
        self,
        case_id: str,
        actor: ActorContext,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lists historical and active AI advisory results for a Master Case."""
        case = await self.db.get(Case, case_id)
        if not case:
            raise ClinovaAPIError(
                code="CASE_NOT_FOUND",
                message=f"Master Case '{case_id}' does not exist.",
                status_code=404,
            )

        # Facility Scope Check
        await authorize_case_access(case, actor, db=self.db)

        # Build current context pack to evaluate live staleness
        context_pack = await AIContextBuilder.build(case, self.db)

        query = (
            select(AIResultRecord)
            .where(AIResultRecord.case_id == case.id)
            .order_by(desc(AIResultRecord.created_at))
        )
        if task_id:
            canonical_task = get_task_definition(task_id)
            target_id = canonical_task.task_id if canonical_task else task_id
            query = query.where(AIResultRecord.task_id == target_id)

        res = await self.db.execute(query)
        records = res.scalars().all()

        formatted_results = []
        for rec in records:
            is_stale = rec.is_stale or (rec.context_fingerprint != context_pack.context_fingerprint)
            formatted_results.append(
                self._format_result_response(
                    record=rec,
                    is_cached=False,
                    is_stale=is_stale,
                    deterministic_context=context_pack.deterministic_safety_context,
                )
            )

        return formatted_results

    def _format_result_response(
        self,
        record: AIResultRecord,
        is_cached: bool,
        is_stale: bool,
        deterministic_context: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Formats an AI result response with mandatory advisory disclaimers and safety boundaries."""
        return {
            "id": record.id,
            "case_id": record.case_id,
            "task_id": record.task_id,
            "task_version": record.task_version,
            "model_id": record.model_id,
            "model_version": record.model_version,
            "prompt_id": record.prompt_id,
            "prompt_version": record.prompt_version,
            "status": "SUCCESS_CACHED" if is_cached else record.status,
            "validation_state": record.validation_state,
            "epistemic_state": record.epistemic_state,
            "is_stale": is_stale,
            "is_cached": is_cached,
            "is_advisory_only": True,
            "disclaimer": (
                "CLINOVA AI ADVISORY RESULT. Non-diagnostic and non-binding. "
                "Must be verified and signed off by a qualified registered clinician."
            ),
            "generated_at": record.generated_at.isoformat() if record.generated_at else None,
            "context_fingerprint": record.context_fingerprint,
            "case_version": record.case_version,
            "source_evidence_references": record.source_evidence_references or [],
            "payload": record.payload or {},
            "errors": record.errors or [],
            "warnings": record.warnings or [],
            "confidence": record.confidence,
            "deterministic_safety_summary": {
                "acuity_tier": deterministic_context.get("acuity_tier"),
                "priority_tier": deterministic_context.get("priority_tier"),
                "news2_score": deterministic_context.get("news2", {}).get("score"),
                "shock_index": deterministic_context.get("shock_index", {}).get("value"),
                "has_critical_red_flags": deterministic_context.get("has_critical_red_flags", False),
            },
            "correlation_id": correlation_id,
        }
