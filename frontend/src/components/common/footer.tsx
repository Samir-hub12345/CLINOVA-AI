import React from "react";
import Link from "next/link";
import { ShieldCheck, Lock, AlertTriangle, Mail } from "lucide-react";
import { ClinovaLogo } from "@/components/common/clinova-logo";

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white text-slate-600 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-10">
          {/* Col 1: Brand & Overview */}
          <div className="lg:col-span-2 space-y-3">
            <ClinovaLogo variant="full" size="sm" />
            <p className="text-xs text-slate-500 leading-relaxed max-w-sm">
              Multimodal healthcare triage assistant and clinical decision support system.
              Designed for public health institutions, district hospitals, and outpatient facilities
              facing acute clinical workload and multilingual documentation challenges.
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-500">
              <span className="inline-flex items-center gap-1 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                <ShieldCheck className="w-3 h-3 text-teal-600" />
                Deterministic Clinical Rules
              </span>
              <span className="inline-flex items-center gap-1 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                <Lock className="w-3 h-3 text-teal-600" />
                Strict Human-in-the-Loop
              </span>
            </div>
          </div>

          {/* Col 2: Navigation */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">Platform</h4>
            <ul className="space-y-1.5 text-xs text-slate-500">
              <li>
                <Link href="/#how-it-works" className="hover:text-teal-700 transition">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/#features" className="hover:text-teal-700 transition">
                  Clinical Features
                </Link>
              </li>
              <li>
                <Link href="/#who-its-for" className="hover:text-teal-700 transition">
                  Who It&apos;s For
                </Link>
              </li>
              <li>
                <Link href="/#human-in-the-loop" className="hover:text-teal-700 transition">
                  Human-in-the-Loop Architecture
                </Link>
              </li>
              <li>
                <Link href="/#privacy-safety" className="hover:text-teal-700 transition">
                  Privacy &amp; Safety Controls
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Role Portals */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">Role Portals</h4>
            <ul className="space-y-1.5 text-xs text-slate-500">
              <li>
                <Link href="/get-started" className="hover:text-teal-700 transition">
                  Get Started
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-teal-700 transition">
                  Clinician &amp; Staff Login
                </Link>
              </li>
              <li>
                <Link href="/intake" className="hover:text-teal-700 transition">
                  Patient Intake Flow
                </Link>
              </li>
              <li>
                <Link href="/review" className="hover:text-teal-700 transition">
                  Clinical Review Queue
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-teal-700 transition">
                  Facility Admin Access
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Governance & Contact */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">Governance</h4>
            <ul className="space-y-1.5 text-xs text-slate-500">
              <li>
                <span className="text-slate-600 font-medium">Rules:</span> TRIAGE-R01 to R06
              </li>
              <li>
                <span className="text-slate-600 font-medium">Data:</span> Synthetic &amp; De-identified
              </li>
              <li>
                <span className="text-slate-600 font-medium">Retention:</span> 24-Hour Ephemeral Cache
              </li>
              <li>
                <Link href="/#contact" className="hover:text-teal-700 transition flex items-center gap-1">
                  <Mail className="w-3 h-3 text-teal-600" />
                  <span>Institutional Inquiries</span>
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Regulatory & Clinical Safety Disclaimer */}
        <div className="pt-6 border-t border-slate-200 space-y-3">
          <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-[11px] text-amber-900 leading-relaxed flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold uppercase tracking-wider">Clinical Decision Support Notice: </span>
              Clinova AI is a clinical workflow optimization and triage-assistance tool intended exclusively for licensed healthcare personnel and institutional health facilities. It does not formulate medical diagnoses, establish definitive prognoses, or prescribe pharmaceutical treatments. All triage notes, vital interpretations, and urgency indicators must be verified and authorized by a qualified medical practitioner before initiating clinical interventions.
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-400">
            <p>
              &copy; {new Date().getFullYear()} Clinova AI. Built for institutional healthcare facilities and high-volume triage environments.
            </p>
            <p className="flex items-center gap-3">
              <span>Zero Unconsented PHI Storage</span>
              <span>&bull;</span>
              <span>Full Provenance Audit Trail</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};
