"""0003_medical_document_architecture

Revision ID: b4edef189201
Revises: a3dcfe723965
Create Date: 2026-09-20 23:59:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4edef189201'
down_revision: Union[str, Sequence[str], None] = 'a3dcfe723965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Safely upgrade schema for medical documents and object storage."""
    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        # 0. Add enum values if needed
        exec_sql("ALTER TYPE documentstatus ADD VALUE IF NOT EXISTS 'QUARANTINED';")
        exec_sql("ALTER TYPE documenttype ADD VALUE IF NOT EXISTS 'DISCHARGE_SUMMARY';")

        # 1. Add new columns to documents table
        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='safe_filename') THEN
                    ALTER TABLE documents ADD COLUMN safe_filename VARCHAR(255);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='detected_mime_type') THEN
                    ALTER TABLE documents ADD COLUMN detected_mime_type VARCHAR(100);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='scan_status') THEN
                    ALTER TABLE documents ADD COLUMN scan_status VARCHAR(50) NOT NULL DEFAULT 'clean';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='scan_details') THEN
                    ALTER TABLE documents ADD COLUMN scan_details TEXT;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='quarantined_at') THEN
                    ALTER TABLE documents ADD COLUMN quarantined_at TIMESTAMPTZ;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='checksum_algorithm') THEN
                    ALTER TABLE documents ADD COLUMN checksum_algorithm VARCHAR(32) NOT NULL DEFAULT 'SHA-256';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='version') THEN
                    ALTER TABLE documents ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='parent_document_id') THEN
                    ALTER TABLE documents ADD COLUMN parent_document_id VARCHAR(36) REFERENCES documents(id) ON DELETE SET NULL;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='is_current_version') THEN
                    ALTER TABLE documents ADD COLUMN is_current_version BOOLEAN NOT NULL DEFAULT TRUE;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='deleted_at') THEN
                    ALTER TABLE documents ADD COLUMN deleted_at TIMESTAMPTZ;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='storage_bucket') THEN
                    ALTER TABLE documents ADD COLUMN storage_bucket VARCHAR(100) NOT NULL DEFAULT 'medical-documents';
                END IF;
            END $$;
        """)
    else:
        from sqlalchemy import inspect
        inspector = inspect(bind)
        if inspector.has_table("documents"):
            cols = {c["name"] for c in inspector.get_columns("documents")}
            cols_to_add = [
                ("safe_filename", sa.Column("safe_filename", sa.String(255), nullable=True)),
                ("detected_mime_type", sa.Column("detected_mime_type", sa.String(100), nullable=True)),
                ("scan_status", sa.Column("scan_status", sa.String(50), nullable=False, server_default="clean")),
                ("scan_details", sa.Column("scan_details", sa.Text(), nullable=True)),
                ("quarantined_at", sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=True)),
                ("checksum_algorithm", sa.Column("checksum_algorithm", sa.String(32), nullable=False, server_default="SHA-256")),
                ("version", sa.Column("version", sa.Integer(), nullable=False, server_default="1")),
                ("parent_document_id", sa.Column("parent_document_id", sa.String(36), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)),
                ("is_current_version", sa.Column("is_current_version", sa.Boolean(), nullable=False, server_default=sa.true())),
                ("deleted_at", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)),
                ("storage_bucket", sa.Column("storage_bucket", sa.String(100), nullable=False, server_default="medical-documents")),
            ]
            for col_name, col_def in cols_to_add:
                if col_name not in cols:
                    try:
                        op.add_column("documents", col_def)
                    except Exception:
                        pass

    # 2. Backfill existing document rows in a single UPDATE command
    exec_sql("""
        UPDATE documents SET 
            safe_filename = COALESCE(safe_filename, filename),
            detected_mime_type = COALESCE(detected_mime_type, mime_type),
            scan_status = COALESCE(scan_status, 'clean'),
            checksum_algorithm = COALESCE(checksum_algorithm, 'SHA-256'),
            version = COALESCE(version, 1),
            is_current_version = COALESCE(is_current_version, TRUE),
            storage_bucket = COALESCE(storage_bucket, 'medical-documents');
    """)

    # 3. Create indexes on documents individually
    exec_sql("CREATE INDEX IF NOT EXISTS ix_documents_parent_document_id ON documents(parent_document_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_documents_scan_status ON documents(scan_status);")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_documents_deleted_at ON documents(deleted_at);")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_documents_facility_created ON documents(facility_id, created_at DESC);")

    # 4. Create document_artifacts table
    exec_sql("""
        CREATE TABLE IF NOT EXISTS document_artifacts (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(36) NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
            artifact_type VARCHAR(50) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            checksum_sha256 VARCHAR(64) NOT NULL,
            storage_key VARCHAR(500) NOT NULL,
            storage_provider VARCHAR(50) NOT NULL DEFAULT 'local_object_store',
            content_text TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_document_artifacts_document_id ON document_artifacts(document_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_document_artifacts_created_at ON document_artifacts(created_at);")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_document_artifacts_artifact_type ON document_artifacts(artifact_type);")


def downgrade() -> None:
    """Revert Phase 3 document schema changes."""
    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    exec_sql("DROP TABLE IF EXISTS document_artifacts CASCADE;")
    exec_sql("DROP INDEX IF EXISTS ix_documents_facility_created;")
    exec_sql("DROP INDEX IF EXISTS ix_documents_deleted_at;")
    exec_sql("DROP INDEX IF EXISTS ix_documents_scan_status;")
    exec_sql("DROP INDEX IF EXISTS ix_documents_parent_document_id;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS storage_bucket;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS deleted_at;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS is_current_version;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS parent_document_id;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS version;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS checksum_algorithm;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS quarantined_at;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS scan_details;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS scan_status;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS detected_mime_type;")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS safe_filename;")
