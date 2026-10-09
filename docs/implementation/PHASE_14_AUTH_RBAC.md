# CLINOVA AI — Phase 14 Architecture & Implementation Record: Authentication, RBAC, Authorization & Identity Hardening

**Document ID:** CLINOVA-DOC-PHASE14-AUTH-RBAC  
**Status:** IMPLEMENTED & VERIFIED  
**Phase:** 14 (Strictly Atomic Phase 14 Boundary — No Phase 15 Advance)  
**Security Level:** Production-Hardened Clinical Advisory Architecture  
**Dependencies:** Phase 13 Core Backend Foundation (`c06d314060ef`)  
**Target Environment:** Local-First SQLite & Production PostgreSQL  

---

## 1. Executive Summary

Phase 14 delivers an enterprise-grade, zero-cost, local-first **Authentication, Role-Based Access Control (RBAC), Multi-Facility Boundary Scoping, and Identity Hardening System** for CLINOVA AI. It replaces transitional test identity headers with an authoritative server-side security perimeter backed by cryptographic tokens, database validation, role enforcement, and non-diagnostic clinical safety guardrails.

All identity, permission, and facility assertions are resolved server-side against persisted relational records. Client headers attempting role spoofing or facility tampering are strictly ignored. Prohibited autonomous AI actions (`AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE`) are unconditionally rejected at the server gateway with HTTP 422 `UNSUPPORTED_OPERATION`.

---

## 2. Threat Model & Security Perimeter

CLINOVA AI operates in high-stakes clinical triage and referral coordination environments. The Phase 14 security model enforces six foundational defensive principles:

1. **Non-Diagnostic, Advisory-Only Clinical Boundary:**
   CLINOVA AI provides clinical decision support and care continuity orchestration. It does not replace human clinical judgment. Any attempt by automated agents or clients to invoke prohibited autonomous decisions is stopped at the policy barrier.
2. **Authoritative Server-Side Identity:**
   Client-supplied identity headers (`X-Actor-Role`, `X-Facility-Id`) cannot escalate privileges. When an `Authorization: Bearer <token>` header is present, the server decodes the signature, verifies revocation status, loads the persisted database record, checks `is_active`, and derives roles authoritatively from `user.role`.
3. **Multi-Facility Boundary Isolation (Zero Enumeration Leakage):**
   Staff assigned to a specific healthcare facility (e.g., Cuttack District Headquarters Hospital `FAC-DH-04`) cannot view, list, or mutate cases belonging to another facility (e.g., Angul Rural PHC `FAC-PHC-01`). Cross-facility access attempts return HTTP 404 `NOT_FOUND` rather than HTTP 403 `FORBIDDEN`, concealing resource existence from unauthorized callers.
4. **Patient Privacy & Self-Scope Enforcement:**
   Users with the `PATIENT` role are strictly restricted to reading and submitting their own intake and follow-up data. Access to cases or records of other patients returns HTTP 404 `NOT_FOUND`.
5. **Session Revocation & Token Lifecycle:**
   Every issued JWT includes a unique JWT ID (`jti`) and expiration timestamp (`exp`). Logout requests record the token hash in the `revoked_tokens` database table. Revoked tokens are immediately rejected across all protected endpoints.
6. **Zero Paid Services & Local-First Stack:**
   Authentication uses native Python `bcrypt` and `python-jose` (HS256) with zero cloud SaaS identity dependencies (no Auth0, Firebase Auth, or external paid SSO). Compatible with SQLite in development and PostgreSQL in production.

---

## 3. Cryptographic Identity & Session Lifecycle

### 3.1 Password Hashing
- **Algorithm:** Native `bcrypt` (`bcrypt.hashpw` / `bcrypt.checkpw`) with salt generation.
- **Bypass of Passlib Bug:** Python 3.14 includes runtime check incompatibilities with older `passlib` releases. Phase 14 directly utilizes native `bcrypt` bindings for maximum performance and stability.
- **Demo Credential:** Seeded synthetic users are initialized with `ClinovaDemo2026!` for rapid evaluation, which is hashed with bcrypt during database initialization.

### 3.2 JWT Token Specification
- **Algorithm:** `HS256` (`JWT_ALGORITHM = "HS256"` in `app.core.config`).
- **Signature Secret:** Configurable via `settings.SECRET_KEY`.
- **Token Claims:**
  - `sub`: User UUID
  - `username`: User handle
  - `role`: Canonical role
  - `facility_id`: Primary facility UUID (or null for global roles)
  - `iat`: Issued-at timestamp (UTC)
  - `exp`: Expiration timestamp (default: 60 minutes)
  - `jti`: Unique UUID preventing replay attacks and enabling selective blacklisting

### 3.3 Token Revocation
- **Table:** `revoked_tokens`
- **Fields:** `id`, `token_hash` (SHA-256 hex digest of the raw JWT), `user_id`, `revoked_at`, `expires_at`, `reason`.
- **Revocation Check:** `get_current_actor` computes `SHA-256` of the incoming Bearer token and verifies whether the hash exists in `revoked_tokens`.

---

## 4. Canonical Role & Persona Architecture

Phase 14 defines eight canonical roles and seeds a complete synthetic evaluation roster:

| Persona ID | Username | Role | Assigned Facility | Permissions / Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| `usr-doc-01` | `clinician` | `CLINICIAN` | `FAC-DH-04` (Cuttack DH) | Case creation, vitals, triage notes, clinical review actions (`VERIFY`, `MODIFY`, `REJECT`, `REFER`), full clinical transitions, audit read |
| `usr-nurse-02` | `nurse` | `NURSE` | `FAC-DH-04` (Cuttack DH) | Case creation, vitals, triage notes, nurse transitions (`START_TRIAGE`, `SUBMIT_TRIAGE`, `ESCALATE`), verification review actions |
| `usr-nurse-phc` | `nurse_phc` | `NURSE` | `FAC-PHC-01` (Angul PHC) | Rural PHC triage nurse for cross-facility boundary testing |
| `usr-ref-03` | `referral` | `REFERRAL_COORDINATOR` | `FAC-DH-04` (Cuttack DH) | Referral coordination, facility capacity inspection; cannot perform clinical diagnoses or review decisions |
| `usr-admin-03` | `facility_admin` | `FACILITY_ADMIN` | `FAC-DH-04` (Cuttack DH) | Facility bed/resource management; strictly barred from clinical actions |
| `usr-audit-05` | `auditor` | `AUDITOR` | *Global* (None) | System-wide read-only visibility into cases, timeline, and audit logs; zero mutation permission |
| `usr-sys-06` | `sysadmin` | `SYSTEM_ADMIN` | *Global* (None) | System configuration, security monitoring, global oversight |
| `usr-patient-07` | `patient` | `PATIENT` | `FAC-PHC-01` (Angul PHC) | Self-scope patient intake, questionnaire completion |
| `usr-pt-09` | `patient_09` | `PATIENT` | `FAC-DH-04` (Cuttack DH) | Synthetic patient for urban hospital testing |
| `usr-inactive-08` | `inactive_user` | `NURSE` | `FAC-PHC-01` (Angul PHC) | `is_active: False`; login and API calls rejected with 403 |

---

## 5. Server-Side RBAC Permission Matrix

Permissions are strongly typed via the `Permission` enum in `app.core.rbac`:

```
User Management:
  user:self_read, user:admin_read, user:admin_write

Case Operations:
  case:create, case:read, case:list, case:update, case:delete

Clinical Workflow:
  clinical:vitals_record, clinical:evidence_add, clinical:follow_up_create,
  clinical:follow_up_answer, clinical:triage_note_create, clinical:triage_start,
  clinical:triage_submit, clinical:review_action_execute, clinical:state_transition,
  clinical:disposition_finalize, clinical:case_close

Referral Operations:
  referral:coordinate

Administration:
  admin:facility_manage, admin:system_config

Audit:
  audit:read
```

### Review Vocabulary Guardrails
- **Allowed Human Review Actions:** `VERIFY`, `REJECT`, `MODIFY`, `RESOLVE_CONFLICT`, `REQUEST_INFORMATION`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- **Nurse-Permitted Actions:** `REQUEST_INFORMATION`, `OBSERVE`, `ESCALATE`. (Nurses are barred from executing clinical sign-offs or CareGraph evidence node verification).
- **Clinician-Only Actions:** `VERIFY`, `REJECT`, `MODIFY`, `RESOLVE_CONFLICT`, `CONTINUE`, `REFER`.
- **Prohibited Autonomous Actions:** `AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE` (unconditionally rejected with 422 `UNSUPPORTED_OPERATION`).

---

## 6. Endpoints Implemented

### Authentication Endpoints (`/api/v1/auth/`)
- `POST /login`: Authenticates username/email + password, checks `is_active`, records audit log, updates `last_login_at`, returns JWT `TokenResponse`.
- `POST /logout`: Blacklists caller's JWT hash in `revoked_tokens` idempotently, records audit log, returns `LogoutResponse`.
- `GET /me`: Returns authoritative current user profile (`UserRead`) resolved from database.
- `GET /personas`: Lists active synthetic evaluation personas with facility metadata.
- `POST /switch-persona`: Rapid persona switching for testing; issues valid JWT for target persona.

### Protected Case Endpoints (`/api/v1/cases/`)
- All case sub-resources (`/cases`, `/cases/{id}`, `/evidence`, `/vitals`, `/timeline`, `/consent`, `/follow-up`, `/triage-note`, `/review-actions`, `/transitions`, `/audit`) enforce:
  1. `get_current_actor` dependency
  2. `authorize_case_access` (RBAC + Facility Scope + Patient Scope)
  3. `validate_review_action_safety` (Safety guardrails on `/review-actions`)
  4. `validate_state_transition_safety` (Role checks on `/transitions`)

---

## 7. Database Migration Record

- **File:** `backend/alembic/versions/0011_phase14_authentication_rbac.py`
- **Revision ID:** `d17e293848ef`
- **Down Revision:** `c06d314060ef` (`0010_phase13_core_backend_foundation`)
- **Modifications:**
  - Added `username` (`VARCHAR(64)`), `hashed_password` (`VARCHAR(255)`), `patient_id` (`VARCHAR(36)`), `updated_at` (`DATETIME`), `last_login_at` (`DATETIME`) to `users` table.
  - Added unique index `ix_users_username`.
  - Batch alter table syntax ensures full SQLite and PostgreSQL compatibility.

---

## 8. Frontend Resilient Client & Route Protection Architecture

- **Token Storage & Interceptor:** `frontend/src/lib/api.ts` manages JWT tokens in session storage with in-memory fallback. `safeFetch` automatically injects `Authorization: Bearer <token>`. Dispatches `clinova_session_expired` upon receiving 401 and `clinova_auth_changed` upon login/logout.
- **Route Guard System:** `frontend/src/components/common/RoleGuard.tsx` protects routes against unauthenticated or unauthorized roles, rendering a de-identified `UnauthorizedState` with a direct role switcher.
- **TopBar Session Management:** `frontend/src/components/common/TopBar.tsx` displays active identity badge, facility assignment, session expired alert banner, explicit `LogOut` button, and a modal with 1-click test credentials.

### Protected Route Matrix

| Route Path | Surface Description | Permitted Roles |
| :--- | :--- | :--- |
| `/staff` | Staff Workstation Gateway | `CLINICIAN`, `DOCTOR`, `NURSE`, `FACILITY_ADMIN`, `REFERRAL_COORDINATOR`, `SYSTEM_ADMIN`, `AUDITOR` |
| `/staff/triage` | Nurse Triage Workstation | `NURSE`, `CLINICIAN`, `DOCTOR`, `SYSTEM_ADMIN` |
| `/staff/review` | Clinician Review Queue | `CLINICIAN`, `DOCTOR`, `SYSTEM_ADMIN` |
| `/staff/cases/[caseId]` | Doctor Reviewer Workbench | `CLINICIAN`, `DOCTOR`, `SYSTEM_ADMIN` |
| `/referrals` | Referral Coordination | `REFERRAL_COORDINATOR`, `CLINICIAN`, `DOCTOR`, `SYSTEM_ADMIN`, `AUDITOR`, `FACILITY_ADMIN` |
| `/facilities` | Facility Resource Telemetry | `FACILITY_ADMIN`, `SYSTEM_ADMIN`, `AUDITOR`, `CLINICIAN`, `DOCTOR`, `NURSE` |
| `/system` | Tamper-Evident Audit Ledger | `SYSTEM_ADMIN`, `AUDITOR` |

- **Build Quality:**
  - `npm run typecheck`: 0 errors
  - `npm run lint`: 0 errors, 0 warnings
  - `npm run build`: 15/15 static and dynamic routes compiled cleanly

---

## 9. Comprehensive Verification Record

### 9.1 Phase 13 Core Foundation Baseline
- **Runner:** `backend/tests/run_phase13_tests.py`
- **Scenarios:** 26/26 (Scenarios A through Z)
- **Status:** **PASS** (100%)

### 9.2 Phase 14 Authentication & RBAC Suite
- **Test File:** `backend/tests/test_phase14_auth_rbac.py`
- **Total Test Cases:** 30
- **Status:** **30 PASSED / 0 FAILED** (100% in 24.17s)
- **Breakdown:**
  - Scenario A (Valid Login): PASS
  - Scenario B (Invalid Credentials Rejection): PASS
  - Scenario C (Logout Token Revocation): PASS
  - Scenario D (Expired Token Rejection): PASS
  - Scenario E (Malformed/Tampered Token Rejection): PASS
  - Scenario F (Deactivated User Prohibited): PASS
  - Scenario G (Current User /me Retrieval): PASS
  - Scenario H (Authoritative Role Resolution / Anti-Spoofing): PASS
  - Scenario I (Nurse Capabilities): PASS
  - Scenario J (Clinician Capabilities): PASS
  - Scenario K (Patient Restrictions): PASS
  - Scenario L (Referral Coordinator Restrictions): PASS
  - Scenario M (Auditor Read-Only Enforcement): PASS
  - Scenario N (Facility Admin Restrictions): PASS
  - Scenario O (Cross-Facility Denial 404): PASS
  - Scenario P (Cross-Case Non-Existent 404): PASS
  - Scenario Q (Nurse Clinical Action Denial 403): PASS
  - Scenario R (Patient Clinical Action Denial 403): PASS
  - Scenario S (Prohibited AI Action Rejection 422): PASS
  - Scenario T (Structured Error Envelope): PASS
  - Scenario U (Zero Password Leakage in Responses): PASS
  - Scenario V (Zero Secret Leakage in Errors): PASS
  - Scenario W (Authenticated Bearer API Call): PASS
  - Scenario X (Tampered Session Signature Rejection): PASS
  - Scenario Y (Revoked Token Invalidation Across Protected Routes): PASS
  - Scenario Z (Audit Log Generation for Auth Mutations): PASS
  - Adversarial Role Forgery with Bearer: PASS
  - Adversarial Unauthenticated Request Rejection: PASS
  - Adversarial Facility Spoofing: PASS
  - Section 24 17-Step Multi-Persona Clinical Smoke Flow: PASS

### 9.3 Total Backend Test Suite Run
- **Command:** `& "C:\Users\admin\CLINOVA-AI\backend\.venv\Scripts\python.exe" -m pytest backend/tests`
- **Result:** **119 PASSED / 0 FAILED** (45.28s across all 10 test modules)
  - `backend/tests/ai_dataset/test_data_quality_audit.py`: 1 passed
  - `backend/tests/ai_dataset/test_dataset_schema.py`: 8 passed
  - `backend/tests/ai_evaluation/test_eval_metrics.py`: 6 passed
  - `backend/tests/ai_evaluation/test_evaluator_harness.py`: 3 passed
  - `backend/tests/ai_runtime/test_ai_runtime_harness.py`: 20 passed
  - `backend/tests/test_clinical_scenarios.py`: 17 passed
  - `backend/tests/test_foundation.py`: 3 passed
  - `backend/tests/test_innovation_acceptance.py`: 5 passed
  - `backend/tests/test_phase13_foundation.py`: 26 passed
  - `backend/tests/test_phase14_auth_rbac.py`: 30 passed

---

## 10. Known Limitations & Forward Boundary

1. **Strict Phase 14 Isolation:** Phase 14 strictly covers authentication, authorization, RBAC, and boundary enforcement. It does not implement automated bed allocation or real-time GPS transport tracking (Phase 15 scope).
2. **Permission Harmonization:** CareGraph vital sign mutation endpoint harmonized with canonical `Permission.VITALS_RECORD` (with backward-compatible `VITALS_WRITE` alias in `Permission` enum).
3. **Refresh Tokens:** Phase 14 implements secure 60-minute JWT access tokens with revocation blacklisting. Long-lived refresh token rotation is reserved for future enterprise identity hardening.
4. **MFA / 2FA:** Multi-factor authentication is not implemented in Phase 14 to preserve zero-cost, local-first simulation autonomy.
