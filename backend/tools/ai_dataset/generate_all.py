"""CLINOVA AI — Generate Synthetic Dataset Files.

Executes generator to populate data/synthetic/ with the 6 canonical splits.
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from backend.tools.ai_dataset.generator import SyntheticDatasetGenerator
from backend.tools.ai_dataset.audit import DataQualityAudit


def main():
    target_dir = repo_root / "data" / "synthetic"
    
    print(f"Generating synthetic datasets in {target_dir}...")
    generator = SyntheticDatasetGenerator(seed=42)
    counts = generator.write_to_directory(target_dir)
    for filename, count in counts.items():
        print(f"  Generated {filename}: {count} records")

    print("\nRunning immediate Data Quality Audit...")
    report = DataQualityAudit.audit_splits(target_dir)
    print(f"Total audited: {report.total_records_audited}")
    print(f"Zero PII: {report.zero_pii_confirmed}")
    print(f"Zero Leakage: {report.zero_leakage_confirmed}")
    print(f"Zero Autonomous Diagnoses: {report.zero_autonomous_diagnoses_confirmed}")
    print(f"Audit Passed: {report.is_audit_passed}")


if __name__ == "__main__":
    main()
