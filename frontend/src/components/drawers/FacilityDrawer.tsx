import React from "react";
import { Drawer } from "@/components/ui/OverlayControls";
import { Button } from "@/components/ui/Button";
import { MOCK_FACILITIES } from "@/mock/facilities";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

interface FacilityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedFacilityId?: string;
}

export const FacilityDrawer: React.FC<FacilityDrawerProps> = ({
  isOpen,
  onClose,
  selectedFacilityId = "FAC-DH-04",
}) => {
  const facility =
    MOCK_FACILITIES.find((f) => f.id === selectedFacilityId) || MOCK_FACILITIES[0];

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="Facility Resources & Feasibility Inspector"
      subtitle={`${facility.name} (${facility.tier} — ${facility.location_name})`}
      width={600}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
        {/* Real-time Operational Bed Capacity */}
        <div className="clinova-grid-2col">
          <div className="clinova-card" style={{ padding: 12 }}>
            <span className="clinova-label">ICU Ventilator Beds</span>
            <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, margin: "4px 0" }}>
              {facility.icu_beds_available} <span style={{ fontSize: "0.875rem", color: "var(--clinova-text-muted)" }}>/ {facility.icu_beds_total}</span>
            </div>
            <span style={{ fontSize: "0.6875rem", color: facility.icu_beds_available > 0 ? "var(--clinova-success-text)" : "var(--clinova-danger-text)" }}>
              {facility.icu_beds_available > 0 ? "Operational Capacity Available" : "Full / Critical Divert Active"}
            </span>
          </div>

          <div className="clinova-card" style={{ padding: 12 }}>
            <span className="clinova-label">General Ward Beds</span>
            <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, margin: "4px 0" }}>
              {facility.general_beds_available} <span style={{ fontSize: "0.875rem", color: "var(--clinova-text-muted)" }}>/ {facility.general_beds_total}</span>
            </div>
            <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
              Oxygen Points: <strong>{facility.oxygen_points_available}</strong>
            </span>
          </div>
        </div>

        {/* Telemetry Freshness */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.75rem",
            color: "var(--clinova-text-muted)",
            padding: "6px 12px",
            backgroundColor: "var(--clinova-surface-subtle)",
            borderRadius: "var(--clinova-radius-md)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Clock style={{ width: 13, height: 13 }} aria-hidden="true" />
            <span>Telemetry Freshness: <strong>{facility.freshness_minutes} minutes ago</strong></span>
          </div>
          <span>ED Wait: <strong>{facility.ed_avg_wait_min}m</strong> ({facility.ed_waiting_cases} in queue)</span>
        </div>

        {/* Capability Checklist */}
        <div>
          <h4 style={{ fontSize: "0.9375rem", marginBottom: 8 }}>
            Clinical Capabilities & Equipment Status
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {facility.capabilities.map((cap) => (
              <div
                key={cap.capability_code}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 12px",
                  borderRadius: "var(--clinova-radius-md)",
                  border: "1px solid var(--clinova-border)",
                  backgroundColor: cap.is_operational ? "var(--clinova-surface)" : "#fffbeb",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  {cap.is_operational ? (
                    <CheckCircle2 style={{ width: 16, height: 16, color: "var(--clinova-success)" }} aria-hidden="true" />
                  ) : (
                    <XCircle style={{ width: 16, height: 16, color: "var(--clinova-warning)" }} aria-hidden="true" />
                  )}
                  <div>
                    <span style={{ fontSize: "0.8125rem", fontWeight: 600 }}>{cap.label}</span>
                    {cap.maintenance_note && (
                      <p style={{ fontSize: "0.6875rem", color: "var(--clinova-warning-text)" }}>
                        {cap.maintenance_note}
                      </p>
                    )}
                  </div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <span
                    className="clinova-badge"
                    style={{
                      backgroundColor: cap.is_operational ? "#f0fdf4" : "#fef2f2",
                      color: cap.is_operational ? "#15803d" : "#b91c1c",
                      borderColor: cap.is_operational ? "#bbf7d0" : "#fecaca",
                    }}
                  >
                    {cap.is_operational ? "ACTIVE" : "UNAVAILABLE"}
                  </span>
                  {cap.last_verified && (
                    <span style={{ display: "block", fontSize: "0.6875rem", color: "var(--clinova-text-muted)", marginTop: 2 }}>
                      Verified {cap.last_verified}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", paddingTop: 12, borderTop: "1px solid var(--clinova-border)" }}>
          <Button variant="secondary" size="md" onClick={onClose}>
            Close Inspector
          </Button>
        </div>
      </div>
    </Drawer>
  );
};
