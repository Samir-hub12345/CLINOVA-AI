"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
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
  Mail,
  KeyRound,
  FileText,
  Clock,
  Sparkles,
  CheckCircle2,
  Building,
} from "lucide-react";
import { login } from "@/lib/api";

const FLOW_STEPS = [
  { step: 1, title: "Relevant clinical history is organised", actor: "AI" },
  { step: 2, title: "Draft clinical summary is prepared", actor: "AI" },
  { step: 3, title: "Missing information is highlighted", actor: "AI" },
  { step: 4, title: "Clinician reviews and documents decisions", actor: "Clinician" },
  { step: 5, title: "Note is approved and signed", actor: "Clinician" },
  { step: 6, title: "Instructions and follow-up are prepared", actor: "AI • Staff Approved" },
];

const DEMO_ROLES = [
  {
    id: "clinician",
    label: "Attending Physician (Doctor)",
    desc: "Doctor Reviewer Workbench & Decision Sign-off",
    route: "/staff/review",
  },
  {
    id: "nurse",
    label: "Triage Nurse (RN)",
    desc: "Vital Signs & NEWS2 Acuity Worklist",
    route: "/staff/triage",
  },
  {
    id: "receptionist",
    label: "Medical Receptionist",
    desc: "Patient Registration & Pathway Routing",
    route: "/staff/reception",
  },
  {
    id: "facility_admin",
    label: "Facility Administrator",
    desc: "Bed Capacity & Regional Telemetry",
    route: "/facilities",
  },
  {
    id: "sysadmin",
    label: "System Administrator",
    desc: "Cryptographic Audit Ledger & Sync Health",
    route: "/system",
  },
  {
    id: "patient",
    label: "Registered Patient",
    desc: "Patient Portal & Digital Care Tracker",
    route: "/patient",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState("clinician");
  const [username, setUsername] = useState("clinician");
  const [password, setPassword] = useState("ClinovaDemo2026!");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [ssoLoading, setSsoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forgotModal, setForgotModal] = useState(false);

  const handleRoleSelectChange = (roleId: string) => {
    setSelectedRole(roleId);
    setUsername(roleId);
    setPassword("ClinovaDemo2026!");
    setError(null);
  };

  const executeLogin = async (userToAuth: string, passToAuth: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await login(userToAuth, passToAuth);
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
      setSsoLoading(false);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      setError("Please enter your username or work email.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }
    await executeLogin(username, password);
  };

  const handleSsoClick = async () => {
    setSsoLoading(true);
    setError(null);
    // Instant organization SSO authentication using active demo credentials
    await executeLogin(selectedRole, "ClinovaDemo2026!");
  };

  return (
    <div style={{ maxWidth: 1100, margin: "20px auto", padding: "0 var(--s-3)" }}>
      <div className="auth">
        {/* LEFT PANE: Sign-in Form */}
        <div className="auth-panel">
          {/* Top Bar: Brand & Demo badge */}
          <div className="row between" style={{ marginBottom: 24 }}>
            <Link href="/" className="row gap-2" style={{ textDecoration: "none" }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  minWidth: 32,
                  minHeight: 32,
                  borderRadius: "var(--r-md)",
                  border: "1px solid var(--border)",
                  backgroundColor: "var(--navy-800)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  overflow: "hidden",
                  flexShrink: 0,
                }}
              >
                <Image
                  src="/branding/clinova-ai-mark.png"
                  alt="CLINOVA AI Logo"
                  width={24}
                  height={24}
                  priority
                  style={{ objectFit: "contain" }}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span
                  style={{
                    fontSize: "1.0625rem",
                    fontWeight: 800,
                    color: "var(--navy-900)",
                    letterSpacing: "-0.02em",
                    lineHeight: 1.15,
                  }}
                >
                  CLINOVA <span style={{ color: "var(--teal-600)" }}>AI</span>
                </span>
                <span
                  style={{
                    fontSize: "0.625rem",
                    color: "var(--teal-700)",
                    fontWeight: 700,
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                    lineHeight: 1.2,
                  }}
                >
                  Continuous Care
                </span>
              </div>
            </Link>

            <span className="demo-ribbon demo-ribbon-teal">
              <span className="dot" style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--teal-600)" }} />
              Demo Environment
            </span>
          </div>

          {/* Form Wrap */}
          <div className="auth-form-wrap">
            <div className="stack gap-1" style={{ marginBottom: 20 }}>
              <h1 style={{ fontSize: "var(--fs-2xl)", color: "var(--navy-900)", fontWeight: 700 }}>
                Welcome to Clinova AI
              </h1>
              <p className="small muted">
                Your clinical workspace, organized around better care.
              </p>
            </div>

            {error && (
              <div className="alert alert-error" style={{ marginBottom: 16 }}>
                <AlertTriangle style={{ width: 16, height: 16 }} aria-hidden="true" />
                <span>{error}</span>
              </div>
            )}

            {/* Organization SSO Button */}
            <button
              type="button"
              onClick={handleSsoClick}
              disabled={loading || ssoLoading}
              className="btn btn-secondary btn-lg btn-block"
              style={{ marginBottom: 16, justifyContent: "center", gap: 10 }}
            >
              <Building style={{ width: 18, height: 18, color: "var(--teal-700)" }} aria-hidden="true" />
              <span>{ssoLoading ? "Connecting to Hospital SSO..." : "Sign in with Organization SSO"}</span>
            </button>

            {/* Divider */}
            <div className="row gap-3 xs muted" style={{ marginBottom: 16 }}>
              <hr className="grow" style={{ borderColor: "var(--border)", borderStyle: "solid", borderWidth: "1px 0 0 0" }} />
              <span>or sign in with credentials</span>
              <hr className="grow" style={{ borderColor: "var(--border)", borderStyle: "solid", borderWidth: "1px 0 0 0" }} />
            </div>

            <form onSubmit={handleFormSubmit} className="stack gap-4">
              {/* Role Quick Selector */}
              <div className="field">
                <label className="label" htmlFor="role-select">
                  <span>Demo: Sign in as persona</span>
                  <span className="req">*</span>
                </label>
                <select
                  id="role-select"
                  className="select"
                  value={selectedRole}
                  onChange={(e) => handleRoleSelectChange(e.target.value)}
                >
                  {DEMO_ROLES.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.label} — {role.desc}
                    </option>
                  ))}
                </select>
                <span className="hint">
                  Role controls workspace access (e.g. only clinicians can sign consultation notes).
                </span>
              </div>

              {/* Username / Email */}
              <div className="field">
                <label className="label" htmlFor="username-input">
                  <span>Work Email or Username</span>
                  <span className="req">*</span>
                </label>
                <div className="input-group">
                  <Mail style={{ width: 16, height: 16, color: "var(--text-4)" }} aria-hidden="true" />
                  <input
                    id="username-input"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    className="input"
                    placeholder="name@clinic.org"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="field">
                <div className="row between">
                  <label className="label" htmlFor="password-input">
                    <span>Password</span>
                    <span className="req">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setForgotModal(true)}
                    className="btn btn-ghost btn-sm"
                    style={{ padding: "0 4px", fontSize: "11px", color: "var(--teal-700)" }}
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="input-group">
                  <KeyRound style={{ width: 16, height: 16, color: "var(--text-4)" }} aria-hidden="true" />
                  <input
                    id="password-input"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="input"
                    placeholder="Enter password"
                    style={{ paddingRight: 40 }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="input-action btn btn-ghost btn-icon btn-sm"
                  >
                    {showPassword ? (
                      <EyeOff style={{ width: 15, height: 15 }} aria-hidden="true" />
                    ) : (
                      <Eye style={{ width: 15, height: 15 }} aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || ssoLoading}
                className="btn btn-primary btn-lg btn-block"
                style={{ marginTop: 4, justifyContent: "center" }}
              >
                <LogIn style={{ width: 18, height: 18 }} aria-hidden="true" />
                <span>{loading ? "Signing in..." : "Sign in"}</span>
              </button>

              <p className="xs muted" style={{ textAlign: "center", margin: "4px 0 0" }}>
                Demo password: <code className="mono">ClinovaDemo2026!</code> for all pre-seeded accounts.
              </p>
            </form>
          </div>

          {/* Footer note */}
          <div className="row between xs muted" style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
            <span>Protected by Role-Based Access Control</span>
            <span>Sessions time out after 15 minutes of inactivity</span>
          </div>
        </div>

        {/* RIGHT PANE: Workflow Continuum Showcase */}
        <div className="auth-aside">
          <div className="stack gap-4">
            <span className="demo-ribbon" style={{ alignSelf: "flex-start", background: "rgba(255,255,255,0.08)", color: "#9fb3c8", borderColor: "rgba(255,255,255,0.15)" }}>
              AI Clinical Workflow Assistant
            </span>

            <div>
              <h2>Less paperwork. More time for patient care.</h2>
              <p style={{ color: "#9fb3c8", maxWidth: 460, marginTop: 10, lineHeight: 1.6, fontSize: "var(--fs-base)" }}>
                Clinova AI organises patient information, prepares documentation and coordinates follow-ups — while healthcare professionals stay in control of every clinical decision.
              </p>
            </div>

            {/* 6 Continuous Flow Steps */}
            <div className="stack gap-2" style={{ maxWidth: 460, marginTop: 8 }}>
              {FLOW_STEPS.map((item) => (
                <div key={item.step} className="flow-step">
                  <span className="n">{item.step}</span>
                  <span style={{ color: "#e2e8f0", fontWeight: 500 }}>{item.title}</span>
                  <span
                    className="who"
                    style={{
                      color: item.actor.includes("Clinician") ? "#5fd3c7" : "#94a3b8",
                      background: item.actor.includes("Clinician") ? "rgba(95, 211, 199, 0.12)" : "rgba(255, 255, 255, 0.06)",
                    }}
                  >
                    {item.actor}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Security Highlights */}
          <div className="row gap-4 xs" style={{ color: "#8aa0b8", marginTop: 24, flexWrap: "wrap" }}>
            <span className="row gap-2">
              <ShieldCheck style={{ width: 15, height: 15, color: "#5fd3c7" }} aria-hidden="true" />
              Role-Based Access
            </span>
            <span className="row gap-2">
              <Clock style={{ width: 15, height: 15, color: "#38bdf8" }} aria-hidden="true" />
              Full Audit Trail
            </span>
            <span>Non-Diagnostic Clinical Safety Invariant</span>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {forgotModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(13, 33, 53, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
            padding: 16,
          }}
          onClick={() => setForgotModal(false)}
        >
          <div
            className="card"
            style={{ maxWidth: 420, width: "100%", padding: "var(--s-6)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="row gap-2" style={{ marginBottom: 12 }}>
              <KeyRound style={{ width: 20, height: 20, color: "var(--teal-600)" }} aria-hidden="true" />
              <h3 style={{ fontSize: "var(--fs-lg)", margin: 0 }}>Demo Account Credentials</h3>
            </div>
            <p className="small subtle" style={{ lineHeight: 1.5, marginBottom: 16 }}>
              All demo persona accounts are pre-configured with the default demo password:
            </p>
            <div
              style={{
                padding: "10px 14px",
                background: "var(--surface-sunken)",
                border: "1px solid var(--border)",
                borderRadius: "var(--r-md)",
                marginBottom: 16,
                fontSize: "var(--fs-sm)",
              }}
            >
              Password: <code className="mono strong">ClinovaDemo2026!</code>
            </div>
            <p className="xs muted" style={{ lineHeight: 1.5, marginBottom: 16 }}>
              Select any role from the dropdown menu to sign in as Doctor, Nurse, Receptionist, Facility Admin, or Patient.
            </p>
            <button
              type="button"
              className="btn btn-primary btn-block"
              onClick={() => setForgotModal(false)}
            >
              Close and Continue
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
