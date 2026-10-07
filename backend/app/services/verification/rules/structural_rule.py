"""Structural integrity verification rule."""

from datetime import datetime, timezone
from typing import List, Tuple
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class StructuralIntegrityRule(BaseVerificationRule):
    """Verifies fundamental case existence, patient linkage, and foreign key referential integrity."""
    rule_id: str = "structural_integrity_rule"
    rule_version: str = "4.0.0"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []
        now = datetime.now(timezone.utc)

        # 1. Check patient association
        if not context.case.patient_id:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.STRUCTURAL,
                    category=FindingCategory.IDENTITY,
                    field_name="patient_id",
                    severity=FindingSeverity.BLOCKING,
                    is_blocking=True,
                    title="Missing Patient Identity Association",
                    description="The case is not linked to a valid patient record.",
                    explanation="A canonical triage case must be linked to a known patient record before professional clinical review can proceed.",
                    expected_information="Valid patient UUID string.",
                    observed_information="null / empty",
                )
            )

        # 2. Check snapshot association
        if not context.snapshot:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.STRUCTURAL,
                    category=FindingCategory.VERIFICATION,
                    field_name="case_snapshot",
                    severity=FindingSeverity.BLOCKING,
                    is_blocking=True,
                    title="Missing Canonical Case Snapshot",
                    description=f"No compiled snapshot exists for case {context.case_id} at version {context.case_version}.",
                    explanation="Verification requires a compiled Phase 3 Canonical Case Snapshot. Please execute case build first.",
                    expected_information="Active CaseSnapshot record.",
                    observed_information="null",
                )
            )

        # 3. Check evidence ID duplication
        ev_ids = [e.id for e in context.evidence_items]
        if len(ev_ids) != len(set(ev_ids)):
            duplicates = [x for x in ev_ids if ev_ids.count(x) > 1]
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.STRUCTURAL,
                    category=FindingCategory.SOURCE_METADATA,
                    field_name="evidence_id",
                    severity=FindingSeverity.HIGH,
                    is_blocking=False,
                    title="Duplicate Evidence Identifier Detected",
                    description=f"Evidence collection contains duplicate identifiers: {set(duplicates)}",
                    explanation="Evidence items must have unique UUIDs to maintain tamper-proof provenance graphs.",
                    expected_information="Unique evidence IDs.",
                    observed_information=f"Duplicate IDs: {set(duplicates)}",
                )
            )

        # 4. Check fact-to-evidence reference resolution
        evidence_ids = set(context.evidence_by_id.keys())
        for fact in context.facts:
            if fact.source_evidence_id and fact.source_evidence_id not in evidence_ids:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.STRUCTURAL,
                        category=FindingCategory.SOURCE_METADATA,
                        field_name="source_evidence_id",
                        severity=FindingSeverity.HIGH,
                        is_blocking=False,
                        title=f"Unresolved Evidence Reference on Fact: {fact.concept}",
                        description=f"Fact references evidence ID '{fact.source_evidence_id}' which does not exist in the case evidence collection.",
                        explanation="Every derived fact must refer to an existent CaseEvidence entity to ensure complete auditability.",
                        expected_information="Existent CaseEvidence ID.",
                        observed_information=f"Missing evidence ID: {fact.source_evidence_id}",
                        fact_ids=[fact.id],
                    )
                )

        # 5. Check timeline event reference resolution
        for ev in context.timeline_events:
            if ev.source_evidence_id and ev.source_evidence_id not in evidence_ids:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.STRUCTURAL,
                        category=FindingCategory.TIMELINE,
                        field_name="source_evidence_id",
                        severity=FindingSeverity.MEDIUM,
                        is_blocking=False,
                        title=f"Unresolved Timeline Evidence Reference: {ev.event_type}",
                        description=f"Timeline event references missing evidence item '{ev.source_evidence_id}'.",
                        explanation="Timeline events should be traceable back to valid intake evidence.",
                        timeline_event_ids=[ev.id],
                    )
                )

        # 6. Check for future timestamps on evidence
        for ev in context.evidence_items:
            if ev.observed_at:
                obs_at = ev.observed_at.replace(tzinfo=timezone.utc) if ev.observed_at.tzinfo is None else ev.observed_at
                if obs_at > now:
                    findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.STRUCTURAL,
                        category=FindingCategory.SOURCE_METADATA,
                        field_name="observed_at",
                        severity=FindingSeverity.MEDIUM,
                        is_blocking=False,
                        title=f"Future Timestamp on Evidence Item: {ev.canonical_field}",
                        description=f"Evidence observed_at timestamp ({ev.observed_at.isoformat()}) is in the future.",
                        explanation="Clinical evidence cannot have observation timestamps occurring after current wall-clock time.",
                        source_evidence_ids=[ev.id],
                        expected_information="Timestamp <= current time.",
                        observed_information=ev.observed_at.isoformat(),
                    )
                )

        return findings, conflicts
