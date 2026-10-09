"""0012_phase18_ai_results_architecture

Revision ID: e28f304959fa
Revises: d17e293848ef
Create Date: 2026-10-09 04:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e28f304959fa"
down_revision: Union[str, None] = "d17e293848ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("cases.id"), nullable=False, index=True),
        sa.Column("task_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("task_version", sa.String(length=32), nullable=False, default="1.0.0"),
        sa.Column("model_id", sa.String(length=64), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("prompt_id", sa.String(length=64), nullable=False),
        sa.Column("prompt_version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, default="SUCCESS"),
        sa.Column("validation_state", sa.String(length=32), nullable=False, default="VALID"),
        sa.Column("epistemic_state", sa.String(length=32), nullable=False, default="AI_INFERRED"),
        sa.Column("is_stale", sa.Boolean(), nullable=False, default=False),
        sa.Column("context_fingerprint", sa.String(length=64), nullable=False, index=True),
        sa.Column("case_version", sa.Integer(), nullable=False, default=1),
        sa.Column("source_evidence_references", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_results")
