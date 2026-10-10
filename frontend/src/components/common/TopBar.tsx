"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Share2,
  Building2,
  ShieldCheck,
  Menu,
  X,
  LogOut,
  LogIn,
  AlertTriangle,
} from "lucide-react";
import { Persona } from "@/types";
import { getPersonas, getCurrentUser, getStoredUser, switchPersona, login, logout, FALLBACK_PERSONAS } from "@/lib/api";
import { RoleBadge } from "./RoleBadge";
import { ConnectionStatus } from "./ConnectionStatus";
import { NotificationCenter } from "./NotificationCenter";

interface TopBarProps {
  onOpenReferralDrawer?: () => void;
  onOpenFacilityDrawer?: () => void;
  onOpenSystemDrawer?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  onOpenReferralDrawer,
  onOpenFacilityDrawer,
  onOpenSystemDrawer,
}) => {
  const pathname = usePathname();
  const [personas, setPersonas] = useState<Persona[]>(FALLBACK_PERSONAS);
  const [currentUser, setCurrentUser] = useState<Persona | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [loginUsername, setLoginUsername] = useState("clinician");
  const [loginPassword, setLoginPassword] = useState("ClinovaDemo2026!");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    // 1. Immediately hydrate cached user from session storage synchronously on client mount
    const stored = getStoredUser();
    if (stored) {
      setCurrentUser(stored);
    }

    // 2. Validate live session and fetch updated personas in background
    async function validateSession() {
      try {
        const u = await getCurrentUser();
        if (u) {
          setCurrentUser(u);
        }
        const plist = await getPersonas();
        if (plist && plist.length > 0) {
          setPersonas(plist);
        }
      } catch {
        // Handled by resilient fallback
      }
    }
    validateSession();

    const handleExpired = () => {
      setSessionExpired(true);
      setCurrentUser(null);
    };

    const handleAuthChange = (e: Event) => {
      const custom = e as CustomEvent<{ token: string | null; user: Persona | null }>;
      if (custom.detail && custom.detail.user !== undefined) {
        setSessionExpired(false);
        setCurrentUser(custom.detail.user);
        return;
      }
      validateSession();
    };

    window.addEventListener("clinova_session_expired", handleExpired);
    window.addEventListener("clinova_auth_changed", handleAuthChange);

    return () => {
      window.removeEventListener("clinova_session_expired", handleExpired);
      window.removeEventListener("clinova_auth_changed", handleAuthChange);
    };
  }, []);

  const handleRoleChange = async (personaId: string) => {
    try {
      const u = await switchPersona(personaId);
      setCurrentUser(u);
      setSessionExpired(false);
    } catch (e) {
      console.warn("Role switch fallback:", e);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setCurrentUser(null);
      setSessionExpired(false);
    } catch (e) {
      console.warn("Logout error:", e);
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError(null);
    try {
      const result = await login(loginUsername, loginPassword);
      setCurrentUser(result.user);
      setSessionExpired(false);
      setLoginModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed";
      setLoginError(msg);
    } finally {
      setLoginLoading(false);
    }
  };

  const navLinks = [
    { label: "Overview", href: "/" },
    { label: "Reception", href: "/staff/reception" },
    { label: "Patient Intake", href: "/patient" },
    { label: "Nurse Triage", href: "/staff/triage" },
    { label: "Doctor Review", href: "/staff/review" },
    { label: "Referrals", href: "/referrals" },
    { label: "Facilities", href: "/facilities" },
    { label: "System", href: "/system" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header
      style={{
        backgroundColor: "var(--clinova-surface)",
        borderBottom: "1px solid var(--clinova-border)",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}
    >
      <div className="clinova-container">
        {/* Main Header Bar */}
        <div
          style={{
            height: 60,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          {/* 1. Brand Identity */}
          <Link
            href="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
              flexShrink: 0,
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                minWidth: 32,
                minHeight: 32,
                borderRadius: "var(--r-md, 8px)",
                backgroundColor: "var(--navy-800, #16324f)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
              aria-hidden="true"
            >
              <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
                <path d="M8 2v12M2 8h12" stroke="#5fd3c7" strokeWidth="2.75" strokeLinecap="round" />
              </svg>
            </div>
            <div style={{ display: "flex", flexDirection: "column", flexShrink: 0 }}>
              <span
                style={{
                  fontSize: "1.0625rem",
                  fontWeight: 800,
                  color: "var(--navy-900, #0d2135)",
                  letterSpacing: "-0.02em",
                  display: "block",
                  lineHeight: 1.15,
                  whiteSpace: "nowrap",
                }}
              >
                CLINOVA <span style={{ color: "var(--teal-600, #0f9d91)" }}>AI</span>
              </span>
              <span
                style={{
                  fontSize: "0.625rem",
                  color: "var(--teal-700, #0b7d73)",
                  fontWeight: 700,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  display: "block",
                  lineHeight: 1.2,
                  whiteSpace: "nowrap",
                }}
              >
                Continuous Care Intelligence
              </span>
            </div>
          </Link>

          {/* 2. Desktop Navigation Links */}
          <nav
            aria-label="Main Navigation"
            style={{
              display: "none",
              alignItems: "center",
              gap: 3,
              flexShrink: 1,
              minWidth: 0,
            }}
            className="clinova-desktop-nav"
          >
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  fontSize: "0.8125rem",
                  fontWeight: 600,
                  textDecoration: "none",
                  padding: "4px 8px",
                  borderRadius: "var(--clinova-radius-md)",
                  whiteSpace: "nowrap",
                  color: isActive(link.href)
                    ? "var(--clinova-accent-text)"
                    : "var(--clinova-text-secondary)",
                  backgroundColor: isActive(link.href)
                    ? "var(--clinova-accent-light)"
                    : "transparent",
                  border: isActive(link.href)
                    ? "1px solid var(--clinova-accent-border)"
                    : "1px solid transparent",
                  transition: "all 0.15s ease",
                }}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* 3. Operational Status, Role Switcher & Drawer Triggers */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
            {/* Connection Status Indicator */}
            <div className="clinova-desktop-status">
              <ConnectionStatus status="ONLINE" />
            </div>

            {/* Clinical Notifications & Quick Drawer Action Toggles */}
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <NotificationCenter />
              {onOpenReferralDrawer && (
                <button
                  onClick={onOpenReferralDrawer}
                  className="clinova-icon-btn hide-mobile"
                  title="Open Referral Coordination Drawer"
                  aria-label="Open Referral Coordination Drawer"
                >
                  <Share2 style={{ width: 15, height: 15 }} aria-hidden="true" />
                </button>
              )}
              {onOpenFacilityDrawer && (
                <button
                  onClick={onOpenFacilityDrawer}
                  className="clinova-icon-btn hide-mobile"
                  title="Open Facility Resources Drawer"
                  aria-label="Open Facility Resources Drawer"
                >
                  <Building2 style={{ width: 15, height: 15 }} aria-hidden="true" />
                </button>
              )}
              {onOpenSystemDrawer && (
                <button
                  onClick={onOpenSystemDrawer}
                  className="clinova-icon-btn hide-mobile"
                  title="Open System Audit Drawer"
                  aria-label="Open System Audit Drawer"
                >
                  <ShieldCheck style={{ width: 15, height: 15 }} aria-hidden="true" />
                </button>
              )}
            </div>

            {/* Role Switcher & Session Controls */}
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              {currentUser ? (
                <>
                  <div className="clinova-desktop-badge">
                    <RoleBadge role={currentUser.role} />
                  </div>
                  <select
                    aria-label="Select Active Clinical Role"
                    value={currentUser.id}
                    onChange={(e) => handleRoleChange(e.target.value)}
                    className="hide-mobile"
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      padding: "4px 8px",
                      borderRadius: "var(--clinova-radius-md)",
                      border: "1px solid var(--clinova-border-subtle)",
                      backgroundColor: "var(--clinova-surface)",
                      color: "var(--clinova-text-primary)",
                      cursor: "pointer",
                      maxWidth: 160,
                      textOverflow: "ellipsis",
                    }}
                  >
                    {personas.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.full_name} ({p.role})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleLogout}
                    className="clinova-icon-btn"
                    title="Sign Out of Active Session"
                    aria-label="Sign Out of Active Session"
                  >
                    <LogOut style={{ width: 15, height: 15, color: "var(--clinova-danger)" }} aria-hidden="true" />
                  </button>
                </>
              ) : (
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <Link
                    href="/login"
                    className="btn btn-primary btn-sm"
                    style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6 }}
                  >
                    <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
                    <span>Sign In</span>
                  </Link>
                  <select
                    aria-label="Demo Persona Quick Select"
                    value=""
                    onChange={(e) => {
                      if (e.target.value) handleRoleChange(e.target.value);
                    }}
                    className="select hide-mobile"
                    style={{
                      height: 30,
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      padding: "2px 24px 2px 8px",
                      maxWidth: 130,
                      cursor: "pointer",
                    }}
                  >
                    <option value="" disabled>Demo Persona</option>
                    {personas.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.full_name} ({p.role})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="clinova-icon-btn clinova-mobile-menu-btn"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? (
                <X style={{ width: 18, height: 18 }} aria-hidden="true" />
              ) : (
                <Menu style={{ width: 18, height: 18 }} aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* Session Expired Alert Banner */}
        {sessionExpired && (
          <div
            style={{
              backgroundColor: "var(--clinova-warning-bg)",
              color: "var(--clinova-warning-text)",
              padding: "6px 16px",
              fontSize: "0.8125rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderTop: "1px solid var(--clinova-warning-border)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <AlertTriangle style={{ width: 16, height: 16 }} aria-hidden="true" />
              <span>Authentication session has expired. Please sign in again.</span>
            </div>
            <button
              onClick={() => setLoginModalOpen(true)}
              className="clinova-btn clinova-btn-outline"
              style={{ fontSize: "0.75rem", padding: "2px 8px" }}
            >
              Sign In
            </button>
          </div>
        )}

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div
            style={{
              padding: "12px 0 16px",
              borderTop: "1px solid var(--clinova-border)",
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: 600,
                    padding: "8px 12px",
                    borderRadius: "var(--clinova-radius-md)",
                    textDecoration: "none",
                    color: isActive(link.href)
                      ? "var(--clinova-accent-text)"
                      : "var(--clinova-text-primary)",
                    backgroundColor: isActive(link.href)
                      ? "var(--clinova-accent-light)"
                      : "transparent",
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Mobile Clinical Drawer Actions */}
            <div
              style={{
                borderTop: "1px solid var(--clinova-border)",
                paddingTop: 10,
                marginTop: 4,
                display: "flex",
                flexDirection: "column",
                gap: 6,
              }}
            >
              <span className="section-title" style={{ padding: "0 12px", marginBottom: 2 }}>
                Clinical Coordination
              </span>
              {onOpenReferralDrawer && (
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenReferralDrawer();
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ justifyContent: "flex-start", margin: "0 8px" }}
                >
                  <Share2 style={{ width: 15, height: 15, color: "var(--teal-600)" }} aria-hidden="true" />
                  <span>Referral Coordination</span>
                </button>
              )}
              {onOpenFacilityDrawer && (
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenFacilityDrawer();
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ justifyContent: "flex-start", margin: "0 8px" }}
                >
                  <Building2 style={{ width: 15, height: 15, color: "var(--info)" }} aria-hidden="true" />
                  <span>Facility Resources</span>
                </button>
              )}
              {onOpenSystemDrawer && (
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenSystemDrawer();
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ justifyContent: "flex-start", margin: "0 8px" }}
                >
                  <ShieldCheck style={{ width: 15, height: 15, color: "var(--success)" }} aria-hidden="true" />
                  <span>System Audit Ledger</span>
                </button>
              )}
            </div>

            {/* Mobile Persona Switcher */}
            <div
              style={{
                borderTop: "1px solid var(--clinova-border)",
                paddingTop: 10,
                marginTop: 4,
                padding: "8px 12px",
                display: "flex",
                flexDirection: "column",
                gap: 6,
              }}
            >
              <span className="section-title">
                {currentUser ? "Active Session" : "Demo Persona Quick Switch"}
              </span>
              {currentUser ? (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <RoleBadge role={currentUser.role} />
                    <span style={{ fontSize: "0.8125rem", fontWeight: 600 }}>{currentUser.full_name}</span>
                  </div>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      handleLogout();
                    }}
                    className="btn btn-danger btn-sm"
                  >
                    <LogOut style={{ width: 14, height: 14 }} aria-hidden="true" />
                    <span>Sign Out</span>
                  </button>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <select
                    aria-label="Mobile Demo Persona Quick Select"
                    value=""
                    onChange={(e) => {
                      if (e.target.value) {
                        setMobileMenuOpen(false);
                        handleRoleChange(e.target.value);
                      }
                    }}
                    className="select"
                    style={{ height: 36, fontSize: "0.8125rem" }}
                  >
                    <option value="" disabled>Select Demo Persona to Explore</option>
                    {personas.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.full_name} ({p.role})
                      </option>
                    ))}
                  </select>
                  <Link
                    href="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="btn btn-primary btn-block"
                    style={{ textDecoration: "none" }}
                  >
                    <LogIn style={{ width: 15, height: 15 }} aria-hidden="true" />
                    <span>Staff Sign In</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Lightweight Login Modal */}
      {loginModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="login-dialog-title"
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(15, 23, 42, 0.6)",
            backdropFilter: "blur(2px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
            padding: 16,
          }}
        >
          <div
            className="clinova-card"
            style={{
              maxWidth: 420,
              width: "100%",
              padding: "var(--clinova-space-6)",
              backgroundColor: "var(--clinova-surface)",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <ShieldCheck style={{ width: 20, height: 20, color: "var(--clinova-accent)" }} aria-hidden="true" />
                <h3 id="login-dialog-title" style={{ fontSize: "1.125rem", margin: 0 }}>
                  Staff Authentication
                </h3>
              </div>
              <button
                onClick={() => setLoginModalOpen(false)}
                className="clinova-icon-btn"
                aria-label="Close dialog"
              >
                <X style={{ width: 16, height: 16 }} aria-hidden="true" />
              </button>
            </div>

            {loginError && (
              <div
                style={{
                  backgroundColor: "var(--clinova-danger-bg)",
                  color: "var(--clinova-danger-text)",
                  border: "1px solid var(--clinova-danger-border)",
                  borderRadius: "var(--clinova-radius-md)",
                  padding: "8px 12px",
                  fontSize: "0.8125rem",
                  marginBottom: 12,
                }}
              >
                {loginError}
              </div>
            )}

            <form onSubmit={handleLoginSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <label style={{ fontSize: "0.75rem", fontWeight: 700, display: "block", marginBottom: 4 }}>
                  Username / Persona Identifier
                </label>
                <input
                  type="text"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  required
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: "var(--clinova-radius-md)",
                    border: "1px solid var(--clinova-border)",
                    fontSize: "0.875rem",
                    backgroundColor: "var(--clinova-surface)",
                    color: "var(--clinova-text-primary)",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.75rem", fontWeight: 700, display: "block", marginBottom: 4 }}>
                  Password
                </label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: "var(--clinova-radius-md)",
                    border: "1px solid var(--clinova-border)",
                    fontSize: "0.875rem",
                    backgroundColor: "var(--clinova-surface)",
                    color: "var(--clinova-text-primary)",
                  }}
                />
              </div>

              <div style={{ marginTop: 4, display: "flex", gap: 8 }}>
                <button
                  type="submit"
                  disabled={loginLoading}
                  className="clinova-btn clinova-btn-primary"
                  style={{ flex: 1 }}
                >
                  {loginLoading ? "Authenticating..." : "Sign In"}
                </button>
                <button
                  type="button"
                  onClick={() => setLoginModalOpen(false)}
                  className="clinova-btn clinova-btn-outline"
                >
                  Cancel
                </button>
              </div>

              <div style={{ marginTop: 8, borderTop: "1px solid var(--clinova-border)", paddingTop: 12 }}>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", display: "block", marginBottom: 6 }}>
                  Quick Demo Personas:
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {["clinician", "nurse", "receptionist", "referral", "facility_admin", "auditor", "sysadmin", "patient"].map((u) => (
                    <button
                      key={u}
                      type="button"
                      onClick={() => {
                        setLoginUsername(u);
                        setLoginPassword("ClinovaDemo2026!");
                      }}
                      style={{
                        fontSize: "0.6875rem",
                        padding: "2px 6px",
                        borderRadius: "var(--clinova-radius-sm)",
                        border: "1px solid var(--clinova-border-subtle)",
                        backgroundColor: "var(--clinova-surface-subtle)",
                        cursor: "pointer",
                      }}
                    >
                      {u}
                    </button>
                  ))}
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
};
