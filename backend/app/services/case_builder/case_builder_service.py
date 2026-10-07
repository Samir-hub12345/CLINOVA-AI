"""Canonical Patient Case Intelligence Builder Service for Clinova AI.

Orchestrates multi-source extraction, clinical normalization, timeline construction,
multimodal fusion, delta summary computation, and immutable snapshot versioning.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence
from app.models.canonical_case import (
    CaseBuildRun,
    CaseSnapshot,
    CanonicalFact,
    TimelineEvent,
    BuildRunStatus,
)
from app.services.case_builder.extraction_engine import StructuredExtractionEngine, CandidateFact
from app.services.case_builder.normalization_engine import ClinicalNormalizationEngine
from app.services.case_builder.timeline_engine import TimelineEngine, CandidateTimelineEvent
from app.services.case_builder.multimodal_fusion import MultimodalFusionEngine

logger = logging.getLogger("clinova.case_builder")


class CaseBuilderService:
    """Core service for compiling raw evidence into versioned Canonical Patient Case Snapshots."""

    BUILD_LOGIC_VERSION = "3.0.0"

    def __init__(self):
        self.extractor = StructuredExtractionEngine()
        self.normalizer = ClinicalNormalizationEngine()
        self.timeline_engine = TimelineEngine()
        self.fusion_engine = MultimodalFusionEngine()

    async def build_canonical_case(
        self,
        case_id: str,
        db: AsyncSession,
        trigger_type: str = "manual_rebuild",
        force_rebuild: bool = False,
        include_inactive_evidence: bool = False,
    ) -> Tuple[CaseSnapshot, CaseBuildRun]:
        """Builds a new immutable canonical case snapshot from all available case evidence.
        
        Guarantees Last-Known-Good rollback safety if compilation encounters an error.
        """
        start_time = time.time()
        now = datetime.now(timezone.utc)

        # 1. Fetch case
        case_res = await db.execute(select(TriageCase).where(TriageCase.id == case_id))
        case = case_res.scalar_one_or_none()
        if not case:
            raise ValueError(f"Triage case with ID '{case_id}' not found.")

        # 2. Fetch evidence
        ev_query = select(CaseEvidence).where(CaseEvidence.case_id == case_id)
        if not include_inactive_evidence:
            ev_query = ev_query.where(CaseEvidence.is_active == True)
        ev_query = ev_query.order_by(CaseEvidence.created_at.asc())
        ev_res = await db.execute(ev_query)
        evidence_items = list(ev_res.scalars().all())

        # 3. Determine target case version and fetch previous snapshot
        prev_snap_res = await db.execute(
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id, CaseSnapshot.is_current == True)
            .options(selectinload(CaseSnapshot.facts))
        )
        previous_snapshot = prev_snap_res.scalar_one_or_none()

        if previous_snapshot:
            target_version = previous_snapshot.case_version + 1
        else:
            target_version = max(case.case_version, 1)

        build_run_id = str(uuid.uuid4())
        build_run = CaseBuildRun(
            id=build_run_id,
            case_id=case_id,
            status=BuildRunStatus.BUILDING.value,
            trigger_type=trigger_type,
            input_evidence_count=len(evidence_items),
            facts_extracted_count=0,
            facts_rejected_count=0,
            target_case_version=target_version,
            build_logic_version=self.BUILD_LOGIC_VERSION,
            provider_name="clinova_rule_builder",
            model_name="deterministic_v3",
            started_at=now,
        )
        db.add(build_run)
        await db.flush()

        try:
            # 4. Extract facts from evidence
            raw_facts: List[CandidateFact] = []
            total_rejected = 0
            for ev in evidence_items:
                ev_facts, rejected = self.extractor.extract_from_evidence(ev)
                raw_facts.extend(ev_facts)
                total_rejected += rejected

            build_run.facts_rejected_count = total_rejected

            # Also check if raw_symptoms or normalized_symptoms on the case can supply facts if evidence list is empty
            if not evidence_items and (case.normalized_symptoms or case.raw_symptoms):
                # Create a synthetic evidence item for baseline case symptoms
                synth_ev = CaseEvidence(
                    id=str(uuid.uuid4()),
                    case_id=case.id,
                    canonical_field="reported_symptoms",
                    raw_value=case.raw_symptoms or case.normalized_symptoms or "",
                    normalized_value=case.normalized_symptoms,
                    source_type="PATIENT_REPORTED",
                )
                ev_facts, rejected = self.extractor.extract_from_evidence(synth_ev)
                raw_facts.extend(ev_facts)

            # 5. Normalize clinical concepts & units
            normalized_facts = self.normalizer.normalize_all(raw_facts)

            # 6. Multimodal fusion: multi-source linkage & conflict preservation
            fused_facts, conflicts = self.fusion_engine.fuse_and_link_facts(normalized_facts)
            build_run.facts_extracted_count = len(fused_facts)

            # 7. Compute specialty signals
            specialty_signals = self.fusion_engine.compute_specialty_signals(fused_facts)

            # 8. Build ordered timeline events
            timeline_events = self.timeline_engine.extract_timeline_events(evidence_items)

            # 9. Compute delta summary vs previous snapshot
            delta_summary: Dict[str, Any] = {
                "previous_version": previous_snapshot.case_version if previous_snapshot else None,
                "new_version": target_version,
                "facts_count": len(fused_facts),
                "conflicts_count": len(conflicts),
                "timeline_events_count": len(timeline_events),
            }
            if previous_snapshot and previous_snapshot.facts:
                prev_concepts = {f.concept for f in previous_snapshot.facts}
                new_concepts = {f.concept for f in fused_facts}
                delta_summary["added_concepts"] = list(new_concepts - prev_concepts)
                delta_summary["removed_concepts"] = list(prev_concepts - new_concepts)
            else:
                delta_summary["initial_build"] = True

            # 10. Assemble structured Canonical Case data dictionary
            case_data: Dict[str, Any] = {
                "case_id": case.id,
                "synthetic_case_id": case.synthetic_case_id,
                "case_version": target_version,
                "compiled_at": now.isoformat(),
                "patient_id": case.patient_id,
                "facility_type": case.facility_type,
                "visit_type": case.visit_type,
                "language": case.language,
                "demographics": {
                    "age": case.approximate_age,
                    "gender": case.gender,
                },
                "summary": {
                    "symptoms": [f.normalized_value or f.value for f in fused_facts if f.category == "symptom"],
                    "vitals": [f.normalized_value or f.value for f in fused_facts if f.category == "vital"],
                    "labs": [f.normalized_value or f.value for f in fused_facts if f.category == "lab_value"],
                    "conditions": [f.concept for f in fused_facts if f.category == "documented_condition"],
                    "medications": [f.value for f in fused_facts if f.category == "medication"],
                    "allergies": [f.value for f in fused_facts if f.category == "allergy"],
                    "family_history": [f.value for f in fused_facts if f.category == "family_history"],
                },
                "conflicts": conflicts,
                "specialty_signals": [s.model_dump() for s in specialty_signals],
                "timeline": [
                    {
                        "order": ev.order_index,
                        "relative_time": ev.relative_time,
                        "description": ev.description,
                        "temporal_status": ev.temporal_status,
                    }
                    for ev in timeline_events
                ],
            }

            # 11. Deactivate prior snapshots for this case
            if previous_snapshot:
                await db.execute(
                    update(CaseSnapshot)
                    .where(CaseSnapshot.case_id == case_id)
                    .values(is_current=False)
                )

            # 12. Create new immutable CaseSnapshot
            snapshot_id = str(uuid.uuid4())
            new_snapshot = CaseSnapshot(
                id=snapshot_id,
                case_id=case_id,
                build_run_id=build_run_id,
                case_version=target_version,
                schema_version=1,
                build_version=self.BUILD_LOGIC_VERSION,
                provider_name="clinova_rule_builder",
                model_name="deterministic_v3",
                case_data=case_data,
                delta_summary=delta_summary,
                is_current=True,
                created_at=now,
            )
            db.add(new_snapshot)
            await db.flush()

            # 13. Persist CanonicalFact atoms attached to snapshot
            fact_models: List[CanonicalFact] = []
            for f in fused_facts:
                fact_m = CanonicalFact(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    snapshot_id=snapshot_id,
                    category=f.category,
                    concept=f.concept,
                    value=f.value,
                    normalized_value=f.normalized_value,
                    unit=f.unit,
                    polarity=f.polarity,
                    certainty=f.certainty,
                    attribution=f.attribution,
                    temporal_status=f.temporal_status,
                    duration=f.duration,
                    onset_approximate=f.onset_approximate,
                    source_evidence_id=f.source_evidence_id,
                    source_span=f.source_span,
                    supporting_evidence_ids=f.supporting_evidence_ids,
                    has_conflict=f.has_conflict,
                    conflicting_value=f.conflicting_value,
                    conflicting_source_id=f.conflicting_source_id,
                    verification_state="unverified",
                    confidence_score=1.0,
                    is_active=True,
                    created_at=now,
                )
                db.add(fact_m)
                fact_models.append(fact_m)

            # 14. Persist TimelineEvent records attached to snapshot
            timeline_models: List[TimelineEvent] = []
            for ev in timeline_events:
                t_m = TimelineEvent(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    snapshot_id=snapshot_id,
                    event_type=ev.event_type,
                    description=ev.description,
                    relative_time=ev.relative_time,
                    approximate_date=ev.approximate_date,
                    temporal_status=ev.temporal_status,
                    source_evidence_id=ev.source_evidence_id,
                    attribution=ev.attribution,
                    certainty=ev.certainty,
                    order_index=ev.order_index,
                    created_at=now,
                )
                db.add(t_m)
                timeline_models.append(t_m)

            # 15. Update case version on TriageCase
            case.case_version = target_version
            case.updated_at = now

            # 16. Complete build run
            latency_ms = int((time.time() - start_time) * 1000)
            build_run.status = BuildRunStatus.COMPLETED.value
            build_run.completed_at = datetime.now(timezone.utc)
            build_run.latency_ms = latency_ms

            await db.commit()

            # Eagerly reload snapshot with all relationships to avoid MissingGreenlet
            snap_res = await db.execute(
                select(CaseSnapshot)
                .where(CaseSnapshot.id == snapshot_id)
                .options(
                    selectinload(CaseSnapshot.facts),
                    selectinload(CaseSnapshot.timeline_events),
                )
            )
            final_snapshot = snap_res.scalar_one()

            # Also ensure build_run has latency and completed_at
            build_run.status = BuildRunStatus.COMPLETED.value
            build_run.latency_ms = latency_ms
            build_run.completed_at = datetime.now(timezone.utc)

            return final_snapshot, build_run

        except Exception as e:
            # Last-Known-Good Rollback Safety:
            # Previous snapshot remains is_current=True!
            await db.rollback()
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Canonical case build run failed for case {case_id}: {str(e)}", exc_info=True)

            # Record failed build run with fresh UUID to avoid identity map collisions
            try:
                failed_run = CaseBuildRun(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    status=BuildRunStatus.FAILED.value,
                    trigger_type=trigger_type,
                    input_evidence_count=len(evidence_items),
                    target_case_version=target_version,
                    build_logic_version=self.BUILD_LOGIC_VERSION,
                    provider_name="clinova_rule_builder",
                    error_code="BUILD_EXECUTION_FAILURE",
                    error_message=str(e),
                    started_at=now,
                    completed_at=datetime.now(timezone.utc),
                    latency_ms=latency_ms,
                )
                db.add(failed_run)
                await db.commit()
            except Exception:
                pass
            raise

    async def get_current_snapshot(self, case_id: str, db: AsyncSession) -> Optional[CaseSnapshot]:
        res = await db.execute(
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id, CaseSnapshot.is_current == True)
            .options(
                selectinload(CaseSnapshot.facts),
                selectinload(CaseSnapshot.timeline_events),
            )
        )
        return res.scalar_one_or_none()

    async def list_snapshots(self, case_id: str, db: AsyncSession) -> List[CaseSnapshot]:
        res = await db.execute(
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id)
            .order_by(CaseSnapshot.case_version.desc())
            .options(
                selectinload(CaseSnapshot.facts),
                selectinload(CaseSnapshot.timeline_events),
            )
        )
        return list(res.scalars().all())

    async def get_snapshot_by_version(
        self, case_id: str, version: int, db: AsyncSession
    ) -> Optional[CaseSnapshot]:
        res = await db.execute(
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case_id, CaseSnapshot.case_version == version)
            .options(
                selectinload(CaseSnapshot.facts),
                selectinload(CaseSnapshot.timeline_events),
            )
        )
        return res.scalar_one_or_none()

    async def list_build_runs(self, case_id: str, db: AsyncSession) -> List[CaseBuildRun]:
        res = await db.execute(
            select(CaseBuildRun)
            .where(CaseBuildRun.case_id == case_id)
            .order_by(CaseBuildRun.started_at.desc())
        )
        return list(res.scalars().all())
