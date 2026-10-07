"""0009_phase5_intelligent_completion_architecture

Revision ID: b95c203959de
Revises: a84b192848cd
Create Date: 2026-10-06 23:30:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b95c203959de"
down_revision: Union[str, None] = "a84b192848cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. completion_sessions table
    op.create_table(
        "completion_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=True),
        sa.Column("encounter_id", sa.String(length=36), nullable=True),
        sa.Column("initial_verification_run_id", sa.String(length=36), nullable=True),
        sa.Column("latest_verification_run_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("case_version_started", sa.Integer(), nullable=False),
        sa.Column("case_version_current", sa.Integer(), nullable=False),
        sa.Column("current_turn", sa.Integer(), nullable=False),
        sa.Column("max_turns", sa.Integer(), nullable=False),
        sa.Column("questions_asked_count", sa.Integer(), nullable=False),
        sa.Column("questions_answered_count", sa.Integer(), nullable=False),
        sa.Column("questions_skipped_count", sa.Integer(), nullable=False),
        sa.Column("initial_gap_count", sa.Integer(), nullable=False),
        sa.Column("remaining_gap_count", sa.Integer(), nullable=False),
        sa.Column("initial_readiness_score", sa.Float(), nullable=False),
        sa.Column("current_readiness_score", sa.Float(), nullable=False),
        sa.Column("stopping_reason", sa.Text(), nullable=True),
        sa.Column("stopping_criterion", sa.String(length=50), nullable=True),
        sa.Column("completion_summary", sa.JSON(), nullable=True),
        sa.Column("engine_version", sa.String(length=50), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["initial_verification_run_id"], ["verification_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["latest_verification_run_id"], ["verification_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_completion_sessions_case_id"), "completion_sessions", ["case_id"], unique=False)
    op.create_index(op.f("ix_completion_sessions_patient_id"), "completion_sessions", ["patient_id"], unique=False)
    op.create_index(op.f("ix_completion_sessions_status"), "completion_sessions", ["status"], unique=False)
    op.create_index(op.f("ix_completion_sessions_is_current"), "completion_sessions", ["is_current"], unique=False)
    op.create_index("ix_completion_sessions_case_status", "completion_sessions", ["case_id", "status"], unique=False)
    op.create_index("ix_completion_sessions_case_current", "completion_sessions", ["case_id", "is_current"], unique=False)

    # 2. completion_questions table
    op.create_table(
        "completion_questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("target_gap_id", sa.String(length=100), nullable=True),
        sa.Column("target_gap_type", sa.String(length=50), nullable=False),
        sa.Column("target_field", sa.String(length=100), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("placeholder", sa.String(length=255), nullable=True),
        sa.Column("priority_score", sa.Float(), nullable=False),
        sa.Column("clinical_rationale", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_safety_flag", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("presented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["completion_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_completion_questions_session_id"), "completion_questions", ["session_id"], unique=False)
    op.create_index(op.f("ix_completion_questions_case_id"), "completion_questions", ["case_id"], unique=False)
    op.create_index(op.f("ix_completion_questions_target_field"), "completion_questions", ["target_field"], unique=False)
    op.create_index(op.f("ix_completion_questions_status"), "completion_questions", ["status"], unique=False)
    op.create_index("ix_completion_questions_session_turn", "completion_questions", ["session_id", "turn_number"], unique=False)
    op.create_index("ix_completion_questions_target_field_case", "completion_questions", ["case_id", "target_field"], unique=False)

    # 3. completion_answers table
    op.create_table(
        "completion_answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=True),
        sa.Column("raw_answer_text", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=True),
        sa.Column("structured_payload", sa.JSON(), nullable=True),
        sa.Column("answer_modality", sa.String(length=50), nullable=False),
        sa.Column("is_skipped", sa.Boolean(), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("validation_notes", sa.Text(), nullable=True),
        sa.Column("evidence_id", sa.String(length=36), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["completion_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["completion_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["triage_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["evidence_id"], ["case_evidence.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id"),
    )
    op.create_index(op.f("ix_completion_answers_question_id"), "completion_answers", ["question_id"], unique=True)
    op.create_index(op.f("ix_completion_answers_session_id"), "completion_answers", ["session_id"], unique=False)
    op.create_index(op.f("ix_completion_answers_case_id"), "completion_answers", ["case_id"], unique=False)
    op.create_index(op.f("ix_completion_answers_patient_id"), "completion_answers", ["patient_id"], unique=False)
    op.create_index(op.f("ix_completion_answers_evidence_id"), "completion_answers", ["evidence_id"], unique=False)
    op.create_index("ix_completion_answers_case_question", "completion_answers", ["case_id", "question_id"], unique=False)


def downgrade() -> None:
    op.drop_table("completion_answers")
    op.drop_table("completion_questions")
    op.drop_table("completion_sessions")
