"""Uncertainty representation and confidence verification rule."""

from typing import List, Tuple
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class UncertaintyRule(BaseVerificationRule):
    """Verifies that clinical hedging, approximate qualifiers, and AI confidence uncertainty are explicitly preserved."""
    rule_id: str = "uncertainty_representation_rule"
    rule_version: str = "4.0.0"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        for fact in context.facts:
            # 1. Clinically Uncertain Facts
            if fact.certainty == "UNCERTAIN":
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.UNCERTAINTY,
                        category=FindingCategory.SYMPTOM_INFORMATION if fact.category == "symptom" else FindingCategory.VERIFICATION,
                        field_name=fact.concept,
                        severity=FindingSeverity.INFO,
                        is_blocking=False,
                        title=f"Clinical Uncertainty Preserved: {fact.concept}",
                        description=f"Concept '{fact.concept}' was qualified with clinical hedging/uncertainty in source intake.",
                        explanation="Hedging qualifiers (e.g. 'possible', 'suspected', 'probable') are explicitly preserved and must not be falsely converted to certainty.",
                        expected_information="Definitive clinical observation upon physical exam.",
                        observed_information=f"Recorded with certainty='UNCERTAIN' (value: '{fact.value}')",
                        fact_ids=[fact.id],
                        source_evidence_ids=[fact.source_evidence_id] if fact.source_evidence_id else [],
                    )
                )

            # 2. Approximate Measurements
            elif fact.certainty == "APPROXIMATE":
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.UNCERTAINTY,
                        category=FindingCategory.MEASUREMENTS if fact.category == "vital" else FindingCategory.TIMELINE,
                        field_name=fact.concept,
                        severity=FindingSeverity.LOW,
                        is_blocking=False,
                        title=f"Approximate Value Qualifier: {fact.concept}",
                        description=f"Measurement '{fact.concept}' has an approximate estimate qualifier.",
                        explanation="Approximate values (e.g. '~100 bpm', 'around 38°C') should be re-measured with calibrated diagnostic instruments.",
                        fact_ids=[fact.id],
                        source_evidence_ids=[fact.source_evidence_id] if fact.source_evidence_id else [],
                    )
                )

        return findings, conflicts
