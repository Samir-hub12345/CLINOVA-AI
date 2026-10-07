"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { TimelineView } from "@/components/clinical/timeline-view";
import { ProvenanceBadge } from "@/components/clinical/provenance-badge";
import { VerificationPanel } from "@/components/clinical/verification-panel";
import { CompletionPanel } from "@/components/clinical/completion-panel";
import { api } from "@/lib/api";

import { useAuth } from "@/lib/auth";
import { TriageCase, OCRField } from "@/types";
import {
  ArrowLeft,
  CheckCircle2,
  Edit3,
  XCircle,
  Share2,
  Clock,
  FileText,
  AlertTriangle,
  ShieldAlert,
  Loader2,
  Trash2,
  Printer,
  Sparkles,
  HelpCircle,
  UserCheck,
  Activity,
} from "lucide-react";

export default function CaseReviewDetailPage() {
  const { isDoctor } = useAuth();
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const [caseData, setCaseData] = useState<TriageCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reviewer edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editedSummary, setEditedSummary] = useState("");
  const [editedCategory, setEditedCategory] = useState("routine");
  const [reviewerNotes, setReviewerNotes] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const loadCase = async () => {
    setLoading(true);
    setError(null);
    const res = await api.getCase(caseId);
    if (res.data) {
      setCaseData(res.data);
      setEditedSummary(res.data.normalized_symptoms || res.data.raw_symptoms || "");
      setEditedCategory(res.data.queue_category);
      setReviewerNotes(res.data.reviewer_notes || "");
    } else {
      setError(res.error || "Unable to load case.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (caseId) loadCase();
  }, [caseId]);

  const handleReviewAction = async (action: "approve" | "edit" | "reject" | "escalate") => {
    setActionLoading(true);
    setActionSuccess(null);
    try {
      const payload = {
        action,
        reviewer_notes: reviewerNotes,
        edited_summary: editedSummary,
        confirmed_queue_category: editedCategory,
      };

      const res = await api.performReviewAction(caseId, payload);
      if (res.data) {
        setCaseData(res.data);
        setIsEditing(false);
        setActionSuccess(`Review action '${action.toUpperCase()}' completed successfully.`);
        if (action === "escalate") {
          router.push(`/review/case/${caseId}/referral`);
        }
      } else {
        setError(res.error || "Unable to save this review.");
      }
    } catch (e: any) {
      setError("Action execution failed.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteCase = async () => {
    if (!confirm("Delete temporary intake symptoms and media per privacy retention policy?")) return;
    const res = await api.deleteCaseData(caseId);
    if (res.data) {
      alert(res.data.message);
      router.push("/review");
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col min-h-screen bg-slate-50">
        <Header />
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="flex items-center gap-2 text-teal-700 text-xs font-semibold">
            <Loader2 className="w-5 h-5 animate-spin" />
            Loading clinical case review file...
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (!caseData || error) {
    return (
      <div className="flex flex-col min-h-screen bg-slate-50">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center p-12 space-y-4">
          <p className="text-sm font-bold text-rose-700">{error || "Case not found."}</p>
          <Link href="/review" className="text-xs text-teal-600 font-semibold underline">
            Return to Review Queue
          </Link>
        </div>
        <Footer />
      </div>
    );
  }

  const isUrgent = caseData.queue_category === "urgent-review";
  const isPriority = caseData.queue_category === "priority";

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header />

      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 sm:px-6 w-full space-y-6">
        {/* Safety Disclaimer Banner */}
        <ClinicalDisclaimer />

        {/* Action feedback */}
        {actionSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-800 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Section A: Case Header */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <Link
                href="/review"
                className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-500"
                title="Back to queue"
              >
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold text-slate-900">
                    Case {caseData.synthetic_case_id}
                  </h1>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                    SYNTHETIC DEMO
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Facility: <strong className="text-slate-700">{caseData.facility_type}</strong> &bull; Visit Type: <strong className="text-slate-700">{caseData.visit_type}</strong>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full font-bold text-xs uppercase tracking-wider ${
                  isUrgent
                    ? "bg-rose-100 text-rose-900 border border-rose-200"
                    : isPriority
                    ? "bg-amber-100 text-amber-900 border border-amber-200"
                    : "bg-teal-50 text-teal-800 border border-teal-200"
                }`}
              >
                {caseData.queue_category.replace("-", " ")}
              </span>

              <span className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 capitalize">
                Status: {caseData.status.replace("_", " ")}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Demographics</span>
              <span className="font-semibold text-slate-800">
                {caseData.approximate_age ? `${caseData.approximate_age} years old` : "Adult"} &bull; {caseData.gender || "Unspecified"}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Language</span>
              <span className="font-semibold text-slate-800 uppercase">{caseData.language}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Waiting Time</span>
              <span className="font-semibold text-slate-800 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {caseData.waiting_minutes || 0} minutes
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Assigned Reviewer</span>
              <span className="font-semibold text-slate-800">
                {caseData.reviewer_name || "Unassigned (Awaiting Review)"}
              </span>
            </div>
          </div>
        </div>

        {/* Section B0: Verified Triage Vitals & Routing */}
        {caseData.vitals && (
          <div className="p-4 bg-teal-50/70 border border-teal-200 rounded-2xl flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-2 font-bold text-teal-900">
              <Activity className="w-4 h-4 text-teal-600" />
              <span>Verified Clinical Vitals {caseData.intake_verified ? "(Staff Verified)" : "(Patient Reported)"}</span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-slate-700 font-medium">
              {caseData.vitals.blood_pressure && (
                <span>BP: <strong className="text-slate-900">{caseData.vitals.blood_pressure}</strong> mmHg</span>
              )}
              {caseData.vitals.heart_rate && (
                <span>Heart Rate: <strong className="text-slate-900">{caseData.vitals.heart_rate}</strong> bpm</span>
              )}
              {caseData.vitals.oxygen_saturation && (
                <span>SpO2: <strong className="text-slate-900">{caseData.vitals.oxygen_saturation}</strong>%</span>
              )}
              {caseData.vitals.temperature && (
                <span>Temp: <strong className="text-slate-900">{caseData.vitals.temperature}</strong> °C</span>
              )}
              {caseData.assigned_department && (
                <span className="px-2 py-0.5 rounded bg-teal-100 text-teal-800 font-bold">
                  Department: {caseData.assigned_department}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Section B_VERIFY: Phase 4 Verification & Review Readiness */}
        <VerificationPanel
          caseId={caseData.id}
          currentCaseVersion={caseData.case_version}
          onRefreshCase={loadCase}
        />

        {/* Section B_COMPLETE: Phase 5 Intelligent Completion & Adaptive Interview */}
        <CompletionPanel
          caseId={caseData.id}
          onCaseUpdated={loadCase}
        />

        {/* Section B: Patient Provided Information */}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Original Patient Narrative
              </h3>
              <ProvenanceBadge
                sourceType={caseData.speech_transcript ? "voice" : "direct"}
                label={caseData.speech_transcript ? "Speech-to-Text" : "Direct Input"}
              />
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed font-mono">
              "{caseData.raw_symptoms}"
            </div>

            {caseData.speech_transcript && (
              <p className="text-[11px] text-slate-500 italic">
                * Audio transcribed automatically with speech-to-text demo fallback.
              </p>
            )}
          </div>

          {/* Section F: AI Information Organization */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Structured Clinical Summary (Non-Diagnostic)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-200">
                HUMAN REVIEW REQUIRED
              </span>
            </div>

            {isEditing ? (
              <div className="space-y-2 text-xs">
                <textarea
                  value={editedSummary}
                  onChange={(e) => setEditedSummary(e.target.value)}
                  rows={4}
                  className="w-full p-2.5 rounded-lg border border-teal-400 text-xs text-slate-900 bg-white"
                />
                <div className="flex items-center gap-2">
                  <label className="font-bold text-slate-600">Urgency Category:</label>
                  <select
                    value={editedCategory}
                    onChange={(e) => setEditedCategory(e.target.value)}
                    className="p-1 rounded border border-slate-300 text-xs"
                  >
                    <option value="routine">Routine</option>
                    <option value="priority">Priority</option>
                    <option value="urgent-review">Urgent Review</option>
                  </select>
                </div>
              </div>
            ) : (
              <div className="p-3.5 rounded-xl bg-teal-50/40 border border-teal-200 text-xs text-slate-800 leading-relaxed">
                {caseData.normalized_symptoms}
              </div>
            )}

            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
              <span>Provenance: Extracted from patient narrative &amp; normalized.</span>
              {isDoctor && <button
                type="button"
                onClick={() => setIsEditing(!isEditing)}
                className="text-teal-700 hover:text-teal-800 font-bold flex items-center gap-1 text-xs"
              >
                <Edit3 className="w-3.5 h-3.5" />
                {isEditing ? "Cancel Edit" : "Edit Summary"}
              </button>}
            </div>
          </div>
        </div>

        {/* Section C & D: Timeline and Report OCR */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section C: Timeline View */}
          <TimelineView events={caseData.timeline_events || []} />

          {/* Section D: OCR Report Data */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-sky-600" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Extracted Lab Report Parameters
                </h3>
              </div>
              {caseData.report_ocr_data && (
                <ProvenanceBadge sourceType="ocr" label={caseData.report_filename || "CBC Report"} />
              )}
            </div>

            {caseData.report_ocr_data && caseData.report_ocr_data.length > 0 ? (
              <div className="space-y-2">
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
                  {caseData.report_ocr_data.map((param, idx) => (
                    <div key={idx} className="p-2.5 bg-slate-50 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-semibold text-slate-900 block">{param.field_name}</span>
                        <span className="text-[11px] text-slate-500">
                          Confidence: {Math.round(param.confidence * 100)}%
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="font-mono font-bold text-slate-900 text-xs">
                          {param.value} {param.unit}
                        </span>
                        <span className="block text-[10px] text-emerald-700 font-bold">Verified</span>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-[10px] text-slate-400 italic">
                  * OCR extracted from synthetic pathology specimen. Not an automated diagnosis.
                </p>
              </div>
            ) : (
              <div className="p-6 text-center border-2 border-dashed border-slate-200 rounded-xl text-xs text-slate-500">
                No previous diagnostic report attached. Intake completed with primary symptoms only.
              </div>
            )}
          </div>
        </div>

        {/* Section G: Missing Information & Follow-Up Questions */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
            <HelpCircle className="w-4 h-4 text-teal-600" />
            <span>Missing Information Engine &bull; Recommended Follow-Up Inquiries</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {caseData.follow_up_questions && caseData.follow_up_questions.length > 0 ? (
              caseData.follow_up_questions.map((q, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-bold text-teal-700 uppercase block">
                    Suggested Clinician Query #{idx + 1}
                  </span>
                  <p className="text-slate-800 font-medium">"{q}"</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">Baseline information complete for intake.</p>
            )}
          </div>
        </div>

        {/* Section H: Review Signals (Rule Engine) */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                Deterministic Review Signals (Prototype Rules &bull; Transparent Attention Flags)
              </h3>
            </div>
            <ProvenanceBadge sourceType="rule" label="Explainable Logic" />
          </div>

          {caseData.risk_signals && caseData.risk_signals.length > 0 ? (
            <div className="space-y-2">
              {caseData.risk_signals.map((sig, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-amber-50/60 border border-amber-200 text-xs flex items-center justify-between"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-amber-900">{sig.rule_id}</span>
                      <span className="font-bold text-amber-800">{sig.signal}</span>
                    </div>
                    <p className="text-[11px] text-amber-700">
                      Triggered by text match: <strong>"{sig.source_text}"</strong> &bull; Reviewer confirmation required.
                    </p>
                  </div>
                  <span className="text-[10px] font-bold uppercase px-2 py-0.5 bg-white text-amber-800 rounded border border-amber-300">
                    {sig.status.replace("_", " ")}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500">No high-risk emergency rules triggered.</p>
          )}
        </div>

        {/* Section I: Reviewer Actions Bar (Human-in-the-Loop Gate) */}
        <div className="p-6 rounded-2xl bg-slate-900 text-white shadow-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-teal-400" />
                <span>Human Review Gate &bull; Medical Officer Sign-Off</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                AI outputs cannot proceed to clinical handoff without explicit qualified human review.
              </p>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-teal-300 border border-slate-700">
              MANDATORY GATE
            </span>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Reviewer Clinical Notes</label>
            <input
              type="text"
              disabled={!isDoctor}
              value={reviewerNotes}
              onChange={(e) => setReviewerNotes(e.target.value)}
              placeholder="e.g. Verified by Dr. S. Chen: Patient stable, proceed with OPD consultation or tertiary referral..."
              className="w-full p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-teal-400"
            />
          </div>

          {isDoctor ? <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <div className="flex flex-wrap items-center gap-2">
              {isEditing && <button type="button" disabled={actionLoading} onClick={() => handleReviewAction("edit")} className="px-4 py-2.5 bg-teal-700 rounded-xl text-xs font-bold">Save edits</button>}
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => handleReviewAction("approve")}
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Confirm &amp; Approve Note</span>
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={() => handleReviewAction("escalate")}
                className="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition-all"
              >
                <Share2 className="w-4 h-4" />
                <span>Prepare Referral Support Note</span>
              </button>

              <button
                type="button"
                disabled={actionLoading}
                onClick={() => handleReviewAction("reject")}
                className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-rose-300 font-bold rounded-xl text-xs flex items-center gap-1.5 border border-slate-700 transition-all"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject / Flag Re-Intake</span>
              </button>
            </div>

            {/* Privacy control: Data retention deletion */}
            <button
              type="button"
              onClick={handleDeleteCase}
              className="px-3.5 py-2 text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 rounded-xl text-xs font-semibold flex items-center gap-1 transition-all"
              title="Delete temporary intake media per privacy retention policy"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Case Data</span>
            </button>
          </div> : <p className="text-sm text-slate-300">Doctor sign-off is required. Nurse access is view only.</p>}
        </div>
      </main>

      <Footer />
    </div>
  );
}