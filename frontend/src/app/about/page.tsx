import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";

export default function AboutPage() {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="About CLINOVA AI"
        subtitle="Continuous Care Intelligence & Clinical Navigation Platform for Institutional Health Systems"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "About" }]}
      />

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <h3 style={{ fontSize: "1.25rem" }}>Clinical Mission & Institutional Philosophy</h3>
        <p style={{ lineHeight: 1.6 }}>
          In overcrowded district hospitals and under-resourced rural clinics across India, patients often experience fragmented transitions between isolated triage, bedside examination, and referral handoffs.
        </p>
        <p style={{ lineHeight: 1.6 }}>
          <strong>CLINOVA AI</strong> re-architects this journey by shifting from <em>isolated point-in-time triage</em> to <em>continuous care intelligence</em>. The platform synthesizes physiological vitals, evidence provenance, protocol completeness, and regional facility capabilities into a cohesive, explainable decision-support model.
        </p>
      </section>

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <h3 style={{ fontSize: "1.25rem" }}>Core Architectural Pillars</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 12 }}>
          <div style={{ padding: 12, border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong style={{ fontSize: "0.875rem", color: "var(--clinova-accent-text)", display: "block", marginBottom: 4 }}>
              1. Non-Diagnostic Support
            </strong>
            <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
              The system assists human clinical workflow by structuring evidence, surfacing red flags, and estimating risk, without ever claiming autonomous diagnosis.
            </p>
          </div>

          <div style={{ padding: 12, border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong style={{ fontSize: "0.875rem", color: "var(--clinova-accent-text)", display: "block", marginBottom: 4 }}>
              2. Epistemic Uncertainty
            </strong>
            <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
              Missing information, conflicting measurements, and unverified extractions are highlighted prominently rather than hidden behind opaque percentage scores.
            </p>
          </div>

          <div style={{ padding: 12, border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)" }}>
            <strong style={{ fontSize: "0.875rem", color: "var(--clinova-accent-text)", display: "block", marginBottom: 4 }}>
              3. Full Provenance Tracking
            </strong>
            <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
              Every data point is labeled with its origin—patient reported, OCR extracted, voice transcribed, or doctor verified—with an immutable tamper-evident audit trail.
            </p>
          </div>
        </div>
      </section>

      <section className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <h3 style={{ fontSize: "1.25rem" }}>Legal & Clinical Framework Alignment</h3>
        <ul style={{ paddingLeft: 20, fontSize: "0.875rem", display: "flex", flexDirection: "column", gap: 8 }}>
          <li>
            <strong>National Medical Commission (NMC) 2023 Regulations:</strong> Preserves physician sovereignty; no clinical prescription or admission without licensed doctor sign-off.
          </li>
          <li>
            <strong>Bharatiya Sakshya Adhiniyam (BSA) 2023, Section 63:</strong> Tamper-evident cryptographic logging of electronic medical evidence and overrides.
          </li>
          <li>
            <strong>Digital Personal Data Protection (DPDP) Act, 2023:</strong> Strict purpose limitation, zero third-party commercial profiling, and zero-PII architectural design.
          </li>
          <li>
            <strong>Supreme Court of India (Paschim Banga, 1996):</strong> Uncompromising priority for clinical emergency resuscitation before administrative documentation.
          </li>
        </ul>
      </section>

      <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
        <Link href="/staff/triage" className="clinova-btn clinova-btn-primary" style={{ textDecoration: "none" }}>
          <span>Explore Clinical Workstation</span>
          <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
        </Link>
      </div>
    </div>
  );
}
