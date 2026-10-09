import React from "react";
import {
  UserCheck,
  User,
  Mic,
  FileScan,
  Sparkles,
  Cpu,
  FileText,
  Building,
} from "lucide-react";
import { ProvenanceType } from "@/types";

interface ProvenanceBadgeProps {
  provenance: ProvenanceType;
  showIcon?: boolean;
}

export const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({
  provenance,
  showIcon = true,
}) => {
  const configs: Record<
    ProvenanceType,
    { label: string; bg: string; color: string; border: string; borderStyle?: string; icon: React.ReactNode }
  > = {
    CLINICIAN_VERIFIED: {
      label: "CLINICIAN VERIFIED",
      bg: "#ecfdf5",
      color: "#047857",
      border: "#6ee7b7",
      borderStyle: "solid",
      icon: <UserCheck style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    PATIENT_REPORTED: {
      label: "PATIENT REPORTED",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#7dd3fc",
      borderStyle: "solid",
      icon: <User style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    VOICE_TRANSCRIBED: {
      label: "VOICE TRANSCRIBED",
      bg: "#f5f3ff",
      color: "#6d28d9",
      border: "#c4b5fd",
      borderStyle: "solid",
      icon: <Mic style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    OCR_EXTRACTED: {
      label: "OCR EXTRACTED",
      bg: "#fff7ed",
      color: "#c2410c",
      border: "#fdba74",
      borderStyle: "solid",
      icon: <FileScan style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    STAFF_ENTERED: {
      label: "STAFF ENTERED",
      bg: "#f1f5f9",
      color: "#334155",
      border: "#cbd5e1",
      borderStyle: "solid",
      icon: <FileText style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    AI_INFERRED: {
      label: "AI INFERRED (UNVERIFIED)",
      bg: "#fffbeb",
      color: "#b45309",
      border: "#f59e0b",
      borderStyle: "dashed", // Visual distinction: dashed border for AI inference
      icon: <Sparkles style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    SYSTEM_DERIVED: {
      label: "SYSTEM DERIVED",
      bg: "#f8fafc",
      color: "#475569",
      border: "#e2e8f0",
      borderStyle: "solid",
      icon: <Cpu style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    EXTERNAL_RECORD: {
      label: "EXTERNAL RECORD",
      bg: "#f0fdf4",
      color: "#166534",
      border: "#bbf7d0",
      borderStyle: "solid",
      icon: <Building style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
  };

  const current = configs[provenance] || configs.SYSTEM_DERIVED;

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: current.bg,
        color: current.color,
        borderColor: current.border,
        borderStyle: current.borderStyle || "solid",
        borderWidth: "1.5px",
      }}
      title={`Data Provenance: ${current.label}`}
    >
      {showIcon && current.icon}
      <span>{current.label}</span>
    </span>
  );
};
