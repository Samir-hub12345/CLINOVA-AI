"""CLINOVA AI — Offline Edge Synchronization & Conflict Resolution Router.

Continuous Care Intelligence System.
Phase 24: Offline / Low-Bandwidth / Sync Architecture.
Grounded in RES-99 (Offline Edge Synchronization & Conflict Resolution Model).

Invariants Enforced:
- Inv SYNC-1: When sync_status == 'SYNCED', synced_at is non-null and remote_version >= 1.
- Inv SYNC-2: Clinical events and vital readings are strictly APPEND_ONLY; never overwritten.
- Inv SYNC-3: Primary keys across all entities use RFC 4122 UUIDv4; zero collision between nodes.
- Inv SYNC-4: Clinical decisions & dispositions NEVER silently overwritten by LWW; frozen for human review.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import (
    Case,
    Patient,
    PatientIdentifier,
    Encounter,
    Vital,
    VitalReading,
    EvidenceRecord,
    TimelineEvent,
    ClinicianDecision,
    CaseOutcome,
    AuditLog,
    SyncJournal,
    SyncConflict,
    utc_now,
    generate_uuid,
)
from app.domain.triage import compute_deterministic_triage
from app.core.auth import get_current_actor, ActorContext
from app.core.rbac import (
    Permission,
    check_role_permission,
    ROLE_CLINICIAN,
    ROLE_DOCTOR,
    ROLE_SYSTEM_ADMIN,
    ROLE_AUDITOR,
    ROLE_NURSE,
    ROLE_PATIENT,
    PROHIBITED_CLINICAL_ACTIONS,
)
from app.core.policy import authorize_case_access
from app.core.errors import ClinovaAPIError

router = APIRouter()


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------

class SyncJournalItemIn(BaseModel):
    sync_id: str
    entity_type: str  # CASES, PATIENT_INTAKE, VITALS, EVIDENCE, TIMELINE_EVENTS, CLINICIAN_DECISIONS, CASE_OUTCOMES
    entity_id: str
    case_id: Optional[str] = None
    operation: str = "INSERT"  # INSERT, UPDATE, TOMBSTONE
    local_version: int = 1
    conflict_strategy: Optional[str] = "APPEND_ONLY"  # APPEND_ONLY, CLINICIAN_WINS, LAST_WRITE_WINS, MANUAL_GATE
    payload_snapshot: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class SyncPushBatchRequest(BaseModel):
    node_id: str
    items: List[SyncJournalItemIn]


class SyncItemResult(BaseModel):
    sync_id: str
    entity_type: str
    entity_id: str
    case_id: Optional[str] = None
    status: str  # SYNCED, ALREADY_SYNCED, CONFLICT, FAILED
    remote_version: int = 1
    conflict_id: Optional[str] = None
    message: str = "Synchronized successfully."


class SyncPushBatchResponse(BaseModel):
    node_id: str
    batch_id: str
    processed_count: int
    synced_count: int
    conflict_count: int
    failed_count: int
    results: List[SyncItemResult]


class SyncConflictResolveRequest(BaseModel):
    resolution_choice: str  # KEEP_LOCAL, KEEP_REMOTE, MERGE
    merged_payload: Optional[Dict[str, Any]] = None
    clinical_rationale: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/push", response_model=SyncPushBatchResponse, tags=["Offline Sync"])
async def push_sync_batch(
    payload: SyncPushBatchRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Ingests an ordered batch of offline sync journal items from edge nodes or client devices.
    Enforces idempotency, append-only invariants for clinical data, and human gates for clinical conflicts.
    """
    check_role_permission(actor.role, Permission.SYNC_PUSH)

    batch_id = str(uuid.uuid4())
    results: List[SyncItemResult] = []
    synced_count = 0
    conflict_count = 0
    failed_count = 0

    for item in payload.items:
        try:
            # 1. Idempotency Check (Inv SYNC-1 & Safe Retry)
            existing_journal_res = await db.execute(
                select(SyncJournal).where(SyncJournal.sync_id == item.sync_id)
            )
            existing_journal = existing_journal_res.scalars().first()

            if existing_journal:
                if existing_journal.sync_status == "SYNCED":
                    # Detect operation ID reuse with conflicting entity or payload (tampering/replay protection)
                    def normalize_entity_type(et: str) -> str:
                        et = (et or "").upper()
                        if et in ["PATIENT_INTAKE", "CASES", "CASE"]:
                            return "CASES"
                        if et in ["VITALS", "VITAL_READINGS"]:
                            return "VITALS"
                        if et in ["EVIDENCE", "EVIDENCE_RECORDS"]:
                            return "EVIDENCE"
                        if et in ["TIMELINE_EVENTS", "TIMELINE"]:
                            return "TIMELINE"
                        if et in ["CLINICIAN_DECISIONS", "DECISIONS"]:
                            return "CLINICIAN_DECISIONS"
                        if et in ["CASE_OUTCOMES", "OUTCOMES"]:
                            return "CASE_OUTCOMES"
                        return et

                    def payloads_match(p1: Any, p2: Any) -> bool:
                        if p1 == p2:
                            return True
                        if isinstance(p1, str) and isinstance(p2, dict):
                            try:
                                return json.loads(p1) == p2
                            except Exception:
                                return False
                        if isinstance(p1, dict) and isinstance(p2, str):
                            try:
                                return p1 == json.loads(p2)
                            except Exception:
                                return False
                        return False

                    if (
                        normalize_entity_type(existing_journal.entity_type) != normalize_entity_type(item.entity_type)
                        or not payloads_match(existing_journal.payload_snapshot, item.payload_snapshot)
                    ):
                        results.append(
                            SyncItemResult(
                                sync_id=item.sync_id,
                                entity_type=item.entity_type,
                                entity_id=item.entity_id,
                                case_id=item.case_id,
                                status="FAILED",
                                remote_version=existing_journal.remote_version,
                                conflict_id=None,
                                message="Operation ID reused with conflicting payload (tampering/replay detected).",
                            )
                        )
                        failed_count += 1
                        continue

                    results.append(
                        SyncItemResult(
                            sync_id=item.sync_id,
                            entity_type=existing_journal.entity_type,
                            entity_id=existing_journal.entity_id,
                            case_id=existing_journal.case_id,
                            status="ALREADY_SYNCED",
                            remote_version=existing_journal.remote_version,
                            conflict_id=None,
                            message="Idempotent: item was already synchronized previously.",
                        )
                    )
                    synced_count += 1
                    continue
                elif existing_journal.sync_status == "CONFLICT":
                    conf_res = await db.execute(
                        select(SyncConflict).where(SyncConflict.sync_id == item.sync_id)
                    )
                    conf_rec = conf_res.scalars().first()
                    results.append(
                        SyncItemResult(
                            sync_id=item.sync_id,
                            entity_type=existing_journal.entity_type,
                            entity_id=existing_journal.entity_id,
                            case_id=existing_journal.case_id,
                            status="CONFLICT",
                            remote_version=existing_journal.remote_version,
                            conflict_id=conf_rec.conflict_id if conf_rec else None,
                            message="Item is in conflict and awaiting clinician review.",
                        )
                    )
                    conflict_count += 1
                    continue

            # 2. Entity Dispatched Handling
            entity_type_upper = item.entity_type.upper()
            target_case_id = item.case_id

            # Role-based restriction on clinical mutations via sync push
            if actor.role == ROLE_PATIENT:
                if entity_type_upper in ["CLINICIAN_DECISIONS", "DECISIONS", "CASE_OUTCOMES", "OUTCOMES"]:
                    results.append(
                        SyncItemResult(
                            sync_id=item.sync_id,
                            entity_type=item.entity_type,
                            entity_id=item.entity_id,
                            case_id=item.case_id,
                            status="FAILED",
                            remote_version=0,
                            conflict_id=None,
                            message="Authorization error: Patient role cannot synchronize clinical decisions or outcomes.",
                        )
                    )
                    failed_count += 1
                    continue
            elif actor.role == ROLE_NURSE:
                if entity_type_upper in ["CLINICIAN_DECISIONS", "DECISIONS"]:
                    results.append(
                        SyncItemResult(
                            sync_id=item.sync_id,
                            entity_type=item.entity_type,
                            entity_id=item.entity_id,
                            case_id=item.case_id,
                            status="FAILED",
                            remote_version=0,
                            conflict_id=None,
                            message="Authorization error: Nurse role cannot synchronize clinician decisions.",
                        )
                    )
                    failed_count += 1
                    continue

            if entity_type_upper in ["PATIENT_INTAKE", "CASES", "CASE"]:
                res = await _handle_case_sync(item, payload.node_id, actor, db)
                results.append(res)
                if res.status == "SYNCED":
                    synced_count += 1
                elif res.status == "CONFLICT":
                    conflict_count += 1
                else:
                    failed_count += 1

            elif entity_type_upper in ["VITALS", "VITAL_READINGS"]:
                res = await _handle_vitals_sync(item, payload.node_id, actor, db)
                results.append(res)
                synced_count += 1

            elif entity_type_upper in ["EVIDENCE", "EVIDENCE_RECORDS"]:
                res = await _handle_evidence_sync(item, payload.node_id, actor, db)
                results.append(res)
                synced_count += 1

            elif entity_type_upper in ["TIMELINE_EVENTS", "TIMELINE"]:
                res = await _handle_timeline_sync(item, payload.node_id, actor, db)
                results.append(res)
                synced_count += 1

            elif entity_type_upper in ["CLINICIAN_DECISIONS", "DECISIONS"]:
                res = await _handle_decision_sync(item, payload.node_id, actor, db)
                results.append(res)
                if res.status == "SYNCED":
                    synced_count += 1
                elif res.status == "CONFLICT":
                    conflict_count += 1
                else:
                    failed_count += 1

            elif entity_type_upper in ["CASE_OUTCOMES", "OUTCOMES"]:
                res = await _handle_outcome_sync(item, payload.node_id, actor, db)
                results.append(res)
                if res.status == "SYNCED":
                    synced_count += 1
                elif res.status == "CONFLICT":
                    conflict_count += 1
                else:
                    failed_count += 1

            else:
                # Generic fallback: append-only journal recording
                new_journal = SyncJournal(
                    sync_id=item.sync_id,
                    node_id=payload.node_id,
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    case_id=item.case_id,
                    operation=item.operation,
                    local_version=item.local_version,
                    remote_version=1,
                    sync_status="SYNCED",
                    payload_snapshot=item.payload_snapshot,
                    conflict_strategy=item.conflict_strategy or "APPEND_ONLY",
                    created_at=item.created_at or utc_now(),
                    synced_at=utc_now(),
                )
                db.add(new_journal)
                results.append(
                    SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type=item.entity_type,
                        entity_id=item.entity_id,
                        case_id=item.case_id,
                        status="SYNCED",
                        remote_version=1,
                        message="Generic entity recorded in sync journal.",
                    )
                )
                synced_count += 1

        except Exception as e:
            failed_count += 1
            results.append(
                SyncItemResult(
                    sync_id=item.sync_id,
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    case_id=item.case_id,
                    status="FAILED",
                    remote_version=0,
                    message=f"Sync processing error: {str(e)}",
                )
            )

    # 3. Medicolegal Audit Entry for Sync Batch Ingestion
    audit = AuditLog(
        actor_id=actor.actor_id,
        action="SYNC_BATCH_INGESTED",
        entity_type="SYNC_BATCH",
        entity_id=batch_id,
        details={
            "node_id": payload.node_id,
            "total_items": len(payload.items),
            "synced_count": synced_count,
            "conflict_count": conflict_count,
            "failed_count": failed_count,
        },
        timestamp=utc_now(),
    )
    db.add(audit)
    await db.commit()

    return SyncPushBatchResponse(
        node_id=payload.node_id,
        batch_id=batch_id,
        processed_count=len(payload.items),
        synced_count=synced_count,
        conflict_count=conflict_count,
        failed_count=failed_count,
        results=results,
    )


@router.get("/status/{sync_id}", tags=["Offline Sync"])
async def get_sync_status(
    sync_id: str,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Retrieves synchronization journal record and any associated conflict state."""
    check_role_permission(actor.role, Permission.SYNC_READ)

    stmt = select(SyncJournal).where(SyncJournal.sync_id == sync_id)
    res = await db.execute(stmt)
    journal = res.scalars().first()

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync journal record {sync_id} not found",
        )

    conflict_data = None
    if journal.sync_status == "CONFLICT":
        conf_res = await db.execute(
            select(SyncConflict).where(SyncConflict.sync_id == sync_id)
        )
        conf = conf_res.scalars().first()
        if conf:
            conflict_data = {
                "conflict_id": conf.conflict_id,
                "resolution_status": conf.resolution_status,
                "local_payload": conf.local_payload,
                "remote_payload": conf.remote_payload,
                "created_at": conf.created_at.isoformat() if conf.created_at else None,
            }

    return {
        "sync_id": journal.sync_id,
        "node_id": journal.node_id,
        "entity_type": journal.entity_type,
        "entity_id": journal.entity_id,
        "case_id": journal.case_id,
        "operation": journal.operation,
        "local_version": journal.local_version,
        "remote_version": journal.remote_version,
        "sync_status": journal.sync_status,
        "conflict_strategy": journal.conflict_strategy,
        "created_at": journal.created_at.isoformat() if journal.created_at else None,
        "synced_at": journal.synced_at.isoformat() if journal.synced_at else None,
        "conflict": conflict_data,
    }


@router.get("/conflicts", tags=["Offline Sync"])
async def list_sync_conflicts(
    case_id: Optional[str] = None,
    resolution_status: Optional[str] = "PENDING_HUMAN_REVIEW",
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """Queries active synchronization conflicts awaiting clinician or staff resolution."""
    check_role_permission(actor.role, Permission.SYNC_READ)

    stmt = select(SyncConflict)
    if case_id:
        stmt = stmt.where(SyncConflict.case_id == case_id)
    if resolution_status:
        stmt = stmt.where(SyncConflict.resolution_status == resolution_status)
    stmt = stmt.order_by(desc(SyncConflict.created_at))

    res = await db.execute(stmt)
    conflicts = res.scalars().all()

    return [
        {
            "conflict_id": c.conflict_id,
            "sync_id": c.sync_id,
            "entity_type": c.entity_type,
            "entity_id": c.entity_id,
            "case_id": c.case_id,
            "local_payload": c.local_payload,
            "remote_payload": c.remote_payload,
            "resolution_status": c.resolution_status,
            "resolved_by_actor_id": c.resolved_by_actor_id,
            "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
            "resolution_notes": c.resolution_notes,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in conflicts
    ]


@router.post("/conflicts/{conflict_id}/resolve", tags=["Offline Sync"])
async def resolve_sync_conflict(
    conflict_id: str,
    resolution: SyncConflictResolveRequest,
    db: AsyncSession = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor),
):
    """
    Authoritative Clinician-Only Reconciliation Gate (Inv SYNC-4 / RES-99).
    Resolves frozen synchronization conflicts using explicit clinical rationale.
    """
    check_role_permission(actor.role, Permission.SYNC_RESOLVE)

    if not resolution.clinical_rationale or not resolution.clinical_rationale.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory clinical rationale is required to resolve a clinical sync conflict.",
        )

    stmt = select(SyncConflict).where(SyncConflict.conflict_id == conflict_id)
    res = await db.execute(stmt)
    conflict = res.scalars().first()

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conflict {conflict_id} not found",
        )

    if conflict.resolution_status != "PENDING_HUMAN_REVIEW":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conflict {conflict_id} has already been resolved ({conflict.resolution_status}).",
        )

    choice = resolution.resolution_choice.upper()
    if choice not in ["KEEP_LOCAL", "KEEP_REMOTE", "MERGE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resolution_choice. Allowed values: KEEP_LOCAL, KEEP_REMOTE, MERGE.",
        )

    # 1. Update target entity based on choice
    if conflict.case_id:
        case_res = await db.execute(select(Case).where(Case.id == conflict.case_id))
        case = case_res.scalars().first()
        if case:
            if actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
                if actor.facility_id and case.facility_id and actor.facility_id != case.facility_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cross-facility conflict resolution prohibited.",
                    )
            if choice == "KEEP_LOCAL":
                lp = conflict.local_payload
                if "presenting_complaint" in lp:
                    case.presenting_complaint = lp["presenting_complaint"]
                if "status" in lp:
                    case.status = lp["status"]
                if "acuity_tier" in lp:
                    case.acuity_tier = lp["acuity_tier"]
                case.state_version += 1
            elif choice == "MERGE" and resolution.merged_payload:
                mp = resolution.merged_payload
                if "presenting_complaint" in mp:
                    case.presenting_complaint = mp["presenting_complaint"]
                if "status" in mp:
                    case.status = mp["status"]
                if "acuity_tier" in mp:
                    case.acuity_tier = mp["acuity_tier"]
                case.state_version += 1

    # 2. Update SyncConflict record
    conflict.resolution_status = f"RESOLVED_{choice}" if choice != "MERGE" else "RESOLVED_MERGED"
    conflict.resolved_by_actor_id = actor.actor_id
    conflict.resolved_at = utc_now()
    conflict.resolution_notes = resolution.clinical_rationale.strip()

    # 3. Update SyncJournal record to SYNCED (Inv SYNC-1)
    j_res = await db.execute(select(SyncJournal).where(SyncJournal.sync_id == conflict.sync_id))
    journal = j_res.scalars().first()
    if journal:
        journal.sync_status = "SYNCED"
        journal.synced_at = utc_now()
        journal.remote_version += 1

    # 4. Audit Log
    db.add(
        AuditLog(
            actor_id=actor.actor_id,
            action="SYNC_CONFLICT_RESOLVED",
            entity_type="SYNC_CONFLICT",
            entity_id=conflict_id,
            details={
                "sync_id": conflict.sync_id,
                "case_id": conflict.case_id,
                "resolution_choice": choice,
                "rationale": resolution.clinical_rationale,
            },
            timestamp=utc_now(),
        )
    )

    await db.commit()

    return {
        "conflict_id": conflict.conflict_id,
        "sync_id": conflict.sync_id,
        "resolution_status": conflict.resolution_status,
        "resolved_by_actor_id": conflict.resolved_by_actor_id,
        "resolved_at": conflict.resolved_at.isoformat() if conflict.resolved_at else None,
        "resolution_notes": conflict.resolution_notes,
    }


# ---------------------------------------------------------------------------
# Internal Entity Handlers
# ---------------------------------------------------------------------------

async def _handle_case_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Handles sync for Case / Patient Intake entities with version checks and conflict gating."""
    target_case_id = item.entity_id or item.case_id

    # Check if case exists
    stmt = select(Case).where(Case.id == target_case_id)
    res = await db.execute(stmt)
    case = res.scalars().first()

    payload = item.payload_snapshot

    if not case:
        # Create Patient, Encounter, Case (Inv SYNC-3: client UUIDv4)
        synth_pt_id = f"SYN-PT-{uuid.uuid4().hex[:6].upper()}"
        patient = Patient(
            id=str(uuid.uuid4()),
            synthetic_id=synth_pt_id,
            age_bracket=payload.get("age_bracket", payload.get("reported_age_bracket", "30-39")),
            biological_sex=payload.get("biological_sex", "UNKNOWN"),
            is_synthetic=True,
            created_at=item.created_at or utc_now(),
        )
        db.add(patient)
        await db.flush()

        facility_id = payload.get("facility_id", actor.facility_id or "FAC-PHC-01")
        encounter = Encounter(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            facility_id=facility_id,
            pathway=payload.get("pathway", "REGULAR_STANDARD"),
            started_at=item.created_at or utc_now(),
        )
        db.add(encounter)
        await db.flush()

        case_num = payload.get("case_number") or f"CAS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        complaint = payload.get("presenting_complaint", payload.get("chief_complaint", ""))
        vitals_data = payload.get("vital_signs", {})
        symptoms = payload.get("symptoms", [])

        # Deterministic triage calculation
        triage_res = compute_deterministic_triage(
            case_id=target_case_id,
            pathway=encounter.pathway,
            current_state=payload.get("current_state", "INTAKE_RECORDED"),
            presenting_complaint=complaint,
            latest_vital=vitals_data,
            extracted_symptoms=symptoms,
        )

        case = Case(
            id=target_case_id,
            case_number=case_num,
            patient_id=patient.id,
            encounter_id=encounter.id,
            facility_id=facility_id,
            pathway=encounter.pathway,
            current_state=payload.get("current_state", "INTAKE_RECORDED"),
            status=payload.get("status", "NEW"),
            acuity_tier=triage_res.get("acuity_tier", "ROUTINE"),
            risk_score=triage_res.get("risk_score", 0.1),
            uncertainty_score=0.4,
            state_version=1,
            presenting_complaint=complaint,
            created_at=item.created_at or utc_now(),
        )
        db.add(case)
        await db.flush()

        # If vitals present in payload, record them
        if vitals_data:
            vital_rec = Vital(
                id=str(uuid.uuid4()),
                case_id=case.id,
                heart_rate=vitals_data.get("heart_rate"),
                systolic_bp=vitals_data.get("systolic_bp"),
                diastolic_bp=vitals_data.get("diastolic_bp"),
                spo2_percent=vitals_data.get("spo2"),
                respiratory_rate=vitals_data.get("respiratory_rate"),
                temperature_celsius=vitals_data.get("temperature"),
                provenance_metadata={"offline_captured": True, "sync_id": item.sync_id, "node_id": node_id},
                created_at=item.created_at or utc_now(),
            )
            db.add(vital_rec)

        # Record SyncJournal (Inv SYNC-1)
        journal = SyncJournal(
            sync_id=item.sync_id,
            node_id=node_id,
            entity_type="CASES",
            entity_id=case.id,
            case_id=case.id,
            operation="INSERT",
            local_version=item.local_version,
            remote_version=1,
            sync_status="SYNCED",
            payload_snapshot=item.payload_snapshot,
            conflict_strategy=item.conflict_strategy or "APPEND_ONLY",
            created_at=item.created_at or utc_now(),
            synced_at=utc_now(),
        )
        db.add(journal)

        return SyncItemResult(
            sync_id=item.sync_id,
            entity_type="CASES",
            entity_id=case.id,
            case_id=case.id,
            status="SYNCED",
            remote_version=1,
            message="Offline case intake persisted successfully.",
        )

    else:
        # Case already exists: verify authorization and scoping
        if actor.role == ROLE_PATIENT:
            if not actor.patient_id or case.patient_id != actor.patient_id:
                return SyncItemResult(
                    sync_id=item.sync_id,
                    entity_type="CASES",
                    entity_id=case.id,
                    case_id=case.id,
                    status="FAILED",
                    remote_version=case.state_version,
                    message="Authorization error: Patient cannot synchronize case of another patient.",
                )
        elif actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
            if actor.facility_id and case.facility_id and actor.facility_id != case.facility_id:
                return SyncItemResult(
                    sync_id=item.sync_id,
                    entity_type="CASES",
                    entity_id=case.id,
                    case_id=case.id,
                    status="FAILED",
                    remote_version=case.state_version,
                    message="Authorization error: Cross-facility synchronization prohibited.",
                )

        # Case already exists: compare versions
        if case.state_version == item.local_version:
            # Safe non-conflicting update
            if "presenting_complaint" in payload and payload["presenting_complaint"]:
                case.presenting_complaint = payload["presenting_complaint"]
            case.state_version += 1

            journal = SyncJournal(
                sync_id=item.sync_id,
                node_id=node_id,
                entity_type="CASES",
                entity_id=case.id,
                case_id=case.id,
                operation="UPDATE",
                local_version=item.local_version,
                remote_version=case.state_version,
                sync_status="SYNCED",
                payload_snapshot=item.payload_snapshot,
                conflict_strategy=item.conflict_strategy or "APPEND_ONLY",
                created_at=item.created_at or utc_now(),
                synced_at=utc_now(),
            )
            db.add(journal)

            return SyncItemResult(
                sync_id=item.sync_id,
                entity_type="CASES",
                entity_id=case.id,
                case_id=case.id,
                status="SYNCED",
                remote_version=case.state_version,
                message="Case state synchronized with version increment.",
            )
        else:
            # Concurrent mutation detected: local_version != remote state_version
            # Gated by Inv SYNC-4: Clinical state conflicts must NOT silently overwrite!
            conflict = SyncConflict(
                conflict_id=str(uuid.uuid4()),
                sync_id=item.sync_id,
                entity_type="CASES",
                entity_id=case.id,
                case_id=case.id,
                local_payload=item.payload_snapshot,
                remote_payload={
                    "case_number": case.case_number,
                    "current_state": case.current_state,
                    "status": case.status,
                    "acuity_tier": case.acuity_tier,
                    "state_version": case.state_version,
                    "presenting_complaint": case.presenting_complaint,
                },
                resolution_status="PENDING_HUMAN_REVIEW",
                created_at=utc_now(),
            )
            db.add(conflict)

            journal = SyncJournal(
                sync_id=item.sync_id,
                node_id=node_id,
                entity_type="CASES",
                entity_id=case.id,
                case_id=case.id,
                operation="UPDATE",
                local_version=item.local_version,
                remote_version=case.state_version,
                sync_status="CONFLICT",
                payload_snapshot=item.payload_snapshot,
                conflict_strategy=item.conflict_strategy or "MANUAL_GATE",
                created_at=item.created_at or utc_now(),
                synced_at=None,
            )
            db.add(journal)

            return SyncItemResult(
                sync_id=item.sync_id,
                entity_type="CASES",
                entity_id=case.id,
                case_id=case.id,
                status="CONFLICT",
                remote_version=case.state_version,
                conflict_id=conflict.conflict_id,
                message="Concurrent case modification detected. Frozen in sync_conflicts for human clinician review.",
            )


async def _handle_vitals_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Enforces Inv SYNC-2: Vitals are strictly APPEND_ONLY; never overwritten."""
    payload = item.payload_snapshot
    target_case_id = item.case_id or payload.get("case_id")

    if target_case_id:
        c_res = await db.execute(select(Case).where(Case.id == target_case_id))
        target_case = c_res.scalars().first()
        if target_case:
            if actor.role == ROLE_PATIENT:
                if not actor.patient_id or target_case.patient_id != actor.patient_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="VITALS",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Patient cannot access another patient's case.",
                    )
            elif actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
                if actor.facility_id and target_case.facility_id and actor.facility_id != target_case.facility_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="VITALS",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Cross-facility synchronization prohibited.",
                    )

    vital = Vital(
        id=item.entity_id or str(uuid.uuid4()),
        case_id=target_case_id,
        heart_rate=payload.get("heart_rate"),
        systolic_bp=payload.get("systolic_bp"),
        diastolic_bp=payload.get("diastolic_bp"),
        spo2_percent=payload.get("spo2") or payload.get("spo2_percent"),
        respiratory_rate=payload.get("respiratory_rate"),
        temperature_celsius=payload.get("temperature") or payload.get("temperature_celsius"),
        avpu_score=payload.get("avpu_score", "ALERT"),
        supplemental_o2=payload.get("supplemental_o2", False),
        source="OFFLINE_EDGE_SYNC",
        provenance_metadata={"offline_captured": True, "sync_id": item.sync_id, "node_id": node_id},
        created_at=item.created_at or utc_now(),
    )
    db.add(vital)

    # Record journal as SYNCED (Inv SYNC-1)
    journal = SyncJournal(
        sync_id=item.sync_id,
        node_id=node_id,
        entity_type="VITALS",
        entity_id=vital.id,
        case_id=target_case_id,
        operation="INSERT",
        local_version=item.local_version,
        remote_version=1,
        sync_status="SYNCED",
        payload_snapshot=payload,
        conflict_strategy="APPEND_ONLY",
        created_at=item.created_at or utc_now(),
        synced_at=utc_now(),
    )
    db.add(journal)

    return SyncItemResult(
        sync_id=item.sync_id,
        entity_type="VITALS",
        entity_id=vital.id,
        case_id=target_case_id,
        status="SYNCED",
        remote_version=1,
        message="Vitals appended safely (STRAT_APPEND).",
    )


async def _handle_evidence_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Enforces Inv SYNC-2: Evidence records are strictly APPEND_ONLY."""
    payload = item.payload_snapshot
    target_case_id = item.case_id or payload.get("case_id")

    if target_case_id:
        c_res = await db.execute(select(Case).where(Case.id == target_case_id))
        target_case = c_res.scalars().first()
        if target_case:
            if actor.role == ROLE_PATIENT:
                if not actor.patient_id or target_case.patient_id != actor.patient_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="EVIDENCE",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Patient cannot access another patient's case.",
                    )
            elif actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
                if actor.facility_id and target_case.facility_id and actor.facility_id != target_case.facility_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="EVIDENCE",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Cross-facility synchronization prohibited.",
                    )

    ev = EvidenceRecord(
        id=item.entity_id or str(uuid.uuid4()),
        case_id=target_case_id,
        provenance_type=payload.get("provenance_type", "OFFLINE_RECORD"),
        source_filename=payload.get("source_filename"),
        extracted_payload=payload.get("extracted_payload", {}),
        confidence_score=payload.get("confidence_score", 1.0),
        verification_status="UNVERIFIED",
        created_at=item.created_at or utc_now(),
    )
    db.add(ev)

    journal = SyncJournal(
        sync_id=item.sync_id,
        node_id=node_id,
        entity_type="EVIDENCE",
        entity_id=ev.id,
        case_id=target_case_id,
        operation="INSERT",
        local_version=item.local_version,
        remote_version=1,
        sync_status="SYNCED",
        payload_snapshot=payload,
        conflict_strategy="APPEND_ONLY",
        created_at=item.created_at or utc_now(),
        synced_at=utc_now(),
    )
    db.add(journal)

    return SyncItemResult(
        sync_id=item.sync_id,
        entity_type="EVIDENCE",
        entity_id=ev.id,
        case_id=target_case_id,
        status="SYNCED",
        remote_version=1,
        message="Evidence appended safely (STRAT_APPEND).",
    )


async def _handle_timeline_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Enforces Inv SYNC-2: Timeline milestones are strictly APPEND_ONLY."""
    payload = item.payload_snapshot
    target_case_id = item.case_id or payload.get("case_id")

    event = TimelineEvent(
        id=item.entity_id or str(uuid.uuid4()),
        case_id=target_case_id,
        event_type=payload.get("event_type", "OFFLINE_EVENT"),
        event_title=payload.get("event_title", "Offline Event Recorded"),
        event_content=payload.get("event_content", ""),
        event_timestamp=item.created_at or utc_now(),
        actor_id=actor.actor_id,
        actor_role=actor.role,
        provenance_metadata={"offline_captured": True, "sync_id": item.sync_id, "node_id": node_id},
        created_at=item.created_at or utc_now(),
    )
    db.add(event)

    journal = SyncJournal(
        sync_id=item.sync_id,
        node_id=node_id,
        entity_type="TIMELINE_EVENTS",
        entity_id=event.id,
        case_id=target_case_id,
        operation="INSERT",
        local_version=item.local_version,
        remote_version=1,
        sync_status="SYNCED",
        payload_snapshot=payload,
        conflict_strategy="APPEND_ONLY",
        created_at=item.created_at or utc_now(),
        synced_at=utc_now(),
    )
    db.add(journal)

    return SyncItemResult(
        sync_id=item.sync_id,
        entity_type="TIMELINE_EVENTS",
        entity_id=event.id,
        case_id=target_case_id,
        status="SYNCED",
        remote_version=1,
        message="Timeline milestone appended safely (STRAT_APPEND).",
    )


async def _handle_decision_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Enforces STRAT_CLINICIAN / MANUAL_GATE for clinician decisions."""
    payload = item.payload_snapshot
    target_case_id = item.case_id or payload.get("case_id")

    # Prohibited autonomous clinical action check
    action_type = str(payload.get("action_type", "")).upper()
    decision_type = str(payload.get("decision_type", "")).upper()
    if action_type in PROHIBITED_CLINICAL_ACTIONS or decision_type in PROHIBITED_CLINICAL_ACTIONS:
        return SyncItemResult(
            sync_id=item.sync_id,
            entity_type="CLINICIAN_DECISIONS",
            entity_id=item.entity_id or "",
            case_id=target_case_id,
            status="FAILED",
            remote_version=0,
            message="Prohibited autonomous clinical action rejected server-side.",
        )

    # Scoping check on target case
    if target_case_id:
        c_res = await db.execute(select(Case).where(Case.id == target_case_id))
        target_case = c_res.scalars().first()
        if target_case:
            if actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
                if actor.facility_id and target_case.facility_id and actor.facility_id != target_case.facility_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="CLINICIAN_DECISIONS",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Cross-facility synchronization prohibited.",
                    )

    # Check if case exists and already has clinician decisions
    existing_dec_res = await db.execute(
        select(ClinicianDecision).where(ClinicianDecision.case_id == target_case_id)
    )
    existing_dec = existing_dec_res.scalars().all()

    # If clinician decisions exist and local action conflicts, gate for review
    if existing_dec and item.conflict_strategy == "MANUAL_GATE":
        conflict = SyncConflict(
            conflict_id=str(uuid.uuid4()),
            sync_id=item.sync_id,
            entity_type="CLINICIAN_DECISIONS",
            entity_id=item.entity_id or str(uuid.uuid4()),
            case_id=target_case_id,
            local_payload=payload,
            remote_payload={
                "decisions_count": len(existing_dec),
                "last_decision_type": existing_dec[-1].decision_type if existing_dec else None,
            },
            resolution_status="PENDING_HUMAN_REVIEW",
            created_at=utc_now(),
        )
        db.add(conflict)

        journal = SyncJournal(
            sync_id=item.sync_id,
            node_id=node_id,
            entity_type="CLINICIAN_DECISIONS",
            entity_id=item.entity_id,
            case_id=target_case_id,
            operation="INSERT",
            local_version=item.local_version,
            remote_version=len(existing_dec),
            sync_status="CONFLICT",
            payload_snapshot=payload,
            conflict_strategy="MANUAL_GATE",
            created_at=item.created_at or utc_now(),
            synced_at=None,
        )
        db.add(journal)

        return SyncItemResult(
            sync_id=item.sync_id,
            entity_type="CLINICIAN_DECISIONS",
            entity_id=item.entity_id,
            case_id=target_case_id,
            status="CONFLICT",
            remote_version=len(existing_dec),
            conflict_id=conflict.conflict_id,
            message="Conflicting clinical decision detected. Gated in sync_conflicts for human clinician review.",
        )

    # Clinician wins or initial decision
    new_dec = ClinicianDecision(
        id=item.entity_id or str(uuid.uuid4()),
        case_id=target_case_id,
        clinician_id=actor.actor_id if actor.role in [ROLE_CLINICIAN, ROLE_DOCTOR] else None,
        action_type=payload.get("action_type", "OFFLINE_DECISION"),
        decision_type=payload.get("decision_type", "ACCEPT"),
        clinical_rationale=payload.get("clinical_rationale"),
        notes=payload.get("notes"),
        timestamp=item.created_at or utc_now(),
    )
    db.add(new_dec)

    journal = SyncJournal(
        sync_id=item.sync_id,
        node_id=node_id,
        entity_type="CLINICIAN_DECISIONS",
        entity_id=new_dec.id,
        case_id=target_case_id,
        operation="INSERT",
        local_version=item.local_version,
        remote_version=1,
        sync_status="SYNCED",
        payload_snapshot=payload,
        conflict_strategy=item.conflict_strategy or "CLINICIAN_WINS",
        created_at=item.created_at or utc_now(),
        synced_at=utc_now(),
    )
    db.add(journal)

    return SyncItemResult(
        sync_id=item.sync_id,
        entity_type="CLINICIAN_DECISIONS",
        entity_id=new_dec.id,
        case_id=target_case_id,
        status="SYNCED",
        remote_version=1,
        message="Clinician decision synchronized successfully.",
    )


async def _handle_outcome_sync(
    item: SyncJournalItemIn,
    node_id: str,
    actor: ActorContext,
    db: AsyncSession,
) -> SyncItemResult:
    """Handles sync for case outcome records."""
    payload = item.payload_snapshot
    target_case_id = item.case_id or payload.get("case_id")

    if target_case_id:
        c_res = await db.execute(select(Case).where(Case.id == target_case_id))
        target_case = c_res.scalars().first()
        if target_case:
            if actor.role not in [ROLE_SYSTEM_ADMIN, ROLE_AUDITOR]:
                if actor.facility_id and target_case.facility_id and actor.facility_id != target_case.facility_id:
                    return SyncItemResult(
                        sync_id=item.sync_id,
                        entity_type="CASE_OUTCOMES",
                        entity_id=item.entity_id or "",
                        case_id=target_case_id,
                        status="FAILED",
                        remote_version=0,
                        message="Authorization error: Cross-facility synchronization prohibited.",
                    )

    res = await db.execute(
        select(CaseOutcome).where(CaseOutcome.case_id == target_case_id)
    )
    existing_outcome = res.scalars().first()

    if existing_outcome:
        # Check version conflict
        if existing_outcome.version > item.local_version:
            conflict = SyncConflict(
                conflict_id=str(uuid.uuid4()),
                sync_id=item.sync_id,
                entity_type="CASE_OUTCOMES",
                entity_id=existing_outcome.id,
                case_id=target_case_id,
                local_payload=payload,
                remote_payload={
                    "disposition": existing_outcome.disposition,
                    "final_condition": existing_outcome.final_condition,
                    "version": existing_outcome.version,
                },
                resolution_status="PENDING_HUMAN_REVIEW",
                created_at=utc_now(),
            )
            db.add(conflict)

            journal = SyncJournal(
                sync_id=item.sync_id,
                node_id=node_id,
                entity_type="CASE_OUTCOMES",
                entity_id=existing_outcome.id,
                case_id=target_case_id,
                operation="UPDATE",
                local_version=item.local_version,
                remote_version=existing_outcome.version,
                sync_status="CONFLICT",
                payload_snapshot=payload,
                conflict_strategy="MANUAL_GATE",
                created_at=item.created_at or utc_now(),
                synced_at=None,
            )
            db.add(journal)

            return SyncItemResult(
                sync_id=item.sync_id,
                entity_type="CASE_OUTCOMES",
                entity_id=existing_outcome.id,
                case_id=target_case_id,
                status="CONFLICT",
                remote_version=existing_outcome.version,
                conflict_id=conflict.conflict_id,
                message="Case outcome conflict detected. Gated in sync_conflicts.",
            )

        # Update outcome
        existing_outcome.disposition = payload.get("disposition", existing_outcome.disposition)
        existing_outcome.final_condition = payload.get("final_condition", existing_outcome.final_condition)
        existing_outcome.version += 1

        journal = SyncJournal(
            sync_id=item.sync_id,
            node_id=node_id,
            entity_type="CASE_OUTCOMES",
            entity_id=existing_outcome.id,
            case_id=target_case_id,
            operation="UPDATE",
            local_version=item.local_version,
            remote_version=existing_outcome.version,
            sync_status="SYNCED",
            payload_snapshot=payload,
            conflict_strategy="APPEND_ONLY",
            created_at=item.created_at or utc_now(),
            synced_at=utc_now(),
        )
        db.add(journal)

        return SyncItemResult(
            sync_id=item.sync_id,
            entity_type="CASE_OUTCOMES",
            entity_id=existing_outcome.id,
            case_id=target_case_id,
            status="SYNCED",
            remote_version=existing_outcome.version,
            message="Case outcome updated successfully.",
        )
    else:
        new_outcome = CaseOutcome(
            id=item.entity_id or str(uuid.uuid4()),
            case_id=target_case_id,
            disposition=payload.get("disposition", "UNKNOWN"),
            final_condition=payload.get("final_condition", "STABLE"),
            actual_action=payload.get("actual_action", "UNKNOWN"),
            recommendation=payload.get("recommendation"),
            professional_decision=payload.get("professional_decision"),
            outcome_status=payload.get("outcome_status", "UNKNOWN"),
            recorded_by=actor.actor_id,
            actor_role=actor.role,
            version=1,
            notes=payload.get("notes"),
            recorded_at=item.created_at or utc_now(),
        )
        db.add(new_outcome)

        journal = SyncJournal(
            sync_id=item.sync_id,
            node_id=node_id,
            entity_type="CASE_OUTCOMES",
            entity_id=new_outcome.id,
            case_id=target_case_id,
            operation="INSERT",
            local_version=1,
            remote_version=1,
            sync_status="SYNCED",
            payload_snapshot=payload,
            conflict_strategy="APPEND_ONLY",
            created_at=item.created_at or utc_now(),
            synced_at=utc_now(),
        )
        db.add(journal)

        return SyncItemResult(
            sync_id=item.sync_id,
            entity_type="CASE_OUTCOMES",
            entity_id=new_outcome.id,
            case_id=target_case_id,
            status="SYNCED",
            remote_version=1,
            message="Case outcome created successfully.",
        )
