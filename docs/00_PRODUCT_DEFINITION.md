# CLINOVA AI — Product Definition

> **Document ID:** `DOC-00`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  
> **Classification:** Non-Diagnostic Clinical Decision Support & Care Intelligence  

---

## 1. Product Identity

- **Product Name:** CLINOVA AI
- **Product Category:** Adaptive Clinical Care Intelligence & Navigation Platform
- **Primary Positioning:** `FROM ISOLATED TRIAGE → CONTINUOUS CARE INTELLIGENCE`
- **Primary Product Statement:**
  > **CLINOVA connects patient risk, evidence uncertainty, facility capability, system demand and real outcomes to identify the safest achievable care pathway while keeping qualified healthcare professionals in control.**

### Naming Consistency Mandate
Do not use alternate product names in any project documentation, metadata, future UI, architecture, database models, API naming, README, public website, or presentation references. The canonical name is strictly **CLINOVA AI** (or **CLINOVA**).

---

## 2. Product Purpose

CLINOVA exists to:
1. **Understand fragmented multimodal patient information** across speech, typed narrative, lab images, printed reports, and vitals.
2. **Convert that information into structured clinical content** without hallucinating or inventing missing values.
3. **Make evidence quality visible** by tracking source provenance, timestamps, and confidence.
4. **Identify missing, conflicting, and unreliable information** as first-class clinical state objects.
5. **Support safer clinical decisions without replacing the clinician**, operating strictly as a human-in-the-loop advisory engine.
6. **Connect patient requirements with available healthcare resources** dynamically evaluated through facility capabilities and capacity.
7. **Maintain continuity** through referrals, admissions, appointments, transfers, and real-world outcomes.
8. **Learn from clinician decisions and outcomes** at the system-evaluation level to refine guidance without modifying live clinical parameters autonomously.

---

## 3. Core Product Goals

- **G1 — UNDERSTAND:** Convert fragmented multimodal information (spoken, typed, OCR, vitals) into an interpretable, standardized patient state.
- **G2 — IDENTIFY UNCERTAINTY:** Distinguish what is known, unknown, conflicting, unreliable, verified, and inferred, making evidential gaps explicit.
- **G3 — SUPPORT DECISIONS:** Provide structured, explainable decision support while keeping the qualified clinician in absolute control.
- **G4 — NAVIGATE CARE:** Connect patient requirements with feasible healthcare resources across the regional care network.
- **G5 — MAINTAIN CONTINUITY:** Connect intake → review → action → referral/admission → follow-up → outcome as an unbroken clinical journey.
- **G6 — LEARN FROM OUTCOMES:** Connect AI-supported recommendation → clinician decision → actual action → real outcome for system evaluation and future model calibration.

---

## 4. The Four Innovation Pillars

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
   - Continuously models physiological state, longitudinal trajectory, missing parameters, evidence provenance, and uncertainty.
   - Core Question: *What is happening to this patient right now?*

2. **FACILITYGRAPH (Facility-Level Feasibility Intelligence):**
   - Evaluates whether indicated care can actually be delivered at the current facility based on real equipment, beds, blood bank stock, and on-duty specialists.
   - Core Question: *Can the required care actually be delivered here, and where else can it safely happen?*

3. **SIGNALGRAPH (System-Level Operational & Epidemiological Intelligence):**
   - Aggregates privacy-preserving, de-identified signals from patient encounters and facility bottlenecks across connected facilities.
   - Core Question: *What is happening across the connected healthcare environment?*

4. **ORCHESTRATION ENGINE (Decision & Action Synthesis):**
   - Combines `CareGraph + Uncertainty + FacilityGraph + System Context`.
   - Recommends candidate next actions: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
   - Core Question: *What is the safest achievable next care action?*

---

## 5. Scope & Strict Non-Scope (Phase 1 Boundaries)

### 5.1 In Scope for Phase 1
- Complete product definition, user journey mapping, and root cause analysis.
- Definitive role-permission and environment matrices (6 environments, 8 user roles).
- Exact specification of Master Case data model, evidence model, and 4 intelligence graphs.
- Purpose-specific reporting contracts (6 report archetypes).
- Static wireframe and screen specifications for all 40 system screens (`docs/design/`).
- BPUT baseline (B01–B18) and CLINOVA core innovation (C01–C11) tracking matrix in `docs/FEATURE_INVENTORY.md`.
- Architectural contracts for ₹0 open-source technology stack, AI safety, and privacy compliance.

### 5.2 Strict Non-Scope for Phase 1
- **NO** production application code implementation (frontend or backend).
- **NO** live database migrations or production table creation.
- **NO** live API keys or external paid cloud connections.
- **NO** model training, LoRA fine-tuning, or weights updating.
- **NO** production deployment to public servers.
- **NO** progression to Phase 2 until human-in-the-loop review approves Phase 1.
