# CLINOVA AI — Target-Environment Gap Matrix & Operational Workflows

> **Document ID:** `RES-15`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary

This document performs an exhaustive cross-environment operational comparison across the six distinct healthcare environments targeted by CLINOVA AI:
1. **Government Hospital (Tertiary / District Hospital)**
2. **Primary Health Centre (PHC / Ayushman Arogya Mandir)**
3. **Public Health Camp (Outreach / Mobile Health Unit)**
4. **Company Clinic (Corporate Wellness & Occupational Outpatient)**
5. **Industrial Health Unit (High-Hazard Manufacturing, Mining, Petrochemical)**
6. **Campus Health Centre (University & Residential Academic Institution)**

For each environment, we trace the complete workflow chain:
$$\mathbf{ENTRY} \to \mathbf{USERS} \to \mathbf{DATA} \to \mathbf{WORKFLOW} \to \mathbf{CONSTRAINTS} \to \mathbf{FAILURES} \to \mathbf{ESCALATION} \to \mathbf{REFERRAL} \to \mathbf{FOLLOW\text{-}UP} \to \mathbf{OUTCOME}$$

We then isolate the common CLINOVA core architecture from environment-specific behaviors, UI configurations, and permission models.

---

## 2. Granular Target-Environment Workflow Comparison

| Dimension | 1. Government Hospital (Tertiary/DH) | 2. Primary Health Centre (PHC / AAM) | 3. Public Health Camp | 4. Company Clinic | 5. Industrial Health Unit | 6. Campus Health Centre |
|:---|:---|:---|:---|:---|:---|:---|
| **Entry Point** | Emergency Casualty gate, central OPD registration hall, ambulance drop-off. | Single outpatient entrance, main veranda, ASHA escort. | Makeshift tent desk, village schoolroom, community hall. | Corporate campus lobby, wellness kiosk, appointment portal. | Factory medical room, emergency ambulance gate, plant floor escort. | University student clinic, residential hostel nurse station. |
| **Primary Users** | Casualty MO, Triage Nurse, GDAs, Department Specialists, Residents. | Single Medical Officer (MBBS), Community Health Officer (CHO), ANM, Pharmacist. | Visiting Outreach Doctor, Medical Interns, ASHA workers, Camp Organizers. | Occupational Health Physician, Corporate Wellness Nurse, HR liaison. | Factory Medical Officer (AFIH certified), Industrial Nurse, Safety Marshals. | Campus Doctor, Staff Nurse, Student Counselor / Psychologist. |
| **Input Data Modalities** | Massive paper OPD tickets, crumpled past prescriptions, typed lab panels, portable X-rays, monitors. | Spoken Odia/Hindi narratives, handwritten slips, rapid test strips (malaria/sugar). | Vernacular speech, paper camp screening forms, fingerstick rapid blood tests. | Employee health IDs, digital check-ins, annual health check PDFs. | Toxic exposure logs, safety incident reports, burn/trauma assessments, spirometry. | Student health profiles, hostel contagion logs, psychiatric screening scales. |
| **Core Workflow** | High-throughput registration $\to$ rapid triage $\to$ crowded waiting hall $\to$ 90s doctor consult $\to$ central lab $\to$ disposition. | Morning OPD $\to$ vital check by ANM $\to$ single MO consultation $\to$ pharmacy dispensing $\to$ home or 108 referral. | Episodic screening queue $\to$ blood pressure/sugar check $\to$ brief doctor review $\to$ advice & medication packet. | Scheduled wellness consult $\to$ ergonomic/lifestyle review $\to$ prescription $\to$ return to work. | Urgent trauma triage $\to$ de-contamination / stabilization $\to$ fitness-to-work review $\to$ statutory filing. | Walk-in triage $\to$ infectious/mental health review $\to$ medication $\to$ hostel isolation or tertiary consult. |
| **System Constraints** | Extreme crowding (1000–3000/day), noise, staff exhaustion, intermittent intranet. | Single doctor, basic POC lab only, intermittent grid power, weak internet (2G/4G). | Completely offline, battery power, transient setup (24–48 hours max), zero permanent storage. | Low acute volume, high privacy demands, corporate IT firewalls. | High-consequence chemical/trauma risk, strict statutory reporting (Factories Act), noise. | High seasonal surge vulnerability, student privacy sensitivity, suicide/mental health risk. |
| **Dominant Failure States** | Patients decompensate unmonitored in waiting halls; violent clashes between relatives and staff over queue delays. | Blind referral to overcrowded district hospital; patient dies in ambulance transit due to lack of ICU beds. | Screened abnormalities are never followed up; 80% loss-to-follow-up after camp disbands. | Over-medicalization of minor stress; failure to catch acute cardiovascular red flags in executives. | Failure to recognize acute toxic exposure or internal trauma; improper emergency decontamination. | Rapid uncontained infectious outbreaks in dorms (dengue, mumps); missed acute depressive crises. |
| **Emergency Escalation** | Code Blue / Trauma alert to Emergency Resuscitation Room (ERR). | Immediate stabilization with oxygen/IV fluids + manual call to 108 ambulance dispatch. | Red flag case immediately placed in camp transport vehicle for transfer to nearest CHC/DH. | Corporate security alert; private emergency ambulance dispatch to partner hospital. | Factory siren / Plant emergency response team dispatch; industrial ambulance run. | Campus ambulance dispatch to district medical college; notification of dean / guardians. |
| **Referral Routing** | Internal inter-departmental transfer (OPD to Ward/OT); specialized quaternary transfers. | Referral to Sub-District Hospital (SDH), District Hospital (DH), or Medical College. | Referral slip handed to patient directing them to nearest CHC or Ayushman Arogya Mandir. | Referral to private tertiary partner network or empanelled insurance hospital. | Direct transfer to dedicated regional Burn Centre or Level-1 Trauma Centre. | Direct transfer to university hospital or affiliated tertiary teaching hospital. |
| **Follow-up Model** | Return OPD visit in 7–14 days (patients rarely return unless symptoms worsen). | ASHA home visits; village health sanitation and nutrition days (VHSND). | None (historically non-existent; major public health failure point). | Automated email / corporate health app check-in; occupational fitness revisit. | Mandatory statutory follow-up exam; return-to-work clearance certification. | Revisit at campus clinic; hostel warden health check; counseling check-in. |
| **Clinical Outcome** | Inpatient discharge summary; mortality register in hospital medical records department. | Resolution recorded only if patient revisits PHC; referred outcomes lost. | Completely lost; camp team disbands with zero outcome tracking. | Wellness score improvement; sick leave days tracked by corporate HR. | Statutory incident closure; disability assessment; OSHA / Factory Inspectorate log. | Resolution of acute illness; academic medical leave sign-off. |

---

## 3. The Common Core vs Environment-Specific Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLINOVA ADAPTIVE CORE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  COMMON CLINOVA CORE (Identical across all 6 environments):                 │
│  ├── Unified Master Case Model (`CaseModel`)                                │
│  ├── Multimodal Ingestion Pipeline (Voice, OCR, Vitals, Narrative)          │
│  ├── Evidence Provenance & Confidence Engine (`EvidenceNode`)               │
│  ├── CAREGRAPH Active Patient State Engine (Acuity $R_t$, Uncertainty $U_t$)│
│  ├── Deterministic Red-Flag Safety Bounds (`TRIAGE-R01` to `TRIAGE-R06`)    │
│  ├── Meaningful Human Control Reviewer Dashboard & Sign-Off Gate            │
│  └── Immutable Tamper-Evident Audit Ledger                                  │
│                                                                             │
│  ENVIRONMENT-SPECIFIC ADAPTATIONS:                                          │
│  ├── Government Hospital:  High-density Queue UI, Multi-doctor Workstations,│
│  │                         Departmental Ward/OT Flow (`DOC-16`)             │
│  ├── PHC / Camp:           100% Offline Mode, Audio Vernacular Prompts,     │
│  │                         Single-click 108 Capability-Matched Referral Pack│
│  ├── Company / Industrial: Statutory Workplace Incident Logs, Toxic Hazmat  │
│  │                         Checklists, Fitness-to-Work Certification        │
│  └── Campus Health:        Syndromic Hostel Surge Tracking, Mental Health   │
│                            Screening Privacy Bounds, Guardian Handoff       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Permission & Role Adjustments by Environment
- **In Public Hospitals & PHCs:** The primary decision actor is the **Licensed Medical Officer (MO)** or **Community Health Officer (CHO)**. Triage nurses and GDAs hold intake permissions, but cannot close a case without doctor review.
- **In Public Health Camps:** Fast-entry mode allows **Medical Interns and ANMs** to rapidly batch-screen vitals, with a single roving doctor executing bulk approvals on flagged cases.
- **In Industrial Health Units:** The **Factory Medical Officer** requires specialized access to occupational exposure registries and legal reporting modules under the Factories Act.
- **In Campus Clinics:** Strict psychological data segregation ensures student counseling records cannot be viewed by administrative faculty without explicit student consent.

---

## 4. Key Findings for CLINOVA Product Definition

1. **Offline-First is Non-Negotiable for PHCs & Camps:** Health camps and rural PHCs cannot depend on real-time internet connectivity. Ingestion, OCR, and deterministic rule evaluation must function 100% locally on a laptop or tablet using SQLite and local models.
2. **One Core Engine, Six Configurable Workspaces:** CLINOVA does not need six different codebases. A single core engine configured by an environment profile flag (`ENV_GOV_HOSPITAL`, `ENV_PHC`, `ENV_CAMP`, etc.) provides the exact required workflow adaptations.
