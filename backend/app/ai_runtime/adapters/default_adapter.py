"""CLINOVA AI — Default High-Level AI Adapter Implementation.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Provides the canonical concrete implementation of AIAdapter, bridging
domain service requests to the underlying RuntimeAdapter while preserving
epistemic boundaries, structured schemas, and input sanitization.
"""

import json
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel
from app.ai_runtime.adapters.base import AIAdapter, RuntimeAdapter
from app.ai_runtime.prompts.templates import (
    PROMPT_EXTRACTION_V1,
    PROMPT_SUMMARY_V1,
    PROMPT_FOLLOWUP_V1,
    PROMPT_TRANSLATION_V1,
    PROMPT_NORMALIZATION_V1,
    PROMPT_TRIAGE_DRAFT_V1,
    PROMPT_ADVISORY_V1,
)
from app.ai_runtime.schemas.contracts import (
    ExtractionPayload,
    SummaryPayload,
    QuestionPayload,
    TranslationPayload,
    NormalizationPayload,
    DraftNotePayload,
    AdvisoryPayload,
)
from app.ai_runtime.validation.sanitizer import InputSanitizer


class DefaultAIAdapter(AIAdapter):
    """Canonical implementation of high-level AIAdapter for CLINOVA domain services."""

    def __init__(self, runtime: RuntimeAdapter):
        super().__init__(runtime)

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        target_schema: Type[BaseModel],
        **kwargs,
    ) -> BaseModel:
        """Executes structured generation and validates result against schema."""
        raw_output = await self.runtime.invoke_raw(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            enforce_json=True,
            **kwargs,
        )
        data = json.loads(raw_output)
        return target_schema.model_validate(data)

    async def extract_entities(self, narrative_text: str, source_evidence_id: str) -> BaseModel:
        """Extracts clinical entities (symptoms, vitals) from narrative."""
        sanitized = InputSanitizer.sanitize(narrative_text, source_id=source_evidence_id)
        user_prompt = f"EVIDENCE ITEM:\n{sanitized.delimited_block}"
        return await self.generate_structured(
            system_prompt=PROMPT_EXTRACTION_V1.system_text,
            user_prompt=user_prompt,
            target_schema=ExtractionPayload,
        )

    async def summarize(self, case_narratives: Dict[str, str]) -> BaseModel:
        """Synthesizes clinical timeline while preserving epistemic uncertainty."""
        blocks = []
        for ev_id, text in case_narratives.items():
            sanitized = InputSanitizer.sanitize(text, source_id=ev_id)
            blocks.append(sanitized.delimited_block)
        user_prompt = "CASE NARRATIVES:\n" + "\n\n".join(blocks)
        return await self.generate_structured(
            system_prompt=PROMPT_SUMMARY_V1.system_text,
            user_prompt=user_prompt,
            target_schema=SummaryPayload,
        )

    async def translate(self, source_text: str, source_lang: str, target_lang: str) -> BaseModel:
        """Translates vernacular text while preserving regional clinical terminology."""
        sanitized = InputSanitizer.sanitize(source_text, source_id="translation_input")
        user_prompt = (
            f"SOURCE LANGUAGE: {source_lang}\n"
            f"TARGET LANGUAGE: {target_lang}\n"
            f"TEXT TO TRANSLATE:\n{sanitized.delimited_block}"
        )
        return await self.generate_structured(
            system_prompt=PROMPT_TRANSLATION_V1.system_text,
            user_prompt=user_prompt,
            target_schema=TranslationPayload,
        )

    async def generate_questions(self, identified_gaps: List[str]) -> BaseModel:
        """Generates targeted Next-Best-Inquiry questions."""
        gaps_text = "\n".join(f"- {gap}" for gap in identified_gaps)
        user_prompt = f"IDENTIFIED INFORMATION GAPS:\n{gaps_text}"
        return await self.generate_structured(
            system_prompt=PROMPT_FOLLOWUP_V1.system_text,
            user_prompt=user_prompt,
            target_schema=QuestionPayload,
        )
