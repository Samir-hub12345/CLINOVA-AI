"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  Clock,
  Layers,
  FileQuestion,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  HelpCircle,
  Check,
  X,
  Loader2,
  ArrowRight,
} from "lucide-react";
import { verificationApi } from "@/lib/api";
import {
  VerificationRun,
  VerificationFinding,
  VerificationConflict,
  FindingSeverity,
  ReviewReadinessStatus,
} from "@/types";

interface VerificationPanelProps {
  caseId: string;
  currentCaseVersion?: number;
  onRefreshCase?: () => void;
}

export function VerificationPanel({
  caseId,
  currentCaseVersion = 1,
  onRefreshCase,
}: VerificationPanelProps) {
  const [verification, setVerification] = useState<VerificationRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters & expansion state
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [expandedFindingId, setExpandedFindingId] = useState<string | null>(null);

  // Resolving finding modal/popover state
  const [resolvingFinding, setResolvingFinding] = useState<VerificationFinding | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [resolutionState, setResolutionState] = useState("RESOLVED_BY_HUMAN_VERIFICATION");
  const [submittingResolution, setSubmittingResolution] = useState(false);

  const fetchVerification = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await verificationApi.getLatestVerification(caseId);
      if (res.data) {
        setVerification(res.data);
      } else if (res.status === 404) {
        setVerification(null);
      } else {
        setError(res.error || "Unable to load verification data.");
      }
    } catch (e: any) {
      setError("Network error fetching verification run.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) fetchVerification();
  }, [caseId]);

  const handleRunVerification = async () => {
    setVerifying(true);
    setError(null);
    try {
      const res = await verificationApi.verifyCase(caseId, { force_reverify: true });
      if (res.data) {
        setVerification(res.data);
        if (onRefreshCase) onRefreshCase();
      } else {
        setError(res.error || "Verification run failed.");
      }
    } catch (e: any) {
      setError("Failed to execute case verification.");
    } finally {
      setVerifying(false);
    }
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolvingFinding || !resolutionNotes.trim()) return;

    setSubmittingResolution(true);
    try {
      const res = await verificationApi.resolveFinding(caseId, resolvingFinding.id, {
        resolution_state: resolutionState,
        resolution_notes: resolutionNotes,
      });
      if (res.data) {
        // Update local state
        setVerification((prev) => {
          if (!prev) return prev;
          const updatedFindings = (prev.findings || []).map((f) =>
            f.id === resolvingFinding.id ? res.data! : f
          );
          return {
            ...prev,
            findings: updatedFindings,
            unresolved_findings_count: Math.max(0, prev.unresolved_findings_count - 1),
            resolved_findings_count: prev.resolved_findings_count + 1,
          };
        });
        setResolvingFinding(null);
        setResolutionNotes("");
      } else {
        alert(res.error || "Unable to save finding resolution.");
      }
    } catch {
      alert("Resolution submission failed.");
    } finally {
      setSubmittingResolution(false);
    }
  };

  const getReadinessBadge = (status: ReviewReadinessStatus) => {
    switch (status) {
      case "review_ready":
        return {
          label: "REVIEW READY",
          bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" />,
        };
      case "review_ready_with_flags":
        return {
          label: "READY WITH FLAGS",
          bg: "bg-amber-50 text-amber-800 border-amber-200",
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />,
        };
      case "partially_ready":
        return {
          label: "PARTIALLY READY",
          bg: "bg-orange-50 text-orange-800 border-orange-200",
          icon: <Clock className="w-4 h-4 text-orange-600" />,
        };
      case "not_ready":
      default:
        return {
          label: "NOT READY",
          bg: "bg-rose-50 text-rose-800 border-rose-200",
          icon: <AlertOctagon className="w-4 h-4 text-rose-600" />,
        };
    }
  };

  const getSeverityBadge = (severity: FindingSeverity) => {
    switch (severity) {
      case "BLOCKING":
        return "bg-rose-100 text-rose-900 border-rose-300 font-bold";
      case "HIGH":
        return "bg-amber-100 text-amber-900 border-amber-300";
      case "MEDIUM":
        return "bg-yellow-100 text-yellow-900 border-yellow-300";
      case "LOW":
        return "bg-sky-100 text-sky-900 border-sky-300";
      case "INFO":
      default:
        return "bg-slate-100 text-slate-700 border-slate-300";
    }
  };

  const findings = verification?.findings || [];
  const conflicts = verification?.conflicts || [];

  const filteredFindings = findings.filter((f) => {
    if (severityFilter === "ALL") return true;
    return f.severity === severityFilter;
  });

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 flex items-center justify-center gap-3 text-slate-600 text-xs font-semibold">
        <Loader2 className="w-5 h-5 animate-spin text-teal-600" />
        Loading clinical case verification intelligence...
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-8">
      {/* Panel Header */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-100 text-teal-800 rounded-lg">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                Phase 4 — Clinical Information Verification & Review Readiness
              </h3>
              {verification?.is_stale && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                  STALE (v{verification.case_version} vs Current v{currentCaseVersion})
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">
              Evaluates case completeness, cross-source conflicts, temporal coherence, and provenance grounding without making autonomous clinical diagnoses.
            </p>
          </div>
        </div>

        <button
          onClick={handleRunVerification}
          disabled={verifying}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white hover:bg-teal-700 disabled:opacity-50 transition"
        >
          {verifying ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Verifying Case...
            </>
          ) : (
            <>
              <RefreshCw className="w-3.5 h-3.5" />
              {verification ? "Re-Verify Case" : "Run Verification"}
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border-b border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {!verification ? (
        <div className="p-8 text-center">
          <FileQuestion className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-800 mb-1">
            Verification Not Yet Executed
          </h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">
            No verification run has been conducted for this case. Run verification to validate information completeness, detect contradictions, and assess professional review readiness.
          </p>
          <button
            onClick={handleRunVerification}
            disabled={verifying}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg text-xs font-semibold hover:bg-teal-700 transition"
          >
            Execute Verification Pipeline
          </button>
        </div>
      ) : (
        <div className="p-6 space-y-6">
          {/* Readiness Index & Subsystem Dashboard */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Readiness Card */}
            <div className="lg:col-span-1 p-5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Review Readiness
                  </span>
                  {(() => {
                    const badge = getReadinessBadge(verification.review_readiness_status);
                    return (
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${badge.bg}`}
                      >
                        {badge.icon}
                        {badge.label}
                      </span>
                    );
                  })()}
                </div>

                {/* Score Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                    <span>Information Package Completeness</span>
                    <span>{Math.round(verification.review_readiness_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        verification.review_readiness_score >= 0.8
                          ? "bg-emerald-500"
                          : verification.review_readiness_score >= 0.5
                          ? "bg-amber-500"
                          : "bg-rose-500"
                      }`}
                      style={{ width: `${Math.round(verification.review_readiness_score * 100)}%` }}
                    />
                  </div>
                </div>

                {/* Explainable Reasons */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Readiness Evaluation Rationale:
                  </span>
                  <ul className="text-xs text-slate-700 space-y-1 list-none pl-0">
                    {verification.review_readiness_reasons.map((reason, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-teal-600 font-bold">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200 text-[10px] text-slate-500">
                Evaluation version: {verification.engine_version} | Latency: {verification.latency_ms}ms
              </div>
            </div>

            {/* Subsystems Breakdown */}
            <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Structural Integrity</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  {verification.structural_integrity_status === "VALID" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <AlertOctagon className="w-3.5 h-3.5 text-rose-600" />
                  )}
                  {verification.structural_integrity_status}
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Case Completeness</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  {verification.completeness_status === "COMPLETE" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-amber-600" />
                  )}
                  {verification.completeness_status}
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Internal Consistency</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  {verification.consistency_status === "CONSISTENT" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  )}
                  {verification.consistency_status}
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Timeline Coherence</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  {verification.temporal_status === "COHERENT" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  )}
                  {verification.temporal_status}
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Evidence Provenance</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  {verification.provenance_status === "COMPLETE" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  )}
                  {verification.provenance_status}
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-slate-200 bg-white">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Uncertainty Handling</span>
                <div className="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-teal-600" />
                  {verification.uncertainty_status}
                </div>
              </div>
            </div>
          </div>

          {/* Active Conflicts Card */}
          {conflicts.length > 0 && (
            <div className="border border-amber-300 bg-amber-50/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                  Active Cross-Source / Cross-Modal Conflicts ({conflicts.length})
                </h4>
              </div>
              <p className="text-xs text-amber-800 mb-4">
                The verification engine detected contradictory clinical facts across multimodal inputs. Both source records remain preserved in the canonical record without silent resolution:
              </p>

              <div className="space-y-3">
                {conflicts.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 bg-white rounded-lg border border-amber-200 shadow-2xs text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{c.field_name}</span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">
                        {c.conflict_type}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-700 pt-1">
                      <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                        <span className="text-[10px] font-bold text-slate-400 block uppercase mb-1">
                          Source A ({c.source_a_modality || c.source_a_type || "Source A"})
                        </span>
                        <div className="font-semibold text-slate-900">{c.source_a_value}</div>
                      </div>

                      <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                        <span className="text-[10px] font-bold text-slate-400 block uppercase mb-1">
                          Source B ({c.source_b_modality || c.source_b_type || "Source B"})
                        </span>
                        <div className="font-semibold text-slate-900">{c.source_b_value}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verification Findings Section */}
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Verification Findings ({findings.length})
                </h4>
                <p className="text-xs text-slate-500">
                  {verification.blocking_findings_count} blocking, {verification.high_findings_count} high, {verification.unresolved_findings_count} unresolved
                </p>
              </div>

              {/* Severity Filter Tabs */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-xs">
                {["ALL", "BLOCKING", "HIGH", "MEDIUM", "LOW", "INFO"].map((s) => (
                  <button
                    key={s}
                    onClick={() => setSeverityFilter(s)}
                    className={`px-2.5 py-1 rounded text-[11px] font-semibold transition ${
                      severityFilter === s
                        ? "bg-white text-slate-900 shadow-2xs"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {filteredFindings.length === 0 ? (
              <div className="p-6 text-center border border-dashed border-slate-200 rounded-xl text-slate-500 text-xs">
                No information verification findings match the selected filter.
              </div>
            ) : (
              <div className="border border-slate-200 rounded-xl divide-y divide-slate-200 overflow-hidden">
                {filteredFindings.map((finding) => {
                  const isExpanded = expandedFindingId === finding.id;
                  const isResolved = finding.status !== "UNRESOLVED";

                  return (
                    <div key={finding.id} className="p-4 hover:bg-slate-50/50 transition">
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(
                                finding.severity
                              )}`}
                            >
                              {finding.severity}
                            </span>
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                              {finding.category}
                            </span>
                            <h5 className="text-xs font-bold text-slate-900">{finding.title}</h5>
                            {isResolved && (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                                <Check className="w-3 h-3" />
                                Resolved
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-600">{finding.description}</p>
                        </div>

                        <div className="flex items-center gap-2">
                          {!isResolved && (
                            <button
                              onClick={() => setResolvingFinding(finding)}
                              className="px-2.5 py-1 text-xs font-semibold rounded bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 transition"
                            >
                              Resolve
                            </button>
                          )}
                          <button
                            onClick={() =>
                              setExpandedFindingId(isExpanded ? null : finding.id)
                            }
                            className="p-1 text-slate-400 hover:text-slate-600 rounded"
                          >
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Expandable details */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-slate-100 text-xs space-y-2 bg-slate-50/80 p-3 rounded-lg">
                          <div>
                            <span className="font-bold text-slate-700">Clinical Information Rationale: </span>
                            <span className="text-slate-600">{finding.explanation}</span>
                          </div>
                          {finding.expected_information && (
                            <div>
                              <span className="font-bold text-slate-700">Expected: </span>
                              <span className="text-slate-600">{finding.expected_information}</span>
                            </div>
                          )}
                          {finding.observed_information && (
                            <div>
                              <span className="font-bold text-slate-700">Observed: </span>
                              <span className="text-slate-600">{finding.observed_information}</span>
                            </div>
                          )}
                          {isResolved && finding.resolution_notes && (
                            <div className="p-2 bg-emerald-50 border border-emerald-200 rounded text-emerald-900">
                              <span className="font-bold">Resolution Note: </span>
                              {finding.resolution_notes}
                            </div>
                          )}
                          <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                            <span>Rule: {finding.rule_id} (v{finding.rule_version})</span>
                            {finding.source_evidence_ids && (
                              <span>Evidence Links: {finding.source_evidence_ids.join(", ")}</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Clinician Finding Resolution Modal */}
      {resolvingFinding && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-bold text-slate-900">
                Resolve Finding: {resolvingFinding.title}
              </h4>
              <button
                onClick={() => setResolvingFinding(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleResolveSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Resolution State
                </label>
                <select
                  value={resolutionState}
                  onChange={(e) => setResolutionState(e.target.value)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2 focus:ring-2 focus:ring-teal-500"
                >
                  <option value="RESOLVED_BY_HUMAN_VERIFICATION">
                    Resolved by Clinician Verification
                  </option>
                  <option value="RESOLVED_BY_CORRECTION">Resolved by Record Correction</option>
                  <option value="DISMISSED_WITH_REASON">Dismissed with Reason</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Clinical Rationale / Notes *
                </label>
                <textarea
                  required
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="Explain why this finding is resolved (e.g. 'Verified with patient triage reading: BP 132/84 mmHg')..."
                  className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setResolvingFinding(null)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingResolution || !resolutionNotes.trim()}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white hover:bg-teal-700 disabled:opacity-50 flex items-center gap-1.5"
                >
                  {submittingResolution && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  Submit Resolution
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
