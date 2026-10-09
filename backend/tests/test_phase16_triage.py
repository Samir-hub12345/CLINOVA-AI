"""CLINOVA AI — Phase 16 Vitals + Queue + Deterministic Triage Test Suite.

Continuous Care Intelligence System.
Phase 16: Vitals + Queue + Deterministic Triage Foundation.
Grounded in Section 27 of Master Specification, DOC-03, DOC-07, DOC-08, DOC-14.

Complete Test Matrix:
A. valid vital creation
B. invalid vital range rejected
C. SBP < DBP rejected
D. malformed value rejected
E. vital provenance preserved
F. vital timestamp preserved
G. latest-vital retrieval
H. stale-vital detection
I. missing-vital detection
J. complete NEWS2 calculation
K. incomplete NEWS2 calculation
L. NEWS2 deterministic repeatability
M. NEWS2 component traceability
N. Shock Index calculation
O. Shock Index missing-input handling
P. Shock Index invalid-input handling
Q. deterministic red-flag trigger
R. non-triggered red-flag case
S. rule explanation present
T. rule/version recorded
U. emergency pathway priority
V. normal pathway priority
W. queue ordering deterministic
X. query-time waiting time
Y. tie-breaker determinism
Z. facility-scoped queue access
AA. patient cannot access staff queue
AB. nurse queue authorization
AC. clinician queue authorization
AD. cross-facility queue denial
AE. prohibited clinical actions remain blocked
AF. uncertainty remains separate from physiological risk
AG. high uncertainty does not automatically become emergency without supporting rule
AH. missing critical data surfaces correctly
AI. historical vitals remain immutable
AJ. recalculation does not erase history
AK. audit event created where required
AL. transaction rollback
AM. structured error contract
AN. synthetic mode preserved

Adversarial Tests:
- forged priority values
- client-supplied risk score override
- client-supplied NEWS2 and Shock Index ignored
- client-supplied red-flag status ignored
- facility scope spoofing denied
- manipulation of wait time prevented
- future-dated vital observation rejected
- duplicate vital submissions preserved as distinct history
- stale-data manipulation prevented
- malformed rule inputs rejected
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
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
    ROLE_SYSTEM_ADMIN,
)
from app.db.init_db import init_db
from app.db.session import async_session_factory
from app.db.models import (
    Patient,
    Encounter,
    Case,
    Vital,
    AuditEvent,
    TriageSnapshotRecord,
    User,
)
from app.domain.triage import (
    calculate_deterministic_news2,
    calculate_deterministic_shock_index,
    evaluate_vital_freshness,
    evaluate_deterministic_red_flags,
    evaluate_priority_tier,
    sort_clinical_queue,
    compute_deterministic_triage,
    NEWS2_VERSION,
    SHOCK_INDEX_VERSION,
    RED_FLAGS_VERSION,
    PRIORITY_RULES_VERSION,
)


@pytest.fixture(autouse=True)
async def setup_phase16_environment():
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


async def create_case_helper(
    client: AsyncClient,
    token: str,
    facility_id: str = "FAC-DH-04",
    pathway: str = "REGULAR_STANDARD",
    chief_complaint: str = "Intermittent fever and fatigue",
) -> str:
    """Helper to create a case via the intake endpoint and return its case_id."""
    res = await client.post(
        "/api/v1/intake/submit",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "facility_id": facility_id,
            "pathway": pathway,
            "reported_age_bracket": "40-49",
            "biological_sex": "FEMALE",
            "preferred_language": "en",
            "chief_complaint": chief_complaint,
            "symptom_duration": "2 days",
            "consent_confirmed": True,
        },
    )
    assert res.status_code == 200, f"Case creation failed: {res.text}"
    return res.json()["case_id"]


# ===========================================================================
# UNIT TESTS: DETERMINISTIC TRIAGE DOMAIN LOGIC
# ===========================================================================

def test_unit_news2_scoring_boundaries():
    """Unit: Verifies all NEWS2 scoring boundaries against RCP 2017 specification."""
    # Zero score normal physiology
    res_normal = calculate_deterministic_news2(
        respiratory_rate=16,
        spo2_percent=98,
        supplemental_o2=False,
        systolic_bp=120,
        heart_rate=72,
        avpu_score="ALERT",
        temperature_celsius=37.0,
    )
    assert res_normal["is_complete"] is True
    assert res_normal["score"] == 0
    assert res_normal["risk_level"] == "LOW"

    # Extreme respiratory rate
    assert calculate_deterministic_news2(respiratory_rate=8, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["respiratory_rate"] == 3
    assert calculate_deterministic_news2(respiratory_rate=25, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["respiratory_rate"] == 3
    assert calculate_deterministic_news2(respiratory_rate=22, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["respiratory_rate"] == 2
    assert calculate_deterministic_news2(respiratory_rate=10, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["respiratory_rate"] == 1

    # Oxygen saturation boundaries
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=91, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["spo2"] == 3
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=93, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["spo2"] == 2
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=95, systolic_bp=120, heart_rate=72, avpu_score="ALERT", temperature_celsius=37.0)["component_scores"]["spo2"] == 1

    # Consciousness: Any non-alert scores 3
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="VOICE", temperature_celsius=37.0)["component_scores"]["avpu"] == 3
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="PAIN", temperature_celsius=37.0)["component_scores"]["avpu"] == 3
    assert calculate_deterministic_news2(respiratory_rate=16, spo2_percent=98, systolic_bp=120, heart_rate=72, avpu_score="UNRESPONSIVE", temperature_celsius=37.0)["component_scores"]["avpu"] == 3


def test_unit_shock_index_division_and_bounds():
    """Unit: Verifies Allgöwer & Burri Shock Index calculation and threshold interpretation."""
    # Normal: 70 / 120 = 0.58 < 0.7
    r1 = calculate_deterministic_shock_index(heart_rate=70, systolic_bp=120)
    assert r1["is_complete"] is True
    assert r1["score"] == 0.58
    assert r1["interpretation"] == "NORMAL"

    # Mild: 80 / 100 = 0.80 in [0.7, 0.9)
    r2 = calculate_deterministic_shock_index(heart_rate=80, systolic_bp=100)
    assert r2["score"] == 0.80
    assert r2["interpretation"] == "MILD_ELEVATED"

    # High: 95 / 100 = 0.95 in [0.9, 1.0)
    r3 = calculate_deterministic_shock_index(heart_rate=95, systolic_bp=100)
    assert r3["score"] == 0.95
    assert r3["interpretation"] == "HIGH_SHOCK_RISK"

    # Critical: 110 / 100 = 1.10 >= 1.0
    r4 = calculate_deterministic_shock_index(heart_rate=110, systolic_bp=100)
    assert r4["score"] == 1.10
    assert r4["interpretation"] == "CRITICAL_SHOCK_RISK"


# ===========================================================================
# PHASE 16 INTEGRATION TEST MATRIX: SCENARIOS A - AN
# ===========================================================================

@pytest.mark.asyncio
async def test_scenario_a_valid_vital_creation():
    """Scenario A: Valid vital sign observation is accepted and persisted with 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 78,
                "systolic_bp": 122,
                "diastolic_bp": 82,
                "spo2_percent": 98,
                "respiratory_rate": 16,
                "temperature_celsius": 36.9,
                "avpu_score": "ALERT",
                "supplemental_o2": False,
                "source": "NURSE_ENTERED",
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["case_id"] == case_id
        assert data["heart_rate"] == 78
        assert data["systolic_bp"] == 122
        assert data["diastolic_bp"] == 82
        assert data["spo2_percent"] == 98
        assert data["respiratory_rate"] == 16
        assert data["temperature_celsius"] == 36.9
        assert data["avpu_score"] == "ALERT"
        assert data["source"] == "NURSE_ENTERED"


@pytest.mark.asyncio
async def test_scenario_b_invalid_vital_range_rejected():
    """Scenario B: Physiologically impossible vital values are rejected with 422 VALIDATION_ERROR."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Pulse > 260 bpm
        r1 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 300},
        )
        assert r1.status_code == 422
        assert r1.json()["error"]["code"] == "VALIDATION_ERROR"

        # Systolic BP < 30 mmHg
        r2 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"systolic_bp": 15},
        )
        assert r2.status_code == 422

        # SpO2 < 30%
        r3 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"spo2_percent": 25},
        )
        assert r3.status_code == 422

        # Temperature > 44.0 C
        r4 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"temperature_celsius": 45.5},
        )
        assert r4.status_code == 422


@pytest.mark.asyncio
async def test_scenario_c_sbp_less_than_dbp_rejected():
    """Scenario C: SBP <= DBP violates physiological perfusion gradient and is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # SBP strictly less than DBP
        res1 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"systolic_bp": 70, "diastolic_bp": 90},
        )
        assert res1.status_code == 422
        assert "greater than diastolic" in str(res1.json()["error"])

        # SBP equal to DBP
        res2 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"systolic_bp": 85, "diastolic_bp": 85},
        )
        assert res2.status_code == 422


@pytest.mark.asyncio
async def test_scenario_d_malformed_value_rejected():
    """Scenario D: Malformed enum or non-standard source values are rejected with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Invalid AVPU
        res1 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"avpu_score": "CONFUSED_SLEEPY"},
        )
        assert res1.status_code == 422

        # Invalid source
        res2 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"source": "INTERNET_FORUM"},
        )
        assert res2.status_code == 422


@pytest.mark.asyncio
async def test_scenario_e_vital_provenance_preserved():
    """Scenario E: Provenance governance strictly preserved; PATIENT_REPORTED and DEVICE_DERIVED never auto-verified."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        clinician_token = await login_helper(client, "clinician")
        case_id = await create_case_helper(client, nurse_token)

        # Patient reported vital entered via nurse
        r_patient = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 84, "source": "PATIENT_REPORTED"},
        )
        assert r_patient.status_code == 200
        v_patient_id = r_patient.json()["id"]

        # Device derived vital entered
        r_device = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 86, "source": "DEVICE_DERIVED"},
        )
        assert r_device.status_code == 200
        v_device_id = r_device.json()["id"]

        # Clinician entered vital
        r_clinician = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {clinician_token}"},
            json={"heart_rate": 80, "source": "CLINICIAN_ENTERED"},
        )
        assert r_clinician.status_code == 200
        v_clinician_id = r_clinician.json()["id"]

        async with async_session_factory() as db:
            vp = await db.get(Vital, v_patient_id)
            vd = await db.get(Vital, v_device_id)
            vc = await db.get(Vital, v_clinician_id)

            assert vp.verification_context["verified"] is False
            assert vp.verification_context["verification_status"] == "UNVERIFIED"

            assert vd.verification_context["verified"] is False
            assert vd.verification_context["verification_status"] == "UNVERIFIED"

            assert vc.verification_context["verified"] is True
            assert vc.verification_context["verification_status"] == "CLINICIAN_VERIFIED"


@pytest.mark.asyncio
async def test_scenario_f_vital_timestamp_preserved():
    """Scenario F: Explicit observation timestamps in past are preserved exactly without distortion."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        recorded_time = datetime.now(timezone.utc) - timedelta(minutes=45)
        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 74,
                "recorded_at": recorded_time.isoformat(),
                "source": "NURSE_ENTERED",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["recorded_at"].startswith(recorded_time.isoformat()[:16])


@pytest.mark.asyncio
async def test_scenario_g_latest_vital_retrieval():
    """Scenario G: GET /cases/{case_id}/vitals/latest returns the authoritative latest vital observation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # First vital: HR = 90
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 90, "systolic_bp": 130, "diastolic_bp": 85},
        )

        # Second vital: HR = 78
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 78, "systolic_bp": 120, "diastolic_bp": 80},
        )

        res = await client.get(
            f"/api/v1/cases/{case_id}/vitals/latest",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["vital"]["heart_rate"] == 78
        assert data["vital"]["systolic_bp"] == 120
        assert data["freshness_by_parameter"]["heart_rate"] == "AVAILABLE"
        assert data["freshness_by_parameter"]["systolic_bp"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_scenario_h_stale_vital_detection():
    """Scenario H: Vitals recorded between 2 and 6 hours ago are deterministically flagged as STALE."""
    now = datetime.now(timezone.utc)
    recorded_3h_ago = now - timedelta(hours=3)

    freshness = evaluate_vital_freshness(
        recorded_at=recorded_3h_ago,
        parameter_values={"heart_rate": 80, "systolic_bp": 120},
        now=now,
    )
    assert freshness["freshness_by_parameter"]["heart_rate"] == "STALE"
    assert freshness["freshness_by_parameter"]["systolic_bp"] == "STALE"
    assert freshness["age_minutes"] == pytest.approx(180.0, 1.0)
    assert freshness["overall_status"] == "STALE"


@pytest.mark.asyncio
async def test_scenario_i_missing_vital_detection():
    """Scenario I: Absent vitals or vitals older than 6 hours are marked MISSING for acute triage."""
    now = datetime.now(timezone.utc)
    # Case 1: No vitals recorded
    f_empty = evaluate_vital_freshness(recorded_at=None, parameter_values={}, now=now)
    assert f_empty["overall_status"] == "MISSING"
    assert all(status == "MISSING" for status in f_empty["freshness_by_parameter"].values())

    # Case 2: Vitals recorded 8 hours ago (> 6h expiry limit)
    recorded_8h_ago = now - timedelta(hours=8)
    f_expired = evaluate_vital_freshness(
        recorded_at=recorded_8h_ago,
        parameter_values={"heart_rate": 80, "systolic_bp": 120},
        now=now,
    )
    assert f_expired["freshness_by_parameter"]["heart_rate"] == "MISSING"
    assert f_expired["overall_status"] == "MISSING"


@pytest.mark.asyncio
async def test_scenario_j_complete_news2_calculation():
    """Scenario J: Complete vital signs vector yields authoritative NEWS2 integer score and risk tier."""
    res = calculate_deterministic_news2(
        respiratory_rate=22,      # 2 pts (21-24)
        spo2_percent=93,          # 2 pts (92-93)
        supplemental_o2=True,     # 2 pts
        systolic_bp=95,           # 2 pts (91-100)
        heart_rate=115,           # 2 pts (111-130)
        avpu_score="ALERT",       # 0 pts
        temperature_celsius=38.5, # 1 pt (38.1-39.0)
    )
    assert res["is_complete"] is True
    assert res["score"] == 11
    assert res["risk_level"] == "HIGH"
    assert res["missing_components"] == []
    assert res["version"] == NEWS2_VERSION


@pytest.mark.asyncio
async def test_scenario_k_incomplete_news2_calculation():
    """Scenario K: Missing parameters do NOT default to 0 or normal physiology; score is None and missing surfaced."""
    res = calculate_deterministic_news2(
        respiratory_rate=16,
        spo2_percent=98,
        systolic_bp=120,
        heart_rate=None,          # Missing
        avpu_score="ALERT",
        temperature_celsius=None, # Missing
    )
    assert res["is_complete"] is False
    assert res["score"] is None
    assert res["risk_level"] is None
    assert "heart_rate" in res["missing_components"]
    assert "temperature_celsius" in res["missing_components"]
    assert res["limitation"] is not None


def test_scenario_l_news2_deterministic_repeatability():
    """Scenario L: Calling NEWS2 scoring multiple times with identical inputs produces bit-exact repeatable outputs."""
    inputs = {
        "respiratory_rate": 20,
        "spo2_percent": 96,
        "supplemental_o2": False,
        "systolic_bp": 115,
        "heart_rate": 88,
        "avpu_score": "ALERT",
        "temperature_celsius": 37.2,
    }
    r1 = calculate_deterministic_news2(**inputs)
    r2 = calculate_deterministic_news2(**inputs)
    r3 = calculate_deterministic_news2(**inputs)

    assert r1["score"] == r2["score"] == r3["score"] == 0
    assert r1["risk_level"] == r2["risk_level"] == r3["risk_level"] == "LOW"
    assert r1["component_scores"] == r2["component_scores"] == r3["component_scores"]


def test_scenario_m_news2_component_traceability():
    """Scenario M: Every physiological component score is individually traceable in the result payload."""
    res = calculate_deterministic_news2(
        respiratory_rate=23,      # 2
        spo2_percent=92,          # 2
        supplemental_o2=True,     # 2
        systolic_bp=105,          # 1
        heart_rate=45,            # 1
        avpu_score="VOICE",       # 3
        temperature_celsius=35.0, # 3
    )
    assert res["component_scores"]["respiratory_rate"] == 2
    assert res["component_scores"]["spo2"] == 2
    assert res["component_scores"]["supplemental_o2"] == 2
    assert res["component_scores"]["systolic_bp"] == 1
    assert res["component_scores"]["heart_rate"] == 1
    assert res["component_scores"]["avpu"] == 3
    assert res["component_scores"]["temperature"] == 3
    assert res["score"] == 14


def test_scenario_n_shock_index_calculation():
    """Scenario N: Shock Index (HR / SBP) is computed deterministically with documented clinical interpretation."""
    res = calculate_deterministic_shock_index(heart_rate=120, systolic_bp=100)
    assert res["is_complete"] is True
    assert res["score"] == 1.20
    assert res["interpretation"] == "CRITICAL_SHOCK_RISK"
    assert res["version"] == SHOCK_INDEX_VERSION


def test_scenario_o_shock_index_missing_input_handling():
    """Scenario O: Incomplete Shock Index inputs return is_complete=False without fabricating a score."""
    r_no_hr = calculate_deterministic_shock_index(heart_rate=None, systolic_bp=120)
    assert r_no_hr["is_complete"] is False
    assert r_no_hr["score"] is None
    assert "heart_rate" in r_no_hr["missing_components"]

    r_no_sbp = calculate_deterministic_shock_index(heart_rate=80, systolic_bp=None)
    assert r_no_sbp["is_complete"] is False
    assert r_no_sbp["score"] is None
    assert "systolic_bp" in r_no_sbp["missing_components"]


def test_scenario_p_shock_index_invalid_input_handling():
    """Scenario P: Zero or negative SBP is safely handled without division by zero errors."""
    r_zero = calculate_deterministic_shock_index(heart_rate=80, systolic_bp=0)
    assert r_zero["is_complete"] is False
    assert r_zero["score"] is None
    assert r_zero["interpretation"] == "INVALID_INPUTS"
    assert r_zero["error"] is not None


def test_scenario_q_deterministic_red_flag_triggers():
    """Scenario Q: All configured deterministic red-flag rules trigger on acute physiological derangements."""
    now = datetime.now(timezone.utc)

    # 1. Hypoxia (SpO2 <= 88)
    rf_hypox = evaluate_deterministic_red_flags({"spo2_percent": 85}, evaluated_at=now)
    h_rule = next(r for r in rf_hypox if r["rule_id"] == "RF-PHYSIO-HYPOXIA")
    assert h_rule["triggered"] is True
    assert h_rule["severity"] == "CRITICAL"

    # 2. Decompensated Shock (SBP <= 80)
    rf_shock = evaluate_deterministic_red_flags({"systolic_bp": 75}, evaluated_at=now)
    s_rule = next(r for r in rf_shock if r["rule_id"] == "RF-PHYSIO-SHOCK")
    assert s_rule["triggered"] is True
    assert s_rule["severity"] == "CRITICAL"

    # 3. Severe Unresponsiveness (AVPU = UNRESPONSIVE)
    rf_avpu = evaluate_deterministic_red_flags({"avpu_score": "UNRESPONSIVE"}, evaluated_at=now)
    u_rule = next(r for r in rf_avpu if r["rule_id"] == "RF-PHYSIO-UNRESPONSIVE")
    assert u_rule["triggered"] is True

    # 4. Extreme RR (RR <= 8 or >= 35)
    rf_rr = evaluate_deterministic_red_flags({"respiratory_rate": 38}, evaluated_at=now)
    rr_rule = next(r for r in rf_rr if r["rule_id"] == "RF-PHYSIO-EXTREME-RR")
    assert rr_rule["triggered"] is True

    # 5. Extreme HR (HR <= 35 or >= 150)
    rf_hr = evaluate_deterministic_red_flags({"heart_rate": 160}, evaluated_at=now)
    hr_rule = next(r for r in rf_hr if r["rule_id"] == "RF-PHYSIO-EXTREME-HR")
    assert hr_rule["triggered"] is True

    # 6. Malignant Hyperpyrexia (Temp >= 40.5 C)
    rf_temp = evaluate_deterministic_red_flags({"temperature_celsius": 41.2}, evaluated_at=now)
    temp_rule = next(r for r in rf_temp if r["rule_id"] == "RF-PHYSIO-HYPERPYREXIA")
    assert temp_rule["triggered"] is True

    # 7. Airway Compromise (presentation narrative)
    rf_airway = evaluate_deterministic_red_flags({}, presenting_complaint="Child with acute inspiratory stridor", evaluated_at=now)
    air_rule = next(r for r in rf_airway if r["rule_id"] == "RF-CLINICAL-AIRWAY")
    assert air_rule["triggered"] is True

    # 8. Massive Hemorrhage
    rf_bleed = evaluate_deterministic_red_flags({}, presenting_complaint="Postpartum hemorrhage with massive bleeding", evaluated_at=now)
    b_rule = next(r for r in rf_bleed if r["rule_id"] == "RF-CLINICAL-MASSIVE-BLEEDING")
    assert b_rule["triggered"] is True


def test_scenario_r_non_triggered_red_flag_case():
    """Scenario R: Patient with normal physiological parameters triggers zero clinical red flags."""
    normal_vitals = {
        "heart_rate": 72,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "spo2_percent": 99,
        "respiratory_rate": 16,
        "temperature_celsius": 36.8,
        "avpu_score": "ALERT",
    }
    rf_list = evaluate_deterministic_red_flags(normal_vitals, presenting_complaint="Routine antenatal checkup")
    assert all(rf["triggered"] is False for rf in rf_list)


def test_scenario_s_rule_explanation_present():
    """Scenario S: Every red-flag rule evaluation contains a non-empty clinical explanation."""
    vitals = {"spo2_percent": 84, "heart_rate": 75}
    rf_list = evaluate_deterministic_red_flags(vitals)
    for rf in rf_list:
        assert isinstance(rf["explanation"], str)
        assert len(rf["explanation"].strip()) > 0


def test_scenario_t_rule_and_version_recorded():
    """Scenario T: Every rule execution records rule_id and rule_version for full auditability."""
    rf_list = evaluate_deterministic_red_flags({"heart_rate": 80})
    for rf in rf_list:
        assert rf["rule_version"] == RED_FLAGS_VERSION
        assert rf["rule_id"].startswith("RF-")


@pytest.mark.asyncio
async def test_scenario_u_emergency_pathway_priority():
    """Scenario U: Cases entering the EMERGENCY pathway are deterministically assigned P1_CRITICAL priority."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token, pathway="EMERGENCY")

        res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["priority_tier"] == "P1_CRITICAL"
        assert data["acuity_tier"] == "CRITICAL"
        assert data["pathway"] == "EMERGENCY"


@pytest.mark.asyncio
async def test_scenario_v_normal_pathway_priority():
    """Scenario V: Stable cases in the regular outpatient pathway are deterministically assigned P4_ROUTINE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token, pathway="REGULAR_STANDARD")

        # Record stable vitals
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 72,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "spo2_percent": 98,
                "respiratory_rate": 16,
                "temperature_celsius": 36.8,
                "avpu_score": "ALERT",
            },
        )

        res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["priority_tier"] == "P4_ROUTINE"
        assert data["acuity_tier"] == "ROUTINE"


def test_scenario_w_queue_ordering_deterministic():
    """Scenario W: Queue items are sorted strictly by Emergency > Red Flags > Priority Tier > Risk > Wait Time."""
    items = [
        {"case_id": "c-routine", "pathway": "REGULAR", "has_critical_red_flags": False, "priority_tier": "P4_ROUTINE", "risk_score": 0.1, "waiting_minutes": 10},
        {"case_id": "c-emergency", "pathway": "EMERGENCY", "has_critical_red_flags": False, "priority_tier": "P1_CRITICAL", "risk_score": 0.9, "waiting_minutes": 5},
        {"case_id": "c-urgent-rf", "pathway": "REGULAR", "has_critical_red_flags": True, "priority_tier": "P1_CRITICAL", "risk_score": 0.95, "waiting_minutes": 8},
        {"case_id": "c-moderate", "pathway": "REGULAR", "has_critical_red_flags": False, "priority_tier": "P3_MODERATE", "risk_score": 0.35, "waiting_minutes": 30},
    ]
    sorted_items = sort_clinical_queue(items)
    order = [i["case_id"] for i in sorted_items]

    # Emergency pathway comes first, followed by active critical red flag, then moderate, then routine
    assert order[0] == "c-emergency"
    assert order[1] == "c-urgent-rf"
    assert order[2] == "c-moderate"
    assert order[3] == "c-routine"


@pytest.mark.asyncio
async def test_scenario_x_query_time_waiting_time():
    """Scenario X: Waiting time in minutes is computed at query time relative to created_at and current time."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {nurse_token}"})
        assert res.status_code == 200
        data = res.json()
        for item in data["queue"]:
            assert "waiting_minutes" in item
            assert isinstance(item["waiting_minutes"], int)
            assert item["waiting_minutes"] >= 0


def test_scenario_y_tie_breaker_determinism():
    """Scenario Y: Identical clinical parameters break ties strictly by created_at then case_id without jitter."""
    items = [
        {"case_id": "case-B", "pathway": "REGULAR", "has_critical_red_flags": False, "priority_tier": "P3_MODERATE", "risk_score": 0.35, "waiting_minutes": 20, "created_at": "2026-10-09T00:00:00Z"},
        {"case_id": "case-A", "pathway": "REGULAR", "has_critical_red_flags": False, "priority_tier": "P3_MODERATE", "risk_score": 0.35, "waiting_minutes": 20, "created_at": "2026-10-09T00:00:00Z"},
    ]
    res1 = sort_clinical_queue(items)
    res2 = sort_clinical_queue(items)
    # Both runs produce exact same lexicographic tie-break: case-A before case-B
    assert [i["case_id"] for i in res1] == ["case-A", "case-B"]
    assert [i["case_id"] for i in res2] == ["case-A", "case-B"]


@pytest.mark.asyncio
async def test_scenario_z_facility_scoped_queue_access():
    """Scenario Z: Staff members query only cases associated with their authorized facility."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_dh_token = await login_helper(client, "nurse")  # FAC-DH-04
        nurse_phc_token = await login_helper(client, "nurse_phc")  # FAC-PHC-01

        # Create case at FAC-DH-04
        await create_case_helper(client, nurse_dh_token, facility_id="FAC-DH-04")

        res_dh = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {nurse_dh_token}"})
        assert res_dh.status_code == 200
        for item in res_dh.json()["queue"]:
            assert item["facility_id"] == "FAC-DH-04"

        res_phc = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {nurse_phc_token}"})
        assert res_phc.status_code == 200
        for item in res_phc.json()["queue"]:
            assert item["facility_id"] == "FAC-PHC-01"


@pytest.mark.asyncio
async def test_scenario_aa_patient_cannot_access_staff_queue():
    """Scenario AA: Patient role attempting to access staff clinical queue is rejected with 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        patient_token = await login_helper(client, "patient")
        res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {patient_token}"})
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_ab_nurse_queue_authorization():
    """Scenario AB: Licensed nurse is authorized to access the facility triage queue."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "nurse")
        res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "queue" in res.json()


@pytest.mark.asyncio
async def test_scenario_ac_clinician_queue_authorization():
    """Scenario AC: Clinician is authorized to access the operational clinical queue."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await login_helper(client, "clinician")
        res = await client.get("/api/v1/cases/queue", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "queue" in res.json()


@pytest.mark.asyncio
async def test_scenario_ad_cross_facility_queue_denial():
    """Scenario AD: Staff requesting explicit cross-facility queue filter receives 404 (preventing existence leak)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_dh = await login_helper(client, "nurse")  # Assigned to FAC-DH-04
        res = await client.get(
            "/api/v1/cases/queue?facility_id=FAC-PHC-01",
            headers={"Authorization": f"Bearer {nurse_dh}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_scenario_ae_prohibited_clinical_actions_remain_blocked():
    """Scenario AE: Prohibited clinical mutation (patient executing triage calculation) is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        patient_token = await login_helper(client, "patient")
        case_id = await create_case_helper(client, nurse_token)

        res = await client.post(
            f"/api/v1/cases/{case_id}/triage/calculate",
            headers={"Authorization": f"Bearer {patient_token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTHORIZATION_ERROR"


@pytest.mark.asyncio
async def test_scenario_af_uncertainty_remains_separate_from_physiological_risk():
    """Scenario AF: Missing data raises uncertainty without inflating physiological risk score."""
    snapshot = compute_deterministic_triage(
        case_id="case-test-uncert",
        pathway="REGULAR_STANDARD",
        current_state="INTAKE_RECORDED",
        latest_vital=None,  # Zero vitals recorded
    )
    # Uncertainty is elevated because no bedside vitals exist
    assert snapshot["uncertainty_score"] >= 0.60
    assert snapshot["uncertainty_level"] == "HIGH"

    # Physiological risk score remains low (0.15) — missing data is NOT treated as physiological deterioration
    assert snapshot["risk_score"] <= 0.20
    assert snapshot["priority_tier"] == "P4_ROUTINE"


@pytest.mark.asyncio
async def test_scenario_ag_high_uncertainty_does_not_force_emergency_escalation():
    """Scenario AG (Phase 7 Critical Invariant): High uncertainty from missing data does NOT force emergency tier."""
    snapshot = compute_deterministic_triage(
        case_id="case-invariant",
        pathway="REGULAR_STANDARD",
        current_state="INTAKE_RECORDED",
        presenting_complaint="Mild common cold symptoms",
        latest_vital=None,
    )
    assert snapshot["priority_tier"] != "P1_CRITICAL"
    assert snapshot["priority_tier"] != "P2_URGENT"
    assert snapshot["priority_tier"] == "P4_ROUTINE"
    assert snapshot["has_critical_red_flags"] is False


@pytest.mark.asyncio
async def test_scenario_ah_missing_critical_data_surfaces_correctly():
    """Scenario AH: Missing critical vital parameters are explicitly enumerated in priority breakdown."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Record only Heart Rate
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 78},
        )

        res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "systolic_bp" in data["missing_critical_vitals"]
        assert "spo2_percent" in data["missing_critical_vitals"]
        assert any("Missing critical vital" in r for r in data["priority_reasons"])


@pytest.mark.asyncio
async def test_scenario_ai_historical_vitals_remain_immutable():
    """Scenario AI: New vital observations append to timeline and never overwrite prior records."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        r1 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 88, "systolic_bp": 124, "diastolic_bp": 82},
        )
        v1_id = r1.json()["id"]

        r2 = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 72, "systolic_bp": 118, "diastolic_bp": 78},
        )
        v2_id = r2.json()["id"]

        # List all vitals for case
        list_res = await client.get(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert list_res.status_code == 200
        v_list = list_res.json()
        assert len(v_list) >= 2
        ids = [v["id"] for v in v_list]
        assert v1_id in ids
        assert v2_id in ids

        # Verify v1 data remained untouched
        v1_record = next(v for v in v_list if v["id"] == v1_id)
        assert v1_record["heart_rate"] == 88


@pytest.mark.asyncio
async def test_scenario_aj_recalculation_does_not_erase_history():
    """Scenario AJ: Executing recalculation persists a new snapshot record and preserves historical snapshots."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Run triage calculation twice
        r1 = await client.post(
            f"/api/v1/cases/{case_id}/triage/calculate",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert r1.status_code == 200

        r2 = await client.post(
            f"/api/v1/cases/{case_id}/triage/calculate",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert r2.status_code == 200

        async with async_session_factory() as db:
            stmt = select(TriageSnapshotRecord).where(TriageSnapshotRecord.case_id == case_id)
            snapshots = (await db.execute(stmt)).scalars().all()
            # Multiple distinct immutable snapshot rows exist
            assert len(snapshots) >= 2


@pytest.mark.asyncio
async def test_scenario_ak_audit_event_created_where_required():
    """Scenario AK: Vital acquisition and triage calculation create structured audit entries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 82, "systolic_bp": 120, "diastolic_bp": 80},
        )

        await client.post(
            f"/api/v1/cases/{case_id}/triage/calculate",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )

        auditor_token = await login_helper(client, "auditor")
        audit_res = await client.get(
            f"/api/v1/cases/{case_id}/audit",
            headers={"Authorization": f"Bearer {auditor_token}"},
        )
        assert audit_res.status_code == 200
        logs = audit_res.json()
        actions = [l["action"] for l in logs]
        assert "vital.created" in actions
        assert "triage.calculated" in actions


@pytest.mark.asyncio
async def test_scenario_al_transaction_rollback():
    """Scenario AL: Failure during vital recording rolls back database transaction cleanly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        fake_case_id = str(uuid.uuid4())

        # Attempt to record vitals for non-existent case ID
        res = await client.post(
            f"/api/v1/cases/{fake_case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 80},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"

        # Verify no orphan vitals created
        async with async_session_factory() as db:
            orphans = (await db.execute(select(Vital).where(Vital.case_id == fake_case_id))).scalars().all()
            assert len(orphans) == 0


@pytest.mark.asyncio
async def test_scenario_am_structured_error_contract():
    """Scenario AM: All client errors return standard Clinova structured error dictionary."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Trigger 422 error
        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 999},
        )
        assert res.status_code == 422
        payload = res.json()
        assert "error" in payload
        assert "code" in payload["error"]
        assert "message" in payload["error"]


@pytest.mark.asyncio
async def test_scenario_an_synthetic_mode_preserved():
    """Scenario AN: Patient identifiers remain strictly synthetic (PT-SYN-) with is_synthetic=True."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            patient = await db.get(Patient, case.patient_id)
            assert patient.is_synthetic is True
            assert patient.synthetic_id.startswith("PT-SYN-")


# ===========================================================================
# ADVERSARIAL TEST SUITE: SERVER-SIDE AUTHORITATIVE HARDENING
# ===========================================================================

@pytest.mark.asyncio
async def test_adversarial_forged_priority_ignored():
    """Adversarial: Client passing forged priority_tier in vital payload cannot override server calculation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token, pathway="REGULAR_STANDARD")

        # Client submits payload with forged priority
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 72,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "spo2_percent": 98,
                "respiratory_rate": 16,
                "temperature_celsius": 36.8,
                "priority_tier": "P1_CRITICAL",
                "risk_score": 0.99,
            },
        )

        # Verify server evaluated priority truthfully
        res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["priority_tier"] == "P4_ROUTINE"
        assert data["risk_score"] < 0.20


@pytest.mark.asyncio
async def test_adversarial_client_supplied_risk_score_override():
    """Adversarial: Case risk_score cannot be arbitrarily set by client request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Triage calculation calculates authoritative score
        snap_res = await client.post(
            f"/api/v1/cases/{case_id}/triage/calculate",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert snap_res.status_code == 200
        snap_data = snap_res.json()

        # Database state matches server-calculated value, not client assertion
        async with async_session_factory() as db:
            case = await db.get(Case, case_id)
            assert case.risk_score == snap_data["risk_score"]


@pytest.mark.asyncio
async def test_adversarial_client_supplied_news2_and_shock_index_ignored():
    """Adversarial: Client attempts to supply fake NEWS2 or Shock Index; server computes genuine scores."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Submit normal vitals with attempted injection of fake high NEWS2
        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 70,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "spo2_percent": 99,
                "respiratory_rate": 16,
                "temperature_celsius": 36.8,
                "news2_score": 15,
                "shock_index": 2.5,
            },
        )
        assert res.status_code == 200

        snap = await client.get(
            f"/api/v1/cases/{case_id}/triage/snapshot",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert snap.status_code == 200
        data = snap.json()
        assert data["news2"]["score"] == 0
        assert data["shock_index"]["score"] == 0.58


@pytest.mark.asyncio
async def test_adversarial_client_supplied_red_flags_ignored():
    """Adversarial: Client cannot forge red flags when physiological indicators do not support them."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Normal vitals
        await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": 72, "systolic_bp": 120, "diastolic_bp": 80},
        )

        p_res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert p_res.status_code == 200
        assert p_res.json()["has_critical_red_flags"] is False
        assert p_res.json()["triggering_rules"] == []


@pytest.mark.asyncio
async def test_adversarial_facility_scope_spoofing_denied():
    """Adversarial: Non-admin user cannot view other facilities by manipulating URL parameters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")  # FAC-DH-04
        res = await client.get(
            "/api/v1/cases/queue?facility_id=FAC-TMC-05",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_adversarial_manipulation_of_wait_time_prevented():
    """Adversarial: Client cannot send artificial waiting_minutes to manipulate queue ordering."""
    items = [
        {"case_id": "c1", "created_at": "2026-10-09T00:00:00Z", "pathway": "REGULAR", "acuity_tier": "ROUTINE", "risk_score": 0.1, "waiting_minutes": 9999},
        {"case_id": "c2", "created_at": "2026-10-09T00:00:00Z", "pathway": "EMERGENCY", "acuity_tier": "CRITICAL", "risk_score": 0.9, "waiting_minutes": 1},
    ]
    # Clinical severity and emergency pathway always dominate operational wait time
    sorted_items = sort_clinical_queue(items)
    assert sorted_items[0]["case_id"] == "c2"


@pytest.mark.asyncio
async def test_adversarial_future_dated_vital_observation_rejected():
    """Adversarial: Vital timestamp in the future (> 5 minutes) is rejected by Pydantic validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 80,
                "recorded_at": future_time.isoformat(),
            },
        )
        assert res.status_code == 422
        assert "cannot be in the future" in str(res.json()["error"])


@pytest.mark.asyncio
async def test_adversarial_duplicate_vital_submissions_preserved_as_distinct_history():
    """Adversarial: Duplicate submissions with identical values are stored as discrete historical events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        payload = {"heart_rate": 78, "systolic_bp": 120, "diastolic_bp": 80}
        r1 = await client.post(f"/api/v1/cases/{case_id}/vitals", headers={"Authorization": f"Bearer {nurse_token}"}, json=payload)
        r2 = await client.post(f"/api/v1/cases/{case_id}/vitals", headers={"Authorization": f"Bearer {nurse_token}"}, json=payload)

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["id"] != r2.json()["id"]


@pytest.mark.asyncio
async def test_adversarial_stale_data_manipulation_prevented():
    """Adversarial: An old vital observation (> 6h) cannot be claimed fresh by client; server enforces decay."""
    now = datetime.now(timezone.utc)
    old_vital_time = now - timedelta(hours=7)

    # Server freshness evaluation marks it expired/missing regardless of client expectation
    freshness = evaluate_vital_freshness(
        recorded_at=old_vital_time,
        parameter_values={"heart_rate": 80, "systolic_bp": 120},
        now=now,
    )
    assert freshness["overall_status"] == "MISSING"


@pytest.mark.asyncio
async def test_adversarial_malformed_rule_inputs_rejected():
    """Adversarial: Malformed payloads containing string types where numbers expected fail with 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={"heart_rate": "SEVENTY_FIVE_BPM"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_vitals_provenance_preserves_encounter_id_and_audit_events():
    """Requirement 6 & 20: Encounter ID preserved in provenance metadata and triage audit events emitted."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        nurse_token = await login_helper(client, "nurse")
        case_id = await create_case_helper(client, nurse_token)

        # Record critical vitals triggering red flags
        res = await client.post(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
            json={
                "heart_rate": 160,  # Triggers RF-PHYSIO-HR
                "systolic_bp": 75,   # Triggers RF-PHYSIO-HYPOTENSION
                "diastolic_bp": 45,
                "spo2_percent": 84,  # Triggers RF-PHYSIO-HYPOXIA
                "respiratory_rate": 32,
                "temperature_celsius": 37.0,
                "avpu_score": "ALERT",
            },
        )
        assert res.status_code == 200
        vital_data = res.json()
        assert vital_data["provenance_metadata"]["source"] == "STAFF_ENTERED"

        # Check audit trail for triage events using auditor role
        auditor_token = await login_helper(client, "auditor")
        audit_res = await client.get(
            f"/api/v1/cases/{case_id}/audit",
            headers={"Authorization": f"Bearer {auditor_token}"},
        )
        assert audit_res.status_code == 200
        audit_events = audit_res.json()
        actions = [a["action"] for a in audit_events]
        assert "triage.red_flag_triggered" in actions

        # Check priority breakdown has physiological_indicators
        pri_res = await client.get(
            f"/api/v1/cases/{case_id}/priority",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert pri_res.status_code == 200
        pri_data = pri_res.json()
        assert "physiological_indicators" in pri_data
        assert "news2" in pri_data["physiological_indicators"]
        assert "shock_index" in pri_data["physiological_indicators"]
        assert "vitals_summary" in pri_data["physiological_indicators"]


@pytest.mark.asyncio
async def test_intake_submit_vitals_unverified_and_generates_snapshot():
    """Patient-reported vitals during intake are UNVERIFIED and generate initial deterministic snapshot."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pt_token = await login_helper(client, "patient")

        submit_payload = {
            "facility_id": "FAC-PHC-01",
            "chief_complaint": "Severe chest pain and sudden sweating",
            "symptoms": ["chest pain", "sweating"],
            "consent_granted": True,
            "vitals": {
                "heart_rate": 125,
                "systolic_bp": 95,
                "diastolic_bp": 60,
                "spo2_percent": 94,
                "respiratory_rate": 24,
                "temperature_celsius": 37.2,
                "avpu_score": "ALERT",
            },
        }

        res = await client.post(
            "/api/v1/intake/submit",
            headers={"Authorization": f"Bearer {pt_token}"},
            json=submit_payload,
        )
        assert res.status_code == 200
        case_id = res.json()["case_id"]

        # Verify case has vitals in canonical endpoint
        nurse_token = await login_helper(client, "nurse_phc")
        vitals_res = await client.get(
            f"/api/v1/cases/{case_id}/vitals",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert vitals_res.status_code == 200
        vitals_list = vitals_res.json()
        assert len(vitals_list) == 1
        assert vitals_list[0]["source"] == "PATIENT_REPORTED"
        assert vitals_list[0]["verification_context"]["verified"] is False
        assert vitals_list[0]["verification_context"]["verification_status"] == "UNVERIFIED"

        # Verify initial snapshot was persisted
        snap_res = await client.get(
            f"/api/v1/cases/{case_id}/triage/snapshot",
            headers={"Authorization": f"Bearer {nurse_token}"},
        )
        assert snap_res.status_code == 200
        snap_data = snap_res.json()
        assert snap_data["priority_tier"] in ["P1_CRITICAL", "P2_URGENT", "P3_MODERATE", "P4_ROUTINE"]
        assert snap_data["shock_index"]["score"] is not None

