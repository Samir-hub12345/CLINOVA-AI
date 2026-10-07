"""Phase 3 — BUILD: Canonical Patient Case Intelligence Build Test Suite for Clinova AI.

Validates all 22 core scenarios:
- Grounded extraction & anti-hallucination span validation
- Negation detection & uncertainty tagging
- Temporal structuring & chronological timeline ordering
- Lab value, vital sign, medication, allergy, and family history isolation
- Multi-source evidence linkage and conflict preservation
- Immutable snapshot versioning, delta summaries, and last-known-good rollback safety
- Clinical specialty signals (Cardiology, Pulmonology, Endocrinology)
- Indic multilingual concept handling (Odia, Hindi)
- Build run telemetry and API endpoints
"""

import json
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
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
from app.services.case_builder import (
    StructuredExtractionEngine,
    ClinicalNormalizationEngine,
    TimelineEngine,
    MultimodalFusionEngine,
    CaseBuilderService,
)


@pytest.fixture
async def sample_case(database):
    """Creates a fresh test patient and triage case in the database."""
    async with database() as db:
        user = User(
            email=f"patient.phase3.{datetime.now().timestamp()}@test.invalid",
            full_name="Phase3 Patient",
            role=UserRole.PATIENT,
            hashed_password=get_password_hash("TestPass123!"),
        )
        db.add(user)
        await db.flush()

        case = TriageCase(
            synthetic_case_id="CLN-P3-TEST-001",
            owner_user_id=user.id,
            language="en",
            facility_type="District Hospital",
            visit_type="Outpatient Intake",
            status="active",
            workflow_state="INTAKE",
            case_version=1,
            review_readiness_status="ready_for_review",
            queue_category="priority",
            consent_status=True,
            approximate_age=45,
            gender="Male",
            raw_symptoms="High fever for 3 days and headache.",
        )
        db.add(case)
        await db.commit()
        await db.refresh(case)
        await db.refresh(user)
        return case, user


# 1. Anti-hallucination / Grounded extraction
@pytest.mark.asyncio
async def test_scenario_21_anti_hallucination_span_validation():
    """Scenario 21: Verify that extracted facts must match explicit spans in the source evidence."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-01",
        case_id="case-01",
        canonical_field="intake_text",
        raw_value="Patient reports severe fever for 2 days. No vomiting.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, rejected = extractor.extract_from_evidence(ev)
    for f in facts:
        assert f.source_span is not None
        assert f.source_span in ev.raw_value


# 2. Negation detection
@pytest.mark.asyncio
async def test_scenario_2_negation_detection():
    """Scenario 2: Explicit negation cues tag polarity='NEGATED' without deleting the concept."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-02",
        case_id="case-01",
        canonical_field="intake_text",
        raw_value="Patient has high fever and cough, but denies chest pain and no shortness of breath.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    fact_map = {f.concept.lower(): f for f in facts}

    assert "chest pain" in fact_map
    assert fact_map["chest pain"].polarity == FactPolarity.NEGATED.value

    assert "shortness of breath" in fact_map
    assert fact_map["shortness of breath"].polarity == FactPolarity.NEGATED.value

    assert "fever" in fact_map
    assert fact_map["fever"].polarity == FactPolarity.AFFIRMED.value


# 3. Uncertainty handling
@pytest.mark.asyncio
async def test_scenario_3_uncertainty_handling():
    """Scenario 3: Terms like 'possible' or 'suspected' trigger certainty='UNCERTAIN'."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-03",
        case_id="case-01",
        canonical_field="clinical_impression",
        raw_value="Possible fever with suspected migraine headache.",
        source_type=EvidenceSourceType.CLINICIAN_ENTERED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    fact_map = {f.concept.lower(): f for f in facts}

    assert "fever" in fact_map
    assert fact_map["fever"].certainty == FactCertainty.UNCERTAIN.value
    assert "headache" in fact_map
    assert fact_map["headache"].certainty == FactCertainty.UNCERTAIN.value


# 4. Temporal progression & Timeline engine
@pytest.mark.asyncio
async def test_scenario_4_temporal_progression():
    """Scenario 4: Day 1, Day 2, Day 3 markers are correctly sequenced in chronological order."""
    timeline_engine = TimelineEngine()
    ev = CaseEvidence(
        id="ev-04",
        case_id="case-01",
        canonical_field="narrative",
        raw_value="Day 1: Chills and mild headache.\nDay 2: Persistent fever 102 F.\nDay 3 (Today): Shortness of breath upon walking.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    events = timeline_engine.extract_timeline_events([ev])

    assert len(events) == 3
    assert events[0].order_index == 1
    assert "Day 1" in events[0].relative_time
    assert events[1].order_index == 2
    assert "Day 2" in events[1].relative_time
    assert events[2].order_index == 3
    assert "Day 3" in events[2].relative_time


# 5. Lab slip extraction
@pytest.mark.asyncio
async def test_scenario_5_lab_slip_extraction():
    """Scenario 5: Lab values (HbA1c, platelets, hemoglobin) are extracted with units and categorized as lab_value."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-05",
        case_id="case-01",
        canonical_field="lab_report",
        raw_value="Complete Blood Count: Hb: 11.5 g/dL, Platelets: 150000 /mcL, HbA1c: 8.4 %.",
        source_type=EvidenceSourceType.DOCUMENT_DERIVED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    lab_facts = {f.concept: f for f in facts if f.category == "lab_value"}

    assert "Hemoglobin" in lab_facts
    assert "11.5" in lab_facts["Hemoglobin"].value
    assert lab_facts["Hemoglobin"].unit == "g/dL"

    assert "Platelet Count" in lab_facts
    assert "150000" in lab_facts["Platelet Count"].value

    assert "HbA1c" in lab_facts
    assert "8.4" in lab_facts["HbA1c"].value


# 6. Vital signs normalization
@pytest.mark.asyncio
async def test_scenario_6_vital_signs_normalization():
    """Scenario 6: Vital signs are extracted and normalized with standard units."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()
    ev = CaseEvidence(
        id="ev-06",
        case_id="case-01",
        canonical_field="triage_vitals",
        raw_value="Vitals taken: BP: 132/84 mmHg, HR: 76 bpm, Temp: 101.4 F, SpO2: 97 %.",
        source_type=EvidenceSourceType.STAFF_ENTERED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    normalized = normalizer.normalize_all(facts)
    vitals_map = {f.concept: f for f in normalized if f.category == "vital"}

    assert "Blood Pressure" in vitals_map
    assert vitals_map["Blood Pressure"].normalized_value == "132/84 mmHg"

    assert "Heart Rate" in vitals_map
    assert vitals_map["Heart Rate"].normalized_value == "76 bpm"

    assert "Body Temperature" in vitals_map
    assert "°F" in vitals_map["Body Temperature"].normalized_value
    assert "°C" in vitals_map["Body Temperature"].normalized_value


# 7. Medication reconciliation
@pytest.mark.asyncio
async def test_scenario_7_medication_reconciliation():
    """Scenario 7: Documented current medications are extracted and categorized as medication."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-07",
        case_id="case-01",
        canonical_field="medication_list",
        raw_value="Current prescriptions: Metformin 500mg, Lisinopril 10mg, Atorvastatin 20mg.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    med_concepts = {f.concept for f in facts if f.category == "medication"}

    assert "Metformin" in med_concepts
    assert "Lisinopril" in med_concepts
    assert "Atorvastatin" in med_concepts


# 8. Allergy isolation
@pytest.mark.asyncio
async def test_scenario_8_allergy_isolation():
    """Scenario 8: Allergies are categorized strictly as allergy, not symptoms or conditions."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-08",
        case_id="case-01",
        canonical_field="allergies",
        raw_value="Allergies: Penicillin allergy, Sulfa drugs.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    allergy_facts = [f for f in facts if f.category == "allergy"]

    assert len(allergy_facts) >= 2
    concepts = {f.concept for f in allergy_facts}
    assert "Penicillin" in concepts
    assert "Sulfa drugs" in concepts


# 9. Family history isolation (Strict Anti-Conflation Rule)
@pytest.mark.asyncio
async def test_scenario_9_family_history_isolation():
    """Scenario 9: Family history ('father has diabetes') is strictly categorized as family_history, NOT patient condition."""
    extractor = StructuredExtractionEngine()
    ev = CaseEvidence(
        id="ev-09",
        case_id="case-01",
        canonical_field="intake_notes",
        raw_value="Patient reports no chronic illnesses. Father had diabetes and hypertension.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, _ = extractor.extract_from_evidence(ev)

    family_facts = [f for f in facts if f.category == "family_history"]
    condition_facts = [f for f in facts if f.category == "documented_condition"]

    assert len(family_facts) >= 1
    assert any("Father" in f.concept for f in family_facts)
    # Patient condition must NOT falsely contain Type 2 Diabetes
    assert not any(f.concept == "Type 2 Diabetes Mellitus" and f.polarity == "AFFIRMED" for f in condition_facts)


# 10. Multi-source evidence linkage
@pytest.mark.asyncio
async def test_scenario_10_multimodal_source_linkage():
    """Scenario 10: The same concept across multiple evidence items links all evidence IDs."""
    fusion = MultimodalFusionEngine()
    f1 = StructuredExtractionEngine().extract_from_evidence(
        CaseEvidence(id="ev-voice-1", case_id="c1", raw_value="High fever for 3 days", source_type=EvidenceSourceType.PATIENT_VOICE)
    )[0][0]
    f2 = StructuredExtractionEngine().extract_from_evidence(
        CaseEvidence(id="ev-note-2", case_id="c1", raw_value="Patient examined with persistent fever", source_type=EvidenceSourceType.CLINICIAN_ENTERED)
    )[0][0]

    fused, conflicts = fusion.fuse_and_link_facts([f1, f2])
    assert len(fused) == 1
    assert len(conflicts) == 0
    assert "ev-voice-1" in fused[0].supporting_evidence_ids
    assert "ev-note-2" in fused[0].supporting_evidence_ids


# 11. Contradictory vitals preservation (Conflict rule)
@pytest.mark.asyncio
async def test_scenario_11_contradictory_vitals_preservation():
    """Scenario 11: Conflicting vitals across sources preserve both records and set has_conflict=True."""
    fusion = MultimodalFusionEngine()
    normalizer = ClinicalNormalizationEngine()
    extractor = StructuredExtractionEngine()

    ev1 = CaseEvidence(id="ev-patient", case_id="c1", raw_value="Patient reports BP: 120/80 mmHg at home", source_type=EvidenceSourceType.PATIENT_REPORTED)
    ev2 = CaseEvidence(id="ev-monitor", case_id="c1", raw_value="Clinic triage monitor recorded BP: 165/100 mmHg", source_type=EvidenceSourceType.STAFF_VERIFIED)

    f1 = normalizer.normalize_all(extractor.extract_from_evidence(ev1)[0])
    f2 = normalizer.normalize_all(extractor.extract_from_evidence(ev2)[0])

    fused, conflicts = fusion.fuse_and_link_facts(f1 + f2)

    assert len(conflicts) >= 1
    # Both conflicting records must be retained
    assert len(fused) == 2
    assert all(f.has_conflict is True for f in fused)
    assert any("120/80" in f.value for f in fused)
    assert any("165/100" in f.value for f in fused)


# 12. Immutable version increment & Case Builder Service
@pytest.mark.asyncio
async def test_scenario_12_immutable_version_increment(database, sample_case):
    """Scenario 12: Building twice increments case_version from 1 to 2, keeping snapshot v1 immutable."""
    case, user = sample_case
    builder = CaseBuilderService()

    async with database() as db:
        # Add initial evidence
        ev = CaseEvidence(
            case_id=case.id,
            canonical_field="reported_symptoms",
            raw_value="Fever and cough for 2 days",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        db.add(ev)
        await db.commit()

        # Build 1
        snap1, run1 = await builder.build_canonical_case(case.id, db)
        assert snap1.case_version == 1
        assert snap1.is_current is True
        assert run1.status == BuildRunStatus.COMPLETED.value

        # Add more evidence
        ev2 = CaseEvidence(
            case_id=case.id,
            canonical_field="vital_signs",
            raw_value="BP: 130/85 mmHg",
            source_type=EvidenceSourceType.STAFF_ENTERED,
        )
        db.add(ev2)
        await db.commit()

        # Build 2
        snap2, run2 = await builder.build_canonical_case(case.id, db)
        assert snap2.case_version == 2
        assert snap2.is_current is True

        # Verify snapshot 1 is no longer current but still exists in DB
        snap1_reloaded = (await db.execute(select(CaseSnapshot).where(CaseSnapshot.id == snap1.id))).scalar_one()
        assert snap1_reloaded.is_current is False
        assert snap1_reloaded.case_version == 1


# 13. Delta summary calculation
@pytest.mark.asyncio
async def test_scenario_13_delta_summary_calculation(database, sample_case):
    """Scenario 13: Second snapshot records delta summary highlighting added concepts."""
    case, _ = sample_case
    builder = CaseBuilderService()

    async with database() as db:
        ev1 = CaseEvidence(
            case_id=case.id,
            canonical_field="symptoms",
            raw_value="Patient reports fever for 3 days",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        db.add(ev1)
        await db.commit()
        await builder.build_canonical_case(case.id, db)

        # Add new symptom in second run
        ev2 = CaseEvidence(
            case_id=case.id,
            canonical_field="symptoms_update",
            raw_value="Patient now reports severe headache",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        db.add(ev2)
        await db.commit()

        snap2, _ = await builder.build_canonical_case(case.id, db)
        assert snap2.delta_summary is not None
        assert "Headache" in snap2.delta_summary.get("added_concepts", [])


# 14. Last-known-good rollback recovery
@pytest.mark.asyncio
async def test_scenario_14_last_known_good_recovery(database, sample_case):
    """Scenario 14: If build fails halfway, previous valid snapshot remains is_current=True."""
    case, _ = sample_case
    builder = CaseBuilderService()

    async with database() as db:
        ev = CaseEvidence(
            case_id=case.id,
            canonical_field="symptoms",
            raw_value="Persistent fever",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        db.add(ev)
        await db.commit()

        # Valid build 1
        snap1, _ = await builder.build_canonical_case(case.id, db)
        assert snap1.is_current is True

        # Intentionally induce failure by providing invalid case_id
        with pytest.raises(ValueError):
            await builder.build_canonical_case("non-existent-case-id", db)

        # Verify original snapshot for valid case is completely unaffected
        snap1_check = (await db.execute(select(CaseSnapshot).where(CaseSnapshot.id == snap1.id))).scalar_one()
        assert snap1_check.is_current is True


# 15. Specialty signals - Cardiology
@pytest.mark.asyncio
async def test_scenario_15_specialty_signals_cardiology():
    """Scenario 15: Chest pain, dyspnea, and hypertension trigger Cardiology routing signal."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()
    fusion = MultimodalFusionEngine()

    ev = CaseEvidence(
        id="ev-cardio",
        case_id="c1",
        raw_value="Crushing chest pain radiating to arm, shortness of breath, profuse sweating, history of hypertension.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts = normalizer.normalize_all(extractor.extract_from_evidence(ev)[0])
    signals = fusion.compute_specialty_signals(facts)

    assert any(s.specialty == "Cardiology" and s.relevance_score > 0.5 for s in signals)


# 16. Specialty signals - Pulmonology
@pytest.mark.asyncio
async def test_scenario_16_specialty_signals_pulmonology():
    """Scenario 16: Dyspnea, cough, and asthma trigger Pulmonology routing signal."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()
    fusion = MultimodalFusionEngine()

    ev = CaseEvidence(
        id="ev-pulm",
        case_id="c1",
        raw_value="Acute shortness of breath, persistent cough, history of asthma.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts = normalizer.normalize_all(extractor.extract_from_evidence(ev)[0])
    signals = fusion.compute_specialty_signals(facts)

    assert any(s.specialty == "Pulmonology" and s.relevance_score > 0.5 for s in signals)


# 17. Specialty signals - Endocrinology
@pytest.mark.asyncio
async def test_scenario_17_specialty_signals_endocrine():
    """Scenario 17: Diabetes, high blood sugar, and Metformin trigger Endocrinology routing signal."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()
    fusion = MultimodalFusionEngine()

    ev = CaseEvidence(
        id="ev-endo",
        case_id="c1",
        raw_value="Type 2 diabetes, FBS: 185 mg/dL, currently taking Metformin.",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts = normalizer.normalize_all(extractor.extract_from_evidence(ev)[0])
    signals = fusion.compute_specialty_signals(facts)

    assert any(s.specialty == "Endocrinology" and s.relevance_score > 0.5 for s in signals)


# 18. Indic multilingual - Odia concept extraction
@pytest.mark.asyncio
async def test_scenario_18_indic_odia_concept_extraction():
    """Scenario 18: Odia script symptom text is accurately mapped to canonical clinical concepts."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()

    ev = CaseEvidence(
        id="ev-odia",
        case_id="c1",
        raw_value="ମୋତେ ୩ ଦିନ ହେଲା ପ୍ରବଳ ଜ୍ୱର ଅଛି, ମୁଣ୍ଡ ବିନ୍ଧା ହେଉଛି ଏବଂ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି।",
        source_type=EvidenceSourceType.PATIENT_VOICE,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    normalized = normalizer.normalize_all(facts)
    concepts = {f.concept for f in normalized}

    assert "Pyrexia" in concepts
    assert "Headache" in concepts
    assert "Dyspnea" in concepts


# 19. Indic multilingual - Hindi concept extraction
@pytest.mark.asyncio
async def test_scenario_19_indic_hindi_concept_extraction():
    """Scenario 19: Hindi script symptom text is accurately mapped to canonical clinical concepts."""
    extractor = StructuredExtractionEngine()
    normalizer = ClinicalNormalizationEngine()

    ev = CaseEvidence(
        id="ev-hindi",
        case_id="c1",
        raw_value="मरीज को दो दिन से तेज बुखार है, खांसी है और सांस लेने में तकलीफ हो रही है।",
        source_type=EvidenceSourceType.PATIENT_REPORTED,
    )
    facts, _ = extractor.extract_from_evidence(ev)
    normalized = normalizer.normalize_all(facts)
    concepts = {f.concept for f in normalized}

    assert "Pyrexia" in concepts
    assert "Cough" in concepts
    assert "Dyspnea" in concepts


# 20. Build run telemetry
@pytest.mark.asyncio
async def test_scenario_20_build_run_telemetry(database, sample_case):
    """Scenario 20: CaseBuildRun captures run status, latency, input count, extracted count, and logic version."""
    case, _ = sample_case
    builder = CaseBuilderService()

    async with database() as db:
        ev = CaseEvidence(
            case_id=case.id,
            canonical_field="symptoms",
            raw_value="Fever and chills for 2 days",
            source_type=EvidenceSourceType.PATIENT_REPORTED,
        )
        db.add(ev)
        await db.commit()

        _, run = await builder.build_canonical_case(case.id, db)

        assert run.status == BuildRunStatus.COMPLETED.value
        assert run.input_evidence_count == 1
        assert run.facts_extracted_count >= 1
        assert run.build_logic_version == "3.0.0"
        assert run.latency_ms >= 0
        assert run.completed_at is not None


# 1 & 22. End-to-end API: Patient text/voice build and snapshot retrieval
@pytest.mark.asyncio
async def test_scenario_1_and_22_api_build_and_snapshot_retrieval(async_client: AsyncClient, database, sample_case):
    """Scenario 1 & 22: HTTP POST /build, GET /snapshots, GET /snapshots/1, and GET /builds via API."""
    case, user = sample_case
    token = create_access_token(subject=user.id, role="patient")
    headers = {"Authorization": f"Bearer {token}"}

    # Add text symptom via API
    text_res = await async_client.post(
        f"/api/v1/cases/{case.id}/text",
        headers=headers,
        json={"text": "Severe fever for 3 days and headache.", "field_name": "reported_symptoms"},
    )
    assert text_res.status_code == 201

    # 1. POST /build
    build_res = await async_client.post(
        f"/api/v1/cases/{case.id}/build",
        headers=headers,
        json={"trigger_type": "manual_rebuild"},
    )
    assert build_res.status_code == 200
    snap_data = build_res.json()
    assert snap_data["case_version"] == 1
    assert snap_data["is_current"] is True
    assert len(snap_data["facts"]) >= 1

    # 2. GET /snapshots
    snaps_res = await async_client.get(f"/api/v1/cases/{case.id}/snapshots", headers=headers)
    assert snaps_res.status_code == 200
    snaps_list = snaps_res.json()
    assert len(snaps_list) == 1

    # 3. GET /snapshots/{version}
    snap_v1_res = await async_client.get(f"/api/v1/cases/{case.id}/snapshots/1", headers=headers)
    assert snap_v1_res.status_code == 200
    assert snap_v1_res.json()["case_version"] == 1

    # 4. GET /builds
    builds_res = await async_client.get(f"/api/v1/cases/{case.id}/builds", headers=headers)
    assert builds_res.status_code == 200
    builds_list = builds_res.json()
    assert len(builds_list) == 1
    assert builds_list[0]["status"] == "completed"

    # 5. GET /canonical (verify current snapshot included)
    canon_res = await async_client.get(f"/api/v1/cases/{case.id}/canonical", headers=headers)
    assert canon_res.status_code == 200
    canon_data = canon_res.json()
    assert canon_data["current_snapshot"] is not None
    assert canon_data["current_snapshot"]["case_version"] == 1
