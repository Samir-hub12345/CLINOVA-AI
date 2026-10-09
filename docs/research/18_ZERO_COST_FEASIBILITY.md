# CLINOVA AI — Zero-Cost Architecture Feasibility Audit

> **Document ID:** `RES-18`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Audit Mandate

This audit validates the feasibility of the proposed **₹0 / $0 infrastructure architecture** for CLINOVA AI.

A core directive of Phase 2 is that **we must never recommend a service merely because it claims to have a "free tier" if usage limits, latency, or rate limits make the system unreliable or fragile during a live hackathon evaluation**.

Every layer of the stack is evaluated across nine operational criteria: licensing, hardware requirements, API key dependence, network requirements, deployment constraints, offline fallbacks, performance risks, cost risks, and hackathon viability.

---

## 2. Master Component Feasibility Evaluation

| Stack Layer & Component | Candidate Technology | Software License | Local Hardware Footprint | Mandatory API Key? | Network Connectivity Mandate | Deployment Constraints | Offline Local Fallback | Performance Risk & Latency | Cost Risk (Surprise Bills) | Hackathon Feasibility Verdict |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Clinical SLM / LLM** | **Qwen2.5-3B / Qwen3-4B** (via Ollama / llama.cpp) | Apache 2.0 (Open Weights) | 4GB–8GB RAM (CPU), ~2.5GB VRAM (GPU, Q4_K_M) | **NO.** 100% Local offline runtime. | **Zero network.** Runs completely offline. | Large container image (~4GB); free cloud VMs (Render) exceed memory limits. | Deterministic clinical heuristic rules & structured templates (`clinical-rules.md`). | Moderate on CPU (15–25 tokens/s); near-instant on local RTX GPU (60+ tokens/s). | **₹0.00 Guaranteed.** Zero API calls; impossible to incur billing. | **APPROVED (Local Dev & Demo).** Use local Ollama for demo; rule fallback for web. |
| **Speech Ingestion (STT)** | **faster-whisper** (`base` / `small` model via CTranslate2) | MIT License | ~500MB RAM (base), CPU-friendly | **NO.** Local CTranslate2 engine. | **Zero network.** Local audio inference. | Native C++ binaries required; easy to package in Python backend. | Direct keyboard text input fallback; web SpeechRecognition API. | Fast on CPU (~1.5s for 10s audio clip on modern i5/Ryzen). | **₹0.00 Guaranteed.** Completely local open-source execution. | **APPROVED.** Rock-solid local performance; zero third-party latency. |
| **Document OCR** | **PaddleOCR / pytesseract** | Apache 2.0 / Apache 2.0 | ~800MB RAM (PaddleOCR lightweight models) | **NO.** Local PyTorch / OpenCV models. | **Zero network.** Processes local image files. | Requires C++ leptonica / tesseract-ocr binaries installed on OS. | Manual parameter entry form; structured JSON lab file upload. | Fast (~1–2s per prescription slip or CBC image on CPU). | **₹0.00 Guaranteed.** Local computer vision library. | **APPROVED.** Local PaddleOCR provides high accuracy on printed Hindi/English slips. |
| **Vernacular Translation** | **IndicTrans2 / MarianMT / Clinical Lexicon** | MIT / Apache 2.0 | ~1GB RAM (IndicTrans2-distilled) | **NO.** Local neural translation or static lexicon. | **Zero network.** Offline local lookup. | Model weights require disk space (~1.5GB); dictionary is ~5MB. | Medical Terminology Synonym Dictionary (Odia/Hindi to English regex). | Instant dictionary lookup (< 5ms); neural translation (~500ms). | **₹0.00 Guaranteed.** Completely local open-source execution. | **APPROVED.** Hybrid approach: high-speed clinical dictionary + local MarianMT. |
| **Relational Database** | **PostgreSQL 15+ (Supabase Free) + SQLite** | PostgreSQL / Public Domain | < 100MB RAM (SQLite); Cloud hosted (Supabase) | Supabase Key optional (SQLite requires none). | SQLite: 0% network; Supabase: internet required. | Supabase Free tier pauses after 7 days of inactivity; 500MB storage cap. | **Zero-install SQLite (`clinova-dev.db`) via `aiosqlite`.** | Ultra-fast local SQLite (< 1ms queries); network latency on Supabase (100–300ms). | **₹0.00 Guaranteed.** SQLite has zero cost; Supabase free tier does not auto-charge. | **APPROVED.** SQLite as primary rock-solid development & demo database; Supabase for cloud preview. |
| **Authentication** | **Supabase Auth / Local JWT** | Apache 2.0 / MIT | Negligible (< 10MB) | Supabase Key (Local JWT requires none). | Local JWT: Zero network; Supabase: internet. | Supabase rate limit: 30 emails/hour on free tier (avoid email confirmation). | Local mock JWT authentication with role headers (`X-Clinova-Role`). | Sub-millisecond JWT verification locally. | **₹0.00 Guaranteed.** Local JWT is completely free. | **APPROVED.** Use local JWT / role-selector for hackathon demo to avoid Supabase auth timeouts. |
| **Object Storage** | **Local File System / Supabase Storage** | MIT / Apache 2.0 | Disk space only (local uploads folder) | Optional (Local uses standard OS filesystem). | Local: Zero network; Supabase: internet. | Supabase Free tier: 1GB storage cap. | **Local `backend/uploads/` directory with 24-hr cleanup.** | Instant local file read/write; zero cloud upload buffering. | **₹0.00 Guaranteed.** Local disk storage costs zero. | **APPROVED.** Local filesystem storage with automatic 24-hour cleanup cron script. |
| **Geospatial & Mapping** | **Leaflet.js + OpenStreetMap (OSM) Tiles** | BSD-2-Clause / ODbL (OpenStreetMap) | Client browser rendering | **NO.** OpenStreetMap public tile servers. | Internet for tile fetching (cached locally via ServiceWorker). | OSM public tile servers request fair use (no high-frequency automated scraping). | Fallback schematic coordinate grid if network tiles fail to load. | Hardware-accelerated client canvas rendering (< 16ms/frame). | **₹0.00 Guaranteed.** Completely free open-source mapping stack. | **APPROVED.** Zero dependency on Google Maps Platform or Mapbox billing keys! |
| **Geospatial Distance** | **Local Python Haversine Formula** | Public Domain / MIT | Mathematical formula (0 bytes memory) | **NO.** Pure native Python math. | **Zero network.** Calculates point-to-point distance locally. | None. Computes instantly in microseconds. | N/A (Standard trigonometry: spherical law of cosines). | Sub-microsecond calculation ($\sim 0.002$ ms). | **₹0.00 Guaranteed.** Pure mathematical calculation. | **APPROVED.** Fast, deterministic, and 100% offline. |
| **Frontend Framework** | **Next.js 14+ (React 19 / TypeScript / Tailwind)** | MIT License | Node.js runtime (Dev: ~300MB RAM) | **NO.** | Internet for initial package install; offline in dev. | Vercel Free tier has 100GB bandwidth limit (plenty for hackathon). | Local Next.js dev server on `http://localhost:3000`. | Instant hot-reloading; fast client-side navigation via App Router. | **₹0.00 Guaranteed.** Vercel Hobby Tier is free. | **APPROVED.** Standard modern frontend stack with absolute type safety. |
| **Backend Framework** | **FastAPI + Uvicorn + Pydantic v2** | MIT License | Python 3.11+ runtime (~150MB RAM) | **NO.** | Internet for pip install; offline in dev. | Render Free tier spins down after 15 mins of inactivity (50s cold start). | Local Uvicorn server on `http://localhost:8000`. | Extremely high asynchronous throughput; sub-millisecond route latency. | **₹0.00 Guaranteed.** Free open-source Python framework. | **APPROVED.** Runs locally on Windows workstation without external dependency. |

---

## 3. The Cold-Start Hazard & Hackathon Resilience Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   HACKATHON ZERO-FAILURE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HAZARD: FREE-TIER CLOUD SPIN-DOWN                                          │
│  • Free cloud providers (Render, Railway free, Fly.io free) spin containers │
│    down after 15 minutes of inactivity.                                     │
│  • If a hackathon judge opens the URL, they face a 50-second cold start     │
│    or a 504 Gateway Timeout!                                                │
│                                                                             │
│  CLINOVA RESILIENCE SOLUTION (Dual-Target Deployment):                      │
│                                                                             │
│  TARGET 1: NATIVE LOCAL WORKSTATION (PRIMARY DEMO)                          │
│  • Runs natively on Windows host (`npm run dev` + `uvicorn main:app`).     │
│  • Local SQLite database (`clinova-dev.db`).                                │
│  • Local Ollama SLM + Local faster-whisper.                                 │
│  • 100% ZERO NETWORK LATENCY. ZERO DEPENDENCY ON CLOUD APIS.                │
│                                                                             │
│  TARGET 2: VERCEL + SUPABASE CLOUD PREVIEW (SECONDARY)                     │
│  • Frontend hosted on Vercel Hobby (instant, zero cold-start).              │
│  • Backend deployed on Render with an active healthcheck ping cron.         │
│  • Deterministic fallback mode enabled so UI remains fully functional even  │
│    if cloud SLM container runs out of RAM!                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 The Anti-API Key Mandate Re-Verified
CLINOVA AI operates with **ZERO mandatory commercial API keys**:
- ❌ No OpenAI API key required.
- ❌ No Google Gemini / Vertex AI API key required.
- ❌ No Google Maps Platform API key required.
- ❌ No Anthropic API key required.
- ❌ No AWS cloud billing account required.

Every workflow executes locally via open-source engines with deterministic clinical fallbacks.

---

## 4. Audit Conclusion on Zero-Cost Feasibility

The ₹0 architecture is **100% FEASIBLE, ROBUST, AND VERIFIED**.
- Local execution on standard developer hardware (Windows 11, 16GB RAM, modern multi-core CPU) provides lightning-fast response times.
- Eliminating proprietary cloud APIs eliminates the single greatest point of failure in hackathon prototypes: rate-limit exhaustion, credit-card suspension, and cloud outage.
