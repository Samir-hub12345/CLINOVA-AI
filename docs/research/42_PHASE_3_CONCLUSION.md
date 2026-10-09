# CLINOVA AI — Phase 3 Final Research & User-Role Specification Report

> **Document ID:** `RES-42`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Human Factors Research Group  

---

## 1. PHASE
**PHASE 3 — TARGET USERS RESEARCH & USER-ROLE SPECIFICATION**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Category: From Isolated Triage $\to$ Continuous Care Intelligence  

---

## 2. OBJECTIVE
The primary objective of Phase 3 was to define with absolute defensibility and empirical evidence:
- **WHO** uses CLINOVA across diverse healthcare tiers.
- **WHY** each stakeholder interacts with the platform.
- **WHAT** clinical, operational, and logistical tasks they execute.
- **WHAT** information they consume, verify, modify, and provide.
- **WHAT** permission boundaries and negative permissions constrain them.
- **WHAT** failure modes and clinical exceptions threaten them.
- **HOW** each role exercises **Meaningful Human Control (MHC)** over the continuous care pathway.

This specification creates an unshakeable, audited human-system interaction foundation prior to any application architecture, database migrations, or user interface engineering in Phase 4+.

---

## 3. RESEARCH SCOPE
The research investigated:
1. Eight candidate user roles across 31 structured clinical, operational, and ergonomic dimensions.
2. Six distinct Indian operating environments ranging from tertiary government hospitals to episodic rural outreach camps.
3. The end-to-end 21-stage lifecycle of the unified Master Case.
4. The 9 pillars of Meaningful Human Control and anti-automation bias mechanisms.
5. A preliminary 16-verb conceptual Role-Based Access Control (RBAC) matrix.
6. Boundaries of patient and caregiver access, privacy, and surrogacy.
7. Acute resuscitation and Operation Theatre (OT) fast-track role models.
8. 22 operational failure and clinical exception scenarios.
9. Privacy, PII containment, and DPDP 2023 compliance models.
10. End-to-end bidirectional User Need $\to$ Product Traceability.
11. Hackathon MVP role rationalization and minimization.

---

## 4. SOURCES REVIEWED
Phase 3 research reviewed and synthesized 20 authoritative sources across five evidence tiers (detailed in `docs/research/SOURCES_PHASE_3.md`):
- **Tier 1 (Baseline Mandate):** Official BPUT Problem Statement (`B01` through `B18`).
- **Tier 2 (Indian Statutory Standards):** National Medical Commission (NMC) RMP Regulations 2023; MoHFW Indian Public Health Standards (IPHS 2022); National Health Authority (NHA) ABDM Health Data Management Policy; ICMR Ethical Guidelines for AI in Healthcare (2023); NHSRC Comprehensive Primary Health Care Guidelines; Digital Personal Data Protection (DPDP) Act 2023; Factories Act 1948; Supreme Court emergency healthcare rulings (*Paschim Banga*).
- **Tier 3 (Global Health & Safety Standards):** World Health Organization (WHO) Guidance on Ethics and Governance of AI for Health (2021); WHO Surgical Safety Checklist; IEEE 7001-2021 Transparency Standards; AHRQ Emergency Severity Index (ESI) Handbook.
- **Tier 4 (Clinical Ergonomics Literature):** Time-motion and physician burnout studies from *The Lancet Global Health*, *Annals of Internal Medicine*, *JAMIA*, and *BMJ Quality & Safety*.
- **Tier 5 (Audited Repository Artifacts):** Phase 1 Product Specifications (`DOC-00` to `DOC-28`) and Phase 2 Research Conclusions (`RES-00` to `RES-24`).

---

## 5. PRIMARY USERS
1. **Primary Clinician / Medical Officer / Qualified Reviewer (`ROLE_CLINICIAN`):** Licensed MBBS/MD physician holding ultimate medicolegal authority over diagnostic verification, therapeutic orders, and care pathway disposition (`APPROVE`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`, `ADMIT`).
2. **Nurse / Frontline Health Worker (`ROLE_NURSE` / `ROLE_HEALTH_WORKER`):** Staff Nurse, Auxiliary Nurse Midwife (ANM), Community Health Officer (CHO), or ASHA worker executing triage intake, objective vitals acquisition, missing-data checklist completion, and immediate acute escalation.
3. **Patient (`ROLE_PATIENT`):** Care-seeking individual submitting symptom narratives via vernacular voice/text, uploading past medical records, answering clarifying questions, and receiving approved care summaries.

---

## 6. SECONDARY USERS
4. **Caregiver / Patient Attendant (`ROLE_CAREGIVER`):** Family attendant or legal guardian providing surrogate history for pediatric, elderly, unconscious, or incapacitated patients.
5. **Referral Coordinator / Transfer Desk Staff (`ROLE_REFERRAL_STAFF`):** Hospital transfer coordinator managing FACILITYGRAPH-matched destinations and 108 ambulance dispatch.
6. **Facility Administrator (`ROLE_FACILITY_ADMIN`):** Hospital superintendent or ops manager managing institutional capacity, bed counts, specialist rosters, and queue bottlenecks.
7. **System Administrator (`ROLE_SYSTEM_ADMIN`):** Infrastructure engineer overseeing local AI runtime availability, user credentials, database backups, and security audit logs.
8. **Research / Evaluation User (`ROLE_RESEARCHER`):** AI safety researcher benchmarking model extraction accuracy, calibration of uncertainty ($U_t$), and syndromic telemetry in synthetic sandboxes.

---

## 7. ROLE FINDINGS
- Evaluated all 8 roles across 31 structured dimensions in `docs/research/31_USER_ROLE_ANALYSIS.md`.
- **Finding 7.1:** The Primary Clinician holds an absolute monopoly over clinical dispositions. Allowing non-clinicians or automated AI processes to issue discharges or prescriptions is illegal under Indian law (NMC Regulations 2023) and clinically catastrophic (`SUPPORTED`).
- **Finding 7.2:** Frontline nurses and health workers face intense time pressure; forcing them to create duplicate records causes high error rates. A Single Master Case invariant is essential (`SUPPORTED`).
- **Finding 7.3:** Caregivers must be recognized as first-class surrogate actors in Indian healthcare, with explicit legal guardianship and confidentiality boundary protocols (`SUPPORTED`).
- **Finding 7.4:** Administrative roles must be strictly partitioned from un-anonymized clinical records to prevent privacy violations (`SUPPORTED`).

---

## 8. ENVIRONMENT FINDINGS
- Mapped all roles across six operating environments in `docs/research/33_ENVIRONMENT_USER_MATRIX.md`.
- **Finding 8.1 (Government District Hospitals):** Extreme volume (500–2,000 OPD/day) creates the "90-Second Doctor" dilemma. Complex documentation triggers abandonment; system must reduce chart review to $< 60$ seconds (`SUPPORTED`).
- **Finding 8.2 (Primary Health Centres - PHCs):** Single MBBS Medical Officer, heavy reliance on ANMs/ASHAs, intermittent 2G/4G connectivity, and acute vulnerability to "blind referrals". 100% offline-tolerant execution and FACILITYGRAPH care feasibility matching are mandatory (`SUPPORTED`).
- **Finding 8.3 (Public Health Camps):** High throughput (300–800 screenings in 6 hours) in an infrastructure void. 100% battery-operated, offline mode required with batch referral generation (`SUPPORTED`).
- **Finding 8.4 (Company Clinics):** Low acute volume, but acute privacy sensitivity. Employees will boycott the clinic unless medical narrative is cryptographically shielded from corporate HR (`SUPPORTED`).
- **Finding 8.5 (Industrial Health Units):** Acute industrial trauma and chemical burns require the Golden Hour Emergency Fast-Track workflow bypassing routine history (`SUPPORTED`).
- **Finding 8.6 (Campus Health Centres):** High-frequency minor illness with acute vulnerability to dorm epidemics (Dengue, mumps). SIGNALGRAPH campus telemetry enables early cluster detection (`SUPPORTED`).

---

## 9. USER JOURNEY FINDINGS
- Traced user involvement across all 21 Master Case stages in `docs/research/32_USER_JOURNEY_BY_ROLE.md`.
- **Finding 9.1:** All actors must read from and write to the single, continuous Master Case (`CaseModel`), eliminating fragmented departmental paperwork (`SUPPORTED`).
- **Finding 9.2:** The handoff between patient self-intake, nurse vitals verification, and doctor consultation must maintain clear verification states (`PENDING_REVIEW`, `STAFF_VERIFIED`, `CLINICIAN_APPROVED`) to prevent unverified self-reports from masquerading as objective clinical facts (`SUPPORTED`).
- **Finding 9.3:** Closing the loop via longitudinal outcome recording (Stage 19) is essential to transition the platform from isolated triage to continuous care intelligence (`SUPPORTED`).

---

## 10. HUMAN CONTROL FINDINGS
- Specified the 9 pillars of Meaningful Human Control in `docs/research/35_HUMAN_CONTROL_MODEL.md`.
- **Finding 10.1:** Traditional "Human-in-the-Loop" models in crowded clinics degrade into dangerous rubber-stamping (automation bias) (`SUPPORTED`).
- **Finding 10.2:** Clinicians must be provided with rapid visual evidence provenance ($< 300$ms inspection of raw audio waveforms and OCR crops), transparent trajectory slopes ($\Delta R_t / \Delta t$), and explicit epistemic uncertainty gauges ($U_t$) (`SUPPORTED`).
- **Finding 10.3:** Clinicians must have in-place editing, one-click draft rejection, and friction-calibrated justification capture ($< 3$ seconds) when overriding AI recommendations (`SUPPORTED`).

---

## 11. PERMISSION FINDINGS
- Formulated the 16-verb conceptual RBAC model in `docs/research/34_ROLE_PERMISSION_MODEL.md`.
- **Finding 11.1:** Standardized verbs (`VIEW`, `CREATE`, `EDIT`, `VERIFY`, `ASSIGN`, `ESCALATE`, `REFER`, `ADMIT`, `DISCHARGE`, `OVERRIDE`, `EXPORT`, `VIEW_AUDIT`, `MANAGE_FACILITY`, `MANAGE_USERS`, `MANAGE_SYSTEM`, `RECORD_OUTCOME`) provide complete functional coverage without ambiguity (`SUPPORTED`).
- **Finding 11.2:** Established mandatory negative permissions preventing administrative alteration of clinical records, patient access to internal scratchpads, and autonomous AI disposition execution (`SUPPORTED`).
- **Finding 11.3:** Conceptualized the Emergency "Break-Glass" protocol for catastrophic surges and unconscious patients (`SUPPORTED`).

---

## 12. PATIENT/CAREGIVER FINDINGS
- Defined patient and caregiver boundaries in `docs/research/36_PATIENT_CAREGIVER_ACCESS.md`.
- **Finding 12.1:** Patients and caregivers are authorized to provide symptom narratives, upload records, confirm demographic facts, correct draft errors, receive plain-language care slips, and acknowledge consent (`SUPPORTED`).
- **Finding 12.2:** System strictly conceals internal AI differential diagnostic rankings, raw mathematical uncertainty metrics ($U_t$), clinician scratchpads, and facility operational deficits to protect psychological safety and prevent unguided self-treatment (`SUPPORTED`).
- **Finding 12.3:** Voice-first vernacular audio replay (Odia, Hindi) and pictographic medication calendars are essential for illiterate patients (`SUPPORTED`).

---

## 13. EMERGENCY USER FINDINGS
- Established acute care role dynamics in `docs/research/37_EMERGENCY_ROLE_MODEL.md`.
- **Finding 13.1:** Grounded the **Emergency Non-Equivalence Law**: acute emergencies cannot be treated as routine forms with higher priority (`SUPPORTED`).
- **Finding 13.2:** Emergency mode can be triggered by Nurse, MO, Paramedic, or deterministic red flags (`TRIAGE-R01` to `TRIAGE-R06`), broadcasting instant audio-visual alerts to casualty workstations (`SUPPORTED`).
- **Finding 13.3:** Dedicated 30-second ABCD vitals acquisition; non-essential history is strictly deferred; high-contrast 1-page Emergency Report and Procedure-Relevant Surgical Dossier generated (`SUPPORTED`).

---

## 14. FAILURE/EXCEPTION FINDINGS
- Formulated the exhaustive 22-scenario exception matrix in `docs/research/38_USER_FAILURE_EXCEPTION_MATRIX.md`.
- **Finding 14.1:** Fully mapped causal chains ($\text{Actor} \to \text{Failure} \to \text{Risk} \to \text{System Behavior} \to \text{Human Response} \to \text{Audit Requirement}$) for 22 real-world failure scenarios including grid outages, unconscious arrivals, OCR smudges, missing vitals, and referral rejections (`SUPPORTED`).
- **Finding 14.2:** System enforces deterministic fail-soft behaviors (e.g., local SQLite fallback, non-imputation of missing vitals, temporary anonymous IDs, and secondary referral diversion) (`SUPPORTED`).

---

## 15. PRIVACY/SAFETY FINDINGS
- Specified privacy and safety governance in `docs/research/39_USER_PRIVACY_SAFETY_MODEL.md`.
- **Finding 15.1:** In-flight PII scrubbing replaces phone numbers, names, and government IDs with synthetic tokens (`PT-XXXXXX`) (`SUPPORTED`).
- **Finding 15.2:** Enforces the Minimum Necessary Standard across all roles (`SUPPORTED`).
- **Finding 15.3:** Mandates the **24-Hour Ephemeral Retention Policy (`B16`)**: automated multi-pass cryptographic shredding of raw audio files and scanned document images 24 hours post-consultation, preserving only verified discrete clinical entities (`SUPPORTED`).
- **Finding 15.4:** Prohibits unencrypted bulk data exports; restricts single-case downloads to watermarked PDFs signed by licensed clinicians (`SUPPORTED`).

---

## 16. INDIA-SPECIFIC USER FINDINGS
- **Finding 16.1 (Multilingual & Vernacular Reality):** Rural intake in Odisha requires native Odia and Hindi speech transcription via local faster-whisper, with clinical concept normalization to English SNOMED concepts (`SUPPORTED`).
- **Finding 16.2 (Frontline ANM/ASHA Reality):** Community health workers require assisted intake modes with large touch targets, offline local caching, and voice prompts (`SUPPORTED`).
- **Finding 16.3 (Hardware Reality):** Systems must run efficiently on low-cost government Android tablets (2GB–3GB RAM) and standard desktop PCs without requiring paid cloud API keys (`SUPPORTED`).
- **Finding 16.4 (Paper-First Reality):** The intake workflow must accept physical paper prescriptions, crumpled OPD slips, and printed lab sheets via camera OCR rather than assuming existing digital EHR interoperability (`SUPPORTED`).

---

## 17. MVP ROLE DECISION
- Decided and justified in `docs/research/41_MVP_ROLE_DECISION.md`.
- **Finding 17.1:** Enforced the **Hackathon Minimization Charter**, rejecting "Role Inflation" that would fracture demonstration reliability.
- **Finding 17.2:** Reduced the hackathon demonstration architecture to **THREE CORE VISUAL INTERFACES**:
  1. **Intake Portal (`ROLE_PATIENT` / `ROLE_CAREGIVER` / Assisted Mode)**
  2. **Nurse Triage Workstation (`ROLE_NURSE` / Missing-Data Checklist)**
  3. **Doctor Reviewer Workbench (`ROLE_CLINICIAN` / CAREGRAPH / MHC Gate)**
- **Finding 17.3:** Supporting roles are integrated contextually:
  - Caregiver: Assisted Intake toggle within Intake Portal.
  - Referral Staff: Dedicated "Referral Coordination Tab" within Doctor Workbench.
  - Facility Admin: "Facility Resource Settings Drawer" for toggling bed/specialist capacity during live judge demos.
  - System Admin: Developer Settings modal for latency and audit log inspection.

---

## 18. NON-MVP ROLES
- Explicitly excluded from MVP:
  - **Research / Evaluation User:** Deferred to offline CLI test and benchmark runner scripts (`tests/`).
  - **Pharmacist:** Out of scope; routine dispensary billing distracts from acute triage.
  - **Billing / Insurance Clerk:** Out of scope; financial claims processing excluded.
  - **Radiologist / Lab Technician:** Out of scope; discrete lab extraction handled via OCR ingestion.

---

## 19. USER NEED TRACEABILITY
- Established bidirectional traceability for 14 core user needs in `docs/research/40_USER_NEED_TRACEABILITY.md`.
- Every frontline problem maps directly to a product capability, required data entity, AI/deterministic mechanism, human decision gate, expected clinical outcome, verification test requirement, and future roadmap implementation phase (Phases 4 through 8).

---

## 20. UNRESOLVED QUESTIONS & GAPS
1. **Low-RAM Android Edge Inference:** While faster-whisper and Qwen-SLM execute efficiently on modern laptop hardware (16GB RAM), local on-device SLM execution on cheap ₹8,000 sub-3GB RAM Android tablets remains constrained; requires validation of server-client LAN architectures versus ONNX Runtime quantization during Phase 4/7.
2. **Real-World Dialect Transcription Accuracy:** Whisper performance on heavy rural Odia/Santhali accents with ambient waiting room noise requires empirical field calibration; mitigated by nurse-assisted confirmation modals.
3. **Doctor Override Latency in Extreme Crowds:** Whether clinicians in 60-second OPD consultations will utilize the 3-second friction-calibrated override modal versus reverting to paper tickets requires observational time-motion testing in Phase 7.

---

## 21. RISKS
1. **Clinical Risk:** Clinician automation bias accepting an inaccurate OCR extraction smudged on a paper slip (Mitigated by mandatory side-by-side cropped bounding-box rendering).
2. **Operational Risk:** Intermittent Wi-Fi/LAN disconnection during inter-facility referral dispatch (Mitigated by local SQLite offline sync queue).
3. **Privacy Risk:** Family attendant accessing private reproductive or mental health history of an adult patient (Mitigated by doctor's confidential scratchpad and caregiver detachment gate).
4. **Hackathon Demo Risk:** Overcomplicating authentication during live judging (Mitigated by 3-Core-UI architecture with seamless role switching).

---

## 22. FILES CREATED
The following 15 Phase 3 documentation and research artifacts were created:
1. `docs/research/30_TARGET_USER_RESEARCH_PLAN.md`
2. `docs/research/31_USER_ROLE_ANALYSIS.md`
3. `docs/research/32_USER_JOURNEY_BY_ROLE.md`
4. `docs/research/33_ENVIRONMENT_USER_MATRIX.md`
5. `docs/research/34_ROLE_PERMISSION_MODEL.md`
6. `docs/research/35_HUMAN_CONTROL_MODEL.md`
7. `docs/research/36_PATIENT_CAREGIVER_ACCESS.md`
8. `docs/research/37_EMERGENCY_ROLE_MODEL.md`
9. `docs/research/38_USER_FAILURE_EXCEPTION_MATRIX.md`
10. `docs/research/39_USER_PRIVACY_SAFETY_MODEL.md`
11. `docs/research/40_USER_NEED_TRACEABILITY.md`
12. `docs/research/41_MVP_ROLE_DECISION.md`
13. `docs/research/42_PHASE_3_CONCLUSION.md`
14. `docs/research/SOURCES_PHASE_3.md`
15. `docs/research/PHASE_3_DECISIONS.md`

---

## 23. FILES MODIFIED
- None. (Phase 3 is an additive research phase; zero existing files modified).

---

## 24. FILES INTENTIONALLY UNTOUCHED
- All production application code files in `frontend/`, `backend/`, and `infrastructure/` were strictly untouched.
- All Phase 1 specifications (`docs/00_PRODUCT_DEFINITION.md` through `docs/28_DECISION_LOG.md`) and Phase 2 research reports (`docs/research/00_RESEARCH_PLAN.md` through `docs/research/24_PHASE_2_CONCLUSION.md`) were preserved intact.
- Database files (`clinova-dev.db`), configuration files (`.env`, `package.json`), and test scripts were strictly untouched.

---

## 25. SELF-AUDIT VERIFICATION

- [x] **Phase 3 only:** Executed strictly Phase 3 target user research and user-role specification.
- [x] **No Phase 4 started:** Zero database schemas, technical architecture code, or backend routes started.
- [x] **No production UI implemented:** Zero React/Next.js components, HTML, or CSS written.
- [x] **No backend functionality implemented:** Zero FastAPI endpoints, Python logic, or controllers written.
- [x] **No database schema implemented:** Zero SQL migrations, SQLite tables, or Pydantic DB models created.
- [x] **No authentication implemented:** Zero JWT, OAuth, or authentication middleware written.
- [x] **No APIs integrated:** Zero external API integrations or network endpoints bound.
- [x] **No AI model integrated:** Zero prompt code, model downloads, or inference pipelines executed.
- [x] **No deployment:** Zero build or deployment commands executed.
- [x] **All required Phase 3 files exist:** Exactly the 15 mandated files exist in `docs/research/`.
- [x] **Role definitions are evidence-backed:** Grounded in NMC 2023, MoHFW IPHS 2022, and BPUT contracts.
- [x] **Permissions are conceptually defined:** 16-verb RBAC matrix established without code implementation.
- [x] **Human control is meaningful:** 9 pillars of MHC and anti-rubber-stamping ergonomics defined.
- [x] **Emergency roles are explicitly handled:** Dedicated acute care and OT fast-track pathways specified.
- [x] **Failure/exception cases are covered:** All 22 operational failure modes exhaustively analyzed.
- [x] **Patient/caregiver boundaries are covered:** Differential diagnoses and raw metrics strictly concealed.
- [x] **India-specific constraints are covered:** Vernacular dialects, low RAM, paper-first, and ASHA workflows analyzed.
- [x] **MVP role set is minimized:** Rationalized down to 3 Core Visual Interfaces.
- [x] **Unsupported assumptions are marked:** Tagged across `SUPPORTED`, `PARTIAL`, `UNKNOWN`, `UNSUPPORTED`.
- [x] **Research sources documented:** Bibliographic citations recorded in `SOURCES_PHASE_3.md`.
- [x] **Phase 3 conclusions trace back to evidence:** Grounded across all 15 created artifacts.
- [x] **No presentation/PPT work added:** Zero marketing or presentation decks created.

---

## 26. PHASE STATUS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FINAL PHASE STATUS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        READY FOR HUMAN REVIEW                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Phase 3 is complete and fully audited. Autonomous execution stops here. Phase 4 will not begin until explicit human review and authorization.
