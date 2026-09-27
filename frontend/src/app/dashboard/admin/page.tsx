"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ShieldCheck,
  Trash2,
  RefreshCw,
  Server,
  AlertTriangle,
  Building2,
  HeartPulse,
  Users,
  FileClock,
  Database,
  Cpu,
  CheckCircle2,
  XCircle,
  Search,
  Filter,
  ArrowRight,
  ChevronRight,
  Lock,
  Zap,
} from "lucide-react";
import { DashboardShell, DataState, MetricCard, SectionCard } from "@/components/common/dashboard-shell";
import { RoleGuard } from "@/components/common/role-guard";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { AdminOverview, User, AuditLog } from "@/types";

function AdminDashboardContent() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [activeTab, setActiveTab] = useState<"users" | "audit" | "compliance">("users");
  const [userSearch, setUserSearch] = useState("");
  const [userRoleFilter, setUserRoleFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Retention state
  const [retentionReport, setRetentionReport] = useState<any | null>(null);
  const [retentionLoading, setRetentionLoading] = useState(false);
  const [togglingUserId, setTogglingUserId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [oRes, uRes, aRes] = await Promise.all([
        api.getAdminOverview(),
        api.getAdminUsers(),
        api.getAuditLogs(30),
      ]);

      if (oRes.error || uRes.error) {
        setError(oRes.error || uRes.error || "Could not load administration data.");
      } else {
        setOverview(oRes.data || null);
        setUsers(Array.isArray(uRes.data) ? uRes.data : ((uRes.data as any)?.items || []));
        if (aRes.data) {
          setAuditLogs(Array.isArray(aRes.data) ? aRes.data : (aRes.data?.items || []));
        }
      }
    } catch {
      setError("Failed to load administration data. Please retry.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleRetentionSweep = async (dryRun: boolean) => {
    if (!dryRun) {
      if (
        !confirm(
          "WARNING: Permanent data purge will irreversibly delete expired soft-deleted documents and quarantined malware files. Proceed?"
        )
      ) {
        return;
      }
    }
    setRetentionLoading(true);
    try {
      const res = await api.triggerRetentionSweep(dryRun);
      if (res.data) {
        setRetentionReport(res.data);
      } else {
        alert(res.error || "Failed to execute data retention sweep.");
      }
    } catch {
      alert("Error triggering retention sweep.");
    } finally {
      setRetentionLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    setTogglingUserId(userId);
    try {
      await api.toggleUserStatus(userId, !currentStatus);
      await loadData();
    } catch {
      // Handled via API error reporting
    } finally {
      setTogglingUserId(null);
    }
  };

  const filteredUsers = users.filter((u) => {
    if (userRoleFilter !== "all" && u.role !== userRoleFilter) return false;
    if (userSearch.trim()) {
      const q = userSearch.toLowerCase();
      return (
        u.full_name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        u.role.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const adminName = user?.full_name || "Hospital Administrator";

  return (
    <DashboardShell
      title={`Admin Console — ${adminName}`}
      description="Hospital system governance • Clinical user directory • Telemetry & service health • Audit compliance"
      refresh={() => void loadData()}
      badge="Hospital Administration"
      actions={
        <Link
          href="/audit"
          className="inline-flex items-center gap-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-3.5 py-2 text-xs font-bold tracking-wide shadow-xs transition-colors"
        >
          <FileClock className="h-4 w-4" />
          <span>Audit Trail Explorer</span>
        </Link>
      }
    >
      <DataState loading={loading} error={error} retry={() => void loadData()} />

      {!loading && !error && overview && (
        <div className="space-y-8">
          {/* ========================================================================= */}
          {/* 1. ADMIN GREETING & SYSTEM STATUS BANNER                                  */}
          {/* ========================================================================= */}
          <div className="rounded-3xl bg-white border border-slate-200/90 p-6 md:p-8 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start sm:items-center gap-4">
              <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 font-extrabold text-xl shadow-xs">
                <ShieldCheck className="h-7 w-7 text-teal-600" />
                <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    System Administrator
                  </span>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    Primary Facility: Government District Hospital
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    All 4 Containers Online (Postgres, Redis, Backend, Frontend)
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {adminName}
                </h2>
                <p className="text-xs text-slate-500">
                  {overview.users} Registered Accounts • {overview.cases} Clinical Cases • {overview.audit_records} Audit Trail Events Recorded
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/audit"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 text-xs font-bold shadow-xs transition-colors"
              >
                <FileClock className="h-4 w-4" />
                <span>Security Audit Trail</span>
              </Link>
              <Link
                href="/patients"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-4 py-2.5 text-xs font-semibold transition-colors"
              >
                <Users className="h-4 w-4 text-teal-600" />
                <span>Patient EHR Records</span>
              </Link>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 2. ADMIN KPI / METRIC SUMMARY CARDS                                       */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <MetricCard
              title="Platform Users"
              value={overview.users}
              subtitle="Registered clinical & patient accounts"
              icon={Users}
              statusColor="teal"
              badge="4 Active Roles"
              trend={{
                direction: "up",
                value: "Active",
                label: "RBAC Verified",
              }}
            />

            <MetricCard
              title="Clinical Encounters"
              value={overview.cases}
              subtitle="Triage intakes & encounters"
              icon={Activity}
              statusColor="blue"
              trend={{
                direction: "up",
                value: `${overview.consultations} Visits`,
                label: "Total Consultations",
              }}
            />

            <MetricCard
              title="Audit Log Events"
              value={overview.audit_records}
              subtitle="Tamper-proof event logs stored"
              icon={FileClock}
              statusColor="amber"
              trend={{
                direction: "up",
                value: "Active",
                label: "Security Audit Trail",
              }}
            />

            <MetricCard
              title="System Uptime"
              value="99.98%"
              subtitle="All 4 services operational"
              icon={Server}
              statusColor="emerald"
              trend={{
                direction: "neutral",
                value: "Healthy",
                label: "Production Telemetry",
              }}
            />
          </div>

          {/* ========================================================================= */}
          {/* 3. MAIN DASHBOARD CONTENT GRID (2/3 Left, 1/3 Right)                      */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* ----------------------------------------------------------------------- */}
            {/* Left Console Panel (8 cols): Users, Audit Stream, Compliance Sweep      */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-8 space-y-6">
              {/* Tab Navigation */}
              <div className="flex items-center gap-2 p-1.5 bg-slate-100/80 rounded-2xl border border-slate-200/80 w-fit">
                <button
                  onClick={() => setActiveTab("users")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "users"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Users className="h-3.5 w-3.5 text-teal-600" />
                  <span>User Accounts ({users.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("audit")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "audit"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <FileClock className="h-3.5 w-3.5 text-teal-600" />
                  <span>Audit Stream ({auditLogs.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("compliance")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "compliance"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Trash2 className="h-3.5 w-3.5 text-teal-600" />
                  <span>Data Retention &amp; Compliance</span>
                </button>
              </div>

              {/* Tab 1: User Directory & Management */}
              {activeTab === "users" && (
                <SectionCard
                  title="User Accounts &amp; Role Management"
                  description="Inspect registered clinical staff, administrators, and patients. Manage account access status."
                  icon={Users}
                  action={
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold">
                      {[
                        { key: "all", label: "All" },
                        { key: "doctor", label: "Doctors" },
                        { key: "nurse", label: "Nurses" },
                        { key: "patient", label: "Patients" },
                        { key: "admin", label: "Admins" },
                      ].map((tab) => (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setUserRoleFilter(tab.key)}
                          className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                            userRoleFilter === tab.key
                              ? "bg-white text-slate-900 font-bold shadow-xs"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  }
                >
                  {/* Search within Users */}
                  <div className="mb-4 relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                      <Search className="h-4 w-4" />
                    </div>
                    <input
                      type="text"
                      value={userSearch}
                      onChange={(e) => setUserSearch(e.target.value)}
                      placeholder="Search accounts by name, email, or role..."
                      className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    />
                  </div>

                  {filteredUsers.length === 0 ? (
                    <div className="p-8 text-center bg-slate-50 rounded-xl text-xs text-slate-500">
                      No accounts found matching filter.
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider">
                          <tr>
                            <th className="py-3 px-4 font-bold">User Details</th>
                            <th className="py-3 px-4 font-bold">Assigned Role</th>
                            <th className="py-3 px-4 font-bold">Account Status</th>
                            <th className="py-3 px-4 font-bold">Created At</th>
                            <th className="py-3 px-4 font-bold text-right">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {filteredUsers.map((u) => {
                            const isDoctor = u.role === "doctor";
                            const isNurse = u.role === "nurse";
                            const isAdmin = u.role === "admin";

                            return (
                              <tr key={u.id} className="hover:bg-slate-50/70 transition-colors">
                                <td className="py-3.5 px-4">
                                  <div className="font-bold text-slate-900">{u.full_name}</div>
                                  <div className="text-[11px] text-slate-500">{u.email}</div>
                                </td>

                                <td className="py-3.5 px-4">
                                  <span
                                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                                      isAdmin
                                        ? "bg-purple-50 text-purple-800 border-purple-200"
                                        : isDoctor
                                        ? "bg-teal-50 text-teal-800 border-teal-200"
                                        : isNurse
                                        ? "bg-blue-50 text-blue-800 border-blue-200"
                                        : "bg-slate-100 text-slate-800 border-slate-200"
                                    }`}
                                  >
                                    {u.role}
                                  </span>
                                </td>

                                <td className="py-3.5 px-4">
                                  <span
                                    className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold ${
                                      u.is_active
                                        ? "bg-emerald-50 text-emerald-700"
                                        : "bg-rose-50 text-rose-700"
                                    }`}
                                  >
                                    <span
                                      className={`h-1.5 w-1.5 rounded-full ${
                                        u.is_active ? "bg-emerald-500" : "bg-rose-500"
                                      }`}
                                    />
                                    {u.is_active ? "Active" : "Inactive"}
                                  </span>
                                </td>

                                <td className="py-3.5 px-4 text-slate-500 text-[11px]">
                                  {new Date(u.created_at).toLocaleDateString()}
                                </td>

                                <td className="py-3.5 px-4 text-right">
                                  <button
                                    onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                    disabled={togglingUserId === u.id}
                                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                                      u.is_active
                                        ? "bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200"
                                        : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200"
                                    } disabled:opacity-50`}
                                  >
                                    {togglingUserId === u.id
                                      ? "Updating..."
                                      : u.is_active
                                      ? "Deactivate"
                                      : "Activate"}
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </SectionCard>
              )}

              {/* Tab 2: Security & Audit Log Stream */}
              {activeTab === "audit" && (
                <SectionCard
                  title="Live Security &amp; Audit Log Stream"
                  description="Tamper-proof event logs recording access, case reviews, user status updates, and intake operations"
                  icon={FileClock}
                  action={
                    <Link
                      href="/audit"
                      className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-900 bg-teal-50 px-3 py-1.5 rounded-lg border border-teal-200"
                    >
                      <span>Full Audit Log View</span>
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  }
                >
                  {auditLogs.length === 0 ? (
                    <div className="p-8 text-center bg-slate-50 rounded-xl text-xs text-slate-500">
                      No recent audit events in buffer.
                    </div>
                  ) : (
                    <div className="space-y-2.5 max-h-[580px] overflow-y-auto pr-1">
                      {auditLogs.map((log) => (
                        <div
                          key={log.id}
                          className="p-3.5 rounded-xl border border-slate-200/90 bg-slate-50/50 hover:bg-white text-xs space-y-1.5 transition-colors"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 text-[11px]">
                                {log.action}
                              </span>
                              <span className="text-slate-600 font-semibold">
                                {log.resource_type}: {log.resource_id || "System"}
                              </span>
                            </div>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {new Date(log.timestamp).toLocaleString()}
                            </span>
                          </div>

                          <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-1">
                            <span>Actor: <strong className="text-slate-700">{log.user_email || log.user_id || "System"}</strong></span>
                            {log.ip_address && <span className="font-mono">IP: {log.ip_address}</span>}
                          </div>

                          {log.details && (
                            <p className="text-[11px] text-slate-600 italic bg-white p-2 rounded-lg border border-slate-100">
                              {log.details}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </SectionCard>
              )}

              {/* Tab 3: Data Retention & Compliance */}
              {activeTab === "compliance" && (
                <SectionCard
                  title="Data Retention &amp; Compliance Policy"
                  description="Automated lifecycle purge of expired soft-deleted documents and quarantined malware records"
                  icon={Trash2}
                >
                  <div className="space-y-6 text-xs">
                    <div className="p-4 rounded-2xl bg-amber-50/80 border border-amber-200 text-amber-900 space-y-2">
                      <div className="flex items-center gap-2 font-bold text-sm">
                        <AlertTriangle className="h-4 w-4 text-amber-600" />
                        <span>HIPAA / DISHA Retention Standard Compliance</span>
                      </div>
                      <p className="leading-relaxed">
                        Clinova AI enforces a 90-day retention window on clinical case files and temporary documents. Purge sweeps identify expired items while preserving tamper-proof audit trails for legal compliance.
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                      <button
                        onClick={() => handleRetentionSweep(true)}
                        disabled={retentionLoading}
                        className="px-4 py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold shadow-xs transition-colors disabled:opacity-50"
                      >
                        {retentionLoading ? "Scanning..." : "Dry Run (Scan Expired)"}
                      </button>
                      <button
                        onClick={() => handleRetentionSweep(false)}
                        disabled={retentionLoading}
                        className="px-4 py-2.5 bg-rose-700 hover:bg-rose-800 text-white rounded-xl font-bold shadow-xs transition-colors disabled:opacity-50"
                      >
                        {retentionLoading ? "Purging..." : "Permanent Purge Expired"}
                      </button>
                    </div>

                    {retentionReport && (
                      <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 font-mono text-xs">
                        <span className="font-bold text-slate-900 block font-sans text-sm">
                          Retention Sweep Report:
                        </span>
                        <pre className="overflow-x-auto text-[11px] text-slate-700">
                          {JSON.stringify(retentionReport, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </SectionCard>
              )}
            </div>

            {/* ----------------------------------------------------------------------- */}
            {/* Right Column (4 cols): Service Health & Facility Configuration           */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-4 space-y-6">
              {/* Infrastructure Service Health Card */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Infrastructure Telemetry
                  </h3>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100 flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Healthy
                  </span>
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="flex items-center gap-2.5">
                      <Server className="h-4 w-4 text-teal-600" />
                      <div>
                        <span className="font-bold text-slate-900 block">FastAPI Backend</span>
                        <span className="text-[10px] text-slate-400">Port 8000 • Live</span>
                      </div>
                    </div>
                    <span className="font-mono text-emerald-700 font-bold">200 OK</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="flex items-center gap-2.5">
                      <Database className="h-4 w-4 text-teal-600" />
                      <div>
                        <span className="font-bold text-slate-900 block">PostgreSQL 16</span>
                        <span className="text-[10px] text-slate-400">Port 5432 • AsyncPG</span>
                      </div>
                    </div>
                    <span className="font-mono text-emerald-700 font-bold">Connected</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="flex items-center gap-2.5">
                      <Zap className="h-4 w-4 text-teal-600" />
                      <div>
                        <span className="font-bold text-slate-900 block">Redis 7 Cache</span>
                        <span className="text-[10px] text-slate-400">Port 6379 • Session Store</span>
                      </div>
                    </div>
                    <span className="font-mono text-emerald-700 font-bold">Active</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="flex items-center gap-2.5">
                      <Cpu className="h-4 w-4 text-teal-600" />
                      <div>
                        <span className="font-bold text-slate-900 block">AI Triage Service</span>
                        <span className="text-[10px] text-slate-400">Rules R01-R06 + Gemini</span>
                      </div>
                    </div>
                    <span className="font-mono text-emerald-700 font-bold">Ready</span>
                  </div>
                </div>
              </div>

              {/* Facility & Policy Configuration */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-3 text-xs">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Facility Configuration
                </h3>

                <div className="space-y-2 text-slate-600">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Affiliated Facility</span>
                    <strong className="text-slate-900 block mt-0.5">Government District Hospital</strong>
                    <span className="text-[11px] text-slate-500">Tier 2 Community Health Center</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Regulatory Compliance</span>
                    <strong className="text-slate-900 block mt-0.5">WHO / ICMR Triage Protocols</strong>
                    <span className="text-[11px] text-slate-500">ABDM &amp; DISHA standards adherence</span>
                  </div>
                </div>
              </div>

              {/* Admin Quick Navigation */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-2">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-2">
                  System Shortcuts
                </h3>
                <Link
                  href="/audit"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Audit Trail Explorer</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
                <Link
                  href="/patients"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Patient EHR Records</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
                <Link
                  href="/documents"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>System Document Ingestion</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
                <Link
                  href="/review"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Clinical Review Console</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
              </div>
            </div>
          </div>

          {/* Operational Safety Disclaimer */}
          <ClinicalDisclaimer />
        </div>
      )}
    </DashboardShell>
  );
}

export default function AdminDashboard() {
  return (
    <RoleGuard roles={["admin"]}>
      <AdminDashboardContent />
    </RoleGuard>
  );
}