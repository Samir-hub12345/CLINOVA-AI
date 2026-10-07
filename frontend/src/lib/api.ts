/**
 * CLINOVA AI — Front-end API Client.
 * Communicates with FastAPI backend (/api/v1).
 * Features graceful resilient fallbacks for offline demo modes.
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
  SyndromicCluster,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}: ${res.statusText}`);
    }
    return (await res.json()) as T;
  } catch (error: any) {
    console.warn(`[Clinova API] Request to ${endpoint} failed:`, error.message);
    throw error;
  }
}

// 1. Authentication & Personas
export async function getPersonas(): Promise<Persona[]> {
  try {
    return await request<Persona[]>("/auth/personas");
  } catch {
    return [
      {
        id: "usr-doc-01",
        full_name: "Dr. Priya Sharma",
        email: "dr.priya.sharma@clinova.internal",
        role: "CLINICIAN",
        facility_id: "FAC-DH-04",
        facility_name: "Cuttack District Headquarters Hospital",
      },
      {
        id: "usr-nurse-02",
        full_name: "Ananya Patel, RN",
        email: "ananya.patel@clinova.internal",
        role: "NURSE",
        facility_id: "FAC-PHC-01",
        facility_name: "Angul Rural PHC",
      },
      {
        id: "usr-admin-03",
        full_name: "Rajesh Mohanty",
        email: "rajesh.mohanty@clinova.internal",
        role: "ADMIN",
        facility_id: "FAC-DH-04",
        facility_name: "Cuttack District Headquarters Hospital",
      },
    ];
  }
}

export async function getCurrentUser(): Promise<Persona> {
  try {
    return await request<Persona>("/auth/me");
  } catch {
    return {
      id: "usr-doc-01",
      full_name: "Dr. Priya Sharma",
      email: "dr.priya.sharma@clinova.internal",
      role: "CLINICIAN",
      facility_id: "FAC-DH-04",
      facility_name: "Cuttack District Headquarters Hospital",
    };
  }
}

export async function switchPersona(personaId: string): Promise<Persona> {
  return await request<Persona>("/auth/switch-persona", {
    method: "POST",
    body: JSON.stringify({ persona_id: personaId }),
  });
}

// 2. Intake
export async function submitTextIntake(payload: {
  facility_id: string;
  reported_name?: string;
  reported_age?: number;
  biological_sex: string;
  narrative_text: string;
  language?: string;
  vitals?: Record<string, any>;
}): Promise<any> {
  return await request<any>("/intake/text", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function submitVoiceIntake(payload: {
  facility_id: string;
  audio_transcript: string;
  confidence_score?: number;
  language?: string;
}): Promise<any> {
  return await request<any>("/intake/voice", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function parseOcrReport(rawText: string, confidence: number = 0.88): Promise<any> {
  return await request<any>("/intake/ocr", {
    method: "POST",
    body: JSON.stringify({ raw_text: rawText, confidence_score: confidence }),
  });
}

// 3. Clinical Queue & Cases
export async function getClinicalQueue(): Promise<{
  total_cases: number;
  critical_count: number;
  urgent_count: number;
  queue: QueueItem[];
}> {
  return await request<any>("/cases/queue");
}

export async function closeCaseOutcome(
  caseId: string,
  payload: { disposition: string; final_condition: string; notes?: string; actor_id: string }
): Promise<any> {
  return await request<any>(`/cases/${caseId}/outcome`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// 4. CareGraph
export async function getCareGraph(caseId: string): Promise<CareGraphData> {
  return await request<CareGraphData>(`/caregraph/${caseId}`);
}

export async function appendVitals(caseId: string, vitals: Record<string, any>): Promise<any> {
  return await request<any>(`/caregraph/${caseId}/vitals`, {
    method: "POST",
    body: JSON.stringify(vitals),
  });
}

export async function verifyEvidence(
  caseId: string,
  payload: { evidence_id: string; verification_status: string; clinician_id: string; notes?: string }
): Promise<any> {
  return await request<any>(`/caregraph/${caseId}/verify`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// 5. FacilityGraph
export async function getFacilities(): Promise<Facility[]> {
  return await request<Facility[]>("/facilities");
}

export async function checkFeasibility(
  facilityId: string,
  bundleCode: string
): Promise<{ feasibility: FeasibilityResult }> {
  return await request<any>("/facilities/match", {
    method: "POST",
    body: JSON.stringify({ facility_id: facilityId, required_bundle: bundleCode }),
  });
}

export async function rankReferrals(
  currentFacilityId: string,
  bundleCode: string
): Promise<{ ranked_destinations: ReferralOption[] }> {
  return await request<any>("/facilities/referral-rank", {
    method: "POST",
    body: JSON.stringify({ current_facility_id: currentFacilityId, required_bundle: bundleCode }),
  });
}

export async function toggleCapability(
  facilityId: string,
  capabilityCode: string,
  isOperational: boolean
): Promise<any> {
  return await request<any>(`/facilities/${facilityId}/toggle-capability`, {
    method: "POST",
    body: JSON.stringify({ capability_code: capabilityCode, is_operational: isOperational }),
  });
}

export async function generateSbar(caseId: string, destinationFacilityId: string): Promise<SbarPacket> {
  return await request<SbarPacket>("/referrals/sbar", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId, destination_facility_id: destinationFacilityId }),
  });
}

// 6. Orchestration
export async function evaluateOrchestration(
  caseId: string,
  facilityId?: string
): Promise<OrchestrationEvaluation> {
  return await request<OrchestrationEvaluation>("/orchestration/evaluate", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId, facility_id: facilityId }),
  });
}

export async function submitClinicianDecision(payload: {
  case_id: string;
  action: string;
  decision_type: string;
  clinician_id: string;
  override_reason?: string;
  notes?: string;
}): Promise<any> {
  return await request<any>("/orchestration/decision", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// 7. SignalGraph
export async function getSignalSummary(): Promise<SignalSummary> {
  return await request<SignalSummary>("/signalgraph/summary");
}

export async function getSyndromicSurges(): Promise<{ clusters: SyndromicCluster[] }> {
  return await request<any>("/signalgraph/surges");
}

export async function injectSignalEvent(payload: {
  facility_id: string;
  syndrome_tag: string;
  acuity_tier: string;
}): Promise<any> {
  return await request<any>("/signalgraph/inject-event", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// 8. Audit Trail
export async function getAuditLogs(caseId?: string): Promise<{ count: number; logs: AuditLogEntry[] }> {
  const query = caseId ? `?case_id=${caseId}` : "";
  return await request<any>(`/audit/logs${query}`);
}
