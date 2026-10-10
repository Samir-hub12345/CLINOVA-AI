import React from "react";
import { Stethoscope, UserCheck, Shield, ClipboardCheck } from "lucide-react";
import { ClinicalRole } from "@/types";

interface RoleBadgeProps {
  role: ClinicalRole;
}

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role }) => {
  const configs: Record<
    ClinicalRole,
    { label: string; bg: string; color: string; border: string; icon: React.ReactNode }
  > = {
    CLINICIAN: {
      label: "DOCTOR / CLINICIAN",
      bg: "#f0fdfa",
      color: "#0f766e",
      border: "#99f6e4",
      icon: <Stethoscope style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    NURSE: {
      label: "TRIAGE NURSE",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#bae6fd",
      icon: <UserCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    ADMIN: {
      label: "ADMINISTRATOR",
      bg: "#f1f5f9",
      color: "#334155",
      border: "#cbd5e1",
      icon: <Shield style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    FACILITY_ADMIN: {
      label: "FACILITY ADMIN",
      bg: "#f1f5f9",
      color: "#334155",
      border: "#cbd5e1",
      icon: <Shield style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    SYSTEM_ADMIN: {
      label: "SYSTEM ADMIN",
      bg: "#f8fafc",
      color: "#0f172a",
      border: "#94a3b8",
      icon: <Shield style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    REFERRAL_COORDINATOR: {
      label: "REFERRAL COORDINATOR",
      bg: "#fdf4ff",
      color: "#a21caf",
      border: "#f5d0fe",
      icon: <ClipboardCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    AUDITOR: {
      label: "AUDITOR (READ ONLY)",
      bg: "#fafaf9",
      color: "#57534e",
      border: "#e7e5e4",
      icon: <ClipboardCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    PATIENT: {
      label: "PATIENT",
      bg: "#fffbeb",
      color: "#b45309",
      border: "#fde68a",
      icon: <UserCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    RECEPTIONIST: {
      label: "RECEPTIONIST",
      bg: "#f5f3ff",
      color: "#6d28d9",
      border: "#ddd6fe",
      icon: <UserCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
    REVIEWER: {
      label: "PEER REVIEWER",
      bg: "#faf5ff",
      color: "#7e22ce",
      border: "#e9d5ff",
      icon: <ClipboardCheck style={{ width: 12, height: 12 }} aria-hidden="true" />,
    },
  };

  const current = configs[role] || configs.CLINICIAN;

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: current.bg,
        color: current.color,
        borderColor: current.border,
      }}
      title={`Active Clinical Role: ${current.label}`}
    >
      {current.icon}
      <span>{current.label}</span>
    </span>
  );
};
