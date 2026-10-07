"""Question Candidate Engine for Phase 5 Intelligent Completion (Sub-Phase 5.4).

Generates empathetic, plain-language, strictly non-diagnostic question candidates
grounded in identified clinical information gaps.
"""

import uuid
from typing import List, Dict, Any, Optional
from app.models.completion import (
    GapType,
    QuestionType,
)
from app.services.completion.domain import InformationGap, QuestionCandidate


class QuestionCandidateEngine:
    """Generates structured candidate questions targeting specific clinical information gaps."""

    def generate_candidates(self, gaps: List[InformationGap]) -> List[QuestionCandidate]:
        """Generates one or more validated question candidates for each information gap."""
        candidates: List[QuestionCandidate] = []

        for gap in gaps:
            gap_candidates = self._generate_for_gap(gap)
            candidates.extend(gap_candidates)

        return candidates

    def _generate_for_gap(self, gap: InformationGap) -> List[QuestionCandidate]:
        candidates: List[QuestionCandidate] = []
        field_lower = gap.target_field.lower()

        # 0. Unresolved Conflicts (always takes precedence)
        if gap.gap_type in (GapType.UNRESOLVED_CONFLICT, "UNRESOLVED_CONFLICT"):
            val_a = gap.context_data.get("source_a_value", "first report")
            val_b = gap.context_data.get("source_b_value", "second report")
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text=f"Our records show different details regarding {gap.target_field.replace('_', ' ')}: '{val_a}' vs '{val_b}'. Which is more accurate?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": f"{val_a}", "value": f"clarify_{val_a}"},
                        {"label": f"{val_b}", "value": f"clarify_{val_b}"},
                        {"label": "Neither is completely accurate", "value": "neither_accurate"},
                    ],
                    clinical_rationale=f"Clarifies discrepancy between contradictory records for {gap.target_field}.",
                    base_clinical_utility=0.94,
                    burden_score=0.08,
                )
            )
            return candidates

        # 0b. Uncertain Facts
        if gap.gap_type in (GapType.UNCERTAIN_FACT, "UNCERTAIN_FACT"):
            fact_summary = gap.context_data.get("fact_summary") or gap.description
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text=f"Regarding '{fact_summary}': Could you confirm whether this is still actively happening?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "Yes, currently ongoing", "value": "confirmed_ongoing"},
                        {"label": "Occurs only occasionally", "value": "intermittent"},
                        {"label": "Resolved / No longer happening", "value": "resolved"},
                        {"label": "Not certain", "value": "uncertain"},
                    ],
                    clinical_rationale="Resolves uncertain clinical observation to enhance intake precision.",
                    base_clinical_utility=0.72,
                    burden_score=0.06,
                )
            )
            return candidates

        # 1. Symptom Duration & Onset
        if any(k in field_lower for k in ("duration", "onset", "symptom_duration")):
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="How long have you been experiencing these symptoms?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "Less than 24 hours", "value": "under_24_hours"},
                        {"label": "1 to 3 days", "value": "1_to_3_days"},
                        {"label": "4 to 7 days (about a week)", "value": "4_to_7_days"},
                        {"label": "1 to 2 weeks", "value": "1_to_2_weeks"},
                        {"label": "More than 2 weeks", "value": "over_2_weeks"},
                    ],
                    clinical_rationale="Clarifies symptom duration and onset timing for chronological intake record.",
                    base_clinical_utility=0.96,
                    burden_score=0.05,
                )
            )

        # 2. Allergies
        elif any(k in field_lower for k in ("allerg", "allergy", "allergies")):
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="Do you have any known allergies to medications, foods, or other substances?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "No known allergies (NKDA)", "value": "no_known_allergies"},
                        {"label": "Yes, allergies to specific medications", "value": "medication_allergies"},
                        {"label": "Yes, food or environmental allergies", "value": "other_allergies"},
                        {"label": "I am not sure", "value": "unsure"},
                    ],
                    clinical_rationale="Documents patient allergy history for medication safety prior to clinician review.",
                    base_clinical_utility=0.95,
                    burden_score=0.05,
                )
            )

        # 3. Vital Signs & Body Temperature
        elif any(k in field_lower for k in ("vital", "temp", "fever", "blood_pressure", "vital_signs")):
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="Have you checked your body temperature recently, or do you feel feverish?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "No fever, feels normal", "value": "normal_temp"},
                        {"label": "Mild fever (feeling warm or chills)", "value": "mild_fever"},
                        {"label": "High fever measured on a thermometer", "value": "high_fever"},
                        {"label": "Have not checked temperature", "value": "not_measured"},
                    ],
                    clinical_rationale="Captures baseline temperature and fever status to complete vital signs record.",
                    base_clinical_utility=0.88,
                    burden_score=0.05,
                )
            )

        # 4. Medication List
        elif any(k in field_lower for k in ("medication", "medicine", "drug", "rx")):
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="Are you currently taking any regular prescription or over-the-counter medications?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "No regular medications", "value": "no_medications"},
                        {"label": "Yes, daily prescription medications", "value": "prescription_meds"},
                        {"label": "Only occasional over-the-counter medicines", "value": "otc_meds"},
                        {"label": "Prefer not to say / Unsure", "value": "unsure"},
                    ],
                    clinical_rationale="Documents current medication regimen to identify potential drug interactions.",
                    base_clinical_utility=0.85,
                    burden_score=0.05,
                )
            )

        # 5. Symptom Severity & Pain Scale
        elif any(k in field_lower for k in ("severity", "intensity", "pain")):
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="On a scale of 1 to 10, how would you describe the intensity of your discomfort?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "1 to 3 (Mild - noticeable but easily tolerated)", "value": "mild_1_3"},
                        {"label": "4 to 6 (Moderate - interferes with daily routine)", "value": "moderate_4_6"},
                        {"label": "7 to 10 (Severe - very intense discomfort)", "value": "severe_7_10"},
                    ],
                    clinical_rationale="Records standardized subjective severity score for clinical evaluation.",
                    base_clinical_utility=0.80,
                    burden_score=0.05,
                )
            )

        # 6. Timeline Progression / Trajectory
        elif gap.gap_type in (GapType.INCOMPLETE_TIMELINE, "INCOMPLETE_TIMELINE") or "progression" in field_lower:
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text="Compared to when your symptoms first began, are they currently getting better, staying the same, or getting worse?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    options=[
                        {"label": "Getting better", "value": "improving"},
                        {"label": "Staying about the same", "value": "stable"},
                        {"label": "Getting worse", "value": "worsening"},
                    ],
                    clinical_rationale="Documents symptom trajectory and clinical progression over time.",
                    base_clinical_utility=0.75,
                    burden_score=0.05,
                )
            )

        # 9. Generic Fallback for Other Fields (e.g. contextual)
        else:
            readable_name = gap.target_field.replace("_", " ")
            candidates.append(
                QuestionCandidate(
                    candidate_id=str(uuid.uuid4()),
                    target_gap_id=gap.gap_id,
                    target_gap_type=gap.gap_type,
                    target_field=gap.target_field,
                    question_text=f"Could you please share any additional details regarding your {readable_name}?",
                    question_type=QuestionType.TEXT,
                    placeholder=f"Enter details about {readable_name}...",
                    clinical_rationale=f"Collects additional contextual information for {readable_name}.",
                    base_clinical_utility=0.55,
                    burden_score=0.20,
                )
            )

        return candidates
