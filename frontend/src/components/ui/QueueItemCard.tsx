import React from "react";
import Link from "next/link";
import { Clock, ArrowRight } from "lucide-react";
import { QueueItem as QueueItemType } from "@/types";
import { PriorityBadge } from "./PriorityBadge";
import { StatusBadge } from "./StatusBadge";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { UncertaintyIndicator } from "./UncertaintyIndicator";

export const QueueItemCard: React.FC<{
  item: QueueItemType;
}> = ({ item }) => {
  return (
    <div
      className="clinova-card clinova-card-interactive"
      style={{
        borderLeft: item.emergency_active
          ? "5px solid var(--clinova-emergency)"
          : item.acuity_tier === "CRITICAL"
          ? "5px solid var(--clinova-danger)"
          : item.acuity_tier === "URGENT"
          ? "5px solid var(--clinova-warning)"
          : "5px solid var(--clinova-border)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--clinova-space-3)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="clinova-mono" style={{ fontSize: "1rem", fontWeight: 700, color: "var(--clinova-text-primary)" }}>
            {item.case_id}
          </span>
          <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
            ({item.patient_synthetic_id} • {item.age_bracket})
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <PriorityBadge tier={item.acuity_tier} />
          <StatusBadge status={item.status} />
        </div>
      </div>

      <div>
        <h4 style={{ fontSize: "0.9375rem", color: "var(--clinova-text-primary)", marginBottom: 2 }}>
          {item.primary_syndrome || "Syndrome Pending"}
        </h4>
        <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", lineHeight: 1.4 }}>
          {item.presenting_complaint}
        </p>
      </div>

      {/* Vitals & Indicators Row */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 8,
          fontSize: "0.75rem",
          paddingTop: 6,
          borderTop: "1px solid var(--clinova-border)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4, color: item.sla_breached ? "var(--clinova-danger)" : "var(--clinova-text-muted)" }}>
            <Clock style={{ width: 12, height: 12 }} aria-hidden="true" />
            <span>Wait: <strong>{item.waiting_minutes}m</strong> (SLA {item.sla_limit_minutes}m)</span>
          </div>

          {item.latest_vitals && (
            <div className="clinova-mono" style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--clinova-text-secondary)" }}>
              {item.latest_vitals.bp && <span>BP: <strong>{item.latest_vitals.bp}</strong></span>}
              {item.latest_vitals.hr && <span>HR: <strong>{item.latest_vitals.hr}</strong></span>}
              {item.latest_vitals.spo2 && <span>SpO2: <strong>{item.latest_vitals.spo2}%</strong></span>}
            </div>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <ProvenanceBadge provenance={item.provenance_type} showIcon={false} />
          <UncertaintyIndicator status={item.epistemic_status} />
          <Link
            href={`/staff/cases/${item.case_id}`}
            className="clinova-btn clinova-btn-secondary clinova-btn-sm"
            style={{ textDecoration: "none" }}
          >
            <span>Review</span>
            <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export const QueueItem = QueueItemCard;
