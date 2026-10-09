# CLINOVA AI — Multi-Clock Temporal Provenance Model

> **Document ID:** `RES-118`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Multi-Clock Phenomenon in Clinical Medicine

In standard enterprise database architecture, tables typically maintain a single timestamp column: `created_at DEFAULT NOW()`. In clinical systems, **relying on a single system clock is a catastrophic medicolegal and clinical error**.

A physiological event, its digital capture, its server ingestion, its clinical verification, and the resulting medical decision almost **never occur simultaneously**:
- A patient experiences crushing substernal chest pain at 6:30 AM (*Event Time*).
- An ASHA worker in a remote village measures their blood pressure on an offline tablet at 7:15 AM (*Capture Time*).
- The tablet reconnects to cellular data when the ambulance reaches the highway at 8:45 AM, syncing the record to the central server (*Ingestion Time*).
- The emergency medical officer at the District Hospital reviews the ECG and confirms acute myocardial infarction at 8:52 AM (*Verification Time*).
- The doctor orders IV Tenecteplase thrombolysis at 8:54 AM (*Decision Time*).

If the system collapses these into a single `created_at = 08:45 AM`, two catastrophic distortions occur:
1. **Clinical Error:** The system believes the patient's chest pain began at 8:45 AM, leading an automated protocol to falsely calculate a symptom duration of 9 minutes instead of 2 hours and 24 minutes, dangerously distorting the eligibility window for thrombolysis (which has a strict $< 4.5\text{ hour}$ cutoff).
2. **Medicolegal Vulnerability:** Under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023, conflating server storage time with physical measurement time destroys the evidentiary chain of custody in medical negligence litigation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL MULTI-CLOCK TEMPORAL INVARIANT                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  DECOUPLE EVENT, CAPTURE, INGESTION,                        │
│                   VERIFICATION, AND DECISION TIMES.                         │
│                                                                             │
│   Every clinical fact must preserve its five distinct temporal anchors.     │
│   Physiological trajectory modeling must ALWAYS plot against EVENT_TIME.    │
│   Audit integrity and legal custody must ALWAYS verify INGESTION_TIME.      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Five Canonical Temporal Anchors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FIVE CANONICAL TEMPORAL ANCHORS                       │
├────────────────────┬────────────────────────────────────────────────────────┤
│ Temporal Anchor    │ Operational & Physical Meaning                         │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 1. EVENT_TIME      │ When the biological phenomenon occurred in the patient.│
├────────────────────┼────────────────────────────────────────────────────────┤
│ 2. CAPTURE_TIME    │ When the physical sensor or human entered the datum.   │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 3. INGESTION_TIME  │ When the server database committed the row to disk.    │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 4. VERIFICATION_TIME│ When an authenticated clinician digitally attested it.│
├────────────────────┼────────────────────────────────────────────────────────┤
│ 5. DECISION_TIME   │ When a clinical order/action was executed based on it. │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Four Real-World Clinical Delay Case Studies

### 3.1 Case Study 1: Delayed OCR Document Upload
- **Real-World Reality:** A patient arrives at a District Hospital emergency department at 11:00 AM with acute pulmonary edema. The family hands the doctor a paper discharge summary from an admission 3 weeks ago. The triage clerk photographs the paper summary at 11:15 AM.
- **Temporal Decoupling:**
  - $\text{EVENT\_TIME} = \text{September 14, 2026, 14:30:00}$ (When the prior echocardiogram was performed).
  - $\text{CAPTURE\_TIME} = \text{October 08, 2026, 11:15:20}$ (When the smartphone camera snapped the image).
  - $\text{INGESTION\_TIME} = \text{October 08, 2026, 11:15:24}$ (When the OCR engine parsed the text).
  - $\text{VERIFICATION\_TIME} = \text{October 08, 2026, 11:20:00}$ (When the doctor confirmed the EF of 25%).
- **Clinical Significance:** Plotting this left ventricular ejection fraction ($25\%$) at 11:15 AM today would imply acute cardiogenic collapse occurred 15 minutes ago. Grounding it in `EVENT_TIME` correctly reflects chronic systolic heart failure dating back 3 weeks.

### 3.2 Case Study 2: Delayed Biochemistry Laboratory Result
- **Real-World Reality:** In a busy hospital, blood for Serum Potassium is drawn at 08:00 AM. Due to laboratory backlog, the specimen is centrifuged at 10:30 AM, analyzed at 11:45 AM, and transmitted via the laboratory interface at 12:15 PM.
- **Temporal Decoupling:**
  - $\text{EVENT\_TIME} = 08:00:00\text{ AM}$ (When the patient's cellular blood was extracted).
  - $\text{CAPTURE\_TIME} = 11:45:00\text{ AM}$ (When the biochemistry analyzer executed the assay).
  - $\text{INGESTION\_TIME} = 12:15:00\text{ PM}$ (When the LIS pushed the JSON result into CLINOVA).
- **Clinical Significance:** By 12:15 PM, a potassium reading of $6.8\text{ mEq/L}$ (severe hyperkalemia) represents the patient's state **4 hours and 15 minutes ago**. The clinician must immediately recognize that the lab is historic and order an emergency bedside 12-lead ECG to detect active hyperkalemic cardiac arrhythmias.

### 3.3 Case Study 3: Delayed Offline Edge Synchronization
- **Real-World Reality:** An ANM health worker in a remote tribal village in Mayurbhanj district measures an infant's blood glucose at 09:30 AM ($42\text{ mg/dL}$, severe hypoglycemia) on a solar-powered offline tablet. The health worker administers oral glucose and travels by motorcycle to a township with cellular signal, syncing at 03:00 PM.
- **Temporal Decoupling:**
  - $\text{EVENT\_TIME} = 09:30:00\text{ AM}$
  - $\text{CAPTURE\_TIME} = 09:30:00\text{ AM}$ (Local tablet hardware clock).
  - $\text{INGESTION\_TIME} = 03:00:15\text{ PM}$ (Central cloud database).
- **Clinical Significance:** Central risk dashboards must NOT flag the child as actively hypoglycemic at 3:00 PM. The timeline correctly anchors the hypoglycemia at 9:30 AM and prompts the receiving clinic to verify post-treatment recovery.

### 3.4 Case Study 4: Retrospective Emergency Resuscitation Charting
- **Real-World Reality:** During a cardiac arrest code blue at 02:00 AM, the resuscitation team delivers 3 defibrillation shocks and injects 3 doses of Epinephrine. The patient achieves return of spontaneous circulation (ROSC) at 02:22 AM. After stabilizing the endotracheal tube and central line, the resident physician sits at the workstation at 03:15 AM to document the resuscitation.
- **Temporal Decoupling:**
  - $\text{EVENT\_TIME} = 02:05:00\text{ AM}$ (First shock), $02:10:00\text{ AM}$ (Second shock), etc.
  - $\text{CAPTURE\_TIME} = 03:15:00\text{ AM}$ (Workstation documentation).
  - $\text{INGESTION\_TIME} = 03:15:45\text{ AM}$.
  - $\text{VERIFICATION\_TIME} = 03:20:00\text{ AM}$ (Consultant review).
- **Clinical Significance:** Conflating event time with capture time would make it appear that the shocks were delivered after ROSC, creating severe legal liability. Preserving true `EVENT_TIME` preserves clinical truth.

---

## 4. Canonical Temporal Relational Schema

```sql
CREATE TABLE temporal_provenance_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evidence_record_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    
    -- The Five Temporal Anchors
    event_timestamp TIMESTAMPTZ NOT NULL,       -- Biological occurrence time
    capture_timestamp TIMESTAMPTZ NOT NULL,     -- Sensor / manual input time
    ingestion_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Database commit time
    verification_timestamp TIMESTAMPTZ,         -- RMP attestation time
    decision_timestamp TIMESTAMPTZ,             -- Clinical action execution time
    
    -- Temporal Quality & Approximation Flags
    event_time_precision VARCHAR(16) NOT NULL DEFAULT 'EXACT_SECOND' CHECK (event_time_precision IN (
        'EXACT_SECOND', 'MINUTE_ESTIMATE', 'HOUR_ESTIMATE', 'APPROXIMATE_DAY', 'HISTORICAL_YEAR'
    )),
    is_retrospective_documentation BOOLEAN NOT NULL DEFAULT FALSE,
    documentation_lag_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (capture_timestamp - event_timestamp)) / 60
    ) STORED,
    
    -- Device Clock Synchronization Telemetry
    device_clock_synced_ntp BOOLEAN NOT NULL DEFAULT TRUE,
    estimated_clock_drift_ms INTEGER NOT NULL DEFAULT 0,
    
    CONSTRAINT chk_capture_after_or_equal_event CHECK (capture_timestamp >= (event_timestamp - INTERVAL '60 seconds')),
    CONSTRAINT chk_ingest_after_or_equal_capture CHECK (ingestion_timestamp >= (capture_timestamp - INTERVAL '60 seconds'))
);

CREATE INDEX ix_temp_case ON temporal_provenance_ledgers(case_id);
CREATE INDEX ix_temp_evidence ON temporal_provenance_ledgers(evidence_record_id);
CREATE INDEX ix_temp_event_time ON temporal_provenance_ledgers(event_timestamp);
```

By decoupling these five distinct temporal clocks, CLINOVA AI guarantees accurate mathematical trajectory modeling, respects biological reality, and establishes unassailable forensic chain of custody.
