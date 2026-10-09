import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle, Info } from "lucide-react";

interface AlertBannerProps {
  variant?: "info" | "warning" | "danger" | "success";
  title?: string;
  message: string;
  action?: React.ReactNode;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({
  variant = "info",
  title,
  message,
  action,
}) => {
  const configs = {
    info: {
      bg: "var(--clinova-informational-bg)",
      border: "var(--clinova-informational-border)",
      color: "var(--clinova-informational-text)",
      icon: <Info style={{ width: 16, height: 16 }} aria-hidden="true" />,
    },
    warning: {
      bg: "var(--clinova-warning-bg)",
      border: "var(--clinova-warning-border)",
      color: "var(--clinova-warning-text)",
      icon: <AlertTriangle style={{ width: 16, height: 16 }} aria-hidden="true" />,
    },
    danger: {
      bg: "var(--clinova-danger-bg)",
      border: "var(--clinova-danger-border)",
      color: "var(--clinova-danger-text)",
      icon: <AlertCircle style={{ width: 16, height: 16 }} aria-hidden="true" />,
    },
    success: {
      bg: "var(--clinova-success-bg)",
      border: "var(--clinova-success-border)",
      color: "var(--clinova-success-text)",
      icon: <CheckCircle style={{ width: 16, height: 16 }} aria-hidden="true" />,
    },
  };

  const current = configs[variant];

  return (
    <div
      role="alert"
      style={{
        backgroundColor: current.bg,
        border: `1px solid ${current.border}`,
        borderRadius: "var(--clinova-radius-md)",
        padding: "var(--clinova-space-3) var(--clinova-space-4)",
        display: "flex",
        alignItems: "flex-start",
        gap: "var(--clinova-space-3)",
        color: current.color,
      }}
    >
      <span style={{ marginTop: 2, flexShrink: 0 }}>{current.icon}</span>
      <div style={{ flex: 1 }}>
        {title && <strong style={{ display: "block", fontSize: "0.875rem", marginBottom: 2 }}>{title}</strong>}
        <span style={{ fontSize: "0.8125rem" }}>{message}</span>
      </div>
      {action && <div style={{ flexShrink: 0 }}>{action}</div>}
    </div>
  );
};
