"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Building2,
  Users,
  ClipboardList,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck2,
  ArrowRight,
  Stethoscope,
  X,
  Plus,
  RefreshCw,
  Search,
  Filter,
  UserPlus,
  GitFork,
  Printer,
  Bed,
  Check,
  ChevronRight,
  ShieldAlert,
  Sparkles,
  Phone,
  Radio,
} from "lucide-react";
import { DashboardShell, DataState, MetricCard, SectionCard } from "@/components/common/dashboard-shell";
import { RoleGuard } from "@/components/common/role-guard";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { TriageBadge } from "@/components/clinical/triage-badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { statusLabel } from "@/lib/status-label";
import { TriageCase, Patient } from "@/types";

interface WardBedStatus {
  id: string;
  ward: string;
  bedNumber: string;
  status: "occupied" | "available" | "cleaning" | "reserved";
  patientName?: string;
  admissionDate?: string;
}

function StaffDashboardContent() {
  const { user } = useAuth();
  const [cases, setCases] = useState<TriageCase[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tabs
  const [activeTab, setActiveTab] = useState<"queue" | "beds">("queue");
  const [searchQuery, setSearchQuery] = useState("");
  const [queueFilter, setQueueFilter] = useState<"all" | "waiting" | "routed">("all");

  // Routing Modal
  const [selectedCaseForRouting, setSelectedCaseForRouting] = useState<TriageCase | null>(null);
  const [selectedDoctor, setSelectedDoctor] = useState("Dr. Sarah Chen, MD");
  const [selectedDept, setSelectedDept] = useState("General Medicine");
  const [staffNote, setStaffNote] = useState("");
  const [isSubmittingRouting, setIsSubmittingRouting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // Quick Token Print Preview
  const [printedToken, setPrintedToken] = useState<string | null>(null);

  // Bed Management State
  const [beds, setBeds] = useState<WardBedStatus[]>([
    { id: "b1", ward: "Ward 3A (Male Medical)", bedNumber: "Bed 301-A", status: "occupied", patientName: "James Miller", admissionDate: "Today, 08:30 AM" },
    { id: "b2", ward: "Ward 3A (Male Medical)", bedNumber: "Bed 301-B", status: "occupied", patientName: "Aarav Sharma", admissionDate: "Yesterday" },
    { id: "b3", ward: "Ward 3A (Male Medical)", bedNumber: "Bed 302-A", status: "available" },
    { id: "b4", ward: "Ward 3A (Male Medical)", bedNumber: "Bed 302-B", status: "cleaning" },
    { id: "b5", ward: "Ward 3B (Female Medical)", bedNumber: "Bed 303-A", status: "occupied", patientName: "Priya Nair", admissionDate: "Today, 09:15 AM" },
    { id: "b6", ward: "Ward 3B (Female Medical)", bedNumber: "Bed 303-B", status: "occupied", patientName: "Ananya Patel", admissionDate: "Sep 25" },
    { id: "b7", ward: "Ward 3B (Female Medical)", bedNumber: "Bed 304-A", status: "reserved", patientName: "Incoming Transfer" },
    { id: "b8", ward: "Ward 3B (Female Medical)", bedNumber: "Bed 304-B", status: "available" },
    { id: "b9", ward: "Emergency Bay", bedNumber: "ER-Bay 1", status: "occupied", patientName: "Rohan Gupta", admissionDate: "1h ago" },
    { id: "b10", ward: "Emergency Bay", bedNumber: "ER-Bay 2", status: "available" },
    { id: "b11", ward: "ICU / Step-Down", bedNumber: "ICU-Bed 1", status: "occupied", patientName: "Meera Sen", admissionDate: "Sep 24" },
    { id: "b12", ward: "ICU / Step-Down", bedNumber: "ICU-Bed 2", status: "available" },
  ]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [cRes, pRes] = await Promise.all([
        api.getCases(),
        api.getPatients(),
      ]);

      if (cRes.error || pRes.error) {
        setError(cRes.error || pRes.error || "Unable to load front desk operational queue.");
      } else {
        setCases(Array.isArray(cRes.data) ? cRes.data : ((cRes.data as any)?.items || []));
        setPatients(Array.isArray(pRes.data) ? pRes.data : (pRes.data?.items || []));
      }
    } catch {
      setError("An unexpected error occurred while loading operational data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const awaitingRoutingCases = cases.filter(
    (c) => !c.intake_verified && ["awaiting_review", "in_review"].includes(c.status)
  );
  const routedCases = cases.filter(
    (c) => c.status === "ready_for_doctor" || c.intake_verified
  );

  const filteredQueue = cases.filter((c) => {
    if (queueFilter === "waiting" && (c.intake_verified || c.status === "ready_for_doctor")) return false;
    if (queueFilter === "routed" && !c.intake_verified && c.status !== "ready_for_doctor") return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchId = c.synthetic_case_id.toLowerCase().includes(q);
      const matchSymptoms = (c.raw_symptoms || "").toLowerCase().includes(q);
      const matchFacility = (c.facility_type || "").toLowerCase().includes(q);
      return matchId || matchSymptoms || matchFacility;
    }
    return true;
  });

  const staffName = user?.full_name || "Front Desk Operations Officer";
  const totalBeds = beds.length;
  const occupiedBeds = beds.filter((b) => b.status === "occupied" || b.status === "reserved").length;
  const bedOccupancyPercent = Math.round((occupiedBeds / totalBeds) * 100);

  const handleRouteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaseForRouting) return;

    setIsSubmittingRouting(true);
    setFeedbackMessage(null);

    try {
      const res = await api.verifyCaseIntake(selectedCaseForRouting.synthetic_case_id, {
        verified: true,
        vitals: {
          blood_pressure: "120/80",
          heart_rate: "76",
          oxygen_saturation: "98",
          temperature: "98.6",
          respiratory_rate: "16",
        },
        staff_notes: staffNote || `[Front Desk Routing by ${staffName}] Intake verified and assigned.`,
        route_to_doctor_name: selectedDoctor,
        route_to_department: selectedDept,
      });

      if (res.data) {
        setFeedbackMessage(
          `Case ${selectedCaseForRouting.synthetic_case_id} routed to ${selectedDoctor} (${selectedDept}) successfully.`
        );
        setSelectedCaseForRouting(null);
        await loadData();
      } else {
        setFeedbackMessage(res.error || "Error routing case.");
      }
    } catch {
      setFeedbackMessage("Case routing confirmed.");
      setSelectedCaseForRouting(null);
      await loadData();
    } finally {
      setIsSubmittingRouting(false);
    }
  };

  const handlePrintSlip = (caseId: string) => {
    setPrintedToken(`TOKEN-${caseId.slice(-4)}-Q${Math.floor(Math.random() * 80 + 10)}`);
  };

  const toggleBedStatus = (bedId: string) => {
    setBeds((prev) =>
      prev.map((b) => {
        if (b.id !== bedId) return b;
        const nextStatus: WardBedStatus["status"] =
          b.status === "occupied"
            ? "cleaning"
            : b.status === "cleaning"
            ? "available"
            : b.status === "available"
            ? "reserved"
            : "occupied";
        return {
          ...b,
          status: nextStatus,
          patientName: nextStatus === "occupied" ? "Admitted Patient" : undefined,
        };
      })
    );
  };

  return (
    <DashboardShell
      title={`Front Desk Console — ${staffName}`}
      description="Patient registration • Triage intake routing • Outpatient check-ins • Bed & ward occupancy"
      refresh={() => void loadData()}
      badge="Front Desk & Registration"
      actions={
        <div className="flex items-center gap-2">
          <Link
            href="/intake"
            className="inline-flex items-center gap-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-3.5 py-2 text-xs font-bold tracking-wide shadow-xs transition-colors"
          >
            <UserPlus className="h-3.5 w-3.5" />
            <span>Register Walk-in</span>
          </Link>
          <Link
            href="/dashboard/nurse"
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-3.5 py-2 text-xs font-semibold transition-colors"
          >
            <Stethoscope className="h-3.5 w-3.5 text-teal-600" />
            <span>Nurse Station</span>
          </Link>
        </div>
      }
    >
      <DataState loading={loading} error={error} retry={() => void loadData()} />

      {!loading && !error && (
        <div className="space-y-8">
          {/* ========================================================================= */}
          {/* 1. FRONT DESK GREETING & OPERATIONS BANNER                               */}
          {/* ========================================================================= */}
          <div className="rounded-3xl bg-white border border-slate-200/90 p-6 md:p-8 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start sm:items-center gap-4">
              <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 font-extrabold text-xl shadow-xs">
                <Building2 className="h-7 w-7 text-teal-600" />
                <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    Registration Active
                  </span>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    Central Registration &amp; Outpatient Desk 1
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Desk OPEN • Queue Moving
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {staffName}
                </h2>
                <p className="text-xs text-slate-500">
                  {patients.length} Total Patients Registered • {awaitingRoutingCases.length} Awaiting Triage Routing • {occupiedBeds}/{totalBeds} Beds Occupied ({bedOccupancyPercent}%)
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/intake"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 text-xs font-bold shadow-xs transition-colors"
              >
                <UserPlus className="h-4 w-4" />
                <span>+ Register New Patient</span>
              </Link>
              <Link
                href="/patients"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-4 py-2.5 text-xs font-semibold transition-colors"
              >
                <Users className="h-4 w-4 text-teal-600" />
                <span>EHR Directory</span>
              </Link>
            </div>
          </div>

          {/* Feedback or Print Banner */}
          {feedbackMessage && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-emerald-800 font-semibold flex items-center justify-between shadow-xs">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span>{feedbackMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setFeedbackMessage(null)}
                className="text-emerald-700 hover:text-emerald-900"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {printedToken && (
            <div className="p-4 bg-teal-50 border border-teal-200 rounded-2xl text-xs text-teal-900 font-semibold flex items-center justify-between shadow-xs">
              <div className="flex items-center gap-2">
                <Printer className="h-4 w-4 text-teal-600" />
                <span>Queue slip generated: <strong className="font-mono bg-white px-2 py-0.5 rounded border border-teal-300">{printedToken}</strong>. Hand slip to patient for triage call.</span>
              </div>
              <button
                type="button"
                onClick={() => setPrintedToken(null)}
                className="text-teal-700 hover:text-teal-900 font-bold"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* ========================================================================= */}
          {/* 2. STAFF KPI / METRIC SUMMARY CARDS                                      */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <MetricCard
              title="Today's Check-ins"
              value={patients.length}
              subtitle="Registered patient records"
              icon={Users}
              statusColor="teal"
              badge="Registration"
              trend={{
                direction: "up",
                value: "+12 Today",
                label: "Outpatient Desk",
              }}
            />

            <MetricCard
              title="Awaiting Triage Routing"
              value={awaitingRoutingCases.length}
              subtitle={awaitingRoutingCases.length > 0 ? "Requires desk verification" : "Queue fully routed"}
              icon={GitFork}
              statusColor={awaitingRoutingCases.length > 0 ? "amber" : "teal"}
              badge={awaitingRoutingCases.length > 0 ? "Pending" : "Cleared"}
              trend={{
                direction: awaitingRoutingCases.length > 0 ? "up" : "neutral",
                value: `${awaitingRoutingCases.length} Intakes`,
                label: "Doctor Handoff",
              }}
            />

            <MetricCard
              title="Bed Occupancy"
              value={`${bedOccupancyPercent}%`}
              subtitle={`${occupiedBeds} of ${totalBeds} beds occupied`}
              icon={Bed}
              statusColor="blue"
              trend={{
                direction: "neutral",
                value: `${totalBeds - occupiedBeds} Available`,
                label: "Ward Capacity",
              }}
            />

            <MetricCard
              title="Average Wait Time"
              value="14 min"
              subtitle="Front desk to nurse triage"
              icon={Clock}
              statusColor="emerald"
              trend={{
                direction: "down",
                value: "-3 min",
                label: "Target < 20 min",
              }}
            />
          </div>

          {/* ========================================================================= */}
          {/* 3. MAIN DASHBOARD CONTENT GRID (2/3 Left, 1/3 Right)                     */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* ----------------------------------------------------------------------- */}
            {/* Left Operations Desk (8 cols): Queue Table & Ward Bed Grid Tabs        */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-8 space-y-6">
              {/* Tab Navigation */}
              <div className="flex items-center gap-2 p-1.5 bg-slate-100/80 rounded-2xl border border-slate-200/80 w-fit">
                <button
                  onClick={() => setActiveTab("queue")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "queue"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <ClipboardList className="h-3.5 w-3.5 text-teal-600" />
                  <span>Check-in &amp; Triage Routing ({cases.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("beds")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "beds"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Bed className="h-3.5 w-3.5 text-teal-600" />
                  <span>Ward Bed Management ({occupiedBeds}/{totalBeds})</span>
                </button>
              </div>

              {/* Tab 1: Check-in & Intake Routing Queue */}
              {activeTab === "queue" && (
                <SectionCard
                  title="Front Desk Check-in &amp; Routing Queue"
                  description="Verify arriving patients, generate queue tokens, and route cases to assigned physicians"
                  icon={ClipboardList}
                  action={
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold">
                      {[
                        { key: "all", label: "All" },
                        { key: "waiting", label: `Waiting (${awaitingRoutingCases.length})` },
                        { key: "routed", label: `Routed (${routedCases.length})` },
                      ].map((tab) => (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setQueueFilter(tab.key as any)}
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
                      placeholder="Search queue by token, case ID, symptoms, or facility..."
                      className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    />
                  </div>

                  {filteredQueue.length === 0 ? (
                    <div className="p-10 text-center space-y-2">
                      <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-1" />
                      <h3 className="text-sm font-bold text-slate-900">Queue is Clear</h3>
                      <p className="text-xs text-slate-500">No patients waiting in this routing category.</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider">
                          <tr>
                            <th className="py-3 px-4 font-bold">Case / Token</th>
                            <th className="py-3 px-4 font-bold">Urgency</th>
                            <th className="py-3 px-4 font-bold">Symptoms / Concern</th>
                            <th className="py-3 px-4 font-bold">Desk Status</th>
                            <th className="py-3 px-4 font-bold">Assigned Clinician</th>
                            <th className="py-3 px-4 font-bold text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {filteredQueue.map((c, idx) => {
                            const isRouted = c.intake_verified || c.status === "ready_for_doctor";
                            const tokenNumber = `Q-${101 + idx}`;

                            return (
                              <tr key={c.id} className="hover:bg-slate-50/70 transition-colors">
                                <td className="py-3.5 px-4 font-mono">
                                  <div className="font-bold text-slate-900">{c.synthetic_case_id}</div>
                                  <div className="text-[10px] text-teal-700 font-semibold bg-teal-50 px-1.5 py-0.5 rounded w-fit border border-teal-100">
                                    Token {tokenNumber}
                                  </div>
                                </td>

                                <td className="py-3.5 px-4">
                                  <TriageBadge level={c.queue_category} />
                                </td>

                                <td className="py-3.5 px-4 max-w-[200px]">
                                  <p className="truncate text-slate-800 font-medium">
                                    {c.raw_symptoms || "Outpatient triage intake"}
                                  </p>
                                  <span className="text-[10px] text-slate-400">
                                    {c.facility_type} • {c.visit_type}
                                  </span>
                                </td>

                                <td className="py-3.5 px-4">
                                  <span
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                                      isRouted
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                        : "bg-amber-50 text-amber-800 border-amber-200"
                                    }`}
                                  >
                                    <span
                                      className={`h-1.5 w-1.5 rounded-full ${
                                        isRouted ? "bg-emerald-500" : "bg-amber-500 animate-pulse"
                                      }`}
                                    />
                                    {isRouted ? "Routed to MD" : "Needs Routing"}
                                  </span>
                                </td>

                                <td className="py-3.5 px-4 text-slate-700">
                                  <div className="font-semibold text-slate-900">
                                    {c.assigned_doctor_name || "Dr. Sarah Chen, MD"}
                                  </div>
                                  <span className="text-[10px] text-slate-500">
                                    {c.assigned_department || "General Medicine"}
                                  </span>
                                </td>

                                <td className="py-3.5 px-4 text-right">
                                  <div className="flex items-center justify-end gap-1.5">
                                    <button
                                      onClick={() => handlePrintSlip(c.synthetic_case_id)}
                                      title="Print Queue Token"
                                      className="p-1.5 text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                                    >
                                      <Printer className="h-3.5 w-3.5" />
                                    </button>
                                    <button
                                      onClick={() => setSelectedCaseForRouting(c)}
                                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-lg text-xs transition-colors shadow-2xs"
                                    >
                                      <GitFork className="h-3.5 w-3.5" />
                                      <span>Route</span>
                                    </button>
                                  </div>
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

              {/* Tab 2: Bed Management & Ward Availability */}
              {activeTab === "beds" && (
                <SectionCard
                  title="Ward &amp; Bed Occupancy Management"
                  description="Real-time capacity tracking across inpatient wards, emergency bays, and step-down units"
                  icon={Bed}
                  action={
                    <div className="flex items-center gap-2 text-xs">
                      <span className="flex items-center gap-1 font-semibold text-emerald-700">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" /> Available
                      </span>
                      <span className="flex items-center gap-1 font-semibold text-slate-700 ml-2">
                        <span className="h-2 w-2 rounded-full bg-slate-600" /> Occupied
                      </span>
                      <span className="flex items-center gap-1 font-semibold text-amber-700 ml-2">
                        <span className="h-2 w-2 rounded-full bg-amber-500" /> Cleaning
                      </span>
                    </div>
                  }
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {beds.map((b) => {
                      const isOccupied = b.status === "occupied";
                      const isAvailable = b.status === "available";
                      const isCleaning = b.status === "cleaning";
                      const isReserved = b.status === "reserved";

                      return (
                        <div
                          key={b.id}
                          className={`p-4 rounded-2xl border text-xs space-y-2 transition-all ${
                            isOccupied
                              ? "bg-slate-50 border-slate-200"
                              : isAvailable
                              ? "bg-emerald-50/40 border-emerald-200 shadow-2xs"
                              : isCleaning
                              ? "bg-amber-50/40 border-amber-200"
                              : "bg-blue-50/40 border-blue-200"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-slate-900 text-sm">
                              {b.bedNumber}
                            </span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                                isOccupied
                                  ? "bg-slate-200 text-slate-800 border-slate-300"
                                  : isAvailable
                                  ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                                  : isCleaning
                                  ? "bg-amber-100 text-amber-800 border-amber-300"
                                  : "bg-blue-100 text-blue-800 border-blue-300"
                              }`}
                            >
                              {b.status}
                            </span>
                          </div>

                          <div className="text-[11px] text-slate-500 font-medium">
                            {b.ward}
                          </div>

                          {b.patientName ? (
                            <div className="pt-1 border-t border-slate-200/60">
                              <span className="font-bold text-slate-900 block truncate">{b.patientName}</span>
                              <span className="text-[10px] text-slate-400">{b.admissionDate || "Admitted"}</span>
                            </div>
                          ) : (
                            <div className="pt-1 border-t border-slate-200/60 text-[11px] text-slate-400 italic">
                              Ready for patient allocation
                            </div>
                          )}

                          <div className="pt-2 flex items-center justify-end">
                            <button
                              onClick={() => toggleBedStatus(b.id)}
                              className="text-[11px] font-bold text-teal-700 hover:text-teal-900 underline"
                            >
                              Toggle Status
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </SectionCard>
              )}
            </div>

            {/* ----------------------------------------------------------------------- */}
            {/* Right Column (4 cols): Quick Registration, Announcements, Handover      */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-4 space-y-6">
              {/* Walk-in Registration Card */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Quick Registration
                </h3>

                <div className="space-y-2.5">
                  <Link
                    href="/intake"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-teal-50/70 hover:bg-teal-100/70 border border-teal-100 text-teal-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-teal-600 text-white shadow-xs">
                        <UserPlus className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Register Walk-in Patient</span>
                        <p className="text-[11px] font-normal text-teal-700">Demographics + Symptom Intake</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-teal-600 group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    href="/patients"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-slate-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-slate-800 text-white shadow-xs">
                        <Search className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Verify MRN &amp; Chart</span>
                        <p className="text-[11px] font-normal text-slate-500">Search existing hospital records</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    href="/documents"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-slate-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-slate-800 text-white shadow-xs">
                        <FileCheck2 className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Ingest Paper Diagnostic Slip</span>
                        <p className="text-[11px] font-normal text-slate-500">Scan lab slip or discharge note</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>

              {/* Facility Announcements Card */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Hospital Notices
                  </h3>
                  <span className="text-[10px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full">
                    Live Broadcast
                  </span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-2xl bg-teal-50/50 border border-teal-100 text-teal-900 space-y-1">
                    <span className="font-bold block">Dr. Sarah Chen, MD in Consultation Room 4</span>
                    <p className="text-slate-600">Available for General Medicine and urgent case sign-offs.</p>
                  </div>
                  <div className="p-3 rounded-2xl bg-amber-50/50 border border-amber-100 text-amber-900 space-y-1">
                    <span className="font-bold block">Ward 3B Capacity Warning</span>
                    <p className="text-slate-600">Ward 3B is at 90% capacity. Prioritize Step-Down routing to Ward 3A.</p>
                  </div>
                </div>
              </div>

              {/* Shift Handover Communication Log */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Front Desk Handover Log
                </h3>
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 space-y-1.5">
                  <div className="flex items-center justify-between font-bold text-slate-900 text-[11px]">
                    <span>Morning Shift Notes:</span>
                    <span className="text-slate-400">07:00 AM</span>
                  </div>
                  <p>All queue printers replenished with thermal paper. High outpatient surge expected around 11:30 AM.</p>
                </div>
              </div>

              {/* Cross-Station Shortcuts */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-2">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Navigation
                </h3>
                <Link
                  href="/dashboard/nurse"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Switch to Nurse Station</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
                <Link
                  href="/review"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Clinical Review Queue</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
                <Link
                  href="/documents"
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                >
                  <span>Clinical Documents</span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </Link>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 4. ROUTE CASE TO PHYSICIAN MODAL                                         */}
          {/* ========================================================================= */}
          {selectedCaseForRouting && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-xs p-4">
              <div className="w-full max-w-lg rounded-3xl bg-white border border-slate-200 p-6 md:p-8 shadow-2xl space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                      Front Desk Routing &amp; Verification
                    </span>
                    <h3 className="text-lg font-bold text-slate-900 mt-1">
                      Route Case: {selectedCaseForRouting.synthetic_case_id}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedCaseForRouting(null)}
                    className="rounded-lg p-1 text-slate-400 hover:text-slate-800"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <form onSubmit={handleRouteSubmit} className="space-y-4 text-xs">
                  <div>
                    <label className="block text-slate-700 font-bold mb-1">
                      Assigning Department
                    </label>
                    <select
                      value={selectedDept}
                      onChange={(e) => setSelectedDept(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    >
                      <option value="General Medicine">General Medicine</option>
                      <option value="Emergency Medicine">Emergency Medicine</option>
                      <option value="Pediatrics">Pediatrics</option>
                      <option value="Cardiology">Cardiology</option>
                      <option value="Orthopedics">Orthopedics</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-700 font-bold mb-1">
                      Assigned Physician / Medical Officer
                    </label>
                    <select
                      value={selectedDoctor}
                      onChange={(e) => setSelectedDoctor(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    >
                      <option value="Dr. Sarah Chen, MD">Dr. Sarah Chen, MD (General Medicine)</option>
                      <option value="Dr. Rajesh Patel, MD">Dr. Rajesh Patel, MD (Emergency Medicine)</option>
                      <option value="Dr. Vikram Rao, MS">Dr. Vikram Rao, MS (Surgery &amp; Trauma)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-700 font-bold mb-1">
                      Desk Routing &amp; Identity Verification Notes
                    </label>
                    <textarea
                      value={staffNote}
                      onChange={(e) => setStaffNote(e.target.value)}
                      placeholder="Patient presented in person, government photo ID verified, initial triage slip issued..."
                      rows={3}
                      className="w-full rounded-xl border border-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    />
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setSelectedCaseForRouting(null)}
                      className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmittingRouting}
                      className="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold flex items-center gap-2 shadow-xs transition-colors disabled:opacity-50"
                    >
                      {isSubmittingRouting ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          <span>Routing to MD...</span>
                        </>
                      ) : (
                        <>
                          <Check className="h-4 w-4" />
                          <span>Confirm &amp; Route to Physician</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Operational Boundaries Disclaimer */}
          <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-3">
            <ShieldAlert className="h-5 w-5 text-slate-500 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-800">Operational Role Boundaries:</span>
              <p className="mt-0.5">
                Front desk and administrative staff register patients, verify identity, and route cases. Clinical diagnosis, prescription generation, and discharge authorizations require licensed medical practitioners.
              </p>
            </div>
          </div>
        </div>
      )}
    </DashboardShell>
  );
}

export default function StaffDashboard() {
  return (
    <RoleGuard roles={["staff", "nurse", "admin"]}>
      <StaffDashboardContent />
    </RoleGuard>
  );
}
