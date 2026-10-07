"""Case verification orchestrator service for Clinova AI (Phase 4).

Coordinates modular verification rules, idempotency, version tracking, database persistence,
and audit logging.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import TriageCase
from app.models.patient import Patient
from app.models.case_evidence import CaseEvidence
from app.models.canonical_case import CaseSnapshot, CanonicalFact, TimelineEvent
from app.models.verification import (
    VerificationRun,
    VerificationFinding,
    VerificationConflict,
    VerificationRunStatus,
    ReviewReadinessLevel,
    FindingSeverity,
    FindingStatus,
)
from app.models.user import User
from app.services.verification.context import VerificationContext
from app.services.verification.base import FindingCandidate, ConflictCandidate
from app.services.verification.rules import (
    StructuralIntegrityRule,
    CompletenessRule,
    EvidenceStatusRule,
    CrossSourceConflictRule,
    TemporalConsistencyRule,
    ProvenanceRule,
    UncertaintyRule,
    ReviewReadinessCalculator,
)
from app.services.audit import AuditService

logger = logging.getLogger("clinova.verification")


class CaseVerificationService:
    """Core service orchestrating Phase 4 Clinical Information Verification."""

    ENGINE_VERSION = "4.0.0"
    RULESET_VERSION = "4.0.0"

    def __init__(self):
        self.rules = [
            StructuralIntegrityRule(),
            CompletenessRule(),
            EvidenceStatusRule(),
            CrossSourceConflictRule(),
            TemporalConsistencyRule(),
            ProvenanceRule(),
            UncertaintyRule(),
        ]

    async def verify_case(
        self,
        case_id: str,
        db: AsyncSession,
        actor: Optional[User] = None,
        force_reverify: bool = False,
        include_ai_checks: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VerificationRun:
        """Executes the complete verification pipeline for a canonical patient case."""
        start_time = time.time()
        now = datetime.now(timezone.utc)

        # 1. Fetch Case with patient relation
        stmt = (
            select(TriageCase)
            .where(TriageCase.id == case_id)
            .options(selectinload(TriageCase.patient))
        )
        case_res = await db.execute(stmt)
        case = case_res.scalar_one_or_none()
        if not case:
            raise ValueError(f"Triage case with ID '{case_id}' not found.")
        case_patient_id = case.patient_id
        case_encounter_id = case.encounter_id
        case_synthetic_id = case.synthetic_case_id

        # 2. Fetch current snapshot
        snap_stmt = (
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id, CaseSnapshot.is_current == True)
            .options(
                selectinload(CaseSnapshot.facts),
                selectinload(CaseSnapshot.timeline_events),
            )
        )
        snap_res = await db.execute(snap_stmt)
        snapshot = snap_res.scalar_one_or_none()

        target_version = snapshot.case_version if snapshot else case.case_version

        # 3. Idempotency Check:
        # If identical case version already has a completed verification run and not force_reverify
        if not force_reverify:
            existing_run_stmt = (
                select(VerificationRun)
                .where(
                    VerificationRun.case_id == case_id,
                    VerificationRun.case_version == target_version,
                    VerificationRun.status == VerificationRunStatus.COMPLETED.value,
                )
                .options(
                    selectinload(VerificationRun.findings),
                    selectinload(VerificationRun.conflicts),
                )
                .order_by(VerificationRun.completed_at.desc())
            )
            existing_res = await db.execute(existing_run_stmt)
            existing_run = existing_res.scalars().first()
            if existing_run:
                logger.info(
                    f"Idempotent verification hit: returning cached run {existing_run.id} for case {case_id} v{target_version}"
                )
                return existing_run

        # 4. Fetch evidence items
        ev_stmt = (
            select(CaseEvidence)
            .where(CaseEvidence.case_id == case_id, CaseEvidence.is_active == True)
            .order_by(CaseEvidence.created_at.asc())
        )
        ev_res = await db.execute(ev_stmt)
        evidence_items = list(ev_res.scalars().all())

        # 5. Build VerificationContext
        facts = list(snapshot.facts) if snapshot and snapshot.facts else []
        timeline = list(snapshot.timeline_events) if snapshot and snapshot.timeline_events else []

        context = VerificationContext(
            case=case,
            snapshot=snapshot,
            case_version=target_version,
            facts=facts,
            evidence_items=evidence_items,
            timeline_events=timeline,
            metadata={"include_ai_checks": include_ai_checks},
        )

        # 6. Execute rules
        all_findings: List[FindingCandidate] = []
        all_conflicts: List[ConflictCandidate] = []

        try:
            for rule in self.rules:
                r_findings, r_conflicts = await rule.evaluate(context)
                all_findings.extend(r_findings)
                all_conflicts.extend(r_conflicts)

            # 7. Deduplicate findings by (finding_type, category, field_name, title)
            seen_signatures = set()
            unique_findings: List[FindingCandidate] = []
            for f in all_findings:
                sig = (f.finding_type.value, f.category.value, f.field_name or "", f.title)
                if sig not in seen_signatures:
                    seen_signatures.add(sig)
                    unique_findings.append(f)

            # 8. Sort findings by severity: BLOCKING -> HIGH -> MEDIUM -> LOW -> INFO
            severity_order = {
                FindingSeverity.BLOCKING: 0,
                FindingSeverity.HIGH: 1,
                FindingSeverity.MEDIUM: 2,
                FindingSeverity.LOW: 3,
                FindingSeverity.INFO: 4,
            }
            unique_findings.sort(key=lambda x: severity_order.get(x.severity, 5))

            # 9. Calculate Review Readiness
            readiness_level, readiness_score, readiness_reasons, subsystems = (
                ReviewReadinessCalculator.calculate(context, unique_findings, all_conflicts)
            )

            # 10. Counts
            blocking_count = sum(1 for f in unique_findings if f.is_blocking or f.severity == FindingSeverity.BLOCKING)
            high_count = sum(1 for f in unique_findings if f.severity == FindingSeverity.HIGH)
            med_count = sum(1 for f in unique_findings if f.severity == FindingSeverity.MEDIUM)
            low_count = sum(1 for f in unique_findings if f.severity == FindingSeverity.LOW)
            info_count = sum(1 for f in unique_findings if f.severity == FindingSeverity.INFO)
            unresolved_count = sum(1 for f in unique_findings if f.status == FindingStatus.UNRESOLVED)

            # 11. Deactivate older current verification runs for this case
            await db.execute(
                update(VerificationRun)
                .where(VerificationRun.case_id == case_id)
                .values(is_current=False)
            )

            # 12. Create VerificationRun entity
            run_id = str(uuid.uuid4())
            run = VerificationRun(
                id=run_id,
                case_id=case_id,
                patient_id=case.patient_id,
                encounter_id=case.encounter_id,
                case_snapshot_id=snapshot.id if snapshot else None,
                case_version=target_version,
                status=VerificationRunStatus.COMPLETED.value,
                engine_version=self.ENGINE_VERSION,
                ruleset_version=self.RULESET_VERSION,
                review_readiness_status=readiness_level.value,
                review_readiness_score=readiness_score,
                review_readiness_reasons=readiness_reasons,
                findings_count=len(unique_findings),
                blocking_findings_count=blocking_count,
                high_findings_count=high_count,
                medium_findings_count=med_count,
                low_findings_count=low_count,
                info_findings_count=info_count,
                unresolved_findings_count=unresolved_count,
                resolved_findings_count=0,
                structural_integrity_status=subsystems["structural"],
                completeness_status=subsystems["completeness"],
                consistency_status=subsystems["consistency"],
                temporal_status=subsystems["temporal"],
                provenance_status=subsystems["provenance"],
                uncertainty_status=subsystems["uncertainty"],
                is_current=True,
                latency_ms=int((time.time() - start_time) * 1000),
                summary={
                    "case_version": target_version,
                    "evidence_count": len(evidence_items),
                    "facts_count": len(facts),
                    "timeline_events_count": len(timeline),
                    "conflicts_count": len(all_conflicts),
                    "evaluated_at": now.isoformat(),
                },
                started_at=now,
                completed_at=datetime.now(timezone.utc),
            )
            db.add(run)
            await db.flush()

            # 13. Persist VerificationFindings
            for cand in unique_findings:
                vf = VerificationFinding(
                    id=str(uuid.uuid4()),
                    verification_run_id=run_id,
                    case_id=case_id,
                    case_version=target_version,
                    finding_type=cand.finding_type.value,
                    category=cand.category.value,
                    field_name=cand.field_name,
                    severity=cand.severity.value,
                    status=cand.status.value,
                    is_blocking=cand.is_blocking,
                    title=cand.title,
                    description=cand.description,
                    explanation=cand.explanation,
                    expected_information=cand.expected_information,
                    observed_information=cand.observed_information,
                    source_evidence_ids=cand.source_evidence_ids,
                    fact_ids=cand.fact_ids,
                    timeline_event_ids=cand.timeline_event_ids,
                    rule_id=cand.rule_id,
                    rule_version=cand.rule_version,
                    created_at=now,
                )
                db.add(vf)

            # 14. Persist VerificationConflicts
            for cand_c in all_conflicts:
                vc = VerificationConflict(
                    id=str(uuid.uuid4()),
                    verification_run_id=run_id,
                    case_id=case_id,
                    case_version=target_version,
                    conflict_type=cand_c.conflict_type.value,
                    field_name=cand_c.field_name,
                    severity=cand_c.severity.value,
                    source_a_evidence_id=cand_c.source_a_evidence_id,
                    source_a_type=cand_c.source_a_type,
                    source_a_modality=cand_c.source_a_modality,
                    source_a_value=cand_c.source_a_value,
                    source_a_timestamp=cand_c.source_a_timestamp,
                    source_b_evidence_id=cand_c.source_b_evidence_id,
                    source_b_type=cand_c.source_b_type,
                    source_b_modality=cand_c.source_b_modality,
                    source_b_value=cand_c.source_b_value,
                    source_b_timestamp=cand_c.source_b_timestamp,
                    resolution_state=cand_c.resolution_state.value,
                    rule_id=cand_c.rule_id,
                    created_at=now,
                )
                db.add(vc)

            # 15. Update case review_readiness_status
            case.review_readiness_status = readiness_level.value
            case.updated_at = now

            # 16. Audit Log
            await AuditService.log_event(
                db=db,
                action="CASE_VERIFICATION_COMPLETED",
                resource_type="TRIAGE_CASE",
                resource_id=case.synthetic_case_id,
                user=actor,
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"Case verified for version {target_version}. Readiness: {readiness_level.value} (score: {readiness_score:.2f}). Findings: {len(unique_findings)}, Conflicts: {len(all_conflicts)}.",
            )

            await db.commit()

            # Eagerly reload full run with findings and conflicts
            run_reload_stmt = (
                select(VerificationRun)
                .where(VerificationRun.id == run_id)
                .options(
                    selectinload(VerificationRun.findings),
                    selectinload(VerificationRun.conflicts),
                )
            )
            reloaded_run = (await db.execute(run_reload_stmt)).scalar_one()
            return reloaded_run

        except Exception as e:
            await db.rollback()
            logger.error(f"Case verification failed for case {case_id}: {str(e)}", exc_info=True)
            # Record failed run
            try:
                failed_run = VerificationRun(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    patient_id=case_patient_id,
                    encounter_id=case_encounter_id,
                    case_version=target_version,
                    status=VerificationRunStatus.FAILED.value,
                    engine_version=self.ENGINE_VERSION,
                    ruleset_version=self.RULESET_VERSION,
                    review_readiness_status=ReviewReadinessLevel.NOT_READY.value,
                    review_readiness_score=0.0,
                    review_readiness_reasons=[f"Verification failed: {str(e)}"],
                    failure_reason=str(e),
                    is_current=True,
                    started_at=now,
                    completed_at=datetime.now(timezone.utc),
                    latency_ms=int((time.time() - start_time) * 1000),
                )
                db.add(failed_run)
                await db.commit()
                # Eagerly reload failed run to avoid lazy load issues during serialization
                reload_failed = (
                    select(VerificationRun)
                    .where(VerificationRun.id == failed_run.id)
                    .options(
                        selectinload(VerificationRun.findings),
                        selectinload(VerificationRun.conflicts),
                    )
                )
                return (await db.execute(reload_failed)).scalar_one()
            except Exception:
                raise e

    async def get_latest_verification(
        self, case_id: str, db: AsyncSession
    ) -> Optional[VerificationRun]:
        """Retrieves the latest current verification run and computes whether it is stale."""
        stmt = (
            select(VerificationRun)
            .where(VerificationRun.case_id == case_id, VerificationRun.is_current == True)
            .options(
                selectinload(VerificationRun.findings),
                selectinload(VerificationRun.conflicts),
            )
            .order_by(VerificationRun.started_at.desc())
        )
        res = await db.execute(stmt)
        run = res.scalars().first()
        if not run:
            # Check any most recent run
            stmt2 = (
                select(VerificationRun)
                .where(VerificationRun.case_id == case_id)
                .options(
                    selectinload(VerificationRun.findings),
                    selectinload(VerificationRun.conflicts),
                )
                .order_by(VerificationRun.started_at.desc())
            )
            run = (await db.execute(stmt2)).scalars().first()

        if run:
            # Check if stale vs current case_version
            case_res = await db.execute(select(TriageCase.case_version).where(TriageCase.id == case_id))
            curr_v = case_res.scalar_one_or_none()
            if curr_v and curr_v > run.case_version:
                run.is_stale = True
            else:
                run.is_stale = False

        return run

    async def list_verification_runs(
        self, case_id: str, db: AsyncSession
    ) -> List[VerificationRun]:
        """Lists all historical verification runs for a case."""
        stmt = (
            select(VerificationRun)
            .where(VerificationRun.case_id == case_id)
            .options(
                selectinload(VerificationRun.findings),
                selectinload(VerificationRun.conflicts),
            )
            .order_by(VerificationRun.started_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_verification_run(
        self, run_id: str, db: AsyncSession
    ) -> Optional[VerificationRun]:
        """Retrieves a specific verification run by ID."""
        stmt = (
            select(VerificationRun)
            .where(VerificationRun.id == run_id)
            .options(
                selectinload(VerificationRun.findings),
                selectinload(VerificationRun.conflicts),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_findings(
        self,
        case_id: str,
        db: AsyncSession,
        run_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[VerificationFinding]:
        """Lists verification findings with optional filtering."""
        query = select(VerificationFinding).where(VerificationFinding.case_id == case_id)
        if run_id:
            query = query.where(VerificationFinding.verification_run_id == run_id)
        if severity:
            query = query.where(VerificationFinding.severity == severity.upper())
        if status:
            query = query.where(VerificationFinding.status == status.upper())
        if category:
            query = query.where(VerificationFinding.category == category.upper())

        query = query.order_by(VerificationFinding.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    async def resolve_finding(
        self,
        case_id: str,
        finding_id: str,
        resolution_state: str,
        resolution_notes: str,
        actor: User,
        db: AsyncSession,
        ip_address: Optional[str] = None,
    ) -> VerificationFinding:
        """Resolves an open finding with human clinician rationale without erasing history."""
        stmt = select(VerificationFinding).where(
            VerificationFinding.id == finding_id,
            VerificationFinding.case_id == case_id,
        )
        finding = (await db.execute(stmt)).scalar_one_or_none()
        if not finding:
            raise ValueError(f"Finding with ID '{finding_id}' not found for case '{case_id}'.")

        now = datetime.now(timezone.utc)
        finding.status = resolution_state
        finding.resolved_by_user_id = actor.id
        finding.resolved_at = now
        finding.resolution_notes = resolution_notes

        # Also update parent verification run counts
        run_stmt = select(VerificationRun).where(VerificationRun.id == finding.verification_run_id)
        run = (await db.execute(run_stmt)).scalar_one_or_none()
        if run:
            run.resolved_findings_count += 1
            run.unresolved_findings_count = max(0, run.unresolved_findings_count - 1)

        await AuditService.log_event(
            db=db,
            action="VERIFICATION_FINDING_RESOLVED",
            resource_type="VERIFICATION_FINDING",
            resource_id=finding.id,
            user=actor,
            ip_address=ip_address,
            details=f"Finding '{finding.title}' resolved by {actor.full_name} ({actor.role.value}). State: {resolution_state}. Rationale: {resolution_notes}",
        )

        await db.commit()
        await db.refresh(finding)
        return finding
