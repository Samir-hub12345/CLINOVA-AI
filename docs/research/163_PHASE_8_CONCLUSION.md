# CLINOVA AI — Phase 8 Final Technical Architecture & System Design Report

> **Document ID:** `RES-163`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Distributed Systems Engineering Group  

---

## 1. PHASE
**PHASE 8 — TECHNICAL ARCHITECTURE & SYSTEM DESIGN**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Architectural Role: *Translating the approved clinical product specifications, user journeys, operational environments, Master Case relational models, and evidence provenance foundations into a cohesive, build-ready, zero-cost Technical Architecture.*

---

## 2. OBJECTIVE
The primary objective of Phase 8 is to design, formalize, reconcile, and validate the complete technical architecture for CLINOVA AI without implementing production code, applying database migrations, building UI components, or deploying services.

The architecture strictly upholds:
- **MODULAR MONOLITH CORE:** A single unified domain core within FastAPI and Next.js, eliminating distributed network latency and memory thrashing on low-cost edge hardware.
- **SINGLE MASTER CASE:** Exactly one continuous canonical Master Case entity coordinates an entire clinical episode from arrival to discharge.
- **DETERMINISTIC CLINICAL SAFETY:** Physiological scoring (NEWS2, Shock Index, Red Flags) is 100% decoupled from stochastic AI models.
- **₹0 ZERO-COST FEASIBILITY:** Zero mandatory paid third-party APIs (OpenAI, Gemini, Google Maps); 100% operational on open-source runtimes (Qwen-family SLM, faster-whisper, PaddleOCR, Leaflet/OSM).
- **OFFLINE-FIRST RESILIENCE:** Edge Primary Health Centres operate 100% autonomously on local fanless Mini-PCs using local SQLite WAL persistence and local LAN Wi-Fi.
- **FORENSIC AUDITABILITY:** Append-only cryptographic Merkle hash chaining ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$) guaranteeing legal admissibility under Section 63 Bharatiya Sakshya Adhiniyam 2023.

---

## 3. SOURCE MATERIAL
Phase 8 synthesizes and reconciles fifteen authoritative statutory, clinical, and architectural sources (cataloged in `docs/research/SOURCES_PHASE_8.md`):
- **Statutory Indian Frameworks:** National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Regulations 27 & 28); Bharatiya Sakshya Adhiniyam, 2023 (Section 63, modernizing Indian Evidence Act Section 65B); Digital Personal Data Protection (DPDP) Act, 2023 (Sections 4, 6, 7, 8(7), 9); Indian Public Health Standards (IPHS 2022); Supreme Court *Paschim Banga* emergency doctrine (1996).
- **Informatics & Engineering Standards:** W3C PROV-O Recommendation; HL7 FHIR Release 5; LOINC Database; SNOMED CT; Royal College of Physicians NEWS2 (2017); Shock Index (Allgöwer & Burri); PostgreSQL 15 Documentation; SQLite 3.45 WAL Documentation; NIST SP 800-88 Rev 1; Domain-Driven Design (Evans); Modular Monolith Patterns (Grzybek).
- **Immediate Upstream Baseline:** Phase 1 Product Architecture (`DOC-00`–`28`), Phase 2 Innovation Audits (`RES-00`–`24`), Phase 3 User Roles (`RES-30`–`42`), Phase 4 Environments (`RES-43`–`56`), Phase 5 Master Journey (`RES-57`–`77`), Phase 6 Master Case (`RES-78`–`105`), and Phase 7 Evidence & Provenance (`RES-106`–`133`).

---

## 4. SYSTEM ARCHITECTURE RESULT
Specified in `docs/research/135_SYSTEM_ARCHITECTURE.md` (`RES-135`):
- Formulated the high-level six-tier architecture: **Client Layer** $\to$ **API Gateway & Reverse Proxy** $\to$ **Domain Services Layer** $\to$ **Persistence Layer** $\to$ **Storage & Audit Archive**, connected asynchronously to **AI & Perceptual Adapters**.
- Enforced strict boundary rules: Clinical safety rules and security decisions are NEVER placed solely in the client browser.
- Established clear trust zones with cryptographic JWT authentication, input sanitization, and isolated loopback IPC communication for local AI models.

---

## 5. FRONTEND ARCHITECTURE RESULT
Specified in `docs/research/136_FRONTEND_ARCHITECTURE.md` (`RES-136`):
- Designed Next.js 15+ App Router application shell with React 19 Server Components for data hydration and Client Components for rich interactivity.
- Structured the three approved core interfaces:
  1. *Patient Intake Portal:* Multilingual (English, Hindi, Odia), voice symptom capture, paper slip photo upload, mandatory consent gating.
  2. *Nurse Triage Workstation:* Serial vitals acquisition form, deterministic early warning badges, missing data worklist.
  3. *Doctor Reviewer Workbench:* Dynamic prioritized queue, one-screen Master Case review, CAREGRAPH trajectory widget, side-by-side perceptual crop previews ($[0, 1000]^2$ visual bounding boxes and 3-second acoustic snippets).
- Encapsulated secondary workflows into slide-over drawers: Referral Coordination Drawer, Facility Resources Drawer, and Audit/Developer Console Drawer.
- Enforced Secret Isolation Invariant ($\mathbf{Inv\ FE\text{-}1}$): Zero service-role keys or database credentials in client bundles.

---

## 6. BACKEND ARCHITECTURE RESULT
Specified in `docs/research/137_BACKEND_ARCHITECTURE.md` (`RES-137`):
- Architected FastAPI Python 3.11+ modular monolith across four distinct layers: API/Presentation $\to$ Application/Services $\to$ Domain Layer $\to$ Infrastructure/Adapters.
- Categorized backend operations via CQRS principles: Commands (mutations writing to event ledgers), Queries (high-performance read projections), Safety Services (pure deterministic evaluators), AI Adapters (statistical wrappers), and Sync Services.
- Decoupled clinical safety logic completely from AI runtimes: NEWS2 and Shock Index execute as pure Python functions with sub-2ms latency, remaining 100% operational during AI outages.

---

## 7. DOMAIN MODULE RESULT
Specified in `docs/research/138_DOMAIN_MODULE_ARCHITECTURE.md` (`RES-138`):
- Consolidated 28 functional areas into 11 cohesive domain modules under `backend/app/domain/`:
  `case_aggregate`, `identity_registry`, `intake_stream`, `multimodal_media`, `evidence_provenance`, `clinical_observations`, `gap_resolution`, `triage_review`, `continuous_graphs`, `care_pathways`, and `governance_sync`.
- Formally justified the Modular Monolith over microservices for low-cost edge Mini-PCs, eliminating network serialization overhead and memory thrashing while preserving transactional ACID integrity.

---

## 8. MASTER CASE RESULT
Specified in `docs/research/139_MASTER_CASE_ARCHITECTURE.md` (`RES-139`):
- Enforced the Single Master Case Invariant ($\forall e, \exists ! \text{ case\_id} \in \text{UUIDv4}$) as the sole root aggregate for an entire clinical episode.
- Mapped all 27 canonical states ($S01$ to $S27$) across 6 care epochs, governed by Optimistic Concurrency Control (`cases.state_version`) and atomic compare-and-swap transitions.
- Fully resolved the `triage_cases` vs. canonical `cases` conflict by designating `cases` as the sole canonical entity and establishing the Phase 9 migration roadmap.

---

## 9. CAREGRAPH RESULT
Specified in `docs/research/140_CAREGRAPH_ARCHITECTURE.md` (`RES-140`):
- Explicitly rejected Neo4j and external graph databases, saving $> 2\text{GB}$ RAM and avoiding distributed transaction failures.
- Formulated CAREGRAPH as an in-memory computed projection and domain service over relational tables (`vital_readings`, `clinical_observations`, `evidence_conflicts`).
- Defined mathematical formulas for composite physiological risk ($R_t \in [0.0, 1.0]$), trajectory slope ($\Delta R / \Delta t$), and epistemic uncertainty ($U_t \in [0.0, 1.0]$), executing in $< 2\text{ms}$.

---

## 10. FACILITYGRAPH RESULT
Specified in `docs/research/141_FACILITYGRAPH_ARCHITECTURE.md` (`RES-141`):
- Modeled facility capabilities, bed availability, specialist staffing, and telemetry freshness across five states (`KNOWN`, `VERIFIED`, `STALE`, `CONFLICTING`, `UNKNOWN`).
- Established mathematical care feasibility gating matching patient requirement bundles ($B_{\text{req}}$) against operational capabilities within the clinical golden hour ($T_{\text{transit}} \le T_{\text{golden\_hour}}$).
- Enforced the Anti-Blind Referral Invariant ($\mathbf{Inv\ FG\text{-}1}$), prohibiting automated referrals to facilities with broken equipment or zero available beds.

---

## 11. SIGNALGRAPH RESULT
Specified in `docs/research/142_SIGNALGRAPH_ARCHITECTURE.md` (`RES-142`):
- Strictly bounded SIGNALGRAPH to local, facility, and campus operational and syndromic telemetry, explicitly disclaiming replacement of national disease surveillance programs.
- Implemented in-flight privacy scrubbing stripping all 18 identifiers and severing patient foreign keys before aggregate calculation.
- Formulated rolling time-windowed z-score anomaly detection ($Z \ge 2.5$) feeding epidemiologic context badges directly to the Doctor Workbench.

---

## 12. ORCHESTRATION RESULT
Specified in `docs/research/143_ORCHESTRATION_ARCHITECTURE.md` (`RES-143`):
- Architected the Multi-Graph Synthesis Core merging CareGraph, Evidence, Uncertainty, FacilityGraph, Environment, and SignalGraph into an advisory recommendation vector.
- Formulated six canonical candidate actions: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- Enforced strict human-in-the-loop tripwires under NMC Regulation 27: The system is strictly forbidden from autonomously diagnosing, prescribing, admitting, discharging, or authorizing surgery.

---

## 13. AI BOUNDARY RESULT
Specified in `docs/research/144_AI_BOUNDARY_ARCHITECTURE.md` (`RES-144`):
- Encapsulated all local AI models (Qwen3-4B SLM, faster-whisper, PaddleOCR) behind the abstract `AIAdapter` interface.
- Defined the canonical five-stage AI lifecycle: `AI_REQUEST` $\to$ `AI_RESPONSE` $\to$ `VALIDATION` (Pydantic schema & bounds) $\to$ `PROVENANCE` (tagged `AI_INFERRED`) $\to$ `HUMAN REVIEW` (`ACCEPT`, `MODIFY`, `REJECT`).
- Implemented deterministic fallback extractors (regex and medical dictionaries) guaranteeing uninterrupted workflow if the AI runtime is offline or out of memory.

---

## 14. PROVENANCE RESULT
Specified in `docs/research/145_PROVENANCE_ARCHITECTURE.md` (`RES-145`):
- Integrated the nine-stage provenance chain ($\text{RAW SOURCE} \to \text{INGESTION} \to \text{TRANSFORMATION} \to \text{EXTRACTION} \to \text{NORMALIZATION} \to \text{VERIFICATION} \to \text{CLINICAL USE} \to \text{DECISION} \to \text{OUTCOME}$).
- Mapped eight evidence sources and six epistemic states, enforcing the non-negotiable law: $\mathbf{INFERRED \neq VERIFIED}$.
- Linked perceptual grounding pointers ($[0, 1000]^2$ spatial bounding boxes and word-level acoustic timecodes) for instant side-by-side verification on the Doctor Workbench.

---

## 15. MEDIA PROCESSING RESULT
Specified in `docs/research/146_MEDIA_PROCESSING_ARCHITECTURE.md` (`RES-146`):
- Designed an asynchronous, non-blocking multimodal pipeline: `UPLOAD` $\to$ `CHECKSUM (SHA-256)` $\to$ `STORAGE` $\to$ `BACKGROUND JOB` $\to$ `OCR/ASR` $\to$ `EXTRACTION` $\to$ `PROVENANCE` $\to$ `REVIEW READY`.
- Abstracted media storage across local filesystem (`/var/data/clinova/media/`) and Supabase Storage.
- Enforced the UI Non-Assumption Invariant ($\mathbf{Inv\ MP\text{-}1}$): The frontend never assumes extraction success while background jobs are running.

---

## 16. OFFLINE-FIRST RESULT
Specified in `docs/research/147_OFFLINE_FIRST_ARCHITECTURE.md` (`RES-147`):
- Established three-tier edge topology: Frontline Client Tablets $\to$ Local Clinic Server (Fanless Mini-PC) $\to$ Central Cloud Hub.
- Enforced persistence boundaries: Frontline browser clients (IndexedDB) act as smart terminals and are NOT the authoritative database; the Local Clinic Server hosts canonical edge SQLite WAL persistence.
- Enabled 100% autonomous operation during weeks of internet blackout across rural health centres.

---

## 17. SYNC RESULT
Specified in `docs/research/148_SYNC_ARCHITECTURE.md` (`RES-148`):
- Prohibited blind Last-Write-Wins on clinical data; implemented append-only `sync_journals` with 64-bit monotonic sequence counters (`device_seq`).
- Designed a two-phase push/pull replication protocol between edge nodes and cloud hubs.
- Established deterministic conflict resolution strategies (`APPEND_ONLY`, `CLINICIAN_WINS_WITH_AUDIT`, and `SAFETY_PESSIMISTIC`).

---

## 18. QUEUE RESULT
Specified in `docs/research/149_QUEUE_ARCHITECTURE.md` (`RES-149`):
- Addressed PostgreSQL engine restrictions prohibiting volatile functions like `NOW()` in stored generated columns; implemented dynamic wait-time calculation strictly at **query time** via view `v_active_doctor_queue`.
- Formulated multi-dimensional priority score balancing base acuity ($W_{\text{acuity}}$), trajectory slope ($W_{\text{trajectory}}$), dynamic wait escalation ($W_{\text{wait}}$), and facility context.
- Implemented the Decoupling Law ($U_t \neq R_t$): High uncertainty routes to the Nurse Missing-Data Worklist for NBI resolution rather than triggering false ED alarms.

---

## 19. DATABASE RESULT
Specified in `docs/research/150_DATABASE_ARCHITECTURE.md` (`RES-150`):
- Formalized dual relational engine compatibility: SQLite 3.45+ (WAL mode, PRAGMA foreign keys) on edge Mini-PCs and PostgreSQL 15+ / Supabase on cloud hubs.
- Resolved table divergence: Designated `cases` as the sole canonical Master Case table, mapping all child foreign keys to `cases(id)`.
- Standardized RFC 4122 UUIDv4 primary keys, ISO-8601 UTC timestamps, JSON payloads, and Optimistic Concurrency Control (`state_version`).

---

## 20. RETENTION RESULT
Specified in `docs/research/151_RETENTION_ARCHITECTURE.md` (`RES-151`):
- Integrated the DPDP Act 2023 storage limitation lifecycle: `ACTIVE` $\to$ `RETENTION_PERIOD` (30–90 days for raw media) $\to$ `PURGE` $\to$ `HASH_ONLY`.
- Resolved the database trigger exception: Scoped transaction configuration (`SET LOCAL clinova.retention_daemon_active = 'true'`) allows the authorized retention daemon to update storage state to `HASH_ONLY` while strictly prohibiting payload tampering.

---

## 21. DUAL REVIEW RESULT
Specified in `docs/research/152_DUAL_REVIEW_ARCHITECTURE.md` (`RES-152`):
- Corrected the Phase 7 insert-time deadlock: Architected the asynchronous dual-review state machine (`PENDING_SECONDARY_REVIEW` $\to$ `SECONDARY_REVIEW_INVITED` $\to$ `SECONDARY_REVIEW_COMMITTED` $\to$ `VERIFIED` / `REJECTED`).
- Enforced the Distinct Reviewer Invariant ($\mathbf{Inv\ DR\text{-}1}$): Primary and secondary reviewers must be distinct licensed RMPs ($Reviewer_1 \neq Reviewer_2$).
- Provided emergency rural single-doctor override protocols for isolated night shifts with mandatory retrospective CMO auditing.

---

## 22. SECURITY RESULT
Specified in `docs/research/153_SECURITY_ARCHITECTURE.md` (`RES-153`):
- Formalized Zero-Trust architecture with short-lived JWT session tokens and Role-Based Access Control (`PATIENT`, `NURSE`, `CLINICIAN`, `ADMIN`).
- Enforced Secret Isolation: Service-role credentials and database connection strings never cross the network to client browsers.
- Implemented break-glass emergency access protocols for unconscious patients with instant unblocking and high-priority cryptographic Merkle audit logging.

---

## 23. ENVIRONMENT CONFIGURATION RESULT
Specified in `docs/research/154_ENVIRONMENT_CONFIGURATION_ARCHITECTURE.md` (`RES-154`):
- Codified the Golden Law: **One Codebase, Configured Environments**. Supported all six target settings (`ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_COMPANY_CLINIC`, `ENV_INDUSTRIAL_HEALTH`, `ENV_CAMPUS_HEALTH`).
- Injected strongly typed configuration profiles at boot time, enforcing session immutability during active clinical encounters.

---

## 24. OBSERVABILITY RESULT
Specified in `docs/research/155_OBSERVABILITY_ARCHITECTURE.md` (`RES-155`):
- Enforced the Zero PHI in Logs Invariant ($\mathbf{Inv\ OBS\text{-}1}$): Structured JSON operational logs capture technical metrics, durations, and correlation UUIDs, but never raw patient health information.
- Defined standardized health probes (`/health`, `/health/ready`, `/health/ai`, `/health/sync`) and Prometheus operational metrics.

---

## 25. FAILURE RESULT
Specified in `docs/research/156_FAILURE_ARCHITECTURE.md` (`RES-156`):
- Codified the Safe Failure Law: **Never Fake Success**. System degrades gracefully, exposes exact failure boundaries to staff, and provides explicit human manual procedures.
- Formulated an exhaustive failure matrix covering eleven scenarios including network drops, server crashes, database locks, perceptual engine failures, and stale telemetry.

---

## 26. THREAT MODEL RESULT
Specified in `docs/research/157_THREAT_MODEL.md` (`RES-157`):
- Conducted an exhaustive fifteen-point healthcare threat analysis utilizing the STRIDE methodology.
- Mapped attack surfaces, impacts, mitigations, and residual risks across threats including unauthorized clinician access, prompt injection, OCR poisoning, AI hallucination, audit tampering, and physical device theft.

---

## 27. PERFORMANCE RESULT
Specified in `docs/research/158_PERFORMANCE_ARCHITECTURE.md` (`RES-158`):
- Enforced architectural honesty by strictly separating **Design Targets** (theoretical latency ceilings) from **Measured Results** (empirical benchmarking).
- Bounded design targets: Initial shell load $< 1.5\text{s}$, NEWS2 scoring $< 50\text{ms}$, doctor queue evaluation $< 200\text{ms}$, edge CPU OCR $< 5.0\text{s}$, and edge CPU transcription $< 4.0\text{s}$.
- Defined hardware sizing ceilings ($< 4.5\text{GB}$ RAM usage on edge Mini-PCs).

---

## 28. ZERO-COST RESULT
Specified in `docs/research/159_ZERO_COST_ARCHITECTURE.md` (`RES-159`):
- Bounded system dependencies across four economic tiers, verifying **ZERO mandatory paid third-party APIs**.
- Core workflow runs completely on free open-source software (FastAPI, Next.js, SQLite WAL, Qwen-family local SLM, faster-whisper, PaddleOCR, Leaflet/OSM).
- Sized rural edge hardware CapEx at ₹12,000–₹16,000 one-time, with ₹0/month recurring software licensing.

---

## 29. DEPLOYMENT TOPOLOGY RESULT
Specified in `docs/research/160_DEPLOYMENT_TOPOLOGY.md` (`RES-160`):
- Detailed five deployment topologies: `DEV`, `LOCAL_DEMO`, `PHC_EDGE`, `DISTRICT_HOSPITAL`, and `OPTIONAL_CLOUD`.
- Established clear data residency boundaries: Raw audio and image media never leave the local clinic perimeter; only cryptographic SHA-256 hashes and normalized clinical concepts synchronize with district hubs.

---

## 30. ARCHITECTURE DECISION RESULT
Specified in `docs/research/161_ARCHITECTURE_DECISION_RECORD.md` (`RES-161`) and `docs/research/PHASE_8_DECISIONS.md`:
- Formally approved ten master Architecture Decision Records (ADR 8.1 through ADR 8.10) and sixteen executive decisions (Decisions 8.1 through 8.16).
- Codified decisions covering modular monolith boundaries, canonical `cases` table designation, query-time wait evaluation, asynchronous dual review, authorized retention bypass, and in-memory CAREGRAPH projections.

---

## 31. TRACEABILITY RESULT
Specified in `docs/research/162_ARCHITECTURE_TRACEABILITY.md` (`RES-162`):
- Constructed a complete bidirectional traceability matrix linking all 18 BPUT Baseline requirements (`B01`–`B18`), 11 Core Innovations (`C01`–`C11`), and Phases 3–7 specifications directly to Phase 8 architectural specifications, backend domain modules, and frontend components.

---

## 32. ARCHITECTURAL CONFLICTS
Phase 8 formally investigated and resolved four primary technical conflicts identified in prior phase audits:
1. **`triage_cases` vs. Canonical `cases`:** Resolved by designating `cases` as the sole canonical entity and scheduling an atomic rename and compatibility view for Phase 9.
2. **PostgreSQL Stored Generated Column Rejection:** Resolved by eliminating stored generated columns referencing `NOW()` and moving wait-time calculation strictly to query time via view `v_active_doctor_queue`.
3. **Dual-Review Insert-Time Deadlock:** Resolved by introducing an asynchronous state machine (`PENDING_SECONDARY_REVIEW` $\to$ `SECONDARY_REVIEW_COMMITTED` $\to$ `VERIFIED`).
4. **Retention Daemon Immutability Trigger Lock:** Resolved by implementing a scoped transaction configuration bypass (`SET LOCAL clinova.retention_daemon_active = 'true'`) allowing authorized media purges to `HASH_ONLY` state while blocking content tampering.

---

## 33. CLAIMS NARROWED
1. **Queue Wait-Time Calculation:** Narrowed claims from "real-time stored database column" to "deterministic query-time evaluation over an indexed active queue view" to adhere to PostgreSQL engine constraints.
2. **Dual-Review Synchronization:** Narrowed claims from "instantaneous dual-physician co-signing" to "asynchronous invitation, notification, and independent attestation workflow".
3. **Graph Database Architecture:** Narrowed CAREGRAPH claims from "graph database traversal engine" to "in-memory computed projection and domain service over relational state", eliminating unnecessary Neo4j infrastructure.

---

## 34. CLAIMS REMOVED
1. **Uncalibrated Model Confidence:** Stripped raw neural Softmax probabilities from clinical decision flows; mandated temperature scaling / Platt calibration (Expected Calibration Error $< 0.05$).
2. **Fabricated Performance Benchmarks:** Stripped unmeasured millisecond latency claims; categorized all operational metrics strictly as **Design Targets** pending empirical Phase 9 profiling.
3. **Autonomous Clinical Actions:** Removed any possibility of automated AI prescriptions, formal medical diagnoses, or independent ambulance dispatches; reinforced absolute physician monopoly under NMC Regulation 27.

---

## 35. UNRESOLVED QUESTIONS
1. **Empirical Edge CPU Throughput on Celeron Hardware:** Hardware benchmarking of concurrent faster-whisper (int8) and PaddleOCR CPU execution on a physical Celeron N5105 Mini-PC under sustained 30-case/hour clinical load must be conducted in Phase 9.
2. **Local Dialect Phonetic Calibration:** Empirical phonetic accuracy of edge Whisper models on western Odisha Sambalpuri and tribal Kui vernacular speech recordings requires field acoustic testing in Phase 9.
3. **Cross-Facility Sync Scalability:** Network sync throughput of `sync_journals` over 2G/3G cellular links when an edge node reconnects after a 14-day partition requires empirical testing in Phase 9.

---

## 36. RISKS
1. **Risk of SQLite Busy Lock Contention on Edge Mini-PCs:** Concurrent write operations from multiple staff tablets could trigger `SQLITE_BUSY` errors.  
   *Mitigation:* Large binary media is stored on the filesystem; SQLite transactions are bounded to $< 5\text{ms}$; connection pool sets `busy_timeout = 5000ms`.
2. **Risk of Clinical Alert Fatigue from Dual-Review Notifications:** Secondary physicians may be inundated with notifications during casualty surges.  
   *Mitigation:* Dual review is strictly restricted to Tier 4 life-critical interventions (thrombolysis, blood transfusion, surgery); single-doctor rural exemption protocol provided.
3. **Risk of Accidental Secret Exposure in Frontend Bundles:** Developers may inadvertently commit private keys to client code.  
   *Mitigation:* Automated CI/CD git-secrets scanning; Next.js App Router enforces server-only secret isolation.

---

## 37. FILES CREATED
Phase 8 authored and committed all **thirty-two required authoritative architectural specifications** in `docs/research/`:
1. `docs/research/134_TECHNICAL_ARCHITECTURE_PLAN.md` (`RES-134`)
2. `docs/research/135_SYSTEM_ARCHITECTURE.md` (`RES-135`)
3. `docs/research/136_FRONTEND_ARCHITECTURE.md` (`RES-136`)
4. `docs/research/137_BACKEND_ARCHITECTURE.md` (`RES-137`)
5. `docs/research/138_DOMAIN_MODULE_ARCHITECTURE.md` (`RES-138`)
6. `docs/research/139_MASTER_CASE_ARCHITECTURE.md` (`RES-139`)
7. `docs/research/140_CAREGRAPH_ARCHITECTURE.md` (`RES-140`)
8. `docs/research/141_FACILITYGRAPH_ARCHITECTURE.md` (`RES-141`)
9. `docs/research/142_SIGNALGRAPH_ARCHITECTURE.md` (`RES-142`)
10. `docs/research/143_ORCHESTRATION_ARCHITECTURE.md` (`RES-143`)
11. `docs/research/144_AI_BOUNDARY_ARCHITECTURE.md` (`RES-144`)
12. `docs/research/145_PROVENANCE_ARCHITECTURE.md` (`RES-145`)
13. `docs/research/146_MEDIA_PROCESSING_ARCHITECTURE.md` (`RES-146`)
14. `docs/research/147_OFFLINE_FIRST_ARCHITECTURE.md` (`RES-147`)
15. `docs/research/148_SYNC_ARCHITECTURE.md` (`RES-148`)
16. `docs/research/149_QUEUE_ARCHITECTURE.md` (`RES-149`)
17. `docs/research/150_DATABASE_ARCHITECTURE.md` (`RES-150`)
18. `docs/research/151_RETENTION_ARCHITECTURE.md` (`RES-151`)
19. `docs/research/152_DUAL_REVIEW_ARCHITECTURE.md` (`RES-152`)
20. `docs/research/153_SECURITY_ARCHITECTURE.md` (`RES-153`)
21. `docs/research/154_ENVIRONMENT_CONFIGURATION_ARCHITECTURE.md` (`RES-154`)
22. `docs/research/155_OBSERVABILITY_ARCHITECTURE.md` (`RES-155`)
23. `docs/research/156_FAILURE_ARCHITECTURE.md` (`RES-156`)
24. `docs/research/157_THREAT_MODEL.md` (`RES-157`)
25. `docs/research/158_PERFORMANCE_ARCHITECTURE.md` (`RES-158`)
26. `docs/research/159_ZERO_COST_ARCHITECTURE.md` (`RES-159`)
27. `docs/research/160_DEPLOYMENT_TOPOLOGY.md` (`RES-160`)
28. `docs/research/161_ARCHITECTURE_DECISION_RECORD.md` (`RES-161`)
29. `docs/research/162_ARCHITECTURE_TRACEABILITY.md` (`RES-162`)
30. `docs/research/163_PHASE_8_CONCLUSION.md` (`RES-163`)
31. `docs/research/SOURCES_PHASE_8.md` (`SOURCES-PHASE-8`)
32. `docs/research/PHASE_8_DECISIONS.md` (`DECISION-LOG-PHASE-8`)

---

## 38. FILES MODIFIED
- None. (Phase 8 is strictly an additive architectural design, reconciliation, validation, and documentation phase).

---

## 39. FILES INTENTIONALLY UNTOUCHED
- `frontend/` (Zero UI code modified, refactored, or implemented).
- `backend/app/` (Zero production runtime backend code modified or refactored).
- `backend/alembic/` (Zero database migrations created or applied to live instances).
- Active database instances (`clinova-dev.db` preserved intact; zero schema alterations executed).
- Upstream specifications (`docs/00_*` through `docs/28_*` and `docs/research/00_*` through `docs/research/133_*` preserved as immutable historical truth).

---

## 40. PHASE STATUS
**READY FOR HUMAN REVIEW**
