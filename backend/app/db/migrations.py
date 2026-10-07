"""Additive ownership migration for existing prototype databases. Never drops data."""
from sqlalchemy import inspect, text


def upgrade_ownership(connection):
    # 1. Existing ownership columns
    for table, column, unique in (
        ("patients", "user_id", True),
        ("triage_cases", "owner_user_id", False),
    ):
        try:
            columns = {c["name"] for c in inspect(connection).get_columns(table)}
            if column not in columns:
                connection.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN {column} VARCHAR(36) REFERENCES users(id)"
                ))
            connection.execute(text(
                f"CREATE {'UNIQUE ' if unique else ''}INDEX IF NOT EXISTS ix_{table}_{column} "
                f"ON {table} ({column})"
            ))
        except Exception:
            pass

    # 2. Canonical case columns on triage_cases
    try:
        triage_cols = {c["name"] for c in inspect(connection).get_columns("triage_cases")}
        if "case_version" not in triage_cols:
            connection.execute(text(
                "ALTER TABLE triage_cases ADD COLUMN case_version INTEGER NOT NULL DEFAULT 1"
            ))
        if "workflow_state" not in triage_cols:
            connection.execute(text(
                "ALTER TABLE triage_cases ADD COLUMN workflow_state VARCHAR(50) NOT NULL DEFAULT 'CREATED'"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_triage_cases_workflow_state ON triage_cases (workflow_state)"
            ))
        if "review_readiness_status" not in triage_cols:
            connection.execute(text(
                "ALTER TABLE triage_cases ADD COLUMN review_readiness_status VARCHAR(50) NOT NULL DEFAULT 'not_ready'"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_triage_cases_readiness ON triage_cases (review_readiness_status)"
            ))
    except Exception:
        pass