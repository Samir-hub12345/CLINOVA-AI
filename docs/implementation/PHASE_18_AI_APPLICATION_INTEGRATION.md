# CLINOVA AI — Phase 18: Clinical AI Application Integration

## 1. Executive Summary & Architecture Overview

Phase 18 integrates CLINOVA AI's local open-source AI runtime foundation (established in Phase 10) into the authoritative Master Case workflow of the application.

The core objective is:
```
MASTER CASE
  → AUTHORITATIVE EVIDENCE
  → DETERMINISTIC SAFETY CONTEXT
  → AI TASK ORCHESTRATION
  → LOCAL LLM (Qwen / MockDeterministicAdapter)
  → STRUCTURED VALIDATION
  → PROVENANCE
  → UNCERTAINTY
  → HUMAN REVIEW (Doctor Workbench)
  → HUMAN CLINICAL DECISION
```

The AI is **ADVISORY ONLY**. It is never the final decision-maker.

```
                    ┌───────────────────────────┐
                    │     Master Case Data      │
                    │ (Authoritative Ledgers)   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Deterministic Safety    │
                    │   NEWS2, Shock Index,     │
                    │   Red Flags, Missing Vit. │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    AI Context Builder     │
                    │  (Sanitization, Passive   │
                    │   Delimiters, SHA-256)    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    Local Qwen Runtime /   │
                    │  MockDeterministicAdapter │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Input/Output Safety &   │
                    │    Grounding Validator    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    AI ADVISORY RESULT     │
                    │ (Tagged AI_INFERRED,      │
                    │  Persisted in ai_results) │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  Qualified Human Review   │
                    │     & Clinical Decision   │
                    │  (Doctor Workbench Gate)  │
                    └───────────────────────────┘
```

---

## 2. Advisory-Only Mandate & Regulatory Guardrails

Under Section 22 of the Master Specification and National Medical Commission (NMC) Regulations 2023:
1. **Never Autonomous Decision-Maker**: The AI subsystem cannot diagnose, prescribe medication, order procedures, admit patients, discharge patients, or transition case states directly.
2. **Deterministic Safety Precedence**: All physiological risk scores (NEWS2, Shock Index, Red Flags, Missing Critical Vitals) are computed strictly outside the LLM using deterministic Python algorithms. They are authoritative and attached to every advisory payload.
3. **Epistemic State Invariant**: AI outputs are tagged strictly as `AI_INFERRED` and `is_advisory_only = True`. They are never stored as `VERIFIED` or `CLINICIAN_VERIFIED` unless explicitly verified by a human clinician.
4. **Mandatory Disclaimer**: Every AI-generated payload and API response carries the medicolegal disclaimer:
   > *"CLINOVA AI ADVISORY RESULT. Non-diagnostic and non-binding. Must be verified and signed off by a qualified registered clinician."*

---

## 3. Registered AI Task Catalog

Phase 18 registers five specialized, structured clinical advisory tasks (`backend/app/ai/tasks.py`):

| Task Identifier | Task Version | Prompt Version | Input Contract | Output Contract | Permitted Roles |
|---|---|---|---|---|---|
| `CASE_SUMMARY_V1` | `1.0.0` | `1.0.0` | `CaseSummaryPayload` | `CaseSummaryResult` | CLINICIAN, DOCTOR, NURSE |
| `TIMELINE_SUMMARY_V1` | `1.0.0` | `1.0.0` | `TimelineSummaryPayload` | `TimelineSummaryResult` | CLINICIAN, DOCTOR, NURSE |
| `MISSING_INFORMATION_V1` | `1.0.0` | `1.0.0` | `MissingInformationPayload` | `MissingInformationResult` | CLINICIAN, DOCTOR, NURSE |
| `FOLLOWUP_QUESTION_V1` | `1.0.0` | `1.0.0` | `CandidateQuestion` | `FollowUpQuestionsPayload` | CLINICIAN, DOCTOR, NURSE |
| `TRIAGE_NOTE_DRAFT_V1` | `1.0.0` | `1.0.0` | `DraftNotePayload` | `DraftTriageNotePayload` | CLINICIAN, DOCTOR, NURSE |

---

## 4. Context-Building Rules & Prompt Injection Defense

`AIContextBuilder` (`backend/app/ai/context_builder.py`) controls all information exposed to the model:

1. **Strict Instruction Hierarchy**:
   - Level 1: System Safety Policy (highest priority, cannot be overridden)
   - Level 2: Application Task Contract
   - Level 3: Deterministic Clinical Context (NEWS2, Shock Index, Red Flags)
   - Level 4: Untrusted Clinical Evidence Blocks (lowest priority)
2. **Data-Only Wrapping**: Untrusted clinical notes, patient complaints, and staff inputs are wrapped inside `<untrusted_clinical_data source="...">` tags, preventing prompt injection instructions from escaping into system instructions.
3. **Zero Secret Leakage**: No JWT tokens, passwords, database URLs, API keys, or unrelated patient records are ever injected into prompts.
4. **Context Fingerprinting**: A deterministic SHA-256 hash is computed over sorted evidence IDs, vital readings, presenting complaint, and case state version (`context_fingerprint`).

---

## 5. Model Configuration & Zero-Dollar ($0) Operation

1. **Config-Driven Runtime Factory** (`backend/app/ai/runtime_factory.py`):
   - `MOCK_DETERMINISTIC` (default): Hermetic, deterministic testing without external dependencies.
   - `LOCAL_OLLAMA`: Real local Qwen model (`qwen3-4b-instruct` or configured local model) via local Ollama endpoint (`http://127.0.0.1:11434`).
   - `DISABLED`: Fails closed safely into `REJECTED_UNAVAILABLE` fallback mode.
2. **Zero Commercial API Dependency**: ₹0 prototype operation is guaranteed. No OpenAI, Gemini, Claude, or paid inference APIs are used or required.

---

## 6. Output Validation, Grounding & Anti-Hallucination

`OutputValidator` (`backend/app/ai_runtime/validation/output_validator.py`):
1. **Two-Pass Validation**:
   - Pass 1: Strict Pydantic JSON schema compliance.
   - Pass 2: Safety & policy checks (forbidden clinical actions, hallucination checks, evidence grounding).
2. **Action Prohibition**: Rejects text or actions attempting `PRESCRIBE`, `ADMIT`, `DISCHARGE`, `AUTHORIZE_PROCEDURE`, or `DIAGNOSE`.
3. **Evidence Grounding**: Model citations (`cited_evidence_ids`) are checked against the case's authoritative evidence IDs in the database. Ungrounded claims trigger `REJECTED_UNGROUNDED`.
4. **Adversarial Safety**: Blocks all 10 mandatory adversarial attacks (`[SYSTEM OVERRIDE]`, `Act as treating doctor`, `Invent missing vitals`, `Close case automatically`, etc.).

---

## 7. AI Uncertainty vs. Clinical Uncertainty

- **Model Confidence**: LLM runtime confidence (0.0 to 1.0).
- **Clinical Epistemic Uncertainty ($U_t$)**: Calculated deterministically by clinical rules from missing vitals, syndrome ambiguity, and contradictory evidence.
- High clinical uncertainty does NOT automatically trigger an emergency. It prompts for targeted follow-up questions or clinician review. Escalation occurs only via deterministic red flags or explicit clinician action.

---

## 8. Safe Degradation & Resilience (Section 37 Invariant)

When the local AI runtime is offline, unreachable, or disabled:
1. Intake, vitals recording, and deterministic triage continue without interruption.
2. Doctor Workbench continues to operate normally with `system_deterministic_support`.
3. AI advisory surfaces display `AI SUPPORT UNAVAILABLE` with status `FALLBACK` / `REJECTED_UNAVAILABLE`.
4. No fabricated results are ever displayed.

---

## 9. AI Result Persistence & Versioning

- Canonical table: `ai_results` (`AIResultRecord` in `backend/app/db/models.py`).
- ForeignKey: `case_id` references `cases.id`.
- Immutable audit log: Historical AI executions are preserved and never overwritten.
- Staleness detection: If case evidence or vitals are updated after an AI result was generated, `is_stale` is evaluated using `context_fingerprint`.

---

## 10. Frontend Integration

1. **AIAdvisoryPanel** (`frontend/src/components/staff/AIAdvisoryPanel.tsx`):
   - Renders 5 distinct task tabs (Summary, Timeline, Missing Info, Follow-up Questions, Draft Note).
   - Shows loading, success, stale, fallback, and unavailable states cleanly.
   - Distinct visual sections for:
     - DETERMINISTIC SAFETY SUPPORT (NEWS2, Shock Index, Red Flags)
     - AI ADVISORY SUPPORT (clearly marked advisory with medicolegal disclaimer)
     - HUMAN CLINICAL DECISION (Doctor sole decision-maker)
2. **DoctorWorkbenchView** (`frontend/src/components/staff/DoctorWorkbenchView.tsx`):
   - Embedded advisory panel alongside care trajectory and human decision cards.

---

## 11. Strict Phase Boundaries & Explicit Exclusions

As mandated by Section 4 and Section 63 of the Phase 18 specification, the following are **NOT IMPLEMENTED IN PHASE 18**:

- **VOICE/STT NOT IMPLEMENTED IN PHASE 18** (Reserved for Phase 19)
- **OCR NOT IMPLEMENTED IN PHASE 18** (Reserved for Phase 20)
- **TRANSLATION NOT IMPLEMENTED IN PHASE 18** (Reserved for Phase 21)
- **FACILITYGRAPH NOT IMPLEMENTED IN PHASE 18** (Reserved for Phase 22)
- **SIGNALGRAPH NOT IMPLEMENTED IN PHASE 18** (Reserved for Phase 23)

---

## 12. Verification & Regression Record

### Targeted Test Matrix:
- **Phase 18 AI Application (`test_phase18_ai_application.py`)**: 45/45 PASSED (100%)
  - Tests A through AV, plus Section 37 failure invariance, and AW config-driven factory tests.
  - All 10 mandatory adversarial prompt injection attacks tested and blocked.
- **Phase 13 Foundation Tests (`test_phase13_foundation.py`)**: PASSED
- **Phase 14 Auth & RBAC Tests (`test_phase14_auth_rbac.py`)**: PASSED
- **Phase 15 Intake Tests (`test_phase15_intake.py`)**: PASSED
- **Phase 16 Vitals & Deterministic Triage Tests (`test_phase16_triage.py`)**: PASSED
  - Total Phase 13-16 regression: 141/141 PASSED (100%)
- **Phase 17 Human Review Tests (`test_phase17_human_review.py`)**: 61/61 PASSED (100%)
- **AI Runtime Harness Tests (`test_ai_runtime_harness.py`)**: 20/20 PASSED (100%)
- **Clinical Scenario Tests (`test_clinical_scenarios.py`)**: 17/17 PASSED (100%)
- **Innovation Acceptance Tests (`test_innovation_acceptance.py`)**: 5/5 PASSED (100%)
- **Frontend Typecheck (`npx tsc --noEmit`)**: 0 errors (PASSED)
- **Frontend Linting (`npm run lint`)**: 0 warnings, 0 errors (PASSED)
- **Frontend Production Build (`npm run build`)**: 15/15 static pages successfully generated (PASSED)

### Total Verified Test Count:
**289 passing backend unit and regression tests** across all relevant active phases.

---

## 13. Limitations & Phase 19 Carry-Forward

1. **Local Model Hardware**: When running with actual local Qwen weights on resource-constrained PHC hardware, quantization (GGUF 4-bit) or fallback to `MockDeterministicAdapter` is recommended.
2. **Phase 19 Carry-Forward**: Multimodal intake via local Whisper speech-to-text (STT) and streaming audio transcription is planned for Phase 19.

---

**PHASE 18 STATUS: READY FOR HUMAN REVIEW**
