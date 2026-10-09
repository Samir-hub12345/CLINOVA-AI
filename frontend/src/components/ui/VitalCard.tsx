import React from "react";
import { ProvenanceType, EpistemicStatus } from "@/types";
import { ProvenanceBadge } from "./ProvenanceBadge";

interface VitalCardProps {
  label: string;
  value: string | number | undefined;
  unit: string;
  normalRange?: string;
  isAbnormal?: boolean;
  isCritical?: boolean;
  provenance?: ProvenanceType;
  epistemicStatus?: EpistemicStatus;
  freshnessStatus?: "AVAILABLE" | "STALE" | "MISSING";
}

export const VitalCard: React.FC<VitalCardProps> = ({
  label,
  value,
  unit,
  normalRange,
  isAbnormal = false,
  isCritical = false,
  provenance,
  freshnessStatus,
}) => {
  const isMissing = value === undefined || value === null || value === "";

  let borderColor = "var(--clinova-border)";
  let bgColor = "var(--clinova-surface)";
  let valueColor = "var(--clinova-text-primary)";

  if (isCritical) {
    borderColor = "var(--clinova-danger)";
    bgColor = "var(--clinova-danger-bg)";
    valueColor = "var(--clinova-danger-text)";
  } else if (isAbnormal) {
    borderColor = "var(--clinova-warning)";
    bgColor = "var(--clinova-warning-bg)";
    valueColor = "var(--clinova-warning-text)";
  }

  return (
    <div
      className="clinova-card"
      style={{
        borderColor,
        backgroundColor: bgColor,
        padding: "var(--clinova-space-3) var(--clinova-space-4)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        minHeight: 96,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 4 }}>
        <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>
          {label}
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {freshnessStatus && (
            <span
              className="clinova-badge"
              style={{
                fontSize: "0.625rem",
                padding: "1px 5px",
                fontWeight: 600,
                backgroundColor:
                  freshnessStatus === "AVAILABLE"
                    ? "var(--clinova-success-bg)"
                    : freshnessStatus === "STALE"
                    ? "var(--clinova-warning-bg)"
                    : "var(--clinova-danger-bg)",
                color:
                  freshnessStatus === "AVAILABLE"
                    ? "var(--clinova-success-text)"
                    : freshnessStatus === "STALE"
                    ? "var(--clinova-warning-text)"
                    : "var(--clinova-danger-text)",
                borderColor:
                  freshnessStatus === "AVAILABLE"
                    ? "var(--clinova-success-border)"
                    : freshnessStatus === "STALE"
                    ? "var(--clinova-warning-border)"
                    : "var(--clinova-danger-border)",
              }}
            >
              {freshnessStatus}
            </span>
          )}
          {provenance && <ProvenanceBadge provenance={provenance} showIcon={false} />}
        </div>
      </div>

      <div style={{ margin: "4px 0", display: "flex", alignItems: "baseline", gap: 6 }}>
        {isMissing ? (
          <span style={{ color: "var(--clinova-text-muted)", fontStyle: "italic", fontSize: "0.875rem" }}>
            Unrecorded
          </span>
        ) : (
          <>
            <span
              className="clinova-mono"
              style={{
                fontSize: "1.5rem",
                fontWeight: 700,
                color: valueColor,
                lineHeight: 1.1,
              }}
            >
              {value}
            </span>
            <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)", fontWeight: 500 }}>
              {unit}
            </span>
          </>
        )}
      </div>

      {normalRange && (
        <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
          Ref: {normalRange}
        </span>
      )}
    </div>
  );
};
