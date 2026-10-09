import React from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  Building2,
  Stethoscope,
  UserCheck,
  AlertOctagon,
} from "lucide-react";

export default function HomePage() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-10)", padding: "var(--clinova-space-4) 0" }}>
      {/* 1. HERO SECTION */}
      <section
        style={{
          textAlign: "center",
          maxWidth: 920,
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "var(--clinova-space-4)",
        }}
      >
        <div
          className="clinova-badge"
          style={{
            backgroundColor: "var(--clinova-accent-light)",
            color: "var(--clinova-accent-text)",
            borderColor: "var(--clinova-accent-border)",
            padding: "4px 12px",
            fontSize: "0.75rem",
          }}
        >
          <Activity style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Continuous Care Intelligence Platform</span>
        </div>

        <h1
          style={{
            fontSize: "2.75rem",
            fontWeight: 800,
            lineHeight: 1.15,
            color: "var(--clinova-text-primary)",
            letterSpacing: "-0.03em",
          }}
        >
          From Isolated Triage to <br />
          <span style={{ color: "var(--clinova-accent)" }}>Continuous Care Intelligence</span>
        </h1>

        <p
          style={{
            fontSize: "1.125rem",
            color: "var(--clinova-text-secondary)",
            lineHeight: 1.6,
            maxWidth: 780,
          }}
        >
          CLINOVA AI connects <strong>Patient Risk</strong>, <strong>Evidence Uncertainty</strong>,{" "}
          <strong>Facility Capability</strong>, <strong>System Demand</strong>, and <strong>Outcomes</strong>{" "}
          to identify the <strong>Safest Achievable Care Pathway</strong> while keeping qualified
          healthcare professionals strictly in control.
        </p>

        {/* CTA Launch Buttons into 3 Core Workbenches */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: 12,
            marginTop: 8,
          }}
        >
          <Link
            href="/staff/triage"
            className="clinova-btn clinova-btn-primary clinova-btn-lg"
            style={{ textDecoration: "none" }}
          >
            <UserCheck style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Nurse Triage Workstation</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>

          <Link
            href="/staff/cases/CASE-SYNTH-003"
            className="clinova-btn clinova-btn-secondary clinova-btn-lg"
            style={{ textDecoration: "none" }}
          >
            <Stethoscope style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Doctor Reviewer Workbench</span>
          </Link>

          <Link
            href="/patient/intake"
            className="clinova-btn clinova-btn-outline clinova-btn-lg"
            style={{ textDecoration: "none" }}
          >
            <Activity style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Patient Intake Portal</span>
          </Link>
        </div>
      </section>

      {/* 2. THREE APPROVED CORE WORKBENCHES SHOWCASE */}
      <section style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
        <div style={{ textAlign: "center" }}>
          <span className="clinova-label">CORE OPERATIONAL INTERFACES</span>
          <h2 style={{ fontSize: "1.75rem", marginTop: 4 }}>
            Three Cohesive Clinical Workbenches
          </h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-muted)", marginTop: 2 }}>
            Connected to a single unified CLINOVA Master Case data model.
          </p>
        </div>

        <div className="clinova-grid-3col">
          {/* Workbench A: Patient Intake */}
          <div
            className="clinova-card"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--clinova-accent)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Activity style={{ width: 20, height: 20, color: "var(--clinova-accent)" }} aria-hidden="true" />
                <h3 style={{ fontSize: "1.125rem" }}>Patient Intake Portal</h3>
              </div>
              <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
                Patient-facing structured demographic capture, multi-language speech transcription, adaptive questions to reduce epistemic gaps, and optional prescription uploads.
              </p>
              <ul style={{ paddingLeft: 18, fontSize: "0.8125rem", color: "var(--clinova-text-muted)", display: "flex", flexDirection: "column", gap: 4 }}>
                <li>Informative digital consent & zero PII</li>
                <li>Vernacular Odia, Hindi, and English</li>
                <li>Adaptive uncertainty-reducing inquiries</li>
              </ul>
            </div>
            <div style={{ marginTop: 16 }}>
              <Link href="/patient/intake" className="clinova-btn clinova-btn-outline clinova-btn-sm" style={{ textDecoration: "none", width: "100%" }}>
                <span>Launch Patient Portal</span>
                <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Workbench B: Nurse Triage */}
          <div
            className="clinova-card"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--clinova-warning)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <UserCheck style={{ width: 20, height: 20, color: "var(--clinova-warning)" }} aria-hidden="true" />
                <h3 style={{ fontSize: "1.125rem" }}>Nurse Triage Workstation</h3>
              </div>
              <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
                High-density operational triage worklist monitoring composite risk scores, waiting SLA targets, bedside vital sign acquisition, and red-flag acute shock alarms.
              </p>
              <ul style={{ paddingLeft: 18, fontSize: "0.8125rem", color: "var(--clinova-text-muted)", display: "flex", flexDirection: "column", gap: 4 }}>
                <li>Color + icon multi-attribute acuity tags</li>
                <li>Wait time SLA tracking & breach alerts</li>
                <li>Emergency fast-track bay diversion</li>
              </ul>
            </div>
            <div style={{ marginTop: 16 }}>
              <Link href="/staff/triage" className="clinova-btn clinova-btn-outline clinova-btn-sm" style={{ textDecoration: "none", width: "100%" }}>
                <span>Launch Nurse Queue</span>
                <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Workbench C: Doctor Reviewer */}
          <div
            className="clinova-card"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid #0f766e",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Stethoscope style={{ width: 20, height: 20, color: "#0f766e" }} aria-hidden="true" />
                <h3 style={{ fontSize: "1.125rem" }}>Doctor Reviewer Workbench</h3>
              </div>
              <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
                3-panel asymmetric workstation for definitive clinician review. Examines timeline evidence with provenance, inspects epistemic uncertainty, and executes clinical decisions.
              </p>
              <ul style={{ paddingLeft: 18, fontSize: "0.8125rem", color: "var(--clinova-text-muted)", display: "flex", flexDirection: "column", gap: 4 }}>
                <li>Full source provenance badges & audit trail</li>
                <li>Epistemic gap & conflict highlight controls</li>
                <li>Strict human-in-the-loop decision gate</li>
              </ul>
            </div>
            <div style={{ marginTop: 16 }}>
              <Link href="/staff/cases/CASE-SYNTH-003" className="clinova-btn clinova-btn-outline clinova-btn-sm" style={{ textDecoration: "none", width: "100%" }}>
                <span>Launch Doctor Workbench</span>
                <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3. CENTRAL CLINICAL CARE INTELLIGENCE MODEL */}
      <section
        className="clinova-card"
        style={{
          backgroundColor: "var(--clinova-surface)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--clinova-space-4)",
        }}
      >
        <div>
          <span className="clinova-label">THE MASTER CASE CONTINUOUS LOOP</span>
          <h2 style={{ fontSize: "1.375rem", marginTop: 4 }}>
            Evidence Grounding Before Clinical Action
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
            gap: 8,
            textAlign: "center",
          }}
        >
          {[
            { step: "1. PATIENT", label: "Multimodal Intake" },
            { step: "2. EVIDENCE", label: "Provenance Tags" },
            { step: "3. TIMELINE", label: "Chronological Progression" },
            { step: "4. GAPS", label: "Missing Info Audit" },
            { step: "5. ADAPTIVE", label: "Targeted Questions" },
            { step: "6. UNCERTAINTY", label: "Epistemic Score" },
            { step: "7. REVIEW", label: "Clinician Authority" },
            { step: "8. PATHWAY", label: "Safest Care Route" },
            { step: "9. REFERRAL", label: "Facility Handoff" },
            { step: "10. OUTCOME", label: "Continuous Quality" },
          ].map((item, idx) => (
            <div
              key={idx}
              style={{
                border: "1px solid var(--clinova-border)",
                borderRadius: "var(--clinova-radius-md)",
                padding: "8px 4px",
                backgroundColor: "var(--clinova-surface-subtle)",
              }}
            >
              <strong style={{ fontSize: "0.6875rem", color: "var(--clinova-accent-text)", display: "block" }}>
                {item.step}
              </strong>
              <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-primary)", fontWeight: 600 }}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 4. GOVERNANCE & ARCHITECTURAL INVARIANTS */}
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "var(--clinova-space-4)",
        }}
      >
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ShieldCheck style={{ width: 18, height: 18, color: "var(--clinova-success)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>Zero-PII & Statutory Compliance</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Full statutory alignment with India&apos;s DPDP Act 2023 and NMC RMP Regulations 2023. Zero personal identifiers transmitted to public APIs.
          </p>
        </div>

        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Building2 style={{ width: 18, height: 18, color: "var(--clinova-informational)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>₹0 Zero-Cost Production Stack</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Engineered exclusively on self-hostable open technologies. Zero required paid API subscriptions for core clinical triage, vital risk scoring, or referral routing.
          </p>
        </div>

        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertOctagon style={{ width: 18, height: 18, color: "var(--clinova-emergency)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9375rem" }}>Paschim Banga Doctrine</h4>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
            Supreme Court constitutional emergency doctrine. Administrative completion cannot delay clinical resuscitation in life-threatening presentations.
          </p>
        </div>
      </section>
    </div>
  );
}