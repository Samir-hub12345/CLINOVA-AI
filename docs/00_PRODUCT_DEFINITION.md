# CLINOVA AI — Product Definition

> **Document ID:** `DOC-00`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  
> **Classification:** Non-Diagnostic Clinical Decision Support & Care Intelligence  

---

## 1. Executive Summary & Core Positioning

**CLINOVA AI** is an **Adaptive Clinical Care Intelligence & Navigation Platform**.

### Core Evolution
$$\text{From Isolated Triage} \longrightarrow \text{To Continuous Care Intelligence}$$

In standard hospital emergency departments, outpatient clinics, and rural Primary Health Centers (PHCs), conventional triage is an isolated, static event: a single assessment based on instantaneous vitals and subjective reporting that outputs an acuity category (e.g., ESI 1–5 or CTAS) and stops.

Isolated triage fails modern healthcare in three critical dimensions:
1. **Dynamic Patient Deterioration:** Patients evolve while waiting or under observation; static triage fails to capture trajectory or mounting evidence uncertainty.
2. **Resource & Feasibility Blindness:** Standard triage assigns priority without knowing if the facility has functioning diagnostics, available ICU beds, oxygen, surgical staff, or antivenom/blood products to actually execute the needed care.
3. **System Disconnection:** Isolated cases generate no systemic epidemiological or operational feedback, leaving network command blind to regional surges, referral logjams, and facility exhaustion.

**CLINOVA AI** connects:
$$\text{Patient Risk} + \text{Evidence Uncertainty} + \text{Facility Capability} + \text{System Demand} + \text{Outcomes}$$
to continuously determine:
$$\mathbf{THE\ SAFEST\ ACHIEVABLE\ CARE\ PATHWAY}$$
while keeping **qualified healthcare professionals in absolute control**.

The system is strictly **non-diagnostic, advisory, and human-in-the-loop (HITL)**.

---

## 2. The Four Innovation Pillars

CLINOVA AI introduces four interconnected intelligence graphs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLINOVA AI ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ Multimodal Clinical Intake ] ──> Text / Voice / OCR / Vitals / Labs       │
│                │                                                            │
│                ▼                                                            │
│  ┌───────────────────────────┐         ┌───────────────────────────┐        │
│  │       1. CAREGRAPH        │         │      2. FACILITYGRAPH     │        │
│  │ Patient State, Trajectory,│         │ Facility Capability, Bed  │        │
│  │ Uncertainty, Evidence     │         │ Capacity, Care Feasibility│        │
│  └─────────────┬─────────────┘         └─────────────┬─────────────┘        │
│                │                                     │                      │
│                └──────────────────┬──────────────────┘                      │
│                                   ▼                                         │
│                      ┌───────────────────────────┐                          │
│                      │ 4. ORCHESTRATION ENGINE   │                          │
│                      │ Safest Achievable Action  │                          │
│                      │ (Ask, Verify, Escalate..) │                          │
│                      └────────────┬──────────────┘                          │
│                                   │                                         │
│                                   ▼                                         │
│                      ┌───────────────────────────┐                          │
│                      │ QUALIFIED CLINICIAN GATE  │ <── Mandatory Human      │
│                      │ (Advisory Only Sign-off)  │     Review & Override    │
│                      └────────────┬──────────────┘                          │
│                                   │                                         │
│                         Care Action & Outcome                               │
│                                   │                                         │
│                                   ▼                                         │
│                      ┌───────────────────────────┐                          │
│                      │       3. SIGNALGRAPH      │                          │
│                      │ System Demand, Congestion,│                          │
│                      │ Syndromic Surge Telemetry │                          │
│                      └───────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **CAREGRAPH (Patient-Level Intelligence):**
   - Represents the evolving clinical state of a patient.
   - Continuously tracks symptoms, vitals, lab results, timeline, evidence provenance, uncertainty, missing parameters, and risk trajectory.
   - Core Question: *What is happening to this patient right now?*

2. **FACILITYGRAPH (Facility-Level Feasibility Intelligence):**
   - Models healthcare facility capabilities (emergency, surgical, pediatric, diagnostic labs, imaging, oxygen, ICU beds, specialists).
   - Dynamically evaluates whether the clinically indicated care can actually be delivered at the current facility or where in the network it can be safely received.
   - Core Question: *Can the required care actually be delivered here, and where else can it safely happen?*

3. **SIGNALGRAPH (System-Level Operational & Epidemiological Intelligence):**
   - Aggregates privacy-preserving, de-identified signals from patient encounters and facility states.
   - Detects syndromic disease clusters, department bottlenecks, and referral pressures across connected facilities.
   - Core Question: *What is happening across the connected healthcare environment?*

4. **ORCHESTRATION ENGINE (Decision & Action Synthesis):**
   - Synthesizes `CareGraph + Uncertainty + FacilityGraph + System Context`.
   - Generates advisory candidate next actions: `ASK` (missing info), `VERIFY` (conflicting data), `CONTINUE` (maintain pathway), `OBSERVE` (close monitoring), `ESCALATE` (immediate bedside clinician attention), `REFER` (transfer to capable facility).
   - Core Question: *What is the safest achievable next care action?*

---

## 3. Product Principles & Non-Negotiable Boundaries

### 3.1 Non-Diagnostic Mandate
- **No Autonomous Diagnosis:** CLINOVA AI never outputs an autonomous diagnosis (e.g., "Patient has Acute Myocardial Infarction"). Instead, it evaluates clinical syndromes, objective physiological deviations, risk stratification (e.g., "High-risk chest pain syndrome with hemodynamic instability"), and evidence uncertainty.
- **No Treatment Prescription:** The system never orders medications, dosages, or invasive interventions autonomously.
- **Clinician Override:** A qualified clinician has 100% authority to accept, modify, or reject any advisory recommendation.
- **Non-Obscured Uncertainty:** The system never conceals data gaps or conflicting findings; missing data is treated as a first-class clinical signal.

### 3.2 Synthetic Data & Privacy Safeguards
- **Synthetic/Public Records Only:** The prototype exclusively processes synthetic patient data and simulated facility telemetry.
- **Strict PII Minimization:** Patient name, national ID, contact details, and precise residential addresses are pseudonymized or withheld at ingestion.
- **Immutable Audit Trail:** All system inferences, evidence extractions, and clinician sign-offs are logged with cryptographically verifiable timestamps and user IDs.

---

## 4. Primary Stakeholders

| Stakeholder Role | Primary User Journey & Value |
| :--- | :--- |
| **Clinicians & Medical Officers** | Fast, high-confidence review of complex patient trajectories, evidence provenance, missing information flags, and facility feasibility. |
| **Triage Nurses & Health Workers** | Rapid, multimodal intake (speech, text, report OCR) with deterministic safety checklists and immediate red-flag detection. |
| **Referral Coordinators** | Instant capability-matching across network hospitals, eliminating blind transfers to facilities lacking ICU beds or specialists. |
| **Hospital & System Administrators** | Real-time SignalGraph telemetry identifying department congestion, supply strains, and emerging regional syndromic surges. |
| **Patients & Caregivers** | Multilingual, respectful intake with informed consent and clear advisories to seek immediate human medical care. |

---

## 5. Master Clinical Care Flow

Every patient encounter moves through the unified continuous care loop:
```
PATIENT
  ↓ MULTIMODAL INTAKE (Text / Voice / OCR / Vitals)
  ↓ INFORMATION STATE & PII MINIMIZATION
  ↓ EVIDENCE STATE (Provenance & Confidence Scoring)
  ↓ CAREGRAPH (Timeline & Physiological State)
  ↓ RISK STRATIFICATION & TRAJECTORY ANALYSIS
  ↓ UNCERTAINTY & MISSING INFORMATION IDENTIFICATION
  ↓ NEXT-BEST INFORMATION / TARGETED FOLLOW-UP
  ↓ CLINICAL ACTION OPTIONS EVALUATION
  ↓ FACILITYGRAPH (Resource & Feasibility Matching)
  ↓ ORCHESTRATION ENGINE (Safest Achievable Pathway)
  ↓ QUALIFIED CLINICIAN REVIEW & DECISION GATE
  ↓ CARE ACTION (CONTINUE / OBSERVE / ESCALATE / REFER)
  ↓ PATIENT OUTCOME RECORDING
  ↓ CAREGRAPH UPDATE (State Transition)
  ↓ SIGNALGRAPH UPDATE (System-wide Telemetry)
  ↓ SYSTEM INTELLIGENCE & AUDIT ARCHIVE
```

---

## 6. Document Authority & Governance

This document serves as the top-level specification for the CLINOVA AI platform. All downstream architectural specifications (`01_` through `20_`) derive their authority from this definition. Changes to core positioning, clinical safety rules, or architectural pillars require a logged decision in `19_DECISION_LOG.md`.
