# CLINOVA AI — Model Load & Memory Lifecycle Strategy

> **Document ID:** `RES-207`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering & Performance Architecture Group  

---

## 1. Evaluation of Model Loading Strategies

| Strategy | Mechanism | Cold Latency | Active RAM Impact | Suitability for CLINOVA |
|:---|:---|:---|:---|:---|
| **Always Warm (Pre-Loaded)** | Weights mapped into RAM at system boot; keeps model resident indefinitely. | **$< 50\text{ ms}$** | Constant $\sim 2.8\text{ GB}$ held in RAM. | **RECOMMENDED FOR DEMO & CLINIC WORKSTATIONS** (zero UI lag). |
| **Lazy Loading** | Weights loaded only upon the first AI request arrival. | $3.0–8.0\text{ s}$ initial request | Zero RAM until first usage. | Acceptable for edge nodes where AI is rarely utilized. |
| **Request-Scoped (Load/Unload)**| Loads model, runs inference, immediately unloads weights. | $3.0–8.0\text{ s}$ **EVERY request** | RAM freed immediately. | **REJECTED:** Completely unviable due to unacceptable clinical UI lag. |
| **Idle Timeout Unloading** | Remains warm for 15 minutes after last request; unloads if idle. | Variable | Balanced | Secondary option for low-memory edge devices. |

---

## 2. Selected Hackathon & Edge Baseline: Persistent Warm Memory Map

For hackathon demonstrations and rural clinical workstations, CLINOVA adopts the **Persistent Warm Memory Map Strategy**:

1. **Boot-Time Background Warmup:** Upon FastAPI application startup (`@asynccontextmanager lifespan`), if `AI_PROVIDER != DISABLED`, a non-blocking background task sends a warm-up probe to Ollama / llama-server.
2. **Zero-Copy Memory Mapping (`mmap`):** The underlying C++ runtime maps GGUF weights directly from disk into virtual memory. The operating system page cache shares tensor pages without duplicating memory buffers.
3. **Keep-Alive Configuration:** Ollama is configured with `keep_alive: "24h"`, preventing the daemon from automatically evicting model weights between sporadic patient encounters.

---

## 3. Emergency Memory Recovery & Host Restart

If host telemetry detects that available system RAM drops below $10\%$ ($<800\text{ MB}$):
1. **Model Eviction:** An administrative signal (`POST /api/generate` with `keep_alive: 0`) is dispatched to release model tensor pages immediately.
2. **State Transition:** The backend transitions to `RuntimeState.MODEL_UNAVAILABLE`.
3. **Zero Host Lockup:** The operating system recovers memory, ensuring SQLite transactions and network sockets continue without encountering kernel panic or OOM killer invocation.
