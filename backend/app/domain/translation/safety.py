"""CLINOVA AI — Multilingual Clinical Safety & Semantic Integrity Validator.

Grounded in Phase 21 Sections 11, 12, 13, 29, 50, 54.
Validates:
1. Negation preservation (no, not, denies, without, never, absent, negative, etc.)
2. Numeric & vital measurement preservation (BP ratios, temperatures, percentages, counts)
3. Uncertainty preservation (maybe, possibly, not sure, etc.)
4. Prompt injection untrusted data boundary detection
"""

import re
from typing import Dict, Any, List, Set

# Negation lexicon per supported language
NEGATION_LEXICON: Dict[str, Set[str]] = {
    "en": {"no", "not", "denies", "without", "never", "absent", "negative", "none", "neither", "nor"},
    "hi": {"नहीं", "ना", "बिना", "रहित", "न", "इनकार"},
    "or": {"ନାହିଁ", "ନାହି", "ବିନା", "ନୁହେଁ", "ନୁହେ", "ମନା"},
}

# Uncertainty lexicon per supported language
UNCERTAINTY_LEXICON: Dict[str, Set[str]] = {
    "en": {"maybe", "possibly", "perhaps", "not sure", "uncertain", "unclear", "probable", "suspected"},
    "hi": {"शायद", "हो सकता है", "पक्का नहीं", "संभवतः", "अनिश्चित"},
    "or": {"ହୁଏତ", "ହୋଇପାରେ", "ନିଶ୍ଚିତ ନୁହେଁ", "ସମ୍ଭବତଃ"},
}

# Known prompt injection patterns
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"drop\s+table", re.IGNORECASE),
    re.compile(r"prescribe\s+(medicine|drugs|medication)", re.IGNORECASE),
    re.compile(r"override\s+(policy|triage|safety)", re.IGNORECASE),
]

def extract_numbers(text: str) -> List[str]:
    """Extracts numbers, fractions, percentages, and vital ratios (e.g. 120/80, 37.5)."""
    # Matches integers, decimals, and slash-separated values like BP 120/80
    return re.findall(r"\b\d+(?:[\./]\d+)?%?\b", text)

def has_negation(text: str, lang: str) -> bool:
    """Checks if text contains negation markers in the specified language."""
    words = re.findall(r"[\w\u0900-\u097F\u0B00-\u0B7F]+", text.lower())
    lexicon = NEGATION_LEXICON.get(lang, NEGATION_LEXICON["en"])
    return any(w in lexicon for w in words)

def has_uncertainty(text: str, lang: str) -> bool:
    """Checks if text contains uncertainty markers in the specified language."""
    words = re.findall(r"[\w\u0900-\u097F\u0B00-\u0B7F]+", text.lower())
    lexicon = UNCERTAINTY_LEXICON.get(lang, UNCERTAINTY_LEXICON["en"])
    return any(w in lexicon for w in words)

def contains_prompt_injection(text: str) -> bool:
    """Detects untrusted prompt injection patterns."""
    return any(p.search(text) for p in INJECTION_PATTERNS)

def validate_translation_safety(
    source_text: str,
    source_lang: str,
    translated_text: str,
    target_lang: str,
) -> Dict[str, Any]:
    """Performs deterministic clinical semantic safety checks on a translation pair.
    
    Returns:
        is_safe (bool): False if critical clinical meaning was altered or omitted.
        requires_review (bool): True if clinician review is warranted.
        flags (List[str]): List of detected anomalies.
        untrusted_injection (bool): True if prompt injection payload detected.
    """
    flags: List[str] = []
    
    # 1. Negation preservation check
    source_has_neg = has_negation(source_text, source_lang)
    target_has_neg = has_negation(translated_text, target_lang)
    
    if source_has_neg and not target_has_neg:
        flags.append("NEGATION_DROPPED")
    elif not source_has_neg and target_has_neg:
        flags.append("NEGATION_INVENTED")

    # 2. Numeric and Vital measurement preservation check
    source_numbers = set(extract_numbers(source_text))
    target_numbers = set(extract_numbers(translated_text))
    
    # Check if numbers present in source are missing in target
    missing_numbers = source_numbers - target_numbers
    if missing_numbers:
        flags.append(f"NUMERICS_MISSING:{','.join(missing_numbers)}")
    
    # Check if numbers were invented in target
    invented_numbers = target_numbers - source_numbers
    if invented_numbers:
        flags.append(f"NUMERICS_INVENTED:{','.join(invented_numbers)}")

    # 3. Uncertainty preservation check
    source_has_unc = has_uncertainty(source_text, source_lang)
    target_has_unc = has_uncertainty(translated_text, target_lang)
    if source_has_unc and not target_has_unc:
        flags.append("UNCERTAINTY_DROPPED")

    # 4. Prompt injection detection
    is_injection = contains_prompt_injection(source_text) or contains_prompt_injection(translated_text)
    if is_injection:
        flags.append("PROMPT_INJECTION_UNTRUSTED_CONTENT")

    is_safe = ("NEGATION_DROPPED" not in flags) and not any(f.startswith("NUMERICS_MISSING") for f in flags)
    requires_review = len(flags) > 0

    return {
        "is_safe": is_safe,
        "requires_review": requires_review,
        "flags": flags,
        "untrusted_injection": is_injection,
    }
