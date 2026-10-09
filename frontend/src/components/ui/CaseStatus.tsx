import React from "react";
import { FsmStatus, AcuityTier } from "@/types";
import { StatusBadge } from "./StatusBadge";
import { PriorityBadge } from "./PriorityBadge";
import { AlertOctagon, Activity } from "lucide-react";

interface CaseStatusProps {
  status: FsmStatus;
  acuityTier?: AcuityTier;
  emergencyActive?: boolean;
  caseId?: string;
  facilityName?: string;
  updatedAt?: string;
  variant?: "compact" | "card";
}

const STATUS_DESCRIPTIONS: Record<FsmStatus, string> = {
  NEW: "Case initial registration received. Awaiting intake assignment.",
  INTAKE: "Patient completing multimodal digital symptom registration.",
  PROCESSING: "Extracting clinical observations and structuring parameters.",
  REVIEW_REQUIRED: "Awaiting attending clinician verification and sign-off.",
  TRIAGED: "Nursing triage complete. Case assigned to physician queue.",
  CLINICIAN_REVIEW: "Attending clinician reviewing evidence and care pathway.",
  DECISION: "Clinician decision recorded in immutable audit log.",
  CONTINUE: "Proceeding with primary care pathway management.",
  OBSERVE: "Serial observation and monitored follow-up active.",
  ESCALATE: "High-priority resuscitation or specialty transfer initiated.",
  REFER: "Inter-facility transfer and SBAR handoff dispatched.",
  TRANSFER_PENDING: "Awaiting destination facility bed acceptance confirmation.",
  TRANSFER: "Patient in active transit with synchronized telemetry.",
  COMPLETED: "Clinical encounter concluded and signed off by physician.",
  OUTCOME: "Longitudinal care outcome and quality metrics logged.",
  PROCESSING_FAILED: "Telemetry ingestion encountered a recoverable issue.",
  OCR_FAILED: "Document OCR text extraction failed; manual entry required.",
  INSUFFICIENT_DATA: "Critical observations missing; adaptive inquiry triggered.",
  CONFLICTING_DATA: "Contradicting observations detected across data sources.",
  REFERRAL_FAILED: "Destination facility unavailable; re-routing required.",
  INTAKE_RECORDED: "Multimodal intake recorded. Awaiting triage assignment.",
  TRIAGE_PENDING: "Pending nurse triage assessment.",
  TRIAGE_IN_PROGRESS: "Active nurse triage evaluation in progress.",
  PENDING_INFORMATION: "Awaiting requested clinical information from patient or staff.",
  CLINICIAN_REVIEW_REQUIRED: "Awaiting qualified clinician review and decision.",
  REVIEW_IN_PROGRESS: "Active physician review in progress at Doctor Workbench.",
  DISPOSITION_PENDING: "Clinical decision recorded. Awaiting final disposition or closure.",
  CLOSED: "Encounter concluded and case closed.",
};

export const CaseStatus: React.FC<CaseStatusProps> = ({
  status,
  acuityTier,
  emergencyActive = false,
  caseId,
  facilityName,
  updatedAt,
  variant = "compact",
}) => {
  const description = STATUS_DESCRIPTIONS[status] || "Status monitoring active.";

  if (variant === "compact") {
    return (
      <div style={{ display: "inline-flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <StatusBadge status={status} />
        {acuityTier && <PriorityBadge tier={acuityTier} />}
        {emergencyActive && (
          <span
            className="clinova-badge"
            style={{
              backgroundColor: "var(--clinova-emergency-bg)",
              color: "var(--clinova-emergency-text)",
              borderColor: "var(--clinova-emergency-border)",
            }}
          >
            <AlertOctagon style={{ width: 10, height: 10 }} aria-hidden="true" />
            <span>EMERGENCY</span>
          </span>
        )}
      </div>
    );
  }

  return (
    <div
      className="clinova-card"
      style={{
        borderLeft: emergencyActive
          ? "5px solid var(--clinova-emergency)"
          : acuityTier === "CRITICAL"
          ? "5px solid var(--clinova-danger)"
          : "5px solid var(--clinova-accent)",
        backgroundColor: emergencyActive ? "var(--clinova-emergency-bg)" : "var(--clinova-surface)",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Activity style={{ width: 16, height: 16, color: "var(--clinova-accent)" }} aria-hidden="true" />
          {caseId && (
            <span className="clinova-mono" style={{ fontSize: "0.875rem", fontWeight: 700 }}>
              {caseId}
            </span>
          )}
          <StatusBadge status={status} />
          {acuityTier && <PriorityBadge tier={acuityTier} />}
        </div>
        {updatedAt && (
          <span className="clinova-metadata" style={{ fontSize: "0.75rem" }}>
            Updated: {updatedAt}
          </span>
        )}
      </div>

      <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", margin: 0 }}>
        {description}
      </p>

      {facilityName && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
          Managing Facility: <strong>{facilityName}</strong>
        </span>
      )}
    </div>
  );
};
