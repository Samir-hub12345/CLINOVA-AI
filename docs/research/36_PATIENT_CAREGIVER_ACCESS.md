# CLINOVA AI — Patient & Caregiver Access, Boundary & Privacy Specification

> **Document ID:** `RES-36`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Patient Advocacy Research Group  

---

## 1. Executive Summary & Foundational Principles

In Indian healthcare, care-seeking is fundamentally a **family and community phenomenon**. Patients rarely navigate hospitals alone; they are almost universally accompanied by family attendants, spouses, adult children, or community health workers (ASHAs). Furthermore, a significant proportion of presenting patients face literacy or digital barriers, speak vernacular regional dialects (Odia, Hindi), or present in an acutely incapacitated state.

This document establishes the precise boundaries of **what patients and caregivers can provide, view, confirm, correct, receive, and acknowledge**, while strictly defining what clinical, operational, and algorithmic information **must remain restricted**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PATIENT & CAREGIVER ACCESS BOUNDARIES                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  PERMITTED PATIENT INTERACTIONS             RESTRICTED / CONCEALED DATA     │
│  ├── Provide symptom narratives & photos    ├── Internal differential diagnoses│
│  ├── View clinician-approved care summaries ├── Raw uncertainty metrics (U_t)│
│  ├── Confirm demographic & timeline facts   ├── Clinician private scratchpads │
│  ├── Correct self-reported draft errors     ├── Facility operational deficits │
│  ├── Receive vernacular medication slips   ├── Other patients' records       │
│  └── Acknowledge consent & warning signs    └── Unverified AI triage notes    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Six-Dimension Functional Matrix

| Dimension | Patient (`ROLE_PATIENT`) | Caregiver / Attendant (`ROLE_CAREGIVER`) |
|:---|:---|:---|
| **1. What They PROVIDE** | • Free-form spoken voice narrative in Odia/Hindi/English.<br>• Typed symptom descriptions and duration.<br>• Photographs of past paper prescriptions, lab reports, discharge cards.<br>• Responses to 1–3 multiple-choice clarification questions.<br>• Emergency contact details. | • Surrogate symptom history on behalf of patient.<br>• Observed timeline of acute changes (e.g., "seizure lasted 2 minutes").<br>• Known chronic medications, drug allergies, past surgeries.<br>• Attendant identity, contact number, and legal relationship to patient.<br>• Physical document uploads. |
| **2. What They VIEW** | • Dynamic digital queue token number and estimated wait status.<br>• Digital transcript of own spoken intake for confirmation.<br>• **Clinician-Approved Master Clinical Summary** (only *after* doctor sign-off).<br>• Prescribed medication list with dosage icons.<br>• Red-flag return warning signs in native language.<br>• Scheduled revisit appointment date and department location. | • Identical scope to patient view, provided valid surrogate authorization exists.<br>• Approved referral destination slip and travel instructions.<br>• Emergency pharmacy and diagnostic requisition slips. |
| **3. What They CONFIRM** | • Patient demographic identity (Name, Age, Gender, Village/Locality).<br>• Explicit digital/verbal consent for data processing (`B14`).<br>• Accuracy of symptom onset timeline (e.g., "Fever began 3 days ago"). | • Attendant identity and legal guardianship status.<br>• Surrogate consent for pediatric ($< 18$ years) or incapacitated patient.<br>• Patient's known baseline chronic medical conditions. |
| **4. What They CORRECT** | • Misspellings in self-entered demographic fields.<br>• Misheard or mis-transcribed words in draft voice intake transcript.<br>• Contact phone numbers and address.<br>• *Cannot alter clinician notes or verified vitals.* | • Inaccurate medication history or dosages provided during initial intake.<br>• Spelling of patient name or guardian contact details.<br>• *Cannot alter clinician notes or verified vitals.* |
| **5. What They RECEIVE** | • Vernacular, simplified Patient Care Summary Slip.<br>• Visual Medication Calendar (pictographic morning/noon/night icons).<br>• Red-Flag Warning Advisory ("Return immediately if you develop...").<br>• Referral Transfer Pack (if transferring to higher-tier hospital).<br>• Follow-up appointment SMS / WhatsApp confirmation. | • Physical/digital printout of Approved Discharge/Referral Pack.<br>• Transport guidance and receiving hospital directions.<br>• Home care and dietary instructions in plain regional language. |
| **6. What They ACKNOWLEDGE** | • Mandatory initial data processing and privacy consent (`B14`).<br>• Comprehension of prescribed medication instructions.<br>• Acknowledgment of scheduled revisit date.<br>• Formal signature if leaving Against Medical Advice (LAMA). | • Surrogate consent acknowledgment.<br>• Custody acknowledgment of patient during inter-facility transit.<br>• Acknowledgment of high-risk surgical consent in emergency OT. |

---

## 3. Strictly Restricted & Concealed Data Domains

To prevent severe clinical harm, anxiety, unguided self-treatment, and medicolegal disputes, the following domains are **strictly concealed** from patient and caregiver views:

### 3.1 Unverified Differential Diagnostic Rankings
- **Rationale:** Exposing an AI draft list of differential diagnoses (e.g., *"1. Malignancy (24%), 2. Tuberculosis (18%), 3. Reactive Lymphadenitis (58%)"*) directly to an anxious patient or family triggers acute psychological panic, online misinterpretation, and dangerous self-medication.
- **Enforcement Rule:** Differential diagnoses are strictly restricted to the `ROLE_CLINICIAN` workbench. The patient portal only displays the final, verified provisional diagnosis approved and communicated by the examining doctor.

### 3.2 Raw Epistemic Uncertainty Metrics ($U_t$)
- **Rationale:** Displaying mathematical scalars like *"Uncertainty: 0.68"* or raw Bayesian confidence scores has zero clinical utility for laypersons and undermines basic institutional trust.
- **Enforcement Rule:** $U_t$ is rendered exclusively on the Doctor Workbench. Patient interfaces translate uncertainty into simple, actionable clarification questions (`B08`).

### 3.3 Clinician Internal Scratchpads & Sensitive Notes
- **Rationale:** Physicians require a secure documentation zone to record provisional hunches, psychiatric observations, suspicions of domestic abuse or non-accidental trauma, and sensitive medicolegal notes that should not be released to family members without formal clinical counseling.
- **Enforcement Rule:** Internal clinician notes tagged `CONFIDENTIAL_CLINICAL_NOTE` are completely filtered out of patient-facing summaries.

### 3.4 Facility Operational & Resource Deficits
- **Rationale:** Exposing internal facility struggles (e.g., *"Oxygen plant pressure dropping"*, *"Staff shortage in Ward 3"*) induces public panic and waiting room agitation.
- **Enforcement Rule:** FACILITYGRAPH operational telemetry is restricted to `ROLE_CLINICIAN` and `ROLE_FACILITY_ADMIN`.

### 3.5 Other Patients' Records & Queue Identities
- **Rationale:** Patients waiting in high-density outpatient halls must not see names, diagnoses, or clinical details of other citizens.
- **Enforcement Rule:** Public display boards and mobile queue views show strictly anonymized token numbers (`Token #42`) and synthetic identifiers (`PT-91823`).

---

## 4. Caregiver Surrogacy & Legal Guardianship Protocols

In Indian clinical practice, caregiver surrogacy occurs across four distinct clinical archetypes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FOUR SURROGACY ARCHETYPES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. PEDIATRIC PATIENTS (< 18 Years)                                         │
│     Legal parent or documented guardian holds complete surrogate authority. │
│                                                                             │
│  2. UNCONSCIOUS / ACUTE TRAUMA PATIENTS                                     │
│     Emergency implied surrogate protocol; next-of-kin provides history.      │
│                                                                             │
│  3. GERIATRIC / COGNITIVELY IMPAIRED PATIENTS                               │
│     Documented primary family caregiver provides assisted history.          │
│                                                                             │
│  4. ILLITERATE / NON-DIGITAL PATIENTS                                       │
│     Patient is conscious but family attendant operates digital terminal.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Surrogate Authorization Gate
- **Rule:** A caregiver cannot access or submit records for an adult patient without documented authorization.
- **Mechanism:**
  - *Conscious Adult:* System prompts patient for verbal or digital confirmation to link caregiver account.
  - *Pediatric:* Parent enters name, Aadhaar/ABHA ID, and declares guardianship.
  - *Incapacitated Adult:* System tags the record `EMERGENCY_SURROGATE_OVERRIDE`, requiring attending clinician sign-off at the start of consultation.

### 4.2 Confidentiality Conflicts (The Sensitive Health Boundary)
- **Clinical Reality:** In conservative social environments, adult patients may wish to conceal sensitive health conditions (e.g., pregnancy, contraception, sexually transmitted infections, psychiatric treatment) from accompanying family members or in-laws.
- **Protection Architecture:**
  - When an adult patient enters the private consultation room, the examining doctor can activate `RESTRICT_CAREGIVER_ACCESS`.
  - This setting detaches the caregiver's portal access for that specific encounter, ensuring sensitive clinical summaries are delivered solely to the patient's personal device.

---

## 5. Vernacular Accessibility & Low-Literacy Design

To ensure genuine equity across rural and semi-urban populations in Odisha and wider India, patient and caregiver interfaces adhere to strict accessibility rules:

1. **Voice-First Audio Replay:** Every piece of post-consultation advice, medication instruction, and warning sign can be listened to via a single-tap audio speaker icon in spoken **Odia**, **Hindi**, or **English**.
2. **Pictographic Medication Calendars:** Dosages are represented using universal sun/moon icons:
   - ☀️ Morning (Before food / After food)
   - 🌤️ Afternoon
   - 🌙 Night
3. **High-Contrast Warning Signs:** Red-flag danger signs ("Return Immediately") are rendered in high-contrast red cards with universally recognizable warning symbols (e.g., chest pain icon, breathing difficulty icon, bleeding icon).
4. **Zero Technical Jargon:** Clinical terms are translated into plain vernacular phrases (e.g., *"High blood sugar"* instead of *"Hyperglycemia"*; *"Low platelets"* instead of *"Thrombocytopenia"*).
