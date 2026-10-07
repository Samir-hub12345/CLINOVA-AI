# CLINOVA AI — Complete Screen Inventory & Lifecycle Matrix

> **Document ID:** `DOC-25`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Overview & Screen Catalog

CLINOVA AI defines **40 distinct screens** organized across seven operational workflow clusters. Every screen connects directly to the underlying **Master Case** architecture and participates in the continuous care intelligence loop.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLINOVA 40-SCREEN WORKFLOW CLUSTERS                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  CLUSTER 1: PUBLIC & AUTHENTICATION (Screens 1–4)                           │
│  CLUSTER 2: INTAKE, EXTRACTION & TRIAGE GAP AUDIT (Screens 5–12)             │
│  CLUSTER 3: STAFF WORKSPACE & DATA CONSOLIDATION (Screens 13–15)            │
│  CLUSTER 4: CAREGRAPH & DOCTOR REVIEW WORKBENCH (Screens 16–23)             │
│  CLUSTER 5: FACILITYGRAPH, ORCHESTRATION & DISPOSITION PATHWAYS (24–31)     │
│  CLUSTER 6: EMERGENCY FAST-TRACK & OPERATION THEATRE (Screens 32–36)        │
│  CLUSTER 7: CONTINUITY, SIGNALGRAPH & SYSTEM GOVERNANCE (Screens 37–40)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete 40-Screen Master Registry

| # | Screen Name | Route / Path | Primary Actor | Clinical / Operational Purpose | Graph Linkage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Public Landing Page** | `/` | Public, Clinician | Platform identity, institutional positioning, system overview. | Platform Overview |
| **02** | **Product / Innovation Page** | `/innovation` | Clinician, Researcher | Deep-dive into CAREGRAPH, FACILITYGRAPH, SIGNALGRAPH, Orchestration. | All 4 Graphs |
| **03** | **User Login** | `/login` | All Authenticated | Secure credential entry, Supabase Auth session initialization. | Auth Layer |
| **04** | **Role Selection** | `/select-role` | All Authenticated | Select active clinical role (Doctor, Nurse, Admin, Referral, etc.). | RBAC Security |
| **05** | **Patient Entry: Mode Selector** | `/encounter/new` | Patient, Nurse | Select Regular/Standard Intake vs. Emergency Fast-Track. | Master Case Entry |
| **06** | **Patient Information Intake** | `/encounter/intake` | Patient, Nurse | Demographic capture, digital consent, structured chief complaint. | Master Case Core |
| **07** | **Voice Symptom Intake** | `/encounter/voice` | Patient, Nurse | Regional audio speech recording (Odia/Hindi/English) via Whisper. | Evidence Node (Voice) |
| **08** | **Medical Report Upload** | `/encounter/upload` | Patient, Nurse | Prescriptions, lab reports, ECG photos upload for local OCR. | Evidence Node (OCR) |
| **09** | **Extraction & Visual Review**| `/encounter/extraction` | Nurse, Reviewer | Inspect raw source vs. extracted clinical entities with confidence scores.| Provenance Layer |
| **10** | **Longitudinal Timeline** | `/encounter/timeline` | Nurse, Doctor | Chronological progression of symptoms, medications, and vitals. | CAREGRAPH Timeline |
| **11** | **Missing Information Audit** | `/encounter/audit` | Nurse, Doctor | Audit of `KNOWN`, `UNKNOWN`, `CONFLICTING`, and `UNRELIABLE` parameters.| Uncertainty Vector |
| **12** | **Dynamic Follow-up Questions**| `/encounter/follow-up` | Patient, Nurse | Interactive Next-Best Information questions to reduce uncertainty. | NBI Engine |
| **13** | **Staff Assignment Workspace** | `/staff/worklist` | Nurse, Health Worker | Queue of incomplete cases requiring bedside vital acquisition. | Master Case Queue |
| **14** | **Staff Vitals Checklist** | `/staff/checklist/:id` | Nurse, Health Worker | Direct entry of missing BP, SpO2, HR, RR, and red-flag checklists. | Master Case (Vitals) |
| **15** | **Consolidated Master Case View**| `/case/:id/consolidated`| Nurse, Doctor | Synthesized case file after intake and vitals completion. | Master Case Core |
| **16** | **CAREGRAPH Interactive View** | `/case/:id/caregraph` | Doctor, Reviewer | Dynamic patient-state visualization (syndrome, trajectory, uncertainty).| CAREGRAPH Engine |
| **17** | **Risk & Trajectory Monitor** | `/case/:id/trajectory` | Doctor, Reviewer | Explainable risk tuple (Risk, Reason, Evidence, Trajectory, Action). | Risk & Trajectory |
| **18** | **Uncertainty & Evidence View**| `/case/:id/evidence` | Doctor, Reviewer | Deep inspection of data gaps, contradiction callouts, and provenance. | Uncertainty Engine |
| **19** | **Structured Triage Note Editor**| `/case/:id/triage-note`| Doctor, Reviewer | Review and edit AI-drafted structured clinical note. | Master Case Notes |
| **20** | **Master Clinical Report** | `/case/:id/master-report`| Doctor, Reviewer | Definitive comprehensive clinical report (View, Download PDF, Print). | Report Type 1 |
| **21** | **Doctor Prioritized Queue** | `/doctor/queue` | Doctor, Reviewer | Dynamic clinical worklist sorted by composite risk, trajectory, wait time.| Priority Engine |
| **22** | **Doctor Case Overview** | `/doctor/case/:id` | Doctor, Reviewer | Unified one-screen clinical workstation displaying complete patient state.| Doctor Workbench |
| **23** | **Doctor Verify / Modify / Add**| `/doctor/case/:id/audit`| Doctor, Reviewer | Interactive parameter verification, clinical override, and exam entry.| Verification Ledger |
| **24** | **FACILITYGRAPH Inspector** | `/facilities/capability`| Doctor, Admin | Local facility resource inspection (ICU beds, oxygen, specialists). | FACILITYGRAPH |
| **25** | **Facility Comparison Matrix** | `/facilities/compare` | Doctor, Referral Staff| Feasibility matching across regional network with Leaflet map. | Care Feasibility |
| **26** | **ORCHESTRATION Engine View** | `/case/:id/orchestrate`| Doctor, Reviewer | Displays Safest Achievable Care Pathway recommendation. | ORCHESTRATION |
| **27** | **Routine Care & Calendar** | `/case/:id/routine` | Doctor, Patient | Outpatient discharge plan with recurring follow-up calendar. | Pathway A |
| **28** | **Further Review Scheduler** | `/case/:id/revisit` | Doctor, Patient | Single next appointment scheduler for pending investigations. | Pathway B |
| **29** | **Inpatient Ward Admission** | `/case/:id/admission` | Doctor, Nurse | Formal ward bed request, comorbidity dossier, and precautions list. | Pathway C |
| **30** | **Staff Admission Verification** | `/ward/verify/:id` | Ward Nursing Staff | Ward bed confirmation, allergy review, and admission acceptance. | Pathway C (Staff) |
| **31** | **Transfer & Handoff Screen** | `/case/:id/handoff` | Nurse, Ward Staff | Structured SBAR handoff checklist and dual digital sign-off. | Report Type 4 |
| **32** | **Emergency Fast-Track Intake** | `/emergency/fast-track` | Emergency Nurse/Doctor| Ultra-rapid (<30s) ABCD vitals entry and immediate bedside alert. | Emergency Flow |
| **33** | **Emergency Resuscitation Bay** | `/emergency/bay/:id` | Emergency Team | Resuscitation bundle execution (STEMI, Sepsis, Shock, Trauma). | Emergency Bundle |
| **34** | **Operation Theatre Checklist** | `/ot/checklist/:id` | Surgeon, Anesthetist | WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out). | OT Surgical Pack |
| **35** | **Emergency Report View** | `/emergency/report/:id` | Emergency Team | High-contrast 1-page emergency resuscitation summary. | Report Type 5 |
| **36** | **OT Surgical Report View** | `/ot/report/:id` | Surgeon, Scrub Nurse | Procedure findings, surgical pathology, and post-op recovery orders. | Report Type 6 |
| **37** | **Longitudinal Outcome Tracker**| `/case/:id/outcome` | Doctor, Quality Nurse | Real-world outcome recording (Recovery, Complication, Re-triage). | Outcome Loop |
| **38** | **SIGNALGRAPH Telemetry View** | `/signals/surveillance` | System Admin, Officer | Regional syndromic disease cluster map and epidemic surge alerts. | SIGNALGRAPH |
| **39** | **Facility Capacity Analytics**| `/analytics/capacity` | Facility Administrator| Departmental wait times, bed occupancy trends, and referral logjams. | Operational Telemetry|
| **40** | **System Audit & Compliance** | `/admin/audit-logs` | System Administrator | Tamper-evident ledger of clinical overrides, PII sanitization, logins.| Security Ledger |

---

## 3. Screen Lifecycle States

Every screen adheres to a standardized state lifecycle:
- **Normal State:** Complete, styled UI displaying verified or pending data.
- **Loading State:** Subtle skeleton loaders matching the exact dimensions of final cards; zero layout shifts.
- **Empty State:** Clear, non-punitive empty message explaining what action is required to populate data.
- **Error State:** Explainable error card with recovery action button (e.g., "Retry local OCR" or "Enter manually").
- **Permission Denied State:** Institutional security card stating why the active role lacks access and directing to authorized screen.
- **Mobile Responsive State:** Fully collapsible, touch-friendly layout with 48px touch targets for tablet/mobile operation.
