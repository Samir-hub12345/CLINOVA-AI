# CLINOVA AI — Phase 4 Architectural & Operational Decision Log

> **Document ID:** `PHASE_4_DECISIONS`  
> **Status:** LOCKED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & Decision Mandate

This document serves as the immutable architectural contract and decision log locked during Phase 4 of the CLINOVA AI implementation roadmap. All technical decisions recorded herein are binding on subsequent implementation phases (Phase 5+).

---

## 2. Locked Decisions

### DECISION 4.1: The Single Platform Invariant (Zero Code Forks)
- **Status:** APPROVED & LOCKED
- **Decision:** CLINOVA will **NOT** be developed as separate, forked software applications (e.g., no separate "PHC Edition" vs. "Hospital Edition"). Exactly **ONE** unified CLINOVA Core codebase will be developed. All environmental specializations are modulated strictly via declarative runtime configuration schemas (`environment-config.json`), dynamic facility capability states (`facility-graph-state.json`), and active role permission matrices (`role-config.json`).
- **Rationale:** Prevents codebase fragmentation, simplifies automated testing, ensures unified clinical safety invariants, and enables a single engineering team to maintain multi-environment deployments.

---

### DECISION 4.2: Deployment-Time Environment Identification & Locking
- **Status:** APPROVED & LOCKED
- **Decision:** A deployment identifies its operating environment at startup via an immutable deployment-time configuration parameter (`CLINOVA_ENVIRONMENT_ID`). The environment **CANNOT** be switched dynamically mid-session for active clinical queues. Changing an environment requires administrative facility re-provisioning, queue flushing/synchronization, and explicit database reset.
- **Rationale:** Permitting ad-hoc runtime environment toggles within an active clinical queue would cause undefined state transitions, corrupt active triage priority rankings, and invalidate active clinical audit trails.

---

### DECISION 4.3: 100% Offline Local LAN Autonomy for Primary & Outreach Nodes
- **Status:** APPROVED & LOCKED
- **Decision:** In `ENV_PHC` and `ENV_PUBLIC_CAMP`, CLINOVA must execute with 100% operational autonomy on a Local Clinic Server broadcasting a local Wi-Fi LAN without active internet connectivity. All core features—Master Case creation, vernacular voice transcription, vital sign logging, risk calculation, clinical decision gates, and printable referral slip generation—must execute without making external cloud calls.
- **Rationale:** Field evidence shows rural peripheral health centres in India experience multi-day cellular outages. Any cloud-dependent medical workflow halts clinical care and creates lethal patient abandonment.

---

### DECISION 4.4: The Emergency Decoupling Principle
- **Status:** APPROVED & LOCKED
- **Decision:** Clinical resuscitation workflows must **NEVER** require completion of the routine intake workflow before life-saving resuscitation orders, facility capability checks, and transfer alerts are executed. In all six environments, a 1-click **Emergency Fast-Track Bypass** is implemented, requiring $< 20$ seconds to acquire minimal life-saving data (ABC + Vitals) while deferring all administrative, demographic, and billing data until post-stabilization.
- **Rationale:** Forcing nurses and doctors during acute trauma, cardiac arrest, or eclampsia to complete multi-screen demographic or insurance forms violates clinical ethics and Indian Supreme Court rulings (*Paschim Banga*).

---

### DECISION 4.5: Explicit Epistemic Uncertainty ($U_t$) Degradation
- **Status:** APPROVED & LOCKED
- **Decision:** When diagnostic laboratories or imaging modalities are absent (as in `ENV_PHC` and `ENV_PUBLIC_CAMP`), the system **MUST NOT** hallucinate high diagnostic certainty or recommend complex specialist therapies. The system must explicitly elevate the Epistemic Uncertainty score ($U_t \ge 0.65$), suppress confident automated diagnoses, and surface **Verification & Triage-to-Safety Actions** (`ORDER_POC_GLUCOSE`, `VERIFY_BILATERAL_BREATH_SOUNDS`, `REFER_FOR_IMAGING`).
- **Rationale:** Grounded in ICMR AI Ethics Guidelines 2023. Prevents clinicians from developing dangerous automation complacency based on absent diagnostic data.

---

### DECISION 4.6: Stale Facility Telemetry Degradation & Mandatory Human Telephone Gate
- **Status:** APPROVED & LOCKED
- **Decision:** In $\text{FACILITYGRAPH}$, any receiving hospital capability node (e.g., ICU beds, oxygen, antivenom) that has not been refreshed within 12 hours is automatically degraded to `STALE`. The referral routing engine **CANNOT** silently route an emergency ambulance to a facility with stale or conflicting data without displaying an explicit amber warning and enforcing a mandatory telephonic bed confirmation step.
- **Rationale:** Directly eliminates the "Blind Referral Disaster" where ambulances transfer deteriorating patients to tertiary hospitals only to be turned away at the gate due to unadvertised bed saturation.

---

### DECISION 4.7: Bounded SIGNALGRAPH Definition (Strictly Local Telemetry)
- **Status:** APPROVED & LOCKED
- **Decision:** SIGNALGRAPH is strictly defined and implemented as a **local, privacy-preserving operational and syndromic telemetry engine** operating at the individual facility or campus level. It is **NOT** a national surveillance system, does **NOT** collect biometric identifiers, and does **NOT** replace IHIP/IDSP. All telemetry exports must enforce $k$-anonymity ($k \ge 5$) and differential privacy noise.
- **Rationale:** Prevents surveillance overreach, guarantees compliance with the DPDP Act 2023, and preserves patient trust.

---

### DECISION 4.8: Deterministic High-Acuity Conservative Conflict Resolution
- **Status:** APPROVED & LOCKED
- **Decision:** When offline local nodes synchronize with cloud databases and encounter concurrent data conflicts on patient acuity or vital signs, the sync engine executes a **Deterministic Conservative Merge**:
  1. All vital signs are preserved in an append-only timeline with explicit author provenance.
  2. If a conflict arises between differing acuity risk scores, the engine defaults to the **Higher Acuity Level** (conservative fail-safe bias).
- **Rationale:** Clinical safety dictates that an acute vital reading or high risk flag must never be silently overwritten by an earlier or lower reading during offline synchronization.

---

### DECISION 4.9: Hackathon MVP Scope Rationalization
- **Status:** APPROVED & LOCKED
- **Decision:** For the hackathon MVP implementation:
  1. **Core Demo Environments (Primary Visual Scope):** `ENV_PHC` (Peripheral Spoke) and `ENV_GOV_HOSPITAL` (Central Hub). These two form the end-to-end continuous care referral loop.
  2. **Supporting Simulations (Demonstrable Scenario Benchmarks):** `ENV_PUBLIC_CAMP` (Batch High-Throughput Triage) and `ENV_INDUSTRIAL_HEALTH` (Trauma/Burn Emergency Resuscitation).
  3. **Configuration-Only Tier (Schema-Validated):** `ENV_COMPANY_CLINIC` (DPDP Role Segregation) and `ENV_CAMPUS_HEALTH` (Hostel Outbreak Telemetry).
  4. **Zero Environments Removed:** All six environments remain fully specified in architectural documentation and data models.
- **Rationale:** Maximizes implementation depth, judges' emotional and cognitive comprehension, and architectural credibility while guaranteeing sprint feasibility.

---

### DECISION 4.10: Zero-Cost / Open-Source Tech Stack Invariant
- **Status:** APPROVED & LOCKED
- **Decision:** Across all six environments, CLINOVA must remain 100% operational on a **₹0 open-source first technology stack**:
  - Frontend: Next.js + TypeScript (lightweight thin-client HTML5).
  - Backend: FastAPI + Python.
  - Database: Local SQLite (WAL mode) / PostgreSQL (Supabase compatible).
  - Speech: local quantized faster-whisper.
  - OCR: local PaddleOCR / Tesseract.
  - Maps: Leaflet + OpenStreetMap (OSRM).
  - Zero mandatory commercial APIs (zero OpenAI, zero Google Maps Platform paid tiers, zero commercial cloud subscriptions).
- **Rationale:** Mandatory hackathon constraint ensuring genuine deployability in resource-poor public healthcare facilities across India.
