"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  ShieldCheck,
  Lock,
  Mail,
  User,
  ArrowRight,
  AlertCircle,
  Building,
} from "lucide-react";
import { api } from "@/lib/api";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { Button } from "@/components/ui/button";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { ClinovaLogo } from "@/components/common/clinova-logo";

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const roleParam = searchParams?.get("role");

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("patient");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (roleParam === "patient") {
      setRole("patient");
    } else if (roleParam === "nurse" || roleParam === "staff") {
      setRole("nurse");
    } else if (roleParam === "doctor") {
      setRole("doctor");
    }
  }, [roleParam]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const res = await api.register({
      full_name: fullName,
      email,
      password,
      role: role as any,
    });
    setLoading(false);

    if (res.error) {
      setError(res.error);
    } else {
      router.push(`/login?role=${role}&registered=true`);
    }
  };

  return (
    <div className="w-full max-w-md bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
      <div className="text-center space-y-1">
        <div className="inline-flex p-2.5 bg-teal-50/80 rounded-2xl border border-teal-100/80 shadow-xs mb-2">
          <ClinovaLogo variant="mark" size="lg" priority={true} />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Create Account</h1>
        <p className="text-xs text-slate-500">
          Register to access Clinova AI clinical decision and triage flows
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 font-medium flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Full Legal Name
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Dr. Jordan Mitchell / Sunita Patel"
              className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Access Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
          >
            <option value="patient">Patient (Personal Symptom Intake & Records)</option>
            <option value="doctor">Physician / Medical Officer (Doctor)</option>
            <option value="nurse">Triage Nurse / Healthcare Staff</option>
          </select>
          <p className="text-[11px] text-slate-500 mt-1">
            Staff roles require institution authorization.
          </p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>
        </div>

        <Button type="submit" loading={loading} className="w-full py-2.5 mt-2 gap-2 text-sm">
          Register Account <ArrowRight className="w-4 h-4" />
        </Button>
      </form>

      <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl flex items-start gap-2 text-[11px] text-amber-900 leading-tight">
        <Building className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Facility Administrator Access: </span>
          Administrative credentials cannot be self-registered publicly. Contact your institution&apos;s system supervisor to provision admin tokens.
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
          HIPAA-Ready Architecture
        </span>
        <Link href="/login" className="text-teal-600 font-semibold hover:underline">
          Already registered? Sign in
        </Link>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto w-full space-y-6">
        <ClinicalDisclaimer />
        <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading registration form...</div>}>
          <RegisterForm />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}