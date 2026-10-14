"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Activity,
  UserPlus,
  UserCheck,
  Stethoscope,
  Building2,
  ShieldCheck,
  LogIn,
  ArrowRight,
  Lock,
} from "lucide-react";

export const RoleWorkspacesSection: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<string>("clinician");

  const roles = [
    {
      id: "patient",
      title: "Patient Portal",
      persona: "Patient",
      icon: Activity,
      borderColor: "var(--teal-600)",
      badgeClass: "badge-teal",
      summary:
        "Digital self-service symptom intake, vernacular audio speech recording (Odia/Hindi/English), and physician-approved care-plan instructions.",
      responsibilities: [
        "Informed digital consent under DPDP Act 2023 with zero PII exposure",
        "Vernacular voice audio recording with dynamic speech confidence scoring",
        "Access to doctor-signed plain-language care plans and appointment reminders",
      ],
      previewSnippet: {
        title: "Patient Self-Service Screen",
        meta: "Public / Walk-In Ingress",
        lines: [
          { k: "Symptom Intake", v: "Vernacular Speech Audio Captured (Odia/Hindi/English)" },
          { k: "Consent Token", v: "DPDP-CONSENT-VERIFIED • Zero PII to 3rd-Party Endpoints" },
          { k: "Care Plan Output", v: "Doctor-approved medication instructions & vernacular diet guidance" },
        ],
      },
      actionLink: "/patient",
      actionLabel: "Explore Patient Portal",
      isPublicAction: true,
    },
    {
      id: "receptionist",
      title: "Receptionist Desk",
      persona: "Receptionist",
      icon: UserPlus,
      borderColor: "var(--navy-800)",
      badgeClass: "badge-navy",
      summary:
        "Front-desk patient registration, demographic capture, legal DPDP Act 2023 consent logging, and clinical pathway assignment (Regular OPD vs Emergency).",
      responsibilities: [
        "Find or create hospital patient identity records",
        "Staff-directed clinical pathway routing: Outpatient Clinic vs Emergency Priority",
        "Strict boundary isolation: Zero autonomous medical diagnosis or prescription capability",
      ],
      previewSnippet: {
        title: "Receptionist Front Desk Console",
        meta: "Protected Staff Workspace",
        lines: [
          { k: "Active Queue", v: "14 Registered Patients • Average Wait Time 8.2 mins" },
          { k: "Pathway Routing", v: "Regular OPD (12) • Emergency Bay Direct (2)" },
          { k: "Consent Status", v: "100% DPDP Act Statutory Consent Recorded" },
        ],
      },
      actionLink: "/login",
      actionLabel: "Sign In as Receptionist",
      isPublicAction: false,
    },
    {
      id: "nurse",
      title: "Nurse Triage",
      persona: "Triage Nurse",
      icon: UserCheck,
      borderColor: "var(--warning)",
      badgeClass: "badge-warning",
      summary:
        "High-volume operational triage queue tracking composite risk scores, NEWS2 bedside vital sign acquisition, and red-flag acute shock alarms.",
      responsibilities: [
        "Bedside vital acquisition: GCS, SpO2, Blood Pressure, Heart Rate, Respiratory Rate",
        "Deterministic real-time computation of NEWS2 and Shock Index scores",
        "Emergency fast-track bay diversion and wait-time SLA breach alerting",
      ],
      previewSnippet: {
        title: "Nurse Triage & NEWS2 Queue",
        meta: "Protected Clinical Workspace",
        lines: [
          { k: "Queue Acuity", v: "High Acuity (3) • Moderate (7) • Low Risk (4)" },
          { k: "Deterministic Alarms", v: "Shock Index > 0.9 Red-Flag Alarm Triggered" },
          { k: "Vital Acquisition", v: "NEWS2 Bedside Score Evaluated Instantly" },
        ],
      },
      actionLink: "/login",
      actionLabel: "Sign In as Nurse",
      isPublicAction: false,
    },
    {
      id: "clinician",
      title: "Doctor Workbench",
      persona: "Clinician / Doctor",
      icon: Stethoscope,
      borderColor: "#0f766e",
      badgeClass: "badge-teal",
      summary:
        "3-panel asymmetric workstation for attending medical practitioners. Inspects chronological timeline evidence, verifies provenance tags, resolves gaps, and executes sign-offs.",
      responsibilities: [
        "Evidence inspection with color-coded provenance tags and epistemic uncertainty meters",
        "Attending physician review queue with batch case verification",
        "Non-delegable clinical decision gate: system never signs on physician's behalf (NMC 2023)",
      ],
      previewSnippet: {
        title: "3-Panel Doctor Workbench",
        meta: "Protected Attending Physician Workspace",
        lines: [
          { k: "Timeline Evidence", v: "Chronological history with provenance tags (EHR, Voice, Vitals)" },
          { k: "Epistemic Gap Audit", v: "Surfaces unconfirmed medications and missing renal panels" },
          { k: "Authoritative Decision", v: "Physician non-repudiable digital sign-off and care plan" },
        ],
      },
      actionLink: "/login",
      actionLabel: "Sign In as Clinician",
      isPublicAction: false,
    },
    {
      id: "facility_admin",
      title: "Facility Administrator",
      persona: "Facility Admin",
      icon: Building2,
      borderColor: "var(--info)",
      badgeClass: "badge-info",
      summary:
        "FacilityGraph resource management: bed occupancy, ICU ventilator capacity, oxygen manifold telemetry, capability flags, and regional SBAR transfer dispatch.",
      responsibilities: [
        "Regional receiving center telemetry and critical care resource tracking",
        "SBAR structured transfer handoff dispatch for unstable clinical cases",
        "Strictly isolated to designated institutional facility scope",
      ],
      previewSnippet: {
        title: "Facility Telemetry & SBAR Dispatch",
        meta: "Protected Administrative Console",
        lines: [
          { k: "Bed Capacity", v: "General 88/120 Occupied • ICU Ventilators: 4 Available" },
          { k: "Oxygen Telemetry", v: "Manifold Pressure 94 psi (Normal Reserve)" },
          { k: "Transfer Transit", v: "SBAR Packet Dispatched to SCB Medical College" },
        ],
      },
      actionLink: "/login",
      actionLabel: "Sign In as Facility Admin",
      isPublicAction: false,
    },
    {
      id: "sysadmin",
      title: "System Administrator",
      persona: "System Admin",
      icon: ShieldCheck,
      borderColor: "#475569",
      badgeClass: "badge-navy",
      summary:
        "Platform health monitoring, cryptographic SHA-256 chained security audit ledger, offline edge synchronization queue status, and compliance verification.",
      responsibilities: [
        "Cryptographic SHA-256 chained audit log for every encounter transition",
        "Offline edge synchronization queue inspection and conflict resolution",
        "Zero clinical authority bypass: administrative oversight strictly separated from care decisions",
      ],
      previewSnippet: {
        title: "Security Audit & Edge Sync Ledger",
        meta: "Protected System Governance Console",
        lines: [
          { k: "Audit Ledger", v: "Immutable SHA-256 Chained Hash Verification: VALID" },
          { k: "Edge Sync Status", v: "Offline Queue Synchronized • Zero Conflict Clashes" },
          { k: "RBAC Governance", v: "Cryptographic Role-Based Token Validation Active" },
        ],
      },
      actionLink: "/login",
      actionLabel: "Sign In as System Admin",
      isPublicAction: false,
    },
  ];

  const currentRole = roles.find((r) => r.id === selectedRole) || roles[3];
  const CurrentIcon = currentRole.icon;

  return (
    <section
      id="roles"
      tabIndex={-1}
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="roles-main-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 820, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            ROLE-BASED GOVERNANCE & ARCHITECTURE
          </div>
          <h2
            id="roles-main-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            Six Distinct Role Experiences
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            Strict role-based isolation, authentic access control, and specialized workspaces for every clinical persona across the patient journey.
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div
          role="tablist"
          aria-label="Healthcare roles"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 160px), 1fr))",
            gap: 8,
            marginBottom: "var(--clinova-space-6)",
          }}
        >
          {roles.map((r) => {
            const RIcon = r.icon;
            const isSelected = r.id === selectedRole;
            return (
              <button
                key={r.id}
                id={`role-tab-${r.id}`}
                type="button"
                role="tab"
                aria-selected={isSelected}
                aria-controls={`role-panel-${r.id}`}
                onClick={() => setSelectedRole(r.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "10px 12px",
                  borderRadius: "var(--r-md)",
                  border: isSelected ? `2px solid ${r.borderColor}` : "1px solid var(--border)",
                  backgroundColor: isSelected ? "var(--surface-sunken)" : "var(--surface)",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.15s ease",
                }}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: "var(--r-sm)",
                    backgroundColor: isSelected ? "var(--surface)" : "var(--surface-sunken)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: r.borderColor,
                    flexShrink: 0,
                  }}
                >
                  <RIcon style={{ width: 16, height: 16 }} aria-hidden="true" />
                </div>
                <div style={{ minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: "0.8125rem",
                      fontWeight: 600,
                      color: isSelected ? "var(--navy-900)" : "var(--text)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {r.persona}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Role Detail Workspace Explorer */}
        <div
          id={`role-panel-${currentRole.id}`}
          role="tabpanel"
          aria-labelledby={`role-tab-${currentRole.id}`}
          tabIndex={0}
          className="card landing-role-detail-grid"
          style={{
            padding: "var(--clinova-space-6)",
            borderTop: `4px solid ${currentRole.borderColor}`,
            backgroundColor: "var(--surface)",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          {/* Left: Role Responsibilities */}
          <div className="stack gap-4">
            <div>
              <div className="row gap-2">
                <span className={`badge ${currentRole.badgeClass}`}>{currentRole.persona}</span>
                <span className="xs muted">Dedicated Workspace</span>
              </div>
              <h3 style={{ fontSize: "1.5rem", color: "var(--navy-900)", marginTop: 4 }}>
                {currentRole.title}
              </h3>
              <p style={{ fontSize: "0.9375rem", color: "var(--text)", lineHeight: 1.6, marginTop: 6 }}>
                {currentRole.summary}
              </p>
            </div>

            <div>
              <strong style={{ fontSize: "0.8125rem", color: "var(--navy-900)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Core Operational Responsibilities:
              </strong>
              <ul className="xs muted stack gap-2" style={{ paddingLeft: 18, marginTop: 6, lineHeight: 1.5 }}>
                {currentRole.responsibilities.map((resp, idx) => (
                  <li key={idx}>
                    <span>{resp}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 4 }}>
              <Link
                href={currentRole.actionLink}
                className="btn btn-primary btn-sm"
                style={{ gap: 6 }}
              >
                {currentRole.isPublicAction ? (
                  <Activity style={{ width: 14, height: 14 }} aria-hidden="true" />
                ) : (
                  <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
                )}
                <span>{currentRole.actionLabel}</span>
                <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Right: Authentic Interface Preview */}
          <div
            style={{
              backgroundColor: "var(--surface-sunken)",
              border: "1px solid var(--border)",
              borderRadius: "var(--r-md)",
              padding: "16px",
            }}
          >
            <div
              style={{
                backgroundColor: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: "var(--r-sm)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  backgroundColor: "var(--surface-2)",
                  padding: "8px 12px",
                  borderBottom: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div className="row gap-2">
                  <CurrentIcon style={{ width: 14, height: 14, color: currentRole.borderColor }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.8125rem", color: "var(--navy-900)" }}>
                    {currentRole.previewSnippet.title}
                  </strong>
                </div>
                <span className="xs muted">{currentRole.previewSnippet.meta}</span>
              </div>

              <div style={{ padding: "14px" }} className="stack gap-3">
                {currentRole.previewSnippet.lines.map((line, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 2,
                      paddingBottom: idx < currentRole.previewSnippet.lines.length - 1 ? 8 : 0,
                      borderBottom: idx < currentRole.previewSnippet.lines.length - 1 ? "1px solid var(--border)" : "none",
                    }}
                  >
                    <span className="xs muted medium">{line.k}</span>
                    <span style={{ fontSize: "0.8125rem", color: "var(--navy-900)", fontWeight: 500 }}>
                      {line.v}
                    </span>
                  </div>
                ))}
              </div>

              <div
                style={{
                  backgroundColor: "var(--surface-2)",
                  padding: "6px 12px",
                  borderTop: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: "11px",
                  color: "var(--text-3)",
                }}
              >
                <Lock style={{ width: 12, height: 12, color: "var(--text-4)" }} aria-hidden="true" />
                <span>Protected by hospital cryptographic credentials & role token boundary.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Role Access Security & Login Gateway Banner (preserves test requirement) */}
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
            marginTop: "var(--clinova-space-6)",
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
      </div>
    </section>
  );
};
