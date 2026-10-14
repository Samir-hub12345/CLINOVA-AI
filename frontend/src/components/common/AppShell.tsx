"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  FlaskConical,
  Clock,
  CheckSquare,
  Sparkles,
  BarChart3,
  Shield,
  Settings as SettingsIcon,
  Stethoscope,
  UserCheck,
  UserPlus,
  Building2,
  Share2,
  Menu,
  X,
  Search,
  Bell,
  HelpCircle,
  LogOut,
  ChevronDown,
  ShieldAlert,
  Server,
  HeartPulse,
  Layers,
  Activity,
} from "lucide-react";
import { useClinova, ClinovaProvider } from "@/lib/referenceContext";
import { EnvironmentBanner } from "./EnvironmentBanner";
import { DemoBanner } from "./DemoBanner";
import { Footer } from "./Footer";
import { LandingHeader } from "@/components/landing/LandingHeader";
import { ReferralDrawer } from "@/components/drawers/ReferralDrawer";
import { FacilityDrawer } from "@/components/drawers/FacilityDrawer";
import { SystemAuditDrawer } from "@/components/drawers/SystemAuditDrawer";
import { FloatingPersonaSwitcher } from "./FloatingPersonaSwitcher";
import { RoleBadge } from "./RoleBadge";
import { ConnectionStatus } from "./ConnectionStatus";
import { AskClinovaDrawer } from "./AskClinovaDrawer";
import { RoleChooserModal } from "@/components/dashboard/RoleChooserModal";

interface AppShellProps {
  children: React.ReactNode;
  activeCaseId?: string;
}

const InnerAppShell: React.FC<AppShellProps> = ({
  children,
  activeCaseId = "CASE-SYNTH-003",
}) => {
  const pathname = usePathname();
  const router = useRouter();
  const {
    user,
    reviews,
    followUps,
    notifications,
    toasts,
    removeToast,
    dismissNotification,
    signOut,
    switchRole,
    can,
  } = useClinova();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notifMenuOpen, setNotifMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isReferralOpen, setIsReferralOpen] = useState(false);
  const [isFacilityOpen, setIsFacilityOpen] = useState(false);
  const [isSystemOpen, setIsSystemOpen] = useState(false);
  const [isAskOpen, setIsAskOpen] = useState(false);
  const [isRoleChooserOpen, setIsRoleChooserOpen] = useState(false);

  // Close menus on route change
  useEffect(() => {
    setSidebarOpen(false);
    setUserMenuOpen(false);
    setNotifMenuOpen(false);
  }, [pathname]);

  const pendingReviewsCount = reviews.filter((r) => r.status === "pending").length;
  const pendingFollowUpsCount = followUps.filter(
    (f) => f.status === "Due today" || f.status === "Contact attempted"
  ).length;
  const unreadNotifsCount = notifications.filter((n) => !n.read).length;

  const isPublicRoute =
    pathname === "/" ||
    pathname === "/login" ||
    pathname === "/signin" ||
    pathname === "/register" ||
    pathname === "/about" ||
    pathname === "/disclaimer" ||
    pathname === "/privacy";

  // If unauthenticated or viewing public landing page/auth, render clean public layout
  const showSidebar = !isPublicRoute || (user && pathname !== "/login" && pathname !== "/signin");

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  const userRole = (user?.role || "CLINICIAN").toUpperCase();

  // Role-specific brand and navigation mapping according to Sections 4-9
  let brandName = { main: "Clinova", sub: "AI" };
  let navSections: { title: string; items: { label: string; href: string; icon: any; count?: number }[] }[] = [];

  if (userRole === "PATIENT") {
    brandName = { main: "HealthCare+", sub: "Portal" };
    navSections = [
      {
        title: "Patient Navigation",
        items: [
          { label: "Dashboard", href: "/patient", icon: LayoutDashboard },
          { label: "My Records", href: "/patient?tab=records", icon: FileText },
          { label: "Appointments", href: "/patient?tab=appointments", icon: Calendar },
          { label: "Reports", href: "/patient?tab=reports", icon: BarChart3 },
          { label: "Messages", href: "/patient?tab=messages", icon: Sparkles },
          { label: "Follow-up", href: "/patient?tab=followup", icon: Clock },
          { label: "Profile", href: "/patient?tab=profile", icon: Users },
        ],
      },
    ];
  } else if (userRole === "RECEPTIONIST") {
    brandName = { main: "HTN", sub: "Reception" };
    navSections = [
      {
        title: "Receptionist Navigation",
        items: [
          { label: "Dashboard", href: "/staff/reception", icon: LayoutDashboard },
          { label: "Patient Registration", href: "/staff/reception?tab=register", icon: UserPlus },
          { label: "Appointments", href: "/staff/reception?tab=schedule", icon: Calendar },
          { label: "Check-in", href: "/staff/reception?tab=checkin", icon: CheckSquare },
          { label: "Patient Queue", href: "/staff/reception?tab=queue", icon: Users },
          { label: "Patient Lookup", href: "/staff/reception?tab=lookup", icon: Search },
          { label: "Notifications", href: "/staff/reception?tab=notifications", icon: Bell },
        ],
      },
    ];
  } else if (userRole === "NURSE") {
    brandName = { main: "MediWatch", sub: "Triage" };
    navSections = [
      {
        title: "Nurse Navigation",
        items: [
          { label: "Dashboard", href: "/staff/triage", icon: LayoutDashboard },
          { label: "Assigned Queue", href: "/staff/triage?tab=queue", icon: Users },
          { label: "Patient Intake", href: "/patient/intake", icon: FileText },
          { label: "Vital Signs", href: "/staff/triage?tab=vitals", icon: HeartPulse },
          { label: "Evidence Upload", href: "/staff/triage?tab=evidence", icon: Sparkles },
          { label: "Patient Timeline", href: "/staff/triage?tab=timeline", icon: Clock },
          { label: "Tasks", href: "/staff/triage?tab=tasks", icon: CheckSquare },
          { label: "Handover", href: "/staff/triage?tab=handover", icon: Share2 },
        ],
      },
    ];
  } else if (userRole === "FACILITY_ADMIN") {
    brandName = { main: "Operations", sub: "& Resource" };
    navSections = [
      {
        title: "Facility Management",
        items: [
          { label: "Dashboard", href: "/facilities", icon: LayoutDashboard },
          { label: "Facility Management", href: "/facilities?tab=management", icon: Building2 },
          { label: "Staff Management", href: "/facilities?tab=staff", icon: Users },
          { label: "Service Capacity", href: "/facilities?tab=capacity", icon: HeartPulse },
          { label: "Resource Planning", href: "/facilities?tab=resources", icon: LayoutDashboard },
          { label: "Analytics", href: "/facilities?tab=analytics", icon: BarChart3 },
          { label: "Reports", href: "/facilities?tab=reports", icon: FileText },
          { label: "Settings", href: "/settings", icon: SettingsIcon },
        ],
      },
    ];
  } else if (userRole === "SYSTEM_ADMIN" || userRole === "AUDITOR") {
    brandName = { main: "CLINOVA", sub: "Admin" };
    navSections = [
      {
        title: "Platform Administration",
        items: [
          { label: "Dashboard", href: "/system", icon: LayoutDashboard },
          { label: "User Management", href: "/system?tab=users", icon: Users },
          { label: "Role Management", href: "/system?tab=roles", icon: Shield },
          { label: "Facility Directory", href: "/facilities", icon: Building2 },
          { label: "System Analytics", href: "/system?tab=analytics", icon: BarChart3 },
          { label: "AI Model Status", href: "/system?tab=models", icon: Sparkles },
          { label: "Audit Logs", href: "/audit", icon: ShieldAlert },
          { label: "System Health", href: "/system?tab=health", icon: Server },
          { label: "Security", href: "/system?tab=security", icon: Shield },
          { label: "Settings", href: "/settings", icon: SettingsIcon },
        ],
      },
    ];
  } else {
    // Clinician / Medical Officer
    brandName = { main: "Clinova", sub: "Doctor" };
    navSections = [
      {
        title: "Clinical Navigation",
        items: [
          { label: "Dashboard", href: "/", icon: LayoutDashboard },
          { label: "Patient Review", href: "/staff/review", icon: CheckSquare, count: pendingReviewsCount > 0 ? pendingReviewsCount : undefined },
          { label: "Clinical Cases", href: "/staff/cases/CASE-SYNTH-003", icon: Stethoscope },
          { label: "AI Insights", href: "/assistant", icon: Sparkles },
          { label: "CAREGRAPH", href: "/review?tab=caregraph", icon: Activity },
          { label: "Safety Alerts", href: "/review?tab=safety", icon: ShieldAlert },
          { label: "Referrals", href: "/referrals", icon: Share2 },
          { label: "Reports", href: "/reports", icon: BarChart3 },
          { label: "Follow-up", href: "/follow-ups", icon: Clock, count: pendingFollowUpsCount > 0 ? pendingFollowUpsCount : undefined },
        ],
      },
    ];
  }

  const mobileNavItems = [
    { label: "Today", href: "/", icon: LayoutDashboard },
    { label: "Patients", href: "/patients", icon: Users },
    { label: "Schedule", href: "/appointments", icon: Calendar },
    { label: "Review", href: "/review", icon: CheckSquare },
    { label: "Follow-ups", href: "/follow-ups", icon: Clock },
  ];

  return (
    <div className="clinova-shell-wrapper">
      {/* 1. Operational Environment Indicator */}
      <EnvironmentBanner />

      {/* 2. Mandatory Synthetic / Demo Safety Banner */}
      <DemoBanner />

      {showSidebar ? (
        <div className="shell">
          <a href="#main" className="skip-link">
            Skip to main content
          </a>

          {/* Reference Sidebar */}
          <aside className={`sidebar ${sidebarOpen ? "open" : ""}`} aria-label="Primary Navigation">
            <div className="row between">
              <Link href="/" className="brand" onClick={() => setSidebarOpen(false)}>
                <span className="brand-mark" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 16 16">
                    <path d="M8 2v12M2 8h12" stroke="#5fd3c7" strokeWidth="3" strokeLinecap="round" />
                  </svg>
                </span>
                <span className="brand-name">
                  {brandName.main} <span>{brandName.sub}</span>
                </span>
              </Link>
              <button
                className="btn btn-ghost btn-icon btn-sm mobile-only-btn"
                style={{ color: "#c6d3e1" }}
                onClick={() => setSidebarOpen(false)}
                aria-label="Close navigation"
              >
                <X style={{ width: 18, height: 18 }} />
              </button>
            </div>

            <nav className="stack gap-1" style={{ marginTop: 8 }}>
              {navSections.map((sec, sIdx) => (
                <React.Fragment key={sIdx}>
                  <div className="nav-section">{sec.title}</div>
                  {sec.items.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={`nav-link ${active ? "active" : ""}`}
                        onClick={() => setSidebarOpen(false)}
                      >
                        <Icon style={{ width: 18, height: 18 }} aria-hidden="true" />
                        <span>{item.label}</span>
                        {item.count !== undefined && <span className="nav-count">{item.count}</span>}
                      </Link>
                    );
                  })}
                </React.Fragment>
              ))}
            </nav>

            <div className="sidebar-foot">
              <div className="row gap-2">
                <ShieldAlert style={{ width: 14, height: 14, color: "#5fd3c7" }} aria-hidden="true" />
                <span>Demo mode · synthetic data only</span>
              </div>
              <div style={{ color: "#6f86a0" }}>Lekki Family Health Clinic • FAC-DH-04</div>
            </div>
          </aside>

          {/* Sidebar mobile overlay */}
          {sidebarOpen && (
            <div
              className="overlay"
              style={{ zIndex: 65 }}
              onClick={() => setSidebarOpen(false)}
              aria-hidden="true"
            />
          )}

          {/* Main Column */}
          <div className="main-col">
            {/* Reference Sticky TopBar */}
            <header className="topbar">
              <button
                className="icon-btn mobile-only-btn"
                onClick={() => setSidebarOpen(true)}
                aria-label="Open navigation"
              >
                <Menu style={{ width: 18, height: 18 }} />
              </button>

              <button
                className="workspace-switch hide-mobile"
                aria-label="Current workspace: Lekki Family Health Clinic"
                onClick={() => setIsRoleChooserOpen(true)}
              >
                <span className="ws-mark">LF</span>
                <span className="ws-text stack">
                  <span className="small medium">Lekki Family Health Clinic</span>
                  <span className="xs muted">Outpatient workspace</span>
                </span>
                <ChevronDown style={{ width: 14, height: 14, color: "var(--text-3)" }} aria-hidden="true" />
              </button>

              {/* Global Search Bar */}
              <div className="global-search hide-mobile">
                <div className="input-group">
                  <Search style={{ width: 16, height: 16 }} aria-hidden="true" />
                  <input
                    type="search"
                    className="input"
                    placeholder="Search patients, charts, encounters… (Press ⌘K)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && searchQuery.trim()) {
                        router.push(`/patients?q=${encodeURIComponent(searchQuery)}`);
                      }
                    }}
                  />
                  <span className="kbd">⌘K</span>
                </div>
              </div>

              {/* Actions & Session Controls */}
              <div className="row gap-2" style={{ marginLeft: "auto" }}>
                <div className="hide-mobile">
                  <ConnectionStatus status="ONLINE" />
                </div>

                <button
                  type="button"
                  className="btn btn-secondary btn-sm hide-mobile"
                  onClick={() => setIsAskOpen(true)}
                >
                  <Sparkles style={{ width: 14, height: 14, color: "var(--teal-600)" }} />
                  <span>Ask Clinova</span>
                </button>

                {/* Notifications Bell */}
                <div style={{ position: "relative" }}>
                  <button
                    className="icon-btn"
                    onClick={() => setNotifMenuOpen(!notifMenuOpen)}
                    aria-label="Notifications"
                    title="Notifications"
                  >
                    <Bell style={{ width: 18, height: 18 }} />
                    {unreadNotifsCount > 0 && <span className="pip" />}
                  </button>

                  {notifMenuOpen && (
                    <div
                      className="popover"
                      style={{ right: 0, width: 320, padding: 12, top: "calc(100% + 8px)" }}
                    >
                      <div className="row between" style={{ marginBottom: 8 }}>
                        <span className="strong small">Clinical Notifications</span>
                        <span className="xs muted">{unreadNotifsCount} new</span>
                      </div>
                      <div className="stack gap-2" style={{ maxHeight: 280, overflowY: "auto" }}>
                        {notifications.map((n) => (
                          <div
                            key={n.id}
                            style={{
                              padding: "8px 10px",
                              borderRadius: 6,
                              background: n.read ? "transparent" : "var(--navy-50)",
                              cursor: "pointer",
                            }}
                            onClick={() => {
                              dismissNotification(n.id);
                              router.push(n.to);
                              setNotifMenuOpen(false);
                            }}
                          >
                            <div className="small medium">{n.title}</div>
                            <div className="xs subtle">{n.body}</div>
                            <div className="xs muted" style={{ marginTop: 2 }}>
                              {n.at}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <Link
                  href="/assistant?tab=help"
                  className="icon-btn hide-mobile"
                  aria-label="Help"
                  title="Documentation & Help"
                >
                  <HelpCircle style={{ width: 18, height: 18 }} />
                </Link>

                {/* User Profile Menu */}
                {user ? (
                  <div style={{ position: "relative" }}>
                    <button
                      className="user-btn"
                      onClick={() => setUserMenuOpen(!userMenuOpen)}
                      aria-expanded={userMenuOpen}
                    >
                      <span className="avatar sm">
                        {user.full_name
                          .split(" ")
                          .map((n) => n[0])
                          .slice(0, 2)
                          .join("")}
                      </span>
                      <span className="small medium hide-mobile" style={{ maxWidth: 120 }}>
                        {user.full_name}
                      </span>
                      <RoleBadge role={user.role} />
                      <ChevronDown style={{ width: 14, height: 14, color: "var(--text-3)" }} />
                    </button>

                    {userMenuOpen && (
                      <div
                        className="popover"
                        style={{ right: 0, width: 220, top: "calc(100% + 8px)" }}
                      >
                        <div className="menu-label">Active Session</div>
                        <div style={{ padding: "6px 10px" }}>
                          <div className="small strong">{user.full_name}</div>
                          <div className="xs muted">{user.role}</div>
                        </div>
                        <hr className="divider" />
                        <button
                          role="menuitem"
                          className="menu-item"
                          onClick={() => {
                            setUserMenuOpen(false);
                            setIsRoleChooserOpen(true);
                          }}
                        >
                          <Layers style={{ width: 16, height: 16 }} />
                          <span>Switch Role / Facility</span>
                        </button>
                        <button
                          role="menuitem"
                          className="menu-item"
                          onClick={() => {
                            setUserMenuOpen(false);
                            router.push("/settings");
                          }}
                        >
                          <SettingsIcon style={{ width: 16, height: 16 }} />
                          <span>Workspace Settings</span>
                        </button>
                        <button
                          role="menuitem"
                          className="menu-item"
                          onClick={async () => {
                            setUserMenuOpen(false);
                            await signOut();
                            router.push("/login");
                          }}
                        >
                          <LogOut style={{ width: 16, height: 16, color: "var(--error)" }} />
                          <span style={{ color: "var(--error)" }}>Sign out</span>
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <Link href="/login" className="btn btn-primary btn-sm">
                    <span>Sign In</span>
                  </Link>
                )}
              </div>
            </header>

            {/* Main Application Body */}
            <main id="main" tabIndex={-1} style={{ outline: "none", minHeight: "calc(100vh - 120px)" }}>
              {children}
            </main>

            {/* Mobile Bottom Navigation */}
            <nav className="mobile-nav" aria-label="Mobile Navigation">
              {mobileNavItems.map((m) => {
                const Icon = m.icon;
                const active = isActive(m.href);
                return (
                  <Link key={m.href} href={m.href} className={active ? "active" : ""}>
                    <Icon style={{ width: 20, height: 20 }} />
                    <span>{m.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      ) : (
        /* Public Pages (Landing, Auth, Static) */
        <div className="clinova-public-shell">
          <LandingHeader />
          <main className={pathname === "/" ? "clinova-landing-main" : "clinova-main"}>
            {pathname === "/" ? children : <div className="clinova-container">{children}</div>}
          </main>
          <Footer />
        </div>
      )}

      {/* Floating Drawers */}
      <ReferralDrawer
        isOpen={isReferralOpen}
        onClose={() => setIsReferralOpen(false)}
        caseId={activeCaseId}
      />
      <FacilityDrawer isOpen={isFacilityOpen} onClose={() => setIsFacilityOpen(false)} />
      <SystemAuditDrawer isOpen={isSystemOpen} onClose={() => setIsSystemOpen(false)} />
      <AskClinovaDrawer isOpen={isAskOpen} onClose={() => setIsAskOpen(false)} />
      <RoleChooserModal isOpen={isRoleChooserOpen} onClose={() => setIsRoleChooserOpen(false)} />

      {/* Floating Demo Persona Switcher (Fixed Bottom-Right) */}
      <FloatingPersonaSwitcher />

      {/* Toast Notification Deck */}
      {toasts.length > 0 && (
        <div className="toasts" role="region" aria-label="Notifications">
          {toasts.map((t) => (
            <div key={t.id} className="toast" onClick={() => removeToast(t.id)} style={{ cursor: "pointer" }}>
              <Sparkles style={{ width: 18, height: 18, color: "#5fd3c7" }} />
              <div>
                <strong style={{ display: "block" }}>{t.title}</strong>
                {t.desc && <div className="toast-desc">{t.desc}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const AppShell: React.FC<AppShellProps> = (props) => {
  return (
    <ClinovaProvider>
      <InnerAppShell {...props} />
    </ClinovaProvider>
  );
};
