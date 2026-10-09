# CLINOVA AI — Phase 24: Offline / Low-Bandwidth / Sync Implementation Report

## 1. Executive Summary & Objective

Phase 24 implements and verifies reliable, resilient offline and low-bandwidth synchronization behavior for the canonical CLINOVA AI workflow:
**Offline Intake → Temporary Local Capture → Connection Restored → Safe Sync / Retry → Backend Persistence → Consistency Verification**

Rural Primary Health Centres (PHCs) and community outreach camps across Odisha routinely experience electrical outages and cellular uplink dropouts. During these periods, healthcare workers must continue taking patient intakes, recording vital signs, and conducting clinical reviews locally. When connectivity returns, the local node synchronizes with the central cloud hub safely, preserving one canonical Master Case without duplicate submissions, silent overwrites, or data loss.

---

## 2. Invariants & Conflict Resolution Strategies (RES-99)

Grounding: `docs/research/99_OFFLINE_SYNC_MODEL.md` (`RES-99`).

### Formal Invariants
- $\mathbf{Inv\ SYNC\text{-}1}$: $\forall j \in \text{SyncJournals}, j.\text{sync\_status} = \text{'SYNCED'} \implies j.\text{synced\_at} \neq \text{NULL} \land j.\text{remote\_version} \ge 1$
- $\mathbf{Inv\ SYNC\text{-}2}$: Clinical events, vital readings, notes, and evidence are strictly $\text{APPEND\_ONLY}$; non-destructive union with `offline_captured: true`.
- $\mathbf{Inv\ SYNC\text{-}3}$: Primary keys across all entities use RFC 4122 UUIDv4; zero collision between disconnected nodes.
- $\mathbf{Inv\ SYNC\text{-}4}$: Clinical disposition and triage conflicts require human clinician sign-off ($\text{PENDING\_HUMAN\_REVIEW}$); silent overwrite by Last-Write-Wins (LWW) is forbidden.

### Four Canonical Conflict Resolution Strategies
1. `STRAT_APPEND` (**Append-Only Merging**): Non-destructive chronological union for vitals, evidence, and timeline events.
2. `STRAT_CLINICIAN` (**Clinician Monopoly Wins**): Qualified human doctor decisions supersede AI inferences or staff drafts.
3. `STRAT_LWW` (**Last-Write-Wins**): Applied strictly to non-clinical metadata (e.g., contact phone number, spelling).
4. `STRAT_MANUAL` (**Manual Reconciliation Gate**): Conflicting clinical state freezes in `sync_conflicts` for human sign-off with mandatory clinical rationale.

---

## 3. Relational Schema Architecture

### Database Models ([`backend/app/db/models.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/db/models.py))

#### `SyncJournal` (`sync_journals`)
```python
class SyncJournal(Base):
    __tablename__ = "sync_journals"

    sync_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    node_id: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    operation: Mapped[str] = mapped_column(String(16))  # INSERT, UPDATE, TOMBSTONE
    local_version: Mapped[int] = mapped_column(Integer, default=1)
    remote_version: Mapped[int] = mapped_column(Integer, default=0)
    sync_status: Mapped[str] = mapped_column(String(32), default="PENDING_UPLOAD", index=True)  # PENDING_UPLOAD, SYNCED, CONFLICT, FAILED
    payload_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    conflict_strategy: Mapped[str] = mapped_column(String(32), default="APPEND_ONLY")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    case = relationship("Case", back_populates="sync_journals")
    conflicts = relationship("SyncConflict", back_populates="journal", cascade="all, delete-orphan")
```

#### `SyncConflict` (`sync_conflicts`)
```python
class SyncConflict(Base):
    __tablename__ = "sync_conflicts"

    conflict_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sync_id: Mapped[str] = mapped_column(String(36), ForeignKey("sync_journals.sync_id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    local_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    remote_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    resolution_status: Mapped[str] = mapped_column(String(32), default="PENDING_HUMAN_REVIEW", index=True)
    resolved_by_actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    journal = relationship("SyncJournal", back_populates="conflicts")
```

### Alembic Migration ([`backend/alembic/versions/0015_phase24_offline_sync_architecture.py`](file:///c:/Users/admin/CLINOVA-AI/backend/alembic/versions/0015_phase24_offline_sync_architecture.py))
- Revision ID: `b84f3782910c`
- Down Revision: `a48b526171bc` (Phase 23 migration)
- Idempotently provisions `sync_journals` and `sync_conflicts` tables with appropriate foreign keys and indexes.

---

## 4. API Endpoints ([`backend/app/api/v1/endpoints/sync.py`](file:///c:/Users/admin/CLINOVA-AI/backend/app/api/v1/endpoints/sync.py))

Mounted under `/api/v1/sync`:

| Method | Path | Required Permission | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/sync/push` | `Permission.SYNC_PUSH` | Ingests ordered batch of offline sync journals with idempotency and conflict gating. |
| `GET` | `/api/v1/sync/status/{sync_id}` | `Permission.SYNC_READ` | Retrieves sync status, remote version, and any associated conflict state. |
| `GET` | `/api/v1/sync/conflicts` | `Permission.SYNC_READ` | Lists pending sync conflicts filtered by `case_id` and `resolution_status`. |
| `POST` | `/api/v1/sync/conflicts/{conflict_id}/resolve` | `Permission.SYNC_RESOLVE` | Clinician-only reconciliation gate. Requires mandatory clinical rationale. |

---

## 5. Client-Side Offline Queue & UI Integration

- **Persistent Queue** ([`frontend/src/lib/offlineQueue.ts`](file:///c:/Users/admin/CLINOVA-AI/frontend/src/lib/offlineQueue.ts)):
  - Backed by browser `localStorage` (`clinova_offline_sync_queue`).
  - Automatically captures intakes and clinical measurements when offline as `PENDING_UPLOAD`.
  - Dispatches `clinova:sync_queue_updated` events.
  - Automatically triggers `processOfflineSync` upon window `online` reconnection events.
- **Intake Flow Integration** ([`frontend/src/lib/api.ts`](file:///c:/Users/admin/CLINOVA-AI/frontend/src/lib/api.ts)):
  - In `submitPatientIntake`, network dropouts enqueue the intake with `sync_id` (UUIDv4) into the offline queue without data loss.
- **ConnectionStatus Component** ([`frontend/src/components/common/ConnectionStatus.tsx`](file:///c:/Users/admin/CLINOVA-AI/frontend/src/components/common/ConnectionStatus.tsx)):
  - Dynamically displays queued sync item count.
  - Shows animated `SYNCING` state during background push and returns to `SYNCED`.

---

## 6. Verification & Test Results

### Dedicated Phase 24 Test Suite (`backend/tests/test_phase24_offline_sync.py`)
10 tests executed and passed (100% pass rate):
- `test_online_sync_push_creates_case_and_vitals`: **PASSED**
- `test_idempotency_and_duplicate_prevention`: **PASSED**
- `test_inv_sync_2_append_only_vitals_merge`: **PASSED**
- `test_inv_sync_3_uuid_uniqueness_multi_node`: **PASSED**
- `test_inv_sync_4_concurrent_case_conflict_detection`: **PASSED**
- `test_clinician_conflict_resolution`: **PASSED**
- `test_conflict_resolution_mandatory_rationale`: **PASSED**
- `test_rbac_conflict_resolution_enforcement`: **PASSED**
- `test_get_sync_status_and_list_conflicts`: **PASSED**
- `test_zero_credential_leakage`: **PASSED**

### Full Regression Test Suite (Phases 18–24)
Executed across all consecutive integration layers:
- Phase 18 (AI Application Integration): 45 tests passed
- Phase 19 (Voice / STT / Multimodal Intake): 13 tests passed
- Phase 20 (OCR + Report Extraction): 6 tests passed
- Phase 21 (Translation + Multilingual): 12 tests passed
- Phase 22 (FacilityGraph + Care Orchestration): 7 tests passed
- Phase 23 (Outcome Loop + SignalGraph): 9 tests passed
- Phase 23 (Migration Verification): 3 tests passed
- Phase 24 (Offline Edge Sync & Conflict Resolution): 10 tests passed
- **Total Suite**: **105 passed in 88.61s (0:01:28)** — 0 failed, 0 skipped.

### Frontend Quality Gates
- `npm run typecheck --prefix frontend`: **0 errors (passed)**
- `npm run lint --prefix frontend`: **0 warnings, 0 errors (passed)**
- Alembic head: `b84f3782910c (head)` **(verified)**
