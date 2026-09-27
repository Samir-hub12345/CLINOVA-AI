"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ClipboardList,
  Stethoscope,
  Users,
  Calendar,
  FileText,
  FileClock,
  UserRound,
  LogOut,
  Search,
  Bell,
  Menu,
  X,
  RefreshCw,
  Plus,
  CheckSquare,
  ClipboardPlus,
  UserPlus,
  GitFork,
  Building2,
  AlertCircle,
  Clock,
  Sparkles,
  Command,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { MetricCard, MetricCardProps } from "./metric-card";
import { SectionCard, SectionCardProps } from "./section-card";
import { NetworkIndicator } from "./network-indicator";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export { MetricCard, SectionCard };
export type { MetricCardProps, SectionCardProps };

interface NavLinkItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const roleNavigation: Record<string, NavLinkItem[]> = {
  patient: [
    { label: "My Dashboard", href: "/dashboard/patient", icon: LayoutDashboard },
    { label: "Start Intake", href: "/intake", icon: ClipboardList, badge: "New" },
    { label: "Consultations", href: "/consultations", icon: Calendar },
    { label: "Lab Documents", href: "/documents", icon: FileText },
    { label: "Medical Profile", href: "/portal/profile", icon: UserRound },
  ],
  doctor: [
    { label: "Clinical Workspace", href: "/dashboard/doctor", icon: LayoutDashboard },
    { label: "Review Queue", href: "/review", icon: CheckSquare, badge: "Live" },
    { label: "Patient Directory", href: "/patients", icon: Users },
    { label: "Consultations", href: "/consultations", icon: Stethoscope },
    { label: "Clinical Records", href: "/documents", icon: FileText },
  ],
  nurse: [
    { label: "Nurse Station", href: "/dashboard/nurse", icon: LayoutDashboard },
    { label: "Patient Intake", href: "/intake", icon: ClipboardPlus },
    { label: "Review Queue", href: "/review", icon: CheckSquare },
    { label: "Patient Directory", href: "/patients", icon: Users },
    { label: "Front Desk Console", href: "/dashboard/staff", icon: Building2 },
    { label: "Clinical Records", href: "/documents", icon: FileText },
  ],
  staff: [
    { label: "Front Desk Console", href: "/dashboard/staff", icon: LayoutDashboard },
    { label: "Patient Registration", href: "/intake", icon: UserPlus },
    { label: "Review & Routing", href: "/review", icon: GitFork },
    { label: "Patient Directory", href: "/patients", icon: Users },
    { label: "Nurse Station", href: "/dashboard/nurse", icon: Stethoscope },
    { label: "Documents", href: "/documents", icon: FileText },
  ],
  admin: [
    { label: "Admin Console", href: "/dashboard/admin", icon: LayoutDashboard },
    { label: "Audit Trail", href: "/audit", icon: FileClock },
    { label: "System Documents", href: "/documents", icon: FileText },
  ],
};

const quickActionsByRole: Record<
  string,
  { label: string; href: string; icon: React.ComponentType<{ className?: string }> }
> = {
  patient: { label: "+ New Intake", href: "/intake", icon: Plus },
  doctor: { label: "Review Queue", href: "/review", icon: CheckSquare },
  nurse: { label: "+ New Intake", href: "/intake", icon: Plus },
  staff: { label: "+ Register Patient", href: "/intake", icon: UserPlus },
  admin: { label: "Audit Trail", href: "/audit", icon: FileClock },
};

export interface DashboardShellProps {
  title: string;
  description: string;
  children: React.ReactNode;
  refresh?: () => void;
  actions?: React.ReactNode;
  badge?: string;
}

export function DashboardShell({
  title,
  description,
  children,
  refresh,
  actions,
  badge,
}: DashboardShellProps) {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchFocused, setSearchFocused] = useState(false);
  const [currentDateString, setCurrentDateString] = useState("");

  // Role resolution
  const roleKey = user?.role || "patient";
  const navItems = roleNavigation[roleKey] || roleNavigation.patient;
  const quickAction = quickActionsByRole[roleKey] || quickActionsByRole.patient;

  // Format date display
  useEffect(() => {
    const now = new Date();
    const options: Intl.DateTimeFormatOptions = {
      weekday: "long",
      year: "numeric",
      month: "short",
      day: "numeric",
    };
    setCurrentDateString(now.toLocaleDateString("en-US", options));
  }, []);

  // Keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        const input = document.getElementById("clinova-global-search") as HTMLInputElement;
        if (input) {
          input.focus();
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [pathname]);

  const initials = (user?.full_name || user?.email || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const roleBadgeText =
    user?.role === "doctor"
      ? "Physician"
      : user?.role === "nurse"
      ? "Staff Nurse"
      : user?.role === "admin"
      ? "Administrator"
      : user?.role === "staff"
      ? "Front Desk Staff"
      : "Patient";

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row antialiased font-sans">
      {/* ========================================================================= */}
      {/* 1. DARK NAVY SIDEBAR (Desktop & Off-canvas Mobile Drawer)                */}
      {/* ========================================================================= */}
      {/* Mobile Backdrop */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-xs md:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-slate-900 text-slate-200 transition-transform duration-300 ease-in-out md:static md:translate-x-0 ${
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-20 items-center justify-between border-b border-slate-800/80 px-6">
          <ClinovaLogo
            href="/"
            variant="full"
            size="md"
            theme="dark"
            showTagline={true}
            taglineText="Clinical Suite"
          />

          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="md:hidden text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Workspace Indicator */}
        <div className="px-6 py-4 border-b border-slate-800/50">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold tracking-wider uppercase text-slate-400">
              Workspace
            </span>
            <span className="inline-flex items-center gap-1.5 text-[11px] text-teal-400 font-medium bg-teal-950/80 px-2 py-0.5 rounded-full border border-teal-800/60">
              <span className="h-1.5 w-1.5 rounded-full bg-teal-400 animate-pulse" />
              {roleBadgeText}
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-1.5 overflow-y-auto px-4 py-5" aria-label="Sidebar Navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href + "/"));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`group flex items-center justify-between rounded-xl px-3.5 py-3 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-teal-500/15 text-teal-300 font-semibold shadow-xs border-l-4 border-teal-400"
                    : "text-slate-400 hover:bg-slate-800/70 hover:text-slate-100"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-5 w-5 transition-colors ${
                      isActive ? "text-teal-400" : "text-slate-400 group-hover:text-slate-200"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      isActive
                        ? "bg-teal-400 text-slate-900"
                        : "bg-slate-800 text-slate-400 border border-slate-700"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer User Card */}
        <div className="border-t border-slate-800/90 p-4">
          <div className="flex items-center justify-between rounded-xl bg-slate-800/60 p-3 border border-slate-700/60">
            <div className="flex items-center gap-3 min-w-0">
              <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-900/60 text-teal-300 font-bold text-sm border border-teal-700/50 shadow-inner">
                {initials}
                <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-emerald-500 border-2 border-slate-900" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-bold text-slate-100">
                  {user?.full_name || "Clinova User"}
                </p>
                <p className="truncate text-[11px] text-slate-400">
                  {user?.email || "user@clinova.ai"}
                </p>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="ml-2 rounded-lg p-1.5 text-slate-400 hover:bg-rose-500/20 hover:text-rose-300 transition-colors"
              aria-label="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* 2. MAIN VIEWPORT & TOP BAR                                               */}
      {/* ========================================================================= */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Clean Top Bar */}
        <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200/90 bg-white/95 backdrop-blur-md px-4 sm:px-6 lg:px-8">
          {/* Left: Mobile hamburger & Global Search */}
          <div className="flex items-center gap-4 flex-1 max-w-xl">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="md:hidden text-slate-600 hover:text-slate-900 p-2 rounded-xl hover:bg-slate-100"
              aria-label="Open navigation menu"
            >
              <Menu className="h-6 w-6" />
            </button>

            {/* Global Search Bar */}
            <div className="relative w-full">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                <Search className="h-4 w-4" />
              </div>
              <input
                id="clinova-global-search"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setTimeout(() => setSearchFocused(false), 200)}
                placeholder="Search symptoms, patients, medical records..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50/80 py-2.5 pl-10 pr-12 text-sm text-slate-900 placeholder-slate-400 transition-all focus:border-teal-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              />
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-semibold text-slate-500 shadow-2xs">
                  <Command className="h-3 w-3" />K
                </kbd>
              </div>

              {/* Quick Search Preview dropdown */}
              {searchFocused && (
                <div className="absolute left-0 right-0 top-full mt-2 rounded-2xl border border-slate-200 bg-white p-3 shadow-xl z-50 text-xs text-slate-600">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
                    <span>Suggested Searches</span>
                    <span>Press ESC to close</span>
                  </div>
                  <div className="space-y-1">
                    <Link
                      href="/patients"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-teal-50 text-slate-700 hover:text-teal-800"
                    >
                      <Users className="h-4 w-4 text-teal-600" />
                      <span>Search Patient Records & Clinical History</span>
                    </Link>
                    <Link
                      href="/review"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-teal-50 text-slate-700 hover:text-teal-800"
                    >
                      <CheckSquare className="h-4 w-4 text-teal-600" />
                      <span>Active Triage Queue & Urgent Cases</span>
                    </Link>
                    <Link
                      href="/documents"
                      className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-teal-50 text-slate-700 hover:text-teal-800"
                    >
                      <FileText className="h-4 w-4 text-teal-600" />
                      <span>Diagnostic Lab Reports & Prescriptions</span>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Date, Quick Action, Notifications, Avatar */}
          <div className="flex items-center gap-3 sm:gap-4 pl-3">
            {/* Live Date Display */}
            {currentDateString && (
              <div className="hidden lg:flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200/80">
                <Clock className="h-3.5 w-3.5 text-teal-600" />
                <span>{currentDateString}</span>
              </div>
            )}

            {/* Quick Action Button */}
            {quickAction && (
              <Link
                href={quickAction.href}
                className="hidden sm:inline-flex items-center gap-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 text-xs font-bold tracking-wide shadow-xs transition-colors"
              >
                <quickAction.icon className="h-3.5 w-3.5" />
                <span>{quickAction.label}</span>
              </Link>
            )}

            {/* Notifications Bell */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="relative rounded-xl border border-slate-200 bg-white p-2.5 text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors"
                aria-label="View notifications"
              >
                <Bell className="h-4 w-4" />
                <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500" />
                </span>
              </button>

              {notificationsOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl border border-slate-200 bg-white p-4 shadow-xl z-50">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <span className="font-bold text-slate-900 text-sm">Notifications</span>
                    <span className="text-[11px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full">
                      2 Unread
                    </span>
                  </div>
                  <div className="mt-3 space-y-2.5">
                    <div className="p-2.5 rounded-xl bg-teal-50/50 border border-teal-100 text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-teal-900">
                        <Sparkles className="h-3.5 w-3.5 text-teal-600" />
                        <span>AI Triage Analysis Complete</span>
                      </div>
                      <p className="text-slate-600 mt-1">
                        High confidence triage score synthesized for recent case.
                      </p>
                    </div>
                    <div className="p-2.5 rounded-xl bg-amber-50/50 border border-amber-100 text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-amber-900">
                        <AlertCircle className="h-3.5 w-3.5 text-amber-600" />
                        <span>Clinical Triage Queue</span>
                      </div>
                      <p className="text-slate-600 mt-1">
                        1 priority case awaiting clinician review.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Network connectivity indicator */}
            <div className="hidden sm:block">
              <NetworkIndicator />
            </div>
          </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 space-y-8 max-w-7xl mx-auto w-full">
          {/* Header Greeting Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-3xl border border-slate-200/90 bg-white p-6 md:p-8 shadow-xs">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md border border-teal-100">
                  {roleBadgeText} Workspace
                </span>
                {badge && (
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
                    {badge}
                  </span>
                )}
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
                {title}
              </h1>
              <p className="text-sm text-slate-500 max-w-3xl leading-relaxed">
                {description}
              </p>
            </div>

            <div className="flex items-center gap-3 self-start md:self-center">
              {actions}
              {refresh && (
                <button
                  onClick={refresh}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-2xs"
                  title="Refresh workspace data"
                >
                  <RefreshCw className="h-3.5 w-3.5 text-teal-600" />
                  <span>Refresh</span>
                </button>
              )}
            </div>
          </div>

          {/* Children: Role-Specific Dashboard Content */}
          {children}
        </main>
      </div>
    </div>
  );
}

// Backwards-compatible Stat component
export function Stat({ title, value }: { title: string; value: number | string }) {
  return (
    <MetricCard
      title={title}
      value={value}
      statusColor="teal"
    />
  );
}

// Enhanced DataState component
export function DataState({
  loading,
  error,
  retry,
}: {
  loading: boolean;
  error: string | null;
  retry: () => void;
}) {
  if (loading) {
    return (
      <div
        className="flex flex-col items-center justify-center p-12 rounded-3xl bg-white border border-slate-200/90 shadow-xs text-center space-y-3"
        role="status"
      >
        <div className="h-12 w-12 rounded-2xl bg-teal-50 border border-teal-100 flex items-center justify-center p-2">
          <ClinovaLogo variant="mark" size="sm" className="animate-pulse" />
        </div>
        <p className="text-sm font-bold text-slate-900">Synchronizing clinical workspace...</p>
        <p className="text-xs text-slate-500 max-w-sm">
          Loading EHR records, triage queues, and recent updates from secure servers.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="rounded-3xl border border-rose-200 bg-rose-50/70 p-6 md:p-8 text-center space-y-3 shadow-xs"
        role="alert"
      >
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-100 text-rose-700 border border-rose-200">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="text-base font-bold text-rose-950">Workspace Connection Error</h2>
        <p className="text-sm text-rose-800 max-w-md mx-auto">{error}</p>
        <div className="pt-2">
          <button
            onClick={retry}
            className="inline-flex items-center gap-2 rounded-xl bg-rose-700 text-white px-5 py-2.5 text-xs font-bold tracking-wide hover:bg-rose-800 transition-colors shadow-xs"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    );
  }

  return null;
}