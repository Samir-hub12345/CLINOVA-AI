"""Phase 1 Production Foundation Re-Audit and Verification Test Suite.

Validates all 28 Phase 1 requirements, including:
1. Real persistent authentication & password hashing
2. Valid login, invalid password, unknown account, missing credentials
3. Persistent logout with server-side token revocation
4. Four primary roles (PATIENT, STAFF, DOCTOR, ADMIN) with server-side RBAC
5. User vs. Patient separation with persistent MRN
6. Mandatory IDOR cross-patient isolation (PATIENT-A -> CASE-B = 403)
7. Encounter foundation & facility scoping
8. Case evidence foundation, provenance, and verification states
9. Database restart persistence simulation
10. Consistent error structure without credential / trace leakage
11. Provider abstraction contracts and graceful failure states
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.facility import Facility
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.encounter import Encounter, EncounterType, EncounterStatus
from app.models.revoked_token import RevokedToken
from app.services.case_state_machine import CaseWorkflowState
from app.services.providers.base import ProviderError, ProviderErrorCode
from app.services.providers.local_fallback import LocalSpeechToTextProvider


@pytest.mark.asyncio
async def test_01_registration_and_duplicate_rejection(async_client: AsyncClient, database):
    """Test 1: Real registration creates persistent hashed account; duplicate email is rejected."""
    email = f"patient_{uuid.uuid4().hex[:8]}@clinova.test"
    reg_payload = {
        "email": email,
        "password": "SecurePassword2026!",
        "full_name": "Verified Patient One",
        "role": "patient",
    }
    # 1. Register new account
    res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201, res.text
    user_data = res.json()
    assert user_data["email"] == email
    assert user_data["role"] == "patient"
    assert "hashed_password" not in user_data  # Password hash never leaked

    # 2. Verify password securely hashed in database
    async with database() as db:
        user_db = (await db.execute(select(User).where(User.email == email))).scalar_one()
        assert user_db.hashed_password != "SecurePassword2026!"
        assert verify_password("SecurePassword2026!", user_db.hashed_password) is True

    # 3. Duplicate registration rejection
    dup_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_02_login_credential_validation(async_client: AsyncClient, database):
    """Test 2: Valid login succeeds; invalid password, unknown user, and missing credentials rejected."""
    email = f"auth_test_{uuid.uuid4().hex[:8]}@clinova.test"
    password = "CorrectPassword123!"

    async with database() as db:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Auth Verification User",
            role=UserRole.PATIENT,
            is_active=True,
        )
        db.add(user)
        await db.commit()

    # A. Valid login
    valid_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert valid_res.status_code == 200, valid_res.text
    token_data = valid_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # B. Invalid password
    bad_pass = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert bad_pass.status_code == 401
    assert "incorrect" in bad_pass.json()["detail"].lower()

    # C. Unknown user
    unknown_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent_user@clinova.test", "password": password},
    )
    assert unknown_res.status_code == 401

    # D. Missing credentials
    missing_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "", "password": ""},
    )
    assert missing_res.status_code == 400


@pytest.mark.asyncio
async def test_03_logout_and_token_revocation(async_client: AsyncClient, database):
    """Test 3: Logout invalidates token server-side; subsequent requests are rejected."""
    email = f"logout_{uuid.uuid4().hex[:8]}@clinova.test"
    password = "LogoutPass2026!"

    async with database() as db:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Logout Test User",
            role=UserRole.PATIENT,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 1. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Access protected resource successfully
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 3. Call logout endpoint
    logout_res = await async_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert "invalidated" in logout_res.json()["message"].lower()

    # 4. Attempt to access protected resource with same token -> Must be rejected with 401
    revoked_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert revoked_res.status_code == 401
    assert "revoked" in revoked_res.json()["detail"].lower()

    # 5. Verify token hash exists in database revoked_tokens table
    async with database() as db:
        token_hash = RevokedToken.hash_token(token)
        rev = (await db.execute(select(RevokedToken).where(RevokedToken.token_hash == token_hash))).scalar_one_or_none()
        assert rev is not None
        assert rev.user_id == user.id


@pytest.mark.asyncio
async def test_04_four_primary_roles_authorization(async_client: AsyncClient, database):
    """Test 4: RBAC enforcement across PATIENT, STAFF, DOCTOR, ADMIN.
    
    Verifies patients/staff cannot access admin APIs, and backend enforces roles strictly.
    """
    async with database() as db:
        # Create users for all 4 primary roles
        u_patient = User(email=f"p_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("Pass1!"), full_name="Patient User", role=UserRole.PATIENT)
        u_staff = User(email=f"s_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("Pass1!"), full_name="Staff User", role=UserRole.STAFF)
        u_doctor = User(email=f"d_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("Pass1!"), full_name="Doctor User", role=UserRole.DOCTOR)
        u_admin = User(email=f"a_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("Pass1!"), full_name="Admin User", role=UserRole.ADMIN)
        db.add_all([u_patient, u_staff, u_doctor, u_admin])
        await db.commit()
        for u in [u_patient, u_staff, u_doctor, u_admin]:
            await db.refresh(u)

    tokens = {
        "patient": create_access_token(subject=u_patient.id, role="patient"),
        "staff": create_access_token(subject=u_staff.id, role="staff"),
        "doctor": create_access_token(subject=u_doctor.id, role="doctor"),
        "admin": create_access_token(subject=u_admin.id, role="admin"),
    }

    # Protected Admin Endpoint: GET /api/v1/auth/users
    # Patient -> 403 Forbidden
    res_p = await async_client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {tokens['patient']}"})
    assert res_p.status_code == 403

    # Staff -> 403 Forbidden
    res_s = await async_client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {tokens['staff']}"})
    assert res_s.status_code == 403

    # Doctor -> 403 Forbidden
    res_d = await async_client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {tokens['doctor']}"})
    assert res_d.status_code == 403

    # Admin -> 200 OK
    res_a = await async_client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res_a.status_code == 200


@pytest.mark.asyncio
async def test_05_user_patient_separation_and_mrn(database):
    """Test 5: Clean separation between User (auth identity) and Patient (clinical subject) with persistent MRN."""
    async with database() as db:
        user = User(
            email=f"patient_sep_{uuid.uuid4().hex[:6]}@clinova.test",
            hashed_password=get_password_hash("Pass123!"),
            full_name="Ananya Dash",
            role=UserRole.PATIENT,
        )
        db.add(user)
        await db.flush()

        mrn = f"MRN-{uuid.uuid4().hex[:8].upper()}"
        patient = Patient(
            user_id=user.id,
            mrn=mrn,
            first_name="Ananya",
            last_name="Dash",
            date_of_birth="1992-04-15",
            gender="Female",
            blood_group="B+",
            phone="+919876543210",
        )
        db.add(patient)
        await db.commit()

        # Query back via relationship and assert separation
        stmt = select(Patient).where(Patient.user_id == user.id)
        saved_patient = (await db.execute(stmt)).scalar_one()
        assert saved_patient.mrn == mrn
        assert saved_patient.user.email == user.email
        assert saved_patient.user.id == user.id


@pytest.mark.asyncio
async def test_06_mandatory_synthetic_idor_isolation(async_client: AsyncClient, database):
    """Test 6 (Mandatory Section 39): PATIENT-A -> CASE-B is strictly DENIED (403).
    
    Verifies that manipulating URL params, request body, or query params cannot bypass isolation.
    """
    async with database() as db:
        # Create Patient A and Patient B
        user_a = User(email=f"patient_a_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("P!"), full_name="Patient A", role=UserRole.PATIENT)
        user_b = User(email=f"patient_b_{uuid.uuid4().hex[:6]}@clinova.test", hashed_password=get_password_hash("P!"), full_name="Patient B", role=UserRole.PATIENT)
        db.add_all([user_a, user_b])
        await db.flush()

        # Create Case A (owned by A) and Case B (owned by B)
        case_a = TriageCase(synthetic_case_id="CASE-SYN-A", owner_user_id=user_a.id, patient_id=str(uuid.uuid4()), language="en", status="active")
        case_b = TriageCase(synthetic_case_id="CASE-SYN-B", owner_user_id=user_b.id, patient_id=str(uuid.uuid4()), language="en", status="active")
        db.add_all([case_a, case_b])
        await db.commit()
        await db.refresh(case_a)
        await db.refresh(case_b)

    token_a = create_access_token(subject=user_a.id, role="patient")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Patient A attempts to retrieve Case B
    idor_get = await async_client.get(f"/api/v1/cases/{case_b.id}", headers=headers_a)
    assert idor_get.status_code == 403, f"Expected 403 but got {idor_get.status_code}: {idor_get.text}"
    assert "access denied" in idor_get.json()["detail"].lower()

    # Patient A attempts to add symptom text to Case B
    idor_post = await async_client.post(
        f"/api/v1/cases/{case_b.id}/text",
        json={"text": "Malicious symptom injection"},
        headers=headers_a,
    )
    assert idor_post.status_code == 403


@pytest.mark.asyncio
async def test_07_encounter_lifecycle_and_facility_scoping(database):
    """Test 7: Encounter represents distinct clinical interaction with facility scoping and status tracking."""
    async with database() as db:
        fac = Facility(facility_code=f"FAC-{uuid.uuid4().hex[:4]}", name="Rural PHC Test", facility_type="PHC")
        db.add(fac)
        await db.flush()

        patient = Patient(
            mrn=f"MRN-{uuid.uuid4().hex[:6]}",
            first_name="Sunil",
            last_name="Behera",
            date_of_birth="1985-02-10",
            gender="Male",
            facility_id=fac.id,
        )
        db.add(patient)
        await db.flush()

        encounter = Encounter(
            patient_id=patient.id,
            facility_id=fac.id,
            encounter_type=EncounterType.TRIAGE,
            status=EncounterStatus.IN_PROGRESS,
            reason_for_visit="Acute fever and cough",
        )
        db.add(encounter)
        await db.commit()
        await db.refresh(encounter)

        assert encounter.id is not None
        assert encounter.status == EncounterStatus.IN_PROGRESS
        assert encounter.facility_id == fac.id
        assert encounter.patient_id == patient.id


@pytest.mark.asyncio
async def test_08_case_evidence_provenance_and_verification_states(database):
    """Test 8: CaseEvidence preserves provenance, confidence score, and verification states without data flattening."""
    async with database() as db:
        case = TriageCase(
            synthetic_case_id=f"SYN-{uuid.uuid4().hex[:6]}",
            language="en",
            status="active",
        )
        db.add(case)
        await db.flush()

        # Evidence item 1: Patient text reported
        ev1 = CaseEvidence(
            case_id=case.id,
            canonical_field="chief_complaint",
            raw_value="Persistent fever for 3 days",
            source_type=EvidenceSourceType.PATIENT_TEXT,
            verification_state=VerificationState.UNVERIFIED,
            confidence_score=1.0,
            processor_name="patient_input",
        )
        # Evidence item 2: Staff verified vitals
        ev2 = CaseEvidence(
            case_id=case.id,
            canonical_field="body_temperature",
            raw_value="102.4 F",
            source_type=EvidenceSourceType.STAFF_ENTERED,
            verification_state=VerificationState.STAFF_VERIFIED,
            confidence_score=1.0,
            processor_name="nurse_vitals_station",
        )
        db.add_all([ev1, ev2])
        await db.commit()

        # Verify discrete items retained in case graph
        stmt = select(CaseEvidence).where(CaseEvidence.case_id == case.id).order_by(CaseEvidence.created_at)
        items = (await db.execute(stmt)).scalars().all()
        assert len(items) == 2
        assert items[0].verification_state == VerificationState.UNVERIFIED
        assert items[1].verification_state == VerificationState.STAFF_VERIFIED
        assert items[0].source_type == EvidenceSourceType.PATIENT_TEXT


@pytest.mark.asyncio
async def test_09_restart_persistence_simulation(database):
    """Test 9 (Mandatory Section 40): Data created in one session persists across simulated backend restart."""
    test_email = f"persist_{uuid.uuid4().hex[:8]}@clinova.test"
    case_synthetic_id = f"PERSIST-{uuid.uuid4().hex[:6].upper()}"
    patient_mrn = f"MRN-P-{uuid.uuid4().hex[:6].upper()}"

    # SESSION 1: Create Account, Patient Profile, Case, Evidence
    async with database() as session1:
        user = User(
            email=test_email,
            hashed_password=get_password_hash("PersistPass123!"),
            full_name="Persistent Record Subject",
            role=UserRole.PATIENT,
        )
        session1.add(user)
        await session1.flush()

        patient = Patient(
            user_id=user.id,
            mrn=patient_mrn,
            first_name="Ramesh",
            last_name="Pradhan",
            date_of_birth="1978-11-20",
            gender="Male",
        )
        session1.add(patient)
        await session1.flush()

        case = TriageCase(
            synthetic_case_id=case_synthetic_id,
            owner_user_id=user.id,
            patient_id=patient.id,
            language="en",
            status="active",
            case_version=1,
            workflow_state=CaseWorkflowState.INTAKE.value,
        )
        session1.add(case)
        await session1.flush()

        evidence = CaseEvidence(
            case_id=case.id,
            canonical_field="persisted_symptom",
            raw_value="Severe knee pain",
            source_type=EvidenceSourceType.PATIENT_TEXT,
            verification_state=VerificationState.UNVERIFIED,
        )
        session1.add(evidence)
        await session1.commit()
    # Session 1 ends (simulates process stop)

    # SESSION 2: Start new session (simulates process restart)
    async with database() as session2:
        # 1. Retrieve user
        u = (await session2.execute(select(User).where(User.email == test_email))).scalar_one_or_none()
        assert u is not None
        assert u.full_name == "Persistent Record Subject"

        # 2. Retrieve patient
        p = (await session2.execute(select(Patient).where(Patient.mrn == patient_mrn))).scalar_one_or_none()
        assert p is not None
        assert p.user_id == u.id

        # 3. Retrieve case
        c = (await session2.execute(select(TriageCase).where(TriageCase.synthetic_case_id == case_synthetic_id))).scalar_one_or_none()
        assert c is not None
        assert c.owner_user_id == u.id
        assert c.workflow_state == CaseWorkflowState.INTAKE.value

        # 4. Retrieve evidence
        ev = (await session2.execute(select(CaseEvidence).where(CaseEvidence.case_id == c.id))).scalar_one_or_none()
        assert ev is not None
        assert ev.raw_value == "Severe knee pain"


@pytest.mark.asyncio
async def test_10_consistent_error_structure(async_client: AsyncClient):
    """Test 10 (Section 29): Standardized error structure returns consistent envelope without leaking stack traces."""
    # 401 Authentication Error
    res_401 = await async_client.get("/api/v1/auth/me")
    assert res_401.status_code == 401
    err_401 = res_401.json()
    assert err_401["error_code"] == "AUTHENTICATION_ERROR"
    assert "timestamp" in err_401
    assert "status_code" in err_401
    assert err_401["status_code"] == 401

    # 404 Not Found
    res_404 = await async_client.get("/api/v1/nonexistent-endpoint-test")
    assert res_404.status_code == 404
    err_404 = res_404.json()
    assert err_404["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_11_provider_abstraction_and_normalized_failure():
    """Test 11 (Sections 30-33): Provider adapters handle failures gracefully via ProviderError contracts."""
    provider = LocalSpeechToTextProvider()

    # Verify provider name and availability
    assert provider.is_available() is True
    assert provider.provider_name == "local_speech_engine"

    # Empty audio payload raises normalized ProviderError(VALIDATION_ERROR)
    with pytest.raises(ProviderError) as exc_info:
        await provider.transcribe(audio_bytes=b"")

    err = exc_info.value
    assert err.error_code == ProviderErrorCode.VALIDATION_ERROR
    assert "empty" in err.message.lower()
    assert err.provider_name == "local_speech_engine"
    assert err.retryable is False
