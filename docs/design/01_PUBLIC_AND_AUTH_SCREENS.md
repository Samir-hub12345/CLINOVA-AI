# CLINOVA AI — Design Specifications: Cluster 1 (Public & Authentication)

> **File:** `docs/design/01_PUBLIC_AND_AUTH_SCREENS.md`  
> **Screens Covered:** Screen 01, Screen 02, Screen 03, Screen 04  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 Design Source of Truth  

---

## Screen 01: Public Landing Page

### 1. Specification
- **Route:** `/`
- **Purpose:** Communicate institutional identity, explain the paradigm shift from isolated triage to continuous care intelligence, and provide portal entry for clinicians, researchers, and public health officials.
- **Actor:** Public, Healthcare Leadership, Clinicians, Evaluators, Patients.
- **Entry Condition:** Publicly accessible.
- **Inputs:** None (Read-only presentation with navigation buttons).
- **Outputs:** Platform positioning statement, four innovation pillar overviews, BPUT baseline compliance badges, interactive platform demo entry.
- **Actions:** "Launch Clinical Portal" (redirects to `/login`), "Explore Technology & Innovation" (redirects to `/innovation`), "View Live Simulated Telemetry" (scrolls to live ticker).
- **Navigation:** Links to `/innovation`, `/login`, `/encounter/new`.
- **States:**
  - *Normal:* Clean, institutional hero section with live simulated metrics ticker.
  - *Loading:* Fast SSR render; zero skeleton delay.
  - *Error:* Static fail-safe HTML if web server is degraded.
  - *Mobile:* Hero collapses vertically; navigation collapses to standard accessible mobile menu.
- **Graph Linkage:** High-level educational introduction to CAREGRAPH, FACILITYGRAPH, and SIGNALGRAPH.

### 2. Wireframe (Screen 01)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Technology   Baseline   Demo   [ CLINICAL LOGIN ]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ADAPTIVE CLINICAL CARE INTELLIGENCE & NAVIGATION PLATFORM                 │
│                                                                             │
│   From Isolated Triage  ──>  To Continuous Care Intelligence               │
│                                                                             │
│   CLINOVA connects patient risk, evidence uncertainty, facility capability, │
│   system demand and real outcomes to identify the safest achievable care    │
│   pathway while keeping qualified healthcare professionals in control.      │
│                                                                             │
│   [ LAUNCH CLINICAL WORKSPACE ]       [ EXPLORE THE 4 PILLARS ]             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│   LIVE TELEMETRY (SIMULATED): 1,420 Enounters | 8 Facilities | 0 Paid APIs  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────┐ ┌───────────────────────┐ ┌──────────────────┐  │
│   │ 1. CAREGRAPH          │ │ 2. FACILITYGRAPH      │ │ 3. SIGNALGRAPH   │  │
│   │ Dynamic Patient State,│ │ Resource Feasibility, │ │ Regional Disease │  │
│   │ Uncertainty & Vitals  │ │ ICU Beds & Staff      │ │ Outbreak Signals │  │
│   └───────────────────────┘ └───────────────────────┘ └──────────────────┘  │
│                                                                             │
│   [ BPUT MANDATORY BASELINE: B01-B18 FULLY INTEGRATED IN ₹0 OPEN ARCH ]     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Educational Prototype Only | Non-Diagnostic | Qualified Human Gate Enforced│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 02: Product & Innovation Page

### 1. Specification
- **Route:** `/innovation`
- **Purpose:** Technical deep-dive for hackathon evaluators, researchers, and clinical informaticists detailing the mathematical and architectural foundations of the continuous care loop.
- **Actor:** Evaluators, Researchers, Medical Officers, System Architects.
- **Entry Condition:** Publicly accessible.
- **Inputs:** Interactive tab selector (CareGraph / FacilityGraph / SignalGraph / Orchestration).
- **Outputs:** In-depth architectural diagrams, mathematical formulations (VOI ranking, z-score clustering, Haversine routing), and comparative table (Isolated Triage vs. CLINOVA).
- **Actions:** "Download Architectural Whitepaper", "Switch Graph Pillar View", "Return to Home".
- **Navigation:** Links to `/`, `/login`.
- **States:**
  - *Normal:* Interactive tabbed layout detailing each graph's inputs, internal algorithms, and outputs.
  - *Mobile:* Tabs convert to vertical collapsible accordion sections.
- **Graph Linkage:** Authoritative interactive visualizer of all four graphs.

### 2. Wireframe (Screen 02)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI  < Back to Home                       [ CLINICAL LOGIN ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CONTINUOUS CARE INTELLIGENCE: ARCHITECTURAL SPECIFICATION                 │
│                                                                             │
│   [ CAREGRAPH ]     [ FACILITYGRAPH ]     [ SIGNALGRAPH ]   [ ORCHESTRATION]│
│   ═════════════                                                             │
│                                                                             │
│   CAREGRAPH: DYNAMIC PATIENT STATE & UNCERTAINTY ENGINE                     │
│                                                                             │
│   Unlike static triage protocols that calculate a single priority color,    │
│   CAREGRAPH models longitudinal physiological trajectory:                   │
│                                                                             │
│   Formula: ΔAcuity = w1·ΔShockIndex + w2·ΔSpO2⁻¹ + w3·ΔMEWS + w4·ΔGCS⁻¹     │
│                                                                             │
│   ┌────────────────────────────────┐ ┌───────────────────────────────────┐  │
│   │ EVIDENCE PROVENANCE LEDGER     │ │ FIRST-CLASS UNCERTAINTY PROFILE   │  │
│   │ • Source Modality Tracking     │ │ • Known vs Unknown Parameters     │  │
│   │ • Algorithmic Quality Scores   │ │ • Contradiction Identification    │  │
│   │ • Verified Clinician Sign-off  │ │ • Next-Best Information (NBI)     │  │
│   └────────────────────────────────┘ └───────────────────────────────────┘  │
│                                                                             │
│   [ VIEW FACILITYGRAPH SPECIFICATION ]    [ VIEW ORCHESTRATION ENGINE ]     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 03: User Login Screen

### 1. Specification
- **Route:** `/login`
- **Purpose:** Authenticate clinical and administrative personnel using Supabase Auth or local development credentials.
- **Actor:** All staff roles (Doctor, Nurse, Admin, Referral Staff, Researcher).
- **Entry Condition:** Unauthenticated session.
- **Inputs:** Email address, password, optional facility selector dropdown.
- **Outputs:** Error notifications for invalid credentials; automatic redirection to role selection or default dashboard.
- **Actions:** "Sign In", "Switch to Offline / Demo Mode", "Forgot Password".
- **Navigation:** On success, redirects to `/select-role` or assigned role workbench.
- **States:**
  - *Normal:* Clean, centered clinical authentication card.
  - *Loading:* Button shows spinner with "Authenticating..."; inputs disabled.
  - *Error:* High-contrast alert badge: "Invalid clinical credentials. Please verify your facility email."
  - *Mobile:* Form expands to full width with 48px touch targets.
- **Graph Linkage:** Establishes `actor_id` and `actor_role` required for all downstream audit logs.

### 2. Wireframe (Screen 03)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                            ┌──────────────────────┐                         │
│                            │   [LOGO] CLINOVA AI  │                         │
│                            │ Clinical Care Portal │                         │
│                            ├──────────────────────┤                         │
│                            │ Facility Email       │                         │
│                            │ [ dr.mohapatra@phc ] │                         │
│                            │                      │                         │
│                            │ Security Password    │                         │
│                            │ [ •••••••••••••••• ] │                         │
│                            │                      │                         │
│                            │ Assigned Facility    │                         │
│                            │ [ Capital Dist Hosp▼]│                         │
│                            │                      │                         │
│                            │ [ SECURE SIGN IN ]   │                         │
│                            │                      │                         │
│                            │ ─── OR DEMO LOGIN ───│                         │
│                            │ [ Quick Doctor Demo] │                         │
│                            │ [ Quick Nurse Demo ] │                         │
│                            └──────────────────────┘                         │
│                                                                             │
│      Compliance: DISHA / DPDP 2023 | 256-Bit TLS | Audit Logging Active     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 04: Role Selection Screen

### 1. Specification
- **Route:** `/select-role`
- **Purpose:** In multi-role development environments or shared hospital workstations, allow authenticated staff to select their operational clinical persona.
- **Actor:** Authenticated users with multi-role permissions.
- **Entry Condition:** Authenticated session.
- **Inputs:** Clickable role selection card.
- **Outputs:** Grid of available personas with description and permission scope.
- **Actions:** "Enter as Medical Officer", "Enter as Triage Nurse", "Enter as Referral Coordinator", "Enter as Facility Administrator".
- **Navigation:** Redirects to the respective role's primary workbench route.
- **States:**
  - *Normal:* Four to six distinct role cards with clear icons and authority boundaries.
  - *Permission Denied:* In production, cards for unauthorized roles appear grayed out with a lock badge.
  - *Mobile:* Vertical stack of large touch-friendly cards.
- **Graph Linkage:** Binds session to the **Role-Permission Matrix** (`docs/03_ROLE_PERMISSION_MODEL.md`).

### 2. Wireframe (Screen 04)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] CLINOVA AI       Logged in: Dr. S. Mohapatra         [ SIGN OUT ]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SELECT OPERATIONAL CLINICAL WORKSPACE                                     │
│   Select your active duty role for this terminal session:                   │
│                                                                             │
│   ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│   │ 👨‍⚕️ MEDICAL OFFICER           │  │ 👩‍⚕️ TRIAGE NURSE / ANM        │        │
│   │ Comprehensive Case Review,   │  │ Multimodal Ingestion, Vitals │        │
│   │ CAREGRAPH, Verification Gate,│  │ Checklist, Red-Flag Triage,  │        │
│   │ Care Pathway Disposition     │  │ Missing Data Collection      │        │
│   │ [ ENTER DOCTOR WORKBENCH ]   │  │ [ ENTER INTAKE WORKLIST ]    │        │
│   └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                             │
│   ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│   │ 🚑 REFERRAL COORDINATOR      │  │ 🏥 FACILITY ADMINISTRATOR    │        │
│   │ Regional Transfer Logistics, │  │ Bed Board, Resource Roster,  │        │
│   │ Transport Dispatch, Inter-   │  │ Operational Congestion,      │        │
│   │ Facility Handoff Tracking    │  │ Referral Turnaround Audits   │        │
│   │ [ ENTER REFERRAL DESK ]      │  │ [ ENTER FACILITY ADMIN ]     │        │
│   └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
