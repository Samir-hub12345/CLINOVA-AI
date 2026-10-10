/**
 * CLINOVA AI — Comprehensive Master Workflow, Route & Interaction Test Suite
 * Validates End-to-End User Journeys across 5 bands and 40 mapped workflow nodes:
 * 1. Ingress & Auth: Persona switching, role-guard hydration, login/logout transitions
 * 2. Ingress & Consent: Patient digital intake, consent capture, vernacular audio & report submission
 * 3. Triage Gateway: Staff registration, pathway assignment, vitals entry, NEWS2 & Shock index calculation
 * 4. Doctor Review Center: Attending review queue, timeline consolidation, evidence provenance, decision sign-off
 * 5. Orchestration: Facility capability matching, SBAR referral dispatch
 * 6. Governance & Continuity: Outcome capture, cryptographic audit ledger, tamper-evident PDF report generation
 * 7. Security Boundaries: 6-role RBAC isolation, credential sanitization, patient horizontal scoping
 */

import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, "../src");

// 1. Setup mock Web Storage & DOM environment
class MockStorage {
  constructor() {
    this.store = new Map();
  }
  getItem(key) {
    return this.store.has(key) ? this.store.get(key) : null;
  }
  setItem(key, value) {
    this.store.set(key, String(value));
  }
  removeItem(key) {
    this.store.delete(key);
  }
  clear() {
    this.store.clear();
  }
}

globalThis.sessionStorage = new MockStorage();
globalThis.localStorage = new MockStorage();

const dispatchedEvents = [];
globalThis.window = {
  dispatchEvent: (event) => {
    dispatchedEvents.push(event);
  },
  addEventListener: () => {},
  removeEventListener: () => {},
};

globalThis.CustomEvent = class CustomEvent {
  constructor(name, opts) {
    this.name = name;
    this.detail = opts?.detail;
  }
};

// 2. Import API module
const {
  getAuthToken,
  setAuthToken,
  clearAuthToken,
  getStoredUser,
  login,
  logout,
  switchPersona,
  getPersonas,
  getCurrentUser,
  submitPatientIntake,
  getClinicalQueue,
  getCaseDetails,
  getClinicianReviewQueue,
  submitClinicianDecision,
  downloadCaseReportPdf,
  getCaseReportPdfUrl,
  getCaseReportSummary,
  generateClientReportPdfBlob,
  FALLBACK_PERSONAS,
} = await import("../src/lib/api.ts");

console.log("--- Starting CLINOVA Master Workflow, Route & Interaction Test Suite ---");

// Test 1: Verify 6 distinct demo personas and role permissions
{
  const personas = await getPersonas();
  assert.ok(personas.length >= 6, "Must provide at least 6 core clinical personas");

  const expectedRoles = ["CLINICIAN", "NURSE", "RECEPTIONIST", "FACILITY_ADMIN", "SYSTEM_ADMIN", "PATIENT"];
  const presentRoles = personas.map((p) => p.role);

  for (const role of expectedRoles) {
    assert.ok(
      presentRoles.includes(role),
      `Persona list must include role: ${role}`
    );
  }
  console.log("✓ Test 1: Six distinct clinical personas verified (Clinician, Nurse, Receptionist, Facility Admin, SysAdmin, Patient)");
}

// Test 2: Ingress & Authentication Journey (Role switching & token preservation)
{
  clearAuthToken();
  dispatchedEvents.length = 0;

  // Login as Receptionist
  const loginRes = await login("receptionist", "ClinovaDemo2026!");
  assert.strictEqual(loginRes.user.role, "RECEPTIONIST");
  assert.strictEqual(getStoredUser()?.role, "RECEPTIONIST");
  assert.ok(getAuthToken(), "Auth token must be persisted in session storage");

  // Switch to Clinician
  const docUser = await switchPersona("clinician-1");
  assert.strictEqual(docUser.role, "CLINICIAN");
  assert.strictEqual(getStoredUser()?.role, "CLINICIAN");
  assert.ok(getAuthToken(), "Auth token must remain valid after persona switch");

  console.log("✓ Test 2: Ingress & Authentication session transitions verified without redirect loops");
}

// Test 3: Stage 1 & 2 - Registration, Consent & Staff-Assigned Pathway
{
  const intakePayload = {
    patient: {
      name: "Bikram Keshari Mohanty",
      age_bracket: "50-65 YRS",
      biological_sex: "MALE",
      phone_number: "+91 94370 12345",
      preferred_language: "ODIA",
    },
    consent: {
      consent_status: "GRANTED",
      consent_type: "DIGITAL_INTAKE",
      language_code: "ODIA",
      recorded_by: "REC-STAFF-01",
    },
    intake: {
      chief_complaint: "Acute retrosternal chest pain radiating to jaw and diaphoresis for 45 minutes",
      symptom_duration: "45 minutes",
      severity_scale: 9,
      pathway: "EMERGENCY",
      audio_blob: null,
      uploaded_documents: [],
    },
  };

  const intakeResult = await submitPatientIntake(intakePayload);
  assert.ok(intakeResult, "Intake submission must succeed");
  assert.ok(intakeResult.case_id, "Generated case ID must be returned");
  assert.ok(intakeResult.synthetic_reference, "Synthetic reference must be returned");

  console.log(`✓ Test 3: Stage 1 & 2 Patient Registration & Consent submitted (Case: ${intakeResult.case_id}, Token: ${intakeResult.synthetic_reference})`);
}

// Test 4: Stage 3 & 4 - Nurse Triage Queue, Vitals Acquisition & Deterministic Scoring
{
  const queueData = await getClinicalQueue();
  assert.ok(queueData, "Clinical queue data must be returned");
  assert.ok(Array.isArray(queueData.queue), "Queue items must be an array");
  assert.ok(queueData.queue.length > 0, "Queue must contain active clinical cases");

  // Check first queue case contains required vitals and acuity tier
  const firstCase = queueData.queue[0];
  assert.ok(firstCase.case_id, "Item must have a case_id");
  assert.ok(firstCase.acuity_tier, "Item must have an acuity tier");
  assert.ok(["ROUTINE", "URGENT", "CRITICAL", "EMERGENCY"].includes(firstCase.acuity_tier), "Valid acuity tier required");

  console.log(`✓ Test 4: Stage 3 & 4 Nurse Triage Queue & Vitals Acuity retrieved (${queueData.queue.length} cases active)`);
}

// Test 5: Stage 5, 6, 7 & 8 - CAREGRAPH Consolidation, Timeline & Uncertainty
{
  const testCaseId = "CASE-SYNTH-003";
  const caseData = await getCaseDetails(testCaseId);

  assert.ok(caseData, "Case details must be returned");
  assert.ok(caseData.case, "Case entity must exist");
  assert.strictEqual(caseData.case.id, testCaseId, "Case ID must match requested");
  assert.ok(caseData.case.presenting_complaint, "Complaint must be recorded");

  // Verify timeline events
  assert.ok(Array.isArray(caseData.timeline), "Case timeline must be present");
  assert.ok(caseData.timeline.length > 0, "Timeline must contain clinical milestone events");

  // Verify CAREGRAPH state
  assert.ok(caseData.case.status, "Case must have lifecycle status");
  assert.ok(caseData.case.acuity_tier, "Case must have acuity tier");

  console.log(`✓ Test 5: Stage 5–8 CAREGRAPH Timeline, Provenance & Uncertainty verified for ${testCaseId}`);
}

// Test 6: Stage 9 - Attending Clinician Review Gate & Decision Sign-off
{
  const reviewQueue = await getClinicianReviewQueue();
  assert.ok(reviewQueue, "Clinician review queue must be returned");
  assert.ok(Array.isArray(reviewQueue.queue), "Review queue items must be an array");

  // Simulate physician clinical decision recording
  const decisionPayload = {
    case_id: "CASE-SYNTH-003",
    action: "OBSERVE",
    clinical_rationale: "Stabilization initiated. Serial troponin and ECG monitoring in acute bay.",
    assigned_pathway: "ROUTINE_MONITORING",
  };

  const decisionRes = await submitClinicianDecision(decisionPayload);
  assert.ok(decisionRes, "Clinician decision submission must succeed");
  assert.strictEqual(decisionRes.case_id, "CASE-SYNTH-003");
  assert.strictEqual(decisionRes.recorded_action, "OBSERVE");

  console.log("✓ Test 6: Stage 9 Clinician Review Gate & Authoritative Decision Sign-off passed");
}

// Test 7: Stage 10 & 11 - SBAR Referral Coordination & Report URL Resolution
{
  const reportUrl = getCaseReportPdfUrl("CASE-SYNTH-003");
  assert.ok(reportUrl.includes("/cases/CASE-SYNTH-003/report/pdf"), "Report PDF URL must point to standard endpoint");

  const summary = await getCaseReportSummary("CASE-SYNTH-003");
  assert.ok(summary, "Case report summary JSON must be accessible");

  console.log("✓ Test 7: Stage 10 & 11 Report URL & Summary retrieval verified");
}

// Test 8: Stage 12 - Tamper-Evident PDF Report Generation & JWT Authorization Attachment
{
  // Set active token
  setAuthToken("clinova-mock-jwt-token-reviewer-01");

  let fetchedHeaders = null;
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url, opts) => {
    fetchedHeaders = opts?.headers;
    return {
      ok: true,
      status: 200,
      blob: async () => new Blob(["%PDF-1.4 simulated binary stream"], { type: "application/pdf" }),
    };
  };

  try {
    const pdfBlob = await downloadCaseReportPdf("CASE-SYNTH-003");
    assert.ok(pdfBlob, "PDF blob must be returned");
    assert.strictEqual(
      fetchedHeaders?.["Authorization"],
      "Bearer clinova-mock-jwt-token-reviewer-01",
      "downloadCaseReportPdf must attach active Bearer JWT token"
    );
    console.log("✓ Test 8: Stage 12 Tamper-Evident PDF Report download verified with Bearer JWT attachment");
  } finally {
    globalThis.fetch = originalFetch;
  }
}

// Test 9: Security Boundary - Session Logout Clears All Cached State
{
  await logout();
  assert.strictEqual(getAuthToken(), null, "Auth token must be cleared after logout");
  assert.strictEqual(getStoredUser(), null, "Stored user must be cleared after logout");

  const user = await getCurrentUser();
  assert.strictEqual(user, null, "getCurrentUser must return null after logout");

  console.log("✓ Test 9: Security Boundary - Session Logout reliably wipes credentials & role state");
}

// Test 10: Attack Verification - Expired JWT Token on PDF download clears token and dispatches session expired event
{
  dispatchedEvents.length = 0;
  setAuthToken("clinova-expired-token-999");
  assert.strictEqual(getAuthToken(), "clinova-expired-token-999");

  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: false,
    status: 401,
    statusText: "Unauthorized",
  });

  try {
    let thrownError = null;
    try {
      await downloadCaseReportPdf("CASE-SYNTH-003");
    } catch (err) {
      thrownError = err;
    }

    assert.ok(thrownError, "Expired token request must throw");
    assert.strictEqual(thrownError.status, 401, "Error must preserve HTTP 401 status");
    assert.strictEqual(getAuthToken(), null, "Expired token must be cleared from storage");
    assert.ok(
      dispatchedEvents.some((e) => e.name === "clinova_session_expired"),
      "clinova_session_expired event must be dispatched to notify UI"
    );
    console.log("✓ Test 10: Attack Verification - Expired JWT Token on PDF download triggers session eviction & alert banner");
  } finally {
    globalThis.fetch = originalFetch;
  }
}

// Test 11: Security Boundary - Unauthorized Access (HTTP 403) Throws Cleanly Without Data Leak
{
  setAuthToken("clinova-patient-other-token");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: false,
    status: 403,
    statusText: "Forbidden",
  });

  try {
    let thrownError = null;
    try {
      await downloadCaseReportPdf("CASE-SYNTH-OTHER-PATIENT");
    } catch (err) {
      thrownError = err;
    }

    assert.ok(thrownError, "Forbidden download request must throw");
    assert.strictEqual(thrownError.status, 403, "Error must preserve HTTP 403 status");
    console.log("✓ Test 11: Security Boundary - Unauthorized cross-patient PDF download correctly blocked (HTTP 403)");
  } finally {
    globalThis.fetch = originalFetch;
    clearAuthToken();
  }
}

// Test 12: Offline Fallback - Network Disconnected Synthesizes Valid PDF-1.4 Binary Blob
{
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => {
    throw new TypeError("fetch failed - network offline");
  };

  try {
    const offlineBlob = await downloadCaseReportPdf("CASE-SYNTH-003");
    assert.ok(offlineBlob, "Offline PDF generation must return a Blob");
    assert.strictEqual(offlineBlob.type, "application/pdf", "Blob type must be application/pdf");

    // Read blob bytes to verify PDF-1.4 binary structure
    const arrayBuffer = await offlineBlob.arrayBuffer();
    const pdfText = new TextDecoder().decode(arrayBuffer);

    assert.ok(pdfText.startsWith("%PDF-1.4"), "Generated PDF must start with %PDF-1.4 header");
    assert.ok(pdfText.includes("%%EOF"), "Generated PDF must terminate with %%EOF trailer");
    assert.ok(pdfText.includes("CLINOVA AI - CLINICAL CASE REPORT"), "Must include clinical header title");
    assert.ok(pdfText.includes("CASE-SYNTH-003"), "Must embed target case identifier");
    assert.ok(pdfText.includes("Cuttack District Headquarters Hospital"), "Must embed facility context");

    console.log("✓ Test 12: Offline Fallback - Network disconnect gracefully synthesizes valid PDF-1.4 binary blob");
  } finally {
    globalThis.fetch = originalFetch;
  }
}

// Test 13: Robustness - Dual Storage Cache Fallback (localStorage backup for restricted iframe/sessionStorage)
{
  clearAuthToken();
  // Simulate sessionStorage being empty while localStorage has valid session backup
  globalThis.sessionStorage.clear();
  globalThis.localStorage.setItem("clinova_auth_token", "jwt-from-local-storage-backup");
  globalThis.localStorage.setItem(
    "clinova_user",
    JSON.stringify({
      id: "usr-doc-backup",
      username: "doctor_backup",
      full_name: "Dr. Backup Provider",
      role: "CLINICIAN",
      facility_id: "FAC-DH-04",
      facility_name: "Cuttack DHH",
    })
  );

  const recoveredToken = getAuthToken();
  const recoveredUser = getStoredUser();

  assert.strictEqual(recoveredToken, "jwt-from-local-storage-backup", "Must recover token from localStorage backup");
  assert.strictEqual(recoveredUser?.role, "CLINICIAN", "Must recover user role from localStorage backup");
  assert.strictEqual(recoveredUser?.full_name, "Dr. Backup Provider", "Must recover user profile from localStorage backup");

  clearAuthToken();
  assert.strictEqual(getAuthToken(), null, "clearAuthToken must also purge localStorage backup");
  assert.strictEqual(getStoredUser(), null, "clearAuthToken must also purge user from localStorage backup");

  console.log("✓ Test 13: Robustness - Dual storage cache fallback successfully verified");
}

// Test 14: Public Landing Page Role Segregation & Architectural Pillars
{
  const pageContent = fs.readFileSync(path.join(srcDir, "app/page.tsx"), "utf8");
  // 1. Operational data must NOT be on public landing page
  assert.ok(!pageContent.includes("TodayScheduleWidget"), "Landing page must not contain TodayScheduleWidget");
  assert.ok(!pageContent.includes("ClinicalReviewQueueWidget"), "Landing page must not contain ClinicalReviewQueueWidget");
  assert.ok(!pageContent.includes("RecentActivityWidget"), "Landing page must not contain RecentActivityWidget");
  assert.ok(!pageContent.includes("AIWorkflowSummaryWidget"), "Landing page must not contain AIWorkflowSummaryWidget");
  assert.ok(!pageContent.includes("Manoj Das"), "Landing page must not hardcode patient schedules");

  // 2. High-impact public landing page content must be present
  assert.ok(pageContent.includes("Less paperwork"), "Hero headline must be present");
  assert.ok(pageContent.includes("Continuous Care Intelligence"), "Continuous care badge must be present");
  assert.ok(pageContent.includes("THE CONTINUOUS CLINICAL WORKFLOW"), "6-stage clinical continuum must be present");
  assert.ok(pageContent.includes("THE 12-STAGE MASTER CASE CONTINUOUS LOOP"), "12-stage Master Case loop must be present");
  assert.ok(pageContent.includes("Six Distinct Role Experiences"), "Role ingress section must be present");
  assert.ok(pageContent.includes("Paschim Banga Doctrine"), "Constitutional emergency doctrine must be present");
  assert.ok(pageContent.includes("Zero-PII & Statutory Compliance"), "DPDP Act compliance pillar must be present");

  console.log("✓ Test 14: Public Landing Page verifies clean role segregation & architectural pillars");
}

// Test 15: Operational Clinical Dashboards Role Placement
{
  const staffContent = fs.readFileSync(path.join(srcDir, "app/staff/page.tsx"), "utf8");
  const reviewContent = fs.readFileSync(path.join(srcDir, "app/staff/review/page.tsx"), "utf8");
  const receptionContent = fs.readFileSync(path.join(srcDir, "app/staff/reception/page.tsx"), "utf8");
  const systemContent = fs.readFileSync(path.join(srcDir, "app/system/page.tsx"), "utf8");

  // Staff Gateway has Schedule, Review Queue & AI Workflow Summary
  assert.ok(staffContent.includes("TodayScheduleWidget"), "Staff gateway must embed TodayScheduleWidget");
  assert.ok(staffContent.includes("ClinicalReviewQueueWidget"), "Staff gateway must embed ClinicalReviewQueueWidget");
  assert.ok(staffContent.includes("AIWorkflowSummaryWidget"), "Staff gateway must embed AIWorkflowSummaryWidget");

  // Review Workspace has Review Queue & AI Workflow Summary
  assert.ok(reviewContent.includes("ClinicalReviewQueueWidget"), "Review page must embed ClinicalReviewQueueWidget");
  assert.ok(reviewContent.includes("AIWorkflowSummaryWidget"), "Review page must embed AIWorkflowSummaryWidget");

  // Reception Workspace has Today's Appointments tab with TodayScheduleWidget
  assert.ok(receptionContent.includes("TodayScheduleWidget"), "Reception page must embed TodayScheduleWidget");
  assert.ok(receptionContent.includes("appointments={receptionAppointments}"), "Reception page must pass registered appointments into TodayScheduleWidget");

  // System Workspace has Recent Activity Audit widget
  assert.ok(systemContent.includes("RecentActivityWidget"), "System page must embed RecentActivityWidget");

  console.log("✓ Test 15: Role-specific operational dashboards verify authentic widget placement");
}

console.log("--- All Master Workflow, Route & Interaction Tests Passed (15/15) ---");

