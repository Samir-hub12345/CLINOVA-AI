# CLINOVA AI — Zero-Cost Architecture & Technology Stack Specification

> **Document ID:** `DOC-21`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Zero-Cost Architectural Mandate

CLINOVA AI is designed to be fully operational at **₹0 / $0 infrastructure cost**, utilizing open-source engines and generous free cloud tiers.

> **Non-Negotiable Invariants:**
> 1. No paid third-party API is mandatory for any core workflow.
> 2. No Google Cloud or Google AI services (e.g., Gemini API, Vertex AI, Google Maps Platform) are required for baseline operation.
> 3. The system must remain fully functional in completely offline, on-premise, or local development environments.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA ₹0 ARCHITECTURE STACK                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTEND LAYER                                                            │
│   ├── Framework: Next.js (App Router, React 19 / Server Components)         │
│   ├── Language: TypeScript (Strict typing, zero implicit any)               │
│   ├── Styling: Tailwind CSS (Modern, clinical design tokens)                │
│   ├── Component Base: Radix UI primitives + Lucide Icons                    │
│   └── Mapping: Leaflet.js + OpenStreetMap (OSM) Tiles (Zero-cost)           │
│                                                                             │
│   BACKEND & API LAYER                                                       │
│   ├── Framework: FastAPI (Asynchronous Python 3.11+)                        │
│   ├── Data Validation: Pydantic v2 (Strict schema contracts)                │
│   ├── ASGI Server: Uvicorn                                                  │
│   └── Orchestration: Native Python Async State Machine                      │
│                                                                             │
│   PERSISTENCE, AUTH & STORAGE LAYER                                         │
│   ├── Relational DB: PostgreSQL (via Supabase Free tier or local Postgres) │
│   ├── Local Fallback: SQLite with aiosqlite for zero-install dev           │
│   ├── Authentication: Supabase Auth (Free Tier) / Local JWT tokens          │
│   └── Object Storage: Supabase Storage (Free Tier) / Local file system      │
│                                                                             │
│   LOCAL AI & MULTIMODAL INFERENCE ENGINES (100% On-Premise / Local)         │
│   ├── Clinical LLM / SLM: Local Qwen3-4B runtime (via Ollama / llama.cpp)   │
│   ├── Speech-to-Text: Local Whisper / faster-whisper                        │
│   ├── Computer Vision / OCR: Local PaddleOCR / Tesseract                    │
│   ├── Translation: Local MarianMT / IndicTrans2 / Clinical Dictionary       │
│   └── Geospatial Calculations: Local Haversine formula (Zero map API cost)  │
│                                                                             │
│   FREE DEPLOYMENT TARGETS                                                   │
│   ├── Frontend: Vercel Free Hobby Tier                                      │
│   ├── Backend: Render / Railway / Fly.io Free Tier                          │
│   └── Database: Supabase Free Tier                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Component Specifications

### 2.1 Frontend: Next.js + TypeScript
- **Framework:** Next.js 14+ with App Router.
- **Language:** TypeScript 5+ with absolute type safety across all clinical entities.
- **Styling:** Tailwind CSS with custom clinical palettes (calm slate, clinical blue, warning amber, emergency crimson).
- **Icons:** `lucide-react` (strictly no emojis as clinical icons).
- **Mapping:** `leaflet` and `react-leaflet` rendering vector tiles from OpenStreetMap.
- **State Management:** React Context + TanStack React Query for cached, reactive state updates.

### 2.2 Backend: FastAPI + Python
- **Framework:** FastAPI with asynchronous endpoint handlers.
- **Performance:** High concurrency handling multiple intake streams simultaneously.
- **Documentation:** Interactive OpenAPI / Swagger UI automatically generated at `/docs`.
- **Modularity:** Strict separation into `api/v1/endpoints/`, `services/`, `models/`, and `core/`.

### 2.3 Persistence & Authentication: PostgreSQL + Supabase Free
- **Database:** PostgreSQL 15+ hosted on Supabase Free Tier (500MB storage, 50,000 monthly active users included at $0).
- **ORM:** SQLAlchemy 2.0 with asynchronous driver (`asyncpg`).
- **Development Fallback:** Zero-config SQLite (`clinova-dev.db`) supported out-of-the-box for standalone testing without network connectivity.
- **Auth:** Supabase Auth providing secure email/password and session token management.

### 2.4 Multimodal Local Intelligence Stack
- **Local SLM:** Qwen3-4B running locally. Prompted with strict Pydantic JSON schemas and governed by deterministic medical heuristic rules.
- **Speech Ingestion:** `faster-whisper` (CTranslate2 implementation) running `base` or `small` models locally on CPU/GPU.
- **Document OCR:** `paddleocr` / `pytesseract` executing locally on uploaded prescription slips and lab images.
- **Geospatial Distance:** Local Python Haversine formula calculating exact point-to-point kilometer distances between facilities.

---

## 3. Deployment Strategy (₹0 Free Tier First)

1. **Frontend Deployment:** Deployed to Vercel Hobby Tier connecting directly to the repository's GitHub master branch. Automated CI/CD builds on push.
2. **Backend Deployment:** Deployed to Render / Railway / Fly.io Free Tier running the FastAPI container.
3. **Database Deployment:** Hosted on Supabase Free Tier.
4. **Subdomain Strategy:** Utilizes standard free deployment subdomains (e.g., `clinova-ai.vercel.app`). No purchased custom domain is required for hackathon validation.
