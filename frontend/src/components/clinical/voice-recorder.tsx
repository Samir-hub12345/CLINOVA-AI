"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Mic,
  Square,
  RotateCcw,
  Check,
  AlertCircle,
  Volume2,
  WifiOff,
  Globe,
  ChevronDown,
  Edit3,
  ArrowRight,
  PlusCircle,
  RefreshCw,
} from "lucide-react";
import { ProvenanceBadge } from "./provenance-badge";
import { useConnectivity } from "@/lib/connectivity";
import {
  SPEECH_LANGUAGES,
  isSpeechRecognitionSupported,
  detectScriptFromText,
  combineTranscripts,
  SpeechLanguage,
} from "@/lib/speech-recognition";

export type RecorderState =
  | "ready"
  | "requesting_permission"
  | "recording"
  | "transcribed"
  | "error"
  | "unsupported";

export interface VoiceRecorderProps {
  languageHint?: string;
  existingText?: string;
  onTranscriptionComplete: (
    transcript: string,
    detectedLanguage: string,
    mode?: "replace" | "append"
  ) => void;
  onInterimChange?: (interimText: string) => void;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  languageHint = "en",
  existingText = "",
  onTranscriptionComplete,
  onInterimChange,
}) => {
  const { state: networkState, isLowBandwidthActive } = useConnectivity();

  // Primary component state
  const [state, setState] = useState<RecorderState>("ready");
  const [seconds, setSeconds] = useState(0);
  const [confirmedTranscript, setConfirmedTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [editableTranscript, setEditableTranscript] = useState("");
  const [selectedLanguageCode, setSelectedLanguageCode] = useState<string>(() => {
    if (languageHint === "hi") return "hi";
    if (languageHint === "or") return "or";
    if (languageHint === "en") return "en";
    return "auto";
  });
  const [detectedLangLabel, setDetectedLangLabel] = useState<string>("English");
  const [confidence, setConfidence] = useState<number>(0.96);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showLanguagePicker, setShowLanguagePicker] = useState<boolean>(false);
  const [transferMode, setTransferMode] = useState<"append" | "replace">("append");
  const [isTransferred, setIsTransferred] = useState<boolean>(false);

  // References to keep event handlers clean and avoid stale closures
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);
  const sessionTokenRef = useRef<number>(0);
  const isManuallyStoppedRef = useRef<boolean>(false);
  const isRecordingRef = useRef<boolean>(false);

  // Sync language selection when parent languageHint changes (if still in ready state)
  useEffect(() => {
    if (state === "ready" && languageHint) {
      if (languageHint === "hi") setSelectedLanguageCode("hi");
      else if (languageHint === "or") setSelectedLanguageCode("or");
      else if (languageHint === "en") setSelectedLanguageCode("en");
    }
  }, [languageHint, state]);

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      sessionTokenRef.current += 1;
      isManuallyStoppedRef.current = true;
      if (timerRef.current) clearInterval(timerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
        recognitionRef.current = null;
      }
    };
  }, []);

  const getRecognitionLocale = (code: string): string => {
    const lang = SPEECH_LANGUAGES.find((l) => l.code === code);
    if (lang && lang.locale) return lang.locale;
    if (code === "hi") return "hi-IN";
    if (code === "or") return "or-IN";
    return "en-IN";
  };

  const startRecording = useCallback(() => {
    if (networkState === "OFFLINE") {
      setErrorMessage("Voice transcription requires an active internet connection. Please type symptoms manually below.");
      setState("error");
      return;
    }

    if (!isSpeechRecognitionSupported()) {
      setState("unsupported");
      setErrorMessage(
        "Speech recognition is not supported in this browser. Please use Google Chrome, Edge, or enter your symptoms using the text area below."
      );
      return;
    }

    // Invalidate any previous session
    sessionTokenRef.current += 1;
    const currentSession = sessionTokenRef.current;
    isManuallyStoppedRef.current = false;
    isRecordingRef.current = true;

    setState("recording");
    setSeconds(0);
    setConfirmedTranscript("");
    setInterimTranscript("");
    setEditableTranscript("");
    setErrorMessage("");
    setIsTransferred(false);

    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    const SpeechRecognitionClass =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    try {
      const recognition = new SpeechRecognitionClass();
      recognitionRef.current = recognition;

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.lang = getRecognitionLocale(selectedLanguageCode);

      recognition.onstart = () => {
        if (currentSession !== sessionTokenRef.current) return;
        setState("recording");
      };

      recognition.onresult = (event: any) => {
        if (currentSession !== sessionTokenRef.current) return;

        let finalAccumulator = "";
        let interimAccumulator = "";

        for (let i = 0; i < event.results.length; i++) {
          const result = event.results[i];
          const transcriptSegment = result[0]?.transcript || "";
          if (result.isFinal) {
            finalAccumulator += (finalAccumulator ? " " : "") + transcriptSegment.trim();
          } else {
            interimAccumulator += (interimAccumulator ? " " : "") + transcriptSegment.trim();
          }
        }

        if (finalAccumulator) {
          setConfirmedTranscript(finalAccumulator);
          setEditableTranscript(finalAccumulator);
        }
        setInterimTranscript(interimAccumulator);

        if (onInterimChange) {
          onInterimChange(interimAccumulator);
        }

        // Determine language script from the latest speech text
        const activeText = finalAccumulator || interimAccumulator;
        if (activeText) {
          if (selectedLanguageCode !== "auto") {
            const matched = SPEECH_LANGUAGES.find((l) => l.code === selectedLanguageCode);
            setDetectedLangLabel(`${matched?.name || selectedLanguageCode} (Selected)`);
          } else {
            const detected = detectScriptFromText(activeText);
            setDetectedLangLabel(detected.label);
          }
        }
      };

      recognition.onerror = (event: any) => {
        if (currentSession !== sessionTokenRef.current) return;

        const err = event.error;
        if (err === "no-speech") {
          // Non-fatal if still recording
          return;
        }

        if (err === "not-allowed" || err === "service-not-allowed") {
          isRecordingRef.current = false;
          isManuallyStoppedRef.current = true;
          if (timerRef.current) clearInterval(timerRef.current);
          setState("error");
          setErrorMessage(
            "Microphone permission was denied. Please allow microphone access in your browser settings to dictate symptoms, or type directly in the text area below."
          );
        } else if (err === "network") {
          isRecordingRef.current = false;
          if (timerRef.current) clearInterval(timerRef.current);
          setState("error");
          setErrorMessage(
            "Speech recognition network timeout or connectivity interruption. Your previously captured words remain available below."
          );
        } else {
          console.warn("Speech recognition notice:", err);
        }
      };

      recognition.onend = () => {
        if (currentSession !== sessionTokenRef.current) return;

        // If recording was NOT manually stopped, restart to maintain continuous capture
        if (isRecordingRef.current && !isManuallyStoppedRef.current) {
          try {
            recognition.start();
          } catch {}
        }
      };

      recognition.start();
    } catch (e: any) {
      console.error("SpeechRecognition initialization failed:", e);
      setState("error");
      setErrorMessage(
        "Could not access audio speech recognition. Please verify microphone permissions or enter symptoms manually."
      );
      if (timerRef.current) clearInterval(timerRef.current);
    }
  }, [networkState, selectedLanguageCode, onInterimChange]);

  const stopRecording = useCallback(() => {
    isManuallyStoppedRef.current = true;
    isRecordingRef.current = false;

    if (timerRef.current) clearInterval(timerRef.current);

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      recognitionRef.current = null;
    }

    // Flush any pending interim text into confirmed transcript
    setConfirmedTranscript((prev) => {
      let merged = prev.trim();
      if (interimTranscript.trim()) {
        merged = merged ? `${merged} ${interimTranscript.trim()}` : interimTranscript.trim();
      }

      setInterimTranscript("");
      setEditableTranscript(merged);

      if (!merged) {
        setState("error");
        setErrorMessage(
          "No speech was detected. Please check your microphone, speak clearly, or type your symptoms directly."
        );
      } else {
        setState("transcribed");
        // Automatically provide the transcribed text to the parent handler
        onTranscriptionComplete(merged, detectedLangLabel, transferMode);
        setIsTransferred(true);
      }
      return merged;
    });
  }, [interimTranscript, detectedLangLabel, transferMode, onTranscriptionComplete]);

  const resetRecording = () => {
    sessionTokenRef.current += 1;
    isManuallyStoppedRef.current = true;
    isRecordingRef.current = false;

    if (timerRef.current) clearInterval(timerRef.current);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {}
      recognitionRef.current = null;
    }

    setState("ready");
    setSeconds(0);
    setConfirmedTranscript("");
    setInterimTranscript("");
    setEditableTranscript("");
    setErrorMessage("");
    setIsTransferred(false);
  };

  const handleApplyTranscript = (mode: "append" | "replace") => {
    if (!editableTranscript.trim()) return;
    setTransferMode(mode);
    onTranscriptionComplete(editableTranscript.trim(), detectedLangLabel, mode);
    setIsTransferred(true);
  };

  return (
    <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-sm space-y-4">
      {/* Header & Language Selection */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div
            className={`p-2 rounded-lg transition-colors ${
              state === "recording"
                ? "bg-rose-100 text-rose-700 animate-pulse"
                : "bg-teal-50 text-teal-700"
            }`}
          >
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span>Multimodal Voice Symptom Intake</span>
              {state === "recording" && (
                <span className="flex items-center gap-1 text-[11px] font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-ping" />
                  Live Listening
                </span>
              )}
            </h4>
            <p className="text-xs text-slate-500">
              Real-time speech-to-text &bull; English, हिन्दी, and ଓଡ଼ିଆ
            </p>
          </div>
        </div>

        {/* Language selector & provenance badge */}
        <div className="flex items-center gap-2">
          {state === "transcribed" && (
            <ProvenanceBadge sourceType="voice" confidence={confidence} label={detectedLangLabel} />
          )}

          <div className="relative">
            <button
              type="button"
              disabled={state === "recording"}
              onClick={() => setShowLanguagePicker(!showLanguagePicker)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors disabled:opacity-50"
              title="Select speech recognition language"
            >
              <Globe className="w-3.5 h-3.5 text-teal-600" />
              <span>
                {SPEECH_LANGUAGES.find((l) => l.code === selectedLanguageCode)?.name || "Language"}
              </span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {showLanguagePicker && (
              <div className="absolute right-0 mt-1 w-52 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-20 text-xs">
                <div className="px-3 py-1 text-[10px] uppercase font-bold text-slate-400 border-b border-slate-100">
                  Recognition Language
                </div>
                {SPEECH_LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => {
                      setSelectedLanguageCode(lang.code);
                      setShowLanguagePicker(false);
                    }}
                    className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-teal-50 transition-colors ${
                      selectedLanguageCode === lang.code
                        ? "font-bold text-teal-700 bg-teal-50/50"
                        : "text-slate-700 font-medium"
                    }`}
                  >
                    <span>{lang.nativeName}</span>
                    {selectedLanguageCode === lang.code && (
                      <Check className="w-3.5 h-3.5 text-teal-600" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Network / Connectivity Banners */}
      {networkState === "OFFLINE" ? (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center gap-2">
          <WifiOff className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>
            You are currently offline. Voice transcription requires network connectivity. You can type
            symptoms directly into the narrative field below.
          </span>
        </div>
      ) : isLowBandwidthActive ? (
        <div className="p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-[11px] text-amber-900 flex items-center justify-between">
          <span className="font-semibold">
            Low-Bandwidth Mode active: Extended response timeouts and lightweight telemetry enabled.
          </span>
          <span className="text-[10px] bg-amber-200/80 font-bold px-1.5 py-0.5 rounded uppercase">
            Optimized
          </span>
        </div>
      ) : null}

      {/* State 1: Ready to Record */}
      {state === "ready" && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-dashed border-slate-300">
          <div className="text-xs text-slate-600 text-center sm:text-left space-y-0.5">
            <p className="font-semibold text-slate-800">Ready to record patient speech</p>
            <p>
              Click below to start. Real-time words will appear as you speak. Target:{" "}
              <span className="uppercase font-bold text-teal-700">
                {SPEECH_LANGUAGES.find((l) => l.code === selectedLanguageCode)?.name ||
                  selectedLanguageCode}
              </span>
            </p>
          </div>
          <button
            type="button"
            disabled={networkState === "OFFLINE"}
            onClick={startRecording}
            className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl shadow-sm transition-all"
          >
            <Mic className="w-4 h-4" /> Start Voice Recording
          </button>
        </div>
      )}

      {/* State 2: Actively Recording (Live Real-Time Streaming Hypotheses) */}
      {state === "recording" && (
        <div className="space-y-3 p-4 rounded-xl bg-gradient-to-br from-rose-50/70 to-slate-50 border border-rose-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-rose-900 font-bold">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse" />
              <span>Dictating Symptoms...</span>
              <span className="text-slate-500 font-mono font-normal">({seconds}s elapsed)</span>
            </div>
            <button
              type="button"
              onClick={stopRecording}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-lg shadow-sm transition-all"
            >
              <Square className="w-3.5 h-3.5" /> Stop &amp; Review
            </button>
          </div>

          {/* Real-time speech view area */}
          <div className="p-3 min-h-[72px] rounded-lg bg-white border border-rose-200/80 text-xs leading-relaxed space-y-1">
            <div className="text-[10px] uppercase font-bold text-slate-400 flex items-center justify-between">
              <span>Live Transcription</span>
              <span className="text-rose-600 font-semibold">{detectedLangLabel}</span>
            </div>
            <p className="text-slate-900 font-medium">
              {confirmedTranscript ? (
                <span>{confirmedTranscript} </span>
              ) : null}
              {interimTranscript ? (
                <span className="text-teal-700 italic bg-teal-50 px-1 rounded animate-pulse">
                  {interimTranscript}
                </span>
              ) : null}
              {!confirmedTranscript && !interimTranscript && (
                <span className="text-slate-400 italic">
                  Listening for speech... Please speak into your microphone clearly.
                </span>
              )}
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>Interim words stream live and stabilize as pauses are detected.</span>
            <span>Click &quot;Stop &amp; Review&quot; when finished.</span>
          </div>
        </div>
      )}

      {/* State 3: Transcribed & Reviewable */}
      {state === "transcribed" && (
        <div className="space-y-3.5 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>Transcribed Speech ({detectedLangLabel})</span>
            </div>
            <button
              type="button"
              onClick={resetRecording}
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 font-semibold"
            >
              <RotateCcw className="w-3 h-3" /> Record Again
            </button>
          </div>

          {/* Editable review field */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px]">
              <label className="text-slate-600 font-semibold flex items-center gap-1">
                <Edit3 className="w-3.5 h-3.5 text-teal-600" />
                <span>Review &amp; Edit Transcript before applying:</span>
              </label>
              <span className="text-slate-400 font-mono text-[10px]">
                {editableTranscript.length} characters
              </span>
            </div>
            <textarea
              value={editableTranscript}
              onChange={(e) => {
                setEditableTranscript(e.target.value);
                setIsTransferred(false);
              }}
              rows={3}
              className="w-full text-xs p-3 rounded-lg border border-slate-300 bg-white text-slate-900 font-medium focus:outline-none focus:ring-1 focus:ring-teal-500 leading-relaxed"
              placeholder="Edit speech transcript..."
            />
          </div>

          {/* Transfer to narrative buttons */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <p className="text-[11px] text-slate-500 italic">
              * Voice recognition is an assistive input aid &mdash; verify details before clinical review.
            </p>

            <div className="flex items-center gap-2">
              {existingText && existingText.trim().length > 0 && (
                <button
                  type="button"
                  onClick={() => handleApplyTranscript("replace")}
                  className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg shadow-sm transition-all"
                >
                  Replace Narrative
                </button>
              )}

              <button
                type="button"
                onClick={() => handleApplyTranscript("append")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-lg shadow-sm transition-all ${
                  isTransferred
                    ? "bg-emerald-600 text-white"
                    : "bg-teal-600 hover:bg-teal-700 text-white"
                }`}
              >
                {isTransferred ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Applied to Narrative</span>
                  </>
                ) : existingText ? (
                  <>
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Append to Narrative</span>
                  </>
                ) : (
                  <>
                    <ArrowRight className="w-3.5 h-3.5" />
                    <span>Transfer to Narrative</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* State 4: Error or Permission Denied */}
      {state === "error" && (
        <div className="space-y-3 p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900">
          <div className="flex items-start gap-2.5">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-amber-950 block">Voice Input Notice</span>
              <p className="text-amber-900 leading-relaxed">{errorMessage}</p>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-1 border-t border-amber-200/60">
            <button
              type="button"
              onClick={resetRecording}
              className="px-3.5 py-1.5 bg-white border border-amber-300 rounded-lg font-semibold text-amber-900 hover:bg-amber-100/50 transition-colors shadow-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* State 5: Unsupported Browser */}
      {state === "unsupported" && (
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-2">
          <div className="flex items-center gap-2 font-bold text-slate-800">
            <AlertCircle className="w-4 h-4 text-slate-500" />
            <span>Browser Speech-to-Text Unavailable</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            The Web Speech API is not enabled in this browser. You can still type your full clinical
            symptoms directly into the narrative field below.
          </p>
        </div>
      )}
    </div>
  );
};
