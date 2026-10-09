import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PatientIntakeWizard } from "@/components/patient/PatientIntakeWizard";

export default function PatientIntakePage() {
  return (
    <div>
      <PageHeader
        title="Patient Intake Portal"
        subtitle="Step-by-step clinical registration, language selection, adaptive inquiries, and optional report upload"
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Patient", href: "/patient" },
          { label: "Intake Flow" },
        ]}
      />
      <PatientIntakeWizard />
    </div>
  );
}
