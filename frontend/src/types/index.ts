/**
 * CLINOVA AI — Core Frontend Type Definitions & Clinical Domain Model.
 * Architecture: Continuous Care Intelligence
 * Non-diagnostic, advisory, human-in-the-loop clinical decision support.
 */

export type ClinicalRole =
  | "CLINICIAN"
  | "NURSE"
  | "RECEPTIONIST"
  | "PATIENT"
  | "REFERRAL_COORDINATOR"
  | "FACILITY_ADMIN"
  | "AUDITOR"
  | "SYSTEM_ADMIN"
  | "ADMIN"
  | "REVIEWER";

export type AcuityTier = "ROUTINE" | "MODERATE" | "URGENT" | "CRITICAL";

export type ConnectionState =
  | "ONLINE"
  | "OFFLINE"
  | "SYNCING"
  | "SYNCED"
  | "SYNC_ERROR"
  | "STALE_DATA";

export type FsmStatus =
  | "NEW"
  | "INTAKE"
  | "PROCESSING"
  | "REVIEW_REQUIRED"
  | "TRIAGED"
  | "CLINICIAN_REVIEW"
  | "DECISION"
  | "CONTINUE"
  | "OBSERVE"
  | "ESCALATE"
  | "REFER"
  | "TRANSFER_PENDING"
  | "TRANSFER"
  | "COMPLETED"
  | "OUTCOME"
  | "INTAKE_RECORDED"
  | "TRIAGE_PENDING"
  | "TRIAGE_IN_PROGRESS"
  | "PENDING_INFORMATION"
  | "CLINICIAN_REVIEW_REQUIRED"
  | "REVIEW_IN_PROGRESS"
  | "DISPOSITION_PENDING"
  | "CLOSED"
  | "PROCESSING_FAILED"
  | "OCR_FAILED"
  | "INSUFFICIENT_DATA"
  | "CONFLICTING_DATA"
  | "REFERRAL_FAILED";

export type AdvisoryAction =
  | "ASK"
  | "VERIFY"
  | "CONTINUE"
  | "OBSERVE"
  | "ESCALATE"
  | "REFER";

export type HumanDecisionAction =
  | "VERIFY"
  | "REJECT"
  | "MODIFY"
  | "RESOLVE_CONFLICT"
  | "REQUEST_INFO"
  | "CONTINUE"
  | "OBSERVE"
  | "ESCALATE"
  | "REFER";

export type ProvenanceType =
  | "PATIENT_REPORTED"
  | "VOICE_TRANSCRIBED"
  | "OCR_EXTRACTED"
  | "CLINICIAN_VERIFIED"
  | "STAFF_ENTERED"
  | "AI_INFERRED"
  | "SYSTEM_DERIVED"
  | "EXTERNAL_RECORD";

export type EpistemicStatus =
  | "KNOWN"
  | "UNKNOWN"
  | "CONFLICTING"
  | "UNRELIABLE"
  | "VERIFIED"
  | "INFERRED"
  | "REJECTED"
  | "SUPERSEDED";

export type VerificationStatus =
  | "UNVERIFIED"
  | "CONFIRMED"
  | "MODIFIED"
  | "DISPUTED";

export interface Persona {
  id: string;
  username?: string;
  full_name: string;
  email: string;
  role: ClinicalRole;
  facility_id?: string;
  facility_name?: string;
}

export interface VitalSign {
  id?: string;
  heart_rate?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  spo2_percent?: number;
  respiratory_rate?: number;
  temperature_celsius?: number;
  avpu_score?: "A" | "V" | "P" | "U";
  recorded_at?: string;
  provenance?: ProvenanceType;
  epistemic_status?: EpistemicStatus;
}

export interface EvidenceRecord {
  id: string;
  provenance_type: ProvenanceType;
  epistemic_status: EpistemicStatus;
  source_filename?: string;
  extracted_payload: Record<string, string | number | boolean | null>;
  confidence_score: number;
  verification_status: VerificationStatus;
  verified_by?: string;
  verified_at?: string;
  claim_text: string;
}

export interface TimelineEventItem {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  provenance: ProvenanceType;
  epistemic_status: EpistemicStatus;
  evidence_id?: string;
  is_red_flag?: boolean;
}

export interface UncertaintyItem {
  parameter: string;
  status: EpistemicStatus;
  explanation: string;
  impact_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  suggested_question?: string;
}

export interface ConflictItem {
  parameter: string;
  source_a: { source: string; value: string; id?: string };
  source_b: { source: string; value: string; id?: string };
  resolution_status: "UNRESOLVED" | "RESOLVED";
  clinical_risk: string;
}

export interface RedFlagAlert {
  id: string;
  flag_name: string;
  severity: "CRITICAL" | "HIGH";
  detected_at: string;
  source_evidence: string;
  requires_immediate_resuscitation: boolean;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, string | number | boolean | null>;
  provenance: ProvenanceType;
  status: VerificationStatus;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
}

export interface CareGraphData {
  case: {
    id: string;
    case_number: string;
    patient_synthetic_id: string;
    age_bracket: string;
    biological_sex: string;
    status: FsmStatus;
    acuity_tier: AcuityTier;
    risk_score: number;
    uncertainty_score: number;
    trajectory_slope: number;
    presenting_complaint: string;
    primary_syndrome?: string;
    required_bundle?: string;
    emergency_active?: boolean;
  };
  trajectory: {
    slope: number;
    trend: "STABLE" | "IMPROVING" | "DETERIORATING" | "CRITICAL";
    readings_count: number;
  };
  uncertainty: {
    uncertainty_score: number;
    protocol_completeness: number;
    evidence_quality: number;
    clinician_verification_ratio: number;
    missing_parameters: string[];
    follow_up_questions: Array<{ parameter: string; question: string; priority: number }>;
    conflicts: ConflictItem[];
    uncertainty_items: UncertaintyItem[];
  };
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    total_nodes: number;
    total_edges: number;
  };
  evidence_records: EvidenceRecord[];
  vitals_history: VitalSign[];
  red_flags: RedFlagAlert[];
  timeline: TimelineEventItem[];
}

export interface QueueItem {
  case_id: string;
  case_number: string;
  patient_synthetic_id: string;
  age_bracket: string;
  biological_sex: string;
  facility_name: string;
  status: FsmStatus;
  current_state?: string;
  facility_id?: string;
  pathway?: string;
  acuity_tier: AcuityTier;
  risk_score: number;
  trajectory_slope: number;
  uncertainty_score: number;
  epistemic_status: EpistemicStatus;
  presenting_complaint: string;
  primary_syndrome?: string;
  required_bundle?: string;
  waiting_minutes: number;
  sla_limit_minutes: number;
  sla_breached: boolean;
  emergency_active?: boolean;
  red_flags_count: number;
  missing_vitals_count: number;
  next_recommended_action: AdvisoryAction;
  provenance_type: ProvenanceType;
  latest_vitals?: {
    hr?: number;
    bp?: string;
    spo2?: number;
    temp?: number;
  };
  priority_tier?: string;
  vitals_overall_status?: "AVAILABLE" | "STALE" | "MISSING" | string;
  missing_critical_vitals?: string[];
  has_critical_red_flags?: boolean;
  critical_red_flags_count?: number;
  created_at: string;
}

export interface FacilityCapability {
  capability_code: string;
  label: string;
  is_operational: boolean;
  maintenance_note?: string;
  last_verified?: string;
}

export interface Facility {
  id: string;
  facility_code: string;
  name: string;
  tier: "PHC" | "CHC" | "SDH" | "DHH" | "MCH";
  location_name: string;
  latitude: number;
  longitude: number;
  icu_beds_total: number;
  icu_beds_available: number;
  general_beds_total: number;
  general_beds_available: number;
  oxygen_points_available: number;
  ed_waiting_cases: number;
  ed_avg_wait_min: number;
  capabilities: FacilityCapability[];
  freshness_minutes: number;
}

export interface FeasibilityResult {
  status: "FEASIBLE" | "DEGRADED" | "INFEASIBLE";
  reason: string;
  missing_capabilities: string[];
  critical_bed_type?: string;
  available_beds: number;
}

export interface ReferralOption {
  facility_id: string;
  facility_name: string;
  tier: string;
  location_name: string;
  feasibility_status: "FEASIBLE" | "DEGRADED" | "INFEASIBLE";
  feasibility_reason: string;
  missing_capabilities: string[];
  available_beds: number;
  distance_km: number;
  transit_minutes: number;
  ed_avg_wait_min: number;
  suitability_score: number;
}

export interface OrchestrationEvaluation {
  case_id: string;
  facility_id: string;
  facility_name: string;
  recommended_action: AdvisoryAction;
  priority_level: string;
  clinical_rationale: string;
  clinical_directive: string;
  secondary_pathway: string;
  inputs_considered: {
    risk_score: number;
    acuity_tier: string;
    trajectory_slope: number;
    uncertainty_score: number;
    feasibility_status: string;
    conflicts_count: number;
    missing_parameters_count: number;
  };
  advisory_disclaimer: string;
  evidence_provenance: string[];
  epistemic_gaps: string[];
}

export interface AuditLogEntry {
  id: number;
  actor_id: string;
  actor_role: ClinicalRole;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, string | number | boolean | null>;
  timestamp: string;
  provenance_type: ProvenanceType;
}

export interface SbarPacket {
  sbar_situation: string;
  sbar_background: string;
  sbar_assessment: string;
  sbar_recommendation: string;
  required_bundle: string;
  origin_facility_name: string;
  destination_facility_name: string;
  estimated_transit_minutes: number;
  acuity_tier: AcuityTier;
  vital_summary: string;
}

export interface SyndromicCluster {
  syndrome: string;
  observed_cases_48h: number;
  baseline_mean: number;
  z_score: number;
  status: "SURGE_ALERT" | "ELEVATED_CLUSTER" | "NORMAL_BASELINE";
  alert_class: "CRITICAL" | "WARNING" | "NORMAL";
}

export interface SignalSummary {
  mode: string;
  active_events_logged: number;
  overall_epidemiological_alert: string;
  network_icu_occupancy_pct: number;
  total_ed_waiting: number;
  active_clusters: SyndromicCluster[];
}

export interface PatientIntakeSubmission {
  facility_id: string;
  pathway: "OPD_GENERAL" | "EMERGENCY" | "MATERNAL_CHILD" | "CHRONIC_CARE";
  reported_age_bracket: string;
  biological_sex: "MALE" | "FEMALE" | "OTHER";
  preferred_language: "en" | "hi" | "or";
  chief_complaint: string;
  symptom_duration: string;
  narrative_notes?: string;
  voice_transcript?: string;
  document_uploaded?: boolean;
  document_type?: string;
  vitals?: Partial<VitalSign>;
  consent_confirmed: boolean;
  consent_status?: "GRANTED" | "REVOKED" | "IMPLIED_EMERGENCY";
  client_submission_id?: string;
}

// ---------------------------------------------------------------------------
// Phase 16: Deterministic Triage & Queue Types
// ---------------------------------------------------------------------------

export interface NEWS2Result {
  score: number | null;
  is_complete: boolean;
  risk_level: string | null;
  component_scores: Record<string, number | null>;
  missing_components: string[];
  version: string;
  calculated_at: string;
  limitation: string | null;
}

export interface ShockIndexResult {
  score: number | null;
  is_complete: boolean;
  interpretation: string | null;
  missing_components: string[];
  version: string;
  calculated_at: string;
  error: string | null;
}

export interface RedFlagResult {
  rule_id: string;
  rule_version: string;
  name: string;
  severity: "CRITICAL" | "URGENT" | "WARNING";
  triggered: boolean;
  explanation: string;
  observed_inputs: Record<string, unknown>;
  vital_references: string[];
  timestamp: string;
}

export interface TriageSnapshot {
  case_id: string;
  vital_id?: string | null;
  pathway: string;
  current_state: string;
  vitals_summary: Record<string, unknown>;
  vitals_freshness: Record<string, "AVAILABLE" | "STALE" | "MISSING">;
  vitals_overall_status: "AVAILABLE" | "STALE" | "MISSING";
  vital_age_minutes: number | null;
  news2: NEWS2Result;
  shock_index: ShockIndexResult;
  red_flags: RedFlagResult[];
  has_critical_red_flags: boolean;
  uncertainty_score: number;
  uncertainty_level: string;
  missing_critical_vitals: string[];
  data_completeness_ratio: number;
  priority_tier: "P1_CRITICAL" | "P2_URGENT" | "P3_MODERATE" | "P4_ROUTINE" | string;
  acuity_tier: AcuityTier;
  risk_score: number;
  priority_reasons: string[];
  ruleset_version: string;
  calculated_at: string;
}

export interface VitalLatestRead {
  vital?: VitalSign | null;
  freshness_by_parameter: Record<string, string>;
  overall_status: "AVAILABLE" | "STALE" | "MISSING";
  age_minutes?: number | null;
  recorded_at?: string | null;
}

export interface CasePriority {
  case_id: string;
  priority_tier: string;
  acuity_tier: string;
  risk_score: number;
  uncertainty_score: number;
  pathway: string;
  has_critical_red_flags: boolean;
  triggering_rules: string[];
  priority_reasons: string[];
  physiological_indicators?: Record<string, unknown>;
  missing_critical_vitals: string[];
  ruleset_version: string;
  calculated_at: string;
}

export interface ReviewQueueItem extends QueueItem {
  review_status: "PENDING_REVIEW" | "IN_REVIEW" | "AWAITING_DECISION" | "AWAITING_DISPOSITION" | string;
  assigned_clinician_id?: string | null;
}

export interface ReviewQueueData {
  total_cases: number;
  emergency_count: number;
  critical_count: number;
  urgent_count: number;
  moderate_count: number;
  routine_count: number;
  queue: ReviewQueueItem[];
  is_synthetic_mode: boolean;
  generated_at: string;
}

export interface CaseReviewContext {
  case: Record<string, unknown>;
  patient: Record<string, unknown>;
  system_deterministic_support: {
    is_system_determined: boolean;
    is_authoritative_clinical_decision: boolean;
    mandate: string;
    disclaimer: string;
    acuity_tier: string;
    priority_tier: string;
    risk_score: number;
    uncertainty_score: number;
    news2?: Record<string, unknown>;
    shock_index?: Record<string, unknown>;
    red_flags?: Array<Record<string, unknown>>;
    has_critical_red_flags?: boolean;
    priority_reasons?: string[];
    missing_critical_vitals?: string[];
    vitals_overall_status?: string;
    ruleset_version?: string;
    calculated_at?: string;
  };
  evidence: Array<Record<string, unknown>>;
  conflicts: Array<Record<string, unknown>>;
  vitals_history: Array<Record<string, unknown>>;
  timeline: Array<Record<string, unknown>>;
  follow_ups: Array<Record<string, unknown>>;
  triage_notes: Array<Record<string, unknown>>;
  prior_review_actions: Array<Record<string, unknown>>;
  prior_decisions: Array<Record<string, unknown>>;
  state_transitions: Array<Record<string, unknown>>;
  ai_advisory_results?: AIResultRecord[];
  is_synthetic_mode: boolean;
}

export interface CaseReviewHistory {
  case_id: string;
  case_number: string;
  current_state: string;
  state_version: number;
  review_actions: Array<Record<string, unknown>>;
  decisions: Array<Record<string, unknown>>;
  transitions: Array<Record<string, unknown>>;
  audit_events: Array<Record<string, unknown>>;
}

export type AITaskId =
  | "CASE_SUMMARY_V1"
  | "TIMELINE_SUMMARY_V1"
  | "MISSING_INFORMATION_V1"
  | "FOLLOWUP_QUESTION_V1"
  | "TRIAGE_NOTE_DRAFT_V1"
  | string;

export interface AIResultRecord {
  id: string;
  case_id: string;
  task_id: string;
  task_version: string;
  model_id: string;
  model_version: string;
  prompt_id: string;
  prompt_version: string;
  status: "SUCCESS" | "SUCCESS_CACHED" | "REJECTED" | "FALLBACK" | "FAILED" | string;
  validation_state: string;
  epistemic_state: "AI_INFERRED" | string;
  is_stale: boolean;
  is_cached: boolean;
  is_advisory_only: boolean;
  disclaimer: string;
  generated_at: string | null;
  context_fingerprint: string;
  case_version: number;
  source_evidence_references: string[];
  payload: Record<string, unknown>;
  errors: string[];
  warnings: string[];
  confidence?: number | null;
  deterministic_safety_summary?: {
    acuity_tier?: string;
    priority_tier?: string;
    news2_score?: number | null;
    shock_index?: number | null;
    has_critical_red_flags?: boolean;
  };
  correlation_id?: string | null;
}

export interface CaseSummaryPayload {
  case_id: string;
  clinical_summary: string;
  key_findings: string[];
  source_evidence_ids: string[];
  advisory_notice: string;
}

export interface TimelineSummaryPayload {
  case_id: string;
  chronological_narrative: string;
  milestones: Array<{
    timestamp?: string;
    event: string;
    evidence_id?: string;
  }>;
  progression_assessment: string;
}

export interface MissingInformationPayload {
  case_id: string;
  missing_parameters: Array<{
    parameter_name: string;
    clinical_rationale: string;
    impact_level: string;
    suggested_inquiry?: string;
  }>;
  overall_data_completeness: string;
}

export interface CandidateQuestion {
  question_text: string;
  clinical_target: string;
  priority: "CRITICAL" | "IMPORTANT" | "OPTIONAL" | string;
  source_gap_parameter: string;
}

export interface FollowUpQuestionsPayload {
  case_id: string;
  questions: CandidateQuestion[];
}

export interface DraftTriageNotePayload {
  case_id: string;
  subjective_summary: string;
  objective_summary: string;
  assessment_synthesis: string;
  suggested_next_steps: string[];
  is_ai_draft: boolean;
}


// ===========================================================================
// Phase 21: Translation & Multilingual Workflow Types
// Strict Invariants: Original is authoritative, translation is derived representation
// ===========================================================================

export interface TranslationRecordItem {
  id: string;
  case_id: string;
  entity_type: string;
  entity_id: string;
  source_language: string;
  target_language: string;
  source_text: string;
  translated_text: string;
  translation_status: 'COMPLETE' | 'LOW_CONFIDENCE' | 'REQUIRES_REVIEW' | 'FAILED' | string;
  review_status: 'PENDING' | 'VERIFIED' | 'CORRECTED' | 'REJECTED' | string;
  provider: string;
  model_version: string;
  is_active: boolean;
  corrected_text?: string | null;
}
