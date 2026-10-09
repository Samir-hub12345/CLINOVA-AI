# CLINOVA AI — Phase 4 Research Sources & Evidence Bibliography

> **Document ID:** `SOURCES_PHASE_4`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Indian Public Health Standards & Regulations

1. **Ministry of Health & Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Sub-Divisional and District Hospitals (100–500 Beds).*  
   New Delhi: Directorate General of Health Services.  
   - *Key Evidence:* Mandated staffing ratios (CMOs, staff nurses, specialists), essential diagnostic laboratories, blood bank operational requirements, casualty observation bed formulas, and emergency major OT readiness.

2. **Ministry of Health & Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Primary Health Centres (PHCs) and Ayushman Arogya Mandirs.*  
   New Delhi: Directorate General of Health Services.  
   - *Key Evidence:* Catchment population benchmarks (20,000–30,000 in plains; 10,000–20,000 in hilly/tribal tracts), single MBBS Medical Officer staffing reality, 4–6 observation bed norms, point-of-care rapid testing lists, and cold-chain anti-snake venom stocking mandates.

3. **National Health Authority (NHA), Government of India (2023).**  
   *Ayushman Bharat Digital Mission (ABDM): Health Facility Registry (HFR) and Health Professional Registry (HPR) Architecture.*  
   New Delhi: NHA.  
   - *Key Evidence:* ABDM M1/M2/M3 milestone requirements, ABHA identifier resolution, paperless token issuance, and health information exchange protocols.

4. **National Medical Commission (NMC), India (2023).**  
   *Registered Medical Practitioner (Professional Conduct) Regulations, 2023.*  
   Gazette of India, Extraordinary, Part III, Section 4.  
   - *Key Evidence:* Sole legal authority of Registered Medical Practitioners (RMPs) to prescribe medications and issue discharge orders; legal liability under Medical Negligence (Section 304A IPC); emergency care duty-to-treat mandates.

5. **Government of India (1948).**  
   *The Factories Act, 1948 (Act No. 63 of 1948), Section 45: Ambulance Room and Medical Care Mandates.*  
   New Delhi: Ministry of Labour & Employment.  
   - *Key Evidence:* Mandatory on-site ambulance rooms and certified Industrial Medical Officers (holding AFIH qualification) for manufacturing facilities employing $> 500$ workers; statutory Form 21 reporting for industrial accidents causing lost-time $> 48$ hours.

6. **Ministry of Law and Justice, Government of India (2023).**  
   *The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023).*  
   Gazette of India, Extraordinary, Part II, Section 1.  
   - *Key Evidence:* Section 4, 6, and 9 provisions regarding sensitive health data processing, absolute requirement of purpose limitation, prohibition of non-clinical employer surveillance, and statutory penalties up to ₹250 crore for unauthorized disclosures.

7. **Supreme Court of India (1996).**  
   *Paschim Banga Khet Mazdoor Samity & Ors. v. State of West Bengal & Anr.*  
   (1996) 4 SCC 37; AIR 1996 SC 2426.  
   - *Key Evidence:* Foundational constitutional ruling declaring that denial of timely medical treatment to an emergency patient by government hospitals violates Article 21 (Right to Life); established statutory duty of public hospitals to provide immediate stabilization prior to transfer.

---

## 2. Clinical Emergency, Ergonomics & Public Health Literature

8. **Indian Council of Medical Research (ICMR) (2020).**  
   *Standard Treatment Workflows (STWs) for Management of Common Medical Emergencies at Primary and Secondary Healthcare Levels.*  
   New Delhi: ICMR Division of Non-Communicable Diseases.  
   - *Key Evidence:* Clinical management protocols for venomous snakebites, organophosphate insecticide poisoning, acute coronary syndromes, hypertensive crises, and status epilepticus in peripheral clinics.

9. **Indian Council of Medical Research (ICMR) (2023).**  
   *Ethical Guidelines for Application of Artificial Intelligence in Biomedical Research and Healthcare.*  
   New Delhi: ICMR Bioethics Unit.  
   - *Key Evidence:* Human-in-the-loop (HITL) mandatory governance, anti-automation bias mechanisms, explainability and provenance requirements, and prohibitions against autonomous algorithmic clinical actions.

10. **World Health Organization (WHO) (2021).**  
    *Essential Emergency and Critical Care (EECC): A Framework for Low-Resource Health Systems.*  
    Geneva: World Health Organization.  
    - *Key Evidence:* Identification of low-cost, high-impact clinical interventions (oxygen delivery, airway positioning, rapid fluid resuscitation, hypoglycemia correction) that halt preventable in-hospital deaths.

11. **Agency for Healthcare Research and Quality (AHRQ) (2020).**  
    *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care (Version 4).*  
    Rockville, MD: U.S. Department of Health and Human Services.  
    - *Key Evidence:* 5-tier algorithmic acuity stratification balancing vital sign physiological stability against expected resource consumption; foundation for CLINOVA's government hospital triage model.

12. **The Lancet Global Health (2018).**  
    *Kruk, M. E., et al. High-quality health systems in the Sustainable Development Goals era: time for a revolution.*  
    *The Lancet Global Health*, 6(11), e1196-e1252.  
    - *Key Evidence:* Demonstrates that $> 50\%$ of maternal and trauma deaths in low- and middle-income countries result not from lack of access, but from poor quality of care and fragmented, delayed referral navigation.

13. **Journal of Family Medicine and Primary Care (2021).**  
    *Garg, R., et al. Time-motion study of outpatient consultations in secondary public healthcare facilities in North India.*  
    *J Family Med Prim Care*, 10(4), 1620–1626.  
    - *Key Evidence:* Empirical measurement of outpatient physician consultation durations in Indian public hospitals (median duration: 112 seconds per patient), demonstrating the severe time poverty that causes electronic documentation abandonment.

14. **American College of Surgeons Committee on Trauma (ACS-COT) (2021).**  
    *Resources for Optimal Care of the Injured Patient: Field Triage Decision Scheme.*  
    Chicago: American College of Surgeons.  
    - *Key Evidence:* Revised Trauma Score (RTS), physiological threshold markers, and destination facility matching for specialized trauma centers.

15. **University Grants Commission (UGC), India (2019).**  
    *Guidelines on Safety and Health of Students in Higher Educational Institutions.*  
    New Delhi: UGC.  
    - *Key Evidence:* Infirmary bed requirements, mandatory on-campus psychological counseling support, and communicable disease quarantine protocols for student residential halls.

---

## 3. Audited Project Artefacts & Architecture Repositories

16. **CLINOVA AI Project Architecture (2026).**  
    *Phase 1 Product Definition & Source of Truth Documentation (`DOC-00` to `DOC-28`).*  
    - `DOC-04`: Target Environments & Operational Workflows.  
    - `DOC-06`: Master Patient Flow & Lifecycle Architecture.  
    - `DOC-09`: CAREGRAPH Dynamic Risk & Trajectory Concept.  
    - `DOC-11`: FACILITYGRAPH Regional Capability Network Concept.  
    - `DOC-12`: SIGNALGRAPH Privacy-Preserving Telemetry Concept.  
    - `DOC-13`: ORCHESTRATION Safety & Action Engine.  
    - `DOC-21`: Zero-Cost ₹0 Open-Source First Technology Stack.

17. **CLINOVA AI Project Architecture (2026).**  
    *Phase 2 Adversarial Research & Innovation Audit (`RES-00` to `RES-24`).*  
    - `RES-10` to `RES-13`: Foundational Graph Gaps & Architectural Boundaries.  
    - `RES-15`: Six-Environment Operational Gap Matrix.  
    - `RES-18`: Zero-Cost Technology Feasibility Validation.  
    - `RES-24`: Phase 2 Synthesis & Architectural Decisions.

18. **CLINOVA AI Project Architecture (2026).**  
    *Phase 3 Target Users & Human-System Interaction Specification (`RES-30` to `RES-42`).*  
    - `RES-31`: 31-Dimension Evaluation of the 8 User Roles.  
    - `RES-33`: Cross-Environment User Role Distribution Matrix.  
    - `RES-34`: 16-Verb Conceptual Role-Based Access Control (RBAC) Model.  
    - `RES-35`: Nine Pillars of Meaningful Human Control (MHC).  
    - `RES-37`: Emergency Resuscitation and OT Fast-Track Role Model.  
    - `RES-39`: DPDP 2023 User Privacy and Cryptographic Shielding Specification.  
    - `RES-42`: Phase 3 Final Synthesis Report.
