# CLINOVA AI — Phase 6 Formal Architectural Decision Log

> **Document ID:** `DECISION-LOG-PHASE-6`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Governance & Architectural Rationale

The Phase 6 Decision Log codifies the definitive architectural, clinical, and data engineering resolutions reached during the canonical data model specification.

Every decision is grounded in:
1. **Clinical Safety & Legal Compliance:** NMC Regulations 2023, DPDP Act 2023, Indian Evidence Act Section 65B.
2. **Mathematical Precision & Immutability:** Merkle hash chaining, finite state machine transition guarantees, and zero imputation.
3. **Operational Robustness:** Flawless execution on edge Mini-PCs (SQLite WAL) with seamless central synchronization (PostgreSQL).

---

## 2. Definitive Phase 6 Decisions (Decisions 6.1 – 6.12)

---

### Decision 6.1: The Single Canonical Identifier Invariant (`case_id`)
- **Context:** Fragmenting patient records across intake, nursing vitals, doctor notes, referral letters, and ward charts leads to lost clinical context, overlooked drug allergies, and medical errors.
- **Decision:** Every patient encounter is governed by exactly ONE immutable primary key: `case_id` ($\text{UUIDv4}$). All 17 sub-systems (audio, OCR crops, vitals, timeline, triage note, clinician review, referral, ward, OT, outcomes, audit) hold foreign keys pointing directly to `cases(id)`.
- **Safety Boundary:** Spawning secondary or disconnected clinical cases for the same care episode is structurally prohibited by database foreign key constraints.

---

### Decision 6.2: Decoupling of Identity, Encounter, Case, Facility, and Actor
- **Context:** Requiring full government identity (Aadhaar/ABHA) before emergency care kills trauma patients, while conflating patient identity with a single visit prevents longitudinal tracking.
- **Decision:** Enforced a strict 5-way relational decoupling: `patients` (biological person), `encounters` (facility visit boundary), `cases` (clinical condition and trajectory graph), `facilities` (institution), and `users` (human staff or daemon).
- **Safety Boundary:** Emergency anonymous patients are instantly provisioned ($< 200\text{ms}$) with an `EMG-YYYYMMDD-XXXX` token without mandatory demographic fields. Post-stabilization identity discovery binds the token to verified identity via `identity_link_events` without losing historical data.

---

### Decision 6.3: Relational Modeling of 27 Canonical States with Optimistic Locking
- **Context:** The Phase 5 state machine contains 27 discrete states. If concurrent clinical users mutate state without concurrency control, data will be lost or race conditions will occur.
- **Decision:** Mapped all 27 canonical states into `case_state_transitions`. The root `cases` record tracks `current_state`, `previous_state`, and an integer `state_version` counter implementing atomic compare-and-swap Optimistic Concurrency Control (OCC).
- **Safety Boundary:** Transition history is append-only. Terminal state `STATE_CLOSED` is an absorbing state that permanently locks the case.

---

### Decision 6.4: Cryptographic Append-Only Event Sourcing over In-Place Updates
- **Context:** Destructive updates to clinical databases prevent medicolegal auditability and violate Section 65B of the Indian Evidence Act.
- **Decision:** Established an append-only event sourcing ledger (`case_events`). Every clinical mutation writes an immutable row with a SHA-256 cryptographic link:
  $$H_n = \text{SHA256}(H_{n-1} \parallel \text{event\_id} \parallel \text{timestamp} \parallel \text{payload})$$
- **Safety Boundary:** Triggers prohibit `UPDATE` and `DELETE` queries on event tables. Tampering invalidates the cryptographic Merkle chain.

---

### Decision 6.5: Explicit Epistemic States and Conflict Persistence without Silent Overwriting
- **Context:** When patient self-report contradicts physical nurse measurement (e.g. reported BP normal vs measured BP 190/110), standard systems overwrite the first entry, losing evidence of non-compliance.
- **Decision:** Clinical parameters are categorized across eight source types and six epistemic states (`KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`, `INFERRED`). Contradictory values are BOTH preserved in `evidence_records` and surfaced in `evidence_conflicts`.
- **Safety Boundary:** Silent overwriting is prohibited. Clinicians must explicitly adjudicate active values on the review workbench.

---

### Decision 6.6: Bi-directional Visual and Acoustic Provenance Grounding
- **Context:** Frontline clinicians under intense OPD time pressure cannot trust "black-box" AI entity extractions without verifying the raw text or image.
- **Decision:** Every extracted entity in `ocr_extracted_snippets` maintains spatial bounding boxes $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$ linking to the original document image crop. Every transcribed entity in `audio_transcripts` maintains word timestamp offsets linking to the raw audio recording.
- **Safety Boundary:** Unverified extractions carry a mandatory provenance label and direct visual hyperlink on the review workbench.

---

### Decision 6.7: Relational Enforcement of Zero-Imputation Law and Sufficiency Gate ($S \ge 0.85$)
- **Context:** Treating blank physiological inputs as normal causes high-risk decompensating patients to be overlooked.
- **Decision:** Absence of evidence is NEVER evidence of absence. Missing parameters are stored as `missing_information_items` with status `UNKNOWN`. The database evaluates mathematical sufficiency:
  $$S = \frac{\sum w_i \cdot \delta_i}{\sum w_i} \ge 0.85$$
- **Safety Boundary:** If $S < 0.85$ or any Tier 1 vital sign is `UNKNOWN`, the state machine hard-blocks promotion to the doctor queue and diverts the case to the Nurse Missing-Data Worklist.

---

### Decision 6.8: Decoupled 3-Axis Clinical Representation (Risk, Trajectory, Uncertainty)
- **Context:** Collapsing clinical condition into a single scalar score blinds clinicians to rapidly deteriorating low-baseline patients and confuses data gaps with clinical health.
- **Decision:** The data model strictly separates:
  1. Risk Score / Level: `LOW`, `MODERATE`, `HIGH`, `CRITICAL` (physiological hazard).
  2. Trajectory: `IMPROVING`, `STABLE`, `DETERIORATING`, `RAPIDLY_DETERIORATING`, `UNCERTAIN` (slope over time).
  3. Uncertainty Score / Level: `LOW`, `MODERATE`, `HIGH`, `CRITICAL_UNCERTAINTY` (epistemic data gaps).
- **Safety Boundary:** High uncertainty ($U_t > 0.50$) automatically elevates triage priority to prevent dangerous waiting-room delays.

---

### Decision 6.9: Advisory Orchestration Boundary with Mandatory Non-Destructive Modifications
- **Context:** Autonomous AI disposition systems violate NMC regulations. Conversely, doctor edits that erase AI recommendations prevent quality audits.
- **Decision:** The Orchestration Engine output (`orchestration_recommendations`) carries mandatory `human_review_required = TRUE`. When a clinician edits a suggestion, `clinician_modifications` preserves the original AI recommendation, the doctor's override, and the medical justification.
- **Safety Boundary:** AI is strictly non-prescriptive. Doctors retain total decision authority.

---

### Decision 6.10: Closed-Loop Referral and Transfer Logistics Architecture
- **Context:** Blind referrals cause patients to die during transit or upon arrival at saturated hospitals.
- **Decision:** Referrals model the complete physical transfer lifecycle in `referrals`, including $\text{FACILITYGRAPH}$ capacity pre-locking, pre-departure digital SBAR pack transmission, en-route serial monitoring in `transfer_transit_logs`, and zero-reentry reception at the receiving hospital.
- **Safety Boundary:** Hospital rejections automatically trigger alternative facility recalculation.

---

### Decision 6.11: Dual SQLite WAL / PostgreSQL Cross-Dialect Engine Compatibility
- **Context:** Remote clinics operate on local Mini-PCs without internet, while regional hospitals use cloud clusters. Codebases that bifurcate between engines create unmaintainable drift.
- **Decision:** All tables are specified in dual-compatible DDL. Local nodes run SQLite 3.45+ in WAL mode (`PRAGMA journal_mode = WAL`, `PRAGMA foreign_keys = ON`). Central hubs run PostgreSQL 15+ / Supabase. Universal RFC 4122 `UUIDv4` identifiers eliminate primary key sync collisions.
- **Safety Boundary:** No engine-specific extensions that break portable execution are permitted.

---

### Decision 6.12: Statutory Medico-Legal Retention and Cryptographic Archival Sealing
- **Context:** Blanket consumer data erasure rules conflict with Indian statutory health record preservation laws.
- **Decision:** Implemented `data_retention_policies` enforcing statutory periods (3 years for outpatient, 7 years for surgical/MLC, pediatric records until age 21). Sealed cases in `archived_cases` receive a cryptographic Merkle root hash lock.
- **Safety Boundary:** Legal hold flags (`is_legal_hold = TRUE`) permanently lock records against purging during ongoing litigation.
