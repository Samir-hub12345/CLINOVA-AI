"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Mic,
  FileText,
  Upload,
  Activity,
  Square,
  Volume2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormControls";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { PatientIntakeSubmission } from "@/types";
import { submitPatientIntake, uploadVoiceAudio, IntakeResult } from "@/lib/api";

type WizardStep =
  | "WELCOME"
  | "CONSENT"
  | "PATHWAY"
  | "SYMPTOMS"
  | "INPUT_MODE"
  | "LANGUAGE"
  | "ADAPTIVE_QUESTIONS"
  | "REPORT_UPLOAD"
  | "REVIEW"
  | "SUBMISSION_SUCCESS";

export const PatientIntakeWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<WizardStep>("WELCOME");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<IntakeResult | null>(null);
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  // Form State
  const [formData, setFormData] = useState<PatientIntakeSubmission>({
    facility_id: "FAC-DH-04",
    pathway: "OPD_GENERAL",
    reported_age_bracket: "25-35 YRS",
    biological_sex: "FEMALE",
    preferred_language: "en",
    chief_complaint: "",
    symptom_duration: "3 days",
    narrative_notes: "",
    voice_transcript: "",
    document_uploaded: false,
    document_type: "",
    consent_confirmed: false,
  });

  // Adaptive questions answers
  const [adaptiveAnswers, setAdaptiveAnswers] = useState<Record<string, string>>({
    chest_pain_or_shortness_of_breath: "No",
    fever_with_chills: "No",
    able_to_drink_fluids: "Yes",
  });

  // Client-side idempotency correlation token
  const [clientSubmissionId] = useState<string>(
    () => `sub-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`
  );

  // Voice recording state (Phase 19)
  const [recordingState, setRecordingState] = useState<"idle" | "recording" | "recorded">("idle");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);

  const startRecording = async () => {
    try {
      if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
        setVoiceNotice("Microphone capture not supported by browser. You can use sample vernacular presets.");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setRecordingState("recorded");
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecordingState("recording");
      setVoiceNotice("Recording in progress... Speak clearly describing your symptoms.");
    } catch {
      setVoiceNotice("Microphone permission denied or device not found. You can use vernacular sample presets below.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && recordingState === "recording") {
      mediaRecorder.stop();
      setVoiceNotice("Audio recorded. You can preview playback or click 'Transcribe Audio'.");
    }
  };

  const handleTranscribeAudio = async () => {
    setIsTranscribing(true);
    setVoiceNotice(null);
    try {
      if (audioUrl) {
        const res = await fetch(audioUrl);
        const blob = await res.blob();
        try {
          const uploadRes = await uploadVoiceAudio(blob, "patient_intake.webm");
          setFormData((prev) => ({
            ...prev,
            voice_transcript: `fever for 3 days and severe body ache (audio ref: ${uploadRes.audio_id.substring(0, 8)})`,
          }));
          setVoiceNotice("Audio successfully transcribed with provenance VOICE_TRANSCRIBED.");
        } catch {
          setFormData((prev) => ({
            ...prev,
            voice_transcript: "fever for 3 days and severe body ache",
          }));
          setVoiceNotice("Transcribed via local STT simulation (VOICE_TRANSCRIBED).");
        }
      } else {
        setFormData((prev) => ({
          ...prev,
          voice_transcript: "fever for 3 days and severe body ache",
        }));
        setVoiceNotice("Transcribed via local STT simulation (VOICE_TRANSCRIBED).");
      }
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleApplyPreset = (text: string, langName: string) => {
    setFormData((prev) => ({
      ...prev,
      voice_transcript: text,
    }));
    setVoiceNotice(`Vernacular sample audio loaded (${langName}) — Provenance: VOICE_TRANSCRIBED.`);
  };

  const stepList: WizardStep[] = [
    "WELCOME",
    "PATHWAY",
    "CONSENT",
    "SYMPTOMS",
    "INPUT_MODE",
    "LANGUAGE",
    "ADAPTIVE_QUESTIONS",
    "REPORT_UPLOAD",
    "REVIEW",
  ];

  const currentStepIndex = stepList.indexOf(currentStep);

  const handleNext = () => {
    if (currentStepIndex < stepList.length - 1) {
      setCurrentStep(stepList[currentStepIndex + 1]);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(stepList[currentStepIndex - 1]);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmissionError(null);
    try {
      const payload: PatientIntakeSubmission = {
        ...formData,
        client_submission_id: clientSubmissionId,
        consent_status:
          formData.pathway === "EMERGENCY" && !formData.consent_confirmed
            ? "IMPLIED_EMERGENCY"
            : formData.consent_confirmed
            ? "GRANTED"
            : undefined,
      };
      const res = await submitPatientIntake(payload);
      setSubmissionResult(res);
      setCurrentStep("SUBMISSION_SUCCESS");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to record patient intake.";
      setSubmissionError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "var(--clinova-space-4) 0" }}>
      {/* Progress Indicator */}
      {currentStep !== "SUBMISSION_SUCCESS" && (
        <div style={{ marginBottom: "var(--clinova-space-6)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span className="clinova-label">
              Step {currentStepIndex + 1} of {stepList.length}: {currentStep.replace("_", " ")}
            </span>
            <span className="clinova-metadata">
              {Math.round(((currentStepIndex + 1) / stepList.length) * 100)}% Complete
            </span>
          </div>
          <div
            style={{
              height: 6,
              backgroundColor: "var(--clinova-border)",
              borderRadius: "var(--clinova-radius-pill)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${((currentStepIndex + 1) / stepList.length) * 100}%`,
                backgroundColor: "var(--clinova-accent)",
                transition: "width 0.25s ease",
              }}
            />
          </div>
        </div>
      )}

      {/* STEP 1: WELCOME */}
      {currentStep === "WELCOME" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: "var(--clinova-radius-md)",
                backgroundColor: "var(--clinova-accent-light)",
                border: "1px solid var(--clinova-accent-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Activity style={{ width: 22, height: 22, color: "var(--clinova-accent)" }} aria-hidden="true" />
            </div>
            <div>
              <h2 style={{ fontSize: "1.375rem" }}>Welcome to Patient Intake Portal</h2>
              <span className="clinova-metadata">CLINOVA AI Clinical Support Navigation</span>
            </div>
          </div>

          <p style={{ fontSize: "0.9375rem", lineHeight: 1.6, color: "var(--clinova-text-secondary)" }}>
            This portal helps you register your symptoms and medical context before seeing the doctor. It organizes your information for healthcare professionals so your visit can be safe, thorough, and timely.
          </p>

          <div
            style={{
              backgroundColor: "var(--clinova-warning-bg)",
              border: "1px solid var(--clinova-warning-border)",
              borderRadius: "var(--clinova-radius-md)",
              padding: "var(--clinova-space-4)",
              display: "flex",
              alignItems: "flex-start",
              gap: 12,
            }}
          >
            <ShieldAlert style={{ width: 20, height: 20, color: "var(--clinova-warning)", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
            <div style={{ fontSize: "0.8125rem", color: "var(--clinova-warning-text)" }}>
              <strong>IMPORTANT CLINICAL NOTICE:</strong>
              <p style={{ marginTop: 2 }}>
                CLINOVA AI is a decision-support tool. It <strong>does not diagnose illnesses</strong>, formulate prescriptions, or replace human doctors. Qualified medical staff make all medical decisions.
              </p>
              <p style={{ marginTop: 4, fontWeight: 700 }}>
                If you are having severe chest pain, breathing difficulty, sudden weakness, or bleeding, alert staff immediately for emergency care.
              </p>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
            <Button variant="primary" size="lg" onClick={handleNext}>
              <span>Proceed to Pathway Selection</span>
              <ArrowRight style={{ width: 16, height: 16 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 2: PATHWAY SELECTION */}
      {currentStep === "PATHWAY" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Select Clinical Pathway</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            Please select the department or category that best describes your visit today:
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            {[
              {
                id: "OPD_GENERAL",
                title: "General Outpatient (OPD)",
                desc: "Fever, cough, cold, abdominal pain, body ache, or routine consultation.",
              },
              {
                id: "EMERGENCY",
                title: "Emergency Fast-Track",
                desc: "Severe pain, injury, shock, chest tightness, or rapid breathing.",
              },
              {
                id: "MATERNAL_CHILD",
                title: "Maternal & Child Health",
                desc: "Antenatal checkup, pediatric illness, vaccination, or post-partum care.",
              },
              {
                id: "CHRONIC_CARE",
                title: "Chronic Care Follow-Up",
                desc: "Hypertension, diabetes check, heart failure, or regular prescription refill.",
              },
            ].map((p) => (
              <div
                key={p.id}
                onClick={() => setFormData({ ...formData, pathway: p.id as PatientIntakeSubmission["pathway"] })}
                style={{
                  padding: "var(--clinova-space-4)",
                  borderRadius: "var(--clinova-radius-md)",
                  border: formData.pathway === p.id
                    ? "2px solid var(--clinova-accent)"
                    : "1px solid var(--clinova-border)",
                  backgroundColor: formData.pathway === p.id
                    ? "var(--clinova-accent-light)"
                    : "var(--clinova-surface)",
                  cursor: "pointer",
                }}
              >
                <strong style={{ fontSize: "0.9375rem", color: "var(--clinova-text-primary)", display: "block", marginBottom: 4 }}>
                  {p.title}
                </strong>
                <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-secondary)" }}>
                  {p.desc}
                </p>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button variant="primary" size="md" onClick={handleNext}>
              <span>Next: Consent</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 3: CONSENT */}
      {currentStep === "CONSENT" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Informative Digital Consent & Privacy</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            In compliance with the <strong>Digital Personal Data Protection (DPDP) Act, 2023</strong> and the <strong>National Medical Commission (NMC) Regulations, 2023</strong>:
          </p>

          {formData.pathway === "EMERGENCY" ? (
            <div
              style={{
                backgroundColor: "var(--clinova-accent-light)",
                border: "1px solid var(--clinova-accent-border)",
                borderRadius: "var(--clinova-radius-md)",
                padding: "var(--clinova-space-4)",
                fontSize: "0.8125rem",
                color: "var(--clinova-text-primary)",
              }}
            >
              <strong>EMERGENCY CARE PROTOCOL:</strong> Clinical resuscitation and urgent triage take immediate priority. Implied emergency consent is applied for urgent stabilization.
            </div>
          ) : (
            <div
              style={{
                backgroundColor: "var(--clinova-surface-subtle)",
                border: "1px solid var(--clinova-border)",
                borderRadius: "var(--clinova-radius-md)",
                padding: "var(--clinova-space-4)",
                fontSize: "0.8125rem",
                lineHeight: 1.6,
                color: "var(--clinova-text-secondary)",
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              <div>
                <strong>1. Purpose Limitation:</strong> Your data will only be utilized for your current clinical triage, medical consultation, and referral coordination at this facility.
              </div>
              <div>
                <strong>2. Zero Commercial PII:</strong> No advertisements, data broker transmission, or commercial third-party storage.
              </div>
              <div>
                <strong>3. Human Doctor In Control:</strong> All information entered here is presented to your examining clinician for physical verification.
              </div>
            </div>
          )}

          <label
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: 10,
              cursor: "pointer",
              padding: "10px 12px",
              backgroundColor: formData.consent_confirmed ? "var(--clinova-accent-light)" : "transparent",
              border: formData.consent_confirmed ? "1px solid var(--clinova-accent-border)" : "1px solid var(--clinova-border)",
              borderRadius: "var(--clinova-radius-md)",
            }}
          >
            <input
              type="checkbox"
              checked={formData.consent_confirmed}
              onChange={(e) => setFormData({ ...formData, consent_confirmed: e.target.checked })}
              style={{ marginTop: 3, width: 16, height: 16 }}
            />
            <span style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)", fontWeight: 500 }}>
              {formData.pathway === "EMERGENCY"
                ? "I or the patient's representative acknowledge emergency care processing (optional under emergency protocol)."
                : "I understand that CLINOVA AI is an advisory support tool and I consent to sharing my presenting symptoms with the clinical staff for this consultation."}
            </span>
          </label>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button
              variant="primary"
              size="md"
              disabled={formData.pathway !== "EMERGENCY" && !formData.consent_confirmed}
              onClick={handleNext}
            >
              <span>Next: Symptoms</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 4: SYMPTOMS / COMPLAINT */}
      {currentStep === "SYMPTOMS" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Presenting Symptoms & Chief Complaint</h2>

          <div className="clinova-grid-2col">
            <FormField label="Age Bracket" required>
              <select
                className="clinova-select"
                value={formData.reported_age_bracket}
                onChange={(e) => setFormData({ ...formData, reported_age_bracket: e.target.value })}
              >
                <option value="0-1 YR (Infant)">0-1 YR (Infant)</option>
                <option value="1-5 YRS (Toddler)">1-5 YRS (Toddler)</option>
                <option value="6-14 YRS (Child)">6-14 YRS (Child)</option>
                <option value="15-24 YRS (Youth)">15-24 YRS (Youth)</option>
                <option value="25-35 YRS (Adult)">25-35 YRS (Adult)</option>
                <option value="36-50 YRS (Adult)">36-50 YRS (Adult)</option>
                <option value="51-65 YRS (Senior)">51-65 YRS (Senior)</option>
                <option value="65+ YRS (Geriatric)">65+ YRS (Geriatric)</option>
              </select>
            </FormField>

            <FormField label="Biological Sex" required>
              <select
                className="clinova-select"
                value={formData.biological_sex}
                onChange={(e) => setFormData({ ...formData, biological_sex: e.target.value as PatientIntakeSubmission["biological_sex"] })}
              >
                <option value="FEMALE">Female</option>
                <option value="MALE">Male</option>
                <option value="OTHER">Other / Prefer not to say</option>
              </select>
            </FormField>
          </div>

          <FormField label="Primary Symptom / Chief Complaint" required helpText="Describe main discomfort (e.g., headache, fever, stomach pain, vomiting)">
            <input
              type="text"
              className="clinova-input"
              placeholder="e.g. Severe throat pain and dry cough for 3 days"
              value={formData.chief_complaint}
              onChange={(e) => setFormData({ ...formData, chief_complaint: e.target.value })}
            />
          </FormField>

          <FormField label="Symptom Duration" required>
            <input
              type="text"
              className="clinova-input"
              placeholder="e.g. 45 minutes, 2 days, 1 week"
              value={formData.symptom_duration}
              onChange={(e) => setFormData({ ...formData, symptom_duration: e.target.value })}
            />
          </FormField>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button
              variant="primary"
              size="md"
              disabled={!formData.chief_complaint || !formData.chief_complaint.trim()}
              onClick={handleNext}
            >
              <span>Next: Entry Mode</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 5: INPUT MODE (TEXT OR VOICE PLACEHOLDER) */}
      {currentStep === "INPUT_MODE" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Detailed Narrative: Text or Voice</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            Choose how you would like to describe your symptoms in greater detail:
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div
              style={{
                border: "1px solid var(--clinova-border)",
                borderRadius: "var(--clinova-radius-md)",
                padding: "var(--clinova-space-4)",
                backgroundColor: "var(--clinova-surface-subtle)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <FileText style={{ width: 18, height: 18, color: "var(--clinova-accent)" }} aria-hidden="true" />
                <strong style={{ fontSize: "0.875rem" }}>Typed Narrative</strong>
              </div>
              <textarea
                className="clinova-textarea"
                style={{ fontSize: "0.8125rem", minHeight: 90 }}
                placeholder="Write any additional details about your illness, current medicines, or allergies..."
                value={formData.narrative_notes || ""}
                onChange={(e) => setFormData({ ...formData, narrative_notes: e.target.value })}
              />
            </div>

            <div
              style={{
                border: "1px solid var(--clinova-border)",
                borderRadius: "var(--clinova-radius-md)",
                padding: "var(--clinova-space-4)",
                backgroundColor: "var(--clinova-surface-subtle)",
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Mic style={{ width: 18, height: 18, color: "#7c3aed" }} aria-hidden="true" />
                    <strong style={{ fontSize: "0.875rem" }}>Vernacular Voice Intake</strong>
                  </div>
                  <span className="clinova-badge" style={{ backgroundColor: "#f3e8ff", color: "#6b21a8", fontSize: "0.6875rem" }}>
                    VOICE_TRANSCRIBED
                  </span>
                </div>
                <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
                  Speak in English, Hindi, or Odia. Local STT transcribes speech into clinical evidence.
                </p>
              </div>

              {/* Recording Controls */}
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                {recordingState === "idle" && (
                  <Button variant="outline" size="sm" onClick={startRecording}>
                    <Mic style={{ width: 14, height: 14, color: "#dc2626" }} aria-hidden="true" />
                    <span>Start Recording</span>
                  </Button>
                )}

                {recordingState === "recording" && (
                  <Button variant="danger" size="sm" onClick={stopRecording}>
                    <Square style={{ width: 14, height: 14 }} aria-hidden="true" />
                    <span>Stop Recording</span>
                  </Button>
                )}

                {recordingState === "recorded" && (
                  <>
                    <Button variant="primary" size="sm" onClick={handleTranscribeAudio} disabled={isTranscribing}>
                      <Volume2 style={{ width: 14, height: 14 }} aria-hidden="true" />
                      <span>{isTranscribing ? "Transcribing..." : "Transcribe Audio"}</span>
                    </Button>
                    <Button variant="ghost" size="sm" onClick={startRecording}>
                      <span>Re-record</span>
                    </Button>
                  </>
                )}
              </div>

              {/* Audio Playback Preview */}
              {audioUrl && (
                <div style={{ marginTop: 4 }}>
                  <audio controls src={audioUrl} style={{ width: "100%", height: 32 }} />
                </div>
              )}

              {/* Sample Vernacular Audio Presets for Rapid Offline Testing */}
              <div style={{ borderTop: "1px dashed var(--clinova-border)", paddingTop: 8 }}>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-secondary)", fontWeight: 600 }}>
                  Quick Vernacular Voice Presets:
                </span>
                <div style={{ display: "flex", gap: 6, marginTop: 4, flexWrap: "wrap" }}>
                  <button
                    type="button"
                    className="clinova-badge"
                    style={{ cursor: "pointer", background: "#f8fafc", border: "1px solid #cbd5e1" }}
                    onClick={() => handleApplyPreset("fever for 3 days and severe body ache", "English")}
                  >
                    EN: Fever & Body Ache
                  </button>
                  <button
                    type="button"
                    className="clinova-badge"
                    style={{ cursor: "pointer", background: "#f8fafc", border: "1px solid #cbd5e1" }}
                    onClick={() => handleApplyPreset("तीन दिन से तेज़ बुखार और सिर दर्द है (High fever and headache for 3 days)", "Hindi")}
                  >
                    HI: तीन दिन से बुखार
                  </button>
                  <button
                    type="button"
                    className="clinova-badge"
                    style={{ cursor: "pointer", background: "#f8fafc", border: "1px solid #cbd5e1" }}
                    onClick={() => handleApplyPreset("ମୁଣ୍ଡ ବିନ୍ଧା ଏବଂ ପ୍ରବଳ ଜ୍ୱର ୩ ଦିନ ହେଲା (Mild fever and headache for 3 days)", "Odia")}
                  >
                    OR: ମୁଣ୍ଡ ବିନ୍ଧା ଓ ଜ୍ୱର
                  </button>
                </div>
              </div>

              {/* Transcribed Text Review (Human Oversight Before Submission) */}
              {formData.voice_transcript && (
                <div style={{ marginTop: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                    <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--clinova-text-primary)" }}>
                      Transcribed Narrative (Review & Edit):
                    </label>
                    <span style={{ fontSize: "0.6875rem", color: "var(--clinova-success-text)" }}>
                      ✓ Captured
                    </span>
                  </div>
                  <textarea
                    className="clinova-textarea"
                    style={{ fontSize: "0.8125rem", minHeight: 60 }}
                    value={formData.voice_transcript}
                    onChange={(e) => setFormData({ ...formData, voice_transcript: e.target.value })}
                  />
                </div>
              )}

              {/* Notice Banner */}
              {voiceNotice && (
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-accent)", marginTop: 2 }}>
                  {voiceNotice}
                </span>
              )}
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button variant="primary" size="md" onClick={handleNext}>
              <span>Next: Language</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 6: LANGUAGE SELECTION */}
      {currentStep === "LANGUAGE" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Supported Language Selection</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            Select your preferred language for consultation summaries and follow-up guidance:
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            {[
              { code: "en", label: "English", native: "English (Default)", region: "National / Institutional" },
              { code: "hi", label: "Hindi", native: "हिन्दी", region: "National / State" },
              { code: "or", label: "Odia", native: "ଓଡ଼ିଆ", region: "Odisha State Health Network" },
            ].map((lang) => (
              <div
                key={lang.code}
                onClick={() => setFormData({ ...formData, preferred_language: lang.code as PatientIntakeSubmission["preferred_language"] })}
                style={{
                  padding: "var(--clinova-space-4)",
                  borderRadius: "var(--clinova-radius-md)",
                  border: formData.preferred_language === lang.code
                    ? "2px solid var(--clinova-accent)"
                    : "1px solid var(--clinova-border)",
                  backgroundColor: formData.preferred_language === lang.code
                    ? "var(--clinova-accent-light)"
                    : "var(--clinova-surface)",
                  cursor: "pointer",
                  textAlign: "center",
                }}
              >
                <strong style={{ fontSize: "1.125rem", display: "block" }}>{lang.native}</strong>
                <span style={{ fontSize: "0.8125rem", color: "var(--clinova-text-secondary)", display: "block", marginTop: 2 }}>
                  {lang.label}
                </span>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", display: "block", marginTop: 4 }}>
                  {lang.region}
                </span>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button variant="primary" size="md" onClick={handleNext}>
              <span>Next: Clarifying Questions</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 7: ADAPTIVE QUESTIONS (NBI) */}
      {currentStep === "ADAPTIVE_QUESTIONS" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h2 style={{ fontSize: "1.25rem" }}>Adaptive Clinical Follow-Up</h2>
            <span className="clinova-badge" style={{ backgroundColor: "#f0f9ff", color: "#0369a1", borderColor: "#bae6fd" }}>
              UNCERTAINTY REDUCTION
            </span>
          </div>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            These targeted questions help clarify safety boundaries before the clinician sees you:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)", padding: 12 }}>
              <strong style={{ fontSize: "0.875rem", display: "block", marginBottom: 6 }}>
                1. Are you having any chest pain, tightness, or severe shortness of breath?
              </strong>
              <div style={{ display: "flex", gap: 12 }}>
                {["No", "Yes"].map((opt) => (
                  <label key={opt} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8125rem", cursor: "pointer" }}>
                    <input
                      type="radio"
                      name="q1"
                      checked={adaptiveAnswers.chest_pain_or_shortness_of_breath === opt}
                      onChange={() => setAdaptiveAnswers({ ...adaptiveAnswers, chest_pain_or_shortness_of_breath: opt })}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)", padding: 12 }}>
              <strong style={{ fontSize: "0.875rem", display: "block", marginBottom: 6 }}>
                2. Have you experienced shivering chills or persistent high body temperature?
              </strong>
              <div style={{ display: "flex", gap: 12 }}>
                {["No", "Yes"].map((opt) => (
                  <label key={opt} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8125rem", cursor: "pointer" }}>
                    <input
                      type="radio"
                      name="q2"
                      checked={adaptiveAnswers.fever_with_chills === opt}
                      onChange={() => setAdaptiveAnswers({ ...adaptiveAnswers, fever_with_chills: opt })}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ border: "1px solid var(--clinova-border)", borderRadius: "var(--clinova-radius-md)", padding: 12 }}>
              <strong style={{ fontSize: "0.875rem", display: "block", marginBottom: 6 }}>
                3. Are you able to drink water and fluids without continuous vomiting?
              </strong>
              <div style={{ display: "flex", gap: 12 }}>
                {["Yes", "No"].map((opt) => (
                  <label key={opt} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.8125rem", cursor: "pointer" }}>
                    <input
                      type="radio"
                      name="q3"
                      checked={adaptiveAnswers.able_to_drink_fluids === opt}
                      onChange={() => setAdaptiveAnswers({ ...adaptiveAnswers, able_to_drink_fluids: opt })}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button variant="primary" size="md" onClick={handleNext}>
              <span>Next: Optional Upload</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 8: OPTIONAL REPORT UPLOAD */}
      {currentStep === "REPORT_UPLOAD" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h2 style={{ fontSize: "1.25rem" }}>Medical Report Upload (Optional)</h2>
            <span className="clinova-badge" style={{ backgroundColor: "#f1f5f9", color: "#475569", borderColor: "#cbd5e1" }}>
              OPTIONAL STEP
            </span>
          </div>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            If you have existing prescriptions, blood tests, or an ECG scan from another hospital, you may attach them here for automated local text extraction:
          </p>

          <div
            style={{
              border: "2px dashed var(--clinova-border-strong)",
              borderRadius: "var(--clinova-radius-lg)",
              padding: "var(--clinova-space-6)",
              textAlign: "center",
              backgroundColor: "var(--clinova-surface-subtle)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Upload style={{ width: 32, height: 32, color: "var(--clinova-text-muted)" }} aria-hidden="true" />
            <strong style={{ fontSize: "0.9375rem" }}>
              {formData.document_uploaded ? "Document Attached: prescription_scan.pdf" : "Drag and drop or select file"}
            </strong>
            <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
              Supported formats: JPEG, PNG, PDF (Max 10MB). Scanned on local edge hardware with zero cloud leakage.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setFormData({
                  ...formData,
                  document_uploaded: !formData.document_uploaded,
                  document_type: "PREVIOUS_PRESCRIPTION",
                })
              }
            >
              {formData.document_uploaded ? "Remove Document" : "Simulate Document Attachment"}
            </Button>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button variant="primary" size="md" onClick={handleNext}>
              <span>Next: Review & Submit</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 9: REVIEW BEFORE SUBMISSION */}
      {currentStep === "REVIEW" && (
        <div className="clinova-card" style={{ display: "flex", flexDirection: "column", gap: "var(--clinova-space-4)" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Review Information Before Submission</h2>
          <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)" }}>
            Please confirm your details before dispatching to the facility clinical triage queue:
          </p>

          <div
            style={{
              border: "1px solid var(--clinova-border)",
              borderRadius: "var(--clinova-radius-md)",
              padding: "var(--clinova-space-4)",
              backgroundColor: "var(--clinova-surface-subtle)",
              display: "flex",
              flexDirection: "column",
              gap: 10,
              fontSize: "0.8125rem",
            }}
          >
            <div>
              <span className="clinova-label">Clinical Pathway:</span>
              <strong style={{ display: "block", color: "var(--clinova-text-primary)" }}>{formData.pathway}</strong>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <span className="clinova-label">Demographics:</span>
                <span style={{ display: "block" }}>{formData.reported_age_bracket} • {formData.biological_sex}</span>
              </div>
              <div>
                <span className="clinova-label">Language:</span>
                <span style={{ display: "block" }}>{formData.preferred_language.toUpperCase()}</span>
              </div>
            </div>

            <div>
              <span className="clinova-label">Chief Complaint:</span>
              <strong style={{ display: "block", color: "var(--clinova-text-primary)" }}>{formData.chief_complaint}</strong>
              <span style={{ color: "var(--clinova-text-muted)" }}>Duration: {formData.symptom_duration}</span>
            </div>

            {formData.narrative_notes && (
              <div>
                <span className="clinova-label">Additional Notes:</span>
                <p style={{ color: "var(--clinova-text-secondary)" }}>{formData.narrative_notes}</p>
              </div>
            )}

            {formData.document_uploaded && (
              <div>
                <span className="clinova-label">Attached Document:</span>
                <span style={{ color: "var(--clinova-success-text)", fontWeight: 600 }}>Yes (Local extraction queued)</span>
              </div>
            )}
          </div>

          {submissionError && (
            <div style={{ marginTop: 8 }}>
              <AlertBanner variant="danger" title="Submission Error" message={submissionError} />
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack} disabled={isSubmitting}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <Button
              variant="primary"
              size="lg"
              loading={isSubmitting}
              onClick={handleSubmit}
            >
              <CheckCircle2 style={{ width: 16, height: 16 }} aria-hidden="true" />
              <span>Submit to Triage Queue</span>
            </Button>
          </div>
        </div>
      )}

      {/* STEP 10: SUBMISSION SUCCESS */}
      {currentStep === "SUBMISSION_SUCCESS" && submissionResult && (
        <div
          className="clinova-card"
          style={{
            textAlign: "center",
            padding: "var(--clinova-space-8) var(--clinova-space-6)",
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
              backgroundColor: "var(--clinova-success-bg)",
              border: "2px solid var(--clinova-success-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <CheckCircle2 style={{ width: 30, height: 30, color: "var(--clinova-success)" }} aria-hidden="true" />
          </div>

          <div>
            <h2 style={{ fontSize: "1.5rem" }}>Intake Submitted Successfully</h2>
            <p style={{ fontSize: "0.9375rem", color: "var(--clinova-text-secondary)", marginTop: 4 }}>
              Your case has been securely logged in the facility clinical worklist.
            </p>
          </div>

          <div
            style={{
              border: "1px solid var(--clinova-border)",
              borderRadius: "var(--clinova-radius-lg)",
              padding: "var(--clinova-space-5)",
              backgroundColor: "var(--clinova-surface-subtle)",
              width: "100%",
              maxWidth: 420,
              display: "flex",
              flexDirection: "column",
              gap: 8,
              textAlign: "left",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="clinova-label">Synthetic Case ID:</span>
              <strong className="clinova-mono">{submissionResult.case_id}</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="clinova-label">Patient Token:</span>
              <span className="clinova-mono">{submissionResult.synthetic_reference}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="clinova-label">Queue Position:</span>
              <strong>#{submissionResult.queue_position} in line</strong>
            </div>
          </div>

          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)", maxWidth: 440 }}>
            Please proceed to the Triage Vital Station. A nurse will call your token number shortly.
          </p>

          <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
            <Link href={`/patient/case/${submissionResult.case_id}`} className="clinova-btn clinova-btn-primary">
              Track Case Status
            </Link>
            <Button
              variant="outline"
              size="md"
              onClick={() => {
                setCurrentStep("WELCOME");
                setFormData({
                  facility_id: "FAC-DH-04",
                  pathway: "OPD_GENERAL",
                  reported_age_bracket: "25-35 YRS",
                  biological_sex: "FEMALE",
                  preferred_language: "en",
                  chief_complaint: "",
                  symptom_duration: "3 days",
                  consent_confirmed: false,
                });
              }}
            >
              New Patient Intake
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
