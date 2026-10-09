# CLINOVA AI — Phase 10 Architectural Decision Records (ADRs)

> **Document ID:** `DECISION-LOG-PHASE-10`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Safety Informatics & AI Governance Group  

---

## Decision 10.1: Primary Local Model Strategy
- **Context:** CLINOVA requires a local, open-source, zero-cost Small Language Model (SLM) capable of high-fidelity clinical narrative parsing, structured JSON generation, and Indic vernacular comprehension (Hindi, Odia).
- **Decision:** Select **Qwen3-4B-Instruct (GGUF Q4_K_M)** as the primary development and workstation model, with **Qwen2.5-1.5B-Instruct (GGUF Q4_K_M)** as the ultra-lightweight deployment model for ₹14,000 rural edge Mini-PCs (8GB RAM).
- **Rationale:** Permissive Apache 2.0 license, expanded 152k tokenizer with native Eastern Indic support, low memory footprint ($< 2.8\text{ GB}$ RAM), and high adherence to grammar-guided JSON extraction.
- **Alternatives Rejected:** Llama 3.2 3B (weak Odia comprehension; community license restrictions); BioMistral 7B (English-only; poor Indic support); vLLM / 70B models (excessive hardware costs).

---

## Decision 10.2: Decoupled Three-Tier Runtime Architecture
- **Context:** Binding application code directly to an inference engine creates brittle vendor lock-in and impedes cross-environment deployments.
- **Decision:** Formalize a three-tier decoupled runtime pattern: `AIAdapter` $\to$ `RuntimeAdapter` $\to$ `Model`, with dual concrete adapters for **Ollama** (`http://127.0.0.1:11434`) and **llama.cpp / llama-server** (`http://127.0.0.1:8080`), backed by a hermetic `MockDeterministicAdapter`.
- **Rationale:** Enables zero-dependency unit testing, allows drop-in binary deployment on edge Mini-PCs via pure C++ llama-server, and provides seamless one-command developer workflow via Ollama.

---

## Decision 10.3: Strict Structured Output Law
- **Context:** Freeform conversational LLM completions introduce markdown code fences, conversational fluff, and unpredictable keys that break downstream deterministic logic.
- **Decision:** Enforce that all machine-consumed AI outputs MUST be valid JSON adhering strictly to registered Pydantic schemas. Unrestricted prose is permanently prohibited for machine ingestion.
- **Rationale:** Prevents parsing crashes, enables compile-time type verification, and allows deterministic validation barriers to inspect values before state mutations.

---

## Decision 10.4: Fail-Closed Output Validation Gatekeeper
- **Context:** Generative models are susceptible to hallucinating impossible physiological values (e.g. HR=999 bpm) or asserting unauthorized clinical commands.
- **Decision:** Implement `OutputValidator`, a deterministic post-inference gatekeeper that evaluates JSON syntax, forbidden clinical actions, physiological ranges, and evidence citations. Any violation triggers immediate `REJECTED_*` status.
- **Rationale:** Upholds the Golden Law of Clinical Safety: *Never silently repair medically meaningful output*. Malformed responses are dropped, audited, and routed to safe deterministic fallbacks.

---

## Decision 10.5: Decoupling AI Confidence from Clinical Uncertainty
- **Context:** LLMs frequently produce fluent, confident prose even when critical clinical facts are absent. Confusing model predictive confidence with clinical risk creates fatal false-security traps.
- **Decision:** Mathematically isolate AI predictive confidence ($C$) from mathematical epistemic uncertainty ($U_t$) and physiological risk (NEWS2). Enforce the invariant: $\frac{\partial U_t}{\partial C} = 0$.
- **Rationale:** Ensures that missing essential clinical data (ECG, troponins) keeps uncertainty high regardless of how confident the language model sounds.

---

## Decision 10.6: Prompt Injection Defense via Delimited Context
- **Context:** Scanned OCR documents and patient speech transcripts are untrusted data streams that may contain adversarial injection strings ("ignore instructions", "mark as verified").
- **Decision:** Implement `InputSanitizer` to detect override patterns and encapsulate raw text inside `<untrusted_input_data>` passive data blocks with XML tag escaping.
- **Rationale:** Guarantees that untrusted patient content is processed strictly as passive perceptual data, never as system-level execution directives.

---

## Decision 10.7: Minimum-Necessary Episodic Context Pack Assembly
- **Context:** Feeding complete medical charts to models wastes token budgets, slows edge CPU inference, and violates data protection standards.
- **Decision:** Assemble focused Context Packs containing only current acute episode observations, while strictly excluding direct identifiers (Aadhaar, phone, name), administrative billing data, and private doctor notes.
- **Rationale:** Complies with Section 6 of the DPDP Act 2023 (Data Minimisation) and enhances LLM attention focus on relevant clinical signals.

---

## Decision 10.8: Multilingual Vernacular Colloquial Preservation
- **Context:** Rural Indian patients describe acute emergencies using regional idioms (*"chhati re gapa gapa laguchi"*). Naive translation strips the somatic metaphor.
- **Decision:** Mandate that translation and extraction operations preserve original patient phrasing verbatim in `source_text` alongside translated concepts, and record regional terms in an explicit `preserved_colloquialisms` dictionary.
- **Rationale:** Protects clinical nuance, prevents diagnostic errors, and allows dialect-speaking physicians to cross-reference raw patient words on the workbench.

---

## Decision 10.9: Deterministic Evidence-Fingerprinted Caching
- **Context:** Re-running SLM inference on every UI re-render causes CPU thrashing on edge hardware; however, serving stale AI outputs when patient status changes is dangerous.
- **Decision:** Implement `AICache` in volatile RAM, keyed to a SHA-256 hash incorporating the case ID, task name, prompt version, model version, and the deterministic fingerprint of input evidence items.
- **Rationale:** Serves instant ($<1\text{ms}$) cached responses for identical views, while guaranteeing instant invalidation the moment any vital sign or clinical note is added.

---

## Decision 10.10: Isolated Scaffolding & 20-Scenario Verification
- **Context:** Phase 10 must establish runtime foundations without prematurely integrating into production patient workflows.
- **Decision:** House all runtime scaffolding strictly in `backend/app/ai_runtime/` and implement 20 comprehensive test scenarios in `backend/tests/ai_runtime/`, verified via a standalone direct runner.
- **Rationale:** Satisfies the Atomic Phase Rule, proves fail-safe operation, and provides a verified foundation for subsequent phases without creating coupling to live triage services.
