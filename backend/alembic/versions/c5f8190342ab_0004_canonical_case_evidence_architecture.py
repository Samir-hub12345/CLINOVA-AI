"""0004_canonical_case_evidence_architecture

Revision ID: c5f8190342ab
Revises: b4edef189201
Create Date: 2026-10-06 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5f8190342ab'
down_revision: Union[str, Sequence[str], None] = 'b4edef189201'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add canonical case tracking fields and create case_evidence table."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    if dialect == "postgresql":
        # 1. Add canonical fields to triage_cases if not already present
        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='triage_cases' AND column_name='case_version') THEN
                    ALTER TABLE triage_cases ADD COLUMN case_version INTEGER NOT NULL DEFAULT 1;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='triage_cases' AND column_name='workflow_state') THEN
                    ALTER TABLE triage_cases ADD COLUMN workflow_state VARCHAR(50) NOT NULL DEFAULT 'CREATED';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='triage_cases' AND column_name='review_readiness_status') THEN
                    ALTER TABLE triage_cases ADD COLUMN review_readiness_status VARCHAR(50) NOT NULL DEFAULT 'not_ready';
                END IF;
            END $$;
        """)
        exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_workflow_state ON triage_cases(workflow_state);")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_readiness ON triage_cases(review_readiness_status);")

        # 2. Create case_evidence table
        exec_sql("""
            CREATE TABLE IF NOT EXISTS case_evidence (
                id VARCHAR(36) PRIMARY KEY,
                case_id VARCHAR(36) NOT NULL REFERENCES triage_cases(id) ON DELETE CASCADE,
                encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
                canonical_field VARCHAR(100) NOT NULL,
                raw_value TEXT NOT NULL,
                normalized_value TEXT,
                source_type VARCHAR(50) NOT NULL DEFAULT 'patient_reported',
                source_reference VARCHAR(255),
                verification_state VARCHAR(50) NOT NULL DEFAULT 'unverified',
                confidence_score FLOAT,
                observed_at TIMESTAMPTZ,
                created_by_user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
                processor_name VARCHAR(100),
                version INTEGER NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        exec_sql("CREATE INDEX IF NOT EXISTS ix_case_evidence_case_id ON case_evidence(case_id);")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_case_evidence_canonical_field ON case_evidence(canonical_field);")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_case_evidence_case_field ON case_evidence(case_id, canonical_field);")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_case_evidence_case_active ON case_evidence(case_id, is_active);")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_case_evidence_verification ON case_evidence(verification_state, source_type);")
    else:
        # SQLite fallback handling
        # Add columns if not existing
        try:
            op.add_column("triage_cases", sa.Column("case_version", sa.Integer(), nullable=False, server_default="1"))
        except Exception:
            pass
        try:
            op.add_column("triage_cases", sa.Column("workflow_state", sa.String(50), nullable=False, server_default="CREATED"))
        except Exception:
            pass
        try:
            op.add_column("triage_cases", sa.Column("review_readiness_status", sa.String(50), nullable=False, server_default="not_ready"))
        except Exception:
            pass

        try:
            op.create_table(
                "case_evidence",
                sa.Column("id", sa.String(36), primary_key=True),
                sa.Column("case_id", sa.String(36), sa.ForeignKey("triage_cases.id", ondelete="CASCADE"), nullable=False),
                sa.Column("encounter_id", sa.String(36), sa.ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True),
                sa.Column("canonical_field", sa.String(100), nullable=False),
                sa.Column("raw_value", sa.Text(), nullable=False),
                sa.Column("normalized_value", sa.Text(), nullable=True),
                sa.Column("source_type", sa.String(50), nullable=False, server_default="patient_reported"),
                sa.Column("source_reference", sa.String(255), nullable=True),
                sa.Column("verification_state", sa.String(50), nullable=False, server_default="unverified"),
                sa.Column("confidence_score", sa.Float(), nullable=True),
                sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
                sa.Column("created_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
                sa.Column("processor_name", sa.String(100), nullable=True),
                sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
                sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
                sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
                sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
            )
        except Exception:
            pass


def downgrade() -> None:
    """Revert Phase 1 canonical case evidence schema changes."""
    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        exec_sql("DROP TABLE IF EXISTS case_evidence CASCADE;")
        exec_sql("DROP INDEX IF EXISTS ix_triage_cases_readiness;")
        exec_sql("DROP INDEX IF EXISTS ix_triage_cases_workflow_state;")
        exec_sql("ALTER TABLE triage_cases DROP COLUMN IF EXISTS review_readiness_status;")
        exec_sql("ALTER TABLE triage_cases DROP COLUMN IF EXISTS workflow_state;")
        exec_sql("ALTER TABLE triage_cases DROP COLUMN IF EXISTS case_version;")
    else:
        op.drop_table("case_evidence")
