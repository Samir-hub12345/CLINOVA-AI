"use client";

import React from "react";
import {
  Activity,
  Layers,
  Building2,
  Radio,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Lock,
  FileCheck2,
  FileSpreadsheet,
  Zap,
} from "lucide-react";

interface PublicWebsiteProps {
  onLaunchWorkstation: () => void;
}

export const PublicWebsite: React.FC<PublicWebsiteProps> = ({ onLaunchWorkstation }) => {
  return (
    <div className="space-y-24 py-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* 1. HERO SECTION */}
      <section className="text-center space-y-6 max-w-4xl mx-auto pt-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-100 text-teal-800 text-xs font-bold uppercase tracking-wider border border-teal-200">
          <Activity className="w-3.5 h-3.5" />
          Adaptive Clinical Care Intelligence & Navigation Platform
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-slate-950 tracking-tight leading-[1.1]">
          From Isolated Triage <br />
          <span className="text-teal-700">To Continuous Care Intelligence</span>
        </h1>

        <p className="text-slate-600 text-base sm:text-lg leading-relaxed max-w-3xl mx-auto">
          CLINOVA AI connects <strong>Patient Risk</strong>, <strong>Evidence Uncertainty</strong>,{" "}
          <strong>Facility Capability</strong>, <strong>System Demand</strong>, and <strong>Outcomes</strong>{" "}
          to identify the <strong>Safest Achievable Care Pathway</strong> while keeping qualified
          healthcare professionals strictly in control.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={onLaunchWorkstation}
            className="px-6 py-3 rounded-xl bg-teal-700 hover:bg-teal-800 text-white font-bold text-sm shadow-md flex items-center gap-2 transition-all transform hover:-translate-y-0.5"
          >
            Launch Clinical Workstation
            <ArrowRight className="w-4 h-4" />
          </button>
          <a
            href="#architecture"
            className="px-6 py-3 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-800 font-bold text-sm transition-all"
          >
            Explore System Architecture
          </a>
        </div>
      </section>

      {/* 2. THE PROBLEM & THE EXISTING GAP */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-rose-600">The Healthcare Gap</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Why Isolated Point-in-Time Triage Fails
          </h3>
          <p className="text-xs sm:text-sm text-slate-500">
            Traditional hospital triage systems treat patient admission as an isolated, static event.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-900 text-base">Blind Emergency Referrals</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Patients suffering acute emergencies (e.g. stroke, severe trauma) are routinely sent to
              higher-tier centers without verifying whether the receiving facility has functioning
              diagnostics (CT/MRI) or available ICU beds.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-900 text-base">Static vs Evolving Trajectory</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Patients deteriorate over time. A patient classified as &quot;routine&quot; during initial arrival
              may experience rapid sepsis deterioration within 30 minutes. Point-in-time scores miss dynamic trajectory.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
              <Radio className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-900 text-base">Epidemiological Blindness</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Public health directors have zero real-time visibility into localized disease clusters
              (e.g. Dengue, cholera) until emergency departments are already paralyzed by admission surges.
            </p>
          </div>
        </div>
      </section>

      {/* 3. THE 4 INNOVATION PILLARS */}
      <section id="architecture" className="space-y-8 scroll-mt-20">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-teal-700">The CLINOVA Solution</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Four Connected Intelligence Pillars
          </h3>
          <p className="text-xs sm:text-sm text-slate-500">
            A continuous loop from individual patient physiology to regional hospital network capacity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pillar 1 */}
          <div className="p-7 rounded-2xl bg-white border border-teal-200 shadow-xs space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-teal-50 border border-teal-200 text-teal-700">
                <Layers className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-teal-700 uppercase tracking-wider">PILLAR 1</span>
                <h4 className="text-lg font-bold text-slate-900">CAREGRAPH — Patient Clinical State</h4>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Models changing patient state as a directed knowledge graph. Computes standardized NEWS2
              acuity, continuous trajectory slope (ΔR points/hour), and diagnostic uncertainty (U_t).
              Maintains full data provenance across all symptoms, labs, and vitals.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] font-mono text-slate-700">
              Core Question: <em>&quot;What is happening to this patient right now?&quot;</em>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-7 rounded-2xl bg-white border border-blue-200 shadow-xs space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-700">
                <Building2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider">PILLAR 2</span>
                <h4 className="text-lg font-bold text-slate-900">FACILITYGRAPH — Care Feasibility</h4>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Models facility capabilities (blood banks, CT scanners, ICU beds) across regional tiers (PHC, CHC, SDH, DH, Tertiary).
              Evaluates care feasibility predicate Φ(F, B) and ranks referral destinations by transit time and capacity.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] font-mono text-slate-700">
              Core Question: <em>&quot;Can the required care actually be delivered here?&quot;</em>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="p-7 rounded-2xl bg-white border border-purple-200 shadow-xs space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-purple-50 border border-purple-200 text-purple-700">
                <Radio className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider">PILLAR 3</span>
                <h4 className="text-lg font-bold text-slate-900">SIGNALGRAPH — System Telemetry</h4>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Aggregates de-identified synthetic signals from real prototype intakes to detect regional
              syndromic outbreaks using statistical Z-scores (Z ≥ 2.5 alert). Monitors department queue congestion and ICU bed depletion.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] font-mono text-slate-700">
              Core Question: <em>&quot;What is happening across the connected healthcare environment?&quot;</em>
            </div>
          </div>

          {/* Pillar 4 */}
          <div className="p-7 rounded-2xl bg-white border border-emerald-200 shadow-xs space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700">
                <Cpu className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">PILLAR 4</span>
                <h4 className="text-lg font-bold text-slate-900">ORCHESTRATION ENGINE — Next Care Action</h4>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Synthesizes CareGraph + Uncertainty + Facility Feasibility + System Context to recommend the
              safest achievable action: <code>ASK</code>, <code>VERIFY</code>, <code>CONTINUE</code>,{" "}
              <code>OBSERVE</code>, <code>ESCALATE</code>, or <code>REFER</code>. Enforces mandatory clinician review gate.
            </p>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] font-mono text-slate-700">
              Core Question: <em>&quot;What is the safest achievable next care action?&quot;</em>
            </div>
          </div>
        </div>
      </section>

      {/* 4. MASTER CLINICAL WORKFLOW */}
      <section className="p-8 rounded-2xl bg-slate-900 text-white space-y-6 shadow-md">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider">Continuous Loop</span>
          <h3 className="text-2xl font-bold">Master Clinical Workflow (Section 4)</h3>
          <p className="text-xs text-slate-400">
            From arrival to patient outcome closure — an unbroken clinical chain.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] font-mono text-slate-300">
          <span className="px-3 py-1 rounded bg-slate-800 border border-slate-700">PATIENT</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-slate-800 border border-slate-700">MULTIMODAL INTAKE</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-teal-900 border border-teal-700 text-teal-200 font-bold">CAREGRAPH</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-slate-800 border border-slate-700">RISK + TRAJECTORY</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-blue-900 border border-blue-700 text-blue-200 font-bold">FACILITYGRAPH</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-emerald-900 border border-emerald-700 text-emerald-200 font-bold">ORCHESTRATION</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-rose-900 border border-rose-700 text-rose-200 font-bold">CLINICIAN GATE</span>
          <span>→</span>
          <span className="px-3 py-1 rounded bg-purple-900 border border-purple-700 text-purple-200 font-bold">OUTCOME / SIGNALGRAPH</span>
        </div>
      </section>

      {/* 5. CLINICAL USE CASES (Section 10) */}
      <section id="use-cases" className="space-y-8 scroll-mt-20">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-teal-700">Validated Scenarios</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Clinical Care Navigation in Action
          </h3>
          <p className="text-xs sm:text-sm text-slate-500">
            Demonstrating care intelligence across primary, secondary, and tertiary tiers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
              <span className="px-2.5 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-mono">SCENARIO A</span>
              <span>Rural Acute Stroke at Level 1 PHC</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Patient arrives at Angul Rural PHC with acute hemiparesis and facial droop within 45 minutes.
              FACILITYGRAPH immediately identifies that Level 1 PHC lacks a CT scanner and IV thrombolytics (Φ = INFEASIBLE).
              The Orchestration Engine advises <code>REFER</code>, calculates a ~35-minute transit window to Cuttack DH,
              and generates an SBAR transfer packet with pre-arrival thrombolytic bed reservation.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
              <span className="px-2.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-mono">SCENARIO B</span>
              <span>Severe Snakebite Envenomation with Respiratory Failure</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Patient with venomous Russell&apos;s viper bite presents at CHC. Serial vitals reveal deteriorating
              respiratory rate (RR 14 → 28 breaths/min) and SpO2 drop (96% → 88%). CAREGRAPH computes rapid trajectory
              deterioration (ΔR = +1.6 points/hour). Orchestration triggers <code>ESCALATE</code> for immediate bag-valve-mask
              airway support while reserving ventilator capacity at District Hospital.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
              <span className="px-2.5 py-0.5 rounded bg-purple-100 text-purple-800 text-[10px] font-mono">SCENARIO C</span>
              <span>Dengue Hemorrhagic Outbreak Surge Detection</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Multiple febrile patients with petechial rash and thrombocytopenia (platelet &lt; 50,000) present across rural PHCs.
              SIGNALGRAPH aggregates de-identified events in real time. Statistical anomaly detection detects a surge Z-score of 3.8
              (Z ≥ 3.5), raising an automated <code>SURGE_ALERT</code> for regional health directors before inpatient wards are overwhelmed.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
              <span className="px-2.5 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-mono">SCENARIO D</span>
              <span>Dynamic Feasibility Shift via Real-Time Equipment Outage</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              When District Hospital&apos;s 24/7 CT Scanner experiences maintenance tube failure, a facility admin toggles it offline.
              Immediately, care feasibility Φ for acute neuro-trauma flips from <code>FEASIBLE</code> to <code>INFEASIBLE</code>.
              The regional routing engine automatically redirects upcoming trauma ambulances to SCB Medical College without bottleneck delay.
            </p>
          </div>
        </div>
      </section>

      {/* 6. RESEARCH & ACADEMIC FOUNDATIONS */}
      <section id="research" className="p-8 rounded-2xl bg-slate-100 border border-slate-200 space-y-6 scroll-mt-20">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-[10px] font-bold text-teal-700 uppercase tracking-wider">Methodology & Rigor</span>
          <h3 className="text-2xl font-bold text-slate-900">Research & Clinical Foundations</h3>
          <p className="text-xs text-slate-500">
            Grounded in established international medical scoring, topological mathematics, and epidemiological surveillance.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-2">
            <h5 className="font-bold text-slate-900">NEWS2 Physiological Acuity</h5>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Calculates standard National Early Warning Score 2 (RR, SpO2, SBP, HR, AVPU, Temp) normalized to R_t ∈ [0.0, 1.0].
            </p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-2">
            <h5 className="font-bold text-slate-900">Haversine Rural Geodesics</h5>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Computes geographical distance with a 1.3 road tortuosity factor and 45 km/h rural road ambulance transit speed.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-2">
            <h5 className="font-bold text-slate-900">Statistical Z-Score Alerts</h5>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Monitors syndromic volume against rolling 48h baseline mean and variance: Z = (Observed - μ) / σ (Z ≥ 2.5 warning, Z ≥ 3.5 surge).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-2">
            <h5 className="font-bold text-slate-900">Cognitive Human-in-the-Loop</h5>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              All AI inferences remain advisory. Overrides require mandatory clinical justification and immutable medicolegal signatures.
            </p>
          </div>
        </div>
      </section>

      {/* 7. INTERACTIVE DEMO GUIDE (Section 21 Scenarios) */}
      <section id="demo" className="space-y-6 scroll-mt-20">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <span className="text-[10px] font-bold text-teal-700 uppercase tracking-wider">Verification Guide</span>
          <h3 className="text-2xl font-bold text-slate-900">How to Test the System in the Workstation</h3>
          <p className="text-xs text-slate-500">
            Follow this 4-step workflow to experience end-to-end continuous care intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 font-bold flex items-center justify-center text-xs">1</div>
            <h5 className="font-bold text-slate-900">Create an Intake</h5>
            <p className="text-slate-600 text-[11px]">
              Go to <strong>Multimodal Intake</strong>. Select a preset (e.g. <em>Acute Stroke at Rural PHC</em> or <em>Dengue Hemorrhagic</em>) or dictate symptoms in Hindi/English.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 font-bold flex items-center justify-center text-xs">2</div>
            <h5 className="font-bold text-slate-900">Inspect CareGraph</h5>
            <p className="text-slate-600 text-[11px]">
              View the interactive patient knowledge graph. Inject serial vitals in the simulator to watch the trajectory slope (ΔR) update live.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 font-bold flex items-center justify-center text-xs">3</div>
            <h5 className="font-bold text-slate-900">Verify Feasibility</h5>
            <p className="text-slate-600 text-[11px]">
              Switch to <strong>Facility Feasibility</strong>. Check local predicate Φ. Toggle the CT scanner offline to observe dynamic referral reranking and SBAR generation.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 font-bold flex items-center justify-center text-xs">4</div>
            <h5 className="font-bold text-slate-900">Clinician Review Gate</h5>
            <p className="text-slate-600 text-[11px]">
              In <strong>Orchestration</strong>, review the advisory recommendation. Authorize the action or submit an override with clinical notes, then close the outcome loop.
            </p>
          </div>
        </div>
      </section>

      {/* 8. CLINICAL GOVERNANCE & SAFETY NOTICE */}
      <section className="p-8 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-emerald-700 font-bold text-base">
          <ShieldCheck className="w-6 h-6" />
          <span>Non-Diagnostic Clinical Safety Mandate (Section 6 & 7)</span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          CLINOVA AI is strictly non-diagnostic and advisory. The system does not autonomously prescribe medications,
          override doctors, or make unsupervised emergency routing decisions. All recommendations require verification
          by a qualified healthcare professional. The prototype operates exclusively on synthetic or public sample data
          with full PII minimization and tamper-evident audit trails.
        </p>
      </section>

      {/* 9. ABOUT & BPUT ALIGNMENT */}
      <section id="about" className="p-8 rounded-2xl bg-teal-900 text-teal-50 space-y-4 shadow-md scroll-mt-20">
        <div className="max-w-2xl space-y-2">
          <span className="text-[10px] font-bold text-teal-300 uppercase tracking-wider">Institutional Background</span>
          <h3 className="text-2xl font-bold text-white">About CLINOVA AI</h3>
          <p className="text-xs text-teal-100 leading-relaxed">
            CLINOVA AI was developed in alignment with the BPUT problem statement mandate for intelligent, resilient,
            and accessible healthcare navigation. Designed for rural and peri-urban healthcare networks across India and
            global public health systems, CLINOVA demonstrates how AI can empower frontline nurses, medical officers,
            and district administrators without replacing the human judgment essential to medical care.
          </p>
        </div>
      </section>

      {/* 10. BOTTOM CTA */}
      <section className="text-center space-y-4 pt-6">
        <h3 className="text-2xl font-bold text-slate-900">Experience Continuous Care Intelligence</h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Test real multimodal intakes, serial trajectory recalculations, facility feasibility flips, and clinician sign-off gates.
        </p>
        <button
          onClick={onLaunchWorkstation}
          className="px-8 py-3.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white font-bold text-sm shadow-md inline-flex items-center gap-2 transition-all transform hover:-translate-y-0.5"
        >
          Launch Clinical Workstation
          <ArrowRight className="w-4 h-4" />
        </button>
      </section>
    </div>
  );
};
