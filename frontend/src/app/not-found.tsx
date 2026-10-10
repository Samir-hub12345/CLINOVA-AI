import React from "react";
import Link from "next/link";
import { AlertCircle, Home, UserCheck, Stethoscope } from "lucide-react";

export default function NotFound() {
  return (
    <div
      style={{
        maxWidth: 640,
        margin: "60px auto",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "var(--clinova-space-4)",
      }}
    >
      <div
        style={{
          width: 54,
          height: 54,
          borderRadius: "50%",
          backgroundColor: "var(--clinova-warning-bg)",
          border: "2px solid var(--clinova-warning-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <AlertCircle style={{ width: 28, height: 28, color: "var(--clinova-warning)" }} aria-hidden="true" />
      </div>

      <h1 style={{ fontSize: "1.75rem" }}>Clinical Resource Not Found (404)</h1>
      <p style={{ fontSize: "0.9375rem", color: "var(--clinova-text-secondary)", maxWidth: 480 }}>
        The requested patient encounter, workstation route, or clinical resource could not be found in the current CLINOVA institutional network.
      </p>

      <div style={{ display: "flex", gap: 10, marginTop: 12, flexWrap: "wrap", justifyContent: "center" }}>
        <Link href="/" className="clinova-btn clinova-btn-secondary" style={{ textDecoration: "none" }}>
          <Home style={{ width: 14, height: 14 }} aria-hidden="true" />
          <span>Return Home</span>
        </Link>
        <Link href="/login" className="clinova-btn clinova-btn-primary" style={{ textDecoration: "none" }}>
          <span>Staff Sign In</span>
        </Link>
        <Link href="/patient" className="clinova-btn clinova-btn-outline" style={{ textDecoration: "none" }}>
          <span>Patient Portal</span>
        </Link>
      </div>
    </div>
  );
}
