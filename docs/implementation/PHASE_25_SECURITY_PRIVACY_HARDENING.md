# CLINOVA AI — Phase 25: Security, Privacy & Audit Hardening

## 1. Executive Summary & Objective
Phase 25 hardens the entire CLINOVA AI platform against unauthorized access, privilege escalation, cross-patient and cross-facility data leakage, client-side offline storage vulnerabilities, insecure synchronization replay/tampering, credential exposure, audit trail modification, and unauthorized autonomous clinical execution.

CLINOVA AI strictly preserves the foundational safety invariant:
> **CLINOVA AI is a decision-support and care-orchestration architecture, NEVER an autonomous clinical authority.**
> The backend server unconditionally rejects any autonomous action attempting diagnosis, prescription, admission, discharge, or procedure authorization with HTTP 403/422.

---

## 2. Threat Model & Security Posture

| Threat Vector | Attack Scenario | CLINOVA Defense & Countermeasure |
|---|---|---|
| **Token Forgery & Revocation Bypass** | Replaying revoked tokens or crafting forged JWT signatures | Server-side cryptographic signature validation (`HS256`), expiration enforcement (`exp`), and active token revocation verification against `revoked_tokens` table. |
| **Inactive Account Exploitation** | Suspended staff account attempting API operations | Global `get_current_actor` dependency checks `user.is_active` in DB and returns `401 Unauthorized` (`USER_INACTIVE`). |
| **Vertical Privilege Escalation (RBAC)** | Patient or Nurse calling clinician decision, referral coordination, or facility admin endpoints | Declarative `check_role_permission(actor.role, Permission.<X>)` enforced server-side. Patient role cannot initiate referrals or record clinical decisions. |
| **Horizontal Privilege Escalation (Multi-Tenancy)** | Patient viewing another patient's case, or staff from Facility A modifying resources at Facility B | `authorize_case_access()` checks `patient_id` matches actor for patients; enforces facility assignment match for facility staff. `authorize_facility_access()` blocks cross-facility admin mutations. |
| **Random ID Enumeration** | Attacker guessing UUIDs to probe system existence | Endpoints perform object lookup and authorization checks consistently, returning structured 404s without leaking database traces or stack traces. |
| **Mass-Assignment / Parameter Tampering** | Attacker posting `role: "SYSTEM_ADMIN"` or `is_active: true` in intake payloads | Pydantic strict request schemas with `extra = "forbid"` reject unmapped client fields with HTTP 422. |
| **Autonomous Clinical Actions** | Client or rogue agent attempting `AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, or `AUTHORIZE_PROCEDURE` | Backend `validate_review_action_safety()` unconditionally rejects prohibited actions with HTTP 403/422. |
| **Sync Replay & Tampering** | Malicious node reusing legitimate `sync_id` with modified clinical payload | Server-side detection: if `sync_id` exists in `SYNCED` state but entity type or payload snapshot differs, batch item fails immediately as `FAILED` (`tampering/replay detected`). |
| **Insecure Offline Client Storage** | Sensitive auth tokens or credentials saved in browser `localStorage` queue | Client offline queue sanitizes payloads recursively (stripping tokens, passwords, API keys), enforces 7-day TTL pruning, caps queue to 500 items, partitions by `user_id`, and purges on logout. |
| **Audit Trail Tampering** | Malicious user attempting to update or delete audit events | The `audit_events` and `audit_logs` tables have zero update/delete API routes and zero cascade deletions; records are strictly append-only. |
| **Information Leakage via Errors** | Unhandled server exceptions leaking database schemas or internal filesystem paths | Global FastAPI exception handler catches unhandled errors, logs internally, and returns generic sanitized JSON error envelope without stack traces or filenames. |

---

## 3. Server-Side Enforcement Architecture

### 3.1 Authentication & Actor Context
All protected endpoints depend upon `get_current_actor`:
```python
actor: ActorContext = Depends(get_current_actor)
```
- Authenticates JWT bearer token with signature validation.
- Checks `revoked_tokens` table for revocation state.
- Queries `users` table to guarantee account exists and `is_active is True`.
- Populates authoritative `ActorContext(actor_id, role, facility_id, patient_id)`.
- Client-supplied `actor_id` or `clinician_id` fields are strictly ignored; server-derived context is used.

### 3.2 Role-Based Access Control (RBAC)
Server endpoints enforce specific permissions via `check_role_permission(actor.role, Permission.<NAME>)`:
- **Referrals** (`/api/v1/referrals/*`): Requires `Permission.REFERRAL_COORDINATE`.
- **Facilities** (`/api/v1/facilities/*`): Requires `Permission.FACILITY_ADMIN_MANAGE` and `authorize_facility_access()`.
- **Orchestration Decisions** (`/api/v1/orchestration/decision`): Requires `Permission.CLINICAL_DECISION_RECORD`.
- **SignalGraph Telemetry** (`/api/v1/signalgraph/inject-event`): Restricted from `PATIENT` role; facility scope enforced.
- **Offline Sync Push** (`/api/v1/sync/push`): Requires `Permission.SYNC_PUSH`; patients restricted from pushing decisions/outcomes; nurses restricted from pushing clinician decisions.

### 3.3 Zero Autonomous Clinical Actions
In accordance with CLINOVA clinical governance principles, autonomous actions are strictly blocked:
```python
PROHIBITED_CLINICAL_ACTIONS = {
    "AI_DIAGNOSIS",
    "AUTO_PRESCRIBE",
    "AI_ADMISSION",
    "AI_DISCHARGE",
    "AUTHORIZE_PROCEDURE",
}
```
Both orchestration endpoints (`/api/v1/orchestration/decision`) and offline sync handlers validate action safety:
```python
validate_review_action_safety(payload.action)  # Raises ClinovaAPIError 403/422 if prohibited
```

### 3.4 Offline Sync Hardening & Replay Detection
1. **Replay & Tampering Protection**:
   When an incoming item has a `sync_id` already present with `sync_status == "SYNCED"`:
   - If the normalized entity type or payload snapshot differs from the stored journal entry, the item is rejected as `FAILED` (`"Operation ID reused with conflicting payload (tampering/replay detected)."`).
   - If identical, the item is safely marked `ALREADY_SYNCED` without creating duplicate records.
2. **Append-Only Invariants**:
   Vitals and timeline events are append-only.
3. **Mandatory Human Gate on Conflicts**:
   Conflicts on cases or decisions require explicit clinician resolution (`CLINICIAN_WINS`, `KEEP_LOCAL`, `MERGE`) accompanied by mandatory `clinical_rationale`.

### 3.5 Client-Side Offline Storage Hardening
File: `frontend/src/lib/offlineQueue.ts`
- **Credential Sanitization**: `sanitizePayload()` recursively strips `password`, `token`, `secret`, `api_key`, `auth_token`, `authorization`, and bearer tokens prior to saving to browser `localStorage`.
- **TTL Pruning**: Items older than 7 days (`MAX_ITEM_AGE_MS`) are automatically pruned during retrieval.
- **Queue Bounding**: Maximum 500 items (`MAX_QUEUE_SIZE`); pending items are preserved, older completed items trimmed.
- **User Scoping & Logout Purge**:
  - `getOfflineQueue(userId)` filters items by authenticated user.
  - `clearUserQueue(userId)` purges cached data upon logout to prevent cross-session leakage.
- **Documented Residual Risk**: `localStorage` is unencrypted at rest; client-side queue is for transient offline queuing only and must never store unencrypted PII or credentials permanently.

### 3.6 Security Headers & Error Sanitization
File: `backend/app/main.py`
- **Security Headers Middleware**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Global Generic Exception Handler**:
  Masks internal server exceptions and returns standard JSON error responses without stack traces or path names.

---

## 4. Test Suite Matrix & Verification Results

### Dedicated Phase 25 Security & Privacy Test Suite
File: `backend/tests/test_phase25_security_privacy.py`
Execution Time: 23.02s
Result: **20 passed, 0 failed**

| Test Identifier | Security Invariant Tested | HTTP / Assertion Result |
|---|---|---|
| `test_p25_01_unauthenticated_rejection` | Protected endpoints reject missing authentication | 401 Unauthorized (`MISSING_TOKEN`) |
| `test_p25_02_tampered_expired_revoked_token` | Revoked, expired, or tampered tokens rejected | 401 Unauthorized (`TOKEN_REVOKED`, `INVALID_TOKEN`) |
| `test_p25_03_inactive_account_rejection` | Inactive/suspended user accounts blocked | 401 Unauthorized (`USER_INACTIVE`) |
| `test_p25_04_server_side_rbac_enforcement` | Patients blocked from referrals; Nurses blocked from clinician decisions | 403 Forbidden |
| `test_p25_05_patient_data_isolation` | Patient 2 cannot access Patient 1 case details | 403 Forbidden / 404 Not Found |
| `test_p25_06_facility_data_isolation` | Facility admin at FAC-A cannot modify FAC-B capacity | 403 Forbidden |
| `test_p25_07_object_level_authorization` | Guessing random UUIDs yields structured 404 without traces | 404 Not Found, 0 traceback traces |
| `test_p25_08_mass_assignment_protection` | Client injecting privilege escalation fields (`role`, `is_admin`) rejected | 422 Unprocessable Entity |
| `test_p25_09_prohibited_autonomous_clinical_actions` | `AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE` blocked | 403 / 422 rejection |
| `test_p25_10_referral_mutation_access_control` | Referral mutations require `REFERRAL_COORDINATE` permission | 403 Forbidden for Nurse |
| `test_p25_11_facility_capability_capacity_mutation_access` | Facility mutations require `FACILITY_ADMIN_MANAGE` permission | 403 Forbidden for Nurse |
| `test_p25_12_signalgraph_telemetry_access_control` | Patient role blocked from injecting telemetry; cross-facility boundary enforced | 403 Forbidden |
| `test_p25_13_orchestration_decision_clinician_only` | Clinician ID is authoritatively derived from actor, not spoofed request body | Verified DB clinician_id matches token |
| `test_p25_14_sync_replay_and_tampering_detection` | Replaying `sync_id` with tampered payload snapshot detected and rejected | status: FAILED (`tampering/replay detected`) |
| `test_p25_15_sync_cross_facility_and_patient_scope` | Patients cannot sync decisions/outcomes; nurses cannot sync clinician decisions | status: FAILED with authorization error |
| `test_p25_16_sync_prohibited_clinical_action_rejection` | Autonomous clinical actions submitted via offline sync batch rejected | status: FAILED (`prohibited autonomous action`) |
| `test_p25_17_sync_conflict_resolution_clinician_cross_facility` | Conflict resolution restricted to clinicians matching case facility | 403 Forbidden |
| `test_p25_18_audit_immutability` | Audit logs have no update/delete routes; cascade deletes do not purge audit logs | Immutability verified |
| `test_p25_19_zero_credential_leakage` | API endpoints and error logs never leak passwords or secret keys | Zero leakage across responses |
| `test_p25_20_structured_error_contract_and_security_headers` | Security headers present; unhandled exceptions return structured error without traces | Headers present; no trace in body |

---

## 5. Comprehensive Regression Test Execution

A complete regression suite across Phases 18 through 25 was executed simultaneously:
```powers
$env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe -m pytest \
    backend/tests/test_phase18_ai_application.py \
    backend/tests/test_phase19_voice_stt.py \
    backend/tests/test_phase20_ocr_extraction.py \
    backend/tests/test_phase21_translation.py \
    backend/tests/test_phase22_facilitygraph_referral.py \
    backend/tests/test_phase23_migration.py \
    backend/tests/test_phase23_outcome_signalgraph.py \
    backend/tests/test_phase24_offline_sync.py \
    backend/tests/test_phase25_security_privacy.py \
    -q -p no:logging
```

### Verified Test Outcome:
```
125 passed in 108.47s (0:01:48)
```
- **Phase 18 (AI Application Integration)**: 15 passed
- **Phase 19 (Voice / STT / Multimodal Intake)**: 14 passed
- **Phase 20 (OCR + Report Extraction)**: 6 passed
- **Phase 21 (Translation + Multilingual Workflow)**: 12 passed
- **Phase 22 (Referral + FacilityGraph + Care Orchestration)**: 23 passed
- **Phase 23 (Migration Architecture Verification)**: 7 passed
- **Phase 23 (Outcome Loop + SignalGraph)**: 18 passed
- **Phase 24 (Offline / Low-Bandwidth / Sync)**: 10 passed
- **Phase 25 (Security + Privacy + Audit Hardening)**: 20 passed
**Total: 125 passed, 0 failed, 0 skipped.**

### Frontend Quality Verification:
- `npm run typecheck`: **0 errors** (`tsc --noEmit`)
- `npm run lint`: **0 warnings, 0 errors** (`next lint`)

---

## 6. Conclusion
Phase 25 is fully implemented, verified, and regression-tested. The CLINOVA AI security and privacy perimeter is hardened server-side across authentication, authorization, multi-tenant isolation, offline sync replay defense, client storage sanitization, error shielding, and strict non-autonomous clinical governance.
