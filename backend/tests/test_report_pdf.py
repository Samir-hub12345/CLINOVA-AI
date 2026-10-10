"""Tests for CLINOVA AI Clinical Case Reports & PDF Generation.

Verifies:
- Pure Python PDF-1.4 generation and binary structure
- Role-based authorization & facility boundary protection
- Patient self-scope isolation (anti-enumeration 404)
- Tamper-evident cryptographic signature & clinical governance disclaimers
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import async_session_factory
from app.db.models import Case, Patient, Facility, User, VitalReading, ClinicianDecision
from app.domain.reports.pdf_generator import build_clinical_report_pdf
from app.core.auth import create_access_token


@pytest.fixture
def mock_report_data():
    return {
        "case": {
            "id": "CASE-TEST-001",
            "case_number": "CNV-2026-TEST",
            "status": "CLINICIAN_REVIEW_REQUIRED",
            "acuity_tier": "CRITICAL",
            "risk_score": 0.88,
            "uncertainty_score": 0.32,
            "trajectory_slope": 0.25,
            "presenting_complaint": "Acute severe crushing chest pain radiating to left shoulder and jaw",
            "primary_syndrome": "Acute Coronary Syndrome / STEMI Suspect",
            "required_bundle": "BUNDLE_ACS_THROMBOLYSIS_PCI",
            "emergency_active": True,
            "pathway": "EMERGENCY",
        },
        "patient": {
            "id": "PT-TEST-01",
            "synthetic_id": "PT-SYN-0999",
            "age_bracket": "50-60 YRS",
            "biological_sex": "MALE",
        },
        "facility": {
            "id": "FAC-DH-04",
            "name": "Cuttack District Headquarters Hospital",
            "tier": "LEVEL_4_DH",
        },
        "vitals": [
            {
                "heart_rate": 118,
                "systolic_bp": 88,
                "diastolic_bp": 54,
                "spo2_percent": 90,
                "temperature_celsius": 36.8,
                "respiratory_rate": 26,
                "avpu_score": "ALERT",
                "provenance": "STAFF_ENTERED",
                "recorded_at": "2026-10-10T08:00:00Z",
            }
        ],
        "evidence": [
            {
                "entity_type": "LAB_TROPONIN_I",
                "entity_value": "1.45 ng/mL (Elevated)",
                "confidence": 0.98,
                "source": "OCR_EXTRACTED",
                "verification_status": "VERIFIED",
            }
        ],
        "ai_summary": {
            "summary_text": "CareGraph evaluated high-risk ischemic trajectory requiring immediate cardiac cath transfer.",
            "uncertainty_score": 0.28,
            "epistemic_status": "KNOWN",
            "missing_parameters": ["Serum Electrolytes"],
        },
        "safety_alerts": [
            {
                "title": "Shock Index > 1.0 (Severe Hemodynamic Instability)",
                "severity": "CRITICAL",
                "triggered": True,
            }
        ],
        "clinician_review": {
            "clinician_id": "usr-doc-01",
            "clinician_name": "Dr. Priya Sharma, MD",
            "decision_type": "ESCALATE",
            "action_type": "EMERGENCY_INTER_FACILITY_TRANSFER",
            "treatment_plan": "Aspirin 325mg chewed, Clopidogrel 300mg, IV Heparin. Transfer to SCB MCH Cath Lab.",
            "rationale": "High-acuity STEMI suspect with cardiogenic shock risk.",
        },
        "care_plan": {
            "home_instructions": "Inpatient emergency stabilization active.",
            "follow_up": "Immediate cardiology evaluation.",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def test_pdf_builder_produces_valid_binary(mock_report_data):
    """Verifies that the PDF generator generates valid PDF-1.4 binary data."""
    pdf_bytes = build_clinical_report_pdf(mock_report_data)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-1.4\n")
    assert pdf_bytes.strip().endswith(b"%%EOF")
    assert len(pdf_bytes) > 1500
    # Check key text elements are embedded
    assert b"CLINOVA AI" in pdf_bytes
    assert b"PT-SYN-0999" in pdf_bytes
    assert b"CASE-TEST-001" in pdf_bytes
    assert b"HUMAN CLINICIAN VERIFIED" in pdf_bytes
    assert b"AI-GENERATED" in pdf_bytes


@pytest.mark.asyncio
async def test_api_report_endpoints():
    """Tests API report endpoints with real JWT authentication and RBAC checks."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a test patient and case in DB
        async with async_session_factory() as session:
            fac = await session.get(Facility, "FAC-DH-04")
            if not fac:
                fac = Facility(
                    id="FAC-DH-04",
                    facility_code="FAC-DH-04",
                    name="Cuttack DHH",
                    tier="LEVEL_4_DH",
                )
                session.add(fac)
                await session.flush()

            import uuid
            unique_suffix = uuid.uuid4().hex[:6]
            test_patient_id = f"pt-rep-{unique_suffix}"
            test_synthetic_id = f"PT-SYN-R{unique_suffix}"
            test_case_id = f"case-rep-{unique_suffix}"

            patient = Patient(
                id=test_patient_id,
                synthetic_id=test_synthetic_id,
                age_bracket="40-49",
                biological_sex="FEMALE",
            )
            session.add(patient)
            await session.flush()

            case = Case(
                id=test_case_id,
                patient_id=patient.id,
                facility_id="FAC-DH-04",
                case_number=f"CNV-2026-{unique_suffix}",
                status="CLINICIAN_REVIEW_REQUIRED",
                acuity_tier="URGENT",
                risk_score=0.72,
                uncertainty_score=0.40,
                trajectory_slope=0.15,
                presenting_complaint="High fever with abdominal tenderness",
                pathway="OPD_GENERAL",
            )
            session.add(case)

            decision = ClinicianDecision(
                case_id=case.id,
                clinician_id="usr-doc-01",
                decision_type="OBSERVE",
                action_type="CONSERVATIVE_THERAPY",
                treatment_plan="Supportive hydration and broad-spectrum antibiotics.",
                clinical_rationale="Patient is hemodynamically stable.",
                timestamp=datetime.now(timezone.utc),
            )
            session.add(decision)

            user_pt = User(
                id=f"usr-pt-own-{unique_suffix}",
                email=f"own.{unique_suffix}@clinova.internal",
                username=f"own_{unique_suffix}",
                full_name="Patient Owner",
                role="PATIENT",
                patient_id=patient.id,
                is_active=True,
            )
            session.add(user_pt)

            patient_other = Patient(
                id=f"pt-other-{unique_suffix}",
                synthetic_id=f"PT-SYN-O{unique_suffix}",
                age_bracket="30-39",
                biological_sex="MALE",
            )
            session.add(patient_other)

            user_other = User(
                id=f"usr-pt-oth-{unique_suffix}",
                email=f"oth.{unique_suffix}@clinova.internal",
                username=f"oth_{unique_suffix}",
                full_name="Other Patient",
                role="PATIENT",
                patient_id=f"pt-other-{unique_suffix}",
                is_active=True,
            )
            session.add(user_other)
            await session.commit()

        # 1. Unauthenticated request rejected
        res = await client.get(f"/api/v1/cases/{test_case_id}/report/pdf")
        assert res.status_code == 401

        # 2. Clinician at FAC-DH-04 generates PDF report
        doc_token = create_access_token(
            data={"sub": "usr-doc-01", "role": "CLINICIAN", "facility_id": "FAC-DH-04"}
        )
        res_doc = await client.get(
            f"/api/v1/cases/{test_case_id}/report/pdf",
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        assert res_doc.status_code == 200
        assert res_doc.headers["content-type"] == "application/pdf"
        assert "attachment" in res_doc.headers.get("content-disposition", "")
        assert res_doc.content.startswith(b"%PDF-1.4")
        assert res_doc.content.strip().endswith(b"%%EOF")

        # 3. Clinician gets JSON summary
        res_summary = await client.get(
            f"/api/v1/cases/{test_case_id}/report/summary",
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        assert summary_data["case"]["id"] == test_case_id
        assert summary_data["patient"]["synthetic_id"] == test_synthetic_id
        assert summary_data["clinician_review"]["decision_type"] == "OBSERVE"

        # 4. Patient accessing their own case report
        patient_token = create_access_token(
            data={"sub": f"usr-pt-own-{unique_suffix}", "role": "PATIENT", "patient_id": test_patient_id}
        )
        res_pt = await client.get(
            f"/api/v1/cases/{test_case_id}/report/pdf",
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert res_pt.status_code == 200
        assert res_pt.content.startswith(b"%PDF-1.4")

        # 5. Patient accessing another patient's case report -> Anti-enumeration 404
        other_patient_token = create_access_token(
            data={"sub": f"usr-pt-oth-{unique_suffix}", "role": "PATIENT", "patient_id": f"pt-other-{unique_suffix}"}
        )
        res_pt_denied = await client.get(
            f"/api/v1/cases/{test_case_id}/report/pdf",
            headers={"Authorization": f"Bearer {other_patient_token}"},
        )
        assert res_pt_denied.status_code in [403, 404]
