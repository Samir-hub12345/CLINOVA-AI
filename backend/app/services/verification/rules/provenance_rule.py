"""Source provenance and fact traceability verification rule."""

from typing import List, Tuple
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class ProvenanceRule(BaseVerificationRule):
    """Verifies that every canonical fact can be traced back to raw source evidence and verifiable spans."""
    rule_id: str = "source_provenance_rule"
    rule_version: str = "4.0.0"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        ev_map = context.evidence_by_id

        for fact in context.facts:
            # 1. Missing source evidence ID
            if not fact.source_evidence_id:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.PROVENANCE,
                        category=FindingCategory.SOURCE_METADATA,
                        field_name=fact.concept,
                        severity=FindingSeverity.HIGH,
                        is_blocking=False,
                        title=f"Untraceable Clinical Fact: {fact.concept}",
                        description=f"Canonical fact '{fact.concept}' has no linked source_evidence_id.",
                        explanation="Every clinical fact in the canonical record must anchor to a concrete multimodal evidence item to prevent hallucination.",
                        expected_information="Valid source_evidence_id linking to CaseEvidence.",
                        observed_information="source_evidence_id is null",
                        fact_ids=[fact.id],
                    )
                )
                continue

            source_ev = ev_map.get(fact.source_evidence_id)
            if not source_ev:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.PROVENANCE,
                        category=FindingCategory.SOURCE_METADATA,
                        field_name=fact.concept,
                        severity=FindingSeverity.HIGH,
                        is_blocking=False,
                        title=f"Broken Evidence Provenance Link: {fact.concept}",
                        description=f"Fact references evidence '{fact.source_evidence_id}', but the evidence record was not found.",
                        explanation="The provenance link points to a non-existent or deleted evidence entity.",
                        fact_ids=[fact.id],
                    )
                )
                continue

            # 2. Missing source span
            if not fact.source_span or not fact.source_span.strip():
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.PROVENANCE,
                        category=FindingCategory.SOURCE_METADATA,
                        field_name=fact.concept,
                        severity=FindingSeverity.MEDIUM,
                        is_blocking=False,
                        title=f"Missing Source Span on Fact: {fact.concept}",
                        description=f"Fact '{fact.concept}' has evidence linkage but lacks the exact text substring span.",
                        explanation="Clinova AI requires character-level source span grounding for anti-hallucination verification.",
                        expected_information="Non-empty source_span substring.",
                        observed_information="source_span is empty or null",
                        fact_ids=[fact.id],
                        source_evidence_ids=[source_ev.id],
                    )
                )
            else:
                # 3. Grounding validation: Does source_span exist in source evidence raw or normalized text?
                raw_text = (source_ev.raw_value or "").lower()
                norm_text = (source_ev.normalized_value or "").lower()
                span_lower = fact.source_span.lower().strip()

                if span_lower not in raw_text and span_lower not in norm_text:
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.PROVENANCE,
                            category=FindingCategory.SOURCE_METADATA,
                            field_name=fact.concept,
                            severity=FindingSeverity.HIGH,
                            is_blocking=False,
                            title=f"Ungrounded Source Span on Fact: {fact.concept}",
                            description=f"Source span '{fact.source_span}' does not appear in linked evidence text.",
                            explanation="Grounded anti-hallucination checks failed: candidate fact span cannot be matched inside source text.",
                            expected_information=f"Substring '{fact.source_span}' inside source evidence.",
                            observed_information=f"Span '{fact.source_span}' absent from raw evidence of length {len(raw_text)}.",
                            fact_ids=[fact.id],
                            source_evidence_ids=[source_ev.id],
                        )
                    )

            # 4. OCR Document Linkage Check
            if source_ev.source_type.value in ("ocr_derived", "document_derived"):
                if not source_ev.source_reference:
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.PROVENANCE,
                            category=FindingCategory.DOCUMENTS,
                            field_name=fact.concept,
                            severity=FindingSeverity.LOW,
                            is_blocking=False,
                            title=f"OCR Fact Lacks Document File Reference: {fact.concept}",
                            description=f"Evidence for '{fact.concept}' is OCR-derived but has no linked document file path or artifact ID.",
                            explanation="Scanned document evidence should link to the underlying stored PDF/image artifact for audit verification.",
                            fact_ids=[fact.id],
                            source_evidence_ids=[source_ev.id],
                        )
                    )

        return findings, conflicts
