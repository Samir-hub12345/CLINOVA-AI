"use client";

import React, { useState } from "react";
import {
  FileText,
  Mic,
  FileSpreadsheet,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Send,
  Sparkles,
  Volume2,
  RefreshCw,
} from "lucide-react";
import { submitTextIntake, submitVoiceIntake, parseOcrReport } from "@/lib/api";

interface IntakeTabProps {
  onCaseCreated: (caseId: string) => void;
}

export const IntakeTab: React.FC<IntakeTabProps> = ({ onCaseCreated }) => {
  const [mode, setMode] = useState<"TEXT" | "VOICE" | "OCR">("TEXT");
  const [facilityId, setFacilityId] = useState("FAC-DH-04");
  const [reportedName, setReportedName] = useState("Ramesh Patnaik");
  const [reportedAge, setReportedAge] = useState<number>(54);
  const [biologicalSex, setBiologicalSex] = useState("MALE");
  const [consentGranted, setConsentGranted] = useState(true);
  const [language, setLanguage] = useState("en");

  // Text state
  const [narrativeText, setNarrativeText] = useState(
    "Patient reports acute severe crushing chest pain radiating to left arm and jaw for 45 minutes, with diaphoresis and mild shortness of breath."
  );

  // Vitals state
  const [hr, setHr] = useState<number>(108);
  const [sysBp, setSysBp] = useState<number>(135);
  const [diaBp, setDiaBp] = useState<number>(88);
  const [spo2, setSpo2] = useState<number>(95);
  const [rr, setRr] = useState<number>(22);
  const [temp, setTemp] = useState<number>(37.2);

  // Voice state
  const [isRecording, setIsRecording] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState(
    "मुझे छाती में बहुत तेज दर्द हो रहा है और सांस लेने में तकलीफ हो रही है"
  );
  const [voiceConfidence, setVoiceConfidence] = useState(0.93);

  // OCR state
  const [ocrText, setOcrText] = useState(
    "DISTRICT PATHOLOGY LAB REPORT\nHb: 11.2 g/dL\nPlatelets: 42,000 /uL (CRITICAL LOW)\nWBC: 16,800 /uL\nBP: 100/60 mmHg | SpO2: 94%"
  );
  const [ocrConfidence, setOcrConfidence] = useState(0.89);
  const [ocrResult, setOcrResult] = useState<any>(null);

  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Presets
  const applyPreset = (type: string) => {
    if (type === "CHEST_PAIN") {
      setNarrativeText("Acute severe crushing chest pain radiating to left jaw, diaphoresis, shortness of breath.");
      setHr(112);
      setSysBp(140);
      setSpo2(95);
      setRr(22);
      setFacilityId("FAC-DH-04");
    } else if (type === "STROKE_PHC") {
      setNarrativeText("Right-sided facial droop, arm weakness, and slurred speech starting 40 minutes ago.");
      setHr(84);
      setSysBp(165);
      setSpo2(97);
      setRr(18);
      setFacilityId("FAC-PHC-01"); // PHC lacks CT scanner -> triggers REFER!
    } else if (type === "DENGUE_FEVER") {
      setNarrativeText("High fever for 4 days, petechial rash on forearms, severe retro-orbital pain, epistaxis.");
      setHr(104);
      setSysBp(98);
      setSpo2(96);
      setTemp(39.4);
      setFacilityId("FAC-DH-04");
    } else if (type === "ROUTINE") {
      setNarrativeText("Mild runny nose, sneezing, scratchy throat for 2 days. Normal appetite.");
      setHr(72);
      setSysBp(118);
      setSpo2(99);
      setRr(16);
      setTemp(36.8);
      setFacilityId("FAC-CHC-02");
    }
  };

  const handleTestOcr = async () => {
    try {
      const res = await parseOcrReport(ocrText, ocrConfidence);
      setOcrResult(res);
      if (res.extracted_vitals) {
        if (res.extracted_vitals.systolic_bp) setSysBp(res.extracted_vitals.systolic_bp);
        if (res.extracted_vitals.spo2_percent) setSpo2(res.extracted_vitals.spo2_percent);
      }
    } catch (e: any) {
      alert("OCR parsing failed: " + e.message);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      let res;
      if (mode === "TEXT") {
        res = await submitTextIntake({
          facility_id: facilityId,
          reported_name: reportedName,
          reported_age: reportedAge,
          biological_sex: biologicalSex,
          narrative_text: narrativeText,
          language: language,
          vitals: {
            heart_rate: hr,
            systolic_bp: sysBp,
            diastolic_bp: diaBp,
            spo2_percent: spo2,
            respiratory_rate: rr,
            temperature_celsius: temp,
          },
        });
      } else if (mode === "VOICE") {
        res = await submitVoiceIntake({
          facility_id: facilityId,
          audio_transcript: voiceTranscript,
          confidence_score: voiceConfidence,
          language: language,
        });
      } else {
        // OCR text intake
        res = await submitTextIntake({
          facility_id: facilityId,
          reported_name: reportedName,
          reported_age: reportedAge,
          biological_sex: biologicalSex,
          narrative_text: `Extracted Lab Report: ${ocrText}`,
          language: "en",
          vitals: ocrResult?.extracted_vitals || { heart_rate: hr, systolic_bp: sysBp, spo2_percent: spo2 },
        });
      }

      setFeedback(`Encounter ${res.case_number} created successfully! Status: ${res.status} (${res.acuity_tier})`);
      onCaseCreated(res.case_id);
    } catch (err: any) {
      setFeedback(`Error creating case: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-teal-600" />
            Multimodal Symptom & Evidence Intake
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Compliant with BPUT Baseline: Voice, Text, OCR, Regional Languages, Consent & Automatic PII Scrubbing.
          </p>
        </div>
        {/* Preset quick buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Presets:</span>
          <button
            onClick={() => applyPreset("CHEST_PAIN")}
            className="text-xs px-2.5 py-1 rounded bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100"
          >
            Acute STEMI
          </button>
          <button
            onClick={() => applyPreset("STROKE_PHC")}
            className="text-xs px-2.5 py-1 rounded bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100"
          >
            Stroke @ PHC
          </button>
          <button
            onClick={() => applyPreset("DENGUE_FEVER")}
            className="text-xs px-2.5 py-1 rounded bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100"
          >
            Dengue Surge
          </button>
          <button
            onClick={() => applyPreset("ROUTINE")}
            className="text-xs px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100"
          >
            Routine Cold
          </button>
        </div>
      </div>

      {/* Mode Switcher Tabs */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-xl px-4 pt-2 gap-2">
        <button
          onClick={() => setMode("TEXT")}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            mode === "TEXT"
              ? "border-teal-600 text-teal-800 bg-teal-50/50"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <FileText className="w-4 h-4" />
          Narrative Text Intake
        </button>
        <button
          onClick={() => setMode("VOICE")}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            mode === "VOICE"
              ? "border-teal-600 text-teal-800 bg-teal-50/50"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Mic className="w-4 h-4" />
          Voice / Speech Transcription
        </button>
        <button
          onClick={() => setMode("OCR")}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
            mode === "OCR"
              ? "border-teal-600 text-teal-800 bg-teal-50/50"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          Medical Report / Lab OCR
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Main Intake Form */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-b-xl border border-t-0 border-slate-200 shadow-xs space-y-5">
            {/* Facility & Language Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Arrival Facility
                </label>
                <select
                  value={facilityId}
                  onChange={(e) => setFacilityId(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
                >
                  <option value="FAC-PHC-01">Angul Rural PHC (Level 1 PHC - No CT/ICU)</option>
                  <option value="FAC-CHC-02">Talcher CHC (Level 2 CHC - Basic X-ray)</option>
                  <option value="FAC-SDH-03">Dhenkanal SDH (Level 3 SDH - General Surgery)</option>
                  <option value="FAC-DH-04">Cuttack District Hospital (Level 4 DH - CT & ICU)</option>
                  <option value="FAC-TMC-05">SCB Medical College (Level 5 Tertiary - Level 1 Trauma)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Intake Language (Auto-Translated)
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi (हिंदी)</option>
                  <option value="or">Odia (ଓଡ଼ିଆ)</option>
                </select>
              </div>
            </div>

            {/* Mode Specific Body */}
            {mode === "TEXT" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Clinical Narrative & Presenting Complaint
                  </label>
                  <textarea
                    rows={4}
                    value={narrativeText}
                    onChange={(e) => setNarrativeText(e.target.value)}
                    placeholder="Describe symptoms, onset duration, radiation, aggravating factors..."
                    className="w-full text-xs p-3 rounded-lg border border-slate-300 font-mono focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>
            )}

            {mode === "VOICE" && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl border border-teal-200 bg-teal-50/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                      <Volume2 className="w-4 h-4 text-teal-600" />
                      Speech-to-Text Transcription Stream
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800">
                      Confidence: {(voiceConfidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-10 rounded bg-white border border-slate-200 flex items-center justify-center px-4">
                    <div className="flex items-center gap-1">
                      {[30, 60, 45, 90, 75, 40, 85, 95, 30, 70, 50, 40].map((h, i) => (
                        <span
                          key={i}
                          style={{ height: `${h}%` }}
                          className={`w-1 rounded-full ${isRecording ? "bg-red-500 animate-pulse" : "bg-teal-500"}`}
                        />
                      ))}
                    </div>
                  </div>
                  <textarea
                    rows={3}
                    value={voiceTranscript}
                    onChange={(e) => setVoiceTranscript(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-slate-300 bg-white font-mono"
                  />
                  <div className="flex items-center justify-between">
                    <button
                      type="button"
                      onClick={() => setIsRecording(!isRecording)}
                      className={`text-xs px-3 py-1.5 rounded-lg font-semibold flex items-center gap-2 ${
                        isRecording ? "bg-red-600 text-white" : "bg-slate-900 text-white"
                      }`}
                    >
                      <Mic className="w-3.5 h-3.5" />
                      {isRecording ? "Stop Listening" : "Record Speech Stream"}
                    </button>
                    <span className="text-[11px] text-slate-500">
                      Tagged with <code className="text-teal-700 font-mono">VOICE_TRANSCRIBED</code> provenance
                    </span>
                  </div>
                </div>
              </div>
            )}

            {mode === "OCR" && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-slate-700">
                      Medical Report / Lab Slip OCR Buffer
                    </label>
                    <div className="flex items-center gap-2 text-xs">
                      <span>Simulated Confidence:</span>
                      <select
                        value={ocrConfidence}
                        onChange={(e) => setOcrConfidence(parseFloat(e.target.value))}
                        className="text-xs p-1 border rounded"
                      >
                        <option value={0.92}>0.92 (High Quality)</option>
                        <option value={0.78}>0.78 (Standard Scan)</option>
                        <option value={0.42}>0.42 (Low - Triggers Fallback)</option>
                      </select>
                    </div>
                  </div>
                  <textarea
                    rows={4}
                    value={ocrText}
                    onChange={(e) => setOcrText(e.target.value)}
                    className="w-full text-xs p-3 rounded-lg border border-slate-300 font-mono"
                  />
                  <div className="mt-2 flex items-center justify-between">
                    <button
                      type="button"
                      onClick={handleTestOcr}
                      className="text-xs px-3 py-1.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 font-semibold flex items-center gap-1.5"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Execute Parser
                    </button>
                    <span className="text-[11px] text-slate-500">
                      Tagged with <code className="text-teal-700 font-mono">OCR_EXTRACTED</code> provenance
                    </span>
                  </div>
                </div>

                {ocrResult && (
                  <div
                    className={`p-3 rounded-lg border text-xs ${
                      ocrResult.status === "OCR_FAILED"
                        ? "bg-rose-50 border-rose-200 text-rose-800"
                        : "bg-slate-50 border-slate-200"
                    }`}
                  >
                    <div className="font-bold mb-1">
                      Parser Status: {ocrResult.status} (Score: {ocrResult.confidence_score})
                    </div>
                    {ocrResult.error && <p className="text-rose-700 text-xs">{ocrResult.error}</p>}
                    {ocrResult.extracted_labs && (
                      <div className="grid grid-cols-3 gap-2 mt-2">
                        {Object.entries(ocrResult.extracted_labs).map(([k, v]) => (
                          <div key={k} className="p-1.5 rounded bg-white border border-slate-200 text-[11px]">
                            <span className="text-slate-500 block">{k}</span>
                            <span className="font-bold text-slate-900">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Vital Signs Grid */}
            <div className="border-t border-slate-200 pt-4 space-y-3">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Baseline Bedside Vitals (NEWS2 Inputs)
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">HR (bpm)</label>
                  <input
                    type="number"
                    value={hr}
                    onChange={(e) => setHr(parseInt(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">Sys BP (mmHg)</label>
                  <input
                    type="number"
                    value={sysBp}
                    onChange={(e) => setSysBp(parseInt(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">Dia BP (mmHg)</label>
                  <input
                    type="number"
                    value={diaBp}
                    onChange={(e) => setDiaBp(parseInt(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">SpO2 (%)</label>
                  <input
                    type="number"
                    value={spo2}
                    onChange={(e) => setSpo2(parseInt(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">RR (/min)</label>
                  <input
                    type="number"
                    value={rr}
                    onChange={(e) => setRr(parseInt(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-500 block">Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={temp}
                    onChange={(e) => setTemp(parseFloat(e.target.value) || 0)}
                    className="w-full text-xs p-2 rounded border border-slate-300"
                  />
                </div>
              </div>
            </div>

            {/* Submit Action */}
            <div className="pt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-xs transition-all disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {loading ? "Processing Intake..." : "Submit to Clinical Triage Queue"}
              </button>
            </div>

            {feedback && (
              <div className="p-3 rounded-lg bg-teal-50 border border-teal-200 text-xs font-semibold text-teal-900">
                {feedback}
              </div>
            )}
          </div>
        </div>

        {/* Right 1 Col: Governance, PII Scrubbing & Consent */}
        <div className="space-y-6">
          {/* Anonymization Preview */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              PII Minimization & Anonymization
            </h3>
            <p className="text-[11px] text-slate-500">
              Raw patient identity is scrubbed into synthetic identifiers and 10-year age brackets.
            </p>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                <span className="text-[10px] text-slate-400 block font-semibold">Reported Identity</span>
                <span className="font-semibold text-slate-700">
                  {reportedName} (Age: {reportedAge}, Sex: {biologicalSex})
                </span>
              </div>
              <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200">
                <span className="text-[10px] text-emerald-700 block font-semibold">
                  Scrubbed Synthetic Profile
                </span>
                <span className="font-bold text-emerald-950 font-mono">
                  SYN-PT-•••• (Age Bracket: {reportedAge >= 50 ? "50-59" : "40-49"})
                </span>
              </div>
            </div>
          </div>

          {/* Informed Consent Gate */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
              Informed Patient Consent
            </h3>
            <label className="flex items-start gap-2.5 text-xs text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={consentGranted}
                onChange={(e) => setConsentGranted(e.target.checked)}
                className="mt-0.5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
              />
              <span className="text-[11px] leading-snug">
                Patient / caregiver provided verbal or digital consent for non-diagnostic AI-assisted care navigation.
              </span>
            </label>
            {!consentGranted && (
              <div className="text-[11px] text-rose-600 font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Consent required before clinical review handoff.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
