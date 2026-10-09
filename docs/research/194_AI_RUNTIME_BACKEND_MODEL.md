# CLINOVA AI — Local AI Runtime Backend Architecture

> **Document ID:** `RES-194`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering & Inference Infrastructure Group  

---

## 1. Executive Summary & Runtime Evaluation

The choice of inference runtime determines memory footprint, deployment friction, startup latency, and offline survivability across clinical deployment tiers.

```
================================================================================
RUNTIME BACKEND SELECTION SUMMARY
================================================================================
1. PRIMARY HACKATHON & DEMO BACKEND: Ollama
   • Simplest one-command installation, automatic model downloading, native
     cross-platform support (Windows/Linux/macOS), RESTful JSON API.
   • Endpoint: http://127.0.0.1:11434

2. LOW-SPEC RURAL EDGE (PHC) BACKEND: llama.cpp / llama-server
   • Minimal binary footprint (<50MB executable), zero daemon overhead,
     highest CPU AVX2 efficiency, direct GBNF grammar JSON enforcement.
   • Endpoint: http://127.0.0.1:8080 (or in-process bindings)

3. REJECTED BACKENDS FOR EDGE:
   • vLLM: Heavyweight Python/CUDA dependencies; requires >16GB VRAM and Linux kernel
     with modern GPU; completely unsuitable for ₹14,000 CPU Mini-PCs.
   • Hugging Face Transformers: High PyTorch memory bloat (>1.8GB Python overhead
     before loading weights); slow CPU inference without extensive ONNX tuning.
================================================================================
```

---

## 2. Comparative Runtime Backend Matrix

| Runtime Backend | Binary / Package Size | Python Dependency Overhead | CPU Optimization (AVX2/AVX-512) | GPU Acceleration Support | Structured JSON Constraint Support | Offline Installation Simplicity | Suitability for CLINOVA |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Ollama** | ~60 MB installer | None (standalone Go/C++ daemon) | Very High (embedded llama.cpp) | CUDA, ROCm, Metal, Vulkan | High (`format: "json"`) | **Very High** (single executable) | **Primary Local Dev & Demo Runtime** |
| **llama.cpp (llama-server)** | ~35 MB standalone binary | None (Pure C/C++) | **Highest** (pure assembly / AVX) | CUDA, Vulkan, OpenCL, CPU | **Exceptional** (GBNF grammars) | **Highest** (drop-in portable binary) | **Primary Edge Mini-PC Runtime** |
| **vLLM** | > 4 GB Python env | Extreme (PyTorch, Triton, Ray) | Poor (designed exclusively for GPUs) | CUDA only | Exceptional (Outlines guided decoding) | Poor (compilation required on edge) | Strictly rejected for edge; optional cloud cluster only. |
| **Hugging Face Transformers** | > 2.5 GB PyTorch env | Heavy (PyTorch, Accelerate) | Moderate (torch.compile) | CUDA, MPS | Moderate (requires external grammar) | Moderate (complex wheel dependencies) | Rejected due to high RAM overhead. |
| **CTranslate2** | ~80 MB package | Low (Python C-extension) | High (int8 quantization) | CUDA, CPU | Low (unconstrained text output) | High | Reserved for fast ASR (faster-whisper). |

---

## 3. The Three-Tier Architectural Decoupling

The clinical application domain layer must never bind directly to any specific third-party runtime library or daemon. It communicates exclusively through the decoupled adapter hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE THREE-TIER RUNTIME DECOUPLING                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: CLINICAL DOMAIN LAYER ]                                          │
│  • Master Case Lifecycle                                                    │
│  • Clinical Observation Service                                             │
│  • Deterministic Safety Engine (NEWS2, Shock Index, Red Flags)              │
│                                  │                                          │
│                                  ▼ Depends ONLY on AIAdapter Interface      │
│  [ TIER 2: HIGH-LEVEL AI ADAPTER ]                                          │
│  • AIAdapter (Abstract Base Class)                                          │
│    ├── generate_structured(task, schema, evidence)                          │
│    ├── extract_entities(narrative, evidence_id)                             │
│    ├── summarize(case_narratives)                                           │
│    └── translate(source_text, lang)                                         │
│                                  │                                          │
│                                  ▼ Communicates via RuntimeAdapter          │
│  [ TIER 3: PLUGGABLE RUNTIME ADAPTERS ]                                     │
│  • RuntimeAdapter (Abstract Base Class)                                     │
│    ├── OllamaRuntimeAdapter (HTTP 127.0.0.1:11434)                          │
│    ├── LlamaCppRuntimeAdapter (HTTP 127.0.0.1:8080)                         │
│    └── MockDeterministicAdapter (Hermetic in-memory test double)            │
│                                  │                                          │
│                                  ▼ Local IPC / Socket / Tensor Execution    │
│  [ TIER 4: LOCAL MODEL INSTANCE ]                                           │
│  • Qwen3-4B-Instruct-Q4_K_M.gguf                                            │
│  • Qwen2.5-1.5B-Instruct-Q4_K_M.gguf                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Failure Isolation & Health Probes

Every runtime implementation implements the canonical `check_health()` contract:

```python
class RuntimeState(str, Enum):
    MODEL_DISCOVERY = "MODEL_DISCOVERY"
    MODEL_LOAD = "MODEL_LOAD"
    MODEL_WARM = "MODEL_WARM"
    MODEL_READY = "MODEL_READY"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_LOAD_FAILURE = "MODEL_LOAD_FAILURE"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    TIMEOUT = "TIMEOUT"
    PROCESS_CRASH = "PROCESS_CRASH"
```

### 4.1 Fail-Safe Guarantees
1. **Daemon Crash Resilience:** If the Ollama or llama-server process terminates unexpectedly, the `AIAdapter` catches `httpx.ConnectError`, maps the condition to `RuntimeState.MODEL_UNAVAILABLE`, and routes the request to deterministic rule fallbacks without raising an unhandled 500 error to the client.
2. **Deterministic Service Continuity:** Clinical triage and vital sign entry endpoints never wait synchronously on unresponsive AI daemons. Background probes monitor health every 30 seconds.
3. **Zero Leaked Coroutines:** All network calls to local inference engines are wrapped with strict cancellation tokens and timeout bounds ($\le 5.0\text{ seconds}$).
