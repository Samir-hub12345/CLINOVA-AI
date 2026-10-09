# CLINOVA AI — Granular Feature Novelty & Classification Matrix

> **Document ID:** `RES-17`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Classification Methodology

Every claimed capability in CLINOVA AI—encompassing the **18 BPUT Mandatory Baseline Requirements** (`B01`–`B18`) and the **11 Core Continuous Care Innovations** (`C01`–`C11`)—is subjected here to strict adversarial novelty classification.

### Permitted Classification Statuses:
- **`BASELINE`:** Explicitly mandated by the official BPUT problem statement; operational necessity.
- **`EXISTING`:** Widely solved and deployed in industry or open-source; no novelty claim permitted.
- **`INTEGRATION`:** Existing technologies unified across silos to solve a documented workflow gap.
- **`RESEARCH`:** Active academic research frontier; requires rigorous validation.
- **`CLINOVA CONTRIBUTION`:** The defensible, bounded core innovation introduced by the CLINOVA architecture.
- **`FUTURE`:** Post-hackathon capability deferred to Phase 3/4 or research grant stage.
- **`UNVALIDATED`:** Hypothesis lacking empirical evidence; slated for modification or de-scoping.

---

## 2. Granular Novelty Audit of the 18 BPUT Baseline Capabilities (`B01`–`B18`)

| ID | Feature Name | BPUT Baseline? | Existing Industry? | Existing Research? | Existing Gov System? | Existing Open-Source? | Novel Combination? | Research Opportunity? | CLINOVA Contribution? | Evidence Strength | Confidence | Classification Decision | Technical Rationale & Scope Boundary |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **B01** | **Text Symptom Intake** | **Yes** | Yes (Ada, WebMD, K Health) | Yes | Yes (e-Hospital, CoWIN) | Yes (OpenMRS, Bahmni) | No | No | No | **Grade A** | 100% | **BASELINE** | Standard textarea narrative entry with duration capture. Zero novelty; mandatory table-stakes baseline. |
| **B02** | **Voice Symptom Intake** | **Yes** | Yes (Nuance, Abridge, Suki) | Yes (Whisper benchmarks) | No | Yes (faster-whisper, Whisper.cpp)| Yes (Local Indic offline)| No | No | **Grade A** | 100% | **BASELINE** | Local speech-to-text via faster-whisper (CTranslate2). Established tech integrated at ₹0 on-premise. |
| **B03** | **Medical Report Extraction** | **Yes** | Yes (AWS Comprehend, Google Health) | Yes (Biomedical NER) | No | Yes (Spacy, Transformers) | Yes (Coupled to graph)| No | No | **Grade A** | 100% | **BASELINE** | Extraction of discrete lab biomarkers (Hb, TLC, Platelets). Standard clinical NLP applied to CBC panels. |
| **B04** | **Optical Character Recognition (OCR)**| **Yes** | Yes (Google Cloud Vision, ABBYY) | Yes | Yes | Yes (PaddleOCR, Tesseract) | Yes (Local offline) | No | No | **Grade A** | 100% | **BASELINE** | Local computer vision extracting printed text from prescription slips. Solved open-source capability. |
| **B05** | **Extraction & Structuring** | **Yes** | Yes (Epic, Cerner, Linguamatics) | Yes (SNOMED / UMLS mapping) | Yes (ABDM Terminology)| Yes (cTAKES, MedCAT) | Yes (Master Case mapping)| No | No | **Grade A** | 100% | **BASELINE** | Mapping vernacular descriptions into standardized entities. Essential baseline processing pipeline. |
| **B06** | **Timeline Summarization** | **Yes** | Yes (Abridge, Ambience, Epic) | Yes (Event extraction) | No | Yes (Timeline.js, D3.js) | Yes (Provenance linked)| No | No | **Grade A** | 100% | **BASELINE** | Chronological ordering of clinical onset and interventions. Established UI summarization technique. |
| **B07** | **Missing-Information Detection** | **Yes** | Yes (Infermedica API) | Yes (Value of Information) | No | No | Yes (Uncertainty linked)| Yes | Yes (NBI engine) | **Grade A** | 95% | **INTEGRATION** | Auditing clinical checklists for absent vitals/qualifiers. Combined with CAREGRAPH uncertainty state. |
| **B08** | **Follow-up Question Generation** | **Yes** | Yes (Ada Health, Infermedica) | Yes (Active learning) | No | No | Yes (Gap closure) | Yes | Yes (NBI engine) | **Grade A** | 95% | **INTEGRATION** | Algorithmic generation of 1–3 high-yield gap questions. Solved by Bayesian engines; integrated into SLM. |
| **B09** | **Language / Translation Support** | **Yes** | Yes (Google Translate, Bhashini) | Yes (IndicTrans2, MarianMT) | Yes (Bhashini MoU) | Yes (IndicTrans2 open weights)| Yes (Local offline) | No | No | **Grade A** | 100% | **BASELINE** | Translating Odia/Hindi narratives to English clinical descriptors. Open-source models applied locally. |
| **B10** | **Risk-Category Support** | **Yes** | Yes (ESI, MTS, Epic EDI) | Yes (NEWS2 validation) | Yes (ICMR Triage guidelines)| Yes (MEWS Python libs) | Yes (Dynamic trajectory)| No | No | **Grade A** | 100% | **BASELINE** | NEWS2 and Shock Index calculation with deterministic red-flag triggers (`TRIAGE-R01` to `TRIAGE-R06`). |
| **B11** | **Queue Prioritization** | **Yes** | Yes (Hospital token systems) | Yes (Queuing theory $M/M/c$) | Yes (NIC e-Hospital tokens) | Yes (Queue managers) | Yes (Wait-time penalty) | No | No | **Grade A** | 100% | **BASELINE** | Multi-factor queue sorting combining risk band, wait duration, and trajectory delta. Standard ops engine. |
| **B12** | **Reviewer Dashboard** | **Yes** | Yes (Epic, Cerner, Ambience) | Yes (Cognitive load UI) | Yes (e-Hospital Doctor Desk)| Yes (Bahmni Clinical UI) | Yes (One-screen graph) | No | No | **Grade A** | 100% | **BASELINE** | One-screen workstation for doctor verification and override. Mandated human-in-the-loop interface. |
| **B13** | **Referral Preparation** | **Yes** | Yes (ReferralMD, Epic CareLink)| Yes | Yes (Form 14 paper slips) | No | Yes (Capability matched)| No | No | **Grade A** | 100% | **BASELINE** | Automated synthesis of structured transfer documentation. Baseline administrative feature. |
| **B14** | **Consent Capture** | **Yes** | Yes (Docusign, OneTrust) | Yes | Yes (ABDM Consent Manager) | Yes | No | No | No | **Grade A** | 100% | **BASELINE** | Digital and verbal consent confirmation gate prior to data persistence. Compliance invariant. |
| **B15** | **Privacy & Anonymization** | **Yes** | Yes (John Snow Labs, Microsoft) | Yes (HIPAA de-id benchmarks) | Yes (DISHA / DPDP Act) | Yes (Presidio, Scrubber) | No | No | No | **Grade A** | 100% | **BASELINE** | In-flight regex and NLP scrubbing of phone numbers and government IDs. Standard privacy filter. |
| **B16** | **Minimal Data Retention** | **Yes** | Yes (AWS S3 lifecycle, GDPR) | Yes | Yes (DPDP Act mandates) | Yes (Postgres cron) | No | No | No | **Grade A** | 100% | **BASELINE** | 24-hour ephemeral retention policy purging transient audio and images. Standard security safeguard. |
| **B17** | **Auditability** | **Yes** | Yes (Epic Chronicles audit log) | Yes (Tamper-evident logs) | Yes (CERT-In mandates) | Yes (Blockchain / Hash chains)| No | No | No | **Grade A** | 100% | **BASELINE** | Cryptographically hashed append-only audit ledger tracking actor ID, timestamps, and overrides. |
| **B18** | **Non-Diagnostic Advisory Stance** | **Yes** | Yes (Ada Health disclaimer) | Yes (FDA SaMD guidelines) | Yes (ICMR AI Guidelines) | Yes | No | No | No | **Grade A** | 100% | **BASELINE** | Enforced non-diagnostic labeling and mandatory licensed clinician sign-off gate. Legal boundary. |

---

## 3. Granular Novelty Audit of the 11 CLINOVA Core Innovations (`C01`–`C11`)

| ID | Feature Name | BPUT Baseline? | Existing Industry? | Existing Research? | Existing Gov System? | Existing Open-Source? | Novel Combination? | Research Opportunity? | CLINOVA Contribution? | Evidence Strength | Confidence | Classification Decision | Technical Rationale & Scope Boundary |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **C01** | **CAREGRAPH Dynamic State Engine** | No | Partial (ICU monitors) | Yes (Temporal GNNs) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 90% | **CLINOVA CONTRIBUTION** | Translating ICU dynamic trajectory slope ($\Delta R_t / \Delta t$) into an active outpatient triage state engine. |
| **C02** | **Multi-Source Evidence Provenance** | No | Partial (Abridge audio only) | Yes (W3C PROV-O) | No | No | **Yes** | No | **Yes** | **Grade B** | 95% | **INTEGRATION** | Uniting audio timecodes, OCR bounding boxes, vitals, and patient self-report into unified provenance links. |
| **C03** | **Uncertainty Quantification ($U_t$)**| No | No (Commercial CDSS hide gaps)| Yes (Conformal prediction) | No | No | **Yes** | **Yes** | **Yes** | **Grade A** | 95% | **CLINOVA CONTRIBUTION** | Mathematical modeling of missing/conflicting clinical data as a first-class state vector driving UI alerts. |
| **C04** | **Next-Best Information (NBI) Engine**| No | Partial (Infermedica API) | Yes (Value of Information) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 90% | **CLINOVA CONTRIBUTION** | Ranking candidate questions by expected uncertainty reduction to collapse diagnostic ambiguity. |
| **C05** | **FACILITYGRAPH Resource Modeling** | No | Partial (TeleTracking beds) | Yes (Healthcare OR) | Partial (HMIS bed counts) | No | **Yes** | No | **Yes** | **Grade A** | 95% | **CLINOVA CONTRIBUTION** | Modeling 5 granular resource tiers (resuscitation, on-duty specialists, blood, beds, distance) at ₹0. |
| **C06** | **Care Feasibility Matching Engine**| No | No (Commercial match on tags) | Yes (Constraint matching) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 90% | **CLINOVA CONTRIBUTION** | Algorithmic evaluation of patient clinical prerequisites against live facility capabilities before transfer. |
| **C07** | **SIGNALGRAPH Macro-Telemetry** | No | Partial (IHIP upwards only) | Yes (EARS anomaly algorithms)| Yes (IHIP / IDSP) | No | **Yes** | No | **Yes** | **Grade A** | 95% | **INTEGRATION** | Uniting syndromic disease surges with hospital queuing bottlenecks; feeding intelligence back to clinic desk. |
| **C08** | **Multi-Graph ORCHESTRATION Core** | No | No (No system bridges all graphs)| Yes (Multi-agent planning) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 85% | **CLINOVA CONTRIBUTION** | Synthesizing CareGraph + Uncertainty + FacilityGraph + SignalGraph into candidate actions (`ASK` to `REFER`). |
| **C09** | **The Safest Achievable Care Pathway**| No | No (Systems output single answers) | Yes (Risk-sensitive MDPs) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 90% | **CLINOVA CONTRIBUTION** | Framing AI decision support as resource-aware, safety-first guidance rather than authoritative diagnosis. |
| **C10** | **Post-Disposition Continuity & Loop**| No | Partial (CarePort post-acute) | Yes (Longitudinal EHR) | No | No | **Yes** | **Yes** | **Yes** | **Grade B** | 90% | **CLINOVA CONTRIBUTION** | Two-tier outcome tracking linking ground-truth clinical recovery back to Master Case and calibration telemetry. |
| **C11** | **Clinician Learning & Calibration** | No | Partial (Offline ML logs) | Yes (Active learning) | No | No | **Yes** | **Yes** | **FUTURE** | **Grade B** | 80% | **FUTURE (Phase 3/4)**| Structured discordance logging in Phase 2; offline LoRA model fine-tuning deferred to post-hackathon grant stage. |

---

## 3. Summary Novelty Distribution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA CAPABILITY COMPOSITION                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ MANDATORY BASELINE ] ────────> 18 Capabilities (B01–B18)                 │
│  (100% required by BPUT; zero novelty claimed; table-stakes foundation)     │
│                                                                             │
│  [ MEANINGFUL INTEGRATIONS ] ───> 4 Capabilities (B07, B08, C02, C07)       │
│  (Uniting existing proven technologies across historical silos)             │
│                                                                             │
│  [ DEFENSIBLE CONTRIBUTIONS ] ──> 7 Capabilities (C01, C03, C04, C05,       │
│                                                   C06, C08, C09, C10)       │
│  (The core continuous care intelligence suite evaluated under ₹0 constraints)│
│                                                                             │
│  [ DEFERRED FUTURE RESEARCH ] ──> 1 Capability (C11)                        │
│  (Continuous model fine-tuning deferred to Phase 3/4 grant evaluation)      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
