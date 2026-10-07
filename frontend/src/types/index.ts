export type UserRole = "admin" | "doctor" | "nurse" | "patient" | "staff";

export interface PatientCase {
  id: string;
  synthetic_case_id: string;
  language: string;
  facility_type: string;
  visit_type: string;
  status: CaseStatus;
  raw_symptoms: string | null;
  report_filename: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export type CaseReceipt = Pick<PatientCase, "id" | "synthetic_case_id" | "language" | "facility_type" | "visit_type" | "status">;

export interface PatientConsultation {
  id: string;
  scheduled_at: string;
  chief_complaint: string;
  status: ConsultationStatus;
  doctor_name: string;
  summary: string | null;
}

export interface PortalProfileInput {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  emergency_contact: string;
}

export interface AdminOverview {
  users: number;
  patients: number;
  consultations: number;
  cases: number;
  awaiting_review: number;
  audit_records: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Patient {
  id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  blood_group?: string;
  phone?: string;
  email?: string;
  emergency_contact?: string;
  allergies?: string;
  current_medications?: string;
  medical_history?: string;
  created_at: string;
  updated_at: string;
  consultations?: Consultation[];
}

export type ConsultationStatus = "scheduled" | "in_progress" | "completed" | "cancelled";
export type TriageLevel = "critical" | "urgent" | "routine" | "low" | "unassigned";

export interface Consultation {
  id: string;
  patient_id: string;
  doctor_id: string;
  scheduled_at: string;
  status: ConsultationStatus;
  triage_level: TriageLevel;
  chief_complaint: string;
  vitals_data?: string;
  subjective?: string;
  objective?: string;
  assessment?: string;
  plan?: string;
  ai_generated_summary?: string;
  ai_differential_diagnosis?: string;
  created_at: string;
  updated_at: string;
  patient?: Patient;
  doctor?: User;
}

export interface VitalsInput {
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  temperature?: number;
  pain_score?: number;
}

export interface DifferentialDiagnosisItem {
  condition: string;
  probability: string; // High, Moderate, Low
  rationale: string;
  recommended_workup: string[];
}

export interface TriageResponse {
  urgency_level: "CRITICAL" | "URGENT" | "ROUTINE" | "LOW" | string;
  urgency_color: string;
  emergency_red_flags: string[];
  differential_diagnoses: DifferentialDiagnosisItem[];
  immediate_actions: string[];
  clinical_reasoning: string;
  suggested_monitoring: string[];
  disclaimer: string;
  source: string;
}

export interface SOAPGenerateResponse {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  patient_friendly_summary: string;
  disclaimer: string;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  user_email?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  details?: string;
  timestamp: string;
}

// ---------------------------------------------------------------------------
// PS03 Multimodal Triage Assistant Types
// ---------------------------------------------------------------------------
export type QueueCategory = "urgent-review" | "priority" | "routine";
export type CaseStatus =
  | "awaiting_review"
  | "ready_for_doctor"
  | "in_review"
  | "approved"
  | "rejected"
  | "referred"
  | "deleted";

export interface OCRField {
  field_name: string;
  value: string;
  unit?: string;
  confidence: number;
  bounding_box?: number[];
  verification_status: "pending" | "verified" | "rejected";
  source_reference?: string;
}

export interface ReportOCRResult {
  report_filename: string;
  fields: OCRField[];
  raw_extracted_text: string;
  confidence_average: number;
  is_synthetic_sample: boolean;
  status: string;
  disclaimer: string;
}

export interface SpeechTranscribeResult {
  transcript: string;
  detected_language: string;
  confidence: number;
  duration_seconds: number;
  is_demo_fallback: boolean;
  disclaimer: string;
}

export interface TranslationResult {
  original_text: string;
  original_language: string;
  translated_text: string;
  target_language: string;
  normalization_summary: string;
  is_demo_fallback: boolean;
}

export interface TimelineEvent {
  day: string;
  description: string;
  source?: string;
}

export interface RiskSignal {
  rule_id: string;
  signal: string;
  source_text: string;
  severity: "URGENT REVIEW" | "PRIORITY" | "ROUTINE";
  timestamp: string;
  reviewer_confirmation_required: boolean;
  status: "pending_confirmation" | "confirmed" | "dismissed";
}

export interface TriageCase {
  id: string;
  synthetic_case_id: string;
  language: string;
  facility_type: string;
  visit_type: string;
  status: CaseStatus;
  queue_category: QueueCategory;
  queue_reason?: string;
  consent_status: boolean;
  patient_id?: string;
  approximate_age?: number;
  gender?: string;
  context_notes?: string;
  vitals?: Record<string, any>;
  intake_verified?: boolean;
  assigned_doctor_id?: string;
  assigned_doctor_name?: string;
  assigned_department?: string;
  raw_symptoms?: string;
  normalized_symptoms?: string;
  speech_transcript?: string;
  detected_language?: string;
  report_filename?: string;
  report_ocr_data?: OCRField[];
  image_reference?: string;
  triage_summary?: Record<string, any>;
  missing_information?: string[];
  follow_up_questions?: string[];
  risk_signals?: RiskSignal[];
  timeline_events?: TimelineEvent[];
  reviewer_notes?: string;
  reviewer_id?: string;
  reviewer_name?: string;
  reviewed_at?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
  waiting_minutes?: number;
  is_deleted?: boolean;
  case_version?: number;
  workflow_state?: string;
  review_readiness_status?: string;
}


export interface ReferralNote {
  case_id: string;
  synthetic_case_id: string;
  facility: string;
  visit_type: string;
  patient_reported_symptoms: string;
  timeline: TimelineEvent[];
  available_report_data: OCRField[];
  reviewer_confirmed_summary: string;
  outstanding_questions: string[];
  review_signals: RiskSignal[];
  reviewer_reason: string;
  reviewer_name: string;
  reviewer_role: string;
  timestamp: string;
  footer_disclaimer: string;
}

export interface DocumentArtifact {
  id: string;
  document_id: string;
  artifact_type: string;
  filename: string;
  mime_type: string;
  file_size_bytes: number;
  checksum_sha256?: string;
  storage_key?: string;
  storage_provider?: string;
  content_text?: string;
  created_at: string;
}

export interface MedicalDocument {
  id: string;
  patient_id?: string;
  encounter_id?: string;
  consultation_id?: string;
  case_id?: string;
  facility_id?: string;
  document_type: string;
  filename: string;
  safe_filename?: string;
  mime_type: string;
  detected_mime_type?: string;
  file_size_bytes: number;
  checksum_sha256: string;
  checksum_algorithm?: string;
  storage_key: string;
  storage_provider: string;
  storage_bucket?: string;
  status: string;
  scan_status: string;
  scan_details?: string;
  quarantined_at?: string;
  version: number;
  parent_document_id?: string;
  is_current_version: boolean;
  deleted_at?: string;
  uploaded_by?: string;
  created_at: string;
  updated_at: string;
  artifacts?: DocumentArtifact[];
}

export interface PresignedUrlResponse {
  document_id: string;
  filename: string;
  access_url: string;
  expires_in_seconds: number;
  expires_at: string;
}

export interface AssistantPreference {
  assistant_enabled: boolean;
  language: string;
  voice_enabled: boolean;
  voice_response_enabled: boolean;
}

export interface SupportedLanguage {
  code: string;
  name: string;
}

export interface AssistantCapabilities {
  role: string;
  available_tools: string[];
  supported_languages: SupportedLanguage[];
  voice_input_available: boolean;
  tts_available: boolean;
  disclaimer: string;
}

export interface ProposedAction {
  tool_name: string;
  description: string;
  parameters: Record<string, any>;
  risk_level: string;
}

export interface AssistantMessageRequest {
  message: string;
  language?: string;
  context_resource_type?: string;
  context_resource_id?: string;
  voice_input?: boolean;
  history?: Array<{ role: "user" | "assistant"; content: string }>;
  voice_persona?: string;
}

export interface AssistantMessageResponse {
  text: string;
  language: string;
  original_statement?: string;
  source_label: string;
  requires_confirmation: boolean;
  proposed_action?: ProposedAction;
  structured_data?: Record<string, any>;
  follow_up_suggestions: string[];
  detected_language?: string;
}

export interface AssistantToolExecuteRequest {
  tool_name: string;
  parameters?: Record<string, any>;
  confirmed?: boolean;
}

export interface AssistantToolExecuteResponse {
  success: boolean;
  tool_name: string;
  result: any;
  message: string;
  audit_logged: boolean;
}

// Phase 4 Clinical Verification Types
export type FindingSeverity = "BLOCKING" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type FindingType = "STRUCTURAL" | "COMPLETENESS" | "CONFLICT" | "TEMPORAL" | "PROVENANCE" | "UNCERTAINTY" | "EVIDENCE_QUALITY";
export type FindingStatus = "UNRESOLVED" | "RESOLVED_BY_NEW_EVIDENCE" | "RESOLVED_BY_HUMAN_VERIFICATION" | "RESOLVED_BY_CORRECTION" | "DISMISSED_WITH_REASON";
export type ReviewReadinessStatus = "not_ready" | "partially_ready" | "review_ready_with_flags" | "review_ready";

export interface VerificationFinding {
  id: string;
  verification_run_id: string;
  case_id: string;
  case_version: number;
  finding_type: FindingType;
  category: string;
  field_name?: string | null;
  severity: FindingSeverity;
  status: FindingStatus;
  is_blocking: boolean;
  title: string;
  description: string;
  explanation: string;
  expected_information?: string | null;
  observed_information?: string | null;
  source_evidence_ids?: string[] | null;
  fact_ids?: string[] | null;
  timeline_event_ids?: string[] | null;
  rule_id: string;
  rule_version: string;
  resolved_by_user_id?: string | null;
  resolved_at?: string | null;
  resolution_notes?: string | null;
  created_at: string;
}

export interface VerificationConflict {
  id: string;
  verification_run_id: string;
  case_id: string;
  case_version: number;
  conflict_type: string;
  field_name: string;
  severity: FindingSeverity;
  source_a_evidence_id?: string | null;
  source_a_type?: string | null;
  source_a_modality?: string | null;
  source_a_value: string;
  source_a_timestamp?: string | null;
  source_b_evidence_id?: string | null;
  source_b_type?: string | null;
  source_b_modality?: string | null;
  source_b_value: string;
  source_b_timestamp?: string | null;
  resolution_state: string;
  resolution_notes?: string | null;
  resolved_by_user_id?: string | null;
  resolved_at?: string | null;
  rule_id: string;
  created_at: string;
}

export interface VerificationRun {
  id: string;
  case_id: string;
  patient_id?: string | null;
  encounter_id?: string | null;
  case_snapshot_id?: string | null;
  case_version: number;
  status: string;
  engine_version: string;
  ruleset_version: string;
  review_readiness_status: ReviewReadinessStatus;
  review_readiness_score: number;
  review_readiness_reasons: string[];
  findings_count: number;
  blocking_findings_count: number;
  high_findings_count: number;
  medium_findings_count: number;
  low_findings_count: number;
  info_findings_count: number;
  unresolved_findings_count: number;
  resolved_findings_count: number;
  structural_integrity_status: string;
  completeness_status: string;
  consistency_status: string;
  temporal_status: string;
  provenance_status: string;
  uncertainty_status: string;
  is_current: boolean;
  is_stale?: boolean;
  latency_ms: number;
  failure_reason?: string | null;
  summary?: Record<string, any> | null;
  started_at: string;
  completed_at?: string | null;
  findings?: VerificationFinding[];
  conflicts?: VerificationConflict[];
}

export interface ReviewReadinessSummary {
  case_id: string;
  case_version: number;
  verified_case_version?: number | null;
  review_readiness_status: ReviewReadinessStatus;
  review_readiness_score: number;
  review_readiness_reasons: string[];
  is_stale: boolean;
  blocking_count: number;
  unresolved_count: number;
  completeness_status: string;
  consistency_status: string;
  temporal_status: string;
  provenance_status: string;
  uncertainty_status: string;
  last_verified_at?: string | null;
}

export interface CompletionQuestion {
  id: string;
  session_id: string;
  case_id: string;
  turn_number: number;
  target_gap_id?: string | null;
  target_gap_type: string;
  target_field: string;
  question_text: string;
  question_type: 'text' | 'single_choice' | 'multi_choice' | 'numeric' | 'boolean' | 'date_time';
  options?: Array<{ label: string; value: string; description?: string }> | null;
  placeholder?: string | null;
  priority_score: number;
  clinical_rationale: string;
  status: 'candidate' | 'selected' | 'presented' | 'answered' | 'skipped' | 'superseded' | 'cancelled';
  is_safety_flag: boolean;
  created_at: string;
  presented_at?: string | null;
  answered_at?: string | null;
}

export interface CompletionAnswer {
  id: string;
  question_id: string;
  session_id: string;
  case_id: string;
  patient_id?: string | null;
  raw_answer_text: string;
  normalized_value?: string | null;
  structured_payload?: Record<string, any> | null;
  answer_modality: string;
  is_skipped: boolean;
  is_valid: boolean;
  validation_notes?: string | null;
  evidence_id?: string | null;
  answered_at: string;
}

export interface CompletionSession {
  id: string;
  case_id: string;
  patient_id?: string | null;
  encounter_id?: string | null;
  status: string;
  case_version_started: number;
  case_version_current: number;
  current_turn: number;
  max_turns: number;
  questions_asked_count: number;
  questions_answered_count: number;
  questions_skipped_count: number;
  initial_gap_count: number;
  remaining_gap_count: number;
  initial_readiness_score: number;
  current_readiness_score: number;
  stopping_reason?: string | null;
  stopping_criterion?: string | null;
  completion_summary?: Record<string, any> | null;
  engine_version: string;
  is_current: boolean;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  current_question?: CompletionQuestion | null;
  questions?: CompletionQuestion[];
}

export interface NextQuestionResponse {
  session_id: string;
  case_id: string;
  turn_number: number;
  max_turns: number;
  is_complete: boolean;
  stopping_reason?: string | null;
  stopping_criterion?: string | null;
  question?: CompletionQuestion | null;
  remaining_gaps_count: number;
  current_readiness_score: number;
}

export interface SubmitAnswerResponse {
  session_id: string;
  case_id: string;
  answer: CompletionAnswer;
  new_evidence_id?: string | null;
  new_case_version: number;
  rebuilt_snapshot_id?: string | null;
  verification_run_id?: string | null;
  new_readiness_score: number;
  readiness_improved: boolean;
  next_question?: CompletionQuestion | null;
  is_session_complete: boolean;
  stopping_reason?: string | null;
  stopping_criterion?: string | null;
}

