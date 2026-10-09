import React from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { getCaseDetails } from "@/lib/api";
import { CaseStatus } from "@/components/ui/CaseStatus";
import { Clock, UserCheck, ArrowLeft } from "lucide-react";

interface PageProps {
  params: Promise<{ caseId: string }>;
}

export default async function PatientCasePage({ params }: PageProps) {
  const { caseId } = await params;
  const caseData = await getCaseDetails(caseId);

  return (
    <div style={{ maxWidth: 840, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title={`Patient Token Status: ${caseData.case.patient_synthetic_id}`}
        subtitle={`Synthetic Case Reference: ${caseData.case.id} (${caseData.case.case_number})`}
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Patient", href: "/patient" },
          { label: "Case Status" },
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
      <div className="clinova-grid-2col">
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <span className="clinova-label">REGISTERED CHIEF COMPLAINT</span>
          <strong style={{ fontSize: "0.9375rem" }}>{caseData.case.presenting_complaint}</strong>
          <span style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)" }}>
            Demographics: {caseData.case.age_bracket} • {caseData.case.biological_sex}
          </span>
        </div>

        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <span className="clinova-label">EXAMINING CLINICAL TEAM</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <UserCheck style={{ width: 18, height: 18, color: "var(--clinova-accent)" }} aria-hidden="true" />
            <div>
              <strong style={{ fontSize: "0.9375rem", display: "block" }}>Cuttack DHH Clinical Team</strong>
              <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                Attending: Dr. Priya Sharma / Ananya Patel, RN
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Safety Guidance */}
      <div
        className="clinova-card"
        style={{
          backgroundColor: "var(--clinova-warning-bg)",
          borderColor: "var(--clinova-warning-border)",
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
        }}
      >
        <Clock style={{ width: 20, height: 20, color: "var(--clinova-warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
        <div style={{ fontSize: "0.8125rem", color: "var(--clinova-warning-text)" }}>
          <strong>Notice to Patient & Family:</strong>
          <p style={{ marginTop: 2 }}>
            If your condition worsens or you experience shortness of breath, sudden sweating, dizziness, or chest tightness, please notify the nearest triage nurse immediately.
          </p>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Link href="/patient" className="clinova-btn clinova-btn-secondary" style={{ textDecoration: "none" }}>
          <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Back to Patient Portal</span>
        </Link>
        <Link href={`/staff/cases/${caseId}`} className="clinova-btn clinova-btn-outline" style={{ textDecoration: "none" }}>
          <span>Switch to Clinician View</span>
        </Link>
      </div>
    </div>
  );
}
