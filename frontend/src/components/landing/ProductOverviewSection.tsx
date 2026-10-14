"use client";

import React, { useState } from "react";
import {
  FileText,
  Mic,
  Search,
  Clock,
  Sparkles,
  AlertTriangle,
  HelpCircle,
  Stethoscope,
  BarChart3,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";

export const ProductOverviewSection: React.FC = () => {
  const capabilities = [
    {
      id: "intake",
      title: "Patient Narrative Intake",
      category: "Ingress",
      icon: FileText,
      badge: "Multilingual",
      summary:
        "Walk-in and scheduled patients provide symptom narratives and encounter details via intuitive digital forms with DPDP Act 2023 consent capture.",
      howItConnects:
        "Feeds raw patient-reported symptoms directly into the extraction pipeline without losing verbatim phrasing or vernacular context.",
      preview: {
        type: "form",
        label: "Vernacular Intake Screen",
        items: [
          { label: "Primary Complaint", val: "Bilateral pedal swelling & shortness of breath on exertion" },
          { label: "Duration", val: "4 days progressive worsening" },
          { label: "Consent Status", val: "DPDP Act Digital Consent Authenticated" },
        ],
      },
    },
    {
      id: "voice",
      title: "Voice Transcription & Processing",
      category: "Speech AI",
      icon: Mic,
      badge: "STT Engine",
      summary:
        "Speech-to-text recognition supporting vernacular audio input (Odia, Hindi, English) with word-level confidence and clinical entity tagging.",
      howItConnects:
        "Translates verbal descriptions into structured text while storing original audio waveforms for clinical audit.",
      preview: {
        type: "audio",
        label: "Audio Speech-to-Text Pipeline",
        items: [
          { label: "Spoken Dialect", val: "Vernacular Audio Input (Odia / Hindi / English)" },
          { label: "Transcription Confidence", val: "0.96 (High Spectral Clarity)" },
          { label: "Extracted Utterance", val: "“Chhati re kasta heuchhi, gochha phuli jaichhi”" },
        ],
      },
    },
    {
      id: "extraction",
      title: "Evidence Extraction & Provenance",
      category: "Context",
      icon: Search,
      badge: "Traceability",
      summary:
        "Identifies symptoms, past medical history, and current medications, explicitly tagging every extracted datum with its provenance source.",
      howItConnects:
        "Ensures attending physicians can instantly audit whether a fact originated from patient statements, bedside monitors, or prior hospital EHRs.",
      preview: {
        type: "tags",
        label: "Color-Coded Provenance Tags",
        items: [
          { label: "Pedal Edema", val: "Provenance: Patient Voice [Reported]" },
          { label: "Heart Failure NYHA II", val: "Provenance: EHR Record [Imported]" },
          { label: "BP 142/90 mmHg", val: "Provenance: Nurse Monitor [Verified]" },
        ],
      },
    },
    {
      id: "timeline",
      title: "Patient Timeline Progression",
      category: "Progression",
      icon: Clock,
      badge: "Chronology",
      summary:
        "Arranges historical diagnoses, past admissions, vital fluctuations, and recent symptomatic episodes into a single chronological progression.",
      howItConnects:
        "Enables physicians to differentiate chronic disease baselines from acute destabilization within seconds.",
      preview: {
        type: "timeline",
        label: "Chronological Sequence",
        items: [
          { label: "2024–2025", val: "Outpatient Hypertension management (Amlodipine 10mg)" },
          { label: "4 Days Ago", val: "Onset of lower extremity edema post-salt intake" },
          { label: "Today 08:30", val: "Acute dyspnea requiring bedside triage evaluation" },
        ],
      },
    },
    {
      id: "summary",
      title: "Clinical Summary & Explanation",
      category: "Synthesis",
      icon: Sparkles,
      badge: "Deterministic",
      summary:
        "Synthesizes evidence into a structured draft summary, pairing natural language explanation with deterministic NEWS2 and Shock Index risk calculations.",
      howItConnects:
        "Provides a synthesized clinical overview for the physician while keeping calculations completely transparent and deterministic.",
      preview: {
        type: "soap",
        label: "Draft Summary & Calculation",
        items: [
          { label: "NEWS2 Score", val: "6 (Moderate Risk: SpO2 93%, RR 22, HR 104)" },
          { label: "Shock Index", val: "0.74 (Hemodynamically compensated)" },
          { label: "Draft Rationale", val: "Decompensated chronic heart failure secondary to fluid overload" },
        ],
      },
    },
    {
      id: "audit",
      title: "Missing-Information Audit",
      category: "Governance",
      icon: AlertTriangle,
      badge: "Epistemic Gap",
      summary:
        "Surfaces unknown or conflicting clinical details, missing routine lab investigations, and unconfirmed drug dosages before physician consultation.",
      howItConnects:
        "Prevents diagnostic closure on incomplete records by prompting healthcare staff to collect vital missing data before final review.",
      preview: {
        type: "gaps",
        label: "Proactive Gap Detection",
        items: [
          { label: "Unconfirmed Allergy", val: "Penicillin allergy reported by family; no chart confirmation" },
          { label: "Missing Renal Panel", val: "No serum creatinine recorded within previous 6 months" },
          { label: "Medication Adherence", val: "Last refill date for Loop Diuretic unrecorded" },
        ],
      },
    },
    {
      id: "adaptive",
      title: "Adaptive Follow-up Inquiries",
      category: "Refinement",
      icon: HelpCircle,
      badge: "Dynamic QA",
      summary:
        "Generates targeted, patient-friendly follow-up questions tailored specifically to unresolved symptoms and identified missing information.",
      howItConnects:
        "Gathers critical context from the patient while still in the waiting area, saving physician examination time.",
      preview: {
        type: "questions",
        label: "Targeted Inquiries",
        items: [
          { label: "Target: Orthopnea", val: "“How many pillows do you need to sleep comfortably at night?”" },
          { label: "Target: Fluid Balance", val: "“Have you noticed sudden weight gain or swelling in both legs?”" },
          { label: "Target: Medication", val: "“Did you take your morning blood pressure medication today?”" },
        ],
      },
    },
    {
      id: "review",
      title: "Clinician Review Workbench",
      category: "Authority Gate",
      icon: Stethoscope,
      badge: "Physician Gate",
      summary:
        "3-panel workstation for attending medical practitioners to inspect timeline evidence, verify provenance, resolve conflicts, and document final care decisions.",
      howItConnects:
        "Acts as the mandatory human authorization gate: AI outputs are never finalized without non-repudiable physician approval.",
      preview: {
        type: "review",
        label: "Attending Physician Console",
        items: [
          { label: "Authoritative Decision", val: "Admit to telemetry bed; IV Furosemide 40mg stat" },
          { label: "Verification Gate", val: "Dr. Joshua Ajose, MD • Medical Officer (NMC Authenticated)" },
          { label: "Action Status", val: "Care Plan Approved & Non-Repudiably Signed" },
        ],
      },
    },
    {
      id: "reporting",
      title: "Patient-Specific Reporting & SBAR",
      category: "Continuity",
      icon: BarChart3,
      badge: "Handoff",
      summary:
        "Compiles doctor-signed clinical encounter summaries, plain-language vernacular care instructions for patients, and structured SBAR transfer packets.",
      howItConnects:
        "Ensures uninterrupted continuity of care across regional hospital transfers and transparent health literacy for discharging patients.",
      preview: {
        type: "reporting",
        label: "Multi-Audience Outputs",
        items: [
          { label: "Patient Care Plan", val: "Vernacular instructions on low-sodium diet and red-flag symptoms" },
          { label: "SBAR Transfer Packet", val: "Situation, Background, Assessment, Recommendation for receiving center" },
          { label: "PDF Verification", val: "Cryptographically verifiable signed encounter summary" },
        ],
      },
    },
  ];

  const [activeCapId, setActiveCapId] = useState("intake");
  const activeCap = capabilities.find((c) => c.id === activeCapId) || capabilities[0];
  const Icon = activeCap.icon;

  return (
    <section
      id="platform"
      tabIndex={-1}
      className="landing-section"
      style={{
        paddingTop: "var(--clinova-space-10)",
        paddingBottom: "var(--clinova-space-10)",
        backgroundColor: "var(--surface-sunken)",
        borderBottom: "1px solid var(--border)",
      }}
      aria-labelledby="overview-heading"
    >
      <div className="clinova-container">
        {/* Section Header */}
        <div style={{ maxWidth: 760, marginBottom: "var(--clinova-space-8)" }}>
          <div className="section-title" style={{ color: "var(--teal-700)" }}>
            ONE CONNECTED VIEW OF THE PATIENT JOURNEY
          </div>
          <h2
            id="overview-heading"
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.375rem)",
              fontWeight: 800,
              color: "var(--navy-900)",
              lineHeight: 1.2,
              letterSpacing: "-0.025em",
              marginTop: 6,
            }}
          >
            One connected view of the patient journey.
          </h2>
          <p
            style={{
              fontSize: "1rem",
              color: "var(--text-2)",
              lineHeight: 1.6,
              marginTop: 8,
            }}
          >
            CLINOVA AI is designed to connect patient information, structured evidence, AI-assisted analysis, clinician review and follow-up across nine modular capabilities.
          </p>
        </div>

        {/* Capabilities Explorer Grid: Navigation Tabs on Left, Active Showcase on Right */}
        <div className="landing-overview-grid">
          {/* Left Column: Capability Selector List */}
          <div
            role="tablist"
            aria-label="Clinical platform capabilities"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 6,
              maxHeight: 580,
              overflowY: "auto",
              paddingRight: 6,
            }}
          >
            {capabilities.map((cap) => {
              const CapIcon = cap.icon;
              const isSelected = cap.id === activeCapId;
              return (
                <button
                  key={cap.id}
                  id={`cap-tab-${cap.id}`}
                  type="button"
                  role="tab"
                  aria-selected={isSelected}
                  aria-controls={`cap-panel-${cap.id}`}
                  onClick={() => setActiveCapId(cap.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 14px",
                    borderRadius: "var(--r-md)",
                    border: isSelected ? "1.5px solid var(--teal-600)" : "1px solid var(--border)",
                    backgroundColor: isSelected ? "var(--surface)" : "var(--surface)",
                    boxShadow: isSelected ? "0 2px 8px rgba(15, 157, 145, 0.12)" : "none",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: "var(--r-sm)",
                        backgroundColor: isSelected ? "var(--teal-50)" : "var(--surface-sunken)",
                        color: isSelected ? "var(--teal-700)" : "var(--text-3)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                      }}
                    >
                      <CapIcon style={{ width: 16, height: 16 }} aria-hidden="true" />
                    </div>
                    <div>
                      <strong
                        style={{
                          fontSize: "0.875rem",
                          color: isSelected ? "var(--navy-900)" : "var(--text)",
                          display: "block",
                        }}
                      >
                        {cap.title}
                      </strong>
                      <span className="xs muted">{cap.category}</span>
                    </div>
                  </div>
                  <span
                    className={`badge ${isSelected ? "badge-teal" : "badge-outline"}`}
                    style={{ fontSize: "10px", height: "20px" }}
                  >
                    {cap.badge}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Right Column: Active Capability Deep-Dive Preview */}
          <div
            id={`cap-panel-${activeCap.id}`}
            role="tabpanel"
            aria-labelledby={`cap-tab-${activeCap.id}`}
            tabIndex={0}
            className="card"
            style={{
              padding: "var(--clinova-space-6)",
              backgroundColor: "var(--surface)",
              boxShadow: "var(--shadow-sm)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: 520,
            }}
          >
            <div className="stack gap-4">
              {/* Header */}
              <div className="row between wrap gap-2">
                <div className="row gap-3">
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "var(--r-md)",
                      backgroundColor: "var(--navy-100)",
                      color: "var(--navy-800)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Icon style={{ width: 22, height: 22 }} aria-hidden="true" />
                  </div>
                  <div>
                    <span className="section-title" style={{ color: "var(--teal-700)" }}>
                      {activeCap.category} CAPABILITY
                    </span>
                    <h3 style={{ fontSize: "1.25rem", color: "var(--navy-900)", margin: 0 }}>
                      {activeCap.title}
                    </h3>
                  </div>
                </div>
                <span className="badge badge-teal" style={{ fontWeight: 600 }}>
                  Active in Codebase
                </span>
              </div>

              {/* Functional Explanation */}
              <div>
                <span className="xs muted medium" style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  What It Does
                </span>
                <p style={{ fontSize: "0.9375rem", color: "var(--text)", lineHeight: 1.6, margin: "4px 0 0" }}>
                  {activeCap.summary}
                </p>
              </div>

              {/* Workflow Connection */}
              <div
                style={{
                  backgroundColor: "var(--surface-sunken)",
                  padding: "12px 14px",
                  borderRadius: "var(--r-md)",
                  borderLeft: "3px solid var(--teal-600)",
                }}
              >
                <div className="row gap-1" style={{ color: "var(--teal-700)", fontWeight: 600, fontSize: "0.75rem" }}>
                  <ArrowRight style={{ width: 13, height: 13 }} aria-hidden="true" />
                  <span>How It Connects to the Wider Workflow</span>
                </div>
                <p className="xs subtle" style={{ margin: "4px 0 0", lineHeight: 1.5 }}>
                  {activeCap.howItConnects}
                </p>
              </div>

              {/* Authentic UI Snippet Preview */}
              <div
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r-md)",
                  backgroundColor: "var(--surface)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    backgroundColor: "var(--surface-2)",
                    padding: "8px 12px",
                    borderBottom: "1px solid var(--border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <span className="xs strong" style={{ color: "var(--navy-900)" }}>
                    {activeCap.preview.label}
                  </span>
                  <span className="xs muted">Synthetic Demonstration Data</span>
                </div>
                <div style={{ padding: "12px 14px" }} className="stack gap-2">
                  {activeCap.preview.items.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 2,
                        paddingBottom: idx < activeCap.preview.items.length - 1 ? 8 : 0,
                        borderBottom: idx < activeCap.preview.items.length - 1 ? "1px solid var(--border)" : "none",
                      }}
                    >
                      <span className="xs muted medium">{item.label}</span>
                      <span style={{ fontSize: "0.8125rem", color: "var(--navy-900)", fontWeight: 500 }}>
                        {item.val}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Callout */}
            <div
              style={{
                borderTop: "1px solid var(--border)",
                paddingTop: 12,
                marginTop: 16,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 8,
              }}
            >
              <div className="row gap-2">
                <CheckCircle2 style={{ width: 14, height: 14, color: "var(--teal-600)" }} aria-hidden="true" />
                <span className="xs muted">
                  Validated against automated clinical test invariants, provenance bounds, and deterministic safety rules
                </span>
              </div>
              <a href="#workflow" className="xs strong" style={{ color: "var(--teal-700)" }}>
                See in Workflow Sequence →
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
