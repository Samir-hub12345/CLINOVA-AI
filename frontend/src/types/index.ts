/**
 * CLINOVA AI — Core Frontend Type Definitions.
 * Architecture: Continuous Care Intelligence
 * Non-diagnostic, advisory, human-in-the-loop clinical decision support.
 */

export type ClinicalRole = "CLINICIAN" | "NURSE" | "ADMIN" | "REVIEWER";

export type AcuityTier = "ROUTINE" | "MODERATE" | "URGENT" | "CRITICAL";

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
  | "PROCESSING_FAILED"
  | "OCR_FAILED"
  | "INSUFFICIENT_DATA"
  | "CONFLICTING_DATA"
  | "REFERRAL_FAILED";

export type AdvisoryAction = "ASK" | "VERIFY" | "CONTINUE" | "OBSERVE" | "ESCALATE" | "REFER";

export type ProvenanceType =
  | "PATIENT_REPORTED"
  | "VOICE_TRANSCRIBED"
  | "OCR_EXTRACTED"
  | "CLINICIAN_VERIFIED"
  | "AI_INFERRED"
  | "SYSTEM_DERIVED";

export type VerificationStatus = "UNVERIFIED" | "CONFIRMED" | "MODIFIED" | "DISPUTED";

export interface Persona {
  id: string;
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
  avpu_score?: string;
  recorded_at?: string;
}

export interface EvidenceRecord {
  id: string;
  provenance_type: ProvenanceType;
  source_filename?: string;
  extracted_payload: Record<string, any>;
  confidence_score: number;
  verification_status: VerificationStatus;
  verified_by?: string;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, any>;
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
  };
  trajectory: {
    slope: number;
    trend: string;
    readings_count: number;
  };
  uncertainty: {
    uncertainty_score: number;
    protocol_completeness: number;
    evidence_quality: number;
    clinician_verification_ratio: number;
    missing_parameters: string[];
    follow_up_questions: Array<{ parameter: string; question: string }>;
    conflicts: Array<{ type: string; message: string }>;
  };
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    total_nodes: number;
    total_edges: number;
  };
  evidence_records: EvidenceRecord[];
  vitals_history: VitalSign[];
}

export interface QueueItem {
  case_id: string;
  case_number: string;
  patient_synthetic_id: string;
  age_bracket: string;
  biological_sex: string;
  facility_name: string;
  status: FsmStatus;
  acuity_tier: AcuityTier;
  risk_score: number;
  trajectory_slope: number;
  uncertainty_score: number;
  presenting_complaint: string;
  primary_syndrome?: string;
  required_bundle?: string;
  waiting_minutes: number;
  sla_limit_minutes: number;
  sla_breached: boolean;
  latest_vitals?: {
    hr?: number;
    bp?: string;
    spo2?: number;
    temp?: number;
  };
  created_at: string;
}

export interface Facility {
  id: string;
  facility_code: string;
  name: string;
  tier: string;
  latitude: number;
  longitude: number;
  icu_beds_total: number;
  icu_beds_available: number;
  general_beds_total: number;
  general_beds_available: number;
  ed_waiting_cases: number;
  ed_avg_wait_min: number;
  capabilities: Array<{
    capability_code: string;
    is_operational: boolean;
    maintenance_note?: string;
  }>;
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

export interface AuditLogEntry {
  id: number;
  actor_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, any>;
  ip_address?: string;
  timestamp: string;
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
}
