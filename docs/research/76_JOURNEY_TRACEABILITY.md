# CLINOVA AI — Master Journey Bidirectional Traceability Matrix Specification

> **Document ID:** `RES-76`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Traceability Architecture & Governance

The **Master Journey Bidirectional Traceability Matrix** establishes unbroken, end-to-end structural alignment across every operational milestone of the CLINOVA platform. It guarantees that every user interaction, algorithm invocation, clinical safety gate, and audit event maps directly to an underlying engineering deliverable and implementation roadmap phase.

### 1.1 Traceability Schema (12 Dimensions)
Each milestone is defined across 12 rigorous parameters:
1. **Journey Stage:** Formal stage label within the care continuum.
2. **User Role:** Active human actor under RBAC governance (`ROLE_PATIENT`, `ROLE_HEALTH_WORKER`, `ROLE_NURSE`, `ROLE_CLINICIAN`, `ROLE_ADMIN`).
3. **Target Environment:** Operational setting (`ENV_PHC`, `ENV_GOV_HOSPITAL`, or `ALL`).
4. **Input Modality:** Physical or digital data ingested.
5. **Data State:** Canonical state machine state ID ($S01$–$S27$).
6. **AI / Rule Support:** Underlying deterministic rule or ML microservice.
7. **Human Decision:** The clinical judgment executed by the human actor.
8. **Next State:** Target destination state following transition.
9. **Safety Control:** Active safety gate, validation check, or statutory constraint.
10. **Audit Event:** Cryptographic event identifier logged to immutable ledger.
11. **Generated Output:** Concrete clinical or administrative document produced.
12. **Implementation Phase:** Target roadmap phase responsible for software delivery.

---

## 2. End-to-End Journey Traceability Matrix

| # | Journey Stage | User Role | Environment | Input Modality | Data State | AI / Rule Support | Human Decision | Next State | Safety Control | Audit Event | Generated Output | Implementation Phase |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **01** | **New Encounter** | `ROLE_PATIENT` / `ROLE_ADMIN` | ALL | Demographic voice/text | `S01: STATE_NEW` | Language detector | Selects regular vs emergency intake | `S02` / `S22` | DPDP explicit consent validation | `ENCOUNTER_INITIALIZED` | Synthetic Patient Token (`PT-XXXXXX`) | Phase 6 |
| **02** | **Multimodal Ingestion** | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | ALL | Vernacular speech, paper slips | `S02: INTAKE_COLLECTING` | Local audio & image buffer | Submits raw symptoms and prior files | `S03: STATE_EXTRACTING` | Antivirus scan; file size $\le 15$MB | `INPUTS_SUBMITTED` | Raw Multimodal Ingestion Payload | Phase 6 |
| **03** | **Entity Extraction** | `ROLE_SYSTEM_AI` | ALL | Raw files | `S03: STATE_EXTRACTING` | Quantized Whisper & PaddleOCR | Background worker execution | `S04: EXTRACTION_REVIEW` | Timeout fallback; bounds check | `EXTRACTION_FINISHED` | Extracted Clinical Entity List | Phase 7 |
| **04** | **Extraction Review** | `ROLE_PATIENT` / `ROLE_HEALTH_WORKER` | ALL | Touch / keyboard edits | `S04: EXTRACTION_REVIEW` | Side-by-side snippet highlighter | Confirms or corrects extracted symptoms | `S05: MISSING_AUDIT` | Visual provenance display mandate | `EXTRACTION_CONFIRMED` | Reviewed & Normalized Entity Set | Phase 8 |
| **05** | **Missing Information Audit** | `ROLE_SYSTEM_AI` | ALL | Extracted entities | `S05: MISSING_AUDIT` | Deterministic Completeness Engine | Computes Known/Unknown/Conflict vector | `S06` / `S07` / `S09` | Zero Imputation Law (No default normal) | `MISSING_AUDIT_LOGGED` | Information Sufficiency Vector | Phase 7 |
| **06** | **Targeted Follow-Up** | `ROLE_PATIENT` | ALL | Touch selection | `S06: FOLLOW_UP_PENDING`| Next-Best-Information (NBI) Engine| Answers 1–3 vernacular clarifying questions | `S07` / `S09` | Hard limit $\le 3$ questions; 120s timeout | `FOLLOW_UP_COMPLETED` | Refined Encounter Data Payload | Phase 8 |
| **07** | **Staff Point-of-Care Vitals** | `ROLE_NURSE` / `ROLE_HEALTH_WORKER` | `ENV_PHC` / `ENV_GOV_HOSPITAL` | Physical instruments (BP, SpO2) | `S07: STAFF_DATA_PENDING` | Range validation & shock index alert | Measures calibrated physiological vitals | `S08: STAFF_VERIFIED` | Dynamic Red-Flag Gate (SpO2 $< 85\%$) | `STAFF_VITALS_RECORDED` | Verified Vitals Snapshot | Phase 8 |
| **08** | **Staff Sign-Off** | `ROLE_NURSE` | ALL | Nurse digital signature | `S08: STAFF_VERIFIED` | Completeness validator | Validates nursing dataset | `S09: CONSOLIDATED` | Two-factor credential check | `STAFF_SIGN_OFF_EXECUTED` | `STAFF_VERIFIED` Provenance Stamp | Phase 8 |
| **09** | **Data Consolidation** | `ROLE_SYSTEM_AI` | ALL | Validated data streams | `S09: CONSOLIDATED` | Master Case schema assembler | Merges data into Master Clinical Dossier | `S10: TRIAGE_READY` | Data integrity & UUID validation | `DOSSIER_CONSOLIDATED` | Master Clinical Dossier | Phase 9 |
| **10** | **CAREGRAPH Synthesis** | `ROLE_SYSTEM_AI` | ALL | Master Clinical Dossier | `S10: TRIAGE_READY` | CAREGRAPH reasoning engine | Evaluates Risk, Trajectory, Uncertainty | `S11: DOCTOR_QUEUED` | Mandatory AI Advisory watermark | `CAREGRAPH_SYNTHESIZED` | Structured Triage Note & Report 1 | Phase 9 |
| **11** | **Doctor Queue Prioritization** | `ROLE_SYSTEM_AI` | ALL | Risk & wait metrics | `S11: DOCTOR_QUEUED` | Dynamic Queue Prioritization Engine | Ranks cases by composite priority vector | `S12: DOCTOR_REVIEWING` | Time-decay anti-starvation gate | `CASE_ENQUEUED` | Acuity-Sorted Outpatient Queue | Phase 8 |
| **12** | **Doctor Case Consultation** | `ROLE_CLINICIAN` | ALL | Clinical exam & history | `S12: DOCTOR_REVIEWING` | 7-Panel Unified Workbench HUD | Reviews evidence, history, and graph | `S13: CLINICIAN_VERIFIED`| Session exclusivity lock on case | `CONSULTATION_OPENED` | Active Doctor Session Workspace | Phase 8 |
| **13** | **Doctor Verification & Actions** | `ROLE_CLINICIAN` | ALL | Keyboard / voice physical exam | `S13: CLINICIAN_VERIFIED`| Trajectory recalculator | Executes `VERIFY`, `MODIFY`, or `ADD` | `S14: FACILITY_EVALUATING`| Mandatory clinical diagnosis input | `CLINICIAN_VERIFICATION_SIGNED`| Authoritative Clinical Record | Phase 8 |
| **14** | **FACILITYGRAPH Feasibility** | `ROLE_SYSTEM_AI` | ALL | Clinical needs vs facility assets | `S14: FACILITY_EVALUATING` | FACILITYGRAPH network search | Computes Feasibility Index $\Phi_{\text{local}}$ | `S15: ORCHESTRATION_PENDING`| Stale data warning if $> 12$h old | `FEASIBILITY_COMPUTED` | Feasibility Index & Deficit Vector | Phase 10 |
| **15** | **Orchestration Advice** | `ROLE_SYSTEM_AI` | ALL | Patient state + feasibility | `S15: ORCHESTRATION_PENDING`| Multi-Graph Orchestration Engine | Recommends Safest Achievable Pathway | Disposition Gate | Meaningful Human Control (Advisory only) | `ORCHESTRATION_ADVICE_EMITTED` | Advisory Care Pathway Card | Phase 10 |
| **16** | **Pathway A: Routine Home Care** | `ROLE_CLINICIAN` | ALL | E-prescription orders | `S16: ROUTINE_CARE` | Drug allergy & interaction checker | Confirms discharge & follow-up calendar | `S25: OUTCOME_PENDING` | Drug-allergy hard block | `ROUTINE_DISCHARGE_SIGNED` | Routine Discharge Pack (Report 3) | Phase 11 |
| **17** | **Pathway B: Further Review** | `ROLE_CLINICIAN` | ALL | Lab orders & return date | `S17: FURTHER_REVIEW` | Calendar revisit slot allocator | Books single revisit within $\le 7$ days | `S25: OUTCOME_PENDING` | Revisit window cap ($\le 7$ days) | `REVISIT_SCHEDULED` | Targeted Revisit Appointment Slip | Phase 11 |
| **18** | **Pathway C: Ward Admission** | `ROLE_CLINICIAN` | `ENV_GOV_HOSPITAL` | Target ward & diagnosis | `S18: WARD_REQUESTED` | Automated Dossier Assembler | Orders inpatient ward admission | `S19: WARD_ADMITTED` | Physical bed allocation check | `WARD_ADMISSION_ORDERED` | Inpatient Ward Dossier (Report 4) | Phase 11 |
| **19** | **Ward SBAR Handoff** | `ROLE_NURSE` & `ROLE_CLINICIAN` | `ENV_GOV_HOSPITAL` | SBAR checklist items | `S19: WARD_ADMITTED` | Inpatient monitoring mode switcher | Dual sign-off of transferring/ward staff | `S25: OUTCOME_PENDING` | Two-party signature mandate | `WARD_HANDOFF_VERIFIED` | Signed Inpatient SBAR Record | Phase 11 |
| **20** | **Pathway D: Referral Transfer** | `ROLE_CLINICIAN` | `ENV_PHC` | Destination hospital choice | `S20: REFERRAL_PENDING` | Regional facility capability ranker | Authorizes inter-facility transfer | `S21: TRANSFER_IN_TRANSIT` | Anti-Blind-Transfer confirmation gate | `REFERRAL_DISPATCH_CONFIRMED` | Digital Referral Pack (Report 2) | Phase 10 |
| **21** | **Ambulance In-Transit Handoff** | Paramedic & Receiving Doctor | Corridor | En-route vitals / QR scan | `S21: TRANSFER_IN_TRANSIT` | In-transit deterioration alert | Handoff executed at receiving casualty | `S25: OUTCOME_PENDING` | Transport departure/arrival sign-off | `TRANSFER_HANDOFF_SEALED` | In-Transit Care & Intake Log | Phase 10 |
| **22** | **Pathway E: Emergency Resuscitation**| Emergency Doctor / Nurse | ALL | 30s ABCD vitals | `S22: EMERGENCY_ACTIVE` | Deterministic Red-Flag Rules | Immediate hands-on resuscitation | `S18` / `S20` / `S23` | Resuscitation monopoly (Admin locked) | `EMERGENCY_FAST_TRACK_LOGGED` | Emergency Report (Report Type 5) | Phase 8 |
| **23** | **Pathway F: OT Fast-Track** | Operating Surgeon | `ENV_GOV_HOSPITAL` | Surgical indication, NPO | `S23: OT_PENDING` | Surgical dossier compiler | Books emergent operation theatre | `S24: OT_HANDOFF` | Surgeon credential authorization | `SURGICAL_PROCEDURE_BOOKED` | Pre-Op Surgical Dossier | Phase 11 |
| **24** | **WHO Surgical Sign In** | Surgeon & Anesthesiologist | `ENV_GOV_HOSPITAL` | WHO Surgical Safety checklist | `S24: OT_HANDOFF` | Intra-op safety checklist verifier | Dual sign-off before anesthesia | `S25: OUTCOME_PENDING` | Mandatory surgical site mark check | `WHO_SIGN_IN_VERIFIED` | OT Operative Report (Report Type 6)| Phase 11 |
| **25** | **Clinical Outcome Logging** | `ROLE_CLINICIAN` / `ROLE_NURSE` | ALL | Outcome category selection | `S26: RESOLVED` | Delta calculator & concordance scorer | Records verified clinical endpoint | `S27: CLOSED` | Adverse event audit prompt | `CLINICAL_OUTCOME_RECORDED` | Clinical Endpoint Record | Phase 12 |
| **26** | **Encounter Seal & Archive** | `ROLE_SYSTEM_AI` | ALL | Audit ledger hashes | `S27: CLOSED` | SHA-256 Merkle root sealer | Finalizes and locks Master Case | Sealed (Terminal) | Immutability lock (Zero post edits) | `CASE_CRYPTOGRAPHICALLY_SEALED`| Sealed Invariant Case Archive | Phase 12 |
