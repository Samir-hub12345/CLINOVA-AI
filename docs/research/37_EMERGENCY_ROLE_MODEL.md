# CLINOVA AI — Emergency & Acute Care Role Architecture

> **Document ID:** `RES-37`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Emergency Architecture & Acute Resuscitation Group  

---

## 1. Executive Summary & The Emergency Non-Equivalence Law

A foundational failure of conventional Electronic Health Records (EHR) is treating emergency care as simply a "routine outpatient encounter with high priority." In standard systems, an emergency room nurse or doctor is confronted with the exact same 40-field form, required dropdowns, and billing prompts, merely badged with a red "STAT" label.

> **The Emergency Non-Equivalence Law:**  
> An acute emergency resuscitation or emergent surgical presentation is **qualitatively distinct** from a routine clinical consultation.  
> When life, limb, or brain viability is in acute jeopardy (Golden Hour), every second diverted into navigating complex user interfaces directly increases patient morbidity and mortality.

CLINOVA AI establishes dedicated **Emergency Fast-Track** and **Operation Theatre (OT) Fast-Track** workflows (`DOC-16`). This document specifies the exact **role responsibilities, alert topologies, decision authorities, and information filtering boundaries** governing acute care operations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EMERGENCY ROLE & INTERACTION TOPOLOGY                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ INITIATION ] ──> Nurse / MO / Paramedic / System Rule                    │
│         │                                                                   │
│         ▼                                                                   │
│  [ ALERT BROADCAST ] ──> Casualty Team, Resuscitation Bay, OT Scrub Team   │
│         │                                                                   │
│         ▼                                                                   │
│  [ RAPID ABCD VITALS ] ──> Triage Nurse / Paramedic (30 Seconds)            │
│         │                                                                   │
│         ▼                                                                   │
│  [ CLINICAL DECISION ] ──> Emergency Medical Officer (Exclusive Lead)       │
│         │                                                                   │
│         ├──────────────────────────────┬─────────────────────────────┐      │
│         ▼                              ▼                             ▼      │
│  [ MEDICAL RESUSCITATION ]     [ SURGICAL OT PATH ]          [ EM TRANSFER ]│
│  Emergency Ward Admission      Surgeon / Anesthesia Sign     108 Dispatch   │
│  Lead: Casualty MO             Lead: Attending Surgeon       Lead: Ref Staff│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Emergency Role Distribution

### 2.1 Who Can INITIATE Emergency Mode?
Emergency mode can be activated via five distinct human and deterministic entry points:
1. **Frontline Triage Nurse (`ROLE_NURSE`):** Activates via physical presentation of acute distress (seizure, severe cyanosis, stridor, massive trauma).
2. **Casualty Medical Officer (`ROLE_CLINICIAN`):** Activates immediately upon bedside visual examination.
3. **Industrial Paramedic / Ambulance Crew (`ROLE_HEALTH_WORKER`):** Pre-notifies incoming facility while en route via mobile emergency fast-track toggle.
4. **Deterministic System Red-Flag Rule:** Automatically triggered if entered vitals cross critical physiological thresholds:
   - Systolic BP $< 90$ mmHg or Shock Index ($HR / SBP$) $> 1.0$ (`TRIAGE-R01`).
   - Pulse Oximetry SpO2 $< 90\%$ on room air (`TRIAGE-R02`).
   - Glasgow Coma Scale (GCS) $\le 8$ or AVPU = `U` (Unresponsive) (`TRIAGE-R03`).
   - Panic Lab Value (e.g., Platelets $< 20,000/\mu\text{L}$, Hemoglobin $< 5.0\text{ g/dL}$) (`TRIAGE-R04`).
5. **Patient / Attendant Waiting-Room Distress Call:** A high-contrast "Call Nurse Immediately" button on the waiting-room mobile portal alerts the triage desk to check on a deteriorating patient in the hall.

---

### 2.2 Who SEES Emergency Information & RECEIVES Alerts?
- **Casualty Resuscitation Bay:** Dedicated wall-mounted emergency monitor flashes high-contrast red banner with synthetic patient ID, chief crisis, and bed assignment.
- **Doctor Workstations:** All active physician terminals in Casualty/Emergency receive an instant audio alert and an un-dismissible top notification drawer.
- **Inpatient Ward / Step-Down Unit:** If admitted, receiving ward nursing station receives advance electronic notification with pre-arrival vitals.
- **Operation Theatre Scrub Station:** If routed to OT, anesthesiology and surgical nursing consoles receive the Procedure-Relevant Surgical Dossier.
- **Referral Desk:** If on-site capability fails (e.g., lack of emergency neurosurgeon), Transfer Staff receives instant capability deficit alert to begin 108 dispatch.

---

### 2.3 Who Collects Emergency Vitals?
- **Actor:** Triage Nurse, Industrial Paramedic, or Emergency Casualty GDA under nurse supervision.
- **Time Target:** Completed in **under 30 seconds**.
- **The Mandatory ABCD Acquisition Bundle:**
  - **A & B (Airway & Breathing):** Respiratory Rate, SpO2 percentage, supplemental oxygen flow (L/min).
  - **C (Circulation):** Heart Rate, Blood Pressure (automatic oscillometric or rapid manual), Shock Index calculation.
  - **D (Disability):** Rapid GCS or AVPU scale, capillary blood glucose (RBS) via fingerstick.
- **Constraint:** All non-vital fields (detailed history, family tree, insurance, address) are **strictly bypassed**.

---

### 2.4 Who Makes Clinical Decisions & Authorizes Dispositions?
- **Resuscitation Orders & Pharmacotherapy:** Exclusive authority of the licensed Emergency Medical Officer / Casualty Physician (`ROLE_CLINICIAN`).
- **Emergency Inpatient Ward Admission:** Authorized exclusively by the Emergency MO in coordination with the Inpatient Registrar.
- **Operation Theatre (OT) Fast-Track Pathway:** Authorized by the attending Surgeon and Anesthesiologist following completion of the **WHO Surgical Safety Checklist (Sign-In phase)**.
- **Inter-Facility Emergency Transfer:** Clinically authorized by the Emergency MO; logistically executed by the Referral Coordinator and 108 Ambulance Dispatcher.

---

## 3. Immediately Visible vs Deferred Information Matrix

Under acute resuscitation, cognitive overload kills. The interface strictly partitions data into **Immediate Mission-Critical Telemetry** versus **Deferred Documentation**:

| Mission-Critical IMMEDIATE Visibility (Surfaced in $< 1$ Second) | DEFERRED Documentation (Strictly Suppressed / Hidden) |
|:---|:---|
| • **ABCD Vitals:** SpO2, HR, BP, RR, Shock Index ($HR / SBP$). | • Detailed family medical history and non-critical pedigrees. |
| • **Conscious Level:** Glasgow Coma Scale (GCS) or AVPU status. | • Extended demographic questionnaires (employer, detailed address). |
| • **Acuity & Golden Hour:** Onset timestamp, elapsed time from injury. | • Non-acute outpatient complaints or mild chronic symptoms. |
| • **Critical Allergies & Warnings:** Penicillin, latex, contrast allergy. | • Historical childhood vaccination and immunization logs. |
| • **Blood Group & Cross-Match Status:** Units reserved in blood bank. | • Routine billing codes, insurance policy numbers, copay terms. |
| • **Active Red Flags & Panic Labs:** Active hemorrhage, severe acidosis. | • Extended lifestyle, dietary, and social history narratives. |
| • **Immediate Medications Administered:** Epinephrine, Aspirin, Atropine. | • Unverified differential diagnostic lists and AI reasoning drafts. |

---

## 4. Emergency Sub-Workflows & Decision Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TWO DEDICATED ACUTE PATHWAYS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PATHWAY A: MEDICAL EMERGENCY RESUSCITATION (Report Type 5)                 │
│  ├── Protocol: Sepsis Bundle / STEMI Bundle / Anaphylaxis / Trauma Resus   │
│  ├── Documentation: Single-Page High-Contrast High-Density Scan             │
│  ├── Disposition: Resuscitation Bay ──> High-Dependency Unit (HDU) / ICU    │
│  └── Sign-Off: Casualty Medical Officer                                     │
│                                                                             │
│  PATHWAY B: SURGICAL OPERATION THEATRE [OT] (Report Type 6)                 │
│  ├── Protocol: WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out)  │
│  ├── Documentation: Procedure-Relevant Surgical Dossier                     │
│  │   (Airway/Mallampati, NPO fasting hours, Platelets/INR, Blood units)     │
│  ├── Disposition: Casualty ──> OT Table ──> Post-Anesthesia Care Unit (PACU)│
│  └── Sign-Off: Operating Surgeon + Attending Anesthesiologist               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Medical Emergency Resuscitation Flow
- **Goal:** Rapid physiological stabilization within the "Golden Hour".
- **Role Interactions:**
  - Triage Nurse enters ABCD vitals and initiates oxygen.
  - Emergency MO opens Emergency Report (Report Type 5) and orders targeted bundle (e.g., Sepsis: 30 mL/kg IV crystalloids, STAT broad-spectrum antibiotics, blood cultures).
  - System recalculates CAREGRAPH trajectory slope ($\Delta R_t / \Delta t$) in real-time as repeat vitals are entered.

### 4.2 Surgical OT Fast-Track Flow
- **Goal:** Transfer acute surgical emergencies (ruptured ectopic, acute hemoperitoneum, open fracture) to the operating table without administrative blockage.
- **Information Filtering Rule:** The OT view strictly suppresses medical outpatient narrative and surfaces strictly surgical parameters:
  - Surgical Site Verification & Planned Procedure.
  - Airway & Aspiration Risk (NPO fasting duration, Mallampati score).
  - Hemostasis & Blood Bank Readiness (Hb, Platelets, PT/INR, Cross-matched units).
  - WHO Surgical Safety Checklist gates (Sign In before induction, Time Out before incision, Sign Out before skin closure).

---

## 5. Emergency Inter-Facility Referral Coordination

When an emergency presentation exceeds local institutional capacity (e.g., acute subdural hematoma presenting at a rural PHC lacking neurosurgery):

1. **Trigger:** FACILITYGRAPH declares `CURRENT_FACILITY_INSUFFICIENT` for required procedure (`NEUROSURGICAL_DECOMPRESSION`).
2. **Clinical Order:** Emergency MO confirms transfer requirement and signs clinical transfer order in $< 30$ seconds.
3. **Logistics Hand-Off:** Referral Coordinator receives immediate dispatch alert:
   - Selects nearest capable Level-1 Trauma Centre with confirmed open neuro-ICU bed.
   - Dispatches 108 Advanced Life Support (ALS) ambulance.
   - Pushes digital Emergency Transfer Pack to receiving hospital casualty desk.
4. **En-Route Continuity:** Paramedic logs serial en-route vitals on mobile terminal, ensuring receiving trauma team sees live trajectory upon arrival.
