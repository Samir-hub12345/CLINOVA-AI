# CLINOVA AI — Master Workflow Transition & Interaction Mapping
> **Document ID:** `DOC-WORKFLOW-01`  
> **Status:** VERIFIED & SYNCHRONIZED  
> **Repository Target:** `master` (Authoritative Main Platform)  
> **Production Target:** https://clinova-ai-pink.vercel.app/  
> **Reference Platform:** https://clinova-ai.vercel.app  

---

## 1. 12-Stage Clinical Workflow Transition Model

The application adheres strictly to the 12-stage Master Case Lifecycle defined in `docs/06_MASTER_PATIENT_FLOW.md` and verified in `backend/tests/test_phase26_integration_e2e.py`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    12-STAGE CLINICAL WORKFLOW CONTINUUM                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  [1. Registration & Consent] ───────────► [2. Staff Pathway Assignment]     │
│                 │                                      │                    │
│                 ▼                                      ▼                    │
│  [3. Nurse Intake & Vitals]  ───────────► [4. AI Extraction & Provenance]   │
│                 │                                      │                    │
│                 ▼                                      ▼                    │
│  [5. Timeline & Gaps Audit]  ───────────► [6. Adaptive Follow-up (NBI)]     │
│                 │                                      │                    │
│                 ▼                                      ▼                    │
│  [7. CAREGRAPH Synthesis]    ───────────► [8. Deterministic Safety Engine]  │
│                 │                                      │                    │
│                 ▼                                      ▼                    │
│  [9. Clinician Review Gate]  ───────────► [10. FACILITYGRAPH & SBAR Handoff]│
│                 │                                      │                    │
│                 ▼                                      ▼                    │
│  [11. Outcome & SIGNALGRAPH] ───────────► [12. Reassessment & PDF Report]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Complete Lifecycle Transition Table

| Stage | Name | Entry Condition | Responsible Role | Required Information | Action Advancing Workflow | Persisted State Transition | Next Stage | Failure / Escalation Path |
|:---:|:---|:---|:---|:---|:---|:---|:---|:---|
| **1** | **Registration & Consent** | Walk-in patient arrives or digital portal opened | RECEPTIONIST / PATIENT | Name, Age bracket, Sex, Phone, Explicit Informed Consent (`GRANTED`) | Click "Save Registration & Proceed" | `Case.status: INTAKE_PENDING`, `Consent.status: GRANTED` | Stage 2 | Consent refused -> Case halted with `CONSENT_DENIED` |
| **2** | **Staff-Assigned Pathway** | Patient registered in master record | RECEPTIONIST / NURSE | Clinical acuity assessment, Chief complaint acuity | Select Routine OPD vs Emergency Fast-Track | `Case.pathway: OPD_GENERAL` or `EMERGENCY_FAST_TRACK` | Stage 3 | Acute red flags -> Immediate override to `EMERGENCY` |
| **3** | **Nurse Intake & Vitals** | Patient queued in Triage Worklist (`/staff/triage`) | NURSE | Bedside vitals: HR, BP (Systolic/Diastolic), SpO2, RR, Temp, AVPU | Click "Submit Vitals & Advance" | `Case.status: TRIAGE_IN_PROGRESS`, `VitalReading` inserted | Stage 4 | Shock Index > 1.0 or SpO2 < 90% -> Auto-flags `CRITICAL` |
| **4** | **AI Extraction & Provenance** | Intake text, audio, or PDF uploaded | CLINOVA LOCAL ENGINE / AI | Audio blob, OCR scanned PDF, Structured complaints | Automated entity extraction pipeline | `EvidenceRecord` created with `provenance_type: AI_INFERRED` | Stage 5 | AI unreachable -> Fallback heuristic extraction executed |
| **5** | **Timeline & Gaps Audit** | Extracted entities & vitals present | NURSE / CLINICIAN | Chronological clinical events, known vs unknown data | System aggregates longitudinal timeline | `TimelineEvent` linked to Master Case | Stage 6 | Inconsistent dates -> Flagged as `CONFLICTING` |
| **6** | **Adaptive Follow-up (NBI)** | Epistemic uncertainty detected in record | PATIENT / NURSE | Targeted answers to Next-Best-Information questions | Answer questions & confirm | `EpistemicStatus: RESOLVED`, Uncertainty score updated | Stage 7 | Patient unable to answer -> Marked as `UNKNOWN` |
| **7** | **CAREGRAPH Synthesis** | Sufficient evidence assembled | CAREGRAPH ENGINE | Evidence records, vital trends, risk factors | Compute risk tuple `(Risk, Reason, Evidence, Trajectory)` | `Case.risk_score`, `Case.trajectory_slope` updated | Stage 8 | Calculation failure -> Reverts to baseline MEWS |
| **8** | **Deterministic Safety Engine** | Acuity score computed | DETERMINISTIC RULES | NEWS2 parameters, Shock Index, red-flag checklists | Rule validation engine execution | `Case.acuity_tier: ROUTINE / URGENT / CRITICAL / EMERGENCY` | Stage 9 | Red flag triggered -> Bedside alert banner displayed |
| **9** | **Clinician Review Gate** | Case status is `CLINICIAN_REVIEW_REQUIRED` | CLINICIAN / DOCTOR | Physician exam findings, clinical impression, rationale | Attending doctor signs off clinical decision | `ClinicianDecision` recorded, `Case.status: REVIEWED` | Stage 10 | Disputed evidence -> Doctor overrides parameter |
| **10** | **FACILITYGRAPH & Referral** | Review complete; transfer required | CLINICIAN / REFERRAL_COORDINATOR | Target hospital capabilities, transit travel time, ICU beds | Click "Dispatch SBAR Transfer" | `Referral.status: DISPATCHED`, SBAR packet generated | Stage 11 | No ICU beds -> Auto-ranks alternative receiving centers |
| **11** | **Outcome & SIGNALGRAPH** | Patient discharged, admitted, or transferred | ATTENDING CLINICIAN | Disposition (`DISCHARGE_HOME`, `ADMIT_WARD`, `TRANSFER`) | Record definitive outcome | `CaseOutcome` inserted, `SIGNALGRAPH` telemetry logged | Stage 12 | Unexpected complication -> Re-opens case for review |
| **12** | **Follow-Up & PDF Report** | Case reached terminal or active monitoring state | AUTHORIZED USER (Doctor, Nurse, or Patient for self) | Persisted case history, verified decisions, care plan | Click "Download Care Summary (PDF)" | PDF generated on-the-fly with tamper-evident signature | Case Complete | Auth expired -> Prompts login without losing case data |

---

## 2. Master Button & Interactive Control Contract

Every button, link, and interactive element across the application binds to an explicit handler, authorization gate, and persistence contract:

| Component / Screen | Control Label / Icon | Permitted Roles | Event Handler | Target Route / Action | Success State | Failure / Error State |
|:---|:---|:---|:---|:---|:---|:---|
| **TopBar Header** | Brand Logo ("CLINOVA AI") | Public, All | Nav Link | `/` (Home) | Instant navigation to overview | N/A |
| **TopBar Header** | "Sign In" Button | Public | Nav Link | `/login` | Opens split-pane login | N/A |
| **TopBar Header** | Demo Persona Dropdown | All Authenticated | `onChange={handleRoleChange}` | `switchPersona(personaId)` | Active session role and badge update synchronously | Warning toast; keeps current session |
| **TopBar Header** | Logout Icon Button | All Authenticated | `onClick={handleLogout}` | `logout()` | Session tokens cleared, transitions to public view | Safe fallback clearing |
| **TopBar Header** | Referral Drawer Toggle | Staff (Referral, Doctor, Admin) | `onClick={onOpenReferralDrawer}` | Opens right slide-over drawer | SBAR transfer coordination tools displayed | Controlled drawer close |
| **TopBar Header** | Facility Drawer Toggle | Staff (Facility Admin, Doctor) | `onClick={onOpenFacilityDrawer}` | Opens right slide-over drawer | Regional ICU/Ward bed telemetry displayed | Controlled drawer close |
| **TopBar Header** | System Audit Drawer Toggle | SYSTEM_ADMIN, AUDITOR | `onClick={onOpenSystemDrawer}` | Opens right slide-over drawer | SHA-256 compliance logs displayed | Controlled drawer close |
| **Landing Hero** | "Doctor Workbench" CTA | CLINICIAN, DOCTOR, ADMIN | Nav Link | `/staff/cases/CASE-SYNTH-003` | Opens 3-panel clinical workstation | RoleGuard prompts login if unauthorized |
| **Landing Hero** | "Nurse Triage" CTA | NURSE, CLINICIAN, ADMIN | Nav Link | `/staff/triage` | Opens priority triage queue | RoleGuard prompts login if unauthorized |
| **Landing Hero** | "Reception Desk" CTA | RECEPTIONIST, ADMIN | Nav Link | `/staff/reception` | Opens walk-in patient registration | RoleGuard prompts login if unauthorized |
| **Landing Hero** | "Patient Self-Intake" CTA | Public, PATIENT | Nav Link | `/patient/intake` | Opens 10-step patient intake wizard | N/A |
| **Landing Schedule** | "My patients" / "Whole clinic" | All Authenticated | `onClick={() => setScheduleScope()}` | State filter toggle | Schedule table filters rows instantly | N/A |
| **Landing Schedule** | Table Row Click | All Authenticated | `onClick={navigateToCase}` | `/staff/cases/[patientId]` | Direct navigation to selected clinical case | Safe link fallback |
| **Login Screen** | Role Quick Switch Tabs | Public, All | `onClick={() => handleRoleSelectChange()}` | State role prefill | Updates username and pre-fills demo role | N/A |
| **Login Screen** | "Sign In to Workstation" | Public, All | `onSubmit={executeLogin}` | `POST /auth/login` | Redirects to role-authorized destination | Displays inline validation error banner |
| **Login Screen** | Password Eye Toggle | Public | `onClick={() => setShowPassword(!v)}` | Form input type toggle | Flips password visibility (`text` vs `password`) | Retains entered password value |
| **Patient Portal** | "View Care Status" Submit | Public, PATIENT | `onSubmit={handleLookup}` | `/patient/case/[token]` | Navigates to patient's private case status | Inline error: "Please enter your assigned token" |
| **Patient Case View** | "Download Care PDF" | PATIENT, CLINICIAN, NURSE | `onClick={handleDownload}` | `downloadCaseReportPdf(caseId)` | Triggers browser download of `clinova_report_[id].pdf` | Direct link fallback or error toast |
| **Doctor Workbench** | Decision Sign-Off ("OBSERVE") | CLINICIAN, DOCTOR | `onClick={handleDecisionSubmit}` | `submitClinicianDecision(payload)` | Clinician decision saved, status transitions to `REVIEWED` | Inline error; prevents unconfirmed advancement |
| **Referrals Page** | "Dispatch Transfer" Button | REFERRAL_COORDINATOR, DOCTOR | `onClick={handleDispatch}` | Synthetic SBAR transfer dispatch | Status banner: "Synthetic SBAR handoff dispatched" | Error alert banner |

---

## 3. Security Boundary Verification Record

1. **Horizontal Patient Isolation:**
   - Patient A accessing Patient B's case is rejected with masked HTTP 404/403.
   - Tested in `backend/tests/test_phase26_integration_e2e.py::test_journey_c_role_and_authorization_boundaries_end_to_end` (PASSED).
2. **Vertical Privilege Escalation:**
   - Patient or Nurse attempting to record clinical decisions is rejected with HTTP 403.
   - Nurse attempting to resolve edge sync conflicts is rejected with HTTP 403.
   - Tested in `backend/tests/test_phase26_integration_e2e.py` (PASSED).
3. **Autonomous AI Action Prohibition:**
   - Autonomous AI actions (`AI_DIAGNOSIS`, `AUTO_PRESCRIBE`, `AI_ADMISSION`, `AI_DISCHARGE`, `AUTHORIZE_PROCEDURE`) are rejected with HTTP 422 (`UNSUPPORTED_OPERATION`).
   - Tested in `backend/tests/test_phase26_integration_e2e.py::test_journey_b_emergency_pathway_end_to_end` (PASSED).
4. **Offline Edge Node Replay & Tamper Defense:**
   - Duplicate offline sync submissions return idempotent `ALREADY_SYNCED` without duplicate rows.
   - Payload tampering on existing `sync_id` is rejected as `FAILED` (`tampering/replay detected`).
   - Tested in `frontend/tests/offlineQueue.test.mjs` (6/6 PASSED) & `backend/tests/test_phase26_integration_e2e.py::test_journey_d_offline_sync_and_data_consistency_end_to_end` (PASSED).
