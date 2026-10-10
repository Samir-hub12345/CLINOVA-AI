"use client";

import React from "react";
import Link from "next/link";
import { Sparkles, ShieldCheck, ArrowRight } from "lucide-react";

interface AIWorkflowSummaryWidgetProps {
  draftsCount?: number;
  reviewedCount?: number;
  awaitingCount?: number;
  showReviewButton?: boolean;
}

export const AIWorkflowSummaryWidget: React.FC<AIWorkflowSummaryWidgetProps> = ({
  draftsCount = 16,
  reviewedCount = 14,
  awaitingCount = 2,
  showReviewButton = true,
}) => {
  return (
    <div className="card" aria-labelledby="ai-summary-heading">
      <div className="card-header">
        <div className="row gap-2">
          <span className="ai-mark">
            <Sparkles aria-hidden="true" />
          </span>
          <h2 id="ai-summary-heading" style={{ margin: 0, fontSize: "1.125rem", fontWeight: 700 }}>
            AI Workflow Summary
          </h2>
        </div>
        <span className="badge badge-teal">Today</span>
      </div>
      <div className="card-body stack gap-4">
        <div className="grid grid-3" style={{ gap: 10 }}>
          <div
            className="stack gap-1"
            style={{
              padding: 12,
              borderRadius: "var(--r-md)",
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
            }}
          >
            <span className="stat-value" style={{ fontSize: "1.375rem" }}>{draftsCount}</span>
            <span className="xs muted" style={{ lineHeight: 1.3 }}>Drafts prepared</span>
          </div>
          <div
            className="stack gap-1"
            style={{
              padding: 12,
              borderRadius: "var(--r-md)",
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
            }}
          >
            <span className="stat-value" style={{ fontSize: "1.375rem" }}>{reviewedCount}</span>
            <span className="xs muted" style={{ lineHeight: 1.3 }}>Reviewed by staff</span>
          </div>
          <div
            className="stack gap-1"
            style={{
              padding: 12,
              borderRadius: "var(--r-md)",
              background: "var(--warning-bg)",
              border: "1px solid #f6d6a8",
            }}
          >
            <span className="stat-value" style={{ fontSize: "1.375rem", color: "var(--warning-text)" }}>{awaitingCount}</span>
            <span className="xs muted" style={{ lineHeight: 1.3, color: "var(--warning-text)" }}>Awaiting review</span>
          </div>
        </div>

        <div className="stack gap-2">
          {[
            { label: "Clinical documentation drafts", count: 4 },
            { label: "NEWS2 & laboratory summaries", count: 3 },
            { label: "Patient follow-up instructions", count: 2 },
            { label: "Epistemic uncertainty checks", count: 1 },
          ].map((cat) => (
            <div key={cat.label} className="row between small">
              <span className="subtle">{cat.label}</span>
              <span className="tnum medium" style={{ color: "var(--navy-900)" }}>{cat.count}</span>
            </div>
          ))}
        </div>

        <div className="alert alert-ai" style={{ padding: "8px 12px" }}>
          <ShieldCheck style={{ width: 16, height: 16, flexShrink: 0 }} aria-hidden="true" />
          <span style={{ fontSize: "var(--fs-xs)", lineHeight: 1.4 }}>
            Nothing drafted by AI is added to a chart, signed, or transmitted without definitive clinician approval.
          </span>
        </div>

        {showReviewButton && (
          <Link
            href="/staff/review"
            className="btn btn-secondary btn-sm"
            style={{ alignSelf: "flex-start" }}
          >
            <span>Open Review Center</span>
            <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
          </Link>
        )}
      </div>
    </div>
  );
};
