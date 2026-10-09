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
import { getPersonas, getCurrentUser, switchPersona, login, logout } from "@/lib/api";
import { RoleBadge } from "./RoleBadge";
import { ConnectionStatus } from "./ConnectionStatus";

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
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [currentUser, setCurrentUser] = useState<Persona | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [loginUsername, setLoginUsername] = useState("clinician");
  const [loginPassword, setLoginPassword] = useState("ClinovaDemo2026!");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    async function initUser() {
      try {
        const [u, plist] = await Promise.all([getCurrentUser(), getPersonas()]);
        setCurrentUser(u);
        setPersonas(plist);
      } catch {
        // Handled by resilient fallback
      }
    }
    initUser();

    const handleExpired = () => {
      setSessionExpired(true);
      setCurrentUser(null);
    };

    const handleAuthChange = () => {
      setSessionExpired(false);
      initUser();
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
          {/* Brand Identity */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <Link
              href="/"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                textDecoration: "none",
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "var(--clinova-radius-md)",
                  border: "1px solid var(--clinova-border)",
                  backgroundColor: "var(--clinova-surface-subtle)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  overflow: "hidden",
                }}
              >
                <Image
                  src="/branding/clinova-ai-mark.png"
                  alt="CLINOVA AI Logo"
                  width={28}
                  height={28}
                  style={{ objectFit: "contain" }}
                />
              </div>
              <div>
                <span
                  style={{
                    fontSize: "1.0625rem",
                    fontWeight: 800,
                    color: "var(--clinova-text-primary)",
                    letterSpacing: "-0.02em",
                    display: "block",
                    lineHeight: 1.1,
                  }}
                >
                  CLINOVA AI
                </span>
                <span
                  style={{
                    fontSize: "0.625rem",
                    color: "var(--clinova-accent)",
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    display: "block",
                  }}
                >
                  Continuous Care Intelligence
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <nav
              aria-label="Main Navigation"
              style={{
                display: "none",
                alignItems: "center",
                gap: 4,
                marginLeft: 12,
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
                    padding: "6px 12px",
                    borderRadius: "var(--clinova-radius-md)",
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
          </div>

          {/* Operational Status, Role Switcher & Drawer Triggers */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {/* Connection Status Indicator */}
            <div className="clinova-desktop-item">
              <ConnectionStatus status="ONLINE" />
            </div>

            {/* Quick Drawer Action Toggles */}
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              {onOpenReferralDrawer && (
                <button
                  onClick={onOpenReferralDrawer}
                  className="clinova-icon-btn"
                  title="Open Referral Coordination Drawer"
                  aria-label="Open Referral Coordination Drawer"
                >
                  <Share2 style={{ width: 15, height: 15 }} aria-hidden="true" />
                </button>
              )}
              {onOpenFacilityDrawer && (
                <button
                  onClick={onOpenFacilityDrawer}
                  className="clinova-icon-btn"
                  title="Open Facility Resources Drawer"
                  aria-label="Open Facility Resources Drawer"
                >
                  <Building2 style={{ width: 15, height: 15 }} aria-hidden="true" />
                </button>
              )}
              {onOpenSystemDrawer && (
                <button
                  onClick={onOpenSystemDrawer}
                  className="clinova-icon-btn"
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
                  <div className="clinova-desktop-item">
                    <RoleBadge role={currentUser.role} />
                  </div>
                  <select
                    aria-label="Select Active Clinical Role"
                    value={currentUser.id}
                    onChange={(e) => handleRoleChange(e.target.value)}
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      padding: "4px 8px",
                      borderRadius: "var(--clinova-radius-md)",
                      border: "1px solid var(--clinova-border-subtle)",
                      backgroundColor: "var(--clinova-surface)",
                      color: "var(--clinova-text-primary)",
                      cursor: "pointer",
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
                <button
                  onClick={() => setLoginModalOpen(true)}
                  className="clinova-btn clinova-btn-primary"
                  style={{ fontSize: "0.75rem", padding: "4px 10px", display: "flex", alignItems: "center", gap: 6 }}
                >
                  <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
                  <span>Sign In</span>
                </button>
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
              gap: 6,
            }}
          >
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
                  {["clinician", "nurse", "referral", "facility_admin", "auditor", "sysadmin", "patient"].map((u) => (
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
