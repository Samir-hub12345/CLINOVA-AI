# CLINOVA AI — Phase 5 Formal Decision Log

> **Document ID:** `DECISION-LOG-PHASE-5`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Governance & Decision Framework

The Phase 5 Decision Log documents the definitive clinical, architectural, and operational resolutions reached during the Master Patient Journey and Care Pathway modeling.

Every decision is evaluated against:
1. **Clinical Safety & Patient Autonomy** (NMC Regulations 2023, ICMR AI Ethics Guidelines 2023).
2. **Statutory Legal Compliance** (DPDP Act 2023, IPHS 2022, Supreme Court *Paschim Banga* doctrine).
3. **Architectural Coherence & Zero Code Bifurcation** (Single Master Case, Single Codebase).
4. **Resilience under Resource Scarcity** (Offline local LAN, anti-blind-transfer verification).

---

## 2. Definitive Phase 5 Decisions (Decisions 5.1 – 5.10)

---

### Decision 5.1: The Inviolable Single Master Case Invariant
- **Context:** Healthcare software frequently fractures a patient's visit into isolated records—triage creates one ticket, the doctor opens another, the referral desk spawns a third, and the ward opens a fourth. This causes lost allergies, conflicting medication lists, and uncoordinated transfers.
- **Decision:** CLINOVA enforces the **Single Master Case Invariant**. Every encounter is allocated exactly one `case_id` UUIDv4. All multimodal inputs, OCR crops, nursing vitals, doctor modifications, facility feasibility evaluations, referral manifests, ward charts, and real-world outcomes MUST attach directly to this single Master Case.
- **Safety Boundary:** No subsystem or staff member may spawn a secondary, disconnected patient case for the same clinical episode.

---

### Decision 5.2: Dual-Track Entry Decoupling & Acute Resuscitation Priority
- **Context:** Enforcing a lengthy administrative intake, comprehensive document scanning, and multi-turn questionnaire on a patient in cardiac arrest or hypovolemic shock is fatal.
- **Decision:** The Master Journey immediately decouples upon presentation into the **Regular / Routine Pathway** and the **Emergency Fast-Track Pathway**. Emergency cases operate under the doctrine: **"Clinical Resuscitation BEFORE Administrative Completion"**.
- **Safety Boundary:** Emergency presentation bypasses non-essential demographics, billing entries, and routine follow-up Q&A. The case is provisioned in $< 200\text{ms}$ with an Anonymous Emergency Token (`EMG-XXXX`) and Priority P1 badge. Routine cases can dynamically escalate to emergency at any intermediate state.

---

### Decision 5.3: Minimization to 27 Canonical States in Finite State Machine
- **Context:** Candidate state proposals contained vague, overlapping milestones (e.g., separating "VERIFICATION_PENDING" from nurse sign-off, or creating redundant referral states).
- **Decision:** Formalized a minimal, deterministic 6-tuple Finite State Machine comprising exactly **27 Canonical States** (`S01: STATE_NEW` through `S27: STATE_CLOSED`). Evaluated every state through formal `KEEP`, `MERGE`, `SPLIT`, `REMOVE`, and `ADD` criteria.
- **Safety Boundary:** States are mutually exclusive; transitions require explicit actor authorization, data completeness gates, and immutable audit events.

---

### Decision 5.4: Epistemic Sufficiency Thresholding & The Zero-Imputation Law
- **Context:** Standard medical software often treats empty fields as negative or normal (e.g., if blood pressure is blank, the algorithm assumes normal hemodynamics).
- **Decision:** Enforced the **Zero-Imputation Law**: Absence of evidence is NEVER evidence of absence. Missing parameters are permanently stored as `UNKNOWN`. Established mathematical sufficiency metric:
  $$S = \frac{\sum w_i \cdot \delta_i}{\sum w_i} \ge 0.85$$
- **Safety Boundary:** If $S < 0.85$ OR any Critical Vital (BP, SpO2, HR, RR) is `UNKNOWN`, the system hard-blocks automatic doctor queue promotion and diverts the case to the **Nurse Missing-Data Worklist** for calibrated physical measurement.

---

### Decision 5.5: Procedural Information Ergonomics in the Operation Theatre (OT) Pathway
- **Context:** In acute surgical crises (e.g., ruptured ectopic pregnancy, hemoperitoneum), surgical scrub nurses and anesthesiologists cannot waste cognitive bandwidth reading 5 pages of outpatient history.
- **Decision:** The OT Fast-Track Pathway enforces **Procedure-Relevant Ergonomic Filtering**. The OT interface strictly suppresses non-acute text and surfaces only critical surgical parameters: Airway (Mallampati), NPO fasting time, blood group and cross-match hold, coagulation profile, and active anticoagulant therapies.
- **Safety Boundary:** The system CANNOT independently authorize surgical bookings. OT initiation requires surgeon authorization and adherence to the 3-phase WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out).

---

### Decision 5.6: Advisory Orchestration Boundary & Meaningful Human Control
- **Context:** Algorithmic systems that automatically route, discharge, or refer patients without doctor oversight violate the NMC Registered Medical Practitioner Regulations 2023 and create immense liability.
- **Decision:** The Orchestration Engine is strictly **ADVISORY**. It evaluates six canonical actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`) and surfaces the **Safest Achievable Care Pathway**, but CANNOT autonomously execute orders.
- **Safety Boundary:** Only a credentialed Registered Medical Practitioner (`ROLE_CLINICIAN`) can authorize medical prescriptions, inpatient ward admissions, inter-facility transfers, surgical bookings, and hospital discharges.

---

### Decision 5.7: Closed-Loop Outcome Architecture & Reality-Grounding
- **Context:** Existing triage tools end when a category is assigned, never recording whether the patient recovered or died, preventing algorithmic improvement and safety auditing.
- **Decision:** Established the **Closed-Loop Outcome Architecture**, decoupling:
  $$\mathbf{Planned\ Advice} \neq \mathbf{Actual\ Clinician\ Decision} \neq \mathbf{Actual\ Care\ Action} \neq \mathbf{Real-World\ Outcome}$$
  The system tracks clinician adherence (`ACCEPTED`, `MODIFIED`, `OVERRIDDEN`, `REJECTED`, `NOT_COMPLETED`) and logs definitive clinical endpoints across 6 standardized outcome categories.
- **Safety Boundary:** Any `ADVERSE_EVENT` or unexpected deterioration triggers an automatic high-priority safety audit review.

---

### Decision 5.8: Single Codebase Doctrine Across All Six Environments
- **Context:** Building separate applications for rural PHCs, district hospitals, outreach camps, and industrial clinics creates unsustainable code fragmentation and architectural divergence.
- **Decision:** Approved the **Single Codebase Doctrine**. CLINOVA is ONE software platform running ONE master state machine across all six environments (`ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_PUBLIC_CAMP`, `ENV_COMPANY_CLINIC`, `ENV_INDUSTRIAL_HEALTH`, `ENV_CAMPUS_HEALTH`). Environmental differences are handled exclusively via declarative configuration profiles and facility resource matrices ($\text{FACILITYGRAPH}$).
- **Safety Boundary:** In environments lacking a capability (e.g., surgical OT at a rural PHC), the state machine does not delete the state; rather, $\text{FACILITYGRAPH}$ calculates $\Phi_{\text{local}} = 0.0$, directing the Orchestration Engine to recommend **Inter-Facility Referral** instead of on-site surgery.

---

### Decision 5.9: Auditable Break-Glass Emergency Privilege
- **Context:** In crowded waiting rooms or during registration, patients can suddenly collapse. If staff must navigate through multiple permission menus or request supervisor overrides, the patient will suffer irreversible harm.
- **Decision:** Any authenticated clinical user (`ROLE_NURSE`, `ROLE_HEALTH_WORKER`, `ROLE_CLINICIAN`) can trigger an emergency escalation from any screen via the **Break-Glass Emergency Protocol**.
- **Safety Boundary:** Invocation instantly freezes routine UI, transitions state to `STATE_EMERGENCY_ACTIVE`, and writes an immutable cryptographic record to the audit ledger capturing actor ID, physical station IP, timestamp, and clinical rationale.

---

### Decision 5.10: Hackathon MVP Demonstration Corridor (PHC Spoke $\to$ District Hospital Hub)
- **Context:** Attempting to demonstrate all six operating environments simultaneously in a 10-minute hackathon evaluation results in superficial depth and evaluator confusion.
- **Decision:** Approved the **Dual-Facility Public Healthcare Demonstration Corridor**:
  $$\mathbf{Peripheral\ Rural\ PHC\ (Spoke)} \quad \overset{\text{FACILITYGRAPH Transfer}}{\Longrightarrow} \quad \mathbf{District\ Government\ Hospital\ (Hub)}$$
  Demonstrates two complete scenarios:
  1. *Scenario 1 (Regular to Referral):* Odia vernacular voice intake $\to$ visual extraction review $\to$ sufficiency check divert $\to$ nurse point-of-care vitals $\to$ CAREGRAPH $\to$ doctor review & physical exam $\to$ facility deficit check $\to$ capability-matched referral $\to$ zero-reentry reception at district hospital $\to$ outcome closure.
  2. *Scenario 2 (Emergency Fast-Track):* Walk-in collapse $\to$ $<200\text{ms}$ anonymous P1 token $\to$ 30s ABCD vitals $\to$ deterministic red-flag firing $\to$ resuscitation bundle stabilization.
- **Safety Boundary:** The demonstration corridor exercises all core engines ($\text{CAREGRAPH}$, $\text{FACILITYGRAPH}$, $\text{ORCHESTRATION}$, $\text{SIGNALGRAPH}$) without mocking or cutting architectural corners.
