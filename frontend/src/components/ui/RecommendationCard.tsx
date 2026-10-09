import React from "react";
import { Sparkles, Shield } from "lucide-react";
import { OrchestrationEvaluation } from "@/types";

interface RecommendationCardProps {
  evaluation: OrchestrationEvaluation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  evaluation,
}) => {
  return (
    <div
      className="clinova-card"
      style={{
        borderLeft: "4px solid var(--clinova-accent)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-3)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Sparkles style={{ width: 15, height: 15, color: "var(--clinova-accent)" }} aria-hidden="true" />
          <span className="clinova-label" style={{ color: "var(--clinova-accent-text)" }}>
            CLINICAL ADVISORY SUPPORT (NON-DIAGNOSTIC)
          </span>
        </div>
        <span
          className="clinova-badge"
          style={{
            backgroundColor: "var(--clinova-accent-light)",
            color: "var(--clinova-accent-text)",
            borderColor: "var(--clinova-accent-border)",
            fontWeight: 700,
          }}
        >
          {evaluation.recommended_action}
        </span>
      </div>

      <div>
        <h4 style={{ fontSize: "1rem", color: "var(--clinova-text-primary)", marginBottom: 4 }}>
          {evaluation.priority_level}
        </h4>
        <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
          {evaluation.clinical_rationale}
        </p>
      </div>

      <div
        style={{
          backgroundColor: "var(--clinova-surface-subtle)",
          border: "1px solid var(--clinova-border)",
          borderRadius: "var(--clinova-radius-md)",
          padding: "var(--clinova-space-3)",
          fontSize: "0.8125rem",
        }}
      >
        <span style={{ fontWeight: 600, color: "var(--clinova-text-primary)", display: "block", marginBottom: 2 }}>
          Suggested Pathway Directive:
        </span>
        <span style={{ color: "var(--clinova-text-secondary)" }}>
          {evaluation.clinical_directive}
        </span>
      </div>

      {evaluation.secondary_pathway && (
        <div style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
          <strong>Contingency Option:</strong> {evaluation.secondary_pathway}
        </div>
      )}

      {/* Advisory Mandatory Notice */}
      <div
        style={{
          borderTop: "1px solid var(--clinova-border)",
          paddingTop: 8,
          display: "flex",
          alignItems: "flex-start",
          gap: 6,
          fontSize: "0.6875rem",
          color: "var(--clinova-text-muted)",
        }}
      >
        <Shield style={{ width: 12, height: 12, flexShrink: 0, marginTop: 1, color: "var(--clinova-text-muted)" }} aria-hidden="true" />
        <span>
          <strong>Human Authority Invariant:</strong> Algorithmic advisory synthesis. Clinician retains ultimate diagnostic, prescription, and triage discretion.
        </span>
      </div>
    </div>
  );
};
