"""Cross-source and cross-modal conflict detection rule."""

from datetime import datetime
from typing import List, Tuple, Dict, Optional
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
    ConflictType,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class CrossSourceConflictRule(BaseVerificationRule):
    """Detects and preserves cross-source, cross-modal, value, and polarity contradictions.
    
    Guarantees that contradictory values are never silently overwritten or averaged.
    """
    rule_id: str = "cross_source_conflict_rule"
    rule_version: str = "4.0.0"

    def _determine_modality(self, source_type: Optional[str]) -> str:
        if not source_type:
            return "UNKNOWN"
        st = source_type.lower()
        if "voice" in st or "speech" in st or "audio" in st:
            return "VOICE"
        if "ocr" in st or "document" in st or "pdf" in st:
            return "DOCUMENT_OCR"
        if "staff" in st or "clinician" in st:
            return "CLINICIAN_ENTRY"
        if "text" in st or "patient" in st:
            return "PATIENT_TEXT"
        if "ai" in st:
            return "AI_DERIVED"
        return "STRUCTURED_INTAKE"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        ev_map = context.evidence_by_id

        # 1. Process facts with has_conflict=True flagged by Phase 3 Multimodal Fusion
        for fact in context.facts:
            if fact.has_conflict:
                source_a_ev = ev_map.get(fact.source_evidence_id) if fact.source_evidence_id else None
                source_b_ev = ev_map.get(fact.conflicting_source_id) if fact.conflicting_source_id else None

                mod_a = self._determine_modality(source_a_ev.source_type.value if source_a_ev else fact.attribution)
                mod_b = self._determine_modality(source_b_ev.source_type.value if source_b_ev else "prior_source")

                val_a = f"{fact.value} {fact.unit or ''}".strip()
                val_b = fact.conflicting_value or "Discrepant value"

                c_type = ConflictType.MODALITY_CONFLICT if mod_a != mod_b else ConflictType.VALUE_CONFLICT

                conflict = ConflictCandidate(
                    rule_id=self.rule_id,
                    conflict_type=c_type,
                    field_name=fact.concept,
                    severity=FindingSeverity.HIGH,
                    source_a_value=val_a,
                    source_b_value=val_b,
                    source_a_evidence_id=source_a_ev.id if source_a_ev else fact.source_evidence_id,
                    source_a_type=source_a_ev.source_type.value if source_a_ev else fact.attribution,
                    source_a_modality=mod_a,
                    source_a_timestamp=source_a_ev.observed_at or source_a_ev.created_at if source_a_ev else None,
                    source_b_evidence_id=source_b_ev.id if source_b_ev else fact.conflicting_source_id,
                    source_b_type=source_b_ev.source_type.value if source_b_ev else "conflicting_record",
                    source_b_modality=mod_b,
                    source_b_timestamp=source_b_ev.observed_at or source_b_ev.created_at if source_b_ev else None,
                    resolution_state=FindingStatus.UNRESOLVED,
                )
                conflicts.append(conflict)

                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.CONFLICT,
                        category=FindingCategory.MEASUREMENTS if fact.category in ("vital", "lab_value") else FindingCategory.SYMPTOM_INFORMATION,
                        field_name=fact.concept,
                        severity=FindingSeverity.HIGH,
                        is_blocking=False,
                        title=f"Cross-Source Discrepancy on {fact.concept}",
                        description=f"Contradictory values recorded across sources for '{fact.concept}': [{mod_a}] '{val_a}' vs [{mod_b}] '{val_b}'.",
                        explanation="Both contradictory records are preserved intact. Clinical verification is required to adjudicate authoritative measurement.",
                        expected_information="Single authoritative clinical observation.",
                        observed_information=f"Source A ({mod_a}): '{val_a}', Source B ({mod_b}): '{val_b}'",
                        fact_ids=[fact.id],
                        source_evidence_ids=[i for i in [fact.source_evidence_id, fact.conflicting_source_id] if i],
                    )
                )

        # 2. Check for Polarity Contradictions across distinct facts of the same concept
        # (e.g. one fact AFFIRMED "Fever", another fact NEGATED "Fever")
        facts_by_concept: Dict[str, List[Any]] = {}
        for f in context.facts:
            facts_by_concept.setdefault(f.concept.lower(), []).append(f)

        for concept_key, concept_facts in facts_by_concept.items():
            if len(concept_facts) > 1:
                polarities = {f.polarity for f in concept_facts}
                if "AFFIRMED" in polarities and "NEGATED" in polarities:
                    f_aff = next(f for f in concept_facts if f.polarity == "AFFIRMED")
                    f_neg = next(f for f in concept_facts if f.polarity == "NEGATED")

                    ev_aff = ev_map.get(f_aff.source_evidence_id) if f_aff.source_evidence_id else None
                    ev_neg = ev_map.get(f_neg.source_evidence_id) if f_neg.source_evidence_id else None

                    mod_aff = self._determine_modality(ev_aff.source_type.value if ev_aff else f_aff.attribution)
                    mod_neg = self._determine_modality(ev_neg.source_type.value if ev_neg else f_neg.attribution)

                    conflict = ConflictCandidate(
                        rule_id=self.rule_id,
                        conflict_type=ConflictType.STATUS_CONFLICT,
                        field_name=f_aff.concept,
                        severity=FindingSeverity.HIGH,
                        source_a_value=f"AFFIRMED: {f_aff.value}",
                        source_b_value=f"NEGATED: {f_neg.value}",
                        source_a_evidence_id=ev_aff.id if ev_aff else f_aff.source_evidence_id,
                        source_a_type=ev_aff.source_type.value if ev_aff else f_aff.attribution,
                        source_a_modality=mod_aff,
                        source_b_evidence_id=ev_neg.id if ev_neg else f_neg.source_evidence_id,
                        source_b_type=ev_neg.source_type.value if ev_neg else f_neg.attribution,
                        source_b_modality=mod_neg,
                        resolution_state=FindingStatus.UNRESOLVED,
                    )
                    conflicts.append(conflict)

                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.CONFLICT,
                            category=FindingCategory.SYMPTOM_INFORMATION,
                            field_name=f_aff.concept,
                            severity=FindingSeverity.HIGH,
                            is_blocking=False,
                            title=f"Polarity Contradiction on {f_aff.concept}",
                            description=f"Concept '{f_aff.concept}' is affirmed in one record ({mod_aff}) and negated in another ({mod_neg}).",
                            explanation="Contradictory polarity (presence vs absence) indicates conflicting patient reporting or inconsistent clinician notes.",
                            expected_information="Consistent polarity (either present or ruled out).",
                            observed_information=f"AFFIRMED via {mod_aff} vs NEGATED via {mod_neg}",
                            fact_ids=[f_aff.id, f_neg.id],
                            source_evidence_ids=[i for i in [f_aff.source_evidence_id, f_neg.source_evidence_id] if i],
                        )
                    )

        # 3. Check for Cross-Modal discrepancies between raw evidence items directly
        # Example: Audio transcript says "started 3 days ago" vs text note says "started yesterday"
        text_evs = [e for e in context.evidence_items if "text" in e.source_type.value]
        voice_evs = [e for e in context.evidence_items if "voice" in e.source_type.value]

        for t_ev in text_evs:
            for v_ev in voice_evs:
                t_val = (t_ev.raw_value or "").lower()
                v_val = (v_ev.raw_value or "").lower()
                # Check known duration/temporal discrepancies
                if ("yesterday" in t_val and ("3 days" in v_val or "three days" in v_val or "week" in v_val)) or (
                    "yesterday" in v_val and ("3 days" in t_val or "three days" in t_val or "week" in t_val)
                ):
                    conflict = ConflictCandidate(
                        rule_id=self.rule_id,
                        conflict_type=ConflictType.TEMPORAL_CONFLICT,
                        field_name="symptom_onset_duration",
                        severity=FindingSeverity.HIGH,
                        source_a_value=t_ev.raw_value,
                        source_b_value=v_ev.raw_value,
                        source_a_evidence_id=t_ev.id,
                        source_a_type=t_ev.source_type.value,
                        source_a_modality="PATIENT_TEXT",
                        source_b_evidence_id=v_ev.id,
                        source_b_type=v_ev.source_type.value,
                        source_b_modality="PATIENT_VOICE",
                        resolution_state=FindingStatus.UNRESOLVED,
                    )
                    conflicts.append(conflict)

                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.CONFLICT,
                            category=FindingCategory.TIMELINE,
                            field_name="symptom_onset",
                            severity=FindingSeverity.HIGH,
                            is_blocking=False,
                            title="Cross-Modal Temporal Discrepancy (Voice vs Text)",
                            description=f"Voice transcript and text intake document conflicting symptom duration estimates.",
                            explanation="The patient provided different onset durations across oral voice recording and written intake.",
                            expected_information="Concordant symptom onset timeframe.",
                            observed_information=f"Text: '{t_ev.raw_value}' vs Voice: '{v_ev.raw_value}'",
                            source_evidence_ids=[t_ev.id, v_ev.id],
                        )
                    )

        # 4. Check for direct evidence-level value conflicts on matching canonical_field
        ev_by_field: Dict[str, List[Any]] = {}
        for ev in context.evidence_items:
            cf = (ev.canonical_field or "").strip().lower()
            if cf:
                ev_by_field.setdefault(cf, []).append(ev)

        for field_key, ev_list in ev_by_field.items():
            if len(ev_list) > 1:
                for i in range(len(ev_list)):
                    for j in range(i + 1, len(ev_list)):
                        ev_a = ev_list[i]
                        ev_b = ev_list[j]
                        val_a = (ev_a.normalized_value or ev_a.raw_value or "").strip()
                        val_b = (ev_b.normalized_value or ev_b.raw_value or "").strip()
                        if val_a and val_b and val_a.lower() != val_b.lower():
                            existing = any(
                                (c.source_a_evidence_id == ev_a.id and c.source_b_evidence_id == ev_b.id)
                                or (c.source_a_evidence_id == ev_b.id and c.source_b_evidence_id == ev_a.id)
                                for c in conflicts
                            )
                            if not existing:
                                st_a = ev_a.source_type.value if hasattr(ev_a.source_type, "value") else str(ev_a.source_type)
                                st_b = ev_b.source_type.value if hasattr(ev_b.source_type, "value") else str(ev_b.source_type)
                                mod_a = self._determine_modality(st_a)
                                mod_b = self._determine_modality(st_b)

                                c_type = ConflictType.MODALITY_CONFLICT if mod_a != mod_b else ConflictType.VALUE_CONFLICT
                                conflict = ConflictCandidate(
                                    rule_id=self.rule_id,
                                    conflict_type=c_type,
                                    field_name=field_key,
                                    severity=FindingSeverity.HIGH,
                                    source_a_value=val_a,
                                    source_b_value=val_b,
                                    source_a_evidence_id=ev_a.id,
                                    source_a_type=st_a,
                                    source_a_modality=mod_a,
                                    source_b_evidence_id=ev_b.id,
                                    source_b_type=st_b,
                                    source_b_modality=mod_b,
                                    resolution_state=FindingStatus.UNRESOLVED,
                                )
                                conflicts.append(conflict)

                                is_measurement = "vital" in field_key or "temp" in field_key or "pressure" in field_key or "lab" in field_key
                                findings.append(
                                    FindingCandidate(
                                        rule_id=self.rule_id,
                                        rule_version=self.rule_version,
                                        finding_type=FindingType.CONFLICT,
                                        category=FindingCategory.MEASUREMENTS if is_measurement else FindingCategory.SYMPTOM_INFORMATION,
                                        field_name=field_key,
                                        severity=FindingSeverity.HIGH,
                                        is_blocking=False,
                                        title=f"Cross-Source Evidence Conflict: {field_key}",
                                        description=f"Contradictory records across sources for '{field_key}': [{mod_a}] '{val_a}' vs [{mod_b}] '{val_b}'.",
                                        explanation="Both contradictory records are preserved intact without silent overwrite. Clinical verification is required.",
                                        expected_information="Single authoritative clinical observation.",
                                        observed_information=f"Source A ({mod_a}): '{val_a}' vs Source B ({mod_b}): '{val_b}'",
                                        source_evidence_ids=[ev_a.id, ev_b.id],
                                    )
                                )

        return findings, conflicts
