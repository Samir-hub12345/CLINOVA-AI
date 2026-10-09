# CLINOVA AI — Phase 9 Source Material & Statutory References

> **Document ID:** `SOURCES-PHASE-9`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Legal Informatics, Information Security & Standards Group  

---

## 1. Statutory & Regulatory Sources (India)

1. **National Medical Commission (NMC) Registered Medical Practitioner (Professional Conduct) Regulations, 2023:**
   - *Regulation 27 (AI & Clinical Decision Support):* Mandates that clinical responsibility rests solely with the registered medical practitioner; clinical systems must remain strictly advisory.
   - *Regulation 28 (Digital Prescriptions & Telemedicine):* Prescribes standards for electronic record attribution and verification.

2. **Bharatiya Sakshya Adhiniyam, 2023 (BSA):**
   - *Section 63 (Admissibility of Electronic Records):* Replaces and modernizes Section 65B of the Indian Evidence Act, 1872. Mandates proof of lawful device custody, operational normality, and cryptographic integrity for computer-generated records.

3. **Digital Personal Data Protection (DPDP) Act, 2023:**
   - *Section 4 & 6:* Grounds for processing and notice/consent requirements for health data.
   - *Section 8(7):* Storage limitation principle requiring data fiduciaries to erase personal data as soon as the specified purpose is fulfilled (operationalized via raw media retention limits).
   - *Section 9:* Processing of personal data of children and vulnerable persons.

4. **Indian Public Health Standards (IPHS) 2022:**
   - Standards for Primary Health Centres (PHCs), Community Health Centres (CHCs), Sub-Divisional Hospitals (SDHs), and District Hospitals (DHs), defining facility tiers and staffing requirements.

5. **Supreme Court of India — *Paschim Banga Khet Mazdoor Samity v. State of West Bengal* (1996) 4 SCC 37:**
   - Establishes the constitutional right to emergency medical care under Article 21, informing CLINOVA AI's mandatory rapid casualty intake bypass.

---

## 2. Technical, Cryptographic & Security Standards

6. **The Twelve-Factor App Methodology (Adam Wiggins, Heroku):**
   - *Factor III (Config):* Strict separation of configuration from source code; injection of config via environment variables.

7. **NIST Special Publication 800-63B — Digital Identity Guidelines:**
   - Cryptographic authentication, session management, and secret entropy requirements.

8. **NIST Special Publication 800-88 Rev. 1 — Guidelines for Media Sanitization:**
   - Standards for cryptographic data erasure and storage lifecycle management.

9. **OWASP Top 10 (2021) — A05:2021 Security Misconfiguration:**
   - Threat modeling for default accounts, excessive permissions, CORS misconfigurations, and verbose error messages.

10. **W3C Cross-Origin Resource Sharing (CORS) Specification:**
    - Origin validation, pre-flight checks, and prohibition of wildcard credentials.

11. **W3C CSS Custom Properties (CSS Variables) Level 1:**
    - Standardized design token specification for resilient clinical interfaces without third-party utility compiler overhead.

12. **Next.js 15 Environment Variable Inlining Architecture (Vercel Documentation):**
    - Technical specification governing `NEXT_PUBLIC_*` build-time inlining versus server-side Node.js runtime process isolation.

13. **Pydantic Settings & Zod Type Safety Specifications:**
    - Strongly typed environment variable parsing, field validation, and model validators.

---

## 3. Project Baseline Specifications

14. **Biju Patnaik University of Technology (BPUT) Problem Statement:**
    - Academic specifications for intelligent triage, vernacular intake, resource-aware healthcare, and zero-cost edge operation.

15. **CLINOVA AI Project Master Journey & Architecture Specifications (Phases 1–8):**
    - `docs/research/00_*` through `docs/research/163_*` documenting user roles, environment profiles, master case schemas, evidence provenance, and technical architecture.
