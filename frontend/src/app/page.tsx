import React from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  Building2,
  Stethoscope,
  UserCheck,
  UserPlus,
  AlertOctagon,
  Share2,
  FileCheck2,
  Lock,
  Layers,
  HeartPulse,
} from "lucide-react";

export default function HomePage() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-10)", padding: "var(--clinova-space-4) 0" }}>
      {/* 1. HERO SECTION */}
      <section
        style={{
          textAlign: "center",
          maxWidth: 960,
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "var(--clinova-space-4)",
        }}
      >
        <div
          className="badge badge-teal"
          style={{
            padding: "4px 14px",
            fontSize: "var(--fs-xs)",
            fontWeight: 600,
          }}
        >
          <Activity style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Continuous Care Intelligence Platform</span>
        </div>

        <h1
          style={{
            fontSize: "3rem",
            fontWeight: 800,
            lineHeight: 1.15,
            color: "var(--navy-900)",
            letterSpacing: "-0.03em",
          }}
        >
          From Isolated Triage to <br />
          <span style={{ color: "var(--teal-600)" }}>Continuous Care Intelligence</span>
        </h1>

        <p
          style={{
            fontSize: "1.125rem",
            color: "var(--text-2)",
            lineHeight: 1.6,
            maxWidth: 820,
          }}
        >
          CLINOVA AI connects <strong>Patient Risk</strong>, <strong>Evidence Uncertainty</strong>,{" "}
          <strong>Facility Capability</strong>, <strong>System Demand</strong>, and <strong>Outcomes</strong>{" "}
          to identify the <strong>Safest Achievable Care Pathway</strong> while keeping qualified
          healthcare professionals strictly in control.
        </p>

        {/* Quick Launch Buttons into Key Operational Surfaces */}
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
            href="/staff/reception"
            className="btn btn-primary btn-lg"
          >
            <UserPlus style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Reception Desk</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>

          <Link
            href="/staff/triage"
            className="btn btn-secondary btn-lg"
          >
            <UserCheck style={{ width: 18, height: 18, color: "var(--warning)" }} aria-hidden="true" />
            <span>Nurse Triage Workstation</span>
          </Link>

          <Link
            href="/staff/cases/CASE-SYNTH-003"
            className="btn btn-accent btn-lg"
          >
            <Stethoscope style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Doctor Workbench</span>
          </Link>

          <Link
            href="/patient/intake"
            className="btn btn-ghost btn-lg"
            style={{ border: "1px solid var(--border-strong)" }}
          >
            <Activity style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
            <span>Patient Intake</span>
          </Link>
        </div>
      </section>

      {/* 2. SIX DISTINCT ROLE WORKSPACES SHOWCASE */}
      <section style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
        <div style={{ textAlign: "center" }}>
          <span className="section-title">ROLE-BASED GOVERNANCE & ARCHITECTURE</span>
          <h2 style={{ fontSize: "1.875rem", marginTop: 4, color: "var(--navy-900)" }}>
            Six Distinct Role Experiences
          </h2>
          <p style={{ fontSize: "0.875rem", color: "var(--text-3)", marginTop: 2 }}>
            Strict role-based isolation, authentic access control, and specialized workflows for every member of the care continuum.
          </p>
        </div>

        <div className="grid grid-3 gap-4">
          {/* Role 1: Patient */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--teal-600)",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <Activity style={{ width: 20, height: 20, color: "var(--teal-600)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>A. Patient Portal</h3>
                </div>
                <span className="badge badge-teal">Patient</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                Digital intake, multilingual vernacular entry (Odia/Hindi/English), personal case token status tracking, and doctor-approved care-plan instructions with mobile SMS previews.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Informative digital consent & zero PII</li>
                <li>Strict patient record boundary isolation</li>
                <li>Follow-up appointments & medication guidance</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/patient" className="btn btn-secondary btn-sm btn-block">
                <span>Access Patient Portal</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Role 2: Receptionist */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--navy-800)",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <UserPlus style={{ width: 20, height: 20, color: "var(--navy-800)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>B. Receptionist Desk</h3>
                </div>
                <span className="badge badge-navy">Receptionist</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                Patient registration, identity demographic capture, DPDP Act 2023 consent recording, and staff-directed clinical pathway assignment (Regular OPD vs Emergency).
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Find or create patient records</li>
                <li>Staff-assigned initial pathway routing</li>
                <li>Zero autonomous medical diagnoses</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/staff/reception" className="btn btn-primary btn-sm btn-block">
                <span>Access Reception Desk</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Role 3: Nurse */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--warning)",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <UserCheck style={{ width: 20, height: 20, color: "var(--warning)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>C. Nurse Triage</h3>
                </div>
                <span className="badge badge-warning">Triage Nurse</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                Operational triage worklist monitoring composite risk scores, NEWS2 bedside vital sign acquisition, red-flag acute shock alarms, and SLA wait-time breach alerts.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Color + icon multi-attribute acuity tags</li>
                <li>NEWS2 & Shock Index real-time compute</li>
                <li>Emergency fast-track bay diversion</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/staff/triage" className="btn btn-secondary btn-sm btn-block">
                <span>Access Triage Workstation</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Role 4: Clinician / Medical Officer */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid #0f766e",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <Stethoscope style={{ width: 20, height: 20, color: "#0f766e" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>D. Doctor Workbench</h3>
                </div>
                <span className="badge badge-teal">Clinician / Doctor</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                3-panel asymmetric workstation for definitive clinician review. Examines timeline evidence with provenance, epistemic uncertainty meters, conflict resolution, and authoritative sign-off.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Provenance badges & epistemic gap audit</li>
                <li>Review queue with batch verification</li>
                <li>Strict human clinician decision gate</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/staff/cases/CASE-SYNTH-003" className="btn btn-accent btn-sm btn-block">
                <span>Access Doctor Workbench</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Role 5: Facility Administrator */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid var(--info)",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <Building2 style={{ width: 20, height: 20, color: "var(--info)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>E. Facility Admin</h3>
                </div>
                <span className="badge badge-info">Facility Admin</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                FacilityGraph resource management: bed occupancy, ICU ventilator capacity, oxygen telemetry, capability flags, and referral coordination with SBAR transfer packet dispatch.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Regional receiving center telemetry</li>
                <li>SBAR structured transfer coordination</li>
                <li>Isolated to designated facility scope</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/facilities" className="btn btn-secondary btn-sm btn-block">
                <span>Access Facility Operations</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Role 6: System Administrator */}
          <div
            className="card interactive"
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: "4px solid #475569",
            }}
          >
            <div className="card-body stack gap-2">
              <div className="row between">
                <div className="row gap-2">
                  <ShieldCheck style={{ width: 20, height: 20, color: "#475569" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>F. System Admin</h3>
                </div>
                <span className="badge badge-navy">System Admin</span>
              </div>
              <p className="small subtle" style={{ margin: 0 }}>
                Platform health monitoring, cryptographic SHA-256 chained security audit ledger, offline edge synchronization queue status, integration health, and compliance verification.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Immutable security audit trail</li>
                <li>Offline sync queue & conflict inspection</li>
                <li>Zero clinical authority bypass</li>
              </ul>
            </div>
            <div className="card-footer">
              <Link href="/system" className="btn btn-secondary btn-sm btn-block">
                <span>Access System Console</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3. CENTRAL CLINICAL CARE INTELLIGENCE MODEL (13-STAGE CONTINUOUS LOOP) */}
      <section
        className="card"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--clinova-space-4)",
          padding: "var(--clinova-space-6)",
        }}
      >
        <div>
          <span className="section-title">THE 13-STAGE MASTER CASE CONTINUOUS LOOP</span>
          <h2 style={{ fontSize: "1.5rem", marginTop: 4, color: "var(--navy-900)" }}>
            Connected Clinical Care Journey
          </h2>
          <p className="xs muted" style={{ marginTop: 2 }}>
            Rigorous evidence grounding and deterministic safety checks before every clinical recommendation.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: 10,
            textAlign: "center",
          }}
        >
          {[
            { step: "1. ENTRY", label: "Public / Portal Entry" },
            { step: "2. CONSENT", label: "DPDP Act Digital Consent" },
            { step: "3. PATHWAY", label: "Staff-Assigned Pathway" },
            { step: "4. INTAKE", label: "Symptoms & Evidence" },
            { step: "5. EXTRACTION", label: "Provenance & Uncertainty" },
            { step: "6. TIMELINE", label: "Chronological Progression" },
            { step: "7. ADAPTIVE", label: "Targeted Inquiries" },
            { step: "8. CAREGRAPH", label: "Risk & Trajectory" },
            { step: "9. SAFETY", label: "Deterministic Alarms" },
            { step: "10. REVIEW", label: "Clinician Authority" },
            { step: "11. FACILITY", label: "SBAR Referral" },
            { step: "12. OUTCOME", label: "Outcome Capture" },
            { step: "13. SIGNAL", label: "SignalGraph Telemetry" },
          ].map((item, idx) => (
            <div
              key={item.step}
              style={{
                border: "1px solid var(--border)",
                borderRadius: "var(--r-md)",
                padding: "10px 6px",
                backgroundColor: "var(--surface-sunken)",
                display: "flex",
                flexDirection: "column",
                gap: 4,
              }}
            >
              <strong style={{ fontSize: "0.6875rem", color: "var(--teal-700)" }}>
                {item.step}
              </strong>
              <span style={{ fontSize: "0.75rem", color: "var(--text)", fontWeight: 600 }}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 4. CLINICAL GOVERNANCE & STATUTORY PILLARS */}
      <section className="grid grid-3 gap-4">
        <div className="card">
          <div className="card-body tight stack gap-2">
            <div className="row gap-2">
              <ShieldCheck style={{ width: 18, height: 18, color: "var(--success)" }} aria-hidden="true" />
              <h4 style={{ fontSize: "0.9375rem", margin: 0 }}>Zero-PII & Statutory Compliance</h4>
            </div>
            <p className="xs subtle" style={{ margin: 0, lineHeight: 1.5 }}>
              Full statutory alignment with India&apos;s DPDP Act 2023 and NMC RMP Regulations 2023. Zero personal health identifiers transmitted to commercial third-party APIs.
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-body tight stack gap-2">
            <div className="row gap-2">
              <Building2 style={{ width: 18, height: 18, color: "var(--info)" }} aria-hidden="true" />
              <h4 style={{ fontSize: "0.9375rem", margin: 0 }}>₹0 Zero-Cost Production Stack</h4>
            </div>
            <p className="xs subtle" style={{ margin: 0, lineHeight: 1.5 }}>
              Engineered exclusively on self-hostable open technologies. Zero required paid API subscriptions for core clinical triage, vital risk scoring, or referral routing.
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-body tight stack gap-2">
            <div className="row gap-2">
              <AlertOctagon style={{ width: 18, height: 18, color: "var(--error)" }} aria-hidden="true" />
              <h4 style={{ fontSize: "0.9375rem", margin: 0 }}>Paschim Banga Doctrine</h4>
            </div>
            <p className="xs subtle" style={{ margin: 0, lineHeight: 1.5 }}>
              Supreme Court constitutional emergency doctrine. Administrative delays or lacking paperwork must never prevent clinical resuscitation in life-threatening conditions.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}