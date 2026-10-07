"""Safety, Failure Recovery, and Abstention Guard for Phase 5 Intelligent Completion (Sub-Phase 5.13).

Guarantees strict non-diagnostic boundary enforcement, zero-cost offline deterministic execution,
red-flag symptom preservation for clinician review, and graceful failure containment.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from app.models.completion import (
    CompletionSession,
    CompletionSessionStatus,
    CompletionQuestion,
)

logger = logging.getLogger("clinova.completion.safety")


class CompletionSafetyGuard:
    """Enforces non-negotiable clinical safety boundaries and error containment."""

    # Red flag keywords to detect and preserve without autonomous triage
    RED_FLAG_PATTERNS = [
        re.compile(r"\b(crushing chest pain|radiating to arm|radiating to jaw)\b", re.IGNORECASE),
        re.compile(r"\b(severe shortness of breath|cannot breathe|stridor)\b", re.IGNORECASE),
        re.compile(r"\b(sudden weakness|facial droop|slurred speech)\b", re.IGNORECASE),
        re.compile(r"\b(unconscious|unresponsive|cyanosis)\b", re.IGNORECASE),
        re.compile(r"\b(coughing blood|vomiting blood|massive bleeding)\b", re.IGNORECASE),
    ]

    def check_for_red_flags(self, answer_text: str) -> Optional[str]:
        """Detects whether an answer contains severe red flag symptoms that must be surfaced."""
        for pat in self.RED_FLAG_PATTERNS:
            match = pat.search(answer_text)
            if match:
                return f"Red flag clinical symptom detected: '{match.group(0)}'. Surfaced for immediate clinical review."
        return None

    def enforce_non_diagnostic_boundary(self, text: str) -> None:
        """Raises ValueError if any diagnostic or prescriptive language is detected."""
        diagnostic_checks = [
            (r"\b(you have|you do not have|you don'?t have)\s+[a-z]+", "Diagnostic assertion"),
            (r"\b(diagnos(is|ed|ing)|we diagnose|our diagnosis)\b", "Diagnostic assertion"),
            (r"\b(suffer(ing)? from\s+[a-z]+)\b", "Diagnostic assertion"),
            (r"\b(take \d+\s?mg|prescribe|prescribing|dosage|dose of|\d+\s?tablets?)\b", "Prescriptive treatment recommendation"),
            (r"\b(start taking|stop taking|apply cream|inject)\b", "Prescriptive treatment recommendation"),
            (r"\b(antibiotics?|steroids?|paracetamol|ibuprofen|amoxicillin)\b", "Medication recommendation"),
            (r"\b(no need to see a doctor|don'?t need a doctor|safe to stay home)\b", "Autonomous discharge advice"),
            (r"\b(you do not need medical attention|emergency cleared)\b", "Autonomous discharge advice"),
            (r"\b(admit(ted)?(\s+\w+)?\s+to\s+(the\s+)?hospital|should be admitted|must be admitted)\b", "Autonomous admission recommendation"),
            (r"\b(discharge(d)?(\s+\w+)?\s+from\s+(the\s+)?hospital|should be discharged)\b", "Autonomous discharge recommendation"),
        ]
        for pattern, label in diagnostic_checks:
            if re.search(pattern, text, re.IGNORECASE):
                logger.critical(f"NON-DIAGNOSTIC BOUNDARY BREACH ATTEMPT: {label} in text: '{text}'")
                raise ValueError(f"Safety boundary breach: {label} is strictly forbidden in Phase 5.")

    def handle_session_failure(
        self,
        session: CompletionSession,
        error: Exception,
    ) -> None:
        """Safely transitions a session to FAILED state without corrupting historical records."""
        logger.error(f"Completion session {session.id} encountered error: {str(error)}", exc_info=True)
        session.status = CompletionSessionStatus.FAILED.value
        session.stopping_reason = f"Execution error: {str(error)}"
