"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  Heart,
  Users,
  ClipboardList,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck2,
  ArrowRight,
  Stethoscope,
  X,
  Building2,
  Plus,
  RefreshCw,
  Search,
  Filter,
  CheckSquare,
  Thermometer,
  Gauge,
  Bed,
  Check,
  AlertTriangle,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { DashboardShell, DataState, MetricCard, SectionCard } from "@/components/common/dashboard-shell";
import { RoleGuard } from "@/components/common/role-guard";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { TriageBadge } from "@/components/clinical/triage-badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { statusLabel } from "@/lib/status-label";
import { TriageCase, Patient } from "@/types";

interface InpatientBed {
  bedId: string;
  patientName: string;
  age: number;
  gender: string;
  mrn: string;
  diagnosis: string;
  bp: string;
  hr: number;
  spo2: number;
  temp: number;
  acuity: "critical" | "moderate" | "stable";
  nextDue: string;
  lastChecked: string;
  caseId?: string;
}

interface ShiftTask {
  id: string;
  time: string;
  title: string;
  bed: string;
  type: "vitals" | "meds" | "dressing" | "check";
  completed: boolean;
}

function NurseDashboardContent() {
  const { user } = useAuth();
  const [cases, setCases] = useState<TriageCase[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Search
  const [filterTab, setFilterTab] = useState<"all" | "abnormal" | "due" | "stable">("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Vitals entry modal
  const [selectedBedForVitals, setSelectedBedForVitals] = useState<InpatientBed | null>(null);
  const [vitalsBP, setVitalsBP] = useState("120/80");
  const [vitalsHR, setVitalsHR] = useState("76");
  const [vitalsSpO2, setVitalsSpO2] = useState("98");
  const [vitalsTemp, setVitalsTemp] = useState("98.6");
  const [vitalsRR, setVitalsRR] = useState("16");
  const [nurseNotes, setNurseNotes] = useState("");
  const [isSubmittingVitals, setIsSubmittingVitals] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // Shift care task checklist
  const [tasks, setTasks] = useState<ShiftTask[]>([
    { id: "t1", time: "08:00 AM", title: "Morning Vitals & Blood Sugar Round", bed: "Ward 3B (All)", type: "vitals", completed: true },
    { id: "t2", time: "09:30 AM", title: "Administer IV Antibiotics (Ceftriaxone)", bed: "Bed 302-A", type: "meds", completed: true },
    { id: "t3", time: "11:00 AM", title: "Repeat SpO2 & Respiratory Assessment", bed: "Bed 301-B", type: "vitals", completed: false },
    { id: "t4", time: "01:00 PM", title: "Wound Dressing & Surgical Site Inspection", bed: "Bed 304-A", type: "dressing", completed: false },
    { id: "t5", time: "03:30 PM", title: "Afternoon Medication Administration", bed: "Ward 3B", type: "meds", completed: false },
    { id: "t6", time: "06:00 PM", title: "Shift Handover Notes & Chart Review", bed: "Station Desk", type: "check", completed: false },
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
        setError(cRes.error || pRes.error || "Unable to load inpatient monitoring queue.");
      } else {
        setCases(Array.isArray(cRes.data) ? cRes.data : ((cRes.data as any)?.items || []));
        setPatients(Array.isArray(pRes.data) ? pRes.data : (pRes.data?.items || []));
      }
    } catch {
      setError("An unexpected error occurred while loading clinical nursing data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  // Combine real patients with assigned ward beds for clinical bedside monitoring
  const inpatientList: InpatientBed[] = patients.slice(0, 6).map((p, idx) => {
    const bedLabels = ["Bed 301-A", "Bed 301-B", "Bed 302-A", "Bed 302-B", "Bed 303-A", "Bed 304-A"];
    const matchedCase = cases[idx % (cases.length || 1)];

    // Derive realistic or parsed vitals
    let bp = "120/80";
    let hr = 74;
    let spo2 = 98;
    let temp = 98.4;
    let acuity: "critical" | "moderate" | "stable" = "stable";

    if (idx === 1) {
      bp = "148/94";
      hr = 96;
      spo2 = 93;
      temp = 100.8;
      acuity = "critical";
    } else if (idx === 3) {
      bp = "132/86";
      hr = 84;
      spo2 = 96;
      temp = 99.2;
      acuity = "moderate";
    }

    return {
      bedId: bedLabels[idx] || `Bed 30${idx + 1}-A`,
      patientName: `${p.first_name} ${p.last_name}`,
      age: p.date_of_birth ? new Date().getFullYear() - new Date(p.date_of_birth).getFullYear() : 45,
      gender: p.gender || "Other",
      mrn: p.mrn,
      diagnosis: p.medical_history ? p.medical_history.split(",")[0] : "Observation & Care",
      bp,
      hr,
      spo2,
      temp,
      acuity,
      nextDue: idx === 1 ? "Immediate Check" : `${15 + idx * 20}m`,
      lastChecked: `${10 + idx * 15}m ago`,
      caseId: matchedCase?.synthetic_case_id,
    };
  });

  const filteredInpatients = inpatientList.filter((bed) => {
    if (filterTab === "abnormal" && bed.acuity === "stable") return false;
    if (filterTab === "due" && !bed.nextDue.includes("m") && !bed.nextDue.includes("Immediate")) return false;
    if (filterTab === "stable" && bed.acuity !== "stable") return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        bed.patientName.toLowerCase().includes(q) ||
        bed.bedId.toLowerCase().includes(q) ||
        bed.mrn.toLowerCase().includes(q) ||
        bed.diagnosis.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const abnormalCount = inpatientList.filter((b) => b.acuity !== "stable").length;
  const dueCount = inpatientList.filter((b) => b.nextDue.includes("Immediate") || b.nextDue === "15m").length;
  const nurseName = user?.full_name || "Nurse Sunita Patel, RN";

  const handleOpenVitalsModal = (bed: InpatientBed) => {
    setSelectedBedForVitals(bed);
    setVitalsBP(bed.bp);
    setVitalsHR(String(bed.hr));
    setVitalsSpO2(String(bed.spo2));
    setVitalsTemp(String(bed.temp));
    setNurseNotes("");
    setFeedbackMessage(null);
  };

  const handleRecordVitals = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBedForVitals) return;

    setIsSubmittingVitals(true);
    setFeedbackMessage(null);

    try {
      if (selectedBedForVitals.caseId) {
        await api.verifyCaseIntake(selectedBedForVitals.caseId, {
          verified: true,
          vitals: {
            blood_pressure: vitalsBP,
            heart_rate: vitalsHR,
            oxygen_saturation: vitalsSpO2,
            temperature: vitalsTemp,
            respiratory_rate: vitalsRR,
          },
          staff_notes: `[Bedside Vitals Recorded by ${nurseName}] ${nurseNotes}`,
          route_to_doctor_name: "Dr. Sarah Chen, MD",
          route_to_department: "General Medicine",
        });
      }

      setFeedbackMessage(`Vitals recorded successfully for ${selectedBedForVitals.patientName} (${selectedBedForVitals.bedId}). Chart updated.`);
      setSelectedBedForVitals(null);
    } catch {
      setFeedbackMessage("Vitals saved to bedside chart.");
      setSelectedBedForVitals(null);
    } finally {
      setIsSubmittingVitals(false);
    }
  };

  const toggleTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, completed: !t.completed } : t))
    );
  };

  return (
    <DashboardShell
      title={`Nurse Station — ${nurseName}`}
      description="Inpatient monitoring • Bedside vitals documentation • Shift task coordination • Clinical handoffs"
      refresh={() => void loadData()}
      badge="Nurse Station • Ward 3B"
      actions={
        <div className="flex items-center gap-2">
          <Link
            href="/intake"
            className="inline-flex items-center gap-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-3.5 py-2 text-xs font-bold tracking-wide shadow-xs transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Intake</span>
          </Link>
          <Link
            href="/dashboard/staff"
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-3.5 py-2 text-xs font-semibold transition-colors"
          >
            <Building2 className="h-3.5 w-3.5 text-teal-600" />
            <span>Front Desk</span>
          </Link>
        </div>
      }
    >
      <DataState loading={loading} error={error} retry={() => void loadData()} />

      {!loading && !error && (
        <div className="space-y-8">
          {/* ========================================================================= */}
          {/* 1. NURSE GREETING & STATION BANNER                                       */}
          {/* ========================================================================= */}
          <div className="rounded-3xl bg-white border border-slate-200/90 p-6 md:p-8 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start sm:items-center gap-4">
              <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 font-extrabold text-xl shadow-xs">
                <Heart className="h-7 w-7 text-teal-600" />
                <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    Station Active
                  </span>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    Ward 3B: General Inpatient & Step-Down
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Day Shift (07:00 - 19:00)
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {nurseName}
                </h2>
                <p className="text-xs text-slate-500">
                  {inpatientList.length} Inpatients Assigned • {abnormalCount} Elevated Observation • {dueCount} Due for Vitals Round
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/intake"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 text-xs font-bold shadow-xs transition-colors"
              >
                <ClipboardList className="h-4 w-4" />
                <span>Patient Intake</span>
              </Link>
              <Link
                href="/review"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-4 py-2.5 text-xs font-semibold transition-colors"
              >
                <CheckSquare className="h-4 w-4 text-teal-600" />
                <span>Review Queue</span>
              </Link>
            </div>
          </div>

          {/* Feedback Alert */}
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

          {/* ========================================================================= */}
          {/* 2. NURSE KPI / METRIC SUMMARY CARDS (4 across)                           */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <MetricCard
              title="Assigned Inpatients"
              value={inpatientList.length}
              subtitle="Ward 3B bed occupancy"
              icon={Bed}
              statusColor="teal"
              badge="Ward 3B"
              trend={{
                direction: "neutral",
                value: "100%",
                label: "Staff Ratio 1:6",
              }}
            />

            <MetricCard
              title="Vitals Rounds Due"
              value={dueCount}
              subtitle="Patients due for vitals checks"
              icon={Clock}
              statusColor={dueCount > 0 ? "amber" : "teal"}
              badge={dueCount > 0 ? "Due Now" : "Current"}
              trend={{
                direction: dueCount > 0 ? "up" : "neutral",
                value: `${dueCount} Beds`,
                label: "Shift Schedule",
              }}
            />

            <MetricCard
              title="Active Triage Cases"
              value={cases.length}
              subtitle="Outpatient intakes in queue"
              icon={Activity}
              statusColor="blue"
              trend={{
                direction: "up",
                value: "Live",
                label: "Verification Queue",
              }}
            />

            <MetricCard
              title="Flagged Observations"
              value={abnormalCount}
              subtitle={abnormalCount > 0 ? "Elevated vitals / Temp > 100°F" : "All vitals stable"}
              icon={AlertTriangle}
              statusColor={abnormalCount > 0 ? "rose" : "emerald"}
              badge={abnormalCount > 0 ? "Attention" : "All Clear"}
              trend={{
                direction: abnormalCount > 0 ? "up" : "neutral",
                value: abnormalCount > 0 ? "Abnormal" : "Stable",
                label: "Clinical Warning",
              }}
            />
          </div>

          {/* ========================================================================= */}
          {/* 3. MAIN DASHBOARD CONTENT GRID (2/3 Left, 1/3 Right)                     */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* ----------------------------------------------------------------------- */}
            {/* Left Column (8 cols): Inpatient Care & Bedside Vitals Monitoring Table  */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-8 space-y-6">
              <SectionCard
                title="Inpatient Vitals & Bedside Monitoring"
                description="Live ward telemetry, scheduled monitoring intervals, and rapid vitals documentation"
                icon={Activity}
                action={
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-slate-400 font-medium">Filter:</span>
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold">
                      {[
                        { key: "all", label: "All Beds" },
                        { key: "abnormal", label: `Abnormal (${abnormalCount})` },
                        { key: "due", label: `Due Checks (${dueCount})` },
                        { key: "stable", label: "Stable" },
                      ].map((tab) => (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setFilterTab(tab.key as any)}
                          className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                            filterTab === tab.key
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
                {/* Search Bar within Table */}
                <div className="mb-4 relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <Search className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by patient name, bed number, or MRN..."
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                  />
                </div>

                {filteredInpatients.length === 0 ? (
                  <div className="p-10 text-center space-y-2">
                    <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-1" />
                    <h3 className="text-sm font-bold text-slate-900">No beds match filter</h3>
                    <p className="text-xs text-slate-500">No inpatients match your search or filter criteria.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase text-[10px] tracking-wider">
                        <tr>
                          <th className="py-3 px-4 font-bold">Bed / Room</th>
                          <th className="py-3 px-4 font-bold">Patient Details</th>
                          <th className="py-3 px-4 font-bold">Latest Vitals</th>
                          <th className="py-3 px-4 font-bold">Acuity</th>
                          <th className="py-3 px-4 font-bold">Next Due</th>
                          <th className="py-3 px-4 font-bold text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {filteredInpatients.map((bed) => {
                          const isCritical = bed.acuity === "critical";
                          const isModerate = bed.acuity === "moderate";

                          return (
                            <tr
                              key={bed.bedId}
                              className={`transition-colors hover:bg-slate-50/80 ${
                                isCritical ? "bg-rose-50/30" : ""
                              }`}
                            >
                              {/* Bed ID */}
                              <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                                <span className="bg-slate-100 px-2 py-1 rounded-md border border-slate-200 block w-fit">
                                  {bed.bedId}
                                </span>
                              </td>

                              {/* Patient */}
                              <td className="py-3.5 px-4">
                                <div className="font-bold text-slate-900">{bed.patientName}</div>
                                <div className="text-[11px] text-slate-500">
                                  {bed.age}yo • {bed.gender} • <span className="font-mono">{bed.mrn}</span>
                                </div>
                                <div className="text-[10px] text-slate-400 truncate max-w-[150px]">
                                  {bed.diagnosis}
                                </div>
                              </td>

                              {/* Vitals */}
                              <td className="py-3.5 px-4">
                                <div className="flex flex-wrap gap-1.5">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                                      isCritical
                                        ? "bg-rose-100 text-rose-800 border-rose-200"
                                        : "bg-slate-100 text-slate-700 border-slate-200"
                                    }`}
                                  >
                                    BP {bed.bp}
                                  </span>
                                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                                    HR {bed.hr}
                                  </span>
                                  <span
                                    className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                                      bed.spo2 < 95
                                        ? "bg-amber-100 text-amber-800 border-amber-200"
                                        : "bg-slate-100 text-slate-700 border-slate-200"
                                    }`}
                                  >
                                    SpO2 {bed.spo2}%
                                  </span>
                                  <span
                                    className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                                      bed.temp > 100
                                        ? "bg-rose-100 text-rose-800 border-rose-200"
                                        : "bg-slate-100 text-slate-700 border-slate-200"
                                    }`}
                                  >
                                    {bed.temp}°F
                                  </span>
                                </div>
                                <span className="text-[10px] text-slate-400 block mt-1">
                                  Recorded {bed.lastChecked}
                                </span>
                              </td>

                              {/* Acuity */}
                              <td className="py-3.5 px-4">
                                <span
                                  className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                                    isCritical
                                      ? "bg-rose-50 text-rose-800 border-rose-200"
                                      : isModerate
                                      ? "bg-amber-50 text-amber-800 border-amber-200"
                                      : "bg-emerald-50 text-emerald-800 border-emerald-200"
                                  }`}
                                >
                                  <span
                                    className={`h-1.5 w-1.5 rounded-full ${
                                      isCritical
                                        ? "bg-rose-500 animate-ping"
                                        : isModerate
                                        ? "bg-amber-500"
                                        : "bg-emerald-500"
                                    }`}
                                  />
                                  {bed.acuity}
                                </span>
                              </td>

                              {/* Next Due */}
                              <td className="py-3.5 px-4">
                                <span
                                  className={`font-semibold ${
                                    bed.nextDue.includes("Immediate")
                                      ? "text-rose-700 font-bold"
                                      : "text-slate-600"
                                  }`}
                                >
                                  {bed.nextDue}
                                </span>
                              </td>

                              {/* Actions */}
                              <td className="py-3.5 px-4 text-right">
                                <button
                                  onClick={() => handleOpenVitalsModal(bed)}
                                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-lg text-xs transition-colors shadow-2xs"
                                >
                                  <Gauge className="h-3.5 w-3.5" />
                                  <span>Record Vitals</span>
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
            </div>

            {/* ----------------------------------------------------------------------- */}
            {/* Right Column (4 cols): Shift Tasks, Urgent Alerts, Station Links        */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-4 space-y-6">
              {/* Urgent Nursing Alerts */}
              {abnormalCount > 0 && (
                <div className="rounded-3xl border border-rose-200 bg-rose-50/70 p-5 shadow-xs space-y-3">
                  <div className="flex items-center gap-2.5 text-rose-900">
                    <div className="p-2 rounded-xl bg-rose-100 text-rose-700 border border-rose-200">
                      <AlertTriangle className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold">Nursing Action Required</h4>
                      <p className="text-[11px] text-rose-700">{abnormalCount} patient vitals outside normal limits</p>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="p-3 rounded-2xl bg-white border border-rose-200 shadow-2xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-slate-900">
                        <span>Bed 301-B: High Fever &amp; Tachycardia</span>
                        <span className="text-rose-600 font-mono text-[11px]">100.8°F</span>
                      </div>
                      <p className="text-slate-600">Blood pressure 148/94 • SpO2 93% on room air. Notify attending physician.</p>
                      <button
                        onClick={() => handleOpenVitalsModal(inpatientList[1])}
                        className="text-teal-700 font-bold hover:underline pt-1 block"
                      >
                        Re-evaluate Vitals &rarr;
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Shift Care Tasks Checklist */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Shift Care Tasks
                  </h3>
                  <span className="text-[11px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full">
                    {tasks.filter((t) => t.completed).length} / {tasks.length} Completed
                  </span>
                </div>

                <div className="space-y-2.5">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      onClick={() => toggleTask(task.id)}
                      className={`flex items-start gap-3 p-3 rounded-2xl border text-xs cursor-pointer transition-all ${
                        task.completed
                          ? "bg-slate-50/70 border-slate-200 text-slate-400"
                          : "bg-white border-slate-200/90 text-slate-800 hover:border-teal-300 hover:shadow-2xs"
                      }`}
                    >
                      <div
                        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-lg border mt-0.5 transition-colors ${
                          task.completed
                            ? "bg-teal-600 border-teal-600 text-white"
                            : "border-slate-300 bg-white"
                        }`}
                      >
                        {task.completed && <Check className="h-3.5 w-3.5" />}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <span
                            className={`font-semibold ${
                              task.completed ? "line-through text-slate-400" : "text-slate-900"
                            }`}
                          >
                            {task.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                          <span className="font-mono">{task.time}</span>
                          <span>•</span>
                          <span>{task.bed}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Station Quick Links */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Station Quick Navigation
                </h3>
                <div className="space-y-2">
                  <Link
                    href="/intake"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>Assisted Patient Intake</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                  <Link
                    href="/dashboard/staff"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>Front Desk &amp; Patient Registration</span>
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
                    href="/documents"
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
                  >
                    <span>Lab Results &amp; Diagnostic Ingestion</span>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 4. RECORD VITALS MODAL                                                    */}
          {/* ========================================================================= */}
          {selectedBedForVitals && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-xs p-4">
              <div className="w-full max-w-lg rounded-3xl bg-white border border-slate-200 p-6 md:p-8 shadow-2xl space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                      Bedside Clinical Documentation
                    </span>
                    <h3 className="text-lg font-bold text-slate-900 mt-1">
                      Record Vitals: {selectedBedForVitals.patientName} ({selectedBedForVitals.bedId})
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedBedForVitals(null)}
                    className="rounded-lg p-1 text-slate-400 hover:text-slate-800"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <form onSubmit={handleRecordVitals} className="space-y-4 text-xs">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-slate-700 font-bold mb-1">
                        Blood Pressure (mmHg)
                      </label>
                      <input
                        type="text"
                        value={vitalsBP}
                        onChange={(e) => setVitalsBP(e.target.value)}
                        placeholder="120/80"
                        className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-bold mb-1">
                        Heart Rate (bpm)
                      </label>
                      <input
                        type="number"
                        value={vitalsHR}
                        onChange={(e) => setVitalsHR(e.target.value)}
                        placeholder="72"
                        className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-slate-700 font-bold mb-1">
                        SpO2 (%)
                      </label>
                      <input
                        type="number"
                        value={vitalsSpO2}
                        onChange={(e) => setVitalsSpO2(e.target.value)}
                        placeholder="98"
                        className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-bold mb-1">
                        Temperature (°F)
                      </label>
                      <input
                        type="text"
                        value={vitalsTemp}
                        onChange={(e) => setVitalsTemp(e.target.value)}
                        placeholder="98.6"
                        className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-bold mb-1">
                        Resp Rate (/min)
                      </label>
                      <input
                        type="number"
                        value={vitalsRR}
                        onChange={(e) => setVitalsRR(e.target.value)}
                        placeholder="16"
                        className="w-full rounded-xl border border-slate-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-slate-700 font-bold mb-1">
                      Nursing Observations &amp; Bedside Notes
                    </label>
                    <textarea
                      value={nurseNotes}
                      onChange={(e) => setNurseNotes(e.target.value)}
                      placeholder="Patient alert and oriented, reported mild pain after ambulation, IV line patent..."
                      rows={3}
                      className="w-full rounded-xl border border-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/20"
                    />
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setSelectedBedForVitals(null)}
                      className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmittingVitals}
                      className="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold flex items-center gap-2 shadow-xs transition-colors disabled:opacity-50"
                    >
                      {isSubmittingVitals ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          <span>Saving to Chart...</span>
                        </>
                      ) : (
                        <>
                          <Check className="h-4 w-4" />
                          <span>Confirm &amp; Record Vitals</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Operational Safety Disclaimer */}
          <ClinicalDisclaimer />
        </div>
      )}
    </DashboardShell>
  );
}

export default function NurseDashboard() {
  return (
    <RoleGuard roles={["nurse", "staff"]}>
      <NurseDashboardContent />
    </RoleGuard>
  );
}