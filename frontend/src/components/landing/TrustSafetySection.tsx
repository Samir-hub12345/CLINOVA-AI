"use client";

import React from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  AlertTriangle,
  FileCheck,
  Stethoscope,
  HeartPulse,
} from "lucide-react";

export const TrustSafetySection: React.FC = () => {
  const trustPillars = [
    {
      title: "Evidence Provenance & Traceability",
      icon: Search,
      badge: "Source Grounding",
      desc: "Every clinical datum is tagged with its verifiable source origin: Patient Voice, Bedside Monitor, Clinician Note, or EHR Record. Clinicians can immediately trace any extracted symptom back to its exact raw source.",
    },
    {
      title: "Epistemic Uncertainty Tracking",
      icon: AlertTriangle,
      badge: "Epistemic State",
      desc: "The system actively classifies evidence confidence into Verified, Inferred, Conflicting, and Unknown. If essential information (such as recent kidney function or allergy records) is missing, it is prominently flagged rather than guessed.",
    },
    {
      title: "Non-Delegable Clinician Gate",
      icon: Stethoscope,
      badge: "Human-in-the-Loop",
      desc: "In compliance with National Medical Commission (NMC 2023) regulations, artificial intelligence is strictly assistive. It never prescribes, signs diagnostic notes, or issues clinical orders autonomously without non-repudiable physician approval.",
    },
    {
      title: "Deterministic Clinical Guardrails",
      icon: HeartPulse,
      badge: "Deterministic R01–R06",
      desc: "Acuity scores (NEWS2 and Shock Index) run on verified deterministic algorithms, not generative language models. Acute physiologic deterioration triggers hard alarms that cannot be suppressed by AI suggestions.",
    },
    {
      title: "Zero-PII & Statutory Compliance",
      icon: ShieldCheck,
      badge: "DPDP Act 2023",
      desc: "In alignment with the Digital Personal Data Protection (DPDP) Act 2023, patient identifiers are isolated on edge infrastructure. Zero Personally Identifiable Information (PII) is transmitted to third-party commercial LLM endpoints.",
    },
    {
      title: "Cryptographic Audit Ledger",
      icon: FileCheck,
      badge: "Forensic Ledger",
      desc: "All encounter transitions, diagnostic edits, and referral dispatches are permanently sealed in a SHA-256 chained audit ledger, ensuring non-repudiable accountability and forensic auditability.",
    },
  ];

  return (
    <section
      id="trust"
      tabIndex={-1}
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface-sunken)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="trust-main-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 840, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            TRANSPARENCY, SAFETY & CLINICAL TRUST
          </div>
          <h2
            id="trust-main-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            Built for Clinical Scrutiny and Medical Trust
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            How CLINOVA AI handles clinical information responsibly through explicit provenance, uncertainty auditing, deterministic guardrails, and non-delegable physician authority.
          </p>
        </div>

        {/* 6 Trust Pillars Grid */}
        <div
          className="landing-trust-grid"
          style={{
            marginBottom: "var(--clinova-space-8)",
          }}
        >
          {trustPillars.map((pillar) => {
            const PIcon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className="card"
                style={{
                  padding: "var(--clinova-space-5)",
                  backgroundColor: "var(--surface)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: 12,
                }}
              >
                <div className="stack gap-2">
                  <div className="row between">
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: "var(--r-md)",
                        backgroundColor: "var(--navy-50)",
                        color: "var(--navy-800)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <PIcon style={{ width: 18, height: 18 }} aria-hidden="true" />
                    </div>
                    <span className="badge badge-outline" style={{ fontSize: "10px" }}>
                      {pillar.badge}
                    </span>
                  </div>
                  <strong style={{ fontSize: "1rem", color: "var(--navy-900)" }}>
                    {pillar.title}
                  </strong>
                  <p className="xs subtle" style={{ margin: 0, lineHeight: 1.55 }}>
                    {pillar.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Statutory Clinical Non-Delegation Notice (preserves test requirement) */}
        <div
          className="card"
          style={{
            borderLeft: "6px solid var(--warning)",
            backgroundColor: "var(--surface)",
            padding: "var(--clinova-space-5) var(--clinova-space-6)",
          }}
          aria-labelledby="disclaimer-banner-heading"
        >
          <div className="row gap-3 items-start">
            <ShieldAlert style={{ width: 22, height: 22, color: "var(--warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
            <div className="stack gap-1">
              <strong id="disclaimer-banner-heading" style={{ fontSize: "0.9375rem", color: "var(--navy-900)" }}>
                Mandatory Clinical Decision Support Disclaimer (NMC 2023 & CDSCO)
              </strong>
              <p className="xs subtle" style={{ margin: 0, lineHeight: 1.6 }}>
                CLINOVA AI operates strictly under the principle of <strong>Human-in-the-Loop Clinical Non-Delegation</strong>.
                The platform does not diagnose, prescribe, or execute medical orders autonomously. All care pathways,
                NEWS2 risk scores, epistemic evaluations, and referral recommendations require review, authentication, and non-repudiable
                digital sign-off by a licensed Registered Medical Practitioner.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
