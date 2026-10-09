# CLINOVA AI — Zero-Cost Architecture & Economic Tier Audit

> **Document ID:** `RES-217`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Health Economics & Open-Source Infrastructure Group  

---

## 1. Statutory Mandate & Economic Feasibility

In public healthcare infrastructure across India, recurring operational software fees (e.g. $0.02 per 1,000 tokens for commercial LLMs or \$500/month cloud SaaS subscriptions) are completely unsustainable for rural Primary Health Centres (PHCs) and Community Health Centres (CHCs).

**The Zero-Cost Core Mandate:**
Core clinical triage, emergency red-flag alerting, speech recognition, entity extraction, and doctor queue management MUST operate at **₹0 / month in mandatory recurring software licensing or API fees**.

---

## 2. Dependency Classification across Four Economic Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 FOUR-TIER ECONOMIC CLASSIFICATION MATRIX                    │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ Economic Tier        │ CLINOVA Component    │ Licensing & Cost Model        │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 1. FREE LOCAL        │ Qwen3-4B / Qwen2.5   │ Apache 2.0 (Open-weights)     │
│    (Core Baseline)   │ llama.cpp / Ollama   │ MIT / Apache 2.0 (Free binary)│
│                      │ SQLite 3.45+ (WAL)   │ Public Domain (Zero cost)     │
│                      │ Python / FastAPI     │ MIT / BSD (Zero cost)         │
│                      │ faster-whisper (CPU) │ MIT (Open-source weights)     │
│                      │ PaddleOCR (v4 CPU)   │ Apache 2.0 (Open-source)      │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 2. FREE HOSTED       │ Supabase Community   │ Managed Free Tier for demo &  │
│    (Preview Only)    │ Cloud (Cloud Preview)│ non-production staging.       │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 3. FREE-TIER LIMITED │ GitHub Actions CI/CD │ Free open-source compute mins │
│    (Development)     │ Hugging Face Hub     │ Free public checkpoint storage│
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ 4. OPTIONAL FUTURE   │ Dedicated Centralized│ Optional district hospital    │
│    PAID (Non-Core)   │ GPU Inference Cluster│ enterprise scaling; NEVER     │
│                      │ (e.g. AWS / GCP GPU) │ required for local clinic core│
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

---

## 3. Total Cost of Ownership (TCO) Audit

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                MONTHLY RECURRING OPERATIONAL EXPENDITURE (OpEx)             │
├────────────────────────────────────────┬────────────────────────────────────┤
│ Item / Service                         │ Monthly Recurring Cost (INR)       │
├────────────────────────────────────────┼────────────────────────────────────┤
│ Operating System (Debian Linux)        │ ₹0.00                              │
│ Local Database (SQLite WAL)            │ ₹0.00                              │
│ Application Server (FastAPI / Uvicorn) │ ₹0.00                              │
│ AI Inference Engine (llama.cpp/Ollama) │ ₹0.00                              │
│ Base Model Weights (Qwen Open Weights) │ ₹0.00                              │
│ External AI API Calls (OpenAI/Gemini)  │ ₹0.00 (Zero Mandatory APIs)       │
│ Cloud Hosting Fees (Edge Deployment)   │ ₹0.00 (Local on-premise hardware)  │
├────────────────────────────────────────┼────────────────────────────────────┤
│ TOTAL MANDATORY SOFTWARE OPEX          │ ₹0.00 / month                      │
└────────────────────────────────────────┴────────────────────────────────────┘
```

---

## 4. Absolute Freedom from Commercial AI Vendor Lock-In

1. **No Mandatory Google AI Dependency:** Zero requirement for Google Gemini, Vertex AI, or Google Cloud APIs.
2. **No Mandatory OpenAI Dependency:** Zero requirement for GPT-4, Whisper API, or Azure OpenAI services.
3. **Hardware Agnostic:** Runs identically on x86_64 Intel/AMD CPUs, ARM64 processors, or local consumer GPUs without closed-source proprietary runtimes.
