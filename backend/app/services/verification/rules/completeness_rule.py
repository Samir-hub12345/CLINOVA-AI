"""Completeness and Required Information Verification Rule."""

from typing import List, Tuple, Dict, Any
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
    CompletenessFieldStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class CompletenessRule(BaseVerificationRule):
    """Evaluates case completeness across standard clinical categories.
    
    Distinguishes: PRESENT, MISSING, UNKNOWN, NOT_APPLICABLE, UNVERIFIED, CONFLICTING, PARTIALLY_AVAILABLE.
    """
    rule_id: str = "clinical_completeness_rule"
    rule_version: str = "4.0.0"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        case = context.case
        facts_by_cat = context.facts_by_category

        # 1. Category: IDENTITY
        # Required fields: patient_id, age/approximate_age, gender
        if not case.approximate_age and not getattr(case.patient, "date_of_birth", None):
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.IDENTITY,
                    field_name="patient_age",
                    severity=FindingSeverity.HIGH,
                    is_blocking=False,
                    title="Missing Patient Age / Date of Birth",
                    description="Patient demographic age or date of birth is not recorded.",
                    explanation="Patient age is a critical demographic parameter for pediatric/geriatric clinical risk assessment and dosing reference.",
                    expected_information="Integer age (years) or ISO date of birth.",
                    observed_information="null",
                    metadata={"completeness_status": CompletenessFieldStatus.MISSING.value},
                )
            )

        if not case.gender:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.IDENTITY,
                    field_name="patient_gender",
                    severity=FindingSeverity.MEDIUM,
                    is_blocking=False,
                    title="Missing Patient Gender",
                    description="Patient biological sex or gender is unrecorded.",
                    explanation="Gender information aids in evaluating sex-specific presentations and reference intervals.",
                    expected_information="Biological sex or gender string.",
                    observed_information="null",
                    metadata={"completeness_status": CompletenessFieldStatus.MISSING.value},
                )
            )

        # 2. Category: PRESENTING_INFORMATION / SYMPTOM_INFORMATION
        # Check presenting complaints: case.raw_symptoms, case.normalized_symptoms, symptom facts
        symptom_facts = facts_by_cat.get("symptom", [])
        has_symptom_text = bool(
            (case.raw_symptoms and case.raw_symptoms.strip())
            or (case.normalized_symptoms and case.normalized_symptoms.strip())
        )

        if not symptom_facts and not has_symptom_text:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.PRESENTING_INFORMATION,
                    field_name="chief_complaint",
                    severity=FindingSeverity.BLOCKING,
                    is_blocking=True,
                    title="Missing Chief Presenting Complaint",
                    description="No symptoms or presenting complaints are recorded for this case.",
                    explanation="A triage case cannot be clinically reviewed without at least one documented presenting symptom or chief complaint.",
                    expected_information="Chief complaint description or active symptom facts.",
                    observed_information="None recorded",
                    metadata={"completeness_status": CompletenessFieldStatus.MISSING.value},
                )
            )
        else:
            # Check for symptom onset timing / duration
            symptoms_with_duration = [f for f in symptom_facts if f.duration or f.onset_approximate]
            if symptom_facts and not symptoms_with_duration:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.COMPLETENESS,
                        category=FindingCategory.SYMPTOM_INFORMATION,
                        field_name="symptom_duration",
                        severity=FindingSeverity.MEDIUM,
                        is_blocking=False,
                        title="Missing Symptom Duration / Onset Timing",
                        description="Symptom concepts are present but lack explicit onset timing or duration qualifiers.",
                        explanation="Documenting symptom duration (e.g., 'started 3 days ago') is essential for distinguishing acute presentations from chronic illness.",
                        expected_information="Duration phrase (e.g., '2 days') or approximate onset date.",
                        observed_information="No duration recorded on identified symptoms.",
                        fact_ids=[f.id for f in symptom_facts],
                        metadata={"completeness_status": CompletenessFieldStatus.PARTIALLY_AVAILABLE.value},
                    )
                )

        # 3. Category: MEASUREMENTS (Vital Signs)
        vital_facts = facts_by_cat.get("vital", [])
        has_vitals_text = bool(case.vitals and case.vitals.strip() and case.vitals != "{}")

        if not vital_facts and not has_vitals_text:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.MEASUREMENTS,
                    field_name="vital_signs",
                    severity=FindingSeverity.HIGH,
                    is_blocking=False,
                    title="Missing Objective Vital Signs",
                    description="No objective vital signs (blood pressure, heart rate, temperature, SpO2, respiratory rate) are recorded.",
                    explanation="Objective physiological measurements are vital for risk stratification and clinical triage assessment.",
                    expected_information="At least one objective vital sign measurement.",
                    observed_information="No vital signs recorded",
                    metadata={"completeness_status": CompletenessFieldStatus.MISSING.value},
                )
            )
        else:
            # Check specific core vitals
            vital_concepts = {v.concept.lower() for v in vital_facts}
            missing_core = []
            if not any("pressure" in c or "bp" in c for c in vital_concepts):
                missing_core.append("Blood Pressure")
            if not any("heart rate" in c or "pulse" in c for c in vital_concepts):
                missing_core.append("Heart Rate")
            if not any("temperature" in c or "temp" in c for c in vital_concepts):
                missing_core.append("Body Temperature")

            if len(missing_core) >= 2:
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.COMPLETENESS,
                        category=FindingCategory.MEASUREMENTS,
                        field_name="core_vital_signs",
                        severity=FindingSeverity.LOW,
                        is_blocking=False,
                        title=f"Incomplete Core Vital Signs: {', '.join(missing_core)}",
                        description=f"Core vitals missing from intake: {', '.join(missing_core)}.",
                        explanation="While some vitals are recorded, collecting a complete baseline vital signs panel improves assessment reliability.",
                        expected_information="Complete vitals panel (BP, HR, Temp, SpO2).",
                        observed_information=f"Missing: {', '.join(missing_core)}",
                        metadata={"completeness_status": CompletenessFieldStatus.PARTIALLY_AVAILABLE.value},
                    )
                )

        # 4. Category: HISTORY
        # Medications, allergies, and past medical history
        allergy_facts = facts_by_cat.get("allergy", [])
        med_facts = facts_by_cat.get("medication", [])
        history_facts = facts_by_cat.get("documented_condition", [])

        # Check if allergy status is documented or explicitly unknown/none
        if not allergy_facts and not getattr(case.patient, "allergies", None):
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.HISTORY,
                    field_name="allergies",
                    severity=FindingSeverity.MEDIUM,
                    is_blocking=False,
                    title="Allergy Status Unrecorded",
                    description="No allergy history or explicit 'no known allergies' statement was recorded.",
                    explanation="Patient drug and substance allergy history must be recorded or confirmed absent prior to prescription recommendations.",
                    expected_information="Specific allergy list or explicit confirmation of NKDA.",
                    observed_information="Unrecorded",
                    metadata={"completeness_status": CompletenessFieldStatus.UNKNOWN.value},
                )
            )

        # 5. Category: TIMELINE
        if not context.timeline_events:
            findings.append(
                FindingCandidate(
                    rule_id=self.rule_id,
                    rule_version=self.rule_version,
                    finding_type=FindingType.COMPLETENESS,
                    category=FindingCategory.TIMELINE,
                    field_name="case_timeline",
                    severity=FindingSeverity.LOW,
                    is_blocking=False,
                    title="Timeline Sequence Empty",
                    description="No chronological milestone events are parsed for this case version.",
                    explanation="A chronological timeline assists clinicians in understanding progression across pre-admission milestones.",
                    expected_information="Ordered clinical timeline events.",
                    observed_information="0 timeline events",
                    metadata={"completeness_status": CompletenessFieldStatus.MISSING.value},
                )
            )

        return findings, conflicts
