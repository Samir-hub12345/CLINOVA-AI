"""Question Validation Engine for Phase 5 Intelligent Completion (Sub-Phase 5.5).

Enforces non-diagnostic clinical boundaries, prevents medication recommendations,
checks for duplicates against interaction history, and validates structural integrity.
"""

import re
from typing import Tuple, List, Optional
from app.models.completion import QuestionType, CompletionQuestion
from app.services.completion.domain import QuestionCandidate
from app.services.completion.history_tracker import InteractionHistoryTracker


class QuestionValidator:
    """Validates candidate questions against safety, clinical, and interaction constraints."""

    # Forbidden diagnostic and prescriptive patterns
    FORBIDDEN_DIAGNOSTIC_PATTERNS = [
        re.compile(r"\b(you have|you don'?t have|you do not have)\s+[a-z]+", re.IGNORECASE),
        re.compile(r"\b(diagnos(is|ed|ing)|we diagnose|our diagnosis)\b", re.IGNORECASE),
        re.compile(r"\b(suffer(ing)? from\s+[a-z]+)\b", re.IGNORECASE),
        re.compile(r"\b(you (likely|probably|definitely) have)\b", re.IGNORECASE),
    ]

    FORBIDDEN_TREATMENT_PATTERNS = [
        re.compile(r"\b(take|prescribe|prescribing|dosage|dose of|\d+\s?mg|\d+\s?tablets?)\b", re.IGNORECASE),
        re.compile(r"\b(antibiotics?|steroids?|paracetamol|ibuprofen|amoxicillin)\b", re.IGNORECASE),
        re.compile(r"\b(start taking|stop taking|apply cream|inject)\b", re.IGNORECASE),
    ]

    FORBIDDEN_DISMISSAL_PATTERNS = [
        re.compile(r"\b(no need to see a doctor|don'?t need a doctor|safe to stay home)\b", re.IGNORECASE),
        re.compile(r"\b(you do not need medical attention|emergency cleared)\b", re.IGNORECASE),
        re.compile(r"\b(admit(ted)? to hospital|discharge from hospital)\b", re.IGNORECASE),
    ]

    def __init__(self):
        self.history_tracker = InteractionHistoryTracker()

    def validate_candidate(
        self,
        candidate: QuestionCandidate,
        existing_questions: List[CompletionQuestion],
    ) -> Tuple[bool, str]:
        """Validates a single candidate question. Returns (is_valid, rejection_reason)."""
        text = candidate.question_text.strip()

        # 1. Basic Content Integrity
        if not text or len(text) < 10:
            return False, "Question text is too short or empty."

        if not candidate.clinical_rationale or len(candidate.clinical_rationale.strip()) < 5:
            return False, "Clinical rationale is missing or inadequate."

        # 2. Strict Non-Diagnostic Boundary Checks
        for pat in self.FORBIDDEN_DIAGNOSTIC_PATTERNS:
            if pat.search(text):
                return False, f"Question violates non-diagnostic boundary: matched '{pat.pattern}'."

        for pat in self.FORBIDDEN_TREATMENT_PATTERNS:
            if pat.search(text):
                return False, f"Question violates non-treatment boundary: matched '{pat.pattern}'."

        for pat in self.FORBIDDEN_DISMISSAL_PATTERNS:
            if pat.search(text):
                return False, f"Question violates non-dismissal safety boundary: matched '{pat.pattern}'."

        # 3. Choice Structure Validation
        if candidate.question_type in (QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE):
            if not candidate.options or len(candidate.options) < 2:
                return False, "Choice question must have at least 2 valid options."
            for opt in candidate.options:
                if not isinstance(opt, dict) or "label" not in opt or "value" not in opt:
                    return False, "Choice option must contain 'label' and 'value' keys."

        # 4. Redundancy & Duplicate Checks
        if self.history_tracker.is_duplicate_question(text, existing_questions):
            return False, "Question is duplicate of a previously presented question."

        if self.history_tracker.is_field_exhausted(candidate.target_field, existing_questions):
            return False, f"Target field '{candidate.target_field}' has reached maximum interview attempts."

        return True, "VALID"
