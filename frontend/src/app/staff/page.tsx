"use client";

import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import {
  UserPlus,
  UserCheck,
  Stethoscope,
  ClipboardCheck,
  ArrowRight,
  Share2,
  Building2,
  ShieldCheck,
} from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function StaffLandingPage() {
  return (
    <RoleGuard
      allowedRoles={[
        "RECEPTIONIST",
        "NURSE",
        "CLINICIAN",
        "DOCTOR",
        "FACILITY_ADMIN",
        "REFERRAL_COORDINATOR",
        "SYSTEM_ADMIN",
        "AUDITOR",
      ]}
      title="Staff Gateway Restricted"
      message="This surface is restricted to verified clinical, operational, and administrative healthcare network staff."
    >
      <div style={{ maxWidth: 1100, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
        <PageHeader
          title="Clinical & Operational Staff Gateway"
          subtitle="Role-aware clinical workspaces for Medical Receptionists, Triage Nurses, Examining Physicians, and Health System Administrators"
          breadcrumbs={[{ label: "Home", href: "/" }, { label: "Staff Gateway" }]}
        />

        {/* Primary Clinical & Intake Workstations */}
        <div>
          <span className="clinova-label">CORE CLINICAL & INTAKE WORKSTATIONS</span>
          <div className="grid grid-3 gap-4" style={{ marginTop: 8 }}>
            {/* Workstation 0: Medical Reception */}
            <div
              className="card"
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                borderTop: "4px solid var(--teal-600)",
              }}
            >
              <div className="card-body stack gap-2">
                <div className="row gap-2">
                  <UserPlus style={{ width: 20, height: 20, color: "var(--teal-600)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Medical Reception Desk</h3>
                </div>
                <p className="small subtle" style={{ margin: 0 }}>
                  Patient intake registration, identity verification, DPDP Act 2023 digital consent recording, and staff-directed clinical pathway assignment (Regular vs Emergency).
                </p>
                <div style={{ marginTop: 6 }}>
                  <span className="badge badge-teal">Receptionist Authority</span>
                </div>
              </div>
              <div className="card-footer">
                <Link href="/staff/reception" className="btn btn-primary btn-sm btn-block">
                  <span>Enter Reception Desk</span>
                  <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                </Link>
              </div>
            </div>

            {/* Workstation 1: Nurse Triage */}
            <div
              className="card"
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                borderTop: "4px solid var(--warning)",
              }}
            >
              <div className="card-body stack gap-2">
                <div className="row gap-2">
                  <UserCheck style={{ width: 20, height: 20, color: "var(--warning)" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Nurse Triage Workstation</h3>
                </div>
                <p className="small subtle" style={{ margin: 0 }}>
                  High-volume triage worklist. Acuity-tiered patient queues, vital signs acquisition (NEWS2, Shock Index), red-flag alarms, and SLA wait-time monitoring.
                </p>
                <div style={{ marginTop: 6 }}>
                  <span className="badge badge-warning">Triage Nurse</span>
                </div>
              </div>
              <div className="card-footer">
                <Link href="/staff/triage" className="btn btn-secondary btn-sm btn-block">
                  <span>Enter Triage Workstation</span>
                  <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                </Link>
              </div>
            </div>

            {/* Workstation 2: Doctor Workbench */}
            <div
              className="card"
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                borderTop: "4px solid #0f766e",
              }}
            >
              <div className="card-body stack gap-2">
                <div className="row gap-2">
                  <Stethoscope style={{ width: 20, height: 20, color: "#0f766e" }} aria-hidden="true" />
                  <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Doctor Reviewer Workbench</h3>
                </div>
                <p className="small subtle" style={{ margin: 0 }}>
                  3-panel asymmetric clinical workbench. Inspect chronological timeline evidence with provenance, evaluate epistemic uncertainty, and execute signed clinical decisions.
                </p>
                <div style={{ marginTop: 6 }}>
                  <span className="badge badge-teal">Clinician / Doctor</span>
                </div>
              </div>
              <div className="card-footer">
                <Link href="/staff/cases/CASE-SYNTH-003" className="btn btn-accent btn-sm btn-block">
                  <span>Open Doctor Workbench</span>
                  <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Operational, Administrative & System Surfaces */}
        <div>
          <span className="clinova-label">DEPARTMENTAL REVIEW, REFERRALS & ADMINISTRATION</span>
          <div className="grid grid-4 gap-3" style={{ marginTop: 8 }}>
            {/* Batch Review Queue */}
            <div className="card interactive stack between">
              <div className="card-body tight stack gap-2">
                <div className="row gap-2">
                  <ClipboardCheck style={{ width: 18, height: 18, color: "#7c3aed" }} aria-hidden="true" />
                  <strong className="small">Attending Review Queue</strong>
                </div>
                <p className="xs muted">Multi-case review queue awaiting physician sign-off, conflict resolution, and disposition.</p>
              </div>
              <div className="card-footer tight">
                <Link href="/staff/review" className="btn btn-ghost btn-sm btn-block">
                  <span>Review Queue</span>
                  <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
                </Link>
              </div>
            </div>

            {/* Referral Coordination */}
            <div className="card interactive stack between">
              <div className="card-body tight stack gap-2">
                <div className="row gap-2">
                  <Share2 style={{ width: 18, height: 18, color: "var(--info)" }} aria-hidden="true" />
                  <strong className="small">Referral Coordination</strong>
                </div>
                <p className="xs muted">FacilityGraph transfer feasibility, SBAR handoff dispatch, transit tracking, and bed matching.</p>
              </div>
              <div className="card-footer tight">
                <Link href="/referrals" className="btn btn-ghost btn-sm btn-block">
                  <span>Referrals</span>
                  <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
                </Link>
              </div>
            </div>

            {/* Facility Operations */}
            <div className="card interactive stack between">
              <div className="card-body tight stack gap-2">
                <div className="row gap-2">
                  <Building2 style={{ width: 18, height: 18, color: "var(--teal-700)" }} aria-hidden="true" />
                  <strong className="small">Facility Administrator</strong>
                </div>
                <p className="xs muted">Regional ICU/bed telemetry, oxygen capacity, emergency capabilities, and operational resource planning.</p>
              </div>
              <div className="card-footer tight">
                <Link href="/facilities" className="btn btn-ghost btn-sm btn-block">
                  <span>Facility Ops</span>
                  <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
                </Link>
              </div>
            </div>

            {/* System Audit & Telemetry */}
            <div className="card interactive stack between">
              <div className="card-body tight stack gap-2">
                <div className="row gap-2">
                  <ShieldCheck style={{ width: 18, height: 18, color: "var(--navy-800)" }} aria-hidden="true" />
                  <strong className="small">System Administrator</strong>
                </div>
                <p className="xs muted">Cryptographic audit log, offline edge node sync queue, system telemetry, and compliance verification.</p>
              </div>
              <div className="card-footer tight">
                <Link href="/system" className="btn btn-ghost btn-sm btn-block">
                  <span>System Console</span>
                  <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}
