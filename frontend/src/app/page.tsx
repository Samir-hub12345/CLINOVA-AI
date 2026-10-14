"use client";

import React from "react";
import Link from "next/link";
import { useClinova } from "@/lib/referenceContext";
import { ReferenceDashboard } from "@/components/dashboard/ReferenceDashboard";
import { HeroSection } from "@/components/landing/HeroSection";
import { ProductOverviewSection } from "@/components/landing/ProductOverviewSection";
import { WorkflowSection } from "@/components/landing/WorkflowSection";
import { InnovationLayersSection } from "@/components/landing/InnovationLayersSection";
import { RoleWorkspacesSection } from "@/components/landing/RoleWorkspacesSection";
import { TrustSafetySection } from "@/components/landing/TrustSafetySection";
import { ReportShowcaseSection } from "@/components/landing/ReportShowcaseSection";
import { FinalCtaSection } from "@/components/landing/FinalCtaSection";

export default function HomePage() {
  const { user } = useClinova();

  // If user is already authenticated, preserve existing role-based dashboard view
  if (user) {
    return <ReferenceDashboard />;
  }

  return (
    <div className="clinova-landing-page" style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      {/* 
        CLINOVA AI — Premium Public Landing Page
        Architectural Pillars:
        - Continuous Care Intelligence
        - Less paperwork. More time for patient care.
        - Zero-PII & Statutory Compliance (DPDP Act 2023)
        - Paschim Banga Doctrine (Constitutional Emergency Fast-Track)
        - THE CONTINUOUS CLINICAL WORKFLOW
        - THE 12-STAGE MASTER CASE CONTINUOUS LOOP
        - Six Distinct Role Experiences
        - Role-Based Access Control (RBAC) & Hospital Authentication
        - Public staff routing strictly via href="/login"
      */}

      {/* 1. HERO SECTION: Asymmetric headline, value props, live product preview */}
      <HeroSection />

      {/* 2. PRODUCT OVERVIEW: 9 Core Capabilities connected into a single patient view */}
      <ProductOverviewSection />

      {/* 3. HOW CLINOVA WORKS: Dual clinical pathways (Regular OPD vs Emergency Paschim Banga Branch) */}
      <WorkflowSection />

      {/* 4. INNOVATION LAYERS: CAREGRAPH, FACILITYGRAPH & SIGNALGRAPH */}
      <InnovationLayersSection />

      {/* 5. DESIGNED FOR HEALTHCARE: Six Distinct Role Experiences & RBAC Workspaces */}
      <RoleWorkspacesSection />

      {/* 6. TRANSPARENCY, SAFETY & TRUST: Evidence provenance, epistemic uncertainty, NMC 2023 gate */}
      <TrustSafetySection />

      {/* 7. CLINICAL REPORTS & CONTINUITY: Non-repudiable documentation with synthetic demonstration */}
      <ReportShowcaseSection />

      {/* 8. FINAL CALL TO ACTION: Bring the patient journey into clearer focus */}
      <FinalCtaSection />
    </div>
  );
}