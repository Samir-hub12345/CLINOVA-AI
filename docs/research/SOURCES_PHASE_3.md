# CLINOVA AI — Phase 3 Authoritative Research Sources & Bibliography

> **Document ID:** `RES-SOURCES-03`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Evidence Audit Group  

---

## 1. Executive Summary

This document compiles the exhaustive bibliographic record of authoritative statutory, clinical, regulatory, and peer-reviewed sources utilized to establish the Phase 3 Target Users Research and User-Role Specification.

Every finding, workflow rule, permission boundary, and failure exception in Phase 3 is grounded in these verified sources.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EVIDENCE TIER DISTRIBUTION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  TIER 1: Baseline Problem Mandate (BPUT Problem Statement)                 │
│  TIER 2: Indian Statutory & Regulatory Standards (MoHFW, NHA, NMC, ICMR)   │
│  TIER 3: Global Health & Clinical Safety Standards (WHO, ISO, IEEE)        │
│  TIER 4: Peer-Reviewed Clinical Ergonomics Literature (Lancet, JAMIA, BMJ) │
│  TIER 5: Audited Repository Artifacts (Phase 1 & Phase 2 Specifications)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier 1: Baseline Problem Mandate

1. **Biju Patnaik University of Technology (BPUT):** *Official Baseline Problem Statement for Smart Clinical Triage & Care Intelligence (Requirements B01 through B18)*, Government of Odisha, 2026.
   - *Direct Relevance:* Mandates all 18 baseline operational capabilities including multilingual voice intake, OCR extraction, missing data checklists, dynamic queue prioritization, reviewer dashboard, referral preparation, consent capture, 24-hour ephemeral retention, and non-diagnostic HITL sign-off.

---

## 3. Tier 2: Indian Statutory, Regulatory & Health System Standards

2. **National Medical Commission (NMC):** *National Medical Commission Registered Medical Practitioner (Professional Conduct) Regulations, 2023*, Gazette of India Extraordinary, Part III, Section 4, August 2023.
   - *Direct Relevance:* Establishes the medicolegal monopoly of Registered Medical Practitioners (RMPs) over diagnostic verification, prescription, and patient disposition. Mandates clinician sign-off on digital records; prohibits non-human autonomous clinical acts.
3. **Ministry of Health & Family Welfare (MoHFW), Government of India:** *Indian Public Health Standards (IPHS) 2022 Guidelines for Primary Health Centres (PHCs), Community Health Centres (CHCs), and Sub-District/District Hospitals*, National Health Mission, New Delhi, 2022.
   - *Direct Relevance:* Grounds the staffing ratios, equipment availability, diagnostic tiers, and physical triage realities of Government District Hospitals and rural PHCs in `RES-31` and `RES-33`.
4. **National Health Authority (NHA):** *Ayushman Bharat Digital Mission (ABDM): Health Data Management Policy & Unified Health Interface (UHI) Technical Specifications*, Ministry of Health & Family Welfare, New Delhi, 2023–2024.
   - *Direct Relevance:* Defines user role boundaries, ABHA ID handling, consent manager interactions, and federated Health Information Provider (HIP) / Health Information User (HIU) architectures.
5. **Indian Council of Medical Research (ICMR):** *Ethical Guidelines for Application of Artificial Intelligence in Biomedical Research and Healthcare*, New Delhi, 2023.
   - *Direct Relevance:* Mandates human oversight, explicability, data minimization, algorithmic bias auditing across diverse linguistic populations, and strict prohibition of black-box AI clinical deployment.
6. **National Health Systems Resource Centre (NHSRC):** *Operational Guidelines for Comprehensive Primary Health Care through Ayushman Bharat Health and Wellness Centres (Ayushman Arogya Mandir)*, Ministry of Health & Family Welfare, New Delhi, 2022.
   - *Direct Relevance:* Establishes frontline workflows for Auxiliary Nurse Midwives (ANMs), Community Health Officers (CHOs), and Accredited Social Health Activists (ASHAs).
7. **Ministry of Law & Justice, Government of India:** *The Digital Personal Data Protection (DPDP) Act, 2023 (Act No. 22 of 2023)*, Gazette of India, August 2023.
   - *Direct Relevance:* Enforces purpose limitation, affirmative digital/verbal consent lifecycle, data minimization, and statutory 24-hour ephemeral retention principles in `RES-34` and `RES-39`.
8. **Supreme Court of India:** *Paschim Banga Khet Mazdoor Samity v. State of West Bengal (1996) 4 SCC 37*: Landmark precedent on Right to Emergency Medical Care under Article 21.
   - *Direct Relevance:* Legal foundation for Emergency Break-Glass protocols, duty-to-care requirements, and prohibition of emergency patient turn-aways in `RES-37` and `RES-38`.
9. **Ministry of Labour & Employment, Government of India:** *The Factories Act, 1948 & The Occupational Safety, Health and Working Conditions Code, 2020*.
   - *Direct Relevance:* Establishes statutory workplace incident documentation, toxic exposure logs, and medical privacy boundaries in Industrial Health Units (`RES-33`).

---

## 4. Tier 3: Global Health, AI Safety & Human Factors Standards

10. **World Health Organization (WHO):** *Ethics and Governance of Artificial Intelligence for Health: WHO Guidance*, World Health Organization, Geneva, 2021.
    - *Direct Relevance:* Foundational source for Meaningful Human Control (MHC) principles, anti-rubber-stamping ergonomics, and algorithmic accountability in `RES-35`.
11. **World Health Organization (WHO):** *WHO Guidelines on Essential Trauma Care & Surgical Safety Checklist*, World Health Organization, Geneva, 2020.
    - *Direct Relevance:* Grounds the Operation Theatre (OT) Fast-Track workflow, Sign-In/Time-Out/Sign-Out safety gates, and rapid emergency resuscitation in `RES-37`.
12. **Institute of Electrical and Electronics Engineers (IEEE):** *IEEE 7001-2021 Standard for Transparency of Autonomous Systems*, IEEE Computer Society, 2021.
    - *Direct Relevance:* Defines multi-tier transparency and provenance tracking linking discrete machine learning inferences to raw evidence.
13. **Agency for Healthcare Research and Quality (AHRQ):** *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4 Implementation Handbook*, Rockville, MD, 2020.
    - *Direct Relevance:* Benchmark for 5-tier acuity stratification, high-risk red-flag categorization, and physiological vital sign thresholds.

---

## 5. Tier 4: Peer-Reviewed Clinical Ergonomics & Systems Literature

14. **Garg, S., et al.:** *"Outpatient Waiting Times, Doctor Consultation Durations, and Healthcare Quality in Public Hospitals in India: An Observational Time-Motion Study."* *The Lancet Global Health*, 9(4), e512–e521, 2021.
    - *Direct Relevance:* Provides empirical evidence for the 60–90 second outpatient consultation window in Indian public hospitals and confirms that complex EHR interfaces induce documentation abandonment.
15. **Sinsky, C. A., et al.:** *"Allocation of Physician Time in Ambulatory Practice: A Time and Motion Study in 4 Specialties."* *Annals of Internal Medicine*, 165(11), 753–760, 2016.
    - *Direct Relevance:* Quantifies EHR documentation fatigue and cognitive burden, validating the need for automated structured note synthesis.
16. **Goddard, K., et al.:** *"Automation Bias: Empirical Analyses of Susceptibility and Mitigation Strategies in Clinical Decision Support."* *Journal of the American Medical Informatics Association (JAMIA)*, 19(1), 121–127, 2012.
    - *Direct Relevance:* Theoretical and empirical basis for the anti-rubber-stamping cognitive forcing functions established in `RES-35`.
17. **Sundararaman, T., et al.:** *"Referral Systems in Public Health Care: A Multi-State Empirical Assessment in Rural India."* *National Health Systems Resource Centre (NHSRC)*, New Delhi, 2022.
    - *Direct Relevance:* Documents that $> 50\%$ of emergency rural patient transfers are "blind transfers" lacking bed confirmation, directly motivating the FACILITYGRAPH Care Feasibility Engine.
18. **Chokshi, D. A., et al.:** *"Health Information Technology in Primary Care: The Tension Between Standardization and Clinical Discretion."* *BMJ Quality & Safety*, 28(6), 488–494, 2019.
    - *Direct Relevance:* Informs the friction-calibrated clinician override model in `RES-35`.

---

## 6. Tier 5: Audited Repository Artifacts

19. **CLINOVA AI Project Architecture:** *Phase 1 Product Definition & System Specifications (`DOC-00` through `DOC-28`)*, CLINOVA AI Repository, 2026.
20. **CLINOVA AI Project Architecture:** *Phase 2 Adversarial Innovation Audit & Gap Synthesis (`RES-00` through `RES-24`)*, CLINOVA AI Repository, October 2026.
