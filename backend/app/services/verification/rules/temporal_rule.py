"""Temporal consistency and timeline integrity verification rule."""

import re
from typing import List, Tuple, Optional
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class TemporalConsistencyRule(BaseVerificationRule):
    """Verifies chronological coherence across timeline events, medication dates, and symptom onset."""
    rule_id: str = "temporal_consistency_rule"
    rule_version: str = "4.0.0"

    def _extract_day_number(self, relative_str: Optional[str]) -> Optional[int]:
        if not relative_str:
            return None
        m = re.search(r"day\s*(\d+)", relative_str, re.IGNORECASE)
        if m:
            return int(m.group(1))
        if "yesterday" in relative_str.lower():
            return -1
        if "today" in relative_str.lower():
            return 0
        return None

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        timeline_events = sorted(context.timeline_events, key=lambda x: x.order_index)

        # 1. Check sequence ordering and relative day progression
        for i in range(len(timeline_events) - 1):
            curr_ev = timeline_events[i]
            next_ev = timeline_events[i + 1]

            curr_day = self._extract_day_number(curr_ev.relative_time)
            next_day = self._extract_day_number(next_ev.relative_time)

            if curr_day is not None and next_day is not None:
                # If current day is greater than next day while order_index is smaller -> inverted chronology
                if curr_day > next_day and curr_ev.order_index < next_ev.order_index:
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.TEMPORAL,
                            category=FindingCategory.TIMELINE,
                            field_name="event_chronology",
                            severity=FindingSeverity.HIGH,
                            is_blocking=False,
                            title=f"Inverted Timeline Chronology: Event {curr_ev.order_index} vs {next_ev.order_index}",
                            description=f"Event '{curr_ev.description}' (relative time: '{curr_ev.relative_time}') appears ordered before Event '{next_ev.description}' (relative time: '{next_ev.relative_time}').",
                            explanation="Chronological order requires antecedent events to have smaller relative elapsed day offsets than subsequent events.",
                            expected_information=f"Chronological progression: Day {curr_day} <= Day {next_day}.",
                            observed_information=f"Day {curr_day} preceded Day {next_day} in timeline sequence.",
                            timeline_event_ids=[curr_ev.id, next_ev.id],
                            source_evidence_ids=[ev_id for ev_id in [curr_ev.source_evidence_id, next_ev.source_evidence_id] if ev_id],
                        )
                    )

        # 2. Check for conflicting onset statements across facts
        onset_facts = [f for f in context.facts if f.onset_approximate or f.duration]
        onsets_by_concept = {}
        for f in onset_facts:
            token = f"{f.onset_approximate or ''} {f.duration or ''}".strip().lower()
            if token:
                onsets_by_concept.setdefault(f.concept.lower(), []).append((f, token))

        for concept_name, f_list in onsets_by_concept.items():
            if len(f_list) > 1:
                unique_tokens = {token for _, token in f_list}
                if len(unique_tokens) > 1:
                    facts_involved = [f for f, _ in f_list]
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.TEMPORAL,
                            category=FindingCategory.SYMPTOM_INFORMATION,
                            field_name=f"{concept_name}_onset",
                            severity=FindingSeverity.MEDIUM,
                            is_blocking=False,
                            title=f"Conflicting Onset Timing on {concept_name.capitalize()}",
                            description=f"Multiple onset/duration values recorded for '{concept_name}': {list(unique_tokens)}.",
                            explanation="Varying reported onset intervals create clinical uncertainty regarding acute vs subacute presentation.",
                            expected_information="Single consistent onset duration.",
                            observed_information=f"Recorded: {list(unique_tokens)}",
                            fact_ids=[f.id for f in facts_involved],
                            source_evidence_ids=[f.source_evidence_id for f in facts_involved if f.source_evidence_id],
                        )
                    )

        # 3. Check for Medication Timeline Contradictions
        # (e.g., 'stopped medication' recorded before 'started medication')
        med_events = [ev for ev in timeline_events if "medication" in ev.event_type.lower()]
        stopped_events = [ev for ev in med_events if "stop" in ev.description.lower() or "discontinued" in ev.description.lower()]
        started_events = [ev for ev in med_events if "start" in ev.description.lower() or "prescribed" in ev.description.lower()]

        for st_ev in stopped_events:
            for sta_ev in started_events:
                if st_ev.order_index < sta_ev.order_index:
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.TEMPORAL,
                            category=FindingCategory.TIMELINE,
                            field_name="medication_lifecycle",
                            severity=FindingSeverity.HIGH,
                            is_blocking=False,
                            title="Medication Discontinuation Precedes Initiation",
                            description=f"Medication discontinuation '{st_ev.description}' is sequenced prior to initiation '{sta_ev.description}'.",
                            explanation="Medication lifecycle records cannot document discontinuation prior to initial prescription or intake.",
                            expected_information="Medication start before medication stop.",
                            observed_information=f"Stop event index {st_ev.order_index} precedes start event index {sta_ev.order_index}.",
                            timeline_event_ids=[st_ev.id, sta_ev.id],
                        )
                    )

        return findings, conflicts
