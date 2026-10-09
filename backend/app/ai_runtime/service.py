"""CLINOVA AI — Local AI Runtime Orchestration Service.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Orchestrates the canonical fail-safe pipeline:
EVIDENCE CONTEXT -> DEFENSIVE DELIMITING -> LOCAL SLM INFERENCE ->
FAIL-CLOSED VALIDATION -> PROVENANCE BINDING -> UNCERTAINTY ISOLATION.
"""

from typing import Dict, Any, List, Optional, Set, Type
from datetime import datetime, timezone
from pydantic import BaseModel
from app.ai_runtime.models import (
    RuntimeConfig,
    ValidationStatus,
    EvidenceReference,
)
from app.ai_runtime.adapters.base import RuntimeAdapter
from app.ai_runtime.adapters.mock_adapter import MockDeterministicAdapter
from app.ai_runtime.validation.sanitizer import InputSanitizer
from app.ai_runtime.validation.output_validator import OutputValidator
from app.ai_runtime.prompts.templates import PROMPT_REGISTRY, PromptMetadata
from app.ai_runtime.schemas.contracts import (
    ExtractionResult,
    ExtractionPayload,
    SummaryResult,
    SummaryPayload,
    QuestionResult,
    QuestionPayload,
    TranslationResult,
    TranslationPayload,
    NormalizationResult,
    NormalizationPayload,
    DraftNoteResult,
    DraftNotePayload,
    AdvisoryResult,
    AdvisoryPayload,
)
from app.ai_runtime.cache import AICache


class AIRuntimeService:
    """Safe, isolated local AI runtime coordinator."""

    def __init__(self, runtime_adapter: Optional[RuntimeAdapter] = None):
        self.runtime = runtime_adapter or MockDeterministicAdapter()
        self.cache = AICache()

    async def execute_task(
        self,
        case_id: str,
        task_prompt_id: str,
        evidence_items: List[Dict[str, Any]],
        target_schema: Type[BaseModel],
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Executes the canonical, fail-safe AI inference pipeline."""
        prompt_meta: PromptMetadata = PROMPT_REGISTRY.get(task_prompt_id)
        if not prompt_meta:
            raise ValueError(f"Unknown prompt template ID: {task_prompt_id}")

        model_info = await self.runtime.get_model_info()
        allowed_evidence_ids: Set[str] = {str(item.get("id", "")) for item in evidence_items if item.get("id")}

        # 1. Compute Source Evidence Fingerprint
        source_fingerprint = self.cache.compute_source_fingerprint(evidence_items)

        # 2. Cache Check
        if use_cache:
            cached = self.cache.get(
                case_id=case_id,
                task_name=task_prompt_id,
                prompt_version=prompt_meta.version,
                model_id=model_info.model_id,
                model_version=model_info.version,
                current_source_fingerprint=source_fingerprint,
            )
            if cached:
                cached_copy = dict(cached)
                cached_copy["status"] = "SUCCESS_CACHED"
                return cached_copy

        # 3. Assemble Grounded & Sanitized Context Pack
        context_blocks: List[str] = []
        for item in evidence_items:
            ev_id = str(item.get("id", "unknown_evidence"))
            raw_text = str(item.get("text", ""))
            sanitized = InputSanitizer.sanitize(raw_text, source_id=ev_id)
            context_blocks.append(sanitized.delimited_block)

        user_content = (
            f"CASE ID: {case_id}\n\n"
            f"AVAILABLE EVIDENCE ITEMS ({len(evidence_items)}):\n"
            + "\n\n".join(context_blocks)
            + f"\n\nParse the evidence above strictly into valid JSON matching {prompt_meta.task_type} schema."
        )

        # 4. Invoke Local Inference Runtime (Fail-Safe Boundary)
        raw_completion: str = ""
        try:
            raw_completion = await self.runtime.invoke_raw(
                system_prompt=prompt_meta.system_text,
                user_prompt=user_content,
                temperature=0.0,
                max_tokens=1024,
                enforce_json=True,
            )
        except TimeoutError as texc:
            return {
                "status": "FALLBACK",
                "validation_state": ValidationStatus.REJECTED_TIMEOUT,
                "errors": [f"AI runtime timed out: {str(texc)}"],
                "model": model_info.model_id,
                "model_version": model_info.version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "payload": {},
                "source_references": [],
                "warnings": ["AI assistant offline or timed out; deterministic care continues."],
            }
        except MemoryError as oom_exc:
            return {
                "status": "FALLBACK",
                "validation_state": ValidationStatus.REJECTED_OOM,
                "errors": [f"Edge RAM exhausted: {str(oom_exc)}"],
                "model": model_info.model_id,
                "model_version": model_info.version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "payload": {},
                "source_references": [],
                "warnings": ["Local memory pressure; falling back to deterministic processing."],
            }
        except Exception as exc:
            err_msg = str(exc)
            val_status = ValidationStatus.REJECTED_MALFORMED
            if any(k in err_msg.lower() or k in err_msg for k in ["MODEL_UNAVAILABLE", "unavailable", "offline", "connection"]):
                val_status = ValidationStatus.REJECTED_UNAVAILABLE

            return {
                "status": "FALLBACK",
                "validation_state": val_status,
                "errors": [f"Runtime execution error: {err_msg}"],
                "model": model_info.model_id,
                "model_version": model_info.version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "payload": {},
                "source_references": [],
                "warnings": ["AI runtime unavailable."],
            }

        # 5. Deterministic Output Validation
        val_result = OutputValidator.validate(
            raw_output=raw_completion,
            target_schema=target_schema,
            allowed_evidence_ids=allowed_evidence_ids,
        )

        if not val_result.is_valid:
            return {
                "status": "REJECTED",
                "validation_state": val_result.status,
                "errors": val_result.errors,
                "model": model_info.model_id,
                "model_version": model_info.version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "payload": val_result.validated_payload or {},
                "source_references": [],
                "warnings": ["AI output failed deterministic safety checks and was rejected."],
            }

        # 6. Build Provenance Record
        final_response = {
            "status": "SUCCESS",
            "model": model_info.model_id,
            "model_version": model_info.version,
            "runtime": "local_qwen_runtime",
            "prompt_id": prompt_meta.prompt_id,
            "prompt_version": prompt_meta.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_references": [
                {"evidence_id": ev_id, "source_type": "NARRATIVE"}
                for ev_id in sorted(list(allowed_evidence_ids))
            ],
            "confidence": 0.85,
            "validation_state": ValidationStatus.VALID,
            "epistemic_state": "AI_INFERRED",
            "payload": val_result.validated_payload,
            "warnings": [],
        }

        # 7. Cache Valid Result
        if use_cache:
            self.cache.set(
                case_id=case_id,
                task_name=task_prompt_id,
                prompt_version=prompt_meta.version,
                model_id=model_info.model_id,
                model_version=model_info.version,
                source_fingerprint=source_fingerprint,
                payload=final_response,
            )

        return final_response
