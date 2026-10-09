# CLINOVA AI — Data Integrity Invariants & Constraints Specification

> **Document ID:** `RES-102`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Invariant-Driven Design

In clinical software systems, bugs are not mere user inconveniences; they cause misdiagnoses, delayed resuscitations, and patient mortality. To guarantee software correctness under extreme frontline pressures, CLINOVA AI is architected around **Twelve Inviolable Data Integrity Invariants**.

Every invariant is mathematically defined, enforced via database constraints and triggers, and audited for zero-violation compliance.

---

## 2. The Twelve Fundamental Invariants

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE TWELVE CLINOVA DATA INVARIANTS                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  INV-01: The Single Continuous Master Case Invariant                        │
│  INV-02: The Zero-Imputation Law (Epistemic Completeness)                   │
│  INV-03: Append-Only Event & Transition Immutability                        │
│  INV-04: Registered Medical Practitioner (RMP) Clinical Monopoly           │
│  INV-05: The Advisory-Only Artificial Intelligence Boundary                 │
│  INV-06: Continuous Epistemic Provenance & Attribution                      │
│  INV-07: Strict Orthogonal 3-Axis Clinical Decomposition                    │
│  INV-08: Non-Destructive Clinician Recommendation Overrides                 │
│  INV-09: Closed-Loop Referral & Anti-Blind-Transfer Integrity              │
│  INV-10: Auditable Break-Glass Emergency Escalation Privilege               │
│  INV-11: DPDP Act Consent Gate & Demographic PII Air-Gapping                │
│  INV-12: Idempotent Offline Synchronization & Zero ID Collisions            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical Formalization & Database Enforcement

### 3.1 Invariant 1: Single Continuous Master Case Invariant
- **Formal Statement:**
  $$\forall \text{ clinical encounter } e, \quad \exists ! \text{ canonical identifier } \mathbf{case\_id} \in \text{UUIDv4}$$
  $$\forall r \in \text{CareArtifacts}(e), \quad r.\text{case\_id} = \mathbf{case\_id}$$
- **DB Enforcement:** Foreign keys with `ON DELETE RESTRICT` linking all 17 sub-systems directly to `cases(id)`.
- **Violation Consequence:** Transaction aborted; zero orphan or sidecar records allowed.

### 3.2 Invariant 2: The Zero-Imputation Law
- **Formal Statement:**
  $$\text{Absence of evidence } \neq \text{ Evidence of absence}$$
  $$\forall p \in \text{ClinicalParameters}, \quad \text{IsMissing}(p) \implies p.\text{epistemic\_status} = \text{'UNKNOWN'} \land p.\text{value} = \text{NULL}$$
- **DB Enforcement:** Check constraints prohibiting automatic default values for physiological measurements (`systolic_bp`, `spo2`, `heart_rate`).

### 3.3 Invariant 3: Append-Only Event Immutability
- **Formal Statement:**
  $$\forall e \in \text{CaseEvents}, \quad \text{Op}(e) \in \{\text{INSERT}\} \quad \land \quad \text{Op}(e) \notin \{\text{UPDATE}, \text{DELETE}\}$$
  $$H_n = \text{SHA256}(H_{n-1} \parallel e_n.\text{id} \parallel e_n.\text{timestamp} \parallel e_n.\text{payload})$$
- **DB Enforcement:** Database-level trigger blocking `UPDATE` or `DELETE` on `case_events` and `case_state_transitions`.

### 3.4 Invariant 4: RMP Clinical Monopoly
- **Formal Statement:**
  $$\forall d \in \text{ClinicalDispositions}, \quad \text{User}(d.\text{actor\_id}).\text{role} = \text{'ROLE\_CLINICIAN'}$$
- **DB Enforcement:** Check constraint and FK join verifying `users.role = 'ROLE_CLINICIAN'` on `clinician_reviews` and `clinician_orders`.

### 3.5 Invariant 5: Advisory-Only AI Boundary
- **Formal Statement:**
  $$\forall o \in \text{OrchestrationRecommendations}, \quad o.\text{human\_review\_required} = \text{TRUE}$$
- **DB Enforcement:** `CHECK (human_review_required = TRUE)` hardcoded in table DDL.

### 3.6 Invariant 6: Continuous Epistemic Provenance
- **Formal Statement:**
  $$\forall f \in \text{ClinicalFacts}, \quad f.\text{source\_type} \neq \text{NULL} \land f.\text{confidence\_score} \in [0.0, 1.0] \land f.\text{recorded\_by} \neq \text{NULL}$$
- **DB Enforcement:** `NOT NULL` constraints on `source_type`, `confidence_score`, and `recorded_by_actor_id` in `evidence_records`.

### 3.7 Invariant 7: Strict 3-Axis Clinical Decomposition
- **Formal Statement:**
  $$\mathcal{E} = \langle \text{RiskLevel}, \text{TrajectorySlope}, \text{UncertaintyScore} \rangle \in \mathcal{R} \times \mathcal{T} \times \mathcal{U}$$
  $$\frac{\partial \text{Risk}}{\partial \text{Uncertainty}} = 0 \quad \text{(Orthogonal Axes)}$$
- **DB Enforcement:** Separate non-overlapping columns in `clinical_evaluations` with independent check constraints.

### 3.8 Invariant 8: Non-Destructive Recommendation Overrides
- **Formal Statement:**
  $$\forall m \in \text{Modifications}, \quad m.\text{original\_value} = \text{Snapshot}_{\text{pre}}(f) \land m.\text{new\_value} = \text{Value}_{\text{post}}(f)$$
- **DB Enforcement:** `clinician_modifications` table mandates both `original_value` and `new_value` alongside `clinical_justification`.

### 3.9 Invariant 9: Closed-Loop Referral Integrity
- **Formal Statement:**
  $$\forall r \in \text{Referrals}, \quad r.\text{referring\_facility\_id} \neq r.\text{destination\_facility\_id} \land r.\text{clinical\_summary\_pack} \neq \text{NULL}$$
- **DB Enforcement:** Table check constraint ensuring distinct originating and destination facility IDs.

### 3.10 Invariant 10: Auditable Break-Glass Emergency Escalation
- **Formal Statement:**
  $$\forall t \in \text{Transitions}, \quad t.\text{trigger} = \text{'BREAK\_GLASS\_EMERGENCY'} \implies \exists ! a \in \text{AuditLedger} \text{ s.t. } a.\text{case\_id} = t.\text{case\_id}$$
- **DB Enforcement:** Atomic transaction trigger logging `privacy_break_glass_audits` upon emergency transition invocation.

### 3.11 Invariant 11: DPDP Consent & Demographic Air-Gap
- **Formal Statement:**
  $$c.\text{intake\_mode} = \text{'REGULAR'} \implies \text{HasConsent}(c, \text{'INTAKE'}) = \text{TRUE}$$
  $$\text{Payload}(\text{SLM\_Inference}) \cap \text{DemographicPII} = \emptyset$$
- **DB Enforcement:** Foreign key and state machine transition guards checking `patient_consents.is_active = TRUE`.

### 3.12 Invariant 12: Idempotent Offline Synchronization
- **Formal Statement:**
  $$\forall e_1, e_2 \in \text{Entities}, \quad e_1.\text{id} = e_2.\text{id} \implies e_1 = e_2 \quad (\text{UUIDv4 Collision Probability } < 10^{-15})$$
- **DB Enforcement:** Universal UUIDv4 primary keys and append-only sync journal matching on `(entity_type, entity_id)`.
