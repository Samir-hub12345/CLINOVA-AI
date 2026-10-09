# CLINOVA AI — Phase 7 Formal Architectural Decision Log

> **Document ID:** `DECISION-LOG-PHASE-7`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Governance & Architectural Rationale

The Phase 7 Decision Log codifies the definitive architectural, clinical, and data engineering resolutions governing evidence provenance, perceptual grounding, conflict persistence, and epistemic uncertainty in CLINOVA AI.

Every decision is grounded in:
1. **Statutory Indian Compliance:** National Medical Commission (NMC) Regulations 2023, Bharatiya Sakshya Adhiniyam (BSA) 2023 (Section 63), and Digital Personal Data Protection (DPDP) Act 2023.
2. **Mathematical Invariance & Epistemic Safety:** Strict rejection of silent overwriting, formal decoupling of uncertainty ($U_t$) from risk ($R_t$), and immutable Merkle hash chaining.
3. **Clinical Reality in Low-Resource Settings:** Resilient operation across rural PHCs, outreach health camps, and edge Mini-PCs under bandwidth constraints and ambient noise.

---

## 2. Definitive Phase 7 Decisions (Decisions 7.1 – 7.16)

---

### Decision 7.1: Strict Decoupling of Source Class from Clinical Truth
- **Context:** In conventional EHRs, data source is either ignored or assumed to guarantee truth (e.g. staff entries treated as infallible, patient statements dismissed as noise).
- **Decision:** Formally established that $\text{Source Class } S \neq \text{Objective Truth } \Omega$. Every datum is categorized across eight canonical source types (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `CLINICIAN_VERIFIED`, `STAFF_ENTERED`, `AI_INFERRED`, `SYSTEM_DERIVED`, `EXTERNAL_RECORD`) without prejudging its absolute accuracy.
- **Safety Boundary:** Source class dictates legal attribution and review tier; it never grants automatic truth status.

---

### Decision 7.2: The Absolute Law of $\text{INFERRED} \neq \text{VERIFIED}$
- **Context:** AI models frequently produce plausible clinical deductions that unguided junior staff accept as facts.
- **Decision:** Mandated that under no operational, technical, or emergency circumstance can an AI inference transition to `VERIFIED` autonomously. `VERIFIED` requires an explicit, authenticated affirmative attestation by an RMP registered on the National Medical Register.
- **Safety Boundary:** Enforced via database table check constraint `chk_ai_never_self_verified`.

---

### Decision 7.3: Complete Nine-Stage Provenance Chain & Media Pointer Model
- **Context:** Storing raw binary files (audio recordings, high-res scans) inside relational databases causes severe bloating, locking SQLite WAL threads on edge devices.
- **Decision:** Enforced complete nine-stage lineage (`RAW SOURCE` $\to$ `INGESTION` $\to$ `TRANSFORMATION` $\to$ `EXTRACTION` $\to$ `NORMALIZATION` $\to$ `VERIFICATION` $\to$ `CLINICAL USE` $\to$ `DECISION` $\to$ `OUTCOME`). Raw binaries are stored on filesystem/object storage; relational tables store immutable URI pointers, SHA-256 hashes, and offsets.
- **Safety Boundary:** Zero binary BLOBs inside relational evidence records; relational integrity maintained via cryptographic checksums.

---

### Decision 7.4: Normalized Spatial Bounding Boxes $[0, 1000]$ for OCR Extractions
- **Context:** OCR extractions lose meaning if the doctor cannot verify them against the physical paper slip.
- **Decision:** Every OCR field preserves normalized bounding box coordinates $[y_{\min}, x_{\min}, y_{\max}, x_{\max}] \subset [0, 1000]^2$, enabling instant side-by-side cropped preview on the Doctor Workbench across responsive screen sizes.
- **Safety Boundary:** No OCR extraction may enter the active patient chart without a spatial bounding box link.

---

### Decision 7.5: Word-Level Timecode Alignment & Acoustic Distinguishability for Voice
- **Context:** Voice transcriptions frequently drop critical words (such as negation particles), risking catastrophic misinterpretation.
- **Decision:** Audio transcripts are stored with word-level timecode boundaries $[t_{\text{start}}, t_{\text{end}}]$, acoustic confidence scores, and speaker diarization tags. The raw audio recording remains permanently distinguishable from the machine transcript.
- **Safety Boundary:** Tapping any symptom streams the exact 3-second audio snippet; human corrections preserve the original acoustic hypothesis in `audio_transcript_corrections`.

---

### Decision 7.6: Non-Destructive Conflict Persistence over Silent Overwriting
- **Context:** When patient self-report contradicts physical nurse measurement (e.g. SBP 120 vs 195 mmHg), traditional systems overwrite the earlier record, concealing vital clinical insight.
- **Decision:** Prohibited destructive updates. All contradictory values remain permanently stored in `evidence_records`, linked in `evidence_conflicts`, and presented side-by-side for clinician adjudication.
- **Safety Boundary:** Database triggers reject in-place updates; conflict records remain active until resolved by an authenticated RMP.

---

### Decision 7.7: The Safety-Pessimistic Principle for Conflicting Physiological Data
- **Context:** While a conflict is awaiting physician review, downstream risk engines need to know how to score patient acuity.
- **Decision:** Established the Safety-Pessimistic Principle: the highest-acuity conflicting value acts as a protective tripwire for emergency triage monitoring **without declaring it clinically verified**.
- **Safety Boundary:** Protects patients from waiting-room deterioration while upholding diagnostic truth.

---

### Decision 7.8: Five-Axis Decoupling of Reliability
- **Context:** Collapsing data quality, model confidence, human verification, provenance, and source into a single score leads to opaque, unsafe decisions.
- **Decision:** Decoupled reliability into five independent orthogonal dimensions: **Source Modality**, **Provenance Lineage**, **Physical Signal Quality ($Q$)**, **Calibrated Model Confidence ($C$)**, and **Human Verification Status ($\mathcal{V}$)**.
- **Safety Boundary:** Prohibited fabricated probability claims; required temperature scaling / Platt calibration (ECE $< 0.05$).

---

### Decision 7.9: Mathematical Formulation of Case Epistemic Uncertainty ($U_t$)
- **Context:** Epistemic uncertainty was defined conceptually in Phase 6; Phase 7 requires an explicit mathematical formulation.
- **Decision:** Formulated $U_t \in [0, 1]$ as the normalized weighted sum of eight concrete evidence gaps (missing Tier 1 vitals, active conflicts, low-quality OCR, low SNR audio, stale records, unverified text, incomplete timeline, unavailable labs).
- **Safety Boundary:** Reaffirmed that **Uncertainty $\neq$ Risk Severity**; high uncertainty constrains automated pathways and prompts human re-check.

---

### Decision 7.10: Physiological Volatility Windows & Multi-Clock Temporal Decoupling
- **Context:** Treating a single server timestamp `created_at` as clinical truth causes fatal delays and invalidates legal chain of custody.
- **Decision:** Mandated five distinct temporal clocks: **Event Time**, **Capture Time**, **Ingestion Time**, **Verification Time**, and **Decision Time**. Stratified evidence into five volatility tiers with explicit stale and expired thresholds.
- **Safety Boundary:** Trajectory models must ALWAYS plot against Event Time; audit ledgers must verify Ingestion Time.

---

### Decision 7.11: Transformation Lineage & Reversibility Taxonomy
- **Context:** Complex NLP pipelines and translations hide the original source phrasing, introducing clinical errors.
- **Decision:** Mandated that every transformation records input, output, transformer engine, version, and reversibility class (`FULLY_REVERSIBLE`, `PARTIALLY_REVERSIBLE`, `IRREVERSIBLE`).
- **Safety Boundary:** Transformed concepts must never conceal the original text; raw inputs are permanently inspectable.

---

### Decision 7.12: Physician Monopoly over Clinical Dispositions under NMC Regulation 27
- **Context:** Commercial healthcare AI often blurs the line between clinical advice and autonomous prescription or diagnosis.
- **Decision:** Reaffirmed that under NMC Regulations 2023 (Regulation 27), the system hard-blocks AI models from autonomously creating formal diagnoses, drug prescriptions, ward admissions, surgical bookings, or patient discharges.
- **Safety Boundary:** AI is strictly advisory; doctor overrides are non-destructively preserved in `clinician_modifications`.

---

### Decision 7.13: Deterministic Invalidation & Re-Derivation of System Scores
- **Context:** Clinical scores like NEWS2 or Shock Index frozen in databases remain active even after their underlying vitals are found to be typos.
- **Decision:** System-derived calculations are modeled as reactive projections of an evidence vector. Any mutation to an input vital automatically marks the derived score as superseded and triggers real-time re-derivation.
- **Safety Boundary:** A derived value is never treated as independent raw clinical evidence.

---

### Decision 7.14: Post-Purge Cryptographic Hash Preservation under DPDP Act 2023
- **Context:** Storing raw audio files indefinitely violates the DPDP Act 2023 (storage limitation), but deleting files risks breaking legal evidence chains under BSA 2023.
- **Decision:** Formulated the `HASH_ONLY` state transition. When raw media is purged after 90 days, its SHA-256 hash, extracted text, and verification metadata remain permanently intact.
- **Safety Boundary:** The UI clearly states media is purged; post-purge provenance never falsely implies media is playable.

---

### Decision 7.15: Offline Edge RFC 4122 UUIDv4 and Append-Only Synchronization Journals
- **Context:** Disconnected rural edge tablets risk ID collisions and data clobbering upon network reconnection.
- **Decision:** Edge devices generate RFC 4122 UUIDv4 identifiers locally and log mutations in append-only `sync_journals`. Synchronization preserves edge capture timestamps and resolves clinical conflicts via `APPEND_ONLY` or `CLINICIAN_WINS`.
- **Safety Boundary:** A sync event must never make provenance ambiguous or overwrite edge timestamps.

---

### Decision 7.16: Evidentiary Certification under Section 63 Bharatiya Sakshya Adhiniyam 2023
- **Context:** Earlier documentation cited obsolete statutory references (Section 65B of Indian Evidence Act, 1872).
- **Decision:** Formally updated all legal terminology to Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (BSA 2023). Implemented append-only Merkle hash chaining ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$) to guarantee forensic admissibility.
- **Safety Boundary:** Modernized statutory citations; guaranteed unalterable legal chain-of-custody.
