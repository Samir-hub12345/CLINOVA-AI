import React from "react";
import {
  CheckCircle2,
  HelpCircle,
  AlertTriangle,
  Clock,
  Sparkles,
} from "lucide-react";
import { EpistemicStatus } from "@/types";

interface UncertaintyIndicatorProps {
  status: EpistemicStatus;
  explanation?: string;
  showExplanation?: boolean;
}

export const UncertaintyIndicator: React.FC<UncertaintyIndicatorProps> = ({
  status,
  explanation,
  showExplanation = false,
}) => {
  const configs: Record<
    EpistemicStatus,
    { label: string; bg: string; color: string; border: string; icon: React.ReactNode; defaultDesc: string }
  > = {
    VERIFIED: {
      label: "VERIFIED",
      bg: "#ecfdf5",
      color: "#047857",
      border: "#a7f3d0",
      icon: <CheckCircle2 style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Directly corroborated and verified by qualified medical practitioner.",
    },
    KNOWN: {
      label: "DOCUMENTED",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#bae6fd",
      icon: <CheckCircle2 style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Directly reported by patient or primary source, pending clinician gate.",
    },
    INFERRED: {
      label: "INFERRED",
      bg: "#fff7ed",
      color: "#c2410c",
      border: "#fed7aa",
      icon: <Sparkles style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Computational inference from clinical patterns; requires independent clinical judgment.",
    },
    CONFLICTING: {
      label: "CONFLICTING",
      bg: "#fff1f2",
      color: "#be123c",
      border: "#fecdd3",
      icon: <AlertTriangle style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Discrepancy detected across multiple data sources. Clinician resolution needed.",
    },
    UNKNOWN: {
      label: "MISSING / UNKNOWN",
      bg: "#f1f5f9",
      color: "#475569",
      border: "#cbd5e1",
      icon: <HelpCircle style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Critical clinical parameter has not been acquired or documented.",
    },
    UNRELIABLE: {
      label: "LOW CONFIDENCE",
      bg: "#fefce8",
      color: "#a16207",
      border: "#fef08a",
      icon: <Clock style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Stale, noisy, or uncorroborated report requiring repeat acquisition.",
    },
    REJECTED: {
      label: "REJECTED",
      bg: "#fee2e2",
      color: "#991b1b",
      border: "#fca5a5",
      icon: <AlertTriangle style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Explicitly rejected by clinician as artifact or incorrect observation.",
    },
    SUPERSEDED: {
      label: "SUPERSEDED",
      bg: "#f3f4f6",
      color: "#6b7280",
      border: "#d1d5db",
      icon: <Clock style={{ width: 11, height: 11 }} aria-hidden="true" />,
      defaultDesc: "Superseded by newer authoritative clinical record.",
    },
  };

  const current = configs[status] || configs.UNKNOWN;
  const desc = explanation || current.defaultDesc;

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: 3 }}>
      <span
        className="clinova-badge"
        style={{
          backgroundColor: current.bg,
          color: current.color,
          borderColor: current.border,
        }}
        title={`Epistemic State: ${current.label} — ${desc}`}
      >
        {current.icon}
        <span>{current.label}</span>
      </span>
      {showExplanation && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
          {desc}
        </span>
      )}
    </div>
  );
};
