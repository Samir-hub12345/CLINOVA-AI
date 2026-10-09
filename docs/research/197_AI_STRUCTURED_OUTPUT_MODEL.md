# CLINOVA AI — Structured Output Enforcement Architecture

> **Document ID:** `RES-197`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering & Data Architecture Group  

---

## 1. The Structured Output Law

$$\mathbf{UNRESTRICTED\ PROSE\ IS\ FORBIDDEN\ FOR\ MACHINE\ INGESTION}$$

Language models generating unconstrained natural language introduce conversational preamble, Markdown noise, and hallucinated schema keys. In clinical software, unconstrained strings cannot be safely routed through deterministic early warning algorithms or database foreign key constraints.

**The Golden Law of Machine Ingestion:**
All generative AI outputs intended for downstream processing MUST be emitted as **syntactically valid, schema-conforming JSON objects**. If an LLM response cannot be parsed into its registered Pydantic schema, it is **instantly rejected** (`REJECTED_MALFORMED` or `REJECTED_SCHEMA`) and never passed to downstream application code.

---

## 2. Multi-Stage Schema Enforcement Mechanisms

CLINOVA implements a two-stage containment strategy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 DUAL-LAYER STRUCTURED OUTPUT CONSTRAINTS                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STAGE 1: RUNTIME DECODING CONSTRAINTS (IN-ENGINE) ]                      │
│  • Ollama: format="json" enforces JSON grammar in logits sampler.           │
│  • llama.cpp: GBNF Grammar forces the tokenizer to select only tokens       │
│    matching valid JSON production rules.                                    │
│                                                                             │
│  [ STAGE 2: DETERMINISTIC APPLICATION BARRIER (POST-ENGINE) ]               │
│  • OutputValidator parses string and strips any accidental Markdown fences. │
│  • Pydantic v2 strict model parsing verifies all required fields.           │
│  • Physiological boundary checks (e.g. HR in [20, 300]) evaluated.          │
│  • Forbidden action scanner inspects values for illegal clinical commands.  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Universal Response Envelope Schema

Every structured output payload is enclosed within the standard CLINOVA envelope:

```python
class BaseAIResponse(BaseModel):
    status: str                         # SUCCESS | SUCCESS_CACHED | REJECTED | FALLBACK
    model: str                          # e.g. qwen3-4b-instruct
    model_version: str                  # e.g. 1.0.0
    runtime: str                        # e.g. local_qwen_runtime
    prompt_id: str                      # e.g. PROMPT_EXTRACTION
    prompt_version: str                 # e.g. 1.0.0
    generated_at: str                   # ISO-8601 UTC timestamp
    source_references: List[EvidenceRef]# Array of evidence UUIDs fed to context
    confidence: Optional[float]         # Predictive probability score [0.0, 1.0]
    warnings: List[str]                 # Non-fatal ambiguity flags
    validation_state: ValidationStatus  # VALID | REJECTED_*
    epistemic_state: str                # AI_INFERRED
    payload: Dict[str, Any]             # Task-specific validated dictionary
```

---

## 4. Failure Handling & Fatal Invalidation

An AI output is classified as **FATALLY INVALID** under any of the following conditions:
1. **JSON Syntax Error:** Unclosed quotes, missing braces, or truncated text.
2. **Missing Required Key:** Any required attribute (e.g. `source_evidence_id` in `ExtractedSymptom` or `uncertainty_statement` in `SummaryPayload`) is absent.
3. **Type Mismatch:** A vital sign value passed as a non-numeric string (e.g. `"HR": "fast"` instead of `"HR": 110.0`).
4. **Physiological Limit Breach:** Extracted values exceed biological viability (e.g. `SBP = 950 mmHg`).
5. **Forbidden Clinical Action:** Text contains prescriptions, discharge orders, or claims of definitive medical diagnosis.

Under any of these conditions, the output is marked `REJECTED`, audited, and prevented from altering application state.
