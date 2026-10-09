"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { UncertaintyIndicator } from "@/components/ui/UncertaintyIndicator";
import { getClinicianReviewQueue } from "@/lib/api";
import { ReviewQueueData } from "@/types";
import { LoadingState, EmptyState } from "@/components/ui/States";
import { ArrowRight, Stethoscope } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";

export default function StaffReviewPage() {
  const [queueData, setQueueData] = useState<ReviewQueueData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await getClinicianReviewQueue();
        setQueueData(res);
      } catch (err) {
        console.warn("Failed to load review queue:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const casesNeedingReview = queueData?.queue || [];

  return (
    <RoleGuard
      allowedRoles={["CLINICIAN", "DOCTOR", "SYSTEM_ADMIN"]}
      title="Clinician Review Restricted"
      message="Only licensed medical clinicians and physicians hold clinical authority to access the clinical review queue."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
      <PageHeader
        title="Clinician Review & Verification Queue"
        subtitle="Cases awaiting attending physician authentication, parameter verification, and care pathway sign-off"
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Staff", href: "/staff" },
          { label: "Review Queue" },
        ]}
      />

      {loading ? (
        <LoadingState message="Loading cases awaiting clinician review..." />
      ) : casesNeedingReview.length === 0 ? (
        <EmptyState
          title="Review Queue Clear"
          description="All active cases have completed physician review and verification sign-off."
        />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {casesNeedingReview.map((item) => (
            <div
              key={item.case_id}
              className="clinova-card"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 16,
                borderLeft: item.acuity_tier === "CRITICAL"
                  ? "6px solid var(--clinova-emergency)"
                  : "6px solid var(--clinova-accent)",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1, minWidth: 280 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span className="clinova-mono" style={{ fontSize: "1rem", fontWeight: 700 }}>
                    {item.case_id}
                  </span>
                  <span className="clinova-metadata">({item.patient_synthetic_id} • {item.age_bracket})</span>
                  <PriorityBadge tier={item.acuity_tier} />
                  <StatusBadge status={item.status} />
                </div>

                <strong style={{ fontSize: "0.9375rem", color: "var(--clinova-text-primary)" }}>
                  {item.primary_syndrome || "Primary syndrome pending"}
                </strong>
                <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
                  {item.presenting_complaint}
                </p>

                <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                  <ProvenanceBadge provenance={item.provenance_type} showIcon={false} />
                  <UncertaintyIndicator status={item.epistemic_status} />
                  {item.red_flags_count > 0 && (
                    <span className="clinova-badge" style={{ backgroundColor: "#fef2f2", color: "#b91c1c", borderColor: "#fecaca" }}>
                      {item.red_flags_count} Red Flag Alert
                    </span>
                  )}
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <Link
                  href={`/staff/cases/${item.case_id}`}
                  className="clinova-btn clinova-btn-primary"
                  style={{ textDecoration: "none" }}
                >
                  <Stethoscope style={{ width: 14, height: 14 }} aria-hidden="true" />
                  <span>Examine & Verify</span>
                  <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
    </RoleGuard>
  );
}
