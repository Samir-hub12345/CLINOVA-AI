import React from "react";
import { AuditLogEntry } from "@/types";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { User } from "lucide-react";

interface AuditTrailItemProps {
  entry: AuditLogEntry;
  compact?: boolean;
}

export const AuditTrailItem: React.FC<AuditTrailItemProps> = ({
  entry,
  compact = false,
}) => {
  return (
    <div
      style={{
        border: "1px solid var(--clinova-border)",
        borderRadius: "var(--clinova-radius-md)",
        padding: compact ? "8px 10px" : "10px 14px",
        backgroundColor: "var(--clinova-surface)",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        transition: "border-color 0.15s ease",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="clinova-mono" style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--clinova-text-muted)" }}>
            #{entry.id}
          </span>
          <span
            className="clinova-badge"
            style={{
              backgroundColor: "#f1f5f9",
              color: "#334155",
              borderColor: "#cbd5e1",
              fontWeight: 700,
            }}
          >
            {entry.action}
          </span>
        </div>

        <span className="clinova-mono" style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
          {entry.timestamp}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
          <User style={{ width: 12, height: 12, color: "var(--clinova-text-muted)" }} aria-hidden="true" />
          <span>
            <strong>{entry.actor_id}</strong> ({entry.actor_role})
          </span>
          <span style={{ color: "var(--clinova-text-muted)" }}>•</span>
          <span style={{ color: "var(--clinova-text-muted)" }}>
            {entry.entity_type} ({entry.entity_id})
          </span>
        </div>

        <ProvenanceBadge provenance={entry.provenance_type} showIcon={false} />
      </div>

      {entry.details && Object.keys(entry.details).length > 0 && (
        <div
          style={{
            marginTop: 2,
            padding: "4px 8px",
            borderRadius: "var(--clinova-radius-xs)",
            backgroundColor: "var(--clinova-surface-subtle)",
            fontSize: "0.6875rem",
            color: "var(--clinova-text-secondary)",
            fontFamily: "var(--clinova-font-mono)",
            wordBreak: "break-all",
          }}
        >
          {Object.entries(entry.details).map(([k, v]) => (
            <span key={k} style={{ marginRight: 10 }}>
              <strong>{k}:</strong> {String(v)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
