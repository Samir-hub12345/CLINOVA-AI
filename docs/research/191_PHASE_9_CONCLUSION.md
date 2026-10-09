# CLINOVA AI — Phase 9 Final Environment, Secrets & Configuration Foundation Report

> **Document ID:** `RES-191`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Security Engineering & Clinical Configuration Group  

---

## 1. PHASE
**PHASE 9 — ENVIRONMENT, SECRETS & CONFIGURATION FOUNDATION**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Architectural Role: *Establishing the definitive, secure, fail-fast, zero-cost, and environment-separated configuration and secret-management foundation across development, local demo, rural edge, district hospital, cloud preview, and automated test environments.*

---

## 2. OBJECTIVE
The primary objective of Phase 9 is to define, formalize, reconcile, and validate the complete configuration and secret-management architecture for CLINOVA AI without executing Phase 10 (AI integration), applying database migrations, building production UI components, implementing auth flows, integrating external APIs, or deploying services.

The configuration model strictly upholds:
- **Zero Secrets in Frontend Bundles:** Complete elimination of administrative tokens (e.g. `SUPABASE_SERVICE_ROLE_KEY`) and database credentials from client code.
- **Explicit Two-Dimensional Identity:** Total separation between infrastructure deployment topology (`APP_ENV`) and clinical facility operational profile (`CLINOVA_ENVIRONMENT_ID`).
- **Fail-Closed Boot Validation:** Fatal pre-flight halt if critical security credentials, persistence paths, or environment tokens are absent or malformed.
- **Synthetic Medical Data by Default:** Mandatory enforcement of `CLINOVA_DATA_MODE=synthetic` across all development, demo, and preview sandboxes.
- **₹0 Zero-Cost Core Mandate:** Zero mandatory paid third-party APIs for core clinical triage, vital risk scoring, queueing, and prescription sign-off.
- **Frontend Technology Correction:** Unambiguous rejection of Tailwind CSS in favor of Next.js plain CSS Modules, W3C CSS Custom Properties (CSS variables), and native CSS Grid / Flexbox.

---

## 3. SOURCE MATERIAL
Phase 9 synthesizes and reconciles fifteen authoritative statutory, cryptographic, and architectural sources (cataloged in `docs/research/SOURCES_PHASE_9.md`):
- **Statutory Indian Frameworks:** National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Regulations 27 & 28); Bharatiya Sakshya Adhiniyam, 2023 (Section 63, replacing Indian Evidence Act Section 65B); Digital Personal Data Protection (DPDP) Act, 2023 (Sections 4, 6, 8(7), 9); Indian Public Health Standards (IPHS 2022); Supreme Court *Paschim Banga* emergency doctrine (1996).
- **Security & Informatics Standards:** The Twelve-Factor App (Factor III: Config); NIST SP 800-63B (Digital Identity); NIST SP 800-88 Rev. 1 (Media Sanitization); OWASP Top 10 (A05:2021 Security Misconfiguration); W3C CORS Specification; W3C CSS Custom Properties Level 1.
- **Immediate Upstream Baseline:** Phases 1–8 research and architecture specifications (`docs/research/00_*` through `docs/research/163_*`), current repository configuration files (`.env`, `.env.example`, `backend/app/core/config.py`, `frontend/package.json`).

---

## 4. CONFIGURATION PRINCIPLES RESULT
Specified in `docs/research/164_ENVIRONMENT_CONFIG_PLAN.md` (`RES-164`):
- Codified the twelve fundamental configuration laws:
  1. *Safe Defaults:* Defaults to most secure, offline-resilient setting.
  2. *Explicit Environment:* Prohibits environment guessing; mandates explicit tokens.
  3. *No Secrets in Source Code:* Zero credentials committed to git or built into bundles.
  4. *No Service-Role Key in Browser:* Permanent firewall against administrative key leakage.
  5. *No Production Credentials in Local Demo:* Prohibits live hospital connections locally.
  6. *Synthetic Data by Default:* Enforces mock data in all non-certified instances.
  7. *Zero-Cost by Default:* Zero required paid subscriptions.
  8. *Fail Closed:* Fatal boot termination on missing critical secrets.
  9. *Clear Local/Offline Behavior:* Authoritative local server persistence on edge.
  10. *Environment Configuration $\neq$ User Role:* Configuration does not replace RBAC.
  11. *Environment Configuration $\neq$ Clinical Decision:* Configuration cannot alter safety rules.
  12. *Configuration Versioning:* Every deployed profile carries immutable audit metadata.

---

## 5. CORE VARIABLES RESULT
Specified in `docs/research/165_CONFIGURATION_SCHEMA.md` (`RES-165`):
- Formalized strongly typed Pydantic Settings schema (`BackendSettings`) and Zod client schema (`clientEnvSchema`).
- Classified 24 core variables across five structural states: `REQUIRED`, `OPTIONAL`, `FORBIDDEN`, `DERIVED`, and `DEFAULTABLE`.
- Enforced type safety, value constraints, and path sanitization across all operational settings.

---

## 6. SECRET CLASSIFICATION RESULT
Specified in `docs/research/166_SECRET_CLASSIFICATION.md` (`RES-166`):
- Established the six-tier credential taxonomy: `PUBLIC_RUNTIME_CONFIG`, `SERVER_ONLY_SECRET`, `LOCAL_ONLY_SECRET`, `DEPLOYMENT_SECRET`, `OPTIONAL_PROVIDER_CONFIG`, and `NON_SECRET_CONFIGURATION`.
- Defined strict boundaries isolating seven forbidden credentials from client access.
- Outlined zero-downtime dual-key migration, emergency leak revocation, and offline USB dongle rotation procedures.

---

## 7. FRONTEND/BACKEND BOUNDARY RESULT
Specified in `docs/research/167_FRONTEND_BACKEND_CONFIG_BOUNDARY.md` (`RES-167`):
- Enforced the boundary law: $\mathbf{Client\ Bundle} \cap \mathbf{Server\ Secrets} = \emptyset$.
- Permitted strictly seven public variables carrying `NEXT_PUBLIC_*` prefixes.
- Established server component data serialization barriers protecting backend memory.

---

## 8. DEV CONFIG RESULT
Specified in `docs/research/168_DEV_ENVIRONMENT.md` (`RES-168`):
- Defined agile developer workstation profile: `APP_ENV=dev`.
- Configured local SQLite WAL persistence (`clinova-dev.db`), local filesystem media storage (`./data/storage`), loopback SLM endpoints, and `CLINOVA_DATA_MODE=synthetic`.

---

## 9. LOCAL DEMO CONFIG RESULT
Specified in `docs/research/169_LOCAL_DEMO_ENVIRONMENT.md` (`RES-169`):
- Defined bulletproof, zero-latency showcase profile: `APP_ENV=local_demo`.
- Pre-seeded four approved synthetic Master Cases (Acute STEMI, Pediatric Dehydration, Maternal Pre-Eclampsia, Thoracoabdominal Trauma) with synthetic bounding boxes and audio assets.
- Guarantees 100% offline execution during conference presentations and stakeholder reviews.

---

## 10. PHC EDGE CONFIG RESULT
Specified in `docs/research/170_PHC_EDGE_ENVIRONMENT.md` (`RES-170`):
- Defined rural health center profile: `APP_ENV=phc_edge`, running on a ₹12,000–₹16,000 fanless Mini-PC (Intel Celeron N5105 / 8GB RAM).
- Configured local SQLite WAL persistence (`/var/data/clinova/db/`), local quantized SLM (`qwen2.5-3b-instruct-q4`), local faster-whisper CPU, and asynchronous push/pull sync.

---

## 11. DISTRICT HOSPITAL CONFIG RESULT
Specified in `docs/research/171_DISTRICT_HOSPITAL_ENVIRONMENT.md` (`RES-171`):
- Defined enterprise hospital profile: `APP_ENV=district_hospital`, coordinating 20–50 concurrent workstations.
- Configured PostgreSQL 15+ cluster with connection pooling (`asyncpg` via PgBouncer), enterprise NAS media storage, dedicated inference servers, and mandatory dual-physician sign-offs.

---

## 12. CLOUD PREVIEW CONFIG RESULT
Specified in `docs/research/172_CLOUD_PREVIEW_ENVIRONMENT.md` (`RES-172`):
- Defined hosted web sandbox profile: `APP_ENV=cloud_preview`.
- Integrated managed Supabase PostgreSQL, private Supabase Storage buckets with 15-minute signed URLs, mandatory public preview banners, and strict synthetic data enforcement.

---

## 13. TEST CONFIG RESULT
Specified in `docs/research/173_TEST_ENVIRONMENT.md` (`RES-173`):
- Defined automated testing and CI/CD profile: `APP_ENV=test`.
- Configured in-memory SQLite (`sqlite+aiosqlite:///:memory:`), ephemeral test storage, deterministic mock AI doubles ($<1\text{ms}$ latency), zero outbound network sockets, and hermetic test isolation.

---

## 14. CLINOVA ENVIRONMENT PROFILE RESULT
Specified in `docs/research/174_CLINOVA_ENVIRONMENT_PROFILES.md` (`RES-174`):
- Codified declarative configurations for all six operational facility contexts: `ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_COMPANY_CLINIC`, `ENV_INDUSTRIAL_HEALTH`, and `ENV_CAMPUS_HEALTH`.
- Formulated profile-driven queue depth thresholds, wait acceleration factors ($\alpha$), specialist routing flags, and occupational hazard screening modules.
- Prohibited profiles from altering fundamental clinical safety invariants.

---

## 15. ENVIRONMENT ID RESULT
Specified in `docs/research/175_ENVIRONMENT_ID_MODEL.md` (`RES-175`):
- Formulated the boot-time identity loading, enum validation, and cross-dimension compatibility checks.
- Enforced the Session Immutability Invariant ($\mathbf{Inv\ ENV\text{-}1}$): Zero in-app switching of the facility profile during active clinical sessions.

---

## 16. DATABASE CONFIG RESULT
Specified in `docs/research/176_DATABASE_CONFIG_MODEL.md` (`RES-176`):
- Defined dual-engine configuration for SQLite 3.45+ (WAL mode, `PRAGMA foreign_keys = ON;`, busy timeout 5000ms) and PostgreSQL 15+ (asyncpg, connection pooling, 5000ms statement timeout).
- Implemented pre-flight scheme validation preventing local development instances from connecting to live hospital or government databases.

---

## 17. STORAGE CONFIG RESULT
Specified in `docs/research/177_STORAGE_CONFIG_MODEL.md` (`RES-177`):
- Abstracted media persistence across `LOCAL_FS` and `SUPABASE_STORAGE`.
- Enforced the Inviolable Storage Law: Raw patient media is never written to public web-accessible folders.
- Integrated DPDP Act storage limitation policies (30–90 days retention, automated purge to hash-only state).

---

## 18. AI CONFIG BOUNDARY RESULT
Specified in `docs/research/178_AI_CONFIG_BOUNDARY.md` (`RES-178`):
- Bounded all AI inference to local open-source runtimes (Qwen SLM, faster-whisper, PaddleOCR, IndicTrans2) with ₹0 mandatory external API costs.
- Formulated the Safe Degradation Law: When AI is offline, the system enters `AI_UNAVAILABLE` mode; core deterministic NEWS2 triage continues 100%, and zero fake AI results are fabricated.

---

## 19. CORS/NETWORK RESULT
Specified in `docs/research/179_CORS_NETWORK_CONFIG.md` (`RES-179`):
- Defined strict origin whitelists per environment.
- Enforced the absolute prohibition of wildcard CORS (`*`) in production and cloud preview to prevent cross-origin medical credential theft.
- Mandated TLS 1.3 encryption across hospital and cloud ingress points.

---

## 20. OFFLINE CONFIG RESULT
Specified in `docs/research/180_OFFLINE_CONFIG_MODEL.md` (`RES-180`):
- Formulated five discrete connectivity states: `ONLINE`, `OFFLINE`, `DEGRADED`, `SYNCING`, and `SYNC_CONFLICT`.
- Codified the Edge Persistence Law: Local Clinic Server SQLite database remains the authoritative clinical source of truth during weeks of internet blackout; frontline tablets operate as thin clients.

---

## 21. SYNTHETIC DATA RESULT
Specified in `docs/research/181_SYNTHETIC_DATA_MODE.md` (`RES-181`):
- Established `CLINOVA_DATA_MODE=synthetic` as the mandatory default for `DEV`, `LOCAL_DEMO`, `CLOUD_PREVIEW`, and `TEST`.
- Formulated the quadruple-barrier validation check required before an instance can operate in `live` patient mode.

---

## 22. FEATURE FLAG RESULT
Specified in `docs/research/182_FEATURE_FLAG_MODEL.md` (`RES-182`):
- Defined nine declarative feature flags (`FEATURE_VOICE`, `FEATURE_OCR`, etc.).
- Codified the Seven Inviolable Invariants: Core clinical safety controls (RMP verification gate, NEWS2 scoring, Merkle audit chaining, zero-imputation) are hardcoded and cannot be disabled by any feature flag.

---

## 23. LOGGING RESULT
Specified in `docs/research/183_LOGGING_CONFIG_MODEL.md` (`RES-183`):
- Enforced absolute decoupling between Technical Operational Logs (JSON console/syslog) and the Forensic Clinical Audit Ledger (`audit_events` table).
- Integrated automated regex redaction filters guaranteeing Zero PHI in operational log streams.

---

## 24. CONFIG FAILURE RESULT
Specified in `docs/research/184_CONFIG_FAILURE_MODEL.md` (`RES-184`):
- Mapped nine explicit configuration failure scenarios across the complete five-stage lifecycle: `DETECTION` $\to$ `FAIL-SAFE RESPONSE` $\to$ `USER/ADMIN MESSAGE` $\to$ `AUDIT` $\to$ `RECOVERY`.
- Defined pre-flight fatal halt behaviors (Exit 1) and decoupled health probes (`/health`, `/health/ready`, `/health/ai`, `/health/sync`).

---

## 25. THREAT MODEL RESULT
Specified in `docs/research/185_CONFIGURATION_THREAT_MODEL.md` (`RES-185`):
- Conducted exhaustive STRIDE threat analysis covering thirteen configuration failure vectors.
- Mapped attack scenarios, technical impacts, architectural mitigations, and automated verification checks.

---

## 26. EDGE CONFIG RESULT
Specified in `docs/research/186_EDGE_CONFIG_MODEL.md` (`RES-186`):
- Detailed physical edge topology: Frontline Tablets (Thin Clients) $\to$ Local Clinic Wi-Fi $\to$ Local Clinic Server (Fanless Mini-PC) $\to$ SQLite WAL.
- Outlined mDNS and static LAN server discovery, edge power UPS safe shutdown hooks, and memory pressure throttling.

---

## 27. CLOUD CONFIG RESULT
Specified in `docs/research/187_CLOUD_CONFIG_MODEL.md` (`RES-187`):
- Defined central cloud hub architecture: Next.js frontend $\to$ FastAPI backend $\to$ Supabase managed persistence.
- Established clear matrices separating shared system standards from environment-specific configuration parameters.

---

## 28. ZERO-COST RESULT
Specified in `docs/research/188_ZERO_COST_CONFIG_MODEL.md` (`RES-188`):
- Audited all dependencies across four economic tiers, verifying **₹0 / month recurring software OpEx**.
- Confirmed that the entire clinical workflow operates without mandatory external commercial API keys.

---

## 29. VERSIONING RESULT
Specified in `docs/research/189_CONFIGURATION_VERSIONING.md` (`RES-189`):
- Defined immutable configuration profile manifest schema (`configuration_id`, `version`, `approved_by`, `change_reason`, `config_hash`).
- Formalized the six-stage configuration change governance lifecycle and automated rollback procedures.

---

## 30. TAILWIND RECONCILIATION RESULT
Specified in `docs/research/167_FRONTEND_BACKEND_CONFIG_BOUNDARY.md` (`RES-167`) and `docs/research/PHASE_9_DECISIONS.md` (Decision 9.2):
- **Tailwind CSS is formally rejected and eliminated** from the CLINOVA AI architectural baseline.
- Reconciled Phase 8 documentation: CLINOVA AI enforces Next.js 15+ App Router, TypeScript 5.6+, plain CSS Modules, W3C CSS Custom Properties (CSS variables) for clinical acuity design tokens, and native CSS Grid / Flexbox layouts.

---

## 31. TRACEABILITY RESULT
Specified in `docs/research/190_CONFIGURATION_TRACEABILITY.md` (`RES-190`):
- Established complete bidirectional traceability linking BPUT Baseline requirements (`B01`–`B18`), Core Innovations (`C01`–`C11`), and Indian statutory acts (NMC, BSA, DPDP) directly to Phase 9 configuration parameters and invariants.

---

## 32. CONFIGURATION CONFLICTS
Phase 9 formally investigated and resolved three major configuration conflicts:
1. **Frontend Styling Conflict (Tailwind vs. Pure CSS):** Phase 8 doc 136 mentioned Tailwind. Resolved by rejecting Tailwind and formalizing pure CSS Modules with clinical CSS Custom Properties.
2. **Environment Identity Ambiguity:** Phase 4 facility tokens conflicted with Phase 8 deployment topologies. Resolved via the two-dimensional model: `APP_ENV` (topology) $\times$ `CLINOVA_ENVIRONMENT_ID` (facility profile).
3. **Storage Public Path Fallback Risk:** Legacy file handlers fell back to web root directories upon permission errors. Resolved by enforcing pre-flight write barriers and fatal halts.

---

## 33. CLAIMS NARROWED
1. **Cloud Service Integration:** Narrowed claims regarding Supabase to an **optional cloud preview adapter**; confirmed that edge nodes operate 100% on local SQLite without Supabase dependencies.
2. **Edge Hardware Capabilities:** Sized local SLM reasoning claims to quantized 3B models (`qwen2.5-3b-instruct-q4`) running on CPU cores rather than unquantized 7B/14B models.
3. **Dynamic Environment Switching:** Narrowed operational assumptions to prohibit in-app facility switching during active clinical sessions.

---

## 34. CLAIMS REMOVED
1. **Mandatory Third-Party Cloud APIs:** Completely stripped any requirement for Google Gemini, OpenAI, or paid cloud OCR keys for core clinical workflows.
2. **Tailwind Framework:** Stripped Tailwind utility styling from the approved frontend technical stack.
3. **Simulated AI Fallbacks:** Removed any concept of fabricating synthetic AI text during AI engine outages; mandated transparent manual data entry.

---

## 35. UNRESOLVED QUESTIONS
1. **Physical UPS Telemetry Drivers on Linux Mini-PCs:** Specific USB driver compatibility between `apcupsd` and low-cost Indian 12V DC router UPS models must be empirically tested during hardware commissioning.
2. **Local PKI Certificate Distribution:** Seamless distribution of local facility TLS root certificates to unmanaged frontline Android tablets without manual browser warnings requires edge field testing.
3. **Cellular Partition Reconnect Throughput:** Real-world cellular sync journal transmission times over throttled 2G networks when reconnecting after a 14-day partition require field benchmarking in Phase 11.

---

## 36. RISKS
1. **Risk of Accidental Service-Role Key Deployment:** Developers may inadvertently set `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY`.  
   *Mitigation:* Automated CI build AST linting and Zod schema type assertions immediately fail compilation.
2. **Risk of Clinician Confusion Over Synthetic Data:** Clinicians testing the demo may confuse synthetic cases with real patients.  
   *Mitigation:* Persistent non-dismissible high-contrast "SYNTHETIC DEMO DATA" banner displayed across all screens.
3. **Risk of SQLite Lock Starvation Under Casualty Surges:** Multiple staff tablets submitting vitals concurrently could trigger write timeouts.  
   *Mitigation:* SQLite connection pool configures `PRAGMA busy_timeout = 5000;` and WAL mode; binary media stored on filesystem.

---

## 37. FILES CREATED
Phase 9 authored and committed all **thirty required authoritative configuration specifications** in `docs/research/`:
1. `docs/research/164_ENVIRONMENT_CONFIG_PLAN.md` (`RES-164`)
2. `docs/research/165_CONFIGURATION_SCHEMA.md` (`RES-165`)
3. `docs/research/166_SECRET_CLASSIFICATION.md` (`RES-166`)
4. `docs/research/167_FRONTEND_BACKEND_CONFIG_BOUNDARY.md` (`RES-167`)
5. `docs/research/168_DEV_ENVIRONMENT.md` (`RES-168`)
6. `docs/research/169_LOCAL_DEMO_ENVIRONMENT.md` (`RES-169`)
7. `docs/research/170_PHC_EDGE_ENVIRONMENT.md` (`RES-170`)
8. `docs/research/171_DISTRICT_HOSPITAL_ENVIRONMENT.md` (`RES-171`)
9. `docs/research/172_CLOUD_PREVIEW_ENVIRONMENT.md` (`RES-172`)
10. `docs/research/173_TEST_ENVIRONMENT.md` (`RES-173`)
11. `docs/research/174_CLINOVA_ENVIRONMENT_PROFILES.md` (`RES-174`)
12. `docs/research/175_ENVIRONMENT_ID_MODEL.md` (`RES-175`)
13. `docs/research/176_DATABASE_CONFIG_MODEL.md` (`RES-176`)
14. `docs/research/177_STORAGE_CONFIG_MODEL.md` (`RES-177`)
15. `docs/research/178_AI_CONFIG_BOUNDARY.md` (`RES-178`)
16. `docs/research/179_CORS_NETWORK_CONFIG.md` (`RES-179`)
17. `docs/research/180_OFFLINE_CONFIG_MODEL.md` (`RES-180`)
18. `docs/research/181_SYNTHETIC_DATA_MODE.md` (`RES-181`)
19. `docs/research/182_FEATURE_FLAG_MODEL.md` (`RES-182`)
20. `docs/research/183_LOGGING_CONFIG_MODEL.md` (`RES-183`)
21. `docs/research/184_CONFIG_FAILURE_MODEL.md` (`RES-184`)
22. `docs/research/185_CONFIGURATION_THREAT_MODEL.md` (`RES-185`)
23. `docs/research/186_EDGE_CONFIG_MODEL.md` (`RES-186`)
24. `docs/research/187_CLOUD_CONFIG_MODEL.md` (`RES-187`)
25. `docs/research/188_ZERO_COST_CONFIG_MODEL.md` (`RES-188`)
26. `docs/research/189_CONFIGURATION_VERSIONING.md` (`RES-189`)
27. `docs/research/190_CONFIGURATION_TRACEABILITY.md` (`RES-190`)
28. `docs/research/191_PHASE_9_CONCLUSION.md` (`RES-191`)
29. `docs/research/SOURCES_PHASE_9.md` (`SOURCES-PHASE-9`)
30. `docs/research/PHASE_9_DECISIONS.md` (`DECISION-LOG-PHASE-9`)

---

## 38. FILES MODIFIED
- None. (Phase 9 is strictly an additive architectural configuration, reconciliation, and specification phase).

---

## 39. FILES INTENTIONALLY UNTOUCHED
- `frontend/src/` (Zero UI components or client-side code implemented or modified).
- `backend/app/` (Zero production runtime backend code or AI inference modules modified).
- `backend/alembic/` (Zero database migrations created or applied to live instances).
- Active database instances (`clinova-dev.db` preserved intact; zero schema alterations executed).
- Upstream specifications (`docs/research/00_*` through `docs/research/163_*` preserved as immutable historical truth).

---

## 40. PHASE STATUS
**READY FOR HUMAN REVIEW**
