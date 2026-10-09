"use client";

import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { UserCheck, Stethoscope, ClipboardCheck, ArrowRight } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function StaffLandingPage() {
  return (
    <RoleGuard
      allowedRoles={["NURSE", "CLINICIAN", "DOCTOR", "FACILITY_ADMIN", "REFERRAL_COORDINATOR", "SYSTEM_ADMIN", "AUDITOR"]}
      title="Staff Gateway Restricted"
      message="This surface is restricted to verified clinical and administrative healthcare network staff."
    >
      <div style={{ maxWidth: 960, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Clinical Staff Workstation Gateway"
        subtitle="Role-aware clinical workspaces for Triage Nurses, Examining Physicians, and Department Reviewers"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Staff Gateway" }]}
      />

      <div className="clinova-grid-3col">
        {/* Workstation 1: Nurse Triage */}
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
              <UserCheck style={{ width: 22, height: 22, color: "var(--clinova-warning)" }} aria-hidden="true" />
              <h3 style={{ fontSize: "1.125rem" }}>Nurse Triage Workstation</h3>
            </div>
            <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
              High-volume triage worklist. Acuity-tiered patient queues, vital signs documentation, red-flag shock alarms, and SLA wait-time monitoring.
            </p>
          </div>
          <div style={{ marginTop: 16 }}>
            <Link href="/staff/triage" className="clinova-btn clinova-btn-primary" style={{ textDecoration: "none", width: "100%" }}>
              <span>Enter Triage Workstation</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>

        {/* Workstation 2: Doctor Workbench */}
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
              <Stethoscope style={{ width: 22, height: 22, color: "#0f766e" }} aria-hidden="true" />
              <h3 style={{ fontSize: "1.125rem" }}>Doctor Reviewer Workbench</h3>
            </div>
            <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
              3-panel asymmetric clinical workbench. Inspect chronological timeline evidence with provenance, evaluate epistemic uncertainty, and execute signed clinical decisions.
            </p>
          </div>
          <div style={{ marginTop: 16 }}>
            <Link href="/staff/cases/CASE-SYNTH-003" className="clinova-btn clinova-btn-secondary" style={{ textDecoration: "none", width: "100%" }}>
              <span>Open Case Workbench</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>

        {/* Workstation 3: Clinician Multi-Case Review List */}
        <div
          className="clinova-card"
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            borderTop: "4px solid #7c3aed",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <ClipboardCheck style={{ width: 22, height: 22, color: "#7c3aed" }} aria-hidden="true" />
              <h3 style={{ fontSize: "1.125rem" }}>Multi-Case Review List</h3>
            </div>
            <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
              Batch verification and sign-off queue for cases awaiting physician review, evidence authentication, or transfer authorization.
            </p>
          </div>
          <div style={{ marginTop: 16 }}>
            <Link href="/staff/review" className="clinova-btn clinova-btn-outline" style={{ textDecoration: "none", width: "100%" }}>
              <span>Open Review Queue</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>
    </div>
    </RoleGuard>
  );
}
