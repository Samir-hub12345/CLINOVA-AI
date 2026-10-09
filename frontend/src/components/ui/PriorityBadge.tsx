import React from "react";
import { AlertOctagon, AlertTriangle, Clock, CheckCircle } from "lucide-react";
import { AcuityTier } from "@/types";

interface PriorityBadgeProps {
  tier: AcuityTier;
  showIcon?: boolean;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  tier,
  showIcon = true,
}) => {
  const configs: Record<
    AcuityTier,
    { label: string; bg: string; color: string; border: string; icon: React.ReactNode }
  > = {
    CRITICAL: {
      label: "P1 — CRITICAL / IMMEDIATE",
      bg: "#fef2f2",
      color: "#991b1b",
      border: "#f87171",
      icon: <AlertOctagon style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    URGENT: {
      label: "P2 — URGENT",
      bg: "#fffbeb",
      color: "#92400e",
      border: "#fcd34d",
      icon: <AlertTriangle style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    MODERATE: {
      label: "P3 — MODERATE",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#7dd3fc",
      icon: <Clock style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    ROUTINE: {
      label: "P4 — ROUTINE",
      bg: "#f0fdf4",
      color: "#166534",
      border: "#86efac",
      icon: <CheckCircle style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
  };

  const current = configs[tier] || configs.ROUTINE;

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: current.bg,
        color: current.color,
        borderColor: current.border,
        fontWeight: tier === "CRITICAL" ? 700 : 600,
      }}
    >
      {showIcon && current.icon}
      <span>{current.label}</span>
    </span>
  );
};
