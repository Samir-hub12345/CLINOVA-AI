# CLINOVA AI — Referral & Care-Navigation Audit

> **Document ID:** `RES-05`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Audit Mandate

A critical finding of Phase 2 is that **referral management, automated provider matching, and closed-loop referral tracking are ALREADY established commercial capabilities**. Platforms like **ReferralMD**, **AristaMD**, **Kyruus Health**, **RubiconMD**, and the UK **NHS e-Referral Service (e-RS)** have processed tens of millions of referrals, automating intake fax parsing, insurance matching, calendar scheduling, and EHR write-backs.

Therefore, **CLINOVA AI must NEVER claim to have "invented" digital referral management or closed-loop tracking**. 

This audit maps existing commercial solutions in detail to identify the **precise remaining innovation gap**: the dynamic integration of real-time clinical physiological risk and acute bed/equipment feasibility under emergency transfer conditions.

---

## 2. Master Audit of Referral & Care-Navigation Systems

| Solution & Region | Primary Referral Input | Clinical Information Handling | Provider / Facility Matching Logic | Real-Time Facility Capability Aware? | Real-Time Capacity / Bed Aware? | Scheduling & Booking | Patient Notification | Closed-Loop Completion Tracking | Outcome Tracking Depth | Documented Limitations | Evidence Grade |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **ReferralMD** *(USA)* | Inbound electronic faxes, PDFs, Direct messaging, EHR orders. | AI fax OCR parses clinical notes and demographic fields into structured forms. | "SmartMATCH" algorithm: matches by insurance, specialty taxonomy, geographic distance, provider tier. | **Static directory.** Checks if clinic lists specialty service in profile. | **Wait-time only.** Based on historical schedule slots; **blind to emergency ICU bed occupancy**. | Automated online calendar booking and EHR write-back. | SMS and email appointment reminders with two-way confirmation. | **Yes.** Tracks referral lifecycle from intake to attended visit. | **Administrative.** Confirms appointment completion and consult note return; **no physiological outcome**. | Focused on US outpatient elective referrals; zero utility for acute emergency resuscitation routing. | **Grade B** (ReferralMD Platform Documentation & KLAS, 2024) |
| **AristaMD** *(USA)* | Primary care provider referral order or eConsult requisition. | Standardized clinical templates with specialty-specific guidelines. | Specialty matching algorithm routing to panel of licensed medical specialists. | **Specialist credential based.** Confirms board certification of provider. | **Queue availability.** Tracks specialist responsiveness to eConsult requests. | Facilitates electronic specialist consultation within 24–48 hours. | Direct provider-to-provider communication; optional patient SMS. | **Yes.** Confirms whether eConsult resolved case or necessitated face-to-face visit. | **Care diversion metrics.** Measures avoidance of unnecessary outpatient visits. | Designed for asynchronous elective specialist advice; not built for acute inter-facility hospital transfers. | **Grade B** (AristaMD Clinical Outcome Studies, 2023) |
| **Kyruus Health (Kyruus Connect)** *(USA)* | Health system call center, web portal, EHR scheduling queue. | Clinical keyword search mapped to proprietary clinical taxonomy. | Deep provider directory matching clinical focus, insurance, location, language, and gender. | **Clinical scope.** Matches specific procedures (e.g., pediatric cardiology vs adult). | **Template scheduling.** Reads open calendar slots in Epic/Cerner schedule. | Real-time direct scheduling into EHR provider templates. | Multichannel appointment confirmations (SMS, email, portal). | **Partial.** Tracks whether booked appointment was completed or cancelled. | **None.** Does not track longitudinal clinical recovery or complications. | Enterprise directory search engine; completely blind to emergency hospital resources (oxygen, blood, ICU). | **Grade B** (Kyruus Health Architecture Whitepapers, 2024) |
| **NHS e-Referral Service (e-RS)** *(UK)* | General Practitioner (GP) electronic referral order in primary care EMR. | Attached summary care record, GP letter, and recent pathology results. | Service directory matching clinical specialty, NHS Trust catchment area, and clinic clinic codes. | **Trust service specification.** Defined by commissioning contracts. | **Published wait times.** Displays 18-week RTT (Referral to Treatment) queue estimates. | Patient selects preferred hospital and appointment slot online or via telephone. | Postal booking letter, NHS App digital notifications. | **Yes.** Full national tracking of referral acceptance, rejection, and clinic attendance. | **Administrative.** Records final discharge back to GP or admission to waiting list. | Rigid national infrastructure; notoriously slow to adapt during acute hospital capacity crises; zero real-time bed telemetry. | **Grade A** (NHS England Digital e-RS Documentation, 2023) |
| **RubiconMD** *(USA)* | eConsult submission with attached clinical history, ECGs, photos. | Structured eConsult intake form; attachments reviewed by specialist. | Algorithmic routing across 140+ specialty panels based on question type. | **Subspecialty coverage.** Evaluates clinical complexity against specialist training. | **SLA turnaround.** Ensures specialist response within 4 hours. | Delivers formal specialist written opinion back to referring primary care doctor. | Primary care doctor communicates guidance back to patient. | **Yes.** Records primary care clinician acceptance of specialist guidance. | **Specialist concordance.** Tracks treatment plan alterations. | Limited strictly to asynchronous peer-to-peer consultation; no physical transport or bed transfer capabilities. | **Grade B** (RubiconMD Annual Clinical Impact Report, 2023) |
| **Ocean by CognisantMD** *(Canada)* | EMR eReferral form; secure cloud messaging between clinics. | Structured EMR data fields + standardized clinical requisitions. | Directory matching based on Ontario Health / regional health authority pathways. | **Regional service catalog.** Static capability listings. | **Central intake triage.** Central triage nurses assign wait-time priority. | Direct integration with provincial central intake queues. | Automated patient email and SMS status updates. | **Yes.** Closed-loop status updates sent back to referring clinician's EMR inbox. | **Milestone tracking.** Tracks initial consult, surgical booking, and discharge. | High dependence on provincial EMR adoption (Telus, Oscar, Accuro); does not track real-time emergency resources. | **Grade B** (Ocean Platform Architecture, 2023) |

---

## 3. The Precise Innovation Gap for CLINOVA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE REMAINING REFERRAL GAP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHAT EXISTING COMMERCIAL SYSTEMS SOLVE:                                    │
│  ✅ Inbound fax/document parsing and OCR                                     │
│  ✅ Provider directory matching (insurance, specialty, distance)             │
│  ✅ Calendar appointment scheduling and EHR write-back                      │
│  ✅ Administrative closed-loop tracking (booked ──> attended)                │
│                                                                             │
│  WHAT REMAINS COMPLETELY UNSOLVED IN EXISTING PLATFORMS:                    │
│  ❌ Real-time facility capability validation under acute emergency stress    │
│     (Does the destination have functioning oxygen, blood, CT, and ICU right  │
│      now, or will the patient arrive only to be turned away?)               │
│  ❌ Dynamic clinical urgency synthesis                                      │
│     (Matching physiological risk trajectory to golden-hour transit times)   │
│  ❌ Zero-cost, vernacular-friendly deployment in public health systems       │
│     (Existing tools cost tens of thousands in SaaS licenses per hospital)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Elective Scheduling vs Acute Feasibility
All audited commercial platforms (ReferralMD, Kyruus, AristaMD, NHS e-RS) are designed for **scheduled, elective, or semi-urgent outpatient appointments**. They answer: *"Which clinic has an open appointment slot next Thursday for a patient with Blue Cross insurance?"*

In contrast, the crisis in public healthcare in India occurs in **acute, time-critical, emergency inter-facility transfers**. When a primary health center or district hospital refers an acute trauma patient, septic infant, or severe dengue case, the question is:
$$\mathbf{Can\ this\ hospital\ physically\ execute\ emergency\ resuscitation\ and\ surgery\ RIGHT\ NOW?}$$

### 3.2 The Multi-Tier Feasibility Engine
Existing systems match referrals based on static provider tags (e.g., "General Surgery available"). CLINOVA's `FACILITYGRAPH` evaluates five interdependent dimensions:
1. **Emergency & Resuscitation Capability Tier** (Airway, suction, mechanical ventilator).
2. **On-Duty Specialist Presence** (Not just on the hospital roster, but physically logged on shift today).
3. **Diagnostic Infrastructure State** (Hematology analyzer calibrated, contrast CT online).
4. **Bed Capacity & Occupancy Pressure** (ICU occupancy < 95%, open resuscitation bays).
5. **Geospatial Transit Feasibility** (Transit distance via local Haversine calculations compared to clinical golden-hour urgency).

### 3.3 Audit Conclusion on Referral Novelty
- **Do NOT claim:** Automated referral intake, closed-loop tracking, or provider matching as novel inventions.
- **Defensible Claim:** **Resource-aware, capability-matched emergency referral routing** that couples physiological patient trajectory (`CAREGRAPH`) with real-time institutional care feasibility (`FACILITYGRAPH`) at ₹0 open-source infrastructure cost.
