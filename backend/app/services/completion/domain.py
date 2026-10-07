"""Domain entities and dataclasses for Phase 5 Intelligent Completion."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from app.models.completion import (
    GapType,
    QuestionType,
    QuestionStatus,
    AnswerModality,
    StoppingCriterion,
)
from app.models.verification import FindingSeverity, FindingCategory


@dataclass
class InformationGap:
    """Discrete clinical information gap identified from case state and verification runs."""
    gap_id: str
    gap_type: GapType
    target_field: str
    category: str
    severity: FindingSeverity
    description: str
    source_finding_id: Optional[str] = None
    source_conflict_id: Optional[str] = None
    source_fact_id: Optional[str] = None
    is_addressable: bool = True
    resolved: bool = False
    context_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionCandidate:
    """A generated candidate question targeting a specific information gap."""
    candidate_id: str
    target_gap_id: str
    target_gap_type: GapType
    target_field: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[Dict[str, Any]]] = None
    placeholder: Optional[str] = None
    clinical_rationale: str = ""
    base_clinical_utility: float = 0.5
    burden_score: float = 0.1
    is_safety_flag: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrioritizedQuestion:
    """A question candidate that has been validated and scored for execution."""
    candidate: QuestionCandidate
    priority_score: float
    rank: int
    utility_score: float
    gap_severity_weight: float
    burden_penalty: float
    validation_status: str = "VALID"
