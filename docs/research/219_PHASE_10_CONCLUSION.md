# CLINOVA AI — Phase 10 Final Local AI Runtime Foundation Report

> **Document ID:** `RES-219`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Safety Informatics & AI Systems Group  

---

## 1. PHASE
**PHASE 10 — LOCAL AI RUNTIME FOUNDATION & SAFE INFERENCE ARCHITECTURE**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Architectural Role: *Establishing the definitive, local-first, open-source-first, zero-mandatory-cost, auditable, and fail-safe AI runtime foundation decoupling clinical safety logic from probabilistic machine learning models.*

---

## 2. OBJECTIVE
The primary objective of Phase 10 is to design, model, formalize, and validate the complete local AI runtime architecture for CLINOVA AI without executing Phase 11 (live clinical intake), modifying production patient workflows, executing database migrations, or deploying services.

The foundation guarantees:
- **Local-First & Zero-Cost:** ₹0 mandatory commercial API fees; powered by open-weight Qwen SLMs running via local Ollama or llama.cpp on standard CPU/GPU hardware.
- **Fail-Closed Safety Gatekeeper:** Deterministic post-inference validation blocking autonomous diagnoses, prescriptions, ward admissions, and ungrounded hallucinations.
- **Epistemic Uncertainty Independence:** Separation of model predictive confidence ($C$) from mathematical clinical uncertainty ($U_t$) and physiological early warning scoring (NEWS2).
- **Prompt Injection Defense:** Active sanitization and passive data delimitation neutralizing prompt override and role hijacking attacks.
- **Vernacular Preservation:** Lossless capture of regional Odia and Hindi idioms alongside standardized clinical translations.
- **Isolated Non-Production Scaffolding:** Clean implementation and verification of 20 test scenarios strictly within `backend/app/ai_runtime/` and `backend/tests/ai_runtime/`.

---

## 3. SOURCE MATERIAL
Phase 10 synthesizes and reconciles seventeen statutory, clinical, and architectural frameworks:
- **Statutory Indian Frameworks:** National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Regulations 27 & 28); Bharatiya Sakshya Adhiniyam (BSA) 2023 (Section 63); Digital Personal Data Protection (DPDP) Act 2023 (Sections 4, 6, 8); Supreme Court *Paschim Banga* emergency doctrine (1996).
- **Clinical Safety & Terminology Standards:** Royal College of Physicians NEWS2; Shock Index; SNOMED-CT; LOINC; ICD-11; MedAbstain benchmark framework.
- **Immediate Upstream Baseline:** Phases 1–9 research and architecture specifications (`docs/research/00_*` through `docs/research/191_*`), current repository configuration files, and domain models.

---

## 4. MODEL SELECTION RESULT
Specified in `docs/research/193_AI_MODEL_SELECTION.md` (`RES-193`):
- Selected **Qwen3-4B-Instruct** (GGUF `Q4_K_M`, ~2.8 GB RAM footprint) as the primary local development and workstation base model.
- Selected **Qwen2.5-1.5B-Instruct** (GGUF `Q4_K_M`, ~1.2 GB RAM footprint) as the ultra-lightweight deployment model for resource-constrained edge Mini-PCs (8GB RAM).
- Formally recorded that CLINOVA does NOT claim clinical validation, medical accuracy, or proprietary pre-training of base weights.

---

## 5. RUNTIME BACKEND RESULT
Specified in `docs/research/194_AI_RUNTIME_BACKEND_MODEL.md` (`RES-194`):
- Established three-tier decoupling: `AIAdapter` $\to$ `RuntimeAdapter` $\to$ `Model`.
- Selected **Ollama** (`http://127.0.0.1:11434`) as primary developer and demo runtime.
- Selected **llama.cpp / llama-server** (`http://127.0.0.1:8080`) as primary lightweight CPU edge runtime.
- Rejected vLLM and heavy PyTorch Transformers for edge deployment due to excessive memory overhead.

---

## 6. ADAPTER RESULT
Specified in `docs/research/195_AI_ADAPTER_INTERFACE.md` (`RES-195`):
- Formalized abstract `AIAdapter` interface providing `generate_structured()`, `extract_entities()`, `summarize()`, `translate()`, and `generate_questions()`.
- Bounded timeouts ($3.5\text{s}$ to $6.0\text{s}$), locked temperature ($0.0$), and isolated coroutine cancellation.

---

## 7. TASK CONTRACT RESULT
Specified in `docs/research/196_AI_TASK_CONTRACTS.md` (`RES-196`):
- Defined strongly-typed Pydantic contracts for all seven machine-consumed tasks (`EXTRACTION`, `SUMMARY`, `QUESTION_GENERATION`, `TRANSLATION`, `NORMALIZATION`, `DRAFT_NOTE`, `ADVISORY`).
- Mandated universal base envelope (`BaseAIResponse`) recording status, model lineage, timestamp, source citations, and validation state.

---

## 8. STRUCTURED OUTPUT RESULT
Specified in `docs/research/197_AI_STRUCTURED_OUTPUT_MODEL.md` (`RES-197`):
- Enforced the Structured Output Law: Unrestricted natural language prose is strictly forbidden for machine ingestion.
- Combined engine-level grammar decoding (GBNF / Ollama JSON mode) with post-inference Pydantic v2 validation.

---

## 9. PROMPT ARCHITECTURE RESULT
Specified in `docs/research/198_AI_PROMPT_ARCHITECTURE.md` (`RES-198`):
- Cataloged seven versioned system prompts (`PROMPT_EXTRACTION_V1` through `PROMPT_ADVISORY_V1`).
- Enforced non-diagnostic behavior, uncertainty preservation, anti-fabrication rules, and mandatory evidence citations.

---

## 10. GROUNDING RESULT
Specified in `docs/research/199_AI_GROUNDING_MODEL.md` (`RES-199`):
- Established the minimum-necessary context pipeline: `CASE DATA` $\to$ `EVIDENCE FILTER` $\to$ `CONTEXT PACK` $\to$ `AI`.
- Excluded direct patient identifiers (Aadhaar, phone, name), administrative billing data, and private clinician notes from context.
- Enforced deterministic citation membership verification against input evidence IDs.

---

## 11. PROMPT INJECTION RESULT
Specified in `docs/research/200_PROMPT_INJECTION_DEFENSE.md` (`RES-200`):
- Established five-layer defense perimeter for untrusted OCR, audio transcripts, and patient portal text.
- Implemented `InputSanitizer` to detect override patterns and wrap inputs inside passive `<untrusted_input_data>` delimiters with tag escaping.

---

## 12. OUTPUT VALIDATION RESULT
Specified in `docs/research/201_AI_OUTPUT_VALIDATION.md` (`RES-201`):
- Implemented fail-closed `OutputValidator` evaluating JSON syntax, forbidden actions (prescriptions, admissions, discharges), physiological boundaries (HR, BP, SpO2, Temp), and citation links.
- Codified the non-repair law: Malformed or unsafe outputs are rejected immediately without silent guessing.

---

## 13. HALLUCINATION CONTROL RESULT
Specified in `docs/research/202_HALLUCINATION_CONTROL.md` (`RES-202`):
- Formulated the seven-layer hallucination control perimeter.
- Mandated that clinical hypotheses lacking supporting evidence in context are tagged as ungrounded and suppressed from primary clinical views.

---

## 14. UNCERTAINTY BOUNDARY RESULT
Specified in `docs/research/203_AI_UNCERTAINTY_BOUNDARY.md` (`RES-203`):
- Enforced the four-way separation between AI Predictive Confidence ($C$), Epistemic Uncertainty ($U_t$), Physiological Risk (NEWS2), and Evidentiary Verification.
- Codified the invariant: An LLM sounding confident can never decrease $U_t$.

---

## 15. MODEL VERSIONING RESULT
Specified in `docs/research/204_AI_MODEL_VERSIONING.md` (`RES-204`):
- Bound every inference to eight immutable attributes: `model_id`, `model_version`, `quantization`, `runtime`, `runtime_version`, `prompt_version`, `config_version`, and generation timestamp.
- Enforced that updating model weights creates a new identifiable configuration and invalidates previous caches.

---

## 16. INFERENCE LIFECYCLE RESULT
Specified in `docs/research/205_AI_INFERENCE_LIFECYCLE.md` (`RES-205`):
- Mapped the eight canonical lifecycle states (`MODEL_DISCOVERY` to `RELEASE`) and six failure states (`MODEL_UNAVAILABLE` to `PROCESS_CRASH`).
- Enforced that model crashes or OOM events never block deterministic clinical care.

---

## 17. RESOURCE GOVERNANCE RESULT
Specified in `docs/research/206_AI_RESOURCE_GOVERNANCE.md` (`RES-206`):
- Bounded model RAM to $\le 3200\text{ MB}$ on edge Mini-PCs and restricted concurrency to 1 serial request.
- Prioritized real-time vital sign recording and NEWS2 evaluation above AI inference tasks in edge CPU scheduling.

---

## 18. MODEL LOAD RESULT
Specified in `docs/research/207_AI_MODEL_LOAD_STRATEGY.md` (`RES-207`):
- Selected the Persistent Warm Memory Map (`mmap`) strategy with boot-time warmup for hackathon and clinical workstations.
- Outlined emergency RAM eviction protocols when host memory drops below $10\%$.

---

## 19. OFFLINE RESULT
Specified in `docs/research/208_AI_OFFLINE_BEHAVIOR.md` (`RES-208`):
- Defined tri-state availability (`AI_AVAILABLE`, `AI_DEGRADED`, `AI_UNAVAILABLE`).
- Guaranteed that when AI is offline, deterministic triage operates at 100%, manual typing is enabled, and zero fake AI outputs are generated.

---

## 20. MULTILINGUAL RESULT
Specified in `docs/research/209_AI_MULTILINGUAL_MODEL.md` (`RES-209`):
- Codified the Original Text Preservation Law: Translations must never destroy original patient phrasing.
- Implemented structured capture of regional somatic idioms (Odia *"chhati re gapa gapa"*, Hindi *"kaleja kaanpna"*).

---

## 21. LOCAL PRIVACY RESULT
Specified in `docs/research/210_AI_LOCAL_PRIVACY.md` (`RES-210`):
- Enforced zero outbound network egress to external cloud AI APIs, strictly complying with the DPDP Act 2023.
- Restricted inference transport to localhost socket `127.0.0.1` and volatile memory scrubbing.

---

## 22. CACHE RESULT
Specified in `docs/research/211_AI_CACHE_MODEL.md` (`RES-211`):
- Implemented deterministic RAM caching keyed to SHA-256 hash of `case_id`, `task`, `prompt_version`, `model_id`, and `source_evidence_fingerprint`.
- Enforced instant cache invalidation upon any alteration to underlying case observations.

---

## 23. RESULT PROVENANCE
Specified in `docs/research/212_AI_RESULT_PROVENANCE.md` (`RES-212`):
- Bound all AI inferences to the Phase 7 provenance chain and `ai_inferences` table.
- Permanently stamped outputs with epistemic state `AI_INFERRED`, legally prohibiting autonomous self-verification.

---

## 24. RESULT LIFECYCLE
Specified in `docs/research/213_AI_RESULT_LIFECYCLE.md` (`RES-213`):
- Established the eight lifecycle states (`GENERATED` to `EXPIRED`).
- Codified the Clinician Modification Ledger preserving original AI suggestions alongside physician overrides.

---

## 25. TEST HARNESS RESULT
Specified in `docs/research/214_AI_TEST_HARNESS.md` (`RES-214`):
- Implemented and verified all **twenty isolated test scenarios** in `backend/tests/ai_runtime/`:
  1. Valid structured output (PASS)
  2. Malformed JSON (PASS)
  3. Missing required field (PASS)
  4. Hallucinated fact / citation failure (PASS)
  5. Unsupported diagnosis (PASS)
  6. Prescription request (PASS)
  7. Prompt injection defense (PASS)
  8. Evidence-less hypothesis (PASS)
  9. Multilingual input preservation (PASS)
  10. Long context input (PASS)
  11. Empty input (PASS)
  12. Model timeout fallback (PASS)
  13. Out-of-memory fallback (PASS)
  14. Model unavailable fallback (PASS)
  15. Conflicting evidence uncertainty (PASS)
  16. Stale cache invalidation (PASS)
  17. Wrong evidence references (PASS)
  18. Invalid numeric vital ranges (PASS)
  19. Prohibited autonomous disposition (PASS)
  20. Clinician override ledger preservation (PASS)

---

## 26. BENCHMARK RESULT
Specified in `docs/research/215_AI_BENCHMARK_FRAMEWORK.md` (`RES-215`):
- Formalized future eight-dimension evaluation protocol (Extraction Accuracy, Schema Validity, Grounding Precision, Hallucination Rate, Multilingual Quality, Latency, Memory, Failure Recovery).
- Strictly separated design expectations from empirical benchmarks.

---

## 27. MODEL CARD RESULT
Specified in `docs/research/216_CLINOVA_AI_MODEL_CARD.md` (`RES-216`):
- Authored complete runtime model card detailing base model source (Qwen3-4B / Qwen2.5-1.5B), Apache 2.0 license, intended advisory uses, prohibited autonomous tasks, and prominent regulatory disclaimers.

---

## 28. ZERO-COST RESULT
Specified in `docs/research/217_AI_ZERO_COST_MODEL.md` (`RES-217`):
- Verified **₹0.00 / month recurring software OpEx** across all core clinical capabilities.
- Confirmed zero mandatory dependencies on commercial AI vendors (OpenAI, Google Gemini, Anthropic).

---

## 29. TRACEABILITY RESULT
Specified in `docs/research/218_AI_RUNTIME_TRACEABILITY.md` (`RES-218`):
- Constructed complete bidirectional traceability linking statutory Indian laws (NMC, BSA, DPDP), BPUT baseline requirements (`B01`–`B18`), and Core Innovations (`C01`–`C11`) directly to Phase 10 runtime components.

---

## 30. IMPLEMENTATION FILES CREATED
Phase 10 created isolated non-production runtime scaffolding strictly within approved directories:

### Scaffolding in `backend/app/ai_runtime/`:
1. `backend/app/ai_runtime/__init__.py`: Module initialization and metadata.
2. `backend/app/ai_runtime/models.py`: Runtime enums, descriptors, and configuration models.
3. `backend/app/ai_runtime/schemas/__init__.py`: Schema package exports.
4. `backend/app/ai_runtime/schemas/contracts.py`: Strongly-typed Pydantic contracts for 7 tasks.
5. `backend/app/ai_runtime/validation/__init__.py`: Validation package exports.
6. `backend/app/ai_runtime/validation/sanitizer.py`: Prompt injection defense and delimiter framing.
7. `backend/app/ai_runtime/validation/output_validator.py`: Deterministic safety gatekeeper.
8. `backend/app/ai_runtime/prompts/__init__.py`: Prompts package exports.
9. `backend/app/ai_runtime/prompts/templates.py`: Versioned prompt templates and registry.
10. `backend/app/ai_runtime/adapters/__init__.py`: Adapters package exports.
11. `backend/app/ai_runtime/adapters/base.py`: Abstract `AIAdapter` and `RuntimeAdapter` classes.
12. `backend/app/ai_runtime/adapters/default_adapter.py`: Canonical `DefaultAIAdapter` implementation.
13. `backend/app/ai_runtime/adapters/mock_adapter.py`: Hermetic deterministic test double.
14. `backend/app/ai_runtime/adapters/ollama_adapter.py`: Local Ollama REST client.
15. `backend/app/ai_runtime/adapters/llamacpp_adapter.py`: Local llama.cpp / llama-server client.
16. `backend/app/ai_runtime/cache.py`: Deterministic evidence-fingerprinted RAM cache.
17. `backend/app/ai_runtime/service.py`: End-to-end safe runtime orchestration facade.

### Test Scaffolding in `backend/tests/ai_runtime/`:
18. `backend/tests/ai_runtime/__init__.py`: Test suite initialization.
19. `backend/tests/ai_runtime/test_ai_runtime_harness.py`: Comprehensive 20-scenario test suite.
20. `backend/tests/ai_runtime/run_standalone_tests.py`: Standalone direct execution runner.

---

## 31. IMPLEMENTATION FILES MODIFIED
- **None.** (Zero existing clinical domain or backend files were altered).

---

## 32. ARCHITECTURAL CONFLICTS
Phase 10 investigated and resolved three key architectural conflicts:
1. **Generative Autonomy vs. Statutory Physician Monopoly:** Generative models naturally tend to emit definitive statements ("Patient has Acute Appendicitis; admit to ward"). Resolved by enforcing strict fail-closed regex barriers (`OutputValidator`) intercepting definitive claims and converting them to advisory candidate considerations.
2. **Model Confidence vs. Clinical Uncertainty:** Probabilistic models often emit high token probabilities for ungrounded text. Resolved by decoupling AI confidence ($C$) from mathematical clinical uncertainty ($U_t$), mathematically prohibiting $C$ from altering $U_t$.
3. **Cloud LLM API Convenience vs. Zero-Cost & DPDP Egress Law:** Third-party cloud APIs introduce recurring costs and cross-border data leakage risks. Resolved by mandating 100% on-premise local open-weight SLMs with zero outbound WAN egress.

---

## 33. CLAIMS NARROWED
1. **Clinical Diagnostic Claims:** Explicitly narrowed all AI capabilities to non-diagnostic, advisory decision support; revoked any autonomous diagnostic authority.
2. **Hardware Sizing:** Narrowed edge reasoning expectations to quantized 1.5B–4B parameter models running on CPU cores rather than unquantized large models.
3. **Vernacular Translation Scope:** Narrowed translation guarantees to clinical narrative comprehension with colloquial preservation; recognized extreme tribal dialects as requiring human clarification.

---

## 34. CLAIMS REMOVED
1. **Proprietary Pre-Trained Medical Model:** Removed any claim that CLINOVA has pre-trained a proprietary foundation LLM; affirmed that CLINOVA provides runtime orchestration around open weights.
2. **Empirical Diagnostic Accuracy Benchmarks:** Stripped any unmeasured claims of diagnostic sensitivity/specificity; replaced with formal evaluation protocols.
3. **Autonomous Verification:** Eliminated any mechanism for an AI model to mark evidence records as `VERIFIED`.

---

## 35. UNRESOLVED QUESTIONS
1. **Empirical Edge CPU Latency on Intel Celeron N5105:** Exact token generation speed for `Qwen2.5-1.5B-Q4_K_M` under thermal load in non-air-conditioned rural clinics requires physical benchmarking during hardware commissioning.
2. **Indic Transliteration Edge Cases:** Rare Odia colloquialisms spelled phonetically in English script by frontline staff require continued dictionary expansion.
3. **AVX-512 vs. AVX2 Compile Flags:** Optimal binary compilation flags for low-cost Indian Mini-PCs must be validated across specific processor stepping revisions.

---

## 36. RISKS
1. **Risk of Frontend Bypassing Validation:** Future developers might inadvertently call the AI runtime directly from frontend components.  
   *Mitigation:* AI runtime is strictly contained within backend services; no public API exposes raw unvalidated completions.
2. **Risk of Clinician Over-Reliance (Automation Bias):** Attending physicians might accept AI draft notes without careful verification.  
   *Mitigation:* Non-dismissible advisory visual badges and required affirmative signature step.
3. **Risk of Thermal Throttling on Fanless Edge PCs:** High ambient temperatures could trigger CPU downclocking during patient surges.  
   *Mitigation:* AI inference is throttled or deferred during casualty surges to prioritize deterministic vitals recording.

---

## 37. FILES CREATED
Phase 10 authored and committed all **thirty required research and architecture documents** in `docs/research/`:
1. `docs/research/192_AI_RUNTIME_RESEARCH_PLAN.md` (`RES-192`)
2. `docs/research/193_AI_MODEL_SELECTION.md` (`RES-193`)
3. `docs/research/194_AI_RUNTIME_BACKEND_MODEL.md` (`RES-194`)
4. `docs/research/195_AI_ADAPTER_INTERFACE.md` (`RES-195`)
5. `docs/research/196_AI_TASK_CONTRACTS.md` (`RES-196`)
6. `docs/research/197_AI_STRUCTURED_OUTPUT_MODEL.md` (`RES-197`)
7. `docs/research/198_AI_PROMPT_ARCHITECTURE.md` (`RES-198`)
8. `docs/research/199_AI_GROUNDING_MODEL.md` (`RES-199`)
9. `docs/research/200_PROMPT_INJECTION_DEFENSE.md` (`RES-200`)
10. `docs/research/201_AI_OUTPUT_VALIDATION.md` (`RES-201`)
11. `docs/research/202_HALLUCINATION_CONTROL.md` (`RES-202`)
12. `docs/research/203_AI_UNCERTAINTY_BOUNDARY.md` (`RES-203`)
13. `docs/research/204_AI_MODEL_VERSIONING.md` (`RES-204`)
14. `docs/research/205_AI_INFERENCE_LIFECYCLE.md` (`RES-205`)
15. `docs/research/206_AI_RESOURCE_GOVERNANCE.md` (`RES-206`)
16. `docs/research/207_AI_MODEL_LOAD_STRATEGY.md` (`RES-207`)
17. `docs/research/208_AI_OFFLINE_BEHAVIOR.md` (`RES-208`)
18. `docs/research/209_AI_MULTILINGUAL_MODEL.md` (`RES-209`)
19. `docs/research/210_AI_LOCAL_PRIVACY.md` (`RES-210`)
20. `docs/research/211_AI_CACHE_MODEL.md` (`RES-211`)
21. `docs/research/212_AI_RESULT_PROVENANCE.md` (`RES-212`)
22. `docs/research/213_AI_RESULT_LIFECYCLE.md` (`RES-213`)
23. `docs/research/214_AI_TEST_HARNESS.md` (`RES-214`)
24. `docs/research/215_AI_BENCHMARK_FRAMEWORK.md` (`RES-215`)
25. `docs/research/216_CLINOVA_AI_MODEL_CARD.md` (`RES-216`)
26. `docs/research/217_AI_ZERO_COST_MODEL.md` (`RES-217`)
27. `docs/research/218_AI_RUNTIME_TRACEABILITY.md` (`RES-218`)
28. `docs/research/219_PHASE_10_CONCLUSION.md` (`RES-219`)
29. `docs/research/SOURCES_PHASE_10.md` (`SOURCES-PHASE-10`)
30. `docs/research/PHASE_10_DECISIONS.md` (`DECISION-LOG-PHASE-10`)

And created **twenty isolated non-production code files** in `backend/`:
1. `backend/app/ai_runtime/__init__.py`
2. `backend/app/ai_runtime/models.py`
3. `backend/app/ai_runtime/schemas/__init__.py`
4. `backend/app/ai_runtime/schemas/contracts.py`
5. `backend/app/ai_runtime/validation/__init__.py`
6. `backend/app/ai_runtime/validation/sanitizer.py`
7. `backend/app/ai_runtime/validation/output_validator.py`
8. `backend/app/ai_runtime/prompts/__init__.py`
9. `backend/app/ai_runtime/prompts/templates.py`
10. `backend/app/ai_runtime/adapters/__init__.py`
11. `backend/app/ai_runtime/adapters/base.py`
12. `backend/app/ai_runtime/adapters/default_adapter.py`
13. `backend/app/ai_runtime/adapters/mock_adapter.py`
14. `backend/app/ai_runtime/adapters/ollama_adapter.py`
15. `backend/app/ai_runtime/adapters/llamacpp_adapter.py`
16. `backend/app/ai_runtime/cache.py`
17. `backend/app/ai_runtime/service.py`
18. `backend/tests/ai_runtime/__init__.py`
19. `backend/tests/ai_runtime/test_ai_runtime_harness.py`
20. `backend/tests/ai_runtime/run_standalone_tests.py`

---

## 38. FILES MODIFIED
- **None.** (Zero existing clinical domain or production files were modified).

---

## 39. FILES INTENTIONALLY UNTOUCHED
- `frontend/src/` (Zero UI components or patient screens touched).
- `backend/app/domain/` (Existing clinical state machines, NEWS2 scoring, and triage queues preserved 100% untouched).
- `backend/app/core/` (Core application settings preserved untouched).
- `backend/app/api/` (Zero live patient endpoints connected to AI).
- `backend/alembic/` (Zero database migrations executed).
- Active database instances (`clinova-dev.db` preserved intact).

---

## 40. PHASE STATUS
**READY FOR HUMAN REVIEW**
