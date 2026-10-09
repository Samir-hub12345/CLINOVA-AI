# CLINOVA AI — Innovation Architecture Decisions & Graph Scoping

> **Document ID:** `RES-22`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Architectural Directives

Based on the adversarial audits conducted in Phase 2, this document formalizes the architectural decisions for the four core intelligence engines of CLINOVA AI:
1. **CAREGRAPH** (Patient-Level State & Trajectory)
2. **FACILITYGRAPH** (Facility-Level Capability & Feasibility)
3. **SIGNALGRAPH** (System-Level Syndromic & Operational Telemetry)
4. **ORCHESTRATION ENGINE** (Multi-Graph Synthesis & Care Pathway Recommendation)

For each engine, we document the validated problem, existing alternatives, remaining gap, intended function, novelty category, implementation feasibility, demonstration methodology, risk factors, and the final recommended scope decision: **KEEP**, **MODIFY**, **REMOVE**, or **FUTURE**.

---

## 2. Granular Architectural Decisions

### 1. CAREGRAPH Engine
- **Validated Problem:** Frontline outpatient triage treats patient risk as a static snapshot at intake, failing to detect clinical deterioration during long waiting-room delays and ignoring evidential uncertainty.
- **Existing Solutions:** Hospital Early Warning Systems (NEWS2, Epic Deterioration Index), Bayesian symptom checkers (Ada, Infermedica), ICU telemetry monitors.
- **Remaining Gap:** Translating ICU-style trajectory slope ($\Delta R_t / \Delta t$) into an active outpatient queue re-prioritization engine that couples multimodal evidence provenance to explicit missing-data uncertainty ($U_t$).
- **Intended CLINOVA Function:** Reactive clinical state machine maintaining physiological parameters, evidence provenance pointers, rate-of-change trajectory, and epistemic uncertainty vectors.
- **Novelty Category:** **Category C (Meaningful Integration)** with a **Category E Contribution** in uncertainty-driven question generation.
- **Evidence Strength:** **Grade A** (NEWS2 validation studies; BMJ queue safety audits).
- **Implementation Feasibility:** **100% Feasible at ₹0**; implemented in pure async Python (`backend/app/domain/caregraph/engine.py`) using SQLite/PostgreSQL.
- **Demonstration Method in Hackathon:** Ingest serial vitals for a waiting patient (e.g., HR rising from 88 to 125 bpm, BP dropping from 120/80 to 88/60); observe CAREGRAPH automatically transition trajectory from `STABLE` to `WORSENING`, elevate acuity to `EMERGENCY_RED`, and flash an urgent bedside re-triage alert.
- **Risks:** Clinician cognitive overload if graph mutations trigger excessive pop-up notifications.
- **Recommended Scope Decision:** **KEEP WITH NARROWED DEFINITION**
  *(Focus on state machine transitions and trajectory slope rather than complex graph theory visuals).*

---

### 2. FACILITYGRAPH Engine
- **Validated Problem:** Over 60% of rural emergency referrals are dispatched "blindly" to hospitals that lack open ICU beds, functioning ventilators, blood components, or on-duty specialists, resulting in fatal admission turnaways.
- **Existing Solutions:** Commercial hospital capacity software (TeleTracking, Epic Grand Central), state-level manual bed count websites (Delhi Corona portal), emergency ambulance dispatch (108).
- **Remaining Gap:** Lightweight, frontline care feasibility matching that evaluates individual clinical prerequisites against real-time 5-tier facility capabilities at the point of primary care intake.
- **Intended CLINOVA Function:** Resource topology engine modeling resuscitation capabilities, specialist duty status, diagnostic inventory, bed occupancy, and Haversine transit distances.
- **Novelty Category:** **Category C (Meaningful Combination)** + **Category E Contribution** in low-resource public health settings.
- **Evidence Strength:** **Grade A** (Rural Health Statistics 2022; ICMR Emergency Care Audits 2023).
- **Implementation Feasibility:** **100% Feasible at ₹0**; implemented via relational capability schemas and local Python Haversine algorithms (`backend/app/domain/facilitygraph/engine.py`).
- **Demonstration Method in Hackathon:** Simulate a severe pediatric dengue patient with hemorrhagic shock presenting at a rural PHC; watch FACILITYGRAPH evaluate local capabilities as `CURRENT_FACILITY_INSUFFICIENT`, query the regional network, identify a tertiary Medical College with confirmed platelets and ICU beds, and generate a capability-matched Referral Pack with destination pre-alert.
- **Risks:** Simulated facility capacity telemetry must be clearly marked as synthetic demonstration data to avoid misleading judges.
- **Recommended Scope Decision:** **KEEP & PRIORITIZE**
  *(Highest demonstrable clinical impact in rural public healthcare scenarios).*

---

### 3. SIGNALGRAPH Engine
- **Validated Problem:** National public health surveillance (IHIP/IDSP) operates as a unidirectional reporting requirement; zero real-time epidemiological surge context flows back down to the examining doctor during active outpatient triage.
- **Existing Solutions:** National surveillance systems (IHIP, IDSP, CDC ESSENCE), hospital operations command centers (GE Healthcare Command Center).
- **Remaining Gap:** Uniting local syndromic disease cluster detection with departmental queue saturation telemetry, and closing the loop by pushing real-time surge context into the doctor's active triage review screen.
- **Intended CLINOVA Function:** Aggregates de-identified syndromic encodings and queue wait durations; computes moving-average $z$-scores ($z > 2.58$) to detect outbreaks; pushes alerts to clinician workstations.
- **Novelty Category:** **Category C (Meaningful Combination / Integration)**.
- **Evidence Strength:** **Grade A** (MoHFW IHIP standards; CDC EARS algorithms).
- **Implementation Feasibility:** **100% Feasible at ₹0**; dynamic SQL aggregation queries over Master Case encounters (`backend/app/domain/signalgraph/engine.py`).
- **Demonstration Method in Hackathon:** Ingest 15 synthetic cases of febrile illness with thrombocytopenia within a 24-hour window; watch SIGNALGRAPH trigger a `SYNDROMIC_CLUSTER_ALERT` ($z = 3.12, p < 0.01$) on the Leaflet network map, and observe the Doctor Dashboard display an epidemiological surge badge.
- **Risks:** Must never be presented as a "replacement for National IDSP/IHIP"; must be framed strictly as a local clinic-level telemetry loop.
- **Recommended Scope Decision:** **MODIFY SCOPE**
  *(Narrow claim from "national surveillance replacement" to "frontline two-way syndromic & operational telemetry loop").*

---

### 4. ORCHESTRATION Synthesis Engine
- **Validated Problem:** Frontline clinical decision support either produces passive, non-executable notes (AI scribes) or generates unconstrained generative diagnoses that trigger automation bias or hallucinations.
- **Existing Solutions:** Commercial CDSS (UpToDate, Isabel), payer next-best-action rules (Optum, Pega), ambient scribes (Nuance DAX, Abridge).
- **Remaining Gap:** Synthesizing patient physiological trajectory (`CareGraph`), epistemic uncertainty (`Uncertainty`), institutional capabilities (`FacilityGraph`), and macro context (`SignalGraph`) into six standardized candidate next actions (`ASK` to `REFER`) under strict deterministic safety bounds and qualified clinician oversight.
- **Intended CLINOVA Function:** The central decision-synthesis core recommending "The Safest Achievable Care Pathway."
- **Novelty Category:** **Category C (Integration)** + **Category D / E (Research Formulation)**.
- **Evidence Strength:** **Grade A** (FDA CDSS Guidance 2022; WHO AI Health Guidance 2021).
- **Implementation Feasibility:** **100% Feasible at ₹0**; rule-governed async state evaluator (`backend/app/domain/orchestration/engine.py`).
- **Demonstration Method in Hackathon:** Walk a complex multi-factor clinical vignette through the complete pipeline: show how missing vital parameters trigger `ASK`, conflicting readings trigger `VERIFY`, stable low-risk profiles trigger `CONTINUE`, borderline vitals trigger `OBSERVE`, red flags trigger `ESCALATE`, and facility deficits trigger `REFER`.
- **Risks:** The evaluation objective function must remain transparent and explainable rather than operating as an opaque black box.
- **Recommended Scope Decision:** **KEEP AS CENTRAL ARCHITECTURAL CORE**

---

## 3. Master Architecture Decision Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MASTER ARCHITECTURAL VERDICTS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CAREGRAPH:             [ KEEP — NARROW DEFINITION ]                     │
│     Active clinical state machine; dynamic trajectory slope; $U_t$ gauge.   │
│                                                                             │
│  2. FACILITYGRAPH:         [ KEEP — HIGH PRIORITY ]                         │
│     Point-of-intake 5-tier care feasibility matching at ₹0.                 │
│                                                                             │
│  3. SIGNALGRAPH:           [ MODIFY — BOUND SCOPE ]                         │
│     Local clinic two-way telemetry loop; NOT national IHIP replacement.     │
│                                                                             │
│  4. ORCHESTRATION ENGINE:  [ KEEP — CENTRAL CORE ]                          │
│     6 standardized candidate actions; deterministic red-flag overrides.     │
│                                                                             │
│  5. CONTINUOUS FINE-TUNING:[ DEFER TO FUTURE PHASE 3/4 ]                    │
│     LoRA/PEFT model fine-tuning moved to post-hackathon research grant.     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
