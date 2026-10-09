# CLINOVA AI — Master Case Architecture & Lifecycle Specification

> **Document ID:** `RES-139`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Healthcare Data Modeling Group  

---

## 1. The Single Master Case Invariant

In conventional hospital systems, clinical records suffer from severe structural fragmentation: triage forms exist as temporary paper slips, vital signs are locked in nursing charts, doctor notes sit in electronic records, and referral letters are drafted in separate portals.

CLINOVA AI eliminates this fragmentation through the **Single Master Case Invariant**:

$$\forall \text{ clinical encounter } e, \quad \exists ! \text{ canonical entity } \mathbf{cases} \text{ identified by } \mathbf{case\_id} \in \text{UUIDv4}$$

The Master Case (`cases`) serves as the root relational aggregate and operational anchor for the patient's entire clinical episode. Every clinical observation, raw audio recording, OCR bounding box, triage evaluation, doctor review, facility evaluation, and referral document must link directly to `cases.id` via an indexed foreign key with `ON DELETE RESTRICT`.

**Anti-Fragmentation Guarantee:** No subsystem, AI adapter, or background worker may create a sidecar encounter or disconnected patient record. All data generated during an episode joins the single continuous Master Case.

---

## 2. Complete Master Case Dependency Graph

```
                            ┌────────────────────────┐
                            │      cases (Root)      │
                            │  id (UUIDv4, PK)       │
                            │  case_number (Unique)  │
                            │  status (S01 - S27)    │
                            │  state_version (Int)   │
                            │  acuity_tier (Enum)    │
                            │  risk_score (Float)    │
                            │  trajectory (Float)    │
                            │  uncertainty (Float)   │
                            └───────────┬────────────┘
                                        │
        ┌───────────────────────────────┼──────────────────────────────┐
        │                               │                              │
        ▼                               ▼                              ▼
┌──────────────┐                ┌──────────────┐               ┌──────────────┐
│  encounters  │                │   patients   │               │  facilities  │
│  (Episode)   │                │  (Identity)  │               │ (Origin Site)│
└──────────────┘                └──────────────┘               └──────────────┘
        │                               │                              │
        ├───────────────────────────────┴──────────────────────────────┤
        │
        ├──► evidence_records        (8 source classes; normalized payloads)
        │     └──► evidence_conflicts (Discordant values linked for RMP review)
        ├──► raw_evidence_sources    (Physical file URIs, SHA-256 hashes, offsets)
        ├──► vital_readings          (Serial physiological vitals: HR, BP, SpO2, RR)
        ├──► clinical_observations   (LOINC/SNOMED discrete lab & exam findings)
        ├──► symptoms                (Longitudinal trajectories & progression events)
        ├──► missing_information    (Zero-imputation items: UNKNOWN qualifiers)
        ├──► followup_questions     (NBI clarifying sessions & answers)
        ├──► caregraph_states        (Computed risk, slope & uncertainty projections)
        ├──► triage_evaluations      (Deterministic NEWS2, Shock Index, Acuity Tiers)
        ├──► clinician_decisions     (RMP reviews, overrides & sign-off events)
        ├──► facility_evaluations    (Resource feasibility & golden hour checks)
        ├──► orchestrations          (Candidate actions: ASK, VERIFY, CONTINUE...)
        ├──► referrals               (Capability-matched transfer packs & SBAR)
        ├──► ward_admissions         (Inpatient bed allocation & clinical handoffs)
        ├──► ot_handoffs             (Emergency surgical alerts & checklist sign-offs)
        ├──► case_outcomes           (Final discharge, recovery & follow-up loops)
        └──► case_events             (Append-only Merkle-linked audit ledger)
```

---

## 3. The 27-State Canonical Lifecycle State Machine

The Master Case transitions through **twenty-seven explicit, mutually exclusive states** categorized across six longitudinal care epochs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    27 CANONICAL MASTER CASE STATES (S01–S27)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ EPOCH 1: ARRIVAL & INTAKE ]                                              │
│  • S01: STATE_NEW                      (Arrival registered / ticket issued) │
│  • S02: STATE_INTAKE_COLLECTING        (Multimodal data capture active)     │
│  • S03: STATE_EXTRACTING               (OCR and speech processing running)  │
│  • S04: STATE_EXTRACTION_REVIEW        (Draft transcription & text ready)   │
│                                                                             │
│  [ EPOCH 2: DATA COMPLETION & TRIAGE PREPARATION ]                          │
│  • S05: STATE_MISSING_AUDIT            (Zero-imputation gap audit underway) │
│  • S06: STATE_FOLLOW_UP_PENDING        (NBI questions presented to patient) │
│  • S07: STATE_STAFF_DATA_PENDING       (Awaiting bedside nurse vital signs) │
│  • S08: STATE_STAFF_VERIFIED           (Vitals & physical measurements done)│
│  • S09: STATE_CONSOLIDATED             (Sufficiency score S >= 0.85 reached)│
│  • S10: STATE_TRIAGE_READY             (Deterministic early warning scored) │
│                                                                             │
│  [ EPOCH 3: WAITING & CLINICIAN REVIEW ]                                    │
│  • S11: STATE_DOCTOR_QUEUED            (Placed in active prioritized queue) │
│  • S12: STATE_DOCTOR_REVIEWING         (Active on doctor workbench screen)  │
│  • S13: STATE_CLINICIAN_VERIFIED       (RMP attested facts & exam findings) │
│                                                                             │
│  [ EPOCH 4: FACILITY FEASIBILITY & ORCHESTRATION ]                          │
│  • S14: STATE_FACILITY_EVALUATING      (Checking local beds & capabilities) │
│  • S15: STATE_ORCHESTRATION_PENDING    (Synthesizing safest care pathway)   │
│                                                                             │
│  [ EPOCH 5: CLINICAL PATHWAY EXECUTION ]                                    │
│  • S16: STATE_ROUTINE_CARE             (Outpatient prescription & advice)   │
│  • S17: STATE_FURTHER_REVIEW           (Observation ward / serial repeat)   │
│  • S18: STATE_WARD_REQUESTED           (Inpatient admission requested)      │
│  • S19: STATE_WARD_ADMITTED            (Transferred to inpatient ward bed)  │
│  • S20: STATE_REFERRAL_PENDING         (Capability-matched transfer prep)   │
│  • S21: STATE_TRANSFER_IN_TRANSIT      (Dispatched in ambulance)            │
│  • S22: STATE_EMERGENCY_ACTIVE         (Resuscitation room code activated)  │
│  • S23: STATE_OT_PENDING               (Emergency surgical prep initiated)  │
│  • S24: STATE_OT_HANDOFF               (Surgical team handoff signed off)   │
│                                                                             │
│  [ EPOCH 6: CONTINUITY, OUTCOME & CLOSING ]                                 │
│  • S25: STATE_OUTCOME_PENDING          (Discharge / transfer review)        │
│  • S26: STATE_RESOLVED                 (Clinical disposition finalized)     │
│  • S27: STATE_CLOSED                   (Episode sealed; records archived)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. State Transition Governance & Optimistic Concurrency Control

To guarantee transactional consistency under concurrent updates (e.g., a nurse entering vitals while an OCR job completes):

1. **State Versioning:** Every row in `cases` maintains an integer column `state_version` (starting at `1`).
2. **Optimistic Concurrency Control (OCC):** State mutations require an atomic compare-and-swap update:
   ```sql
   UPDATE cases
   SET status = :new_state,
       state_version = state_version + 1,
       updated_at = :utc_now
   WHERE id = :case_id AND state_version = :expected_version;
   ```
   If the update affects 0 rows, a `ConcurrentModificationError` is raised, forcing the caller to reload the latest state before retrying.
3. **State Transition Ledger:** Every transition writes an immutable row into `case_state_transitions` capturing `case_id`, `from_state`, `to_state`, `trigger_event`, `actor_id`, and `duration_seconds`.

---

## 5. Architectural Reconciliation: `triage_cases` vs. Canonical `cases`

### 5.1 Analysis of Codebase Divergence
- **Historical Alembic Migrations:** Earlier development migrations (`0001_initial`, `0002_clinical_data`, `0004`, `0005`, `0007`, `0008`, `0009`) created and referenced a table named `triage_cases`.
- **Approved Specifications:** Phase 6 canonical model (`RES-79`) and `backend/app/db/models.py` define the canonical entity as `cases`.
- **Root Cause:** Early prototypes viewed the platform as a narrow "triage tool." As the system evolved into **Continuous Care Intelligence**, the domain scope expanded across the full clinical journey, rendering the name `triage_cases` semantically misleading and restrictive.

### 5.2 Definitive Architectural Resolution
1. **Single Canonical Table:** The architecture formally designates `cases` as the **sole canonical table** for CLINOVA AI.
2. **Phase 9 Migration Roadmap:**
   - In Phase 9, an Alembic migration will execute `ALTER TABLE triage_cases RENAME TO cases;`.
   - Update foreign key constraint names to point to `cases.id`.
   - Create a backward-compatible database view:
     ```sql
     CREATE VIEW v_legacy_triage_cases AS SELECT * FROM cases;
     ```
   - This ensures zero downtime and absolute compatibility for any legacy endpoints while standardizing all new domain models, foreign keys, and documentation on `cases`.
