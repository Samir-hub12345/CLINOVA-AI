"use client";

import React from "react";
import Link from "next/link";
import {
  Sparkles,
  ArrowRight,
  LogIn,
  ShieldCheck,
  HeartPulse,
  AlertOctagon,
  Activity,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Stethoscope,
} from "lucide-react";

export const HeroSection: React.FC = () => {
  return (
    <section
      className="landing-section landing-hero-section"
      style={{
        paddingTop: "var(--clinova-space-8)",
        paddingBottom: "var(--clinova-space-12)",
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="hero-main-heading"
    >
      <div className="clinova-container">
        <div className="landing-hero-grid">
          {/* LEFT COLUMN: Narrative & Call to Actions */}
          <div className="landing-hero-left stack gap-4">
            {/* Eyebrow Ribbon */}
            <div className="demo-ribbon demo-ribbon-teal" style={{ alignSelf: "flex-start" }}>
              <Sparkles style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />
              <span>CLINICAL INTELLIGENCE PLATFORM</span>
            </div>

            {/* Headline — Deep Clinical Navy, STRICTLY NO GRADIENT TEXT */}
            <h1
              id="hero-main-heading"
              className="landing-hero-headline"
              style={{
                fontSize: "clamp(2.25rem, 4vw, 3.25rem)",
                fontWeight: 800,
                lineHeight: 1.15,
                color: "var(--navy-900)",
                letterSpacing: "-0.03em",
                margin: 0,
              }}
            >
              From Patient Information to Clearer Clinical Decisions.
            </h1>

            {/* Supporting Text */}
            <p
              className="landing-hero-sub"
              style={{
                fontSize: "1.125rem",
                color: "var(--text-2)",
                lineHeight: 1.6,
                margin: 0,
                maxWidth: 580,
              }}
            >
              Bring patient narratives, clinical evidence, AI-generated summaries and connected care workflows into one structured review experience.
            </p>

            {/* Sub-value Proposition (preserves test requirement: 'Less paperwork') */}
            <div
              style={{
                backgroundColor: "var(--surface-sunken)",
                borderLeft: "3px solid var(--teal-600)",
                borderRadius: "0 var(--r-md) var(--r-md) 0",
                padding: "10px 14px",
                maxWidth: 580,
              }}
            >
              <div style={{ fontSize: "0.875rem", color: "var(--navy-900)", fontWeight: 600 }}>
                Less paperwork. More time for patient care.
              </div>
              <div className="xs muted" style={{ marginTop: 2, lineHeight: 1.4 }}>
                Continuous Care Intelligence connects Patient Risk, Evidence Uncertainty, and Facility Resources into the Safest Achievable Care Pathway.
              </div>
            </div>

            {/* Primary & Secondary Action CTAs */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                flexWrap: "wrap",
                gap: 12,
                marginTop: 4,
              }}
            >
              <a href="#platform" className="btn btn-primary btn-lg" style={{ gap: 8, backgroundColor: "var(--navy-900)" }}>
                <span>Explore the Platform</span>
                <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
              </a>

              <Link href="/login" className="btn btn-secondary btn-lg" style={{ gap: 8 }}>
                <LogIn style={{ width: 16, height: 16, color: "var(--navy-800)" }} aria-hidden="true" />
                <span>Sign In</span>
              </Link>
            </div>

            {/* Mandatory Non-Delegation Clinical Statement */}
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 8,
                maxWidth: 560,
                marginTop: 2,
              }}
            >
              <ShieldCheck
                style={{ width: 18, height: 18, color: "var(--teal-600)", flexShrink: 0, marginTop: 2 }}
                aria-hidden="true"
              />
              <p
                style={{
                  fontSize: "0.8125rem",
                  color: "var(--text-3)",
                  lineHeight: 1.45,
                  margin: 0,
                }}
              >
                AI supports clinical review. Authorized healthcare professionals retain decision authority.
              </p>
            </div>

            {/* Architectural Trust Pillars */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 170px), 1fr))",
                gap: 10,
                marginTop: 10,
                maxWidth: 580,
              }}
            >
              <div
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "10px 12px",
                  backgroundColor: "var(--surface)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <ShieldCheck style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.75rem", color: "var(--navy-900)" }}>Zero-PII & Statutory Compliance</strong>
                </div>
                <div style={{ fontSize: "0.6875rem", color: "var(--text-3)" }}>
                  DPDP Act 2023 & NMC regulations
                </div>
              </div>

              <div
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "10px 12px",
                  backgroundColor: "var(--surface)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <HeartPulse style={{ width: 14, height: 14, color: "var(--warning)" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.75rem", color: "var(--navy-900)" }}>Clinical Guardrails</strong>
                </div>
                <div style={{ fontSize: "0.6875rem", color: "var(--text-3)" }}>
                  Dual-engine NEWS2 & Shock Index
                </div>
              </div>

              <div
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "10px 12px",
                  backgroundColor: "var(--surface)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <AlertOctagon style={{ width: 14, height: 14, color: "var(--info)" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.75rem", color: "var(--navy-900)" }}>Paschim Banga Doctrine</strong>
                </div>
                <div style={{ fontSize: "0.6875rem", color: "var(--text-3)" }}>
                  Emergency resuscitation priority
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Authentic High-Fidelity Product Preview */}
          <div className="landing-hero-right">
            <div className="landing-product-preview-frame">
              {/* Mockup Window Titlebar */}
              <div className="preview-window-bar">
                <div className="preview-window-dots" aria-hidden="true">
                  <span className="dot dot-red" />
                  <span className="dot dot-amber" />
                  <span className="dot dot-green" />
                </div>
                <div className="preview-window-title">
                  <span>CLINOVA Doctor Workbench</span>
                  <span className="preview-case-tag">CASE-SYNTH-003</span>
                </div>
                <div className="preview-demo-badge">
                  <span>SYNTHETIC DEMO</span>
                </div>
              </div>

              {/* Mockup Patient Header */}
              <div className="preview-patient-header">
                <div className="row gap-3 wrap">
                  <div className="preview-avatar">AB</div>
                  <div>
                    <div className="row gap-2">
                      <strong style={{ fontSize: "1rem", color: "var(--navy-900)" }}>Aisha Bello</strong>
                      <span className="badge badge-navy">58F • PT-SYN-3720</span>
                    </div>
                    <div className="xs muted" style={{ marginTop: 2 }}>
                      Encounter: Acute Exacerbation OPD • Lekki Family Health Clinic (FAC-DH-04)
                    </div>
                  </div>
                </div>
                <div className="row gap-2">
                  <span className="badge badge-warning" style={{ fontWeight: 600 }}>
                    <Activity style={{ width: 12, height: 12 }} aria-hidden="true" />
                    NEWS2: 6 (Moderate Risk)
                  </span>
                  <span className="badge badge-teal">
                    Shock Index: 0.74 (Stable)
                  </span>
                </div>
              </div>

              {/* Mockup 2-Column Workstation Grid */}
              <div className="preview-workstation-content">
                {/* Column A: Patient Timeline & Extracted Findings */}
                <div className="preview-subpanel">
                  <div className="preview-subpanel-title">
                    <Clock style={{ width: 13, height: 13, color: "var(--teal-600)" }} aria-hidden="true" />
                    <span>TIMELINE & EVIDENCE PROVENANCE</span>
                  </div>

                  <div className="preview-timeline-list stack gap-2">
                    <div className="preview-timeline-item">
                      <div className="row between">
                        <strong className="xs" style={{ color: "var(--navy-900)" }}>08:30 Bedside Vitals</strong>
                        <span className="prov prov-verified">Bedside Vitals</span>
                      </div>
                      <div className="xs subtle" style={{ marginTop: 2 }}>
                        BP 142/90 mmHg • HR 104 bpm • SpO2 93% on room air • RR 22/min
                      </div>
                    </div>

                    <div className="preview-timeline-item">
                      <div className="row between">
                        <strong className="xs" style={{ color: "var(--navy-900)" }}>08:45 Voice Intake (Transcribed)</strong>
                        <span className="prov prov-reported">Patient Stated</span>
                      </div>
                      <div className="xs subtle" style={{ marginTop: 2 }}>
                        “Worsening shortness of breath on exertion, orthopnea x 3 nights, bilateral pedal edema”
                      </div>
                    </div>

                    <div className="preview-timeline-item">
                      <div className="row between">
                        <strong className="xs" style={{ color: "var(--navy-900)" }}>09:10 EHR History Import</strong>
                        <span className="prov prov-imported">Verified EHR</span>
                      </div>
                      <div className="xs subtle" style={{ marginTop: 2 }}>
                        Essential Hypertension • Heart Failure NYHA II • Amlodipine 10mg daily
                      </div>
                    </div>
                  </div>
                </div>

                {/* Column B: AI Synthesis, Uncertainty & Clinician Authority Gate */}
                <div className="preview-subpanel">
                  <div className="preview-subpanel-title">
                    <Stethoscope style={{ width: 13, height: 13, color: "var(--navy-800)" }} aria-hidden="true" />
                    <span>CLINICAL SUMMARY & DECISION GATE</span>
                  </div>

                  {/* Missing Information / Epistemic Uncertainty Audit */}
                  <div className="preview-gap-box">
                    <div className="row gap-1" style={{ color: "var(--warning-text)", fontWeight: 600, fontSize: "0.6875rem" }}>
                      <AlertTriangle style={{ width: 12, height: 12 }} aria-hidden="true" />
                      <span>EPISTEMIC GAP AUDIT</span>
                    </div>
                    <ul className="xs muted stack gap-1" style={{ margin: "4px 0 0", paddingLeft: 14 }}>
                      <li>Serum creatinine / renal panel missing within past 6 months</li>
                      <li>Diuretic compliance unconfirmed by accompanying caregiver</li>
                    </ul>
                  </div>

                  {/* AI Summary Draft */}
                  <div className="preview-summary-box">
                    <div className="row between">
                      <span className="xs strong" style={{ color: "var(--teal-700)" }}>AI Synthesis Draft</span>
                      <span className="badge badge-teal" style={{ fontSize: "10px", height: "18px" }}>Advisory</span>
                    </div>
                    <p className="xs subtle" style={{ margin: "4px 0 0", lineHeight: 1.4 }}>
                      Presentation aligns with acute decompensated chronic heart failure triggered by hypertensive urgency. Moderate acute risk flagged.
                    </p>
                  </div>

                  {/* Non-Delegable Clinician Gate */}
                  <div className="preview-decision-gate">
                    <div className="row between">
                      <div className="stack">
                        <span className="xs strong" style={{ color: "var(--navy-900)" }}>Clinician Decision Gate</span>
                        <span style={{ fontSize: "11px", color: "var(--text-3)" }}>Dr. J. Ajose, MD (Medical Officer)</span>
                      </div>
                      <span className="badge badge-warning" style={{ fontSize: "10px", height: "18px" }}>
                        Action Required
                      </span>
                    </div>
                    <div style={{ marginTop: 8 }}>
                      <div className="preview-decision-status-pill">
                        <CheckCircle2 style={{ width: 13, height: 13, color: "var(--teal-600)" }} aria-hidden="true" />
                        <span>Physician Sign-off Required (Protected Action)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Framing Disclaimer */}
              <div className="preview-footer-note">
                <CheckCircle2 style={{ width: 12, height: 12, color: "var(--teal-600)" }} aria-hidden="true" />
                <span>Demonstration data (CASE-SYNTH-003). Decision authority remains with licensed clinician.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
