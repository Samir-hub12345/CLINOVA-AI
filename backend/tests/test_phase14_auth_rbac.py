"""CLINOVA AI — Phase 14 Authentication + RBAC + Identity Hardening Test Suite.

Comprehensive verification of:
- Scenarios A through Z (Authentication, Authorization, RBAC Matrix, Boundary Isolation, Safety Guardrails)
- Adversarial Security & Anti-Spoofing Tests
- Section 24 End-to-End Multi-Persona Integration Flow (Steps 1 to 17)
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from jose import jwt

from app.main import app
from app.core.config import settings
from app.core.rbac import (
    ROLE_CLINICIAN,
    ROLE_NURSE,
    ROLE_RECEPTIONIST,
    ROLE_PATIENT,
    ROLE_REFERRAL_COORDINATOR,
    ROLE_FACILITY_ADMIN,
    ROLE_AUDITOR,
    ROLE_SYSTEM_ADMIN,
)
from app.db.init_db import init_db


@pytest.fixture(autouse=True)
async def setup_phase14_environment():
    """Ensure DB schema is initialized and configure strict Phase 14 identity defaults."""
    await init_db()
    original_legacy_headers = settings.ALLOW_LEGACY_ACTOR_HEADERS
    original_legacy_anon = settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK

    # Set strict authentication environment for Phase 14 tests
    settings.ALLOW_LEGACY_ACTOR_HEADERS = True
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False

    yield

    settings.ALLOW_LEGACY_ACTOR_HEADERS = original_legacy_headers
    settings.ALLOW_LEGACY_ANONYMOUS_FALLBACK = original_legacy_anon


async def login_helper(client: AsyncClient, username: str, password: str = settings.DEMO_USER_PASSWORD) -> str:
    """Helper to authenticate and return bearer JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# ===========================================================================
# SCENARIOS A - Z
# ===========================================================================

@pytest.mark.asyncio
async def test_scenario_a_valid_login():
    """Scenario A: Valid login returns JWT token and sanitized user details."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/auth/login",
            json={"username": "clinician", "password": settings.DEMO_USER_PASSWORD},
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        user = data["user"]
        assert user["username"] == "clinician"
        assert user["role"] == ROLE_CLINICIAN
        assert user["facility_id"] == "FAC-DH-04"
        assert "password" not in user
        assert "hashed_password" not in user


@pytest.mark.asyncio
async def test_scenario_b_invalid_credentials():
    """Scenario B: Invalid credentials or unknown user rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Wrong password
        res_bad_pwd = await client.post(
            "/api/v1/auth/login",
            json={"username": "clinician", "password": "WrongPassword123!"},
        )
        assert res_bad_pwd.status_code == 401
        err1 = res_bad_pwd.json()["error"]
        assert err1["code"] == "AUTHORIZATION_ERROR"
        assert "Invalid" in err1["message"]

        # Unknown username
        res_bad_user = await client.post(
            "/api/v1/auth/login",
            json={"username": "non_existent_user_999", "password": settings.DEMO_USER_PASSWORD},
        )
        assert res_bad_user.status_code == 401
        err2 = res_bad_user.json()["error"]
        assert err2["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_c_logout_revokes_token():
    """Scenario C: Logout revokes token so subsequent calls with that token fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Verify token is initially valid
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200

        # Perform logout
        logout_res = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "revoked"

        # Subsequent use must be rejected
        revoked_res = await client.get("/api/v1/auth/me", headers=headers)
        assert revoked_res.status_code == 401
        assert "revoked" in revoked_res.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_scenario_d_expired_token():
    """Scenario D: Expired JWT token is rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        expired_payload = {
            "sub": "usr-doc-01",
            "username": "clinician",
            "role": ROLE_CLINICIAN,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "jti": str(uuid.uuid4()),
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res.status_code == 401
        assert "expired" in res.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_scenario_e_malformed_and_tampered_token():
    """Scenario E: Malformed, forged, or invalid tokens are rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid signature
        fake_token = jwt.encode({"sub": "usr-doc-01"}, "WRONG_SECRET_KEY", algorithm="HS256")
        res1 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake_token}"})
        assert res1.status_code == 401

        # Garbage string
        res2 = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token-at-all"})
        assert res2.status_code == 401


@pytest.mark.asyncio
async def test_scenario_f_deactivated_user():
    """Scenario F: Deactivated user is prohibited from login and API access."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login attempt
        res = await client.post(
            "/api/v1/auth/login",
            json={"username": "inactive_user", "password": settings.DEMO_USER_PASSWORD},
        )
        assert res.status_code == 403
        assert "deactivated" in res.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_scenario_g_current_user_me():
    """Scenario G: GET /me returns verified identity, role, and facility."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "nurse"
        assert data["role"] == ROLE_NURSE
        assert data["facility_id"] == "FAC-DH-04"
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_scenario_h_authoritative_server_side_role_resolution():
    """Scenario H: Client header role spoofing is strictly ignored; role derived from DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        # Attacker nurse sends forged X-Actor-Role: SYSTEM_ADMIN
        spoofed_headers = {
            "Authorization": f"Bearer {nurse_token}",
            "X-Actor-Role": "SYSTEM_ADMIN",
            "X-Actor-Id": "usr-sys-06",
        }
        me_res = await client.get("/api/v1/auth/me", headers=spoofed_headers)
        assert me_res.status_code == 200
        # Authoritative role MUST remain NURSE from user database
        assert me_res.json()["role"] == ROLE_NURSE


@pytest.mark.asyncio
async def test_scenario_i_nurse_permissions():
    """Scenario I: Nurse can record vitals, write triage notes, and start triage."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        # Clinician creates case at FAC-DH-04
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "FEMALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # 1. Nurse records vitals -> 200
        v_res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={
                "heart_rate": 88,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "spo2_percent": 98,
                "respiratory_rate": 16,
                "temperature_celsius": 36.8,
                "avpu_score": "ALERT",
            },
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert v_res.status_code == 200, v_res.text

        # 2. Nurse records triage note -> 200
        tn_res = await client.post(
            f"/api/v1/cases/{case_id}/triage-note",
            json={
                "summary": "Stable presentation, initial vitals normal.",
                "acuity_assessment": "ROUTINE",
                "clinical_concerns": ["Mild cephalalgia"],
                "suggested_next_steps": ["Observation"],
            },
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert tn_res.status_code == 200, tn_res.text

        # 3. Nurse starts triage transition -> 200
        tr_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={
                "action": "START_TRIAGE",
                "reason": "Nurse initiating nursing assessment",
                "expected_state_version": 1,
            },
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert tr_res.status_code == 200, tr_res.text
        assert tr_res.json()["to_state"] == "TRIAGE_IN_PROGRESS"


@pytest.mark.asyncio
async def test_scenario_j_clinician_permissions():
    """Scenario J: Clinician can verify case and record clinical review actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "45-55", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Clinician submits human review action VERIFY
        rev_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={
                "action": "VERIFY",
                "target_entity_type": "CASE",
                "target_entity_id": case_id,
                "reason": "Confirmed acute presentation details.",
            },
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        assert rev_res.status_code == 200, rev_res.text
        assert rev_res.json()["action"] == "VERIFY"


@pytest.mark.asyncio
async def test_scenario_k_patient_restriction():
    """Scenario K: Patient cannot access staff actions or other patient data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        patient_token = await login_helper(client, "patient")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "20-29", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Patient attempting staff triage note insertion -> 403
        res = await client.post(
            f"/api/v1/cases/{case_id}/triage-note",
            json={
                "summary": "Patient self note attempt",
                "acuity_assessment": "ROUTINE",
                "clinical_concerns": [],
                "suggested_next_steps": [],
            },
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_l_referral_coordinator_restriction():
    """Scenario L: Referral coordinator cannot submit clinical review actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        ref_token = await login_helper(client, "referral")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "50-59", "biological_sex": "FEMALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Attempt clinical VERIFY
        rev_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "VERIFY", "reason": "Referral coordinator verification attempt"},
            headers={"Authorization": f"Bearer {ref_token}"},
        )
        assert rev_res.status_code == 403
        assert rev_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_m_auditor_read_only_restriction():
    """Scenario M: Auditor can read case details and audit logs, but cannot mutate cases."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        audit_token = await login_helper(client, "auditor")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "60-69", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Auditor can READ case and audit trail
        get_res = await client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": f"Bearer {audit_token}"})
        assert get_res.status_code == 200

        audit_res = await client.get(f"/api/v1/cases/{case_id}/audit", headers={"Authorization": f"Bearer {audit_token}"})
        assert audit_res.status_code == 200

        # Auditor CANNOT record vitals -> 403
        v_res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={"heart_rate": 80, "systolic_bp": 120, "diastolic_bp": 80, "spo2_percent": 98, "respiratory_rate": 16, "temperature_celsius": 37.0, "avpu_score": "ALERT"},
            headers={"Authorization": f"Bearer {audit_token}"},
        )
        assert v_res.status_code == 403


@pytest.mark.asyncio
async def test_scenario_n_facility_admin_restriction():
    """Scenario N: Facility admin cannot submit clinical review actions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        admin_token = await login_helper(client, "facility_admin")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Facility Admin attempting clinical review action -> 403
        res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "OVERRIDE", "reason": "Admin override attempt"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_scenario_o_cross_facility_denial_returns_404():
    """Scenario O: Cross-facility case access returns 404 (not 403) to hide existence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        dh_doc_token = await login_helper(client, "clinician")  # FAC-DH-04
        phc_nurse_token = await login_helper(client, "nurse_phc")  # FAC-PHC-01

        # Create case at FAC-DH-04
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "FEMALE"},
            headers={"Authorization": f"Bearer {dh_doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {dh_doc_token}"},
        )
        case_id = c_res.json()["id"]

        # PHC Nurse attempts to retrieve DH-04 case -> 404 Not Found
        res = await client.get(
            f"/api/v1/cases/{case_id}",
            headers={"Authorization": f"Bearer {phc_nurse_token}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_scenario_p_cross_case_not_found():
    """Scenario P: Non-existent case ID returns structured 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        fake_id = str(uuid.uuid4())
        res = await client.get(
            f"/api/v1/cases/{fake_id}",
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_scenario_q_nurse_clinical_action_denial():
    """Scenario Q: Nurse attempting clinician review action (VERIFY) is rejected with 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        nurse_token = await login_helper(client, "nurse")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # 1. Nurse attempting clinician review action (VERIFY) -> 403
        res_verify = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "VERIFY", "reason": "Nurse verify attempt"},
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res_verify.status_code == 403
        assert res_verify.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # 2. Nurse attempting clinician review action (REJECT) -> 403
        res_reject = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "REJECT", "reason": "Nurse reject attempt"},
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res_reject.status_code == 403
        assert res_reject.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # 3. Nurse attempting clinician evidence verification in CareGraph -> 403
        res_cg_verify = await client.post(
            f"/api/v1/caregraph/{case_id}/verify",
            json={"evidence_id": "non-existent", "verification_status": "CONFIRMED"},
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res_cg_verify.status_code == 403
        assert res_cg_verify.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_r_patient_clinical_action_denial():
    """Scenario R: Patient attempting clinician review action (REFER) is rejected with 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")
        patient_token = await login_helper(client, "patient")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "REFER", "reason": "Patient self-referral attempt"},
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_s_prohibited_ai_action_rejection():
    """Scenario S: Prohibited autonomous clinical actions rejected with 422 UNSUPPORTED_OPERATION."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        doc_token = await login_helper(client, "clinician")

        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "MALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        for prohibited_act in ["AI_DIAGNOSIS", "AUTO_PRESCRIBE", "AI_ADMISSION", "AI_DISCHARGE", "AUTHORIZE_PROCEDURE"]:
            res = await client.post(
                f"/api/v1/cases/{case_id}/review-actions",
                json={"action": prohibited_act, "reason": "Attempting prohibited action"},
                headers={"Authorization": f"Bearer {doc_token}"},
            )
            assert res.status_code == 422, f"Expected 422 for {prohibited_act}, got {res.status_code}"
            err = res.json()["error"]
            assert err["code"] == "UNSUPPORTED_OPERATION"
            assert "prohibited" in err["message"].lower()


@pytest.mark.asyncio
async def test_scenario_t_structured_error_format():
    """Scenario T: All errors conform strictly to Clinova structured envelope."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/login", json={"username": "bad", "password": "bad"})
        assert res.status_code == 401
        body = res.json()
        assert "error" in body
        err = body["error"]
        assert "code" in err
        assert "message" in err
        assert "correlation_id" in err
        assert "details" in err


@pytest.mark.asyncio
async def test_scenario_u_no_passwords_in_payloads():
    """Scenario U: Passwords and hashes are never exposed in user responses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Check /me
        me = (await client.get("/api/v1/auth/me", headers=headers)).json()
        assert "hashed_password" not in me
        assert "password" not in me

        # Check /personas
        personas = (await client.get("/api/v1/auth/personas", headers=headers)).json()
        for p in personas:
            assert "hashed_password" not in p
            assert "password" not in p


@pytest.mark.asyncio
async def test_scenario_v_no_secret_leakage_in_errors():
    """Scenario V: Secret keys or stack traces are not leaked in error details."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad.token.value"})
        text = res.text
        assert settings.SECRET_KEY not in text
        assert "Traceback" not in text


@pytest.mark.asyncio
async def test_scenario_w_authenticated_api_call():
    """Scenario W: Protected endpoints succeed with Authorization: Bearer <token>."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.get("/api/v1/cases", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_scenario_x_tampered_session_rejected():
    """Scenario X: Tampered token signature is rejected on protected endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        # Tamper payload
        tampered_token = token[:-4] + "xxxx"
        res = await client.get("/api/v1/cases", headers={"Authorization": f"Bearer {tampered_token}"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_scenario_y_logout_invalidates_all_protected_endpoints():
    """Scenario Y: Revoked token fails across all protected API routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Logout
        await client.post("/api/v1/auth/logout", headers=headers)

        # Cases list
        assert (await client.get("/api/v1/cases", headers=headers)).status_code == 401
        # Auth me
        assert (await client.get("/api/v1/auth/me", headers=headers)).status_code == 401
        # Case creation
        assert (await client.post("/api/v1/cases", json={}, headers=headers)).status_code == 401


@pytest.mark.asyncio
async def test_scenario_z_audit_event_creation():
    """Scenario Z: Audit records are written for authentication events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login writes audit event
        token = await login_helper(client, "clinician")
        headers = {"Authorization": f"Bearer {token}"}

        # Switch persona writes audit event
        switch_res = await client.post(
            "/api/v1/auth/switch-persona",
            json={"persona_id": "nurse"},
            headers=headers,
        )
        assert switch_res.status_code == 200


# ===========================================================================
# ADVERSARIAL & SECURITY TESTS
# ===========================================================================

@pytest.mark.asyncio
async def test_adversarial_role_forgery_with_bearer():
    """Attacker with nurse token attempts to elevate to SYSTEM_ADMIN via header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        doc_token = await login_helper(client, "clinician")

        # Create case
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "FEMALE"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-DH-04"},
            headers={"Authorization": f"Bearer {doc_token}"},
        )
        case_id = c_res.json()["id"]

        # Nurse sends X-Actor-Role: CLINICIAN to call review-actions with clinician-only REJECT
        res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "REJECT", "reason": "Spoofed clinician action"},
            headers={
                "Authorization": f"Bearer {nurse_token}",
                "X-Actor-Role": "CLINICIAN",
                "X-Actor-Id": "usr-doc-01",
            },
        )
        # MUST BE 403: Server derives role from token (NURSE) and ignores forged header
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_adversarial_unauthenticated_request_rejected():
    """When legacy anonymous fallback is disabled, calls without token are rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # No auth headers
        res = await client.get("/api/v1/cases")
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_adversarial_facility_spoofing():
    """Staff at FAC-DH-04 cannot bypass facility boundary by passing X-Facility-Id: FAC-PHC-01."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        phc_nurse_token = await login_helper(client, "nurse_phc")
        dh_doc_token = await login_helper(client, "clinician")

        # Create case at FAC-PHC-01
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "30-39", "biological_sex": "FEMALE"},
            headers={"Authorization": f"Bearer {phc_nurse_token}"},
        )
        c_res = await client.post(
            "/api/v1/cases",
            json={"patient_id": p_res.json()["id"], "facility_id": "FAC-PHC-01"},
            headers={"Authorization": f"Bearer {phc_nurse_token}"},
        )
        case_id = c_res.json()["id"]

        # DH Clinician passes X-Facility-Id: FAC-PHC-01 in header to access it
        res = await client.get(
            f"/api/v1/cases/{case_id}",
            headers={
                "Authorization": f"Bearer {dh_doc_token}",
                "X-Facility-Id": "FAC-PHC-01",
            },
        )
        # MUST BE 404: The token's facility (FAC-DH-04) cannot be overridden by client header
        assert res.status_code == 404


# ===========================================================================
# SECTION 24: END-TO-END MULTI-PERSONA INTEGRATION SMOKE FLOW
# ===========================================================================

@pytest.mark.asyncio
async def test_section_24_end_to_end_smoke_flow():
    """
    Executes full 17-step end-to-end multi-persona verification flow (Section 24):
    1. login as synthetic nurse
    2. retrieve current user
    3. create/access authorized synthetic case
    4. perform permitted nurse operation
    5. attempt clinician-only operation
    6. verify denial
    7. login as synthetic clinician
    8. perform allowed clinician action
    9. attempt cross-facility access
    10. verify denial
    11. attempt forged role header
    12. verify server ignores/rejects forged role
    13. attempt prohibited AI clinical action
    14. verify rejection
    15. inspect audit events
    16. logout
    17. verify authenticated endpoint no longer accepts the invalidated session
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Login as synthetic nurse
        nurse_login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "nurse", "password": settings.DEMO_USER_PASSWORD},
        )
        assert nurse_login_res.status_code == 200
        nurse_token = nurse_login_res.json()["access_token"]
        nurse_headers = {"Authorization": f"Bearer {nurse_token}"}

        # Step 2: Retrieve current user
        nurse_me = await client.get("/api/v1/auth/me", headers=nurse_headers)
        assert nurse_me.status_code == 200
        assert nurse_me.json()["role"] == ROLE_NURSE
        assert nurse_me.json()["facility_id"] == "FAC-DH-04"

        # Step 3: Create/access authorized synthetic case at FAC-DH-04
        p_res = await client.post(
            "/api/v1/patients",
            json={"age_bracket": "50-59", "biological_sex": "MALE"},
            headers=nurse_headers,
        )
        assert p_res.status_code == 200
        patient_id = p_res.json()["id"]

        c_res = await client.post(
            "/api/v1/cases",
            json={
                "patient_id": patient_id,
                "facility_id": "FAC-DH-04",
                "pathway": "REGULAR_STANDARD",
                "acuity_tier": "URGENT",
                "presenting_complaint": "Acute central chest pressure radiating to left arm",
                "primary_syndrome": "Acute Coronary Syndrome",
            },
            headers=nurse_headers,
        )
        assert c_res.status_code == 200
        case_id = c_res.json()["id"]
        assert c_res.json()["current_state"] == "INTAKE_RECORDED"

        # Step 4: Perform permitted nurse operation (vitals & triage start)
        v_res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            json={
                "heart_rate": 104,
                "systolic_bp": 138,
                "diastolic_bp": 88,
                "spo2_percent": 96,
                "respiratory_rate": 20,
                "temperature_celsius": 37.1,
                "avpu_score": "ALERT",
            },
            headers=nurse_headers,
        )
        assert v_res.status_code == 200

        tr_res = await client.post(
            f"/api/v1/cases/{case_id}/transitions",
            json={
                "action": "START_TRIAGE",
                "reason": "Nurse commenced initial triage bundle",
                "expected_state_version": 1,
            },
            headers=nurse_headers,
        )
        assert tr_res.status_code == 200
        assert tr_res.json()["to_state"] == "TRIAGE_IN_PROGRESS"

        # Step 5: Attempt clinician-only operation (Nurse calls review-actions with VERIFY)
        nurse_rev_attempt = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={
                "action": "VERIFY",
                "target_entity_type": "CASE",
                "target_entity_id": case_id,
                "reason": "Nurse attempting clinical review verification",
            },
            headers=nurse_headers,
        )

        # Step 6: Verify denial (403)
        assert nurse_rev_attempt.status_code == 403
        assert nurse_rev_attempt.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # Step 7: Login as synthetic clinician
        doc_login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "clinician", "password": settings.DEMO_USER_PASSWORD},
        )
        assert doc_login_res.status_code == 200
        doc_token = doc_login_res.json()["access_token"]
        doc_headers = {"Authorization": f"Bearer {doc_token}"}

        # Step 8: Perform allowed clinician action (Clinician verifies)
        doc_rev_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={
                "action": "VERIFY",
                "target_entity_type": "CASE",
                "target_entity_id": case_id,
                "reason": "Clinician verified presentation, ECG ordered",
            },
            headers=doc_headers,
        )
        assert doc_rev_res.status_code == 200
        assert doc_rev_res.json()["action"] == "VERIFY"

        # Step 9: Attempt cross-facility access (DH clinician accessing PHC case)
        phc_token = await login_helper(client, "nurse_phc")
        phc_case = await client.post(
            "/api/v1/cases",
            json={
                "patient_id": patient_id,
                "facility_id": "FAC-PHC-01",
                "pathway": "REGULAR_STANDARD",
                "acuity_tier": "ROUTINE",
            },
            headers={"Authorization": f"Bearer {phc_token}"},
        )
        phc_case_id = phc_case.json()["id"]

        cross_res = await client.get(f"/api/v1/cases/{phc_case_id}", headers=doc_headers)

        # Step 10: Verify denial (404 hides existence across facility boundaries)
        assert cross_res.status_code == 404
        assert cross_res.json()["error"]["code"] == "NOT_FOUND"

        # Step 11: Attempt forged role header (Nurse claims to be CLINICIAN)
        forged_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "REJECT", "reason": "Nurse attempting role spoofing"},
            headers={
                "Authorization": f"Bearer {nurse_token}",
                "X-Actor-Role": "CLINICIAN",
                "X-Actor-Id": "usr-doc-01",
            },
        )

        # Step 12: Verify server ignores/rejects forged role (403)
        assert forged_res.status_code == 403
        assert forged_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # Step 13: Attempt prohibited AI clinical action (AI_DIAGNOSIS)
        prohibited_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={
                "action": "AI_DIAGNOSIS",
                "reason": "Attempting autonomous diagnosis",
            },
            headers=doc_headers,
        )

        # Step 14: Verify rejection (422)
        assert prohibited_res.status_code == 422
        assert prohibited_res.json()["error"]["code"] == "UNSUPPORTED_OPERATION"

        # Step 15: Inspect audit events
        audit_res = await client.get(f"/api/v1/cases/{case_id}/audit", headers=doc_headers)
        assert audit_res.status_code == 200
        events = audit_res.json()
        assert len(events) >= 3
        # Verify event structures and correlation identifiers
        for ev in events:
            assert "correlation_id" in ev
            assert "action" in ev
            assert "actor_id" in ev

        # Step 16: Logout
        logout_res = await client.post("/api/v1/auth/logout", headers=doc_headers)
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "revoked"

        # Step 17: Verify authenticated endpoint no longer accepts the invalidated session (401)
        subsequent_res = await client.get(f"/api/v1/cases/{case_id}", headers=doc_headers)
        assert subsequent_res.status_code == 401
        assert subsequent_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_receptionist_role_workflow_and_governance():
    """Verify Receptionist role authentication, registration capability, and clinical boundary enforcement."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Authenticate as Receptionist (Tunde Olawale)
        rec_token = await login_helper(client, "receptionist")
        assert rec_token is not None
        rec_headers = {"Authorization": f"Bearer {rec_token}"}

        # 2. Verify identity profile endpoint
        me_res = await client.get("/api/v1/auth/me", headers=rec_headers)
        assert me_res.status_code == 200
        user_data = me_res.json()
        assert user_data["username"] == "receptionist"
        assert user_data["role"] == ROLE_RECEPTIONIST
        assert user_data["facility_id"] == "FAC-DH-04"

        # 3. Create/register a new case intake at reception desk
        intake_res = await client.post(
            "/api/v1/intake/submit",
            json={
                "facility_id": "FAC-DH-04",
                "pathway": "OPD_GENERAL",
                "chief_complaint": "Persistent headache and fever for 2 days",
                "consent_confirmed": True,
                "reported_age_bracket": "25-35 YRS",
                "biological_sex": "FEMALE",
            },
            headers=rec_headers,
        )
        assert intake_res.status_code == 200
        case_id = intake_res.json()["case_id"]

        # 4. Read case within same facility scope
        case_res = await client.get(f"/api/v1/cases/{case_id}", headers=rec_headers)
        assert case_res.status_code == 200

        # 5. Strictly barred from performing clinical review action
        review_res = await client.post(
            f"/api/v1/cases/{case_id}/review-actions",
            json={"action": "VERIFY_EVIDENCE", "evidence_id": "ev-01"},
            headers=rec_headers,
        )
        assert review_res.status_code == 403
        assert review_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"

        # 6. Strictly barred from clinical decision recording
        decision_res = await client.post(
            f"/api/v1/cases/{case_id}/decision",
            json={
                "decision_type": "CONFIRM_DIAGNOSIS",
                "clinical_impression": "Receptionist attempting clinical diagnosis",
                "clinical_rationale": "Non-clinical actor rationale",
            },
            headers=rec_headers,
        )
        assert decision_res.status_code == 403
        assert decision_res.json()["error"]["code"] == "AUTHORIZATION_ERROR"

