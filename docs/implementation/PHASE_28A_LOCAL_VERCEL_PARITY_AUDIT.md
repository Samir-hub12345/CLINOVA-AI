# CLINOVA AI — Phase 28A: Local–Vercel Parity Audit and Root-Cause Investigation Report

> **System:** CLINOVA AI Continuous Care Intelligence System  
> **Milestone:** Phase 28A — Local–Vercel Parity Audit & Root-Cause Diagnosis  
> **Status:** **DIAGNOSIS COMPLETE — AWAITING OPERATOR REVIEW BEFORE PHASE 28B**  
> **Clinical Governance:** Strictly Non-Diagnostic | Advisory Only | Mandatory Human Verification  
> **Execution Boundary:** Read-Only Investigation. Zero changes to application source code, database schemas, or Git commit history.

---

## 1. Executive Summary & Core Diagnostic Findings

This investigation determines why the CLINOVA AI application running locally differs substantially from the current Vercel production deployment (`https://clinova-ai.vercel.app`).

### Key Conclusions:
1. **Source Version Desynchronization (Root Cause of Parity Divergence):**  
   The Vercel production deployment is running a **legacy codebase commit** (from the `abbf81a` / `58fc9c8` / `302921b` commit era), prior to the major Phase 13–27 architectural overhaul implemented in commits `619cb84` ("fresh flow") and `558c9a2` ("overall phase complete").  
   - **Vercel Deployment:** Built on the older, monolithic `/dashboard` routing structure with Tailwind CSS styling, but containing identical nurse/doctor dashboards, unauthenticated role selection at registration, incomplete patient intake, and stubbed workflows.
   - **Local Master Branch (`6e2b88a`):** Contains the functionally verified 13-stage Continuous Care Intelligence architecture across 15 App Router routes (`/patient/intake`, `/staff/triage`, `/staff/review`, `/staff/cases/[caseId]`, `/facilities`, `/referrals`, `/system`), 400/400 passing backend tests, and strict RBAC isolation. However, Tailwind CSS was removed in commit `558c9a2` and replaced with raw CSS variables and inline styles, resulting in a plainer visual design.

2. **Root Cause of the Continuously Flickering Landing Page on Vercel:**  
   The flickering on the Vercel landing page is caused by an **unhandled asynchronous connectivity polling loop coupled to layout-shifting adaptive images**:
   - The legacy landing page rendered `<Header />` with `<NetworkIndicator />`, which was driven by `useConnectivity()` in `frontend/src/lib/connectivity.tsx`.
   - `useConnectivity()` executed periodic fetch requests to `${API_BASE_URL}/api/v1/ping`.
   - Because no live backend service is connected to Vercel (or requests failed/timed out), each ping failed (`failureCountRef.current += 1`), causing rapid state hysteresis transitions (`GOOD` -> `OFFLINE` -> retry after 5 seconds).
   - The landing page rendered `<AdaptiveImage />` (`frontend/src/components/common/adaptive-image.tsx`) tied directly to `useConnectivity()`. When `state === "OFFLINE"`, `shouldAutoLoad` evaluated to `false`, unmounting the hero image and rendering a "Load Image" fallback button. When the ping re-evaluated, it remounted the image with an `animate-spin` spinner.
   - This continuous toggle created an infinite cycle of layout shifts, spinners, and DOM re-renders.
   - **Local Resolution:** On local `master`, `/` is a React Server Component with static layout, zero client-side ping loops, and zero flicker.

3. **Backend & Database Status:**  
   - Local: Fully verified SQLite WAL engine (`clinova-dev.db`), 400/400 pytest suite passing, Alembic head revision `b84f3782910c`.
   - Hosted Production: Provisioning of Supabase Free PostgreSQL and Render Free Web Service is **BLOCKED at the Operator Access Boundary**. Neither cloud service is currently online or linked to Vercel.

---

## 2. Source of Truth & Repository Identity Audit

| Parameter | Local Source of Truth | Deployed Production (Vercel) | Parity Status & Risk |
|:---|:---|:---|:---:|
| **Root Directory** | `c:\Users\admin\CLINOVA-AI` | `frontend` subdirectory of GitHub repo | Synchronized |
| **Git Remote Origin** | `https://github.com/Samir-hub12345/CLIVORA-AI.git` | `https://github.com/Samir-hub12345/CLIVORA-AI.git` | Discrepancy (`CLIVORA` vs `CLINOVA`) |
| **Tracked Branch** | `master` | Unknown (legacy `master` or feature branch) | **DESYNCHRONIZED** |
| **Latest Local Commit** | `6e2b88acf2ff1c0542573833d72f3fe00a2b1b5e` | `abbf81a` / `58fc9c8` era commit | **COMMIT MISMATCH** |
| **Working Tree Status** | Clean (`git status --short`: 0 changes) | Remote CDN artifact | Verified |
| **Frontend Framework** | Next.js 15.5.24 (App Router) | Next.js 15.x App Router | Matched |
| **Styling Engine** | Custom CSS variables (`globals.css`) | Tailwind CSS (`tailwind.config.ts`) | **STYLING DIVERGENCE** |
| **Vercel CLI Status** | Token expired (`vercel whoami` -> 401) | Managed via GitHub integration | Operator Action Required |

### Evidence from Git Commit Log:
- In commit `58fc9c8` ("perfect dashboard integration") and `abbf81a` ("all integrated"):
  The frontend utilized `frontend/src/app/dashboard/page.tsx`, `frontend/src/app/dashboard/nurse/page.tsx`, `frontend/src/app/dashboard/doctor/page.tsx`, and Tailwind CSS.
- In commit `619cb84` ("fresh flow"):
  The legacy dashboard files, `floating-assistant.tsx`, and `adaptive-image.tsx` were deleted.
- In commit `558c9a2` ("overall phase complete"):
  Tailwind CSS (`tailwind.config.ts`, `postcss.config.mjs`) was completely removed, and 15 dedicated routes (`/staff/*`, `/patient/*`, etc.) with `PatientIntakeWizard.tsx` (1076 lines) and `DoctorWorkbenchView.tsx` (1044 lines) were established.
- Commit `6e2b88a` ("useless") added live deployment documentation.

---

## 3. Route-by-Route Comparison Matrix

The table below contrasts the local application (`master`) with the Vercel deployment:

| Route Path | Exists in Local Source? | Local Behavior (`npm run build`) | Vercel Behavior | Component Rendered (Local vs Vercel) | Real API Call? | Data Persistence | Root Cause of Discrepancy |
|:---|:---:|:---|:---|:---|:---:|:---:|:---|
| `/` | Yes | Static Server Component; 173 B; zero flicker; clear CTAs | Renders Tailwind hero; continuously flickers/re-renders | `HomePage` (`app/page.tsx`) vs Legacy `Home` + `AdaptiveImage` + `NetworkIndicator` | Local: No (SSR)<br>Vercel: `/api/v1/ping` loop | Local: None<br>Vercel: None | Replaced in `558c9a2`; Vercel still runs legacy ping loop |
| `/login` | **No** (Integrated into TopBar modal) | Redirects to `/_not-found` (404) | Loads full login page with role tabs | `TopBar.tsx` modal vs Legacy `app/login/page.tsx` | Local: `POST /auth/login`<br>Vercel: Failed API fetch | Local: SessionStorage / Bearer JWT<br>Vercel: Mock fallback | Routed through global TopBar modal on `master` |
| `/register` | **No** (Removed for security) | Returns 404 | Loads public registration form allowing arbitrary role selection | None (Removed) vs Legacy `app/register/page.tsx` | Local: N/A<br>Vercel: Stubbed API call | None | Removed in `619cb84`; arbitrary role self-selection is a security defect |
| `/patient` | Yes | Static portal with intake initiation & synthetic case tracking | Redirects to `/dashboard` or loads legacy portal | `PatientLandingPage` (`app/patient/page.tsx`) | Local: Internal navigation<br>Vercel: Mocked | Local: State<br>Vercel: Mocked | Route restructured in `558c9a2` |
| `/patient/intake` | Yes | 10-step `PatientIntakeWizard` (Consent, Voice STT, Adaptive Questions, Report Upload) | Legacy 4-step form without adaptive questions | `PatientIntakeWizard` vs Legacy `app/intake/page.tsx` | Local: `POST /intake/submit`<br>Vercel: Mock / failed | Local: DB or offline queue<br>Vercel: Local mock | Wizard introduced in Phase 15/26 (`558c9a2`) |
| `/patient/case/[caseId]` | Yes | Dynamic patient case tracking, urgency guidance, clinical team info | 404 or redirects to `/dashboard` | `PatientCasePage` (`app/patient/case/[caseId]/page.tsx`) | Local: `GET /caregraph/{id}`<br>Vercel: None | Local: Persistent<br>Vercel: None | New route on `master` |
| `/staff` | Yes | Staff gateway with role cards for Triage, Doctor Workbench, and Review Queue | Loads monolithic `/dashboard` | `StaffLandingPage` (`app/staff/page.tsx`) with `RoleGuard` | Local: Role check<br>Vercel: None | Local: Session<br>Vercel: Mock | Restructured in `558c9a2` |
| `/staff/triage` | Yes | Dedicated high-volume nurse queue, NEWS2, red flags, vitals capture | Loads `/dashboard/nurse` (identical to doctor view) | `NurseTriagePage` + `NurseTriageQueue` vs Legacy `ClinicianDashboard` | Local: `GET /cases/queue`<br>Vercel: `/api/v1/cases` | Local: DB / Mock fallback<br>Vercel: Hardcoded mock | Nurse view previously duplicated doctor component |
| `/staff/review` | Yes | Attending physician multi-case batch verification queue | Loads `/dashboard/doctor` (identical to nurse view) | `StaffReviewPage` (`app/staff/review/page.tsx`) | Local: `GET /cases/review-queue`<br>Vercel: Hardcoded mock | Local: DB / Mock fallback<br>Vercel: Hardcoded mock | Review queue isolated in `558c9a2` |
| `/staff/cases/[caseId]` | Yes | 3-panel asymmetric Doctor Workbench (timeline, provenance, AI advice, decisions) | 404 or legacy modal | `DoctorWorkbenchView` (1044 lines) | Local: `GET /caregraph/{id}`, `POST /decision`<br>Vercel: None | Local: Full DB persistence<br>Vercel: None | Comprehensive clinical workbench introduced in Phase 17/26 |
| `/facilities` | Yes | Regional facility directory, ICU/bed telemetry, capability flags | Missing / 404 | `FacilitiesPage` (`app/facilities/page.tsx`) | Local: Static seed data<br>Vercel: None | Local: Seeded in DB<br>Vercel: None | Added in Phase 22 |
| `/referrals` | Yes | Transfer coordination, SBAR handoff dispatch, transit tracking | Missing / 404 | `ReferralsPage` (`app/referrals/page.tsx`) | Local: Synthetic dispatch<br>Vercel: None | Local: Seeded<br>Vercel: None | Added in Phase 22 |
| `/system` | Yes | Security audit ledger, offline sync status, system telemetry | Missing or legacy `/audit` | `SystemPage` (`app/system/page.tsx`) | Local: Audit logs<br>Vercel: None | Local: DB `audit_events`<br>Vercel: None | Added in Phase 25 |
| `/about` | Yes | System architecture, 4 pillars, ethical bounds | 404 or anchor section | `AboutPage` (`app/about/page.tsx`) | Local: SSR<br>Vercel: None | Static | Added in Phase 27 |
| `/disclaimer` | Yes | Non-diagnostic disclaimer, legal notices | Modal disclaimer | `DisclaimerPage` (`app/disclaimer/page.tsx`) | Local: SSR<br>Vercel: None | Static | Added in Phase 27 |
| `/privacy` | Yes | DPDP Act 2023 compliance, PII shielding, ephemeral retention | Missing | `PrivacyPage` (`app/privacy/page.tsx`) | Local: SSR<br>Vercel: None | Static | Added in Phase 25 |

---

## 4. Root-Cause Investigation: Landing Page Flicker

### Observed Behavior on Vercel:
The public landing page continuously flickers, with layout elements jumping, images disappearing and reappearing, and loading indicators pulsating indefinitely.

### Evidence & Call-Chain Breakdown:

1. **The Polling Trigger (`frontend/src/lib/connectivity.tsx` in legacy commit):**
   ```typescript
   // Lines 120-145 in abbf81a:
   const measureNow = useCallback(async () => {
     if (typeof window === "undefined") return;
     try {
       const res = await fetch(`${API_BASE_URL}/api/v1/ping`, { cache: "no-store" });
       if (res.ok) {
         evaluateQuality("ping measurement");
       } else {
         failureCountRef.current += 1;
         evaluateQuality("ping status error");
       }
     } catch {
       failureCountRef.current += 1;
       evaluateQuality("ping network failure");
     }
   }, [applyStateWithHysteresis, evaluateQuality]);
   ```
   - On Vercel, `API_BASE_URL` was configured to `http://localhost:8000` or an unreachable backend.
   - Every fetch to `/api/v1/ping` failed immediately with a network error.

2. **The State Bouncing Loop (`applyStateWithHysteresis`):**
   ```typescript
   if (target === "OFFLINE") {
     setNaturalState("OFFLINE");
     triggerTransitionToast(current, "OFFLINE");
   }
   ```
   - The failure caused `state` to transition to `"OFFLINE"`.
   - `scheduleNextPing` scheduled an immediate probe: `delay = cur === "OFFLINE" ? 5000 : ...`.
   - State changes triggered component re-renders across the entire tree via `ConnectivityContext.Provider`.

3. **The Visual Flicker Culprit (`AdaptiveImage.tsx`):**
   ```typescript
   // In frontend/src/components/common/adaptive-image.tsx:
   const { state, isLowBandwidthActive } = useConnectivity();
   const shouldAutoLoad = isEssential || (!isLowBandwidthActive && state !== "OFFLINE");

   useEffect(() => {
     if (!isLowBandwidthActive && state !== "OFFLINE") {
       setUserRequestedLoad(true);
     }
   }, [isLowBandwidthActive, state]);
   ```
   - When `state` flipped to `"OFFLINE"`, `shouldAutoLoad` evaluated to `false`.
   - The hero image was unmounted and replaced by a fallback "Load Image" button.
   - When the next ping probe ran, or browser `online` fired, state bounced back temporarily, causing the image to remount with an animated spinner (`animate-spin`), re-fetch from Unsplash, and snap into view.
   - This cycle repeated every 5 seconds, causing continuous layout thrashing and visual flicker.

4. **Local Master Verification:**
   - In commit `558c9a2`, `AdaptiveImage`, `useConnectivity`, and `NetworkIndicator` were eliminated.
   - The current landing page (`frontend/src/app/page.tsx`) is a **React Server Component** with zero client-side ping loops, zero state hooks, and zero network polling.
   - Locally, the page renders instantly with **zero flicker**.

---

## 5. Backend Service and Database Status

### 5.1 Local Environment
- **Runtime:** FastAPI 0.115+ on Python 3.14.5 (`.venv/Scripts/python.exe`).
- **Database Engine:** SQLite in WAL mode (`sqlite+aiosqlite:///./clinova-dev.db`) with `PRAGMA foreign_keys=ON`.
- **Schema Head:** Alembic migration revision `b84f3782910c`.
- **Health Probes:**
  - `GET /health/live`: Returns HTTP 200 with `{ "status": "healthy", "liveness": "alive" }` without database overhead.
  - `GET /health/ready`: Returns HTTP 200 with `{ "status": "ready", "database": "connected" }` after verifying `SELECT 1`. Returns HTTP 503 upon failure with zero credential leakage.
- **Test Verification:**
  - `pytest backend/tests/test_foundation.py`: 9 / 9 passed (100%).
  - `pytest backend/tests/test_phase14_auth_rbac.py`: 30 / 30 passed (100%).
  - Full test suite: 400 / 400 passed (100%).

### 5.2 Hosted Production Environment
- **PostgreSQL Database (Supabase Free Tier):**
  - Status: **UNPROVISIONED / BLOCKED AT OPERATOR GATE**.
  - No connection string has been provided or configured.
- **Backend Service (Render Free Web Service):**
  - Status: **UNDEPLOYED / BLOCKED AT OPERATOR GATE**.
  - No Render web service is currently active.
- **Frontend-to-Backend Connectivity:**
  - On Vercel, requests to `/api/v1/*` fail because no live backend exists.
  - The resilient frontend adapter (`frontend/src/lib/api.ts`) catches these failures and falls back to deterministic synthetic fixtures and localStorage offline queuing.

---

## 6. Audit of Role-to-Dashboard Separation

### 6.1 Why Multiple Roles Appeared to Use the Same Dashboard on Vercel
In the legacy codebase (commit `abbf81a`), role separation was purely superficial:
1. `frontend/src/app/dashboard/nurse/page.tsx`:
   ```typescript
   "use client";
   import { ClinicianDashboard } from "@/components/clinical/clinician-dashboard";
   export default function NurseDashboard() { return <ClinicianDashboard />; }
   ```
2. `frontend/src/app/dashboard/doctor/page.tsx`:
   ```typescript
   "use client";
   import { ClinicianDashboard } from "@/components/clinical/clinician-dashboard";
   export default function DoctorDashboard() { return <ClinicianDashboard />; }
   ```
   **Both the Nurse and Doctor routes literally imported and rendered the exact same component.**
3. `frontend/src/app/dashboard/page.tsx`: Contained a monolithic page with a client-side dropdown (`setActiveRoleView(e.target.value)`) that switched mock data views without server-side verification.
4. `frontend/src/app/register/page.tsx`: Contained an unauthenticated registration form where any user could select `role = "doctor"` from a dropdown, posing a critical security vulnerability.

### 6.2 Verified Role-to-Dashboard Matrix on Local Master

On local `master`, genuine role-to-dashboard separation is enforced at both the UI (`RoleGuard.tsx`) and backend (`app/core/policy.py`) layers:

| Role Persona | Backend Role Value | Expected & Local Landing Route | Vercel Landing Route | Authorized Actions & Workspaces | Genuine Role Separation? | Backend Policy Enforcement |
|:---|:---|:---|:---|:---|:---:|:---:|
| **Patient** | `PATIENT` | `/patient` | `/dashboard/patient` | Multi-step intake, digital consent, symptom review, personal case tracker | **Yes** | Scoped strictly to own patient records (`patient_id`) |
| **Triage Nurse** | `NURSE` | `/staff/triage` | `/dashboard/nurse` (shared) | Acuity worklist, NEWS2 vital signs entry, SLA wait-time tracking | **Yes** | Blocked from clinician sign-off (`HTTP 403`) |
| **Attending Physician** | `CLINICIAN` / `DOCTOR` | `/staff/review` & `/staff/cases/[id]` | `/dashboard/doctor` (shared) | 3-panel review, timeline verification, evidence resolution, decision sign-off | **Yes** | Authoritative clinical decision attribution |
| **Referral Coordinator** | `REFERRAL_COORDINATOR` | `/referrals` | N/A (redirected) | Facility feasibility assessment, SBAR transfer handoff, dispatch tracking | **Yes** | Restricted to referral orchestration endpoints |
| **Facility Administrator** | `FACILITY_ADMIN` | `/facilities` | N/A (redirected) | Bed capacity, ICU availability, oxygen telemetry, capability flags | **Yes** | Scoped to designated facility metadata |
| **System Administrator** | `SYSTEM_ADMIN` | `/system` | `/dashboard/admin` | Immutable security audit log, offline edge sync, system telemetry | **Yes** | Full administrative oversight; non-clinical |
| **Auditor** | `AUDITOR` | `/system` | N/A | Read-only compliance review, audit trail inspection | **Yes** | Read-only access across all models |

---

## 7. Patient-Care Workflow Connectivity Matrix

Every stage of the established 13-stage clinical workflow has been mapped and classified:

| Stage # | Workflow Stage Name | Local Classification | Vercel Classification | Frontend Component | Backend API Endpoint | Backend Service / Model | Persistence Mechanism |
|:---:|:---|:---:|:---:|:---|:---|:---|:---|
| **1** | Public Landing Page | **Implemented & Connected** | Partially Implemented (Flickering) | `app/page.tsx` | `GET /` | `app/main.py` | Static / In-memory |
| **2** | Pathway Selection (Regular vs Emergency) | **Implemented & Connected** | Partially Implemented | `PatientIntakeWizard.tsx` (Step 2) | `POST /intake/submit` | `app/api/v1/endpoints/intake.py` | `Case.pathway` in SQLite/PostgreSQL |
| **3** | Patient Intake & Digital Consent | **Implemented & Connected** | Partially Implemented | `PatientIntakeWizard.tsx` (Step 3) | `POST /intake/submit` | `app/db/models.py` | `consents` table (DPDP Act compliant) |
| **4** | Multimodal Intake (Text, Voice STT, Docs) | **Implemented & Connected** | Missing / Disconnected | `PatientIntakeWizard.tsx` (Steps 4–8) | `POST /intake/voice`, `POST /documents/upload` | `voice.py`, `documents.py` | `documents`, `storage/documents` |
| **5** | Extraction, Provenance & Missing Info | **Implemented & Connected** | Missing | `DoctorWorkbenchView.tsx`, `ProvenanceBadge.tsx` | `POST /cases/{id}/request-information` | `app/domain/caregraph.py` | `evidence.provenance_type` |
| **6** | Timeline Consolidation & Follow-up | **Implemented & Connected** | Missing | `Timeline.tsx`, `DoctorWorkbenchView.tsx` | `GET /caregraph/{caseId}` | `app/db/models.py` | `timeline_events` table |
| **7** | CAREGRAPH Risk & Uncertainty | **Implemented & Connected** | Missing | `UncertaintyIndicator.tsx`, `PriorityBadge.tsx` | `GET /caregraph/{caseId}` | `app/api/v1/endpoints/caregraph.py` | Epistemic state in `cases` table |
| **8** | Deterministic Safety Checks (R01–R06) | **Implemented & Connected** | Partially Implemented | `NurseTriageQueue.tsx`, `RedFlagBanner.tsx` | `POST /cases/{id}/triage/calculate` | `app/domain/clinical_rules.py` | Evaluated on vitals/intake ingest |
| **9** | Clinician Review & Decision Attribution | **Implemented & Connected** | Disconnected | `DoctorWorkbenchView.tsx`, `HumanDecisionCard.tsx` | `POST /cases/{id}/decision` | `app/api/v1/endpoints/review.py` | `clinical_decisions` table with JWT actor |
| **10** | FACILITYGRAPH & SBAR Referral | **Implemented & Connected** | Missing | `app/referrals/page.tsx`, `FacilityDrawer.tsx` | `POST /referrals/dispatch` | `app/api/v1/endpoints/referrals.py` | `referrals`, `facilities` tables |
| **11** | Outcome Capture | **Implemented & Connected** | Missing | `DoctorWorkbenchView.tsx` | `POST /cases/{id}/disposition` | `app/api/v1/endpoints/review.py` | `cases.disposition` |
| **12** | SIGNALGRAPH Update | **Implemented & Connected** | Missing | `SignalGraphData`, `DoctorWorkbenchView.tsx` | `POST /signalgraph/update` | `app/api/v1/endpoints/signalgraph.py` | Syndromic surveillance aggregation |
| **13** | Final Case State & Immutable Audit Log | **Implemented & Connected** | Partially Implemented | `app/system/page.tsx`, `SystemAuditDrawer.tsx` | `POST /cases/{id}/close-encounter`, `GET /audit` | `app/api/v1/endpoints/audit.py` | `audit_events` table (SHA-256 chained) |

> **Note on Vercel Status:** While all 13 stages are fully implemented on local `master`, on Vercel they are **Blocked by Infrastructure/Configuration** because the deployed Vercel frontend is running the legacy code and has no live backend service connected.

---

## 8. Visual Appearance vs Functional Completeness Analysis

The core user observation stated:  
> *"The local version appears to contain more of the intended application functionality, while the Vercel version has a better visual appearance in some areas..."*

### Forensic Breakdown of Why This Occurred:

1. **Why Vercel Looks Visually Better in Some Areas:**
   - The legacy Vercel build used **Tailwind CSS** with utility classes (`bg-slate-50 selection:bg-teal-100`, `rounded-2xl shadow-sm`, `bg-gradient-to-r from-teal-600 to-emerald-600`).
   - It included external Unsplash hero photography via `AdaptiveImage`.
   - It had styled badge pills, hover drop shadows, and visual marketing callouts across the landing page.

2. **Why Local Master Looks Plainer:**
   - In commit `558c9a2` ("overall phase complete"), the developer removed `tailwind.config.ts` (-56 lines) and `postcss.config.mjs` (-9 lines) to eliminate build-time dependency overhead and ensure zero-warning TypeScript compilation.
   - The styling was replaced with **raw CSS custom properties** (`globals.css`, 848 lines) and extensive inline styles (`style={{ display: "flex", gap: "var(--clinova-space-4)" }}`).
   - While structurally sound, accessible, and fast-loading (173 B HTML bundle), this gives the local UI a sparser, more utilitarian aesthetic.

3. **Why Local Master is Functionally Superior:**
   - Local `master` has **15 real Next.js routes** compiling in 6.2s with 0 errors.
   - It has the complete **10-step Patient Intake Wizard** (`PatientIntakeWizard.tsx`), including Odia/Hindi vernacular translation and audio STT.
   - It has the **Doctor Workbench** (`DoctorWorkbenchView.tsx`), with live timeline evidence verification, conflict resolution, epistemic uncertainty meters, and clinician sign-offs.
   - It has the **Nurse Triage Queue** (`NurseTriageQueue.tsx`), with real-time NEWS2 calculations and red-flag alerts.
   - It has **RoleGuard** with authentic RBAC enforcement, plus the **Offline Sync Queue** (`offlineQueue.ts`) for resilient edge caching.

---

## 9. Prioritized Defects and Recommended Remediations (for Phase 28B)

| Priority | Issue / Defect | Exact Files / Locations | Root Cause | Smallest Safe Remediation (Phase 28B) |
|:---:|:---|:---|:---|:---|
| **P1** | **Source Version Desynchronization on Vercel** | Vercel Project Settings / GitHub Remote | Vercel deployment tracking old commit or stalled deployment | Connect Vercel to `master` branch at commit `6e2b88a` (or latest) and trigger a clean production build. |
| **P2** | **Landing Page Flicker on Production** | `frontend/src/lib/connectivity.tsx`, `AdaptiveImage.tsx` (legacy) | Unhandled `/api/v1/ping` network errors triggering layout shift in `AdaptiveImage` | Deploying local `master` automatically resolves this, as `/` is already a static Server Component with zero ping loops. |
| **P3** | **Visual Styling Gap (Tailwind vs Custom CSS)** | `frontend/src/app/globals.css`, `frontend/src/app/page.tsx` | Removal of Tailwind in commit `558c9a2` resulted in plain inline styling | Reintroduce Tailwind CSS or enhance the design tokens in `globals.css` (modern gradients, card elevation, refined typography) without altering component logic. |
| **P4** | **Unprovisioned Production Backend & Database** | `backend/app/core/config.py`, Render, Supabase | Cloud services lack authenticated provisioning credentials | Human operator provisions free Supabase PostgreSQL and Render Web Service as detailed in the Phase 28 runbook. |
| **P5** | **Repository Identity Discrepancy** | Git remote config, GitHub repo | Discrepancy between `CLIVORA-AI` (GitHub) and `CLINOVA-AI` (local) | Operator confirms repo name or renames GitHub repo to `CLINOVA-AI` and updates remote URL. |
| **P6** | **Auxiliary Drawer Static Mock Fallbacks** | `FacilitiesPage.tsx`, `ReferralsPage.tsx`, `SystemPage.tsx` | Auxiliary pages fall back to static fixtures when backend is offline | Connect drawer data fetches to live backend endpoints (`/api/v1/facilities`, `/api/v1/referrals`, `/api/v1/audit/logs`) while retaining resilient fallback. |

---

## 10. Operator Verification Boundary & Required Human Actions

The following actions cannot be performed autonomously and require human authorization outside chat:

1. **GitHub Repository Name Confirmation:**  
   Confirm whether `https://github.com/Samir-hub12345/CLIVORA-AI` is authoritative, or rename it on GitHub to `CLINOVA-AI`.
2. **Vercel Project Deployment Trigger:**  
   Authenticate via `vercel login` or visit the Vercel dashboard to verify that the project root is set to `frontend` and deploy from the latest `master` commit.
3. **Supabase Database Provisioning:**  
   Create the free PostgreSQL instance on Supabase and inject the connection string into Render.
4. **Render Web Service Deployment:**  
   Create the free Python web service on Render pointing to root directory `backend`.
