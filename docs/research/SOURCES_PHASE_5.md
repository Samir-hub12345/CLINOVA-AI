# CLINOVA AI — Phase 5 Authoritative Sources Inventory

> **Document ID:** `SOURCES-PHASE-5`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Indian Public Health, Legal & Regulatory Sources

1. **Ministry of Health and Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Sub-Divisional and District Hospitals (Vol. I & II).* New Delhi: Directorate General of Health Services.  
   *Applied for:* Triage infrastructure, staffing norms, inpatient ward admission ratios, ICU bed specifications, and inter-facility referral protocols.

2. **Ministry of Health and Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Primary Health Centres (PHCs).* New Delhi: DGHS.  
   *Applied for:* Rural primary care staffing limitations, essential drug lists (EDL), diagnostic equipment boundaries, and referral transport triggers.

3. **National Medical Commission (NMC) (2023).**  
   *Registered Medical Practitioner (Professional Conduct) Regulations, 2023.* Gazette of India, CG-DL-E-03082023-247852.  
   *Applied for:* Section 27 physician monopoly over medical diagnoses, prescription writing, surgical consent, hospital admission, and formal patient discharge.

4. **Ministry of Law and Justice, Government of India (2023).**  
   *The Digital Personal Data Protection Act, 2023 (No. 22 of 2023).* Gazette of India, CG-DL-E-12082023-248045.  
   *Applied for:* Sections 4, 6, and 9 governing explicit data consent, parental consent for pediatric minors, and administrative data air-gapping (DPDP Shield).

5. **Supreme Court of India (1996).**  
   *Paschim Banga Khet Mazdoor Samity & Ors. v. State of West Bengal & Anr.* (1996) 4 SCC 37; AIR 1996 SC 2426.  
   *Applied for:* Landmark constitutional ruling under Article 21 establishing that government hospitals cannot deny emergency treatment or resuscitation to patients citing lack of beds or specialized equipment without immediate stabilization.

6. **Ministry of Labour and Employment, Government of India (1948).**  
   *The Factories Act, 1948 (Act No. 63 of 1948), Section 45: Ambulance Room and First-Aid Appliances.*  
   *Applied for:* Statutory industrial health clinic operations, emergency crash protocols, and Medico-Legal Case (MLC) accident registers.

---

## 2. Clinical Triage, Critical Care & Patient Safety Standards

7. **Indian Council of Medical Research (ICMR) (2023).**  
   *Ethical Guidelines for Application of Artificial Intelligence in Healthcare.* Department of Health Research, Ministry of Health and Family Welfare, Government of India.  
   *Applied for:* Principles of autonomy, human-in-the-loop oversight, explainability, visual evidence provenance, and prohibition of autonomous AI diagnosis.

8. **World Health Organization (WHO) (2021).**  
   *Essential Emergency and Critical Care (EECC): A Framework for Low- and Middle-Income Settings.* Geneva: World Health Organization.  
   *Applied for:* The 30-second ABCD vital signs protocol, early oxygen therapy, shock recognition, and resuscitation bundle prioritization over administrative intake.

9. **Agency for Healthcare Research and Quality (AHRQ) (2012).**  
   *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4. Implementation Handbook 2012 Edition.* Rockville, MD: AHRQ Publication No. 12-0014.  
   *Applied for:* Acuity level stratification (Levels 1–5), high-risk physiological danger triggers, and resource consumption predictions.

10. **World Health Organization (WHO) (2009).**  
    *WHO Surgical Safety Checklist and Implementation Manual.* Geneva: World Health Organization.  
    *Applied for:* Three-phase surgical verification protocol ("Sign In", "Time Out", "Sign Out") and dual clinician authorization in the Operation Theatre (OT) Pathway.

11. **Royal College of Physicians (2017).**  
    *National Early Warning Score (NEWS) 2: Standardising the assessment of acute-illness severity in the NHS.* London: RCP.  
    *Applied for:* Composite physiological deterioration scoring, trajectory calculation, and early warning alerting for inpatient and waiting-room decompensation.

---

## 3. Health Informatics & Systems Architecture References

12. **National Health Authority (NHA), Government of India (2023).**  
    *Ayushman Bharat Digital Mission (ABDM): Health Facility Registry (HFR) and Health Professional Registry (HPR) Architecture Specifications (Version 2.0).*  
    *Applied for:* Cross-facility referral data payloads, practitioner identity verification, and synthetic anonymized identifier architecture (`PT-XXXXXX`).

13. **Joint Commission International (JCI) (2020).**  
    *Standards for Clinical Handoff Communication: The SBAR Framework (Situation, Background, Assessment, Recommendation).*  
    *Applied for:* Inpatient ward admission transfers and inter-facility ambulance departure/arrival handoffs.

---

## 4. Internal CLINOVA Repository Specifications & Decision Logs

14. **CLINOVA Phase 1 Product Definition & Architecture Source of Truth (2026).**  
    - `docs/00_PRODUCT_DEFINITION.md` (`DOC-00`)
    - `docs/06_MASTER_PATIENT_FLOW.md` (`DOC-06`)
    - `docs/07_MASTER_CASE_MODEL.md` (`DOC-07`)
    - `docs/08_EVIDENCE_PROVENANCE_MODEL.md` (`DOC-08`)
    - `docs/15_POST_DOCTOR_PATHWAYS.md` (`DOC-15`)
    - `docs/16_EMERGENCY_OT_FLOW.md` (`DOC-16`)
    - `docs/17_CONTINUITY_OUTCOME_MODEL.md` (`DOC-17`)
    - `docs/28_DECISION_LOG.md` (`DOC-28`)

15. **CLINOVA Phase 2 Clinical AI & Innovation Research Audits (2026).**  
    - `docs/research/01_PATIENT_JOURNEY_RESEARCH.md` (`RES-01`)
    - `docs/research/09_CLINICAL_AI_SAFETY_AUDIT.md` (`RES-09`)
    - `docs/research/10_CAREGRAPH_GAP.md` (`RES-10`)
    - `docs/research/11_FACILITYGRAPH_GAP.md` (`RES-11`)
    - `docs/research/13_ORCHESTRATION_GAP.md` (`RES-13`)
    - `docs/research/14_OUTCOME_LOOP_AUDIT.md` (`RES-14`)

16. **CLINOVA Phase 3 Target User Roles & Human Control Specifications (2026).**  
    - `docs/research/31_USER_ROLE_ANALYSIS.md` (`RES-31`)
    - `docs/research/34_ROLE_PERMISSION_MODEL.md` (`RES-34`)
    - `docs/research/35_HUMAN_CONTROL_MODEL.md` (`RES-35`)
    - `docs/research/37_EMERGENCY_ROLE_MODEL.md` (`RES-37`)
    - `docs/research/PHASE_3_DECISIONS.md`

17. **CLINOVA Phase 4 Target Environments & Operational Context Specifications (2026).**  
    - `docs/research/44_GOVERNMENT_HOSPITAL_ENVIRONMENT.md` (`RES-44`)
    - `docs/research/45_PHC_ENVIRONMENT.md` (`RES-45`)
    - `docs/research/50_ENVIRONMENT_CORE_VS_CONFIGURATION.md` (`RES-50`)
    - `docs/research/51_ENVIRONMENT_FAILURE_MATRIX.md` (`RES-51`)
    - `docs/research/52_ENVIRONMENT_EMERGENCY_MODEL.md` (`RES-52`)
    - `docs/research/55_MVP_ENVIRONMENT_DECISION.md` (`RES-55`)
    - `docs/research/56_PHASE_4_CONCLUSION.md` (`RES-56`)
    - `docs/research/PHASE_4_DECISIONS.md`

18. **CLINOVA Phase 5 Decision Log (2026).**  
    - `docs/research/PHASE_5_DECISIONS.md` (Formal log of Decisions 5.1 through 5.10).
