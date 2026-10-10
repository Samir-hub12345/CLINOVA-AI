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
import { ArrowRight, Stethoscope, Sparkles, CheckCircle2 } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";
import { AIWorkflowSummaryWidget, ClinicalReviewQueueWidget } from "@/components/dashboard";

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

        {/* AI Workflow Intelligence Overview */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(0, 1.4fr) minmax(0, 1fr)",
            gap: "var(--clinova-space-6)",
            alignItems: "start",
          }}
          className="clinova-dash-grid"
        >
          <div className="stack gap-4">
            <div className="card">
              <div className="card-header">
                <div className="row gap-2">
                  <Stethoscope style={{ width: 18, height: 18, color: "var(--teal-600)" }} aria-hidden="true" />
                  <h2 style={{ margin: 0, fontSize: "1.125rem", fontWeight: 700 }}>
                    Attending Physician Oversight Gate
                  </h2>
                </div>
                <span className="badge badge-warning">{casesNeedingReview.length} Pending Sign-off</span>
              </div>
              <div className="card-body stack gap-3">
                <p className="small subtle" style={{ margin: 0 }}>
                  Every clinical synthesis, composite risk score, and care pathway formulated by AI requires
                  direct physician verification and authoritative digital signature per NMC 2023 regulations.
                </p>
                <div className="row gap-3 wrap">
                  <div className="row gap-2 small">
                    <CheckCircle2 style={{ width: 16, height: 16, color: "var(--success)" }} aria-hidden="true" />
                    <span>Human-in-the-loop clinical non-delegation</span>
                  </div>
                  <div className="row gap-2 small">
                    <Sparkles style={{ width: 16, height: 16, color: "var(--teal-600)" }} aria-hidden="true" />
                    <span>Deterministic safety score grounding</span>
                  </div>
                </div>
              </div>
            </div>

            <ClinicalReviewQueueWidget showFooter={false} />
          </div>

          <div className="stack gap-4">
            <AIWorkflowSummaryWidget showReviewButton={false} awaitingCount={casesNeedingReview.length || 2} />
          </div>
        </div>

        {/* Primary Case Review Worklist */}
        <section aria-labelledby="review-list-heading">
          <div className="row between" style={{ marginBottom: 12 }}>
            <h2 id="review-list-heading" style={{ fontSize: "1.25rem", margin: 0, color: "var(--navy-900)", fontWeight: 700 }}>
              Cases Awaiting Clinical Sign-Off
            </h2>
            <span className="small muted">
              Showing {casesNeedingReview.length} active case{casesNeedingReview.length === 1 ? "" : "s"}
            </span>
          </div>

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
        </section>
      </div>
    </RoleGuard>
  );
}
