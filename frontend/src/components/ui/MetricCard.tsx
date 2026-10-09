import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: string;
  icon?: React.ReactNode;
  variant?: "default" | "critical" | "warning" | "success";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  icon,
  variant = "default",
}) => {
  const borderMap = {
    default: "var(--clinova-border)",
    critical: "var(--clinova-danger)",
    warning: "var(--clinova-warning)",
    success: "var(--clinova-success)",
  };

  return (
    <div
      className="clinova-card"
      style={{
        borderColor: borderMap[variant],
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span className="clinova-label">{label}</span>
        {icon && <span style={{ color: "var(--clinova-text-muted)" }}>{icon}</span>}
      </div>

      <div className="clinova-mono" style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--clinova-text-primary)" }}>
        {value}
      </div>

      {subtext && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
          {subtext}
        </span>
      )}
    </div>
  );
};
