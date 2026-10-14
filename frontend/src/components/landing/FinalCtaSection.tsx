"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, LogIn, ArrowDown, ShieldCheck, Sparkles } from "lucide-react";

export const FinalCtaSection: React.FC = () => {
  return (
    <section
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-12)",
        paddingBottom: "var(--clinova-space-12)",
        backgroundColor: "var(--navy-900)",
        color: "#ffffff",
      }}
      aria-labelledby="cta-main-heading"
    >
      <div className="clinova-container">
        <div
          style={{
            maxWidth: 840,
            margin: "0 auto",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "var(--clinova-space-4)",
          }}
        >
          {/* Eyebrow Ribbon */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              fontSize: "11px",
              fontWeight: 700,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "var(--teal-100)",
              backgroundColor: "rgba(15, 157, 145, 0.2)",
              border: "1px solid var(--teal-600)",
              padding: "4px 12px",
              borderRadius: "var(--r-full)",
            }}
          >
            <Sparkles style={{ width: 13, height: 13, color: "var(--teal-100)" }} aria-hidden="true" />
            <span>CONTINUOUS CARE INTELLIGENCE</span>
          </div>

          {/* Heading — Deep contrasting white text, clean, readable */}
          <h2
            id="cta-main-heading"
            style={{
              fontSize: "clamp(2rem, 3.5vw, 2.75rem)",
              fontWeight: 800,
              lineHeight: 1.2,
              letterSpacing: "-0.03em",
              color: "#ffffff",
              margin: 0,
            }}
          >
            Bring the patient journey into clearer focus.
          </h2>

          {/* Supporting Text */}
          <p
            style={{
              fontSize: "1.125rem",
              lineHeight: 1.6,
              color: "#cbd5e1",
              maxWidth: 680,
              margin: 0,
            }}
          >
            Explore a connected approach to patient intake, clinical evidence, AI-assisted review and care workflow coordination.
          </p>

          {/* 3 Active Action Buttons */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexWrap: "wrap",
              gap: 12,
              marginTop: 12,
            }}
          >
            <a
              href="#platform"
              className="btn btn-secondary btn-lg"
              style={{
                backgroundColor: "#ffffff",
                color: "var(--navy-900)",
                border: "none",
                fontWeight: 600,
                gap: 8,
              }}
            >
              <span>Explore the Platform</span>
              <ArrowDown style={{ width: 16, height: 16 }} aria-hidden="true" />
            </a>

            <Link
              href="/login"
              className="btn btn-ghost btn-lg"
              style={{
                color: "#ffffff",
                border: "1px solid rgba(255, 255, 255, 0.24)",
                gap: 8,
              }}
            >
              <LogIn style={{ width: 16, height: 16 }} aria-hidden="true" />
              <span>Sign In</span>
            </Link>

            <Link
              href="/register"
              className="btn btn-accent btn-lg"
              style={{
                gap: 8,
                backgroundColor: "var(--teal-600)",
                fontWeight: 600,
              }}
            >
              <span>Get Started</span>
              <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
            </Link>
          </div>

          {/* Clinical Authority Note */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: "0.8125rem",
              color: "#94a3b8",
              marginTop: 16,
            }}
          >
            <ShieldCheck style={{ width: 16, height: 16, color: "var(--teal-600)" }} aria-hidden="true" />
            <span>
              Authorized clinical personnel retain non-delegable medical authority for all patient dispositions.
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
