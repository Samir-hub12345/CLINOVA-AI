# CLINOVA AI — Phase 11 Statutory & Clinical Source Authorities

> **Document ID:** `SOURCES_PHASE_11`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Legal Informatics & AI Systems Group  

---

## 1. Statutory Indian Legal & Regulatory Frameworks
1. **National Medical Commission (NMC) Registered Medical Practitioner (Professional Conduct) Regulations, 2023:**
   - Regulation 27: Strict physician monopoly on clinical diagnoses, prescriptions, and medical certificates.
   - Regulation 28: Prohibition of automated, unsupervised electronic prescribing.
2. **Bharatiya Sakshya Adhiniyam (BSA), 2023:**
   - Section 63: Admissibility and continuous evidentiary chain of custody for electronic clinical records and AI provenance pointers.
3. **Digital Personal Data Protection (DPDP) Act, 2023:**
   - Sections 4, 6, 8: Mandatory data minimization, purpose limitation, zero real patient data leakage, and local on-premise data residency.
4. **Supreme Court of India — *Paschim Banga Khet Mazdoor Samity v. State of West Bengal* (1996):**
   - Constitutional emergency doctrine guaranteeing immediate emergency triage and stabilization without administrative delay.

---

## 2. Clinical Terminology, Safety & Scoring Standards
5. **Royal College of Physicians (UK) National Early Warning Score 2 (NEWS2):**
   - Standardized physiological risk stratification across respiratory rate, oxygen saturation, temperature, blood pressure, heart rate, and level of consciousness.
6. **Shock Index (SI):**
   - Hemodynamic compromise threshold ($SI = HR / SBP \ge 0.9$) identifying occult shock.
7. **SNOMED-CT (Systematized Nomenclature of Medicine — Clinical Terms):**
   - International standardized clinical vocabulary for concept normalization.
8. **LOINC (Logical Observation Identifiers Names and Codes):**
   - Universal laboratory and vital sign observation coding.
9. **ICD-11 (International Classification of Diseases, 11th Revision):**
   - Standard epidemiological disease and health condition classifications.
10. **WHO Surgical Safety Checklist:**
    - Standard perioperative sign-in, time-out, and sign-out protocols.

---

## 3. Machine Learning & Safety Benchmarks
11. **MedAbstain Benchmark Protocol (2024):**
    - Evaluation methodology for clinical language models measuring safe abstention under epistemic uncertainty.
12. **Qwen2.5 Technical Report (Alibaba Cloud, 2024):**
    - Architectural specifications, quantization profiles, and multilingual capabilities of Qwen2.5 SLMs.
13. **Llama.cpp & GGUF Quantization Specification (2023–2024):**
    - Efficient integer quantization (`Q4_K_M`) for edge CPU inference without GPU acceleration.

---

## 4. Upstream CLINOVA Architectural Authorities
14. **Phase 10 — Local AI Runtime Foundation (`RES-192` through `RES-219`):**
    - Immediate upstream authority for model selection, task contracts, output validators, and runtime interfaces.
15. **Phase 7 — Provenance & Audit Ledger (`RES-112` through `RES-132`):**
    - Upstream authority for evidence pointers, epistemic state models, and immutable audit ledgers.
