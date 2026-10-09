# CLINOVA AI — Master Patient Journey Specification

> **Document ID:** `RES-58`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary

The **CLINOVA Master Patient Journey** defines the complete end-to-end trajectory of a patient encounter from the moment of clinical presentation to long-term outcome resolution. 

Unlike conventional emergency department software or telemedicine portals that treat "triage" as an isolated, transactional sorting event, CLINOVA models the patient journey as a **continuous, stateful, evidence-grounded, and human-governed clinical trajectory**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE CLINOVA MASTER CARE CONTINUUM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ INGESTION ] ──> [ REFINEMENT ] ──> [ VERIFICATION ] ──> [ SYNTHESIS ]  │
│   Multimodal        Sufficiency &      Frontline Nurse      CAREGRAPH &     │
│   Intake            Audit Checklist    Point-of-Care Vitals Risk Vector     │
│          │                                                        │         │
│          ▼                                                        ▼         │
│   [ OUTCOME LOOP ] <── [ CONTINUATION ] <── [ ORCHESTRATION ] <── [ REVIEW ]│
│   Recovery / Delta     Ward / Referral /    Resource-Aware        Doctor    │
│   SIGNALGRAPH Feed     OT / Routine Path    Care Navigation       Verify/Add│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Operational Principles

The journey is anchored by five inviolable operational principles:

1. **One Master Case Invariant:**  
   Every patient interaction within an encounter belongs to exactly one `MasterCase` instance. No auxiliary desk, triage point, nursing bay, ward, or referral coordinator may generate a separate, unlinked case.
2. **Dual-Track Entry Decoupling:**  
   The initial presentation immediately branches into either the **Regular / Routine Pathway** or the **Emergency Fast-Track Pathway**. Emergency cases are never forced through standard multimodal intake before life-saving stabilization begins.
3. **Dynamic Acuity Escalation:**  
   A case originating in the regular workflow can escalate dynamically to the emergency pathway at *any* intermediate state (e.g., patient collapses during voice intake, SpO2 drops to 78% during nurse vitals check, or doctor identifies acute peritonitis on palpation).
4. **Multiple Human Handoffs, One Cryptographic Audit Trail:**  
   As care transfers from patient/caregiver to frontline health worker, to triage nurse, to attending medical officer, to ward sister, to transport team, and to receiving facility clinician, every handoff is explicitly recorded with actor ID, timestamp, and verification sign-off.
5. **Closed-Loop Outcome Accountability:**  
   Care does not terminate upon doctor sign-off or referral dispatch. The journey explicitly tracks patient arrival, ward admission, surgical procedure completion, recovery status, and follow-up compliance, feeding real-world clinical endpoints back into the system intelligence layer.

---

## 3. Global End-to-End Master Journey Flowchart

```
                                  [ NEW ENCOUNTER ]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  │                                               │
                  ▼                                               ▼
       [ REGULAR ENTRY TRACK ]                         [ EMERGENCY FAST-TRACK ]
                  │                                               │
                  ▼                                               │
      Multimodal Data Collection                                  │
    (Vernacular Voice, Text, OCR)                                 │
                  │                                               │
                  ▼                                               │
     Extraction & Entity Structuring                              │
                  │                                               │
                  ▼                                               │
      Visual Extraction Review                                    │
                  │                                               │
                  ▼                                               │
       Timeline Construction                                      │
                  │                                               │
                  ▼                                               │
     Missing Information Audit                                    │
                  │                                               │
                  ▼                                               │
      Follow-up Question Engine                                   │
                  │                                               │
                  ▼                                               │
     [ SUFFICIENCY EVALUATION ]                                   │
                  │                                               │
         ┌────────┴────────┐                                      │
         ▼                 ▼                                      │
   [ SUFFICIENT ]   [ INSUFFICIENT ]                              │
         │                 │                                      │
         │                 ▼                                      │
         │          Staff Worklist                                │
         │                 │                                      │
         │                 ▼                                      │
         │          Missing-Data &                                │
         │       Point-of-Care Vitals                             │
         │                 │                                      │
         │                 ▼                                      │
         │          Staff Sign-Off                                │
         │                 │                                      │
         └────────┬────────┘                                      │
                  ▼                                               ▼
         Data Consolidation                             [ DYNAMIC ESCALATION ]
                  │                                       (At any point if
                  ▼                                        red-flags trigger)
          CAREGRAPH Engine                                        │
     (State, Risk, Trajectory,                                    ▼
       Uncertainty Calculus)                            Rapid ABCD Vitals
                  │                                     Emergency Checklist
                  ▼                                     Deterministic Rules
        Structured Triage Note                                    │
                  │                                               ▼
        Master Clinical Report                          Immediate Resuscitation
                  │                                               │
                  ▼                                               ▼
         Doctor Dynamic Queue                           Emergency FACILITYGRAPH
                  │                                               │
                  ▼                                               ▼
          Doctor Comprehensive                          Emergency Disposition:
              Case Review                               • Resuscitation Bay
                  │                                     • Emergency OT
                  ▼                                     • Critical Transfer
          Doctor Action Gate:                                     │
         VERIFY / MODIFY / ADD                                    │
                  │                                               │
                  ▼                                               │
          FACILITYGRAPH &                                         │
          Care Feasibility                                        │
                  │                                               │
                  ▼                                               │
         ORCHESTRATION Engine                                     │
           Advisory Guidance                                      │
                  │                                               │
                  ▼                                               │
     [ CLINICIAN DISPOSITION GATE ]                               │
                  │                                               │
   ┌──────────────┼──────────────┬──────────────┬─────────────────┤
   ▼              ▼              ▼              ▼                 ▼
[PATHWAY A]    [PATHWAY B]    [PATHWAY C]    [PATHWAY D]      [PATHWAY E]
 ROUTINE /       FURTHER        INPATIENT       INTER-         EMERGENCY /
 HOME CARE       REVIEW           WARD         FACILITY         SURGICAL
  CALENDAR      REVISIT        ADMISSION       REFERRAL            OT
   FOLLOW         SLOT          HANDOFF        TRANSFER         HANDOFF
     │              │              │              │                │
     └──────────────┼──────────────┴──────────────┴────────────────┘
                    ▼
          [ CONTINUATION OF CARE ]
                    │
                    ▼
          [ OUTCOME RECORDING ]
    (Full Recovery, Stabilized, Referred,
     Complication Managed, Adverse Event)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   CAREGRAPH Update     SIGNALGRAPH Update
  (Individual Delta)   (Macro Telemetry)
         │                     │
         └──────────┬──────────┘
                    ▼
            [ ENCOUNTER CLOSED ]
```

---

## 4. Multi-Actor Clinical Handoff Continuum

Clinical care is collaborative. CLINOVA models the explicit transitions between distinct human actors, preserving the evidentiary chain of custody across every node:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ACTOR HANDOFF CHAIN OF CUSTODY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ ACTOR 1: PATIENT / CAREGIVER / ASHA ]                                    │
│  • Initiates encounter; inputs vernacular voice / mobile text / paper slips.│
│  • Holds provenance tag: `PATIENT_REPORTED`.                                │
│                                                                             │
│         │ HANDOFF 1: Physical Arrival / Triage Desk Check-in                │
│         ▼                                                                   │
│                                                                             │
│  [ ACTOR 2: FRONTLINE NURSE / HEALTH WORKER ]                               │
│  • Receives missing data worklist; measures BP, HR, SpO2, Temp, RR.         │
│  • Verifies patient identity; signs off point-of-care checklist.            │
│  • Holds provenance tag: `STAFF_VERIFIED`.                                  │
│                                                                             │
│         │ HANDOFF 2: Dynamic Queue Promotion to Doctor OPD Bay              │
│         ▼                                                                   │
│                                                                             │
│  [ ACTOR 3: REGISTERED MEDICAL PRACTITIONER (CLINICIAN) ]                   │
│  • Reviews multimodal evidence, CAREGRAPH trajectory, and uncertainty.     │
│  • Performs physical examination; executes `VERIFY`, `MODIFY`, `ADD`.       │
│  • Reviews FACILITYGRAPH feasibility; approves clinical disposition.        │
│  • Holds provenance tag: `CLINICIAN_APPROVED`.                              │
│                                                                             │
│         │ HANDOFF 3: Formal Disposition Execution                           │
│         ├──────────────────────────────┬─────────────────────────────┐      │
│         ▼                              ▼                             ▼      │
│  [ WARD NURSE ]             [ AMBULANCE / EMS ]           [ OT SCRUB / ANES ]│
│  • Inpatient Bed Sign-in    • Transport Manifest          • WHO Sign In      │
│  • SBAR Intake Sign-off     • En-route Vitals             • Surgical Timeout │
│                                                                             │
│         │                              │                             │      │
│         └──────────────────────────────┼─────────────────────────────┘      │
│                                        ▼                                    │
│  [ ACTOR 4: RECEIVING CLINICIAN / WARD ATTENDING ]                          │
│  • Completes clinical continuation; logs real-world outcome endpoint.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Journey Invariants Across All Operating Environments

Regardless of whether CLINOVA executes in a high-volume District Hospital (`ENV_GOV_HOSPITAL`), a remote rural sub-centre (`ENV_PHC`), a makeshift outreach tent (`ENV_PUBLIC_CAMP`), or a factory medical room (`ENV_INDUSTRIAL_HEALTH`), the following six journey invariants remain non-negotiable:

1. **Deterministic Red-Flag Priority:**  
   Physiological instability ($\text{SpO}_2 < 85\%$, $\text{Shock Index} > 1.0$, pediatric stridor, severe hemorrhage) overrides all non-emergency UI sequences instantly.
2. **Human Monopolies:**  
   AI models and deterministic rule engines cannot authorize prescriptions, order surgeries, sign ward admissions, or dispatch inter-facility referrals.
3. **No Phantom Imputation:**  
   The journey explicitly surfaces missing parameters as `UNKNOWN`. At no stage does the system hallucinate or impute negative values for missing clinical tests.
4. **Immutable Audit Persistence:**  
   Every state change, data modification, clinician override, and actor login is written to an append-only audit trail with UTC timestamp and SHA-256 integrity hash.
5. **Decoupled Local Execution:**  
   All journey stages from intake to clinician sign-off can function over an isolated Local Area Network (LAN) without external cloud dependencies.
6. **Provenance Traceability:**  
   Every extracted clinical entity displayed to the physician must provide immediate visual traceability to its underlying raw input source (audio crop, OCR snippet, or manual entry).

---

## 6. Structural Synthesis

The CLINOVA Master Patient Journey bridges the gap between chaotic real-world clinical presentations and structured digital care navigation. By enforcing stateful transitions, explicit handoff checkpoints, mathematical sufficiency audits, and resource-aware routing, the platform transforms fragmented frontline encounters into a coordinated, accountable continuum of care.
