# CLINOVA AI — Phase 10 Authoritative Sources & Statutory References

> **Document ID:** `SOURCES-PHASE-10`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Safety Informatics & Regulatory Compliance Group  

---

## 1. Statutory Indian Legal & Regulatory Frameworks

1. **National Medical Commission (NMC) Registered Medical Practitioner Regulations, 2023:**
   - *Regulations 27 & 28:* Establishing physician monopoly over clinical diagnosis, medical prescriptions, surgical authorizations, and hospital admissions/discharges. Formally cited as the statutory basis for prohibiting autonomous AI clinical decisions.
2. **Bharatiya Sakshya Adhiniyam (BSA), 2023:**
   - *Section 63:* Admissibility and electronic evidence certification standards for digital computing devices and automated algorithms, establishing the legal requirement for immutable provenance chains (`weights_sha256`, `prompt_git_commit_hash`).
3. **Digital Personal Data Protection (DPDP) Act, 2023:**
   - *Sections 4, 6, and 8:* Purpose limitation, data minimisation, and technical safeguards prohibiting unauthorized egress or cross-border transfer of sensitive personal health data to foreign commercial cloud APIs.
4. **Supreme Court of India — Landmark Emergency Jurisprudence:**
   - *Paschim Banga Khet Mazdoor Samity v. State of West Bengal (1996) 4 SCC 37:* Establishing the constitutional duty of healthcare facilities to provide immediate emergency care without administrative or technical impediment, legally grounding CLINOVA's non-blocking fallback architecture during AI outages.

---

## 2. Clinical Safety, Physiological & Informatics Standards

5. **Royal College of Physicians (UK):**
   - *National Early Warning Score (NEWS) 2: Standardising the assessment of acute-illness severity in the NHS (2017).* Formally cited for deterministic physiological risk scoring independent of generative models.
6. **SNOMED International:**
   - *SNOMED CT Clinical Terminology Core System (2024).* Standardized concept identifiers for terminology normalization.
7. **Regenstrief Institute:**
   - *Logical Observation Identifiers Names and Codes (LOINC) Version 2.76.* Standardized laboratory and observation coding.
8. **World Health Organization (WHO):**
   - *International Classification of Diseases, Eleventh Revision (ICD-11) (2022).* Standardized diagnostic categorization codes.
9. **MedAbstain Evaluation Protocol:**
   - *Evaluating Selective Prediction and Uncertainty Abstention in Clinical Foundation Models (2024).* Clinical benchmarking standard for models declaring epistemic uncertainty.

---

## 3. Open-Source Machine Learning & Runtime Systems

10. **Qwen Team (Alibaba Cloud):**
    - *Qwen2.5: A Party of Foundation Models (2024) / Qwen3 Technical Reports.* Open-weights model family evaluated for Indic multilingual capability and structured output fidelity.
11. **Gerganov, Georgi et al.:**
    - *llama.cpp: Port of Facebook's LLaMA model in C/C++ (2023–2026).* Ultra-low-overhead C++ inference runtime with AVX2/AVX-512 CPU acceleration and GBNF grammar constraints.
12. **Ollama Project:**
    - *Ollama: Get up and running with large language models locally (2023–2026).* Container-free local daemon supporting RESTful JSON structured inference.
13. **OWASP Foundation:**
    - *OWASP Top 10 for Large Language Model Applications (2025):*
      - `LLM01: Prompt Injection`
      - `LLM02: Insecure Output Handling`
      - `LLM06: Sensitive Information Disclosure`
      - `LLM09: Overreliance`

---

## 4. Problem Statement & Upstream System Specifications

14. **BPUT Hackathon Problem Statement & Requirements Baseline (2026):**
    - Requirements `B01` through `B18` and Innovations `C01` through `C11`.
15. **CLINOVA Upstream Research & Architecture Specifications:**
    - Phase 1: Patient Journey & Root-Cause Evidence (`RES-00` to `RES-15`)
    - Phase 2: Existing-Solution Audit & Model Feasibility (`RES-16` to `RES-30`, specifically `RES-19`)
    - Phase 3: Role & Permission Model (`RES-31` to `RES-42`, specifically `RES-34`, `RES-35`)
    - Phase 4: Target Environment & Degradation (`RES-43` to `RES-56`, specifically `RES-50`, `RES-51`)
    - Phase 5: Master Patient Journey & State Machine (`RES-57` to `RES-77`, specifically `RES-61`, `RES-63`)
    - Phase 6: Master Case Canonical Data Model (`RES-78` to `RES-105`, specifically `RES-79`, `RES-89`)
    - Phase 7: Evidence, Provenance & Uncertainty (`RES-106` to `RES-133`, specifically `RES-107`, `RES-116`, `RES-120`)
    - Phase 8: Technical Architecture & System Design (`RES-134` to `RES-163`, specifically `RES-144`, `RES-157`, `RES-159`)
    - Phase 9: Environment, Secrets & Configuration (`RES-164` to `RES-191`, specifically `RES-178`, `RES-185`, `RES-188`)
