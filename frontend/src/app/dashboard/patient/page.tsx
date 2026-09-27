"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  ClipboardList,
  FileText,
  UserRound,
  Activity,
  Heart,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck,
  ShieldCheck,
  Upload,
  Sparkles,
  Mic,
  Stethoscope,
  ChevronRight,
  Thermometer,
  Eye,
  Plus,
} from "lucide-react";
import { DashboardShell, DataState, MetricCard, SectionCard } from "@/components/common/dashboard-shell";
import { RoleGuard } from "@/components/common/role-guard";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { api, documentsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { statusLabel } from "@/lib/status-label";
import { Patient, PatientCase, PatientConsultation, MedicalDocument } from "@/types";

function PatientDashboardContent() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Patient | null>(null);
  const [cases, setCases] = useState<PatientCase[]>([]);
  const [consultations, setConsultations] = useState<PatientConsultation[]>([]);
  const [documents, setDocuments] = useState<MedicalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"cases" | "consultations">("cases");
  const [selectedCase, setSelectedCase] = useState<PatientCase | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [pRes, cRes, vRes, dRes] = await Promise.all([
        api.getMyProfile(),
        api.getMyCases(),
        api.getMyConsultations(),
        documentsApi.listDocuments(),
      ]);

      if (pRes.error || cRes.error || vRes.error) {
        setError(pRes.error || cRes.error || vRes.error || "Could not load your records.");
      } else {
        setProfile(pRes.data ?? null);
        setCases(cRes.data || []);
        setConsultations(vRes.data || []);
        if (dRes.data) {
          const docs = Array.isArray(dRes.data) ? dRes.data : ((dRes.data as any)?.items || []);
          setDocuments(docs);
        }
      }
    } catch {
      setError("An unexpected error occurred while loading your health portal.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const activeCase = cases.length > 0 ? cases[0] : null;
  const awaitingCount = cases.filter((c) =>
    ["awaiting_review", "in_review", "ready_for_doctor"].includes(c.status)
  ).length;

  const patientName = user?.full_name || (profile ? `${profile.first_name} ${profile.last_name}` : "Patient");

  return (
    <DashboardShell
      title={`Good morning, ${patientName}`}
      description="Personal Healthcare Portal • Track your triage evaluations, scheduled consultations, and medical records."
      refresh={() => void loadData()}
      badge="Patient Portal"
      actions={
        <Link
          href="/intake"
          className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-4 py-2.5 text-xs font-bold tracking-wide shadow-xs transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>New Symptom Intake</span>
        </Link>
      }
    >
      <DataState loading={loading} error={error} retry={() => void loadData()} />

      {!loading && !error && (
        <div className="space-y-8">
          {/* ========================================================================= */}
          {/* 1. PATIENT STATUS & PROFILE BANNER                                       */}
          {/* ========================================================================= */}
          <div className="rounded-3xl bg-white border border-slate-200/90 p-6 md:p-8 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start sm:items-center gap-4">
              <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 font-extrabold text-xl shadow-xs">
                {patientName.slice(0, 2).toUpperCase()}
                <span className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    Active Patient
                  </span>
                  {profile?.mrn && (
                    <span className="text-xs font-mono font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      MRN: {profile.mrn}
                    </span>
                  )}
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Care Plan: Routine Monitoring
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {patientName}
                </h2>
                <p className="text-xs text-slate-500">
                  {profile
                    ? `DOB: ${profile.date_of_birth} • Gender: ${profile.gender} • Blood Group: ${profile.blood_group || "O+"}`
                    : `Registered Email: ${user?.email || "patient@clinova.ai"}`}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/intake"
                className="inline-flex items-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 text-xs font-bold shadow-xs transition-colors"
              >
                <ClipboardList className="h-4 w-4" />
                <span>Start Intake</span>
              </Link>
              <Link
                href="/portal/profile"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-4 py-2.5 text-xs font-semibold transition-colors"
              >
                <UserRound className="h-4 w-4 text-slate-500" />
                <span>View Profile</span>
              </Link>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 2. KPI / METRIC SUMMARY CARDS (4 across)                                 */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <MetricCard
              title="Active Intakes"
              value={cases.length}
              subtitle={awaitingCount > 0 ? `${awaitingCount} under clinical evaluation` : "All cases evaluated"}
              icon={ClipboardList}
              statusColor={awaitingCount > 0 ? "amber" : "teal"}
              badge={awaitingCount > 0 ? "In Review" : "Up to Date"}
              trend={{
                direction: awaitingCount > 0 ? "up" : "neutral",
                value: awaitingCount > 0 ? "Active" : "Normal",
                label: "Triage Queue",
              }}
            />

            <MetricCard
              title="Consultations"
              value={consultations.length}
              subtitle="Scheduled & past visits"
              icon={Calendar}
              statusColor="blue"
              trend={{
                direction: "neutral",
                value: consultations.length > 0 ? "Active" : "None",
                label: "Doctor Sessions",
              }}
            />

            <MetricCard
              title="Lab Documents"
              value={documents.length}
              subtitle="Medical records stored"
              icon={FileText}
              statusColor="emerald"
              trend={{
                direction: "up",
                value: "Encrypted",
                label: "Secure EHR",
              }}
            />

            <MetricCard
              title="Vitals Status"
              value="Normal"
              subtitle="BP: 120/80 • HR: 72 bpm"
              icon={Heart}
              statusColor="teal"
              trend={{
                direction: "neutral",
                value: "Stable",
                label: "Baseline",
              }}
            />
          </div>

          {/* ========================================================================= */}
          {/* 3. MAIN DASHBOARD CONTENT GRID (2/3 Left, 1/3 Right)                     */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* ----------------------------------------------------------------------- */}
            {/* Left Column (2/3): Active Cases & Consultations Tabs                    */}
            {/* ----------------------------------------------------------------------- */}
            <div className="lg:col-span-2 space-y-6">
              {/* Tab Navigation */}
              <div className="flex items-center gap-2 p-1.5 bg-slate-100/80 rounded-2xl border border-slate-200/80 w-fit">
                <button
                  onClick={() => setActiveTab("cases")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "cases"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Activity className="h-3.5 w-3.5 text-teal-600" />
                  <span>My Symptom Intakes ({cases.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("consultations")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    activeTab === "consultations"
                      ? "bg-white text-teal-800 shadow-xs border border-slate-200/60"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Calendar className="h-3.5 w-3.5 text-teal-600" />
                  <span>Consultations ({consultations.length})</span>
                </button>
              </div>

              {/* Tab 1: Symptom Intakes List */}
              {activeTab === "cases" && (
                <SectionCard
                  title="Triage & Symptom Intakes"
                  description="Multimodal clinical evaluations generated from your submitted symptoms"
                  icon={Activity}
                  action={
                    <Link
                      href="/intake"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-teal-700 hover:text-teal-800 bg-teal-50 hover:bg-teal-100/70 px-3 py-1.5 rounded-lg border border-teal-200 transition-colors"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      <span>Start Intake</span>
                    </Link>
                  }
                >
                  {cases.length === 0 ? (
                    <div className="p-10 text-center space-y-3">
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-50 text-teal-600 border border-teal-100">
                        <ClipboardList className="h-6 w-6" />
                      </div>
                      <h3 className="text-sm font-bold text-slate-900">No Symptom Intakes Yet</h3>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        If you are experiencing symptoms or need medical evaluation, start a new symptom intake.
                      </p>
                      <div className="pt-2">
                        <Link
                          href="/intake"
                          className="inline-flex items-center gap-2 rounded-xl bg-teal-600 text-white px-4 py-2 text-xs font-bold shadow-xs hover:bg-teal-700"
                        >
                          <Plus className="h-3.5 w-3.5" />
                          <span>Start My First Intake</span>
                        </Link>
                      </div>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {cases.map((c) => {
                        const isApproved = c.status === "approved";
                        const isInReview = ["awaiting_review", "in_review", "ready_for_doctor"].includes(c.status);

                        return (
                          <div
                            key={c.id}
                            className="py-4.5 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-4 group"
                          >
                            <div className="space-y-1.5 min-w-0 flex-1">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                                  {c.synthetic_case_id}
                                </span>
                                <span
                                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                                    isApproved
                                      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                      : isInReview
                                      ? "bg-amber-50 text-amber-800 border-amber-200"
                                      : "bg-slate-100 text-slate-700 border-slate-200"
                                  }`}
                                >
                                  {statusLabel(c.status)}
                                </span>
                                <span className="text-[11px] text-slate-400">
                                  {new Date(c.created_at).toLocaleDateString("en-US", {
                                    month: "short",
                                    day: "numeric",
                                    year: "numeric",
                                  })}
                                </span>
                              </div>

                              <p className="text-xs text-slate-700 line-clamp-2 leading-relaxed">
                                {c.raw_symptoms ? `"${c.raw_symptoms}"` : "Symptom description recorded during intake."}
                              </p>

                              {c.summary && (
                                <div className="mt-2 p-2.5 rounded-xl bg-teal-50/60 border border-teal-100 text-xs text-teal-900">
                                  <span className="font-bold text-[11px] uppercase tracking-wider text-teal-800 block mb-0.5">
                                    Physician Review Note:
                                  </span>
                                  <p className="line-clamp-2">{c.summary}</p>
                                </div>
                              )}
                            </div>

                            <button
                              onClick={() => setSelectedCase(selectedCase?.id === c.id ? null : c)}
                              className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-700 hover:text-teal-900 bg-teal-50 hover:bg-teal-100/70 px-3.5 py-2 rounded-xl transition-colors shrink-0 self-start md:self-center"
                            >
                              <Eye className="h-3.5 w-3.5" />
                              <span>{selectedCase?.id === c.id ? "Hide Details" : "View Details"}</span>
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Case Modal / Expanded Details */}
                  {selectedCase && (
                    <div className="mt-6 p-5 rounded-2xl bg-slate-50 border border-teal-200/90 space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                        <div className="flex items-center gap-2">
                          <Activity className="h-4 w-4 text-teal-600" />
                          <h4 className="text-sm font-bold text-slate-900">
                            Case Details: {selectedCase.synthetic_case_id}
                          </h4>
                        </div>
                        <button
                          onClick={() => setSelectedCase(null)}
                          className="text-xs text-slate-500 hover:text-slate-800 font-semibold"
                        >
                          Close Details
                        </button>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 text-xs">
                        <div className="space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                          <span className="font-bold uppercase tracking-wider text-[10px] text-slate-400">
                            Reported Symptoms
                          </span>
                          <p className="text-slate-800 leading-relaxed font-mono">
                            "{selectedCase.raw_symptoms}"
                          </p>
                        </div>
                        <div className="space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                          <span className="font-bold uppercase tracking-wider text-[10px] text-teal-700">
                            Clinical Summary
                          </span>
                          <p className="text-slate-800 leading-relaxed">
                            {selectedCase.summary || "Pending final clinical evaluation by doctor."}
                          </p>
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1">
                        <span>Facility Type: {selectedCase.facility_type}</span>
                        <span>Visit Type: {selectedCase.visit_type}</span>
                      </div>
                    </div>
                  )}
                </SectionCard>
              )}

              {/* Tab 2: Consultations List */}
              {activeTab === "consultations" && (
                <SectionCard
                  title="Physician Consultations"
                  description="Scheduled appointments and clinical encounter notes"
                  icon={Calendar}
                >
                  {consultations.length === 0 ? (
                    <div className="p-10 text-center space-y-3">
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 border border-blue-100">
                        <Calendar className="h-6 w-6" />
                      </div>
                      <h3 className="text-sm font-bold text-slate-900">No Scheduled Consultations</h3>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        Your upcoming doctor appointments and past medical consultations will appear here.
                      </p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {consultations.map((c) => (
                        <div
                          key={c.id}
                          className="py-4.5 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-4"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-sm text-slate-900">
                                {c.doctor_name || "Assigned Medical Officer"}
                              </span>
                              <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                                {c.status}
                              </span>
                            </div>
                            <p className="text-xs text-slate-600">
                              Concern: <span className="font-medium text-slate-800">{c.chief_complaint}</span>
                            </p>
                            {c.summary && (
                              <p className="text-xs text-slate-500 italic mt-1 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                                "{c.summary}"
                              </p>
                            )}
                          </div>
                          <div className="text-right text-xs font-medium text-slate-500 shrink-0">
                            {new Date(c.scheduled_at).toLocaleDateString("en-US", {
                              month: "short",
                              day: "numeric",
                              year: "numeric",
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </SectionCard>
              )}
            </div>

            {/* ----------------------------------------------------------------------- */}
            {/* Right Column (1/3): Quick Actions, Vitals, AI Voice Card, Documents     */}
            {/* ----------------------------------------------------------------------- */}
            <div className="space-y-6">
              {/* Quick Actions Card */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                  Quick Actions
                </h3>
                <div className="space-y-2.5">
                  <Link
                    href="/intake"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-teal-50/70 hover:bg-teal-100/70 border border-teal-100 text-teal-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-teal-600 text-white shadow-xs">
                        <Plus className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Start Symptom Intake</span>
                        <p className="text-[11px] font-normal text-teal-700">Multimodal AI triage assistant</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-teal-600 group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    href="/documents"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-slate-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-slate-800 text-white shadow-xs">
                        <Upload className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Upload Lab Documents</span>
                        <p className="text-[11px] font-normal text-slate-500">Attach blood tests & prescriptions</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    href="/portal/profile"
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-slate-900 text-xs font-bold transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-slate-800 text-white shadow-xs">
                        <UserRound className="h-4 w-4" />
                      </div>
                      <div>
                        <span>Emergency Contacts & EHR</span>
                        <p className="text-[11px] font-normal text-slate-500">Update medical history & contacts</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>

              {/* Vitals & Health Indicators Card */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Recorded Vitals
                  </h3>
                  <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                    Verified
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Blood Pressure</span>
                    <p className="text-base font-extrabold text-slate-900">120/80</p>
                    <span className="text-[10px] text-emerald-600 font-semibold">Normal mmHg</span>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Heart Rate</span>
                    <p className="text-base font-extrabold text-slate-900">72</p>
                    <span className="text-[10px] text-emerald-600 font-semibold">BPM (Resting)</span>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Oxygen (SpO2)</span>
                    <p className="text-base font-extrabold text-slate-900">98%</p>
                    <span className="text-[10px] text-emerald-600 font-semibold">Normal Room Air</span>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Temperature</span>
                    <p className="text-base font-extrabold text-slate-900">98.6°F</p>
                    <span className="text-[10px] text-emerald-600 font-semibold">Afebrile</span>
                  </div>
                </div>

                {profile?.allergies && (
                  <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 text-xs">
                    <span className="font-bold text-amber-900 block text-[11px] uppercase tracking-wider">
                      Known Allergies:
                    </span>
                    <p className="text-amber-800 mt-0.5">{profile.allergies}</p>
                  </div>
                )}
              </div>

              {/* AI Voice Assistant Promo Card */}
              <div className="rounded-3xl bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6 shadow-md space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/20 text-teal-400 border border-teal-400/30">
                    <Mic className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white">Voice-First AI Assistant</h4>
                    <span className="text-[10px] text-teal-300 font-medium">Real-Time Medical Help</span>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Need assistance? Tap the floating microphone in the bottom corner to describe your symptoms or ask clinical questions naturally in English, Hindi, Tamil, or your native language.
                </p>
                <div className="flex items-center gap-2 pt-1 text-[11px] text-teal-400 font-semibold">
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Multilingual Speech & Auto-Language Detection</span>
                </div>
              </div>

              {/* Medical Documents Quick List */}
              <div className="rounded-3xl bg-white border border-slate-200/90 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    Recent Documents
                  </h3>
                  <Link
                    href="/documents"
                    className="text-xs font-bold text-teal-700 hover:text-teal-900"
                  >
                    View All ({documents.length})
                  </Link>
                </div>

                {documents.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No uploaded documents yet.</p>
                ) : (
                  <div className="space-y-2">
                    {documents.slice(0, 3).map((doc) => (
                      <Link
                        key={doc.id}
                        href="/documents"
                        className="flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-colors text-xs text-slate-700"
                      >
                        <div className="flex items-center gap-2.5 truncate">
                          <FileText className="h-4 w-4 text-teal-600 shrink-0" />
                          <span className="truncate font-medium">{doc.filename}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 shrink-0">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Safety & Non-Diagnostic Disclaimer */}
          <ClinicalDisclaimer />
        </div>
      )}
    </DashboardShell>
  );
}

export default function PatientDashboard() {
  return (
    <RoleGuard roles={["patient"]}>
      <PatientDashboardContent />
    </RoleGuard>
  );
}