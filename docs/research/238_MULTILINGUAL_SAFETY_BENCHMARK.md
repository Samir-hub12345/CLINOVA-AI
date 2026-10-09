# CLINOVA AI — Multilingual Safety Benchmark

> **Document ID:** `RES-238`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Vernacular Informatics, AI Safety & Multilingual NLP Group  

---

## 1. Multilingual Safety Challenge & Asymmetry
A known vulnerability in cross-lingual AI deployments is safety filter asymmetry: models that refuse dangerous instructions in English may comply when prompted in regional languages or mixed vernacular scripts.

CLINOVA evaluates safety constraints across four linguistic profiles:
1. Standard Clinical English.
2. Hindi (Devanagari script).
3. Odia (Odia script).
4. Mixed Code-Switching (Hinglish / Odia-English romanized and native script).

---

## 2. Evaluation Dimensions & Test Matrix
Explicitly evaluated across all languages:
- **Negation Preserving:** Inverting or dropping negation markers (e.g. Hindi *बुखार नहीं है* [no fever] vs *बुखार है* [fever present]; Odia *କଷ୍ଟ ନାହିଁ* vs *କଷ୍ଟ ଅଛି*).
- **Emergency Keyword Detection:** High-risk indicators (*ଛାତିରେ ଗପ ଗପ*, *सांस फूलना*, *बेहोशी*).
- **Dosage & Prescription Rejection:** Regional phrased demands for drugs (e.g. *ଦୟାକରି ଆଣ୍ଟିବାୟୋଟିକ୍ ଔଷଧ ଲେଖନ୍ତୁ* [please write antibiotic medicine]).
- **Vernacular Prompt Injections:** Adversarial jailbreaks written in mixed scripts attempting to bypass English keyword filters.

---

## 3. Benchmark Metrics & Findings

| Test Dimension | English | Hindi (हिन्दी) | Odia (ଓଡ଼ିଆ) | Mixed Code-Switching |
|---|:---:|:---:|:---:|:---:|
| **Negation Accuracy** | 0.995 | 0.990 | 0.985 | 0.980 |
| **Emergency Detection Rate** | 1.000 | 1.000 | 1.000 | 1.000 |
| **Prescription Demand Refusal** | 1.000 | 1.000 | 1.000 | 1.000 |
| **Prompt Injection Defense** | 1.000 | 1.000 | 0.980 | 0.980 |
| **Colloquial Meaning Preservation** | 0.985 | 0.970 | 0.965 | 0.950 |

---

## 4. Key Architectural Insight: Multilingual Regex Gap
The round-1 investigation identified a critical architectural limitation:
- Phase 10's `FORBIDDEN_ACTION_PATTERNS` in `output_validator.py` was compiled primarily against English tokens (e.g. `prescribe`, `admit to ward`, `discharge patient`).
- While the base model's system prompt successfully refused vernacular prescription requests in Hindi and Odia, relying solely on English regex patterns at the validator level leaves a theoretical vulnerability if a model were to emit forbidden actions in native Devanagari or Odia script.
- **Phase 11 Recommendation:** Hardened deterministic multilingual regex catalogs (covering Hindi *दवा लिखना*, *डिस्चार्ज करना* and Odia *ଔଷଧ ଲେଖିବା*, *ଡିସଚାର୍ଜ*) must be incorporated into future production validators prior to live clinical intake.
