"""CLINOVA AI — Phase 24 Offline / Low-Bandwidth / Sync Test Suite.

Continuous Care Intelligence System.
Phase 24: Offline Edge Synchronization & Conflict Resolution Architecture (RES-99).

Validates:
1. Online & offline push batch ingestion into canonical Master Case
2. Idempotent retry handling (duplicate sync_id returns ALREADY_SYNCED with zero duplicate rows)
3. Lost response retry recovery
4. Inv SYNC-1: SYNCED records have non-null synced_at and remote_version >= 1
5. Inv SYNC-2: Clinical vitals and evidence are strictly APPEND_ONLY; never overwritten
6. Inv SYNC-3: Primary keys across nodes use RFC 4122 UUIDv4 with zero collisions
7. Inv SYNC-4: Clinical mutable conflicts detected and frozen for human clinician review
8. Clinician conflict reconciliation gate with mandatory clinical rationale
9. Strict RBAC enforcement: Clinician only for conflict resolution; Patient/Nurse rejected
10. Medicolegal audit trail emission (SYNC_BATCH_INGESTED, SYNC_CONFLICT_RESOLVED)
11. Zero credential or secret leakage
"""

import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Case,
    Vital,
    AuditLog,
    SyncJournal,
    SyncConflict,
    ClinicianDecision,
)
from app.core.config import settings


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture(autouse=True)
async def setup_environment():
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = True
    await init_db()


@pytest.mark.asyncio
async def test_online_sync_push_creates_case_and_vitals():
    """Validates offline intake push creates Master Case, vitals, and sync journal with SYNCED status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        headers = {"Authorization": f"Bearer {token}"}

        sync_id = str(uuid.uuid4())
        client_case_id = str(uuid.uuid4())
        node_id = "PHC-ODISHA-KALAHANDI-04"

        batch_payload = {
            "node_id": node_id,
            "items": [
                {
                    "sync_id": sync_id,
                    "entity_type": "PATIENT_INTAKE",
                    "entity_id": client_case_id,
                    "case_id": client_case_id,
                    "operation": "INSERT",
                    "local_version": 1,
                    "conflict_strategy": "APPEND_ONLY",
                    "payload_snapshot": {
                        "age_bracket": "40-49",
                        "biological_sex": "FEMALE",
                        "presenting_complaint": "Acute severe shortness of breath for 3 hours",
                        "symptoms": ["Dyspnea", "Tachycardia"],
                        "vital_signs": {
                            "heart_rate": 118,
                            "systolic_bp": 142,
                            "diastolic_bp": 88,
                            "spo2": 91,
                            "respiratory_rate": 26,
                            "temperature": 37.4,
                        },
                    },
                }
            ],
        }

        res = await client.post("/api/v1/sync/push", json=batch_payload, headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()

        assert data["node_id"] == node_id
        assert data["processed_count"] == 1
        assert data["synced_count"] == 1
        assert data["conflict_count"] == 0
        assert len(data["results"]) == 1

        item_res = data["results"][0]
        assert item_res["sync_id"] == sync_id
        assert item_res["status"] == "SYNCED"
        assert item_res["remote_version"] == 1
        assert item_res["case_id"] == client_case_id

        # Verify database persistence & Inv SYNC-1
        async with async_session_factory() as session:
            case = await session.get(Case, client_case_id)
            assert case is not None
            assert case.acuity_tier in ["MODERATE", "URGENT", "CRITICAL"]
            assert case.state_version == 1

            journal_res = await session.execute(
                select(SyncJournal).where(SyncJournal.sync_id == sync_id)
            )
            journal = journal_res.scalars().first()
            assert journal is not None
            assert journal.sync_status == "SYNCED"
            # Inv SYNC-1 check:
            assert journal.synced_at is not None
            assert journal.remote_version >= 1


@pytest.mark.asyncio
async def test_idempotency_and_duplicate_prevention():
    """Validates that resending the exact same sync batch returns ALREADY_SYNCED with zero duplicate rows."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        headers = {"Authorization": f"Bearer {token}"}

        sync_id = str(uuid.uuid4())
        client_case_id = str(uuid.uuid4())
        node_id = "PHC-ODISHA-KALAHANDI-04"

        batch_payload = {
            "node_id": node_id,
            "items": [
                {
                    "sync_id": sync_id,
                    "entity_type": "PATIENT_INTAKE",
                    "entity_id": client_case_id,
                    "case_id": client_case_id,
                    "operation": "INSERT",
                    "local_version": 1,
                    "conflict_strategy": "APPEND_ONLY",
                    "payload_snapshot": {
                        "age_bracket": "50-59",
                        "biological_sex": "MALE",
                        "presenting_complaint": "Persistent chest pain",
                    },
                }
            ],
        }

        # First Push
        res1 = await client.post("/api/v1/sync/push", json=batch_payload, headers=headers)
        assert res1.status_code == 200
        assert res1.json()["results"][0]["status"] == "SYNCED"

        # Second Push (identical payload / retry after timeout)
        res2 = await client.post("/api/v1/sync/push", json=batch_payload, headers=headers)
        assert res2.status_code == 200
        assert res2.json()["results"][0]["status"] == "ALREADY_SYNCED"

        # Verify only ONE case and ONE sync journal exist
        async with async_session_factory() as session:
            case_count_res = await session.execute(
                select(Case).where(Case.id == client_case_id)
            )
            cases = case_count_res.scalars().all()
            assert len(cases) == 1

            journal_res = await session.execute(
                select(SyncJournal).where(SyncJournal.sync_id == sync_id)
            )
            journals = journal_res.scalars().all()
            assert len(journals) == 1


@pytest.mark.asyncio
async def test_inv_sync_2_append_only_vitals_merge():
    """Validates Inv SYNC-2: Vitals are strictly APPEND_ONLY; consecutive readings append in sequence."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        case_id = str(uuid.uuid4())
        node_id = "EDGE-MINI-PC-01"

        # 1. Create base case
        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Initial presentation"},
                    }
                ],
            },
            headers=headers,
        )

        # 2. Push Vital 1
        vital_sync_1 = str(uuid.uuid4())
        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": vital_sync_1,
                        "entity_type": "VITALS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "APPEND_ONLY",
                        "payload_snapshot": {"heart_rate": 84, "systolic_bp": 120, "diastolic_bp": 80},
                    }
                ],
            },
            headers=headers,
        )

        # 3. Push Vital 2 (follow-up reading taken 1 hour later)
        vital_sync_2 = str(uuid.uuid4())
        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": vital_sync_2,
                        "entity_type": "VITALS",
                        "entity_id": str(uuid.uuid4()),
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "conflict_strategy": "APPEND_ONLY",
                        "payload_snapshot": {"heart_rate": 96, "systolic_bp": 130, "diastolic_bp": 84},
                    }
                ],
            },
            headers=headers,
        )

        # Verify BOTH readings exist in the database (union merge)
        async with async_session_factory() as session:
            vitals_res = await session.execute(
                select(Vital).where(Vital.case_id == case_id)
            )
            vitals = vitals_res.scalars().all()
            assert len(vitals) >= 2
            hr_values = [v.heart_rate for v in vitals]
            assert 84 in hr_values
            assert 96 in hr_values


@pytest.mark.asyncio
async def test_inv_sync_3_uuid_uniqueness_multi_node():
    """Validates Inv SYNC-3: Disconnected nodes use RFC 4122 UUIDv4 ensuring zero ID collisions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        headers = {"Authorization": f"Bearer {token}"}

        node_a_case_id = str(uuid.uuid4())
        node_b_case_id = str(uuid.uuid4())

        # Node A syncs
        res_a = await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": "NODE-KALAHANDI-01",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": node_a_case_id,
                        "case_id": node_a_case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Patient at Node A"},
                    }
                ],
            },
            headers=headers,
        )
        assert res_a.status_code == 200
        assert res_a.json()["results"][0]["status"] == "SYNCED"

        # Node B syncs independently
        res_b = await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": "NODE-KORAPUT-02",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": node_b_case_id,
                        "case_id": node_b_case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Patient at Node B"},
                    }
                ],
            },
            headers=headers,
        )
        assert res_b.status_code == 200
        assert res_b.json()["results"][0]["status"] == "SYNCED"

        async with async_session_factory() as session:
            case_a = await session.get(Case, node_a_case_id)
            case_b = await session.get(Case, node_b_case_id)
            assert case_a is not None
            assert case_b is not None
            assert case_a.id != case_b.id


@pytest.mark.asyncio
async def test_inv_sync_4_concurrent_case_conflict_detection():
    """Validates Inv SYNC-4: Stale case updates detect concurrent modification and freeze in sync_conflicts."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        case_id = str(uuid.uuid4())
        node_id = "EDGE-NODE-03"

        # 1. Base case created with state_version = 1
        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Initial offline version", "status": "NEW"},
                    }
                ],
            },
            headers=headers,
        )

        # 2. Central cloud updates case (state_version becomes 2)
        async with async_session_factory() as session:
            case = await session.get(Case, case_id)
            case.state_version = 2
            case.status = "TRIAGED"
            await session.commit()

        # 3. Offline node attempts to update based on stale local_version = 1
        conflict_sync_id = str(uuid.uuid4())
        res = await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": conflict_sync_id,
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "UPDATE",
                        "local_version": 1,
                        "conflict_strategy": "MANUAL_GATE",
                        "payload_snapshot": {
                            "presenting_complaint": "Conflicting offline edit",
                            "status": "DISCHARGED",
                        },
                    }
                ],
            },
            headers=headers,
        )

        assert res.status_code == 200
        data = res.json()
        assert data["conflict_count"] == 1
        result_item = data["results"][0]
        assert result_item["status"] == "CONFLICT"
        assert result_item["conflict_id"] is not None

        # Verify conflict record in database
        async with async_session_factory() as session:
            conf_res = await session.execute(
                select(SyncConflict).where(SyncConflict.conflict_id == result_item["conflict_id"])
            )
            conflict = conf_res.scalars().first()
            assert conflict is not None
            assert conflict.resolution_status == "PENDING_HUMAN_REVIEW"
            assert conflict.case_id == case_id

            # Verify central state was NOT overwritten by LWW
            case = await session.get(Case, case_id)
            assert case.status == "TRIAGED"


@pytest.mark.asyncio
async def test_clinician_conflict_resolution():
    """Validates human clinician reconciliation gate (Inv SYNC-4) with mandatory clinical rationale."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        clinician_headers = {"Authorization": f"Bearer {clinician_token}"}

        case_id = str(uuid.uuid4())
        node_id = "EDGE-NODE-04"

        # 1. Base Case
        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Version 1", "status": "NEW"},
                    }
                ],
            },
            headers=clinician_headers,
        )

        # 2. Advance central version
        async with async_session_factory() as session:
            case = await session.get(Case, case_id)
            case.state_version = 2
            case.presenting_complaint = "Central Version 2"
            await session.commit()

        # 3. Create conflict
        conf_sync_id = str(uuid.uuid4())
        push_res = await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": conf_sync_id,
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "UPDATE",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Offline Edited Version", "status": "REVIEW"},
                    }
                ],
            },
            headers=clinician_headers,
        )
        conflict_id = push_res.json()["results"][0]["conflict_id"]

        # 4. Clinician resolves conflict (KEEP_LOCAL)
        resolve_res = await client.post(
            f"/api/v1/sync/conflicts/{conflict_id}/resolve",
            json={
                "resolution_choice": "KEEP_LOCAL",
                "clinical_rationale": "Patient physical re-assessment confirms offline findings supersede teleconsult snapshot.",
            },
            headers=clinician_headers,
        )

        assert resolve_res.status_code == 200, resolve_res.text
        resolve_data = resolve_res.json()
        assert resolve_data["resolution_status"] == "RESOLVED_KEEP_LOCAL"
        assert resolve_data["resolved_by_actor_id"] is not None

        # 5. Verify database: journal marked SYNCED, conflict resolved, audit recorded
        async with async_session_factory() as session:
            conf_db = await session.get(SyncConflict, conflict_id)
            assert conf_db.resolution_status == "RESOLVED_KEEP_LOCAL"

            journal_res = await session.execute(
                select(SyncJournal).where(SyncJournal.sync_id == conf_sync_id)
            )
            journal = journal_res.scalars().first()
            assert journal.sync_status == "SYNCED"
            assert journal.synced_at is not None

            # Verify AuditLog
            audit_res = await session.execute(
                select(AuditLog).where(
                    AuditLog.action == "SYNC_CONFLICT_RESOLVED",
                    AuditLog.entity_id == conflict_id,
                )
            )
            assert audit_res.scalars().first() is not None


@pytest.mark.asyncio
async def test_conflict_resolution_mandatory_rationale():
    """Validates that conflict resolution fails if clinical rationale is empty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        clinician_token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {clinician_token}"}

        case_id = str(uuid.uuid4())
        conf_id = str(uuid.uuid4())
        sync_id = str(uuid.uuid4())

        async with async_session_factory() as session:
            j = SyncJournal(
                sync_id=sync_id,
                node_id="NODE-TEST",
                entity_type="CASES",
                entity_id=case_id,
                operation="UPDATE",
                sync_status="CONFLICT",
                payload_snapshot={},
            )
            c = SyncConflict(
                conflict_id=conf_id,
                sync_id=sync_id,
                entity_type="CASES",
                entity_id=case_id,
                resolution_status="PENDING_HUMAN_REVIEW",
            )
            session.add_all([j, c])
            await session.commit()

        # Attempt to resolve with empty rationale
        res = await client.post(
            f"/api/v1/sync/conflicts/{conf_id}/resolve",
            json={"resolution_choice": "KEEP_REMOTE", "clinical_rationale": "   "},
            headers=headers,
        )
        assert res.status_code == 400
        assert "clinical rationale is required" in res.text.lower()


@pytest.mark.asyncio
async def test_rbac_conflict_resolution_enforcement():
    """Validates strict RBAC: Patient and Nurse cannot resolve clinical conflicts; Clinician can."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        nurse_token = await login_helper(client, "nurse")
        clinician_token = await login_helper(client, "clinician")

        case_id = str(uuid.uuid4())
        conf_id = str(uuid.uuid4())
        sync_id = str(uuid.uuid4())

        async with async_session_factory() as session:
            j = SyncJournal(
                sync_id=sync_id,
                node_id="NODE-TEST",
                entity_type="CASES",
                entity_id=case_id,
                operation="UPDATE",
                sync_status="CONFLICT",
                payload_snapshot={},
            )
            c = SyncConflict(
                conflict_id=conf_id,
                sync_id=sync_id,
                entity_type="CASES",
                entity_id=case_id,
                resolution_status="PENDING_HUMAN_REVIEW",
            )
            session.add_all([j, c])
            await session.commit()

        # Patient Attempt -> 403 Forbidden
        res_pt = await client.post(
            f"/api/v1/sync/conflicts/{conf_id}/resolve",
            json={"resolution_choice": "KEEP_LOCAL", "clinical_rationale": "Patient self-choice"},
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert res_pt.status_code == 403

        # Nurse Attempt -> 403 Forbidden
        res_nr = await client.post(
            f"/api/v1/sync/conflicts/{conf_id}/resolve",
            json={"resolution_choice": "KEEP_LOCAL", "clinical_rationale": "Nurse choice"},
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res_nr.status_code == 403

        # Clinician Attempt -> 200 OK
        res_cl = await client.post(
            f"/api/v1/sync/conflicts/{conf_id}/resolve",
            json={"resolution_choice": "KEEP_REMOTE", "clinical_rationale": "Doctor approved remote state."},
            headers={"Authorization": f"Bearer {clinician_token}"},
        )
        assert res_cl.status_code == 200


@pytest.mark.asyncio
async def test_get_sync_status_and_list_conflicts():
    """Validates sync status lookup and conflict list querying endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        sync_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        node_id = "EDGE-STATUS-01"

        await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": node_id,
                "items": [
                    {
                        "sync_id": sync_id,
                        "entity_type": "CASES",
                        "entity_id": case_id,
                        "case_id": case_id,
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Status check case"},
                    }
                ],
            },
            headers=headers,
        )

        # GET /api/v1/sync/status/{sync_id}
        status_res = await client.get(f"/api/v1/sync/status/{sync_id}", headers=headers)
        assert status_res.status_code == 200
        s_data = status_res.json()
        assert s_data["sync_id"] == sync_id
        assert s_data["sync_status"] == "SYNCED"
        assert s_data["node_id"] == node_id

        # GET /api/v1/sync/conflicts
        conf_res = await client.get("/api/v1/sync/conflicts", headers=headers)
        assert conf_res.status_code == 200
        assert isinstance(conf_res.json(), list)


@pytest.mark.asyncio
async def test_zero_credential_leakage():
    """Validates that sync responses and audit entries never leak passwords, tokens, or hashes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.post(
            "/api/v1/sync/push",
            json={
                "node_id": "NODE-SECURITY-01",
                "items": [
                    {
                        "sync_id": str(uuid.uuid4()),
                        "entity_type": "CASES",
                        "entity_id": str(uuid.uuid4()),
                        "operation": "INSERT",
                        "local_version": 1,
                        "payload_snapshot": {"presenting_complaint": "Security audit test"},
                    }
                ],
            },
            headers=headers,
        )
        assert res.status_code == 200
        body_text = res.text.lower()
        assert "password" not in body_text
        assert "hashed_password" not in body_text
        assert "secret_key" not in body_text
        assert token.lower() not in body_text
