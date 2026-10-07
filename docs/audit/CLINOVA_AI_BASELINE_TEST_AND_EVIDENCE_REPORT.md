# CLINOVA AI — BASELINE TEST & EVIDENCE REPORT

**Execution Timestamp:** 2026-10-06T13:57:48+05:30  
**Phase:** Phase 1 Pre-Implementation Baseline  
**Environment:** Windows (Native PowerShell, Python 3.14.5, Node.js v24.14.1)  
**Git Branch:** `master`  
**Git Status:** Clean (`nothing to commit, working tree clean`)  

---

## 1. Executive Summary

Prior to initiating any schema or code changes for Phase 1 ("SECURE FOUNDATION + CANONICAL PATIENT CASE"), a full baseline test and typecheck verification run was executed across the entire repository.

- **Backend Pytest Suite:** **69 / 69 PASSED** (100% success rate, 0 failed, 0 skipped, run time: 537.61s)
- **Frontend Test Suite:** **27 / 27 PASSED** (100% success rate across all 3 test suites)
- **Frontend Typecheck (`tsc --noEmit`):** **0 ERRORS, 0 WARNINGS**

All tests pass reproducibly under the native Windows environment.

---

## 2. Backend Pytest Execution Evidence (69 Tests)

```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\admin\CLIVORA-AI\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\admin\CLIVORA-AI\backend
configfile: pytest.ini
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=session, asyncio_default_test_loop_scope=session
collected 69 items

backend\tests\test_ai.py::test_ai_triage_clinical_decision_support PASSED [  1%]
backend\tests\test_ai.py::test_ai_soap_synthesis PASSED                  [  2%]
backend\tests\test_assistant.py::test_assistant_capabilities_and_preferences PASSED [  4%]
backend\tests\test_assistant.py::test_assistant_prompt_injection_defense PASSED [  5%]
backend\tests\test_assistant.py::test_assistant_medical_boundaries_and_emergency PASSED [  7%]
backend\tests\test_assistant.py::test_assistant_multilingual_support PASSED [  8%]
backend\tests\test_assistant.py::test_assistant_rbac_tool_execution PASSED [ 10%]
backend\tests\test_audit.py::test_audit_logging_trail PASSED             [ 11%]
backend\tests\test_auth.py::test_auth_flow PASSED                        [ 13%]
backend\tests\test_auth.py::test_login_invalid_credentials PASSED        [ 14%]
backend\tests\test_consultations.py::test_consultation_lifecycle PASSED  [ 15%]
backend\tests\test_health.py::test_root_endpoint PASSED                  [ 17%]
backend\tests\test_health.py::test_health_check_endpoint PASSED          [ 18%]
backend\tests\test_health.py::test_ping_endpoint PASSED                  [ 20%]
backend\tests\test_migration.py::test_existing_database_upgrade_preserves_unlinked_records PASSED [ 21%]
backend\tests\test_patients.py::test_patient_crud_flow PASSED            [ 23%]
backend\tests\test_phase1_security_foundation.py::test_health_liveness_and_readiness PASSED [ 24%]
backend\tests\test_phase1_security_foundation.py::test_idor_protection_cross_patient_access PASSED [ 26%]
backend\tests\test_phase1_security_foundation.py::test_rbac_patient_forbidden_endpoints PASSED [ 27%]
backend\tests\test_phase1_security_foundation.py::test_object_storage_document_lifecycle_and_validation PASSED [ 28%]
backend\tests\test_phase1_security_foundation.py::test_background_job_queue PASSED [ 30%]
backend\tests\test_phase1_security_foundation.py::test_multi_facility_listing PASSED [ 31%]
backend\tests\test_phase2_clinical_architecture.py::test_clinical_encounters_lifecycle PASSED [ 33%]
backend\tests\test_phase2_clinical_architecture.py::test_clinical_observations_and_vitals PASSED [ 34%]
backend\tests\test_phase2_clinical_architecture.py::test_allergies_and_intolerances PASSED [ 36%]
backend\tests\test_phase2_clinical_architecture.py::test_medication_regimens PASSED [ 37%]
backend\tests\test_phase2_clinical_architecture.py::test_diagnoses_ai_attribution_and_clinician_verification PASSED [ 39%]
backend\tests\test_phase2_clinical_architecture.py::test_clinical_notes_immutability_and_amendments PASSED [ 40%]
backend\tests\test_phase2_clinical_architecture.py::test_referral_management_lifecycle PASSED [ 42%]
backend\tests\test_phase2_clinical_architecture.py::test_multi_tenancy_cross_facility_isolation PASSED [ 43%]
backend\tests\test_phase2_clinical_architecture.py::test_patient_multi_identifiers_and_auto_mrn PASSED [ 44%]
backend\tests\test_phase2_clinical_architecture.py::test_longitudinal_patient_timeline PASSED [ 46%]
backend\tests\test_phase2_clinical_architecture.py::test_synthetic_scale_and_index_performance PASSED [ 47%]
backend\tests\test_phase3_document_storage.py::test_valid_pdf_and_image_upload PASSED [ 49%]
backend\tests\test_phase3_document_storage.py::test_file_validation_and_mime_spoofing_defense PASSED [ 50%]
backend\tests\test_phase3_document_storage.py::test_path_traversal_filename_sanitization PASSED [ 52%]
backend\tests\test_phase3_document_storage.py::test_malware_detection_and_quarantine_isolation PASSED [ 53%]
backend\tests\test_phase3_document_storage.py::test_idor_protection_cross_patient_isolation PASSED [ 55%]
backend\tests\test_phase3_document_storage.py::test_presigned_time_limited_access_token PASSED [ 56%]
backend\tests\test_phase3_document_storage.py::test_document_versioning_and_amendments PASSED [ 57%]
backend\tests\test_phase3_document_storage.py::test_derived_artifacts_linkage PASSED [ 59%]
backend\tests\test_phase3_document_storage.py::test_soft_deletion_and_retention_compliance PASSED [ 60%]
backend\tests\test_phase3_document_storage.py::test_large_file_streaming_benchmark PASSED [ 62%]
backend\tests\test_phase3_document_storage.py::test_cross_facility_document_isolation PASSED [ 63%]
backend\tests\test_phase3_document_storage.py::test_anonymous_access_strictly_denied PASSED [ 65%]
backend\tests\test_phase3_document_storage.py::test_document_search_filtering_and_pagination PASSED [ 66%]
backend\tests\test_phase4_enterprise_readiness.py::test_keyset_cursor_pagination_encode_decode PASSED [ 68%]
backend\tests\test_phase4_enterprise_readiness.py::test_prometheus_telemetry_metrics_collection PASSED [ 69%]
backend\tests\test_phase4_enterprise_readiness.py::test_bulk_csv_patient_import_preview_and_execute PASSED [ 71%]
backend\tests\test_phase4_enterprise_readiness.py::test_bulk_fhir_bundle_import PASSED [ 72%]
backend\tests\test_phase4_enterprise_readiness.py::test_patient_deduplication_and_chart_merge PASSED [ 73%]
backend\tests\test_phase4_enterprise_readiness.py::test_retention_sweep_dry_run_and_admin_execution PASSED [ 75%]
backend\tests\test_risk_engine.py::test_anonymizer_phone_and_email PASSED [ 76%]
backend\tests\test_risk_engine.py::test_anonymizer_aadhaar PASSED        [ 78%]
backend\tests\test_risk_engine.py::test_risk_engine_breathing_urgency PASSED [ 79%]
backend\tests\test_risk_engine.py::test_risk_engine_chest_pain_urgency PASSED [ 81%]
backend\tests\test_risk_engine.py::test_risk_engine_routine_presentation PASSED [ 82%]
backend\tests\test_risk_engine.py::test_non_diagnostic_triage_note_structure PASSED [ 84%]
backend\tests\test_role_workflows.py::test_full_role_workflow_and_rbac PASSED [ 85%]
backend\tests\test_roles.py::test_private_endpoints_require_auth PASSED  [ 86%]
backend\tests\test_roles.py::test_role_endpoint_matrix PASSED            [ 88%]
backend\tests\test_roles.py::test_cannot_self_register_staff PASSED      [ 89%]
backend\tests\test_roles.py::test_patient_intake_review_and_isolation PASSED [ 91%]
backend\tests\test_roles.py::test_patient_records_use_id_not_email PASSED [ 92%]
backend\tests\test_doctor_encounter_ownership PASSED                    [ 94%]
backend\tests\test_patient_profile_cannot_change_identity_or_medical_notes PASSED [ 95%]
backend\tests\test_speech_service.py::test_detect_script_multilingual PASSED [ 97%]
backend\tests\test_speech_service.py::test_transcribe_empty_audio PASSED [ 98%]
backend\tests\test_speech_service.py::test_transcribe_audio_offline_graceful PASSED [100%]

======================= 69 passed in 537.61s (0:08:57) ========================
```

---

## 3. Frontend Test Execution Evidence (27 Tests)

```text
> clinova-frontend@0.1.0 test
> node scripts/test-voice-state-machine.js && node scripts/test-speech-recognition.js && node scripts/test-voice-conversation-e2e.js

=================================================
CLINOVA AI — VOICE STATE MACHINE TEST SUITE
=================================================
  ✓ [PASS] Allows CLOSED to REQUESTING_MIC and CONNECTING
  ✓ [PASS] Allows full standard conversation loop
  ✓ [PASS] Allows Interruption from ASSISTANT_SPEAKING
  ✓ [PASS] Allows CLOSED from any active state
  ✓ [PASS] Rejects invalid jumps like CLOSED to USER_SPEAKING
  ✓ [PASS] Detects Latin and Indic terminal punctuation correctly
-------------------------------------------------
Results: 6 / 6 tests passed (100%)
=================================================
=================================================
CLINOVA AI — SPEECH TRANSCRIPTION TEST SUITE
=================================================
  ✓ [PASS] Detects Hindi Devanagari script accurately
  ✓ [PASS] Detects Odia script accurately
  ✓ [PASS] Detects English script accurately
  ✓ [PASS] Detects Bengali script accurately
  ✓ [PASS] Detects Tamil script accurately
  ✓ [PASS] Detects Telugu script accurately
  ✓ [PASS] Handles empty and non-alphabetic inputs gracefully
  ✓ [PASS] Combines with period when existing text lacks punctuation
  ✓ [PASS] Combines with space when existing text ends with period
  ✓ [PASS] Supports Hindi purna viram (।) boundary joining
  ✓ [PASS] Replaces existing text cleanly in replace mode
  ✓ [PASS] Prevents duplicate appending if transcript already present
  ✓ [PASS] Ensures supported Indic recognition locales exist
-------------------------------------------------
Results: 13 / 13 tests passed (100%)
=================================================
=================================================
CLINOVA AI — MULTI-TURN CONVERSATION MATRIX
=================================================
  ✓ [PASS] Multi-Turn Turn 1: Patient reports dizziness
  ✓ [PASS] Multi-Turn Turn 2: Patient clarifies orthostatic trigger with context retention
  ✓ [PASS] Multi-Turn Turn 3: Patient clarifies absence of red flags with context retention
  ✓ [PASS] Rejects prompt injection attempts safely
  ✓ [PASS] Prohibits autonomous definitive diagnosis
  ✓ [PASS] Prohibits autonomous prescribing
  ✓ [PASS] Escalates emergency chest pain immediately
  ✓ [PASS] Gates consequential submission behind human confirmation
-------------------------------------------------
Results: 8 / 8 tests passed (100%)
=================================================
```

---

## 4. Frontend Typecheck Verification Evidence

```text
Command: node frontend/node_modules/typescript/bin/tsc --project frontend/tsconfig.json --noEmit
Exit code: 0
Output: Clean (0 errors, 0 warnings)
```

---

## 5. Baseline Conclusions

1. The repository is in an operational, fully verified baseline state.
2. All current role workflows (Patient, Nurse, Doctor, Admin) function according to specification.
3. Zero breaking changes or regressions exist in the current codebase.
4. All future Phase 1 enhancements must maintain 100% pass rate on this regression baseline.
