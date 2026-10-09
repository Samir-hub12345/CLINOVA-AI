from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.core.auth import get_current_actor, ActorContext
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import (
    Case,
    Evidence,
    EvidenceRecord,
    AuditEvent,
    AuditLog,
    TimelineEvent,
    utc_now,
)
from app.baseline.intake.stt_provider import get_stt_provider


router = APIRouter()
stt_provider = get_stt_provider()


class VoiceUploadResponse(BaseModel):
    message: str
    audio_id: str
    filename: str
    size_bytes: int


class TranscribeRequest(BaseModel):
    audio_id: str
    case_id: str
    language: Optional[str] = "en"


class TranscriptResponse(BaseModel):
    transcript_id: str
    case_id: str
    transcript: str
    confidence: float
    provider_metadata: Dict[str, Any]
    status: str
    created_at: str


class TranscriptConfirmRequest(BaseModel):
    transcript: str


ALLOWED_MIME_TYPES = {
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "audio/x-m4a",
    "audio/m4a",
    "audio/mp4",
}


@router.post("/intake/voice", tags=["Voice Intake"])
async def upload_voice(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if "application/json" in request.headers.get("content-type", ""):
        from app.api.v1.endpoints.intake import intake_voice, VoiceIntakeRequest
        data = await request.json()
        req = VoiceIntakeRequest(**data)
        return await intake_voice(req, db)

    # For multipart file upload, actor must be authenticated
    current_user = await get_current_actor(request, db=db)
    form = await request.form()
    file = form.get("file")
    if not file or not hasattr(file, "read"):
        raise HTTPException(status_code=400, detail="Empty audio file")

    if getattr(file, "content_type", None) not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: '{getattr(file, 'content_type', '')}'. Supported: wav, mp3, webm, ogg, m4a.",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    max_size_bytes = 10 * 1024 * 1024  # 10 MB limit
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 10MB.")

    audio_id = str(uuid.uuid4())
    if not hasattr(request.app.state, "audio_storage"):
        request.app.state.audio_storage = {}
    request.app.state.audio_storage[audio_id] = {
        "content": content,
        "filename": getattr(file, "filename", "audio.webm") or "audio.webm",
        "mime_type": getattr(file, "content_type", "audio/webm"),
        "uploaded_by": current_user.actor_id,
        "created_at": utc_now(),
    }

    return VoiceUploadResponse(
        message="Audio uploaded successfully",
        audio_id=audio_id,
        filename=getattr(file, "filename", "audio.webm") or "audio.webm",
        size_bytes=len(content),
    )


@router.post("/intake/voice/transcribe", response_model=TranscriptResponse, tags=["Voice Intake"])
async def transcribe_voice(
    request: Request,
    payload: TranscribeRequest,
    current_user: ActorContext = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    audio_storage = getattr(request.app.state, "audio_storage", {})
    stored_entry = audio_storage.get(payload.audio_id)
    if not stored_entry:
        raise HTTPException(status_code=404, detail="Audio not found or expired")

    audio_data = stored_entry["content"] if isinstance(stored_entry, dict) else stored_entry
    filename = stored_entry.get("filename", "audio.webm") if isinstance(stored_entry, dict) else "audio.webm"

    # Check case exists and access authorization
    stmt = select(Case).where(Case.id == payload.case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if current_user.role == "PATIENT":
        if case.patient_id != current_user.patient_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this case")
    elif not current_user.is_admin():
        if current_user.facility_id and case.facility_id != current_user.facility_id:
            raise HTTPException(status_code=403, detail="Cross-facility access denied")

    # Transcribe audio using STT provider
    try:
        stt_result = stt_provider.transcribe(audio_data, filename, payload.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    transcript = stt_result.get("transcript", "").strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Empty transcription output")

    transcript_id = str(uuid.uuid4())

    if not hasattr(request.app.state, "transcripts"):
        request.app.state.transcripts = {}

    trans = TranscriptResponse(
        transcript_id=transcript_id,
        case_id=payload.case_id,
        transcript=transcript,
        confidence=float(stt_result.get("confidence", 0.0)),
        provider_metadata=stt_result.get("metadata", {}),
        status="READY_FOR_REVIEW",
        created_at=utc_now().isoformat(),
    )
    request.app.state.transcripts[transcript_id] = trans

    # Create audit records
    audit = AuditLog(
        action="VOICE_TRANSCRIPTION_COMPLETED",
        actor_id=current_user.actor_id,
        entity_type="CASE",
        entity_id=payload.case_id,
        details={
            "transcript_id": transcript_id,
            "provider": stt_result.get("metadata", {}).get("provider"),
            "actor_role": current_user.role,
        },
        timestamp=utc_now(),
    )
    db.add(audit)

    audit_event = AuditEvent(
        case_id=payload.case_id,
        actor_id=current_user.actor_id,
        actor_role=current_user.role,
        action="voice.transcription.completed",
        object_type="CASE",
        object_id=payload.case_id,
        result="SUCCESS",
        details={
            "transcript_id": transcript_id,
            "provider": stt_result.get("metadata", {}).get("provider"),
        },
        created_at=utc_now(),
    )
    db.add(audit_event)

    await db.commit()

    return trans


@router.get("/cases/{case_id}/transcripts", response_model=List[TranscriptResponse], tags=["Voice Intake"])
async def get_transcripts(
    case_id: str,
    request: Request,
    current_user: ActorContext = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if current_user.role == "PATIENT":
        if case.patient_id != current_user.patient_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this case")
    elif not current_user.is_admin():
        if current_user.facility_id and case.facility_id != current_user.facility_id:
            raise HTTPException(status_code=403, detail="Cross-facility access denied")

    transcripts = getattr(request.app.state, "transcripts", {})
    case_transcripts = [t for t in transcripts.values() if t.case_id == case_id]
    return case_transcripts


@router.post("/cases/{case_id}/transcripts/{transcript_id}/confirm", tags=["Voice Intake"])
async def confirm_transcript(
    case_id: str,
    transcript_id: str,
    request: Request,
    payload: TranscriptConfirmRequest,
    current_user: ActorContext = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if current_user.role == "PATIENT":
        if case.patient_id != current_user.patient_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this case")
    elif not current_user.is_admin():
        if current_user.facility_id and case.facility_id != current_user.facility_id:
            raise HTTPException(status_code=403, detail="Cross-facility access denied")

    transcripts = getattr(request.app.state, "transcripts", {})
    t = transcripts.get(transcript_id)
    if not t or t.case_id != case_id:
        raise HTTPException(status_code=404, detail="Transcript not found")

    if t.status == "CONFIRMED":
        raise HTTPException(status_code=400, detail="Transcript already confirmed")

    # Authoritative canonical Evidence record
    evidence = Evidence(
        id=str(uuid.uuid4()),
        case_id=case.id,
        source_class="VOICE_TRANSCRIBED",
        epistemic_state="KNOWN",
        parameter_name="voice_transcript",
        content_value={
            "transcript": payload.transcript,
            "transcript_id": transcript_id,
            "confidence": t.confidence,
        },
        confidence_score=t.confidence,
        captured_timestamp=utc_now(),
        provenance_metadata={
            "channel": "VOICE_INTAKE",
            "actor_id": current_user.actor_id,
            "actor_role": current_user.role,
            "provider": t.provider_metadata.get("provider"),
            "model": t.provider_metadata.get("model"),
            "original_transcript": t.transcript if t.transcript != payload.transcript else None,
            "edited_by": current_user.actor_id if t.transcript != payload.transcript else None,
        },
        verification_metadata={
            "verified": False,
            "verification_status": "UNVERIFIED",
        },
        transformation_metadata={},
        created_at=utc_now(),
    )
    db.add(evidence)

    # Legacy / Compatibility EvidenceRecord
    ev_compat = EvidenceRecord(
        id=str(uuid.uuid4()),
        case_id=case.id,
        provenance_type="VOICE_TRANSCRIBED",
        source_filename="voice_intake.webm",
        extracted_payload={
            "transcript": payload.transcript,
            "confidence": t.confidence,
            "provider": t.provider_metadata.get("provider"),
        },
        confidence_score=t.confidence,
        verification_status="UNVERIFIED",
        created_at=utc_now(),
    )
    db.add(ev_compat)

    # Timeline event
    tl = TimelineEvent(
        id=str(uuid.uuid4()),
        case_id=case.id,
        event_type="VOICE_TRANSCRIPT_CONFIRMED",
        event_title="Voice Transcript Confirmed",
        event_content=f"Voice transcript confirmed: {payload.transcript[:100]}",
        event_timestamp=utc_now(),
        actor_id=current_user.actor_id,
        actor_role=current_user.role,
        evidence_id=evidence.id,
        is_conflict=False,
        provenance_metadata={
            "transcript_id": transcript_id,
            "confidence": t.confidence,
            "provider": t.provider_metadata.get("provider"),
        },
        created_at=utc_now(),
    )
    db.add(tl)

    # Update in-memory transcript status
    t.status = "CONFIRMED"
    t.transcript = payload.transcript

    # Audit records
    audit = AuditLog(
        action="VOICE_TRANSCRIPT_CONFIRMED",
        actor_id=current_user.actor_id,
        entity_type="EVIDENCE",
        entity_id=evidence.id,
        details={
            "transcript_id": transcript_id,
            "case_id": case_id,
            "actor_role": current_user.role,
        },
        timestamp=utc_now(),
    )
    db.add(audit)

    audit_event = AuditEvent(
        case_id=case.id,
        actor_id=current_user.actor_id,
        actor_role=current_user.role,
        action="voice.transcript.confirmed",
        object_type="EVIDENCE",
        object_id=evidence.id,
        result="SUCCESS",
        details={
            "transcript_id": transcript_id,
            "case_id": case_id,
            "confidence": t.confidence,
        },
        created_at=utc_now(),
    )
    db.add(audit_event)

    await db.commit()

    return {
        "message": "Transcript confirmed and added as evidence",
        "evidence_id": evidence.id,
        "transcript": payload.transcript,
        "provenance": "VOICE_TRANSCRIBED",
    }
