"use client";

import React, { useState, useEffect } from "react";
import {
  Layers,
  Activity,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  HelpCircle,
  ShieldCheck,
  PlusCircle,
  FileText,
  Mic,
  FileSpreadsheet,
  Cpu,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import { CareGraphData } from "@/types";
import { getCareGraph, appendVitals, verifyEvidence } from "@/lib/api";

interface CareGraphTabProps {
  caseId: string | null;
  onNavigateToFacility: () => void;
  onNavigateToOrchestration: () => void;
}

export const CareGraphTab: React.FC<CareGraphTabProps> = ({
  caseId,
  onNavigateToFacility,
  onNavigateToOrchestration,
}) => {
  const [data, setData] = useState<CareGraphData | null>(null);
  const [loading, setLoading] = useState(false);

  // Serial vitals form state
  const [hr, setHr] = useState<number>(120);
  const [sysBp, setSysBp] = useState<number>(95);
  const [diaBp, setDiaBp] = useState<number>(60);
  const [spo2, setSpo2] = useState<number>(91);
  const [rr, setRr] = useState<number>(26);
  const [temp, setTemp] = useState<number>(38.8);
  const [avpu, setAvpu] = useState("ALERT");
  const [vitalsLoading, setVitalsLoading] = useState(false);
  const [verifyLoading, setVerifyLoading] = useState(false);

  const loadCareGraph = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const res = await getCareGraph(caseId);
      setData(res);
    } catch (err) {
      console.error("Failed to load CareGraph:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCareGraph();
  }, [caseId]);

  const handleAppendVitals = async () => {
    if (!caseId) return;
    setVitalsLoading(true);
    try {
      await appendVitals(caseId, {
        heart_rate: hr,
        systolic_bp: sysBp,
        diastolic_bp: diaBp,
        spo2_percent: spo2,
        respiratory_rate: rr,
        temperature_celsius: temp,
        avpu_score: avpu,
      });
      await loadCareGraph();
    } catch (e: any) {
      alert("Failed to append vitals: " + e.message);
    } finally {
      setVitalsLoading(false);
    }
  };

  const handleVerifyEvidence = async (evidenceId: string) => {
    if (!caseId) return;
    setVerifyLoading(true);
    try {
      await verifyEvidence(caseId, {
        evidence_id: evidenceId,
        verification_status: "CONFIRMED",
        clinician_id: "usr-doc-01",
        notes: "Verified on bedside clinical evaluation.",
      });
      await loadCareGraph();
    } catch (e: any) {
      alert("Failed to verify evidence: " + e.message);
    } finally {
      setVerifyLoading(false);
    }
  };

  if (!caseId) {
    return (
      <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-500 text-xs">
        Please select a case from the Clinical Queue or create a new intake to inspect CareGraph.
      </div>
    );
  }

  if (loading && !data) {
    return (
      <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-500 text-xs flex items-center justify-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-teal-600" />
        Loading CareGraph Knowledge Topology...
      </div>
    );
  }

  if (!data) return null;

  const { case: c, trajectory, uncertainty, graph, evidence_records, vitals_history } = data;

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span
              className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                c.acuity_tier === "CRITICAL"
                  ? "bg-rose-100 text-rose-800 border-rose-300"
                  : c.acuity_tier === "URGENT"
                  ? "bg-amber-100 text-amber-800 border-amber-300"
                  : "bg-emerald-100 text-emerald-800 border-emerald-300"
              }`}
            >
              {c.acuity_tier}
            </span>
            <h2 className="text-xl font-bold text-slate-900 font-mono">{c.case_number}</h2>
            <span className="text-xs text-slate-500 font-mono">
              ({c.patient_synthetic_id} • {c.age_bracket} • {c.biological_sex})
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            <strong>Syndrome:</strong> {c.primary_syndrome || "General"} |{" "}
            <strong>Required Bundle:</strong> {c.required_bundle || "Routine Ambulatory"}
          </p>
        </div>

        {/* Acuity Metrics Strip */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center min-w-24">
            <span className="text-[10px] text-slate-400 block font-semibold">Risk Score (R_t)</span>
            <span
              className={`font-mono font-bold text-base ${
                c.risk_score >= 0.7 ? "text-rose-600" : c.risk_score >= 0.4 ? "text-amber-600" : "text-emerald-700"
              }`}
            >
              {c.risk_score.toFixed(2)}
            </span>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center min-w-28">
            <span className="text-[10px] text-slate-400 block font-semibold">Trajectory Slope</span>
            <span
              className={`font-mono font-bold text-base ${
                trajectory.slope >= 1.5 ? "text-rose-600" : "text-slate-800"
              }`}
            >
              {trajectory.slope > 0 ? `+${trajectory.slope}` : trajectory.slope}/hr
            </span>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center min-w-24">
            <span className="text-[10px] text-slate-400 block font-semibold">Uncertainty (U_t)</span>
            <span
              className={`font-mono font-bold text-base ${
                uncertainty.uncertainty_score > 0.4 ? "text-amber-600" : "text-emerald-700"
              }`}
            >
              {uncertainty.uncertainty_score.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Contradiction & Red Flag Warning */}
      {uncertainty.conflicts.length > 0 && (
        <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/70 text-rose-900 space-y-1">
          <div className="flex items-center gap-2 font-bold text-xs text-rose-800">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            Contradictory Clinical Findings Detected (VERIFY Gate Active)
          </div>
          {uncertainty.conflicts.map((conf, idx) => (
            <p key={idx} className="text-xs pl-6 text-rose-700">
              • {conf.message}
            </p>
          ))}
        </div>
      )}

      {/* Main Grid: Interactive Graph vs Trajectory/Uncertainty */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Graph Topology Canvas */}
        <div className="lg:col-span-2 space-y-6">
          {/* Visual Graph Nodes Canvas */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-teal-600" />
                  CareGraph Topological Node View
                </h3>
                <p className="text-[11px] text-slate-500">
                  Directed multi-attribute graph modeling active clinical state, evidence, and trajectory.
                </p>
              </div>
              <span className="text-[11px] font-semibold text-slate-400">
                {graph.total_nodes} Nodes • {graph.total_edges} Directed Edges
              </span>
            </div>

            {/* Simulated Visual Graph Network */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {graph.nodes.map((node) => (
                <div
                  key={node.id}
                  className={`p-3.5 rounded-lg border text-xs space-y-2 transition-all ${
                    node.type === "PATIENT_PROFILE"
                      ? "border-teal-200 bg-teal-50/30"
                      : node.type === "VITAL_SIGN"
                      ? "border-blue-200 bg-blue-50/30"
                      : node.type === "EVIDENCE"
                      ? "border-purple-200 bg-purple-50/30"
                      : node.type === "CLINICAL_DECISION"
                      ? "border-emerald-200 bg-emerald-50/30"
                      : "border-slate-200 bg-slate-50/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      {node.type.replace("_", " ")}
                    </span>
                    <span
                      className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                        node.status === "CONFIRMED"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {node.status}
                    </span>
                  </div>
                  <div className="font-bold text-slate-900 text-xs">{node.label}</div>
                  <div className="text-[10px] text-slate-600 font-mono bg-white/80 p-1.5 rounded border border-slate-200/60 truncate">
                    {JSON.stringify(node.data)}
                  </div>
                  <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-100">
                    <span>Provenance:</span>
                    <span className="font-semibold text-teal-700">{node.provenance}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dynamic Serial Vitals Injector */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <PlusCircle className="w-4 h-4 text-teal-600" />
                  Append Serial Vitals (Test Trajectory Shift & Delta R)
                </h3>
                <p className="text-[11px] text-slate-500">
                  Inject serial bedside vitals to observe dynamic NEWS2 calculation and trajectory slope shift.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">HR (bpm)</label>
                <input
                  type="number"
                  value={hr}
                  onChange={(e) => setHr(parseInt(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">Sys BP (mmHg)</label>
                <input
                  type="number"
                  value={sysBp}
                  onChange={(e) => setSysBp(parseInt(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">Dia BP (mmHg)</label>
                <input
                  type="number"
                  value={diaBp}
                  onChange={(e) => setDiaBp(parseInt(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">SpO2 (%)</label>
                <input
                  type="number"
                  value={spo2}
                  onChange={(e) => setSpo2(parseInt(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">RR (/min)</label>
                <input
                  type="number"
                  value={rr}
                  onChange={(e) => setRr(parseInt(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 block">Temp (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  value={temp}
                  onChange={(e) => setTemp(parseFloat(e.target.value) || 0)}
                  className="w-full text-xs p-2 rounded border border-slate-300"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-400">
                Logged Vitals Count: <strong>{vitals_history.length}</strong>
              </span>
              <button
                onClick={handleAppendVitals}
                disabled={vitalsLoading}
                className="text-xs px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold flex items-center gap-1.5 shadow-xs transition-colors"
              >
                <Activity className="w-3.5 h-3.5" />
                {vitalsLoading ? "Recalculating..." : "Append & Compute Trajectory"}
              </button>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Uncertainty, Missing Items & Evidence Verification */}
        <div className="space-y-6">
          {/* Uncertainty & Protocol Gaps Card */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-amber-600" />
              Evidence Uncertainty & Protocol Gaps
            </h3>
            <p className="text-[11px] text-slate-500">
              Formulated as: U_t = 1.0 - (0.40 C_data + 0.35 Q_evidence + 0.25 V_clinician)
            </p>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                <span className="text-slate-600">Protocol Completeness (C_data)</span>
                <span className="font-mono font-bold text-slate-900">
                  {(uncertainty.protocol_completeness * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                <span className="text-slate-600">Evidence Quality (Q_evidence)</span>
                <span className="font-mono font-bold text-slate-900">
                  {(uncertainty.evidence_quality * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                <span className="text-slate-600">Clinician Verification (V_clinician)</span>
                <span className="font-mono font-bold text-slate-900">
                  {(uncertainty.clinician_verification_ratio * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Missing Protocol Chips */}
            {uncertainty.missing_parameters.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Missing Protocol Parameters
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {uncertainty.missing_parameters.map((param) => (
                    <span
                      key={param}
                      className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200"
                    >
                      {param.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Follow-up Questions */}
            {uncertainty.follow_up_questions.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Targeted Follow-Up Questions (ASK Action)
                </span>
                <div className="space-y-1.5">
                  {uncertainty.follow_up_questions.slice(0, 3).map((q, idx) => (
                    <div key={idx} className="p-2 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-700">
                      <strong>Q:</strong> {q.question}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Evidence Records & Clinician Verification */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              Evidence Provenance & Clinician Gate
            </h3>
            <div className="space-y-2.5">
              {evidence_records.map((ev) => (
                <div key={ev.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{ev.provenance_type}</span>
                    <span
                      className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                        ev.verification_status === "CONFIRMED"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {ev.verification_status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 font-mono truncate">
                    Source: {ev.source_filename || "N/A"} (Conf: {(ev.confidence_score * 100).toFixed(0)}%)
                  </p>
                  {ev.verification_status !== "CONFIRMED" && (
                    <button
                      onClick={() => handleVerifyEvidence(ev.id)}
                      disabled={verifyLoading}
                      className="w-full text-xs py-1 rounded bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 font-bold transition-colors"
                    >
                      Clinician Verify Node
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Navigation to next stages */}
          <div className="space-y-2">
            <button
              onClick={onNavigateToFacility}
              className="w-full text-xs py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold flex items-center justify-center gap-2"
            >
              Check Care Feasibility (FacilityGraph)
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onNavigateToOrchestration}
              className="w-full text-xs py-2.5 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold flex items-center justify-center gap-2"
            >
              Evaluate Safest Action (Orchestration)
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
