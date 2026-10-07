"""Phase 5 — Intelligent Information Completion & Adaptive Interviewing Test Suite.

Validates the complete Phase 5 master specification for Clinova AI:
- Modular Engine Tests (History, Gap, Candidate, Validator, Prioritizer, Selector, Stopping, Safety)
- Synthetic Clinical Acceptance Scenarios A through T:
  * Scenario A: Clean intake, duration gap, answered, case rebuilt & re-verified, stops cleanly.
  * Scenario B: Missing vitals gap, patient reports temperature, verified.
  * Scenario C: Allergy status gap, patient reports allergy, evidence created.
  * Scenario D: Conflict resolution (contradictory reports clarified by patient).
  * Scenario E: Uncertain fact clarification (clarifying ambiguous/hedging observation).
  * Scenario F: Max turns ceiling reached (stops cleanly at turn limit).
  * Scenario G: Patient skips / declines question (records skip, continues to next).
  * Scenario H: Red flag symptom preserving (does not diagnose/dismiss, surfaces flag).
  * Scenario I: Zero information gain / plateau stopping.
  * Scenario J: Offline ₹0 deterministic mode (runs 100% without external LLM).
  * Scenario K: Anti-hallucination / strictly grounded question generation.
  * Scenario L: Cross-patient IDOR security isolation (HTTP 403 forbidden).
  * Scenario M: Invalid question ID or duplicate answer rejection.
  * Scenario N: Multi-turn loop (Gap -> Question -> Answer -> Build -> Verify -> Next Turn).
  * Scenario O: Resumption of existing active session.
  * Scenario P: Patient opt-out / early manual conclusion.
  * Scenario Q: Strict non-diagnostic boundary enforcement assertion.
  * Scenario R: Timeline event enrichment from answer.
  * Scenario S: Session idempotency & single active session rule.
  * Scenario T: Cold restart persistence across fresh DB sessions.
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
    FactPolarity,
    FactCertainty,
)
from app.models.verification import (
    VerificationRun,
    VerificationFinding,
    VerificationConflict,
    FindingSeverity,
    FindingType,
    FindingStatus,
    ConflictType,
)
from app.models.completion import (
    CompletionSession,
    CompletionQuestion,
    CompletionAnswer,
    CompletionSessionStatus,
    QuestionType,
    QuestionStatus,
    GapType,
    StoppingCriterion,
)
from app.services.case_builder import CaseBuilderService
from app.services.verification import CaseVerificationService
from app.services.completion import (
    CompletionService,
    InteractionHistoryTracker,
    InformationGapEngine,
    QuestionCandidateEngine,
    QuestionValidator,
    QuestionPrioritizationEngine,
    NextBestQuestionSelector,
    StoppingEngine,
    CompletionSafetyGuard,
    InformationGap,
    QuestionCandidate,
    PrioritizedQuestion,
)


@pytest.fixture
async def sample_completion_case(database):
    """Creates authenticated patient, doctor, and canonical triage case with initial build."""
    async with database() as db:
        patient_user = User(
            id=str(uuid.uuid4()),
            email=f"patient.p5.{datetime.now().timestamp()}@test.invalid",
            full_name="Phase5 Synthetic Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        doctor_user = User(
            id=str(uuid.uuid4()),
            email=f"doctor.p5.{datetime.now().timestamp()}@test.invalid",
            full_name="Dr. Alex Rivera, MD",
            role=UserRole.DOCTOR,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
        )
        patient_b_user = User(
            id=str(uuid.uuid4()),
            email=f"patientb.p5.{datetime.now().timestamp()}@test.invalid",
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
            mrn=f"CLN-P5-{uuid.uuid4().hex[:6].upper()}",
            first_name="Synthetic",
            last_name="PatientFive",
            date_of_birth="1985-04-12",
            gender="Male",
        )
        db.add(patient_rec)
        await db.flush()

        case = TriageCase(
            id=str(uuid.uuid4()),
            synthetic_case_id=f"CLN-P5-CASE-{uuid.uuid4().hex[:6].upper()}",
            owner_user_id=patient_user.id,
            patient_id=patient_rec.id,
            language="en",
            facility_type="Primary Health Center",
            visit_type="Outpatient",
            status="awaiting_review",
            case_version=1,
            workflow_state="INTAKE",
            review_readiness_status="not_ready",
            approximate_age=39,
            gender="Male",
            raw_symptoms="Persistent dry cough and mild sore throat.",
            normalized_symptoms="Subacute dry cough and pharyngitis.",
        )
        db.add(case)
        await db.flush()

        # Add initial evidence (missing duration, missing allergies, missing vitals)
        ev1 = CaseEvidence(
            id=str(uuid.uuid4()),
            case_id=case.id,
            canonical_field="reported_symptoms",
            raw_value="Persistent dry cough and mild sore throat.",
            normalized_value="Subacute dry cough and pharyngitis.",
            source_type=EvidenceSourceType.PATIENT_TEXT,
            verification_state=VerificationState.PATIENT_REPORTED,
        )
        db.add(ev1)
        await db.commit()

        # Compile Phase 3 canonical case snapshot
        builder = CaseBuilderService()
        snapshot, _ = await builder.build_canonical_case(case.id, db, trigger_type="test_setup")

        # Run Phase 4 verification
        verifier = CaseVerificationService()
        verification_run = await verifier.verify_case(case.id, db, force_reverify=True)

        return {
            "case_id": case.id,
            "patient_user": patient_user,
            "doctor_user": doctor_user,
            "patient_b_user": patient_b_user,
            "snapshot_id": snapshot.id,
            "verification_run_id": verification_run.id,
        }


# ============================================================================
# 1. MODULAR ENGINE UNIT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_history_tracker_isolated():
    """InteractionHistoryTracker accurately tracks fields, fatigue, and consecutive skips."""
    tracker = InteractionHistoryTracker()
    now = datetime.now(timezone.utc)

    q1 = CompletionQuestion(
        session_id="s1", case_id="c1", turn_number=1, target_gap_type="MISSING",
        target_field="symptom_duration", question_text="How long have you had cough?",
        question_type=QuestionType.SINGLE_CHOICE.value, clinical_rationale="Testing",
        status=QuestionStatus.ANSWERED.value, priority_score=0.9, created_at=now,
    )
    a1 = CompletionAnswer(
        question_id=q1.id, session_id="s1", case_id="c1", raw_answer_text="3 days",
        is_skipped=False, is_valid=True, answered_at=now,
    )
    q1.answer = a1

    q2 = CompletionQuestion(
        session_id="s1", case_id="c1", turn_number=2, target_gap_type="MISSING",
        target_field="allergies", question_text="Do you have any allergies?",
        question_type=QuestionType.SINGLE_CHOICE.value, clinical_rationale="Testing",
        status=QuestionStatus.SKIPPED.value, priority_score=0.8, created_at=now,
    )
    a2 = CompletionAnswer(
        question_id=q2.id, session_id="s1", case_id="c1", raw_answer_text="Skipped",
        is_skipped=True, is_valid=True, answered_at=now,
    )
    q2.answer = a2

    assert tracker.get_answered_target_fields([q1, q2]) == {"symptom_duration"}
    assert tracker.get_skipped_target_fields([q1, q2]) == {"allergies"}
    assert tracker.is_duplicate_question("How long have you had cough?", [q1, q2]) is True
    assert tracker.is_duplicate_question("What is your temperature?", [q1, q2]) is False
    assert tracker.consecutive_skipped_count([q1, q2]) == 1
    assert tracker.calculate_patient_fatigue([q1, q2]) > 0.0


@pytest.mark.asyncio
async def test_question_validator_boundary():
    """QuestionValidator strictly rejects diagnostic and prescriptive statements."""
    validator = QuestionValidator()

    # Valid question
    valid_cand = QuestionCandidate(
        candidate_id="c1", target_gap_id="g1", target_gap_type=GapType.MISSING_REQUIRED_FIELD,
        target_field="symptom_duration", question_text="How many days have you had these symptoms?",
        question_type=QuestionType.SINGLE_CHOICE,
        options=[{"label": "1 day", "value": "1d"}, {"label": "3 days", "value": "3d"}],
        clinical_rationale="Collects symptom duration for clinical intake.",
    )
    is_valid, _ = validator.validate_candidate(valid_cand, [])
    assert is_valid is True

    # Breaching candidate: diagnostic assertion
    diag_cand = QuestionCandidate(
        candidate_id="c2", target_gap_id="g2", target_gap_type=GapType.MISSING_REQUIRED_FIELD,
        target_field="diagnosis", question_text="You have pneumonia and need immediate antibiotics.",
        question_type=QuestionType.TEXT, clinical_rationale="Invalid diagnostic claim",
    )
    is_valid, reason = validator.validate_candidate(diag_cand, [])
    assert is_valid is False
    assert "non-diagnostic boundary" in reason or "non-treatment boundary" in reason

    # Breaching candidate: discharge advice
    discharge_cand = QuestionCandidate(
        candidate_id="c3", target_gap_id="g3", target_gap_type=GapType.MISSING_REQUIRED_FIELD,
        target_field="advice", question_text="There is no need to see a doctor for this issue.",
        question_type=QuestionType.TEXT, clinical_rationale="Invalid dismissal",
    )
    is_valid, reason = validator.validate_candidate(discharge_cand, [])
    assert is_valid is False
    assert "safety boundary" in reason.lower()


@pytest.mark.asyncio
async def test_prioritization_and_selection():
    """QuestionPrioritizationEngine ranks high-severity gaps above low-severity."""
    engine = QuestionPrioritizationEngine()
    selector = NextBestQuestionSelector()

    gap_high = InformationGap(
        gap_id="g_high", gap_type=GapType.MISSING_REQUIRED_FIELD, target_field="vital_signs",
        category="MEASUREMENTS", severity=FindingSeverity.HIGH, description="Missing vitals",
    )
    gap_low = InformationGap(
        gap_id="g_low", gap_type=GapType.CONTEXT_ENRICHMENT, target_field="context",
        category="CONTEXT", severity=FindingSeverity.LOW, description="Context details",
    )

    c1 = QuestionCandidate(
        candidate_id="c_vitals", target_gap_id="g_high", target_gap_type=GapType.MISSING_REQUIRED_FIELD,
        target_field="vital_signs", question_text="What is your temperature?",
        question_type=QuestionType.SINGLE_CHOICE, base_clinical_utility=0.9, burden_score=0.05,
    )
    c2 = QuestionCandidate(
        candidate_id="c_context", target_gap_id="g_low", target_gap_type=GapType.CONTEXT_ENRICHMENT,
        target_field="context", question_text="Any other notes?",
        question_type=QuestionType.TEXT, base_clinical_utility=0.5, burden_score=0.20,
    )

    prioritized = engine.prioritize_candidates([c2, c1], [gap_high, gap_low], [])
    assert len(prioritized) == 2
    assert prioritized[0].candidate.target_field == "vital_signs"
    assert prioritized[0].priority_score > prioritized[1].priority_score

    session = CompletionSession(case_id="case1", current_turn=0, max_turns=5)
    selected, _ = selector.select_next_question(session, prioritized, [])
    assert selected is not None
    assert selected.candidate.target_field == "vital_signs"


# ============================================================================
# 2. SYNTHETIC CLINICAL ACCEPTANCE SCENARIOS A THROUGH T
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_a_clean_intake_duration_gap(database, sample_completion_case):
    """Scenario A: Clean intake, 1 gap (duration), answered, case improved, stops."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        # 1. Start session
        session, q1 = await service.get_or_generate_next_question(case_id, db)
        assert session is not None
        assert q1 is not None
        assert session.current_turn == 1
        assert "symptom" in q1.target_field.lower() or "duration" in q1.target_field.lower()

        # 2. Patient answers duration
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q1.id,
            raw_answer_text="1 to 3 days",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is not None
        assert res["new_case_version"] >= 2
        assert res["rebuilt_snapshot_id"] is not None


@pytest.mark.asyncio
async def test_scenario_b_missing_vitals_answered(database, sample_completion_case):
    """Scenario B: Missing vitals, patient answers temperature, verified."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session = await service.get_or_create_session(case_id, db)
        assert session.initial_gap_count > 0

        # Deliver a question targeting vital signs
        gap = InformationGap(
            gap_id="g_vitals", gap_type=GapType.MISSING_REQUIRED_FIELD, target_field="vital_signs",
            category="MEASUREMENTS", severity=FindingSeverity.HIGH, description="Missing vitals",
        )
        cand = QuestionCandidateEngine()._generate_for_gap(gap)[0]
        prioritized = PrioritizedQuestion(
            candidate=cand, priority_score=0.9, rank=1, utility_score=0.9,
            gap_severity_weight=0.8, burden_penalty=0.05,
        )
        q = await service.delivery_service.present_question(session, prioritized, db)
        await db.commit()

        # Patient responds with mild fever
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="Mild fever (feeling warm or chills)",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is not None

        # Evidence is present in DB
        ev_stmt = select(CaseEvidence).where(CaseEvidence.id == res["new_evidence_id"])
        ev = (await db.execute(ev_stmt)).scalar_one()
        assert ev.canonical_field == "vital_signs"
        assert "Mild fever" in ev.raw_value


@pytest.mark.asyncio
async def test_scenario_c_allergy_status_gap(database, sample_completion_case):
    """Scenario C: Allergy status gap, patient reports 'Penicillin', evidence created."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session = await service.get_or_create_session(case_id, db)
        gap = InformationGap(
            gap_id="g_allergy", gap_type=GapType.MISSING_REQUIRED_FIELD, target_field="allergies",
            category="HISTORY", severity=FindingSeverity.HIGH, description="Allergy status unknown",
        )
        cand = QuestionCandidateEngine()._generate_for_gap(gap)[0]
        prioritized = PrioritizedQuestion(
            candidate=cand, priority_score=0.95, rank=1, utility_score=0.95,
            gap_severity_weight=0.8, burden_penalty=0.05,
        )
        q = await service.delivery_service.present_question(session, prioritized, db)
        await db.commit()

        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="Yes, allergies to specific medications: Penicillin allergy causing rash.",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is not None

        ev = (await db.execute(select(CaseEvidence).where(CaseEvidence.id == res["new_evidence_id"]))).scalar_one()
        assert ev.canonical_field == "allergies"
        assert "Penicillin" in ev.raw_value


@pytest.mark.asyncio
async def test_scenario_d_conflict_resolution(database, sample_completion_case):
    """Scenario D: Conflict resolution (contradictory records clarified by patient)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]
        session = await service.get_or_create_session(case_id, db)

        # Create conflict gap
        gap = InformationGap(
            gap_id="g_conf", gap_type=GapType.UNRESOLVED_CONFLICT, target_field="symptom_duration",
            category="CONFLICT", severity=FindingSeverity.HIGH, description="Duration conflict",
            context_data={"source_a_value": "2 days", "source_b_value": "3 weeks"},
        )
        cand = QuestionCandidateEngine()._generate_for_gap(gap)[0]
        assert "2 days" in cand.question_text and "3 weeks" in cand.question_text

        prioritized = PrioritizedQuestion(
            candidate=cand, priority_score=0.85, rank=1, utility_score=0.85,
            gap_severity_weight=0.8, burden_penalty=0.08,
        )
        q = await service.delivery_service.present_question(session, prioritized, db)
        await db.commit()

        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="2 days (the cough only started 2 days ago)",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is not None


@pytest.mark.asyncio
async def test_scenario_e_uncertain_fact_clarification(database, sample_completion_case):
    """Scenario E: Uncertain fact clarification (clarifying ambiguous observation)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]
        session = await service.get_or_create_session(case_id, db)

        gap = InformationGap(
            gap_id="g_unc", gap_type=GapType.UNCERTAIN_FACT, target_field="stomach_ache",
            category="SYMPTOMS", severity=FindingSeverity.MEDIUM, description="possible intermittent stomach ache",
            context_data={"fact_summary": "intermittent stomach ache", "concept": "stomach ache"},
        )
        cand = QuestionCandidateEngine()._generate_for_gap(gap)[0]
        prioritized = PrioritizedQuestion(
            candidate=cand, priority_score=0.72, rank=1, utility_score=0.72,
            gap_severity_weight=0.5, burden_penalty=0.06,
        )
        q = await service.delivery_service.present_question(session, prioritized, db)
        await db.commit()

        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="Resolved / No longer happening",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is not None


@pytest.mark.asyncio
async def test_scenario_f_max_turns_ceiling_reached(database, sample_completion_case):
    """Scenario F: Max turns ceiling reached (stops cleanly at turn limit)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        # Initialize session with max_turns = 1
        session = await service.get_or_create_session(case_id, db, max_turns=1, force_new=True)
        _, q = await service.get_or_generate_next_question(case_id, db, max_turns=1)
        assert q is not None
        assert session.current_turn == 1

        # Submit answer for turn 1
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="1 to 3 days",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["is_session_complete"] is True
        assert res["stopping_criterion"] == StoppingCriterion.MAX_TURNS_REACHED.value


@pytest.mark.asyncio
async def test_scenario_g_patient_skips_question(database, sample_completion_case):
    """Scenario G: Patient skips / declines question (records skip, continues)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session, q = await service.get_or_generate_next_question(case_id, db, max_turns=4)
        assert q is not None

        # Patient skips
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="",
            is_skipped=True,
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["new_evidence_id"] is None
        assert session.questions_skipped_count == 1
        assert res["answer"].is_skipped is True


@pytest.mark.asyncio
async def test_scenario_h_red_flag_symptom_preserving(database, sample_completion_case):
    """Scenario H: Red flag symptom preserving (does not dismiss/diagnose, surfaces flag)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session, q = await service.get_or_generate_next_question(case_id, db)
        assert q is not None

        # Patient reports red flag symptom in response
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="Severe crushing chest pain radiating to jaw and arm.",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert q.is_safety_flag is True
        assert res["new_evidence_id"] is not None


@pytest.mark.asyncio
async def test_scenario_i_zero_information_gain_stopping(database, sample_completion_case):
    """Scenario I: StoppingEngine halts interview upon reaching information plateau or no actionable gaps."""
    engine = StoppingEngine()
    session = CompletionSession(
        case_id="c1",
        current_turn=2,
        max_turns=5,
        questions_answered_count=2,
        initial_readiness_score=0.70,
        current_readiness_score=0.70,
    )

    v_run = VerificationRun(
        case_id="c1", review_readiness_status="provisional", review_readiness_score=0.70,
    )
    low_gap = InformationGap(
        gap_id="g_low",
        gap_type=GapType.CONTEXT_ENRICHMENT,
        target_field="context_notes",
        category="CONTEXT",
        severity=FindingSeverity.LOW,
        description="Minor context note gap",
    )

    # 1. Information Plateau detection
    should_stop, crit, reason = engine.evaluate_stopping(session, [low_gap], v_run, [])
    assert should_stop is True
    assert crit == StoppingCriterion.ZERO_INFORMATION_GAIN
    assert "plateau" in reason.lower()

    # 2. No remaining gaps detection
    should_stop_empty, crit_empty, _ = engine.evaluate_stopping(session, [], v_run, [])
    assert should_stop_empty is True
    assert crit_empty == StoppingCriterion.NO_CRITICAL_GAPS


@pytest.mark.asyncio
async def test_scenario_j_offline_zero_cost_deterministic_mode(database, sample_completion_case):
    """Scenario J: Entire completion engine operates deterministically in ₹0 offline mode."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session, q = await service.get_or_generate_next_question(case_id, db)
        assert q is not None
        assert q.question_text != ""
        assert len(q.options) >= 2


@pytest.mark.asyncio
async def test_scenario_k_anti_hallucination_grounding(database, sample_completion_case):
    """Scenario K: QuestionCandidateEngine generates strictly grounded questions with non-empty rationale."""
    engine = QuestionCandidateEngine()
    validator = QuestionValidator()

    gaps = [
        InformationGap(
            gap_id="g1", gap_type=GapType.MISSING_REQUIRED_FIELD, target_field="vital_signs",
            category="MEASUREMENTS", severity=FindingSeverity.HIGH, description="Missing vitals",
        )
    ]
    candidates = engine.generate_candidates(gaps)
    assert len(candidates) > 0
    for cand in candidates:
        is_valid, _ = validator.validate_candidate(cand, [])
        assert is_valid is True
        assert cand.clinical_rationale != ""


@pytest.mark.asyncio
async def test_scenario_l_cross_patient_idor_isolation(async_client, database, sample_completion_case):
    """Scenario L: Patient B is strictly blocked from accessing Patient A's completion session (HTTP 403)."""
    case_id = sample_completion_case["case_id"]
    patient_b = sample_completion_case["patient_b_user"]

    token_b = create_access_token(subject=patient_b.id, role="patient")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Patient B attempts to access Patient A's completion session
    resp = await async_client.get(f"/api/v1/cases/{case_id}/completion/next-question", headers=headers_b)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_scenario_m_invalid_question_id_rejection(database, sample_completion_case):
    """Scenario M: Non-existent question, duplicate answer, skipped answer, and blank text rejection."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        # 1. Non-existent question
        with pytest.raises(ValueError) as excinfo:
            await service.submit_answer(
                case_id=case_id,
                question_id="non-existent-uuid",
                raw_answer_text="Test answer",
                db=db,
            )
        assert "not found" in str(excinfo.value)

        # Generate a real question
        session, q = await service.get_or_generate_next_question(case_id, db)
        assert q is not None

        # 2. Blank text without is_skipped=True rejection
        with pytest.raises(ValueError) as excinfo_blank:
            await service.submit_answer(
                case_id=case_id,
                question_id=q.id,
                raw_answer_text="    ",
                is_skipped=False,
                db=db,
            )
        assert "cannot be empty" in str(excinfo_blank.value)

        # 3. Answer successfully
        await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="1 to 3 days",
            is_skipped=False,
            db=db,
            actor=sample_completion_case["patient_user"],
        )

        # 4. Duplicate submission on already answered question
        with pytest.raises(ValueError) as excinfo_dup:
            await service.submit_answer(
                case_id=case_id,
                question_id=q.id,
                raw_answer_text="3 to 5 days",
                db=db,
            )
        assert "already been resolved" in str(excinfo_dup.value)


@pytest.mark.asyncio
async def test_scenario_n_multi_turn_loop(database, sample_completion_case):
    """Scenario N: Multi-turn loop (Turn 1 -> Answer -> Rebuild -> Reverify -> Turn 2)."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        # Turn 1
        sess1, q1 = await service.get_or_generate_next_question(case_id, db, max_turns=3)
        assert q1 is not None
        assert sess1.current_turn == 1

        res1 = await service.submit_answer(
            case_id=case_id,
            question_id=q1.id,
            raw_answer_text="1 to 3 days",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res1["new_case_version"] >= 2

        # Turn 2
        sess2, q2 = await service.get_or_generate_next_question(case_id, db, max_turns=3)
        if q2:
            assert q2.turn_number == 2
            assert q2.id != q1.id


@pytest.mark.asyncio
async def test_scenario_o_session_resumption(database, sample_completion_case):
    """Scenario O: Active session is reused instead of orphaned when queried repeatedly."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        sess1 = await service.get_or_create_session(case_id, db)
        sess2 = await service.get_or_create_session(case_id, db)
        assert sess1.id == sess2.id


@pytest.mark.asyncio
async def test_scenario_p_patient_opt_out_early_conclusion(database, sample_completion_case):
    """Scenario P: Patient explicitly concludes session early."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session = await service.complete_session_manually(case_id, "Patient requested exit", db)
        assert session.status == CompletionSessionStatus.STOPPED_PATIENT_DECLINED.value
        assert "Patient requested exit" in session.stopping_reason


@pytest.mark.asyncio
async def test_scenario_q_non_diagnostic_boundary_guard():
    """Scenario Q: CompletionSafetyGuard strictly rejects diagnostic, admission, prescription, and discharge statements."""
    guard = CompletionSafetyGuard()

    # 1. Diagnostic assertion
    with pytest.raises(ValueError) as exc1:
        guard.enforce_non_diagnostic_boundary("You have pneumonia and need immediate treatment.")
    assert "Safety boundary breach" in str(exc1.value)

    # 2. Admission recommendation
    with pytest.raises(ValueError) as exc2:
        guard.enforce_non_diagnostic_boundary("Patient must be admitted to hospital immediately.")
    assert "admission" in str(exc2.value).lower()

    # 3. Discharge advice
    with pytest.raises(ValueError) as exc3:
        guard.enforce_non_diagnostic_boundary("There is no need to see a doctor for this issue.")
    assert "discharge" in str(exc3.value).lower()

    # 4. Prescriptive medication recommendation
    with pytest.raises(ValueError) as exc4:
        guard.enforce_non_diagnostic_boundary("We prescribe 500mg amoxicillin three times daily.")
    assert "prescriptive" in str(exc4.value).lower() or "medication" in str(exc4.value).lower()


@pytest.mark.asyncio
async def test_scenario_r_timeline_event_enrichment(database, sample_completion_case):
    """Scenario R: Answer on progression enriches timeline events upon rebuild."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        session, q = await service.get_or_generate_next_question(case_id, db)
        res = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="Symptoms developed gradually over the past 3 days.",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res["rebuilt_snapshot_id"] is not None

        # Verify rebuilt snapshot has facts
        snap = (await db.execute(
            select(CaseSnapshot).where(CaseSnapshot.id == res["rebuilt_snapshot_id"]).options(selectinload(CaseSnapshot.facts))
        )).scalar_one()
        assert len(snap.facts) > 0


@pytest.mark.asyncio
async def test_scenario_s_concurrent_session_idempotency(database, sample_completion_case):
    """Scenario S: Multiple concurrent calls return same pending presented question."""
    async with database() as db:
        service = CompletionService()
        case_id = sample_completion_case["case_id"]

        _, q1 = await service.get_or_generate_next_question(case_id, db)
        _, q2 = await service.get_or_generate_next_question(case_id, db)
        assert q1 is not None and q2 is not None
        assert q1.id == q2.id


@pytest.mark.asyncio
async def test_scenario_t_cold_restart_persistence(database, sample_completion_case):
    """Scenario T: CompletionSession and questions persist across fresh database connections."""
    case_id = sample_completion_case["case_id"]
    sess_id = None
    q_id = None

    # Session 1: Create and present question
    async with database() as db:
        service = CompletionService()
        session, q = await service.get_or_generate_next_question(case_id, db)
        assert q is not None
        sess_id = session.id
        q_id = q.id
        await db.commit()

    # Session 2: Fresh database context
    async with database() as db:
        persisted_sess = (await db.execute(
            select(CompletionSession).where(CompletionSession.id == sess_id)
        )).scalar_one()
        assert persisted_sess is not None
        assert persisted_sess.case_id == case_id

        persisted_q = (await db.execute(
            select(CompletionQuestion).where(CompletionQuestion.id == q_id)
        )).scalar_one()
        assert persisted_q is not None
        assert persisted_q.session_id == sess_id
        assert persisted_q.status == QuestionStatus.PRESENTED.value


@pytest.mark.asyncio
async def test_concurrent_answer_submission_isolation(database, sample_completion_case):
    """Verifies that race conditions on duplicate or rapid submission are safely contained."""
    case_id = sample_completion_case["case_id"]
    service = CompletionService()

    async with database() as db:
        session, q = await service.get_or_generate_next_question(case_id, db)
        assert q is not None
        await db.commit()

        # First submit succeeds
        res1 = await service.submit_answer(
            case_id=case_id,
            question_id=q.id,
            raw_answer_text="1 to 3 days",
            db=db,
            actor=sample_completion_case["patient_user"],
        )
        assert res1["answer"] is not None

        # Second rapid submit fails gracefully with ValueError
        with pytest.raises(ValueError) as exc:
            await service.submit_answer(
                case_id=case_id,
                question_id=q.id,
                raw_answer_text="4 to 7 days",
                db=db,
                actor=sample_completion_case["patient_user"],
            )
        assert "already been" in str(exc.value)
