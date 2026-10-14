"use client";

import React from "react";
import {
  Building2,
  ShieldCheck,
  HeartPulse,
  Radio,
  FileCheck,
} from "lucide-react";

export const InnovationLayersSection: React.FC = () => {
  return (
    <section
      id="intelligence"
      tabIndex={-1}
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface-sunken)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="intelligence-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 820, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            TRI-GRAPH PRODUCT ARCHITECTURE
          </div>
          <h2
            id="intelligence-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            CLINOVA&apos;s Three Innovation Layers
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            A multi-layered architectural model connecting patient clinical evidence to regional facility resources and longitudinal network surveillance.
          </p>
        </div>

        {/* 3 Asymmetric Innovation Layer Showcases */}
        <div className="stack gap-6">
          {/* Layer 1: CAREGRAPH */}
          <div
            className="card"
            style={{
              padding: "var(--clinova-space-6)",
              backgroundColor: "var(--surface)",
              boxShadow: "var(--shadow-sm)",
              borderTop: "4px solid var(--teal-600)",
            }}
          >
            <div className="landing-innovation-card-grid">
              <div className="stack gap-3">
                <div className="row gap-2">
                  <span className="badge badge-teal">Layer 1 • Clinical Knowledge</span>
                  <span className="xs muted">Implemented & Core Engine</span>
                </div>
                <h3 style={{ fontSize: "1.5rem", color: "var(--navy-900)", margin: 0 }}>
                  CAREGRAPH: Patient Evidence & Trajectory
                </h3>
                <p style={{ fontSize: "0.9375rem", color: "var(--text)", lineHeight: 1.6, margin: 0 }}>
                  CAREGRAPH represents the relationship between patient-reported symptoms, objective bedside vitals, chronological timeline progression, epistemic uncertainty flags, and clinician review gates.
                </p>
                <ul className="xs muted stack gap-2" style={{ paddingLeft: 18, lineHeight: 1.5 }}>
                  <li>
                    <strong>Provenance Traceability:</strong> Every piece of evidence explicitly references its origin modality (Patient Audio, Clinician Note, EHR, or Monitor).
                  </li>
                  <li>
                    <strong>Epistemic Uncertainty:</strong> Distinguishes verified facts from unconfirmed medication dosages and missing lab investigations.
                  </li>
                  <li>
                    <strong>Deterministic Risk Scores:</strong> Dual-engine NEWS2 & Shock Index calculations that operate deterministically without LLM hallucination.
                  </li>
                  <li>
                    <strong>Clinician Authority Gate:</strong> Medical Officer authenticates differential risks before care plan dispatch.
                  </li>
                </ul>
              </div>

              {/* Visual Node Diagram for CAREGRAPH */}
              <div
                style={{
                  backgroundColor: "var(--surface-sunken)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                <div className="row between">
                  <strong className="xs" style={{ color: "var(--navy-900)" }}>
                    CAREGRAPH Node Topology (CASE-SYNTH-003)
                  </strong>
                  <span className="xs muted">Active Graph</span>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    fontSize: "0.75rem",
                  }}
                >
                  <div
                    style={{
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--surface)",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div className="row gap-2">
                      <span className="prov prov-reported">Voice Audio</span>
                      <span style={{ fontWeight: 600 }}>“Shortness of breath on exertion”</span>
                    </div>
                    <span className="xs subtle">Provenance: Patient</span>
                  </div>

                  <div style={{ textAlign: "center", color: "var(--text-4)", fontSize: "11px" }}>
                    ↓ connects to timeline ↓
                  </div>

                  <div
                    style={{
                      border: "1px solid #fed7aa",
                      backgroundColor: "#fffaf5",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div className="row gap-2">
                      <span className="prov prov-missing">Gap Flag</span>
                      <span style={{ fontWeight: 600 }}>No serum creatinine on record</span>
                    </div>
                    <span className="xs subtle" style={{ color: "var(--warning-text)" }}>Epistemic Uncertainty</span>
                  </div>

                  <div style={{ textAlign: "center", color: "var(--text-4)", fontSize: "11px" }}>
                    ↓ evaluated against bedside vitals ↓
                  </div>

                  <div
                    style={{
                      border: "1px solid var(--teal-200, #99f6e4)",
                      backgroundColor: "var(--teal-50)",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div className="row gap-2">
                      <HeartPulse style={{ width: 14, height: 14, color: "var(--teal-700)" }} />
                      <span style={{ fontWeight: 600 }}>NEWS2: 6 (Moderate Risk)</span>
                    </div>
                    <span className="badge badge-teal" style={{ fontSize: "10px", height: "18px" }}>Deterministic Guardrail</span>
                  </div>

                  <div style={{ textAlign: "center", color: "var(--text-4)", fontSize: "11px" }}>
                    ↓ human-in-the-loop review ↓
                  </div>

                  <div
                    style={{
                      border: "1.5px solid var(--navy-800)",
                      backgroundColor: "var(--navy-50)",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div className="row gap-2">
                      <ShieldCheck style={{ width: 14, height: 14, color: "var(--navy-800)" }} />
                      <span style={{ fontWeight: 700, color: "var(--navy-900)" }}>Attending Physician Decision Gate</span>
                    </div>
                    <span className="badge badge-navy" style={{ fontSize: "10px", height: "18px" }}>Signed by MD</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Layer 2: FACILITYGRAPH */}
          <div
            className="card"
            style={{
              padding: "var(--clinova-space-6)",
              backgroundColor: "var(--surface)",
              boxShadow: "var(--shadow-sm)",
              borderTop: "4px solid var(--info)",
            }}
          >
            <div className="landing-innovation-card-grid">
              <div className="stack gap-3">
                <div className="row gap-2">
                  <span className="badge badge-info">Layer 2 • Resource Telemetry</span>
                  <span className="xs muted">Implemented & Integrated</span>
                </div>
                <h3 style={{ fontSize: "1.5rem", color: "var(--navy-900)", margin: 0 }}>
                  FACILITYGRAPH: Resource Feasibility & Transfer Handoff
                </h3>
                <p style={{ fontSize: "0.9375rem", color: "var(--text)", lineHeight: 1.6, margin: 0 }}>
                  FACILITYGRAPH maintains live telemetry of regional hospital resources — bed occupancy, ICU ventilator capacity, oxygen manifold pressure, and surgical capability flags. When transfer is clinically warranted, it assesses receiving hospital feasibility.
                </p>
                <ul className="xs muted stack gap-2" style={{ paddingLeft: 18, lineHeight: 1.5 }}>
                  <li>
                    <strong>Dynamic Transfer Feasibility:</strong> Checks whether destination facility has the exact specialized bed and oxygen capability required before dispatch.
                  </li>
                  <li>
                    <strong>Structured SBAR Dispatch:</strong> Generates standardized Situation, Background, Assessment, Recommendation handoff packets for seamless transit.
                  </li>
                  <li>
                    <strong>Network Visibility:</strong> Connects primary community health centers to district headquarters (e.g. Cuttack DHH) and tertiary medical centers.
                  </li>
                </ul>
              </div>

              {/* Visual Telemetry Card for FACILITYGRAPH */}
              <div
                style={{
                  backgroundColor: "var(--surface-sunken)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                <div className="row between">
                  <div className="row gap-2">
                    <Building2 style={{ width: 14, height: 14, color: "var(--info)" }} />
                    <strong className="xs" style={{ color: "var(--navy-900)" }}>
                      Regional Facility Telemetry Hub
                    </strong>
                  </div>
                  <span className="badge badge-success" style={{ fontSize: "10px", height: "18px" }}>Live Feed</span>
                </div>

                <div className="stack gap-2">
                  <div
                    style={{
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--surface)",
                      borderRadius: "var(--r-sm)",
                      padding: "10px 12px",
                    }}
                  >
                    <div className="row between">
                      <strong style={{ fontSize: "0.8125rem", color: "var(--navy-900)" }}>
                        Cuttack District Headquarters Hospital (FAC-DH-04)
                      </strong>
                      <span className="badge badge-teal" style={{ fontSize: "10px" }}>Origin Facility</span>
                    </div>
                    <div className="row gap-3 wrap" style={{ marginTop: 6, fontSize: "0.6875rem", color: "var(--text-3)" }}>
                      <span>General Beds: <strong>88/120</strong></span>
                      <span>•</span>
                      <span>ICU Beds: <strong>4 Available</strong></span>
                      <span>•</span>
                      <span>Oxygen: <strong>Normal (94 psi)</strong></span>
                    </div>
                  </div>

                  <div
                    style={{
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--surface)",
                      borderRadius: "var(--r-sm)",
                      padding: "10px 12px",
                    }}
                  >
                    <div className="row between">
                      <strong style={{ fontSize: "0.8125rem", color: "var(--navy-900)" }}>
                        SCB Medical College & Hospital (FAC-TER-01)
                      </strong>
                      <span className="badge badge-info" style={{ fontSize: "10px" }}>Receiving Center</span>
                    </div>
                    <div className="row gap-3 wrap" style={{ marginTop: 6, fontSize: "0.6875rem", color: "var(--text-3)" }}>
                      <span>Tertiary ICU: <strong>7 Beds</strong></span>
                      <span>•</span>
                      <span>Cath Lab: <strong>Operational</strong></span>
                      <span>•</span>
                      <span>SBAR Transit: <strong>Approved</strong></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Layer 3: SIGNALGRAPH */}
          <div
            className="card"
            style={{
              padding: "var(--clinova-space-6)",
              backgroundColor: "var(--surface)",
              boxShadow: "var(--shadow-sm)",
              borderTop: "4px solid #6366f1",
            }}
          >
            <div className="landing-innovation-card-grid">
              <div className="stack gap-3">
                <div className="row gap-2">
                  <span className="badge badge-purple">Layer 3 • Longitudinal Surveillance</span>
                  <span className="xs muted">Outcome Intelligence Engine</span>
                </div>
                <h3 style={{ fontSize: "1.5rem", color: "var(--navy-900)", margin: 0 }}>
                  SIGNALGRAPH: Closed-Loop Outcome Telemetry
                </h3>
                <p style={{ fontSize: "0.9375rem", color: "var(--text)", lineHeight: 1.6, margin: 0 }}>
                  SIGNALGRAPH captures permitted follow-up observations and clinical disposition outcomes to build continuous workflow intelligence, detect disease clusters, and measure care plan efficacy across institutions.
                </p>
                <ul className="xs muted stack gap-2" style={{ paddingLeft: 18, lineHeight: 1.5 }}>
                  <li>
                    <strong>Closed-Loop Feedback:</strong> Records post-consultation outcomes (admitted, discharged, transferred, resolved) to refine future risk models.
                  </li>
                  <li>
                    <strong>Syndromic Surveillance:</strong> Aggregates anonymized symptom clusters across health districts to spot regional health anomalies early.
                  </li>
                  <li>
                    <strong>Privacy Preserving:</strong> Operates strictly under DPDP Act 2023 with cryptographic de-identification and zero commercial data sharing.
                  </li>
                </ul>
              </div>

              {/* Visual Telemetry Card for SIGNALGRAPH */}
              <div
                style={{
                  backgroundColor: "var(--surface-sunken)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                <div className="row between">
                  <div className="row gap-2">
                    <Radio style={{ width: 14, height: 14, color: "#6366f1" }} />
                    <strong className="xs" style={{ color: "var(--navy-900)" }}>
                      Continuous Surveillance & Disposition Feed
                    </strong>
                  </div>
                  <span className="xs muted">Aggregated Signal</span>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 140px), 1fr))",
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--surface)",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                    }}
                  >
                    <span className="xs muted">Follow-up Disposition</span>
                    <div style={{ fontSize: "0.9375rem", fontWeight: 700, color: "var(--navy-900)", marginTop: 2 }}>
                      Closed-Loop Tracking
                    </div>
                    <span className="xs" style={{ color: "var(--teal-700)" }}>Outcome Audited</span>
                  </div>

                  <div
                    style={{
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--surface)",
                      borderRadius: "var(--r-sm)",
                      padding: "8px 10px",
                    }}
                  >
                    <span className="xs muted">Syndromic Surveillance</span>
                    <div style={{ fontSize: "0.9375rem", fontWeight: 700, color: "var(--navy-900)", marginTop: 2 }}>
                      Cluster Telemetry
                    </div>
                    <span className="xs" style={{ color: "var(--info)" }}>District Signal</span>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: "var(--surface)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--r-sm)",
                    padding: "8px 10px",
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <FileCheck style={{ width: 16, height: 16, color: "var(--teal-600)", flexShrink: 0 }} />
                  <span style={{ fontSize: "0.75rem", color: "var(--text-2)" }}>
                    Immutable SHA-256 chained audit logs preserve complete longitudinal evidence for clinical governance.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
