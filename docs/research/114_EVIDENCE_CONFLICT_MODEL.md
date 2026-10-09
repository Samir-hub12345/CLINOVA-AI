# CLINOVA AI — Epistemic Evidence Conflict Model & Multi-Source Reconciliation

> **Document ID:** `RES-114`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Multi-Source Conflict Dilemma

In clinical practice, different sources of information frequently disagree. When a patient arrives at an emergency department, a single physiological parameter may be captured through multiple discordant channels:
- **Patient Self-Report:** *"My blood pressure is always normal, 120/80 mmHg."* (Recorded via kiosk at 10:14 AM).
- **OCR Lab Scan:** Old paper clinic slip from last month: *"BP 160/100 mmHg."* (Scanned via tablet at 10:18 AM).
- **Triage Nurse Measurement:** Calibrated physical cuff on left arm: *"BP 195/115 mmHg."* (Measured at 10:24 AM).

In traditional hospital EHR systems, a catastrophic bug occurs: the system executes an **in-place database `UPDATE`**, overwriting the previous entry with the latest one. This destroys vital diagnostic context:
1. It erases the fact that the patient is in severe hypertensive crisis *while believing they are normotensive* (indicating severe lack of insight, medication non-adherence, or cognitive alteration).
2. It conceals the longitudinal escalation from 160 to 195 mmHg.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL CONFLICT PERSISTENCE INVARIANT                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  DO NOT OVERWRITE ANY CONFLICTING VALUE.                    │
│                                                                             │
│   Every conflicting datum remains stored permanently in evidence_records.   │
│   Discordant values are linked in evidence_conflicts. The conflict is       │
│   surfaced transparently to the clinician, and the highest-acuity value     │
│   acts as an immediate safety tripwire without declaring it verified.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Tripartite Conflict Architecture

The CLINOVA conflict model is structured across three decoupled database layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. evidence_records: Immutable repository of ALL historical and active facts│
│    ├── Record A: PATIENT_REPORTED -> 120/80 mmHg [10:14 AM]                 │
│    ├── Record B: OCR_EXTRACTED    -> 160/100 mmHg [10:18 AM]                │
│    └── Record C: STAFF_ENTERED    -> 195/115 mmHg [10:24 AM]                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Linked by Conflict Detector
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. evidence_conflicts: First-class entity recording the active discordance  │
│    ├── conflict_id, case_id, field_name: 'blood_pressure'                   │
│    ├── evidence_records: [Record A, Record B, Record C]                     │
│    ├── variance_metrics: Max SBP Delta = 75 mmHg                            │
│    └── conflict_state: ACTIVE_UNRESOLVED                                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Clinician Resolution Event
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. conflict_resolution_events: Medico-legal audit of human adjudication     │
│    ├── resolved_by_clinician_id: Dr. P. K. Patnaik, MD (NMR #78412)         │
│    ├── resolution_strategy: ACCEPTED_LATEST_WITH_HISTORICAL_TREND           │
│    ├── active_physiological_value: 195/115 mmHg                             │
│    └── clinical_rationale: "Patient unaware of acute hypertensive urgency"  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Conflict Lifecycle Governance

### 3.1 Who Sees the Conflict?
- **Triage Nurse:** Sees an immediate visual conflict banner on the intake screen: *"Conflict: Patient reported normal BP, but cuff measured 195/115 mmHg. Re-check scheduled."*
- **Attending Doctor (RMP):** Surfaced prominently at the top of the Doctor Workbench as a high-visibility amber warning box with side-by-side comparison.
- **Referral Receiving Facility:** If the patient is transferred before resolution, the electronic SBAR referral summary highlights the conflict as an open clinical risk.

### 3.2 How Is It Displayed?
The Doctor Workbench displays the conflict in an ergonomic **Multi-Source Juxtaposition Card**:

```
[!] CLINICAL EVIDENCE CONFLICT DETECTED: Blood Pressure
┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
│ Source 1: Patient Stated │ Source 2: Past OCR Scan  │ Source 3: Nurse Cuff     │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ Value: 120/80 mmHg       │ Value: 160/100 mmHg      │ Value: 195/115 mmHg      │
│ Time:  10:14 AM (14m ago)│ Time:  10:18 AM (10m ago)│ Time:  10:24 AM (4m ago) │
│ Actor: Patient Kiosk     │ Engine: PaddleOCR (Scan) │ Actor: Anita Das, RN     │
│ Status: Subjective Report│ Status: Past OPD Card    │ Status: Calibrated Cuff  │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
Delta: +75 mmHg Systolic Variance Detected
ACTION REQUIRED: Select active value for physiological scoring & disposition.
```

### 3.3 Who May Resolve It?
**Registered Medical Practitioners (RMPs) ONLY.**  
Nurses, health workers, and automated AI algorithms are strictly prohibited from resolving evidence conflicts. Only an authenticated physician holding an NMR registration credential can execute a resolution event.

### 3.4 What Remains Preserved?
Everything. The resolution event does **NOT** delete or overwrite Records A, B, or C. It designates which record represents the current active physiological baseline while maintaining permanent audit pointers to all competing records.

### 3.5 What Happens If Unresolved?
If a clinician has not yet reviewed the case:
- The case retains the `CONFLICTING` epistemic status.
- The case’s Uncertainty Score $U_t$ is elevated ($U_t \ge 0.60$).
- The case is promoted in the triage queue to prevent waiting-room deterioration.
- Downstream automated discharge or routine care pathways are hard-blocked.

---

## 4. The Safety-Pessimistic Principle

A critical question arises: *Can downstream risk calculation proceed while a conflict is unresolved?*

**The Safety-Pessimistic Principle:**
$$\text{If an evidence conflict exists between multiple physiological values } \{v_1, v_2, \dots, v_k\},$$
$$\text{the risk scoring engine adopts } v^* = \arg\max_{v} \text{AcuityHazard}(v) \text{ as a temporary safety signal,}$$
$$\text{WITHOUT declaring } v^* \text{ to be clinically verified.}$$

### Concrete Application
- In the example ($120/80$ vs $160/100$ vs $195/115\text{ mmHg}$):
  - Systolic BP $195\text{ mmHg}$ represents the highest physiological hazard (NEWS2 risk score = 3).
  - The system temporarily computes emergency risk based on $195\text{ mmHg}$, immediately alerting the resuscitation team and moving the patient to the front of the queue.
  - However, the system does **NOT** write $195\text{ mmHg}$ as `VERIFIED`. It remains tagged `CONFLICTING / UNVERIFIED` until Dr. Patnaik examines the patient and physically confirms the diagnosis of hypertensive emergency.

---

## 5. Conflict Resolution Strategies

When an RMP resolves a conflict, they select from four formal resolution strategies:

| Strategy Code | Clinical Rationale | Operational Effect |
| :--- | :--- | :--- |
| `ACCEPTED_A` | Source A is clinically accurate; other sources were erroneous (e.g. cuff motion artifact). | Record A becomes active; others flagged `DISPUTED_INACTIVE`. |
| `ACCEPTED_B` | Source B is clinically accurate; Source A was incorrect or outdated. | Record B becomes active; others flagged `DISPUTED_INACTIVE`. |
| `ACCEPTED_BOTH_TEMPORAL`| Both values were accurate at their respective times, representing rapid disease evolution. | Both records remain active across separate temporal epochs. |
| `MANUAL_OVERRIDE` | Neither source was correct; clinician performed physical bedside re-measurement. | Clinician enters fresh `CLINICIAN_VERIFIED` measurement; all prior records archived. |

---

## 6. Conflict Relational Schema

```sql
CREATE TABLE evidence_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_name VARCHAR(64) NOT NULL,
    canonical_concept VARCHAR(64), -- LOINC or SNOMED CT
    
    conflict_detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    max_variance_magnitude NUMERIC(10,3),
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Resolution Metadata (Populated upon RMP Adjudication)
    resolution_strategy VARCHAR(32) CHECK (resolution_strategy IS NULL OR resolution_strategy IN (
        'ACCEPTED_A', 'ACCEPTED_B', 'ACCEPTED_BOTH_TEMPORAL', 'MANUAL_OVERRIDE'
    )),
    active_evidence_record_id UUID REFERENCES evidence_records(id) ON DELETE RESTRICT,
    resolved_by_clinician_id UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    clinician_clinical_note TEXT,
    
    CONSTRAINT chk_conflict_resolution_complete CHECK (
        (is_resolved = FALSE AND resolved_by_clinician_id IS NULL AND resolved_at IS NULL) OR
        (is_resolved = TRUE AND resolved_by_clinician_id IS NOT NULL AND resolved_at IS NOT NULL AND resolution_strategy IS NOT NULL)
    )
);

CREATE TABLE evidence_conflict_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_id UUID NOT NULL REFERENCES evidence_conflicts(id) ON DELETE CASCADE,
    evidence_record_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    participant_role VARCHAR(16) NOT NULL DEFAULT 'COMPETING_VALUE' CHECK (participant_role IN (
        'COMPETING_VALUE', 'SUPERSEDED_HISTORICAL', 'DISPUTED_VALUE'
    )),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_conflict_case ON evidence_conflicts(case_id);
CREATE INDEX ix_conflict_unres ON evidence_conflicts(case_id, is_resolved);
CREATE INDEX ix_conflict_part ON evidence_conflict_participants(conflict_id, evidence_record_id);
```

By decoupling storage, detection, safety signaling, and human adjudication, the CLINOVA Evidence Conflict Model protects patients from the perils of silent data loss and ungrounded algorithmic certainty.
