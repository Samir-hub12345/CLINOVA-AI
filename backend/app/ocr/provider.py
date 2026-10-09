"""CLINOVA AI — OCR Provider Abstraction.

Phase 20: Document OCR + Clinical Report Extraction.
Zero-Cost / Local-First architecture.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DocumentOCRProvider(ABC):
    @abstractmethod
    async def process_document(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Process a document and return a structured OCR extraction result."""
        pass

class MockOCRProvider(DocumentOCRProvider):
    async def process_document(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        # Handle some adversarial test cases based on hints in prompt
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
            if "prompt injection" in content.lower():
                # We extract it safely without executing it
                return {
                    "provider": "MockOCRProvider",
                    "model_version": "1.0",
                    "page_count": 1,
                    "extracted_text": content,
                    "ocr_quality_metadata": {"confidence": 0.95},
                    "language_metadata": "en"
                }

        return {
            "provider": "MockOCRProvider",
            "model_version": "1.0",
            "page_count": 1,
            "extracted_text": "MOCK_OCR_TEXT: Hemoglobin 10.2 g/dL",
            "ocr_quality_metadata": {"confidence": 0.95},
            "language_metadata": "en"
        }

class LocalOCRProvider(DocumentOCRProvider):
    async def process_document(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        return {
            "provider": "LocalOCRProvider",
            "model_version": "Local_Mock",
            "page_count": 1,
            "extracted_text": "LOCAL_OCR_TEXT: Heart Rate 85 bpm",
            "ocr_quality_metadata": {"confidence": 0.88},
            "language_metadata": "en"
        }

def get_ocr_provider(use_mock: bool = True) -> DocumentOCRProvider:
    if use_mock:
        return MockOCRProvider()
    return LocalOCRProvider()
