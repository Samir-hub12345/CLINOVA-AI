"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowLeft, RefreshCw, LogIn } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface UnauthorizedStateProps {
  title?: string;
  message?: string;
  requiredRoles?: string[];
  currentRole?: string;
  onLoginClick?: () => void;
  onSwitchPersona?: () => void;
}

export const UnauthorizedState: React.FC<UnauthorizedStateProps> = ({
  title = "Access Restricted: Unauthorized Role",
  message,
  requiredRoles = [],
  currentRole,
  onLoginClick,
  onSwitchPersona,
}) => {
  return (
    <div
      className="clinova-card"
      role="alert"
      style={{
        maxWidth: 640,
        margin: "var(--clinova-space-8) auto",
        padding: "var(--clinova-space-8) var(--clinova-space-6)",
        textAlign: "center",
        borderTop: "4px solid var(--clinova-danger)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "var(--clinova-space-4)",
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: "var(--clinova-radius-full)",
          backgroundColor: "var(--clinova-danger-bg)",
          color: "var(--clinova-danger)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ShieldAlert style={{ width: 28, height: 28 }} aria-hidden="true" />
      </div>

      <div>
        <h3 style={{ fontSize: "1.25rem", color: "var(--clinova-danger-text)", marginBottom: 8 }}>
          {title}
        </h3>
        <p style={{ fontSize: "0.9375rem", color: "var(--clinova-text-secondary)", lineHeight: 1.5 }}>
          {message ||
            (currentRole
              ? `Your active role (${currentRole}) lacks authorization to access this clinical surface.`
              : "Authentication credentials required to access this clinical surface.")}
        </p>
      </div>

      {requiredRoles.length > 0 && (
        <div
          style={{
            backgroundColor: "var(--clinova-surface-subtle)",
            border: "1px solid var(--clinova-border)",
            borderRadius: "var(--clinova-radius-md)",
            padding: "8px 16px",
            fontSize: "0.8125rem",
          }}
        >
          <span style={{ color: "var(--clinova-text-muted)" }}>Authorized Roles: </span>
          <strong style={{ color: "var(--clinova-text-primary)" }}>
            {requiredRoles.join(", ")}
          </strong>
        </div>
      )}

      <div style={{ display: "flex", gap: 12, marginTop: 8, flexWrap: "wrap", justifyContent: "center" }}>
        {onSwitchPersona && (
          <Button variant="primary" size="sm" onClick={onSwitchPersona}>
            <RefreshCw style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Switch Role Persona</span>
          </Button>
        )}
        {onLoginClick && (
          <Button variant="primary" size="sm" onClick={onLoginClick}>
            <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Sign In with Authorized Account</span>
          </Button>
        )}
        <Link href="/" className="clinova-btn clinova-btn-outline" style={{ textDecoration: "none" }}>
          <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Return to Home</span>
        </Link>
      </div>
    </div>
  );
};
