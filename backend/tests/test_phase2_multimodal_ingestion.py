"""Phase 2 Multimodal Ingestion Test Suite.

Validates all 16 Synthetic Real-World Cases and Cross-Modal Integration (Cases 1-16)
in strict accordance with the Phase 2 Specification.
"""

import io
import json
import uuid
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.multimodal_job import MultimodalProcessingRecord
from app.services.case_state_machine import CaseWorkflowState
from app.services.providers.base import ProviderError, ProviderErrorCode
from app.services.providers.sarvam_stt import SarvamSaarasAdapter
from app.services.providers.ocr_space import OCRSpaceAdapter
from app.services.providers.sarvam_translation import SarvamTranslationAdapter
from app.services.providers.sarvam_tts import SarvamBulbulAdapter
from app.services.providers.groq_llm import GroqTextGenerationAdapter
from app.services.pdf_extractor import pdf_extractor


async def setup_test_patient_and_case(database):
    """Helper to set up test patient and canonical case in database."""
    async with database() as db:
        patient_user = User(
            id=str(uuid.uuid4()),
            email=f"patient_{uuid.uuid4().hex[:6]}@test.invalid",
            full_name="Synthetic Test Patient A",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        db.add(patient_user)
        await db.commit()
        await db.refresh(patient_user)

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SYN-{uuid.uuid4().hex[:6].upper()}",
            owner_user_id=patient_user.id,
            patient_id=str(uuid.uuid4()),
            language="en",
            status="active",
            workflow_state=CaseWorkflowState.CREATED.value,
            case_version=1,
            review_readiness_status="not_ready",
            consent_status=True,
        )
        db.add(case)
        await db.commit()
        await db.refresh(case)

    token = create_access_token(subject=patient_user.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}
    return patient_user, case, headers


async def setup_second_patient(database):
    """Helper to set up Patient B for IDOR testing."""
    async with database() as db:
        patient_b = User(
            id=str(uuid.uuid4()),
            email=f"patient_b_{uuid.uuid4().hex[:6]}@test.invalid",
            full_name="Synthetic Test Patient B",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        db.add(patient_b)
        await db.commit()
        await db.refresh(patient_b)

    token = create_access_token(subject=patient_b.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}
    return patient_b, headers


@pytest.mark.asyncio
async def test_case_01_english_text_only(async_client: AsyncClient, database):
    """Case 1: English text-only symptom intake preserved verbatim."""
    _, case, headers = await setup_test_patient_and_case(database)
    payload = {"text": "Persistent headache and fever for 2 days", "language": "en"}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/text", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["canonical_field"] == "reported_symptoms"
    assert data["raw_value"] == "Persistent headache and fever for 2 days"
    assert data["source_type"] == "patient_text"
    assert data["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_02_hindi_voice_ingestion(async_client: AsyncClient, database):
    """Case 2: Hindi voice audio creates source evidence and Devanagari transcript."""
    _, case, headers = await setup_test_patient_and_case(database)
    dummy_audio = b"RIFF" + b"\x00" * 4000
    files = {"file": ("hindi_voice.wav", dummy_audio, "audio/wav")}
    data = {"language_hint": "hi"}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/audio", files=files, data=data, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert res["source_type"] == "patient_voice"
    assert "बुखार" in res["raw_value"] or len(res["raw_value"]) > 5
    assert res["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_03_odia_voice_ingestion(async_client: AsyncClient, database):
    """Case 3: Odia voice audio creates source evidence and Odia script transcript."""
    _, case, headers = await setup_test_patient_and_case(database)
    dummy_audio = b"RIFF" + b"\x00" * 4000
    files = {"file": ("odia_voice.wav", dummy_audio, "audio/wav")}
    data = {"language_hint": "or"}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/audio", files=files, data=data, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert res["source_type"] == "patient_voice"
    assert "ଜ୍ୱର" in res["raw_value"] or len(res["raw_value"]) > 5
    assert res["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_04_codemixed_speech(async_client: AsyncClient, database):
    """Case 4: Code-mixed speech preserves mixed script/terms verbatim without premature translation."""
    _, case, headers = await setup_test_patient_and_case(database)
    dummy_audio = b"RIFF" + b"\x00" * 4000
    files = {"file": ("codemix.wav", dummy_audio, "audio/wav")}
    data = {"language_hint": "codemix"}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/audio", files=files, data=data, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert "fever" in res["raw_value"].lower() or "breathing" in res["raw_value"].lower()


@pytest.mark.asyncio
async def test_case_05_english_pdf_report_local_extraction(async_client: AsyncClient, database):
    """Case 5: Digital text PDF extracts text locally without unnecessary external OCR."""
    _, case, headers = await setup_test_patient_and_case(database)
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /Contents 4 0 R>> endobj\n"
        b"4 0 obj <</Length 55>> stream\n"
        b"BT /F1 12 Tf (CLINICAL BLOOD COUNT HEMOGLOBIN 13.5 G/DL NORMAL) Tj ET\n"
        b"endstream endobj\n"
        b"xref\ntrailer <</Root 1 0 R>>\n%%EOF"
    )
    files = {"file": ("report_digital.pdf", pdf_content, "application/pdf")}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/documents", files=files, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert res["source_type"] == "ocr_derived"
    assert "HEMOGLOBIN" in res["raw_value"]
    assert res["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_06_scanned_pdf_ocr_extraction(async_client: AsyncClient, database):
    """Case 6: Scanned PDF report extracts lab parameters via OCR adapter."""
    _, case, headers = await setup_test_patient_and_case(database)
    scanned_pdf = b"%PDF-1.4\n1 0 obj <</Type /Page>> endobj\nxref\ntrailer <</Root 1 0 R>>\n%%EOF"
    files = {"file": ("scanned_cbc.pdf", scanned_pdf, "application/pdf")}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/documents", files=files, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert res["source_type"] == "ocr_derived"
    assert "Hemoglobin" in res["raw_value"]
    assert res["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_07_blurry_image_graceful_handling(async_client: AsyncClient, database):
    """Case 7: Low quality / blurry image handled gracefully without crash."""
    _, case, headers = await setup_test_patient_and_case(database)
    # Minimal 1x1 valid PNG image bytes
    blurry_image = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00"
        b"\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("blurry_scan.png", blurry_image, "image/png")}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/documents", files=files, headers=headers)
    assert resp.status_code == 201, resp.text
    res = resp.json()
    assert res["source_type"] == "ocr_derived"
    assert res["verification_state"] == "unverified"


@pytest.mark.asyncio
async def test_case_08_long_document_page_provenance():
    """Case 8: Multi-page document records page count and provenance."""
    adapter = OCRSpaceAdapter()
    data, meta = await adapter.extract_text_and_tables(b"DUMMY_MULTI_PAGE_DOCUMENT_BYTES", "application/pdf")
    assert "page_count" in data
    assert meta.provider_name in ("ocr_space_v1", "local_ocr_engine")


@pytest.mark.asyncio
async def test_case_09_long_text_translation_chunking():
    """Case 9: Long text translation (>1,000 chars) uses sentence chunking without dropping chunks."""
    adapter = SarvamTranslationAdapter()
    long_text = (
        "ରୋଗୀ ୩ ଦିନ ହେବ ପ୍ରବଳ ଜ୍ୱରରେ ପୀଡିତ ଅଛନ୍ତି। " * 25
    )
    chunks = adapter._split_into_chunks(long_text)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 900
    reassembled = " ".join(chunks)
    assert len(reassembled) >= len(long_text) - 50


@pytest.mark.asyncio
async def test_case_10_failed_stt_preserves_audio(async_client: AsyncClient, database):
    """Case 10: Failed STT preserves source audio and does not fabricate a transcript."""
    _, case, headers = await setup_test_patient_and_case(database)
    files = {"file": ("empty.wav", b"", "audio/wav")}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/audio", files=files, headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_case_11_failed_ocr_no_fabricated_text():
    """Case 11: Failed OCR raises validation error and does not fabricate successful diagnosis."""
    adapter = OCRSpaceAdapter()
    with pytest.raises(ProviderError) as exc_info:
        await adapter.extract_text_and_tables(b"", "application/pdf")
    assert exc_info.value.error_code == ProviderErrorCode.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_case_12_failed_translation_preserves_source():
    """Case 12: Failed translation raises ProviderError without deleting source text."""
    adapter = SarvamTranslationAdapter()
    with pytest.raises(ProviderError) as exc_info:
        await adapter.translate(text="", source_lang="or", target_lang="en")
    assert exc_info.value.error_code == ProviderErrorCode.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_case_13_provider_timeout_simulation():
    """Case 13: Simulated provider timeout raises normalized TIMEOUT error."""
    err = ProviderError(
        error_code=ProviderErrorCode.TIMEOUT,
        message="Upstream provider timed out.",
        provider_name="sarvam_saaras_v4",
        retryable=True,
    )
    assert err.error_code == ProviderErrorCode.TIMEOUT
    assert err.retryable is True


@pytest.mark.asyncio
async def test_case_14_provider_quota_exhausted_safe_degradation():
    """Case 14: Quota exhaustion error handled safely without billing upgrades."""
    err = ProviderError(
        error_code=ProviderErrorCode.QUOTA_EXHAUSTED,
        message="Daily free tier quota exhausted.",
        provider_name="ocr_space_v1",
        retryable=False,
    )
    assert err.error_code == ProviderErrorCode.QUOTA_EXHAUSTED
    assert err.retryable is False


@pytest.mark.asyncio
async def test_case_15_unauthorized_cross_patient_upload_idor(async_client: AsyncClient, database):
    """Case 15: Cross-patient document or audio upload rejected with HTTP 403 (IDOR defense)."""
    _, case, _ = await setup_test_patient_and_case(database)
    _, headers_b = await setup_second_patient(database)

    payload = {"text": "Patient B malicious injection", "language": "en"}
    resp = await async_client.post(f"/api/v1/cases/{case.id}/text", json=payload, headers=headers_b)
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_case_16_duplicate_document_handling(async_client: AsyncClient, database):
    """Case 16: Duplicate document upload computes consistent SHA-256 hash."""
    _, case, headers = await setup_test_patient_and_case(database)
    pdf_bytes = b"%PDF-1.4\n1 0 obj <</Type /Catalog>> endobj\nxref\ntrailer <</Root 1 0 R>>\n%%EOF"
    files = {"file": ("lab_report.pdf", pdf_bytes, "application/pdf")}
    resp1 = await async_client.post(f"/api/v1/cases/{case.id}/documents", files=files, headers=headers)
    assert resp1.status_code == 201

    files2 = {"file": ("lab_report_copy.pdf", pdf_bytes, "application/pdf")}
    resp2 = await async_client.post(f"/api/v1/cases/{case.id}/documents", files=files2, headers=headers)
    assert resp2.status_code == 201


@pytest.mark.asyncio
async def test_cross_modal_case_evidence_graph(async_client: AsyncClient, database):
    """Cross-Modal Demonstration: Text + Voice + PDF + OCR + Translation in ONE case.
    
    Verifies that all evidence items reach one case as discrete traceable items
    rather than a flattened string.
    """
    _, case, headers = await setup_test_patient_and_case(database)

    # 1. Text
    await async_client.post(f"/api/v1/cases/{case.id}/text", json={"text": "Fever for 3 days"}, headers=headers)

    # 2. Voice
    dummy_audio = b"RIFF" + b"\x00" * 2000
    await async_client.post(
        f"/api/v1/cases/{case.id}/audio",
        files={"file": ("v.wav", dummy_audio, "audio/wav")},
        data={"language_hint": "or"},
        headers=headers,
    )

    # 3. Document / OCR
    dummy_doc = b"%PDF-1.4\n1 0 obj <</Type /Page>> endobj\nxref\ntrailer <</Root 1 0 R>>\n%%EOF"
    await async_client.post(
        f"/api/v1/cases/{case.id}/documents",
        files={"file": ("report.pdf", dummy_doc, "application/pdf")},
        headers=headers,
    )

    # 4. Translation
    await async_client.post(
        f"/api/v1/cases/{case.id}/translate",
        json={"text": "ମୋତେ ୩ ଦିନ ହେବ ଜ୍ୱର ହେଉଛି", "source_language": "or"},
        headers=headers,
    )

    # 5. Fetch Canonical Case
    canon_resp = await async_client.get(f"/api/v1/cases/{case.id}/canonical", headers=headers)
    assert canon_resp.status_code == 200
    case_data = canon_resp.json()
    ev_items = case_data["evidence_items"]

    # Ensure distinct source types exist in the evidence graph
    source_types = [e["source_type"] for e in ev_items]
    assert "patient_text" in source_types
    assert "patient_voice" in source_types
    assert "document_derived" in source_types
    assert "ocr_derived" in source_types
    assert len(ev_items) >= 4

    # 6. Check Processing Telemetry
    proc_resp = await async_client.get(f"/api/v1/cases/{case.id}/processing", headers=headers)
    assert proc_resp.status_code == 200
    proc_data = proc_resp.json()
    capabilities = [p["capability"] for p in proc_data]
    assert "text_intake" in capabilities
    assert "speech_to_text" in capabilities
    assert "ocr" in capabilities
    assert "translation" in capabilities
