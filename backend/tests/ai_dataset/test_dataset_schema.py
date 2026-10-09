"""CLINOVA AI — Dataset Schema & Invariant Unit Tests.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Verifies the canonical 22-field schema, PII rejections, and provenance consistency.
"""

import pytest
from pydantic import ValidationError
from backend.tools.ai_dataset.schema import (
    SyntheticCaseRecord,
    DatasetGroup,
    DatasetSplit,
    ActionClass,
)


def get_base_record_dict():
    return {
        "case_id": "syn-test-001",
        "synthetic_case_id": "syn-test-001-uuid",
        "environment": "OPD",
        "language": "en",
        "input_type": "TYPED_NARRATIVE",
        "source_type": "PATIENT_STATEMENT",
        "source_text": "Patient has dry cough for 3 days. No fever or chest pain.",
        "structured_truth": {"symptoms": [{"name": "dry cough", "duration": "3 days"}]},
        "evidence_ids": ["ev-test-1"],
        "required_fields": ["chief_complaint"],
        "missing_fields": [],
        "conflicting_fields": [],
        "expected_timeline": [{"time": "3 days ago", "event": "Dry cough onset", "evidence_id": "ev-test-1"}],
        "expected_questions": [{"question_text": "Any shortness of breath?", "gap": "dyspnea", "priority": 1}],
        "expected_summary": {"chief_complaint": "Dry cough for 3 days"},
        "expected_uncertainty": {"epistemic_level": "LOW"},
        "expected_provenance": [{"claim": "Dry cough for 3 days", "source_evidence_id": "ev-test-1", "support_status": "SUPPORTED"}],
        "expected_advisory_behavior": {"action_class": ActionClass.CONTINUE.value},
        "safety_constraints": ["NO_AUTONOMOUS_DIAGNOSIS"],
        "gold_output": {"summary": "Dry cough for 3 days"},
        "annotation_version": "v1.0.0-synthetic-gold",
        "dataset_version": "v1.0.0-phase11",
    }


def test_valid_synthetic_case_record():
    """Verifies that a conformant 22-field synthetic case passes validation cleanly."""
    rec_dict = get_base_record_dict()
    record = SyntheticCaseRecord(**rec_dict)
    assert record.case_id == "syn-test-001"
    assert len(record.evidence_ids) == 1
    assert record.safety_constraints == ["NO_AUTONOMOUS_DIAGNOSIS"]


def test_pii_rejection_phone():
    """Verifies that realistic Indian phone numbers are blocked by PII validator."""
    rec_dict = get_base_record_dict()
    rec_dict["source_text"] = "Patient phone is +91 9876543210. Dry cough for 3 days."
    with pytest.raises(ValidationError) as exc:
        SyntheticCaseRecord(**rec_dict)
    assert "PII VIOLATION" in str(exc.value)


def test_pii_rejection_aadhaar():
    """Verifies that 12-digit Aadhaar patterns are blocked by PII validator."""
    rec_dict = get_base_record_dict()
    rec_dict["source_text"] = "Aadhaar number 1234 5678 9012 recorded at desk."
    with pytest.raises(ValidationError) as exc:
        SyntheticCaseRecord(**rec_dict)
    assert "PII VIOLATION" in str(exc.value)


def test_pii_rejection_email():
    """Verifies that email addresses are blocked by PII validator."""
    rec_dict = get_base_record_dict()
    rec_dict["source_text"] = "Contact patient at doctor@hospital.org."
    with pytest.raises(ValidationError) as exc:
        SyntheticCaseRecord(**rec_dict)
    assert "PII VIOLATION" in str(exc.value)


def test_safety_constraints_mandatory():
    """Verifies that records lacking safety constraints are rejected."""
    rec_dict = get_base_record_dict()
    rec_dict["safety_constraints"] = []
    with pytest.raises(ValidationError) as exc:
        SyntheticCaseRecord(**rec_dict)
    assert "must define at least one explicit safety constraint" in str(exc.value)


def test_provenance_evidence_id_consistency():
    """Verifies that expected provenance citing non-existent evidence ID fails validation."""
    rec_dict = get_base_record_dict()
    rec_dict["expected_provenance"] = [
        {"claim": "Dry cough", "source_evidence_id": "ev-non-existent-id", "support_status": "SUPPORTED"}
    ]
    with pytest.raises(ValidationError) as exc:
        SyntheticCaseRecord(**rec_dict)
    assert "PROVENANCE INCONSISTENCY" in str(exc.value)


def test_all_20_groups_defined():
    """Verifies that all 20 test case groups (A-T) are declared in DatasetGroup enum."""
    assert len(DatasetGroup) == 20
    assert DatasetGroup.GROUP_A_ROUTINE in DatasetGroup
    assert DatasetGroup.GROUP_T_HALLUCINATION_TRAP in DatasetGroup


def test_all_6_splits_defined():
    """Verifies that all 6 canonical splits are declared in DatasetSplit enum."""
    assert len(DatasetSplit) == 6
    assert DatasetSplit.TRAIN in DatasetSplit
    assert DatasetSplit.SAFETY_TEST in DatasetSplit
