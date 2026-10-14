"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  Menu,
  X,
  LogIn,
  ArrowRight,
  LayoutDashboard,
} from "lucide-react";
import { useClinova } from "@/lib/referenceContext";

export const LandingHeader: React.FC = () => {
  const pathname = usePathname();
  const { user } = useClinova();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 16);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const navItems = [
    { label: "Platform", href: "/#platform" },
    { label: "How It Works", href: "/#workflow" },
    { label: "Clinical Intelligence", href: "/#intelligence" },
    { label: "Trust & Safety", href: "/#trust" },
  ];

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (pathname === "/" && href.startsWith("/#")) {
      e.preventDefault();
      const targetId = href.replace("/#", "");
      const elem = document.getElementById(targetId);
      if (elem) {
        if (typeof window !== "undefined") {
          window.history.pushState(null, "", href);
        }
        elem.scrollIntoView({ behavior: "smooth", block: "start" });
        if (typeof elem.focus === "function") {
          elem.focus({ preventScroll: true });
        }
        setMobileMenuOpen(false);
      }
    }
  };

  return (
    <header
      className={`clinova-landing-header ${scrolled ? "scrolled" : ""}`}
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        transition: "box-shadow 0.2s ease, background-color 0.2s ease",
        boxShadow: scrolled ? "0 4px 16px -2px rgba(13, 33, 53, 0.08)" : "none",
      }}
    >
      <div className="clinova-container">
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          {/* 1. CLINOVA AI Brand Identity */}
          <Link
            href="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
              flexShrink: 0,
            }}
            aria-label="CLINOVA AI Home"
          >
            <div
              style={{
                width: 36,
                height: 36,
                minWidth: 36,
                minHeight: 36,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
              }}
            >
              <Image
                src="/branding/clinova-ai-mark.png"
                alt="CLINOVA AI Mark"
                width={36}
                height={36}
                priority
                style={{
                  width: 36,
                  height: 36,
                  objectFit: "contain",
                }}
              />
            </div>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span
                style={{
                  fontSize: "1.125rem",
                  fontWeight: 800,
                  color: "var(--navy-900)",
                  letterSpacing: "-0.025em",
                  lineHeight: 1.15,
                  whiteSpace: "nowrap",
                }}
              >
                CLINOVA <span style={{ color: "var(--teal-600)" }}>AI</span>
              </span>
              <span
                style={{
                  fontSize: "0.625rem",
                  color: "var(--teal-700)",
                  fontWeight: 700,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
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
            aria-label="Public Navigation"
            className="landing-desktop-nav hide-mobile"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={(e) => handleNavClick(e, item.href)}
                className="landing-nav-link"
                style={{
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  color: "var(--text-2)",
                  textDecoration: "none",
                  padding: "6px 12px",
                  borderRadius: "var(--r-md)",
                  transition: "color 0.15s, background-color 0.15s",
                }}
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* 3. Authentication & Entry Buttons */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {user ? (
              <Link
                href="/"
                className="btn btn-primary btn-sm"
                style={{ gap: 6 }}
              >
                <LayoutDashboard style={{ width: 14, height: 14 }} aria-hidden="true" />
                <span className="hide-mobile">Active Session:</span>
                <span>Dashboard</span>
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="btn btn-secondary btn-sm"
                  style={{ gap: 6 }}
                >
                  <LogIn style={{ width: 14, height: 14 }} aria-hidden="true" />
                  <span>Sign In</span>
                </Link>
                <Link
                  href="/register"
                  className="btn btn-primary btn-sm hide-mobile"
                  style={{ gap: 6, backgroundColor: "var(--navy-900)" }}
                >
                  <span>Get Started</span>
                  <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
                </Link>
              </>
            )}

            {/* Mobile Navigation Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="icon-btn show-mobile"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
              style={{
                border: "1px solid var(--border)",
                borderRadius: "var(--r-md)",
                width: 36,
                height: 36,
              }}
            >
              {mobileMenuOpen ? (
                <X style={{ width: 18, height: 18 }} aria-hidden="true" />
              ) : (
                <Menu style={{ width: 18, height: 18 }} aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div
            className="landing-mobile-menu show-mobile"
            style={{
              padding: "16px 0 20px",
              borderTop: "1px solid var(--border)",
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={(e) => handleNavClick(e, item.href)}
                  style={{
                    fontSize: "0.9375rem",
                    fontWeight: 600,
                    color: "var(--navy-900)",
                    textDecoration: "none",
                    padding: "10px 12px",
                    borderRadius: "var(--r-md)",
                    backgroundColor: "var(--surface-sunken)",
                  }}
                >
                  {item.label}
                </a>
              ))}
            </nav>

            <div
              style={{
                borderTop: "1px solid var(--border)",
                paddingTop: 12,
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              {user ? (
                <Link
                  href="/"
                  className="btn btn-primary btn-block"
                  style={{ gap: 6 }}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <LayoutDashboard style={{ width: 16, height: 16 }} aria-hidden="true" />
                  <span>Active Session: Dashboard</span>
                </Link>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="btn btn-secondary btn-block"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <LogIn style={{ width: 16, height: 16 }} aria-hidden="true" />
                    <span>Sign In to Workstation</span>
                  </Link>
                  <Link
                    href="/register"
                    className="btn btn-primary btn-block"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <span>Get Started (Registration)</span>
                    <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
