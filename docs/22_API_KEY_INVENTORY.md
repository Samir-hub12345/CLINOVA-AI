# CLINOVA AI — API Key & Credentials Inventory

> **Document ID:** `DOC-22`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Inventory Governance & Principles

1. **₹0 Baseline Requirement:** The core application must boot, ingest multimodal data, construct CAREGRAPH, calculate care feasibility, and execute clinician reviews **with zero paid API keys**.
2. **Service Role Security Invariant:** The `SUPABASE_SERVICE_ROLE_KEY` possesses administrative bypass privileges and **must NEVER appear in client-side code**, public repositories, or frontend bundles.
3. **Pluggable Adapter Interfaces:** Optional third-party providers (remote cloud LLMs, cloud translation, commercial routing) are encapsulated behind modular provider interfaces. If an optional key is omitted, the system gracefully operates using local open-source fallbacks without throwing runtime errors.

---

## 2. Core Required Credentials (Hosted Prototype Deployment)

| Variable Name | Environment | Access Scope | Provider / Origin | Purpose | Security Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SUPABASE_URL` | Frontend & Backend | Public / Shared | Supabase Free Tier | API endpoint for hosted PostgreSQL database and Supabase Auth. | **Low Risk** (Config identifier) |
| `SUPABASE_ANON_KEY` | Frontend & Backend | Public Client | Supabase Free Tier | Client-side key for user authentication and Row Level Security (RLS) queries. | **Low / Standard** (Protected by RLS) |
| `SUPABASE_SERVICE_ROLE_KEY`| Backend ONLY | Server Process | Supabase Free Tier | Administrative database operations, system migrations, and audit logging. | **CRITICAL SECRET** (Backend only; never expose to client) |

*Note on Local Development:* For local, air-gapped development, the system can run with SQLite (`DATABASE_URL=sqlite+aiosqlite:///./clinova-dev.db`) and local JWT auth, requiring **zero external cloud credentials**.

---

## 3. Local & Open-Source Components Requiring ZERO API Keys

The following components operate completely offline and require **no API keys, subscriptions, or credit cards**:

| Subsystem | Open-Source Technology | Runtime Location | API Key Required? | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Clinical SLM Inference** | Qwen3-4B / Llama-3.2-3B | Local Ollama / vLLM / llama.cpp | **NONE (₹0)** | Free |
| **Speech-to-Text (STT)** | Whisper / faster-whisper | Local in-process Python runtime | **NONE (₹0)** | Free |
| **Lab Report OCR** | PaddleOCR / Tesseract | Local in-process Python runtime | **NONE (₹0)** | Free |
| **Vernacular Translation** | MarianMT / Clinical Synonym Map | Local Python service | **NONE (₹0)** | Free |
| **Interactive Map UI** | Leaflet.js + OpenStreetMap | Client-side browser tiles | **NONE (₹0)** | Free |
| **Geospatial Distance** | Haversine Formula | In-process Python / TypeScript | **NONE (₹0)** | Free |
| **Deterministic Risk Engine**| Python rule engine (MEWS, shock) | In-process backend service | **NONE (₹0)** | Free |

---

## 4. Optional Future Providers (Pluggable Cloud Adapters)

Optional providers may be added for benchmarking or expanded production scale, but are **never mandatory** for the baseline prototype:

| Provider Category | Optional Cloud Provider | Configuration Variable | Fallback when Key Missing |
| :--- | :--- | :--- | :--- |
| **Remote Cloud LLM** | Groq (Llama-3.3-70B) / Mistral | `OPTIONAL_LLM_API_KEY` | Falls back to local Qwen3-4B or deterministic rules |
| **Cloud Translation** | AI4Bharat / Bhashini | `OPTIONAL_TRANSLATION_API_KEY` | Falls back to local clinical synonym normalizer |
| **Cloud OCR** | OCR.Space / Azure Form | `OPTIONAL_OCR_API_KEY` | Falls back to local PaddleOCR / Tesseract |
| **Turn-by-Turn Routing** | OpenRouteService / OSRM | `OPTIONAL_ROUTING_API_KEY` | Falls back to local Haversine distance & terrain heuristic |
| **SMS / WhatsApp Alerts** | Twilio / Gupshup | `OPTIONAL_NOTIFICATION_KEY` | Falls back to in-app notification center |

---

## 5. Google Cloud & Google AI Architectural Decision

> **Explicit Decision (ADR-04):**
> Google Cloud Platform (GCP) and Google AI APIs (Gemini API, Vertex AI, Google Maps Platform) are **NOT required** for the baseline ₹0 architecture.
> 
> No mandatory Google Cloud dependencies shall be introduced in Phase 1 or the core prototype. Any potential enterprise GCP integration (e.g., BigQuery epidemiological surveillance or Cloud Healthcare API) is categorized strictly as post-hackathon enterprise roadmap infrastructure.

---

## 6. Domain Strategy

- **Hackathon Deployment:** Utilizes the free deployment subdomain provided by hosting platforms (e.g., `clinova-ai.vercel.app` or `clinova.onrender.com`).
- **Cost:** ₹0 / $0.
- **Custom Domain:** Purchasing a custom commercial domain (e.g., `.in` or `.ai`) is deferred to post-hackathon institutional deployment. Deployment is never blocked by domain acquisition.
