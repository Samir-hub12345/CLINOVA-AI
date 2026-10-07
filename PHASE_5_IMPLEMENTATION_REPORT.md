# Phase 5 — Intelligent Information Completion & Adaptive Interviewing Architecture Report

## 1. Executive Summary

Phase 5 introduces **Intelligent Information Completion and Adaptive Interviewing** to the CLINOVA AI clinical intake and verification pipeline. Building directly upon Phase 3 (Canonical Case Builder) and Phase 4 (Clinical Verification & Review Readiness Engine), Phase 5 autonomously identifies missing, conflicting, hedging, or incomplete clinical facts in a verified case, formulates bounded non-diagnostic follow-up questions, interacts with patients through an empathetic multi-turn dialogue, converts responses into discrete first-class `CaseEvidence` records, and orchestrates live case rebuilding and re-verification.

Strict adherence to clinical safety boundaries is maintained throughout: Phase 5 operates as an intake completion assistant, never proposing diagnoses, prescribing medications, triaging emergently, or superseding clinician professional authority.

---

## 2. Architecture & Sub-Phase Breakdown (5.1 - 5.16)

```
                                  [ Phase 4 Verified Case ]
                                             │
                                             ▼
                                  [ Sub-Phase 5.3: Gap Engine ]
                         (Completeness findings, Conflicts, Uncertainties)
                                             │
                                             ▼
                                [ Sub-Phase 5.4: Candidate Engine ]
                             (Deterministic, Patient-Friendly Questions)
                                             │
                                             ▼
                                [ Sub-Phase 5.5: Question Validator ]
                         (Strict Non-Diagnostic Boundary Enforcement)
                                             │
                                             ▼
                             [ Sub-Phase 5.6: Prioritization Engine ]
                         (Score = 0.50*Utility + 0.40*Severity - 0.10*Burden)
                                             │
                                             ▼
                              [ Sub-Phase 5.7: Selector Engine ]
                           (Next Best Question / Turn Budgeting)
                                             │
                                             ▼
                             [ Sub-Phase 5.8: Delivery Service ]
                                (Presents Question to Patient)
                                             │
                                             ▼
                                     [ Patient Input ]
                                  (Answer Text / Skip)
                                             │
                                             ▼
                              [ Sub-Phase 5.9: Answer Capture ]
                                  (Creates CaseEvidence)
                                             │
                                             ▼
                              [ Sub-Phase 5.10: Case Rebuilder ]
                              (Phase 3 Live Rebuild -> Snapshot)
                                             │
                                             ▼
                             [ Sub-Phase 5.11: Case Reverifier ]
                             (Phase 4 Reverification & Readiness)
                                             │
                                             ▼
                              [ Sub-Phase 5.12: Stopping Engine ]
                           (Max turns, All gaps resolved, Plateau)
                                             │
                                             ▼
                             [ Sub-Phase 5.13: Completion Summary ]
```

### Sub-Phase 5.1: Data Foundation & Persistence
- **Models** (`backend/app/models/completion.py`):
  - `CompletionSession`: Master session tracking turns, counts, gap statistics, review readiness progression, and stopping rationale.
  - `CompletionQuestion`: Discrete question record capturing turn number, target gap, priority score, clinical rationale, status, and red flag indicators.
  - `CompletionAnswer`: Normalized patient answer linked directly to generated `CaseEvidence`.
  - Enums: `CompletionSessionStatus`, `QuestionType`, `QuestionStatus`, `AnswerModality`, `GapType`, `StoppingCriterion`.
- **Database Migration**: `0009_phase5_intelligent_completion_architecture.py` (Alembic version).
- **Composite Indexes**: Composite indexes on `(case_id, status)`, `(case_id, is_current)`, `(session_id, turn_number)`, `(case_id, target_field)`, and `(case_id, question_id)` ensure high-throughput queries without locks.

### Sub-Phase 5.2: Domain Models & Schemas
- Defined lightweight, immutable dataclasses (`InformationGap`, `QuestionCandidate`, `PrioritizedQuestion`) in `backend/app/services/completion/domain.py`.
- Pydantic v2 schemas in `backend/app/schemas/completion.py` for client request/response serializations.

### Sub-Phase 5.3: Information Gap Detection Engine
- Implemented in `backend/app/services/completion/gap_engine.py`.
- Extracts gaps across 4 dimensions:
  1. *Completeness Findings*: Missing required clinical concepts (`symptom_duration`, `vital_signs`, `allergies`).
  2. *Unresolved Cross-Modal Conflicts*: Contradictory statements preserved by Phase 4.
  3. *Uncertain Facts*: Hedging observations or low certainty scores.
  4. *Incomplete Timelines*: Sparse chronological sequences (<2 milestone events).
- Filters out non-patient-addressable parameters (e.g., histology, lab numbers) and already queried/exhausted fields.

### Sub-Phase 5.4: Candidate Question Generation Engine
- Implemented in `backend/app/services/completion/candidate_engine.py`.
- Generates structured, deterministic questions with clear multiple-choice options and plain-language phrasing.
- Special handling for conflict resolution ("Our records show different details: 'A' vs 'B'. Which is more accurate?") and uncertainty verification.

### Sub-Phase 5.5: Question Safety Validator
- Implemented in `backend/app/services/completion/question_validator.py`.
- Enforces strict regex boundaries against:
  - Prohibited diagnostic claims (*"You might have..."*, *"This sounds like pneumonia"*).
  - Prescriptions or treatment instructions (*"Take 500mg..."*, *"You should start taking..."*).
  - Medical advice or dismissals (*"Don't worry, this is harmless"*).
  - Repetitive queries on previously answered or exhausted topics.

### Sub-Phase 5.6: Multi-Attribute Prioritization Engine
- Implemented in `backend/app/services/completion/prioritization_engine.py`.
- Composite deterministic scoring formula:
  $$\text{Score} = 0.50 \times \text{Utility} + 0.40 \times \text{SeverityWeight} - 0.10 \times \text{BurdenPenalty}$$
- Applies dynamic fatigue penalty based on turns taken and consecutive skipped questions.

### Sub-Phase 5.7: Next-Best-Question Selector
- Implemented in `backend/app/services/completion/selector_engine.py`.
- Manages turn budgeting (default 5 turns) and abstention thresholds (rejects questions with utility < 0.20 or score < 0.25).

### Sub-Phase 5.8: Patient Question Delivery Service
- Implemented in `backend/app/services/completion/delivery_service.py`.
- Advances `current_turn`, sets question state to `PRESENTED`, updates timestamps, and maintains in-memory session relationship integrity.

### Sub-Phase 5.9: Answer Capture & Provenance Linkage
- Implemented in `backend/app/services/completion/answer_service.py`.
- Normalizes patient responses and creates a discrete `CaseEvidence` record with:
  - `verification_state = VerificationState.PATIENT_REPORTED`
  - `source_type = EvidenceSourceType.PATIENT_TEXT` (or choice/voice)
  - `processor_name = "Phase5_Intelligent_Completion"`
  - `source_reference = "Phase 5 Completion Turn {turn}"`
- Directly references `evidence_id` on the `CompletionAnswer`.

### Sub-Phase 5.10: Live Canonical Case Rebuilder
- Implemented in `backend/app/services/completion/rebuilder.py`.
- Invokes `CaseBuilderService.build_canonical_case(force_rebuild=True)`, producing an updated `CaseSnapshot` and updating `case_version_current`.

### Sub-Phase 5.11: Live Clinical Reverifier
- Implemented in `backend/app/services/completion/reverifier.py`.
- Invokes `CaseVerificationService.verify_case(force_reverify=True)`.
- Updates `latest_verification_run_id` and recalculates `current_readiness_score`.

### Sub-Phase 5.12: Stopping & Plateau Engine
- Implemented in `backend/app/services/completion/stopping_engine.py`.
- Evaluates 6 stopping conditions:
  1. Explicit manual clinician/patient opt-out.
  2. Maximum turn limit reached (`current_turn >= max_turns`).
  3. Patient fatigue / consecutive skips (`consecutive_skips >= 2`).
  4. All identified gaps resolved (`remaining_gaps == []`).
  5. Target review readiness achieved without remaining critical gaps.
  6. Information plateau (no readiness score improvement over consecutive turns).

### Sub-Phase 5.13: Completion Summary Generator
- Formulates a structured summary upon conclusion:
  - `initial_readiness`, `final_readiness`, `readiness_delta`
  - `turns_taken`, `questions_answered`, `questions_skipped`
  - `initial_gaps`, `remaining_gaps`, `gaps_resolved`

### Sub-Phase 5.14: API Endpoints & Frontend UI
- **REST Endpoints** (`backend/app/api/v1/endpoints/cases.py`):
  - `POST /api/v1/cases/{case_id}/completion/start`
  - `GET /api/v1/cases/{case_id}/completion/session`
  - `GET /api/v1/cases/{case_id}/completion/next-question`
  - `POST /api/v1/cases/{case_id}/completion/questions/{question_id}/answer`
  - `POST /api/v1/cases/{case_id}/completion/questions/{question_id}/skip`
  - `POST /api/v1/cases/{case_id}/completion/complete`
- **Role-Based Security**: Patients can access only their own cases; doctors/admins can access assigned cases. Cross-patient requests strictly return HTTP 403 Forbidden.
- **Frontend Components**:
  - `frontend/src/components/clinical/completion-panel.tsx`: Interactive multi-turn questionnaire interface displaying question cards, option pills, progress bars, skip buttons, and readiness gain metrics.
  - Integration: Embedded inside `frontend/src/app/review/case/[caseId]/page.tsx`.

---

## 3. Strict Non-Diagnostic & Safety Guarantees

1. **Non-Diagnostic Lexical Guard**: Every candidate question is validated against strict patterns prohibiting disease claims, medication dosing, or definitive reassurance.
2. **Red Flag Symptom Preservation**: If a patient reports acute red flag keywords (e.g., *"crushing chest pain"*, *"shortness of breath"*, *"sudden weakness"*), the engine flags the turn (`is_safety_flag = True`), preserves the statement verbatim in `CaseEvidence`, and alerts the clinician package without autonomously diagnosing or triaging.
3. **Deterministic Offline ₹0 Operation**: The core completion loop operates 100% locally via deterministic templates and rules without dependency on external paid LLM calls.

---

## 4. Verification & Compatibility Summary

- **Phase 5 Dedicated Test Suite**: 23/23 tests passing (Scenarios A through T + Unit tests).
- **Full Backend Regression Suite**: 174/174 tests passing across all 5 phases with 0 regressions.
- **Database Backward Compatibility**: Zero breaking changes to existing Phase 1-4 tables.
