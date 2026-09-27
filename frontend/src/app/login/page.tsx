"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  ShieldCheck,
  Lock,
  Mail,
  ArrowRight,
  UserCheck,
  Stethoscope,
  User,
  Sparkles,
  AlertCircle,
  Building,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { Button } from "@/components/ui/button";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { ClinovaLogo } from "@/components/common/clinova-logo";

function LoginForm() {
  const router = useRouter();
  const { setUser, user, loading: authLoading } = useAuth();
  const searchParams = useSearchParams();
  const roleParam = searchParams?.get("role");
  const redirectParam = searchParams?.get("redirect");

  useEffect(() => {
    if (!authLoading && user) {
      const target = redirectParam || dashboardPath(user.role);
      router.replace(target);
    }
  }, [user, authLoading, router, redirectParam]);

  const [activeTab, setActiveTab] = useState<"patient" | "nurse" | "doctor" | "admin">("doctor");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (roleParam === "patient") {
      setActiveTab("patient");
      setEmail("patient@clinova.ai");
      setPassword("ClinovaPatient2026!");
    } else if (roleParam === "nurse" || roleParam === "staff") {
      setActiveTab("nurse");
      setEmail("staff@clinova.ai");
      setPassword("ClinovaStaff2026!");
    } else if (roleParam === "doctor") {
      setActiveTab("doctor");
      setEmail("doctor@clinova.ai");
      setPassword("ClinovaDoctor2026!");
    } else if (roleParam === "admin") {
      setActiveTab("admin");
      setEmail("admin@clinova.ai");
      setPassword("ClinovaAdmin2026!");
    }
  }, [roleParam]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const res = await api.login(email, password);
    setLoading(false);

    if (res.error) {
      setError(res.error);
    } else if (res.data) {
      setUser(res.data.user);
      const target = redirectParam || dashboardPath(res.data.user.role);
      router.replace(target);
    }
  };

  const setDemoCredentials = (role: "patient" | "nurse" | "doctor" | "admin") => {
    setActiveTab(role);
    setError(null);
    if (role === "doctor") {
      setEmail("doctor@clinova.ai");
      setPassword("ClinovaDoctor2026!");
    } else if (role === "nurse") {
      setEmail("staff@clinova.ai");
      setPassword("ClinovaStaff2026!");
    } else if (role === "patient") {
      setEmail("patient@clinova.ai");
      setPassword("ClinovaPatient2026!");
    } else if (role === "admin") {
      setEmail("admin@clinova.ai");
      setPassword("ClinovaAdmin2026!");
    }
  };

  return (
    <div className="w-full max-w-lg bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
      {/* Header */}
      <div className="text-center space-y-1">
        <div className="inline-flex p-2.5 bg-teal-50/80 rounded-2xl border border-teal-100/80 shadow-xs mb-2">
          <ClinovaLogo variant="mark" size="lg" priority={true} />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Clinova AI Portal Sign In</h1>
        <p className="text-xs text-slate-500">
          Role-authenticated clinical decision support and triage management
        </p>
      </div>

      {/* Role Selection Tabs */}
      <div className="grid grid-cols-4 gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200">
        <button
          type="button"
          onClick={() => setDemoCredentials("doctor")}
          className={`py-2 px-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            activeTab === "doctor"
              ? "bg-white text-emerald-800 shadow-xs border border-slate-200"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Stethoscope className="w-3.5 h-3.5 text-emerald-600" />
          <span>Doctor</span>
        </button>

        <button
          type="button"
          onClick={() => setDemoCredentials("nurse")}
          className={`py-2 px-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            activeTab === "nurse"
              ? "bg-white text-teal-800 shadow-xs border border-slate-200"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Activity className="w-3.5 h-3.5 text-teal-600" />
          <span>Staff</span>
        </button>

        <button
          type="button"
          onClick={() => setDemoCredentials("patient")}
          className={`py-2 px-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            activeTab === "patient"
              ? "bg-white text-blue-800 shadow-xs border border-slate-200"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <User className="w-3.5 h-3.5 text-blue-600" />
          <span>Patient</span>
        </button>

        <button
          type="button"
          onClick={() => setDemoCredentials("admin")}
          className={`py-2 px-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            activeTab === "admin"
              ? "bg-white text-amber-800 shadow-xs border border-slate-200"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Building className="w-3.5 h-3.5 text-amber-600" />
          <span>Admin</span>
        </button>
      </div>

      {/* Quick Demo Fill Matrix */}
      <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
            ⚡ Quick-Select Demo Accounts
          </span>
          <span className="text-[10px] bg-teal-100 text-teal-800 font-semibold px-2 py-0.5 rounded">
            Pre-seeded
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setDemoCredentials("doctor")}
            className="p-2 text-left bg-white border border-slate-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50/30 transition text-xs"
          >
            <div className="font-semibold text-emerald-900 flex items-center gap-1">
              <Stethoscope className="w-3 h-3 text-emerald-600" /> Dr. Sarah Chen
            </div>
            <div className="text-[10px] text-slate-500 font-mono">doctor@clinova.ai</div>
          </button>

          <button
            type="button"
            onClick={() => setDemoCredentials("nurse")}
            className="p-2 text-left bg-white border border-slate-200 rounded-lg hover:border-teal-400 hover:bg-teal-50/30 transition text-xs"
          >
            <div className="font-semibold text-teal-900 flex items-center gap-1">
              <Activity className="w-3 h-3 text-teal-600" /> Nurse Sunita Patel
            </div>
            <div className="text-[10px] text-slate-500 font-mono">staff@clinova.ai</div>
          </button>

          <button
            type="button"
            onClick={() => setDemoCredentials("patient")}
            className="p-2 text-left bg-white border border-slate-200 rounded-lg hover:border-blue-400 hover:bg-blue-50/30 transition text-xs"
          >
            <div className="font-semibold text-blue-900 flex items-center gap-1">
              <User className="w-3 h-3 text-blue-600" /> James Miller
            </div>
            <div className="text-[10px] text-slate-500 font-mono">patient@clinova.ai</div>
          </button>

          <button
            type="button"
            onClick={() => setDemoCredentials("admin")}
            className="p-2 text-left bg-white border border-slate-200 rounded-lg hover:border-amber-400 hover:bg-amber-50/30 transition text-xs"
          >
            <div className="font-semibold text-amber-900 flex items-center gap-1">
              <Lock className="w-3 h-3 text-amber-600" /> Facility Admin
            </div>
            <div className="text-[10px] text-slate-500 font-mono">admin@clinova.ai</div>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 font-medium flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Login Form */}
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Institutional Email
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@clinova.ai"
              className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
        </div>

        <Button type="submit" loading={loading} className="w-full py-2.5 mt-2 gap-2 text-sm">
          Sign In to Clinova AI <ArrowRight className="w-4 h-4" />
        </Button>
      </form>

      {/* Bottom links */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
          HIPAA-Ready Gate
        </span>
        <Link href="/register" className="text-teal-600 font-semibold hover:underline">
          Create new account
        </Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto w-full space-y-6">
        <ClinicalDisclaimer />
        <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading sign-in portal...</div>}>
          <LoginForm />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}