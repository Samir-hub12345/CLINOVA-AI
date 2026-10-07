"""Verification context definition for Phase 4 Clinical Verification Engine."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence
from app.models.canonical_case import CaseSnapshot, CanonicalFact, TimelineEvent


@dataclass
class VerificationContext:
    """Encapsulates the complete clinical case package loaded for verification."""
    case: TriageCase
    snapshot: Optional[CaseSnapshot]
    case_version: int
    facts: List[CanonicalFact] = field(default_factory=list)
    evidence_items: List[CaseEvidence] = field(default_factory=list)
    timeline_events: List[TimelineEvent] = field(default_factory=list)
    previous_findings: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def case_id(self) -> str:
        return self.case.id

    @property
    def patient_id(self) -> Optional[str]:
        return self.case.patient_id

    @property
    def facts_by_category(self) -> Dict[str, List[CanonicalFact]]:
        cats: Dict[str, List[CanonicalFact]] = {}
        for f in self.facts:
            cats.setdefault(f.category, []).append(f)
        return cats

    @property
    def evidence_by_id(self) -> Dict[str, CaseEvidence]:
        return {e.id: e for e in self.evidence_items}

    @property
    def evidence_by_field(self) -> Dict[str, List[CaseEvidence]]:
        fields: Dict[str, List[CaseEvidence]] = {}
        for e in self.evidence_items:
            fields.setdefault(e.canonical_field, []).append(e)
        return fields
