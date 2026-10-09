"""0002_clinical_data_architecture

Revision ID: a3dcfe723965
Revises: e2c6c0aad9de
Create Date: 2026-09-20 08:25:04.108738

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3dcfe723965'
down_revision: Union[str, Sequence[str], None] = 'e2c6c0aad9de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema and migrate existing data cleanly."""

    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------
    # 1. CREATE NEW CLINICAL TABLES (IF NOT EXIST)
    # -------------------------------------------------------------

    # Table: patient_identifiers
    exec_sql("""
        CREATE TABLE IF NOT EXISTS patient_identifiers (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            identifier_type VARCHAR(50) NOT NULL DEFAULT 'mrn',
            identifier_value VARCHAR(128) NOT NULL,
            issuing_system VARCHAR(100),
            is_primary BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_patient_identifier UNIQUE (patient_id, identifier_type, identifier_value)
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_patient_identifiers_patient_id ON patient_identifiers(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_patient_identifiers_type_val ON patient_identifiers(identifier_type, identifier_value)")

    # Table: encounters
    exec_sql("""
        CREATE TABLE IF NOT EXISTS encounters (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            facility_id VARCHAR(36) NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
            attending_clinician_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            encounter_type VARCHAR(50) NOT NULL DEFAULT 'outpatient',
            status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
            reason_for_visit VARCHAR(500),
            clinical_summary TEXT,
            start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_encounters_patient_id ON encounters(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_encounters_facility_id ON encounters(facility_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_encounters_start_time ON encounters(start_time)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_encounters_patient_start_time ON encounters(patient_id, start_time)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_encounters_facility_start_time ON encounters(facility_id, start_time)")

    # Table: clinical_observations
    exec_sql("""
        CREATE TABLE IF NOT EXISTS clinical_observations (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            observation_type VARCHAR(50) NOT NULL,
            value_numeric DOUBLE PRECISION,
            value_text VARCHAR(255),
            unit VARCHAR(50) NOT NULL,
            reference_range_low DOUBLE PRECISION,
            reference_range_high DOUBLE PRECISION,
            interpretation VARCHAR(50),
            observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            recorded_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            source VARCHAR(50) NOT NULL DEFAULT 'human_entered',
            verification_status VARCHAR(50) NOT NULL DEFAULT 'unverified',
            verified_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            verified_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_obs_patient_id ON clinical_observations(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_obs_encounter_id ON clinical_observations(encounter_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_obs_type ON clinical_observations(observation_type)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_obs_patient_type_date ON clinical_observations(patient_id, observation_type, observed_at)")

    # Table: allergies
    exec_sql("""
        CREATE TABLE IF NOT EXISTS allergies (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            substance VARCHAR(255) NOT NULL,
            reaction VARCHAR(255),
            severity VARCHAR(50) NOT NULL DEFAULT 'unknown',
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            onset_date VARCHAR(50),
            notes TEXT,
            recorded_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            verification_status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_allergies_patient_id ON allergies(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_allergies_substance ON allergies(substance)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_allergies_status ON allergies(status)")

    # Table: medications
    exec_sql("""
        CREATE TABLE IF NOT EXISTS medications (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            medication_name VARCHAR(255) NOT NULL,
            dosage VARCHAR(100),
            route VARCHAR(50),
            frequency VARCHAR(100),
            duration VARCHAR(100),
            medication_type VARCHAR(50) NOT NULL DEFAULT 'current',
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            start_date TIMESTAMP WITH TIME ZONE,
            end_date TIMESTAMP WITH TIME ZONE,
            instructions TEXT,
            prescribed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medications_patient_id ON medications(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medications_name ON medications(medication_name)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medications_status ON medications(status)")

    # Table: medical_conditions
    exec_sql("""
        CREATE TABLE IF NOT EXISTS medical_conditions (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            condition_name VARCHAR(255) NOT NULL,
            code VARCHAR(50),
            clinical_status VARCHAR(50) NOT NULL DEFAULT 'active',
            verification_status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
            severity VARCHAR(50),
            onset_date VARCHAR(50),
            resolution_date VARCHAR(50),
            notes TEXT,
            recorded_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medical_conditions_patient_id ON medical_conditions(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medical_conditions_name ON medical_conditions(condition_name)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_medical_conditions_status ON medical_conditions(clinical_status)")

    # Table: diagnoses
    exec_sql("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            description VARCHAR(500) NOT NULL,
            code VARCHAR(50),
            diagnosis_type VARCHAR(50) NOT NULL DEFAULT 'clinician_confirmed',
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            is_primary BOOLEAN NOT NULL DEFAULT FALSE,
            ai_confidence_score DOUBLE PRECISION,
            verification_status VARCHAR(50) NOT NULL DEFAULT 'unverified',
            verified_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            verified_at TIMESTAMP WITH TIME ZONE,
            diagnosed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_diagnoses_patient_id ON diagnoses(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_diagnoses_encounter_id ON diagnoses(encounter_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_diagnoses_type ON diagnoses(diagnosis_type)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_diagnoses_status ON diagnoses(status)")

    # Table: clinical_notes
    exec_sql("""
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            consultation_id VARCHAR(36) REFERENCES consultations(id) ON DELETE SET NULL,
            author_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            note_type VARCHAR(50) NOT NULL DEFAULT 'soap',
            status VARCHAR(50) NOT NULL DEFAULT 'finalized',
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            parent_note_id VARCHAR(36) REFERENCES clinical_notes(id) ON DELETE SET NULL,
            amendment_reason TEXT,
            is_signed BOOLEAN NOT NULL DEFAULT TRUE,
            signed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_clinical_notes_patient_id ON clinical_notes(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_clinical_notes_encounter_id ON clinical_notes(encounter_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_clinical_notes_author_id ON clinical_notes(author_id)")

    # Table: ai_runs
    exec_sql("""
        CREATE TABLE IF NOT EXISTS ai_runs (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) REFERENCES patients(id) ON DELETE SET NULL,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            case_id VARCHAR(36) REFERENCES triage_cases(id) ON DELETE SET NULL,
            task_type VARCHAR(100) NOT NULL,
            model_provider VARCHAR(50) NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            prompt_version VARCHAR(50),
            input_payload_hash VARCHAR(64),
            status VARCHAR(50) NOT NULL DEFAULT 'queued',
            output_data TEXT,
            error_message TEXT,
            latency_ms INTEGER,
            review_status VARCHAR(50) NOT NULL DEFAULT 'unreviewed',
            reviewed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
            reviewed_at TIMESTAMP WITH TIME ZONE,
            review_comments TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP WITH TIME ZONE
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_ai_runs_task_status ON ai_runs(task_type, status)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_ai_runs_patient_id ON ai_runs(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_ai_runs_created_at ON ai_runs(created_at)")

    # Table: referrals
    exec_sql("""
        CREATE TABLE IF NOT EXISTS referrals (
            id VARCHAR(36) PRIMARY KEY,
            patient_id VARCHAR(36) NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
            encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL,
            case_id VARCHAR(36) REFERENCES triage_cases(id) ON DELETE SET NULL,
            origin_facility_id VARCHAR(36) NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
            destination_facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL,
            referring_doctor_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            specialty_requested VARCHAR(100),
            priority VARCHAR(50) NOT NULL DEFAULT 'routine',
            status VARCHAR(50) NOT NULL DEFAULT 'issued',
            reason_for_referral TEXT NOT NULL,
            clinical_summary TEXT,
            transport_requirements VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS ix_referrals_patient_id ON referrals(patient_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_referrals_origin_facility ON referrals(origin_facility_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_referrals_destination_facility ON referrals(destination_facility_id)")
    exec_sql("CREATE INDEX IF NOT EXISTS ix_referrals_status ON referrals(status)")

    # -------------------------------------------------------------
    # 2. ADD COLUMNS & CONSTRAINTS TO EXISTING TABLES
    # -------------------------------------------------------------
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='facility_id') THEN
                    ALTER TABLE users ADD COLUMN facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL;
                    CREATE INDEX ix_users_facility_id ON users(facility_id);
                END IF;
            END $$;
        """)

        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='patients' AND column_name='facility_id') THEN
                    ALTER TABLE patients ADD COLUMN facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL;
                    CREATE INDEX ix_patients_facility_id ON patients(facility_id);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='patients' AND column_name='user_id') THEN
                    ALTER TABLE patients ADD COLUMN user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL;
                    CREATE INDEX ix_patients_user_id ON patients(user_id);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='patients' AND column_name='is_active') THEN
                    ALTER TABLE patients ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
                END IF;
            END $$;
        """)

        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='consultations' AND column_name='facility_id') THEN
                    ALTER TABLE consultations ADD COLUMN facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL;
                    CREATE INDEX ix_consultations_facility_id ON consultations(facility_id);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='consultations' AND column_name='encounter_id') THEN
                    ALTER TABLE consultations ADD COLUMN encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL;
                    CREATE INDEX ix_consultations_encounter_id ON consultations(encounter_id);
                END IF;
            END $$;
        """)

        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='triage_cases' AND column_name='facility_id') THEN
                    ALTER TABLE triage_cases ADD COLUMN facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL;
                    CREATE INDEX ix_triage_cases_facility_id ON triage_cases(facility_id);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='triage_cases' AND column_name='encounter_id') THEN
                    ALTER TABLE triage_cases ADD COLUMN encounter_id VARCHAR(36) REFERENCES encounters(id) ON DELETE SET NULL;
                    CREATE INDEX ix_triage_cases_encounter_id ON triage_cases(encounter_id);
                END IF;
            END $$;
        """)

        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='audit_logs' AND column_name='facility_id') THEN
                    ALTER TABLE audit_logs ADD COLUMN facility_id VARCHAR(36) REFERENCES facilities(id) ON DELETE SET NULL;
                    CREATE INDEX ix_audit_logs_facility_id ON audit_logs(facility_id);
                    CREATE INDEX ix_audit_logs_facility_timestamp ON audit_logs(facility_id, timestamp);
                END IF;
            END $$;
        """)

        exec_sql("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='consultation_id') THEN
                    ALTER TABLE documents ADD COLUMN consultation_id VARCHAR(36) REFERENCES consultations(id) ON DELETE SET NULL;
                    CREATE INDEX ix_documents_consultation_id ON documents(consultation_id);
                END IF;
            END $$;
        """)

        # -------------------------------------------------------------
        # 3. FIX CASCADE DELETE SAFETY ON CONSULTATIONS
        # -------------------------------------------------------------
        exec_sql("""
            DO $$
            BEGIN
                ALTER TABLE consultations DROP CONSTRAINT IF EXISTS consultations_patient_id_fkey;
                ALTER TABLE consultations ADD CONSTRAINT consultations_patient_id_fkey 
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT;

                ALTER TABLE consultations DROP CONSTRAINT IF EXISTS consultations_doctor_id_fkey;
                ALTER TABLE consultations ADD CONSTRAINT consultations_doctor_id_fkey 
                    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE RESTRICT;
            EXCEPTION
                WHEN OTHERS THEN
                    NULL;
            END $$;
        """)

        # -------------------------------------------------------------
        # 4. COMPOSITE INDEXES FOR SCALABLE QUERYING
        # -------------------------------------------------------------
        exec_sql("CREATE INDEX IF NOT EXISTS ix_consultations_patient_created ON consultations(patient_id, created_at)")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_status_created ON triage_cases(status, created_at)")
        exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_facility_created ON triage_cases(facility_id, created_at)")

        # -------------------------------------------------------------
        # 5. DATA MIGRATION & BACKFILL
        # -------------------------------------------------------------
        exec_sql("""
            DO $$
            DECLARE
                default_fac_id VARCHAR(36);
                james_patient_id VARCHAR(36);
                patient_user_id VARCHAR(36);
            BEGIN
                SELECT id INTO default_fac_id FROM facilities WHERE facility_code = 'FAC-DISTRICT-01' LIMIT 1;
                IF default_fac_id IS NOT NULL THEN
                    UPDATE users SET facility_id = default_fac_id WHERE facility_id IS NULL;
                    UPDATE patients SET facility_id = default_fac_id WHERE facility_id IS NULL;
                    UPDATE consultations SET facility_id = default_fac_id WHERE facility_id IS NULL;
                    UPDATE triage_cases SET facility_id = default_fac_id WHERE facility_id IS NULL;
                    UPDATE audit_logs SET facility_id = default_fac_id WHERE facility_id IS NULL;
                END IF;

                SELECT id INTO patient_user_id FROM users WHERE email = 'patient@clinova.ai' LIMIT 1;
                SELECT id INTO james_patient_id FROM patients WHERE email = 'patient@clinova.ai' OR mrn = 'CLN-2026-10482' LIMIT 1;

                IF patient_user_id IS NOT NULL AND james_patient_id IS NOT NULL THEN
                    UPDATE patients SET user_id = patient_user_id WHERE id = james_patient_id;
                    UPDATE triage_cases SET patient_id = james_patient_id WHERE patient_id = patient_user_id;
                END IF;
            END $$;
        """)

        exec_sql("""
            INSERT INTO patient_identifiers (id, patient_id, identifier_type, identifier_value, issuing_system, is_primary, created_at, updated_at)
            SELECT 
                md5(p.id || 'mrn' || p.mrn)::uuid::text,
                p.id,
                'MRN'::identifiertype,
                p.mrn,
                'CLINOVA-EHR',
                TRUE,
                p.created_at,
                p.updated_at
            FROM patients p
            ON CONFLICT (patient_id, identifier_type, identifier_value) DO NOTHING
        """)

        exec_sql("""
            INSERT INTO allergies (id, patient_id, substance, reaction, severity, status, notes, verification_status, created_at, updated_at)
            SELECT 
                md5(p.id || 'allergy' || p.allergies)::uuid::text,
                p.id,
                TRIM(SPLIT_PART(p.allergies, '(', 1)),
                NULLIF(TRIM(REPLACE(SPLIT_PART(p.allergies, '(', 2), ')', '')), ''),
                CASE 
                    WHEN p.allergies ILIKE '%anaphylaxis%' THEN 'LIFE_THREATENING'::allergyseverity
                    WHEN p.allergies ILIKE '%severe%' THEN 'SEVERE'::allergyseverity
                    ELSE 'MODERATE'::allergyseverity
                END,
                'ACTIVE'::allergystatus,
                'Migrated from historical free-text record: ' || p.allergies,
                'confirmed',
                p.created_at,
                p.updated_at
            FROM patients p
            WHERE p.allergies IS NOT NULL 
              AND TRIM(p.allergies) != '' 
              AND p.allergies NOT ILIKE 'none%'
            ON CONFLICT (id) DO NOTHING
        """)

        exec_sql("""
            DO $$
            DECLARE
                c_rec RECORD;
                new_enc_id VARCHAR(36);
            BEGIN
                FOR c_rec IN SELECT id, patient_id, doctor_id, facility_id, scheduled_at, status, chief_complaint, created_at FROM consultations WHERE encounter_id IS NULL LOOP
                    new_enc_id := md5('enc_' || c_rec.id)::uuid::text;
                    
                    INSERT INTO encounters (id, patient_id, facility_id, attending_clinician_id, encounter_type, status, reason_for_visit, start_time, created_at, updated_at)
                    VALUES (
                        new_enc_id,
                        c_rec.patient_id,
                        COALESCE(c_rec.facility_id, (SELECT id FROM facilities WHERE facility_code='FAC-DISTRICT-01' LIMIT 1)),
                        c_rec.doctor_id,
                        'OUTPATIENT'::encountertype,
                        CASE WHEN UPPER(c_rec.status::text) = 'COMPLETED' THEN 'COMPLETED'::encounterstatus ELSE 'IN_PROGRESS'::encounterstatus END,
                        c_rec.chief_complaint,
                        c_rec.scheduled_at,
                        c_rec.created_at,
                        c_rec.created_at
                    ) ON CONFLICT (id) DO NOTHING;

                    UPDATE consultations SET encounter_id = new_enc_id WHERE id = c_rec.id;
                END LOOP;
            END $$;
        """)

        exec_sql("""
            INSERT INTO clinical_notes (id, patient_id, encounter_id, consultation_id, author_id, note_type, status, title, content, version, is_signed, created_at, updated_at)
            SELECT
                md5('note_' || c.id)::uuid::text,
                c.patient_id,
                c.encounter_id,
                c.id,
                c.doctor_id,
                'SOAP'::notetype,
                'FINALIZED'::notestatus,
                'Initial Clinical Assessment — ' || c.chief_complaint,
                'SUBJECTIVE: ' || COALESCE(c.subjective, 'N/A') || E'\n\n' ||
                'OBJECTIVE: ' || COALESCE(c.objective, 'N/A') || E'\n\n' ||
                'ASSESSMENT: ' || COALESCE(c.assessment, 'N/A') || E'\n\n' ||
                'PLAN: ' || COALESCE(c.plan, 'N/A'),
                1,
                TRUE,
                c.created_at,
                c.updated_at
            FROM consultations c
            WHERE (c.subjective IS NOT NULL OR c.objective IS NOT NULL OR c.assessment IS NOT NULL OR c.plan IS NOT NULL)
              AND c.encounter_id IS NOT NULL
            ON CONFLICT (id) DO NOTHING
        """)
    else:
        # Cross-platform / SQLite fallback handling
        from sqlalchemy import inspect
        inspector = inspect(bind)
        if inspector.has_table("users"):
            cols = {c["name"] for c in inspector.get_columns("users")}
            if "facility_id" not in cols:
                try:
                    op.add_column("users", sa.Column("facility_id", sa.String(36), sa.ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_users_facility_id", "users", ["facility_id"])
                except Exception:
                    pass
        if inspector.has_table("patients"):
            cols = {c["name"] for c in inspector.get_columns("patients")}
            if "facility_id" not in cols:
                try:
                    op.add_column("patients", sa.Column("facility_id", sa.String(36), sa.ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_patients_facility_id", "patients", ["facility_id"])
                except Exception:
                    pass
            if "user_id" not in cols:
                try:
                    op.add_column("patients", sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_patients_user_id", "patients", ["user_id"])
                except Exception:
                    pass
            if "is_active" not in cols:
                try:
                    op.add_column("patients", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
                except Exception:
                    pass
        if inspector.has_table("consultations"):
            cols = {c["name"] for c in inspector.get_columns("consultations")}
            if "facility_id" not in cols:
                try:
                    op.add_column("consultations", sa.Column("facility_id", sa.String(36), sa.ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_consultations_facility_id", "consultations", ["facility_id"])
                except Exception:
                    pass
            if "encounter_id" not in cols:
                try:
                    op.add_column("consultations", sa.Column("encounter_id", sa.String(36), sa.ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_consultations_encounter_id", "consultations", ["encounter_id"])
                except Exception:
                    pass
        if inspector.has_table("triage_cases"):
            cols = {c["name"] for c in inspector.get_columns("triage_cases")}
            if "facility_id" not in cols:
                try:
                    op.add_column("triage_cases", sa.Column("facility_id", sa.String(36), sa.ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_triage_cases_facility_id", "triage_cases", ["facility_id"])
                except Exception:
                    pass
            if "encounter_id" not in cols:
                try:
                    op.add_column("triage_cases", sa.Column("encounter_id", sa.String(36), sa.ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_triage_cases_encounter_id", "triage_cases", ["encounter_id"])
                except Exception:
                    pass
        if inspector.has_table("audit_logs"):
            cols = {c["name"] for c in inspector.get_columns("audit_logs")}
            if "facility_id" not in cols:
                try:
                    op.add_column("audit_logs", sa.Column("facility_id", sa.String(36), sa.ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_audit_logs_facility_id", "audit_logs", ["facility_id"])
                    op.create_index("ix_audit_logs_facility_timestamp", "audit_logs", ["facility_id", "timestamp"])
                except Exception:
                    pass
        if inspector.has_table("documents"):
            cols = {c["name"] for c in inspector.get_columns("documents")}
            if "consultation_id" not in cols:
                try:
                    op.add_column("documents", sa.Column("consultation_id", sa.String(36), sa.ForeignKey("consultations.id", ondelete="SET NULL"), nullable=True))
                    op.create_index("ix_documents_consultation_id", "documents", ["consultation_id"])
                except Exception:
                    pass

        try:
            exec_sql("CREATE INDEX IF NOT EXISTS ix_consultations_patient_created ON consultations(patient_id, created_at)")
        except Exception:
            pass
        try:
            exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_status_created ON triage_cases(status, created_at)")
        except Exception:
            pass
        try:
            exec_sql("CREATE INDEX IF NOT EXISTS ix_triage_cases_facility_created ON triage_cases(facility_id, created_at)")
        except Exception:
            pass


def downgrade() -> None:
    """Downgrade schema."""
    def exec_sql(sql: str):
        op.execute(sa.text(sql.strip()))

    exec_sql("DROP TABLE IF EXISTS referrals CASCADE")
    exec_sql("DROP TABLE IF EXISTS ai_runs CASCADE")
    exec_sql("DROP TABLE IF EXISTS clinical_notes CASCADE")
    exec_sql("DROP TABLE IF EXISTS diagnoses CASCADE")
    exec_sql("DROP TABLE IF EXISTS medical_conditions CASCADE")
    exec_sql("DROP TABLE IF EXISTS medications CASCADE")
    exec_sql("DROP TABLE IF EXISTS allergies CASCADE")
    exec_sql("DROP TABLE IF EXISTS clinical_observations CASCADE")
    exec_sql("DROP TABLE IF EXISTS encounters CASCADE")
    exec_sql("DROP TABLE IF EXISTS patient_identifiers CASCADE")

    exec_sql("ALTER TABLE users DROP COLUMN IF EXISTS facility_id")
    exec_sql("ALTER TABLE patients DROP COLUMN IF EXISTS facility_id")
    exec_sql("ALTER TABLE patients DROP COLUMN IF EXISTS user_id")
    exec_sql("ALTER TABLE patients DROP COLUMN IF EXISTS is_active")
    exec_sql("ALTER TABLE consultations DROP COLUMN IF EXISTS facility_id")
    exec_sql("ALTER TABLE consultations DROP COLUMN IF EXISTS encounter_id")
    exec_sql("ALTER TABLE triage_cases DROP COLUMN IF EXISTS facility_id")
    exec_sql("ALTER TABLE triage_cases DROP COLUMN IF EXISTS encounter_id")
    exec_sql("ALTER TABLE audit_logs DROP COLUMN IF EXISTS facility_id")
    exec_sql("ALTER TABLE documents DROP COLUMN IF EXISTS consultation_id")
