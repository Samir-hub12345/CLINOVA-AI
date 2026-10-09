# CLINOVA AI — Multi-Graph Orchestration & Advisory Architecture

> **Document ID:** `RES-143`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Decision Support Engineering Group  

---

## 1. Multi-Graph Orchestration Synthesis Engine

The core clinical differentiator of CLINOVA AI is moving beyond isolated algorithmic triage into **Multi-Graph Clinical Orchestration**.

The Orchestration Engine continuously synthesizes six distinct operational inputs into a unified clinical guidance vector:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MULTI-GRAPH ORCHESTRATION SYNTHESIS                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. CAREGRAPH        ──► Physiological Risk (R_t) & Trajectory Slope       │
│   2. EVIDENCE         ──► Verified Facts, LOINC Labs & Visual Bounding Boxes│
│   3. UNCERTAINTY      ──► Epistemic Gaps (U_t), Data Conflicts & Stale Data │
│   4. FACILITYGRAPH    ──► Local & Regional Beds, Equipment & Specialists    │
│   5. ENVIRONMENT      ──► Operational Context (PHC, Gov Hospital, Camp)     │
│   6. SIGNALGRAPH      ──► Local Epidemiologic Surges & ED Bottlenecks       │
│                                  │                                          │
│                                  ▼                                          │
│             ┌──────────────────────────────────────────┐                    │
│             │   CLINOVA ORCHESTRATION SYNTHESIS CORE   │                    │
│             └────────────────────┬─────────────────────┘                    │
│                                  │                                          │
│                                  ▼                                          │
│                  SIX CANONICAL CANDIDATE ACTIONS                            │
│                  ┌──────────────────────────────┐                           │
│                  │  1. ASK       (Targeted gap) │                           │
│                  │  2. VERIFY    (Nurse checks) │                           │
│                  │  3. CONTINUE  (Routine care) │                           │
│                  │  4. OBSERVE   (Serial vitals)│                           │
│                  │  5. ESCALATE  (Emergency code)                           │
│                  │  6. REFER     (Matched xfer) │                           │
│                  └──────────────────────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Six Canonical Candidate Actions

1. **`ASK` (Targeted Information Acquisition):**
   - *Trigger:* High epistemic uncertainty ($U_t > 0.40$) with missing Tier 2 clinical qualifiers, but stable physiological vitals.
   - *Action:* Recommends presenting 1–3 high-yield Next-Best Information (NBI) questions to patient or caregiver.
2. **`VERIFY` (Bedside Verification):**
   - *Trigger:* Active evidence conflict (e.g., patient claims BP 120 vs OCR scan reading 190), or unverified abnormal vital sign.
   - *Action:* Prompts bedside nurse or ASHA worker for an immediate manual physical re-measurement.
3. **`CONTINUE` (Routine Clinical Care Pathway):**
   - *Trigger:* Low risk ($R_t < 0.20$), stable trajectory, low uncertainty ($U_t < 0.20$), and full local facility capability.
   - *Action:* Recommends routine outpatient consultation, standard prescription drafting, and follow-up advice.
4. **`OBSERVE` (Serial Observation & Trajectory Tracking):**
   - *Trigger:* Moderate risk ($0.20 \le R_t < 0.50$), borderline vitals (e.g. HR 105, BP 100/65), or fluctuating trajectory.
   - *Action:* Places patient in Day Observation / Holding Ward with scheduled serial vital checks every 30 minutes.
5. **`ESCALATE` (Immediate Resuscitation Escalation):**
   - *Trigger:* High physiological risk ($R_t \ge 0.50$), rapid deterioration ($\text{Slope} > +0.25$), Shock Index $> 0.9$, or clinical red flag.
   - *Action:* Activates Emergency Casualty Code, sounds visual alarm on Doctor Workbench, and alerts resuscitation team.
6. **`REFER` (Capability-Matched Inter-Facility Transfer):**
   - *Trigger:* Patient requires a clinical care bundle ($B_{\text{req}}$) exceeding local operational capabilities (e.g., acute STEMI at a rural PHC).
   - *Action:* Invokes FACILITYGRAPH to match nearest capable hospital within the golden hour, drafts an SBAR transfer pack, and notifies receiving hospital.

---

## 3. Advisory Recommendation Object Schema

The Orchestration Engine outputs a strictly typed JSON object adhering to Pydantic and TypeScript validation:

```json
{
  "recommendation_id": "rec-550e8400-e29b-41d4-a716-446655440000",
  "case_id": "cas-2026-001042",
  "generated_at": "2026-10-08T10:45:00.000Z",
  "primary_action": "REFER",
  "secondary_action": "OBSERVE",
  "urgency_tier": "CRITICAL",
  "clinical_rationale": "Patient presents with acute ischemic stroke syndrome (FAST positive, symptom onset 90 min ago). Local PHC lacks CT scanner and thrombolytic agents. Nearest capable tertiary facility has operational CT and available stroke bed.",
  "required_bundle": ["CT_SCAN_24_7", "THROMBOLYSIS_TPA", "ICU_NEURO_BED"],
  "facility_feasibility": {
    "local_can_manage": false,
    "recommended_destination_id": "fac-dh-koraput-01",
    "destination_name": "District Hospital Koraput",
    "distance_km": 34.2,
    "estimated_transit_minutes": 42,
    "golden_hour_status": "WITHIN_WINDOW"
  },
  "safety_disclaimer": "Advisory recommendation only. Requires immediate human review and signed medical officer authorization before dispatch."
}
```

---

## 4. Absolute Human-in-the-Loop Boundaries under NMC Regulations 2023

Under National Medical Commission (NMC) Registered Medical Practitioner Regulations 2023 (Regulation 27), the system enforces ironclad architectural tripwires:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE HUMAN CLINICIAN MONOPOLY BOUNDARY                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT THE SYSTEM CAN DO (Advisory):                                        │
│   ✅ Generate structured SBAR referral pack drafts                          │
│   ✅ Suggest safest achievable care pathway based on resource feasibility   │
│   ✅ Rank candidate actions (ASK, VERIFY, CONTINUE, OBSERVE, ESCALATE, REFER│
│   ✅ Highlight clinical red flags and time-to-golden-hour expiry            │
│                                                                             │
│   WHAT THE SYSTEM IS STRICTLY FORBIDDEN FROM DOING (Non-Negotiable):        │
│   ❌ NEVER autonomously issue a formal medical diagnosis                    │
│   ❌ NEVER autonomously prescribe or dispense medications                   │
│   ❌ NEVER autonomously admit a patient to an inpatient ward                │
│   ❌ NEVER autonomously discharge a patient from medical care               │
│   ❌ NEVER autonomously authorize an emergency surgical procedure           │
│   ❌ NEVER autonomously dispatch an ambulance transfer                      │
│                                                                             │
│   ALL DISPOSITIONS REQUIRE AN AUTHENTICATED RMP SIGNATURE.                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

When an RMP reviews the recommendation, they can:
1. **`ACCEPT`:** Approves the suggested action; binds their digital signature and NMC registration number.
2. **`MODIFY`:** Adjusts the clinical action (e.g. changes destination hospital); system logs modification with justification.
3. **`OVERRIDE`:** Rejects the recommendation completely; system requires an explicit clinical override rationale, preserving full audit history.
