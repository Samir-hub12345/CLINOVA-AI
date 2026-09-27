import re
import random
from typing import Tuple


class AnonymizerService:
    """Anonymization layer removing PII before information is sent to AI models."""

    PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    AADHAAR_REGEX = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")

    @classmethod
    def sanitize_text(cls, text: str) -> Tuple[str, bool]:
        """Redact direct personal identifiers like phone numbers, emails, and identification numbers."""
        if not text:
            return "", False

        redacted = False
        result = text

        if cls.AADHAAR_REGEX.search(result):
            result = cls.AADHAAR_REGEX.sub("[GOVT_ID_REDACTED]", result)
            redacted = True

        if cls.EMAIL_REGEX.search(result):
            result = cls.EMAIL_REGEX.sub("[EMAIL_REDACTED]", result)
            redacted = True

        if cls.PHONE_REGEX.search(result):
            result = cls.PHONE_REGEX.sub("[PHONE_REMOVED]", result)
            redacted = True

        return result, redacted

    @classmethod
    def generate_synthetic_case_id(cls, prefix: str = "CLV-DEMO") -> str:
        """Generate human-readable synthetic case IDs without personal identifiable information."""
        num = random.randint(10000, 999999)
        return f"{prefix}-{num}"


anonymizer = AnonymizerService()
