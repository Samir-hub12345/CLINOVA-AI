import {
  User,
  Patient,
  Consultation,
  TriageResponse,
  SOAPGenerateResponse,
  AuditLog,
  VitalsInput,
  TriageCase,
  ReportOCRResult,
  SpeechTranscribeResult,
  TranslationResult,
  ReferralNote,
  OCRField,
  MedicalDocument,
  DocumentArtifact,
  PresignedUrlResponse,
  PatientCase,
  PatientConsultation,
  CaseReceipt,
  PortalProfileInput,
  AdminOverview,
  AssistantPreference,
  AssistantCapabilities,
  AssistantMessageRequest,
  AssistantMessageResponse,
  AssistantToolExecuteRequest,
  AssistantToolExecuteResponse,
  VerificationRun,
  VerificationFinding,
  VerificationConflict,
  ReviewReadinessSummary,
  CompletionSession,
  CompletionQuestion,
  NextQuestionResponse,
  SubmitAnswerResponse,
} from "@/types";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("clinova_token");
}

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("clinova_token", token);
  }
}

export function clearToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("clinova_token");
    localStorage.removeItem("clinova_user");
  }
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const user = localStorage.getItem("clinova_user");
  try {
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user: User) {
  if (typeof window !== "undefined") {
    localStorage.setItem("clinova_user", JSON.stringify(user));
  }
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Global network latency and failure listeners
let networkLatencyReporter: ((ms: number) => void) | null = null;
let networkFailureReporter: (() => void) | null = null;

export function registerNetworkReporters(
  onLatency: (ms: number) => void,
  onFailure: () => void
) {
  networkLatencyReporter = onLatency;
  networkFailureReporter = onFailure;
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs: number = 14000
): Promise<ApiResponse<T>> {
  // Pre-flight check: if browser is strictly offline, reject immediately
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    return {
      error: "You are currently offline. Please verify your network connection and try again.",
      status: 0,
    };
  }

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const token = getToken();
  const method = (options.method || "GET").toUpperCase();

  const headers: Record<string, string> = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers as Record<string, string>),
  };

  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const executeRequest = async (): Promise<ApiResponse<T>> => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const start = performance.now();

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timer);
      const elapsed = Math.round(performance.now() - start);
      networkLatencyReporter?.(elapsed);

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 401 && token && token === getToken() && !endpoint.startsWith("/api/v1/auth/login")) {
          clearToken();
          window.dispatchEvent(new Event("clinova:session-expired"));
        }
        if (response.status === 403 && !endpoint.startsWith("/api/v1/auth/")) {
          window.dispatchEvent(new Event("clinova:access-denied"));
        }
        let errorMsg = response.statusText;
        if (data?.detail) {
          errorMsg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        }
        return {
          error: errorMsg,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error: any) {
      clearTimeout(timer);
      networkFailureReporter?.();

      if (error.name === "AbortError") {
        return {
          error: "Connection timed out. Clinova AI service did not respond within the time limit.",
          status: 408,
        };
      }

      return {
        error: error?.message || "Network error. Please ensure Clinova AI services are reachable.",
        status: 500,
      };
    }
  };

  // Safe retry: ONLY retry idempotent GET requests once upon network failure
  // NEVER automatically retry state-modifying mutations (POST, PUT, DELETE) to protect clinical integrity
  const initial = await executeRequest();
  if (method === "GET" && (initial.status === 0 || initial.status === 408 || initial.status >= 502)) {
    // Wait 500ms before single safe retry
    await new Promise((r) => setTimeout(r, 500));
    return await executeRequest();
  }

  return initial;
}

// API Service Callers
export const api = {
  getMyProfile: () => fetchApi<Patient | null>("/api/v1/portal/profile"),
  saveMyProfile: (payload: PortalProfileInput) => fetchApi<Patient>("/api/v1/portal/profile", { method: "PUT", body: JSON.stringify(payload) }),
  getMyCases: () => fetchApi<PatientCase[]>("/api/v1/portal/cases"),
  getMyConsultations: () => fetchApi<PatientConsultation[]>("/api/v1/portal/consultations"),
  getAdminOverview: () => fetchApi<AdminOverview>("/api/v1/admin/overview"),
  getAdminUsers: () => fetchApi<User[]>("/api/v1/admin/users"),
  // Auth
  async login(email: string, password: string) {
    const res = await fetchApi<{ access_token: string; user: User }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (res.data) {
      setToken(res.data.access_token);
      setStoredUser(res.data.user);
    }
    return res;
  },

  async register(payload: { email: string; password: string; full_name: string; role: string }) {
    return fetchApi<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getMe() {
    return fetchApi<User>("/api/v1/auth/me");
  },

  // Patients
  async getPatients(search?: string) {
    const query = search ? `?q=${encodeURIComponent(search)}` : "";
    return fetchApi<{ total: number; items: Patient[] }>(`/api/v1/patients${query}`);
  },

  async getPatient(id: string) {
    return fetchApi<Patient>(`/api/v1/patients/${id}`);
  },

  async createPatient(payload: Partial<Patient>) {
    return fetchApi<Patient>("/api/v1/patients", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async updatePatient(id: string, payload: Partial<Patient>) {
    return fetchApi<Patient>(`/api/v1/patients/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },

  // Consultations
  async getConsultations(filters?: string | { patientId?: string; status?: string }) {
    if (typeof filters === "string") {
      const query = filters ? `?patient_id=${filters}` : "";
      return fetchApi<{ total: number; items: Consultation[] }>(`/api/v1/consultations${query}`);
    }
    const params = new URLSearchParams();
    if (filters?.patientId) params.append("patient_id", filters.patientId);
    if (filters?.status) params.append("status", filters.status);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return fetchApi<{ total: number; items: Consultation[] }>(`/api/v1/consultations${qs}`);
  },

  async getConsultation(id: string) {
    return fetchApi<Consultation>(`/api/v1/consultations/${id}`);
  },

  async createConsultation(payload: {
    patient_id: string;
    chief_complaint: string;
    vitals_data?: string;
    triage_level?: string;
    symptoms?: string[];
    vitals?: VitalsInput;
    medical_history?: string;
  }) {
    return fetchApi<Consultation>("/api/v1/consultations", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async updateSoapNotes(
    id: string,
    soap: { subjective: string; objective: string; assessment: string; plan: string }
  ) {
    return fetchApi<Consultation>(`/api/v1/consultations/${id}/soap`, {
      method: "PUT",
      body: JSON.stringify(soap),
    });
  },

  // AI Decision Support
  async runTriage(payload: {
    chief_complaint: string;
    symptoms: string[];
    symptom_duration?: string;
    vitals?: VitalsInput;
    relevant_medical_history?: string;
    patient_id?: string;
  }) {
    return fetchApi<TriageResponse>("/api/v1/ai/triage", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getTriageAssessment(payload: {
    chief_complaint: string;
    symptoms: string[];
    vitals?: VitalsInput;
    patient_age?: number;
    patient_gender?: string;
  }) {
    return fetchApi<TriageResponse>("/api/v1/ai/triage", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async generateSoapNotes(payload: {
    patient_name?: string;
    chief_complaint: string;
    encounter_notes: string;
    vitals?: VitalsInput;
    medical_history?: string;
  }) {
    return fetchApi<SOAPGenerateResponse>("/api/v1/ai/soap-summary", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // Audit Logs
  async getAuditLogs(limit: number = 50) {
    return fetchApi<{ total: number; items: AuditLog[] }>(`/api/v1/audit-logs?limit=${limit}`);
  },

  // -------------------------------------------------------------------------
  // PS03 Triage Assistant & Multimodal Endpoints
  // -------------------------------------------------------------------------
  async getCases(queueCategory?: string, statusFilter?: string) {
    const params = new URLSearchParams();
    if (queueCategory) params.append("queue_category", queueCategory);
    if (statusFilter) params.append("status_filter", statusFilter);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return fetchApi<TriageCase[]>(`/api/v1/cases${qs}`);
  },

  async getCase(caseId: string) {
    return fetchApi<TriageCase>(`/api/v1/cases/${caseId}`);
  },

  async createCase(payload: {
    preferred_language?: string;
    facility_type?: string;
    visit_type?: string;
    approximate_age?: number;
    gender?: string;
    context_notes?: string;
    raw_symptoms: string;
    speech_transcript?: string;
    detected_language?: string;
    report_filename?: string;
    report_ocr_data?: OCRField[];
    image_reference?: string;
    consent_acknowledged?: boolean;
  }) {
    return fetchApi<CaseReceipt>("/api/v1/cases", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async deleteCaseData(caseId: string) {
    return fetchApi<{ status: string; message: string }>(`/api/v1/cases/${caseId}`, {
      method: "DELETE",
    });
  },

  async transcribeSpeech(formData: FormData) {
    return fetchApi<SpeechTranscribeResult>("/api/v1/intake/speech", { method: "POST", body: formData });
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      return { data: null, error: "You are currently offline. Speech transcription requires an internet connection." };
    }

    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 25000);
    const start = performance.now();

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/intake/speech`, {
        method: "POST",
        headers,
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timer);
      networkLatencyReporter?.(Math.round(performance.now() - start));

      if (!res.ok) {
        return { data: null, error: `Upload error: ${res.statusText}` };
      }
      const data = await res.json();
      return { data, error: null };
    } catch (err: any) {
      clearTimeout(timer);
      networkFailureReporter?.();
      return {
        data: null,
        error: err.name === "AbortError"
          ? "Audio upload timed out. Connection is slow or unstable."
          : "Network error during audio processing.",
      };
    }
  },

  async translateText(text: string, source_language: string = "or") {
    return fetchApi<TranslationResult>("/api/v1/intake/translate", {
      method: "POST",
      body: JSON.stringify({ text, source_language }),
    });
  },

  async processReportOCR(formData: FormData) {
    return fetchApi<ReportOCRResult>("/api/v1/intake/ocr", { method: "POST", body: formData });
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      return { data: null, error: "You are currently offline. Document OCR requires an internet connection." };
    }

    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    const start = performance.now();

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/intake/ocr`, {
        method: "POST",
        headers,
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timer);
      networkLatencyReporter?.(Math.round(performance.now() - start));

      if (!res.ok) {
        return { data: null, error: `OCR error: ${res.statusText}` };
      }
      const data = await res.json();
      return { data, error: null };
    } catch (err: any) {
      clearTimeout(timer);
      networkFailureReporter?.();
      return {
        data: null,
        error: err.name === "AbortError"
          ? "Document OCR upload timed out. Connection is slow or unstable."
          : "Network error during document processing.",
      };
    }
  },

  async performReviewAction(
    caseId: string,
    payload: {
      action: "approve" | "edit" | "reject" | "escalate";
      reviewer_notes?: string;
      edited_summary?: string;
      confirmed_queue_category?: string;
      verified_ocr_fields?: OCRField[];
    }
  ) {
    return fetchApi<TriageCase>(`/api/v1/review/${caseId}/action`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getReferralNote(caseId: string) {
    return fetchApi<ReferralNote>(`/api/v1/review/${caseId}/referral`);
  },

  async getTriageCases(params?: {
    queue_category?: string;
    status_filter?: string;
    assigned_doctor_id?: string;
    patient_id?: string;
    limit?: number;
  }) {
    const q = new URLSearchParams();
    if (params?.queue_category) q.set("queue_category", params.queue_category);
    if (params?.status_filter) q.set("status_filter", params.status_filter);
    if (params?.assigned_doctor_id) q.set("assigned_doctor_id", params.assigned_doctor_id);
    if (params?.patient_id) q.set("patient_id", params.patient_id);
    if (params?.limit) q.set("limit", String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : "";
    return fetchApi<TriageCase[]>(`/api/v1/cases${qs}`);
  },

  async assignCase(
    caseId: string,
    payload: {
      assigned_doctor_id?: string;
      assigned_doctor_name?: string;
      assigned_department?: string;
      priority_category?: string;
      notes?: string;
    }
  ) {
    return fetchApi<TriageCase>(`/api/v1/cases/${caseId}/assign`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async verifyCaseIntake(
    caseId: string,
    payload: {
      verified?: boolean;
      vitals?: Record<string, any>;
      staff_notes?: string;
      route_to_doctor_id?: string;
      route_to_doctor_name?: string;
      route_to_department?: string;
    }
  ) {
    return fetchApi<TriageCase>(`/api/v1/cases/${caseId}/verify-intake`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getMyPatientProfile() {
    return fetchApi<Patient>("/api/v1/patients/me");
  },

  async listFacilityUsers() {
    return fetchApi<User[]>("/api/v1/auth/users");
  },

  async toggleUserStatus(userId: string, isActive: boolean) {
    return fetchApi<User>(`/api/v1/auth/users/${userId}/status?is_active=${isActive}`, {
      method: "PUT",
    });
  },

  // Bulk Ingestion & FHIR
  async previewPatientImport(formData: FormData) {
    return fetchApi<{
      total_records: number;
      valid_count: number;
      invalid_count: number;
      preview_items: any[];
      validation_errors: Array<{ row_number: number; raw_data: any; errors: string[] }>;
    }>("/api/v1/patients/import/preview", {
      method: "POST",
      body: formData,
    });
  },

  async executePatientImport(records: any[], facilityId?: string) {
    const qs = facilityId ? `?facility_id=${encodeURIComponent(facilityId)}` : "";
    return fetchApi<{
      total_processed: number;
      created_count: number;
      skipped_count: number;
      duplicate_count: number;
      created_patient_ids: string[];
    }>(`/api/v1/patients/import/execute${qs}`, {
      method: "POST",
      body: JSON.stringify(records),
    });
  },

  // Deduplication & Merge
  async getDuplicateCandidates(facilityId?: string) {
    const qs = facilityId ? `?facility_id=${encodeURIComponent(facilityId)}` : "";
    return fetchApi<Array<{
      primary_patient_id: string;
      primary_mrn: string;
      primary_name: string;
      duplicate_patient_id: string;
      duplicate_mrn: string;
      duplicate_name: string;
      confidence_score: number;
      match_level: string;
      matching_signals: string[];
    }>>(`/api/v1/patients/duplicates/candidates${qs}`);
  },

  async mergePatients(payload: {
    primary_patient_id: string;
    secondary_patient_id: string;
    merge_reason: string;
  }) {
    return fetchApi<{
      primary_patient_id: string;
      merged_patient_id: string;
      encounters_moved: number;
      observations_moved: number;
      notes_moved: number;
      documents_moved: number;
      cases_moved: number;
      status: string;
    }>("/api/v1/patients/merge", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // Data Retention & Disposal
  async triggerRetentionSweep(dryRun: boolean = true) {
    return fetchApi<{
      timestamp: string;
      dry_run: boolean;
      rules_executed: Array<{
        rule_name: string;
        candidates_count: number;
        purged_count: number;
        bytes_freed: number;
        details: any;
      }>;
      total_candidates: number;
      total_purged: number;
      total_bytes_freed: number;
      duration_seconds: number;
    }>(`/api/v1/admin/retention/sweep?dry_run=${dryRun}`, {
      method: "POST",
    });
  },
};

export const documentsApi = {
  async listDocuments(params?: {
    patient_id?: string;
    document_type?: string;
    status?: string;
    facility_id?: string;
    include_archived?: boolean;
    skip?: number;
    limit?: number;
  }) {
    const q = new URLSearchParams();
    if (params?.patient_id) q.set("patient_id", params.patient_id);
    if (params?.document_type) q.set("document_type", params.document_type);
    if (params?.status) q.set("status", params.status);
    if (params?.facility_id) q.set("facility_id", params.facility_id);
    if (params?.include_archived) q.set("include_archived", "true");
    if (params?.skip) q.set("skip", String(params.skip));
    if (params?.limit) q.set("limit", String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : "";
    return fetchApi<{ total: number; items: MedicalDocument[] } | MedicalDocument[]>(`/api/v1/documents${qs}`);
  },

  async uploadDocument(formData: FormData) {
    return fetchApi<MedicalDocument>("/api/v1/documents/upload", {
      method: "POST",
      body: formData,
    });
  },

  async getDocument(id: string) {
    return fetchApi<MedicalDocument>(`/api/v1/documents/${id}`);
  },

  async getPresignedUrl(id: string, expiresInMinutes: number = 15) {
    return fetchApi<PresignedUrlResponse>(
      `/api/v1/documents/${id}/presigned-url?expires_in_minutes=${expiresInMinutes}`
    );
  },

  async amendDocument(id: string, formData: FormData) {
    return fetchApi<MedicalDocument>(`/api/v1/documents/${id}/amend`, {
      method: "POST",
      body: formData,
    });
  },

  async deleteDocument(id: string) {
    return fetchApi<{ message: string; document_id: string }>(`/api/v1/documents/${id}`, {
      method: "DELETE",
    });
  },

  async listArtifacts(documentId: string) {
    return fetchApi<DocumentArtifact[]>(`/api/v1/documents/${documentId}/artifacts`);
  },

  async createArtifact(documentId: string, payload: {
    artifact_type: string;
    filename: string;
    mime_type: string;
    content_text?: string;
  }) {
    return fetchApi<DocumentArtifact>(`/api/v1/documents/${documentId}/artifacts`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

export const assistantApi = {
  async getCapabilities(): Promise<ApiResponse<AssistantCapabilities>> {
    return fetchApi<AssistantCapabilities>("/api/v1/assistant/capabilities");
  },

  async getPreferences(): Promise<ApiResponse<AssistantPreference>> {
    return fetchApi<AssistantPreference>("/api/v1/assistant/preferences");
  },

  async updatePreferences(pref: AssistantPreference): Promise<ApiResponse<AssistantPreference>> {
    return fetchApi<AssistantPreference>("/api/v1/assistant/preferences", {
      method: "PUT",
      body: JSON.stringify(pref),
    });
  },

  async sendMessage(req: AssistantMessageRequest): Promise<ApiResponse<AssistantMessageResponse>> {
    return fetchApi<AssistantMessageResponse>("/api/v1/assistant/message", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  async executeTool(req: AssistantToolExecuteRequest): Promise<ApiResponse<AssistantToolExecuteResponse>> {
    return fetchApi<AssistantToolExecuteResponse>("/api/v1/assistant/tools/execute", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },
};

export const verificationApi = {
  async verifyCase(caseId: string, options?: { force_reverify?: boolean; include_ai_checks?: boolean }): Promise<ApiResponse<VerificationRun>> {
    return fetchApi<VerificationRun>(`/api/v1/cases/${caseId}/verify`, {
      method: "POST",
      body: JSON.stringify({
        force_reverify: options?.force_reverify ?? false,
        include_ai_checks: options?.include_ai_checks ?? true,
      }),
    });
  },

  async getLatestVerification(caseId: string): Promise<ApiResponse<VerificationRun>> {
    return fetchApi<VerificationRun>(`/api/v1/cases/${caseId}/verification`);
  },

  async listVerificationRuns(caseId: string): Promise<ApiResponse<VerificationRun[]>> {
    return fetchApi<VerificationRun[]>(`/api/v1/cases/${caseId}/verification/runs`);
  },

  async getVerificationRun(caseId: string, runId: string): Promise<ApiResponse<VerificationRun>> {
    return fetchApi<VerificationRun>(`/api/v1/cases/${caseId}/verification/runs/${runId}`);
  },

  async listFindings(
    caseId: string,
    filters?: { run_id?: string; severity?: string; status?: string; category?: string }
  ): Promise<ApiResponse<VerificationFinding[]>> {
    const q = new URLSearchParams();
    if (filters?.run_id) q.set("run_id", filters.run_id);
    if (filters?.severity) q.set("severity", filters.severity);
    if (filters?.status) q.set("status", filters.status);
    if (filters?.category) q.set("category", filters.category);
    const qs = q.toString() ? `?${q.toString()}` : "";
    return fetchApi<VerificationFinding[]>(`/api/v1/cases/${caseId}/verification/findings${qs}`);
  },

  async resolveFinding(
    caseId: string,
    findingId: string,
    payload: { resolution_state?: string; resolution_notes: string }
  ): Promise<ApiResponse<VerificationFinding>> {
    return fetchApi<VerificationFinding>(`/api/v1/cases/${caseId}/verification/findings/${findingId}/resolve`, {
      method: "POST",
      body: JSON.stringify({
        resolution_state: payload.resolution_state || "RESOLVED_BY_HUMAN_VERIFICATION",
        resolution_notes: payload.resolution_notes,
      }),
    });
  },

  async getReviewReadiness(caseId: string): Promise<ApiResponse<ReviewReadinessSummary>> {
    return fetchApi<ReviewReadinessSummary>(`/api/v1/cases/${caseId}/review-readiness`);
  },
};

export const completionApi = {
  async startSession(caseId: string, options?: { max_turns?: number; force_new?: boolean }): Promise<ApiResponse<CompletionSession>> {
    return fetchApi<CompletionSession>(`/api/v1/cases/${caseId}/completion/start`, {
      method: "POST",
      body: JSON.stringify(options || {}),
    });
  },

  async getSession(caseId: string): Promise<ApiResponse<CompletionSession>> {
    return fetchApi<CompletionSession>(`/api/v1/cases/${caseId}/completion/session`);
  },

  async getNextQuestion(caseId: string): Promise<ApiResponse<NextQuestionResponse>> {
    return fetchApi<NextQuestionResponse>(`/api/v1/cases/${caseId}/completion/next-question`);
  },

  async submitAnswer(
    caseId: string,
    questionId: string,
    payload: { raw_answer_text: string; modality?: string; is_skipped?: boolean; structured_payload?: any }
  ): Promise<ApiResponse<SubmitAnswerResponse>> {
    return fetchApi<SubmitAnswerResponse>(`/api/v1/cases/${caseId}/completion/questions/${questionId}/answer`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async skipQuestion(
    caseId: string,
    questionId: string,
    payload?: { reason?: string }
  ): Promise<ApiResponse<SubmitAnswerResponse>> {
    return fetchApi<SubmitAnswerResponse>(`/api/v1/cases/${caseId}/completion/questions/${questionId}/skip`, {
      method: "POST",
      body: JSON.stringify(payload || {}),
    });
  },

  async completeSession(
    caseId: string,
    payload?: { reason?: string }
  ): Promise<ApiResponse<CompletionSession>> {
    return fetchApi<CompletionSession>(`/api/v1/cases/${caseId}/completion/complete`, {
      method: "POST",
      body: JSON.stringify(payload || {}),
    });
  },
};

