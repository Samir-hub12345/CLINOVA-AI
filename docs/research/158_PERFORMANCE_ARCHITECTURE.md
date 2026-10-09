# CLINOVA AI — Performance Engineering & Latency Architecture

> **Document ID:** `RES-158`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Performance, Distributed Architecture & Edge Optimization Group  

---

## 1. Architectural Discipline: Design Targets vs. Measured Results

In software architecture documentation, teams frequently claim that their system *"runs in 12ms"* before the code has even been profiled on real target hardware.

**The Architectural Honesty Mandate:**
$$\mathbf{DESIGN\ TARGET} \quad \neq \quad \mathbf{MEASURED\ RESULT}$$

1. **Design Target:** The theoretical latency, throughput, and memory ceilings that the technical architecture is mathematically designed and bounded to achieve.
2. **Measured Result:** Empirical data gathered through reproducible load testing, benchmarking harnesses, and hardware telemetry.

In Phase 8, all figures are explicitly designated as **Design Targets**. Phase 9 and subsequent implementation phases will profile and record actual **Measured Results** against these engineering targets.

---

## 2. Explicit Engineering Latency & Throughput Targets

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LATENCY DESIGN TARGET MATRIX                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ FRONTEND RENDERING TARGETS ]                                             │
│  • Initial Application Shell Load:       < 1.50 s  (Design Target)          │
│  • Triage Form Client Transition:        < 150 ms  (Design Target)          │
│  • Doctor Workbench Case Hydration:      < 300 ms  (Design Target)          │
│  • Side-by-Side Crop Viewer Display:     < 100 ms  (Design Target)          │
│                                                                             │
│  [ BACKEND CORE API TARGETS ]                                               │
│  • Health Probe (`GET /health`):         < 20 ms   (Design Target)          │
│  • Vitals Intake & NEWS2 Scoring:        < 50 ms   (Design Target)          │
│  • Active Doctor Queue Evaluation:       < 200 ms  (Design Target)          │
│  • Merkle Audit Append & Chain Hash:     < 30 ms   (Design Target)          │
│                                                                             │
│  [ PERCEPTUAL MULTIMODAL PROCESSING TARGETS (CPU Edge) ]                    │
│  • PaddleOCR Document Extraction (1-page):< 5.00 s  (Design Target, 4-core) │
│  • faster-whisper Speech ASR (30s audio):< 4.00 s  (Design Target, CPU int8)│
│  • Local SLM Narrative Extraction:       < 3.00 s  (Design Target, Qwen3-4B)│
│                                                                             │
│  [ SYNCHRONIZATION & STORAGE TARGETS ]                                      │
│  • Local SQLite WAL Write Transaction:   < 5 ms    (Design Target)          │
│  • Sync Journal Batch Push (50 events):  < 1.00 s  (Design Target, 100kbps) │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Edge Hardware Sizing & Resource Ceilings

To ensure reliable deployment on low-cost hardware in rural facilities, the technical architecture is bounded within strict memory and compute budgets:

| Deployment Component | Minimum CPU Allocation | Target Memory Ceiling (RAM) | Storage Footprint | Thermal & Power Budget |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI Backend Core** | 1 Core (x86_64 / ARM64) | $\le 250\text{ MB}$ | $\sim 150\text{ MB}$ (Python venv) | Fanless 10–15W TDP |
| **SQLite WAL Engine** | Shared (I/O bounded) | $\le 64\text{ MB}$ (Page cache) | $< 50\text{ MB}$ (10,000 cases) | Native disk I/O |
| **Next.js Frontend Shell** | Client Tablet CPU | $\le 120\text{ MB}$ (Browser tab) | $\sim 25\text{ MB}$ (Static bundle) | Mobile tablet battery |
| **faster-whisper (tiny/base)**| 2 Cores (AVX2 enabled) | $\le 500\text{ MB}$ | $\sim 300\text{ MB}$ (Weights) | CPU burst load |
| **PaddleOCR Engine** | 2 Cores | $\le 450\text{ MB}$ | $\sim 200\text{ MB}$ (Weights) | CPU burst load |
| **Local SLM (Qwen3-4B int4)**| 4 Cores (Optional SLM) | $\le 2.80\text{ GB}$ | $\sim 2.50\text{ GB}$ (GGUF weights)| Optional accelerator |
| **TOTAL LOCAL EDGE NODE** | **4-Core Mini-PC** | **$\le 4.50\text{ GB}$ / 8GB RAM** | **$\le 5.0\text{ GB}$ / 128GB SSD**| **Standard 12V DC UPS** |

---

## 4. Architectural Bottleneck Mitigations

1. **SQLite WAL Thread Lock Mitigation:**
   - Problem: Heavy concurrent disk writes during audio recording chunk uploads can trigger `SQLITE_BUSY` errors.
   - Mitigation: Raw binary audio files are written directly to the filesystem outside of the database; SQLite records only lightweight text metadata in rapid $< 5\text{ms}$ transactions. Connection pool sets `busy_timeout = 5000ms`.
2. **Dynamic Queue Query Mitigation:**
   - Problem: As the cumulative database grows to tens of thousands of historical cases, calculating queue wait times over the whole table would degrade query performance.
   - Mitigation: The query evaluates exclusively over a partial index filtered on `status = 'STATE_DOCTOR_QUEUED'`, bounding the scanned set to active waiting patients (typically $< 100$ rows) and guaranteeing sub-50ms execution.
3. **Perceptual Pipeline Asynchrony:**
   - Problem: Long-running OCR and ASR jobs blocking HTTP worker threads.
   - Mitigation: Requests return HTTP 202 Accepted immediately; processing executes in non-blocking background task pools.
