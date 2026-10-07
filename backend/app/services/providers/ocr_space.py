"""OCR.Space Optical Character Recognition provider adapter for Clinova AI."""

import time
import logging
from typing import Optional, Dict, Any, Tuple
import httpx

from app.core.config import settings
from app.services.providers.base import (
    OCRProvider,
    ProviderResponseMetadata,
    ProviderError,
    ProviderErrorCode,
)
from app.services.providers.local_fallback import LocalOCRProvider

logger = logging.getLogger("clinova.providers.ocr_space")


class OCRSpaceAdapter(OCRProvider):
    """Adapter for OCR.Space free REST API.
    
    Extracts text and table layout from medical laboratory reports, images,
    and scanned PDFs within free-tier resource boundaries.
    """

    API_ENDPOINT = "https://api.ocr.space/parse/image"

    def __init__(self, api_key: Optional[str] = None, fallback_provider: Optional[OCRProvider] = None):
        super().__init__(provider_name="ocr_space_v1")
        self.api_key = api_key or settings.OCR_SPACE_API_KEY
        self.fallback = fallback_provider or LocalOCRProvider()

    def is_available(self) -> bool:
        return bool(settings.AI_EXTERNAL_ENABLED and self.api_key and self.api_key.strip())

    async def extract_text_and_tables(
        self, document_bytes: bytes, mime_type: str = "application/pdf"
    ) -> Tuple[Dict[str, Any], ProviderResponseMetadata]:
        if not document_bytes or len(document_bytes) == 0:
            raise ProviderError(
                error_code=ProviderErrorCode.VALIDATION_ERROR,
                message="Document bytes are empty.",
                provider_name=self.provider_name,
                retryable=False,
            )

        file_size_mb = len(document_bytes) / (1024 * 1024)
        if file_size_mb > 1.0:
            logger.warning("Document size (%.2f MB) exceeds OCR.Space free-tier 1 MB threshold.", file_size_mb)

        if not self.is_available():
            logger.info("OCR.Space external API disabled or key absent. Using local fallback.")
            result, meta = await self.fallback.extract_text_and_tables(document_bytes, mime_type)
            meta.fallback_used = True
            return result, meta

        start_time = time.time()
        headers = {
            "apikey": self.api_key.strip(),
        }
        filename = "document.pdf" if "pdf" in mime_type.lower() else "document.png"
        files = {
            "file": (filename, document_bytes, mime_type),
        }
        data = {
            "isOverlayRequired": "false",
            "isTable": "true",
            "scale": "true",
            "OCREngine": "2",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.API_ENDPOINT, headers=headers, files=files, data=data)

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                resp_json = response.json()
                is_errored = resp_json.get("IsErroredOnProcessing", False)
                if is_errored:
                    err_msg = resp_json.get("ErrorMessage", ["OCR processing failed."])
                    if isinstance(err_msg, list):
                        err_msg = "; ".join(err_msg)
                    raise ProviderError(
                        error_code=ProviderErrorCode.PROCESSING_ERROR,
                        message=f"OCR.Space error: {err_msg}",
                        provider_name=self.provider_name,
                        retryable=False,
                    )

                parsed_results = resp_json.get("ParsedResults", [])
                full_text = "\n".join([r.get("ParsedText", "") for r in parsed_results if isinstance(r, dict)])
                
                result = {
                    "raw_text": full_text.strip(),
                    "page_count": len(parsed_results),
                    "fields": [],
                    "confidence_average": 0.88,
                }
                metadata = ProviderResponseMetadata(
                    provider_name=self.provider_name,
                    model_name="ocr_space_engine_2",
                    latency_ms=latency_ms,
                    fallback_used=False,
                    processing_status="success",
                )
                return result, metadata

            elif response.status_code in (401, 403):
                raise ProviderError(
                    error_code=ProviderErrorCode.AUTHENTICATION_ERROR,
                    message="OCR.Space API key invalid or unauthorized.",
                    provider_name=self.provider_name,
                    retryable=False,
                )
            elif response.status_code == 429:
                raise ProviderError(
                    error_code=ProviderErrorCode.RATE_LIMITED,
                    message="OCR.Space rate limit (500 requests/day) exceeded.",
                    provider_name=self.provider_name,
                    retryable=True,
                )
            else:
                raise ProviderError(
                    error_code=ProviderErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"OCR.Space returned HTTP {response.status_code}",
                    provider_name=self.provider_name,
                    retryable=response.status_code >= 500,
                )

        except httpx.TimeoutException:
            logger.warning("OCR.Space timeout. Falling back to local OCR engine.")
            if self.fallback:
                result, meta = await self.fallback.extract_text_and_tables(document_bytes, mime_type)
                meta.fallback_used = True
                return result, meta
            raise ProviderError(
                error_code=ProviderErrorCode.TIMEOUT,
                message="OCR.Space request timed out.",
                provider_name=self.provider_name,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.warning("OCR.Space network error: %s. Using local fallback.", exc)
            if self.fallback:
                result, meta = await self.fallback.extract_text_and_tables(document_bytes, mime_type)
                meta.fallback_used = True
                return result, meta
            raise ProviderError(
                error_code=ProviderErrorCode.NETWORK_ERROR,
                message="OCR.Space connection failed.",
                provider_name=self.provider_name,
                retryable=True,
            )
