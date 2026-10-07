"use client";

import React, { useState, useEffect } from "react";
import {
  ListFilter,
  Search,
  Clock,
  AlertCircle,
  Activity,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Layers,
} from "lucide-react";
import { QueueItem } from "@/types";
import { getClinicalQueue } from "@/lib/api";

interface QueueTabProps {
  onSelectCase: (caseId: string) => void;
}

export const QueueTab: React.FC<QueueTabProps> = ({ onSelectCase }) => {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAcuity, setFilterAcuity] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const loadQueue = async () => {
    setLoading(true);
    try {
      const data = await getClinicalQueue();
      setQueue(data.queue || []);
    } catch (err) {
      console.error("Failed to load queue:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 15000); // 15s polling
    return () => clearInterval(interval);
  }, []);

  const filtered = queue.filter((item) => {
    if (filterAcuity !== "ALL" && item.acuity_tier !== filterAcuity) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchPt = item.patient_synthetic_id.toLowerCase().includes(q);
      const matchCase = item.case_number.toLowerCase().includes(q);
      const matchComplaint = item.presenting_complaint.toLowerCase().includes(q);
      return matchPt || matchCase || matchComplaint;
    }
    return true;
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "CRITICAL":
        return "bg-rose-100 text-rose-800 border-rose-300";
      case "URGENT":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "MODERATE":
        return "bg-blue-100 text-blue-800 border-blue-300";
      default:
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-600" />
            Clinical Triage Queue & Acuity Priority
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time waiting queue prioritized strictly by Risk Score (R_t), Trajectory (Delta R), and SLA limit.
          </p>
        </div>
        <button
          onClick={loadQueue}
          disabled={loading}
          className="text-xs px-3.5 py-2 rounded-lg border border-slate-300 bg-slate-50 hover:bg-slate-100 font-semibold text-slate-700 flex items-center gap-2 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh Queue
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "CRITICAL", "URGENT", "MODERATE", "ROUTINE"].map((tier) => (
            <button
              key={tier}
              onClick={() => setFilterAcuity(tier)}
              className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all ${
                filterAcuity === tier
                  ? "bg-slate-900 text-white"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search synthetic ID, case..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-8 pr-3 py-1.5 rounded-lg border border-slate-300 bg-white"
          />
        </div>
      </div>

      {/* Queue List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="bg-white p-12 text-center rounded-xl border border-slate-200 text-slate-500 text-xs">
            No clinical cases found matching filter criteria. Create a case via Multimodal Intake.
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.case_id}
              className={`bg-white p-5 rounded-xl border transition-all hover:shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                item.acuity_tier === "CRITICAL"
                  ? "border-rose-300 bg-rose-50/15"
                  : "border-slate-200 hover:border-teal-300"
              }`}
            >
              {/* Left Column: Acuity & Identifiers */}
              <div className="space-y-1.5 max-w-md">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${getTierColor(
                      item.acuity_tier
                    )}`}
                  >
                    {item.acuity_tier}
                  </span>
                  <span className="font-mono font-bold text-xs text-slate-900">
                    {item.case_number}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    ({item.patient_synthetic_id} • {item.age_bracket})
                  </span>
                </div>
                <p className="text-xs text-slate-700 font-medium line-clamp-2">
                  {item.presenting_complaint}
                </p>
                <div className="flex items-center gap-2 text-[11px] text-slate-500">
                  <span>Facility: {item.facility_name}</span>
                  <span>•</span>
                  <span>Status: <code className="text-teal-800 font-semibold">{item.status}</code></span>
                </div>
              </div>

              {/* Middle Column: Acuity Scores & Vitals */}
              <div className="flex flex-wrap items-center gap-4 text-xs">
                <div className="text-center p-2 rounded-lg bg-slate-50 border border-slate-200 min-w-20">
                  <span className="text-[10px] text-slate-400 block font-semibold">Risk (R_t)</span>
                  <span
                    className={`font-mono font-bold text-sm ${
                      item.risk_score >= 0.7
                        ? "text-rose-600"
                        : item.risk_score >= 0.4
                        ? "text-amber-600"
                        : "text-slate-800"
                    }`}
                  >
                    {item.risk_score.toFixed(2)}
                  </span>
                </div>

                <div className="text-center p-2 rounded-lg bg-slate-50 border border-slate-200 min-w-20">
                  <span className="text-[10px] text-slate-400 block font-semibold">Trajectory</span>
                  <span
                    className={`font-mono font-bold text-sm flex items-center justify-center gap-0.5 ${
                      item.trajectory_slope >= 1.5 ? "text-rose-600" : "text-slate-800"
                    }`}
                  >
                    {item.trajectory_slope > 0 ? `+${item.trajectory_slope}` : item.trajectory_slope}/hr
                  </span>
                </div>

                {/* SLA Timer */}
                <div
                  className={`p-2 rounded-lg border text-center min-w-24 ${
                    item.sla_breached
                      ? "bg-rose-50 border-rose-200 text-rose-800"
                      : "bg-slate-50 border-slate-200 text-slate-700"
                  }`}
                >
                  <span className="text-[10px] block font-semibold flex items-center justify-center gap-1">
                    <Clock className="w-3 h-3" />
                    Wait / SLA
                  </span>
                  <span className="font-mono font-bold text-sm">
                    {item.waiting_minutes}m / {item.sla_limit_minutes}m
                  </span>
                </div>
              </div>

              {/* Right Column: CTA */}
              <div className="flex items-center gap-2 self-end md:self-center">
                <button
                  onClick={() => onSelectCase(item.case_id)}
                  className="text-xs px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold flex items-center gap-1.5 shadow-xs transition-colors"
                >
                  <Layers className="w-3.5 h-3.5" />
                  Open CareGraph
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
