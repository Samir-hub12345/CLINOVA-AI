import React from "react";

import { PriorityBadge } from "./PriorityBadge";
import { StatusBadge } from "./StatusBadge";
import { AcuityTier, FsmStatus } from "@/types";

interface PatientSummaryProps {
  caseNumber: string;
  patientSyntheticId: string;
  ageBracket: string;
  biologicalSex: string;
  acuityTier: AcuityTier;
  status: FsmStatus;
  primarySyndrome?: string;
  presentingComplaint: string;
  emergencyActive?: boolean;
}

export const PatientSummary: React.FC<PatientSummaryProps> = ({
  caseNumber,
  patientSyntheticId,
  ageBracket,
  biologicalSex,
  acuityTier,
  status,
  primarySyndrome,
  presentingComplaint,
  emergencyActive = false,
}) => {
  return (
    <div
      className="clinova-card"
      style={{
        borderLeft: emergencyActive
          ? "6px solid var(--clinova-emergency)"
          : "6px solid var(--clinova-accent)",
        backgroundColor: emergencyActive ? "var(--clinova-emergency-bg)" : "var(--clinova-surface)",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span className="clinova-mono" style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--clinova-text-primary)" }}>
              {patientSyntheticId}
            </span>
            <span className="clinova-metadata" style={{ fontSize: "0.75rem" }}>
              ({caseNumber})
            </span>
            <span className="clinova-badge" style={{ backgroundColor: "#f1f5f9", color: "#334155", borderColor: "#cbd5e1" }}>
              {ageBracket} • {biologicalSex}
            </span>
          </div>

          <h3 style={{ fontSize: "1.0625rem", marginTop: 4, color: "var(--clinova-text-primary)" }}>
            {primarySyndrome || "Syndromic Evaluation Pending"}
          </h3>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", marginTop: 2 }}>
            <strong>Chief Complaint:</strong> {presentingComplaint}
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <PriorityBadge tier={acuityTier} />
          <StatusBadge status={status} />
        </div>
      </div>
    </div>
  );
};
