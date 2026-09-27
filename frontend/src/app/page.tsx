"use client";
import { useAuth } from "@/lib/auth";
import { dashboardPath } from "@/lib/permissions";
import React from "react";
import Link from "next/link";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { ClinicalDisclaimer } from "@/components/clinical/disclaimer";
import { AdaptiveImage } from "@/components/common/adaptive-image";
import { ClinovaLogo } from "@/components/common/clinova-logo";
import {
  Mic,
  FileText,
  Languages,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Clock,
  UserCheck,
  Activity,
  Layers,
  Hospital,
  Stethoscope,
  User,
  Building,
  Lock,
  ChevronRight,
  Cpu,
  FileCheck,
  Mail,
  Check,
  X,
  UserPlus,
  LogIn,
} from "lucide-react";

export default function Home() {
  const { user, isClinician } = useAuth();
  // Key Features categorized
  const featureList = [
    {
      icon: <Mic className="w-5 h-5 text-teal-600" />,
      title: "Multimodal Patient Intake",
      description:
        "Capture patient symptoms through voice dictation or structured text. Features 6-state audio recording with fallback offline resilience.",
      tag: "Intake",
    },
    {
      icon: <Languages className="w-5 h-5 text-blue-600" />,
      title: "Multilingual Normalization",
      description:
        "Support vernacular inputs across Odia, Hindi, and English. Preserves original patient quotes while standardizing clinical summaries.",
      tag: "Language",
    },
    {
      icon: <FileText className="w-5 h-5 text-sky-600" />,
      title: "Document OCR & Lab Parsing",
      description:
        "Digitize printed CBC and biochemical reports with local OCR, confidence scores, and parameter extraction for rapid physician review.",
      tag: "OCR & Labs",
    },
    {
      icon: <AlertTriangle className="w-5 h-5 text-amber-600" />,
      title: "Explainable Safety Rules",
      description:
        "Deterministic clinical rules (TRIAGE-R01 to R06) screen for acute red flags including respiratory distress, chest pain, and severe trauma.",
      tag: "Rules Engine",
    },
    {
      icon: <UserCheck className="w-5 h-5 text-emerald-600" />,
      title: "Human-in-the-Loop Authority",
      description:
        "Strict non-diagnostic posture. Qualified physicians review, modify, and authorize all triage summaries before any clinical decision.",
      tag: "Oversight",
    },
    {
      icon: <Layers className="w-5 h-5 text-purple-600" />,
      title: "Referral & Handover Notes",
      description:
        "Generate standardized clinical handover notes aligned with FHIR conventions for seamless transfers between PHCs and district hospitals.",
      tag: "Handoff",
    },
  ];

  // 6 How It Works steps
  const howItWorksSteps = [
    {
      step: "01",
      title: "Multilingual Symptom Intake",
      desc: "Patient or intake nurse captures chief complaints via voice or text in Odia, Hindi, or English.",
      icon: <Mic className="w-5 h-5 text-teal-600" />,
    },
    {
      step: "02",
      title: "Document & Lab Report Upload",
      desc: "Paper lab slips (CBC, renal panels) are uploaded and parsed with local OCR and confidence validation.",
      icon: <FileText className="w-5 h-5 text-blue-600" />,
    },
    {
      step: "03",
      title: "Clinical Translation & Normalization",
      desc: "Regional expressions are mapped to standardized clinical terms while preserving verbatim patient words.",
      icon: <Languages className="w-5 h-5 text-sky-600" />,
    },
    {
      step: "04",
      title: "Deterministic Safety Rules Evaluation",
      desc: "Rules TRIAGE-R01 through R06 evaluate red flags transparently without black-box generative assumptions.",
      icon: <AlertTriangle className="w-5 h-5 text-amber-600" />,
    },
    {
      step: "05",
      title: "Structured Triage Note Assembly",
      desc: "Symptoms, timeline, vital parameters, and lab results are assembled into a clean clinical draft.",
      icon: <FileCheck className="w-5 h-5 text-purple-600" />,
    },
    {
      step: "06",
      title: "Licensed Doctor Review & Sign-Off",
      desc: "The attending medical officer reviews, adjusts priority if needed, and signs off. Zero AI diagnoses.",
      icon: <Stethoscope className="w-5 h-5 text-emerald-600" />,
    },
  ];

  // Who It's For roles
  const audienceRoles = [
    {
      title: "Patients",
      roleBadge: "Symptom Intake",
      badgeColor: "bg-blue-100 text-blue-800 border-blue-200",
      icon: <User className="w-6 h-6 text-blue-600" />,
      desc: "Explain symptoms naturally in your native language through speech or text without complex medical jargon.",
      benefits: [
        "Voice dictation in Odia, Hindi, and English",
        "Clear timeline and symptom organization",
        "Empowers patients ahead of doctor consultation",
      ],
    },
    {
      title: "Healthcare Staff & Nurses",
      roleBadge: "Queue & Intake Management",
      badgeColor: "bg-teal-100 text-teal-800 border-teal-200",
      icon: <Activity className="w-6 h-6 text-teal-600" />,
      desc: "Rapidly process waiting room arrivals, log preliminary vitals, and digitize printed lab slips.",
      benefits: [
        "Streamlined patient intake desk workflows",
        "Local OCR extraction for paper reports",
        "Low-bandwidth toggle for rural connectivity",
      ],
    },
    {
      title: "Physicians & Medical Officers",
      roleBadge: "Clinical Review & Sign-Off",
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      icon: <Stethoscope className="w-6 h-6 text-emerald-600" />,
      desc: "Review pre-structured clinical triage drafts, inspect explainable rule triggers, and maintain 100% sign-off authority.",
      benefits: [
        "Transparent red-flag alerts (TRIAGE-R01 to R06)",
        "Instant access to normalized lab parameters",
        "FHIR-aligned referral note exports",
      ],
    },
    {
      title: "Facility Administrators",
      roleBadge: "Governance & Quality Control",
      badgeColor: "bg-amber-100 text-amber-800 border-amber-200",
      icon: <Building className="w-6 h-6 text-amber-600" />,
      desc: "Monitor facility throughput, ensure clinical guideline compliance, and review comprehensive provenance audit trails.",
      benefits: [
        "Immutable audit logging of every action",
        "Operational queue and wait-time metrics",
        "Strict role-based access control (RBAC)",
      ],
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 selection:bg-teal-100 selection:text-teal-900">
      <Header />

      <main className="flex-1 flex flex-col items-center px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-16 py-8">
        {/* Persistent Amber Safety Disclaimer Banner */}
        <div className="w-full">
          <ClinicalDisclaimer />
        </div>

        {/* 1. HERO SECTION */}
        <section className="w-full text-center space-y-6 pt-4 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full text-xs font-semibold bg-teal-50/90 text-teal-800 border border-teal-200/80 shadow-xs">
            <ClinovaLogo variant="mark" size="xs" priority={true} />
            <span>Clinical Decision Support System &bull; Multimodal Triage Assistant</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-[1.15]">
            Intelligent Clinical Triage for{" "}
            <span className="text-teal-600">High-Volume Facilities</span>
          </h1>

          <p className="text-base sm:text-xl font-medium text-slate-700 max-w-3xl mx-auto leading-relaxed">
            Clinova AI organizes multilingual patient symptoms, voice recordings, and lab reports into
            structured, explainable clinical triage notes for licensed doctor review and authorization.
          </p>

          {/* Action CTAs: 3-Button Layout */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-3">
            {user ? (
              <Link
                href={dashboardPath(user.role)}
                className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl text-sm shadow-sm transition-all flex items-center gap-2"
              >
                <span>Open my dashboard</span> <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  href="/intake"
                  className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl text-sm shadow-sm hover:shadow-md transition-all flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>Patient Intake</span>
                </Link>
                <Link
                  href="/register"
                  className="px-6 py-3 bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 font-bold rounded-xl text-sm shadow-sm transition-all flex items-center gap-2"
                >
                  <UserPlus className="w-4 h-4 text-teal-600" />
                  <span>Sign Up</span>
                </Link>
                <Link
                  href="/login"
                  className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-xl text-sm transition-all flex items-center gap-2"
                >
                  <LogIn className="w-4 h-4 text-slate-600" />
                  <span>Login</span>
                </Link>
              </>
            )}
            {isClinician && <Link
              href="/review"
              className="px-6 py-3 bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 font-bold rounded-xl text-sm shadow-sm transition-all flex items-center gap-2"
            >
              <Activity className="w-4 h-4 text-teal-600" />
              <span>Reviewer Dashboard</span>
            </Link>}
            <a
              href="#how-it-works"
              className="px-6 py-3 bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 font-bold rounded-xl text-sm shadow-xs transition-all flex items-center gap-2"
            >
              <span>Learn How It Works</span>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </a>
          </div>

          {/* Clinical Visual Pipeline Hero Card */}
          <div className="pt-8 w-full">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 text-left space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 bg-teal-50 rounded-lg flex items-center justify-center">
                    <ClinovaLogo variant="mark" size="sm" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      Standardized Triage Architecture
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      From unstructured multilingual inputs to authorized physician sign-off
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-bold px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full w-fit">
                  Strict Human-in-the-Loop Protocol
                </span>
              </div>

              {/* 4-Stage Interactive Pipeline Visual */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                    <span className="text-teal-700">Stage 1</span>
                    <Mic className="w-4 h-4 text-teal-600" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Multimodal Intake</h4>
                  <p className="text-[11px] text-slate-500 leading-snug">
                    Voice &amp; text in Odia, Hindi, English with audio transcription.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                    <span className="text-blue-700">Stage 2</span>
                    <FileText className="w-4 h-4 text-blue-600" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Document &amp; Lab OCR</h4>
                  <p className="text-[11px] text-slate-500 leading-snug">
                    Extracts CBC and lab values locally with confidence metrics.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                    <span className="text-amber-700">Stage 3</span>
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Explainable Rules</h4>
                  <p className="text-[11px] text-slate-500 leading-snug">
                    Screens TRIAGE-R01 to R06 red flags; flags urgency indicators.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                    <span className="text-emerald-700">Stage 4</span>
                    <Stethoscope className="w-4 h-4 text-emerald-600" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Physician Sign-Off</h4>
                  <p className="text-[11px] text-slate-500 leading-snug">
                    Doctor modifies, confirms urgency, and signs off before treatment.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. WHY CLINOVA AI / INSTITUTIONAL NEED */}
        <section id="why-clinova" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Why Institutional Health Facilities Choose Clinova AI
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Engineered specifically to relieve clinical bottlenecks in public and district healthcare settings.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="p-2.5 bg-rose-50 text-rose-700 rounded-xl w-fit border border-rose-100">
                <Clock className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">Outpatient (OPD) Overcrowding</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Public health clinics often see hundreds of patients per medical officer. Clinova AI
                pre-organizes patient histories, timeline, and vitals before the doctor consultation,
                recovering vital clinical minutes per patient.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="p-2.5 bg-blue-50 text-blue-700 rounded-xl w-fit border border-blue-100">
                <Languages className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">Multilingual Clinical Gaps</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Patients articulate pain and symptoms in native languages (Odia, Hindi, regional dialects),
                while medical records require standardized clinical English. Clinova AI bridges this divide
                without losing original patient nuances.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="p-2.5 bg-amber-50 text-amber-700 rounded-xl w-fit border border-amber-100">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">Early Red-Flag Detection</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Subtle life-threatening indicators (acute dyspnea, crushing chest pain, shock vitals)
                can be overlooked in crowded waiting halls. Deterministic rules immediately elevate critical cases for urgent physician evaluation.
              </p>
            </div>
          </div>

          {/* Facility Types Supported */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3 text-left">
            <div className="flex items-center gap-2 text-teal-800">
              <Hospital className="w-5 h-5 text-teal-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                Target Healthcare Facilities &amp; Deployment Environments
              </h3>
            </div>
            <p className="text-xs text-slate-600">
              Proven adaptability across clinical infrastructure levels, from high-connectivity urban tertiary centers to low-bandwidth rural health posts:
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-2">
              {[
                "District Hospitals",
                "Primary Health Centers",
                "Community Health Posts",
                "Occupational Clinics",
                "Campus Health Units",
                "Outreach Health Camps",
              ].map((name, i) => (
                <div
                  key={i}
                  className="p-2.5 bg-slate-50 border border-slate-100 rounded-lg text-xs font-semibold text-slate-700 flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 flex-shrink-0" />
                  <span className="truncate">{name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 3. HOW IT WORKS (6-Step Clinical Workflow) */}
        <section id="how-it-works" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
              <span>Step-by-Step Triage Flow</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              How Clinova AI Operates in Practice
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              A transparent 6-stage clinical pipeline designed to support clinicians, not replace them.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {howItWorksSteps.map((s, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-teal-300 transition group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2.5 bg-slate-50 group-hover:bg-teal-50 transition rounded-xl border border-slate-100">
                      {s.icon}
                    </div>
                    <span className="text-xs font-black text-slate-400 font-mono group-hover:text-teal-600 transition">
                      {s.step}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{s.title}</h3>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{s.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Adaptive Image Clinical Architecture Diagram Showcase */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Standard Clinical Triage Workflow Architecture</h3>
                <p className="text-xs text-slate-500">
                  Multimodal input ingestion to attending medical officer review &amp; verification
                </p>
              </div>
              <span className="text-[10px] font-mono text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 font-bold">
                Adaptive Asset
              </span>
            </div>
            <AdaptiveImage
              src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80"
              alt="Clinova AI Standard Clinical Triage Workflow Architecture"
              isEssential={false}
              estimatedKb={65}
              caption="Clinical triage workflow protocol & human verification gate"
              aspectRatio="aspect-21/9"
            />
          </div>
        </section>

        {/* 4. KEY CLINICAL FEATURES */}
        <section id="features" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
              <span>Platform Capabilities</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Clinical Features Built for Rigorous Practice
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Each capability is grounded in safety protocols, audit trails, and deterministic verification.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureList.map((item, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between hover:border-teal-300 transition space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                      {item.icon}
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 bg-slate-100 text-slate-600 rounded border border-slate-200">
                      {item.tag}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{item.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 5. WHO IS IT FOR? (4 AUDIENCE CARDS) */}
        <section id="who-its-for" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
              <span>Role-Specific User Experience</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Designed for Every Healthcare Stakeholder
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Strict role-based isolation ensures patients, nurses, doctors, and administrators see only what is relevant.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {audienceRoles.map((card, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                      {card.icon}
                    </div>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${card.badgeColor}`}
                    >
                      {card.roleBadge}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-slate-900">{card.title}</h3>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{card.desc}</p>
                  </div>

                  <ul className="space-y-1.5 pt-2">
                    {card.benefits.map((b, bIdx) => (
                      <li key={bIdx} className="flex items-center gap-2 text-xs text-slate-700">
                        <Check className="w-3.5 h-3.5 text-teal-600 flex-shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 6. AI + HUMAN-IN-THE-LOOP ARCHITECTURE */}
        <section id="human-in-the-loop" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
              <span>Safety &amp; Clinical Governance</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              AI Assistance + Qualified Clinician Authority
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Clinova AI strictly delineates automated assistance from authoritative clinical judgment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* What Clinova AI Does */}
            <div className="bg-white rounded-2xl border border-teal-200 p-6 shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-teal-50 text-teal-700 rounded-lg">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">What Clinova AI Does</h3>
                  <p className="text-[11px] text-teal-700 font-semibold">Workflow &amp; Organization Engine</p>
                </div>
              </div>

              <ul className="space-y-2.5 text-xs text-slate-700">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
                  <span>Transcribes multilingual speech (Odia/Hindi) into structured medical English.</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
                  <span>Parses printed CBC and lab reports via optical character recognition.</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
                  <span>Triggers deterministic safety rules (TRIAGE-R01 to R06) to highlight red flags.</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
                  <span>Compiles pre-consultation draft summaries to save documentation time.</span>
                </li>
              </ul>
            </div>

            {/* What Clinova AI Never Does */}
            <div className="bg-white rounded-2xl border border-rose-200 p-6 shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-rose-50 text-rose-700 rounded-lg">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">What Clinova AI Never Does</h3>
                  <p className="text-[11px] text-rose-700 font-semibold">Absolute Non-Diagnostic Boundary</p>
                </div>
              </div>

              <ul className="space-y-2.5 text-xs text-slate-700">
                <li className="flex items-start gap-2">
                  <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <span>Never makes definitive medical diagnoses or autonomous clinical decisions.</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <span>Never prescribes medications, dosages, or pharmaceutical therapies.</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <span>Never discharges, admits, or redirects patients without physician authorization.</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <span>Never bypasses qualified medical officer sign-off under any circumstance.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* 7. PRIVACY, SAFETY & COMPLIANCE */}
        <section id="privacy-safety" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
              <span>Enterprise Trust &amp; Security</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Privacy, Security, and Institutional Governance
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Built on institutional security baselines to protect patient confidentiality.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
              <Lock className="w-5 h-5 text-teal-600" />
              <h3 className="text-xs font-bold text-slate-900">Role-Based Access (RBAC)</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Strict boundaries between patient intake, nurse triage, clinician review, and administrative audits.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              <h3 className="text-xs font-bold text-slate-900">PII Scrubbing &amp; Privacy</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Personal health identifiers are masked and scrubbed during processing with synthetic data fallback.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
              <Clock className="w-5 h-5 text-amber-600" />
              <h3 className="text-xs font-bold text-slate-900">24h Ephemeral Retention</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Intake drafts and session audio recordings expire automatically to prevent unauthorized storage.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
              <FileCheck className="w-5 h-5 text-purple-600" />
              <h3 className="text-xs font-bold text-slate-900">Immutable Audit Logs</h3>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Every symptom entry, rule trigger, edit, and doctor sign-off is logged with timestamp and author ID.
              </p>
            </div>
          </div>
        </section>

        {/* 8. INSTITUTIONAL CONTACT & INQUIRIES */}
        <section id="contact" className="w-full space-y-6 pt-4 scroll-mt-20">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 sm:p-8 max-w-3xl mx-auto space-y-4 text-center">
            <div className="inline-flex p-3 bg-teal-50 text-teal-600 rounded-xl border border-teal-100 mb-1">
              <Mail className="w-6 h-6 text-teal-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Institutional &amp; Pilot Inquiries</h2>
            <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
              Clinova AI is deployed in collaboration with hospital administrations, public health departments,
              and clinical research centers. For technical pilots, custom EHR integrations, or security reviews:
            </p>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl max-w-md mx-auto space-y-2 text-left text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-500 font-semibold">Institutional Pilots:</span>
                <a href="mailto:pilots@clinova.ai" className="text-teal-700 font-bold hover:underline">
                  pilots@clinova.ai
                </a>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 font-semibold">Technical &amp; Compliance:</span>
                <a href="mailto:compliance@clinova.ai" className="text-teal-700 font-bold hover:underline">
                  compliance@clinova.ai
                </a>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 font-semibold">General Inquiries:</span>
                <a href="mailto:contact@clinova.ai" className="text-teal-700 font-bold hover:underline">
                  contact@clinova.ai
                </a>
              </div>
            </div>

            <p className="text-[11px] text-slate-400">
              Pilot onboarding includes clinical workflow mapping, staff training, and local OCR calibration.
            </p>
          </div>
        </section>

        {/* 9. FINAL CALL TO ACTION */}
        <section className="w-full bg-gradient-to-br from-teal-700 to-teal-900 rounded-3xl p-8 sm:p-12 text-center text-white space-y-5 shadow-lg relative overflow-hidden">
          <div className="flex justify-center mb-1">
            <ClinovaLogo variant="badge" size="lg" />
          </div>
          <h2 className="text-2xl sm:text-4xl font-black tracking-tight">
            Ready to Streamline Triage in Your Facility?
          </h2>
          <p className="text-xs sm:text-base text-teal-100 max-w-2xl mx-auto leading-relaxed">
            Experience how multimodal symptom intake, vernacular translation, and explainable safety rules
            reduce outpatient documentation burden while preserving strict physician oversight.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              href="/intake"
              className="px-6 py-3.5 bg-white hover:bg-slate-100 text-teal-900 font-bold rounded-xl text-sm shadow-md transition-all flex items-center gap-2"
            >
              <FileText className="w-4 h-4 text-teal-700" />
              <span>Patient Intake</span>
            </Link>
            <Link
              href="/register"
              className="px-6 py-3.5 bg-teal-800/80 hover:bg-teal-800 text-white font-bold rounded-xl text-sm border border-teal-600 transition-all flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              <span>Sign Up</span>
            </Link>
            <Link
              href="/login"
              className="px-6 py-3.5 bg-teal-800/80 hover:bg-teal-800 text-white font-bold rounded-xl text-sm border border-teal-600 transition-all flex items-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              <span>Login</span>
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}