# CLINOVA AI — Meaningful Human Control (MHC) & Anti-Automation Bias Model

> **Document ID:** `RES-35`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Human-AI Interaction Ergonomics Group  

---

## 1. Executive Summary & The Problem of "Fake HITL"

In digital healthcare, the phrase **"Human-in-the-Loop" (HITL)** is frequently reduced to a superficial cosmetic layer: a user interface presents an AI-generated diagnosis, and an exhausted physician clicks a single green "Approve AI" button to clear their screen.

Under the realities of Indian public hospitals—where a medical officer must examine 80 to 120 patients in a single morning shift (60–90 seconds per patient)—such superficial HITL models inevitably degrade into **systematic rubber-stamping**:
1. **Automation Bias:** Overloaded doctors uncritically trust plausible-sounding AI drafts.
2. **Alert Fatigue:** Clinicians reflexively dismiss pop-up warnings without reading them.
3. **Cognitive Anchoring:** An AI-generated differential diagnosis anchors the physician's thinking, causing them to overlook rare or atypical life-threatening conditions.

CLINOVA AI strictly rejects this paradigm. Grounded in the **WHO Ethics & Governance of AI for Health (2021)**, **IEEE 7001 Standards for Transparency of Autonomous Systems**, and the **ICMR Ethical Guidelines for AI in Healthcare (2023)**, this document specifies the architectural model for **Meaningful Human Control (MHC)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE 9 PILLARS OF MEANINGFUL HUMAN CONTROL                │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. VISIBILITY        │ Instant un-occluded access to raw source evidence   │
│  2. UNDERSTANDING     │ Explainable physiological trajectory & uncertainty  │
│  3. AUTHORITY         │ Exclusive medicolegal decision monopoly by clinician│
│  4. INTERVENE         │ Real-time ability to pause, pull, or freeze queues  │
│  5. MODIFY            │ Direct in-place editing of any clinical entity      │
│  6. REJECT            │ One-click complete dismissal of AI drafts           │
│  7. OVERRIDE          │ Unrestricted clinical override of AI recommendations│
│  8. REASON CAPTURE    │ Friction-calibrated capture of override rationale   │
│  9. AUDIT TRAIL       │ Tamper-evident cryptographic logging of all actions │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Nine Pillars of Meaningful Human Control

### Pillar 1: VISIBILITY (Evidence Provenance)
- **Requirement:** A clinician cannot exercise control over what they cannot inspect.
- **Specification:** Every discrete clinical fact extracted by the system (a symptom, vital sign, or lab result) stores an immutable foreign-key link to its raw source evidence.
- **Ergonomic Invariant:** Clicking any parameter in the Doctor Workbench opens a side inspection drawer in **under 300 milliseconds**, rendering:
  - The exact high-resolution cropped bounding box of the physical lab sheet (`OCR_SOURCE`).
  - The exact audio waveform and playback button starting at the relevant timecode (`AUDIO_SOURCE`).
  - The verbatim typed text snippet (`PATIENT_TEXT_SOURCE`).
  - The extraction confidence score ($[0.0, 1.0]$).
- **Anti-Black-Box Law:** No clinical fact may be displayed without its associated provenance tag.

---

### Pillar 2: UNDERSTANDING (Explainable Trajectory & Uncertainty)
- **Requirement:** Control requires comprehension. A raw percentage probability (e.g., *"78% Risk"*) creates false certainty.
- **Specification:** The system replaces opaque machine learning logits with clinically intuitive, transparent physiological signals:
  1. **Physiological Trajectory Slope ($\Delta R_t / \Delta t$):** Demonstrates whether a patient's NEWS2 / MEWS vital sign trend is `IMPROVING`, `STABLE`, `WORSENING`, or `CRITICAL`.
  2. **Epistemic Uncertainty Gauge ($U_t \in [0, 1]$):** Prominently highlights what the system *does not know*. If a critical vital sign is missing, $U_t$ escalates, triggering an amber warning card that explicitly names the missing parameter.
  3. **Deterministic Bounds:** All AI text generation is strictly subordinate to rule-based red flags (`TRIAGE-R01` to `TRIAGE-R06`). If systolic BP $< 90$ mmHg, the system forces shock escalation regardless of LLM confidence.

---

### Pillar 3: AUTHORITY (Medicolegal Sign-Off Monopoly)
- **Requirement:** The AI is strictly an **advisory scribe and care navigation assistant**; it is legally and architecturally incapable of clinical action.
- **Specification:**
  - The system contains zero APIs, triggers, or cron jobs that can execute autonomous patient discharge, prescribe pharmaceuticals, or dispatch a referral without a registered clinician's cryptographic sign-off.
  - Every finalized encounter requires a licensed practitioner's registration number (State Medical Council / NMC UID) appended to the digital signature.
  - The software prominently displays on all screens:
    > *"Educational Prototype & Triage Support System Only. Non-Diagnostic. All outputs are advisory and reviewer-facing."*

---

### Pillar 4: ABILITY TO INTERVENE (Queue & Process Control)
- **Requirement:** Clinicians must be able to interrupt automated processing at any time.
- **Specification:**
  - A clinician or triage nurse can instantly pause automated queue processing, pull any patient forward from the waiting room into the consultation suite, or trigger an immediate `CODE_RED_RESUSCITATION` bypass.
  - If a patient decompensates in the waiting room, entering updated vitals immediately forces a re-ranking event that bubbles the patient to the absolute top of the queue with an audible chime.

---

### Pillar 5: ABILITY TO MODIFY (In-Place Discrete Editing)
- **Requirement:** Clinicians must not be forced to accept an "all-or-nothing" AI package.
- **Specification:**
  - Every field in the synthesized Master Clinical Report is an in-place editable component.
  - If the AI extracted *"Heart Rate: 120 bpm"* due to an OCR smudge, but the true value on the slip is *"70 bpm"*, the doctor clicks the value, types `70`, and presses Enter.
  - The field immediately updates to `70`, changes its provenance tag to `CLINICIAN_VERIFIED`, and records the edit in the audit log.

---

### Pillar 6: ABILITY TO REJECT (One-Click Dismissal)
- **Requirement:** Clinicians must never be coerced into reviewing hallucinated or irrelevant AI text.
- **Specification:**
  - The draft AI triage note contains a prominent, high-contrast **"Discard Draft"** button.
  - Clicking this button immediately clears the AI draft, opening a blank, standard SOAP clinical note pad.
  - Discarding an AI draft does not trigger annoying confirmation traps or delay the consultation.

---

### Pillar 7: ABILITY TO OVERRIDE (Care Pathway Veto)
- **Requirement:** The physician's clinical judgment strictly supersedes any system recommendation.
- **Specification:**
  - When the Orchestration Engine recommends `INTER_FACILITY_REFERRAL` due to missing local surgical capacity, the examining surgeon can override and select `EMERGENCY_OT_ON_SITE` (e.g., if the surgeon has arrived on-site and can perform life-saving damage-control laparotomy).
  - The system immediately accepts the surgeon's disposition and switches to the OT fast-track workflow without obstruction.

---

### Pillar 8: REASON CAPTURE (Friction-Calibrated Justification)
- **Requirement:** Meaningful control requires accountability, but excessive friction induces workaround fatigue.
- **Specification:** When a clinician overrides an AI recommendation or alters a critical clinical parameter, the system captures the clinical rationale using **friction-calibrated modals**:
  - **Single-Click Structured Tags:** Standardized reasons selectable in $< 1$ second:
    - `MEASUREMENT_ERROR` (Incorrect device or reading)
    - `NEW_PHYSICAL_FINDING` (Finding observed on bedside examination)
    - `PATIENT_CLARIFIED` (Patient corrected history during consult)
    - `SPECIALIST_JUDGMENT` (Doctor overrides algorithmic rule based on clinical expertise)
    - `FACILITY_STATUS_CHANGED` (On-site capability available despite profile)
  - **Optional Free-Text Addendum:** A single-line box for additional clinical nuances.
- **Ergonomic Mandate:** Reason capture must never take longer than **3 seconds** to complete.

---

### Pillar 9: AUDIT TRAIL (Immutable Cryptographic Ledger)
- **Requirement:** All human interventions, modifications, and overrides must be permanently verifiable.
- **Specification:**
  - Every user action is recorded in an append-only audit ledger (`AuditLedgerEntry`).
  - Fields captured: `entry_id`, `case_id`, `actor_id`, `role`, `timestamp`, `action_type`, `field_modified`, `original_value`, `new_value`, `override_reason`, and `sha256_hash`.
  - The audit log is immutable: neither clinicians, facility admins, nor system admins can alter or delete past ledger records.

---

## 3. Cognitive Forcing Functions Against Rubber-Stamping

To defeat the dangerous habit of "blind clicking," CLINOVA incorporates targeted **cognitive forcing functions**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANTI-AUTOMATION BIAS ERGONOMIC CONTROLS                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. MANDATORY UNCERTAINTY VISUALIZATION                                     │
│     The sign-off button remains disabled until the clinician scrolls past   │
│     the highlighted amber Uncertainty Gap card.                             │
│                                                                             │
│  2. NO PRE-CHECKED "APPROVE ALL" BOXES                                      │
│     Interface never presents default-selected consent or verification boxes.│
│                                                                             │
│  3. HIGH-CONTRAST DIVERGENCE HIGHLIGHTING                                    │
│     When AI extraction conflicts with uploaded lab slips, both values are   │
│     rendered side-by-side with a flashing amber "CONFLICT" badge.           │
│                                                                             │
│  4. COLOR-CODED PROVENANCE CHIPS                                            │
│     Parameters are visually tagged:                                         │
│     [VOICE] Purple  |  [OCR] Blue  |  [STAFF] Green  |  [AI-DRAFT] Amber    │
│     Ensures doctor knows at a glance what has NOT been verified by a human. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Human Oversight Models for Non-Clinician Roles

Meaningful Human Control is not confined to physicians. Every role exercises agency over its assigned sphere:

| Role | Domain of Human Agency | Non-Automated Responsibility | Anti-Automation Guardrail |
|:---|:---|:---|:---|
| **Nurse / Health Worker** | Vital Signs Acquisition & Checklist Completion | Validates abnormal readings by repeating physical measurement. | System prevents submitting vitals outside human physiology without explicit re-test confirmation. |
| **Referral Staff** | Transfer Logistics & Bed Reservation | Verifies receiving hospital bed readiness via verbal phone call before dispatch. | System prevents ambulance dispatch status transition without recording receiver confirmation. |
| **Patient / Caregiver** | Self-Reported Symptoms & Consent | Freedom to describe symptoms in own vernacular words; can revoke consent. | Patient can correct misheard words in transcription before doctor consult. |
| **Facility Admin** | Institutional Capability Profile | Attests to operational bed, oxygen, and staffing counts. | System does not auto-infer physical bed availability without administrator sign-off. |
