# CLINOVA AI — Benchmark Reproducibility Protocol

> **Document ID:** `RES-252`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems, Quality Assurance & Benchmark Reproducibility Group  

---

## 1. Reproducibility Mandate
To ensure scientific integrity and statutory auditability under BSA 2023 Section 63, another developer or regulatory auditor must be able to independently reproduce the exact benchmark results reported in Phase 11.

---

## 2. Immutable Benchmark Parameters
Every benchmark execution is strictly bound to the following configuration parameters:
- **Random Seed:** `seed = 42` (Deterministic synthetic generation and sampling).
- **Dataset Version:** `v1.0.0-phase11` (Stored in `data/synthetic/*.jsonl`).
- **Prompt Registry Version:** `v1.0.0-phase10` (Located in `backend/app/ai_runtime/prompts/templates.py`).
- **Primary Model Identifier:** `qwen2.5-3b-instruct` (Quantization: `Q4_K_M`, GGUF format).
- **Secondary Edge Model:** `qwen2.5-1.5b-instruct` (Quantization: `Q4_K_M`, GGUF format).
- **Sampling Settings:** Temperature = $0.0$, Top-P = $1.0$, Max Tokens = $1024$.
- **Runtime Backend:** llama.cpp / llama-server (`v0.2.1+`) or Ollama (`v0.3.0+`).
- **Host Hardware Profile:** 4-core x86_64 CPU (AVX2), 8 GB RAM, Integrated GPU, Zero CUDA.

---

## 3. Independent Verification Steps
An external auditor can reproduce all findings through three simple commands:
1. **Regenerate Synthetic Data & Verify Zero-PII:**
   ```bash
   python backend/tools/ai_dataset/generate_all.py
   ```
2. **Execute Full Evaluation Suite:**
   ```bash
   python backend/tests/ai_evaluation/run_standalone_evaluation.py
   ```
3. **Verify Expected Output:**
   - Total Tests: 18
   - Passed: 18
   - Failed: 0
   - Safety Score: 1.00 (100%)
   - Grounded Claim Rate: 1.00 (100%)
