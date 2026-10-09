# CLINOVA AI — Environment to Product Technical Traceability

> **Document ID:** `RES-54`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Traceability Methodology

To ensure that real-world operational problems encountered in target healthcare environments directly inform interface design, backend architecture, deterministic guardrails, and testing suites, Phase 4 establishes an **End-to-End Bidirectional Traceability Pipeline**:

$$\text{Environment} \to \text{User} \to \text{Operational Problem} \to \text{Required Capability} \to \text{Data Model} \to \text{UI Impact} \to \text{Backend Impact} \to \text{AI/Rule Support} \to \text{Human Decision} \to \text{Safety Req.} \to \text{Test Req.} \to \text{Target Phase}$$

This matrix bridges abstract field observations directly into concrete software engineering specifications for subsequent phases without prematurely implementing production code.

---

## 2. Comprehensive Traceability Matrix Across All Six Environments

### Trace 1: Government Hospital — Emergency Queue Deterioration
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`
- **USER:** Casualty Triage Nurse (`ROLE_NURSE`) & Casualty Medical Officer (`ROLE_CLINICIAN`)
- **OPERATIONAL PROBLEM:** Massive OPD/Casualty queues (500+ patients); unmonitored patients in waiting rooms deteriorate into shock or cardiac arrest behind routine low-acuity cases.
- **REQUIRED CAPABILITY:** Dynamic Acuity-Weighted Queue Prioritization Engine based on vital sign trajectory ($\Delta R_t / \Delta t$) and red-flag extraction.
- **DATA:** Serial Vitals Array (`pulse`, `sbp`, `spo2`, `rr`, `timestamp`), Extracted Symptom Tokens, Computed ESI Level (1–5).
- **UI IMPACT:** Live re-sorting queue table with animated badge transitions; flashing amber/red highlight cards for deteriorating patients; audio chime for critical upward acuity shifts.
- **BACKEND IMPACT:** Fast in-memory priority queue microservice; sub-50ms queue recalculation on vital submission; WebSocket event broadcast to all casualty terminals.
- **AI / DETERMINISTIC SUPPORT:** Deterministic heuristic rules for ESI Level 1/2 red flags; linear regression slope calculation for vital deterioration trajectory.
- **HUMAN DECISION:** Casualty Medical Officer reviews prioritized card, verifies vitals, and summons patient immediately into resuscitation bay.
- **SAFETY REQUIREMENT:** Absolute rule: Patients with $\text{SpO}_2 < 88\%$ or Shock Index $> 1.0$ can never be sorted below stable patients, regardless of waiting time.
- **TEST REQUIREMENT:** Unit test: Verify priority queue correctly elevates deteriorating case above 100 stable baseline cases within $< 100$ms.
- **IMPLEMENTATION PHASE:** Phase 5 (Core Architecture) & Phase 6 (Intelligent Queue).

---

### Trace 2: Government Hospital — Extreme Doctor Time Poverty
- **ENVIRONMENT:** `ENV_GOV_HOSPITAL`
- **USER:** Outpatient Medical Officer (`ROLE_CLINICIAN`)
- **OPERATIONAL PROBLEM:** The "90-Second Doctor" dilemma: clinicians see 100+ patients in a 3-hour shift; cannot read multiple pages of crumpled paper records or type into heavy EMRs.
- **REQUIRED CAPABILITY:** Sub-60-Second Case Synthesis: Multimodal OCR and vernacular speech extraction condensing fragmented history into an executive 3-line clinical summary.
- **DATA:** Raw document image crops, transcribed vernacular text snippets, structured entity mappings (ICD/SNOMED), calculated epistemic uncertainty ($U_t$).
- **UI IMPACT:** Doctor Reviewer Workbench featuring high-density 3-pane layout: Master Case Summary, Evidence Provenance Inspector ($< 300$ms crop preview), 1-click verified disposition buttons.
- **BACKEND IMPACT:** Fast lightweight document processing pipeline (PaddleOCR / Tesseract); local faster-whisper speech-to-text; sub-500ms summary assembly endpoint.
- **AI / DETERMINISTIC SUPPORT:** Named Entity Recognition (NER) for medication and symptom extraction; deterministic validation against Indian pharmacopeia.
- **HUMAN DECISION:** Doctor inspects raw OCR crop with 1 click, modifies or approves medication list, and authorizes prescription with single keystroke.
- **SAFETY REQUIREMENT:** Every AI-extracted clinical token must retain clickable visual provenance linking to raw document image; zero ungrounded tokens allowed.
- **TEST REQUIREMENT:** Synthetic OCR test: verify zero hallucination of ungrounded drug names from 50 blurred prescription images.
- **IMPLEMENTATION PHASE:** Phase 5 (Extraction Pipeline) & Phase 7 (Doctor Workbench).

---

### Trace 3: Primary Health Centre — Offline ANM Assisted Intake
- **ENVIRONMENT:** `ENV_PHC`
- **USER:** Auxiliary Nurse Midwife (`ROLE_HEALTH_WORKER`) & Rural Patient (`ROLE_PATIENT`)
- **OPERATIONAL PROBLEM:** Rural patients speak regional dialects (Odia, Bengali, Hindi); ANMs have high reporting burden; internet drops for days; doctor is frequently away.
- **REQUIRED CAPABILITY:** Vernacular Voice-First Assisted Intake operating 100% locally on low-cost Android tablets over battery-backed local LAN.
- **DATA:** Vernacular audio blob, localized language code (`or-IN`, `hi-IN`), mapped symptom dictionary, local offline Master Case record.
- **UI IMPACT:** Large tap-friendly card UI; giant voice recording button; high-contrast icons; regional language prompts and thermal print output.
- **BACKEND IMPACT:** Fully offline FastAPI backend running on local Mini-PC server; local SQLite WAL mode database; deferred background synchronization queue.
- **AI / DETERMINISTIC SUPPORT:** Local faster-whisper quantized model (int8) running on local server CPU; colloquial symptom dictionary normalizer.
- **HUMAN DECISION:** ANM listens to patient, reviews transcribed symptom cards, measures objective blood pressure/glucose, and submits verified record.
- **SAFETY REQUIREMENT:** System must prompt for essential red-flag vital signs before allowing case submission; cannot complete intake on subjective complaint alone.
- **TEST REQUIREMENT:** Offline test: Disconnect WAN completely for 4 hours; verify 20 complete voice intakes persist locally and sync cleanly when WAN restored.
- **IMPLEMENTATION PHASE:** Phase 5 (Local Server Runtime) & Phase 6 (Frontline Intake Portal).

---

### Trace 4: Primary Health Centre — The Blind Referral Tragedy
- **ENVIRONMENT:** `ENV_PHC`
- **USER:** Medical Officer (`ROLE_CLINICIAN`) & 108 Ambulance Liaison (`ROLE_REFERRAL_STAFF`)
- **OPERATIONAL PROBLEM:** Solo doctor refers critical obstetric/snakebite cases blindly to District Hospital without knowing if ICU beds or blood exist; patient dies in transit or turned away at gate.
- **REQUIRED CAPABILITY:** FACILITYGRAPH Care Feasibility & Intelligent Referral Matching with Verified Capability Status.
- **DATA:** Patient Required Capabilities (`CAP_BLOOD_TRANSFUSION`, `CAP_ICU_VENTILATOR`), Destination Hospital Telemetry (`status`, `beds_available`, `freshness_timestamp`, `distance_km`).
- **UI IMPACT:** Referral Navigation Drawer showing ranked destination cards; color-coded capability verification badges (`VERIFIED`, `STALE`, `CONFLICTING`); 1-click printable thermal pass.
- **BACKEND IMPACT:** Multi-criteria routing algorithm balancing travel transit time ($t_{\text{transit}}$) against destination capability confidence; automated SMS/ABHA referral dispatch.
- **AI / DETERMINISTIC SUPPORT:** Deterministic clinical capability matcher; travel duration estimator using OpenStreetMap (OSRM) road network.
- **HUMAN DECISION:** Medical Officer selects highest-confidence destination facility and authorizes ambulance dispatch with digital transfer manifest.
- **SAFETY REQUIREMENT:** System must explicitly flag if receiving hospital capability data is `STALE` ($> 12$ hours old) and mandate telephonic confirmation before dispatch.
- **TEST REQUIREMENT:** Destination routing test: Given a saturated nearest hospital and an open facility 15 km further, verify engine ranks the capable facility first.
- **IMPLEMENTATION PHASE:** Phase 5 (FACILITYGRAPH Engine) & Phase 8 (Referral Drawer).

---

### Trace 5: Public Health Camp — Extreme Velocity Batch Triage
- **ENVIRONMENT:** `ENV_PUBLIC_CAMP`
- **USER:** Camp Volunteer Nurse (`ROLE_NURSE`) & Volunteer Doctor (`ROLE_CLINICIAN`)
- **OPERATIONAL PROBLEM:** 600 attendees queuing in open-air tents; doctors have $< 60$ seconds per patient; risk of missing severe asymptomatic hypertension or silent ischemia.
- **REQUIRED CAPABILITY:** Rapid 3-Tier Color-Coded Triage (Green / Yellow / Red) with instant point-of-care vital logging and batch thermal ticket generation.
- **DATA:** Rapid Token ID, Random Blood Glucose, Blood Pressure, Pulse, High-Risk Symptom Checkbox, Risk Tier (`GREEN`, `YELLOW`, `RED`).
- **UI IMPACT:** Single-screen rapid data-entry form optimized for 10-second touch completion; oversized Red Flag modal if vitals cross critical threshold; batch queue list.
- **BACKEND IMPACT:** In-memory local SQLite database; zero external network calls; sub-20ms transaction latency.
- **AI / DETERMINISTIC SUPPORT:** Deterministic clinical threshold rules (e.g., $\text{SBP} \ge 180\text{ mmHg} \to \text{RED}$; $\text{RBS} \ge 300\text{ mg/dL} \to \text{YELLOW}$).
- **HUMAN DECISION:** Volunteer doctor evaluates Red cohort first; dispenses essential generic starter pack or issues immediate public hospital referral slip.
- **SAFETY REQUIREMENT:** Red Flag cases cannot be closed without clinician sign-off or documented emergency transport handoff.
- **TEST REQUIREMENT:** High-throughput stress test: Process 500 simulated rapid token intakes within 30 minutes on a low-power laptop without memory leak or UI stutter.
- **IMPLEMENTATION PHASE:** Phase 6 (Batch Triage Workflow) & Phase 7 (Doctor Rapid Review).

---

### Trace 6: Company Clinic — Employee Privacy & DPDP Shield
- **ENVIRONMENT:** `ENV_COMPANY_CLINIC`
- **USER:** Corporate Employee (`ROLE_PATIENT`), Occupational Nurse (`ROLE_NURSE`), HR Manager (`ROLE_FACILITY_ADMIN`)
- **OPERATIONAL PROBLEM:** Employees boycott clinic due to intense fear that personal health disclosures (depression, pregnancy, chronic illness) will leak to corporate management.
- **REQUIRED CAPABILITY:** Strict Cryptographic Role Partitioning (DPDP Shield) isolating clinical data from administrative fitness certifications.
- **DATA:** Clinical Case Record (Symptoms, Vitals, ICD-10, Doctor Notes) vs. Administrative Record (`employee_id`, `fitness_status`, `leave_duration_days`, `ergonomic_restriction`).
- **UI IMPACT:** Doctor/Nurse view displays full clinical chart; HR/Manager view displays strictly non-clinical certificate with download button for signed administrative leave note.
- **BACKEND IMPACT:** Cryptographic field-level encryption; strict RBAC permission middleware rejecting HR role access to `/api/v1/cases/{id}/clinical` endpoints.
- **AI / DETERMINISTIC SUPPORT:** Automated generation of non-clinical administrative summary text from clinical disposition without exposing diagnostic labels.
- **HUMAN DECISION:** Visiting Doctor approves fitness certificate; Employee reviews and consents to sharing non-clinical certificate with HR.
- **SAFETY REQUIREMENT:** Zero leak of clinical diagnosis, symptoms, or consultation notes to employer administration under severe legal penalty of DPDP Act 2023.
- **TEST REQUIREMENT:** Security audit test: Attempt to access clinical endpoints using `ROLE_FACILITY_ADMIN` JWT token; verify absolute HTTP 403 Forbidden rejection.
- **IMPLEMENTATION PHASE:** Phase 5 (RBAC & DPDP Security Architecture).

---

### Trace 7: Industrial Health Unit — Golden-Hour Trauma & Toxic Burn Resuscitation
- **ENVIRONMENT:** `ENV_INDUSTRIAL_HEALTH`
- **USER:** Industrial Paramedic (`ROLE_NURSE`) & Industrial Medical Officer (`ROLE_CLINICIAN`)
- **OPERATIONAL PROBLEM:** High-voltage electrical burns, chemical acid splashes, or crushing trauma require instant calculation of shock index, burn fluid rates, and antidote dosing under extreme stress.
- **REQUIRED CAPABILITY:** Golden-Hour Industrial Trauma & Burn Resuscitation Engine: Instant automated Shock Index, Revised Trauma Score (RTS), and Parkland Burn resuscitation calculations.
- **DATA:** Worker Weight (kg), Burn % TBSA, Time of Burn, Chemical UN Code, Pulse, Systolic BP, Respiratory Rate, GCS.
- **UI IMPACT:** Trauma Resuscitation HUD; glove-friendly massive touch buttons (64x64 px); prominent fluid rate display (e.g., "Parkland: Infuse 650 mL Ringer's Lactate in 1st Hour"); chemical antidote guide.
- **BACKEND IMPACT:** Real-time trauma calculation microservice; automatic generation of pre-arrival trauma manifest; integration with plant emergency sirens/radio.
- **AI / DETERMINISTIC SUPPORT:** Exact Parkland Formula ($4\text{ mL} \times \text{kg} \times \%\text{TBSA}$); Revise Trauma Score algorithm; chemical hazard database lookup.
- **HUMAN DECISION:** Industrial Medical Officer verifies airway, orders fluid rate, administers specific chemical antidote (e.g., Calcium Gluconate gel), and initiates ALS ambulance transfer.
- **SAFETY REQUIREMENT:** Pediatric and adult dosing limits strictly enforced; antidote dosage calculation transparently displays source formula and parameters.
- **TEST REQUIREMENT:** Precision test: Verify Parkland calculator output matches exact clinical formula across 20 synthetic burn cases with variable body weights and TBSA %.
- **IMPLEMENTATION PHASE:** Phase 6 (Trauma Fast-Track) & Phase 8 (Specialized Facility Dispatch).

---

### Trace 8: Campus Health Centre — Dormitory Outbreak Detection & Mental Health Triage
- **ENVIRONMENT:** `ENV_CAMPUS_HEALTH`
- **USER:** Student (`ROLE_PATIENT`), Campus Medical Officer (`ROLE_CLINICIAN`), Dean of Student Welfare (`ROLE_FACILITY_ADMIN`)
- **OPERATIONAL PROBLEM:** High-density student hostels suffer explosive viral/dengue outbreaks; severe student exam stress and depression go unnoticed until fatal self-harm occurs.
- **REQUIRED CAPABILITY:** SIGNALGRAPH Hostel-Level Outbreak Early Warning + Empathetic Digital Mental Health Crisis Screening (PHQ-9 / C-SSRS).
- **DATA:** Student Hostel Hall/Room, De-identified Symptom Tokens, Validated Mental Health Assessment Responses, Acuity Score.
- **UI IMPACT:** Student Self-Intake portal featuring compassionate conversational UI; discrete emergency help banner; Doctor Workbench alerts with silent high-priority psychological crisis flag.
- **BACKEND IMPACT:** De-identified syndromic clustering engine ($k$-anonymity $\ge 5$); automated hostel outbreak anomaly detection; zero-leakage academic segregation.
- **AI / DETERMINISTIC SUPPORT:** Validated C-SSRS suicide risk classification rules; Poisson outbreak anomaly detector for hostel syndromic clusters.
- **HUMAN DECISION:** Campus Medical Officer initiates immediate on-site psychological crisis intervention and coordinates supportive counseling; Dean notified only of hostel sanitation alert.
- **SAFETY REQUIREMENT:** Any active suicidal ideation response triggers immediate silent clinician alert and direct human contact protocol; system never dismisses or closes self-harm cases autonomously.
- **TEST REQUIREMENT:** Synthetic outbreak simulation: Inject 10 synthetic dengue cases across Hostel Block B within 48 hours; verify SIGNALGRAPH emits localized anomaly alert.
- **IMPLEMENTATION PHASE:** Phase 6 (Student Intake & Mental Health Module) & Phase 9 (SIGNALGRAPH Outbreak Telemetry).
