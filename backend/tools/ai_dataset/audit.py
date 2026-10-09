"""CLINOVA AI — Synthetic Dataset Quality Audit Tool.

Phase 11: AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation.
Performs rigorous programmatic quality, leakage, schema, and zero-PII audits
across all synthetic dataset splits.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
from pydantic import BaseModel, Field
from backend.tools.ai_dataset.schema import (
    SyntheticCaseRecord,
    PII_PHONE_REGEX,
    PII_AADHAAR_REGEX,
    PII_EMAIL_REGEX,
)


class DataQualityIssue(BaseModel):
    """Specific flaw detected in dataset record or split."""
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    category: str = Field(..., description="LEAKAGE, PII, SCHEMA, PHYSIOLOGY, CONTRADICTION, AUTONOMOUS_DIAGNOSIS")
    case_id: str
    message: str


class DataQualityReport(BaseModel):
    """Comprehensive dataset quality audit report."""
    total_records_audited: int
    split_record_counts: Dict[str, int]
    is_audit_passed: bool
    critical_issues_count: int
    high_issues_count: int
    medium_issues_count: int
    zero_pii_confirmed: bool
    zero_leakage_confirmed: bool
    zero_autonomous_diagnoses_confirmed: bool
    issues: List[DataQualityIssue] = []


class DataQualityAudit:
    """Rigorous programmatic audit suite for CLINOVA AI datasets."""

    @classmethod
    def audit_splits(cls, dataset_dir: Path) -> DataQualityReport:
        """Audits all JSONL files in the dataset directory."""
        issues: List[DataQualityIssue] = []
        split_counts: Dict[str, int] = {}
        total_records = 0

        # Mapping of case_id -> split_name to detect inter-split leakage
        seen_case_ids: Dict[str, str] = {}
        seen_narratives: Dict[str, str] = {}

        split_files = list(dataset_dir.glob("*.jsonl"))
        if not split_files:
            return DataQualityReport(
                total_records_audited=0,
                split_record_counts={},
                is_audit_passed=False,
                critical_issues_count=1,
                high_issues_count=0,
                medium_issues_count=0,
                zero_pii_confirmed=False,
                zero_leakage_confirmed=False,
                zero_autonomous_diagnoses_confirmed=False,
                issues=[DataQualityIssue(severity="CRITICAL", category="SCHEMA", case_id="GLOBAL", message="No .jsonl dataset files found in directory.")],
            )

        for split_file in split_files:
            split_name = split_file.stem
            records_in_split = 0

            with open(split_file, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    records_in_split += 1
                    total_records += 1

                    # 1. JSON Parsing Check
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as exc:
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="SCHEMA",
                            case_id=f"{split_name}-L{line_idx}",
                            message=f"Malformed JSON: {str(exc)}",
                        ))
                        continue

                    case_id = data.get("case_id", f"UNKNOWN-L{line_idx}")

                    # 2. Canonical Schema Validation
                    try:
                        record = SyntheticCaseRecord(**data)
                    except Exception as exc:
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="SCHEMA",
                            case_id=case_id,
                            message=f"Pydantic schema validation failure: {str(exc)}",
                        ))
                        continue

                    # 3. Data Leakage Check
                    if record.case_id in seen_case_ids:
                        prior_split = seen_case_ids[record.case_id]
                        if prior_split != split_name:
                            issues.append(DataQualityIssue(
                                severity="CRITICAL",
                                category="LEAKAGE",
                                case_id=record.case_id,
                                message=f"Data leakage detected! case_id '{record.case_id}' appears in both '{prior_split}' and '{split_name}'.",
                            ))
                    else:
                        seen_case_ids[record.case_id] = split_name

                    # 4. Strict Zero-PII Regex Audit
                    raw_text = record.source_text
                    if PII_PHONE_REGEX.search(raw_text):
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="PII",
                            case_id=record.case_id,
                            message="Realistic Indian phone number pattern detected in source_text.",
                        ))
                    if PII_AADHAAR_REGEX.search(raw_text):
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="PII",
                            case_id=record.case_id,
                            message="Realistic 12-digit Aadhaar pattern detected in source_text.",
                        ))
                    if PII_EMAIL_REGEX.search(raw_text):
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="PII",
                            case_id=record.case_id,
                            message="Email address detected in source_text.",
                        ))

                    # 5. Autonomous Diagnosis Prohibition in Gold Output
                    gold_dump = json.dumps(record.gold_output).lower()
                    if "definitive diagnosis" in gold_dump or "confirmed diagnosis:" in gold_dump:
                        issues.append(DataQualityIssue(
                            severity="CRITICAL",
                            category="AUTONOMOUS_DIAGNOSIS",
                            case_id=record.case_id,
                            message="Forbidden autonomous diagnosis language found in gold_output.",
                        ))

                    # 6. Physiological Range Check on Structured Truth
                    vitals = record.structured_truth.get("vitals", [])
                    if isinstance(vitals, list):
                        for vital in vitals:
                            if isinstance(vital, dict):
                                param = str(vital.get("parameter", "")).upper()
                                val = vital.get("value")
                                if isinstance(val, (int, float)):
                                    if param == "HR" and not (20 <= val <= 250):
                                        issues.append(DataQualityIssue(
                                            severity="HIGH",
                                            category="PHYSIOLOGY",
                                            case_id=record.case_id,
                                            message=f"Physiologically implausible HR: {val}",
                                        ))
                                    elif param == "TEMP" and not (25 <= val <= 45):
                                        issues.append(DataQualityIssue(
                                            severity="HIGH",
                                            category="PHYSIOLOGY",
                                            case_id=record.case_id,
                                            message=f"Physiologically implausible Celsius Temp: {val}",
                                        ))

            split_counts[split_name] = records_in_split

        critical_count = sum(1 for i in issues if i.severity == "CRITICAL")
        high_count = sum(1 for i in issues if i.severity == "HIGH")
        medium_count = sum(1 for i in issues if i.severity == "MEDIUM")

        zero_pii = not any(i.category == "PII" for i in issues)
        zero_leakage = not any(i.category == "LEAKAGE" for i in issues)
        zero_auto_diag = not any(i.category == "AUTONOMOUS_DIAGNOSIS" for i in issues)

        is_passed = (critical_count == 0 and high_count == 0)

        return DataQualityReport(
            total_records_audited=total_records,
            split_record_counts=split_counts,
            is_audit_passed=is_passed,
            critical_issues_count=critical_count,
            high_issues_count=high_count,
            medium_issues_count=medium_count,
            zero_pii_confirmed=zero_pii,
            zero_leakage_confirmed=zero_leakage,
            zero_autonomous_diagnoses_confirmed=zero_auto_diag,
            issues=issues,
        )
