"""CLINOVA AI — Data Quality Audit Test Suite.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Verifies programmatic data quality audit across all generated synthetic splits in data/synthetic/.
"""

from pathlib import Path
from backend.tools.ai_dataset.audit import DataQualityAudit


def test_synthetic_data_quality_audit():
    """Runs data quality audit over data/synthetic/ and asserts zero critical defects."""
    repo_root = Path(__file__).resolve().parents[3]
    dataset_dir = repo_root / "data" / "synthetic"

    report = DataQualityAudit.audit_splits(dataset_dir)

    assert report.total_records_audited > 0, "No records found to audit."
    assert report.critical_issues_count == 0, f"Critical issues detected: {report.issues}"
    assert report.high_issues_count == 0, f"High issues detected: {report.issues}"
    assert report.zero_pii_confirmed is True, "PII detected in synthetic records!"
    assert report.zero_leakage_confirmed is True, "Data leakage detected across splits!"
    assert report.zero_autonomous_diagnoses_confirmed is True, "Autonomous diagnosis claims detected!"
    assert report.is_audit_passed is True, "Data quality audit failed overall."

    # Verify all 6 splits exist
    expected_splits = {"train", "validation", "test", "adversarial_test", "multilingual_test", "safety_test"}
    assert set(report.split_record_counts.keys()) == expected_splits
