# CLINOVA AI — AI Configuration Boundary & Degradation Model

> **Document ID:** `RES-178`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** AI Safety, Clinical Systems Integration & Fail-Safe Architecture Group  

---

## 1. Phase 9 Boundary Law: Zero AI Implementation

In strict compliance with the **Atomic Phase Rule**, Phase 9 does NOT implement, initialize, or execute machine learning models. No model weights are downloaded, no neural networks are evaluated, and no inference pipelines are started.

Phase 9 defines the **declarative configuration schema, runtime boundaries, and fail-safe degradation behaviors** to prepare for Phase 10.

---

## 2. Zero-Cost, Pure Local AI Architecture

CLINOVA AI is architected to operate with **₹0 in recurring AI API fees**. Under no circumstances is an external paid API (e.g., OpenAI, Google Gemini, Anthropic, or paid cloud OCR) required for core clinical triage:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LOCAL OPEN-SOURCE AI RUNTIMES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. REASONING & EXTRACTION:  Local Qwen SLM (`qwen2.5-3b-instruct-q4`)       │
│                              Quantized GGUF running via llama.cpp on CPU.   │
│                                                                             │
│  2. SPEECH RECOGNITION:      Local `faster-whisper` (`base-int8`)           │
│                              High-speed CPU ASR for vernacular speech.      │
│                                                                             │
│  3. DOCUMENT EXTRACTION:     Local `PaddleOCR` (v4 lightweight CPU)         │
│                              Spatial bounding box extraction $[0, 1000]^2$.  │
│                                                                             │
│  4. VERNACULAR TRANSLATION:  Local `indic-trans-v2` / Deterministic Dictionaries│
│                              Odia, Hindi, and English medical term mapping. │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Safe Degradation Law: Behavior When AI is Unavailable

Machine learning runtimes running on low-cost edge Mini-PCs may experience Out-of-Memory (OOM) crashes, thermal throttling, or missing model weights.

**The Golden Law of Clinical Degradation:**
$$\mathbf{NEVER\ FAKE\ AI\ SUCCESS} \quad \wedge \quad \mathbf{CONTINUE\ DETERMINISTIC\ CARE}$$

When `AI_PROVIDER` is missing, misconfigured, or unreachable:
1. **System Enters `AI_UNAVAILABLE` State:** The backend logs an informational operational warning.
2. **Deterministic Triage Continues Uninterrupted:**
   - Vital sign recording, NEWS2 calculation, Shock Index alerting, and emergency red-flag detections continue with 100% functionality.
   - The Doctor and Nurse workbenches remain fully operational.
3. **Transparent Staff Notification:**
   - The UI displays an explicit non-blocking amber badge:  
     > ℹ️ *AI Assistant Offline — Operating on Deterministic Clinical Rules. Manual transcription/data entry enabled.*
4. **Strict Prohibition of Simulated Predictions:**
   - Under no circumstances will the system fabricate fake AI diagnoses, fake transcribed text, or hallucinated lab extractions to "simulate" operation.
   - Text boxes for transcription remain open for manual nurse/clerk typing.

---

## 4. Declarative AI Configuration Schema

```python
# AI Configuration Model
class AISettings(BaseModel):
    # Provider Mode: local_rules (default), local_qwen, hybrid, or mock
    AI_PROVIDER: AIProviderMode = Field(
        default=AIProviderMode.LOCAL_RULES,
        description="Active AI reasoning backend. Defaults to zero-cost deterministic rules.",
    )
    AI_BASE_URL: Optional[str] = Field(
        default=None,
        description="Loopback HTTP endpoint for local llama.cpp / vLLM server (e.g. http://127.0.0.1:8080/v1)",
    )
    AI_MODEL: str = Field(
        default="qwen2.5-3b-instruct-q4",
        description="Local SLM model weights tag",
    )
    WHISPER_MODEL: str = Field(
        default="base-int8",
        description="Local faster-whisper acoustic model identifier",
    )
    OCR_ENGINE: str = Field(
        default="paddleocr-v4",
        description="Local optical character recognition engine",
    )
    TRANSLATION_ENGINE: str = Field(
        default="indic-trans-v2",
        description="Local vernacular translation engine",
    )

    # Health Probe & Timeout Limits
    AI_REQUEST_TIMEOUT_SECONDS: int = Field(
        default=10,
        description="Maximum seconds to wait for edge SLM before dropping to deterministic fallback",
    )
    AI_HEALTH_PROBE_INTERVAL_SECONDS: int = Field(
        default=30,
        description="Background liveness check interval for local AI server",
    )
```

---

## 5. Invariants Enforced in AI Configuration
1. **Inv-AI-1 (Deterministic Independence):** Clinical safety scoring functions must never import or call modules from `backend/app/ai/`. They execute as standalone pure Python logic.
2. **Inv-AI-2 (Advisory Tagging):** Any output generated by an AI adapter must carry the provenance tag `epistemic_state = 'AI_INFERRED'` and require explicit RMP affirmation.
3. **Inv-AI-3 (Zero Mandatory Third-Party Keys):** The backend must successfully boot with `GEMINI_API_KEY`, `GROQ_API_KEY`, and all cloud provider keys completely empty.
