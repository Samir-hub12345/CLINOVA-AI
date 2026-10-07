"""Local PDF text extraction and classification service for Clinova AI."""

import re
import zlib
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("clinova.pdf_extractor")


class PDFExtractor:
    """Classifies and extracts text from PDF documents.
    
    Distinguishes between machine-readable text PDFs (direct extraction)
    and image-only scanned PDFs (which require OCR processing).
    """

    @classmethod
    def extract_text_from_bytes(cls, pdf_bytes: bytes) -> Tuple[str, bool, int]:
        """Extract text from PDF bytes.
        
        Returns:
            Tuple[str, bool, int]: (extracted_text, is_scanned_pdf, estimated_page_count)
        """
        if not pdf_bytes or len(pdf_bytes) < 10:
            return "", True, 0

        # Check if pypdf is available
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            pages_text = []
            page_count = len(reader.pages)
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            full_text = "\n".join(pages_text).strip()
            is_scanned = len(full_text) < 30
            return full_text, is_scanned, page_count
        except Exception:
            pass

        # Native stream parser fallback using standard zlib and regex
        return cls._native_stream_parse(pdf_bytes)

    @classmethod
    def _native_stream_parse(cls, pdf_bytes: bytes) -> Tuple[str, bool, int]:
        """Native PDF stream decompression and text token extraction."""
        # Estimate page count by counting /Type\s*/Page (not /Pages)
        page_matches = re.findall(rb"/Type\s*/Page\b", pdf_bytes)
        page_count = max(1, len(page_matches))

        # Find all streams
        stream_regex = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
        streams = stream_regex.findall(pdf_bytes)

        extracted_fragments: List[str] = []

        for raw_stream in streams:
            decompressed = None
            try:
                decompressed = zlib.decompress(raw_stream)
            except Exception:
                try:
                    decompressed = zlib.decompress(raw_stream, -zlib.MAX_WBITS)
                except Exception:
                    decompressed = raw_stream

            if not decompressed:
                continue

            # Look for text blocks BT ... ET
            bt_regex = re.compile(rb"BT(.*?)ET", re.DOTALL)
            text_blocks = bt_regex.findall(decompressed)

            for block in text_blocks:
                # Extract strings inside parentheses: (Text here) Tj or [(Text)] TJ
                tj_strings = re.findall(rb"\((.*?)\)", block)
                for tj in tj_strings:
                    try:
                        decoded = tj.decode("utf-8", errors="ignore").strip()
                        if decoded:
                            extracted_fragments.append(decoded)
                    except Exception:
                        pass

        full_text = " ".join(extracted_fragments).strip()
        # Clean up multiple whitespaces
        full_text = re.sub(r"\s+", " ", full_text)

        # If negligible text found, document is an image/scanned PDF requiring OCR
        is_scanned = len(full_text) < 40

        return full_text, is_scanned, page_count


pdf_extractor = PDFExtractor()
