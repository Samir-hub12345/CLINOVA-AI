"""0005 multimodal processing records architecture

Revision ID: d6f920145be1
Revises: c5f8190342ab
Create Date: 2026-10-06 19:18:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d6f920145be1"
down_revision = "c5f8190342ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "multimodal_processing_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("capability", sa.String(length=50), nullable=False),
        sa.Column("modality", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
        sa.Column("source_reference", sa.String(length=255), nullable=True),
        sa.Column("output_evidence_id", sa.String(length=36), sa.ForeignKey("case_evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_processing_records_case_id", "multimodal_processing_records", ["case_id"])
    op.create_index("ix_processing_records_capability", "multimodal_processing_records", ["capability"])
    op.create_index("ix_processing_records_provider_name", "multimodal_processing_records", ["provider_name"])
    op.create_index("ix_processing_records_status", "multimodal_processing_records", ["status"])
    op.create_index("ix_processing_records_case_capability", "multimodal_processing_records", ["case_id", "capability"])


def downgrade() -> None:
    op.drop_index("ix_processing_records_case_capability", table_name="multimodal_processing_records")
    op.drop_index("ix_processing_records_status", table_name="multimodal_processing_records")
    op.drop_index("ix_processing_records_provider_name", table_name="multimodal_processing_records")
    op.drop_index("ix_processing_records_capability", table_name="multimodal_processing_records")
    op.drop_index("ix_processing_records_case_id", table_name="multimodal_processing_records")
    op.drop_table("multimodal_processing_records")
