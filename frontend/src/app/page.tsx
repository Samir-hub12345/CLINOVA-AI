"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  Layers,
  Building2,
  Radio,
  Cpu,
  ShieldCheck,
  FileText,
  UserCheck,
  LogOut,
  Sparkles,
  Send,
  HelpCircle,
  FileCheck2,
} from "lucide-react";
import { Persona } from "@/types";
import { getCurrentUser, getPersonas, switchPersona } from "@/lib/api";

import { PublicWebsite } from "@/components/public/PublicWebsite";
import { IntakeTab } from "@/components/workstation/IntakeTab";
import { QueueTab } from "@/components/workstation/QueueTab";
import { CareGraphTab } from "@/components/workstation/CareGraphTab";
import { FacilityGraphTab } from "@/components/workstation/FacilityGraphTab";
import { OrchestrationTab } from "@/components/workstation/OrchestrationTab";
import { SignalGraphTab } from "@/components/workstation/SignalGraphTab";
import { AuditTab } from "@/components/workstation/AuditTab";

export default function Home() {
  const [viewMode, setViewMode] = useState<"PUBLIC" | "APP">("APP");
  const [activeTab, setActiveTab] = useState<
    "INTAKE" | "QUEUE" | "CAREGRAPH" | "FACILITY" | "ORCHESTRATION" | "SIGNAL" | "AUDIT"
  >("QUEUE");

  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [currentUser, setCurrentUser] = useState<Persona | null>(null);

  useEffect(() => {
    async function initUser() {
      try {
        const [u, plist] = await Promise.all([getCurrentUser(), getPersonas()]);
        setCurrentUser(u);
        setPersonas(plist);
      } catch (err) {
        console.warn("User init fallback:", err);
      }
    }
    initUser();
  }, []);

  const handleSwitchPersona = async (personaId: string) => {
    try {
      const u = await switchPersona(personaId);
      setCurrentUser(u);
    } catch (e: any) {
      console.warn("Failed to switch persona:", e);
    }
  };

  const handleCaseCreated = (newCaseId: string) => {
    setActiveCaseId(newCaseId);
    setActiveTab("CAREGRAPH");
  };

  const handleSelectCase = (caseId: string) => {
    setActiveCaseId(caseId);
    setActiveTab("CAREGRAPH");
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation & View Mode Switcher Bar */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-3">
            {/* View Mode Switcher */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode("PUBLIC")}
                className={`text-xs px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                  viewMode === "PUBLIC"
                    ? "bg-teal-700 text-white shadow-xs"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                Public Product Architecture
              </button>
              <button
                onClick={() => setViewMode("APP")}
                className={`text-xs px-3.5 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                  viewMode === "APP"
                    ? "bg-slate-900 text-white shadow-xs"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                <Activity className="w-3.5 h-3.5 text-teal-400" />
                Operational Clinical Workstation
              </button>
            </div>

            {/* Persona Switcher & Role Info */}
            <div className="flex items-center gap-3 self-end sm:self-auto">
              <div className="flex items-center gap-1.5 text-xs">
                <UserCheck className="w-3.5 h-3.5 text-teal-700" />
                <span className="text-slate-500 font-semibold hidden md:inline">Role Persona:</span>
                <select
                  value={currentUser?.id || "usr-doc-01"}
                  onChange={(e) => handleSwitchPersona(e.target.value)}
                  className="text-xs p-1.5 rounded-md border border-slate-300 bg-white font-bold text-slate-800"
                >
                  {personas.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.full_name} ({p.role})
                    </option>
                  ))}
                </select>
              </div>

              {activeCaseId && (
                <div className="hidden lg:flex items-center gap-1 text-[11px] font-mono bg-teal-50 text-teal-900 px-2.5 py-1 rounded border border-teal-200">
                  <span className="font-semibold text-teal-700">Case Active:</span>
                  <span>{activeCaseId.slice(0, 8)}...</span>
                </div>
              )}
            </div>
          </div>

          {/* Workstation Inner Tabs Bar (when in APP mode) */}
          {viewMode === "APP" && (
            <div className="flex items-center gap-1 overflow-x-auto border-t border-slate-100 pt-1 pb-1">
              <button
                onClick={() => setActiveTab("QUEUE")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "QUEUE"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                Clinical Queue
              </button>

              <button
                onClick={() => setActiveTab("INTAKE")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "INTAKE"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                Multimodal Intake
              </button>

              <button
                onClick={() => setActiveTab("CAREGRAPH")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "CAREGRAPH"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Layers className="w-3.5 h-3.5 text-teal-600" />
                CareGraph Workstation
              </button>

              <button
                onClick={() => setActiveTab("FACILITY")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "FACILITY"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Building2 className="w-3.5 h-3.5 text-blue-600" />
                Facility Feasibility & Referrals
              </button>

              <button
                onClick={() => setActiveTab("ORCHESTRATION")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "ORCHESTRATION"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Cpu className="w-3.5 h-3.5 text-emerald-600" />
                Orchestration & Clinician Gate
              </button>

              <button
                onClick={() => setActiveTab("SIGNAL")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "SIGNAL"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Radio className="w-3.5 h-3.5 text-purple-600" />
                SignalGraph Operations
              </button>

              <button
                onClick={() => setActiveTab("AUDIT")}
                className={`text-xs px-3.5 py-2 rounded-lg font-bold transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === "AUDIT"
                    ? "bg-teal-50 text-teal-800 border-b-2 border-teal-700"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                Audit Trail
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === "PUBLIC" ? (
          <PublicWebsite onLaunchWorkstation={() => setViewMode("APP")} />
        ) : (
          <div>
            {activeTab === "QUEUE" && <QueueTab onSelectCase={handleSelectCase} />}
            {activeTab === "INTAKE" && <IntakeTab onCaseCreated={handleCaseCreated} />}
            {activeTab === "CAREGRAPH" && (
              <CareGraphTab
                caseId={activeCaseId}
                onNavigateToFacility={() => setActiveTab("FACILITY")}
                onNavigateToOrchestration={() => setActiveTab("ORCHESTRATION")}
              />
            )}
            {activeTab === "FACILITY" && (
              <FacilityGraphTab
                caseId={activeCaseId}
                facilityId={currentUser?.facility_id || "FAC-PHC-01"}
                requiredBundle="BUNDLE_STROKE_ACUTE"
                onNavigateToOrchestration={() => setActiveTab("ORCHESTRATION")}
              />
            )}
            {activeTab === "ORCHESTRATION" && (
              <OrchestrationTab
                caseId={activeCaseId}
                facilityId={currentUser?.facility_id || "FAC-DH-04"}
                onOutcomeLogged={() => {
                  setActiveTab("QUEUE");
                }}
              />
            )}
            {activeTab === "SIGNAL" && <SignalGraphTab />}
            {activeTab === "AUDIT" && <AuditTab />}
          </div>
        )}
      </div>
    </div>
  );
}