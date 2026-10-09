# CLINOVA AI — Phase 6 Authoritative Sources Inventory

> **Document ID:** `SOURCES-PHASE-6`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Indian Public Health, Legal & Regulatory Sources

1. **National Medical Commission (NMC) (2023).**  
   *Registered Medical Practitioner (Professional Conduct) Regulations, 2023.* Gazette of India, CG-DL-E-03082023-247852.  
   *Applied for:* Regulation 27 (Physician monopoly over prescriptions, medical diagnoses, surgical orders, hospital admissions, and formal patient discharges); Regulation 28 (Medical records preservation for a minimum of 3 years).

2. **Ministry of Law and Justice, Government of India (2023).**  
   *The Digital Personal Data Protection Act, 2023 (No. 22 of 2023).* Gazette of India, CG-DL-E-12082023-248045.  
   *Applied for:* Sections 4, 6, and 9 (Explicit consent, vernacular notice, parental consent for pediatric minors, and air-gapping demographic PII from AI inferencing); Section 7 (Medical emergency implied consent waiver).

3. **Parliament of India (1872 / 2023).**  
   *Indian Evidence Act, 1872 (Section 65B: Admissibility of Electronic Records) / Bharatiya Sakshya Adhiniyam, 2023 (Section 63).*  
   *Applied for:* Cryptographic hash chaining ($H_n = \text{SHA256}(...)$), tamper-evident audit ledger architecture, device certification metadata, and immutable append-only event persistence for medicolegal admissibility.

4. **Ministry of Health and Family Welfare (MoHFW), Government of India (2022).**  
   *Indian Public Health Standards (IPHS) 2022: Guidelines for Sub-Divisional and District Hospitals & Primary Health Centres.* New Delhi: DGHS.  
   *Applied for:* Staffing ratios, 7-year retention period for Medico-Legal Cases (MLC), emergency crash cart standards, and inter-facility referral transport protocols.

5. **Supreme Court of India (1996).**  
   *Paschim Banga Khet Mazdoor Samity & Ors. v. State of West Bengal & Anr.* (1996) 4 SCC 37; AIR 1996 SC 2426.  
   *Applied for:* Constitutional Article 21 doctrine: Immediate emergency resuscitation and clinical stabilization cannot be delayed or denied for lack of administrative registration, payment, or demographic credentials.

---

## 2. Health Informatics, Interoperability & Medical Knowledge Standards

6. **Health Level Seven International (HL7) (2023).**  
   *Fast Healthcare Interoperability Resources (FHIR) Release 5.* Ann Arbor, MI: HL7 International.  
   *Applied for:* Resource structural alignment across `Patient`, `Encounter`, `Observation`, `Condition`, `ServiceRequest` (Referral), and `Consent` models.

7. **Regenstrief Institute (2023).**  
   *Logical Observation Identifiers Names and Codes (LOINC) Database.* Indianapolis, IN: Regenstrief Institute.  
   *Applied for:* Standardized concept coding for physiological vitals (LOINC 8480-6 Systolic BP, LOINC 59408-5 SpO2, LOINC 8867-4 Heart Rate) and bedside laboratory measurements.

8. **SNOMED International (2024).**  
   *Systematized Nomenclature of Medicine -- Clinical Terms (SNOMED CT).* London: SNOMED International.  
   *Applied for:* Normalized clinical findings, symptom concepts (SNOMED 29857009 Chest Pain, SNOMED 267036007 Dyspnea), and anatomical sites.

9. **World Health Organization (WHO) (2022).**  
   *International Classification of Diseases, Eleventh Revision (ICD-11).* Geneva: World Health Organization.  
   *Applied for:* Standardized diagnosis impressions and differential hypotheses in clinician review workbench.

10. **World Wide Web Consortium (W3C) (2013).**  
    *PROV-O: The PROV Ontology.* W3C Recommendation 30 April 2013.  
    *Applied for:* Epistemic provenance modeling (`wasDerivedFrom`, `wasAttributedTo`, `wasGeneratedBy`) linking clinical extractions directly to raw audio and document image crops.

---

## 3. Database Architecture, Concurrency & Security Standards

11. **Hipp, D. Richard, et al. (2024).**  
    *SQLite Architecture & Write-Ahead Logging (WAL) Technical Specification.* SQLite Development Team.  
    *Applied for:* Edge Mini-PC database concurrency (`PRAGMA journal_mode = WAL`, `PRAGMA foreign_keys = ON`), local transactions, and sub-millisecond edge writes.

12. **The PostgreSQL Global Development Group (2023).**  
    *PostgreSQL 15 Documentation: Relational Architecture, JSONB Indexing, and Concurrency Control.*  
    *Applied for:* Central cloud relational schema, GIN indexing on structured JSON payloads, and optimistic concurrency control (`state_version`).

13. **Leach, P., Mealling, M., & Salz, R. (2005).**  
    *A Universally Unique IDentifier (UUID) URN Namespace.* IETF RFC 4122.  
    *Applied for:* Global collision-safe entity identification (`UUIDv4`) across disconnected edge nodes and central cloud hubs.

14. **Merkle, Ralph C. (1987).**  
    *A Digital Signature Based on a Conventional Encryption Function.* Advances in Cryptology — CRYPTO '87.  
    *Applied for:* Cryptographic Merkle tree hash chaining of the append-only event ledger and tamper-evident archival sealing (`merkle_root_hash`).
