"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Clock,
  AlertOctagon,
  ArrowRight,
  RefreshCw,
  PlusCircle,
} from "lucide-react";
import { getClinicalQueue, QueueResponse } from "@/lib/api";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { UncertaintyIndicator } from "@/components/ui/UncertaintyIndicator";
import { SearchField } from "@/components/ui/FormControls";
import { FilterBar } from "@/components/ui/FilterBar";
import { Button } from "@/components/ui/Button";
import { LoadingState, EmptyState } from "@/components/ui/States";

export const NurseTriageQueue: React.FC = () => {
  const [queueData, setQueueData] = useState<QueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterTier, setFilterTier] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const loadQueue = useCallback(async (acuity?: string) => {
    setLoading(true);
    try {
      const selected = acuity !== undefined ? acuity : filterTier;
      const data = await getClinicalQueue(selected !== "ALL" ? { acuity: selected } : undefined);
      setQueueData(data);
    } catch (err) {
      console.warn("Failed to load queue:", err);
    } finally {
      setLoading(false);
    }
  }, [filterTier]);

  useEffect(() => {
    void loadQueue(filterTier);
  }, [loadQueue, filterTier]);

  const queue = queueData?.queue || [];

  const filteredQueue = queue.filter((item) => {
    if (filterTier !== "ALL" && item.acuity_tier !== filterTier) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchPt = item.patient_synthetic_id.toLowerCase().includes(q);
      const matchCase = item.case_id.toLowerCase().includes(q);
      const matchComplaint = item.presenting_complaint.toLowerCase().includes(q);
      const matchSyndrome = (item.primary_syndrome || "").toLowerCase().includes(q);
      return matchPt || matchCase || matchComplaint || matchSyndrome;
    }
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
      {/* Workstation Top Bar / Stats */}
      <div className="clinova-grid-4col">
        <div className="clinova-card" style={{ padding: "12px 16px", borderLeft: "4px solid var(--clinova-emergency)" }}>
          <span className="clinova-label">P1 — Critical Cases</span>
          <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--clinova-danger-text)", margin: "2px 0" }}>
            {queueData?.critical_count || 0}
          </div>
          <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
            Immediate Resuscitation Gate
          </span>
        </div>

        <div className="clinova-card" style={{ padding: "12px 16px", borderLeft: "4px solid var(--clinova-warning)" }}>
          <span className="clinova-label">P2 — Urgent Cases</span>
          <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--clinova-warning-text)", margin: "2px 0" }}>
            {queueData?.urgent_count || 0}
          </div>
          <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
            Bedside Evaluation &lt;30m
          </span>
        </div>

        <div className="clinova-card" style={{ padding: "12px 16px", borderLeft: "4px solid var(--clinova-informational)" }}>
          <span className="clinova-label">P3 — Moderate Cases</span>
          <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--clinova-informational-text)", margin: "2px 0" }}>
            {queueData?.moderate_count || 0}
          </div>
          <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
            Standard Vital Tracking &lt;60m
          </span>
        </div>

        <div className="clinova-card" style={{ padding: "12px 16px", borderLeft: "4px solid var(--clinova-success)" }}>
          <span className="clinova-label">P4 — Routine OPD</span>
          <div className="clinova-mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--clinova-success-text)", margin: "2px 0" }}>
            {queueData?.routine_count || 0}
          </div>
          <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
            Outpatient Queue
          </span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div
        className="clinova-card"
        style={{
          padding: "var(--clinova-space-3) var(--clinova-space-4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <FilterBar
          label="Filter Acuity:"
          selectedId={filterTier}
          onSelect={setFilterTier}
          options={[
            { id: "ALL", label: "ALL", count: queue.length },
            { id: "CRITICAL", label: "CRITICAL", count: queueData?.critical_count },
            { id: "URGENT", label: "URGENT", count: queueData?.urgent_count },
            { id: "MODERATE", label: "MODERATE", count: queueData?.moderate_count },
            { id: "ROUTINE", label: "ROUTINE", count: queueData?.routine_count },
          ]}
        />

        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <SearchField
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search cases or symptoms..."
          />
          <Button variant="secondary" size="sm" onClick={() => { void loadQueue(); }}>
            <RefreshCw style={{ width: 13, height: 13 }} aria-hidden="true" />
            <span>Refresh</span>
          </Button>
          <Link href="/patient/intake" className="clinova-btn clinova-btn-primary clinova-btn-sm" style={{ textDecoration: "none" }}>
            <PlusCircle style={{ width: 13, height: 13 }} aria-hidden="true" />
            <span>New Intake</span>
          </Link>
        </div>
      </div>

      {/* Triage Queue List / Table */}
      {loading ? (
        <LoadingState message="Fetching active triage worklist..." />
      ) : filteredQueue.length === 0 ? (
        <EmptyState
          title="No Cases Matching Criteria"
          description="Adjust your search query or acuity filter to inspect other patients in the clinical queue."
          action={{ label: "Reset Filters", onClick: () => { setFilterTier("ALL"); setSearchQuery(""); } }}
        />
      ) : (
        <div className="clinova-table-wrapper">
          <table className="clinova-table">
            <thead>
              <tr>
                <th>Case & Patient</th>
                <th>Acuity Tier</th>
                <th>Chief Complaint & Syndrome</th>
                <th>Vitals & Red Flags</th>
                <th>Wait / SLA</th>
                <th>Uncertainty & Provenance</th>
                <th>Recommended Action</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredQueue.map((item) => {
                const isEmergency = Boolean(
                  item.emergency_active ||
                  item.has_critical_red_flags ||
                  (item.critical_red_flags_count && item.critical_red_flags_count > 0)
                );
                const rfCount = item.critical_red_flags_count || item.red_flags_count || 0;

                return (
                <tr
                  key={item.case_id}
                  style={{
                    backgroundColor: isEmergency ? "rgba(254, 242, 242, 0.45)" : undefined,
                  }}
                >
                  {/* Case & Patient */}
                  <td>
                    <div style={{ display: "flex", flexDirection: "column" }}>
                      <strong className="clinova-mono" style={{ fontSize: "0.875rem", color: "var(--clinova-text-primary)" }}>
                        {item.case_id}
                      </strong>
                      <span className="clinova-mono" style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                        {item.patient_synthetic_id}
                      </span>
                      <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                        {item.age_bracket} • {item.biological_sex}
                      </span>
                    </div>
                  </td>

                  {/* Acuity Tier & Operational Priority */}
                  <td>
                    <PriorityBadge tier={item.acuity_tier} />
                    {item.priority_tier && (
                      <span className="clinova-mono" style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", marginTop: 2, display: "block" }}>
                        {item.priority_tier}
                      </span>
                    )}
                    {isEmergency && (
                      <span
                        className="clinova-badge"
                        style={{
                          backgroundColor: "var(--clinova-emergency-bg)",
                          color: "var(--clinova-emergency-text)",
                          borderColor: "var(--clinova-emergency-border)",
                          marginTop: 4,
                          display: "inline-flex",
                        }}
                      >
                        EMERGENCY FAST-TRACK
                      </span>
                    )}
                  </td>

                  {/* Complaint & Syndrome */}
                  <td style={{ maxWidth: 280 }}>
                    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                      <strong style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)" }}>
                        {item.primary_syndrome || "Pending syndromic categorization"}
                      </strong>
                      <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)", lineHeight: 1.3 }}>
                        {item.presenting_complaint}
                      </p>
                    </div>
                  </td>

                  {/* Vitals & Red Flags */}
                  <td>
                    <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        {item.vitals_overall_status && (
                          <span
                            className="clinova-badge"
                            style={{
                              fontSize: "0.625rem",
                              padding: "1px 5px",
                              fontWeight: 600,
                              backgroundColor:
                                item.vitals_overall_status === "AVAILABLE"
                                  ? "var(--clinova-success-bg)"
                                  : item.vitals_overall_status === "STALE"
                                  ? "var(--clinova-warning-bg)"
                                  : "var(--clinova-danger-bg)",
                              color:
                                item.vitals_overall_status === "AVAILABLE"
                                  ? "var(--clinova-success-text)"
                                  : item.vitals_overall_status === "STALE"
                                  ? "var(--clinova-warning-text)"
                                  : "var(--clinova-danger-text)",
                              borderColor:
                                item.vitals_overall_status === "AVAILABLE"
                                  ? "var(--clinova-success-border)"
                                  : item.vitals_overall_status === "STALE"
                                  ? "var(--clinova-warning-border)"
                                  : "var(--clinova-danger-border)",
                            }}
                          >
                            {item.vitals_overall_status}
                          </span>
                        )}
                        {item.latest_vitals ? (
                          <span className="clinova-mono" style={{ fontSize: "0.75rem" }}>
                            BP: <strong>{item.latest_vitals.bp || "—"}</strong> | HR: <strong>{item.latest_vitals.hr || "—"}</strong>
                          </span>
                        ) : (
                          <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)", fontStyle: "italic" }}>
                            Vitals pending entry
                          </span>
                        )}
                      </div>

                      {item.missing_critical_vitals && item.missing_critical_vitals.length > 0 && (
                        <span style={{ fontSize: "0.6875rem", color: "var(--clinova-warning-text)" }}>
                          Missing: {item.missing_critical_vitals.join(", ")}
                        </span>
                      )}

                      {rfCount > 0 ? (
                        <span
                          className="clinova-badge"
                          style={{
                            backgroundColor: "var(--clinova-danger-bg)",
                            color: "var(--clinova-danger-text)",
                            borderColor: "var(--clinova-danger-border)",
                            alignSelf: "flex-start",
                          }}
                        >
                          <AlertOctagon style={{ width: 10, height: 10 }} aria-hidden="true" />
                          <span>{rfCount} RED FLAG{rfCount > 1 ? "S" : ""}</span>
                        </span>
                      ) : (
                        <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                          No acute red flags
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Wait Time & SLA */}
                  <td>
                    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 4,
                          fontSize: "0.8125rem",
                          fontWeight: 600,
                          color: item.sla_breached ? "var(--clinova-danger-text)" : "var(--clinova-text-primary)",
                        }}
                      >
                        <Clock style={{ width: 13, height: 13 }} aria-hidden="true" />
                        <span>{item.waiting_minutes}m</span>
                      </div>
                      <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                        SLA Target: {item.sla_limit_minutes}m
                      </span>
                    </div>
                  </td>

                  {/* Uncertainty & Provenance */}
                  <td>
                    <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "flex-start" }}>
                      <UncertaintyIndicator status={item.epistemic_status} />
                      <ProvenanceBadge provenance={item.provenance_type} showIcon={false} />
                    </div>
                  </td>

                  {/* Next Recommended Action */}
                  <td>
                    <span
                      className="clinova-badge"
                      style={{
                        backgroundColor: "var(--clinova-surface-subtle)",
                        color: "var(--clinova-text-primary)",
                        borderColor: "var(--clinova-border)",
                        fontWeight: 600,
                      }}
                    >
                      {item.next_recommended_action}
                    </span>
                  </td>

                  {/* Review Action */}
                  <td style={{ textAlign: "right" }}>
                    <Link
                      href={`/staff/cases/${item.case_id}`}
                      className="clinova-btn clinova-btn-secondary clinova-btn-sm"
                      style={{ textDecoration: "none" }}
                    >
                      <span>Examine</span>
                      <ArrowRight style={{ width: 12, height: 12 }} aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
