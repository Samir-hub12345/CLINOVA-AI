# CLINOVA AI — Clinical Case State Machine Model

> **Document ID:** `DOC-07`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. State Machine Overview

Clinical encounters do not follow a naive, linear progression. Patients deteriorate, tests fail, data is missing or contradictory, receiving facilities experience sudden bed shortages, and follow-ups are delayed. 

The CLINOVA AI clinical state model rigorously tracks the lifecycle of every patient encounter through a deterministic Finite State Machine (FSM) that guarantees strict human-in-the-loop oversight and robust exception handling.

---

## 2. State Topology & Transition Diagram

```
                             ┌──────────────┐
                             │     NEW      │
                             └──────┬───────┘
                                    │ (Begin Intake)
                                    ▼
                             ┌──────────────┐
                  ┌─────────>│    INTAKE    │
                  │          └──────┬───────┘
                  │                 │ (Submit Payload)
                  │                 ▼
                  │          ┌──────────────┐  (Parsing Fail)   ┌───────────────────┐
                  │          │  PROCESSING  │──────────────────>│ PROCESSING_FAILED │
                  │          └──────┬───────┘                   └───────────────────┘
                  │                 │ (Entities Extracted)
                  │                 ▼
                  │          ┌─────────────────┐  (Critical Gap) ┌───────────────────┐
                  │          │ REVIEW_REQUIRED │────────────────>│ INSUFFICIENT_DATA │
                  │          └──────┬──────────┘                 └─────────┬─────────┘
                  │                 │ (Data Sufficient)                    │
                  │                 ▼                                      ▼
                  │          ┌──────────────┐  (Vital Mismatch)  ┌───────────────────┐
                  │          │   TRIAGED    │───────────────────>│ CONFLICTING_DATA  │
                  │          └──────┬───────┘                    └─────────┬─────────┘
                  │                 │ (Assigned to Queue)                  │
                  │                 ▼                                      ▼
                  │          ┌──────────────────┐               (Prompt / Follow-up)
                  │          │ CLINICIAN_REVIEW │<─────────────────────────┘
                  │          └──────┬───────────┘
                  │                 │ (Clinician Decides)
                  │                 ▼
                  │          ┌──────────────┐
                  │          │   DECISION   │
                  │          └──────┬───────┘
                  │                 │
      ┌───────────┴──────────┬──────┴───────────────┬────────────────┐
      ▼                      ▼                      ▼                ▼
┌───────────┐          ┌───────────┐          ┌───────────┐    ┌───────────┐
│ CONTINUE  │          │  OBSERVE  │          │ ESCALATE  │    │   REFER   │
└─────┬─────┘          └─────┬─────┘          └─────┬─────┘    └─────┬─────┘
      │                      │ (Repeat Vitals)      │                │ (Dispatch)
      │                      └───────┬──────────────┘                ▼
      │                              │                     ┌──────────────────┐
      │                              │                     │ TRANSFER_PENDING │
      │                              │                     └─────────┬────────┘
      │                              │                               │ (Arrive / Reject)
      │                              │                    ┌──────────┴──────────┐
      │                              │                    ▼                     ▼
      │                              │          ┌─────────────────┐   ┌─────────────────┐
      │                              │          │    TRANSFER     │   │ REFERRAL_FAILED │
      │                              │          └────────┬────────┘   └─────────────────┘
      │                              │                   │
      ▼                              ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                          COMPLETED                          │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Record Disposition & Outcome)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                           OUTCOME                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Primary State Definitions

| State Name | Clinical Context | Invariants & Exit Preconditions |
| :--- | :--- | :--- |
| `NEW` | Case identifier initialized; awaiting patient arrival or intake session. | Zero clinical data stored; consent record not yet attached. |
| `INTAKE` | Multimodal input being collected (voice narrative, text, report uploads). | Consent must be verified before proceeding. Direct PII scrubbed. |
| `PROCESSING` | Audio transcription, OCR extraction, and clinical entity parsing executing. | Transient state (`< 5s`); transitions automatically to review or failure. |
| `REVIEW_REQUIRED`| Extraction complete; system checks for critical missing information or red flags. | Flags generated if high-risk parameters missing; uncertainty calculated. |
| `TRIAGED` | Acuity tier assigned (Routine, Moderate, Urgent, Critical); placed in clinical queue. | Case assigned to department waitlist with priority score and SLA timer. |
| `CLINICIAN_REVIEW`| Case open on qualified medical officer's workstation for interactive review. | Human clinician authenticated; CareGraph, evidence, and suggestions visible. |
| `DECISION` | Clinician has chosen an action (or override) and attached their digital sign-off. | Requires explicit clinician authentication token and decision timestamp. |
| `CONTINUE` | Low-risk patient maintained on existing ambulatory care or routine workup. | Case proceeds to routine care delivery. |
| `OBSERVE` | Patient placed in holding bed for serial vitals and dynamic trajectory monitoring. | Scheduled repeat vitals trigger CareGraph re-evaluation at interval. |
| `ESCALATE` | Immediate bedside intervention or resuscitation team dispatched. | High priority emergency alert pushed to department staff. |
| `REFER` | Inter-facility transfer indicated; destination capability matching initiated. | Bundles CareGraph state into standardized SBAR transfer packet. |
| `TRANSFER_PENDING`| SBAR sent to destination facility; ambulance transport coordinating. | Destination bed confirmed or pending response. |
| `TRANSFER` | Patient dispatched and in transit; handoff protocol active. | Ambulance team updates vital telemetry in transit if connected. |
| `COMPLETED` | Clinical encounter concluded (discharged, transferred, or admitted). | All required clinical notes signed; pending actions cleared. |
| `OUTCOME` | Final patient disposition and health outcome recorded. | Feeds SignalGraph aggregate telemetry and updates audit logs. |

---

## 4. Exception & Failure State Definitions

| Exception State | Trigger Condition | System Behavior & Recovery Pathway |
| :--- | :--- | :--- |
| `PROCESSING_FAILED` | Audio/file parsing crash or corrupt format. | Prompts user to retry or switch immediately to manual structured text entry. |
| `OCR_FAILED` | Smudged/unreadable image or OCR model failure. | Retains raw image; prompts intake nurse for manual key-value vital sign entry. |
| `INSUFFICIENT_DATA`| Core protocol data absent (e.g., chest pain without duration or character). | System generates targeted follow-up questions (`ASK` action) to prompt nurse. |
| `CONFLICTING_DATA` | Contradictory clinical evidence (e.g., documented "no distress" with HR 148). | Flags discrepancy badge (`VERIFY` action) requiring clinician reconciliation. |
| `REFERRAL_FAILED` | Destination hospital rejects transfer or lacks ICU beds at arrival. | System instantly re-queries FacilityGraph for next-best capable alternative facility. |
| `FOLLOW_UP_MISSED` | Serial vitals not captured within designated observation window. | High-priority reminder pushed to triage nurse and supervising medical officer. |

---

## 5. State Transition Guard Rules

1. **The Human Gate Invariant:** A case cannot transition from `CLINICIAN_REVIEW` to any action state (`CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`) without an authenticated clinician credential.
2. **The Consent Invariant:** A case cannot transition from `NEW` to `PROCESSING` without `consent_recorded == True`.
3. **The Data Integrity Invariant:** A case cannot transition to `OUTCOME` without all pending verification flags either accepted, rejected, or overridden with notes.
