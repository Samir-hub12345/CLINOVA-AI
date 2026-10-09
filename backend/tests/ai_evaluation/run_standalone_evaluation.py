"""CLINOVA AI — Standalone AI Evaluation & Dataset Test Runner.

Executes all Phase 11 dataset, schema, audit, metric, and evaluator tests
directly using Python's standard library.
"""

import sys
from pathlib import Path

# Add backend directory and repo root to sys.path
backend_dir = Path(__file__).resolve().parents[2]
repo_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from backend.tests.ai_dataset.test_dataset_schema import (
    test_valid_synthetic_case_record,
    test_pii_rejection_phone,
    test_pii_rejection_aadhaar,
    test_pii_rejection_email,
    test_safety_constraints_mandatory,
    test_provenance_evidence_id_consistency,
    test_all_20_groups_defined,
    test_all_6_splits_defined,
)
from backend.tests.ai_dataset.test_data_quality_audit import (
    test_synthetic_data_quality_audit,
)
from backend.tests.ai_evaluation.test_eval_metrics import (
    test_timeline_contracts,
    test_entity_metrics_exact_match,
    test_entity_metrics_partial,
    test_timeline_ordering_accuracy,
    test_grounding_metrics_supported_and_phantom,
    test_error_taxonomy_classification,
)
from backend.tests.ai_evaluation.test_evaluator_harness import (
    test_evaluator_full_benchmark,
    test_prompt_injection_case_evaluation,
    test_multilingual_odia_idiom_evaluation,
)


def main():
    print("=" * 75)
    print("CLINOVA AI — PHASE 11 DATASET & EVALUATION TEST RUNNER")
    print("=" * 75)

    test_cases = [
        ("dataset_schema_valid_record", test_valid_synthetic_case_record),
        ("dataset_schema_pii_phone", test_pii_rejection_phone),
        ("dataset_schema_pii_aadhaar", test_pii_rejection_aadhaar),
        ("dataset_schema_pii_email", test_pii_rejection_email),
        ("dataset_schema_safety_mandatory", test_safety_constraints_mandatory),
        ("dataset_schema_provenance_consistency", test_provenance_evidence_id_consistency),
        ("dataset_schema_all_20_groups", test_all_20_groups_defined),
        ("dataset_schema_all_6_splits", test_all_6_splits_defined),
        ("data_quality_audit_suite", test_synthetic_data_quality_audit),
        ("eval_timeline_contracts", test_timeline_contracts),
        ("eval_entity_metrics_exact", test_entity_metrics_exact_match),
        ("eval_entity_metrics_partial", test_entity_metrics_partial),
        ("eval_timeline_ordering_accuracy", test_timeline_ordering_accuracy),
        ("eval_grounding_metrics_phantom", test_grounding_metrics_supported_and_phantom),
        ("eval_error_taxonomy_mapping", test_error_taxonomy_classification),
        ("evaluator_full_benchmark", test_evaluator_full_benchmark),
        ("evaluator_prompt_injection_gate", test_prompt_injection_case_evaluation),
        ("evaluator_odia_idiom_preservation", test_multilingual_odia_idiom_evaluation),
    ]

    passed = 0
    failed = 0

    for name, test_func in test_cases:
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {name}: {exc}")
            failed += 1

    print("-" * 75)
    print(f"Total Tests: {len(test_cases)} | Passed: {passed} | Failed: {failed}")
    print("=" * 75)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL 18 PHASE 11 DATASET & EVALUATION TESTS PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    main()
