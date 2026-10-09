"""0011_phase14_authentication_rbac

Revision ID: d17e293848ef
Revises: c06d314060ef
Create Date: 2026-10-09 00:20:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d17e293848ef"
down_revision: Union[str, None] = "c06d314060ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("username", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(
            sa.Column("hashed_password", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("patient_id", sa.String(length=36), sa.ForeignKey("patients.id"), nullable=True)
        )
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index(batch_op.f("ix_users_username"), ["username"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_username"))
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("patient_id")
        batch_op.drop_column("hashed_password")
        batch_op.drop_column("username")
