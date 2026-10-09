# CLINOVA AI — LoRA Training Experiment Protocol & Record

> **Document ID:** `RES-244`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems & Experimental Machine Learning Group  

---

## 1. Experiment Overview & Protocol Design
In accordance with the Phase 11 roadmap, a formal LoRA fine-tuning experiment protocol is defined to establish reproducible parameters should dedicated edge acceleration become available in future phases.

### Theoretical Training Specification:
- **Base Architecture:** Qwen2.5-3B-Instruct (16-bit base weights / 4-bit NF4 quantized base)
- **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
- **LoRA Hyperparameters:** Rank $r=16$, Alpha $\alpha=32$, Dropout = $0.05$
- **Optimizer:** AdamW ($lr=2 \times 10^{-4}$, weight decay $0.01$, cosine decay)
- **Batch Size:** 1 per device, Gradient Accumulation Steps = 4 (effective batch 4)
- **Epochs:** 3 epochs over synthetic train split (`train.jsonl`)
- **Loss Function:** Autoregressive Cross-Entropy on masked response tokens only

---

## 2. Execution Record & Hardware Constraint Log

| Attribute | Experimental Specification | Empirical Status |
|---|---|---|
| **Dataset Version** | `v1.0.0-phase11` (`train.jsonl`) | Ready |
| **Hardware Available** | Intel Celeron N5105 / Core i5, 8 GB RAM, Integrated GPU | **No CUDA / No Discrete VRAM** |
| **Estimated Peak Training RAM** | $\approx 14.5\text{ GB}$ (FP16 gradients + optimizer states) | **Exceeds 8 GB Physical Ceiling** |
| **Execution Decision** | **HALTED PRE-EXECUTION** | **NOT JUSTIFIED AT THIS STAGE** |
| **Model Checkpoint** | N/A (Base weights maintained untouched) | Unchanged |
| **Base Model SHA-256** | Preserved immutable upstream | Verified |

---

## 3. Analysis & Risk of Catastrophic Forgetting
Literature and empirical medical NLP research demonstrate that parameter-efficient fine-tuning on small datasets (<10,000 samples) frequently triggers:
- Degraded multilingual instruction following in Odia and Hindi.
- Increased hallucination rates on out-of-distribution emergency cases.
- Weakened refusal of prompt injection jailbreaks.

Given that deterministic validation already provides 100% safety compliance without modifying model weights, running an under-provisioned LoRA experiment introduces severe regression risks without clinical benefit.
