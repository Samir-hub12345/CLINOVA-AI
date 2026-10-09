# CLINOVA AI — Conceptual Role-Based Access Control (RBAC) & Permission Model

> **Document ID:** `RES-34`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 3 — Target Users Research & User-Role Specification  
> **Version:** 3.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Security Governance Group  

---

## 1. Executive Summary & Governance Principles

This document establishes the **preliminary conceptual permission matrix and access governance boundaries** for CLINOVA AI.

> **CRITICAL ARCHITECTURAL NOTICE:**  
> This specification defines the **conceptual security and authorization model only**.  
> In strict compliance with the Phase 3 charter, **NO authentication (OAuth, JWT), authorization middleware, or database access control logic is implemented in this phase**. Implementation is strictly deferred to Phase 4+.

### 1.1 Four Core Architectural Invariants
1. **The Clinician Monopoly on Clinical Disposition:** Only a qualified, licensed Primary Clinician (`ROLE_CLINICIAN`) possesses the authority to execute binding clinical decisions (`DISCHARGE`, `ADMIT`, `REFER`, `OVERRIDE`). No automated AI process, non-clinical staff, or administrative role can order clinical disposition.
2. **The Principle of Least Privilege:** Users receive strictly the minimum visibility and transactional capability necessary to execute their assigned clinical or operational duties.
3. **The Administrative-Clinical Partition:** System and Facility Administrators have zero access to un-anonymized, identified clinical records. Conversely, clinical staff have zero rights to modify system configurations, model weights, or audit trails.
4. **Universal Auditability:** Every write, verification, modification, disposition, and override action generates an immutable, tamper-evident audit entry capturing Actor ID, Role, Timestamp, Target ID, Previous Value, New Value, and Justification.

---

## 2. Standardized Permission Verbs

The conceptual model utilizes 16 standardized permission verbs:

| Permission Verb | Functional Definition | Typical Scope & Resource |
|:---|:---|:---|
| `VIEW` | Read access to inspect data records, summaries, or dashboards. | Case records, queue boards, reports, audit logs. |
| `CREATE` | Authoring and submitting new data entries or encounters. | Intake drafts, vitals readings, notes, referral requests. |
| `EDIT` | Modifying mutable fields in drafts or assigned records. | In-progress intake drafts, transport notes, facility rosters. |
| `VERIFY` | Attesting to the clinical or factual accuracy of data. | Extracted labs, vital signs, physical exam findings. |
| `ASSIGN` | Delegating or transferring task custody to a specific role/user. | Assigning missing-data checklist to nurse desk. |
| `ESCALATE` | Triggering acute clinical emergency alerts or priority promotions. | Code Red alerts, bedside emergency calls, shock alerts. |
| `REFER` | Authorizing medical inter-facility transfer of a patient. | Transfer requisition pack, receiving hospital matching. |
| `ADMIT` | Authorizing physical admission to inpatient ward, ICU, or OT. | Bed reservation, inpatient admission order. |
| `DISCHARGE` | Authorizing completion of care and release from facility. | Discharge summary, follow-up prescription slip. |
| `OVERRIDE` | Explicitly overriding an AI recommendation or standard queue order. | Modifying AI triage note, changing priority ranking. |
| `EXPORT` | Downloading or transmitting structured reports or datasets. | Master Clinical Report, Referral Pack, Audit archive. |
| `VIEW_AUDIT` | Inspecting the tamper-evident system access and modification log. | Security audit console, patient access receipts. |
| `MANAGE_FACILITY` | Modifying institutional capabilities, beds, and rosters. | FACILITYGRAPH profile, department capacity settings. |
| `MANAGE_USERS` | Provisioning, updating, or revoking user accounts and roles. | User credential directory, role assignment tables. |
| `MANAGE_SYSTEM` | Configuring server runtime, local AI processes, and backups. | Environment variables, local model ports, cache purges. |
| `RECORD_OUTCOME` | Registering verified longitudinal patient recovery status. | Resolution endpoints (`FULL_RECOVERY`, `MORTALITY`). |

---

## 3. Master Conceptual Permission Matrix

The following matrix cross-maps the 16 permission verbs across all eight candidate user roles:

| Permission Verb | 1. Clinician (`ROLE_CLINICIAN`) | 2. Nurse (`ROLE_NURSE`) | 3. Referral Staff (`ROLE_REFERRAL`) | 4. Patient (`ROLE_PATIENT`) | 5. Caregiver (`ROLE_CAREGIVER`) | 6. Facility Admin (`ROLE_FAC_ADMIN`) | 7. System Admin (`ROLE_SYS_ADMIN`) | 8. Researcher (`ROLE_RESEARCHER`) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `VIEW` | **FULL (All Cases)** | **ASSIGNED (Intake/Vitals)** | **REFERRALS ONLY** | **OWN APPROVED ONLY** | **OWN APPROVED ONLY** | **AGGREGATED ONLY** | **LOGS ONLY (No PII)** | **SYNTHETIC ONLY** |
| `CREATE` | Cases, Notes, Orders | Cases, Vitals, Checklists | Transport Manifests | Self-Intake Drafts | Surrogate Intake Drafts| Facility Capabilities | User Accounts, Keys | Benchmark Jobs |
| `EDIT` | All Clinical Fields | Own Vitals, Draft Intake | Transport Notes | Unsubmitted Draft Only| Unsubmitted Draft Only | Bed Counts, Rosters | User Roles, Settings | Benchmark Configs |
| `VERIFY` | **FULL (Labs, Vitals, AI)**| **PARTIAL (Vitals Only)** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| `ASSIGN` | Tasks, Ward Transfer | Triage Desks | Ambulance Units | ❌ DENIED | ❌ DENIED | Staff Shift Rosters | ❌ DENIED | ❌ DENIED |
| `ESCALATE` | **FULL (Resuscitation/OT)**| **FULL (Bedside Doctor Call)**| Transport Delay Flags | Distress Button Call | Distress Button Call | Disaster Protocol | Failover Alert | ❌ DENIED |
| `REFER` | **AUTHORIZE (Exclusive)** | ❌ DENIED | **EXECUTE (Logistics)** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| `ADMIT` | **AUTHORIZE (Exclusive)** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | Bed Allocation Only | ❌ DENIED | ❌ DENIED |
| `DISCHARGE` | **AUTHORIZE (Exclusive)** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| `OVERRIDE` | **FULL (AI & Queue)** | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |
| `EXPORT` | Full Clinical Packs | Vitals Slips | Referral Slips | Approved Care Summary | Approved Care Summary | Operational Reports | System Error Logs | De-identified Metrics|
| `VIEW_AUDIT` | Clinical Case Audit | Own Action Log | Transfer Log | Access History Receipt| Access History Receipt| Department Stats | **FULL (Security Log)**| ❌ DENIED |
| `MANAGE_FACILITY` | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | **FULL** | ❌ DENIED | ❌ DENIED |
| `MANAGE_USERS` | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | Staff Rostering Only | **FULL (Accounts/RBAC)**| ❌ DENIED |
| `MANAGE_SYSTEM` | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | **FULL (Runtime/DB)**| ❌ DENIED |
| `RECORD_OUTCOME` | **YES** | **YES (Community)** | **YES (Transfer Result)**| ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED | ❌ DENIED |

---

## 4. Resource-Level Permission Breakdown

To ensure zero ambiguity during subsequent Phase 4 implementation, the table below maps permission boundaries across **nine discrete architectural resource domains**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA RESOURCE SECURITY DOMAINS                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  DOMAIN 1: Patient Identity & Consent       DOMAIN 6: Queue & Assignments   │
│  DOMAIN 2: Raw Intake & Media Ingestion     DOMAIN 7: Clinical Disposition  │
│  DOMAIN 3: Extracted Clinical Parameters    DOMAIN 8: Referral & Logistics  │
│  DOMAIN 4: Vitals & Danger Sign Checklists  DOMAIN 9: Facility & Governance │
│  DOMAIN 5: AI Inferences & Triage Drafts                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Domain 1: Patient Identity, Demographics & Consent (`B14`, `B15`)
- `ROLE_PATIENT`, `ROLE_CAREGIVER`: Can provide initial demographics; can grant, view, and revoke data processing consent (`B14`).
- `ROLE_NURSE`: Can verify synthetic patient ID against physical wristband/OPD ticket; can record verbal consent.
- `ROLE_CLINICIAN`: Full read access; can mark emergency implied consent for unconscious patients.
- `ROLE_FACILITY_ADMIN`, `ROLE_SYS_ADMIN`: Barred from viewing decrypted demographic PII.

### 4.2 Domain 2: Raw Ingestion Media (Audio Recordings & Document Scans) (`B01`-`B04`)
- `ROLE_PATIENT`, `ROLE_CAREGIVER`: Can upload audio and photos during intake session; zero access to other patients' uploads.
- `ROLE_NURSE`: Can assist upload and trigger OCR processing.
- `ROLE_CLINICIAN`: Full access to play audio waveforms and view OCR bounding crops for clinical evidence provenance (`C02`).
- `ROLE_SYS_ADMIN`: Barred from accessing media content; oversees automated 24-hour ephemeral file purge (`B16`).

### 4.3 Domain 3: Extracted Clinical Entities & Longitudinal Timeline (`B05`, `B06`)
- `ROLE_CLINICIAN`: **Exclusive full authority** to `VERIFY`, `MODIFY`, or `ADD` discrete clinical entities, symptom onset dates, and lab assay values.
- `ROLE_NURSE`: Read access; can flag conflicting information for doctor review.
- `ROLE_PATIENT`: Read access restricted to clinician-approved summaries.

### 4.4 Domain 4: Vital Signs & Danger Sign Checklists (`B07`, `B10`)
- `ROLE_NURSE`: Authorized to `CREATE` and `VERIFY` vital sign measurements (BP, PR, SpO2, RR, Temp, Glucose); can complete danger checklists.
- `ROLE_CLINICIAN`: Full authority to inspect, re-measure, override, or verify all vitals.
- `ROLE_PATIENT`: Self-reported vitals are tagged `UNVERIFIED_SELF_REPORTED` until confirmed by nurse or clinician.

### 4.5 Domain 5: AI Inferences, Trajectory & Triage Note Drafts (`B18`, `C01`, `C03`)
- `ROLE_CLINICIAN`: Full access to inspect AI triage drafts, trajectory slope ($\Delta R_t / \Delta t$), and uncertainty gauges ($U_t$). Possesses exclusive authority to accept, modify, or reject AI drafts.
- `ROLE_NURSE`: Sees red-flag alert badges and missing-data prompts; does not review full diagnostic differential drafts.
- `ROLE_PATIENT`: Strictly barred from viewing internal AI reasoning, differential diagnoses, or mathematical uncertainty scores.

### 4.6 Domain 6: Queue Management & Escalation (`B11`)
- `ROLE_NURSE`: Authorized to trigger immediate acute escalation (`ESCALATE_EMERGENCY`), which moves the patient to the top of the Doctor Queue.
- `ROLE_CLINICIAN`: Can claim any case from the queue, prioritize emergency presentations, or assign observation tasks.
- `ROLE_FACILITY_ADMIN`: Can monitor queue wait-time distributions; cannot re-order individual clinical queue priority.

### 4.7 Domain 7: Clinical Disposition & Sign-Off (`B18`, `DOC-15`)
- `ROLE_CLINICIAN`: **Exclusive monopoly** over `ROUTINE_DISCHARGE`, `OBSERVATION`, `WARD_ADMISSION`, `EMERGENCY_OT`, and `INTER_FACILITY_REFERRAL`.
- All other roles: Strictly prohibited (`DENIED`). Attempting to issue a disposition from a non-clinician role triggers an immediate security exception.

### 4.8 Domain 8: Referral Logistics & Transport Matching (`B13`, `C05`, `C06`)
- `ROLE_CLINICIAN`: Initiates and signs the clinical referral order and capability justification.
- `ROLE_REFERRAL_STAFF`: Inspects FACILITYGRAPH destination recommendations; contacts receiving hospital; confirms bed reservation; assigns ambulance; updates logistical milestones (`IN_TRANSIT`, `HANDOFF_CONFIRMED`).

### 4.9 Domain 9: Facility Configuration & Security Governance
- `ROLE_FACILITY_ADMIN`: Exclusive authority to update FACILITYGRAPH capacity (beds, specialists on duty, oxygen pressure, equipment status).
- `ROLE_SYSTEM_ADMIN`: Exclusive authority to manage user accounts, RBAC credentials, cryptographic keys, and database maintenance. Barred from clinical data.

---

## 5. Explicit Negative Permissions & Anti-Bypass Guardrails

To prevent privilege creep and medicolegal violations, the system enforces strict negative permissions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MANDATORY ENFORCED NEGATIVE PERMISSIONS                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ❌ NP-01: NO Non-Clinician Discharge / Prescribe / Referral Authority      │
│  ❌ NP-02: NO Autonomous AI Disposition or Medication Ordering              │
│  ❌ NP-03: NO Administrative Modification of Clinical Case Records          │
│  ❌ NP-04: NO Clinician / Staff Alteration of Immutable Audit Logs          │
│  ❌ NP-05: NO Patient Access to Unverified Differentials or AI Scratchpads  │
│  ❌ NP-06: NO Researcher Access to Live Identifiable Patient Data           │
│  ❌ NP-07: NO Creation of Duplicate Master Cases for an Existing Patient    │
│  ❌ NP-08: NO Omission of Ephemeral Media Purging Beyond 24 Hours           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Emergency "Break-Glass" Protocol

Under catastrophic mass-casualty conditions or sudden staff incapacitation, the platform supports a formal **Emergency Break-Glass Exception**:

1. **Trigger Condition:** Licensed Medical Officer or Senior Triage Nurse declares `BREAK_GLASS_EMERGENCY` when:
   - Examining physician is incapacitated.
   - Sudden mass casualty event (bus crash, industrial blast) overwhelms standard registration.
   - Unconscious patient arrives with no identity and immediate resuscitation is required.
2. **Behavioral Effect:**
   - Temporarily grants visiting/emergency medical staff immediate read/write access to open cases without formal department transfer approval.
   - Fast-tracks patient entry without blocking for digital consent (implied emergency consent under Indian law).
3. **Audit Invariant:**
   - Every Break-Glass activation triggers a persistent visual banner, broadcasts an alert to the Facility Administrator, and records a permanent, high-severity entry in the tamper-evident security audit log requiring administrative review within 24 hours.
