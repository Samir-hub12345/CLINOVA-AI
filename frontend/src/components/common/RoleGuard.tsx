"use client";

import React, { useState, useEffect } from "react";
import { Persona } from "@/types";
import { getCurrentUser } from "@/lib/api";
import { LoadingState } from "@/components/ui/States";
import { UnauthorizedState } from "./UnauthorizedState";

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
  title?: string;
  message?: string;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  allowedRoles,
  children,
  title,
  message,
}) => {
  const [user, setUser] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function checkAuth() {
      try {
        const u = await getCurrentUser();
        if (mounted) {
          setUser(u);
          setLoading(false);
        }
      } catch {
        if (mounted) {
          setUser(null);
          setLoading(false);
        }
      }
    }

    checkAuth();

    const handleAuthChange = () => {
      checkAuth();
    };

    window.addEventListener("clinova_auth_changed", handleAuthChange);
    window.addEventListener("clinova_session_expired", handleAuthChange);

    return () => {
      mounted = false;
      window.removeEventListener("clinova_auth_changed", handleAuthChange);
      window.removeEventListener("clinova_session_expired", handleAuthChange);
    };
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: "360px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <LoadingState message="Verifying clinical role and security authorizations..." />
      </div>
    );
  }

  const role = user?.role ? user.role.toUpperCase() : "UNAUTHENTICATED";
  const normalizedAllowed = allowedRoles.map((r) => r.toUpperCase());

  // CLINICIAN / DOCTOR alias normalization
  const effectiveRole = role === "DOCTOR" ? "CLINICIAN" : role;
  const isAuthorized = normalizedAllowed.some(
    (allowed) => allowed === effectiveRole || (allowed === "DOCTOR" && effectiveRole === "CLINICIAN")
  );

  if (!isAuthorized) {
    const isUnauth = role === "UNAUTHENTICATED";
    return (
      <UnauthorizedState
        title={
          isUnauth
            ? "Authentication Required: Clinical Gateway"
            : title || "Access Denied: Insufficient Role Authority"
        }
        message={
          isUnauth
            ? "You must sign in with an authorized clinical or administrative account to access this workstation."
            : message ||
              `Current identity (${user?.full_name || "Unknown"} as ${role}) is not authorized to access this surface.`
        }
        requiredRoles={allowedRoles}
        currentRole={role}
        onLoginClick={() => {
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
        }}
        onSwitchPersona={() => {
          const selectEl = document.querySelector('select[aria-label="Select Active Clinical Role"]') as HTMLSelectElement | null;
          if (selectEl) {
            selectEl.focus();
          }
        }}
      />
    );
  }

  return <>{children}</>;
};
