# CLINOVA AI — Entry Routing & Dynamic Escalation Specification

> **Document ID:** `DOC-05`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Dual Entry Architecture

Every clinical encounter in CLINOVA AI begins with an explicit architectural decision:

$$\mathbf{NEW\ ENCOUNTER} \Longrightarrow \begin{cases} \mathbf{REGULAR\ /\ STANDARD\ INTAKE} & \text{(Comprehensive Multimodal Processing)} \\ \mathbf{EMERGENCY\ FAST-TRACK} & \text{(Immediate Resuscitation \& Critical Override)} \end{cases}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA ENCOUNTER ENTRY ROUTING                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                               NEW ENCOUNTER                                 │
│                                     │                                       │
│                    ┌────────────────┴────────────────┐                      │
│                    ▼                                 ▼                      │
│       [ 1. REGULAR / STANDARD ]            [ 2. EMERGENCY FAST-TRACK ]      │
│                    │                                 │                      │
│                    ▼                                 ▼                      │
│        Comprehensive Multimodal Intake     Immediate Red-Flag Triage        │
│        (Text, Voice, OCR, History)         Critical Vitals Check (30 sec)   │
│                    │                                 │                      │
│                    ▼                                 ▼                      │
│        Evidence Quality & Extraction       Emergency Bedside Doctor Call    │
│                    │                                 │                      │
│                    ▼                                 ▼                      │
│        Timeline & Missing Info Audit       Resuscitation / Emergency Ward   │
│                    │                                                        │
│                    │ ◄─── DYNAMIC MID-ENCOUNTER ESCALATION ───              │
│                    │      (Red Flag Discovered at Any Point)                │
│                    ▼                                                        │
│        Full CAREGRAPH Synthesis                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mode 1: Regular / Standard Intake

### 2.1 Criteria for Selection
- Patient is conscious, alert, with stable airway, breathing, and circulation.
- Absence of overt catastrophic physiological decompensation (e.g., massive external hemorrhage, active seizure, cardiac arrest, severe respiratory stridor).

### 2.2 Operational Flow
1. **Consent & Verification:** Digital or verbal consent captured; identity confirmed or synthetic anonymous tag issued.
2. **Multimodal Ingestion:** Patient or health worker submits symptoms via typed narrative, spoken voice recording, or uploaded document/photo.
3. **Automated PII Sanitization:** Immediate regex and NLP scrubbing of government IDs, phone numbers, and direct identifiers.
4. **Information Extraction & Entity Resolution:** Normalization of regional clinical descriptors (Odia/Hindi/English) into structured clinical parameters.
5. **Timeline Synthesis:** Chronological mapping of symptom onset, duration, peak severity, and prior self-medications.
6. **Missing-Information Audit:** Identification of critical clinical omissions (e.g., radiating pain, allergy history, fever duration).
7. **Interactive Follow-up Questions:** Targeted conversational prompts presented to the patient to reduce clinical uncertainty.
8. **Consolidation & CAREGRAPH Generation:** Synthesis of complete clinical state, risk classification, trajectory, and uncertainty metrics.

---

## 3. Mode 2: Emergency Fast-Track

### 3.1 Criteria for Selection (Immediate Triggers)
Any patient presenting with the following triggers bypasses the standard intake queue immediately:
- **Airway / Breathing:** Severe stridor, cyanosis, SpO2 < 88% on room air, respiratory rate > 35 or < 8 bpm, acute gasping.
- **Circulation / Hemodynamics:** Systolic BP < 80 mmHg, heart rate > 140 or < 40 bpm, cold clammy extremities with capillary refill > 3s, pulselessness.
- **Neurological:** Glasgow Coma Scale (GCS) < 9, sudden onset hemiparesis, active tonic-clonic seizure, acute altered sensorium.
- **Trauma / Catastrophe:** Massive uncontrolled hemorrhage, penetrative torso trauma, high-voltage electrical shock, major burn > 20% TBSA.
- **Syndromic Emergencies:** Acute severe crushing central chest pain with diaphoresis, acute anaphylaxis, snakebite with neurological or hematological toxicity.

### 3.2 Fast-Track Operational Flow
1. **Instant Master Case Creation:** System provisions a Master Case ID flagged with `ENCOUNTER_TYPE = EMERGENCY_CRITICAL` in < 200 milliseconds.
2. **Abbreviated 30-Second Vital Acquisition:** Nurse inputs only life-saving vitals (SpO2, Pulse, BP, GCS).
3. **Immediate Bedside Alert:** Real-time push alert sounds on the Doctor Workbench and triage station; patient appears at the pinned top of the Doctor Queue highlighted in flashing high-contrast amber/red.
4. **Emergency Checklist Activation:** System surfaces the targeted emergency resuscitation protocol (e.g., STEMI checklist, Sepsis bundle, Anaphylaxis pathway).
5. **Direct Ward / OT Routing:** Case routed directly to Emergency Resuscitation Bay or Operation Theatre.
6. **Post-Stabilization Reconciliation:** Full history and previous records are backfilled and attached to the existing Master Case only after physiological stabilization.

---

## 4. The Dynamic Escalation Invariant

### 4.1 Non-Trapped Patient Principle
> **Architectural Law:** A patient must NEVER become trapped inside a non-emergency workflow. Any regular encounter may dynamically escalate to an emergency encounter at any millisecond of the care journey.

```
REGULAR INTAKE STATE
  │
  ├── Patient uploads ECG showing STEMI ──────────────┐
  ├── Voice transcript reveals "sudden loss of speech" ──┼──> DYNAMIC ESCALATION
  ├── Nurse enters BP showing 70/40 mmHg ─────────────┤    Interrupts standard flow,
  └── Patient collapses in waiting room ──────────────┘    promotes case to Emergency Fast-Track
```

### 4.2 Dynamic Escalation Triggers
A regular encounter is immediately interrupted and promoted to Emergency status if:
1. **Extraction Trigger:** Text or voice transcription detects emergency keywords (`chest pain radiating to jaw`, `blood in vomitus`, `sudden blindness`, `toxic ingestion`).
2. **OCR Trigger:** Lab extraction returns panic values (e.g., Platelets < 20,000/μL, Potassium > 6.5 mmol/L, Troponin positive).
3. **Vital Entry Trigger:** Staff enters vitals meeting Modified Early Warning Score (MEWS) $\ge 5$ or shock index $> 1.0$.
4. **Clinician / Nurse Manual Escalation:** Frontline staff clicks the physical or UI "ESCALATE NOW" button at any stage.

### 4.3 Escalation State Transition
When dynamic escalation fires:
- The active UI screen displays an instant emergency banner.
- All non-critical questionnaire fields are instantly deferred.
- An immutable audit event `EVENT_DYNAMIC_ESCALATION` is committed to the Master Case.
- The case moves immediately to the Emergency Workbench without creating a new or duplicate patient record.
