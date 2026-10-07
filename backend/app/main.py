import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.metrics import PrometheusMiddleware
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.migrations import upgrade_ownership
from app.db.session import engine, async_session_factory
import json
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.consultation import Consultation, ConsultationStatus, TriageLevel
from app.models.case import TriageCase
from app.models.facility import Facility
from app.models.encounter import Encounter, EncounterType, EncounterStatus

logger = logging.getLogger("clinova")


async def seed_initial_data():
    """Seed initial clinical demo accounts, patients, and triage cases."""
    async with async_session_factory() as db:
        # 0. Ensure default facilities exist
        fac1 = (await db.execute(select(Facility).where(Facility.facility_code == "FAC-DISTRICT-01"))).scalar_one_or_none()
        fac2 = (await db.execute(select(Facility).where(Facility.facility_code == "FAC-PHC-RURAL-02"))).scalar_one_or_none()
        if not fac1:
            fac1 = Facility(
                id="a1fa1a80-0a86-40bb-8358-5c12a06e0fe5",
                facility_code="FAC-DISTRICT-01",
                name="Government District Hospital",
                facility_type="District Hospital",
                address="Medical Enclave, Unit 4, Bhubaneswar, Odisha",
                contact_phone="+91 (0674) 230-1999",
                contact_email="casualty@clinova.ai",
                is_active=True,
            )
            db.add(fac1)
        if not fac2:
            fac2 = Facility(
                id="b1fb2a91-0b97-41cc-8469-6d23a07e0fe6",
                facility_code="FAC-PHC-RURAL-02",
                name="Community Primary Health Center (PHC)",
                facility_type="Primary Health Center",
                address="Rural Health Post, Khordha Block",
                contact_phone="+91 (0674) 230-1988",
                contact_email="phc.khordha@clinova.ai",
                is_active=True,
            )
            db.add(fac2)
        await db.commit()
        await db.refresh(fac1)
        await db.refresh(fac2)

        # Check if users exist
        res = await db.execute(select(User).limit(1))
        if res.scalar_one_or_none() is None:
            logger.info("Fresh database detected. Seeding CLINOVA AI demo users...")
            # 1. Demo Users
            doctor = User(
                email="doctor@clinova.ai",
                hashed_password=get_password_hash("ClinovaDoctor2026!"),
                full_name="Dr. Sarah Chen, MD",
                role=UserRole.DOCTOR,
                facility_id=fac1.id,
                is_active=True,
            )
            patient_user = User(
                email="patient@clinova.ai",
                hashed_password=get_password_hash("ClinovaPatient2026!"),
                full_name="James Miller",
                role=UserRole.PATIENT,
                is_active=True,
            )
            nurse = User(
                email="staff@clinova.ai",
                hashed_password=get_password_hash("ClinovaStaff2026!"),
                full_name="Nurse Sunita Patel, RN",
                role=UserRole.NURSE,
                facility_id=fac1.id,
                is_active=True,
            )
            admin = User(
                email="admin@clinova.ai",
                hashed_password=get_password_hash("ClinovaAdmin2026!"),
                full_name="Clinical Administrator",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add_all([doctor, patient_user, nurse, admin])
            await db.flush()

            # 2. Demo Patients
            patient1 = Patient(
                user_id=patient_user.id,
                mrn="CLN-2026-10482",
                first_name="James",
                last_name="Miller",
                date_of_birth="1982-06-14",
                gender="Male",
                blood_group="O+",
                phone="+1 (555) 234-5678",
                email="patient@clinova.ai",
                facility_id=fac1.id,
                emergency_contact="Sarah Miller (Spouse): +1 (555) 234-5679",
                allergies="Penicillin (Anaphylaxis)",
                current_medications="Lisinopril 10mg daily, Atorvastatin 20mg daily",
                medical_history="Hypertension (dx 2018), Hyperlipidemia, Former smoker (quit 2021)",
            )
            patient2 = Patient(
                mrn="CLN-2026-21890",
                first_name="Elena",
                last_name="Rostova",
                date_of_birth="1995-11-03",
                gender="Female",
                blood_group="A-",
                phone="+1 (555) 876-5432",
                email="elena.rostova@example.com",
                facility_id=fac1.id,
                emergency_contact="Dmitri Rostov (Brother): +1 (555) 876-5433",
                allergies="Sulfa drugs (Rash)",
                current_medications="Albuterol inhaler PRN",
                medical_history="Mild intermittent asthma since childhood",
            )
            patient3 = Patient(
                mrn="CLN-2026-34901",
                first_name="Marcus",
                last_name="Vance",
                date_of_birth="1960-03-22",
                gender="Male",
                blood_group="B+",
                phone="+1 (555) 432-1098",
                email="marcus.vance@example.com",
                facility_id=fac1.id,
                emergency_contact="Patricia Vance: +1 (555) 432-1099",
                allergies="None known",
                current_medications="Metformin 500mg BID, Amlodipine 5mg",
                medical_history="Type 2 Diabetes Mellitus (dx 2015), Stage 1 Hypertension",
            )
            db.add_all([patient1, patient2, patient3])
            await db.flush()

            # 3. Demo Consultation
            consultation = Consultation(
                patient_id=patient1.id,
                doctor_id=doctor.id,
                scheduled_at=datetime.now(timezone.utc),
                status=ConsultationStatus.COMPLETED,
                triage_level=TriageLevel.ROUTINE,
                chief_complaint="Follow-up on blood pressure control and routine medication review",
                vitals_data='{"blood_pressure_systolic":132,"blood_pressure_diastolic":84,"heart_rate":72,"respiratory_rate":16,"oxygen_saturation":98,"temperature":36.8}',
                subjective="Patient reports feeling well overall. Complies with daily Lisinopril and Atorvastatin. Denies chest pain, shortness of breath, palpitations, or lightheadedness.",
                objective="BP: 132/84 mmHg, HR: 72 bpm regular, SpO2: 98% room air, Temp: 36.8C. Cardiovascular: S1/S2 present, no murmurs. Lungs: Clear to auscultation bilaterally. No peripheral edema.",
                assessment="Essential Hypertension, stable on current monotherapy. Hyperlipidemia, controlled.",
                plan="1. Continue Lisinopril 10mg PO daily.\n2. Repeat basic metabolic panel and lipid panel in 6 months.\n3. Return to clinic in 6 months or sooner if symptomatic.",
                ai_generated_summary="Routine hypertensive follow-up with good medication compliance and stable physiological vitals.",
            )
            db.add(consultation)

            # 4. Demo Encounter
            encounter = Encounter(
                patient_id=patient1.id,
                attending_clinician_id=doctor.id,
                facility_id=fac1.id,
                encounter_type=EncounterType.OUTPATIENT,
                status=EncounterStatus.COMPLETED,
                reason_for_visit="Routine hypertension surveillance and metabolic review",
                clinical_summary="Patient reports feeling well overall. Complies with daily Lisinopril and Atorvastatin.",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
            )
            db.add(encounter)

            await db.commit()
            logger.info("CLINOVA AI demo users, patients, and encounters seeded successfully.")
        else:
            # If users already exist, ensure doctor and nurse have facility_id populated
            doc_user = (await db.execute(select(User).where(User.email == "doctor@clinova.ai"))).scalar_one_or_none()
            if doc_user and not doc_user.facility_id:
                doc_user.facility_id = fac1.id
            nurse_user = (await db.execute(select(User).where(User.email == "staff@clinova.ai"))).scalar_one_or_none()
            if nurse_user and not nurse_user.facility_id:
                nurse_user.facility_id = fac1.id
            await db.commit()

        # Only the well-known synthetic demo chart may be linked automatically.
        # Other legacy charts stay unlinked until an operator verifies ownership.
        demo_user = (await db.execute(select(User).where(User.email == "patient@clinova.ai", User.role == UserRole.PATIENT))).scalar_one_or_none()
        demo_chart = (await db.execute(select(Patient).where(Patient.mrn == "CLN-2026-10482", Patient.email == "patient@clinova.ai", Patient.first_name == "James", Patient.last_name == "Miller"))).scalar_one_or_none()
        if demo_user and demo_chart and demo_chart.user_id is None:
            existing_link = (await db.execute(select(Patient).where(Patient.user_id == demo_user.id))).scalar_one_or_none()
            if existing_link is None:
                demo_chart.user_id = demo_user.id
                await db.commit()

        # Check if triage cases exist
        case_res = await db.execute(select(TriageCase).limit(1))
        if case_res.scalar_one_or_none() is None:
            logger.info("Seeding 6 synthetic public health triage cases...")
            case1 = TriageCase(
                synthetic_case_id="CLV-DEMO-001",
                language="or",
                facility_type="Campus Health Center",
                visit_type="Campus Fever Triage",
                status="awaiting_review",
                queue_category="priority",
                queue_reason="TRIAGE-R05: High sustained fever or infectious disease signal",
                consent_status=True,
                approximate_age=21,
                gender="Male",
                context_notes="University undergraduate reporting acute fever outbreak in hostel.",
                raw_symptoms="à¬®à­‹à¬¤à­‡ à­© à¬¦à¬¿à¬¨ à¬¹à­‡à¬²à¬¾ à¬ªà­à¬°à¬¬à¬³ à¬œà­à­±à¬° à¬…à¬›à¬¿, à¬®à­à¬£à­à¬¡ à¬¬à¬¿à¬¨à­à¬§à¬¾ à¬¹à­‡à¬‰à¬›à¬¿ à¬à¬¬à¬‚ à¬¨à¬¿à¬¶à­à­±à¬¾à¬¸ à¬¨à­‡à¬¬à¬¾à¬°à­‡ à¬•à¬·à­à¬Ÿ à¬¹à­‡à¬‰à¬›à¬¿à¥¤",
                normalized_symptoms="Patient reports high fever for 3 days, severe headache, generalized body weakness, and progressive shortness of breath upon minimal exertion.",
                speech_transcript="à¬®à­‹à¬¤à­‡ à­© à¬¦à¬¿à¬¨ à¬¹à­‡à¬²à¬¾ à¬ªà­à¬°à¬¬à¬³ à¬œà­à­±à¬° à¬…à¬›à¬¿, à¬®à­à¬£à­à¬¡ à¬¬à¬¿à¬¨à­à¬§à¬¾ à¬¹à­‡à¬‰à¬›à¬¿ à¬à¬¬à¬‚ à¬¨à¬¿à¬¶à­à­±à¬¾à¬¸ à¬¨à­‡à¬¬à¬¾à¬°à­‡ à¬•à¬·à­à¬Ÿ à¬¹à­‡à¬‰à¬›à¬¿à¥¤",
                detected_language="Odia",
                timeline_events=json.dumps([
                    {"day": "Day 1", "description": "High fever, chills, severe frontal headache after hostel return.", "source": "Patient voice"},
                    {"day": "Day 2", "description": "Persistent fever 102.5F, nausea, poor oral intake.", "source": "Patient voice"},
                    {"day": "Day 3 (Today)", "description": "Shortness of breath on walking to campus clinic.", "source": "Current intake"},
                ]),
                risk_signals=json.dumps([
                    {"rule_id": "TRIAGE-R05", "signal": "High sustained fever or infectious disease signal", "source_text": "fever for 3 days", "severity": "PRIORITY", "timestamp": "10:14:02", "reviewer_confirmation_required": True, "status": "pending_confirmation"},
                    {"rule_id": "TRIAGE-R01", "signal": "Potential breathing-related urgency signal detected", "source_text": "shortness of breath", "severity": "URGENT REVIEW", "timestamp": "10:14:03", "reviewer_confirmation_required": True, "status": "pending_confirmation"}
                ]),
                missing_information=json.dumps([
                    "Symptom progression timeline in campus hostel setting",
                    "Recent exposure to water-borne or mosquito-borne illnesses"
                ]),
                follow_up_questions=json.dumps([
                    "Have any roommates in your dormitory exhibited similar high fever or rash?",
                    "Have you had recent travel outside the university campus?"
                ]),
            )

            case2 = TriageCase(
                synthetic_case_id="CLV-DEMO-002",
                language="hi",
                facility_type="Industrial Health Unit",
                visit_type="Occupational Screening",
                status="awaiting_review",
                queue_category="urgent-review",
                queue_reason="TRIAGE-R01: Potential breathing-related urgency signal detected",
                consent_status=True,
                approximate_age=44,
                gender="Male",
                context_notes="Machinist at metal fabrication unit with chronic dust exposure.",
                raw_symptoms="à¤¸à¤¾à¤‚à¤¸ à¤²à¥‡à¤¨à¥‡ à¤®à¥‡à¤‚ à¤¬à¤¹à¥à¤¤ à¤¤à¤•à¤²à¥€à¤« à¤¹à¥‹ à¤°à¤¹à¥€ à¤¹à¥ˆ, à¤¸à¥€à¤¨à¥‡ à¤®à¥‡à¤‚ à¤­à¤¾à¤°à¥€à¤ªà¤¨ à¤”à¤° à¤«à¥ˆà¤•à¥à¤Ÿà¥à¤°à¥€ à¤®à¥‡à¤‚ à¤§à¥‚à¤² à¤•à¥€ à¤µà¤œà¤¹ à¤¸à¥‡ à¤¤à¥‡à¤œ à¤–à¤¾à¤‚à¤¸à¥€ à¤¹à¥ˆà¥¤",
                normalized_symptoms="Industrial worker reports acute-on-chronic dyspnea, substernal heaviness, and severe paroxysmal coughing exacerbated by particulate exposure.",
                detected_language="Hindi",
                timeline_events=json.dumps([
                    {"day": "Day 1", "description": "Mild wheezing at end of shift.", "source": "Occupational intake"},
                    {"day": "Day 2", "description": "Coughing bouts waking from sleep.", "source": "Patient report"},
                    {"day": "Day 3 (Today)", "description": "Inability to catch breath during factory shift.", "source": "Current intake"}
                ]),
                risk_signals=json.dumps([
                    {"rule_id": "TRIAGE-R01", "signal": "Potential breathing-related urgency signal detected", "source_text": "difficulty breathing", "severity": "URGENT REVIEW", "timestamp": "09:30:11", "reviewer_confirmation_required": True, "status": "pending_confirmation"}
                ]),
                missing_information=json.dumps(["PPE compliance history", "Peak expiratory flow measurement"]),
                follow_up_questions=json.dumps(["Were you wearing an N95 respirator during the cutting shift?"]),
            )

            case3 = TriageCase(
                synthetic_case_id="CLV-DEMO-003",
                language="en",
                facility_type="Government Hospital",
                visit_type="Outpatient",
                status="approved",
                queue_category="routine",
                queue_reason="Standard non-emergent outpatient intake",
                consent_status=True,
                approximate_age=58,
                gender="Female",
                context_notes="Routine diabetic health surveillance.",
                raw_symptoms="Routine diabetes follow-up. Mild fatigue in evenings, checking recent fasting blood sugar report.",
                normalized_symptoms="Patient presenting for routine diabetic follow-up with mild evening fatigue and stable glycemic control.",
                detected_language="English",
                report_filename="CBC_DEMO_001.png",
                report_ocr_data=json.dumps([
                    {"field_name": "Hemoglobin (Hb)", "value": "12.4", "unit": "g/dL", "confidence": 0.94, "verification_status": "verified"},
                    {"field_name": "Total WBC", "value": "7.2", "unit": "x10^3/uL", "confidence": 0.91, "verification_status": "verified"},
                    {"field_name": "Platelets", "value": "220", "unit": "x10^3/uL", "confidence": 0.95, "verification_status": "verified"}
                ]),
                reviewer_name="Dr. S. Chen, MD",
                reviewer_notes="Routine follow-up approved. CBC parameters within expected reference margins.",
                approved_at=datetime.now(timezone.utc),
            )

            case4 = TriageCase(
                synthetic_case_id="CLV-DEMO-004",
                language="hi",
                facility_type="Public Health Camp",
                visit_type="Public Health Camp",
                status="awaiting_review",
                queue_category="routine",
                queue_reason="Standard non-emergent screening",
                consent_status=True,
                approximate_age=32,
                gender="Female",
                context_notes="Rural community public health camp attendee.",
                raw_symptoms="à¤•à¤®à¤œà¥‹à¤°à¥€ à¤”à¤° à¤¬à¤¦à¤¨ à¤¦à¤°à¥à¤¦ à¤¦à¥‹ à¤¦à¤¿à¤¨à¥‹à¤‚ à¤¸à¥‡ à¤¹à¥ˆ, à¤­à¥‚à¤– à¤•à¤® à¤²à¤— à¤°à¤¹à¥€ à¤¹à¥ˆà¥¤",
                normalized_symptoms="Patient reports generalized body ache and mild appetite suppression for two days; vital signs stable.",
                detected_language="Hindi",
            )

            case5 = TriageCase(
                synthetic_case_id="CLV-DEMO-005",
                language="or",
                facility_type="PHC",
                visit_type="Referral Preparation",
                status="referred",
                queue_category="urgent-review",
                queue_reason="TRIAGE-R04: Potential acute chest-pain or cardiovascular urgency signal",
                consent_status=True,
                approximate_age=62,
                gender="Male",
                context_notes="Primary health center patient requiring tertiary cardiology referral.",
                raw_symptoms="à¬›à¬¾à¬¤à¬¿à¬°à­‡ à¬ªà­à¬°à¬¬à¬³ à¬¯à¬¨à­à¬¤à­à¬°à¬£à¬¾ à¬¹à­‡à¬‰à¬›à¬¿ à¬à¬¬à¬‚ à¬¬à¬¾à¬® à¬¹à¬¾à¬¤à¬•à­ à¬¯à¬¨à­à¬¤à­à¬°à¬£à¬¾ à¬¬à­à­Ÿà¬¾à¬ªà­à¬›à¬¿, à¬ªà­à¬°à¬¬à¬³ à¬à¬¾à¬³ à¬¬à¬¾à¬¹à¬¾à¬°à­à¬›à¬¿à¥¤",
                normalized_symptoms="Patient reports acute chest pain radiating to the left arm with associated diaphoresis (profuse sweating). Urgent referral prepared.",
                detected_language="Odia",
                reviewer_name="Dr. S. Chen, MD",
                reviewer_notes="Urgent escalation to District Hospital Cardiology Unit. Stabilize on 100% O2 and urgent ECG.",
                referral_note=json.dumps({
                    "case_id": "CLV-DEMO-005",
                    "synthetic_case_id": "CLV-DEMO-005",
                    "facility": "PHC",
                    "visit_type": "Referral Preparation",
                    "patient_reported_symptoms": "à¬›à¬¾à¬¤à¬¿à¬°à­‡ à¬ªà­à¬°à¬¬à¬³ à¬¯à¬¨à­à¬¤à­à¬°à¬£à¬¾ à¬¹à­‡à¬‰à¬›à¬¿ à¬à¬¬à¬‚ à¬¬à¬¾à¬® à¬¹à¬¾à¬¤à¬•à­ à¬¯à¬¨à­à¬¤à­à¬°à¬£à¬¾ à¬¬à­à­Ÿà¬¾à¬ªà­à¬›à¬¿, à¬ªà­à¬°à¬¬à¬³ à¬à¬¾à¬³ à¬¬à¬¾à¬¹à¬¾à¬°à­à¬›à¬¿à¥¤",
                    "timeline": [
                        {"day": "Day 1", "description": "Intermittent chest tightness after walking up hill."},
                        {"day": "Day 2 (Today)", "description": "Crushing central chest pain radiating to left arm with cold diaphoresis."}
                    ],
                    "available_report_data": [],
                    "reviewer_confirmed_summary": "Acute angina equivalent symptoms requiring urgent secondary evaluation.",
                    "outstanding_questions": ["Time since onset of acute ischemic symptoms"],
                    "review_signals": [
                        {"rule_id": "TRIAGE-R04", "signal": "Potential acute chest-pain or cardiovascular urgency signal", "source_text": "chest pain", "severity": "URGENT REVIEW", "timestamp": "08:15:00", "reviewer_confirmation_required": True, "status": "confirmed"}
                    ],
                    "reviewer_reason": "High suspicion of acute coronary event; transfer with ACLS capability.",
                    "reviewer_name": "Dr. S. Chen, MD",
                    "reviewer_role": "Medical Officer",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "footer_disclaimer": "AI-assisted organization of information. Not a diagnosis or treatment recommendation. Final referral decision is made by qualified healthcare staff."
                }),
            )

            case6 = TriageCase(
                synthetic_case_id="CLV-DEMO-006",
                language="en",
                facility_type="Company Clinic",
                visit_type="Follow-up",
                status="awaiting_review",
                queue_category="routine",
                queue_reason="Standard chronic care check-in",
                consent_status=True,
                approximate_age=39,
                gender="Male",
                context_notes="Corporate clinic annual health check-in.",
                raw_symptoms="Blood pressure check-up and renewal of maintenance medication prescription.",
                normalized_symptoms="Hypertension surveillance visit; adherence to anti-hypertensive medication reported good.",
                detected_language="English",
            )

            db.add_all([case1, case2, case3, case4, case5, case6])
            await db.commit()
            logger.info("6 synthetic public health triage cases seeded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan manager to ensure initial seed data and graceful resource teardown."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(upgrade_ownership)
        if settings.DEMO_MODE and settings.ENVIRONMENT != "production":
            await seed_initial_data()
    except Exception as e:
        logger.error("Database initialization failed", exc_info=True)
        raise

    yield

    # Clean shutdown of background resources
    from app.core.redis import close_redis_client
    await close_redis_client()


app = FastAPI(
    title=settings.APP_NAME,
    description="Next-generation healthcare intelligence and clinical decision support API.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Enable Prometheus Request Telemetry
app.add_middleware(PrometheusMiddleware)

# Configure Cross-Origin Resource Sharing (CORS)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register Standardized Error Envelopes
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint welcoming clients."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "version": "0.1.0",
        "status": "online",
    }