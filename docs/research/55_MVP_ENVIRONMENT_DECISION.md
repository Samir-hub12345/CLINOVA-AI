# CLINOVA AI — Hackathon MVP Target Environment Scope & Architecture Decision

> **Document ID:** `RES-55`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Problem Framing

A lethal pitfall in engineering hackathon prototypes is **Scope Overreach**—attempting to build six separate, fully customized graphical user interfaces and simulated workflows simultaneously. Such an approach inevitably leads to superficial, shallow mockups, uncalibrated AI pipelines, broken edge cases, and catastrophic presentation failures.

Conversely, shrinking the scope to a single generic clinic destroys CLINOVA's core value proposition:
> *CLINOVA connects patient risk, evidence uncertainty, facility capability, system demand, and real outcomes to identify the safest achievable care pathway across fragmented tiers.*

Phase 4 resolves this tension by executing a rigorous evaluation of all six candidate environments across eight strategic engineering and demonstration dimensions. The final decision establishes:
1. **The Core Demo Pair:** The two foundational environments fully implemented across all UI workspaces.
2. **The Supporting Simulations:** Two high-impact stress scenarios demonstrated through simulated test benches.
3. **The Configuration-Only Tier:** Two specialized environments implemented via declarative configuration schemas and data models.
4. **Zero Removals:** All six environments remain fully supported by the unified CLINOVA Core architecture.

---

## 2. Multi-Dimensional Evaluation Matrix

Each candidate environment is evaluated against eight explicit hackathon criteria:
- **Demonstration Value (DV):** Impact on judges, emotional resonance with healthcare reality.
- **Implementation Complexity (IC):** Engineering hours required for UI and backend specialization.
- **Clinical Safety Rigor (CSR):** Defensibility of HITL guardrails and clinical logic.
- **Time to Ship (TTS):** Feasibility within hackathon sprint timelines.
- **Data Availability (DA):** Availability of realistic synthetic clinical cases and scenarios.
- **Realistic Simulation (RS):** Ability to simulate the environment convincingly on a single demo laptop.
- **Judge Comprehension (JC):** Instant intuitive clarity for technical and medical judges.
- **Architectural Maintainability (AM):** Freedom from code forks and technical debt.

```
┌─────────────────────────┬────┬────┬────┬────┬────┬────┬────┬────┬────────────────────────┐
│ Target Environment      │ DV │ IC │ CSR│ TTS│ DA │ RS │ JC │ AM │ MVP Scope Classification│
├─────────────────────────┼────┼────┼────┼────┼────┼────┼────┼────┼────────────────────────┤
│ **1. Government Hosp.** │ 5  │ 4  │ 5  │ 4  │ 5  │ 5  │ 5  │ 5  │ **CORE DEMO (Hub)**    │
│ **2. PHC (Primary)**    │ 5  │ 4  │ 5  │ 5  │ 5  │ 5  │ 5  │ 5  │ **CORE DEMO (Spoke)**  │
│ **3. Public Camp**      │ 4  │ 3  │ 4  │ 4  │ 4  │ 4  │ 4  │ 5  │ **SUPPORTING SIM.**   │
│ **4. Company Clinic**   │ 3  │ 3  │ 4  │ 4  │ 3  │ 4  │ 4  │ 5  │ **CONFIGURATION-ONLY** │
│ **5. Industrial Health**│ 4  │ 4  │ 5  │ 3  │ 4  │ 4  │ 4  │ 4  │ **SUPPORTING SIM.**   │
│ **6. Campus Health**    │ 3  │ 3  │ 4  │ 4  │ 3  │ 4  │ 4  │ 5  │ **CONFIGURATION-ONLY** │
└─────────────────────────┴────┴────┴────┴────┴────┴────┴────┴────┴────────────────────────┘
*(Ratings: 1 = Lowest / Most Unfavorable, 5 = Highest / Most Favorable)*
```

---

## 3. Tiered Environment Scope Classification

### 3.1 Tier 1: CORE DEMO ENVIRONMENTS (The Hub-and-Spoke Public Spine)
The live hackathon demonstration focuses primarily on the **Rural PHC $\longleftrightarrow$ District Hospital Public Care Continuum**:

1. **`ENV_PHC` (Primary Health Centre — The Peripheral Spoke):**
   - *Why Selected:* Directly addresses the BPUT mandate and the core crisis of rural Indian healthcare. Demonstrates vernacular voice intake (ASHA/ANM), 100% offline local LAN execution, point-of-care rapid testing under high uncertainty ($U_t$), and **FACILITYGRAPH Care Feasibility Checking**.
   - *Live Demo Flow:* Patient presents with acute snakebite/fever $\to$ System evaluates local PHC capabilities $\to$ Flags local care as infeasible $\to$ Recommends intelligent referral to nearest capable District Hospital with verified anti-snake venom and beds $\to$ Dispatches digital referral pass.
2. **`ENV_GOV_HOSPITAL` (District Hospital — The Central Hub):**
   - *Why Selected:* Demonstrates high-throughput public hospital casualty triage, the "90-Second Doctor" multimodal case synthesis (OCR of old paper slips), dynamic queue re-prioritization of deteriorating patients, and receiving the referral dispatched from the PHC.
   - *Live Demo Flow:* Receiving the PHC referral with pre-arrival manifest $\to$ Queue re-ranks based on vital sign trajectory ($\Delta R_t / \Delta t$) $\to$ Doctor reviews synthesized case in $< 45$ seconds $\to$ Verifies orders and authorizes emergency admission.

> **Demonstration Impact:** Showing the **same Master Case** originated in a rural PHC and seamlessly received, prioritized, and treated at a District Hospital proves that CLINOVA is not an isolated triage widget, but a continuous care navigation platform!

---

### 3.2 Tier 2: SUPPORTING SIMULATIONS (High-Impact Edge Benchmarks)
These environments are implemented as pre-configured scenario test benches selectable via a single developer toggle to prove architectural depth:

3. **`ENV_PUBLIC_CAMP` (Public Health Camp Simulation):**
   - *Implementation:* Demonstrates batch high-throughput screening mode. Allows loading a batch of 50 synthetic village attendees into an offline queue, showcasing instant 3-color risk classification (Green, Yellow, Red) and batch referral pass generation in $< 30$ seconds per encounter.
4. **`ENV_INDUSTRIAL_HEALTH` (Industrial Trauma Fast-Track Simulation):**
   - *Implementation:* Demonstrates the emergency resuscitation workflow. Loads an acute chemical burn / machinery crush trauma case, showcasing instant automated calculation of Shock Index, Revised Trauma Score (RTS), and Parkland burn fluid resuscitation rates with direct matching to regional Burn ICUs.

---

### 3.3 Tier 3: CONFIGURATION-ONLY ENVIRONMENTS (Schema-Proven Architecture)
These environments exist as complete declarative configuration profiles (`environment-config.json`), database seed profiles, and API permission test fixtures:

5. **`ENV_COMPANY_CLINIC` (Corporate Clinic Configuration):**
   - *Implementation:* Demonstrates strict DPDP Act 2023 employer-employee cryptographic role segregation. Validated via automated API tests confirming that `ROLE_FACILITY_ADMIN` (HR Manager) receives only non-clinical fitness certificates while clinical endpoints return HTTP 403 Forbidden.
6. **`ENV_CAMPUS_HEALTH` (Campus Health Configuration):**
   - *Implementation:* Demonstrates SIGNALGRAPH hostel-level syndromic clustering. Validated via synthetic telemetry scripts proving that localized fever spikes in student dormitories trigger automated early outbreak warnings without exposing student identities.

---

## 4. Why This Rationalization Guarantees Hackathon Victory

1. **Depth Over Breadth:** Instead of six half-finished, buggy screens, the team delivers an unshakeable, deeply polished, end-to-end continuous care referral loop across `ENV_PHC` and `ENV_GOV_HOSPITAL`.
2. **Defensible Hackathon Storyline:** The judges experience the most urgent, high-stakes problem in Indian healthcare: a rural villager transferred safely from an off-grid outpost to a crowded district emergency room without data loss or blind refusal.
3. **Zero Vision Compromise:** When judges ask: *"Can this work in an industrial factory or corporate office?"*, the team immediately presents the active configuration schemas (`RES-47`, `RES-48`, `RES-49`), the failure matrix (`RES-51`), and the supporting simulation test benches.
4. **Guaranteed Execution Feasibility:** Reduces front-end UI surface area to three core visual workspaces (Patient Intake, Nurse Triage, Doctor Reviewer) across the primary hub-and-spoke pair while keeping all six environments fully specified in architecture.
