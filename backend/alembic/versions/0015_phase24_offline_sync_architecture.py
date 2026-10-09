"""0015_phase24_offline_sync_architecture

Revision ID: b84f3782910c
Revises: a48b526171bc
Create Date: 2026-10-09 15:10:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b84f3782910c"
down_revision: Union[str, None] = "a48b526171bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("sync_journals"):
        op.create_table(
            "sync_journals",
            sa.Column("sync_id", sa.String(length=36), primary_key=True),
            sa.Column("node_id", sa.String(length=64), nullable=False),
            sa.Column("entity_type", sa.String(length=64), nullable=False),
            sa.Column("entity_id", sa.String(length=64), nullable=False),
            sa.Column("case_id", sa.String(length=36), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=True),
            sa.Column("operation", sa.String(length=16), nullable=False),
            sa.Column("local_version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("remote_version", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("sync_status", sa.String(length=32), nullable=False, server_default="PENDING_UPLOAD"),
            sa.Column("payload_snapshot", sa.JSON(), nullable=False),
            sa.Column("conflict_strategy", sa.String(length=32), nullable=False, server_default="APPEND_ONLY"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_sync_journals_node_id", "sync_journals", ["node_id"])
        op.create_index("ix_sync_journals_entity_type", "sync_journals", ["entity_type"])
        op.create_index("ix_sync_journals_entity_id", "sync_journals", ["entity_id"])
        op.create_index("ix_sync_journals_case_id", "sync_journals", ["case_id"])
        op.create_index("ix_sync_journals_sync_status", "sync_journals", ["sync_status"])

    if not inspector.has_table("sync_conflicts"):
        op.create_table(
            "sync_conflicts",
            sa.Column("conflict_id", sa.String(length=36), primary_key=True),
            sa.Column("sync_id", sa.String(length=36), sa.ForeignKey("sync_journals.sync_id", ondelete="CASCADE"), nullable=False),
            sa.Column("entity_type", sa.String(length=64), nullable=False),
            sa.Column("entity_id", sa.String(length=64), nullable=False),
            sa.Column("case_id", sa.String(length=36), sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
            sa.Column("local_payload", sa.JSON(), nullable=False),
            sa.Column("remote_payload", sa.JSON(), nullable=False),
            sa.Column("resolution_status", sa.String(length=32), nullable=False, server_default="PENDING_HUMAN_REVIEW"),
            sa.Column("resolved_by_actor_id", sa.String(length=64), nullable=True),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("resolution_notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_sync_conflicts_sync_id", "sync_conflicts", ["sync_id"])
        op.create_index("ix_sync_conflicts_entity_type", "sync_conflicts", ["entity_type"])
        op.create_index("ix_sync_conflicts_entity_id", "sync_conflicts", ["entity_id"])
        op.create_index("ix_sync_conflicts_case_id", "sync_conflicts", ["case_id"])
        op.create_index("ix_sync_conflicts_resolution_status", "sync_conflicts", ["resolution_status"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("sync_conflicts"):
        op.drop_table("sync_conflicts")
    if inspector.has_table("sync_journals"):
        op.drop_table("sync_journals")
