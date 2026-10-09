# CLINOVA AI — Phase 23: Outcome Loop + SignalGraph Implementation Report

## 1. Executive Summary & Objective

Phase 23 establishes the continuous care intelligence loop connecting the patient care pathway, recorded outcomes, **CAREGRAPH** (patient-level state representation), and **SIGNALGRAPH** (system-level epidemiological telemetry).

Crucially, CLINOVA enforces strict epistemological separation across the four distinct stages of clinical care delivery:
1. **AI Recommendation**: What the system suggested (strictly advisory).
2. **Professional Decision**: What the qualified human clinician authorized.
3. **Actual Action**: What operationally happened in practice (e.g. transfer executed, admitted locally, discharged, or unknown).
4. **Recorded Outcome**: What was subsequently observed about the patient's condition (e.g. recovered, stable, deteriorated, or unknown).

None of these four stages are conflated or assumed. An action can take place while its outcome is unknown; a clinician can override an AI recommendation; an authorized transfer may fail or be redirected; and outcomes may be corrected historically without rewriting audit logs.

---

## 2. Four-Way Outcome Data Model

### Database Representation (`CaseOutcome` in [`backend/app/db/models.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/db/models.py))

```python
class CaseOutcome(Base):
    __tablename__ = "case_outcomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), unique=True)
    disposition: Mapped[str] = mapped_column(String(64))
    final_condition: Mapped[str] = mapped_column(String(64), default="STABLE")
    actual_action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default="UNKNOWN")
    recommendation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    professional_decision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    outcome_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default="UNKNOWN")
    recorded_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_corrected: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
```

### Invariant Rules
- **Explicit UNKNOWN Semantics**: When a patient is transferred or discharged and their post-discharge status is not yet confirmed, `outcome_status` is explicitly set to `"UNKNOWN"`. The system never assumes success or recovery.
- **Historical Correction Workflow**: Corrections to recorded outcomes set `is_corrected = True`, increment the integer `version`, and record a `CASE_OUTCOME_CORRECTED` audit event without overwriting historical audit entries.
- **Idempotency**: Retried submissions for an existing outcome update the current record idempotently rather than duplicating database rows or double-counting in telemetry.

---

## 3. CAREGRAPH Outcome Feedback

In [`backend/app/domain/caregraph/engine.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/domain/caregraph/engine.py) and [`backend/app/api/v1/endpoints/caregraph.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/api/v1/endpoints/caregraph.py):

When a case has a recorded outcome:
1. `get_case_caregraph` loads the associated `CaseOutcome` via `selectinload(Case.outcome)`.
2. `build_caregraph_view` appends an authoritative node of type `OUTCOME` to the serialized graph:
   ```json
   {
     "id": "node-outcome-node-case-<id>",
     "type": "OUTCOME",
     "label": "Outcome: RECOVERED",
     "data": {
       "outcome_status": "RECOVERED",
       "actual_action": "DISCHARGED",
       "disposition": "DISCHARGE_HOME",
       "recommendation": "CONTINUE_MEDICATION",
       "professional_decision": "DISCHARGE_WITH_ORAL_ANTIBIOTICS",
       "version": 1,
       "is_corrected": false
     },
     "provenance": "CLINICIAN_VERIFIED",
     "status": "CONFIRMED"
   }
   ```
3. A directed edge connects the encounter node to the outcome node with relation `CONCLUDES_WITH`.
4. The endpoint response returns the full outcome summary packet alongside the trajectory and uncertainty evaluation.

---

## 4. SIGNALGRAPH Telemetry & Privacy Aggregation

In [`backend/app/domain/signalgraph/engine.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/domain/signalgraph/engine.py) and [`backend/app/api/v1/endpoints/signalgraph.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/api/v1/endpoints/signalgraph.py):

- **Event Deduplication**: `signal_engine.record_event()` accepts `source_event_id=outcome.id`. If an event with the same `source_event_id` already exists (due to retries or corrections), it updates fields in place without incrementing event counts or skewing signal statistics.
- **De-identified Macro Telemetry (`GET /api/v1/signalgraph/outcomes`)**: Exposes macro aggregations across facilities and syndromic clusters:
  - `outcome_status_distribution` (counts of RECOVERED, STABLE, DETERIORATED, UNKNOWN, etc.)
  - `actual_action_distribution` (counts of TRANSFERRED, DISCHARGED, ADMITTED_LOCAL, etc.)
  - `disposition_distribution`
  - `unknown_outcomes_count` (explicit count preserving uncertainty)
- **Zero PHI Guarantee**: The endpoint returns strictly anonymized counters, percentages, facility tiers, and syndromic categories. No patient IDs, names, or free-text clinical notes are emitted.

---

## 5. Security & RBAC Enforcement

- **Clinician Sole Authority**: Finalizing case disposition and recording outcomes requires `Permission.DISPOSITION_FINALIZE` (exclusive to `ROLE_CLINICIAN`).
- **Nurses & Patients Blocked**: Nurses and Patients attempting to record outcomes are rejected with HTTP 403 Forbidden.
- **Audit Logging**: Every outcome creation generates `CASE_OUTCOME_RECORDED` in `AuditLog`. Corrections generate `CASE_OUTCOME_CORRECTED` with actor ID and version metadata.

---

## 6. Verification Results

### Dedicated Phase 23 Suite ([`backend/tests/test_phase23_outcome_signalgraph.py`](file:///c:/Users/admin/CLINOVA-AI/backend/tests/test_phase23_outcome_signalgraph.py))
- `test_outcome_creation_and_retrieval`: **PASSED**
- `test_separation_of_recommendation_decision_action_outcome`: **PASSED**
- `test_unknown_outcome_handling`: **PASSED**
- `test_outcome_correction_workflow`: **PASSED**
- `test_duplicate_submission_idempotency`: **PASSED**
- `test_authorization_enforcement`: **PASSED** (401 unauthenticated, 403 nurse, 403 patient)
- `test_caregraph_outcome_node_feedback`: **PASSED** (OUTCOME node, CONCLUDES_WITH edge)
- `test_signalgraph_deduplication_and_privacy_aggregation`: **PASSED**
- `test_failure_recovery_invalid_case`: **PASSED** (404 on invalid case UUID)

**Total Dedicated Phase 23 Tests**: 9 passed (100%).

### Full Phase 18–23 Regression Suite
Ran all test suites from Phase 18 through Phase 23:
- Phase 18 (AI Application Integration): 35 tests
- Phase 19 (Voice / STT / Multimodal Intake): 12 tests
- Phase 20 (OCR + Document Extraction): 6 tests
- Phase 21 (Translation & Multilingual Workflow): 13 tests
- Phase 22 (FacilityGraph, Referral & Care Orchestration): 7 tests
- Phase 23 (Outcome Loop & SignalGraph): 9 tests
- Phase 23 (Migration Verification): 3 tests

**Result**: **95 passed in 89.16s (0:01:29) — 0 failed, 0 skipped**.

---

## 7. Migration Verification & Schema Reproducibility

- **Alembic Migration**: Created [`backend/alembic/versions/0014_phase23_case_outcome_architecture.py`](file:///c:/Users/admin/CLINOVA-AI/backend/alembic/versions/0014_phase23_case_outcome_architecture.py) (`revision: a48b526171bc`, down_revision `f39a415060ab`).
- **Idempotent Dual-Mode DDL**:
  - Fresh databases: creates full `case_outcomes` table with all Phase 23 columns.
  - Pre-existing databases: uses `op.batch_alter_table("case_outcomes")` to inspect existing schema and add missing columns (`actual_action`, `recommendation`, `professional_decision`, `outcome_status`, `recorded_by`, `actor_role`, `is_corrected`, `version`) non-destructively.
- **Runtime Synchronizer**: Updated [`init_db.upgrade_schema_if_needed`](file:///c:/Users/admin/CLINOVA-AI/backend/app/db/init_db.py) to dynamically patch missing columns on standalone SQLite startup.
- **Automated Migration Tests ([`backend/tests/test_phase23_migration.py`](file:///c:/Users/admin/CLINOVA-AI/backend/tests/test_phase23_migration.py))**:
  - `test_migration_on_pre_existing_legacy_database`: verified zero data loss and column addition on existing databases.
  - `test_migration_on_fresh_database`: verified clean creation from scratch.
  - `test_migration_downgrade`: verified safe rollback.

