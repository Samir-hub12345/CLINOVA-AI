"""0007_canonical_case_builder_architecture

Revision ID: f82a192837bc
Revises: e71b2938472a
Create Date: 2026-10-06 21:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f82a192837bc"
down_revision: Union[str, None] = "e71b2938472a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. case_build_runs table
    op.create_table(
        "case_build_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("trigger_type", sa.String(length=50), nullable=False),
        sa.Column("input_evidence_count", sa.Integer(), nullable=False),
        sa.Column("facts_extracted_count", sa.Integer(), nullable=False),
        sa.Column("facts_rejected_count", sa.Integer(), nullable=False),
        sa.Column("target_case_version", sa.Integer(), nullable=False),
        sa.Column("build_logic_version", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_case_build_runs_case_id"), "case_build_runs", ["case_id"], unique=False)
    op.create_index(op.f("ix_case_build_runs_status"), "case_build_runs", ["status"], unique=False)
    op.create_index(op.f("ix_case_build_runs_started_at"), "case_build_runs", ["started_at"], unique=False)
    op.create_index("ix_case_build_runs_case_status", "case_build_runs", ["case_id", "status"], unique=False)

    # 2. case_snapshots table
    op.create_table(
        "case_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("build_run_id", sa.String(length=36), nullable=True),
        sa.Column("case_version", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("build_version", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("case_data", sa.JSON(), nullable=False),
        sa.Column("delta_summary", sa.JSON(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["build_run_id"], ["case_build_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_case_snapshots_case_id"), "case_snapshots", ["case_id"], unique=False)
    op.create_index(op.f("ix_case_snapshots_build_run_id"), "case_snapshots", ["build_run_id"], unique=False)
    op.create_index(op.f("ix_case_snapshots_is_current"), "case_snapshots", ["is_current"], unique=False)
    op.create_index(op.f("ix_case_snapshots_created_at"), "case_snapshots", ["created_at"], unique=False)
    op.create_index("ix_case_snapshots_case_version", "case_snapshots", ["case_id", "case_version"], unique=True)
    op.create_index("ix_case_snapshots_case_current", "case_snapshots", ["case_id", "is_current"], unique=False)

    # 3. canonical_facts table
    op.create_table(
        "canonical_facts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("concept", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("polarity", sa.String(length=20), nullable=False),
        sa.Column("certainty", sa.String(length=20), nullable=False),
        sa.Column("attribution", sa.String(length=50), nullable=False),
        sa.Column("temporal_status", sa.String(length=20), nullable=False),
        sa.Column("duration", sa.String(length=100), nullable=True),
        sa.Column("onset_approximate", sa.String(length=100), nullable=True),
        sa.Column("source_evidence_id", sa.String(length=36), nullable=True),
        sa.Column("source_span", sa.Text(), nullable=True),
        sa.Column("supporting_evidence_ids", sa.JSON(), nullable=True),
        sa.Column("has_conflict", sa.Boolean(), nullable=False),
        sa.Column("conflicting_value", sa.Text(), nullable=True),
        sa.Column("conflicting_source_id", sa.String(length=36), nullable=True),
        sa.Column("verification_state", sa.String(length=50), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["case_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_evidence_id"], ["case_evidence.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_canonical_facts_case_id"), "canonical_facts", ["case_id"], unique=False)
    op.create_index(op.f("ix_canonical_facts_snapshot_id"), "canonical_facts", ["snapshot_id"], unique=False)
    op.create_index(op.f("ix_canonical_facts_category"), "canonical_facts", ["category"], unique=False)
    op.create_index(op.f("ix_canonical_facts_concept"), "canonical_facts", ["concept"], unique=False)
    op.create_index(op.f("ix_canonical_facts_source_evidence_id"), "canonical_facts", ["source_evidence_id"], unique=False)
    op.create_index(op.f("ix_canonical_facts_created_at"), "canonical_facts", ["created_at"], unique=False)
    op.create_index("ix_canonical_facts_case_category", "canonical_facts", ["case_id", "category"], unique=False)
    op.create_index("ix_canonical_facts_snapshot_concept", "canonical_facts", ["snapshot_id", "concept"], unique=False)

    # 4. timeline_events table
    op.create_table(
        "timeline_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("relative_time", sa.String(length=100), nullable=True),
        sa.Column("approximate_date", sa.String(length=50), nullable=True),
        sa.Column("temporal_status", sa.String(length=20), nullable=False),
        sa.Column("source_evidence_id", sa.String(length=36), nullable=True),
        sa.Column("attribution", sa.String(length=50), nullable=False),
        sa.Column("certainty", sa.String(length=20), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["case_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_evidence_id"], ["case_evidence.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timeline_events_case_id"), "timeline_events", ["case_id"], unique=False)
    op.create_index(op.f("ix_timeline_events_snapshot_id"), "timeline_events", ["snapshot_id"], unique=False)
    op.create_index(op.f("ix_timeline_events_event_type"), "timeline_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_timeline_events_source_evidence_id"), "timeline_events", ["source_evidence_id"], unique=False)
    op.create_index("ix_timeline_events_case_order", "timeline_events", ["case_id", "order_index"], unique=False)


def downgrade() -> None:
    op.drop_table("timeline_events")
    op.drop_table("canonical_facts")
    op.drop_table("case_snapshots")
    op.drop_table("case_build_runs")
