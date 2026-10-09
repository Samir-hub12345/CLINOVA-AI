# CLINOVA AI — AI Adapter Interface & Contract Specification

> **Document ID:** `RES-195`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Architecture, API Contracts & System Integration Working Group  

---

## 1. Stable Internal Interface Definition

The `AIAdapter` interface defines the single boundary through which CLINOVA backend services interact with artificial intelligence capabilities. In strict accordance with Phase 10 rules, these methods are defined and validated via isolated test doubles, and are **not yet wired into live patient intake or triage loops**.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel

class AIAdapter(ABC):
    """Authoritative abstract boundary isolating AI engines from clinical domains."""

    @abstractmethod
    async def generate_structured(
        self,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        target_schema: Type[BaseModel],
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout_seconds: float = 5.0,
    ) -> BaseModel:
        """Executes structured LLM generation with schema enforcement and post-validation."""
        pass

    @abstractmethod
    async def extract_entities(
        self,
        narrative_text: str,
        source_evidence_id: str,
        temperature: float = 0.0,
    ) -> BaseModel:
        """Extracts symptoms, vitals, allergies, and medications from clinical text."""
        pass

    @abstractmethod
    async def summarize(
        self,
        case_narratives: List[Dict[str, Any]],
        temperature: float = 0.0,
    ) -> BaseModel:
        """Synthesizes clinical chronologies while explicitly declaring uncertainty."""
        pass

    @abstractmethod
    async def translate(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str = "en",
    ) -> BaseModel:
        """Translates vernacular text while preserving regional clinical terminology."""
        pass

    @abstractmethod
    async def generate_questions(
        self,
        identified_gaps: List[str],
        clinical_context: str,
    ) -> BaseModel:
        """Formulates targeted clarification inquiries to close epistemic gaps."""
        pass
```

---

## 2. Parameter & Invariant Specifications per Operation

| Operation | Default Temperature | Timeout Ceiling | Max Tokens | Output Format | Deterministic Validation Guard | Provenance Tag |
|:---|:---|:---|:---|:---|:---|:---|
| `generate_structured()` | $0.0$ | $5.0\text{ s}$ | $1024$ | JSON Object | Schema match + Forbidden action check | `AI_INFERRED` |
| `extract_entities()` | $0.0$ | $3.5\text{ s}$ | $768$ | JSON (`ExtractionResult`) | Physiological range check + Citation check | `AI_INFERRED` |
| `summarize()` | $0.0$ | $6.0\text{ s}$ | $1200$ | JSON (`SummaryResult`) | Non-diagnostic check + Uncertainty check | `AI_INFERRED` |
| `translate()` | $0.0$ | $3.0\text{ s}$ | $512$ | JSON (`TranslationResult`) | Colloquialism preservation check | `AI_INFERRED` |
| `generate_questions()` | $0.2$ | $4.0\text{ s}$ | $512$ | JSON (`QuestionResult`) | Patient safety alarm check | `AI_INFERRED` |

---

## 3. Request & Response Payload Lifecycles

Every operation executed via `AIAdapter` adheres to an immutable four-stage cycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OPERATION LIFECYCLE SEQUENCE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. SANITIZED REQUEST ASSEMBLY                                              │
│     • Evidence items filtered to minimum requisite context                  │
│     • Raw text wrapped in defensive isolation tags (<untrusted_input_data>) │
│                                                                             │
│  2. LOCAL RUNTIME EXECUTION                                                 │
│     • Temperature locked at 0.0 for deterministic reproducibility           │
│     • Strict timeout enforced via async cancellation token                  │
│                                                                             │
│  3. FAIL-CLOSED OUTPUT VALIDATION                                           │
│     • Output parsed into JSON                                               │
│     • Checked against forbidden clinical actions (Rx, Admission, Discharge) │
│     • Checked against physiological limits (HR, BP, SpO2)                   │
│     • Validated against source evidence IDs                                 │
│                                                                             │
│  4. IMMUTABLE METADATA ATTACHMENT                                           │
│     • Model name, version, prompt version, timestamp stamped                │
│     • Epistemic state set to AI_INFERRED                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Fallback Execution Protocol

If an adapter method raises a `TimeoutError`, `MemoryError`, or receives malformed data from the local engine:
1. The exception is trapped within the adapter layer.
2. An audit warning event is logged to technical logs.
3. The adapter returns a structured `FALLBACK` response with `status: "FALLBACK"` and `validation_state: REJECTED_*` (including `REJECTED_UNAVAILABLE` when the inference daemon is offline or unreachable).
4. The caller receives zero synthetic hallucinations. The UI gracefully continues with manual transcription and deterministic triage.

---

## 5. Concrete Default AI Adapter Implementation (`DefaultAIAdapter`)

The authoritative implementation of the `AIAdapter` interface is provided in `backend/app/ai_runtime/adapters/default_adapter.py` and exported via `backend/app/ai_runtime/adapters/__init__.py`.

```python
from app.ai_runtime.adapters.default_adapter import DefaultAIAdapter
from app.ai_runtime.adapters.mock_adapter import MockDeterministicAdapter

runtime = MockDeterministicAdapter()
adapter = DefaultAIAdapter(runtime)
```

### Key Functional Responsibilities:
1. **Delegation to RuntimeAdapter:** Decouples task-specific orchestration from backend inference engines (`invoke_raw()`).
2. **Untrusted Data Sanitization:** Routes narrative inputs through `InputSanitizer.sanitize()` prior to prompt encapsulation, defending against injection attacks.
3. **Strict Schema Parsing:** Enforces Pydantic model validation on raw engine outputs, ensuring structural compliance before application consumption.
4. **Epistemic Integrity:** Does not alter clinical state or allow autonomous action, returning structured contract payloads only.
