"use client";

import React, { useState, useEffect } from "react";
import {
  Cpu,
  ShieldCheck,
  CheckCircle2,
  AlertOctagon,
  ArrowRight,
  TrendingUp,
  FileCheck2,
  Lock,
  RefreshCw,
  LogOut,
  Send,
} from "lucide-react";
import { OrchestrationEvaluation, Persona } from "@/types";
import {
  evaluateOrchestration,
  submitClinicianDecision,
  closeCaseOutcome,
  getCurrentUser,
} from "@/lib/api";

interface OrchestrationTabProps {
  caseId: string | null;
  facilityId: string;
  onOutcomeLogged: () => void;
}

export const OrchestrationTab: React.FC<OrchestrationTabProps> = ({
  caseId,
  facilityId,
  onOutcomeLogged,
}) => {
  const [evaluation, setEvaluation] = useState<OrchestrationEvaluation | null>(null);
  const [currentUser, setCurrentUser] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(false);

  // Clinician decision form state
  const [chosenAction, setChosenAction] = useState<string>("CONTINUE");
  const [decisionType, setDecisionType] = useState<"ACCEPT" | "OVERRIDE">("ACCEPT");
  const [overrideReason, setOverrideReason] = useState("");
  const [notes, setNotes] = useState("");
  const [submittingDecision, setSubmittingDecision] = useState(false);
  const [decisionFeedback, setDecisionFeedback] = useState<string | null>(null);

  // Outcome closure state
  const [disposition, setDisposition] = useState("DISCHARGED_ROUTINE");
  const [finalCondition, setFinalCondition] = useState("STABLE");
  const [outcomeNotes, setOutcomeNotes] = useState("Patient completed treatment and discharged home in stable condition.");
  const [submittingOutcome, setSubmittingOutcome] = useState(false);
  const [outcomeFeedback, setOutcomeFeedback] = useState<string | null>(null);

  const loadData = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);

      const res = await evaluateOrchestration(caseId, facilityId);
      setEvaluation(res);
      setChosenAction(res.recommended_action);
    } catch (err) {
      console.error("Failed to evaluate orchestration:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [caseId, facilityId]);

  const handleAuthorizeDecision = async () => {
    if (!caseId || !currentUser) return;
    if (decisionType === "OVERRIDE" && (!overrideReason || !overrideReason.trim())) {
      alert("A mandatory clinical justification reason is required when overriding AI advisory guidance.");
      return;
    }
    setSubmittingDecision(true);
    setDecisionFeedback(null);
    try {
      const res = await submitClinicianDecision({
        case_id: caseId,
        action: chosenAction,
        decision_type: decisionType,
        clinician_id: currentUser.id,
        override_reason: decisionType === "OVERRIDE" ? overrideReason : undefined,
        notes: notes,
      });
      setDecisionFeedback(
        `Action ${res.action_authorized} authorized! Case status updated to ${res.case_status}.`
      );
    } catch (e: any) {
      alert("Failed to record clinician decision: " + e.message);
    } finally {
      setSubmittingDecision(false);
    }
  };

  const handleCloseOutcome = async () => {
    if (!caseId || !currentUser) return;
    setSubmittingOutcome(true);
    setOutcomeFeedback(null);
    try {
      const res = await closeCaseOutcome(caseId, {
        disposition: disposition,
        final_condition: finalCondition,
        notes: outcomeNotes,
        actor_id: currentUser.id,
      });
      setOutcomeFeedback(`Encounter closed successfully! Outcome logged: ${res.disposition}.`);
      onOutcomeLogged();
    } catch (e: any) {
      alert("Failed to close outcome: " + e.message);
    } finally {
      setSubmittingOutcome(false);
    }
  };

  if (!caseId) {
    return (
      <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-500 text-xs">
        Please select a case to run the Orchestration Cognitive Synthesis engine.
      </div>
    );
  }

  if (loading && !evaluation) {
    return (
      <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-500 text-xs flex items-center justify-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-teal-600" />
        Synthesizing Patient Risk, Uncertainty, Facility Feasibility & System Context...
      </div>
    );
  }

  if (!evaluation) return null;

  const getActionColor = (action: string) => {
    switch (action) {
      case "ESCALATE":
        return "bg-rose-600 text-white border-rose-700";
      case "REFER":
        return "bg-amber-600 text-white border-amber-700";
      case "OBSERVE":
        return "bg-blue-600 text-white border-blue-700";
      case "VERIFY":
        return "bg-purple-600 text-white border-purple-700";
      case "ASK":
        return "bg-yellow-500 text-slate-950 border-yellow-600";
      default:
        return "bg-emerald-600 text-white border-emerald-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-600" />
            ORCHESTRATION ENGINE — Cognitive Synthesis Core
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            CareGraph + Evidence Uncertainty + FacilityGraph Feasibility + System Context ➔ Safest Achievable Care Pathway.
          </p>
        </div>
        <div className="text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Active Reviewer: <strong>{currentUser?.full_name}</strong> ({currentUser?.role})</span>
        </div>
      </div>

      {/* Advisory Recommendation Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              ADVISORY RECOMMENDATION
            </span>
            <div className="flex items-center gap-3 mt-1">
              <span
                className={`text-sm font-extrabold px-3 py-1 rounded-lg border shadow-xs ${getActionColor(
                  evaluation.recommended_action
                )}`}
              >
                ACTION: {evaluation.recommended_action}
              </span>
              <span className="text-xs font-bold text-slate-500">
                Priority: {evaluation.priority_level}
              </span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 max-w-xs text-left sm:text-right">
            <span>Secondary Backup Pathway:</span>
            <span className="font-bold text-slate-900 block font-mono">
              {evaluation.secondary_pathway}
            </span>
          </div>
        </div>

        {/* Clinical Directive & Rationale */}
        <div className="space-y-3">
          <div className="p-4 rounded-xl bg-teal-50/50 border border-teal-200 space-y-1">
            <span className="text-xs font-bold text-teal-900 block">Immediate Clinical Directive</span>
            <p className="text-xs text-teal-800 leading-relaxed font-medium">
              {evaluation.clinical_directive}
            </p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1 text-xs">
            <span className="font-bold text-slate-700 block">Algorithmic Rationale</span>
            <p className="text-slate-600 leading-relaxed">{evaluation.clinical_rationale}</p>
          </div>
        </div>

        {/* Inputs Considered Check Matrix */}
        <div className="border-t border-slate-100 pt-4">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            Inputs Evaluated in Synthesis
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 text-center text-xs">
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Risk (R_t)</span>
              <span className="font-mono font-bold text-slate-900">
                {evaluation.inputs_considered.risk_score.toFixed(2)}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Trajectory</span>
              <span className="font-mono font-bold text-slate-900">
                {evaluation.inputs_considered.trajectory_slope > 0 ? `+${evaluation.inputs_considered.trajectory_slope}` : evaluation.inputs_considered.trajectory_slope}/h
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Uncertainty</span>
              <span className="font-mono font-bold text-slate-900">
                {evaluation.inputs_considered.uncertainty_score.toFixed(2)}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Feasibility</span>
              <span className="font-bold text-slate-900 text-[11px]">
                {evaluation.inputs_considered.feasibility_status}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Conflicts</span>
              <span className="font-mono font-bold text-slate-900">
                {evaluation.inputs_considered.conflicts_count}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Missing Gaps</span>
              <span className="font-mono font-bold text-slate-900">
                {evaluation.inputs_considered.missing_parameters_count}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-400 block">Acuity Tier</span>
              <span className="font-bold text-slate-900 text-[11px]">
                {evaluation.inputs_considered.acuity_tier}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Qualified Clinician Review Gate & Decision Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Col: Clinician Sign-Off Gate */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Lock className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Qualified Clinician Review Gate (Mandatory Human Sign-Off)
            </h3>
          </div>
          <p className="text-[11px] text-slate-500">
            AI recommendations remain strictly advisory. The qualified clinician must sign off or enter structured justification to override.
          </p>

          <div className="space-y-3 text-xs">
            {/* Decision Type */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Decision Mode</label>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="decisionType"
                    value="ACCEPT"
                    checked={decisionType === "ACCEPT"}
                    onChange={() => setDecisionType("ACCEPT")}
                  />
                  <span>Accept Advisory Guidance</span>
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="decisionType"
                    value="OVERRIDE"
                    checked={decisionType === "OVERRIDE"}
                    onChange={() => setDecisionType("OVERRIDE")}
                  />
                  <span className="text-rose-700 font-bold">Override Guidance</span>
                </label>
              </div>
            </div>

            {/* Action Selector */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Authorized Next Action</label>
              <select
                value={chosenAction}
                onChange={(e) => setChosenAction(e.target.value)}
                className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="CONTINUE">CONTINUE — Standard Ambulatory Care</option>
                <option value="OBSERVE">OBSERVE — Holding Bed with Serial Trajectory Vitals</option>
                <option value="ESCALATE">ESCALATE — Immediate Bedside Resuscitation</option>
                <option value="REFER">REFER — Inter-Facility Emergency Transfer</option>
                <option value="ASK">ASK — Resolve Protocol Information Gaps</option>
                <option value="VERIFY">VERIFY — Reconcile Contradictory Clinical Data</option>
              </select>
            </div>

            {/* Mandatory Override Justification when OVERRIDE is chosen */}
            {decisionType === "OVERRIDE" && (
              <div className="space-y-1">
                <label className="font-bold text-rose-700 block">
                  Mandatory Clinician Override Justification *
                </label>
                <textarea
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="State clinical reasoning for departing from advisory guidance (e.g. bedside peritonitis, clinical deterioration)..."
                  className="w-full text-xs p-2.5 rounded-lg border border-rose-300 bg-rose-50/30 focus:ring-2 focus:ring-rose-500"
                />
              </div>
            )}

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Clinical Notes</label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Optional notes for encounter chart..."
                className="w-full text-xs p-2 rounded-lg border border-slate-300"
              />
            </div>

            <button
              onClick={handleAuthorizeDecision}
              disabled={submittingDecision}
              className="w-full py-2.5 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-xs transition-colors"
            >
              <ShieldCheck className="w-4 h-4" />
              {submittingDecision ? "Authorizing..." : "Authorize Decision as Qualified Clinician"}
            </button>

            {decisionFeedback && (
              <div className="p-2.5 rounded-lg bg-teal-50 border border-teal-200 text-xs font-semibold text-teal-900">
                {decisionFeedback}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Encounter Outcome Loop (Discharge / Finalize) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <LogOut className="w-4 h-4 text-purple-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Encounter Outcome Loop (Closing Care Cycle)
            </h3>
          </div>
          <p className="text-[11px] text-slate-500">
            Records final patient disposition, closes encounter state machine (OUTCOME), and routes de-identified telemetry to SignalGraph.
          </p>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Final Disposition</label>
              <select
                value={disposition}
                onChange={(e) => setDisposition(e.target.value)}
                className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="DISCHARGED_ROUTINE">Discharged Routine (Home)</option>
                <option value="OBSERVATION_RESOLVED">Observation Resolved (Discharged)</option>
                <option value="ADMITTED_INPATIENT">Admitted to Inpatient Ward / ICU</option>
                <option value="TRANSFERRED_OUT">Transferred Out to Network Center</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Final Condition</label>
              <select
                value={finalCondition}
                onChange={(e) => setFinalCondition(e.target.value)}
                className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
              >
                <option value="STABLE">Stable / Normal</option>
                <option value="IMPROVED">Improved following treatment</option>
                <option value="REFERRED">Referred in transit</option>
                <option value="CRITICAL">Critical (Inpatient care required)</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Discharge Notes</label>
              <textarea
                rows={2}
                value={outcomeNotes}
                onChange={(e) => setOutcomeNotes(e.target.value)}
                className="w-full text-xs p-2 rounded-lg border border-slate-300"
              />
            </div>

            <button
              onClick={handleCloseOutcome}
              disabled={submittingOutcome}
              className="w-full py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-xs transition-colors"
            >
              <CheckCircle2 className="w-4 h-4" />
              {submittingOutcome ? "Closing Encounter..." : "Log Patient Outcome & Close Loop"}
            </button>

            {outcomeFeedback && (
              <div className="p-2.5 rounded-lg bg-purple-50 border border-purple-200 text-xs font-semibold text-purple-900">
                {outcomeFeedback}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
