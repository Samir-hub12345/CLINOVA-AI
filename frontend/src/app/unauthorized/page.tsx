"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowLeft, LogIn } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import { Header } from "@/components/common/header";

export default function UnauthorizedPage() {
  const { user } = useAuth();
  const targetDashboard = user ? dashboardPath(user.role) : "/login";

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-md w-full rounded-3xl bg-white border border-slate-200/90 p-8 shadow-sm text-center space-y-5">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 border border-rose-100">
            <ShieldAlert className="h-8 w-8" />
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
              Access Restricted
            </span>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Role Permission Required
            </h1>
            <p className="text-sm text-slate-500 leading-relaxed">
              {user
                ? `Your current role (${user.role.toUpperCase()}) does not have clearance to view this clinical workspace.`
                : "You must be authenticated with the proper clinical role to access this area."}
            </p>
          </div>

          <div className="pt-2 flex flex-col gap-2.5">
            <Link
              href={targetDashboard}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-5 py-3 text-sm font-bold shadow-xs transition-colors"
            >
              {user ? (
                <>
                  <ArrowLeft className="h-4 w-4" />
                  <span>Return to My Authorized Workspace</span>
                </>
              ) : (
                <>
                  <LogIn className="h-4 w-4" />
                  <span>Sign In with Clinical Credentials</span>
                </>
              )}
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}