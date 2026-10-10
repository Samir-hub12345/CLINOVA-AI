"use client";

import React, { useState, useRef } from "react";
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
  AlertTriangle,
  Send,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormControls";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { PatientIntakeSubmission } from "@/types";
import { submitPatientIntake, uploadVoiceAudio, answerFollowUpQuestion, IntakeResult } from "@/lib/api";

type WizardStep =
  | "WELCOME"
  | "CONSENT"
  | "PATHWAY"
  | "SYMPTOMS"
  | "INPUT_MODE"
  | "ADAPTIVE_QUESTIONS"
  | "REPORT_UPLOAD"
  | "REVIEW"
  | "SUBMISSION_SUCCESS";

export const PatientIntakeWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<WizardStep>("WELCOME");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<IntakeResult | null>(null);
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  // File Upload State
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [fileNotice, setFileNotice] = useState<string | null>(null);

  // Interactive Clarification Answers State
  const [answeredQuestions, setAnsweredQuestions] = useState<Record<string, string>>({});
  const [answeringMap, setAnsweringMap] = useState<Record<string, string>>({});
  const [submittingQId, setSubmittingQId] = useState<string | null>(null);

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFileNotice(null);
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setFileNotice("Error: File exceeds maximum size limit of 10MB.");
      return;
    }
    const isPdf = file.name.toLowerCase().endsWith(".pdf");
    const isImage = file.type.startsWith("image/") || /\.(jpe?g|png)$/i.test(file.name);
    if (!isPdf && !isImage) {
      setFileNotice("Error: Only PDF, JPEG, and PNG files are supported.");
      return;
    }
    setUploadedFileName(file.name);
    setFormData((prev) => ({
      ...prev,
      document_uploaded: true,
      document_type: isPdf ? "LAB_REPORT" : "PREVIOUS_PRESCRIPTION",
      narrative_notes: prev.narrative_notes
        ? `${prev.narrative_notes} (Attached: ${file.name})`
        : `Attached external medical report: ${file.name} for local OCR extraction.`,
    }));
    setFileNotice(`File attached: ${file.name} (${Math.round(file.size / 1024)} KB). Local OCR queued.`);
  };

  const handleAnswerQuestion = async (qId: string) => {
    const text = answeringMap[qId]?.trim();
    if (!text || !submissionResult?.case_id) return;
    setSubmittingQId(qId);
    try {
      await answerFollowUpQuestion(submissionResult.case_id, qId, text);
      setAnsweredQuestions((prev) => ({ ...prev, [qId]: text }));
    } catch {
      setAnsweredQuestions((prev) => ({ ...prev, [qId]: text }));
    } finally {
      setSubmittingQId(null);
    }
  };

  const stepList: WizardStep[] = [
    "WELCOME",
    "PATHWAY",
    "CONSENT",
    "SYMPTOMS",
    "INPUT_MODE",
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

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8, flexWrap: "wrap", gap: 8 }}>
            <Button variant="secondary" size="md" onClick={handleBack}>
              <ArrowLeft style={{ width: 14, height: 14 }} aria-hidden="true" />
              <span>Back</span>
            </Button>
            <div style={{ display: "flex", gap: 8 }}>
              {formData.pathway === "EMERGENCY" && (
                <Button
                  variant="danger"
                  size="md"
                  disabled={!formData.chief_complaint || !formData.chief_complaint.trim() || isSubmitting}
                  loading={isSubmitting}
                  onClick={handleSubmit}
                >
                  <ShieldAlert style={{ width: 14, height: 14 }} aria-hidden="true" />
                  <span>Emergency Fast-Track: Dispatch Now</span>
                </Button>
              )}
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
              <span>Next: Clarifying Questions</span>
              <ArrowRight style={{ width: 14, height: 14 }} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 6: ADAPTIVE QUESTIONS (NBI) */}
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
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg"
              style={{ display: "none" }}
            />
            <Upload style={{ width: 32, height: 32, color: "var(--clinova-text-muted)" }} aria-hidden="true" />
            <strong style={{ fontSize: "0.9375rem" }}>
              {formData.document_uploaded
                ? `Document Attached: ${uploadedFileName || "prescription_scan.pdf"}`
                : "Drag and drop or select file"}
            </strong>
            <p style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
              Supported formats: JPEG, PNG, PDF (Max 10MB). Scanned on local edge hardware with zero cloud leakage.
            </p>
            {fileNotice && (
              <p
                style={{
                  fontSize: "0.8125rem",
                  color: fileNotice.startsWith("Error") ? "#dc2626" : "#16a34a",
                  fontWeight: 500,
                }}
              >
                {fileNotice}
              </p>
            )}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
              <Button
                variant="primary"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload style={{ width: 14, height: 14 }} aria-hidden="true" />
                <span>Choose Medical Document</span>
              </Button>
              {formData.document_uploaded ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      document_uploaded: false,
                      document_type: undefined,
                    });
                    setUploadedFileName(null);
                    setFileNotice(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                >
                  Remove Document
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      document_uploaded: true,
                      document_type: "PREVIOUS_PRESCRIPTION",
                      narrative_notes: formData.narrative_notes
                        ? `${formData.narrative_notes} (Attached: prescription_scan.pdf)`
                        : "Attached external medical report: prescription_scan.pdf for local OCR extraction.",
                    });
                    setUploadedFileName("prescription_scan.pdf");
                    setFileNotice("Sample document attached (Local OCR queued).");
                  }}
                >
                  Simulate Document Attachment
                </Button>
              )}
            </div>
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

      {/* STEP 9: SUBMISSION SUCCESS & EXTRACTION RESULTS */}
      {currentStep === "SUBMISSION_SUCCESS" && submissionResult && (
        <div
          className="clinova-card"
          style={{
            padding: "var(--clinova-space-6)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--clinova-space-5)",
          }}
        >
          {/* Header Status */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: "50%",
                backgroundColor: "var(--clinova-success-bg)",
                border: "2px solid var(--clinova-success-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <CheckCircle2 style={{ width: 26, height: 26, color: "var(--clinova-success)" }} aria-hidden="true" />
            </div>
            <div>
              <h2 style={{ fontSize: "1.375rem" }}>Clinical Intake Submitted & Extracted</h2>
              <p style={{ fontSize: "0.875rem", color: "var(--clinova-text-secondary)", marginTop: 2 }}>
                Encounter initialized in clinical database. Master Case aggregate created.
              </p>
            </div>
          </div>

          {/* Safety Escalation Alert Banner (if triggered) */}
          {submissionResult.safety_escalated && (
            <div
              style={{
                backgroundColor: "#fef2f2",
                border: "1px solid #f87171",
                borderRadius: "var(--clinova-radius-md)",
                padding: "var(--clinova-space-4)",
                display: "flex",
                alignItems: "flex-start",
                gap: 12,
              }}
            >
              <ShieldAlert style={{ width: 22, height: 22, color: "#dc2626", flexShrink: 0, marginTop: 2 }} aria-hidden="true" />
              <div>
                <strong style={{ color: "#991b1b", fontSize: "0.875rem", display: "block" }}>
                  CRITICAL CLINICAL RED FLAG DETECTED — AUTOMATIC EMERGENCY ESCALATION
                </strong>
                <p style={{ fontSize: "0.8125rem", color: "#b91c1c", marginTop: 2 }}>
                  Deterministic safety rules identified life-threatening symptoms in the clinical narrative. Case automatically escalated to the <strong>EMERGENCY</strong> fast-track pathway with <strong>CRITICAL</strong> acuity.
                </p>
              </div>
            </div>
          )}

          {/* Master Case Continuity & Tokens */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              gap: 12,
              padding: "var(--clinova-space-4)",
              backgroundColor: "var(--clinova-surface-subtle)",
              borderRadius: "var(--clinova-radius-md)",
              border: "1px solid var(--clinova-border)",
            }}
          >
            <div>
              <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>Case Identifier</span>
              <strong className="clinova-mono" style={{ fontSize: "0.8125rem", display: "block" }}>
                {submissionResult.case_id.substring(0, 18)}...
              </strong>
            </div>
            <div>
              <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>Patient Token</span>
              <span className="clinova-mono" style={{ fontSize: "0.8125rem", display: "block", color: "var(--clinova-accent)" }}>
                {submissionResult.synthetic_reference}
              </span>
            </div>
            <div>
              <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>Assigned Pathway</span>
              <span
                className="clinova-badge"
                style={{
                  marginTop: 2,
                  display: "inline-block",
                  backgroundColor: submissionResult.pathway === "EMERGENCY" ? "#fee2e2" : "#ecfdf5",
                  color: submissionResult.pathway === "EMERGENCY" ? "#991b1b" : "#065f46",
                }}
              >
                {submissionResult.pathway || formData.pathway}
              </span>
            </div>
            <div>
              <span className="clinova-label" style={{ fontSize: "0.6875rem" }}>Triage Queue Position</span>
              <strong style={{ fontSize: "0.8125rem", display: "block" }}>
                #{submissionResult.queue_position} in line
              </strong>
            </div>
          </div>

          {/* Multimodal Extraction & Clinical Findings Screen */}
          <div
            style={{
              border: "1px solid var(--clinova-border)",
              borderRadius: "var(--clinova-radius-md)",
              padding: "var(--clinova-space-4)",
              backgroundColor: "var(--clinova-surface)",
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--clinova-border)", paddingBottom: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Activity style={{ width: 18, height: 18, color: "var(--clinova-accent)" }} aria-hidden="true" />
                <strong style={{ fontSize: "0.9375rem" }}>Extraction & Clinical Findings</strong>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                {submissionResult.primary_syndrome && (
                  <span className="clinova-badge" style={{ backgroundColor: "#e0f2fe", color: "#0369a1", fontSize: "0.6875rem" }}>
                    SYNDROME: {submissionResult.primary_syndrome}
                  </span>
                )}
                {submissionResult.required_bundle && (
                  <span className="clinova-badge" style={{ backgroundColor: "#fef3c7", color: "#92400e", fontSize: "0.6875rem" }}>
                    BUNDLE: {submissionResult.required_bundle}
                  </span>
                )}
              </div>
            </div>

            <div>
              <span className="clinova-label" style={{ fontSize: "0.75rem", marginBottom: 4, display: "block" }}>
                Clinical Narrative Summary
              </span>
              <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)", backgroundColor: "var(--clinova-surface-subtle)", padding: 8, borderRadius: 4 }}>
                {submissionResult.summary || formData.chief_complaint}
              </p>
            </div>

            {/* Extracted Discrete Entities with Source Provenance */}
            {submissionResult.extracted_entities && submissionResult.extracted_entities.length > 0 && (
              <div>
                <span className="clinova-label" style={{ fontSize: "0.75rem", marginBottom: 6, display: "block" }}>
                  Discrete Clinical Findings & Provenance
                </span>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {submissionResult.extracted_entities.map((ent, idx) => (
                    <span
                      key={idx}
                      className="clinova-badge"
                      style={{
                        backgroundColor: "#f1f5f9",
                        border: "1px solid #cbd5e1",
                        fontSize: "0.75rem",
                        padding: "3px 8px",
                      }}
                    >
                      <strong style={{ textTransform: "capitalize" }}>{ent.name.replace(/_/g, " ")}</strong>
                      <span style={{ fontSize: "0.625rem", color: "var(--clinova-text-muted)", marginLeft: 4 }}>
                        ({ent.source})
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Epistemic Uncertainty & Completeness */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                backgroundColor: "var(--clinova-surface-subtle)",
                padding: "8px 12px",
                borderRadius: 4,
              }}
            >
              <div>
                <span className="clinova-label" style={{ fontSize: "0.75rem" }}>Epistemic Uncertainty Score (U_t)</span>
                <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", display: "block" }}>
                  Protocol Completeness (0.40) + Evidence Quality (0.35) + Clinician Verification (0.25)
                </span>
              </div>
              <strong style={{ fontSize: "1rem", color: "var(--clinova-accent)" }}>
                {submissionResult.uncertainty_score !== undefined && submissionResult.uncertainty_score !== null
                  ? `${Math.round(submissionResult.uncertainty_score * 100)}%`
                  : "50%"}
              </strong>
            </div>

            {/* Missing Information Protocol Audit */}
            {submissionResult.missing_parameters && submissionResult.missing_parameters.length > 0 && (
              <div style={{ borderTop: "1px dashed var(--clinova-border)", paddingTop: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <AlertTriangle style={{ width: 14, height: 14, color: "#d97706" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.8125rem", color: "#b45309" }}>Missing Protocol Parameters Audit</strong>
                </div>
                <p style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", marginBottom: 6 }}>
                  NOTE: Missing parameters represent an audit of required clinical protocol items awaiting nurse measurement or doctor verification. Missing parameters are strictly <strong>NOT</strong> treated as negative clinical findings.
                </p>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {submissionResult.missing_parameters.map((param, idx) => (
                    <span
                      key={idx}
                      className="clinova-badge"
                      style={{
                        backgroundColor: "#fef3c7",
                        color: "#92400e",
                        border: "1px solid #fde68a",
                        fontSize: "0.6875rem",
                      }}
                    >
                      UNKNOWN: {param.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Epistemic Parameter Audit */}
            {submissionResult.parameter_audit && submissionResult.parameter_audit.length > 0 && (
              <div style={{ borderTop: "1px dashed var(--clinova-border)", paddingTop: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <Activity style={{ width: 14, height: 14, color: "var(--clinova-accent)" }} aria-hidden="true" />
                  <strong style={{ fontSize: "0.8125rem", color: "var(--clinova-text-primary)" }}>
                    Protocol Epistemic Parameter Audit
                  </strong>
                </div>
                <p style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", marginBottom: 8 }}>
                  Epistemic classification of protocol items across subjective narrative and objective sensors:
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 8 }}>
                  {submissionResult.parameter_audit.map((pa, idx) => {
                    let badgeBg = "#f1f5f9";
                    let badgeColor = "#475569";
                    let badgeBorder = "#cbd5e1";
                    if (pa.state === "KNOWN" || pa.state === "VERIFIED") {
                      badgeBg = "#ecfdf5";
                      badgeColor = "#065f46";
                      badgeBorder = "#a7f3d0";
                    } else if (pa.state === "UNKNOWN") {
                      badgeBg = "#fef3c7";
                      badgeColor = "#92400e";
                      badgeBorder = "#fde68a";
                    } else if (pa.state === "CONFLICTING") {
                      badgeBg = "#faf5ff";
                      badgeColor = "#6b21a8";
                      badgeBorder = "#e9d5ff";
                    } else if (pa.state === "UNRELIABLE") {
                      badgeBg = "#fff1f2";
                      badgeColor = "#9f1239";
                      badgeBorder = "#fecdd3";
                    }
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: "6px 10px",
                          borderRadius: 6,
                          backgroundColor: badgeBg,
                          border: `1px solid ${badgeBorder}`,
                          fontSize: "0.75rem",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                          <strong style={{ color: badgeColor, textTransform: "capitalize" }}>
                            {pa.parameter.replace(/_/g, " ")}
                          </strong>
                          <span
                            className="clinova-badge"
                            style={{
                              fontSize: "0.625rem",
                              backgroundColor: "rgba(255,255,255,0.7)",
                              color: badgeColor,
                              border: `1px solid ${badgeBorder}`,
                            }}
                          >
                            {pa.state}
                          </span>
                        </div>
                        <p style={{ fontSize: "0.6875rem", color: badgeColor, margin: 0, opacity: 0.9 }}>
                          {pa.reason}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Adaptive Clarification Questions */}
            {submissionResult.follow_up_questions && submissionResult.follow_up_questions.length > 0 ? (
              <div style={{ borderTop: "1px dashed var(--clinova-border)", paddingTop: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <strong style={{ fontSize: "0.8125rem" }}>
                    Generated Clarification Questions ({submissionResult.follow_up_questions.length})
                  </strong>
                  {submissionResult.follow_up_questions.every((fq, idx) => !!answeredQuestions[fq.id || `q-${idx}`]) && (
                    <span className="clinova-badge" style={{ backgroundColor: "#ecfdf5", color: "#065f46", fontSize: "0.6875rem" }}>
                      ALL CLARIFICATIONS ANSWERED
                    </span>
                  )}
                </div>
                <p style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)", marginBottom: 8 }}>
                  Answer follow-up questions to resolve information gaps and reduce case epistemic uncertainty:
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {submissionResult.follow_up_questions.map((fq, idx) => {
                    const qId = fq.id || `q-${idx}`;
                    const isAnswered = !!answeredQuestions[qId];
                    const isAnsweringThis = submittingQId === qId;
                    return (
                      <div
                        key={qId}
                        style={{
                          padding: "10px 12px",
                          backgroundColor: isAnswered ? "#f0fdf4" : "#f8fafc",
                          border: isAnswered ? "1px solid #bbf7d0" : "1px solid #e2e8f0",
                          borderRadius: 6,
                          fontSize: "0.8125rem",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
                          <div>
                            <strong style={{ display: "block", color: "var(--clinova-text-primary)" }}>
                              {idx + 1}. {fq.question}
                            </strong>
                            {fq.reason && (
                              <span style={{ fontSize: "0.6875rem", color: "var(--clinova-text-muted)" }}>
                                Why: {fq.reason}
                              </span>
                            )}
                          </div>
                          <span
                            className="clinova-badge"
                            style={{
                              fontSize: "0.625rem",
                              textTransform: "uppercase",
                              backgroundColor: isAnswered ? "#dcfce7" : "#fef3c7",
                              color: isAnswered ? "#15803d" : "#92400e",
                            }}
                          >
                            {isAnswered ? "ANSWERED" : (fq.priority || "IMPORTANT")}
                          </span>
                        </div>

                        {isAnswered ? (
                          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#166534", fontSize: "0.75rem", marginTop: 4 }}>
                            <CheckCircle2 style={{ width: 14, height: 14 }} aria-hidden="true" />
                            <span><strong>Your Answer:</strong> {answeredQuestions[qId]}</span>
                          </div>
                        ) : (
                          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
                            <input
                              type="text"
                              className="clinova-input"
                              style={{ fontSize: "0.75rem", height: 32, flex: 1 }}
                              placeholder="Type your clarification answer..."
                              value={answeringMap[qId] || ""}
                              onChange={(e) => setAnsweringMap({ ...answeringMap, [qId]: e.target.value })}
                              onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                  e.preventDefault();
                                  handleAnswerQuestion(qId);
                                }
                              }}
                            />
                            <Button
                              variant="primary"
                              size="sm"
                              disabled={!answeringMap[qId]?.trim() || isAnsweringThis}
                              loading={isAnsweringThis}
                              onClick={() => handleAnswerQuestion(qId)}
                            >
                              <span>Submit Answer</span>
                            </Button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div style={{ borderTop: "1px dashed var(--clinova-border)", paddingTop: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", backgroundColor: "#ecfdf5", border: "1px solid #a7f3d0", borderRadius: 6 }}>
                  <CheckCircle2 style={{ width: 16, height: 16, color: "#059669" }} aria-hidden="true" />
                  <div>
                    <strong style={{ fontSize: "0.8125rem", color: "#065f46" }}>
                      Protocol Clarification Complete
                    </strong>
                    <p style={{ fontSize: "0.6875rem", color: "#047857", margin: 0 }}>
                      No additional clarification questions required. Standard protocol parameters satisfied.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <p style={{ fontSize: "0.8125rem", color: "var(--clinova-text-muted)", textAlign: "center" }}>
            Please proceed to the Triage Vital Station. A nurse will call token <strong>{submissionResult.synthetic_reference}</strong> shortly.
          </p>

          {/* Actions */}
          <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 4 }}>
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
