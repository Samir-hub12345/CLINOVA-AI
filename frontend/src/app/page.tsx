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
  Clock,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Calendar,
  Users,
  Building,
  HelpCircle,
  LogIn,
  ExternalLink,
} from "lucide-react";

export default function HomePage() {
  const metricTiles = [
    {
      label: "Patients Scheduled Today",
      value: "24",
      note: "18 seen & evaluated so far",
      icon: Users,
      tile: "tile-navy",
      to: "/staff/triage",
    },
    {
      label: "Consultations in Progress",
      value: "6",
      note: "Across 4 active clinical bays",
      icon: Stethoscope,
      tile: "tile-info",
      to: "/staff/reception",
    },
    {
      label: "Notes Awaiting Clinician Review",
      value: "4",
      note: "Physician sign-off & human gate",
      icon: FileCheck2,
      tile: "tile-warning",
      to: "/staff/review",
    },
    {
      label: "SBAR Transfers & Follow-Ups",
      value: "8",
      note: "Regional telemetry active",
      icon: Share2,
      tile: "tile-teal",
      to: "/referrals",
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

  const taskQueueItems = [
    {
      id: "task-1",
      title: "Consultation note awaiting review",
      who: "Dr. Priya Sharma • Patient Manoj Das (Chest Pain)",
      to: "/staff/review",
      badge: "tile-navy",
      icon: FileText,
    },
    {
      id: "task-2",
      title: "Missing information in patient record",
      who: "Epistemic Check • Conflicting lisinopril dosage",
      to: "/staff/cases/CASE-SYNTH-003",
      badge: "tile-warning",
      icon: AlertTriangle,
    },
    {
      id: "task-3",
      title: "Laboratory result awaiting clinician review",
      who: "Biochemistry • Cardiac Troponin-I: 0.12 ng/mL (High)",
      to: "/staff/cases/CASE-SYNTH-003",
      badge: "tile-info",
      icon: Activity,
    },
    {
      id: "task-4",
      title: "Follow-up instructions awaiting approval",
      who: "Odia/Hindi Vernacular • BP monitoring schedule",
      to: "/patient/case/CASE-SYNTH-003",
      badge: "tile-teal",
      icon: CheckCircle2,
    },
  ];

  const recentActivity = [
    {
      id: "act-1",
      actor: "Clinova AI",
      action: "Calculated NEWS2 score (8 - High)",
      source: "Bedside vitals acquisition • Bay 2",
      time: "10 mins ago",
      isAi: true,
    },
    {
      id: "act-2",
      actor: "Dr. Priya Sharma",
      action: "Verified ECG findings & signed admission",
      source: "Encounter ENC-5310 • Acute Coronary Bay",
      time: "24 mins ago",
      isAi: false,
    },
    {
      id: "act-3",
      actor: "Ananya Patel, RN",
      action: "Completed triage intake & shock index check",
      source: "Triage Queue • Cuttack DHH",
      time: "42 mins ago",
      isAi: false,
    },
    {
      id: "act-4",
      actor: "Clinova AI",
      action: "Prepared SBAR transfer dossier",
      source: "FacilityGraph referral to SCB Cath Lab",
      time: "1 hour ago",
      isAi: true,
    },
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
          to identify the <strong>Safest Achievable Care Pathway</strong> — while healthcare professionals
          stay strictly in control of every clinical decision.
        </p>

        {/* Quick Launch Action Buttons */}
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
          <Link href="/staff/cases/CASE-SYNTH-003" className="btn btn-accent btn-lg">
            <Stethoscope style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Doctor Workbench</span>
            <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
          </Link>

          <Link href="/staff/triage" className="btn btn-secondary btn-lg">
            <UserCheck style={{ width: 18, height: 18, color: "var(--warning)" }} aria-hidden="true" />
            <span>Nurse Triage</span>
          </Link>

          <Link href="/staff/reception" className="btn btn-primary btn-lg">
            <UserPlus style={{ width: 18, height: 18 }} aria-hidden="true" />
            <span>Reception Desk</span>
          </Link>

          <Link href="/patient/intake" className="btn btn-secondary btn-lg">
            <Activity style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
            <span>Patient Self-Intake</span>
          </Link>

          <Link href="/login" className="btn btn-ghost btn-lg" style={{ border: "1px solid var(--border-strong)" }}>
            <LogIn style={{ width: 16, height: 16 }} aria-hidden="true" />
            <span>Staff Sign In</span>
          </Link>
        </div>
      </section>

      {/* 2. SIGNATURE METRIC TILES (FROM REFERENCE DASHBOARD) */}
      <section>
        <div className="grid grid-4 gap-4">
          {metricTiles.map((tile) => {
            const Icon = tile.icon;
            return (
              <Link
                key={tile.label}
                href={tile.to}
                className="card interactive metric-card"
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div className="row between">
                  <span className="small subtle medium">{tile.label}</span>
                  <span className={`icon-tile ${tile.tile}`}>
                    <Icon aria-hidden="true" />
                  </span>
                </div>
                <div className="stat-value" style={{ color: "var(--navy-900)" }}>
                  {tile.value}
                </div>
                <div className="xs muted">{tile.note}</div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* 3. SIGNATURE 6-STAGE WORKFLOW ENGINE (FROM REFERENCE cS & auth-aside) */}
      <section className="card" style={{ padding: "var(--s-6)" }}>
        <div style={{ marginBottom: 20 }}>
          <div className="row between wrap gap-2">
            <div>
              <span className="section-title">THE CONTINUOUS CLINICAL WORKFLOW</span>
              <h2 style={{ fontSize: "1.5rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
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

      {/* 4. CLINICAL TASK QUEUE & ACTIVITY AUDIT FEED (FROM REFERENCE DASHBOARD) */}
      <section className="grid grid-2 gap-6" style={{ alignItems: "start" }}>
        {/* Left: Real Clinical Task Queue */}
        <div className="card" aria-labelledby="tasks-heading">
          <div className="card-header">
            <div className="row gap-2">
              <FileCheck2 style={{ width: 18, height: 18, color: "var(--warning)" }} aria-hidden="true" />
              <h2 id="tasks-heading" style={{ margin: 0 }}>Clinical Review Queue</h2>
            </div>
            <span className="badge badge-warning">4 Need Attention</span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <ul className="list-reset">
              {taskQueueItems.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <Link
                      href={item.to}
                      className="row between gap-3 interactive"
                      style={{
                        padding: "12px 18px",
                        color: "inherit",
                        textDecoration: "none",
                        display: "flex",
                      }}
                    >
                      <div className="row gap-3">
                        <span className={`icon-tile ${item.badge}`} style={{ width: 32, height: 32 }}>
                          <Icon style={{ width: 16, height: 16 }} aria-hidden="true" />
                        </span>
                        <div className="stack gap-1">
                          <span className="small medium" style={{ color: "var(--navy-900)" }}>
                            {item.title}
                          </span>
                          <span className="xs muted">{item.who}</span>
                        </div>
                      </div>
                      <ArrowRight style={{ width: 15, height: 15, color: "var(--text-4)" }} aria-hidden="true" />
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
          <div className="card-footer">
            <Link href="/staff/review" className="btn btn-secondary btn-sm btn-block">
              <span>View Full Attending Review Worklist</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>

        {/* Right: Immutable Activity Audit Timeline */}
        <div className="card" aria-labelledby="audit-heading">
          <div className="card-header">
            <div className="row gap-2">
              <Clock style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
              <h2 id="audit-heading" style={{ margin: 0 }}>Recent Patient Activity</h2>
            </div>
            <Link href="/system" className="small" style={{ color: "var(--teal-700)" }}>
              View Audit Ledger
            </Link>
          </div>
          <div className="card-body">
            <ol className="list-reset timeline">
              {recentActivity.map((act) => (
                <li key={act.id} className="timeline-item">
                  <span className="timeline-dot">
                    {act.isAi ? (
                      <Sparkles style={{ width: 8, height: 8, color: "var(--teal-600)" }} aria-hidden="true" />
                    ) : (
                      <UserCheck style={{ width: 8, height: 8, color: "var(--success)" }} aria-hidden="true" />
                    )}
                  </span>
                  <div className="stack" style={{ gap: 2 }}>
                    <div className="small">
                      <span className="medium" style={{ color: "var(--navy-900)" }}>
                        {act.actor}
                      </span>{" "}
                      <span className="subtle">{act.action}</span>
                    </div>
                    <div className="xs muted">
                      {act.source} • {act.time}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <div className="card-footer">
            <Link href="/system" className="btn btn-secondary btn-sm btn-block">
              <span>Inspect Cryptographic SHA-256 Ledger</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      {/* 5. SIX SPECIALIZED ROLE WORKSPACES */}
      <section style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
        <div style={{ textAlign: "center" }}>
          <span className="section-title">ROLE-BASED GOVERNANCE & ARCHITECTURE</span>
          <h2 style={{ fontSize: "1.875rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
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
              <p className="small subtle" style={{ margin: 0, lineHeight: 1.5 }}>
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

      {/* 6. THE 13-STAGE CONTINUOUS CARE INTELLIGENCE LOOP */}
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
          <h2 style={{ fontSize: "1.5rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
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
          ].map((item) => (
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

      {/* 7. CLINICAL GOVERNANCE & STATUTORY PILLARS */}
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