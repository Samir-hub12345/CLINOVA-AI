# CLINOVA AI — Phase 5 Final Master Patient Journey & End-to-End Care Pathway Specification Report

> **Document ID:** `RES-77`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. PHASE
**PHASE 5 — MASTER PATIENT JOURNEY & END-TO-END CARE PATHWAY SPECIFICATION**  
Project: CLINOVA AI (Adaptive Clinical Care Intelligence & Navigation Platform)  
Positioning: *From Isolated Triage $\longrightarrow$ Continuous Care Intelligence*  

---

## 2. OBJECTIVE
The primary objective of Phase 5 is to establish with empirical defensibility, mathematical precision, and clinical rigor the complete **Master Patient Journey** from initial clinical presentation through outcome resolution and closed-loop feedback.

The journey models care as:
- **CONTINUOUS:** Triage is never an isolated sorting event; it is an evolving trajectory across multiple human handoffs.
- **STATEFUL:** Governed by an authoritative 27-state deterministic finite state machine.
- **HUMAN-CONTROLLED:** Registered medical practitioners retain absolute monopoly over clinical decisions.
- **EVIDENCE-AWARE:** Every clinical entity carries unalterable visual provenance pointers to raw inputs.
- **UNCERTAINTY-AWARE:** Missing data is explicitly scored ($U_t$) and never imputed as normal or negative.
- **ENVIRONMENT-AWARE:** Adapts across 6 operational settings through configuration without codebase fragmentation.
- **RESOURCE-AWARE:** Recommendations are grounded in verified real-time facility capabilities ($\text{FACILITYGRAPH}$).
- **OUTCOME-AWARE:** Tracks what happens *after* the decision to close the learning loop for $\text{CAREGRAPH}$ and $\text{SIGNALGRAPH}$.

---

## 3. SOURCE MATERIAL
Phase 5 reconciled and synthesized 20 authoritative statutory, clinical, and architectural sources (cataloged in `docs/research/SOURCES_PHASE_5.md`):
- **Statutory Indian Guidelines:** Indian Public Health Standards (IPHS 2022) for District Hospitals and Primary Health Centres; National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Section 27); Digital Personal Data Protection (DPDP) Act 2023 (Sections 4, 6, 9); Supreme Court emergency health rulings (*Paschim Banga* doctrine).
- **Clinical & Safety Standards:** ICMR Ethical Guidelines for AI in Healthcare (2023); WHO Essential Emergency and Critical Care (EECC) framework; AHRQ Emergency Severity Index (ESI Version 4); WHO Surgical Safety Checklist; National Early Warning Score (NEWS2).
- **Internal Repository Artifacts:** Phase 1 Architecture (`DOC-00` to `DOC-28`), Phase 2 Gap Audits (`RES-00` to `RES-24`), Phase 3 User Roles (`RES-30` to `RES-42`), Phase 4 Environments (`RES-43` to `RES-56`), and Phase 5 Decision Log (`PHASE_5_DECISIONS.md`).

---

## 4. MASTER JOURNEY
Specified in `docs/research/58_MASTER_PATIENT_JOURNEY.md` (`RES-58`):
- Replaces transactional triage with an end-to-end continuous care continuum.
- Unifies multimodal ingestion, entity extraction, visual review, timeline construction, information sufficiency gating, frontline nurse point-of-care verification, CAREGRAPH synthesis, doctor review, facility feasibility check, orchestration advice, pathway execution, and closed-loop outcome tracking.
- Establishes the chain of custody across five human actor tiers: Patient/Caregiver $\to$ Frontline Health Worker / Triage Nurse $\to$ Attending Clinician $\to$ Ward Nurse / Paramedic / Scrub Team $\to$ Receiving Clinician.

---

## 5. REGULAR PATHWAY
Specified in `docs/research/59_REGULAR_PATHWAY.md` (`RES-59`):
- 17-step end-to-end pipeline governing non-emergent ambulatory and outpatient presentations.
- Ingests regional vernacular voice (Odia, Hindi, English), free text, and uploaded prescription slips.
- Implements visual extraction review with side-by-side snippet previews ($< 300\text{ms}$).
- Formulates chronological timeline and audits missing data.
- Enforces the mathematical sufficiency gate ($S \ge 0.85$); automatically diverts cases with missing critical vitals to the Nurse Missing-Data Worklist for point-of-care BP, SpO2, HR, and RR verification.
- Enriches case into Doctor Review Workbench with 7 unified panels, enabling `VERIFY`, `MODIFY`, and `ADD`.

---

## 6. EMERGENCY PATHWAY
Specified in `docs/research/60_EMERGENCY_PATHWAY.md` (`RES-60`):
- Operates under the inviolable doctrine: **"Clinical Resuscitation BEFORE Administrative Completion"**.
- Bypasses non-essential administrative registration, billing entries, prior document OCR, and multi-turn Q&A.
- Instantly provisions Master Case in $< 200\text{ms}$ with an Anonymous Emergency Token (`EMG-YYYYMMDD-XXXX`) and Priority P1 tag.
- Enforces statutory Emergency Implied Consent.
- Compresses clinical evaluation into a 30-second rapid ABCD vital signs protocol.
- Executes sub-50ms deterministic safety rules ($\text{SpO}_2 < 85\%$, $\text{Shock Index} > 1.0$, pediatric stridor, massive trauma).
- Generates high-contrast Single-Page Emergency Report (`Report Type 5`).
- Preserves single case continuity via post-stabilization cryptographic identity binding.

---

## 7. STATE MACHINE RESULT
Specified in `docs/research/61_MASTER_CASE_STATE_MACHINE.md` (`RES-61`):
- Evaluated candidate states and established a formal 6-tuple Finite State Machine containing **27 Canonical States**:
  `S01: STATE_NEW`, `S02: STATE_INTAKE_COLLECTING`, `S03: STATE_EXTRACTING`, `S04: STATE_EXTRACTION_REVIEW`, `S05: STATE_MISSING_AUDIT`, `S06: STATE_FOLLOW_UP_PENDING`, `S07: STATE_STAFF_DATA_PENDING`, `S08: STATE_STAFF_VERIFIED`, `S09: STATE_CONSOLIDATED`, `S10: STATE_TRIAGE_READY`, `S11: STATE_DOCTOR_QUEUED`, `S12: STATE_DOCTOR_REVIEWING`, `S13: STATE_CLINICIAN_VERIFIED`, `S14: STATE_FACILITY_EVALUATING`, `S15: STATE_ORCHESTRATION_PENDING`, `S16: STATE_ROUTINE_CARE`, `S17: STATE_FURTHER_REVIEW`, `S18: STATE_WARD_REQUESTED`, `S19: STATE_WARD_ADMITTED`, `S20: STATE_REFERRAL_PENDING`, `S21: STATE_TRANSFER_IN_TRANSIT`, `S22: STATE_EMERGENCY_ACTIVE`, `S23: STATE_OT_PENDING`, `S24: STATE_OT_HANDOFF`, `S25: STATE_OUTCOME_PENDING`, `S26: STATE_RESOLVED`, `S27: STATE_CLOSED`.
- Every state defines: Entry condition, Exit condition, Allowed actors, Required data, Optional data, Safety gate, Audit event, Failure behavior, Re-entry behavior, Downstream consequence.

---

## 8. TRANSITION MODEL
Specified in `docs/research/62_JOURNEY_TRANSITION_MATRIX.md` (`RES-62`):
- Catalogs 42 comprehensive transition rules across normal, incomplete, failure, exception, rollback, and emergency jump flows.
- Models optimistic concurrency control using version vectors to handle simultaneous edits.
- Formalizes break-glass emergency escalation from any active state to `STATE_EMERGENCY_ACTIVE`.

---

## 9. INFORMATION SUFFICIENCY
Specified in `docs/research/63_INFORMATION_SUFFICIENCY_MODEL.md` (`RES-63`):
- Establishes the **Zero-Imputation Law**: Absence of evidence is NEVER evidence of absence; missing clinical parameters are permanently tagged as `UNKNOWN`.
- Formalizes 6 explicit operational sufficiency states: `SUFFICIENT`, `PARTIALLY_SUFFICIENT`, `INSUFFICIENT`, `CONFLICTING`, `UNRELIABLE`, `EMERGENCY_OVERRIDDEN`.
- Weighting formula stratifies parameters into Tier 1 Critical ($w=3.0$), Tier 2 Important ($w=1.5$), and Tier 3 Optional ($w=0.5$).
- Hard blocks unverified critical vitals from reaching doctor review without staff point-of-care acquisition.

---

## 10. MASTER CASE INVARIANT
Specified across all Phase 5 specifications:
- **One Master Case Invariant:** Every encounter has exactly one `case_id` UUIDv4.
- Voice recordings, OCR images, nursing vitals, doctor notes, referral manifests, ward charts, surgical checklists, and outcomes attach directly to the same case.
- Handles duplicate cases via algorithmic deduplication, wrong-patient mismatches via session rollback, unknown identities via ephemeral tokens, and late identity discovery via cryptographic identity binding.

---

## 11. EVIDENCE / PROVENANCE JOURNEY
- Every clinical entity carries an immutable provenance tag:
  `PATIENT_REPORTED` $\longrightarrow$ `VOICE_TRANSCRIBED` / `OCR_EXTRACTED` $\longrightarrow$ `STAFF_VERIFIED` $\longrightarrow$ `CLINICIAN_APPROVED`.
- Parameters are tracked in discrete epistemic states: `KNOWN`, `UNKNOWN`, `CONFLICTING`, `UNRELIABLE`, `VERIFIED`, `INFERRED`.
- Visual provenance displays bounding box crops and audio playback directly on the Doctor Workbench.

---

## 12. CAREGRAPH JOURNEY
Specified in `docs/research/64_CAREGRAPH_JOURNEY.md` (`RES-64`):
- Tracks the evolution of $\mathcal{G}_{\text{care}}(t)$ across 9 operational milestones.
- Calculates dynamic physiological risk score, disease trajectory ($\boldsymbol{\tau}_t \in \{\text{IMPROVING}, \text{STABLE}, \text{DETERIORATING}, \text{CRITICAL}\}$), and epistemic uncertainty ($U_t \in [0.0, 1.0]$).
- Recalculates dynamically upon nursing point-of-care vitals, doctor physical exam findings, and serial inpatient observations.

---

## 13. FACILITYGRAPH JOURNEY
Specified in `docs/research/65_FACILITYGRAPH_JOURNEY.md` (`RES-65`):
- Evaluates real-time patient requirements against regional facility resources to compute Feasibility Index $\Phi_{\text{feasibility}} \in [0.0, 1.0]$.
- Invoked during emergency triage, doctor review HUD, care feasibility check, ward bed allocation, inter-facility referral, and surgical theatre audit.
- Eliminates "blind transfers" through verified destination matching and pre-arrival dossier transmission.

---

## 14. ORCHESTRATION JOURNEY
Specified in `docs/research/66_ORCHESTRATION_JOURNEY.md` (`RES-66`):
- Evaluates six canonical advisory actions: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- Couples biological state ($\text{CAREGRAPH}$) with operational resources ($\text{FACILITYGRAPH}$).
- Operates under the **Advisory-Only Invariant**: AI cannot execute clinical dispositions autonomously.

---

## 15. ROUTINE CARE
Specified in `docs/research/67_ROUTINE_CARE_PATH.md` (`RES-67`):
- Pathway A: Generates Routine / Follow-Up Pack (`Report Type 3`), e-prescriptions, and embeds dates into recurring outpatient calendar.
- Distinct Pathway B (Further Review): Single targeted revisit slot within $\le 7$ days for pending investigations or 24-48h reassessment. Resumes the **SAME Master Case** upon revisit check-in.

---

## 16. WARD ADMISSION
Specified in `docs/research/68_WARD_ADMISSION_PATH.md` (`RES-68`):
- Pathway C: Generates Inpatient Ward Dossier (`Report Type 4`), automated medication list, allergy warnings, and inpatient precautions.
- Enforces two-party SBAR (Situation, Background, Assessment, Recommendation) handoff sign-off between transferring and receiving ward staff.

---

## 17. REFERRAL / TRANSFER
Specified in `docs/research/69_REFERRAL_TRANSFER_PATH.md` (`RES-69`):
- Pathway D: Ranks regional receiving hospitals, compiles Digital Referral Pack (`Report Type 2`), enforces telephonic/digital receiving confirmation, and matches BLS/ALS transport.
- Explicitly handles referral rejections, destination saturation, and Against Medical Advice (AMA) refusal.

---

## 18. OT PATHWAY
Specified in `docs/research/70_OT_PATHWAY.md` (`RES-70`):
- Pathway F: Surgical Fast-Track governed by Ergonomic Filtering (suppressing general outpatient text in favor of airway, NPO, and cross-match data).
- Enforces WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out) and dual clinician sign-off.
- Generates Operative Report (`Report Type 6`).

---

## 19. OUTCOME LOOP
Specified in `docs/research/71_OUTCOME_LOOP_JOURNEY.md` (`RES-71`):
- Decouples Planned Advice vs Actual Clinician Decision vs Actual Care Action vs Real-World Clinical Outcome.
- Tracks clinician adoption: `ACCEPTED`, `MODIFIED`, `OVERRIDDEN`, `REJECTED`, `NOT_COMPLETED`.
- 6-tier outcome taxonomy: `FULL_RECOVERY`, `STABILIZED`, `COMPLICATION_MANAGED`, `REFERRED_HIGHER`, `CRITICAL_TRANSFER`, `ADVERSE_EVENT`.
- Two-tier feedback: updates individual CAREGRAPH delta and emits macro telemetry to $\text{SIGNALGRAPH}$.

---

## 20. FAILURE / EXCEPTION FINDINGS
Specified in `docs/research/72_JOURNEY_FAILURE_EXCEPTION_MATRIX.md` (`RES-72`):
- Comprehensive matrix covering **31 discrete failure scenarios** across infrastructure, hardware, identity, clinical inputs, facility logistics, staffing, and data synchronization.
- All failures specify: Current State, Safety Risk, Automated System Response, Human Clinical Response, Recovery State, and Audit Event.

---

## 21. PERMISSION FINDINGS
Specified in `docs/research/73_JOURNEY_PERMISSION_MATRIX.md` (`RES-73`):
- Governs 11 clinical actions across 6 actor roles.
- Establishes Registered Medical Practitioner (`ROLE_CLINICIAN`) monopoly over diagnoses, prescriptions, surgical bookings, admissions, referrals, and discharges.
- Strict administrative air-gap under DPDP Act; advisory-only boundary for AI; auditable break-glass emergency escalation.

---

## 22. ENVIRONMENT FINDINGS
Specified in `docs/research/74_ENVIRONMENT_JOURNEY_MATRIX.md` (`RES-74`):
- Confirms the Single Codebase Doctrine: All 6 environments execute the exact same 27-state machine.
- Demonstrates environmental modulation via configuration profiles and resource matrices without code bifurcation.

---

## 23. MVP JOURNEY
Specified in `docs/research/75_MVP_JOURNEY.md` (`RES-75`):
- Establishes the Dual-Facility Public Healthcare Demonstration Corridor:
  $$\mathbf{Peripheral\ Rural\ PHC\ (Spoke)} \quad \overset{\text{FACILITYGRAPH Transfer}}{\Longrightarrow} \quad \mathbf{District\ Government\ Hospital\ (Hub)}$$
- Scenario 1 (Regular to Referral): Proves vernacular intake $\to$ visual review $\to$ missing vitals divert $\to$ nurse bedside check $\to$ CAREGRAPH $\to$ doctor review $\to$ facility deficit check $\to$ capability-matched referral $\to$ zero-reentry reception at district hospital $\to$ outcome.
- Scenario 2 (Emergency Fast-Track): Proves $< 200\text{ms}$ tokenization, 30s ABCD vitals, deterministic red-flag firing, and resuscitation stabilization.

---

## 24. SIMPLIFIED JOURNEY
To enable instantaneous comprehension by hackathon judges, the journey is distilled into a 1-page visual flow classifying every stage:
- **MANDATORY:** Consent, Multimodal Ingestion, Visual Review, Sufficiency Gate, Doctor Review, Disposition.
- **CONDITIONAL:** Staff Point-of-Care Vitals (only if sufficiency $< 0.85$), Follow-Up Q&A.
- **OPTIONAL:** Prior historical document OCR upload.
- **DEFERRED:** Detailed lifestyle and demographic billing during acute emergencies.
- **EMERGENCY-BYPASSED:** Routine follow-up questions, non-critical document OCR, billing gates.
- **FUTURE:** Automated wearable sensor telemetry integration.

---

## 25. TRACEABILITY
Specified in `docs/research/76_JOURNEY_TRACEABILITY.md` (`RES-76`):
- Complete 26-row bidirectional matrix mapping Journey Stage $\to$ User Role $\to$ Environment $\to$ Input $\to$ Data State $\to$ AI/Rule Support $\to$ Human Decision $\to$ Next State $\to$ Safety Control $\to$ Audit Event $\to$ Output Artifact $\to$ Implementation Phase.

---

## 26. UNRESOLVED QUESTIONS
1. *Empirical WAN Latency Distributions during Monsoon:* Real-world 4G uplink latency during severe weather across tribal PHCs in Odisha requires live pilot measurement.
2. *Mini-PC Fanless Thermal Limits:* Sustained thermal stability of local edge Mini-PCs running quantized Faster-Whisper under 42°C ambient heat in non-AC rural clinics requires physical bench testing.
3. *State-Specific Medico-Legal Registers:* Statutory variations in police Medico-Legal Case (MLC) physical paper register requirements across Indian states require legal verification before multi-state rollout.

---

## 27. RISKS
1. **Automation Bias in High-Throughput OPDs:** Doctors rubber-stamping advisory notes under extreme time pressure; mitigated by mandatory visual provenance preview and friction-calibrated override logging.
2. **Device Hardware Starvation:** Older hospital desktop PCs (2GB RAM) freezing under heavy frontends; mitigated by strict lightweight server-side rendered / thin-client web standards.
3. **Stale Referral Capability Telemetry:** Receiving hospitals failing to update bed availability; mitigated by automatic status degradation to `STALE` after 12 hours and mandatory telephonic confirmation gates.

---

## 28. FILES CREATED
Phase 5 created all 23 authoritative research, specification, and decision documents in `docs/research/`:
1. `docs/research/57_MASTER_JOURNEY_RESEARCH_PLAN.md` (`RES-57`)
2. `docs/research/58_MASTER_PATIENT_JOURNEY.md` (`RES-58`)
3. `docs/research/59_REGULAR_PATHWAY.md` (`RES-59`)
4. `docs/research/60_EMERGENCY_PATHWAY.md` (`RES-60`)
5. `docs/research/61_MASTER_CASE_STATE_MACHINE.md` (`RES-61`)
6. `docs/research/62_JOURNEY_TRANSITION_MATRIX.md` (`RES-62`)
7. `docs/research/63_INFORMATION_SUFFICIENCY_MODEL.md` (`RES-63`)
8. `docs/research/64_CAREGRAPH_JOURNEY.md` (`RES-64`)
9. `docs/research/65_FACILITYGRAPH_JOURNEY.md` (`RES-65`)
10. `docs/research/66_ORCHESTRATION_JOURNEY.md` (`RES-66`)
11. `docs/research/67_ROUTINE_CARE_PATH.md` (`RES-67`)
12. `docs/research/68_WARD_ADMISSION_PATH.md` (`RES-68`)
13. `docs/research/69_REFERRAL_TRANSFER_PATH.md` (`RES-69`)
14. `docs/research/70_OT_PATHWAY.md` (`RES-70`)
15. `docs/research/71_OUTCOME_LOOP_JOURNEY.md` (`RES-71`)
16. `docs/research/72_JOURNEY_FAILURE_EXCEPTION_MATRIX.md` (`RES-72`)
17. `docs/research/73_JOURNEY_PERMISSION_MATRIX.md` (`RES-73`)
18. `docs/research/74_ENVIRONMENT_JOURNEY_MATRIX.md` (`RES-74`)
19. `docs/research/75_MVP_JOURNEY.md` (`RES-75`)
20. `docs/research/76_JOURNEY_TRACEABILITY.md` (`RES-76`)
21. `docs/research/77_PHASE_5_CONCLUSION.md` (`RES-77`)
22. `docs/research/SOURCES_PHASE_5.md`
23. `docs/research/PHASE_5_DECISIONS.md`

---

## 29. FILES MODIFIED
- None. (Phase 5 is strictly additive journey analysis, safety specification, and operational modeling).

---

## 30. FILES INTENTIONALLY UNTOUCHED
- `frontend/` (Zero production UI code modified or created).
- `backend/` (Zero production backend business logic created).
- Database migrations & schema definitions (Zero database schemas altered).
- `docs/research/00_*` through `24_*` (Phase 2 audit files preserved as immutable historical evidence).
- `docs/research/30_*` through `42_*` (Phase 3 user role files preserved as immutable historical evidence).
- `docs/research/43_*` through `56_*` (Phase 4 environment files preserved as immutable historical evidence).
- Phase 1 documentation (`docs/00_*` through `docs/28_*` preserved as locked source of truth).

---

## 31. PHASE STATUS
**READY FOR HUMAN REVIEW**
