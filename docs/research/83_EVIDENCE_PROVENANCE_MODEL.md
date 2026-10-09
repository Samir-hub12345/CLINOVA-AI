# CLINOVA AI — Evidence Provenance & Epistemic Conflict Data Model

> **Document ID:** `RES-83`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. The Evidence Provenance Mandate

A clinical parameter in an electronic health system (e.g. `Blood Pressure: 190/110 mmHg` or `Chest Pain: 3 days`) has zero clinical validity unless a doctor can inspect:
1. **Source Modality:** Who or what produced this datum? (Patient voice, OCR crop, nurse cuff, or AI assumption?)
2. **Epistemic State:** Is the datum known, conflicting, unreliable, verified, or merely inferred?
3. **Traceability:** Can the raw supporting audio snippet or document bounding box be viewed side-by-side?
4. **Conflict Persistence:** If two sources contradict each other, are BOTH preserved without silent overwrites?

CLINOVA AI formalizes the **Evidence Provenance & Epistemic Model**, eliminating silent data loss and opaque algorithmic hallucination.

---

## 2. Eight Canonical Evidence Source Types

Every piece of clinical information is categorized into one of eight immutable source types:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EIGHT EVIDENCE SOURCE TYPES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. PATIENT_REPORTED   ──> Subjective narrative entered by patient/caregiver│
│  2. VOICE_TRANSCRIBED  ──> Transcribed vernacular audio (Whisper engine)    │
│  3. OCR_EXTRACTED      ──> Parsed document slip (PaddleOCR / Tesseract)     │
│  4. CLINICIAN_VERIFIED ──> Physical exam finding or confirmed doctor entry  │
│  5. STAFF_ENTERED      ──> Point-of-care vital measured by nurse/worker     │
│  6. AI_INFERRED        ──> Extracted entity or clinical signal by SLM       │
│  7. SYSTEM_DERIVED     ──> Deterministic physiological score (Shock Index)  │
│  8. EXTERNAL_RECORD    ──> Prior EHR record or ABDM Health Information (FHIR)│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Six Canonical Epistemic States

Clinical knowledge is never purely binary (true/false). The CLINOVA data model represents clinical facts across six discrete epistemic states:

| Epistemic State | Clinical Definition | Operational Treatment |
| :--- | :--- | :--- |
| `KNOWN` | High-confidence parameter present and corroborated. | Eligible for clinical scoring and CAREGRAPH synthesis. |
| `UNKNOWN` | Parameter completely unmeasured or absent. | Explicitly flagged in epistemic audit; NEVER imputed as normal. |
| `CONFLICTING` | Mutually contradictory values exist across sources. | Both values preserved; flagged in red on doctor review screen. |
| `UNRELIABLE` | Low confidence ($< 0.70$) or degraded image/audio source. | Tagged as unverified; requires human re-measurement. |
| `VERIFIED` | Explicitly confirmed by a licensed clinician. | Medico-legally binding; unlocks final disposition sign-off. |
| `INFERRED` | Algorithmic entity or differential candidate from AI. | Strictly advisory; labeled with mandatory AI watermark. |

---

## 4. Conflicting Evidence Without Silent Overwrite

### 4.1 The Clinical Dilemma
A patient presents to triage stating: *"My blood pressure is completely normal, I take my tablet."* (Recorded as `PATIENT_REPORTED: SBP = 120 mmHg`).  
10 minutes later, the triage nurse places a calibrated sphygmomanometer on the patient's arm and records: `STAFF_ENTERED: SBP = 190 mmHg, DBP = 110 mmHg`.

In legacy systems, one of two dangerous errors occurs:
1. The nurse's entry silently overwrites the patient's statement, erasing evidence that the patient is in severe hypertensive crisis *despite believing they are normotensive* (indicating medication non-compliance or lack of insight).
2. The system averages them or rejects the second entry as a duplicate.

### 4.2 The CLINOVA Resolution
In CLINOVA AI:
- **Both records remain stored permanently** in `evidence_records` with their respective sources, actors, and timestamps.
- An explicit conflict entry is instantiated in `evidence_conflicts`.
- The doctor workbench displays both values side-by-side:

```
[!] CLINICAL CONFLICT DETECTED: Systolic Blood Pressure
    ├── Source A: PATIENT_REPORTED  [10:14 AM] -> 120 mmHg (Subjective statement)
    └── Source B: STAFF_ENTERED     [10:24 AM] -> 190 mmHg (Nurse Cuff Reading - Nurse Anita, RN)
    RESOLUTION REQUIRED: Clinician must select active physiological value.
```

---

## 5. Relational Schema Specification

### 5.1 `evidence_records` Table

```sql
CREATE TABLE evidence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_name VARCHAR(64) NOT NULL, -- e.g., 'systolic_bp', 'chest_pain_duration'
    canonical_concept VARCHAR(64),   -- SNOMED CT / LOINC identifier
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN (
        'PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 
        'CLINICIAN_VERIFIED', 'STAFF_ENTERED', 'AI_INFERRED', 
        'SYSTEM_DERIVED', 'EXTERNAL_RECORD'
    )),
    epistemic_status VARCHAR(16) NOT NULL DEFAULT 'INFERRED' CHECK (epistemic_status IN (
        'KNOWN', 'UNKNOWN', 'CONFLICTING', 'UNRELIABLE', 'VERIFIED', 'INFERRED'
    )),
    value_raw TEXT NOT NULL,
    value_normalized JSONB,           -- Structured representation: { "value": 190, "unit": "mmHg" }
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 
        CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_media_type VARCHAR(32)     -- 'AUDIO', 'DOCUMENT', 'MANUAL_ENTRY', 'SENSOR'
        CHECK (source_media_type IS NULL OR source_media_type IN ('AUDIO', 'DOCUMENT', 'MANUAL_ENTRY', 'SENSOR')),
    source_media_id UUID,             -- FK to audio_recordings(id) or documents(id)
    source_snippet_ref VARCHAR(128),  -- Word timestamp or bounding box crop ID
    recorded_by_actor_id UUID NOT NULL REFERENCES users(id),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verification_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED', 'REJECTED'
    )),
    verified_by_actor_id UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ
);

CREATE INDEX ix_ev_case_field ON evidence_records(case_id, field_name);
CREATE INDEX ix_ev_source_type ON evidence_records(source_type);
CREATE INDEX ix_ev_epistemic ON evidence_records(epistemic_status);
```

### 5.2 `evidence_conflicts` Table

```sql
CREATE TABLE evidence_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_name VARCHAR(64) NOT NULL,
    evidence_record_a_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    evidence_record_b_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    conflict_detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_type VARCHAR(32) CHECK (resolution_type IS NULL OR resolution_type IN (
        'ACCEPTED_A', 'ACCEPTED_B', 'ACCEPTED_BOTH_TEMPORAL', 'MANUAL_OVERRIDE'
    )),
    resolved_value JSONB,
    resolved_by_clinician_id UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    clinician_clinical_note TEXT
);

CREATE INDEX ix_conflicts_case ON evidence_conflicts(case_id);
CREATE INDEX ix_conflicts_unresolved ON evidence_conflicts(case_id, is_resolved);
```

---

## 6. SQLite Dialect Implementation

```sql
CREATE TABLE evidence_records (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_name TEXT NOT NULL,
    canonical_concept TEXT,
    source_type TEXT NOT NULL CHECK (source_type IN (
        'PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'OCR_EXTRACTED', 
        'CLINICIAN_VERIFIED', 'STAFF_ENTERED', 'AI_INFERRED', 
        'SYSTEM_DERIVED', 'EXTERNAL_RECORD'
    )),
    epistemic_status TEXT NOT NULL DEFAULT 'INFERRED' CHECK (epistemic_status IN (
        'KNOWN', 'UNKNOWN', 'CONFLICTING', 'UNRELIABLE', 'VERIFIED', 'INFERRED'
    )),
    value_raw TEXT NOT NULL,
    value_normalized TEXT, -- JSON text
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_media_type TEXT CHECK (source_media_type IS NULL OR source_media_type IN ('AUDIO', 'DOCUMENT', 'MANUAL_ENTRY', 'SENSOR')),
    source_media_id TEXT,
    source_snippet_ref TEXT,
    recorded_by_actor_id TEXT NOT NULL REFERENCES users(id),
    recorded_at TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
        'UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'DISPUTED', 'REJECTED'
    )),
    verified_by_actor_id TEXT REFERENCES users(id),
    verified_at TEXT
);

CREATE TABLE evidence_conflicts (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    field_name TEXT NOT NULL,
    evidence_record_a_id TEXT NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    evidence_record_b_id TEXT NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    conflict_detected_at TEXT NOT NULL,
    is_resolved INTEGER NOT NULL DEFAULT 0 CHECK (is_resolved IN (0, 1)),
    resolution_type TEXT CHECK (resolution_type IS NULL OR resolution_type IN (
        'ACCEPTED_A', 'ACCEPTED_B', 'ACCEPTED_BOTH_TEMPORAL', 'MANUAL_OVERRIDE'
    )),
    resolved_value TEXT, -- JSON text
    resolved_by_clinician_id TEXT REFERENCES users(id),
    resolved_at TEXT,
    clinician_clinical_note TEXT
);
```

---

## 7. Mathematical Invariants of Provenance

$$\begin{aligned}
\mathbf{Inv\ PROV\text{-}1} &: \quad \forall e \in \text{EvidenceRecords}, \quad e.\text{epistemic\_status} = \text{'VERIFIED'} \iff e.\text{verified\_by\_actor\_id} \neq \text{NULL} \\
\mathbf{Inv\ PROV\text{-}2} &: \quad \text{Evidence records are strictly immutable: no physical updates of } e.\text{value\_raw} \text{ permitted.} \\
\mathbf{Inv\ PROV\text{-}3} &: \quad \text{If two concurrent records } e_1, e_2 \text{ for field } f \text{ differ beyond tolerance } \epsilon, \\
& \quad \exists ! c \in \text{Conflicts} \text{ s.t. } c.\text{evidence\_record\_a\_id} = e_1.\text{id} \land c.\text{evidence\_record\_b\_id} = e_2.\text{id}
\end{aligned}$$
