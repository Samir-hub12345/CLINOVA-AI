import {
  CareGraphData,
  QueueItem,
} from "@/types";

/**
 * Canonical Synthetic Clinical Cases for Phase 12 UI Foundation.
 * Strictly 100% Synthetic — Zero real patient records or PII.
 * Aligned with Phase 11 Evaluation Datasets (Groups A–T).
 */

export const MOCK_SYNTHETIC_QUEUE: QueueItem[] = [
  {
    case_id: "CASE-SYNTH-003",
    case_number: "CNV-2026-003",
    patient_synthetic_id: "PT-SYN-0842",
    age_bracket: "52-58 YRS",
    biological_sex: "MALE",
    facility_name: "Cuttack District Headquarters Hospital",
    status: "REVIEW_REQUIRED",
    acuity_tier: "CRITICAL",
    risk_score: 0.92,
    trajectory_slope: 0.38,
    uncertainty_score: 0.35,
    epistemic_status: "CONFLICTING",
    presenting_complaint: "Severe substernal crushing chest pain radiating to left jaw, diaphoresis for 45 min",
    primary_syndrome: "Acute Coronary Syndrome / STEMI Suspect",
    required_bundle: "BUNDLE_ACS_THROMBOLYSIS_PCI",
    waiting_minutes: 8,
    sla_limit_minutes: 10,
    sla_breached: false,
    emergency_active: true,
    red_flags_count: 2,
    missing_vitals_count: 0,
    next_recommended_action: "ESCALATE",
    provenance_type: "OCR_EXTRACTED",
    latest_vitals: {
      hr: 114,
      bp: "88/54",
      spo2: 91,
      temp: 36.7,
    },
    created_at: "2026-10-08T14:42:00Z",
  },
  {
    case_id: "CASE-SYNTH-004",
    case_number: "CNV-2026-004",
    patient_synthetic_id: "PT-SYN-0319",
    age_bracket: "28-34 YRS",
    biological_sex: "FEMALE",
    facility_name: "Angul Rural PHC",
    status: "TRIAGED",
    acuity_tier: "URGENT",
    risk_score: 0.68,
    trajectory_slope: 0.22,
    uncertainty_score: 0.58,
    epistemic_status: "UNKNOWN",
    presenting_complaint: "High-grade fever for 5 days with retro-orbital pain, petechial rash on shins",
    primary_syndrome: "Acute Febrile Illness / Dengue Warning Signs",
    required_bundle: "BUNDLE_DENGUE_MONITORING",
    waiting_minutes: 24,
    sla_limit_minutes: 30,
    sla_breached: false,
    emergency_active: false,
    red_flags_count: 1,
    missing_vitals_count: 1,
    next_recommended_action: "VERIFY",
    provenance_type: "PATIENT_REPORTED",
    latest_vitals: {
      hr: 98,
      bp: "102/68",
      spo2: 97,
      temp: 39.2,
    },
    created_at: "2026-10-08T14:26:00Z",
  },
  {
    case_id: "CASE-SYNTH-005",
    case_number: "CNV-2026-005",
    patient_synthetic_id: "PT-SYN-1104",
    age_bracket: "65-72 YRS",
    biological_sex: "FEMALE",
    facility_name: "Cuttack District Headquarters Hospital",
    status: "CLINICIAN_REVIEW",
    acuity_tier: "MODERATE",
    risk_score: 0.46,
    trajectory_slope: 0.14,
    uncertainty_score: 0.28,
    epistemic_status: "INFERRED",
    presenting_complaint: "Progressive breathlessness on exertion and bilateral ankle swelling for 2 weeks",
    primary_syndrome: "Congestive Cardiac Failure / Decompensation",
    required_bundle: "BUNDLE_HEART_FAILURE_STABILIZATION",
    waiting_minutes: 42,
    sla_limit_minutes: 60,
    sla_breached: false,
    emergency_active: false,
    red_flags_count: 0,
    missing_vitals_count: 0,
    next_recommended_action: "OBSERVE",
    provenance_type: "AI_INFERRED",
    latest_vitals: {
      hr: 82,
      bp: "148/92",
      spo2: 95,
      temp: 36.8,
    },
    created_at: "2026-10-08T14:08:00Z",
  },
  {
    case_id: "CASE-SYNTH-001",
    case_number: "CNV-2026-001",
    patient_synthetic_id: "PT-SYN-0014",
    age_bracket: "22-26 YRS",
    biological_sex: "FEMALE",
    facility_name: "Angul Rural PHC",
    status: "COMPLETED",
    acuity_tier: "ROUTINE",
    risk_score: 0.12,
    trajectory_slope: -0.05,
    uncertainty_score: 0.18,
    epistemic_status: "VERIFIED",
    presenting_complaint: "Mild throat irritation, rhinorrhea and occasional dry cough for 3 days",
    primary_syndrome: "Upper Respiratory Tract Infection (Viral URI)",
    required_bundle: "BUNDLE_OPD_SYMPTOMATIC",
    waiting_minutes: 62,
    sla_limit_minutes: 120,
    sla_breached: false,
    emergency_active: false,
    red_flags_count: 0,
    missing_vitals_count: 0,
    next_recommended_action: "CONTINUE",
    provenance_type: "CLINICIAN_VERIFIED",
    latest_vitals: {
      hr: 72,
      bp: "120/80",
      spo2: 99,
      temp: 36.8,
    },
    created_at: "2026-10-08T13:48:00Z",
  },
  {
    case_id: "CASE-SYNTH-006",
    case_number: "CNV-2026-006",
    patient_synthetic_id: "PT-SYN-0567",
    age_bracket: "4-6 YRS",
    biological_sex: "MALE",
    facility_name: "Choudwar Community Health Centre",
    status: "PROCESSING",
    acuity_tier: "URGENT",
    risk_score: 0.62,
    trajectory_slope: 0.19,
    uncertainty_score: 0.44,
    epistemic_status: "UNRELIABLE",
    presenting_complaint: "Watery diarrhea 6 times since morning, lethargy, sunken eyes, thirst",
    primary_syndrome: "Acute Gastroenteritis / Moderate Dehydration",
    required_bundle: "BUNDLE_PEDIATRIC_REHYDRATION",
    waiting_minutes: 18,
    sla_limit_minutes: 30,
    sla_breached: false,
    emergency_active: false,
    red_flags_count: 1,
    missing_vitals_count: 1,
    next_recommended_action: "VERIFY",
    provenance_type: "VOICE_TRANSCRIBED",
    latest_vitals: {
      hr: 128,
      bp: "90/60",
      spo2: 98,
      temp: 37.4,
    },
    created_at: "2026-10-08T14:32:00Z",
  },
];

export const MOCK_DETAILED_CASES: Record<string, CareGraphData> = {
  "CASE-SYNTH-003": {
    case: {
      id: "CASE-SYNTH-003",
      case_number: "CNV-2026-003",
      patient_synthetic_id: "PT-SYN-0842",
      age_bracket: "52-58 YRS",
      biological_sex: "MALE",
      status: "REVIEW_REQUIRED",
      acuity_tier: "CRITICAL",
      risk_score: 0.92,
      uncertainty_score: 0.35,
      trajectory_slope: 0.38,
      presenting_complaint: "Severe substernal crushing chest pain radiating to left jaw, diaphoresis for 45 min",
      primary_syndrome: "Acute Coronary Syndrome / STEMI Suspect",
      required_bundle: "BUNDLE_ACS_THROMBOLYSIS_PCI",
      emergency_active: true,
    },
    trajectory: {
      slope: 0.38,
      trend: "CRITICAL",
      readings_count: 4,
    },
    uncertainty: {
      uncertainty_score: 0.35,
      protocol_completeness: 0.82,
      evidence_quality: 0.74,
      clinician_verification_ratio: 0.4,
      missing_parameters: ["Troponin-I Quantitative", "Serum Potassium", "Baseline Creatinine"],
      follow_up_questions: [
        { parameter: "prior_cad_history", question: "Any history of stent placement, angioplasty, or bypass surgery?", priority: 1 },
        { parameter: "bleeding_risk", question: "Any active bleeding, recent major surgery, or hemorrhagic stroke history?", priority: 1 },
      ],
      conflicts: [
        {
          parameter: "blood_pressure",
          source_a: { source: "Home Automatic Cuff (Patient Reported)", value: "145/90 mmHg at 13:30" },
          source_b: { source: "Hospital Manual Triage Cuff (Staff Entered)", value: "88/54 mmHg at 14:40" },
          resolution_status: "UNRESOLVED",
          clinical_risk: "Hypotension / Cardiogenic shock emergence vs measurement artifact",
        },
      ],
      uncertainty_items: [
        {
          parameter: "Troponin-I Level",
          status: "UNKNOWN",
          explanation: "Point-of-care rapid troponin pending laboratory run; cannot confirm non-STEMI vs early STEMI without quantitative marker.",
          impact_level: "HIGH",
          suggested_question: "Expedite STAT point-of-care cardiac enzyme cassette.",
        },
        {
          parameter: "Blood Pressure Trajectory",
          status: "CONFLICTING",
          explanation: "Acute drop of 57 mmHg systolic between reported pre-arrival value and triage measurement.",
          impact_level: "CRITICAL",
          suggested_question: "Perform bilateral manual brachial repeat BP check immediately.",
        },
        {
          parameter: "Thrombolysis Contraindications",
          status: "UNKNOWN",
          explanation: "No confirmed record of intracranial pathology or gastrointestinal bleeding in the last 6 months.",
          impact_level: "HIGH",
          suggested_question: "Confirm absence of bleeding disorders with patient/attendant.",
        },
      ],
    },
    graph: {
      total_nodes: 6,
      total_edges: 5,
      nodes: [
        { id: "node-1", type: "SYMPTOM", label: "Crushing Retrosternal Chest Pain", data: { severity: "Severe 9/10", duration: "45m" }, provenance: "PATIENT_REPORTED", status: "CONFIRMED" },
        { id: "node-2", type: "VITAL", label: "Hypotension (88/54 mmHg)", data: { sbp: 88, dbp: 54 }, provenance: "STAFF_ENTERED", status: "CONFIRMED" },
        { id: "node-3", type: "INVESTIGATION", label: "ECG: 2.5mm ST Elevation in V1-V4", data: { lead_pattern: "Anterior STEMI" }, provenance: "OCR_EXTRACTED", status: "UNVERIFIED" },
        { id: "node-4", type: "SYNDROME", label: "Acute Anterior Wall STEMI", data: { icd11: "BA41" }, provenance: "AI_INFERRED", status: "UNVERIFIED" },
        { id: "node-5", type: "RISK", label: "Cardiogenic Shock Risk (Shock Index 1.30)", data: { si: 1.30 }, provenance: "SYSTEM_DERIVED", status: "CONFIRMED" },
        { id: "node-6", type: "DISPOSITION", label: "Cath Lab PCI / Immediate Thrombolysis", data: { urgency: "IMMEDIATE" }, provenance: "SYSTEM_DERIVED", status: "UNVERIFIED" },
      ],
      edges: [
        { source: "node-1", target: "node-4", relation: "INDICATES" },
        { source: "node-3", target: "node-4", relation: "CONFIRMS_PATTERN" },
        { source: "node-2", target: "node-5", relation: "PRECIPITATES" },
        { source: "node-4", target: "node-6", relation: "REQUIRES" },
        { source: "node-5", target: "node-6", relation: "ESCALATES_PRIORITY" },
      ],
    },
    evidence_records: [
      {
        id: "ev-003-1",
        provenance_type: "PATIENT_REPORTED",
        epistemic_status: "VERIFIED",
        claim_text: "Pain started while climbing stairs; accompanied by profuse sweating and nausea.",
        confidence_score: 0.95,
        verification_status: "CONFIRMED",
        verified_by: "Dr. Priya Sharma",
        verified_at: "2026-10-08T14:44:00Z",
        extracted_payload: { symptom: "chest_pain", quality: "crushing", radiation: "left_jaw", onset: "acute" },
      },
      {
        id: "ev-003-2",
        provenance_type: "OCR_EXTRACTED",
        epistemic_status: "INFERRED",
        source_filename: "ecg_triage_bay1_scan.jpg",
        claim_text: "12-Lead ECG strip demonstrates ST segment elevation >2mm in Leads V2-V4 with reciprocal depressions in III and aVF.",
        confidence_score: 0.91,
        verification_status: "UNVERIFIED",
        extracted_payload: { rhythm: "Sinus tachycardia", rate: 114, st_elevation_mm: 2.5, leads: "V1, V2, V3, V4" },
      },
      {
        id: "ev-003-3",
        provenance_type: "STAFF_ENTERED",
        epistemic_status: "VERIFIED",
        claim_text: "Bedside manual vitals: HR 114 bpm regular, BP 88/54 mmHg, SpO2 91% on room air, RR 26/min.",
        confidence_score: 1.0,
        verification_status: "CONFIRMED",
        verified_by: "Ananya Patel, RN",
        verified_at: "2026-10-08T14:41:00Z",
        extracted_payload: { hr: 114, sbp: 88, dbp: 54, spo2: 91, rr: 26 },
      },
      {
        id: "ev-003-4",
        provenance_type: "AI_INFERRED",
        epistemic_status: "INFERRED",
        claim_text: "Shock Index calculated as 1.30 (HR 114 / SBP 88). Threshold >0.9 signals impending hemodynamically significant failure.",
        confidence_score: 0.88,
        verification_status: "UNVERIFIED",
        extracted_payload: { shock_index: 1.30, reference_upper: 0.9, risk_tier: "CRITICAL" },
      },
    ],
    vitals_history: [
      { id: "v-003-1", heart_rate: 114, systolic_bp: 88, diastolic_bp: 54, spo2_percent: 91, respiratory_rate: 26, temperature_celsius: 36.7, avpu_score: "A", recorded_at: "14:41", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED" },
      { id: "v-003-2", heart_rate: 110, systolic_bp: 92, diastolic_bp: 58, spo2_percent: 94, respiratory_rate: 24, temperature_celsius: 36.7, avpu_score: "A", recorded_at: "14:50", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED" },
    ],
    red_flags: [
      {
        id: "rf-003-1",
        flag_name: "Severe Hypotension / Cardiogenic Shock Danger",
        severity: "CRITICAL",
        detected_at: "14:41",
        source_evidence: "Staff Vital Entry (BP 88/54 mmHg, Shock Index 1.30)",
        requires_immediate_resuscitation: true,
      },
      {
        id: "rf-003-2",
        flag_name: "Acute Anterior STEMI Pattern on ECG",
        severity: "CRITICAL",
        detected_at: "14:43",
        source_evidence: "OCR Extracted ECG strip (V1-V4 ST elevation)",
        requires_immediate_resuscitation: true,
      },
    ],
    timeline: [
      { id: "tl-1", timestamp: "13:30", title: "Symptom Onset", description: "Patient developed acute chest heaviness at home.", provenance: "PATIENT_REPORTED", epistemic_status: "KNOWN" },
      { id: "tl-2", timestamp: "14:38", title: "Arrival at Triage", description: "Walk-in with attendant; immediate diversion to Resuscitation Bay 1.", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED" },
      { id: "tl-3", timestamp: "14:41", title: "Triage Vitals Logged", description: "Hypotension (88/54) and tachycardia (114) documented.", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED", is_red_flag: true },
      { id: "tl-4", timestamp: "14:43", title: "12-Lead ECG Acquired & Scanned", description: "ST elevations detected; awaiting physician confirmation.", provenance: "OCR_EXTRACTED", epistemic_status: "INFERRED", is_red_flag: true },
    ],
  },

  "CASE-SYNTH-004": {
    case: {
      id: "CASE-SYNTH-004",
      case_number: "CNV-2026-004",
      patient_synthetic_id: "PT-SYN-0319",
      age_bracket: "28-34 YRS",
      biological_sex: "FEMALE",
      status: "TRIAGED",
      acuity_tier: "URGENT",
      risk_score: 0.68,
      uncertainty_score: 0.58,
      trajectory_slope: 0.22,
      presenting_complaint: "High-grade fever for 5 days with retro-orbital pain, petechial rash on shins",
      primary_syndrome: "Acute Febrile Illness / Dengue Warning Signs",
      required_bundle: "BUNDLE_DENGUE_MONITORING",
      emergency_active: false,
    },
    trajectory: {
      slope: 0.22,
      trend: "DETERIORATING",
      readings_count: 2,
    },
    uncertainty: {
      uncertainty_score: 0.58,
      protocol_completeness: 0.55,
      evidence_quality: 0.65,
      clinician_verification_ratio: 0.2,
      missing_parameters: ["Platelet Count", "Hematocrit Level", "Dengue NS1 Antigen", "Urine Output 24h"],
      follow_up_questions: [
        { parameter: "bleeding_manifestation", question: "Have you had gum bleeding, epistaxis, or black tarry stools?", priority: 1 },
        { parameter: "fluid_tolerance", question: "Are you able to keep oral liquids down without persistent vomiting?", priority: 1 },
      ],
      conflicts: [],
      uncertainty_items: [
        {
          parameter: "Platelet Count & Hematocrit",
          status: "UNKNOWN",
          explanation: "Crucial diagnostic parameter missing; cannot determine plasma leakage or severe thrombocytopenia.",
          impact_level: "HIGH",
          suggested_question: "Order immediate STAT CBC with differential.",
        },
        {
          parameter: "Serology Status",
          status: "UNKNOWN",
          explanation: "NS1 / IgM / IgG pending; clinical presentation consistent with regional syndromic surge.",
          impact_level: "MODERATE",
          suggested_question: "Send rapid combo NS1 antigen cassette.",
        },
      ],
    },
    graph: {
      total_nodes: 4,
      total_edges: 3,
      nodes: [
        { id: "node-1", type: "SYMPTOM", label: "High Fever 39.2°C (5 Days)", data: { temp: 39.2, duration: "5d" }, provenance: "PATIENT_REPORTED", status: "CONFIRMED" },
        { id: "node-2", type: "FINDING", label: "Petechial Rash", data: { location: "Bilateral shins" }, provenance: "STAFF_ENTERED", status: "CONFIRMED" },
        { id: "node-3", type: "SYNDROME", label: "Dengue with Warning Signs Suspect", data: { icd11: "1D20" }, provenance: "AI_INFERRED", status: "UNVERIFIED" },
        { id: "node-4", type: "ACTION", label: "Urgent Hematocrit & IV Hydration Protocol", data: { protocol: "NVBDCP 2024" }, provenance: "SYSTEM_DERIVED", status: "UNVERIFIED" },
      ],
      edges: [
        { source: "node-1", target: "node-3", relation: "INDICATES" },
        { source: "node-2", target: "node-3", relation: "CORROBORATES" },
        { source: "node-3", target: "node-4", relation: "RECOMMENDS" },
      ],
    },
    evidence_records: [
      {
        id: "ev-004-1",
        provenance_type: "PATIENT_REPORTED",
        epistemic_status: "KNOWN",
        claim_text: "High fever began Saturday with severe body aches and pain behind the eyes.",
        confidence_score: 0.9,
        verification_status: "CONFIRMED",
        verified_by: "Ananya Patel, RN",
        extracted_payload: { symptom: "fever", retro_orbital_pain: true, days: 5 },
      },
      {
        id: "ev-004-2",
        provenance_type: "STAFF_ENTERED",
        epistemic_status: "VERIFIED",
        claim_text: "Multiple tiny non-blanching red spots noted on lower limbs. Tourniquet test borderline positive.",
        confidence_score: 0.95,
        verification_status: "CONFIRMED",
        verified_by: "Ananya Patel, RN",
        extracted_payload: { finding: "petechiae", tourniquet_test: "positive" },
      },
    ],
    vitals_history: [
      { id: "v-004-1", heart_rate: 98, systolic_bp: 102, diastolic_bp: 68, spo2_percent: 97, respiratory_rate: 20, temperature_celsius: 39.2, avpu_score: "A", recorded_at: "14:25", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED" },
    ],
    red_flags: [
      {
        id: "rf-004-1",
        flag_name: "Spontaneous Cutaneous Petechiae with Persistent High Fever",
        severity: "HIGH",
        detected_at: "14:26",
        source_evidence: "Physical examination by RN",
        requires_immediate_resuscitation: false,
      },
    ],
    timeline: [
      { id: "tl-41", timestamp: "5 days ago", title: "Fever Onset", description: "Began with chills and generalized myalgia.", provenance: "PATIENT_REPORTED", epistemic_status: "KNOWN" },
      { id: "tl-42", timestamp: "Today 10:00", title: "Petechial Rash Observed", description: "Attendant noticed spots on shins.", provenance: "PATIENT_REPORTED", epistemic_status: "KNOWN" },
      { id: "tl-43", timestamp: "Today 14:25", title: "Triage Intake Completed", description: "Vitals documented; platelet count requested.", provenance: "STAFF_ENTERED", epistemic_status: "VERIFIED" },
    ],
  },

  "CASE-SYNTH-001": {
    case: {
      id: "CASE-SYNTH-001",
      case_number: "CNV-2026-001",
      patient_synthetic_id: "PT-SYN-0014",
      age_bracket: "22-26 YRS",
      biological_sex: "FEMALE",
      status: "COMPLETED",
      acuity_tier: "ROUTINE",
      risk_score: 0.12,
      uncertainty_score: 0.18,
      trajectory_slope: -0.05,
      presenting_complaint: "Mild throat irritation, rhinorrhea and occasional dry cough for 3 days",
      primary_syndrome: "Upper Respiratory Tract Infection (Viral URI)",
      required_bundle: "BUNDLE_OPD_SYMPTOMATIC",
      emergency_active: false,
    },
    trajectory: {
      slope: -0.05,
      trend: "STABLE",
      readings_count: 1,
    },
    uncertainty: {
      uncertainty_score: 0.18,
      protocol_completeness: 0.95,
      evidence_quality: 0.92,
      clinician_verification_ratio: 1.0,
      missing_parameters: [],
      follow_up_questions: [],
      conflicts: [],
      uncertainty_items: [],
    },
    graph: {
      total_nodes: 3,
      total_edges: 2,
      nodes: [
        { id: "n1", type: "SYMPTOM", label: "Mild Rhinorrhea / Throat Scratch", data: { duration: "3d" }, provenance: "PATIENT_REPORTED", status: "CONFIRMED" },
        { id: "n2", type: "VITAL", label: "Normal Vitals (BP 120/80, SpO2 99%)", data: { sbp: 120, dbp: 80, spo2: 99 }, provenance: "CLINICIAN_VERIFIED", status: "CONFIRMED" },
        { id: "n3", type: "SYNDROME", label: "Self-Limiting Viral URI", data: { icd11: "CA00" }, provenance: "CLINICIAN_VERIFIED", status: "CONFIRMED" },
      ],
      edges: [
        { source: "n1", target: "n3", relation: "INDICATES" },
        { source: "n2", target: "n3", relation: "SUPPORTS_BENIGN" },
      ],
    },
    evidence_records: [
      {
        id: "ev-001-1",
        provenance_type: "CLINICIAN_VERIFIED",
        epistemic_status: "VERIFIED",
        claim_text: "Clear nasal discharge, erythematous posterior oropharynx without tonsillar exudates.",
        confidence_score: 1.0,
        verification_status: "CONFIRMED",
        verified_by: "Dr. Priya Sharma",
        extracted_payload: { ent_exam: "erythematous", exudates: false },
      },
    ],
    vitals_history: [
      { id: "v-001-1", heart_rate: 72, systolic_bp: 120, diastolic_bp: 80, spo2_percent: 99, respiratory_rate: 16, temperature_celsius: 36.8, avpu_score: "A", recorded_at: "13:48", provenance: "CLINICIAN_VERIFIED", epistemic_status: "VERIFIED" },
    ],
    red_flags: [],
    timeline: [
      { id: "tl-01", timestamp: "3 days ago", title: "URI Symptoms Start", description: "Scratchy throat, sneezing.", provenance: "PATIENT_REPORTED", epistemic_status: "KNOWN" },
      { id: "tl-02", timestamp: "Today 13:48", title: "OPD Consultation & Discharge Plan", description: "Supportive care advised, hydration, warning signs explained.", provenance: "CLINICIAN_VERIFIED", epistemic_status: "VERIFIED" },
    ],
  },
};

export function getMockCase(caseId: string): CareGraphData {
  if (MOCK_DETAILED_CASES[caseId]) {
    return MOCK_DETAILED_CASES[caseId];
  }
  // Try matching by patient_synthetic_id, case_number, or id in detailed cases
  const matched = Object.values(MOCK_DETAILED_CASES).find(
    (c) =>
      c.case.patient_synthetic_id === caseId ||
      c.case.case_number === caseId ||
      c.case.id === caseId
  );
  if (matched) return matched;

  // Try matching by queue item
  const queueItem = MOCK_SYNTHETIC_QUEUE.find(
    (q) =>
      q.case_id === caseId ||
      q.patient_synthetic_id === caseId ||
      q.case_number === caseId
  );
  if (queueItem) {
    const trendValue =
      queueItem.acuity_tier === "CRITICAL"
        ? "CRITICAL"
        : queueItem.trajectory_slope > 0.2
        ? "DETERIORATING"
        : queueItem.trajectory_slope < -0.05
        ? "IMPROVING"
        : "STABLE";

    return {
      case: {
        id: queueItem.case_id,
        case_number: queueItem.case_number,
        patient_synthetic_id: queueItem.patient_synthetic_id,
        age_bracket: queueItem.age_bracket,
        biological_sex: queueItem.biological_sex,
        status: queueItem.status,
        acuity_tier: queueItem.acuity_tier,
        risk_score: queueItem.risk_score,
        uncertainty_score: queueItem.uncertainty_score,
        trajectory_slope: queueItem.trajectory_slope,
        presenting_complaint: queueItem.presenting_complaint,
        primary_syndrome: queueItem.primary_syndrome,
        required_bundle: queueItem.required_bundle,
        emergency_active: queueItem.emergency_active,
      },
      trajectory: {
        slope: queueItem.trajectory_slope,
        trend: trendValue,
        readings_count: 2,
      },
      uncertainty: {
        uncertainty_score: queueItem.uncertainty_score,
        protocol_completeness: 0.85,
        evidence_quality: 0.88,
        clinician_verification_ratio: 0.5,
        missing_parameters: [],
        follow_up_questions: [],
        conflicts: [],
        uncertainty_items: [],
      },
      graph: {
        total_nodes: 2,
        total_edges: 1,
        nodes: [
          {
            id: "n1",
            type: "SYMPTOM",
            label: queueItem.presenting_complaint,
            data: { complaint: queueItem.presenting_complaint },
            provenance: queueItem.provenance_type,
            status: "CONFIRMED",
          },
          {
            id: "n2",
            type: "SYNDROME",
            label: queueItem.primary_syndrome || "Clinical Evaluation Pending",
            data: { syndrome: queueItem.primary_syndrome || "Pending" },
            provenance: "CLINICIAN_VERIFIED",
            status: "CONFIRMED",
          },
        ],
        edges: [{ source: "n1", target: "n2", relation: "INDICATES" }],
      },
      evidence_records: [],
      vitals_history: queueItem.latest_vitals
        ? [
            {
              id: "v-q-1",
              heart_rate: queueItem.latest_vitals.hr,
              systolic_bp: parseInt(queueItem.latest_vitals.bp?.split("/")[0] || "120"),
              diastolic_bp: parseInt(queueItem.latest_vitals.bp?.split("/")[1] || "80"),
              spo2_percent: queueItem.latest_vitals.spo2,
              respiratory_rate: 18,
              temperature_celsius: queueItem.latest_vitals.temp || 37.0,
              avpu_score: "A",
              recorded_at: "Just now",
              provenance: "STAFF_ENTERED",
              epistemic_status: "VERIFIED",
            },
          ]
        : [],
      red_flags: [],
      timeline: [
        {
          id: "tl-q-1",
          timestamp: "Today",
          title: "Registration & Triage",
          description: queueItem.presenting_complaint,
          provenance: queueItem.provenance_type,
          epistemic_status: "KNOWN",
        },
      ],
    };
  }

  // Fallback to CASE-SYNTH-003 with preserved requested identifier
  const fallback = MOCK_DETAILED_CASES["CASE-SYNTH-003"];
  return {
    ...fallback,
    case: {
      ...fallback.case,
      id: caseId.startsWith("CASE-") ? caseId : fallback.case.id,
      patient_synthetic_id: caseId.startsWith("PT-") || caseId.startsWith("REC-") ? caseId : fallback.case.patient_synthetic_id,
    },
  };
}
