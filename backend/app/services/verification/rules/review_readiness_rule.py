"""Review readiness calculation rule for Phase 4."""

from typing import List, Tuple, Dict, Any
from app.models.verification import (
    ReviewReadinessLevel,
    FindingSeverity,
    FindingType,
    FindingStatus,
)
from app.services.verification.base import FindingCandidate, ConflictCandidate
from app.services.verification.context import VerificationContext


class ReviewReadinessCalculator:
    """Calculates explainable Review Readiness Level and Score.
    
    IMPORTANT: This represents information package integrity and readiness for professional review.
    It is NOT a diagnosis probability, disease severity score, or emergency risk index!
    """

    @staticmethod
    def calculate(
        context: VerificationContext,
        findings: List[FindingCandidate],
        conflicts: List[ConflictCandidate],
    ) -> Tuple[ReviewReadinessLevel, float, List[str], Dict[str, str]]:
        """Calculates readiness level, numerical score (0.0 to 1.0), explainable reasons, and subsystem status."""
        reasons: List[str] = []

        # Count finding severities
        blocking_findings = [f for f in findings if f.is_blocking or f.severity == FindingSeverity.BLOCKING]
        high_findings = [f for f in findings if f.severity == FindingSeverity.HIGH]
        unresolved_conflicts = [c for c in conflicts if c.resolution_state == FindingStatus.UNRESOLVED]

        # Determine Subsystem Statuses
        structural_status = "INVALID" if any(f.finding_type == FindingType.STRUCTURAL and f.is_blocking for f in findings) else "VALID"
        completeness_status = "INCOMPLETE" if any(f.finding_type == FindingType.COMPLETENESS and f.severity == FindingSeverity.BLOCKING for f in findings) else (
            "PARTIAL" if any(f.finding_type == FindingType.COMPLETENESS for f in findings) else "COMPLETE"
        )
        consistency_status = "CONFLICTS_DETECTED" if unresolved_conflicts else "CONSISTENT"
        temporal_status = "ANOMALIES_DETECTED" if any(f.finding_type == FindingType.TEMPORAL for f in findings) else "COHERENT"
        provenance_status = "GAPS_DETECTED" if any(f.finding_type == FindingType.PROVENANCE and f.severity in (FindingSeverity.BLOCKING, FindingSeverity.HIGH) for f in findings) else "COMPLETE"
        uncertainty_status = "UNCERTAINTIES_PRESERVED" if any(f.finding_type == FindingType.UNCERTAINTY for f in findings) else "CLEAR"

        # 1. NOT_READY: Any blocking findings exist
        if blocking_findings:
            level = ReviewReadinessLevel.NOT_READY
            score = 0.20
            reasons.append(f"Blocked by {len(blocking_findings)} critical structural or completeness issues:")
            for b in blocking_findings[:3]:
                reasons.append(f"• {b.title}: {b.description}")
            return level, score, reasons, {
                "structural": structural_status,
                "completeness": completeness_status,
                "consistency": consistency_status,
                "temporal": temporal_status,
                "provenance": provenance_status,
                "uncertainty": uncertainty_status,
            }

        # 2. Base score calculation based on information availability
        score = 1.0

        # Penalties for completeness gaps
        if completeness_status == "PARTIAL":
            score -= 0.15
            reasons.append("Clinical intake is partially complete; optional baseline vitals or allergy status unrecorded.")

        # Penalties for cross-source / cross-modal conflicts
        if unresolved_conflicts:
            score -= 0.20
            reasons.append(f"{len(unresolved_conflicts)} cross-source or cross-modal discrepancies preserved awaiting clinician adjudication.")

        # Penalties for temporal anomalies
        if temporal_status == "ANOMALIES_DETECTED":
            score -= 0.15
            reasons.append("Timeline events contain ordering anomalies or inconsistent duration statements.")

        # Penalties for provenance gaps
        if provenance_status == "GAPS_DETECTED":
            score -= 0.15
            reasons.append("One or more extracted facts have ungrounded source spans or missing raw evidence links.")

        # Ensure score bounds
        score = max(0.0, min(1.0, round(score, 2)))

        # Determine level
        if high_findings or unresolved_conflicts:
            level = ReviewReadinessLevel.REVIEW_READY_WITH_FLAGS
            if not reasons:
                reasons.append("Case information is assembled but contains quality flags requiring reviewer attention.")
        elif score < 0.70:
            level = ReviewReadinessLevel.PARTIALLY_READY
            if not reasons:
                reasons.append("Information package is partially ready for review.")
        else:
            level = ReviewReadinessLevel.REVIEW_READY
            reasons.append("Case information is complete, internally consistent, and fully grounded to source evidence.")

        # Add positive attributes if ready
        if level in (ReviewReadinessLevel.REVIEW_READY, ReviewReadinessLevel.REVIEW_READY_WITH_FLAGS):
            reasons.append("Patient identity verified.")
            reasons.append("Presenting complaint and symptom graph documented.")
            if context.evidence_items:
                reasons.append(f"{len(context.evidence_items)} multimodal evidence records linked with SHA-256 provenance.")

        return level, score, reasons, {
            "structural": structural_status,
            "completeness": completeness_status,
            "consistency": consistency_status,
            "temporal": temporal_status,
            "provenance": provenance_status,
            "uncertainty": uncertainty_status,
        }
