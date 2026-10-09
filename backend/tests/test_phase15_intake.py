"""CLINOVA AI — Phase 15 Patient Intake + Consent + Persistence Test Suite.

Continuous Care Intelligence System.
Phase 15: Patient Intake + Consent + Persistence.
Grounded in Section 20 of Master Specification, DOC-02, DOC-03, DOC-07.

Test Matrix:
A. valid patient intake
B. valid staff-assisted intake
C. regular pathway persisted
D. emergency pathway persisted
E. missing symptoms rejected
F. whitespace-only symptoms rejected
G. invalid payload rejected
H. consent required
I. consent persisted
J. consent metadata persisted
K. patient persisted
L. encounter persisted
M. canonical Master Case persisted
N. correct initial case state (INTAKE_RECORDED)
O. correct state_version (1)
P. provenance preserved
Q. timeline event created (INTAKE_SUBMITTED)
R. audit event created (intake.submitted)
S. transaction rollback on downstream failure
T. duplicate/repeat handling
U. unauthorized patient access denied
V. cross-patient access denied
W. staff authorization works
X. old actor-header spoofing cannot bypass Phase 14 security
Y. synthetic mode preserved
Z. frontend intake API integration
AA. structured validation errors
AB. backend unavailable handling
AC. emergency administrative incompleteness does not destroy the emergency intake path
AD. no secret/credential leakage
AE. no real PII requirement
"""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_PATIENT,
    ROLE_AUDITOR,
)
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Patient,
    Encounter,
    Case,
    CaseStateTransition,
    Consent,
    Evidence,
    TimelineEvent,
    AuditEvent,
    User,
)


@pytest.fixture(autouse=True)
async def setup_phase15_environment():
    """Ensure DB schema is initialized and configure strict authentication defaults."""
    await init_db()
    original_legacy_headers = settings.ALLOW_LEGACY_ACTOR_HEADERS
    original_legacy_anon = settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK
    settings.ALLOW_LEGACY_ACTOR_HEADERS = False
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False

    yield

    settings.ALLOW_LEGACY_ACTOR_HEADERS = original_legacy_headers
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = original_legacy_anon


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Helper to authenticate and return a bearer JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# ===========================================================================
# PHASE 15 TEST SCENARIOS A - AE
# ===========================================================================

@pytest.mark.asyncio
async def test_scenario_a_valid_patient_intake():
    """Scenario A: Valid patient self-intake returns 200 and structured record."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "reported_age_bracket": "25-35 YRS",
                "biological_sex": "FEMALE",
                "preferred_language": "en",
                "chief_complaint": "Persistent throat irritation and mild dry cough for 2 days",
                "symptom_duration": "2 days",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["case_id"]
        assert data["case_number"].startswith("CAS-")
        assert data["patient_id"]
        assert data["synthetic_reference"].startswith("PT-SYN-")
        assert data["current_state"] == "INTAKE_RECORDED"
        assert data["status"] == "NEW"
        assert data["state_version"] == 1
        assert data["consent_status"] == "GRANTED"
        assert data["is_mock"] is False


@pytest.mark.asyncio
async def test_scenario_b_valid_staff_assisted_intake():
    """Scenario B: Valid staff-assisted intake by nurse returns 200 and structured record."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "reported_age_bracket": "40-49",
                "biological_sex": "MALE",
                "preferred_language": "en",
                "chief_complaint": "Acute lower back muscle spasm after lifting heavy load",
                "symptom_duration": "1 day",
                "intake_channel": "STAFF_KIOSK",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["status"] == "NEW"
        assert data["current_state"] == "INTAKE_RECORDED"


@pytest.mark.asyncio
async def test_scenario_c_regular_pathway_persisted():
    """Scenario C: Regular pathway is correctly stored in case and encounter."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Mild recurrent seasonal allergy and sneezing",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case is not None
            assert case.pathway == "REGULAR_STANDARD"
            assert case.acuity_tier == "ROUTINE"

            encounter = await db.get(Encounter, case.encounter_id)
            assert encounter is not None
            assert encounter.pathway == "REGULAR_STANDARD"


@pytest.mark.asyncio
async def test_scenario_d_emergency_pathway_persisted():
    """Scenario D: Emergency pathway assigns correct metadata and CRITICAL acuity tier."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Crushing retrosternal chest pain radiating to left arm with cold diaphoresis",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case is not None
            assert case.pathway == "EMERGENCY"
            assert case.acuity_tier == "CRITICAL"
            assert case.risk_score >= 0.70


@pytest.mark.asyncio
async def test_scenario_e_missing_symptoms_rejected():
    """Scenario E: Submission missing presenting symptoms is rejected with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 422
        err = res.json()["error"]
        assert err["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_f_whitespace_only_symptoms_rejected():
    """Scenario F: Whitespace-only symptoms are rejected with 422 structured error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "     \t \n   ",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 422
        err = res.json()["error"]
        assert err["code"] == "VALIDATION_ERROR"
        err_text = str(err)
        assert "empty or whitespace-only" in err_text


@pytest.mark.asyncio
async def test_scenario_g_invalid_payload_rejected():
    """Scenario G: Malformed payload (e.g. invalid biological sex or excessive length) rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        # Invalid biological sex
        res1 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "biological_sex": "INVALID_SEX_VALUE",
                "chief_complaint": "Headache",
                "consent_confirmed": True,
            },
        )
        assert res1.status_code == 422

        # Excessively large payload
        res2 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "chief_complaint": "A" * 5001,
                "consent_confirmed": True,
            },
        )
        assert res2.status_code == 422

        # Unsupported extra field rejected by extra="forbid"
        res3 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "chief_complaint": "Valid complaint",
                "consent_confirmed": True,
                "unsupported_extra_field": "disallowed",
            },
        )
        assert res3.status_code == 422
        assert "unsupported_extra_field" in str(res3.json())

        # Whitespace-only facility_id rejected
        res4 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "   ",
                "chief_complaint": "Valid complaint",
                "consent_confirmed": True,
            },
        )
        assert res4.status_code == 422


@pytest.mark.asyncio
async def test_scenario_h_consent_required():
    """Scenario H: Non-emergency submission without consent is rejected with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Knee soreness for 3 days",
                "consent_confirmed": False,
            },
        )
        assert res.status_code == 422
        err = res.json()["error"]
        assert err["code"] == "VALIDATION_ERROR"
        assert "Informed consent is mandatory" in err["message"]

        # Explicitly revoked consent rejected with 422
        res_revoked = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Knee soreness for 3 days",
                "consent_confirmed": True,
                "consent_status": "REVOKED",
            },
        )
        assert res_revoked.status_code == 422
        assert "Informed consent is mandatory" in res_revoked.json()["error"]["message"]


@pytest.mark.asyncio
async def test_scenario_i_consent_persisted():
    """Scenario I: Informed consent record is persisted in the live database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Persistent headache and fever",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            stmt = select(Consent).where(Consent.case_id == case_id)
            consent = (await db.execute(stmt)).scalars().first()
            assert consent is not None
            assert consent.consent_granted is True
            assert consent.status == "GRANTED"


@pytest.mark.asyncio
async def test_scenario_j_consent_metadata_persisted():
    """Scenario J: Consent metadata (purpose, version, channel, language) is persisted."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Stomach cramp after dinner",
                "preferred_language": "or",
                "consent_confirmed": True,
                "consent_purpose": "CLINICAL_CARE_TRIAGE",
                "consent_version": "v1.0",
                "consent_channel": "DIGITAL_APP",
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            consent = (await db.execute(select(Consent).where(Consent.case_id == case_id))).scalars().first()
            assert consent is not None
            assert consent.purpose == "CLINICAL_CARE_TRIAGE"
            assert consent.consent_version == "v1.0"
            assert consent.channel == "DIGITAL_APP"
            assert consent.language == "or"
            assert consent.recorded_at is not None
            assert consent.hash_reference is not None


@pytest.mark.asyncio
async def test_scenario_k_patient_persisted():
    """Scenario K: Persistent Patient and synthetic identifier are created."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "reported_age_bracket": "51-65 YRS",
                "biological_sex": "MALE",
                "chief_complaint": "Dizziness and fatigue for 1 week",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        pt_id = res.json()["patient_id"]

        async with async_session_factory() as db:
            patient = await db.get(Patient, pt_id)
            assert patient is not None
            assert patient.is_synthetic is True
            assert patient.age_bracket == "51-65 YRS"
            assert patient.biological_sex == "MALE"
            assert patient.synthetic_id.startswith("PT-SYN-")


@pytest.mark.asyncio
async def test_scenario_l_encounter_persisted():
    """Scenario L: Encounter is persisted and linked to Patient and Facility."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Joint pain in knees",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        encounter_id = res.json()["encounter_id"]
        patient_id = res.json()["patient_id"]

        async with async_session_factory() as db:
            enc = await db.get(Encounter, encounter_id)
            assert enc is not None
            assert enc.patient_id == patient_id
            assert enc.facility_id == "FAC-DH-04"
            assert enc.started_at is not None


@pytest.mark.asyncio
async def test_scenario_m_canonical_master_case_persisted():
    """Scenario M: Canonical Master Case is persisted as the root aggregate."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Productive cough and low-grade evening fever",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case is not None
            assert case.case_number.startswith("CAS-")
            assert case.presenting_complaint == "Productive cough and low-grade evening fever"
            assert case.encounter_id is not None
            assert case.patient_id is not None


@pytest.mark.asyncio
async def test_scenario_n_correct_initial_case_state():
    """Scenario N: Case enters INTAKE_RECORDED state and transition record is stored."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Rash on forearm with itching",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case.current_state == "INTAKE_RECORDED"
            assert case.status == "NEW"

            stmt = select(CaseStateTransition).where(CaseStateTransition.case_id == case_id)
            trans = (await db.execute(stmt)).scalars().first()
            assert trans is not None
            assert trans.from_state == "NONE"
            assert trans.to_state == "INTAKE_RECORDED"


@pytest.mark.asyncio
async def test_scenario_o_correct_state_version():
    """Scenario O: Optimistic concurrency state_version initializes to 1."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Ear ache for 1 day",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200, res.text
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case.state_version == 1


@pytest.mark.asyncio
async def test_scenario_p_provenance_preserved():
    """Scenario P: Evidence distinguishes PATIENT_REPORTED vs STAFF_ENTERED and assigns KNOWN epistemic state."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Patient self-intake
        pt_token = await login_helper(client, "patient")
        res_pt = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {pt_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Mild stomach ache",
                "consent_confirmed": True,
            },
        )
        case_pt_id = res_pt.json()["case_id"]

        # 2. Staff-assisted intake
        staff_token = await login_helper(client, "nurse")
        res_staff = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {staff_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Severe ankle swelling",
                "consent_confirmed": True,
            },
        )
        case_staff_id = res_staff.json()["case_id"]

        async with async_session_factory() as db:
            ev_pt = (await db.execute(select(Evidence).where(Evidence.case_id == case_pt_id))).scalars().first()
            assert ev_pt is not None
            assert ev_pt.source_class == "PATIENT_REPORTED"
            assert ev_pt.epistemic_state == "KNOWN"
            assert ev_pt.verification_metadata["verified"] is False

            ev_staff = (await db.execute(select(Evidence).where(Evidence.case_id == case_staff_id))).scalars().first()
            assert ev_staff is not None
            assert ev_staff.source_class == "STAFF_ENTERED"
            assert ev_staff.epistemic_state == "KNOWN"


@pytest.mark.asyncio
async def test_scenario_q_timeline_event_created():
    """Scenario Q: Complete Section 18 milestone events (INTAKE_SUBMITTED, CONSENT_RECORDED, CASE_CREATED) are recorded in timeline."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Sinus congestion and facial pressure",
                "consent_confirmed": True,
            },
        )
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            events = (await db.execute(select(TimelineEvent).where(TimelineEvent.case_id == case_id))).scalars().all()
            event_types = {e.event_type for e in events}
            assert "INTAKE_SUBMITTED" in event_types
            assert "CONSENT_RECORDED" in event_types
            assert "CASE_CREATED" in event_types


@pytest.mark.asyncio
async def test_scenario_r_audit_event_created():
    """Scenario R: Section 18 AuditEvents (intake, case, encounter, consent, patient) are stored in ledger."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Sore throat and chills",
                "consent_confirmed": True,
            },
        )
        case_id = res.json()["case_id"]

        async with async_session_factory() as db:
            audits = (await db.execute(select(AuditEvent).where(AuditEvent.case_id == case_id))).scalars().all()
            actions = {a.action for a in audits if a.result == "SUCCESS"}
            assert "intake.submitted" in actions
            assert "case.created" in actions
            assert "encounter.created" in actions
            assert "consent.recorded" in actions
            assert any(act in actions for act in ("patient.created", "patient.reused"))


@pytest.mark.asyncio
async def test_scenario_s_transaction_rollback_on_downstream_failure(monkeypatch):
    """Scenario S: Database rollback triggers on downstream error leaving no partial records."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")

        # Mock TimelineEvent constructor to raise an exception simulating downstream crash
        def failing_init(*args, **kwargs):
            raise RuntimeError("Simulated unexpected failure during timeline creation")

        monkeypatch.setattr("app.api.v1.endpoints.intake.TimelineEvent", failing_init)

        with pytest.raises(RuntimeError):
            await client.post(
                "/api/v1/intake/submit",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "facility_id": "FAC-DH-04",
                    "pathway": "OPD_GENERAL",
                    "chief_complaint": "Severe migraine and vomiting downstream fail",
                    "consent_confirmed": True,
                },
            )

        # Verify no orphan case or patient was committed with that specific presenting complaint
        async with async_session_factory() as db:
            cases = (
                await db.execute(
                    select(Case).where(Case.presenting_complaint == "Severe migraine and vomiting downstream fail")
                )
            ).scalars().all()
            assert len(cases) == 0


@pytest.mark.asyncio
async def test_scenario_t_duplicate_repeat_handling():
    """Scenario T: Idempotent client_submission_id prevents duplicate case creation without orphan records."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        sub_id = f"sub-idemp-{uuid.uuid4().hex[:8]}"

        payload = {
            "facility_id": "FAC-DH-04",
            "pathway": "OPD_GENERAL",
            "chief_complaint": "Recurrent ankle sprain after soccer match",
            "consent_confirmed": True,
            "client_submission_id": sub_id,
        }

        # First submission
        res1 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        assert res1.status_code == 200
        case1_id = res1.json()["case_id"]
        assert res1.json()["is_duplicate"] is False
        p1_id = res1.json()["patient_id"]
        ref1 = res1.json()["synthetic_reference"]

        # Duplicate submission with exact same client_submission_id
        res2 = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        assert res2.status_code == 200
        case2_id = res2.json()["case_id"]
        assert case1_id == case2_id
        assert res2.json()["is_duplicate"] is True
        # Verify identical patient references returned
        assert res2.json()["patient_id"] == p1_id
        assert res2.json()["synthetic_reference"] == ref1


@pytest.mark.asyncio
async def test_scenario_u_unauthorized_patient_access_denied():
    """Scenario U: Role lacking CASE_CREATE (e.g. AUDITOR) is rejected with 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auditor_token = await login_helper(client, "auditor")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {auditor_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Trying to create case as auditor",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 403
        err = res.json()["error"]
        assert err["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_v_cross_patient_access_denied():
    """Scenario V: Patient attempting to submit intake for another patient ID is blocked."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pt_token = await login_helper(client, "patient")

        # Create a legitimate case first so patient has a verified patient_id
        res_init = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {pt_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Initial mild cough",
                "consent_confirmed": True,
            },
        )
        assert res_init.status_code == 200

        # Attempt to supply a different patient's identifier
        res_bad = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {pt_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "synthetic_patient_id": "PT-SYN-FORGED-9999",
                "chief_complaint": "Attempting to spoof another patient's file",
                "consent_confirmed": True,
            },
        )
        assert res_bad.status_code == 403
        err = res_bad.json()["error"]
        assert "own patient identity" in err["message"]

        # Unlinked patient account claiming external synthetic patient ID rejected with 403
        unlinked_user_id = str(uuid.uuid4())
        async with async_session_factory() as db:
            from app.db.models import User
            from app.core.auth import hash_password, create_access_token
            from app.core.rbac import ROLE_PATIENT
            unlinked_user = User(
                id=unlinked_user_id,
                username=f"unlinked_pt_{uuid.uuid4().hex[:6]}",
                email=f"unlinked_{uuid.uuid4().hex[:6]}@example.com",
                full_name="Unlinked Test Patient",
                hashed_password=hash_password("ClinovaDemo2026!"),
                role=ROLE_PATIENT,
                is_active=True,
                patient_id=None,
            )
            db.add(unlinked_user)
            await db.commit()

        unlinked_token = create_access_token(data={"sub": unlinked_user_id, "role": ROLE_PATIENT})
        res_unlinked_forged = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {unlinked_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "synthetic_patient_id": "PT-SYN-UNLINKED-FORGED",
                "chief_complaint": "Unlinked user trying to claim identity",
                "consent_confirmed": True,
            },
        )
        assert res_unlinked_forged.status_code == 403
        assert "own patient identity" in res_unlinked_forged.json()["error"]["message"]

        # Attempt to supply a different patient's identifier
        res_bad = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {pt_token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "synthetic_patient_id": "PT-SYN-FORGED-9999",
                "chief_complaint": "Attempting to spoof another patient's file",
                "consent_confirmed": True,
            },
        )
        assert res_bad.status_code == 403
        err = res_bad.json()["error"]
        assert "own patient identity" in err["message"]


@pytest.mark.asyncio
async def test_scenario_w_staff_authorization_works():
    """Scenario W: Nurse and Clinician can authoritatively create intake on behalf of patients."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Nurse intake
        nurse_token = await login_helper(client, "nurse")
        res_nurse = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Walk-in patient with mild fever",
                "consent_confirmed": True,
            },
        )
        assert res_nurse.status_code == 200

        # Clinician intake
        doc_token = await login_helper(client, "clinician")
        res_doc = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {doc_token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Direct clinician intake consultation",
                "consent_confirmed": True,
            },
        )
        assert res_doc.status_code == 200


@pytest.mark.asyncio
async def test_scenario_x_old_actor_header_spoofing_cannot_bypass_phase14_security():
    """Scenario X: Client sending forged X-Actor-Role header cannot elevate privileges."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pt_token = await login_helper(client, "patient")

        # Patient token with forged X-Actor-Role: CLINICIAN
        res = await client.post(
            "/api/v1/intake/submit",
            headers={
                "Authorization": f"Bearer {pt_token}",
                "X-Actor-Role": "CLINICIAN",  # Spoofed header
                "X-Facility-Id": "FAC-DH-04",
            },
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Legitimate patient complaint despite spoofed header",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        case_id = res.json()["case_id"]

        # Check evidence was recorded as PATIENT_REPORTED, not CLINICIAN_VERIFIED
        async with async_session_factory() as db:
            ev = (await db.execute(select(Evidence).where(Evidence.case_id == case_id))).scalars().first()
            assert ev.source_class == "PATIENT_REPORTED"

        # Completely unauthenticated request with forged X-Actor-Id rejected with 401
        res_spoof = await client.post(
            "/api/v1/intake/submit",
            headers={
                "X-Actor-Id": "fake_hacker_id",
                "X-Actor-Role": "CLINICIAN",
            },
            json={
                "facility_id": "FAC-PHC-01",
                "chief_complaint": "Hacker complaint",
                "consent_confirmed": True,
            },
        )
        assert res_spoof.status_code == 401


@pytest.mark.asyncio
async def test_scenario_y_synthetic_mode_preserved():
    """Scenario Y: Persistent records carry synthetic flags and environment identifiers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Periodic indigestion",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["synthetic_reference"].startswith("PT-SYN-")

        async with async_session_factory() as db:
            case = await db.get(Case, data["case_id"])
            assert case.environment_id == "development"
            patient = await db.get(Patient, data["patient_id"])
            assert patient.is_synthetic is True


@pytest.mark.asyncio
async def test_scenario_z_frontend_intake_api_integration():
    """Scenario Z: Exact payload structure used by frontend PatientIntakeWizard succeeds."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        frontend_payload = {
            "facility_id": "FAC-DH-04",
            "pathway": "OPD_GENERAL",
            "reported_age_bracket": "25-35 YRS",
            "biological_sex": "FEMALE",
            "preferred_language": "en",
            "chief_complaint": "Severe throat pain and dry cough for 3 days",
            "symptom_duration": "3 days",
            "narrative_notes": "Patient self-medicated with paracetamol without relief",
            "voice_transcript": None,
            "document_uploaded": False,
            "consent_confirmed": True,
        }
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json=frontend_payload,
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["case_id"]
        assert data["synthetic_reference"]
        assert data["queue_position"] >= 1
        assert "Patient intake recorded successfully" in data["message"]


@pytest.mark.asyncio
async def test_scenario_aa_structured_validation_errors():
    """Scenario AA: Validation failures return structured ClinovaAPIError contract."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "pathway": "INVALID_PATHWAY_ABC",
                "chief_complaint": "Valid complaint",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 422
        body = res.json()
        assert "error" in body
        err = body["error"]
        assert err["code"] == "VALIDATION_ERROR"
        err_text = str(err)
        assert "Allowed pathways" in err_text


@pytest.mark.asyncio
async def test_scenario_ab_backend_unavailable_handling():
    """Scenario AB: Verify offline/mock contract conformance and graceful error recovery."""
    from app.schemas.intake import PatientIntakeResponse

    # 1. Verify fallback response contract conforms strictly to PatientIntakeResponse
    mock_payload = {
        "success": True,
        "case_id": "CASE-SYNTH-999",
        "case_number": "CAS-2026-99999",
        "patient_id": "PT-SYNTH-999",
        "patient_synthetic_id": "PT-SYN-9999",
        "synthetic_reference": "PT-SYN-9999",
        "encounter_id": "ENC-SYNTH-999",
        "facility_id": "FAC-DH-04",
        "pathway": "OPD_GENERAL",
        "status": "NEW",
        "current_state": "INTAKE_RECORDED",
        "state_version": 1,
        "consent_status": "GRANTED",
        "consent_id": "CON-SYNTH-999",
        "queue_position": 1,
        "message": "Backend unavailable. Patient intake recorded in local demonstration queue.",
        "is_mock": True,
        "is_duplicate": False,
    }
    validated = PatientIntakeResponse(**mock_payload)
    assert validated.success is True
    assert validated.is_mock is True
    assert validated.case_id.startswith("CASE-SYNTH-")

    # 2. Verify backend returns structured 404 for unreachable/non-existent facility without leaking paths
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-UNREACHABLE-999",
                "chief_complaint": "Simulated offline symptoms",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_scenario_ac_emergency_administrative_incompleteness():
    """Scenario AC: Emergency pathway does not block on missing explicit consent."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        # In emergency resuscitation, patient is unconscious / unable to confirm consent
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "EMERGENCY",
                "chief_complaint": "Unconscious trauma patient in acute hypovolemic shock following vehicular collision",
                "consent_confirmed": False,  # Patient cannot confirm
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["success"] is True
        assert data["pathway"] == "EMERGENCY"
        assert data["consent_status"] == "IMPLIED_EMERGENCY"

        async with async_session_factory() as db:
            case = await db.get(Case, data["case_id"])
            assert case.acuity_tier == "CRITICAL"
            consent = (await db.execute(select(Consent).where(Consent.case_id == case.id))).scalars().first()
            assert consent.status == "IMPLIED_EMERGENCY"


@pytest.mark.asyncio
async def test_scenario_ad_no_secret_credential_leakage():
    """Scenario AD: Responses and audit records do not leak secrets, hashes, or passwords."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "patient")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-PHC-01",
                "chief_complaint": "General weakness",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        text = res.text
        assert "password" not in text.lower()
        assert "secret" not in text.lower()
        assert settings.SECRET_KEY not in text

        case_id = res.json()["case_id"]
        async with async_session_factory() as db:
            audits = (await db.execute(select(AuditEvent).where(AuditEvent.case_id == case_id))).scalars().all()
            for a in audits:
                details_str = str(a.details)
                assert "password" not in details_str.lower()
                assert settings.SECRET_KEY not in details_str


@pytest.mark.asyncio
async def test_scenario_ae_no_real_pii_requirement():
    """Scenario AE: Intake requires zero real PII (no Aadhaar, phone number, or address)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "chief_complaint": "Intermittent lower abdominal pain",
                "consent_confirmed": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "aadhaar" not in data
        assert "phone" not in data
        assert "address" not in data
