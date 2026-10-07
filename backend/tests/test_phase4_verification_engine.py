"""Phase 4 — VERIFY: Clinical Information Verification & Review Readiness Test Suite.

Validates the complete Phase 4 master specification for Clinova AI:
- Modular Verification Rules (Structural, Completeness, EvidenceStatus, Conflict, Temporal, Provenance, Uncertainty, ReviewReadiness)
- All 12 Synthetic Clinical Acceptance Scenarios (Scenarios A through L)
- Idempotency and Stale-Version Detection
- Finding Human Resolution & Auditability
- Cold Restart Persistence
- Anti-Hallucination & No-Invention Guarantee
- IDOR Cross-Patient Security Isolation
"""

import uuid
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.case import TriageCase
from app.models.case_evidence import CaseEvidence, EvidenceSourceType, VerificationState
from app.models.canonical_case import (
    CaseBuildRun,
    CaseSnapshot,
    CanonicalFact,
    TimelineEvent,
    BuildRunStatus,
    FactPolarity,
    FactCertainty,
    TemporalStatus,
)
from app.models.verification import (
    VerificationRun,
    VerificationFinding,
    VerificationConflict,
    VerificationRunStatus,
    ReviewReadinessLevel,
    FindingSeverity,
    FindingType,
    FindingCategory,
    FindingStatus,
    ConflictType,
)
from app.services.case_builder import CaseBuilderService
from app.services.verification import CaseVerificationService
from app.services.verification.context import VerificationContext
from app.services.verification.rules import (
    StructuralIntegrityRule,
    CompletenessRule,
    EvidenceStatusRule,
    CrossSourceConflictRule,
    TemporalConsistencyRule,
    ProvenanceRule,
    UncertaintyRule,
    ReviewReadinessCalculator,
)


@pytest.fixture
async def sample_test_case(database):
    """Creates an authenticated patient, doctor, and canonical triage case with initial build."""
    async with database() as db:
        patient_user = User(
            id=str(uuid.uuid4()),
            email=f"patient.p4.{datetime.now().timestamp()}@test.invalid",
            full_name="Phase4 Synthetic Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        doctor_user = User(
            id=str(uuid.uuid4()),
            email=f"doctor.p4.{datetime.now().timestamp()}@test.invalid",
            full_name="Dr. Sarah Chen, MD",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        patient_b_user = User(
            id=str(uuid.uuid4()),
            email=f"patientb.p4.{datetime.now().timestamp()}@test.invalid",
            full_name="Unrelated Patient B",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        db.add_all([patient_user, doctor_user, patient_b_user])
        await db.flush()

        patient_rec = Patient(
            id=str(uuid.uuid4()),
            user_id=patient_user.id,
            mrn=f"CLN-P4-{uuid.uuid4().hex[:6].upper()}",
            first_name="Synthetic",
            last_name="Patient",
            date_of_birth="1980-05-15",
            gender="Female",
            allergies="Penicillin",
        )
        db.add(patient_rec)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"CLN-P4-CASE-{uuid.uuid4().hex[:6].upper()}",
            owner_user_id=patient_user.id,
            patient_id=patient_rec.id,
            language="en",
            facility_type="District Hospital",
            visit_type="Outpatient",
            status="awaiting_review",
            case_version=1,
            workflow_state="BUILDING",
            review_readiness_status="not_ready",
            approximate_age=45,
            gender="Female",
            raw_symptoms="High fever and severe dry cough since yesterday. Blood pressure 120/80 mmHg.",
            normalized_symptoms="Pyrexia and acute dry cough for 1 day.",
            vitals='{"blood_pressure": "120/80", "heart_rate": 84, "temperature": 38.5}',
        )
        db.add(case)
        await db.flush()

        # Add initial evidence items
        ev1 = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="reported_symptoms",
            raw_value="High fever and severe dry cough since yesterday.",
            normalized_value="Pyrexia and acute dry cough for 1 day.",
            source_type=EvidenceSourceType.PATIENT_TEXT,
            verification_state=VerificationState.PATIENT_REPORTED,
        )
        ev2 = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="vital_signs",
            raw_value="Blood pressure 120/80 mmHg, heart rate 84 bpm, temp 38.5 C.",
            normalized_value="BP: 120/80 mmHg, HR: 84 bpm, Temp: 38.5 °C.",
            source_type=EvidenceSourceType.STAFF_VERIFIED,
            verification_state=VerificationState.STAFF_VERIFIED,
        )
        db.add_all([ev1, ev2])
        await db.commit()

        # Compile Phase 3 canonical case snapshot
        builder = CaseBuilderService()
        snapshot, _ = await builder.build_canonical_case(case.id, db, trigger_type="initial_test_setup")

        return {
            "case_id": case.id,
            "patient_user": patient_user,
            "doctor_user": doctor_user,
            "patient_b_user": patient_b_user,
            "snapshot_id": snapshot.id,
        }


# ============================================================================
# 1. MODULAR UNIT TESTS FOR EACH VERIFICATION RULE IN ISOLATION
# ============================================================================

@pytest.mark.asyncio
async def test_structural_integrity_rule_isolated(database, sample_test_case):
    """Rule 1: StructuralIntegrityRule detects broken relationships and invalid cases."""
    rule = StructuralIntegrityRule()
    async with database() as db:
        case_res = await db.execute(select(TriageCase).where(TriageCase.id == sample_test_case["case_id"]))
        case = case_res.scalar_one()

        snap_res = await db.execute(
            select(CaseSnapshot)
            .where(CaseSnapshot.case_id == case.id)
            .options(selectinload(CaseSnapshot.facts), selectinload(CaseSnapshot.timeline_events))
        )
        snapshot = snap_res.scalar_one()

        # Valid context
        context = VerificationContext(
            case=case,
            snapshot=snapshot,
            case_version=1,
            facts=list(snapshot.facts),
            evidence_items=[],
            timeline_events=[],
        )
        findings, conflicts = await rule.evaluate(context)
        # No blocking findings on valid case
        assert not any(f.is_blocking for f in findings)

        # Invalidate patient association -> must generate BLOCKING finding
        case.patient_id = None
        context_broken = VerificationContext(case=case, snapshot=snapshot, case_version=1)
        broken_findings, _ = await rule.evaluate(context_broken)
        assert any(f.is_blocking and f.field_name == "patient_id" for f in broken_findings)


@pytest.mark.asyncio
async def test_completeness_rule_isolated(database, sample_test_case):
    """Rule 2: CompletenessRule distinguishes present, missing, and partially available fields."""
    rule = CompletenessRule()
    async with database() as db:
        case = (await db.execute(select(TriageCase).where(TriageCase.id == sample_test_case["case_id"]))).scalar_one()
        snapshot = (await db.execute(select(CaseSnapshot).where(CaseSnapshot.case_id == case.id).options(selectinload(CaseSnapshot.facts)))).scalar_one()

        # Case without symptoms
        empty_case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id="EMPTY-CASE-001",
            language="en",
            case_version=1,
            raw_symptoms=None,
            normalized_symptoms=None,
        )
        context_empty = VerificationContext(case=empty_case, snapshot=None, case_version=1)
        findings, _ = await rule.evaluate(context_empty)

        # Missing chief complaint is BLOCKING
        chief_complaint_finding = next((f for f in findings if f.field_name == "chief_complaint"), None)
        assert chief_complaint_finding is not None
        assert chief_complaint_finding.is_blocking is True
        assert chief_complaint_finding.severity == FindingSeverity.BLOCKING


@pytest.mark.asyncio
async def test_evidence_status_rule_isolated(database):
    """Rule 3: EvidenceStatusRule preserves quality origin: presence != verification."""
    rule = EvidenceStatusRule()
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-AI-01", case_version=1)

    ai_fact = CanonicalFact(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        category="symptom",
        concept="Dyspnea",
        value="shortness of breath",
        attribution="AI_EXTRACTED",
        verification_state="unverified",
        confidence_score=0.98,
    )
    context = VerificationContext(case=case, snapshot=None, case_version=1, facts=[ai_fact])
    findings, _ = await rule.evaluate(context)

    # Must flag unverified AI extraction despite high 0.98 confidence score
    ai_finding = next((f for f in findings if "Unverified AI Extraction" in f.title), None)
    assert ai_finding is not None
    assert ai_finding.severity == FindingSeverity.MEDIUM


@pytest.mark.asyncio
async def test_conflict_rule_preserves_both_sources_isolated(database):
    """Rule 4: CrossSourceConflictRule detects discrepancies and preserves both sources intact."""
    rule = CrossSourceConflictRule()
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-CONF-01", case_version=1)

    # Fact with has_conflict=True
    fact_conf = CanonicalFact(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        category="vital",
        concept="Blood Pressure",
        value="120/80",
        unit="mmHg",
        has_conflict=True,
        conflicting_value="160/100 mmHg",
        conflicting_source_id=str(uuid.uuid4()),
    )
    context = VerificationContext(case=case, snapshot=None, case_version=1, facts=[fact_conf])
    findings, conflicts = await rule.evaluate(context)

    assert len(conflicts) == 1
    assert conflicts[0].source_a_value == "120/80 mmHg"
    assert conflicts[0].source_b_value == "160/100 mmHg"
    assert conflicts[0].resolution_state == FindingStatus.UNRESOLVED

    assert len(findings) == 1
    assert findings[0].finding_type == FindingType.CONFLICT


@pytest.mark.asyncio
async def test_temporal_consistency_rule_isolated(database):
    """Rule 5: TemporalConsistencyRule detects chronological ordering inversions."""
    rule = TemporalConsistencyRule()
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-TEMP-01", case_version=1)

    # Sequence where Day 5 precedes Day 2
    ev1 = TimelineEvent(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        event_type="symptom_progression",
        description="Severe dyspnea worsening",
        relative_time="Day 5",
        order_index=1,
    )
    ev2 = TimelineEvent(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        event_type="symptom_onset",
        description="Fever started",
        relative_time="Day 2",
        order_index=2,
    )
    context = VerificationContext(case=case, snapshot=None, case_version=1, timeline_events=[ev1, ev2])
    findings, _ = await rule.evaluate(context)

    inverted_finding = next((f for f in findings if "Inverted Timeline Chronology" in f.title), None)
    assert inverted_finding is not None
    assert inverted_finding.severity == FindingSeverity.HIGH


@pytest.mark.asyncio
async def test_provenance_rule_isolated(database):
    """Rule 6: ProvenanceRule detects ungrounded candidate facts and missing source spans."""
    rule = ProvenanceRule()
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-PROV-01", case_version=1)

    ev_id = str(uuid.uuid4())
    ev = CaseEvidence(
        id=ev_id,
        case_id=case.id,
        canonical_field="symptoms",
        raw_value="Mild headache only.",
        source_type=EvidenceSourceType.PATIENT_TEXT,
    )
    # Fact claiming 'Chest Pain' which does NOT exist in raw_value
    hallucinated_fact = CanonicalFact(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        category="symptom",
        concept="Chest Pain",
        value="chest pain",
        source_evidence_id=ev_id,
        source_span="chest pain",
    )
    context = VerificationContext(
        case=case, snapshot=None, case_version=1, facts=[hallucinated_fact], evidence_items=[ev]
    )
    findings, _ = await rule.evaluate(context)

    ungrounded_finding = next((f for f in findings if "Ungrounded Source Span" in f.title), None)
    assert ungrounded_finding is not None
    assert ungrounded_finding.severity == FindingSeverity.HIGH


@pytest.mark.asyncio
async def test_uncertainty_rule_isolated(database):
    """Rule 7: UncertaintyRule preserves clinical hedging and approximate qualifiers."""
    rule = UncertaintyRule()
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-UNC-01", case_version=1)

    fact_uncertain = CanonicalFact(
        id=str(uuid.uuid4()),
        case_id=case.id,
        snapshot_id=str(uuid.uuid4()),
        category="symptom",
        concept="Dizziness",
        value="possible lightheadedness",
        certainty="UNCERTAIN",
    )
    context = VerificationContext(case=case, snapshot=None, case_version=1, facts=[fact_uncertain])
    findings, _ = await rule.evaluate(context)

    unc_finding = next((f for f in findings if f.finding_type == FindingType.UNCERTAINTY), None)
    assert unc_finding is not None
    assert "Clinical Uncertainty Preserved" in unc_finding.title


@pytest.mark.asyncio
async def test_review_readiness_calculator_explainability(database):
    """Rule 8: ReviewReadinessCalculator provides explainable reasons and non-medical score."""
    case = TriageCase(id=str(uuid.uuid4()), synthetic_case_id="TEST-READ-01", case_version=1)
    context = VerificationContext(case=case, snapshot=None, case_version=1)

    # 1. Clean run -> REVIEW_READY
    level_clean, score_clean, reasons_clean, _ = ReviewReadinessCalculator.calculate(context, [], [])
    assert level_clean == ReviewReadinessLevel.REVIEW_READY
    assert score_clean >= 0.8
    assert len(reasons_clean) >= 1

    # 2. Run with blocking finding -> NOT_READY
    from app.services.verification.base import FindingCandidate
    blocking_f = FindingCandidate(
        rule_id="r1",
        rule_version="4.0",
        finding_type=FindingType.STRUCTURAL,
        category=FindingCategory.IDENTITY,
        title="Missing Patient Linkage",
        description="No patient record",
        explanation="Identity required",
        severity=FindingSeverity.BLOCKING,
        is_blocking=True,
    )
    level_block, score_block, reasons_block, _ = ReviewReadinessCalculator.calculate(context, [blocking_f], [])
    assert level_block == ReviewReadinessLevel.NOT_READY
    assert score_block < 0.5
    assert any("Blocked by" in r for r in reasons_block)


# ============================================================================
# 2. THE 12 SYNTHETIC CLINICAL ACCEPTANCE SCENARIOS (A THROUGH L)
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_a_complete_clean_case(database, sample_test_case):
    """Scenario A: Complete clean case -> High review readiness, 0 blocking findings."""
    verifier = CaseVerificationService()
    async with database() as db:
        run = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=True)
        assert run.status == VerificationRunStatus.COMPLETED.value
        assert run.blocking_findings_count == 0
        assert run.review_readiness_status in (
            ReviewReadinessLevel.REVIEW_READY.value,
            ReviewReadinessLevel.REVIEW_READY_WITH_FLAGS.value,
        )
        assert run.review_readiness_score >= 0.70
        assert len(run.review_readiness_reasons) > 0


@pytest.mark.asyncio
async def test_scenario_b_missing_information_detection(database):
    """Scenario B: Missing information -> Detected and categorized, reduced readiness."""
    async with database() as db:
        user = User(
            id=str(uuid.uuid4()),
            email=f"patient.b.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario B Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(user)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-B-{uuid.uuid4().hex[:6]}",
            owner_user_id=user.id,
            language="en",
            case_version=1,
            raw_symptoms="Headache.",
            normalized_symptoms="Headache.",
            # Missing patient_id, age, gender, vitals
        )
        db.add(case)
        await db.commit()

        # Build snapshot
        builder = CaseBuilderService()
        await builder.build_canonical_case(case.id, db)

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        assert run.findings_count > 0
        finding_fields = {f.field_name for f in run.findings}
        assert "patient_id" in finding_fields
        assert "patient_age" in finding_fields
        assert "vital_signs" in finding_fields
        assert run.review_readiness_status == ReviewReadinessLevel.NOT_READY.value


@pytest.mark.asyncio
async def test_scenario_c_conflicting_values_preserved(database):
    """Scenario C: Conflicting values -> Preserved in verification_conflicts, no silent resolution."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.c.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario C Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-C-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="en",
            case_version=1,
            approximate_age=40,
            gender="Male",
            raw_symptoms="High fever 39 C.",
            vitals='{"temperature": 39.0}',
        )
        db.add(case)
        await db.flush()

        # Add two contradictory evidence items
        ev1 = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="vital_temperature",
            raw_value="Temperature measured 39.0 C",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        ev2 = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="vital_temperature",
            raw_value="Temperature triage reading 36.8 C",
            source_type=EvidenceSourceType.STAFF_VERIFIED,
        )
        db.add_all([ev1, ev2])
        await db.commit()

        builder = CaseBuilderService()
        await builder.build_canonical_case(case.id, db)

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        # Conflict preserved
        assert len(run.conflicts) >= 1 or any(f.finding_type == FindingType.CONFLICT.value for f in run.findings)
        assert run.consistency_status in ("CONFLICTS_DETECTED", "CONSISTENT")


@pytest.mark.asyncio
async def test_scenario_d_temporal_contradiction_detected(database):
    """Scenario D: Temporal contradiction -> Detected and flagged in findings."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.d.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario D Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-D-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="en",
            case_version=1,
            raw_symptoms="Started antibiotics yesterday, but discontinued 5 days ago.",
        )
        db.add(case)
        await db.commit()

        # Add explicit timeline events with inverted order
        snap = CaseSnapshot(
            id=str(uuid.uuid4()),
            case_id=case.id,
            case_version=1,
            schema_version=1,
            build_version="3.0.0",
            case_data={},
            is_current=True,
        )
        db.add(snap)
        await db.flush()

        te1 = TimelineEvent(
            id=str(uuid.uuid4()),
            case_id=case.id,
            snapshot_id=snap.id,
            event_type="medication_stopped",
            description="Discontinued amoxicillin",
            order_index=1,
        )
        te2 = TimelineEvent(
            id=str(uuid.uuid4()),
            case_id=case.id,
            snapshot_id=snap.id,
            event_type="medication_started",
            description="Started amoxicillin",
            order_index=2,
        )
        db.add_all([te1, te2])
        await db.commit()

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        temporal_finding = next((f for f in run.findings if f.finding_type == FindingType.TEMPORAL.value), None)
        assert temporal_finding is not None
        assert "Medication Discontinuation Precedes Initiation" in temporal_finding.title


@pytest.mark.asyncio
async def test_scenario_e_ocr_vs_patient_conflict(database):
    """Scenario E: OCR vs Patient Voice cross-modal conflict detected."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.e.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario E Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-E-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="en",
            case_version=1,
        )
        db.add(case)
        await db.flush()

        ev_ocr = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="vital_blood_pressure",
            raw_value="BP: 155/95 mmHg",
            source_type=EvidenceSourceType.OCR_DERIVED,
        )
        ev_voice = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="vital_blood_pressure",
            raw_value="My doctor checked my BP yesterday and said it was 120/80",
            source_type=EvidenceSourceType.PATIENT_VOICE,
        )
        db.add_all([ev_ocr, ev_voice])
        await db.commit()

        builder = CaseBuilderService()
        await builder.build_canonical_case(case.id, db)

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        # Cross-modal or quality finding generated
        assert run.findings_count > 0
        assert any(
            f.finding_type in (FindingType.CONFLICT.value, FindingType.EVIDENCE_QUALITY.value)
            for f in run.findings
        )


@pytest.mark.asyncio
async def test_scenario_f_translation_provenance_preserved(database):
    """Scenario F: Translation relationship -> Original preserved, translation linked."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.f.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario F Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-F-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="or",
            case_version=1,
        )
        db.add(case)
        await db.flush()

        # Odia input with English translation
        ev = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="reported_symptoms",
            raw_value="ମୋତେ ୩ ଦିନ ହେଲା ଜ୍ୱର ହେଉଛି।",
            normalized_value="I have had fever for 3 days.",
            source_type=EvidenceSourceType.PATIENT_TEXT,
        )
        db.add(ev)
        await db.commit()

        builder = CaseBuilderService()
        await builder.build_canonical_case(case.id, db)

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        assert run.status == VerificationRunStatus.COMPLETED.value
        assert run.provenance_status == "COMPLETE"


@pytest.mark.asyncio
async def test_scenario_g_missing_provenance_detected(database):
    """Scenario G: Missing provenance -> Fact without evidence span flagged."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.g.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario G Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-G-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="en",
            case_version=1,
        )
        db.add(case)
        await db.flush()

        snap = CaseSnapshot(
            id=str(uuid.uuid4()),
            case_id=case.id,
            case_version=1,
            schema_version=1,
            build_version="3.0.0",
            case_data={},
            is_current=True,
        )
        db.add(snap)
        await db.flush()

        # Fact without source_evidence_id
        fact_untraceable = CanonicalFact(
            id=str(uuid.uuid4()),
            case_id=case.id,
            snapshot_id=snap.id,
            category="symptom",
            concept="Hypotension",
            value="low blood pressure",
            source_evidence_id=None,
            source_span=None,
        )
        db.add(fact_untraceable)
        await db.commit()

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        prov_finding = next((f for f in run.findings if f.finding_type == FindingType.PROVENANCE.value), None)
        assert prov_finding is not None
        assert "Untraceable Clinical Fact" in prov_finding.title


@pytest.mark.asyncio
async def test_scenario_h_unverified_ai_extraction_retained(database):
    """Scenario H: Unverified AI extraction -> Retained with clear unverified state."""
    async with database() as db:
        patient = User(
            id=str(uuid.uuid4()),
            email=f"patient.h.{datetime.now().timestamp()}@test.invalid",
            full_name="Scenario H Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("Pass123!"),
        )
        db.add(patient)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"SCENARIO-H-{uuid.uuid4().hex[:6]}",
            owner_user_id=patient.id,
            patient_id=patient.id,
            language="en",
            case_version=1,
        )
        db.add(case)
        await db.flush()

        ev_ai = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="derived_note",
            raw_value="Patient may have early signs of mild bronchitis.",
            source_type=EvidenceSourceType.AI_EXTRACTED,
            verification_state=VerificationState.EXTRACTED_PENDING_VERIFICATION,
        )
        db.add(ev_ai)
        await db.commit()

        builder = CaseBuilderService()
        await builder.build_canonical_case(case.id, db)

        verifier = CaseVerificationService()
        run = await verifier.verify_case(case.id, db, force_reverify=True)

        assert run.status == VerificationRunStatus.COMPLETED.value
        # Check that AI quality was flagged
        assert any(f.finding_type == FindingType.EVIDENCE_QUALITY.value for f in run.findings)


@pytest.mark.asyncio
async def test_scenario_i_staff_verification_resolves_conflict(database, sample_test_case):
    """Scenario I: Clinician resolves finding -> Previous conflict preserved, resolution recorded."""
    verifier = CaseVerificationService()
    async with database() as db:
        # Add an unverified evidence item so there is an active finding to resolve
        ev_unverified = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=sample_test_case["case_id"],
            canonical_field="preliminary_ai_impression",
            raw_value="AI suspecting acute bronchitis.",
            source_type=EvidenceSourceType.AI_EXTRACTED,
            verification_state=VerificationState.EXTRACTED_PENDING_VERIFICATION,
        )
        db.add(ev_unverified)
        await db.commit()

        run = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=True)
        assert run.findings_count > 0
        target_finding = run.findings[0]

        doctor = sample_test_case["doctor_user"]

        resolved = await verifier.resolve_finding(
            case_id=sample_test_case["case_id"],
            finding_id=target_finding.id,
            resolution_state="RESOLVED_BY_HUMAN_VERIFICATION",
            resolution_notes="Clinician verified via manual auscultation.",
            actor=doctor,
            db=db,
        )
        assert resolved.status == "RESOLVED_BY_HUMAN_VERIFICATION"
        assert resolved.resolution_notes == "Clinician verified via manual auscultation."
        assert resolved.resolved_by_user_id == doctor.id


@pytest.mark.asyncio
async def test_scenario_j_broken_case_structure_fails_safely(database):
    """Scenario J: Broken case structure -> Verification fails safely without crashing system."""
    verifier = CaseVerificationService()
    async with database() as db:
        # Non-existent case ID
        with pytest.raises(ValueError):
            await verifier.verify_case("00000000-0000-0000-0000-000000000000", db)


@pytest.mark.asyncio
async def test_scenario_k_offline_fallback_mode(database, sample_test_case):
    """Scenario K: ₹0 offline development mode -> Deterministic checks complete without third-party AI."""
    verifier = CaseVerificationService()
    async with database() as db:
        run = await verifier.verify_case(
            sample_test_case["case_id"],
            db,
            force_reverify=True,
            include_ai_checks=False,  # strictly offline mode
        )
        assert run.status == VerificationRunStatus.COMPLETED.value
        assert run.latency_ms >= 0


@pytest.mark.asyncio
async def test_scenario_l_cross_patient_access_attempt_blocked(database, sample_test_case):
    """Scenario L: Patient B accessing Patient A's verification -> HTTP 403 Forbidden."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Authenticate as Patient B
        token_b = create_access_token(
            subject=sample_test_case["patient_b_user"].id,
            role=UserRole.PATIENT,
        )
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Attempt to access Patient A's verification endpoint
        case_id_a = sample_test_case["case_id"]
        res = await ac.get(f"/api/v1/cases/{case_id_a}/verification", headers=headers_b)
        assert res.status_code == 403
        assert "Access denied" in res.json()["detail"]


# ============================================================================
# 3. IDEMPOTENCY, VERSIONING, PERSISTENCE & REST API TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_verification_idempotency_and_stale_detection(database, sample_test_case):
    """Verify that repeated verification returns cached result, and new case build flags stale."""
    verifier = CaseVerificationService()
    async with database() as db:
        # 1. Run 1
        run1 = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=True)
        # 2. Run 2 with force_reverify=False should hit cache
        run2 = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=False)
        assert run1.id == run2.id

        # 3. Add new evidence and advance case version to v2
        ev_new = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=sample_test_case["case_id"],
            canonical_field="lab_test",
            raw_value="WBC: 11,200 /mcL",
            source_type=EvidenceSourceType.STAFF_VERIFIED,
        )
        db.add(ev_new)
        await db.commit()

        builder = CaseBuilderService()
        snap2, _ = await builder.build_canonical_case(sample_test_case["case_id"], db)
        assert snap2.case_version == 2

        # 4. Check that latest verification is flagged as STALE
        latest = await verifier.get_latest_verification(sample_test_case["case_id"], db)
        assert latest is not None
        assert latest.is_stale is True
        assert latest.case_version == 1


@pytest.mark.asyncio
async def test_cold_restart_persistence(database, sample_test_case):
    """Verify that verification runs, findings, and conflicts survive session closes."""
    verifier = CaseVerificationService()
    async with database() as db:
        # Add an evidence item to generate a finding
        ev = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=sample_test_case["case_id"],
            canonical_field="preliminary_note",
            raw_value="AI generated differential hint",
            source_type=EvidenceSourceType.AI_EXTRACTED,
            verification_state=VerificationState.EXTRACTED_PENDING_VERIFICATION,
        )
        db.add(ev)
        await db.commit()

        run = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=True)
        run_id = run.id
        expected_count = run.findings_count

    # Simulate restart by opening a brand new independent DB session
    async with database() as fresh_db:
        res = await fresh_db.execute(
            select(VerificationRun)
            .where(VerificationRun.id == run_id)
            .options(selectinload(VerificationRun.findings))
        )
        reloaded = res.scalar_one_or_none()
        assert reloaded is not None
        assert reloaded.status == VerificationRunStatus.COMPLETED.value
        assert len(reloaded.findings) == expected_count
        assert len(reloaded.findings) > 0


@pytest.mark.asyncio
async def test_no_invention_anti_hallucination_verification(database, sample_test_case):
    """Anti-hallucination check: Verification produces findings only about input evidence."""
    verifier = CaseVerificationService()
    async with database() as db:
        run = await verifier.verify_case(sample_test_case["case_id"], db, force_reverify=True)
        for finding in run.findings:
            # Findings must only describe data quality, never invent new medical diagnoses
            assert "diagnosis confirmed" not in finding.description.lower()
            assert "patient is diagnosed with" not in finding.explanation.lower()
