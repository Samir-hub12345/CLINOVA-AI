# CLINOVA AI — Target Environment Specification: Public Health Camp

> **Document ID:** `RES-46`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Environment Identification & Core Purpose

- **ENVIRONMENT ID:** `ENV_PUBLIC_CAMP`
- **ENVIRONMENT NAME:** Public Health Camp (Rural Outreach Screening Camp / Mega Health Camp / Pop-Up Tribal Mela Clinic)
- **PURPOSE:** Conducts high-throughput episodic mass screening, point-of-care chronic disease detection (hypertension, diabetes, anemia, cataract, oral/cervical cancer pre-screening), basic medication dispensing, and triage-to-referral navigation for remote and underserved populations lacking routine healthcare access.
- **TYPICAL LOCATION / CONTEXT:** Village school courtyards, community panchayat halls, religious temple premises, open-air tented canopies (*shamianas*), and mobile healthcare bus sites across rural and peri-urban India. Operates for 6 to 8 hours as an ad-hoc clinical setup characterized by extreme ambient heat, dust, crowd noise, and zero permanent institutional infrastructure.

---

## 2. Stakeholders & Patient Demographics

- **PRIMARY USERS:**
  - Volunteer & Deputed Medical Officers (`ROLE_CLINICIAN`): Visiting general physicians, postgraduate medical residents, and Ayush medical officers conducting rapid consultations.
  - Frontline Camp Triage Nurses & Nursing Students (`ROLE_NURSE`): Measuring vitals, administering capillary finger-prick tests, and operating screening stations.
  - Community Volunteers / NGO Workers (`ROLE_HEALTH_WORKER`): Managing queue flow, vernacular language translation, and registration assistance.
  - Registration Desk Volunteers (`ROLE_FACILITY_ADMIN` / Intake clerk): Issuing queue tokens and recording basic demographic markers.
- **SECONDARY USERS:**
  - Camp Coordinator / District Health Officer (`ROLE_FACILITY_ADMIN`): Overseeing camp logistics, drug stock quotas, and aggregate reporting.
  - Emergency Ambulance Liaison (`ROLE_REFERRAL_STAFF`): Coordinating on-call 108 ambulance transport for acutely decompensated attendees.
  - Rural beneficiaries and accompanying family members (`ROLE_PATIENT`, `ROLE_CAREGIVER`).
- **PATIENT / BENEFICIARY TYPES:** Economically marginalized rural villagers, agrarian daily-wage laborers, elderly community members with chronic undiagnosed symptoms, women with young infants, and individuals who rarely travel to formal public hospitals due to transport costs.
- **PATIENT VOLUME:**
  - Screening throughput: 300 to 1,000 beneficiaries within a single 6- to 8-hour operating window.
  - Triage station velocity: 40 to 120 patients processed per hour across multiple parallel stations.
- **EXPECTED WAITING PRESSURE:** Extreme throughput velocity. The time budget per attendee is strictly limited to 60 to 90 seconds at registration and vitals stations, and 2 to 3 minutes at the physician consultation desk. Lines of 100+ individuals routinely accumulate outside tents in direct sunlight, creating severe operational pressure.

---

## 3. Clinical Case Mix & Acuity Distribution

- **TYPICAL CASE TYPES:** Undiagnosed or poorly controlled essential hypertension, type 2 diabetes mellitus, severe nutritional iron-deficiency anemia, cataract and refractive visual deficits, chronic scabies and fungal dermatoses, osteoarthritic degenerative joint disease, pediatric undernutrition, chronic obstructive pulmonary symptoms, and incidental discovery of acute medical crises.
- **ROUTINE CASES:** Asymptomatic blood pressure screening, random blood glucose finger-prick testing, visual acuity card checks, distribution of standard 30-day generic medication packs (multivitamins, analgesics, antacids, metformin, amlodipine), and preventive lifestyle counseling.
- **URGENT CASES:** Asymptomatic malignant hypertension ($\text{BP} > 190/115\text{ mmHg}$), random blood glucose $> 450\text{ mg/dL}$ with ketonuria symptoms, profound clinical anemia ($\text{Hb} < 5.5\text{ g/dL}$ with exertional tachycardia), suspicious chronic oral leukoplakia or ulcerated breast lumps, and productive chronic cough with hemoptysis (suspected tuberculosis).
- **EMERGENCY CASES:** Acute ischemic chest pain (STEMI/NSTEMI discovered during triage), acute focal neurological deficits (evolving stroke), severe hypoglycemic disorientation or collapse during queue waiting, acute hypertensive crisis with pulmonary edema, and environmental heat exhaustion / heat stroke during summer camps.

---

## 4. Entry Pathways, Identity & Consent

- **ENTRY MODES:**
  1. *Perimeter Queue Gate:* Crowds entering through a single physical barrier where volunteers issue sequential physical tokens.
  2. *ASHA / Community Mobilizer Batches:* Groups of 10 to 30 villagers escorted by local ASHA workers from outlying hamlets.
  3. *Acute Walk-Up Presentation:* Acutely ill individuals bypassed directly to the doctor table by queue marshals.
- **REGISTRATION METHOD:** Rapid token-based entry. Sequential paper tokens with pre-printed numeric barcodes or QR codes are handed to attendees and affixed to a blank screening card. Demographics (Name, Age, Village, Phone) are rapidly logged via tablet voice input or quick single-line typing.
- **IDENTITY AVAILABILITY:** Exceptionally low. Attendees rarely carry physical Aadhaar cards to open-air camps. Registration must tolerate missing national identity documents, utilizing temporary Camp Identifier tokens linked to mobile numbers or village names.
- **CONSENT CONTEXT:** Implied collective consent for community health screening; express verbal consent for capillary blood draws. Transparent explanation required prior to digital image capture of skin lesions or oral cavity screening.

---

## 5. Staffing Ratios & Clinician Availability

- **AVAILABLE STAFF:**
  - 2 to 4 Volunteer / Deputed Medical Officers.
  - 4 to 8 Staff Nurses / Nursing Interns across vitals, glucose, and eye-testing stations.
  - 6 to 12 Community Volunteers managing intake lines and crowd flow.
  - 1 to 2 Pharmacists running the generic dispensing table.
- **CLINICIAN AVAILABILITY:** Concentrated strictly within the active camp hours (e.g., 09:30 to 16:30). Doctors experience severe cognitive fatigue after conducting 120 to 180 rapid back-to-back consultations.
- **NURSING / HEALTH-WORKER AVAILABILITY:** High numerical staffing, but high variance in clinical experience (frequently composed of rotating student volunteers).
- **SPECIALIST AVAILABILITY:** Episodic and theme-dependent. Eye specialists (ophthalmologists / optometrists), dentists, or gynecologists may be present if the camp is co-sponsored for specialized screening; general medical specialists are rarely available.

---

## 6. Diagnostic, Procedural & Infrastructure Capabilities

- **DIAGNOSTIC CAPABILITY:** Strictly limited to portable, battery-powered point-of-care rapid testing (POCT).
- **LAB CAPABILITY:** Battery-operated digital glucometers, digital hemoglobinometers, multi-parameter urine reagent test strips (glucose, protein, ketones), rapid lateral-flow test cassettes (Malaria, Dengue, HIV, Hepatitis B/C). Zero automated hematology, zero biochemistry, zero wet lab infrastructure.
- **IMAGING CAPABILITY:** Zero on-site imaging, unless a specialized mobile radiography/mammography screening van with an on-board diesel generator is co-deployed at the perimeter.
- **MEDICATION / PHARMACY CONTEXT:** Pre-assembled camp emergency and chronic dispensing kit. Dispenses 15- to 30-day blister packs of essential oral generic drugs (amlodipine, atenolol, metformin, glimepiride, paracetamol, cetirizine, albendazole, omeprazole, ORS). Popular antihypertensive and antidiabetic drugs frequently run completely out of stock 2 to 3 hours before camp conclusion.
- **BED / OBSERVATION CAPACITY:** Absolute zero. 1 to 2 canvas folding cots or shaded wooden benches set aside under a tree or tent flap for vasovagal episodes, post-fingerprick dizziness, or heat exhaustion.
- **OT / PROCEDURE CAPABILITY:** Completely absent. Strictly non-invasive clinical evaluation and screening.
- **EMERGENCY CAPABILITY:** Elementary emergency stabilization only. Compact first-aid kit, sublingual nitroglycerin tablets, dispersible aspirin (325 mg), clopidogrel (300 mg), oral glucose gel, 25% IV dextrose vials, and 1 portable D-type oxygen cylinder with mask (if arranged by organizers). On-call reliance on local 108 ambulance dispatch.

---

## 7. Referral, Transport & Outcome Linkages

- **REFERRAL CAPABILITY:** The fundamental raison d'être of the screening camp. 15% to 35% of all screened participants are identified as requiring formal clinical referral to primary health centres, community health centres, or district specialty hospitals for confirmatory laboratory workup, surgical intervention (cataract extraction), or continuous chronic disease management.
- **TRANSPORT / TRANSFER CONTEXT:** Attendees arrive and depart on foot, bicycles, or tractor-trailers. For acute emergency detections (e.g., STEMI, malignant hypertension with altered sensorium), transport requires emergency 108 dispatch or organizing immediate private transport to the nearest secondary hospital.
- **FOLLOW-UP CAPABILITY:** The historic point of failure for public outreach camps. Once camp infrastructure is dismantled at 17:00, visiting medical teams depart. Historically, $> 85\%$ of camp referrals are lost to follow-up because no local clinical node is formally notified.
- **OUTCOME DATA AVAILABILITY:** Zero longitudinal feedback. Traditional camp records capture only aggregate counts of total persons screened and total drug strips dispensed for sponsor reporting; whether referred patients ever received definitive hospital care is completely unknown.

---

## 8. Digital Infrastructure, Hardware & Connectivity Constraints

- **DIGITAL MATURITY:** Primitive / Ad-hoc. Paper registers, printed physical screening tokens, and carbon-copy referral slips remain the operational default. Digital systems are rejected unless they operate faster than pen and paper.
- **DEVICE AVAILABILITY:** Battery-powered mobile hardware: 3 to 6 Android tablets (2GB–4GB RAM), personal smartphones of volunteers, and 1 to 2 battery-operated laptops. Portable battery-operated Bluetooth thermal receipt printers used for issuing referral passes.
- **LOW-RAM / EDGE DEVICE CONSTRAINTS:** Severe. Hardware must operate continuously on internal batteries or external power banks in high ambient temperatures (up to 42°C). Applications must impose minimal CPU/RAM load to avoid thermal throttling and rapid battery drain.
- **LOCAL SERVER REQUIREMENTS:** Standalone battery-powered Local Camp Server (e.g., laptop or Mini PC running on a 12V DC power bank) broadcasting a self-contained local Wi-Fi network across the tents. Enables all screening station tablets to write to the common camp database without external internet.
- **INTERNET DEPENDENCY:** Completely zero. Cellular 4G signals in rural village spaces are notoriously unstable, congested, or non-existent inside tin-roofed school buildings. **CLINOVA must operate 100% offline.**
- **OFFLINE REQUIREMENTS:** Absolute requirement. All core operations—rapid token issuance, vitals recording, point-of-care lab logging, risk grouping (Green, Yellow, Red), doctor note capture, and thermal referral pass printing—must execute locally without a single outbound internet packet.
- **NETWORK FAILURE IMPACT:** Zero clinical disruption. The local ad-hoc Wi-Fi mesh synchronizes all station tablets with the Local Camp Server. When the camp team returns to base with broadband, the server executes bulk cryptographic synchronization to the state cloud registry.
- **POWER FAILURE IMPACT:** Severe operational hazard. Rural grid power is erratic or unavailable. All digital gear must be fully charged prior to departure and backed by 20,000 mAh power banks.
- **PAPER WORKFLOW DEPENDENCY:** High practical requirement. Attendees physically carry their paper screening card from station to station. CLINOVA bridges this by printing instant 58mm thermal receipts containing the Master Case QR code and summarized findings.

---

## 9. Ergonomics, Language & Human Factors

- **LANGUAGE REQUIREMENTS:** Multilingual vernacular-only for attendees. Audio intake prompts, conversational symptom capture, and printed thermal referral slips must be presented in the regional language (Odia, Hindi, Marathi, etc.) with zero medical jargon.
- **DIGITAL LITERACY:** Camp attendees exhibit low to zero digital literacy. Triage station volunteers possess basic mobile literacy. User interfaces must eliminate text typing entirely, utilizing oversized visual buttons, color badges, and voice dictation.
- **ACCESSIBILITY REQUIREMENTS:** Sunlight-readable high-contrast UI modes for outdoor tents; audio chime notifications for queue advancement; clear color-coded acuity flags (Green = Normal, Yellow = Borderline, Red = High-Risk Urgent Referral).

---

## 10. Privacy, Security & Governance Mandates

- **PRIVACY RISKS:**
  - *Public Screening Areas:* Screenings conducted in open school rooms or under canopies where bystanders hear all medical disclosures.
  - *Community Stigma:* High risk of gossip if a neighbor overhears an attendee being flagged for chronic infectious disease, mental health symptoms, or reproductive health issues.
  - *Discarded Paper Slips:* Attendees discarding paper slips containing medical information in open fields.
- **SECURITY RISKS:** Physical vulnerability and theft of portable tablets in chaotic, crowded tents; loss of USB flash drives containing offline camp databases.
- **AUDIT REQUIREMENTS:** Compliance with corporate social responsibility (CSR) and National Health Mission (NHM) outreach audit guidelines. Must provide immutable aggregated proof of screening counts, disease detection yields, and formal referral handoffs without exposing identifiable patient health records.

---

## 11. Systemic Bottlenecks & Operational Failure Modes

- **OPERATIONAL BOTTLENECKS:**
  1. Queuing bottlenecks at the point-of-care glucose/BP testing tables, where manual finger-prick testing takes 90 seconds per person, causing upstream queue stalls.
  2. Severe logjams at the physician consultation desk, where 2 doctors must review 500 attendees in 5 hours.
  3. Chaotic pharmacy dispensing bottlenecks as crowds attempt to collect free medicine packs simultaneously.
- **CLINICAL BOTTLENECKS:**
  1. *The 60-Second Consultation Danger:* Under intense crowd pressure, volunteer doctors risk missing life-threatening occult presentations (e.g., severe hypertensive crises or asymptomatic severe anemia).
  2. Inability to conduct confirmatory secondary laboratory workup on-site.
- **REFERRAL BOTTLENECKS:**
  1. *The Camp Referral Black Hole:* Attendees handed loose paper slips that are discarded or misunderstood; zero notification sent to the receiving primary health centre.
  2. Economic barriers: Attendees cannot afford transport to the distant referral hospital.
- **FOLLOW-UP BOTTLENECKS:** Complete severance of communication once the camp vehicle drives away at the end of the day.

---

## 12. CLINOVA Value Proposition & Hard Limitations

- **MOST IMPORTANT CLINOVA VALUE IN THIS ENVIRONMENT:**
  1. **High-Throughput 3-Tier Risk Stratification:** Rapidly classifies attendees into Green (Normative / Self-Care), Yellow (Borderline Chronic / Lifestyle Counseling), and Red (High-Risk Urgent Referral) in under 45 seconds, ensuring doctors review critical cases first.
  2. **Zero-Internet Local Mesh Deployment:** Operates entirely on battery power and local Wi-Fi, allowing 6 screening tablets to work in perfect synchronization inside an off-grid rural tent.
  3. **Structured Digital Referral Handshake:** Generates structured referral passes tied to the local PHC/CHC network and sends SMS/ABHA notifications to village ASHA workers, converting an isolated outreach camp into a connected gateway to continuous care.
- **HARD LIMITATIONS OF CLINOVA IN THIS ENVIRONMENT:**
  - CLINOVA cannot speed up the biochemical reaction time of a physical glucometer test strip.
  - CLINOVA cannot manufacture more tablets of amlodipine when the camp drug box runs empty.
  - CLINOVA cannot force an impoverished patient to pay for bus fare to a referral hospital.
