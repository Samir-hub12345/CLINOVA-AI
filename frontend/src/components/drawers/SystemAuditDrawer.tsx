import React from "react";
import { Drawer } from "@/components/ui/OverlayControls";
import { Button } from "@/components/ui/Button";
import { AuditTrailItem } from "@/components/ui/AuditTrailItem";
import { ConnectionStatus } from "@/components/common/ConnectionStatus";
import { MOCK_AUDIT_LOGS } from "@/mock/auditLogs";
import { ShieldCheck, Terminal, Database, Key } from "lucide-react";

interface SystemAuditDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SystemAuditDrawer: React.FC<SystemAuditDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="Developer & System Audit Ledger"
      subtitle="Tamper-Evident Provenance & Zero-PII Compliance Records"
      width={640}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
        {/* Compliance Guarantee */}
        <div
          className="clinova-card"
          style={{
            backgroundColor: "#f8fafc",
            borderColor: "#cbd5e1",
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <ShieldCheck style={{ width: 16, height: 16, color: "var(--clinova-success)" }} aria-hidden="true" />
              <strong style={{ fontSize: "0.875rem" }}>Section 63 BSA & DPDP Act 2023 Compliance</strong>
            </div>
            <ConnectionStatus status="ONLINE" />
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
            Immutable electronic record certification. Every clinician override, vital update, and provenance assertion is cryptographically signed and logged with zero real patient identity storage.
          </p>
        </div>

        {/* Security & Secret Separation Invariant */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, fontSize: "0.75rem" }}>
          <div className="clinova-card" style={{ padding: 10, textAlign: "center" }}>
            <Key style={{ width: 14, height: 14, margin: "0 auto 4px", color: "var(--clinova-accent)" }} aria-hidden="true" />
            <span className="clinova-label" style={{ fontSize: "0.625rem" }}>BROWSER SECRETS</span>
            <strong style={{ display: "block", color: "var(--clinova-success-text)", marginTop: 2 }}>0 EXPOSED</strong>
          </div>
          <div className="clinova-card" style={{ padding: 10, textAlign: "center" }}>
            <Database style={{ width: 14, height: 14, margin: "0 auto 4px", color: "var(--clinova-informational)" }} aria-hidden="true" />
            <span className="clinova-label" style={{ fontSize: "0.625rem" }}>DATA MODE</span>
            <strong style={{ display: "block", color: "var(--clinova-text-primary)", marginTop: 2 }}>SYNTHETIC</strong>
          </div>
          <div className="clinova-card" style={{ padding: 10, textAlign: "center" }}>
            <Terminal style={{ width: 14, height: 14, margin: "0 auto 4px", color: "#6d28d9" }} aria-hidden="true" />
            <span className="clinova-label" style={{ fontSize: "0.625rem" }}>APP ENVIRONMENT</span>
            <strong style={{ display: "block", color: "var(--clinova-text-primary)", marginTop: 2 }}>LOCAL PREVIEW</strong>
          </div>
        </div>

        {/* Audit Log Entries List */}
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
            <h4 style={{ fontSize: "0.9375rem" }}>Recent Tamper-Evident Ledger Entries</h4>
            <span className="clinova-metadata">Showing {MOCK_AUDIT_LOGS.length} records</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {MOCK_AUDIT_LOGS.map((log) => (
              <AuditTrailItem key={log.id} entry={log} />
            ))}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", paddingTop: 12, borderTop: "1px solid var(--clinova-border)" }}>
          <Button variant="secondary" size="md" onClick={onClose}>
            Close Audit Ledger
          </Button>
        </div>
      </div>
    </Drawer>
  );
};
