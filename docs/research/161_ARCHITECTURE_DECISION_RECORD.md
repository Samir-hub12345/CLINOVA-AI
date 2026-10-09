# CLINOVA AI — Master Architecture Decision Record (ADR) Log

> **Document ID:** `RES-161`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Technical Governance Group  

---

## 1. Architectural Governance Overview

This document codifies the definitive Architecture Decision Records (ADRs) formulated and approved during Phase 8. Every record adheres to the standard architectural structure:
$$\mathbf{DECISION} \quad \mathbf{RATIONALE} \quad \mathbf{ALTERNATIVES} \quad \mathbf{REJECTED\ OPTIONS} \quad \mathbf{IMPACT} \quad \mathbf{RISKS} \quad \mathbf{FOLLOW\text{-}UP\ PHASE}$$

---

## 2. Master Architecture Decision Records (ADR 8.1 – ADR 8.10)

---

### ADR-8.1: Modular Monolith vs. Microservices Architecture
- **DECISION:** Implement CLINOVA AI backend as an Asynchronous Modular Monolith within FastAPI, partitioning domain logic into eleven cohesive domain packages under `app/domain/`.
- **RATIONALE:** Edge deployment on low-cost fanless Mini-PCs ($< 8\text{GB}$ RAM) cannot support the container memory overhead, network serialization latency, and distributed transaction complexity of 15 microservices. A modular monolith provides strict domain boundaries, sub-millisecond in-process function calls, and atomic ACID transactions.
- **ALTERNATIVES CONSIDERED:** Microservices with Docker Swarm; Event-Driven Microservices with Kafka; Serverless Functions (AWS Lambda).
- **REJECTED OPTIONS:** Microservices (rejected due to memory exhaustion on edge Mini-PCs); Serverless (rejected due to cloud dependency and failure in 100% offline environments).
- **IMPACT:** Single deployable artifact; trivial local developer setup; high maintainability.
- **RISKS:** Potential for domain boundary erosion if developers make direct cross-module calls without interfaces.
- **FOLLOW-UP PHASE:** Phase 9 (Enforce strict linter rules and domain import boundaries).

---

### ADR-8.2: Canonical `cases` Table and Deprecation of `triage_cases`
- **DECISION:** Formally designate `cases` as the single canonical Master Case table. Deprecate the legacy name `triage_cases`. Schedule Phase 9 migration to execute `ALTER TABLE triage_cases RENAME TO cases;` and create compatibility view `v_legacy_triage_cases`.
- **RATIONALE:** CLINOVA has evolved from an isolated 90-second triage tool into Continuous Care Intelligence spanning the entire patient episode. Retaining `triage_cases` creates mental fragmentation and violates DDD naming standards.
- **ALTERNATIVES CONSIDERED:** Keep `triage_cases` forever; create a parallel `cases` table and copy data; migrate immediately in Phase 8.
- **REJECTED OPTIONS:** Parallel table (rejected due to synchronization bugs); Immediate migration in Phase 8 (rejected to uphold Atomic Phase Rule prohibiting database mutations in Phase 8).
- **IMPACT:** Aligns codebase with Phase 6/7 canonical specifications (`RES-79`).
- **RISKS:** Breaking legacy queries if not provided with a backward-compatible view.
- **FOLLOW-UP PHASE:** Phase 9 (Implement and execute Alembic migration script).

---

### ADR-8.3: Query-Time Dynamic Wait Time vs. Stored Generated Columns
- **DECISION:** Prohibit PostgreSQL stored generated columns using `NOW()` for elapsed wait time. Implement dynamic wait times and composite doctor queue priorities at query time via indexed datetime subtraction (`clock_timestamp() - queued_at`) in SQL View `v_active_doctor_queue`.
- **RATIONALE:** PostgreSQL raises `ERROR: generation expression is not immutable` when volatile functions like `NOW()` are used in stored columns. Furthermore, stored values do not update as real-world time elapses.
- **ALTERNATIVES CONSIDERED:** Cron daemon updating rows every minute; Stored column with application-level touch triggers.
- **REJECTED OPTIONS:** Cron daemon updates (rejected due to database write thrashing and WAL file bloat); Stored generated column (rejected due to Postgres engine rejection).
- **IMPACT:** Zero database write overhead for ticking clocks; 100% mathematically accurate elapsed wait times.
- **RISKS:** Query latency if queue table becomes massive (mitigated by partial index on active cases).
- **FOLLOW-UP PHASE:** Phase 9 (Implement `v_active_doctor_queue` view).

---

### ADR-8.4: Asynchronous Dual-Review State Machine
- **DECISION:** Replace the insert-time dual signature requirement with an asynchronous lifecycle: `PENDING_SECONDARY_REVIEW` $\to$ `SECONDARY_REVIEW_INVITED` $\to$ `SECONDARY_REVIEW_COMMITTED` $\to$ `VERIFIED` / `REJECTED`.
- **RATIONALE:** Requiring both primary and secondary physician signatures at the moment of row creation causes an immediate database deadlock during acute emergency resuscitations.
- **ALTERNATIVES CONSIDERED:** Synchronous pop-up modal requiring second doctor's password immediately; Single doctor signature with post-hoc audit.
- **REJECTED OPTIONS:** Synchronous modal (rejected because second doctor may be in the resuscitation bay washing hands); Single signature without gate (rejected for high-risk thrombolysis).
- **IMPACT:** Smooth clinical workflow without database lockups; safety gating preserved.
- **RISKS:** Delay in secondary review (mitigated by automated audio/visual alerts on Doctor Workbench).
- **FOLLOW-UP PHASE:** Phase 9 (Implement dual-review table and notification hooks).

---

### ADR-8.5: Privileged Retention Daemon Database Trigger Bypass
- **DECISION:** Authorize the background Retention Daemon to update media storage state to `HASH_ONLY` via transaction-scoped configuration (`SET LOCAL clinova.retention_daemon_active = 'true'`) or dedicated database role, while keeping immutability triggers active for standard users.
- **RATIONALE:** DPDP Act 2023 mandates raw media purging after 30–90 days, while database immutability triggers block all updates. A scoped authorization bypass allows compliant data disposal without compromising forensic integrity.
- **ALTERNATIVES CONSIDERED:** Hard delete of entire database rows; Disabling triggers globally during daemon runs.
- **REJECTED OPTIONS:** Hard delete (rejected because Section 63 BSA requires preserving SHA-256 hashes); Disabling triggers globally (rejected due to race condition permitting tampering).
- **IMPACT:** 100% statutory compliance with both DPDP Act 2023 and Section 63 BSA 2023.
- **RISKS:** Rogue processes impersonating daemon setting (mitigated by database user permission checks).
- **FOLLOW-UP PHASE:** Phase 9 (Implement trigger function and retention daemon script).

---

### ADR-8.6: CAREGRAPH as Computed Projection vs. Neo4j Graph Database
- **DECISION:** Model CAREGRAPH as an in-memory computed projection and domain service over relational state, explicitly rejecting Neo4j or external graph databases.
- **RATIONALE:** CAREGRAPH represents the multi-dimensional physiological trajectory of a single patient, not a complex cross-entity network topology. Running Neo4j on rural edge Mini-PCs would consume excessive RAM ($> 2\text{GB}$) and introduce distributed failure modes.
- **ALTERNATIVES CONSIDERED:** Dedicated Neo4j instance; PostgreSQL Apache AGE extension; RedisGraph.
- **REJECTED OPTIONS:** Neo4j (rejected due to hardware and operational overhead); Apache AGE (rejected due to SQLite incompatibility on edge nodes).
- **IMPACT:** Zero extra infrastructure overhead; sub-2ms Python projection execution.
- **RISKS:** None; projection logic is pure deterministic mathematics.
- **FOLLOW-UP PHASE:** Phase 9 (Implement `CareGraphService`).

---

### ADR-8.7: Local SLM Runtime Boundary & Deterministic Safety Decoupling
- **DECISION:** Encapsulate local SLM/Whisper/OCR behind an abstract `AIAdapter` interface. Enforce complete decoupling of deterministic clinical rules (NEWS2, Shock Index, Red Flags) from AI models.
- **RATIONALE:** If the local AI model crashes or experiences OOM, the patient triage, vital scoring, and emergency alerting must remain 100% operational without degradation.
- **ALTERNATIVES CONSIDERED:** Embedding LLM as a core dependency for all triage decisions; Cloud-only AI API calls.
- **REJECTED OPTIONS:** LLM in core safety loop (rejected due to hallucination risks and latency); Cloud AI (rejected due to rural internet blackouts).
- **IMPACT:** System remains 100% resilient and fail-safe.
- **RISKS:** Fallback regex extraction captures fewer nuances than SLM (acceptable trade-off for reliability).
- **FOLLOW-UP PHASE:** Phase 9 (Implement `AIAdapter` and fallback extractors).

---

### ADR-8.8: Next.js App Router Client/Server Boundary & Secret Protection
- **DECISION:** Utilize Next.js App Router Server Components for data fetching and shell rendering. Strictly prohibit `service_role` keys, database connection strings, or master secrets in client bundles.
- **RATIONALE:** Prevents credential leakage across client browsers and mobile tablets.
- **ALTERNATIVES CONSIDERED:** Client-side only SPA (Vite/CRA); Full SSR for all interactive components.
- **REJECTED OPTIONS:** Client-side SPA (rejected due to secret leakage risks); Full SSR (rejected due to lack of interactivity for canvas cropping and audio recording).
- **IMPACT:** High security posture; fast initial load times.
- **RISKS:** Developer error adding `NEXT_PUBLIC_` to private variables (mitigated by CI secrets scanner).
- **FOLLOW-UP PHASE:** Phase 9 (Configure Next.js environment guards).

---

### ADR-8.9: Two-Phase Push/Pull Offline Sync Protocol
- **DECISION:** Implement bi-directional synchronization between edge Mini-PCs and central cloud hubs using append-only `sync_journals` and a two-phase push/pull protocol with logical monotonic counters (`device_seq`).
- **RATIONALE:** Immunizes synchronization against rural hardware clock drift; prevents blind Last-Write-Wins overwrites of critical clinical measurements.
- **ALTERNATIVES CONSIDERED:** Distributed SQLite (LiteFS / CRDTs); Blind Last-Write-Wins timestamp sync.
- **REJECTED OPTIONS:** CRDTs (rejected due to complex schema adaptations); Blind LWW (rejected due to fatal clinical overwrite risks).
- **IMPACT:** Reliable synchronization across days of intermittent network partitions.
- **RISKS:** Journal table growth over years (mitigated by periodic compaction of committed journals).
- **FOLLOW-UP PHASE:** Phase 9 (Implement `SyncJournalService`).

---

### ADR-8.10: Acuity-Preserving Uncertainty Routing
- **DECISION:** Decouple epistemic uncertainty ($U_t$) from physiological risk ($R_t$). High uncertainty primarily routes to the Nurse Missing-Data Worklist for NBI gap closure, unless independent clinical safety rules trigger emergency escalation.
- **RATIONALE:** High uncertainty regarding non-critical history (e.g. forgotten ointment name) must not trigger emergency casualty alarms, which causes clinical alert fatigue and distorts ED operations.
- **ALTERNATIVES CONSIDERED:** Uncertainty always elevates to CRITICAL; Uncertainty ignored in triage.
- **REJECTED OPTIONS:** Uncertainty always critical (rejected due to alert fatigue); Uncertainty ignored (rejected due to missed decompensation risks).
- **IMPACT:** Clinically realistic queue sorting; focused nursing workflow.
- **RISKS:** Edge cases where missing data conceals an acute crisis (mitigated by mandatory bedside vital check).
- **FOLLOW-UP PHASE:** Phase 9 (Implement queue routing logic in `TriageReviewService`).
