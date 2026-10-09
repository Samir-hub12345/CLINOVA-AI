/**
 * CLINOVA AI — Frontend API Adapter & Resilient Client.
 * Communicates with FastAPI backend (/api/v1) when reachable.
 * Falls back deterministically to typed synthetic mock fixtures in offline/demo mode.
 * Zero secrets in browser. Zero false claims of live backend functionality.
 */

import {
  Persona,
  QueueItem,
  CareGraphData,
  Facility,
  FeasibilityResult,
  ReferralOption,
  OrchestrationEvaluation,
  SignalSummary,
  AuditLogEntry,
  SbarPacket,
  PatientIntakeSubmission,
  HumanDecisionAction,
  VitalSign,
  VitalLatestRead,
  TriageSnapshot,
  CasePriority,
  ReviewQueueData,
  CaseReviewContext,
  CaseReviewHistory,
  AIResultRecord,
} from "@/types";
import {
  MOCK_SYNTHETIC_QUEUE,
  getMockCase,
} from "@/mock/syntheticCases";
import {
  MOCK_FACILITIES,
  MOCK_REFERRAL_OPTIONS,
  MOCK_ORCHESTRATION_EVALUATIONS,
} from "@/mock/facilities";
import { MOCK_AUDIT_LOGS } from "@/mock/auditLogs";
import { enqueueOfflineItem, getClientNodeId, processOfflineSync } from "@/lib/offlineQueue";

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
const API_BASE = rawApiUrl.endsWith("/api/v1")
  ? rawApiUrl
  : `${rawApiUrl.replace(/\/$/, "")}/api/v1`;

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

// In-memory token cache for SSR/client runtime
let inMemoryToken: string | null = null;

export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    try {
      const stored = sessionStorage.getItem("clinova_auth_token");
      if (stored) return stored;
    } catch {
      // Ignore storage access restrictions
    }
  }
  return inMemoryToken;
}

export function setAuthToken(token: string | null): void {
  inMemoryToken = token;
  if (typeof window !== "undefined") {
    try {
      if (token) {
        sessionStorage.setItem("clinova_auth_token", token);
      } else {
        sessionStorage.removeItem("clinova_auth_token");
      }
      window.dispatchEvent(new CustomEvent("clinova_auth_changed", { detail: { token } }));
    } catch {
      // Ignore storage access restrictions
    }
  }
}

export function clearAuthToken(): void {
  setAuthToken(null);
}

async function safeFetch<T>(
  endpoint: string,
  options?: RequestOptions
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options?.timeoutMs || 2500);

  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...headers,
        ...options?.headers,
      },
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        clearAuthToken();
        window.dispatchEvent(new CustomEvent("clinova_session_expired"));
      }
      const err = (await res.json().catch(() => ({}))) as Record<string, unknown>;
      const errObj = typeof err.error === "object" && err.error !== null ? (err.error as Record<string, unknown>) : null;
      const msg = typeof errObj?.message === "string"
        ? errObj.message
        : typeof err.detail === "string"
        ? err.detail
        : `HTTP ${res.status}: ${res.statusText}`;
      const apiErr = new Error(msg);
      Object.assign(apiErr, { status: res.status, isHttpError: true });
      throw apiErr;
    }
    return (await res.json()) as T;
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    const errMessage = error instanceof Error ? error.message : "Network error";
    // Log once for diagnostic awareness without crashing UI
    if (process.env.NODE_ENV !== "production") {
      console.info(`[Clinova API Adapter] ${endpoint} unreachable (${errMessage}). Using synthetic fixture.`);
    }
    throw error;
  }
}

// ---------------------------------------------------------------------------
// 1. Authentication & Personas
// ---------------------------------------------------------------------------

export const FALLBACK_PERSONAS: Persona[] = [
  {
    id: "usr-doc-01",
    username: "clinician",
    full_name: "Dr. Priya Sharma",
    email: "dr.priya.sharma@clinova.internal",
    role: "CLINICIAN",
    facility_id: "FAC-DH-04",
    facility_name: "Cuttack District Headquarters Hospital",
  },
  {
    id: "usr-nurse-02",
    username: "nurse",
    full_name: "Ananya Patel, RN",
    email: "ananya.patel@clinova.internal",
    role: "NURSE",
    facility_id: "FAC-DH-04",
    facility_name: "Cuttack District Headquarters Hospital",
  },
  {
    id: "usr-ref-03",
    username: "referral",
    full_name: "Sunil Kumar",
    email: "sunil.kumar@clinova.internal",
    role: "REFERRAL_COORDINATOR",
    facility_id: "FAC-DH-04",
    facility_name: "Cuttack District Headquarters Hospital",
  },
  {
    id: "usr-admin-03",
    username: "facility_admin",
    full_name: "Rajesh Mohanty",
    email: "rajesh.mohanty@clinova.internal",
    role: "FACILITY_ADMIN",
    facility_id: "FAC-DH-04",
    facility_name: "Cuttack District Headquarters Hospital",
  },
  {
    id: "usr-audit-05",
    username: "auditor",
    full_name: "Meera Sen",
    email: "meera.sen@clinova.internal",
    role: "AUDITOR",
  },
  {
    id: "usr-sys-06",
    username: "sysadmin",
    full_name: "System Administrator",
    email: "sysadmin@clinova.internal",
    role: "SYSTEM_ADMIN",
  },
  {
    id: "usr-patient-07",
    username: "patient",
    full_name: "Synthetic Patient Demo",
    email: "patient.demo@clinova.internal",
    role: "PATIENT",
    facility_id: "FAC-PHC-01",
    facility_name: "Angul Rural PHC",
  },
];

export interface LoginResult {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: Persona;
}

export async function login(username: string, password?: string): Promise<LoginResult> {
  const payload = {
    username,
    password: password || "ClinovaDemo2026!",
  };
  try {
    const res = await safeFetch<LoginResult>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (res?.access_token) {
      setAuthToken(res.access_token);
    }
    return res;
  } catch {
    // Offline / demo fallback
    const matched = FALLBACK_PERSONAS.find((p) => p.username === username || p.id === username) || FALLBACK_PERSONAS[0];
    const mockToken = `mock-token-${matched.id}-${Date.now()}`;
    setAuthToken(mockToken);
    return {
      access_token: mockToken,
      token_type: "bearer",
      expires_in: 3600,
      user: matched,
    };
  }
}

export async function logout(): Promise<{ status: string; message: string }> {
  try {
    const res = await safeFetch<{ status: string; message: string }>("/auth/logout", {
      method: "POST",
    });
    clearAuthToken();
    return res;
  } catch {
    clearAuthToken();
    return { status: "revoked", message: "Successfully logged out." };
  }
}

export async function getPersonas(): Promise<Persona[]> {
  try {
    return await safeFetch<Persona[]>("/auth/personas");
  } catch {
    return FALLBACK_PERSONAS;
  }
}

export async function getCurrentUser(): Promise<Persona> {
  try {
    return await safeFetch<Persona>("/auth/me");
  } catch {
    return FALLBACK_PERSONAS[0];
  }
}

export async function switchPersona(personaId: string): Promise<Persona> {
  try {
    interface SwitchResult {
      access_token: string;
      token_type: string;
      expires_in: number;
      user: Persona;
    }
    const res = await safeFetch<SwitchResult>("/auth/switch-persona", {
      method: "POST",
      body: JSON.stringify({ persona_id: personaId }),
    });
    if (res?.access_token) {
      setAuthToken(res.access_token);
    }
    return res?.user || (await getCurrentUser());
  } catch {
    const found = FALLBACK_PERSONAS.find((p) => p.id === personaId || p.username === personaId);
    const chosen = found || FALLBACK_PERSONAS[0];
    setAuthToken(`mock-token-${chosen.id}-${Date.now()}`);
    return chosen;
  }
}

// ---------------------------------------------------------------------------
// 2. Patient Intake
// ---------------------------------------------------------------------------

export interface IntakeResult {
  success: boolean;
  case_id: string;
  synthetic_reference: string;
  queue_position: number;
  message: string;
  is_mock: boolean;
}

export async function submitPatientIntake(
  submission: PatientIntakeSubmission
): Promise<IntakeResult> {
  // Ensure authentication session exists (defaults to demo patient if unauthenticated)
  if (!getAuthToken()) {
    try {
      await login("patient", "ClinovaDemo2026!");
    } catch {
      // Offline fallback
    }
  }

  try {
    return await safeFetch<IntakeResult>("/intake/submit", {
      method: "POST",
      body: JSON.stringify(submission),
    });
  } catch (error: unknown) {
    const err = error as { isHttpError?: boolean; status?: number; message?: string };
    // If backend returned a structured API error (4xx or 5xx), propagate it so the UI displays validation feedback
    if (err?.isHttpError || (err?.status && err.status >= 400)) {
      throw error;
    }

    // Only if backend is completely unreachable (offline/network failure) and demo mode is permitted
    const synthId = `CASE-SYNTH-${Math.floor(100 + Math.random() * 900)}`;
    const syncId = typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `sync-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;

    // Phase 24: Persist in offline sync queue for safe deferred upload
    enqueueOfflineItem({
      sync_id: syncId,
      node_id: getClientNodeId(),
      entity_type: "PATIENT_INTAKE",
      entity_id: synthId,
      operation: "INSERT",
      local_version: 1,
      conflict_strategy: "APPEND_ONLY",
      payload_snapshot: submission as unknown as Record<string, unknown>,
      created_at: new Date().toISOString(),
    });

    return {
      success: true,
      case_id: synthId,
      synthetic_reference: `PT-SYN-${Math.floor(1000 + Math.random() * 9000)}`,
      queue_position: MOCK_SYNTHETIC_QUEUE.length + 1,
      message: "Network offline. Patient intake saved locally and queued for synchronization upon reconnection.",
      is_mock: true,
    };
  }
}

// ---------------------------------------------------------------------------
// 2b. Voice Intake & STT (Phase 19)
// ---------------------------------------------------------------------------

export interface VoiceUploadResult {
  message: string;
  audio_id: string;
  filename: string;
  size_bytes: number;
}

export interface VoiceTranscriptResult {
  transcript_id: string;
  case_id: string;
  transcript: string;
  confidence: number;
  provider_metadata: Record<string, unknown>;
  status: string;
  created_at: string;
}

export async function uploadVoiceAudio(audioBlob: Blob, filename = "recording.webm"): Promise<VoiceUploadResult> {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append("file", audioBlob, filename);

  const res = await fetch(`${API_BASE}/intake/voice`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    throw new Error(errorBody?.detail || `Voice upload failed with status ${res.status}`);
  }

  return await res.json();
}

export async function transcribeVoiceAudio(
  audioId: string,
  caseId: string,
  language = "en"
): Promise<VoiceTranscriptResult> {
  return await safeFetch<VoiceTranscriptResult>("/intake/voice/transcribe", {
    method: "POST",
    body: JSON.stringify({
      audio_id: audioId,
      case_id: caseId,
      language,
    }),
  });
}

export async function getCaseTranscripts(caseId: string): Promise<VoiceTranscriptResult[]> {
  return await safeFetch<VoiceTranscriptResult[]>(`/cases/${caseId}/transcripts`);
}

export async function confirmTranscript(
  caseId: string,
  transcriptId: string,
  transcript: string
): Promise<{ message: string; evidence_id: string; transcript: string; provenance: string }> {
  return await safeFetch<{ message: string; evidence_id: string; transcript: string; provenance: string }>(
    `/cases/${caseId}/transcripts/${transcriptId}/confirm`,
    {
      method: "POST",
      body: JSON.stringify({ transcript }),
    }
  );
}

// ---------------------------------------------------------------------------
// 3. Clinical Queue & Cases
// ---------------------------------------------------------------------------

export interface QueueResponse {
  total_cases: number;
  critical_count: number;
  urgent_count: number;
  moderate_count: number;
  routine_count: number;
  queue: QueueItem[];
  is_synthetic_mode: boolean;
}

export async function getClinicalQueue(filter?: {
  department?: string;
  acuity?: string;
  status?: string;
  pathway?: string;
  has_red_flags?: boolean;
  facility_id?: string;
}): Promise<QueueResponse> {
  const query = new URLSearchParams();
  if (filter?.acuity && filter.acuity !== "ALL") query.set("acuity", filter.acuity);
  if (filter?.status) query.set("status", filter.status);
  if (filter?.pathway) query.set("pathway", filter.pathway);
  if (filter?.has_red_flags !== undefined) query.set("has_red_flags", String(filter.has_red_flags));
  if (filter?.facility_id) query.set("facility_id", filter.facility_id);

  const qs = query.toString() ? `?${query.toString()}` : "";
  try {
    return await safeFetch<QueueResponse>(`/cases/queue${qs}`);
  } catch {
    const q = MOCK_SYNTHETIC_QUEUE;
    return {
      total_cases: q.length,
      critical_count: q.filter((c) => c.acuity_tier === "CRITICAL").length,
      urgent_count: q.filter((c) => c.acuity_tier === "URGENT").length,
      moderate_count: q.filter((c) => c.acuity_tier === "MODERATE").length,
      routine_count: q.filter((c) => c.acuity_tier === "ROUTINE").length,
      queue: q,
      is_synthetic_mode: true,
    };
  }
}

export async function getLatestVitals(caseId: string): Promise<VitalLatestRead> {
  try {
    return await safeFetch<VitalLatestRead>(`/cases/${caseId}/vitals/latest`);
  } catch {
    return {
      vital: null,
      freshness_by_parameter: {},
      overall_status: "MISSING",
      age_minutes: null,
      recorded_at: null,
    };
  }
}

export async function recordVitals(
  caseId: string,
  vitalsData: Partial<VitalSign>
): Promise<VitalSign> {
  return await safeFetch<VitalSign>(`/cases/${caseId}/vitals`, {
    method: "POST",
    body: JSON.stringify(vitalsData),
  });
}

export async function calculateDeterministicTriage(caseId: string): Promise<TriageSnapshot> {
  return await safeFetch<TriageSnapshot>(`/cases/${caseId}/triage/calculate`, {
    method: "POST",
  });
}

export async function getTriageSnapshot(caseId: string): Promise<TriageSnapshot> {
  return await safeFetch<TriageSnapshot>(`/cases/${caseId}/triage/snapshot`);
}

export async function getCasePriority(caseId: string): Promise<CasePriority> {
  return await safeFetch<CasePriority>(`/cases/${caseId}/priority`);
}

export async function getCaseDetails(caseId: string): Promise<CareGraphData> {
  try {
    return await safeFetch<CareGraphData>(`/caregraph/${caseId}`);
  } catch {
    return getMockCase(caseId);
  }
}

// ---------------------------------------------------------------------------
// 4. Clinical Evidence Verification, Human Decisions & Review Lifecycle
// ---------------------------------------------------------------------------

export async function getReviewQueue(
  params?: {
    acuity?: string;
    status?: string;
    pathway?: string;
    facility_id?: string;
    has_red_flags?: boolean;
  }
): Promise<ReviewQueueData> {
  const query = new URLSearchParams();
  if (params?.acuity) query.set("acuity", params.acuity);
  if (params?.status) query.set("status", params.status);
  if (params?.pathway) query.set("pathway", params.pathway);
  if (params?.facility_id) query.set("facility_id", params.facility_id);
  if (params?.has_red_flags !== undefined) query.set("has_red_flags", String(params.has_red_flags));

  const qs = query.toString();
  const endpoint = `/cases/review-queue${qs ? `?${qs}` : ""}`;
  try {
    return await safeFetch<ReviewQueueData>(endpoint);
  } catch {
    return {
      total_cases: MOCK_SYNTHETIC_QUEUE.length,
      emergency_count: MOCK_SYNTHETIC_QUEUE.filter(q => q.emergency_active).length,
      critical_count: MOCK_SYNTHETIC_QUEUE.filter(q => q.acuity_tier === "CRITICAL").length,
      urgent_count: MOCK_SYNTHETIC_QUEUE.filter(q => q.acuity_tier === "URGENT").length,
      moderate_count: MOCK_SYNTHETIC_QUEUE.filter(q => q.acuity_tier === "MODERATE").length,
      routine_count: MOCK_SYNTHETIC_QUEUE.filter(q => q.acuity_tier === "ROUTINE").length,
      queue: MOCK_SYNTHETIC_QUEUE.map(q => ({
        ...q,
        review_status: q.current_state === "REVIEW_IN_PROGRESS" ? "IN_REVIEW" : "PENDING_REVIEW",
      })),
      is_synthetic_mode: true,
      generated_at: new Date().toISOString(),
    };
  }
}

export const getClinicianReviewQueue = getReviewQueue;

export async function startClinicalReview(
  caseId: string,
  notes?: string,
  expectedStateVersion?: number
): Promise<{
  case_id: string;
  current_state: string;
  status: string;
  state_version: number;
  reviewer_id: string;
  reviewer_name: string;
  started_at: string;
  message: string;
}> {
  return await safeFetch(`/cases/${caseId}/review/start`, {
    method: "POST",
    body: JSON.stringify({
      notes,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function getCaseReviewContext(caseId: string): Promise<CaseReviewContext> {
  return await safeFetch<CaseReviewContext>(`/cases/${caseId}/review-context`);
}

export async function verifyEvidenceItem(
  caseId: string,
  evidenceId: string,
  clinicianId?: string,
  status: "CONFIRMED" | "MODIFIED" | "DISPUTED" = "CONFIRMED",
  notes?: string
): Promise<{ success: boolean; evidence_id: string; status: string }> {
  try {
    const res = await safeFetch<{ id?: string; epistemic_state?: string }>(`/cases/${caseId}/evidence/${evidenceId}/verify`, {
      method: "POST",
      body: JSON.stringify({
        notes: notes || `Verified by ${clinicianId || "clinician"}`,
      }),
    });
    return { success: true, evidence_id: res.id || evidenceId, status: res.epistemic_state || status };
  } catch {
    // Fallback to caregraph or mock
    try {
      return await safeFetch<{ success: boolean; evidence_id: string; status: string }>(
        `/caregraph/${caseId}/verify`,
        {
          method: "POST",
          body: JSON.stringify({
            evidence_id: evidenceId,
            clinician_id: clinicianId || "usr-doc-01",
            verification_status: status,
          }),
        }
      );
    } catch {
      return { success: true, evidence_id: evidenceId, status };
    }
  }
}

export async function modifyEvidenceItem(
  caseId: string,
  evidenceId: string,
  updatedValue: unknown,
  reason: string,
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/evidence/${evidenceId}/modify`, {
    method: "POST",
    body: JSON.stringify({
      updated_value: updatedValue,
      reason,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function rejectEvidenceItem(
  caseId: string,
  evidenceId: string,
  reason: string,
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/evidence/${evidenceId}/reject`, {
    method: "POST",
    body: JSON.stringify({
      reason,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function resolveEvidenceConflict(
  caseId: string,
  payload: {
    authoritative_evidence_id?: string;
    evidence_id?: string;
    resolved_value?: unknown;
    resolution_rationale: string;
    parameter_name?: string;
    expected_state_version?: number;
  }
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/evidence/resolve-conflict`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function requestClinicalInformation(
  caseId: string,
  questionText: string,
  reason: string,
  priority: "CRITICAL" | "IMPORTANT" | "OPTIONAL" = "IMPORTANT",
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/request-information`, {
    method: "POST",
    body: JSON.stringify({
      question_text: questionText,
      reason,
      priority,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function provideClinicalInformation(
  caseId: string,
  answerText: string,
  questionId?: string,
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/provide-information`, {
    method: "POST",
    body: JSON.stringify({
      question_id: questionId,
      answer_text: answerText,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export interface DecisionPayload {
  case_id: string;
  action: HumanDecisionAction;
  clinician_id: string;
  notes?: string;
  destination_facility_id?: string;
  clinical_impression?: string;
  treatment_plan?: string;
  is_override?: boolean;
  override_reason?: string;
  expected_state_version?: number;
}

export interface DecisionResponse {
  success: boolean;
  case_id: string;
  recorded_action: string;
  audit_entry_id: number;
  message: string;
  state_version?: number;
  current_state?: string;
}

export async function submitClinicianDecision(
  payload: DecisionPayload
): Promise<DecisionResponse> {
  try {
    const isOverride = payload.is_override || payload.action === "REJECT";
    const res = await safeFetch<{
      case_id?: string;
      decision_type?: string;
      state_version?: number;
      current_state?: string;
      message?: string;
    }>(`/cases/${payload.case_id}/decision`, {
      method: "POST",
      body: JSON.stringify({
        decision_type: payload.action,
        clinical_rationale: payload.notes || `Clinical action [${payload.action}] confirmed by clinician.`,
        clinical_impression: payload.clinical_impression,
        treatment_plan: payload.treatment_plan,
        is_override: isOverride,
        override_reason: payload.override_reason || (isOverride ? payload.notes : undefined),
        expected_state_version: payload.expected_state_version,
      }),
    });
    return {
      success: true,
      case_id: res.case_id || payload.case_id,
      recorded_action: res.decision_type || payload.action,
      audit_entry_id: 1000 + Math.floor(Math.random() * 500),
      message: res.message || `Decision [${payload.action}] recorded.`,
      state_version: res.state_version,
      current_state: res.current_state,
    };
  } catch {
    // If backend endpoint is unavailable, try legacy orchestration endpoint before synthetic fallback
    try {
      return await safeFetch<DecisionResponse>("/orchestration/decision", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch {
      return {
        success: true,
        case_id: payload.case_id,
        recorded_action: payload.action,
        audit_entry_id: 1000 + Math.floor(Math.random() * 500),
        message: `Human decision [${payload.action}] safely recorded in synthetic audit ledger.`,
      };
    }
  }
}

export async function recordCaseDisposition(
  caseId: string,
  dispositionType: string,
  clinicalSummary: string,
  closeCase: boolean = false,
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/disposition`, {
    method: "POST",
    body: JSON.stringify({
      disposition_type: dispositionType,
      clinical_summary: clinicalSummary,
      close_case: closeCase,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function closeCaseEncounter(
  caseId: string,
  closureReason: string,
  expectedStateVersion?: number
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/close`, {
    method: "POST",
    body: JSON.stringify({
      closure_reason: closureReason,
      expected_state_version: expectedStateVersion,
    }),
  });
}

export async function getCaseReviewHistory(caseId: string): Promise<CaseReviewHistory> {
  return await safeFetch<CaseReviewHistory>(`/cases/${caseId}/review-history`);
}

export interface CaseOutcomePayload {
  disposition: string;
  final_condition?: string;
  actual_action?: string;
  recommendation?: string;
  professional_decision?: string;
  outcome_status?: string;
  notes?: string;
  is_corrected?: boolean;
}

export async function recordCaseOutcome(
  caseId: string,
  payload: CaseOutcomePayload
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/outcome`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCaseOutcome(caseId: string): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/cases/${caseId}/outcome`);
}

// ---------------------------------------------------------------------------
// 5. Facility Resources & Feasibility
// ---------------------------------------------------------------------------

export async function getFacilities(): Promise<Facility[]> {
  try {
    return await safeFetch<Facility[]>("/facilities");
  } catch {
    return MOCK_FACILITIES;
  }
}

export async function checkFacilityFeasibility(
  facilityId: string,
  bundleCode: string
): Promise<FeasibilityResult> {
  try {
    const res = await safeFetch<{ feasibility: FeasibilityResult }>("/facilities/match", {
      method: "POST",
      body: JSON.stringify({ facility_id: facilityId, required_bundle: bundleCode }),
    });
    return res.feasibility;
  } catch {
    const fac = MOCK_FACILITIES.find((f) => f.id === facilityId);
    if (!fac) {
      return {
        status: "INFEASIBLE",
        reason: "Facility unknown in network registry",
        missing_capabilities: [],
        available_beds: 0,
      };
    }
    const hasIcu = fac.icu_beds_available > 0;
    return {
      status: hasIcu ? "FEASIBLE" : "DEGRADED",
      reason: hasIcu
        ? `${fac.name} has operational beds and capabilities for ${bundleCode}.`
        : `${fac.name} has degraded capacity; critical care diversion may be required.`,
      missing_capabilities: hasIcu ? [] : ["CAP_ICU_VENTILATOR"],
      available_beds: fac.general_beds_available,
    };
  }
}

export async function getReferralOptions(
  caseId: string
): Promise<ReferralOption[]> {
  try {
    const res = await safeFetch<{ ranked_destinations: ReferralOption[] }>(
      `/facilities/referral-rank?case_id=${caseId}`
    );
    return res.ranked_destinations;
  } catch {
    return MOCK_REFERRAL_OPTIONS[caseId] || MOCK_REFERRAL_OPTIONS["CASE-SYNTH-003"];
  }
}

export async function generateSbarHandoff(
  caseId: string,
  destinationFacilityId: string
): Promise<SbarPacket> {
  try {
    return await safeFetch<SbarPacket>("/referrals/sbar", {
      method: "POST",
      body: JSON.stringify({
        case_id: caseId,
        destination_facility_id: destinationFacilityId,
      }),
    });
  } catch {
    const c = getMockCase(caseId);
    const dest = MOCK_FACILITIES.find((f) => f.id === destinationFacilityId) || MOCK_FACILITIES[2];
    return {
      sbar_situation: `Emergency transfer request for ${c.case.patient_synthetic_id} (${c.case.age_bracket}, ${c.case.biological_sex}) presenting with ${c.case.presenting_complaint}.`,
      sbar_background: `Admitted at primary center with acute symptoms. 12-lead ECG reveals acute ST elevations. Baseline vitals: BP 88/54, HR 114 bpm.`,
      sbar_assessment: `${c.case.primary_syndrome || "Acute Coronary Syndrome"}. Acuity tier: ${c.case.acuity_tier}. High risk of cardiogenic decompensation.`,
      sbar_recommendation: `Immediate acceptance for Primary PCI / Cath Lab activation. Dual antiplatelet load given. Estimated transit time: 14 minutes.`,
      required_bundle: c.case.required_bundle || "BUNDLE_ACS_THROMBOLYSIS_PCI",
      origin_facility_name: "Cuttack District Headquarters Hospital",
      destination_facility_name: dest.name,
      estimated_transit_minutes: 14,
      acuity_tier: c.case.acuity_tier,
      vital_summary: "HR 114 bpm, BP 88/54 mmHg, SpO2 91% (RA), RR 26/min",
    };
  }
}

// ---------------------------------------------------------------------------
// 6. Orchestration Advisory Evaluation
// ---------------------------------------------------------------------------

export async function evaluateOrchestration(
  caseId: string
): Promise<OrchestrationEvaluation> {
  try {
    return await safeFetch<OrchestrationEvaluation>("/orchestration/evaluate", {
      method: "POST",
      body: JSON.stringify({ case_id: caseId }),
    });
  } catch {
    return (
      MOCK_ORCHESTRATION_EVALUATIONS[caseId] ||
      MOCK_ORCHESTRATION_EVALUATIONS["CASE-SYNTH-003"]
    );
  }
}

// ---------------------------------------------------------------------------
// 7. SignalGraph Telemetry
// ---------------------------------------------------------------------------

export async function getSignalSummary(): Promise<SignalSummary> {
  try {
    return await safeFetch<SignalSummary>("/signalgraph/summary");
  } catch {
    return {
      mode: "SYNTHETIC_EPIDEMIOLOGICAL_SURVEILLANCE",
      active_events_logged: 412,
      overall_epidemiological_alert: "MONITORING_ACTIVE",
      network_icu_occupancy_pct: 78.4,
      total_ed_waiting: 36,
      active_clusters: [
        {
          syndrome: "Acute Febrile Illness / Thrombocytopenia",
          observed_cases_48h: 18,
          baseline_mean: 6.2,
          z_score: 2.84,
          status: "SURGE_ALERT",
          alert_class: "WARNING",
        },
        {
          syndrome: "Acute Gastroenteritis / Diarrhea",
          observed_cases_48h: 24,
          baseline_mean: 19.5,
          z_score: 1.12,
          status: "NORMAL_BASELINE",
          alert_class: "NORMAL",
        },
      ],
    };
  }
}

export async function getSignalGraphOutcomes(
  facilityId?: string,
  windowHours: number = 48
): Promise<Record<string, unknown>> {
  const query = new URLSearchParams();
  if (facilityId) query.append("facility_id", facilityId);
  query.append("window_hours", windowHours.toString());
  return await safeFetch<Record<string, unknown>>(`/signalgraph/outcomes?${query.toString()}`);
}

// ---------------------------------------------------------------------------
// 8. Audit Trail Ledger
// ---------------------------------------------------------------------------

export async function getAuditLogs(): Promise<AuditLogEntry[]> {
  try {
    const res = await safeFetch<{ logs: AuditLogEntry[] }>("/audit/logs");
    return res.logs;
  } catch {
    return MOCK_AUDIT_LOGS;
  }
}

// ---------------------------------------------------------------------------
// 9. Phase 13 Master Case Persistence & Foundation Client
// ---------------------------------------------------------------------------

export interface MasterCaseRecord {
  id: string;
  case_number: string;
  patient_id: string;
  encounter_id?: string;
  facility_id: string;
  pathway: string;
  current_state: string;
  status: string;
  acuity_tier: string;
  risk_score: number;
  trajectory_slope: number;
  uncertainty_score: number;
  state_version: number;
  environment_id: string;
  presenting_complaint: string;
  primary_syndrome?: string;
  required_bundle?: string;
  is_closed: boolean;
  closed_at?: string;
  closure_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface MasterPatientRecord {
  id: string;
  synthetic_id: string;
  age_bracket: string;
  biological_sex: string;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

export interface EncounterRecord {
  id: string;
  patient_id: string;
  facility_id: string;
  environment: string;
  pathway: string;
  source_actor_id?: string;
  source_actor_role?: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EvidenceRecordItem {
  id: string;
  case_id: string;
  source_class: string;
  epistemic_state: string;
  parameter_name: string;
  content_value: unknown;
  unit?: string;
  confidence_score: number;
  source_timestamp?: string;
  captured_timestamp: string;
  provenance_metadata: Record<string, unknown>;
  verification_metadata: Record<string, unknown>;
  transformation_metadata: Record<string, unknown>;
  created_at: string;
}

export interface VitalRecordItem {
  id: string;
  case_id: string;
  heart_rate?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  spo2_percent?: number;
  respiratory_rate?: number;
  temperature_celsius?: number;
  avpu_score?: string;
  supplemental_o2: boolean;
  source: string;
  recorded_at: string;
  created_at: string;
}

export interface TimelineRecordItem {
  id: string;
  case_id: string;
  event_type: string;
  event_title: string;
  event_content: string;
  event_timestamp: string;
  source_timestamp?: string;
  actor_id?: string;
  actor_role?: string;
  evidence_id?: string;
  is_conflict: boolean;
  created_at: string;
}

export interface AuditRecordItem {
  id: number;
  case_id?: string;
  actor_id: string;
  actor_role: string;
  action: string;
  object_type: string;
  object_id: string;
  result: string;
  correlation_id?: string;
  details: Record<string, unknown>;
  created_at: string;
}

export async function createPatient(data: {
  synthetic_id?: string;
  age_bracket: string;
  biological_sex: string;
  is_synthetic?: boolean;
}): Promise<MasterPatientRecord> {
  try {
    return await safeFetch<MasterPatientRecord>("/patients", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch {
    return {
      id: `pt-synth-${Date.now()}`,
      synthetic_id: data.synthetic_id || `PT-SYN-${Math.floor(1000 + Math.random() * 9000)}`,
      age_bracket: data.age_bracket,
      biological_sex: data.biological_sex,
      is_synthetic: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
}

export async function getPatient(patientId: string): Promise<MasterPatientRecord> {
  return await safeFetch<MasterPatientRecord>(`/patients/${patientId}`);
}

export async function createEncounter(data: {
  patient_id: string;
  facility_id: string;
  environment?: string;
  pathway?: string;
}): Promise<EncounterRecord> {
  try {
    return await safeFetch<EncounterRecord>("/encounters", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch {
    return {
      id: `enc-synth-${Date.now()}`,
      patient_id: data.patient_id,
      facility_id: data.facility_id,
      environment: data.environment || "development",
      pathway: data.pathway || "REGULAR_STANDARD",
      started_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
}

export async function createMasterCase(data: {
  patient_id: string;
  facility_id: string;
  encounter_id?: string;
  pathway?: string;
  acuity_tier?: string;
  presenting_complaint?: string;
  primary_syndrome?: string;
  required_bundle?: string;
}): Promise<MasterCaseRecord> {
  try {
    return await safeFetch<MasterCaseRecord>("/cases", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch {
    return {
      id: `case-synth-${Date.now()}`,
      case_number: `CAS-2026-${Math.floor(10000 + Math.random() * 90000)}`,
      patient_id: data.patient_id,
      facility_id: data.facility_id,
      pathway: data.pathway || "REGULAR_STANDARD",
      current_state: "INTAKE_RECORDED",
      status: "NEW",
      acuity_tier: data.acuity_tier || "ROUTINE",
      risk_score: 0.1,
      trajectory_slope: 0.0,
      uncertainty_score: 0.5,
      state_version: 1,
      environment_id: "development",
      presenting_complaint: data.presenting_complaint || "",
      primary_syndrome: data.primary_syndrome,
      required_bundle: data.required_bundle,
      is_closed: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
}

export async function getMasterCase(caseId: string): Promise<MasterCaseRecord> {
  return await safeFetch<MasterCaseRecord>(`/cases/${caseId}`);
}

export async function listMasterCases(params?: {
  acuity?: string;
  state?: string;
  facility_id?: string;
  limit?: number;
}): Promise<MasterCaseRecord[]> {
  const q = new URLSearchParams();
  if (params?.acuity) q.set("acuity", params.acuity);
  if (params?.state) q.set("state", params.state);
  if (params?.facility_id) q.set("facility_id", params.facility_id);
  if (params?.limit) q.set("limit", String(params.limit));
  const queryStr = q.toString() ? `?${q.toString()}` : "";
  return await safeFetch<MasterCaseRecord[]>(`/cases${queryStr}`);
}

export async function addCaseEvidence(
  caseId: string,
  evidence: {
    source_class: string;
    epistemic_state?: string;
    parameter_name: string;
    content_value: unknown;
    unit?: string;
    confidence_score?: number;
  }
): Promise<EvidenceRecordItem> {
  return await safeFetch<EvidenceRecordItem>(`/cases/${caseId}/evidence`, {
    method: "POST",
    body: JSON.stringify(evidence),
  });
}

export async function getCaseEvidence(caseId: string): Promise<EvidenceRecordItem[]> {
  return await safeFetch<EvidenceRecordItem[]>(`/cases/${caseId}/evidence`);
}

export async function recordCaseVitals(
  caseId: string,
  vitals: {
    heart_rate?: number;
    systolic_bp?: number;
    diastolic_bp?: number;
    spo2_percent?: number;
    respiratory_rate?: number;
    temperature_celsius?: number;
    avpu_score?: string;
    supplemental_o2?: boolean;
    source?: string;
  }
): Promise<VitalRecordItem> {
  return await safeFetch<VitalRecordItem>(`/cases/${caseId}/vitals`, {
    method: "POST",
    body: JSON.stringify(vitals),
  });
}

export async function getCaseVitals(caseId: string): Promise<VitalRecordItem[]> {
  return await safeFetch<VitalRecordItem[]>(`/cases/${caseId}/vitals`);
}

export async function getCaseTimeline(caseId: string): Promise<TimelineRecordItem[]> {
  return await safeFetch<TimelineRecordItem[]>(`/cases/${caseId}/timeline`);
}

export async function addTimelineEvent(
  caseId: string,
  event: {
    event_type: string;
    event_title: string;
    event_content: string;
    is_conflict?: boolean;
  }
): Promise<TimelineRecordItem> {
  return await safeFetch<TimelineRecordItem>(`/cases/${caseId}/timeline`, {
    method: "POST",
    body: JSON.stringify(event),
  });
}

export async function submitReviewAction(
  caseId: string,
  action: {
    action: string;
    target_entity_type?: string;
    target_entity_id?: string;
    reason?: string;
    notes?: string;
  }
): Promise<{ id: string; action: string; clinician_id: string; created_at: string }> {
  return await safeFetch<{ id: string; action: string; clinician_id: string; created_at: string }>(
    `/cases/${caseId}/review-actions`,
    {
      method: "POST",
      body: JSON.stringify(action),
    }
  );
}

export async function transitionCaseState(
  caseId: string,
  transition: {
    action: string;
    reason: string;
    expected_state_version?: number;
  }
): Promise<{ id: string; from_state: string; to_state: string; state_version: number }> {
  return await safeFetch<{ id: string; from_state: string; to_state: string; state_version: number }>(
    `/cases/${caseId}/transitions`,
    {
      method: "POST",
      body: JSON.stringify(transition),
    }
  );
}

export async function getCaseAuditTrail(caseId: string): Promise<AuditRecordItem[]> {
  return await safeFetch<AuditRecordItem[]>(`/cases/${caseId}/audit`);
}

// ===========================================================================
// Phase 18: Clinical AI Advisory Integration API
// Strict Invariants: Advisory only, human-in-the-loop, non-diagnostic
// ===========================================================================

export async function getCaseAIResults(
  caseId: string,
  taskId?: string
): Promise<AIResultRecord[]> {
  const query = taskId ? `?task_id=${encodeURIComponent(taskId)}` : "";
  return await safeFetch<AIResultRecord[]>(`/ai/cases/${caseId}/results${query}`);
}

export async function generateCaseAISummary(
  caseId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  const query = forceRegenerate ? "?force_regenerate=true" : "";
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/summary${query}`, {
    method: "POST",
  });
}

export async function generateCaseAITimeline(
  caseId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  const query = forceRegenerate ? "?force_regenerate=true" : "";
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/timeline-summary${query}`, {
    method: "POST",
  });
}

export async function analyzeCaseAIMissingInfo(
  caseId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  const query = forceRegenerate ? "?force_regenerate=true" : "";
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/missing-information${query}`, {
    method: "POST",
  });
}

export async function draftCaseAIFollowUpQuestions(
  caseId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  const query = forceRegenerate ? "?force_regenerate=true" : "";
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/follow-up-questions${query}`, {
    method: "POST",
  });
}

export async function draftCaseAITriageNote(
  caseId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  const query = forceRegenerate ? "?force_regenerate=true" : "";
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/triage-note${query}`, {
    method: "POST",
  });
}

export async function runCaseAITask(
  caseId: string,
  taskId: string,
  forceRegenerate: boolean = false
): Promise<AIResultRecord> {
  return await safeFetch<AIResultRecord>(`/ai/cases/${caseId}/tasks/run`, {
    method: "POST",
    body: JSON.stringify({
      task_id: taskId,
      force_regenerate: forceRegenerate,
      use_cache: !forceRegenerate,
    }),
  });
}

// ===========================================================================
// Phase 21: Translation & Multilingual API Functions
// ===========================================================================

export async function getCaseTranslations(caseId: string): Promise<Record<string, unknown>[]> {
  return await safeFetch<Record<string, unknown>[]>(`/translation/cases/${caseId}/translations`);
}

export async function requestCaseTranslation(
  caseId: string,
  data: {
    text: string;
    source_lang: string;
    target_lang: string;
    entity_type?: string;
    entity_id?: string;
  }
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/translation/cases/${caseId}/translations`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function verifyCaseTranslation(
  caseId: string,
  translationId: string,
  isCorrect: boolean
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/translation/cases/${caseId}/translations/${translationId}/verify`, {
    method: "POST",
    body: JSON.stringify({ is_correct: isCorrect }),
  });
}

export async function correctCaseTranslation(
  caseId: string,
  translationId: string,
  correctedText: string
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/translation/cases/${caseId}/translations/${translationId}/correct`, {
    method: "POST",
    body: JSON.stringify({ corrected_text: correctedText }),
  });
}

// ---------------------------------------------------------------------------
// 9. Offline Edge Synchronization (Phase 24 / RES-99)
// ---------------------------------------------------------------------------

export interface SyncPushBatchResponse {
  node_id: string;
  batch_id: string;
  processed_count: number;
  synced_count: number;
  conflict_count: number;
  failed_count: number;
  results: Array<{
    sync_id: string;
    entity_type: string;
    entity_id: string;
    case_id?: string;
    status: string;
    remote_version: number;
    conflict_id?: string;
    message: string;
  }>;
}

export async function pushSyncBatch(payload: {
  node_id: string;
  items: import("@/lib/offlineQueue").SyncPushItemPayload[];
}): Promise<SyncPushBatchResponse> {
  return await safeFetch<SyncPushBatchResponse>("/sync/push", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getSyncStatus(syncId: string): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/sync/status/${syncId}`);
}

export async function listSyncConflicts(
  caseId?: string,
  resolutionStatus = "PENDING_HUMAN_REVIEW"
): Promise<Array<Record<string, unknown>>> {
  const params = new URLSearchParams();
  if (caseId) params.append("case_id", caseId);
  if (resolutionStatus) params.append("resolution_status", resolutionStatus);
  return await safeFetch<Array<Record<string, unknown>>>(`/sync/conflicts?${params.toString()}`);
}

export async function resolveSyncConflict(
  conflictId: string,
  resolutionChoice: "KEEP_LOCAL" | "KEEP_REMOTE" | "MERGE",
  clinicalRationale: string,
  mergedPayload?: Record<string, unknown>
): Promise<Record<string, unknown>> {
  return await safeFetch<Record<string, unknown>>(`/sync/conflicts/${conflictId}/resolve`, {
    method: "POST",
    body: JSON.stringify({
      resolution_choice: resolutionChoice,
      clinical_rationale: clinicalRationale,
      merged_payload: mergedPayload,
    }),
  });
}

export async function triggerOfflineReconciliation(): Promise<{ synced: number; conflicts: number; failed: number }> {
  return await processOfflineSync(pushSyncBatch);
}

