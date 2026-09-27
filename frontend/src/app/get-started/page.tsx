"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  Sparkles,
  FileText,
  UserPlus,
  LogIn,
} from "lucide-react";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { ClinovaLogo } from "@/components/common/clinova-logo";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import { useRouter } from "next/navigation";

export default function GetStartedPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to their dashboard
  React.useEffect(() => {
    if (!loading && user) {
      router.replace(dashboardPath(user.role));
    }
  }, [user, loading, router]);

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto w-full py-12 space-y-8">
        <ClinicalDisclaimer />

        {/* Page Header */}
        <div className="text-center max-w-xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200 shadow-xs">
            <ClinovaLogo variant="mark" size="xs" />
            <span>Welcome to Clinova AI</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            How would you like to <span className="text-teal-600">get started</span>?
          </h1>
          <p className="text-sm text-slate-600 leading-relaxed">
            Choose one of the options below to begin. Whether you&apos;re a patient describing symptoms,
            creating a new account, or signing in to your existing portal.
          </p>
        </div>

        {/* Three Action Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 w-full">
          {/* Patient Intake */}
          <Link
            href="/intake"
            className="group bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:border-blue-400 hover:shadow-md transition-all flex flex-col items-center text-center space-y-4"
          >
            <div className="p-3.5 bg-blue-50 rounded-xl border border-blue-100 group-hover:bg-blue-100 transition">
              <FileText className="w-7 h-7 text-blue-600" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-slate-900">Patient Intake</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Describe your symptoms in your own language using voice or text.
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700 group-hover:text-blue-900 transition mt-auto">
              <span>Start Intake</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </Link>

          {/* Sign Up */}
          <Link
            href="/register"
            className="group bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:border-teal-400 hover:shadow-md transition-all flex flex-col items-center text-center space-y-4"
          >
            <div className="p-3.5 bg-teal-50 rounded-xl border border-teal-100 group-hover:bg-teal-100 transition">
              <UserPlus className="w-7 h-7 text-teal-600" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-slate-900">Sign Up</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Create a new account to access your role-specific dashboard.
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-teal-700 group-hover:text-teal-900 transition mt-auto">
              <span>Create Account</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </Link>

          {/* Login */}
          <Link
            href="/login"
            className="group bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:border-emerald-400 hover:shadow-md transition-all flex flex-col items-center text-center space-y-4"
          >
            <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-100 group-hover:bg-emerald-100 transition">
              <LogIn className="w-7 h-7 text-emerald-600" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-bold text-slate-900">Login</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Sign in to your existing portal with your institutional credentials.
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 group-hover:text-emerald-900 transition mt-auto">
              <span>Sign In</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </Link>
        </div>

        {/* Bottom note */}
        <p className="text-xs text-slate-400 text-center max-w-md">
          All portals enforce strict role-based access control. Four role branches
          (Patient, Doctor, Staff, Admin) are available on the login and sign-up pages.
        </p>
      </main>

      <Footer />
    </div>
  );
}
