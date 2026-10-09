"""CLINOVA AI — Clinical Review Domain Logic & Synthesis Engine.

Continuous Care Intelligence System.
Phase 17: Human Review + Case State Lifecycle.
Grounded in DOC-03, DOC-06, DOC-07, DOC-08, DOC-14.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.models import (
    Case,
    Evidence,
    Vital,
    TimelineEvent,
    FollowUpQuestion,
    FollowUpAnswer,
    TriageNote,
    ReviewAction,
    AuditEvent,
    ClinicianDecision,
    CaseStateTransition,
    TriageSnapshotRecord,
    AIResultRecord,
    utc_now,
)
from app.domain.triage import (
    compute_deterministic_triage,
    sort_clinical_queue,
    evaluate_vital_freshness,
)


def detect_evidence_conflicts(evidence_items: List[Evidence]) -> List[Dict[str, Any]]:
    """
    Identifies conflicting clinical observations.
    Flags items explicitly marked CONFLICTING as well as contradictory parameter entries.
    """
    conflicts: List[Dict[str, Any]] = []
    
    # 1. Explicitly marked CONFLICTING items
    explicit_conflicts = [
        ev for ev in evidence_items if ev.epistemic_state == "CONFLICTING"
    ]
    for ev in explicit_conflicts:
        conflicts.append({
            "conflict_id": f"conf-{ev.id}",
            "parameter_name": ev.parameter_name,
            "evidence_id": ev.id,
            "source_class": ev.source_class,
            "content_value": ev.content_value,
            "unit": ev.unit,
            "epistemic_state": ev.epistemic_state,
            "captured_timestamp": ev.captured_timestamp.isoformat() if ev.captured_timestamp else None,
            "status": "UNRESOLVED",
            "clinical_risk": f"Epistemic conflict detected on parameter '{ev.parameter_name}'. Requires clinician resolution.",
        })

    # 2. Contradictory values for the same parameter
    param_map: Dict[str, List[Evidence]] = {}
    for ev in evidence_items:
        if ev.epistemic_state not in {"SUPERSEDED", "RESOLVED", "REJECTED"}:
            param_map.setdefault(ev.parameter_name.lower(), []).append(ev)

    for param, items in param_map.items():
        if len(items) > 1:
            values = [str(it.content_value) for it in items]
            if len(set(values)) > 1 and not any(c["parameter_name"].lower() == param for c in conflicts):
                conflicts.append({
                    "conflict_id": f"conf-multi-{param}",
                    "parameter_name": items[0].parameter_name,
                    "evidence_id": items[0].id,
                    "competing_evidence_ids": [it.id for it in items],
                    "competing_values": [
                        {
                            "id": it.id,
                            "source": it.source_class,
                            "value": it.content_value,
                            "epistemic_state": it.epistemic_state,
                        }
                        for it in items
                    ],
                    "status": "UNRESOLVED",
                    "clinical_risk": f"Multiple contradictory values recorded for parameter '{items[0].parameter_name}'.",
                })

    return conflicts


async def build_case_review_context(
    case: Case,
    db: AsyncSession,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Assembles comprehensive clinical review context for the Doctor Workbench.
    Strictly distinguishes SYSTEM-DETERMINED SUPPORT from HUMAN CLINICAL JUDGMENT.
    """
    if now is None:
        now = utc_now()

    # Load fresh case relationships
    ev_stmt = select(Evidence).where(Evidence.case_id == case.id).order_by(Evidence.captured_timestamp)
    evidence_items = (await db.execute(ev_stmt)).scalars().all()

    v_stmt = select(Vital).where(Vital.case_id == case.id).order_by(Vital.recorded_at)
    vitals_items = (await db.execute(v_stmt)).scalars().all()
    latest_vital = vitals_items[-1] if vitals_items else None

    tl_stmt = select(TimelineEvent).where(TimelineEvent.case_id == case.id).order_by(TimelineEvent.event_timestamp)
    timeline_items = (await db.execute(tl_stmt)).scalars().all()

    fq_stmt = (
        select(FollowUpQuestion)
        .options(selectinload(FollowUpQuestion.answers))
        .where(FollowUpQuestion.case_id == case.id)
        .order_by(FollowUpQuestion.created_at)
    )
    follow_up_items = (await db.execute(fq_stmt)).scalars().all()

    tn_stmt = select(TriageNote).where(TriageNote.case_id == case.id).order_by(TriageNote.created_at)
    triage_notes = (await db.execute(tn_stmt)).scalars().all()

    ra_stmt = select(ReviewAction).where(ReviewAction.case_id == case.id).order_by(ReviewAction.created_at)
    review_actions = (await db.execute(ra_stmt)).scalars().all()

    cd_stmt = select(ClinicianDecision).where(ClinicianDecision.case_id == case.id).order_by(ClinicianDecision.timestamp)
    clinician_decisions = (await db.execute(cd_stmt)).scalars().all()

    st_stmt = select(CaseStateTransition).where(CaseStateTransition.case_id == case.id).order_by(CaseStateTransition.created_at)
    state_transitions = (await db.execute(st_stmt)).scalars().all()

    ai_stmt = select(AIResultRecord).where(AIResultRecord.case_id == case.id).order_by(desc(AIResultRecord.created_at))
    ai_results_items = (await db.execute(ai_stmt)).scalars().all()

    # Calculate deterministic support safely
    triage_summary = compute_deterministic_triage(
        case_id=case.id,
        pathway=case.pathway,
        current_state=case.current_state,
        presenting_complaint=case.presenting_complaint,
        latest_vital=latest_vital,
        now=now,
    )

    # Detect epistemic conflicts
    conflicts = detect_evidence_conflicts(evidence_items)

    # Vitals history representation
    vitals_history = []
    for v in vitals_items:
        v_dict = {
            "id": v.id,
            "heart_rate": v.heart_rate,
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "spo2_percent": v.spo2_percent,
            "respiratory_rate": v.respiratory_rate,
            "temperature_celsius": v.temperature_celsius,
            "avpu_score": v.avpu_score,
            "supplemental_o2": v.supplemental_o2,
            "source": v.source,
            "recorded_at": v.recorded_at.isoformat() if v.recorded_at else None,
            "provenance_metadata": v.provenance_metadata or {},
        }
        vitals_history.append(v_dict)

    # Timeline representation
    timeline_list = []
    for tl in timeline_items:
        timeline_list.append({
            "id": tl.id,
            "event_type": tl.event_type,
            "event_title": tl.event_title,
            "event_content": tl.event_content,
            "event_timestamp": tl.event_timestamp.isoformat() if tl.event_timestamp else None,
            "actor_id": tl.actor_id,
            "actor_role": tl.actor_role,
            "evidence_id": tl.evidence_id,
            "is_conflict": tl.is_conflict,
            "provenance_metadata": tl.provenance_metadata or {},
        })

    # Follow-ups representation
    follow_ups_list = []
    for q in follow_up_items:
        answers_list = [
            {
                "id": a.id,
                "answer_text": a.answer_text,
                "answered_by": a.answered_by,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
                "evidence_id": a.evidence_id,
            }
            for a in q.answers
        ]
        follow_ups_list.append({
            "id": q.id,
            "question_text": q.question_text,
            "reason": q.reason,
            "priority": q.priority,
            "status": q.status,
            "created_at": q.created_at.isoformat() if q.created_at else None,
            "answers": answers_list,
        })

    # Evidence items representation
    evidence_list = []
    for ev in evidence_items:
        evidence_list.append({
            "id": ev.id,
            "case_id": ev.case_id,
            "source_class": ev.source_class,
            "epistemic_state": ev.epistemic_state,
            "parameter_name": ev.parameter_name,
            "content_value": ev.content_value,
            "unit": ev.unit,
            "confidence_score": ev.confidence_score,
            "source_timestamp": ev.source_timestamp.isoformat() if ev.source_timestamp else None,
            "captured_timestamp": ev.captured_timestamp.isoformat() if ev.captured_timestamp else None,
            "provenance_metadata": ev.provenance_metadata or {},
            "verification_metadata": ev.verification_metadata or {},
            "transformation_metadata": ev.transformation_metadata or {},
            "is_conflicting": ev.epistemic_state == "CONFLICTING",
        })

    # System-determined support with mandatory disclaimer
    system_support = {
        "is_system_determined": True,
        "is_authoritative_clinical_decision": False,
        "mandate": "DETERMINISTIC_SAFETY_SUPPORT_ONLY",
        "disclaimer": (
            "CLINOVA AI deterministic safety layer calculation. "
            "Non-diagnostic and advisory only. Qualified licensed clinician holds "
            "sole authority and responsibility for all clinical decisions."
        ),
        "acuity_tier": triage_summary.get("acuity_tier", case.acuity_tier),
        "priority_tier": triage_summary.get("priority_tier", "P4_ROUTINE"),
        "risk_score": triage_summary.get("risk_score", case.risk_score),
        "uncertainty_score": triage_summary.get("uncertainty_score", case.uncertainty_score),
        "news2": triage_summary.get("news2", {}),
        "shock_index": triage_summary.get("shock_index", {}),
        "red_flags": triage_summary.get("red_flags", []),
        "has_critical_red_flags": triage_summary.get("has_critical_red_flags", False),
        "priority_reasons": triage_summary.get("priority_reasons", []),
        "missing_critical_vitals": triage_summary.get("missing_critical_vitals", []),
        "vitals_overall_status": triage_summary.get("vitals_overall_status", "MISSING"),
        "ruleset_version": triage_summary.get("ruleset_version", "CLINOVA-TRIAGE-v1.0"),
        "calculated_at": triage_summary.get("calculated_at", now.isoformat()),
    }

    # Case info dict
    case_dict = {
        "id": case.id,
        "case_number": case.case_number,
        "facility_id": case.facility_id,
        "patient_id": case.patient_id,
        "pathway": case.pathway,
        "current_state": case.current_state,
        "status": case.status,
        "acuity_tier": case.acuity_tier,
        "risk_score": case.risk_score,
        "trajectory_slope": case.trajectory_slope,
        "uncertainty_score": case.uncertainty_score,
        "state_version": case.state_version,
        "presenting_complaint": case.presenting_complaint,
        "primary_syndrome": case.primary_syndrome,
        "required_bundle": case.required_bundle,
        "is_closed": case.is_closed,
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "closure_reason": case.closure_reason,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
    }

    # Patient demographic bracket
    patient = None
    try:
        patient = case.patient
    except Exception:
        pass
    if not patient and case.patient_id:
        patient = await db.get(Patient, case.patient_id)

    patient_dict = {
        "id": patient.id if patient else "PT-SYN",
        "synthetic_id": patient.synthetic_id if patient else "SYN-PT",
        "age_bracket": patient.age_bracket if patient else "40-49",
        "biological_sex": patient.biological_sex if patient else "UNKNOWN",
        "is_synthetic": True,
    }

    return {
        "case": case_dict,
        "patient": patient_dict,
        "system_deterministic_support": system_support,
        "evidence": evidence_list,
        "conflicts": conflicts,
        "vitals_history": vitals_history,
        "timeline": timeline_list,
        "follow_ups": follow_ups_list,
        "triage_notes": [
            {
                "id": tn.id,
                "author_id": tn.author_id,
                "author_role": tn.author_role,
                "author_type": tn.author_type,
                "summary": tn.summary,
                "acuity_assessment": tn.acuity_assessment,
                "clinical_concerns": tn.clinical_concerns,
                "suggested_next_steps": tn.suggested_next_steps,
                "is_ai_generated": tn.is_ai_generated,
                "created_at": tn.created_at.isoformat() if tn.created_at else None,
            }
            for tn in triage_notes
        ],
        "prior_review_actions": [
            {
                "id": ra.id,
                "clinician_id": ra.clinician_id,
                "action": ra.action,
                "target_entity_type": ra.target_entity_type,
                "target_entity_id": ra.target_entity_id,
                "original_value": ra.original_value,
                "updated_value": ra.updated_value,
                "reason": ra.reason,
                "notes": ra.notes,
                "created_at": ra.created_at.isoformat() if ra.created_at else None,
            }
            for ra in review_actions
        ],
        "prior_decisions": [
            {
                "id": cd.id,
                "clinician_id": cd.clinician_id,
                "action_type": cd.action_type,
                "decision_type": cd.decision_type,
                "override_reason": cd.override_reason,
                "clinical_impression": getattr(cd, "clinical_impression", None),
                "treatment_plan": getattr(cd, "treatment_plan", None),
                "clinical_rationale": getattr(cd, "clinical_rationale", None) or cd.notes,
                "notes": cd.notes,
                "timestamp": cd.timestamp.isoformat() if cd.timestamp else None,
            }
            for cd in clinician_decisions
        ],
        "state_transitions": [
            {
                "id": st.id,
                "from_state": st.from_state,
                "to_state": st.to_state,
                "actor_id": st.actor_id,
                "actor_role": st.actor_role,
                "reason": st.reason,
                "state_version": st.state_version,
                "created_at": st.created_at.isoformat() if st.created_at else None,
            }
            for st in state_transitions
        ],
        "ai_advisory_results": [
            {
                "id": ar.id,
                "task_id": ar.task_id,
                "task_version": ar.task_version,
                "status": ar.status,
                "validation_state": ar.validation_state,
                "epistemic_state": ar.epistemic_state,
                "is_stale": ar.is_stale,
                "payload": ar.payload,
                "errors": ar.errors,
                "warnings": ar.warnings,
                "confidence": ar.confidence,
                "generated_at": ar.generated_at.isoformat() if ar.generated_at else None,
            }
            for ar in ai_results_items
        ],
        "is_synthetic_mode": True,
    }
