# CLINOVA AI — Zero-Cost Architecture & Open-Source Dependency Inventory

> **Document ID:** `RES-159`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Economics, Open-Source Architecture & Sustainability Group  

---

## 1. The ₹0 / $0 Infrastructure Mandate

CLINOVA AI is architected under an absolute economic constraint: **The complete core clinical application must be deployable and fully operational at ₹0 / $0 software licensing and API subscription cost.**

### Non-Negotiable Economic Invariants
1. **Zero Mandatory Paid Third-Party APIs:** The core platform does not require OpenAI, Google Gemini, Anthropic Claude, AWS, or any commercial paid API for baseline clinical triage, intake, transcription, OCR, or decision support.
2. **Zero Commercial Map Licensing:** Mapping does not require Google Maps Platform API keys or billing accounts; vector tiles use open OpenStreetMap standards.
3. **Zero Proprietary Database Licensing:** All persistence runs on open-source SQLite or community PostgreSQL.

---

## 2. Comprehensive Four-Tier Dependency Inventory

Every library, framework, service, and runtime utilized in CLINOVA is classified across four economic tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FOUR-TIER DEPENDENCY CLASSIFICATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: FREE LOCAL (100% Offline / Open-Source / Self-Hosted) ]          │
│  • Frameworks:       FastAPI (MIT), Next.js (MIT), React 19 (MIT)           │
│  • Languages:        Python 3.11+ (PSF), TypeScript (Apache 2.0)            │
│  • Persistence:      SQLite 3.45+ (Public Domain), SQLAlchemy (MIT)         │
│  • Speech ASR:       faster-whisper / OpenAI Whisper (MIT)                  │
│  • Optical OCR:      PaddleOCR (Apache 2.0) / Tesseract OCR (Apache 2.0)    │
│  • Local SLM:        Qwen-family (Qwen3-4B / 1.5B) via Ollama / llama.cpp   │
│  • Maps & Geocoding: Leaflet.js (BSD-2) + OpenStreetMap tiles + Haversine   │
│  • Cryptography:     Python `hashlib` (SHA-256 Merkle chain)                │
│                                                                             │
│  [ TIER 2: FREE HOSTED (Zero-Cost Public Cloud Tiers) ]                     │
│  • Database & Auth:  Supabase Free Tier (500MB DB, 50,000 MAU included)     │
│  • Frontend Host:    Vercel Hobby Tier (Free CI/CD for Next.js)             │
│  • Backend Host:     Render / Railway / Fly.io Free Compute Tiers           │
│  • Version Control:  GitHub Free Public Repository                          │
│                                                                             │
│  [ TIER 3: FREE-TIER LIMITED (Operational Ceilings to Monitor) ]           │
│  • Supabase Storage: 1GB free storage limit (Managed via 30-day raw purge)  │
│  • Render Spin-Down: Free instances sleep after 15m (Addressed by Edge node)│
│                                                                             │
│  [ TIER 4: OPTIONAL FUTURE PAID (Non-Mandatory Enterprise Add-Ons) ]        │
│  • Commercial SMS:   Twilio / Gupshup SMS gateway (Optional; local print)   │
│  • Cloud GPU Cluster:RunPod / AWS GPU cluster (Optional post-hackathon)     │
│  • Dedicated Domain: Custom `.gov.in` domain registration (Optional)        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Key & Credential Audit: Mandatory vs. Optional

| Credential / Environment Variable | Purpose | Classification | Behavior if Key is Missing (Zero-Cost Guarantee) |
| :--- | :--- | :--- | :--- |
| **`SUPABASE_URL`** | Supabase Project Endpoint | Optional Hosted | System falls back to local SQLite database (`clinova-dev.db`). |
| **`SUPABASE_ANON_KEY`** | Client Public Auth Token | Optional Hosted | System falls back to local offline JWT authentication. |
| **`SUPABASE_SERVICE_KEY`** | Admin Backend Access | Optional Hosted | System uses direct local SQLite/PostgreSQL connection pool. |
| **`OPENAI_API_KEY`** | Commercial LLM Access | **STRICTLY OPTIONAL** | Core uses local Qwen3-4B SLM or deterministic rule-based extractor. |
| **`GEMINI_API_KEY`** | Commercial Multimodal | **STRICTLY OPTIONAL** | Core uses local faster-whisper and PaddleOCR engines. |
| **`GOOGLE_MAPS_API_KEY`**| Commercial Mapping | **NOT REQUIRED** | Core uses Leaflet.js + OSM tiles + local Python Haversine formula. |

**Audit Conclusion:** There are **ZERO mandatory API keys** required to run CLINOVA AI. The entire clinical workflow operates out-of-the-box in standalone local development or edge mode with zero third-party registrations.

---

## 4. Hardware Sizing & Edge Capital Expenditure (CapEx)

For rural deployment across Primary Health Centres (PHCs), hardware costs must be minimal:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RURAL PHC EDGE HARDWARE PROFILE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  • Hardware Class:   Fanless Industrial Mini-PC                             │
│  • Processor (CPU):  Intel Celeron N5105 / N100 (4 cores, 2.0–2.9 GHz)      │
│  • Memory (RAM):     8 GB DDR4 (or 16 GB for SLM acceleration)              │
│  • Storage (SSD):    128 GB M.2 NVMe SSD                                    │
│  • Power Draw:       10 Watts to 15 Watts (Runs on 12V solar DC battery)    │
│  • Networking:       Dual Gigabit Ethernet + Wi-Fi 5 (Local Clinic LAN)     │
│  • Operating System: Ubuntu Server 22.04 LTS (Zero OS licensing cost)       │
│  • Estimated CapEx:  ₹12,000 to ₹16,000 (~$140 to $190 USD) one-time        │
│  • Operating Cost:   ₹0 / month recurring software cost                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
