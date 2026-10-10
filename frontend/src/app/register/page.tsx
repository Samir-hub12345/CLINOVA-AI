"use client";

import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import {
  Activity,
  UserPlus,
  ShieldCheck,
  Lock,
  ArrowRight,
  LogIn,
  AlertCircle,
} from "lucide-react";

export default function RegisterGatePage() {
  return (
    <div style={{ maxWidth: 840, margin: "20px auto", padding: "0 var(--s-4)", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="CLINOVA AI Registration & Onboarding"
        subtitle="Role-governed patient onboarding and clinical staff credentials"
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Registration" }]}
      />

      {/* Security Governance Notice */}
      <div className="alert alert-info">
        <ShieldCheck style={{ width: 18, height: 18, color: "var(--info)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
        <div style={{ fontSize: "var(--fs-sm)", lineHeight: 1.5 }}>
          <strong>Institutional Access Policy:</strong> In compliance with National Medical Commission (NMC) regulations and DPDP Act 2023, clinical roles (Doctors, Triage Nurses, Administrators) cannot be self-selected via public forms. Clinical credentials are provisioned exclusively through authorized hospital administrators.
        </div>
      </div>

      <div className="grid grid-2 gap-4">
        {/* Pathway 1: Patient Self-Intake */}
        <div className="card interactive stack between" style={{ borderTop: "4px solid var(--teal-600)" }}>
          <div className="card-body stack gap-3">
            <div className="row gap-2">
              <Activity style={{ width: 22, height: 22, color: "var(--teal-600)" }} aria-hidden="true" />
              <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Patient Intake Portal</h3>
            </div>
            <p className="small subtle" style={{ margin: 0, lineHeight: 1.6 }}>
              Patients seeking medical care can complete digital symptom intake, vernacular voice recording (Odia, Hindi, English), and informed consent before seeing the doctor.
            </p>
            <span className="badge badge-teal" style={{ alignSelf: "flex-start" }}>
              Public / Walk-In Patient
            </span>
          </div>
          <div className="card-footer">
            <Link href="/patient/intake" className="btn btn-primary btn-block">
              <span>Begin Patient Intake</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>

        {/* Pathway 2: Staff-Led Reception Registration */}
        <div className="card interactive stack between" style={{ borderTop: "4px solid var(--navy-800)" }}>
          <div className="card-body stack gap-3">
            <div className="row gap-2">
              <UserPlus style={{ width: 22, height: 22, color: "var(--navy-800)" }} aria-hidden="true" />
              <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Medical Reception Desk</h3>
            </div>
            <p className="small subtle" style={{ margin: 0, lineHeight: 1.6 }}>
              Authorized hospital receptionists register walk-in patients, record legal DPDP Act 2023 consent, and assign the clinical pathway (Regular OPD vs Emergency Fast-Track).
            </p>
            <span className="badge badge-navy" style={{ alignSelf: "flex-start" }}>
              Staff-Assigned Pathway
            </span>
          </div>
          <div className="card-footer">
            <Link href="/staff/reception" className="btn btn-secondary btn-block">
              <span>Open Reception Desk</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>

      {/* Existing Staff Gateway */}
      <div className="card" style={{ backgroundColor: "var(--surface-sunken)" }}>
        <div className="card-body row between wrap gap-3">
          <div className="stack gap-1">
            <strong style={{ fontSize: "var(--fs-md)" }}>Already have clinical staff credentials?</strong>
            <p className="xs muted" style={{ margin: 0 }}>
              Access Doctor Workbench, Nurse Triage, Referral Coordination, or Facility Operations.
            </p>
          </div>
          <Link href="/login" className="btn btn-accent btn-sm">
            <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Staff Sign In</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
