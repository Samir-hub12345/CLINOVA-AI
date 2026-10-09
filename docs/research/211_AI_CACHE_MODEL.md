# CLINOVA AI — Deterministic AI Inference Caching & Invalidation Architecture

> **Document ID:** `RES-211`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering, Performance & Data Consistency Group  

---

## 1. Feasibility & Appropriateness of Caching in Clinical AI

Repeatedly running local SLM inference on resource-constrained edge hardware consumes substantial CPU cycles ($100\%$ load for 2–4 seconds). Multiple frontend tabs or re-renders viewing the same patient chart can cause redundant processing.

However, in medicine, **stale cached outputs can be fatal**:
- If an initial extraction cached "No chest pain", and 5 minutes later a nurse enters a new observation noting "Severe retrosternal chest pain", serving the cached output would obscure acute myocardial infarction.

**The Golden Law of Clinical Caching:**
Caching is permitted **ONLY IF** cryptographically bound to the exact source evidence fingerprint. Any alteration to underlying evidence MUST trigger **instant cache invalidation**.

---

## 2. Immutable Cache Key Specification

The cache key is computed as a SHA-256 hash across six immutable dimensions:

$$\mathbf{CacheKey} = \text{SHA-256}\Big(\text{case\_id} \parallel \text{task\_name} \parallel \text{prompt\_version} \parallel \text{model\_id} \parallel \text{model\_version} \parallel \mathbf{F}_{\text{evidence}}\Big)$$

Where the **Source Evidence Fingerprint** ($\mathbf{F}_{\text{evidence}}$) is deterministically generated from all input evidence items sorted by ID:

$$\mathbf{F}_{\text{evidence}} = \text{SHA-256}\Big(\text{SortedCanonicalJSON}(\{e_1, e_2, \dots, e_n\})\Big)$$

---

## 3. Cache Invalidation Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CACHE RETRIEVAL & INVALIDATION FLOW                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ INFERENCE REQUEST RECEIVED ]                                             │
│  (case_id, task="PROMPT_EXTRACTION", current_evidence_set)                  │
│          │                                                                  │
│          ▼                                                                  │
│  Compute Source Evidence Fingerprint: F_current                             │
│  Generate Cache Key: Key_lookup                                             │
│          │                                                                  │
│          ├── Cache Key Exists & TTL Valid & F_cached == F_current?          │
│          │   ├── YES ──> [ CACHE HIT ]                                      │
│          │   │           Return cached payload (status: "SUCCESS_CACHED")   │
│          │   │           Latency: < 1ms (Zero CPU Tensor Execution)         │
│          │   │                                                              │
│          │   └── NO ───> [ CACHE MISS / INVALIDATION ]                      │
│          │               • Evict stale cache entry immediately              │
│          │               • Execute local model inference on fresh evidence  │
│          │               • Validate output via OutputValidator              │
│          │               • Store validated result in cache with F_current   │
│          │                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Cache Expiration & Scope Policies

| Parameter | Policy Value | Clinical Rationale |
|:---|:---|:---|
| **Default TTL** | $3600\text{ seconds}$ ($1\text{ hour}$) | Ensures background clearance of old session data. |
| **Storage Medium**| Volatile Process Memory | Ensures no persistent unencrypted PHI left in disk caches. |
| **Case Invalidation**| `cache.invalidate_case(case_id)` | Triggered immediately on patient discharge or status change. |
| **Model Invalidation**| Full cache purge on model change | Changing model weights renders all prior caches obsolete. |
