import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { Activity, ShieldCheck, ArrowRight, Clock, FileCheck2 } from "lucide-react";

export default function PatientLandingPage() {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Patient Intake & Care Navigation Portal"
        subtitle="Digital symptom registration, vernacular speech entry, and targeted pre-consultation inquiries"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Patient Portal" }]}
      />

      <div
        className="clinova-card"
        style={{
          borderLeft: "6px solid var(--clinova-accent)",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        <h3 style={{ fontSize: "1.25rem" }}>Register for Consultation</h3>
        <p style={{ fontSize: "0.9375rem", color: "var(--clinova-text-secondary)", lineHeight: 1.6 }}>
          Complete a quick digital intake before seeing your doctor. Your information will be summarized directly on the clinical workstation for the examining doctor and triage nurse.
        </p>

        <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
          <Link href="/patient/intake" className="clinova-btn clinova-btn-primary clinova-btn-lg" style={{ textDecoration: "none" }}>
            <Activity style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Begin Patient Intake</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>
        </div>
      </div>

      <div className="clinova-grid-3col">
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <ShieldCheck style={{ width: 18, height: 18, color: "var(--clinova-success)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>Safe & Confidential</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Zero third-party commercial data sharing. Compliant with DPDP Act 2023.
          </p>
        </div>

        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Clock style={{ width: 18, height: 18, color: "var(--clinova-informational)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>Saves Hospital Time</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Pre-structures chief complaints so the doctor can focus on your physical examination.
          </p>
        </div>

        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <FileCheck2 style={{ width: 18, height: 18, color: "#7c3aed" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>Optional Uploads</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Easily attach prior prescriptions or lab reports for automated local text extraction.
          </p>
        </div>
      </div>

      {/* Synthetic Demonstration Quick Track */}
      <div className="clinova-card" style={{ backgroundColor: "var(--clinova-surface-subtle)" }}>
        <span className="clinova-label">SYNTHETIC DEMONSTRATION CASES</span>
        <h4 style={{ fontSize: "0.9375rem", margin: "4px 0 8px" }}>
          Track Existing Demonstration Patient Tokens
        </h4>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <Link href="/patient/case/CASE-SYNTH-001" className="clinova-btn clinova-btn-secondary clinova-btn-sm" style={{ textDecoration: "none" }}>
            Track PT-SYN-0014 (Routine URI)
          </Link>
          <Link href="/patient/case/CASE-SYNTH-003" className="clinova-btn clinova-btn-secondary clinova-btn-sm" style={{ textDecoration: "none" }}>
            Track PT-SYN-0842 (Critical Chest Pain)
          </Link>
          <Link href="/patient/case/CASE-SYNTH-004" className="clinova-btn clinova-btn-secondary clinova-btn-sm" style={{ textDecoration: "none" }}>
            Track PT-SYN-0319 (Urgent Febrile)
          </Link>
        </div>
      </div>
    </div>
  );
}
