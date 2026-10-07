# CLINOVA AI — Comprehensive User Journeys

> **Document ID:** `DOC-04`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Persona Overview

| Persona | Role | Primary Objective | Key Interface |
| :--- | :--- | :--- | :--- |
| **Dr. Ananya Sharma** | Medical Officer / ED Physician | Rapidly review complex patient trajectories, verify evidence, and authorize safest actions. | Clinician Reviewer Workstation |
| **Nurse Rajesh Patel** | Triage Nurse / Community Health Worker | Ingest multimodal patient narratives (voice/text/OCR), capture vitals, and prompt missing facts. | Multimodal Triage Intake Portal |
| **Pooja Das** | Referral & Care Navigation Officer | Identify nearest capable facility for transferring patients requiring specialized interventions. | Facility Navigation & Transfer Desk |
| **Dr. Sanjeev Mohanty** | Chief Medical Officer / Network Administrator | Monitor system-wide capacity, department bottlenecks, epidemiological surges, and AI audits. | SignalGraph & System Intelligence Dashboard |
| **Sunita & Caregiver** | Patient & Family Member | Provide symptoms in native language, grant informed consent, and receive clear safety guidance. | Patient Intake & Advisory Kiosk |

---

## 2. Journey 1: Medical Officer Clinical Review & Orchestration Sign-off

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINICIAN WORKSTATION FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Log into Clinova Secure Clinician Workspace                             │
│  2. Review Dynamic Prioritized Queue (sorted by Acuity + Waiting Time)      │
│  3. Select Patient Case: "SYN-PT-8821" (High Risk, Trajectory Deteriorating)│
│  4. Inspect CareGraph Synthesis:                                            │
│     - Timeline: Fever day 1 -> Chest pain day 3 -> Breathlessness today     │
│     - Vitals Trend: SpO2 dropped from 94% to 87% over 45 minutes            │
│     - Evidence Provenance: OCR ECG shows ST-elevation (Confidence: 96%)     │
│     - Uncertainty Flag: High Uncertainty (Troponin level missing)           │
│  5. Review Orchestration Engine Recommendation:                             │
│     - Safest Achievable Action: ESCALATE (Immediate Bedside Resuscitation) │
│     - Secondary Pathway: REFER to District Hospital (Cardiac ICU Feasible)  │
│  6. Clinical Decision Gate:                                                 │
│     - Option A: Accept Recommendation (One-click digital signature)        │
│     - Option B: Override Recommendation (Provide structured rationale)      │
│  7. Case state transitions from `CLINICIAN_REVIEW` -> `DECISION` -> `ACTION` │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Journey 2: Triage Nurse Multimodal Intake & Missing Information Resolution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TRIAGE INTAKE FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Open Multimodal Intake Form at triage desk                              │
│  2. Administer Informed Consent (Patient accepts via multi-language prompt) │
│  3. Input Patient Data:                                                     │
│     - Mode A: Speak in Hindi/Odia ("मरीज को 3 दिन से सीने में दर्द है...")   │
│     - Mode B: Type structured narrative in English                          │
│     - Mode C: Upload photo of handwritten referral slip                     │
│  4. System executes instant OCR & transcription:                            │
│     - Extracted entities parsed into draft CareGraph nodes                  │
│     - Direct PII automatically scrubbed; synthetic identifier assigned      │
│  5. System detects Missing Information:                                     │
│     - Red Flag Detected: Chest pain present                                 │
│     - Missing Parameter: Onset duration, Radiation to arm/jaw, Diaphoresis │
│  6. System presents Targeted Follow-up Questions to Nurse:                  │
│     - "Did the pain start suddenly, and does it radiate to the left arm?"   │
│  7. Nurse records patient response -> Uncertainty drops from 0.65 to 0.18    │
│  8. Case submitted to Priority Queue with deterministic risk tier           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Journey 3: Referral Coordinator Feasibility-Aware Navigation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CARE NAVIGATION & REFERRAL FLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Case receives clinician decision: `REFER` (Emergency Neuro-Surgical)    │
│  2. Referral Coordinator opens FacilityGraph Navigation View                │
│  3. System matches patient care bundle against regional facility network:   │
│     - Hospital A (12 km): Has CT, but Adult ICU beds are 100% full (INFEASIBLE)
│     - Hospital B (28 km): Has CT, 3 ICU beds, On-duty Neurosurgeon (FEASIBLE)│
│     - Hospital C (45 km): Tertiary Medical College, Full capacity           │
│  4. System recommends Hospital B as "Safest Achievable Destination"         │
│  5. Coordinator generates auto-populated SBAR Transfer Packet:              │
│     - Situation: Acute Ischemic Stroke with worsening GCS                   │
│     - Background: HTN, Symptom onset 110 minutes ago                        │
│     - Assessment: CareGraph trajectory steep, SpO2 stable on O2             │
│     - Recommendation: Immediate non-contrast CT on arrival, ICU bed reserved│
│  6. Receiving facility acknowledges transfer electronically                  │
│  7. Ambulance dispatched; Case state moves to `TRANSFER_PENDING`            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Journey 4: Hospital Administrator & Public Health Surveillance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SIGNALGRAPH TELEMETRY & AUDIT FLOW                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Administrator logs into Hospital Command Center                         │
│  2. Views SignalGraph Real-Time Network Heatmap:                            │
│     - Bottleneck Alert: District Hospital ED triage queue > 25 patients     │
│     - Surge Signal: 14 acute hemorrhagic fever cases detected in 48 hours   │
│       across Sub-District Facilities North & West                           │
│  3. System flags potential Dengue outbreak cluster (Confidence: 89%)        │
│  4. Administrator broadcasts resource re-allocation:                        │
│     - Dispatches additional platelet reserves to northern facilities        │
│     - Diverts routine ambulatory referrals to secondary satellite clinics   │
│  5. Review AI Audit Log:                                                    │
│     - Inspects override frequency (e.g., 94% clinician agreement rate)      │
│     - Validates zero PII leakage across external model calls                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Journey 5: Patient & Caregiver Respectful Interaction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PATIENT & CAREGIVER FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Patient approaches self-service triage terminal or triage assistant     │
│  2. Language selection: English, Hindi, Odia, Bengali                       │
│  3. Clear, non-technical Consent Disclosure presented:                      │
│     - "This system helps nurses and doctors prioritize your care."          │
│     - "It is an advisory assistant and does NOT make medical decisions."    │
│     - "A doctor will examine you directly."                                 │
│  4. Patient speaks symptoms naturally; audio recorded securely              │
│  5. Visual confirmation of understood symptoms shown on screen              │
│  6. Patient receives printed/digital queue token with wait time estimate    │
│  7. Safety advisory displayed: "If symptoms worsen suddenly, notify nurse"  │
└─────────────────────────────────────────────────────────────────────────────┘
```
