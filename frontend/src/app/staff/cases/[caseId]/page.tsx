import React from "react";
import { DoctorWorkbenchView } from "@/components/staff/DoctorWorkbenchView";

interface PageProps {
  params: Promise<{ caseId: string }>;
}

export default async function DoctorCaseWorkbenchPage({ params }: PageProps) {
  const { caseId } = await params;
  return <DoctorWorkbenchView caseId={caseId} />;
}
