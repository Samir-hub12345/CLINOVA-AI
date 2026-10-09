# CLINOVA AI — Manual Entry Provenance & Human Attribution Model

> **Document ID:** `RES-112`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Human Attribution Principle

In clinical environments, humans are both the primary collectors and the primary consumers of clinical data. However, human data entry is neither monolithic nor inherently error-free:
- A patient typing on a waiting room kiosk may misunderstand medical terminology (e.g., mistaking gastroesophageal reflux for an acute heart attack).
- An overburdened triage nurse typing under severe time pressure may commit a numerical transposition typo (e.g. entering pulse `132` as `231`).
- A registration clerk may accidentally enter demographic information under an existing homonymous patient profile.
- A junior resident doctor may document an initial tentative clinical hypothesis that changes after senior consultant review.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL MANUAL ENTRY SAFETY INVARIANT                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│         MANUALLY ENTERED DATA IS NEVER AUTOMATICALLY VERIFIED.              │
│                                                                             │
│   Human entry creates an immutable audit trail of ATTRIBUTION, not an       │
│   unconditional guarantee of truth. Every manual entry must record the      │
│   identity, role, device, and clinical context of the actor, and be         │
│   assigned an epistemic state proportional to the actor's legal scope.      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six Canonical Manual Entry Actor Roles

Every manual entry in CLINOVA AI is bound to an authenticated user whose operational role dictates the default epistemic classification and downstream clinical permissions:

| Actor Role | Operational Setting | Captured Data Types | Default Epistemic Status | Statutory Authority (NMC / Clinical) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Patient** | Mobile App / Intake Kiosk | Presenting symptoms, pain score, known allergies, current pills | `PATIENT_REPORTED` / `KNOWN` | Self-report only; cannot enter physical signs or lab values. |
| **2. Caregiver** | Rural Tablet / Kiosk | Pediatric symptoms, elderly history, observed seizures | `PATIENT_REPORTED` / `KNOWN` | Proxy report; relationship to patient explicitly recorded. |
| **3. Community Health Worker (ASHA / ANM)**| Sub-Centre / Village Camp | Rapid blood glucose, urine dipstick, basic pulse, weight | `STAFF_ENTERED` / `KNOWN` | Point-of-care screening; cannot prescribe or authorize care. |
| **4. Staff Nurse / Paramedic** | Triage Desk / Inpatient Ward / Ambulance | Full vital signs (BP, SpO2, HR, RR), GCS/AVPU, nursing notes | `STAFF_ENTERED` / `KNOWN` | Licensed clinical measurement; triggers emergency escalation. |
| **5. Clinician (RMP)** | Doctor Workbench / Consultation Room | Physical exam findings, differential diagnosis, orders | `CLINICIAN_VERIFIED` / `VERIFIED` | Full medical monopoly (NMC Reg 27); legally binding orders. |
| **6. Facility Administrator**| Admission / Billing Desk / MRD Desk | Bed assignment, insurance eligibility, medico-legal status | Administrative metadata only | Non-clinical; strictly prohibited from altering clinical facts. |

---

## 3. Mandatory Contextual Attribution Metadata

Every manual entry event captures six invariant attribution vectors:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MANUAL ENTRY ATTRIBUTION VECTORS                        │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Actor Identity    │ UUID, Authenticated Username, Full Legal Name        │
│ 2. Professional Role │ Enum: PATIENT, CAREGIVER, ASHA, NURSE, RMP, ADMIN    │
│ 3. Statutory Reg #   │ Medical/Nursing Council Reg # (for RMP and Nurses)   │
│ 4. Session & Device  │ Device Hardware ID, IP Address, Client App Version   │
│ 5. Temporal Markers  │ Event Timestamp (when observed) vs Recorded Timestamp│
│ 6. Justification     │ Clinical rationale (mandatory for edits/corrections) │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 4. Retrospective Entry and Clinical Correction Governance

In acute emergency settings, documentation frequently lags behind physical patient care. A resuscitation team may administer IV fluids, push adrenaline, and perform cardiopulmonary resuscitation (CPR) for 20 minutes before a nurse or physician sits down at a workstation to log the event.

To maintain medicolegal admissibility under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (formerly Section 65B of the Indian Evidence Act):
1. **Separation of Clocks:** The system strictly decouples `event_time` (when the drug was injected) from `recorded_at` (when the computer key was pressed).
2. **Retrospective Flagging:** Any entry where $(\text{recorded\_at} - \text{event\_time}) > 15\text{ minutes}$ is automatically flagged as `IS_RETROSPECTIVE_ENTRY = TRUE`.
3. **Mandatory Clinical Justification:** When a clinician edits, amends, or overrides an existing value, a structured reason must be selected:
   - `TYPOGRAPHICAL_ERROR_CORRECTION`
   - `SUBSEQUENT_CLINICAL_REEVALUATION`
   - `EQUIPMENT_RECALIBRATION`
   - `LATE_DIAGNOSTIC_REPORT_CORRELATION`
4. **Non-Destructive Amendment:** The original entry is NEVER overwritten in place. The database stores the original record, creates a new record, and writes an immutable row into `evidence_modification_events`.

---

## 5. Manual Entry Relational Schema

```sql
CREATE TABLE manual_entry_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evidence_record_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    actor_role VARCHAR(32) NOT NULL CHECK (actor_role IN (
        'PATIENT', 'CAREGIVER', 'ASHA_ANM', 'STAFF_NURSE', 'PARAMEDIC', 
        'RESIDENT_DOCTOR', 'CONSULTANT_RMP', 'FACILITY_ADMINISTRATOR'
    )),
    nmr_registration_number VARCHAR(64), -- Required if role IN ('RESIDENT_DOCTOR', 'CONSULTANT_RMP')
    
    device_id VARCHAR(64) NOT NULL,
    client_ip_address VARCHAR(45) NOT NULL,
    session_token_hash CHAR(64) NOT NULL,
    client_app_version VARCHAR(32) NOT NULL,
    
    event_timestamp TIMESTAMPTZ NOT NULL,   -- When the physiological event physically occurred
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- When the data was submitted
    is_retrospective BOOLEAN NOT NULL DEFAULT FALSE,
    retrospective_lag_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (recorded_at - event_timestamp)) / 60
    ) STORED,
    
    entry_action VARCHAR(16) NOT NULL DEFAULT 'INSERT' CHECK (entry_action IN (
        'INSERT', 'AMEND', 'OVERRIDE', 'RETRACT'
    )),
    justification_category VARCHAR(64) CHECK (justification_category IS NULL OR justification_category IN (
        'INITIAL_DOCUMENTATION', 'TYPOGRAPHICAL_ERROR_CORRECTION', 
        'SUBSEQUENT_CLINICAL_REEVALUATION', 'EQUIPMENT_RECALIBRATION',
        'EMERGENCY_RETROSPECTIVE_ENTRY', 'CLINICAL_DISAGREEMENT'
    )),
    justification_narrative TEXT
);

CREATE INDEX ix_manual_log_case ON manual_entry_audit_logs(case_id);
CREATE INDEX ix_manual_log_actor ON manual_entry_audit_logs(actor_id);
CREATE INDEX ix_manual_log_evidence ON manual_entry_audit_logs(evidence_record_id);
```

---

## 6. Verification Status of Manual Data

To avoid false safety assumptions:
- Manual patient entries remain `PATIENT_REPORTED` / `UNVERIFIED` until reviewed by clinical staff.
- Manual nursing measurements are tagged `STAFF_ENTERED` / `KNOWN`. They are clinically actionable for triage risk scoring, but do not satisfy the statutory definition of `CLINICIAN_VERIFIED`.
- Only when an RMP explicitly accepts or authors the datum does it attain `CLINICIAN_APPROVED` / `VERIFIED` status.

This clear attribution boundary guarantees that legal responsibility, operational trust, and forensic accountability remain aligned with medical reality.
