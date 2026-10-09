"""CLINOVA AI — Translation Application Service.

Grounded in Phase 21 Sections 8, 10, 19, 20, 27, 28, 30, 31, 48.
Handles:
- Deterministic SHA-256 fingerprint caching
- Local/mock provider dispatch with timeout resilience
- Semantic safety verification (negation, numbers, uncertainty)
- Provenance tracking (ORIGINAL -> TRANSLATED)
- Historical version retention
- Human clinician review and correction workflow
- Auditable lifecycle events
"""

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TranslationRecord, Case, AuditEvent, utc_now
from app.domain.translation.provider import get_translation_provider, TranslationProvider
from app.domain.translation.safety import validate_translation_safety

TRANSLATION_TIMEOUT_SECONDS = 5.0

def generate_fingerprint(text: str, source_lang: str, target_lang: str, provider: str, model: str) -> str:
    """Computes deterministic SHA-256 fingerprint for translation cache isolation."""
    content = f"{text.strip()}|{source_lang}|{target_lang}|{provider}|{model}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

async def get_or_create_translation(
    db: AsyncSession,
    case_id: str,
    entity_type: str,
    entity_id: str,
    text: str,
    source_lang: str,
    target_lang: str = "en",
    actor_id: str = "SYSTEM",
    actor_role: str = "SYSTEM",
    provider: Optional[TranslationProvider] = None,
) -> TranslationRecord:
    """Translates text for a case entity, checking cache and logging provenance."""
    if not text or not text.strip():
        raise ValueError("Cannot translate empty text")

    active_provider = provider or get_translation_provider()
    provider_name = active_provider.__class__.__name__
    model_version = "v1.mock" if "Mock" in provider_name else "v1.local"

    fingerprint = generate_fingerprint(text, source_lang, target_lang, provider_name, model_version)

    # 1. Deterministic Cache Check
    stmt = select(TranslationRecord).where(
        TranslationRecord.case_id == case_id,
        TranslationRecord.entity_type == entity_type,
        TranslationRecord.entity_id == entity_id,
        TranslationRecord.source_fingerprint == fingerprint,
        TranslationRecord.is_active == True,
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        return existing

    # 2. Execution with Timeout & Graceful Degradation
    try:
        result = await asyncio.wait_for(
            active_provider.translate(text, source_lang, target_lang),
            timeout=TRANSLATION_TIMEOUT_SECONDS,
        )
        translated_text = result["translated_text"]
        confidence = float(result.get("confidence", 1.0))
        provider_returned = result.get("provider", provider_name)
        model_returned = result.get("model_version", model_version)

        # 3. Clinical Semantic Safety Analysis
        safety = validate_translation_safety(text, source_lang, translated_text, target_lang)
        if not safety["is_safe"]:
            status = "REQUIRES_REVIEW"
        elif safety["requires_review"] or confidence < 0.7:
            status = "LOW_CONFIDENCE"
        else:
            status = "COMPLETE"

    except asyncio.TimeoutError:
        status = "FAILED"
        translated_text = text  # Fallback to source text
        provider_returned = provider_name
        model_returned = model_version
    except Exception:
        status = "FAILED"
        translated_text = text  # Fallback to source text
        provider_returned = provider_name
        model_returned = model_version

    # 4. Deactivate previous active records for this entity to preserve version history
    old_stmt = select(TranslationRecord).where(
        TranslationRecord.case_id == case_id,
        TranslationRecord.entity_type == entity_type,
        TranslationRecord.entity_id == entity_id,
        TranslationRecord.is_active == True,
    )
    for old_record in (await db.execute(old_stmt)).scalars().all():
        old_record.is_active = False

    # 5. Persist New Translation Record
    record = TranslationRecord(
        id=str(uuid.uuid4()),
        case_id=case_id,
        entity_type=entity_type,
        entity_id=entity_id,
        source_language=source_lang,
        target_language=target_lang,
        source_text=text,
        translated_text=translated_text,
        translation_status=status,
        provider=provider_returned,
        model_version=model_returned,
        source_fingerprint=fingerprint,
        task_version="1.0.0",
        generated_at=utc_now(),
        is_active=True,
        review_status="PENDING",
    )
    db.add(record)

    # 6. Audit Trail Logging
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="translation_requested",
        object_type="TRANSLATION",
        object_id=record.id,
        result="SUCCESS" if status != "FAILED" else "FAILED",
        details={
            "source_lang": source_lang,
            "target_lang": target_lang,
            "status": status,
            "entity_type": entity_type,
        },
    )
    db.add(audit)

    await db.flush()
    return record

async def verify_translation(
    db: AsyncSession,
    translation_id: str,
    actor_id: str,
    actor_role: str,
    is_correct: bool = True,
) -> TranslationRecord:
    """Explicit clinician review verification. Does not mutate source text."""
    record = await db.get(TranslationRecord, translation_id)
    if not record:
        raise ValueError("Translation not found")

    record.review_status = "VERIFIED" if is_correct else "REJECTED"
    record.reviewed_by = actor_id
    record.reviewed_at = utc_now()

    audit = AuditEvent(
        case_id=record.case_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="translation_verified" if is_correct else "translation_rejected",
        object_type="TRANSLATION",
        object_id=record.id,
        result="SUCCESS",
        details={"translation_id": record.id, "review_status": record.review_status},
    )
    db.add(audit)

    await db.flush()
    return record

async def correct_translation(
    db: AsyncSession,
    translation_id: str,
    corrected_text: str,
    actor_id: str,
    actor_role: str,
) -> TranslationRecord:
    """Clinician edits translation. Preserves original translation in history, leaves source text intact."""
    record = await db.get(TranslationRecord, translation_id)
    if not record:
        raise ValueError("Translation not found")

    record.review_status = "CORRECTED"
    record.reviewed_by = actor_id
    record.reviewed_at = utc_now()
    record.corrected_text = corrected_text
    record.is_active = False

    audit = AuditEvent(
        case_id=record.case_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="translation_corrected",
        object_type="TRANSLATION",
        object_id=record.id,
        result="SUCCESS",
        details={"translation_id": record.id},
    )
    db.add(audit)

    # Spawn new version with clinician-corrected representation
    new_record = TranslationRecord(
        id=str(uuid.uuid4()),
        case_id=record.case_id,
        entity_type=record.entity_type,
        entity_id=record.entity_id,
        source_language=record.source_language,
        target_language=record.target_language,
        source_text=record.source_text,
        translated_text=corrected_text,
        translation_status="COMPLETE",
        provider="HUMAN",
        model_version="manual_correction",
        source_fingerprint=record.source_fingerprint,
        task_version=record.task_version,
        generated_at=utc_now(),
        is_active=True,
        review_status="CORRECTED",
        reviewed_by=actor_id,
        reviewed_at=utc_now(),
        corrected_text=corrected_text,
    )
    db.add(new_record)

    await db.flush()
    return new_record
