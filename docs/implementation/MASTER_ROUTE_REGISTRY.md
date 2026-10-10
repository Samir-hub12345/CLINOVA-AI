# CLINOVA AI — Master Route Registry
> **Document ID:** `DOC-REGISTRY-01`  
> **Status:** VERIFIED & SYNCHRONIZED  
> **Repository Target:** `master` (Authoritative Main Platform)  
> **Deployment Production Target:** https://clinova-ai-pink.vercel.app/  
> **Reference Platform:** https://clinova-ai.vercel.app  

---

## 1. Executive Summary & Routing Architecture

The CLINOVA AI routing architecture operates across **5 distinct operational bands** and **18 verified App Router routes**, ensuring strict zero-drift mapping between the user experience and backend clinical governance.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA 5-BAND ROUTING ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  BAND 1: PUBLIC & PATIENT INGRESS                                           │
│          /                               Public Landing & Overview          │
│          /login                          Split-Pane Role-Governed Auth      │
│          /register                       Institutional Onboarding Gateway   │
│          /about, /disclaimer, /privacy   Compliance, Architecture & Ethics  │
│          /patient                        Patient Care Navigation Portal     │
│          /patient/intake                 10-Step Adaptive Intake Wizard     │
│          /patient/case/[caseId]          Private Patient Status & Care Plan │
├─────────────────────────────────────────────────────────────────────────────┤
│  BAND 2: RECEPTION & TRIAGE GATEWAY                                         │
│          /staff                          Clinical Gateway & Persona Hub     │
│          /staff/reception                Reception Desk & Pathway Assignment│
│          /staff/triage                   Nurse Worklist, NEWS2 & Red Flags  │
├─────────────────────────────────────────────────────────────────────────────┤
│  BAND 3: CLINICIAN REVIEW & DECISION WORKBENCH                              │
│          /staff/review                   Attending Verification Queue       │
│          /staff/cases/[caseId]           3-Panel Asymmetric Doctor Workbench│
├─────────────────────────────────────────────────────────────────────────────┤
│  BAND 4: ORCHESTRATION & TRANSFERS                                          │
│          /facilities                     Regional Capabilities & Bed Telemetry│
│          /referrals                      SBAR Transfer Dispatch Workbench   │
├─────────────────────────────────────────────────────────────────────────────┤
│  BAND 5: CONTINUITY, GOVERNANCE & TELEMETRY                                 │
│          /system                         SHA-256 Audit Ledger & Sync Engine │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete 18-Route Master Registry

| Route Path | Band | Clinical / Operational Purpose | Allowed Roles | Originating Controls | Destination / Next Route | Required Data / State | Backend Dependency | Implementation & Test Status |
|:---|:---:|:---|:---|:---|:---|:---|:---|:---:|
| `/` | 1 | Platform overview, signature metric tiles, schedule table, task queue, and workflow continuum | Public, All Authenticated | Header Logo, Direct URL, Nav Links | `/staff/cases/*`, `/staff/triage`, `/staff/reception`, `/patient/intake`, `/login` | None (Static SSR with Client Interactive Widgets) | `GET /auth/me`, `GET /cases/queue` | **VERIFIED** (Static 9.46 kB, 0-flicker) |
| `/login` | 1 | Split-pane authentication, role tab switcher, demo quick login, password toggle, credential recovery | Public, All Roles | TopBar Sign-In, Hero Staff Button, Session Guard Expired | Authorized Role Dashboard (`/staff/*`, `/facilities`, `/patient`, `/system`) | Username, Password | `POST /auth/login`, `POST /auth/switch-persona` | **VERIFIED** (10/10 Auth Stability Tests) |
| `/register` | 1 | Institutional access policy gate, walk-in patient intake route, reception desk dispatch | Public | TopBar, Landing Page Hero | `/patient/intake` or `/staff/reception` | None | None (Informational Gate & Pathway Router) | **VERIFIED** (Static 2.86 kB) |
| `/about` | 1 | 4 Architectural Pillars, zero-cloud bounds, continuous care intelligence definition | Public | Footer Link, TopBar Brand | `/`, `/privacy`, `/disclaimer` | None | None (SSR) | **VERIFIED** (Static 165 B) |
| `/disclaimer` | 1 | Non-diagnostic legal disclaimer, NMC 2023 compliance, clinician final authority notice | Public | Footer Link, Alert Banners | `/` | None | None (SSR) | **VERIFIED** (Static 131 B) |
| `/privacy` | 1 | DPDP Act 2023 compliance, PII redaction rules, ephemeral retention, cryptographic ledger | Public | Footer Link | `/system` | None | None (SSR) | **VERIFIED** (Static 131 B) |
| `/patient` | 1 | Patient self-service ingress, digital registration CTA, token status lookup form | Public, PATIENT | TopBar "Patient Intake", Hero CTA | `/patient/intake`, `/patient/case/[caseId]` | Patient Token / Case Reference | `GET /cases/{id}` | **VERIFIED** (Static 3.4 kB) |
| `/patient/intake` | 1 | 10-step patient intake wizard (Consent, Odia/Hindi voice STT, adaptive follow-up, report upload) | Public, PATIENT, NURSE | Landing CTA, `/register`, `/patient` | `/patient/case/[caseId]` upon submit | Patient Demographics, Chief Complaint, Consent | `POST /intake/submit`, `POST /intake/voice`, `POST /documents/upload` | **VERIFIED** (Static 10.5 kB, Offline Queue Support) |
| `/patient/case/[caseId]` | 1 | Patient private case view: Acuity tier, care team, approved care plan, vernacular instructions, PDF download | PATIENT, CLINICIAN, NURSE | Patient token lookup, SMS link, Intake completion | PDF Download, Home | `caseId` (URL Param) | `GET /caregraph/{id}`, `GET /cases/{id}/report/pdf` | **VERIFIED** (Dynamic SSR, 1.83 kB) |
| `/staff` | 2 | Staff role gateway: Quick launch cards for Triage Queue, Doctor Workbench, Reception Desk, Referrals | Authenticated Staff (NURSE, CLINICIAN, RECEPTIONIST, ADMIN) | TopBar, Direct URL | `/staff/reception`, `/staff/triage`, `/staff/review`, `/facilities` | Active Persona JWT Session | `RoleGuard` + `GET /auth/personas` | **VERIFIED** (Static 6.08 kB) |
| `/staff/reception` | 2 | Patient registration, consent capture, duplicate search, OPD vs Emergency staff-assigned pathway | RECEPTIONIST, CLINICIAN, SYSTEM_ADMIN | TopBar "Reception", Staff Hub, Landing Table Footer | `/staff/triage`, `/staff/cases/[caseId]` | Demographics, Pathway selection, Consent | `POST /intake/submit`, `GET /cases/queue` | **VERIFIED** (Static 10.4 kB) |
| `/staff/triage` | 2 | High-volume nurse worklist, bedside ABCD vitals capture, deterministic NEWS2 & Shock Index scoring | NURSE, CLINICIAN, SYSTEM_ADMIN | TopBar "Nurse Triage", Staff Hub, Metric Card | `/staff/cases/[caseId]`, `/patient/case/[caseId]` | Bedside Vitals (HR, BP, SpO2, RR, Temp, AVPU) | `GET /cases/queue`, `POST /cases/{id}/vitals` | **VERIFIED** (Static 7.33 kB) |
| `/staff/review` | 3 | Attending physician verification worklist, multi-case triage status, red-flag prioritization | CLINICIAN, DOCTOR, SYSTEM_ADMIN | TopBar "Doctor Review", Staff Hub, Metric Card | `/staff/cases/[caseId]` | Filter params (acuity, red flags) | `GET /cases/review-queue` | **VERIFIED** (Static 4.87 kB) |
| `/staff/cases/[caseId]` | 3 | 3-panel asymmetric Doctor Workbench: Clinical timeline, provenance badges, AI advisory, sign-off | CLINICIAN, DOCTOR, SYSTEM_ADMIN | Schedule row click, Review worklist, Triage handoff | `/referrals`, `/patient/case/[caseId]`, PDF Export | `caseId` (URL Param), Decision payload | `GET /caregraph/{id}`, `POST /cases/{id}/decision`, `POST /evidence/{id}/verify` | **VERIFIED** (Dynamic SSR, 18.6 kB) |
| `/facilities` | 4 | Regional facility network directory, ICU/Ward bed telemetry, operational capabilities, equipment health | FACILITY_ADMIN, SYSTEM_ADMIN, CLINICIAN, NURSE | TopBar "Facilities", TopBar Drawer Button | `/referrals` | Facility search / tier filters | `GET /facilities`, `GET /facilities/{id}` | **VERIFIED** (Static 4.75 kB) |
| `/referrals` | 4 | Inter-hospital transfer coordination, feasibility ranking, transit route mapping, SBAR dispatch | REFERRAL_COORDINATOR, CLINICIAN, FACILITY_ADMIN | TopBar "Referrals", Workbench Disposition, TopBar Drawer | External facility handoff, SBAR PDF print | Target Facility ID, Transfer Packet | `GET /referrals`, `POST /referrals/dispatch` | **VERIFIED** (Static 6.22 kB) |
| `/system` | 5 | Cryptographic SHA-256 audit ledger, edge node offline synchronization status, tamper detection | SYSTEM_ADMIN, AUDITOR | TopBar "System", Activity Card Footer, TopBar Drawer | Export audit logs | Audit filter query | `GET /audit/events`, `GET /sync/status` | **VERIFIED** (Static 7.72 kB) |
| `/_not-found` | 1 | Graceful 404 handler with clinical safe recovery navigation | Public | Invalid URL path | `/` | None | None | **VERIFIED** (Static 131 B) |

---

## 3. Route Guard & Protection Policies

1. **RoleGuard Client Boundary (`RoleGuard.tsx`):**
   - Synchronously reads `sessionStorage.getItem("clinova_user")` during initial render.
   - Prevents unauthenticated flashes, redirects unauthorized roles to clean institutional fallback with explicit permission explanation.
2. **Authoritative Backend Boundary (`policy.py` & `rbac.py`):**
   - The server validates Bearer JWT on every HTTP request.
   - Patient horizontal isolation: Patient A cannot access Patient B (HTTP 404/403 masked).
   - Vertical isolation: Nurse cannot sign off clinical decisions (HTTP 403); Receptionist cannot modify vitals (HTTP 403); Sysadmin cannot make clinical decisions (HTTP 403).
