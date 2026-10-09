# CLINOVA AI — Target Environment Specification: Primary Health Centre (PHC)

> **Document ID:** `RES-45`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Environment Identification & Core Purpose

- **ENVIRONMENT ID:** `ENV_PHC`
- **ENVIRONMENT NAME:** Primary Health Centre (PHC / Ayushman Arogya Mandir / Block Primary Health Outpost)
- **PURPOSE:** Serves as the primary public clinical gateway for rural, tribal, and peripheral populations. Delivers basic outpatient consultations, maternal-child health (MCH) interventions, national disease control program execution, non-communicable disease (NCD) screening, first-aid acute stabilization, and timely referral navigation onward to Community Health Centres (CHCs) and District Hospitals.
- **TYPICAL LOCATION / CONTEXT:** Rural gram panchayats, block sub-districts, hilly tribal tracts, and remote agrarian belts across India (mandated under IPHS 2022 to cover 20,000–30,000 population in plains, and 10,000–20,000 in hilly/tribal areas). Standalone single-story government buildings, unpaved or narrow access roads, unconditioned clinical rooms, and frequent ambient dust and power cuts.

---

## 2. Stakeholders & Patient Demographics

- **PRIMARY USERS:**
  - Medical Officer (`ROLE_CLINICIAN`): Typically a single MBBS doctor (often a recent graduate serving a mandatory rural service bond or contractual recruit).
  - Community Health Officer (CHO) / Staff Nurse (`ROLE_NURSE`): B.Sc. Nursing or GNM trained health professional running daily triage and non-communicable disease screenings.
  - Auxiliary Nurse Midwife (ANM) (`ROLE_HEALTH_WORKER`): Grassroots health worker managing maternal-child immunization, antenatal care, and field registers.
  - Accredited Social Health Activist (ASHA) (`ROLE_HEALTH_WORKER`): Community health mobilizer bringing rural beneficiaries from isolated hamlets.
- **SECONDARY USERS:**
  - Pharmacist / Multipurpose Health Worker (Male) (Dispensing and dressing station ops).
  - Block Medical Officer of Health (BMOH) / CHC Superintendent (`ROLE_FACILITY_ADMIN`).
  - 108 Emergency Ambulance Driver / Liaison (`ROLE_REFERRAL_STAFF`).
  - Rural patients and their family caregivers (`ROLE_PATIENT`, `ROLE_CAREGIVER`).
- **PATIENT / BENEFICIARY TYPES:** Smallholder farmers, daily wage agricultural laborers, pregnant women, neonates and infants, elderly patients with uncontrolled hypertension/diabetes, rural trauma/snakebite victims, and economically disadvantaged rural families.
- **PATIENT VOLUME:**
  - Outpatient Department (OPD): 40 to 120 patient presentations per day.
  - Acute / Emergency presentations: 2 to 10 acute life-threatening presentations per week (snakebites, poisonings, acute asthma, obstructed labor).
- **EXPECTED WAITING PRESSURE:** Moderate absolute numbers, but severe morning compression. 80% of patients arrive between 09:00 and 11:30 due to shared rural transport schedules (bus/auto-rickshaw). If consultations are delayed past 12:30, patients leave without care to catch the only return transport home.

---

## 3. Clinical Case Mix & Acuity Distribution

- **TYPICAL CASE TYPES:** Acute febrile illness (malaria, viral fever, scrub typhus, typhoid), acute gastroenteritis and childhood diarrhea, chronic primary hypertension, type 2 diabetes mellitus, superficial skin infections (scabies, impetigo, tinea), minor agricultural lacerations and soft-tissue injuries, musculoskeletal backache/osteoarthritis, respiratory tract infections, and antenatal assessments.
- **ROUTINE CASES:** Antenatal care checkups (ANC), infant routine immunization, oral rehydration therapy dispensing, repeat prescription refills for hypertension and diabetes, distribution of iron-folic acid and calcium supplements, and routine dressing changes for farm scrapes.
- **URGENT CASES:** Persistent high fever with vomiting and poor oral intake, moderate pediatric dehydration, severe asthma/COPD wheezing exacerbation, infected agricultural lacerations with cellulitis, uncontrolled hypertension with severe headache, and non-healing diabetic foot ulcers.
- **EMERGENCY CASES:** Venomous snakebite (vasculotoxic or neurotoxic envenomation), organophosphate/pesticide poisoning, obstructed labor / impending eclampsia, severe neonatal hypothermia or asphyxia, pediatric foreign body aspiration, anaphylaxis from insect stings, acute coronary syndrome (ACS) presenting remotely, and hypovolemic shock.

---

## 4. Entry Pathways, Identity & Consent

- **ENTRY MODES:**
  1. *Walk-In Primary Presentation:* Rural villagers arriving on foot, bicycles, or shared autos.
  2. *ASHA-Escorted Presentation:* Beneficiaries accompanied directly by village ASHA workers who provide verbal history.
  3. *Acute Farm / Emergency Transport:* Emergency arrival via motorcycle, tractor-trailer, or hired auto following snakebite, trauma, or toxic ingestion.
  4. *Maternal Labor Arrival:* Pregnant women arriving in active labor via 102 Janani Shishu Suraksha Karyakram (JSSK) ambulances.
- **REGISTRATION METHOD:** Manual paper-based entry in the central OPD Register (Register 1) maintained by the ANM or pharmacist. Secondary entry into national digital portals (ABDM ABHA, e-Sanjeevani, NCD Portal) is executed intermittently via government tablets when wireless reception permits.
- **IDENTITY AVAILABILITY:** Inconsistent. Beneficiaries frequently carry paper photocopies of their Aadhaar card, Ration card, or handwritten immunization/ANC cards. Elderly villagers frequently possess no identity documentation on their person, or have significant phonetic discrepancies across legal documents.
- **CONSENT CONTEXT:** Implicit verbal consent for standard primary care. Deep social trust in local ASHAs and ANMs. High medicolegal apprehension by solo Medical Officers regarding delayed transfers; clinicians require explicit documentation of patient refusal or referral acceptance to protect against community retribution.

---

## 5. Staffing Ratios & Clinician Availability

- **AVAILABLE STAFF:**
  - 1 Medical Officer (MBBS) (often the sole registered clinician for the entire catchment area).
  - 1 Community Health Officer (CHO) / Staff Nurse.
  - 1 to 2 ANMs.
  - 1 Pharmacist / Lab Technician (frequently a dual-responsibility post or vacant).
- **CLINICIAN AVAILABILITY:** Intermittent and fragile. Officially scheduled from 09:00 to 14:00, but the single Medical Officer is frequently pulled away for district administrative review meetings, post-mortem duties at sub-divisional morgues, VIP protocol events, or mandatory court appearances. During doctor absences, the PHC is operated entirely by the CHO and ANM.
- **NURSING / HEALTH-WORKER AVAILABILITY:** Continuous and resilient. Frontline ANMs, CHOs, and visiting ASHAs maintain high, uninterrupted presence on-site and serve as the foundational backbone of clinical operations.
- **SPECIALIST AVAILABILITY:** Absolute zero. No general physicians, surgeons, pediatricians, obstetricians, or anesthesiologists exist on-site. The nearest specialist is stationed at the Block CHC (15–35 km away) or District Hospital (30–80 km away).

---

## 6. Diagnostic, Procedural & Infrastructure Capabilities

- **DIAGNOSTIC CAPABILITY:** Minimal point-of-care rapid diagnostics only.
- **LAB CAPABILITY:** Point-of-care rapid diagnostic kits (RDT) only: digital hemoglobinometer (or Sahli’s), urine dipsticks (protein/glucose), digital glucometer strips, rapid lateral-flow antigen kits (Malaria *Pf*/*Pv*, Dengue NS1/IgM, Syphilis, HIV, Urine Pregnancy Test). No automated hematology analyzers, no clinical biochemistry, no blood culture, and zero blood bank/storage units.
- **IMAGING CAPABILITY:** Completely absent. Zero plain X-ray, zero ultrasound, and zero CT capability. Electrocardiography (ECG) is either absent or limited to a single portable single-lead ECG device where interpretation must be done remotely.
- **MEDICATION / PHARMACY CONTEXT:** State Essential Drugs List (EDL) primary health pack. Oral generic formulations (paracetamol, amoxicillin, ciprofloxacin, metronidazole, cetirizine, amlodipine, metformin, albendazole, ORS packets). Emergency injectable inventory strictly limited to: adrenaline, hydrocortisone, atropine, oxytocin, diazepam, tetanus toxoid, and a limited supply of Polyvalent Anti-Snake Venom (ASV) (subject to erratic cold chain maintenance).
- **BED / OBSERVATION CAPACITY:** 4 to 6 basic non-monitored beds designated for uncomplicated normal vaginal delivery observation and acute oral rehydration therapy (ORT). Zero ICU, zero High Dependency Unit (HDU), zero mechanical ventilators.
- **OT / PROCEDURE CAPABILITY:** Minor dressing room only. Wound cleansing, primary single-layer skin suturing, abscess drainage, and uncomplicated normal vaginal deliveries in the clean labor room. Zero major surgical capacity.
- **EMERGENCY CAPABILITY:** Elementary stabilization prior to urgent transfer. 1 to 2 oxygen cylinders with manual flowmeters (or a solar-powered oxygen concentrator), foot-operated suction pump, pediatric and adult Bag-Valve-Mask (Ambu) units, and peripheral IV cannulation supplies with Ringer’s Lactate and Normal Saline. Defibrillators are absent.

---

## 7. Referral, Transport & Outcome Linkages

- **REFERRAL CAPABILITY:** High referral generator. 10% to 25% of all non-routine presentations exceed the diagnostic or therapeutic capability of the PHC and must be referred upward to First Referral Units (CHCs) or District Hospitals.
- **TRANSPORT / TRANSFER CONTEXT:** Reliance on the centralized 108 Emergency Ambulance network and 102 maternal transport services. Ambulance dispatch response times in remote rural sectors range from 30 to 75 minutes. In acute envenomation or hemorrhage, families frequently reject waiting for the ambulance and transport patients on private motorcycles or auto-rickshaws, frequently leading to respiratory arrest or fatal shock en route.
- **FOLLOW-UP CAPABILITY:** Robust grassroots community follow-up mediated by village ASHAs and monthly Village Health Sanitation and Nutrition Days (VHSND).
- **OUTCOME DATA AVAILABILITY:** Near-zero. Once a patient is dispatched in an ambulance to a District Hospital or Medical College, the PHC Medical Officer and ANM almost never receive discharge summaries, operative reports, or confirmation of patient survival ("the referral black hole").

---

## 8. Digital Infrastructure, Hardware & Connectivity Constraints

- **DIGITAL MATURITY:** Low to moderate. Primary data collection occurs via government-issued Android tablets (e.g., ANMOL tablet for maternal-child tracking) and personal smartphones. Desktop computers are rarely functional due to voltage surges or lack of maintenance.
- **DEVICE AVAILABILITY:** 1 to 3 government-issued Android tablets (ARM-based, 2GB–3GB RAM) shared among the CHO and ANMs; 1 personal smartphone belonging to the Medical Officer.
- **LOW-RAM / EDGE DEVICE CONSTRAINTS:** Extreme constraint. Devices operate on low-end mobile processors with severe memory limitations (2GB RAM, Android 10/11 Go edition). Web applications must be ultra-lean (< 1.5MB initial bundle), avoid heavy JavaScript frameworks, and execute zero heavy client-side machine learning.
- **LOCAL SERVER REQUIREMENTS:** Standalone ultra-low-power Local Clinic Server (e.g., Mini PC, repurposed low-cost laptop, or Raspberry Pi 4 with battery backup) broadcasting a local Wi-Fi hotspot within the PHC building. Enables all staff tablets to interact with the local Master Case database without external internet.
- **INTERNET DEPENDENCY:** Intermittent to completely absent. Cell towers frequently lose grid power during rural load-shedding, dropping data bandwidth to 2G or zero. Wireline broadband is virtually non-existent. **CLINOVA must operate with 100% offline autonomy.**
- **OFFLINE REQUIREMENTS:** Absolute requirement. Master Case creation, vernacular voice-to-text intake, vital signs logging, automated risk scoring, care feasibility checks, and printable referral slip generation must execute completely locally on the Local Clinic Server.
- **NETWORK FAILURE IMPACT:** Completely transparent to clinical operations. All clinical assessments and referral recommendations proceed uninterrupted; outbound records are staged in an encrypted local queue and synchronized to state servers when connectivity resumes.
- **POWER FAILURE IMPACT:** Severe everyday threat. Grid power is absent for 4 to 10 hours daily. Facility power depends on solar inverters or lead-acid battery backup systems. Systems must tolerate abrupt power cuts and boot instantaneously without database file corruption.
- **PAPER WORKFLOW DEPENDENCY:** High statutory dependence. Physical OPD slips, Maternal-Child Protection (MCP) cards, and tripartite referral slips are statutory legal records. CLINOVA must generate rapid printable/shareable digital passes that can be photographed or printed on a low-cost Bluetooth thermal printer.

---

## 9. Ergonomics, Language & Human Factors

- **LANGUAGE REQUIREMENTS:** Multilingual, vernacular-first architecture. All patient-facing narratives, ASHA-assisted intake screens, and printed care guidance must support regional languages (Odia, Hindi, Bengali, Marathi, Telugu, etc.). Audio intake must understand local colloquial expressions for pain, fever, bleeding, and breathlessness.
- **DIGITAL LITERACY:** Frontline ASHAs and elderly patients possess low digital literacy; ANMs and CHOs possess moderate mobile literacy; Medical Officers possess high smartphone literacy. User interfaces must prioritize tap-based visual cards, high-contrast visual cues, and speech recognition over keyboard typing.
- **ACCESSIBILITY REQUIREMENTS:** High-visibility color-coded acuity badges (Green, Yellow, Orange, Red), audible voice prompts in regional dialect, and large touch targets (minimum 48x48 dp) optimized for rapid thumb operation on cracked tablet screens.

---

## 10. Privacy, Security & Governance Mandates

- **PRIVACY RISKS:**
  - *Communal Consultation Spaces:* Rural consultation rooms lack acoustic isolation; family members and fellow villagers frequently crowd the examination space.
  - *Social Stigma:* Inadvertent disclosure of tuberculosis, leprosy, psychiatric illness, or sexually transmitted infections can result in severe social ostracization within the village.
  - *Shared Hardware:* Staff tablets are routinely shared without individual user logout, risking unauthorized record viewing.
- **SECURITY RISKS:** Physical theft of portable tablets; corruption of local storage via unverified USB drives; failure to patch Android OS vulnerabilities.
- **AUDIT REQUIREMENTS:** Strict compliance with Maternal Death Surveillance and Response (MDSR) and Child Death Review (CDR) statutory protocols. Every referral decision, dispatch timestamp, and emergency escalation must be immutably recorded to demonstrate appropriate standard of care by the solo Medical Officer.

---

## 11. Systemic Bottlenecks & Operational Failure Modes

- **OPERATIONAL BOTTLENECKS:**
  1. Administrative reporting burden: ANMs and CHOs spend up to 40% of their working hours manually copying the same clinical data into multiple disjoint government portals.
  2. Transport coordination friction: Protracted delays in reaching the 108 emergency dispatch centre via congested cellular lines.
- **CLINICAL BOTTLENECKS:**
  1. *Diagnostic Uncertainty Void ($U_t$):* Complete absence of laboratory analyzers and imaging creates profound epistemic uncertainty, forcing clinicians to make high-stakes referral decisions on physical signs alone.
  2. Solo clinician fatigue and isolation: Lack of peer consultation or specialist second opinions during complex emergencies.
- **REFERRAL BOTTLENECKS:**
  1. *The Blind Referral Tragedy:* Patients are dispatched to distant tertiary hospitals without knowing whether an ICU bed, operating theater, or specialist is available, leading to patients dying in transit or being turned away at the tertiary gate.
  2. Lack of clinical transfer documentation: Patients arrive at receiving hospitals with illegible slips, forcing duplicate triage and delayed resuscitation.
- **FOLLOW-UP BOTTLENECKS:** Total loss of longitudinal visibility once the patient departs the primary village catchment area.

---

## 12. CLINOVA Value Proposition & Hard Limitations

- **MOST IMPORTANT CLINOVA VALUE IN THIS ENVIRONMENT:**
  1. **Care Feasibility Matching via FACILITYGRAPH:** Instantly checks patient acuity requirements against local PHC stock and capabilities; if care is infeasible, it immediately triggers early referral navigation before the patient deteriorates into irreversible shock.
  2. **Vernacular Voice-Assisted Intake for Frontline ANMs/ASHAs:** Converts rural colloquial narratives into structured clinical triage summaries, allowing frontline workers to capture complete histories before the doctor consultation.
  3. **Intelligent, Capability-Matched Referral Slips:** Generates structured, tamper-evident digital referral passes matched against known regional hospital capabilities, eliminating blind transfers and closing the communication loop with receiving hospitals.
- **HARD LIMITATIONS OF CLINOVA IN THIS ENVIRONMENT:**
  - CLINOVA cannot pave rural roads or accelerate an ambulance stuck in monsoon mud.
  - CLINOVA cannot manufacture units of blood or replenish expired antivenom vials.
  - CLINOVA cannot perform emergency surgery in the absence of an operating theater and anesthesiologist.
