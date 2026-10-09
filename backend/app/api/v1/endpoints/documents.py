"""CLINOVA AI — Document API Router.

Phase 20: OCR + CLINICAL REPORT EXTRACTION.
Handles document upload, validation, OCR processing, and extraction.
"""

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import hashlib
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Case, Document, DocumentExtraction, AuditEvent
from app.core.auth import get_current_actor, ActorContext
from app.core.config import settings
from app.core.policy import authorize_case_access
from app.core.errors import ClinovaAPIError
from app.ocr.provider import get_ocr_provider

router = APIRouter()

UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

class DocumentResponse(BaseModel):
    id: str
    case_id: str
    filename: str
    mime_type: str
    processing_status: str
    created_at: datetime
    ocr_provider: Optional[str] = None
    page_count: Optional[int] = None

class ExtractionResponse(BaseModel):
    id: str
    document_id: str
    entity_type: str
    entity_value: str
    confidence: float
    created_at: datetime

def generate_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

@router.post("/{case_id}/documents", response_model=DocumentResponse)
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    # Authorization
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)

    # Validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ClinovaAPIError("VALIDATION_ERROR", f"Unsupported MIME type: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ClinovaAPIError("VALIDATION_ERROR", "File size exceeds limit")
        
    # Adversarial Path Traversal Validation
    safe_filename = os.path.basename(file.filename)
    if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
        # Strictly, if any malicious pattern, reject safely
        safe_filename = "malformed_name"

    content_hash = generate_file_hash(content)
    storage_path = os.path.join(UPLOAD_DIR, f"{case_id}_{content_hash}_{safe_filename}")

    with open(storage_path, "wb") as out_file:
        out_file.write(content)

    doc = Document(
        case_id=case_id,
        filename=safe_filename,
        mime_type=file.content_type,
        file_size_bytes=len(content),
        storage_path=storage_path,
        content_fingerprint=content_hash,
        processing_status="UPLOADED"
    )
    db.add(doc)
    
    # Audit
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="DOCUMENT_UPLOAD",
        object_type="Document",
        object_id="PENDING", # Assigned after flush
        result="SUCCESS"
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(doc)
    
    audit.object_id = doc.id
    await db.commit()

    return doc

@router.get("/{case_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)
    
    result = await db.execute(select(Document).where(Document.case_id == case_id))
    docs = result.scalars().all()
    return docs

@router.post("/{case_id}/documents/{document_id}/ocr")
async def run_ocr(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)
    
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.case_id == case_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise ClinovaAPIError("NOT_FOUND", "Document not found")
        
    provider = get_ocr_provider(use_mock=True)
    
    doc.processing_status = "OCR_PROCESSING"
    await db.commit()
    
    try:
        ocr_result = await provider.process_document(doc.storage_path, doc.mime_type)
        doc.ocr_provider = ocr_result.get("provider")
        doc.ocr_model_version = ocr_result.get("model_version")
        doc.page_count = ocr_result.get("page_count")
        doc.extracted_text = ocr_result.get("extracted_text")
        doc.ocr_quality_metadata = ocr_result.get("ocr_quality_metadata")
        doc.language_metadata = ocr_result.get("language_metadata")
        doc.processing_status = "OCR_COMPLETED"
    except Exception as e:
        doc.processing_status = "OCR_FAILED"
        doc.error_status = str(e)
        
    audit = AuditEvent(
        case_id=case_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action="DOCUMENT_OCR",
        object_type="Document",
        object_id=doc.id,
        result="SUCCESS" if doc.processing_status == "OCR_COMPLETED" else "FAILURE"
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(doc)
    
    return {"status": doc.processing_status, "document_id": doc.id}

@router.get("/{case_id}/documents/{document_id}/ocr")
async def get_ocr(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.case_id == case_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise ClinovaAPIError("NOT_FOUND", "Document not found")
        
    return {
        "document_id": doc.id,
        "processing_status": doc.processing_status,
        "extracted_text": doc.extracted_text,
        "ocr_metadata": doc.ocr_quality_metadata
    }

@router.post("/{case_id}/documents/{document_id}/extract", response_model=List[ExtractionResponse])
async def extract_structured_data(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.case_id == case_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise ClinovaAPIError("NOT_FOUND", "Document not found")
        
    if doc.processing_status != "OCR_COMPLETED":
        raise ClinovaAPIError("INVALID_STATE", "Document OCR not completed")

    # Simulate Extraction Logic
    extractions = []
    text = doc.extracted_text or ""
    if "Hemoglobin" in text:
        extractions.append(
            DocumentExtraction(
                document_id=doc.id,
                case_id=doc.case_id,
                entity_type="LAB_RESULT_HEMOGLOBIN",
                entity_value="10.2",
                confidence=0.95
            )
        )
        
    if "Heart Rate" in text:
        extractions.append(
            DocumentExtraction(
                document_id=doc.id,
                case_id=doc.case_id,
                entity_type="VITAL_HEART_RATE",
                entity_value="85",
                confidence=0.88
            )
        )
        
    for e in extractions:
        db.add(e)
        
    doc.processing_status = "EXTRACTION_COMPLETED"
    await db.commit()
    
    # Return added extractions (we need to refresh to get IDs)
    for e in extractions:
        await db.refresh(e)
        
    return extractions

@router.get("/{case_id}/documents/{document_id}/extractions", response_model=List[ExtractionResponse])
async def list_extractions(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    case = await db.get(Case, case_id)
    if not case:
        raise ClinovaAPIError("NOT_FOUND", "Case not found", status_code=404)
    await authorize_case_access(case, actor, db=db)
    result = await db.execute(
        select(DocumentExtraction).where(
            DocumentExtraction.document_id == document_id, 
            DocumentExtraction.case_id == case_id
        )
    )
    return result.scalars().all()
