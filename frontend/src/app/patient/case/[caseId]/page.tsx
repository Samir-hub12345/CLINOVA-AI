import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { getCaseDetails } from "@/lib/api";
import { CaseStatus } from "@/components/ui/CaseStatus";
import {
  Clock,
  UserCheck,
  ArrowLeft,
  Calendar,
  MessageSquare,
  ShieldCheck,
  FileCheck2,
  PhoneCall,
  CheckCircle,
} from "lucide-react";

interface PageProps {
  params: Promise<{ caseId: string }>;
}

export default async function PatientCasePage({ params }: PageProps) {
  const { caseId } = await params;
  const caseData = await getCaseDetails(caseId);

  const isCompleted =
    caseData.case.status === "COMPLETED" ||
    caseData.case.status === "CLOSED" ||
    caseData.case.status === "DISPOSITION_PENDING";

  return (
    <div style={{ maxWidth: 880, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title={`Patient Token Status: ${caseData.case.patient_synthetic_id}`}
        subtitle={`Case Reference: ${caseData.case.id} (${caseData.case.case_number}) • Private Patient View`}
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Patient", href: "/patient" },
          { label: "My Case Status" },
        ]}
      />

      {/* Structured Case Status Block */}
      <CaseStatus
        status={caseData.case.status}
        acuityTier={caseData.case.acuity_tier}
        emergencyActive={caseData.case.emergency_active}
        caseId={caseData.case.id}
        facilityName="Cuttack District Headquarters Hospital"
        variant="card"
      />

      {/* Patient Summary Details */}
      <div className="grid grid-2 gap-3">
        <div className="card">
          <div className="card-body tight stack gap-2">
            <span className="section-title">Registered Chief Complaint</span>
            <strong style={{ fontSize: "var(--fs-md)", color: "var(--text)" }}>
              {caseData.case.presenting_complaint}
            </strong>
            <span className="xs muted">
              Recorded Demographics: {caseData.case.age_bracket} • {caseData.case.biological_sex}
            </span>
          </div>
        </div>

        <div className="card">
          <div className="card-body tight stack gap-2">
            <span className="section-title">Assigned Care Team</span>
            <div className="row gap-2">
              <UserCheck style={{ width: 20, height: 20, color: "var(--teal-600)" }} aria-hidden="true" />
              <div>
                <strong style={{ fontSize: "var(--fs-sm)", display: "block" }}>Cuttack DHH Clinical Team</strong>
                <span className="xs muted">
                  Attending: Dr. Priya Sharma / Ananya Patel, RN
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Approved Patient Instructions & Care Plan (Reference Feature) */}
      <div className="card">
        <div className="card-header">
          <div className="row gap-2">
            <FileCheck2 style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
            <h3 style={{ fontSize: "var(--fs-md)" }}>Approved Care Plan & Instructions</h3>
          </div>
          <span className="badge badge-success">
            <CheckCircle style={{ width: 11, height: 11 }} aria-hidden="true" />
            <span>Clinician Approved</span>
          </span>
        </div>

        <div className="card-body stack gap-4">
          <div className="grid grid-2 gap-4">
            {/* Written Care Guidelines */}
            <div className="stack gap-3">
              <div>
                <strong className="small" style={{ display: "block", color: "var(--text)" }}>
                  Home Care & Medication Instructions
                </strong>
                <p className="xs subtle" style={{ marginTop: 4, lineHeight: 1.6 }}>
                  {caseData.case.emergency_active
                    ? "Patient admitted for urgent stabilization. Bedside oxygen and cardiac monitoring active. Please follow nursing staff directions."
                    : "Maintain oral hydration with warm fluids. Take prescribed symptomatic medications after meals as advised by your physician. Complete full course even if symptoms improve."}
                </p>
              </div>

              <div>
                <strong className="small" style={{ display: "block", color: "var(--text)" }}>
                  Scheduled Follow-Up Appointment
                </strong>
                <div className="row gap-2" style={{ marginTop: 4 }}>
                  <Calendar style={{ width: 15, height: 15, color: "var(--teal-600)" }} aria-hidden="true" />
                  <span className="xs strong">Review in 5–7 Days (OPD Desk 4, Cuttack DHH)</span>
                </div>
              </div>

              <div className="alert alert-neutral" style={{ padding: 10 }}>
                <ShieldCheck style={{ width: 16, height: 16, color: "var(--success)", flexShrink: 0 }} aria-hidden="true" />
                <span className="xs muted">
                  Strictly Patient-Approved Information: Internal diagnostic reasoning, preliminary hypotheses, and system telemetry are restricted to authorized clinical staff.
                </span>
              </div>
            </div>

            {/* Reference Design: Phone Frame & SMS Bubble Preview */}
            <div className="stack gap-2" style={{ alignItems: "center" }}>
              <span className="xs muted row gap-1">
                <MessageSquare style={{ width: 12, height: 12 }} aria-hidden="true" />
                <span>Patient Mobile Notification Preview</span>
              </span>

              <div className="phone-frame" style={{ width: "100%", maxWidth: 320 }}>
                <div className="xs muted" style={{ textAlign: "center", marginBottom: 8, fontWeight: 600 }}>
                  CLINOVA CARE • Cuttack DHH
                </div>
                <div className="sms-bubble">
                  {`Hello! Your clinic visit for Token ${caseData.case.patient_synthetic_id} has been recorded at Cuttack DHH.
Care Plan: ${caseData.case.emergency_active ? "Urgent clinical stabilization active." : "Rest, warm fluids, take prescribed medication."}
Follow-up: In 5-7 days or immediately if fever >102°F, chest pain, or breathing difficulty develops.
Emergency Helpline: 108`}
                </div>
                <div className="xs muted" style={{ marginTop: 6, textAlign: "right" }}>
                  Delivery: SMS Sent • Verified Delivery
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Emergency Red Flag Warning */}
      <div
        className="card"
        style={{
          backgroundColor: "var(--clinova-warning-bg)",
          borderColor: "var(--clinova-warning-border)",
        }}
      >
        <div className="card-body tight" style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
          <Clock style={{ width: 20, height: 20, color: "var(--clinova-warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
          <div style={{ fontSize: "var(--fs-sm)", color: "var(--clinova-warning-text)" }}>
            <strong>When to Seek Immediate Emergency Attention:</strong>
            <p style={{ marginTop: 4, lineHeight: 1.5 }}>
              If your condition worsens or you experience shortness of breath, sudden sweating, dizziness, fainting, severe vomiting, or chest tightness, do not wait for your scheduled appointment. Go to the nearest Emergency Department immediately or dial <strong>108 (Emergency Ambulance)</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Patient Navigation (Role Boundary Enforced) */}
      <div className="row between">
        <Link href="/patient" className="btn btn-secondary">
          <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Return to Patient Portal</span>
        </Link>
        <div className="row gap-2">
          <a href="tel:108" className="btn btn-danger btn-sm">
            <PhoneCall style={{ width: 14, height: 14 }} aria-hidden="true" />
            <span>Emergency: Call 108</span>
          </a>
        </div>
      </div>
    </div>
  );
}
