"use client";

import React from "react";
import {
  FileText,
  AlertTriangle,
} from "lucide-react";

export const ReportShowcaseSection: React.FC = () => {
  return (
    <section
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="reports-main-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 840, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            DOCUMENTATION & CARE CONTINUITY
          </div>
          <h2
            id="reports-main-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            Authorized Reports & Care Continuity
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            How clinical evidence, AI-assisted summaries, and attending physician decisions are consolidated into an authorized, non-repudiable medical report.
          </p>
        </div>

        {/* Realistic High-Fidelity Report Document Mockup */}
        <div
          style={{
            maxWidth: 920,
            margin: "0 auto",
            backgroundColor: "var(--surface)",
            border: "1px solid var(--border-strong)",
            borderRadius: "var(--r-lg)",
            boxShadow: "0 8px 30px -4px rgba(13, 33, 53, 0.08)",
            overflow: "hidden",
          }}
        >
          {/* Document Header Bar */}
          <div
            style={{
              backgroundColor: "var(--navy-900)",
              color: "#ffffff",
              padding: "16px 24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 12,
            }}
          >
            <div className="row gap-3">
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "var(--r-sm)",
                  backgroundColor: "rgba(255, 255, 255, 0.12)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <FileText style={{ width: 18, height: 18, color: "var(--teal-100)" }} aria-hidden="true" />
              </div>
              <div>
                <strong style={{ fontSize: "1rem", letterSpacing: "-0.01em", display: "block" }}>
                  Lekki Family Health Clinic • Clinical Encounter Summary
                </strong>
                <span className="xs" style={{ color: "#94a3b8" }}>
                  Case Token: CASE-SYNTH-003 • Encounter Date: 11 October 2026 • Verified PDF-1.4
                </span>
              </div>
            </div>
            <div className="row gap-2">
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 600,
                  backgroundColor: "rgba(15, 157, 145, 0.25)",
                  color: "var(--teal-100)",
                  padding: "3px 8px",
                  borderRadius: "var(--r-full)",
                  border: "1px solid var(--teal-600)",
                }}
              >
                PHYSICIAN AUTHENTICATED
              </span>
            </div>
          </div>

          {/* Document Interior */}
          <div style={{ padding: "24px 28px" }} className="stack gap-4">
            {/* Meta Row */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: 12,
                backgroundColor: "var(--surface-sunken)",
                padding: "12px 16px",
                borderRadius: "var(--r-md)",
                border: "1px solid var(--border)",
              }}
            >
              <div>
                <span className="xs muted medium">Patient Demographics</span>
                <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "var(--navy-900)" }}>
                  Aisha Bello (58F) • ID: PT-SYN-3720
                </div>
              </div>
              <div>
                <span className="xs muted medium">Attending Physician</span>
                <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "var(--navy-900)" }}>
                  Dr. Joshua Ajose, MD (Medical Officer)
                </div>
              </div>
              <div>
                <span className="xs muted medium">Clinical Pathway</span>
                <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "var(--navy-900)" }}>
                  Staff-Assigned Outpatient Acute Review
                </div>
              </div>
            </div>

            {/* Section 1: Patient-Reported Information */}
            <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: 16 }}>
              <div className="row between" style={{ marginBottom: 6 }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  1. Patient-Reported Intake
                </strong>
                <span className="prov prov-reported">Patient Stated (Voice Audio)</span>
              </div>
              <p style={{ fontSize: "0.875rem", color: "var(--text)", margin: 0, lineHeight: 1.5 }}>
                Patient presented reporting worsening breathlessness on minimal exertion and orthopnea requiring elevation on three pillows for the past four days. Bilateral lower limb swelling noticed following dietary salt indiscretion.
              </p>
            </div>

            {/* Section 2: Extracted Evidence & Provenance Table */}
            <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: 16 }}>
              <div className="row between" style={{ marginBottom: 8 }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  2. Objective Evidence & Source Provenance
                </strong>
                <span className="xs muted">Auditable Multi-Source Traceability</span>
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                  gap: 8,
                }}
              >
                <div
                  style={{
                    border: "1px solid var(--border)",
                    padding: "8px 10px",
                    borderRadius: "var(--r-sm)",
                    backgroundColor: "var(--surface-sunken)",
                  }}
                >
                  <div className="row between">
                    <span className="xs muted">Bedside Vitals (08:30)</span>
                    <span className="prov prov-verified">Nurse Verified</span>
                  </div>
                  <div style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--navy-900)", marginTop: 2 }}>
                    BP 142/90 • HR 104 • SpO2 93% (RA) • RR 22/min
                  </div>
                </div>

                <div
                  style={{
                    border: "1px solid var(--border)",
                    padding: "8px 10px",
                    borderRadius: "var(--r-sm)",
                    backgroundColor: "var(--surface-sunken)",
                  }}
                >
                  <div className="row between">
                    <span className="xs muted">Prior Hospital EHR</span>
                    <span className="prov prov-imported">EHR Record</span>
                  </div>
                  <div style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--navy-900)", marginTop: 2 }}>
                    Essential HTN • CHF NYHA II • Amlodipine 10mg
                  </div>
                </div>
              </div>
            </div>

            {/* Section 3: AI-Generated Summary & Uncertainty Disclosure */}
            <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: 16 }}>
              <div className="row between" style={{ marginBottom: 6 }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--teal-700)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  3. AI Advisory Synthesis & Uncertainty Disclosure
                </strong>
                <span className="badge badge-teal" style={{ fontSize: "10px" }}>Advisory Only • Non-Diagnostic</span>
              </div>
              <p style={{ fontSize: "0.8125rem", color: "var(--text)", margin: 0, lineHeight: 1.5 }}>
                Presentation is consistent with acute decompensated chronic heart failure triggered by hypertensive urgency. Dual-engine NEWS2 score: 6 (Moderate Risk).
              </p>
              <div
                style={{
                  marginTop: 6,
                  padding: "6px 10px",
                  borderRadius: "var(--r-sm)",
                  backgroundColor: "#fffbeb",
                  border: "1px solid #fde68a",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <AlertTriangle style={{ width: 14, height: 14, color: "#b45309", flexShrink: 0 }} aria-hidden="true" />
                <span style={{ fontSize: "0.75rem", color: "#92400e" }}>
                  <strong>Epistemic Uncertainty Notice:</strong> Renal function panel not on file within last 6 months. Potassium and creatinine must be verified before titrating diuretics.
                </span>
              </div>
            </div>

            {/* Section 4: Clinician-Authored / Approved Findings */}
            <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: 16 }}>
              <div className="row between" style={{ marginBottom: 6 }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  4. Attending Physician Verified Assessment & Disposition
                </strong>
                <span className="badge badge-navy" style={{ fontSize: "10px" }}>Human Clinician Decision Gate</span>
              </div>
              <p style={{ fontSize: "0.875rem", color: "var(--navy-900)", margin: 0, lineHeight: 1.5, fontWeight: 500 }}>
                Diagnosis confirmed: Acute Decompensated Heart Failure (NYHA Class III). Plan: IV Furosemide 40mg administered; urgent renal panel ordered; continuous telemetry bed admitted to Ward B.
              </p>
              <div className="row between wrap gap-2" style={{ marginTop: 10, fontSize: "0.75rem", color: "var(--text-3)" }}>
                <span>Signed: <strong>Dr. Joshua Ajose, MD</strong> • Registration: LK-2018-9942</span>
                <span>Cryptographic JWT Signature Verified • NMC 2023 Compliant</span>
              </div>
            </div>

            {/* Section 5: Referral & Follow-up Information */}
            <div>
              <div className="row between" style={{ marginBottom: 6 }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  5. Follow-Up Plan & Patient Guidance
                </strong>
                <span className="xs muted">Care Continuity</span>
              </div>
              <p style={{ fontSize: "0.8125rem", color: "var(--text)", margin: 0, lineHeight: 1.5 }}>
                Patient provided vernacular follow-up instructions regarding fluid restriction (1.5L/day), daily morning weight tracking, and red-flag escalation triggers. In-person review scheduled in 5 days.
              </p>
            </div>
          </div>

          {/* Document Framing Notice */}
          <div
            style={{
              backgroundColor: "var(--surface-sunken)",
              borderTop: "1px solid var(--border)",
              padding: "12px 24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 8,
              fontSize: "0.75rem",
              color: "var(--text-3)",
            }}
          >
            <span>
              Report generation occurs exclusively within authenticated clinical workflows. Report content reflects the real encounter state.
            </span>
            <span style={{ fontWeight: 600, color: "var(--navy-900)" }}>
              Synthetic Demo Preview (CASE-SYNTH-003)
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
