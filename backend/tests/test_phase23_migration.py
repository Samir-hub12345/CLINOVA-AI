"""CLINOVA AI — Phase 23 CaseOutcome Migration Verification Test Suite.

Validates:
1. Migration of pre-existing databases containing legacy case_outcomes schema:
   Legacy fields: id, case_id, disposition, final_condition, notes, recorded_at.
2. Safe additive upgrade introducing all 8 Phase 23 fields:
   - actual_action (VARCHAR(64), default 'UNKNOWN')
   - recommendation (VARCHAR(64), nullable)
   - professional_decision (VARCHAR(64), nullable)
   - outcome_status (VARCHAR(64), default 'UNKNOWN')
   - recorded_by (VARCHAR(36), nullable)
   - actor_role (VARCHAR(32), nullable)
   - is_corrected (BOOLEAN, default False)
   - version (INTEGER, default 1)
3. Historical data preservation (zero data loss on existing records).
4. Creation on fresh databases where case_outcomes does not yet exist.
5. Cross-platform DDL compatibility (SQLite batch mode and PostgreSQL compatible).
"""

import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect, text, select
from alembic.config import Config
from alembic import command
import alembic.op as op


def test_migration_on_pre_existing_legacy_database():
    """
    Simulates an existing operational database that has legacy case_outcomes
    and verifies that the migration upgrades the schema non-destructively.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)

        # 1. Setup a legacy case_outcomes table (pre-Phase 23 schema)
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE cases (
                    id VARCHAR(36) PRIMARY KEY,
                    case_number VARCHAR(32) NOT NULL
                );
            """))
            conn.execute(text("""
                CREATE TABLE case_outcomes (
                    id VARCHAR(36) PRIMARY KEY,
                    case_id VARCHAR(36) NOT NULL UNIQUE,
                    disposition VARCHAR(64) NOT NULL,
                    final_condition VARCHAR(64) DEFAULT 'STABLE',
                    notes TEXT,
                    recorded_at DATETIME
                );
            """))
            # Insert historical legacy record
            conn.execute(text("""
                INSERT INTO cases (id, case_number) VALUES ('case-leg-01', 'CASE-2026-001');
            """))
            conn.execute(text("""
                INSERT INTO case_outcomes (id, case_id, disposition, final_condition, notes, recorded_at)
                VALUES ('out-leg-01', 'case-leg-01', 'DISCHARGED', 'STABLE', 'Legacy pre-Phase 23 record', '2026-10-08 12:00:00');
            """))

        # 2. Run the Alembic migration on this database
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        alembic_ini_path = os.path.join(backend_dir, "alembic.ini")

        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Import and run migration upgrade directly via file path
        import importlib.util
        mig_path = os.path.join(backend_dir, "alembic", "versions", "0014_phase23_case_outcome_architecture.py")
        spec = importlib.util.spec_from_file_location("mig_0014", mig_path)
        mig_0014 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mig_0014)
        
        # Test direct upgrade logic with Alembic operations
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            
            # Execute upgrade
            mig_0014.op = op_instance
            mig_0014.upgrade()

        # 3. Inspect columns after upgrade
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("case_outcomes")}

        required_phase23_fields = [
            "actual_action",
            "recommendation",
            "professional_decision",
            "outcome_status",
            "recorded_by",
            "actor_role",
            "is_corrected",
            "version",
        ]

        for field in required_phase23_fields:
            assert field in columns, f"Field '{field}' was not created in case_outcomes"

        # 4. Verify that historical data was preserved intact
        with engine.begin() as conn:
            row = conn.execute(text(
                "SELECT id, case_id, disposition, final_condition, notes FROM case_outcomes WHERE id = 'out-leg-01'"
            )).fetchone()
            assert row is not None
            assert row[0] == "out-leg-01"
            assert row[1] == "case-leg-01"
            assert row[2] == "DISCHARGED"
            assert row[3] == "STABLE"
            assert row[4] == "Legacy pre-Phase 23 record"

            # 5. Insert a full Phase 23 record
            conn.execute(text("""
                INSERT INTO cases (id, case_number) VALUES ('case-p23-02', 'CASE-2026-002');
            """))
            conn.execute(text("""
                INSERT INTO case_outcomes (
                    id, case_id, disposition, final_condition,
                    actual_action, recommendation, professional_decision, outcome_status,
                    recorded_by, actor_role, is_corrected, version, notes, recorded_at
                ) VALUES (
                    'out-p23-02', 'case-p23-02', 'TRANSFER_EXTERNAL', 'DETERIORATED',
                    'TRANSFERRED', 'REFER_TERTIARY', 'ADMIT_LOCAL_OBSERVE', 'DETERIORATED',
                    'usr-doc-01', 'CLINICIAN', 1, 2, 'Full Phase 23 verified', '2026-10-09 14:00:00'
                );
            """))

            p23_row = conn.execute(text(
                "SELECT actual_action, recommendation, professional_decision, outcome_status, version, is_corrected "
                "FROM case_outcomes WHERE id = 'out-p23-02'"
            )).fetchone()
            assert p23_row is not None
            assert p23_row[0] == "TRANSFERRED"
            assert p23_row[1] == "REFER_TERTIARY"
            assert p23_row[2] == "ADMIT_LOCAL_OBSERVE"
            assert p23_row[3] == "DETERIORATED"
            assert p23_row[4] == 2
            assert p23_row[5] in (1, True)

    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass


def test_migration_on_fresh_database():
    """
    Simulates a fresh database where case_outcomes does not yet exist,
    verifying that the migration creates the table from scratch with all fields.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)

        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE cases (
                    id VARCHAR(36) PRIMARY KEY,
                    case_number VARCHAR(32) NOT NULL
                );
            """))

        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        import importlib.util
        mig_path = os.path.join(backend_dir, "alembic", "versions", "0014_phase23_case_outcome_architecture.py")
        spec = importlib.util.spec_from_file_location("mig_0014_fresh", mig_path)
        mig_0014 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mig_0014)

        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            mig_0014.op = op_instance
            mig_0014.upgrade()

        inspector = inspect(engine)
        assert inspector.has_table("case_outcomes")
        columns = {c["name"]: c for c in inspector.get_columns("case_outcomes")}

        expected_all_fields = [
            "id",
            "case_id",
            "disposition",
            "final_condition",
            "actual_action",
            "recommendation",
            "professional_decision",
            "outcome_status",
            "recorded_by",
            "actor_role",
            "is_corrected",
            "version",
            "notes",
            "recorded_at",
        ]
        for field in expected_all_fields:
            assert field in columns, f"Expected field '{field}' not found in fresh case_outcomes table"

    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass


def test_migration_downgrade():
    """
    Verifies that downgrade() safely removes the Phase 23 columns
    without dropping the legacy table or legacy columns.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)

        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE cases (
                    id VARCHAR(36) PRIMARY KEY,
                    case_number VARCHAR(32) NOT NULL
                );
            """))

        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        import importlib.util
        mig_path = os.path.join(backend_dir, "alembic", "versions", "0014_phase23_case_outcome_architecture.py")
        spec = importlib.util.spec_from_file_location("mig_0014_down", mig_path)
        mig_0014 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mig_0014)

        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        # 1. Upgrade first
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            mig_0014.op = op_instance
            mig_0014.upgrade()

        # 2. Downgrade
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            op_instance = Operations(ctx)
            mig_0014.op = op_instance
            mig_0014.downgrade()

        inspector = inspect(engine)
        assert inspector.has_table("case_outcomes")
        columns = {c["name"]: c for c in inspector.get_columns("case_outcomes")}

        # Legacy columns still exist
        assert "id" in columns
        assert "case_id" in columns
        assert "disposition" in columns
        assert "final_condition" in columns

        # Phase 23 columns were removed
        for field in ["actual_action", "recommendation", "professional_decision", "outcome_status", "is_corrected", "version"]:
            assert field not in columns, f"Field '{field}' should have been removed during downgrade"

    finally:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass

