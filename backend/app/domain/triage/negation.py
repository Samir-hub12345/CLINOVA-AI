"""CLINOVA AI — Clinical Negation Detection Utility.

Implements rule-based clinical negation boundary detection (NegEx principles)
to prevent false-positive safety escalations and misclassification of negated symptoms.
"""

import re
from typing import List, Sequence

NEGATION_TRIGGERS: List[str] = [
    r"\bno\b",
    r"\bnot\b",
    r"\bdenies\b",
    r"\bdenied\b",
    r"\bdenying\b",
    r"\bwithout\b",
    r"\bnegative for\b",
    r"\babsence of\b",
    r"\bruled out\b",
    r"\brule out\b",
    r"\bfree of\b",
    r"\bnever\b",
    r"\bnone\b",
]

_NEG_TRIGGER_OR = "|".join(NEGATION_TRIGGERS)


def is_phrase_negated(text: str, keyword: str) -> bool:
    """
    Checks if keyword in text is preceded by a clinical negation trigger
    within a local 0-4 word scope window.
    """
    if not text or not keyword:
        return False
    lower_text = text.lower()
    lower_kw = keyword.lower()
    if lower_kw not in lower_text:
        return False

    pattern = re.compile(
        rf"(?:(?:{_NEG_TRIGGER_OR})\s+(?:(?:\w+)\s+){{0,4}}{re.escape(lower_kw)})",
        re.IGNORECASE,
    )
    return bool(pattern.search(lower_text))


def has_positive_finding(text: str, keywords: Sequence[str]) -> bool:
    """
    Returns True if any keyword in keywords appears in text without being clinically negated.
    """
    if not text or not keywords:
        return False
    lower_text = text.lower()
    for kw in keywords:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        if kw_clean in lower_text:
            if not is_phrase_negated(lower_text, kw_clean):
                return True
    return False
