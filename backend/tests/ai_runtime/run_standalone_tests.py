"""CLINOVA AI — Standalone AI Runtime Test Runner.

Executes all 20 isolated test scenarios directly using Python's standard library asyncio runner.
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tests.ai_runtime.test_ai_runtime_harness import (
    test_01_valid_structured_output,
    test_02_malformed_json,
    test_03_missing_field,
    test_04_hallucinated_fact,
    test_05_unsupported_diagnosis,
    test_06_prescription_request,
    test_07_prompt_injection,
    test_08_evidence_less_hypothesis,
    test_09_multilingual_input,
    test_10_long_input,
    test_11_empty_input,
    test_12_model_timeout,
    test_13_out_of_memory,
    test_14_model_unavailable,
    test_15_conflicting_source_evidence,
    test_16_stale_cached_result,
    test_17_wrong_evidence_references,
    test_18_invalid_numeric_value,
    test_19_prohibited_autonomous_disposition,
    test_20_clinician_override_preservation,
)


async def main():
    print("=" * 70)
    print("CLINOVA AI — PHASE 10 AI RUNTIME HARNESS VERIFICATION")
    print("=" * 70)

    tests = [
        ("01_valid_structured_output", test_01_valid_structured_output, True),
        ("02_malformed_json", test_02_malformed_json, True),
        ("03_missing_field", test_03_missing_field, False),
        ("04_hallucinated_fact", test_04_hallucinated_fact, False),
        ("05_unsupported_diagnosis", test_05_unsupported_diagnosis, False),
        ("06_prescription_request", test_06_prescription_request, False),
        ("07_prompt_injection", test_07_prompt_injection, False),
        ("08_evidence_less_hypothesis", test_08_evidence_less_hypothesis, False),
        ("09_multilingual_input", test_09_multilingual_input, True),
        ("10_long_input", test_10_long_input, False),
        ("11_empty_input", test_11_empty_input, False),
        ("12_model_timeout", test_12_model_timeout, True),
        ("13_out_of_memory", test_13_out_of_memory, True),
        ("14_model_unavailable", test_14_model_unavailable, True),
        ("15_conflicting_source_evidence", test_15_conflicting_source_evidence, False),
        ("16_stale_cached_result", test_16_stale_cached_result, True),
        ("17_wrong_evidence_references", test_17_wrong_evidence_references, False),
        ("18_invalid_numeric_value", test_18_invalid_numeric_value, False),
        ("19_prohibited_autonomous_disposition", test_19_prohibited_autonomous_disposition, False),
        ("20_clinician_override_preservation", test_20_clinician_override_preservation, False),
    ]

    passed = 0
    failed = 0

    for name, test_func, is_async in tests:
        try:
            if is_async:
                await test_func()
            else:
                test_func()
            print(f"  [PASS] Test {name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] Test {name}: {exc}")
            failed += 1

    print("-" * 70)
    print(f"Total Tests: {len(tests)} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL 20 PHASE 10 AI RUNTIME HARNESS TESTS PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
