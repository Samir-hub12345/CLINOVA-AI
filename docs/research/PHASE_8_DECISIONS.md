# CLINOVA AI — Phase 8 Formal Architectural Decision Log

> **Document ID:** `DECISION-LOG-PHASE-8`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Distributed Systems Group  

---

## 1. Governance & Architectural Rationale

The Phase 8 Decision Log codifies the definitive architectural, systems engineering, security, and persistence resolutions that translate the approved upstream clinical product definitions (Phases 1–7) into an integrated, build-ready technical architecture for CLINOVA AI.

Every decision is grounded in:
1. **Statutory Indian Compliance:** National Medical Commission (NMC) Regulations 2023, Bharatiya Sakshya Adhiniyam (BSA) 2023 (Section 63), and Digital Personal Data Protection (DPDP) Act 2023.
2. **Clinical Safety & Determinism:** The absolute monopoly of human clinicians over medical dispositions, zero-imputation of missing data, and complete decoupling of deterministic clinical rules from stochastic AI models.
3. **Low-Resource Edge Feasibility:** Zero mandatory paid third-party APIs (₹0 software stack), 100% offline edge operational capability on low-cost fanless Mini-PCs, and dual SQLite/PostgreSQL persistence compatibility.

---

## 2. Definitive Phase 8 Decisions (Decisions 8.1 – 8.16)

---

### Decision 8.1: Modular Monolith Architecture over Microservices
- **Context:** Distributing system capabilities across 15+ containerized microservices would exhaust CPU and RAM on rural edge Mini-PCs ($< 8\text{GB}$ RAM).
- **Decision:** Architect the backend as an asynchronous modular monolith in FastAPI, organizing domain logic into 11 cohesive domain packages with strict boundary interfaces under `backend/app/domain/`.
- **Safety Boundary:** In-process ACID transactions guarantee atomicity across Master Case mutations, clinical observations, and audit logging.

---

### Decision 8.2: Designation of `cases` as the Sole Canonical Table
- **Context:** Early Alembic migrations created `triage_cases`, while Phase 6/7 canonical specifications established `cases`.
- **Decision:** Formally designated `cases` as the single canonical table representing the continuous Master Case. Scheduled Phase 9 migration to execute `ALTER TABLE triage_cases RENAME TO cases;` and create compatibility view `v_legacy_triage_cases`.
- **Safety Boundary:** Eliminates conceptual fragmentation; unifies all clinical foreign keys on `cases.id`.

---

### Decision 8.3: Query-Time Dynamic Wait Time Evaluation (Prohibiting Stored `NOW()`)
- **Context:** PostgreSQL strictly prohibits volatile functions like `NOW()` in `STORED GENERATED ALWAYS AS` columns, raising an immutable expression error.
- **Decision:** Mandated that dynamic wait times and multi-dimensional queue priority rankings are evaluated strictly at query time via indexed datetime subtraction in SQL view `v_active_doctor_queue`.
- **Safety Boundary:** Eliminates database write thrashing; ensures wait times reflect real-time elapsed seconds.

---

### Decision 8.4: Asynchronous Dual-Review State Machine
- **Context:** Requiring two physician signatures at initial row creation causes an immediate database deadlock during acute emergency resuscitations.
- **Decision:** Formalized an asynchronous lifecycle: `PENDING_SECONDARY_REVIEW` $\to$ `SECONDARY_REVIEW_INVITED` $\to$ `SECONDARY_REVIEW_COMMITTED` $\to$ `VERIFIED` / `REJECTED`.
- **Safety Boundary:** Protects clinical workflow continuity while hard-blocking nursing execution until both independent RMPs attest.

---

### Decision 8.5: Privileged Retention Daemon Database Trigger Bypass
- **Context:** Database triggers prevent updates to immutable evidence tables, but DPDP Act 2023 mandates raw media purging to `HASH_ONLY` state after retention periods expire.
- **Decision:** Architected a scoped transaction configuration bypass (`SET LOCAL clinova.retention_daemon_active = 'true'`) allowing the authorized retention daemon to update storage state to `HASH_ONLY` while strictly prohibiting payload tampering.
- **Safety Boundary:** Reconciles data minimization law with immutable cryptographic evidence custody under Section 63 BSA 2023.

---

### Decision 8.6: In-Memory Computed Projection for CAREGRAPH (No Graph Database)
- **Context:** Running an external graph database (e.g. Neo4j) on rural edge Mini-PCs consumes excessive RAM and introduces distributed failure modes.
- **Decision:** CAREGRAPH is architected as an in-memory computed projection and domain service over relational tables (`vital_readings`, `clinical_observations`, `evidence_conflicts`).
- **Safety Boundary:** Pure Python deterministic mathematical execution takes $< 2\text{ms}$; zero graph database licensing or infrastructure overhead.

---

### Decision 8.7: Strict Decoupling of Deterministic Clinical Safety from AI
- **Context:** Relying on LLMs for early warning scores or red flags introduces stochastic hallucination and out-of-memory failure risks.
- **Decision:** Deterministic safety rules (NEWS2 composite score, Shock Index $\text{HR}/\text{SBP}$, Red Flags) execute as pure Python functions completely outside the AI layer.
- **Safety Boundary:** If the local SLM crashes or runs out of memory, clinical scoring and emergency alerting continue operating at 100% capacity.

---

### Decision 8.8: Next.js App Router Client/Server Boundary & Secret Isolation
- **Context:** Leaking backend service keys or master secrets to browser bundles exposes clinical data to unauthorized extraction.
- **Decision:** Data fetching and authorization logic execute within Next.js Server Components. Only public anonymous keys and session JWTs are accessible to client components.
- **Safety Boundary:** Master database credentials and Supabase `service_role` keys never cross the network to client browsers.

---

### Decision 8.9: Two-Phase Push/Pull Offline Sync Protocol with Monotonic Counters
- **Context:** Rural hardware clock drift causes fatal data overwrites if sync relies on wall-clock timestamps (blind Last-Write-Wins).
- **Decision:** Implemented append-only `sync_journals` with 64-bit monotonic sequence counters (`device_seq`) and a two-phase push/pull replication protocol.
- **Safety Boundary:** Eliminates blind Last-Write-Wins; resolves clinical conflicts via `APPEND_ONLY` or `CLINICIAN_WINS`.

---

### Decision 8.10: Acuity-Preserving Epistemic Uncertainty Routing
- **Context:** Treating all uncertainty as an emergency causes severe alert fatigue and overwhelms emergency casualty staff.
- **Decision:** Decoupled uncertainty ($U_t$) from physiological risk ($R_t$). High uncertainty routes to the Nurse Missing-Data Worklist for NBI question closure unless independent physiological rules trigger escalation.
- **Safety Boundary:** Protects emergency resuscitations from routine data gap distractions while preventing patient decompensation.

---

### Decision 8.11: Local Clinic Server as the Authoritative Edge Database Hub
- **Context:** Making browser IndexedDB the authoritative database fragments records across multiple staff tablets on a local clinic network.
- **Decision:** The local fanless Mini-PC hosts the single canonical edge database (SQLite WAL); tablets act as smart terminals communicating over local clinic Wi-Fi LAN.
- **Safety Boundary:** Instant cross-terminal visibility of vital signs and triage notes even during external internet blackouts.

---

### Decision 8.12: Strict Separation of Design Targets from Measured Results
- **Context:** Unverified latency claims in technical documentation undermine engineering credibility.
- **Decision:** Formally decoupled architectural **Design Targets** (theoretical latency and throughput ceilings) from **Measured Results** (empirical benchmarking data).
- **Safety Boundary:** Preserves architectural honesty; mandates empirical benchmarking in Phase 9.

---

### Decision 8.13: Anti-Blind Referral Feasibility Gating
- **Context:** Referring emergency patients to hospitals with broken equipment or zero ICU beds leads to fatal transit turnaways.
- **Decision:** Mandatory mathematical feasibility gating in FACILITYGRAPH ($Feasible(F, P) = \text{Match}(B_{\text{req}}, C_{\text{active}}) \land (T_{\text{transit}} \le T_{\text{golden\_hour}})$).
- **Safety Boundary:** Hard-blocks blind referrals; alerts district command if no regional facility can manage the clinical bundle.

---

### Decision 8.14: In-Flight Differential Privacy & De-Identification in SIGNALGRAPH
- **Context:** Public health telemetry must never leak private patient identities or clinical notes.
- **Decision:** Implemented an in-flight redaction proxy stripping all 18 identifiers and severing foreign keys to patient identity prior to aggregate telemetry calculation.
- **Safety Boundary:** Guarantees zero PHI in operational logs and epidemiologic surge dashboards under DPDP Act 2023.

---

### Decision 8.15: Break-Glass Emergency Access with Cryptographic Merkle Logging
- **Context:** Strict consent barriers must not delay life-saving resuscitation of unconscious trauma victims (*Paschim Banga* doctrine).
- **Decision:** Implemented an immediate break-glass access protocol that unblocks clinical records instantly while logging a high-priority cryptographic audit event.
- **Safety Boundary:** Reconciles emergency life preservation with strict legal accountability under Section 63 BSA 2023.

---

### Decision 8.16: Zero Mandatory Paid Third-Party APIs (₹0 Tech Stack)
- **Context:** Mandatory cloud API fees prevent adoption across low-resource public health facilities.
- **Decision:** The entire core application is bounded to free, open-source runtimes (FastAPI, Next.js, SQLite WAL, Qwen-family local SLM, faster-whisper, PaddleOCR, Leaflet/OSM).
- **Safety Boundary:** Zero monthly software subscription costs; resilient to external billing or API cutoff.
