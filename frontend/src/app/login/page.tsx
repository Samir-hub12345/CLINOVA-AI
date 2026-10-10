"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LogIn,
  AlertTriangle,
  ShieldCheck,
  Stethoscope,
  UserCheck,
  UserPlus,
  Building2,
  Lock,
  ArrowRight,
  Activity,
  Eye,
  EyeOff,
} from "lucide-react";
import { login } from "@/lib/api";
import { Persona } from "@/types";

const DEMO_PERSONAS = [
  {
    id: "clinician",
    name: "Dr. Priya Sharma",
    role: "CLINICIAN",
    desc: "Attending Physician • Doctor Reviewer Workbench",
    icon: Stethoscope,
    badge: "badge-teal",
    target: "/staff/review",
  },
  {
    id: "nurse",
    name: "Ananya Patel, RN",
    role: "NURSE",
    desc: "Triage Nurse • Vital Signs & Acuity Worklist",
    icon: UserCheck,
    badge: "badge-warning",
    target: "/staff/triage",
  },
  {
    id: "receptionist",
    name: "Tunde Olawale",
    role: "RECEPTIONIST",
    desc: "Medical Receptionist • Patient Registration Desk",
    icon: UserPlus,
    badge: "badge-navy",
    target: "/staff/reception",
  },
  {
    id: "facility_admin",
    name: "Rajesh Mohanty",
    role: "FACILITY_ADMIN",
    desc: "Facility Administrator • Bed & ICU Telemetry",
    icon: Building2,
    badge: "badge-info",
    target: "/facilities",
  },
  {
    id: "sysadmin",
    name: "System Administrator",
    role: "SYSTEM_ADMIN",
    desc: "Platform Admin • Cryptographic Audit Ledger",
    icon: ShieldCheck,
    badge: "badge-navy",
    target: "/system",
  },
  {
    id: "patient",
    name: "Synthetic Patient",
    role: "PATIENT",
    desc: "Patient Portal • Digital Intake & Care Status",
    icon: Activity,
    badge: "badge-purple",
    target: "/patient",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("clinician");
  const [password, setPassword] = useState("ClinovaDemo2026!");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await login(username, password);
      const role = result.user?.role?.toUpperCase();

      if (role === "PATIENT") {
        router.push("/patient");
      } else if (role === "RECEPTIONIST") {
        router.push("/staff/reception");
      } else if (role === "NURSE") {
        router.push("/staff/triage");
      } else if (role === "CLINICIAN" || role === "DOCTOR") {
        router.push("/staff/review");
      } else if (role === "FACILITY_ADMIN") {
        router.push("/facilities");
      } else if (role === "SYSTEM_ADMIN" || role === "AUDITOR") {
        router.push("/system");
      } else if (role === "REFERRAL_COORDINATOR") {
        router.push("/referrals");
      } else {
        router.push("/staff");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (personaId: string, targetPath: string) => {
    setUsername(personaId);
    setPassword("ClinovaDemo2026!");
  };

  return (
    <div style={{ maxWidth: 1040, margin: "20px auto", padding: "0 var(--s-4)" }}>
      <div className="grid grid-2 gap-6" style={{ alignItems: "start" }}>
        {/* Left Card: Login Form */}
        <div className="card" style={{ padding: "var(--s-6)" }}>
          <div className="stack gap-1" style={{ marginBottom: 20 }}>
            <span className="badge badge-teal" style={{ alignSelf: "flex-start" }}>
              Secure Clinical Gateway
            </span>
            <h1 style={{ fontSize: "var(--fs-2xl)", color: "var(--navy-900)", marginTop: 6 }}>
              Sign In to CLINOVA AI
            </h1>
            <p className="small muted">
              Continuous care intelligence, facility feasibility, and clinical orchestration.
            </p>
          </div>

          {error && (
            <div className="alert alert-error" style={{ marginBottom: 16 }}>
              <AlertTriangle style={{ width: 16, height: 16 }} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="stack gap-4">
            <div className="field">
              <label className="label">
                Username or Persona Identifier <span className="req">*</span>
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="input"
                placeholder="e.g. clinician, nurse, receptionist"
              />
            </div>

            <div className="field">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <label className="label">
                  Password <span className="req">*</span>
                </label>
                <span className="xs muted" style={{ fontSize: "11px" }}>
                  Demo: <code>ClinovaDemo2026!</code>
                </span>
              </div>
              <div style={{ position: "relative" }}>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="input"
                  style={{ paddingRight: 38 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  style={{
                    position: "absolute",
                    right: 8,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--text-muted, #94a3b8)",
                    padding: 4,
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {showPassword ? (
                    <EyeOff style={{ width: 16, height: 16 }} aria-hidden="true" />
                  ) : (
                    <Eye style={{ width: 16, height: 16 }} aria-hidden="true" />
                  )}
                </button>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "var(--fs-xs)" }}>
              <span className="xs muted">
                Forgot password? Contact facility sysadmin.
              </span>
              <Link href="/register" className="xs link" style={{ color: "var(--teal-600)", fontWeight: 600 }}>
                Register Staff Account
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary btn-lg btn-block"
              style={{ marginTop: 8 }}
            >
              <LogIn style={{ width: 16, height: 16 }} aria-hidden="true" />
              <span>{loading ? "Authenticating Session..." : "Sign In to Workstation"}</span>
            </button>
          </form>

          {/* Quick Demo Persona Shortcuts */}
          <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
            <span className="section-title" style={{ display: "block", marginBottom: 10 }}>
              Quick Demonstration Personas:
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {DEMO_PERSONAS.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => handleQuickSelect(p.id, p.target)}
                  className={`btn btn-sm ${username === p.id ? "btn-primary" : "btn-secondary"}`}
                  style={{ fontSize: "var(--fs-xs)" }}
                >
                  <p.icon style={{ width: 12, height: 12 }} aria-hidden="true" />
                  <span>{p.name} ({p.role})</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Card: Persona Reference & Security Governance */}
        <div className="stack gap-4">
          <div className="card" style={{ backgroundColor: "var(--navy-900)", color: "#fff", padding: "var(--s-6)" }}>
            <h2 style={{ fontSize: "var(--fs-lg)", color: "#fff", marginBottom: 8 }}>
              Role-Aware Clinical Isolation
            </h2>
            <p className="xs subtle" style={{ color: "#c6d3e1", lineHeight: 1.6, marginBottom: 16 }}>
              CLINOVA AI strictly separates permissions across the healthcare continuum. Choose a persona to enter their dedicated workspace:
            </p>

            <div className="stack gap-2">
              {DEMO_PERSONAS.map((p) => (
                <div
                  key={p.id}
                  onClick={() => handleQuickSelect(p.id, p.target)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "8px 12px",
                    borderRadius: "var(--r-md)",
                    backgroundColor: username === p.id ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.06)",
                    cursor: "pointer",
                    border: username === p.id ? "1px solid var(--teal-600)" : "1px solid transparent",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div className="row gap-2">
                    <p.icon style={{ width: 16, height: 16, color: "var(--teal-100)" }} aria-hidden="true" />
                    <div>
                      <strong style={{ fontSize: "var(--fs-sm)", display: "block", color: "#fff" }}>
                        {p.name}
                      </strong>
                      <span style={{ fontSize: "11px", color: "#98a2b3" }}>{p.desc}</span>
                    </div>
                  </div>
                  <ArrowRight style={{ width: 14, height: 14, color: "#98a2b3" }} aria-hidden="true" />
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ padding: "var(--s-5)" }}>
            <div className="row gap-2" style={{ marginBottom: 6 }}>
              <ShieldCheck style={{ width: 16, height: 16, color: "var(--success)" }} aria-hidden="true" />
              <strong className="small">Compliance & Safety Safeguards</strong>
            </div>
            <p className="xs muted" style={{ lineHeight: 1.5, margin: 0 }}>
              Strictly non-diagnostic clinical decision support. Zero autonomous clinical actions. Server-side RBAC and DPDP Act 2023 certified.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
