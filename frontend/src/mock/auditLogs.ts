import type { AuditLogEntry } from "@/types";

/**
 * Immutable Audit Trail Ledger Mock Fixture.
 * Demonstrates tamper-evident tracking of human decisions,
 * provenance changes, parameter verification, and zero-PII logging.
 */

export const MOCK_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 101,
    actor_id: "usr-doc-01",
    actor_role: "CLINICIAN",
    action: "VERIFY_EVIDENCE",
    entity_type: "EVIDENCE_RECORD",
    entity_id: "ev-003-1",
    provenance_type: "CLINICIAN_VERIFIED",
    details: {
      case_id: "CASE-SYNTH-003",
      claim: "Pain started while climbing stairs",
      status: "CONFIRMED",
      rationale: "Corroborated during bedside clinical interview",
    },
    timestamp: "2026-10-08T14:44:00Z",
  },
  {
    id: 102,
    actor_id: "usr-nurse-02",
    actor_role: "NURSE",
    action: "LOG_VITALS",
    entity_type: "VITAL_SIGN",
    entity_id: "v-003-1",
    provenance_type: "STAFF_ENTERED",
    details: {
      case_id: "CASE-SYNTH-003",
      hr: 114,
      sbp: 88,
      dbp: 54,
      spo2: 91,
      alert_generated: "SHOCK_INDEX_ELEVATED",
    },
    timestamp: "2026-10-08T14:41:00Z",
  },
  {
    id: 103,
    actor_id: "usr-doc-01",
    actor_role: "CLINICIAN",
    action: "RESOLVE_CONFLICT",
    entity_type: "CONFLICT_RECORD",
    entity_id: "conf-bp-003",
    provenance_type: "CLINICIAN_VERIFIED",
    details: {
      case_id: "CASE-SYNTH-003",
      parameter: "blood_pressure",
      resolved_value: "88/54 mmHg",
      override_reason: "Manual hospital mercury sphygmomanometer reading confirms hypotension",
    },
    timestamp: "2026-10-08T14:46:00Z",
  },
  {
    id: 104,
    actor_id: "system-engine",
    actor_role: "ADMIN",
    action: "ORCHESTRATION_EVALUATION_GENERATED",
    entity_type: "ORCHESTRATION",
    entity_id: "orch-eval-003",
    provenance_type: "SYSTEM_DERIVED",
    details: {
      case_id: "CASE-SYNTH-003",
      recommended_action: "ESCALATE",
      primary_pathway: "Cath Lab PCI / Immediate Thrombolysis",
      uncertainty_score: 0.35,
    },
    timestamp: "2026-10-08T14:43:00Z",
  },
  {
    id: 105,
    actor_id: "usr-doc-01",
    actor_role: "CLINICIAN",
    action: "CLINICIAN_OVERRIDE_PATHWAY",
    entity_type: "CARE_PATHWAY",
    entity_id: "path-003",
    provenance_type: "CLINICIAN_VERIFIED",
    details: {
      case_id: "CASE-SYNTH-003",
      selected_action: "ESCALATE",
      destination_facility: "FAC-MCH-02",
      clinical_rationale: "Approved transfer to SCB MCH for primary PCI while initiating DAPT load",
    },
    timestamp: "2026-10-08T14:48:00Z",
  },
];
