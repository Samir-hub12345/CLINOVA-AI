"""Information Gap Engine for Phase 5 Intelligent Completion (Sub-Phase 5.3).

Reads case state, verification findings, cross-source conflicts, canonical facts,
and interaction history to detect, classify, and filter actionable information gaps.
"""

from typing import List, Optional, Dict, Any, Set
from app.models.completion import (
    GapType,
    CompletionQuestion,
)
from app.models.verification import (
    VerificationRun,
    VerificationFinding,
    VerificationConflict,
    FindingSeverity,
    FindingType,
    FindingStatus,
)
from app.models.canonical_case import (
    CaseSnapshot,
    CanonicalFact,
    TimelineEvent,
    FactCertainty,
)
from app.services.completion.domain import InformationGap
from app.services.completion.history_tracker import InteractionHistoryTracker


class InformationGapEngine:
    """Detects, classifies, and filters actionable information gaps in a verified case."""

    def __init__(self):
        self.history_tracker = InteractionHistoryTracker()

    def identify_gaps(
        self,
        snapshot: Optional[CaseSnapshot],
        verification_run: Optional[VerificationRun],
        session_questions: List[CompletionQuestion],
    ) -> List[InformationGap]:
        """Identifies all candidate information gaps and filters out already-queried ones."""
        raw_gaps: List[InformationGap] = []

        # Track already answered and exhausted fields
        answered_fields = self.history_tracker.get_answered_target_fields(session_questions)

        # 1. Gaps from Phase 4 Verification Findings
        if verification_run and verification_run.findings:
            for finding in verification_run.findings:
                if finding.status not in (
                    FindingStatus.UNRESOLVED.value,
                    "UNRESOLVED",
                ):
                    continue

                if finding.finding_type == FindingType.COMPLETENESS.value:
                    field_name = finding.field_name or "unknown_field"
                    severity = self._map_severity(finding.severity)
                    if field_name == "symptom_duration":
                        severity = FindingSeverity.HIGH
                    raw_gaps.append(
                        InformationGap(
                            gap_id=f"gap_comp_{finding.id}",
                            gap_type=GapType.MISSING_REQUIRED_FIELD,
                            target_field=field_name,
                            category=finding.category,
                            severity=severity,
                            description=finding.description or f"Missing {field_name}",
                            source_finding_id=finding.id,
                            is_addressable=self._is_patient_addressable(field_name),
                            resolved=False,
                            context_data={
                                "expected_information": finding.expected_information,
                                "observed_information": finding.observed_information,
                            },
                        )
                    )
                elif finding.finding_type == FindingType.UNCERTAINTY.value:
                    field_name = finding.field_name or "uncertain_symptom"
                    severity = self._map_severity(finding.severity)
                    raw_gaps.append(
                        InformationGap(
                            gap_id=f"gap_unc_{finding.id}",
                            gap_type=GapType.UNCERTAIN_FACT,
                            target_field=field_name,
                            category=finding.category,
                            severity=severity,
                            description=finding.description or f"Uncertain {field_name}",
                            source_finding_id=finding.id,
                            is_addressable=True,
                            resolved=False,
                            context_data={
                                "observed_information": finding.observed_information,
                            },
                        )
                    )

        # 2. Gaps from Phase 4 Verification Conflicts
        if verification_run and verification_run.conflicts:
            for conflict in verification_run.conflicts:
                if conflict.resolution_state in ("RESOLVED", "RESOLVED_BY_HUMAN_VERIFICATION"):
                    continue

                field_name = conflict.field_name or "conflicting_field"
                severity = self._map_severity(conflict.severity)
                raw_gaps.append(
                    InformationGap(
                        gap_id=f"gap_conf_{conflict.id}",
                        gap_type=GapType.UNRESOLVED_CONFLICT,
                        target_field=field_name,
                        category="CONFLICT",
                        severity=severity,
                        description=f"Discrepancy in {field_name}: '{conflict.source_a_value}' vs '{conflict.source_b_value}'",
                        source_conflict_id=conflict.id,
                        is_addressable=True,
                        resolved=False,
                        context_data={
                            "source_a_value": conflict.source_a_value,
                            "source_b_value": conflict.source_b_value,
                            "source_a_type": conflict.source_a_type,
                            "source_b_type": conflict.source_b_type,
                        },
                    )
                )

        # 3. Gaps from Snapshot Facts (Hedging, Approximate, or Missing Core Concept)
        if snapshot and snapshot.facts:
            for fact in snapshot.facts:
                if fact.certainty in (FactCertainty.UNCERTAIN.value, FactCertainty.APPROXIMATE.value):
                    target_field = f"{fact.category.lower()}_{fact.concept.lower().replace(' ', '_')}"
                    # Avoid duplicating finding gap
                    if not any(g.target_field == target_field for g in raw_gaps):
                        raw_gaps.append(
                            InformationGap(
                                gap_id=f"gap_fact_{fact.id}",
                                gap_type=GapType.UNCERTAIN_FACT,
                                target_field=target_field,
                                category=fact.category,
                                severity=FindingSeverity.MEDIUM,
                                description=f"Uncertain observation: '{fact.summary}' ({fact.certainty})",
                                source_fact_id=fact.id,
                                is_addressable=True,
                                resolved=False,
                                context_data={
                                    "fact_summary": fact.summary,
                                    "concept": fact.concept,
                                    "certainty": fact.certainty,
                                },
                            )
                        )

        # 4. Contextual & Progression Gaps (if baseline exists but trajectory missing)
        if snapshot:
            case_data = snapshot.case_data or {}
            # If timeline is sparse (less than 2 events)
            events_count = len(snapshot.timeline_events) if snapshot.timeline_events else 0
            if events_count < 2 and not any(g.target_field == "symptom_progression" for g in raw_gaps):
                raw_gaps.append(
                    InformationGap(
                        gap_id="gap_timeline_progression",
                        gap_type=GapType.INCOMPLETE_TIMELINE,
                        target_field="symptom_progression",
                        category="TIMELINE",
                        severity=FindingSeverity.LOW,
                        description="Sparse symptom timeline: trajectory from onset to present unrecorded.",
                        is_addressable=True,
                        resolved=False,
                    )
                )

        # 5. Filter gaps based on interaction history
        actionable_gaps: List[InformationGap] = []
        seen_fields: Set[str] = set()

        for gap in raw_gaps:
            # Skip if not patient addressable
            if not gap.is_addressable:
                continue

            # Skip if already answered
            if gap.target_field in answered_fields:
                continue

            # Skip if exhausted (e.g. asked twice without answer)
            if self.history_tracker.is_field_exhausted(gap.target_field, session_questions):
                continue

            # Deduplicate by target_field
            if gap.target_field in seen_fields:
                continue

            seen_fields.add(gap.target_field)
            actionable_gaps.append(gap)

        return actionable_gaps

    def _is_patient_addressable(self, field_name: str) -> bool:
        """Determines if a field can be reasonably answered by a lay patient."""
        # Unaddressable without laboratory / professional instrumentation
        unaddressable = {
            "laboratory_results",
            "imaging_study",
            "ecg_interpretation",
            "histopathology",
            "arterial_blood_gas",
        }
        return field_name.lower() not in unaddressable

    def _map_severity(self, severity_str: str) -> FindingSeverity:
        try:
            return FindingSeverity(severity_str.upper())
        except Exception:
            return FindingSeverity.MEDIUM
