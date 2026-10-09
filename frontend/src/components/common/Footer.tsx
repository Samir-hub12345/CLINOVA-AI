import React from "react";
import Link from "next/link";
import { ShieldAlert } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--clinova-border)",
        backgroundColor: "var(--clinova-surface)",
        padding: "var(--clinova-space-8) 0 var(--clinova-space-6)",
        marginTop: "auto",
        fontSize: "0.8125rem",
        color: "var(--clinova-text-secondary)",
      }}
    >
      <div className="clinova-container">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "var(--clinova-space-6)",
            marginBottom: "var(--clinova-space-6)",
          }}
        >
          {/* Column 1: Identity & Architecture */}
          <div>
            <strong style={{ fontSize: "0.9375rem", color: "var(--clinova-text-primary)", display: "block", marginBottom: 6 }}>
              CLINOVA AI
            </strong>
            <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", lineHeight: 1.5 }}>
              Continuous Care Intelligence & Clinical Navigation Platform. Connecting Patient Risk, Evidence Uncertainty, and Facility Resources to discover the Safest Achievable Care Pathway.
            </p>
          </div>

          {/* Column 2: Mandatory Clinical Safety Invariant */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <ShieldAlert style={{ width: 15, height: 15, color: "var(--clinova-warning)" }} aria-hidden="true" />
              <strong style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)" }}>
                Clinical Safety Invariant
              </strong>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)", lineHeight: 1.5 }}>
              CLINOVA AI does not formulate autonomous diagnoses or author prescriptions. All care pathways, triage scores, and transfer decisions require review and verification by registered medical practitioners (NMC 2023 Regulations).
            </p>
          </div>

          {/* Column 3: Institutional Links & Policies */}
          <div>
            <strong style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)", display: "block", marginBottom: 6 }}>
              Governance & Compliance
            </strong>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6 }}>
              <li>
                <Link href="/disclaimer" style={{ color: "var(--clinova-accent)", textDecoration: "none" }}>
                  Clinical Decision Support Disclaimer
                </Link>
              </li>
              <li>
                <Link href="/privacy" style={{ color: "var(--clinova-accent)", textDecoration: "none" }}>
                  Zero-PII Privacy & DPDP Act 2023 Policy
                </Link>
              </li>
              <li>
                <Link href="/about" style={{ color: "var(--clinova-accent)", textDecoration: "none" }}>
                  Institutional Mission & Technical Architecture
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div
          style={{
            borderTop: "1px solid var(--clinova-border)",
            paddingTop: "var(--clinova-space-4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            fontSize: "0.75rem",
            color: "var(--clinova-text-muted)",
          }}
        >
          <span>
            © {new Date().getFullYear()} CLINOVA AI. Strictly ₹0 Zero-Cost Production Architecture.
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span>Synthetic Demonstration Instance</span>
            <span>•</span>
            <span>Paschim Banga Emergency Doctrine Enabled</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
