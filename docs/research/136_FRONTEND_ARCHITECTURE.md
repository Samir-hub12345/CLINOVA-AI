# CLINOVA AI — Frontend Architecture Specification

> **Document ID:** `RES-136`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Frontend Engineering, Clinical UX & Human Factors Architecture Group  

---

## 1. Frontend Technology Stack & Design System

The CLINOVA AI user interface is built as a responsive, high-performance web application designed for fast rendering, touch-friendly tablet usability in rural clinics, and zero-latency clinical workflow execution:

- **Framework:** Next.js 15+ (App Router architecture)
- **Language:** TypeScript 5.6+ with strict type checking (`noImplicitAny: true`, `strictNullChecks: true`)
- **Rendering Engine:** React 19 (Server Components for static layout shells; Client Components for rich interactive workbenches)
- **Styling:** Tailwind CSS with standardized clinical design tokens:
  - *Clinical Slate / Neutral:* `#0f172a` (slate-900), `#1e293b` (slate-800), `#f8fafc` (slate-50)
  - *Acuity Tier Critical (Red Flag):* `#dc2626` (red-600), `#fef2f2` (red-50)
  - *Acuity Tier Urgent (Amber Warning):* `#d97706` (amber-600), `#fffbeb` (amber-50)
  - *Acuity Tier Moderate (Yellow Alert):* `#ca8a04` (yellow-600), `#fefce8` (yellow-50)
  - *Acuity Tier Routine (Clinical Blue/Green):* `#2563eb` (blue-600), `#16a34a` (green-600)
- **Icons:** `lucide-react` (strictly no informal emojis as clinical symbols)
- **Mapping:** `leaflet` and `react-leaflet` with OpenStreetMap (OSM) vector tiles for facility networks
- **Audio Capture:** Native Web Audio / MediaStream API with offline WAV encoding

---

## 2. Application Shell & Route Hierarchy

The frontend enforces strict role-based access control (RBAC) mapping directly to the three approved core interfaces and three supporting drawers:

```
frontend/src/app/
├── layout.tsx                     # Global App Shell (Header, Environment Badge, Connectivity Status)
├── page.tsx                       # Smart Landing / Role Dispatcher (Redirects to active role workbench)
├── (auth)/
│   └── login/page.tsx             # Staff Authentication & Role Selection Portal
├── (clinical)/
│   ├── intake/                    # 1. Patient Intake Portal (Patient/Caregiver/ASHA)
│   │   ├── page.tsx               # Multimodal Intake Form (Symptom Text, Voice Capture, Slip Upload)
│   │   └── success/page.tsx       # Intake Confirmation, Token Slip Display & Print View
│   ├── triage/                    # 2. Nurse Triage Workstation (Staff Nurse)
│   │   ├── page.tsx               # Nurse Worklist & Active Triage Dashboard
│   │   └── [caseId]/page.tsx      # Vitals Acquisition, Missing Data Resolution, Physical Exam Entry
│   └── doctor/                    # 3. Doctor Reviewer Workbench (RMP / Medical Officer)
│       ├── page.tsx               # Prioritized Doctor Queue (Dynamic Acuity & Wait Ranking)
│       └── [caseId]/page.tsx      # Comprehensive Master Case Review, CareGraph, Side-by-Side Verification
└── api/                           # Next.js BFF (Backend-for-Frontend) Proxy Routes
    └── auth/callback/route.ts     # Supabase Auth Session Callback
```

### Supporting Drawers (Global Slide-Over Drawers)
Rather than fragmenting navigation into separate top-level pages, secondary clinical and administrative workflows are encapsulated in **slide-over drawers** accessible directly from the Doctor Workbench and Nurse Workstation:
1. **Referral Coordination Drawer:** Inter-facility transfer synthesis, destination capability matching via FACILITYGRAPH, SBAR note generation, and transport dispatch.
2. **Facility Resources Drawer:** Local facility bed status, operational capabilities (ICU, blood bank, CT scanner), specialist availability, and oxygen pressure telemetry.
3. **Audit & Developer Console Drawer:** Merkle hash chain verification, raw event stream inspection, Section 63 BSA compliance certification preview, and local offline sync status.

---

## 3. The Three Approved Core Interfaces

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA THREE CORE INTERFACES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ INTERFACE 1: PATIENT INTAKE PORTAL ]                                      │
│  ├── Multilingual Support (English, Hindi, Odia)                            │
│  ├── Voice Symptom Recording (Press-and-talk vernacular audio capture)      │
│  ├── Paper Record Photo / PDF Upload (Prescriptions, prior lab slips)       │
│  ├── Plain Text Symptom Entry (Auto-expanding narrative box)                │
│  ├── Mandatory Consent Gate (Digital/Verbal consent toggle)                 │
│  └── Emergency Quick-Token Generation (< 200ms anonymous ticket)            │
│                                                                             │
│  [ INTERFACE 2: NURSE TRIAGE WORKSTATION ]                                  │
│  ├── Active Inflow Patient Queue (Arrival sorting & triage readiness)       │
│  ├── Serial Vitals Acquisition Form (HR, SBP, DBP, SpO2, RR, Temp, AVPU)   │
│  ├── Deterministic Early Warning Badges (NEWS2 score, Shock Index alert)    │
│  ├── Missing-Data Resolution Worklist (Tier 1 vital gap prompts)            │
│  └── Physical Nurse Validation Gate (Affirmative check before doctor queue) │
│                                                                             │
│  [ INTERFACE 3: DOCTOR REVIEWER WORKBENCH ]                                 │
│  ├── Multi-Dimensional Prioritized Queue (Acuity tier, wait time, slope)    │
│  ├── One-Screen Holistic Clinical Summary (Longitudinal Master Case view)   │
│  ├── CAREGRAPH Visual Trajectory Widget (Delta vitals & physiological slope)│
│  ├── Perceptual Side-by-Side Crop Viewer:                                   │
│  │   • Visual [0, 1000] Bounding Box crop alongside extracted lab value     │
│  │   • Acoustic 3-second audio snippet player alongside transcribed symptom │
│  ├── Evidence Conflict Adjudication Panel (Side-by-side conflicting facts)   │
│  ├── Multi-Graph Orchestration Advisory Panel (Candidate clinical actions)  │
│  └── Formal Decision & Sign-Off Controls (Accept, Override, Prescribe, Sign)│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Server vs. Client Component Boundaries & Security Invariants

Next.js App Router enforces strict isolation between server-side data fetching and client-side user interactivity:

```
[ SERVER COMPONENT LAYER (Default) ]
├── Fetches Master Case data from Backend API using internal network / localhost
├── Enforces session claims and role validation before rendering
├── Never leaks service-role keys, private environment variables, or database credentials
├── Renders static page skeleton, patient header, and initial layout
└── Passes sanitized props to Client Components
       │
       ▼ Props Boundary (Sanitized JSON)
[ CLIENT COMPONENT LAYER ("use client") ]
├── Interactive form controls, audio recorder, and canvas slip cropper
├── Side-by-side modal drawers (Referral, Facility, Audit)
├── Real-time queue sorting and dynamic timer ticks
└── Mutation handlers calling Backend REST endpoints via authenticated fetch
```

### Security Invariants on the Frontend
- **Invariant FE-1 (No Secret Leakage):** The frontend bundle MUST NEVER contain Supabase `service_role` keys, backend admin passwords, or master encryption keys. Only public anonymous keys (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) or session JWTs are exposed.
- **Invariant FE-2 (No Client-Only Authorization):** Route guards in Next.js middleware provide UI redirection for convenience, but the Backend API independently authenticates and authorizes every incoming HTTP request.

---

## 5. State Management & Form Handling Architecture

To prevent state desynchronization and handle rural edge conditions cleanly:
1. **Server State (Remote Clinical Data):**
   - Managed via React Query (`@tanstack/react-query`) or SWR.
   - Cached by `caseId` with optimistic updates for non-clinical UI actions (e.g., toggling drawer views).
   - Dynamic polling or WebSocket subscription invalidates stale cache when new vitals arrive.
2. **Form State (Active Triage & Intake):**
   - Managed using React Hook Form (`react-hook-form`) with Zod schema validation matching backend Pydantic models.
   - Auto-saves dirty drafts to browser `localStorage` or `IndexedDB` every 5 seconds to prevent data loss if a browser tab accidentally closes.
3. **Queue State (Doctor & Nurse Queue):**
   - Local timer ticks (1-second intervals) recalculate elapsed wait time dynamically in memory without re-fetching entire database rows.

---

## 6. Environment Awareness & Clinical Safety Banners

The frontend dynamically displays the active operational environment injected via environment configuration (`NEXT_PUBLIC_ENVIRONMENT`):
- `ENV_GOV_HOSPITAL`: Government District Hospital (High-volume ED queue, specialist routing enabled).
- `ENV_PHC`: Primary Health Centre (Single-doctor queue, referral drawer emphasized).
- `ENV_PUBLIC_CAMP`: Outreach Health Camp (Offline-first banner, batch intake mode).
- `ENV_COMPANY_CLINIC`: Corporate Occupational Clinic (Shift notes, ergonomics intake).
- `ENV_INDUSTRIAL_HEALTH`: Industrial Health Centre (Occupational hazard screening, chemical exposure tags).
- `ENV_CAMPUS_HEALTH`: University Student Health Centre (Acute sports injuries, student ID fields).

### Non-Diagnostic Clinical Safety Banner
Every screen features a persistent, non-dismissible top-level safety banner:
> ⚠️ **CLINOVA AI Educational Prototype & Clinical Advisory System — Non-Diagnostic Only. All recommendations require verification by a Registered Medical Practitioner (RMP).**

---

## 7. Offline Client Behavior & Emergency Resuscitation Mode

1. **Connectivity Degradation:**
   - A global `ConnectivityStatusIndicator` component probes `/api/health` every 10 seconds.
   - When offline, a prominent Amber banner notifies staff: *"Operating in Offline Local Mode. Records saved to local clinic server."*
2. **Emergency Mode (Red Flag Flow):**
   - A single prominent red button (`EMERGENCY CASUALTY INTAKE`) is permanently accessible from the header.
   - Tapping generates an instant anonymous emergency token (`EMG-YYYYMMDD-XXXX`) in $< 200\text{ms}$, immediately bypassing all non-essential intake questionnaires and placing the case at the absolute top of the doctor and resuscitation queue.
