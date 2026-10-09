# CLINOVA AI — Benchmark Evaluation Framework & Future Measurement Protocol

> **Document ID:** `RES-215`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Evaluation, Clinical Benchmarking & Metrics Working Group  

---

## 1. Benchmarking Philosophy & Anti-Fabrication Rule

$$\mathbf{NO\ FABRICATED\ BENCHMARK\ RESULTS\ IN\ PHASE\ 10}$$

In accordance with Phase 10 contract rules, CLINOVA strictly distinguishes between **architectural design expectations** and **empirically measured benchmarks**.

At this foundation phase, CLINOVA does not claim experimental clinical validation or publish synthetic accuracy metrics. Instead, this document establishes the **future evaluation framework, standardized metrics, and evaluation harness** to be executed once physical edge hardware is commissioned.

---

## 2. Eight Core Benchmark Evaluation Dimensions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       EIGHT EVALUATION DIMENSIONS                           │
├─────────────────────────┬───────────────────────────────────────────────────┤
│ 1. Extraction Accuracy  │ Token-level F1 and Exact Match (EM) for symptoms, │
│                         │ durations, anatomical sites, and vital numbers.   │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 2. Schema Validity      │ Percentage of model outputs adhering strictly to  │
│                         │ Pydantic JSON contracts on the first pass (0-shot)│
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 3. Source Attribution   │ Precision of `source_evidence_id` citations       │
│                         │ matching true clinician ground-truth text spans.  │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 4. Hallucination Rate   │ Frequency of ungrounded entities, fabricated      │
│                         │ numbers, or unstated clinical assertions.         │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 5. Multilingual Quality │ BLEU / chrF++ scores and colloquial preservation  │
│                         │ fidelity across Odia, Hindi, and Hinglish.        │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 6. Inference Latency    │ Time-to-First-Token (TTFT) and generation tokens/s│
│                         │ measured on target Intel Celeron & Core i5 CPUs.  │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 7. Memory Stability     │ Peak resident set size (RSS) and KV cache growth  │
│                         │ over a 24-hour continuous burn-in test.           │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 8. Failure Recovery     │ Time required to recover from simulated SIGKILL   │
│                         │ or OOM without dropping queued clinical vitals.   │
└─────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 3. Standardized Mathematical Metric Formulations

### 3.1 Extraction Precision, Recall, and F1
For clinical entities $\mathcal{E} = \{\text{symptoms}, \text{vitals}, \text{allergies}\}$:
$$\text{Precision} = \frac{|\mathcal{E}_{\text{extracted}} \cap \mathcal{E}_{\text{gold}}|}{|\mathcal{E}_{\text{extracted}}|}, \quad \text{Recall} = \frac{|\mathcal{E}_{\text{extracted}} \cap \mathcal{E}_{\text{gold}}|}{|\mathcal{E}_{\text{gold}}|}$$
$$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 3.2 Grounding Precision ($P_{\text{ground}}$)
$$P_{\text{ground}} = \frac{\sum_{i=1}^{M} \mathbf{1}_{\{\text{citation}_i \text{ is verified in Context Pack}\}}}{M}$$
Target requirement: **$100\%$ Grounding Precision** (enforced by `OutputValidator`).

### 3.3 Hallucination Rate ($H_{\text{rate}}$)
$$H_{\text{rate}} = \frac{|\mathcal{E}_{\text{extracted}} \setminus \mathcal{E}_{\text{context}}|}{|\mathcal{E}_{\text{extracted}}|}$$
Target requirement: **$0.0\%$ ungrounded entities accepted** into clinical view.

---

## 4. Benchmark Harness Execution Architecture (Future)

The benchmark harness will execute using an automated evaluation script:
1. **Curated Vignette Corpus:** 200 synthetic, clinician-annotated multi-lingual clinical transcripts representing rural, emergency, and outpatient scenarios.
2. **Deterministic Evaluation Runner:** Iterates across model checkpoints (`qwen2.5-1.5b-q4`, `qwen3-4b-q4`) on target hardware.
3. **Automated Error Logging:** Generates comprehensive CSV logs of token latency, memory consumption, and schema validation failures.
