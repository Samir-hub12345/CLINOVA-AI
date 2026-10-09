"""0014_phase23_case_outcome_architecture

Revision ID: a48b526171bc
Revises: f39a415060ab
Create Date: 2026-10-09 14:40:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a48b526171bc"
down_revision: Union[str, None] = "f39a415060ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    has_table = inspector.has_table("case_outcomes")

    if not has_table:
        op.create_table(
            "case_outcomes",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("case_id", sa.String(length=36), sa.ForeignKey("cases.id"), unique=True, nullable=False),
            sa.Column("disposition", sa.String(length=64), nullable=False),
            sa.Column("final_condition", sa.String(length=64), nullable=False, server_default="STABLE"),
            sa.Column("actual_action", sa.String(length=64), nullable=True, server_default="UNKNOWN"),
            sa.Column("recommendation", sa.String(length=64), nullable=True),
            sa.Column("professional_decision", sa.String(length=64), nullable=True),
            sa.Column("outcome_status", sa.String(length=64), nullable=True, server_default="UNKNOWN"),
            sa.Column("recorded_by", sa.String(length=36), nullable=True),
            sa.Column("actor_role", sa.String(length=32), nullable=True),
            sa.Column("is_corrected", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        )
    else:
        existing_cols = {col["name"] for col in inspector.get_columns("case_outcomes")}
        with op.batch_alter_table("case_outcomes") as batch_op:
            if "actual_action" not in existing_cols:
                batch_op.add_column(
                    sa.Column("actual_action", sa.String(length=64), nullable=True, server_default="UNKNOWN")
                )
            if "recommendation" not in existing_cols:
                batch_op.add_column(
                    sa.Column("recommendation", sa.String(length=64), nullable=True)
                )
            if "professional_decision" not in existing_cols:
                batch_op.add_column(
                    sa.Column("professional_decision", sa.String(length=64), nullable=True)
                )
            if "outcome_status" not in existing_cols:
                batch_op.add_column(
                    sa.Column("outcome_status", sa.String(length=64), nullable=True, server_default="UNKNOWN")
                )
            if "recorded_by" not in existing_cols:
                batch_op.add_column(
                    sa.Column("recorded_by", sa.String(length=36), nullable=True)
                )
            if "actor_role" not in existing_cols:
                batch_op.add_column(
                    sa.Column("actor_role", sa.String(length=32), nullable=True)
                )
            if "is_corrected" not in existing_cols:
                batch_op.add_column(
                    sa.Column("is_corrected", sa.Boolean(), nullable=False, server_default=sa.false())
                )
            if "version" not in existing_cols:
                batch_op.add_column(
                    sa.Column("version", sa.Integer(), nullable=False, server_default="1")
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("case_outcomes"):
        existing_cols = {col["name"] for col in inspector.get_columns("case_outcomes")}
        with op.batch_alter_table("case_outcomes") as batch_op:
            for col_name in [
                "version",
                "is_corrected",
                "actor_role",
                "recorded_by",
                "outcome_status",
                "professional_decision",
                "recommendation",
                "actual_action",
            ]:
                if col_name in existing_cols:
                    batch_op.drop_column(col_name)
