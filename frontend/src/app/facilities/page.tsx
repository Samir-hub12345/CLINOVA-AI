"use client";

import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { MOCK_FACILITIES } from "@/mock/facilities";
import { CheckCircle2, XCircle } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function FacilitiesPage() {
  return (
    <RoleGuard
      allowedRoles={["FACILITY_ADMIN", "SYSTEM_ADMIN", "AUDITOR", "CLINICIAN", "DOCTOR", "NURSE"]}
      title="Facility Access Restricted"
      message="Only authorized clinical and administrative personnel may access regional facility operations."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Regional Facility Resources & Capabilities"
        subtitle="Network-wide bed availability, operational capabilities, oxygen telemetry, and equipment status"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Facilities" }]}
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "var(--clinova-space-5)" }}>
        {MOCK_FACILITIES.map((facility) => (
          <div
            key={facility.id}
            className="clinova-card"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              gap: 12,
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span className="clinova-mono" style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                  {facility.facility_code}
                </span>
                <span className="clinova-badge" style={{ backgroundColor: "#f0f9ff", color: "#0369a1", borderColor: "#bae6fd" }}>
                  Tier: {facility.tier}
                </span>
              </div>

              <h3 style={{ fontSize: "1.125rem", margin: "4px 0" }}>{facility.name}</h3>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                {facility.location_name}
              </p>

              {/* Bed Metrics */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 8,
                  margin: "12px 0",
                  padding: 8,
                  backgroundColor: "var(--clinova-surface-subtle)",
                  borderRadius: "var(--clinova-radius-md)",
                }}
              >
                <div>
                  <span className="clinova-label" style={{ fontSize: "0.625rem" }}>ICU Beds</span>
                  <div className="clinova-mono" style={{ fontSize: "1.125rem", fontWeight: 700 }}>
                    {facility.icu_beds_available} / {facility.icu_beds_total}
                  </div>
                </div>
                <div>
                  <span className="clinova-label" style={{ fontSize: "0.625rem" }}>Ward Beds</span>
                  <div className="clinova-mono" style={{ fontSize: "1.125rem", fontWeight: 700 }}>
                    {facility.general_beds_available} / {facility.general_beds_total}
                  </div>
                </div>
              </div>

              {/* Capabilities List */}
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>KEY CAPABILITIES:</span>
                {facility.capabilities.slice(0, 4).map((cap) => (
                  <div
                    key={cap.capability_code}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "0.75rem",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      {cap.is_operational ? (
                        <CheckCircle2 style={{ width: 12, height: 12, color: "var(--clinova-success)" }} aria-hidden="true" />
                      ) : (
                        <XCircle style={{ width: 12, height: 12, color: "var(--clinova-warning)" }} aria-hidden="true" />
                      )}
                      <span>{cap.label}</span>
                    </div>
                    <span style={{ color: cap.is_operational ? "var(--clinova-success-text)" : "var(--clinova-warning-text)", fontWeight: 600 }}>
                      {cap.is_operational ? "Active" : "Down"}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "0.6875rem",
                color: "var(--clinova-text-muted)",
                paddingTop: 8,
                borderTop: "1px solid var(--clinova-border)",
              }}
            >
              <span>Telemetry: <strong>{facility.freshness_minutes}m ago</strong></span>
              <span>ED Wait: <strong>{facility.ed_avg_wait_min}m</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
    </RoleGuard>
  );
}
