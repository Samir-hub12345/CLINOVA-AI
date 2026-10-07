"""CLINOVA AI — Multimodal Intake Router.

Implements BPUT Baseline Multimodal Intake:
- Informed consent capture
- Text narrative intake with PII anonymization
- Voice speech-to-text intake (VOICE_TRANSCRIBED provenance)
- Medical report / lab OCR extraction (OCR_EXTRACTED provenance)
- Regional translation (Hindi, Odia, English)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import (
    Patient,
    Case,
    Consent,
    EvidenceRecord,
    VitalReading,
    AuditLog,
    Facility,
)
from app.baseline.intake.adapters import (
    translate_text,
    scrub_pii,
    parse_clinical_narrative,
    process_voice_transcript,
    parse_medical_report_ocr,
)
from app.domain.caregraph.engine import (
    calculate_risk_score,
    evaluate_uncertainty_and_gaps,
)
from app.domain.signalgraph.engine import signal_engine

router = APIRouter()


class ConsentRequest(BaseModel):
    case_id: Optional[str] = None
    patient_ref: Optional[str] = None
    language: str = "en"
    consent_granted: bool = True


class TextIntakeRequest(BaseModel):
    facility_id: str = "FAC-DH-04"
    reported_name: Optional[str] = None
    reported_age: Optional[int] = 45
    biological_sex: str = "MALE"
    narrative_text: str
    language: str = "en"
    consent_granted: bool = True
    vitals: Optional[Dict[str, Any]] = None


class VoiceIntakeRequest(BaseModel):
    facility_id: str = "FAC-PHC-01"
    audio_transcript: str
    confidence_score: float = 0.92
    language: str = "hi"
    reported_name: Optional[str] = None
    reported_age: Optional[int] = 50
    biological_sex: str = "MALE"
    consent_granted: bool = True


class OCRIntakeRequest(BaseModel):
    raw_text: str
    confidence_score: float = 0.88
    filename: Optional[str] = "lab_report.pdf"


class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str = "en"


@router.post("/consent", tags=["Multimodal Intake"])
async def record_consent(req: ConsentRequest, db: AsyncSession = Depends(get_db)):
    """Records patient informed consent."""
    consent_id = str(uuid.uuid4())
    if req.case_id:
        existing = await db.execute(select(Consent).where(Consent.case_id == req.case_id))
        consent_obj = existing.scalars().first()
        if consent_obj:
            consent_obj.consent_granted = req.consent_granted
            consent_obj.language = req.language
            consent_obj.recorded_at = datetime.now(timezone.utc)
        else:
            consent_obj = Consent(
                id=consent_id,
                case_id=req.case_id,
                consent_granted=req.consent_granted,
                language=req.language,
                recorded_at=datetime.now(timezone.utc),
            )
            db.add(consent_obj)
        await db.commit()

    return {
        "consent_id": consent_id,
        "consent_granted": req.consent_granted,
        "language": req.language,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "status": "RECORDED",
    }


@router.post("/text", tags=["Multimodal Intake"])
async def intake_text_narrative(req: TextIntakeRequest, db: AsyncSession = Depends(get_db)):
    """
    Ingests text narrative clinical encounter.
    Enforces PII minimization, translation, initial risk scoring, and uncertainty evaluation.
    """
    # 1. Translation
    normalized_text, _ = translate_text(req.narrative_text, req.language, target_lang="en")

    # 2. PII Scrubbing
    pii_result = scrub_pii(normalized_text, reported_name=req.reported_name, reported_age=req.reported_age)
    synthetic_pt_id = pii_result["synthetic_id"]
    age_bracket = pii_result["age_bracket"]
    scrubbed_narrative = pii_result["scrubbed_narrative"]

    # 3. Clinical Entity & Syndrome Extraction
    parsed = parse_clinical_narrative(scrubbed_narrative)
    syndrome = parsed["primary_syndrome"]
    req_bundle = parsed["required_bundle"]
    red_flags = parsed["red_flags"]

    # 4. Risk & Acuity Scoring
    vitals_dict = req.vitals or {}
    rt, acuity_tier = calculate_risk_score(vitals_dict, red_flags=red_flags)

    # 5. Uncertainty & Missing Parameter Detection
    ev_record_temp = [{"provenance_type": "PATIENT_REPORTED", "confidence_score": 0.90, "verification_status": "UNVERIFIED"}]
    u_eval = evaluate_uncertainty_and_gaps(syndrome, vitals_dict, ev_record_temp, narrative_text=scrubbed_narrative)
    u_t = u_eval["uncertainty_score"]

    # Determine initial FSM state
    if len(u_eval["conflicts"]) > 0:
        initial_status = "CONFLICTING_DATA"
    elif u_t > 0.40 and len(u_eval["missing_parameters"]) > 0 and rt < 0.70:
        initial_status = "INSUFFICIENT_DATA"
    elif rt >= 0.70:
        initial_status = "TRIAGED"
    else:
        initial_status = "REVIEW_REQUIRED"

    # Persist Synthetic Patient
    patient = Patient(
        synthetic_id=synthetic_pt_id,
        age_bracket=age_bracket,
        biological_sex=req.biological_sex,
    )
    db.add(patient)
    await db.flush()

    # Verify Facility exists
    fac = await db.get(Facility, req.facility_id)
    if not fac:
        fac = (await db.execute(select(Facility))).scalars().first()
        facility_id = fac.id if fac else req.facility_id
    else:
        facility_id = req.facility_id

    case_num = f"CAS-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
    case = Case(
        case_number=case_num,
        patient_id=patient.id,
        facility_id=facility_id,
        status=initial_status,
        acuity_tier=acuity_tier,
        risk_score=rt,
        trajectory_slope=0.0,
        uncertainty_score=u_t,
        presenting_complaint=scrubbed_narrative,
        primary_syndrome=syndrome,
        required_bundle=req_bundle,
    )
    db.add(case)
    await db.flush()

    # Consent
    consent = Consent(
        case_id=case.id,
        consent_granted=req.consent_granted,
        language=req.language,
    )
    db.add(consent)

    # Evidence Record
    ev = EvidenceRecord(
        case_id=case.id,
        provenance_type="PATIENT_REPORTED",
        source_filename="narrative_text_intake.txt",
        extracted_payload={"narrative": scrubbed_narrative, "syndrome": syndrome, "bundle": req_bundle},
        confidence_score=0.90,
        verification_status="UNVERIFIED",
    )
    db.add(ev)

    # Initial Vital Reading if provided
    if vitals_dict:
        vital_reading = VitalReading(
            case_id=case.id,
            heart_rate=vitals_dict.get("heart_rate"),
            systolic_bp=vitals_dict.get("systolic_bp"),
            diastolic_bp=vitals_dict.get("diastolic_bp"),
            spo2_percent=vitals_dict.get("spo2_percent"),
            respiratory_rate=vitals_dict.get("respiratory_rate"),
            temperature_celsius=vitals_dict.get("temperature_celsius"),
            avpu_score=vitals_dict.get("avpu_score", "ALERT"),
        )
        db.add(vital_reading)

    # Audit Trail
    audit = AuditLog(
        actor_id="INTAKE_SYSTEM",
        action="INTAKE_TEXT_CREATED",
        entity_type="CASE",
        entity_id=case.id,
        details={
            "case_number": case.case_number,
            "patient_synthetic_id": synthetic_pt_id,
            "status": initial_status,
            "risk_score": rt,
            "acuity_tier": acuity_tier,
        },
    )
    db.add(audit)
    await db.commit()

    # Feed SignalGraph
    signal_engine.record_event(
        facility_id=facility_id,
        syndrome_tag=f"SYNDROME_{syndrome}",
        acuity_tier=acuity_tier,
    )

    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "patient_synthetic_id": synthetic_pt_id,
        "status": case.status,
        "acuity_tier": case.acuity_tier,
        "risk_score": case.risk_score,
        "uncertainty_score": case.uncertainty_score,
        "primary_syndrome": syndrome,
        "required_bundle": req_bundle,
        "missing_parameters": u_eval["missing_parameters"],
        "follow_up_questions": u_eval["follow_up_questions"],
        "conflicts": u_eval["conflicts"],
    }


@router.post("/voice", tags=["Multimodal Intake"])
async def intake_voice(req: VoiceIntakeRequest, db: AsyncSession = Depends(get_db)):
    """Transcribes audio narrative, assigns VOICE_TRANSCRIBED provenance, and executes intake."""
    translated, _ = translate_text(req.audio_transcript, req.language, target_lang="en")
    voice_result = process_voice_transcript(translated, confidence=req.confidence_score)

    # Execute text intake with voice metadata
    text_req = TextIntakeRequest(
        facility_id=req.facility_id,
        reported_name=req.reported_name,
        reported_age=req.reported_age,
        biological_sex=req.biological_sex,
        narrative_text=translated,
        language="en",
        consent_granted=req.consent_granted,
    )
    result = await intake_text_narrative(text_req, db)

    # Update evidence record provenance to VOICE_TRANSCRIBED
    ev_stmt = select(EvidenceRecord).where(EvidenceRecord.case_id == result["case_id"])
    ev_obj = (await db.execute(ev_stmt)).scalars().first()
    if ev_obj:
        ev_obj.provenance_type = "VOICE_TRANSCRIBED"
        ev_obj.confidence_score = req.confidence_score
        ev_obj.source_filename = "voice_audio_stream.wav"
        await db.commit()

    result["provenance_type"] = "VOICE_TRANSCRIBED"
    result["voice_confidence"] = req.confidence_score
    return result


@router.post("/ocr", tags=["Multimodal Intake"])
async def intake_medical_report_ocr(req: OCRIntakeRequest):
    """Parses medical report / lab slip with OCR extraction and confidence guardrails."""
    res = parse_medical_report_ocr(req.raw_text, confidence=req.confidence_score)
    return res


@router.post("/translate", tags=["Multimodal Intake"])
async def translate_clinical_text(req: TranslateRequest):
    """Translates between regional Indian languages and clinical English."""
    translated, target = translate_text(req.text, req.source_lang, req.target_lang)
    return {
        "original_text": req.text,
        "translated_text": translated,
        "source_lang": req.source_lang,
        "target_lang": target,
    }
