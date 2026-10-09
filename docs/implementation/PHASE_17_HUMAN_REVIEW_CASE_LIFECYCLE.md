# CLINOVA AI — Phase 17 Architecture & Implementation Record: Human Review + Case State Lifecycle

**Document ID:** CLINOVA-DOC-PHASE17-HUMAN-REVIEW-CASE-LIFECYCLE  
**Status:** IMPLEMENTED & VERIFIED  
**Phase:** 17 (Strictly Atomic Phase 17 Boundary — Zero Phase 18 AI Reasoning / LLM / Offline Sync Leakage)  
**Security Level:** Production-Hardened Authoritative Clinical Governance & Lifecycle Architecture  
**Dependencies:** Phase 13 Core Persistence, Phase 14 Auth & RBAC Hardening, Phase 15 Intake & Consent, Phase 16 Vitals, Queue & Deterministic Triage  
**Target Environment:** Local-First SQLite & Production PostgreSQL  

---

## 1. Executive Summary

Phase 17 establishes the authoritative **Human Review and Case State Lifecycle** foundation for CLINOVA AI. Grounded in the core principle that clinical authority resides strictly and exclusively with qualified human healthcare professionals, Phase 17 implements:
1. **The Clinician Review Queue:** Deterministic, priority-ordered clinical review queue with explainable operational priority tiers, SLA tracking, and emergency-first flagging.
2. **Review Session Context:** High-fidelity, real-time snapshot of the canonical Master Case (`cases`), combining demographics, vital trends, timeline events, evidence records, triage calculations, and audit history.
3. **Evidence Verification & Modification:** Immutable provenance preservation where original evidence is never overwritten; modifications generate linked revisions with explicit clinician attribution and rationale.
4. **Explicit Conflict Resolution:** Deterministic multi-source discrepancy adjudication where an authoritative evidence item is designated with mandatory clinical rationale, marking superseded records.
5. **Missing Information Lifecycle:** Two-way lifecycle transitioning cases from review to `PENDING_INFORMATION` and automatically returning them to review upon intake of missing data.
6. **Human Decision & Override:** Mandatory clinical rationale for all decisions; mandatory structured override reasons whenever overriding automated risk classifications or clinical pathway suggestions.
7. **Clinical Disposition & Controlled Case Closure:** Authorized transitions to `DISPOSITION_PENDING` and terminal `CLOSED` state, strictly prohibited for unauthorized or non-clinician actors.
8. **Optimistic Concurrency & Transaction Safety:** Enforced `state_version` incrementing on every atomic transition, preventing lost updates and race conditions across distributed clinical stations.

---

## 2. Authoritative Master Case State Machine

The Master Case lifecycle is governed by an immutable finite state machine (`backend/app/domain/state_machine.py`) enforcing legal state transitions and role permissions.

```
       [INTAKE_RECORDED]
               │
               ├───────────────────────(ESCALATE)──────────────────────┐
               ▼                                                       ▼
      [TRIAGE_IN_PROGRESS] ────(SUBMIT_TRIAGE)─────────► [CLINICIAN_REVIEW_REQUIRED]
               │                                                       ▲
      (REQUEST_INFORMATION)                                            │
               ▼                                                       │
      [PENDING_INFORMATION] ───(PROVIDE_INFO / RETURN_TO_REVIEW)───────┤
               │                                                       │
               └───────────────────────(START_REVIEW)──────────────────┼──────┐
                                                                       ▼      │
                                                           [REVIEW_IN_PROGRESS]
                                                                       │
                                                       (RECORD_DECISION / OVERRIDE)
                                                                       ▼
                                                           [DISPOSITION_PENDING]
                                                                       │
                                                       (FINALIZE_DISPOSITION / CLOSE)
                                                                       ▼
                                                                   [CLOSED]
```

### Canonical States:
- `INTAKE_RECORDED`: Master Case initialized with verified patient intake and consent.
- `TRIAGE_PENDING`: Patient awaiting triage assignment.
- `TRIAGE_IN_PROGRESS`: Nursing or point-of-care staff acquiring vitals and clinical observations.
- `PENDING_INFORMATION`: Case paused awaiting specific laboratory, diagnostic, or patient-reported data.
- `CLINICIAN_REVIEW_REQUIRED`: Triage completed or urgent escalation triggered; awaiting physician review.
- `REVIEW_IN_PROGRESS`: Licensed clinician actively inspecting evidence, reconciling conflicts, or verifying data.
- `DISPOSITION_PENDING`: Clinical decision recorded; awaiting final admission, transfer, or discharge orders.
- `CLOSED`: Terminal encounter closure; immutable to further clinical mutation.

---

## 3. Endpoints & API Surface

All Phase 17 endpoints are rooted in `/api/v1/cases` and require Bearer token authentication with facility-scoping validation:

| Method | Endpoint | Authorized Roles | Description |
|---|---|---|---|
| `GET` | `/api/v1/cases/review-queue` | `CLINICIAN`, `DOCTOR`, `SYSTEM_ADMIN`, `AUDITOR` | Retrieves prioritized cases awaiting or undergoing clinical review. |
| `POST` | `/api/v1/cases/{case_id}/review/start` | `CLINICIAN`, `DOCTOR` | Initiates review session, advancing state to `REVIEW_IN_PROGRESS`. |
| `GET` | `/api/v1/cases/{case_id}/review-context` | `CLINICIAN`, `DOCTOR`, `NURSE`, `ADMIN` | Provides 360-degree clinical review context for workbench views. |
| `POST` | `/api/v1/cases/{case_id}/evidence/{evidence_id}/verify` | `CLINICIAN`, `DOCTOR` | Marks evidence as clinically verified with provenance record. |
| `POST` | `/api/v1/cases/{case_id}/evidence/{evidence_id}/modify` | `CLINICIAN`, `DOCTOR` | Modifies evidence value with original record preservation and reason. |
| `POST` | `/api/v1/cases/{case_id}/evidence/{evidence_id}/reject` | `CLINICIAN`, `DOCTOR` | Rejects discrete evidence item with mandatory clinical rationale. |
| `POST` | `/api/v1/cases/{case_id}/evidence/resolve-conflict` | `CLINICIAN`, `DOCTOR` | Designates authoritative evidence or resolved value (case-insensitive) among conflicting data points. |
| `POST` | `/api/v1/cases/{case_id}/request-information` | `CLINICIAN`, `DOCTOR` | Moves case to `PENDING_INFORMATION` with specific information request. |
| `POST` | `/api/v1/cases/{case_id}/provide-information` | `NURSE`, `CLINICIAN`, `PATIENT` | Submits requested data, returning case to `REVIEW_IN_PROGRESS`. |
| `POST` | `/api/v1/cases/{case_id}/decision` | `CLINICIAN`, `DOCTOR` | Records clinical decision (`ACCEPT`, `MODIFY`, `OVERRIDE`, `DEFER`). |
| `POST` | `/api/v1/cases/{case_id}/disposition` | `CLINICIAN`, `DOCTOR` | Records patient disposition and optionally finalizes case closure. |
| `POST` | `/api/v1/cases/{case_id}/close` | `CLINICIAN`, `DOCTOR`, `FACILITY_ADMIN` | Formally closes the case encounter with audit verification. |
| `GET` | `/api/v1/cases/{case_id}/review-history` | `CLINICIAN`, `DOCTOR`, `AUDITOR`, `ADMIN` | Auditable history of all review actions, transitions, and decisions. |

---

## 4. Invariants & Governance Rules

1. **Human Supremacy (Section 20 & DOC-03):**
   Automated algorithmic calculations (NEWS2, Shock Index, priority tiers) serve strictly as deterministic decision support. Every clinical decision, prescription, override, and disposition is enacted exclusively by an authenticated human clinician.
2. **Prohibited Autonomous Actions:**
   Direct execution of `AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, or `AUTHORIZE_PROCEDURE` is unconditionally blocked with HTTP 422 `UNSUPPORTED_OPERATION`.
3. **Mandatory Rationale on Override & Rejection:**
   Whenever a clinician overrides system recommendations or rejects clinical evidence, mandatory non-empty rationale must be supplied.
4. **Optimistic Concurrency Control:**
   Clients submitting state transitions may optionally or mandatorily supply `expected_state_version`. If the database version has advanced, the server rejects the request with HTTP 409 `CONFLICT`.
5. **Immutable Audit Ledger:**
   Every review action (`VERIFY`, `MODIFY`, `REJECT`, `RESOLVE_CONFLICT`, `START_REVIEW`, `DECISION`, `DISPOSITION`, `CLOSE_CASE`) produces an append-only `AuditEvent` record with correlation ID, actor ID, role, and sanitized object IDs.
6. **Closed Case Immutability:**
   Once a case enters `CLOSED`, further evidence verification, modification, conflict resolution, decisions, or dispositions are rejected with HTTP 422 `INVALID_STATE_TRANSITION`.
7. **Review Completion Gate (Requirement 37):**
   Advancing state via `COMPLETE_REVIEW` or `COMPLETE_CLINICAL_REVIEW` strictly requires an existing `ClinicianDecision` record in the database; completing review without a recorded human decision is rejected with HTTP 422 `INVALID_STATE_TRANSITION`.

---

## 5. Verification Record

### Comprehensive Test Suite:
- **Phase 17 Human Review Suite:** 61/61 passed (100%) in `backend/tests/test_phase17_human_review.py`
  - Tests A–AV (45 baseline requirement tests, including evidence rejection, case-insensitive conflict adjudication, and completion invariants)
  - 13 Adversarial Security & Concurrency Tests (spoofing, header tampering, version race, cross-facility tampering, duplicate finalize)
  - 3 Resuscitation Priority & Lifecycle Scenarios
- **Regression Suite (Phases 13–16):** 141/141 passed (100%)
  - Phase 13 Foundation: 26 passed
  - Phase 14 Auth & RBAC: 30 passed
  - Phase 15 Intake & Consent: 37 passed
  - Phase 16 Vitals, Queue & Deterministic Triage: 48 passed
- **Total Combined Backend Tests:** 202 passed (100%)

### Frontend Verification:
- **TypeScript Typecheck:** `npm --prefix frontend run typecheck` — 0 errors
- **ESLint Clean:** `npm --prefix frontend run lint` — 0 errors, 0 warnings
- **Production Build:** `npm --prefix frontend run build` — 15/15 static and dynamic routes compiled successfully

---

## 6. Next Steps (Phase 18 Transition)

Phase 17 establishes the authoritative human validation and state machine barrier. Phase 18 will introduce the AI reasoning layer, ensuring that all generative outputs are strictly funneled into the Phase 17 Human Review Queue as preliminary proposals requiring human clinician verification before taking effect.

**PHASE 17 STATUS: READY FOR HUMAN REVIEW**
