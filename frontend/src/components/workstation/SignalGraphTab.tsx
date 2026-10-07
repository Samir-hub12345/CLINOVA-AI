"use client";

import React, { useState, useEffect } from "react";
import {
  Radio,
  AlertTriangle,
  Activity,
  ShieldCheck,
  TrendingUp,
  RefreshCw,
  PlusCircle,
  Building2,
  Clock,
  Layers,
} from "lucide-react";
import { SignalSummary, SyndromicCluster } from "@/types";
import { getSignalSummary, injectSignalEvent } from "@/lib/api";

export const SignalGraphTab: React.FC = () => {
  const [summary, setSummary] = useState<SignalSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [injecting, setInjecting] = useState(false);

  const loadSignalData = async () => {
    setLoading(true);
    try {
      const data = await getSignalSummary();
      setSummary(data);
    } catch (err) {
      console.error("Failed to load SignalGraph:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSignalData();
    const interval = setInterval(loadSignalData, 10000); // 10s auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleSimulateSurge = async () => {
    setInjecting(true);
    try {
      // Inject 3 hemorrhagic fever events
      for (let i = 0; i < 3; i++) {
        await injectSignalEvent({
          facility_id: "FAC-DH-04",
          syndrome_tag: "SYNDROME_HEMORRHAGIC_FEVER",
          acuity_tier: "URGENT",
        });
      }
      await loadSignalData();
    } catch (e: any) {
      alert("Failed to inject event: " + e.message);
    } finally {
      setInjecting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Persistent Synthetic Telemetry Header (Mandatory DOC-10) */}
      <div className="bg-purple-950 text-purple-100 p-5 rounded-xl border border-purple-800 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-bold text-sm text-purple-300">
            <Radio className="w-4 h-4 text-purple-400 animate-pulse" />
            <span>[SYNTHETIC TELEMETRY MODE ACTIVE]</span>
          </div>
          <p className="text-xs text-purple-200">
            SIGNALGRAPH monitors regional outbreak surges and department queue bottlenecks.
            All statistics derive dynamically from prototype and synthetic clinical events. Zero real-world PHI.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSimulateSurge}
            disabled={injecting}
            className="text-xs px-3.5 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold flex items-center gap-1.5 transition-colors shadow-xs"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            {injecting ? "Injecting..." : "Simulate Dengue Surge (+3 Cases)"}
          </button>
          <button
            onClick={loadSignalData}
            disabled={loading}
            className="text-xs p-2 rounded-lg bg-purple-900 border border-purple-700 hover:bg-purple-800 text-purple-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Macro System Telemetry Counters */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              Outbreak Alert Level
            </span>
            <div
              className={`text-xl font-black font-mono ${
                summary.overall_epidemiological_alert === "CRITICAL"
                  ? "text-rose-600"
                  : summary.overall_epidemiological_alert === "WARNING"
                  ? "text-amber-600"
                  : "text-emerald-700"
              }`}
            >
              {summary.overall_epidemiological_alert}
            </div>
            <p className="text-[10px] text-slate-500">Based on multi-catchment Z-scores</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              Network ICU Utilization
            </span>
            <div className="text-xl font-black font-mono text-slate-900">
              {summary.network_icu_occupancy_pct}%
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
              <div
                className={`h-1.5 rounded-full ${
                  summary.network_icu_occupancy_pct > 85 ? "bg-rose-500" : "bg-teal-500"
                }`}
                style={{ width: `${Math.min(100, summary.network_icu_occupancy_pct)}%` }}
              />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              Total Active ED Queue
            </span>
            <div className="text-xl font-black font-mono text-slate-900">
              {summary.total_ed_waiting} Patients
            </div>
            <p className="text-[10px] text-slate-500">Across 5 regional network nodes</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
              Signal Events Logged
            </span>
            <div className="text-xl font-black font-mono text-slate-900">
              {summary.active_events_logged}
            </div>
            <p className="text-[10px] text-slate-500">Immutable event stream</p>
          </div>
        </div>
      )}

      {/* Regional Syndromic Clusters (Z-Score Outbreak Detector) */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-purple-600" />
              Regional Syndromic Outbreak Cluster Detection (Rolling 48h)
            </h3>
            <p className="text-[11px] text-slate-500">
              Z = (C_observed - μ_baseline) / σ_baseline. Triggers warning at Z ≥ 2.5 and emergency surge alarm at Z ≥ 3.5.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {summary?.active_clusters?.map((cluster) => (
            <div
              key={cluster.syndrome}
              className={`p-4 rounded-xl border transition-all ${
                cluster.alert_class === "CRITICAL"
                  ? "bg-rose-50/50 border-rose-300 shadow-xs"
                  : cluster.alert_class === "WARNING"
                  ? "bg-amber-50/50 border-amber-300"
                  : "bg-slate-50 border-slate-200"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                    cluster.alert_class === "CRITICAL"
                      ? "bg-rose-600 text-white"
                      : cluster.alert_class === "WARNING"
                      ? "bg-amber-600 text-white"
                      : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {cluster.status}
                </span>
                <span className="font-mono font-bold text-xs text-slate-500">
                  Z = {cluster.z_score >= 0 ? `+${cluster.z_score}` : cluster.z_score}
                </span>
              </div>
              <h4 className="font-bold text-slate-900 text-xs">{cluster.syndrome.replace("SYNDROME_", "")}</h4>
              <div className="mt-2 text-[11px] text-slate-600 space-y-0.5">
                <div>
                  Observed Cases (48h): <strong>{cluster.observed_cases_48h}</strong>
                </div>
                <div>
                  Baseline Mean (μ): <strong>{cluster.baseline_mean}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
