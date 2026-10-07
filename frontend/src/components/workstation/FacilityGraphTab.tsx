"use client";

import React, { useState, useEffect } from "react";
import {
  Building2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Truck,
  FileCheck2,
  ToggleLeft,
  ToggleRight,
  Clock,
  ArrowRight,
  RefreshCw,
  Send,
} from "lucide-react";
import { Facility, FeasibilityResult, ReferralOption, SbarPacket } from "@/types";
import {
  getFacilities,
  checkFeasibility,
  rankReferrals,
  toggleCapability,
  generateSbar,
} from "@/lib/api";

interface FacilityGraphTabProps {
  caseId: string | null;
  facilityId: string;
  requiredBundle: string;
  onNavigateToOrchestration: () => void;
}

export const FacilityGraphTab: React.FC<FacilityGraphTabProps> = ({
  caseId,
  facilityId,
  requiredBundle = "BUNDLE_STROKE_ACUTE",
  onNavigateToOrchestration,
}) => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedFacId, setSelectedFacId] = useState(facilityId || "FAC-PHC-01");
  const [bundle, setBundle] = useState(requiredBundle || "BUNDLE_STROKE_ACUTE");
  const [feasibility, setFeasibility] = useState<FeasibilityResult | null>(null);
  const [rankedReferrals, setRankedReferrals] = useState<ReferralOption[]>([]);
  const [sbarPacket, setSbarPacket] = useState<SbarPacket | null>(null);
  const [loading, setLoading] = useState(false);
  const [sbarLoading, setSbarLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const facs = await getFacilities();
      setFacilities(facs);

      // Check feasibility for current facility
      const feasRes = await checkFeasibility(selectedFacId, bundle);
      setFeasibility(feasRes.feasibility);

      // Rank network referrals
      const rankRes = await rankReferrals(selectedFacId, bundle);
      setRankedReferrals(rankRes.ranked_destinations || []);
    } catch (err) {
      console.error("Failed to load FacilityGraph:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedFacId, bundle]);

  const handleToggleCap = async (facId: string, capCode: string, currentStatus: boolean) => {
    try {
      await toggleCapability(facId, capCode, !currentStatus);
      await loadData();
    } catch (e: any) {
      alert("Failed to toggle capability: " + e.message);
    }
  };

  const handleGenerateSbar = async (destinationFacId: string) => {
    if (!caseId) {
      alert("Please select an active clinical case to generate an SBAR packet.");
      return;
    }
    setSbarLoading(true);
    try {
      const packet = await generateSbar(caseId, destinationFacId);
      setSbarPacket(packet);
    } catch (e: any) {
      alert("Failed to generate SBAR: " + e.message);
    } finally {
      setSbarLoading(false);
    }
  };

  const currentFac = facilities.find((f) => f.id === selectedFacId);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-600" />
            FACILITYGRAPH — Care Feasibility & Referral Engine
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Validates on-site clinical execution predicate Phi(F, B) and computes road-transit referral suitability.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedFacId}
            onChange={(e) => setSelectedFacId(e.target.value)}
            className="text-xs p-2 rounded-lg border border-slate-300 bg-white"
          >
            {facilities.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.tier})
              </option>
            ))}
          </select>
          <select
            value={bundle}
            onChange={(e) => setBundle(e.target.value)}
            className="text-xs p-2 rounded-lg border border-slate-300 bg-white"
          >
            <option value="BUNDLE_STROKE_ACUTE">Acute Stroke Protocol (CT Scan & ICU)</option>
            <option value="BUNDLE_STEMI_CARDIAC">Acute STEMI Protocol (Cath Lab & CCU)</option>
            <option value="BUNDLE_OBSTETRIC_HEMORRHAGE">Obstetric Hemorrhage (Blood Bank & OT)</option>
            <option value="BUNDLE_SEPSIS_SEVERE">Severe Sepsis Protocol (HDU & High O2)</option>
            <option value="BUNDLE_TRAUMA_CRITICAL">Critical Trauma Protocol (Level 1 Trauma)</option>
            <option value="BUNDLE_ROUTINE_AMBULATORY">Routine Ambulatory Protocol</option>
          </select>
        </div>
      </div>

      {/* Local Feasibility Status Banner */}
      {feasibility && (
        <div
          className={`p-5 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
            feasibility.status === "FEASIBLE"
              ? "bg-emerald-50/70 border-emerald-300 text-emerald-950"
              : feasibility.status === "DEGRADED"
              ? "bg-amber-50/70 border-amber-300 text-amber-950"
              : "bg-rose-50/70 border-rose-300 text-rose-950"
          }`}
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-bold text-sm">
              {feasibility.status === "FEASIBLE" && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
              {feasibility.status === "DEGRADED" && <AlertTriangle className="w-5 h-5 text-amber-600" />}
              {feasibility.status === "INFEASIBLE" && <XCircle className="w-5 h-5 text-rose-600" />}
              <span>
                On-Site Care Feasibility: <strong>{feasibility.status}</strong>
              </span>
            </div>
            <p className="text-xs opacity-90">{feasibility.reason}</p>
          </div>
          {feasibility.status !== "FEASIBLE" && (
            <span className="text-xs font-bold px-3 py-1.5 rounded-lg bg-rose-600 text-white shrink-0">
              Inter-Facility Transfer Required
            </span>
          )}
        </div>
      )}

      {/* Main Grid: Facility Capabilities vs Network Referral Ranking */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 1 Col: Current Facility Equipment & Live Toggles */}
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-slate-900 flex items-center justify-between">
              <span>Operational Capabilities ({currentFac?.name})</span>
              <span className="text-[10px] text-slate-400 font-semibold">{currentFac?.tier}</span>
            </h3>
            <p className="text-[11px] text-slate-500">
              Click any equipment toggle below to test instant feasibility shifts and referral generation.
            </p>

            <div className="space-y-2">
              {currentFac?.capabilities.map((cap) => (
                <div
                  key={cap.capability_code}
                  className="flex items-center justify-between p-2.5 rounded-lg border border-slate-200 bg-slate-50/60 text-xs"
                >
                  <span className="font-semibold text-slate-800">{cap.capability_code}</span>
                  <button
                    onClick={() =>
                      handleToggleCap(currentFac.id, cap.capability_code, cap.is_operational)
                    }
                    className={`flex items-center gap-1 font-bold text-[11px] px-2 py-0.5 rounded transition-colors ${
                      cap.is_operational
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-rose-100 text-rose-800"
                    }`}
                  >
                    {cap.is_operational ? (
                      <>
                        <ToggleRight className="w-4 h-4 text-emerald-600" />
                        Online
                      </>
                    ) : (
                      <>
                        <ToggleLeft className="w-4 h-4 text-rose-600" />
                        Offline
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-slate-100 text-xs text-slate-600 space-y-1">
              <div>
                ICU Beds Available: <strong>{currentFac?.icu_beds_available}</strong> / {currentFac?.icu_beds_total}
              </div>
              <div>
                General Beds Available: <strong>{currentFac?.general_beds_available}</strong> / {currentFac?.general_beds_total}
              </div>
              <div>
                ED Avg Wait Time: <strong>{currentFac?.ed_avg_wait_min} min</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Right 2 Cols: Ranked Referral Destinations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Truck className="w-4 h-4 text-teal-600" />
                  Ranked Regional Referral Destinations
                </h3>
                <p className="text-[11px] text-slate-500">
                  Calculated based on capability match, ICU bed availability, ED congestion, and road transit duration.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {rankedReferrals.map((dest, idx) => (
                <div
                  key={dest.facility_id}
                  className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    idx === 0 && dest.feasibility_status === "FEASIBLE"
                      ? "border-teal-400 bg-teal-50/20 shadow-xs"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="space-y-1 max-w-sm">
                    <div className="flex items-center gap-2">
                      {idx === 0 && (
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-teal-700 text-white uppercase">
                          Recommended #1
                        </span>
                      )}
                      <span className="font-bold text-xs text-slate-900">{dest.facility_name}</span>
                      <span className="text-[10px] text-slate-500">({dest.tier})</span>
                    </div>
                    <p className="text-[11px] text-slate-600">{dest.feasibility_reason}</p>
                    <div className="flex items-center gap-3 text-[11px] text-slate-500 pt-1">
                      <span className="flex items-center gap-1 font-semibold text-slate-700">
                        <Clock className="w-3 h-3 text-teal-600" />
                        ~{dest.transit_minutes} min ({dest.distance_km} km)
                      </span>
                      <span>•</span>
                      <span>Available Beds: {dest.available_beds}</span>
                      <span>•</span>
                      <span>ED Wait: {dest.ed_avg_wait_min}m</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <span
                      className={`text-[10px] font-bold px-2 py-1 rounded ${
                        dest.feasibility_status === "FEASIBLE"
                          ? "bg-emerald-100 text-emerald-800"
                          : dest.feasibility_status === "DEGRADED"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-rose-100 text-rose-800"
                      }`}
                    >
                      {dest.feasibility_status}
                    </span>
                    <button
                      onClick={() => handleGenerateSbar(dest.facility_id)}
                      disabled={sbarLoading}
                      className="text-xs px-3 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold flex items-center gap-1 shadow-xs transition-colors"
                    >
                      <FileCheck2 className="w-3.5 h-3.5" />
                      Generate SBAR
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SBAR Packet Viewer */}
          {sbarPacket && (
            <div className="bg-white p-6 rounded-xl border border-teal-300 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-teal-100 pb-3">
                <h3 className="text-sm font-bold text-teal-950 flex items-center gap-2">
                  <FileCheck2 className="w-4 h-4 text-teal-700" />
                  Standardized SBAR Transfer Packet (Digital Handoff Ready)
                </h3>
                <span className="text-[10px] font-mono bg-teal-100 text-teal-800 px-2 py-0.5 rounded font-bold">
                  {sbarPacket.required_bundle}
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="font-bold text-teal-800 block mb-0.5">S — SITUATION</span>
                  <p className="text-slate-700">{sbarPacket.sbar_situation}</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="font-bold text-teal-800 block mb-0.5">B — BACKGROUND</span>
                  <p className="text-slate-700">{sbarPacket.sbar_background}</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="font-bold text-teal-800 block mb-0.5">A — ASSESSMENT</span>
                  <p className="text-slate-700">{sbarPacket.sbar_assessment}</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="font-bold text-teal-800 block mb-0.5">R — RECOMMENDATION</span>
                  <p className="text-slate-700">{sbarPacket.sbar_recommendation}</p>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-end">
                <button
                  onClick={onNavigateToOrchestration}
                  className="text-xs px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold flex items-center gap-1.5"
                >
                  Proceed to Clinician Review Gate
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
