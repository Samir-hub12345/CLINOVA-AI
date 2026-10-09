"""0010_phase13_core_backend_foundation

Revision ID: c06d314060ef
Revises: b95c203959de
Create Date: 2026-10-08 23:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c06d314060ef"
down_revision: Union[str, None] = "b95c203959de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Alter existing tables for Phase 13 requirements
    # 0a. facilities
    with op.batch_alter_table("facilities") as batch_op:
        batch_op.add_column(
            sa.Column("operational_status", sa.String(length=32), nullable=False, server_default="OPERATIONAL")
        )
        batch_op.add_column(
            sa.Column("capabilities_profile", sa.JSON(), nullable=True)
        )

    # 0b. patients
    with op.batch_alter_table("patients") as batch_op:
        batch_op.add_column(
            sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true())
        )
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)
        )

    # 0c. consents
    with op.batch_alter_table("consents") as batch_op:
        batch_op.add_column(
            sa.Column("purpose", sa.String(length=64), nullable=False, server_default="CLINICAL_CARE_TRIAGE")
        )
        batch_op.add_column(
            sa.Column("channel", sa.String(length=32), nullable=False, server_default="DIGITAL_APP")
        )
        batch_op.add_column(
            sa.Column("consent_version", sa.String(length=16), nullable=False, server_default="v1.0")
        )
        batch_op.add_column(
            sa.Column("status", sa.String(length=32), nullable=False, server_default="GRANTED")
        )
        batch_op.add_column(
            sa.Column("hash_reference", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)
        )

    # 1. patient_identifiers
    op.create_table(
        "patient_identifiers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("identifier_type", sa.String(length=32), nullable=False),
        sa.Column("identifier_value", sa.String(length=64), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patient_identifiers_patient_id"), "patient_identifiers", ["patient_id"], unique=False)
    op.create_index(op.f("ix_patient_identifiers_identifier_value"), "patient_identifiers", ["identifier_value"], unique=False)

    # 2. encounters
    op.create_table(
        "encounters",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("facility_id", sa.String(length=36), nullable=False),
        sa.Column("environment", sa.String(length=32), nullable=False, server_default="development"),
        sa.Column("pathway", sa.String(length=64), nullable=False, server_default="REGULAR_STANDARD"),
        sa.Column("source_actor_id", sa.String(length=64), nullable=True),
        sa.Column("source_actor_role", sa.String(length=32), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_encounters_patient_id"), "encounters", ["patient_id"], unique=False)
    op.create_index(op.f("ix_encounters_facility_id"), "encounters", ["facility_id"], unique=False)

    # 3. Canonical Master Case root table: cases
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_number", sa.String(length=32), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("encounter_id", sa.String(length=36), nullable=True),
        sa.Column("facility_id", sa.String(length=36), nullable=False),
        sa.Column("pathway", sa.String(length=64), nullable=False, server_default="REGULAR_STANDARD"),
        sa.Column("current_state", sa.String(length=64), nullable=False, server_default="INTAKE_RECORDED"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="NEW"),
        sa.Column("acuity_tier", sa.String(length=16), nullable=False, server_default="ROUTINE"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("trajectory_slope", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("uncertainty_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("state_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("environment_id", sa.String(length=32), nullable=False, server_default="development"),
        sa.Column("presenting_complaint", sa.Text(), nullable=False, server_default=""),
        sa.Column("primary_syndrome", sa.String(length=64), nullable=True),
        sa.Column("required_bundle", sa.String(length=64), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closure_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_number"),
    )
    op.create_index(op.f("ix_cases_case_number"), "cases", ["case_number"], unique=True)
    op.create_index(op.f("ix_cases_patient_id"), "cases", ["patient_id"], unique=False)
    op.create_index(op.f("ix_cases_encounter_id"), "cases", ["encounter_id"], unique=False)
    op.create_index(op.f("ix_cases_facility_id"), "cases", ["facility_id"], unique=False)
    op.create_index(op.f("ix_cases_current_state"), "cases", ["current_state"], unique=False)
    op.create_index(op.f("ix_cases_status"), "cases", ["status"], unique=False)

    # 4. case_state_transitions
    op.create_table(
        "case_state_transitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("from_state", sa.String(length=64), nullable=False),
        sa.Column("to_state", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("actor_role", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("state_version", sa.Integer(), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("transition_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_case_state_transitions_case_id"), "case_state_transitions", ["case_id"], unique=False)

    # 5. evidence
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("source_class", sa.String(length=32), nullable=False),
        sa.Column("epistemic_state", sa.String(length=32), nullable=False, server_default="INFERRED"),
        sa.Column("parameter_name", sa.String(length=128), nullable=False),
        sa.Column("content_value", sa.JSON(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provenance_metadata", sa.JSON(), nullable=True),
        sa.Column("verification_metadata", sa.JSON(), nullable=True),
        sa.Column("transformation_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_case_id"), "evidence", ["case_id"], unique=False)
    op.create_index(op.f("ix_evidence_source_class"), "evidence", ["source_class"], unique=False)
    op.create_index(op.f("ix_evidence_epistemic_state"), "evidence", ["epistemic_state"], unique=False)
    op.create_index(op.f("ix_evidence_parameter_name"), "evidence", ["parameter_name"], unique=False)

    # 6. vitals
    op.create_table(
        "vitals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("heart_rate", sa.Integer(), nullable=True),
        sa.Column("systolic_bp", sa.Integer(), nullable=True),
        sa.Column("diastolic_bp", sa.Integer(), nullable=True),
        sa.Column("spo2_percent", sa.Integer(), nullable=True),
        sa.Column("respiratory_rate", sa.Integer(), nullable=True),
        sa.Column("temperature_celsius", sa.Float(), nullable=True),
        sa.Column("avpu_score", sa.String(length=16), nullable=True, server_default="ALERT"),
        sa.Column("supplemental_o2", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="STAFF_ENTERED"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provenance_metadata", sa.JSON(), nullable=True),
        sa.Column("verification_context", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vitals_case_id"), "vitals", ["case_id"], unique=False)

    # 7. timeline_events
    op.create_table(
        "timeline_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_title", sa.String(length=128), nullable=False),
        sa.Column("event_content", sa.Text(), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actor_id", sa.String(length=64), nullable=True),
        sa.Column("actor_role", sa.String(length=32), nullable=True),
        sa.Column("evidence_id", sa.String(length=36), nullable=True),
        sa.Column("is_conflict", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provenance_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timeline_events_case_id"), "timeline_events", ["case_id"], unique=False)
    op.create_index(op.f("ix_timeline_events_event_type"), "timeline_events", ["event_type"], unique=False)

    # 8. follow_up_questions
    op.create_table(
        "follow_up_questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="IMPORTANT"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_follow_up_questions_case_id"), "follow_up_questions", ["case_id"], unique=False)

    # 9. follow_up_answers
    op.create_table(
        "follow_up_answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("answered_by", sa.String(length=64), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["question_id"], ["follow_up_questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_follow_up_answers_case_id"), "follow_up_answers", ["case_id"], unique=False)
    op.create_index(op.f("ix_follow_up_answers_question_id"), "follow_up_answers", ["question_id"], unique=False)

    # 10. triage_notes
    op.create_table(
        "triage_notes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=64), nullable=False),
        sa.Column("author_role", sa.String(length=32), nullable=False),
        sa.Column("author_type", sa.String(length=32), nullable=False, server_default="STAFF_ENTERED"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("acuity_assessment", sa.String(length=32), nullable=False),
        sa.Column("clinical_concerns", sa.JSON(), nullable=True),
        sa.Column("suggested_next_steps", sa.JSON(), nullable=True),
        sa.Column("is_ai_generated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_triage_notes_case_id"), "triage_notes", ["case_id"], unique=False)

    # 11. review_actions
    op.create_table(
        "review_actions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("clinician_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("target_entity_type", sa.String(length=64), nullable=True),
        sa.Column("target_entity_id", sa.String(length=36), nullable=True),
        sa.Column("original_value", sa.JSON(), nullable=True),
        sa.Column("updated_value", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_actions_case_id"), "review_actions", ["case_id"], unique=False)

    # 12. audit_events
    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=True),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("actor_role", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("object_id", sa.String(length=64), nullable=False),
        sa.Column("result", sa.String(length=32), nullable=False, server_default="SUCCESS"),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_case_id"), "audit_events", ["case_id"], unique=False)
    op.create_index(op.f("ix_audit_events_action"), "audit_events", ["action"], unique=False)
    op.create_index(op.f("ix_audit_events_created_at"), "audit_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("review_actions")
    op.drop_table("triage_notes")
    op.drop_table("follow_up_answers")
    op.drop_table("follow_up_questions")
    op.drop_table("timeline_events")
    op.drop_table("vitals")
    op.drop_table("evidence")
    op.drop_table("case_state_transitions")
    op.drop_table("cases")
    op.drop_table("encounters")
    op.drop_table("patient_identifiers")

    with op.batch_alter_table("consents") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("hash_reference")
        batch_op.drop_column("status")
        batch_op.drop_column("consent_version")
        batch_op.drop_column("channel")
        batch_op.drop_column("purpose")

    with op.batch_alter_table("patients") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("is_synthetic")

    with op.batch_alter_table("facilities") as batch_op:
        batch_op.drop_column("capabilities_profile")
        batch_op.drop_column("operational_status")
