"""CLINOVA AI — Deterministic AI Output Validator.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Deterministic gatekeeper evaluating all LLM outputs before application consumption.
Enforces:
1. JSON Schema Conformity
2. Physiological Range Validity
3. Anti-Hallucination Grounding (Evidence Pointer Verification)
4. Absolute Prohibition of Autonomous Clinical Decisions (Prescriptions, Admissions, Discharges)
5. Non-Diagnostic Epistemic State Invariants
"""

import json
import re
from typing import Dict, Any, List, Optional, Set, Type
from pydantic import BaseModel, ValidationError
from app.ai_runtime.models import ValidationStatus


# Physiological ranges for vital sign validation
PHYSIOLOGICAL_RANGES = {
    "HR": (20.0, 300.0),      # bpm
    "SBP": (30.0, 300.0),     # mmHg
    "DBP": (20.0, 200.0),     # mmHg
    "RR": (4.0, 80.0),        # breaths/min
    "SPO2": (30.0, 100.0),    # %
    "TEMP_C": (25.0, 45.0),   # Celsius
    "TEMP_F": (77.0, 113.0),  # Fahrenheit
}

# Forbidden action triggers in generated output
FORBIDDEN_ACTION_PATTERNS = [
    (r"(?i)\b(prescribe|rx|dosage\s*:\s*\d|take\s+\d+\s*mg|tablet\s+daily|auto\s*prescribe)\b", "FORBIDDEN_PRESCRIPTION"),
    (r"(?i)\b(admit\s+to\s+ward|admit\s+to\s+icu|order\s+admission|auto\s*admit)\b", "FORBIDDEN_ADMISSION"),
    (r"(?i)\b(discharge\s+patient|patient\s+is\s+discharged|auto\s*discharge)\b", "FORBIDDEN_DISCHARGE"),
    (r"(?i)\b(authorize\s+surgery|schedule\s+emergency\s+or|authorize\s+procedure|procedure\s+authorized)\b", "FORBIDDEN_PROCEDURE_AUTHORIZATION"),
    (r"(?i)\b(status\s*:\s*verified|mark\s+as\s+verified|mark\s+as\s+clinician\s+verified)\b", "FORBIDDEN_SELF_VERIFICATION"),
    (r"(?i)\b(override\s+doctor|ignore\s+clinician)\b", "FORBIDDEN_CLINICIAN_OVERRIDE"),
    (r"(?i)\b(definitive\s+diagnosis\s*:\s*confirmed|definitive\s+diagnosis|confirmed\s+diagnosis|ai\s+diagnose)\b", "FORBIDDEN_AUTONOMOUS_DIAGNOSIS"),
    (r"(?i)\b(close\s+case\s+automatically|auto\s*close\s*case)\b", "FORBIDDEN_CASE_CLOSURE"),
]


class ValidationResult(BaseModel):
    """Deterministic validation evaluation result."""
    is_valid: bool
    status: ValidationStatus
    errors: List[str] = []
    warnings: List[str] = []
    validated_payload: Optional[Dict[str, Any]] = None


class OutputValidator:
    """Rigorous fail-closed validator for AI outputs."""

    @classmethod
    def validate_raw_json(cls, raw_text: str) -> Tuple_Parsing:
        """Attempts to parse raw output into a JSON dictionary, stripping markdown fences if present."""
        cleaned = raw_text.strip()
        # Strip markdown fences if LLM wrapped output
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                return False, {}, "Parsed JSON is not an object/dictionary"
            return True, parsed, ""
        except json.JSONDecodeError as exc:
            return False, {}, f"Malformed JSON: {str(exc)}"

    @classmethod
    def check_forbidden_clinical_actions(cls, payload: Dict[str, Any]) -> List[str]:
        """Scans payload values recursively for prohibited clinical actions."""
        violations: List[str] = []
        payload_str = json.dumps(payload)

        for pattern, violation_code in FORBIDDEN_ACTION_PATTERNS:
            if re.search(pattern, payload_str):
                violations.append(f"{violation_code}: Matched prohibited pattern '{pattern}'")

        return violations

    @classmethod
    def check_grounding_references(
        cls, payload: Dict[str, Any], allowed_evidence_ids: Set[str]
    ) -> List[str]:
        """Ensures that all cited source_evidence_ids genuinely exist in the input context."""
        violations: List[str] = []
        reference_keys = (
            "source_evidence_id",
            "source_evidence_ids",
            "supporting_evidence_ids",
            "target_evidence_id",
            "evidence_reference",
            "evidence_id",
        )

        def recurse_find_ids(data: Any):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k in reference_keys:
                        if isinstance(v, str) and v.strip():
                            if v not in allowed_evidence_ids:
                                violations.append(f"UNGROUNDED_EVIDENCE_CITATION: Cited '{v}' not in context")
                        elif isinstance(v, list):
                            for item in v:
                                if isinstance(item, str) and item.strip() and item not in allowed_evidence_ids:
                                    violations.append(f"UNGROUNDED_EVIDENCE_CITATION: Cited '{item}' not in context")
                    else:
                        recurse_find_ids(v)
            elif isinstance(data, list):
                for item in data:
                    recurse_find_ids(item)

        recurse_find_ids(payload)
        return violations

    @classmethod
    def check_vital_ranges(cls, payload: Dict[str, Any]) -> List[str]:
        """Validates that extracted vitals fall within plausible human physiological boundaries."""
        violations: List[str] = []
        vital_mentions = payload.get("vital_mentions", [])
        if isinstance(vital_mentions, list):
            for vital in vital_mentions:
                if isinstance(vital, dict):
                    param = str(vital.get("parameter", "")).upper()
                    val = vital.get("value")
                    if isinstance(val, (int, float)):
                        if param in PHYSIOLOGICAL_RANGES:
                            low, high = PHYSIOLOGICAL_RANGES[param]
                            if not (low <= float(val) <= high):
                                violations.append(
                                    f"IMPOSSIBLE_PHYSIOLOGICAL_VALUE: {param}={val} outside human limits [{low}, {high}]"
                                )
                        elif param in ("TEMP", "TEMPERATURE"):
                            unit = str(vital.get("unit", "")).upper()
                            if "F" in unit:
                                low, high = PHYSIOLOGICAL_RANGES["TEMP_F"]
                            else:
                                low, high = PHYSIOLOGICAL_RANGES["TEMP_C"]
                            if not (low <= float(val) <= high):
                                violations.append(
                                    f"IMPOSSIBLE_PHYSIOLOGICAL_VALUE: Temperature={val} outside limits [{low}, {high}]"
                                )
        return violations

    @classmethod
    def validate(
        cls,
        raw_output: str,
        target_schema: Type[BaseModel],
        allowed_evidence_ids: Optional[Set[str]] = None,
    ) -> ValidationResult:
        """Executes full fail-closed deterministic validation pipeline."""
        # 1. Parse JSON
        is_json, parsed_dict, json_err = cls.validate_raw_json(raw_output)
        if not is_json:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.REJECTED_MALFORMED,
                errors=[json_err],
            )

        # 2. Check Forbidden Clinical Actions
        forbidden_violations = cls.check_forbidden_clinical_actions(parsed_dict)
        if forbidden_violations:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.REJECTED_FORBIDDEN_ACTION,
                errors=forbidden_violations,
                validated_payload=parsed_dict,
            )

        # 3. Check Physiological Boundaries
        range_violations = cls.check_vital_ranges(parsed_dict)
        if range_violations:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.REJECTED_OUT_OF_BOUNDS,
                errors=range_violations,
                validated_payload=parsed_dict,
            )

        # 4. Check Grounding (Evidence Linkage)
        if allowed_evidence_ids is not None:
            grounding_violations = cls.check_grounding_references(parsed_dict, allowed_evidence_ids)
            if grounding_violations:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.REJECTED_UNGROUNDED,
                    errors=grounding_violations,
                    validated_payload=parsed_dict,
                )

        # 5. Pydantic Schema Validation
        try:
            validated_obj = target_schema.model_validate(parsed_dict)
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.VALID,
                errors=[],
                validated_payload=validated_obj.model_dump(),
            )
        except ValidationError as val_err:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.REJECTED_SCHEMA,
                errors=[f"Schema error: {err['loc']} - {err['msg']}" for err in val_err.errors()],
                validated_payload=parsed_dict,
            )


Tuple_Parsing = tuple[bool, Dict[str, Any], str]
