"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  X,
  LogOut,
  LogIn,
  Sparkles,
  Check,
  ChevronDown,
  Shield,
  Layers,
} from "lucide-react";
import { Persona } from "@/types";
import {
  getPersonas,
  getCurrentUser,
  getStoredUser,
  switchPersona,
  logout,
  FALLBACK_PERSONAS,
} from "@/lib/api";
import { RoleBadge } from "./RoleBadge";

export const FloatingPersonaSwitcher: React.FC = () => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [personas, setPersonas] = useState<Persona[]>(FALLBACK_PERSONAS);
  const [currentUser, setCurrentUser] = useState<Persona | null>(null);
  const [switchingId, setSwitchingId] = useState<string | null>(null);

  useEffect(() => {
    // 1. Hydrate user synchronously from storage
    const stored = getStoredUser();
    if (stored) {
      setCurrentUser(stored);
    }

    // 2. Fetch live session and personas
    async function loadData() {
      try {
        const u = await getCurrentUser();
        if (u) setCurrentUser(u);
        const plist = await getPersonas();
        if (plist && plist.length > 0) setPersonas(plist);
      } catch {
        // Fallbacks preserved
      }
    }
    loadData();

    // 3. Listen to auth changes and session expiry
    const handleAuthChange = (e: Event) => {
      const custom = e as CustomEvent<{ token: string | null; user: Persona | null }>;
      if (custom.detail && custom.detail.user !== undefined) {
        setCurrentUser(custom.detail.user);
      } else {
        loadData();
      }
    };

    const handleExpired = () => {
      setCurrentUser(null);
    };

    window.addEventListener("clinova_auth_changed", handleAuthChange);
    window.addEventListener("clinova_session_expired", handleExpired);

    return () => {
      window.removeEventListener("clinova_auth_changed", handleAuthChange);
      window.removeEventListener("clinova_session_expired", handleExpired);
    };
  }, []);

  const getRoleDestination = (role: string): string => {
    const r = role.toLowerCase();
    switch (r) {
      case "clinician":
      case "doctor":
        return "/staff/review";
      case "nurse":
        return "/staff/triage";
      case "receptionist":
        return "/staff/reception";
      case "facility_admin":
      case "facility administrator":
        return "/facilities";
      case "admin":
      case "system_admin":
      case "system administrator":
      case "auditor":
        return "/system";
      case "referral_coordinator":
      case "referral coordinator":
        return "/referrals";
      case "patient":
        return "/patient";
      default:
        return "/staff";
    }
  };

  const handleSelectPersona = async (persona: Persona) => {
    try {
      setSwitchingId(persona.id);
      const switched = await switchPersona(persona.id);
      setCurrentUser(switched);
      setIsOpen(false);
      const destination = getRoleDestination(switched.role);
      router.push(destination);
    } catch (err) {
      console.warn("Failed to switch persona:", err);
    } finally {
      setSwitchingId(null);
    }
  };

  const handleSignOut = async () => {
    try {
      await logout();
      setCurrentUser(null);
      setIsOpen(false);
      router.push("/");
    } catch (err) {
      console.warn("Logout error:", err);
    }
  };

  return (
    <div
      className="clinova-floating-persona-wrapper"
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        zIndex: 9999,
        fontFamily: "var(--font-sans, system-ui, sans-serif)",
      }}
    >
      {/* Expanded Popover Card */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Demo Persona Quick Switcher"
          aria-modal="false"
          className="clinova-floating-card"
          style={{
            position: "absolute",
            bottom: 56,
            right: 0,
            width: 360,
            maxWidth: "calc(100vw - 32px)",
            backgroundColor: "var(--clinova-surface, #ffffff)",
            color: "var(--clinova-text-primary, #0f172a)",
            border: "1px solid var(--clinova-border, #cbd5e1)",
            borderRadius: 12,
            boxShadow: "0 12px 36px -4px rgba(0, 0, 0, 0.18), 0 4px 12px rgba(0, 0, 0, 0.08)",
            padding: 16,
            display: "flex",
            flexDirection: "column",
            gap: 12,
            maxHeight: "min(560px, 85vh)",
            overflowY: "auto",
            animation: "clinovaFadeInUp 0.18s ease-out",
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderBottom: "1px solid var(--clinova-border, #e2e8f0)",
              paddingBottom: 10,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  backgroundColor: "rgba(15, 157, 145, 0.12)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--teal-600, #0f9d91)",
                }}
              >
                <Sparkles style={{ width: 16, height: 16 }} aria-hidden="true" />
              </div>
              <div>
                <h4 style={{ fontSize: "0.875rem", fontWeight: 700, margin: 0, lineHeight: 1.2 }}>
                  Demo Role Switcher
                </h4>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted, #64748b)" }}>
                  Evaluate clinical workflows across all 6 roles
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="clinova-icon-btn"
              title="Close persona switcher"
              aria-label="Close persona switcher"
              style={{
                width: 24,
                height: 24,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: 4,
                border: "none",
                background: "transparent",
                cursor: "pointer",
              }}
            >
              <X style={{ width: 16, height: 16 }} aria-hidden="true" />
            </button>
          </div>

          {/* Active Session Status */}
          <div
            style={{
              backgroundColor: "var(--clinova-surface-subtle, #f8fafc)",
              border: "1px solid var(--clinova-border-subtle, #e2e8f0)",
              borderRadius: 8,
              padding: "10px 12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 8,
            }}
          >
            {currentUser ? (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
                  <span style={{ fontSize: "0.6875rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--clinova-text-muted, #64748b)", fontWeight: 700 }}>
                    Active Session
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ fontSize: "0.8125rem", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {currentUser.full_name}
                    </span>
                    <RoleBadge role={currentUser.role} />
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleSignOut}
                  className="btn btn-outline btn-sm"
                  title="Sign out of current persona"
                  style={{
                    padding: "4px 8px",
                    fontSize: "0.6875rem",
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                    color: "var(--clinova-danger, #ef4444)",
                    borderColor: "var(--clinova-danger, #ef4444)",
                    flexShrink: 0,
                  }}
                >
                  <LogOut style={{ width: 12, height: 12 }} aria-hidden="true" />
                  <span>Sign Out</span>
                </button>
              </>
            ) : (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary, #475569)" }}>
                  No active session • Select a role below
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setIsOpen(false);
                    router.push("/login");
                  }}
                  className="btn btn-primary btn-sm"
                  style={{ padding: "4px 8px", fontSize: "0.6875rem", display: "flex", alignItems: "center", gap: 4 }}
                >
                  <LogIn style={{ width: 12, height: 12 }} aria-hidden="true" />
                  <span>Login</span>
                </button>
              </div>
            )}
          </div>

          {/* Persona List Grid */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span
              style={{
                fontSize: "0.6875rem",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--clinova-text-muted, #64748b)",
                fontWeight: 700,
                padding: "0 2px",
              }}
            >
              Select Persona to Activate
            </span>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {personas.map((p) => {
                const isSelected = currentUser?.id === p.id;
                const isBusy = switchingId === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => handleSelectPersona(p)}
                    disabled={isBusy}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: 10,
                      padding: "8px 10px",
                      borderRadius: 8,
                      border: isSelected
                        ? "1.5px solid var(--teal-600, #0f9d91)"
                        : "1px solid var(--clinova-border, #e2e8f0)",
                      backgroundColor: isSelected
                        ? "rgba(15, 157, 145, 0.08)"
                        : "var(--clinova-surface, #ffffff)",
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.15s ease",
                    }}
                    className="clinova-persona-option-btn"
                  >
                    <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                        <span style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--clinova-text-primary, #0f172a)" }}>
                          {p.full_name}
                        </span>
                        <RoleBadge role={p.role} />
                      </div>
                      <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-secondary, #64748b)" }}>
                        {p.facility_name || p.email}
                      </span>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 4, flexShrink: 0 }}>
                      {isSelected ? (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 3,
                            fontSize: "0.6875rem",
                            fontWeight: 700,
                            color: "var(--teal-600, #0f9d91)",
                          }}
                        >
                          <Check style={{ width: 14, height: 14 }} aria-hidden="true" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted, #94a3b8)" }}>
                          {isBusy ? "Activating..." : "Switch →"}
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Footer note */}
          <div
            style={{
              borderTop: "1px solid var(--clinova-border-subtle, #e2e8f0)",
              paddingTop: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: "0.6875rem",
              color: "var(--clinova-text-muted, #64748b)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <Shield style={{ width: 12, height: 12, color: "var(--teal-600, #0f9d91)" }} aria-hidden="true" />
              <span>Synthetic DPDP-Isolated Sandbox</span>
            </div>
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                router.push("/login");
              }}
              style={{
                background: "none",
                border: "none",
                color: "var(--teal-600, #0f9d91)",
                fontWeight: 600,
                fontSize: "0.6875rem",
                cursor: "pointer",
                padding: 0,
                textDecoration: "underline",
              }}
            >
              Staff Login Credentials
            </button>
          </div>
        </div>
      )}

      {/* Floating Trigger Pill */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label="Toggle demo persona quick switch menu"
        className="clinova-floating-trigger-btn"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 14px",
          borderRadius: 9999,
          backgroundColor: currentUser
            ? "var(--clinova-surface, #ffffff)"
            : "var(--clinova-primary, #0f9d91)",
          color: currentUser
            ? "var(--clinova-text-primary, #0f172a)"
            : "#ffffff",
          border: currentUser
            ? "1.5px solid var(--clinova-border, #cbd5e1)"
            : "1.5px solid var(--teal-600, #0f9d91)",
          boxShadow: "0 6px 20px -2px rgba(0, 0, 0, 0.16), 0 2px 6px rgba(0, 0, 0, 0.08)",
          cursor: "pointer",
          fontWeight: 600,
          fontSize: "0.8125rem",
          transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
          transform: isOpen ? "scale(1.02)" : "scale(1)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 22,
            height: 22,
            borderRadius: "50%",
            backgroundColor: currentUser
              ? "rgba(15, 157, 145, 0.12)"
              : "rgba(255, 255, 255, 0.22)",
            color: currentUser ? "var(--teal-600, #0f9d91)" : "#ffffff",
          }}
        >
          {currentUser ? (
            <Users style={{ width: 13, height: 13 }} aria-hidden="true" />
          ) : (
            <Sparkles style={{ width: 13, height: 13 }} aria-hidden="true" />
          )}
        </div>

        {currentUser ? (
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ maxWidth: 120, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {currentUser.full_name}
            </span>
            <RoleBadge role={currentUser.role} />
          </div>
        ) : (
          <span style={{ whiteSpace: "nowrap" }}>Demo Personas</span>
        )}

        <div
          style={{
            width: 18,
            height: 18,
            borderRadius: "50%",
            backgroundColor: currentUser
              ? "var(--clinova-surface-subtle, #f1f5f9)"
              : "rgba(0, 0, 0, 0.18)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "0.625rem",
            fontWeight: 700,
          }}
        >
          {personas.length}
        </div>

        <ChevronDown
          style={{
            width: 14,
            height: 14,
            transition: "transform 0.2s ease",
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
          }}
          aria-hidden="true"
        />
      </button>
    </div>
  );
};
