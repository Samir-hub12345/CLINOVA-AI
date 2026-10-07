"""CLINOVA AI — Database Initialization & Synthetic Seed Data.

Bootstraps the 5 representative healthcare network facilities and baseline personas
strictly using synthetic clinical profiles as mandated by DOC-09 and DOC-14.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import Base
from app.db.session import engine, async_session_factory
from app.db.models import Facility, FacilityCapability, User


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
        "email": "dr.priya.sharma@clinova.internal",
        "full_name": "Dr. Priya Sharma",
        "role": "CLINICIAN",
        "facility_id": "FAC-DH-04",
    },
    {
        "id": "usr-nurse-02",
        "email": "ananya.patel@clinova.internal",
        "full_name": "Ananya Patel, RN",
        "role": "NURSE",
        "facility_id": "FAC-PHC-01",
    },
    {
        "id": "usr-admin-03",
        "email": "rajesh.mohanty@clinova.internal",
        "full_name": "Rajesh Mohanty",
        "role": "ADMIN",
        "facility_id": "FAC-DH-04",
    },
]


async def init_db() -> None:
    """Creates database tables and seeds synthetic healthcare facilities and personas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if facilities exist
        existing = await session.execute(select(Facility))
        if existing.scalars().first() is None:
            for raw_fac in SEED_FACILITIES:
                caps = raw_fac.get("capabilities", [])
                fac_attrs = {k: v for k, v in raw_fac.items() if k != "capabilities"}
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

            for user_data in SEED_USERS:
                user = User(**user_data)
                session.add(user)

            await session.commit()
