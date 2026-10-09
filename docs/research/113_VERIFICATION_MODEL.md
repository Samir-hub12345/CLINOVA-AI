# CLINOVA AI — Acuity-Proportional Verification Model

> **Document ID:** `RES-113`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Verification Dilemma: Clinical Safety vs Cognitive Friction

In clinical software architecture, verification protocols frequently oscillate between two fatal extremes:
1. **The Dangerous Permissive Flaw:** All data (OCR scans, patient statements, AI deductions) is ingested without review, leading to catastrophic medical errors, hallucinated diagnoses, and medicolegal exposure under National Medical Commission (NMC) regulations.
2. **The Crippling Friction Flaw:** Requiring exhaustive multi-step physician sign-off on every non-critical data field (e.g., patient hair color, routine address, standard dietary preference) creates alert fatigue, cognitive exhaustion, and systemic circumvention.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE LAW OF ACUITY-PROPORTIONAL VERIFICATION                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   The stringency of clinical verification must scale proportionally with    │
│   the physiological hazard, diagnostic sensitivity, and legal finality      │
│   of the underlying datum. Low-risk information must flow with minimal      │
│   friction; critical life-safety data requires mandatory human attestation. │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Verification Progression Lifecycle

Clinical facts transition across three canonical verification milestones:

```
┌────────────────┐        Staff Confirmation        ┌────────────────┐       Clinician Sign-off       ┌────────────────────┐
│   UNVERIFIED   │ ────────────────────────────────► │ STAFF_VERIFIED │ ────────────────────────────► │ CLINICIAN_APPROVED │
│  (Raw Ingest)  │                                   │ (Triage Check) │                               │  (Legal RMP Sign)  │
└────────────────┘                                   └────────────────┘                               └────────────────────┘
```

- **`UNVERIFIED`:** Initial state of all raw perceptual extractions (OCR text, Whisper transcripts, direct patient app submissions).
- **`STAFF_VERIFIED`:** Reviewed and corroborated by a licensed staff nurse, ANM, or paramedic during intake or vital measurement. Operationally valid for triage scoring and queue ranking.
- **`CLINICIAN_APPROVED`:** Explicitly attested by a Registered Medical Practitioner (RMP) holding a verified National Medical Register (NMR) credential. Medico-legally binding for medical orders, prescriptions, and disposition.

---

## 3. Four Canonical Verification Tiers

To eliminate unnecessary clinical bottlenecks, every clinical entity in the system is statically categorized into one of four **Verification Tiers**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FOUR VERIFICATION TIERS                               │
├──────────────────────────┬─────────────────────────┬────────────────────────┤
│ Verification Tier Code   │ Review Requirement      │ Clinical Risk Domain   │
├──────────────────────────┼─────────────────────────┼────────────────────────┤
│ NO_REVIEW_REQUIRED       │ Autonomous System Ingest│ Administrative / Routine│
│ STAFF_REVIEW_REQUIRED    │ Frontline Nurse / ASHA  │ Standard Vitals / Labs │
│ CLINICIAN_REVIEW_REQUIRED│ Attending Doctor (RMP)  │ Abnormal Signs / Dx    │
│ DUAL_REVIEW_REQUIRED     │ Dual Independent Clin.  │ Critical Organ Failure │
└──────────────────────────┴─────────────────────────┴────────────────────────┘
```

### Detailed Tier Classifications

#### Tier 1: `NO_REVIEW_REQUIRED` (Friction-Free Operational Data)
- **Scope:** Non-clinical administrative metadata, appointment check-in timestamps, demographic spellings, deterministic unit conversions ($140\text{ lbs} \to 63.5\text{ kg}$), standard insurance policy numbers, and queue sequence counters.
- **Verification Rule:** Automatically ingested upon schema validation. Zero human intervention required.
- **Safety Boundary:** Prohibited from containing physiological measurements, medication names, or clinical symptoms.

#### Tier 2: `STAFF_REVIEW_REQUIRED` (Nurse / Frontline Verification)
- **Scope:** Routine normal vital signs (e.g. SBP $110\text{--}130\text{ mmHg}$, SpO2 $\ge 97\%$), verified patient symptom checklist, basic demographic past medical history (e.g., self-reported childhood asthma), standard outpatient lab values within normal reference limits.
- **Verification Rule:** Staff Nurse or ANM verifies via 1-click batch confirmation during triage intake. Unlocks routine queue promotion.
- **Safety Boundary:** If a vital reading crosses abnormal thresholds (e.g., NEWS2 $\ge 5$), it is dynamically escalated to Tier 3.

#### Tier 3: `CLINICIAN_REVIEW_REQUIRED` (RMP Attestation Monopoly)
- **Scope:** Critical red-flag symptoms (severe chest pain, thunderclap headache, acute motor deficit), abnormal physiological vitals, OCR extractions of high-potency medications (Insulin, Digoxin, Warfarin), abnormal lab results (Serum Creatinine $\ge 2.0\text{ mg/dL}$, Troponin positive), AI-inferred differential hypotheses, and all formal ICD-11 diagnostic impressions.
- **Verification Rule:** Cannot be finalized or acted upon without authenticated review and affirmative digital sign-off by an RMP on the Doctor Workbench.
- **Statutory Grounding:** National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023, Regulation 27.

#### Tier 4: `DUAL_REVIEW_REQUIRED` (High-Hazard Independent Verification)
- **Scope:** High-alert medication dosing (e.g. IV Thrombolysis / Alteplase infusion, IV Insulin infusion, Opioid titration), Blood Transfusion ABO/Rh compatibility, Emergency Resuscitation Do-Not-Attempt-Resuscitation (DNAR) orders, and Emergency Operation Theatre (OT) surgical bookings without prior guardian consent.
- **Verification Rule:** Requires **Two Independent Clinicians** (e.g. Attending Consultant + Senior Medical Officer, or Lead Surgeon + Consultant Anesthesiologist) to physically authenticate on separate credentials.
- **Safety Boundary:** The system strictly prohibits the same user ID from signing both primary and secondary attestations.

---

## 4. Verification Relational Schema

```sql
CREATE TABLE verification_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evidence_record_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    
    verification_tier VARCHAR(32) NOT NULL CHECK (verification_tier IN (
        'NO_REVIEW_REQUIRED', 'STAFF_REVIEW_REQUIRED', 
        'CLINICIAN_REVIEW_REQUIRED', 'DUAL_REVIEW_REQUIRED'
    )),
    
    previous_verification_status VARCHAR(24) NOT NULL,
    new_verification_status VARCHAR(24) NOT NULL CHECK (new_verification_status IN (
        'STAFF_VERIFIED', 'CLINICIAN_APPROVED', 'REJECTED', 'DISPUTED'
    )),
    
    primary_verifier_id UUID NOT NULL REFERENCES users(id),
    primary_verifier_role VARCHAR(32) NOT NULL,
    primary_nmr_number VARCHAR(64),
    primary_verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    secondary_verifier_id UUID REFERENCES users(id),
    secondary_verifier_role VARCHAR(32),
    secondary_nmr_number VARCHAR(64),
    secondary_verified_at TIMESTAMPTZ,
    
    verification_channel VARCHAR(32) NOT NULL DEFAULT 'WORKBENCH_GUI' CHECK (verification_channel IN (
        'WORKBENCH_GUI', 'MOBILE_TRIAGE_APP', 'EMERGENCY_VOICE_OVERRIDE', 'BATCH_INTAKE_CONFIRM'
    )),
    
    verification_notes TEXT,
    
    -- Invariant: For DUAL_REVIEW_REQUIRED, secondary verifier cannot be primary verifier
    CONSTRAINT chk_dual_verifier_distinct CHECK (
        verification_tier != 'DUAL_REVIEW_REQUIRED' OR (
            secondary_verifier_id IS NOT NULL AND 
            secondary_verifier_id != primary_verifier_id AND
            secondary_verified_at IS NOT NULL
        )
    )
);

CREATE INDEX ix_verif_case ON verification_events(case_id);
CREATE INDEX ix_verif_evidence ON verification_events(evidence_record_id);
CREATE INDEX ix_verif_primary_user ON verification_events(primary_verifier_id);
```

---

## 5. Acuity Escalation Dynamic

The verification tier of an evidence record is **not static**; it automatically escalates based on physiological context:
- *Example:* A patient’s respiratory rate of $18\text{ breaths/min}$ is classified as Tier 2 (`STAFF_REVIEW_REQUIRED`).
- If 15 minutes later, the patient's SpO2 drops to $84\%$ while the respiratory rate jumps to $38\text{ breaths/min}$, the system’s physiological monitoring engine automatically escalates both the vitals and the associated case to Tier 3 (`CLINICIAN_REVIEW_REQUIRED`), alerting the attending physician immediately.

This acuity-proportional architecture guarantees that frontline staff are never buried in needless bureaucratic clicks, while life-threatening abnormalities are subjected to rigorous, tamper-evident physician review.
