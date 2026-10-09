"""CLINOVA AI — Standalone Phase 13 Foundation Test Runner.

Executes all 26 test matrix scenarios (A through Z) using Python's standard library asyncio runner.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.init_db import init_db
from tests.test_phase13_foundation import (
    test_a_patient_creation,
    test_b_encounter_creation,
    test_c_case_creation,
    test_d_case_retrieval,
    test_e_case_filtering,
    test_f_evidence_insertion,
    test_g_provenance_persistence,
    test_h_vital_insertion,
    test_i_timeline_retrieval,
    test_j_follow_up_insertion,
    test_k_triage_note_insertion,
    test_l_human_review_action,
    test_m_invalid_review_action_prohibited,
    test_n_state_transition,
    test_o_invalid_state_transition,
    test_p_optimistic_concurrency_conflict,
    test_q_audit_creation,
    test_r_unauthorized_access,
    test_s_cross_case_not_found,
    test_t_consent_persistence,
    test_u_invalid_vital_data,
    test_v_transaction_rollback,
    test_w_error_contract_shielding,
    test_x_structured_error_response_schema,
    test_y_synthetic_mode_verification,
    test_z_migration_schema_verification,
)


async def main():
    print("=" * 80)
    print("CLINOVA AI — PHASE 13 FOUNDATION TEST MATRIX EXECUTION (A through Z)")
    print("=" * 80)

    # Initialize Database
    from app.core.config import settings
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = True
    print("[INIT] Initializing database and synthetic facilities...")
    await init_db()
    print("[INIT] Database initialized successfully.\n")

    test_matrix = [
        ("A: Patient Creation", test_a_patient_creation),
        ("B: Encounter Creation", test_b_encounter_creation),
        ("C: Master Case Creation", test_c_case_creation),
        ("D: Master Case Retrieval", test_d_case_retrieval),
        ("E: Case Filtering", test_e_case_filtering),
        ("F: Evidence Insertion", test_f_evidence_insertion),
        ("G: Provenance Persistence", test_g_provenance_persistence),
        ("H: Vital Insertion & Bounds Checking", test_h_vital_insertion),
        ("I: Timeline Retrieval", test_i_timeline_retrieval),
        ("J: Follow-up Insertion & Answering", test_j_follow_up_insertion),
        ("K: Triage Note Insertion", test_k_triage_note_insertion),
        ("L: Human Review Action", test_l_human_review_action),
        ("M: Prohibited Autonomous Action Rejection", test_m_invalid_review_action_prohibited),
        ("N: Valid State Transition", test_n_state_transition),
        ("O: Invalid State Transition Rejection", test_o_invalid_state_transition),
        ("P: Optimistic Concurrency Conflict (409)", test_p_optimistic_concurrency_conflict),
        ("Q: Audit Creation", test_q_audit_creation),
        ("R: Unauthorized Access Rejection (403)", test_r_unauthorized_access),
        ("S: Cross-Case Not Found Handling (404)", test_s_cross_case_not_found),
        ("T: Consent Persistence", test_t_consent_persistence),
        ("U: Invalid Vital Data Rejection (422)", test_u_invalid_vital_data),
        ("V: Transaction Rollback Integrity", test_v_transaction_rollback),
        ("W: Error Contract Shielding (No Leakage)", test_w_error_contract_shielding),
        ("X: Structured Error Response Schema", test_x_structured_error_response_schema),
        ("Y: Synthetic Mode Verification", test_y_synthetic_mode_verification),
        ("Z: Migration Upgrade Schema Verification", test_z_migration_schema_verification),
    ]

    passed = 0
    failed = 0
    failures = []
    start_total = time.time()

    for name, test_func in test_matrix:
        t0 = time.time()
        try:
            await test_func()
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  [PASS] {name:<46} ({elapsed_ms:.1f}ms)")
            passed += 1
        except Exception as exc:
            elapsed_ms = (time.time() - t0) * 1000
            print(f"  [FAIL] {name:<46} ({elapsed_ms:.1f}ms) -> {exc}")
            failures.append((name, str(exc)))
            failed += 1

    total_time = (time.time() - start_total) * 1000
    print("\n" + "=" * 80)
    print(f"PHASE 13 TEST SUMMARY: {passed} PASSED | {failed} FAILED | TOTAL: {len(test_matrix)} | TIME: {total_time:.1f}ms")
    if failures:
        print("FAILURES:")
        for fname, fexc in failures:
            print(f"  - {fname}: {fexc}")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
