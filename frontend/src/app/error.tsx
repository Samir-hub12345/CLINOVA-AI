"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { AlertCircle, RefreshCw, Home } from "lucide-react";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export default function RootErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error boundary captured exception:", error.message, error.digest);
  }, [error]);

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-lg bg-white rounded-3xl border border-slate-200 shadow-lg p-8 text-center space-y-6">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-50 border border-teal-100 p-3">
          <ClinovaLogo variant="mark" size="md" />
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>Connection Resilience Notice</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900">
            Clinova AI Service Notice
          </h1>
          <p className="text-sm text-slate-600 leading-relaxed max-w-md mx-auto">
            An unexpected error occurred while rendering the current page. Please click retry to reload the interface safely.
          </p>
        </div>

        {error.digest && (
          <div className="text-[11px] font-mono text-slate-400 bg-slate-50 py-1.5 px-3 rounded-lg border border-slate-100 inline-block">
            Ref: {error.digest}
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => reset()}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-6 py-2.5 text-xs font-bold transition-all shadow-sm cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Retry</span>
          </button>
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 px-5 py-2.5 text-xs font-semibold transition-colors"
          >
            <Home className="h-4 w-4 text-slate-500" />
            <span>Home</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
