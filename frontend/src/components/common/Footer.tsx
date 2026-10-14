"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowRight, ShieldCheck, Mail, Building2 } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--border)",
        backgroundColor: "var(--surface)",
        padding: "var(--clinova-space-8) 0 var(--clinova-space-6)",
        marginTop: "auto",
        fontSize: "0.8125rem",
        color: "var(--text-2)",
      }}
    >
      <div className="clinova-container">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "var(--clinova-space-6)",
            marginBottom: "var(--clinova-space-6)",
          }}
        >
          {/* Column 1: Identity & Architecture */}
          <div>
            <strong
              style={{
                fontSize: "1rem",
                color: "var(--navy-900)",
                display: "block",
                marginBottom: 6,
                letterSpacing: "-0.01em",
              }}
            >
              CLINOVA <span style={{ color: "var(--teal-600)" }}>AI</span>
            </strong>
            <p style={{ fontSize: "0.8125rem", color: "var(--text-3)", lineHeight: 1.5, margin: 0 }}>
              Continuous Care Intelligence & Clinical Navigation Platform. Connecting Patient Risk, Evidence Uncertainty, and Facility Resources to identify the Safest Achievable Care Pathway.
            </p>
            <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6 }}>
              <span className="badge badge-teal" style={{ fontSize: "10px", height: "18px" }}>
                Synthetic Demonstration Instance
              </span>
            </div>
          </div>

          {/* Column 2: Platform Navigation */}
          <div>
            <strong
              style={{
                fontSize: "0.8125rem",
                color: "var(--navy-900)",
                display: "block",
                marginBottom: 8,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Platform Navigation
            </strong>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6, padding: 0, margin: 0 }}>
              <li>
                <a href="/#platform" className="clinova-footer-link">
                  Product Overview
                </a>
              </li>
              <li>
                <a href="/#workflow" className="clinova-footer-link">
                  How It Works (Dual Pathways)
                </a>
              </li>
              <li>
                <a href="/#intelligence" className="clinova-footer-link">
                  Clinical Intelligence (Tri-Graph)
                </a>
              </li>
              <li>
                <a href="/#roles" className="clinova-footer-link">
                  Healthcare Workspaces
                </a>
              </li>
              <li>
                <a href="/#trust" className="clinova-footer-link">
                  Trust & Safety
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Ingress & Authentication */}
          <div>
            <strong
              style={{
                fontSize: "0.8125rem",
                color: "var(--navy-900)",
                display: "block",
                marginBottom: 8,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Ingress & Entry
            </strong>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6, padding: 0, margin: 0 }}>
              <li>
                <Link href="/login" className="clinova-footer-link">
                  Sign In (Staff Login)
                </Link>
              </li>
              <li>
                <Link href="/register" className="clinova-footer-link">
                  Sign Up (Get Started)
                </Link>
              </li>
              <li>
                <Link href="/patient" className="clinova-footer-link">
                  Patient Portal & Intake
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 4: Governance & Compliance */}
          <div>
            <strong
              style={{
                fontSize: "0.8125rem",
                color: "var(--navy-900)",
                display: "block",
                marginBottom: 8,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Governance & Policies
            </strong>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6, padding: 0, margin: 0 }}>
              <li>
                <Link href="/disclaimer" className="clinova-footer-link-accent">
                  Clinical Decision Support Disclaimer
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="clinova-footer-link-accent">
                  Zero-PII Privacy & DPDP Act 2023
                </Link>
              </li>
              <li>
                <Link href="/about" className="clinova-footer-link-accent">
                  Mission & Technical Architecture
                </Link>
              </li>
              <li style={{ fontSize: "0.75rem", color: "var(--text-3)", marginTop: 4 }}>
                Reference Center: Lekki Family Health Clinic (FAC-DH-04)
              </li>
            </ul>
          </div>
        </div>

        {/* Clinical Safety Invariant Banner */}
        <div
          style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "var(--clinova-space-4)",
            marginBottom: "var(--clinova-space-4)",
            display: "flex",
            alignItems: "flex-start",
            gap: 8,
          }}
        >
          <ShieldAlert style={{ width: 16, height: 16, color: "var(--warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
          <p style={{ fontSize: "0.75rem", color: "var(--text-3)", lineHeight: 1.5, margin: 0 }}>
            <strong>Clinical Safety Invariant:</strong> CLINOVA AI operates strictly under human-in-the-loop governance. It does not formulate autonomous diagnoses, author prescriptions, or override physician decision authority. All care pathways require review and non-repudiable approval by a registered medical practitioner (NMC 2023 Regulations).
          </p>
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "var(--clinova-space-3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            fontSize: "0.75rem",
            color: "var(--text-4)",
          }}
        >
          <span>
            © {new Date().getFullYear()} CLINOVA AI. Strictly ₹0 Zero-Cost Open Production Architecture.
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span>Synthetic Demonstration Build</span>
            <span>•</span>
            <span>Paschim Banga Emergency Doctrine Enabled</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
