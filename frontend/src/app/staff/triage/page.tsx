"use client";

import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { NurseTriageQueue } from "@/components/staff/NurseTriageQueue";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function NurseTriagePage() {
  return (
    <RoleGuard
      allowedRoles={["NURSE", "CLINICIAN", "DOCTOR", "SYSTEM_ADMIN"]}
      title="Nurse Triage Access Restricted"
      message="Only licensed triage nurses and clinicians are authorized to access the high-volume triage worklist."
    >
      <div>
        <PageHeader
          title="Nurse Triage Workstation"
          subtitle="Priority triage worklist, SLA monitoring, red-flag detection, and rapid vital signs entry"
          breadcrumbs={[
            { label: "Home", href: "/" },
            { label: "Staff", href: "/staff" },
            { label: "Triage Worklist" },
          ]}
        />
        <NurseTriageQueue />
      </div>
    </RoleGuard>
  );
}
