"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { AlertCircle, RefreshCw, Home, ShieldAlert } from "lucide-react";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export default function DashboardErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log safe error telemetry without exposing secrets or PHI
    console.error("Dashboard error boundary captured exception:", error.message, error.digest);
  }, [error]);

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-lg bg-white rounded-3xl border border-slate-200 shadow-lg p-8 text-center space-y-6">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 border border-rose-100">
          <ShieldAlert className="h-8 w-8" />
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-100/70 text-rose-700 text-xs font-semibold">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>Workspace Resilience Guard</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900">
            Workspace Temporarily Unavailable
          </h1>
          <p className="text-sm text-slate-600 leading-relaxed max-w-md mx-auto">
            The clinical dashboard encountered an unexpected rendering condition while loading your authorized records. All underlying data remains secure and isolated.
          </p>
        </div>

        {error.digest && (
          <div className="text-[11px] font-mono text-slate-400 bg-slate-50 py-1.5 px-3 rounded-lg border border-slate-100 inline-block">
            Incident Correlation Ref: {error.digest}
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => reset()}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-6 py-2.5 text-xs font-bold transition-all shadow-sm cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Retry Workspace</span>
          </button>
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-5 py-2.5 text-xs font-semibold transition-colors"
          >
            <Home className="h-4 w-4 text-slate-500" />
            <span>Return to Gateway</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
