"""0008_phase4_verification_architecture

Revision ID: a84b192848cd
Revises: f82a192837bc
Create Date: 2026-10-06 22:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a84b192848cd"
down_revision: Union[str, None] = "f82a192837bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. verification_runs table
    op.create_table(
        "verification_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=True),
        sa.Column("encounter_id", sa.String(length=36), nullable=True),
        sa.Column("case_snapshot_id", sa.String(length=36), nullable=True),
        sa.Column("case_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("engine_version", sa.String(length=50), nullable=False),
        sa.Column("ruleset_version", sa.String(length=50), nullable=False),
        sa.Column("review_readiness_status", sa.String(length=50), nullable=False),
        sa.Column("review_readiness_score", sa.Float(), nullable=False),
        sa.Column("review_readiness_reasons", sa.JSON(), nullable=False),
        sa.Column("findings_count", sa.Integer(), nullable=False),
        sa.Column("blocking_findings_count", sa.Integer(), nullable=False),
        sa.Column("high_findings_count", sa.Integer(), nullable=False),
        sa.Column("medium_findings_count", sa.Integer(), nullable=False),
        sa.Column("low_findings_count", sa.Integer(), nullable=False),
        sa.Column("info_findings_count", sa.Integer(), nullable=False),
        sa.Column("unresolved_findings_count", sa.Integer(), nullable=False),
        sa.Column("resolved_findings_count", sa.Integer(), nullable=False),
        sa.Column("structural_integrity_status", sa.String(length=50), nullable=False),
        sa.Column("completeness_status", sa.String(length=50), nullable=False),
        sa.Column("consistency_status", sa.String(length=50), nullable=False),
        sa.Column("temporal_status", sa.String(length=50), nullable=False),
        sa.Column("provenance_status", sa.String(length=50), nullable=False),
        sa.Column("uncertainty_status", sa.String(length=50), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["case_snapshot_id"], ["case_snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_verification_runs_case_id"), "verification_runs", ["case_id"], unique=False)
    op.create_index(op.f("ix_verification_runs_patient_id"), "verification_runs", ["patient_id"], unique=False)
    op.create_index("ix_verification_runs_case_ver_composite", "verification_runs", ["case_id", "case_version"], unique=False)
    op.create_index(op.f("ix_verification_runs_case_current"), "verification_runs", ["case_id", "is_current"], unique=False)

    # 2. verification_findings table
    op.create_table(
        "verification_findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("verification_run_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("case_version", sa.Integer(), nullable=False),
        sa.Column("finding_type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_blocking", sa.Boolean(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("expected_information", sa.Text(), nullable=True),
        sa.Column("observed_information", sa.Text(), nullable=True),
        sa.Column("source_evidence_ids", sa.JSON(), nullable=True),
        sa.Column("fact_ids", sa.JSON(), nullable=True),
        sa.Column("timeline_event_ids", sa.JSON(), nullable=True),
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("rule_version", sa.String(length=50), nullable=False),
        sa.Column("resolved_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["verification_run_id"], ["verification_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_verification_findings_run_id"), "verification_findings", ["verification_run_id"], unique=False)
    op.create_index(op.f("ix_verification_findings_case_id"), "verification_findings", ["case_id"], unique=False)
    op.create_index(op.f("ix_verification_findings_case_severity"), "verification_findings", ["case_id", "severity"], unique=False)
    op.create_index(op.f("ix_verification_findings_case_status"), "verification_findings", ["case_id", "status"], unique=False)

    # 3. verification_conflicts table
    op.create_table(
        "verification_conflicts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("verification_run_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("case_version", sa.Integer(), nullable=False),
        sa.Column("conflict_type", sa.String(length=50), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("source_a_evidence_id", sa.String(length=36), nullable=True),
        sa.Column("source_a_type", sa.String(length=50), nullable=True),
        sa.Column("source_a_modality", sa.String(length=50), nullable=True),
        sa.Column("source_a_value", sa.Text(), nullable=False),
        sa.Column("source_a_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_b_evidence_id", sa.String(length=36), nullable=True),
        sa.Column("source_b_type", sa.String(length=50), nullable=True),
        sa.Column("source_b_modality", sa.String(length=50), nullable=True),
        sa.Column("source_b_value", sa.Text(), nullable=False),
        sa.Column("source_b_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_state", sa.String(length=50), nullable=False),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("resolved_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["verification_run_id"], ["verification_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_a_evidence_id"], ["case_evidence.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_b_evidence_id"], ["case_evidence.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_verification_conflicts_run_id"), "verification_conflicts", ["verification_run_id"], unique=False)
    op.create_index(op.f("ix_verification_conflicts_case_id"), "verification_conflicts", ["case_id"], unique=False)
    op.create_index("ix_verification_conflicts_case_field", "verification_conflicts", ["case_id", "field_name"], unique=False)
    op.create_index("ix_verification_conflicts_state", "verification_conflicts", ["case_id", "resolution_state"], unique=False)


def downgrade() -> None:
    op.drop_table("verification_conflicts")
    op.drop_table("verification_findings")
    op.drop_table("verification_runs")
