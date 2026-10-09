"""CLINOVA AI — Database Initialization & Synthetic Seed Data.

Bootstraps the 5 representative healthcare network facilities and baseline personas
strictly using synthetic clinical profiles as mandated by DOC-09 and DOC-14.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import Base
from app.db.session import engine, async_session_factory
from app.db.models import Facility, FacilityCapability, User, TriageSnapshotRecord


SEED_FACILITIES = [
    {
        "id": "FAC-PHC-01",
        "facility_code": "FAC-PHC-01",
        "name": "Angul Rural PHC",
        "tier": "LEVEL_1_PHC",
        "latitude": 20.84,
        "longitude": 85.10,
        "icu_beds_total": 0,
        "icu_beds_available": 0,
        "general_beds_total": 6,
        "general_beds_available": 4,
        "ed_waiting_cases": 2,
        "ed_avg_wait_min": 10,
        "capabilities": [
            ("OUTPATIENT_TRIAGE", True),
            ("ORAL_MEDS", True),
            ("BASIC_WOUND_CARE", True),
            ("NORMAL_DELIVERY", True),
            ("CAPILLARY_GLUCOSE", True),
            ("URINE_DIPSTICK", True),
            ("MALARIAL_RDT", True),
        ],
    },
    {
        "id": "FAC-CHC-02",
        "facility_code": "FAC-CHC-02",
        "name": "Talcher Community Health Center",
        "tier": "LEVEL_2_CHC",
        "latitude": 20.95,
        "longitude": 85.22,
        "icu_beds_total": 0,
        "icu_beds_available": 0,
        "general_beds_total": 30,
        "general_beds_available": 12,
        "ed_waiting_cases": 6,
        "ed_avg_wait_min": 25,
        "capabilities": [
            ("RESUSCITATION_BAY", True),
            ("MINOR_OT", True),
            ("OXYGEN_CONCENTRATOR", True),
            ("MATERNITY_WARD", True),
            ("PLAIN_XRAY", True),
            ("BASIC_MICROSCOPY", True),
            ("CBC_ANALYZER", True),
            ("BIOCHEMISTRY", True),
        ],
    },
    {
        "id": "FAC-SDH-03",
        "facility_code": "FAC-SDH-03",
        "name": "Dhenkanal Sub-District Hospital",
        "tier": "LEVEL_3_SDH",
        "latitude": 20.66,
        "longitude": 85.59,
        "icu_beds_total": 4,
        "icu_beds_available": 2,
        "general_beds_total": 100,
        "general_beds_available": 35,
        "ed_waiting_cases": 14,
        "ed_avg_wait_min": 40,
        "capabilities": [
            ("GENERAL_SURGERY", True),
            ("EMERGENCY_ROOM", True),
            ("BLOOD_STORAGE", True),
            ("HDU_BEDS", True),
            ("OXYGEN_CONCENTRATOR", True),
            ("ULTRASOUND", True),
            ("DIGITAL_XRAY", True),
            ("AUTOMATED_HEMATOLOGY", True),
            ("ECG", True),
        ],
    },
    {
        "id": "FAC-DH-04",
        "facility_code": "FAC-DH-04",
        "name": "Cuttack District Headquarters Hospital",
        "tier": "LEVEL_4_DH",
        "latitude": 20.46,
        "longitude": 85.88,
        "icu_beds_total": 12,
        "icu_beds_available": 2,
        "general_beds_total": 350,
        "general_beds_available": 45,
        "ed_waiting_cases": 28,
        "ed_avg_wait_min": 75,
        "capabilities": [
            ("EMERGENCY_DEPT", True),
            ("ICU_BEDS", True),
            ("BLOOD_BANK", True),
            ("EMERGENCY_OT", True),
            ("MULTI_SPECIALTY_OT", True),
            ("CT_SCAN_24_7", True),
            ("THROMBOLYTICS", True),
            ("OXYGEN_CONCENTRATOR", True),
            ("ARTERIAL_BLOOD_GAS", True),
            ("TROPONIN_LAB", True),
            ("ULTRASOUND", True),
            ("MICROBIOLOGY", True),
        ],
    },
    {
        "id": "FAC-TMC-05",
        "facility_code": "FAC-TMC-05",
        "name": "SCB Medical College & Hospital",
        "tier": "LEVEL_5_TERTIARY",
        "latitude": 20.48,
        "longitude": 85.89,
        "icu_beds_total": 48,
        "icu_beds_available": 6,
        "general_beds_total": 1200,
        "general_beds_available": 110,
        "ed_waiting_cases": 65,
        "ed_avg_wait_min": 110,
        "capabilities": [
            ("LEVEL_1_TRAUMA", True),
            ("NEURO_TRAUMA_ICU", True),
            ("CARDIAC_CATH_LAB", True),
            ("DIALYSIS_UNIT", True),
            ("PICU_NICU", True),
            ("MRI", True),
            ("CT_128_SLICE", True),
            ("COMPREHENSIVE_BLOOD_BANK", True),
            ("EMERGENCY_OT", True),
            ("NEUROLOGY", True),
            ("CARDIOLOGY", True),
            ("THROMBOLYTICS", True),
        ],
    },
]

SEED_USERS = [
    {
        "id": "usr-doc-01",
        "username": "clinician",
        "email": "dr.priya.sharma@clinova.internal",
        "full_name": "Dr. Priya Sharma",
        "role": "CLINICIAN",
        "facility_id": "FAC-DH-04",
        "is_active": True,
    },
    {
        "id": "usr-nurse-02",
        "username": "nurse",
        "email": "ananya.patel@clinova.internal",
        "full_name": "Ananya Patel, RN",
        "role": "NURSE",
        "facility_id": "FAC-DH-04",
        "is_active": True,
    },
    {
        "id": "usr-nurse-phc",
        "username": "nurse_phc",
        "email": "nurse.phc@clinova.internal",
        "full_name": "Nurse PHC",
        "role": "NURSE",
        "facility_id": "FAC-PHC-01",
        "is_active": True,
    },
    {
        "id": "usr-ref-03",
        "username": "referral",
        "email": "sunil.kumar@clinova.internal",
        "full_name": "Sunil Kumar",
        "role": "REFERRAL_COORDINATOR",
        "facility_id": "FAC-DH-04",
        "is_active": True,
    },
    {
        "id": "usr-admin-03",
        "username": "facility_admin",
        "email": "rajesh.mohanty@clinova.internal",
        "full_name": "Rajesh Mohanty",
        "role": "FACILITY_ADMIN",
        "facility_id": "FAC-DH-04",
        "is_active": True,
    },
    {
        "id": "usr-audit-05",
        "username": "auditor",
        "email": "meera.sen@clinova.internal",
        "full_name": "Meera Sen",
        "role": "AUDITOR",
        "facility_id": None,
        "is_active": True,
    },
    {
        "id": "usr-sys-06",
        "username": "sysadmin",
        "email": "sysadmin@clinova.internal",
        "full_name": "System Administrator",
        "role": "SYSTEM_ADMIN",
        "facility_id": None,
        "is_active": True,
    },
    {
        "id": "usr-patient-07",
        "username": "patient",
        "email": "patient.demo@clinova.internal",
        "full_name": "Synthetic Patient Demo",
        "role": "PATIENT",
        "facility_id": "FAC-PHC-01",
        "is_active": True,
    },
    {
        "id": "usr-pt-09",
        "username": "patient_09",
        "email": "patient.09@clinova.internal",
        "full_name": "Patient 09 Demo",
        "role": "PATIENT",
        "facility_id": "FAC-DH-04",
        "is_active": True,
    },
    {
        "id": "usr-inactive-08",
        "username": "inactive_user",
        "email": "inactive.user@clinova.internal",
        "full_name": "Inactive Staff Member",
        "role": "NURSE",
        "facility_id": "FAC-PHC-01",
        "is_active": False,
    },
]


async def init_db() -> None:
    """Creates database tables and seeds synthetic healthcare facilities and personas."""
    from app.core.config import settings
    from app.core.auth import hash_password

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def upgrade_schema_if_needed(connection):
            from sqlalchemy import inspect, text
            inspector = inspect(connection)
            cols = {c["name"] for c in inspector.get_columns("users")}
            if "username" not in cols:
                connection.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(64)"))
                try:
                    connection.execute(text("CREATE UNIQUE INDEX ix_users_username ON users(username)"))
                except Exception:
                    pass
            if "hashed_password" not in cols:
                connection.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))
            if "patient_id" not in cols:
                connection.execute(text("ALTER TABLE users ADD COLUMN patient_id VARCHAR(36)"))
            if "updated_at" not in cols:
                connection.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP"))
            if "last_login_at" not in cols:
                connection.execute(text("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP"))

            if inspector.has_table("clinician_decisions"):
                d_cols = {c["name"] for c in inspector.get_columns("clinician_decisions")}
                if "clinical_impression" not in d_cols:
                    connection.execute(text("ALTER TABLE clinician_decisions ADD COLUMN clinical_impression TEXT"))
                if "treatment_plan" not in d_cols:
                    connection.execute(text("ALTER TABLE clinician_decisions ADD COLUMN treatment_plan TEXT"))
                if "clinical_rationale" not in d_cols:
                    connection.execute(text("ALTER TABLE clinician_decisions ADD COLUMN clinical_rationale TEXT"))

            if inspector.has_table("cases"):
                c_cols = {c["name"] for c in inspector.get_columns("cases")}
                if "source_language" not in c_cols:
                    connection.execute(text("ALTER TABLE cases ADD COLUMN source_language VARCHAR(16)"))
                if "translation_status" not in c_cols:
                    connection.execute(text("ALTER TABLE cases ADD COLUMN translation_status VARCHAR(32)"))
                if "translated_complaint" not in c_cols:
                    connection.execute(text("ALTER TABLE cases ADD COLUMN translated_complaint TEXT"))
                if "target_language" not in c_cols:
                    connection.execute(text("ALTER TABLE cases ADD COLUMN target_language VARCHAR(16)"))

            if inspector.has_table("case_outcomes"):
                o_cols = {c["name"] for c in inspector.get_columns("case_outcomes")}
                if "actual_action" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN actual_action VARCHAR(64) DEFAULT 'UNKNOWN'"))
                if "recommendation" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN recommendation VARCHAR(64)"))
                if "professional_decision" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN professional_decision VARCHAR(64)"))
                if "outcome_status" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN outcome_status VARCHAR(64) DEFAULT 'UNKNOWN'"))
                if "recorded_by" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN recorded_by VARCHAR(36)"))
                if "actor_role" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN actor_role VARCHAR(32)"))
                if "is_corrected" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN is_corrected BOOLEAN DEFAULT FALSE"))
                if "version" not in o_cols:
                    connection.execute(text("ALTER TABLE case_outcomes ADD COLUMN version INTEGER DEFAULT 1"))

            if inspector.has_table("document_extractions"):
                de_cols = {c["name"] for c in inspector.get_columns("document_extractions")}
                if "entity_type" not in de_cols:
                    connection.execute(text("ALTER TABLE document_extractions ADD COLUMN entity_type VARCHAR(64)"))
                if "entity_value" not in de_cols:
                    connection.execute(text("ALTER TABLE document_extractions ADD COLUMN entity_value VARCHAR(255)"))
                if "confidence" not in de_cols:
                    connection.execute(text("ALTER TABLE document_extractions ADD COLUMN confidence FLOAT DEFAULT 1.0"))
                if "bounding_box" not in de_cols:
                    connection.execute(text("ALTER TABLE document_extractions ADD COLUMN bounding_box JSON"))

            if not inspector.has_table("sync_journals"):
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS sync_journals (
                        sync_id VARCHAR(36) PRIMARY KEY,
                        node_id VARCHAR(64) NOT NULL,
                        entity_type VARCHAR(64) NOT NULL,
                        entity_id VARCHAR(64) NOT NULL,
                        case_id VARCHAR(36) REFERENCES cases(id) ON DELETE CASCADE,
                        operation VARCHAR(16) NOT NULL,
                        local_version INTEGER DEFAULT 1,
                        remote_version INTEGER DEFAULT 0,
                        sync_status VARCHAR(32) DEFAULT 'PENDING_UPLOAD',
                        payload_snapshot TEXT NOT NULL,
                        conflict_strategy VARCHAR(32) DEFAULT 'APPEND_ONLY',
                        created_at TIMESTAMP NOT NULL,
                        synced_at TIMESTAMP
                    )
                """))
            if not inspector.has_table("sync_conflicts"):
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS sync_conflicts (
                        conflict_id VARCHAR(36) PRIMARY KEY,
                        sync_id VARCHAR(36) NOT NULL REFERENCES sync_journals(sync_id) ON DELETE CASCADE,
                        entity_type VARCHAR(64) NOT NULL,
                        entity_id VARCHAR(64) NOT NULL,
                        case_id VARCHAR(36) REFERENCES cases(id) ON DELETE SET NULL,
                        local_payload TEXT NOT NULL,
                        remote_payload TEXT NOT NULL,
                        resolution_status VARCHAR(32) DEFAULT 'PENDING_HUMAN_REVIEW',
                        resolved_by_actor_id VARCHAR(64),
                        resolved_at TIMESTAMP,
                        resolution_notes TEXT,
                        created_at TIMESTAMP NOT NULL
                    )
                """))

            # Synchronize Alembic schema version tracking to current head revision (b84f3782910c)
            # This ensures 'alembic current' correctly reflects schema state and prevents
            # fresh database deployments from failing on subsequent 'alembic upgrade head' runs.
            if not inspector.has_table("alembic_version"):
                connection.execute(text(
                    "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
                ))
                connection.execute(text(
                    "INSERT INTO alembic_version (version_num) VALUES ('b84f3782910c')"
                ))
            else:
                res = connection.execute(text("SELECT version_num FROM alembic_version"))
                current_ver = res.scalars().first()
                if not current_ver:
                    connection.execute(text(
                        "INSERT INTO alembic_version (version_num) VALUES ('b84f3782910c')"
                    ))

        await conn.run_sync(upgrade_schema_if_needed)

    async with async_session_factory() as session:
        # Seed and synchronize healthcare facilities and baseline operational capabilities
        for raw_fac in SEED_FACILITIES:
            caps = raw_fac.get("capabilities", [])
            fac_attrs = {k: v for k, v in raw_fac.items() if k != "capabilities"}
            existing_fac = await session.get(Facility, raw_fac["id"])
            if existing_fac is None:
                fac = Facility(**fac_attrs)
                session.add(fac)
                await session.flush()
                for cap_code, is_op in caps:
                    cap = FacilityCapability(
                        facility_id=fac.id,
                        capability_code=cap_code,
                        is_operational=is_op,
                    )
                    session.add(cap)
            else:
                for k, v in fac_attrs.items():
                    setattr(existing_fac, k, v)
                for cap_code, is_op in caps:
                    stmt = select(FacilityCapability).where(
                        FacilityCapability.facility_id == existing_fac.id,
                        FacilityCapability.capability_code == cap_code,
                    )
                    cap_res = await session.execute(stmt)
                    cap = cap_res.scalars().first()
                    if cap:
                        cap.is_operational = is_op
                    else:
                        session.add(
                            FacilityCapability(
                                facility_id=existing_fac.id,
                                capability_code=cap_code,
                                is_operational=is_op,
                            )
                        )

        # Seed and synchronize synthetic users with bcrypt credentials
        demo_pwd_hash = hash_password(settings.DEMO_USER_PASSWORD)
        for user_data in SEED_USERS:
            existing_user = await session.get(User, user_data["id"])
            if existing_user is None:
                # Also check by email
                stmt = select(User).where(User.email == user_data["email"])
                res = await session.execute(stmt)
                existing_user = res.scalars().first()

            if existing_user is None:
                new_user = User(
                    **user_data,
                    hashed_password=demo_pwd_hash,
                )
                session.add(new_user)
            else:
                existing_user.username = user_data["username"]
                existing_user.full_name = user_data["full_name"]
                existing_user.role = user_data["role"]
                existing_user.facility_id = user_data["facility_id"]
                existing_user.is_active = user_data["is_active"]
                if not existing_user.hashed_password:
                    existing_user.hashed_password = demo_pwd_hash

        await session.commit()


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
