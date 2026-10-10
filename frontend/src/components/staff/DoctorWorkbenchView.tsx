"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  Share2,
  ArrowLeft,
  FileScan,
  AlertTriangle,
  Edit3,
  XCircle,
  HelpCircle,
  Send,
  Lock,
  Check,
} from "lucide-react";
import { CareGraphData, OrchestrationEvaluation, HumanDecisionAction, TriageSnapshot, CaseReviewContext } from "@/types";
import {
  getCaseDetails,
  evaluateOrchestration,
  submitClinicianDecision,
  verifyEvidenceItem,
  modifyEvidenceItem,
  rejectEvidenceItem,
  resolveEvidenceConflict,
  requestClinicalInformation,
  recordCaseDisposition,
  closeCaseEncounter,
  getTriageSnapshot,
  startClinicalReview,
  getCaseReviewContext,
} from "@/lib/api";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { EvidenceBadge } from "@/components/ui/EvidenceBadge";
import { UncertaintyIndicator } from "@/components/ui/UncertaintyIndicator";
import { VitalCard } from "@/components/ui/VitalCard";
import { RedFlagBanner } from "@/components/ui/RedFlagBanner";
import { Timeline } from "@/components/ui/Timeline";
import { RecommendationCard } from "@/components/ui/RecommendationCard";
import { HumanDecisionCard } from "@/components/ui/HumanDecisionCard";
import { AIAdvisoryPanel } from "@/components/staff/AIAdvisoryPanel";
import { DocumentUpload } from "@/components/staff/DocumentUpload";
import { MultilingualTranslationPanel } from "@/components/staff/MultilingualTranslationPanel";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/States";
import { RoleGuard } from "@/components/common/RoleGuard";
import { DownloadReportButton } from "@/components/common/DownloadReportButton";

interface DoctorWorkbenchViewProps {
  caseId: string;
}

export const DoctorWorkbenchView: React.FC<DoctorWorkbenchViewProps> = ({ caseId }) => {
  const [data, setData] = useState<CareGraphData | null>(null);
  const [evaluation, setEvaluation] = useState<OrchestrationEvaluation | null>(null);
  const [triageSnapshot, setTriageSnapshot] = useState<TriageSnapshot | null>(null);
  const [reviewContext, setReviewContext] = useState<CaseReviewContext | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [caseRes, evalRes, triageRes, reviewCtxRes] = await Promise.all([
          getCaseDetails(caseId),
          evaluateOrchestration(caseId),
          getTriageSnapshot(caseId).catch(() => null),
          getCaseReviewContext(caseId).catch(() => null),
        ]);
        setData(caseRes);
        setEvaluation(evalRes);
        setTriageSnapshot(triageRes);
        setReviewContext(reviewCtxRes);
        if (caseRes.case.status === "CLINICIAN_REVIEW_REQUIRED" || caseRes.case.status === "REVIEW_REQUIRED") {
          startClinicalReview(caseId).catch(() => null);
        }
      } catch (err) {
        console.warn("Failed to load workbench data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [caseId]);

  const handleDecision = async (action: HumanDecisionAction, notes: string) => {
    await submitClinicianDecision({
      case_id: caseId,
      action,
      clinician_id: "usr-doc-01",
      notes,
    });
    try {
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch {
      // Keep state
    }
  };

  const handleVerifyEvidence = async (evidenceId: string) => {
    await verifyEvidenceItem(caseId, evidenceId, "usr-doc-01", "CONFIRMED");
    try {
      const reviewCtxRes = await getCaseReviewContext(caseId).catch(() => null);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch {
      // Keep state
    }
    // Update local state to show verified badge immediately
    if (data) {
      setData({
        ...data,
        evidence_records: data.evidence_records.map((ev) =>
          ev.id === evidenceId
            ? { ...ev, verification_status: "CONFIRMED", verified_by: "Dr. Priya Sharma" }
            : ev
        ),
      });
    }
  };

  // Evidence modification & rejection state
  const [modifyingEvidenceId, setModifyingEvidenceId] = useState<string | null>(null);
  const [modifiedValue, setModifiedValue] = useState("");
  const [modifyReason, setModifyReason] = useState("");
  const [rejectingEvidenceId, setRejectingEvidenceId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");

  // Conflict resolution state
  const [resolvingConflictId, setResolvingConflictId] = useState<string | null>(null);
  const [conflictAuthoritativeId, setConflictAuthoritativeId] = useState("");
  const [conflictResolvedValue, setConflictResolvedValue] = useState("");
  const [conflictRationale, setConflictRationale] = useState("");

  // Information request state
  const [showInfoRequestForm, setShowInfoRequestForm] = useState(false);
  const [infoQuestion, setInfoQuestion] = useState("");
  const [infoReason, setInfoReason] = useState("");
  const [infoPriority, setInfoPriority] = useState<"CRITICAL" | "IMPORTANT" | "OPTIONAL">("IMPORTANT");

  // Disposition & Closure state
  const [dispositionType, setDispositionType] = useState("DISCHARGE_HOME");
  const [dispositionSummary, setDispositionSummary] = useState("");
  const [dispositionCloseCase, setDispositionCloseCase] = useState(false);
  const [isSubmittingDisposition, setIsSubmittingDisposition] = useState(false);
  const [dispositionFeedback, setDispositionFeedback] = useState<string | null>(null);
  const [showCloseForm, setShowCloseForm] = useState(false);
  const [closeReason, setCloseReason] = useState("");
  const [isSubmittingClose, setIsSubmittingClose] = useState(false);
  const [closeFeedback, setCloseFeedback] = useState<string | null>(null);

  const handleModifyEvidence = async (evidenceId: string) => {
    if (!modifyReason.trim()) return;
    try {
      await modifyEvidenceItem(caseId, evidenceId, modifiedValue, modifyReason);
      setModifyingEvidenceId(null);
      setModifiedValue("");
      setModifyReason("");
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err) {
      console.warn("Modify evidence failed:", err);
    }
  };

  const handleRejectEvidence = async (evidenceId: string) => {
    if (!rejectReason.trim()) return;
    try {
      await rejectEvidenceItem(caseId, evidenceId, rejectReason);
      setRejectingEvidenceId(null);
      setRejectReason("");
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err) {
      console.warn("Reject evidence failed:", err);
    }
  };

  const handleResolveConflict = async () => {
    if (!conflictRationale.trim()) return;
    try {
      await resolveEvidenceConflict(caseId, {
        authoritative_evidence_id: conflictAuthoritativeId || undefined,
        resolved_value: conflictResolvedValue || undefined,
        resolution_rationale: conflictRationale,
      });
      setResolvingConflictId(null);
      setConflictRationale("");
      setConflictAuthoritativeId("");
      setConflictResolvedValue("");
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err) {
      console.warn("Resolve conflict failed:", err);
    }
  };

  const handleRequestInformation = async () => {
    if (!infoQuestion.trim() || !infoReason.trim()) return;
    try {
      await requestClinicalInformation(caseId, infoQuestion, infoReason, infoPriority);
      setShowInfoRequestForm(false);
      setInfoQuestion("");
      setInfoReason("");
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err) {
      console.warn("Request information failed:", err);
    }
  };

  const handleRecordDisposition = async () => {
    if (!dispositionSummary.trim()) return;
    setIsSubmittingDisposition(true);
    setDispositionFeedback(null);
    try {
      await recordCaseDisposition(caseId, dispositionType, dispositionSummary, dispositionCloseCase);
      setDispositionFeedback(`Disposition [${dispositionType}] recorded.`);
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setDispositionFeedback(`Error: ${e?.message || "Failed to record disposition"}`);
    } finally {
      setIsSubmittingDisposition(false);
    }
  };

  const handleCloseEncounter = async () => {
    if (!closeReason.trim()) return;
    setIsSubmittingClose(true);
    setCloseFeedback(null);
    try {
      await closeCaseEncounter(caseId, closeReason);
      setShowCloseForm(false);
      setCloseFeedback("Case closed successfully.");
      const [caseRes, reviewCtxRes] = await Promise.all([
        getCaseDetails(caseId),
        getCaseReviewContext(caseId).catch(() => null),
      ]);
      setData(caseRes);
      if (reviewCtxRes) setReviewContext(reviewCtxRes);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setCloseFeedback(`Error: ${e?.message || "Failed to close case"}`);
    } finally {
      setIsSubmittingClose(false);
    }
  };

  if (loading || !data || !evaluation) {
    return <LoadingState message={`Assembling clinical workbench for Case ${caseId}...`} lines={6} />;
  }

  const { case: caseInfo, uncertainty, vitals_history, red_flags, timeline, evidence_records } = data;
  const latestVitals = vitals_history[vitals_history.length - 1] || {};

  return (
    <RoleGuard
      allowedRoles={["CLINICIAN", "DOCTOR", "SYSTEM_ADMIN", "AUDITOR"]}
      title="Doctor Workbench Access Restricted"
      message="Only licensed medical clinicians, department reviewers, and audit officers hold authority to access the clinical case workbench."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
      {/* Top Breadcrumb & Case Bar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Link href="/staff/triage" className="clinova-btn clinova-btn-outline clinova-btn-sm" style={{ textDecoration: "none" }}>
            <ArrowLeft style={{ width: 13, height: 13 }} aria-hidden="true" />
            <span>Triage Worklist</span>
          </Link>
          <span style={{ color: "var(--clinova-border-strong)" }}>|</span>
          <h2 style={{ fontSize: "1.25rem", margin: 0 }}>
            Case File: <span className="clinova-mono">{caseInfo.id}</span>
          </h2>
          <span className="clinova-badge" style={{ backgroundColor: "#f1f5f9", color: "#334155", borderColor: "#cbd5e1" }}>
            {caseInfo.patient_synthetic_id}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <DownloadReportButton caseId={caseInfo.id} label="Export Case PDF" size="sm" variant="outline" />
          <PriorityBadge tier={caseInfo.acuity_tier} />
          <StatusBadge status={caseInfo.status} />
        </div>
      </div>

      {/* Emergency Resuscitation Alert Banner (when active) */}
      {caseInfo.emergency_active && (
        <RedFlagBanner
          flags={red_flags}
          onInitiateResuscitation={() => {
            alert("Resuscitation Bay alert broadcasted. Clinical team dispatched to bedside.");
          }}
        />
      )}

      {/* 3-Panel Asymmetric Doctor Workbench Layout */}
      <div className="clinova-workbench-grid">
        {/* =========================================================================
            PANEL 1 (LEFT, 300px): Case Identity, Pathway, Key Vitals, Red Flags
            ========================================================================= */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          {/* Patient Demographic Card */}
          <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <span className="clinova-label">PATIENT CONTEXT</span>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
              <strong style={{ fontSize: "1.125rem", color: "var(--clinova-text-primary)" }}>
                {caseInfo.patient_synthetic_id}
              </strong>
              <span className="clinova-mono" style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)" }}>
                {caseInfo.case_number}
              </span>
            </div>
            <div style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)" }}>
              <span>Bracket: <strong>{caseInfo.age_bracket}</strong></span> • <span>Sex: <strong>{caseInfo.biological_sex}</strong></span>
            </div>
            <div style={{ marginTop: 4, paddingTop: 6, borderTop: "1px solid var(--clinova-border)" }}>
              <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>CHIEF COMPLAINT:</span>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", marginTop: 2 }}>
                {caseInfo.presenting_complaint}
              </p>
            </div>
          </div>

          {/* Key Vitals Matrix */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="clinova-label">PHYSIOLOGICAL VITALS</span>
              <span className="clinova-mono" style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                Latest: {latestVitals.recorded_at || "Triage"}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <VitalCard
                label="BLOOD PRESSURE"
                value={latestVitals.systolic_bp && latestVitals.diastolic_bp ? `${latestVitals.systolic_bp}/${latestVitals.diastolic_bp}` : undefined}
                unit="mmHg"
                normalRange="110-130/70-85"
                isAbnormal={(latestVitals.systolic_bp || 120) < 95 || (latestVitals.systolic_bp || 120) > 160}
                isCritical={(latestVitals.systolic_bp || 120) < 90}
                provenance={latestVitals.provenance}
                freshnessStatus={triageSnapshot?.vitals_freshness?.systolic_bp}
              />
              <VitalCard
                label="HEART RATE"
                value={latestVitals.heart_rate}
                unit="bpm"
                normalRange="60-100"
                isAbnormal={(latestVitals.heart_rate || 72) > 100 || (latestVitals.heart_rate || 72) < 55}
                isCritical={(latestVitals.heart_rate || 72) > 120}
                provenance={latestVitals.provenance}
                freshnessStatus={triageSnapshot?.vitals_freshness?.heart_rate}
              />
              <VitalCard
                label="SPO2 OXYGEN"
                value={latestVitals.spo2_percent}
                unit="%"
                normalRange=">= 95%"
                isAbnormal={(latestVitals.spo2_percent || 99) < 95}
                isCritical={(latestVitals.spo2_percent || 99) < 92}
                provenance={latestVitals.provenance}
                freshnessStatus={triageSnapshot?.vitals_freshness?.spo2_percent}
              />
              <VitalCard
                label="RESPIRATORY RATE"
                value={latestVitals.respiratory_rate}
                unit="/min"
                normalRange="12-20"
                isAbnormal={(latestVitals.respiratory_rate || 16) > 22}
                isCritical={(latestVitals.respiratory_rate || 16) > 26}
                provenance={latestVitals.provenance}
                freshnessStatus={triageSnapshot?.vitals_freshness?.respiratory_rate}
              />
            </div>
          </div>

          {/* Deterministic Triage Metrics (RCP NEWS2 + Shock Index) */}
          <div className="clinova-card" style={{ padding: 12 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="clinova-label">DETERMINISTIC TRIAGE METRICS</span>
              <span className="clinova-badge" style={{ fontSize: "0.625rem", padding: "1px 6px" }}>
                Non-Diagnostic
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 8 }}>
              {/* NEWS2 Card */}
              <div style={{ padding: "8px 10px", backgroundColor: "var(--clinova-surface-subtle)", borderRadius: "var(--clinova-radius-md)", border: "1px solid var(--clinova-border)" }}>
                <span className="clinova-label" style={{ fontSize: "0.625rem" }}>NEWS2 (RCP 2017)</span>
                <div style={{ display: "flex", alignItems: "baseline", gap: 6, margin: "2px 0" }}>
                  <strong className="clinova-mono" style={{ fontSize: "1.25rem", color: "var(--clinova-text-primary)" }}>
                    {triageSnapshot?.news2?.is_complete ? triageSnapshot.news2.score : "Incomplete"}
                  </strong>
                  {triageSnapshot?.news2?.risk_level && (
                    <span className="clinova-badge" style={{ fontSize: "0.625rem" }}>
                      {triageSnapshot.news2.risk_level}
                    </span>
                  )}
                </div>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                  {triageSnapshot?.news2?.is_complete
                    ? "Full physiological vector"
                    : triageSnapshot?.news2?.limitation || "Partial vitals"}
                </span>
              </div>

              {/* Shock Index Card */}
              <div style={{ padding: "8px 10px", backgroundColor: "var(--clinova-surface-subtle)", borderRadius: "var(--clinova-radius-md)", border: "1px solid var(--clinova-border)" }}>
                <span className="clinova-label" style={{ fontSize: "0.625rem" }}>SHOCK INDEX</span>
                <div style={{ display: "flex", alignItems: "baseline", gap: 6, margin: "2px 0" }}>
                  <strong className="clinova-mono" style={{ fontSize: "1.25rem", color: "var(--clinova-text-primary)" }}>
                    {triageSnapshot?.shock_index?.is_complete ? triageSnapshot.shock_index.score : "—"}
                  </strong>
                  {triageSnapshot?.shock_index?.interpretation && (
                    <span className="clinova-badge" style={{ fontSize: "0.625rem" }}>
                      {triageSnapshot.shock_index.interpretation}
                    </span>
                  )}
                </div>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                  HR / SBP (Allgöwer & Burri)
                </span>
              </div>
            </div>

            {triageSnapshot?.priority_tier && (
              <div style={{ marginTop: 8, paddingTop: 6, borderTop: "1px solid var(--clinova-border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>Operational Priority:</span>
                <span className="clinova-mono" style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--clinova-text-primary)" }}>
                  {triageSnapshot.priority_tier}
                </span>
              </div>
            )}
          </div>
          
          <DocumentUpload caseId={caseId} />

          {/* Physiological Trajectory Card */}
          <div className="clinova-card" style={{ padding: 12 }}>
            <span className="clinova-label">PHYSIOLOGICAL TRAJECTORY</span>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 4 }}>
              <span className="clinova-mono" style={{ fontSize: "1.125rem", fontWeight: 700, color: data.trajectory.trend === "CRITICAL" ? "var(--clinova-danger-text)" : "var(--clinova-text-primary)" }}>
                Trend: {data.trajectory.trend}
              </span>
              <span className="clinova-badge" style={{ backgroundColor: "#f1f5f9", color: "#334155", borderColor: "#cbd5e1" }}>
                Slope: {data.trajectory.slope > 0 ? `+${data.trajectory.slope}` : data.trajectory.slope}
              </span>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)", marginTop: 4 }}>
              Derived across {data.trajectory.readings_count} sequential bedside recordings.
            </p>
          </div>
        </div>

        {/* =========================================================================
            PANEL 2 (CENTER, minmax(0, 1fr)): Timeline, Evidence with Provenance,
            Missing Information Audit, Contradiction Callouts
            ========================================================================= */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-5)" }}>
          {/* Epistemic Gaps & Missing Information Audit */}
          <div
            className="clinova-card"
            style={{
              backgroundColor: "var(--clinova-surface)",
              border: "1px solid var(--clinova-border)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
              <span className="clinova-label">EPISTEMIC UNCERTAINTY & MISSING PARAMETERS</span>
              <span className="clinova-badge" style={{ backgroundColor: "#fef3c7", color: "#92400e", borderColor: "#fde68a" }}>
                Completeness: {Math.round(uncertainty.protocol_completeness * 100)}%
              </span>
            </div>

            {uncertainty.uncertainty_items && uncertainty.uncertainty_items.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {uncertainty.uncertainty_items.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "8px 12px",
                      borderRadius: "var(--clinova-radius-md)",
                      border: "1px solid var(--clinova-border)",
                      backgroundColor: "var(--clinova-surface-subtle)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <strong style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)" }}>
                        {item.parameter}
                      </strong>
                      <UncertaintyIndicator status={item.status} />
                    </div>
                    <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
                      {item.explanation}
                    </p>
                    {item.suggested_question && (
                      <span style={{ fontSize: "0.6875rem", color: "var(--clinova-accent-text)", fontWeight: 600 }}>
                        Action: {item.suggested_question}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)", fontStyle: "italic" }}>
                No significant epistemic gaps identified for this standard protocol.
              </p>
            )}

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 6 }}>
              <span className="clinova-metadata">Clinical Information Requests</span>
              <Button size="sm" variant="outline" onClick={() => setShowInfoRequestForm(!showInfoRequestForm)}>
                <HelpCircle style={{ width: 12, height: 12 }} />
                <span>Request Information</span>
              </Button>
            </div>

            {showInfoRequestForm && (
              <div style={{ padding: 10, background: "var(--clinova-surface-subtle)", borderRadius: 6, border: "1px solid var(--clinova-border)", display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                <strong style={{ fontSize: "0.8125rem" }}>Request Missing Clinical Data</strong>
                <input
                  type="text"
                  className="clinova-input"
                  style={{ fontSize: "0.75rem" }}
                  placeholder="Targeted question (e.g. Confirm time of symptom onset)..."
                  value={infoQuestion}
                  onChange={(e) => setInfoQuestion(e.target.value)}
                />
                <input
                  type="text"
                  className="clinova-input"
                  style={{ fontSize: "0.75rem" }}
                  placeholder="Clinical reason (e.g. Critical for thrombolytic eligibility)..."
                  value={infoReason}
                  onChange={(e) => setInfoReason(e.target.value)}
                />
                <div style={{ display: "flex", gap: 6, alignItems: "center", justifyContent: "space-between" }}>
                  <select
                    className="clinova-select"
                    style={{ fontSize: "0.75rem", padding: "2px 6px" }}
                    value={infoPriority}
                    onChange={(e) => setInfoPriority(e.target.value as "CRITICAL" | "IMPORTANT" | "OPTIONAL")}
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="IMPORTANT">IMPORTANT</option>
                    <option value="OPTIONAL">OPTIONAL</option>
                  </select>
                  <div style={{ display: "flex", gap: 6 }}>
                    <Button size="sm" variant="outline" onClick={() => setShowInfoRequestForm(false)}>Cancel</Button>
                    <Button size="sm" variant="primary" onClick={handleRequestInformation} disabled={!infoQuestion.trim() || !infoReason.trim()}>
                      <Send style={{ width: 11, height: 11 }} />
                      <span>Submit Request</span>
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {reviewContext?.follow_ups && reviewContext.follow_ups.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: 6 }}>
                <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>PENDING & RECORDED FOLLOW-UPS:</span>
                {reviewContext.follow_ups.map((fq, fqi) => {
                  const answersList = Array.isArray(fq.answers) ? (fq.answers as Array<Record<string, unknown>>) : [];
                  return (
                    <div key={fqi} style={{ padding: "6px 8px", background: "var(--clinova-surface)", borderRadius: 4, border: "1px solid var(--clinova-border)", fontSize: "0.75rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <strong>{String(fq.question_text || "")}</strong>
                        <span className="clinova-badge" style={{ fontSize: "0.625rem" }}>{String(fq.status || "")}</span>
                      </div>
                      {answersList.length > 0 && (
                        <p style={{ margin: "2px 0 0", color: "var(--clinova-success-text)" }}>
                          Answer: {String(answersList[0]?.answer_text || "")}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Contradiction Callout (when conflicting data exists) */}
            {uncertainty.conflicts && uncertainty.conflicts.length > 0 && (
              <div
                style={{
                  marginTop: 12,
                  padding: "10px 12px",
                  borderRadius: "var(--clinova-radius-md)",
                  border: "1px solid var(--clinova-epistemic-conflicting-border)",
                  backgroundColor: "var(--clinova-epistemic-conflicting-bg)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <AlertTriangle style={{ width: 14, height: 14, color: "var(--clinova-epistemic-conflicting)" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.8125rem", color: "var(--clinova-epistemic-conflicting)" }}>
                    UNRESOLVED EVIDENCE CONFLICT DETECTED
                  </strong>
                </div>
                {uncertainty.conflicts.map((conf, ci) => (
                  <div key={ci} style={{ fontSize: "0.75rem", color: "#9f1239", borderTop: ci > 0 ? "1px solid #fecdd3" : undefined, paddingTop: ci > 0 ? 6 : 0 }}>
                    <span>Parameter: <strong>{conf.parameter}</strong></span>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 4 }}>
                      <div style={{ background: "#ffffff", padding: 6, borderRadius: 4, border: "1px solid #fecdd3" }}>
                        <strong>{conf.source_a.source}:</strong> {conf.source_a.value}
                      </div>
                      <div style={{ background: "#ffffff", padding: 6, borderRadius: 4, border: "1px solid #fecdd3" }}>
                        <strong>{conf.source_b.source}:</strong> {conf.source_b.value}
                      </div>
                    </div>
                    <span style={{ display: "block", marginTop: 4, fontStyle: "italic" }}>
                      Risk: {conf.clinical_risk}
                    </span>

                    {resolvingConflictId === conf.parameter ? (
                      <div style={{ marginTop: 8, padding: 8, background: "#ffffff", borderRadius: 4, border: "1px solid #fecdd3", display: "flex", flexDirection: "column", gap: 6 }}>
                        <strong style={{ color: "#881337" }}>Resolve Conflict: {conf.parameter}</strong>
                        <input
                          type="text"
                          className="clinova-input"
                          style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                          placeholder="Authoritative / Resolved Value (optional override)..."
                          value={conflictResolvedValue}
                          onChange={(e) => setConflictResolvedValue(e.target.value)}
                        />
                        <textarea
                          className="clinova-textarea"
                          style={{ fontSize: "0.75rem", minHeight: 48, padding: "4px 8px" }}
                          placeholder="Mandatory clinical rationale for resolving conflict..."
                          value={conflictRationale}
                          onChange={(e) => setConflictRationale(e.target.value)}
                        />
                        <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                          <Button size="sm" variant="outline" onClick={() => setResolvingConflictId(null)}>Cancel</Button>
                          <Button size="sm" variant="primary" onClick={handleResolveConflict} disabled={!conflictRationale.trim()}>Commit Resolution</Button>
                        </div>
                      </div>
                    ) : (
                      <div style={{ marginTop: 6 }}>
                        <Button size="sm" variant="outline" onClick={() => { setResolvingConflictId(conf.parameter); setConflictAuthoritativeId(conf.source_a?.id || ""); }}>
                          <Check style={{ width: 12, height: 12 }} />
                          <span>Resolve Conflict</span>
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Longitudinal Evidence Cards with Provenance & Epistemic Tags */}
          <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="clinova-label">CLINICAL EVIDENCE LEDGER & PROVENANCE</span>
              <span className="clinova-metadata">{evidence_records.length} items logged</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {evidence_records.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    border: "1px solid var(--clinova-border)",
                    borderRadius: "var(--clinova-radius-md)",
                    padding: "10px 12px",
                    backgroundColor: "var(--clinova-surface)",
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <ProvenanceBadge provenance={ev.provenance_type} />
                      <UncertaintyIndicator status={ev.epistemic_status} />
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      {ev.epistemic_status === "REJECTED" ? (
                        <span className="clinova-badge" style={{ backgroundColor: "#fee2e2", color: "#991b1b", borderColor: "#fca5a5" }}>
                          REJECTED
                        </span>
                      ) : ev.verification_status === "CONFIRMED" ? (
                        <EvidenceBadge status="CONFIRMED" verifiedBy={ev.verified_by} />
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleVerifyEvidence(ev.id)}
                        >
                          <CheckCircle2 style={{ width: 12, height: 12 }} aria-hidden="true" />
                          <span>Verify</span>
                        </Button>
                      )}

                      {ev.epistemic_status !== "REJECTED" && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setModifyingEvidenceId(modifyingEvidenceId === ev.id ? null : ev.id);
                              setModifiedValue("");
                              setModifyReason("");
                              setRejectingEvidenceId(null);
                            }}
                          >
                            <Edit3 style={{ width: 12, height: 12 }} aria-hidden="true" />
                            <span>Modify</span>
                          </Button>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setRejectingEvidenceId(rejectingEvidenceId === ev.id ? null : ev.id);
                              setRejectReason("");
                              setModifyingEvidenceId(null);
                            }}
                          >
                            <XCircle style={{ width: 12, height: 12 }} aria-hidden="true" />
                            <span>Reject</span>
                          </Button>
                        </>
                      )}
                    </div>
                  </div>

                  <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)", lineHeight: 1.4 }}>
                    {ev.claim_text}
                  </p>

                  {ev.source_filename && (
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                      <FileScan style={{ width: 11, height: 11 }} aria-hidden="true" />
                      <span>Source Attachment: {ev.source_filename}</span>
                    </div>
                  )}

                  {modifyingEvidenceId === ev.id && (
                    <div style={{ marginTop: 8, padding: 8, background: "var(--clinova-surface-subtle)", borderRadius: 6, border: "1px solid var(--clinova-border)", display: "flex", flexDirection: "column", gap: 6 }}>
                      <strong style={{ fontSize: "0.75rem" }}>Modify Clinical Evidence Observation</strong>
                      <input
                        type="text"
                        className="clinova-input"
                        style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                        placeholder="New updated clinical value..."
                        value={modifiedValue}
                        onChange={(e) => setModifiedValue(e.target.value)}
                      />
                      <input
                        type="text"
                        className="clinova-input"
                        style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                        placeholder="Mandatory clinical rationale for modification..."
                        value={modifyReason}
                        onChange={(e) => setModifyReason(e.target.value)}
                      />
                      <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                        <Button size="sm" variant="outline" onClick={() => setModifyingEvidenceId(null)}>Cancel</Button>
                        <Button size="sm" variant="primary" onClick={() => handleModifyEvidence(ev.id)} disabled={!modifyReason.trim()}>Commit Modification</Button>
                      </div>
                    </div>
                  )}

                  {rejectingEvidenceId === ev.id && (
                    <div style={{ marginTop: 8, padding: 8, background: "#fff1f2", borderRadius: 6, border: "1px solid #fecdd3", display: "flex", flexDirection: "column", gap: 6 }}>
                      <strong style={{ fontSize: "0.75rem", color: "#9f1239" }}>Reject Clinical Evidence Observation</strong>
                      <input
                        type="text"
                        className="clinova-input"
                        style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                        placeholder="Mandatory clinical rationale for rejection (e.g. Artifact, erroneous measurement)..."
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                      />
                      <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                        <Button size="sm" variant="outline" onClick={() => setRejectingEvidenceId(null)}>Cancel</Button>
                        <Button size="sm" variant="primary" onClick={() => handleRejectEvidence(ev.id)} disabled={!rejectReason.trim()}>Commit Rejection</Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Chronological Clinical Timeline */}
          <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-3)" }}>
            <span className="clinova-label">CHRONOLOGICAL CLINICAL TIMELINE</span>
            <Timeline events={timeline} />
          </div>
        </div>

        {/* =========================================================================
            PANEL 3 (RIGHT, 360px): AI Advisory Support, Human Decision Controls,
            Verification Controls, Audit Context
            ========================================================================= */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          {/* Phase 18: Local Clinical AI Advisory Support Panel */}
          <AIAdvisoryPanel
            caseId={caseId}
            initialResults={reviewContext?.ai_advisory_results}
            onNoteDrafted={() => {
              getCaseReviewContext(caseId).then(setReviewContext).catch(() => null);
              getCaseDetails(caseId).then(setData).catch(() => null);
            }}
          />

          {/* Phase 21: Multilingual Translation & Provenance Panel */}
          <MultilingualTranslationPanel
            caseId={caseId}
            sourceComplaint={data?.case?.presenting_complaint}
          />

          {/* AI Advisory Section (Clearly designated as advisory, non-dominant) */}
          <RecommendationCard evaluation={evaluation} />

          {/* Clinician Decision Gate (Physician retains decision authority) */}
          <HumanDecisionCard
            caseId={caseId}
            clinicianName="Dr. Priya Sharma"
            onDecision={handleDecision}
          />

          {/* Clinical Disposition & Encounter Sign-Off (Human-Authorized Lifecycle Gate) */}
          <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8, padding: 12 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="clinova-label">CLINICAL DISPOSITION & SIGN-OFF</span>
              <Lock style={{ width: 14, height: 14, color: "var(--clinova-accent)" }} />
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)", margin: 0 }}>
              Authorized clinician disposition plan. Governs case transition and final destination.
            </p>

            <label style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--clinova-text-muted)", marginTop: 4 }}>
              DISPOSITION ACTION:
            </label>
            <select
              className="clinova-select"
              style={{ fontSize: "0.75rem", padding: "4px 8px" }}
              value={dispositionType}
              onChange={(e) => setDispositionType(e.target.value)}
            >
              <option value="DISCHARGE_HOME">DISCHARGE HOME (Ambulatory follow-up)</option>
              <option value="ADMIT_INPATIENT">ADMIT INPATIENT (Ward / Monitoring)</option>
              <option value="TRANSFER_SPECIALTY">TRANSFER SPECIALTY (Specialized Unit)</option>
              <option value="OBSERVE_AND_REASSESS">OBSERVE & REASSESS (Clinical Decision Unit)</option>
              <option value="REFER_OUT">REFER OUT (External Tertiary Center)</option>
            </select>

            <label style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--clinova-text-muted)" }}>
              CLINICAL SUMMARY (MANDATORY):
            </label>
            <textarea
              className="clinova-textarea"
              style={{ fontSize: "0.75rem", minHeight: 60, padding: "4px 8px" }}
              placeholder="Summary of clinical course, rationale for disposition, and follow-up plan..."
              value={dispositionSummary}
              onChange={(e) => setDispositionSummary(e.target.value)}
            />

            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", cursor: "pointer", marginTop: 2 }}>
              <input
                type="checkbox"
                checked={dispositionCloseCase}
                onChange={(e) => setDispositionCloseCase(e.target.checked)}
              />
              <span>Finalize Disposition & Close Case Encounter</span>
            </label>

            {dispositionFeedback && (
              <p style={{ fontSize: "0.6875rem", color: dispositionFeedback.startsWith("Error") ? "var(--clinova-danger-text)" : "var(--clinova-success-text)", margin: "2px 0" }}>
                {dispositionFeedback}
              </p>
            )}

            <Button
              size="sm"
              variant="primary"
              onClick={handleRecordDisposition}
              disabled={isSubmittingDisposition || !dispositionSummary.trim()}
            >
              <CheckCircle2 style={{ width: 12, height: 12 }} />
              <span>{isSubmittingDisposition ? "Recording..." : "Record Disposition"}</span>
            </Button>

            {/* Direct Encounter Closure Option */}
            <div style={{ borderTop: "1px solid var(--clinova-border)", paddingTop: 8, marginTop: 4 }}>
              {!showCloseForm ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowCloseForm(true)}
                  style={{ width: "100%", justifyContent: "center" }}
                >
                  <Lock style={{ width: 12, height: 12 }} />
                  <span>Close Case Encounter</span>
                </Button>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <strong style={{ fontSize: "0.75rem" }}>Confirm Case Closure</strong>
                  <input
                    type="text"
                    className="clinova-input"
                    style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                    placeholder="Mandatory case closure reason..."
                    value={closeReason}
                    onChange={(e) => setCloseReason(e.target.value)}
                  />
                  {closeFeedback && (
                    <p style={{ fontSize: "0.6875rem", color: closeFeedback.startsWith("Error") ? "var(--clinova-danger-text)" : "var(--clinova-success-text)", margin: "2px 0" }}>
                      {closeFeedback}
                    </p>
                  )}
                  <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                    <Button size="sm" variant="outline" onClick={() => setShowCloseForm(false)}>Cancel</Button>
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={handleCloseEncounter}
                      disabled={isSubmittingClose || !closeReason.trim()}
                    >
                      <span>{isSubmittingClose ? "Closing..." : "Close Case"}</span>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Prior Clinical Decisions & Review Actions (Audit History) */}
          {reviewContext && (
            (reviewContext.prior_decisions && reviewContext.prior_decisions.length > 0) ||
            (reviewContext.prior_review_actions && reviewContext.prior_review_actions.length > 0)
          ) && (
            <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: 8, padding: 12 }}>
              <span className="clinova-label">HUMAN REVIEW & AUDIT HISTORY</span>
              {reviewContext.prior_decisions?.map((dec, di) => (
                <div
                  key={di}
                  style={{
                    padding: "6px 8px",
                    borderRadius: "var(--clinova-radius-md)",
                    backgroundColor: "var(--clinova-surface-subtle)",
                    border: "1px solid var(--clinova-border)",
                    fontSize: "0.75rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ color: "var(--clinova-accent)" }}>
                      {String(dec.decision_type || "DECISION")}
                    </strong>
                    <span className="clinova-mono" style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                      {String(dec.timestamp || "").slice(0, 19)}
                    </span>
                  </div>
                  {Boolean(dec.clinical_rationale) && (
                    <p style={{ margin: "4px 0 0", color: "var(--clinova-text-secondary)" }}>
                      {String(dec.clinical_rationale)}
                    </p>
                  )}
                </div>
              ))}
              {reviewContext.prior_review_actions?.map((act, ai) => (
                <div
                  key={ai}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "0.6875rem",
                    color: "var(--clinova-text-muted)",
                    padding: "2px 0",
                    borderTop: "1px solid var(--clinova-border-subtle)",
                  }}
                >
                  <span>Action: <strong>{String(act.action)}</strong> ({String(act.target_entity_type)})</span>
                  <span className="clinova-mono">{String(act.created_at || "").slice(11, 19)}</span>
                </div>
              ))}
            </div>
          )}

          {/* Quick Inter-Facility Referral Dispatch Link */}
          <div
            className="clinova-card"
            style={{
              padding: 12,
              backgroundColor: "var(--clinova-surface-subtle)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div>
              <strong style={{ fontSize: "0.8125rem" }}>Inter-Facility Coordination</strong>
              <p style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                Generate SBAR handoff & feasibility
              </p>
            </div>
            <Link href="/referrals" className="clinova-btn clinova-btn-secondary clinova-btn-sm" style={{ textDecoration: "none" }}>
              <Share2 style={{ width: 12, height: 12 }} aria-hidden="true" />
              <span>Referrals</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
    </RoleGuard>
  );
};
