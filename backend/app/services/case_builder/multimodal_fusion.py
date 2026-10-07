"""Multimodal fusion, multi-source linkage, conflict preservation, and specialty signal engine for Clinova AI."""

from typing import List, Dict, Any, Tuple
from app.services.case_builder.extraction_engine import CandidateFact
from app.schemas.canonical_case import SpecialtySignal


class MultimodalFusionEngine:
    """Fuses multi-source evidence, tracks provenance linkage, preserves conflicts, and computes specialty signals."""

    SPECIALTY_PROFILES = {
        "Cardiology": [
            "Chest Pain", "Dyspnea", "Diaphoresis", "Palpitations",
            "Essential Hypertension", "Coronary Artery Disease", "Blood Pressure", "Heart Rate", "Troponin"
        ],
        "Pulmonology": [
            "Dyspnea", "Cough", "Wheezing", "Oxygen Saturation", "Respiratory Rate",
            "Bronchial Asthma", "Albuterol"
        ],
        "Endocrinology": [
            "Type 2 Diabetes Mellitus", "Random Blood Sugar", "Fasting Blood Sugar",
            "HbA1c", "Metformin"
        ],
        "Infectious Disease": [
            "Pyrexia", "Chills", "Total Leukocyte Count", "Platelet Count"
        ],
        "Neurology": [
            "Headache", "Dizziness", "Vertigo"
        ],
    }

    def __init__(self):
        pass

    def fuse_and_link_facts(
        self, facts: List[CandidateFact]
    ) -> Tuple[List[CandidateFact], List[Dict[str, Any]]]:
        """Fuses candidate facts by linking supporting evidence and tagging conflicts.
        
        Returns:
            Tuple[List[CandidateFact], List[Dict[str, Any]]]: (fused_facts, conflicts_list)
        """
        conflicts: List[Dict[str, Any]] = []
        if not facts:
            return [], conflicts

        # Group facts by (category, concept)
        grouped: Dict[Tuple[str, str], List[CandidateFact]] = {}
        for f in facts:
            key = (f.category, f.concept.lower().strip())
            grouped.setdefault(key, []).append(f)

        fused_facts: List[CandidateFact] = []

        for (category, concept_lower), fact_group in grouped.items():
            if len(fact_group) == 1:
                f = fact_group[0]
                if f.source_evidence_id:
                    f.supporting_evidence_ids = [f.source_evidence_id]
                else:
                    f.supporting_evidence_ids = []
                f.has_conflict = False
                f.conflicting_value = None
                f.conflicting_source_id = None
                fused_facts.append(f)
                continue

            # Multi-source group: Check for conflicts
            # 1. Polarity Conflict (AFFIRMED vs NEGATED)
            affirmed = [f for f in fact_group if f.polarity == "AFFIRMED"]
            negated = [f for f in fact_group if f.polarity == "NEGATED"]

            # 2. Value Conflict for vitals/labs
            has_value_conflict = False
            distinct_values = {f.normalized_value or f.value for f in fact_group}

            is_conflicted = bool((affirmed and negated) or (len(distinct_values) > 1 and category in ("vital", "lab_value")))

            all_evidence_ids = [f.source_evidence_id for f in fact_group if f.source_evidence_id]

            if is_conflicted:
                # Conflict Preservation Rule: Keep ALL representations, mark conflict!
                for idx, f in enumerate(fact_group):
                    f.supporting_evidence_ids = all_evidence_ids
                    f.has_conflict = True
                    # Find counter-fact
                    counter = fact_group[(idx + 1) % len(fact_group)]
                    f.conflicting_value = f"Contradicts {counter.attribution}: {counter.value}"
                    f.conflicting_source_id = counter.source_evidence_id

                    conflicts.append({
                        "category": f.category,
                        "concept": f.concept,
                        "value_a": f.value,
                        "source_a": f.source_evidence_id,
                        "value_b": counter.value,
                        "source_b": counter.source_evidence_id,
                        "conflict_type": "POLARITY_MISMATCH" if (affirmed and negated) else "NUMERICAL_DISCREPANCY",
                    })
                    fused_facts.append(f)
            else:
                # Consolidated: values and polarities agree across multiple sources!
                primary = fact_group[0]
                primary.supporting_evidence_ids = list(set(all_evidence_ids))
                primary.has_conflict = False
                primary.conflicting_value = None
                primary.conflicting_source_id = None
                # If supported by clinician/device or multiple sources, increase confidence
                if len(all_evidence_ids) > 1:
                    primary.certainty = "CONFIRMED"
                fused_facts.append(primary)

        return fused_facts, conflicts

    def compute_specialty_signals(self, facts: List[CandidateFact]) -> List[SpecialtySignal]:
        """Computes relevant clinical specialty routing signals based on active extracted facts."""
        signals: List[SpecialtySignal] = []
        active_concepts = {f.concept for f in facts if f.polarity == "AFFIRMED"}

        for specialty, target_concepts in self.SPECIALTY_PROFILES.items():
            matches = [c for c in target_concepts if c in active_concepts]
            if matches:
                # Score between 0.0 and 1.0 based on match ratio and urgency weighting
                score = round(min(1.0, len(matches) / max(2, len(target_concepts) * 0.4)), 2)
                rationale = f"Detected {len(matches)} associated concepts: {', '.join(matches)}"
                signals.append(
                    SpecialtySignal(
                        specialty=specialty,
                        relevance_score=score,
                        matching_concepts=matches,
                        rationale=rationale,
                    )
                )

        signals.sort(key=lambda s: s.relevance_score, reverse=True)
        return signals
