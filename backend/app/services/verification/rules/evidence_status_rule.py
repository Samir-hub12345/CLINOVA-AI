"""Evidence status and quality awareness verification rule."""

from typing import List, Tuple
from app.models.verification import (
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
)
from app.services.verification.base import BaseVerificationRule, FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class EvidenceStatusRule(BaseVerificationRule):
    """Enforces evidence quality awareness: presence != verification.
    
    Identifies AI-derived, OCR-extracted, or patient-claimed facts that require clinical confirmation.
    """
    rule_id: str = "evidence_status_awareness_rule"
    rule_version: str = "4.0.0"

    async def evaluate(
        self, context: VerificationContext
    ) -> Tuple[List[FindingCandidate], List[ConflictCandidate]]:
        findings: List[FindingCandidate] = []
        conflicts: List[ConflictCandidate] = []

        ev_map = context.evidence_by_id

        # 1. Fact-level evaluation
        for fact in context.facts:
            source_ev = ev_map.get(fact.source_evidence_id) if fact.source_evidence_id else None
            source_type_val = source_ev.source_type.value if source_ev and hasattr(source_ev.source_type, "value") else (str(source_ev.source_type) if source_ev else (fact.attribution or "").lower())

            # 1.1 Unverified AI Extraction
            if fact.attribution in ("AI_EXTRACTED", "AI_INFERRED") or (
                source_ev and source_type_val in ("ai_extracted", "ai_inferred")
            ):
                if fact.verification_state == "unverified":
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.EVIDENCE_QUALITY,
                            category=FindingCategory.VERIFICATION,
                            field_name=fact.concept,
                            severity=FindingSeverity.MEDIUM,
                            is_blocking=False,
                            title=f"Unverified AI Extraction: {fact.concept}",
                            description=f"Concept '{fact.concept}' was extracted by AI pipeline but has not received clinical verification.",
                            explanation="Automated AI extractions remain unverified machine outputs until reviewed by a healthcare professional.",
                            expected_information="Human clinician or staff verification sign-off.",
                            observed_information=f"AI extracted with confidence {fact.confidence_score:.2f}, verification_state='unverified'",
                            fact_ids=[fact.id],
                            source_evidence_ids=[fact.source_evidence_id] if fact.source_evidence_id else [],
                        )
                    )

            # 1.2 OCR-derived clinical measurement without staff verification
            if fact.category in ("vital", "lab_value") and (
                fact.attribution == "DOCUMENT_EXTRACTED"
                or (source_ev and source_type_val in ("ocr_derived", "document_derived"))
            ):
                if fact.verification_state == "unverified":
                    findings.append(
                        FindingCandidate(
                            rule_id=self.rule_id,
                            rule_version=self.rule_version,
                            finding_type=FindingType.EVIDENCE_QUALITY,
                            category=FindingCategory.DOCUMENTS,
                            field_name=fact.concept,
                            severity=FindingSeverity.LOW,
                            is_blocking=False,
                            title=f"Unverified OCR Extraction: {fact.concept}",
                            description=f"Measurement '{fact.concept}' ({fact.value} {fact.unit or ''}) was derived via document OCR and awaits clinical verification.",
                            explanation="Optical character recognition from scanned records may contain character misrecognitions or artifacts.",
                            expected_information="Staff verification against original scanned document.",
                            observed_information=f"OCR raw value: '{fact.value}'",
                            fact_ids=[fact.id],
                            source_evidence_ids=[fact.source_evidence_id] if fact.source_evidence_id else [],
                        )
                    )

            # 1.3 Patient-Reported Vital Signs (Self-Report vs Clinical Device)
            if fact.category == "vital" and fact.attribution == "PATIENT_REPORTED":
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.EVIDENCE_QUALITY,
                        category=FindingCategory.MEASUREMENTS,
                        field_name=fact.concept,
                        severity=FindingSeverity.LOW,
                        is_blocking=False,
                        title=f"Patient-Reported Vital Sign: {fact.concept}",
                        description=f"Vital sign '{fact.concept}' ({fact.value} {fact.unit or ''}) is patient-reported rather than clinically measured.",
                        explanation="Patient self-reported vitals must be distinguished from objective medical device measurements taken at triage.",
                        expected_information="Calibrated medical device measurement recorded by clinical staff.",
                        observed_information=f"Patient-reported: '{fact.value}'",
                        fact_ids=[fact.id],
                        source_evidence_ids=[fact.source_evidence_id] if fact.source_evidence_id else [],
                    )
                )

        # 2. Evidence-level evaluation (for evidence not directly converted to discrete facts)
        linked_evidence_ids = {f.source_evidence_id for f in context.facts if f.source_evidence_id}
        for ev in context.evidence_items:
            st = ev.source_type.value if hasattr(ev.source_type, "value") else str(ev.source_type)
            vs = ev.verification_state.value if hasattr(ev.verification_state, "value") else str(ev.verification_state)
            field = ev.canonical_field or "clinical_evidence"

            if "ai" in st.lower() and vs.lower() not in ("staff_verified", "confirmed", "clinician_verified"):
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.EVIDENCE_QUALITY,
                        category=FindingCategory.VERIFICATION,
                        field_name=field,
                        severity=FindingSeverity.MEDIUM,
                        is_blocking=False,
                        title=f"Unverified AI Evidence: {field}",
                        description=f"Evidence record for '{field}' was derived via AI pipeline and has not received clinical verification.",
                        explanation="Automated AI extractions remain unverified machine outputs until reviewed by a healthcare professional.",
                        expected_information="Human clinician or staff verification sign-off.",
                        observed_information=f"Source type '{st}', verification state '{vs}'",
                        source_evidence_ids=[ev.id],
                    )
                )
            elif ("ocr" in st.lower() or "document" in st.lower()) and vs.lower() not in ("staff_verified", "confirmed"):
                findings.append(
                    FindingCandidate(
                        rule_id=self.rule_id,
                        rule_version=self.rule_version,
                        finding_type=FindingType.EVIDENCE_QUALITY,
                        category=FindingCategory.DOCUMENTS,
                        field_name=field,
                        severity=FindingSeverity.LOW,
                        is_blocking=False,
                        title=f"Unverified OCR Document Evidence: {field}",
                        description=f"Document evidence for '{field}' was derived via OCR and awaits clinical verification.",
                        explanation="Optical character recognition from scanned records may contain character misrecognitions or artifacts.",
                        expected_information="Staff verification against original scanned document.",
                        observed_information=f"OCR raw value: '{ev.raw_value}'",
                        source_evidence_ids=[ev.id],
                    )
                )

        return findings, conflicts
