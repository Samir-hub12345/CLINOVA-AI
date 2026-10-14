"use client";

import React, { useState } from "react";
import {
  AlertOctagon,
  HeartPulse,
  GitBranch,
} from "lucide-react";

export const WorkflowSection: React.FC = () => {
  const [activePathway, setActivePathway] = useState<"regular" | "emergency" | "both">("both");

  const regularSteps = [
    {
      step: "R1",
      title: "Patient Information Collection",
      sub: "Walk-in & Portal Ingress",
      actor: "Patient / Receptionist",
      badge: "badge-teal",
      desc: "Digital consent under DPDP Act 2023, demographic entry, and self-service symptom capture.",
      route: "/patient/intake",
    },
    {
      step: "R2",
      title: "Typed or Voice Narrative",
      sub: "Vernacular Speech Intake",
      actor: "Patient Audio / Form",
      badge: "badge-teal",
      desc: "Multilingual transcription (Odia, Hindi, English) capturing symptom history without losing spoken context.",
      route: "/patient/intake",
    },
    {
      step: "R3",
      title: "Evidence Extraction",
      sub: "Provenance Tagging",
      actor: "CLINOVA Extraction",
      badge: "badge-navy",
      desc: "Clinical entities tagged to origin: Patient Reported, Bedside Monitor, Clinician Observed, or EHR Imported.",
      route: "/staff/review",
    },
    {
      step: "R4",
      title: "Clinical Summary & Explanation",
      sub: "Dual-Engine Evaluation",
      actor: "Deterministic Compute",
      badge: "badge-navy",
      desc: "Structured draft note generated alongside deterministic NEWS2 and Shock Index physiologic scores.",
      route: "/staff/cases/CASE-SYNTH-003",
    },
    {
      step: "R5",
      title: "Timeline & Missing-Info Audit",
      sub: "Epistemic Gap Discovery",
      actor: "Epistemic Audit",
      badge: "badge-warning",
      desc: "Surfaces unconfirmed drug dosages, missing renal panels, or conflicting allergy records before physician review.",
      route: "/staff/review",
    },
    {
      step: "R6",
      title: "Adaptive Follow-up Questions",
      sub: "Dynamic Inquiries",
      actor: "Adaptive QA",
      badge: "badge-teal",
      desc: "Targeted inquiries presented to patient in waiting area to resolve identified informational gaps.",
      route: "/patient/intake",
    },
    {
      step: "R7",
      title: "Staff Bedside Verification",
      sub: "Nurse Triage Worklist",
      actor: "Triage Nurse",
      badge: "badge-warning",
      desc: "Nurse captures vital signs, verifies ambulatory status, and flags acuity before physician examination.",
      route: "/staff/triage",
    },
    {
      step: "R8",
      title: "CAREGRAPH & Clinician Review",
      sub: "Non-Delegable Physician Gate",
      actor: "Attending Doctor",
      badge: "badge-navy",
      desc: "Licensed Medical Officer inspects timeline, resolves conflicts, and digitally approves the definitive diagnosis.",
      route: "/staff/review",
    },
    {
      step: "R9",
      title: "Report & Continuity of Care",
      sub: "Discharge & Referral",
      actor: "Doctor Signed",
      badge: "badge-teal",
      desc: "Doctor-approved care instructions generated for patient; SBAR transfer packet prepared if tertiary transfer required.",
      route: "/reports",
    },
  ];

  const emergencySteps = [
    {
      step: "E1",
      title: "Emergency Case Creation",
      sub: "Immediate Resuscitation Ingress",
      actor: "Emergency Staff",
      badge: "badge-error",
      desc: "Immediate walk-in or acute trauma admission; all non-essential intake paperwork and questions bypassed.",
    },
    {
      step: "E2",
      title: "Configured Urgent-Signal Checks",
      sub: "Deterministic Red-Flag Triggers",
      actor: "Deterministic Rules",
      badge: "badge-error",
      desc: "NEWS2 ≥ 7, Shock Index > 0.9, acute hypoxia, or shock signs trigger immediate visual alarms.",
    },
    {
      step: "E3",
      title: "Rapid Staff Assessment & Vitals",
      sub: "Bedside Acuity Acquisition",
      actor: "Nurse / Triage Officer",
      badge: "badge-warning",
      desc: "Bedside vital sign capture in seconds: GCS, pulse oximetry, blood pressure, and core respiration.",
    },
    {
      step: "E4",
      title: "Fast-Track Clinician Review",
      sub: "Emergency Physician Override",
      actor: "Attending Emergency MD",
      badge: "badge-navy",
      desc: "Physician immediately assumes clinical direction; optional AI summarization runs strictly in background.",
    },
    {
      step: "E5",
      title: "Emergency / Ward / OT Handoff",
      sub: "Immediate Resuscitation Bay",
      actor: "Clinical Team",
      badge: "badge-error",
      desc: "Direct disposition to resuscitation bay, emergency operating theater, or ICU without barrier delays.",
    },
    {
      step: "E6",
      title: "Relevant Documentation & Follow-up",
      sub: "Post-Stabilization Audit",
      actor: "Clinical Staff",
      badge: "badge-teal",
      desc: "Comprehensive SBAR transfer handoff, forensic audit logging, and post-stabilization documentation.",
    },
  ];

  const masterCaseLoopStages = [
    { step: "1. ENTRY", label: "Public / Portal Entry" },
    { step: "2. CONSENT", label: "DPDP Act Digital Consent" },
    { step: "3. PATHWAY", label: "Staff-Assigned Pathway" },
    { step: "4. INTAKE", label: "Symptoms & Evidence" },
    { step: "5. EXTRACTION", label: "Provenance & Uncertainty" },
    { step: "6. TIMELINE", label: "Chronological Progression" },
    { step: "7. ADAPTIVE", label: "Targeted Inquiries" },
    { step: "8. CAREGRAPH", label: "Risk & Trajectory" },
    { step: "9. SAFETY", label: "Deterministic Alarms" },
    { step: "10. REVIEW", label: "Clinician Authority Gate" },
    { step: "11. FACILITY", label: "SBAR Referral" },
    { step: "12. OUTCOME", label: "Outcome Capture & Telemetry" },
  ];

  return (
    <section
      id="workflow"
      tabIndex={-1}
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="workflow-main-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 840, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            THE CONTINUOUS CLINICAL WORKFLOW
          </div>
          <h2
            id="workflow-main-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            How Clinova AI Coordinates Patient Care
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            Structured evidence processing and diagnostic safety bounds. Two visibly distinct clinical branches ensure scheduled outpatients receive thorough intake while acute resuscitation is never delayed.
          </p>
        </div>

        {/* Pathway Filter Switcher */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            marginBottom: "var(--clinova-space-6)",
            padding: "12px 16px",
            backgroundColor: "var(--surface-sunken)",
            borderRadius: "var(--r-lg)",
            border: "1px solid var(--border)",
          }}
        >
          <div className="row gap-2">
            <GitBranch style={{ width: 18, height: 18, color: "var(--navy-800)" }} aria-hidden="true" />
            <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)" }}>
              Dual Clinical Pathways (Separated Branches)
            </strong>
          </div>

          <div className="segmented">
            <button
              type="button"
              aria-pressed={activePathway === "both"}
              onClick={() => setActivePathway("both")}
            >
              Show Both Branches
            </button>
            <button
              type="button"
              aria-pressed={activePathway === "regular"}
              onClick={() => setActivePathway("regular")}
            >
              Regular OPD Pathway
            </button>
            <button
              type="button"
              aria-pressed={activePathway === "emergency"}
              onClick={() => setActivePathway("emergency")}
            >
              Emergency Pathway
            </button>
          </div>
        </div>

        {/* 1. Paschim Banga Emergency Doctrine Callout Invariant */}
        <div
          style={{
            borderLeft: "4px solid var(--error)",
            backgroundColor: "var(--error-bg)",
            border: "1px solid var(--border)",
            borderLeftWidth: 4,
            borderLeftColor: "var(--error)",
            borderRadius: "var(--r-md)",
            padding: "14px 18px",
            marginBottom: "var(--clinova-space-8)",
          }}
        >
          <div className="row gap-3 items-start">
            <AlertOctagon style={{ width: 22, height: 22, color: "var(--error)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
            <div>
              <strong style={{ fontSize: "0.9375rem", color: "#991b1b", display: "block" }}>
                Paschim Banga Doctrine — Constitutional Emergency Priority
              </strong>
              <p style={{ fontSize: "0.8125rem", color: "#7f1d1d", margin: "4px 0 0", lineHeight: 1.55 }}>
                In strict adherence to the Supreme Court constitutional emergency doctrine, <strong>urgent human assessment and resuscitation must never be delayed</strong> while optional AI analysis, intake surveys, or adaptive questioning run. Emergency cases immediately bypass standard queues straight to bedside clinician attention.
              </p>
            </div>
          </div>
        </div>

        {/* Two Pathway Columns */}
        <div
          className={activePathway === "both" ? "landing-workflow-grid" : ""}
          style={
            activePathway === "both"
              ? undefined
              : { display: "grid", gridTemplateColumns: "1fr", gap: "var(--clinova-space-6)" }
          }
        >
          {/* BRANCH A: Regular / Outpatient Pathway */}
          {(activePathway === "both" || activePathway === "regular") && (
            <div
              className="card"
              style={{
                padding: "var(--clinova-space-6)",
                borderTop: "4px solid var(--teal-600)",
                backgroundColor: "var(--surface)",
              }}
            >
              <div style={{ marginBottom: 16 }}>
                <div className="row between">
                  <span className="section-title" style={{ color: "var(--teal-700)" }}>
                    BRANCH A • SCHEDULED & WALK-IN
                  </span>
                  <span className="badge badge-teal">Regular OPD Pathway</span>
                </div>
                <h3 style={{ fontSize: "1.25rem", color: "var(--navy-900)", marginTop: 4 }}>
                  Comprehensive Care Sequence (9 Steps)
                </h3>
                <p className="xs muted" style={{ marginTop: 2 }}>
                  Thorough multimodal intake, evidence extraction, timeline synthesis, and human clinician review.
                </p>
              </div>

              <div className="stack gap-3">
                {regularSteps.map((step) => (
                  <div
                    key={step.step}
                    style={{
                      border: "1px solid var(--border)",
                      borderRadius: "var(--r-md)",
                      padding: "10px 14px",
                      backgroundColor: "var(--surface-sunken)",
                      transition: "border-color 0.15s ease",
                    }}
                  >
                    <div className="row between" style={{ marginBottom: 4 }}>
                      <div className="row gap-2">
                        <span
                          style={{
                            width: 24,
                            height: 24,
                            borderRadius: "50%",
                            backgroundColor: "var(--teal-100)",
                            color: "var(--teal-700)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: "11px",
                            fontWeight: 700,
                          }}
                        >
                          {step.step}
                        </span>
                        <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)" }}>
                          {step.title}
                        </strong>
                      </div>
                      <span className={`badge ${step.badge}`} style={{ fontSize: "10px", height: "18px" }}>
                        {step.actor}
                      </span>
                    </div>
                    <div className="xs muted" style={{ fontWeight: 500, marginBottom: 2 }}>
                      {step.sub}
                    </div>
                    <p className="xs subtle" style={{ margin: 0, lineHeight: 1.45 }}>
                      {step.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* BRANCH B: Emergency Pathway */}
          {(activePathway === "both" || activePathway === "emergency") && (
            <div
              className="card"
              style={{
                padding: "var(--clinova-space-6)",
                borderTop: "4px solid var(--error)",
                backgroundColor: "var(--surface)",
              }}
            >
              <div style={{ marginBottom: 16 }}>
                <div className="row between">
                  <span className="section-title" style={{ color: "var(--error)" }}>
                    BRANCH B • ACUTE & UNSTABLE
                  </span>
                  <span className="badge badge-error">Emergency Pathway</span>
                </div>
                <h3 style={{ fontSize: "1.25rem", color: "var(--navy-900)", marginTop: 4 }}>
                  Fast-Track Resuscitation Sequence (6 Steps)
                </h3>
                <p className="xs muted" style={{ marginTop: 2 }}>
                  Immediate red-flag diversion, bedside vital sign acquisition, and instant physician override.
                </p>
              </div>

              <div className="stack gap-3">
                {emergencySteps.map((step) => (
                  <div
                    key={step.step}
                    style={{
                      border: "1px solid #fecaca",
                      borderRadius: "var(--r-md)",
                      padding: "12px 14px",
                      backgroundColor: "#fffdfd",
                    }}
                  >
                    <div className="row between" style={{ marginBottom: 4 }}>
                      <div className="row gap-2">
                        <span
                          style={{
                            width: 24,
                            height: 24,
                            borderRadius: "50%",
                            backgroundColor: "var(--error-bg)",
                            color: "var(--error)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: "11px",
                            fontWeight: 700,
                          }}
                        >
                          {step.step}
                        </span>
                        <strong style={{ fontSize: "0.875rem", color: "var(--navy-900)" }}>
                          {step.title}
                        </strong>
                      </div>
                      <span className={`badge ${step.badge}`} style={{ fontSize: "10px", height: "18px" }}>
                        {step.actor}
                      </span>
                    </div>
                    <div className="xs muted" style={{ fontWeight: 500, marginBottom: 2 }}>
                      {step.sub}
                    </div>
                    <p className="xs subtle" style={{ margin: 0, lineHeight: 1.45 }}>
                      {step.desc}
                    </p>
                  </div>
                ))}

                {/* Emergency Handoff Banner */}
                <div
                  style={{
                    backgroundColor: "var(--navy-50)",
                    border: "1px dashed var(--border-strong)",
                    borderRadius: "var(--r-md)",
                    padding: "12px 14px",
                    marginTop: 4,
                  }}
                >
                  <div className="row gap-2" style={{ color: "var(--navy-900)", fontWeight: 600, fontSize: "0.8125rem" }}>
                    <HeartPulse style={{ width: 14, height: 14, color: "var(--error)" }} aria-hidden="true" />
                    <span>Emergency Handoff Telemetry</span>
                  </div>
                  <p className="xs muted" style={{ margin: "4px 0 0", lineHeight: 1.4 }}>
                    If facility resources (ICU/oxygen) are constrained, SBAR transfer handoff dispatches directly through FACILITYGRAPH to the nearest tertiary receiving center.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 12-STAGE MASTER CASE CONTINUOUS LOOP (preserves test requirement) */}
        <div
          className="card"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--clinova-space-4)",
            padding: "var(--clinova-space-6)",
            marginTop: "var(--clinova-space-8)",
            backgroundColor: "var(--surface-sunken)",
          }}
          aria-labelledby="loop-heading"
        >
          <div>
            <span className="section-title">THE 12-STAGE MASTER CASE CONTINUOUS LOOP</span>
            <h3 id="loop-heading" style={{ fontSize: "1.375rem", marginTop: 4, color: "var(--navy-900)", fontWeight: 700 }}>
              Connected Clinical Care Journey
            </h3>
            <p className="xs muted" style={{ marginTop: 2 }}>
              Rigorous evidence grounding and deterministic safety checks before every clinical recommendation.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 140px), 1fr))",
              gap: 10,
              textAlign: "center",
            }}
          >
            {masterCaseLoopStages.map((item) => (
              <div
                key={item.step}
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  padding: "10px 6px",
                  backgroundColor: "var(--surface)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <strong style={{ fontSize: "0.6875rem", color: "var(--teal-700)" }}>
                  {item.step}
                </strong>
                <span style={{ fontSize: "0.75rem", color: "var(--text)", fontWeight: 600 }}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
