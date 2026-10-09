# CLINOVA AI — AI Adapter Boundary & Model Decoupling Architecture

> **Document ID:** `RES-144`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering, Clinical Safety & NLP Architecture Group  

---

## 1. The Adapter Pattern & Decoupling Mandate

CLINOVA AI treats all Artificial Intelligence and Large/Small Language Model (LLM/SLM) runtimes as **untrusted, external perceptual adapters**.

### The Anti-Single-Point-of-Failure Law
**The core clinical application must remain 100% operational if every AI model is disabled, crashed, or absent.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AI ADAPTER ARCHITECTURAL BOUNDARY                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ DOMAIN SERVICES (FastAPI Modular Monolith) ]                             │
│  ├── Master Case Lifecycle & State Machine                                  │
│  ├── Deterministic Clinical Safety Engine (NEWS2, Shock Index, Red Flags)   │
│  ├── Doctor Queue Prioritization                                            │
│  └── Provenance & Audit Chains                                              │
│                                  │                                          │
│                                  │ Abstract Interface: `AIAdapter`          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │                     AI ADAPTER LAYER                    │                │
│  ├─────────────────────────────────────────────────────────┤                │
│  │  Local SLM Runtime      Speech-to-Text    Vision OCR    │                │
│  │  (Qwen3-4B via Ollama/  (faster-whisper)  (PaddleOCR /  │                │
│  │   llama.cpp REST)                         Tesseract)    │                │
│  └─────────────────────────────────────────────────────────┘                │
│                                  │                                          │
│                                  ▼ (Strict Fallback on Timeout / Error)     │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │              DETERMINISTIC FALLBACK ENGINE              │                │
│  ├─────────────────────────────────────────────────────────┤                │
│  │  • Regex entity extraction & keyword dictionary matching │                │
│  │  • Deterministic template-based clinical note synthesis │                │
│  │  • Standard clinical gap checklists                     │                │
│  └─────────────────────────────────────────────────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Permitted vs. Strictly Forbidden AI Scope

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI RESPONSIBILITY MATRIX                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT AI IS PERMITTED TO DO               WHAT AI MUST NEVER BE AUTHORITATIVE│
│   (Advisory / Structuring Support)         FOR (Enforced Deterministically) │
│   ──────────────────────────────────       ───────────────────────────────  │
│   ✅ Extract entities from text narrative   ❌ Deterministic early warning    │
│   ✅ Normalize vernacular terms to LOINC   ❌ NEWS2 score calculation        │
│   ✅ Transcribe audio speech waveforms     ❌ Shock Index evaluation         │
│   ✅ Recognize printed OCR characters       ❌ Clinical Red Flag alerts       │
│   ✅ Draft summary notes for physician     ❌ Patient state transitions      │
│   ✅ Translate Odia/Hindi to English       ❌ Clinical disposition decisions │
│   ✅ Suggest 1–3 candidate NBI questions   ❌ Inpatient hospital admissions  │
│   ✅ Propose candidate clinical actions    ❌ Patient discharges             │
│                                            ❌ Drug prescriptions / dosages   │
│                                            ❌ Autonomous self-verification   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Complete AI Lifecycle Pipeline

Every interaction with an AI component follows an immutable five-stage lifecycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE CANONICAL AI LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. AI_REQUEST                                                              │
│     • Formatted with strict JSON schema instructions                        │
│     • Bounded timeout: 3000ms for SLM extraction; 8000ms for OCR/ASR        │
│                                                                             │
│  2. AI_RESPONSE                                                             │
│     • Raw text output received from local inference engine                  │
│                                                                             │
│  3. VALIDATION                                                              │
│     • Pydantic schema validation parses structured output                   │
│     • Physiological range boundary check (e.g. Reject SBP = 850 mmHg)       │
│     • If validation fails => Fall back to raw text preservation             │
│                                                                             │
│  4. PROVENANCE BINDING                                                      │
│     • Output permanently tagged with source: `AI_INFERRED`                  │
│     • Calibrated model confidence score C in [0.0, 1.0] recorded            │
│     • Direct pointer to model name, checkpoint hash, and prompt version     │
│                                                                             │
│  5. HUMAN REVIEW & DISPOSITION                                              │
│     • Displayed on Doctor Workbench with visual advisory badge              │
│     • RMP exercises sole authority: ACCEPT, MODIFY, or REJECT               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Abstract AI Adapter Interface Definition

The Python domain layer interacts exclusively with the abstract `AIAdapter` interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ClinicalExtractionResult(BaseModel):
    extracted_entities: Dict[str, Any]
    confidence_score: float
    model_identifier: str
    is_fallback: bool = False

class AIAdapter(ABC):
    """Abstract interface isolating AI runtimes from clinical core."""
    
    @abstractmethod
    async def extract_narrative_entities(
        self, narrative_text: str, language: str
    ) -> ClinicalExtractionResult:
        """Extract clinical symptoms, duration, and qualifiers from text."""
        pass
        
    @abstractmethod
    async def transcribe_speech(
        self, audio_bytes: bytes, language: str
    ) -> Dict[str, Any]:
        """Convert vernacular audio to text with word-level timecodes."""
        pass
        
    @abstractmethod
    async def extract_document_ocr(
        self, document_bytes: bytes
    ) -> Dict[str, Any]:
        """Extract text and 2D spatial bounding boxes from document scans."""
        pass
```

### Deterministic Fallback Implementation
If `LocalOllamaSLMAdapter.extract_narrative_entities` raises a `TimeoutError` or network error:
1. The exception is caught within the adapter layer.
2. `DeterministicFallbackExtractor` executes instantly:
   - Matches symptom keywords against a curated multilingual medical dictionary (`dictionary_symptoms.json`).
   - Extracts numeric qualifiers via regex (`r"(\d+)\s*(days?|hours?|months?)"`).
3. Returns `ClinicalExtractionResult` with `is_fallback: True`, `confidence_score: 0.50`, and `model_identifier: "RULE_BASED_HEURISTIC"`.
4. The clinical intake workflow completes without interruption.
