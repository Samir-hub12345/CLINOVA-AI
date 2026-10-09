import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { ShieldCheck } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Privacy & Data Protection Policy"
        subtitle="Zero-PII Architecture & Compliance with Digital Personal Data Protection (DPDP) Act, 2023"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Privacy Policy" }]}
      />

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <ShieldCheck style={{ width: 20, height: 20, color: "var(--clinova-success)" }} aria-hidden="true" />
          <h3 style={{ fontSize: "1.125rem" }}>Zero-PII Engineering Commitment</h3>
        </div>
        <p style={{ lineHeight: 1.6, fontSize: "0.875rem" }}>
          CLINOVA AI is engineered from the ground up to prevent the storage, leakage, or external transmission of Personally Identifiable Information (PII). All patient records in non-production environments utilize strictly synthetic identifiers (e.g. <code>CASE-SYNTH-*</code>, <code>PT-SYN-*</code>).
        </p>
      </section>

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <h3 style={{ fontSize: "1.125rem" }}>Statutory DPDP Act 2023 Principles</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: "0.875rem" }}>
          <div style={{ padding: 12, backgroundColor: "var(--clinova-surface-subtle)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong>Section 4 — Lawful Purpose:</strong> Clinical data processing is strictly limited to patient care navigation, vital risk triage, and referral coordination during active hospital encounters.
          </div>
          <div style={{ padding: 12, backgroundColor: "var(--clinova-surface-subtle)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong>Section 6 — Explicit Consent:</strong> Patients provide informed consent prior to entering symptom narratives and report uploads.
          </div>
          <div style={{ padding: 12, backgroundColor: "var(--clinova-surface-subtle)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong>Section 8(7) — Local Edge Persistence:</strong> Sensitive medical tokens and clinical transcripts are processed on institutional edge devices, eliminating mandatory cloud relay.
          </div>
        </div>
      </section>

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <h3 style={{ fontSize: "1.125rem" }}>No Third-Party Advertising or Brokerage</h3>
        <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
          CLINOVA AI does not monetize, sell, license, or share clinical health data with pharmaceutical companies, insurance underwriters, ad brokers, or marketing intermediaries.
        </p>
      </section>
    </div>
  );
}
