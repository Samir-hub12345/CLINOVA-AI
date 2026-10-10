"use client";

import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { ConnectionStatus } from "@/components/common/ConnectionStatus";
import { DataTable, ColumnDef } from "@/components/ui/DataTable";
import { MOCK_AUDIT_LOGS } from "@/mock/auditLogs";
import { AuditLogEntry } from "@/types";
import { ShieldCheck, Database, Key } from "lucide-react";
import { RoleGuard } from "@/components/common/RoleGuard";
import { RecentActivityWidget } from "@/components/dashboard";

export default function SystemPage() {
  const columns: ColumnDef<AuditLogEntry>[] = [
    {
      header: "ID",
      width: "80px",
      accessor: (row) => (
        <span className="clinova-mono" style={{ fontWeight: 700 }}>
          #{row.id}
        </span>
      ),
    },
    {
      header: "Timestamp",
      width: "160px",
      accessor: (row) => (
        <span className="clinova-mono" style={{ fontSize: "0.75rem" }}>
          {row.timestamp}
        </span>
      ),
    },
    {
      header: "Actor",
      width: "180px",
      accessor: (row) => (
        <div>
          <strong>{row.actor_id}</strong>
          <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", display: "block" }}>
            {row.actor_role}
          </span>
        </div>
      ),
    },
    {
      header: "Action",
      width: "160px",
      accessor: (row) => (
        <span
          className="clinova-badge"
          style={{ backgroundColor: "#f1f5f9", color: "#334155", borderColor: "#cbd5e1" }}
        >
          {row.action}
        </span>
      ),
    },
    {
      header: "Entity",
      accessor: (row) => (
        <span style={{ fontSize: "0.75rem" }}>
          {row.entity_type} ({row.entity_id})
        </span>
      ),
    },
    {
      header: "Provenance",
      width: "180px",
      accessor: (row) => (
        <ProvenanceBadge provenance={row.provenance_type} showIcon={false} />
      ),
    },
    {
      header: "Details",
      accessor: (row) => (
        <span style={{ fontSize: "0.75rem", maxWidth: 240, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", display: "block" }}>
          {JSON.stringify(row.details)}
        </span>
      ),
    },
  ];

  return (
    <RoleGuard
      allowedRoles={["SYSTEM_ADMIN", "AUDITOR"]}
      title="System Audit Access Restricted"
      message="Only system administrators and compliance auditors may view tamper-evident system audit logs."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-6)" }}>
        <PageHeader
          title="Developer & System Audit Workbench"
          subtitle="Tamper-evident clinical provenance ledger, zero-PII sanitization compliance, and system status"
          breadcrumbs={[{ label: "Home", href: "/" }, { label: "System Audit" }]}
        />

        {/* Top Architecture Status Cards */}
        <div className="clinova-grid-3col">
          <div className="clinova-card" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <ShieldCheck style={{ width: 28, height: 28, color: "var(--clinova-success)" }} aria-hidden="true" />
            <div>
              <span className="clinova-label">COMPLIANCE LEDGER</span>
              <strong style={{ fontSize: "1rem", display: "block" }}>Section 63 BSA Certified</strong>
              <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>Tamper-Evident SHA-256</span>
            </div>
          </div>

          <div className="clinova-card" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Database style={{ width: 28, height: 28, color: "var(--clinova-informational)" }} aria-hidden="true" />
            <div>
              <span className="clinova-label">DATA ENVIRONMENT</span>
              <strong style={{ fontSize: "1rem", display: "block" }}>CLINOVA Synthetic Mode</strong>
              <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>Zero Real Patient PII</span>
            </div>
          </div>

          <div className="clinova-card" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Key style={{ width: 28, height: 28, color: "var(--clinova-accent)" }} aria-hidden="true" />
            <div>
              <span className="clinova-label">SECURITY BOUNDARY</span>
              <strong style={{ fontSize: "1rem", display: "block" }}>Zero Secrets Exposed</strong>
              <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>No Service Role in Bundle</span>
            </div>
          </div>
        </div>

        {/* Recent Patient Activity / Provenance Feed */}
        <RecentActivityWidget compact={true} />

        {/* Audit Log Table */}
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h3 style={{ fontSize: "1.125rem", margin: 0 }}>Audit Trail Ledger</h3>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)", margin: "4px 0 0 0" }}>
                Chronological log of clinical decisions, evidence overrides, and algorithmic advisory generation.
              </p>
            </div>
            <ConnectionStatus status="ONLINE" />
          </div>

          <DataTable
            columns={columns}
            data={MOCK_AUDIT_LOGS}
            keyExtractor={(row) => String(row.id)}
            ariaLabel="Tamper-Evident Audit Trail Ledger"
          />
        </div>
      </div>
    </RoleGuard>
  );
}
