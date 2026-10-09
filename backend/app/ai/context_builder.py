"""CLINOVA AI — Application AI Context Builder.

Phase 18: AI Application Integration.
Builds controlled, minimal, evidence-grounded context packs for local AI inference.
Enforces:
1. Instruction Hierarchy: SYSTEM SAFETY POLICY -> TASK CONTRACT -> STRUCTURED CASE DATA -> UNTRUSTED FREE TEXT.
2. Untrusted text sanitization & passive data encapsulation via InputSanitizer.
3. Strict secret exclusion (Zero passwords, tokens, JWTs, or unrelated case data).
4. Deterministic context fingerprinting across sorted evidence and case version.
5. Deterministic clinical safety context inclusion (NEWS2, Shock Index, Red Flags).
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import (
    Case,
    Patient,
    Evidence,
    Vital,
    TimelineEvent,
    FollowUpQuestion,
    TriageNote,
    utc_now,
)
from app.ai_runtime.validation.sanitizer import InputSanitizer, SanitizedContent
from app.domain.triage import compute_deterministic_triage


class AIContextPack:
    """Assembled context payload ready for local AI execution."""

    def __init__(
        self,
        case_id: str,
        case_version: int,
        context_fingerprint: str,
        evidence_items_for_runtime: List[Dict[str, Any]],
        allowed_evidence_ids: Set[str],
        allowed_vital_params: Set[str],
        structured_summary_text: str,
        deterministic_safety_context: Dict[str, Any],
        is_suspicious_input: bool = False,
        detected_injections: Optional[List[str]] = None,
    ):
        self.case_id = case_id
        self.case_version = case_version
        self.context_fingerprint = context_fingerprint
        self.evidence_items_for_runtime = evidence_items_for_runtime
        self.allowed_evidence_ids = allowed_evidence_ids
        self.allowed_vital_params = allowed_vital_params
        self.structured_summary_text = structured_summary_text
        self.deterministic_safety_context = deterministic_safety_context
        self.is_suspicious_input = is_suspicious_input
        self.detected_injections = detected_injections or []


class AIContextBuilder:
    """Builder enforcing strict context boundary, privacy, and grounding."""

    @classmethod
    async def build(
        cls,
        case: Case,
        db: AsyncSession,
        now: Optional[datetime] = None,
    ) -> AIContextPack:
        """Constructs an isolated, defensively sanitized AI context pack from Master Case."""
        if now is None:
            now = utc_now()

        # 1. Fetch relevant case entities
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
        follow_ups = (await db.execute(fq_stmt)).scalars().all()

        # 2. Compute Deterministic Clinical Safety Context
        triage_support = compute_deterministic_triage(
            case_id=case.id,
            pathway=case.pathway,
            current_state=case.current_state,
            presenting_complaint=case.presenting_complaint,
            latest_vital=latest_vital,
            now=now,
        )

        # 3. Sanitize untrusted text inputs and extract allowed evidence IDs
        allowed_evidence_ids: Set[str] = set()
        evidence_items_for_runtime: List[Dict[str, Any]] = []
        sanitized_evidence_blocks: List[str] = []
        detected_injections: List[str] = []
        is_suspicious = False

        # Add presenting complaint as baseline evidence if present
        if case.presenting_complaint:
            pc_sanitized: SanitizedContent = InputSanitizer.sanitize(
                case.presenting_complaint,
                source_id=f"pc-{case.id[:8]}",
            )
            if pc_sanitized.is_suspicious:
                is_suspicious = True
                detected_injections.extend(pc_sanitized.injection_patterns_detected)
            pc_ev_id = f"ev-complaint-{case.id[:8]}"
            allowed_evidence_ids.add(pc_ev_id)
            evidence_items_for_runtime.append({
                "id": pc_ev_id,
                "text": f"Presenting Complaint: {pc_sanitized.sanitized_text}",
            })
            sanitized_evidence_blocks.append(pc_sanitized.delimited_block)

        # Sanitize and assemble discrete evidence records
        for ev in evidence_items:
            allowed_evidence_ids.add(ev.id)
            ev_text = f"{ev.parameter_name}: {ev.content_value}"
            if ev.unit:
                ev_text += f" {ev.unit}"
            ev_sanitized: SanitizedContent = InputSanitizer.sanitize(ev_text, source_id=ev.id)
            if ev_sanitized.is_suspicious:
                is_suspicious = True
                detected_injections.extend(ev_sanitized.injection_patterns_detected)

            evidence_items_for_runtime.append({
                "id": ev.id,
                "text": ev_sanitized.sanitized_text,
                "parameter_name": ev.parameter_name,
                "epistemic_state": ev.epistemic_state,
                "source_class": ev.source_class,
                "confidence_score": ev.confidence_score,
            })
            sanitized_evidence_blocks.append(ev_sanitized.delimited_block)

        # 4. Collect allowed vital sign parameters from actual recorded vitals
        allowed_vital_params: Set[str] = set()
        vitals_summary_lines: List[str] = []
        if latest_vital:
            if latest_vital.heart_rate is not None:
                allowed_vital_params.add("HR")
                vitals_summary_lines.append(f"HR: {latest_vital.heart_rate} bpm")
            if latest_vital.systolic_bp is not None:
                allowed_vital_params.add("SBP")
                vitals_summary_lines.append(f"SBP: {latest_vital.systolic_bp} mmHg")
            if latest_vital.diastolic_bp is not None:
                allowed_vital_params.add("DBP")
                vitals_summary_lines.append(f"DBP: {latest_vital.diastolic_bp} mmHg")
            if latest_vital.respiratory_rate is not None:
                allowed_vital_params.add("RR")
                vitals_summary_lines.append(f"RR: {latest_vital.respiratory_rate} /min")
            if latest_vital.spo2_percent is not None:
                allowed_vital_params.add("SPO2")
                vitals_summary_lines.append(f"SpO2: {latest_vital.spo2_percent}%")
            if latest_vital.temperature_celsius is not None:
                allowed_vital_params.add("TEMP")
                vitals_summary_lines.append(f"Temp: {latest_vital.temperature_celsius} C")
            if latest_vital.avpu_score:
                allowed_vital_params.add("AVPU")
                vitals_summary_lines.append(f"AVPU: {latest_vital.avpu_score}")

            # Also add vital record as valid evidence pointer
            allowed_evidence_ids.add(latest_vital.id)
            evidence_items_for_runtime.append({
                "id": latest_vital.id,
                "text": "Vitals: " + ", ".join(vitals_summary_lines),
            })

        # 5. Timeline summaries
        timeline_summary_lines: List[str] = []
        for tl in timeline_items:
            timeline_summary_lines.append(
                f"- [{tl.event_timestamp.isoformat() if tl.event_timestamp else 'unrecorded'}] {tl.event_title}: {tl.event_content}"
            )
            if tl.evidence_id:
                allowed_evidence_ids.add(tl.evidence_id)

        # 6. Follow-up summaries
        follow_up_lines: List[str] = []
        for q in follow_ups:
            ans_text = "; ".join(a.answer_text for a in q.answers) if q.answers else "UNANSWERED"
            follow_up_lines.append(f"Q: {q.question_text} | A: {ans_text}")

        # 7. Build structured summary text adhering to strict instruction hierarchy
        news2_data = triage_support.get("news2", {})
        shock_data = triage_support.get("shock_index", {})
        red_flags_raw = triage_support.get("red_flags", [])
        red_flag_labels: List[str] = []
        for rf in red_flags_raw:
            if isinstance(rf, dict):
                if rf.get("triggered", True):
                    red_flag_labels.append(str(rf.get("name") or rf.get("flag_id") or rf))
            else:
                red_flag_labels.append(str(rf))

        missing_vitals_raw = triage_support.get("missing_critical_vitals", [])
        missing_vital_labels: List[str] = [
            str(mv.get("name") or mv.get("parameter") or mv) if isinstance(mv, dict) else str(mv)
            for mv in missing_vitals_raw
        ]

        structured_summary_text = (
            "=== SYSTEM CLINICAL SAFETY CONTEXT (DETERMINISTIC RULES - AUTHORITATIVE) ===\n"
            f"Case Number: {case.case_number}\n"
            f"Pathway: {case.pathway}\n"
            f"State Version: {case.state_version}\n"
            f"Acuity Tier: {triage_support.get('acuity_tier', 'ROUTINE')}\n"
            f"Priority Tier: {triage_support.get('priority_tier', 'P4_ROUTINE')}\n"
            f"NEWS2 Score: {news2_data.get('score', 'N/A')} ({news2_data.get('risk_level', 'N/A')})\n"
            f"Shock Index: {shock_data.get('value', 'N/A')} ({shock_data.get('category', 'NORMAL')})\n"
            f"Active Red Flags: {', '.join(red_flag_labels) if red_flag_labels else 'None'}\n"
            f"Missing Critical Vitals: {', '.join(missing_vital_labels) if missing_vital_labels else 'None'}\n"
            f"Epistemic Uncertainty: {triage_support.get('uncertainty_score', 0.5):.2f}\n\n"
            "=== RECORDED VITALS ===\n"
            + ("\n".join(vitals_summary_lines) if vitals_summary_lines else "No vitals recorded.")
            + "\n\n=== CHRONOLOGICAL MILESTONES ===\n"
            + ("\n".join(timeline_summary_lines) if timeline_summary_lines else "No timeline events recorded.")
            + "\n\n=== PRIOR INQUIRIES & ANSWERS ===\n"
            + ("\n".join(follow_up_lines) if follow_up_lines else "No inquiries recorded.")
            + "\n\n=== UNTRUSTED CLINICAL EVIDENCE BLOCKS ===\n"
            + ("\n\n".join(sanitized_evidence_blocks) if sanitized_evidence_blocks else "No evidence blocks available.")
        )

        # 8. Compute Deterministic Context Fingerprint
        canonical_fp_data = {
            "case_id": case.id,
            "case_version": case.state_version,
            "evidence_ids": sorted(list(allowed_evidence_ids)),
            "vital_values": vitals_summary_lines,
            "pathway": case.pathway,
            "acuity_tier": triage_support.get("acuity_tier"),
            "priority_tier": triage_support.get("priority_tier"),
        }
        fp_json = json.dumps(canonical_fp_data, sort_keys=True)
        context_fingerprint = hashlib.sha256(fp_json.encode("utf-8")).hexdigest()

        return AIContextPack(
            case_id=case.id,
            case_version=case.state_version,
            context_fingerprint=context_fingerprint,
            evidence_items_for_runtime=evidence_items_for_runtime,
            allowed_evidence_ids=allowed_evidence_ids,
            allowed_vital_params=allowed_vital_params,
            structured_summary_text=structured_summary_text,
            deterministic_safety_context=triage_support,
            is_suspicious_input=is_suspicious,
            detected_injections=list(set(detected_injections)),
        )
