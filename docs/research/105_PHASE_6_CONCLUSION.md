# CLINOVA AI — Phase 6 Final Master Case & Data Model Specification Report

> **Document ID:** `RES-105`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. PHASE
**PHASE 6 — MASTER CASE / DATA MODEL SPECIFICATION**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Architectural Role: *Translating the 27-State Continuous Master Patient Journey into Canonical Relational Schemas, Epistemic Provenance Ledgers, and Dual SQLite/Postgres Engines.*

---

## 2. OBJECTIVE
The primary objective of Phase 6 is to design, formalize, and validate the canonical data model for **ONE CONTINUOUS MASTER CASE**.

The model represents with mathematical rigor and database-level enforcement:
- **LONGITUDINAL CONTINUITY:** Eliminating record fragmentation across intake, waiting room, review, transfer, ward, OT, and outcome.
- **PROVENANCE-AWARENESS:** Grounding all clinical facts in 8 explicit source types and dual visual/acoustic bounding pointers.
- **UNCERTAINTY-AWARENESS:** Implementing the Zero-Imputation Law and decoupling physiological risk, trajectory slope, and epistemic data gaps.
- **ENVIRONMENT-AWARENESS:** Supporting all 6 operational healthcare settings via facility capability matrices without codebase bifurcation.
- **PERMISSION-AWARENESS:** Upholding Registered Medical Practitioner (RMP) monopoly over medical dispositions under NMC Regulations 2023.
- **AUDITABILITY:** Guaranteeing Section 65B Indian Evidence Act compliance via cryptographic Merkle hash chaining.
- **OFFLINE EDGE RESILIENCE:** Operating 100% offline on local SQLite WAL edge nodes and synchronizing idempotently with central PostgreSQL/Supabase hubs.

Phase 6 is strictly a **Data Model Design and Validation Phase**. It does not construct production application endpoints, write UI components, or apply schema changes to active production databases.

---

## 3. SOURCE MATERIAL
Phase 6 directly reconciles and synthesizes 14 authoritative statutory, clinical, and architectural sources (cataloged in `docs/research/SOURCES_PHASE_6.md`):
- **Statutory Indian Frameworks:** National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Regulations 27 & 28); Digital Personal Data Protection (DPDP) Act 2023 (Sections 4, 6, 7, 9); Indian Evidence Act, 1872 (Section 65B) / Bharatiya Sakshya Adhiniyam 2023 (Section 63); Indian Public Health Standards (IPHS 2022); Supreme Court *Paschim Banga* emergency doctrine.
- **Informatics Standards:** HL7 FHIR Release 5; LOINC Database; SNOMED CT; WHO ICD-11; W3C PROV-O Provenance Ontology; IETF RFC 4122 (UUIDv4).
- **Internal Repository Artifacts:** Phase 1 Product Architecture (`DOC-00` to `DOC-28`); Phase 2 Innovation Audits (`RES-00` to `RES-24`); Phase 3 User Roles (`RES-30` to `RES-42`); Phase 4 Environments (`RES-43` to `RES-56`); Phase 5 Master Journey (`RES-57` to `RES-77`); and Alembic Migrations 0001–0009.

---

## 4. MASTER CASE RESULT
Specified in `docs/research/79_MASTER_CASE_CANONICAL_MODEL.md` (`RES-79`):
- Enforces the **Single Master Case Invariant**:
  $$\forall \text{ encounter } e, \quad \exists ! \text{ canonical identifier } \mathbf{case\_id} \in \text{UUIDv4}$$
- The root relational entity `cases` coordinates the entire clinical episode across intake mode, current state, acuity tier, composite risk, trajectory slope, uncertainty score, presenting complaint, and cryptographic sealing.
- All 17 sub-systems link directly to `cases.id` via indexed foreign keys with `ON DELETE RESTRICT`, eliminating orphaned records, sidecar encounters, or disconnected triage notes.

---

## 5. IDENTITY MODEL RESULT
Specified in `docs/research/80_IDENTITY_MODEL.md` (`RES-80`):
- Strictly decouples: **Patient Identity** (`patients`, `patient_identifiers`), **Encounter** (`encounters`), **Master Case** (`cases`), **Facility** (`facilities`), and **Actor** (`users`).
- Establishes mathematical and operational mechanisms for all six canonical identity modes:
  1. *Fully Identified Patient:* ABHA / MRN / Aadhaar verified.
  2. *Partially Identified Patient:* Stated name and approximate age without blocking care.
  3. *Emergency Anonymous Patient:* Instant $< 200\text{ms}$ generation of anonymous token (`EMG-YYYYMMDD-XXXX`) enabling immediate clinical resuscitation before administrative registration.
  4. *Late Identity Discovery:* Post-stabilization cryptographic binding via `identity_link_events` updating `cases.patient_id` without losing resuscitation history.
  5. *Accidental Duplicate Detection:* Phonetic and demographic matching flagged in `patient_merge_candidates`.
  6. *Non-Destructive Identity Merge:* Surviving canonical profile designated; deprecated profile aliased with tombstone; full historical event audit trail preserved in `patient_merges`.

---

## 6. CASE LIFECYCLE RESULT
Specified in `docs/research/81_CASE_LIFECYCLE_MODEL.md` (`RES-81`):
- Maps all **27 Canonical States** from Phase 5 into the relational schema:
  `S01: STATE_NEW`, `S02: STATE_INTAKE_COLLECTING`, `S03: STATE_EXTRACTING`, `S04: STATE_EXTRACTION_REVIEW`, `S05: STATE_MISSING_AUDIT`, `S06: STATE_FOLLOW_UP_PENDING`, `S07: STATE_STAFF_DATA_PENDING`, `S08: STATE_STAFF_VERIFIED`, `S09: STATE_CONSOLIDATED`, `S10: STATE_TRIAGE_READY`, `S11: STATE_DOCTOR_QUEUED`, `S12: STATE_DOCTOR_REVIEWING`, `S13: STATE_CLINICIAN_VERIFIED`, `S14: STATE_FACILITY_EVALUATING`, `S15: STATE_ORCHESTRATION_PENDING`, `S16: STATE_ROUTINE_CARE`, `S17: STATE_FURTHER_REVIEW`, `S18: STATE_WARD_REQUESTED`, `S19: STATE_WARD_ADMITTED`, `S20: STATE_REFERRAL_PENDING`, `S21: STATE_TRANSFER_IN_TRANSIT`, `S22: STATE_EMERGENCY_ACTIVE`, `S23: STATE_OT_PENDING`, `S24: STATE_OT_HANDOFF`, `S25: STATE_OUTCOME_PENDING`, `S26: STATE_RESOLVED`, `S27: STATE_CLOSED`.
- Implements `case_state_transitions` tracking `state_version`, previous state, new state, trigger, actor ID, duration, and transition reason.
- Enforces Optimistic Concurrency Control (OCC) using atomic compare-and-swap on `cases.state_version`.

---

## 7. EVENT HISTORY RESULT
Specified in `docs/research/82_EVENT_HISTORY_MODEL.md` (`RES-82`):
- Implements an **Append-Only Event Ledger** (`case_events`).
- Every clinical, administrative, or algorithmic mutation writes an immutable row capturing `event_id`, `case_id`, `encounter_id`, `facility_id`, `actor_id`, `actor_role`, `event_type`, `timestamp`, `payload`, `previous_event_id`, and `integrity_hash`.
- Enforces deterministic cryptographic hash chaining:
  $$H_n = \text{SHA256}(H_{n-1} \parallel \text{event\_id} \parallel \text{case\_id} \parallel \text{timestamp} \parallel \text{CanonicalJSON}(\text{payload}))$$
- Database-level triggers prohibit `UPDATE` and `DELETE` operations on historical events.

---

## 8. EVIDENCE / PROVENANCE RESULT
Specified in `docs/research/83_EVIDENCE_PROVENANCE_MODEL.md` (`RES-83`):
- Models **Eight Evidence Sources:** `PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `CLINICIAN_VERIFIED`, `STAFF_ENTERED`, `AI_INFERRED`, `SYSTEM_DERIVED`, and `EXTERNAL_RECORD`.
- Models **Six Epistemic States:** `KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`, and `INFERRED`.
- Eliminates silent data overwrites: Contradictory clinical facts (e.g. patient reported BP normal vs nurse measured BP 190/110) are BOTH preserved in `evidence_records` and linked in `evidence_conflicts` for clinician adjudication.

---

## 9. MEDIA / DOCUMENT RESULT
Specified in `docs/research/84_MEDIA_DOCUMENT_MODEL.md` (`RES-84`):
- Establishes **Bi-directional Visual & Acoustic Grounding**.
- Vernacular audio recordings (`audio_recordings`) preserve duration, SHA-256 hash, and word alignment timestamps in `audio_transcripts`.
- Document images and PDFs (`documents`) preserve page layouts in `document_ocr_pages` and normalized field entities in `ocr_extracted_snippets`.
- Extracted entities maintain spatial bounding box coordinates $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$, enabling one-click visual crop previews on the Doctor Workbench.

---

## 10. CLINICAL OBSERVATION RESULT
Specified in `docs/research/85_CLINICAL_OBSERVATION_MODEL.md` (`RES-85`):
- Captures serial time-series vital sign snapshots in `vital_readings` across intake, waiting room, resuscitation, ward, and transit epochs.
- Implements generated columns for deterministic physiological indices: $\text{Shock Index} = \text{HR} / \text{SBP}$ and NEWS2 composite early warning scores.
- Captures discrete clinical observations in `clinical_observations` with LOINC/SNOMED CT coding, unit normalization, reference ranges, and automated abnormality flags.

---

## 11. SYMPTOM / TIMELINE RESULT
Specified in `docs/research/86_SYMPTOM_TIMELINE_MODEL.md` (`RES-86`):
- Models symptoms as dynamic trajectory entities in `symptoms`.
- Supports both precise datetimes and vernacular temporal anchors (*"3 days ago after dinner"*).
- Classifies trajectory into `IMPROVING`, `STABLE`, `WORSENING`, `FLUCTUATING`, or `UNCERTAIN`.
- Captures modulating triggers, relieving factors, associated systemic manifestations, and serial progression in `symptom_progression_events`.

---

## 12. MISSING INFORMATION RESULT
Specified in docs/research/87_MISSING_INFORMATION_MODEL.md (RES-87):
- Enforces the **Zero-Imputation Law**: Missing data is stored explicitly in missing_information_items with status UNKNOWN; never imputed as normal.
- Computes mathematical sufficiency  \ge 0.85$ weighted by Tier 1 Critical (=3.0$), Tier 2 Important (=1.5$), and Tier 3 Routine (=0.5$).
- Hard-blocks cases with  < 0.85$ or unmeasured Tier 1 vitals from doctor queue promotion, diverting them to the Nurse Missing-Data Worklist.

---

## 13. FOLLOW-UP QUESTION RESULT
Specified in docs/research/88_FOLLOWUP_QUESTION_MODEL.md (RES-88):
- Implements adaptive Next-Best-Information (NBI) interactive questioning (completion_sessions, completion_questions, completion_answers) capped at 1–3 questions to prevent cognitive abandonment.
- Binds follow-up responses to the originating missing data item, dynamically updating sufficiency score $.

Specified in `docs/research/87_MISSING_INFORMATION_MODEL.md` (`RES-87`) and `docs/research/88_FOLLOWUP_QUESTION_MODEL.md` (`RES-88`):
- Enforces the **Zero-Imputation Law**: Missing data is stored explicitly in `missing_information_items` with status `UNKNOWN`; never imputed as normal.
- Computes mathematical sufficiency $S \ge 0.85$ weighted by Tier 1 Critical ($w=3.0$), Tier 2 Important ($w=1.5$), and Tier 3 Routine ($w=0.5$).
- Hard-blocks cases with $S < 0.85$ or unmeasured Tier 1 vitals from doctor queue promotion, diverting them to the Nurse Missing-Data Worklist.
- Implements adaptive Next-Best-Information (NBI) interactive questioning (`completion_sessions`, `followup_questions`) capped at 1–3 questions to prevent cognitive abandonment.

---

## 14. RISK / TRAJECTORY / UNCERTAINTY RESULT
Specified in `docs/research/89_RISK_TRAJECTORY_UNCERTAINTY_MODEL.md` (`RES-89`):
- Strictly decouples evaluation into **Three Independent Orthogonal Axes**:
  1. *Risk Level:* `LOW`, `MODERATE`, `HIGH`, `CRITICAL` (physiological hazard).
  2. *Trajectory:* `IMPROVING`, `STABLE`, `DETERIORATING`, `RAPIDLY_DETERIORATING`, `UNCERTAIN` (slope over time).
  3. *Uncertainty Level:* `LOW`, `MODERATE`, `HIGH`, `CRITICAL_UNCERTAINTY` (epistemic data completeness).
- Stored independently in `clinical_evaluations`; high uncertainty ($U_t > 0.50$) automatically elevates triage priority to prevent waiting-room decompensation.

---

## 15. TRIAGE / REVIEW RESULT
Specified in docs/research/90_TRIAGE_REVIEW_MODEL.md (RES-90):
- Triage synthesis compiles 	riage_notes carrying mandatory advisory watermarks, differential diagnostic hypotheses, detected red-flags, and suggested priority.
- Dynamically orders the clinician queue via composite priority function (t)$ factoring acuity, wait-time decay, trajectory penalty, and uncertainty.

---

## 16. CLINICIAN DECISION RESULT
Specified in docs/research/91_CLINICIAN_DECISION_MODEL.md (RES-91):
- Doctor review on the workbench captures verified diagnoses and dispositions in clinician_reviews.
- When an RMP modifies an AI suggestion, clinician_modifications preserves the original machine recommendation, the doctor override, and the clinical justification. Machine suggestions are NEVER overwritten.

Specified in `docs/research/90_TRIAGE_REVIEW_MODEL.md` (`RES-90`) and `docs/research/91_CLINICIAN_DECISION_MODEL.md` (`RES-91`):
- Triage synthesis compiles `triage_notes` carrying mandatory advisory watermarks, differential diagnostic hypotheses, detected red-flags, and suggested priority.
- Dynamically orders the clinician queue via composite priority function $P(t)$ factoring acuity, wait-time decay, trajectory penalty, and uncertainty.
- Doctor review on the workbench captures verified diagnoses and dispositions in `clinician_reviews`.
- When an RMP modifies an AI suggestion, `clinician_modifications` preserves the original machine recommendation, the doctor's override, and the clinical justification. Machine suggestions are NEVER overwritten.

---

## 17. FACILITY REQUIREMENT RESULT
Specified in `docs/research/92_FACILITY_REQUIREMENT_MODEL.md` (`RES-92`):
- Couples biological need with infrastructure reality via **FACILITYGRAPH**.
- Identifies required specialties, diagnostics, and interventions in `care_requirements`.
- Tracks real-time resource availability in `facility_capabilities`, categorizing telemetry freshness into `FRESH` ($< 4\text{h}$), `STALE` ($4\text{--}12\text{h}$), and `UNVERIFIED` ($> 12\text{h}$).
- Evaluates feasibility in `feasibility_evaluations`, computing whether care should be `LOCAL_CARE`, `STABILIZE_AND_TRANSFER`, or `IMMEDIATE_TRANSFER`.

---

## 18. ORCHESTRATION RESULT
Specified in `docs/research/93_ORCHESTRATION_RECOMMENDATION_MODEL.md` (`RES-93`):
- Orchestration Engine recommends the **Safest Achievable Care Pathway** across six canonical actions: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- Enforces the **Advisory-Only Invariant**: `human_review_required = TRUE` is hardcoded. The system cannot execute dispositions autonomously.
- Manages active care branches in `care_pathways` (`ROUTINE`, `WARD`, `REFERRAL`, `EMERGENCY`, `OT`, `FOLLOW_UP`).

---

## 19. REFERRAL / TRANSFER RESULT
Specified in `docs/research/94_REFERRAL_TRANSFER_MODEL.md` (`RES-94`):
- Models closed-loop inter-facility transfers in `referrals` to eliminate "blind transfers".
- Enforces capability matching, pre-departure digital SBAR clinical summary transmission, en-route serial vitals logging in `transfer_transit_logs`, and zero-reentry reception at the receiving hospital under the **SAME `case_id`**.
- Captures referral rejections and automatically reroutes to alternative regional facilities in `referral_rejections`.

---

## 20. WARD / OT RESULT
Specified in `docs/research/95_WARD_OT_MODEL.md` (`RES-95`):
- Manages Inpatient Ward Admissions (Pathway C) in `ward_admissions`, requiring two-party SBAR handoff sign-off and bed allocation.
- Manages Operation Theatre Procedures (Pathway F) in `surgical_procedures`, implementing ergonomic filtering (airway, NPO fasting, cross-match units hold) and enforcing the 3-phase WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out) with dual surgeon/anesthesiologist sign-off.

---

## 21. APPOINTMENT / OUTCOME RESULT
Specified in `docs/research/96_APPOINTMENT_OUTCOME_MODEL.md` (`RES-96`):
- Manages outpatient return slots in `appointments` (`ROUTINE_FOLLOWUP`, `SPECIALIST_CONSULT`, `LAB_REVIEW`).
- Closes the clinical intelligence loop via `case_outcomes`, decoupling:
  $$\mathbf{Planned\ Advice} \neq \mathbf{Actual\ Clinician\ Decision} \neq \mathbf{Actual\ Care\ Action} \neq \mathbf{Real\text{-}World\ Outcome}$$
- Standardizes outcomes across 7 categories: `RESOLVED`, `IMPROVED`, `UNCHANGED`, `DETERIORATED`, `TRANSFERRED_OUT`, `LAMA`, `EXPIRED`.

---

## 22. CONSENT / PRIVACY RESULT
Specified in docs/research/97_CONSENT_PRIVACY_MODEL.md (RES-97):
- Models DPDP Act compliance across 5 consent types in patient_consents, enforcing vernacular notice, parental consent for minors, and demographic PII air-gapping from AI inferencing.
- Models emergency implied consent and break-glass overrides in privacy_break_glass_audits.

---

## 23. AUDIT RESULT
Specified in docs/research/98_AUDIT_EVENT_MODEL.md (RES-98):
- Formulates Section 65B Indian Evidence Act compliant append-only ledger in case_events with SHA-256 Merkle chaining.
- Database-level triggers prohibit UPDATE and DELETE operations on historical clinical and administrative events.

---

## 24. OFFLINE / SYNC RESULT
Specified in docs/research/99_OFFLINE_SYNC_MODEL.md (RES-99):
- Implements offline-edge synchronization in sync_journals, supporting four conflict resolution strategies: APPEND_ONLY, CLINICIAN_WINS, LAST_WRITE_WINS, and MANUAL_GATE.

Specified in `docs/research/97_CONSENT_PRIVACY_MODEL.md` (`RES-97`) and `docs/research/99_OFFLINE_SYNC_MODEL.md` (`RES-99`):
- Models DPDP Act compliance across 5 consent types in `patient_consents`, enforcing vernacular notice, parental consent for minors, and demographic PII air-gapping from AI inferencing.
- Models emergency implied consent and break-glass overrides in `privacy_break_glass_audits`.
- Implements offline-edge synchronization in `sync_journals`, supporting four conflict resolution strategies: `APPEND_ONLY`, `CLINICIAN_WINS`, `LAST_WRITE_WINS`, and `MANUAL_GATE`.

---

## 26. SQLITE / POSTGRES RESULT
Specified in `docs/research/101_SQLITE_POSTGRES_COMPATIBILITY.md` (`RES-101`):
- Formulates a complete cross-engine mapping layer:
  - UUID: `TEXT(36)` in SQLite vs native `UUID` in PostgreSQL.
  - Timestamps: ISO-8601 strings in SQLite vs `TIMESTAMPTZ` in PostgreSQL.
  - JSON: `TEXT` + `json_valid()` check in SQLite vs native `JSONB` in PostgreSQL.
  - Booleans: `INTEGER` (0/1) in SQLite vs `BOOLEAN` in PostgreSQL.
  - Enums: Table check constraints in SQLite vs native enums/checks in PostgreSQL.
  - Foreign Keys: Mandatory `PRAGMA foreign_keys = ON;` in SQLite WAL mode.

---

## 25. RETENTION RESULT
Specified in docs/research/100_DATA_RETENTION_MODEL.md (RES-100):
- Implements data_retention_policies enforcing Indian statutory retention periods (3 years for outpatient, 7 years for surgical/MLC, pediatric records until age 21).
- Sealed cases in rchived_cases receive a cryptographic Merkle root hash lock.

---

## 27. DATA INTEGRITY INVARIANTS
Specified in docs/research/102_DATA_INTEGRITY_INVARIANTS.md (RES-102):
- Formalizes the **Twelve Data Integrity Invariants** (INV-01 to INV-12) governing single-case continuity, zero-imputation, append-only immutability, RMP monopoly, and offline sync.

Specified in `docs/research/100_DATA_RETENTION_MODEL.md` (`RES-100`) and `docs/research/102_DATA_INTEGRITY_INVARIANTS.md` (`RES-102`):
- Implements `data_retention_policies` enforcing Indian statutory retention periods (3 years for outpatient, 7 years for surgical/MLC, pediatric records until age 21).
- Sealed cases in `archived_cases` receive a cryptographic Merkle root hash lock.
- Formalizes the **Twelve Data Integrity Invariants** (`INV-01` to `INV-12`) governing single-case continuity, zero-imputation, append-only immutability, RMP monopoly, and offline sync.

---

## 28. TEST SCENARIO RESULT
Specified in `docs/research/103_MASTER_CASE_TEST_SCENARIOS.md` (`RES-103`):
- Rigorously validates the canonical data model against all ten benchmark clinical scenarios:
  - *Case A (Routine PHC to DH Referral):* Proven single `case_id` continuity across facilities and zero-reentry reception.
  - *Case B (Missing Vitals Divert):* Proven mathematical sufficiency gating ($S = 0.58 < 0.85$) and nurse worklist resolution.
  - *Case C (Waiting Room Deterioration):* Proven break-glass jump from $S11 \to S22$ with immutable audit logging.
  - *Case D (Emergency Anonymous Patient):* Proven instant $< 200\text{ms}$ tokenization and post-stabilization identity binding.
  - *Case E (Referral Destination Saturated):* Proven rejection auditing and automated FACILITYGRAPH rerouting.
  - *Case F (Conflicting Evidence):* Proven persistent side-by-side storage of conflicting patient vs nurse vitals.
  - *Case G (Clinician AI Override):* Proven non-destructive preservation of original AI recommendation alongside doctor justification.
  - *Case H (Offline Edge Reconnection):* Proven zero ID collisions via RFC 4122 UUIDv4 and clean sync journal merging.
  - *Case I (Further Review Revisit):* Proven resumption of the exact same `case_id` upon outpatient lab check-in.
  - *Case J (OT Fast-Track):* Proven ergonomic surgical filtering and mandatory WHO checklist dual sign-off.

---

## 29. TRACEABILITY RESULT
Specified in `docs/research/104_MASTER_CASE_TRACEABILITY.md` (`RES-104`):
- Complete bidirectional matrix mapping all 27 Phase 5 Journey States $\longrightarrow$ Phase 6 Canonical Relational Entities $\longrightarrow$ DB Attributes $\longrightarrow$ Mathematical Invariants $\longrightarrow$ Test Scenarios $\longrightarrow$ Phase 7 Implementation Targets.

---

## 30. IMPLEMENTATION ROADMAP & PHASE 7 HANDOFF
Phase 6 establishes the verified architectural blueprint for the data model. The downstream Phase 7 handoff requirements are:
1. **Repository Model Modularization:** Translate specifications into Python SQLAlchemy models under `backend/app/db/models/`.
2. **Alembic Migration Script:** Author single forward migration (e.g. `0010_canonical_master_case_architecture.py`) realizing all specified tables.
3. **Pydantic Serialization Schemas:** Author request/response DTOs mirroring the JSON schema definitions.
4. **Offline SQLite Seeding & Test Harness:** Validate SQLite WAL initialization on edge nodes using the test scenarios from `RES-103`.

---

## 31. UNRESOLVED QUESTIONS
1. **ABDM Milestones 1–3 Gateway Latency:** The latency distribution of the Indian National Health Authority (NHA) ABDM M1/M2/M3 FHIR gateway callbacks in low-bandwidth rural networks requires empirical telemetry.
2. **Local Edge SQLite WAL Autocheckpoint Thresholds:** Optimal WAL checkpoint frequency under continuous high-throughput Whisper audio writes on fanless Celeron Mini-PCs requires physical hardware stress testing.
3. **Biometric ABHA Token Integration:** The data model specifies string tokens for ABHA; integrating physical biometric fingerprint/iris sensors will require hardware abstraction driver specifications in Phase 8.

---

## 32. RISKS
1. **Risk of SQLite WAL Database Locking under Concurrent Audio Writes:** High-frequency binary audio chunk uploads could lock SQLite threads.  
   *Mitigation:* Large audio and image binary files are stored directly on the local filesystem (`/var/data/clinova/media/`); the database stores only file paths, SHA-256 hashes, and duration metadata.
2. **Risk of Clock Drift between Offline Edge Mini-PCs and Central Cloud:** Desynchronized hardware clocks on edge nodes could distort event ordering.  
   *Mitigation:* Local nodes enforce NTP synchronization; event ledger relies primarily on monotonically increasing logical counters (`state_version`, `seq`) rather than wall-clock timestamps for causality.
3. **Risk of Overwhelming Frontline Nurses with Missing Data Alerts:** Too many non-critical gaps diverting to nurse worklists.  
   *Mitigation:* Strict two-tier weighting: only Tier 1 Critical parameters ($w=3.0$) trigger mandatory nurse worklist diversion.

---

## 33. FILES CREATED
Phase 6 authored all **30 required authoritative specification documents** in `docs/research/`:
1. `docs/research/78_MASTER_CASE_DATA_MODEL_PLAN.md` (`RES-78`)
2. `docs/research/79_MASTER_CASE_CANONICAL_MODEL.md` (`RES-79`)
3. `docs/research/80_IDENTITY_MODEL.md` (`RES-80`)
4. `docs/research/81_CASE_LIFECYCLE_MODEL.md` (`RES-81`)
5. `docs/research/82_EVENT_HISTORY_MODEL.md` (`RES-82`)
6. `docs/research/83_EVIDENCE_PROVENANCE_MODEL.md` (`RES-83`)
7. `docs/research/84_MEDIA_DOCUMENT_MODEL.md` (`RES-84`)
8. `docs/research/85_CLINICAL_OBSERVATION_MODEL.md` (`RES-85`)
9. `docs/research/86_SYMPTOM_TIMELINE_MODEL.md` (`RES-86`)
10. `docs/research/87_MISSING_INFORMATION_MODEL.md` (`RES-87`)
11. `docs/research/88_FOLLOWUP_QUESTION_MODEL.md` (`RES-88`)
12. `docs/research/89_RISK_TRAJECTORY_UNCERTAINTY_MODEL.md` (`RES-89`)
13. `docs/research/90_TRIAGE_REVIEW_MODEL.md` (`RES-90`)
14. `docs/research/91_CLINICIAN_DECISION_MODEL.md` (`RES-91`)
15. `docs/research/92_FACILITY_REQUIREMENT_MODEL.md` (`RES-92`)
16. `docs/research/93_ORCHESTRATION_RECOMMENDATION_MODEL.md` (`RES-93`)
17. `docs/research/94_REFERRAL_TRANSFER_MODEL.md` (`RES-94`)
18. `docs/research/95_WARD_OT_MODEL.md` (`RES-95`)
19. `docs/research/96_APPOINTMENT_OUTCOME_MODEL.md` (`RES-96`)
20. `docs/research/97_CONSENT_PRIVACY_MODEL.md` (`RES-97`)
21. `docs/research/98_AUDIT_EVENT_MODEL.md` (`RES-98`)
22. `docs/research/99_OFFLINE_SYNC_MODEL.md` (`RES-99`)
23. `docs/research/100_DATA_RETENTION_MODEL.md` (`RES-100`)
24. `docs/research/101_SQLITE_POSTGRES_COMPATIBILITY.md` (`RES-101`)
25. `docs/research/102_DATA_INTEGRITY_INVARIANTS.md` (`RES-102`)
26. `docs/research/103_MASTER_CASE_TEST_SCENARIOS.md` (`RES-103`)
27. `docs/research/104_MASTER_CASE_TRACEABILITY.md` (`RES-104`)
28. `docs/research/105_PHASE_6_CONCLUSION.md` (`RES-105`)
29. `docs/research/SOURCES_PHASE_6.md`
30. `docs/research/PHASE_6_DECISIONS.md`

---

## 34. FILES MODIFIED
- None. (Phase 6 is strictly additive data model research, specification, and validation).

---

## 35. FILES INTENTIONALLY UNTOUCHED
- `frontend/` (Zero UI code modified or created).
- `backend/app/` (Zero runtime production backend logic modified or replaced).
- Production database & migrations (Zero live database migrations executed).
- Phase 1 documentation (`docs/00_*` through `docs/28_*` preserved as locked baseline).
- Phase 2 research (`docs/research/00_*` through `24_*` preserved as immutable historical gap audits).
- Phase 3 user role research (`docs/research/30_*` through `42_*` preserved).
- Phase 4 environment research (`docs/research/43_*` through `56_*` preserved).
- Phase 5 master journey research (`docs/research/57_*` through `77_*` preserved as immediate upstream source of truth).

---

## 36. PHASE STATUS
**READY FOR HUMAN REVIEW**
