"use client";

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
  Sparkles,
  LogIn,
  HeartPulse,
  Scale,
  ShieldAlert,
  Server,
  CheckCircle2,
} from "lucide-react";

export default function HomePage() {
  const platformStats = [
    {
      label: "Production Architecture",
      value: "₹0 Stack",
      note: "100% open-source, self-hostable • Zero paid API fees",
      icon: Server,
      tile: "tile-teal",
    },
    {
      label: "Privacy & Statutory Compliance",
      value: "Zero-PII",
      note: "DPDP Act 2023 & NMC RMP Regulations 2023 aligned",
      icon: ShieldCheck,
      tile: "tile-navy",
    },
    {
      label: "Clinical Guardrails",
      value: "Deterministic",
      note: "Dual-engine NEWS2 & Shock Index vital algorithms",
      icon: HeartPulse,
      tile: "tile-warning",
    },
    {
      label: "Emergency Protocol",
      value: "Paschim Banga",
      note: "Constitutional non-refusal emergency resuscitation",
      icon: AlertOctagon,
      tile: "tile-info",
    },
  ];

  const workflowSteps = [
    {
      step: 1,
      title: "Relevant clinical history is organised",
      desc: "Synthesises previous encounters, chronic conditions, and medication lists without losing source context.",
      actor: "AI",
      actorBadge: "badge-teal",
    },
    {
      step: 2,
      title: "Draft clinical summary is prepared",
      desc: "Calculates deterministic NEWS2 and Shock Index scores, flagging acute physiologic instability instantly.",
      actor: "AI",
      actorBadge: "badge-teal",
    },
    {
      step: 3,
      title: "Missing information is highlighted",
      desc: "Surfaces epistemic uncertainty, unconfirmed allergies, or conflicting medication dosages before physician consult.",
      actor: "AI",
      actorBadge: "badge-teal",
    },
    {
      step: 4,
      title: "Clinician reviews and documents decisions",
      desc: "Physician verifies evidence provenance, adjusts differential risks, and determines definitive clinical disposition.",
      actor: "Clinician",
      actorBadge: "badge-navy",
    },
    {
      step: 5,
      title: "Authoritative note is approved and signed",
      desc: "Non-repudiable physician sign-off adhering strictly to NMC 2023 regulations. System never signs on doctor's behalf.",
      actor: "Clinician",
      actorBadge: "badge-navy",
    },
    {
      step: 6,
      title: "Instructions & SBAR transfer coordinated",
      desc: "Plain-language vernacular instructions generated for patient and hospital transfer handoff dispatched.",
      actor: "AI • Staff Approved",
      actorBadge: "badge-outline",
    },
  ];

  const masterCaseLoopStages = [
    { step: "1. ENTRY", label: "Public / Portal Entry" },
    { step: "2. CONSENT", label: "DPDP Act Digital Consent" },
    { step: "3. PATHWAY", label: "Staff-Assigned Pathway" },
    { step: "4. INTAKE", label: "Symptoms & Evidence" },
    { step: "5. EXTRACTION", label: "Provenance & Uncertainty" },
    { step: "6. TIMELINE", label: "Chronological Progression" },
    { step: "7. ADAPTIVE", label: "Targeted Inquiries" },
    { step: "8. CAREGRAPH", label: "Risk & Trajectory" },
    { step: "9. SAFETY", label: "Deterministic Alarms" },
    { step: "10. REVIEW", label: "Clinician Authority Gate" },
    { step: "11. FACILITY", label: "SBAR Referral" },
    { step: "12. OUTCOME", label: "Outcome Capture & Telemetry" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-8)", padding: "var(--clinova-space-4) 0" }}>
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
        <div className="demo-ribbon demo-ribbon-teal">
          <Sparkles style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />
          <span>AI Clinical Workflow Assistant • Continuous Care Intelligence</span>
        </div>

        <h1
          style={{
            fontSize: "2.75rem",
            fontWeight: 800,
            lineHeight: 1.15,
            color: "var(--navy-900)",
            letterSpacing: "-0.03em",
            margin: 0,
          }}
        >
          Less paperwork. <br />
          <span style={{ color: "var(--teal-600)" }}>More time for patient care.</span>
        </h1>

        <p
          style={{
            fontSize: "1.125rem",
            color: "var(--text-2)",
            lineHeight: 1.6,
            maxWidth: 820,
            margin: 0,
          }}
        >
          CLINOVA AI connects <strong>Patient Risk</strong>, <strong>Evidence Uncertainty</strong>,{" "}
          <strong>Facility Capability</strong>, <strong>System Demand</strong>, and <strong>Outcomes</strong>{" "}
          to identify the <strong>Safest Achievable Care Pathway</strong> — while registered healthcare professionals
          stay strictly in control of every clinical decision.
        </p>

        {/* Public Entry Action CTAs */}
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
          <Link href="/login" className="btn btn-primary btn-lg">
            <LogIn style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Staff Sign In</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>

          <Link href="/patient" className="btn btn-secondary btn-lg">
            <Activity style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
            <span>Patient Portal & Intake</span>
          </Link>

          <a href="#capabilities" className="btn btn-ghost btn-lg" style={{ border: "1px solid var(--border-strong)" }}>
            <ShieldCheck style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Platform Capabilities</span>
          </a>
        </div>
      </section>

      {/* 2. PLATFORM ARCHITECTURAL HIGHLIGHTS & CAPABILITIES */}
      <section id="capabilities" aria-labelledby="platform-stats-heading">
        <h2 id="platform-stats-heading" className="sr-only">Platform Architectural Highlights</h2>
        <div className="grid grid-4 gap-4">
          {platformStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="card metric-card"
                style={{ color: "inherit" }}
              >
                <div className="row between">
                  <span className="small subtle medium">{stat.label}</span>
                  <span className={`icon-tile ${stat.tile}`}>
                    <Icon aria-hidden="true" />
                  </span>
                </div>
                <div className="stat-value" style={{ color: "var(--navy-900)" }}>
                  {stat.value}
                </div>
                <div className="xs muted">{stat.note}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. THE CONTINUOUS CLINICAL WORKFLOW (6-STAGE CONTINUUM) */}
      <section className="card" style={{ padding: "var(--s-6)" }} aria-labelledby="workflow-heading">
        <div style={{ marginBottom: 20 }}>
          <div className="row between wrap gap-2">
            <div>
              <span className="section-title">THE CONTINUOUS CLINICAL WORKFLOW</span>
              <h2 id="workflow-heading" style={{ fontSize: "1.5rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
                How Clinova AI Coordinates Patient Care
              </h2>
            </div>
            <span className="demo-ribbon demo-ribbon-teal">
              Human-in-the-Loop Governance
            </span>
          </div>
          <p className="small muted" style={{ marginTop: 4, maxWidth: 760 }}>
            Structured evidence processing and diagnostic safety bounds. Artificial intelligence organizes clinical history and drafts assessments, but never formulates autonomous diagnoses or replaces physician judgment.
          </p>
        </div>

        <div className="grid grid-3 gap-3">
          {workflowSteps.map((step) => (
            <div key={step.step} className="flow-step-light stack between" style={{ borderRadius: "var(--r-md)" }}>
              <div className="stack gap-2">
                <div className="row between">
                  <span className="n">{step.step}</span>
                  <span className={`badge ${step.actorBadge}`}>{step.actor}</span>
                </div>
                <strong style={{ fontSize: "var(--fs-sm)", color: "var(--navy-900)" }}>
                  {step.title}
                </strong>
                <p className="xs muted" style={{ margin: 0, lineHeight: 1.5 }}>
                  {step.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. SIX SPECIALIZED ROLE WORKSPACES (AUTHENTIC ROLE INGRESS) */}
      <section style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }} aria-labelledby="roles-heading">
        <div style={{ textAlign: "center" }}>
          <span className="section-title">ROLE-BASED GOVERNANCE & ARCHITECTURE</span>
          <h2 id="roles-heading" style={{ fontSize: "1.875rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
            Six Distinct Role Experiences
          </h2>
          <p style={{ fontSize: "0.875rem", color: "var(--text-3)", marginTop: 2 }}>
            Strict role-based isolation, authentic access control, and specialized workspaces for every clinical persona.
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                Digital intake, multilingual vernacular entry (Odia/Hindi/English), personal case token status tracking, and doctor-approved care-plan instructions with mobile SMS previews.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Informative digital consent & zero PII</li>
                <li>Strict patient record boundary isolation</li>
                <li>Follow-up appointments & medication guidance</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />
                <span>Patient-facing self-service & vernacular intake</span>
              </span>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                Patient registration, identity demographic capture, DPDP Act 2023 consent recording, and staff-directed clinical pathway assignment (Regular OPD vs Emergency).
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Find or create patient records</li>
                <li>Staff-assigned initial pathway routing</li>
                <li>Zero autonomous medical diagnoses</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "var(--navy-800)" }} aria-hidden="true" />
                <span>Registration & staff-directed routing only</span>
              </span>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                Operational triage worklist monitoring composite risk scores, NEWS2 bedside vital sign acquisition, red-flag acute shock alarms, and SLA wait-time breach alerts.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Color + icon multi-attribute acuity tags</li>
                <li>NEWS2 & Shock Index real-time compute</li>
                <li>Emergency fast-track bay diversion</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "var(--warning)" }} aria-hidden="true" />
                <span>Vital acquisition & acute clinical scoring</span>
              </span>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                3-panel asymmetric workstation for definitive clinician review. Examines timeline evidence with provenance, epistemic uncertainty meters, conflict resolution, and authoritative sign-off.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Provenance badges & epistemic gap audit</li>
                <li>Review queue with batch verification</li>
                <li>Strict human clinician decision gate</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "#0f766e" }} aria-hidden="true" />
                <span>Authoritative clinical sign-off & human decision gate</span>
              </span>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                FacilityGraph resource management: bed occupancy, ICU ventilator capacity, oxygen telemetry, capability flags, and referral coordination with SBAR transfer packet dispatch.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Regional receiving center telemetry</li>
                <li>SBAR structured transfer coordination</li>
                <li>Isolated to designated facility scope</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "var(--info)" }} aria-hidden="true" />
                <span>Facility-scoped telemetry & regional transfer</span>
              </span>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
                Platform health monitoring, cryptographic SHA-256 chained security audit ledger, offline edge synchronization queue status, integration health, and compliance verification.
              </p>
              <ul className="xs muted stack gap-1" style={{ paddingLeft: 16 }}>
                <li>Immutable security audit trail</li>
                <li>Offline sync queue & conflict inspection</li>
                <li>Zero clinical authority bypass</li>
              </ul>
            </div>
            <div className="card-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 12 }}>
              <span className="xs subtle" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 style={{ width: 14, height: 14, color: "#475569" }} aria-hidden="true" />
                <span>Security audit ledger & zero diagnostic bypass</span>
              </span>
            </div>
          </div>
        </div>

        {/* Role Access Security & Login Gateway Banner */}
        <div
          className="card"
          style={{
            backgroundColor: "var(--surface-sunken)",
            border: "1px solid var(--border-strong)",
            padding: "var(--s-4) var(--s-6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 16,
            borderRadius: "var(--r-md)",
            marginTop: 4,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12, maxWidth: 680 }}>
            <ShieldCheck style={{ width: 28, height: 28, color: "var(--teal-600)", flexShrink: 0 }} aria-hidden="true" />
            <div>
              <strong style={{ fontSize: "0.9375rem", color: "var(--navy-900)", display: "block" }}>
                Role-Based Access Control (RBAC) & Hospital Authentication
              </strong>
              <p className="xs subtle" style={{ margin: 0, lineHeight: 1.4 }}>
                Access to clinical workstations, triage queues, and administrative consoles requires authenticated credentials. Unauthorized bypass is prevented at the network and token boundary.
              </p>
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <Link href="/login" className="btn btn-primary btn-sm">
              <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Sign In to Authorized Workstation</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      {/* 5. THE 12-STAGE MASTER CASE CONTINUOUS LOOP */}
      <section
        className="card"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--clinova-space-4)",
          padding: "var(--clinova-space-6)",
        }}
        aria-labelledby="loop-heading"
      >
        <div>
          <span className="section-title">THE 12-STAGE MASTER CASE CONTINUOUS LOOP</span>
          <h2 id="loop-heading" style={{ fontSize: "1.5rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
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
          {masterCaseLoopStages.map((item) => (
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

      {/* 6. CLINICAL GOVERNANCE & STATUTORY PILLARS */}
      <section className="grid grid-3 gap-4" aria-labelledby="pillars-heading">
        <h2 id="pillars-heading" className="sr-only">Clinical Governance & Statutory Pillars</h2>
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

      {/* 7. STATUTORY CLINICAL NON-DELEGATION NOTICE */}
      <section
        className="card"
        style={{
          borderLeft: "6px solid var(--warning)",
          backgroundColor: "var(--surface)",
          padding: "var(--clinova-space-4) var(--clinova-space-6)",
        }}
        aria-labelledby="disclaimer-banner-heading"
      >
        <div className="row gap-3 items-start">
          <ShieldAlert style={{ width: 22, height: 22, color: "var(--warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
          <div className="stack gap-1">
            <strong id="disclaimer-banner-heading" style={{ fontSize: "0.875rem", color: "var(--navy-900)" }}>
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
      </section>
    </div>
  );
}