"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/ui/PageHeader";
import { Activity, ShieldCheck, ArrowRight, Clock, FileCheck2, Search, KeyRound } from "lucide-react";

export default function PatientLandingPage() {
  const router = useRouter();
  const [tokenInput, setTokenInput] = useState("");
  const [searchError, setSearchError] = useState<string | null>(null);

  const handleLookup = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = tokenInput.trim();
    if (!clean) {
      setSearchError("Please enter your assigned patient token or case reference number.");
      return;
    }
    setSearchError(null);
    router.push(`/patient/case/${encodeURIComponent(clean)}`);
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Patient Intake & Care Navigation Portal"
        subtitle="Digital symptom registration, vernacular speech entry, and targeted pre-consultation inquiries"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Patient Portal" }]}
      />

      {/* Primary Intake Registration CTA */}
      <div
        className="card"
        style={{
          borderLeft: "6px solid var(--teal-600)",
          display: "flex",
          flexDirection: "column",
          gap: 12,
          padding: "var(--s-6)",
        }}
      >
        <h3 style={{ fontSize: "1.25rem", margin: 0 }}>Register for Clinical Consultation</h3>
        <p style={{ fontSize: "0.9375rem", color: "var(--text-2)", lineHeight: 1.6, margin: 0 }}>
          Complete a quick digital intake before seeing your doctor. Your information will be summarized directly on the clinical workstation for the examining doctor and triage nurse.
        </p>

        <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
          <Link href="/patient/intake" className="btn btn-primary btn-lg" style={{ textDecoration: "none" }}>
            <Activity style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Begin Patient Intake</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>
        </div>
      </div>

      {/* Case Status Token Lookup Form */}
      <div className="card" style={{ padding: "var(--s-6)", borderTop: "4px solid var(--navy-800)" }}>
        <div className="stack gap-1" style={{ marginBottom: 14 }}>
          <div className="row gap-2">
            <KeyRound style={{ width: 20, height: 20, color: "var(--navy-800)" }} aria-hidden="true" />
            <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Check My Case Status & Care Plan</h3>
          </div>
          <p className="small subtle" style={{ margin: 0 }}>
            Enter your patient reference token (e.g. <code>PT-SYN-0014</code> or <code>CASE-SYNTH-001</code>) issued at registration or SMS confirmation.
          </p>
        </div>

        {searchError && (
          <div className="alert alert-error" style={{ marginBottom: 12 }}>
            <span className="xs">{searchError}</span>
          </div>
        )}

        <form onSubmit={handleLookup} style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <input
            type="text"
            value={tokenInput}
            onChange={(e) => {
              setTokenInput(e.target.value);
              if (searchError) setSearchError(null);
            }}
            placeholder="Enter token (e.g. PT-SYN-0014, CASE-SYNTH-003)"
            className="input"
            style={{ flex: 1, minWidth: 260 }}
          />
          <button type="submit" className="btn btn-primary">
            <Search style={{ width: 15, height: 15 }} aria-hidden="true" />
            <span>View Care Status</span>
          </button>
        </form>
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
      <div className="card" style={{ backgroundColor: "var(--surface-sunken)" }}>
        <div className="card-body tight stack gap-2">
          <span className="section-title">SYNTHETIC DEMONSTRATION CASES</span>
          <h4 style={{ fontSize: "0.9375rem", margin: "2px 0 6px" }}>
            Track Existing Demonstration Patient Tokens
          </h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            <Link href="/patient/case/PT-SYN-0014" className="btn btn-secondary btn-sm" style={{ textDecoration: "none" }}>
              Track PT-SYN-0014 (Routine URI)
            </Link>
            <Link href="/patient/case/PT-SYN-0842" className="btn btn-secondary btn-sm" style={{ textDecoration: "none" }}>
              Track PT-SYN-0842 (Critical Chest Pain)
            </Link>
            <Link href="/patient/case/PT-SYN-0319" className="btn btn-secondary btn-sm" style={{ textDecoration: "none" }}>
              Track PT-SYN-0319 (Urgent Febrile)
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
