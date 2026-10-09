"""CLINOVA AI — Translation & Multilingual API Endpoints.

Grounded in Phase 21 Sections 36, 38, 39, 40, 62.
Provides:
- POST /api/v1/translation/translate (Stateless or case-scoped translation)
- POST /api/v1/translation/cases/{case_id}/translations (Case entity translation)
- GET  /api/v1/translation/cases/{case_id}/translations (List translations for a case)
- POST /api/v1/translation/cases/{case_id}/translations/{translation_id}/verify (Clinician verification)
- POST /api/v1/translation/cases/{case_id}/translations/{translation_id}/correct (Clinician correction)
"""

import uuid
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_actor, ActorContext
from app.core.policy import authorize_case_access
from app.core.rbac import check_role_permission, Permission
from app.db.models import Case, TranslationRecord
from app.db.session import get_db
from app.domain.translation.provider import get_translation_provider
from app.domain.translation.registry import validate_language_pair, UnsupportedLanguageError
from app.domain.translation.safety import validate_translation_safety
from app.domain.translation.service import (
    get_or_create_translation,
    verify_translation as domain_verify_translation,
    correct_translation as domain_correct_translation,
)

router = APIRouter(tags=["Translation"])

MAX_TRANSLATION_CHARS = 5000

class TranslateRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TRANSLATION_CHARS)
    source_lang: str
    target_lang: str
    case_id: Optional[str] = None
    entity_type: str = "Standalone"
    entity_id: str = "None"

class TranslateResponse(BaseModel):
    translation_id: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    status: str
    provider: str
    model_version: str

class VerifyRequest(BaseModel):
    is_correct: bool
    comments: Optional[str] = None

class CorrectRequest(BaseModel):
    corrected_text: str
    comments: Optional[str] = None

class TranslationDetailResponse(BaseModel):
    id: str
    case_id: str
    entity_type: str
    entity_id: str
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    translation_status: str
    review_status: str
    provider: str
    model_version: str
    is_active: bool
    corrected_text: Optional[str] = None

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(
    req: TranslateRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Translates arbitrary text or creates translation record for a case entity."""
    check_role_permission(actor.role, Permission.CASE_READ)

    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Cannot translate empty text.")

    if len(req.text) > MAX_TRANSLATION_CHARS:
        raise HTTPException(status_code=400, detail=f"Text exceeds limit of {MAX_TRANSLATION_CHARS} characters.")

    try:
        validate_language_pair(req.source_lang, req.target_lang)
    except UnsupportedLanguageError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Patient privacy protection: Patients cannot translate clinician-only notes
    if actor.role == "PATIENT" and req.entity_type in ["CLINICIAN_NOTE", "DoctorNote", "InternalNote"]:
        raise HTTPException(status_code=403, detail="Patients are not authorized to translate clinician-only notes.")

    if req.case_id:
        case = await db.get(Case, req.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found.")
        await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    # Stateless translation when no case_id is associated
    if not req.case_id:
        provider = get_translation_provider()
        res = await provider.translate(req.text, req.source_lang, req.target_lang)
        safety = validate_translation_safety(req.text, req.source_lang, res["translated_text"], req.target_lang)
        
        status = "COMPLETE"
        if not safety["is_safe"]:
            status = "REQUIRES_REVIEW"
        elif safety["requires_review"] or res.get("confidence", 1.0) < 0.7:
            status = "LOW_CONFIDENCE"

        return TranslateResponse(
            translation_id=str(uuid.uuid4()),
            original_text=req.text,
            translated_text=res["translated_text"],
            source_lang=req.source_lang,
            target_lang=req.target_lang,
            status=status,
            provider=res.get("provider", provider.__class__.__name__),
            model_version=res.get("model_version", "v1.local"),
        )

    # Case-associated translation
    record = await get_or_create_translation(
        db=db,
        case_id=req.case_id,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        text=req.text,
        source_lang=req.source_lang,
        target_lang=req.target_lang,
        actor_id=actor.actor_id,
        actor_role=actor.role,
    )
    await db.commit()

    return TranslateResponse(
        translation_id=record.id,
        original_text=record.source_text,
        translated_text=record.translated_text,
        source_lang=record.source_language,
        target_lang=record.target_language,
        status=record.translation_status,
        provider=record.provider,
        model_version=record.model_version,
    )

@router.post("/cases/{case_id}/translations", response_model=TranslateResponse)
async def translate_case_entity(
    case_id: str,
    req: TranslateRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Creates or retrieves a case entity translation with full audit and access control."""
    check_role_permission(actor.role, Permission.CASE_READ)

    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Cannot translate empty text.")

    if len(req.text) > MAX_TRANSLATION_CHARS:
        raise HTTPException(status_code=400, detail=f"Text exceeds limit of {MAX_TRANSLATION_CHARS} characters.")

    try:
        validate_language_pair(req.source_lang, req.target_lang)
    except UnsupportedLanguageError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if actor.role == "PATIENT" and req.entity_type in ["CLINICIAN_NOTE", "DoctorNote", "InternalNote"]:
        raise HTTPException(status_code=403, detail="Patients are not authorized to translate clinician-only notes.")

    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    req.case_id = case_id
    record = await get_or_create_translation(
        db=db,
        case_id=case_id,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        text=req.text,
        source_lang=req.source_lang,
        target_lang=req.target_lang,
        actor_id=actor.actor_id,
        actor_role=actor.role,
    )
    await db.commit()

    return TranslateResponse(
        translation_id=record.id,
        original_text=record.source_text,
        translated_text=record.translated_text,
        source_lang=record.source_language,
        target_lang=record.target_language,
        status=record.translation_status,
        provider=record.provider,
        model_version=record.model_version,
    )

@router.get("/cases/{case_id}/translations", response_model=List[TranslationDetailResponse])
async def get_case_translations(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Retrieves all translation records for a case, enforcing patient privacy."""
    check_role_permission(actor.role, Permission.CASE_READ)
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    await authorize_case_access(case, actor, required_permission=Permission.CASE_READ, db=db)

    stmt = select(TranslationRecord).where(TranslationRecord.case_id == case_id)
    res = await db.execute(stmt)
    records = res.scalars().all()

    # Filter out clinician-only notes if caller is a patient
    if actor.role == "PATIENT":
        records = [r for r in records if r.entity_type not in ["CLINICIAN_NOTE", "DoctorNote", "InternalNote"]]

    return [
        TranslationDetailResponse(
            id=r.id,
            case_id=r.case_id,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            source_language=r.source_language,
            target_language=r.target_language,
            source_text=r.source_text,
            translated_text=r.translated_text,
            translation_status=r.translation_status,
            review_status=r.review_status,
            provider=r.provider,
            model_version=r.model_version,
            is_active=r.is_active,
            corrected_text=r.corrected_text,
        )
        for r in records
    ]

@router.post("/cases/{case_id}/translations/{translation_id}/verify")
async def verify_translation(
    case_id: str,
    translation_id: str,
    req: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Clinician verification of translation accuracy."""
    check_role_permission(actor.role, Permission.REVIEW_ACTION_EXECUTE)

    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    try:
        record = await domain_verify_translation(
            db=db,
            translation_id=translation_id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            is_correct=req.is_correct,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": record.review_status, "translation_id": record.id}

@router.post("/cases/{case_id}/translations/{translation_id}/correct")
async def correct_translation(
    case_id: str,
    translation_id: str,
    req: CorrectRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Clinician correction of translation. Preserves history and source text."""
    check_role_permission(actor.role, Permission.REVIEW_ACTION_EXECUTE)

    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    await authorize_case_access(case, actor, required_permission=Permission.REVIEW_ACTION_EXECUTE, db=db)

    try:
        record = await domain_correct_translation(
            db=db,
            translation_id=translation_id,
            corrected_text=req.corrected_text,
            actor_id=actor.actor_id,
            actor_role=actor.role,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "status": record.review_status,
        "translation_id": record.id,
        "corrected_text": record.corrected_text,
    }
