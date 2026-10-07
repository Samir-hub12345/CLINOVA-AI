# CLINOVA AI — Design Specifications: Cluster 5 (FACILITYGRAPH, Orchestration & Disposition Pathways)

> **File:** `docs/design/05_FACILITY_ORCHESTRATION_AND_PATHWAYS.md`  
> **Screens Covered:** Screens 24 through 31  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 24: FACILITYGRAPH Local Capability Inspector

### 1. Specification
- **Route:** `/facilities/capability`
- **Purpose:** Inspect real-time physical capabilities, diagnostic machinery, bed counts, and staffing at the current healthcare facility.
- **Actor:** Medical Officer, Facility Administrator, Referral Coordinator.
- **Entry Condition:** Authenticated session.
- **Inputs:** Facility selector dropdown, service category filters (Emergency, Inpatient, Diagnostics, Blood Bank, Staff).
- **Outputs:** Real-time capability radar matrix, current bed occupancy bars, active on-duty specialist roster.
- **Actions:** "Update Bed Availability", "Toggle Equipment Maintenance Status", "View Network Interconnects".
- **Navigation:** Links to Screen 25.
- **Graph Linkage:** Reads and updates `FacilityNode` in FACILITYGRAPH.

### 2. Wireframe (Screen 24)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       FACILITYGRAPH Inspector         [ CAPITAL DIST HOSP]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FACILITY CAPABILITY & RESOURCE STATUS: CAPITAL DISTRICT HOSPITAL          │
│   Level: Secondary Referral Center | Network ID: FAC-OD-004                 │
│                                                                             │
│   DIAGNOSTIC CAPABILITIES               BED OCCUPANCY & CAPACITY            │
│   • 24/7 Hematology / CBC: [✓ ACTIVE]   • Emergency Resus: 4/4 [100% FULL] ⚠️│
│   • Contrast CT Scanner:   [✓ ACTIVE]   • Intensive Care (ICU): 8/8 [FULL] ⚠️│
│   • Ultrasound / FAST:     [✓ ACTIVE]   • High Dependency: 11/12 [92% FULL] │
│   • Blood Bank: [✓ PRBC] [❌ NO PLTLTS] • General Male Ward: 34/40 [85%]     │
│                                                                             │
│   ON-DUTY SPECIALIST ROSTER (TODAY):                                        │
│   • General Medicine: Dr. S. Mohapatra [ON-SITE]                            │
│   • General Surgery:  Dr. R. Patnaik   [IN EMERGENCY OT]                    │
│   • Pediatrics:       On Call (Field Visit)                                 │
│                                                                             │
│   [ UPDATE BED OCCUPANCY ]                     [ COMPARE REGIONAL NETWORK ] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 25: Facility Comparison & Care Feasibility Matrix

### 1. Specification
- **Route:** `/facilities/compare`
- **Purpose:** Multi-facility feasibility evaluation matching patient requirements against regional health facilities using Leaflet/OSM mapping and local Haversine calculations.
- **Actor:** Medical Officer, Referral Coordinator.
- **Entry Condition:** Patient requirement exceeds local facility capability or ICU capacity is saturated.
- **Inputs:** Filter by capability requirements (e.g., "Must have open ICU bed + Blood Platelets").
- **Outputs:** Side-by-side comparison matrix of candidate hospitals, transit distance (km), estimated ambulance travel time (mins), Leaflet network map.
- **Actions:** "Select Facility & Generate Referral Pack", "Recalculate Transit Times", "Contact Transfer Desk".
- **Navigation:** Selected hospital advances to Screen 31 (`/case/:id/handoff`).
- **Graph Linkage:** Core realization of the **Care Feasibility Engine** (C06).

### 2. Wireframe (Screen 25)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Care Feasibility & Referral      [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CARE FEASIBILITY EVALUATION: PATIENT REQUIRES ICU BED + PLATELET TRANSF. │
│                                                                             │
│   HOSPITAL NAME         CAPABILITY MATCH    OPEN BEDS   DIST.   ETA    ACT. │
│   ───────────────────── ─────────────────── ─────────── ─────── ────── ─────│
│   ⭐ SCB Medical College 100% (ICU, Pltlts)  4 ICU Open  28 km   42 min [SEL]│
│   AIIMS Bhubaneswar     100% (ICU, Pltlts)  2 ICU Open  34 km   50 min [SEL]│
│   Capital Hospital (Curr) 60% (No Pltlt Unit) 0 ICU Open   0 km    0 min [DEF]│
│                                                                             │
│   LEAFLET / OPENSTREETMAP ROUTE VISUALIZATION:                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ [MAP: Capital Hospital ● ═════ (28 km Highway) ═════> SCB Medical ●]  │ │
│   │ OpenStreetMap Tiles | Haversine Transit Calculation: 42 Mins (Traffic)│ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   [ CANCEL ]                       [ GENERATE STRUCTURED REFERRAL PACK ──>] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 26: ORCHESTRATION Engine Recommendation Screen

### 1. Specification
- **Route:** `/case/:id/orchestrate`
- **Purpose:** Present the synthesized **Safest Achievable Next Care Pathway** to the licensed physician with explicit rationale, evidence justification, and override controls.
- **Actor:** Medical Officer.
- **Entry Condition:** Doctor review on Screen 22.
- **Inputs:** Action selection radio buttons (`Accept Pathway`, `Select Alternative`, `Custom Disposition`).
- **Outputs:** Highlighted recommendation card, evaluation rationale, safety bounds, required clinical orders checklist.
- **Actions:** "Execute Safest Pathway", "Override with Custom Plan", "Print Clinical Summary".
- **Navigation:** Routes to Pathway A (Screen 27), Pathway B (Screen 28), Pathway C (Screen 29), or Referral (Screen 25).
- **Graph Linkage:** The operational realization of the **ORCHESTRATION Engine** (C08 / C09).

### 2. Wireframe (Screen 26)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Orchestration Recommendation     [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   THE SAFEST ACHIEVABLE NEXT CARE PATHWAY (ADVISORY RECOMMENDATION)         │
│                                                                             │
│   RECOMMENDED ACTION: 🚨 IMMEDIATE RESUSCITATION & TERTIARY REFERRAL STANDBY│
│                                                                             │
│   SYNTHESIS RATIONALE:                                                      │
│   1. CareGraph Acuity: Hypotensive shock (BP 88/60) with platelets 42k/μL   │
│   2. Evidence Quality: 100% verified point-of-care data; zero uncertainty.  │
│   3. FacilityGraph Status: Local facility lacks platelet unit & ICU beds.   │
│   4. Feasibility Verdict: Initiate STAT IV crystalloids on-site; dispatch   │
│      urgent transfer to SCB Medical College (28 km / 42 mins).              │
│                                                                             │
│   CLINICAL ORDERS CHECKLIST:                                                │
│   [X] Insert 2 large-bore peripheral IV lines (16G/18G)                    │
│   [X] Infuse 500 mL normal saline bolus over 30 mins                        │
│   [X] Transmit Referral Pack to SCB Medical College Transfer Desk           │
│                                                                             │
│   [ OVERRIDE ADVISORY ]                     [ CONFIRM & EXECUTE PATHWAY [✓]]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 27: Routine Home Care & Follow-up Calendar (Pathway A)

### 1. Specification
- **Route:** `/case/:id/routine`
- **Purpose:** Manage outpatient discharge for stable, low-risk patients with take-home instructions and recurring calendar booking.
- **Actor:** Medical Officer, Patient.
- **Entry Condition:** Doctor confirms `ROUTINE_HOME_CARE`.
- **Inputs:** Recurring schedule interval (e.g., "Every 4 weeks"), prescription notes, diet/lifestyle instructions.
- **Outputs:** Routine discharge slip with calendar appointment dates and red-flag return warnings.
- **Actions:** "Book Calendar Appointment", "Print Patient Discharge Slip", "Send SMS Reminder".
- **Navigation:** Completes encounter and updates Master Case.
- **Graph Linkage:** Commits to `MasterCase.follow_up_record` and updates CAREGRAPH to `RESOLVED_ROUTINE`.

### 2. Wireframe (Screen 27)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Routine Care & Calendar          [ CASE: PT-94002 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PATHWAY A: ROUTINE DISCHARGE & RECURRING FOLLOW-UP CALENDAR               │
│   Patient: 34M | Disposition: Stable Upper Respiratory Infection / Routine  │
│                                                                             │
│   [1. Recurring Follow-Up Schedule]                                         │
│   Revisit Interval: [ Every 4 Weeks ▼ ]  Next Date: [ 05-Nov-2026 10:00 AM] │
│   Clinic Room: Room 2 (Outpatient Medicine) | Clinician: Dr. Mohapatra      │
│                                                                             │
│   [2. Approved Patient Instructions (Vernacular Odia & English)]            │
│   • Complete oral medication course as prescribed.                          │
│   • Maintain adequate hydration (>2.5 liters/day).                          │
│   • Return immediately if fever exceeds 39°C or breathing becomes labored.  │
│                                                                             │
│   [ 📱 SEND SMS REMINDER ]                     [ PRINT DISCHARGE SUMMARY ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 28: Further Review & Single Revisit Scheduler (Pathway B)

### 1. Specification
- **Route:** `/case/:id/revisit`
- **Purpose:** Schedule a single, short-interval targeted revisit for pending diagnostic reports or clinical reassessment. (Distinct from recurring chronic checkups!).
- **Actor:** Medical Officer, Patient.
- **Entry Condition:** Doctor confirms `FURTHER_REVIEW`.
- **Inputs:** Pending investigation checklist (Ultrasound, Biopsy, Blood Culture), target return date/time window (e.g., "In 48 Hours").
- **Outputs:** Single-revisit appointment slip with pending investigation instructions.
- **Actions:** "Confirm Revisit Slot", "Print Revisit Slip", "Send Single Alert".
- **Navigation:** Completes initial session; holds Master Case in `PENDING_REVIEW` state.
- **Graph Linkage:** Keeps `MasterCase` open with pending uncertainty targets.

### 2. Wireframe (Screen 28)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Single Revisit Scheduler         [ CASE: PT-94012 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PATHWAY B: FURTHER REVIEW & SINGLE REVISIT SCHEDULER                      │
│   Patient: 12M | Presentation: Subacute Abdominal Pain / Rule-Out Appendic. │
│                                                                             │
│   TARGET REVISIT WINDOW: [ In 24 Hours: 09-Oct-2026 at 09:00 AM ]           │
│                                                                             │
│   PENDING INVESTIGATIONS REQUIRED AT REVISIT:                               │
│   [X] Ultrasound Abdomen (Booked for tomorrow 08:30 AM at Radiology)        │
│   [X] Repeat Complete Blood Count (TLC / Neutrophil differential)           │
│                                                                             │
│   CLINICAL REASSESSMENT MANDATE:                                            │
│   Evaluate for localization of right iliac fossa tenderness and guarding.   │
│                                                                             │
│   [ PRINT SINGLE REVISIT SLIP ]                [ CONFIRM APPOINTMENT SLOT ] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 29: Inpatient Ward Admission Request (Pathway C)

### 1. Specification
- **Route:** `/case/:id/admission`
- **Purpose:** Physician admission requisition detailing target ward, admitting diagnosis, comorbidity dossier, and precaution flags.
- **Actor:** Medical Officer.
- **Entry Condition:** Doctor selects `WARD_ADMISSION`.
- **Inputs:** Target ward selector (Medical, Surgical, Pediatric, HDU), urgency level, initial admission orders, isolation/precaution checkboxes.
- **Outputs:** Requisition summary sent to ward nursing worklist.
- **Actions:** "Transmit Admission Requisition", "Print Admission Order".
- **Navigation:** Advances to Screen 30 on ward staff workstation.
- **Graph Linkage:** Initializes `MasterCase.admission_record`.

### 2. Wireframe (Screen 29)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Inpatient Ward Requisition       [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PATHWAY C: INPATIENT WARD ADMISSION REQUISITION                           │
│   Patient: 45M | Admitting Diagnosis: Severe Dengue / Fluid Decompensation  │
│                                                                             │
│   Target Ward: [ High Dependency Unit (HDU) ▼ ]  Urgency: [ STAT / Immed.▼]│
│                                                                             │
│   PRECAUTIONS & NURSING FLAGS:                                              │
│   [X] Strict Intake/Output Charting (Hourly)  [X] Fall Risk Precaution      │
│   [X] Continuous Cardiac / SpO2 Monitoring   [ ] Contact Isolation         │
│                                                                             │
│   INITIAL ADMISSION ORDERS:                                                 │
│   1. IV Normal Saline at 100 mL/hr via infusion pump.                       │
│   2. Stat CBC every 12 hours; alert if platelets drop below 20,000/μL.      │
│                                                                             │
│   [ CANCEL ]                      [ TRANSMIT REQUISITION TO WARD DESK ──>]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 30: Staff Admission Verification

### 1. Specification
- **Route:** `/ward/verify/:id`
- **Purpose:** Inpatient ward nursing desk accepts the incoming transfer, confirms physical bed availability, and verifies allergy alerts.
- **Actor:** Ward Staff Nurse, Inpatient Charge Nurse.
- **Entry Condition:** Incoming admission requisition from Screen 29.
- **Inputs:** Assigned physical bed ID (e.g., "Bed HDU-03"), admitting nurse ID.
- **Outputs:** Bed board confirmation, allergy cross-check alert.
- **Actions:** "Accept & Assign Bed", "Flag Bed Delay", "Open Handoff Screen".
- **Navigation:** Advances to Screen 31 (`/case/:id/handoff`).
- **Graph Linkage:** Mutates `MasterCase.admission_record.bed_id`.

### 2. Wireframe (Screen 30)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Ward Bed Verification            [ HDU WARD DESK ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INCOMING INPATIENT ADMISSION VERIFICATION: CASE PT-94021                  │
│   Patient: 45M | Service: Internal Medicine HDU | Dr. S. Mohapatra          │
│                                                                             │
│   ASSIGN PHYSICAL BED: [ Bed HDU-03 (Clean & Prepared) ▼ ]                  │
│                                                                             │
│   ALLERGY & MEDICATION SAFETY CHECK:                                        │
│   • Known Allergies: None Reported [✓]                                      │
│   • Active Orders Verified: Hourly I/O Charting, Continuous SpO2 [✓]        │
│                                                                             │
│   Status: Bed Reserved. Awaiting physical patient escort from Triage.       │
│                                                                             │
│   [ REJECT / WARD FULL ]                       [ PROCEED TO SBAR HANDOFF ]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 31: Transfer & SBAR Handoff Screen

### 1. Specification
- **Route:** `/case/:id/handoff`
- **Purpose:** Formal clinical handoff screen implementing structured SBAR (Situation, Background, Assessment, Recommendation) transfer with mandatory dual digital sign-off.
- **Actor:** Transferring Triage Nurse, Receiving Ward/Ambulance Nurse.
- **Entry Condition:** Patient arrives at ward or ambulance bay.
- **Inputs:** Handoff checklist confirmations, transferring staff PIN, receiving staff PIN.
- **Outputs:** Complete SBAR dossier, dual digital signature timestamps.
- **Actions:** "Execute Two-Party Handoff", "Generate Ward Admission Report (Type 4)".
- **Navigation:** Completes handoff; generates Report Type 4.
- **Graph Linkage:** Sets `MasterCase.admission_record.handoff_checklist_confirmed = True`.

### 2. Wireframe (Screen 31)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       SBAR Clinical Handoff            [ CASE: PT-94021 ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STRUCTURED SBAR HANDOFF & CUSTODY TRANSFER                                │
│                                                                             │
│   [S] SITUATION: 45M with severe Dengue, admitted for fluid resuscitation.  │
│   [B] BACKGROUND: 4-day fever, petechial rash, platelets 42k/μL.            │
│   [A] ASSESSMENT: BP 88/60 on admission, now 96/68 post-500mL saline bolus. │
│   [R] RECOMMENDATION: Continue IV NS @ 100 mL/hr, repeat vitals every 30m. │
│                                                                             │
│   TWO-PARTY CLINICAL CHECKLIST:                                             │
│   [X] Patient wristband & synthetic ID verified at bedside                  │
│   [X] 18G IV cannula patent in left forearm with saline running             │
│   [X] Physical chart, lab slips, and medication sheet transferred           │
│                                                                             │
│   Transferring Nurse: Sister S. Nayak   [ PIN: •••• ] [✓ SIGNED 11:15 AM]   │
│   Receiving Ward Nurse: Sister P. Das   [ PIN: •••• ] [✓ SIGNED 11:16 AM]   │
│                                                                             │
│   [ COMPLETE HANDOFF & GENERATE WARD ADMISSION REPORT (TYPE 4) ]            │
└─────────────────────────────────────────────────────────────────────────────┘
```
