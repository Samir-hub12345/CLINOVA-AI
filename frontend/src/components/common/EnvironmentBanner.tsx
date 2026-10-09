import React from "react";
import { Server, MapPin } from "lucide-react";

interface EnvironmentBannerProps {
  environmentName?: string;
  facilityName?: string;
  facilityCode?: string;
}

export const EnvironmentBanner: React.FC<EnvironmentBannerProps> = ({
  environmentName = "Local Edge Sandbox (Phase 12)",
  facilityName = "Cuttack District Headquarters Hospital",
  facilityCode = "FAC-DH-04",
}) => {
  return (
    <div className="clinova-banner-env">
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <Server style={{ width: 12, height: 12, color: "#38bdf8" }} aria-hidden="true" />
        <span style={{ color: "#94a3b8" }}>ENV:</span>
        <strong style={{ color: "#f8fafc" }}>{environmentName}</strong>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <MapPin style={{ width: 12, height: 12, color: "#34d399" }} aria-hidden="true" />
        <span style={{ color: "#94a3b8" }}>FACILITY:</span>
        <strong style={{ color: "#f8fafc" }}>
          {facilityName} ({facilityCode})
        </strong>
      </div>
    </div>
  );
};
