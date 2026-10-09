# CLINOVA AI — Common Core vs. Environment Configuration Architecture

> **Document ID:** `RES-50`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 4 — Target Environments & Operational Context Specification  
> **Version:** 4.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Executive Summary & Architectural Invariant

A foundational hazard in healthcare systems engineering is **architectural fragmentation**—forking the code repository into bespoke, incompatible builds for different deployment sites (e.g., "CLINOVA Hospital Edition" vs. "CLINOVA Rural Camp Edition"). 

Phase 4 firmly rejects code forking and establishes the **Single Platform Invariant**:
> **The Single Platform Invariant:** There is exactly **ONE CLINOVA CORE ENGINE**. Environmental specialization is achieved strictly through declarative runtime schemas:
> $$\text{Runtime Behavior} = \text{CLINOVA Core} \oplus \text{Environment Config} \oplus \text{Facility State} \oplus \text{Role Matrix}$$

Every patient encounter, whether occurring in an air-conditioned IT corporate clinic or an off-grid rural tented outreach camp, is governed by the exact same **Master Case (`CaseModel`)**, the exact same **Evidence Provenance Engine**, the exact same **Epistemic Uncertainty Calculus ($U_t$)**, and the exact same **Meaningful Human Control (MHC)** safety gates.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA UNIFIED RUNTIME ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         CLINOVA CORE ENGINE                         │   │
│   │  • Master Case (`CaseModel`)      • Evidence Provenance Tracker     │   │
│   │  • Epistemic Uncertainty ($U_t$)   • Meaningful Human Control Gates  │   │
│   │  • Hard Clinical Safety Invariants • Cryptographic Audit Trail       │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │ Modulated by                         │
│           ┌──────────────────────────┼──────────────────────────┐           │
│           ▼                          ▼                          ▼           │
│   ┌───────────────────┐      ┌───────────────────┐      ┌─────────────────┐ │
│   │ ENVIRONMENT CONFIG│      │   FACILITY STATE  │      │   ROLE MATRIX   │ │
│   │ • Intake Workflow │      │ • Live Capacities │      │ • Active Roles  │ │
│   │ • Queue Policy    │      │ • Capability Map  │      │ • Permission Set│ │
│   │ • Referral Topology│     │ • Freshness State │      │ • Context Grids │ │
│   └───────────────────┘      └───────────────────┘      └─────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six-Tier Architectural Layering Taxonomy

To ensure clean separation of concerns, system parameters are classified into six distinct structural tiers:

```
┌───────┬──────────────────────────────────┬──────────────────────────────────┐
│ Tier  │ Architectural Domain             │ Modification Cadence / Ownership │
├───────┼──────────────────────────────────┼──────────────────────────────────┤
│ A     │ CLINOVA CORE (Invariant)         │ Locked codebase; zero deviation  │
│ B     │ ENVIRONMENT CONFIGURATION        │ Static JSON/YAML at deployment   │
│ C     │ ROLE CONFIGURATION               │ Shift-based runtime assignment   │
│ D     │ FACILITY DATA (Dynamic State)    │ Continuous / periodic telemetry  │
│ E     │ WORKFLOW CONFIGURATION           │ Department-level route overrides │
│ F     │ HARDWARE / NETWORK CONFIGURATION │ Infrastructure environment layer │
└───────┴──────────────────────────────────┴──────────────────────────────────┘
```

---

## 3. Tier A: The Invariant CLINOVA Core

The following components and behaviors remain **100% identical and non-negotiable** across all six environments:

1. **The Single Master Case Invariant (`CaseModel`):**
   - Every patient encounter generates exactly one immutable Master Case record.
   - All actors (intake clerks, triage nurses, examining clinicians, referral coordinators) read from and append to this continuous record. Departmental data silos are strictly prohibited.
2. **Evidence Provenance & Verification State Tracking:**
   - Every extracted clinical entity (symptom, vital, allergy, diagnosis) retains an unalterable pointer to its raw capture modality (audio waveform timestamp, OCR document bounding box, manual staff keyboard entry).
   - Entities strictly progress through explicit verification states: `PATIENT_UNVERIFIED` $\to$ `STAFF_VERIFIED` $\to$ `CLINICIAN_APPROVED`.
3. **Epistemic Uncertainty Engine ($U_t$):**
   - The system must always compute and display explicit uncertainty scores alongside clinical recommendations. The formula incorporates missing critical parameters, time elapsed since last vitals, and diagnostic ambiguity:
     $$U_t = 1.0 - \left( w_v \cdot \frac{\text{Vitals}_{\text{present}}}{\text{Vitals}_{\text{required}}} + w_e \cdot \frac{\text{Evidence}_{\text{verified}}}{\text{Evidence}_{\text{total}}} + w_t \cdot e^{-\lambda \Delta t} \right)$$
   - AI recommendations can never claim high confidence when foundational objective vitals are missing.
4. **Meaningful Human Control (MHC) Safety Gates:**
   - Under no circumstances does the system execute autonomous clinical dispositions. Only a licensed Registered Medical Practitioner (`ROLE_CLINICIAN`) can authorize `APPROVE`, `PRESCRIBE`, `DISCHARGE`, `ADMIT`, or `REFER`.
   - Clinicians have mandatory 1-click override capabilities with frictionless justification capture.
5. **Hard Clinical Safety Guardrails:**
   - Absolute red-flag detection rules (e.g., $\text{SpO}_2 < 85\%$, Systolic $\text{BP} < 80\text{ mmHg}$, Shock Index $> 1.0$, pediatric stridor, active chest trauma) immediately elevate case acuity to emergency status regardless of the operating environment.
6. **Append-Only Tamper-Evident Audit Trail:**
   - Every read, edit, override, and disposition event is recorded in a cryptographic append-only audit log with UTC timestamps, user IDs, and environmental tags.

---

## 4. Tiers B–F: Configurable Environmental Dimensions

The following parameters vary systematically across the six target environments:

```
┌─────────────────────────────────┬───────────────────┬──────────────┬──────────────┬──────────────┬───────────────────┬──────────────┐
│ Operational Dimension           │ Gov. Hospital     │ PHC          │ Public Camp  │ Company      │ Industrial Health │ Campus       │
├─────────────────────────────────┼───────────────────┼──────────────┼──────────────┼──────────────┼───────────────────┼──────────────┤
│ Default Intake Mode             │ Desk + Kiosk      │ ASHA-Assisted│ Token-Batch  │ SSO Self-App │ Paramedic Rush    │ Student App  │
│ Primary Acuity Scoring          │ ESI 5-Tier        │ 3-Tier Risk  │ 3-Color Flag │ Occupational │ RTS / Shock Index │ Syndromic    │
│ Target Consult Budget           │ 90–180 sec        │ 3–6 min      │ 60–90 sec    │ 5–10 min     │ < 3 min (Trauma)  │ 5–10 min     │
│ Diagnostic Verification Latency │ 2–6 hours         │ Absent       │ POCT Instant │ Private Lab  │ Instant i-STAT    │ 15–30 min    │
│ Facility Capability Matching    │ Internal Bed Mgt  │ Outward Reg. │ Camp Outward │ Private Emp. │ Burn/Trauma Specs │ Municipal MCH│
│ Offline Cache Tolerance         │ LAN-Autonomous    │ 100% Offline │ 100% Battery │ Cloud Cache  │ Air-Gapped LAN    │ LAN-Hybrid   │
│ PII Boundary Level              │ Standard Medical  │ Standard Med.│ Semi-Anon    │ DPDP Shield  │ Statutory Hazmat  │ Academic Sh. │
│ Vernacular Audio Default        │ State + English   │ Pure Vernac. │ Pure Vernac. │ English/Bili │ Multilingual      │ English/Bili │
└─────────────────────────────────┴───────────────────┴──────────────┴──────────────┴──────────────┴───────────────────┴──────────────┘
```

---

## 5. Declarative Environment Configuration Schema

At deployment time, the operating environment is instantiated via a declarative schema:

```json
{
  "$schema": "https://clinova.org/schemas/v4/environment-config.json",
  "environmentId": "ENV_PHC",
  "environmentName": "Primary Health Centre",
  "tier": "PRIMARY_CARE_OUTPOST",
  "operationalProfile": {
    "intakeDefault": "ASSISTED_HEALTH_WORKER",
    "primaryAcuityModel": "THREE_TIER_RISK",
    "consultationTimeBudgetSeconds": 300,
    "allowUnidentifiedPatients": true,
    "enforceEmergencyBypass": true
  },
  "connectivityProfile": {
    "networkTopology": "LOCAL_LAN_OFFLINE_AUTONOMOUS",
    "cloudSyncMode": "DEFERRED_ASYNC_BATCH",
    "syncIntervalMinutes": 60,
    "requireWanForEmergency": false
  },
  "facilityCapabilityDefaults": {
    "hasInpatientBeds": true,
    "inpatientBedCapacity": 6,
    "hasIcuBeds": false,
    "hasMechanicalVentilators": false,
    "hasBloodBank": false,
    "hasEmergencyOt": false,
    "hasImaging": false,
    "labCapabilityTier": "POCT_RAPID_KITS_ONLY"
  },
  "referralPolicy": {
    "autoTriggerFeasibilityCheck": true,
    "preferredReceivingTiers": ["COMMUNITY_HEALTH_CENTRE", "DISTRICT_HOSPITAL"],
    "requireBedConfirmationBeforeDispatch": true,
    "generateThermalReferralPass": true
  },
  "privacyGovernance": {
    "piiBoundaryType": "STANDARD_CLINICAL",
    "enforceEmployerSegregation": false,
    "enforceAcademicSegregation": false,
    "dpdpPurposeTag": "PUBLIC_PRIMARY_HEALTHCARE"
  }
}
```

---

## 6. Environment Selection & Routing Architecture

### 6.1 Evaluation of Identification Mechanisms

| Identification Strategy | Mechanism | Pros | Cons | Recommendation |
|:---|:---|:---|:---|:---|
| **Strategy 1: Deployment-Time Config** | Baked into `.env` or container config file | Immutable, impossible for non-admin to accidentally break, zero runtime latency | Requires container redeploy to change | **RECOMMENDED FOR MVP & PRODUCTION** |
| **Strategy 2: Facility Profile Lookup** | Loaded from database based on registered `FacilityID` | Dynamic, central management across multi-facility health networks | Fails during complete cold offline boot without central database access | Supporting production feature |
| **Strategy 3: User Runtime Toggle** | Dropdown on UI login screen | Flexible for multi-setting demonstrations | High risk of staff selecting wrong environment, corrupting clinical queues | **DEMO/DEV ONLY** |

### 6.2 The Post-Deployment Environment Change Policy
- **Rule:** A live deployment **CANNOT** dynamically toggle its `environmentId` mid-session for active cases.
- **Consequence of Change:** Switching from `ENV_GOV_HOSPITAL` to `ENV_PHC` changes triage risk models, queue sorting algorithms, and referral routing logic. If permitted mid-flight, active queue states would become undefined and invalidate active clinical audit trails.
- **Protocol:** Changing an environment requires administrative facility re-provisioning, flushing/syncing all closed cases, and initializing a clean operational state.

---

## 7. CAREGRAPH Environmental Modulation

The patient care graph ($\text{CAREGRAPH}$) models clinical state, trajectories, and epistemic uncertainty over time. Operating environments profoundly alter the topology and data density of $\text{CAREGRAPH}$:

```
┌───────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Environment       │ Evidence Available      │ Evidence Missing        │ Trajectory Resolution   │
├───────────────────┼─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ **Gov Hospital**  │ Dense serial vitals,    │ Past longitudinal OPD   │ High temporal frequency │
│                   │ basic blood labs, X-ray │ history, baseline vitals│ ($\Delta t = 15$ min)   │
│ **PHC**           │ Point-of-care dipsticks,│ Automated biochemistry, │ Low temporal frequency  │
│                   │ verbal family history   │ imaging, serial vitals  │ ($\Delta t = 2$ hours)  │
│ **Public Camp**   │ Single-point vitals,    │ All prior history,      │ Static single snapshot  │
│                   │ capillary blood glucose │ confirmatory labs       │ ($\Delta t = 0$, no $\Delta R_t$)│
│ **Company Clinic**│ Historic annual checkup,│ Complex emergency labs, │ High chronic resolution │
│                   │ connected digital vitals│ inpatient trajectories  │ ($\Delta t = \text{weeks/months}$)│
│ **Industrial**    │ Acute trauma vitals,    │ Prior medical history,  │ Hyper-acute trajectory  │
│                   │ toxic gas exposure tags │ chronic disease baseline│ ($\Delta t = 2$ min in bay)│
│ **Campus Health** │ High-fidelity history,  │ Complex inpatient labs, │ Acute-subacute series   │
│                   │ serial CBC platelets    │ formal imaging          │ ($\Delta t = 12$ hours) │
└───────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

### Epistemic Uncertainty Modulation
In `ENV_PHC` and `ENV_PUBLIC_CAMP`, missing diagnostics elevate epistemic uncertainty ($U_t \ge 0.65$). The system explicitly reflects this:
$$\text{Care Recommendation} = f(\text{Risk Score}, U_t)$$
When $U_t$ is high, the system suppresses confident definitive treatment suggestions and surfaces **Verification & Triage-to-Safety Actions** (`ORDER_POC_GLUCOSE`, `VERIFY_BILATERAL_BREATH_SOUNDS`, `REFER_FOR_IMAGING`).

---

## 8. FACILITYGRAPH Environmental Modulation

The facility capability graph ($\text{FACILITYGRAPH}$) models resource states, equipment availability, and referral destination readiness.

### 8.1 Capability Status Taxonomy
Every capability node (e.g., `CAP_ICU_BED`, `CAP_OXYGEN_SUPPLY`, `CAP_BLOOD_BANK`, `CAP_SNAKE_ANTIVENOM`) is assigned an explicit verification state:

```
┌───────────────┬─────────────────────────────────────────────────────────────┐
│ Status Code   │ Operational Meaning                                         │
├───────────────┼─────────────────────────────────────────────────────────────┤
│ `VERIFIED`    │ Telemetry or authorized staff updated within $< 60$ minutes │
│ `KNOWN`       │ Confirmed static baseline within current shift ($< 8$ hours)│
│ `STALE`       │ No capability refresh for $> 12$ hours; reliability suspect │
│ `CONFLICTING` │ Differing reports between dispatch desk and receiving ward  │
│ `UNKNOWN`     │ Zero capability telemetry available; assumed unavailable    │
└───────────────┴─────────────────────────────────────────────────────────────┘
```

### 8.2 Representation & Handling of Stale Facility Data
- If a receiving tertiary hospital's ICU bed availability has not been verified within 4 hours, its node status is automatically downgraded to `STALE`.
- **System Behavior:** CLINOVA does not silently assume the bed exists. When generating referral recommendations, the UI displays an amber warning:
  > `⚠️ Tertiary Hospital A: ICU Status STALE (Last verified 6h ago). Telephonic bed confirmation required before dispatch.`
- The system prioritizes destinations with `VERIFIED` capabilities over closer facilities with `STALE` or `CONFLICTING` data.

---

## 9. ORCHESTRATION Action Constraints per Environment

The clinical orchestration engine generates six primary candidate actions: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, and `REFER`. Environmental constraints restrict and prioritize these actions:

```
┌─────────────┬────────────────────────────────────────────────────────────────────────┐
│ Environment │ Environmental Orchestration Constraints & Policy Overrides             │
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **Gov Hosp**│ • `OBSERVE` constrained by triage observation bed saturation.          │
│             │ • `ESCALATE` prioritizes internal emergency resuscitation bay.         │
│             │ • `REFER` restricted to specialized tertiary medical college transfers.│
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **PHC**     │ • `OBSERVE` strictly capped at $< 4$ hours for uncomplicated rehydration│
│             │ • `REFER` triggered early whenever condition requires missing labs/OT.  │
│             │ • `VERIFY` prioritizes simple bedside physical exam maneuvers.          │
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **Pub Camp**│ • `OBSERVE` is completely DISABLED (zero holding capacity).            │
│             │ • `ASK` heavily constrained by the 60-second encounter time budget.    │
│             │ • `REFER` generates outward batch digital passes to local PHC network. │
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **Company** │ • `CONTINUE` supports ergonomic workplace modifications and rest.      │
│             │ • `REFER` routes to private empanelled cashless tertiary hospitals.    │
│             │ • `ASK` enforces DPDP non-clinical privacy boundaries.                 │
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **Indust.** │ • `ESCALATE` triggers immediate sirens, ALS ambulance, and ERT team.    │
│             │ • `REFER` auto-filters regional network for specialized Burn/Trauma ICU│
│             │ • `ASK` suppresses non-essential history during active hemorrhage.     │
├─────────────┼────────────────────────────────────────────────────────────────────────┤
│ **Campus**  │ • `OBSERVE` utilizes campus infirmary beds for temporary isolation.    │
│             │ • `CONTINUE` coordinates academic medical leave certificates.          │
│             │ • `REFER` routes to municipal medical college or affiliated hospital.  │
└─────────────┴────────────────────────────────────────────────────────────────────────┘
```
