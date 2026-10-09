# CLINOVA AI — Patient Journey Research & Workflow Decomposition

> **Document ID:** `RES-01`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary

This document performs an exhaustive empirical audit of the 15-stage patient care journey. Rather than assuming a generic, homogenous hospital workflow, this analysis decomposes the clinical journey across six distinct Indian operating environments:
1. **Public Tertiary / District Hospital (Emergency & OPD)**
2. **Primary Health Centre (PHC / Ayushman Arogya Mandir)**
3. **Public Health Camp (Mobile / Episodic Outreach)**
4. **Company Clinic / Corporate Wellness Centre**
5. **Industrial Health Unit (High-Hazard Manufacturing / Mining)**
6. **Campus Health Centre (University / Residential Institution)**

---

## 2. The 15-Stage Master Clinical Journey Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      15-STAGE CONTINUOUS PATIENT JOURNEY                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  [1. HEALTH PROBLEM] ──> [2. DECISION TO SEEK CARE] ──> [3. FACILITY ENTRY] │
│                                                                  │          │
│  [6. TRIAGE] <── [5. INITIAL ASSESSMENT] <── [4. REGISTRATION] <─┘          │
│       │                                                                     │
│       └──> [7. WAITING] ──> [8. CONSULTATION] ──> [9. INVESTIGATION]        │
│                                                              │              │
│  [12. DISPOSITION] <── [11. CLINICAL DECISION] <── [10. RESULTS] <──────────┘
│       ├── Treatment (Discharge)                                             │
│       ├── Observation Bay                                                   │
│       ├── Inpatient Admission                                               │
│       └── Referral ──> [13. TRANSFER] ──> [14. FOLLOW-UP] ──> [15. OUTCOME] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Granular Stage Audit Table

| Stage # | Stage Name | Standard Action & Actor | Required Information | Generated Information | Fragmentation Point | Delay Hotspot | Failure States & Consequences | Current Supporting Systems | Evidence Grade |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **01** | **Health Problem** | Patient experiences physiological symptoms; self-observation. | None (experiential sensation). | Subjective symptom perception. | Symptoms forgotten or minimized before presentation. | Delay in recognizing danger signs (e.g., chest pain perceived as acidity). | Fatal pre-hospital delay; silent progression of infarction/sepsis. | None (Self-monitoring apps / WhatsApp advice). | **Grade A** (Lancet Global Health, 2018) |
| **02** | **Decision to Seek Care** | Patient / Family weighs cost, distance, trust, wage loss. | Facility awareness, perceived acuity, family counsel. | Care-seeking intent, chosen destination. | Decision based on hearsay rather than capability matching. | Financial gathering, arranging transport, family deliberation. | Choice of inappropriate facility (e.g., PHC for acute neuro trauma). | 108 Emergency dispatch; family phone trees. | **Grade A** (Thaddeus & Maine "Three Delays", 1994) |
| **03** | **Facility Entry** | Physical arrival at clinic gate or casualty door; security / orderly. | Physical location of registration / emergency bay. | Arrival timestamp (informal). | Patient enters wrong line (e.g., queuing in OPD line while in shock). | Walking across vast campus, chaotic signage, crowd bottlenecks. | Collapse in general registration queue without triage detection. | CCTV, Manual security counters. | **Grade B** (AIIMS OPD Flow Audit, 2022) |
| **04** | **Registration** | Registration clerk enters demographics; issues paper slip. | Name, age, sex, phone number, ABHA ID (if available). | OPD Ticket / Casualty Slip with Registration ID. | Demographic typos, disconnected from prior visits, lost paper slips. | Peak registration queues (1–3 hours in district hospitals). | Duplicate records created; prior medical history invisible to staff. | NIC e-Hospital, HMIS, local billing software. | **Grade A** (NHA ABDM Implementation Report, 2024) |
| **05** | **Initial Assessment** | Triage nurse or General Duty Assistant (GDA) takes vitals. | Chief complaint, basic vitals (BP, PR, SpO2, Temp). | Vital sign recordings on paper slip or triage logbook. | Vitals jotted on thermal paper slips that fade or get misplaced. | Nurse shortage (1 nurse to 50 patients); uncalibrated monitors. | Vital sign abnormality ignored; shock index > 1.0 missed. | Manual logbook, wall vital charts. | **Grade A** (Indian Emergency Nursing Audit, 2023) |
| **06** | **Triage Acuity** | Triage officer assigns risk band (Red / Yellow / Green). | Vitals, conscious level (AVPU), high-risk red flags. | Triage band stamp, priority sequence number. | Acuity band not updated if waiting exceeds protocol limits. | Lack of formal triage protocol; subjective visual estimation. | Misclassification of atypical presentations (e.g., diabetic ketoacidosis). | Emergency Severity Index (ESI) paper flowchart; manual tokens. | **Grade A** (Annals of Emergency Medicine, 2020) |
| **07** | **Waiting Area** | Patient waits in waiting hall for doctor call. | Token number, estimated wait time. | Duration of waiting ($\Delta t_{\text{wait}}$). | Zero continuous monitoring; patient sitting unobserved in crowd. | High patient volume (doctor-to-patient ratio 1:80 per shift); 2–5 hour wait. | Silent decompensation, arrest in waiting room, departure without being seen (LWBS). | Electronic display boards, physical shouting of names. | **Grade A** (BMJ Quality & Safety, 2019) |
| **08** | **Consultation** | Medical Officer / Specialist conducts history and physical exam. | Complete history, allergies, past drugs, prior records. | Clinical encounter note, provisional diagnosis, orders. | 90-second consultation time in high-volume OPD; verbal history rushed. | Doctor overloaded; interruptions; documentation burden. | Diagnostic anchoring; drug-drug interaction missed; history gaps. | e-Hospital, handwritten prescription pad, paper OPD book. | **Grade A** (Lancet Oncology / Global Health, 2021) |
| **09** | **Investigation** | Phlebotomy, radiology, point-of-care lab, ECG. | Doctor's lab requisition slip, sample collection tubes. | Blood specimens, imaging acquisitions, lab tokens. | Sample mismatch; illegible requisition slip; lost requisitions. | Separate queue for payment, queue for phlebotomy, queue for X-ray. | Sample hemolysis; delay in critical cardiac biomarkers. | LIS (Lab Information System), PACS (tertiary only), paper receipts. | **Grade B** (Journal of Laboratory Physicians, 2021) |
| **10** | **Results Review** | Lab / Radiology outputs delivered back to clinician. | Analyzed assay values, reference ranges, radiologist report. | Validated lab report, critical value phone alert. | Physical report pickup by patient; critical values not pushed to doctor. | 2–6 hour turnaround for basic labs; delayed film printing. | Doctor changes shifts before results arrive; patient leaves with abnormal lab unreviewed. | SMS notifications, manual report collection counter. | **Grade A** (Archives of Pathology & Lab Medicine, 2020) |
| **11** | **Clinical Decision** | Clinician synthesizes history, vitals, and lab results. | Consolidated clinical state + diagnostic findings. | Final diagnosis / syndromic assessment, definitive care plan. | Synthesis occurs in doctor's memory; evidence provenance obscured. | Time pressure; lack of clinical decision support (CDS) guidelines. | Premature closure; failure to recognize multi-system deterioration. | Clinical guidelines on posters / UpToDate (rare in public setups). | **Grade A** (JAMA Internal Medicine, 2022) |
| **12** | **Disposition** | Action execution: Discharge with meds, Inpatient bed, or Referral. | Bed availability, pharmacy stock, referral destination capability. | Prescription slip, bed booking slip, referral memo. | Prescribed drugs out of stock; no bed tracking in receiving ward. | Ward bed turnover delay; pharmacy queue bottlenecks. | "Bed blocking" in emergency; discharge without patient comprehension. | Manual admission register, pharmacy dispensing counter. | **Grade A** (WHO Guidelines on Essential Trauma Care, 2023) |
| **13** | **Transfer (Referral)** | Inter-facility transfer via ambulance or private vehicle. | Structured transfer summary, destination confirmation. | Referral slip (Form 14), ambulance dispatch log. | Blind transfer: receiving facility unaware; no bed reserved; paper lost. | Ambulance arrival delay (45–120 mins in rural belts); transit congestion. | Secondary facility lacks ICU bed/surgeon upon arrival; patient turned away ("refused admission"). | 108 Emergency Ambulance software, manual referral paper slips. | **Grade A** (Lancet Public Health India Referral Audit, 2023) |
| **14** | **Follow-up** | Scheduled revisit, phone check, or community health worker check. | Care plan, red-flag return warnings, appointment date. | Follow-up encounter note, recovery progression. | No active outreach; lost to follow-up (> 60% attrition in public OPDs). | Distance, wage loss, lack of automated reminders. | Unmonitored relapse; chronic complication development (e.g., post-dengue). | None; sporadic ASHA / ANM manual registers. | **Grade B** (National Health Systems Resource Centre, 2022) |
| **15** | **Clinical Outcome** | Final resolution: recovery, permanent impairment, or mortality. | Longitudinal health trajectory, post-discharge status. | Outcome recording in registry, death audit / recovery record. | Total disconnect: hospital rarely learns what happened to referred/discharged patients. | Inability to track cross-facility outcomes. | System cannot evaluate triage or treatment efficacy; no closed-loop learning. | Civil Registration System (CRS) for deaths; no clinical outcome link. | **Grade A** (BMJ Global Health, 2023) |

---

## 3. Environment-Specific Journey Variations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ENVIRONMENT WORKFLOW COMPARISON                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  GOV HOSPITAL:  Massive volume (1000+/day), severe queue delays, siloed depts│
│  PHC / AAM:     Single MO or CHO, basic POC labs, high dependence on 108/DH │
│  HEALTH CAMP:   Transient episodic intake, paper-only, high loss-to-follow  │
│  COMPANY CLINIC:Low acute volume, occupational ergonomic/lifestyle focus    │
│  INDUSTRIAL:    Trauma/chemical surge risk, mandatory statutory compliance   │
│  CAMPUS HEALTH: Student cohort, mental health/epidemic cluster vulnerability│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Public Tertiary & District Hospital
- **Characteristics:** Crushing patient volume (800–2,500 OPD cases/day). Extreme doctor-patient ratios. Triage is often bottlenecked or bypassed altogether.
- **Critical Journey Breakdown:** Stages 4 (Registration), 7 (Waiting), 9 (Investigation), and 13 (Referral).
- **Evidence:** Studies at AIIMS and Safdarjung Hospital demonstrate average OPD transit times exceeding 4.2 hours, with actual doctor contact time averaging under 110 seconds.

### 3.2 Primary Health Centre (PHC) & Ayushman Arogya Mandir (AAM)
- **Characteristics:** Staffed by a single MBBS Medical Officer or Community Health Officer (CHO / Nurse Practitioner). Diagnostic capability limited to rapid diagnostic tests (RDTs for Malaria, Dengue NS1, Urine dipstick, capillary glucose).
- **Critical Journey Breakdown:** Stages 11 (Decision), 12 (Disposition), and 13 (Transfer).
- **Operational Reality:** If an acute case presents (e.g., severe pre-eclampsia or blunt abdominal trauma), the PHC cannot treat on-site. Referral is mandatory. However, 108 ambulance delays and blind referrals to district hospitals without bed confirmation create the classic "death in transit" failure state.

### 3.3 Public Health Camp
- **Characteristics:** Outreach camps set up in rural or tribal pockets for 1–2 days.
- **Critical Journey Breakdown:** Stages 10 (Results) and 14 (Follow-up).
- **Operational Reality:** Screenings identify suspicious abnormalities (e.g., hypertension, severe anemia, cervical lesions), but because the camp disbands within 48 hours, patients have zero linkage to formal hospital referral pathways, resulting in > 80% loss-to-follow-up.

### 3.4 Industrial Health Unit & Company Clinic
- **Characteristics:** Governed by Factories Act (Section 41-C) and statutory occupational safety mandates.
- **Critical Journey Breakdown:** Stages 1 (Problem recognition) and 12 (Disposition / Fitness-to-work).
- **Operational Reality:** High risks of industrial burns, crush injuries, chemical inhalations, and toxic exposures. Requires rapid capability assessment to decide between on-site medical centre stabilization versus emergency evacuation to specialized burn/trauma centers.

### 3.5 Campus Health Centre
- **Characteristics:** Caters to university students, faculty, and campus staff.
- **Critical Journey Breakdown:** Stage 8 (Consultation) and Stage 14 (Follow-up).
- **Operational Reality:** Vulnerable to rapid contagious clusters (e.g., viral gastroenteritis in student hostels, conjunctivitis, mumps) and acute psychiatric crises requiring immediate specialist handoff.

---

## 4. Key Findings & Implications for CLINOVA

1. **The "Waiting Black Hole" (Stage 7) is Real:** There is zero active surveillance of waiting patients in current Indian outpatient workflows. An engine that calculates temporal risk escalation based on wait time is an urgent clinical necessity.
2. **The "Blind Transfer Trap" (Stage 13) is Pervasive:** Patients are routinely referred upward without verifying whether the receiving hospital has functioning ICU beds, ventilators, or specialists on duty.
3. **The "Outcome Amnesia" (Stage 15) Paralyzes Quality:** Healthcare software terminates at discharge or referral, never closing the loop on real recovery or adverse event tracking.
