"""Medical Report OCR and document extraction service for Clinova AI."""

import logging
from typing import List, Optional
from app.schemas.case import OCRFieldSchema, ReportOCRResponse
from app.services.providers.ocr_space import OCRSpaceAdapter
from app.services.providers.local_fallback import LocalOCRProvider
from app.services.pdf_extractor import pdf_extractor

logger = logging.getLogger("clinova.ocr")


class OCRService:
    """Medical Report OCR extraction service with OCR.Space and local PDF parser."""

    def __init__(self):
        self.local_provider = LocalOCRProvider()
        self.adapter = OCRSpaceAdapter(fallback_provider=self.local_provider)

    async def process_report(
        self, file_bytes: bytes, filename: str = "report.png"
    ) -> ReportOCRResponse:
        """Process an uploaded medical lab report and extract key clinical fields."""
        if not file_bytes or len(file_bytes) == 0:
            return ReportOCRResponse(
                report_filename=filename,
                fields=[],
                raw_extracted_text="",
                confidence_average=0.0,
                is_synthetic_sample=False,
                status="failed",
                disclaimer="Empty file payload provided.",
            )

        mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/png"

        # Check if text PDF first
        if filename.lower().endswith(".pdf"):
            extracted_text, is_scanned, page_count = pdf_extractor.extract_text_from_bytes(file_bytes)
            if not is_scanned and len(extracted_text) >= 40:
                logger.info("PDF contains native digital text stream. Using direct extraction without OCR.")
                return ReportOCRResponse(
                    report_filename=filename,
                    fields=[],
                    raw_extracted_text=extracted_text,
                    confidence_average=1.0,
                    is_synthetic_sample=False,
                    status="success",
                    disclaimer="Extracted from digital text PDF stream. Requires reviewer verification.",
                )

        # Scanned PDF or Image: Route to OCR adapter
        try:
            data, metadata = await self.adapter.extract_text_and_tables(file_bytes, mime_type)
            raw_text = data.get("raw_text", "")
            raw_fields = data.get("fields", [])
            fields = []
            for f in raw_fields:
                fields.append(
                    OCRFieldSchema(
                        field_name=f.get("field_name", "Parameter"),
                        value=str(f.get("value", "")),
                        unit=f.get("unit", ""),
                        confidence=float(f.get("confidence", 0.9)),
                        verification_status="pending",
                        source_reference=filename,
                    )
                )

            return ReportOCRResponse(
                report_filename=filename,
                fields=fields,
                raw_extracted_text=raw_text,
                confidence_average=data.get("confidence_average", 0.9),
                is_synthetic_sample=metadata.fallback_used,
                status="success",
                disclaimer="Extracted via OCR — not a clinically confirmed diagnosis. Requires reviewer verification.",
            )
        except Exception as e:
            logger.error("OCR extraction failure: %s", e)
            return ReportOCRResponse(
                report_filename=filename,
                fields=[],
                raw_extracted_text="",
                confidence_average=0.0,
                is_synthetic_sample=False,
                status="failed",
                disclaimer=f"OCR processing failed: {str(e)}",
            )


ocr_service = OCRService()
