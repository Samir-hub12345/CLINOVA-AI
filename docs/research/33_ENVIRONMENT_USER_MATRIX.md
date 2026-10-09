# CLINOVA AI — Target Environment & Operational User Matrix

> **Document ID:** `RES-33`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Healthcare Human Factors Research Group  

---

## 1. Executive Summary

Healthcare in India does not operate in a homogenous, well-resourced hospital environment. An acute triage and care navigation platform designed solely for an air-conditioned corporate hospital will fail catastrophically when deployed in an overburdened rural Primary Health Centre (PHC) or an episodic public health outreach camp.

This document systematically cross-maps all eight CLINOVA user roles across **six distinct operational healthcare environments**:
1. **Government Hospital (District Hospital / Sub-Divisional Hospital / Medical College)**
2. **Primary Health Centre (PHC / Ayushman Arogya Mandir / CHC)**
3. **Public Health Camp (Mobile Outreach / Rural Screening Camp)**
4. **Company Clinic (Corporate / IT Park Wellness Centre)**
5. **Industrial Health Unit (High-Hazard Manufacturing, Mining, Petrochemical)**
6. **Campus Health Centre (University & Residential College Clinic)**

Each environment is analyzed across **16 operational, clinical, and infrastructural dimensions**, establishing explicit constraints for hardware, connectivity, staffing ratios, time pressure, and decision boundaries.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SIX OPERATIONAL DEPLOYMENT ARCHETYPES                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. GOVERNMENT HOSPITAL    │ Extreme volume (500–2000/d), 90s consults,     │
│                            │ chaotic queues, multi-tier specialist staff    │
│  2. PRIMARY HEALTH CENTRE  │ Rural outpost (40–120/d), single MO, heavy     │
│                            │ ASHA/ANM dependence, blind referral crisis     │
│  3. PUBLIC HEALTH CAMP     │ High-speed screening (300–800/d), 100% offline,│
│                            │ transient team, severe loss-to-follow-up       │
│  4. COMPANY CLINIC         │ Low acute volume (20–50/d), high privacy,      │
│                            │ occupational health, desk worker ergonomics    │
│  5. INDUSTRIAL HEALTH UNIT │ Variable load, acute trauma/chemical burns,    │
│                            │ strict statutory OSHA logs, Golden Hour rush   │
│  6. CAMPUS HEALTH CENTRE   │ High minor illness (50–150/d), hostel contagions│
│                            │ mental health sensitivity, student privacy     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Cross-Environment Comparison Matrix

| Operational Dimension | 1. Government Hospital | 2. Primary Health Centre (PHC) | 3. Public Health Camp | 4. Company Clinic | 5. Industrial Health Unit | 6. Campus Health Centre |
|:---|:---|:---|:---|:---|:---|:---|
| **1. Existing Users** | Clinician, Nurse, Referral Staff, Patient, Caregiver, Facility Admin, Sys Admin | Clinician, Nurse (ANM/ASHA), Patient, Caregiver, Facility Admin | Clinician, Nurse (ANM/ASHA/Student), Patient, Caregiver, Camp Lead | Clinician, Nurse, Patient, Facility Admin | Clinician (Factory MO), Nurse/Paramedic, Patient, Safety Officer | Clinician, Nurse, Patient, Counselor, Hostel Warden |
| **2. Primary Roles** | Clinician, Nurse, Referral Staff | Clinician, Nurse (ANM/ASHA) | Nurse (ANM/ASHA), Clinician | Clinician, Nurse, Patient | Clinician (Factory MO), Nurse/Paramedic | Clinician, Nurse, Patient |
| **3. Secondary Roles** | Patient, Caregiver, Facility Admin, Sys Admin | Patient, Caregiver, Facility Admin | Patient, Caregiver, Camp Lead | Facility Admin, Caregiver | Safety Officer, Facility Admin, Caregiver | Counselor, Facility Admin, Caregiver |
| **4. Typical Daily Volume** | 500 – 2,000 OPD; 50 – 200 Emergency | 40 – 120 OPD; 5 – 15 Acute / Maternal | 300 – 800 Screenings (6–8 hours) | 20 – 60 Consults | 10 – 30 Routine; sudden trauma spikes (10–50) | 50 – 150 Consults (seasonal spikes to 250) |
| **5. Time Pressure** | Extreme (60–90 seconds per patient) | High (2–4 minutes per patient) | Severe (45–60 seconds per screening) | Relaxed (10–15 minutes per patient) | Extreme during trauma ($< 60$s); relaxed routine | Moderate (3–5 minutes per patient) |
| **6. Digital Maturity** | Low–Medium (Registrars use e-Hospital; paper charts rule) | Low (Tablets used for ANM portals; heavy paper books) | Very Low (Paper tally sheets dominate) | High (Fully digital, paperless workflows) | Medium (Statutory paper logs + basic digital reporting) | High (Students & doctors comfortable with web apps) |
| **7. Connectivity** | Intermittent LAN; patchy mobile 4G; frequent DNS stalls | Highly Intermittent (2G/3G cellular; daily outages) | Completely Offline (zero guaranteed cellular/broadband) | High-speed dedicated enterprise fiber broadband | Reliable wired plant intranet; restricted external internet | Reliable campus Wi-Fi + 4G cellular |
| **8. Available Devices** | Legacy Desktop PCs (Core i3, 4GB RAM), triage tablet | Government Android Tablets (2–3GB RAM), MO smartphone | Battery-operated tablets, laptops, volunteer phones | High-end laptops / PCs (16GB RAM), dual-screen setups | Ruggedized industrial PC terminals, emergency tablet | Clinic desktop PC, student smartphones, kiosk |
| **9. Staff Composition** | Casualty MOs, PG Residents, Staff Nurses, GDAs, Sweepers | 1 MBBS MO, 1 Ayush MO, 2–3 ANMs, 1 Pharmacist, ASHAs | 1–2 Volunteer MOs, 4–8 Nursing students, 10+ ASHAs | 1 Occupational Physician (part-time), 1 Staff Nurse | 1 Factory Medical Officer (AFIH), 2 Industrial Paramedics | 1–2 Campus Doctors, 2 Staff Nurses, 1 Counselor |
| **10. Specialist Access** | On-site (Medicine, Surgery, OBGYN, Peds, Ortho, Anesthesia) | None (Visiting gynecologist/pediatrician 1x/month) | None (General outreach only) | None (Empanelled tele-specialist network) | None (Contracted tertiary trauma hospital network) | None (Visiting psychiatrist/dermatologist 1x/week) |
| **11. Diagnostic Availability** | Central Lab (CBC, LFT, KFT), X-Ray, CT, Ultrasound, ECG | Basic POC: Hb meter, urine dipstick, malaria RDT, BP, sugar | Fingerstick glucose, rapid BP, pulse oximeter only | Connected digital vitals, basic POC blood tests | Rapid toxicology screens, spirometry, ECG, trauma ultrasound | Rapid antigen kits (Dengue, Covid, Malaria), basic urine |
| **12. Referral Complexity** | Internal inter-departmental transfers; tertiary transfers | High: Distant District Hospital (20–60 km); no bed tracking | High: Directing screen-positive patients to nearest PHC/CHC | Low: Direct transfer to preferred empanelled private hospital | Critical: Emergency ambulance run to Level-1 Trauma/Burn Centre | Moderate: University ambulance to city medical college |
| **13. Emergency Complexity** | High: Resuscitation bay, polytrauma, STEMI, severe sepsis | Moderate: Basic CPR, oxygen cylinder, IV fluids, 108 call | Low: Immediate stabilization and packaging into camp vehicle | Low: First-aid, AED, acute chest pain stabilization | Extreme: Chemical burns, toxic inhalation, crush injuries, blast | Moderate: Anaphylaxis, sports trauma, acute panic/suicide risk |
| **14. Follow-up Complexity** | Extremely High attrition ($> 70\%$ lost to follow-up) | Managed via ASHA village registers & VHSND days | Near-Total Attrition ($> 85\%$ un-contactable post-camp) | Highly Structured: Automated email/calendar check-ins | Statutory Mandate: Mandatory fitness-to-work re-evaluation | Simple: Student hostel revisit tracking; SMS check-in |
| **15. Privacy Constraints** | Low physical privacy (crowded OPDs); high data confidentiality | Low physical privacy (veranda consultations); community known | Minimal physical privacy (open tent screening desks) | Maximum Privacy: Employee health shielded from HR/employer | High Privacy: Medical records separate from HR personnel files | High Privacy: Confidentiality regarding mental/sexual health |
| **16. Operational Constraints** | Severe queue crowding, noise, violence against doctors | Power grid outages, single-doctor fatigue, drug stockouts | Battery life limits, dust, heat, lack of running water | Strict corporate IT firewall and zero-trust policies | High ambient factory noise, PPE requirements, safety drills | Academic calendar surges (exams, seasonal monsoon fevers) |

---

## 3. Granular Deep-Dive by Operating Environment

### 3.1 Environment 1: Government Hospital (District / Sub-Divisional Hospital)

#### 3.1.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** A typical District Hospital in Odisha or Uttar Pradesh processes 800 to 1,800 outpatients every morning between 8:00 AM and 1:30 PM. The OPD waiting hall is an un-airconditioned, crowded space where 150+ patients wait simultaneously.
- **The "90-Second Doctor" Problem:** A single Medical Officer examines 80–120 patients per 4-hour shift. The average consultation window is 60 to 90 seconds. Any digital tool that adds 30 seconds of typing will be immediately discarded by the physician in favor of handwritten scribbles on a paper ticket.
- **Staff Hierarchies:** Clear division between Casualty Medical Officers (CMO), Resident Doctors, Staff Nurses, and General Duty Assistants (GDAs). Nurses do not have prescribing authority and are overwhelmed with procedural tasks (injections, dressings).
- **Physical Triage Infrastructure:** Triage is often visual and subjective. High-risk patients with atypical presentations (e.g., painless diabetic MI or normotensive sepsis) frequently wait hours in the general queue before collapsing.

#### 3.1.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Standard desktop PCs at doctor desks; wall-mounted token queue displays; tablet for triage nursing desk.
- **Connectivity:** Local network (LAN) client-server architecture with SQLite/PostgreSQL running on a local clinic server; zero dependency on external internet.
- **User Role Configuration:**
  - `ROLE_CLINICIAN`: Full high-density Doctor Workbench with rapid keyboard navigation (Enter to verify, Tab to jump).
  - `ROLE_NURSE`: Dedicated Missing-Data Worklist; rapidly enters vitals for waiting patients to update CAREGRAPH trajectory.
  - `ROLE_REFERRAL_STAFF`: Active Transfer Desk dashboard for managing outbound referrals to Medical College.
- **Critical Safety Constraint:** Deterministic red-flag alerts (`TRIAGE-R01` to `TRIAGE-R06`) must visually interrupt the doctor's queue if a waiting patient's serial vitals mutate to `WORSENING`.
- **Evidence Tag:** `SUPPORTED` (Lancet Oncology Indian OPD Audit 2021; AIIMS OPD Flow Study 2022; IPHS 2022).

---

### 3.2 Environment 2: Primary Health Centre (PHC / Ayushman Arogya Mandir)

#### 3.2.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** A rural PHC serves a catchment population of 20,000 to 30,000 citizens across 15–25 villages. Daily OPD volume is 40–100 patients.
- **The "Single Doctor" Dilemma:** The facility is staffed by a single MBBS Medical Officer who must also attend administrative meetings, court summons, and post-mortem duties. On many days, triage and clinical care are managed entirely by the Community Health Officer (CHO) or Auxiliary Nurse Midwife (ANM).
- **ASHA & ANM Workflow Reality:** Accredited Social Health Activists (ASHAs) escort pregnant women, malnourished children, and febrile patients to the PHC. They carry paper registers (MCTS / RCH register) and speak local vernacular dialects (Odia, Santhali, Bhojpuri).
- **The "Blind Referral" Crisis:** When a patient is unstable, the PHC doctor has no choice but to write a paper referral slip ("Referred to DHH") and call the 108 ambulance. The doctor has zero real-time visibility into whether the District Hospital 45 km away has an open ICU bed or a functioning ventilator. Over 50% of rural transit mortality occurs during these uncoordinated transfers.

#### 3.2.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Low-cost government Android tablets (2GB–3GB RAM) and MO personal smartphone; portable battery pack.
- **Connectivity:** Intermittent cellular (2G/4G). The system must operate **100% offline**, queuing referral packets and state updates locally until network syncs.
- **User Role Configuration:**
  - `ROLE_NURSE` (ANM / CHO): Uses vernacular voice intake (`B02`) in Odia/Hindi to record patient symptoms; measures vitals using basic tools; completes red-flag danger checklists.
  - `ROLE_CLINICIAN` (Single MO): Reviews synthesized notes on tablet/phone; evaluates FACILITYGRAPH care feasibility.
  - `ROLE_PATIENT`: Purely assisted intake; patients rarely operate the screen directly due to digital literacy limits.
- **Critical Innovation Deployment:** **FACILITYGRAPH Care Feasibility Matching (`C05`, `C06`)**. Instead of blind transfers, the system queries the regional capability graph to match the patient to a hospital with confirmed open beds, oxygen, and specialists.
- **Evidence Tag:** `SUPPORTED` (NHSRC PHC Evaluation Report 2023; MoHFW Rural Health Statistics 2022; Lancet Public Health India 2023).

---

### 3.3 Environment 3: Public Health Camp (Rural Outreach / Screening Camp)

#### 3.3.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** Episodic camps organized in village schoolrooms, temples, or community centres. 300 to 800 villagers arrive within a 6-hour window.
- **Extreme High-Throughput Screening:** The operational goal is rapid population-level screening for non-communicable diseases (hypertension, diabetes), anemia, cataract, and acute seasonal fevers. Clinicians have under 45 seconds per screening.
- **Total Infrastructure Void:** Zero reliable grid electricity, zero Wi-Fi, dusty open-air environment, extreme heat. All equipment runs on batteries.
- **The "Outcome Void" Problem:** Once the camp pack-up occurs at 4:00 PM, the medical team leaves. Screened patients with severe hypertension (e.g., BP 210/110) or suspicious lumps are given a handwritten paper slip and are almost completely lost to follow-up ($> 85\%$ attrition).

#### 3.3.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Volunteer Android tablets and laptops running local SQLite database; battery banks.
- **Connectivity:** Completely offline standalone mode (`OFFLINE_CAMP_MODE`).
- **User Role Configuration:**
  - `ROLE_HEALTH_WORKER` (Nursing students / ASHAs): Execute batch rapid screening intake (voice or rapid checkboxes); record fingerstick blood glucose and BP.
  - `ROLE_CLINICIAN`: Fast-tracks "Red Flag" cohort; reviews auto-flagged critical outliers; signs structured referral slips for local PHC/CHC follow-up.
- **Critical Innovation Deployment:** Batch PII scrubbing and automated structured referral slip generation with ASHA assignment to anchor community follow-up. Aggregated camp data exports to SIGNALGRAPH for village syndromic baselines.
- **Evidence Tag:** `SUPPORTED` (WHO Mobile Health Guidelines; ICMR Outreach Screening Audits).

---

### 3.4 Environment 4: Company Clinic (Corporate Campus / IT Park Clinic)

#### 3.4.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** 20 to 60 encounters per day in an IT park or corporate office. Presentations are dominated by ergonomic strains, migraines, acute anxiety, viral upper respiratory infections, and occasional executive cardiovascular emergencies.
- **The Employer Privacy Boundary:** Employees are acutely sensitive to privacy. If an employee suspects that seeking care for depression, pregnancy, or chronic illness will be reported to corporate HR or impact performance appraisals, they will boycott the clinic.
- **Digital Infrastructure:** High-speed gigabit fiber, dual-screen workstations, connected Bluetooth vital monitors. High digital literacy among patients.

#### 3.4.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Modern workstation PCs, mobile web portal for employee self-check-in.
- **Connectivity:** Enterprise cloud connection or local server.
- **User Role Configuration:**
  - `ROLE_PATIENT`: Independent self-intake via mobile portal; enters symptoms and past history directly.
  - `ROLE_CLINICIAN` (Occupational Physician): Detailed review; ergonomic and lifestyle evaluation.
  - `ROLE_FACILITY_ADMIN` (HR / Wellness Manager): Strictly walled off from clinical records. Can ONLY receive anonymized wellness trend statistics and binary "Fit / Unfit for Work" medical leave certificates.
- **Critical Safety Constraint:** Cryptographic role separation ensuring zero medical narrative or psychiatric screening notes can ever be viewed by non-clinical corporate personnel.
- **Evidence Tag:** `SUPPORTED` (Occupational Safety, Health and Working Conditions Code 2020; DPDP Act 2023).

---

### 3.5 Environment 5: Industrial Health Unit (Factory / Manufacturing / Mining Site)

#### 3.5.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** Located inside automotive factories, chemical plants, steel mills, or mines. Routine volume is low (10–30 occupational visits), but the clinic must handle catastrophic industrial emergencies: molten metal burns, chemical splashes, blast trauma, toxic gas inhalation, and limb crush injuries.
- **The "Golden Hour" Mandate:** In severe industrial trauma, on-site treatment is strictly limited to rapid decontamination, airway management, and high-velocity packaging for Level-1 trauma transfer within 15 minutes.
- **Statutory Reporting Requirements:** Every workplace injury is legally compensable and subject to statutory investigation under the Factories Act 1948 and OSHA norms. Detailed, tamper-evident documentation of incident time, PPE status, and initial clinical vitals is legally required.

#### 3.5.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Ruggedized, dust-proof industrial PC terminal in the medical room; rugged ambulance tablet.
- **Connectivity:** Local plant intranet with fail-safe local storage; tolerant of factory electromagnetic interference.
- **User Role Configuration:**
  - `ROLE_CLINICIAN` (Factory Medical Officer - AFIH certified): Resuscitation lead; rapid emergency classification.
  - `ROLE_NURSE` (Industrial Paramedic): Rapid trauma ABCD vitals acquisition ($< 30$ seconds); burn surface area estimation.
  - `ROLE_REFERRAL_STAFF`: Direct hotline to empanelled Burn/Trauma ICU; dispatches industrial ambulance.
- **Critical Innovation Deployment:** **Emergency Fast-Track Workflow (`DOC-16`, Stage 02 bypass)**. Strips away routine history prompts and renders instant toxic-exposure protocols, GCS calculators, and immediate FACILITYGRAPH matching for specialized regional burn/trauma centers.
- **Evidence Tag:** `SUPPORTED` (The Factories Act 1948; National Disaster Management Authority Guidelines on Chemical Disasters).

---

### 3.6 Environment 6: Campus Health Centre (University / Residential College)

#### 3.6.1 Clinical Reality & Ground Truth
- **Patient Journey Dynamics:** Serves 5,000 to 20,000 students and faculty. Typical volume is 50–150 visits per day. Presentations include sports injuries, infectious viral fevers, gastroenteritis, academic stress, acute depressive episodes, and substance misuse.
- **Hostel Contagion Vulnerability:** A single case of Dengue, Chickenpox, or Norovirus inside a high-density student hostel can cause an explosive outbreak of 100+ cases within a week.
- **Mental Health & Guardian Sensitivity:** Students seeking confidential reproductive or mental health care require strict privacy from university administrators, while acute suicide risk requires an emergency protocol to notify campus counselors and parents.

#### 3.6.2 Specific CLINOVA System Configuration
- **Hardware Profile:** Standard clinic PCs; student mobile self-intake web app.
- **Connectivity:** High-speed campus Wi-Fi network.
- **User Role Configuration:**
  - `ROLE_PATIENT` (Student): Self-intake on mobile device; vernacular or English options.
  - `ROLE_CLINICIAN`: Campus Doctor evaluating illness; can flag hostel contagion tags.
  - `ROLE_CAREGIVER` (Hostel Warden / Parent): Restricted view for emergency hospital transfer authorizations.
- **Critical Innovation Deployment:** **SIGNALGRAPH Campus Telemetry (`C07`)**. Aggregates anonymized syndromic fevers tagged by hostel building to provide early cluster warnings to campus health officials before full-scale dorm epidemics take hold.
- **Evidence Tag:** `SUPPORTED` (UGC Student Health Guidelines; Indian Journal of Community Medicine Campus Outbreak Audits).

---

## 4. Cross-Environment Capability & Constraint Summary

| Capability / Constraint | Government Hospital | PHC / AAM | Health Camp | Company Clinic | Industrial Unit | Campus Health |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Offline-First Requirement** | High (LAN server) | **Mandatory (Total)** | **Mandatory (Total)** | Low (Cloud ok) | High (Intranet) | Moderate (Wi-Fi) |
| **Voice Vernacular Intake** | Essential | **Critical (ASHA)** | **Critical** | Low (Text first) | Moderate | Low (English/Hindi) |
| **Document OCR Parsing** | **Critical (Old slips)** | Moderate | Low | High (PDF reports) | Moderate | Moderate |
| **Emergency Fast-Track UI** | **Critical** | Moderate | Low | Low | **Critical (Trauma)** | Moderate |
| **FACILITYGRAPH Referral** | Moderate (Tertiary) | **Critical (Lifeline)** | High | Low | **Critical (Burns)** | Moderate |
| **SIGNALGRAPH Surge Alerts** | **Critical (District)** | Moderate | High (Batch feed) | Low | Low | **Critical (Hostels)** |
| **Statutory Incident Logging**| Standard | Standard | Minimal | High (HR fit) | **Critical (OSHA)** | Moderate |
