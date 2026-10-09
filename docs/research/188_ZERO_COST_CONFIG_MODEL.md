# CLINOVA AI — Zero-Cost Architecture Audit & Dependency Economic Model

> **Document ID:** `RES-188`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Health Economics, Open Source Governance & Software Architecture Group  

---

## 1. The ₹0 Zero-Cost Core Mandate

A pervasive failure mode in global digital health deployments is introducing enterprise cloud software with recurring per-API or per-token fees (e.g., OpenAI API tokens, Google Maps geocoding charges, proprietary speech-to-text subscriptions). When donor or pilot grant funding expires, public health systems are forced to shut down the software due to unsustainable recurring OpEx.

**The Inviolable Zero-Cost Law:**
$$\mathbf{Core\ Clinical\ Triage\ OpEx} = \mathbf{₹0.00\ /\ Month}$$

CLINOVA AI must remain **100% operational in perpetuity** without requiring a single paid software license, cloud API token, or third-party subscription.

---

## 2. Four-Tier Economic Taxonomy

Every dependency, library, driver, and external asset in CLINOVA AI is categorized into four strict economic tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FOUR-TIER DEPENDENCY TAXONOMY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: FREE LOCAL (100% Open Source / On-Premise) ]                     │
│  ├── Executes entirely on local hardware (Mini-PC or Hospital Server).      │
│  ├── Zero network egress, zero recurring licensing fees, zero token meters.  │
│  └── Examples: FastAPI, SQLite, Next.js, Qwen SLM, faster-whisper, PaddleOCR│
│                                                                             │
│  [ TIER 2: FREE HOSTED (Public Domain / Open Data Infrastructure) ]         │
│  ├── Community-maintained public infrastructure with ₹0 access fees.        │
│  └── Examples: OpenStreetMap vector tiles, WHO/IPHS public clinical tables. │
│                                                                             │
│  [ TIER 3: FREE-TIER LIMITED (Optional Cloud Development Sandboxes) ]       │
│  ├── Zero-cost free developer tiers used strictly for cloud evaluation.     │
│  └── Examples: Supabase Free Tier, Vercel Hobby Tier, GitHub Free Actions.  │
│                                                                             │
│  [ TIER 4: OPTIONAL FUTURE PAID (Pluggable Commercial Endpoints) ]          │
│  ├── Proprietary cloud endpoints that may optionally be connected later.    │
│  ├── STRICT LAW: NEVER MANDATORY FOR CORE TRIAGE OR SAFETY.                 │
│  └── Examples: Commercial Gemini 1.5 Pro, Azure Health Bot, OpenAI GPT-4o.  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Dependency Audit Matrix

| System Component | Selected Technology | Economic Classification | Upstream License | Recurring Cost | Mandatory API Key? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Application Backend** | FastAPI (Python 3.11) | `FREE_LOCAL` | MIT | **₹0.00** | **NO** |
| **Frontend Framework** | Next.js 15+ (React 19) | `FREE_LOCAL` | MIT | **₹0.00** | **NO** |
| **Styling & Design** | Plain CSS Modules + Vars | `FREE_LOCAL` | W3C Standard | **₹0.00** | **NO** |
| **Edge Database** | SQLite 3.45+ (WAL mode) | `FREE_LOCAL` | Public Domain | **₹0.00** | **NO** |
| **Hospital Database** | PostgreSQL 15+ | `FREE_LOCAL` | PostgreSQL Open | **₹0.00** | **NO** |
| **Local Reasoning SLM**| Qwen2.5-3B-Instruct (GGUF)| `FREE_LOCAL` | Apache 2.0 | **₹0.00** | **NO** |
| **Local Speech Engine**| `faster-whisper` (int8) | `FREE_LOCAL` | MIT | **₹0.00** | **NO** |
| **Local Document OCR** | `PaddleOCR` (v4 CPU) | `FREE_LOCAL` | Apache 2.0 | **₹0.00** | **NO** |
| **Vernacular Translation**| `indic-trans-v2` / Rules | `FREE_LOCAL` | MIT / Apache | **₹0.00** | **NO** |
| **Facility Mapping** | Leaflet + OpenStreetMap | `FREE_HOSTED` | BSD-2 / ODbL | **₹0.00** | **NO** |
| **Iconography** | `lucide-react` | `FREE_LOCAL` | ISC | **₹0.00** | **NO** |
| **Cloud Persistence** | Supabase (Free Tier) | `FREE_TIER_LIMITED`| Apache 2.0 / Free| **₹0.00** (Sandbox)| **NO** (Only in Cloud) |
| **Commercial AI (Opt.)**| Gemini / Groq / Sarvam | `OPTIONAL_FUTURE_PAID`| Commercial | Variable | **NO (100% Optional)** |

---

## 4. Invariants Enforced in Zero-Cost Model
1. **Inv-COST-1 (Zero Paywall Triage):** The complete patient journey (registration, vitals, triage scoring, queueing, doctor verification, prescription sign-off) executes 100% without entering any credit card or commercial API token.
2. **Inv-COST-2 (Free-Tier Resiliency):** In `CLOUD_PREVIEW`, if the Supabase Free Tier monthly quota is exhausted, the application gracefully degrades to local SQLite storage without crashing.
3. **Inv-COST-3 (Zero Proprietary Map Lock-In):** Facility navigation and referral routes use Leaflet with OpenStreetMap tiles; Google Maps Platform APIs are strictly optional and not required.
