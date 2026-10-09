# CLINOVA AI — Acuity-Proportional Dual-Review Architecture

> **Document ID:** `RES-152`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Safety & Physician Workflow Architecture Group  

---

## 1. Clinical Context & Acuity-Proportional Verification

In healthcare environments, requiring physician sign-off on every trivial data point (e.g. administrative spelling, normal temperature reading) creates crippling cognitive friction and alert fatigue. Conversely, allowing a single clinician to authorize irreversible, life-critical procedures without independent cross-checking introduces single-human failure risks.

CLINOVA AI resolves this via the **Acuity-Proportional Verification Framework**:

| Verification Tier | Clinical Scope | Authorized Actor | Database Gating |
| :--- | :--- | :--- | :--- |
| **Tier 1: `NO_REVIEW_REQUIRED`** | Administrative metadata, automatic unit conversions, deterministic math scores | System Engine | Immediate persistence; status `SYSTEM_DERIVED` |
| **Tier 2: `STAFF_REVIEW_REQUIRED`** | Routine vital signs, normal outpatient lab scans, demographic updates | Staff Nurse / ANM | Nurse affirmation required before queue promotion |
| **Tier 3: `CLINICIAN_REVIEW_REQUIRED`** | Abnormal vitals, diagnostic notes, drug prescriptions, hospital admissions | RMP / Medical Officer | Primary RMP signature required under NMC Reg 27 |
| **Tier 4: `DUAL_REVIEW_REQUIRED`** | IV thrombolysis, blood transfusion cross-match, irreversible surgical consent | **Two Independent RMPs** | Asynchronous dual-physician verification workflow |

---

## 2. Resolving the Insert-Time Deadlock in Dual Review

### 2.1 The Architectural Flaw in Phase 7
In early Phase 7 conceptual drafts, `verification_events` for Tier 4 actions required both `verified_by_primary` and `verified_by_secondary` foreign keys to be non-null upon row insertion.

**The Resulting Deadlock:**
- When the primary emergency physician decides to administer IV Tenecteplase for an acute myocardial infarction, they must create the clinical order record.
- If the database schema enforces `NOT NULL` on both physician IDs at insertion, the primary physician's write fails because the second physician has not yet examined the patient or authenticated their session.
- The clinical workflow halts precisely when seconds count during emergency resuscitation.

### 2.2 The Asynchronous Dual-Review State Machine
CLINOVA resolves this deadlock by formalizing an **Asynchronous Dual-Review Lifecycle**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ASYNCHRONOUS DUAL-REVIEW LIFECYCLE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: PRIMARY ORDER CREATION ]                                         │
│  ├── Primary Clinician (RMP 1) enters high-risk order (e.g. IV Thrombolytic)│
│  ├── Database writes row with:                                              │
│  │   • primary_reviewer_id = RMP_1.id                                       │
│  │   • secondary_reviewer_id = NULL                                         │
│  │   • verification_status = 'PENDING_SECONDARY_REVIEW'                     │
│  └── Output: Order is NOT yet executable; flagged on nursing console        │
│                                  │                                          │
│                                  ▼ (System Emits Real-Time Alert)           │
│  [ STEP 2: SECONDARY REVIEWER INVITATION ]                                  │
│  ├── Push notification sent to secondary on-duty RMP (e.g. Senior MO / ED HOD)│
│  └── Displayed in "Pending Dual Review" panel on Doctor Workbench           │
│                                  │                                          │
│                                  ▼                                          │
│  [ STEP 3: INDEPENDENT CROSS-CHECK & ATTESTATION ]                          │
│  ├── Secondary Clinician (RMP 2) reviews clinical indication and contra-    │
│  │   indications independently                                              │
│  └── Submits independent verification transaction:                          │
│                                  │                                          │
│         ┌────────────────────────┴────────────────────────┐                 │
│         ▼                                                 ▼                 │
│  [ RMP 2 CONFIRMS ]                              [ RMP 2 REJECTS ]          │
│  • secondary_reviewer_id = RMP_2.id              • secondary_reviewer_id = RMP_2.id│
│  • status = 'VERIFIED'                           • status = 'REJECTED'      │
│  • Action unblocked for nursing execution        • Order cancelled; reason logged│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dual-Review Database Schema & Independence Invariants

```sql
-- Authoritative Schema for Asynchronous Dual-Review Events
CREATE TABLE dual_review_verifications (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    order_type VARCHAR(64) NOT NULL, -- e.g., 'IV_THROMBOLYSIS_STROKE', 'PRBC_TRANSFUSION'
    clinical_payload JSONB NOT NULL,
    primary_reviewer_id VARCHAR(36) NOT NULL REFERENCES users(id),
    primary_attested_at TIMESTAMPTZ NOT NULL,
    secondary_reviewer_id VARCHAR(36) REFERENCES users(id),
    secondary_attested_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_SECONDARY_REVIEW',
    rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Invariant DR-1: Primary and Secondary Reviewers MUST BE DISTINCT
    CONSTRAINT chk_dual_reviewers_distinct 
        CHECK (secondary_reviewer_id IS NULL OR primary_reviewer_id <> secondary_reviewer_id)
);
```

### Safety Invariants
1. **Distinct Actor Invariant ($\mathbf{Inv\ DR\text{-}1}$):** Under no circumstance may the secondary reviewer be the same user identity as the primary reviewer ($Reviewer_1 \neq Reviewer_2$).
2. **Role Qualification Invariant ($\mathbf{Inv\ DR\text{-}2}$):** Both actors must hold verified `CLINICIAN` roles with active National Medical Register (NMR) credentials.
3. **Execution Blocking Invariant ($\mathbf{Inv\ DR\text{-}3}$):** The Nurse Workstation hard-blocks barcode dispensing and administration confirmation until `status = 'VERIFIED'`.

---

## 4. Emergency Fallback & Single-Doctor Rural Exemption

In isolated Primary Health Centres during night shifts, **only one doctor may be physically on duty in the entire facility**.

### The Rural Emergency Single-Doctor Override Protocol
If a second RMP is physically unavailable during an acute life-threatening emergency (e.g. severe postpartum hemorrhage requiring uncrossed blood transfusion):
1. The on-duty RMP can invoke the **`RURAL_SINGLE_DOCTOR_OVERRIDE`** flag.
2. The system demands an explicit clinical justification (*"Sole Medical Officer on duty at PHC; immediate life threat"*).
3. The order executes with status `VERIFIED_SINGLE_DOCTOR_OVERRIDE`.
4. The event generates an automated high-priority audit dispatch to the District Chief Medical Officer (CMO) for mandatory post-incident retrospective review within 24 hours.
