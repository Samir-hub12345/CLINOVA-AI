import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 mt-auto py-8 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <p className="font-medium text-slate-700">CLINOVA AI — Continuous Care Intelligence</p>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Non-diagnostic clinical decision support & triage intelligence architecture.
          </p>
        </div>
        <div className="text-right text-[11px] text-slate-400">
          <span>Synthetic data prototype • Privacy-first • Qualified human handoff required</span>
        </div>
      </div>
    </footer>
  );
};
