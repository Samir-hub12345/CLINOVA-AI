"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { MOCK_REFERRAL_OPTIONS, MOCK_FACILITIES } from "@/mock/facilities";
import { Send } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function ReferralsPage() {
  const [selectedCaseId, setSelectedCaseId] = useState("CASE-SYNTH-003");
  const options = MOCK_REFERRAL_OPTIONS[selectedCaseId] || MOCK_REFERRAL_OPTIONS["CASE-SYNTH-003"];
  const [selectedFacilityId, setSelectedFacilityId] = useState(options[0]?.facility_id || "FAC-MCH-02");
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedFacility = MOCK_FACILITIES.find((f) => f.id === selectedFacilityId);

  const handleDispatch = () => {
    setStatusMessage(
      `Synthetic SBAR handoff dispatched to ${selectedFacility?.name}. Ambulance transport telemetry synchronized.`
    );
  };

  return (
    <RoleGuard
      allowedRoles={["REFERRAL_COORDINATOR", "CLINICIAN", "DOCTOR", "SYSTEM_ADMIN", "AUDITOR", "FACILITY_ADMIN"]}
      title="Referral Coordination Restricted"
      message="Only authorized referral coordinators, clinicians, and facility administrators may access transfer orchestration."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Referral Coordination Workbench"
        subtitle="Regional patient transfers, SBAR clinical handoffs, feasibility matching, and transit tracking"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Referral Coordination" }]}
      />

      {statusMessage && (
        <div
          role="status"
          style={{
            backgroundColor: "var(--clinova-success-bg)",
            border: "1px solid var(--clinova-success-border)",
            color: "var(--clinova-success-text)",
            padding: "10px 14px",
            borderRadius: "var(--clinova-radius-md)",
            fontSize: "0.875rem",
          }}
        >
          {statusMessage}
        </div>
      )}

      {/* Case Selector */}
      <div className="clinova-card" style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <span className="clinova-label">Active Transfer Case:</span>
        {["CASE-SYNTH-003", "CASE-SYNTH-004"].map((cid) => (
          <button
            key={cid}
            onClick={() => {
              setSelectedCaseId(cid);
              setStatusMessage(null);
            }}
            className="clinova-btn clinova-btn-sm"
            style={{
              backgroundColor: selectedCaseId === cid ? "var(--clinova-accent)" : "var(--clinova-surface-subtle)",
              color: selectedCaseId === cid ? "#ffffff" : "var(--clinova-text-secondary)",
              border: "1px solid var(--clinova-border)",
            }}
          >
            {cid}
          </button>
        ))}
      </div>

      <div className="clinova-grid-2col">
        {/* Destination Facility Options */}
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <span className="clinova-label">REGIONAL DESTINATIONS & FEASIBILITY</span>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {options.map((opt) => (
              <div
                key={opt.facility_id}
                onClick={() => setSelectedFacilityId(opt.facility_id)}
                style={{
                  padding: 12,
                  borderRadius: "var(--clinova-radius-md)",
                  border: selectedFacilityId === opt.facility_id
                    ? "2px solid var(--clinova-accent)"
                    : "1px solid var(--clinova-border)",
                  backgroundColor: selectedFacilityId === opt.facility_id
                    ? "var(--clinova-accent-light)"
                    : "var(--clinova-surface)",
                  cursor: "pointer",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <strong style={{ fontSize: "0.9375rem" }}>{opt.facility_name}</strong>
                  <span
                    className="clinova-badge"
                    style={{
                      backgroundColor: opt.feasibility_status === "FEASIBLE" ? "#f0fdf4" : "#fffbeb",
                      color: opt.feasibility_status === "FEASIBLE" ? "#166534" : "#92400e",
                      borderColor: opt.feasibility_status === "FEASIBLE" ? "#bbf7d0" : "#fde68a",
                    }}
                  >
                    {opt.feasibility_status}
                  </span>
                </div>
                <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", marginTop: 4 }}>
                  {opt.feasibility_reason}
                </p>
                <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                  <span>Distance: <strong>{opt.distance_km} km</strong></span>
                  <span>ETA: <strong>{opt.transit_minutes} min</strong></span>
                  <span>Available Beds: <strong>{opt.available_beds}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SBAR Handoff Dossier */}
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span className="clinova-label">SBAR TRANSFER DOSSIER</span>
            <span className="clinova-badge" style={{ backgroundColor: "#ecfdf5", color: "#047857", borderColor: "#a7f3d0" }}>
              SYNTHETIC PROTOCOL
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: "0.8125rem", backgroundColor: "var(--clinova-surface-subtle)", padding: 12, borderRadius: "var(--clinova-radius-md)" }}>
            <div>
              <strong>[S] SITUATION:</strong>
              <p style={{ color: "var(--clinova-text-secondary)" }}>
                Emergency transfer request for {selectedCaseId} requiring immediate tertiary intervention.
              </p>
            </div>
            <div>
              <strong>[B] BACKGROUND:</strong>
              <p style={{ color: "var(--clinova-text-secondary)" }}>
                Baseline stabilized at Cuttack DHH. Acute ECG and vital abnormalities identified.
              </p>
            </div>
            <div>
              <strong>[A] ASSESSMENT:</strong>
              <p style={{ color: "var(--clinova-text-secondary)" }}>
                Critical cardiovascular emergency. Local cath lab down; primary PCI required at SCB MCH.
              </p>
            </div>
            <div>
              <strong>[R] RECOMMENDATION:</strong>
              <p style={{ color: "var(--clinova-text-secondary)" }}>
                Pre-arrival bed reservation, cath lab activation, and ALS ambulance escort.
              </p>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 4 }}>
            <Button variant="emergency" size="md" onClick={handleDispatch}>
              <Send style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Confirm & Dispatch Transfer</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
    </RoleGuard>
  );
}
