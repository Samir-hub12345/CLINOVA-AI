import React, { useState } from "react";
import { Drawer } from "@/components/ui/OverlayControls";
import { Button } from "@/components/ui/Button";
import { ReferralOption } from "@/types";
import { MOCK_REFERRAL_OPTIONS, MOCK_FACILITIES } from "@/mock/facilities";
import { Share2, Send } from "lucide-react";

interface ReferralDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  caseId?: string;
}

export const ReferralDrawer: React.FC<ReferralDrawerProps> = ({
  isOpen,
  onClose,
  caseId = "CASE-SYNTH-003",
}) => {
  const options: ReferralOption[] =
    MOCK_REFERRAL_OPTIONS[caseId] || MOCK_REFERRAL_OPTIONS["CASE-SYNTH-003"];
  const [selectedFacilityId, setSelectedFacilityId] = useState<string>(
    options[0]?.facility_id || "FAC-MCH-02"
  );
  const sbarGenerated = true;
  const [transferStatus, setTransferStatus] = useState<string>("READY_TO_DISPATCH");

  const selectedFacility = MOCK_FACILITIES.find((f) => f.id === selectedFacilityId);

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="Referral Coordination Workbench"
      subtitle={`Inter-Facility Transfer & SBAR Handoff for ${caseId}`}
      width={600}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
        {/* Status Callout */}
        <div
          style={{
            backgroundColor: "var(--clinova-informational-bg)",
            border: "1px solid var(--clinova-informational-border)",
            borderRadius: "var(--clinova-radius-md)",
            padding: "var(--clinova-space-3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Share2 style={{ width: 16, height: 16, color: "var(--clinova-informational-text)" }} aria-hidden="true" />
            <span style={{ fontSize: "0.8125rem", color: "var(--clinova-informational-text)" }}>
              Transfer Readiness: <strong>{transferStatus}</strong>
            </span>
          </div>
          <span className="clinova-badge" style={{ backgroundColor: "#ffffff", color: "#0369a1", borderColor: "#bae6fd" }}>
            SYNTHETIC REFERRAL SHELL
          </span>
        </div>

        {/* Destination Facility Selector */}
        <div>
          <label className="clinova-form-label" style={{ marginBottom: 6, display: "block" }}>
            Select Regional Destination Facility:
          </label>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {options.map((opt) => (
              <div
                key={opt.facility_id}
                onClick={() => setSelectedFacilityId(opt.facility_id)}
                style={{
                  padding: "var(--clinova-space-3)",
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
                  <strong style={{ fontSize: "0.875rem" }}>{opt.facility_name}</strong>
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
                <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)", marginTop: 4 }}>
                  {opt.feasibility_reason}
                </p>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 6, fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                  <span>Distance: <strong>{opt.distance_km} km</strong></span>
                  <span>Transit ETA: <strong>{opt.transit_minutes} min</strong></span>
                  <span>Available Beds: <strong>{opt.available_beds}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Structured SBAR Packet */}
        {sbarGenerated && (
          <div
            className="clinova-card"
            style={{
              backgroundColor: "var(--clinova-surface-subtle)",
              display: "flex",
              flexDirection: "column",
              gap: 10,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="clinova-label">STRUCTURED SBAR CLINICAL HANDOFF</span>
              <span className="clinova-badge" style={{ backgroundColor: "#ecfdf5", color: "#047857", borderColor: "#a7f3d0" }}>
                WHO-COMPLIANT
              </span>
            </div>

            <div>
              <strong style={{ fontSize: "0.75rem", color: "var(--clinova-text-primary)" }}>[S] SITUATION:</strong>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                Emergency transfer request for PT-SYN-0842 (52-58 YRS, MALE) presenting with acute crushing chest pain for 45 min.
              </p>
            </div>

            <div>
              <strong style={{ fontSize: "0.75rem", color: "var(--clinova-text-primary)" }}>[B] BACKGROUND:</strong>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                Pre-hospital presentation with severe distress. Triage ECG demonstrates acute anterior STEMI (V1-V4). Initial BP 88/54 mmHg.
              </p>
            </div>

            <div>
              <strong style={{ fontSize: "0.75rem", color: "var(--clinova-text-primary)" }}>[A] ASSESSMENT:</strong>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                Impending cardiogenic shock with anterior STEMI. Acuity: CRITICAL. Local Cath Lab undergoing calibration; immediate PCI diversion mandatory.
              </p>
            </div>

            <div>
              <strong style={{ fontSize: "0.75rem", color: "var(--clinova-text-primary)" }}>[R] RECOMMENDATION:</strong>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                Acceptance to SCB MCH Cath Lab. Dual antiplatelet load (Aspirin 300mg, Clopidogrel 300mg) administered. Advanced Life Support ambulance dispatched.
              </p>
            </div>
          </div>
        )}

        {/* Transfer Action Controls */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, paddingTop: 12, borderTop: "1px solid var(--clinova-border)" }}>
          <Button variant="secondary" size="md" onClick={onClose}>
            Close
          </Button>
          <Button
            variant="emergency"
            size="md"
            onClick={() => {
              setTransferStatus("DISPATCHED");
              alert(`Synthetic transfer handoff dispatched to ${selectedFacility?.name || "destination"}!`);
            }}
          >
            <Send style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Confirm & Dispatch Transfer</span>
          </Button>
        </div>
      </div>
    </Drawer>
  );
};
