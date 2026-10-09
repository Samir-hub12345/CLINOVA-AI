# CLINOVA AI — Environment Journey Comparison & Invariant Matrix Specification

> **Document ID:** `RES-74`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Invariant: The Single Codebase Doctrine

A common architectural failure in health tech is attempting to build separate, siloed software applications for different deployment settings—one app for rural clinics, another for large hospitals, a third for health camps, and a fourth for factory rooms. This results in code fragmentation, fractured data models, and unmaintainable technical debt.

CLINOVA AI operates under the **Single Codebase Doctrine**:
> **Core Principle:** CLINOVA AI is **ONE single software platform** executing **ONE master state machine** across all operational environments.  
> The 27 canonical states, the Master Case schema, the provenance ledger, and clinical safety gates remain **100% INVARIANT**. Environmental differences are accommodated exclusively through declarative configuration profiles, local hardware capabilities, and facility resource matrices ($\text{FACILITYGRAPH}$).

$$\text{Runtime Behavior} = \text{CLINOVA Core State Machine} + \text{Environment Config Profile} + \text{Facility Resource Graph}$$

---

## 2. Invariant Core vs Environmental Adaptations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INVARIANT CORE VS CONFIGURATION                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ THE NON-NEGOTIABLE CLINOVA CORE ] ────────────────────────────────────┐  │
│  • Single Master Case Invariant (No duplicate cases)                     │  │
│  • Dual-Track Entry Decoupling (Regular vs Emergency)                    │  │
│  • Deterministic Red-Flag Rules (SpO2 < 85%, Shock Index > 1.0)          │  │
│  • Evidence Provenance Ledger (Source tags, verified tracking)           │  │
│  • Epistemic Uncertainty Calculus (Ut score)                             │  │
│  • Meaningful Human Control (Doctor monopoly over prescriptions/admissions)│
│  • Tamper-Evident SHA-256 Audit Trail                                    │  │
│                                                                          │  │
│                                     │                                    │  │
│                                     ▼                                    │  │
│  [ DECLARATIVE ENVIRONMENT PROFILES ] <──────────────────────────────────┘  │
│  ├── ENV_GOV_HOSPITAL  : High throughput, Casualty Bay HUD, Bed telemetry   │
│  ├── ENV_PHC           : 100% Offline LAN, ASHA vernacular audio, Referrals  │
│  ├── ENV_PUBLIC_CAMP   : Ultra-rapid screening, Wi-Fi mesh, Digital vouchers│
│  ├── ENV_COMPANY_CLINIC: DPDP role partition, HR fitness slip, Tele-consult │
│  ├── ENV_INDUSTRIAL    : Trauma/Burn HUD, Factories Act MLC log, Toxic PPE  │
│  └── ENV_CAMPUS_HEALTH : Student confidentiality shield, Outbreak cluster    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Cross-Environment Journey Comparison Matrix

The table below traces how each journey stage adapts across the six target environments while preserving the core state machine:

| Journey Stage | State ID | Government Hospital (`ENV_GOV_HOSPITAL`) | Primary Health Centre (`ENV_PHC`) | Public Health Camp (`ENV_PUBLIC_CAMP`) | Company Clinic (`ENV_COMPANY_CLINIC`) | Industrial Health (`ENV_INDUSTRIAL_HEALTH`) | Campus Health (`ENV_CAMPUS_HEALTH`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Encounter Entry** | `S01` | High-volume registration desk; barcode token slip printed. | Frontline ASHA or ANM desk; vernacular verbal intake. | Fast queue token; pop-up tent intake; batch check-in. | Employee badge tap / corporate SSO; DPDP consent modal. | Shop-floor biometric badge; hazard classification tag. | Student ID number / mobile app check-in; privacy shield. |
| **Multimodal Ingestion** | `S02` | Paper OPD slips OCR; printed lab reports uploaded. | Vernacular voice audio (Odia/Hindi) via worker tablet. | Quick touch-screen questionnaire; portable point-of-care test. | Desktop keyboard narrative; digital insurance upload. | Voice-first trauma narration; toxic exposure chemical tag. | Mobile app text entry; self-reported symptoms. |
| **Extraction & Review** | `S03` / `S04` | Asynchronous local server processing; nurse review. | Frontline ANM verifies extracted symptoms on tablet. | Batch automated verification; flags extreme values. | Employee self-reviews extracted details on portal. | Plant nurse reviews chemical & burn classification. | Student self-reviews extracted history on phone. |
| **Sufficiency & Vitals** | `S07` / `S08` | Dedicated Triage Nursing Desk; electronic vital monitors. | ANM/CHO measures BP, SpO2 with portable manual kit. | High-speed screening line (BP cuff, fingerstick glucometer). | Corporate nurse measures BP, BMI, ergonomic metrics. | Plant nurse measures trauma vitals, burn surface area (BSA). | University nurse measures vitals, rapid antigen tests. |
| **CAREGRAPH Synthesis** | `S10` | Full multi-parameter risk stratification; NEWS2. | Uncertainty-weighted triage; flags local diagnostic gaps. | 3-tier rapid acuity color-band (Green, Yellow, Red). | Ergonomic strain scoring; mental wellness screening. | Trauma / Burn Severity Index; chemical toxidrome vector. | Infectious syndromic cluster tracking (Hostel fever). |
| **Doctor Queue** | `S11` | Dynamic Acuity Queue; 400+ patients/day; wait prioritization. | Single Medical Officer queue; 40–80 patients/day. | Fast-track doctor station in main screening tent. | Scheduled appointment slots; zero waiting room pressure. | Immediate walk-in triage; zero non-emergent wait. | Walk-in student clinic queue; low wait duration. |
| **Doctor Review** | `S12` / `S13` | High-density 7-panel Doctor Workbench; 90-second workflow. | Streamlined Doctor Workbench; highlights local drug stock. | Rapid verification HUD; 60-second sign-off. | Occupational health view; workstation ergonomic review. | Trauma / Occupational Injury Workbench; MLC register. | Confidential health view; academic stress notes. |
| **FACILITYGRAPH Check** | `S14` | Internal bed occupancy; ICU bed count; on-call surgery. | Evaluates PHC medicine stock vs District Hospital capability.| Checks nearest CHC/DH referral beds for camp transfers. | Checks empaneled private network hospital network. | Checks on-site burn dressing vs regional Burn ICU. | Checks university infirmary beds vs city hospital. |
| **Pathway A: Routine Care**| `S16` | Prescription sent to hospital dispensary; 3-month follow-up.| Free essential drug dispensing (Niramaya); ASHA follow-up.| Lifestyle counseling slip; NCD card issued. | E-prescription; digital corporate fitness certificate. | First-aid dressing; return-to-work fitness certificate. | Prescription sent to campus pharmacy; rest certificate. |
| **Pathway B: Further Review**| `S17` | Return to hospital OPD with pending CT/Biopsy report. | Return to PHC on weekly visit of visiting specialist. | Referral to regular Tuesday PHC NCD clinic. | Return visit after ergonomic workstation evaluation. | Follow-up wound inspection in 48 hours. | Return visit in 48h to evaluate persistent fever/rash. |
| **Pathway C: Ward Admission**| `S18` / `S19` | Inpatient bed allocated in Male/Female Medical Ward. | Short-stay observation bed (PHC 6-bed ward; $< 24\text{h}$). | Not applicable (Camp lacks overnight inpatient beds). | Corporate medical room rest bay ($< 4\text{h}$ rest). | Industrial infirmary observation cot ($< 8\text{h}$). | University infirmary sick bay admission ($< 48\text{h}$). |
| **Pathway D: Referral** | `S20` / `S21` | Tertiary transfer to Government Medical College (MCH). | Critical transfer to District Headquarters Hospital (DHH). | Structured referral voucher linking camp to PHC/CHC. | Emergency transfer to empaneled private hospital. | STAT transfer to Burn Centre / Regional Trauma Hospital.| Transfer to tertiary hospital; parent notification. |
| **Pathway E: Emergency**| `S22` | Direct casualty resuscitation bay; STAT ECG & trauma team. | Emergency stabilization (IV fluids, O2) while summoning 108. | Emergency tent evacuation; immediate 108 dispatch. | Plant ambulance dispatch; emergency defibrillator (AED). | Shop-floor crash team; chemical decontamination shower. | Campus ambulance dispatch; university physician on-site. |
| **Pathway F: OT Fast-Track**| `S23` / `S24` | Hospital Emergency OT; surgeon/anesthetist on duty. | Not applicable (PHC lacks surgical OT; triggers transfer). | Not applicable (Camp lacks surgical OT). | Not applicable (Transfers to tertiary surgical center). | Minor OT for wound debridement; major OT transferred. | Minor dressing room; surgical cases transferred. |
| **Outcome Closure** | `S26` / `S27` | Discharge summary sealed; hospital statistics updated. | Outcome recorded; ASHA field visit confirmed. | Camp referral outcome tracked via public health network. | Employee fitness closed; HR receives non-clinical certificate.| Statutory Factories Act Form 21 injury register sealed. | Student illness resolved; academic leave cleared. |

---

## 4. Key Takeaways & Design Defensibility

1. **Zero State Machine Alteration:**  
   Every environment executes the exact same 27 states. In environments where a capability does not exist (e.g., surgical OT at a rural PHC or public health camp), the state machine does not delete `STATE_OT_PENDING`; rather, $\text{FACILITYGRAPH}$ calculates $\Phi_{\text{local}} = 0.0$, causing the Orchestration Engine to recommend **Inter-Facility Referral (`STATE_REFERRAL_PENDING`)** instead of local surgery.
2. **Configuration-Driven Privacy:**  
   In corporate and campus settings, legal privacy shields (DPDP Act) are enforced via RBAC configuration, ensuring employers and university administrators receive strictly non-clinical administrative certificates without modifying clinical database structures.
3. **Resilience Portability:**  
   The offline local LAN and peer-to-peer failover mechanisms developed for rural PHCs guarantee uninterrupted uptime during power and network collapses in urban hospitals and remote health camps.
