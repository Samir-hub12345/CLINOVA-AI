import { CheckCircle2, AlertCircle, Edit2, AlertTriangle } from "lucide-react";
import { VerificationStatus } from "@/types";

interface EvidenceBadgeProps {
  status: VerificationStatus;
  verifiedBy?: string;
  showIcon?: boolean;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({
  status,
  verifiedBy,
  showIcon = true,
}) => {
  const configs: Record<
    VerificationStatus,
    { label: string; bg: string; color: string; border: string; icon: React.ReactNode }
  > = {
    CONFIRMED: {
      label: verifiedBy ? `VERIFIED (${verifiedBy})` : "CLINICIAN CONFIRMED",
      bg: "#ecfdf5",
      color: "#047857",
      border: "#a7f3d0",
      icon: <CheckCircle2 style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    UNVERIFIED: {
      label: "AWAITING VERIFICATION",
      bg: "#fffbeb",
      color: "#b45309",
      border: "#fde68a",
      icon: <AlertCircle style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    MODIFIED: {
      label: "CLINICIAN MODIFIED",
      bg: "#f0f9ff",
      color: "#0369a1",
      border: "#bae6fd",
      icon: <Edit2 style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
    DISPUTED: {
      label: "DISPUTED EVIDENCE",
      bg: "#fff1f2",
      color: "#be123c",
      border: "#fecdd3",
      icon: <AlertTriangle style={{ width: 11, height: 11 }} aria-hidden="true" />,
    },
  };

  const current = configs[status] || configs.UNVERIFIED;

  return (
    <span
      className="clinova-badge"
      style={{
        backgroundColor: current.bg,
        color: current.color,
        borderColor: current.border,
      }}
      title={`Evidence Verification Status: ${current.label}`}
    >
      {showIcon && current.icon}
      <span>{current.label}</span>
    </span>
  );
};
