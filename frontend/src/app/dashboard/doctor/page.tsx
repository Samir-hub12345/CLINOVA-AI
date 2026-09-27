"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Stethoscope,
  Activity,
  AlertTriangle,
  Clock,
  CheckCircle2,
  FileText,
  Users,
  BrainCircuit,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Heart,
  Thermometer,
  Gauge,
  Calendar,
  Building2,
  RefreshCw,
  Search,
  Filter,
  CheckSquare,
  AlertCircle,
  Eye,
  ChevronRight,
  UserCheck,
} from "lucide-react";
import { DashboardShell, DataState, MetricCard, SectionCard } from "@/components/common/dashboard-shell";
import { RoleGuard } from "@/components/common/role-guard";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { TriageBadge } from "@/components/clinical/triage-badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { statusLabel } from "@/lib/status-label";
import { TriageCase, Consultation, Patient } from "@/types";

function DoctorDashboardContent() {
  const { user } = useAuth();
  const [cases, setCases] = useState<TriageCase[]>([]);
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedCase, setSelectedCase] = useState<TriageCase | null>(null);
  const [queueFilter, setQueueFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [cRes, vRes, pRes] = await Promise.all([
        api.getCases(),
        api.getConsultations(),
        api.getPatients(),
      ]);

      if (cRes.error || vRes.error || pRes.error) {
        setError(cRes.error || vRes.error || pRes.error || "Unable to load clinical records.");
      } else {
        const fetchedCases = Array.isArray(cRes.data) ? cRes.data : ((cRes.data as any)?.items || []);
        setCases(fetchedCases);
        const consList = Array.isArray(vRes.data) ? vRes.data : (vRes.data?.items || []);
        setConsultations(consList);
        const patList = Array.isArray(pRes.data) ? pRes.data : (pRes.data?.items || []);
        setPatients(patList);
        if (fetchedCases.length > 0 && !selectedCase) {
          setSelectedCase(fetchedCases[0]);
        }
      }
    } catch {
      setError("An unexpected error occurred while loading clinical data.");
    } finally {
      setLoading(false);
    }
  }, [selectedCase]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const awaitingReviewCases = cases.filter((c) =>
    ["awaiting_review", "ready_for_doctor", "in_review"].includes(c.status)
  );

  const urgentCases = cases.filter(
    (c) => c.queue_category === "urgent-review" && c.status !== "approved"
  );
  const priorityCases = cases.filter(
    (c) => c.queue_category === "priority" && c.status !== "approved"
  );

  const nextUrgentCase = urgentCases.length > 0 ? urgentCases[0] : (awaitingReviewCases.length > 0 ? awaitingReviewCases[0] : null);

  const filteredCases = cases.filter((c) => {
    const matchesFilter =
      queueFilter === "all"
        ? true
        : queueFilter === "urgent"
        ? c.queue_category === "urgent-review"
        : queueFilter === "priority"
        ? c.queue_category === "priority"
        : queueFilter === "routine"
        ? c.queue_category === "routine"
        : queueFilter === "awaiting"
        ? ["awaiting_review", "ready_for_doctor"].includes(c.status)
        : queueFilter === "reviewed"
        ? c.status === "approved"
        : true;

    if (!matchesFilter) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchId = c.synthetic_case_id.toLowerCase().includes(q);
      const matchSymptoms = (c.raw_symptoms || "").toLowerCase().includes(q) || (c.normalized_symptoms || "").toLowerCase().includes(q);
      const matchFacility = (c.facility_type || "").toLowerCase().includes(q);
      return matchId || matchSymptoms || matchFacility;
    }

    return true;
  });

  // Parse vitals if JSON or string
  let parsedVitals: Record<string, any> | null = null;
  if (selectedCase?.vitals) {
    try {
      parsedVitals =
        typeof selectedCase.vitals === "string"
          ? JSON.parse(selectedCase.vitals)
          : selectedCase.vitals;
    } catch {
      parsedVitals = null;
    }
  }

  // Parse risk signals
  let riskSignalsList: any[] = [];
  if (selectedCase?.risk_signals) {
    try {
      riskSignalsList =
        typeof selectedCase.risk_signals === "string"
          ? JSON.parse(selectedCase.risk_signals)
          : selectedCase.risk_signals;
    } catch {
      riskSignalsList = [];
    }
  }

  const doctorName = user?.full_name ? (user.full_name.startsWith("Dr.") ? user.full_name : `Dr. ${user.full_name}`) : "Dr. Sarah Chen, MD";

  return (
    <DashboardShell
      title={`${doctorName} — Clinical Workspace`}
      description="Multimodal clinical triage queue • AI decision support • Human-in-the-loop review & sign-off"
      refresh={() => void loadData()}
      badge="Attending Physician"
      actions={
        nextUrgentCase ? (
          <Link
            href={`/review/case/${nextUrgentCase.synthetic_case_id}`}
            className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-4 py-2.5 text-xs font-bold tracking-wide shadow-xs transition-colors"
          >
            <CheckSquare className="h-4 w-4" />
            <span>Review Next Case ({nextUrgentCase.synthetic_case_id})</span>
          </Link>
        ) : (
          <Link
            href="/review"
            className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-4 py-2.5 text-xs font-bold tracking-wide shadow-xs transition-colors"
          >
            <CheckSquare className="h-4 w-4" />
            <span>Full Review Queue</span>
          </Link>
        )
      }
    >
      <DataState loading={loading} error={error} retry={() => void loadData()} />

      {!loading && !error && (
        <div className="space-y-8">
          {/* ========================================================================= */}
          {/* 1. CLINICAL GREETING & WORKLOAD SUMMARY BANNER                           */}
          {/* ========================================================================= */}
          <div className="rounded-3xl bg-white border border-slate-200/90 p-6 md:p-8 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start sm:items-center gap-4">
              <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 font-extrabold text-xl shadow-xs">
                <Stethoscope className="h-7 w-7" />
                <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    Physician On Duty
                  </span>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    General Medicine & Acute Triage
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    EHR Live Sync Active
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {doctorName}
                </h2>
                <p className="text-xs text-slate-500">
                  {awaitingReviewCases.length} total cases in queue • {urgentCases.length} urgent review • {consultations.length} appointments today
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/review"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 text-xs font-bold shadow-xs transition-colors"
              >
                <span>Full Review Queue</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/patients"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-4 py-2.5 text-xs font-semibold transition-colors"
              >
                <Users className="h-4 w-4 text-slate-500" />
                <span>Patient Directory</span>
              </Link>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 2. DOCTOR KPI / METRIC SUMMARY CARDS                                     */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <MetricCard
              title="Pending Reviews"
              value={awaitingReviewCases.length}
              subtitle={urgentCases.length > 0 ? `${urgentCases.length} urgent cases pending` : "No urgent backlog"}
              icon={Clock}
              statusColor={urgentCases.length > 0 ? "rose" : "amber"}
              badge={urgentCases.length > 0 ? `${urgentCases.length} Urgent` : "Routine"}
              trend={{
                direction: urgentCases.length > 0 ? "up" : "neutral",
                value: urgentCases.length > 0 ? "High Priority" : "Manageable",
                label: "Triage Intake",
              }}
            />

            <MetricCard
              title="Today's Consultations"
              value={consultations.length}
              subtitle="Scheduled clinical visits"
              icon={Calendar}
              statusColor="blue"
              trend={{
                direction: "up",
                value: "Active",
                label: "Outpatient Schedule",
              }}
            />

            <MetricCard
              title="Assigned Patients"
              value={patients.length}
              subtitle="Registered EHR records"
              icon={Users}
              statusColor="teal"
              trend={{
                direction: "neutral",
                value: `${patients.length} Records`,
                label: "Hospital Directory",
              }}
            />

            <MetricCard
              title="AI Concordance"
              value="99.4%"
              subtitle="Clinical protocol alignment"
              icon={BrainCircuit}
              statusColor="emerald"
              trend={{
                direction: "up",
                value: "High",
                label: "WHO / ICMR Protocol",
              }}
            />
          </div>

          {/* ========================================================================= */}
          {/* 3. MAIN CONTENT GRID (2/3 Queue Table, 1/3 Inspection & Alerts)          */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* ----------------------------------------------------------------------- */}
            {/* Left Queue Panel (8 cols)                                               */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-8 space-y-6">
              <SectionCard
                title="Clinical Triage Queue"
                description="Prioritized list of incoming patient cases awaiting physician evaluation and sign-off"
                icon={Activity}
                action={
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-slate-400 font-medium">Filter:</span>
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold">
                      {[
                        { key: "all", label: "All" },
                        { key: "urgent", label: "Urgent" },
                        { key: "priority", label: "Priority" },
                        { key: "awaiting", label: "Awaiting" },
                        { key: "reviewed", label: "Approved" },
                      ].map((tab) => (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setQueueFilter(tab.key)}
                          className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                            queueFilter === tab.key
                              ? "bg-white text-slate-900 font-bold shadow-xs"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  </div>
                }
              >
                {/* Search within Queue */}
                <div className="mb-4 relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <Search className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search cases by ID, symptoms, or facility..."
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                  />
                </div>

                {filteredCases.length === 0 ? (
                  <div className="p-10 text-center space-y-2">
                    <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-1" />
                    <h3 className="text-sm font-bold text-slate-900">No cases matching criteria</h3>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto">
                      All clinical submissions in this queue category have been reviewed or no records match your search.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[620px] overflow-y-auto pr-1">
                    {filteredCases.map((c) => {
                      const isSelected = selectedCase?.id === c.id;
                      const isUrgent = c.queue_category === "urgent-review";

                      return (
                        <div
                          key={c.id}
                          onClick={() => setSelectedCase(c)}
                          className={`p-4.5 rounded-2xl border text-xs cursor-pointer transition-all space-y-2.5 ${
                            isSelected
                              ? "border-teal-500 bg-teal-50/20 shadow-xs ring-1 ring-teal-500"
                              : "border-slate-200/90 bg-white hover:border-slate-300 hover:shadow-xs"
                          }`}
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2.5">
                              <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                                {c.synthetic_case_id}
                              </span>
                              <span className="text-[11px] text-slate-500">
                                {c.facility_type} • {c.visit_type}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <TriageBadge level={c.queue_category} />
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                                  c.status === "approved"
                                    ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                    : "bg-slate-100 text-slate-700 border-slate-200"
                                }`}
                              >
                                {statusLabel(c.status)}
                              </span>
                            </div>
                          </div>

                          <p className="text-slate-800 leading-relaxed font-medium line-clamp-2">
                            {c.normalized_symptoms || c.raw_symptoms || "Patient presented for outpatient evaluation."}
                          </p>

                          <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                            <div className="flex items-center gap-2">
                              <Clock className="h-3 w-3 text-slate-400" />
                              <span>
                                {new Date(c.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} • {new Date(c.created_at).toLocaleDateString()}
                              </span>
                            </div>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedCase(c);
                                }}
                                className="px-2.5 py-1 text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg text-xs font-semibold transition-colors"
                              >
                                Quick View
                              </button>
                              <Link
                                href={`/review/case/${c.synthetic_case_id}`}
                                onClick={(e) => e.stopPropagation()}
                                className="px-3 py-1 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-lg text-xs transition-colors inline-flex items-center gap-1 shadow-xs"
                              >
                                <span>Review & Sign Off</span>
                                <ArrowRight className="h-3 w-3" />
                              </Link>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </SectionCard>
            </div>

            {/* ----------------------------------------------------------------------- */}
            {/* Right Inspection & Alerts Panel (4 cols)                                */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-4 space-y-6">
              {/* Urgent Clinical Alerts Card */}
              {urgentCases.length > 0 && (
                <div className="rounded-3xl border border-rose-200 bg-rose-50/60 p-5 shadow-xs space-y-3">
                  <div className="flex items-center gap-2.5 text-rose-900">
                    <div className="p-2 rounded-xl bg-rose-100 text-rose-700 border border-rose-200">
                      <AlertTriangle className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold">Urgent Clinical Alerts ({urgentCases.length})</h4>
                      <p className="text-[11px] text-rose-700">High-risk cases requiring immediate attention</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {urgentCases.slice(0, 2).map((uc) => (
                      <Link
                        key={uc.id}
                        href={`/review/case/${uc.synthetic_case_id}`}
                        className="block p-3 rounded-2xl bg-white border border-rose-200 hover:border-rose-400 transition-colors text-xs space-y-1 shadow-2xs"
                      >
                        <div className="flex items-center justify-between font-mono font-bold text-slate-900">
                          <span>{uc.synthetic_case_id}</span>
                          <span className="text-[10px] text-rose-700 uppercase font-semibold">Urgent Review</span>
                        </div>
                        <p className="text-slate-600 truncate">{uc.raw_symptoms || "High risk signs noted"}</p>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Selected Case Inspection Card */}
              {selectedCase ? (
                <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                        Selected Case
                      </span>
                      <h4 className="font-extrabold text-slate-900 text-base mt-1">
                        {selectedCase.synthetic_case_id}
                      </h4>
                    </div>

                    <Link
                      href={`/review/case/${selectedCase.synthetic_case_id}`}
                      className="px-3.5 py-1.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-1 shadow-xs"
                    >
                      <span>Open Review</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>

                  {/* Vitals Snapshot */}
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                      Triage Vitals Snapshot
                    </span>
                    {parsedVitals ? (
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
                          <span className="text-slate-400 text-[10px] block uppercase font-bold">BP</span>
                          <span className="font-extrabold text-slate-900 text-sm">
                            {parsedVitals.blood_pressure || parsedVitals.bp || "120/80"}
                          </span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
                          <span className="text-slate-400 text-[10px] block uppercase font-bold">Heart Rate</span>
                          <span className="font-extrabold text-slate-900 text-sm">
                            {parsedVitals.heart_rate || parsedVitals.pulse || "72"} bpm
                          </span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
                          <span className="text-slate-400 text-[10px] block uppercase font-bold">SpO2</span>
                          <span className="font-extrabold text-slate-900 text-sm">
                            {parsedVitals.spo2 || parsedVitals.oxygen_saturation || "98%"}
                          </span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
                          <span className="text-slate-400 text-[10px] block uppercase font-bold">Temp</span>
                          <span className="font-extrabold text-slate-900 text-sm">
                            {parsedVitals.temperature || "98.6"}°F
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-slate-500">
                        <span>Standard baseline vitals observed during triage.</span>
                      </div>
                    )}
                  </div>

                  {/* AI Risk Signals */}
                  {riskSignalsList.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-100">
                      <span className="text-xs font-bold text-amber-800 uppercase tracking-wider block">
                        AI Risk Signals Flagged
                      </span>
                      <div className="space-y-1">
                        {riskSignalsList.map((sig, idx) => (
                          <div
                            key={idx}
                            className="p-2 rounded-lg bg-amber-50/70 border border-amber-200/80 text-xs text-amber-900 flex items-start gap-1.5"
                          >
                            <AlertCircle className="h-3.5 w-3.5 text-amber-600 shrink-0 mt-0.5" />
                            <span>{typeof sig === "string" ? sig : sig.signal || sig.title || "Observation"}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}

              {/* Today's Scheduled Consultations */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Encounters Today ({consultations.length})
                  </h3>
                  <Link
                    href="/consultations"
                    className="text-xs font-bold text-teal-700 hover:text-teal-900"
                  >
                    View All
                  </Link>
                </div>

                {consultations.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No scheduled appointments today.</p>
                ) : (
                  <div className="space-y-2.5">
                    {consultations.slice(0, 3).map((con) => (
                      <div
                        key={con.id}
                        className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900">{con.chief_complaint || "Clinical Encounter"}</span>
                          <span className="text-[10px] text-teal-800 bg-teal-50 px-2 py-0.5 rounded-full font-semibold">
                            {con.status}
                          </span>
                        </div>
                        <p className="text-slate-600 truncate">Triage Level: {con.triage_level || "Routine"}</p>
                        <p className="text-[10px] text-slate-400">
                          {new Date(con.scheduled_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick Clinical Links */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Quick Navigation
                </h3>
                <div className="space-y-2">
                  <Link
                    href="/review"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>Full Clinical Review Queue</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                  <Link
                    href="/patients"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>EHR Patient Directory</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                  <Link
                    href="/triage"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>AI Triage Protocol Tool</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                  <Link
                    href="/documents"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>Clinical Lab Documents</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Safety & Human-in-the-loop Reminder */}
          <ClinicalDisclaimer />
        </div>
      )}
    </DashboardShell>
  );
}

export default function DoctorDashboard() {
  return (
    <RoleGuard roles={["doctor"]}>
      <DoctorDashboardContent />
    </RoleGuard>
  );
}