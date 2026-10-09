import React from "react";
import { FsmStatus } from "@/types";

interface StatusBadgeProps {
  status: FsmStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStyle = (s: FsmStatus) => {
    switch (s) {
      case "NEW":
      case "INTAKE":
      case "INTAKE_RECORDED":
        return { bg: "#f0f9ff", color: "#0369a1", border: "#bae6fd", label: "INTAKE" };
      case "TRIAGE_PENDING":
      case "TRIAGE_IN_PROGRESS":
        return { bg: "#fffbeb", color: "#b45309", border: "#fde68a", label: "TRIAGE" };
      case "PENDING_INFORMATION":
        return { bg: "#fef3c7", color: "#92400e", border: "#fde68a", label: "PENDING INFO" };
      case "REVIEW_REQUIRED":
      case "CLINICIAN_REVIEW_REQUIRED":
      case "DECISION":
        return { bg: "#fef2f2", color: "#b91c1c", border: "#fecaca", label: "REVIEW REQUIRED" };
      case "TRIAGED":
      case "CLINICIAN_REVIEW":
      case "REVIEW_IN_PROGRESS":
        return { bg: "#eff6ff", color: "#1d4ed8", border: "#bfdbfe", label: "REVIEW IN PROGRESS" };
      case "CONTINUE":
      case "OBSERVE":
        return { bg: "#f0fdf4", color: "#15803d", border: "#bbf7d0", label: s };
      case "ESCALATE":
      case "REFER":
      case "TRANSFER_PENDING":
      case "TRANSFER":
      case "DISPOSITION_PENDING":
        return { bg: "#fff7ed", color: "#c2410c", border: "#fed7aa", label: s.replace("_", " ") };
      case "COMPLETED":
      case "OUTCOME":
      case "CLOSED":
        return { bg: "#ecfdf5", color: "#047857", border: "#a7f3d0", label: s === "CLOSED" ? "CLOSED" : "RESOLVED" };
      default:
        return { bg: "#f1f5f9", color: "#475569", border: "#cbd5e1", label: s };
    }
  };

  const st = getStyle(status);

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: st.bg,
        color: st.color,
        borderColor: st.border,
      }}
    >
      {st.label}
    </span>
  );
};
