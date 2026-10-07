# CLINOVA AI — Clinical Reporting Architecture & Purpose-Specific Report Models

> **Document ID:** `DOC-14`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Reporting Philosophy & Design Principles

> **Core Architectural Law:** All reports are dynamically generated, purpose-specific views rooted in the single **Master Case**.
>
> Reports must never become disconnected secondary data silos. In addition, reports must adhere to the **Anti-Wall-of-Text Law**:
> - Never output one massive, undifferentiated AI text block.
> - Structure content hierarchically into discrete clinical panels.
> - Prominently display source provenance, timestamps, and verification badges.
> - Explicitly mark AI-assisted content vs. clinician-verified observations.
> - Ensure all reports support three native operational actions: **VIEW**, **DOWNLOAD (PDF)**, and **PRINT (Optimized Thermal/A4 CSS)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MASTER CASE REPORT DERIVATIONS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                            MASTER CASE RECORD                               │
│                         `case_id`: UUID (Single Source)                     │
│                                     │                                       │
│          ┌──────────────────────────┼──────────────────────────┐            │
│          ▼                          ▼                          ▼            │
│  [ REPORT TYPE 1 ]          [ REPORT TYPE 2 ]          [ REPORT TYPE 3 ]    │
│  Comprehensive Clinical /   Staff & Vitals             Routine / Outpatient │
│  Triage Master Report       Addendum Slip              Follow-up Report     │
│                                                                             │
│          ┌──────────────────────────┼──────────────────────────┐            │
│          ▼                          ▼                          ▼            │
│  [ REPORT TYPE 4 ]          [ REPORT TYPE 5 ]          [ REPORT TYPE 6 ]    │
│  Inpatient Ward Admission   Emergency Fast-Track       Operation Theatre    │
│  & Handoff Report           Resuscitation Pack         (OT) Surgical Pack   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six Purpose-Specific Report Specifications

### 2.1 Report Type 1: Comprehensive Clinical / Triage Master Report
- **Target Audience:** Medical Officers, Senior Consultants, Clinical Quality Auditors.
- **Operational Purpose:** The definitive, exhaustive medicolegal record of the complete triage encounter.
- **Mandatory Sections:**
  1. Header: Facility metadata, timestamp, synthetic patient ID, age, gender, language.
  2. Intake Provenance Summary: Source modalities (voice, OCR, text) with confidence indicators.
  3. Chief Complaint & Extracted Symptom Matrix: Structured clinical terms, onset, duration, radiation.
  4. Longitudinal Timeline: Chronological sequence of onset, prior medications, and triage milestones.
  5. Objective Observations: Serial vitals table (BP, HR, SpO2, RR, Temp, GCS) with verification badges.
  6. Point-of-Care & Lab Extractions: CBC panels, urine, rapid antigen tests with source image snippets.
  7. CAREGRAPH Synthesis: Current syndrome, risk band, trajectory arrow, uncertainty breakdown.
  8. Missing Information & Contradiction Audit: Explicit record of unresolved gaps.
  9. Orchestration Advisory & Feasibility Context: Recommended safest achievable pathway.
  10. Clinician Verification & Decision Section: Signed verification audit log, modifications, final orders.

### 2.2 Report Type 2: Staff & Vitals Addendum Slip
- **Target Audience:** Frontline Triage Nurses, ANMs, ASHA workers.
- **Operational Purpose:** Rapid point-of-care receipt capturing newly acquired vitals and missing-data checklist responses.
- **Mandatory Sections:**
  - Case ID & Patient Anonymized Identifier.
  - Timestamp of measurement.
  - Acquired Vitals Table with physiological normal ranges and highlighted abnormal values.
  - Mandatory Triage Checklist responses (Chest pain, breathlessness, altered sensorium flags).
  - Staff Member Name and ID.
  - Linked Master Case QR code for instant workstation scanning.

### 2.3 Report Type 3: Routine / Outpatient Follow-Up Report
- **Target Audience:** Patient, Caregiver, Primary Care Clinician.
- **Operational Purpose:** Patient-accessible take-home summary for routine home care and scheduled revisits.
- **Mandatory Sections:**
  - Patient-Friendly Clinical Summary: Vernacular language translation (Odia/Hindi/English) explaining home care in non-technical terms.
  - Doctor-Approved Instructions: Activity restrictions, hydration, warning signs.
  - Follow-up Appointment Schedule: Date, time, clinic room, and attending medical officer.
  - Emergency Return Warnings: Explicit list of danger signs requiring immediate emergency return.
  - *Redaction Rule:* Internal differential diagnoses, model thinking tokens, and raw risk heuristics are strictly omitted.

### 2.4 Report Type 4: Inpatient Ward Admission & Handoff Report
- **Target Audience:** Inpatient Ward Nursing Staff, Admitting Ward Physician.
- **Operational Purpose:** Structured SBAR (Situation, Background, Assessment, Recommendation) handoff for ward transfer.
- **Mandatory Sections:**
  - Situation: Reason for admission, admitting service (Internal Medicine, Pediatrics, etc.), assigned bed.
  - Background: Comorbidities, chronic medications, known drug allergies.
  - Assessment: Triage trajectory, baseline vitals, abnormal lab parameters.
  - Recommendation & Initial Orders: IV fluids, oxygen titration targets, medication initiation, vital frequency (e.g., q2h).
  - Formal Two-Party Sign-off: Digital acknowledgment by transferring triage doctor and receiving ward nurse.

### 2.5 Report Type 5: Emergency Fast-Track Resuscitation Pack
- **Target Audience:** Emergency Resuscitation Team, Trauma Surgeon, ICU Registrar.
- **Operational Purpose:** Ultra-concise, high-contrast, 1-page emergency summary designed for instant scanning under acute resuscitation conditions (< 15 seconds reading time).
- **Mandatory Sections:**
  - High-Contrast Red Flag Banner: Prominently displays primary life threat (e.g., *MASSIVE UPPER GI BLEED / HEMODYNAMIC SHOCK*).
  - Critical Vitals: SBP/DBP, HR, SpO2, GCS, Shock Index.
  - Key Presentation & Onset Window: Time of last known well (golden-hour tracker).
  - Stat Lab & Panic Findings: Rapid blood sugar, Bedside ECG rhythm, Troponin status, Blood type.
  - Known Allergies & Anti-Coagulation Status: High-contrast callout for blood-thinners / penicillin.
  - Resuscitation Interventions Administered: IV access gauge, fluids bolused, oxygen delivery method.

### 2.6 Report Type 6: Operation Theatre (OT) Surgical Pack
- **Target Audience:** Consultant Surgeon, Anesthesiologist, OT Scrub/Circulating Nurse.
- **Operational Purpose:** Procedure-specific pre-operative safety checklist complying with the WHO Surgical Safety Checklist.
- **Mandatory Sections:**
  - Patient Identity & Procedure Verification: Anonymized ID, planned surgical procedure, surgical site marking.
  - Anesthesia Risk Profile: Mallampati score, NPO status (hours since last oral intake), loose teeth/airway notes.
  - Pre-Op Investigations: Hemoglobin, Platelets, PT/INR, Serum Electrolytes, Cross-matched blood units reserved.
  - Medication & Infection Control: Pre-op antibiotic prophylaxis timing, antiplatelet cessation window.
  - Required Special Equipment: Laparoscopy tower, C-arm fluoroscopy, specific graft/mesh availability.

---

## 3. Formatting & Print Layout Standards

1. **Standard Print CSS:** Clean, monochrome-optimized print stylesheets ensuring perfect formatting on standard A4 paper and 80mm thermal receipt printers without visual clipping.
2. **AI Disclaimer Stamp:** Every report bears the non-negotiable legal footer:
   > *"CLINOVA AI is a clinical care intelligence decision support platform for triage and navigation assistance. This report is strictly advisory, non-diagnostic, and human-in-the-loop. All clinical parameters and care dispositions are reviewed and finalized by a licensed healthcare professional."*
3. **Traceability Barcode / QR Code:** Every report includes a secure verification QR code linking directly to the encrypted Master Case record in the hospital system.
