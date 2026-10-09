# CLINOVA AI — Phase 8 Authoritative Technical Architecture & Systems Engineering Literature Inventory

> **Document ID:** `SOURCES-PHASE-8`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Safety & Health Informatics Research Group  

---

## 1. Statutory Indian Public Health, Legal & Regulatory Frameworks

1. **National Medical Commission (NMC) (2023).**  
   *National Medical Commission Registered Medical Practitioner (Professional Conduct) Regulations, 2023.* Gazette of India, CG-DL-E-03082023-247852.  
   - *Applied For:* Regulation 27 (Exclusive physician monopoly over medical diagnoses, drug prescriptions, hospital admissions, surgical authorizations, and patient discharges); Regulation 28 (Preservation of medical records for a minimum of 3 years).  
   - *Claim Status:* **SUPPORTED** (Primary statutory text; codified in `RES-137`, `RES-143`, `RES-151`, `RES-152`).

2. **Ministry of Law and Justice, Government of India (2023).**  
   *The Bharatiya Sakshya Adhiniyam, 2023 (Act No. 47 of 2023).* Gazette of India, CG-DL-E-25122023-250882.  
   - *Applied For:* Section 63 (Admissibility of electronic records in legal proceedings, superseding Section 65B of the Indian Evidence Act, 1872; conditions for computer system integrity, uncorrupted hash chaining, and digital certificates of custody).  
   - *Claim Status:* **SUPPORTED** (Primary statutory text; codified in `RES-135`, `RES-145`, `RES-151`, `RES-153`).

3. **Ministry of Law and Justice, Government of India (2023).**  
   *The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023).* Gazette of India, CG-DL-E-12082023-248045.  
   - *Applied For:* Section 4 & 6 (Lawful grounds and notice); Section 7 (Medical emergency implied consent exemption for resuscitation); Section 8(7) (Storage limitation and purpose limitation mandating raw media purging); Section 9 (Verifiable parental consent for pediatric data).  
   - *Claim Status:* **SUPPORTED** (Primary statutory text; codified in `RES-142`, `RES-151`, `RES-153`).

4. **Ministry of Health and Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Sub-Divisional and District Hospitals & Primary Health Centres.* New Delhi: Directorate General of Health Services.  
   - *Applied For:* Standards for 7-year retention of Medico-Legal Case (MLC) and surgical records; frontline clinical staffing ratios; emergency triage equipment lists; facility capability tiers.  
   - *Claim Status:* **SUPPORTED** (Official national standard; codified in `RES-141`, `RES-151`, `RES-154`).

5. **Supreme Court of India (1996).**  
   *Paschim Banga Khet Mazdoor Samity v. State of West Bengal.* (1996) 4 SCC 37.  
   - *Applied For:* Constitutional obligation under Article 21 mandating that government healthcare facilities cannot refuse emergency treatment to a person in critical condition due to lack of beds or equipment without active arranged transfer.  
   - *Claim Status:* **SUPPORTED** (Binding Supreme Court precedent; codified in `RES-141`, `RES-143`, `RES-153`).

6. **Indian Council of Medical Research (ICMR) (2023).**  
   *Ethical Guidelines for Application of Artificial Intelligence in Biomedical Research and Healthcare.* New Delhi: ICMR Department of Health Research.  
   - *Applied For:* Principles of algorithmic accountability, non-autonomous clinical deployment, mandatory human-in-the-loop validation, transparent data provenance, and bias mitigation.  
   - *Claim Status:* **SUPPORTED** (Official national ethical guideline; codified in `RES-135`, `RES-144`, `RES-145`).

---

## 2. Clinical Physiological Scoring & Early Warning Standards

7. **Royal College of Physicians (2017).**  
   *National Early Warning Score (NEWS) 2: Standardising the assessment of acute-illness severity in the NHS.* London: RCP.  
   - *Applied For:* Deterministic physiological scoring table mapping respiration rate, oxygen saturation, systolic BP, pulse, consciousness (AVPU), and temperature into composite early warning scores (0–20) with strict red-flag thresholds ($\ge 7$).  
   - *Claim Status:* **SUPPORTED** (International clinical guideline; codified in `RES-137`, `RES-140`, `RES-149`).

8. **Allgöwer, M., & Burri, C. (1967).**  
   *Schockindex (Shock Index).* Deutsche Medizinische Wochenschrift, 92(43), 1947–1950.  
   - *Applied For:* Deterministic mathematical formula for acute circulatory collapse: $\text{Shock Index} = \text{Heart Rate} / \text{Systolic BP}$ (Normal: 0.5–0.7; Impending Shock: $> 0.9$).  
   - *Claim Status:* **SUPPORTED** (Peer-reviewed physiological standard; codified in `RES-137`, `RES-140`).

---

## 3. Systems Engineering, Distributed Architecture & Informatics Standards

9. **Evans, E. (2003).**  
   *Domain-Driven Design: Tackling Complexity in the Heart of Software.* Addison-Wesley.  
   - *Applied For:* Bounded contexts, aggregates, command-query separation, and domain event ledgers.  
   - *Claim Status:* **SUPPORTED** (Definitive software engineering text; codified in `RES-137`, `RES-138`, `RES-139`).

10. **Grzybek, K. (2019).**  
    *Modular Monolith: A Primer.* Software Architecture Guidelines.  
    - *Applied For:* Structuring in-process modular domain boundaries within a single deployable runtime to achieve microservice-level modularity with zero distributed network overhead.  
    - *Claim Status:* **SUPPORTED** (Modern software engineering pattern; codified in `RES-137`, `RES-138`, `RES-161`).

11. **PostgreSQL Global Development Group (2024).**  
    *PostgreSQL 15 Documentation: Generated Columns and Function Volatility.*  
    - *Applied For:* Mathematical constraints prohibiting volatile functions (`NOW()`, `clock_timestamp()`) in `STORED GENERATED ALWAYS AS` columns.  
    - *Claim Status:* **SUPPORTED** (Official database engineering documentation; codified in `RES-149`, `RES-150`, `RES-161`).

12. **Hipp, D. R. et al. (2024).**  
    *SQLite Write-Ahead Logging (WAL) Architecture and Concurrency.* SQLite Consortium.  
    - *Applied For:* Concurrent read-unblocked writes, busy timeout tuning, PRAGMA foreign key constraints, and 64MB cache configuration on edge Mini-PCs.  
    - *Claim Status:* **SUPPORTED** (Official database engine specification; codified in `RES-147`, `RES-150`, `RES-160`).

13. **National Institute of Standards and Technology (NIST) (2014).**  
    *Special Publication 800-88 Revision 1: Guidelines for Media Sanitization.* Gaithersburg, MD: NIST.  
    - *Applied For:* Cryptographic and physical overwriting techniques for digital media disposal in compliance with DPDP Act retention mandates.  
    - *Claim Status:* **SUPPORTED** (Authoritative security standard; codified in `RES-151`).

14. **World Wide Web Consortium (W3C) (2013).**  
    *PROV-O: The PROV Ontology.* W3C Recommendation 30 April 2013.  
    - *Applied For:* Epistemic provenance lineage (`wasDerivedFrom`, `wasAttributedTo`, `wasGeneratedBy`).  
    - *Claim Status:* **SUPPORTED** (W3C Recommendation; codified in `RES-145`).

15. **Health Level Seven International (HL7) (2023).**  
    *HL7 Fast Healthcare Interoperability Resources (FHIR) Release 5.* Ann Arbor, MI: HL7 International.  
    - *Applied For:* Core resources for `Provenance`, `VerificationResult`, `Observation`, and `ServiceRequest`.  
    - *Claim Status:* **SUPPORTED** (Informatics standard; codified in `RES-138`, `RES-145`, `RES-162`).
