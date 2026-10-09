"use client";

import React from "react";
import { FolderOpen, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

export const EmptyState: React.FC<{
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: { label: string; onClick: () => void };
}> = ({ title, description, icon, action }) => {
  return (
    <div
      className="clinova-card"
      style={{
        textAlign: "center",
        padding: "var(--clinova-space-8) var(--clinova-space-6)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "var(--clinova-space-3)",
      }}
    >
      <div style={{ color: "var(--clinova-text-muted)" }}>
        {icon || <FolderOpen style={{ width: 36, height: 36 }} aria-hidden="true" />}
      </div>
      <h4 style={{ fontSize: "1.125rem" }}>{title}</h4>
      <p style={{ maxWidth: 440, fontSize: "0.875rem" }}>{description}</p>
      {action && (
        <Button variant="secondary" size="sm" onClick={action.onClick} style={{ marginTop: 8 }}>
          {action.label}
        </Button>
      )}
    </div>
  );
};

export const LoadingState: React.FC<{
  message?: string;
  lines?: number;
}> = ({ message = "Loading clinical workspace data...", lines = 3 }) => {
  return (
    <div
      className="clinova-card"
      role="status"
      aria-live="polite"
      style={{
        padding: "var(--clinova-space-6)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-3)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <RefreshCw style={{ width: 16, height: 16, color: "var(--clinova-accent)", animation: "spin 1.5s linear infinite" }} aria-hidden="true" />
        <span style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--clinova-text-secondary)" }}>
          {message}
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 4 }}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            style={{
              height: 14,
              backgroundColor: "var(--clinova-surface-subtle)",
              borderRadius: "var(--clinova-radius-sm)",
              width: i === lines - 1 ? "60%" : "100%",
            }}
          />
        ))}
      </div>
    </div>
  );
};

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({
  title = "Clinical Data Acquisition Error",
  message,
  onRetry,
}) => {
  return (
    <div
      className="clinova-card"
      role="alert"
      style={{
        borderColor: "var(--clinova-danger)",
        backgroundColor: "var(--clinova-danger-bg)",
        padding: "var(--clinova-space-6)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-3)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <AlertCircle style={{ width: 20, height: 20, color: "var(--clinova-danger)" }} aria-hidden="true" />
        <h4 style={{ color: "var(--clinova-danger-text)", margin: 0 }}>{title}</h4>
      </div>
      <p style={{ color: "var(--clinova-danger-text)", fontSize: "0.875rem" }}>{message}</p>
      {onRetry && (
        <div style={{ marginTop: 4 }}>
          <Button variant="danger" size="sm" onClick={onRetry}>
            <RefreshCw style={{ width: 12, height: 12 }} aria-hidden="true" />
            <span>Retry Connection</span>
          </Button>
        </div>
      )}
    </div>
  );
};
