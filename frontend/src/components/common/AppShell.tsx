"use client";

import React, { useState } from "react";
import { TopBar } from "./TopBar";
import { EnvironmentBanner } from "./EnvironmentBanner";
import { DemoBanner } from "./DemoBanner";
import { Footer } from "./Footer";
import { ReferralDrawer } from "@/components/drawers/ReferralDrawer";
import { FacilityDrawer } from "@/components/drawers/FacilityDrawer";
import { SystemAuditDrawer } from "@/components/drawers/SystemAuditDrawer";

interface AppShellProps {
  children: React.ReactNode;
  activeCaseId?: string;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeCaseId = "CASE-SYNTH-003",
}) => {
  const [isReferralOpen, setIsReferralOpen] = useState(false);
  const [isFacilityOpen, setIsFacilityOpen] = useState(false);
  const [isSystemOpen, setIsSystemOpen] = useState(false);

  return (
    <div className="clinova-shell">
      {/* 1. Operational Environment Indicator */}
      <EnvironmentBanner />

      {/* 2. Mandatory Synthetic / Demo Safety Banner */}
      <DemoBanner />

      {/* 3. Global Navigation Header */}
      <TopBar
        onOpenReferralDrawer={() => setIsReferralOpen(true)}
        onOpenFacilityDrawer={() => setIsFacilityOpen(true)}
        onOpenSystemDrawer={() => setIsSystemOpen(true)}
      />

      {/* 4. Main Clinical Workstation Space */}
      <main className="clinova-main">
        <div className="clinova-container">{children}</div>
      </main>

      {/* 5. Global Footer */}
      <Footer />

      {/* 6. Contextual Supporting Drawers */}
      <ReferralDrawer
        isOpen={isReferralOpen}
        onClose={() => setIsReferralOpen(false)}
        caseId={activeCaseId}
      />
      <FacilityDrawer
        isOpen={isFacilityOpen}
        onClose={() => setIsFacilityOpen(false)}
      />
      <SystemAuditDrawer
        isOpen={isSystemOpen}
        onClose={() => setIsSystemOpen(false)}
      />
    </div>
  );
};
