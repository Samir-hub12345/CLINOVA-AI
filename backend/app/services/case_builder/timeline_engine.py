"""Timeline engine for Clinova AI.

Constructs chronological clinical event sequences from patient narratives,
consultation notes, and multimodal evidence.
"""

import re
import json
from typing import List, Dict, Any, Optional
from app.models.case_evidence import CaseEvidence, EvidenceSourceType
from app.models.canonical_case import TemporalStatus, FactCertainty


class CandidateTimelineEvent:
    def __init__(
        self,
        event_type: str,
        description: str,
        relative_time: Optional[str] = None,
        approximate_date: Optional[str] = None,
        temporal_status: str = TemporalStatus.CURRENT.value,
        source_evidence_id: Optional[str] = None,
        attribution: str = "PATIENT_REPORTED",
        certainty: str = FactCertainty.REPORTED.value,
        order_index: int = 0,
    ):
        self.event_type = event_type
        self.description = description
        self.relative_time = relative_time
        self.approximate_date = approximate_date
        self.temporal_status = temporal_status
        self.source_evidence_id = source_evidence_id
        self.attribution = attribution
        self.certainty = certainty
        self.order_index = order_index


class TimelineEngine:
    """Builds an ordered sequence of timeline events from multimodal evidence items."""

    # Time weight for sorting
    TIME_WEIGHTS = {
        "past": -100,
        "years ago": -90,
        "months ago": -80,
        "weeks ago": -70,
        "day 1": 10,
        "day 2": 20,
        "day 3": 30,
        "day 4": 40,
        "day 5": 50,
        "3 days ago": 10,
        "2 days ago": 20,
        "yesterday": 30,
        "last night": 35,
        "today": 50,
        "day 3 (today)": 50,
        "current intake": 60,
    }

    def __init__(self):
        pass

    def _determine_attribution(self, source_type: Any) -> str:
        src_str = str(getattr(source_type, "value", source_type)).lower()
        if "clinician" in src_str or "staff" in src_str:
            return "CLINICIAN_ENTERED"
        elif "device" in src_str or "monitor" in src_str:
            return "DEVICE_MEASURED"
        elif "document" in src_str or "ocr" in src_str or "lab" in src_str:
            return "DOCUMENT_EXTRACTED"
        return "PATIENT_REPORTED"

    def _score_time_token(self, time_str: str) -> int:
        clean = time_str.lower().strip()
        for token, weight in self.TIME_WEIGHTS.items():
            if token in clean:
                return weight
        # Match "X days ago"
        m = re.search(r"(\d+)\s*days?\s*ago", clean)
        if m:
            days = int(m.group(1))
            return 50 - days * 10
        return 0

    def extract_timeline_events(self, evidence_list: List[CaseEvidence]) -> List[CandidateTimelineEvent]:
        raw_events: List[CandidateTimelineEvent] = []

        for ev in evidence_list:
            attribution = self._determine_attribution(ev.source_type)
            text = (ev.normalized_value or ev.raw_value or "").strip()
            if not text:
                continue

            # 1. Check if the text is JSON list of events (from Phase 1 / demo cases)
            if text.startswith("[") and text.endswith("]"):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, dict) and "description" in item:
                                rel_time = item.get("day") or item.get("time") or item.get("relative_time")
                                raw_events.append(
                                    CandidateTimelineEvent(
                                        event_type="symptom_onset",
                                        description=item["description"],
                                        relative_time=rel_time,
                                        temporal_status=TemporalStatus.CURRENT.value if "today" in str(rel_time).lower() else TemporalStatus.HISTORICAL.value,
                                        source_evidence_id=ev.id,
                                        attribution=attribution,
                                        certainty=FactCertainty.REPORTED.value,
                                    )
                                )
                        continue
                except Exception:
                    pass

            # 2. Extract structured narrative patterns like "Day X: ..." or "Since yesterday: ..."
            lines = text.splitlines()
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue

                # Pattern: "Day 1 - Chills and high fever" or "Day 1: Chills"
                day_match = re.match(r"^(Day\s+\d+(?:\s*\([^)]+\))?|Yesterday|Today|Last night)[:\-–\s]+(.+)$", line_clean, re.IGNORECASE)
                if day_match:
                    rel_time = day_match.group(1).strip()
                    desc = day_match.group(2).strip()
                    raw_events.append(
                        CandidateTimelineEvent(
                            event_type="symptom_progression",
                            description=desc,
                            relative_time=rel_time,
                            temporal_status=TemporalStatus.CURRENT.value if "today" in rel_time.lower() else TemporalStatus.HISTORICAL.value,
                            source_evidence_id=ev.id,
                            attribution=attribution,
                            certainty=FactCertainty.REPORTED.value,
                        )
                    )

            # 3. If no structured day lines, extract onset markers
            onset_matches = list(re.finditer(
                r"\b(started|onset|began|since|for)\s+([a-zA-Z0-9\s]+?)(?:,|\.|$|and\s+has)",
                text,
                re.IGNORECASE,
            ))
            for om in onset_matches:
                span = om.group(0).strip()
                rel = om.group(2).strip()
                # Exclude long or spurious matches
                if len(rel.split()) <= 4:
                    raw_events.append(
                        CandidateTimelineEvent(
                            event_type="symptom_onset",
                            description=span,
                            relative_time=rel,
                            temporal_status=TemporalStatus.CURRENT.value,
                            source_evidence_id=ev.id,
                            attribution=attribution,
                            certainty=FactCertainty.REPORTED.value,
                        )
                    )

        # De-duplicate events with identical description
        deduped: List[CandidateTimelineEvent] = []
        seen_descriptions = set()
        for ev in raw_events:
            key = ev.description.lower().strip()
            if key not in seen_descriptions:
                seen_descriptions.add(key)
                deduped.append(ev)

        # Sort chronologically using time scores
        deduped.sort(key=lambda x: self._score_time_token(x.relative_time or ""))

        # Assign sequential order_index
        for idx, event in enumerate(deduped):
            event.order_index = idx + 1

        return deduped
