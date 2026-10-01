"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Menu,
  X,
  LogOut,
  ArrowRight,
  LayoutDashboard,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import { Badge } from "@/components/ui/badge";
import { NetworkIndicator } from "@/components/common/network-indicator";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export const Header: React.FC = () => {
  const pathname = usePathname();
  const { user, logout, isDoctor, isAdmin, isPatient } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const isHomePage = pathname === "/";

  // Section anchor links for public navigation
  const publicNavLinks = [
    { label: "How It Works", href: isHomePage ? "#how-it-works" : "/#how-it-works" },
    { label: "Features", href: isHomePage ? "#features" : "/#features" },
    { label: "Who It's For", href: isHomePage ? "#who-its-for" : "/#who-its-for" },
    { label: "Safety & Privacy", href: isHomePage ? "#privacy-safety" : "/#privacy-safety" },
    { label: "Contact", href: isHomePage ? "#contact" : "/#contact" },
  ];

  // Role-specific authenticated navigation links (Strict boundary enforcement)
  const getAuthenticatedNavItems = () => {
    if (!user) return [];

    if (isPatient) {
      return [
        { label: "My Dashboard", href: "/dashboard/patient" },
        { label: "Patient Intake", href: "/intake" },
        { label: "Documents", href: "/documents" },
      ];
    }

    if (user.role === "nurse") {
      return [
        { label: "Staff Dashboard", href: "/dashboard/nurse" },
        { label: "Patient Intake", href: "/intake" },
        { label: "Review Queue", href: "/review" },
        { label: "Patients", href: "/patients" },
        { label: "Documents", href: "/documents" },
      ];
    }

    if (isDoctor) {
      return [
        { label: "Doctor Dashboard", href: "/dashboard/doctor" },
        { label: "Review Queue", href: "/review" },
        { label: "EHR Directory", href: "/patients" },
        { label: "Consultations", href: "/consultations" },
        { label: "AI Triage", href: "/triage" },
        { label: "Documents", href: "/documents" },
      ];
    }

    if (isAdmin) {
      return [
        { label: "Admin Console", href: "/dashboard/admin" },
        { label: "Audit Trail", href: "/audit" },
        { label: "Documents", href: "/documents" },
      ];
    }

    return [{ label: "Dashboard", href: dashboardPath(user.role) }, { label: "Documents", href: "/documents" }];
  };

  const authNavItems = getAuthenticatedNavItems();

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Tag */}
        <div className="flex items-center gap-6">
          <ClinovaLogo
            href="/"
            variant="full"
            size="md"
            showTagline={true}
            taglineText="Multimodal Healthcare Triage"
            priority={true}
          />

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {isHomePage
              ? publicNavLinks.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-teal-700 hover:bg-teal-50/50 transition-colors"
                  >
                    {item.label}
                  </a>
                ))
              : user
              ? authNavItems.map((item) => {
                  const active = pathname === item.href || (pathname ? pathname.startsWith(item.href + "/") : false);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        active
                          ? "bg-teal-50 text-teal-800 border border-teal-200 shadow-xs"
                          : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                      }`}
                    >
                      {item.label}
                    </Link>
                  );
                })
              : publicNavLinks.map((item) => (
                  <Link
                    key={item.label}
                    href={item.href}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-teal-700 hover:bg-teal-50/50 transition-colors"
                  >
                    {item.label}
                  </Link>
                ))}
          </nav>
        </div>

        {/* Right side controls: Real-Time Network Indicator, Assistant Control, User Auth / CTAs, Hamburger */}
        <div className="flex items-center gap-2 sm:gap-3">

          {/* Real-Time Adaptive Network Indicator */}
          <NetworkIndicator />

          {/* User state handling */}
          {user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                href={dashboardPath(user.role)}
                className="hidden sm:flex items-center gap-1 px-3 py-1.5 bg-teal-50 text-teal-800 border border-teal-200 rounded-lg text-xs font-semibold hover:bg-teal-100 transition"
              >
                <LayoutDashboard className="w-3.5 h-3.5 text-teal-700" />
                <span>Dashboard</span>
              </Link>
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-xs font-semibold text-slate-900 truncate max-w-[120px]">
                  {user.full_name}
                </span>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                  {user.role}
                </span>
              </div>
              <Badge
                variant={
                  user.role === "doctor"
                    ? "default"
                    : user.role === "admin"
                    ? "warning"
                    : "secondary"
                }
                className="text-[10px] uppercase font-bold"
              >
                {user.role}
              </Badge>
              <button
                onClick={logout}
                title="Sign out"
                className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-2">
              <Link
                href="/intake"
                className="px-3 py-1.5 text-teal-700 hover:text-teal-900 hover:bg-teal-50 rounded-lg text-xs font-semibold transition-colors border border-teal-200"
              >
                Patient Intake
              </Link>
              <Link
                href="/login"
                className="px-3 py-1.5 text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg text-xs font-semibold transition-colors border border-transparent hover:border-slate-200"
              >
                Login
              </Link>
              <Link
                href="/get-started"
                className="px-3.5 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1"
              >
                <span>Get Started</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}

          {/* Mobile Menu Hamburger Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            className="lg:hidden p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-slate-200 bg-white px-4 pt-3 pb-5 space-y-3 animate-in slide-in-from-top-2 duration-200 shadow-lg">
          <nav className="flex flex-col space-y-1">
            {isHomePage ? (
              publicNavLinks.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-teal-50 transition"
                >
                  {item.label}
                </a>
              ))
            ) : user ? (
              authNavItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-teal-50 transition"
                >
                  {item.label}
                </Link>
              ))
            ) : (
              publicNavLinks.map((item) => (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-teal-50 transition"
                >
                  {item.label}
                </Link>
              ))
            )}
          </nav>

          <div className="pt-2 border-t border-slate-100 flex flex-col gap-2">

            {user ? (
              <div className="flex items-center justify-between pt-1">
                <div>
                  <span className="block text-xs font-semibold text-slate-900">{user.full_name}</span>
                  <span className="text-[10px] text-slate-500 uppercase">{user.role}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href={dashboardPath(user.role)}
                    onClick={() => setMobileMenuOpen(false)}
                    className="px-3 py-1.5 bg-teal-50 text-teal-800 border border-teal-200 rounded-lg text-xs font-semibold"
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={logout}
                    className="p-1.5 text-slate-500 hover:text-rose-600 rounded-lg"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-2 pt-1">
                <Link
                  href="/intake"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center px-2 py-2 border border-teal-200 text-teal-700 hover:bg-teal-50 rounded-lg text-xs font-semibold"
                >
                  Intake
                </Link>
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center px-2 py-2 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold"
                >
                  Login
                </Link>
                <Link
                  href="/get-started"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center px-2 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-xs"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
