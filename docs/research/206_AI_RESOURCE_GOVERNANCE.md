# CLINOVA AI — Edge Resource Governance & Scheduling Policy

> **Document ID:** `RES-206`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Engineering & Real-Time Edge Scheduling Group  

---

## 1. Hardware Resource Budgets

To prevent system lockups on entry-level rural hardware (₹14,000 Intel Celeron 8GB Mini-PC), CLINOVA strictly governs resource consumption:

| Resource Dimension | Edge Mini-PC Budget (8GB RAM) | Workstation Budget (16GB RAM) | Enforcement Mechanism |
|:---|:---|:---|:---|
| **Max Model RAM** | $3200\text{ MB}$ ($3.1\text{ GB}$) | $6000\text{ MB}$ ($5.8\text{ GB}$) | GGUF Q4_K_M quantization + mmap limit. |
| **Max CPU Utilization** | $50\%$ (2 out of 4 cores) | $75\%$ (6 out of 8 cores) | Process affinity (`taskset`) & thread bounds. |
| **Max VRAM (if GPU)** | $0\text{ MB}$ (CPU baseline) | $4000\text{ MB}$ (RTX 3060) | CUDA memory fraction cap ($0.8$). |
| **Max Disk for Models**| $12\text{ GB}$ total storage | $30\text{ GB}$ total storage | Prunes unreferenced GGUF checkpoints. |
| **Max Concurrency** | **1 Request** (Strictly Serial) | 2–3 Requests (FIFO Queue) | In-memory asyncio Semaphore (`max_concurrency=1`). |
| **Default Temperature**| $0.0$ (Locked) | $0.0$ (Locked) | Hardcoded in `RuntimeConfig`. |
| **Request Timeout** | $5.0\text{ seconds}$ | $5.0\text{ seconds}$ | Asyncio cancellation deadline. |

---

## 2. Real-Time Edge Scheduling Policy

Under Casualty Surge conditions (e.g. mass road traffic accident), clinical staff may submit dozens of vital signs concurrently while AI background summarization is queued.

$$\mathbf{PATIENT\ SAFETY\ OPERATIONS\ PREEMPT\ AI\ INFERENCE}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TASK PRIORITY SCHEDULING TIERS                        │
├──────────┬─────────────────────────────────────┬────────────────────────────┤
│ Priority │ Operation Class                     │ CPU & Resource Allocation  │
├──────────┼─────────────────────────────────────┼────────────────────────────┤
│ PRIORITY 1│ Real-Time Vitals Entry, NEWS2 Calc, │ Real-time immediate thread │
│ (HIGHEST)│ Shock Index, Red Flag Evaluation    │ (Zero lock contention)     │
├──────────┼─────────────────────────────────────┼────────────────────────────┤
│ PRIORITY 2│ Master Case State Transitions,      │ Immediate execution        │
│          │ SQLite WAL Writes, Audit Logging    │ (Timeout limit: 100ms)     │
├──────────┼─────────────────────────────────────┼────────────────────────────┤
│ PRIORITY 3│ Doctor Queue Prioritization & View  │ Fast query execution       │
├──────────┼─────────────────────────────────────┼────────────────────────────┤
│ PRIORITY 4│ Frontline Front-End Web Serving     │ Standard async loop        │
├──────────┼─────────────────────────────────────┼────────────────────────────┤
│ PRIORITY 5│ Local AI Inference Tasks            │ Background bounded thread  │
│ (LOWEST) │ (Extraction, Summaries, Advisory)   │ (Throttled or dropped)     │
└──────────┴─────────────────────────────────────┴────────────────────────────┘
```

---

## 3. Starvation Prevention & CPU Throttling

1. **Serial Inference Execution:** On edge nodes, `AIRuntimeService` enforces a strict semaphore limit of 1. If an extraction is running, subsequent AI tasks are placed in a FIFO queue with a maximum depth of 5.
2. **Surge Dropping:** If the queue depth exceeds 5 requests, subsequent AI advisory tasks are dropped immediately with `AI_BUSY_DEFERRED`. Frontline nurses are prompted:
   > *"AI assistant busy; please proceed with direct entry."*
3. **Core Thread Pinning:** In Linux deployments, CPU cores 0 and 1 are dedicated to the OS, SQLite WAL, and web server; cores 2 and 3 are allocated to the AI inference engine. This guarantees that an inference job running at 100% core load can never starve the database or clinical UI.
