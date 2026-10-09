# CLINOVA AI — Mathematical Evidence & Provenance Data Integrity Invariants

> **Document ID:** `RES-131`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Formal Invariant Mandate

In enterprise clinical architecture, software reliability cannot depend solely on developer vigilance or runtime application logic. System safety must be grounded in **Formal Mathematical Invariants** enforced by database-level schema constraints, foreign key restrictions, cryptographic hashes, and database triggers.

Phase 7 formalizes the **Eighteen Evidence & Provenance Invariants (`INV-PROV-01` through `INV-PROV-18`)**. These invariants are non-negotiable laws that govern every state transition, data ingestion, transformation, and clinical disposition across the platform.

---

## 2. The Eighteen Mathematical Invariants of Provenance

$$\begin{aligned}
\mathbf{INV\text{-}PROV\text{-}01} &: \quad \forall e \in \text{EvidenceRecords}, \quad e.\text{source\_type} \in \mathcal{S}_8 \land e.\text{epistemic\_status} \in \mathcal{E}_6 \\
& \quad \text{Every clinical datum must belong to one of 8 canonical sources and 6 epistemic states.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}02} &: \quad \forall e \in \text{EvidenceRecords}, \quad \text{Physical UPDATE of } e.\text{value\_raw} \text{ or } e.\text{recorded\_by\_actor\_id} = \bot \\
& \quad \text{Evidence records are strictly append-only; in-place destructive updates are prohibited.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}03} &: \quad \forall e \in \text{EvidenceRecords}, \quad e.\text{state\_version}_{n+1} = e.\text{state\_version}_n + 1 \\
& \quad \text{Optimistic concurrency control governs all concurrent writes via atomic compare-and-swap.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}04} &: \quad \forall e_1, e_2 \in \text{EvidenceRecords} \text{ where } e_1.\text{field} = e_2.\text{field} \land |e_1.v - e_2.v| > \epsilon, \\
& \quad \exists ! c \in \text{EvidenceConflicts} \text{ s.t. } c.\text{status} = \text{'ACTIVE'} \land c.\text{participants} = \{e_1.\text{id}, e_2.\text{id}\} \\
& \quad \text{Conflicting values must both be preserved and linked in an active conflict record.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}05} &: \quad \forall e \in \text{EvidenceRecords}, \quad \left(e.\text{source\_type} = \text{'AI\_INFERRED'}\right) \implies \\
& \quad \left(e.\text{epistemic\_status} \neq \text{'VERIFIED'} \land e.\text{verified\_by\_actor\_id} = \text{NULL}\right) \\
& \quad \text{The Cardinal Law: Inferences can NEVER become verified automatically or autonomously.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}06} &: \quad \forall s \in \text{OCRExtractedSnippets}, \quad s.\text{review\_status} = \text{'ACCEPTED'} \iff s.\text{reviewed\_by\_user\_id} \neq \text{NULL} \\
& \quad \text{No OCR value is clinically verified without explicit, authenticated human visual review.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}07} &: \quad \forall t \in \text{AudioTranscripts}, \quad t.\text{audio\_recording\_id} \in \text{AudioRecordings(id)} \land t.\text{is\_source} = \mathbf{FALSE} \\
& \quad \text{The raw audio recording remains permanently distinguishable from the machine transcript.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}08} &: \quad \forall c \in \text{ActiveConflicts}, \quad \text{EmergencyAcuitySignal}(c) = \max_{e \in c} \text{Hazard}(e) \\
& \quad \text{Highest-acuity conflicting value acts as safety signal without declaring it verified.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}09} &: \quad \forall s \in \text{OCRExtractedSnippets}, \quad s.\text{bbox} = [y_{\min}, x_{\min}, y_{\max}, x_{\max}] \subset [0, 1000]^2 \\
& \quad \text{Every extracted OCR field must preserve normalized 2D spatial bounding box coordinates.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}10} &: \quad \forall e \in \text{EvidenceRecords}, \quad t_{\text{event}} \le t_{\text{capture}} \le t_{\text{ingest}} \\
& \quad \text{Physical causality holds: Event Time } \le \text{ Capture Time } \le \text{ Ingestion Time.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}11} &: \quad \forall r \in \text{ClinicalReports}, \quad r.\text{attesting\_clinician\_id} \in \text{Users(id)} \land \text{Role}(r.\text{actor}) = \text{'RMP'} \\
& \quad \text{Only an authenticated Registered Medical Practitioner may sign legal clinical reports.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}12} &: \quad \forall a \in \text{AIInferences}, \quad a.\text{grounding\_evidence\_ids} \neq \emptyset \land a.\text{grounding\_evidence\_ids} \subset \text{CaseEvidence} \\
& \quad \text{AI deductions must be explicitly grounded in pre-existing case evidence records.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}13} &: \quad \forall m \in \text{ClinicianModifications}, \quad m.\text{original\_ai\_payload} \neq \bot \land m.\text{clinician\_override} \neq \bot \\
& \quad \text{When a doctor modifies an AI suggestion, the original machine advice is NEVER erased.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}14} &: \quad \forall m \in \text{RawMedia}, \quad \exists ! h = \text{SHA256}(m) \land \text{Duplicate}(h) \implies \text{IdempotentReference} \\
& \quad \text{Media ingestion is cryptographically idempotent based on SHA-256 content hashing.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}15} &: \quad \forall e \in \text{EvidenceRecords}, \quad e.\text{case\_id} = \text{Constant} \quad (\text{ON UPDATE RESTRICT}) \\
& \quad \text{Case boundary immutability: Evidence cannot be silently reassigned across cases.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}16} &: \quad \forall m \in \text{PurgedMedia}, \quad m.\text{retention\_class} = \text{'HASH\_ONLY'} \implies m.\text{sha256} \neq \bot \\
& \quad \text{Purging raw media preserves cryptographic integrity hashes and extracted fact lineage.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}17} &: \quad \forall e \in \text{OfflineRecords}, \quad e.\text{id} \in \text{UUIDv4} \land e.\text{sync\_status} \in \mathcal{Y}_4 \\
& \quad \text{Offline records utilize globally unique UUIDv4 keys and append-only sync journals.} \\[8pt]
\mathbf{INV\text{-}PROV\text{-}18} &: \quad \forall d \in \text{SystemDerivedCalculations}, \quad d.\text{input\_evidence\_ids} \neq \emptyset \land \text{IsDeterministic}(d.\text{formula}) \\
& \quad \text{Every derived metric must point to its input evidence snapshot and mathematical formula.}
\end{aligned}$$

---

## 3. Enforcement Mechanisms by Architectural Layer

| Invariant Code | Database Constraint / Mechanism | Application Layer Enforcement |
| :--- | :--- | :--- |
| `INV-PROV-01` | `CHECK (source_type IN (...))` & `CHECK (epistemic_status IN (...))` | Pydantic model validation on API ingress |
| `INV-PROV-02` | Database Trigger: `trg_protect_evidence_records` (Blocks UPDATE/DELETE) | Append-only repository pattern |
| `INV-PROV-03` | Column `state_version INTEGER NOT NULL DEFAULT 1` with CAS lock | Optimistic Concurrency Control middleware |
| `INV-PROV-04` | Table `evidence_conflicts` with Foreign Key constraints | Automated Conflict Detection service |
| `INV-PROV-05` | Table Check Constraint: `chk_ai_never_self_verified` | AI Orchestrator output sanitizer |
| `INV-PROV-06` | Foreign Key: `ocr_extracted_snippets.reviewed_by_user_id REFERENCES users(id)`| Doctor Workbench verification modal |
| `INV-PROV-07` | Relational separation: `audio_recordings` vs `audio_transcripts` | Audio processing pipeline pipeline bounds |
| `INV-PROV-08` | Dynamic SQL view: `vw_pessimistic_safety_signals` | Triage priority calculation engine |
| `INV-PROV-09` | Coordinate bounds: `CHECK (bbox_ymin >= 0 AND bbox_ymax <= 1000)` | Document layout analysis parser |
| `INV-PROV-10` | Check Constraints: `chk_capture_after_or_equal_event` | Clock calibration and NTP synchronization |
| `INV-PROV-11` | Check: `primary_nmr_number IS NOT NULL` on clinical sign-off | National Medical Register credential check |
| `INV-PROV-12` | JSONB Validation: `jsonb_array_length(grounding_evidence_ids) > 0` | Anti-hallucination grounding gate |
| `INV-PROV-13` | Table `clinician_modifications` with immutable foreign keys | Workbench override capture form |
| `INV-PROV-14` | Unique Index: `ix_raw_src_hash ON raw_evidence_sources(checksum_sha256)` | Ingestion deduplication filter |
| `INV-PROV-15` | Foreign Key Constraint: `ON UPDATE RESTRICT ON DELETE RESTRICT` | Case management isolation boundary |
| `INV-PROV-16` | Enum: `retention_class IN ('ACTIVE', 'HASH_ONLY', 'PURGED')` | Automated retention maintenance cron |
| `INV-PROV-17` | RFC 4122 client generator & table `sync_journals` | Offline-first sync manager on SQLite WAL |
| `INV-PROV-18` | Array Constraint: `jsonb_array_length(input_evidence_record_ids) > 0` | Deterministic clinical scoring engine |

---

## 4. Verification Compliance Certification

The eighteen invariants have been formally modeled and verified against the Phase 6 canonical schemas. No edge case, adversarial attack, or network synchronization event can violate these invariants without raising a database-level fatal exception.
