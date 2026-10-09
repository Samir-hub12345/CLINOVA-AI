# CLINOVA AI — AI Model Feasibility & Local Inference Research

> **Document ID:** `RES-19`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Audit Mandate

In accordance with Phase 2 contract rules, **no model training or weight fine-tuning is executed during this phase**.

This research evaluates the feasibility of open-weight Small Language Models (SLMs) and Large Language Models (LLMs)—with primary focus on the **Qwen series (Qwen2.5 / Qwen3)**, **Llama 3.2**, and open biomedical models—for local on-premise clinical inference under zero-cost constraints.

The objective is to establish:
1. The optimal local development model.
2. The optimal lightweight deployment model.
3. The exact partition between LLM generative tasks and deterministic rule tasks.
4. What clinical decisions must **NEVER** depend exclusively on an LLM.
5. The dataset requirements for future Phase 3/4 LoRA fine-tuning.

---

## 2. Model Family Comparative Evaluation

| Model Candidate | Parameter Count | Quantization (GGUF) | RAM / VRAM Footprint | License | Multilingual Indic Support (Hindi/Odia) | Structured JSON Output Fidelity | CPU Inference Speed (tokens/s) | GPU Inference Speed (tokens/s) | Recommended Role in CLINOVA |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Qwen2.5-0.5B-Instruct** | 0.5 Billion | Q4_K_M | ~450MB RAM | Apache 2.0 | Moderate (basic Hindi) | Moderate (simple schemas) | 45–65 t/s | 120+ t/s | Extreme lightweight edge testing only; prone to subtle clinical entity omissions. |
| **Qwen2.5-1.5B-Instruct** | 1.5 Billion | Q4_K_M | ~1.2GB RAM | Apache 2.0 | Good (Hindi, basic Odia) | High (strict JSON mode) | 30–45 t/s | 95+ t/s | **Best Ultra-Lightweight Deployment Model** (suitable for 8GB RAM laptops). |
| **Qwen2.5-3B-Instruct** | 3.1 Billion | Q4_K_M | ~2.2GB RAM | Qwen Research License | Very Good (Hindi, Odia script) | Very High (Pydantic schemas) | 20–32 t/s | 75+ t/s | Strong candidate, but licensing requires review for commercial use. |
| **Qwen3-4B-Instruct** | 4.0 Billion | Q4_K_M | ~2.8GB RAM | Apache 2.0 | Excellent (High Indic benchmark) | **Exceptional (Grammar-guided JSON)** | 18–28 t/s | 65+ t/s | **PRIMARY RECOMMENDED LOCAL BASE MODEL** (optimal balance of reasoning & speed). |
| **Qwen2.5-7B-Instruct** | 7.6 Billion | Q4_K_M | ~4.8GB RAM / 6GB VRAM | Apache 2.0 | Excellent | Exceptional | 8–14 t/s | 45+ t/s | High reasoning fidelity; however, CPU inference latency (> 5s) creates UI lag without GPU. |
| **Llama-3.2-3B-Instruct** | 3.2 Billion | Q4_K_M | ~2.3GB RAM | Llama 3.2 Community License | Moderate (English-biased; weak Odia) | High | 22–35 t/s | 80+ t/s | Secondary backup; inferior to Qwen on Indic regional dialect normalization. |
| **BioMistral-7B** | 7.2 Billion | Q4_K_M | ~4.6GB RAM | Apache 2.0 | English-focused | Moderate | 9–15 t/s | 40+ t/s | Strong biomedical knowledge; poor Indic vernacular translation support. |

---

## 3. The Division of Labor: LLM vs Deterministic Rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CLINICAL INTELLIGENCE DIVISION OF LABOR                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ WHAT THE LOCAL LLM HANDLES ]                                             │
│  ✅ Parsing messy, unstructured colloquial narratives                        │
│  ✅ Translating regional expressions (e.g., "chhati re gapa gapa laguchi")   │
│  ✅ Normalizing colloquial phrases to standardized clinical concepts        │
│  ✅ Synthesizing chronological progress notes from discrete timeline nodes  │
│  ✅ Formulating natural-language patient-friendly clarification questions    │
│                                                                             │
│  [ WHAT DETERMINISTIC RULES HANDLE ]                                        │
│  ⚙️ NEWS2 and MEWS physiological score calculation                          │
│  ⚙️ Shock Index computation ($\text{Heart Rate} / \text{Systolic BP}$)      │
│  ⚙️ Deterministic Red-Flag Triggers (`TRIAGE-R01` to `TRIAGE-R06`)         │
│  ⚙️ Missing-Data Protocol Checklist validation (`SYNDROME_PROTOCOLS`)        │
│  ⚙️ Mathematical Uncertainty Score ($U_t$) computation                      │
│  ⚙️ Facility capability prerequisite boolean evaluation                      │
│  ⚙️ Haversine distance and transit time calculations                         │
│                                                                             │
│  [ WHAT MUST NEVER DEPEND EXCLUSIVELY ON AN LLM ]                           │
│  🚫 Triage Urgency Level (Emergency Red vs Routine Green)                   │
│  🚫 Immediate Emergency Bedside Escalation alerts                           │
│  🚫 Medication dosage or prescription generation                            │
│  🚫 Autonomous patient admission or hospital discharge                     │
│  🚫 Overriding a human doctor's clinical modification                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Why Deterministic Rules Must Govern Triage
Generative language models are probabilistic text predictors. Even with temperature set to $0.0$, a slight phrasing variation in a prompt can alter an LLM's classification from "Immediate Resuscitation" to "Urgent Assessment."

In clinical medicine, **a 1% probabilistic failure rate on an acute myocardial infarction is fatal**. Therefore, CLINOVA enforces the **Anti-Hallucination Safety Rule**:
$$\mathbf{RiskBand} = \max\Big(\mathbf{NEWS2\_Score},\ \mathbf{Deterministic\_Red\_Flags},\ \mathbf{LLM\_Inferred\_Urgency}\Big)$$

If the patient has a Systolic BP $< 90$ mmHg or SpO2 $< 90\%$, the deterministic red-flag rule (`TRIAGE-R01`) automatically triggers `EMERGENCY_RED` regardless of what the LLM generates.

---

## 4. Local Inference Runtime Architecture

For the native Windows workstation prototype, local inference is structured as follows:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LOCAL INFERENCE RUNTIME STACK                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CLIENT / BROWSER ] ──> Next.js App Router                                │
│          │                                                                  │
│          ▼ HTTP (JSON Schemas)                                              │
│  [ FASTAPI BACKEND ] ──> Pydantic v2 Strict Validation Models               │
│          │                                                                  │
│          ├── 1. Check Offline Heuristic Rules (Instant: < 2ms)              │
│          │                                                                  │
│          └── 2. Query Local SLM Engine:                                     │
│                 ├── Primary: Ollama Local Daemon (`localhost:11434`)        │
│                 │   Model: `qwen2.5:3b` or `qwen3:4b` (GGUF Q4_K_M)         │
│                 │   Latency: ~800ms on GPU / ~2.5s on CPU                   │
│                 │                                                           │
│                 └── Fallback: In-Process CTranslate2 / llama-cpp-python     │
│                     (Activates if Ollama service is stopped)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Future Model Fine-Tuning Roadmap (Post-Hackathon Phase 3/4)

Model training does not occur in Phase 2. However, the data requirements for future adaptation are established here:

1. **Target Architecture:** Parameter-Efficient Fine-Tuning (PEFT) using **LoRA (Low-Rank Adaptation)** with rank $r=16$, $\alpha=32$ on the attention projection layers (`q_proj`, `v_proj`).
2. **Dataset Composition:**
   - 5,000 synthetic multi-lingual clinical intake dialogues (Odia, Hindi, colloquial English).
   - 2,500 paired clinical entity extraction annotations mapped to SNOMED-CT / ICD-11.
   - 1,000 clinical question-generation vignettes trained on Value-of-Information gap closure.
3. **Safety Benchmarking:** Every fine-tuned checkpoint must be audited against the **MedAbstain** benchmark to verify that the model's ability to abstain under uncertainty does not degrade.
